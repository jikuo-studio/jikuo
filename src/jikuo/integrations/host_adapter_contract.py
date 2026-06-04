"""Cross-client host adapter contract helpers.

This module is intentionally integration-neutral. It defines the small data
shape that Codex, Claude, Cursor, VS Code, or future wrappers/plugins can map
to before calling JIKUO. It does not run hooks, call models, decide policies, or
perform durable writes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jikuo import turn_anchor, work_profile


HOST_ADAPTER_TURN_INPUT_SCHEMA = "jikuo.host_adapter.turn_input.v0"
HOST_ADAPTER_TURN_RESULT_SCHEMA = "jikuo.host_adapter.turn_result.v0"

SUPPORTED_CLIENT_IDS = {
    "codex",
    "claude",
    "cursor",
    "vscode_copilot",
    "agent_sdk",
    "other",
}
SUPPORTED_TRIGGER_MODES = {"mounted", "semantic", "ask"}
SUPPORTED_ADAPTER_STATUSES = {"ok", "degraded", "blocked"}

REDACTED_USER_TURN = "<redacted_user_turn>"
REDACTED_PROMPT_ECHO = "<REDACTED_PROMPT_ECHO>"
SUMMARY_MAX_CHARS = 160


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _dict_or_none(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    return None


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        text = _string_or_none(item)
        if text and text not in output:
            output.append(text)
    return output


def _normalize_client_id(value: Any) -> str:
    text = (_string_or_none(value) or "other").lower().replace("-", "_")
    if text in SUPPORTED_CLIENT_IDS:
        return text
    return "other"


def _normalize_trigger_mode(value: Any) -> str:
    text = (_string_or_none(value) or "semantic").lower()
    if text in SUPPORTED_TRIGGER_MODES:
        return text
    return "semantic"


def _normalize_status(value: Any) -> str:
    text = (_string_or_none(value) or "degraded").lower()
    if text in SUPPORTED_ADAPTER_STATUSES:
        return text
    return "degraded"


def _compact_summary(value: Any) -> str | None:
    text = _string_or_none(value)
    if not text:
        return None
    compact = " ".join(text.split())
    if len(compact) <= SUMMARY_MAX_CHARS:
        return compact
    return compact[: SUMMARY_MAX_CHARS - 3].rstrip() + "..."


def _raw_turn_text(raw: dict[str, Any]) -> str | None:
    return (
        _string_or_none(raw.get("prompt"))
        or _string_or_none(raw.get("user_phrase"))
        or _string_or_none(raw.get("raw_prompt"))
        or _string_or_none(raw.get("raw_transcript"))
    )


def _redact_prompt_echo(value: str | None, raw_turn: str | None) -> str | None:
    if not value:
        return None
    if raw_turn and len(raw_turn) >= 8 and raw_turn in value:
        return value.replace(raw_turn, REDACTED_PROMPT_ECHO)
    return value


def normalize_turn_input(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize host input without persisting the raw prompt or transcript."""

    raw = raw if isinstance(raw, dict) else {}
    raw_turn = _raw_turn_text(raw)
    compact_summary = _compact_summary(raw.get("user_turn_summary"))
    if compact_summary:
        user_turn_summary = compact_summary
        user_turn_summary_status = "provided_compact"
    elif raw_turn:
        user_turn_summary = REDACTED_USER_TURN
        user_turn_summary_status = "provided_redacted"
    else:
        user_turn_summary = None
        user_turn_summary_status = "not_provided"

    raw_semantic_intent = (
        _dict_or_none(raw.get("host_semantic_intent"))
        or _dict_or_none(raw.get("hostSemanticIntent"))
    )
    anchor = turn_anchor.build_turn_anchor(
        client_id=raw.get("client_id") or raw.get("clientId"),
        client_event=raw.get("client_event") or raw.get("clientEvent"),
        session_id=raw.get("session_id") or raw.get("sessionId"),
        turn_id=raw.get("turn_id") or raw.get("turnId"),
        raw_prompt=raw_turn,
        user_turn_summary=user_turn_summary,
        user_turn_summary_status=user_turn_summary_status,
    )
    if raw_semantic_intent:
        raw_semantic_intent = dict(raw_semantic_intent)
        raw_semantic_intent.setdefault("turn_anchor", anchor)
    else:
        raw_semantic_intent = {
            "schema": work_profile.HOST_SEMANTIC_INTENT_SCHEMA,
            "status": "unavailable",
            "provider": "unavailable",
            "confidence": "unavailable",
            "policy_scopes": [],
            "constraints": [],
            "intent_slices": [],
            "policy_contract": {},
            "turn_anchor": anchor,
        }
    semantic_intent = work_profile.normalize_host_semantic_intent(raw_semantic_intent)

    return {
        "schema": HOST_ADAPTER_TURN_INPUT_SCHEMA,
        "client_id": _normalize_client_id(raw.get("client_id") or raw.get("clientId")),
        "client_event": _string_or_none(raw.get("client_event") or raw.get("clientEvent")),
        "project_root": _string_or_none(raw.get("project_root") or raw.get("projectRoot")),
        "project_root_ref": (
            str(Path(str(raw.get("project_root") or raw.get("projectRoot"))))
            if raw.get("project_root") or raw.get("projectRoot")
            else None
        ),
        "session_id": _string_or_none(raw.get("session_id") or raw.get("sessionId")),
        "turn_id": _string_or_none(raw.get("turn_id") or raw.get("turnId")),
        "trigger_mode": _normalize_trigger_mode(
            raw.get("trigger_mode") or raw.get("triggerMode")
        ),
        "user_turn_summary": user_turn_summary,
        "user_turn_summary_status": user_turn_summary_status,
        "raw_turn_present": bool(raw_turn),
        "turn_anchor": anchor,
        "host_semantic_intent": semantic_intent,
        "privacy": {
            "raw_prompt_persisted": False,
            "raw_transcript_persisted": False,
            "stored_input": user_turn_summary_status,
        },
        "non_effects": [
            "does_not_call_host_ai",
            "does_not_decide_policy_applicability",
            "does_not_perform_durable_writes",
            "does_not_store_raw_prompt_or_transcript",
        ],
    }


def normalize_turn_result(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize host adapter output for proof notes and client display."""

    raw = raw if isinstance(raw, dict) else {}
    raw_turn = _raw_turn_text(raw)
    semantic_status = _string_or_none(raw.get("semantic_intent_status")) or "unavailable"
    failure_summary = _redact_prompt_echo(
        _compact_summary(raw.get("failure_summary")),
        raw_turn,
    )
    return {
        "schema": HOST_ADAPTER_TURN_RESULT_SCHEMA,
        "status": _normalize_status(raw.get("status")),
        "semantic_intent_status": semantic_status,
        "card_links": _list_of_strings(raw.get("card_links")),
        "policy_trigger_summary": _dict_or_none(raw.get("policy_trigger_summary")) or {},
        "missing_evidence_summary": _dict_or_none(raw.get("missing_evidence_summary")) or {},
        "next_required_actions": _list_of_strings(raw.get("next_required_actions")),
        "failure_summary": failure_summary,
        "privacy": {
            "raw_prompt_persisted": False,
            "raw_transcript_persisted": False,
            "failure_summary_redacted": failure_summary != _compact_summary(raw.get("failure_summary")),
        },
        "non_effects": [
            "does_not_create_task_session",
            "does_not_write_policy_records",
            "does_not_satisfy_policy_evidence_by_itself",
        ],
    }


def codex_current_project_hook_path() -> dict[str, Any]:
    """Return the accepted Codex path and the remaining host-provider gap."""

    return {
        "schema": "jikuo.host_adapter.codex_path.v0",
        "current_path": "project_local_user_prompt_submit_hook",
        "accepted_capabilities": [
            "pre_turn_additional_context_visible",
            "in_process_jikuo_invocation",
            "visible_degradation_on_failure",
        ],
        "semantic_provider_status": "unavailable_until_wrapper_plugin_or_sampling_provider",
        "next_paths": [
            "codex_project_hook_transports_explicit_host_semantic_intent_when_available",
            "mcp_sampling_probe_supplies_client_mediated_semantic_intent_after_jikuo_call",
            "future_wrapper_or_plugin_controls_host_time_classifier_before_jikuo_call",
        ],
        "non_effects": [
            "does_not_claim_codex_user_prompt_submit_hook_can_access_model_reasoning_before_it_runs",
            "does_not_claim_host_time_ai_semantic_routing_is_accepted",
            "does_not_replace_full_lifecycle_strict_mounted_proof",
        ],
    }
