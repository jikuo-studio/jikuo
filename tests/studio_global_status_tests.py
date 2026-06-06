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
        self.assertIn("document_mounts", report["summaries"])
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
        self.assertIn("studio.document_mounts.review", action_ids)
        self.assertIn("studio.document_mounts.plan_update", action_ids)
        self.assertIn("studio.policy_management.status", action_ids)
        self.assertIn("studio.policy_evolution.plan", action_ids)
        self.assertIn("studio.runtime.open_latest_card", action_ids)

    def test_global_status_exposes_first_run_configuration_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = global_status.build_global_status(project_root=project_root)

            first_run = report["summaries"]["configuration"]["first_run"]
            self.assertEqual(
                first_run["schema"],
                "jikuo.first_run_configuration_status.v0",
            )
            self.assertEqual(first_run["status"], "needs_configuration")
            self.assertFalse(first_run["user_usable"])
            self.assertEqual(first_run["blocker_count"], 3)
            diagnostic_codes = {item["code"] for item in report["diagnostics"]}
            self.assertIn("first_run_configuration_incomplete", diagnostic_codes)
            markdown = global_status.format_markdown(report)
            self.assertIn("First run: `needs_configuration`", markdown)

    def test_runtime_summary_exposes_latest_task_artifact_assurance(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            runtime_root = project_root / ".jikuo" / "runtime"
            runtime_root.mkdir(parents=True)
            (project_root / ".jikuo" / "project_context.yaml").write_text(
                "\n".join(
                    [
                        'schema_version: "jikuo.project_context.v0"',
                        "document_roles: {}",
                        "main_document_mounts:",
                        '  canonical_path_root: "."',
                        "  active_mount_authority: []",
                        "  checked_before_slice_completion: []",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (runtime_root / "state_summary.json").write_text(
                json.dumps(
                    {
                        "schema": "jikuo.runtime_state_summary.v0",
                        "status": "available",
                        "semantic_intent_coverage": {
                            "schema": "jikuo.semantic_intent_coverage.v0",
                            "coverage_status": "missing",
                            "semantic_intent_status": "unavailable",
                            "evidence_status": "missing",
                            "provider": "unavailable",
                            "required": True,
                            "policy_scopes": ["editing"],
                            "fallback_expanded": False,
                            "gap_reason": "host_ai_did_not_return_intent",
                        },
                        "turn_anchor": {
                            "schema": "jikuo.turn_anchor.v0",
                            "status": "available",
                            "anchor_id": "turn_status_fixture",
                            "source_kind": "host_adapter",
                            "client_id": "codex",
                            "client_event": "UserPromptSubmit",
                            "session_id": "session-status",
                            "turn_id": "turn-status",
                            "received_at_utc": "2026-06-05T00:00:00Z",
                            "prompt_sha256": "0" * 64,
                            "prompt_digest_status": "hash_only",
                            "natural_key_basis": [
                                "received_at_utc",
                                "client_id",
                                "session_id",
                                "turn_id",
                                "prompt_sha256",
                            ],
                            "identity_strength": "host_turn_id_plus_prompt_hash",
                        },
                        "artifact_assurance": {
                            "schema": "jikuo.studio.artifact_assurance.v0",
                            "status": "review",
                            "read_assurance": {"required_read_count": 2},
                            "write_assurance": {"planned_write_count": 1},
                            "gap_report": {"gap_count": 1},
                        },
                    }
                ),
                encoding="utf-8",
            )

            report = global_status.build_global_status(project_root=project_root)

            runtime = report["summaries"]["runtime"]
            self.assertEqual(runtime["artifact_assurance"]["status"], "review")
            self.assertEqual(
                runtime["semantic_intent_coverage"]["coverage_status"],
                "missing",
            )
            self.assertEqual(runtime["turn_anchor"]["status"], "available")
            self.assertEqual(runtime["turn_anchor"]["anchor_id"], "turn_status_fixture")
            semantic_evidence = runtime["semantic_intent_evidence"]
            self.assertEqual(
                semantic_evidence["schema"],
                "jikuo.studio.semantic_intent_evidence.v0",
            )
            self.assertEqual(semantic_evidence["status"], "degraded")
            classification = semantic_evidence["classification"]
            self.assertFalse(classification["ai_classified"])
            self.assertEqual(classification["classification_source"], "missing")
            self.assertEqual(classification["intent_class"], "unknown")
            self.assertEqual(
                semantic_evidence["latest_round"]["source_kind"],
                "latest_runtime_state",
            )
            self.assertGreaterEqual(semantic_evidence["imperfection_count"], 1)
            self.assertEqual(
                semantic_evidence["turn_anchor"]["anchor_id"],
                "turn_status_fixture",
            )
            diagnostic_codes = {item["code"] for item in report["diagnostics"]}
            self.assertIn("runtime_semantic_intent_coverage_degraded", diagnostic_codes)
            self.assertEqual(
                runtime["artifact_assurance"]["write_assurance"]["planned_write_count"],
                1,
            )

    def test_semantic_evidence_exposes_runtime_inherited_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            runtime_root = project_root / ".jikuo" / "runtime"
            runtime_root.mkdir(parents=True)
            (project_root / ".jikuo" / "project_context.yaml").write_text(
                "\n".join(
                    [
                        'schema_version: "jikuo.project_context.v0"',
                        "document_roles: {}",
                        "main_document_mounts:",
                        '  canonical_path_root: "."',
                        "  active_mount_authority: []",
                        "  checked_before_slice_completion: []",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (runtime_root / "state_summary.json").write_text(
                json.dumps(
                    {
                        "schema": "jikuo.runtime_state_summary.v0",
                        "status": "available",
                        "source": {
                            "proposal_id": "proposal_inherited",
                            "status": "review",
                            "event": "completion_review",
                        },
                        "runtime_visibility": {
                            "history_ref": ".jikuo/runtime/history/inherited.md"
                        },
                        "work_profile": {
                            "intent_class": "implementation",
                            "operation_class": "write_file",
                        },
                        "semantic_intent_coverage": {
                            "schema": "jikuo.semantic_intent_coverage.v0",
                            "coverage_status": "complete",
                            "semantic_intent_status": "provided",
                            "evidence_status": "ok",
                            "provider": "host_ai",
                            "evidence_source_kind": "runtime_inherited",
                            "semantic_intent_ref": "sem_fixture",
                            "required": True,
                            "policy_scopes": ["editing"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            report = global_status.build_global_status(project_root=project_root)

            classification = report["summaries"]["runtime"][
                "semantic_intent_evidence"
            ]["classification"]
            self.assertTrue(classification["ai_classified"])
            self.assertEqual(
                classification["classification_source"],
                "runtime_inherited",
            )
            self.assertEqual(
                classification["evidence_source_kind"],
                "runtime_inherited",
            )

    def test_semantic_evidence_uses_retained_available_turn_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            runtime_root = project_root / ".jikuo" / "runtime"
            history_root = runtime_root / "history"
            history_root.mkdir(parents=True)
            (project_root / ".jikuo" / "project_context.yaml").write_text(
                "\n".join(
                    [
                        'schema_version: "jikuo.project_context.v0"',
                        "document_roles: {}",
                        "main_document_mounts:",
                        '  canonical_path_root: "."',
                        "  active_mount_authority: []",
                        "  checked_before_slice_completion: []",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            latest_ref = ".jikuo/runtime/history/20260605T010000Z_latest.md"
            anchored_ref = ".jikuo/runtime/history/20260605T000000Z_anchored.md"
            (project_root / latest_ref).write_text("# Latest\n", encoding="utf-8")
            (project_root / anchored_ref).write_text("# Anchored\n", encoding="utf-8")
            (runtime_root / "state_summary.json").write_text(
                json.dumps(
                    {
                        "schema": "jikuo.runtime_state_summary.v0",
                        "status": "available",
                        "updated_at_utc": "2026-06-05T01:00:00Z",
                        "source": {
                            "proposal_id": "proposal_latest",
                            "status": "review",
                            "event": "conversation_turn",
                        },
                        "runtime_visibility": {"history_ref": latest_ref},
                        "semantic_intent_coverage": {
                            "schema": "jikuo.semantic_intent_coverage.v0",
                            "coverage_status": "complete",
                            "semantic_intent_status": "provided",
                            "evidence_status": "ok",
                            "provider": "host_ai",
                            "required": True,
                            "policy_scopes": ["discussion"],
                        },
                    }
                ),
                encoding="utf-8",
            )
            (project_root / anchored_ref).with_suffix(".json").write_text(
                json.dumps(
                    {
                        "schema": "jikuo.runtime_state_summary.v0",
                        "status": "available",
                        "updated_at_utc": "2026-06-05T00:00:00Z",
                        "source": {
                            "proposal_id": "proposal_anchored",
                            "status": "review",
                            "event": "conversation_turn",
                        },
                        "runtime_visibility": {"history_ref": anchored_ref},
                        "turn_anchor": {
                            "schema": "jikuo.turn_anchor.v0",
                            "status": "available",
                            "anchor_id": "turn_retained_fixture",
                            "source_kind": "host_adapter",
                            "client_id": "codex",
                            "client_event": "UserPromptSubmit",
                            "session_id": "session-retained",
                            "turn_id": "turn-retained",
                            "received_at_utc": "2026-06-05T00:00:00Z",
                            "prompt_digest_status": "hash_only",
                            "prompt_sha256": "1" * 64,
                            "natural_key_basis": [
                                "received_at_utc",
                                "client_id",
                                "session_id",
                                "turn_id",
                                "prompt_sha256",
                            ],
                            "identity_strength": "host_turn_id_plus_prompt_hash",
                        },
                    }
                ),
                encoding="utf-8",
            )

            report = global_status.build_global_status(project_root=project_root)

            semantic_evidence = report["summaries"]["runtime"]["semantic_intent_evidence"]
            self.assertEqual(
                semantic_evidence["latest_runtime_turn_anchor"]["status"],
                "missing",
            )
            self.assertEqual(
                semantic_evidence["turn_anchor"]["anchor_id"],
                "turn_retained_fixture",
            )
            self.assertEqual(
                semantic_evidence["turn_anchor"]["evidence_round_id"],
                Path(anchored_ref).stem,
            )
            self.assertIn(
                "Latest runtime turn anchor missing",
                {item["title"] for item in semantic_evidence["imperfections"]},
            )

    def test_round_trace_derives_semantic_coverage_from_work_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            trace = global_status.round_trace_from_state(
                project_root,
                {
                    "schema": "jikuo.runtime_state_summary.v0",
                    "status": "available",
                    "updated_at_utc": "2026-06-04T00:00:00Z",
                    "source": {
                        "proposal_id": "proposal_semantic",
                        "status": "review",
                        "event": "conversation_turn",
                    },
                    "runtime_visibility": {},
                    "turn_anchor": {
                        "schema": "jikuo.turn_anchor.v0",
                        "status": "available",
                        "anchor_id": "turn_trace_fixture",
                        "source_kind": "host_adapter",
                        "client_id": "codex",
                        "client_event": "UserPromptSubmit",
                        "session_id": "session-trace",
                        "turn_id": "turn-trace",
                        "received_at_utc": "2026-06-05T00:00:00Z",
                        "prompt_digest_status": "not_available",
                        "natural_key_basis": [
                            "received_at_utc",
                            "client_id",
                            "session_id",
                            "turn_id",
                        ],
                        "identity_strength": "host_turn_id",
                    },
                    "policy_runtime_status": {
                        "work_profile": {
                            "intent_class": "implementation",
                            "operation_class": "workspace_edit",
                            "policy_scopes": ["editing"],
                            "fallback_expanded": False,
                            "basis": {
                                "host_semantic_intent": {
                                    "status": "provided",
                                    "provider": "host_ai",
                                    "policy_scopes": ["editing"],
                                }
                            },
                            "semantic_intent_evidence": {
                                "required": True,
                                "status": "ok",
                                "provider": "host_ai",
                                "semantic_intent_status": "provided",
                            },
                        },
                    },
                },
            )

            self.assertIsNotNone(trace)
            self.assertEqual(
                trace["semantic_intent_coverage"]["coverage_status"],
                "complete",
            )
            self.assertEqual(
                trace["semantic_intent_coverage"]["provider"],
                "host_ai",
            )
            self.assertEqual(trace["intent_class"], "implementation")
            self.assertEqual(trace["operation_class"], "workspace_edit")
            self.assertEqual(trace["turn_anchor"]["anchor_id"], "turn_trace_fixture")

    def test_runtime_summary_exposes_policy_trace_by_turn_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            runtime_root = project_root / ".jikuo" / "runtime"
            history_root = runtime_root / "history"
            history_root.mkdir(parents=True)
            anchor = {
                "schema": "jikuo.turn_anchor.v0",
                "status": "available",
                "anchor_id": "turn_policy_trace_fixture",
                "source_kind": "host_adapter",
                "session_id": "session-policy-trace",
                "turn_id": "turn-policy-trace",
            }

            def runtime_state(
                *,
                event: str,
                history_ref: str,
                updated_at_utc: str,
                policy_ref: str,
                turn_anchor: dict[str, object] | None = None,
            ) -> dict[str, object]:
                state_anchor = turn_anchor or anchor
                return {
                    "schema": "jikuo.runtime_state_summary.v0",
                    "status": "available",
                    "updated_at_utc": updated_at_utc,
                    "source": {
                        "proposal_id": f"proposal_{event}",
                        "status": "review",
                        "event": event,
                    },
                    "runtime_visibility": {"history_ref": history_ref},
                    "turn_anchor": state_anchor,
                    "policy_runtime_status": {
                        "schema": "jikuo.policy_runtime_status.v0",
                        "policy_store_status": "active",
                        "policy_eval_status": "evaluated",
                        "policy_condition_eval_status": "checked",
                        "policy_evidence_check_status": "checked",
                        "active_policy_count": 2,
                        "triggered_policy_count": 1,
                        "not_triggered_policy_count": 1,
                        "required_action_count": 1,
                        "evidence_status_count": 1,
                        "missing_evidence_count": 1,
                        "policy_feedback_option_count": 0,
                        "work_profile": {
                            "lifecycle_event": event,
                            "intent_class": "editing",
                            "operation_class": "workspace_edit",
                            "output_class": "change",
                            "policy_scopes": ["editing"],
                            "fallback_expanded": False,
                            "basis": {
                                "host_semantic_intent": {
                                    "status": "provided",
                                    "provider": "host_ai",
                                    "turn_anchor": state_anchor,
                                }
                            },
                        },
                        "triggered_policies": [
                            {
                                "policy_ref": policy_ref,
                                "policy_title": f"{event} policy",
                                "trigger_ref": f"TRG-{event}",
                                "trigger_reason": f"{event} matched",
                                "declared_trigger_event": event,
                                "evaluation_event": event,
                                "condition_status": "matched",
                                "status": "triggered",
                                "confidence": "tool_verified",
                                "work_profile_match": {
                                    "matched_refs": [
                                        f"lifecycle_event:{event}",
                                        "policy_scope:editing",
                                    ],
                                    "summary": "work_profile matched editing",
                                },
                            }
                        ],
                        "required_actions": [
                            {
                                "action_id": f"ACT-{event}",
                                "type": "render_policy_runtime_status_card",
                                "status": "not_started",
                                "approval_required": False,
                            }
                        ],
                        "evidence_status": [
                            {
                                "evidence_id": f"EVD-{event}",
                                "type": "policy_runtime_status_visibility_evidence",
                                "status": "missing",
                                "satisfies_action": f"ACT-{event}",
                                "reason": "fixture missing evidence",
                            }
                        ],
                        "missing_evidence_reports": [
                            {
                                "report_id": f"MER-{event}",
                                "policy_ref": policy_ref,
                                "status": "review_required",
                                "missing_count": 1,
                                "reason": "fixture missing evidence",
                            }
                        ],
                    },
                }

            task_start_ref = ".jikuo/runtime/history/20260606T010000Z_task_start.md"
            conversation_ref = ".jikuo/runtime/history/20260606T000000Z_conversation.md"
            previous_anchor = {
                "schema": "jikuo.turn_anchor.v0",
                "status": "available",
                "anchor_id": "turn_previous_policy_trace_fixture",
                "source_kind": "host_adapter",
                "session_id": "session-policy-trace",
                "turn_id": "turn-policy-trace-previous",
            }
            previous_ref = ".jikuo/runtime/history/20260605T230000Z_previous.md"
            latest_state = runtime_state(
                event="task_start",
                history_ref=task_start_ref,
                updated_at_utc="2026-06-06T01:00:00Z",
                policy_ref="POLICY-task-start-fixture",
            )
            conversation_state = runtime_state(
                event="conversation_turn",
                history_ref=conversation_ref,
                updated_at_utc="2026-06-06T00:00:00Z",
                policy_ref="POLICY-conversation-fixture",
            )
            previous_state = runtime_state(
                event="completion_review",
                history_ref=previous_ref,
                updated_at_utc="2026-06-05T23:00:00Z",
                policy_ref="POLICY-previous-fixture",
                turn_anchor=previous_anchor,
            )
            (runtime_root / "state_summary.json").write_text(
                json.dumps(latest_state),
                encoding="utf-8",
            )
            for rel_ref, state in (
                (task_start_ref, latest_state),
                (conversation_ref, conversation_state),
                (previous_ref, previous_state),
            ):
                card_path = project_root / rel_ref
                card_path.write_text("# Runtime card\n", encoding="utf-8")
                card_path.with_suffix(".json").write_text(
                    json.dumps(state),
                    encoding="utf-8",
                )

            summary = global_status.runtime_summary(project_root, [])
            policy_trace = summary["policy_trace"]

            self.assertEqual(policy_trace["schema"], global_status.POLICY_TRACES_SCHEMA)
            self.assertFalse(policy_trace["writes_performed"])
            self.assertEqual(
                policy_trace["current_turn_anchor"]["anchor_id"],
                "turn_policy_trace_fixture",
            )
            self.assertEqual(policy_trace["triggered_policy_count"], 2)
            self.assertEqual(policy_trace["missing_evidence_count"], 2)
            self.assertEqual(policy_trace["trace_count"], 2)
            self.assertEqual(policy_trace["all_trace_count"], 3)
            self.assertEqual(len(policy_trace["traces"]), 2)
            self.assertEqual(len(policy_trace["retained_traces"]), 3)
            self.assertEqual(
                policy_trace["observed_lifecycle_events"],
                ["conversation_turn", "task_start"],
            )
            self.assertEqual(policy_trace["missing_recommended_events"], ["completion_review"])
            policy_refs = {
                policy["policy_ref"]
                for trace in policy_trace["traces"]
                for policy in trace["triggered_policies"]
            }
            self.assertEqual(
                policy_refs,
                {"POLICY-conversation-fixture", "POLICY-task-start-fixture"},
            )
            retained_policy_refs = {
                policy["policy_ref"]
                for trace in policy_trace["retained_traces"]
                for policy in trace["triggered_policies"]
            }
            self.assertEqual(
                retained_policy_refs,
                {
                    "POLICY-conversation-fixture",
                    "POLICY-task-start-fixture",
                    "POLICY-previous-fixture",
                },
            )

    def test_runtime_summary_exposes_selectable_round_document_traces(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            runtime_root = project_root / ".jikuo" / "runtime"
            history_root = runtime_root / "history"
            history_root.mkdir(parents=True)
            (project_root / ".jikuo" / "project_context.yaml").write_text(
                "\n".join(
                    [
                        'schema_version: "jikuo.project_context.v0"',
                        "document_roles: {}",
                        "main_document_mounts:",
                        '  canonical_path_root: "."',
                        "  active_mount_authority: []",
                        "  checked_before_slice_completion: []",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            latest_ref = ".jikuo/runtime/history/20260602T010000Z_proposal_latest.md"
            older_ref = ".jikuo/runtime/history/20260602T000000Z_proposal_old.md"
            (project_root / latest_ref).write_text(
                "\n".join(
                    [
                        "# JIKUO Agent Flow Proposal",
                        "",
                        "- Status: `review`",
                        "- Proposal id: `proposal_latest`",
                        "",
                        "## Work Profile",
                        "",
                        "- Lifecycle event: `conversation_turn`",
                        "- Intent class: `discussion`",
                        "- Operation class: `no_tool`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (project_root / older_ref).write_text(
                "\n".join(
                    [
                        "# JIKUO Agent Flow Proposal",
                        "",
                        "- Status: `review`",
                        "- Proposal id: `proposal_old`",
                        "",
                        "## Work Profile",
                        "",
                        "- Lifecycle event: `completion_review`",
                        "- Intent class: `editing`",
                        "- Operation class: `write_file`",
                        "",
                        "## Artifact Assurance",
                        "",
                        "- Status: `review`",
                        "- Guarantee: `evidence_comparison_only`",
                        "- Read assurance status: `review`",
                        "- Write assurance status: `review`",
                        "- Required reads: `2`",
                        "- Read evidence: `1`",
                        "- Completion-check documents: `1`",
                        "- Completion-check documents not evaluated: `0`",
                        "- Applicable required writes: `0`",
                        "- Planned writes: `2`",
                        "- Actual writes: `1`",
                        "- Gap count: `1`",
                        "- Required reads without evidence: `1`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (runtime_root / "state_summary.json").write_text(
                json.dumps(
                    {
                        "schema": "jikuo.runtime_state_summary.v0",
                        "status": "available",
                        "updated_at_utc": "2026-06-02T01:00:00Z",
                        "source": {
                            "proposal_id": "proposal_latest",
                            "status": "review",
                            "event": "conversation_turn",
                        },
                        "runtime_visibility": {"history_ref": latest_ref},
                    }
                ),
                encoding="utf-8",
            )

            report = global_status.build_global_status(project_root=project_root)

            traces = report["summaries"]["runtime"]["round_document_traces"]
            self.assertEqual(traces["schema"], global_status.ROUND_DOCUMENT_TRACES_SCHEMA)
            self.assertEqual(traces["default_round_id"], Path(latest_ref).stem)
            self.assertEqual(traces["default_selection"], "latest_round")
            self.assertEqual(traces["newest_round_id"], Path(latest_ref).stem)
            self.assertEqual(traces["latest_runtime_round_id"], Path(latest_ref).stem)
            self.assertEqual(
                traces["latest_completion_receipt_round_id"],
                Path(older_ref).stem,
            )
            self.assertEqual(traces["completion_receipt_status"], "available")
            self.assertGreaterEqual(traces["round_count"], 2)
            latest = traces["rounds"][0]
            older = traces["rounds"][1]
            self.assertEqual(latest["history_ref"], latest_ref)
            self.assertFalse(latest["has_document_trace"])
            self.assertEqual(latest["document_change_status"], "no_trace")
            self.assertEqual(older["history_ref"], older_ref)
            self.assertTrue(older["has_document_trace"])
            self.assertTrue(older["has_document_changes"])
            self.assertEqual(older["counts"]["planned_write_count"], 2)
            self.assertEqual(older["counts"]["actual_write_count"], 1)
            self.assertEqual(older["gap_count"], 1)
            self.assertIn("completion_review", older["selector_label"])
            self.assertIn("1 gaps", older["selector_label"])
            ordered_times = [item["updated_at_utc"] for item in traces["rounds"]]
            self.assertEqual(ordered_times, sorted(ordered_times, reverse=True))

    def test_history_state_summary_preserves_itemized_round_trace_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            runtime_root = project_root / ".jikuo" / "runtime"
            history_root = runtime_root / "history"
            history_root.mkdir(parents=True)
            (project_root / ".jikuo" / "project_context.yaml").write_text(
                "\n".join(
                    [
                        'schema_version: "jikuo.project_context.v0"',
                        "document_roles: {}",
                        "main_document_mounts:",
                        '  canonical_path_root: "."',
                        "  active_mount_authority: []",
                        "  checked_before_slice_completion: []",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            latest_ref = ".jikuo/runtime/history/20260602T010000Z_proposal_latest.md"
            receipt_ref = ".jikuo/runtime/history/20260602T000000Z_proposal_receipt.md"
            (project_root / latest_ref).write_text(
                "\n".join(
                    [
                        "# JIKUO Agent Flow Proposal",
                        "",
                        "- Status: `review`",
                        "- Proposal id: `proposal_latest`",
                        "",
                        "## Work Profile",
                        "",
                        "- Lifecycle event: `conversation_turn`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (project_root / receipt_ref).write_text(
                "\n".join(
                    [
                        "# JIKUO Agent Flow Proposal",
                        "",
                        "- Status: `review`",
                        "- Proposal id: `proposal_receipt`",
                        "",
                        "## Work Profile",
                        "",
                        "- Lifecycle event: `completion_review`",
                        "",
                        "## Artifact Assurance",
                        "",
                        "- Status: `review`",
                        "- Required companion writes: `1`",
                        "- Actual writes: `6`",
                        "- Gap count: `0`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            actual_writes = [
                {"path": f"docs/item_{index}.md", "operation": "modified"}
                for index in range(6)
            ]
            (project_root / receipt_ref).with_suffix(".json").write_text(
                json.dumps(
                    {
                        "schema": "jikuo.runtime_state_summary.v0",
                        "status": "available",
                        "updated_at_utc": "2026-06-02T00:00:00Z",
                        "source": {
                            "proposal_id": "proposal_receipt",
                            "status": "review",
                            "event": "completion_review",
                        },
                        "runtime_visibility": {"history_ref": receipt_ref},
                        "semantic_intent_coverage": {
                            "schema": "jikuo.semantic_intent_coverage.v0",
                            "coverage_status": "complete",
                            "semantic_intent_status": "provided",
                            "evidence_status": "ok",
                            "provider": "host_ai",
                            "required": True,
                            "policy_scopes": ["editing"],
                        },
                        "artifact_assurance": {
                            "schema": "jikuo.studio.artifact_assurance.v0",
                            "status": "ok",
                            "read_assurance": {"required_read_count": 0},
                            "write_assurance": {
                                "required_write_count": 1,
                                "required_companion_write_count": 1,
                                "actual_write_count": 6,
                                "required_write_set": [
                                    {
                                        "path": "docs/registry/capabilities.yaml",
                                        "reason": "capability registration",
                                    }
                                ],
                                "required_companion_write_set": [
                                    {
                                        "path": "docs/registry/capabilities.yaml",
                                        "reason": "feature atom registration",
                                    }
                                ],
                                "completion_check_candidate_count": 1,
                                "completion_check_candidates": [
                                    {
                                        "path": "docs/work_orders/receipt.md",
                                        "reason": "completion check",
                                    }
                                ],
                                "actual_write_set": actual_writes,
                            },
                            "gap_report": {"gap_count": 0, "write_gaps": []},
                        },
                    }
                ),
                encoding="utf-8",
            )
            (runtime_root / "state_summary.json").write_text(
                json.dumps(
                    {
                        "schema": "jikuo.runtime_state_summary.v0",
                        "status": "available",
                        "updated_at_utc": "2026-06-02T01:00:00Z",
                        "source": {
                            "proposal_id": "proposal_latest",
                            "status": "review",
                            "event": "conversation_turn",
                        },
                        "runtime_visibility": {"history_ref": latest_ref},
                    }
                ),
                encoding="utf-8",
            )

            report = global_status.build_global_status(project_root=project_root)

            traces = report["summaries"]["runtime"]["round_document_traces"]
            self.assertEqual(traces["default_round_id"], Path(latest_ref).stem)
            self.assertEqual(traces["default_selection"], "latest_round")
            self.assertEqual(traces["newest_round_id"], Path(latest_ref).stem)
            receipt = next(
                item for item in traces["rounds"] if item["round_id"] == Path(receipt_ref).stem
            )
            self.assertEqual(receipt["source_kind"], "runtime_history_state_summary")
            self.assertEqual(receipt["trace_label"], "Structured document receipt")
            self.assertEqual(
                receipt["semantic_intent_coverage"]["coverage_status"],
                "complete",
            )
            semantic_evidence = report["summaries"]["runtime"]["semantic_intent_evidence"]
            classification = semantic_evidence["classification"]
            self.assertTrue(classification["ai_classified"])
            self.assertEqual(classification["classification_source"], "host_ai")
            self.assertEqual(classification["provider"], "host_ai")
            self.assertEqual(
                semantic_evidence["latest_round"]["round_id"],
                Path(latest_ref).stem,
            )
            self.assertEqual(
                semantic_evidence["classification_round"]["round_id"],
                Path(receipt_ref).stem,
            )
            self.assertIn(
                "Latest runtime semantic evidence incomplete",
                {item["title"] for item in semantic_evidence["imperfections"]},
            )
            write = receipt["artifact_assurance"]["write_assurance"]
            self.assertEqual(
                write["required_companion_write_set"][0]["path"],
                "docs/registry/capabilities.yaml",
            )
            self.assertEqual(len(write["actual_write_set"]), 6)
            self.assertEqual(receipt["counts"]["actual_write_count"], 6)

    def test_global_status_reports_document_mount_read_model(self):
        report = global_status.build_global_status(project_root=ROOT)

        document_mounts = report["summaries"]["document_mounts"]
        self.assertEqual(document_mounts["status"], "available")
        self.assertEqual(document_mounts["project_context_ref"], ".jikuo/project_context.yaml")
        self.assertEqual(document_mounts["mount_sets_ref"], "docs/registry/mount_sets.yaml")
        self.assertGreaterEqual(document_mounts["role_count"], 1)
        self.assertGreaterEqual(document_mounts["checked_document_count"], 1)
        self.assertIn(".jikuo/project_context.yaml", document_mounts["active_mount_authority"])
        self.assertEqual(
            document_mounts["configuration_language_schema"],
            "jikuo.studio.configuration_language.v0",
        )
        terms = {item["term_id"]: item for item in document_mounts["configuration_terms"]}
        self.assertEqual(terms["document_rules"]["user_label"], "Document rules")
        self.assertIn(
            ".jikuo/project_context.yaml main_document_mounts",
            terms["document_rules"]["internal_refs"],
        )
        self.assertEqual(
            terms["rule_sources"]["user_label"],
            "Configuration sources and guidance",
        )
        self.assertEqual(
            terms["editable_configuration"]["user_label"],
            "Editable configuration",
        )
        self.assertEqual(
            terms["governance_guidance"]["user_label"],
            "Governance guidance",
        )
        self.assertIn("stability_rule", terms["edit_status"])
        editable_sources = document_mounts["editable_configuration_sources"]
        guidance_sources = document_mounts["governance_guidance_sources"]
        self.assertEqual(editable_sources[0]["path"], ".jikuo/project_context.yaml")
        self.assertTrue(editable_sources[0]["editable_in_studio"])
        self.assertEqual(
            guidance_sources[0]["path"],
            "docs/governance/jikuo_execution_mounts.md",
        )
        self.assertFalse(guidance_sources[0]["editable_in_studio"])
        self.assertEqual(
            document_mounts["source_truth_boundary"]["studio_write_target"],
            ".jikuo/project_context.yaml",
        )
        self.assertFalse(report["writes_performed"])

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
        self.assertIn("## Document rules", markdown_completed.stdout)
        self.assertIn("Review document rules", markdown_completed.stdout)


if __name__ == "__main__":
    unittest.main()
