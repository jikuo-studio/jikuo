"""Project-level JIKUO activation settings.

The helper is intentionally small and dependency-light. It treats activation
settings as project-local governed state, so planning is read-only and writes
require explicit confirmation plus an approval phrase.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
from typing import Any

if __package__:
    from . import project_state
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import project_state


SETTINGS_SCHEMA = "jikuo.project_activation_settings.v0"
SETTINGS_PLAN_SCHEMA = "jikuo.activation_settings_plan.v0"
SETTINGS_RESULT_SCHEMA = "jikuo.activation_settings_result.v0"
SETTINGS_STATUS_SCHEMA = "jikuo.activation_settings_status.v0"
SETTINGS_REF = ".jikuo/activation_settings.yaml"
APPROVAL_TARGET = "JIKUO project activation settings"
APPROVAL_EFFECT = f"create or update {SETTINGS_REF}"
TRIGGER_MODE_CHOICES = ("ask", "semantic", "mounted")
ENFORCEMENT_LEVELS = ("mcp_only", "instruction_only", "pre_turn_adapter")
KNOWN_TOP_LEVEL_KEYS = {
    "schema",
    "desired_trigger_mode",
    "effective_enforcement_level",
    "strict_mounted_requires_adapter",
    "configuration_review",
    "field_provenance",
    "enabled_clients",
    "runtime_visibility",
    "guarded_writes",
    "compatibility",
}
CLIENT_INSTRUCTION_REFS = {
    "codex": "AGENTS.md",
    "claude-code": "CLAUDE.md",
    "cursor": ".cursorrules",
    "vscode-copilot": ".github/copilot-instructions.md",
    "continue": ".continuerules",
    "jikuo": "JIKUO.md",
}
REVIEWABLE_FIELDS = (
    "desired_trigger_mode",
    "effective_enforcement_level",
    "strict_mounted_requires_adapter",
)
DEFAULT_FIELD_VALUES = {
    "desired_trigger_mode": "ask",
    "effective_enforcement_level": "instruction_only",
    "strict_mounted_requires_adapter": True,
}
FIELD_MEANINGS = {
    "desired_trigger_mode": (
        "Controls whether JIKUO is invoked semantically, asks first, or expects "
        "mounted pre-turn execution."
    ),
    "effective_enforcement_level": (
        "Describes whether activation is instruction-only, MCP-only, or backed "
        "by a strict pre-turn adapter."
    ),
    "strict_mounted_requires_adapter": (
        "Prevents mounted mode from being treated as strict unless a host "
        "adapter actually calls JIKUO before each turn."
    ),
}
TRIGGER_MODE_DECISIONS = [
    {
        "value": "ask",
        "meaning": "Ask before the first governed turn; safest default.",
    },
    {
        "value": "semantic",
        "meaning": "Agent calls JIKUO when user intent appears governed.",
    },
    {
        "value": "mounted",
        "meaning": "Project requests every-turn JIKUO routing; strictness still needs a host adapter.",
    },
]


def quote_yaml(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return json.dumps(str(value), ensure_ascii=True)


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def parse_scalar(value: str) -> Any:
    raw = value.strip()
    if raw in {"true", "false"}:
        return raw == "true"
    if raw == "null":
        return None
    if raw.startswith('"') or raw.startswith("'"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw.strip("'\"")
    return raw


def normalize_trigger_mode(value: str | None, *, fallback: str = "ask") -> str:
    mode = (value or fallback).strip().lower().replace("_", "-")
    aliases = {
        "mounted-harness": "mounted",
        "natural": "semantic",
        "natural-language": "semantic",
    }
    mode = aliases.get(mode, mode)
    if mode not in TRIGGER_MODE_CHOICES:
        return fallback if fallback in TRIGGER_MODE_CHOICES else "ask"
    return mode


def normalize_enforcement_level(value: str | None) -> str:
    mode = (value or "instruction_only").strip().lower().replace("-", "_")
    if mode not in ENFORCEMENT_LEVELS:
        return "instruction_only"
    return mode


def settings_path(project_root: Path) -> Path:
    return project_root / SETTINGS_REF


def read_top_level_scalars(text: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for raw_line in text.splitlines():
        if not raw_line or raw_line.startswith((" ", "#", "-")):
            continue
        if ":" not in raw_line:
            continue
        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        if key:
            values[key] = parse_scalar(raw_value)
    return values


def preserved_unknown_blocks(text: str) -> list[str]:
    blocks: list[tuple[str | None, list[str]]] = []
    current_key: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        is_top_level_key = bool(line and not line.startswith((" ", "-", "#")) and ":" in line)
        if is_top_level_key:
            if current_lines:
                blocks.append((current_key, current_lines))
            current_key = line.split(":", 1)[0].strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_lines:
        blocks.append((current_key, current_lines))

    preserved: list[str] = []
    for key, lines in blocks:
        if key is None:
            continue
        if key not in KNOWN_TOP_LEVEL_KEYS and any(line.strip() for line in lines):
            preserved.append("\n".join(lines).rstrip())
    return preserved


def load_existing_settings(path: Path) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    if not path.is_file():
        return None, [], []
    text = path.read_text(encoding="utf-8")
    scalars = read_top_level_scalars(text)
    warnings: list[str] = []
    if scalars.get("schema") != SETTINGS_SCHEMA:
        warnings.append("unsupported activation settings schema")
    nested = read_nested_mapping_sections(
        text,
        sections={"configuration_review", "field_provenance"},
    )
    enabled_clients = read_list_mapping_section(text, section="enabled_clients")
    settings = {
        "schema": scalars.get("schema"),
        "desired_trigger_mode": normalize_trigger_mode(
            str(scalars.get("desired_trigger_mode") or "ask")
        ),
        "effective_enforcement_level": normalize_enforcement_level(
            str(scalars.get("effective_enforcement_level") or "instruction_only")
        ),
        "strict_mounted_requires_adapter": bool(
            scalars.get("strict_mounted_requires_adapter", True)
        ),
        "configuration_review": nested.get("configuration_review") or {},
        "field_provenance": nested.get("field_provenance") or {},
        "enabled_clients": enabled_clients,
    }
    return settings, warnings, preserved_unknown_blocks(text)


def read_nested_mapping_sections(
    text: str,
    *,
    sections: set[str],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {section: {} for section in sections}
    current_section: str | None = None
    current_child: str | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0:
            key = line.split(":", 1)[0].strip() if ":" in line else None
            current_section = key if key in sections and line.endswith(":") else None
            current_child = None
            continue
        if current_section is None or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if indent == 2 and raw_value == "":
            result[current_section][key] = {}
            current_child = key
            continue
        if indent == 2:
            result[current_section][key] = parse_scalar(raw_value)
            current_child = None
            continue
        if indent == 4 and current_child:
            child = result[current_section].setdefault(current_child, {})
            if isinstance(child, dict):
                child[key] = parse_scalar(raw_value)
    return result


def read_list_mapping_section(text: str, *, section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    in_section = False
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0:
            in_section = line == f"{section}:"
            current = None
            continue
        if not in_section:
            continue
        if indent == 2 and line.startswith("- "):
            current = {}
            items.append(current)
            remainder = line[2:].strip()
            if ":" in remainder:
                key, raw_value = remainder.split(":", 1)
                current[key.strip()] = parse_scalar(raw_value.strip())
            continue
        if indent == 4 and current is not None and ":" in line:
            key, raw_value = line.split(":", 1)
            current[key.strip()] = parse_scalar(raw_value.strip())
    return items


def field_source_for_value(field: str, value: Any) -> str:
    return (
        "user_reviewed_default"
        if value == DEFAULT_FIELD_VALUES.get(field)
        else "user_configured"
    )


def build_field_provenance(
    settings: dict[str, Any],
    *,
    reviewed_at_utc: str | None,
) -> dict[str, dict[str, Any]]:
    provenance: dict[str, dict[str, Any]] = {}
    for field in REVIEWABLE_FIELDS:
        value = settings.get(field)
        provenance[field] = {
            "value": value,
            "source": field_source_for_value(field, value),
            "review_status": "approved",
            "reviewed_at_utc": reviewed_at_utc,
            "requires_user_review": False,
            "meaning": FIELD_MEANINGS[field],
        }
    return provenance


def implicit_field_provenance() -> dict[str, dict[str, Any]]:
    return {
        field: {
            "value": value,
            "source": "implicit_default",
            "review_status": "unreviewed",
            "reviewed_at_utc": None,
            "requires_user_review": True,
            "meaning": FIELD_MEANINGS[field],
        }
        for field, value in DEFAULT_FIELD_VALUES.items()
    }


def unreviewed_file_field_provenance(settings: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        field: {
            "value": settings.get(field),
            "source": "legacy_file_without_review_metadata",
            "review_status": "unreviewed",
            "reviewed_at_utc": None,
            "requires_user_review": True,
            "meaning": FIELD_MEANINGS[field],
        }
        for field in REVIEWABLE_FIELDS
    }


def normalize_loaded_field_provenance(settings: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = settings.get("field_provenance")
    if not isinstance(raw, dict) or not raw:
        return unreviewed_file_field_provenance(settings)
    normalized: dict[str, dict[str, Any]] = {}
    for field in REVIEWABLE_FIELDS:
        record = raw.get(field)
        if not isinstance(record, dict):
            normalized[field] = unreviewed_file_field_provenance(settings)[field]
            continue
        normalized[field] = {
            "value": settings.get(field),
            "source": str(record.get("source") or "legacy_file_without_review_metadata"),
            "review_status": str(record.get("review_status") or "unreviewed"),
            "reviewed_at_utc": record.get("reviewed_at_utc"),
            "requires_user_review": bool(
                record.get("requires_user_review", record.get("review_status") != "approved")
            ),
            "meaning": str(record.get("meaning") or FIELD_MEANINGS[field]),
        }
    return normalized


def required_user_decisions_for(
    field_provenance: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    trigger_record = field_provenance.get("desired_trigger_mode") or {}
    if trigger_record.get("requires_user_review"):
        decisions.append(
            {
                "field": "desired_trigger_mode",
                "current_value": trigger_record.get("value", "ask"),
                "source": trigger_record.get("source", "implicit_default"),
                "review_status": trigger_record.get("review_status", "unreviewed"),
                "choices": TRIGGER_MODE_DECISIONS,
                "recommended_next_tool": "jikuo.plan_activation_settings_update",
                "meaning": FIELD_MEANINGS["desired_trigger_mode"],
            }
        )
    enforcement_record = field_provenance.get("effective_enforcement_level") or {}
    if enforcement_record.get("requires_user_review"):
        decisions.append(
            {
                "field": "effective_enforcement_level",
                "current_value": enforcement_record.get(
                    "value",
                    "instruction_only",
                ),
                "source": enforcement_record.get("source", "implicit_default"),
                "review_status": enforcement_record.get("review_status", "unreviewed"),
                "choices": list(ENFORCEMENT_LEVELS),
                "recommended_next_tool": "jikuo.plan_activation_settings_update",
                "meaning": FIELD_MEANINGS["effective_enforcement_level"],
            }
        )
    strict_adapter_record = field_provenance.get("strict_mounted_requires_adapter") or {}
    if strict_adapter_record.get("requires_user_review"):
        decisions.append(
            {
                "field": "strict_mounted_requires_adapter",
                "current_value": strict_adapter_record.get("value", True),
                "source": strict_adapter_record.get("source", "implicit_default"),
                "review_status": strict_adapter_record.get(
                    "review_status",
                    "unreviewed",
                ),
                "choices": [
                    {
                        "value": True,
                        "meaning": (
                            "Recommended: mounted mode is not strict unless a host "
                            "adapter actually calls JIKUO before each turn."
                        ),
                    }
                ],
                "recommended_next_tool": "jikuo.plan_activation_settings_update",
                "meaning": FIELD_MEANINGS["strict_mounted_requires_adapter"],
            }
        )
    return decisions


def client_record(client: str) -> dict[str, str]:
    return {
        "client": client,
        "instruction_ref": CLIENT_INSTRUCTION_REFS.get(client, "unknown"),
        "mcp_status": "unknown",
        "adapter_status": "not_available",
    }


def build_settings_draft(
    *,
    trigger_mode: str,
    effective_enforcement_level: str,
    clients: list[str] | None,
    reviewed_at_utc: str | None = None,
) -> dict[str, Any]:
    selected_clients = list(dict.fromkeys(clients or []))
    settings: dict[str, Any] = {
        "schema": SETTINGS_SCHEMA,
        "desired_trigger_mode": normalize_trigger_mode(trigger_mode),
        "effective_enforcement_level": normalize_enforcement_level(
            effective_enforcement_level
        ),
        "strict_mounted_requires_adapter": True,
        "enabled_clients": [client_record(client) for client in selected_clients],
        "runtime_visibility": {
            "last_card_ref": ".jikuo/runtime/last_card.md",
            "state_summary_ref": ".jikuo/runtime/state_summary.json",
            "show_client_links": True,
        },
        "guarded_writes": {
            "require_confirmation": True,
            "require_approval_phrase": True,
        },
        "compatibility": {
            "unknown_fields": "preserve",
            "writer": "jikuo.activation_settings",
        },
    }
    settings["configuration_review"] = {
        "review_status": "approved" if reviewed_at_utc else "pending_user_review",
        "reviewed_at_utc": reviewed_at_utc,
        "reviewed_by": "local_user" if reviewed_at_utc else None,
        "source": "guarded_activation_settings_apply" if reviewed_at_utc else "plan_only",
    }
    settings["field_provenance"] = build_field_provenance(
        settings,
        reviewed_at_utc=reviewed_at_utc,
    )
    if not reviewed_at_utc:
        for record in settings["field_provenance"].values():
            record["review_status"] = "pending_user_review"
            record["requires_user_review"] = True
    return settings


def render_settings_yaml(settings: dict[str, Any], preserved_blocks: list[str] | None = None) -> str:
    lines = [
        f"schema: {quote_yaml(settings['schema'])}",
        f"desired_trigger_mode: {quote_yaml(settings['desired_trigger_mode'])}",
        f"effective_enforcement_level: {quote_yaml(settings['effective_enforcement_level'])}",
        f"strict_mounted_requires_adapter: {quote_yaml(settings['strict_mounted_requires_adapter'])}",
        "configuration_review:",
        f"  review_status: {quote_yaml(settings['configuration_review']['review_status'])}",
        f"  reviewed_at_utc: {quote_yaml(settings['configuration_review']['reviewed_at_utc'])}",
        f"  reviewed_by: {quote_yaml(settings['configuration_review']['reviewed_by'])}",
        f"  source: {quote_yaml(settings['configuration_review']['source'])}",
        "field_provenance:",
    ]
    for field in REVIEWABLE_FIELDS:
        record = settings["field_provenance"][field]
        lines.extend(
            [
                f"  {field}:",
                f"    value: {quote_yaml(record['value'])}",
                f"    source: {quote_yaml(record['source'])}",
                f"    review_status: {quote_yaml(record['review_status'])}",
                f"    reviewed_at_utc: {quote_yaml(record['reviewed_at_utc'])}",
                f"    requires_user_review: {quote_yaml(record['requires_user_review'])}",
                f"    meaning: {quote_yaml(record['meaning'])}",
            ]
        )
    lines.append("enabled_clients:")
    for item in settings.get("enabled_clients", []):
        lines.append(f"  - client: {quote_yaml(item['client'])}")
        lines.append(f"    instruction_ref: {quote_yaml(item['instruction_ref'])}")
        lines.append(f"    mcp_status: {quote_yaml(item['mcp_status'])}")
        lines.append(f"    adapter_status: {quote_yaml(item['adapter_status'])}")
    lines.extend(
        [
            "runtime_visibility:",
            f"  last_card_ref: {quote_yaml(settings['runtime_visibility']['last_card_ref'])}",
            f"  state_summary_ref: {quote_yaml(settings['runtime_visibility']['state_summary_ref'])}",
            f"  show_client_links: {quote_yaml(settings['runtime_visibility']['show_client_links'])}",
            "guarded_writes:",
            f"  require_confirmation: {quote_yaml(settings['guarded_writes']['require_confirmation'])}",
            f"  require_approval_phrase: {quote_yaml(settings['guarded_writes']['require_approval_phrase'])}",
            "compatibility:",
            f"  unknown_fields: {quote_yaml(settings['compatibility']['unknown_fields'])}",
            f"  writer: {quote_yaml(settings['compatibility']['writer'])}",
        ]
    )
    for block in preserved_blocks or []:
        if block.strip():
            lines.extend(["", block.rstrip()])
    return "\n".join(lines).rstrip() + "\n"


def build_status_report(*, project_root: Path | None = None) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    path = settings_path(resolved_root)
    existing, warnings, _preserved = load_existing_settings(path)
    if existing is None:
        field_provenance = implicit_field_provenance()
        required_user_decisions = required_user_decisions_for(field_provenance)
        return {
            "schema": SETTINGS_STATUS_SCHEMA,
            "status": "missing",
            "project_root": str(resolved_root),
            "settings_ref": SETTINGS_REF,
            "desired_trigger_mode": "ask",
            "effective_enforcement_level": "instruction_only",
            "strict_mounted_requires_adapter": True,
            "adapter_status": "not_available",
            "strict_mount_status": "not_configured",
            "configuration_required": True,
            "onboarding_required": True,
            "field_provenance": field_provenance,
            "required_user_decisions": required_user_decisions,
            "recommended_next_tool": "jikuo.plan_activation_settings_update",
            "reason": "activation settings file is missing; defaults are in effect",
            "warnings": warnings,
            "next_actions": [
                "review activation settings before assuming JIKUO is mounted",
                "use jikuo.plan_activation_settings_update, then guarded apply after approval",
            ],
        }
    field_provenance = normalize_loaded_field_provenance(existing)
    required_user_decisions = required_user_decisions_for(field_provenance)
    onboarding_required = bool(required_user_decisions)
    status = "available" if not warnings and not onboarding_required else "review"
    desired_trigger_mode = existing["desired_trigger_mode"]
    enforcement_level = existing["effective_enforcement_level"]
    strict_mount_status = (
        "strict_pre_turn_adapter"
        if desired_trigger_mode == "mounted" and enforcement_level == "pre_turn_adapter"
        else "degraded_instruction_only"
        if desired_trigger_mode == "mounted"
        else "not_requested"
    )
    configuration_required = status == "review" or strict_mount_status == "degraded_instruction_only"
    return {
        "schema": SETTINGS_STATUS_SCHEMA,
        "status": status,
        "project_root": str(resolved_root),
        "settings_ref": SETTINGS_REF,
        "desired_trigger_mode": desired_trigger_mode,
        "effective_enforcement_level": enforcement_level,
        "strict_mounted_requires_adapter": existing["strict_mounted_requires_adapter"],
        "enabled_clients": existing.get("enabled_clients") or [],
        "adapter_status": "not_available"
        if enforcement_level != "pre_turn_adapter"
        else "configured_by_host",
        "strict_mount_status": strict_mount_status,
        "configuration_required": configuration_required,
        "onboarding_required": onboarding_required,
        "configuration_review": existing.get("configuration_review") or {},
        "field_provenance": field_provenance,
        "required_user_decisions": required_user_decisions,
        "recommended_next_tool": (
            "jikuo.plan_activation_settings_update"
            if onboarding_required
            else None
        ),
        "reason": "activation settings loaded",
        "warnings": warnings,
        "next_actions": (
            [
                "review activation settings provenance before continuing governed work",
                "use jikuo.plan_activation_settings_update, then guarded apply after approval",
            ]
            if onboarding_required
            else [
                "mounted mode is configured but not strict without a pre-turn adapter",
                "install or verify a host adapter before treating mounted mode as guaranteed",
            ]
            if strict_mount_status == "degraded_instruction_only"
            else []
        ),
    }


def resolve_trigger_mode(
    *,
    project_root: Path | None = None,
    requested_trigger_mode: str | None = None,
    default: str = "ask",
) -> tuple[str, str, dict[str, Any]]:
    if requested_trigger_mode:
        status = build_status_report(project_root=project_root)
        return normalize_trigger_mode(requested_trigger_mode, fallback=default), "command", status
    status = build_status_report(project_root=project_root)
    if status["status"] in {"available", "review"}:
        return (
            normalize_trigger_mode(str(status.get("desired_trigger_mode")), fallback=default),
            "project_activation_settings",
            status,
        )
    return normalize_trigger_mode(default, fallback=default), "default", status


def resolve_conversation_trigger_mode(
    *,
    project_root: Path | None = None,
    requested_trigger_mode: str | None = None,
) -> tuple[str, str, dict[str, Any]]:
    mode, source, status = resolve_trigger_mode(
        project_root=project_root,
        requested_trigger_mode=requested_trigger_mode,
        default="semantic",
    )
    if mode == "ask":
        return "semantic", source, status
    return mode, source, status


def build_plan(
    *,
    project_root: Path | None = None,
    trigger_mode: str = "ask",
    effective_enforcement_level: str = "instruction_only",
    clients: list[str] | None = None,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    path = settings_path(resolved_root)
    existing, warnings, preserved = load_existing_settings(path)
    status_before = build_status_report(project_root=resolved_root)
    draft = build_settings_draft(
        trigger_mode=trigger_mode,
        effective_enforcement_level=effective_enforcement_level,
        clients=clients,
    )
    planned_text = render_settings_yaml(draft, preserved)
    if existing:
        values_match = (
            existing.get("desired_trigger_mode") == draft["desired_trigger_mode"]
            and existing.get("effective_enforcement_level")
            == draft["effective_enforcement_level"]
            and existing.get("strict_mounted_requires_adapter")
            == draft["strict_mounted_requires_adapter"]
            and existing.get("enabled_clients") == draft["enabled_clients"]
        )
        operation = (
            "noop"
            if values_match and not status_before.get("onboarding_required")
            else "update"
        )
    else:
        operation = "create"
    return {
        "schema": SETTINGS_PLAN_SCHEMA,
        "status": "ok" if operation == "noop" else "review",
        "project_root": str(resolved_root),
        "settings_ref": SETTINGS_REF,
        "settings_path": str(path),
        "operation": operation,
        "write_allowed_by_command": False,
        "writes_performed": False,
        "approval_required": operation != "noop",
        "approval_target": APPROVAL_TARGET,
        "approval_effect": APPROVAL_EFFECT,
        "existing_settings_status": str(status_before.get("status") or "missing"),
        "onboarding_required_before": bool(status_before.get("onboarding_required")),
        "field_provenance_before": status_before.get("field_provenance") or {},
        "required_user_decisions": status_before.get("required_user_decisions") or [],
        "desired_trigger_mode": draft["desired_trigger_mode"],
        "effective_enforcement_level": draft["effective_enforcement_level"],
        "strict_mounted_requires_adapter": True,
        "planned_field_provenance": draft["field_provenance"],
        "enabled_clients": draft["enabled_clients"],
        "planned_size_bytes": len(planned_text.encode("utf-8")),
        "warnings": warnings,
        "refusal_reasons": [],
        "next_actions": (
            ["review activation settings, then rerun with apply + confirmation"]
            if operation != "noop"
            else ["activation settings already match the requested state"]
        ),
    }


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)


def apply_plan(
    *,
    project_root: Path | None = None,
    trigger_mode: str = "ask",
    effective_enforcement_level: str = "instruction_only",
    clients: list[str] | None = None,
    confirm_apply: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_plan(
        project_root=project_root,
        trigger_mode=trigger_mode,
        effective_enforcement_level=effective_enforcement_level,
        clients=clients,
    )
    refusals: list[str] = []
    if not confirm_apply:
        refusals.append("confirm_apply_required")
    if not approval_phrase:
        refusals.append("approval_phrase_required")
    if refusals:
        result = dict(plan)
        result["schema"] = SETTINGS_RESULT_SCHEMA
        result["status"] = "refused"
        result["refusal_reasons"] = refusals
        result["next_actions"] = [
            "rerun with --confirm-apply and --approval-phrase after reviewing the plan"
        ]
        return result, 2

    resolved_root = Path(plan["project_root"]).resolve()
    path = settings_path(resolved_root)
    _existing, _warnings, preserved = load_existing_settings(path)
    reviewed_at_utc = utc_now_iso()
    draft = build_settings_draft(
        trigger_mode=trigger_mode,
        effective_enforcement_level=effective_enforcement_level,
        clients=clients,
        reviewed_at_utc=reviewed_at_utc,
    )
    planned_text = render_settings_yaml(draft, preserved)
    write_performed = plan["operation"] != "noop" or bool(
        plan.get("onboarding_required_before")
    )
    if write_performed:
        write_text_atomic(path, planned_text)
    result = dict(plan)
    result["schema"] = SETTINGS_RESULT_SCHEMA
    result["status"] = "ok"
    result["write_allowed_by_command"] = True
    result["writes_performed"] = write_performed
    result["written_refs"] = [SETTINGS_REF] if write_performed else []
    result["approval_record"] = {
        "approval_target": APPROVAL_TARGET,
        "approval_effect": APPROVAL_EFFECT,
        "approval_phrase_recorded": True,
        "phrase": "<REDACTED>",
    }
    result["review_record"] = draft["configuration_review"]
    result["field_provenance"] = draft["field_provenance"]
    result["post_write_verification"] = build_status_report(project_root=resolved_root)
    result["next_actions"] = [
        "run jikuo show to verify effective activation settings",
        "rerun jikuo install without --trigger-mode to use project defaults",
    ]
    return result, 0


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "# JIKUO Activation Settings",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Project root: `{report.get('project_root')}`",
        f"- Settings ref: `{report.get('settings_ref')}`",
        f"- Desired trigger mode: `{report.get('desired_trigger_mode')}`",
        f"- Effective enforcement: `{report.get('effective_enforcement_level')}`",
        f"- Strict mounted requires adapter: `{str(report.get('strict_mounted_requires_adapter')).lower()}`",
        f"- Strict mounted status: `{report.get('strict_mount_status')}`",
        f"- Adapter status: `{report.get('adapter_status')}`",
    ]
    if report.get("onboarding_required") is not None:
        lines.append(f"- Onboarding required: `{str(report.get('onboarding_required')).lower()}`")
    if report.get("recommended_next_tool"):
        lines.append(f"- Recommended next tool: `{report.get('recommended_next_tool')}`")
    if report.get("operation"):
        lines.append(f"- Operation: `{report.get('operation')}`")
    if report.get("writes_performed") is not None:
        lines.append(f"- Writes performed: `{str(report.get('writes_performed')).lower()}`")
    clients = report.get("enabled_clients") or []
    if clients:
        lines.extend(["", "## Enabled Clients", ""])
        for item in clients:
            lines.append(
                f"- `{item.get('client')}`: instruction=`{item.get('instruction_ref')}`, "
                f"mcp=`{item.get('mcp_status')}`, adapter=`{item.get('adapter_status')}`"
            )
    if report.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {item}" for item in report["warnings"])
    if report.get("required_user_decisions"):
        lines.extend(["", "## Required User Decisions", ""])
        for decision in report["required_user_decisions"]:
            lines.append(
                f"- `{decision.get('field')}`: current=`{decision.get('current_value')}`, "
                f"source=`{decision.get('source')}`, review=`{decision.get('review_status')}`"
            )
            choices = decision.get("choices")
            if choices:
                if isinstance(choices[0], dict):
                    choice_values = [str(item.get("value")) for item in choices]
                else:
                    choice_values = [str(item) for item in choices]
                lines.append(f"  choices: {', '.join(f'`{item}`' for item in choice_values)}")
    if report.get("refusal_reasons"):
        lines.extend(["", "## Refusal Reasons", ""])
        lines.extend(f"- `{item}`" for item in report["refusal_reasons"])
    if report.get("next_actions"):
        lines.extend(["", "## Next Actions", ""])
        lines.extend(f"- {item}" for item in report["next_actions"])
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage JIKUO activation settings.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("status", "plan", "apply"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--project-root", type=Path, default=None)
        sub.add_argument("--format", choices=("markdown", "json"), default="markdown")
        if command in {"plan", "apply"}:
            sub.add_argument("--trigger-mode", choices=TRIGGER_MODE_CHOICES, default="ask")
            sub.add_argument(
                "--effective-enforcement-level",
                choices=ENFORCEMENT_LEVELS,
                default="instruction_only",
            )
            sub.add_argument("--client", action="append", default=[])
        if command == "apply":
            sub.add_argument("--confirm-apply", action="store_true")
            sub.add_argument("--approval-phrase", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "status":
        report = build_status_report(project_root=args.project_root)
        exit_code = 0
    elif args.command == "plan":
        report = build_plan(
            project_root=args.project_root,
            trigger_mode=args.trigger_mode,
            effective_enforcement_level=args.effective_enforcement_level,
            clients=args.client,
        )
        exit_code = 0
    else:
        report, exit_code = apply_plan(
            project_root=args.project_root,
            trigger_mode=args.trigger_mode,
            effective_enforcement_level=args.effective_enforcement_level,
            clients=args.client,
            confirm_apply=args.confirm_apply,
            approval_phrase=args.approval_phrase,
        )
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report), end="")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
