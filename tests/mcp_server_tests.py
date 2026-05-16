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


class MCPServerWrapperTests(unittest.TestCase):
    def test_create_server_registers_stage_a_plus_accepted_stage_b_tools_only(self):
        fake = server.create_server(fastmcp_cls=FakeFastMCP)

        self.assertEqual(fake.name, server.SERVER_NAME)
        self.assertEqual(list(fake.tools), list(schemas.EXPOSED_TOOL_NAMES))
        self.assertIn("jikuo.apply_task_session_evidence_update", fake.tools)
        self.assertIn("jikuo.apply_policy_evolution_write", fake.tools)
        self.assertIn("jikuo.apply_policy_template_activation", fake.tools)

    def test_card_tool_descriptions_include_display_contract(self):
        fake = server.create_server(fastmcp_cls=FakeFastMCP)

        card_description = fake.tools["jikuo.get_runtime_status_card"]["description"]
        plain_description = fake.tools["jikuo.status"]["description"]

        self.assertIn("CRITICAL DISPLAY CONTRACT", card_description)
        self.assertIn("card_markdown", card_description)
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
