"""Document/artifact read-write assurance projections for Studio.

This module compares expected document/artifact interactions against observed
evidence. It intentionally does not read files, inspect git, or write runtime
state; callers supply the required, planned, and actual facts they want to
compare.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARTIFACT_ASSURANCE_SCHEMA = "jikuo.studio.artifact_assurance.v0"
COMPLETION_CHECK_CANDIDATE = "completion_check_candidate"
APPLICABLE_STATUSES = {"applicable", "required"}
NOT_APPLICABLE_STATUSES = {"not_applicable", "unchanged_ok", "deferred"}


def normalize_applicability_status(value: Any, *, default: str) -> str:
    text = str(value or "").strip().lower()
    if text in APPLICABLE_STATUSES | NOT_APPLICABLE_STATUSES | {"not_evaluated"}:
        return text
    return default


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_path_ref(project_root: Path, value: Any) -> tuple[str | None, dict[str, Any] | None]:
    raw = str(value or "").strip()
    if not raw:
        return None, {"code": "path_ref_empty", "message": "path ref is empty"}
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    try:
        relative = candidate.resolve().relative_to(project_root.resolve())
    except Exception:
        return None, {
            "code": "path_outside_project_root",
            "message": "path ref must resolve inside project root",
            "path": raw,
        }
    return relative.as_posix(), None


def _coerce_artifact_items(
    *,
    project_root: Path,
    values: list[Any] | None,
    set_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, value in enumerate(values or []):
        record = value if isinstance(value, dict) else {"path": value}
        path_ref = (
            record.get("path")
            or record.get("path_ref")
            or record.get("ref")
            or record.get("target")
        )
        normalized, error = normalize_path_ref(project_root, path_ref)
        if error:
            invalid.append(
                {
                    "set": set_name,
                    "index": index,
                    **error,
                }
            )
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        obligation_level = (
            record.get("obligation_level")
            or record.get("write_obligation")
            or (
                COMPLETION_CHECK_CANDIDATE
                if record.get("role") == "completion_check"
                else "required"
            )
        )
        default_applicability = (
            "not_evaluated"
            if obligation_level == COMPLETION_CHECK_CANDIDATE
            else "applicable"
        )
        item = {
            "path": normalized,
            "reason": record.get("reason")
            or record.get("required_when")
            or record.get("update_required_when")
            or record.get("purpose"),
            "role": record.get("role"),
            "source_ref": record.get("source_ref"),
            "evidence_ref": record.get("evidence_ref"),
            "plan_ref": record.get("plan_ref"),
            "fingerprint": record.get("fingerprint"),
            "obligation_level": obligation_level,
            "applicability_status": normalize_applicability_status(
                record.get("applicability_status")
                or record.get("applicability")
                or record.get("status"),
                default=default_applicability,
            ),
            "applicability_reason": record.get("applicability_reason")
            or record.get("decision_reason"),
        }
        for metadata_key in (
            "source_kind",
            "evidence_kind",
            "evidence_status",
            "attribution_status",
            "operation",
            "previous_path",
            "git_status",
        ):
            if record.get(metadata_key) is not None:
                item[metadata_key] = record.get(metadata_key)
        items.append(item)
    return items, invalid


def _by_path(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("path")): item for item in items if item.get("path")}


def _applicable_required_writes(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for item in items:
        if item.get("obligation_level") == COMPLETION_CHECK_CANDIDATE:
            if item.get("applicability_status") in APPLICABLE_STATUSES:
                output.append(item)
            continue
        if item.get("applicability_status") not in NOT_APPLICABLE_STATUSES:
            output.append(item)
    return output


def _missing_items(
    expected: dict[str, dict[str, Any]],
    observed: dict[str, dict[str, Any]],
    *,
    gap_type: str,
) -> list[dict[str, Any]]:
    return [
        {
            "gap_type": gap_type,
            "path": path_ref,
            "expected": expected_item,
            "observed": None,
        }
        for path_ref, expected_item in sorted(expected.items())
        if path_ref not in observed
    ]


def _unexpected_items(
    expected: dict[str, dict[str, Any]],
    observed: dict[str, dict[str, Any]],
    *,
    gap_type: str,
) -> list[dict[str, Any]]:
    return [
        {
            "gap_type": gap_type,
            "path": path_ref,
            "expected": None,
            "observed": observed_item,
        }
        for path_ref, observed_item in sorted(observed.items())
        if path_ref not in expected
    ]


def build_document_artifact_assurance_report(
    *,
    project_root: Path,
    required_reads: list[Any] | None = None,
    read_evidence: list[Any] | None = None,
    required_writes: list[Any] | None = None,
    planned_writes: list[Any] | None = None,
    actual_writes: list[Any] | None = None,
) -> dict[str, Any]:
    resolved_root = project_root.resolve()
    required_read_items, required_read_invalid = _coerce_artifact_items(
        project_root=resolved_root,
        values=required_reads,
        set_name="required_reads",
    )
    read_evidence_items, read_evidence_invalid = _coerce_artifact_items(
        project_root=resolved_root,
        values=read_evidence,
        set_name="read_evidence",
    )
    required_write_items, required_write_invalid = _coerce_artifact_items(
        project_root=resolved_root,
        values=required_writes,
        set_name="required_writes",
    )
    planned_write_items, planned_write_invalid = _coerce_artifact_items(
        project_root=resolved_root,
        values=planned_writes,
        set_name="planned_writes",
    )
    actual_write_items, actual_write_invalid = _coerce_artifact_items(
        project_root=resolved_root,
        values=actual_writes,
        set_name="actual_writes",
    )
    invalid_refs = [
        *required_read_invalid,
        *read_evidence_invalid,
        *required_write_invalid,
        *planned_write_invalid,
        *actual_write_invalid,
    ]

    required_read_by_path = _by_path(required_read_items)
    read_evidence_by_path = _by_path(read_evidence_items)
    applicable_required_write_items = _applicable_required_writes(required_write_items)
    applicable_required_write_by_path = _by_path(applicable_required_write_items)
    planned_write_by_path = _by_path(planned_write_items)
    actual_write_by_path = _by_path(actual_write_items)
    completion_check_candidates = [
        item
        for item in required_write_items
        if item.get("obligation_level") == COMPLETION_CHECK_CANDIDATE
    ]
    completion_check_not_evaluated = [
        item
        for item in completion_check_candidates
        if item.get("applicability_status") == "not_evaluated"
    ]
    completion_check_not_applicable = [
        item
        for item in completion_check_candidates
        if item.get("applicability_status") in NOT_APPLICABLE_STATUSES
    ]

    read_gaps: list[dict[str, Any]] = []
    if read_evidence is not None:
        read_gaps.extend(
            _missing_items(
                required_read_by_path,
                read_evidence_by_path,
                gap_type="required_read_not_observed",
            )
        )

    write_gaps: list[dict[str, Any]] = []
    if planned_writes is not None:
        write_gaps.extend(
            _missing_items(
                applicable_required_write_by_path,
                planned_write_by_path,
                gap_type="required_write_not_planned",
            )
        )
    if actual_writes is not None:
        write_gaps.extend(
            _missing_items(
                applicable_required_write_by_path,
                actual_write_by_path,
                gap_type="required_write_not_observed",
            )
        )
    if planned_writes is not None and actual_writes is not None:
        write_gaps.extend(
            _missing_items(
                planned_write_by_path,
                actual_write_by_path,
                gap_type="planned_write_not_observed",
            )
        )
        write_gaps.extend(
            _unexpected_items(
                planned_write_by_path,
                actual_write_by_path,
                gap_type="actual_write_not_planned",
            )
        )

    evidence_supplied = read_evidence is not None or planned_writes is not None or actual_writes is not None
    gap_count = len(read_gaps) + len(write_gaps)
    read_status = (
        "not_evaluated"
        if required_read_items and read_evidence is None
        else "review"
        if read_gaps
        else "ok"
    )
    write_status = (
        "review"
        if write_gaps or completion_check_not_evaluated
        else "not_evaluated"
        if required_writes is not None and not evidence_supplied
        else "ok"
    )
    completion_check_status = (
        "not_evaluated"
        if completion_check_not_evaluated
        else "ok"
        if completion_check_candidates
        else "not_applicable"
    )
    if invalid_refs:
        status = "refused"
    elif not evidence_supplied:
        status = "not_evaluated"
    elif gap_count or read_status == "not_evaluated" or completion_check_not_evaluated:
        status = "review"
    else:
        status = "ok"

    return {
        "schema": ARTIFACT_ASSURANCE_SCHEMA,
        "schema_version": ARTIFACT_ASSURANCE_SCHEMA,
        "status": status,
        "project_root": str(resolved_root),
        "generated_at_utc": utc_now_iso(),
        "guarantee": "evidence_comparison_only",
        "inputs_supplied": {
            "required_reads": required_reads is not None,
            "read_evidence": read_evidence is not None,
            "required_writes": required_writes is not None,
            "planned_writes": planned_writes is not None,
            "actual_writes": actual_writes is not None,
        },
        "read_assurance": {
            "status": read_status,
            "required_read_count": len(required_read_items),
            "read_evidence_count": len(read_evidence_items),
            "required_read_set": required_read_items,
            "read_evidence_set": read_evidence_items,
            "required_not_read": read_gaps,
        },
        "write_assurance": {
            "status": write_status,
            "required_write_count": len(applicable_required_write_items),
            "planned_write_count": len(planned_write_items),
            "actual_write_count": len(actual_write_items),
            "required_write_set": applicable_required_write_items,
            "write_candidate_count": len(completion_check_candidates),
            "write_candidate_set": completion_check_candidates,
            "completion_check_candidate_count": len(completion_check_candidates),
            "completion_check_candidates": completion_check_candidates,
            "completion_check_status": completion_check_status,
            "completion_check_not_evaluated": completion_check_not_evaluated,
            "completion_check_not_applicable": completion_check_not_applicable,
            "planned_write_set": planned_write_items,
            "actual_write_set": actual_write_items,
            "required_not_planned": [
                item for item in write_gaps if item["gap_type"] == "required_write_not_planned"
            ],
            "required_not_written": [
                item for item in write_gaps if item["gap_type"] == "required_write_not_observed"
            ],
            "planned_not_written": [
                item for item in write_gaps if item["gap_type"] == "planned_write_not_observed"
            ],
            "unplanned_written": [
                item for item in write_gaps if item["gap_type"] == "actual_write_not_planned"
            ],
        },
        "gap_report": {
            "status": (
                "ok"
                if gap_count == 0 and not invalid_refs and not completion_check_not_evaluated
                else "review"
            ),
            "gap_count": gap_count,
            "read_gap_count": len(read_gaps),
            "write_gap_count": len(write_gaps),
            "completion_check_not_evaluated_count": len(completion_check_not_evaluated),
            "read_gaps": read_gaps,
            "write_gaps": write_gaps,
            "invalid_refs": invalid_refs,
        },
        "next_actions": next_actions_for(status),
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_read_files_by_itself",
            "does_not_write_files",
            "does_not_inspect_git_by_itself",
            "does_not_prove_model_understanding",
            "does_not_replace_guarded_apply",
        ],
    }


def next_actions_for(status: str) -> list[str]:
    if status == "ok":
        return ["continue; required/planned/actual artifact evidence is aligned"]
    if status == "not_evaluated":
        return [
            "supply read evidence and planned/actual write evidence for a governed slice",
            "use this projection during task_start and completion_review before relying on it for UI",
        ]
    if status == "refused":
        return ["repair artifact path refs before evaluating assurance gaps"]
    return [
        "review completion-check candidates, applicability, and write gaps",
        "update the plan, perform the missing applicable write, or record not-applicable/unchanged evidence",
    ]


def required_writes_from_document_mounts(document_mounts: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "path": item.get("path"),
            "reason": item.get("update_required_when"),
            "source_ref": ".jikuo/project_context.yaml main_document_mounts.checked_before_slice_completion",
            "role": "completion_check",
            "obligation_level": COMPLETION_CHECK_CANDIDATE,
            "applicability_status": "not_evaluated",
            "applicability_reason": (
                "completion-check documents are candidates until this slice "
                "records applicability, unchanged, planned-write, or actual-write evidence"
            ),
        }
        for item in document_mounts.get("checked_before_slice_completion") or []
        if isinstance(item, dict) and item.get("path")
    ]


def required_reads_from_document_mounts(document_mounts: dict[str, Any]) -> list[dict[str, Any]]:
    reads = [
        {
            "path": item,
            "reason": "active mount authority configured for governed work",
            "source_ref": ".jikuo/project_context.yaml main_document_mounts.active_mount_authority",
            "role": "active_mount_authority",
        }
        for item in document_mounts.get("active_mount_authority") or []
    ]
    for item in document_mounts.get("roles") or []:
        if isinstance(item, dict) and item.get("required") and item.get("path"):
            reads.append(
                {
                    "path": item.get("path"),
                    "reason": item.get("note") or "required document role",
                    "source_ref": ".jikuo/project_context.yaml document_roles",
                    "role": item.get("role"),
                }
            )
    return reads


def build_summary_from_document_mounts(
    *,
    project_root: Path,
    document_mounts: dict[str, Any],
) -> dict[str, Any]:
    return build_document_artifact_assurance_report(
        project_root=project_root,
        required_reads=required_reads_from_document_mounts(document_mounts),
        read_evidence=None,
        required_writes=required_writes_from_document_mounts(document_mounts),
        planned_writes=None,
        actual_writes=None,
    )
