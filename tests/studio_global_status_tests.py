import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo.studio import global_status  # noqa: E402


class StudioGlobalStatusTests(unittest.TestCase):
    def test_global_status_is_no_write_ui_read_model_for_repo(self):
        report = global_status.build_global_status(project_root=ROOT)

        self.assertEqual(report["schema"], global_status.GLOBAL_STATUS_SCHEMA)
        self.assertEqual(report["schema_version"], global_status.GLOBAL_STATUS_SCHEMA)
        self.assertIn(report["status"], {"available", "degraded"})
        self.assertFalse(report["writes_performed"])
        self.assertFalse(report["write_allowed_by_command"])
        self.assertIn("runtime", report["summaries"])
        self.assertIn("activation", report["summaries"])
        self.assertIn("configuration", report["summaries"])
        self.assertIn("policy_management", report["summaries"])
        self.assertIn("registry", report["summaries"])
        self.assertIn("integrations", report["summaries"])
        self.assertIn("project_context", report["summaries"])
        self.assertEqual(report["panel_registry"]["schema"], "jikuo.studio.panel_registry.v0")
        self.assertEqual(report["action_registry"]["schema"], "jikuo.studio.action_registry.v0")
        self.assertGreaterEqual(len(report["panels"]), 6)

        policy_counts = report["summaries"]["policy_management"]["summary_counts"]
        self.assertGreaterEqual(policy_counts["active_policy_count"], 1)
        self.assertGreaterEqual(policy_counts["package_template_count"], 1)
        self.assertGreaterEqual(policy_counts["starter_pack_count"], 1)

        action_ids = {item["action_id"] for item in report["available_actions"]}
        self.assertIn("studio.configuration.review", action_ids)
        self.assertIn("studio.activation_settings.plan_update", action_ids)
        self.assertIn("studio.policy_management.status", action_ids)
        self.assertIn("studio.runtime.open_latest_card", action_ids)

    def test_missing_project_context_is_unavailable_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = global_status.build_global_status(project_root=project_root)

            self.assertEqual(report["schema"], global_status.GLOBAL_STATUS_SCHEMA)
            self.assertEqual(report["status"], "unavailable")
            self.assertFalse(report["writes_performed"])
            self.assertFalse((project_root / ".jikuo").exists())
            diagnostics = {item["code"] for item in report["diagnostics"]}
            self.assertIn("project_context_missing", diagnostics)

    def test_global_status_reports_activation_decisions_and_diagnostics(self):
        report = global_status.build_global_status(project_root=ROOT)

        activation = report["summaries"]["activation"]
        self.assertIn("required_user_decision_count", activation)
        if activation["required_user_decision_count"]:
            self.assertTrue(report["pending_user_decisions"])
            diagnostic_codes = {item["code"] for item in report["diagnostics"]}
            self.assertIn("activation_settings_require_review", diagnostic_codes)

    def test_global_status_does_not_include_raw_prompt_or_transcript_content(self):
        report = global_status.build_global_status(project_root=ROOT)
        serialized = json.dumps(report, ensure_ascii=False)

        self.assertNotIn("SECRET_PROMPT_VALUE", serialized)
        self.assertNotIn("raw transcript text", serialized)
        self.assertFalse(report["privacy"]["raw_prompt_stored"])
        self.assertFalse(report["privacy"]["transcript_stored"])

    def test_global_status_cli_returns_json_and_markdown(self):
        json_completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "jikuo",
                "studio",
                "status",
                "--project-root",
                str(ROOT),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        markdown_completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "jikuo",
                "studio",
                "status",
                "--project-root",
                str(ROOT),
                "--format",
                "markdown",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(json_completed.returncode, 0, json_completed.stderr)
        report = json.loads(json_completed.stdout)
        self.assertEqual(report["schema"], global_status.GLOBAL_STATUS_SCHEMA)
        self.assertEqual(markdown_completed.returncode, 0, markdown_completed.stderr)
        self.assertIn("# JIKUO Studio Global Status", markdown_completed.stdout)
        self.assertIn("## Panels", markdown_completed.stdout)
        self.assertIn("Available Actions", markdown_completed.stdout)


if __name__ == "__main__":
    unittest.main()
