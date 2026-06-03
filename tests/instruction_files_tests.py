import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jikuo.integrations import instruction_files


ROOT = Path(__file__).resolve().parents[1]


class InstructionFilesTests(unittest.TestCase):
    def test_install_plan_is_review_only_and_includes_canonical_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = instruction_files.build_install_plan(project_root=project_root)

            self.assertEqual(report["schema"], instruction_files.INSTALL_PLAN_SCHEMA)
            self.assertEqual(report["status"], "review")
            self.assertEqual(report["selected_clients"], ["jikuo"])
            self.assertFalse(report["write_allowed_by_command"])
            self.assertFalse(report["writes_performed"])
            self.assertTrue(report["approval_required"])
            self.assertEqual(report["targets"][0]["path_ref"], "JIKUO.md")
            self.assertEqual(report["targets"][0]["operation"], "create")
            self.assertEqual(report["activation_settings"]["trigger_mode"], "ask")
            self.assertTrue(report["activation_settings"]["client_prompt_required"])
            self.assertFalse((project_root / "JIKUO.md").exists())

    def test_write_requires_confirmation_and_approval_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report, exit_code = instruction_files.apply_install_plan(
                project_root=project_root,
                clients=["codex"],
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(report["schema"], instruction_files.INSTALL_RESULT_SCHEMA)
            self.assertEqual(report["status"], "refused")
            self.assertIn("confirm_install_required", report["refusal_reasons"])
            self.assertIn("approval_phrase_required", report["refusal_reasons"])
            self.assertFalse(report["writes_performed"])
            self.assertFalse((project_root / "JIKUO.md").exists())
            self.assertFalse((project_root / "AGENTS.md").exists())

    def test_guarded_write_preserves_existing_client_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            agents_path = project_root / "AGENTS.md"
            agents_path.write_text(
                "# Existing Codex Notes\n\nKeep this local note.\n",
                encoding="utf-8",
            )

            report, exit_code = instruction_files.apply_install_plan(
                project_root=project_root,
                clients=["codex"],
                confirm_install=True,
                approval_phrase="approved for test",
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(report["status"], "ok")
            self.assertTrue(report["writes_performed"])
            self.assertEqual(set(report["written_refs"]), {"JIKUO.md", "AGENTS.md"})
            self.assertTrue((project_root / "JIKUO.md").is_file())
            agents_text = agents_path.read_text(encoding="utf-8")
            self.assertIn("# Existing Codex Notes", agents_text)
            self.assertIn("Keep this local note.", agents_text)
            self.assertIn(instruction_files.MANAGED_BEGIN, agents_text)
            self.assertIn(instruction_files.MANAGED_END, agents_text)
            self.assertIn("Show returned governance card Markdown verbatim", agents_text)
            self.assertIn("--event completion_review", agents_text)
            self.assertIn("after verification and before the final response", agents_text)
            self.assertIn("completion receipt is missing or failed", agents_text)
            self.assertIn("Activation settings:", agents_text)
            self.assertIn("Ask the user to choose `semantic` mode or `mounted` mode", agents_text)
            self.assertIn("Keep this managed block aligned with `JIKUO.md`", agents_text)

    def test_install_plan_can_pin_mounted_mode_for_vscode_copilot(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = instruction_files.build_install_plan(
                project_root=project_root,
                clients=["vscode-copilot"],
                trigger_mode="mounted",
            )

            self.assertEqual(report["selected_clients"], ["jikuo", "vscode-copilot"])
            self.assertEqual(report["activation_settings"]["trigger_mode"], "mounted")
            target_refs = {target["path_ref"] for target in report["targets"]}
            self.assertEqual(target_refs, {"JIKUO.md", ".github/copilot-instructions.md"})

            block = instruction_files.render_managed_block(
                "vscode-copilot",
                trigger_mode="mounted",
            )
            self.assertIn("Configured trigger mode for this client: `mounted`", block)
            self.assertIn("--event completion_review", block)
            self.assertIn("not strictly enforceable until a pre-turn adapter is installed", block)

    def test_install_all_detects_existing_client_instruction_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            (project_root / ".cursorrules").write_text(
                "Existing Cursor rules\n",
                encoding="utf-8",
            )

            report = instruction_files.build_install_plan(
                project_root=project_root,
                all_clients=True,
            )

            self.assertEqual(report["selected_clients"], ["jikuo", "cursor"])
            self.assertEqual(report["warnings"], [])
            target_refs = {target["path_ref"] for target in report["targets"]}
            self.assertEqual(target_refs, {"JIKUO.md", ".cursorrules"})

    def test_top_level_cli_install_outputs_json_and_writes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo",
                    "install",
                    "--project-root",
                    str(project_root),
                    "--client",
                    "continue",
                    "--trigger-mode",
                    "semantic",
                    "--write",
                    "--confirm-install",
                    "--approval-phrase",
                    "approved for test",
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
            self.assertEqual(report["schema"], instruction_files.INSTALL_RESULT_SCHEMA)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["activation_settings"]["trigger_mode"], "semantic")
            self.assertEqual(set(report["written_refs"]), {"JIKUO.md", ".continuerules"})
            self.assertTrue((project_root / "JIKUO.md").is_file())
            self.assertTrue((project_root / ".continuerules").is_file())


if __name__ == "__main__":
    unittest.main()
