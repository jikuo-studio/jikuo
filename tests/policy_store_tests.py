import json
import shutil
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "policy_store.py"
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
MISSING_PROJECT = FIXTURES / "task_session_ready_project"
INITIALIZED_PROJECT = FIXTURES / "policy_store_initialized_project"
ACTIVE_PROJECT = FIXTURES / "policy_store_active_project"
EVIDENCE_PROJECT = FIXTURES / "policy_store_evidence_project"
CONDITION_PROJECT = FIXTURES / "policy_store_condition_project"
REAL_CHAIN_TESTING_PROJECT = FIXTURES / "policy_store_real_chain_testing_project"
STALE_PROJECT = FIXTURES / "policy_store_stale_project"
CONFLICT_PROJECT = FIXTURES / "policy_store_conflict_project"
TEMP_ROOT = ROOT / "tmp" / "jikuo_policy_store_tests"


@contextmanager
def temp_project_dir():
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEMP_ROOT / f"case_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def create_policy_write_ready_project(root: Path) -> Path:
    state_root = root / ".jikuo"
    state_root.mkdir()
    (state_root / "project_state.yaml").write_text(
        "\n".join(
            [
                'schema: "jikuo.project_local_state.v0"',
                'project_id: "policy_write_ready_project"',
                f'project_root: "{root}"',
                f'jikuo_state_root: "{state_root}"',
                "active_scenario_packages:",
                '  - "engineering_governance"',
                "accepted_contract_refs:",
                '  - "docs/jikuo/governance/jikuo_policy_store_configuration_flow.md"',
                'registry_ref: "docs/scenarios/interactive_novel/governance/rule_registry.yaml"',
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
    return root


def run_status(project_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(TOOL),
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


class PolicyStoreStatusTests(unittest.TestCase):
    def test_missing_policy_store_reports_missing_without_write(self):
        completed = run_status(MISSING_PROJECT)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["schema"], "jikuo.policy_store_status.v0")
        self.assertTrue(report["report_only"])
        self.assertEqual(report["policy_store_status"], "missing")
        self.assertEqual(report["policy_eval_status"], "not_evaluated")
        self.assertEqual(report["active_policy_refs"], [])
        self.assertFalse((MISSING_PROJECT / ".jikuo" / "policies").exists())

    def test_initialized_policy_store_reports_no_active_policies(self):
        completed = run_status(INITIALIZED_PROJECT)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["policy_store_status"], "initialized")
        self.assertEqual(report["active_policy_refs"], [])
        self.assertIn("no active policy refs", report["status_reason"])

    def test_active_policy_store_summarizes_approved_policy_refs(self):
        completed = run_status(ACTIVE_PROJECT)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["policy_store_status"], "active")
        self.assertEqual(report["policy_eval_status"], "not_evaluated")
        self.assertEqual(len(report["active_policy_refs"]), 1)
        active_ref = report["active_policy_refs"][0]
        self.assertEqual(active_ref["policy_id"], "POLICY-three-phase-audit")
        self.assertEqual(active_ref["version"], 1)
        self.assertEqual(active_ref["title"], "Three-phase task audit")
        self.assertEqual(active_ref["schema_version"], "jikuo.configurable_rule_policy.v0")

    def test_stale_policy_store_reports_missing_active_ref(self):
        completed = run_status(STALE_PROJECT)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["policy_store_status"], "stale")
        self.assertIn("active policy ref is missing", "\n".join(report["warnings"]))

    def test_conflict_policy_store_refuses_duplicate_active_ids(self):
        completed = run_status(CONFLICT_PROJECT)

        self.assertEqual(completed.returncode, 2, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["policy_store_status"], "conflict")
        self.assertIn("duplicate active policy id", "\n".join(report["warnings"]))

    def test_evaluate_task_start_triggers_active_lifecycle_policy(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(ACTIVE_PROJECT),
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
        self.assertEqual(report["schema"], "jikuo.policy_trigger_eval_report.v0")
        self.assertEqual(report["policy_store_status"], "active")
        self.assertEqual(report["policy_eval_status"], "evaluated")
        self.assertEqual(len(report["triggered_policies"]), 1)
        self.assertEqual(
            report["triggered_policies"][0]["policy_ref"],
            "POLICY-three-phase-audit",
        )
        self.assertEqual(report["triggered_policies"][0]["confidence"], "tool_verified")
        self.assertEqual(len(report["required_actions"]), 1)
        self.assertEqual(
            report["required_actions"][0]["action_type"],
            "render_pre_task_review",
        )
        self.assertEqual(report["policy_evidence_check_status"], "checked")
        self.assertEqual(len(report["evidence_status"]), 1)
        self.assertEqual(report["evidence_status"][0]["current_status"], "missing")
        self.assertEqual(len(report["missing_evidence_reports"]), 1)
        self.assertFalse((ACTIVE_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_evaluate_task_start_accepts_inline_card_rendered_evidence(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(ACTIVE_PROJECT),
                "--produced-evidence-json",
                json.dumps(
                    [
                        {
                            "evidence_id": "EVD-inline-card",
                            "evidence_type": "card_rendered",
                            "action_type": "render_pre_task_review",
                            "status": "ok",
                            "summary": "inline proposal card evidence",
                        }
                    ]
                ),
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
        self.assertEqual(report["policy_evidence_check_status"], "checked")
        self.assertEqual(len(report["evidence_status"]), 1)
        self.assertEqual(report["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(report["evidence_status"][0]["evidence_refs"], ["EVD-inline-card"])
        self.assertEqual(report["missing_evidence_reports"], [])

    def test_evaluate_task_start_accepts_cli_card_rendered_evidence_flags(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(ACTIVE_PROJECT),
                "--produced-evidence-id",
                "EVD-cli-card",
                "--produced-evidence-type",
                "card_rendered",
                "--produced-evidence-action-type",
                "render_pre_task_review",
                "--produced-evidence-status",
                "ok",
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
        self.assertEqual(report["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(report["evidence_status"][0]["evidence_refs"], ["EVD-cli-card"])
        self.assertEqual(report["missing_evidence_reports"], [])

    def test_evaluate_task_start_accepts_persisted_task_session_policy_evidence(self):
        session_file = (
            EVIDENCE_PROJECT
            / ".jikuo"
            / "task_sessions"
            / "task_policy_evidence_probe.yaml"
        )
        before_text = session_file.read_text(encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(EVIDENCE_PROJECT),
                "--task-session-id",
                "task_policy_evidence_probe",
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
        self.assertEqual(report["policy_store_status"], "active")
        self.assertEqual(report["policy_eval_status"], "evaluated")
        self.assertEqual(report["policy_evidence_check_status"], "checked")
        self.assertEqual(report["task_session_id"], "task_policy_evidence_probe")
        self.assertEqual(len(report["evidence_status"]), 1)
        self.assertEqual(report["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            report["evidence_status"][0]["evidence_refs"],
            ["EVD-persisted-card"],
        )
        self.assertEqual(report["missing_evidence_reports"], [])
        self.assertEqual(
            report["evidence_source_refs"],
            [".jikuo/task_sessions/task_policy_evidence_probe.yaml"],
        )
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_evaluate_task_start_triggers_when_conditions_match(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(CONDITION_PROJECT),
                "--task-type",
                "work_order_delivery",
                "--jikuo-layer",
                "configurable_rule_kernel",
                "--changed-path",
                "docs/jikuo/work_orders/SPRINT_050_probe.md",
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
        self.assertEqual(report["policy_store_status"], "active")
        self.assertEqual(report["policy_eval_status"], "evaluated")
        self.assertEqual(report["policy_condition_eval_status"], "checked")
        self.assertEqual(len(report["condition_reports"]), 3)
        self.assertEqual(
            {item["status"] for item in report["condition_reports"]},
            {"matched"},
        )
        self.assertEqual(len(report["triggered_policies"]), 1)
        self.assertEqual(
            report["triggered_policies"][0]["policy_ref"],
            "POLICY-work-order-condition-audit",
        )
        self.assertEqual(len(report["required_actions"]), 1)
        self.assertEqual(report["evidence_status"][0]["current_status"], "missing")

    def test_evaluate_task_start_does_not_trigger_when_condition_misses(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(CONDITION_PROJECT),
                "--task-type",
                "runtime_bugfix",
                "--jikuo-layer",
                "configurable_rule_kernel",
                "--changed-path",
                "docs/jikuo/work_orders/SPRINT_050_probe.md",
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
        self.assertEqual(report["policy_condition_eval_status"], "checked")
        self.assertEqual(len(report["condition_reports"]), 3)
        self.assertIn(
            "not_matched",
            {item["status"] for item in report["condition_reports"]},
        )
        self.assertEqual(report["triggered_policies"], [])
        self.assertEqual(report["required_actions"], [])
        self.assertEqual(report["evidence_status"], [])
        self.assertEqual(report["missing_evidence_reports"], [])

    def test_evaluate_task_start_requires_review_when_condition_context_missing(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(CONDITION_PROJECT),
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
        self.assertEqual(report["policy_condition_eval_status"], "checked")
        self.assertEqual(
            {item["status"] for item in report["condition_reports"]},
            {"review_required"},
        )
        self.assertEqual(report["triggered_policies"], [])
        self.assertEqual(report["required_actions"], [])

    def test_evaluate_testing_governance_requires_real_data_and_chain_evidence(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(REAL_CHAIN_TESTING_PROJECT),
                "--task-type",
                "work_order_delivery",
                "--jikuo-layer",
                "testing_governance",
                "--changed-path",
                "tools/jikuo/policy_store_tests.py",
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
        self.assertEqual(report["policy_store_status"], "active")
        self.assertEqual(report["policy_eval_status"], "evaluated")
        self.assertEqual(report["policy_condition_eval_status"], "checked")
        self.assertEqual(len(report["triggered_policies"]), 1)
        self.assertEqual(
            report["triggered_policies"][0]["policy_ref"],
            "POLICY-real-test-data-and-chain",
        )
        self.assertEqual(
            report["required_actions"][0]["action_type"],
            "verify_real_test_data_and_real_chain",
        )
        self.assertEqual(report["evidence_status"][0]["current_status"], "missing")
        self.assertEqual(
            report["missing_evidence_reports"][0]["missing"][0]["required_type"],
            "real_test_data_and_chain_evidence",
        )

    def test_evaluate_testing_governance_accepts_real_chain_evidence(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(REAL_CHAIN_TESTING_PROJECT),
                "--task-type",
                "work_order_delivery",
                "--jikuo-layer",
                "testing_governance",
                "--changed-path",
                "tools/jikuo/policy_store_tests.py",
                "--produced-evidence-json",
                json.dumps(
                    [
                        {
                            "evidence_id": "EVD-real-chain-smoke",
                            "evidence_type": "real_test_data_and_chain_evidence",
                            "action_type": "verify_real_test_data_and_real_chain",
                            "status": "ok",
                            "summary": "used concrete fixture data through the evaluator path",
                        }
                    ]
                ),
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
        self.assertEqual(report["policy_evidence_check_status"], "checked")
        self.assertEqual(report["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            report["evidence_status"][0]["evidence_refs"],
            ["EVD-real-chain-smoke"],
        )
        self.assertEqual(report["missing_evidence_reports"], [])

    def test_evaluate_code_change_requires_layer_classification_evidence(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(REAL_CHAIN_TESTING_PROJECT),
                "--task-type",
                "code_change",
                "--jikuo-layer",
                "implementation_governance",
                "--changed-path",
                "tools/jikuo/policy_store.py",
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
        self.assertEqual(len(report["triggered_policies"]), 1)
        self.assertEqual(
            report["triggered_policies"][0]["policy_ref"],
            "POLICY-pre-code-change-layer-classification",
        )
        self.assertEqual(
            report["required_actions"][0]["action_type"],
            "classify_governance_vs_implementation_before_code_change",
        )
        self.assertEqual(report["evidence_status"][0]["current_status"], "missing")
        self.assertEqual(
            report["missing_evidence_reports"][0]["missing"][0]["required_type"],
            "governance_vs_implementation_classification_evidence",
        )

    def test_evaluate_code_change_accepts_layer_classification_evidence(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "task_start",
                "--project-root",
                str(REAL_CHAIN_TESTING_PROJECT),
                "--task-type",
                "code_change",
                "--jikuo-layer",
                "implementation_governance",
                "--changed-path",
                "tools/jikuo/policy_store.py",
                "--produced-evidence-json",
                json.dumps(
                    [
                        {
                            "evidence_id": "EVD-layer-classification-smoke",
                            "evidence_type": (
                                "governance_vs_implementation_classification_evidence"
                            ),
                            "action_type": (
                                "classify_governance_vs_implementation_before_code_change"
                            ),
                            "status": "ok",
                            "summary": (
                                "classified the issue as policy/governance before code"
                            ),
                        }
                    ]
                ),
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
        self.assertEqual(report["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            report["evidence_status"][0]["evidence_refs"],
            ["EVD-layer-classification-smoke"],
        )
        self.assertEqual(report["missing_evidence_reports"], [])

    def test_plan_write_builds_policy_write_plan_without_write(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "plan-write",
                "--project-root",
                str(MISSING_PROJECT),
                "--policy-id",
                "POLICY-three-phase-audit",
                "--title",
                "Three-phase task audit",
                "--source-ref",
                "<exact user phrase as spoken>",
                "--task-type",
                "work_order_delivery",
                "--jikuo-layer",
                "configurable_rule_kernel",
                "--changed-path-pattern",
                "docs/jikuo/**",
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
        self.assertEqual(report["schema"], "jikuo.policy_write_plan.v0")
        self.assertTrue(report["report_only"])
        self.assertEqual(report["status"], "review")
        self.assertFalse(report["writes_performed"])
        self.assertFalse(report["write_allowed_by_command"])
        self.assertEqual(report["policy_ref"], "POLICY-three-phase-audit")
        self.assertFalse(report["preflight"]["store_exists"])
        self.assertFalse(report["preflight"]["target_collision"])
        self.assertEqual(len(report["write_set"]), 4)
        self.assertEqual(
            report["write_set"][0]["path"],
            ".jikuo/policies/approved/POLICY-three-phase-audit.yaml",
        )
        self.assertTrue(
            report["write_set"][1]["path"].startswith(
                ".jikuo/policies/decisions/POLICYDECISION-"
            )
        )
        self.assertEqual(
            report["write_set"][2]["path"],
            ".jikuo/policies/manifest.yaml",
        )
        self.assertTrue(
            report["write_set"][3]["path"].startswith(
                ".jikuo/policies/proposals/POLICYPROPOSAL-"
            )
        )
        self.assertEqual(len(report["proposed_policy"]["conditions"]), 3)
        self.assertFalse((MISSING_PROJECT / ".jikuo" / "policies").exists())

    def test_plan_write_refuses_existing_policy_collision_without_write(self):
        policy_file = (
            ACTIVE_PROJECT
            / ".jikuo"
            / "policies"
            / "approved"
            / "POLICY-three-phase-audit.yaml"
        )
        before_text = policy_file.read_text(encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "plan-write",
                "--project-root",
                str(ACTIVE_PROJECT),
                "--policy-id",
                "POLICY-three-phase-audit",
                "--title",
                "Three-phase task audit",
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
        self.assertEqual(report["status"], "refused")
        self.assertTrue(report["preflight"]["target_collision"])
        self.assertIn(
            "target_policy_already_exists_or_active",
            report["refusal_reasons"],
        )
        self.assertEqual(policy_file.read_text(encoding="utf-8"), before_text)

    def test_plan_evolution_builds_no_write_policy_refinement_plan(self):
        policy_file = (
            ACTIVE_PROJECT
            / ".jikuo"
            / "policies"
            / "approved"
            / "POLICY-three-phase-audit.yaml"
        )
        before_text = policy_file.read_text(encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "plan-evolution",
                "--project-root",
                str(ACTIVE_PROJECT),
                "--policy-id",
                "POLICY-three-phase-audit",
                "--operation",
                "refine_policy",
                "--feedback-type",
                "needs_scope_narrowing",
                "--summary",
                "Triggered for a task that should not require this review.",
                "--source-ref",
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
        self.assertEqual(report["schema"], "jikuo.policy_evolution_plan.v0")
        self.assertEqual(report["status"], "review")
        self.assertFalse(report["writes_performed"])
        self.assertFalse(report["write_allowed_by_command"])
        self.assertEqual(report["operation"], "refine_policy")
        self.assertEqual(report["target_policy_ref"], "POLICY-three-phase-audit")
        self.assertEqual(
            report["feedback"]["feedback_type"],
            "needs_scope_narrowing",
        )
        self.assertTrue(report["future_write_boundary"]["requires_guarded_writer"])
        self.assertFalse(report["future_write_boundary"]["writer_implemented"])
        self.assertIn(
            "narrow task_type, jikuo_layer, changed_path, or added_path conditions",
            report["recommended_changes"],
        )
        self.assertEqual(policy_file.read_text(encoding="utf-8"), before_text)

    def test_plan_evolution_refuses_unknown_policy_without_write(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "plan-evolution",
                "--project-root",
                str(ACTIVE_PROJECT),
                "--policy-id",
                "POLICY-does-not-exist",
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
        self.assertEqual(report["status"], "refused")
        self.assertFalse(report["writes_performed"])
        self.assertIn("target_policy_not_active", report["refusal_reasons"])

    def test_write_evolution_requires_confirmation_without_write(self):
        with temp_project_dir() as temp_root:
            project_root = temp_root / "policy_store_active_project"
            shutil.copytree(ACTIVE_PROJECT, project_root)
            manifest_path = project_root / ".jikuo" / "policies" / "manifest.yaml"
            before_text = manifest_path.read_text(encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "write-evolution",
                    "--project-root",
                    str(project_root),
                    "--policy-id",
                    "POLICY-three-phase-audit",
                    "--operation",
                    "deprecate_policy",
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
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertIn("missing_confirmation_flag", result["refusal_reasons"])
            self.assertIn("approval_evidence_missing", result["refusal_reasons"])
            self.assertEqual(manifest_path.read_text(encoding="utf-8"), before_text)

    def test_write_evolution_deprecates_policy_and_evaluate_no_longer_triggers(self):
        with temp_project_dir() as temp_root:
            project_root = temp_root / "policy_store_active_project"
            shutil.copytree(ACTIVE_PROJECT, project_root)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "write-evolution",
                    "--project-root",
                    str(project_root),
                    "--policy-id",
                    "POLICY-three-phase-audit",
                    "--operation",
                    "deprecate_policy",
                    "--feedback-type",
                    "not_applicable",
                    "--summary",
                    "Policy should stop triggering for this project.",
                    "--source-ref",
                    "<exact user phrase as spoken>",
                    "--confirm-write-evolution",
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
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["operation"], "deprecate_policy")
            self.assertIn(result["proposal_ref"], result["written_paths"])
            self.assertIn(result["decision_record_ref"], result["written_paths"])
            self.assertTrue(result["post_write_verification"]["proposal_snapshot_written"])
            self.assertTrue(result["post_write_verification"]["decision_record_written"])
            self.assertFalse(result["post_write_verification"]["active_policy_resolvable"])
            self.assertFalse(result["post_write_verification"]["target_policy_active"])
            self.assertTrue(result["post_write_verification"]["target_policy_deprecated"])

            status = run_status(project_root)
            self.assertEqual(status.returncode, 0, status.stderr)
            status_report = json.loads(status.stdout)
            self.assertEqual(status_report["policy_store_status"], "initialized")
            self.assertEqual(status_report["active_policy_refs"], [])
            self.assertEqual(
                status_report["deprecated_policy_refs"][0]["policy_id"],
                "POLICY-three-phase-audit",
            )

            evaluation = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "evaluate",
                    "--event",
                    "task_start",
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
            self.assertEqual(evaluation.returncode, 0, evaluation.stderr)
            eval_report = json.loads(evaluation.stdout)
            self.assertEqual(eval_report["policy_eval_status"], "not_evaluated")
            self.assertEqual(eval_report["triggered_policies"], [])

    def test_write_evolution_supersedes_policy_and_replacement_triggers(self):
        with temp_project_dir() as temp_root:
            project_root = temp_root / "policy_store_active_project"
            shutil.copytree(ACTIVE_PROJECT, project_root)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "write-evolution",
                    "--project-root",
                    str(project_root),
                    "--policy-id",
                    "POLICY-three-phase-audit",
                    "--operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy.",
                    "--source-ref",
                    "User asked to replace the broad three-phase audit policy with a narrower v2 policy.",
                    "--replacement-policy-id",
                    "POLICY-three-phase-audit-v2",
                    "--replacement-title",
                    "Three-phase task audit v2",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
                    "testing_governance",
                    "--confirm-write-evolution",
                    "--approval-phrase",
                    "I approve superseding POLICY-three-phase-audit with POLICY-three-phase-audit-v2 in this temp project.",
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
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["operation"], "supersede_policy")
            self.assertEqual(result["replacement_policy_ref"], "POLICY-three-phase-audit-v2")
            self.assertIn(result["proposal_ref"], result["written_paths"])
            self.assertIn(
                ".jikuo/policies/approved/POLICY-three-phase-audit-v2.yaml",
                result["written_paths"],
            )
            self.assertTrue(result["post_write_verification"]["proposal_snapshot_written"])
            self.assertTrue(result["post_write_verification"]["decision_record_written"])
            self.assertFalse(result["post_write_verification"]["target_policy_active"])
            self.assertTrue(result["post_write_verification"]["target_policy_superseded"])
            self.assertTrue(result["post_write_verification"]["replacement_policy_active"])

            status = run_status(project_root)
            self.assertEqual(status.returncode, 0, status.stderr)
            status_report = json.loads(status.stdout)
            self.assertEqual(status_report["policy_store_status"], "active")
            self.assertEqual(
                status_report["active_policy_refs"][0]["policy_id"],
                "POLICY-three-phase-audit-v2",
            )
            self.assertEqual(
                status_report["superseded_policy_refs"][0]["policy_id"],
                "POLICY-three-phase-audit",
            )
            self.assertEqual(
                status_report["superseded_policy_refs"][0]["superseded_by"],
                "POLICY-three-phase-audit-v2",
            )

            evaluation = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "evaluate",
                    "--event",
                    "task_start",
                    "--project-root",
                    str(project_root),
                    "--task-type",
                    "work_order_delivery",
                    "--jikuo-layer",
                    "testing_governance",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(evaluation.returncode, 0, evaluation.stderr)
            eval_report = json.loads(evaluation.stdout)
            self.assertEqual(eval_report["policy_eval_status"], "evaluated")
            self.assertEqual(len(eval_report["triggered_policies"]), 1)
            self.assertEqual(
                eval_report["triggered_policies"][0]["policy_ref"],
                "POLICY-three-phase-audit-v2",
            )

    def test_write_policy_requires_confirmation_and_approval_without_write(self):
        with temp_project_dir() as temp_root:
            project_root = create_policy_write_ready_project(temp_root)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "write-policy",
                    "--project-root",
                    str(project_root),
                    "--policy-id",
                    "POLICY-work-order-pre-task-review",
                    "--title",
                    "Work-order pre-task review card",
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
            self.assertEqual(result["schema"], "jikuo.policy_write_result.v0")
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertIn("missing_confirmation_flag", result["refusal_reasons"])
            self.assertIn("approval_evidence_missing", result["refusal_reasons"])
            self.assertFalse((project_root / ".jikuo" / "policies").exists())

    def test_write_policy_creates_initial_store_and_evaluate_reads_policy(self):
        with temp_project_dir() as temp_root:
            project_root = create_policy_write_ready_project(temp_root)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "write-policy",
                    "--project-root",
                    str(project_root),
                    "--policy-id",
                    "POLICY-work-order-pre-task-review",
                    "--title",
                    "Work-order pre-task review card",
                    "--source-ref",
                    "<exact user phrase as spoken>",
                    "--task-type",
                    "work_order_delivery",
                    "--jikuo-layer",
                    "configurable_rule_kernel",
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

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["schema"], "jikuo.policy_write_result.v0")
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["policy_store_status_before"], "missing")
            self.assertEqual(result["policy_store_status_after"], "active")
            self.assertEqual(
                result["written_paths"],
                [
                    result["proposal_ref"],
                    ".jikuo/policies/approved/POLICY-work-order-pre-task-review.yaml",
                    result["decision_record_ref"],
                    ".jikuo/policies/manifest.yaml",
                ],
            )
            policy_file = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-work-order-pre-task-review.yaml"
            )
            self.assertTrue(policy_file.exists())
            proposal_path = project_root / result["proposal_ref"]
            self.assertTrue(proposal_path.exists())
            proposal_text = proposal_path.read_text(encoding="utf-8")
            self.assertIn('schema_version: "jikuo.policy_write_plan.v0"', proposal_text)
            self.assertIn('policy_ref: "POLICY-work-order-pre-task-review"', proposal_text)
            decision_path = project_root / result["decision_record_ref"]
            self.assertTrue(decision_path.exists())
            decision_text = decision_path.read_text(encoding="utf-8")
            self.assertIn('schema_version: "jikuo.policy_decision.v0"', decision_text)
            self.assertIn('decision: "approve_write"', decision_text)
            self.assertIn('policy_ref: "POLICY-work-order-pre-task-review"', decision_text)
            self.assertIn(f'proposal_ref: "{result["proposal_ref"]}"', decision_text)
            self.assertTrue(result["post_write_verification"]["proposal_snapshot_written"])
            self.assertTrue(result["post_write_verification"]["decision_record_written"])
            self.assertTrue((project_root / ".jikuo" / "policies" / "manifest.yaml").exists())

            status = run_status(project_root)
            self.assertEqual(status.returncode, 0, status.stderr)
            status_report = json.loads(status.stdout)
            self.assertEqual(status_report["policy_store_status"], "active")
            self.assertEqual(
                status_report["active_policy_refs"][0]["policy_id"],
                "POLICY-work-order-pre-task-review",
            )
            self.assertEqual(
                status_report["proposal_refs"][0]["policy_id"],
                "POLICY-work-order-pre-task-review",
            )

            evaluation = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "evaluate",
                    "--event",
                    "task_start",
                    "--project-root",
                    str(project_root),
                    "--task-type",
                    "work_order_delivery",
                    "--jikuo-layer",
                    "configurable_rule_kernel",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(evaluation.returncode, 0, evaluation.stderr)
            eval_report = json.loads(evaluation.stdout)
            self.assertEqual(eval_report["policy_eval_status"], "evaluated")
            self.assertEqual(len(eval_report["triggered_policies"]), 1)
            self.assertEqual(
                eval_report["triggered_policies"][0]["policy_ref"],
                "POLICY-work-order-pre-task-review",
            )

    def test_write_policy_refuses_existing_policy_collision(self):
        with temp_project_dir() as temp_root:
            project_root = create_policy_write_ready_project(temp_root)
            command = [
                sys.executable,
                "-B",
                str(TOOL),
                "write-policy",
                "--project-root",
                str(project_root),
                "--policy-id",
                "POLICY-work-order-pre-task-review",
                "--title",
                "Work-order pre-task review card",
                "--source-ref",
                "<exact user phrase as spoken>",
                "--confirm-write-policy",
                "--approval-phrase",
                "<exact user phrase as spoken>",
                "--format",
                "json",
            ]
            first = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            policy_file = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-work-order-pre-task-review.yaml"
            )
            before_text = policy_file.read_text(encoding="utf-8")
            second = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(second.returncode, 2, second.stderr)
            result = json.loads(second.stdout)
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertIn(
                "target_policy_already_exists_or_active",
                result["refusal_reasons"],
            )
            self.assertEqual(policy_file.read_text(encoding="utf-8"), before_text)

    def test_write_policy_appends_second_policy_to_active_store(self):
        with temp_project_dir() as temp_root:
            project_root = create_policy_write_ready_project(temp_root)
            first = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "write-policy",
                    "--project-root",
                    str(project_root),
                    "--policy-id",
                    "POLICY-bootstrap-review",
                    "--title",
                    "Bootstrap review",
                    "--source-ref",
                    "<exact user phrase as spoken>",
                    "--task-type",
                    "bootstrap_task",
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

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "write-policy",
                    "--project-root",
                    str(project_root),
                    "--policy-id",
                    "POLICY-work-order-pre-task-review",
                    "--title",
                    "Work-order pre-task review card",
                    "--source-ref",
                    "<exact user phrase as spoken>",
                    "--task-type",
                    "work_order_delivery",
                    "--jikuo-layer",
                    "configurable_rule_kernel",
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

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["operation"], "append_policy")
            self.assertEqual(result["status"], "written")
            self.assertEqual(result["policy_store_status_before"], "active")
            self.assertEqual(result["policy_store_status_after"], "active")
            self.assertTrue((project_root / result["proposal_ref"]).exists())
            self.assertTrue(result["post_write_verification"]["proposal_snapshot_written"])
            self.assertTrue(result["decision_record_ref"].startswith(".jikuo/policies/decisions/"))
            self.assertTrue((project_root / result["decision_record_ref"]).exists())
            self.assertTrue(result["post_write_verification"]["decision_record_written"])

            manifest_path = project_root / ".jikuo" / "policies" / "manifest.yaml"
            manifest_text = manifest_path.read_text(encoding="utf-8")
            self.assertIn("POLICY-bootstrap-review", manifest_text)
            self.assertIn("POLICY-work-order-pre-task-review", manifest_text)
            self.assertIn('unknown_fields: "preserve"', manifest_text)

            status = run_status(project_root)
            self.assertEqual(status.returncode, 0, status.stderr)
            status_report = json.loads(status.stdout)
            self.assertEqual(status_report["policy_store_status"], "active")
            self.assertEqual(len(status_report["active_policy_refs"]), 2)
            self.assertEqual(len(status_report["proposal_refs"]), 2)
            self.assertEqual(
                status_report["proposal_refs"][1]["policy_id"],
                "POLICY-work-order-pre-task-review",
            )

            evaluation = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "evaluate",
                    "--event",
                    "task_start",
                    "--project-root",
                    str(project_root),
                    "--task-type",
                    "work_order_delivery",
                    "--jikuo-layer",
                    "configurable_rule_kernel",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(evaluation.returncode, 0, evaluation.stderr)
            eval_report = json.loads(evaluation.stdout)
            self.assertEqual(eval_report["policy_eval_status"], "evaluated")
            self.assertEqual(len(eval_report["triggered_policies"]), 1)
            self.assertEqual(
                eval_report["triggered_policies"][0]["policy_ref"],
                "POLICY-work-order-pre-task-review",
            )

    def test_evaluate_non_matching_event_does_not_trigger_policy(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "evaluate",
                "--event",
                "completion_review",
                "--project-root",
                str(ACTIVE_PROJECT),
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
        self.assertEqual(report["policy_eval_status"], "evaluated")
        self.assertEqual(report["triggered_policies"], [])
        self.assertEqual(report["required_actions"], [])


if __name__ == "__main__":
    unittest.main()
