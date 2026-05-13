import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "task_session_cards.py"
TASK_SESSION_TOOL = ROOT / "src" / "jikuo" / "task_session.py"
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
READY_PROJECT = FIXTURES / "task_session_ready_project"
MISSING_PROJECT = FIXTURES / "missing_project"


class TaskSessionCardProjectionTests(unittest.TestCase):
    def test_start_preview_json_card_is_no_write_and_explicit(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "start-preview",
                "--task-title",
                "Card Projection Probe",
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
        card = json.loads(completed.stdout)
        self.assertEqual(
            card["schema"],
            "jikuo.desktop_task_session_workflow_card.v0",
        )
        self.assertEqual(card["card_kind"], "task_session_start_preview")
        self.assertEqual(card["status"], "review")
        self.assertIn("task-session file creation", card["write_effect"]["target"])
        self.assertIn(
            "do not update .jikuo/project_state.yaml latest_task_session_refs",
            card["write_effect"]["non_effects"],
        )
        self.assertEqual(
            card["approval_request"]["exact_user_phrase"],
            "<exact user phrase as spoken>",
        )
        command = card["command_proposal"]["command_preview"]
        self.assertIn("python -B -m jikuo.task_session", command)
        self.assertNotIn("tools/jikuo", command)
        self.assertIn("--confirm-create-task-session", card["command_proposal"]["required_flags"])
        self.assertFalse((READY_PROJECT / ".jikuo" / "task_sessions").exists())

    def test_missing_project_renders_refusal_card_without_command_proposal(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "start-preview",
                "--task-title",
                "Card Projection Probe",
                "--project-root",
                str(MISSING_PROJECT),
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
        card = json.loads(completed.stdout)
        self.assertEqual(card["card_kind"], "task_session_refusal")
        self.assertEqual(card["status"], "refused")
        self.assertIsNone(card["command_proposal"])
        self.assertIn(
            "project state must be initialized before task-session planning",
            card["refusal_reasons"],
        )
        self.assertFalse((MISSING_PROJECT / ".jikuo").exists())

    def test_index_preview_markdown_names_non_effects(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "index-preview",
                "--project-root",
                str(READY_PROJECT),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Task-session index refresh", completed.stdout)
        self.assertIn("do not create task-session files", completed.stdout)
        self.assertIn("would_update_project_state", completed.stdout)

    def test_render_json_projects_existing_start_plan_to_markdown(self):
        plan_completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TASK_SESSION_TOOL),
                "start",
                "--dry-run",
                "--task-title",
                "Render JSON Probe",
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
        self.assertEqual(plan_completed.returncode, 0, plan_completed.stderr)

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8",
        ) as handle:
            handle.write(plan_completed.stdout)
            input_path = handle.name
        try:
            card_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "render-json",
                    "--input",
                    input_path,
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        finally:
            Path(input_path).unlink(missing_ok=True)

        self.assertEqual(card_completed.returncode, 0, card_completed.stderr)
        self.assertIn("Task-session start preview", card_completed.stdout)
        self.assertIn("Command Proposal", card_completed.stdout)
        self.assertIn("python -B -m jikuo.task_session", card_completed.stdout)
        self.assertNotIn("tools/jikuo", card_completed.stdout)
        self.assertIn("<exact user phrase as spoken>", card_completed.stdout)


if __name__ == "__main__":
    unittest.main()
