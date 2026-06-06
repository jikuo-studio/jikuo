import json
import shutil
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from jikuo import policy_management_status, policy_templates, starter_policies  # noqa: E402


TEMP_ROOT = ROOT / "tmp" / "jikuo_policy_management_status_tests"


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
        / f"test_status_{uuid.uuid4().hex}"
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
                'template_id: "POLICYTEMPLATE-legacy-status-policy"',
                'namespace: "local"',
                "version: 1",
                'title: "Legacy status policy"',
                "required_bindings: []",
                "template_policy:",
                '  policy_id: "POLICY-legacy-status-policy"',
                "  version: 1",
                '  status: "active_report_only"',
                '  title: "Legacy status policy"',
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


def write_test_starter_manifest(
    root: Path,
    *,
    pack_id: str,
    template_ref: str,
) -> None:
    pack_root = root / "packs" / pack_id
    pack_root.mkdir(parents=True)
    (pack_root / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.starter_policy_pack_manifest.v0"',
                f'pack_id: "{pack_id}"',
                'title: "Legacy status pack"',
                "policy_templates:",
                f'  - template_ref: "{template_ref}"',
                '    policy_id: "POLICY-legacy-status-policy"',
                '    title: "Legacy status policy"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_project_state(root: Path) -> None:
    jikuo = root / ".jikuo"
    jikuo.mkdir(parents=True, exist_ok=True)
    (jikuo / "project_state.yaml").write_text(
        "\n".join(
            [
                'schema: "jikuo.project_local_state.v0"',
                'project_id: "policy_management_status_fixture"',
                f'project_root: "{root}"',
                f'jikuo_state_root: "{jikuo}"',
                "active_scenario_packages:",
                '  - "engineering_governance"',
                "accepted_contract_refs: []",
                "latest_task_session_refs: []",
                "latest_rule_proposal_refs: []",
                "latest_handoff_ref: null",
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_policy_store(root: Path, *, policy_id: str, title: str) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    (approved / f"{policy_id}.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                f'policy_id: "{policy_id}"',
                "version: 1",
                'status: "active_report_only"',
                f'title: "{title}"',
                'scenario_package: "engineering_governance"',
                "source_refs:",
                '  - type: "test_fixture"',
                f'    ref: "tests:{policy_id}"',
                "triggers:",
                '  - trigger_id: "TRG-task-start"',
                '    type: "task_lifecycle_event"',
                '    event: "task_start"',
                "conditions: []",
                "required_actions:",
                '  - action_id: "ACT-review"',
                '    type: "review"',
                "required_evidence:",
                '  - evidence_id: "EVD-review"',
                '    type: "review_evidence"',
                '    satisfies_action: "ACT-review"',
                "enforcement:",
                '  phase: "report_only"',
                '  level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "policy_management_status_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                f'  - policy_id: "{policy_id}"',
                "    version: 1",
                f'    path: ".jikuo/policies/approved/{policy_id}.yaml"',
                "proposal_refs: []",
                "deprecated_policy_refs: []",
                "superseded_policy_refs: []",
                'last_updated_at: "2026-05-31T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def add_policy_proposal(root: Path, *, proposal_id: str, policy_id: str) -> None:
    store = root / ".jikuo" / "policies"
    proposals = store / "proposals"
    proposals.mkdir(parents=True, exist_ok=True)
    proposal_ref = f".jikuo/policies/proposals/{proposal_id}.yaml"
    (proposals / f"{proposal_id}.yaml").write_text(
        "\n".join(
            [
                'schema: "jikuo.policy_write_plan.v0"',
                'schema_version: "jikuo.policy_write_plan.v0"',
                "report_only: true",
                f'plan_id: "{proposal_id}-PLAN"',
                'operation: "append_policy"',
                'status: "review"',
                f'proposal_ref: "{proposal_ref}"',
                f'policy_ref: "{policy_id}"',
                "write_set:",
                f'  - path: ".jikuo/policies/approved/{policy_id}.yaml"',
                '    operation: "create"',
                '    effect: "create approved policy file"',
                "proposed_trigger_profile:",
                '  trigger_mode: "scope_first"',
                '  policy_scopes: ["discussion"]',
                "  lifecycle_events: []",
                '  declared_trigger_event: "conversation_turn"',
                "  conditions: []",
                "proposed_policy:",
                f'  policy_id: "{policy_id}"',
                '  title: "Candidate discussion policy"',
                '  status: "active_report_only"',
                "  version: 1",
                "refusal_reasons: []",
                "warnings: []",
                'status_reason: "policy write plan is ready for desktop review"',
                "next_actions:",
                '  - "review this candidate before guarded activation"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    manifest_path = store / "manifest.yaml"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(
        manifest_text.replace(
            "proposal_refs: []",
            "\n".join(
                [
                    "proposal_refs:",
                    f'  - proposal_id: "{proposal_id}"',
                    f'    policy_id: "{policy_id}"',
                    f'    path: "{proposal_ref}"',
                    '    status: "candidate"',
                ]
            ),
        ),
        encoding="utf-8",
    )


class PolicyManagementStatusTests(unittest.TestCase):
    def test_status_read_model_links_active_policy_to_package_template_and_starter_pack(self):
        with temp_project_dir() as project_root:
            write_policy_store(
                project_root,
                policy_id="POLICY-task-scope-control-before-packaging",
                title="Task scope control before packaging",
            )

            report = policy_management_status.build_policy_management_status(
                project_root=project_root,
                starter_pack_id="engineering_governance",
            )

        self.assertEqual(report["schema"], "jikuo.policy_management_status.v0")
        self.assertFalse(report["writes_performed"])
        self.assertEqual(report["policy_store"]["active_policy_count"], 1)
        self.assertGreaterEqual(report["package_templates"]["template_count"], 1)
        self.assertEqual(report["starter_packs"]["pack_count"], 1)
        self.assertEqual(
            report["summary_counts"]["active_policy_with_package_template_count"],
            1,
        )
        distribution = report["active_policy_distribution"][0]
        self.assertEqual(distribution["distribution_state"], "starter_pack_available")
        self.assertTrue(distribution["package_template_refs"])
        self.assertEqual(
            distribution["starter_pack_refs"][0]["pack_id"],
            "engineering_governance",
        )
        operations = {
            item["operation"]: item
            for item in report["available_operations"]
        }
        self.assertEqual(
            operations["starter_policy_pack_init_plan"]["surface"],
            "/api/policy-management/starter-init/plan",
        )
        self.assertEqual(
            operations["starter_policy_pack_init"]["write_mode"],
            "guarded-write",
        )
        self.assertEqual(
            operations["policy_final_response_gate_update"]["surface"],
            "/api/policy-management/evolution/plan -> /api/policy-management/evolution/apply",
        )
        self.assertEqual(
            operations["policy_final_response_gate_update"]["write_mode"],
            "no-write-plan+guarded-write",
        )
        self.assertIn(
            "starter policy pack activation installs report-only baseline policies; it does not prove semantic intent or enable blocking gates by itself",
            report["read_model_limitations"],
        )
        detail = report["policy_store"]["active_policy_details"][0]
        self.assertFalse(detail["final_response_gate"]["enabled"])
        self.assertEqual(detail["final_response_gate"]["source"], "default_false")
        self.assertTrue(detail["policy_sha256"])

    def test_status_read_model_projects_legacy_template_compatibility(self):
        with temp_project_dir() as project_root, temp_package_template_dir() as template_dir:
            template_path = template_dir / "POLICYTEMPLATE-legacy-status-policy.yaml"
            write_legacy_package_template(template_path)
            template_ref = package_template_ref(template_path)
            write_test_starter_manifest(
                project_root,
                pack_id="legacy_status_pack",
                template_ref=template_ref,
            )
            old_pack_root = starter_policies.STARTER_PACKS_ROOT
            try:
                starter_policies.STARTER_PACKS_ROOT = project_root / "packs"
                report = policy_management_status.build_policy_management_status(
                    project_root=project_root,
                    template_dir=template_dir,
                    starter_pack_id="legacy_status_pack",
                )
            finally:
                starter_policies.STARTER_PACKS_ROOT = old_pack_root

        self.assertEqual(report["package_templates"]["template_count"], 1)
        detail = report["package_templates"]["templates"][0]
        self.assertEqual(detail["template_ref"], template_ref)
        self.assertEqual(
            detail["schema_version"],
            "jikuo.policy_template.legacy_v0",
        )
        self.assertEqual(detail["compatibility_status"], "legacy_compatible")
        self.assertTrue(detail["migration_available"])
        self.assertEqual(detail["migration_kind"], "deterministic_format_only")
        self.assertEqual(
            detail["target_active_policy_schema"],
            policy_templates.policy_store.POLICY_SCHEMA,
        )
        self.assertFalse(detail["final_response_gate"]["enabled"])
        self.assertEqual(detail["final_response_gate"]["source"], "default_false")
        self.assertEqual(detail["trigger_profile"]["trigger_mode"], "legacy_event_only")
        self.assertEqual(
            report["summary_counts"]["legacy_compatible_template_count"],
            1,
        )
        self.assertEqual(
            report["summary_counts"]["migration_available_template_count"],
            1,
        )
        starter_entry = report["starter_packs"]["packs"][0]["policy_templates"][0]
        self.assertEqual(starter_entry["template_ref"], template_ref)
        self.assertEqual(starter_entry["compatibility_status"], "legacy_compatible")
        self.assertTrue(starter_entry["migration_available"])

    def test_status_read_model_projects_declared_final_response_gate(self):
        with temp_project_dir() as project_root:
            policy_id = "POLICY-final-response-gate-fixture"
            write_policy_store(
                project_root,
                policy_id=policy_id,
                title="Final response gate fixture",
            )
            policy_path = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / f"{policy_id}.yaml"
            )
            policy_path.write_text(
                policy_path.read_text(encoding="utf-8")
                + "final_response_gate: true\n",
                encoding="utf-8",
            )

            report = policy_management_status.build_policy_management_status(
                project_root=project_root,
                starter_pack_id="engineering_governance",
            )

        detail = report["policy_store"]["active_policy_details"][0]
        self.assertTrue(detail["final_response_gate"]["enabled"])
        self.assertEqual(detail["final_response_gate"]["source"], "declared_boolean")
        self.assertEqual(
            detail["final_response_gate"]["visibility"],
            "final_response_required",
        )

    def test_policy_management_status_cli_returns_json_and_markdown(self):
        with temp_project_dir() as project_root:
            write_policy_store(
                project_root,
                policy_id="POLICY-task-scope-control-before-packaging",
                title="Task scope control before packaging",
            )
            json_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo.policy_management_status",
                    "status",
                    "--project-root",
                    str(project_root),
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
                    "jikuo.policy_management_status",
                    "status",
                    "--project-root",
                    str(project_root),
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
        self.assertEqual(report["schema"], "jikuo.policy_management_status.v0")
        self.assertEqual(markdown_completed.returncode, 0, markdown_completed.stderr)
        self.assertIn("# JIKUO Policy Management Status", markdown_completed.stdout)
        self.assertIn("starter_pack_available", markdown_completed.stdout)

    def test_status_read_model_loads_policy_proposal_details(self):
        with temp_project_dir() as project_root:
            write_project_state(project_root)
            write_policy_store(
                project_root,
                policy_id="POLICY-active-fixture",
                title="Active fixture policy",
            )
            add_policy_proposal(
                project_root,
                proposal_id="POLICYPROPOSAL-candidate-fixture",
                policy_id="POLICY-candidate-fixture",
            )

            report = policy_management_status.build_policy_management_status(
                project_root=project_root,
            )

        details = report["policy_store"]["proposal_details"]
        self.assertEqual(len(details), 1)
        detail = details[0]
        self.assertEqual(detail["proposal_id"], "POLICYPROPOSAL-candidate-fixture")
        self.assertEqual(detail["policy_id"], "POLICY-candidate-fixture")
        self.assertEqual(detail["title"], "Candidate discussion policy")
        self.assertEqual(detail["operation"], "append_policy")
        self.assertEqual(detail["write_set_count"], 1)
        self.assertEqual(detail["trigger_profile"]["trigger_mode"], "scope_first")
        self.assertEqual(detail["trigger_profile"]["policy_scopes"], ["discussion"])
        activatable = report["policy_store"]["activatable_policy_proposals"]
        self.assertEqual(len(activatable), 1)
        self.assertEqual(
            report["summary_counts"]["activatable_policy_proposal_count"],
            1,
        )
        self.assertEqual(activatable[0]["activation_status"], "ready_to_activate")
        self.assertEqual(activatable[0]["policy_id"], "POLICY-candidate-fixture")
        self.assertEqual(
            activatable[0]["trigger_profile"]["policy_scopes"],
            ["discussion"],
        )

    def test_status_read_model_excludes_already_active_proposal_from_activatable_list(self):
        with temp_project_dir() as project_root:
            write_project_state(project_root)
            write_policy_store(
                project_root,
                policy_id="POLICY-active-fixture",
                title="Active fixture policy",
            )
            add_policy_proposal(
                project_root,
                proposal_id="POLICYPROPOSAL-active-history",
                policy_id="POLICY-active-fixture",
            )

            report = policy_management_status.build_policy_management_status(
                project_root=project_root,
            )

        self.assertEqual(len(report["policy_store"]["proposal_details"]), 1)
        self.assertEqual(report["policy_store"]["activatable_policy_proposals"], [])
        self.assertEqual(
            report["summary_counts"]["activatable_policy_proposal_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
