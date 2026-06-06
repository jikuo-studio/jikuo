"""JIKUO Studio global status read model.

This module is intentionally read-only. It aggregates existing JIKUO status
surfaces into one compact object that a future thin frontend can consume
without reimplementing governance semantics or scraping Markdown cards.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

if __package__:
    from . import artifact_assurance
    from . import actions as studio_actions
    from . import panels as studio_panels
    from .. import (
        activation_settings,
        configuration_review,
        policy_management_status,
        policy_templates,
        project_state,
        runtime_visibility,
        turn_anchor,
    )
    from ..integrations.mcp import adapter as mcp_adapter
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from jikuo.studio import artifact_assurance
    from jikuo.studio import actions as studio_actions
    from jikuo.studio import panels as studio_panels
    from jikuo import (
        activation_settings,
        configuration_review,
        policy_management_status,
        policy_templates,
        project_state,
        runtime_visibility,
        turn_anchor,
    )
    from jikuo.integrations.mcp import adapter as mcp_adapter


GLOBAL_STATUS_SCHEMA = "jikuo.studio.global_status.v0"
PROJECT_CONTEXT_REF = ".jikuo/project_context.yaml"
REGISTRY_REFS = {
    "work_orders": "docs/registry/work_orders.yaml",
    "capabilities": "docs/registry/capabilities.yaml",
    "mount_sets": "docs/registry/mount_sets.yaml",
    "registry_index": "docs/registry/registry_index.yaml",
}
CONFIGURATION_LANGUAGE_SCHEMA = "jikuo.studio.configuration_language.v0"
ROUND_DOCUMENT_TRACES_SCHEMA = "jikuo.studio.round_document_traces.v0"
ROUND_DOCUMENT_TRACE_SCHEMA = "jikuo.studio.round_document_trace.v0"
SEMANTIC_INTENT_EVIDENCE_SCHEMA = "jikuo.studio.semantic_intent_evidence.v0"
ROUND_DOCUMENT_TRACE_HISTORY_LIMIT = 24


def document_rule_source_descriptor(path_ref: str) -> dict[str, Any]:
    if path_ref == PROJECT_CONTEXT_REF:
        return {
            "path": path_ref,
            "source_kind": "editable_configuration",
            "user_label": "Editable configuration",
            "user_description": "Where Studio previews Document Rules changes and future guarded apply writes project-local document configuration.",
            "editable_in_studio": True,
            "write_target": True,
            "internal_role": "project_context.main_document_mounts",
        }
    if path_ref == "docs/governance/jikuo_execution_mounts.md":
        return {
            "path": path_ref,
            "source_kind": "governance_guidance",
            "user_label": "Governance guidance",
            "user_description": "Project-level execution guide that explains why these rules exist; it is read as context, not edited by Document Rules.",
            "editable_in_studio": False,
            "write_target": False,
            "internal_role": "program_level_roadmap_and_mount_guidance",
        }
    if path_ref.startswith("docs/registry/"):
        return {
            "path": path_ref,
            "source_kind": "registry_authority",
            "user_label": "Registry authority",
            "user_description": "Machine-readable registry shard used for routing and metadata, not a direct Document Rules edit target.",
            "editable_in_studio": False,
            "write_target": False,
            "internal_role": "registry_shard",
        }
    return {
        "path": path_ref,
        "source_kind": "reference_source",
        "user_label": "Reference source",
        "user_description": "A document-rule reference source. Review its source role before making it editable.",
        "editable_in_studio": False,
        "write_target": False,
        "internal_role": "unclassified_active_mount_authority",
    }


def classify_document_rule_sources(active_mount_authority: list[str]) -> list[dict[str, Any]]:
    return [document_rule_source_descriptor(str(path_ref)) for path_ref in active_mount_authority]


def document_mount_configuration_terms(
    *,
    active_mount_authority: list[str],
    mount_sets_ref: str,
) -> list[dict[str, Any]]:
    return [
        {
            "term_id": "document_rules",
            "user_label": "Document rules",
            "user_description": "Which project documents JIKUO should use as context, checks, and governance references.",
            "internal_refs": [
                ".jikuo/project_context.yaml document_roles",
                ".jikuo/project_context.yaml main_document_mounts",
                mount_sets_ref,
            ],
            "stability_rule": "frontend binds to term_id and user_label, not internal_refs",
        },
        {
            "term_id": "completion_checks",
            "user_label": "Completion checks",
            "user_description": "Documents JIKUO should review before saying a governed slice is complete.",
            "internal_refs": [
                ".jikuo/project_context.yaml main_document_mounts.checked_before_slice_completion",
            ],
            "stability_rule": "frontend wording stays stable even if the stored field moves",
        },
        {
            "term_id": "rule_sources",
            "user_label": "Configuration sources and guidance",
            "user_description": "Which files store editable Document Rules configuration versus which files explain governance context.",
            "internal_refs": active_mount_authority,
            "stability_rule": "user-facing source concept stays stable even if authority files change",
        },
        {
            "term_id": "editable_configuration",
            "user_label": "Editable configuration",
            "user_description": "The structured project-local configuration that Studio may update after a guarded apply.",
            "internal_refs": [PROJECT_CONTEXT_REF],
            "stability_rule": "configuration may move later, but Studio keeps this user-facing concept stable",
        },
        {
            "term_id": "governance_guidance",
            "user_label": "Governance guidance",
            "user_description": "Human-readable execution guidance and roadmap context; this should become help/projection text as structured configuration matures.",
            "internal_refs": ["docs/governance/jikuo_execution_mounts.md"],
            "stability_rule": "guidance documents explain configuration but are not the primary edit target",
        },
        {
            "term_id": "edit_status",
            "user_label": "How changes are applied",
            "user_description": "Document-rule changes must be previewed, approved, and applied through a guarded write.",
            "internal_refs": [
                "studio.document_mounts.plan_update",
                "studio.document_mounts.apply_update",
            ],
            "stability_rule": "frontend says whether editing is available, not which implementation owns it",
        },
    ]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def diagnostic(
    code: str,
    *,
    severity: str,
    message: str,
    source_ref: str | None = None,
    next_action: str | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "source_ref": source_ref,
        "next_action": next_action,
    }


def source_ref(path: str) -> dict[str, str]:
    return {"ref": path, "type": "project_file"}


def safe_section(
    name: str,
    builder: Callable[[], dict[str, Any]],
    *,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    try:
        return builder()
    except Exception as exc:  # pragma: no cover - defensive UI boundary
        diagnostics.append(
            diagnostic(
                f"{name}_unavailable",
                severity="error",
                message=f"{name} summary unavailable: {exc}",
                next_action="inspect the source read model directly",
            )
        )
        return {
            "status": "unavailable",
            "reason": f"{name} summary unavailable: {exc}",
        }


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group("body") if match else ""


def markdown_backtick_value(text: str, label: str) -> str | None:
    match = re.search(
        rf"^- {re.escape(label)}: `([^`]*)`",
        text,
        flags=re.MULTILINE,
    )
    return match.group(1) if match else None


def markdown_int_value(text: str, label: str) -> int:
    value = markdown_backtick_value(text, label)
    if value is None:
        match = re.search(
            rf"^- {re.escape(label)}: ([0-9]+)",
            text,
            flags=re.MULTILINE,
        )
        value = match.group(1) if match else None
    try:
        return int(value or 0)
    except ValueError:
        return 0


def history_ref_for_card(project_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def history_markdown_for_ref(project_root: Path, history_ref: str | None) -> str | None:
    if not history_ref:
        return None
    resolved = (project_root / history_ref).resolve()
    runtime_root = runtime_visibility.runtime_root_for(project_root)
    try:
        resolved.relative_to(runtime_root)
    except ValueError:
        return None
    return f"[{Path(history_ref).name}]({resolved.as_posix()})"


def state_summary_for_history_card(project_root: Path, path: Path) -> dict[str, Any] | None:
    state_path = path.with_suffix(".json").resolve()
    runtime_root = runtime_visibility.runtime_root_for(project_root)
    try:
        state_path.relative_to(runtime_root)
    except ValueError:
        return None
    if not state_path.is_file():
        return None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if state.get("schema") != runtime_visibility.RUNTIME_STATE_SUMMARY_SCHEMA:
        return None
    expected_ref = history_ref_for_card(project_root, path)
    runtime = state.setdefault("runtime_visibility", {})
    observed_ref = runtime.get("history_ref")
    if observed_ref and observed_ref != expected_ref:
        return None
    runtime["history_ref"] = expected_ref
    return state


def utc_from_history_name(name: str) -> str | None:
    match = re.match(r"(?P<stamp>\d{8}T\d{6}Z)_", name)
    if not match:
        return None
    try:
        parsed = datetime.strptime(match.group("stamp"), "%Y%m%dT%H%M%SZ")
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def artifact_assurance_from_history_card(
    text: str,
    *,
    event: str | None,
    history_ref: str,
) -> dict[str, Any]:
    section = markdown_section(text, "Artifact Assurance")
    if not section:
        return {}
    required_reads = markdown_int_value(section, "Required reads")
    read_evidence = markdown_int_value(section, "Read evidence")
    completion_checks = markdown_int_value(section, "Completion-check documents")
    completion_not_evaluated = markdown_int_value(
        section,
        "Completion-check documents not evaluated",
    )
    applicable_required_writes = markdown_int_value(section, "Applicable required writes")
    planned_writes = markdown_int_value(section, "Planned writes")
    actual_writes = markdown_int_value(section, "Actual writes")
    required_companion_writes = markdown_int_value(section, "Required companion writes")
    declared_writes = markdown_int_value(section, "Declared writes")
    companion_triggers = markdown_int_value(section, "Companion write triggers")
    companion_ignored = markdown_int_value(section, "Companion ignored actual writes")
    gap_count = markdown_int_value(section, "Gap count")
    required_reads_without_evidence = markdown_int_value(
        section,
        "Required reads without evidence",
    )
    return {
        "schema": artifact_assurance.ARTIFACT_ASSURANCE_SCHEMA,
        "schema_version": artifact_assurance.ARTIFACT_ASSURANCE_SCHEMA,
        "status": markdown_backtick_value(section, "Status") or "review",
        "guarantee": markdown_backtick_value(section, "Guarantee")
        or "evidence_comparison_only",
        "read_assurance": {
            "status": markdown_backtick_value(section, "Read assurance status"),
            "required_read_count": required_reads,
            "read_evidence_count": read_evidence,
            "required_read_set": [],
            "read_evidence_set": [],
            "required_not_read": [],
            "required_reads_without_evidence_count": required_reads_without_evidence,
        },
        "write_assurance": {
            "status": markdown_backtick_value(section, "Write assurance status"),
            "required_write_count": applicable_required_writes,
            "required_companion_write_count": required_companion_writes,
            "companion_trigger_count": companion_triggers,
            "companion_ignored_item_count": companion_ignored,
            "planned_write_count": planned_writes,
            "declared_write_count": declared_writes,
            "actual_write_count": actual_writes,
            "required_write_set": [],
            "required_companion_write_set": [],
            "completion_check_candidate_count": completion_checks,
            "completion_check_candidates": [],
            "completion_check_not_evaluated": [],
            "completion_check_not_evaluated_count": completion_not_evaluated,
            "planned_write_set": [],
            "declared_write_set": [],
            "actual_write_set": [],
            "required_not_planned": [],
            "required_not_written": [],
            "planned_not_written": [],
            "unplanned_written": [],
        },
        "gap_report": {
            "status": "review" if gap_count or completion_not_evaluated else "ok",
            "gap_count": gap_count,
            "read_gap_count": required_reads_without_evidence,
            "write_gap_count": max(0, gap_count - required_reads_without_evidence),
            "completion_check_not_evaluated_count": completion_not_evaluated,
            "read_gaps": [],
            "write_gaps": [],
            "invalid_refs": [],
        },
        "runtime_projection": {
            "schema": "jikuo.runtime_artifact_assurance_projection.v0",
            "event": event,
            "source": "runtime_history_card",
            "persistence": "runtime_card_history",
            "history_ref": history_ref,
            "non_effects": [
                "does_not_read_files_by_itself",
                "does_not_inspect_git_diff",
                "does_not_persist_data01_events",
            ],
        },
    }


def count_artifacts(report: dict[str, Any]) -> dict[str, int]:
    read = report.get("read_assurance") or {}
    write = report.get("write_assurance") or {}
    gaps = report.get("gap_report") or {}
    return {
        "required_read_count": int(read.get("required_read_count") or 0),
        "read_evidence_count": int(read.get("read_evidence_count") or 0),
        "planned_write_count": int(write.get("planned_write_count") or 0),
        "required_companion_write_count": int(
            write.get("required_companion_write_count")
            or len(write.get("required_companion_write_set") or [])
            or 0
        ),
        "companion_trigger_count": int(
            write.get("companion_trigger_count")
            or ((report.get("runtime_projection") or {}).get("companion_write_obligations") or {}).get("trigger_count")
            or 0
        ),
        "companion_ignored_item_count": int(
            write.get("companion_ignored_item_count")
            or ((report.get("runtime_projection") or {}).get("companion_write_obligations") or {}).get("ignored_item_count")
            or 0
        ),
        "declared_write_count": int(
            write.get("declared_write_count")
            or len(write.get("declared_write_set") or [])
            or write.get("planned_write_count")
            or 0
        ),
        "actual_write_count": int(write.get("actual_write_count") or 0),
        "completion_check_candidate_count": int(
            write.get("completion_check_candidate_count")
            or len(write.get("completion_check_candidates") or [])
            or 0
        ),
        "completion_check_not_evaluated_count": int(
            gaps.get("completion_check_not_evaluated_count")
            or write.get("completion_check_not_evaluated_count")
            or len(write.get("completion_check_not_evaluated") or [])
            or 0
        ),
        "gap_count": int(gaps.get("gap_count") or 0),
    }


def empty_artifact_counts() -> dict[str, int]:
    return {
        "required_read_count": 0,
        "read_evidence_count": 0,
        "planned_write_count": 0,
        "required_companion_write_count": 0,
        "companion_trigger_count": 0,
        "companion_ignored_item_count": 0,
        "declared_write_count": 0,
        "actual_write_count": 0,
        "completion_check_candidate_count": 0,
        "completion_check_not_evaluated_count": 0,
        "gap_count": 0,
    }


def round_document_change_status(counts: dict[str, int], *, has_trace: bool) -> str:
    if not has_trace:
        return "no_trace"
    if counts["planned_write_count"] or counts["actual_write_count"]:
        return "changes_reported"
    return "no_document_changes_reported"


def round_document_change_label(status: str) -> str:
    return {
        "changes_reported": "Document changes reported",
        "no_document_changes_reported": "No document changes reported",
        "no_trace": "No document trace",
    }.get(status, status)


def round_trace_from_parts(
    *,
    project_root: Path,
    history_ref: str | None,
    source_kind: str,
    updated_at_utc: str | None,
    lifecycle_event: str | None,
    intent_class: str | None,
    operation_class: str | None,
    status: str | None,
    proposal_id: str | None,
    artifact_report: dict[str, Any],
    semantic_coverage: dict[str, Any] | None = None,
    turn_anchor_projection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    has_trace = bool(artifact_report.get("schema"))
    counts = count_artifacts(artifact_report) if has_trace else empty_artifact_counts()
    change_status = round_document_change_status(counts, has_trace=has_trace)
    round_id = Path(history_ref).stem if history_ref else f"{source_kind}:{updated_at_utc or 'unknown'}"
    label_time = updated_at_utc or "unknown time"
    event_label = lifecycle_event or "unknown event"
    return {
        "schema": ROUND_DOCUMENT_TRACE_SCHEMA,
        "round_id": round_id,
        "label": f"{label_time} / {event_label}",
        "updated_at_utc": updated_at_utc,
        "source_kind": source_kind,
        "history_ref": history_ref,
        "history_markdown": history_markdown_for_ref(project_root, history_ref),
        "lifecycle_event": lifecycle_event,
        "intent_class": intent_class,
        "operation_class": operation_class,
        "proposal_status": status,
        "proposal_id": proposal_id,
        "has_document_trace": has_trace,
        "has_document_changes": change_status == "changes_reported",
        "document_change_status": change_status,
        "document_change_label": round_document_change_label(change_status),
        "trace_label": "Document trace available" if has_trace else "No document trace",
        "counts": counts,
        "semantic_intent_coverage": semantic_coverage or {},
        "turn_anchor": turn_anchor_projection or turn_anchor.missing_turn_anchor(),
        "artifact_assurance": artifact_report if has_trace else {},
        "non_effects": [
            "does_not_read_files_by_itself",
            "does_not_inspect_git_diff",
            "does_not_create_data01_event_ledger_entries",
        ],
    }


def round_trace_from_state(
    project_root: Path,
    state: dict[str, Any],
    *,
    source_kind: str = "latest_runtime_state",
) -> dict[str, Any] | None:
    if state.get("status") in {"missing", "invalid", "unavailable"} and not state.get(
        "runtime_visibility"
    ):
        return None
    source = state.get("source") or {}
    runtime = state.get("runtime_visibility") or {}
    history_ref = runtime.get("history_ref")
    artifact_report = state.get("artifact_assurance") or {}
    policy_runtime = state.get("policy_runtime_status") or {}
    work_profile = state.get("work_profile") or {}
    if not isinstance(work_profile, dict):
        work_profile = {}
    if not work_profile and isinstance(policy_runtime, dict):
        work_profile = policy_runtime.get("work_profile") or {}
    if not isinstance(work_profile, dict):
        work_profile = {}
    semantic_coverage = state.get("semantic_intent_coverage") or {}
    if not semantic_coverage:
        for coverage_source in (state, state.get("policy_runtime_status") or {}):
            if not isinstance(coverage_source, dict):
                continue
            candidate = runtime_visibility.semantic_intent_coverage_for(coverage_source)
            if not semantic_coverage or candidate.get("coverage_status") == "complete":
                semantic_coverage = candidate
            if candidate.get("coverage_status") == "complete":
                break
    turn_anchor_projection = turn_anchor.normalize_turn_anchor(state.get("turn_anchor"))
    return round_trace_from_parts(
        project_root=project_root,
        history_ref=str(history_ref) if history_ref else None,
        source_kind=source_kind,
        updated_at_utc=state.get("updated_at_utc"),
        lifecycle_event=source.get("event") or work_profile.get("lifecycle_event"),
        intent_class=work_profile.get("intent_class"),
        operation_class=work_profile.get("operation_class"),
        status=source.get("status"),
        proposal_id=source.get("proposal_id"),
        artifact_report=artifact_report if isinstance(artifact_report, dict) else {},
        semantic_coverage=semantic_coverage
        if isinstance(semantic_coverage, dict)
        else {},
        turn_anchor_projection=turn_anchor_projection,
    )


def round_trace_from_history_card(project_root: Path, path: Path) -> dict[str, Any]:
    state = state_summary_for_history_card(project_root, path)
    if state:
        trace = round_trace_from_state(
            project_root,
            state,
            source_kind="runtime_history_state_summary",
        )
        if trace:
            trace["trace_label"] = (
                "Structured document receipt"
                if trace.get("has_document_trace")
                else trace.get("trace_label")
            )
            return trace

    history_ref = history_ref_for_card(project_root, path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    lifecycle_event = markdown_backtick_value(text, "Lifecycle event")
    artifact_report = artifact_assurance_from_history_card(
        text,
        event=lifecycle_event,
        history_ref=history_ref,
    )
    return round_trace_from_parts(
        project_root=project_root,
        history_ref=history_ref,
        source_kind="runtime_history_card",
        updated_at_utc=utc_from_history_name(path.name),
        lifecycle_event=lifecycle_event,
        intent_class=markdown_backtick_value(text, "Intent class"),
        operation_class=markdown_backtick_value(text, "Operation class"),
        status=markdown_backtick_value(text, "Status"),
        proposal_id=markdown_backtick_value(text, "Proposal id"),
        artifact_report=artifact_report,
        turn_anchor_projection=turn_anchor.missing_turn_anchor(
            reason="history_card_has_no_structured_turn_anchor"
        ),
    )


def latest_completion_receipt_round(rounds: list[dict[str, Any]]) -> dict[str, Any] | None:
    for round_trace in rounds:
        if (
            round_trace.get("lifecycle_event") == "completion_review"
            and round_trace.get("has_document_trace")
        ):
            return round_trace
    for round_trace in rounds:
        if round_trace.get("lifecycle_event") == "completion_review":
            return round_trace
    return None


def round_document_traces(project_root: Path, state: dict[str, Any]) -> dict[str, Any]:
    runtime_root = runtime_visibility.runtime_root_for(project_root)
    history_root = runtime_root / "history"
    rounds: list[dict[str, Any]] = []
    seen_refs: set[str] = set()
    latest = round_trace_from_state(project_root, state)
    if latest:
        rounds.append(latest)
        if latest.get("history_ref"):
            seen_refs.add(str(latest["history_ref"]))
    if history_root.is_dir():
        for path in sorted(history_root.glob("*.md"), key=lambda item: item.name, reverse=True):
            history_ref = history_ref_for_card(project_root, path)
            if history_ref in seen_refs:
                continue
            rounds.append(round_trace_from_history_card(project_root, path))
            seen_refs.add(history_ref)
            if len(rounds) >= ROUND_DOCUMENT_TRACE_HISTORY_LIMIT:
                break
    latest_runtime_round = rounds[0] if rounds else None
    latest_receipt_round = latest_completion_receipt_round(rounds)
    default_round = latest_receipt_round or latest_runtime_round
    return {
        "schema": ROUND_DOCUMENT_TRACES_SCHEMA,
        "schema_version": ROUND_DOCUMENT_TRACES_SCHEMA,
        "status": "available" if rounds else "missing",
        "default_round_id": default_round.get("round_id") if default_round else None,
        "default_selection": (
            "latest_completion_receipt"
            if latest_receipt_round
            else "latest_runtime_state"
            if latest_runtime_round
            else None
        ),
        "latest_runtime_round_id": (
            latest_runtime_round.get("round_id") if latest_runtime_round else None
        ),
        "latest_runtime_round_label": (
            latest_runtime_round.get("label") if latest_runtime_round else None
        ),
        "latest_completion_receipt_round_id": (
            latest_receipt_round.get("round_id") if latest_receipt_round else None
        ),
        "latest_completion_receipt_label": (
            latest_receipt_round.get("label") if latest_receipt_round else None
        ),
        "completion_receipt_status": "available" if latest_receipt_round else "missing",
        "round_count": len(rounds),
        "rounds_with_document_trace_count": sum(
            1 for item in rounds if item.get("has_document_trace")
        ),
        "rounds_with_document_changes_count": sum(
            1 for item in rounds if item.get("has_document_changes")
        ),
        "rounds": rounds,
        "read_model_limitations": [
            "latest runtime round uses structured state_summary when available",
            "default selected trace prefers the latest completion_review receipt when available",
            "older round labels are derived from runtime history cards and may expose counts without full artifact path sets",
            "this read model does not inspect git diff or infer edits outside JIKUO runtime evidence",
            "raw prompt text is not stored in round traces; turn anchors expose only host ids and prompt digest status when available",
        ],
        "writes_performed": False,
        "write_allowed_by_command": False,
    }


def semantic_intent_status_for_latest_round(coverage: dict[str, Any]) -> str:
    coverage_status = str(coverage.get("coverage_status") or "")
    semantic_status = str(coverage.get("semantic_intent_status") or "")
    provider = str(coverage.get("provider") or "")
    if semantic_status == "provided" and provider == "host_ai":
        return "available" if coverage_status == "complete" else "degraded"
    if coverage_status in {"missing", "fallback_only", "degraded"}:
        return "degraded"
    return "unavailable"


def semantic_coverage_is_host_ai_classified(coverage: dict[str, Any] | None) -> bool:
    if not isinstance(coverage, dict):
        return False
    return (
        str(coverage.get("semantic_intent_status") or "") == "provided"
        and str(coverage.get("provider") or "") == "host_ai"
    )


def latest_host_ai_semantic_round(
    rounds: list[dict[str, Any]],
) -> dict[str, Any] | None:
    for item in rounds:
        if not isinstance(item, dict):
            continue
        if semantic_coverage_is_host_ai_classified(item.get("semantic_intent_coverage")):
            return item
    return None


def semantic_imperfection(
    *,
    title: str,
    detail: str,
    status: str = "degraded",
    source_ref: str | None = None,
) -> dict[str, Any]:
    return {
        "title": title,
        "detail": detail,
        "status": status,
        "source_ref": source_ref,
    }


def latest_available_turn_anchor_from_rounds(
    rounds: list[dict[str, Any]],
) -> dict[str, Any]:
    for item in rounds:
        if not isinstance(item, dict):
            continue
        candidate = turn_anchor.normalize_turn_anchor(item.get("turn_anchor"))
        if candidate.get("status") != "available":
            continue
        enriched = dict(candidate)
        enriched["evidence_round_id"] = item.get("round_id")
        enriched["evidence_round_label"] = item.get("label")
        enriched["evidence_source_kind"] = item.get("source_kind")
        enriched["evidence_history_ref"] = item.get("history_ref")
        return enriched
    return turn_anchor.missing_turn_anchor(
        reason="no_retained_round_with_available_turn_anchor"
    )


def semantic_intent_evidence_overview(
    *,
    runtime: dict[str, Any],
    activation: dict[str, Any],
) -> dict[str, Any]:
    trace_list = runtime.get("round_document_traces") or {}
    rounds = trace_list.get("rounds") or []
    latest_runtime = next(
        (
            item
            for item in rounds
            if item.get("round_id") == trace_list.get("latest_runtime_round_id")
        ),
        rounds[0] if rounds else None,
    )
    latest_runtime_coverage = (
        latest_runtime.get("semantic_intent_coverage")
        if isinstance(latest_runtime, dict)
        else None
    )
    classification_round = latest_host_ai_semantic_round(rounds) or latest_runtime
    coverage = (
        classification_round.get("semantic_intent_coverage")
        if isinstance(classification_round, dict)
        else None
    ) or latest_runtime_coverage or runtime.get("semantic_intent_coverage") or {}
    if not isinstance(coverage, dict):
        coverage = {}
    latest_runtime_anchor = (
        latest_runtime.get("turn_anchor")
        if isinstance(latest_runtime, dict)
        else None
    ) or runtime.get("turn_anchor") or turn_anchor.missing_turn_anchor()
    latest_runtime_anchor = turn_anchor.normalize_turn_anchor(latest_runtime_anchor)
    retained_available_anchor = latest_available_turn_anchor_from_rounds(rounds)
    anchor = (
        latest_runtime_anchor
        if latest_runtime_anchor.get("status") == "available"
        else retained_available_anchor
    )

    semantic_status = str(coverage.get("semantic_intent_status") or "unavailable")
    evidence_status = str(coverage.get("evidence_status") or "unknown")
    coverage_status = str(coverage.get("coverage_status") or "unknown")
    provider = str(coverage.get("provider") or "unavailable")
    evidence_source_kind = str(coverage.get("evidence_source_kind") or "unknown")
    policy_scopes = [
        str(item)
        for item in coverage.get("policy_scopes", [])
        if str(item)
    ] if isinstance(coverage.get("policy_scopes"), list) else []
    intent_class = (
        str(classification_round.get("intent_class") or "unknown")
        if isinstance(classification_round, dict)
        else "unknown"
    )
    operation_class = (
        str(classification_round.get("operation_class") or "unknown")
        if isinstance(classification_round, dict)
        else "unknown"
    )
    ai_classified = semantic_status == "provided" and provider == "host_ai"
    if ai_classified and evidence_source_kind == "runtime_inherited":
        classification_source = "runtime_inherited"
    elif ai_classified:
        classification_source = "host_ai"
    elif coverage_status == "fallback_only" or bool(coverage.get("fallback_expanded")):
        classification_source = "fallback_only"
    elif (
        coverage_status in {"missing", "unavailable"}
        or semantic_status in {"missing", "unavailable"}
        or provider in {"missing", "unavailable", "unknown"}
    ):
        classification_source = "missing"
    else:
        classification_source = "incomplete"
    strict_mount = str(activation.get("strict_mount_status") or "unknown")
    adapter_status = str(activation.get("adapter_status") or "unknown")

    imperfections: list[dict[str, Any]] = []
    if not latest_runtime:
        imperfections.append(
            semantic_imperfection(
                title="No latest runtime round",
                detail="Studio has no retained runtime round to classify.",
                status="unavailable",
                source_ref=runtime_visibility.HISTORY_DIR_REF,
            )
        )
    if not ai_classified:
        imperfections.append(
            semantic_imperfection(
                title="AI classification not proven",
                detail=(
                    f"Latest round semantic status is {semantic_status}; "
                    f"provider is {provider}."
                ),
                source_ref=(
                    classification_round.get("history_ref")
                    if isinstance(classification_round, dict)
                    else runtime_visibility.STATE_SUMMARY_REF
                ),
            )
        )
    if coverage_status != "complete":
        imperfections.append(
            semantic_imperfection(
                title="Classification evidence incomplete",
                detail=str(
                    coverage.get("gap_reason")
                    or f"coverage_status={coverage_status}; evidence_status={evidence_status}"
                ),
                source_ref=(
                    classification_round.get("history_ref")
                    if isinstance(classification_round, dict)
                    else runtime_visibility.STATE_SUMMARY_REF
                ),
            )
        )
    if (
        isinstance(latest_runtime, dict)
        and isinstance(classification_round, dict)
        and latest_runtime.get("round_id") != classification_round.get("round_id")
    ):
        latest_coverage = (
            latest_runtime_coverage if isinstance(latest_runtime_coverage, dict) else {}
        )
        imperfections.append(
            semantic_imperfection(
                title="Latest runtime semantic evidence incomplete",
                detail=(
                    "Latest runtime round is "
                    f"{latest_runtime.get('round_id')}; Studio is showing the "
                    f"latest retained host AI classification from "
                    f"{classification_round.get('round_id')} instead."
                ),
                status=semantic_intent_status_for_latest_round(latest_coverage),
                source_ref=latest_runtime.get("history_ref"),
            )
        )
    if latest_runtime_anchor.get("status") != "available":
        imperfections.append(
            semantic_imperfection(
                title="Latest runtime turn anchor missing",
                detail=(
                    "Latest round has no non-AI turn anchor; later task_start "
                    "or completion_review receipts cannot be linked to this user "
                    "turn by latest runtime evidence alone."
                ),
                source_ref=(
                    latest_runtime.get("history_ref")
                    if isinstance(latest_runtime, dict)
                    else runtime_visibility.STATE_SUMMARY_REF
                ),
            )
        )
    if anchor.get("status") != "available":
        imperfections.append(
            semantic_imperfection(
                title="No retained turn anchor",
                detail=(
                    "No retained runtime round currently exposes an available "
                    "non-AI turn anchor."
                ),
                source_ref=runtime_visibility.HISTORY_DIR_REF,
            )
        )
    if ai_classified and strict_mount not in {"available", "strict", "configured"}:
        imperfections.append(
            semantic_imperfection(
                title="Not strict pre-turn proof",
                detail=(
                    "The latest round shows host AI semantic intent reached JIKUO, "
                    f"but strict_mount={strict_mount} and adapter={adapter_status}; "
                    "this is not proof of enforced pre-action GUI gating."
                ),
                source_ref=activation_settings.SETTINGS_REF,
            )
        )

    status = semantic_intent_status_for_latest_round(coverage)
    if ai_classified:
        headline = f"AI classified the latest round as {intent_class}."
    else:
        headline = "Latest round has no proven AI semantic classification."

    return {
        "schema": SEMANTIC_INTENT_EVIDENCE_SCHEMA,
        "status": status,
        "headline": headline,
        "latest_round": (
            {
                "round_id": latest_runtime.get("round_id"),
                "label": latest_runtime.get("label"),
                "lifecycle_event": latest_runtime.get("lifecycle_event"),
                "source_kind": latest_runtime.get("source_kind"),
                "history_ref": latest_runtime.get("history_ref"),
            }
            if isinstance(latest_runtime, dict)
            else {}
        ),
        "classification_round": (
            {
                "round_id": classification_round.get("round_id"),
                "label": classification_round.get("label"),
                "lifecycle_event": classification_round.get("lifecycle_event"),
                "source_kind": classification_round.get("source_kind"),
                "history_ref": classification_round.get("history_ref"),
            }
            if isinstance(classification_round, dict)
            else {}
        ),
        "classification": {
            "ai_classified": ai_classified,
            "classification_source": classification_source,
            "classifier": provider if ai_classified else "not_proven_ai",
            "intent_class": intent_class,
            "operation_class": operation_class,
            "policy_scopes": policy_scopes,
            "semantic_intent_status": semantic_status,
            "evidence_status": evidence_status,
            "coverage_status": coverage_status,
            "provider": provider,
            "evidence_source_kind": evidence_source_kind,
            "fallback_expanded": bool(coverage.get("fallback_expanded")),
        },
        "turn_anchor": anchor,
        "latest_runtime_turn_anchor": latest_runtime_anchor,
        "imperfection_count": len(imperfections),
        "imperfections": imperfections,
        "read_model_limitations": [
            "semantic classification reports the latest retained host AI semantic round when available",
            "latest_round remains the latest retained runtime round and may have weaker semantic evidence",
            "turn_anchor reports the latest retained available anchor when the latest runtime round lacks one",
            "it does not infer hidden model intent beyond stored semantic evidence",
            "host AI classification evidence does not prove strict pre-action GUI gating",
            "raw prompt text is not stored here; prompt identity is represented by digest status only",
        ],
        "non_effects": [
            "does_not_call_llm_provider",
            "does_not_infer_hidden_model_intent",
            "does_not_change_policy_evaluator_results",
            "does_not_prove_strict_gui_semantic_gate",
        ],
    }


def runtime_summary(project_root: Path, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    state = runtime_visibility.load_state_summary(project_root=project_root)
    _card, last_card_report = runtime_visibility.load_last_card(project_root=project_root)
    state_status = str(state.get("status") or "available")
    last_card_status = str(last_card_report.get("status") or "available")
    status = "available" if state_status == "available" and last_card_status == "available" else "degraded"
    if state_status != "available":
        diagnostics.append(
            diagnostic(
                "runtime_state_summary_not_available",
                severity="warning",
                message=str(state.get("reason") or "runtime state summary is not available"),
                source_ref=runtime_visibility.STATE_SUMMARY_REF,
                next_action="run a card-producing JIKUO proposal or inspect `jikuo show`",
            )
        )
    if last_card_status != "available":
        diagnostics.append(
            diagnostic(
                "runtime_last_card_not_available",
                severity="warning",
                message=str(last_card_report.get("reason") or "runtime last card is not available"),
                source_ref=runtime_visibility.LAST_CARD_REF,
                next_action="run a card-producing JIKUO proposal",
            )
        )
    display_links = state.get("client_display_links") or {}
    links = display_links.get("links") or {}
    counts = state.get("counts") or {}
    semantic_coverage = state.get("semantic_intent_coverage") or {}
    turn_anchor_projection = turn_anchor.normalize_turn_anchor(state.get("turn_anchor"))
    semantic_status = str(semantic_coverage.get("coverage_status") or "")
    if semantic_status in {"missing", "fallback_only", "degraded"}:
        diagnostics.append(
            diagnostic(
                "runtime_semantic_intent_coverage_degraded",
                severity="warning",
                message=(
                    "Semantic intent coverage is "
                    f"{semantic_status}: "
                    f"{semantic_coverage.get('gap_reason') or 'host semantic evidence is incomplete'}"
                ),
                source_ref=runtime_visibility.STATE_SUMMARY_REF,
                next_action=(
                    "provide compact host_semantic_intent before governed action "
                    "or final response"
                ),
            )
        )
    round_traces = round_document_traces(project_root, state)
    return {
        "status": status,
        "updated_at_utc": state.get("updated_at_utc"),
        "last_card_status": last_card_status,
        "state_summary_status": state_status,
        "counts": {
            "card_count": counts.get("card_count", 0),
            "triggered_policy_count": counts.get("triggered_policy_count", 0),
            "missing_evidence_count": counts.get("missing_evidence_count", 0),
            "required_action_count": counts.get("required_action_count", 0),
        },
        "observed_lifecycle": state.get("observed_lifecycle") or {},
        "semantic_intent_coverage": semantic_coverage,
        "turn_anchor": turn_anchor_projection,
        "artifact_assurance": state.get("artifact_assurance") or {},
        "round_document_traces": round_traces,
        "lifecycle_card_count": len(state.get("lifecycle_card_links") or []),
        "card_links": {
            "last_card": (links.get("last_card") or {}).get("markdown"),
            "state_summary": (links.get("state_summary") or {}).get("markdown"),
            "history_card": (links.get("history_card") or {}).get("markdown"),
        },
    }


def activation_summary(
    project_root: Path,
    diagnostics: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    report = activation_settings.build_status_report(project_root=project_root)
    decisions = list(report.get("required_user_decisions") or [])
    status = "available" if report.get("status") == "available" and not decisions else "degraded"
    if decisions:
        diagnostics.append(
            diagnostic(
                "activation_settings_require_review",
                severity="warning",
                message="activation settings have required user decisions",
                source_ref=activation_settings.SETTINGS_REF,
                next_action=str(report.get("recommended_next_tool") or "review activation settings"),
            )
        )
    if report.get("status") == "missing":
        diagnostics.append(
            diagnostic(
                "activation_settings_missing",
                severity="warning",
                message="activation settings file is missing; implicit defaults are in effect",
                source_ref=activation_settings.SETTINGS_REF,
                next_action="run `jikuo settings plan` before assuming strict mounted behavior",
            )
        )
    return (
        {
            "status": status,
            "source_status": report.get("status"),
            "desired_trigger_mode": report.get("desired_trigger_mode"),
            "effective_enforcement_level": report.get("effective_enforcement_level"),
            "strict_mount_status": report.get("strict_mount_status"),
            "adapter_status": report.get("adapter_status"),
            "configuration_required": bool(report.get("configuration_required")),
            "onboarding_required": bool(report.get("onboarding_required")),
            "required_user_decision_count": len(decisions),
            "settings_ref": report.get("settings_ref"),
            "next_actions": report.get("next_actions") or [],
        },
        [
            {
                "domain": "activation",
                "field": item.get("field"),
                "current_value": item.get("current_value"),
                "recommended_next_tool": item.get("recommended_next_tool"),
                "meaning": item.get("meaning"),
            }
            for item in decisions
            if isinstance(item, dict)
        ],
    )


def configuration_summary(
    project_root: Path,
    diagnostics: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    report = configuration_review.build_configuration_review(project_root=project_root)
    status = "available" if report.get("status") == "ok" else "degraded"
    review_items = [
        item
        for item in report.get("items") or []
        if isinstance(item, dict) and item.get("status") != "ok"
    ]
    for item in review_items[:5]:
        diagnostics.append(
            diagnostic(
                f"configuration_{item.get('key')}_requires_review",
                severity="warning",
                message=f"{item.get('title')} requires review: {item.get('current')}",
                source_ref=(item.get("evidence_refs") or [None])[0],
                next_action=(item.get("next_actions") or [None])[0],
            )
        )
    return (
        {
            "status": status,
            "source_status": report.get("status"),
            "summary": report.get("summary") or {},
            "review_item_count": len(review_items),
            "review_items": [
                {
                    "key": item.get("key"),
                    "title": item.get("title"),
                    "status": item.get("status"),
                    "current": item.get("current"),
                    "next_action": (item.get("next_actions") or [None])[0],
                }
                for item in review_items
            ],
            "next_actions": report.get("next_actions") or [],
        },
        [
            {
                "domain": "configuration",
                "field": item.get("key"),
                "current_value": item.get("current"),
                "recommended_next_tool": (item.get("next_actions") or [None])[0],
                "meaning": item.get("meaning"),
            }
            for item in review_items
        ],
    )


def document_mounts_summary(
    project_root: Path,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    context_path = project_root / PROJECT_CONTEXT_REF
    if not context_path.is_file():
        diagnostics.append(
            diagnostic(
                "document_mounts_project_context_missing",
                severity="error",
                message="document mount summary requires .jikuo/project_context.yaml",
                source_ref=PROJECT_CONTEXT_REF,
                next_action="open a JIKUO project root before configuring document mounts",
            )
        )
        return {
            "status": "unavailable",
            "reason": "project context missing",
            "source_refs": [PROJECT_CONTEXT_REF],
        }
    try:
        context = policy_templates.read_yaml_subset(context_path)
    except Exception as exc:
        diagnostics.append(
            diagnostic(
                "document_mounts_project_context_invalid",
                severity="error",
                message=f"document mount summary could not parse project context: {exc}",
                source_ref=PROJECT_CONTEXT_REF,
                next_action="repair .jikuo/project_context.yaml",
            )
        )
        return {
            "status": "unavailable",
            "reason": f"project context invalid: {exc}",
            "source_refs": [PROJECT_CONTEXT_REF],
        }

    document_roles = context.get("document_roles") if isinstance(context, dict) else {}
    if not isinstance(document_roles, dict):
        document_roles = {}
    main_mounts = context.get("main_document_mounts") if isinstance(context, dict) else {}
    if not isinstance(main_mounts, dict):
        main_mounts = {}

    role_items: list[dict[str, Any]] = []
    missing_required_roles: list[dict[str, Any]] = []
    for role, record in sorted(document_roles.items()):
        if not isinstance(record, dict):
            continue
        path_value = record.get("path")
        required = bool(record.get("required"))
        exists = bool(path_value) and (project_root / str(path_value)).is_file()
        item = {
            "role": role,
            "path": path_value,
            "required": required,
            "status": "available" if exists else ("missing" if required else "not_bound"),
            "note": record.get("note"),
        }
        role_items.append(item)
        if required and not exists:
            missing_required_roles.append(item)

    checked_documents: list[dict[str, Any]] = []
    for record in main_mounts.get("checked_before_slice_completion") or []:
        if not isinstance(record, dict):
            continue
        path_value = record.get("path")
        exists = bool(path_value) and (project_root / str(path_value)).is_file()
        checked_documents.append(
            {
                "path": path_value,
                "status": "available" if exists else "missing",
                "update_required_when": record.get("update_required_when"),
            }
        )

    mount_sets_ref = REGISTRY_REFS["mount_sets"]
    mount_sets_path = project_root / mount_sets_ref
    mount_set_count = 0
    studio_mount_set_status = None
    if mount_sets_path.is_file():
        try:
            mount_sets = policy_templates.read_yaml_subset(mount_sets_path)
            entries = mount_sets.get("entries") if isinstance(mount_sets, dict) else []
            if isinstance(entries, list):
                mount_set_count = len(entries)
                for entry in entries:
                    if isinstance(entry, dict) and entry.get("id") == "MOUNT-STUDIO-01":
                        studio_mount_set_status = entry.get("status")
                        break
        except Exception as exc:
            diagnostics.append(
                diagnostic(
                    "document_mounts_mount_set_registry_invalid",
                    severity="warning",
                    message=f"mount-set registry could not be parsed: {exc}",
                    source_ref=mount_sets_ref,
                    next_action="run document registry tests",
                )
            )

    for item in missing_required_roles[:5]:
        diagnostics.append(
            diagnostic(
                f"document_role_{item['role']}_missing",
                severity="warning",
                message=f"required document role is missing: {item['role']}",
                source_ref=str(item.get("path") or PROJECT_CONTEXT_REF),
                next_action="review document mount configuration before editing this project",
            )
        )

    status = "available" if not missing_required_roles else "degraded"
    active_mount_authority = list(main_mounts.get("active_mount_authority") or [])
    rule_source_descriptors = classify_document_rule_sources(active_mount_authority)
    return {
        "status": status,
        "source_status": "available",
        "configuration_language_schema": CONFIGURATION_LANGUAGE_SCHEMA,
        "configuration_terms": document_mount_configuration_terms(
            active_mount_authority=active_mount_authority,
            mount_sets_ref=mount_sets_ref,
        ),
        "project_context_ref": PROJECT_CONTEXT_REF,
        "mount_sets_ref": mount_sets_ref,
        "canonical_path_root": main_mounts.get("canonical_path_root"),
        "path_policy": main_mounts.get("path_policy"),
        "active_mount_authority": active_mount_authority,
        "document_rule_sources": rule_source_descriptors,
        "editable_configuration_sources": [
            item for item in rule_source_descriptors if item["source_kind"] == "editable_configuration"
        ],
        "governance_guidance_sources": [
            item for item in rule_source_descriptors if item["source_kind"] == "governance_guidance"
        ],
        "non_editable_reference_sources": [
            item for item in rule_source_descriptors if not item["editable_in_studio"]
        ],
        "source_truth_boundary": {
            "structured_config": "source_of_truth_for_project_local_document_rules",
            "governance_guidance": "human_readable_context_projection_not_primary_edit_target",
            "studio_write_target": PROJECT_CONTEXT_REF,
        },
        "checked_before_slice_completion": checked_documents,
        "role_count": len(role_items),
        "required_role_count": sum(1 for item in role_items if item["required"]),
        "missing_required_role_count": len(missing_required_roles),
        "checked_document_count": len(checked_documents),
        "mount_set_count": mount_set_count,
        "studio_mount_set_status": studio_mount_set_status,
        "unchanged_report_required": bool(main_mounts.get("unchanged_report_required")),
        "scope_change_rule": main_mounts.get("scope_change_rule"),
        "roles": role_items[:64],
        "missing_required_roles": missing_required_roles[:16],
        "source_refs": [PROJECT_CONTEXT_REF, mount_sets_ref],
        "read_model_limitations": [
            "document mounts are read from project context and registry shards only",
            "this summary does not apply document-mount changes",
            "future guarded actions must plan and apply mount updates through governance tools",
        ],
    }


def policy_management_summary(
    project_root: Path,
    diagnostics: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    report = policy_management_status.build_policy_management_status(project_root=project_root)
    warnings = report.get("warnings") or []
    for warning in warnings[:5]:
        diagnostics.append(
            diagnostic(
                "policy_management_warning",
                severity="warning",
                message=str(warning),
                next_action="inspect `jikuo policy-management status`",
            )
        )
    counts = report.get("summary_counts") or {}
    followups = [
        {
            "domain": "policy_management",
            "field": "active_policy_distribution",
            "current_value": f"{counts.get('active_policy_without_package_template_count', 0)} active policies without package templates",
            "recommended_next_tool": "jikuo.propose_policy_distribution_review",
            "meaning": "Policies intended for reuse need distribution review before package or starter publication.",
        }
    ]
    return (
        {
            "status": "available" if report.get("status") == "available" else "degraded",
            "source_status": report.get("status"),
            "summary_counts": counts,
            "available_operation_count": len(report.get("available_operations") or []),
            "read_model_limitations": report.get("read_model_limitations") or [],
            "next_actions": report.get("next_actions") or [],
        },
        followups,
    )


def registry_summary(project_root: Path, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    registries: dict[str, Any] = {}
    status = "available"
    for key, ref in REGISTRY_REFS.items():
        path = project_root / ref
        if not path.is_file():
            status = "degraded"
            diagnostics.append(
                diagnostic(
                    f"registry_{key}_missing",
                    severity="warning",
                    message=f"registry shard is missing: {ref}",
                    source_ref=ref,
                    next_action="inspect document registry status",
                )
            )
            registries[key] = {"status": "missing", "ref": ref, "entry_count": 0}
            continue
        try:
            record = policy_templates.read_yaml_subset(path)
        except Exception as exc:
            status = "degraded"
            diagnostics.append(
                diagnostic(
                    f"registry_{key}_invalid",
                    severity="warning",
                    message=f"registry shard could not be parsed: {exc}",
                    source_ref=ref,
                    next_action="run document registry tests",
                )
            )
            registries[key] = {"status": "invalid", "ref": ref, "entry_count": 0}
            continue
        entries = record.get("entries") if isinstance(record, dict) else None
        registries[key] = {
            "status": "available",
            "ref": ref,
            "schema_version": record.get("schema_version"),
            "entry_count": len(entries) if isinstance(entries, list) else 0,
        }
    return {
        "status": status,
        "registries": registries,
        "work_order_count": registries.get("work_orders", {}).get("entry_count", 0),
        "capability_count": registries.get("capabilities", {}).get("entry_count", 0),
        "mount_set_count": registries.get("mount_sets", {}).get("entry_count", 0),
    }


def integration_health(project_root: Path, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    tools = mcp_adapter.list_tools()
    tool_names = [str(tool.get("name")) for tool in tools if isinstance(tool, dict)]
    hook_config_ref = ".codex/hooks.json"
    hook_script_ref = ".codex/hooks/jikuo_user_prompt_submit.py"
    hook_config_present = (project_root / hook_config_ref).is_file()
    hook_script_present = (project_root / hook_script_ref).is_file()
    if not hook_config_present or not hook_script_present:
        diagnostics.append(
            diagnostic(
                "codex_hook_files_missing",
                severity="info",
                message="Codex hook proof files are not both present",
                source_ref=hook_config_ref,
                next_action="review Codex hook proof before claiming mounted execution",
            )
        )
    sampling_exposed = "jikuo.probe_sampling_semantic_intent" in tool_names
    return {
        "status": "available",
        "mcp": {
            "tool_count": len(tool_names),
            "sampling_probe_exposed": sampling_exposed,
            "policy_management_tools_exposed": any(
                name == "jikuo.get_policy_management_status" for name in tool_names
            ),
            "strict_mounted_proof": "not_proven_by_tool_inventory",
        },
        "codex_hook": {
            "config_present": hook_config_present,
            "script_present": hook_script_present,
            "strict_mounted_proof": "requires_gui_smoke_card",
        },
        "semantic_provider": {
            "host_time_provider": "not_automatic",
            "mcp_sampling": "probe_only",
        },
    }


def core_project_context_summary(project_root: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    path = project_root / PROJECT_CONTEXT_REF
    if not path.is_file():
        return {
            "status": "missing",
            "ref": PROJECT_CONTEXT_REF,
            "required": True,
        }, diagnostic(
            "project_context_missing",
            severity="error",
            message="core project context is missing",
            source_ref=PROJECT_CONTEXT_REF,
            next_action="open a JIKUO project root or initialize project context",
        )
    try:
        context = policy_templates.read_yaml_subset(path)
    except Exception as exc:
        return {
            "status": "invalid",
            "ref": PROJECT_CONTEXT_REF,
            "required": True,
        }, diagnostic(
            "project_context_invalid",
            severity="error",
            message=f"core project context could not be parsed: {exc}",
            source_ref=PROJECT_CONTEXT_REF,
            next_action="repair .jikuo/project_context.yaml before opening Studio",
        )
    return {
        "status": "available",
        "ref": PROJECT_CONTEXT_REF,
        "required": True,
        "key_count": len(context.keys()) if isinstance(context, dict) else 0,
    }, None


def aggregate_status(
    *,
    project_context: dict[str, Any],
    diagnostics: list[dict[str, Any]],
) -> str:
    if project_context.get("status") != "available":
        return "unavailable"
    if diagnostics:
        return "degraded"
    return "available"


def build_global_status(*, project_root: Path | None = None) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    diagnostics: list[dict[str, Any]] = []
    project_context, context_diagnostic = core_project_context_summary(resolved_root)
    if context_diagnostic:
        diagnostics.append(context_diagnostic)

    activation_section = safe_section(
        "activation",
        lambda: dict(zip(("summary", "decisions"), activation_summary(resolved_root, diagnostics))),
        diagnostics=diagnostics,
    )
    activation = activation_section.get("summary", activation_section)
    activation_decisions = activation_section.get("decisions", [])
    configuration_section = safe_section(
        "configuration",
        lambda: dict(zip(("summary", "decisions"), configuration_summary(resolved_root, diagnostics))),
        diagnostics=diagnostics,
    )
    configuration = configuration_section.get("summary", configuration_section)
    configuration_decisions = configuration_section.get("decisions", [])
    policy_section = safe_section(
        "policy_management",
        lambda: dict(
            zip(
                ("summary", "decisions"),
                policy_management_summary(resolved_root, diagnostics),
            )
        ),
        diagnostics=diagnostics,
    )
    policy_summary = policy_section.get("summary", policy_section)
    policy_decisions = policy_section.get("decisions", [])

    pending_user_decisions = [
        *list(activation_decisions or []),
        *list(configuration_decisions or []),
        *list(policy_decisions or []),
    ]
    document_mounts = safe_section(
        "document_mounts",
        lambda: document_mounts_summary(resolved_root, diagnostics),
        diagnostics=diagnostics,
    )
    runtime = safe_section(
        "runtime",
        lambda: runtime_summary(resolved_root, diagnostics),
        diagnostics=diagnostics,
    )
    if isinstance(runtime, dict):
        runtime["semantic_intent_evidence"] = semantic_intent_evidence_overview(
            runtime=runtime,
            activation=activation if isinstance(activation, dict) else {},
        )
    summaries = {
        "runtime": runtime,
        "activation": activation,
        "configuration": configuration,
        "document_mounts": document_mounts,
        "artifact_assurance": artifact_assurance.build_summary_from_document_mounts(
            project_root=resolved_root,
            document_mounts=document_mounts,
        ),
        "policy_management": policy_summary,
        "registry": safe_section(
            "registry",
            lambda: registry_summary(resolved_root, diagnostics),
            diagnostics=diagnostics,
        ),
        "integrations": safe_section(
            "integrations",
            lambda: integration_health(resolved_root, diagnostics),
            diagnostics=diagnostics,
        ),
        "project_context": project_context,
    }
    action_registry = studio_actions.build_action_registry(
        project_root=resolved_root,
        summaries=summaries,
    )
    available_actions = action_registry.get("actions") or []
    panel_registry = studio_panels.build_panel_registry(
        project_root=resolved_root,
        summaries=summaries,
        actions=available_actions,
    )
    runtime_links = ((summaries.get("runtime") or {}).get("card_links") or {})
    return {
        "schema": GLOBAL_STATUS_SCHEMA,
        "schema_version": GLOBAL_STATUS_SCHEMA,
        "status": aggregate_status(
            project_context=project_context,
            diagnostics=diagnostics,
        ),
        "project_root": str(resolved_root),
        "generated_at_utc": utc_now_iso(),
        "summaries": summaries,
        "panel_registry": panel_registry,
        "action_registry": action_registry,
        "panels": panel_registry.get("panels") or [],
        "pending_user_decisions": pending_user_decisions[:16],
        "available_actions": available_actions,
        "diagnostics": diagnostics,
        "card_links": runtime_links,
        "source_refs": [
            source_ref(PROJECT_CONTEXT_REF),
            *(source_ref(ref) for ref in REGISTRY_REFS.values()),
            source_ref(runtime_visibility.STATE_SUMMARY_REF),
            source_ref(activation_settings.SETTINGS_REF),
            source_ref("src/jikuo/studio/global_status.py"),
            source_ref("src/jikuo/studio/artifact_assurance.py"),
            source_ref("src/jikuo/studio/panels.py"),
            source_ref("src/jikuo/studio/actions.py"),
        ],
        "read_model_limitations": [
            "integration health is a local projection and does not prove GUI mounted behavior",
            "runtime history is based on current runtime visibility snapshots, not DATA-01 event ledger",
            "panels and actions are descriptors only; execution remains behind existing no-write and guarded apply surfaces",
            "policy-management summary does not activate user projects or mutate starter manifests",
            "document-mount summary is read-only and does not decide which documents are canonical for the user",
            "artifact-assurance summary lists configured required reads/writes but needs per-slice evidence before it can prove read/write completion",
        ],
        "privacy": {
            "raw_prompt_stored": False,
            "transcript_stored": False,
            "raw_prompt_or_transcript_included": False,
        },
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_write_project_state",
            "does_not_mutate_policies",
            "does_not_update_starter_manifests",
            "does_not_activate_user_project_policies",
            "does_not_create_runtime_cards",
            "does_not_call_llm_provider",
        ],
    }


def format_markdown(report: dict[str, Any]) -> str:
    summaries = report.get("summaries") or {}
    policy_counts = ((summaries.get("policy_management") or {}).get("summary_counts") or {})
    activation = summaries.get("activation") or {}
    document_mounts = summaries.get("document_mounts") or {}
    configuration_terms = {
        item.get("term_id"): item
        for item in (document_mounts.get("configuration_terms") or [])
        if isinstance(item, dict)
    }
    document_rules_term = configuration_terms.get("document_rules") or {}
    completion_checks_term = configuration_terms.get("completion_checks") or {}
    rule_sources_term = configuration_terms.get("rule_sources") or {}
    document_rules_label = document_rules_term.get("user_label") or "Document rules"
    completion_checks_label = completion_checks_term.get("user_label") or "Completion checks"
    rule_sources_label = rule_sources_term.get("user_label") or "Configuration sources and guidance"
    runtime = summaries.get("runtime") or {}
    assurance = summaries.get("artifact_assurance") or {}
    assurance_write = assurance.get("write_assurance") or {}
    assurance_gap = assurance.get("gap_report") or {}
    integrations = summaries.get("integrations") or {}
    mcp = integrations.get("mcp") or {}
    lines = [
        "# JIKUO Studio Global Status",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Schema: `{report.get('schema')}`",
        f"- Project root: `{report.get('project_root')}`",
        f"- Writes performed: `{str(report.get('writes_performed')).lower()}`",
        "",
        "## Overview",
        "",
        f"- Activation: `{activation.get('source_status') or activation.get('status')}` / trigger_mode=`{activation.get('desired_trigger_mode')}` / strict_mount=`{activation.get('strict_mount_status')}`",
        f"- Runtime: `{runtime.get('status')}` / triggered_policies=`{(runtime.get('counts') or {}).get('triggered_policy_count', 0)}` / missing_evidence=`{(runtime.get('counts') or {}).get('missing_evidence_count', 0)}`",
        f"- {document_rules_label}: `{document_mounts.get('status')}` / configured roles=`{document_mounts.get('role_count', 0)}` / {completion_checks_label.lower()}=`{document_mounts.get('checked_document_count', 0)}`",
        f"- Artifact assurance: `{assurance.get('status')}` / required_writes=`{assurance_write.get('required_write_count', 0)}` / gaps=`{assurance_gap.get('gap_count', 0)}`",
        f"- Policies: active=`{policy_counts.get('active_policy_count', 0)}` / templates=`{policy_counts.get('package_template_count', 0)}` / starter_refs=`{policy_counts.get('starter_template_ref_count', 0)}`",
        f"- MCP tools: `{mcp.get('tool_count', 0)}` / sampling_probe=`{str(mcp.get('sampling_probe_exposed')).lower()}`",
        f"- Pending decisions: `{len(report.get('pending_user_decisions') or [])}`",
        f"- Diagnostics: `{len(report.get('diagnostics') or [])}`",
        "",
        f"## {document_rules_label}",
        "",
        f"- {rule_sources_label}: editable=`{len(document_mounts.get('editable_configuration_sources') or [])}` / guidance=`{len(document_mounts.get('governance_guidance_sources') or [])}`",
        f"- Missing required roles: `{document_mounts.get('missing_required_role_count', 0)}`",
        f"- Rule sets: `{document_mounts.get('mount_set_count', 0)}` / Studio status=`{document_mounts.get('studio_mount_set_status')}`",
        "",
        "## Artifact Assurance",
        "",
        f"- Status: `{assurance.get('status')}`",
        f"- Required reads: `{(assurance.get('read_assurance') or {}).get('required_read_count', 0)}`",
        f"- Required writes: `{assurance_write.get('required_write_count', 0)}`",
        f"- Gap count: `{assurance_gap.get('gap_count', 0)}`",
        f"- Guarantee: `{assurance.get('guarantee')}`",
        "",
        "## Panels",
        "",
    ]
    for panel in report.get("panels") or []:
        lines.append(
            f"- `{panel.get('panel_id')}` / `{panel.get('status')}` / provider=`{panel.get('provider_ref')}`"
        )
    lines.extend(
        [
            "",
            "## Available Actions",
            "",
        ]
    )
    for action in report.get("available_actions") or []:
        lines.append(
            f"- `{action.get('action_id')}` / `{action.get('write_mode')}` / {action.get('title')}"
        )
    if report.get("diagnostics"):
        lines.extend(["", "## Diagnostics", ""])
        for item in report["diagnostics"]:
            lines.append(
                f"- `{item.get('severity')}` / `{item.get('code')}`: {item.get('message')}"
            )
    if report.get("card_links"):
        lines.extend(["", "## Runtime Links", ""])
        for key, value in report["card_links"].items():
            if value:
                lines.append(f"- {key}: {value}")
    lines.extend(["", "## Non-Effects", ""])
    lines.extend(f"- {item}" for item in report.get("non_effects") or [])
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect JIKUO Studio global status.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status")
    status.add_argument("--project-root", type=Path, default=None)
    status.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "status":
        report = build_global_status(project_root=args.project_root)
        if args.format == "markdown":
            print(format_markdown(report), end="")
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("status") in {"available", "degraded"} else 2
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
