import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo import runtime_write_observation  # noqa: E402


def require_git() -> None:
    if shutil.which("git") is None:
        raise unittest.SkipTest("git executable is not available")


def run_git(project_root: Path, *args: str) -> None:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "JIKUO Test",
            "GIT_AUTHOR_EMAIL": "jikuo-test@example.com",
            "GIT_COMMITTER_NAME": "JIKUO Test",
            "GIT_COMMITTER_EMAIL": "jikuo-test@example.com",
        }
    )
    subprocess.run(
        ["git", "-C", str(project_root), "-c", "core.excludesFile=", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )


def create_repo(tmp_root: Path) -> Path:
    require_git()
    project_root = tmp_root / "repo"
    project_root.mkdir()
    run_git(project_root, "init")
    run_git(project_root, "config", "user.name", "JIKUO Test")
    run_git(project_root, "config", "user.email", "jikuo-test@example.com")
    return project_root


def commit_file(project_root: Path, path: str, content: str = "initial\n") -> None:
    target = project_root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    run_git(project_root, "add", path)
    run_git(project_root, "commit", "-m", f"add {path}")


class RuntimeWriteObservationTests(unittest.TestCase):
    def test_clean_git_repo_reports_empty_observed_write_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = create_repo(Path(tmp))
            commit_file(project_root, "tracked.txt")

            report = runtime_write_observation.observe_git_actual_writes(project_root)

            self.assertEqual(report["schema"], runtime_write_observation.RUNTIME_WRITE_OBSERVATION_SCHEMA)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["observed_actual_write_count"], 0)
            self.assertEqual(report["observed_actual_write_set"], [])
            self.assertFalse(report["writes_performed"])
            self.assertIn("does_not_read_file_contents", report["non_effects"])

    def test_observes_added_modified_deleted_and_renamed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = create_repo(Path(tmp))
            commit_file(project_root, "modified.txt")
            commit_file(project_root, "deleted.txt")
            commit_file(project_root, "old.txt")

            (project_root / "modified.txt").write_text("changed\n", encoding="utf-8")
            (project_root / "deleted.txt").unlink()
            run_git(project_root, "mv", "old.txt", "renamed.txt")
            (project_root / "new file.md").write_text("new\n", encoding="utf-8")

            report = runtime_write_observation.observe_git_actual_writes(project_root)

            self.assertEqual(report["status"], "ok")
            by_path = {item["path"]: item for item in report["observed_actual_write_set"]}
            self.assertEqual(by_path["modified.txt"]["operation"], "modified")
            self.assertEqual(by_path["deleted.txt"]["operation"], "deleted")
            self.assertEqual(by_path["renamed.txt"]["operation"], "renamed")
            self.assertEqual(by_path["renamed.txt"]["previous_path"], "old.txt")
            self.assertEqual(by_path["new file.md"]["operation"], "added")
            for item in by_path.values():
                self.assertEqual(item["source_kind"], "git_diff")
                self.assertEqual(item["evidence_kind"], "actual_write")
                self.assertEqual(item["attribution_status"], "mixed_or_uncertain")
            self.assertEqual(report["attribution_status"], "mixed_or_uncertain")

    def test_non_git_project_returns_unavailable_without_raising(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "not-git"
            project_root.mkdir()
            (project_root / "changed.txt").write_text("not tracked\n", encoding="utf-8")

            report = runtime_write_observation.observe_git_actual_writes(project_root)

            self.assertEqual(report["status"], "unavailable")
            self.assertEqual(report["reason"], "not_git_worktree")
            self.assertEqual(report["observed_actual_write_count"], 0)
            self.assertFalse(report["writes_performed"])

    def test_parser_reports_renames_from_porcelain_z_tokens(self) -> None:
        output = "R  docs/new name.md\0docs/old name.md\0?? scratch.txt\0"

        items, warnings = runtime_write_observation.parse_git_status_porcelain_z(output)

        self.assertEqual(warnings, [])
        self.assertEqual(items[0]["path"], "docs/new name.md")
        self.assertEqual(items[0]["previous_path"], "docs/old name.md")
        self.assertEqual(items[0]["operation"], "renamed")
        self.assertEqual(items[1]["path"], "scratch.txt")
        self.assertEqual(items[1]["operation"], "added")


if __name__ == "__main__":
    unittest.main()
