"""Helpers for MCP Sampling semantic-intent proof tools."""

from __future__ import annotations

import json
from typing import Any

from ... import work_profile


SAMPLING_SEMANTIC_RESULT_SCHEMA = "jikuo.mcp_sampling_semantic_intent.v0"
SAMPLING_PROVIDER = "mcp_sampling"
SOURCE_EVENT = "sampling/createMessage"
DEFAULT_SOURCE_CLIENT = "mcp_client"

RAW_PROMPT_KEYS = {
    "exact_user_phrase",
    "prompt",
    "raw_prompt",
    "raw_transcript",
    "transcript",
    "user_phrase",
}


def build_sampling_prompt(
    *,
    user_phrase: str | None,
    task_title: str | None = None,
    summary: str | None = None,
) -> str:
    """Build a transient sampling prompt without asking the model to echo input."""

    return "\n".join(
        [
            "Classify the current user turn for JIKUO governance routing.",
            "Return only one JSON object. Do not use Markdown.",
            "Do not repeat, quote, or store the raw user prompt.",
            "Use this schema:",
            "{",
            '  "provider": "mcp_sampling",',
            '  "confidence": "high|medium|low|unavailable",',
            '  "multi_intent": true,',
            '  "primary_intent_ref": "intent_1",',
            '  "constraints": ["no_file_write"],',
            '  "policy_scopes": ["discussion", "editing", "progress_summary"],',
            '  "intent_slices": [',
            "    {",
            '      "id": "intent_1",',
            '      "policy_scopes": ["discussion"],',
            '      "intent_class": "design_discussion|implementation_request|progress_summary|configuration|policy_governance|other",',
            '      "operation_class": "read_only|code_change|documentation_update|configuration_change|summarize|no_change|other",',
            '      "output_class": "explanation|repository_change|summary|configuration|other",',
            '      "constraints": [],',
            '      "rationale_summary": "compact reason without quoting the prompt"',
            "    }",
            "  ],",
            '  "work_profile": {',
            '    "policy_scopes": ["discussion"],',
            '    "intent_class": "design_discussion",',
            '    "operation_class": "read_only",',
            '    "output_class": "explanation"',
            "  },",
            '  "rationale_summary": "compact reason without quoting the prompt"',
            "}",
            "If the user explicitly says not to edit files, include no_file_write and do not add editing solely from edit-like words.",
            "",
            f"Task title: {task_title or 'unavailable'}",
            f"Summary: {summary or 'unavailable'}",
            "User turn follows. Use it only for classification; do not echo it:",
            user_phrase or "unavailable",
        ]
    )


def _strip_raw_prompt_fields(value: Any) -> Any:
    if isinstance(value, list):
        return [_strip_raw_prompt_fields(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _strip_raw_prompt_fields(item)
            for key, item in value.items()
            if str(key) not in RAW_PROMPT_KEYS
        }
    return value


def _redact_prompt_echo(value: Any, *, user_phrase: str | None) -> Any:
    if not user_phrase or len(user_phrase.strip()) < 8:
        return value
    phrase = user_phrase.strip()
    if isinstance(value, list):
        return [_redact_prompt_echo(item, user_phrase=phrase) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _redact_prompt_echo(item, user_phrase=phrase)
            for key, item in value.items()
        }
    if isinstance(value, str) and phrase in value:
        return "<REDACTED_PROMPT_ECHO>"
    return value


def redact_prompt_echoes(value: Any, *, user_phrase: str | None) -> Any:
    """Redact exact prompt echoes from sampling probe responses."""

    return _redact_prompt_echo(value, user_phrase=user_phrase)


def _extract_json_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = [
            line
            for line in stripped.splitlines()
            if not line.strip().startswith("```")
        ]
        stripped = "\n".join(lines).strip()
    start = stripped.find("{")
    if start < 0:
        return None
    try:
        decoded, _ = decoder.raw_decode(stripped[start:])
    except json.JSONDecodeError:
        return None
    return decoded if isinstance(decoded, dict) else None


def sampling_result_text(result: Any) -> str:
    """Extract text from MCP CreateMessageResult-like objects or dicts."""

    content = getattr(result, "content", None)
    if content is None and isinstance(result, dict):
        content = result.get("content")
    if isinstance(content, list):
        parts = []
        for item in content:
            text = getattr(item, "text", None)
            if text is None and isinstance(item, dict):
                text = item.get("text")
            if text:
                parts.append(str(text))
        return "\n".join(parts)
    text = getattr(content, "text", None)
    if text is None and isinstance(content, dict):
        text = content.get("text")
    return str(text or "")


def sampling_model_name(result: Any) -> str | None:
    model = getattr(result, "model", None)
    if model is None and isinstance(result, dict):
        model = result.get("model")
    return str(model) if model else None


def sampling_stop_reason(result: Any) -> str | None:
    reason = getattr(result, "stopReason", None)
    if reason is None and isinstance(result, dict):
        reason = result.get("stopReason") or result.get("stop_reason")
    return str(reason) if reason else None


def unavailable_host_semantic_intent(
    *,
    reason: str,
    source_client: str = DEFAULT_SOURCE_CLIENT,
) -> dict[str, Any]:
    return {
        "schema": work_profile.HOST_SEMANTIC_INTENT_SCHEMA,
        "status": "unavailable",
        "source_client": source_client,
        "source_event": SOURCE_EVENT,
        "provider": SAMPLING_PROVIDER,
        "confidence": "unavailable",
        "policy_scopes": [],
        "constraints": [],
        "intent_slices": [],
        "work_profile": {},
        "rationale_summary": f"MCP Sampling semantic provider unavailable: {reason}",
    }


def normalize_sampling_semantic_intent(
    raw: dict[str, Any] | None,
    *,
    user_phrase: str | None,
    source_client: str = DEFAULT_SOURCE_CLIENT,
) -> tuple[dict[str, Any], list[str]]:
    """Normalize sampled JSON into the existing prompt-free host intent schema."""

    errors: list[str] = []
    if raw is None:
        return (
            unavailable_host_semantic_intent(
                reason="sampling_response_did_not_contain_json",
                source_client=source_client,
            ),
            ["sampling_response_did_not_contain_json"],
        )
    candidate = raw.get("host_semantic_intent") if isinstance(raw.get("host_semantic_intent"), dict) else raw
    cleaned = _redact_prompt_echo(
        _strip_raw_prompt_fields(candidate),
        user_phrase=user_phrase,
    )
    if not isinstance(cleaned, dict):
        return (
            unavailable_host_semantic_intent(
                reason="sampling_response_json_was_not_an_object",
                source_client=source_client,
            ),
            ["sampling_response_json_was_not_an_object"],
        )
    cleaned.setdefault("schema", work_profile.HOST_SEMANTIC_INTENT_SCHEMA)
    cleaned.setdefault("source_client", source_client)
    cleaned.setdefault("source_event", SOURCE_EVENT)
    cleaned.setdefault("provider", SAMPLING_PROVIDER)
    normalized = work_profile.normalize_host_semantic_intent(cleaned)
    if not isinstance(normalized, dict):
        return (
            unavailable_host_semantic_intent(
                reason="sampling_response_normalization_failed",
                source_client=source_client,
            ),
            ["sampling_response_normalization_failed"],
        )
    if normalized.get("status") == "invalid":
        errors.append("sampling_response_semantic_intent_invalid")
    return normalized, errors


def sampling_report(
    *,
    status: str,
    model: str | None = None,
    stop_reason: str | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema": SAMPLING_SEMANTIC_RESULT_SCHEMA,
        "provider": SAMPLING_PROVIDER,
        "status": status,
        "model": model,
        "stop_reason": stop_reason,
        "errors": list(errors or []),
    }


def attach_sampling_result(
    response: dict[str, Any],
    *,
    report: dict[str, Any],
    semantic_intent: dict[str, Any],
    user_phrase: str | None = None,
) -> dict[str, Any]:
    response["sampling_semantic_intent"] = report
    response["host_semantic_intent"] = semantic_intent
    data_details = response.get("data_details")
    if isinstance(data_details, dict):
        data_details["sampling_semantic_intent"] = report
        data_details["host_semantic_intent"] = semantic_intent
    return redact_prompt_echoes(response, user_phrase=user_phrase)


def parse_sampling_response(
    result: Any,
    *,
    user_phrase: str | None,
    source_client: str = DEFAULT_SOURCE_CLIENT,
) -> tuple[dict[str, Any], dict[str, Any]]:
    text = sampling_result_text(result)
    raw = _extract_json_object(text)
    semantic_intent, errors = normalize_sampling_semantic_intent(
        raw,
        user_phrase=user_phrase,
        source_client=source_client,
    )
    status = str(semantic_intent.get("status") or "unavailable")
    return semantic_intent, sampling_report(
        status=status,
        model=sampling_model_name(result),
        stop_reason=sampling_stop_reason(result),
        errors=errors,
    )
