import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "agent_flow.py"
POLICY_STORE_TOOL = ROOT / "src" / "jikuo" / "policy_store.py"
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
READY_PROJECT = FIXTURES / "task_session_ready_project"
MISSING_PROJECT = FIXTURES / "missing_project"
POLICY_ACTIVE_PROJECT = FIXTURES / "policy_store_active_project"
POLICY_EVIDENCE_SESSION_PROJECT = FIXTURES / "policy_evidence_session_project"
POLICY_EVIDENCE_INGEST_PROJECT = FIXTURES / "policy_store_evidence_project"
POLICY_CONDITION_PROJECT = FIXTURES / "policy_store_condition_project"
POLICY_REAL_CHAIN_PROJECT = FIXTURES / "policy_store_real_chain_testing_project"


class AgentFlowProposalTests(unittest.TestCase):
    def test_task_start_propose_json_composes_no_write_atoms(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Agent Flow Probe",
                "--project-root",
                str(READY_PROJECT),
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
        self.assertEqual(proposal["schema"], "jikuo.agent_flow_proposal.v1")
        self.assertEqual(proposal["previous_schema"], "jikuo.agent_flow_proposal.v0")
        self.assertTrue(proposal["report_only"])
        self.assertEqual(proposal["runner_mode"], "propose")
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertIn(
            "does not create .jikuo/policies/",
            proposal["write_effect"]["non_effects"],
        )
        self.assertEqual(proposal["trigger_decision"]["invocation_scenario"], "task_start")
        self.assertEqual(proposal["trigger_decision"]["confidence"], "event_match")
        self.assertEqual(
            proposal["trigger_decision"]["confidence_basis"],
            "canonical_event_mapping",
        )
        self.assertEqual(
            proposal["trigger_decision"]["intent_classification"]["confidence"],
            "not_evaluated_by_runner",
        )
        self.assertEqual(proposal["trigger_decision"]["execution_readiness"], "ready")
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "missing")
        self.assertEqual(proposal["policy_context"]["policy_eval_status"], "not_evaluated")
        self.assertEqual(proposal["triggered_policies"], [])
        self.assertEqual(proposal["required_actions"], [])
        self.assertEqual(proposal["evidence_status"], [])
        self.assertEqual(proposal["missing_evidence_reports"], [])
        self.assertEqual(proposal["policy_feedback_options"], [])
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-TASK-START-DRYRUN-01", atom_ids)
        self.assertIn("CAP-CARD-TASKSESSION-01", atom_ids)
        self.assertIn("CAP-POLICY-STORE-STATUS-01", atom_ids)
        self.assertEqual(proposal["cards"][0]["card_kind"], "task_session_start_preview")
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_missing_project_status_markdown_remains_no_write(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "status",
                "--project-root",
                str(MISSING_PROJECT),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("JIKUO Agent Flow Proposal", completed.stdout)
        self.assertIn("Writes performed: `false`", completed.stdout)
        self.assertIn("Match confidence: `event_match`", completed.stdout)
        self.assertIn("Match basis: `canonical_event_mapping`", completed.stdout)
        self.assertIn("Intent confidence: `not_evaluated_by_runner`", completed.stdout)
        self.assertNotIn("Confidence: `high`", completed.stdout)
        self.assertIn("Policy Context", completed.stdout)
        self.assertIn("Policy store status: `missing`", completed.stdout)
        self.assertIn("Policy eval status: `not_evaluated`", completed.stdout)
        self.assertIn("CAP-PROJECT-STATE-STATUS-01", completed.stdout)
        self.assertIn("CAP-PROJECT-STATE-INIT-DRYRUN-01", completed.stdout)
        self.assertFalse((MISSING_PROJECT / ".jikuo").exists())

    def test_task_continue_without_session_id_refuses_without_write(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_continue",
                "--project-root",
                str(READY_PROJECT),
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
        proposal = json.loads(completed.stdout)
        self.assertEqual(proposal["status"], "refused")
        self.assertEqual(proposal["trigger_decision"]["confidence"], "event_match")
        self.assertEqual(proposal["trigger_decision"]["execution_readiness"], "blocked")
        self.assertEqual(proposal["cards"][0]["card_kind"], "task_continue_refusal")
        self.assertIn(
            "session_id_required_for_task_continue",
            proposal["cards"][0]["refusal_reasons"],
        )
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "missing")
        self.assertEqual(proposal["policy_context"]["policy_eval_status"], "not_evaluated")
        self.assertEqual(proposal["missing_evidence_reports"], [])
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_active_policy_store_triggers_exact_lifecycle_policy(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Policy Store Probe",
                "--project-root",
                str(POLICY_ACTIVE_PROJECT),
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
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
        self.assertEqual(proposal["policy_context"]["policy_eval_status"], "evaluated")
        self.assertEqual(
            proposal["policy_context"]["policy_evidence_check_status"],
            "checked",
        )
        self.assertEqual(len(proposal["policy_context"]["active_policy_refs"]), 1)
        self.assertEqual(
            proposal["policy_context"]["active_policy_refs"][0]["policy_id"],
            "POLICY-three-phase-audit",
        )
        self.assertEqual(len(proposal["triggered_policies"]), 1)
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-three-phase-audit",
        )
        self.assertEqual(proposal["triggered_policies"][0]["confidence"], "tool_verified")
        self.assertEqual(len(proposal["required_actions"]), 1)
        self.assertEqual(
            proposal["required_actions"][0]["action_type"],
            "render_pre_task_review",
        )
        self.assertEqual(len(proposal["evidence_status"]), 1)
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            proposal["evidence_status"][0]["required_type"],
            "card_rendered",
        )
        self.assertEqual(proposal["missing_evidence_reports"], [])
        self.assertEqual(
            {item["feedback_type"] for item in proposal["policy_feedback_options"]},
            {"not_applicable", "defer", "needs_scope_narrowing"},
        )
        self.assertEqual(
            {
                item["persistence"]
                for item in proposal["policy_feedback_options"]
            },
            {"not_persisted_by_agent_flow_propose"},
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-STORE-STATUS-01", atom_ids)
        self.assertIn("CAP-POLICY-TRIGGER-EVALUATE-01", atom_ids)
        self.assertIn("CAP-POLICY-EVIDENCE-CHECK-01", atom_ids)
        self.assertFalse((POLICY_ACTIVE_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_policy_evidence_record_proposes_guarded_append_without_write(self):
        session_file = (
            POLICY_EVIDENCE_SESSION_PROJECT
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
                "propose",
                "--event",
                "policy_evidence_record",
                "--session-id",
                "task_policy_evidence_probe",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--action-ref",
                "ACT-render-pre-task-review",
                "--requirement-ref",
                "EVD-card-rendered",
                "--evidence-kind",
                "card_rendered",
                "--evidence-ref",
                "EVD-card-rendered",
                "--project-root",
                str(POLICY_EVIDENCE_SESSION_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(proposal["trigger_decision"]["invocation_scenario"], "policy_evidence_record")
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01", atom_ids)
        self.assertIn("CAP-TASK-UPDATE-DRYRUN-01", atom_ids)
        self.assertEqual(proposal["cards"][0]["card_kind"], "task_session_evidence_append")
        command = proposal["cards"][0]["command_proposal"]["command_preview"]
        self.assertIn("python -B -m jikuo.task_session", command)
        self.assertNotIn("tools/jikuo", command)
        self.assertIn("--append-evidence", command)
        self.assertIn("--confirm-update-task-session", command)
        self.assertIn("--approval-phrase", command)
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_policy_feedback_record_proposes_guarded_append_without_write(self):
        session_file = (
            POLICY_EVIDENCE_SESSION_PROJECT
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
                "propose",
                "--event",
                "policy_feedback_record",
                "--session-id",
                "task_policy_evidence_probe",
                "--policy-ref",
                "POLICY-real-test-data-and-chain",
                "--feedback-type",
                "not_applicable",
                "--summary",
                "User marked this triggered policy as not applicable for this task.",
                "--project-root",
                str(POLICY_EVIDENCE_SESSION_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "policy_feedback_record",
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-FEEDBACK-PERSIST-PROPOSE-01", atom_ids)
        self.assertIn("CAP-TASK-UPDATE-DRYRUN-01", atom_ids)
        self.assertEqual(proposal["cards"][0]["card_kind"], "task_session_evidence_append")
        command = proposal["cards"][0]["command_proposal"]["command_preview"]
        self.assertIn("python -B -m jikuo.task_session", command)
        self.assertNotIn("tools/jikuo", command)
        self.assertIn("--append-evidence", command)
        self.assertIn("policy_feedback:not_applicable", command)
        self.assertIn("policy_ref=POLICY-real-test-data-and-chain", command)
        self.assertIn("feedback_type=not_applicable", command)
        self.assertIn("--confirm-update-task-session", command)
        self.assertIn("--approval-phrase", command)
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_policy_feedback_record_refuses_without_summary_or_user_phrase(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_feedback_record",
                "--session-id",
                "task_policy_evidence_probe",
                "--policy-ref",
                "POLICY-real-test-data-and-chain",
                "--feedback-type",
                "defer",
                "--project-root",
                str(POLICY_EVIDENCE_SESSION_PROJECT),
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
        proposal = json.loads(completed.stdout)
        self.assertEqual(proposal["status"], "refused")
        self.assertEqual(proposal["cards"][0]["card_kind"], "policy_feedback_record_refusal")
        self.assertIn(
            "summary_or_user_phrase_required_for_policy_feedback_record",
            proposal["cards"][0]["refusal_reasons"],
        )
        self.assertFalse(
            (POLICY_EVIDENCE_SESSION_PROJECT / ".jikuo" / "policies").exists()
        )

    def test_apply_task_session_evidence_update_refuses_without_approval(self):
        session_file = (
            POLICY_EVIDENCE_SESSION_PROJECT
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
                "apply",
                "--operation",
                "task_session_evidence_update",
                "--session-id",
                "task_policy_evidence_probe",
                "--evidence-kind",
                "policy_feedback:not_applicable",
                "--evidence-ref",
                "policy_ref=POLICY-real-test-data-and-chain;feedback_type=not_applicable",
                "--summary",
                "User marked this triggered policy as not applicable for this task.",
                "--project-root",
                str(POLICY_EVIDENCE_SESSION_PROJECT),
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
        self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
        self.assertFalse(report["write_performed"])
        self.assertEqual(report["status"], "refused")
        self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
        self.assertIn("approval_evidence_missing", report["refusal_reasons"])
        atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
        self.assertIn("CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01", atom_ids)
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_apply_task_session_evidence_update_writes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "policy_evidence_session_project"
            shutil.copytree(POLICY_EVIDENCE_SESSION_PROJECT, project_copy)
            session_file = (
                project_copy
                / ".jikuo"
                / "task_sessions"
                / "task_policy_evidence_probe.yaml"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "task_session_evidence_update",
                    "--session-id",
                    "task_policy_evidence_probe",
                    "--evidence-kind",
                    "policy_feedback:not_applicable",
                    "--evidence-ref",
                    "policy_ref=POLICY-real-test-data-and-chain;feedback_type=not_applicable",
                    "--summary",
                    "User marked this triggered policy as not applicable for this task.",
                    "--project-root",
                    str(project_copy),
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve this task-session evidence append.",
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
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(
                report["target_result_schema"],
                "jikuo.task_session_update_result.v0",
            )
            self.assertTrue(
                report["target_result"]["verification"]["patch_applied"]
            )
            updated = session_file.read_text(encoding="utf-8")
            self.assertIn("policy_feedback:not_applicable", updated)
            self.assertIn("POLICY-real-test-data-and-chain", updated)
            self.assertIn(
                "User marked this triggered policy as not applicable for this task.",
                updated,
            )

    def test_apply_starter_policy_pack_init_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "starter_project"
            project_root.mkdir()
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "starter_policy_pack_init",
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

            self.assertEqual(completed.returncode, 2, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "starter_policy_pack_init")
            self.assertEqual(report["status"], "refused")
            self.assertFalse(report["write_performed"])
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            self.assertFalse((project_root / ".jikuo").exists())

    def test_apply_starter_policy_pack_init_writes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "starter_project"
            project_root.mkdir()
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "starter_policy_pack_init",
                    "--project-root",
                    str(project_root),
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve starter policy initialization through agent_flow.",
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
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "starter_policy_pack_init")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(
                report["target_result_schema"],
                "jikuo.starter_policy_pack_init_result.v0",
            )
            self.assertTrue((project_root / ".jikuo" / "project_state.yaml").is_file())
            approved = project_root / ".jikuo" / "policies" / "approved"
            self.assertEqual(len(list(approved.glob("POLICY-*.yaml"))), 4)
            self.assertTrue(
                report["target_result"]["post_write_verification"]["starter_policies_active"]
            )
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn("CAP-AGENT-FLOW-APPLY-STARTER-POLICY-PACK-01", atom_ids)

    def test_apply_policy_evolution_write_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "policy_store_active_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_copy)
            manifest_file = project_copy / ".jikuo" / "policies" / "manifest.yaml"
            before_text = manifest_file.read_text(encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_evolution_write",
                    "--project-root",
                    str(project_copy),
                    "--policy-ref",
                    "POLICY-three-phase-audit",
                    "--policy-evolution-operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy through agent_flow apply.",
                    "--policy-source-ref",
                    "User asked agent_flow apply to supersede the broad three-phase policy.",
                    "--replacement-policy-ref",
                    "POLICY-three-phase-audit-agent-flow-v2",
                    "--replacement-title",
                    "Three-phase task audit agent-flow v2",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
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

            self.assertEqual(completed.returncode, 2, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "policy_evolution_write")
            self.assertFalse(report["write_performed"])
            self.assertEqual(report["status"], "refused")
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            self.assertIn(
                "proposal_ref_required_for_policy_evolution_apply",
                report["refusal_reasons"],
            )
            self.assertEqual(report["proposal_binding"]["status"], "missing")
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn("CAP-POLICY-EVOLUTION-APPLY-BINDING-01", atom_ids)
            self.assertIn("CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01", atom_ids)
            self.assertEqual(manifest_file.read_text(encoding="utf-8"), before_text)

    def test_apply_policy_evolution_write_refuses_mismatched_proposal_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "policy_store_active_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_copy)
            manifest_file = project_copy / ".jikuo" / "policies" / "manifest.yaml"
            before_text = manifest_file.read_text(encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_evolution_write",
                    "--project-root",
                    str(project_copy),
                    "--policy-ref",
                    "POLICY-three-phase-audit",
                    "--proposal-ref",
                    ".jikuo/policies/proposals/POLICYEVOPROPOSAL-not-approved.yaml",
                    "--policy-evolution-operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy through agent_flow apply.",
                    "--policy-source-ref",
                    "User approved agent_flow apply supersession for the broad three-phase policy.",
                    "--replacement-policy-ref",
                    "POLICY-three-phase-audit-agent-flow-v2",
                    "--replacement-title",
                    "Three-phase task audit agent-flow v2",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
                    "testing_governance",
                    "--replacement-changed-path-pattern",
                    "docs/jikuo/**",
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve agent_flow applying this policy supersession.",
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
            self.assertFalse(report["write_performed"])
            self.assertIn(
                "proposal_ref_mismatch_for_policy_evolution_apply",
                report["refusal_reasons"],
            )
            self.assertEqual(report["proposal_binding"]["status"], "mismatch")
            self.assertEqual(
                report["proposal_binding"]["provided_ref"],
                ".jikuo/policies/proposals/POLICYEVOPROPOSAL-not-approved.yaml",
            )
            self.assertNotEqual(
                report["proposal_binding"]["provided_ref"],
                report["proposal_binding"]["expected_ref"],
            )
            atom_ids = {trace["atom_id"] for trace in report["atom_trace"]}
            self.assertIn("CAP-POLICY-EVOLUTION-APPLY-BINDING-01", atom_ids)
            self.assertEqual(manifest_file.read_text(encoding="utf-8"), before_text)

    def test_apply_policy_evolution_write_supersedes_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_copy = Path(tmp) / "policy_store_active_project"
            shutil.copytree(POLICY_ACTIVE_PROJECT, project_copy)
            plan = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(POLICY_STORE_TOOL),
                    "plan-evolution",
                    "--project-root",
                    str(project_copy),
                    "--policy-id",
                    "POLICY-three-phase-audit",
                    "--operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy through agent_flow apply.",
                    "--source-ref",
                    "User approved agent_flow apply supersession for the broad three-phase policy.",
                    "--replacement-policy-id",
                    "POLICY-three-phase-audit-agent-flow-v2",
                    "--replacement-title",
                    "Three-phase task audit agent-flow v2",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
                    "testing_governance",
                    "--replacement-changed-path-pattern",
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
            self.assertEqual(plan.returncode, 0, plan.stderr)
            proposal_ref = json.loads(plan.stdout)["proposal_ref"]
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "apply",
                    "--operation",
                    "policy_evolution_write",
                    "--project-root",
                    str(project_copy),
                    "--policy-ref",
                    "POLICY-three-phase-audit",
                    "--proposal-ref",
                    proposal_ref,
                    "--policy-evolution-operation",
                    "supersede_policy",
                    "--feedback-type",
                    "needs_scope_narrowing",
                    "--summary",
                    "Replace with a narrower policy through agent_flow apply.",
                    "--policy-source-ref",
                    "User approved agent_flow apply supersession for the broad three-phase policy.",
                    "--replacement-policy-ref",
                    "POLICY-three-phase-audit-agent-flow-v2",
                    "--replacement-title",
                    "Three-phase task audit agent-flow v2",
                    "--replacement-task-type",
                    "work_order_delivery",
                    "--replacement-jikuo-layer",
                    "testing_governance",
                    "--replacement-changed-path-pattern",
                    "docs/jikuo/**",
                    "--confirm-apply",
                    "--approval-phrase",
                    "I approve agent_flow applying this policy supersession.",
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
            self.assertEqual(report["schema"], "jikuo.agent_flow_apply_result.v0")
            self.assertEqual(report["operation"], "policy_evolution_write")
            self.assertEqual(report["status"], "applied")
            self.assertTrue(report["write_performed"])
            self.assertEqual(report["proposal_binding"]["status"], "ok")
            self.assertEqual(report["proposal_binding"]["provided_ref"], proposal_ref)
            self.assertEqual(report["proposal_binding"]["expected_ref"], proposal_ref)
            self.assertEqual(report["target_result_schema"], "jikuo.policy_write_result.v0")
            target = report["target_result"]
            self.assertEqual(target["status"], "written")
            self.assertEqual(target["operation"], "supersede_policy")
            self.assertEqual(target["proposal_ref"], proposal_ref)
            self.assertEqual(
                target["replacement_policy_ref"],
                "POLICY-three-phase-audit-agent-flow-v2",
            )
            self.assertIn(
                ".jikuo/policies/approved/POLICY-three-phase-audit-agent-flow-v2.yaml",
                target["written_paths"],
            )
            self.assertTrue(target["post_write_verification"]["target_policy_superseded"])
            self.assertTrue(target["post_write_verification"]["replacement_policy_active"])

            status = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(POLICY_STORE_TOOL),
                    "status",
                    "--project-root",
                    str(project_copy),
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
            self.assertEqual(
                status_report["active_policy_refs"][0]["policy_id"],
                "POLICY-three-phase-audit-agent-flow-v2",
            )
            self.assertEqual(
                status_report["superseded_policy_refs"][0]["policy_id"],
                "POLICY-three-phase-audit",
            )

            evaluation = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(POLICY_STORE_TOOL),
                    "evaluate",
                    "--event",
                    "task_start",
                    "--project-root",
                    str(project_copy),
                    "--task-type",
                    "work_order_delivery",
                    "--jikuo-layer",
                    "testing_governance",
                    "--changed-path",
                    "docs/jikuo/example.md",
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
            self.assertEqual(len(eval_report["triggered_policies"]), 1)
            self.assertEqual(
                eval_report["triggered_policies"][0]["policy_ref"],
                "POLICY-three-phase-audit-agent-flow-v2",
            )

    def test_policy_evidence_check_ingests_persisted_session_evidence_without_write(self):
        session_file = (
            POLICY_EVIDENCE_INGEST_PROJECT
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
                "propose",
                "--event",
                "policy_evidence_check",
                "--policy-event",
                "task_start",
                "--session-id",
                "task_policy_evidence_probe",
                "--project-root",
                str(POLICY_EVIDENCE_INGEST_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "policy_evidence_check",
        )
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
        self.assertEqual(proposal["policy_context"]["policy_eval_status"], "evaluated")
        self.assertEqual(
            proposal["policy_context"]["policy_evidence_check_status"],
            "checked",
        )
        self.assertEqual(
            proposal["policy_context"]["task_session_id"],
            "task_policy_evidence_probe",
        )
        self.assertEqual(
            proposal["policy_context"]["evidence_source_refs"],
            [".jikuo/task_sessions/task_policy_evidence_probe.yaml"],
        )
        self.assertEqual(len(proposal["evidence_status"]), 1)
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            proposal["evidence_status"][0]["evidence_refs"],
            ["EVD-persisted-card"],
        )
        self.assertEqual(proposal["missing_evidence_reports"], [])
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-EVIDENCE-INGEST-01", atom_ids)
        self.assertIn("CAP-POLICY-EVIDENCE-CHECK-01", atom_ids)
        self.assertEqual(session_file.read_text(encoding="utf-8"), before_text)

    def test_task_start_with_matching_policy_conditions_projects_condition_reports(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Condition Probe",
                "--project-root",
                str(POLICY_CONDITION_PROJECT),
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
        proposal = json.loads(completed.stdout)
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["policy_context"]["policy_condition_eval_status"],
            "checked",
        )
        self.assertEqual(len(proposal["condition_reports"]), 3)
        self.assertEqual(
            {item["status"] for item in proposal["condition_reports"]},
            {"matched"},
        )
        self.assertEqual(len(proposal["triggered_policies"]), 1)
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-work-order-condition-audit",
        )
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-CONDITION-EVALUATOR-01", atom_ids)
        self.assertFalse((POLICY_CONDITION_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_task_start_projects_real_chain_policy_missing_evidence_and_feedback(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Real Chain Policy Probe",
                "--project-root",
                str(POLICY_REAL_CHAIN_PROJECT),
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
        proposal = json.loads(completed.stdout)
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
        self.assertEqual(
            proposal["policy_context"]["policy_condition_eval_status"],
            "checked",
        )
        self.assertEqual(len(proposal["triggered_policies"]), 1)
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-real-test-data-and-chain",
        )
        self.assertEqual(
            proposal["required_actions"][0]["action_type"],
            "verify_real_test_data_and_real_chain",
        )
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "missing")
        self.assertEqual(
            proposal["missing_evidence_reports"][0]["missing"][0]["required_type"],
            "real_test_data_and_chain_evidence",
        )
        feedback_by_type = {
            item["feedback_type"]: item for item in proposal["policy_feedback_options"]
        }
        self.assertEqual(
            set(feedback_by_type),
            {"not_applicable", "defer", "needs_scope_narrowing"},
        )
        self.assertEqual(
            feedback_by_type["defer"]["missing_evidence_types"],
            ["real_test_data_and_chain_evidence"],
        )
        self.assertEqual(feedback_by_type["defer"]["missing_evidence_count"], 1)
        self.assertFalse(
            (POLICY_REAL_CHAIN_PROJECT / ".jikuo" / "task_sessions").exists()
        )

    def test_task_start_projects_real_chain_policy_ok_with_inline_evidence(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Real Chain Evidence Probe",
                "--project-root",
                str(POLICY_REAL_CHAIN_PROJECT),
                "--task-type",
                "work_order_delivery",
                "--jikuo-layer",
                "testing_governance",
                "--changed-path",
                "tools/jikuo/policy_store_tests.py",
                "--produced-evidence-id",
                "EVD-real-chain-agent-flow",
                "--produced-evidence-type",
                "real_test_data_and_chain_evidence",
                "--produced-evidence-action-type",
                "verify_real_test_data_and_real_chain",
                "--produced-evidence-summary",
                "agent_flow used concrete fixture data through the policy evaluator path",
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
        self.assertEqual(proposal["policy_context"]["policy_store_status"], "active")
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-real-test-data-and-chain",
        )
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "ok")
        self.assertEqual(
            proposal["evidence_status"][0]["evidence_refs"],
            ["EVD-real-chain-agent-flow"],
        )
        self.assertEqual(proposal["missing_evidence_reports"], [])
        self.assertEqual(
            {item["feedback_type"] for item in proposal["policy_feedback_options"]},
            {"not_applicable", "defer", "needs_scope_narrowing"},
        )
        self.assertFalse(
            (POLICY_REAL_CHAIN_PROJECT / ".jikuo" / "task_sessions").exists()
        )

    def test_task_start_projects_pre_code_change_classification_policy(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Pre Code Classification Probe",
                "--project-root",
                str(POLICY_REAL_CHAIN_PROJECT),
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
        proposal = json.loads(completed.stdout)
        self.assertEqual(len(proposal["triggered_policies"]), 1)
        self.assertEqual(
            proposal["triggered_policies"][0]["policy_ref"],
            "POLICY-pre-code-change-layer-classification",
        )
        self.assertEqual(
            proposal["required_actions"][0]["action_type"],
            "classify_governance_vs_implementation_before_code_change",
        )
        self.assertEqual(proposal["evidence_status"][0]["current_status"], "missing")
        self.assertEqual(
            proposal["missing_evidence_reports"][0]["missing"][0]["required_type"],
            "governance_vs_implementation_classification_evidence",
        )
        self.assertEqual(
            {item["feedback_type"] for item in proposal["policy_feedback_options"]},
            {"not_applicable", "defer", "needs_scope_narrowing"},
        )
        self.assertFalse(
            (POLICY_REAL_CHAIN_PROJECT / ".jikuo" / "task_sessions").exists()
        )

    def test_policy_write_plan_projects_no_write_card(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_write_plan",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--policy-title",
                "Three-phase task audit",
                "--policy-source-ref",
                "<exact user phrase as spoken>",
                "--policy-task-type",
                "work_order_delivery",
                "--policy-jikuo-layer",
                "configurable_rule_kernel",
                "--policy-changed-path-pattern",
                "docs/jikuo/**",
                "--project-root",
                str(READY_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "policy_write_plan",
        )
        self.assertEqual(proposal["cards"][0]["card_kind"], "policy_write_plan")
        plan = proposal["cards"][0]["policy_write_plan"]
        self.assertEqual(plan["schema"], "jikuo.policy_write_plan.v0")
        self.assertEqual(plan["status"], "review")
        self.assertEqual(plan["policy_ref"], "POLICY-three-phase-audit")
        self.assertEqual(len(plan["proposed_policy"]["conditions"]), 3)
        self.assertEqual(
            plan["write_set"][0]["path"],
            ".jikuo/policies/approved/POLICY-three-phase-audit.yaml",
        )
        command = proposal["cards"][0]["command_proposal"]
        self.assertTrue(command["approval_required"])
        self.assertTrue(command["technical_confirmation_required"])
        self.assertIn("python -B -m jikuo.policy_store", command["command_preview"])
        self.assertNotIn("tools/jikuo", command["command_preview"])
        self.assertIn("write-policy", command["command_preview"])
        self.assertIn("--confirm-write-policy", command["command_preview"])
        self.assertIn("--approval-phrase", command["command_preview"])
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-STORE-WRITE-PROPOSE-01", atom_ids)
        self.assertFalse((READY_PROJECT / ".jikuo" / "policies").exists())

    def test_starter_policy_pack_init_projects_agent_flow_apply_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "starter_project"
            project_root.mkdir()
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "initialize_jikuo",
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
            self.assertFalse(proposal["write_effect"]["writes_performed"])
            self.assertTrue(proposal["approval_boundary"]["guarded_apply_available"])
            self.assertEqual(
                proposal["trigger_decision"]["invocation_scenario"],
                "starter_policy_pack_init",
            )
            card = proposal["cards"][0]
            self.assertEqual(card["card_kind"], "starter_policy_pack_init_plan")
            plan = card["starter_policy_pack_init_plan"]
            self.assertEqual(plan["schema"], "jikuo.starter_policy_pack_init_plan.v0")
            self.assertTrue(plan["would_create_project_state"])
            self.assertEqual(len(plan["starter_policies"]), 4)
            command = card["command_proposal"]["command_preview"]
            self.assertIn("python -B -m jikuo.agent_flow", command)
            self.assertIn("apply", command)
            self.assertIn("--operation \"starter_policy_pack_init\"", command)
            self.assertIn("--confirm-apply", command)
            self.assertNotIn("tools/jikuo", command)
            self.assertFalse((project_root / ".jikuo").exists())

    def test_policy_evolution_plan_projects_refinement_without_write(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_evolution_plan",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--policy-evolution-operation",
                "refine_policy",
                "--feedback-type",
                "needs_scope_narrowing",
                "--summary",
                "Triggered for a task that should not require this review.",
                "--policy-source-ref",
                "<exact user phrase as spoken>",
                "--project-root",
                str(POLICY_ACTIVE_PROJECT),
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
        self.assertFalse(proposal["write_effect"]["writes_performed"])
        self.assertEqual(
            proposal["trigger_decision"]["invocation_scenario"],
            "policy_evolution_plan",
        )
        self.assertEqual(proposal["cards"][0]["card_kind"], "policy_evolution_plan")
        plan = proposal["cards"][0]["policy_evolution_plan"]
        self.assertEqual(plan["schema"], "jikuo.policy_evolution_plan.v0")
        self.assertEqual(plan["status"], "review")
        self.assertEqual(plan["target_policy_ref"], "POLICY-three-phase-audit")
        self.assertFalse(plan["writes_performed"])
        self.assertFalse(plan["future_write_boundary"]["writer_implemented"])
        atom_ids = {trace["atom_id"] for trace in proposal["atom_trace"]}
        self.assertIn("CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01", atom_ids)

    def test_policy_evolution_plan_projects_deprecation_command(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_evolution_plan",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--policy-evolution-operation",
                "deprecate_policy",
                "--feedback-type",
                "not_applicable",
                "--summary",
                "Policy should stop triggering for this project.",
                "--policy-source-ref",
                "User asked to preview deprecating the three-phase audit policy for this project.",
                "--project-root",
                str(POLICY_ACTIVE_PROJECT),
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
        self.assertIn(
            "review policy evolution recommendation and any generated guarded command before approving a write",
            proposal["next_actions"],
        )
        card = proposal["cards"][0]
        self.assertEqual(card["card_kind"], "policy_evolution_plan")
        command = card["command_proposal"]
        self.assertTrue(command["approval_required"])
        self.assertTrue(command["technical_confirmation_required"])
        self.assertIn("python -B -m jikuo.policy_store", command["command_preview"])
        self.assertNotIn("tools/jikuo", command["command_preview"])
        self.assertIn("write-evolution", command["command_preview"])
        self.assertIn("--confirm-write-evolution", command["command_preview"])
        self.assertIn(".jikuo/policies/manifest.yaml", command["writes_if_approved"])

    def test_policy_evolution_plan_projects_supersession_command(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "policy_evolution_plan",
                "--policy-ref",
                "POLICY-three-phase-audit",
                "--policy-evolution-operation",
                "supersede_policy",
                "--feedback-type",
                "needs_scope_narrowing",
                "--summary",
                "Policy should be replaced with narrower conditions.",
                "--policy-source-ref",
                "User asked to preview replacing the broad three-phase audit policy with a narrower v2 policy.",
                "--replacement-policy-ref",
                "POLICY-three-phase-audit-v2",
                "--replacement-title",
                "Three-phase task audit v2",
                "--replacement-task-type",
                "work_order_delivery",
                "--replacement-jikuo-layer",
                "testing_governance",
                "--replacement-changed-path-pattern",
                "docs/jikuo/**",
                "--project-root",
                str(POLICY_ACTIVE_PROJECT),
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
        card = proposal["cards"][0]
        self.assertEqual(card["card_kind"], "policy_evolution_plan")
        plan = card["policy_evolution_plan"]
        self.assertEqual(plan["operation"], "supersede_policy")
        self.assertEqual(plan["replacement_policy_ref"], "POLICY-three-phase-audit-v2")
        self.assertTrue(plan["future_write_boundary"]["writer_implemented"])
        self.assertIn(
            ".jikuo/policies/approved/POLICY-three-phase-audit-v2.yaml",
            {item["path"] for item in plan["write_set"]},
        )
        command = card["command_proposal"]
        self.assertTrue(command["approval_required"])
        self.assertTrue(command["technical_confirmation_required"])
        self.assertIn("python -B -m jikuo.policy_store", command["command_preview"])
        self.assertNotIn("tools/jikuo", command["command_preview"])
        self.assertIn("write-evolution", command["command_preview"])
        self.assertIn("--operation \"supersede_policy\"", command["command_preview"])
        self.assertIn("--replacement-policy-id \"POLICY-three-phase-audit-v2\"", command["command_preview"])
        self.assertIn("--replacement-title \"Three-phase task audit v2\"", command["command_preview"])
        self.assertIn("--confirm-write-evolution", command["command_preview"])
        self.assertIn(
            ".jikuo/policies/approved/POLICY-three-phase-audit-v2.yaml",
            command["writes_if_approved"],
        )
        self.assertIn(".jikuo/policies/manifest.yaml", command["writes_if_approved"])


if __name__ == "__main__":
    unittest.main()
