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
sys.path.insert(0, str(ROOT / "src"))
from jikuo import starter_policies  # noqa: E402


@contextmanager
def temp_project_dir():
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEMP_ROOT / f"case_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def create_policy_write_ready_project(root: Path) -> None:
    state_root = root / ".jikuo"
    state_root.mkdir()
    (state_root / "project_state.yaml").write_text(
        "\n".join(
            [
                'schema: "jikuo.project_local_state.v0"',
                'project_id: "starter_policy_preserve_project"',
                f'project_root: "{root}"',
                f'jikuo_state_root: "{state_root}"',
                "active_scenario_packages:",
                '  - "engineering_governance"',
                "accepted_contract_refs: []",
                'registry_ref: "docs/governance/rule_registry.yaml"',
                "latest_task_session_refs: []",
                "latest_rule_proposal_refs: []",
                "latest_handoff_ref: null",
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "starter_policies_test"',
                "",
            ]
        ),
        encoding="utf-8",
    )


class StarterPolicyPackTests(unittest.TestCase):
    def test_starter_template_refs_must_come_from_official_package_templates(self):
        path, warning = starter_policies.resolve_official_starter_template_path(
            "pkg://jikuo/.jikuo/policies/approved/POLICY-jikuo-self-bootstrap-workflow.yaml"
        )

        self.assertIsNone(path)
        self.assertEqual(
            warning,
            "starter_template_ref_must_be_pkg_policy_template:"
            "pkg://jikuo/.jikuo/policies/approved/POLICY-jikuo-self-bootstrap-workflow.yaml",
        )

    def test_load_pack_policies_refuses_manifest_refs_to_project_local_policy_store(self):
        with temp_project_dir() as root:
            pack_root = root / "packs" / "bad_pack"
            pack_root.mkdir(parents=True)
            (pack_root / "manifest.yaml").write_text(
                "\n".join(
                    [
                        'schema_version: "jikuo.starter_policy_pack_manifest.v0"',
                        'pack_id: "bad_pack"',
                        'title: "Bad pack"',
                        "policy_templates:",
                        "  - template_ref: "
                        '"pkg://jikuo/.jikuo/policies/approved/POLICY-jikuo-self-bootstrap-workflow.yaml"',
                        '    policy_id: "POLICY-jikuo-self-bootstrap-workflow"',
                        '    title: "Self-bootstrap workflow"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            old_pack_root = starter_policies.STARTER_PACKS_ROOT
            try:
                starter_policies.STARTER_PACKS_ROOT = root / "packs"
                policies, warnings = starter_policies.load_pack_policies("bad_pack")
            finally:
                starter_policies.STARTER_PACKS_ROOT = old_pack_root

        self.assertEqual(policies, [])
        self.assertIn(
            "starter_template_ref_must_be_pkg_policy_template:"
            "pkg://jikuo/.jikuo/policies/approved/POLICY-jikuo-self-bootstrap-workflow.yaml",
            warnings,
        )

    def test_plan_refuses_pack_id_path_escape(self):
        with temp_project_dir() as root:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "plan-init",
                    "--project-root",
                    str(root),
                    "--pack-id",
                    "..",
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
            self.assertFalse(report["writes_performed"])
            self.assertIn("starter_pack_source_boundary_violation", report["refusal_reasons"])
            self.assertFalse((root / ".jikuo").exists())

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
            for item in report["starter_policies"]:
                provenance = item["provenance"]
                self.assertEqual(provenance["schema"], "jikuo.policy_provenance.v0")
                self.assertEqual(provenance["source"], "verified_jikuo_official")
                self.assertEqual(provenance["source_ref"], item["template_ref"])
                self.assertEqual(provenance["starter_pack_ref"], "engineering_governance")
                self.assertFalse(provenance["review_wall_required"])
                self.assertEqual(
                    provenance["reviewed_by"]["principal_type"],
                    "package_maintainer",
                )
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
            policy_files = list(approved.glob("POLICY-*.yaml"))
            self.assertEqual(len(policy_files), 4)
            for policy_file in policy_files:
                policy_text = policy_file.read_text(encoding="utf-8")
                self.assertIn("provenance:", policy_text)
                self.assertIn('schema: "jikuo.policy_provenance.v0"', policy_text)
                self.assertIn('source: "verified_jikuo_official"', policy_text)
                self.assertIn('starter_pack_ref: "engineering_governance"', policy_text)
                self.assertIn("review_wall_required: false", policy_text)
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

    def test_guarded_init_appends_without_overwriting_existing_user_policy(self):
        with temp_project_dir() as root:
            create_policy_write_ready_project(root)
            first = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(POLICY_STORE_TOOL),
                    "write-policy",
                    "--project-root",
                    str(root),
                    "--policy-id",
                    "POLICY-user-local-working-rule",
                    "--title",
                    "User local working rule",
                    "--source-ref",
                    "<exact user phrase as spoken>",
                    "--task-type",
                    "user_project_work",
                    "--confirm-write-policy",
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
            user_policy_path = (
                root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-user-local-working-rule.yaml"
            )
            before_user_policy_text = user_policy_path.read_text(encoding="utf-8")

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
            self.assertEqual(user_policy_path.read_text(encoding="utf-8"), before_user_policy_text)
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
            active_policy_ids = [
                ref["policy_id"] for ref in status_report["active_policy_refs"]
            ]
            self.assertIn("POLICY-user-local-working-rule", active_policy_ids)
            self.assertEqual(len(active_policy_ids), 5)

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
            self.assertNotIn("NarrativeSystem", policy_text)
            self.assertNotIn("D:\\", policy_text)
            self.assertNotIn("origin_policy", policy_text)
            self.assertNotIn("user_natural_language", policy_text)
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
