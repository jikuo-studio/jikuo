"""First-use and ongoing JIKUO configuration review.

The review is intentionally read-only. It aggregates existing project-local
signals so a user can see what JIKUO knows about activation, instructions,
runtime visibility, starter policies, and guarded-write boundaries before any
configuration write happens.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

if __package__:
    from . import activation_settings, policy_store, project_state
    from .integrations import instruction_files
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jikuo import activation_settings, policy_store, project_state
    from jikuo.integrations import instruction_files


CONFIGURATION_REVIEW_SCHEMA = "jikuo.configuration_review.v0"
CONFIGURATION_ITEM_SCHEMA = "jikuo.configuration_review_item.v0"
FIRST_RUN_STATUS_SCHEMA = "jikuo.first_run_configuration_status.v0"
FIRST_RUN_REQUIRED_ITEM_KEYS = (
    "activation_settings",
    "project_context",
    "starter_policies",
)
FIRST_RUN_RECOMMENDED_ITEM_KEYS = (
    "instruction_files",
    "runtime_visibility",
    "mcp_server",
)


def status_rank(status: str) -> int:
    return {
        "ok": 0,
        "info": 0,
        "review": 1,
        "missing": 2,
        "blocked": 3,
    }.get(status, 1)


def item(
    *,
    key: str,
    title: str,
    status: str,
    meaning: str,
    current: str,
    evidence_refs: list[str] | None = None,
    next_actions: list[str] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": CONFIGURATION_ITEM_SCHEMA,
        "key": key,
        "title": title,
        "status": status,
        "meaning": meaning,
        "current": current,
        "evidence_refs": evidence_refs or [],
        "next_actions": next_actions or [],
        "details": details or {},
    }


def build_first_run_step(
    *,
    entry: dict[str, Any] | None,
    key: str,
    requirement: str,
) -> dict[str, Any]:
    entry_status = str((entry or {}).get("status") or "missing")
    step_status = (
        "complete"
        if entry_status == "ok"
        else "blocked"
        if entry_status == "blocked"
        else "needs_review"
    )
    required = requirement == "required"
    next_actions = list((entry or {}).get("next_actions") or [])
    return {
        "key": key,
        "title": str((entry or {}).get("title") or key.replace("_", " ").title()),
        "requirement": requirement,
        "status": step_status,
        "source_status": entry_status,
        "is_blocker": required and step_status != "complete",
        "current": str((entry or {}).get("current") or "not observed"),
        "business_meaning": str(
            (entry or {}).get("meaning")
            or "This setup concern affects first-run usability."
        ),
        "next_action": next_actions[0] if next_actions else None,
    }


def build_first_run_status(items: list[dict[str, Any]]) -> dict[str, Any]:
    by_key = {
        str(entry.get("key")): entry
        for entry in items
        if isinstance(entry, dict) and entry.get("key")
    }
    required_steps = [
        build_first_run_step(entry=by_key.get(key), key=key, requirement="required")
        for key in FIRST_RUN_REQUIRED_ITEM_KEYS
    ]
    recommended_steps = [
        build_first_run_step(
            entry=by_key.get(key),
            key=key,
            requirement="recommended",
        )
        for key in FIRST_RUN_RECOMMENDED_ITEM_KEYS
    ]
    steps = [*required_steps, *recommended_steps]
    blockers = [step for step in required_steps if step["is_blocker"]]
    blocked_count = sum(1 for step in blockers if step["status"] == "blocked")
    recommended_attention = [
        step for step in recommended_steps if step["status"] != "complete"
    ]
    status = (
        "blocked"
        if blocked_count
        else "needs_configuration"
        if blockers
        else "ready"
    )
    next_actions = [
        str(step["next_action"])
        for step in steps
        if step.get("next_action")
    ][:8]
    return {
        "schema": FIRST_RUN_STATUS_SCHEMA,
        "status": status,
        "user_usable": not blockers and not blocked_count,
        "required_complete_count": sum(
            1 for step in required_steps if step["status"] == "complete"
        ),
        "required_total_count": len(required_steps),
        "blocker_count": len(blockers),
        "recommended_attention_count": len(recommended_attention),
        "blockers": blockers,
        "required_steps": required_steps,
        "recommended_steps": recommended_steps,
        "next_actions": next_actions,
        "business_meaning": (
            "First-run status separates required setup blockers from recommended "
            "integration checks so a new user can see whether JIKUO is actually "
            "ready to use."
        ),
        "writes_performed": False,
        "write_allowed_by_command": False,
    }


def build_activation_item(project_root: Path) -> dict[str, Any]:
    report = activation_settings.build_status_report(project_root=project_root)
    available = report.get("status") in {"available", "review"}
    trigger_mode = str(report.get("desired_trigger_mode") or "ask")
    enforcement = str(report.get("effective_enforcement_level") or "instruction_only")
    strict_mount_status = str(report.get("strict_mount_status") or "unknown")
    status = (
        "missing"
        if not available
        else "review"
        if report.get("onboarding_required")
        or strict_mount_status == "degraded_instruction_only"
        else "ok"
    )
    next_actions = list(report.get("next_actions") or [])
    if not available:
        next_actions.append(
            "run `jikuo settings plan --trigger-mode ask` and review the activation defaults"
        )
    if trigger_mode == "mounted" and enforcement != "pre_turn_adapter":
        next_actions.append(
            "mounted mode is requested; install a strict adapter before treating it as guaranteed"
        )
    return item(
        key="activation_settings",
        title="Activation settings",
        status=status,
        meaning="The project-level source for semantic vs mounted behavior and enforcement posture.",
        current=(
            f"trigger_mode={trigger_mode}; enforcement={enforcement}; "
            f"strict_mount_status={strict_mount_status}; "
            f"onboarding_required={str(report.get('onboarding_required')).lower()}; "
            f"source={report.get('status')}"
        ),
        evidence_refs=[activation_settings.SETTINGS_REF],
        next_actions=next_actions,
        details=report,
    )


def managed_instruction_targets(project_root: Path) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for client, spec in instruction_files.CLIENT_TARGETS.items():
        target = project_root / spec["path"]
        exists = target.is_file()
        managed = False
        if exists:
            try:
                managed = instruction_files.has_managed_block(
                    target.read_text(encoding="utf-8")
                )
            except OSError:
                managed = False
        targets.append(
            {
                "client": client,
                "path_ref": spec["path"],
                "exists": exists,
                "managed_block_present": managed,
                "label": spec["label"],
            }
        )
    return targets


def build_instruction_item(project_root: Path) -> dict[str, Any]:
    targets = managed_instruction_targets(project_root)
    managed = [target for target in targets if target["managed_block_present"]]
    canonical = next(
        target for target in targets if target["client"] == instruction_files.CANONICAL_CLIENT
    )
    status = "ok" if canonical["managed_block_present"] else "review"
    current = (
        f"{len(managed)} managed instruction target(s); "
        f"canonical_present={str(canonical['managed_block_present']).lower()}"
    )
    return item(
        key="instruction_files",
        title="Instruction files",
        status=status,
        meaning="Client instruction files tell desktop Agents when and how to call JIKUO.",
        current=current,
        evidence_refs=[target["path_ref"] for target in targets if target["exists"]],
        next_actions=(
            []
            if status == "ok"
            else ["run `jikuo install --client <client>` to preview managed instruction blocks"]
        ),
        details={"targets": targets},
    )


def build_runtime_visibility_item(project_root: Path) -> dict[str, Any]:
    refs = [
        ".jikuo/runtime/last_card.md",
        ".jikuo/runtime/state_summary.json",
    ]
    existing = [ref for ref in refs if (project_root / ref).is_file()]
    status = "ok" if len(existing) == len(refs) else "review"
    return item(
        key="runtime_visibility",
        title="Runtime visibility",
        status=status,
        meaning="Out-of-band files let the user verify JIKUO state even when chat output is incomplete.",
        current=f"{len(existing)} of {len(refs)} runtime visibility files present",
        evidence_refs=existing,
        next_actions=(
            []
            if status == "ok"
            else ["run any card-producing JIKUO proposal, then verify with `jikuo show --last-card`"]
        ),
    )


def build_mcp_item(project_root: Path) -> dict[str, Any]:
    package_root = Path(__file__).resolve().parent
    server_ref = "src/jikuo/integrations/mcp/server.py"
    adapter_ref = "src/jikuo/integrations/mcp/adapter.py"
    server_present = (package_root / "integrations" / "mcp" / "server.py").is_file()
    adapter_present = (package_root / "integrations" / "mcp" / "adapter.py").is_file()
    sdk_importable = importlib.util.find_spec("mcp") is not None
    status = "ok" if server_present and adapter_present and sdk_importable else "review"
    return item(
        key="mcp_server",
        title="MCP server",
        status=status,
        meaning="MCP exposes JIKUO tools to compatible desktop AI clients.",
        current=(
            f"server_present={str(server_present).lower()}; "
            f"adapter_present={str(adapter_present).lower()}; "
            f"python_mcp_sdk_importable={str(sdk_importable).lower()}"
        ),
        evidence_refs=[server_ref, adapter_ref],
        next_actions=(
            []
            if status == "ok"
            else ["install project dependencies and run `jikuo-mcp --help` before client smoke tests"]
        ),
        details={
            "project_root": str(project_root),
            "server_present": server_present,
            "adapter_present": adapter_present,
            "python_mcp_sdk_importable": sdk_importable,
        },
    )


def build_project_context_item(project_root: Path) -> dict[str, Any]:
    ref = ".jikuo/project_context.yaml"
    present = (project_root / ref).is_file()
    return item(
        key="project_context",
        title="Project context bindings",
        status="ok" if present else "review",
        meaning="Project context binds reusable JIKUO templates to local docs and directories.",
        current="present" if present else "missing",
        evidence_refs=[ref] if present else [],
        next_actions=[] if present else ["create `.jikuo/project_context.yaml` before template import work"],
    )


def build_starter_policy_item(project_root: Path) -> dict[str, Any]:
    report = policy_store.inspect_policy_store(project_root=project_root)
    store_status = str(report.get("policy_store_status") or "missing")
    active_count = len(report.get("active_policy_refs") or [])
    status = "ok" if store_status == "active" and active_count else "review"
    return item(
        key="starter_policies",
        title="Starter policies",
        status=status,
        meaning="Starter policies give first-use projects useful report-only governance rules.",
        current=f"policy_store_status={store_status}; active_policy_count={active_count}",
        evidence_refs=[str(report.get("manifest_ref"))] if report.get("manifest_ref") else [],
        next_actions=(
            []
            if status == "ok"
            else ["run `jikuo-agent-flow propose --event initialize_jikuo` before expecting starter policy coverage"]
        ),
        details={
            "policy_store_status": store_status,
            "active_policy_count": active_count,
            "warnings": report.get("warnings") or [],
        },
    )


def build_guarded_write_item() -> dict[str, Any]:
    return item(
        key="guarded_writes",
        title="Guarded writes",
        status="ok",
        meaning="JIKUO separates no-write proposals from approval-bound durable writes.",
        current="confirmation and approval phrase are required for activation, install, policy, template, and task-session writes",
        evidence_refs=[
            activation_settings.SETTINGS_REF,
            ".jikuo/policies/",
            ".jikuo/task_sessions/",
        ],
        next_actions=["review proposed write sets before any apply command"],
    )


def build_configuration_review(*, project_root: Path | None = None) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    items = [
        build_activation_item(resolved_root),
        build_instruction_item(resolved_root),
        build_runtime_visibility_item(resolved_root),
        build_mcp_item(resolved_root),
        build_project_context_item(resolved_root),
        build_starter_policy_item(resolved_root),
        build_guarded_write_item(),
    ]
    first_run = build_first_run_status(items)
    worst = max(status_rank(entry["status"]) for entry in items)
    status = "ok" if worst == 0 else "review" if worst < 3 else "blocked"
    return {
        "schema": CONFIGURATION_REVIEW_SCHEMA,
        "status": status,
        "project_root": str(resolved_root),
        "write_allowed_by_command": False,
        "writes_performed": False,
        "summary": {
            "item_count": len(items),
            "ok_count": sum(1 for entry in items if entry["status"] == "ok"),
            "review_count": sum(1 for entry in items if entry["status"] == "review"),
            "missing_count": sum(1 for entry in items if entry["status"] == "missing"),
            "blocked_count": sum(1 for entry in items if entry["status"] == "blocked"),
            "first_run_status": first_run["status"],
            "first_run_blocker_count": first_run["blocker_count"],
        },
        "first_run": first_run,
        "items": items,
        "next_actions": [
            action
            for entry in items
            if entry["status"] != "ok"
            for action in entry.get("next_actions", [])
        ][:8],
    }


def format_review(report: dict[str, Any]) -> str:
    lines = [
        "# JIKUO Configuration Review",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Project root: `{report.get('project_root')}`",
        f"- Writes performed: `{str(report.get('writes_performed')).lower()}`",
        "",
        "## Summary",
        "",
    ]
    summary = report.get("summary") or {}
    for key in ("item_count", "ok_count", "review_count", "missing_count", "blocked_count"):
        lines.append(f"- {key}: `{summary.get(key, 0)}`")
    first_run = report.get("first_run") or {}
    lines.extend(
        [
            "",
            "## First Run",
            "",
            f"- Status: `{first_run.get('status')}`",
            f"- User usable: `{str(first_run.get('user_usable')).lower()}`",
            f"- Required complete: `{first_run.get('required_complete_count', 0)} of {first_run.get('required_total_count', 0)}`",
            f"- Blockers: `{first_run.get('blocker_count', 0)}`",
            f"- Recommended attention: `{first_run.get('recommended_attention_count', 0)}`",
        ]
    )
    if first_run.get("business_meaning"):
        lines.append(f"- Meaning: {first_run.get('business_meaning')}")
    if first_run.get("blockers"):
        lines.extend(["", "### Required Setup"])
        for step in first_run["blockers"]:
            lines.append(
                f"- `{step.get('key')}`: {step.get('title')} / {step.get('source_status')}"
            )
            if step.get("next_action"):
                lines.append(f"  next: {step.get('next_action')}")
    if first_run.get("next_actions"):
        lines.extend(["", "### First-run Next Actions"])
        lines.extend(f"- {action}" for action in first_run["next_actions"][:5])
    lines.extend(["", "## Configuration Items", ""])
    for entry in report.get("items") or []:
        lines.extend(
            [
                f"### {entry.get('title')}",
                "",
                f"- Status: `{entry.get('status')}`",
                f"- Meaning: {entry.get('meaning')}",
                f"- Current: {entry.get('current')}",
            ]
        )
        refs = entry.get("evidence_refs") or []
        if refs:
            lines.append(f"- Evidence refs: {', '.join(f'`{ref}`' for ref in refs)}")
        actions = entry.get("next_actions") or []
        if actions:
            lines.append(f"- Next action: {actions[0]}")
        lines.append("")
    if report.get("next_actions"):
        lines.extend(["## Next Actions", ""])
        lines.extend(f"- {action}" for action in report["next_actions"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review JIKUO first-use configuration.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("status", "review"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--project-root", type=Path, default=None)
        sub.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = build_configuration_review(project_root=args.project_root)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_review(report), end="")
    return 0 if report["status"] in {"ok", "review"} else 2


if __name__ == "__main__":
    sys.exit(main())
