"""No-write work-profile projection for JIKUO user interactions.

The work profile is a compatibility projection over the current event model.
It does not trigger policies by itself and must not be treated as durable
evidence. Its job is to make the user-turn/task/review model explicit before
later policy-trigger work consumes it.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any


WORK_PROFILE_SCHEMA = "jikuo.work_profile.v0"

LIFECYCLE_EVENTS = {"conversation_turn", "task_start", "completion_review"}

COMPLETION_EVENTS = {
    "completion_review",
    "verification_review",
    "handoff",
}

DISCUSSION_TERMS = {
    "discuss",
    "explain",
    "what do you think",
    "design",
    "clarify",
    "review",
    "\u8ba8\u8bba",
    "\u89e3\u91ca",
    "\u600e\u4e48\u770b",
    "\u8bbe\u8ba1",
    "\u6f84\u6e05",
}

RESEARCH_TERMS = {
    "read",
    "inspect",
    "look at",
    "check",
    "analyze",
    "search",
    "browse",
    "\u770b\u4e00\u4e0b",
    "\u9605\u8bfb",
    "\u68c0\u7d22",
    "\u67e5\u7f51\u9875",
    "\u5206\u6790",
}

EDITING_TERMS = {
    "implement",
    "modify",
    "fix",
    "write",
    "commit",
    "continue work",
    "\u5b9e\u73b0",
    "\u4fee\u6539",
    "\u4fee\u590d",
    "\u63d0\u4ea4",
    "\u7ee7\u7eed\u5de5\u4f5c",
}

PROGRESS_TERMS = {
    "progress",
    "todo",
    "summary",
    "status",
    "\u8fdb\u5ea6",
    "\u4ee3\u529e",
    "\u603b\u7ed3",
}

CONFIG_TERMS = {
    "settings",
    "activation",
    "configure",
    "setup",
    "\u914d\u7f6e",
    "\u521d\u59cb\u5316",
}

POLICY_TERMS = {
    "policy",
    "rule",
    "governance",
    "\u89c4\u5219",
    "\u6cbb\u7406",
}


def normalize_lifecycle_event(raw_event: str | None, normalized_event: str | None) -> str:
    """Project the current tool-specific event into the three-step lifecycle."""

    event = normalized_event or raw_event or ""
    if event in LIFECYCLE_EVENTS:
        return event
    if event in COMPLETION_EVENTS:
        return "completion_review"
    if event == "conversation_turn":
        return "conversation_turn"
    if event in {"project_status", "configuration_review"}:
        return "conversation_turn"
    return "task_start"


def _lower_text(*values: str | None) -> str:
    return " ".join(value for value in values if value).lower()


def _contains_any(text: str, terms: set[str]) -> bool:
    for term in terms:
        if _contains_term(text, term):
            return True
    return False


def _contains_term(text: str, term: str) -> bool:
    if term.isascii():
        pattern = (
            r"(?<![A-Za-z0-9_-])"
            + re.escape(term.lower())
            + r"(?![A-Za-z0-9_-])"
        )
        return re.search(pattern, text) is not None
    return term in text


def _path_output_class(paths: list[str]) -> str | None:
    suffixes = {Path(path).suffix.lower() for path in paths}
    if suffixes & {".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go"}:
        return "code_change"
    if suffixes & {".md", ".rst", ".txt"}:
        return "doc_change"
    if suffixes & {".yaml", ".yml", ".json", ".toml"}:
        return "configuration_change"
    return None


def build_work_profile(
    *,
    raw_event: str | None,
    normalized_event: str | None,
    user_phrase: str | None = None,
    task_title: str | None = None,
    summary: str | None = None,
    task_type: str | None = None,
    jikuo_layer: str | None = None,
    changed_paths: list[str] | None = None,
    added_paths: list[str] | None = None,
    agent_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a no-write work-profile projection.

    The projection is intentionally conservative: hard signals such as changed
    paths and explicit task_type fields can increase scope, while ambiguous
    inputs fall back to discussion + editing so future policy matching does not
    silently no-op.
    """

    lifecycle_event = normalize_lifecycle_event(raw_event, normalized_event)
    paths = list(changed_paths or []) + list(added_paths or [])
    text = _lower_text(user_phrase, task_title, summary, task_type, jikuo_layer, raw_event)
    signals: list[dict[str, str]] = []

    intent_class = "discussion" if lifecycle_event == "conversation_turn" else "other"
    operation_class = "no_tool" if lifecycle_event == "conversation_turn" else "read_only"
    output_class = "answer" if lifecycle_event == "conversation_turn" else "plan"
    policy_scopes: list[str] = []

    if agent_hint:
        signals.append(
            {
                "signal": "agent_hint_present",
                "source": "agent_hint",
                "effect": "used_as_soft_context_only",
            }
        )

    if paths:
        intent_class = "editing"
        operation_class = "write_file"
        output_class = _path_output_class(paths) or "change"
        policy_scopes.append("editing")
        signals.append(
            {
                "signal": "changed_or_added_paths_present",
                "source": "changed_paths_or_added_paths",
                "effect": "operation_class=write_file",
            }
        )

    task_type_value = (task_type or "").lower()
    if task_type_value:
        signals.append(
            {
                "signal": "task_type_present",
                "source": "task_type",
                "effect": f"task_type={task_type_value}",
            }
        )
        if any(term in task_type_value for term in ("code", "edit", "change", "implementation")):
            intent_class = "editing"
            operation_class = "write_file"
            output_class = "code_change"
            if "editing" not in policy_scopes:
                policy_scopes.append("editing")
        elif "summary" in task_type_value or "progress" in task_type_value:
            intent_class = "progress_summary"
            output_class = "summary"
            if "progress_summary" not in policy_scopes:
                policy_scopes.append("progress_summary")

    if _contains_any(text, POLICY_TERMS) or str(raw_event or "").startswith("policy_"):
        intent_class = "policy_governance"
        output_class = "policy_candidate" if "candidate" in text else "plan"
        if "discussion" not in policy_scopes:
            policy_scopes.append("discussion")
        signals.append(
            {
                "signal": "policy_governance_terms",
                "source": "user_phrase_or_event",
                "effect": "intent_class=policy_governance",
            }
        )

    if _contains_any(text, CONFIG_TERMS) or normalized_event == "configuration_review":
        intent_class = "configuration"
        output_class = "configuration_review"
        if "discussion" not in policy_scopes:
            policy_scopes.append("discussion")
        signals.append(
            {
                "signal": "configuration_terms",
                "source": "user_phrase_or_event",
                "effect": "intent_class=configuration",
            }
        )

    if _contains_any(text, PROGRESS_TERMS):
        intent_class = "progress_summary"
        output_class = "summary"
        if "progress_summary" not in policy_scopes:
            policy_scopes.append("progress_summary")
        signals.append(
            {
                "signal": "progress_summary_terms",
                "source": "user_phrase_or_task_title",
                "effect": "intent_class=progress_summary",
            }
        )

    if _contains_any(text, RESEARCH_TERMS) and operation_class != "write_file":
        intent_class = "research"
        operation_class = "read_only"
        output_class = "answer"
        if "discussion" not in policy_scopes:
            policy_scopes.append("discussion")
        signals.append(
            {
                "signal": "research_or_read_terms",
                "source": "user_phrase_or_task_title",
                "effect": "operation_class=read_only",
            }
        )

    if _contains_any(text, EDITING_TERMS):
        intent_class = "editing"
        if operation_class != "write_file":
            operation_class = "local_command"
        output_class = "change"
        if "editing" not in policy_scopes:
            policy_scopes.append("editing")
        signals.append(
            {
                "signal": "editing_terms",
                "source": "user_phrase_or_task_title",
                "effect": "policy_scope=editing",
            }
        )

    if _contains_any(text, DISCUSSION_TERMS) and "discussion" not in policy_scopes:
        policy_scopes.append("discussion")
        signals.append(
            {
                "signal": "discussion_terms",
                "source": "user_phrase_or_task_title",
                "effect": "policy_scope=discussion",
            }
        )

    if intent_class == "discussion" and "discussion" not in policy_scopes:
        policy_scopes.append("discussion")

    fallback_expanded = False
    fallback_reason = "not_expanded"
    if not policy_scopes or intent_class == "other":
        policy_scopes = ["discussion", "editing"]
        fallback_expanded = True
        fallback_reason = "expanded_due_to_other_or_low_signal"

    confidence = "high" if paths or task_type_value else "medium" if signals else "low"
    if fallback_expanded:
        confidence = "low"

    return {
        "schema": WORK_PROFILE_SCHEMA,
        "raw_event": raw_event,
        "lifecycle_event": lifecycle_event,
        "primary": intent_class,
        "intent_class": intent_class,
        "operation_class": operation_class,
        "output_class": output_class,
        "policy_scopes": policy_scopes,
        "confidence": confidence,
        "fallback_expanded": fallback_expanded,
        "basis": {
            "agent_hint": agent_hint,
            "deterministic_signals": signals,
            "fallback": fallback_reason,
        },
        "non_effects": [
            "does not change policy evaluator behavior",
            "does not create or update .jikuo/policies/",
            "does not create task-session evidence",
        ],
    }
