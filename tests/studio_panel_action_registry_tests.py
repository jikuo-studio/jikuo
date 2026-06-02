import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jikuo.studio import actions, global_status, panels  # noqa: E402


REQUIRED_ACTION_FIELDS = {
    "action_id",
    "domain",
    "title",
    "write_mode",
    "plan_surface",
    "apply_surface",
    "write_effect",
    "approval_required",
    "source_ref",
    "status",
    "disabled_reason",
    "non_effects",
}

REQUIRED_PANEL_FIELDS = {
    "panel_id",
    "provider_ref",
    "empty_state",
    "privacy_level",
    "action_refs",
    "status",
    "disabled_reason",
    "write_boundary",
}


class StudioPanelActionRegistryTests(unittest.TestCase):
    def test_action_registry_exposes_guarded_boundaries_without_writes(self):
        report = global_status.build_global_status(project_root=ROOT)
        registry = actions.build_action_registry(
            project_root=ROOT,
            summaries=report["summaries"],
        )

        self.assertEqual(registry["schema"], actions.ACTION_REGISTRY_SCHEMA)
        self.assertFalse(registry["writes_performed"])
        self.assertFalse(registry["write_allowed_by_command"])
        self.assertGreaterEqual(registry["action_count"], 8)
        action_by_id = {item["action_id"]: item for item in registry["actions"]}
        for action in registry["actions"]:
            self.assertTrue(
                REQUIRED_ACTION_FIELDS.issubset(action.keys()),
                f"missing required action fields for {action.get('action_id')}: "
                f"{REQUIRED_ACTION_FIELDS - set(action.keys())}",
            )

        activation = action_by_id["studio.activation_settings.plan_update"]
        self.assertEqual(activation["write_mode"], "no-write-plan")
        self.assertEqual(activation["apply_surface"], "jikuo.apply_activation_settings_update")
        self.assertTrue(activation["approval_required"])
        self.assertIn("does_not_apply_without_approval_phrase", activation["non_effects"])

        runtime = action_by_id["studio.runtime.open_latest_card"]
        self.assertEqual(runtime["write_mode"], "no-write")
        self.assertFalse(runtime["approval_required"])

        document_review = action_by_id["studio.document_mounts.review"]
        self.assertEqual(document_review["domain"], "document_mounts")
        self.assertEqual(document_review["title"], "Review document rules")
        self.assertEqual(document_review["write_mode"], "no-write")
        self.assertFalse(document_review["approval_required"])

        document_plan = action_by_id["studio.document_mounts.plan_update"]
        self.assertEqual(document_plan["title"], "Plan document-rule update")
        self.assertEqual(document_plan["write_mode"], "no-write-plan")
        self.assertEqual(
            document_plan["plan_surface"],
            "python -B -m jikuo studio document-rules plan",
        )
        self.assertEqual(
            document_plan["apply_surface"],
            "python -B -m jikuo studio document-rules apply",
        )
        self.assertTrue(document_plan["approval_required"])
        self.assertEqual(document_plan["status"], "available")

    def test_panel_registry_binds_panels_to_valid_action_refs(self):
        report = global_status.build_global_status(project_root=ROOT)
        registry = panels.build_panel_registry(
            project_root=ROOT,
            summaries=report["summaries"],
            actions=report["available_actions"],
        )

        self.assertEqual(registry["schema"], panels.PANEL_REGISTRY_SCHEMA)
        self.assertFalse(registry["writes_performed"])
        self.assertFalse(registry["write_allowed_by_command"])
        panel_by_id = {item["panel_id"]: item for item in registry["panels"]}

        self.assertIn("studio.overview", panel_by_id)
        self.assertIn("studio.runtime", panel_by_id)
        self.assertIn("studio.configuration", panel_by_id)
        self.assertIn("studio.document_mounts", panel_by_id)
        self.assertEqual(panel_by_id["studio.document_mounts"]["title"], "Document Rules")
        self.assertIn("studio.policy_management", panel_by_id)
        self.assertIn("studio.actions", panel_by_id)
        self.assertIn("studio.diagnostics", panel_by_id)
        for panel in registry["panels"]:
            self.assertTrue(
                REQUIRED_PANEL_FIELDS.issubset(panel.keys()),
                f"missing required panel fields for {panel.get('panel_id')}: "
                f"{REQUIRED_PANEL_FIELDS - set(panel.keys())}",
            )
            self.assertIn("provider_ref", panel)
            self.assertIn("empty_state", panel)
            self.assertIn("privacy_level", panel)
            self.assertEqual(panel["missing_action_refs"], [])

    def test_global_status_consumes_panel_and_action_registries(self):
        report = global_status.build_global_status(project_root=ROOT)

        self.assertEqual(report["panel_registry"]["schema"], panels.PANEL_REGISTRY_SCHEMA)
        self.assertEqual(report["action_registry"]["schema"], actions.ACTION_REGISTRY_SCHEMA)
        self.assertEqual(
            report["available_actions"],
            report["action_registry"]["actions"],
        )
        self.assertEqual(report["panels"], report["panel_registry"]["panels"])
        source_refs = {item["ref"] for item in report["source_refs"]}
        self.assertIn("src/jikuo/studio/panels.py", source_refs)
        self.assertIn("src/jikuo/studio/actions.py", source_refs)

    def test_registry_serialization_does_not_include_raw_prompt_or_transcript(self):
        report = global_status.build_global_status(project_root=ROOT)
        serialized = json.dumps(
            {
                "panels": report["panel_registry"],
                "actions": report["action_registry"],
            },
            ensure_ascii=False,
        )

        self.assertNotIn("SECRET_PROMPT_VALUE", serialized)
        self.assertNotIn("raw transcript text", serialized)


if __name__ == "__main__":
    unittest.main()
