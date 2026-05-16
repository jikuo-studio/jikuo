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
            self.assertIn('client: "claude-code"', text)
            self.assertIn('client: "cursor"', text)
            self.assertIn('custom_field: "keep me"', text)

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
