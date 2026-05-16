import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jikuo import activation_settings
from jikuo.integrations import instruction_files


ROOT = Path(__file__).resolve().parents[1]


class ActivationSettingsTests(unittest.TestCase):
    def test_plan_is_review_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = activation_settings.build_plan(
                project_root=project_root,
                trigger_mode="mounted",
                clients=["claude-code"],
            )

            self.assertEqual(report["schema"], activation_settings.SETTINGS_PLAN_SCHEMA)
            self.assertEqual(report["status"], "review")
            self.assertEqual(report["operation"], "create")
            self.assertFalse(report["write_allowed_by_command"])
            self.assertFalse(report["writes_performed"])
            self.assertTrue(report["approval_required"])
            self.assertEqual(report["desired_trigger_mode"], "mounted")
            self.assertFalse((project_root / activation_settings.SETTINGS_REF).exists())

    def test_missing_status_reports_non_strict_configuration_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = activation_settings.build_status_report(project_root=project_root)

            self.assertEqual(report["status"], "missing")
            self.assertEqual(report["desired_trigger_mode"], "ask")
            self.assertEqual(report["effective_enforcement_level"], "instruction_only")
            self.assertEqual(report["strict_mount_status"], "not_configured")
            self.assertEqual(report["adapter_status"], "not_available")
            self.assertTrue(report["configuration_required"])
            self.assertTrue(report["onboarding_required"])
            self.assertEqual(
                report["field_provenance"]["desired_trigger_mode"]["source"],
                "implicit_default",
            )
            self.assertEqual(
                report["required_user_decisions"][0]["field"],
                "desired_trigger_mode",
            )
            self.assertTrue(report["next_actions"])

    def test_existing_settings_without_provenance_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            settings_path = project_root / activation_settings.SETTINGS_REF
            settings_path.parent.mkdir(parents=True)
            settings_path.write_text(
                "\n".join(
                    [
                        'schema: "jikuo.project_activation_settings.v0"',
                        'desired_trigger_mode: "ask"',
                        'effective_enforcement_level: "instruction_only"',
                        "strict_mounted_requires_adapter: true",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = activation_settings.build_status_report(project_root=project_root)

            self.assertEqual(report["status"], "review")
            self.assertTrue(report["onboarding_required"])
            self.assertEqual(
                report["field_provenance"]["desired_trigger_mode"]["source"],
                "legacy_file_without_review_metadata",
            )

    def test_apply_requires_confirmation_and_approval_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report, exit_code = activation_settings.apply_plan(
                project_root=project_root,
                trigger_mode="semantic",
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(report["schema"], activation_settings.SETTINGS_RESULT_SCHEMA)
            self.assertEqual(report["status"], "refused")
            self.assertIn("confirm_apply_required", report["refusal_reasons"])
            self.assertIn("approval_phrase_required", report["refusal_reasons"])
            self.assertFalse((project_root / activation_settings.SETTINGS_REF).exists())

    def test_guarded_apply_writes_settings_and_preserves_unknown_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            settings_path = project_root / activation_settings.SETTINGS_REF
            settings_path.parent.mkdir(parents=True)
            settings_path.write_text(
                "\n".join(
                    [
                        'schema: "jikuo.project_activation_settings.v0"',
                        'desired_trigger_mode: "semantic"',
                        'custom_field: "keep me"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report, exit_code = activation_settings.apply_plan(
                project_root=project_root,
                trigger_mode="mounted",
                clients=["claude-code", "cursor"],
                confirm_apply=True,
                approval_phrase="approved for test",
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(report["status"], "ok")
            self.assertTrue(report["writes_performed"])
            self.assertEqual(report["written_refs"], [activation_settings.SETTINGS_REF])
            text = settings_path.read_text(encoding="utf-8")
            self.assertIn('desired_trigger_mode: "mounted"', text)
            self.assertIn("configuration_review:", text)
            self.assertIn("field_provenance:", text)
            self.assertIn('source: "user_configured"', text)
            self.assertIn('client: "claude-code"', text)
            self.assertIn('client: "cursor"', text)
            self.assertIn('custom_field: "keep me"', text)
            status = activation_settings.build_status_report(project_root=project_root)
            self.assertFalse(status["onboarding_required"])

    def test_guarded_apply_can_record_reviewed_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report, exit_code = activation_settings.apply_plan(
                project_root=project_root,
                trigger_mode="ask",
                effective_enforcement_level="instruction_only",
                confirm_apply=True,
                approval_phrase="approved for test",
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report["writes_performed"])
            text = (project_root / activation_settings.SETTINGS_REF).read_text(
                encoding="utf-8"
            )
            self.assertIn('source: "user_reviewed_default"', text)
            status = activation_settings.build_status_report(project_root=project_root)
            self.assertEqual(status["status"], "available")
            self.assertFalse(status["onboarding_required"])
            self.assertEqual(status["required_user_decisions"], [])

    def test_plan_detects_enabled_client_changes_after_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            activation_settings.apply_plan(
                project_root=project_root,
                trigger_mode="ask",
                clients=["codex"],
                confirm_apply=True,
                approval_phrase="approved for test",
            )

            status = activation_settings.build_status_report(project_root=project_root)
            self.assertEqual(
                [item["client"] for item in status["enabled_clients"]],
                ["codex"],
            )
            noop_plan = activation_settings.build_plan(
                project_root=project_root,
                trigger_mode="ask",
                clients=["codex"],
            )
            update_plan = activation_settings.build_plan(
                project_root=project_root,
                trigger_mode="ask",
                clients=["codex", "cursor"],
            )

            self.assertEqual(noop_plan["operation"], "noop")
            self.assertEqual(update_plan["operation"], "update")

    def test_instruction_install_uses_project_trigger_mode_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            activation_settings.apply_plan(
                project_root=project_root,
                trigger_mode="mounted",
                confirm_apply=True,
                approval_phrase="approved for test",
            )

            report = instruction_files.build_install_plan(
                project_root=project_root,
                clients=["codex"],
            )

            self.assertEqual(report["activation_settings"]["trigger_mode"], "mounted")
            self.assertEqual(
                report["activation_settings"]["trigger_mode_source"],
                "project_activation_settings",
            )

    def test_agent_flow_uses_project_trigger_mode_when_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            activation_settings.apply_plan(
                project_root=project_root,
                trigger_mode="mounted",
                confirm_apply=True,
                approval_phrase="approved for test",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo.agent_flow",
                    "propose",
                    "--event",
                    "conversation_turn",
                    "--project-root",
                    str(project_root),
                    "--user-phrase",
                    "thanks for the update",
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
            router = proposal["conversation_router"]
            self.assertEqual(router["trigger_mode"], "mounted")
            self.assertEqual(
                router["classified_obligations"][0]["kind"],
                "mounted_idle_tick",
            )
            self.assertEqual(
                router["activation_settings"]["strict_mount_status"],
                "degraded_instruction_only",
            )
            self.assertFalse(
                router["mount_degradation"]["strict_pre_turn_guaranteed"]
            )

    def test_show_includes_activation_settings_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            activation_settings.apply_plan(
                project_root=project_root,
                trigger_mode="semantic",
                confirm_apply=True,
                approval_phrase="approved for test",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo",
                    "show",
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
            self.assertEqual(
                report["activation_settings"]["desired_trigger_mode"],
                "semantic",
            )


if __name__ == "__main__":
    unittest.main()
