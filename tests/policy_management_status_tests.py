import json
import shutil
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from jikuo import policy_management_status  # noqa: E402


TEMP_ROOT = ROOT / "tmp" / "jikuo_policy_management_status_tests"


@contextmanager
def temp_project_dir():
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEMP_ROOT / f"case_{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def write_policy_store(root: Path, *, policy_id: str, title: str) -> None:
    store = root / ".jikuo" / "policies"
    approved = store / "approved"
    approved.mkdir(parents=True, exist_ok=True)
    (approved / f"{policy_id}.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.configurable_rule_policy.v0"',
                f'policy_id: "{policy_id}"',
                "version: 1",
                'status: "active_report_only"',
                f'title: "{title}"',
                'scenario_package: "engineering_governance"',
                "source_refs:",
                '  - type: "test_fixture"',
                f'    ref: "tests:{policy_id}"',
                "triggers:",
                '  - trigger_id: "TRG-task-start"',
                '    type: "task_lifecycle_event"',
                '    event: "task_start"',
                "conditions: []",
                "required_actions:",
                '  - action_id: "ACT-review"',
                '    type: "review"',
                "required_evidence:",
                '  - evidence_id: "EVD-review"',
                '    type: "review_evidence"',
                '    satisfies_action: "ACT-review"',
                "enforcement:",
                '  phase: "report_only"',
                '  level: "review_required"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (store / "manifest.yaml").write_text(
        "\n".join(
            [
                'schema_version: "jikuo.policy_store_manifest.v0"',
                'project_id: "policy_management_status_fixture"',
                'store_root: ".jikuo/policies"',
                "active_policy_refs:",
                f'  - policy_id: "{policy_id}"',
                "    version: 1",
                f'    path: ".jikuo/policies/approved/{policy_id}.yaml"',
                "proposal_refs: []",
                "deprecated_policy_refs: []",
                "superseded_policy_refs: []",
                'last_updated_at: "2026-05-31T00:00:00Z"',
                "compatibility:",
                '  unknown_fields: "preserve"',
                '  writer: "test_fixture"',
                "",
            ]
        ),
        encoding="utf-8",
    )


class PolicyManagementStatusTests(unittest.TestCase):
    def test_status_read_model_links_active_policy_to_package_template_and_starter_pack(self):
        with temp_project_dir() as project_root:
            write_policy_store(
                project_root,
                policy_id="POLICY-task-scope-control-before-packaging",
                title="Task scope control before packaging",
            )

            report = policy_management_status.build_policy_management_status(
                project_root=project_root,
                starter_pack_id="engineering_governance",
            )

        self.assertEqual(report["schema"], "jikuo.policy_management_status.v0")
        self.assertFalse(report["writes_performed"])
        self.assertEqual(report["policy_store"]["active_policy_count"], 1)
        self.assertGreaterEqual(report["package_templates"]["template_count"], 1)
        self.assertEqual(report["starter_packs"]["pack_count"], 1)
        self.assertEqual(
            report["summary_counts"]["active_policy_with_package_template_count"],
            1,
        )
        distribution = report["active_policy_distribution"][0]
        self.assertEqual(distribution["distribution_state"], "starter_pack_available")
        self.assertTrue(distribution["package_template_refs"])
        self.assertEqual(
            distribution["starter_pack_refs"][0]["pack_id"],
            "engineering_governance",
        )

    def test_policy_management_status_cli_returns_json_and_markdown(self):
        with temp_project_dir() as project_root:
            write_policy_store(
                project_root,
                policy_id="POLICY-task-scope-control-before-packaging",
                title="Task scope control before packaging",
            )
            json_completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "jikuo.policy_management_status",
                    "status",
                    "--project-root",
                    str(project_root),
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
                    "jikuo.policy_management_status",
                    "status",
                    "--project-root",
                    str(project_root),
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
        self.assertEqual(report["schema"], "jikuo.policy_management_status.v0")
        self.assertEqual(markdown_completed.returncode, 0, markdown_completed.stderr)
        self.assertIn("# JIKUO Policy Management Status", markdown_completed.stdout)
        self.assertIn("starter_pack_available", markdown_completed.stdout)


if __name__ == "__main__":
    unittest.main()
