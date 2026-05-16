import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jikuo import configuration_review


ROOT = Path(__file__).resolve().parents[1]


class ConfigurationReviewTests(unittest.TestCase):
    def test_review_aggregates_first_use_state_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = configuration_review.build_configuration_review(
                project_root=project_root
            )

            self.assertEqual(
                report["schema"], configuration_review.CONFIGURATION_REVIEW_SCHEMA
            )
            self.assertEqual(report["status"], "review")
            self.assertFalse(report["write_allowed_by_command"])
            self.assertFalse(report["writes_performed"])
            item_keys = {item["key"] for item in report["items"]}
            self.assertIn("activation_settings", item_keys)
            self.assertIn("instruction_files", item_keys)
            self.assertIn("runtime_visibility", item_keys)
            self.assertIn("mcp_server", item_keys)
            self.assertIn("project_context", item_keys)
            self.assertIn("starter_policies", item_keys)
            self.assertIn("guarded_writes", item_keys)
            self.assertFalse((project_root / ".jikuo" / "activation_settings.yaml").exists())

    def test_top_level_configure_command_outputs_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo",
                    "configure",
                    "status",
                    "--project-root",
                    str(project_root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(
                report["schema"], configuration_review.CONFIGURATION_REVIEW_SCHEMA
            )
            self.assertEqual(report["status"], "review")

    def test_agent_flow_can_render_configuration_review_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo.agent_flow",
                    "propose",
                    "--event",
                    "configuration_review",
                    "--project-root",
                    str(project_root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            proposal = json.loads(completed.stdout)
            card_kinds = {card["card_kind"] for card in proposal["cards"]}
            self.assertIn("configuration_review", card_kinds)
            self.assertIn("CAP-CONFIGURATION-REVIEW-01", {
                trace["atom_id"] for trace in proposal["atom_trace"]
            })

    def test_conversation_turn_routes_setup_requests_to_configuration_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo.agent_flow",
                    "propose",
                    "--event",
                    "conversation_turn",
                    "--project-root",
                    str(project_root),
                    "--user-phrase",
                    "please review setup settings before implementation",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            proposal = json.loads(completed.stdout)
            router = proposal["conversation_router"]
            kinds = {item["kind"] for item in router["classified_obligations"]}
            self.assertIn("configuration_review", kinds)
            self.assertIn(
                "python -B -m jikuo.agent_flow propose --event configuration_review",
                router["required_followup_tools"],
            )


if __name__ == "__main__":
    unittest.main()
