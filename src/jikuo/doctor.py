"""Terminal diagnostics for JIKUO first-run readiness.

The doctor report is intentionally a projection over the Studio global status
read model. It should not scrape runtime files or duplicate frontend logic.
"""

from __future__ import annotations

import argparse
import json
import sys
from importlib import metadata
from pathlib import Path
from typing import Any

if __package__:
    from .studio import global_status
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jikuo.studio import global_status


DOCTOR_REPORT_SCHEMA = "jikuo.doctor_report.v0"
DOCTOR_CHECK_SCHEMA = "jikuo.doctor_check.v0"
STATUS_ORDER = {
    "ok": 0,
    "review": 1,
    "action_required": 2,
    "unavailable": 3,
}


def package_version() -> str:
    try:
        return metadata.version("jikuo")
    except metadata.PackageNotFoundError:
        return "source-tree-or-uninstalled"


def count_value(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def command_line(command: str) -> str:
    return command


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def check(
    check_id: str,
    *,
    title: str,
    status: str,
    summary: str,
    evidence: list[str] | None = None,
    next_actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema": DOCTOR_CHECK_SCHEMA,
        "check_id": check_id,
        "title": title,
        "status": status,
        "summary": summary,
        "evidence": evidence or [],
        "next_actions": next_actions or [],
    }


def step_action(step: dict[str, Any]) -> dict[str, Any]:
    guidance = step.get("guidance") or {}
    resolution = step.get("resolution") or {}
    return {
        "key": step.get("key"),
        "title": step.get("title"),
        "status": step.get("status"),
        "requirement": step.get("requirement"),
        "next_action": step.get("next_action"),
        "resolution_bucket": resolution.get("bucket"),
        "action_boundary": resolution.get("action_boundary"),
        "guidance_label": guidance.get("guidance_label"),
        "guidance_ref": guidance.get("doc_ref"),
    }


def build_install_check() -> dict[str, Any]:
    version = package_version()
    return check(
        "install_and_cli",
        title="Install and CLI",
        status="ok",
        summary="The JIKUO Python module is importable and the doctor command is executing.",
        evidence=[
            f"package_version={version}",
            f"python_executable={sys.executable}",
            command_line("jikuo --help"),
            command_line("jikuo doctor --format markdown"),
        ],
        next_actions=[
            {
                "label": "Verify entry points after install",
                "command": "jikuo --help",
            }
        ],
    )


def build_first_run_check(first_run: dict[str, Any]) -> dict[str, Any]:
    blocker_count = count_value(first_run.get("blocker_count"))
    recommended_count = count_value(first_run.get("recommended_attention_count"))
    status = "action_required" if blocker_count else "review" if recommended_count else "ok"
    actions = [step_action(item) for item in first_run.get("blockers") or []]
    if not actions:
        actions = [
            step_action(item)
            for item in first_run.get("recommended_steps") or []
            if item.get("status") not in {"ok", "complete", "available"}
        ]
    return check(
        "first_run_readiness",
        title="First-run Readiness",
        status=status,
        summary=(
            f"{first_run.get('status', 'unknown')}; "
            f"required {first_run.get('required_complete_count', 0)}/"
            f"{first_run.get('required_total_count', 0)} complete; "
            f"blockers={blocker_count}; recommended_attention={recommended_count}."
        ),
        evidence=[
            f"user_usable={str(first_run.get('user_usable')).lower()}",
            f"resolution_buckets={compact_json((first_run.get('resolution_buckets') or {}).get('bucket_counts', {}))}",
        ],
        next_actions=actions,
    )


def build_activation_check(activation: dict[str, Any]) -> dict[str, Any]:
    source_status = activation.get("source_status") or activation.get("status") or "unknown"
    strict_mount_status = activation.get("strict_mount_status") or "unknown"
    needs_review = source_status in {"missing", "needs_review", "review"}
    return check(
        "activation_settings",
        title="Activation Settings",
        status="action_required" if needs_review else "ok",
        summary=(
            f"source_status={source_status}; "
            f"trigger_mode={activation.get('desired_trigger_mode')}; "
            f"enforcement={activation.get('effective_enforcement_level')}; "
            f"strict_mount={strict_mount_status}."
        ),
        evidence=[
            f"settings_ref={activation.get('settings_ref', '.jikuo/activation_settings.yaml')}",
            f"adapter_status={activation.get('adapter_status', 'unknown')}",
            f"configuration_required={str(activation.get('configuration_required')).lower()}",
            f"required_user_decision_count={activation.get('required_user_decision_count', 0)}",
        ],
        next_actions=[
            {
                "label": "Preview activation settings update",
                "command": "jikuo settings plan --format markdown",
            }
        ]
        if needs_review
        else [],
    )


def build_policy_check(policy_summary: dict[str, Any]) -> dict[str, Any]:
    counts = policy_summary.get("summary_counts") or {}
    active_count = count_value(counts.get("active_policy_count"))
    starter_count = count_value(counts.get("starter_pack_count"))
    status = "ok" if active_count else "action_required"
    return check(
        "policy_management",
        title="Policy Management",
        status=status,
        summary=(
            f"active_policies={active_count}; "
            f"templates={counts.get('package_template_count', 0)}; "
            f"starter_packs={starter_count}."
        ),
        evidence=[
            f"read_model_status={policy_summary.get('status') or policy_summary.get('source_status')}",
            f"available_operations={policy_summary.get('available_operation_count', 0)}",
        ],
        next_actions=[
            {
                "label": "Inspect starter policy status",
                "command": "jikuo policy-management status --format markdown",
            }
        ]
        if not active_count
        else [],
    )


def build_document_check(document_mounts: dict[str, Any]) -> dict[str, Any]:
    missing_roles = count_value(document_mounts.get("missing_required_role_count"))
    status = "action_required" if missing_roles else "ok"
    return check(
        "document_rules",
        title="Document Rules",
        status=status,
        summary=(
            f"status={document_mounts.get('status')}; "
            f"configured_roles={document_mounts.get('role_count', 0)}; "
            f"completion_checks={document_mounts.get('checked_document_count', 0)}; "
            f"missing_required_roles={missing_roles}."
        ),
        evidence=[
            f"editable_sources={len(document_mounts.get('editable_configuration_sources') or [])}",
            f"getting_started={document_mounts.get('getting_started_doc_ref')}",
            f"document_management={document_mounts.get('document_management_doc_ref')}",
        ],
        next_actions=[
            {
                "label": "Preview Document Rules change",
                "command": "jikuo studio document-rules plan --format markdown",
            }
        ]
        if missing_roles
        else [],
    )


def build_studio_check(report: dict[str, Any]) -> dict[str, Any]:
    panel_count = len(report.get("panels") or [])
    return check(
        "studio",
        title="Studio",
        status="ok" if panel_count else "review",
        summary=(
            f"global_status={report.get('status')}; "
            f"panels={panel_count}; "
            f"actions={len(report.get('available_actions') or [])}."
        ),
        evidence=[
            f"source_schema={report.get('schema')}",
            command_line("jikuo studio status --format markdown"),
            command_line("jikuo studio serve --host 127.0.0.1 --port 8765"),
        ],
    )


def build_mcp_check(integrations: dict[str, Any]) -> dict[str, Any]:
    mcp = integrations.get("mcp") or {}
    tool_count = count_value(mcp.get("tool_count"))
    strict_proof = mcp.get("strict_mounted_proof")
    status = "ok" if tool_count else "review"
    if strict_proof and strict_proof != "proven":
        status = "review"
    return check(
        "mcp_server",
        title="MCP Server",
        status=status,
        summary=(
            f"tools={tool_count}; "
            f"sampling_probe={str(mcp.get('sampling_probe_exposed')).lower()}; "
            f"strict_mounted_proof={strict_proof}."
        ),
        evidence=[
            command_line("jikuo-mcp"),
            command_line("python -B -m jikuo.integrations.mcp.server"),
            f"policy_management_tools_exposed={str(mcp.get('policy_management_tools_exposed')).lower()}",
        ],
        next_actions=[
            {
                "label": "Configure an MCP client",
                "doc_ref": "docs/integrations/mcp_client_configuration_examples.md",
            }
        ],
    )


def build_runtime_check(runtime: dict[str, Any], release_limitations: dict[str, Any]) -> dict[str, Any]:
    counts = runtime.get("counts") or {}
    card_links = runtime.get("card_links") or {}
    missing_count = count_value(counts.get("missing_evidence_count"))
    status = "review" if missing_count else "ok"
    return check(
        "runtime_visibility",
        title="Runtime Visibility",
        status=status,
        summary=(
            f"status={runtime.get('status')}; "
            f"triggered_policies={counts.get('triggered_policy_count', 0)}; "
            f"missing_evidence={missing_count}."
        ),
        evidence=[
            f"last_card={card_links.get('last_card') or 'unavailable'}",
            f"history_card={card_links.get('history_card') or 'unavailable'}",
            f"limitations={release_limitations.get('doc_ref')}",
        ],
        next_actions=[
            {
                "label": "Inspect latest runtime card",
                "command": "jikuo show --last-card",
            },
            {
                "label": "Read missing-evidence limits",
                "doc_ref": "docs/user/limitations.md",
            },
        ]
        if missing_count
        else [],
    )


def overall_status(checks: list[dict[str, Any]]) -> str:
    if not checks:
        return "unavailable"
    return max(checks, key=lambda item: STATUS_ORDER.get(item.get("status"), 99))[
        "status"
    ]


def build_doctor_report(*, project_root: Path | None = None) -> dict[str, Any]:
    status_report = global_status.build_global_status(project_root=project_root)
    summaries = status_report.get("summaries") or {}
    configuration = summaries.get("configuration") or {}
    checks = [
        build_install_check(),
        build_first_run_check(configuration.get("first_run") or {}),
        build_activation_check(summaries.get("activation") or {}),
        build_policy_check(summaries.get("policy_management") or {}),
        build_document_check(summaries.get("document_mounts") or {}),
        build_studio_check(status_report),
        build_mcp_check(summaries.get("integrations") or {}),
        build_runtime_check(
            summaries.get("runtime") or {},
            summaries.get("release_limitations") or {},
        ),
    ]
    return {
        "schema": DOCTOR_REPORT_SCHEMA,
        "schema_version": DOCTOR_REPORT_SCHEMA,
        "status": overall_status(checks),
        "project_root": status_report.get("project_root"),
        "generated_at_utc": status_report.get("generated_at_utc"),
        "source_read_model": {
            "schema": status_report.get("schema"),
            "status": status_report.get("status"),
            "provider": "jikuo.studio.global_status.build_global_status",
        },
        "checks": checks,
        "diagnostics": status_report.get("diagnostics") or [],
        "pending_user_decisions": status_report.get("pending_user_decisions") or [],
        "card_links": status_report.get("card_links") or {},
        "privacy": status_report.get("privacy") or {},
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
    lines = [
        "# JIKUO Doctor",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Schema: `{report.get('schema')}`",
        f"- Project root: `{report.get('project_root')}`",
        f"- Source read model: `{(report.get('source_read_model') or {}).get('schema')}` / status=`{(report.get('source_read_model') or {}).get('status')}`",
        f"- Writes performed: `{str(report.get('writes_performed')).lower()}`",
        "",
        "## Checks",
        "",
    ]
    for item in report.get("checks") or []:
        lines.extend(
            [
                f"### {item.get('title')}",
                "",
                f"- Status: `{item.get('status')}`",
                f"- Summary: {item.get('summary')}",
            ]
        )
        if item.get("evidence"):
            lines.append("- Evidence:")
            lines.extend(f"  - {entry}" for entry in item.get("evidence") or [])
        if item.get("next_actions"):
            lines.append("- Next actions:")
            for action in item.get("next_actions") or []:
                label = action.get("label") or action.get("title") or action.get("key")
                details = []
                if action.get("command"):
                    details.append(f"command=`{action.get('command')}`")
                if action.get("next_action"):
                    details.append(f"next_action={action.get('next_action')}")
                if action.get("guidance_ref"):
                    details.append(f"guidance={action.get('guidance_ref')}")
                if action.get("doc_ref"):
                    details.append(f"doc={action.get('doc_ref')}")
                if action.get("resolution_bucket"):
                    details.append(f"bucket={action.get('resolution_bucket')}")
                suffix = f" ({'; '.join(details)})" if details else ""
                lines.append(f"  - {label}{suffix}")
        lines.append("")
    if report.get("diagnostics"):
        lines.extend(["## Diagnostics", ""])
        for item in report.get("diagnostics") or []:
            lines.append(
                f"- `{item.get('severity')}` / `{item.get('code')}`: {item.get('message')}"
            )
        lines.append("")
    lines.extend(["## Non-Effects", ""])
    lines.extend(f"- {item}" for item in report.get("non_effects") or [])
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run JIKUO terminal diagnostics.")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = build_doctor_report(project_root=args.project_root)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
