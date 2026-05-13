"""Desktop-card projection helper for JIKUO task-session outputs.

This helper is intentionally no-write. It projects existing task-session helper
plans/results into compact Markdown or JSON cards for Codex / Claude desktop
workflows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

if __package__:
    from . import task_session
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import task_session


CARD_SCHEMA = "jikuo.desktop_task_session_workflow_card.v0"
COMMAND_PROPOSAL_SCHEMA = "jikuo.desktop_command_proposal.v0"
APPROVAL_CAPTURE_SCHEMA = "jikuo.desktop_approval_capture.v0"
APPROVAL_PHRASE_PLACEHOLDER = '"<exact user phrase as spoken>"'
TASK_SESSION_COMMAND = "python -B -m jikuo.task_session"


def stable_card_id(card_kind: str, seed: str) -> str:
    digest = hashlib.sha256(f"{card_kind}|{seed}".encode("utf-8")).hexdigest()[:10]
    return f"card_{card_kind}_{digest}"


def quote_arg(value: str | None) -> str:
    if value is None:
        return '""'
    return '"' + value.replace('"', '\\"') + '"'


def status_from_refusals(refusal_reasons: list[str], default: str = "review") -> str:
    return "refused" if refusal_reasons else default


def approval_request(
    *,
    card_id: str,
    target: str,
    effect: str,
    non_effects: list[str],
    command_kind: str,
) -> dict[str, Any]:
    return {
        "schema": APPROVAL_CAPTURE_SCHEMA,
        "card_id": card_id,
        "approval_target": target,
        "approval_effect": effect,
        "approval_non_effects": non_effects,
        "exact_user_phrase": "<exact user phrase as spoken>",
        "approval_surface": "codex_desktop_or_claude_desktop",
        "approved_command_kind": command_kind,
    }


def command_proposal(
    *,
    command_kind: str,
    command_preview: str,
    expected_result_schema: str,
    writes: list[str],
    does_not_write: list[str],
    required_flags: list[str],
) -> dict[str, Any]:
    return {
        "schema": COMMAND_PROPOSAL_SCHEMA,
        "command_kind": command_kind,
        "command_preview": command_preview,
        "expected_result_schema": expected_result_schema,
        "writes": writes,
        "does_not_write": does_not_write,
        "requires_user_approval": True,
        "required_flags": required_flags,
        "approval_phrase_placeholder": APPROVAL_PHRASE_PLACEHOLDER,
    }


def start_plan_card(plan: dict[str, Any]) -> dict[str, Any]:
    refusal_reasons = list(plan.get("warnings", [])) if not plan.get("can_start") else []
    card_kind = (
        "task_session_start_preview"
        if plan.get("can_start")
        else "task_session_refusal"
    )
    card_id = stable_card_id(card_kind, plan.get("session_id", "missing_session"))
    target = "JIKUO task-session file creation"
    effect = "create one compact task-session sidecar record"
    non_effects = [
        "do not capture raw chat transcript",
        "do not update .jikuo/project_state.yaml latest_task_session_refs",
        "do not judge product output quality",
    ]
    title = (
        "Task-session start preview"
        if plan.get("can_start")
        else "Task-session start refused"
    )
    would_create = plan.get("would_create") or {}
    session = would_create.get("session") or {}
    command = (
        f"{TASK_SESSION_COMMAND} start --write "
        f"--task-title {quote_arg(session.get('task_title'))} "
        f"--owner-agent {quote_arg(session.get('owner_agent'))} "
        f"--project-root {quote_arg(plan.get('project_root'))} "
        "--confirm-create-task-session "
        "--approval-phrase \"<exact user phrase as spoken>\" "
        "--format json"
    )
    proposal = (
        command_proposal(
            command_kind="task_session_start_write",
            command_preview=command,
            expected_result_schema=task_session.WRITE_RESULT_SCHEMA,
            writes=[plan.get("target_session_file", "")],
            does_not_write=[".jikuo/project_state.yaml"],
            required_flags=["--confirm-create-task-session", "--approval-phrase"],
        )
        if plan.get("can_start")
        else None
    )

    return {
        "schema": CARD_SCHEMA,
        "card_id": card_id,
        "card_kind": card_kind,
        "status": status_from_refusals(refusal_reasons),
        "title": title,
        "user_facing_summary": (
            "A task-session file can be created after explicit approval."
            if plan.get("can_start")
            else "Task-session creation is not safe yet; resolve the refusal reasons first."
        ),
        "source_refs": plan.get("source_refs", []),
        "task_session_refs": [plan.get("session_id")] if plan.get("session_id") else [],
        "command_proposal": proposal,
        "approval_request": (
            approval_request(
                card_id=card_id,
                target=target,
                effect=effect,
                non_effects=non_effects,
                command_kind="task_session_start_write",
            )
            if plan.get("can_start")
            else None
        ),
        "write_effect": {
            "target": target,
            "effect": effect,
            "non_effects": non_effects,
        },
        "shown_inputs": [
            f"project_root: {plan.get('project_root')}",
            f"project_state_status: {plan.get('project_state_status')}",
            f"session_id: {plan.get('session_id')}",
        ],
        "shown_outputs": [
            f"target_session_file: {plan.get('target_session_file')}",
            f"write_allowed_by_command: {plan.get('write_allowed_by_command')}",
        ],
        "refusal_reasons": refusal_reasons,
        "next_actions": plan.get("next_actions", []),
    }


def index_plan_card(plan: dict[str, Any]) -> dict[str, Any]:
    refusal_reasons = list(plan.get("refusal_reasons", []))
    card_kind = (
        "task_session_index_refresh"
        if not refusal_reasons
        else "task_session_refusal"
    )
    card_id = stable_card_id(card_kind, plan.get("project_state_path", "missing_state"))
    target = "JIKUO project-state task-session index update"
    effect = "update .jikuo/project_state.yaml latest_task_session_refs"
    non_effects = [
        "do not create task-session files",
        "do not capture raw chat transcript",
        "do not judge product output quality",
    ]
    command = (
        f"{TASK_SESSION_COMMAND} index --refresh "
        f"--project-root {quote_arg(plan.get('project_root'))} "
        "--confirm-update-project-state-index "
        "--approval-phrase \"<exact user phrase as spoken>\" "
        "--format json"
    )
    proposal = (
        command_proposal(
            command_kind="task_session_index_refresh",
            command_preview=command,
            expected_result_schema=task_session.INDEX_RESULT_SCHEMA,
            writes=[plan.get("project_state_path", "")],
            does_not_write=[plan.get("task_sessions_root", "")],
            required_flags=[
                "--confirm-update-project-state-index",
                "--approval-phrase",
            ],
        )
        if not refusal_reasons and plan.get("would_update_project_state")
        else None
    )

    return {
        "schema": CARD_SCHEMA,
        "card_id": card_id,
        "card_kind": card_kind,
        "status": status_from_refusals(
            refusal_reasons,
            "review" if plan.get("would_update_project_state") else "ok",
        ),
        "title": "Task-session index refresh",
        "user_facing_summary": (
            "Project-state latest task-session refs can be refreshed after explicit approval."
            if plan.get("would_update_project_state")
            else "No project-state task-session index update is needed right now."
        ),
        "source_refs": plan.get("source_refs", []),
        "task_session_refs": [
            ref.get("session_id")
            for ref in plan.get("proposed_latest_task_session_refs", [])
            if ref.get("session_id")
        ],
        "command_proposal": proposal,
        "approval_request": (
            approval_request(
                card_id=card_id,
                target=target,
                effect=effect,
                non_effects=non_effects,
                command_kind="task_session_index_refresh",
            )
            if proposal
            else None
        ),
        "write_effect": {
            "target": target,
            "effect": effect,
            "non_effects": non_effects,
        },
        "shown_inputs": [
            f"project_root: {plan.get('project_root')}",
            f"project_state_status: {plan.get('project_state_status')}",
            f"discovered_session_count: {plan.get('discovered_session_count')}",
        ],
        "shown_outputs": [
            f"would_update_project_state: {plan.get('would_update_project_state')}",
            "unknown_fields_preserved: true",
        ],
        "refusal_reasons": refusal_reasons,
        "next_actions": [
            "approve the index refresh card before running guarded refresh"
            if proposal
            else "continue without index refresh"
        ],
    }


def update_plan_card(plan: dict[str, Any]) -> dict[str, Any]:
    refusal_reasons = list(plan.get("refusal_reasons", []))
    patch_kind = plan.get("patch_kind", "inspect")
    card_kind = (
        f"task_session_{patch_kind}_append"
        if patch_kind in {"evidence", "verification"}
        else "task_session_completion_acceptance"
        if patch_kind == "completion"
        else "task_session_handoff"
        if patch_kind == "handoff"
        else "task_session_refusal"
    )
    if refusal_reasons:
        card_kind = "task_session_refusal"
    card_id = stable_card_id(card_kind, f"{plan.get('session_id')}|{patch_kind}")
    target = "JIKUO task-session lifecycle update"
    effect = f"append or update compact {patch_kind} process state"
    non_effects = [
        "do not update .jikuo/project_state.yaml latest_task_session_refs",
        "do not capture raw chat transcript",
        "do not judge product output quality",
    ]
    proposal = None
    if plan.get("can_update") and patch_kind in {"evidence", "verification", "completion", "handoff"}:
        proposal = command_proposal(
            command_kind=f"task_session_{patch_kind}_update",
            command_preview=update_command_preview(plan),
            expected_result_schema=task_session.UPDATE_RESULT_SCHEMA,
            writes=[plan.get("session_path", "")],
            does_not_write=[".jikuo/project_state.yaml"],
            required_flags=[
                "--confirm-complete-task-session"
                if patch_kind == "completion"
                else "--confirm-update-task-session",
                "--approval-phrase",
            ],
        )

    return {
        "schema": CARD_SCHEMA,
        "card_id": card_id,
        "card_kind": card_kind,
        "status": status_from_refusals(
            refusal_reasons,
            "review" if proposal else "ok" if patch_kind == "inspect" else "missing",
        ),
        "title": f"Task-session {patch_kind} workflow",
        "user_facing_summary": (
            f"The task session can receive a guarded {patch_kind} update after explicit approval."
            if proposal
            else "No guarded lifecycle update is ready from this preview."
        ),
        "source_refs": plan.get("source_refs", []),
        "task_session_refs": [plan.get("session_id")] if plan.get("session_id") else [],
        "command_proposal": proposal,
        "approval_request": (
            approval_request(
                card_id=card_id,
                target=target,
                effect=effect,
                non_effects=non_effects,
                command_kind=f"task_session_{patch_kind}_update",
            )
            if proposal
            else None
        ),
        "write_effect": {
            "target": target,
            "effect": effect,
            "non_effects": non_effects,
        },
        "shown_inputs": [
            f"project_root: {plan.get('project_root')}",
            f"session_id: {plan.get('session_id')}",
            f"patch_kind: {patch_kind}",
        ],
        "shown_outputs": [
            f"session_path: {plan.get('session_path')}",
            f"would_update_task_session: {plan.get('would_update_task_session')}",
            f"would_update_project_state_index: {plan.get('would_update_project_state_index')}",
        ],
        "refusal_reasons": refusal_reasons,
        "next_actions": [
            "approve the lifecycle update card before running guarded update"
            if proposal
            else "resolve missing/refusal items before guarded lifecycle update"
        ],
    }


def update_command_preview(plan: dict[str, Any]) -> str:
    patch = plan.get("patch") or {}
    session_id = quote_arg(plan.get("session_id"))
    project_root = quote_arg(plan.get("project_root"))
    phrase = "--approval-phrase \"<exact user phrase as spoken>\""
    patch_kind = plan.get("patch_kind")
    if patch_kind == "evidence":
        return (
            f"{TASK_SESSION_COMMAND} update --append-evidence "
            f"--session-id {session_id} "
            f"--project-root {project_root} "
            f"--evidence-kind {quote_arg(patch.get('evidence_kind'))} "
            f"--evidence-ref {quote_arg(patch.get('source_ref'))} "
            f"--summary {quote_arg(patch.get('summary'))} "
            "--confirm-update-task-session "
            f"{phrase} --format json"
        )
    if patch_kind == "verification":
        return (
            f"{TASK_SESSION_COMMAND} update --append-verification "
            f"--session-id {session_id} "
            f"--project-root {project_root} "
            f"--command-name {quote_arg(patch.get('command'))} "
            f"--summary {quote_arg(patch.get('summary'))} "
            "--confirm-update-task-session "
            f"{phrase} --format json"
        )
    if patch_kind == "completion":
        return (
            f"{TASK_SESSION_COMMAND} complete "
            f"--session-id {session_id} "
            f"--project-root {project_root} "
            f"--status {quote_arg(patch.get('completion_status'))} "
            f"--summary {quote_arg(patch.get('summary'))} "
            "--confirm-complete-task-session "
            f"{phrase} --format json"
        )
    return (
        f"{TASK_SESSION_COMMAND} handoff "
        f"--session-id {session_id} "
        f"--project-root {project_root} "
        f"--summary {quote_arg(patch.get('summary'))} "
        "--confirm-update-task-session "
        f"{phrase} --format json"
    )


def build_card(report: dict[str, Any]) -> dict[str, Any]:
    schema = report.get("schema")
    if schema == task_session.START_PLAN_SCHEMA:
        return start_plan_card(report)
    if schema == task_session.INDEX_PLAN_SCHEMA:
        return index_plan_card(report)
    if schema == task_session.UPDATE_PLAN_SCHEMA:
        return update_plan_card(report)
    raise ValueError(f"unsupported task-session report schema: {schema}")


def render_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"## {card['title']}",
        "",
        f"- Status: `{card['status']}`",
        f"- Card kind: `{card['card_kind']}`",
        f"- Card id: `{card['card_id']}`",
        f"- Summary: {card['user_facing_summary']}",
        "",
        "### Write Effect",
        "",
        f"- Target: {card['write_effect']['target']}",
        f"- Effect: {card['write_effect']['effect']}",
    ]
    for non_effect in card["write_effect"]["non_effects"]:
        lines.append(f"- Non-effect: {non_effect}")
    if card["shown_inputs"]:
        lines.extend(["", "### Shown Inputs", ""])
        lines.extend(f"- {item}" for item in card["shown_inputs"])
    if card["shown_outputs"]:
        lines.extend(["", "### Shown Outputs", ""])
        lines.extend(f"- {item}" for item in card["shown_outputs"])
    if card["refusal_reasons"]:
        lines.extend(["", "### Refusal Reasons", ""])
        lines.extend(f"- {item}" for item in card["refusal_reasons"])
    proposal = card.get("command_proposal")
    if proposal:
        lines.extend(
            [
                "",
                "### Command Proposal",
                "",
                f"- Command kind: `{proposal['command_kind']}`",
                f"- Expected result schema: `{proposal['expected_result_schema']}`",
                "- Requires explicit user approval: `true`",
                "",
                "```powershell",
                proposal["command_preview"],
                "```",
            ]
        )
    approval = card.get("approval_request")
    if approval:
        lines.extend(
            [
                "",
                "### Approval Capture",
                "",
                f"- Approval target: {approval['approval_target']}",
                f"- Approval effect: {approval['approval_effect']}",
                f"- Exact phrase placeholder: `{approval['exact_user_phrase']}`",
            ]
        )
    if card["next_actions"]:
        lines.extend(["", "### Next Actions", ""])
        lines.extend(f"- {item}" for item in card["next_actions"])
    return "\n".join(lines) + "\n"


def print_card(card: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(card))


def read_json_input(path: str) -> dict[str, Any]:
    if path == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="No-write JIKUO task-session desktop card projection helper."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start-preview")
    start.add_argument("--task-title", required=True)
    start.add_argument(
        "--owner-agent",
        choices=sorted(task_session.ALLOWED_OWNER_AGENTS),
        default="codex",
    )
    start.add_argument("--project-root", type=Path, default=None)
    start.add_argument("--format", choices=("markdown", "json"), default="markdown")

    index = subparsers.add_parser("index-preview")
    index.add_argument("--project-root", type=Path, default=None)
    index.add_argument("--format", choices=("markdown", "json"), default="markdown")

    update = subparsers.add_parser("update-preview")
    update.add_argument("--session-id", required=True)
    update.add_argument("--project-root", type=Path, default=None)
    update.add_argument("--summary", default=None)
    update.add_argument("--evidence-kind", default=None)
    update.add_argument("--evidence-ref", default=None)
    update.add_argument("--command-name", default=None)
    update.add_argument("--exit-code", type=int, default=None)
    update.add_argument("--verification-layer", default=None)
    update.add_argument("--format", choices=("markdown", "json"), default="markdown")

    render = subparsers.add_parser("render-json")
    render.add_argument("--input", required=True)
    render.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "start-preview":
        report = task_session.build_start_plan(
            project_root=args.project_root,
            task_title=args.task_title,
            owner_agent=args.owner_agent,
        )
    elif args.command == "index-preview":
        report = task_session.build_index_refresh_plan(project_root=args.project_root)
    elif args.command == "update-preview":
        patch_kind = (
            "verification"
            if args.command_name
            else "evidence"
            if args.evidence_kind or args.evidence_ref or args.summary
            else "inspect"
        )
        report = task_session.build_task_session_update_plan(
            project_root=args.project_root,
            session_id=args.session_id,
            patch_kind=patch_kind,
            summary=args.summary,
            evidence_kind=args.evidence_kind,
            evidence_ref=args.evidence_ref,
            command_name=args.command_name,
            exit_code=args.exit_code,
            verification_layer=args.verification_layer,
        )
    else:
        report = read_json_input(args.input)

    card = build_card(report)
    print_card(card, args.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
