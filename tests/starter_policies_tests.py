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
PACKAGE_TEMPLATE_REF = (
    "pkg://jikuo/policy_templates/engineering_governance/"
    "POLICYTEMPLATE-local-policy-task-scope-control-before-packaging.yaml"
)
sys.path.insert(0, str(ROOT / "src"))
from jikuo import policy_templates, starter_policies  # noqa: E402


@contextmanager
def temp_project_dir():
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEMP_ROOT / f"case_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@contextmanager
def temp_package_template_dir():
    path = (
        ROOT
        / "src"
        / "jikuo"
        / "policy_templates"
        / f"test_legacy_{uuid.uuid4().hex}"
    )
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def package_template_ref(path: Path) -> str:
    relative = path.resolve().relative_to((ROOT / "src" / "jikuo").resolve())
    return f"pkg://jikuo/{relative.as_posix()}"


def write_legacy_package_template(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_template.legacy_v0"',
                'template_id: "POLICYTEMPLATE-legacy-starter-policy"',
                'namespace: "local"',
                "version: 1",
                'title: "Legacy starter policy"',
                "required_bindings: []",
                "template_policy:",
                '  policy_id: "POLICY-legacy-starter-policy"',
                "  version: 1",
                '  status: "active_report_only"',
                '  title: "Legacy starter policy"',
                '  scenario_package: "engineering_governance"',
                "  source_refs: []",
                "  triggers:",
                '    - trigger_id: "TRG-task-start"',
                '      type: "task_lifecycle_event"',
                '      event: "task_start"',
                "  conditions: []",
                "  required_actions:",
                '    - action_id: "ACT-review"',
                '      type: "review"',
                "  required_evidence:",
                '    - evidence_id: "EVD-review"',
                '      type: "review_evidence"',
                '      satisfies_action: "ACT-review"',
                "  enforcement:",
                '    phase: "report_only"',
                '    level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )


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


def write_test_starter_manifest(
    root: Path,
    *,
    pack_id: str = "test_pack",
    template_ref: str | None = None,
    policy_id: str = "POLICY-legacy-starter-policy",
    title: str = "Legacy starter policy",
) -> Path:
    pack_root = root / "packs" / pack_id
    pack_root.mkdir(parents=True)
    manifest_path = pack_root / "manifest.yaml"
    policy_template_lines = ["policy_templates: []"]
    if template_ref:
        policy_template_lines = [
            "policy_templates:",
            f'  - template_ref: "{template_ref}"',
            f'    policy_id: "{policy_id}"',
            f'    title: "{title}"',
        ]
    manifest_path.write_text(
        "\n".join(
            [
                'schema_version: "jikuo.starter_policy_pack_manifest.v0"',
                f'pack_id: "{pack_id}"',
                'title: "Test starter pack"',
                *policy_template_lines,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return manifest_path


class StarterPolicyPackTests(unittest.TestCase):
    def test_starter_manifest_publication_plan_is_no_write(self):
        with temp_project_dir() as root:
            manifest_path = write_test_starter_manifest(root)
            old_pack_root = starter_policies.STARTER_PACKS_ROOT
            try:
                starter_policies.STARTER_PACKS_ROOT = root / "packs"
                report = starter_policies.build_starter_manifest_publication_plan(
                    template_ref=PACKAGE_TEMPLATE_REF,
                    pack_id="test_pack",
                )
            finally:
                starter_policies.STARTER_PACKS_ROOT = old_pack_root

            self.assertEqual(
                report["schema"],
                "jikuo.starter_pack_manifest_publication_plan.v0",
            )
            self.assertEqual(report["status"], "review")
            self.assertFalse(report["writes_performed"])
            self.assertFalse(report["write_allowed_by_command"])
            self.assertEqual(report["manifest_path"], str(manifest_path))
            self.assertEqual(report["template_ref"], PACKAGE_TEMPLATE_REF)
            self.assertEqual(
                report["policy_id"],
                "POLICY-task-scope-control-before-packaging",
            )
            self.assertEqual(len(report["write_set"]), 1)
            self.assertIn(
                "does not activate policies in user projects",
                report["non_effects"],
            )
            self.assertNotIn(PACKAGE_TEMPLATE_REF, manifest_path.read_text(encoding="utf-8"))

    def test_starter_manifest_publication_refuses_project_local_template_refs(self):
        with temp_project_dir() as root:
            write_test_starter_manifest(root)
            old_pack_root = starter_policies.STARTER_PACKS_ROOT
            try:
                starter_policies.STARTER_PACKS_ROOT = root / "packs"
                report = starter_policies.build_starter_manifest_publication_plan(
                    template_ref=(
                        "pkg://jikuo/.jikuo/policies/approved/"
                        "POLICY-jikuo-self-bootstrap-workflow.yaml"
                    ),
                    pack_id="test_pack",
                )
            finally:
                starter_policies.STARTER_PACKS_ROOT = old_pack_root

            self.assertEqual(report["status"], "refused")
            self.assertIn(
                "starter_pack_template_ref_boundary_violation",
                report["refusal_reasons"],
            )
            self.assertIn(
                "does not copy .jikuo/policies/approved files into starter packs",
                report["non_effects"],
            )

    def test_starter_manifest_publication_requires_confirmation_and_approval(self):
        with temp_project_dir() as root:
            manifest_path = write_test_starter_manifest(root)
            old_pack_root = starter_policies.STARTER_PACKS_ROOT
            try:
                starter_policies.STARTER_PACKS_ROOT = root / "packs"
                report, exit_code = starter_policies.publish_template_to_starter_manifest(
                    template_ref=PACKAGE_TEMPLATE_REF,
                    pack_id="test_pack",
                )
            finally:
                starter_policies.STARTER_PACKS_ROOT = old_pack_root

            self.assertEqual(exit_code, 2)
            self.assertFalse(report["write_performed"])
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            self.assertNotIn(PACKAGE_TEMPLATE_REF, manifest_path.read_text(encoding="utf-8"))

    def test_guarded_starter_manifest_publication_appends_package_template_ref(self):
        with temp_project_dir() as root:
            manifest_path = write_test_starter_manifest(root)
            old_pack_root = starter_policies.STARTER_PACKS_ROOT
            try:
                starter_policies.STARTER_PACKS_ROOT = root / "packs"
                report, exit_code = starter_policies.publish_template_to_starter_manifest(
                    template_ref=PACKAGE_TEMPLATE_REF,
                    pack_id="test_pack",
                    confirmed=True,
                    approval_phrase="<exact user phrase as spoken>",
                )
                duplicate = starter_policies.build_starter_manifest_publication_plan(
                    template_ref=PACKAGE_TEMPLATE_REF,
                    pack_id="test_pack",
                )
            finally:
                starter_policies.STARTER_PACKS_ROOT = old_pack_root

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                report["schema"],
                "jikuo.starter_pack_manifest_publication_result.v0",
            )
            self.assertTrue(report["write_performed"])
            self.assertEqual(report["written_paths"], [str(manifest_path)])
            self.assertTrue(report["post_write_verification"]["template_ref_present"])
            self.assertTrue(report["post_write_verification"]["starter_pack_policy_loadable"])
            manifest_text = manifest_path.read_text(encoding="utf-8")
            self.assertIn(PACKAGE_TEMPLATE_REF, manifest_text)
            self.assertIn(
                'policy_id: "POLICY-task-scope-control-before-packaging"',
                manifest_text,
            )
            self.assertFalse((root / ".jikuo").exists())
            self.assertEqual(duplicate["status"], "refused")
            self.assertIn(
                f"starter_pack_template_ref_already_present:{PACKAGE_TEMPLATE_REF}",
                duplicate["refusal_reasons"],
            )

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

    def test_starter_init_normalizes_legacy_template_without_rewriting_template(self):
        with temp_project_dir() as root, temp_package_template_dir() as template_dir:
            template_path = template_dir / "POLICYTEMPLATE-legacy-starter-policy.yaml"
            write_legacy_package_template(template_path)
            original_template_text = template_path.read_text(encoding="utf-8")
            template_ref = package_template_ref(template_path)
            write_test_starter_manifest(
                root,
                pack_id="legacy_pack",
                template_ref=template_ref,
            )
            old_pack_root = starter_policies.STARTER_PACKS_ROOT
            try:
                starter_policies.STARTER_PACKS_ROOT = root / "packs"
                plan = starter_policies.build_starter_init_plan(
                    project_root=root,
                    pack_id="legacy_pack",
                )
                report, exit_code = starter_policies.initialize_starter_pack(
                    project_root=root,
                    pack_id="legacy_pack",
                    confirmed=True,
                    approval_phrase="<exact user phrase as spoken>",
                )
            finally:
                starter_policies.STARTER_PACKS_ROOT = old_pack_root

            self.assertEqual(plan["status"], "review")
            self.assertEqual(len(plan["starter_policies"]), 1)
            plan_item = plan["starter_policies"][0]
            self.assertEqual(plan_item["compatibility_status"], "legacy_compatible")
            self.assertTrue(plan_item["migration_available"])
            compatibility = plan_item["template_compatibility"]
            self.assertEqual(compatibility["migration_kind"], "deterministic_format_only")
            self.assertEqual(exit_code, 0)
            self.assertTrue(report["write_performed"])
            approved_path = (
                root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-legacy-starter-policy.yaml"
            )
            approved_policy = policy_templates.read_yaml_subset(approved_path)
            self.assertEqual(
                approved_policy["schema_version"],
                policy_templates.policy_store.POLICY_SCHEMA,
            )
            self.assertFalse(approved_policy["final_response_gate"])
            self.assertEqual(approved_policy["applies_to_work_profile"], [])
            self.assertEqual(approved_policy["template_ref"], template_ref)
            self.assertEqual(
                template_path.read_text(encoding="utf-8"),
                original_template_text,
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
