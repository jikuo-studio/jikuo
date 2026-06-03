import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo import companion_write_obligations  # noqa: E402


class CompanionWriteObligationsTests(unittest.TestCase):
    def test_code_change_projects_atom_chain_and_active_work_order_obligations(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            report = companion_write_obligations.project_required_companion_writes(
                project_root=project_root,
                observed_actual_writes=[
                    {
                        "path": "src/jikuo/example.py",
                        "operation": "modified",
                        "source_kind": "git_diff",
                    }
                ],
                document_roles={
                    "mvp_work_receipt_configuration_work_order": {
                        "path": "docs/work_orders/SPRINT_050_WO-PER-JIKUO-MVP-01_work_receipt_and_configuration_mvp.md"
                    }
                },
            )

            paths = {
                item["path"] for item in report["required_companion_write_set"]
            }

            self.assertEqual(report["schema"], companion_write_obligations.COMPANION_WRITE_OBLIGATION_SCHEMA)
            self.assertEqual(report["status"], "ok")
            self.assertIn("docs/registry/capabilities.yaml", paths)
            self.assertIn("docs/registry/scenario_chains.yaml", paths)
            self.assertIn("docs/registry/work_orders.yaml", paths)
            self.assertIn(
                "docs/work_orders/SPRINT_050_WO-PER-JIKUO-MVP-01_work_receipt_and_configuration_mvp.md",
                paths,
            )
            for item in report["required_companion_write_set"]:
                self.assertEqual(item["evidence_kind"], "required_companion_write")
                self.assertEqual(item["applicability_status"], "applicable")
                self.assertFalse(item.get("writes_performed", False))

    def test_root_scratch_file_does_not_project_governance_obligation(self):
        report = companion_write_obligations.project_required_companion_writes(
            observed_actual_writes=[
                {
                    "path": "test.md",
                    "operation": "added",
                    "source_kind": "git_diff",
                }
            ],
        )

        self.assertEqual(report["required_companion_write_set"], [])
        self.assertEqual(report["trigger_count"], 0)
        self.assertEqual(report["ignored_item_count"], 1)
        self.assertEqual(
            report["ignored_items"][0]["reason"],
            "no_companion_write_trigger",
        )

    def test_new_insight_document_projects_insights_registry_obligation(self):
        report = companion_write_obligations.project_required_companion_writes(
            observed_actual_writes=[
                {
                    "path": "docs/insights/INSIGHT-2026-06-03-example.md",
                    "operation": "added",
                }
            ],
        )

        paths = {
            item["path"] for item in report["required_companion_write_set"]
        }

        self.assertIn("docs/registry/registry_index.yaml", paths)
        self.assertIn("docs/registry/mount_sets.yaml", paths)
        self.assertIn("docs/insights/insights_registry.yaml", paths)

    def test_registry_change_projects_related_registry_consistency(self):
        report = companion_write_obligations.project_required_companion_writes(
            observed_actual_writes=[
                {
                    "path": "docs/registry/capabilities.yaml",
                    "operation": "modified",
                }
            ],
        )

        paths = {
            item["path"] for item in report["required_companion_write_set"]
        }

        self.assertNotIn("docs/registry/capabilities.yaml", paths)
        self.assertIn("docs/registry/scenario_chains.yaml", paths)
        self.assertIn("docs/registry/work_orders.yaml", paths)


if __name__ == "__main__":
    unittest.main()
