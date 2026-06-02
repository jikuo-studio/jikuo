"""Studio panel registry for the future local JIKUO console."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PANEL_REGISTRY_SCHEMA = "jikuo.studio.panel_registry.v0"


PANEL_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "panel_id": "studio.overview",
        "title": "Overview",
        "domain": "overview",
        "display_order": 10,
        "provider_ref": "jikuo.studio.global_status.v0",
        "summary_key": None,
        "privacy_level": "project_metadata",
        "empty_state": "No global status summary is available yet.",
        "action_refs": [
            "studio.runtime.open_latest_card",
            "studio.configuration.review",
            "studio.policy_management.status",
        ],
    },
    {
        "panel_id": "studio.runtime",
        "title": "Runtime",
        "domain": "runtime",
        "display_order": 20,
        "provider_ref": "runtime_visibility",
        "summary_key": "runtime",
        "privacy_level": "runtime_metadata",
        "empty_state": "Run a JIKUO proposal to create runtime cards.",
        "action_refs": ["studio.runtime.open_latest_card"],
    },
    {
        "panel_id": "studio.configuration",
        "title": "Configuration",
        "domain": "configuration",
        "display_order": 30,
        "provider_ref": "activation_settings + configuration_review",
        "summary_key": "configuration",
        "privacy_level": "project_configuration",
        "empty_state": "No configuration summary is available.",
        "action_refs": [
            "studio.configuration.review",
            "studio.activation_settings.plan_update",
        ],
    },
    {
        "panel_id": "studio.integrations",
        "title": "Integrations",
        "domain": "integrations",
        "display_order": 50,
        "provider_ref": "mcp adapter inventory + hook proof files",
        "summary_key": "integrations",
        "privacy_level": "local_environment_metadata",
        "empty_state": "No integration proof status is available.",
        "action_refs": [],
    },
    {
        "panel_id": "studio.document_mounts",
        "title": "Document Rules",
        "domain": "document_mounts",
        "display_order": 40,
        "provider_ref": ".jikuo/project_context.yaml + docs/registry/mount_sets.yaml",
        "summary_key": "document_mounts",
        "privacy_level": "project_configuration",
        "empty_state": "No document-rule summary is available.",
        "action_refs": [
            "studio.document_mounts.review",
            "studio.document_mounts.plan_update",
        ],
    },
    {
        "panel_id": "studio.artifact_assurance",
        "title": "Round Document Trace",
        "domain": "artifact_assurance",
        "display_order": 45,
        "provider_ref": "jikuo.studio.artifact_assurance.v0",
        "summary_key": "artifact_assurance",
        "privacy_level": "project_metadata",
        "empty_state": "No round document trace projection is available.",
        "action_refs": ["studio.artifact_assurance.review"],
    },
    {
        "panel_id": "studio.policy_management",
        "title": "Policies And Templates",
        "domain": "policy_management",
        "display_order": 60,
        "provider_ref": "policy_management_status",
        "summary_key": "policy_management",
        "privacy_level": "policy_metadata",
        "empty_state": "No policy-management status is available.",
        "action_refs": [
            "studio.policy_management.status",
            "studio.policy_distribution.review",
            "studio.policy_template.plan_publication",
            "studio.policy_template.activate",
            "studio.starter_manifest.plan_publication",
        ],
    },
    {
        "panel_id": "studio.registry",
        "title": "Registry",
        "domain": "registry",
        "display_order": 70,
        "provider_ref": "docs/registry/*.yaml",
        "summary_key": "registry",
        "privacy_level": "project_metadata",
        "empty_state": "No document registry summary is available.",
        "action_refs": [],
    },
    {
        "panel_id": "studio.actions",
        "title": "Actions",
        "domain": "actions",
        "display_order": 80,
        "provider_ref": "jikuo.studio.action_registry.v0",
        "summary_key": None,
        "privacy_level": "project_metadata",
        "empty_state": "No Studio actions are registered.",
        "action_refs": [],
    },
    {
        "panel_id": "studio.diagnostics",
        "title": "Diagnostics",
        "domain": "diagnostics",
        "display_order": 90,
        "provider_ref": "jikuo.studio.global_status.v0.diagnostics",
        "summary_key": None,
        "privacy_level": "project_metadata",
        "empty_state": "No diagnostics are currently reported.",
        "action_refs": [
            "studio.configuration.review",
            "studio.activation_settings.plan_update",
        ],
    },
)


def panel_descriptor(
    definition: dict[str, Any],
    *,
    summaries: dict[str, Any],
    action_ids: set[str],
) -> dict[str, Any]:
    summary_key = definition.get("summary_key")
    status = "available"
    disabled_reason = None
    if summary_key:
        summary = summaries.get(str(summary_key)) or {}
        source_status = summary.get("status")
        if source_status in {"unavailable", "missing", "invalid"}:
            status = "disabled"
            disabled_reason = f"{summary_key} summary is {source_status}"
        elif source_status == "degraded":
            status = "degraded"
    action_refs = list(definition.get("action_refs") or [])
    missing_action_refs = [ref for ref in action_refs if ref not in action_ids]
    if missing_action_refs:
        status = "degraded" if status == "available" else status
    return {
        "panel_id": definition["panel_id"],
        "title": definition["title"],
        "domain": definition["domain"],
        "display_order": definition["display_order"],
        "provider_ref": definition["provider_ref"],
        "summary_key": summary_key,
        "privacy_level": definition["privacy_level"],
        "empty_state": definition["empty_state"],
        "action_refs": action_refs,
        "missing_action_refs": missing_action_refs,
        "status": status,
        "disabled_reason": disabled_reason,
        "write_boundary": "read_only_projection",
    }


def build_panel_registry(
    *,
    project_root: Path | None = None,
    summaries: dict[str, Any] | None = None,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    summaries = summaries or {}
    actions = actions or []
    action_ids = {str(item.get("action_id")) for item in actions if item.get("action_id")}
    panels = [
        panel_descriptor(definition, summaries=summaries, action_ids=action_ids)
        for definition in sorted(PANEL_DEFINITIONS, key=lambda item: item["display_order"])
    ]
    return {
        "schema": PANEL_REGISTRY_SCHEMA,
        "schema_version": PANEL_REGISTRY_SCHEMA,
        "status": "available",
        "project_root": str(project_root) if project_root else None,
        "panel_count": len(panels),
        "available_panel_count": sum(1 for item in panels if item.get("status") == "available"),
        "degraded_panel_count": sum(1 for item in panels if item.get("status") == "degraded"),
        "disabled_panel_count": sum(1 for item in panels if item.get("status") == "disabled"),
        "panels": panels,
        "source_refs": [
            "src/jikuo/studio/panels.py",
            "src/jikuo/studio/actions.py",
            "src/jikuo/studio/global_status.py",
        ],
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_render_frontend",
            "does_not_execute_actions",
            "does_not_mutate_project_state",
        ],
    }
