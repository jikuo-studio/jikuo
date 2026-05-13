import json
import shutil
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "starter_policies.py"
POLICY_STORE_TOOL = ROOT / "src" / "jikuo" / "policy_store.py"
TEMP_ROOT = ROOT / "tmp" / "jikuo_starter_policies_tests"


@contextmanager
def temp_project_dir():
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEMP_ROOT / f"case_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


class StarterPolicyPackTests(unittest.TestCase):
    def test_plan_init_is_no_write_for_fresh_project(self):
        with temp_project_dir() as root:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "plan-init",
                    "--project-root",
                    str(root),
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
            self.assertEqual(report["schema"], "jikuo.starter_policy_pack_init_plan.v0")
            self.assertFalse(report["writes_performed"])
            self.assertTrue(report["would_create_registry"])
            self.assertTrue(report["would_create_project_state"])
            self.assertEqual(len(report["starter_policies"]), 4)
            self.assertFalse((root / ".jikuo").exists())

    def test_init_requires_confirmation_and_approval(self):
        with temp_project_dir() as root:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "init",
                    "--project-root",
                    str(root),
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
            report = json.loads(completed.stdout)
            self.assertFalse(report["write_performed"])
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            self.assertFalse((root / ".jikuo").exists())

    def test_guarded_init_creates_project_state_and_starter_policy_store(self):
        with temp_project_dir() as root:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "init",
                    "--project-root",
                    str(root),
                    "--confirm-starter-init",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
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
            self.assertTrue(report["write_performed"])
            self.assertTrue((root / "docs" / "governance" / "rule_registry.yaml").is_file())
            self.assertTrue((root / ".jikuo" / "project_state.yaml").is_file())
            approved = root / ".jikuo" / "policies" / "approved"
            self.assertEqual(len(list(approved.glob("POLICY-*.yaml"))), 4)
            self.assertTrue(report["post_write_verification"]["starter_policies_active"])

            status = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(POLICY_STORE_TOOL),
                    "status",
                    "--project-root",
                    str(root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            status_report = json.loads(status.stdout)
            self.assertEqual(status_report["policy_store_status"], "active")
            self.assertEqual(len(status_report["active_policy_refs"]), 4)

    def test_guarded_init_records_package_template_refs_not_local_template_paths(self):
        with temp_project_dir() as root:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "init",
                    "--project-root",
                    str(root),
                    "--confirm-starter-init",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
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
            policy_text = (
                root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-desktop-workflow-acceptance-card-and-summary.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn("pkg://jikuo/policy_templates/engineering_governance/", policy_text)
            self.assertNotIn("src\\\\jikuo\\\\policy_templates", policy_text)
            self.assertNotIn("src/jikuo/policy_templates", policy_text)

    def test_init_refuses_existing_starter_policy_collision(self):
        with temp_project_dir() as root:
            first = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "init",
                    "--project-root",
                    str(root),
                    "--confirm-starter-init",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            second = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "init",
                    "--project-root",
                    str(root),
                    "--confirm-starter-init",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(second.returncode, 2, second.stderr)
            report = json.loads(second.stdout)
            self.assertTrue(
                any(
                    reason.startswith("starter_policy_already_active_or_present:")
                    for reason in report["refusal_reasons"]
                )
            )

    def test_plan_refuses_existing_starter_proposal_artifact_collision(self):
        with temp_project_dir() as root:
            proposal = (
                root
                / ".jikuo"
                / "policies"
                / "proposals"
                / "POLICYPROPOSAL-ccd9de7211.yaml"
            )
            proposal.parent.mkdir(parents=True)
            proposal.write_text("status: partial\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "plan-init",
                    "--project-root",
                    str(root),
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
            report = json.loads(completed.stdout)
            self.assertIn(
                "starter_policy_artifact_already_present:"
                ".jikuo/policies/proposals/POLICYPROPOSAL-ccd9de7211.yaml",
                report["refusal_reasons"],
            )


if __name__ == "__main__":
    unittest.main()
