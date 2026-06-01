import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo.studio import document_rules  # noqa: E402


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


def touch(root: Path, rel: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {path.name}\n", encoding="utf-8")


class StudioDocumentRulesTests(unittest.TestCase):
    def test_document_rules_plan_adds_context_completion_and_authority_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/user-guide.md")
            touch(project_root, "docs/governance/custom-rules.md")
            before = (project_root / ".jikuo" / "project_context.yaml").read_text(
                encoding="utf-8"
            )

            plan = document_rules.build_document_rules_update_plan(
                project_root=project_root,
                add_context_docs=["user_guide=docs/user-guide.md"],
                add_completion_checks=["docs/user-guide.md"],
                add_governance_references=["docs/governance/custom-rules.md"],
                completion_update_rule="user guide or document-rule scope changes",
            )

            self.assertEqual(plan["schema"], document_rules.DOCUMENT_RULES_PLAN_SCHEMA)
            self.assertEqual(plan["status"], "review")
            self.assertEqual(plan["target_files"], [".jikuo/project_context.yaml"])
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(plan["write_allowed_by_command"])
            self.assertEqual(plan["change_count"], 3)
            self.assertEqual(plan["validation"]["errors"], [])
            self.assertEqual(
                plan["proposed_changes"]["document_role_additions"][0]["role"],
                "user_guide",
            )
            self.assertEqual(
                plan["proposed_changes"]["completion_check_additions"][0]["path"],
                "docs/user-guide.md",
            )
            self.assertEqual(
                plan["proposed_changes"]["active_mount_authority_additions"][0]["path"],
                "docs/governance/custom-rules.md",
            )
            self.assertEqual(
                before,
                (project_root / ".jikuo" / "project_context.yaml").read_text(
                    encoding="utf-8"
                ),
            )

    def test_document_rules_plan_reports_duplicate_changes_as_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)

            plan = document_rules.build_document_rules_update_plan(
                project_root=project_root,
                add_context_docs=[".jikuo/project_context.yaml"],
                add_completion_checks=[".jikuo/project_context.yaml"],
                add_governance_references=[".jikuo/project_context.yaml"],
            )

            self.assertEqual(plan["status"], "noop")
            self.assertEqual(plan["change_count"], 0)
            noop_codes = {item["code"] for item in plan["validation"]["noops"]}
            self.assertIn("context_document_already_bound", noop_codes)
            self.assertIn("completion_check_already_present", noop_codes)
            self.assertIn("governance_reference_already_active", noop_codes)

    def test_document_rules_plan_refuses_outside_missing_and_legacy_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/governance/jikuo_productization_task_map.md")

            plan = document_rules.build_document_rules_update_plan(
                project_root=project_root,
                add_context_docs=["../outside.md"],
                add_completion_checks=["docs/missing.md"],
                add_governance_references=[
                    "docs/governance/jikuo_productization_task_map.md"
                ],
            )

            self.assertEqual(plan["status"], "refused")
            error_codes = {item["code"] for item in plan["validation"]["errors"]}
            self.assertIn("path_outside_project_root", error_codes)
            self.assertIn("referenced_document_missing", error_codes)
            self.assertIn("legacy_task_map_authority_expansion_refused", error_codes)
            self.assertFalse(plan["writes_performed"])

    def test_document_rules_cli_returns_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/user-guide.md")

            json_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo",
                    "studio",
                    "document-rules",
                    "plan",
                    "--project-root",
                    str(project_root),
                    "--add-context-doc",
                    "docs/user-guide.md",
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
                    "document-rules",
                    "plan",
                    "--project-root",
                    str(project_root),
                    "--add-context-doc",
                    "docs/user-guide.md",
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
            self.assertEqual(report["schema"], document_rules.DOCUMENT_RULES_PLAN_SCHEMA)
            self.assertEqual(report["status"], "review")
            self.assertEqual(markdown_completed.returncode, 0, markdown_completed.stderr)
            self.assertIn("# JIKUO Document Rules Update Plan", markdown_completed.stdout)
            self.assertIn("docs/user-guide.md", markdown_completed.stdout)


if __name__ == "__main__":
    unittest.main()
