"""JIKUO task-session helper.

Dry-run remains the default safe preview path. Write mode is guarded by explicit
command confirmation and approval evidence, refuses overwrites, and deliberately
does not update the project-state latest-session index in this slice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__:
    from . import project_state
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import project_state


TASK_SESSION_SCHEMA = "jikuo.task_session.v0"
START_PLAN_SCHEMA = "jikuo.task_session_start_plan.v0"
STATUS_SCHEMA = "jikuo.task_session_status.v0"
WRITE_PLAN_SCHEMA = "jikuo.task_session_write_plan.v0"
WRITE_RESULT_SCHEMA = "jikuo.task_session_write_result.v0"
INDEX_PLAN_SCHEMA = "jikuo.task_session_index_refresh_plan.v0"
INDEX_RESULT_SCHEMA = "jikuo.task_session_index_refresh_result.v0"
UPDATE_PLAN_SCHEMA = "jikuo.task_session_update_plan.v0"
UPDATE_RESULT_SCHEMA = "jikuo.task_session_update_result.v0"
ALLOWED_OWNER_AGENTS = {"codex", "claude", "other"}
COMPLETION_STATUSES = {
    "not_started",
    "in_progress",
    "blocked",
    "ready_for_review",
    "accepted",
    "superseded",
    "abandoned",
}
TERMINAL_COMPLETION_STATUSES = {"accepted", "superseded", "abandoned"}
DEFAULT_SCENARIO_PACKAGE = "engineering_governance"
DEFAULT_SCENARIO_CHAIN_ID = "engineering_governance.task_session_start"
LATEST_TASK_SESSION_REFS_FIELD = "latest_task_session_refs"
DEFAULT_MAX_INDEX_REFS = 20
TASKSESSION_01_REF = (
    "pkg://jikuo/work_orders/"
    "SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md"
)
TASKSESSION_02_REF = (
    "pkg://jikuo/work_orders/"
    "SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md"
)
TASKSESSION_03_REF = (
    "pkg://jikuo/work_orders/"
    "SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md"
)
TASKSESSION_04_REF = (
    "pkg://jikuo/work_orders/"
    "SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md"
)
TASK_SESSION_SCHEMA_REF = (
    "pkg://jikuo/schemas/task_session.schema.md"
)
TASK_SESSION_APPROVAL_TARGET = "JIKUO task-session file creation"
TASK_SESSION_APPROVAL_EFFECT = "create one compact task-session sidecar record"
TASK_SESSION_APPROVAL_NONEFFECT = "do not capture raw chat transcript"
INDEX_APPROVAL_TARGET = "JIKUO project-state task-session index update"
INDEX_APPROVAL_EFFECT = "update .jikuo/project_state.yaml latest_task_session_refs"
INDEX_APPROVAL_NONEFFECT = "do not create task-session files or capture raw chat transcript"
UPDATE_APPROVAL_NONEFFECT = "do not capture raw chat transcript or judge product output quality"


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug[:48] or "task"


def short_id_for(
    project_root: Path,
    task_title: str,
    owner_agent: str,
    created_at: str | None = None,
) -> str:
    seed = f"{project_root}|{task_title}|{owner_agent}|{created_at or ''}".encode(
        "utf-8"
    )
    return hashlib.sha256(seed).hexdigest()[:8]


def validate_task_title(task_title: str) -> list[str]:
    if not task_title.strip():
        return ["task title is required"]
    return []


def validate_owner_agent(owner_agent: str) -> list[str]:
    if owner_agent not in ALLOWED_OWNER_AGENTS:
        return [f"owner agent must be one of: {', '.join(sorted(ALLOWED_OWNER_AGENTS))}"]
    return []


def build_task_session_record(
    *,
    project_root: Path,
    task_title: str,
    owner_agent: str,
    created_at: str,
    session_id: str,
    lifecycle_status: str = "draft",
    completion_status: str = "not_started",
    approval_phrase: str | None = None,
) -> dict[str, Any]:
    user_decisions = []
    audit_trail = []
    if approval_phrase:
        user_decisions.append(
            {
                "decision_id": "task_session_start_approval",
                "decision_target": TASK_SESSION_APPROVAL_TARGET,
                "decision_effect": TASK_SESSION_APPROVAL_EFFECT,
                "decision_noneffect": TASK_SESSION_APPROVAL_NONEFFECT,
                "exact_user_phrase": approval_phrase,
                "recorded_at": created_at,
                "surface": "desktop_agent_or_cli_bridge",
            }
        )
        audit_trail.append(
            {
                "action": "task_session_started",
                "actor": owner_agent,
                "recorded_at": created_at,
                "effect": TASK_SESSION_APPROVAL_EFFECT,
            }
        )

    return {
        "schema": TASK_SESSION_SCHEMA,
        "session": {
            "session_id": session_id,
            "task_title": task_title,
            "owner_agent": owner_agent,
            "created_at": created_at,
            "updated_at": created_at,
            "lifecycle_status": lifecycle_status,
        },
        "scenario": {
            "scenario_chain_id": DEFAULT_SCENARIO_CHAIN_ID,
            "scenario_package": DEFAULT_SCENARIO_PACKAGE,
        },
        "changed_surfaces": [],
        "rule_results": [],
        "document_mounts": [],
        "evidence_snapshots": [],
        "verification": [],
        "user_decisions": user_decisions,
        "completion": {
            "status": completion_status,
        },
        "handoff": {
            "summary": None,
        },
        "audit_trail": audit_trail,
        "supersession": {
            "supersedes": [],
            "superseded_by": None,
        },
        "capture_policy": {
            "raw_chat_transcript": "disallowed",
            "exact_user_phrase": "decision_only_with_target_and_effect",
            "product_output_quality_judgement": "out_of_scope",
        },
    }


def build_start_plan(
    *,
    project_root: Path | None = None,
    task_title: str,
    owner_agent: str = "codex",
    created_at: str | None = None,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    created_at_value = created_at or utc_now_iso()
    timestamp = (
        created_at_value.replace("-", "")
        .replace(":", "")
        .replace("+0000", "Z")
        .replace("+00:00", "Z")
    )
    timestamp = re.sub(r"[^0-9TZ]", "", timestamp)[:16] or utc_now_compact()
    title_errors = validate_task_title(task_title)
    owner_errors = validate_owner_agent(owner_agent)
    state_report = project_state.build_bootstrap_report(
        project_root=resolved_root,
        command="status",
        include_would_create=False,
    )
    warnings = [*title_errors, *owner_errors]
    if state_report["state_status"] != "initialized":
        warnings.append("project state must be initialized before task-session planning")

    task_slug = slugify(task_title)
    short_id = short_id_for(resolved_root, task_title, owner_agent, created_at_value)
    session_id = f"task_{timestamp}_{task_slug}_{short_id}"
    session_file = resolved_root / ".jikuo" / "task_sessions" / f"{session_id}.yaml"
    can_start = not warnings

    return {
        "schema": START_PLAN_SCHEMA,
        "report_only": True,
        "command": "start",
        "project_root": str(resolved_root),
        "project_state_status": state_report["state_status"],
        "task_sessions_root": str(resolved_root / ".jikuo" / "task_sessions"),
        "target_session_file": str(session_file),
        "session_id": session_id,
        "write_allowed_by_command": False,
        "can_start": can_start,
        "would_create": (
            build_task_session_record(
                project_root=resolved_root,
                task_title=task_title,
                owner_agent=owner_agent,
                created_at=created_at_value,
                session_id=session_id,
            )
            if can_start
            else None
        ),
        "source_refs": [
            TASK_SESSION_SCHEMA_REF,
            TASKSESSION_01_REF,
            ".jikuo/project_state.yaml",
            project_state.REGISTRY_REF,
        ],
        "warnings": warnings,
        "next_actions": [
            "review task-session start plan before approving any write-mode work order"
        ]
        if can_start
        else ["resolve warnings before task-session planning continues"],
    }


def read_project_state_field(project_state_file: Path, field_name: str) -> str | None:
    try:
        text = project_state_file.read_text(encoding="utf-8")
    except OSError:
        return None
    prefix = f"{field_name}:"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip().strip("'\"") or None
    return None


def read_project_state_path_field(
    project_state_file: Path,
    field_name: str,
    *,
    project_root: Path,
) -> Path | None:
    return project_state.resolve_stored_project_path(
        read_project_state_field(project_state_file, field_name),
        project_root=project_root,
    )


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return project_state.quote_yaml(str(value))


def render_yaml_lines(value: Any, indent: int = 0) -> list[str]:
    pad = " " * indent
    if isinstance(value, dict):
        if not value:
            return [f"{pad}{{}}"]
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, dict):
                if item:
                    lines.append(f"{pad}{key}:")
                    lines.extend(render_yaml_lines(item, indent + 2))
                else:
                    lines.append(f"{pad}{key}: {{}}")
            elif isinstance(item, list):
                if item:
                    lines.append(f"{pad}{key}:")
                    lines.extend(render_yaml_lines(item, indent + 2))
                else:
                    lines.append(f"{pad}{key}: []")
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(item)}")
        return lines
    if isinstance(value, list):
        if not value:
            return [f"{pad}[]"]
        lines = []
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{pad}-")
                lines.extend(render_yaml_lines(item, indent + 2))
            elif isinstance(item, list):
                lines.append(f"{pad}-")
                lines.extend(render_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{pad}- {yaml_scalar(item)}")
        return lines
    return [f"{pad}{yaml_scalar(value)}"]


def render_task_session_yaml(record: dict[str, Any]) -> str:
    return "\n".join(render_yaml_lines(record)) + "\n"


def session_source_refs() -> list[str]:
    return [
        TASK_SESSION_SCHEMA_REF,
        TASKSESSION_01_REF,
        TASKSESSION_02_REF,
        ".jikuo/project_state.yaml",
        project_state.REGISTRY_REF,
    ]


def index_source_refs() -> list[str]:
    return [
        TASK_SESSION_SCHEMA_REF,
        TASKSESSION_02_REF,
        TASKSESSION_03_REF,
        ".jikuo/project_state.yaml",
        project_state.REGISTRY_REF,
    ]


def update_source_refs() -> list[str]:
    return [
        TASK_SESSION_SCHEMA_REF,
        TASKSESSION_03_REF,
        TASKSESSION_04_REF,
        ".jikuo/project_state.yaml",
        project_state.REGISTRY_REF,
    ]


def write_next_actions_for(write_performed: bool) -> list[str]:
    if write_performed:
        return [
            "use the task-session file as durable process memory for this governed task",
            "plan project-state latest_task_session_refs update in a later accepted work order",
        ]
    return ["resolve refusal reasons before retrying task-session write mode"]


def build_write_plan(
    *,
    project_root: Path | None = None,
    task_title: str,
    owner_agent: str = "codex",
    created_at: str | None = None,
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> dict[str, Any]:
    start_plan = build_start_plan(
        project_root=project_root,
        task_title=task_title,
        owner_agent=owner_agent,
        created_at=created_at,
    )
    resolved_root = Path(start_plan["project_root"])
    project_state_file = resolved_root / ".jikuo" / "project_state.yaml"
    sessions_root = resolved_root / ".jikuo" / "task_sessions"
    target_file = Path(start_plan["target_session_file"])
    refusal_reasons: list[str] = []
    warnings = [
        warning
        for warning in start_plan["warnings"]
        if warning != "project state must be initialized before task-session planning"
    ]

    if start_plan["project_state_status"] != "initialized":
        refusal_reasons.append("project_state_not_initialized")

    project_state_root = read_project_state_path_field(
        project_state_file,
        "project_root",
        project_root=resolved_root,
    )
    if project_state_root is not None and Path(project_state_root) != resolved_root:
        refusal_reasons.append("project_root_mismatch")
    elif project_state_root is None and start_plan["project_state_status"] == "initialized":
        refusal_reasons.append("project_root_missing_in_project_state")

    if sessions_root.exists() and not sessions_root.is_dir():
        refusal_reasons.append("task_sessions_path_conflict")

    if target_file.exists():
        refusal_reasons.append("session_id_collision")

    if not confirmed:
        refusal_reasons.append("missing_confirmation_flag")

    if not approval_phrase:
        refusal_reasons.append("approval_evidence_missing")

    if validate_task_title(task_title):
        refusal_reasons.append("empty_task_title")

    if validate_owner_agent(owner_agent):
        refusal_reasons.append("invalid_owner_agent")

    registry_path = resolved_root / project_state.REGISTRY_REF
    if not registry_path.exists():
        refusal_reasons.append("required_registry_ref_missing")

    try:
        target_file.resolve().relative_to(sessions_root.resolve())
    except ValueError:
        refusal_reasons.append("target_path_escape")

    can_write = not refusal_reasons
    created_at_value = start_plan["would_create"]["session"]["created_at"] if start_plan["would_create"] else (created_at or utc_now_iso())
    would_write = (
        build_task_session_record(
            project_root=resolved_root,
            task_title=task_title,
            owner_agent=owner_agent,
            created_at=created_at_value,
            session_id=start_plan["session_id"],
            lifecycle_status="started",
            completion_status="in_progress",
            approval_phrase=approval_phrase,
        )
        if can_write
        else None
    )

    return {
        "schema": WRITE_PLAN_SCHEMA,
        "report_only": False,
        "operation": "task_session_start_write",
        "project_root": str(resolved_root),
        "project_state_path": str(project_state_file),
        "project_state_status": start_plan["project_state_status"],
        "task_sessions_root": str(sessions_root),
        "session_id": start_plan["session_id"],
        "session_path": str(target_file),
        "task_title": task_title,
        "owner_agent": owner_agent,
        "record_schema": TASK_SESSION_SCHEMA,
        "approval_required": True,
        "technical_confirmation_required": True,
        "command_confirmed": confirmed,
        "approval_phrase_present": bool(approval_phrase),
        "would_create_directory": not sessions_root.exists(),
        "would_create_file": can_write,
        "would_update_project_state_index": False,
        "no_overwrite": True,
        "can_write": can_write,
        "would_write": would_write,
        "source_refs": session_source_refs(),
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": TASK_SESSION_APPROVAL_TARGET,
            "decision_effect": TASK_SESSION_APPROVAL_EFFECT,
            "decision_noneffect": TASK_SESSION_APPROVAL_NONEFFECT,
            "source_plan_schema": START_PLAN_SCHEMA,
        }
        if approval_phrase
        else None,
        "refusal_reasons": refusal_reasons,
        "warnings": warnings,
    }


def build_write_failure_result(
    *,
    plan: dict[str, Any],
    status: str,
    error: str | None = None,
    cleanup_status: str = "not_needed",
) -> dict[str, Any]:
    return {
        "schema": WRITE_RESULT_SCHEMA,
        "operation": "task_session_start_write",
        "status": status,
        "write_performed": False,
        "project_root": plan["project_root"],
        "task_sessions_root": plan["task_sessions_root"],
        "session_id": plan["session_id"],
        "session_path": plan["session_path"],
        "created_directory": False,
        "created_file": False,
        "updated_project_state_index": False,
        "overwritten_paths": [],
        "approval_record": plan["approval_record"],
        "source_refs": plan["source_refs"],
        "verification": {
            "read_back": False,
            "schema_ok": False,
            "session_id_ok": False,
        },
        "refusal_reasons": plan["refusal_reasons"],
        "warnings": plan["warnings"],
        "error": error,
        "cleanup_status": cleanup_status,
        "next_actions": write_next_actions_for(write_performed=False),
    }


def read_persisted_session_summary(path: Path) -> dict[str, Any]:
    schema = project_state.read_top_level_schema(path)
    summary: dict[str, Any] = {"schema": schema}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        summary["read_error"] = str(exc)
        return summary

    for raw_line in lines:
        line = raw_line.strip()
        for key in (
            "session_id",
            "task_title",
            "owner_agent",
            "created_at",
            "lifecycle_status",
        ):
            prefix = f"{key}:"
            if line.startswith(prefix) and key not in summary:
                summary[key] = line.split(":", 1)[1].strip().strip("'\"")
    return summary


def task_session_ref_from_summary(
    *,
    summary: dict[str, Any],
    session_path: Path,
    project_root: Path,
) -> dict[str, Any]:
    try:
        relative_path = session_path.resolve().relative_to(project_root.resolve())
    except ValueError:
        relative_path = session_path
    return {
        "session_id": summary.get("session_id"),
        "path": str(relative_path).replace("\\", "/"),
        "task_title": summary.get("task_title"),
        "owner_agent": summary.get("owner_agent"),
        "created_at": summary.get("created_at"),
        "lifecycle_status": summary.get("lifecycle_status"),
    }


def normalize_session_ref(ref: dict[str, Any]) -> dict[str, Any]:
    return {
        "session_id": ref.get("session_id"),
        "path": ref.get("path"),
        "task_title": ref.get("task_title"),
        "owner_agent": ref.get("owner_agent"),
        "created_at": ref.get("created_at"),
        "lifecycle_status": ref.get("lifecycle_status"),
    }


def parse_latest_task_session_refs(
    project_state_text: str,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    lines = project_state_text.splitlines()
    warnings: list[str] = []
    refusal_reasons: list[str] = []
    field_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip().startswith(f"{LATEST_TASK_SESSION_REFS_FIELD}:"):
            field_index = index
            break

    if field_index is None:
        return [], warnings, ["latest_task_session_refs_missing"]

    first_line = lines[field_index].strip()
    inline_value = first_line.split(":", 1)[1].strip()
    if inline_value == "[]":
        return [], warnings, []
    if inline_value:
        return [], warnings, ["latest_task_session_refs_unsupported_shape"]

    refs: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in lines[field_index + 1 :]:
        if raw_line and not raw_line.startswith((" ", "\t")) and ":" in raw_line:
            break
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped == "-":
            if current is not None:
                refs.append(current)
            current = {}
            continue
        if stripped.startswith("- "):
            if current is not None:
                refs.append(current)
            current = {}
            remainder = stripped[2:].strip()
            if remainder:
                if ":" not in remainder:
                    return [], warnings, ["latest_task_session_refs_unsupported_shape"]
                key, value = remainder.split(":", 1)
                current[key.strip()] = value.strip().strip("'\"") or None
            continue
        if ":" in stripped and current is not None:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip().strip("'\"") or None
            continue
        return [], warnings, ["latest_task_session_refs_unsupported_shape"]

    if current is not None:
        refs.append(current)

    normalized = [normalize_session_ref(ref) for ref in refs]
    if any(not ref.get("session_id") for ref in normalized):
        refusal_reasons.append("latest_task_session_refs_missing_session_id")
    return normalized, warnings, refusal_reasons


def render_latest_task_session_refs(refs: list[dict[str, Any]]) -> list[str]:
    if not refs:
        return [f"{LATEST_TASK_SESSION_REFS_FIELD}: []"]
    return render_yaml_lines({LATEST_TASK_SESSION_REFS_FIELD: refs})


def replace_latest_task_session_refs(
    project_state_text: str,
    refs: list[dict[str, Any]],
) -> str:
    lines = project_state_text.splitlines()
    field_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip().startswith(f"{LATEST_TASK_SESSION_REFS_FIELD}:"):
            field_index = index
            break
    if field_index is None:
        raise ValueError("latest_task_session_refs field is missing")

    end_index = field_index + 1
    while end_index < len(lines):
        line = lines[end_index]
        if line and not line.startswith((" ", "\t")) and ":" in line:
            break
        end_index += 1

    new_lines = [
        *lines[:field_index],
        *render_latest_task_session_refs(refs),
        *lines[end_index:],
    ]
    return "\n".join(new_lines) + "\n"


def discover_task_session_refs(
    *,
    project_root: Path,
    sessions_root: Path,
    max_refs: int = DEFAULT_MAX_INDEX_REFS,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    warnings: list[str] = []
    refusal_reasons: list[str] = []

    if not sessions_root.exists():
        return [], warnings, refusal_reasons
    if not sessions_root.is_dir():
        return [], warnings, ["task_sessions_path_conflict"]

    refs: list[dict[str, Any]] = []
    seen_ids: dict[str, str] = {}
    for path in sorted(sessions_root.iterdir()):
        if path.is_dir():
            warnings.append(f"ignored task-session subdirectory: {path.name}")
            continue
        if path.suffix.lower() not in {".yaml", ".yml"}:
            warnings.append(f"ignored non-YAML task-session file: {path.name}")
            continue
        try:
            path.resolve().relative_to(sessions_root.resolve())
        except ValueError:
            refusal_reasons.append("session_path_escape")
            continue

        summary = read_persisted_session_summary(path)
        if summary.get("schema") != TASK_SESSION_SCHEMA:
            refusal_reasons.append("unsupported_task_session_schema")
            continue
        session_id = summary.get("session_id")
        if not session_id:
            refusal_reasons.append("task_session_missing_session_id")
            continue
        if session_id in seen_ids:
            refusal_reasons.append("duplicate_session_id")
            continue
        seen_ids[session_id] = str(path)
        if not summary.get("created_at"):
            warnings.append(f"task-session missing created_at: {path.name}")
        refs.append(
            task_session_ref_from_summary(
                summary=summary,
                session_path=path,
                project_root=project_root,
            )
        )

    refs.sort(key=lambda ref: ref.get("path") or "")
    refs.sort(key=lambda ref: ref.get("created_at") or "", reverse=True)
    return refs[:max_refs], warnings, refusal_reasons


def refs_equal(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> bool:
    return [normalize_session_ref(ref) for ref in left] == [
        normalize_session_ref(ref) for ref in right
    ]


def index_next_actions_for(status: str) -> list[str]:
    if status == "updated":
        return ["use latest_task_session_refs as project-level task-session entry points"]
    if status == "no_change":
        return ["no project-state index update is needed"]
    return ["resolve refusal reasons before retrying task-session index refresh"]


def build_index_refresh_plan(
    *,
    project_root: Path | None = None,
    confirmed: bool = False,
    approval_phrase: str | None = None,
    require_write_guards: bool = False,
    max_refs: int = DEFAULT_MAX_INDEX_REFS,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    state_report = project_state.build_bootstrap_report(
        project_root=resolved_root,
        command="status",
        include_would_create=False,
    )
    project_state_path = resolved_root / ".jikuo" / "project_state.yaml"
    sessions_root = resolved_root / ".jikuo" / "task_sessions"
    warnings = list(state_report["warnings"])
    refusal_reasons: list[str] = []
    current_refs: list[dict[str, Any]] = []

    if state_report["state_status"] != "initialized":
        refusal_reasons.append("project_state_not_initialized")

    project_state_root = read_project_state_path_field(
        project_state_path,
        "project_root",
        project_root=resolved_root,
    )
    if project_state_root is not None and Path(project_state_root) != resolved_root:
        refusal_reasons.append("project_root_mismatch")
    elif project_state_root is None and state_report["state_status"] == "initialized":
        refusal_reasons.append("project_root_missing_in_project_state")

    if project_state_path.exists() and project_state_path.is_file():
        try:
            project_state_text = project_state_path.read_text(encoding="utf-8")
            current_refs, parse_warnings, parse_refusals = parse_latest_task_session_refs(
                project_state_text
            )
            warnings.extend(parse_warnings)
            refusal_reasons.extend(parse_refusals)
        except OSError as exc:
            refusal_reasons.append("project_state_read_failed")
            warnings.append(str(exc))

    discovered_refs, discovery_warnings, discovery_refusals = discover_task_session_refs(
        project_root=resolved_root,
        sessions_root=sessions_root,
        max_refs=max_refs,
    )
    warnings.extend(discovery_warnings)
    refusal_reasons.extend(discovery_refusals)

    if require_write_guards:
        if not confirmed:
            refusal_reasons.append("missing_confirmation_flag")
        if not approval_phrase:
            refusal_reasons.append("approval_evidence_missing")

    proposed_refs = [normalize_session_ref(ref) for ref in discovered_refs]
    current_refs = [normalize_session_ref(ref) for ref in current_refs]
    would_update = not refs_equal(current_refs, proposed_refs)
    can_refresh = not refusal_reasons

    return {
        "schema": INDEX_PLAN_SCHEMA,
        "report_only": not require_write_guards,
        "operation": "task_session_index_refresh",
        "project_root": str(resolved_root),
        "project_state_path": str(project_state_path),
        "project_state_status": state_report["state_status"],
        "task_sessions_root": str(sessions_root),
        "discovered_session_count": len(discovered_refs),
        "discovered_session_refs": discovered_refs,
        "current_latest_task_session_refs": current_refs,
        "proposed_latest_task_session_refs": proposed_refs,
        "would_update_project_state": would_update and can_refresh,
        "approval_required": True,
        "technical_confirmation_required": True,
        "command_confirmed": confirmed,
        "approval_phrase_present": bool(approval_phrase),
        "unknown_fields_preserved": True,
        "can_refresh": can_refresh,
        "source_refs": index_source_refs(),
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": INDEX_APPROVAL_TARGET,
            "decision_effect": INDEX_APPROVAL_EFFECT,
            "decision_noneffect": INDEX_APPROVAL_NONEFFECT,
            "source_plan_schema": INDEX_PLAN_SCHEMA,
        }
        if approval_phrase
        else None,
        "refusal_reasons": sorted(set(refusal_reasons)),
        "warnings": warnings,
    }


def build_index_failure_result(
    *,
    plan: dict[str, Any],
    status: str,
    error: str | None = None,
    cleanup_status: str = "not_needed",
) -> dict[str, Any]:
    return {
        "schema": INDEX_RESULT_SCHEMA,
        "operation": "task_session_index_refresh",
        "status": status,
        "project_root": plan["project_root"],
        "project_state_path": plan["project_state_path"],
        "updated_project_state_index": False,
        "previous_latest_task_session_refs": plan["current_latest_task_session_refs"],
        "new_latest_task_session_refs": plan["current_latest_task_session_refs"],
        "preserved_unknown_fields": True,
        "backup_path": None,
        "verification": {
            "read_back": False,
            "refs_ok": False,
        },
        "approval_record": plan["approval_record"],
        "refusal_reasons": plan["refusal_reasons"],
        "warnings": plan["warnings"],
        "error": error,
        "cleanup_status": cleanup_status,
        "next_actions": index_next_actions_for(status),
    }


def refresh_task_session_index(
    *,
    project_root: Path | None = None,
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_index_refresh_plan(
        project_root=project_root,
        confirmed=confirmed,
        approval_phrase=approval_phrase,
        require_write_guards=True,
    )
    if not plan["can_refresh"]:
        return (
            build_index_failure_result(
                plan=plan,
                status="refused",
                error="preflight rejected task-session index refresh",
            ),
            2,
        )

    if not plan["would_update_project_state"]:
        return (
            {
                "schema": INDEX_RESULT_SCHEMA,
                "operation": "task_session_index_refresh",
                "status": "no_change",
                "project_root": plan["project_root"],
                "project_state_path": plan["project_state_path"],
                "updated_project_state_index": False,
                "previous_latest_task_session_refs": plan[
                    "current_latest_task_session_refs"
                ],
                "new_latest_task_session_refs": plan["current_latest_task_session_refs"],
                "preserved_unknown_fields": True,
                "backup_path": None,
                "verification": {
                    "read_back": True,
                    "refs_ok": True,
                },
                "approval_record": plan["approval_record"],
                "refusal_reasons": [],
                "warnings": plan["warnings"],
                "error": None,
                "cleanup_status": "not_needed",
                "next_actions": index_next_actions_for("no_change"),
            },
            0,
        )

    project_state_path = Path(plan["project_state_path"])
    temp_file = project_state_path.with_name("project_state.yaml.tmp")
    cleanup_status = "not_needed"
    try:
        original_text = project_state_path.read_text(encoding="utf-8")
        updated_text = replace_latest_task_session_refs(
            original_text,
            plan["proposed_latest_task_session_refs"],
        )
        temp_file.write_text(updated_text, encoding="utf-8", newline="\n")
        os.replace(temp_file, project_state_path)
    except Exception as exc:
        if temp_file.exists():
            try:
                temp_file.unlink()
                cleanup_status = "completed"
            except OSError as cleanup_exc:
                cleanup_status = "failed"
                plan["warnings"].append(f"temp cleanup failed: {cleanup_exc}")
        return (
            build_index_failure_result(
                plan=plan,
                status="error",
                error=str(exc),
                cleanup_status=cleanup_status,
            ),
            1,
        )

    try:
        verified_text = project_state_path.read_text(encoding="utf-8")
        verified_refs, _, verified_refusals = parse_latest_task_session_refs(
            verified_text
        )
        refs_ok = not verified_refusals and refs_equal(
            verified_refs, plan["proposed_latest_task_session_refs"]
        )
    except OSError as exc:
        refs_ok = False
        plan["warnings"].append(f"post-refresh read failed: {exc}")

    if not refs_ok:
        return (
            build_index_failure_result(
                plan=plan,
                status="error",
                error="post-refresh verification failed",
                cleanup_status="not_attempted_after_write",
            ),
            1,
        )

    return (
        {
            "schema": INDEX_RESULT_SCHEMA,
            "operation": "task_session_index_refresh",
            "status": "updated",
            "project_root": plan["project_root"],
            "project_state_path": plan["project_state_path"],
            "updated_project_state_index": True,
            "previous_latest_task_session_refs": plan["current_latest_task_session_refs"],
            "new_latest_task_session_refs": plan["proposed_latest_task_session_refs"],
            "preserved_unknown_fields": True,
            "backup_path": None,
            "verification": {
                "read_back": True,
                "refs_ok": refs_ok,
            },
            "approval_record": plan["approval_record"],
            "refusal_reasons": [],
            "warnings": plan["warnings"],
            "error": None,
            "cleanup_status": cleanup_status,
            "next_actions": index_next_actions_for("updated"),
        },
        0,
    )


def has_raw_chat_marker(*values: str | None) -> bool:
    markers = ("raw_chat", "raw chat", "chat transcript", "聊天记录", "原始对话")
    return any(
        marker in value.lower()
        for value in values
        if value
        for marker in markers
    )


def patch_id_for(
    *,
    patch_kind: str,
    session_id: str,
    created_at: str,
    summary: str | None,
) -> str:
    seed = f"{patch_kind}|{session_id}|{created_at}|{summary or ''}".encode("utf-8")
    return f"patch_{patch_kind}_{hashlib.sha256(seed).hexdigest()[:8]}"


def section_bounds(lines: list[str], section_name: str) -> tuple[int, int] | None:
    start_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == f"{section_name}:" or line.strip() == f"{section_name}: []":
            start_index = index
            break
    if start_index is None:
        return None

    end_index = start_index + 1
    while end_index < len(lines):
        line = lines[end_index]
        if line and not line.startswith((" ", "\t")) and ":" in line:
            break
        end_index += 1
    return start_index, end_index


def parse_section_scalar(text: str, section_name: str, key: str) -> str | None:
    lines = text.splitlines()
    bounds = section_bounds(lines, section_name)
    if bounds is None:
        return None
    _, end_index = bounds
    for line in lines[bounds[0] + 1 : end_index]:
        stripped = line.strip()
        prefix = f"{key}:"
        if stripped.startswith(prefix):
            return stripped.split(":", 1)[1].strip().strip("'\"") or None
    return None


def parse_section_mapping(lines: list[str], start: int, end: int) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for line in lines[start + 1 : end]:
        stripped = line.strip()
        if not stripped or stripped == "-":
            continue
        if ":" not in stripped or stripped.startswith("- "):
            continue
        key, value = stripped.split(":", 1)
        mapping[key.strip()] = value.strip().strip("'\"") or None
    return mapping


def replace_section_mapping(
    text: str,
    section_name: str,
    updates: dict[str, Any],
) -> str:
    lines = text.splitlines()
    bounds = section_bounds(lines, section_name)
    if bounds is None:
        lines.extend(render_yaml_lines({section_name: updates}))
        return "\n".join(lines) + "\n"
    start, end = bounds
    mapping = parse_section_mapping(lines, start, end)
    mapping.update(updates)
    new_lines = [*lines[:start], *render_yaml_lines({section_name: mapping}), *lines[end:]]
    return "\n".join(new_lines) + "\n"


def append_list_item(text: str, section_name: str, item: dict[str, Any]) -> str:
    lines = text.splitlines()
    bounds = section_bounds(lines, section_name)
    rendered_item = render_yaml_lines([item], indent=2)
    if bounds is None:
        lines.extend([f"{section_name}:", *rendered_item])
        return "\n".join(lines) + "\n"
    start, end = bounds
    if lines[start].strip() == f"{section_name}: []":
        new_lines = [*lines[:start], f"{section_name}:", *rendered_item, *lines[end:]]
    else:
        new_lines = [*lines[:end], *rendered_item, *lines[end:]]
    return "\n".join(new_lines) + "\n"


def update_session_timestamp_and_status(
    text: str,
    *,
    updated_at: str,
    lifecycle_status: str | None = None,
) -> str:
    updates: dict[str, Any] = {"updated_at": updated_at}
    if lifecycle_status:
        updates["lifecycle_status"] = lifecycle_status
    return replace_section_mapping(text, "session", updates)


def select_task_session_file(
    *,
    project_root: Path,
    session_id: str | None,
) -> tuple[Path | None, dict[str, Any] | None, list[str], list[str]]:
    warnings: list[str] = []
    refusal_reasons: list[str] = []
    if not session_id:
        return None, None, warnings, ["missing_session_id"]

    sessions_root = project_root / ".jikuo" / "task_sessions"
    if not sessions_root.exists():
        return None, None, warnings, ["task_sessions_root_missing"]
    if not sessions_root.is_dir():
        return None, None, warnings, ["task_sessions_path_conflict"]

    matches = sorted(sessions_root.glob(f"*{session_id}*.yaml"))
    exact_matches: list[tuple[Path, dict[str, Any]]] = []
    for path in matches:
        try:
            path.resolve().relative_to(sessions_root.resolve())
        except ValueError:
            refusal_reasons.append("session_path_escape")
            continue
        summary = read_persisted_session_summary(path)
        if summary.get("schema") != TASK_SESSION_SCHEMA:
            refusal_reasons.append("unsupported_task_session_schema")
            continue
        if summary.get("session_id") == session_id:
            exact_matches.append((path, summary))

    if not exact_matches:
        refusal_reasons.append("session_not_found")
        return None, None, warnings, sorted(set(refusal_reasons))
    if len(exact_matches) > 1:
        refusal_reasons.append("multiple_session_matches")
        return None, None, warnings, sorted(set(refusal_reasons))

    path, summary = exact_matches[0]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        warnings.append(str(exc))
        return path, summary, warnings, ["session_read_failed"]
    summary["completion_status"] = parse_section_scalar(text, "completion", "status")
    summary["handoff_summary"] = parse_section_scalar(text, "handoff", "summary")
    return path, summary, warnings, sorted(set(refusal_reasons))


def build_update_patch(
    *,
    patch_kind: str,
    session_id: str,
    summary: str | None,
    created_at: str,
    owner_agent: str,
    evidence_kind: str | None = None,
    evidence_ref: str | None = None,
    evidence_status: str = "ok",
    command_name: str | None = None,
    exit_code: int | None = None,
    verification_layer: str | None = None,
    completion_status: str | None = None,
    approval_phrase: str | None = None,
) -> dict[str, Any]:
    patch_id = patch_id_for(
        patch_kind=patch_kind,
        session_id=session_id,
        created_at=created_at,
        summary=summary,
    )
    base = {
        "patch_id": patch_id,
        "patch_kind": patch_kind,
        "target_session_id": session_id,
        "created_at": created_at,
        "actor": owner_agent,
    }
    if patch_kind == "evidence":
        return {
            **base,
            "evidence_id": patch_id,
            "evidence_kind": evidence_kind,
            "source_ref": evidence_ref,
            "summary": summary,
            "status": evidence_status,
            "recorded_at": created_at,
            "recorded_by": owner_agent,
        }
    if patch_kind == "verification":
        return {
            **base,
            "verification_id": patch_id,
            "command": command_name,
            "summary": summary,
            "status": evidence_status,
            "exit_code": exit_code,
            "layer": verification_layer,
            "recorded_at": created_at,
            "recorded_by": owner_agent,
        }
    if patch_kind == "completion":
        return {
            **base,
            "completion_status": completion_status,
            "summary": summary,
            "decision": {
                "decision_id": patch_id,
                "decision_target": "JIKUO task-session completion update",
                "decision_effect": f"set task-session completion to {completion_status}",
                "decision_noneffect": UPDATE_APPROVAL_NONEFFECT,
                "exact_user_phrase": approval_phrase,
                "recorded_at": created_at,
                "surface": "desktop_agent_or_cli_bridge",
            },
        }
    if patch_kind == "handoff":
        return {
            **base,
            "summary": summary,
            "decision": {
                "decision_id": patch_id,
                "decision_target": "JIKUO task-session handoff update",
                "decision_effect": "update task-session handoff summary",
                "decision_noneffect": UPDATE_APPROVAL_NONEFFECT,
                "exact_user_phrase": approval_phrase,
                "recorded_at": created_at,
                "surface": "desktop_agent_or_cli_bridge",
            },
        }
    return base


def validate_update_inputs(
    *,
    patch_kind: str,
    summary: str | None,
    evidence_kind: str | None = None,
    evidence_ref: str | None = None,
    command_name: str | None = None,
    completion_status: str | None = None,
    approval_phrase: str | None = None,
    confirmed: bool = False,
    require_write_guards: bool = False,
) -> list[str]:
    refusal_reasons: list[str] = []
    if patch_kind not in {"inspect", "evidence", "verification", "completion", "handoff"}:
        refusal_reasons.append("unsupported_patch_kind")
    if patch_kind == "inspect":
        return refusal_reasons
    if require_write_guards and not confirmed:
        refusal_reasons.append("missing_confirmation_flag")
    if require_write_guards and not approval_phrase:
        refusal_reasons.append("approval_evidence_missing")
    if patch_kind in {"evidence", "verification", "completion", "handoff"} and not summary:
        refusal_reasons.append("empty_update_summary")
    if patch_kind == "evidence":
        if not evidence_kind:
            refusal_reasons.append("missing_evidence_kind")
        if not evidence_ref:
            refusal_reasons.append("missing_evidence_ref")
    if patch_kind == "verification" and not command_name:
        refusal_reasons.append("missing_verification_command")
    if patch_kind == "completion":
        if completion_status not in COMPLETION_STATUSES:
            refusal_reasons.append("unsupported_completion_status")
        if completion_status == "accepted" and not approval_phrase:
            refusal_reasons.append("accepted_completion_requires_user_decision")
    if has_raw_chat_marker(summary, evidence_kind, evidence_ref, command_name):
        refusal_reasons.append("raw_chat_transcript_disallowed")
    return refusal_reasons


def build_task_session_update_plan(
    *,
    project_root: Path | None = None,
    session_id: str | None,
    patch_kind: str = "inspect",
    owner_agent: str = "codex",
    summary: str | None = None,
    evidence_kind: str | None = None,
    evidence_ref: str | None = None,
    evidence_status: str = "ok",
    command_name: str | None = None,
    exit_code: int | None = None,
    verification_layer: str | None = None,
    completion_status: str | None = None,
    approval_phrase: str | None = None,
    confirmed: bool = False,
    require_write_guards: bool = False,
    created_at: str | None = None,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    session_path, current_summary, warnings, selection_refusals = select_task_session_file(
        project_root=resolved_root,
        session_id=session_id,
    )
    refusal_reasons = [
        *selection_refusals,
        *validate_update_inputs(
            patch_kind=patch_kind,
            summary=summary,
            evidence_kind=evidence_kind,
            evidence_ref=evidence_ref,
            command_name=command_name,
            completion_status=completion_status,
            approval_phrase=approval_phrase,
            confirmed=confirmed,
            require_write_guards=require_write_guards,
        ),
    ]
    current_completion = (
        current_summary.get("completion_status") if current_summary else None
    )
    if (
        current_completion in TERMINAL_COMPLETION_STATUSES
        and patch_kind in {"evidence", "verification", "completion"}
    ):
        refusal_reasons.append("terminal_session_update_disallowed")

    created_at_value = created_at or utc_now_iso()
    patch = None
    if patch_kind != "inspect" and session_id:
        patch = build_update_patch(
            patch_kind=patch_kind,
            session_id=session_id,
            summary=summary,
            created_at=created_at_value,
            owner_agent=owner_agent,
            evidence_kind=evidence_kind,
            evidence_ref=evidence_ref,
            evidence_status=evidence_status,
            command_name=command_name,
            exit_code=exit_code,
            verification_layer=verification_layer,
            completion_status=completion_status,
            approval_phrase=approval_phrase,
        )

    can_update = not refusal_reasons and patch_kind != "inspect"
    return {
        "schema": UPDATE_PLAN_SCHEMA,
        "report_only": not require_write_guards,
        "operation": "task_session_update",
        "project_root": str(resolved_root),
        "task_sessions_root": str(resolved_root / ".jikuo" / "task_sessions"),
        "session_id": session_id,
        "session_path": str(session_path) if session_path else None,
        "current_session_summary": current_summary,
        "patch_kind": patch_kind,
        "patch": patch,
        "would_update_task_session": can_update,
        "would_update_project_state_index": False,
        "approval_required": patch_kind in {"evidence", "verification", "completion", "handoff"},
        "technical_confirmation_required": patch_kind in {"evidence", "verification", "completion", "handoff"},
        "command_confirmed": confirmed,
        "approval_phrase_present": bool(approval_phrase),
        "can_update": can_update,
        "source_refs": update_source_refs(),
        "refusal_reasons": sorted(set(refusal_reasons)),
        "warnings": warnings,
    }


def update_next_actions_for(status: str) -> list[str]:
    if status == "updated":
        return ["use task-session status to support completion review and handoff"]
    if status == "inspected":
        return ["choose a concrete task-session update action before writing"]
    return ["resolve refusal reasons before retrying task-session update"]


def build_update_failure_result(
    *,
    plan: dict[str, Any],
    status: str,
    error: str | None = None,
    cleanup_status: str = "not_needed",
) -> dict[str, Any]:
    return {
        "schema": UPDATE_RESULT_SCHEMA,
        "operation": "task_session_update",
        "status": status,
        "project_root": plan["project_root"],
        "session_id": plan["session_id"],
        "session_path": plan["session_path"],
        "patch_kind": plan["patch_kind"],
        "updated_task_session": False,
        "updated_project_state_index": False,
        "patch": plan["patch"],
        "verification": {
            "read_back": False,
            "patch_applied": False,
        },
        "refusal_reasons": plan["refusal_reasons"],
        "warnings": plan["warnings"],
        "error": error,
        "cleanup_status": cleanup_status,
        "next_actions": update_next_actions_for(status),
    }


def apply_update_patch_to_text(text: str, plan: dict[str, Any]) -> str:
    patch = plan["patch"]
    patch_kind = plan["patch_kind"]
    updated_at = patch["created_at"]
    updated = text
    if patch_kind == "evidence":
        item = {
            "evidence_id": patch["evidence_id"],
            "evidence_kind": patch["evidence_kind"],
            "source_ref": patch["source_ref"],
            "summary": patch["summary"],
            "status": patch["status"],
            "recorded_at": patch["recorded_at"],
            "recorded_by": patch["recorded_by"],
        }
        updated = append_list_item(updated, "evidence_snapshots", item)
    elif patch_kind == "verification":
        item = {
            "verification_id": patch["verification_id"],
            "command": patch["command"],
            "summary": patch["summary"],
            "status": patch["status"],
            "exit_code": patch["exit_code"],
            "layer": patch["layer"],
            "recorded_at": patch["recorded_at"],
            "recorded_by": patch["recorded_by"],
        }
        updated = append_list_item(updated, "verification", item)
    elif patch_kind == "completion":
        updated = replace_section_mapping(
            updated,
            "completion",
            {
                "status": patch["completion_status"],
                "summary": patch["summary"],
                "updated_at": updated_at,
            },
        )
        updated = append_list_item(updated, "user_decisions", patch["decision"])
    elif patch_kind == "handoff":
        updated = replace_section_mapping(
            updated,
            "handoff",
            {
                "summary": patch["summary"],
                "updated_at": updated_at,
            },
        )
        updated = append_list_item(updated, "user_decisions", patch["decision"])

    updated = append_list_item(
        updated,
        "audit_trail",
        {
            "action": f"task_session_{patch_kind}_updated",
            "actor": patch["actor"],
            "recorded_at": updated_at,
            "patch_id": patch["patch_id"],
        },
    )
    lifecycle_status = (
        patch.get("completion_status") if patch_kind == "completion" else None
    )
    return update_session_timestamp_and_status(
        updated,
        updated_at=updated_at,
        lifecycle_status=lifecycle_status,
    )


def update_task_session(
    *,
    project_root: Path | None = None,
    session_id: str | None,
    patch_kind: str,
    owner_agent: str = "codex",
    summary: str | None = None,
    evidence_kind: str | None = None,
    evidence_ref: str | None = None,
    evidence_status: str = "ok",
    command_name: str | None = None,
    exit_code: int | None = None,
    verification_layer: str | None = None,
    completion_status: str | None = None,
    approval_phrase: str | None = None,
    confirmed: bool = False,
    created_at: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_task_session_update_plan(
        project_root=project_root,
        session_id=session_id,
        patch_kind=patch_kind,
        owner_agent=owner_agent,
        summary=summary,
        evidence_kind=evidence_kind,
        evidence_ref=evidence_ref,
        evidence_status=evidence_status,
        command_name=command_name,
        exit_code=exit_code,
        verification_layer=verification_layer,
        completion_status=completion_status,
        approval_phrase=approval_phrase,
        confirmed=confirmed,
        require_write_guards=True,
        created_at=created_at,
    )
    if not plan["can_update"]:
        return (
            build_update_failure_result(
                plan=plan,
                status="refused",
                error="preflight rejected task-session update",
            ),
            2,
        )

    session_path = Path(plan["session_path"])
    temp_file = session_path.with_suffix(".yaml.tmp")
    try:
        original_text = session_path.read_text(encoding="utf-8")
        updated_text = apply_update_patch_to_text(original_text, plan)
        temp_file.write_text(updated_text, encoding="utf-8", newline="\n")
        os.replace(temp_file, session_path)
    except Exception as exc:
        cleanup_status = "not_needed"
        if temp_file.exists():
            try:
                temp_file.unlink()
                cleanup_status = "completed"
            except OSError as cleanup_exc:
                cleanup_status = "failed"
                plan["warnings"].append(f"temp cleanup failed: {cleanup_exc}")
        return (
            build_update_failure_result(
                plan=plan,
                status="error",
                error=str(exc),
                cleanup_status=cleanup_status,
            ),
            1,
        )

    try:
        summary_after = read_persisted_session_summary(session_path)
        text_after = session_path.read_text(encoding="utf-8")
        patch_applied = plan["patch"]["patch_id"] in text_after
        schema_ok = summary_after.get("schema") == TASK_SESSION_SCHEMA
        session_id_ok = summary_after.get("session_id") == plan["session_id"]
    except OSError as exc:
        patch_applied = False
        schema_ok = False
        session_id_ok = False
        plan["warnings"].append(f"post-update read failed: {exc}")

    if not (patch_applied and schema_ok and session_id_ok):
        return (
            build_update_failure_result(
                plan=plan,
                status="error",
                error="post-update verification failed",
                cleanup_status="not_attempted_after_write",
            ),
            1,
        )

    return (
        {
            "schema": UPDATE_RESULT_SCHEMA,
            "operation": "task_session_update",
            "status": "updated",
            "project_root": plan["project_root"],
            "session_id": plan["session_id"],
            "session_path": plan["session_path"],
            "patch_kind": plan["patch_kind"],
            "updated_task_session": True,
            "updated_project_state_index": False,
            "patch": plan["patch"],
            "verification": {
                "read_back": True,
                "patch_applied": patch_applied,
                "schema_ok": schema_ok,
                "session_id_ok": session_id_ok,
            },
            "refusal_reasons": [],
            "warnings": plan["warnings"],
            "error": None,
            "cleanup_status": "not_needed",
            "next_actions": update_next_actions_for("updated"),
        },
        0,
    )


def write_task_session(
    *,
    project_root: Path | None = None,
    task_title: str,
    owner_agent: str = "codex",
    created_at: str | None = None,
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_write_plan(
        project_root=project_root,
        task_title=task_title,
        owner_agent=owner_agent,
        created_at=created_at,
        confirmed=confirmed,
        approval_phrase=approval_phrase,
    )
    if not plan["can_write"]:
        return (
            build_write_failure_result(
                plan=plan,
                status="refused",
                error="preflight rejected task-session write",
            ),
            2,
        )

    sessions_root = Path(plan["task_sessions_root"])
    target_file = Path(plan["session_path"])
    created_directory = False
    created_file = False
    cleanup_status = "not_needed"

    try:
        if not sessions_root.exists():
            sessions_root.mkdir()
            created_directory = True
        fd = os.open(target_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(render_task_session_yaml(plan["would_write"]))
            handle.flush()
            os.fsync(handle.fileno())
        created_file = True
    except Exception as exc:
        cleanup_errors: list[str] = []
        if created_file and target_file.exists():
            try:
                target_file.unlink()
            except OSError as cleanup_exc:
                cleanup_errors.append(f"session file cleanup failed: {cleanup_exc}")
        if created_directory and sessions_root.exists():
            try:
                if not any(sessions_root.iterdir()):
                    sessions_root.rmdir()
            except OSError as cleanup_exc:
                cleanup_errors.append(
                    f"task sessions directory cleanup failed: {cleanup_exc}"
                )
        cleanup_status = "failed" if cleanup_errors else "completed"
        result = build_write_failure_result(
            plan=plan,
            status="error",
            error=str(exc),
            cleanup_status=cleanup_status,
        )
        result["created_directory"] = created_directory
        result["created_file"] = created_file and target_file.exists()
        result["warnings"].extend(cleanup_errors)
        return result, 1

    summary = read_persisted_session_summary(target_file)
    schema_ok = summary.get("schema") == TASK_SESSION_SCHEMA
    session_id_ok = summary.get("session_id") == plan["session_id"]
    if not (schema_ok and session_id_ok):
        cleanup_errors = []
        try:
            target_file.unlink()
            created_file = False
        except OSError as cleanup_exc:
            cleanup_errors.append(f"failed to remove invalid session file: {cleanup_exc}")
        if created_directory and sessions_root.exists():
            try:
                if not any(sessions_root.iterdir()):
                    sessions_root.rmdir()
                    created_directory = False
            except OSError as cleanup_exc:
                cleanup_errors.append(
                    f"task sessions directory cleanup failed: {cleanup_exc}"
                )
        result = build_write_failure_result(
            plan=plan,
            status="error",
            error="post-write verification failed",
            cleanup_status="failed" if cleanup_errors else "completed",
        )
        result["warnings"].extend(cleanup_errors)
        return result, 1

    return (
        {
            "schema": WRITE_RESULT_SCHEMA,
            "operation": "task_session_start_write",
            "status": "written",
            "write_performed": True,
            "project_root": plan["project_root"],
            "task_sessions_root": plan["task_sessions_root"],
            "session_id": plan["session_id"],
            "session_path": plan["session_path"],
            "created_directory": created_directory,
            "created_file": created_file,
            "updated_project_state_index": False,
            "overwritten_paths": [],
            "approval_record": plan["approval_record"],
            "source_refs": plan["source_refs"],
            "verification": {
                "read_back": True,
                "schema_ok": schema_ok,
                "session_id_ok": session_id_ok,
                "summary": summary,
            },
            "refusal_reasons": [],
            "warnings": [],
            "error": None,
            "cleanup_status": cleanup_status,
            "next_actions": write_next_actions_for(write_performed=True),
        },
        0,
    )


def build_status_report(
    *,
    project_root: Path | None = None,
    session_id: str,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    sessions_root = resolved_root / ".jikuo" / "task_sessions"
    matches = []
    records = []
    if sessions_root.is_dir():
        paths = sorted(sessions_root.glob(f"*{session_id}*.yaml"))
        matches = [str(path) for path in paths]
        records = [read_persisted_session_summary(path) for path in paths]
    status = "found" if matches else "not_found"
    return {
        "schema": STATUS_SCHEMA,
        "report_only": True,
        "project_root": str(resolved_root),
        "task_sessions_root": str(sessions_root),
        "session_id": session_id,
        "session_status": status,
        "matched_paths": matches,
        "matched_records": records,
        "write_allowed_by_command": False,
        "warnings": []
        if status == "found"
        else ["task-session persistence is not initialized or session was not found"],
    }


def relative_or_absolute(path: str, root: str) -> str:
    path_obj = Path(path)
    root_obj = Path(root)
    try:
        return str(path_obj.relative_to(root_obj))
    except ValueError:
        return path


def format_text(report: dict[str, Any]) -> str:
    if report["schema"] == UPDATE_RESULT_SCHEMA:
        lines = [
            "JIKUO Task Session Update Result",
            f"Project root: {report['project_root']}",
            f"Session id: {report['session_id']}",
            f"Session path: {relative_or_absolute(report['session_path'], report['project_root']) if report['session_path'] else 'not found'}",
            f"Patch kind: {report['patch_kind']}",
            f"Status: {report['status']}",
            f"Updated task session: {'yes' if report['updated_task_session'] else 'no'}",
            f"Updated project-state index: {'yes' if report['updated_project_state_index'] else 'no'}",
        ]
        if report["refusal_reasons"]:
            lines.append("Refusal reasons:")
            lines.extend(f"- {reason}" for reason in report["refusal_reasons"])
        if report.get("error"):
            lines.append(f"Error: {report['error']}")
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    if report["schema"] == UPDATE_PLAN_SCHEMA:
        lines = [
            "JIKUO Task Session Update Plan (dry-run)",
            f"Project root: {report['project_root']}",
            f"Session id: {report['session_id']}",
            f"Session path: {relative_or_absolute(report['session_path'], report['project_root']) if report['session_path'] else 'not found'}",
            f"Patch kind: {report['patch_kind']}",
            f"Would update task session: {'yes' if report['would_update_task_session'] else 'no'}",
            f"Would update project-state index: {'yes' if report['would_update_project_state_index'] else 'no'}",
            "Writes performed: no",
        ]
        if report["refusal_reasons"]:
            lines.append("Refusal reasons:")
            lines.extend(f"- {reason}" for reason in report["refusal_reasons"])
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        return "\n".join(lines)

    if report["schema"] == INDEX_RESULT_SCHEMA:
        lines = [
            "JIKUO Task Session Index Refresh Result",
            f"Project root: {report['project_root']}",
            f"Project state: {relative_or_absolute(report['project_state_path'], report['project_root'])}",
            f"Status: {report['status']}",
            f"Updated project-state index: {'yes' if report['updated_project_state_index'] else 'no'}",
            f"Previous refs: {len(report['previous_latest_task_session_refs'])}",
            f"New refs: {len(report['new_latest_task_session_refs'])}",
            f"Preserved unknown fields: {'yes' if report['preserved_unknown_fields'] else 'no'}",
        ]
        if report["refusal_reasons"]:
            lines.append("Refusal reasons:")
            lines.extend(f"- {reason}" for reason in report["refusal_reasons"])
        if report.get("error"):
            lines.append(f"Error: {report['error']}")
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    if report["schema"] == INDEX_PLAN_SCHEMA:
        lines = [
            "JIKUO Task Session Index Refresh Plan (dry-run)",
            f"Project root: {report['project_root']}",
            f"Project state: {report['project_state_status']}",
            f"Task sessions root: {relative_or_absolute(report['task_sessions_root'], report['project_root'])}",
            f"Discovered sessions: {report['discovered_session_count']}",
            f"Current refs: {len(report['current_latest_task_session_refs'])}",
            f"Proposed refs: {len(report['proposed_latest_task_session_refs'])}",
            f"Would update project-state index: {'yes' if report['would_update_project_state'] else 'no'}",
            "Writes performed: no",
        ]
        if report["refusal_reasons"]:
            lines.append("Refusal reasons:")
            lines.extend(f"- {reason}" for reason in report["refusal_reasons"])
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        return "\n".join(lines)

    if report["schema"] == WRITE_RESULT_SCHEMA:
        lines = [
            "JIKUO Task Session Write Result",
            f"Project root: {report['project_root']}",
            f"Session id: {report['session_id']}",
            f"Session path: {relative_or_absolute(report['session_path'], report['project_root'])}",
            f"Status: {report['status']}",
            f"Write performed: {'yes' if report['write_performed'] else 'no'}",
            f"Created directory: {'yes' if report['created_directory'] else 'no'}",
            f"Created file: {'yes' if report['created_file'] else 'no'}",
            f"Updated project-state index: {'yes' if report['updated_project_state_index'] else 'no'}",
        ]
        if report["refusal_reasons"]:
            lines.append("Refusal reasons:")
            lines.extend(f"- {reason}" for reason in report["refusal_reasons"])
        if report.get("error"):
            lines.append(f"Error: {report['error']}")
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    if report["schema"] == START_PLAN_SCHEMA:
        lines = [
            "JIKUO Task Session Start Plan (dry-run)",
            f"Project root: {report['project_root']}",
            f"Project state: {report['project_state_status']}",
            f"Session id: {report['session_id']}",
            f"Target file: {relative_or_absolute(report['target_session_file'], report['project_root'])}",
            "Writes performed: no",
            "Write allowed by command: no",
        ]
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    lines = [
        "JIKUO Task Session Status (report-only)",
        f"Project root: {report['project_root']}",
        f"Session id: {report['session_id']}",
        f"Session status: {report['session_status']}",
        "Writes performed: no",
    ]
    if report["matched_paths"]:
        lines.append("Matched paths:")
        lines.extend(
            f"- {relative_or_absolute(path, report['project_root'])}"
            for path in report["matched_paths"]
        )
    if report["matched_records"]:
        lines.append("Matched records:")
        lines.extend(
            f"- {record.get('session_id', 'unknown')} ({record.get('schema', 'unknown schema')})"
            for record in report["matched_records"]
        )
    if report["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run JIKUO task-session helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("--dry-run", action="store_true", help="Build a start plan.")
    start.add_argument(
        "--write",
        action="store_true",
        help="Create a task-session sidecar record when all guards pass.",
    )
    start.add_argument(
        "--confirm-create-task-session",
        action="store_true",
        help="Technical confirmation required for write mode.",
    )
    start.add_argument(
        "--approval-phrase",
        default=None,
        help="Exact user phrase approving the task-session write effect.",
    )
    start.add_argument("--task-title", required=True, help="Short task title.")
    start.add_argument(
        "--owner-agent",
        choices=sorted(ALLOWED_OWNER_AGENTS),
        default="codex",
        help="Agent responsible for the task session.",
    )
    start.add_argument("--project-root", type=Path, default=None)
    start.add_argument("--format", choices=("text", "json"), default="text")

    status = subparsers.add_parser("status")
    status.add_argument("--session-id", required=True)
    status.add_argument("--project-root", type=Path, default=None)
    status.add_argument("--format", choices=("text", "json"), default="text")

    index = subparsers.add_parser("index")
    index.add_argument("--dry-run", action="store_true", help="Build an index plan.")
    index.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh project-state latest_task_session_refs when all guards pass.",
    )
    index.add_argument(
        "--confirm-update-project-state-index",
        action="store_true",
        help="Technical confirmation required for index refresh mode.",
    )
    index.add_argument(
        "--approval-phrase",
        default=None,
        help="Exact user phrase approving the project-state index update.",
    )
    index.add_argument("--project-root", type=Path, default=None)
    index.add_argument("--format", choices=("text", "json"), default="text")

    update = subparsers.add_parser("update")
    update.add_argument("--dry-run", action="store_true", help="Build an update plan.")
    update.add_argument(
        "--append-evidence",
        action="store_true",
        help="Append an evidence snapshot when guards pass.",
    )
    update.add_argument(
        "--append-verification",
        action="store_true",
        help="Append a verification record when guards pass.",
    )
    update.add_argument("--session-id", required=True)
    update.add_argument("--evidence-kind", default=None)
    update.add_argument("--evidence-ref", default=None)
    update.add_argument("--summary", default=None)
    update.add_argument("--evidence-status", default="ok")
    update.add_argument("--command-name", default=None)
    update.add_argument("--exit-code", type=int, default=None)
    update.add_argument("--verification-layer", default=None)
    update.add_argument(
        "--confirm-update-task-session",
        action="store_true",
        help="Technical confirmation required for update mode.",
    )
    update.add_argument("--approval-phrase", default=None)
    update.add_argument(
        "--owner-agent",
        choices=sorted(ALLOWED_OWNER_AGENTS),
        default="codex",
    )
    update.add_argument("--project-root", type=Path, default=None)
    update.add_argument("--format", choices=("text", "json"), default="text")

    complete = subparsers.add_parser("complete")
    complete.add_argument("--session-id", required=True)
    complete.add_argument("--status", choices=sorted(COMPLETION_STATUSES), required=True)
    complete.add_argument("--summary", required=True)
    complete.add_argument(
        "--confirm-complete-task-session",
        action="store_true",
        help="Technical confirmation required for completion updates.",
    )
    complete.add_argument("--approval-phrase", default=None)
    complete.add_argument(
        "--owner-agent",
        choices=sorted(ALLOWED_OWNER_AGENTS),
        default="codex",
    )
    complete.add_argument("--project-root", type=Path, default=None)
    complete.add_argument("--format", choices=("text", "json"), default="text")

    handoff = subparsers.add_parser("handoff")
    handoff.add_argument("--session-id", required=True)
    handoff.add_argument("--summary", required=True)
    handoff.add_argument(
        "--confirm-update-task-session",
        action="store_true",
        help="Technical confirmation required for handoff updates.",
    )
    handoff.add_argument("--approval-phrase", default=None)
    handoff.add_argument(
        "--owner-agent",
        choices=sorted(ALLOWED_OWNER_AGENTS),
        default="codex",
    )
    handoff.add_argument("--project-root", type=Path, default=None)
    handoff.add_argument("--format", choices=("text", "json"), default="text")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "start":
        if args.dry_run and args.write:
            parser.error("task-session start accepts either --dry-run or --write, not both")
        if not args.dry_run and not args.write:
            parser.error("task-session start requires --dry-run or --write")
        if args.write:
            report, exit_code = write_task_session(
                project_root=args.project_root,
                task_title=args.task_title,
                owner_agent=args.owner_agent,
                confirmed=args.confirm_create_task_session,
                approval_phrase=args.approval_phrase,
            )
        else:
            report = build_start_plan(
                project_root=args.project_root,
                task_title=args.task_title,
                owner_agent=args.owner_agent,
            )
            exit_code = 0
    elif args.command == "status":
        report = build_status_report(
            project_root=args.project_root,
            session_id=args.session_id,
        )
        exit_code = 0
    elif args.command == "index":
        if args.dry_run and args.refresh:
            parser.error("task-session index accepts either --dry-run or --refresh, not both")
        if not args.dry_run and not args.refresh:
            parser.error("task-session index requires --dry-run or --refresh")
        if args.refresh:
            report, exit_code = refresh_task_session_index(
                project_root=args.project_root,
                confirmed=args.confirm_update_project_state_index,
                approval_phrase=args.approval_phrase,
            )
        else:
            report = build_index_refresh_plan(project_root=args.project_root)
            exit_code = 0
    elif args.command == "update":
        selected = [args.dry_run, args.append_evidence, args.append_verification]
        if sum(1 for item in selected if item) != 1:
            parser.error(
                "task-session update requires exactly one of --dry-run, "
                "--append-evidence, or --append-verification"
            )
        if args.dry_run:
            patch_kind = (
                "verification"
                if args.command_name
                else "evidence"
                if args.evidence_kind or args.evidence_ref or args.summary
                else "inspect"
            )
            report = build_task_session_update_plan(
                project_root=args.project_root,
                session_id=args.session_id,
                patch_kind=patch_kind,
                owner_agent=args.owner_agent,
                summary=args.summary,
                evidence_kind=args.evidence_kind,
                evidence_ref=args.evidence_ref,
                evidence_status=args.evidence_status,
                command_name=args.command_name,
                exit_code=args.exit_code,
                verification_layer=args.verification_layer,
            )
            exit_code = 0
        else:
            patch_kind = "evidence" if args.append_evidence else "verification"
            report, exit_code = update_task_session(
                project_root=args.project_root,
                session_id=args.session_id,
                patch_kind=patch_kind,
                owner_agent=args.owner_agent,
                summary=args.summary,
                evidence_kind=args.evidence_kind,
                evidence_ref=args.evidence_ref,
                evidence_status=args.evidence_status,
                command_name=args.command_name,
                exit_code=args.exit_code,
                verification_layer=args.verification_layer,
                confirmed=args.confirm_update_task_session,
                approval_phrase=args.approval_phrase,
            )
    elif args.command == "complete":
        report, exit_code = update_task_session(
            project_root=args.project_root,
            session_id=args.session_id,
            patch_kind="completion",
            owner_agent=args.owner_agent,
            summary=args.summary,
            completion_status=args.status,
            confirmed=args.confirm_complete_task_session,
            approval_phrase=args.approval_phrase,
        )
    else:
        report, exit_code = update_task_session(
            project_root=args.project_root,
            session_id=args.session_id,
            patch_kind="handoff",
            owner_agent=args.owner_agent,
            summary=args.summary,
            confirmed=args.confirm_update_task_session,
            approval_phrase=args.approval_phrase,
        )

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_text(report))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
