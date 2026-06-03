"""Universal JIKUO instruction file distribution helper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ == "jikuo.integrations":
    from .. import activation_settings, project_state
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import activation_settings
    import project_state


INSTALL_PLAN_SCHEMA = "jikuo.instruction_install_plan.v0"
INSTALL_RESULT_SCHEMA = "jikuo.instruction_install_result.v0"
MANAGED_BEGIN = "# BEGIN JIKUO MANAGED INSTRUCTIONS"
MANAGED_END = "# END JIKUO MANAGED INSTRUCTIONS"
CANONICAL_CLIENT = "jikuo"
APPROVAL_TARGET = "JIKUO universal instruction distribution"
APPROVAL_EFFECT = "create or update JIKUO instruction files"
TRIGGER_MODE_CHOICES = activation_settings.TRIGGER_MODE_CHOICES

CLIENT_TARGETS: dict[str, dict[str, str]] = {
    CANONICAL_CLIENT: {
        "label": "JIKUO canonical instructions",
        "path": "JIKUO.md",
        "purpose": "canonical project-level JIKUO instruction file",
    },
    "codex": {
        "label": "Codex project instructions",
        "path": "AGENTS.md",
        "purpose": "Codex project instruction sync target",
    },
    "claude-code": {
        "label": "Claude Code project instructions",
        "path": "CLAUDE.md",
        "purpose": "Claude Code project instruction sync target",
    },
    "cursor": {
        "label": "Cursor project rules",
        "path": ".cursorrules",
        "purpose": "Cursor project rule sync target",
    },
    "vscode-copilot": {
        "label": "VS Code Copilot project instructions",
        "path": ".github/copilot-instructions.md",
        "purpose": "VS Code GitHub Copilot Agent mode instruction sync target",
    },
    "continue": {
        "label": "Continue project rules",
        "path": ".continuerules",
        "purpose": "Continue project rule sync target",
    },
}

SYNC_CLIENTS = tuple(key for key in CLIENT_TARGETS if key != CANONICAL_CLIENT)


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
    except ValueError:
        return False
    return True


def path_ref(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).as_posix()


def resolve_target(project_root: Path, target_ref: str) -> Path:
    target = (project_root / target_ref).resolve()
    if not is_relative_to(target, project_root.resolve()):
        raise ValueError(f"instruction target escaped project root: {target_ref}")
    return target


def common_instruction_lines() -> list[str]:
    return [
        "JIKUO is a deterministic governance harness after activation.",
        "For covered JIKUO flows, call the local runner or future MCP tool instead of relying on memory or prose.",
        "Show returned governance card Markdown verbatim before commentary.",
        "Do not summarize, abbreviate, or omit policy runtime status cards.",
        "Surface runtime links so the user can open `.jikuo/runtime/last_card.md` and `.jikuo/runtime/state_summary.json`.",
        "The user can verify current state with `jikuo show` and the latest card with `jikuo show --last-card`.",
        "Guarded writes require explicit approval phrases and technical confirmation.",
        "For governed turns, after reading and understanding the user request and before governed action, tool use, workspace writes, or final response, call the appropriate JIKUO router or proposal surface with compact `host_semantic_intent` using status=provided, provider=host_ai, policy_scopes limited to discussion/editing/progress_summary, requested_outcome, execution_boundary, response_contract, and a short user_expression.",
        "If compact semantic intent cannot be returned in GUI subscription mode, report semantic intent coverage as degraded or missing instead of implying strict semantic gating.",
        "If you perform workspace writes in a turn, including file creation, edits, deletion, generated outputs, git staging, commits, or guarded project writes, run `python -B -m jikuo.agent_flow propose --event completion_review --project-root \"<absolute project root>\" --format json` after verification and before the final response.",
        "Do not ask the user to run that routine completion receipt; if it cannot run or fails, report that the completion receipt is missing or failed.",
        "Do not treat SDK hooks, client plugins, or chat instructions as replacements for local JIKUO evidence.",
    ]


def activation_setting_lines(trigger_mode: str) -> list[str]:
    mode = trigger_mode if trigger_mode in TRIGGER_MODE_CHOICES else "ask"
    lines = [
        "When JIKUO is first enabled for this project, ask the user to review activation settings before governed work continues.",
        "Activation settings to review: trigger mode, MCP server availability, card-display contract, runtime visibility links, guarded-write approval boundary, starter policy initialization, and project-context bindings.",
    ]
    if mode == "ask":
        lines.extend(
            [
                "Trigger mode is not fixed in this instruction block.",
                "Ask the user to choose `semantic` mode or `mounted` mode before the first governed turn.",
                "`semantic` mode means the Agent calls JIKUO when the turn appears to carry JIKUO obligations.",
                "`mounted` mode means a supported hook, plugin, SDK wrapper, Studio entry, or local proxy calls JIKUO before every user turn and records idle ticks when nothing is required.",
            ]
        )
    elif mode == "semantic":
        lines.extend(
            [
                "Configured trigger mode for this client: `semantic`.",
                "Call JIKUO when the user asks for governed work, progress/todo meaning, policy changes, task-session work, acceptance, handoff, or when repeated user needs may become policy candidates.",
            ]
        )
    else:
        lines.extend(
            [
                "Configured trigger mode for this client: `mounted`.",
                "Before every user turn is handled, call JIKUO conversation routing with `--trigger-mode mounted` when this client has a supported pre-turn hook, plugin, SDK wrapper, Studio entry, or local proxy.",
                "If this client has only MCP plus instruction files, tell the user that mounted mode is requested but not strictly enforceable until a pre-turn adapter is installed; use the JIKUO router at the start of governed turns and surface the runtime card link.",
            ]
        )
    return lines


def render_managed_block(client_key: str, *, trigger_mode: str = "ask") -> str:
    spec = CLIENT_TARGETS[client_key]
    lines = [
        MANAGED_BEGIN,
        "",
        "# JIKUO Harness Instructions",
        "",
        f"Target: {spec['label']}",
        f"Purpose: {spec['purpose']}",
        "",
        "Follow these rules whenever this project uses JIKUO:",
        "",
    ]
    lines.extend(f"- {line}" for line in common_instruction_lines())
    lines.extend(
        [
            "",
            "Activation settings:",
            "",
        ]
    )
    lines.extend(f"- {line}" for line in activation_setting_lines(trigger_mode))
    if client_key != CANONICAL_CLIENT:
        lines.extend(
            [
                "",
                "Canonical source:",
                "",
                "- Keep this managed block aligned with `JIKUO.md`.",
            ]
        )
    lines.extend(["", MANAGED_END, ""])
    return "\n".join(lines)


def has_managed_block(text: str) -> bool:
    return MANAGED_BEGIN in text and MANAGED_END in text


def replace_managed_block(existing: str, block: str) -> str:
    start = existing.index(MANAGED_BEGIN)
    end = existing.index(MANAGED_END, start) + len(MANAGED_END)
    suffix = existing[end:]
    if suffix.startswith("\n"):
        suffix = suffix[1:]
    prefix = existing[:start].rstrip()
    pieces = []
    if prefix:
        pieces.append(prefix)
    pieces.append(block.rstrip())
    if suffix.strip():
        pieces.append(suffix.strip())
    return "\n\n".join(pieces).rstrip() + "\n"


def merge_managed_block(existing: str | None, block: str) -> tuple[str, str, bool]:
    if existing is None:
        return block.rstrip() + "\n", "create", False
    if has_managed_block(existing):
        updated = replace_managed_block(existing, block)
        operation = "noop" if updated == existing else "update_managed_block"
        return updated, operation, True
    if not existing.strip():
        return block.rstrip() + "\n", "update_empty_file", False
    merged = existing.rstrip() + "\n\n" + block.rstrip() + "\n"
    return merged, "append_managed_block", False


def select_clients(
    *,
    project_root: Path,
    clients: list[str] | None,
    all_clients: bool,
) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    selected = [CANONICAL_CLIENT]
    if all_clients:
        detected = [
            key
            for key in SYNC_CLIENTS
            if (project_root / CLIENT_TARGETS[key]["path"]).exists()
        ]
        selected.extend(detected)
        if not detected:
            warnings.append("no existing client instruction files detected for --all")
    for client in clients or []:
        if client not in CLIENT_TARGETS:
            warnings.append(f"unsupported client ignored: {client}")
            continue
        if client not in selected:
            selected.append(client)
    return selected, warnings


def build_install_plan(
    *,
    project_root: Path | None = None,
    clients: list[str] | None = None,
    all_clients: bool = False,
    trigger_mode: str | None = None,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    resolved_trigger_mode, trigger_mode_source, settings_status = (
        activation_settings.resolve_trigger_mode(
            project_root=resolved_root,
            requested_trigger_mode=trigger_mode,
            default="ask",
        )
    )
    selected_clients, warnings = select_clients(
        project_root=resolved_root,
        clients=clients,
        all_clients=all_clients,
    )
    targets: list[dict[str, Any]] = []
    for client in selected_clients:
        spec = CLIENT_TARGETS[client]
        target = resolve_target(resolved_root, spec["path"])
        existing = target.read_text(encoding="utf-8") if target.is_file() else None
        merged, operation, managed_block_present = merge_managed_block(
            existing,
            render_managed_block(client, trigger_mode=resolved_trigger_mode),
        )
        targets.append(
            {
                "client": client,
                "label": spec["label"],
                "path_ref": path_ref(target, resolved_root),
                "path": str(target),
                "exists": existing is not None,
                "managed_block_present": managed_block_present,
                "operation": operation,
                "write_needed": operation != "noop",
                "planned_size_bytes": len(merged.encode("utf-8")),
            }
        )
    write_needed = any(target["write_needed"] for target in targets)
    return {
        "schema": INSTALL_PLAN_SCHEMA,
        "status": "review" if write_needed else "ok",
        "project_root": str(resolved_root),
        "selected_clients": selected_clients,
        "targets": targets,
        "write_allowed_by_command": False,
        "writes_performed": False,
        "approval_required": write_needed,
        "approval_target": APPROVAL_TARGET,
        "approval_effect": APPROVAL_EFFECT,
        "activation_settings": {
            "schema": "jikuo.client_activation_settings.v0",
            "trigger_mode": resolved_trigger_mode,
            "trigger_mode_source": trigger_mode_source,
            "project_settings_status": settings_status.get("status"),
            "trigger_mode_choices": list(TRIGGER_MODE_CHOICES),
            "strict_mounted_requires_adapter": True,
            "client_prompt_required": resolved_trigger_mode == "ask",
        },
        "warnings": warnings,
        "refusal_reasons": [],
        "next_actions": (
            [
                "review instruction file targets and managed-block operations",
                "rerun with --write --confirm-install and an approval phrase to apply",
            ]
            if write_needed
            else ["instruction files are already up to date"]
        ),
    }


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def apply_install_plan(
    *,
    project_root: Path | None = None,
    clients: list[str] | None = None,
    all_clients: bool = False,
    confirm_install: bool = False,
    approval_phrase: str | None = None,
    trigger_mode: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_install_plan(
        project_root=project_root,
        clients=clients,
        all_clients=all_clients,
        trigger_mode=trigger_mode,
    )
    refusals: list[str] = []
    if not confirm_install:
        refusals.append("confirm_install_required")
    if not approval_phrase:
        refusals.append("approval_phrase_required")
    if refusals:
        result = dict(plan)
        result["schema"] = INSTALL_RESULT_SCHEMA
        result["status"] = "refused"
        result["refusal_reasons"] = refusals
        result["write_allowed_by_command"] = False
        result["writes_performed"] = False
        result["next_actions"] = [
            "rerun with --confirm-install and --approval-phrase after reviewing the plan"
        ]
        return result, 2

    resolved_root = Path(plan["project_root"]).resolve()
    written_refs: list[str] = []
    updated_targets: list[dict[str, Any]] = []
    for target_info in plan["targets"]:
        target = Path(target_info["path"]).resolve()
        if not is_relative_to(target, resolved_root):
            raise ValueError(f"instruction target escaped project root: {target}")
        existing = target.read_text(encoding="utf-8") if target.is_file() else None
        merged, operation, managed_block_present = merge_managed_block(
            existing,
            render_managed_block(
                str(target_info["client"]),
                trigger_mode=str(plan["activation_settings"]["trigger_mode"]),
            ),
        )
        applied = operation != "noop"
        if applied:
            write_file(target, merged)
            written_refs.append(path_ref(target, resolved_root))
        updated = dict(target_info)
        updated["operation"] = operation
        updated["managed_block_present"] = managed_block_present
        updated["write_performed"] = applied
        updated_targets.append(updated)

    result = dict(plan)
    result["schema"] = INSTALL_RESULT_SCHEMA
    result["status"] = "ok"
    result["targets"] = updated_targets
    result["write_allowed_by_command"] = True
    result["writes_performed"] = bool(written_refs)
    result["written_refs"] = written_refs
    result["approval_record"] = {
        "approval_target": APPROVAL_TARGET,
        "approval_effect": APPROVAL_EFFECT,
        "approval_phrase_recorded": True,
    }
    result["next_actions"] = [
        "review generated instruction files",
        "use jikuo show to verify runtime visibility when governed work runs",
    ]
    return result, 0


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "# JIKUO Instruction Install",
        "",
        f"- Status: `{report['status']}`",
        f"- Project root: `{report['project_root']}`",
        f"- Writes performed: `{str(report.get('writes_performed', False)).lower()}`",
        "",
        "| Client | Path | Operation |",
        "|---|---|---|",
    ]
    for target in report.get("targets", []):
        lines.append(
            f"| `{target['client']}` | `{target['path_ref']}` | `{target['operation']}` |"
        )
    if report.get("written_refs"):
        lines.extend(["", "## Written Files", ""])
        lines.extend(f"- `{ref}`" for ref in report["written_refs"])
    if report.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {item}" for item in report["warnings"])
    if report.get("refusal_reasons"):
        lines.extend(["", "## Refusal Reasons", ""])
        lines.extend(f"- `{item}`" for item in report["refusal_reasons"])
    if report.get("next_actions"):
        lines.extend(["", "## Next Actions", ""])
        lines.extend(f"- {item}" for item in report["next_actions"])
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install JIKUO instruction files.")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--client", choices=SYNC_CLIENTS, action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--trigger-mode", choices=TRIGGER_MODE_CHOICES, default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--confirm-install", action="store_true")
    parser.add_argument("--approval-phrase", default=None)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.write:
        report, exit_code = apply_install_plan(
            project_root=args.project_root,
            clients=args.client,
            all_clients=args.all,
            confirm_install=args.confirm_install,
            approval_phrase=args.approval_phrase,
            trigger_mode=args.trigger_mode,
        )
    else:
        report = build_install_plan(
            project_root=args.project_root,
            clients=args.client,
            all_clients=args.all,
            trigger_mode=args.trigger_mode,
        )
        exit_code = 0
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report), end="")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
