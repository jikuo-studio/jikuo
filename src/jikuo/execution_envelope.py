"""Shared execution-envelope projection for GUI and CLI governed turns."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any

try:
    from . import turn_anchor as turn_anchor_model
except ImportError:  # pragma: no cover - direct script compatibility
    import turn_anchor as turn_anchor_model


EXECUTION_ENVELOPE_SCHEMA = "jikuo.execution_envelope.v0"
HOST_SEMANTIC_INTENT_REF_SCHEMA = "jikuo.host_semantic_intent_ref.v0"

LIFECYCLE_STATES = (
    "received",
    "semantic_classified",
    "routed",
    "task_started",
    "executing",
    "verified",
    "completion_reviewed",
    "receipt_ready",
    "failed",
)

LIFECYCLE_STATE_BY_EVENT = {
    "conversation_turn": "routed",
    "task_start": "task_started",
    "task_continue": "executing",
    "evidence_review": "executing",
    "verification_review": "verified",
    "pre_delivery": "verified",
    "completion_review": "completion_reviewed",
    "handoff": "receipt_ready",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _stable_text_bytes(value: str) -> bytes:
    return value.encode("utf-8", errors="surrogatepass")


def stable_id(prefix: str, parts: list[str | None]) -> str:
    material = "|".join(part or "" for part in parts)
    digest = hashlib.sha256(_stable_text_bytes(material)).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        text = _string_or_none(item)
        if text and text not in output:
            output.append(text)
    return output


def _dict_or_none(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def lifecycle_state_for_event(event: str | None) -> str:
    return LIFECYCLE_STATE_BY_EVENT.get(str(event or ""), "received")


def normalize_lifecycle_state(value: Any, *, event: str | None = None) -> str:
    text = _string_or_none(value)
    if text in LIFECYCLE_STATES:
        return text
    return lifecycle_state_for_event(event)


def _project_root_ref(project_root: Path | str | None) -> str | None:
    if project_root is None:
        return None
    return str(Path(str(project_root)))


def _project_root_resolved(project_root: Path | str | None) -> str | None:
    if project_root is None:
        return None
    try:
        return str(Path(str(project_root)).resolve())
    except OSError:
        return str(Path(str(project_root)))


def _policy_contract_ref(raw: dict[str, Any]) -> dict[str, Any]:
    contract = raw.get("policy_contract")
    if not isinstance(contract, dict):
        return {}
    return {
        key: contract.get(key)
        for key in (
            "requested_outcome",
            "process_contract",
            "execution_boundary",
            "response_contract",
        )
        if contract.get(key) is not None
    }


def compact_host_semantic_intent_ref(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Return prompt-free semantic intent evidence supplied by the host AI."""

    raw = raw if isinstance(raw, dict) else {}
    anchor = turn_anchor_model.normalize_turn_anchor(raw.get("turn_anchor"))
    return {
        "schema": HOST_SEMANTIC_INTENT_REF_SCHEMA,
        "status": _string_or_none(raw.get("status")) or "unavailable",
        "provider": _string_or_none(raw.get("provider")) or "unavailable",
        "confidence": _string_or_none(raw.get("confidence")) or "unavailable",
        "lifecycle_event": _string_or_none(raw.get("lifecycle_event")),
        "policy_scopes": _string_list(raw.get("policy_scopes")),
        "policy_contract": _policy_contract_ref(raw),
        "turn_anchor_id": (
            anchor.get("anchor_id") if anchor.get("status") == "available" else None
        ),
        "non_effects": [
            "does_not_call_llm_provider",
            "does_not_infer_semantic_intent",
            "does_not_include_raw_prompt_or_transcript",
        ],
    }


def _prompt_digest(anchor: dict[str, Any]) -> dict[str, Any]:
    value = _string_or_none(anchor.get("prompt_sha256"))
    return {
        "algorithm": "sha256",
        "value": value,
        "status": (
            _string_or_none(anchor.get("prompt_digest_status"))
            or ("hash_only" if value else "not_available")
        ),
    }


def _private_turn_input_ref(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    raw = _dict_or_none(raw)
    if not raw:
        return None
    privacy = raw.get("privacy") if isinstance(raw.get("privacy"), dict) else {}
    return {
        "schema": _string_or_none(raw.get("schema"))
        or "jikuo.private_turn_input_index_ref.v0",
        "status": _string_or_none(raw.get("status")) or "unknown",
        "record_id": _string_or_none(raw.get("record_id")),
        "index_ref": _string_or_none(raw.get("index_ref")),
        "prompt_sha256": _string_or_none(raw.get("prompt_sha256")),
        "write_performed": bool(raw.get("write_performed")),
        "privacy": {
            "raw_prompt_persisted": bool(privacy.get("raw_prompt_persisted")),
            "raw_prompt_exposed_in_audit": False,
            "raw_transcript_exposed_in_audit": False,
        },
    }


def build_execution_envelope(
    *,
    project_root: Path | str | None = None,
    turn_anchor: dict[str, Any] | None = None,
    host_semantic_intent: dict[str, Any] | None = None,
    lifecycle_event: str | None = None,
    lifecycle_state: str | None = None,
    private_turn_input_ref: dict[str, Any] | None = None,
    runtime_refs: dict[str, Any] | None = None,
    git_observation: dict[str, Any] | None = None,
    receipt_ref: str | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    """Build a prompt-free envelope over existing turn and lifecycle fields."""

    anchor = turn_anchor_model.normalize_turn_anchor(turn_anchor)
    root_ref = _project_root_ref(project_root)
    root_resolved = _project_root_resolved(project_root)
    state = normalize_lifecycle_state(lifecycle_state, event=lifecycle_event)
    private_ref = _private_turn_input_ref(private_turn_input_ref)
    semantic_ref = compact_host_semantic_intent_ref(host_semantic_intent)
    envelope_id = stable_id(
        "env",
        [
            root_resolved,
            _string_or_none(anchor.get("anchor_id")),
            _string_or_none(anchor.get("session_id")),
            _string_or_none(anchor.get("turn_id")),
            _string_or_none(anchor.get("prompt_sha256")),
        ],
    )
    return {
        "schema": EXECUTION_ENVELOPE_SCHEMA,
        "envelope_id": envelope_id,
        "project_root": root_resolved,
        "project_root_ref": root_ref,
        "session_id": _string_or_none(anchor.get("session_id")),
        "turn_id": _string_or_none(anchor.get("turn_id")),
        "turn_anchor": anchor,
        "prompt_digest": _prompt_digest(anchor),
        "created_at_utc": _string_or_none(created_at_utc) or utc_now_iso(),
        "host_semantic_intent": semantic_ref,
        "lifecycle": {
            "state": state,
            "event": _string_or_none(lifecycle_event),
            "state_order": list(LIFECYCLE_STATES),
        },
        "links": {
            "private_turn_input_ref": private_ref,
            "runtime_refs": dict(runtime_refs or {}),
            "receipt_ref": _string_or_none(receipt_ref),
        },
        "git_observation": compact_git_observation_ref(git_observation),
        "privacy": {
            "raw_prompt_storage": "private_index" if private_ref else "none",
            "raw_prompt_exposed_in_audit": False,
            "raw_transcript_exposed_in_audit": False,
            "semantic_intent_source": semantic_ref["provider"],
        },
        "non_effects": [
            "does_not_store_raw_prompt_or_transcript",
            "does_not_call_host_ai",
            "does_not_infer_semantic_intent",
            "does_not_replace_turn_anchor",
            "does_not_perform_lifecycle_transition_by_itself",
        ],
    }


def compact_git_observation_ref(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    raw = raw if isinstance(raw, dict) else None
    if not raw:
        return None
    return {
        "schema": raw.get("schema"),
        "status": raw.get("status"),
        "source_kind": raw.get("source_kind"),
        "command_ref": raw.get("command_ref"),
        "observed_actual_write_count": raw.get("observed_actual_write_count", 0),
        "observed_actual_write_paths": raw.get("observed_actual_write_paths") or [],
        "attribution_status": raw.get("attribution_status"),
    }


def with_runtime_visibility_refs(
    envelope: dict[str, Any] | None,
    *,
    runtime_report: dict[str, Any],
) -> dict[str, Any] | None:
    if not isinstance(envelope, dict):
        return None
    output = dict(envelope)
    links = dict(output.get("links") or {})
    links["runtime_refs"] = {
        "last_card_ref": runtime_report.get("last_card_ref"),
        "state_summary_ref": runtime_report.get("state_summary_ref"),
        "history_ref": runtime_report.get("history_ref"),
        "history_state_summary_ref": runtime_report.get("history_state_summary_ref"),
    }
    output["links"] = links
    return output
