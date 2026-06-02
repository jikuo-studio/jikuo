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
            self.assertIn(".jikuo/project_context.yaml", plan["source_fingerprints"])
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

    def test_document_rules_apply_refuses_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/user-guide.md")
            plan = document_rules.build_document_rules_update_plan(
                project_root=project_root,
                add_context_docs=["docs/user-guide.md"],
            )
            before = (project_root / ".jikuo" / "project_context.yaml").read_text(
                encoding="utf-8"
            )

            result, exit_code = document_rules.apply_document_rules_update_plan(
                plan,
                project_root=project_root,
                confirmed=False,
                approval_phrase=None,
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(result["status"], "refused")
            self.assertFalse(result["write_performed"])
            self.assertIn("missing technical confirmation flag", result["refusal_reasons"])
            self.assertIn("missing approval phrase evidence", result["refusal_reasons"])
            self.assertEqual(
                before,
                (project_root / ".jikuo" / "project_context.yaml").read_text(
                    encoding="utf-8"
                ),
            )

    def test_document_rules_apply_refuses_stale_source_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/user-guide.md")
            plan = document_rules.build_document_rules_update_plan(
                project_root=project_root,
                add_context_docs=["docs/user-guide.md"],
            )
            context_path = project_root / ".jikuo" / "project_context.yaml"
            context_path.write_text(
                context_path.read_text(encoding="utf-8")
                + "compatibility:\n  unknown_fields: \"preserve\"\n",
                encoding="utf-8",
            )

            result, exit_code = document_rules.apply_document_rules_update_plan(
                plan,
                project_root=project_root,
                confirmed=True,
                approval_phrase=document_rules.DOCUMENT_RULES_APPROVAL_PHRASE,
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(result["status"], "refused")
            self.assertIn("stale source fingerprint", result["refusal_reasons"])
            self.assertFalse(result["write_performed"])

    def test_document_rules_apply_with_approval_writes_project_context_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/user-guide.md")
            touch(project_root, "docs/governance/custom-rules.md")
            legacy = project_root / "docs" / "governance" / "jikuo_productization_task_map.md"
            touch(project_root, "docs/governance/jikuo_productization_task_map.md")
            legacy_before = legacy.read_text(encoding="utf-8")
            plan = document_rules.build_document_rules_update_plan(
                project_root=project_root,
                add_context_docs=["user_guide=docs/user-guide.md"],
                add_completion_checks=["docs/user-guide.md"],
                add_governance_references=["docs/governance/custom-rules.md"],
                completion_update_rule="user guide changes",
            )

            result, exit_code = document_rules.apply_document_rules_update_plan(
                plan,
                project_root=project_root,
                confirmed=True,
                approval_phrase=document_rules.DOCUMENT_RULES_APPROVAL_PHRASE,
            )
            context, errors = document_rules.load_project_context(project_root)

            self.assertEqual(exit_code, 0)
            self.assertEqual(result["schema"], document_rules.DOCUMENT_RULES_APPLY_RESULT_SCHEMA)
            self.assertEqual(result["status"], "applied")
            self.assertTrue(result["write_performed"])
            self.assertEqual(result["target_files"], [".jikuo/project_context.yaml"])
            self.assertEqual(result["applied_operation_count"], 3)
            self.assertEqual(errors, [])
            self.assertEqual(
                context["document_roles"]["user_guide"]["path"],
                "docs/user-guide.md",
            )
            self.assertIn(
                "docs/user-guide.md",
                {
                    item["path"]
                    for item in context["main_document_mounts"][
                        "checked_before_slice_completion"
                    ]
                },
            )
            self.assertIn(
                "docs/governance/custom-rules.md",
                context["main_document_mounts"]["active_mount_authority"],
            )
            self.assertEqual(legacy_before, legacy.read_text(encoding="utf-8"))

    def test_document_rules_apply_cli_uses_reviewed_plan_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/user-guide.md")
            plan = document_rules.build_document_rules_update_plan(
                project_root=project_root,
                add_context_docs=["docs/user-guide.md"],
            )
            plan_path = Path(tmp) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo",
                    "studio",
                    "document-rules",
                    "apply",
                    "--project-root",
                    str(project_root),
                    "--plan-json-file",
                    str(plan_path),
                    "--confirm-apply",
                    "--approval-phrase",
                    document_rules.DOCUMENT_RULES_APPROVAL_PHRASE,
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "applied")
            context, errors = document_rules.load_project_context(project_root)
            self.assertEqual(errors, [])
            self.assertTrue(
                any(
                    record["path"] == "docs/user-guide.md"
                    for record in context["document_roles"].values()
                    if isinstance(record, dict)
                )
            )


if __name__ == "__main__":
    unittest.main()
