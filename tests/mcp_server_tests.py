import asyncio
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jikuo.integrations.mcp import schemas, server


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
                '  project_id: "mcp_server_template_activation_fixture"',
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


def policy_evolution_args(project_root: Path) -> dict[str, object]:
    return {
        "project_root": str(project_root),
        "policy_ref": "POLICY-three-phase-audit",
        "policy_evolution_operation": "supersede_policy",
        "feedback_type": "needs_scope_narrowing",
        "summary": "Replace with a narrower policy through MCP server B2.",
        "policy_source_ref": "User approved MCP server B2 supersession.",
        "replacement_policy_ref": "POLICY-three-phase-audit-server-v2",
        "replacement_title": "Three-phase task audit server v2",
        "replacement_trigger_event": "conversation_turn",
        "replacement_task_type": "work_order_delivery",
        "replacement_jikuo_layer": "testing_governance",
        "replacement_changed_path_pattern": "docs/jikuo/**",
    }


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


class FakeFastMCP:
    def __init__(self, name, instructions=None):
        self.name = name
        self.instructions = instructions
        self.tools = {}
        self.run_calls = []

    def tool(self, *, name, description):
        def decorate(fn):
            self.tools[name] = {
                "description": description,
                "function": fn,
            }
            return fn

        return decorate

    def run(self, *args, **kwargs):
        self.run_calls.append({"args": args, "kwargs": kwargs})


class FakeSamplingContent:
    def __init__(self, text: str):
        self.text = text


class FakeSamplingResult:
    def __init__(self, text: str):
        self.content = FakeSamplingContent(text)
        self.model = "fake-client-model"
        self.stopReason = "endTurn"


class FakeSamplingSession:
    def __init__(self, text: str | None = None, error: Exception | None = None):
        self.text = text
        self.error = error
        self.calls = []

    async def create_message(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return FakeSamplingResult(self.text or "{}")


class FakeSamplingContext:
    def __init__(self, session: FakeSamplingSession):
        self.session = session
        self.request_id = "request-1"


class MCPServerWrapperTests(unittest.TestCase):
    def test_create_server_registers_stage_a_plus_accepted_stage_b_tools_only(self):
        fake = server.create_server(fastmcp_cls=FakeFastMCP)

        self.assertEqual(fake.name, server.SERVER_NAME)
        self.assertEqual(list(fake.tools), list(schemas.EXPOSED_TOOL_NAMES))
        self.assertIn("jikuo.get_configuration_status", fake.tools)
        self.assertIn("jikuo.get_activation_settings", fake.tools)
        self.assertIn("jikuo.plan_activation_settings_update", fake.tools)
        self.assertIn("jikuo.apply_activation_settings_update", fake.tools)
        self.assertIn("jikuo.route_user_request", fake.tools)
        self.assertIn("jikuo.propose_policy_suggestions", fake.tools)
        self.assertIn("jikuo.probe_sampling_semantic_intent", fake.tools)
        self.assertIn("jikuo.apply_task_session_evidence_update", fake.tools)
        self.assertIn("jikuo.apply_policy_evolution_write", fake.tools)
        self.assertIn("jikuo.apply_policy_template_activation", fake.tools)

    def test_card_tool_descriptions_include_display_contract(self):
        fake = server.create_server(fastmcp_cls=FakeFastMCP)

        card_description = fake.tools["jikuo.get_runtime_status_card"]["description"]
        config_description = fake.tools["jikuo.get_configuration_status"]["description"]
        plain_description = fake.tools["jikuo.status"]["description"]

        self.assertIn("CRITICAL DISPLAY CONTRACT", card_description)
        self.assertIn("card_markdown", card_description)
        self.assertIn("CRITICAL DISPLAY CONTRACT", config_description)
        self.assertNotIn("CRITICAL DISPLAY CONTRACT", plain_description)

    def test_registered_tool_calls_adapter_without_mcp_sdk(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)
            fake = server.create_server(
                fastmcp_cls=FakeFastMCP,
                default_transport=schemas.UNKNOWN_TRANSPORT,
            )

            response = fake.tools["jikuo.get_runtime_status_card"]["function"](
                project_root=str(project_root),
            )

            self.assertEqual(response["tool_name"], "jikuo.get_runtime_status_card")
            self.assertIn("## Policy runtime status", response["card_markdown"])
            self.assertNotIn(str(project_root.resolve()), str(response))
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())

    def test_policy_write_plan_registered_tool_passes_work_profile_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)
            fake = server.create_server(fastmcp_cls=FakeFastMCP)

            response = fake.tools["jikuo.propose_policy_write_plan"]["function"](
                project_root=str(project_root),
                policy_ref="POLICY-server-work-profile-smoke",
                policy_title="Server work profile smoke",
                policy_work_profile_lifecycle_events=["task_start"],
                policy_work_profile_policy_scopes=["discussion", "editing"],
            )

            plan = response["data_details"]["cards"][0]["policy_write_plan"]
            self.assertEqual(
                plan["proposed_policy"]["applies_to_work_profile"],
                [
                    {
                        "lifecycle_events": ["task_start"],
                        "policy_scopes": ["discussion", "editing"],
                    }
                ],
            )

    def test_configuration_status_registered_tool_delegates_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)
            fake = server.create_server(fastmcp_cls=FakeFastMCP)

            response = fake.tools["jikuo.get_configuration_status"]["function"](
                project_root=str(project_root),
            )

            self.assertEqual(response["tool_name"], "jikuo.get_configuration_status")
            self.assertEqual(
                response["configuration_review"]["schema"],
                "jikuo.configuration_review.v0",
            )
        self.assertIn("card_markdown", response)

    def test_activation_settings_registered_tools_delegate_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            fake = server.create_server(fastmcp_cls=FakeFastMCP)

            status_response = fake.tools["jikuo.get_activation_settings"]["function"](
                project_root=str(project_root),
            )
            plan_response = fake.tools[
                "jikuo.plan_activation_settings_update"
            ]["function"](
                project_root=str(project_root),
                trigger_mode="semantic",
                effective_enforcement_level="instruction_only",
                clients=["codex"],
            )

            self.assertEqual(
                status_response["activation_settings"]["schema"],
                "jikuo.activation_settings_status.v0",
            )
            self.assertEqual(
                plan_response["activation_settings_plan"]["schema"],
                "jikuo.activation_settings_plan.v0",
            )
            self.assertFalse((project_root / ".jikuo" / "activation_settings.yaml").exists())

    def test_apply_activation_settings_registered_tool_delegates_guarded_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            fake = server.create_server(fastmcp_cls=FakeFastMCP)

            response = fake.tools["jikuo.apply_activation_settings_update"]["function"](
                project_root=str(project_root),
                trigger_mode="semantic",
                effective_enforcement_level="instruction_only",
                clients=["codex"],
                confirm_apply=True,
                approval_phrase="I approve MCP activation settings apply.",
            )

            self.assertEqual(response["tool_name"], "jikuo.apply_activation_settings_update")
            self.assertEqual(response["status"], "ok")
            self.assertTrue(response["write_performed"])
            self.assertTrue((project_root / ".jikuo" / "activation_settings.yaml").is_file())
            self.assertNotIn(
                "I approve MCP activation settings apply.",
                str(response),
            )

    def test_router_registered_tools_delegate_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            fake = server.create_server(fastmcp_cls=FakeFastMCP)

            route_response = fake.tools["jikuo.route_user_request"]["function"](
                project_root=str(project_root),
                user_phrase="please show setup settings",
                trigger_mode="semantic",
            )
            policy_response = fake.tools["jikuo.propose_policy_suggestions"]["function"](
                project_root=str(project_root),
                user_phrase=(
                    "I keep asking for progress, todo, and business meaning "
                    "because this repeated need should become a policy."
                ),
                trigger_mode="mounted",
            )

            self.assertEqual(route_response["tool_name"], "jikuo.route_user_request")
            self.assertIn("jikuo.get_configuration_status", route_response["mcp_followup_tools"])
            self.assertEqual(
                policy_response["tool_name"],
                "jikuo.propose_policy_suggestions",
            )
            self.assertEqual(policy_response["policy_candidate_count"], 1)
            self.assertFalse((project_root / ".jikuo" / "policies").exists())
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_sampling_semantic_tool_uses_client_sampling_then_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            fake = server.create_server(fastmcp_cls=FakeFastMCP)
            sampling_json = json.dumps(
                {
                    "provider": "mcp_sampling",
                    "confidence": "high",
                    "policy_scopes": ["editing"],
                    "work_profile": {
                        "policy_scopes": ["editing"],
                        "intent_class": "implementation_request",
                        "operation_class": "documentation_update",
                        "output_class": "repository_change",
                    },
                    "rationale_summary": "The user asked for a documentation update.",
                }
            )
            session = FakeSamplingSession(sampling_json)

            response = asyncio.run(
                fake.tools["jikuo.probe_sampling_semantic_intent"]["function"](
                    project_root=str(project_root),
                    user_phrase="Please update the hook docs.",
                    trigger_mode="mounted",
                    source_client="codex",
                    ctx=FakeSamplingContext(session),
                )
            )

            self.assertEqual(response["tool_name"], "jikuo.probe_sampling_semantic_intent")
            self.assertEqual(response["sampling_semantic_intent"]["status"], "provided")
            self.assertEqual(response["sampling_semantic_intent"]["model"], "fake-client-model")
            self.assertEqual(
                response["work_profile"]["basis"]["host_semantic_intent"]["provider"],
                "mcp_sampling",
            )
            self.assertIn("editing", response["work_profile"]["policy_scopes"])
            self.assertEqual(session.calls[0]["include_context"], "none")
            serialized = json.dumps(response, ensure_ascii=False)
            self.assertNotIn("Please update the hook docs.", serialized)

    def test_sampling_semantic_tool_falls_back_when_client_sampling_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            fake = server.create_server(fastmcp_cls=FakeFastMCP)
            secret_prompt = "SECRET_PROMPT_VALUE please update docs"
            session = FakeSamplingSession(error=RuntimeError(f"sampling failed: {secret_prompt}"))

            response = asyncio.run(
                fake.tools["jikuo.probe_sampling_semantic_intent"]["function"](
                    project_root=str(project_root),
                    user_phrase=secret_prompt,
                    trigger_mode="semantic",
                    source_client="codex",
                    ctx=FakeSamplingContext(session),
                )
            )

            self.assertEqual(response["sampling_semantic_intent"]["status"], "unavailable")
            self.assertEqual(
                response["work_profile"]["basis"]["host_semantic_intent"]["status"],
                "unavailable",
            )
            self.assertEqual(response["host_semantic_intent"]["status"], "unavailable")
            serialized = json.dumps(response, ensure_ascii=False)
            self.assertNotIn(secret_prompt, serialized)
            self.assertIn("<REDACTED_PROMPT_ECHO>", serialized)

    def test_stage_b1_registered_tool_delegates_guarded_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_EVIDENCE_SESSION_PROJECT, tmp)
            fake = server.create_server(fastmcp_cls=FakeFastMCP)

            response = fake.tools["jikuo.apply_task_session_evidence_update"]["function"](
                project_root=str(project_root),
                session_id="task_policy_evidence_probe",
                evidence_kind="policy_feedback:not_applicable",
                evidence_ref="policy_ref=POLICY-real-test-data-and-chain",
                summary="User marked this policy not applicable through MCP server.",
                confirm_apply=True,
                approval_phrase="I approve this task-session evidence append.",
            )

            self.assertEqual(
                response["tool_name"],
                "jikuo.apply_task_session_evidence_update",
            )
            self.assertEqual(response["status"], "applied")
            self.assertTrue(response["write_performed"])
            self.assertIn("# JIKUO Agent Flow Apply Result", response["card_markdown"])
            self.assertNotIn(
                "I approve this task-session evidence append.",
                str(response),
            )

    def test_stage_b2_registered_tool_delegates_guarded_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = copy_fixture(POLICY_ACTIVE_PROJECT, tmp)
            fake = server.create_server(fastmcp_cls=FakeFastMCP)
            plan = fake.tools["jikuo.propose_policy_evolution_plan"]["function"](
                **policy_evolution_args(project_root),
            )
            proposal_ref = policy_evolution_proposal_ref(plan)

            response = fake.tools["jikuo.apply_policy_evolution_write"]["function"](
                **policy_evolution_args(project_root),
                proposal_ref=proposal_ref,
                confirm_apply=True,
                approval_phrase="I approve MCP server B2 applying this policy supersession.",
            )

            self.assertEqual(response["tool_name"], "jikuo.apply_policy_evolution_write")
            self.assertEqual(response["status"], "applied")
            self.assertTrue(response["write_performed"])
            self.assertEqual(response["proposal_binding"]["status"], "ok")
            replacement_policy = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-three-phase-audit-server-v2.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn('event: "conversation_turn"', replacement_policy)
            self.assertIn("# JIKUO Agent Flow Apply Result", response["card_markdown"])
            self.assertNotIn(
                "I approve MCP server B2 applying this policy supersession.",
                str(response),
            )
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_stage_b3_registered_tool_delegates_guarded_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "template_project"
            project_root.mkdir()
            write_mcp_project_context(project_root)
            fake = server.create_server(fastmcp_cls=FakeFastMCP)

            response = fake.tools["jikuo.apply_policy_template_activation"]["function"](
                project_root=str(project_root),
                template=str(POLICY_TEMPLATE),
                confirm_apply=True,
                approval_phrase="I approve MCP server B3 activating this policy template.",
            )

            self.assertEqual(
                response["tool_name"],
                "jikuo.apply_policy_template_activation",
            )
            self.assertEqual(response["status"], "applied")
            self.assertTrue(response["write_performed"])
            self.assertIn("# JIKUO Agent Flow Apply Result", response["card_markdown"])
            self.assertNotIn(
                "I approve MCP server B3 activating this policy template.",
                str(response),
            )
            self.assertTrue(
                (
                    project_root
                    / ".jikuo"
                    / "policies"
                    / "approved"
                    / "POLICY-task-scope-control-before-packaging.yaml"
                ).is_file()
            )
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

    def test_main_uses_stdio_run_by_default(self):
        created = []

        class RecordingFastMCP(FakeFastMCP):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                created.append(self)

        original_loader = server.load_fastmcp_class
        try:
            server.load_fastmcp_class = lambda: RecordingFastMCP
            exit_code = server.main([])
        finally:
            server.load_fastmcp_class = original_loader

        self.assertEqual(exit_code, 0)
        self.assertEqual(created[0].run_calls, [{"args": (), "kwargs": {}}])


if __name__ == "__main__":
    unittest.main()
