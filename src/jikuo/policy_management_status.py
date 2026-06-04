"""Policy-management status read model.

This module provides a no-write backend surface for GUI and MCP clients. It
collects the active project policy store, package-owned policy templates, and
starter-pack manifests into one compact status report without publishing,
activating, or evolving policies.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

if __package__:
    from . import policy_store, policy_templates, project_state, starter_policies
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import policy_store
    import policy_templates
    import project_state
    import starter_policies


POLICY_MANAGEMENT_STATUS_SCHEMA = "jikuo.policy_management_status.v0"
DEFAULT_TEMPLATE_DIR = Path("policy_templates") / "engineering_governance"
DEFAULT_STARTER_PACK_ID = starter_policies.DEFAULT_PACK_ID
POLICY_SCOPE_OPTIONS = ["discussion", "editing", "progress_summary"]
LIFECYCLE_EVENT_OPTIONS = ["conversation_turn", "task_start", "completion_review"]
TRIGGER_MODE_OPTIONS = ["scope_first", "event_anchored", "legacy_event_only"]
SOURCE_REFS = [
    "pkg://jikuo/governance/jikuo_policy_governance_authority.md",
    "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01_policy_management_mvp.md",
]


def package_root() -> Path:
    return Path(__file__).resolve().parent


def template_dir_path(template_dir: Path | None = None) -> Path:
    if template_dir is not None:
        return template_dir.expanduser().resolve()
    return package_root() / DEFAULT_TEMPLATE_DIR


def package_ref(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(package_root().resolve())
    except ValueError:
        return f"redacted://local_package_file/{policy_templates.file_sha256(resolved)}"
    return f"pkg://jikuo/{relative.as_posix()}"


def load_package_templates(
    *,
    template_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    resolved_dir = template_dir_path(template_dir)
    warnings: list[str] = []
    templates: list[dict[str, Any]] = []
    try:
        resolved_dir.relative_to((package_root() / "policy_templates").resolve())
    except ValueError:
        return [], [f"template_dir_outside_package_policy_templates:{resolved_dir}"]
    if not resolved_dir.exists():
        return [], [f"policy_template_dir_missing:{resolved_dir}"]
    if not resolved_dir.is_dir():
        return [], [f"policy_template_dir_not_directory:{resolved_dir}"]

    for path in sorted(resolved_dir.glob("*.yaml")):
        try:
            record = policy_templates.read_yaml_subset(path)
        except OSError as exc:
            warnings.append(f"policy_template_not_readable:{path}:{exc}")
            continue
        schema = record.get("schema_version") or record.get("schema")
        if schema != policy_templates.POLICY_TEMPLATE_SCHEMA:
            warnings.append(f"unsupported_policy_template_schema:{path}:{schema}")
            continue
        template_policy = record.get("template_policy")
        if not isinstance(template_policy, dict):
            template_policy = {}
            warnings.append(f"policy_template_missing_template_policy:{path}")
        templates.append(
            {
                "template_id": record.get("template_id"),
                "template_ref": package_ref(path),
                "template_path": str(path),
                "namespace": record.get("namespace"),
                "version": record.get("version"),
                "title": record.get("title"),
                "template_policy_id": template_policy.get("policy_id"),
                "template_policy_title": template_policy.get("title"),
                "template_policy_status": template_policy.get("status"),
                "portability_status": (record.get("portability") or {}).get("status")
                if isinstance(record.get("portability"), dict)
                else None,
                "required_binding_count": len(record.get("required_bindings") or []),
                "included_in_starter_packs": [],
            }
        )
    return templates, warnings


def iter_starter_manifest_paths(pack_id: str | None) -> list[Path]:
    if pack_id:
        return [starter_policies.pack_manifest_path(pack_id)]
    root = starter_policies.STARTER_PACKS_ROOT
    if not root.exists() or not root.is_dir():
        return []
    return sorted(root.glob("*/manifest.yaml"))


def load_starter_pack_summaries(
    *,
    pack_id: str | None = DEFAULT_STARTER_PACK_ID,
) -> tuple[list[dict[str, Any]], list[str]]:
    packs: list[dict[str, Any]] = []
    warnings: list[str] = []
    for manifest_path in iter_starter_manifest_paths(pack_id):
        current_pack_id = manifest_path.parent.name
        manifest, manifest_warnings = starter_policies.load_pack_manifest(current_pack_id)
        warnings.extend(manifest_warnings)
        if manifest is None:
            packs.append(
                {
                    "pack_id": current_pack_id,
                    "status": "missing_or_invalid",
                    "manifest_path": str(manifest_path),
                    "manifest_ref": package_ref(manifest_path)
                    if manifest_path.exists()
                    else None,
                    "template_count": 0,
                    "policy_templates": [],
                    "warnings": manifest_warnings,
                }
            )
            continue
        entries = starter_policies.existing_manifest_template_entries(manifest)
        packs.append(
            {
                "pack_id": manifest.get("pack_id") or current_pack_id,
                "status": "available" if not manifest_warnings else "review",
                "title": manifest.get("title"),
                "description": manifest.get("description"),
                "manifest_path": str(manifest_path),
                "manifest_ref": package_ref(manifest_path),
                "template_count": len(entries),
                "policy_templates": [
                    {
                        "template_ref": item.get("template_ref"),
                        "policy_id": item.get("policy_id"),
                        "title": item.get("title"),
                    }
                    for item in entries
                ],
                "warnings": manifest_warnings,
            }
        )
    return packs, warnings


def starter_membership_by_template(
    starter_packs: list[dict[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    output: dict[str, list[dict[str, str]]] = {}
    for pack in starter_packs:
        pack_id = str(pack.get("pack_id") or "")
        for item in pack.get("policy_templates") or []:
            if not isinstance(item, dict):
                continue
            template_ref = item.get("template_ref")
            if not isinstance(template_ref, str) or not template_ref:
                continue
            output.setdefault(template_ref, []).append(
                {
                    "pack_id": pack_id,
                    "policy_id": str(item.get("policy_id") or ""),
                    "title": str(item.get("title") or ""),
                }
            )
    return output


def active_policy_distribution_summary(
    active_policy: dict[str, Any],
    *,
    templates_by_policy_id: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    policy_id = str(active_policy.get("policy_id") or "")
    matching_templates = templates_by_policy_id.get(policy_id, [])
    template_refs = [str(item.get("template_ref")) for item in matching_templates]
    in_starter = [
        pack
        for template in matching_templates
        for pack in template.get("included_in_starter_packs") or []
    ]
    if in_starter:
        state = "starter_pack_available"
    elif matching_templates:
        state = "package_template_available"
    else:
        state = "active_project_policy_only"
    return {
        "policy_id": policy_id,
        "title": active_policy.get("title"),
        "status": active_policy.get("status"),
        "path": active_policy.get("path"),
        "distribution_state": state,
        "package_template_refs": template_refs,
        "starter_pack_refs": in_starter,
        "next_actions": [
            "review distribution decision before publication",
            "plan package-template publication only for reusable outcomes",
        ]
        if state == "active_project_policy_only"
        else [
            "review package template before importing into a user project",
            "use guarded starter/template activation for user-project adoption",
        ],
    }


def string_values(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item) for item in values if item is not None]


def policy_trigger_profile(record: dict[str, Any]) -> dict[str, Any]:
    applicability = policy_store.normalize_work_profile_applicability(
        record.get("applies_to_work_profile")
    )
    if applicability is None:
        applicability = {
            "schema": policy_store.WORK_PROFILE_APPLICABILITY_SCHEMA,
            "status": "not_declared",
            "lifecycle_events": [],
            "policy_scopes": [],
            "intent_classes": [],
            "operation_classes": [],
            "output_classes": [],
            "evaluator_effect": "not_applicable",
            "warnings": [],
        }
    lifecycle_events = string_values(applicability.get("lifecycle_events"))
    policy_scopes = string_values(applicability.get("policy_scopes"))
    triggers = record.get("triggers") if isinstance(record.get("triggers"), list) else []
    trigger_events = [
        str(item.get("event"))
        for item in triggers
        if isinstance(item, dict) and item.get("event") is not None
    ]
    if policy_scopes and not lifecycle_events:
        trigger_mode = "scope_first"
    elif policy_scopes and lifecycle_events:
        trigger_mode = "event_anchored"
    elif trigger_events:
        trigger_mode = "legacy_event_only"
    else:
        trigger_mode = "unconfigured"
    return {
        "trigger_mode": trigger_mode,
        "policy_scopes": policy_scopes,
        "lifecycle_events": lifecycle_events,
        "intent_classes": string_values(applicability.get("intent_classes")),
        "operation_classes": string_values(applicability.get("operation_classes")),
        "output_classes": string_values(applicability.get("output_classes")),
        "declared_trigger_events": trigger_events,
        "work_profile_applicability": applicability,
    }


def condition_filter_summary(conditions: Any) -> dict[str, Any]:
    raw_conditions = conditions if isinstance(conditions, list) else []
    def values_for(condition_type: str, field: str) -> list[str]:
        return [
            str(item.get(field))
            for item in raw_conditions
            if isinstance(item, dict)
            and item.get("type") == condition_type
            and item.get(field) is not None
        ]

    return {
        "condition_count": len(raw_conditions),
        "task_types": values_for("task_type_is", "value"),
        "jikuo_layers": values_for("jikuo_layer_is", "value"),
        "changed_path_patterns": values_for("changed_path_matches", "pattern"),
        "added_path_patterns": values_for("added_path_matches", "pattern"),
        "raw_conditions": raw_conditions,
    }


def policy_detail_summary(
    *,
    active_policy: dict[str, Any],
    record: dict[str, Any],
    distribution: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "policy_id": record.get("policy_id") or active_policy.get("policy_id"),
        "title": record.get("title") or active_policy.get("title"),
        "version": record.get("version") or active_policy.get("version"),
        "status": record.get("status") or active_policy.get("status"),
        "path": active_policy.get("path"),
        "schema_version": record.get("schema_version") or record.get("schema"),
        "scenario_package": record.get("scenario_package"),
        "trigger_profile": policy_trigger_profile(record),
        "condition_filters": condition_filter_summary(record.get("conditions")),
        "triggers": record.get("triggers") if isinstance(record.get("triggers"), list) else [],
        "required_actions": (
            record.get("required_actions")
            if isinstance(record.get("required_actions"), list)
            else []
        ),
        "required_evidence": (
            record.get("required_evidence")
            if isinstance(record.get("required_evidence"), list)
            else []
        ),
        "source_refs": record.get("source_refs")
        if isinstance(record.get("source_refs"), list)
        else [],
        "enforcement": record.get("enforcement")
        if isinstance(record.get("enforcement"), dict)
        else {},
        "distribution": distribution or {},
    }


def proposal_file_path_from_ref(
    *,
    resolved_root: Path,
    store_root: Path,
    proposal_ref: dict[str, Any],
) -> tuple[Path | None, str | None]:
    raw_path = proposal_ref.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        return None, f"proposal ref has no path: {proposal_ref.get('proposal_id')}"
    proposal_path, path_error = policy_store.resolve_project_path(resolved_root, raw_path)
    if path_error:
        return None, path_error
    assert proposal_path is not None
    proposal_root = (store_root / "proposals").resolve()
    try:
        proposal_path.relative_to(proposal_root)
    except ValueError:
        return None, f"proposal ref is outside policy proposal store: {raw_path}"
    return proposal_path, None


def compact_write_set(write_set: Any) -> list[dict[str, Any]]:
    if not isinstance(write_set, list):
        return []
    return [
        {
            "path": item.get("path"),
            "operation": item.get("operation"),
            "effect": item.get("effect"),
        }
        for item in write_set
        if isinstance(item, dict)
    ]


def proposal_trigger_profile(record: dict[str, Any]) -> dict[str, Any]:
    proposed_profile = record.get("proposed_trigger_profile")
    if isinstance(proposed_profile, dict):
        return {
            "trigger_mode": proposed_profile.get("trigger_mode") or "unconfigured",
            "policy_scopes": string_values(proposed_profile.get("policy_scopes")),
            "lifecycle_events": string_values(proposed_profile.get("lifecycle_events")),
            "declared_trigger_events": string_values(
                [proposed_profile.get("declared_trigger_event")]
                if proposed_profile.get("declared_trigger_event") is not None
                else []
            ),
            "condition_count": len(proposed_profile.get("conditions") or [])
            if isinstance(proposed_profile.get("conditions"), list)
            else 0,
        }
    proposed_policy = record.get("proposed_policy")
    if isinstance(proposed_policy, dict):
        return policy_trigger_profile(proposed_policy)
    return {
        "trigger_mode": "unconfigured",
        "policy_scopes": [],
        "lifecycle_events": [],
        "declared_trigger_events": [],
    }


def proposal_detail_summary(
    *,
    proposal_ref: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    proposed_policy = record.get("proposed_policy")
    if not isinstance(proposed_policy, dict):
        proposed_policy = {}
    target_snapshot = record.get("target_policy_snapshot")
    if not isinstance(target_snapshot, dict):
        target_snapshot = {}
    return {
        "proposal_id": proposal_ref.get("proposal_id") or record.get("plan_id"),
        "policy_id": (
            record.get("policy_ref")
            or record.get("target_policy_ref")
            or proposed_policy.get("policy_id")
            or proposal_ref.get("policy_id")
        ),
        "title": proposed_policy.get("title") or target_snapshot.get("title"),
        "path": proposal_ref.get("path"),
        "manifest_status": proposal_ref.get("status"),
        "schema_version": record.get("schema_version") or record.get("schema"),
        "plan_id": record.get("plan_id"),
        "operation": record.get("operation"),
        "status": record.get("status"),
        "report_only": bool(record.get("report_only")),
        "writes_performed": bool(record.get("writes_performed")),
        "write_allowed_by_command": bool(record.get("write_allowed_by_command")),
        "approval_required": bool(record.get("approval_required")),
        "guarded_apply_available": bool(record.get("guarded_apply_available")),
        "write_set": compact_write_set(record.get("write_set")),
        "write_set_count": len(compact_write_set(record.get("write_set"))),
        "trigger_profile": proposal_trigger_profile(record),
        "proposed_policy": {
            "policy_id": proposed_policy.get("policy_id"),
            "title": proposed_policy.get("title"),
            "status": proposed_policy.get("status"),
            "version": proposed_policy.get("version"),
            "scenario_package": proposed_policy.get("scenario_package"),
        },
        "target_policy_snapshot": {
            "policy_id": target_snapshot.get("policy_id"),
            "title": target_snapshot.get("title"),
            "status": target_snapshot.get("status"),
            "version": target_snapshot.get("version"),
            "path": target_snapshot.get("path"),
        },
        "refusal_reasons": record.get("refusal_reasons")
        if isinstance(record.get("refusal_reasons"), list)
        else [],
        "warnings": record.get("warnings") if isinstance(record.get("warnings"), list) else [],
        "source_refs": record.get("source_refs")
        if isinstance(record.get("source_refs"), list)
        else [],
        "status_reason": record.get("status_reason"),
        "next_actions": record.get("next_actions")
        if isinstance(record.get("next_actions"), list)
        else [],
    }


def load_active_policy_details(
    *,
    resolved_root: Path,
    policy_report: dict[str, Any],
    active_policy_distribution: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    store_root = Path(str(policy_report.get("policy_store_root") or ""))
    distribution_by_policy = {
        str(item.get("policy_id")): item
        for item in active_policy_distribution
        if item.get("policy_id") is not None
    }
    details: list[dict[str, Any]] = []
    warnings: list[str] = []
    for active_policy in policy_report.get("active_policy_refs") or []:
        if not isinstance(active_policy, dict):
            continue
        policy_path, path_error = policy_store.policy_file_path_from_ref(
            project_root=resolved_root,
            store_root=store_root,
            policy_ref=active_policy,
        )
        if path_error:
            warnings.append(path_error)
            continue
        assert policy_path is not None
        record, record_warnings = policy_store.read_policy_record(policy_path)
        warnings.extend(record_warnings)
        if record is None:
            continue
        policy_id = str(record.get("policy_id") or active_policy.get("policy_id") or "")
        details.append(
            policy_detail_summary(
                active_policy=active_policy,
                record=record,
                distribution=distribution_by_policy.get(policy_id),
            )
        )
    return details, warnings


def load_policy_proposal_details(
    *,
    resolved_root: Path,
    policy_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    store_root = Path(str(policy_report.get("policy_store_root") or ""))
    details: list[dict[str, Any]] = []
    warnings: list[str] = []
    for proposal_ref in policy_report.get("proposal_refs") or []:
        if not isinstance(proposal_ref, dict):
            continue
        proposal_path, path_error = proposal_file_path_from_ref(
            resolved_root=resolved_root,
            store_root=store_root,
            proposal_ref=proposal_ref,
        )
        if path_error:
            warnings.append(path_error)
            continue
        assert proposal_path is not None
        try:
            record = policy_templates.read_yaml_subset(proposal_path)
        except OSError as exc:
            warnings.append(f"policy_proposal_not_readable:{proposal_path}:{exc}")
            continue
        details.append(
            proposal_detail_summary(
                proposal_ref=proposal_ref,
                record=record,
            )
        )
    return details, warnings


def option_sets_from_policy_details(details: list[dict[str, Any]]) -> dict[str, Any]:
    task_types: set[str] = set()
    jikuo_layers: set[str] = set()
    action_types: set[str] = set()
    evidence_types: set[str] = set()
    for detail in details:
        filters = detail.get("condition_filters") or {}
        task_types.update(str(item) for item in filters.get("task_types") or [])
        jikuo_layers.update(str(item) for item in filters.get("jikuo_layers") or [])
        for action in detail.get("required_actions") or []:
            if isinstance(action, dict) and action.get("type") is not None:
                action_types.add(str(action.get("type")))
        for evidence in detail.get("required_evidence") or []:
            if isinstance(evidence, dict) and evidence.get("type") is not None:
                evidence_types.add(str(evidence.get("type")))
    return {
        "policy_scopes": POLICY_SCOPE_OPTIONS,
        "lifecycle_events": LIFECYCLE_EVENT_OPTIONS,
        "trigger_modes": TRIGGER_MODE_OPTIONS,
        "task_types": sorted(task_types | {"code_change", "jikuo_development"}),
        "jikuo_layers": sorted(
            jikuo_layers
            | {"implementation_governance", "policy_governance", "process_governance"}
        ),
        "action_types": sorted(action_types),
        "evidence_types": sorted(evidence_types),
    }


def build_policy_management_status(
    *,
    project_root: Path | None = None,
    starter_pack_id: str | None = DEFAULT_STARTER_PACK_ID,
    template_dir: Path | None = None,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    policy_report = policy_store.inspect_policy_store(project_root=resolved_root)
    templates, template_warnings = load_package_templates(template_dir=template_dir)
    starter_packs, starter_warnings = load_starter_pack_summaries(pack_id=starter_pack_id)
    membership = starter_membership_by_template(starter_packs)
    for template in templates:
        template["included_in_starter_packs"] = membership.get(
            str(template.get("template_ref") or ""),
            [],
        )

    templates_by_policy_id: dict[str, list[dict[str, Any]]] = {}
    for template in templates:
        policy_id = template.get("template_policy_id")
        if isinstance(policy_id, str) and policy_id:
            templates_by_policy_id.setdefault(policy_id, []).append(template)

    active_policy_distribution = [
        active_policy_distribution_summary(
            active_policy,
            templates_by_policy_id=templates_by_policy_id,
        )
        for active_policy in policy_report.get("active_policy_refs") or []
        if isinstance(active_policy, dict)
    ]
    active_with_templates = [
        item
        for item in active_policy_distribution
        if item["distribution_state"] != "active_project_policy_only"
    ]
    active_without_templates = [
        item
        for item in active_policy_distribution
        if item["distribution_state"] == "active_project_policy_only"
    ]
    active_policy_details, detail_warnings = load_active_policy_details(
        resolved_root=resolved_root,
        policy_report=policy_report,
        active_policy_distribution=active_policy_distribution,
    )
    policy_proposal_details, proposal_detail_warnings = load_policy_proposal_details(
        resolved_root=resolved_root,
        policy_report=policy_report,
    )

    warnings = [
        *(policy_report.get("warnings") or []),
        *template_warnings,
        *starter_warnings,
        *detail_warnings,
        *proposal_detail_warnings,
    ]
    status = "review" if warnings else "available"
    return {
        "schema": POLICY_MANAGEMENT_STATUS_SCHEMA,
        "schema_version": POLICY_MANAGEMENT_STATUS_SCHEMA,
        "report_only": True,
        "status": status,
        "project_root": str(resolved_root),
        "write_allowed_by_command": False,
        "writes_performed": False,
        "policy_store": {
            "status": policy_report.get("policy_store_status"),
            "manifest_ref": policy_report.get("manifest_ref"),
            "active_policy_count": len(policy_report.get("active_policy_refs") or []),
            "proposal_ref_count": len(policy_report.get("proposal_refs") or []),
            "deprecated_policy_ref_count": len(
                policy_report.get("deprecated_policy_refs") or []
            ),
            "superseded_policy_ref_count": len(
                policy_report.get("superseded_policy_refs") or []
            ),
            "active_policies": policy_report.get("active_policy_refs") or [],
            "active_policy_details": active_policy_details,
            "proposal_refs": policy_report.get("proposal_refs") or [],
            "proposal_details": policy_proposal_details,
            "deprecated_policy_refs": policy_report.get("deprecated_policy_refs") or [],
            "superseded_policy_refs": policy_report.get("superseded_policy_refs") or [],
        },
        "package_templates": {
            "template_dir": str(template_dir_path(template_dir)),
            "template_count": len(templates),
            "templates": templates,
        },
        "starter_packs": {
            "requested_pack_id": starter_pack_id,
            "pack_count": len(starter_packs),
            "packs": starter_packs,
        },
        "active_policy_distribution": active_policy_distribution,
        "option_sets": option_sets_from_policy_details(active_policy_details),
        "summary_counts": {
            "active_policy_count": len(policy_report.get("active_policy_refs") or []),
            "package_template_count": len(templates),
            "starter_pack_count": len(starter_packs),
            "starter_template_ref_count": sum(
                len(pack.get("policy_templates") or []) for pack in starter_packs
            ),
            "active_policy_with_package_template_count": len(active_with_templates),
            "active_policy_without_package_template_count": len(active_without_templates),
        },
        "available_operations": [
            {
                "operation": "distribution_review",
                "surface": "jikuo.propose_policy_distribution_review",
                "write_mode": "no-write",
            },
            {
                "operation": "policy_evolution_plan",
                "surface": "jikuo.propose_policy_evolution_plan",
                "write_mode": "no-write",
            },
            {
                "operation": "policy_evolution_write",
                "surface": "jikuo.apply_policy_evolution_write",
                "write_mode": "guarded-write",
            },
            {
                "operation": "policy_template_import_plan",
                "surface": "jikuo.propose_policy_template_import_plan",
                "write_mode": "no-write",
            },
            {
                "operation": "policy_template_activation",
                "surface": "jikuo.apply_policy_template_activation",
                "write_mode": "guarded-write",
            },
            {
                "operation": "policy_template_publication_plan",
                "surface": "jikuo.propose_policy_template_publication_plan",
                "write_mode": "no-write",
            },
            {
                "operation": "policy_template_publication",
                "surface": "jikuo.apply_policy_template_publication",
                "write_mode": "guarded-write",
            },
            {
                "operation": "starter_manifest_publication_plan",
                "surface": "jikuo.propose_starter_manifest_publication_plan",
                "write_mode": "no-write",
            },
            {
                "operation": "starter_manifest_publication",
                "surface": "jikuo.apply_starter_manifest_publication",
                "write_mode": "guarded-write",
            },
        ],
        "read_model_limitations": [
            "distribution review decisions are report-only unless separately recorded",
            "package template availability is not user-project activation",
            "starter manifest inclusion is not user-project initialization",
            "natural-language policy selection still depends on host AI or deterministic candidate matching",
        ],
        "non_effects": [
            "does not publish package templates",
            "does not update starter-pack manifests",
            "does not activate or rewrite user-project policies",
            "does not change policy evaluator behavior",
        ],
        "warnings": sorted(set(str(item) for item in warnings)),
        "source_refs": SOURCE_REFS,
        "next_actions": [
            "use this read model as the backend source for a thin policy-management UI",
            "run no-write distribution review before publishing any reusable policy",
            "keep user-project activation behind template import or starter-init guarded flows",
        ],
    }


def format_markdown(report: dict[str, Any]) -> str:
    counts = report.get("summary_counts") or {}
    lines = [
        "# JIKUO Policy Management Status",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Schema: `{report.get('schema')}`",
        f"- Project root: `{report.get('project_root')}`",
        f"- Active policies: `{counts.get('active_policy_count')}`",
        f"- Package templates: `{counts.get('package_template_count')}`",
        f"- Starter packs: `{counts.get('starter_pack_count')}`",
        f"- Starter template refs: `{counts.get('starter_template_ref_count')}`",
        f"- Active policies with package templates: `{counts.get('active_policy_with_package_template_count')}`",
        f"- Active policies without package templates: `{counts.get('active_policy_without_package_template_count')}`",
        "",
        "## Active Policy Distribution",
    ]
    for item in report.get("active_policy_distribution") or []:
        lines.append(
            f"- `{item.get('policy_id')}` / `{item.get('distribution_state')}` / "
            f"{item.get('title') or ''}"
        )
    lines.extend(["", "## Package Templates"])
    for item in (report.get("package_templates") or {}).get("templates") or []:
        starter_packs = item.get("included_in_starter_packs") or []
        pack_text = ", ".join(str(pack.get("pack_id")) for pack in starter_packs) or "none"
        lines.append(
            f"- `{item.get('template_ref')}` / policy=`{item.get('template_policy_id')}` / "
            f"starter_packs=`{pack_text}`"
        )
    lines.extend(["", "## Starter Packs"])
    for pack in (report.get("starter_packs") or {}).get("packs") or []:
        lines.append(
            f"- `{pack.get('pack_id')}` / templates=`{pack.get('template_count')}` / "
            f"status=`{pack.get('status')}`"
        )
    if report.get("warnings"):
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend(["", "## Next Actions"])
    lines.extend(f"- {item}" for item in report.get("next_actions") or [])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect JIKUO policy-management status.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status")
    status.add_argument("--project-root", type=Path, default=None)
    status.add_argument("--starter-pack-id", default=DEFAULT_STARTER_PACK_ID)
    status.add_argument("--template-dir", type=Path, default=None)
    status.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "status":
        report = build_policy_management_status(
            project_root=args.project_root,
            starter_pack_id=args.starter_pack_id,
            template_dir=args.template_dir,
        )
        if args.format == "markdown":
            print(format_markdown(report), end="")
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("status") in {"available", "review"} else 2
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
