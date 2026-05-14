import json
import shutil
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "src" / "jikuo" / "policy_templates.py"
TEMP_ROOT = ROOT / "tmp" / "jikuo_policy_templates_tests"


@contextmanager
def temp_project_dir():
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEMP_ROOT / f"case_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def write_policy(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                'policy_id: "POLICY-task-scope-control-before-packaging"',
                "version: 1",
                'status: "active_report_only"',
                'title: "Task scope control before packaging"',
                'scenario_package: "engineering_governance"',
                "source_refs:",
                '  - type: "user_natural_language"',
                '    ref: "user_policy:task_scope_control"',
                "scope_control:",
                '  purpose: "prevent scope expansion"',
                "  required_method:",
                '    - "mount latest todo map and previous todo map"',
                "triggers:",
                '  - trigger_id: "TRG-task-start"',
                '    type: "task_lifecycle_event"',
                '    event: "task_start"',
                "conditions:",
                '  - condition_id: "COND-task-type"',
                '    type: "task_type_is"',
                '    value: "work_order_delivery"',
                "required_actions:",
                '  - action_id: "ACT-declare-scope"',
                '    type: "declare_task_scope_freeze_and_todo_delta"',
                "required_evidence:",
                '  - evidence_id: "EVD-scope"',
                '    type: "task_scope_control_evidence"',
                '    satisfies_action: "ACT-declare-scope"',
                "enforcement:",
                '  phase: "report_only"',
                '  level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_project_context(root: Path, *, latest_path: str, previous_path: str) -> None:
    context_path = root / ".jikuo" / "project_context.yaml"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(
        "\n".join(
            [
                'schema_version: "jikuo.project_context.v0"',
                "project:",
                '  project_id: "template_import_fixture"',
                '  project_type: "test"',
                '  project_root_policy: "bindings_must_resolve_inside_project_root"',
                "document_roles:",
                "  latest_todo_map:",
                f'    path: "{latest_path}"',
                "    required: true",
                "  previous_todo_map:",
                f'    path: "{previous_path}"',
                "    required: true",
                "directory_roles:",
                "  work_orders:",
                '    path: "docs/work_orders"',
                "",
            ]
        ),
        encoding="utf-8",
    )


class PolicyTemplateTests(unittest.TestCase):
    def test_repository_previous_todo_map_is_disabled_until_snapshot_rotation_exists(self):
        context = (ROOT / ".jikuo" / "project_context.yaml").read_text(encoding="utf-8")
        self.assertIn("previous_todo_map:", context)
        self.assertIn("status: \"not_implemented_in_v0\"", context)
        self.assertIn("replacement: \"future_snapshot_rotation\"", context)
        self.assertNotIn(
            'previous_todo_map:\n    path: "docs/governance/jikuo_productization_task_map.md"',
            context,
        )

    def test_packaged_starter_templates_do_not_expose_private_source_refs(self):
        template_root = ROOT / "src" / "jikuo" / "policy_templates" / "engineering_governance"
        for template_path in template_root.glob("*.yaml"):
            with self.subTest(template=template_path.name):
                text = template_path.read_text(encoding="utf-8")
                self.assertNotIn("NarrativeSystem", text)
                self.assertNotIn("D:\\", text)
                self.assertNotIn("origin_policy", text)
                self.assertNotIn("user_natural_language", text)
                self.assertIn('source_project_ref: "redacted"', text)
                self.assertIn('local_path: "redacted"', text)

    def test_inspect_source_lists_approved_policy_candidates(self):
        with temp_project_dir() as root:
            source_dir = root / "approved"
            source_dir.mkdir()
            write_policy(source_dir / "POLICY-task-scope-control-before-packaging.yaml")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "inspect-source",
                    "--source-dir",
                    str(source_dir),
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
            self.assertEqual(report["candidate_count"], 1)
            self.assertEqual(
                report["candidates"][0]["policy_id"],
                "POLICY-task-scope-control-before-packaging",
            )

    def test_plan_extract_is_no_write_and_infers_todo_bindings(self):
        with temp_project_dir() as root:
            source_policy = root / "POLICY-task-scope-control-before-packaging.yaml"
            write_policy(source_policy)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "plan-extract",
                    "--source-policy",
                    str(source_policy),
                    "--source-project-ref",
                    "IncubatingPrivateProject",
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
            self.assertFalse(report["writes_performed"])
            template = report["proposed_template"]
            self.assertEqual(template["schema_version"], "jikuo.policy_template.v0")
            serialized_template = json.dumps(template, ensure_ascii=False)
            self.assertEqual(template["source"]["source_project_ref"], "redacted")
            self.assertEqual(template["source"]["privacy"]["local_path"], "redacted")
            self.assertEqual(template["source"]["privacy"]["project_identity"], "redacted")
            self.assertNotIn("NarrativeSystem", serialized_template)
            self.assertNotIn("IncubatingPrivateProject", serialized_template)
            self.assertNotIn(str(source_policy), serialized_template)
            self.assertNotIn("origin_policy", serialized_template)
            self.assertNotIn("user_natural_language", serialized_template)
            role_refs = {item["role_ref"] for item in template["required_bindings"]}
            self.assertIn("role://document/latest_todo_map", role_refs)
            self.assertIn("role://document/previous_todo_map", role_refs)
            self.assertEqual(
                template["template_policy"]["scope_control"]["purpose"],
                "prevent scope expansion",
            )

    def test_export_requires_confirmation_and_approval(self):
        with temp_project_dir() as root:
            source_policy = root / "POLICY-task-scope-control-before-packaging.yaml"
            target_dir = root / "templates"
            write_policy(source_policy)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "export-template",
                    "--source-policy",
                    str(source_policy),
                    "--target-dir",
                    str(target_dir),
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
            self.assertFalse(report["write_performed"])
            self.assertIn("missing technical confirmation flag", report["refusal_reasons"])
            self.assertFalse(target_dir.exists())

    def test_export_writes_template_without_activating_project_policy(self):
        with temp_project_dir() as root:
            source_policy = root / "POLICY-task-scope-control-before-packaging.yaml"
            target_dir = root / "templates"
            write_policy(source_policy)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "export-template",
                    "--source-policy",
                    str(source_policy),
                    "--target-dir",
                    str(target_dir),
                    "--confirm-export-template",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
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
            self.assertTrue(report["write_performed"])
            written_path = Path(report["written_paths"][0])
            self.assertTrue(written_path.is_file())
            self.assertFalse((root / ".jikuo" / "policies").exists())
            self.assertEqual(
                report["post_write_verification"]["template_schema"],
                "jikuo.policy_template.v0",
            )
            written_text = written_path.read_text(encoding="utf-8")
            self.assertNotIn(str(source_policy), written_text)
            self.assertNotIn("origin_policy", written_text)
            self.assertNotIn("user_natural_language", written_text)

    def test_plan_import_reports_missing_project_context_bindings(self):
        with temp_project_dir() as root:
            source_policy = root / "POLICY-task-scope-control-before-packaging.yaml"
            target_dir = root / "templates"
            write_policy(source_policy)
            export_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "export-template",
                    "--source-policy",
                    str(source_policy),
                    "--target-dir",
                    str(target_dir),
                    "--confirm-export-template",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(export_completed.returncode, 0, export_completed.stderr)
            export_report = json.loads(export_completed.stdout)
            template_path = export_report["written_paths"][0]

            import_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "plan-import",
                    "--template",
                    template_path,
                    "--project-root",
                    str(root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(import_completed.returncode, 0, import_completed.stderr)
            report = json.loads(import_completed.stdout)
            self.assertEqual(report["status"], "missing_binding")
            self.assertEqual(report["project_context_status"], "missing")
            self.assertFalse(report["writes_performed"])
            self.assertTrue(report["binding_status"])
            self.assertFalse((root / ".jikuo" / "policies").exists())

    def test_plan_import_resolves_project_context_bindings_without_write(self):
        with temp_project_dir() as root:
            source_policy = root / "POLICY-task-scope-control-before-packaging.yaml"
            target_dir = root / "templates"
            docs_dir = root / "docs"
            docs_dir.mkdir()
            (docs_dir / "latest.md").write_text("latest", encoding="utf-8")
            (docs_dir / "previous.md").write_text("previous", encoding="utf-8")
            write_project_context(
                root,
                latest_path="docs/latest.md",
                previous_path="docs/previous.md",
            )
            write_policy(source_policy)
            export_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "export-template",
                    "--source-policy",
                    str(source_policy),
                    "--target-dir",
                    str(target_dir),
                    "--confirm-export-template",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(export_completed.returncode, 0, export_completed.stderr)
            template_path = json.loads(export_completed.stdout)["written_paths"][0]

            import_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "plan-import",
                    "--template",
                    template_path,
                    "--project-root",
                    str(root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(import_completed.returncode, 0, import_completed.stderr)
            report = json.loads(import_completed.stdout)
            self.assertEqual(report["status"], "review")
            self.assertEqual(report["project_context_status"], "present")
            self.assertFalse(report["writes_performed"])
            self.assertEqual(
                {item["status"] for item in report["binding_status"]},
                {"resolved"},
            )
            self.assertEqual(
                report["resolved_policy"]["schema"],
                "jikuo.resolved_policy.v0",
            )
            preview = report["resolved_policy_preview"]
            self.assertEqual(
                preview["template_ref"],
                "POLICYTEMPLATE-local-policy-task-scope-control-before-packaging",
            )
            self.assertEqual(preview["project_context_ref"], ".jikuo/project_context.yaml")
            self.assertFalse((root / ".jikuo" / "policies").exists())

    def test_plan_import_reports_unsafe_project_context_path(self):
        with temp_project_dir() as root:
            source_policy = root / "POLICY-task-scope-control-before-packaging.yaml"
            target_dir = root / "templates"
            write_project_context(
                root,
                latest_path="../outside.md",
                previous_path="docs/previous.md",
            )
            (root / "docs").mkdir()
            (root / "docs" / "previous.md").write_text("previous", encoding="utf-8")
            write_policy(source_policy)
            export_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "export-template",
                    "--source-policy",
                    str(source_policy),
                    "--target-dir",
                    str(target_dir),
                    "--confirm-export-template",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(export_completed.returncode, 0, export_completed.stderr)
            template_path = json.loads(export_completed.stdout)["written_paths"][0]

            import_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "plan-import",
                    "--template",
                    template_path,
                    "--project-root",
                    str(root),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(import_completed.returncode, 0, import_completed.stderr)
            report = json.loads(import_completed.stdout)
            self.assertEqual(report["status"], "missing_binding")
            statuses = {
                item["role_ref"]: item["status"]
                for item in report["binding_status"]
            }
            self.assertEqual(
                statuses["role://document/latest_todo_map"],
                "unsafe_binding",
            )
            self.assertFalse((root / ".jikuo" / "policies").exists())

    def test_activate_template_requires_confirmation_and_approval(self):
        with temp_project_dir() as root:
            source_policy = root / "POLICY-task-scope-control-before-packaging.yaml"
            target_dir = root / "templates"
            docs_dir = root / "docs"
            docs_dir.mkdir()
            (docs_dir / "latest.md").write_text("latest", encoding="utf-8")
            (docs_dir / "previous.md").write_text("previous", encoding="utf-8")
            write_project_context(
                root,
                latest_path="docs/latest.md",
                previous_path="docs/previous.md",
            )
            write_policy(source_policy)
            export_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "export-template",
                    "--source-policy",
                    str(source_policy),
                    "--target-dir",
                    str(target_dir),
                    "--confirm-export-template",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(export_completed.returncode, 0, export_completed.stderr)
            template_path = json.loads(export_completed.stdout)["written_paths"][0]

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "activate-template",
                    "--template",
                    template_path,
                    "--project-root",
                    str(root),
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
            self.assertFalse(report["write_performed"])
            self.assertIn("missing_confirmation_flag", report["refusal_reasons"])
            self.assertIn("approval_evidence_missing", report["refusal_reasons"])
            self.assertFalse((root / ".jikuo" / "policies").exists())

    def test_activate_template_writes_resolved_policy_after_approval(self):
        with temp_project_dir() as root:
            source_policy = root / "POLICY-task-scope-control-before-packaging.yaml"
            target_dir = root / "templates"
            docs_dir = root / "docs"
            docs_dir.mkdir()
            (docs_dir / "latest.md").write_text("latest", encoding="utf-8")
            (docs_dir / "previous.md").write_text("previous", encoding="utf-8")
            write_project_context(
                root,
                latest_path="docs/latest.md",
                previous_path="docs/previous.md",
            )
            write_policy(source_policy)
            export_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "export-template",
                    "--source-policy",
                    str(source_policy),
                    "--target-dir",
                    str(target_dir),
                    "--confirm-export-template",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(export_completed.returncode, 0, export_completed.stderr)
            template_path = json.loads(export_completed.stdout)["written_paths"][0]

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOL),
                    "activate-template",
                    "--template",
                    template_path,
                    "--project-root",
                    str(root),
                    "--confirm-activate-template",
                    "--approval-phrase",
                    "<exact user phrase as spoken>",
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
            self.assertTrue(report["write_performed"])
            self.assertEqual(report["policy_ref"], "POLICY-task-scope-control-before-packaging")
            self.assertTrue(report["post_write_verification"]["policy_active"])
            approved_path = (
                root
                / ".jikuo"
                / "policies"
                / "approved"
                / "POLICY-task-scope-control-before-packaging.yaml"
            )
            self.assertTrue(approved_path.is_file())
            approved_text = approved_path.read_text(encoding="utf-8")
            self.assertIn('template_ref: "POLICYTEMPLATE-local-policy-task-scope-control-before-packaging"', approved_text)
            self.assertIn("resolved_bindings:", approved_text)
            self.assertTrue((root / ".jikuo" / "policies" / "manifest.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
