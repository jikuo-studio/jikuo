import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jikuo import runtime_visibility


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "agent_flow.py"
FIXTURES = ROOT / "src" / "jikuo" / "fixtures"
READY_PROJECT = FIXTURES / "task_session_ready_project"


class RuntimeVisibilityTests(unittest.TestCase):
    def test_agent_flow_writes_runtime_snapshot_and_show_reads_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(READY_PROJECT, project_root)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "propose",
                    "--event",
                    "task_start",
                    "--task-title",
                    "Runtime Visibility Probe",
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
            runtime_report = proposal["runtime_visibility"]
            display_links = proposal["client_display_links"]
            self.assertEqual(runtime_report["status"], "ok")
            self.assertTrue(runtime_report["write_performed"])
            self.assertEqual(runtime_report["last_card_ref"], ".jikuo/runtime/last_card.md")
            self.assertEqual(
                runtime_report["state_summary_ref"],
                ".jikuo/runtime/state_summary.json",
            )
            self.assertEqual(display_links["schema"], "jikuo.client_display_links.v0")
            self.assertEqual(display_links["status"], "available")
            self.assertEqual(
                display_links["links"]["last_card"]["ref"],
                ".jikuo/runtime/last_card.md",
            )
            self.assertIn("## JIKUO Runtime Links", proposal["chat_ready_markdown"])
            self.assertIn(
                display_links["links"]["last_card"]["markdown"],
                proposal["chat_ready_markdown"],
            )
            self.assertIn("CAP-RUNTIME-VISIBILITY-CHANNEL-01", {
                trace["atom_id"] for trace in proposal["atom_trace"]
            })

            last_card_path = project_root / runtime_report["last_card_ref"]
            state_summary_path = project_root / runtime_report["state_summary_ref"]
            history_path = project_root / runtime_report["history_ref"]
            self.assertTrue(last_card_path.is_file())
            self.assertTrue(state_summary_path.is_file())
            self.assertTrue(history_path.is_file())
            self.assertEqual(
                last_card_path.read_text(encoding="utf-8"),
                proposal["chat_ready_markdown"],
            )
            self.assertIn(
                last_card_path.resolve().as_posix(),
                display_links["links"]["last_card"]["markdown_target"],
            )
            state_summary = json.loads(state_summary_path.read_text(encoding="utf-8"))
            self.assertEqual(state_summary["schema"], "jikuo.runtime_state_summary.v0")
            self.assertEqual(
                state_summary["client_display_links"]["links"]["last_card"]["ref"],
                ".jikuo/runtime/last_card.md",
            )
            self.assertEqual(state_summary["counts"]["card_count"], len(proposal["cards"]))
            self.assertTrue(state_summary["write_boundary"]["runtime_visibility_write_performed"])
            self.assertFalse((project_root / ".jikuo" / "policies").exists())
            self.assertFalse((project_root / ".jikuo" / "task_sessions").exists())

            show = subprocess.run(
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
            self.assertEqual(show.returncode, 0, show.stderr)
            show_report = json.loads(show.stdout)
            self.assertEqual(show_report["status"], "available")
            self.assertEqual(
                show_report["runtime_visibility"]["last_card_ref"],
                ".jikuo/runtime/last_card.md",
            )
            self.assertEqual(
                show_report["client_display_links"]["links"]["last_card"]["markdown"],
                display_links["links"]["last_card"]["markdown"],
            )

            show_card = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo",
                    "show",
                    "--project-root",
                    str(project_root),
                    "--last-card",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(show_card.returncode, 0, show_card.stderr)
            self.assertEqual(show_card.stdout, proposal["chat_ready_markdown"])

    def test_show_reports_stale_task_session_index_without_refreshing_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            shutil.copytree(READY_PROJECT, project_root)
            state_path = project_root / ".jikuo" / "project_state.yaml"
            state_path.write_text(
                state_path.read_text(encoding="utf-8")
                .replace('project_root: "fixture"', 'project_root: "."')
                .replace('jikuo_state_root: "fixture/.jikuo"', 'jikuo_state_root: ".jikuo"'),
                encoding="utf-8",
            )
            sessions_root = project_root / ".jikuo" / "task_sessions"
            sessions_root.mkdir(parents=True)
            session_path = sessions_root / "task_20260514T000000Z_stale_probe.yaml"
            session_path.write_text(
                "\n".join(
                    [
                        'schema: "jikuo.task_session.v0"',
                        'session_id: "task_20260514T000000Z_stale_probe"',
                        'task_title: "Stale Probe"',
                        'owner_agent: "codex"',
                        'created_at: "2026-05-14T00:00:00Z"',
                        'lifecycle_status: "started"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            runtime_visibility.persist_agent_flow_snapshot(
                project_root=project_root,
                proposal={
                    "schema": "test.proposal",
                    "proposal_id": "stale_task_session_index_probe",
                    "runner_mode": "test",
                    "status": "review",
                    "trigger_decision": {"invocation_scenario": "test"},
                    "cards": [],
                    "triggered_policies": [],
                    "missing_evidence_reports": [],
                    "required_actions": [],
                    "write_effect": {"writes_performed": False},
                },
                card_markdown="# Probe\n",
            )

            show = subprocess.run(
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

            self.assertEqual(show.returncode, 0, show.stderr)
            show_report = json.loads(show.stdout)
            task_index = show_report["task_session_index"]
            self.assertEqual(task_index["schema"], "jikuo.task_session_index_status.v0")
            self.assertEqual(task_index["status"], "stale")
            self.assertEqual(task_index["current_latest_task_session_ref_count"], 0)
            self.assertEqual(task_index["discovered_task_session_count"], 1)
            self.assertTrue(task_index["would_update_project_state"])
            self.assertIn("--dry-run", task_index["commands"]["dry_run"])
            self.assertIn("--refresh", task_index["commands"]["refresh"])
            self.assertIn("latest_task_session_refs: []", (
                project_root / ".jikuo" / "project_state.yaml"
            ).read_text(encoding="utf-8"))

            show_markdown = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo",
                    "show",
                    "--project-root",
                    str(project_root),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(show_markdown.returncode, 0, show_markdown.stderr)
            self.assertIn("## Task-Session Index", show_markdown.stdout)
            self.assertIn("- Status: `stale`", show_markdown.stdout)
            self.assertIn("jikuo.task_session index --dry-run", show_markdown.stdout)

    def test_package_fixture_projects_are_not_mutated_by_runtime_visibility(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(TOOL),
                "propose",
                "--event",
                "task_start",
                "--task-title",
                "Fixture Runtime Skip Probe",
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
        runtime_report = proposal["runtime_visibility"]
        self.assertEqual(runtime_report["status"], "skipped")
        self.assertEqual(
            runtime_report["reason"],
            "package_fixture_project_is_read_only",
        )
        self.assertEqual(proposal["client_display_links"]["status"], "unavailable")
        self.assertEqual(proposal["client_display_links"]["links"], {})
        self.assertFalse((READY_PROJECT / ".jikuo" / "runtime").exists())

    def test_runtime_history_ref_is_confined_under_runtime_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            report = runtime_visibility.prepare_agent_flow_snapshot(
                project_root=project_root,
                proposal={
                    "schema": "test.proposal",
                    "proposal_id": "../../escape",
                },
            )
            history_path = (project_root / report["history_ref"]).resolve()
            runtime_root = (project_root / ".jikuo" / "runtime").resolve()
            history_path.relative_to(runtime_root)
            self.assertNotIn("..", report["history_ref"])


if __name__ == "__main__":
    unittest.main()
