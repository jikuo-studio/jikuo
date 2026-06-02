import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo.studio import artifact_assurance, global_status  # noqa: E402


class StudioArtifactAssuranceTests(unittest.TestCase):
    def test_write_assurance_compares_required_planned_and_actual_sets(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = artifact_assurance.build_document_artifact_assurance_report(
                project_root=project_root,
                required_writes=[
                    {"path": "docs/required.md", "reason": "completion check"},
                    {"path": "docs/missing.md", "reason": "registry update"},
                ],
                planned_writes=[
                    {"path": "docs/required.md", "plan_ref": "PLAN-1"},
                    {"path": "docs/planned-only.md", "plan_ref": "PLAN-1"},
                ],
                actual_writes=[
                    {"path": "docs/required.md", "evidence_ref": "git-diff"},
                    {"path": "docs/unplanned.md", "evidence_ref": "git-diff"},
                ],
            )

            write = report["write_assurance"]
            self.assertEqual(report["schema"], artifact_assurance.ARTIFACT_ASSURANCE_SCHEMA)
            self.assertEqual(report["status"], "review")
            self.assertFalse(report["writes_performed"])
            self.assertEqual(write["required_write_count"], 2)
            self.assertEqual(write["planned_write_count"], 2)
            self.assertEqual(write["actual_write_count"], 2)
            self.assertEqual(
                {item["path"] for item in write["required_not_planned"]},
                {"docs/missing.md"},
            )
            self.assertEqual(
                {item["path"] for item in write["required_not_written"]},
                {"docs/missing.md"},
            )
            self.assertEqual(
                {item["path"] for item in write["planned_not_written"]},
                {"docs/planned-only.md"},
            )
            self.assertEqual(
                {item["path"] for item in write["unplanned_written"]},
                {"docs/unplanned.md"},
            )

    def test_read_assurance_reports_required_documents_without_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = artifact_assurance.build_document_artifact_assurance_report(
                project_root=project_root,
                required_reads=[
                    {"path": ".jikuo/project_context.yaml", "role": "project_context"},
                    {"path": "docs/current-work.md", "role": "current_slice_anchor"},
                ],
                read_evidence=[
                    {"path": ".jikuo/project_context.yaml", "evidence_ref": "read-1"}
                ],
            )

            read = report["read_assurance"]
            self.assertEqual(report["status"], "review")
            self.assertEqual(read["required_read_count"], 2)
            self.assertEqual(read["read_evidence_count"], 1)
            self.assertEqual(
                [item["path"] for item in read["required_not_read"]],
                ["docs/current-work.md"],
            )

    def test_no_evidence_supplied_is_not_evaluated_instead_of_fake_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = artifact_assurance.build_document_artifact_assurance_report(
                project_root=project_root,
                required_writes=[{"path": "docs/required.md"}],
            )

            self.assertEqual(report["status"], "not_evaluated")
            self.assertEqual(report["gap_report"]["gap_count"], 0)
            self.assertEqual(report["write_assurance"]["required_write_count"], 1)
            self.assertEqual(report["write_assurance"]["required_not_written"], [])

    def test_completion_check_documents_are_candidates_until_applicable(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = artifact_assurance.build_document_artifact_assurance_report(
                project_root=project_root,
                required_writes=[
                    {
                        "path": "docs/main.md",
                        "role": "completion_check",
                        "obligation_level": artifact_assurance.COMPLETION_CHECK_CANDIDATE,
                        "applicability_status": "not_evaluated",
                    }
                ],
                actual_writes=[{"path": "docs/other.md"}],
            )

            write = report["write_assurance"]
            self.assertEqual(report["status"], "review")
            self.assertEqual(write["completion_check_candidate_count"], 1)
            self.assertEqual(write["required_write_count"], 0)
            self.assertEqual(write["required_not_written"], [])
            self.assertEqual(
                report["gap_report"]["completion_check_not_evaluated_count"],
                1,
            )

    def test_completion_check_candidate_can_become_applicable_required_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()

            report = artifact_assurance.build_document_artifact_assurance_report(
                project_root=project_root,
                required_writes=[
                    {
                        "path": "docs/main.md",
                        "role": "completion_check",
                        "obligation_level": artifact_assurance.COMPLETION_CHECK_CANDIDATE,
                        "applicability_status": "applicable",
                    }
                ],
                actual_writes=[],
            )

            write = report["write_assurance"]
            self.assertEqual(report["status"], "review")
            self.assertEqual(write["required_write_count"], 1)
            self.assertEqual(
                [item["path"] for item in write["required_not_written"]],
                ["docs/main.md"],
            )

    def test_absolute_paths_are_normalized_and_outside_paths_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            inside = project_root / "docs" / "inside.md"
            outside = Path(tmp) / "outside.md"

            report = artifact_assurance.build_document_artifact_assurance_report(
                project_root=project_root,
                planned_writes=[str(inside)],
                actual_writes=[str(outside)],
            )

            self.assertEqual(report["status"], "refused")
            self.assertEqual(
                report["write_assurance"]["planned_write_set"][0]["path"],
                "docs/inside.md",
            )
            self.assertEqual(
                report["gap_report"]["invalid_refs"][0]["code"],
                "path_outside_project_root",
            )

    def test_global_status_exposes_artifact_assurance_projection(self):
        report = global_status.build_global_status(project_root=ROOT)

        assurance = report["summaries"]["artifact_assurance"]
        self.assertEqual(assurance["schema"], artifact_assurance.ARTIFACT_ASSURANCE_SCHEMA)
        self.assertEqual(assurance["status"], "not_evaluated")
        self.assertGreaterEqual(
            assurance["write_assurance"]["completion_check_candidate_count"],
            1,
        )
        self.assertFalse(assurance["writes_performed"])
        action_ids = {item["action_id"] for item in report["available_actions"]}
        panel_ids = {item["panel_id"] for item in report["panels"]}
        self.assertIn("studio.artifact_assurance.review", action_ids)
        self.assertIn("studio.artifact_assurance", panel_ids)
        serialized = json.dumps(assurance, ensure_ascii=False)
        self.assertNotIn("SECRET_PROMPT_VALUE", serialized)


if __name__ == "__main__":
    unittest.main()
