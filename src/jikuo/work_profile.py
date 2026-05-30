"""No-write work-profile projection for JIKUO user interactions.

The work profile is a compatibility projection over the current event model.
It is not durable evidence and does not write policy records. Its job is to
make the user-turn/task/review model explicit so policy distribution can match
declared lifecycle and scope without depending only on brittle task labels.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any


WORK_PROFILE_SCHEMA = "jikuo.work_profile.v0"
HOST_SEMANTIC_INTENT_SCHEMA = "jikuo.host_semantic_intent.v0"
SEMANTIC_INTENT_CLASSIFICATION_EVIDENCE_SCHEMA = (
    "jikuo.semantic_intent_classification_evidence.v0"
)
MVP_POLICY_SCOPES = {"discussion", "editing", "progress_summary"}
USER_EXPRESSION_MAX_CHARS = 120
POLICY_CONTRACT_KEYS = (
    "requested_outcome",
    "process_contract",
    "execution_boundary",
    "response_contract",
)

LIFECYCLE_EVENTS = {"conversation_turn", "task_start", "completion_review"}

COMPLETION_EVENTS = {
    "completion_review",
    "verification_review",
    "pre_delivery",
    "handoff",
}

DISCUSSION_TERMS = {
    "align",
    "approach",
    "architecture",
    "brainstorm",
    "discuss",
    "explain",
    "clarify",
    "concept",
    "design",
    "meaning",
    "plan",
    "proposal",
    "review",
    "what do you think",
    "why",
    "\u5bf9\u9f50",
    "\u8ba8\u8bba",
    "\u89e3\u91ca",
    "\u600e\u4e48\u770b",
    "\u8bbe\u8ba1",
    "\u6f84\u6e05",
    "\u65b9\u6848",
    "\u601d\u8def",
    "\u67b6\u6784",
    "\u6982\u5ff5",
    "\u4e1a\u52a1\u610f\u4e49",
    "\u68b3\u7406",
    "\u5efa\u8bae",
    "\u8bc4\u4f30",
    "\u5ba1\u9605",
}

RESEARCH_TERMS = {
    "analyze",
    "audit",
    "browse",
    "check",
    "inspect",
    "investigate",
    "look at",
    "read",
    "research",
    "run tests",
    "search",
    "test",
    "validate",
    "verify",
    "\u5206\u6790",
    "\u67e5\u770b",
    "\u770b\u4e00\u4e0b",
    "\u68c0\u67e5",
    "\u68c0\u7d22",
    "\u67e5\u7f51\u9875",
    "\u8c03\u7814",
    "\u9605\u8bfb",
    "\u9a8c\u8bc1",
    "\u9a8c\u6536",
    "\u6d4b\u8bd5",
    "\u8dd1\u6d4b\u8bd5",
}

EDITING_TERMS = {
    "add",
    "adjust",
    "backfill",
    "change",
    "commit",
    "create",
    "delete",
    "document",
    "edit",
    "implement",
    "modify",
    "patch",
    "refactor",
    "register",
    "remove",
    "revise",
    "update docs",
    "update documentation",
    "update file",
    "update files",
    "fix",
    "write",
    "continue work",
    "write docs",
    "\u5f00\u53d1",
    "\u5b9e\u73b0",
    "\u7f16\u5199",
    "\u4fee\u6539",
    "\u6539\u4e00\u4e0b",
    "\u6539\u52a8",
    "\u6539\u9020",
    "\u4fee\u590d",
    "\u66f4\u65b0",
    "\u8c03\u6574",
    "\u91cd\u6784",
    "\u65b0\u589e",
    "\u6dfb\u52a0",
    "\u5220\u9664",
    "\u79fb\u9664",
    "\u521b\u5efa",
    "\u5199\u5165",
    "\u843d\u5730",
    "\u56de\u586b",
    "\u8865\u9f50",
    "\u6ce8\u518c",
    "\u63d0\u4ea4",
    "\u63d0\u4ea4\u53d8\u66f4",
    "\u7ee7\u7eed\u5de5\u4f5c",
}

PROGRESS_TERMS = {
    "backlog",
    "checklist",
    "next steps",
    "remaining",
    "progress",
    "progress summary",
    "status",
    "todo",
    "todos",
    "summary",
    "\u8fdb\u5ea6",
    "\u8fdb\u5c55",
    "\u4ee3\u529e",
    "\u4ee3\u529e\u6e05\u5355",
    "\u4efb\u52a1\u6e05\u5355",
    "\u5269\u4f59\u4ee3\u529e",
    "\u4e0b\u4e00\u6b65",
    "\u603b\u7ed3",
    "\u603b\u7ed3\u4e00\u4e0b",
    "\u76ee\u524d\u8fdb\u5ea6",
}

CONFIG_TERMS = {
    "activation",
    "client",
    "configure",
    "enable",
    "hook",
    "install",
    "mcp",
    "mount",
    "settings",
    "setup",
    "trust",
    "\u5ba2\u6237\u7aef",
    "\u63a5\u5165",
    "\u914d\u7f6e",
    "\u521d\u59cb\u5316",
    "\u6302\u8f7d",
    "\u542f\u7528",
    "\u8bbe\u7f6e",
    "\u5b89\u88c5",
    "\u9002\u914d",
}

POLICY_TERMS = {
    "candidate policy",
    "distribution",
    "evaluator",
    "policy",
    "policies",
    "rule",
    "rules",
    "trigger",
    "governance",
    "\u5019\u9009policy",
    "\u5019\u9009\u89c4\u5219",
    "\u5206\u53d1",
    "\u653f\u7b56",
    "\u89c4\u5219",
    "\u89e6\u53d1",
    "\u6cbb\u7406",
}

TEXT_EDIT_BLOCKING_TERMS = {
    "discussion only",
    "do not change",
    "do not commit",
    "do not edit",
    "do not modify",
    "do not write",
    "don't change",
    "don't commit",
    "don't edit",
    "don't modify",
    "don't write",
    "no change",
    "no commit",
    "no edit",
    "no file write",
    "no write",
    "no-write",
    "only discuss",
    "read only",
    "without editing",
    "\u4e0d\u52a8\u6587\u4ef6",
    "\u4e0d\u63d0\u4ea4",
    "\u4e0d\u5199\u6587\u4ef6",
    "\u4e0d\u8981\u52a8\u6587\u4ef6",
    "\u4e0d\u8981\u5199\u6587\u4ef6",
    "\u4e0d\u8981\u4fee\u6539",
    "\u4e0d\u8981\u6539",
    "\u4e0d\u8981\u6539\u4ee3\u7801",
    "\u4e0d\u8981\u63d0\u4ea4",
    "\u4e0d\u9700\u8981\u6539\u4ee3\u7801",
    "\u4ec5\u8ba8\u8bba",
    "\u53ea\u8ba8\u8bba",
    "\u53ea\u8bfb",
    "\u53ea\u89e3\u91ca",
    "\u53ea\u770b",
    "\u5148\u4e0d\u6539",
    "\u5148\u4e0d\u52a8",
}

EDIT_BLOCKING_CONSTRAINTS = {
    "discussion_only",
    "read_only",
    "no_change",
    "no_edit",
    "no_file_write",
    "no_write",
    "no_commit",
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


def _string_value(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip() and item.strip() not in output:
            output.append(item.strip())
    return output


def _policy_scope_list(value: Any) -> list[str]:
    output: list[str] = []
    for item in _string_list(value):
        normalized = item.lower().replace("-", "_")
        if normalized in MVP_POLICY_SCOPES and normalized not in output:
            output.append(normalized)
    return output


def _ordered_unique(values: list[str]) -> list[str]:
    output: list[str] = []
    for value in values:
        if value and value not in output:
            output.append(value)
    return output


def _first_string(*values: Any) -> str | None:
    for value in values:
        text = _string_value(value)
        if text:
            return text
    return None


def _short_user_expression(value: Any) -> str | None:
    text = _string_value(value)
    if not text:
        return None
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= USER_EXPRESSION_MAX_CHARS:
        return compact
    return compact[: USER_EXPRESSION_MAX_CHARS - 3].rstrip() + "..."


def _positive_index(value: Any, default: int) -> int:
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str) and value.strip().isdigit():
        number = int(value.strip())
        if number > 0:
            return number
    return default


def _normalize_confidence(value: Any) -> str:
    text = _string_value(value)
    if text in {"high", "medium", "low", "unavailable"}:
        return text
    return "medium"


def _normalize_intent_slices(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    slices: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        slice_index = _positive_index(item.get("index"), index)
        slice_id = _string_value(item.get("id")) or f"intent_{index}"
        slices.append(
            {
                "index": slice_index,
                "id": slice_id,
                "user_expression": _short_user_expression(item.get("user_expression")),
                "policy_scopes": _policy_scope_list(item.get("policy_scopes")),
                "intent_class": _string_value(item.get("intent_class")),
                "operation_class": _string_value(item.get("operation_class")),
                "output_class": _string_value(item.get("output_class")),
                "constraints": _string_list(item.get("constraints")),
                "requested_outcome": _string_value(item.get("requested_outcome")),
                "process_contract": _contract_list(item.get("process_contract")),
                "execution_boundary": _string_value(item.get("execution_boundary")),
                "response_contract": _contract_list(item.get("response_contract")),
                "rationale_summary": _string_value(item.get("rationale_summary")),
            }
        )
    return slices


def _contract_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return _string_list(value)
    text = _string_value(value)
    return [text] if text else []


def _first_contract_list(*values: Any) -> list[str]:
    for value in values:
        items = _contract_list(value)
        if items:
            return items
    return []


def _normalize_policy_contract(
    *,
    raw: dict[str, Any],
    nested_work_profile: dict[str, Any],
    primary_slice: dict[str, Any],
) -> dict[str, Any]:
    return {
        "requested_outcome": _first_string(
            raw.get("requested_outcome"),
            nested_work_profile.get("requested_outcome"),
            primary_slice.get("requested_outcome"),
        ),
        "process_contract": _first_contract_list(
            raw.get("process_contract"),
            nested_work_profile.get("process_contract"),
            primary_slice.get("process_contract"),
        ),
        "execution_boundary": _first_string(
            raw.get("execution_boundary"),
            nested_work_profile.get("execution_boundary"),
            primary_slice.get("execution_boundary"),
        ),
        "response_contract": _first_contract_list(
            raw.get("response_contract"),
            nested_work_profile.get("response_contract"),
            primary_slice.get("response_contract"),
        ),
    }


def normalize_host_semantic_intent(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize host/classifier semantic intent into a prompt-free projection."""

    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "schema": HOST_SEMANTIC_INTENT_SCHEMA,
            "status": "invalid",
            "provider": "unavailable",
            "confidence": "unavailable",
            "policy_scopes": [],
            "constraints": [],
            "intent_slices": [],
            "work_profile": {},
            "policy_contract": {},
            "errors": ["host_semantic_intent must be a JSON object"],
        }

    provider = _string_value(raw.get("provider")) or "host_ai"
    status = "heuristic_fallback" if provider == "heuristic_fallback" else "provided"
    confidence = _normalize_confidence(raw.get("confidence"))
    if confidence == "unavailable":
        status = "unavailable"

    nested_work_profile = raw.get("work_profile") if isinstance(raw.get("work_profile"), dict) else {}
    intent_slices = _normalize_intent_slices(raw.get("intent_slices"))
    primary_ref = _string_value(raw.get("primary_intent_ref"))
    primary_slice = next(
        (item for item in intent_slices if item.get("id") == primary_ref),
        intent_slices[0] if intent_slices else {},
    )

    scopes = _ordered_unique(
        _policy_scope_list(raw.get("policy_scopes"))
        + _policy_scope_list(nested_work_profile.get("policy_scopes"))
        + [
            scope
            for item in intent_slices
            for scope in _policy_scope_list(item.get("policy_scopes"))
        ]
    )
    constraints = _ordered_unique(
        _string_list(raw.get("constraints"))
        + [
            constraint
            for item in intent_slices
            for constraint in _string_list(item.get("constraints"))
        ]
    )
    work_profile = {
        "policy_scopes": scopes,
        "intent_class": _first_string(
            nested_work_profile.get("intent_class"),
            primary_slice.get("intent_class"),
        ),
        "operation_class": _first_string(
            nested_work_profile.get("operation_class"),
            primary_slice.get("operation_class"),
        ),
        "output_class": _first_string(
            nested_work_profile.get("output_class"),
            primary_slice.get("output_class"),
        ),
    }
    policy_contract = _normalize_policy_contract(
        raw=raw,
        nested_work_profile=nested_work_profile,
        primary_slice=primary_slice,
    )

    if not scopes and not any(work_profile.values()) and status != "unavailable":
        status = "invalid"

    return {
        "schema": HOST_SEMANTIC_INTENT_SCHEMA,
        "status": status,
        "source_client": _string_value(raw.get("source_client")),
        "source_event": _string_value(raw.get("source_event")),
        "provider": provider,
        "confidence": confidence,
        "lifecycle_event": _string_value(raw.get("lifecycle_event")),
        "multi_intent": bool(raw.get("multi_intent") or len(intent_slices) > 1),
        "primary_intent_ref": primary_ref,
        "policy_scopes": scopes,
        "constraints": constraints,
        "intent_slices": intent_slices,
        "work_profile": work_profile,
        "policy_contract": policy_contract,
        "rationale_summary": _string_value(raw.get("rationale_summary")),
    }


def _blocks_editing(constraints: list[str]) -> bool:
    return bool(set(constraints) & EDIT_BLOCKING_CONSTRAINTS)


def semantic_intent_classification_evidence_for(
    *,
    lifecycle_event: str,
    intent_class: str,
    operation_class: str,
    output_class: str,
    policy_scopes: list[str],
    semantic_intent: dict[str, Any] | None,
    fallback_expanded: bool,
) -> dict[str, Any]:
    """Project whether host/AI semantic classification is required and present."""

    semantic = semantic_intent if isinstance(semantic_intent, dict) else {}
    semantic_status = str(semantic.get("status") or "unavailable")
    provider = str(semantic.get("provider") or "unavailable")
    constraints = _string_list(semantic.get("constraints"))
    reasons: list[str] = []
    if "editing" in policy_scopes:
        reasons.append("editing_intent")
    if "progress_summary" in policy_scopes:
        reasons.append("progress_summary_intent")
    if operation_class in {"write_file", "local_command", "documentation_update"}:
        reasons.append("operation_may_change_project_state")
    if output_class in {"change", "code_change", "doc_change", "configuration_change"}:
        reasons.append("output_changes_project_state")
    if lifecycle_event in {"policy_evidence_record", "policy_feedback_record"}:
        reasons.append("guarded_policy_record_event")

    required = bool(reasons)
    if required and semantic_status == "provided":
        status = "ok"
    elif required and semantic_status == "heuristic_fallback":
        status = "fallback_only"
    elif required:
        status = "missing"
    elif semantic_status == "provided":
        status = "ok"
    elif semantic_status == "heuristic_fallback":
        status = "fallback_only"
    else:
        status = "not_required"

    if reasons:
        reason = reasons[0] if len(reasons) == 1 else ",".join(reasons)
    elif fallback_expanded:
        reason = "fallback_expanded_but_semantic_classification_not_required"
    elif _blocks_editing(constraints) or "discussion" in policy_scopes:
        reason = "discussion_only_or_no_file_write"
    else:
        reason = "low_risk_turn"

    followup = None
    if required and status in {"missing", "fallback_only"}:
        followup = "provide_host_semantic_intent_and_rerun_route"

    return {
        "schema": SEMANTIC_INTENT_CLASSIFICATION_EVIDENCE_SCHEMA,
        "evidence_type": "semantic_intent_classification_evidence",
        "action_type": "classify_user_intent_before_governed_work",
        "required": required,
        "status": status,
        "provider": provider,
        "semantic_intent_status": semantic_status,
        "reason": reason,
        "reasons": reasons,
        "followup": followup,
        "non_effects": [
            "does_not_call_an_llm_provider",
            "does_not_replace_policy_evaluator_conditions",
            "does_not_block_execution_in_report_only_mode",
        ],
    }


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
    host_semantic_intent: dict[str, Any] | None = None,
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
    semantic_intent = normalize_host_semantic_intent(host_semantic_intent)
    semantic_status = (
        semantic_intent.get("status") if isinstance(semantic_intent, dict) else "unavailable"
    )
    semantic_scopes = (
        list(semantic_intent.get("policy_scopes") or [])
        if isinstance(semantic_intent, dict)
        else []
    )
    semantic_constraints = (
        list(semantic_intent.get("constraints") or [])
        if isinstance(semantic_intent, dict)
        else []
    )
    semantic_blocks_editing = _blocks_editing(semantic_constraints)
    text_blocks_editing = _contains_any(text, TEXT_EDIT_BLOCKING_TERMS)
    effective_blocks_editing = semantic_blocks_editing or text_blocks_editing
    semantic_conflicts: list[dict[str, str]] = []

    if isinstance(semantic_intent, dict):
        signals.append(
            {
                "signal": "host_semantic_intent_present",
                "source": "host_semantic_intent",
                "effect": f"semantic_intent_status={semantic_status}",
            }
        )
        semantic_work_profile = semantic_intent.get("work_profile") or {}
        if semantic_work_profile.get("intent_class"):
            intent_class = str(semantic_work_profile["intent_class"])
        if semantic_work_profile.get("operation_class"):
            operation_class = str(semantic_work_profile["operation_class"])
        if semantic_work_profile.get("output_class"):
            output_class = str(semantic_work_profile["output_class"])
        policy_scopes.extend(semantic_scopes)

    if text_blocks_editing:
        signals.append(
            {
                "signal": "deterministic_edit_blocking_terms",
                "source": "user_phrase_or_task_title",
                "effect": "recorded deterministic no-edit constraint for fallback classification",
            }
        )

    if agent_hint:
        signals.append(
            {
                "signal": "agent_hint_present",
                "source": "agent_hint",
                "effect": "used_as_soft_context_only",
            }
        )

    if paths:
        if effective_blocks_editing:
            semantic_conflicts.append(
                {
                    "signal": "changed_or_added_paths_present",
                    "summary": "changed paths conflict with no-edit constraint",
                }
            )
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

    editing_terms_present = _contains_any(text, EDITING_TERMS)
    if editing_terms_present and effective_blocks_editing and not paths:
        semantic_conflicts.append(
            {
                "signal": "editing_terms_blocked_by_edit_constraint",
                "summary": (
                    "deterministic editing keywords were observed but no-edit "
                    "constraints forbid file edits"
                ),
            }
        )
        signals.append(
            {
                "signal": "editing_terms_blocked_by_edit_constraint",
                "source": "user_phrase_or_task_title",
                "effect": "kept non-editing scope because an edit-blocking constraint blocks editing",
            }
        )
    elif editing_terms_present:
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

    if isinstance(semantic_intent, dict):
        semantic_work_profile = semantic_intent.get("work_profile") or {}
        if semantic_work_profile.get("intent_class"):
            intent_class = str(semantic_work_profile["intent_class"])
        if semantic_work_profile.get("operation_class"):
            operation_class = str(semantic_work_profile["operation_class"])
        if semantic_work_profile.get("output_class"):
            output_class = str(semantic_work_profile["output_class"])
        combined_scopes = _ordered_unique(semantic_scopes + policy_scopes)
        if effective_blocks_editing and "editing" not in semantic_scopes and not paths:
            combined_scopes = [scope for scope in combined_scopes if scope != "editing"]
        policy_scopes = combined_scopes

    fallback_expanded = False
    fallback_reason = "not_expanded"
    if not policy_scopes or intent_class == "other":
        policy_scopes = ["discussion", "editing"]
        fallback_expanded = True
        fallback_reason = "expanded_due_to_other_or_low_signal"

    confidence = "high" if paths or task_type_value else "medium" if signals else "low"
    if isinstance(semantic_intent, dict) and semantic_intent.get("confidence") in {
        "high",
        "medium",
        "low",
    }:
        confidence = str(semantic_intent["confidence"])
    if fallback_expanded:
        confidence = "low"

    semantic_intent_evidence = semantic_intent_classification_evidence_for(
        lifecycle_event=lifecycle_event,
        intent_class=intent_class,
        operation_class=operation_class,
        output_class=output_class,
        policy_scopes=policy_scopes,
        semantic_intent=semantic_intent,
        fallback_expanded=fallback_expanded,
    )

    return {
        "schema": WORK_PROFILE_SCHEMA,
        "raw_event": raw_event,
        "lifecycle_event": lifecycle_event,
        "primary": intent_class,
        "intent_class": intent_class,
        "operation_class": operation_class,
        "output_class": output_class,
        "policy_scopes": policy_scopes,
        "policy_contract": (
            semantic_intent.get("policy_contract")
            if isinstance(semantic_intent, dict)
            else {}
        ),
        "semantic_intent_evidence": semantic_intent_evidence,
        "confidence": confidence,
        "fallback_expanded": fallback_expanded,
        "basis": {
            "agent_hint": agent_hint,
            "host_semantic_intent": semantic_intent
            or {
                "schema": HOST_SEMANTIC_INTENT_SCHEMA,
                "status": "unavailable",
                "provider": "unavailable",
                "confidence": "unavailable",
                "policy_scopes": [],
                "constraints": [],
                "intent_slices": [],
                "policy_contract": {},
            },
            "semantic_intent_status": semantic_status,
            "deterministic_signals": signals,
            "conflicts": semantic_conflicts,
            "fallback": fallback_reason,
        },
        "non_effects": [
            "does not create or update .jikuo/policies/",
            "does not create task-session evidence",
            "does not replace exact policy conditions",
        ],
    }
