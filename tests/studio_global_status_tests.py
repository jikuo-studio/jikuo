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
        self.assertIn("studio.runtime.open_latest_card", action_ids)

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
                runtime["artifact_assurance"]["write_assurance"]["planned_write_count"],
                1,
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
