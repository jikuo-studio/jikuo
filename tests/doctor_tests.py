import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo import doctor  # noqa: E402
from jikuo.studio import global_status  # noqa: E402


class DoctorTests(unittest.TestCase):
    def test_doctor_report_uses_studio_global_status_authority(self):
        report = doctor.build_doctor_report(project_root=ROOT)

        self.assertEqual(report["schema"], doctor.DOCTOR_REPORT_SCHEMA)
        self.assertEqual(report["schema_version"], doctor.DOCTOR_REPORT_SCHEMA)
        self.assertEqual(
            report["source_read_model"]["schema"],
            global_status.GLOBAL_STATUS_SCHEMA,
        )
        self.assertFalse(report["writes_performed"])
        self.assertFalse(report["write_allowed_by_command"])
        check_ids = {item["check_id"] for item in report["checks"]}
        self.assertEqual(
            check_ids,
            {
                "install_and_cli",
                "first_run_readiness",
                "activation_settings",
                "policy_management",
                "document_rules",
                "studio",
                "mcp_server",
                "runtime_visibility",
            },
        )
        self.assertIn(report["status"], {"ok", "review", "action_required"})
        markdown = doctor.format_markdown(report)
        self.assertIn("# JIKUO Doctor", markdown)
        self.assertIn("Source read model: `jikuo.studio.global_status.v0`", markdown)
        self.assertIn("## Non-Effects", markdown)

    def test_doctor_reports_blank_project_first_run_blockers_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = doctor.build_doctor_report(project_root=project_root)

            first_run = next(
                item
                for item in report["checks"]
                if item["check_id"] == "first_run_readiness"
            )
            self.assertEqual(first_run["status"], "action_required")
            self.assertIn("blockers=3", first_run["summary"])
            self.assertFalse((project_root / ".jikuo").exists())

    def test_top_level_doctor_command_outputs_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo",
                    "doctor",
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
            self.assertEqual(report["schema"], doctor.DOCTOR_REPORT_SCHEMA)
            self.assertFalse(report["writes_performed"])
            first_run = next(
                item
                for item in report["checks"]
                if item["check_id"] == "first_run_readiness"
            )
            self.assertEqual(first_run["status"], "action_required")


if __name__ == "__main__":
    unittest.main()
