"""Prompt-free turn-anchor projection helpers for JIKUO runtime evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Any


TURN_ANCHOR_SCHEMA = "jikuo.turn_anchor.v0"
MISSING_TURN_ANCHOR_REASON = "turn_anchor_not_supplied_by_host_adapter"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


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


def _digest_text(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(_stable_text_bytes(value)).hexdigest()


def _anchor_id_for(parts: list[str]) -> str | None:
    material = "|".join(part for part in parts if part)
    if not material:
        return None
    return "turn_" + hashlib.sha256(_stable_text_bytes(material)).hexdigest()[:16]


def _stable_text_bytes(value: str) -> bytes:
    """Encode host-supplied identity text for hashing without display effects."""

    return value.encode("utf-8", errors="surrogatepass")


def missing_turn_anchor(*, reason: str = MISSING_TURN_ANCHOR_REASON) -> dict[str, Any]:
    return {
        "schema": TURN_ANCHOR_SCHEMA,
        "status": "missing",
        "anchor_id": None,
        "gap_reason": reason,
        "natural_key_basis": [],
        "identity_strength": "none",
        "privacy": {
            "raw_prompt_persisted": False,
            "raw_transcript_persisted": False,
            "raw_prompt_included": False,
            "prompt_digest_only": False,
        },
        "non_effects": [
            "does_not_store_raw_prompt_or_transcript",
            "does_not_generate_ai_session_identity",
            "does_not_prove_host_ai_classification",
        ],
    }


def build_turn_anchor(
    *,
    client_id: str | None = None,
    client_event: str | None = None,
    session_id: str | None = None,
    turn_id: str | None = None,
    received_at_utc: str | None = None,
    raw_prompt: str | None = None,
    user_turn_summary: str | None = None,
    user_turn_summary_status: str | None = None,
) -> dict[str, Any]:
    """Build a non-AI turn anchor without persisting raw prompt text."""

    client_id = _string_or_none(client_id)
    client_event = _string_or_none(client_event)
    session_id = _string_or_none(session_id)
    turn_id = _string_or_none(turn_id)
    received_at_utc = _string_or_none(received_at_utc) or utc_now_iso()
    prompt_sha256 = _digest_text(raw_prompt)
    summary_status = _string_or_none(user_turn_summary_status) or "not_provided"
    compact_summary = (
        _string_or_none(user_turn_summary)
        if summary_status == "provided_compact"
        else None
    )

    natural_key_basis: list[str] = ["received_at_utc"]
    if client_id:
        natural_key_basis.append("client_id")
    if session_id:
        natural_key_basis.append("session_id")
    if turn_id:
        natural_key_basis.append("turn_id")
    if prompt_sha256:
        natural_key_basis.append("prompt_sha256")

    anchor_parts = [
        client_id or "",
        client_event or "",
        session_id or "",
        turn_id or "",
        received_at_utc,
        prompt_sha256 or "",
    ]
    if not session_id and not turn_id and not prompt_sha256:
        return missing_turn_anchor(reason="host_turn_identity_fields_missing")

    if session_id and turn_id and prompt_sha256:
        identity_strength = "host_turn_id_plus_prompt_hash"
    elif session_id and turn_id:
        identity_strength = "host_turn_id"
    elif prompt_sha256:
        identity_strength = "prompt_hash"
    else:
        identity_strength = "partial_host_turn_id"

    return {
        "schema": TURN_ANCHOR_SCHEMA,
        "status": "available",
        "anchor_id": _anchor_id_for(anchor_parts),
        "source_kind": "host_adapter",
        "client_id": client_id,
        "client_event": client_event,
        "session_id": session_id,
        "turn_id": turn_id,
        "received_at_utc": received_at_utc,
        "prompt_sha256": prompt_sha256,
        "prompt_digest_status": "hash_only" if prompt_sha256 else "not_available",
        "user_turn_summary": compact_summary,
        "user_turn_summary_status": summary_status,
        "natural_key_basis": natural_key_basis,
        "identity_strength": identity_strength,
        "gap_reason": None,
        "privacy": {
            "raw_prompt_persisted": False,
            "raw_transcript_persisted": False,
            "raw_prompt_included": False,
            "prompt_digest_only": bool(prompt_sha256),
        },
        "non_effects": [
            "does_not_store_raw_prompt_or_transcript",
            "does_not_generate_ai_session_identity",
            "does_not_prove_host_ai_classification",
        ],
    }


def normalize_turn_anchor(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return missing_turn_anchor()

    status = _string_or_none(raw.get("status")) or "available"
    if status != "available":
        return missing_turn_anchor(
            reason=_string_or_none(raw.get("gap_reason"))
            or MISSING_TURN_ANCHOR_REASON
        )

    client_id = _string_or_none(raw.get("client_id"))
    client_event = _string_or_none(raw.get("client_event"))
    session_id = _string_or_none(raw.get("session_id"))
    turn_id = _string_or_none(raw.get("turn_id"))
    received_at_utc = _string_or_none(raw.get("received_at_utc"))
    prompt_sha256 = _string_or_none(raw.get("prompt_sha256"))
    anchor_id = _string_or_none(raw.get("anchor_id")) or _anchor_id_for(
        [
            client_id or "",
            client_event or "",
            session_id or "",
            turn_id or "",
            received_at_utc or "",
            prompt_sha256 or "",
        ]
    )
    if not anchor_id:
        return missing_turn_anchor(reason="turn_anchor_has_no_stable_identity")

    natural_key_basis = _string_list(raw.get("natural_key_basis"))
    if not natural_key_basis:
        natural_key_basis = [
            item
            for item, value in [
                ("received_at_utc", received_at_utc),
                ("client_id", client_id),
                ("session_id", session_id),
                ("turn_id", turn_id),
                ("prompt_sha256", prompt_sha256),
            ]
            if value
        ]

    privacy = raw.get("privacy") if isinstance(raw.get("privacy"), dict) else {}
    return {
        "schema": TURN_ANCHOR_SCHEMA,
        "status": "available",
        "anchor_id": anchor_id,
        "source_kind": _string_or_none(raw.get("source_kind")) or "host_adapter",
        "client_id": client_id,
        "client_event": client_event,
        "session_id": session_id,
        "turn_id": turn_id,
        "received_at_utc": received_at_utc,
        "prompt_sha256": prompt_sha256,
        "prompt_digest_status": (
            _string_or_none(raw.get("prompt_digest_status"))
            or ("hash_only" if prompt_sha256 else "not_available")
        ),
        "user_turn_summary": _string_or_none(raw.get("user_turn_summary")),
        "user_turn_summary_status": (
            _string_or_none(raw.get("user_turn_summary_status")) or "not_provided"
        ),
        "natural_key_basis": natural_key_basis,
        "identity_strength": _string_or_none(raw.get("identity_strength")) or "unknown",
        "gap_reason": None,
        "privacy": {
            "raw_prompt_persisted": bool(privacy.get("raw_prompt_persisted"))
            if isinstance(privacy, dict)
            else False,
            "raw_transcript_persisted": bool(privacy.get("raw_transcript_persisted"))
            if isinstance(privacy, dict)
            else False,
            "raw_prompt_included": False,
            "prompt_digest_only": bool(prompt_sha256),
        },
        "non_effects": [
            "does_not_store_raw_prompt_or_transcript",
            "does_not_generate_ai_session_identity",
            "does_not_prove_host_ai_classification",
        ],
    }


def turn_anchor_from_work_profile(work_profile: dict[str, Any]) -> dict[str, Any]:
    basis = work_profile.get("basis") if isinstance(work_profile, dict) else {}
    if not isinstance(basis, dict):
        return missing_turn_anchor()
    semantic = basis.get("host_semantic_intent")
    if not isinstance(semantic, dict):
        return missing_turn_anchor()
    return normalize_turn_anchor(semantic.get("turn_anchor"))


def turn_anchor_for_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    direct = normalize_turn_anchor(proposal.get("turn_anchor"))
    if direct.get("status") == "available":
        return direct
    work_profile = proposal.get("work_profile")
    if isinstance(work_profile, dict):
        from_profile = turn_anchor_from_work_profile(work_profile)
        if from_profile.get("status") == "available":
            return from_profile
    policy_context = proposal.get("policy_context")
    if isinstance(policy_context, dict):
        context_profile = policy_context.get("work_profile")
        if isinstance(context_profile, dict):
            from_context = turn_anchor_from_work_profile(context_profile)
            if from_context.get("status") == "available":
                return from_context
    return direct


def display_label(anchor: dict[str, Any]) -> str:
    if anchor.get("status") != "available":
        return "missing"
    parts = []
    if anchor.get("session_id"):
        parts.append(f"session={anchor['session_id']}")
    if anchor.get("turn_id"):
        parts.append(f"turn={anchor['turn_id']}")
    if anchor.get("prompt_sha256"):
        parts.append(f"prompt_sha256={str(anchor['prompt_sha256'])[:12]}...")
    return " / ".join(parts) or str(anchor.get("anchor_id") or "available")
