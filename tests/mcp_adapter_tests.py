import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jikuo.integrations.mcp import adapter, schemas


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
POLICY_ACTIVE_PROJECT = FIXTURES / "policy_store_active_project"
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


class MCPStageAAdapterTests(unittest.TestCase):
    def test_tool_list_exposes_stage_a_without_guarded_writes(self):
        tools = adapter.list_tools()
        names = [tool["name"] for tool in tools]

        self.assertEqual(names, list(schemas.STAGE_A_TOOL_NAMES))
        for guarded_tool in schemas.STAGE_B_TOOL_NAMES:
            self.assertNotIn(guarded_tool, names)
        self.assertTrue(all(tool["stage"] == "A" for tool in tools))
        self.assertTrue(all(tool["write_mode"] == "no-write" for tool in tools))

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
            self.assertTrue((project_root / ".jikuo" / "runtime" / "last_card.md").is_file())

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


if __name__ == "__main__":
    unittest.main()
