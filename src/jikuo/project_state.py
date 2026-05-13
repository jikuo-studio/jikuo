"""JIKUO project-state bootstrap helper.

The default helper behavior is read-only. The initial write mode is guarded by
explicit command confirmation and approval evidence, and refuses overwrites.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


BOOTSTRAP_REPORT_SCHEMA = "jikuo.project_state_bootstrap_report.v0"
PROJECT_STATE_SCHEMA = "jikuo.project_local_state.v0"
WRITE_PLAN_SCHEMA = "jikuo.project_state_write_plan.v0"
WRITE_RESULT_SCHEMA = "jikuo.project_state_write_result.v0"
REGISTRY_REF = "docs/scenarios/interactive_novel/governance/rule_registry.yaml"
APPROVAL_TARGET = "JIKUO project-state initialization"
APPROVAL_EFFECT = "create .jikuo/project_state.yaml"
CONTRACT_REFS = [
    "docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md",
    "docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md",
    "docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md",
    "docs/jikuo/schemas/task_session.schema.md",
    REGISTRY_REF,
]


def discover_project_root(project_root: Path | None = None, cwd: Path | None = None) -> Path:
    """Resolve an explicit root or discover a likely repository root."""

    if project_root is not None:
        return project_root.expanduser().resolve()

    current = (cwd or Path.cwd()).expanduser().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / REGISTRY_REF).exists():
            return candidate
    return current


def derive_project_id(project_root: Path) -> str:
    base = project_root.name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
    return slug or "project"


def read_top_level_schema(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None
        schema = value.get("schema") if isinstance(value, dict) else None
        return schema if isinstance(schema, str) else None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("schema:"):
            value = line.split(":", 1)[1].strip()
            return value.strip("'\"") or None
    return None


def classify_state(state_root: Path, state_file: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []

    if not state_root.exists():
        return "missing", warnings

    if not state_root.is_dir():
        return "conflict", [f"state root exists but is not a directory: {state_root}"]

    if not state_file.exists():
        warnings.append("state root exists but project_state.yaml is missing")
        return "missing", warnings

    if not state_file.is_file():
        return "conflict", [f"state file path exists but is not a file: {state_file}"]

    try:
        schema = read_top_level_schema(state_file)
    except OSError as exc:
        return "unsafe", [f"state file cannot be read: {exc}"]

    if schema == PROJECT_STATE_SCHEMA:
        return "initialized", warnings

    if schema is None:
        warnings.append("state file has no supported top-level schema")
    else:
        warnings.append(f"unsupported project state schema: {schema}")
    return "stale_schema", warnings


def quote_yaml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_project_state_yaml(state: dict[str, Any]) -> str:
    """Render the small project-state shape without adding a YAML dependency."""

    compatibility = state["compatibility"]
    lines = [
        f"schema: {quote_yaml(state['schema'])}",
        f"project_id: {quote_yaml(state['project_id'])}",
        f"project_root: {quote_yaml(state['project_root'])}",
        f"jikuo_state_root: {quote_yaml(state['jikuo_state_root'])}",
        "active_scenario_packages:",
    ]
    lines.extend(
        f"  - {quote_yaml(item)}" for item in state["active_scenario_packages"]
    )
    lines.append("accepted_contract_refs:")
    lines.extend(f"  - {quote_yaml(item)}" for item in state["accepted_contract_refs"])
    lines.extend(
        [
            f"registry_ref: {quote_yaml(state['registry_ref'])}",
            "latest_task_session_refs: []",
            "latest_rule_proposal_refs: []",
            "latest_handoff_ref: null",
            "compatibility:",
            f"  unknown_fields: {quote_yaml(compatibility['unknown_fields'])}",
            f"  writer: {quote_yaml(compatibility['writer'])}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_project_state_draft(
    project_root: Path,
    state_root: Path,
    *,
    writer: str = "report_only_bootstrap",
) -> dict[str, Any]:
    return {
        "schema": PROJECT_STATE_SCHEMA,
        "project_id": derive_project_id(project_root),
        "project_root": str(project_root),
        "jikuo_state_root": str(state_root),
        "active_scenario_packages": ["engineering_governance"],
        "accepted_contract_refs": CONTRACT_REFS,
        "registry_ref": REGISTRY_REF,
        "latest_task_session_refs": [],
        "latest_rule_proposal_refs": [],
        "latest_handoff_ref": None,
        "compatibility": {
            "unknown_fields": "preserve",
            "writer": writer,
        },
    }


def next_actions_for(command: str, state_status: str) -> list[str]:
    if state_status == "missing" and command == "status":
        return ["run init --dry-run to inspect the proposed project state"]
    if state_status == "missing" and command == "init":
        return ["review would_create before approving any future write-mode work order"]
    if state_status == "initialized":
        return ["use project state as read-only input for later sidecar planning"]
    if state_status == "stale_schema":
        return ["review the existing project_state.yaml schema before using it"]
    if state_status == "conflict":
        return ["resolve the conflicting .jikuo path before bootstrap planning continues"]
    if state_status == "unsafe":
        return ["fix project-state read permissions before bootstrap planning continues"]
    return []


def write_next_actions_for(state_status: str, write_performed: bool) -> list[str]:
    if write_performed and state_status == "initialized":
        return ["use project state as durable JIKUO governance bootstrap input"]
    if state_status == "initialized":
        return ["project state already exists; do not rerun initial write mode"]
    if state_status == "missing":
        return ["review approval and confirmation flags before retrying write mode"]
    if state_status == "stale_schema":
        return ["review existing project_state.yaml schema before any migration work"]
    if state_status == "conflict":
        return ["resolve .jikuo path conflict before write mode can run"]
    if state_status == "unsafe":
        return ["fix project-state access before write mode can run"]
    return []


def build_bootstrap_report(
    *,
    project_root: Path | None = None,
    cwd: Path | None = None,
    command: str = "status",
    include_would_create: bool = False,
) -> dict[str, Any]:
    resolved_root = discover_project_root(project_root=project_root, cwd=cwd)
    state_root = resolved_root / ".jikuo"
    state_file = state_root / "project_state.yaml"
    state_status, warnings = classify_state(state_root=state_root, state_file=state_file)

    return {
        "schema": BOOTSTRAP_REPORT_SCHEMA,
        "report_only": True,
        "command": command,
        "project_root": str(resolved_root),
        "state_root": str(state_root),
        "state_file": str(state_file),
        "state_status": state_status,
        "write_allowed_by_command": False,
        "would_create": (
            build_project_state_draft(project_root=resolved_root, state_root=state_root)
            if include_would_create
            else None
        ),
        "source_refs": CONTRACT_REFS,
        "warnings": warnings,
        "next_actions": next_actions_for(command=command, state_status=state_status),
    }


def build_write_plan(
    *,
    project_root: Path | None = None,
    approval_phrase: str | None = None,
    confirmed: bool = False,
) -> dict[str, Any]:
    report = build_bootstrap_report(
        project_root=project_root,
        command="init",
        include_would_create=True,
    )
    warnings = list(report["warnings"])
    state_status = report["state_status"]
    resolved_root = Path(report["project_root"])
    state_root = Path(report["state_root"])
    state_file = Path(report["state_file"])
    registry_exists = (resolved_root / REGISTRY_REF).exists()

    if state_root.exists():
        warnings.append("write mode requires .jikuo to be absent for initial creation")
    if not confirmed:
        warnings.append("missing technical confirmation flag")
    if not approval_phrase:
        warnings.append("missing approval phrase evidence")
    if not registry_exists:
        warnings.append(f"required registry source ref is missing: {REGISTRY_REF}")

    can_write = (
        state_status == "missing"
        and not state_root.exists()
        and confirmed
        and bool(approval_phrase)
        and registry_exists
    )

    return {
        "schema": WRITE_PLAN_SCHEMA,
        "report_only": False,
        "write_kind": "initial_project_state",
        "project_root": str(resolved_root),
        "state_root": str(state_root),
        "state_file": str(state_file),
        "preflight_state_status": state_status,
        "requires_human_approval": True,
        "requires_command_confirmation": True,
        "command_confirmed": confirmed,
        "approval_phrase_present": bool(approval_phrase),
        "no_overwrite": True,
        "atomic_write": True,
        "can_write": can_write,
        "would_write": build_project_state_draft(
            project_root=resolved_root,
            state_root=state_root,
            writer="project_state_write_mode",
        ),
        "source_refs": CONTRACT_REFS,
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": APPROVAL_TARGET,
            "decision_effect": APPROVAL_EFFECT,
            "source_report_schema": BOOTSTRAP_REPORT_SCHEMA,
            "source_report_state_status": state_status,
        }
        if approval_phrase
        else None,
        "warnings": warnings,
    }


def build_write_failure_result(
    *,
    plan: dict[str, Any],
    error: str,
    cleanup_status: str = "not_needed",
) -> dict[str, Any]:
    return {
        "schema": WRITE_RESULT_SCHEMA,
        "write_performed": False,
        "write_kind": "initial_project_state",
        "project_root": plan["project_root"],
        "state_root": plan["state_root"],
        "state_file": plan["state_file"],
        "preflight_state_status": plan["preflight_state_status"],
        "post_write_state_status": plan["preflight_state_status"],
        "created_paths": [],
        "overwritten_paths": [],
        "approval_record": plan["approval_record"],
        "source_refs": CONTRACT_REFS,
        "warnings": plan["warnings"],
        "error": error,
        "cleanup_status": cleanup_status,
        "next_actions": write_next_actions_for(
            state_status=plan["preflight_state_status"],
            write_performed=False,
        ),
    }


def write_initial_project_state(
    *,
    project_root: Path | None = None,
    approval_phrase: str | None = None,
    confirmed: bool = False,
) -> tuple[dict[str, Any], int]:
    plan = build_write_plan(
        project_root=project_root,
        approval_phrase=approval_phrase,
        confirmed=confirmed,
    )
    if not plan["can_write"]:
        return (
            build_write_failure_result(
                plan=plan,
                error="preflight rejected project-state write",
            ),
            2,
        )

    state_root = Path(plan["state_root"])
    state_file = Path(plan["state_file"])
    temp_file = state_root / "project_state.yaml.tmp"
    created_paths: list[str] = []
    cleanup_status = "not_needed"

    try:
        state_root.mkdir()
        created_paths.append(".jikuo/")
        state = plan["would_write"]
        temp_file.write_text(render_project_state_yaml(state), encoding="utf-8")
        try:
            fd = os.open(state_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise RuntimeError("project_state.yaml already exists") from None
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(temp_file.read_text(encoding="utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        temp_file.unlink()
        created_paths.append(".jikuo/project_state.yaml")
    except Exception as exc:
        cleanup_errors: list[str] = []
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError as cleanup_exc:
                cleanup_errors.append(f"temp cleanup failed: {cleanup_exc}")
        if ".jikuo/project_state.yaml" not in created_paths and state_root.exists():
            try:
                if not any(state_root.iterdir()):
                    state_root.rmdir()
            except OSError as cleanup_exc:
                cleanup_errors.append(f"state root cleanup failed: {cleanup_exc}")
        cleanup_status = "failed" if cleanup_errors else "completed"
        result = build_write_failure_result(
            plan=plan,
            error=str(exc),
            cleanup_status=cleanup_status,
        )
        if cleanup_errors:
            result["warnings"].extend(cleanup_errors)
        return result, 1

    post_status, post_warnings = classify_state(state_root=state_root, state_file=state_file)
    if post_status != "initialized":
        result = build_write_failure_result(
            plan=plan,
            error="post-write verification failed",
            cleanup_status="not_attempted_after_write",
        )
        result["post_write_state_status"] = post_status
        result["created_paths"] = created_paths
        result["warnings"].extend(post_warnings)
        return result, 1

    return (
        {
            "schema": WRITE_RESULT_SCHEMA,
            "write_performed": True,
            "write_kind": "initial_project_state",
            "project_root": plan["project_root"],
            "state_root": plan["state_root"],
            "state_file": plan["state_file"],
            "preflight_state_status": plan["preflight_state_status"],
            "post_write_state_status": post_status,
            "created_paths": created_paths,
            "overwritten_paths": [],
            "approval_record": plan["approval_record"],
            "source_refs": CONTRACT_REFS,
            "warnings": post_warnings,
            "next_actions": write_next_actions_for(
                state_status=post_status,
                write_performed=True,
            ),
        },
        0,
    )


def relative_or_absolute(path: str, root: str) -> str:
    path_obj = Path(path)
    root_obj = Path(root)
    try:
        return str(path_obj.relative_to(root_obj))
    except ValueError:
        return path


def format_text(report: dict[str, Any]) -> str:
    if report["schema"] == WRITE_RESULT_SCHEMA:
        lines = [
            "JIKUO Project State Write Result",
            f"Project root: {report['project_root']}",
            f"Preflight state: {report['preflight_state_status']}",
            f"Post-write state: {report['post_write_state_status']}",
            f"Write performed: {'yes' if report['write_performed'] else 'no'}",
            f"State file: {relative_or_absolute(report['state_file'], report['project_root'])}",
        ]
        if report["created_paths"]:
            lines.append("Created paths:")
            lines.extend(f"- {path}" for path in report["created_paths"])
        if report.get("error"):
            lines.append(f"Error: {report['error']}")
        if report["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in report["warnings"])
        if report["next_actions"]:
            lines.append("Next actions:")
            lines.extend(f"- {action}" for action in report["next_actions"])
        return "\n".join(lines)

    sidecar_path = relative_or_absolute(report["state_file"], report["project_root"])
    lines = [
        "JIKUO Project State Bootstrap (report-only)",
        f"Project root: {report['project_root']}",
        f"State status: {report['state_status']}",
        f"Sidecar path: {sidecar_path}",
        "Writes performed: no",
        "Write allowed by command: no",
    ]

    if report["would_create"] is not None:
        lines.append(f"Would create schema: {report['would_create']['schema']}")
        lines.append(f"Would create project id: {report['would_create']['project_id']}")

    if report["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])

    if report["next_actions"]:
        lines.append("Next actions:")
        lines.extend(f"- {action}" for action in report["next_actions"])

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report-only JIKUO project-state bootstrap helper."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("status", "init"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument(
            "--project-root",
            type=Path,
            default=None,
            help="Project root to inspect. Defaults to repository discovery from cwd.",
        )
        subparser.add_argument(
            "--format",
            choices=("text", "json"),
            default="text",
            help="Output format.",
        )
        if name == "init":
            subparser.add_argument(
                "--dry-run",
                action="store_true",
                help="Produce the project-state draft without writing files.",
            )
            subparser.add_argument(
                "--write",
                action="store_true",
                help="Create the initial project-state file when all guards pass.",
            )
            subparser.add_argument(
                "--confirm-create-project-state",
                action="store_true",
                help="Technical confirmation required for write mode.",
            )
            subparser.add_argument(
                "--approval-phrase",
                default=None,
                help="Exact user approval phrase recorded as write evidence.",
            )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init" and args.dry_run and args.write:
        parser.error("init requires either --dry-run or --write, not both")
    if args.command == "init" and not args.dry_run and not args.write:
        parser.error("init requires --dry-run or --write")

    if args.command == "init" and args.write:
        result, exit_code = write_initial_project_state(
            project_root=args.project_root,
            approval_phrase=args.approval_phrase,
            confirmed=args.confirm_create_project_state,
        )
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_text(result))
        return exit_code

    report = build_bootstrap_report(
        project_root=args.project_root,
        command=args.command,
        include_would_create=args.command == "init",
    )

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
