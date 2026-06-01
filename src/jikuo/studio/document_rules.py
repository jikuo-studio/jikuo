"""No-write planning for JIKUO Studio document-rule changes."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__:
    from .. import policy_templates, project_state
else:  # pragma: no cover - direct script fallback for ad hoc inspection
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from jikuo import policy_templates, project_state


DOCUMENT_RULES_PLAN_SCHEMA = "jikuo.studio.document_rules_update_plan.v0"
PROJECT_CONTEXT_REF = ".jikuo/project_context.yaml"
LEGACY_TASK_MAP_REF = "docs/governance/jikuo_productization_task_map.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def stable_plan_id(parts: list[str]) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]
    return f"document_rules_plan_{digest}"


def slug_from_path(path_ref: str) -> str:
    stem = Path(path_ref).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return slug or "document"


def split_role_spec(spec: str) -> tuple[str | None, str]:
    if "=" not in spec:
        return None, spec
    left, right = spec.split("=", 1)
    role = left.strip()
    path_ref = right.strip()
    if not role or not path_ref:
        return None, spec
    return role, path_ref


def normalize_project_ref(
    raw_ref: str,
    *,
    project_root: Path,
) -> tuple[str | None, list[dict[str, Any]], list[dict[str, Any]]]:
    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    value = str(raw_ref or "").strip().replace("\\", "/")
    if not value:
        errors.append(
            {
                "code": "empty_path_ref",
                "message": "document-rule path references cannot be empty",
                "input": raw_ref,
            }
        )
        return None, warnings, errors

    candidate = Path(value)
    if candidate.is_absolute():
        resolved = candidate.resolve()
        try:
            relative = resolved.relative_to(project_root.resolve())
        except ValueError:
            errors.append(
                {
                    "code": "path_outside_project_root",
                    "message": "absolute path does not resolve inside project root",
                    "input": raw_ref,
                }
            )
            return None, warnings, errors
        normalized = relative.as_posix()
        warnings.append(
            {
                "code": "absolute_path_normalized",
                "message": "absolute path was normalized to a project-relative path",
                "input": raw_ref,
                "normalized_ref": normalized,
            }
        )
        return normalized, warnings, errors

    resolved = (project_root / value).resolve()
    try:
        relative = resolved.relative_to(project_root.resolve())
    except ValueError:
        errors.append(
            {
                "code": "path_outside_project_root",
                "message": "relative path escapes the project root",
                "input": raw_ref,
            }
        )
        return None, warnings, errors
    normalized = relative.as_posix()
    if normalized == ".":
        errors.append(
            {
                "code": "project_root_path_not_allowed",
                "message": "document-rule entries must target files, not the project root",
                "input": raw_ref,
            }
        )
        return None, warnings, errors
    return normalized, warnings, errors


def path_exists(project_root: Path, path_ref: str) -> bool:
    return (project_root / path_ref).is_file()


def load_project_context(project_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    path = project_root / PROJECT_CONTEXT_REF
    if not path.is_file():
        return {}, [
            {
                "code": "project_context_missing",
                "message": ".jikuo/project_context.yaml is required for document-rule plans",
                "source_ref": PROJECT_CONTEXT_REF,
            }
        ]
    try:
        context = policy_templates.read_yaml_subset(path)
    except Exception as exc:
        return {}, [
            {
                "code": "project_context_invalid",
                "message": f"could not parse .jikuo/project_context.yaml: {exc}",
                "source_ref": PROJECT_CONTEXT_REF,
            }
        ]
    if not isinstance(context, dict):
        return {}, [
            {
                "code": "project_context_not_mapping",
                "message": ".jikuo/project_context.yaml did not parse as a mapping",
                "source_ref": PROJECT_CONTEXT_REF,
            }
        ]
    return context, []


def document_roles(context: dict[str, Any]) -> dict[str, Any]:
    roles = context.get("document_roles")
    return roles if isinstance(roles, dict) else {}


def main_mounts(context: dict[str, Any]) -> dict[str, Any]:
    mounts = context.get("main_document_mounts")
    return mounts if isinstance(mounts, dict) else {}


def existing_completion_checks(context: dict[str, Any]) -> list[dict[str, Any]]:
    records = main_mounts(context).get("checked_before_slice_completion") or []
    return [item for item in records if isinstance(item, dict)]


def existing_authority_refs(context: dict[str, Any]) -> list[str]:
    records = main_mounts(context).get("active_mount_authority") or []
    return [str(item) for item in records if item]


def find_roles_by_path(context: dict[str, Any], path_ref: str) -> list[str]:
    matches: list[str] = []
    for role, record in document_roles(context).items():
        if isinstance(record, dict) and str(record.get("path") or "") == path_ref:
            matches.append(str(role))
    return matches


def validation_item(code: str, message: str, *, path_ref: str | None = None) -> dict[str, Any]:
    item = {"code": code, "message": message}
    if path_ref is not None:
        item["path_ref"] = path_ref
    return item


def normalize_many(
    specs: list[str],
    *,
    project_root: Path,
    kind: str,
    errors: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> list[str]:
    normalized: list[str] = []
    for spec in specs:
        path_ref, new_warnings, new_errors = normalize_project_ref(spec, project_root=project_root)
        for item in new_warnings:
            item["operation_kind"] = kind
            warnings.append(item)
        for item in new_errors:
            item["operation_kind"] = kind
            errors.append(item)
        if path_ref:
            normalized.append(path_ref)
    return normalized


def build_document_rules_update_plan(
    *,
    project_root: Path | None = None,
    add_context_docs: list[str] | None = None,
    remove_context_docs: list[str] | None = None,
    add_completion_checks: list[str] | None = None,
    remove_completion_checks: list[str] | None = None,
    add_governance_references: list[str] | None = None,
    remove_governance_references: list[str] | None = None,
    completion_update_rule: str | None = None,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    add_context_docs = list(add_context_docs or [])
    remove_context_docs = list(remove_context_docs or [])
    add_completion_checks = list(add_completion_checks or [])
    remove_completion_checks = list(remove_completion_checks or [])
    add_governance_references = list(add_governance_references or [])
    remove_governance_references = list(remove_governance_references or [])
    completion_update_rule = (
        completion_update_rule
        or "review this document before declaring the governed slice complete"
    )

    requested_operations = {
        "add_context_docs": add_context_docs,
        "remove_context_docs": remove_context_docs,
        "add_completion_checks": add_completion_checks,
        "remove_completion_checks": remove_completion_checks,
        "add_governance_references": add_governance_references,
        "remove_governance_references": remove_governance_references,
    }
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    noops: list[dict[str, Any]] = []

    context, context_errors = load_project_context(resolved_root)
    errors.extend(context_errors)

    role_additions: list[dict[str, Any]] = []
    role_removals: list[dict[str, Any]] = []
    completion_additions: list[dict[str, Any]] = []
    completion_removals: list[dict[str, Any]] = []
    authority_additions: list[dict[str, Any]] = []
    authority_removals: list[dict[str, Any]] = []

    existing_roles = document_roles(context)
    existing_checks = {str(item.get("path")) for item in existing_completion_checks(context)}
    existing_authority = set(existing_authority_refs(context))

    for raw_spec in add_context_docs:
        role_hint, raw_path = split_role_spec(raw_spec)
        path_ref, new_warnings, new_errors = normalize_project_ref(
            raw_path,
            project_root=resolved_root,
        )
        warnings.extend({**item, "operation_kind": "add_context_doc"} for item in new_warnings)
        errors.extend({**item, "operation_kind": "add_context_doc"} for item in new_errors)
        if not path_ref:
            continue
        if path_ref == LEGACY_TASK_MAP_REF:
            errors.append(
                validation_item(
                    "legacy_task_map_authority_expansion_refused",
                    "legacy task map cannot be newly added as document-rule authority",
                    path_ref=path_ref,
                )
            )
            continue
        if not path_exists(resolved_root, path_ref):
            errors.append(
                validation_item(
                    "referenced_document_missing",
                    "context document must exist before it can be added",
                    path_ref=path_ref,
                )
            )
            continue
        if find_roles_by_path(context, path_ref):
            noops.append(
                validation_item(
                    "context_document_already_bound",
                    "context document already has a document role",
                    path_ref=path_ref,
                )
            )
            continue
        role = role_hint or slug_from_path(path_ref)
        if role in existing_roles or any(item["role"] == role for item in role_additions):
            role = f"{role}_{len(existing_roles) + len(role_additions) + 1}"
        role_additions.append(
            {
                "role": role,
                "path": path_ref,
                "required": False,
                "note": "User-added context document via Studio Document Rules plan.",
            }
        )

    for path_ref in normalize_many(
        remove_context_docs,
        project_root=resolved_root,
        kind="remove_context_doc",
        errors=errors,
        warnings=warnings,
    ):
        roles = find_roles_by_path(context, path_ref)
        if not roles:
            noops.append(
                validation_item(
                    "context_document_not_bound",
                    "context document is not currently bound to a document role",
                    path_ref=path_ref,
                )
            )
            continue
        for role in roles:
            role_removals.append({"role": role, "path": path_ref})

    for path_ref in normalize_many(
        add_completion_checks,
        project_root=resolved_root,
        kind="add_completion_check",
        errors=errors,
        warnings=warnings,
    ):
        if path_ref == LEGACY_TASK_MAP_REF:
            errors.append(
                validation_item(
                    "legacy_task_map_authority_expansion_refused",
                    "legacy task map completion checks may only be changed by explicit projection repair",
                    path_ref=path_ref,
                )
            )
            continue
        if not path_exists(resolved_root, path_ref):
            errors.append(
                validation_item(
                    "referenced_document_missing",
                    "completion check document must exist before it can be added",
                    path_ref=path_ref,
                )
            )
            continue
        if path_ref in existing_checks:
            noops.append(
                validation_item(
                    "completion_check_already_present",
                    "document is already checked before slice completion",
                    path_ref=path_ref,
                )
            )
            continue
        completion_additions.append(
            {
                "path": path_ref,
                "update_required_when": completion_update_rule,
            }
        )

    for path_ref in normalize_many(
        remove_completion_checks,
        project_root=resolved_root,
        kind="remove_completion_check",
        errors=errors,
        warnings=warnings,
    ):
        if path_ref not in existing_checks:
            noops.append(
                validation_item(
                    "completion_check_not_present",
                    "document is not currently checked before slice completion",
                    path_ref=path_ref,
                )
            )
            continue
        completion_removals.append({"path": path_ref})

    for path_ref in normalize_many(
        add_governance_references,
        project_root=resolved_root,
        kind="add_governance_reference",
        errors=errors,
        warnings=warnings,
    ):
        if path_ref == LEGACY_TASK_MAP_REF:
            errors.append(
                validation_item(
                    "legacy_task_map_authority_expansion_refused",
                    "legacy task map cannot be promoted as active mount authority",
                    path_ref=path_ref,
                )
            )
            continue
        if not path_exists(resolved_root, path_ref):
            errors.append(
                validation_item(
                    "referenced_document_missing",
                    "governance reference must exist before it can be added",
                    path_ref=path_ref,
                )
            )
            continue
        if path_ref in existing_authority:
            noops.append(
                validation_item(
                    "governance_reference_already_active",
                    "governance reference is already active mount authority",
                    path_ref=path_ref,
                )
            )
            continue
        authority_additions.append({"path": path_ref})

    for path_ref in normalize_many(
        remove_governance_references,
        project_root=resolved_root,
        kind="remove_governance_reference",
        errors=errors,
        warnings=warnings,
    ):
        if path_ref not in existing_authority:
            noops.append(
                validation_item(
                    "governance_reference_not_active",
                    "governance reference is not currently active mount authority",
                    path_ref=path_ref,
                )
            )
            continue
        authority_removals.append({"path": path_ref})

    proposed_changes = {
        "document_role_additions": role_additions,
        "document_role_removals": role_removals,
        "completion_check_additions": completion_additions,
        "completion_check_removals": completion_removals,
        "active_mount_authority_additions": authority_additions,
        "active_mount_authority_removals": authority_removals,
    }
    change_count = sum(len(value) for value in proposed_changes.values())
    status = "refused" if errors else ("review" if change_count else "noop")

    diff_preview: list[str] = []
    for item in role_additions:
        diff_preview.append(f"+ document_roles.{item['role']}.path: {item['path']}")
    for item in role_removals:
        diff_preview.append(f"- document_roles.{item['role']}")
    for item in completion_additions:
        diff_preview.append(
            f"+ main_document_mounts.checked_before_slice_completion: {item['path']}"
        )
    for item in completion_removals:
        diff_preview.append(
            f"- main_document_mounts.checked_before_slice_completion: {item['path']}"
        )
    for item in authority_additions:
        diff_preview.append(f"+ main_document_mounts.active_mount_authority: {item['path']}")
    for item in authority_removals:
        diff_preview.append(f"- main_document_mounts.active_mount_authority: {item['path']}")

    return {
        "schema": DOCUMENT_RULES_PLAN_SCHEMA,
        "schema_version": DOCUMENT_RULES_PLAN_SCHEMA,
        "plan_id": stable_plan_id(
            [
                str(resolved_root),
                json.dumps(requested_operations, sort_keys=True),
                completion_update_rule,
            ]
        ),
        "status": status,
        "generated_at_utc": utc_now_iso(),
        "project_root": str(resolved_root),
        "target_files": [PROJECT_CONTEXT_REF],
        "requested_operations": requested_operations,
        "current_state_summary": {
            "document_role_count": len(existing_roles),
            "completion_check_count": len(existing_checks),
            "active_mount_authority_count": len(existing_authority),
        },
        "proposed_changes": proposed_changes,
        "change_count": change_count,
        "diff_preview": diff_preview,
        "validation": {
            "status": "failed" if errors else "ok",
            "errors": errors,
            "warnings": warnings,
            "noops": noops,
        },
        "approval": {
            "required": status == "review",
            "apply_surface": "planned:jikuo.apply_document_rules_update",
            "approval_effect": "update .jikuo/project_context.yaml document rules",
        },
        "risks": [
            "document-rule changes can alter which context future governed work mounts",
            "completion-check changes can affect what must be reviewed before final delivery",
        ],
        "next_actions": [
            "review this no-write plan before any guarded apply",
            "use Studio guarded apply only after it is implemented and explicitly approved",
        ]
        if status == "review"
        else [],
        "write_mode": "no-write-plan",
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_write_project_context",
            "does_not_mutate_registry_shards",
            "does_not_regenerate_legacy_task_map",
            "does_not_change_policy_evaluator",
            "does_not_apply_without_guarded_approval",
        ],
    }


def format_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# JIKUO Document Rules Update Plan",
        "",
        f"- Status: `{plan.get('status')}`",
        f"- Schema: `{plan.get('schema')}`",
        f"- Project root: `{plan.get('project_root')}`",
        f"- Writes performed: `{str(plan.get('writes_performed')).lower()}`",
        f"- Change count: `{plan.get('change_count')}`",
        "",
        "## Proposed Changes",
        "",
    ]
    diff_preview = plan.get("diff_preview") or []
    if diff_preview:
        lines.extend(f"- `{item}`" for item in diff_preview)
    else:
        lines.append("- No document-rule changes proposed.")
    validation = plan.get("validation") or {}
    lines.extend(["", "## Validation", ""])
    lines.append(f"- Status: `{validation.get('status')}`")
    for item in validation.get("errors") or []:
        lines.append(f"- error `{item.get('code')}`: {item.get('message')}")
    for item in validation.get("warnings") or []:
        lines.append(f"- warning `{item.get('code')}`: {item.get('message')}")
    for item in validation.get("noops") or []:
        lines.append(f"- noop `{item.get('code')}`: {item.get('message')}")
    lines.extend(["", "## Approval", ""])
    approval = plan.get("approval") or {}
    lines.append(f"- Required: `{str(approval.get('required')).lower()}`")
    lines.append(f"- Apply surface: `{approval.get('apply_surface')}`")
    lines.extend(["", "## Non-Effects", ""])
    lines.extend(f"- {item}" for item in plan.get("non_effects") or [])
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan JIKUO Studio document-rule updates.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan")
    plan.add_argument("--project-root", type=Path, default=None)
    plan.add_argument("--add-context-doc", action="append", default=[])
    plan.add_argument("--remove-context-doc", action="append", default=[])
    plan.add_argument("--add-completion-check", action="append", default=[])
    plan.add_argument("--remove-completion-check", action="append", default=[])
    plan.add_argument("--add-governance-reference", action="append", default=[])
    plan.add_argument("--remove-governance-reference", action="append", default=[])
    plan.add_argument("--completion-update-rule", default=None)
    plan.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "plan":
        plan = build_document_rules_update_plan(
            project_root=args.project_root,
            add_context_docs=args.add_context_doc,
            remove_context_docs=args.remove_context_doc,
            add_completion_checks=args.add_completion_check,
            remove_completion_checks=args.remove_completion_check,
            add_governance_references=args.add_governance_reference,
            remove_governance_references=args.remove_governance_reference,
            completion_update_rule=args.completion_update_rule,
        )
        if args.format == "markdown":
            print(format_markdown(plan), end="")
        else:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0 if plan.get("status") in {"review", "noop"} else 2
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
