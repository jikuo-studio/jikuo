"""Studio action registry for UI-facing JIKUO operations.

The registry is intentionally declarative. It names existing no-write and
guarded boundaries so a frontend can render actions without owning governance
logic or writing canonical state directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .. import runtime_visibility
else:  # pragma: no cover - direct script fallback for ad hoc inspection
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from jikuo import runtime_visibility


ACTION_REGISTRY_SCHEMA = "jikuo.studio.action_registry.v0"


def action_descriptor(
    *,
    action_id: str,
    domain: str,
    title: str,
    write_mode: str,
    plan_surface: str,
    apply_surface: str | None,
    write_effect: str,
    approval_required: bool,
    source_ref: str,
    status: str = "available",
    disabled_reason: str | None = None,
    non_effects: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "domain": domain,
        "title": title,
        "write_mode": write_mode,
        "plan_surface": plan_surface,
        "apply_surface": apply_surface,
        "write_effect": write_effect,
        "approval_required": approval_required,
        "source_ref": source_ref,
        "status": status,
        "disabled_reason": disabled_reason,
        "non_effects": non_effects or [],
    }


def registered_action_descriptors(
    *,
    summaries: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return the currently registered Studio actions.

    Future backend features should add descriptors here, or provide an
    equivalent contribution function that is merged by ``build_action_registry``.
    This keeps the UI dynamic at read time while preserving explicit product
    registration for user-facing controls.
    """

    summaries = summaries or {}
    activation = summaries.get("activation") or {}
    configuration = summaries.get("configuration") or {}
    document_mounts = summaries.get("document_mounts") or {}
    policy_management = summaries.get("policy_management") or {}
    runtime = summaries.get("runtime") or {}

    activation_disabled = None
    if activation.get("status") == "unavailable":
        activation_disabled = "activation settings summary is unavailable"

    configuration_disabled = None
    if configuration.get("status") == "unavailable":
        configuration_disabled = "configuration summary is unavailable"

    document_mounts_disabled = None
    if document_mounts.get("status") == "unavailable":
        document_mounts_disabled = "document-mount summary is unavailable"

    policy_disabled = None
    if policy_management.get("status") == "unavailable":
        policy_disabled = "policy-management summary is unavailable"

    runtime_disabled = None
    if runtime.get("status") == "unavailable":
        runtime_disabled = "runtime visibility summary is unavailable"

    return [
        action_descriptor(
            action_id="studio.configuration.review",
            domain="configuration",
            title="Review JIKUO configuration",
            write_mode="no-write",
            plan_surface="jikuo.get_configuration_status",
            apply_surface=None,
            write_effect="none",
            approval_required=False,
            source_ref="src/jikuo/configuration_review.py",
            status="disabled" if configuration_disabled else "available",
            disabled_reason=configuration_disabled,
            non_effects=["does_not_write_project_state"],
        ),
        action_descriptor(
            action_id="studio.activation_settings.plan_update",
            domain="configuration",
            title="Plan activation settings update",
            write_mode="no-write-plan",
            plan_surface="jikuo.plan_activation_settings_update",
            apply_surface="jikuo.apply_activation_settings_update",
            write_effect=".jikuo/activation_settings.yaml only after guarded apply",
            approval_required=True,
            source_ref="src/jikuo/activation_settings.py",
            status="disabled" if activation_disabled else "available",
            disabled_reason=activation_disabled,
            non_effects=["does_not_apply_without_approval_phrase"],
        ),
        action_descriptor(
            action_id="studio.document_mounts.review",
            domain="document_mounts",
            title="Review document rules",
            write_mode="no-write",
            plan_surface="jikuo.studio.status.summaries.document_mounts",
            apply_surface=None,
            write_effect="none",
            approval_required=False,
            source_ref=".jikuo/project_context.yaml",
            status="disabled" if document_mounts_disabled else "available",
            disabled_reason=document_mounts_disabled,
            non_effects=["does_not_change_main_document_scope"],
        ),
        action_descriptor(
            action_id="studio.document_mounts.plan_update",
            domain="document_mounts",
            title="Plan document-rule update",
            write_mode="no-write-plan",
            plan_surface="python -B -m jikuo studio document-rules plan",
            apply_surface="python -B -m jikuo studio document-rules apply",
            write_effect=".jikuo/project_context.yaml only after reviewed plan, source fingerprint match, confirmation flag, and approval phrase",
            approval_required=True,
            source_ref="src/jikuo/studio/document_rules.py",
            status="disabled" if document_mounts_disabled else "available",
            disabled_reason=document_mounts_disabled,
            non_effects=[
                "does_not_edit_project_context_directly",
                "does_not_regenerate_legacy_task_map",
                "does_not_apply_without_guarded_approval",
            ],
        ),
        action_descriptor(
            action_id="studio.policy_management.status",
            domain="policy_management",
            title="Review policy-management status",
            write_mode="no-write",
            plan_surface="jikuo.get_policy_management_status",
            apply_surface=None,
            write_effect="none",
            approval_required=False,
            source_ref="src/jikuo/policy_management_status.py",
            status="disabled" if policy_disabled else "available",
            disabled_reason=policy_disabled,
            non_effects=["does_not_activate_user_project_policies"],
        ),
        action_descriptor(
            action_id="studio.policy_distribution.review",
            domain="policy_management",
            title="Review policy distribution",
            write_mode="no-write",
            plan_surface="jikuo.propose_policy_distribution_review",
            apply_surface=None,
            write_effect="none",
            approval_required=False,
            source_ref="src/jikuo/policy_templates.py",
            status="disabled" if policy_disabled else "available",
            disabled_reason=policy_disabled,
            non_effects=["does_not_publish_package_templates"],
        ),
        action_descriptor(
            action_id="studio.policy_template.plan_publication",
            domain="policy_management",
            title="Plan package template publication",
            write_mode="no-write-plan",
            plan_surface="jikuo.propose_policy_template_publication_plan",
            apply_surface="jikuo.apply_policy_template_publication",
            write_effect="one package template only after guarded apply",
            approval_required=True,
            source_ref="src/jikuo/policy_templates.py",
            status="disabled" if policy_disabled else "available",
            disabled_reason=policy_disabled,
            non_effects=["does_not_write_without_confirmation"],
        ),
        action_descriptor(
            action_id="studio.policy_template.activate",
            domain="policy_management",
            title="Activate package template in user project",
            write_mode="guarded",
            plan_surface="jikuo.propose_policy_template_import_plan",
            apply_surface="jikuo.apply_policy_template_activation",
            write_effect="project policy files only after guarded apply",
            approval_required=True,
            source_ref="src/jikuo/starter_policies.py",
            status="disabled" if policy_disabled else "available",
            disabled_reason=policy_disabled,
            non_effects=["does_not_mutate_package_templates"],
        ),
        action_descriptor(
            action_id="studio.starter_manifest.plan_publication",
            domain="policy_management",
            title="Plan starter manifest publication",
            write_mode="no-write-plan",
            plan_surface="jikuo.propose_starter_manifest_publication_plan",
            apply_surface="jikuo.apply_starter_manifest_publication",
            write_effect="starter manifest update only after guarded apply",
            approval_required=True,
            source_ref="src/jikuo/starter_policies.py",
            status="disabled" if policy_disabled else "available",
            disabled_reason=policy_disabled,
            non_effects=["does_not_initialize_user_project"],
        ),
        action_descriptor(
            action_id="studio.runtime.open_latest_card",
            domain="runtime",
            title="Open latest runtime card",
            write_mode="no-write",
            plan_surface="jikuo.get_display_card",
            apply_surface=None,
            write_effect="none",
            approval_required=False,
            source_ref=runtime_visibility.LAST_CARD_REF,
            status="disabled" if runtime_disabled else "available",
            disabled_reason=runtime_disabled,
            non_effects=["does_not_create_runtime_cards"],
        ),
    ]


def build_action_registry(
    *,
    project_root: Path | None = None,
    summaries: dict[str, Any] | None = None,
    extra_actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    actions = [
        *registered_action_descriptors(summaries=summaries),
        *(extra_actions or []),
    ]
    by_domain: dict[str, int] = {}
    for action in actions:
        domain = str(action.get("domain") or "unknown")
        by_domain[domain] = by_domain.get(domain, 0) + 1
    return {
        "schema": ACTION_REGISTRY_SCHEMA,
        "schema_version": ACTION_REGISTRY_SCHEMA,
        "status": "available",
        "project_root": str(project_root) if project_root else None,
        "action_count": len(actions),
        "available_action_count": sum(1 for item in actions if item.get("status") == "available"),
        "guarded_action_count": sum(1 for item in actions if item.get("approval_required")),
        "by_domain": by_domain,
        "actions": actions,
        "source_refs": [
            "src/jikuo/studio/actions.py",
            "src/jikuo/studio/global_status.py",
        ],
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_execute_actions",
            "does_not_apply_guarded_writes",
            "does_not_mutate_project_state",
        ],
    }
