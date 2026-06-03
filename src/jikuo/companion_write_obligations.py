"""Project required companion governance writes from observed write evidence.

This module is a pure projector. It does not inspect git, read file contents,
write files, or decide whether a change belongs to the current AI round. The
caller supplies observed/declared write items and project context facts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


COMPANION_WRITE_OBLIGATION_SCHEMA = "jikuo.runtime.companion_write_obligations.v0"

CAPABILITIES_REGISTRY = "docs/registry/capabilities.yaml"
SCENARIO_CHAINS_REGISTRY = "docs/registry/scenario_chains.yaml"
WORK_ORDERS_REGISTRY = "docs/registry/work_orders.yaml"
MOUNT_SETS_REGISTRY = "docs/registry/mount_sets.yaml"
REGISTRY_INDEX = "docs/registry/registry_index.yaml"
INSIGHTS_REGISTRY = "docs/insights/insights_registry.yaml"
PROJECT_CONTEXT = ".jikuo/project_context.yaml"
POLICY_GOVERNANCE_AUTHORITY = "docs/governance/jikuo_policy_governance_authority.md"

KNOWN_PROJECT_PREFIXES = (
    ".jikuo/policies/",
    "docs/",
    "src/",
    "tests/",
)
IGNORED_PREFIXES = (
    ".git/",
    ".jikuo/runtime/",
    ".jikuo/events/",
    "__pycache__/",
)
CODE_PREFIXES = ("src/", "tests/")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_project_path(value: Any) -> str | None:
    text = str(value or "").strip().replace("\\", "/")
    if not text:
        return None
    while text.startswith("./"):
        text = text[2:]
    return text or None


def item_path(item: Any) -> str | None:
    record = item if isinstance(item, dict) else {"path": item}
    return normalize_project_path(
        record.get("path")
        or record.get("path_ref")
        or record.get("ref")
        or record.get("target")
    )


def item_operation(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("operation") or "modify").strip() or "modify"
    return "modify"


def is_known_project_path(path: str) -> bool:
    return path.startswith(KNOWN_PROJECT_PREFIXES)


def is_ignored_path(path: str) -> bool:
    return path.startswith(IGNORED_PREFIXES)


def is_markdown_doc(path: str) -> bool:
    return path.endswith(".md") and path.startswith("docs/")


def active_work_order_paths_from_document_roles(
    document_roles: dict[str, Any] | None,
) -> list[str]:
    roles = document_roles or {}
    preferred_role_order = (
        "mvp_work_receipt_configuration_work_order",
        "studio_global_console_work_order",
    )
    output: list[str] = []
    for role in preferred_role_order:
        record = roles.get(role)
        if isinstance(record, dict):
            path = normalize_project_path(record.get("path"))
            if path:
                return [path]
    return dedupe_paths(output)


def dedupe_paths(paths: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for path in paths:
        normalized = normalize_project_path(path)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(normalized)
    return output


def trigger_for_write(path: str, operation: str) -> dict[str, Any] | None:
    if is_ignored_path(path) or not is_known_project_path(path):
        return None
    if path.startswith(CODE_PREFIXES):
        return {
            "type": "feature_or_code_change",
            "source_ref": path,
            "operation": operation,
            "reason": "Code or test change can affect reusable behavior and user-visible feature atoms.",
        }
    if path.startswith(".jikuo/policies/") or path.startswith("src/jikuo/policy"):
        return {
            "type": "policy_or_evaluator_change",
            "source_ref": path,
            "operation": operation,
            "reason": "Policy or evaluator change needs policy governance and registry consistency evidence.",
        }
    if path.startswith("docs/registry/"):
        return {
            "type": "registry_change",
            "source_ref": path,
            "operation": operation,
            "reason": "Registry shard change needs related registry consistency evidence.",
        }
    if operation in {"added", "renamed"} and is_markdown_doc(path):
        return {
            "type": "new_document",
            "source_ref": path,
            "operation": operation,
            "reason": "New documentation needs registry or mount coverage evidence.",
        }
    if path.startswith("docs/work_orders/"):
        return {
            "type": "work_order_progress",
            "source_ref": path,
            "operation": operation,
            "reason": "Work-order updates need registry projection consistency.",
        }
    return None


def companion_paths_for_trigger(
    trigger: dict[str, Any],
    *,
    active_work_order_paths: list[str],
) -> list[tuple[str, str]]:
    trigger_type = str(trigger.get("type") or "")
    if trigger_type == "feature_or_code_change":
        paths = [
            (
                CAPABILITIES_REGISTRY,
                "Feature/code changes require atom capability registration or an explicit checked-unchanged record.",
            ),
            (
                SCENARIO_CHAINS_REGISTRY,
                "Feature/code changes require user action-chain registration or an explicit checked-unchanged record.",
            ),
            (
                WORK_ORDERS_REGISTRY,
                "Feature/code changes require work-order capability refs and progress projection consistency.",
            ),
        ]
        for work_order_path in active_work_order_paths:
            paths.append(
                (
                    work_order_path,
                    "The active work order should record slice progress and the user-action/atom registration decision.",
                )
            )
        return paths
    if trigger_type == "new_document":
        source = str(trigger.get("source_ref") or "")
        paths = [
            (
                REGISTRY_INDEX,
                "New documentation needs document-registry shard authority or an explicit checked-unchanged record.",
            ),
            (
                MOUNT_SETS_REGISTRY,
                "New documentation needs mount coverage review or an explicit checked-unchanged record.",
            ),
        ]
        if source.startswith("docs/work_orders/"):
            paths.append(
                (
                    WORK_ORDERS_REGISTRY,
                    "New work-order documents must be registered in the work-order registry.",
                )
            )
        if source.startswith("docs/insights/"):
            paths.append(
                (
                    INSIGHTS_REGISTRY,
                    "New insight documents must be registered in the insights registry.",
                )
            )
        return paths
    if trigger_type == "work_order_progress":
        return [
            (
                WORK_ORDERS_REGISTRY,
                "Work-order progress changes require the work-order registry projection to stay aligned.",
            )
        ]
    if trigger_type == "policy_or_evaluator_change":
        return [
            (
                POLICY_GOVERNANCE_AUTHORITY,
                "Policy/evaluator changes require governance authority review or an explicit checked-unchanged record.",
            ),
            (
                CAPABILITIES_REGISTRY,
                "Policy/evaluator changes require capability metadata review.",
            ),
            (
                WORK_ORDERS_REGISTRY,
                "Policy/evaluator changes require work-order registry projection review.",
            ),
        ]
    if trigger_type == "registry_change":
        source = str(trigger.get("source_ref") or "")
        paths = []
        if source != CAPABILITIES_REGISTRY:
            paths.append(
                (
                    CAPABILITIES_REGISTRY,
                    "Registry changes may require atom capability metadata consistency.",
                )
            )
        if source != SCENARIO_CHAINS_REGISTRY:
            paths.append(
                (
                    SCENARIO_CHAINS_REGISTRY,
                    "Registry changes may require scenario-chain consistency.",
                )
            )
        if source != WORK_ORDERS_REGISTRY:
            paths.append(
                (
                    WORK_ORDERS_REGISTRY,
                    "Registry changes may require work-order capability refs or status consistency.",
                )
            )
        return paths
    return []


def project_required_companion_writes(
    *,
    project_root: Path | str | None = None,
    observed_actual_writes: list[Any] | None = None,
    declared_writes: list[Any] | None = None,
    document_roles: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return required companion write paths for supplied write evidence."""

    del declared_writes  # Reserved for future source-aware projection.
    active_work_order_paths = active_work_order_paths_from_document_roles(document_roles)
    observed = list(observed_actual_writes or [])
    triggers: list[dict[str, Any]] = []
    ignored_items: list[dict[str, Any]] = []
    obligations_by_path: dict[str, dict[str, Any]] = {}
    unprojected_triggers: list[dict[str, Any]] = []

    for item in observed:
        path = item_path(item)
        operation = item_operation(item)
        if not path:
            ignored_items.append({"reason": "missing_path", "item": item})
            continue
        trigger = trigger_for_write(path, operation)
        if not trigger:
            ignored_items.append(
                {
                    "path": path,
                    "operation": operation,
                    "reason": "no_companion_write_trigger",
                }
            )
            continue
        triggers.append(trigger)
        companion_paths = companion_paths_for_trigger(
            trigger,
            active_work_order_paths=active_work_order_paths,
        )
        if not companion_paths:
            unprojected_triggers.append(trigger)
            continue
        for companion_path, reason in companion_paths:
            existing = obligations_by_path.get(companion_path)
            if existing:
                existing.setdefault("triggers", []).append(trigger)
                existing["trigger_count"] = len(existing["triggers"])
                continue
            obligations_by_path[companion_path] = {
                "path": companion_path,
                "operation": "modify",
                "evidence_kind": "required_companion_write",
                "evidence_status": "projected",
                "source_kind": "companion_write_obligation",
                "source_ref": "MVP-RECEIPT-02A",
                "reason": reason,
                "role": "required_companion_write",
                "obligation_level": "required",
                "applicability_status": "applicable",
                "applicability_reason": "projected from observed write trigger",
                "trigger": trigger,
                "triggers": [trigger],
                "trigger_count": 1,
            }

    obligations = sorted(obligations_by_path.values(), key=lambda item: item["path"])
    return {
        "schema": COMPANION_WRITE_OBLIGATION_SCHEMA,
        "schema_version": COMPANION_WRITE_OBLIGATION_SCHEMA,
        "status": "ok"
        if not triggers or obligations
        else "review",
        "project_root": str(Path(project_root).resolve()) if project_root else None,
        "generated_at_utc": utc_now_iso(),
        "required_companion_write_count": len(obligations),
        "required_companion_write_set": obligations,
        "trigger_count": len(triggers),
        "triggers": triggers,
        "unprojected_trigger_count": len(unprojected_triggers),
        "unprojected_triggers": unprojected_triggers,
        "ignored_item_count": len(ignored_items),
        "ignored_items": ignored_items,
        "active_work_order_paths": active_work_order_paths,
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_write_files",
            "does_not_read_file_contents",
            "does_not_inspect_git",
            "does_not_call_llm",
            "does_not_assign_round_attribution",
        ],
    }
