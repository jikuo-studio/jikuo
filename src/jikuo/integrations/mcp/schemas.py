"""MCP tool schemas and response privacy classifications."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


ADAPTER_RESULT_SCHEMA = "jikuo.mcp_adapter_result.v0"
DISPLAY_DIRECTIVES_SCHEMA = "jikuo.mcp_display_directives.v0"
DISPLAY_VERIFICATION_SCHEMA = "jikuo.mcp_display_verification.v0"

RETURN = "return"
LOCAL_ONLY = "local_only"
REDACT_REQUIRED = "redact_required"
REDACT_OPTIONAL = "redact_optional"

LOCAL_STDIO_TRANSPORT = "local_stdio"
UNKNOWN_TRANSPORT = "unknown"

CARD_PRIORITY_ORDER = (
    "policy_runtime_status",
    "task_session_completion_acceptance",
    "task_session_start_preview",
)

STAGE_A_TOOL_NAMES = (
    "jikuo.status",
    "jikuo.get_runtime_status",
    "jikuo.get_runtime_status_card",
    "jikuo.get_display_card",
    "jikuo.propose_task_start",
    "jikuo.propose_policy_write_plan",
    "jikuo.propose_policy_evolution_plan",
    "jikuo.propose_policy_template_import_plan",
)

STAGE_B_TOOL_NAMES = (
    "jikuo.apply_task_session_evidence_update",
    "jikuo.apply_policy_evolution_write",
    "jikuo.apply_policy_template_activation",
)

STAGE_B1_TOOL_NAMES = ("jikuo.apply_task_session_evidence_update",)
STAGE_B2_TOOL_NAMES = ("jikuo.apply_policy_evolution_write",)
STAGE_B3_TOOL_NAMES = ("jikuo.apply_policy_template_activation",)

EXPOSED_TOOL_NAMES = (
    STAGE_A_TOOL_NAMES
    + STAGE_B1_TOOL_NAMES
    + STAGE_B2_TOOL_NAMES
    + STAGE_B3_TOOL_NAMES
)


def _tool(
    *,
    name: str,
    description: str,
    input_fields: dict[str, str],
    output_fields: dict[str, str] | None = None,
    card_returning: bool = False,
    stage: str = "A",
    write_mode: str = "no-write",
) -> dict[str, Any]:
    fields = {
        "schema": RETURN,
        "tool_name": RETURN,
        "stage": RETURN,
        "status": RETURN,
        "write_mode": RETURN,
        "transport": RETURN,
        "display": RETURN,
        "field_classification": RETURN,
        "data_details": RETURN,
        "debug_trace": LOCAL_ONLY,
        "local_paths": LOCAL_ONLY,
    }
    if card_returning:
        fields.update(
            {
                "card_markdown": RETURN,
                "chat_ready_markdown": RETURN,
                "runtime_snapshot_ref": RETURN,
                "display_verification": RETURN,
            }
        )
    if output_fields:
        fields.update(output_fields)
    return {
        "name": name,
        "stage": stage,
        "write_mode": write_mode,
        "card_returning": card_returning,
        "description": description,
        "input_fields": dict(input_fields),
        "response_fields": fields,
    }


TOOL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "jikuo.status": _tool(
        name="jikuo.status",
        description="Inspect project-local JIKUO policy-store status without writing files.",
        input_fields={"project_root": LOCAL_ONLY},
        output_fields={"policy_store_status": RETURN},
    ),
    "jikuo.get_runtime_status": _tool(
        name="jikuo.get_runtime_status",
        description="Return the latest JIKUO runtime status as structured data and display-ready Markdown.",
        input_fields={"project_root": LOCAL_ONLY},
        output_fields={"runtime_status": RETURN},
        card_returning=True,
    ),
    "jikuo.get_runtime_status_card": _tool(
        name="jikuo.get_runtime_status_card",
        description=(
            "Return only the chat-ready policy runtime status card. "
            "The card_markdown field is governance output and must be displayed verbatim."
        ),
        input_fields={"project_root": LOCAL_ONLY},
        card_returning=True,
    ),
    "jikuo.get_display_card": _tool(
        name="jikuo.get_display_card",
        description=(
            "Return the latest runtime display card. The card_markdown field is governance "
            "output and must be displayed verbatim."
        ),
        input_fields={"project_root": LOCAL_ONLY},
        card_returning=True,
    ),
    "jikuo.propose_task_start": _tool(
        name="jikuo.propose_task_start",
        description="Build a no-write governed task-start proposal and runtime card.",
        input_fields={
            "project_root": LOCAL_ONLY,
            "task_title": RETURN,
            "task_type": RETURN,
            "jikuo_layer": RETURN,
            "changed_paths": RETURN,
            "added_paths": RETURN,
            "summary": REDACT_OPTIONAL,
        },
        card_returning=True,
    ),
    "jikuo.propose_policy_write_plan": _tool(
        name="jikuo.propose_policy_write_plan",
        description="Build a no-write project policy write plan for user review.",
        input_fields={
            "project_root": LOCAL_ONLY,
            "policy_ref": RETURN,
            "policy_title": RETURN,
            "policy_source_ref": REDACT_OPTIONAL,
        },
        card_returning=True,
    ),
    "jikuo.propose_policy_evolution_plan": _tool(
        name="jikuo.propose_policy_evolution_plan",
        description="Build a no-write active-policy evolution plan for user review.",
        input_fields={
            "project_root": LOCAL_ONLY,
            "policy_ref": RETURN,
            "policy_evolution_operation": RETURN,
            "feedback_type": RETURN,
            "summary": REDACT_OPTIONAL,
            "policy_source_ref": REDACT_OPTIONAL,
        },
        card_returning=True,
    ),
    "jikuo.propose_policy_template_import_plan": _tool(
        name="jikuo.propose_policy_template_import_plan",
        description="Build a no-write reusable policy template import plan for user review.",
        input_fields={
            "project_root": LOCAL_ONLY,
            "template": RETURN,
        },
        card_returning=True,
    ),
    "jikuo.apply_task_session_evidence_update": _tool(
        name="jikuo.apply_task_session_evidence_update",
        description=(
            "Append one explicitly approved evidence item to an existing JIKUO "
            "task-session through the guarded agent_flow apply boundary. Requires "
            "confirm_apply=true and an approval_phrase."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "session_id": RETURN,
            "evidence_kind": RETURN,
            "evidence_ref": REDACT_OPTIONAL,
            "summary": REDACT_OPTIONAL,
            "evidence_status": RETURN,
            "owner_agent": RETURN,
            "confirm_apply": RETURN,
            "approval_phrase": REDACT_REQUIRED,
        },
        output_fields={
            "write_performed": RETURN,
            "target_result_schema": RETURN,
            "target_result": RETURN,
            "approval_boundary": RETURN,
            "refusal_reasons": RETURN,
        },
        card_returning=True,
        stage="B1",
        write_mode="guarded-write",
    ),
    "jikuo.apply_policy_evolution_write": _tool(
        name="jikuo.apply_policy_evolution_write",
        description=(
            "Apply one explicitly approved active-policy deprecation or supersession "
            "through the guarded agent_flow apply boundary. Requires proposal_ref, "
            "confirm_apply=true, and an approval_phrase matching the reviewed plan."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "policy_ref": RETURN,
            "proposal_ref": RETURN,
            "policy_evolution_operation": RETURN,
            "feedback_type": RETURN,
            "summary": REDACT_OPTIONAL,
            "policy_source_ref": REDACT_OPTIONAL,
            "replacement_policy_ref": RETURN,
            "replacement_title": RETURN,
            "replacement_task_type": RETURN,
            "replacement_jikuo_layer": RETURN,
            "replacement_changed_path_pattern": RETURN,
            "replacement_added_path_pattern": RETURN,
            "replacement_action_type": RETURN,
            "replacement_evidence_type": RETURN,
            "owner_agent": RETURN,
            "confirm_apply": RETURN,
            "approval_phrase": REDACT_REQUIRED,
        },
        output_fields={
            "write_performed": RETURN,
            "target_result_schema": RETURN,
            "target_result": RETURN,
            "proposal_binding": RETURN,
            "approval_boundary": RETURN,
            "refusal_reasons": RETURN,
        },
        card_returning=True,
        stage="B2",
        write_mode="guarded-write",
    ),
    "jikuo.apply_policy_template_activation": _tool(
        name="jikuo.apply_policy_template_activation",
        description=(
            "Activate one explicitly approved resolved policy template through the "
            "guarded agent_flow apply boundary. Requires template, confirm_apply=true, "
            "and an approval_phrase after the user reviews the template import plan."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "template": RETURN,
            "owner_agent": RETURN,
            "confirm_apply": RETURN,
            "approval_phrase": REDACT_REQUIRED,
        },
        output_fields={
            "write_performed": RETURN,
            "target_result_schema": RETURN,
            "target_result": RETURN,
            "approval_boundary": RETURN,
            "refusal_reasons": RETURN,
        },
        card_returning=True,
        stage="B3",
        write_mode="guarded-write",
    ),
}


def stage_a_tool_names() -> tuple[str, ...]:
    return STAGE_A_TOOL_NAMES


def build_tool_list() -> list[dict[str, Any]]:
    return [deepcopy(TOOL_DEFINITIONS[name]) for name in EXPOSED_TOOL_NAMES]


def tool_definition(tool_name: str) -> dict[str, Any]:
    try:
        return deepcopy(TOOL_DEFINITIONS[tool_name])
    except KeyError as exc:
        raise ValueError(f"unsupported MCP tool: {tool_name}") from exc


def build_display_directives() -> dict[str, Any]:
    return {
        "schema": DISPLAY_DIRECTIVES_SCHEMA,
        "must_show_verbatim": ["card_markdown"],
        "card_priority_order": list(CARD_PRIORITY_ORDER),
        "may_summarize": ["data_details"],
        "do_not_show": ["debug_trace"],
        "priority": "first_in_response",
        "reason": "policy_runtime_status is first-screen governance context when present",
    }


def response_field_classification(tool_name: str) -> dict[str, str]:
    return dict(tool_definition(tool_name)["response_fields"])


def transport_allows_local_only(transport: str | None) -> bool:
    return transport == LOCAL_STDIO_TRANSPORT
