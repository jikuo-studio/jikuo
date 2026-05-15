import shutil
import tempfile
import unittest
from pathlib import Path

from jikuo.integrations.mcp import schemas, server


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
POLICY_ACTIVE_PROJECT = FIXTURES / "policy_store_active_project"


def copy_fixture(source: Path, tmp: str, name: str = "project") -> Path:
    target = Path(tmp) / name
    shutil.copytree(source, target)
    return target


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
    def test_create_server_registers_stage_a_tools_only(self):
        fake = server.create_server(fastmcp_cls=FakeFastMCP)

        self.assertEqual(fake.name, server.SERVER_NAME)
        self.assertEqual(list(fake.tools), list(schemas.STAGE_A_TOOL_NAMES))
        for guarded_tool in schemas.STAGE_B_TOOL_NAMES:
            self.assertNotIn(guarded_tool, fake.tools)

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
