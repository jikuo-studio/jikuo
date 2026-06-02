import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo.studio import project_files  # noqa: E402


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
                "  customer_guide:",
                '    path: "docs/customer-guide.md"',
                "    required: false",
                "main_document_mounts:",
                '  canonical_path_root: "."',
                "  active_mount_authority:",
                '    - "docs/governance/custom-rules.md"',
                "  checked_before_slice_completion:",
                '    - path: "docs/customer-guide.md"',
                '      update_required_when: "customer guide changes"',
                "  unchanged_report_required: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def touch(root: Path, rel: str, text: str = "# doc\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class StudioProjectFilesTests(unittest.TestCase):
    def test_project_file_inventory_reports_membership_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            project_root.mkdir()
            write_project_context(project_root)
            touch(project_root, "docs/customer-guide.md")
            touch(project_root, "docs/governance/custom-rules.md")
            touch(project_root, ".jikuo/runtime/history/card.md")
            touch(project_root, ".jikuo/policies/approved/POLICY-test.yaml")
            touch(project_root, "src/app.py", "print('not a document candidate')\n")
            before = (project_root / ".jikuo" / "project_context.yaml").read_text(
                encoding="utf-8"
            )

            inventory = project_files.build_project_file_inventory(
                project_root=project_root
            )
            by_path = {item["path"]: item for item in inventory["items"]}

            self.assertEqual(inventory["schema"], project_files.PROJECT_FILE_INVENTORY_SCHEMA)
            self.assertEqual(inventory["status"], "available")
            self.assertFalse(inventory["writes_performed"])
            self.assertIn(".jikuo/project_context.yaml", by_path)
            self.assertIn("docs/customer-guide.md", by_path)
            self.assertNotIn(".jikuo/runtime/history/card.md", by_path)
            self.assertNotIn(".jikuo/policies/approved/POLICY-test.yaml", by_path)
            self.assertNotIn("src/app.py", by_path)
            guide = by_path["docs/customer-guide.md"]["document_rules_membership"]
            self.assertTrue(guide["is_context_document"])
            self.assertTrue(guide["is_completion_check"])
            self.assertEqual(guide["context_role_refs"], ["customer_guide"])
            custom = by_path["docs/governance/custom-rules.md"][
                "document_rules_membership"
            ]
            self.assertTrue(custom["is_governance_reference"])
            self.assertEqual(
                before,
                (project_root / ".jikuo" / "project_context.yaml").read_text(
                    encoding="utf-8"
                ),
            )


if __name__ == "__main__":
    unittest.main()
