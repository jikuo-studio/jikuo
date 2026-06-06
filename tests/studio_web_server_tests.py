import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo.integrations.studio_web import server  # noqa: E402
from jikuo.studio import project_files  # noqa: E402


def write_project_context(root: Path) -> None:
    jikuo = root / ".jikuo"
    jikuo.mkdir(parents=True, exist_ok=True)
    (jikuo / "project_context.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.project_context.v0"',
                "document_roles:",
                "  project_context:",
                '    path: ".jikuo/project_context.yaml"',
                "    required: true",
                '    note: "Project context."',
                "main_document_mounts:",
                '  canonical_path_root: "."',
                '  path_policy: "standalone_repo_paths_only"',
                "  active_mount_authority:",
                '    - ".jikuo/project_context.yaml"',
                "  checked_before_slice_completion:",
                '    - path: ".jikuo/project_context.yaml"',
                '      update_required_when: "document rules change"',
                "  unchanged_report_required: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_project_state(root: Path) -> None:
    jikuo = root / ".jikuo"
    jikuo.mkdir(parents=True, exist_ok=True)
    (jikuo / "project_state.yaml").write_text(
        "\n".join(
            [
                'schema: "jikuo.project_local_state.v0"',
                'project_id: "studio_web_fixture"',
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


def touch(root: Path, rel: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {path.name}\n", encoding="utf-8")


def write_active_policy(root: Path, policy_id: str) -> Path:
    path = root / ".jikuo" / "policies" / "approved" / f"{policy_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                f'policy_id: "{policy_id}"',
                "version: 1",
                'status: "active_report_only"',
                'title: "Studio template publication fixture"',
                'scenario_package: "engineering_governance"',
                "source_refs:",
                '  - type: "test_fixture"',
                f'    ref: "tests:{policy_id}"',
                "triggers:",
                '  - trigger_id: "TRG-conversation-turn"',
                '    type: "task_lifecycle_event"',
                '    event: "conversation_turn"',
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
    return path


def write_policy_store_with_candidate_proposal(
    root: Path,
    *,
    active_policy_id: str = "POLICY-studio-active-fixture",
    candidate_policy_id: str = "POLICY-studio-candidate-fixture",
    proposal_id: str = "POLICYPROPOSAL-studio-candidate-fixture",
) -> dict[str, str]:
    write_project_state(root)
    active_path = write_active_policy(root, active_policy_id)
    store = root / ".jikuo" / "policies"
    proposals = store / "proposals"
    proposals.mkdir(parents=True, exist_ok=True)
    proposal_ref = f".jikuo/policies/proposals/{proposal_id}.yaml"
    decision_ref = ".jikuo/policies/decisions/POLICYDECISION-studio-candidate-fixture.yaml"
    policy_ref = f".jikuo/policies/approved/{candidate_policy_id}.yaml"
    (proposals / f"{proposal_id}.yaml").write_text(
        "\n".join(
            [
                'schema: "jikuo.policy_write_plan.v0"',
                'schema_version: "jikuo.policy_write_plan.v0"',
                "report_only: true",
                'plan_id: "POLICYWRITEPLAN-studio-candidate-fixture"',
                'operation: "append_policy"',
                'status: "review"',
                f'proposal_ref: "{proposal_ref}"',
                f'policy_ref: "{candidate_policy_id}"',
                f'project_root: "{root}"',
                'policy_store_status: "active"',
                f'policy_store_root: "{store}"',
                "write_set:",
                f'  - path: "{policy_ref}"',
                '    effect: "create approved policy file"',
                '    operation: "create"',
                f'  - path: "{decision_ref}"',
                '    effect: "create policy decision record"',
                '    operation: "create"',
                '  - path: ".jikuo/policies/manifest.yaml"',
                '    effect: "create or update policy-store manifest active_policy_refs"',
                '    operation: "create_or_update"',
                f'  - path: "{proposal_ref}"',
                '    effect: "create policy write proposal snapshot"',
                '    operation: "create"',
                "proposed_policy:",
                '  schema_version: "jikuo.configurable_rule_policy.v0"',
                f'  policy_id: "{candidate_policy_id}"',
                "  version: 1",
                '  status: "active_report_only"',
                '  title: "Studio candidate activation fixture"',
                '  scenario_package: "engineering_governance"',
                "  source_refs:",
                '    - type: "test_fixture"',
                '      ref: "tests:studio_candidate_activation"',
                "  triggers:",
                '    - trigger_id: "TRG-conversation-turn"',
                '      type: "task_lifecycle_event"',
                '      event: "conversation_turn"',
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
                "refusal_reasons: []",
                "warnings: []",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "studio_web_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                f'  - policy_id: "{active_policy_id}"',
                "    version: 1",
                f'    path: "{active_path.relative_to(root).as_posix()}"',
                "proposal_refs:",
                f'  - proposal_id: "{proposal_id}"',
                f'    policy_id: "{candidate_policy_id}"',
                f'    path: "{proposal_ref}"',
                '    status: "candidate"',
                "deprecated_policy_refs: []",
                "superseded_policy_refs: []",
                'last_updated_at: "2026-06-04T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "proposal_id": proposal_id,
        "proposal_ref": proposal_ref,
        "policy_id": candidate_policy_id,
        "policy_ref": policy_ref,
        "decision_ref": decision_ref,
    }


class StudioWebServerTests(unittest.TestCase):
    def test_api_payloads_are_read_only_status_views(self):
        status_code, status = server.api_payload_for_path("/api/status", project_root=ROOT)
        panels_code, panels = server.api_payload_for_path("/api/panels", project_root=ROOT)
        actions_code, actions = server.api_payload_for_path("/api/actions", project_root=ROOT)
        files_code, files = server.api_payload_for_path("/api/project-files", project_root=ROOT)
        policy_code, policy_status = server.api_payload_for_path(
            "/api/policy-management/status",
            project_root=ROOT,
        )
        health_code, health = server.api_payload_for_path("/api/health", project_root=ROOT)

        self.assertEqual(status_code, 200)
        self.assertEqual(panels_code, 200)
        self.assertEqual(actions_code, 200)
        self.assertEqual(files_code, 200)
        self.assertEqual(policy_code, 200)
        self.assertEqual(health_code, 200)
        self.assertEqual(status["schema"], "jikuo.studio.global_status.v0")
        self.assertIn("artifact_assurance", status["summaries"])
        self.assertIn("artifact_assurance", status["summaries"]["runtime"])
        self.assertEqual(panels["schema"], "jikuo.studio.panel_registry.v0")
        self.assertEqual(actions["schema"], "jikuo.studio.action_registry.v0")
        self.assertEqual(files["schema"], "jikuo.studio.project_file_inventory.v0")
        self.assertEqual(policy_status["schema"], "jikuo.policy_management_status.v0")
        self.assertIn("active_policies", policy_status["policy_store"])
        self.assertIn("active_policy_details", policy_status["policy_store"])
        self.assertIn("proposal_refs", policy_status["policy_store"])
        self.assertIn("activatable_policy_proposals", policy_status["policy_store"])
        self.assertIn("option_sets", policy_status)
        self.assertIn("policy_scopes", policy_status["option_sets"])
        self.assertIn("editing", policy_status["option_sets"]["policy_scopes"])
        self.assertIn("lifecycle_events", policy_status["option_sets"])
        self.assertIn("completion_review", policy_status["option_sets"]["lifecycle_events"])
        self.assertIn("available_operations", policy_status)
        self.assertEqual(health["schema"], server.STUDIO_WEB_SCHEMA)
        self.assertFalse(status["writes_performed"])
        self.assertFalse(panels["writes_performed"])
        self.assertFalse(actions["writes_performed"])
        self.assertFalse(files["writes_performed"])
        self.assertFalse(policy_status["writes_performed"])
        self.assertFalse(health["writes_performed"])

    def test_project_file_inventory_skips_files_that_disappear_during_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            vanished = project_root / "docs" / "vanished.md"

            with patch.object(
                project_files,
                "iter_project_document_files",
                return_value=[vanished],
            ):
                inventory = project_files.build_project_file_inventory(
                    project_root=project_root,
                )

            self.assertEqual(inventory["status"], "degraded")
            self.assertEqual(inventory["item_count"], 0)
            self.assertEqual(inventory["total_candidate_count"], 1)
            self.assertEqual(inventory["skipped_during_scan_count"], 1)
            self.assertEqual(inventory["items"], [])
            self.assertIn(
                "project_file_disappeared_during_scan",
                {item.get("code") for item in inventory["warnings"]},
            )

    def test_document_rules_plan_api_returns_no_write_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/customer-guide.md")

            status_code, plan = server.api_document_rules_plan_payload(
                {
                    "add_context_docs": ["docs/customer-guide.md"],
                    "add_completion_checks": ["docs/customer-guide.md"],
                    "add_governance_references": ["docs/customer-guide.md"],
                    "completion_update_rule": "customer guide changes",
                    "selection_records": [
                        {
                            "path": "docs/customer-guide.md",
                            "selected_at_utc": "2026-06-02T00:00:00Z",
                        }
                    ],
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(plan["schema"], "jikuo.studio.document_rules_update_plan.v0")
            self.assertEqual(plan["status"], "review")
            self.assertEqual(plan["change_count"], 3)
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(plan["write_allowed_by_command"])
            self.assertEqual(plan["studio_web"]["route"], "/api/document-rules/plan")
            self.assertEqual(
                plan["studio_web"]["selection_records"][0]["selected_at_utc"],
                "2026-06-02T00:00:00Z",
            )

    def test_document_rules_plan_api_surfaces_refused_validation_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)

            status_code, plan = server.api_document_rules_plan_payload(
                {"add_context_docs": ["../outside.md"]},
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(plan["status"], "refused")
            self.assertFalse(plan["writes_performed"])
            self.assertIn(
                "path_outside_project_root",
                {item["code"] for item in plan["validation"]["errors"]},
            )

    def test_policy_evolution_plan_api_returns_no_write_plan(self):
        status_code, plan = server.api_policy_evolution_plan_payload(
            {
                "policy_ref": "POLICY-jikuo-data-model-drift-alarm",
                "policy_evolution_operation": "deprecate_policy",
                "feedback_type": "needs_scope_narrowing",
                "summary": "Studio preview test",
                "replacement_work_profile_policy_scopes": ["editing"],
                "replacement_work_profile_lifecycle_events": [],
            },
            project_root=ROOT,
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(plan["schema"], "jikuo.policy_evolution_plan.v0")
        self.assertEqual(plan["status"], "review")
        self.assertEqual(plan["operation"], "deprecate_policy")
        self.assertEqual(plan["target_policy_ref"], "POLICY-jikuo-data-model-drift-alarm")
        self.assertFalse(plan["writes_performed"])
        self.assertFalse(plan["write_allowed_by_command"])
        self.assertEqual(plan["proposed_trigger_profile"]["trigger_mode"], "scope_first")
        self.assertEqual(plan["proposed_trigger_profile"]["policy_scopes"], ["editing"])
        self.assertEqual(plan["proposed_trigger_profile"]["lifecycle_events"], [])
        self.assertEqual(
            plan["studio_web"]["route"],
            "/api/policy-management/evolution/plan",
        )
        self.assertEqual(plan["studio_web"]["write_mode"], "no-write-plan")

    def test_policy_evolution_apply_api_refuses_without_approval(self):
        status_code, result = server.api_policy_evolution_apply_payload(
            {
                "policy_ref": "POLICY-jikuo-data-model-drift-alarm",
                "policy_evolution_operation": "deprecate_policy",
                "feedback_type": "needs_scope_narrowing",
                "summary": "Studio apply refusal test",
            },
            project_root=ROOT,
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(result["schema"], "jikuo.policy_write_result.v0")
        self.assertEqual(result["status"], "refused")
        self.assertFalse(result["write_performed"])
        self.assertIn("missing_confirmation_flag", result["refusal_reasons"])
        self.assertIn("approval_evidence_missing", result["refusal_reasons"])
        self.assertEqual(
            result["studio_web"]["route"],
            "/api/policy-management/evolution/apply",
        )
        self.assertFalse(result["studio_web"]["writes_performed"])

    def test_policy_evolution_apply_api_writes_temp_policy_store_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            shutil.copytree(ROOT / ".jikuo" / "policies", project_root / ".jikuo" / "policies")
            request_payload = {
                "policy_ref": "POLICY-jikuo-data-model-drift-alarm",
                "policy_evolution_operation": "deprecate_policy",
                "feedback_type": "needs_scope_narrowing",
                "summary": "Studio guarded apply temp policy-store test",
            }
            _plan_code, plan = server.api_policy_evolution_plan_payload(
                request_payload,
                project_root=project_root,
            )

            status_code, result = server.api_policy_evolution_apply_payload(
                {
                    **request_payload,
                    "proposal_ref": plan["proposal_ref"],
                    "confirm_apply": True,
                    "approval_phrase": "Approve Policy Evolution write",
                    "approval_source": "studio_confirmation_dialog",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["studio_web"]["write_mode"], "guarded")
            self.assertTrue(result["studio_web"]["writes_performed"])
            self.assertIn(".jikuo/policies/manifest.yaml", result["written_paths"])
            self.assertTrue((project_root / result["proposal_ref"]).is_file())
            self.assertTrue((project_root / result["decision_record_ref"]).is_file())

    def test_policy_evolution_apply_api_refines_trigger_profile_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            shutil.copytree(ROOT / ".jikuo" / "policies", project_root / ".jikuo" / "policies")
            request_payload = {
                "policy_ref": "POLICY-jikuo-data-model-drift-alarm",
                "policy_evolution_operation": "refine_policy",
                "feedback_type": "needs_scope_narrowing",
                "summary": "Studio guarded refine temp policy-store test",
                "replacement_trigger_event": "conversation_turn",
                "replacement_work_profile_policy_scopes": ["editing"],
                "replacement_work_profile_lifecycle_events": [],
                "replacement_changed_path_pattern": "src/jikuo/**",
            }
            _plan_code, plan = server.api_policy_evolution_plan_payload(
                request_payload,
                project_root=project_root,
            )

            status_code, result = server.api_policy_evolution_apply_payload(
                {
                    **request_payload,
                    "proposal_ref": plan["proposal_ref"],
                    "confirm_apply": True,
                    "approval_phrase": "Approve Policy Evolution write",
                    "approval_source": "studio_confirmation_dialog",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["operation"], "refine_policy")
            self.assertTrue(result["post_write_verification"]["target_policy_refined"])
            self.assertIn(
                ".jikuo/policies/approved/POLICY-jikuo-data-model-drift-alarm.yaml",
                result["written_paths"],
            )
            policy_text = (
                project_root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-jikuo-data-model-drift-alarm.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn('pattern: "src/jikuo/**"', policy_text)

    def test_policy_final_response_gate_uses_evolution_plan_and_apply_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_state(project_root)
            policy_id = "POLICY-studio-final-response-gate"
            policy_path = write_active_policy(project_root, policy_id)
            store = project_root / ".jikuo" / "policies"
            (store / "manifest.yaml").write_text(
                "\n".join(
                    [
                        'schema_version: "jikuo.policy_store_manifest.v0"',
                        'project_id: "studio_web_fixture"',
                        'store_root: ".jikuo/policies"',
                        "active_policy_refs:",
                        f'  - policy_id: "{policy_id}"',
                        "    version: 1",
                        f'    path: "{policy_path.relative_to(project_root).as_posix()}"',
                        "proposal_refs: []",
                        "deprecated_policy_refs: []",
                        "superseded_policy_refs: []",
                        'last_updated_at: "2026-06-05T00:00:00Z"',
                        "compatibility:",
                        '  unknown_fields: "preserve"',
                        '  writer: "test_fixture"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            status_code, refused = server.api_policy_final_response_gate_apply_payload(
                {
                    "policy_ref": policy_id,
                    "enabled": True,
                },
                project_root=project_root,
            )
            _status_code, policy_status = server.api_payload_for_path(
                "/api/policy-management/status",
                project_root=project_root,
            )
            detail = policy_status["policy_store"]["active_policy_details"][0]
            request_payload = {
                "policy_ref": policy_id,
                "policy_evolution_operation": "update_final_response_gate",
                "policy_path": detail["path"],
                "enabled": True,
                "reviewed_policy_sha256": detail["policy_sha256"],
            }

            plan_code, plan = server.api_policy_evolution_plan_payload(
                request_payload,
                project_root=project_root,
            )
            stale_code, stale = server.api_policy_evolution_apply_payload(
                {
                    **request_payload,
                    "plan_id": "stale-plan-id",
                    "confirm_apply": True,
                    "approval_phrase": "Approve Policy Final Response Gate update",
                    "approval_source": "studio_confirmation_dialog",
                },
                project_root=project_root,
            )
            approved_code, result = server.api_policy_evolution_apply_payload(
                {
                    **request_payload,
                    "plan_id": plan["plan_id"],
                    "confirm_apply": True,
                    "approval_phrase": "Approve Policy Final Response Gate update",
                    "approval_source": "studio_confirmation_dialog",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(refused["status"], "refused")
            self.assertFalse(refused["write_performed"])
            self.assertIn("missing_confirmation_flag", refused["refusal_reasons"])
            self.assertIn("approval_evidence_missing", refused["refusal_reasons"])
            self.assertEqual(plan_code, 200)
            self.assertEqual(plan["schema"], "jikuo.policy_final_response_gate_plan.v0")
            self.assertEqual(plan["status"], "review")
            self.assertEqual(plan["operation"], "update_final_response_gate")
            self.assertEqual(
                plan["studio_web"]["route"],
                "/api/policy-management/evolution/plan",
            )
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(plan["write_allowed_by_command"])
            self.assertEqual(plan["target_policy_ref"], policy_id)
            self.assertEqual(plan["target_policy_sha256"], detail["policy_sha256"])
            self.assertFalse(plan["current_final_response_gate"]["enabled"])
            self.assertTrue(plan["proposed_final_response_gate"]["enabled"])
            self.assertEqual(
                plan["approval_phrase"],
                "Approve Policy Final Response Gate update",
            )
            self.assertEqual(
                plan["future_write_boundary"]["writer_route"],
                "/api/policy-management/evolution/apply",
            )
            self.assertEqual(
                plan["write_set"][0]["path"],
                ".jikuo/policies/approved/POLICY-studio-final-response-gate.yaml",
            )
            self.assertEqual(stale_code, 200)
            self.assertEqual(stale["status"], "refused")
            self.assertIn(
                "reviewed_plan_id_does_not_match_current_request",
                stale["refusal_reasons"],
            )
            self.assertFalse(stale["writes_performed"])
            self.assertEqual(
                stale["studio_web"]["route"],
                "/api/policy-management/evolution/apply",
            )
            self.assertEqual(approved_code, 200)
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["policy_ref"], policy_id)
            self.assertTrue(result["final_response_gate"]["enabled"])
            self.assertEqual(
                result["studio_web"]["route"],
                "/api/policy-management/evolution/apply",
            )
            self.assertTrue(result["studio_web"]["writes_performed"])
            self.assertEqual(result["studio_web"]["reviewed_plan_id"], plan["plan_id"])
            self.assertIn(
                ".jikuo/policies/approved/POLICY-studio-final-response-gate.yaml",
                result["written_paths"],
            )
            self.assertIn(
                "final_response_gate: true",
                policy_path.read_text(encoding="utf-8"),
            )

            _status_code, updated_status = server.api_payload_for_path(
                "/api/policy-management/status",
                project_root=project_root,
            )
            updated_detail = updated_status["policy_store"]["active_policy_details"][0]
            self.assertTrue(updated_detail["final_response_gate"]["enabled"])
            self.assertEqual(
                updated_detail["final_response_gate"]["visibility"],
                "final_response_required",
            )

    def test_policy_template_publication_plan_api_returns_no_write_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            policy_id = "POLICY-studio-template-publication-fixture"
            write_active_policy(project_root, policy_id)

            status_code, plan = server.api_policy_template_publication_plan_payload(
                {
                    "policy_ref": policy_id,
                    "distribution_decision": "optional_template",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(plan["schema"], "jikuo.policy_template_publication_plan.v0")
            self.assertEqual(plan["status"], "review")
            self.assertEqual(plan["policy_id"], policy_id)
            self.assertEqual(plan["distribution_decision"], "optional_template")
            self.assertTrue(plan["target_template_path"])
            self.assertEqual(len(plan["write_set"]), 1)
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(plan["write_allowed_by_command"])
            self.assertEqual(
                plan["studio_web"]["route"],
                "/api/policy-management/template-publication/plan",
            )
            self.assertEqual(plan["studio_web"]["write_mode"], "no-write-plan")

    def test_policy_template_publication_apply_api_refuses_review_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            policy_id = "POLICY-studio-template-publication-mismatch"
            write_active_policy(project_root, policy_id)

            status_code, result = server.api_policy_template_publication_apply_payload(
                {
                    "policy_ref": policy_id,
                    "distribution_decision": "optional_template",
                    "reviewed_source_policy_sha256": "not-the-current-source",
                    "confirm_apply": True,
                    "approval_phrase": "Approve Policy Template publication",
                    "approval_source": "studio_confirmation_dialog",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(result["schema"], "jikuo.policy_template_publication_result.v0")
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertIn(
                "reviewed_source_policy_sha256_does_not_match_current_source",
                ";".join(result["refusal_reasons"]),
            )
            self.assertEqual(
                result["studio_web"]["route"],
                "/api/policy-management/template-publication/apply",
            )
            self.assertFalse(result["studio_web"]["writes_performed"])

    def test_policy_template_activation_plan_api_returns_no_write_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            template_path = (
                ROOT
                / "src"
                / "jikuo"
                / "policy_templates"
                / "engineering_governance"
                / "POLICYTEMPLATE-local-policy-jikuo-data-model-drift-alarm.yaml"
            )

            status_code, plan = server.api_policy_template_activation_plan_payload(
                {"template_path": str(template_path)},
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(plan["schema"], "jikuo.policy_template_import_plan.v0")
            self.assertEqual(plan["status"], "review")
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(plan["write_allowed_by_command"])
            self.assertEqual(
                plan["resolved_policy_preview"]["policy_id"],
                "POLICY-jikuo-data-model-drift-alarm",
            )
            self.assertEqual(len(plan["write_set"]), 4)
            self.assertEqual(
                plan["studio_web"]["route"],
                "/api/policy-management/template-activation/plan",
            )
            self.assertEqual(plan["studio_web"]["write_mode"], "no-write-plan")

    def test_policy_template_activation_plan_api_refuses_paths_outside_package_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            outside = project_root / "template.yaml"
            outside.write_text("schema_version: nope\n", encoding="utf-8")

            status_code, plan = server.api_policy_template_activation_plan_payload(
                {"template_path": str(outside)},
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(plan["schema"], "jikuo.policy_template_import_plan.v0")
            self.assertEqual(plan["status"], "refused")
            self.assertIn(
                "template_path_outside_package_policy_templates",
                plan["refusal_reasons"][0],
            )
            self.assertFalse(plan["writes_performed"])

    def test_policy_template_activation_apply_api_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            template_path = (
                ROOT
                / "src"
                / "jikuo"
                / "policy_templates"
                / "engineering_governance"
                / "POLICYTEMPLATE-local-policy-jikuo-data-model-drift-alarm.yaml"
            )

            status_code, result = server.api_policy_template_activation_apply_payload(
                {"template_path": str(template_path)},
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(result["schema"], "jikuo.policy_template_activation_result.v0")
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertIn("missing_confirmation_flag", result["refusal_reasons"])
            self.assertIn("approval_evidence_missing", result["refusal_reasons"])
            self.assertEqual(
                result["studio_web"]["route"],
                "/api/policy-management/template-activation/apply",
            )

    def test_policy_template_activation_apply_api_writes_temp_policy_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            template_path = (
                ROOT
                / "src"
                / "jikuo"
                / "policy_templates"
                / "engineering_governance"
                / "POLICYTEMPLATE-local-policy-jikuo-data-model-drift-alarm.yaml"
            )
            _plan_code, plan = server.api_policy_template_activation_plan_payload(
                {"template_path": str(template_path)},
                project_root=project_root,
            )

            status_code, result = server.api_policy_template_activation_apply_payload(
                {
                    "template_path": str(template_path),
                    "plan_id": plan["plan_id"],
                    "confirm_apply": True,
                    "approval_phrase": "Approve Policy Template activation",
                    "approval_source": "studio_confirmation_dialog",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["studio_web"]["write_mode"], "guarded")
            self.assertTrue(result["studio_web"]["writes_performed"])
            self.assertEqual(
                result["policy_ref"],
                "POLICY-jikuo-data-model-drift-alarm",
            )
            self.assertTrue(result["post_write_verification"]["policy_active"])
            self.assertIn(".jikuo/policies/manifest.yaml", result["written_paths"])
            self.assertTrue((project_root / result["proposal_ref"]).is_file())
            self.assertTrue(
                (
                    project_root
                    / ".jikuo"
                    / "policies"
                    / "approved"
                    / "POLICY-jikuo-data-model-drift-alarm.yaml"
                ).is_file()
            )

    def test_policy_starter_init_plan_api_is_no_write_for_fresh_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            status_code, plan = server.api_policy_starter_init_plan_payload(
                {"pack_id": "engineering_governance"},
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(plan["schema"], "jikuo.starter_policy_pack_init_plan.v0")
            self.assertEqual(plan["status"], "review")
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(plan["write_allowed_by_command"])
            self.assertEqual(plan["studio_web"]["write_mode"], "no-write-plan")
            self.assertEqual(
                plan["studio_web"]["route"],
                "/api/policy-management/starter-init/plan",
            )
            self.assertEqual(len(plan["starter_policies"]), 4)
            self.assertTrue(plan["would_create_registry"])
            self.assertTrue(plan["would_create_project_state"])
            self.assertFalse((project_root / ".jikuo").exists())

    def test_policy_starter_init_apply_api_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            status_code, result = server.api_policy_starter_init_apply_payload(
                {"pack_id": "engineering_governance"},
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(result["schema"], "jikuo.starter_policy_pack_init_result.v0")
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertFalse(result["studio_web"]["writes_performed"])
            self.assertIn("missing_confirmation_flag", result["refusal_reasons"])
            self.assertIn("approval_evidence_missing", result["refusal_reasons"])
            self.assertFalse((project_root / ".jikuo").exists())

    def test_policy_starter_init_apply_api_writes_and_exposes_active_policies(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            _plan_status, plan = server.api_policy_starter_init_plan_payload(
                {"pack_id": "engineering_governance"},
                project_root=project_root,
            )

            status_code, result = server.api_policy_starter_init_apply_payload(
                {
                    "pack_id": "engineering_governance",
                    "plan_id": plan["plan_id"],
                    "confirm_apply": True,
                    "approval_phrase": "Approve Starter Policy Pack activation",
                    "approval_source": "studio_confirmation_dialog",
                },
                project_root=project_root,
            )
            _status_code, policy_status = server.api_payload_for_path(
                "/api/policy-management/status",
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertTrue(result["studio_web"]["writes_performed"])
            self.assertEqual(result["studio_web"]["write_mode"], "guarded")
            self.assertTrue(result["post_write_verification"]["starter_policies_active"])
            self.assertIn(".jikuo/policies/manifest.yaml", result["written_paths"])
            self.assertTrue((project_root / ".jikuo" / "policies" / "manifest.yaml").is_file())
            self.assertEqual(
                policy_status["policy_store"]["active_policy_count"],
                4,
            )
            self.assertEqual(
                policy_status["summary_counts"]["active_policy_count"],
                4,
            )

    def test_policy_candidate_activation_plan_api_returns_existing_proposal_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            fixture = write_policy_store_with_candidate_proposal(project_root)

            status_code, plan = server.api_policy_candidate_activation_plan_payload(
                {"proposal_id": fixture["proposal_id"]},
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(
                plan["schema"],
                "jikuo.policy_proposal_activation_plan.v0",
            )
            self.assertEqual(plan["status"], "review")
            self.assertEqual(plan["policy_ref"], fixture["policy_id"])
            self.assertEqual(plan["proposal_ref"], fixture["proposal_ref"])
            self.assertEqual(len(plan["read_set"]), 1)
            self.assertEqual(len(plan["write_set"]), 3)
            self.assertTrue(plan["guarded_apply_available"])
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(plan["write_allowed_by_command"])
            self.assertEqual(
                plan["studio_web"]["route"],
                "/api/policy-management/candidate-activation/plan",
            )

    def test_policy_candidate_activation_apply_api_writes_existing_proposal_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            fixture = write_policy_store_with_candidate_proposal(project_root)
            _plan_code, plan = server.api_policy_candidate_activation_plan_payload(
                {"proposal_id": fixture["proposal_id"]},
                project_root=project_root,
            )

            refused_code, refused = server.api_policy_candidate_activation_apply_payload(
                {"proposal_id": fixture["proposal_id"]},
                project_root=project_root,
            )
            status_code, result = server.api_policy_candidate_activation_apply_payload(
                {
                    "proposal_id": fixture["proposal_id"],
                    "reviewed_proposal_sha256": plan["proposal_sha256"],
                    "confirm_apply": True,
                    "approval_phrase": "Approve Policy Candidate activation",
                    "approval_source": "studio_confirmation_dialog",
                },
                project_root=project_root,
            )

            self.assertEqual(refused_code, 200)
            self.assertEqual(refused["status"], "refused")
            self.assertFalse(refused["write_performed"])
            self.assertIn("missing_confirmation_flag", refused["refusal_reasons"])
            self.assertEqual(status_code, 200)
            self.assertEqual(result["schema"], "jikuo.policy_write_result.v0")
            self.assertEqual(result["status"], "written")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["policy_ref"], fixture["policy_id"])
            self.assertEqual(result["proposal_ref"], fixture["proposal_ref"])
            self.assertEqual(result["studio_web"]["write_mode"], "guarded")
            self.assertTrue(result["studio_web"]["writes_performed"])
            self.assertEqual(
                result["written_paths"],
                [
                    fixture["policy_ref"],
                    fixture["decision_ref"],
                    ".jikuo/policies/manifest.yaml",
                ],
            )
            self.assertTrue((project_root / fixture["proposal_ref"]).is_file())
            self.assertTrue((project_root / fixture["policy_ref"]).is_file())
            self.assertTrue((project_root / fixture["decision_ref"]).is_file())
            manifest_text = (
                project_root / ".jikuo" / "policies" / "manifest.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn(f'policy_id: "{fixture["policy_id"]}"', manifest_text)
            self.assertTrue(result["post_write_verification"]["active_policy_resolvable"])
            self.assertTrue(result["post_write_verification"]["proposal_snapshot_existing"])

            _second_plan_code, second_plan = server.api_policy_candidate_activation_plan_payload(
                {"proposal_id": fixture["proposal_id"]},
                project_root=project_root,
            )
            self.assertEqual(second_plan["status"], "refused")
            self.assertIn("target_policy_already_active", second_plan["refusal_reasons"])

    def test_policy_template_activation_apply_api_rejects_stale_plan_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            template_path = (
                ROOT
                / "src"
                / "jikuo"
                / "policy_templates"
                / "engineering_governance"
                / "POLICYTEMPLATE-local-policy-jikuo-data-model-drift-alarm.yaml"
            )

            status_code, result = server.api_policy_template_activation_apply_payload(
                {
                    "template_path": str(template_path),
                    "plan_id": "POLICYTEMPLATEIMPORT-stale",
                    "confirm_apply": True,
                    "approval_phrase": "Approve Policy Template activation",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertIn(
                "reviewed_plan_id_does_not_match_current_request",
                result["refusal_reasons"],
            )

    def test_policy_evolution_plan_api_rejects_non_object_requests(self):
        status_code, plan = server.api_policy_evolution_plan_payload(
            ["not", "an", "object"],
            project_root=ROOT,
        )

        self.assertEqual(status_code, 400)
        self.assertEqual(plan["status"], "invalid_request")
        self.assertFalse(plan["writes_performed"])

    def test_policy_evolution_apply_api_rejects_non_object_requests(self):
        status_code, result = server.api_policy_evolution_apply_payload(
            ["not", "an", "object"],
            project_root=ROOT,
        )

        self.assertEqual(status_code, 400)
        self.assertEqual(result["status"], "invalid_request")
        self.assertFalse(result["writes_performed"])

    def test_index_html_is_no_write_control_shell_with_document_rules_preview(self):
        html = server.render_index_html()

        self.assertIn("data-jikuo-studio=\"guarded-control-shell\"", html)
        self.assertIn("JIKUO Studio", html)
        self.assertIn("/api/status", html)
        self.assertIn("/api/project-files", html)
        self.assertIn("/api/document-rules/plan", html)
        self.assertIn("/api/document-rules/apply", html)
        self.assertIn("Document Rules", html)
        self.assertIn("Trace", html)
        self.assertIn("Policy Trace", html)
        self.assertIn("policy-trace-status", html)
        self.assertIn("policy-trace-round-select", html)
        self.assertIn("policy-trace-lifecycle", html)
        self.assertIn("renderPolicyTrace", html)
        self.assertIn("missingClassificationSummary", html)
        self.assertIn("missingClassificationRows", html)
        self.assertIn("Missing classification", html)
        self.assertIn("missing_evidence_classification", html)
        self.assertIn("selectedPolicyTraceId", html)
        self.assertIn("retained_traces", html)
        self.assertIn("policyTraceRoundLabel", html)
        self.assertIn("No policy trace rounds captured", html)
        self.assertIn("Selected lifecycle", html)
        self.assertIn("Document Trace", html)
        self.assertIn("Round Document Trace", html)
        self.assertIn("Configuration", html)
        self.assertIn("First-run readiness", html)
        self.assertIn("first-run-status", html)
        self.assertIn("renderFirstRun", html)
        self.assertIn("Policy Configuration", html)
        self.assertIn("Document Configuration", html)
        self.assertIn("/api/policy-management/status", html)
        self.assertIn("/api/policy-management/evolution/plan", html)
        self.assertIn("/api/policy-management/evolution/apply", html)
        self.assertIn("/api/policy-management/template-activation/plan", html)
        self.assertIn("/api/policy-management/template-activation/apply", html)
        self.assertIn("policy-management-status", html)
        self.assertIn("policy-management-metrics", html)
        self.assertIn("Starter policy pack activation", html)
        self.assertIn("policy-starter-init-pack", html)
        self.assertIn("policy-starter-init-selected-summary", html)
        self.assertIn("policy-starter-init-selected-tags", html)
        self.assertIn("policy-starter-init-selected-config", html)
        self.assertIn("policy-starter-init-preview-button", html)
        self.assertIn("policy-starter-init-apply-button", html)
        self.assertIn("policy-starter-init-plan-result", html)
        self.assertIn("POLICY_STARTER_INIT_APPROVAL_PHRASE", html)
        self.assertIn("previewPolicyStarterInitPlan", html)
        self.assertIn("applyPolicyStarterInitPlan", html)
        self.assertIn("/api/policy-management/starter-init/plan", html)
        self.assertIn("/api/policy-management/starter-init/apply", html)
        self.assertIn("Activate this starter policy pack?", html)
        self.assertIn("report-only baseline policies", html)
        self.assertIn("Change active policy configuration", html)
        self.assertIn("Preview the configuration change plan", html)
        self.assertNotIn("Policy evolution preview", html)
        self.assertIn("policy-evolution-operation", html)
        self.assertIn("policy-evolution-policy", html)
        self.assertIn("policy-selected-summary", html)
        self.assertIn("policy-selected-config", html)
        self.assertIn("policy-selected-trigger-tags", html)
        self.assertIn("policy-evolution-trigger-mode", html)
        self.assertIn("policy-evolution-scope-options", html)
        self.assertIn("policy-evolution-lifecycle-options", html)
        self.assertIn("policy-evolution-replacement-ref", html)
        self.assertIn("policy-trigger-mode-note", html)
        self.assertIn("updatePolicyTriggerModeAffordance", html)
        self.assertIn("selectedPolicyTriggerProfile", html)
        self.assertIn("currentDeclared", html)
        self.assertIn(".option-pill.ignored", html)
        self.assertIn("policy-evolution-preview-button", html)
        self.assertIn("policy-evolution-apply-button", html)
        self.assertIn("POLICY_EVOLUTION_APPROVAL_PHRASE", html)
        self.assertIn("POLICY_FINAL_RESPONSE_GATE_APPROVAL_PHRASE", html)
        self.assertIn("currentPolicyEvolutionPlan", html)
        self.assertIn("currentPolicyEvolutionRequest", html)
        self.assertIn("proposal_ref: currentPolicyEvolutionPlan.proposal_ref", html)
        self.assertIn("plan_id: currentPolicyEvolutionPlan.plan_id", html)
        self.assertIn("policy-evolution-plan-result", html)
        self.assertIn("policy-final-response-gate-toggle", html)
        self.assertNotIn("/api/policy-management/final-response-gate/apply", html)
        self.assertIn('<option value="update_final_response_gate">Update final-response gate</option>', html)
        self.assertIn("policy-final-response-gate-fields", html)
        self.assertNotIn("policyFinalResponseGatePlanFromRequest", html)
        self.assertIn("current_final_response_gate", html)
        self.assertIn("proposed_final_response_gate", html)
        self.assertIn("Require in final response", html)
        self.assertNotIn("policy-final-response-gate-apply-button", html)
        self.assertNotIn("Save gate setting", html)
        self.assertNotIn("applyPolicyFinalResponseGateChange", html)
        self.assertLess(
            html.index("Proposed change"),
            html.index("policy-final-response-gate-toggle"),
        )
        self.assertLess(
            html.index("policy-final-response-gate-toggle"),
            html.index("policy-evolution-plan-result"),
        )
        self.assertIn("policy-editor-grid", html)
        self.assertIn("policy-editor-note", html)
        self.assertIn("policy-action-buttons", html)
        self.assertIn("Make active policy reusable", html)
        self.assertIn("policy-template-publication-policy", html)
        self.assertIn("policy-template-publication-decision", html)
        self.assertIn("policy-template-publication-preview-button", html)
        self.assertIn("policy-template-publication-apply-button", html)
        self.assertIn("policy-template-publication-plan-result", html)
        self.assertIn("POLICY_TEMPLATE_PUBLICATION_APPROVAL_PHRASE", html)
        self.assertIn("previewPolicyTemplatePublicationPlan", html)
        self.assertIn("applyPolicyTemplatePublicationPlan", html)
        self.assertIn("/api/policy-management/template-publication/plan", html)
        self.assertIn("/api/policy-management/template-publication/apply", html)
        self.assertIn("Publish reusable template", html)
        self.assertIn("Template activation preview", html)
        self.assertIn("policy-template-activation-template", html)
        self.assertIn("policy-template-selected-summary", html)
        self.assertIn("policy-template-selected-tags", html)
        self.assertIn("policy-template-selected-config", html)
        self.assertIn("policy-template-activation-preview-button", html)
        self.assertIn("policy-template-activation-apply-button", html)
        self.assertIn("policy-template-activation-plan-result", html)
        self.assertIn("POLICY_TEMPLATE_ACTIVATION_APPROVAL_PHRASE", html)
        self.assertIn("currentPolicyTemplateActivationPlan", html)
        self.assertIn("previewPolicyTemplateActivationPlan", html)
        self.assertIn("applyPolicyTemplateActivationPlan", html)
        self.assertIn("renderPolicyTemplateActivationPlan", html)
        self.assertIn("Apply guarded activation", html)
        self.assertIn("Policy-store records/files to write", html)
        self.assertIn("It does not execute policy actions", html)
        self.assertIn("Activatable policy proposals", html)
        self.assertIn("policy-candidate-activation-proposal", html)
        self.assertIn("policy-candidate-activation-preview-button", html)
        self.assertIn("policy-candidate-activation-apply-button", html)
        self.assertIn("policy-candidate-activation-plan-result", html)
        self.assertIn("Apply pending policy", html)
        self.assertIn("POLICY_CANDIDATE_ACTIVATION_APPROVAL_PHRASE", html)
        self.assertIn("previewPolicyCandidateActivationPlan", html)
        self.assertIn("applyPolicyCandidateActivationPlan", html)
        self.assertIn("/api/policy-management/candidate-activation/plan", html)
        self.assertIn("/api/policy-management/candidate-activation/apply", html)
        self.assertIn("It does not rewrite the proposal snapshot", html)
        self.assertNotIn("Projected writes", html)
        self.assertIn("@media (max-width: 1180px)", html)
        self.assertIn("Status reason", html)
        self.assertIn("Apply readiness", html)
        self.assertIn("Approval boundary", html)
        self.assertIn("Apply next step", html)
        self.assertNotIn("policy-evolution-replacement-trigger", html)
        self.assertIn("policy-active-list", html)
        self.assertIn("policy-candidate-list", html)
        self.assertIn("policy-template-list", html)
        self.assertIn("policy-starter-pack-list", html)
        self.assertIn("policy-operation-list", html)
        self.assertIn("policy-limitation-list", html)
        self.assertIn("scope-first", html)
        self.assertIn("Current project constraints that can affect AI work", html)
        self.assertIn("Pending constraints that are ready for user review", html)
        self.assertIn("renderPolicyManagement", html)
        self.assertIn("proposalDetailsById", html)
        self.assertIn("activatable_policy_proposals", html)
        self.assertIn("Write set", html)
        self.assertIn("Review the pending constraint before guarded activation", html)
        self.assertIn("previewPolicyEvolutionPlan", html)
        self.assertIn("renderPolicyEvolutionPlan", html)
        self.assertIn("loadPolicyManagement", html)
        self.assertIn("Select a runtime round to inspect expected documents", html)
        self.assertIn("round-trace-round-select", html)
        self.assertIn("round-trace-round-overview", html)
        self.assertNotIn("round-select-modified", html)
        self.assertIn("round-option-modified", html)
        self.assertIn("roundOptionLabel", html)
        self.assertIn("roundTurnAnchorLabel", html)
        self.assertIn("turn_anchor=unavailable", html)
        self.assertIn('compactItem("Turn anchor"', html)
        self.assertIn("roundHasActualWrites", html)
        self.assertIn("No document changes", html)
        self.assertIn("round.has_document_changes", html)
        self.assertIn("Expected documents", html)
        self.assertIn("Observed evidence", html)
        self.assertIn("Gaps", html)
        self.assertIn("Unchecked applicability", html)
        self.assertNotIn("Action chain", html)
        self.assertNotIn("round-trace-rounds", html)
        self.assertNotIn("round-trace-summary", html)
        self.assertIn("round-trace-expected", html)
        self.assertIn("round-trace-observed", html)
        self.assertIn("round-trace-gaps", html)
        self.assertIn("trace-group", html)
        self.assertIn("compact-expander", html)
        self.assertIn("compact-toggle", html)
        self.assertIn("traceGroup", html)
        self.assertIn("setExpanded", html)
        self.assertIn("Show hidden ${label}", html)
        self.assertIn("Read obligations", html)
        self.assertIn("Runtime source", html)
        self.assertIn("Write gaps", html)
        self.assertIn("No comparable trace", html)
        self.assertNotIn("round-trace-timeline", html)
        self.assertIn("No comparable trace was captured", html)
        self.assertIn("Selected round", html)
        self.assertIn("Semantic intent", html)
        self.assertIn("Latest Semantic Classification", html)
        self.assertIn("semantic-evidence-list", html)
        self.assertIn("Classified by", html)
        self.assertIn("Classification round", html)
        self.assertIn("Host AI supplied semantic intent", html)
        self.assertIn("Turn anchor", html)
        self.assertIn("semanticAnchorOverviewValue", html)
        self.assertIn("semanticAnchor.anchor_id", html)
        self.assertIn("evidence_source_kind", html)
        self.assertIn("turn_anchor_not_supplied_by_host_adapter", html)
        self.assertIn("prompt_digest_status", html)
        self.assertIn("Evidence imperfections", html)
        self.assertIn("Latest semantic classification", html)
        self.assertIn("semantic_intent_evidence", html)
        self.assertIn("semantic_intent_coverage", html)
        self.assertIn("selectedSemantic.coverage_status", html)
        self.assertIn("traceList.default_round_id", html)
        self.assertNotIn("latest_completion_receipt_round_id", html)
        self.assertIn("const selectedCounts = (selectedRound || {}).counts || {}", html)
        self.assertIn("const active = selectedTraceAvailable ? activeTrace : {}", html)
        self.assertNotIn("latestAvailable", html)
        self.assertNotIn("roundSelect.classList.toggle", html)
        self.assertIn("const artifactCount = (items, ...counts)", html)
        self.assertIn("Actual write source", html)
        self.assertIn("Git observation", html)
        self.assertIn("Git-observed actual writes", html)
        self.assertIn("No git-observed actual write evidence was supplied", html)
        self.assertIn("Declared actual writes", html)
        self.assertIn("Required companion writes", html)
        self.assertIn("Declared writes", html)
        self.assertIn("required / ${numberValue(counts.declared_write_count", html)
        self.assertIn("required companion write", html)
        self.assertIn("Companion projection", html)
        self.assertIn("companion write trigger", html)
        self.assertIn("ignored actual write", html)
        self.assertIn("companion_ignored_item_count", html)
        self.assertIn("trigger ${record.trigger.type", html)
        self.assertIn("record.source_kind", html)
        self.assertIn("Detailed item paths are not available in this history card", html)
        self.assertIn("Detailed gap categories are not available in this history card", html)
        self.assertIn('compactItem("Gaps"', html)
        self.assertNotIn('traceChip("Gaps"', html)
        self.assertNotIn("artifact-assurance-metrics", html)
        self.assertIn("Current Document Rules", html)
        self.assertIn("Each column is one Document Rules purpose", html)
        self.assertIn("Context documents", html)
        self.assertIn("Source: document roles", html)
        self.assertIn("Completion checks", html)
        self.assertIn("Source: completion-check rules", html)
        self.assertIn("Governance references", html)
        self.assertIn("Source: rule-source references", html)
        self.assertIn("User guide", html)
        self.assertIn("document-rules-user-docs", html)
        self.assertIn("First-run documentation for defaults", html)
        self.assertIn("User docs", html)
        self.assertIn("mounts.user_docs", html)
        self.assertIn("default_configuration", html)
        self.assertIn("Add files to Document Rules", html)
        self.assertIn("Candidate local files", html)
        self.assertIn("In Document Rules", html)
        self.assertIn("Not in Document Rules", html)
        self.assertIn("Context document", html)
        self.assertIn("Completion check", html)
        self.assertIn("Governance reference", html)
        self.assertNotIn("document-mounts-completion", html)
        self.assertNotIn("document-mounts-editable-sources", html)
        self.assertNotIn("document-mounts-guidance-sources", html)
        self.assertIn("document-rules-form", html)
        self.assertIn("document-rules-file-list", html)
        self.assertIn("document-rules-selected-files", html)
        self.assertIn("document-rules-clear-selection", html)
        self.assertIn("Preview plan", html)
        self.assertIn("document-rules-apply-note", html)
        self.assertIn("Approve and apply", html)
        self.assertIn("window.confirm", html)
        self.assertIn("Approve Document Rules update", html)
        self.assertIn("studio_confirmation_dialog", html)
        self.assertNotIn("document-rules-approval-phrase", html)
        self.assertNotIn('name="approval_phrase"', html)
        self.assertNotIn("<h2>Panels</h2>", html)
        self.assertNotIn('id="panels"', html)
        self.assertNotIn('document.getElementById("panels")', html)
        self.assertIn("Available Actions", html)
        self.assertNotIn("Mount authority and pending write boundary", html)
        self.assertNotIn("Current rule sources", html)

    def test_http_server_serves_index_and_json_endpoints(self):
        httpd = server.create_server(host="127.0.0.1", port=0, project_root=ROOT)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = httpd.server_address
            base_url = f"http://{host}:{port}"

            with urlopen(f"{base_url}/", timeout=10) as response:
                html = response.read().decode("utf-8")
            with urlopen(f"{base_url}/api/status", timeout=10) as response:
                status = json.loads(response.read().decode("utf-8"))
            with urlopen(f"{base_url}/api/panels", timeout=10) as response:
                panels = json.loads(response.read().decode("utf-8"))
            with urlopen(f"{base_url}/api/actions", timeout=10) as response:
                actions = json.loads(response.read().decode("utf-8"))
            with urlopen(f"{base_url}/api/project-files", timeout=10) as response:
                files = json.loads(response.read().decode("utf-8"))
            with urlopen(
                f"{base_url}/api/policy-management/status",
                timeout=10,
            ) as response:
                policy_status = json.loads(response.read().decode("utf-8"))

            self.assertIn("JIKUO Studio", html)
            self.assertIn("Document Rules", html)
            self.assertIn("Policy Trace", html)
            self.assertIn("Document Trace", html)
            self.assertIn("First-run readiness", html)
            self.assertIn("Policy Configuration", html)
            self.assertIn("Document Configuration", html)
            self.assertEqual(status["schema"], "jikuo.studio.global_status.v0")
            self.assertIn("first_run", status["summaries"]["configuration"])
            self.assertIn("document_mounts", status["summaries"])
            self.assertIn("artifact_assurance", status["summaries"])
            self.assertIn("policy_trace", status["summaries"]["runtime"])
            self.assertIn("artifact_assurance", status["summaries"]["runtime"])
            terms = {
                item["term_id"]: item
                for item in status["summaries"]["document_mounts"]["configuration_terms"]
            }
            self.assertIn("rule_sources", terms)
            self.assertIn("editable_configuration", terms)
            self.assertIn("governance_guidance", terms)
            self.assertTrue(
                status["summaries"]["document_mounts"]["editable_configuration_sources"]
            )
            self.assertTrue(
                status["summaries"]["document_mounts"]["governance_guidance_sources"]
            )
            self.assertEqual(panels["schema"], "jikuo.studio.panel_registry.v0")
            self.assertEqual(actions["schema"], "jikuo.studio.action_registry.v0")
            self.assertEqual(files["schema"], "jikuo.studio.project_file_inventory.v0")
            self.assertEqual(policy_status["schema"], "jikuo.policy_management_status.v0")
            self.assertIn("package_templates", policy_status)
            self.assertFalse(files["writes_performed"])
            self.assertFalse(policy_status["writes_performed"])
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=10)

    def test_http_server_accepts_document_rules_plan_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/customer-guide.md")
            httpd = server.create_server(host="127.0.0.1", port=0, project_root=project_root)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = httpd.server_address
                payload = json.dumps(
                    {"add_context_docs": ["docs/customer-guide.md"]}
                ).encode("utf-8")
                request = Request(
                    f"http://{host}:{port}/api/document-rules/plan",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(request, timeout=10) as response:
                    plan = json.loads(response.read().decode("utf-8"))

                self.assertEqual(plan["schema"], "jikuo.studio.document_rules_update_plan.v0")
                self.assertEqual(plan["status"], "review")
                self.assertFalse(plan["writes_performed"])
            finally:
                httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=10)

    def test_http_server_accepts_policy_evolution_plan_post(self):
        httpd = server.create_server(host="127.0.0.1", port=0, project_root=ROOT)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = httpd.server_address
            payload = json.dumps(
                {
                    "policy_ref": "POLICY-jikuo-data-model-drift-alarm",
                    "policy_evolution_operation": "deprecate_policy",
                }
            ).encode("utf-8")
            request = Request(
                f"http://{host}:{port}/api/policy-management/evolution/plan",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=10) as response:
                plan = json.loads(response.read().decode("utf-8"))

            self.assertEqual(plan["schema"], "jikuo.policy_evolution_plan.v0")
            self.assertEqual(plan["status"], "review")
            self.assertFalse(plan["writes_performed"])
            self.assertEqual(
                plan["studio_web"]["route"],
                "/api/policy-management/evolution/plan",
            )
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=10)

    def test_http_server_accepts_policy_evolution_apply_post_refusal(self):
        httpd = server.create_server(host="127.0.0.1", port=0, project_root=ROOT)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = httpd.server_address
            payload = json.dumps(
                {
                    "policy_ref": "POLICY-jikuo-data-model-drift-alarm",
                    "policy_evolution_operation": "deprecate_policy",
                }
            ).encode("utf-8")
            request = Request(
                f"http://{host}:{port}/api/policy-management/evolution/apply",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))

            self.assertEqual(result["schema"], "jikuo.policy_write_result.v0")
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertEqual(
                result["studio_web"]["route"],
                "/api/policy-management/evolution/apply",
            )
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=10)

    def test_http_server_accepts_policy_template_activation_plan_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            template_path = (
                ROOT
                / "src"
                / "jikuo"
                / "policy_templates"
                / "engineering_governance"
                / "POLICYTEMPLATE-local-policy-jikuo-data-model-drift-alarm.yaml"
            )
            httpd = server.create_server(host="127.0.0.1", port=0, project_root=project_root)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = httpd.server_address
                payload = json.dumps(
                    {"template_path": str(template_path)}
                ).encode("utf-8")
                request = Request(
                    f"http://{host}:{port}/api/policy-management/template-activation/plan",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(request, timeout=10) as response:
                    plan = json.loads(response.read().decode("utf-8"))

                self.assertEqual(plan["schema"], "jikuo.policy_template_import_plan.v0")
                self.assertEqual(plan["status"], "review")
                self.assertFalse(plan["writes_performed"])
                self.assertEqual(
                    plan["studio_web"]["route"],
                    "/api/policy-management/template-activation/plan",
                )
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=10)

    def test_document_rules_apply_api_refuses_then_applies_reviewed_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/customer-guide.md")
            status_code, plan = server.api_document_rules_plan_payload(
                {"add_context_docs": ["customer_guide=docs/customer-guide.md"]},
                project_root=project_root,
            )

            refused_code, refused = server.api_document_rules_apply_payload(
                {"plan": plan, "confirm_apply": False},
                project_root=project_root,
            )
            applied_code, applied = server.api_document_rules_apply_payload(
                {
                    "plan": plan,
                    "confirm_apply": True,
                    "approval_phrase": "Approve Document Rules update",
                },
                project_root=project_root,
            )

            self.assertEqual(status_code, 200)
            self.assertEqual(refused_code, 200)
            self.assertEqual(refused["status"], "refused")
            self.assertFalse(refused["write_performed"])
            self.assertEqual(applied_code, 200)
            self.assertEqual(applied["status"], "applied")
            self.assertTrue(applied["write_performed"])
            self.assertEqual(applied["studio_web"]["route"], "/api/document-rules/apply")
            context, errors = server.document_rules.load_project_context(project_root)
            self.assertEqual(errors, [])
            self.assertEqual(
                context["document_roles"]["customer_guide"]["path"],
                "docs/customer-guide.md",
            )

    def test_http_server_returns_structured_not_found(self):
        httpd = server.create_server(host="127.0.0.1", port=0, project_root=ROOT)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = httpd.server_address
            with self.assertRaises(HTTPError) as caught:
                urlopen(f"http://{host}:{port}/missing", timeout=10)
            self.assertEqual(caught.exception.code, 404)
            try:
                payload = json.loads(caught.exception.read().decode("utf-8"))
            finally:
                caught.exception.close()
            self.assertEqual(payload["status"], "not_found")
            self.assertFalse(payload["writes_performed"])
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=10)

    def test_root_cli_exposes_studio_serve_help_without_starting_server(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "jikuo",
                "studio",
                "--help",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("serve", completed.stdout)
        self.assertIn("--host", completed.stdout)
        self.assertIn("--port", completed.stdout)


if __name__ == "__main__":
    unittest.main()
