import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo import configuration_review, doctor, policy_templates, starter_policies  # noqa: E402
from jikuo.studio import document_rules, global_status  # noqa: E402


DEMO_ROOT = ROOT / "examples" / "demo_project"


class DemoProjectTests(unittest.TestCase):
    def test_demo_project_context_references_existing_public_files(self):
        context_path = DEMO_ROOT / ".jikuo" / "project_context.yaml"
        self.assertTrue(context_path.is_file())
        context = policy_templates.read_yaml_subset(context_path)

        self.assertEqual(context["schema_version"], "jikuo.project_context.v0")
        self.assertEqual(context["project"]["project_id"], "jikuo_demo_project")
        for role in context["document_roles"].values():
            path_ref = role.get("path")
            if path_ref:
                self.assertTrue((DEMO_ROOT / path_ref).is_file(), path_ref)
        for item in context["main_document_mounts"]["checked_before_slice_completion"]:
            self.assertTrue((DEMO_ROOT / item["path"]).is_file(), item["path"])

        for path in DEMO_ROOT.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("D:\\", text)
                self.assertNotIn("C:\\Users", text)

    def test_demo_project_first_run_is_realistic_not_preconfigured(self):
        report = configuration_review.build_configuration_review(project_root=DEMO_ROOT)
        first_run = report["first_run"]

        self.assertEqual(first_run["status"], "needs_configuration")
        required = {item["key"]: item for item in first_run["required_steps"]}
        self.assertEqual(required["project_context"]["status"], "complete")
        self.assertEqual(required["starter_policies"]["status"], "needs_review")
        self.assertEqual(required["activation_settings"]["status"], "needs_review")
        self.assertEqual(first_run["blocker_count"], 2)

        plan = starter_policies.build_starter_init_plan(project_root=DEMO_ROOT)
        self.assertEqual(plan["status"], "review")
        self.assertTrue(plan["would_create_project_state"])
        self.assertGreaterEqual(len(plan["starter_policies"]), 1)

    def test_demo_project_studio_and_doctor_read_models_are_usable(self):
        status = global_status.build_global_status(project_root=DEMO_ROOT)
        document_mounts = status["summaries"]["document_mounts"]

        self.assertEqual(document_mounts["status"], "available")
        self.assertEqual(document_mounts["missing_required_role_count"], 0)
        self.assertEqual(document_mounts["checked_document_count"], 2)

        doctor_report = doctor.build_doctor_report(project_root=DEMO_ROOT)
        self.assertEqual(doctor_report["source_read_model"]["schema"], global_status.GLOBAL_STATUS_SCHEMA)
        self.assertFalse(doctor_report["writes_performed"])
        first_run_check = next(
            item
            for item in doctor_report["checks"]
            if item["check_id"] == "first_run_readiness"
        )
        self.assertEqual(first_run_check["status"], "action_required")

    def test_demo_project_document_rules_plan_can_add_optional_document(self):
        plan = document_rules.build_document_rules_update_plan(
            project_root=DEMO_ROOT,
            add_context_docs=["docs/workflow-notes.md"],
        )

        self.assertEqual(plan["schema"], document_rules.DOCUMENT_RULES_PLAN_SCHEMA)
        self.assertEqual(plan["status"], "review")
        self.assertFalse(plan["writes_performed"])
        self.assertEqual(plan["change_count"], 1)
        additions = plan["proposed_changes"]["document_role_additions"]
        self.assertEqual(additions[0]["path"], "docs/workflow-notes.md")


if __name__ == "__main__":
    unittest.main()
