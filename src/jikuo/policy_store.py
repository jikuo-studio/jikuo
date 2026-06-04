"""JIKUO policy-store inspection and guarded write helper.

This helper discovers and validates the project-local policy-store shape. It can
also run report-only trigger and evidence evaluation slices. Proposal and
evaluation paths stay no-write; guarded write paths require explicit
confirmation and approval evidence.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

if __package__:
    from . import project_state
    from . import work_profile as work_profile_module
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import project_state
    import work_profile as work_profile_module


POLICY_STORE_STATUS_SCHEMA = "jikuo.policy_store_status.v0"
POLICY_TRIGGER_EVAL_REPORT_SCHEMA = "jikuo.policy_trigger_eval_report.v0"
POLICY_WRITE_PLAN_SCHEMA = "jikuo.policy_write_plan.v0"
POLICY_EVOLUTION_PLAN_SCHEMA = "jikuo.policy_evolution_plan.v0"
POLICY_WRITE_RESULT_SCHEMA = "jikuo.policy_write_result.v0"
POLICY_STORE_MANIFEST_SCHEMA = "jikuo.policy_store_manifest.v0"
POLICY_DECISION_SCHEMA = "jikuo.policy_decision.v0"
POLICY_SCHEMA = "jikuo.configurable_rule_policy.v0"
POLICY_MISSING_EVIDENCE_REPORT_SCHEMA = "jikuo.missing_evidence_report.v0"
POLICY_EVAL_STATUS_NOT_EVALUATED = "not_evaluated"
POLICY_EVAL_STATUS_EVALUATED = "evaluated"
POLICY_EVAL_STATUS_REFUSED = "refused"
POLICY_EVIDENCE_CHECK_STATUS_NOT_EVALUATED = "not_evaluated"
POLICY_EVIDENCE_CHECK_STATUS_CHECKED = "checked"
POLICY_EVIDENCE_CHECK_STATUS_REFUSED = "refused"
POLICY_CONDITION_EVAL_STATUS_NOT_EVALUATED = "not_evaluated"
POLICY_CONDITION_EVAL_STATUS_CHECKED = "checked"
WORK_PROFILE_APPLICABILITY_SCHEMA = "jikuo.policy_work_profile_applicability.v0"
POLICY_EVOLUTION_WRITE_SUPPORTED_OPERATIONS = {
    "refine_policy",
    "deprecate_policy",
    "supersede_policy",
}
POLICY_STORE_ROOT = ".jikuo/policies"
MANIFEST_NAME = "manifest.yaml"
DECISIONS_DIR_NAME = "decisions"
PROPOSALS_DIR_NAME = "proposals"
POLICY_EVOLUTION_OPERATIONS = {
    "refine_policy",
    "deprecate_policy",
    "supersede_policy",
}
POLICY_FEEDBACK_TYPES = {
    "not_applicable",
    "defer",
    "needs_scope_narrowing",
}
CONTRACT_REFS = [
    "pkg://jikuo/governance/jikuo_policy_store_configuration_flow.md",
    "pkg://jikuo/governance/jikuo_configurable_rule_trigger_policy.md",
    "pkg://jikuo/governance/jikuo_rule_action_evidence_model.md",
    "pkg://jikuo/governance/jikuo_policy_aware_agent_flow_contract.md",
]


def unquote_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "~"}:
        return None
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value.startswith("[") and value.endswith("]"):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list):
            return decoded
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {"'", '"'}
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def read_minimal_yaml(path: Path) -> dict[str, Any]:
    """Read the small JIKUO YAML subset used by fixtures and sidecars."""

    result: dict[str, Any] = {}
    current_list_key: str | None = None
    current_item: dict[str, Any] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_item = None
            if value == "":
                result[key] = []
                current_list_key = key
            else:
                result[key] = unquote_scalar(value)
                current_list_key = None
            continue

        if current_list_key and indent >= 2 and line.startswith("-"):
            item_text = line[1:].strip()
            if item_text == "":
                current_item = {}
                result[current_list_key].append(current_item)
            elif ":" in item_text:
                key, value = item_text.split(":", 1)
                current_item = {key.strip(): unquote_scalar(value)}
                result[current_list_key].append(current_item)
            else:
                current_item = None
                result[current_list_key].append(unquote_scalar(item_text))
            continue

        if current_item is not None and indent >= 4 and ":" in line:
            key, value = line.split(":", 1)
            current_item[key.strip()] = unquote_scalar(value)

    return result


def schema_from_record(record: dict[str, Any]) -> str | None:
    schema = record.get("schema_version") or record.get("schema")
    return schema if isinstance(schema, str) else None


def display_path(path: Path, project_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def stable_id(prefix: str, seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug_token(value: str) -> str:
    token_chars: list[str] = []
    for char in value.strip().lower():
        if char.isascii() and char.isalnum():
            token_chars.append(char)
        elif char in {"-", "_", " "}:
            token_chars.append("-")
    token = "-".join(part for part in "".join(token_chars).split("-") if part)
    return token[:64] or stable_id("policy", value).lower()


def normalize_policy_id(policy_id: str | None, title: str | None) -> str | None:
    if policy_id:
        return policy_id.strip()
    if title:
        return f"POLICY-{slug_token(title)}"
    return None


def quote_yaml(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def is_scalar_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        not isinstance(item, (dict, list)) for item in value
    )


def quote_yaml_list(value: list[Any]) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_yaml_lines(value: Any, indent: int = 0) -> list[str]:
    pad = " " * indent
    if isinstance(value, dict):
        if not value:
            return [f"{pad}{{}}"]
        lines: list[str] = []
        for key, item in value.items():
            if is_scalar_list(item):
                lines.append(f"{pad}{key}: {quote_yaml_list(item)}")
                continue
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.extend(render_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{pad}{key}: {quote_yaml(item)}")
        return lines
    if isinstance(value, list):
        if not value:
            return [f"{pad}[]"]
        lines = []
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append(f"{pad}- {{}}")
                    continue
                first = True
                for key, child in item.items():
                    prefix = "- " if first else "  "
                    if is_scalar_list(child):
                        lines.append(f"{pad}{prefix}{key}: {quote_yaml_list(child)}")
                        first = False
                        continue
                    if isinstance(child, (dict, list)):
                        lines.append(f"{pad}{prefix}{key}:")
                        lines.extend(render_yaml_lines(child, indent + 4))
                    else:
                        lines.append(f"{pad}{prefix}{key}: {quote_yaml(child)}")
                    first = False
            elif isinstance(item, list):
                lines.append(f"{pad}-")
                lines.extend(render_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{pad}- {quote_yaml(item)}")
        return lines
    return [f"{pad}{quote_yaml(value)}"]


def render_yaml_document(record: dict[str, Any]) -> str:
    return "\n".join(render_yaml_lines(record)) + "\n"


def resolve_project_path(project_root: Path, raw_path: str) -> tuple[Path | None, str | None]:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        return None, f"path escapes project root: {raw_path}"
    return resolved, None


def summarize_policy(
    *,
    policy_path: Path,
    project_root: Path,
    expected_policy_id: str | None,
    expected_version: Any,
) -> tuple[dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    if not policy_path.exists():
        return None, [f"active policy ref is missing: {display_path(policy_path, project_root)}"]
    if not policy_path.is_file():
        return None, [f"active policy ref is not a file: {display_path(policy_path, project_root)}"]

    try:
        record = read_minimal_yaml(policy_path)
    except OSError as exc:
        return None, [f"active policy ref cannot be read: {exc}"]

    schema = schema_from_record(record)
    policy_id = record.get("policy_id")
    version = record.get("version")
    if schema != POLICY_SCHEMA:
        warnings.append(
            f"active policy ref has unsupported schema: {schema or 'missing'}"
        )
    if expected_policy_id and policy_id != expected_policy_id:
        warnings.append(
            f"active policy id mismatch: manifest={expected_policy_id}, file={policy_id}"
        )
    if expected_version is not None and version != expected_version:
        warnings.append(
            f"active policy version mismatch: manifest={expected_version}, file={version}"
        )

    summary = {
        "policy_id": policy_id or expected_policy_id,
        "version": version if version is not None else expected_version,
        "path": display_path(policy_path, project_root),
        "title": record.get("title"),
        "status": record.get("status"),
        "schema_version": schema,
    }
    work_profile_applicability = normalize_work_profile_applicability(
        record.get("applies_to_work_profile")
    )
    if work_profile_applicability:
        summary["applies_to_work_profile"] = work_profile_applicability

    return (summary, warnings)


def read_policy_record(policy_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not policy_path.exists() or not policy_path.is_file():
        return None, [f"policy file is not readable: {policy_path}"]
    try:
        record = read_minimal_yaml(policy_path)
    except OSError as exc:
        return None, [f"policy file cannot be read: {exc}"]
    schema = schema_from_record(record)
    if schema != POLICY_SCHEMA:
        return None, [f"unsupported policy schema: {schema or 'missing'}"]
    return record, []


def scalar_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, str):
        return [value]
    return []


def ordered_nonempty_strings(values: list[str] | None) -> list[str]:
    output: list[str] = []
    for value in values or []:
        text = str(value).strip()
        if text and text not in output:
            output.append(text)
    return output


def build_work_profile_applicability_entries(
    *,
    lifecycle_events: list[str] | None = None,
    policy_scopes: list[str] | None = None,
) -> list[dict[str, Any]]:
    normalized_lifecycle_events = ordered_nonempty_strings(lifecycle_events)
    normalized_policy_scopes = ordered_nonempty_strings(policy_scopes)
    if not normalized_lifecycle_events and not normalized_policy_scopes:
        return []
    return [
        {
            "lifecycle_events": normalized_lifecycle_events,
            "policy_scopes": normalized_policy_scopes,
        }
    ]


def build_policy_authoring_review(
    *,
    trigger_event: str | None,
    lifecycle_events: list[str] | None = None,
    policy_scopes: list[str] | None = None,
) -> dict[str, Any]:
    """Project how a new policy plan will be authored without changing policy YAML."""

    normalized_lifecycle_events = ordered_nonempty_strings(lifecycle_events)
    normalized_policy_scopes = ordered_nonempty_strings(policy_scopes)
    hard_gated_by_lifecycle = bool(normalized_lifecycle_events)
    has_scope_filter = bool(normalized_policy_scopes)
    if has_scope_filter and not hard_gated_by_lifecycle:
        mode = "scope_only"
    elif hard_gated_by_lifecycle:
        mode = "lifecycle_gated"
    else:
        mode = "legacy_event_exact"

    warnings: list[str] = []
    if hard_gated_by_lifecycle:
        warnings.append("lifecycle_events_hard_gate_policy_applicability")
    if not has_scope_filter:
        warnings.append("policy_has_no_work_profile_scope_filter")

    return {
        "mode": mode,
        "scope_first": mode == "scope_only",
        "compatibility_trigger_event": trigger_event or "",
        "policy_scopes": normalized_policy_scopes,
        "lifecycle_events": normalized_lifecycle_events,
        "hard_gated_by_lifecycle": hard_gated_by_lifecycle,
        "warnings": warnings,
        "summary": (
            "scope-only policy plan; trigger_event is a compatibility anchor"
            if mode == "scope_only"
            else (
                "lifecycle_events will hard-gate this policy"
                if mode == "lifecycle_gated"
                else "legacy event-exact policy plan without work_profile scopes"
            )
        ),
    }


def normalize_work_profile_applicability(raw: Any) -> dict[str, Any] | None:
    """Project policy work-profile applicability for scope-aware evaluation.

    The minimal YAML reader supports this field as a top-level list of mappings
    with inline lists, for example:

    applies_to_work_profile:
      - lifecycle_events: ["task_start"]
        policy_scopes: ["editing"]
    """

    if raw in (None, [], {}):
        return None
    entries = raw if isinstance(raw, list) else [raw]
    lifecycle_events: list[str] = []
    policy_scopes: list[str] = []
    intent_classes: list[str] = []
    operation_classes: list[str] = []
    output_classes: list[str] = []
    warnings: list[str] = []

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            warnings.append(f"entry_{index + 1}_is_not_a_mapping")
            continue
        lifecycle_events.extend(scalar_list(entry.get("lifecycle_events")))
        policy_scopes.extend(scalar_list(entry.get("policy_scopes")))
        intent_classes.extend(scalar_list(entry.get("intent_classes")))
        operation_classes.extend(scalar_list(entry.get("operation_classes")))
        output_classes.extend(scalar_list(entry.get("output_classes")))

    def dedupe(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result

    projection = {
        "schema": WORK_PROFILE_APPLICABILITY_SCHEMA,
        "status": "declared",
        "lifecycle_events": dedupe(lifecycle_events),
        "policy_scopes": dedupe(policy_scopes),
        "intent_classes": dedupe(intent_classes),
        "operation_classes": dedupe(operation_classes),
        "output_classes": dedupe(output_classes),
        "evaluator_effect": "consumed_by_POLTRIG_03_scope_filter",
        "warnings": warnings,
    }
    if not any(
        projection[key]
        for key in (
            "lifecycle_events",
            "policy_scopes",
            "intent_classes",
            "operation_classes",
            "output_classes",
        )
    ):
        projection["status"] = "declared_empty_or_unreadable"
    return projection


def next_actions_for(status: str) -> list[str]:
    if status == "missing":
        return ["initialize policy store in a later guarded configuration flow"]
    if status == "initialized":
        return ["add approved policies through a later guarded policy configuration flow"]
    if status == "active":
        return ["policy store is readable; exact lifecycle trigger evaluation can run"]
    if status == "stale":
        return ["review manifest and active policy refs before policy-aware evaluation"]
    if status == "conflict":
        return ["resolve policy-store conflicts before trusting policy-aware output"]
    return []


def eval_next_actions_for(status: str, eval_status: str) -> list[str]:
    if eval_status == POLICY_EVAL_STATUS_EVALUATED:
        return ["review triggered policy actions and evidence status"]
    if status == "missing":
        return ["initialize policy store in a later guarded configuration flow"]
    if status == "initialized":
        return ["add approved policies before trigger evaluation can produce matches"]
    if status in {"stale", "conflict"}:
        return ["resolve policy-store issues before trigger evaluation"]
    return ["review policy-store status before trigger evaluation"]


def status_reason_for(status: str) -> str:
    if status == "missing":
        return "policy store adapter ran, but .jikuo/policies is not initialized"
    if status == "initialized":
        return "policy store manifest is readable, but no active policy refs are configured"
    if status == "active":
        return "policy store manifest and active policy refs are readable"
    if status == "stale":
        return "policy store exists, but manifest or active refs need review"
    if status == "conflict":
        return "policy store exists, but conflicting refs or paths prevent reliable use"
    return "policy store status is unknown"


def eval_status_reason_for(
    *, store_status: str, eval_status: str, triggered_count: int
) -> str:
    if eval_status == POLICY_EVAL_STATUS_EVALUATED:
        return (
            f"evaluated active policies against event surface and work profile; "
            f"triggered policies: {triggered_count}"
        )
    if store_status == "missing":
        return "policy store is missing; trigger evaluation was not run"
    if store_status == "initialized":
        return "policy store has no active policy refs; trigger evaluation produced no matches"
    if store_status == "stale":
        return "policy store is stale; trigger evaluation was not trusted"
    if store_status == "conflict":
        return "policy store is conflicting; trigger evaluation was refused"
    return "policy trigger evaluation was not run"


def evidence_check_status_reason_for(
    *, check_status: str, evidence_count: int, missing_count: int
) -> str:
    if check_status == POLICY_EVIDENCE_CHECK_STATUS_CHECKED:
        return (
            f"checked required evidence; evidence status: {evidence_count}; "
            f"missing reports: {missing_count}"
        )
    if check_status == POLICY_EVIDENCE_CHECK_STATUS_REFUSED:
        return "policy evidence check was refused because trigger evaluation was refused"
    return "policy evidence check was not run"


def inspect_policy_store(
    *,
    project_root: Path | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(
        project_root=project_root,
        cwd=cwd,
    )
    store_root = resolved_root / POLICY_STORE_ROOT
    manifest_path = store_root / MANIFEST_NAME
    warnings: list[str] = []
    active_policy_refs: list[dict[str, Any]] = []
    proposal_refs: list[dict[str, Any]] = []
    deprecated_policy_refs: list[dict[str, Any]] = []
    superseded_policy_refs: list[dict[str, Any]] = []

    if not store_root.exists():
        status = "missing"
    elif not store_root.is_dir():
        status = "conflict"
        warnings.append(f"policy store root exists but is not a directory: {store_root}")
    elif not manifest_path.exists():
        status = "stale"
        warnings.append("policy store root exists but manifest.yaml is missing")
    elif not manifest_path.is_file():
        status = "conflict"
        warnings.append("policy store manifest path exists but is not a file")
    else:
        try:
            manifest = read_minimal_yaml(manifest_path)
        except OSError as exc:
            manifest = {}
            warnings.append(f"policy store manifest cannot be read: {exc}")

        schema = schema_from_record(manifest)
        if schema != POLICY_STORE_MANIFEST_SCHEMA:
            warnings.append(
                f"unsupported policy store manifest schema: {schema or 'missing'}"
            )

        raw_active_refs = manifest.get("active_policy_refs", [])
        raw_proposal_refs = manifest.get("proposal_refs", [])
        raw_deprecated_refs = manifest.get("deprecated_policy_refs", [])
        raw_superseded_refs = manifest.get("superseded_policy_refs", [])
        if not isinstance(raw_active_refs, list):
            raw_active_refs = []
            warnings.append("active_policy_refs must be a list")
        if not isinstance(raw_proposal_refs, list):
            raw_proposal_refs = []
            warnings.append("proposal_refs must be a list")
        if not isinstance(raw_deprecated_refs, list):
            raw_deprecated_refs = []
            warnings.append("deprecated_policy_refs must be a list")
        if not isinstance(raw_superseded_refs, list):
            raw_superseded_refs = []
            warnings.append("superseded_policy_refs must be a list")

        seen_policy_ids: set[str] = set()
        duplicate_policy_ids: set[str] = set()
        path_conflict = False
        stale_ref = False
        for ref in raw_active_refs:
            if not isinstance(ref, dict):
                warnings.append("active policy ref must be a mapping")
                stale_ref = True
                continue
            policy_id = ref.get("policy_id")
            if isinstance(policy_id, str):
                if policy_id in seen_policy_ids:
                    duplicate_policy_ids.add(policy_id)
                seen_policy_ids.add(policy_id)
            raw_path = ref.get("path")
            if not isinstance(raw_path, str) or not raw_path:
                warnings.append(f"active policy ref has no path: {policy_id}")
                stale_ref = True
                continue
            policy_path, path_error = resolve_project_path(resolved_root, raw_path)
            if path_error:
                warnings.append(path_error)
                path_conflict = True
                continue
            assert policy_path is not None
            try:
                policy_path.relative_to(store_root.resolve())
            except ValueError:
                warnings.append(f"active policy ref is outside policy store: {raw_path}")
                path_conflict = True
                continue
            summary, ref_warnings = summarize_policy(
                policy_path=policy_path,
                project_root=resolved_root,
                expected_policy_id=policy_id if isinstance(policy_id, str) else None,
                expected_version=ref.get("version"),
            )
            warnings.extend(ref_warnings)
            if ref_warnings:
                stale_ref = True
            if summary:
                active_policy_refs.append(summary)

        if duplicate_policy_ids:
            status = "conflict"
            warnings.extend(
                f"duplicate active policy id: {policy_id}"
                for policy_id in sorted(duplicate_policy_ids)
            )
        elif path_conflict:
            status = "conflict"
        elif schema != POLICY_STORE_MANIFEST_SCHEMA or stale_ref:
            status = "stale"
        elif active_policy_refs:
            status = "active"
        else:
            status = "initialized"

        proposal_refs = [
            ref
            for ref in raw_proposal_refs
            if isinstance(ref, dict)
        ]
        deprecated_policy_refs = [
            ref
            for ref in raw_deprecated_refs
            if isinstance(ref, dict)
        ]
        superseded_policy_refs = [
            ref
            for ref in raw_superseded_refs
            if isinstance(ref, dict)
        ]

    manifest_ref = (
        display_path(manifest_path, resolved_root)
        if manifest_path.exists()
        else None
    )
    return {
        "schema": POLICY_STORE_STATUS_SCHEMA,
        "report_only": True,
        "project_root": str(resolved_root),
        "policy_store_root": str(store_root),
        "manifest_path": str(manifest_path),
        "manifest_ref": manifest_ref,
        "policy_store_status": status,
        "policy_eval_status": POLICY_EVAL_STATUS_NOT_EVALUATED,
        "active_policy_refs": active_policy_refs,
        "proposal_refs": proposal_refs,
        "deprecated_policy_refs": deprecated_policy_refs,
        "superseded_policy_refs": superseded_policy_refs,
        "write_allowed_by_command": False,
        "warnings": warnings,
        "source_refs": CONTRACT_REFS,
        "status_reason": status_reason_for(status),
        "next_actions": next_actions_for(status),
    }


def build_policy_conditions(
    *,
    policy_id: str,
    task_type: str | None,
    jikuo_layer: str | None,
    changed_path_pattern: str | None,
    added_path_pattern: str | None,
) -> list[dict[str, Any]]:
    conditions: list[dict[str, Any]] = []
    if task_type:
        conditions.append(
            {
                "condition_id": f"COND-{slug_token(policy_id)}-task-type",
                "type": "task_type_is",
                "value": task_type,
            }
        )
    if jikuo_layer:
        conditions.append(
            {
                "condition_id": f"COND-{slug_token(policy_id)}-jikuo-layer",
                "type": "jikuo_layer_is",
                "value": jikuo_layer,
            }
        )
    if changed_path_pattern:
        conditions.append(
            {
                "condition_id": f"COND-{slug_token(policy_id)}-changed-path",
                "type": "changed_path_matches",
                "pattern": changed_path_pattern,
            }
        )
    if added_path_pattern:
        conditions.append(
            {
                "condition_id": f"COND-{slug_token(policy_id)}-added-path",
                "type": "added_path_matches",
                "pattern": added_path_pattern,
            }
        )
    return conditions


def build_policy_write_plan(
    *,
    project_root: Path | None = None,
    cwd: Path | None = None,
    policy_id: str | None = None,
    title: str | None = None,
    source_ref: str | None = None,
    source_type: str = "user_natural_language",
    trigger_event: str = "task_start",
    task_type: str | None = None,
    jikuo_layer: str | None = None,
    changed_path_pattern: str | None = None,
    added_path_pattern: str | None = None,
    work_profile_lifecycle_events: list[str] | None = None,
    work_profile_policy_scopes: list[str] | None = None,
    action_type: str = "render_pre_task_review",
    evidence_type: str = "card_rendered",
) -> dict[str, Any]:
    """Build a no-write policy-store write plan for desktop review."""

    status_report = inspect_policy_store(project_root=project_root, cwd=cwd)
    resolved_root = Path(status_report["project_root"])
    resolved_policy_id = normalize_policy_id(policy_id, title)
    warnings = list(status_report["warnings"])
    refusals: list[str] = []

    if not resolved_policy_id:
        refusals.append("policy_id_or_title_required_for_policy_write_plan")
        resolved_policy_id = "POLICY-unresolved"
    if not title:
        refusals.append("title_required_for_policy_write_plan")
    if not trigger_event:
        refusals.append("trigger_event_required_for_policy_write_plan")
    if not action_type:
        refusals.append("action_type_required_for_policy_write_plan")
    if not evidence_type:
        refusals.append("evidence_type_required_for_policy_write_plan")

    plan_id = stable_id(
        "POLICYWRITEPLAN",
        "|".join([resolved_policy_id, title or "", trigger_event or ""]),
    )
    policy_file_ref = f"{POLICY_STORE_ROOT}/approved/{resolved_policy_id}.yaml"
    manifest_ref = f"{POLICY_STORE_ROOT}/{MANIFEST_NAME}"
    decision_id = stable_id(
        "POLICYDECISION",
        "|".join([plan_id, resolved_policy_id, trigger_event or ""]),
    )
    decision_ref = f"{POLICY_STORE_ROOT}/{DECISIONS_DIR_NAME}/{decision_id}.yaml"
    proposal_ref = (
        f"{POLICY_STORE_ROOT}/proposals/"
        f"{stable_id('POLICYPROPOSAL', resolved_policy_id + '|' + (title or ''))}.yaml"
    )
    target_policy_path = resolved_root / policy_file_ref
    target_decision_path = resolved_root / decision_ref
    target_proposal_path = resolved_root / proposal_ref
    active_policy_ids = {
        str(ref.get("policy_id"))
        for ref in status_report["active_policy_refs"]
        if ref.get("policy_id") is not None
    }
    target_collision = target_policy_path.exists() or resolved_policy_id in active_policy_ids
    decision_collision = target_decision_path.exists()
    proposal_collision = target_proposal_path.exists()
    store_status = status_report["policy_store_status"]
    manifest_stale = store_status in {"stale", "conflict"}
    if target_collision:
        refusals.append("target_policy_already_exists_or_active")
    if decision_collision:
        refusals.append("target_decision_already_exists")
    if proposal_collision:
        refusals.append("target_policy_proposal_already_exists")
    if store_status == "conflict":
        refusals.append("policy_store_conflict_must_be_resolved_before_write_plan")

    action_id = f"ACT-{slug_token(action_type)}"
    evidence_id = f"EVD-{slug_token(evidence_type)}"
    trigger_id = f"TRG-{slug_token(trigger_event)}"
    conditions = build_policy_conditions(
        policy_id=resolved_policy_id,
        task_type=task_type,
        jikuo_layer=jikuo_layer,
        changed_path_pattern=changed_path_pattern,
        added_path_pattern=added_path_pattern,
    )
    work_profile_applicability = build_work_profile_applicability_entries(
        lifecycle_events=work_profile_lifecycle_events,
        policy_scopes=work_profile_policy_scopes,
    )
    authoring_review = build_policy_authoring_review(
        trigger_event=trigger_event,
        lifecycle_events=work_profile_lifecycle_events,
        policy_scopes=work_profile_policy_scopes,
    )
    proposed_policy: dict[str, Any] = {
        "schema_version": POLICY_SCHEMA,
        "policy_id": resolved_policy_id,
        "version": 1,
        "status": "active_report_only",
        "title": title,
        "scenario_package": "engineering_governance",
        "source_refs": [
            {
                "type": source_type,
                "ref": source_ref or "<exact user phrase as spoken>",
            }
        ],
        "triggers": [
            {
                "trigger_id": trigger_id,
                "type": "task_lifecycle_event",
                "event": trigger_event,
            }
        ],
        "conditions": conditions,
        "required_actions": [
            {
                "action_id": action_id,
                "type": action_type,
            }
        ],
        "required_evidence": [
            {
                "evidence_id": evidence_id,
                "type": evidence_type,
                "satisfies_action": action_id,
            }
        ],
        "enforcement": {
            "phase": "report_only",
            "level": "review_required",
        },
    }
    if work_profile_applicability:
        proposed_policy["applies_to_work_profile"] = work_profile_applicability
    status = "refused" if refusals else "review"
    return {
        "schema": POLICY_WRITE_PLAN_SCHEMA,
        "schema_version": POLICY_WRITE_PLAN_SCHEMA,
        "report_only": True,
        "plan_id": plan_id,
        "operation": "append_policy" if store_status == "active" else "create_policy",
        "status": status,
        "proposal_ref": proposal_ref,
        "policy_ref": resolved_policy_id,
        "project_root": str(resolved_root),
        "policy_store_status": store_status,
        "policy_store_root": status_report["policy_store_root"],
        "preflight": {
            "project_state_initialized": (
                resolved_root / ".jikuo" / "project_state.yaml"
            ).is_file(),
            "store_exists": (resolved_root / POLICY_STORE_ROOT).exists(),
            "target_collision": target_collision,
            "decision_record_collision": decision_collision,
            "proposal_snapshot_collision": proposal_collision,
            "manifest_stale": manifest_stale,
            "approval_present": False,
        },
        "write_set": [
            {
                "path": policy_file_ref,
                "effect": "create approved policy file",
                "operation": "create",
            },
            {
                "path": decision_ref,
                "effect": "create policy decision record",
                "operation": "create",
            },
            {
                "path": manifest_ref,
                "effect": "create or update policy-store manifest active_policy_refs",
                "operation": "create_or_update",
            },
            {
                "path": proposal_ref,
                "effect": "create policy write proposal snapshot",
                "operation": "create",
            },
        ],
        "non_effects": [
            "does not create .jikuo/policies/",
            "does not write approved policy files",
            "does not update manifest.yaml",
            "does not execute policy actions",
            "does not create task-session evidence",
            "does not promote gates",
        ],
        "approval_required": True,
        "write_allowed_by_command": False,
        "writes_performed": False,
        "guarded_apply_available": False,
        "authoring_review": authoring_review,
        "proposed_policy": proposed_policy,
        "refusal_reasons": refusals,
        "warnings": warnings,
        "source_refs": CONTRACT_REFS,
        "status_reason": (
            "policy write plan is ready for desktop review; no durable write was performed"
            if status == "review"
            else "policy write plan was refused before any durable write"
        ),
        "next_actions": [
            "review the proposed policy, write targets, and non-effects in chat",
            "approve a future guarded policy writer only after the plan is correct",
        ]
        if status == "review"
        else ["resolve refusal reasons before preparing a policy write plan"],
    }


def policy_evolution_recommendations(
    *,
    operation: str,
    feedback_type: str | None,
) -> list[str]:
    if operation == "deprecate_policy":
        return [
            "confirm the policy should stop triggering for future tasks",
            "review the guarded deprecation write command before approval",
            "record a decision explaining why deprecation is preferred over narrowing",
        ]
    if operation == "supersede_policy":
        return [
            "name the replacement policy and the policy/version it supersedes",
            "review the guarded supersession write command before approval",
            "keep the superseded policy available for audit instead of overwriting it",
        ]
    if feedback_type == "not_applicable":
        return [
            "review whether the policy condition is too broad for this task type or layer",
            "add a narrower condition before considering a superseding policy",
            "preserve the not-applicable feedback as evidence for the future revision",
        ]
    if feedback_type == "needs_scope_narrowing":
        return [
            "narrow task_type, jikuo_layer, changed_path, or added_path conditions",
            "keep the current policy active until an approved replacement is written",
            "prepare a supersession or revision proposal after the narrowed condition is explicit",
        ]
    return [
        "review the feedback before changing durable policy configuration",
        "choose refine, deprecate, or supersede as a separate approved operation",
        "keep this plan no-write until the evolution target is explicit",
    ]


def build_policy_evolution_plan(
    *,
    project_root: Path | None = None,
    cwd: Path | None = None,
    policy_id: str | None = None,
    operation: str = "refine_policy",
    feedback_type: str | None = None,
    summary: str | None = None,
    source_ref: str | None = None,
    replacement_policy_id: str | None = None,
    replacement_title: str | None = None,
    replacement_trigger_event: str = "task_start",
    replacement_work_profile_lifecycle_events: list[str] | None = None,
    replacement_work_profile_policy_scopes: list[str] | None = None,
    replacement_task_type: str | None = None,
    replacement_jikuo_layer: str | None = None,
    replacement_changed_path_pattern: str | None = None,
    replacement_added_path_pattern: str | None = None,
    replacement_action_type: str = "render_pre_task_review",
    replacement_evidence_type: str = "card_rendered",
) -> dict[str, Any]:
    """Build a no-write policy evolution plan before any supersession writer."""

    status_report = inspect_policy_store(project_root=project_root, cwd=cwd)
    resolved_root = Path(status_report["project_root"])
    warnings = list(status_report["warnings"])
    refusals: list[str] = []
    target_ref: dict[str, Any] | None = None
    policy_record: dict[str, Any] | None = None
    policy_path_ref: str | None = None
    resolved_replacement_policy_id = normalize_policy_id(
        replacement_policy_id,
        replacement_title,
    )
    replacement_policy_path_ref: str | None = None
    replacement_collision = False

    if not policy_id:
        refusals.append("policy_id_required_for_policy_evolution_plan")
    if operation not in POLICY_EVOLUTION_OPERATIONS:
        refusals.append("unsupported_policy_evolution_operation")
    if feedback_type and feedback_type not in POLICY_FEEDBACK_TYPES:
        refusals.append("unsupported_policy_feedback_type")
    if status_report["policy_store_status"] != "active":
        refusals.append("active_policy_store_required_for_policy_evolution_plan")
    if operation == "supersede_policy":
        if not resolved_replacement_policy_id:
            refusals.append("replacement_policy_id_or_title_required_for_supersession")
            resolved_replacement_policy_id = "POLICY-replacement-unresolved"
        if not replacement_title:
            refusals.append("replacement_title_required_for_supersession")
        if not replacement_action_type:
            refusals.append("replacement_action_type_required_for_supersession")
        if not replacement_evidence_type:
            refusals.append("replacement_evidence_type_required_for_supersession")
        if resolved_replacement_policy_id == policy_id:
            refusals.append("replacement_policy_must_differ_from_target_policy")
        replacement_policy_path_ref = (
            f"{POLICY_STORE_ROOT}/approved/{resolved_replacement_policy_id}.yaml"
        )
        active_policy_ids = {
            str(ref.get("policy_id"))
            for ref in status_report["active_policy_refs"]
            if ref.get("policy_id") is not None
        }
        replacement_collision = (
            (resolved_root / replacement_policy_path_ref).exists()
            or resolved_replacement_policy_id in active_policy_ids
        )
        if replacement_collision:
            refusals.append("replacement_policy_already_exists_or_active")

    if policy_id and status_report["policy_store_status"] == "active":
        for item in status_report["active_policy_refs"]:
            if item.get("policy_id") == policy_id:
                target_ref = item
                break
        if target_ref is None:
            refusals.append("target_policy_not_active")
        else:
            raw_path = target_ref.get("path")
            if isinstance(raw_path, str):
                policy_path_ref = raw_path
                policy_path, path_error = resolve_project_path(resolved_root, raw_path)
                if path_error:
                    refusals.append("target_policy_path_invalid")
                    warnings.append(path_error)
                elif policy_path is not None:
                    policy_record, record_warnings = read_policy_record(policy_path)
                    warnings.extend(record_warnings)
                    if record_warnings:
                        refusals.append("target_policy_record_not_readable")
            else:
                refusals.append("target_policy_path_missing")

    plan_id = stable_id(
        "POLICYEVO",
        "|".join([
            policy_id or "POLICY-unresolved",
            operation,
            feedback_type or "",
            resolved_replacement_policy_id or "",
            summary or "",
        ]),
    )
    decision_id = stable_id(
        "POLICYDECISION",
        "|".join([plan_id, operation, policy_id or "POLICY-unresolved"]),
    )
    decision_ref = f"{POLICY_STORE_ROOT}/{DECISIONS_DIR_NAME}/{decision_id}.yaml"
    manifest_ref = f"{POLICY_STORE_ROOT}/{MANIFEST_NAME}"
    proposal_ref = (
        f"{POLICY_STORE_ROOT}/proposals/"
        f"{stable_id('POLICYEVOPROPOSAL', plan_id + '|' + (policy_id or ''))}.yaml"
    )
    status = "refused" if refusals else "review"
    current_version = (
        policy_record.get("version")
        if policy_record is not None
        else target_ref.get("version") if target_ref else None
    )
    target_trigger_profile: dict[str, Any] | None = None
    if policy_record is not None:
        target_work_profile = normalize_work_profile_applicability(
            policy_record.get("applies_to_work_profile")
        )
        target_trigger_profile = {
            "work_profile": target_work_profile,
            "declared_trigger_events": [
                str(trigger.get("event"))
                for trigger in policy_record.get("triggers", [])
                if isinstance(trigger, dict) and trigger.get("event") is not None
            ]
            if isinstance(policy_record.get("triggers"), list)
            else [],
            "conditions": policy_record.get("conditions")
            if isinstance(policy_record.get("conditions"), list)
            else [],
        }
    resolved_replacement_lifecycle_events = ordered_nonempty_strings(
        replacement_work_profile_lifecycle_events
    )
    resolved_replacement_policy_scopes = ordered_nonempty_strings(
        replacement_work_profile_policy_scopes
    )
    replacement_work_profile_entries = build_work_profile_applicability_entries(
        lifecycle_events=resolved_replacement_lifecycle_events,
        policy_scopes=resolved_replacement_policy_scopes,
    )
    proposed_trigger_profile = {
        "trigger_mode": (
            "scope_first"
            if resolved_replacement_policy_scopes
            and not resolved_replacement_lifecycle_events
            else "event_anchored"
            if resolved_replacement_policy_scopes
            and resolved_replacement_lifecycle_events
            else "legacy_event_only"
            if replacement_trigger_event
            else "unconfigured"
        ),
        "policy_scopes": resolved_replacement_policy_scopes,
        "lifecycle_events": resolved_replacement_lifecycle_events,
        "declared_trigger_event": replacement_trigger_event,
        "conditions": build_policy_conditions(
            policy_id=resolved_replacement_policy_id or "POLICY-replacement-unresolved",
            task_type=replacement_task_type,
            jikuo_layer=replacement_jikuo_layer,
            changed_path_pattern=replacement_changed_path_pattern,
            added_path_pattern=replacement_added_path_pattern,
        ),
    }
    replacement_policy: dict[str, Any] | None = None
    if operation == "supersede_policy" and resolved_replacement_policy_id:
        action_id = f"ACT-{slug_token(replacement_action_type)}"
        evidence_id = f"EVD-{slug_token(replacement_evidence_type)}"
        trigger_id = f"TRG-{slug_token(replacement_trigger_event)}"
        replacement_policy = {
            "schema_version": POLICY_SCHEMA,
            "policy_id": resolved_replacement_policy_id,
            "version": 1,
            "status": "active_report_only",
            "title": replacement_title,
            "scenario_package": "engineering_governance",
            "source_refs": [
                {
                    "type": "policy_supersession",
                    "ref": source_ref or "<exact user phrase as spoken>",
                }
            ],
            "triggers": [
                {
                    "trigger_id": trigger_id,
                    "type": "task_lifecycle_event",
                    "event": replacement_trigger_event,
                }
            ],
            "conditions": build_policy_conditions(
                policy_id=resolved_replacement_policy_id,
                task_type=replacement_task_type,
                jikuo_layer=replacement_jikuo_layer,
                changed_path_pattern=replacement_changed_path_pattern,
                added_path_pattern=replacement_added_path_pattern,
            ),
            "required_actions": [
                {
                    "action_id": action_id,
                    "type": replacement_action_type,
                }
            ],
            "required_evidence": [
                {
                    "evidence_id": evidence_id,
                    "type": replacement_evidence_type,
                    "satisfies_action": action_id,
                }
            ],
            "enforcement": {
                "phase": "report_only",
                "level": "review_required",
            },
            "revision": {
                "version": 1,
                "supersedes": [
                    {
                        "policy_id": policy_id,
                        "version": current_version,
                    }
                ],
                "superseded_by": None,
            },
        }
        if replacement_work_profile_entries:
            replacement_policy["applies_to_work_profile"] = replacement_work_profile_entries
    write_set = [
        {
            "path": proposal_ref,
            "effect": "create policy evolution proposal snapshot",
            "operation": "create",
        },
        {
            "path": decision_ref,
            "effect": "create policy evolution decision record",
            "operation": "create",
        },
        {
            "path": manifest_ref,
            "effect": "update policy-store manifest lifecycle refs",
            "operation": "update",
        },
    ]
    if operation == "refine_policy" and policy_path_ref:
        write_set.insert(
            1,
            {
                "path": policy_path_ref,
                "effect": "update approved policy trigger profile",
                "operation": "update",
            },
        )
    if operation == "supersede_policy" and replacement_policy_path_ref:
        write_set.insert(
            1,
            {
                "path": replacement_policy_path_ref,
                "effect": "create replacement approved policy file",
                "operation": "create",
            },
        )
    return {
        "schema": POLICY_EVOLUTION_PLAN_SCHEMA,
        "schema_version": POLICY_EVOLUTION_PLAN_SCHEMA,
        "report_only": True,
        "plan_id": plan_id,
        "operation": operation,
        "status": status,
        "proposal_ref": proposal_ref,
        "decision_record_ref": decision_ref,
        "project_root": str(resolved_root),
        "policy_store_status": status_report["policy_store_status"],
        "target_policy_ref": policy_id,
        "target_policy_snapshot": {
            "policy_id": policy_id,
            "version": current_version,
            "path": policy_path_ref,
            "title": policy_record.get("title") if policy_record else None,
            "status": policy_record.get("status") if policy_record else None,
        },
        "target_trigger_profile": target_trigger_profile,
        "proposed_trigger_profile": proposed_trigger_profile,
        "replacement_policy_ref": resolved_replacement_policy_id,
        "replacement_policy_path": replacement_policy_path_ref,
        "replacement_policy": replacement_policy,
        "write_set": write_set,
        "preflight": {
            "replacement_policy_collision": replacement_collision,
        },
        "feedback": {
            "feedback_type": feedback_type,
            "summary": summary,
            "source_ref": source_ref or "<exact user phrase as spoken>",
        },
        "recommended_changes": policy_evolution_recommendations(
            operation=operation,
            feedback_type=feedback_type,
        ),
        "future_write_boundary": {
            "requires_new_proposal": True,
            "requires_decision_record": True,
            "requires_guarded_writer": True,
            "writer_implemented": operation in POLICY_EVOLUTION_WRITE_SUPPORTED_OPERATIONS,
        },
        "non_effects": [
            (
                "does not write policy action, evidence, title, or status fields"
                if operation == "refine_policy"
                else "does not write policy files"
            ),
            "does not update manifest.yaml",
            "does not deprecate or supersede active policies",
            "does not execute policy actions",
            "does not promote gates",
        ],
        "write_allowed_by_command": False,
        "writes_performed": False,
        "guarded_apply_available": False,
        "refusal_reasons": sorted(set(refusals)),
        "warnings": warnings,
        "source_refs": CONTRACT_REFS,
        "status_reason": (
            "policy evolution plan is ready for desktop review; no durable write was performed"
            if status == "review"
            else "policy evolution plan was refused before any durable write"
        ),
        "next_actions": (
            [
                "review the proposed policy evolution path in chat",
                "if accepted, approve the generated guarded evolution write command",
            ]
            if operation in POLICY_EVOLUTION_WRITE_SUPPORTED_OPERATIONS
            else [
                "review the proposed policy evolution path in chat",
                "if accepted, implement a separate guarded revision / rollback writer",
            ]
        )
        if status == "review"
        else ["resolve refusal reasons before preparing a policy evolution plan"],
    }


def policy_store_write_next_actions(status: str) -> list[str]:
    if status == "written":
        return [
            "run policy_store.py status to confirm the approved policy is active",
            "use agent_flow.py propose on a matching task to inspect triggered policy output",
        ]
    return ["review refusal reasons before retrying guarded policy-store write"]


def build_policy_manifest_record(
    *,
    project_root: Path,
    policy_id: str,
    policy_path_ref: str,
    proposal_ref: str,
) -> dict[str, Any]:
    state_file = project_root / ".jikuo" / "project_state.yaml"
    project_id = project_state.derive_project_id(project_root)
    if state_file.is_file():
        try:
            state = read_minimal_yaml(state_file)
        except OSError:
            state = {}
        raw_project_id = state.get("project_id")
        if isinstance(raw_project_id, str) and raw_project_id:
            project_id = raw_project_id
    return {
        "schema_version": POLICY_STORE_MANIFEST_SCHEMA,
        "project_id": project_id,
        "store_root": POLICY_STORE_ROOT,
        "active_policy_refs": [
            {
                "policy_id": policy_id,
                "version": 1,
                "path": policy_path_ref,
            }
        ],
        "proposal_refs": [
            {
                "proposal_id": Path(proposal_ref).stem,
                "policy_id": policy_id,
                "path": proposal_ref,
                "status": "approved_for_write",
            }
        ],
        "deprecated_policy_refs": [],
        "superseded_policy_refs": [],
        "last_updated_at": utc_now_iso(),
        "compatibility": {
            "unknown_fields": "preserve",
            "writer": "policy_store_write_mode",
        },
    }


def build_policy_decision_record(
    *,
    plan: dict[str, Any],
    decision_path_ref: str,
    approval_phrase: str,
) -> dict[str, Any]:
    operation = plan["operation"]
    effect = (
        f"{operation} {plan['policy_ref']} and update policy-store manifest active refs"
    )
    return {
        "schema_version": POLICY_DECISION_SCHEMA,
        "decision_id": Path(decision_path_ref).stem,
        "proposal_ref": plan["proposal_ref"],
        "policy_ref": plan["policy_ref"],
        "decision": "approve_write",
        "target": {
            "kind": "approved_policy",
            "ref": plan["policy_ref"],
        },
        "effect": effect,
        "non_effect": "does not execute policy actions, persist evidence, or promote gates",
        "approval_phrase": approval_phrase,
        "created_at": utc_now_iso(),
        "source_plan_ref": plan["plan_id"],
        "source_plan_schema": POLICY_WRITE_PLAN_SCHEMA,
        "storage": {
            "path": decision_path_ref,
            "policy_store_ref": POLICY_STORE_ROOT,
        },
    }


def build_policy_evolution_decision_record(
    *,
    plan: dict[str, Any],
    approval_phrase: str,
) -> dict[str, Any]:
    operation = plan["operation"]
    target_policy_ref = plan["target_policy_ref"]
    decision = (
        "deprecate"
        if operation == "deprecate_policy"
        else "supersede" if operation == "supersede_policy" else operation
    )
    target: dict[str, Any] = {
        "kind": "approved_policy",
        "ref": target_policy_ref,
    }
    if operation == "supersede_policy":
        target = {
            "kind": "approved_policy_supersession",
            "ref": target_policy_ref,
            "replacement_ref": plan.get("replacement_policy_ref"),
        }
    effect = f"{operation} {target_policy_ref} and update policy-store manifest lifecycle refs"
    if operation == "refine_policy":
        effect = f"refine trigger profile for {target_policy_ref}"
    return {
        "schema_version": POLICY_DECISION_SCHEMA,
        "decision_id": Path(plan["decision_record_ref"]).stem,
        "proposal_ref": plan["proposal_ref"],
        "policy_ref": target_policy_ref,
        "decision": decision,
        "target": target,
        "effect": effect,
        "non_effect": "does not execute policy actions, persist evidence, or promote gates",
        "approval_phrase": approval_phrase,
        "created_at": utc_now_iso(),
        "source_plan_ref": plan["plan_id"],
        "source_plan_schema": POLICY_EVOLUTION_PLAN_SCHEMA,
        "storage": {
            "path": plan["decision_record_ref"],
            "policy_store_ref": POLICY_STORE_ROOT,
        },
    }


def active_policy_ref_lines(*, policy_id: str, policy_path_ref: str) -> list[str]:
    return [
        f"  - policy_id: {quote_yaml(policy_id)}",
        "    version: 1",
        f"    path: {quote_yaml(policy_path_ref)}",
    ]


def proposal_ref_lines(
    *,
    policy_id: str,
    proposal_ref: str,
) -> list[str]:
    return [
        f"  - proposal_id: {quote_yaml(Path(proposal_ref).stem)}",
        f"    policy_id: {quote_yaml(policy_id)}",
        f"    path: {quote_yaml(proposal_ref)}",
        '    status: "approved_for_write"',
    ]


def deprecated_policy_ref_lines(
    *,
    policy_id: str,
    policy_path_ref: str,
    version: Any,
    decision_ref: str,
) -> list[str]:
    return [
        f"  - policy_id: {quote_yaml(policy_id)}",
        f"    version: {quote_yaml(version if version is not None else 1)}",
        f"    path: {quote_yaml(policy_path_ref)}",
        '    status: "deprecated"',
        f"    decision_ref: {quote_yaml(decision_ref)}",
        f"    deprecated_at: {quote_yaml(utc_now_iso())}",
    ]


def superseded_policy_ref_lines(
    *,
    policy_id: str,
    policy_path_ref: str,
    version: Any,
    replacement_policy_id: str,
    decision_ref: str,
) -> list[str]:
    return [
        f"  - policy_id: {quote_yaml(policy_id)}",
        f"    version: {quote_yaml(version if version is not None else 1)}",
        f"    path: {quote_yaml(policy_path_ref)}",
        '    status: "superseded"',
        f"    superseded_by: {quote_yaml(replacement_policy_id)}",
        f"    decision_ref: {quote_yaml(decision_ref)}",
        f"    superseded_at: {quote_yaml(utc_now_iso())}",
    ]


def top_level_field_index(lines: list[str], field_name: str) -> int | None:
    prefix = f"{field_name}:"
    for index, line in enumerate(lines):
        if line.strip().startswith(prefix) and not line.startswith(" "):
            return index
    return None


def top_level_section_end(lines: list[str], start_index: int) -> int:
    for index in range(start_index + 1, len(lines)):
        if lines[index].strip() and not lines[index].startswith(" "):
            return index
    return len(lines)


def list_block_for_policy(
    *,
    lines: list[str],
    field_name: str,
    policy_id: str,
) -> tuple[int, int] | None:
    field_index = top_level_field_index(lines, field_name)
    if field_index is None:
        return None
    section_end = top_level_section_end(lines, field_index)
    index = field_index + 1
    while index < section_end:
        line = lines[index]
        if line.startswith("  - "):
            block_start = index
            block_end = section_end
            for next_index in range(index + 1, section_end):
                if lines[next_index].startswith("  - "):
                    block_end = next_index
                    break
            item_text = line.strip()[2:].strip()
            item_policy_id = None
            if item_text.startswith("policy_id:"):
                item_policy_id = unquote_scalar(item_text.split(":", 1)[1])
            else:
                for block_line in lines[block_start + 1:block_end]:
                    stripped = block_line.strip()
                    if stripped.startswith("policy_id:"):
                        item_policy_id = unquote_scalar(stripped.split(":", 1)[1])
                        break
            if item_policy_id == policy_id:
                return block_start, block_end
            index = block_end
            continue
        index += 1
    return None


def normalize_empty_list_field(lines: list[str], field_name: str) -> None:
    field_index = top_level_field_index(lines, field_name)
    if field_index is None:
        return
    section_end = top_level_section_end(lines, field_index)
    has_items = any(
        line.startswith("  - ")
        for line in lines[field_index + 1:section_end]
    )
    if not has_items:
        lines[field_index:section_end] = [f"{field_name}: []"]


def append_deprecated_policy_ref_to_manifest_text(
    *,
    text: str,
    policy_id: str,
    policy_path_ref: str,
    version: Any,
    decision_ref: str,
) -> str:
    """Move one active policy ref into deprecated refs without deleting history."""

    lines = text.splitlines()
    active_block = list_block_for_policy(
        lines=lines,
        field_name="active_policy_refs",
        policy_id=policy_id,
    )
    if active_block is None:
        raise RuntimeError("target active policy ref is missing")
    del lines[active_block[0]:active_block[1]]
    normalize_empty_list_field(lines, "active_policy_refs")

    deprecated_index = top_level_field_index(lines, "deprecated_policy_refs")
    new_ref_lines = deprecated_policy_ref_lines(
        policy_id=policy_id,
        policy_path_ref=policy_path_ref,
        version=version,
        decision_ref=decision_ref,
    )
    if deprecated_index is None:
        lines.append("deprecated_policy_refs:")
        lines.extend(new_ref_lines)
    else:
        deprecated_line = lines[deprecated_index].strip()
        if deprecated_line == "deprecated_policy_refs: []":
            lines[deprecated_index:deprecated_index + 1] = [
                "deprecated_policy_refs:",
                *new_ref_lines,
            ]
        elif deprecated_line == "deprecated_policy_refs:":
            insert_index = top_level_section_end(lines, deprecated_index)
            lines[insert_index:insert_index] = new_ref_lines
        else:
            raise RuntimeError("manifest deprecated_policy_refs field has unsupported shape")

    now = utc_now_iso()
    for index, line in enumerate(lines):
        if line.strip().startswith("last_updated_at:"):
            lines[index] = f"last_updated_at: {quote_yaml(now)}"
            break
    else:
        lines.append(f"last_updated_at: {quote_yaml(now)}")

    return "\n".join(lines) + "\n"


def append_superseded_policy_ref_to_manifest_text(
    *,
    text: str,
    policy_id: str,
    policy_path_ref: str,
    version: Any,
    replacement_policy_id: str,
    replacement_policy_path_ref: str,
    decision_ref: str,
) -> str:
    """Replace one active policy ref while preserving lifecycle history."""

    lines = text.splitlines()
    active_block = list_block_for_policy(
        lines=lines,
        field_name="active_policy_refs",
        policy_id=policy_id,
    )
    if active_block is None:
        raise RuntimeError("target active policy ref is missing")
    del lines[active_block[0]:active_block[1]]
    normalize_empty_list_field(lines, "active_policy_refs")

    manifest_text = "\n".join(lines) + "\n"
    manifest_text = append_active_policy_ref_to_manifest_text(
        text=manifest_text,
        policy_id=replacement_policy_id,
        policy_path_ref=replacement_policy_path_ref,
    )
    lines = manifest_text.splitlines()

    superseded_index = top_level_field_index(lines, "superseded_policy_refs")
    new_ref_lines = superseded_policy_ref_lines(
        policy_id=policy_id,
        policy_path_ref=policy_path_ref,
        version=version,
        replacement_policy_id=replacement_policy_id,
        decision_ref=decision_ref,
    )
    if superseded_index is None:
        lines.append("superseded_policy_refs:")
        lines.extend(new_ref_lines)
    else:
        superseded_line = lines[superseded_index].strip()
        if superseded_line == "superseded_policy_refs: []":
            lines[superseded_index:superseded_index + 1] = [
                "superseded_policy_refs:",
                *new_ref_lines,
            ]
        elif superseded_line == "superseded_policy_refs:":
            insert_index = top_level_section_end(lines, superseded_index)
            lines[insert_index:insert_index] = new_ref_lines
        else:
            raise RuntimeError("manifest superseded_policy_refs field has unsupported shape")

    now = utc_now_iso()
    for index, line in enumerate(lines):
        if line.strip().startswith("last_updated_at:"):
            lines[index] = f"last_updated_at: {quote_yaml(now)}"
            break
    else:
        lines.append(f"last_updated_at: {quote_yaml(now)}")

    return "\n".join(lines) + "\n"


def append_active_policy_ref_to_manifest_text(
    *,
    text: str,
    policy_id: str,
    policy_path_ref: str,
) -> str:
    """Append one active policy ref while preserving unrelated manifest text."""

    lines = text.splitlines()
    active_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip().startswith("active_policy_refs:"):
            active_index = index
            break
    if active_index is None:
        raise RuntimeError("manifest active_policy_refs field is missing")

    new_ref_lines = active_policy_ref_lines(
        policy_id=policy_id,
        policy_path_ref=policy_path_ref,
    )
    active_line = lines[active_index].strip()
    if active_line == "active_policy_refs: []":
        lines[active_index:active_index + 1] = ["active_policy_refs:", *new_ref_lines]
    elif active_line == "active_policy_refs:":
        insert_index = len(lines)
        for index in range(active_index + 1, len(lines)):
            if lines[index].strip() and not lines[index].startswith(" "):
                insert_index = index
                break
        lines[insert_index:insert_index] = new_ref_lines
    else:
        raise RuntimeError("manifest active_policy_refs field has unsupported shape")

    now = utc_now_iso()
    for index, line in enumerate(lines):
        if line.strip().startswith("last_updated_at:"):
            lines[index] = f"last_updated_at: {quote_yaml(now)}"
            break
    else:
        lines.append(f"last_updated_at: {quote_yaml(now)}")

    return "\n".join(lines) + "\n"


def append_proposal_ref_to_manifest_text(
    *,
    text: str,
    policy_id: str,
    proposal_ref: str,
) -> str:
    """Append one proposal ref while preserving unrelated manifest text."""

    lines = text.splitlines()
    proposal_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip().startswith("proposal_refs:"):
            proposal_index = index
            break
    new_ref_lines = proposal_ref_lines(
        policy_id=policy_id,
        proposal_ref=proposal_ref,
    )
    if proposal_index is None:
        lines.append("proposal_refs:")
        lines.extend(new_ref_lines)
    else:
        proposal_line = lines[proposal_index].strip()
        if proposal_line == "proposal_refs: []":
            lines[proposal_index:proposal_index + 1] = [
                "proposal_refs:",
                *new_ref_lines,
            ]
        elif proposal_line == "proposal_refs:":
            insert_index = len(lines)
            for index in range(proposal_index + 1, len(lines)):
                if lines[index].strip() and not lines[index].startswith(" "):
                    insert_index = index
                    break
            lines[insert_index:insert_index] = new_ref_lines
        else:
            raise RuntimeError("manifest proposal_refs field has unsupported shape")

    now = utc_now_iso()
    for index, line in enumerate(lines):
        if line.strip().startswith("last_updated_at:"):
            lines[index] = f"last_updated_at: {quote_yaml(now)}"
            break
    else:
        lines.append(f"last_updated_at: {quote_yaml(now)}")

    return "\n".join(lines) + "\n"


def next_policy_version(value: Any) -> int:
    try:
        return int(value) + 1
    except (TypeError, ValueError):
        return 1


def replace_top_level_field_text(*, text: str, field_name: str, value: Any) -> str:
    lines = text.splitlines()
    rendered = render_yaml_lines({field_name: value})
    field_index = top_level_field_index(lines, field_name)
    if field_index is None:
        lines.extend(rendered)
    else:
        section_end = top_level_section_end(lines, field_index)
        lines[field_index:section_end] = rendered
    return "\n".join(lines) + "\n"


def update_active_policy_ref_version_in_manifest_text(
    *,
    text: str,
    policy_id: str,
    version: Any,
) -> str:
    lines = text.splitlines()
    active_block = list_block_for_policy(
        lines=lines,
        field_name="active_policy_refs",
        policy_id=policy_id,
    )
    if active_block is None:
        raise RuntimeError("target active policy ref is missing")
    block_start, block_end = active_block
    version_line = None
    for index in range(block_start + 1, block_end):
        if lines[index].strip().startswith("version:"):
            version_line = index
            break
    if version_line is None:
        lines.insert(block_start + 1, f"    version: {quote_yaml(version)}")
    else:
        lines[version_line] = f"    version: {quote_yaml(version)}"

    now = utc_now_iso()
    for index, line in enumerate(lines):
        if line.strip().startswith("last_updated_at:"):
            lines[index] = f"last_updated_at: {quote_yaml(now)}"
            break
    else:
        lines.append(f"last_updated_at: {quote_yaml(now)}")
    return "\n".join(lines) + "\n"


def build_refined_policy_text_from_plan(
    *,
    original_text: str,
    plan: dict[str, Any],
) -> tuple[str, int]:
    proposed = plan.get("proposed_trigger_profile") or {}
    target = plan.get("target_policy_snapshot") or {}
    new_version = next_policy_version(target.get("version"))
    trigger_event = str(proposed.get("declared_trigger_event") or "task_start")
    policy_ref = str(plan.get("target_policy_ref") or "POLICY-refined")
    triggers = [
        {
            "trigger_id": f"TRG-{slug_token(trigger_event)}",
            "type": "task_lifecycle_event",
            "event": trigger_event,
        }
    ]
    work_profile_entries = build_work_profile_applicability_entries(
        lifecycle_events=scalar_list(proposed.get("lifecycle_events")),
        policy_scopes=scalar_list(proposed.get("policy_scopes")),
    )
    conditions = proposed.get("conditions")
    if not isinstance(conditions, list):
        conditions = build_policy_conditions(
            policy_id=policy_ref,
            task_type=None,
            jikuo_layer=None,
            changed_path_pattern=None,
            added_path_pattern=None,
        )

    refined_text = original_text
    refined_text = replace_top_level_field_text(
        text=refined_text,
        field_name="version",
        value=new_version,
    )
    refined_text = replace_top_level_field_text(
        text=refined_text,
        field_name="triggers",
        value=triggers,
    )
    refined_text = replace_top_level_field_text(
        text=refined_text,
        field_name="conditions",
        value=conditions,
    )
    refined_text = replace_top_level_field_text(
        text=refined_text,
        field_name="applies_to_work_profile",
        value=work_profile_entries,
    )
    return refined_text, new_version


def policy_record_matches_refinement_plan(
    *,
    record: dict[str, Any] | None,
    plan: dict[str, Any],
) -> bool:
    if not isinstance(record, dict):
        return False
    proposed = plan.get("proposed_trigger_profile") or {}
    work_profile = normalize_work_profile_applicability(
        record.get("applies_to_work_profile")
    ) or {
        "lifecycle_events": [],
        "policy_scopes": [],
    }
    declared_events = [
        str(trigger.get("event"))
        for trigger in record.get("triggers", [])
        if isinstance(trigger, dict) and trigger.get("event") is not None
    ] if isinstance(record.get("triggers"), list) else []
    conditions = record.get("conditions")
    if not isinstance(conditions, list):
        conditions = []
    expected_conditions = proposed.get("conditions")
    if not isinstance(expected_conditions, list):
        expected_conditions = []
    return (
        scalar_list(work_profile.get("policy_scopes"))
        == scalar_list(proposed.get("policy_scopes"))
        and scalar_list(work_profile.get("lifecycle_events"))
        == scalar_list(proposed.get("lifecycle_events"))
        and declared_events == [str(proposed.get("declared_trigger_event") or "task_start")]
        and conditions == expected_conditions
    )


def build_policy_write_refusal_result(
    *,
    plan: dict[str, Any],
    refusal_reasons: list[str],
    approval_phrase: str | None,
    error: str = "preflight rejected policy-store write",
) -> dict[str, Any]:
    return {
        "schema": POLICY_WRITE_RESULT_SCHEMA,
        "schema_version": POLICY_WRITE_RESULT_SCHEMA,
        "status": "refused",
        "write_performed": False,
        "operation": plan["operation"],
        "plan_ref": plan["plan_id"],
        "policy_ref": plan["policy_ref"],
        "project_root": plan["project_root"],
        "policy_store_status_before": plan["policy_store_status"],
        "policy_store_status_after": plan["policy_store_status"],
        "written_paths": [],
        "created_paths": [],
        "proposal_ref": plan.get("proposal_ref"),
        "decision_record_ref": (
            plan["write_set"][1]["path"]
            if len(plan.get("write_set", [])) > 1
            else None
        ),
        "refusal_reasons": refusal_reasons,
        "warnings": plan["warnings"],
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": "JIKUO approved policy-store write",
            "decision_effect": "create or append approved policy file and policy manifest ref",
            "decision_noneffect": "does not execute policy actions or promote gates",
            "source_plan_schema": POLICY_WRITE_PLAN_SCHEMA,
            "source_plan_ref": plan["plan_id"],
        }
        if approval_phrase
        else None,
        "error": error,
        "post_write_verification": {
            "reread_ok": False,
            "proposal_snapshot_written": False,
            "decision_record_written": False,
            "manifest_updated": False,
            "active_policy_resolvable": False,
        },
        "next_actions": policy_store_write_next_actions("refused"),
    }


def policy_evolution_write_next_actions(status: str) -> list[str]:
    if status == "written":
        return [
            "run policy_store.py status to confirm lifecycle refs are updated",
            "use policy_store.py evaluate to confirm the changed policy lifecycle behaves as intended",
        ]
    return ["review refusal reasons before retrying guarded policy evolution write"]


def build_policy_evolution_write_refusal_result(
    *,
    plan: dict[str, Any],
    refusal_reasons: list[str],
    approval_phrase: str | None,
    error: str = "preflight rejected policy evolution write",
) -> dict[str, Any]:
    return {
        "schema": POLICY_WRITE_RESULT_SCHEMA,
        "schema_version": POLICY_WRITE_RESULT_SCHEMA,
        "status": "refused",
        "write_performed": False,
        "operation": plan["operation"],
        "plan_ref": plan["plan_id"],
        "policy_ref": plan["target_policy_ref"],
        "replacement_policy_ref": plan.get("replacement_policy_ref"),
        "project_root": plan["project_root"],
        "policy_store_status_before": plan["policy_store_status"],
        "policy_store_status_after": plan["policy_store_status"],
        "written_paths": [],
        "created_paths": [],
        "proposal_ref": plan.get("proposal_ref"),
        "decision_record_ref": plan.get("decision_record_ref"),
        "refusal_reasons": refusal_reasons,
        "warnings": plan["warnings"],
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": "JIKUO policy evolution write",
            "decision_effect": f"{plan['operation']} {plan['target_policy_ref']}",
            "decision_noneffect": "does not execute policy actions or promote gates",
            "source_plan_schema": POLICY_EVOLUTION_PLAN_SCHEMA,
            "source_plan_ref": plan["plan_id"],
        }
        if approval_phrase
        else None,
        "error": error,
        "post_write_verification": {
            "reread_ok": False,
            "proposal_snapshot_written": False,
            "decision_record_written": False,
            "manifest_updated": False,
            "active_policy_resolvable": False,
            "target_policy_refined": False,
            "target_policy_version_updated": False,
            "target_policy_deprecated": False,
            "target_policy_superseded": False,
            "replacement_policy_active": False,
        },
        "next_actions": policy_evolution_write_next_actions("refused"),
    }


def write_policy_evolution_from_plan(
    *,
    project_root: Path | None = None,
    policy_id: str | None = None,
    operation: str = "deprecate_policy",
    feedback_type: str | None = None,
    summary: str | None = None,
    source_ref: str | None = None,
    replacement_policy_id: str | None = None,
    replacement_title: str | None = None,
    replacement_trigger_event: str = "task_start",
    replacement_work_profile_lifecycle_events: list[str] | None = None,
    replacement_work_profile_policy_scopes: list[str] | None = None,
    replacement_task_type: str | None = None,
    replacement_jikuo_layer: str | None = None,
    replacement_changed_path_pattern: str | None = None,
    replacement_added_path_pattern: str | None = None,
    replacement_action_type: str = "render_pre_task_review",
    replacement_evidence_type: str = "card_rendered",
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_policy_evolution_plan(
        project_root=project_root,
        policy_id=policy_id,
        operation=operation,
        feedback_type=feedback_type,
        summary=summary,
        source_ref=source_ref,
        replacement_policy_id=replacement_policy_id,
        replacement_title=replacement_title,
        replacement_trigger_event=replacement_trigger_event,
        replacement_work_profile_lifecycle_events=replacement_work_profile_lifecycle_events,
        replacement_work_profile_policy_scopes=replacement_work_profile_policy_scopes,
        replacement_task_type=replacement_task_type,
        replacement_jikuo_layer=replacement_jikuo_layer,
        replacement_changed_path_pattern=replacement_changed_path_pattern,
        replacement_added_path_pattern=replacement_added_path_pattern,
        replacement_action_type=replacement_action_type,
        replacement_evidence_type=replacement_evidence_type,
    )
    refusal_reasons = list(plan["refusal_reasons"])
    if operation not in POLICY_EVOLUTION_WRITE_SUPPORTED_OPERATIONS:
        refusal_reasons.append("unsupported_policy_evolution_writer_operation")
    if not confirmed:
        refusal_reasons.append("missing_confirmation_flag")
    if not approval_phrase:
        refusal_reasons.append("approval_evidence_missing")
    if plan["policy_store_status"] != "active":
        refusal_reasons.append("active_policy_store_required_for_policy_evolution_write")
    if refusal_reasons:
        return (
            build_policy_evolution_write_refusal_result(
                plan=plan,
                refusal_reasons=sorted(set(refusal_reasons)),
                approval_phrase=approval_phrase,
            ),
            2,
        )

    project_root_path = Path(plan["project_root"])
    store_root = project_root_path / POLICY_STORE_ROOT
    approved_root = store_root / "approved"
    decisions_root = store_root / DECISIONS_DIR_NAME
    proposals_root = store_root / PROPOSALS_DIR_NAME
    manifest_ref = f"{POLICY_STORE_ROOT}/{MANIFEST_NAME}"
    manifest_path = project_root_path / manifest_ref
    proposal_ref = plan["proposal_ref"]
    decision_ref = plan["decision_record_ref"]
    proposal_path = project_root_path / proposal_ref
    decision_path = project_root_path / decision_ref
    replacement_policy_path_ref = plan.get("replacement_policy_path")
    replacement_policy_path = (
        project_root_path / replacement_policy_path_ref
        if isinstance(replacement_policy_path_ref, str)
        else None
    )
    target_policy_path: Path | None = None
    target_policy_path_ref: str | None = None
    temp_proposal_path = proposal_path.with_suffix(proposal_path.suffix + ".tmp")
    temp_decision_path = decision_path.with_suffix(decision_path.suffix + ".tmp")
    temp_manifest_path = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    temp_replacement_policy_path = (
        replacement_policy_path.with_suffix(replacement_policy_path.suffix + ".tmp")
        if replacement_policy_path is not None
        else None
    )
    temp_target_policy_path: Path | None = None
    created_paths: list[str] = []
    written_paths: list[str] = []
    proposal_created = False
    decision_created = False
    replacement_policy_created = False
    target_policy_updated = False
    manifest_updated = False
    original_target_policy_text: str | None = None
    refined_policy_version: int | None = None

    try:
        if not manifest_path.exists():
            return (
                build_policy_evolution_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["manifest_missing_at_write_time"],
                    approval_phrase=approval_phrase,
                ),
                2,
            )
        if proposal_path.exists():
            return (
                build_policy_evolution_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["proposal_snapshot_already_exists_at_write_time"],
                    approval_phrase=approval_phrase,
                ),
                2,
            )
        if decision_path.exists():
            return (
                build_policy_evolution_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["decision_record_already_exists_at_write_time"],
                    approval_phrase=approval_phrase,
                ),
                2,
            )
        if operation == "supersede_policy":
            if replacement_policy_path is None:
                return (
                    build_policy_evolution_write_refusal_result(
                        plan=plan,
                        refusal_reasons=["replacement_policy_path_missing_at_write_time"],
                        approval_phrase=approval_phrase,
                    ),
                    2,
                )
            if replacement_policy_path.exists():
                return (
                    build_policy_evolution_write_refusal_result(
                        plan=plan,
                        refusal_reasons=["replacement_policy_already_exists_at_write_time"],
                        approval_phrase=approval_phrase,
                    ),
                    2,
                )
        if not approved_root.exists():
            approved_root.mkdir()
            created_paths.append(f"{POLICY_STORE_ROOT}/approved/")
        if not decisions_root.exists():
            decisions_root.mkdir()
            created_paths.append(f"{POLICY_STORE_ROOT}/{DECISIONS_DIR_NAME}/")
        if not proposals_root.exists():
            proposals_root.mkdir()
            created_paths.append(f"{POLICY_STORE_ROOT}/{PROPOSALS_DIR_NAME}/")

        target = plan["target_policy_snapshot"]
        policy_path_ref = target.get("path")
        if not isinstance(policy_path_ref, str) or not policy_path_ref:
            return (
                build_policy_evolution_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["target_policy_path_missing_at_write_time"],
                    approval_phrase=approval_phrase,
                ),
                2,
            )
        target_policy_path_ref = policy_path_ref
        resolved_target_policy_path, target_path_error = resolve_project_path(
            project_root_path,
            policy_path_ref,
        )
        if target_path_error or resolved_target_policy_path is None:
            return (
                build_policy_evolution_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["target_policy_path_invalid_at_write_time"],
                    approval_phrase=approval_phrase,
                    error=target_path_error or "target policy path invalid",
                ),
                2,
            )
        target_policy_path = resolved_target_policy_path
        if operation == "refine_policy":
            if not target_policy_path.is_file():
                return (
                    build_policy_evolution_write_refusal_result(
                        plan=plan,
                        refusal_reasons=["target_policy_file_missing_at_write_time"],
                        approval_phrase=approval_phrase,
                    ),
                    2,
                )
            original_target_policy_text = target_policy_path.read_text(encoding="utf-8")
            refined_policy_text, refined_policy_version = build_refined_policy_text_from_plan(
                original_text=original_target_policy_text,
                plan=plan,
            )
            temp_target_policy_path = target_policy_path.with_suffix(
                target_policy_path.suffix + ".tmp"
            )
            temp_target_policy_path.write_text(
                refined_policy_text,
                encoding="utf-8",
                newline="\n",
            )
        if operation == "supersede_policy":
            replacement_policy_ref = plan.get("replacement_policy_ref")
            if not isinstance(replacement_policy_ref, str) or not replacement_policy_ref:
                return (
                    build_policy_evolution_write_refusal_result(
                        plan=plan,
                        refusal_reasons=["replacement_policy_ref_missing_at_write_time"],
                        approval_phrase=approval_phrase,
                    ),
                    2,
                )
            if not isinstance(replacement_policy_path_ref, str) or not replacement_policy_path_ref:
                return (
                    build_policy_evolution_write_refusal_result(
                        plan=plan,
                        refusal_reasons=["replacement_policy_path_missing_at_write_time"],
                        approval_phrase=approval_phrase,
                    ),
                    2,
                )
            manifest_text = append_superseded_policy_ref_to_manifest_text(
                text=manifest_path.read_text(encoding="utf-8"),
                policy_id=plan["target_policy_ref"],
                policy_path_ref=policy_path_ref,
                version=target.get("version"),
                replacement_policy_id=replacement_policy_ref,
                replacement_policy_path_ref=replacement_policy_path_ref,
                decision_ref=decision_ref,
            )
        elif operation == "refine_policy":
            manifest_text = update_active_policy_ref_version_in_manifest_text(
                text=manifest_path.read_text(encoding="utf-8"),
                policy_id=plan["target_policy_ref"],
                version=refined_policy_version,
            )
        else:
            manifest_text = append_deprecated_policy_ref_to_manifest_text(
                text=manifest_path.read_text(encoding="utf-8"),
                policy_id=plan["target_policy_ref"],
                policy_path_ref=policy_path_ref,
                version=target.get("version"),
                decision_ref=decision_ref,
            )
        manifest_policy_ref = (
            plan.get("replacement_policy_ref")
            if operation == "supersede_policy"
            else plan["target_policy_ref"]
        )
        manifest_text = append_proposal_ref_to_manifest_text(
            text=manifest_text,
            policy_id=str(manifest_policy_ref),
            proposal_ref=proposal_ref,
        )
        temp_proposal_path.write_text(
            render_yaml_document(dict(plan)),
            encoding="utf-8",
            newline="\n",
        )
        if operation == "supersede_policy":
            replacement_policy = plan.get("replacement_policy")
            if not isinstance(replacement_policy, dict):
                return (
                    build_policy_evolution_write_refusal_result(
                        plan=plan,
                        refusal_reasons=["replacement_policy_missing_at_write_time"],
                        approval_phrase=approval_phrase,
                    ),
                    2,
                )
            assert temp_replacement_policy_path is not None
            temp_replacement_policy_path.write_text(
                render_yaml_document(replacement_policy),
                encoding="utf-8",
                newline="\n",
            )
        temp_decision_path.write_text(
            render_yaml_document(
                build_policy_evolution_decision_record(
                    plan=plan,
                    approval_phrase=approval_phrase,
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        temp_manifest_path.write_text(
            manifest_text,
            encoding="utf-8",
            newline="\n",
        )
        try:
            fd = os.open(proposal_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise RuntimeError("policy evolution proposal snapshot already exists") from None
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(temp_proposal_path.read_text(encoding="utf-8"))
        proposal_created = True
        temp_proposal_path.unlink(missing_ok=True)
        written_paths.append(proposal_ref)

        if operation == "supersede_policy":
            assert replacement_policy_path is not None
            assert temp_replacement_policy_path is not None
            try:
                fd = os.open(replacement_policy_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                raise RuntimeError("replacement policy file already exists") from None
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(temp_replacement_policy_path.read_text(encoding="utf-8"))
            replacement_policy_created = True
            temp_replacement_policy_path.unlink(missing_ok=True)
            written_paths.append(str(replacement_policy_path_ref))

        if operation == "refine_policy":
            if temp_target_policy_path is None or target_policy_path is None:
                raise RuntimeError("refined policy temp path was not prepared")
            os.replace(temp_target_policy_path, target_policy_path)
            target_policy_updated = True
            written_paths.append(str(target_policy_path_ref))

        try:
            fd = os.open(decision_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise RuntimeError("policy evolution decision record already exists") from None
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(temp_decision_path.read_text(encoding="utf-8"))
        decision_created = True
        temp_decision_path.unlink(missing_ok=True)
        written_paths.append(decision_ref)

        os.replace(temp_manifest_path, manifest_path)
        manifest_updated = True
        temp_manifest_path.unlink(missing_ok=True)
        written_paths.append(manifest_ref)
    except Exception as exc:
        temp_paths = [temp_proposal_path, temp_decision_path, temp_manifest_path]
        if temp_replacement_policy_path is not None:
            temp_paths.append(temp_replacement_policy_path)
        if temp_target_policy_path is not None:
            temp_paths.append(temp_target_policy_path)
        for temp_path in temp_paths:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
        if proposal_created and not manifest_updated and proposal_path.exists():
            proposal_path.unlink(missing_ok=True)
        if (
            replacement_policy_created
            and not manifest_updated
            and replacement_policy_path is not None
            and replacement_policy_path.exists()
        ):
            replacement_policy_path.unlink(missing_ok=True)
        if (
            target_policy_updated
            and not manifest_updated
            and target_policy_path is not None
            and original_target_policy_text is not None
        ):
            target_policy_path.write_text(
                original_target_policy_text,
                encoding="utf-8",
                newline="\n",
            )
        if decision_created and not manifest_updated and decision_path.exists():
            decision_path.unlink(missing_ok=True)
        return (
            build_policy_evolution_write_refusal_result(
                plan=plan,
                refusal_reasons=["policy_evolution_write_failed"],
                approval_phrase=approval_phrase,
                error=str(exc),
            ),
            2,
        )

    status_after = inspect_policy_store(project_root=project_root_path)
    target_active = any(
        ref.get("policy_id") == plan["target_policy_ref"]
        for ref in status_after["active_policy_refs"]
    )
    target_deprecated = any(
        ref.get("policy_id") == plan["target_policy_ref"]
        for ref in status_after.get("deprecated_policy_refs", [])
    )
    target_superseded = any(
        ref.get("policy_id") == plan["target_policy_ref"]
        for ref in status_after.get("superseded_policy_refs", [])
    )
    replacement_policy_ref = plan.get("replacement_policy_ref")
    replacement_active = bool(
        operation == "supersede_policy"
        and replacement_policy_ref
        and any(
            ref.get("policy_id") == replacement_policy_ref
            for ref in status_after["active_policy_refs"]
        )
    )
    target_policy_refined = False
    target_policy_version_updated = False
    if operation == "refine_policy" and target_policy_path is not None:
        refined_record, _record_warnings = read_policy_record(target_policy_path)
        target_policy_refined = policy_record_matches_refinement_plan(
            record=refined_record,
            plan=plan,
        )
        if refined_record is not None:
            target_policy_version_updated = (
                refined_record.get("version")
                == refined_policy_version
                and refined_record.get("version")
                != plan["target_policy_snapshot"].get("version")
            )
    if operation == "deprecate_policy":
        ok = target_deprecated and not target_active
    elif operation == "supersede_policy":
        ok = target_superseded and replacement_active and not target_active
    else:
        ok = target_active and target_policy_refined and target_policy_version_updated
    return (
        {
            "schema": POLICY_WRITE_RESULT_SCHEMA,
            "schema_version": POLICY_WRITE_RESULT_SCHEMA,
            "status": "written" if ok else "failed",
            "write_performed": True,
            "operation": plan["operation"],
            "plan_ref": plan["plan_id"],
            "policy_ref": plan["target_policy_ref"],
            "replacement_policy_ref": plan.get("replacement_policy_ref"),
            "project_root": plan["project_root"],
            "policy_store_status_before": plan["policy_store_status"],
            "policy_store_status_after": status_after["policy_store_status"],
            "written_paths": written_paths,
            "created_paths": created_paths,
            "proposal_ref": proposal_ref,
            "decision_record_ref": decision_ref,
            "refusal_reasons": [],
            "warnings": plan["warnings"] + status_after["warnings"],
            "approval_record": {
                "phrase": approval_phrase,
                "decision_target": "JIKUO policy evolution write",
                "decision_effect": f"{plan['operation']} {plan['target_policy_ref']}",
                "decision_noneffect": "does not execute policy actions or promote gates",
                "source_plan_schema": POLICY_EVOLUTION_PLAN_SCHEMA,
                "source_plan_ref": plan["plan_id"],
            },
            "error": None if ok else "post-write policy evolution verification failed",
            "post_write_verification": {
                "reread_ok": status_after["policy_store_status"] in {"initialized", "active"},
                "proposal_snapshot_written": proposal_path.is_file(),
                "decision_record_written": decision_path.is_file(),
                "manifest_updated": manifest_ref in {status_after.get("manifest_ref"), manifest_ref},
                "active_policy_resolvable": target_active,
                "target_policy_active": target_active,
                "target_policy_refined": target_policy_refined,
                "target_policy_version_updated": target_policy_version_updated,
                "target_policy_deprecated": target_deprecated,
                "target_policy_superseded": target_superseded,
                "replacement_policy_active": replacement_active,
            },
            "next_actions": policy_evolution_write_next_actions(
                "written" if ok else "refused"
            ),
        },
        0 if ok else 2,
    )


def write_policy_from_plan(
    *,
    project_root: Path | None = None,
    policy_id: str | None = None,
    title: str | None = None,
    source_ref: str | None = None,
    source_type: str = "user_natural_language",
    trigger_event: str = "task_start",
    task_type: str | None = None,
    jikuo_layer: str | None = None,
    changed_path_pattern: str | None = None,
    added_path_pattern: str | None = None,
    work_profile_lifecycle_events: list[str] | None = None,
    work_profile_policy_scopes: list[str] | None = None,
    action_type: str = "render_pre_task_review",
    evidence_type: str = "card_rendered",
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_policy_write_plan(
        project_root=project_root,
        policy_id=policy_id,
        title=title,
        source_ref=source_ref,
        source_type=source_type,
        trigger_event=trigger_event,
        task_type=task_type,
        jikuo_layer=jikuo_layer,
        changed_path_pattern=changed_path_pattern,
        added_path_pattern=added_path_pattern,
        work_profile_lifecycle_events=work_profile_lifecycle_events,
        work_profile_policy_scopes=work_profile_policy_scopes,
        action_type=action_type,
        evidence_type=evidence_type,
    )
    refusal_reasons = list(plan["refusal_reasons"])
    if not confirmed:
        refusal_reasons.append("missing_confirmation_flag")
    if not approval_phrase:
        refusal_reasons.append("approval_evidence_missing")
    if not plan["preflight"]["project_state_initialized"]:
        refusal_reasons.append("project_state_not_initialized")
    if plan["policy_store_status"] not in {"missing", "initialized", "active"}:
        refusal_reasons.append("policy_store_status_not_supported_by_guarded_writer")
    if plan["preflight"]["manifest_stale"]:
        refusal_reasons.append("manifest_stale_or_conflict")
    if refusal_reasons:
        return (
            build_policy_write_refusal_result(
                plan=plan,
                refusal_reasons=sorted(set(refusal_reasons)),
                approval_phrase=approval_phrase,
            ),
            2,
        )

    project_root_path = Path(plan["project_root"])
    store_root = project_root_path / POLICY_STORE_ROOT
    approved_root = store_root / "approved"
    decisions_root = store_root / DECISIONS_DIR_NAME
    proposals_root = store_root / PROPOSALS_DIR_NAME
    policy_path_ref = plan["write_set"][0]["path"]
    decision_ref = plan["write_set"][1]["path"]
    manifest_ref = plan["write_set"][2]["path"]
    proposal_ref = plan["proposal_ref"]
    policy_path = project_root_path / policy_path_ref
    decision_path = project_root_path / decision_ref
    manifest_path = project_root_path / manifest_ref
    proposal_path = project_root_path / proposal_ref
    temp_policy_path = policy_path.with_suffix(policy_path.suffix + ".tmp")
    temp_decision_path = decision_path.with_suffix(decision_path.suffix + ".tmp")
    temp_manifest_path = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    temp_proposal_path = proposal_path.with_suffix(proposal_path.suffix + ".tmp")
    created_paths: list[str] = []
    written_paths: list[str] = []
    proposal_created = False
    policy_created = False
    decision_created = False
    manifest_updated = False

    try:
        if policy_path.exists():
            return (
                build_policy_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["target_path_already_exists_at_write_time"],
                    approval_phrase=approval_phrase,
                ),
                2,
            )
        if decision_path.exists():
            return (
                build_policy_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["decision_record_already_exists_at_write_time"],
                    approval_phrase=approval_phrase,
                ),
                2,
            )
        if proposal_path.exists():
            return (
                build_policy_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["proposal_snapshot_already_exists_at_write_time"],
                    approval_phrase=approval_phrase,
                ),
                2,
            )
        if manifest_path.exists() and plan["policy_store_status"] not in {"initialized", "active"}:
            return (
                build_policy_write_refusal_result(
                    plan=plan,
                    refusal_reasons=["manifest_already_exists_at_write_time"],
                    approval_phrase=approval_phrase,
                ),
                2,
            )

        if not store_root.exists():
            store_root.mkdir()
            created_paths.append(POLICY_STORE_ROOT + "/")
        if not approved_root.exists():
            approved_root.mkdir()
            created_paths.append(f"{POLICY_STORE_ROOT}/approved/")
        if not decisions_root.exists():
            decisions_root.mkdir()
            created_paths.append(f"{POLICY_STORE_ROOT}/{DECISIONS_DIR_NAME}/")
        if not proposals_root.exists():
            proposals_root.mkdir()
            created_paths.append(f"{POLICY_STORE_ROOT}/{PROPOSALS_DIR_NAME}/")

        proposed_policy = dict(plan["proposed_policy"])
        if manifest_path.exists():
            manifest_text = append_active_policy_ref_to_manifest_text(
                text=manifest_path.read_text(encoding="utf-8"),
                policy_id=plan["policy_ref"],
                policy_path_ref=policy_path_ref,
            )
            manifest_text = append_proposal_ref_to_manifest_text(
                text=manifest_text,
                policy_id=plan["policy_ref"],
                proposal_ref=proposal_ref,
            )
        else:
            manifest = build_policy_manifest_record(
                project_root=project_root_path,
                policy_id=plan["policy_ref"],
                policy_path_ref=policy_path_ref,
                proposal_ref=proposal_ref,
            )
            manifest_text = render_yaml_document(manifest)
        proposal_snapshot = dict(plan)
        temp_policy_path.write_text(
            render_yaml_document(proposed_policy),
            encoding="utf-8",
            newline="\n",
        )
        temp_proposal_path.write_text(
            render_yaml_document(proposal_snapshot),
            encoding="utf-8",
            newline="\n",
        )
        decision_record = build_policy_decision_record(
            plan=plan,
            decision_path_ref=decision_ref,
            approval_phrase=approval_phrase,
        )
        temp_decision_path.write_text(
            render_yaml_document(decision_record),
            encoding="utf-8",
            newline="\n",
        )
        temp_manifest_path.write_text(
            manifest_text,
            encoding="utf-8",
            newline="\n",
        )
        try:
            fd = os.open(proposal_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise RuntimeError("policy proposal snapshot already exists") from None
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(temp_proposal_path.read_text(encoding="utf-8"))
        proposal_created = True
        temp_proposal_path.unlink(missing_ok=True)
        written_paths.append(proposal_ref)

        try:
            fd = os.open(policy_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise RuntimeError("policy file already exists") from None
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(temp_policy_path.read_text(encoding="utf-8"))
        policy_created = True
        temp_policy_path.unlink(missing_ok=True)
        written_paths.append(policy_path_ref)

        try:
            fd = os.open(decision_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise RuntimeError("policy decision record already exists") from None
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(temp_decision_path.read_text(encoding="utf-8"))
        decision_created = True
        temp_decision_path.unlink(missing_ok=True)
        written_paths.append(decision_ref)

        if manifest_path.exists():
            os.replace(temp_manifest_path, manifest_path)
        else:
            try:
                fd = os.open(manifest_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                raise RuntimeError("manifest.yaml already exists") from None
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(temp_manifest_path.read_text(encoding="utf-8"))
        manifest_updated = True
        temp_manifest_path.unlink(missing_ok=True)
        written_paths.append(manifest_ref)
    except Exception as exc:
        for temp_path in (
            temp_policy_path,
            temp_decision_path,
            temp_manifest_path,
            temp_proposal_path,
        ):
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
        if proposal_created and not manifest_updated and proposal_path.exists():
            proposal_path.unlink(missing_ok=True)
        if policy_created and not manifest_updated and policy_path.exists():
            policy_path.unlink(missing_ok=True)
        if decision_created and not manifest_updated and decision_path.exists():
            decision_path.unlink(missing_ok=True)
        return (
            build_policy_write_refusal_result(
                plan=plan,
                refusal_reasons=["policy_store_write_failed"],
                approval_phrase=approval_phrase,
                error=str(exc),
            ),
            2,
        )

    status_after = inspect_policy_store(project_root=project_root_path)
    policy_found = any(
        ref.get("policy_id") == plan["policy_ref"]
        for ref in status_after["active_policy_refs"]
    )
    return (
        {
            "schema": POLICY_WRITE_RESULT_SCHEMA,
            "schema_version": POLICY_WRITE_RESULT_SCHEMA,
            "status": "written" if policy_found else "failed",
            "write_performed": True,
            "operation": plan["operation"],
            "plan_ref": plan["plan_id"],
            "policy_ref": plan["policy_ref"],
            "project_root": plan["project_root"],
            "policy_store_status_before": plan["policy_store_status"],
            "policy_store_status_after": status_after["policy_store_status"],
            "written_paths": written_paths,
            "created_paths": created_paths,
            "proposal_ref": proposal_ref,
            "decision_record_ref": decision_ref,
            "refusal_reasons": [],
            "warnings": plan["warnings"] + status_after["warnings"],
            "approval_record": {
                "phrase": approval_phrase,
                "decision_target": "JIKUO approved policy-store write",
                "decision_effect": "create or append approved policy file and policy manifest ref",
                "decision_noneffect": "does not execute policy actions or promote gates",
                "source_plan_schema": POLICY_WRITE_PLAN_SCHEMA,
                "source_plan_ref": plan["plan_id"],
            },
            "error": None if policy_found else "post-write active policy verification failed",
            "post_write_verification": {
                "reread_ok": status_after["policy_store_status"] == "active",
                "proposal_snapshot_written": proposal_path.is_file(),
                "decision_record_written": decision_path.is_file(),
                "manifest_updated": manifest_ref in {
                    status_after.get("manifest_ref"),
                    manifest_ref,
                },
                "active_policy_resolvable": policy_found,
            },
            "next_actions": policy_store_write_next_actions(
                "written" if policy_found else "refused"
            ),
        },
        0 if policy_found else 2,
    )


def policy_file_path_from_ref(
    *,
    project_root: Path,
    store_root: Path,
    policy_ref: dict[str, Any],
) -> tuple[Path | None, str | None]:
    raw_path = policy_ref.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        return None, f"active policy ref has no path: {policy_ref.get('policy_id')}"
    policy_path, path_error = resolve_project_path(project_root, raw_path)
    if path_error:
        return None, path_error
    assert policy_path is not None
    try:
        policy_path.relative_to(store_root.resolve())
    except ValueError:
        return None, f"active policy ref is outside policy store: {raw_path}"
    return policy_path, None


def trigger_matches_event(trigger: dict[str, Any], event: str) -> bool:
    return (
        trigger.get("type") == "task_lifecycle_event"
        and trigger.get("event") == event
    )


def work_profile_applicability_is_scope_first(
    applicability: dict[str, Any] | None,
) -> bool:
    if not applicability:
        return False
    return bool(applicability.get("policy_scopes")) and not bool(
        applicability.get("lifecycle_events")
    )


def policy_trigger_candidates(
    *,
    triggers: list[Any],
    event: str,
    work_profile_applicability: dict[str, Any] | None,
) -> list[tuple[dict[str, Any], str]]:
    exact: list[tuple[dict[str, Any], str]] = []
    first_task_lifecycle_trigger: dict[str, Any] | None = None
    for trigger in triggers:
        if not isinstance(trigger, dict):
            continue
        if (
            first_task_lifecycle_trigger is None
            and trigger.get("type") == "task_lifecycle_event"
        ):
            first_task_lifecycle_trigger = trigger
        if trigger_matches_event(trigger, event):
            exact.append((trigger, "event_exact"))
    if exact:
        return exact
    if (
        first_task_lifecycle_trigger is not None
        and work_profile_applicability_is_scope_first(work_profile_applicability)
    ):
        return [(first_task_lifecycle_trigger, "work_profile_scope")]
    return []


def trigger_reason_for(
    *, trigger: dict[str, Any], event: str, match_mode: str
) -> str:
    if match_mode == "work_profile_scope":
        declared_event = trigger.get("event") or "unspecified"
        return (
            f"work_profile scope matched during {event}; declared trigger event "
            f"{declared_event} is an evaluation-surface anchor"
        )
    return f"task_lifecycle_event matched {event}"


def normalize_path_for_match(value: str) -> str:
    return value.replace("\\", "/")


def condition_expected_value(condition: dict[str, Any]) -> str | None:
    raw = (
        condition.get("value")
        or condition.get("pattern")
        or condition.get("glob")
        or condition.get("path")
    )
    return str(raw) if raw is not None else None


def evaluate_single_condition(
    *,
    policy_ref: str,
    trigger_ref: str | None,
    condition: dict[str, Any],
    index: int,
    task_type: str | None,
    jikuo_layer: str | None,
    changed_paths: list[str],
    added_paths: list[str],
) -> dict[str, Any]:
    condition_type = condition.get("type")
    condition_ref = condition.get("condition_id") or f"{policy_ref}:condition:{index + 1}"
    expected = condition_expected_value(condition)
    observed: Any = None
    matched_refs: list[str] = []
    status = "review_required"
    summary = "Condition type is unsupported by the MVP evaluator."
    match_basis = "unsupported_condition"

    if condition_type == "task_type_is":
        observed = task_type
        match_basis = "task_type_exact"
        if observed is None:
            summary = "Task type was not supplied to the evaluator."
        elif expected is None:
            summary = "Condition has no expected task type."
        elif observed == expected:
            status = "matched"
            summary = f"task_type matched {expected}"
        else:
            status = "not_matched"
            summary = f"task_type {observed} did not match {expected}"
    elif condition_type == "jikuo_layer_is":
        observed = jikuo_layer
        match_basis = "jikuo_layer_exact"
        if observed is None:
            summary = "JIKUO layer was not supplied to the evaluator."
        elif expected is None:
            summary = "Condition has no expected JIKUO layer."
        elif observed == expected:
            status = "matched"
            summary = f"jikuo_layer matched {expected}"
        else:
            status = "not_matched"
            summary = f"jikuo_layer {observed} did not match {expected}"
    elif condition_type in {"changed_path_matches", "added_path_matches"}:
        raw_paths = changed_paths if condition_type == "changed_path_matches" else added_paths
        paths = [normalize_path_for_match(str(path)) for path in raw_paths]
        observed = paths
        match_basis = condition_type
        if expected is None:
            summary = "Condition has no path pattern."
        elif not paths:
            summary = f"No {condition_type.replace('_matches', 's')} were supplied to the evaluator."
        else:
            pattern = normalize_path_for_match(expected)
            matched_refs = [
                path for path in paths if fnmatch.fnmatchcase(path, pattern)
            ]
            if matched_refs:
                status = "matched"
                summary = f"{len(matched_refs)} path(s) matched {pattern}"
            else:
                status = "not_matched"
                summary = f"No supplied path matched {pattern}"

    return {
        "condition_ref": condition_ref,
        "policy_ref": policy_ref,
        "trigger_ref": trigger_ref,
        "condition_type": condition_type,
        "expected": expected,
        "observed": observed,
        "matched_refs": matched_refs,
        "status": status,
        "summary": summary,
        "match_basis": match_basis,
    }


def evaluate_policy_conditions(
    *,
    policy_ref: str,
    trigger_ref: str | None,
    conditions: list[Any],
    task_type: str | None,
    jikuo_layer: str | None,
    changed_paths: list[str],
    added_paths: list[str],
) -> tuple[bool, list[dict[str, Any]]]:
    reports: list[dict[str, Any]] = []
    for index, condition in enumerate(conditions):
        if not isinstance(condition, dict):
            reports.append(
                {
                    "condition_ref": f"{policy_ref}:condition:{index + 1}",
                    "policy_ref": policy_ref,
                    "trigger_ref": trigger_ref,
                    "condition_type": None,
                    "expected": None,
                    "observed": None,
                    "matched_refs": [],
                    "status": "review_required",
                    "summary": "Condition entry is not an object.",
                    "match_basis": "invalid_condition_shape",
                }
            )
            continue
        reports.append(
            evaluate_single_condition(
                policy_ref=policy_ref,
                trigger_ref=trigger_ref,
                condition=condition,
                index=index,
                task_type=task_type,
                jikuo_layer=jikuo_layer,
                changed_paths=changed_paths,
                added_paths=added_paths,
            )
        )
    return all(item["status"] == "matched" for item in reports), reports


def ensure_work_profile_for_evaluation(
    *,
    event: str,
    supplied_work_profile: dict[str, Any] | None,
    task_type: str | None,
    jikuo_layer: str | None,
    changed_paths: list[str],
    added_paths: list[str],
) -> tuple[dict[str, Any], str]:
    if isinstance(supplied_work_profile, dict):
        return supplied_work_profile, "supplied"
    return (
        work_profile_module.build_work_profile(
            raw_event=event,
            normalized_event=event,
            task_type=task_type,
            jikuo_layer=jikuo_layer,
            changed_paths=changed_paths,
            added_paths=added_paths,
        ),
        "inferred_from_evaluator_context",
    )


def evaluate_work_profile_applicability(
    *,
    policy_ref: str,
    trigger_ref: str | None,
    applicability: dict[str, Any],
    work_profile_projection: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    expected_lifecycle_events = scalar_list(applicability.get("lifecycle_events"))
    expected_policy_scopes = scalar_list(applicability.get("policy_scopes"))
    observed_lifecycle_event = str(
        work_profile_projection.get("lifecycle_event") or ""
    )
    observed_policy_scopes = [
        str(scope)
        for scope in scalar_list(work_profile_projection.get("policy_scopes"))
    ]
    observed_scope_set = set(observed_policy_scopes)
    matched_scopes = [
        scope for scope in expected_policy_scopes if scope in observed_scope_set
    ]
    lifecycle_matched = (
        not expected_lifecycle_events
        or observed_lifecycle_event in expected_lifecycle_events
    )
    scopes_matched = bool(matched_scopes) if expected_policy_scopes else True
    sufficient_declaration = bool(expected_lifecycle_events or expected_policy_scopes)
    fallback_expanded = bool(work_profile_projection.get("fallback_expanded", False))

    status = "matched"
    summary = "work_profile applicability matched"
    if not sufficient_declaration:
        status = "review_required"
        summary = (
            "Policy declares applies_to_work_profile but has no lifecycle_events "
            "or policy_scopes for POLTRIG-03 consumption."
        )
    elif not lifecycle_matched:
        status = "not_matched"
        summary = (
            f"work_profile lifecycle_event {observed_lifecycle_event or 'missing'} "
            f"did not match {expected_lifecycle_events}"
        )
    elif not scopes_matched:
        status = "not_matched"
        summary = (
            f"work_profile policy_scopes {observed_policy_scopes} did not overlap "
            f"{expected_policy_scopes}"
        )
    elif matched_scopes:
        summary = f"work_profile policy_scope matched {', '.join(matched_scopes)}"
        if fallback_expanded:
            summary += " via conservative fallback expansion"

    matched_refs: list[str] = []
    if lifecycle_matched and expected_lifecycle_events:
        matched_refs.append(f"lifecycle_event:{observed_lifecycle_event}")
    matched_refs.extend(f"policy_scope:{scope}" for scope in matched_scopes)

    return (
        status == "matched",
        {
            "condition_ref": f"{policy_ref}:work_profile_applicability",
            "policy_ref": policy_ref,
            "trigger_ref": trigger_ref,
            "condition_type": "work_profile_applicability",
            "expected": {
                "lifecycle_events": expected_lifecycle_events,
                "policy_scopes": expected_policy_scopes,
            },
            "observed": {
                "lifecycle_event": observed_lifecycle_event,
                "policy_scopes": observed_policy_scopes,
                "intent_class": work_profile_projection.get("intent_class"),
                "operation_class": work_profile_projection.get("operation_class"),
                "output_class": work_profile_projection.get("output_class"),
                "fallback_expanded": fallback_expanded,
            },
            "matched_refs": matched_refs,
            "status": status,
            "summary": summary,
            "match_basis": "work_profile_lifecycle_and_scope_overlap",
            "evaluator_effect": "consumed_by_POLTRIG_03_scope_filter",
        },
    )


def project_required_actions(
    *,
    policy_ref: str,
    trigger_ref: str | None,
    actions: list[Any],
    event: str,
) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            continue
        action_type = action.get("type")
        action_ref = action.get("action_id") or f"{policy_ref}:action:{index + 1}"
        projected.append(
            {
                "action_ref": action_ref,
                "policy_ref": policy_ref,
                "trigger_ref": trigger_ref,
                "action_type": action_type,
                "phase": action.get("phase") or event,
                "target": {
                    "kind": action.get("target_kind") or "unspecified",
                    "ref": action.get("target_ref"),
                },
                "status": "not_started",
                "write_boundary": {
                    "write_effect": action.get("write_effect") or "none",
                    "approval_required": bool(action.get("approval_required", False)),
                },
                "next_action": action_type,
            }
        )
    return projected


def project_evidence_requirements(
    *,
    policy_ref: str,
    trigger_ref: str | None,
    requirements: list[Any],
    actions_by_ref: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            continue
        action_ref = requirement.get("satisfies_action") or requirement.get("action_ref")
        action = actions_by_ref.get(str(action_ref)) if action_ref is not None else None
        requirement_ref = requirement.get("evidence_id") or requirement.get("requirement_id")
        if not requirement_ref:
            requirement_ref = f"{policy_ref}:evidence:{index + 1}"
        projected.append(
            {
                "requirement_ref": requirement_ref,
                "policy_ref": policy_ref,
                "trigger_ref": trigger_ref,
                "action_ref": action_ref,
                "action_type": action.get("action_type") if action else None,
                "required_type": requirement.get("type") or requirement.get("required_type"),
                "required_status": requirement.get("required_status") or ["ok"],
            }
        )
    return projected


def evidence_matches_requirement(
    evidence: dict[str, Any],
    requirement: dict[str, Any],
) -> bool:
    if evidence.get("evidence_type") != requirement.get("required_type"):
        return False

    evidence_policy = evidence.get("policy_ref")
    if evidence_policy and evidence_policy != requirement.get("policy_ref"):
        return False

    evidence_action = evidence.get("action_ref")
    if evidence_action and evidence_action == requirement.get("action_ref"):
        return True

    evidence_action_type = evidence.get("action_type")
    return bool(
        evidence_action_type
        and evidence_action_type == requirement.get("action_type")
    )


def allowed_evidence_statuses(requirement: dict[str, Any]) -> set[str]:
    raw_statuses = requirement.get("required_status")
    if isinstance(raw_statuses, list):
        return {str(status) for status in raw_statuses}
    if isinstance(raw_statuses, str):
        return {raw_statuses}
    return {"ok"}


def next_action_for_required_evidence(required_type: Any) -> str:
    if required_type == "card_rendered":
        return "render_required_card"
    if required_type == "checker_result":
        return "run_report_only_checker"
    if required_type == "test_result":
        return "run_declared_test"
    return "record_evidence_snapshot"


def parse_semicolon_ref(value: str | None) -> dict[str, str]:
    parsed: dict[str, str] = {}
    if not value:
        return parsed
    for part in value.split(";"):
        if "=" not in part:
            continue
        key, raw = part.split("=", 1)
        key = key.strip()
        raw = raw.strip()
        if key:
            parsed[key] = raw
    return parsed


def persisted_evidence_from_session(
    *,
    project_root: Path,
    task_session_id: str | None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    if not task_session_id:
        return [], [], []
    if any(part in task_session_id for part in ("/", "\\", "..")):
        return [], [f"task session id is not safe: {task_session_id}"], []

    session_path = project_root / ".jikuo" / "task_sessions" / f"{task_session_id}.yaml"
    try:
        session_path.resolve().relative_to((project_root / ".jikuo" / "task_sessions").resolve())
    except ValueError:
        return [], [f"task session path escapes task_sessions root: {task_session_id}"], []
    if not session_path.exists() or not session_path.is_file():
        return [], [f"task session evidence source is missing: {task_session_id}"], []

    try:
        record = read_minimal_yaml(session_path)
    except OSError as exc:
        return [], [f"task session evidence source cannot be read: {exc}"], []

    snapshots = record.get("evidence_snapshots", [])
    if snapshots is None:
        snapshots = []
    if not isinstance(snapshots, list):
        return [], [f"task session evidence_snapshots must be a list: {task_session_id}"], []

    evidence: list[dict[str, Any]] = []
    source_refs = [display_path(session_path, project_root)]
    for item in snapshots:
        if not isinstance(item, dict):
            continue
        evidence_kind = item.get("evidence_kind")
        if not isinstance(evidence_kind, str):
            continue
        if not evidence_kind.startswith("policy_evidence:"):
            continue
        parsed_ref = parse_semicolon_ref(str(item.get("source_ref") or ""))
        evidence_type = evidence_kind.split(":", 1)[1]
        evidence.append(
            {
                "evidence_id": item.get("evidence_id"),
                "evidence_type": evidence_type,
                "policy_ref": parsed_ref.get("policy_ref"),
                "action_ref": parsed_ref.get("action_ref"),
                "requirement_ref": parsed_ref.get("requirement_ref"),
                "source": {
                    "kind": "task_session_evidence_snapshot",
                    "ref": source_refs[0],
                },
                "producer": {
                    "actor": item.get("recorded_by"),
                    "tool": "python -B -m jikuo.task_session",
                },
                "status": item.get("status") or "ok",
                "summary": item.get("summary"),
                "task_session_ref": task_session_id,
            }
        )
    return evidence, [], source_refs


def evaluate_required_evidence(
    *,
    event: str,
    evidence_requirements: list[dict[str, Any]],
    produced_evidence: list[dict[str, Any]] | None,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    if not evidence_requirements:
        return POLICY_EVIDENCE_CHECK_STATUS_CHECKED, [], []

    produced = [
        item for item in (produced_evidence or []) if isinstance(item, dict)
    ]
    evidence_status: list[dict[str, Any]] = []
    missing_reports: list[dict[str, Any]] = []

    for requirement in evidence_requirements:
        matches = [
            item for item in produced if evidence_matches_requirement(item, requirement)
        ]
        allowed_statuses = allowed_evidence_statuses(requirement)
        satisfying = [
            item for item in matches if str(item.get("status") or "") in allowed_statuses
        ]
        if satisfying:
            refs = [
                str(item.get("evidence_id") or item.get("source_ref") or "inline_evidence")
                for item in satisfying
            ]
            status_item = {
                "requirement_ref": requirement["requirement_ref"],
                "action_ref": requirement.get("action_ref"),
                "policy_ref": requirement["policy_ref"],
                "trigger_ref": requirement.get("trigger_ref"),
                "required_type": requirement.get("required_type"),
                "current_status": str(satisfying[0].get("status") or "ok"),
                "evidence_refs": refs,
                "summary": satisfying[0].get("summary")
                or "Matching policy evidence was supplied by the runner.",
                "match_basis": "evidence_type_and_action",
            }
            evidence_status.append(status_item)
            continue

        reason = (
            "Matching evidence exists but does not have an allowed status."
            if matches
            else f"No matching {requirement.get('required_type')} evidence found for this action."
        )
        status_item = {
            "requirement_ref": requirement["requirement_ref"],
            "action_ref": requirement.get("action_ref"),
            "policy_ref": requirement["policy_ref"],
            "trigger_ref": requirement.get("trigger_ref"),
            "required_type": requirement.get("required_type"),
            "current_status": "missing",
            "evidence_refs": [],
            "summary": reason,
            "match_basis": "evidence_type_and_action",
        }
        evidence_status.append(status_item)
        missing_reports.append(
            {
                "schema_version": POLICY_MISSING_EVIDENCE_REPORT_SCHEMA,
                "report_id": (
                    "MER-"
                    + str(requirement["policy_ref"]).replace(" ", "_")
                    + "-"
                    + str(requirement["requirement_ref"]).replace(" ", "_")
                ),
                "policy_ref": requirement["policy_ref"],
                "trigger_ref": requirement.get("trigger_ref"),
                "task_session_ref": None,
                "missing": [
                    {
                        "requirement_ref": requirement["requirement_ref"],
                        "action_ref": requirement.get("action_ref"),
                        "required_type": requirement.get("required_type"),
                        "current_status": "missing",
                        "reason": reason,
                    }
                ],
                "severity": {
                    "policy_level": "review_required",
                    "enforcement_phase": "report_only",
                },
                "next_actions": [
                    next_action_for_required_evidence(requirement.get("required_type"))
                ],
                "projection": {
                    "desktop_card": True,
                    "checker": True,
                    "frontend": True,
                },
                "event": event,
            }
        )

    return (
        POLICY_EVIDENCE_CHECK_STATUS_CHECKED,
        evidence_status,
        missing_reports,
    )


def evaluate_policy_triggers(
    *,
    event: str,
    project_root: Path | None = None,
    cwd: Path | None = None,
    produced_evidence: list[dict[str, Any]] | None = None,
    task_session_id: str | None = None,
    task_type: str | None = None,
    jikuo_layer: str | None = None,
    changed_paths: list[str] | None = None,
    added_paths: list[str] | None = None,
    work_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status_report = inspect_policy_store(project_root=project_root, cwd=cwd)
    resolved_root = Path(status_report["project_root"])
    store_root = Path(status_report["policy_store_root"])
    warnings = list(status_report["warnings"])
    persisted_evidence, persisted_warnings, persisted_source_refs = (
        persisted_evidence_from_session(
            project_root=resolved_root,
            task_session_id=task_session_id,
        )
    )
    warnings.extend(persisted_warnings)
    all_produced_evidence = [*(produced_evidence or []), *persisted_evidence]
    triggered_policies: list[dict[str, Any]] = []
    required_actions: list[dict[str, Any]] = []
    evidence_requirements: list[dict[str, Any]] = []
    condition_reports: list[dict[str, Any]] = []
    changed_path_list = [str(path) for path in (changed_paths or [])]
    added_path_list = [str(path) for path in (added_paths or [])]
    effective_work_profile, work_profile_source = ensure_work_profile_for_evaluation(
        event=event,
        supplied_work_profile=work_profile,
        task_type=task_type,
        jikuo_layer=jikuo_layer,
        changed_paths=changed_path_list,
        added_paths=added_path_list,
    )

    if status_report["policy_store_status"] != "active":
        eval_status = (
            POLICY_EVAL_STATUS_REFUSED
            if status_report["policy_store_status"] == "conflict"
            else POLICY_EVAL_STATUS_NOT_EVALUATED
        )
        return {
            "schema": POLICY_TRIGGER_EVAL_REPORT_SCHEMA,
            "report_only": True,
            "project_root": status_report["project_root"],
            "event": event,
            "policy_store_status": status_report["policy_store_status"],
            "policy_eval_status": eval_status,
            "active_policy_refs": status_report["active_policy_refs"],
            "policy_snapshot_ref": status_report["manifest_ref"],
            "triggered_policies": [],
            "required_actions": [],
            "policy_condition_eval_status": POLICY_CONDITION_EVAL_STATUS_NOT_EVALUATED,
            "condition_reports": [],
            "policy_evidence_check_status": (
                POLICY_EVIDENCE_CHECK_STATUS_REFUSED
                if eval_status == POLICY_EVAL_STATUS_REFUSED
                else POLICY_EVIDENCE_CHECK_STATUS_NOT_EVALUATED
            ),
            "evidence_status": [],
            "missing_evidence_reports": [],
            "task_session_id": task_session_id,
            "evidence_source_refs": persisted_source_refs,
            "work_profile": effective_work_profile,
            "work_profile_source": work_profile_source,
            "write_allowed_by_command": False,
            "warnings": warnings,
            "source_refs": CONTRACT_REFS,
            "status_reason": eval_status_reason_for(
                store_status=status_report["policy_store_status"],
                eval_status=eval_status,
                triggered_count=0,
            ),
            "evidence_status_reason": evidence_check_status_reason_for(
                check_status=(
                    POLICY_EVIDENCE_CHECK_STATUS_REFUSED
                    if eval_status == POLICY_EVAL_STATUS_REFUSED
                    else POLICY_EVIDENCE_CHECK_STATUS_NOT_EVALUATED
                ),
                evidence_count=0,
                missing_count=0,
            ),
            "next_actions": eval_next_actions_for(
                status_report["policy_store_status"],
                eval_status,
            ),
        }

    for policy_ref in status_report["active_policy_refs"]:
        policy_path, path_error = policy_file_path_from_ref(
            project_root=resolved_root,
            store_root=store_root,
            policy_ref=policy_ref,
        )
        if path_error:
            warnings.append(path_error)
            continue
        assert policy_path is not None
        record, record_warnings = read_policy_record(policy_path)
        warnings.extend(record_warnings)
        if record is None:
            continue

        triggers = record.get("triggers", [])
        if not isinstance(triggers, list):
            warnings.append(f"policy triggers must be a list: {policy_ref.get('policy_id')}")
            continue

        policy_id = str(record.get("policy_id") or policy_ref.get("policy_id"))
        work_profile_applicability = normalize_work_profile_applicability(
            record.get("applies_to_work_profile")
        )
        trigger_candidates = policy_trigger_candidates(
            triggers=triggers,
            event=event,
            work_profile_applicability=work_profile_applicability,
        )

        for trigger, trigger_match_mode in trigger_candidates:
            trigger_ref = trigger.get("trigger_id")
            trigger_ref_text = trigger_ref if isinstance(trigger_ref, str) else None
            work_profile_match_report: dict[str, Any] | None = None
            if work_profile_applicability:
                (
                    work_profile_matched,
                    work_profile_match_report,
                ) = evaluate_work_profile_applicability(
                    policy_ref=policy_id,
                    trigger_ref=trigger_ref_text,
                    applicability=work_profile_applicability,
                    work_profile_projection=effective_work_profile,
                )
                condition_reports.append(work_profile_match_report)
                if not work_profile_matched:
                    continue
            raw_conditions = record.get("conditions", [])
            if raw_conditions is None:
                raw_conditions = []
            if not isinstance(raw_conditions, list):
                warnings.append(f"policy conditions must be a list: {policy_id}")
                condition_reports.append(
                    {
                        "condition_ref": f"{policy_id}:conditions",
                        "policy_ref": policy_id,
                        "trigger_ref": trigger_ref,
                        "condition_type": None,
                        "expected": None,
                        "observed": None,
                        "matched_refs": [],
                        "status": "review_required",
                        "summary": "Policy conditions must be a list.",
                        "match_basis": "invalid_conditions_shape",
                    }
                )
                continue
            conditions_matched, reports = evaluate_policy_conditions(
                policy_ref=policy_id,
                trigger_ref=trigger_ref_text,
                conditions=raw_conditions,
                task_type=task_type,
                jikuo_layer=jikuo_layer,
                changed_paths=changed_path_list,
                added_paths=added_path_list,
            )
            condition_reports.extend(reports)
            if not conditions_matched:
                continue
            triggered_policy = {
                "policy_ref": policy_id,
                "policy_title": record.get("title"),
                "version": record.get("version") or policy_ref.get("version"),
                "source": "project_approved_policy",
                "trigger_ref": trigger_ref,
                "trigger_reason": trigger_reason_for(
                    trigger=trigger,
                    event=event,
                    match_mode=trigger_match_mode,
                ),
                "trigger_match_mode": trigger_match_mode,
                "declared_trigger_event": trigger.get("event"),
                "evaluation_event": event,
                "condition_status": "matched",
                "status": "triggered",
                "confidence": "tool_verified",
            }
            if work_profile_applicability:
                triggered_policy["applies_to_work_profile"] = work_profile_applicability
                triggered_policy["work_profile_match"] = work_profile_match_report
            triggered_policies.append(triggered_policy)
            actions = record.get("required_actions", [])
            projected_actions: list[dict[str, Any]] = []
            if isinstance(actions, list):
                projected_actions = project_required_actions(
                    policy_ref=policy_id,
                    trigger_ref=trigger_ref_text,
                    actions=actions,
                    event=event,
                )
                required_actions.extend(projected_actions)
            else:
                warnings.append(f"policy required_actions must be a list: {policy_id}")

            raw_requirements = record.get("required_evidence", [])
            if isinstance(raw_requirements, list):
                evidence_requirements.extend(
                    project_evidence_requirements(
                        policy_ref=policy_id,
                        trigger_ref=trigger_ref_text,
                        requirements=raw_requirements,
                        actions_by_ref={
                            str(action["action_ref"]): action
                            for action in projected_actions
                            if action.get("action_ref") is not None
                        },
                    )
                )
            else:
                warnings.append(f"policy required_evidence must be a list: {policy_id}")

    eval_status = POLICY_EVAL_STATUS_EVALUATED
    evidence_check_status, evidence_status, missing_evidence_reports = (
        evaluate_required_evidence(
            event=event,
            evidence_requirements=evidence_requirements,
            produced_evidence=all_produced_evidence,
        )
    )
    return {
        "schema": POLICY_TRIGGER_EVAL_REPORT_SCHEMA,
        "report_only": True,
        "project_root": status_report["project_root"],
        "event": event,
        "policy_store_status": status_report["policy_store_status"],
        "policy_eval_status": eval_status,
        "active_policy_refs": status_report["active_policy_refs"],
        "policy_snapshot_ref": status_report["manifest_ref"],
        "triggered_policies": triggered_policies,
        "required_actions": required_actions,
        "policy_condition_eval_status": (
            POLICY_CONDITION_EVAL_STATUS_CHECKED
            if condition_reports
            else POLICY_CONDITION_EVAL_STATUS_NOT_EVALUATED
        ),
        "condition_reports": condition_reports,
        "policy_evidence_check_status": evidence_check_status,
        "evidence_status": evidence_status,
        "missing_evidence_reports": missing_evidence_reports,
        "task_session_id": task_session_id,
        "evidence_source_refs": persisted_source_refs,
        "work_profile": effective_work_profile,
        "work_profile_source": work_profile_source,
        "write_allowed_by_command": False,
        "warnings": warnings,
        "source_refs": CONTRACT_REFS,
        "status_reason": eval_status_reason_for(
            store_status=status_report["policy_store_status"],
            eval_status=eval_status,
            triggered_count=len(triggered_policies),
        ),
        "next_actions": eval_next_actions_for(
            status_report["policy_store_status"],
            eval_status,
        ),
        "evidence_status_reason": evidence_check_status_reason_for(
            check_status=evidence_check_status,
            evidence_count=len(evidence_status),
            missing_count=len(missing_evidence_reports),
        ),
    }


def format_text(report: dict[str, Any]) -> str:
    if report["schema"] == POLICY_WRITE_RESULT_SCHEMA:
        lines = [
            "JIKUO Policy Store Write Result",
            f"Project root: {report['project_root']}",
            f"Status: {report['status']}",
            f"Plan ref: {report['plan_ref']}",
            f"Policy ref: {report['policy_ref']}",
            f"Policy store status before: {report['policy_store_status_before']}",
            f"Policy store status after: {report['policy_store_status_after']}",
            f"Writes performed: {str(report['write_performed']).lower()}",
        ]
        if report["written_paths"]:
            lines.append("Written paths:")
            lines.extend(f"- {item}" for item in report["written_paths"])
        if report["created_paths"]:
            lines.append("Created paths:")
            lines.extend(f"- {item}" for item in report["created_paths"])
        if report["refusal_reasons"]:
            lines.append("Refusal reasons:")
            lines.extend(f"- {item}" for item in report["refusal_reasons"])
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        verification = report["post_write_verification"]
        lines.append("Post-write verification:")
        for key, value in verification.items():
            lines.append(f"- {key}: {str(value).lower()}")
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    if report["schema"] == POLICY_EVOLUTION_PLAN_SCHEMA:
        lines = [
            "JIKUO Policy Evolution Plan (proposal-only)",
            f"Project root: {report['project_root']}",
            f"Status: {report['status']}",
            f"Plan id: {report['plan_id']}",
            f"Operation: {report['operation']}",
            f"Target policy ref: {report['target_policy_ref']}",
            f"Policy store status: {report['policy_store_status']}",
            "Writes performed: no",
            "Write allowed by command: no",
            f"Reason: {report['status_reason']}",
        ]
        target = report["target_policy_snapshot"]
        lines.append("Target policy snapshot:")
        for key, value in target.items():
            lines.append(f"- {key}: {value}")
        feedback = report["feedback"]
        lines.append("Feedback:")
        for key, value in feedback.items():
            lines.append(f"- {key}: {value}")
        lines.append("Recommended changes:")
        lines.extend(f"- {item}" for item in report["recommended_changes"])
        lines.append("Future write boundary:")
        for key, value in report["future_write_boundary"].items():
            lines.append(f"- {key}: {str(value).lower()}")
        lines.append("Non-effects:")
        lines.extend(f"- {item}" for item in report["non_effects"])
        if report["refusal_reasons"]:
            lines.append("Refusal reasons:")
            lines.extend(f"- {item}" for item in report["refusal_reasons"])
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    if report["schema"] == POLICY_WRITE_PLAN_SCHEMA:
        lines = [
            "JIKUO Policy Write Plan (proposal-only)",
            f"Project root: {report['project_root']}",
            f"Status: {report['status']}",
            f"Plan id: {report['plan_id']}",
            f"Policy ref: {report['policy_ref']}",
            f"Policy store status: {report['policy_store_status']}",
            "Writes performed: no",
            "Write allowed by command: no",
            f"Approval required: {str(report['approval_required']).lower()}",
            f"Reason: {report['status_reason']}",
        ]
        lines.append("Preflight:")
        for key, value in report["preflight"].items():
            lines.append(f"- {key}: {str(value).lower()}")
        lines.append("Write set:")
        for item in report["write_set"]:
            lines.append(f"- {item['path']}: {item['effect']}")
        lines.append("Non-effects:")
        lines.extend(f"- {item}" for item in report["non_effects"])
        proposed_policy = report["proposed_policy"]
        lines.append("Proposed policy:")
        lines.append(f"- title: {proposed_policy.get('title')}")
        lines.append(
            f"- trigger: {proposed_policy['triggers'][0].get('event')}"
        )
        lines.append(
            f"- action: {proposed_policy['required_actions'][0].get('type')}"
        )
        lines.append(
            f"- evidence: {proposed_policy['required_evidence'][0].get('type')}"
        )
        if proposed_policy.get("conditions"):
            lines.append("Conditions:")
            for item in proposed_policy["conditions"]:
                expected = condition_expected_value(item)
                lines.append(f"- {item.get('type')}: {expected}")
        if report["refusal_reasons"]:
            lines.append("Refusal reasons:")
            lines.extend(f"- {item}" for item in report["refusal_reasons"])
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    if report["schema"] == POLICY_TRIGGER_EVAL_REPORT_SCHEMA:
        lines = [
            "JIKUO Policy Trigger Evaluation (report-only)",
            f"Project root: {report['project_root']}",
            f"Event: {report['event']}",
            f"Policy store status: {report['policy_store_status']}",
            f"Policy eval status: {report['policy_eval_status']}",
            f"Condition eval status: {report.get('policy_condition_eval_status')}",
            f"Evidence check status: {report['policy_evidence_check_status']}",
            f"Task session id: {report.get('task_session_id')}",
            f"Work profile source: {report.get('work_profile_source')}",
            f"Triggered policies: {len(report['triggered_policies'])}",
            f"Required actions: {len(report['required_actions'])}",
            f"Condition reports: {len(report.get('condition_reports', []))}",
            f"Evidence status: {len(report['evidence_status'])}",
            f"Missing evidence reports: {len(report['missing_evidence_reports'])}",
            "Writes performed: no",
            "Write allowed by command: no",
            f"Reason: {report['status_reason']}",
            f"Evidence reason: {report['evidence_status_reason']}",
        ]
        if report["triggered_policies"]:
            lines.append("Triggered policy refs:")
            for ref in report["triggered_policies"]:
                line = f"- {ref.get('policy_ref')} via {ref.get('trigger_ref')}"
                applicability = ref.get("applies_to_work_profile") or {}
                if applicability:
                    line += (
                        " "
                        f"(work_profile_applicability={applicability.get('status')}, "
                        f"evaluator_effect={applicability.get('evaluator_effect')})"
                    )
                match = ref.get("work_profile_match") or {}
                if match:
                    line += f" match={match.get('status')}"
                lines.append(line)
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        if report["evidence_status"]:
            lines.append("Evidence status:")
            for item in report["evidence_status"]:
                lines.append(
                    f"- {item.get('requirement_ref')} for {item.get('action_ref')}: "
                    f"{item.get('current_status')}"
                )
        if report.get("condition_reports"):
            lines.append("Condition reports:")
            for item in report["condition_reports"]:
                lines.append(
                    f"- {item.get('condition_ref')} "
                    f"({item.get('condition_type')}): {item.get('status')}"
                )
        if report.get("evidence_source_refs"):
            lines.append("Evidence source refs:")
            lines.extend(f"- {ref}" for ref in report["evidence_source_refs"])
        if report["missing_evidence_reports"]:
            lines.append("Missing evidence:")
            for item in report["missing_evidence_reports"]:
                lines.append(
                    f"- {item.get('policy_ref')} via {item.get('trigger_ref')}: "
                    f"{len(item.get('missing', []))} missing requirement(s)"
                )
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    lines = [
        "JIKUO Policy Store Status (report-only)",
        f"Project root: {report['project_root']}",
        f"Policy store status: {report['policy_store_status']}",
        f"Policy eval status: {report['policy_eval_status']}",
        f"Policy store root: {display_path(Path(report['policy_store_root']), Path(report['project_root']))}",
        "Writes performed: no",
        "Write allowed by command: no",
        f"Active policies: {len(report['active_policy_refs'])}",
        f"Reason: {report['status_reason']}",
    ]
    if report["active_policy_refs"]:
        lines.append("Active policy refs:")
        for ref in report["active_policy_refs"]:
            line = (
                f"- {ref.get('policy_id')} v{ref.get('version')} "
                f"({ref.get('path')})"
            )
            applicability = ref.get("applies_to_work_profile") or {}
            if applicability:
                line += (
                    " "
                    f"work_profile_applicability={applicability.get('status')} "
                    f"evaluator_effect={applicability.get('evaluator_effect')}"
                )
            lines.append(line)
    if report["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    if report["next_actions"]:
        lines.append("Next actions:")
        lines.extend(f"- {action}" for action in report["next_actions"])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only JIKUO policy-store inspection helper."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status")
    status.add_argument("--project-root", type=Path, default=None)
    status.add_argument("--format", choices=("text", "json"), default="text")

    plan_write = subparsers.add_parser("plan-write")
    plan_write.add_argument("--project-root", type=Path, default=None)
    plan_write.add_argument("--policy-id", default=None)
    plan_write.add_argument("--title", default=None)
    plan_write.add_argument("--source-ref", default=None)
    plan_write.add_argument("--source-type", default="user_natural_language")
    plan_write.add_argument("--trigger-event", default="task_start")
    plan_write.add_argument("--task-type", default=None)
    plan_write.add_argument("--jikuo-layer", default=None)
    plan_write.add_argument("--changed-path-pattern", default=None)
    plan_write.add_argument("--added-path-pattern", default=None)
    plan_write.add_argument(
        "--work-profile-lifecycle-event",
        action="append",
        default=[],
    )
    plan_write.add_argument(
        "--work-profile-policy-scope",
        action="append",
        default=[],
    )
    plan_write.add_argument("--action-type", default="render_pre_task_review")
    plan_write.add_argument("--evidence-type", default="card_rendered")
    plan_write.add_argument("--format", choices=("text", "json"), default="text")

    plan_evolution = subparsers.add_parser("plan-evolution")
    plan_evolution.add_argument("--project-root", type=Path, default=None)
    plan_evolution.add_argument("--policy-id", default=None)
    plan_evolution.add_argument(
        "--operation",
        choices=sorted(POLICY_EVOLUTION_OPERATIONS),
        default="refine_policy",
    )
    plan_evolution.add_argument(
        "--feedback-type",
        choices=sorted(POLICY_FEEDBACK_TYPES),
        default=None,
    )
    plan_evolution.add_argument("--summary", default=None)
    plan_evolution.add_argument("--source-ref", default=None)
    plan_evolution.add_argument("--replacement-policy-id", default=None)
    plan_evolution.add_argument("--replacement-title", default=None)
    plan_evolution.add_argument("--replacement-trigger-event", default="task_start")
    plan_evolution.add_argument(
        "--replacement-work-profile-lifecycle-event",
        action="append",
        default=[],
    )
    plan_evolution.add_argument(
        "--replacement-work-profile-policy-scope",
        action="append",
        default=[],
    )
    plan_evolution.add_argument("--replacement-task-type", default=None)
    plan_evolution.add_argument("--replacement-jikuo-layer", default=None)
    plan_evolution.add_argument("--replacement-changed-path-pattern", default=None)
    plan_evolution.add_argument("--replacement-added-path-pattern", default=None)
    plan_evolution.add_argument("--replacement-action-type", default="render_pre_task_review")
    plan_evolution.add_argument("--replacement-evidence-type", default="card_rendered")
    plan_evolution.add_argument("--format", choices=("text", "json"), default="text")

    write_evolution = subparsers.add_parser("write-evolution")
    write_evolution.add_argument("--project-root", type=Path, default=None)
    write_evolution.add_argument("--policy-id", default=None)
    write_evolution.add_argument(
        "--operation",
        choices=sorted(POLICY_EVOLUTION_OPERATIONS),
        default="deprecate_policy",
    )
    write_evolution.add_argument(
        "--feedback-type",
        choices=sorted(POLICY_FEEDBACK_TYPES),
        default=None,
    )
    write_evolution.add_argument("--summary", default=None)
    write_evolution.add_argument("--source-ref", default=None)
    write_evolution.add_argument("--replacement-policy-id", default=None)
    write_evolution.add_argument("--replacement-title", default=None)
    write_evolution.add_argument("--replacement-trigger-event", default="task_start")
    write_evolution.add_argument(
        "--replacement-work-profile-lifecycle-event",
        action="append",
        default=[],
    )
    write_evolution.add_argument(
        "--replacement-work-profile-policy-scope",
        action="append",
        default=[],
    )
    write_evolution.add_argument("--replacement-task-type", default=None)
    write_evolution.add_argument("--replacement-jikuo-layer", default=None)
    write_evolution.add_argument("--replacement-changed-path-pattern", default=None)
    write_evolution.add_argument("--replacement-added-path-pattern", default=None)
    write_evolution.add_argument("--replacement-action-type", default="render_pre_task_review")
    write_evolution.add_argument("--replacement-evidence-type", default="card_rendered")
    write_evolution.add_argument("--confirm-write-evolution", action="store_true")
    write_evolution.add_argument("--approval-phrase", default=None)
    write_evolution.add_argument("--format", choices=("text", "json"), default="text")

    write_policy = subparsers.add_parser("write-policy")
    write_policy.add_argument("--project-root", type=Path, default=None)
    write_policy.add_argument("--policy-id", default=None)
    write_policy.add_argument("--title", default=None)
    write_policy.add_argument("--source-ref", default=None)
    write_policy.add_argument("--source-type", default="user_natural_language")
    write_policy.add_argument("--trigger-event", default="task_start")
    write_policy.add_argument("--task-type", default=None)
    write_policy.add_argument("--jikuo-layer", default=None)
    write_policy.add_argument("--changed-path-pattern", default=None)
    write_policy.add_argument("--added-path-pattern", default=None)
    write_policy.add_argument(
        "--work-profile-lifecycle-event",
        action="append",
        default=[],
    )
    write_policy.add_argument(
        "--work-profile-policy-scope",
        action="append",
        default=[],
    )
    write_policy.add_argument("--action-type", default="render_pre_task_review")
    write_policy.add_argument("--evidence-type", default="card_rendered")
    write_policy.add_argument("--confirm-write-policy", action="store_true")
    write_policy.add_argument("--approval-phrase", default=None)
    write_policy.add_argument("--format", choices=("text", "json"), default="text")

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--event", required=True)
    evaluate.add_argument("--project-root", type=Path, default=None)
    evaluate.add_argument("--task-session-id", default=None)
    evaluate.add_argument("--task-type", default=None)
    evaluate.add_argument("--jikuo-layer", default=None)
    evaluate.add_argument("--changed-path", action="append", default=[])
    evaluate.add_argument("--added-path", action="append", default=[])
    evaluate.add_argument(
        "--work-profile-json",
        default=None,
        help="JSON object work_profile projection for POLTRIG-03 scope matching.",
    )
    evaluate.add_argument(
        "--produced-evidence-json",
        default=None,
        help="JSON list of inline produced evidence for report-only matching.",
    )
    evaluate.add_argument("--produced-evidence-id", default=None)
    evaluate.add_argument("--produced-evidence-type", default=None)
    evaluate.add_argument("--produced-evidence-action-type", default=None)
    evaluate.add_argument("--produced-evidence-status", default="ok")
    evaluate.add_argument("--produced-evidence-summary", default=None)
    evaluate.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "plan-write":
        report = build_policy_write_plan(
            project_root=args.project_root,
            policy_id=args.policy_id,
            title=args.title,
            source_ref=args.source_ref,
            source_type=args.source_type,
            trigger_event=args.trigger_event,
            task_type=args.task_type,
            jikuo_layer=args.jikuo_layer,
            changed_path_pattern=args.changed_path_pattern,
            added_path_pattern=args.added_path_pattern,
            work_profile_lifecycle_events=args.work_profile_lifecycle_event,
            work_profile_policy_scopes=args.work_profile_policy_scope,
            action_type=args.action_type,
            evidence_type=args.evidence_type,
        )
    elif args.command == "plan-evolution":
        report = build_policy_evolution_plan(
            project_root=args.project_root,
            policy_id=args.policy_id,
            operation=args.operation,
            feedback_type=args.feedback_type,
            summary=args.summary,
            source_ref=args.source_ref,
            replacement_policy_id=args.replacement_policy_id,
            replacement_title=args.replacement_title,
            replacement_trigger_event=args.replacement_trigger_event,
            replacement_work_profile_lifecycle_events=args.replacement_work_profile_lifecycle_event,
            replacement_work_profile_policy_scopes=args.replacement_work_profile_policy_scope,
            replacement_task_type=args.replacement_task_type,
            replacement_jikuo_layer=args.replacement_jikuo_layer,
            replacement_changed_path_pattern=args.replacement_changed_path_pattern,
            replacement_added_path_pattern=args.replacement_added_path_pattern,
            replacement_action_type=args.replacement_action_type,
            replacement_evidence_type=args.replacement_evidence_type,
        )
    elif args.command == "write-evolution":
        report, exit_code = write_policy_evolution_from_plan(
            project_root=args.project_root,
            policy_id=args.policy_id,
            operation=args.operation,
            feedback_type=args.feedback_type,
            summary=args.summary,
            source_ref=args.source_ref,
            replacement_policy_id=args.replacement_policy_id,
            replacement_title=args.replacement_title,
            replacement_trigger_event=args.replacement_trigger_event,
            replacement_work_profile_lifecycle_events=args.replacement_work_profile_lifecycle_event,
            replacement_work_profile_policy_scopes=args.replacement_work_profile_policy_scope,
            replacement_task_type=args.replacement_task_type,
            replacement_jikuo_layer=args.replacement_jikuo_layer,
            replacement_changed_path_pattern=args.replacement_changed_path_pattern,
            replacement_added_path_pattern=args.replacement_added_path_pattern,
            replacement_action_type=args.replacement_action_type,
            replacement_evidence_type=args.replacement_evidence_type,
            confirmed=args.confirm_write_evolution,
            approval_phrase=args.approval_phrase,
        )
    elif args.command == "write-policy":
        report, exit_code = write_policy_from_plan(
            project_root=args.project_root,
            policy_id=args.policy_id,
            title=args.title,
            source_ref=args.source_ref,
            source_type=args.source_type,
            trigger_event=args.trigger_event,
            task_type=args.task_type,
            jikuo_layer=args.jikuo_layer,
            changed_path_pattern=args.changed_path_pattern,
            added_path_pattern=args.added_path_pattern,
            work_profile_lifecycle_events=args.work_profile_lifecycle_event,
            work_profile_policy_scopes=args.work_profile_policy_scope,
            action_type=args.action_type,
            evidence_type=args.evidence_type,
            confirmed=args.confirm_write_policy,
            approval_phrase=args.approval_phrase,
        )
    elif args.command == "evaluate":
        produced_evidence: list[dict[str, Any]] | None = None
        work_profile_projection: dict[str, Any] | None = None
        if args.work_profile_json:
            try:
                decoded_work_profile = json.loads(args.work_profile_json)
            except json.JSONDecodeError as exc:
                parser.error(f"--work-profile-json must be valid JSON: {exc}")
            if not isinstance(decoded_work_profile, dict):
                parser.error("--work-profile-json must decode to an object")
            work_profile_projection = decoded_work_profile
        if args.produced_evidence_json:
            try:
                decoded = json.loads(args.produced_evidence_json)
            except json.JSONDecodeError as exc:
                parser.error(f"--produced-evidence-json must be valid JSON: {exc}")
            if not isinstance(decoded, list):
                parser.error("--produced-evidence-json must decode to a list")
            produced_evidence = decoded
        if (
            args.produced_evidence_id
            or args.produced_evidence_type
            or args.produced_evidence_action_type
        ):
            if not args.produced_evidence_type or not args.produced_evidence_action_type:
                parser.error(
                    "--produced-evidence-type and --produced-evidence-action-type are required together"
                )
            if produced_evidence is None:
                produced_evidence = []
            produced_evidence.append(
                {
                    "evidence_id": args.produced_evidence_id or "inline_evidence",
                    "evidence_type": args.produced_evidence_type,
                    "action_type": args.produced_evidence_action_type,
                    "status": args.produced_evidence_status,
                    "summary": args.produced_evidence_summary
                    or "inline produced evidence supplied by CLI",
                }
            )
        report = evaluate_policy_triggers(
            event=args.event,
            project_root=args.project_root,
            produced_evidence=produced_evidence,
            task_session_id=args.task_session_id,
            task_type=args.task_type,
            jikuo_layer=args.jikuo_layer,
            changed_paths=args.changed_path,
            added_paths=args.added_path,
            work_profile=work_profile_projection,
        )
    else:
        report = inspect_policy_store(project_root=args.project_root)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_text(report))
    if report["schema"] == POLICY_WRITE_RESULT_SCHEMA:
        return exit_code
    if report["schema"] in {POLICY_WRITE_PLAN_SCHEMA, POLICY_EVOLUTION_PLAN_SCHEMA}:
        return 0 if report["status"] != "refused" else 2
    if report["policy_store_status"] == "conflict":
        return 2
    if report.get("policy_eval_status") == POLICY_EVAL_STATUS_REFUSED:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
