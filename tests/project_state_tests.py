import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "project_state.py"
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
MISSING_PROJECT = FIXTURES / "missing_project"
INITIALIZED_PROJECT = FIXTURES / "initialized_project"
STALE_PROJECT = FIXTURES / "stale_project"
CONFLICT_PROJECT = FIXTURES / "conflict_project"
WRITE_READY_PROJECT = FIXTURES / "write_ready_project"


def load_project_state_module():
    spec = importlib.util.spec_from_file_location("project_state", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load project_state module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProjectStateBootstrapTests(unittest.TestCase):
    def test_missing_status_is_report_only_and_does_not_create_sidecar(self):
        module = load_project_state_module()
        report = module.build_bootstrap_report(
            project_root=MISSING_PROJECT,
            command="status",
            include_would_create=False,
        )

        self.assertEqual(report["schema"], module.BOOTSTRAP_REPORT_SCHEMA)
        self.assertTrue(report["report_only"])
        self.assertEqual(report["state_status"], "missing")
        self.assertFalse(report["write_allowed_by_command"])
        self.assertIsNone(report["would_create"])
        self.assertFalse((MISSING_PROJECT / ".jikuo").exists())

    def test_init_dry_run_reports_would_create_without_writing_files(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "init",
                "--dry-run",
                "--project-root",
                str(MISSING_PROJECT),
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
        self.assertEqual(report["state_status"], "missing")
        self.assertFalse(report["write_allowed_by_command"])
        self.assertEqual(
            report["would_create"]["schema"],
            "jikuo.project_local_state.v0",
        )
        self.assertFalse((MISSING_PROJECT / ".jikuo").exists())

    def test_valid_existing_project_state_is_initialized(self):
        module = load_project_state_module()
        report = module.build_bootstrap_report(project_root=INITIALIZED_PROJECT)

        self.assertEqual(report["state_status"], "initialized")
        self.assertEqual(report["warnings"], [])

    def test_stale_schema_is_reported_without_writing_files(self):
        module = load_project_state_module()
        report = module.build_bootstrap_report(project_root=STALE_PROJECT)

        self.assertEqual(report["state_status"], "stale_schema")
        self.assertIn("unsupported project state schema", report["warnings"][0])
        self.assertTrue((STALE_PROJECT / ".jikuo" / "project_state.yaml").exists())

    def test_conflicting_state_root_is_reported(self):
        module = load_project_state_module()
        report = module.build_bootstrap_report(project_root=CONFLICT_PROJECT)

        self.assertEqual(report["state_status"], "conflict")
        self.assertIn("not a directory", report["warnings"][0])

    def test_init_without_dry_run_is_rejected(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "init",
                "--project-root",
                str(MISSING_PROJECT),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("init requires --dry-run or --write", completed.stderr)

    def test_write_plan_requires_confirmation_and_approval(self):
        module = load_project_state_module()
        plan = module.build_write_plan(project_root=WRITE_READY_PROJECT)

        self.assertFalse(plan["can_write"])
        self.assertIn("missing technical confirmation flag", plan["warnings"])
        self.assertIn("missing approval phrase evidence", plan["warnings"])
        self.assertFalse((WRITE_READY_PROJECT / ".jikuo").exists())

    def test_write_plan_allows_ready_project_when_approved(self):
        module = load_project_state_module()
        plan = module.build_write_plan(
            project_root=WRITE_READY_PROJECT,
            approval_phrase="<exact user phrase as spoken>",
            confirmed=True,
        )

        self.assertTrue(plan["can_write"])
        self.assertEqual(plan["preflight_state_status"], "missing")
        self.assertEqual(plan["approval_record"]["decision_target"], module.APPROVAL_TARGET)
        self.assertFalse((WRITE_READY_PROJECT / ".jikuo").exists())

    def test_write_command_rejects_missing_confirmation_without_writing(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "init",
                "--write",
                "--project-root",
                str(WRITE_READY_PROJECT),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertFalse(result["write_performed"])
        self.assertIn("missing technical confirmation flag", result["warnings"])
        self.assertFalse((WRITE_READY_PROJECT / ".jikuo").exists())

    def test_write_command_rejects_initialized_state_without_overwrite(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "init",
                "--write",
                "--confirm-create-project-state",
                "--approval-phrase",
                "<exact user phrase as spoken>",
                "--project-root",
                str(INITIALIZED_PROJECT),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertFalse(result["write_performed"])
        self.assertEqual(result["preflight_state_status"], "initialized")
        self.assertEqual(result["overwritten_paths"], [])

    def test_text_output_keeps_desktop_summary_no_write_signal(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "status",
                "--project-root",
                str(MISSING_PROJECT),
                "--format",
                "text",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("JIKUO Project State Bootstrap (report-only)", completed.stdout)
        self.assertIn("State status: missing", completed.stdout)
        self.assertIn("Writes performed: no", completed.stdout)


if __name__ == "__main__":
    unittest.main()
