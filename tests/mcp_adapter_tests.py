import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jikuo import runtime_visibility
from jikuo.integrations.mcp import adapter, schemas


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
POLICY_ACTIVE_PROJECT = FIXTURES / "policy_store_active_project"
POLICY_EVIDENCE_SESSION_PROJECT = FIXTURES / "policy_evidence_session_project"
POLICY_TEMPLATE = (
    ROOT
    / "src"
    / "jikuo"
    / "policy_templates"
    / "engineering_governance"
    / "POLICYTEMPLATE-local-policy-task-scope-control-before-packaging.yaml"
)


def copy_fixture(source: Path, tmp: str, name: str = "project") -> Path:
    target = Path(tmp) / name
    shutil.copytree(source, target)
    return target


def write_mcp_project_context(root: Path) -> None:
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "latest.md").write_text("latest", encoding="utf-8")
    (docs_dir / "previous.md").write_text("previous", encoding="utf-8")
    context_path = root / ".jikuo" / "project_context.yaml"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(
        "\n".join(
            [
                'schema_version: "jikuo.project_context.v0"',
                "project:",
                '  project_id: "mcp_template_activation_fixture"',
                '  project_type: "test"',
                '  project_root_policy: "bindings_must_resolve_inside_project_root"',
                "document_roles:",
                "  latest_todo_map:",
                '    path: "docs/latest.md"',
                "    required: true",
                "  previous_todo_map:",
                '    path: "docs/previous.md"',
                "    required: true",
                "",
            ]
        ),
        encoding="utf-8",
    )


def policy_evolution_args(
    project_root: Path,
    *,
    proposal_ref: str | None = None,
    approve: bool = False,
) -> dict[str, object]:
    args: dict[str, object] = {
        "project_root": str(project_root),
        "policy_ref": "POLICY-three-phase-audit",
        "policy_evolution_operation": "supersede_policy",
        "feedback_type": "needs_scope_narrowing",
        "summary": "Replace with a narrower policy through MCP B2.",
        "policy_source_ref": "User approved MCP B2 supersession for the broad policy.",
        "replacement_policy_ref": "POLICY-three-phase-audit-mcp-v2",
        "replacement_title": "Three-phase task audit MCP v2",
        "replacement_trigger_event": "conversation_turn",
        "replacement_task_type": "work_order_delivery",
        "replacement_jikuo_layer": "testing_governance",
        "replacement_changed_path_pattern": "docs/jikuo/**",
    }
    if proposal_ref is not None:
        args["proposal_ref"] = proposal_ref
    if approve:
        args["confirm_apply"] = True
        args["approval_phrase"] = "I approve MCP B2 applying this policy supersession."
    return args


def policy_evolution_proposal_ref(response: dict[str, object]) -> str:
    data = response["data_details"]
    assert isinstance(data, dict)
    for card in data.get("cards", []):
        if not isinstance(card, dict):
            continue
        plan = card.get("policy_evolution_plan")
        if isinstance(plan, dict):
            return str(plan["proposal_ref"])
    raise AssertionError("policy evolution proposal ref not found")


class MCPStageAAdapterTests(unittest.TestCase):
    def test_tool_list_exposes_stage_a_plus_accepted_stage_b_tools_only(self):
        tools = adapter.list_tools()
        names = [tool["name"] for tool in tools]

        self.assertEqual(names, list(schemas.EXPOSED_TOOL_NAMES))
        self.assertIn("jikuo.apply_task_session_evidence_update", names)
        self.assertIn("jikuo.apply_policy_evolution_write", names)
        self.assertIn("jikuo.apply_policy_template_activation", names)
        self.assertIn("jikuo.get_configuration_status", names)
        self.assertIn("jikuo.get_activation_settings", names)
        self.assertIn("jikuo.plan_activation_settings_update", names)
        self.assertIn("jikuo.apply_activation_settings_update", names)
        self.assertIn("jikuo.route_user_request", names)
        self.assertIn("jikuo.propose_policy_suggestions", names)
        by_name = {tool["name"]: tool for tool in tools}
        for name in schemas.STAGE_A_TOOL_NAMES:
            self.assertEqual(by_name[name]["stage"], "A")
            self.assertEqual(by_name[name]["write_mode"], "no-write")
        self.assertEqual(by_name["jikuo.get_configuration_status"]["stage"], "C1")
        self.assertEqual(
            by_name["jikuo.get_configuration_status"]["write_mode"],
            "no-write",
        )
        self.assertEqual(by_name["jikuo.get_activation_settings"]["stage"], "C1")
        self.assertEqual(by_name["jikuo.get_activation_settings"]["write_mode"], "no-write")
        self.assertEqual(by_name["jikuo.plan_activation_settings_update"]["stage"], "C1")
        self.assertEqual(
            by_name["jikuo.plan_activation_settings_update"]["write_mode"],
            "no-write",
        )
        self.assertEqual(by_name["jikuo.apply_activation_settings_update"]["stage"], "C2")
        self.assertEqual(
            by_name["jikuo.apply_activation_settings_update"]["write_mode"],
            "guarded-write",
        )
        self.assertEqual(by_name["jikuo.route_user_request"]["stage"], "R1")
        self.assertEqual(by_name["jikuo.route_user_request"]["write_mode"], "no-write")
        self.assertEqual(by_name["jikuo.propose_policy_suggestions"]["stage"], "R1")
        self.assertEqual(
            by_name["jikuo.propose_policy_suggestions"]["write_mode"],
            "no-write",
        )
        self.assertEqual(
            by_name["jikuo.apply_task_session_evidence_update"]["stage"],
            "B1",
        )
        self.assertEqual(
            by_name["jikuo.apply_task_session_evidence_update"]["write_mode"],
            "guarded-write",
        )
        self.assertEqual(by_name["jikuo.apply_policy_evolution_write"]["stage"], "B2")
        self.assertEqual(
            by_name["jikuo.apply_policy_evolution_write"]["write_mode"],
            "guarded-write",
        )
        self.assertEqual(
            by_name["jikuo.apply_policy_template_activation"]["stage"],
            "B3",
        )
        self.assertEqual(
            by_name["jikuo.apply_policy_template_activation"]["write_mode"],
            "guarded-write",
        )

    def test_status_wraps_policy_store_without_runtime_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)

            response = adapter.call_tool(
                "jikuo.status",
                {"project_root": str(project_root)},
            )

            self.assertEqual(response["schema"], schemas.ADAPTER_RESULT_SCHEMA)
            self.assertEqual(response["tool_name"], "jikuo.status")
            self.assertEqual(response["policy_store_status"], "active")
            self.assertEqual(response["field_classification"]["local_paths"], schemas.LOCAL_ONLY)
            self.assertNotIn("local_paths", response)
            self.assertFalse((project_root / ".jikuo" / "runtime").exists())

    def test_propose_task_start_updates_runtime_only_and_sanitizes_unknown_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)

            response = adapter.call_tool(
                "jikuo.propose_task_start",
                {
                    "project_root": str(project_root),
                    "task_title": "MCP adapter smoke",
                    "task_type": "code_change",
                    "jikuo_layer": "implementation_governance",
                    "changed_paths": ["src/jikuo/integrations/mcp/adapter.py"],
                    "work_routing_category": "taskmap",
                    "work_routing_summary": "Adapter smoke remains inside Stage A scope.",
                },
            )

            self.assertEqual(response["tool_name"], "jikuo.propose_task_start")
            self.assertEqual(response["work_profile"]["schema"], "jikuo.work_profile.v0")
            self.assertEqual(response["work_profile"]["lifecycle_event"], "task_start")
            self.assertEqual(response["work_profile"]["operation_class"], "write_file")
            self.assertIn("editing", response["work_profile"]["policy_scopes"])
            self.assertIn("card_markdown", response)
            self.assertEqual(response["display"]["must_show_verbatim"], ["card_markdown"])
            self.assertEqual(
                response["display"]["card_priority_order"][0],
                "policy_runtime_status",
            )
            self.assertEqual(
                response["display_verification"]["runtime_snapshot_path_relative"],
                ".jikuo/runtime/last_card.md",
            )
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

            serialized = json.dumps(response, ensure_ascii=False)
            self.assertNotIn(str(project_root.resolve()), serialized)
            self.assertIn("<LOCAL_PROJECT_ROOT>", serialized)

    def test_local_stdio_transport_can_return_local_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)

            response = adapter.call_tool(
                "jikuo.propose_task_start",
                {
                    "project_root": str(project_root),
                    "task_title": "MCP adapter local stdio",
                },
                transport=schemas.LOCAL_STDIO_TRANSPORT,
            )

            self.assertIn("local_paths", response)
            self.assertEqual(
                response["local_paths"]["last_card"],
                str((project_root / ".jikuo" / "runtime" / "last_card.md").resolve()),
            )

    def test_propose_task_start_accepts_explicit_deferral_arguments(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)

            response = adapter.call_tool(
                "jikuo.propose_task_start",
                {
                    "project_root": str(project_root),
                    "task_title": "MCP deferral smoke",
                    "task_session_decision": "defer",
                    "task_session_defer_reason": "lightweight discussion only",
                },
                transport=schemas.LOCAL_STDIO_TRANSPORT,
            )

            self.assertEqual(response["tool_name"], "jikuo.propose_task_start")
            cards = response["data_details"]["cards"]
            self.assertEqual(cards[0]["card_kind"], "task_start_processing")
            self.assertEqual(cards[1]["card_kind"], "task_session_binding")
            self.assertEqual(
                cards[1]["task_session_resolution"]["status"],
                "explicitly_deferred",
            )
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_get_configuration_status_returns_review_and_runtime_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)

            response = adapter.call_tool(
                "jikuo.get_configuration_status",
                {"project_root": str(project_root)},
            )

            self.assertEqual(response["tool_name"], "jikuo.get_configuration_status")
            self.assertEqual(response["write_mode"], "no-write")
            self.assertIn(response["configuration_status"], {"ok", "review", "blocked"})
            self.assertEqual(
                response["configuration_review"]["schema"],
                "jikuo.configuration_review.v0",
            )
            self.assertIn("## jikuo configuration review", response["card_markdown"].lower())
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())
            serialized = json.dumps(response, ensure_ascii=False)
            self.assertNotIn(str(project_root.resolve()), serialized)

    def test_activation_settings_tools_are_no_write_and_card_returning(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            status_response = adapter.call_tool(
                "jikuo.get_activation_settings",
                {"project_root": str(project_root)},
            )
            plan_response = adapter.call_tool(
                "jikuo.plan_activation_settings_update",
                {
                    "project_root": str(project_root),
                    "trigger_mode": "mounted",
                    "effective_enforcement_level": "instruction_only",
                    "clients": ["claude-code"],
                },
            )

            self.assertEqual(status_response["tool_name"], "jikuo.get_activation_settings")
            self.assertEqual(status_response["activation_settings"]["status"], "missing")
            self.assertTrue(status_response["activation_settings"]["onboarding_required"])
            self.assertEqual(
                status_response["activation_settings"]["required_user_decisions"][0]["field"],
                "desired_trigger_mode",
            )
            self.assertIn("# JIKUO Activation Settings", status_response["card_markdown"])
            self.assertEqual(
                plan_response["tool_name"],
                "jikuo.plan_activation_settings_update",
            )
            self.assertEqual(
                plan_response["activation_settings_plan"]["desired_trigger_mode"],
                "mounted",
            )
            self.assertFalse((project_root / ".jikuo" / "activation_settings.yaml").exists())
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())

    def test_apply_activation_settings_update_is_guarded_and_redacts_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            refused = adapter.call_tool(
                "jikuo.apply_activation_settings_update",
                {
                    "project_root": str(project_root),
                    "trigger_mode": "mounted",
                    "clients": ["claude-code"],
                },
            )

            self.assertEqual(refused["status"], "refused")
            self.assertFalse(refused["write_performed"])
            self.assertIn("confirm_apply_required", refused["refusal_reasons"])
            self.assertFalse((project_root / ".jikuo" / "activation_settings.yaml").exists())

            applied = adapter.call_tool(
                "jikuo.apply_activation_settings_update",
                {
                    "project_root": str(project_root),
                    "trigger_mode": "mounted",
                    "effective_enforcement_level": "instruction_only",
                    "clients": ["claude-code"],
                    "confirm_apply": True,
                    "approval_phrase": "I approve activation settings update.",
                },
            )

            self.assertEqual(applied["status"], "ok")
            self.assertTrue(applied["write_performed"])
            self.assertEqual(
                applied["target_result_schema"],
                "jikuo.activation_settings_result.v0",
            )
            self.assertEqual(
                applied["written_refs"],
                [".jikuo/activation_settings.yaml"],
            )
            settings_text = (
                project_root / ".jikuo" / "activation_settings.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn('desired_trigger_mode: "mounted"', settings_text)
            serialized = json.dumps(applied, ensure_ascii=False)
            self.assertNotIn("I approve activation settings update.", serialized)
            self.assertIn("<REDACTED>", serialized)

    def test_route_user_request_returns_mcp_followup_tools_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            response = adapter.call_tool(
                "jikuo.route_user_request",
                {
                    "project_root": str(project_root),
                    "user_phrase": "please show setup settings",
                    "trigger_mode": "semantic",
                },
            )

            self.assertEqual(response["tool_name"], "jikuo.route_user_request")
            self.assertEqual(response["write_mode"], "no-write")
            self.assertEqual(response["work_profile"]["schema"], "jikuo.work_profile.v0")
            self.assertEqual(
                response["work_profile"]["lifecycle_event"],
                "conversation_turn",
            )
            self.assertEqual(response["work_profile"]["intent_class"], "configuration")
            self.assertEqual(
                response["conversation_router"]["schema"],
                "jikuo.conversation_turn_router.v0",
            )
            kinds = {
                obligation["kind"]
                for obligation in response["classified_obligations"]
            }
            self.assertIn("configuration_review", kinds)
            self.assertIn("jikuo.get_configuration_status", response["mcp_followup_tools"])
            self.assertIn("Conversation-turn router", response["card_markdown"])
            self.assertEqual(
                response["display"]["card_priority_order"][1],
                "conversation_turn_router",
            )
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())
            self.assertFalse((project_root / ".jikuo" / "policies").exists())
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())
            self.assertFalse((project_root / ".jikuo" / "project_state.yaml").exists())

    def test_route_user_request_prompts_activation_configuration_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            response = adapter.call_tool(
                "jikuo.route_user_request",
                {
                    "project_root": str(project_root),
                    "user_phrase": "continue the NarrativeSystem cleanup",
                },
            )

            router = response["conversation_router"]
            self.assertEqual(router["activation_settings"]["status"], "missing")
            self.assertTrue(router["activation_settings"]["onboarding_required"])
            self.assertEqual(
                router["activation_settings"]["strict_mount_status"],
                "not_configured",
            )
            self.assertEqual(
                response["classified_obligations"][0]["kind"],
                "configuration_review",
            )
            self.assertIn("task_start", {
                item["kind"] for item in response["classified_obligations"]
            })
            self.assertIn("jikuo.get_configuration_status", response["mcp_followup_tools"])
            self.assertIn("JIKUO Runtime Links", response["card_markdown"])
            self.assertFalse((project_root / ".jikuo" / "activation_settings.yaml").exists())

    def test_propose_policy_suggestions_returns_candidates_without_policy_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            response = adapter.call_tool(
                "jikuo.propose_policy_suggestions",
                {
                    "project_root": str(project_root),
                    "user_phrase": (
                        "I keep asking for progress, todo, and business meaning "
                        "because this repeated need should become a policy."
                    ),
                    "trigger_mode": "mounted",
                },
            )

            self.assertEqual(response["tool_name"], "jikuo.propose_policy_suggestions")
            self.assertEqual(response["write_mode"], "no-write")
            self.assertEqual(
                response["policy_suggestion_review"]["schema"],
                "jikuo.proactive_policy_suggestion_review.v0",
            )
            self.assertEqual(response["policy_candidate_count"], 1)
            self.assertEqual(
                response["policy_suggestion_review"]["candidate_count"],
                1,
            )
            self.assertFalse(
                response["policy_suggestion_review"]["privacy"]["raw_transcript_captured"]
            )
            self.assertNotIn(
                "jikuo.propose_policy_suggestions",
                response["mcp_followup_tools"],
            )
            self.assertIn("Proactive policy-suggestion review", response["card_markdown"])
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())
            self.assertFalse((project_root / ".jikuo" / "policies").exists())
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_get_display_card_reads_latest_runtime_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)
            adapter.call_tool(
                "jikuo.propose_task_start",
                {"project_root": str(project_root), "task_title": "Seed card"},
            )

            response = adapter.call_tool(
                "jikuo.get_display_card",
                {"project_root": str(project_root)},
            )

            self.assertEqual(response["status"], "available")
            self.assertIn("## Policy runtime status", response["card_markdown"])
            self.assertEqual(
                response["display_verification"]["runtime_snapshot_path_relative"],
                ".jikuo/runtime/last_card.md",
            )

    def test_get_runtime_status_card_returns_card_only_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)

            response = adapter.call_tool(
                "jikuo.get_runtime_status_card",
                {"project_root": str(project_root)},
            )

            self.assertIn("## Policy runtime status", response["card_markdown"])
            self.assertNotIn("# JIKUO Agent Flow Proposal", response["card_markdown"])
            last_card = project_root / ".jikuo" / "runtime" / "last_card.md"
            self.assertTrue(last_card.is_file())
            self.assertEqual(last_card.read_text(encoding="utf-8"), response["card_markdown"])
            show_card, show_report = runtime_visibility.load_last_card(
                project_root=project_root
            )
            self.assertEqual(show_report["status"], "available")
            self.assertEqual(show_card, response["card_markdown"])

    def test_stage_a_proposal_tools_return_display_verification_without_governance_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)
            calls = [
                (
                    "jikuo.propose_policy_write_plan",
                    {
                        "project_root": str(project_root),
                        "policy_ref": "POLICY-mcp-adapter-smoke",
                        "policy_title": "MCP adapter smoke",
                        "policy_source_ref": "<exact user phrase as spoken>",
                    },
                ),
                (
                    "jikuo.propose_policy_evolution_plan",
                    {
                        "project_root": str(project_root),
                        "policy_ref": "POLICY-three-phase-audit",
                        "policy_evolution_operation": "refine_policy",
                        "feedback_type": "needs_scope_narrowing",
                        "summary": "Adapter smoke.",
                    },
                ),
                (
                    "jikuo.propose_policy_template_import_plan",
                    {
                        "project_root": str(project_root),
                        "template": str(POLICY_TEMPLATE),
                    },
                ),
            ]

            for tool_name, arguments in calls:
                with self.subTest(tool_name=tool_name):
                    response = adapter.call_tool(tool_name, arguments)
                    self.assertEqual(response["tool_name"], tool_name)
                    self.assertIn("card_markdown", response)
                    self.assertIn("display_verification", response)
                    self.assertEqual(
                        response["runtime_snapshot_ref"],
                        ".jikuo/runtime/last_card.md",
                    )

            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())
            self.assertFalse(
                (project_root / ".jikuo" / "policies" / "approved" / "POLICY-mcp-adapter-smoke.yaml").exists()
            )

    def test_stage_b1_task_session_evidence_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_EVIDENCE_SESSION_PROJECT, tmp)
            session_file = (
                project_root
                / ".jikuo"
                / "task_sessions"
                / "task_policy_evidence_probe.yaml"
            )
            before_text = session_file.read_text(encoding="utf-8")

            response = adapter.call_tool(
                "jikuo.apply_task_session_evidence_update",
                {
                    "project_root": str(project_root),
                    "session_id": "task_policy_evidence_probe",
                    "evidence_kind": "policy_feedback:not_applicable",
                    "evidence_ref": "policy_ref=POLICY-real-test-data-and-chain",
                    "summary": "User marked this policy not applicable.",
                },
            )

            self.assertEqual(response["tool_name"], "jikuo.apply_task_session_evidence_update")
            self.assertEqual(response["stage"], "B1")
            self.assertEqual(response["write_mode"], "guarded-write")
            self.assertEqual(response["status"], "refused")
            self.assertFalse(response["write_performed"])
            self.assertIn("missing_confirmation_flag", response["refusal_reasons"])
            self.assertIn("approval_evidence_missing", response["refusal_reasons"])
            self.assertIn("# JIKUO Agent Flow Apply Result", response["card_markdown"])
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())
            self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_stage_b1_task_session_evidence_writes_after_approval_only_to_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_EVIDENCE_SESSION_PROJECT, tmp)
            session_file = (
                project_root
                / ".jikuo"
                / "task_sessions"
                / "task_policy_evidence_probe.yaml"
            )
            project_state_file = project_root / ".jikuo" / "project_state.yaml"
            before_state = project_state_file.read_text(encoding="utf-8")

            response = adapter.call_tool(
                "jikuo.apply_task_session_evidence_update",
                {
                    "project_root": str(project_root),
                    "session_id": "task_policy_evidence_probe",
                    "evidence_kind": "policy_feedback:not_applicable",
                    "evidence_ref": "policy_ref=POLICY-real-test-data-and-chain",
                    "summary": "User marked this policy not applicable through MCP B1.",
                    "confirm_apply": True,
                    "approval_phrase": "I approve this task-session evidence append.",
                },
                transport=schemas.LOCAL_STDIO_TRANSPORT,
            )

            self.assertEqual(response["status"], "applied")
            self.assertTrue(response["write_performed"])
            self.assertEqual(
                response["target_result_schema"],
                "jikuo.task_session_update_result.v0",
            )
            self.assertIn("local_paths", response)
            self.assertEqual(
                response["display_verification"]["runtime_snapshot_path_relative"],
                ".jikuo/runtime/last_card.md",
            )
            self.assertNotIn("I approve this task-session evidence append.", json.dumps(response))
            tool = schemas.tool_definition("jikuo.apply_task_session_evidence_update")
            self.assertEqual(
                tool["input_fields"]["approval_phrase"],
                schemas.REDACT_REQUIRED,
            )
            updated = session_file.read_text(encoding="utf-8")
            self.assertIn("policy_feedback:not_applicable", updated)
            self.assertIn("User marked this policy not applicable through MCP B1.", updated)
            self.assertEqual(project_state_file.read_text(encoding="utf-8"), before_state)
            self.assertFalse((project_root / ".jikuo" / "policies").exists())

    def test_stage_b2_policy_evolution_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)
            manifest_file = project_root / ".jikuo" / "policies" / "manifest.yaml"
            before_text = manifest_file.read_text(encoding="utf-8")

            response = adapter.call_tool(
                "jikuo.apply_policy_evolution_write",
                policy_evolution_args(project_root),
            )

            self.assertEqual(response["tool_name"], "jikuo.apply_policy_evolution_write")
            self.assertEqual(response["stage"], "B2")
            self.assertEqual(response["write_mode"], "guarded-write")
            self.assertEqual(response["status"], "refused")
            self.assertFalse(response["write_performed"])
            self.assertIn("missing_confirmation_flag", response["refusal_reasons"])
            self.assertIn("approval_evidence_missing", response["refusal_reasons"])
            self.assertIn(
                "proposal_ref_required_for_policy_evolution_apply",
                response["refusal_reasons"],
            )
            self.assertEqual(response["proposal_binding"]["status"], "missing")
            self.assertIn("# JIKUO Agent Flow Apply Result", response["card_markdown"])
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())
            self.assertEqual(manifest_file.read_text(encoding="utf-8"), before_text)

    def test_stage_b2_policy_evolution_writes_after_proposal_bound_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)
            manifest_file = project_root / ".jikuo" / "policies" / "manifest.yaml"

            plan = adapter.call_tool(
                "jikuo.propose_policy_evolution_plan",
                policy_evolution_args(project_root),
            )
            proposal_ref = policy_evolution_proposal_ref(plan)
            response = adapter.call_tool(
                "jikuo.apply_policy_evolution_write",
                policy_evolution_args(
                    project_root,
                    proposal_ref=proposal_ref,
                    approve=True,
                ),
                transport=schemas.LOCAL_STDIO_TRANSPORT,
            )

            self.assertEqual(response["status"], "applied")
            self.assertTrue(response["write_performed"])
            self.assertEqual(response["proposal_binding"]["status"], "ok")
            self.assertEqual(response["proposal_binding"]["provided_ref"], proposal_ref)
            self.assertEqual(response["proposal_binding"]["expected_ref"], proposal_ref)
            self.assertEqual(response["target_result_schema"], "jikuo.policy_write_result.v0")
            target = response["target_result"]
            self.assertEqual(target["status"], "written")
            self.assertEqual(target["operation"], "supersede_policy")
            self.assertEqual(target["replacement_policy_ref"], "POLICY-three-phase-audit-mcp-v2")
            replacement_policy = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-three-phase-audit-mcp-v2.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn('event: "conversation_turn"', replacement_policy)
            self.assertTrue(target["post_write_verification"]["target_policy_superseded"])
            self.assertTrue(target["post_write_verification"]["replacement_policy_active"])
            self.assertNotIn(
                "I approve MCP B2 applying this policy supersession.",
                json.dumps(response),
            )
            tool = schemas.tool_definition("jikuo.apply_policy_evolution_write")
            self.assertEqual(tool["input_fields"]["approval_phrase"], schemas.REDACT_REQUIRED)
            self.assertIn("superseded_policy_refs:", manifest_file.read_text(encoding="utf-8"))
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())

    def test_stage_b3_policy_template_activation_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "template_project"
            project_root.mkdir()
            write_mcp_project_context(project_root)

            response = adapter.call_tool(
                "jikuo.apply_policy_template_activation",
                {
                    "project_root": str(project_root),
                    "template": str(POLICY_TEMPLATE),
                },
            )

            self.assertEqual(response["tool_name"], "jikuo.apply_policy_template_activation")
            self.assertEqual(response["stage"], "B3")
            self.assertEqual(response["write_mode"], "guarded-write")
            self.assertEqual(response["status"], "refused")
            self.assertFalse(response["write_performed"])
            self.assertEqual(
                response["target_result_schema"],
                "jikuo.policy_template_activation_result.v0",
            )
            self.assertIn("missing_confirmation_flag", response["refusal_reasons"])
            self.assertIn("approval_evidence_missing", response["refusal_reasons"])
            self.assertIn("# JIKUO Agent Flow Apply Result", response["card_markdown"])
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())
            self.assertFalse((project_root / ".jikuo" / "policies").exists())

    def test_stage_b3_policy_template_activation_writes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "template_project"
            project_root.mkdir()
            write_mcp_project_context(project_root)

            response = adapter.call_tool(
                "jikuo.apply_policy_template_activation",
                {
                    "project_root": str(project_root),
                    "template": str(POLICY_TEMPLATE),
                    "confirm_apply": True,
                    "approval_phrase": "I approve MCP B3 activating this policy template.",
                },
                transport=schemas.LOCAL_STDIO_TRANSPORT,
            )

            self.assertEqual(response["status"], "applied")
            self.assertTrue(response["write_performed"])
            self.assertEqual(
                response["target_result_schema"],
                "jikuo.policy_template_activation_result.v0",
            )
            target = response["target_result"]
            self.assertEqual(target["status"], "written")
            self.assertEqual(
                target["policy_ref"],
                "POLICY-task-scope-control-before-packaging",
            )
            self.assertTrue(target["post_write_verification"]["policy_active"])
            self.assertNotIn(
                "I approve MCP B3 activating this policy template.",
                json.dumps(response),
            )
            tool = schemas.tool_definition("jikuo.apply_policy_template_activation")
            self.assertEqual(tool["input_fields"]["approval_phrase"], schemas.REDACT_REQUIRED)
            approved_path = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-task-scope-control-before-packaging.yaml"
            )
            self.assertTrue(approved_path.is_file())
            self.assertIn("resolved_bindings:", approved_path.read_text(encoding="utf-8"))
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())


if __name__ == "__main__":
    unittest.main()
