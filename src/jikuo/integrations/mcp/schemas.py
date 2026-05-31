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
    "semantic_intent_precondition",
    "conversation_turn_router",
    "configuration_review",
    "policy_suggestion_review",
    "task_start_processing",
    "task_session_completion_acceptance",
    "task_session_start_preview",
    "task_session_binding",
    "task_session_lifecycle_unavailable",
    "task_continue_refusal",
    "task_continue_status",
    "task_session_evidence_append",
    "policy_evidence_check",
    "policy_write_plan",
    "policy_evolution_plan",
    "policy_distribution_review",
    "policy_template_publication_plan",
    "policy_template_import_plan",
    "starter_manifest_publication_plan",
    "starter_policy_pack_init_plan",
)

HOST_SEMANTIC_INTENT_ARGUMENT_GUIDANCE = (
    "When the host AI has classified the turn, pass host_semantic_intent as "
    "compact classifier evidence: schema=jikuo.host_semantic_intent.v0, "
    "status=provided, provider=host_ai, policy_scopes limited to discussion, "
    "editing, and progress_summary, plus requested_outcome, execution_boundary, "
    "response_contract, and a short user_expression. Never include the raw "
    "prompt or transcript."
)

STAGE_A_TOOL_NAMES = (
    "jikuo.status",
    "jikuo.get_policy_management_status",
    "jikuo.get_runtime_status",
    "jikuo.get_runtime_status_card",
    "jikuo.get_display_card",
    "jikuo.propose_task_start",
    "jikuo.propose_policy_write_plan",
    "jikuo.propose_policy_evolution_plan",
    "jikuo.propose_policy_distribution_review",
    "jikuo.propose_policy_template_publication_plan",
    "jikuo.propose_starter_manifest_publication_plan",
    "jikuo.propose_policy_template_import_plan",
)

STAGE_B_TOOL_NAMES = (
    "jikuo.apply_task_session_evidence_update",
    "jikuo.apply_policy_evolution_write",
    "jikuo.apply_policy_template_activation",
    "jikuo.apply_policy_template_publication",
    "jikuo.apply_starter_manifest_publication",
)

STAGE_B1_TOOL_NAMES = ("jikuo.apply_task_session_evidence_update",)
STAGE_B2_TOOL_NAMES = ("jikuo.apply_policy_evolution_write",)
STAGE_B3_TOOL_NAMES = ("jikuo.apply_policy_template_activation",)
STAGE_B4_TOOL_NAMES = ("jikuo.apply_policy_template_publication",)
STAGE_B5_TOOL_NAMES = ("jikuo.apply_starter_manifest_publication",)

CONFIGURATION_TOOL_NAMES = (
    "jikuo.get_configuration_status",
    "jikuo.get_activation_settings",
    "jikuo.plan_activation_settings_update",
    "jikuo.apply_activation_settings_update",
)

ROUTER_TOOL_NAMES = (
    "jikuo.route_user_request",
    "jikuo.propose_policy_suggestions",
)

SAMPLING_TOOL_NAMES = ("jikuo.probe_sampling_semantic_intent",)

EXPOSED_TOOL_NAMES = (
    STAGE_A_TOOL_NAMES
    + CONFIGURATION_TOOL_NAMES
    + ROUTER_TOOL_NAMES
    + SAMPLING_TOOL_NAMES
    + STAGE_B1_TOOL_NAMES
    + STAGE_B2_TOOL_NAMES
    + STAGE_B3_TOOL_NAMES
    + STAGE_B4_TOOL_NAMES
    + STAGE_B5_TOOL_NAMES
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
                "client_display_links": RETURN,
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
    "jikuo.get_policy_management_status": _tool(
        name="jikuo.get_policy_management_status",
        description=(
            "Return the no-write Policy Management MVP read model for GUI/front-end "
            "surfaces: active policies, package policy templates, starter-pack manifests, "
            "and available guarded follow-up operations."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "starter_pack_id": RETURN,
        },
        output_fields={"policy_management_status": RETURN},
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
            "task_session_decision": RETURN,
            "task_session_defer_reason": REDACT_OPTIONAL,
        },
        output_fields={"work_profile": RETURN},
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
            "policy_trigger_event": RETURN,
            "policy_task_type": RETURN,
            "policy_jikuo_layer": RETURN,
            "policy_changed_path_pattern": RETURN,
            "policy_added_path_pattern": RETURN,
            "policy_work_profile_lifecycle_events": RETURN,
            "policy_work_profile_policy_scopes": RETURN,
            "policy_action_type": RETURN,
            "policy_evidence_type": RETURN,
        },
        output_fields={"work_profile": RETURN},
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
            "replacement_policy_ref": RETURN,
            "replacement_title": RETURN,
            "replacement_trigger_event": RETURN,
            "replacement_task_type": RETURN,
            "replacement_jikuo_layer": RETURN,
            "replacement_changed_path_pattern": RETURN,
            "replacement_added_path_pattern": RETURN,
            "replacement_action_type": RETURN,
            "replacement_evidence_type": RETURN,
        },
        output_fields={"work_profile": RETURN},
        card_returning=True,
    ),
    "jikuo.propose_policy_template_import_plan": _tool(
        name="jikuo.propose_policy_template_import_plan",
        description="Build a no-write reusable policy template import plan for user review.",
        input_fields={
            "project_root": LOCAL_ONLY,
            "template": RETURN,
        },
        output_fields={"work_profile": RETURN},
        card_returning=True,
    ),
    "jikuo.propose_policy_distribution_review": _tool(
        name="jikuo.propose_policy_distribution_review",
        description=(
            "Build a no-write policy distribution review from a policy id, source policy path, "
            "or natural-language policy query. This does not publish templates, update starter "
            "packs, or activate user-project policies."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "policy_ref": RETURN,
            "source_policy": LOCAL_ONLY,
            "policy_query": REDACT_OPTIONAL,
            "distribution_decision": RETURN,
            "source_project_ref": REDACT_OPTIONAL,
            "starter_pack_id": RETURN,
            "rationale": REDACT_OPTIONAL,
        },
        output_fields={
            "work_profile": RETURN,
            "policy_distribution_review": RETURN,
            "policy_distribution_source_resolution": RETURN,
        },
        card_returning=True,
    ),
    "jikuo.propose_policy_template_publication_plan": _tool(
        name="jikuo.propose_policy_template_publication_plan",
        description=(
            "Build a no-write package policy-template publication plan from a resolved "
            "policy id, source policy path, or natural-language policy query. This does "
            "not write package template files, update starter packs, or activate user "
            "project policies."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "policy_ref": RETURN,
            "source_policy": LOCAL_ONLY,
            "policy_query": REDACT_OPTIONAL,
            "distribution_decision": RETURN,
            "source_project_ref": REDACT_OPTIONAL,
            "starter_pack_id": RETURN,
            "rationale": REDACT_OPTIONAL,
            "target_dir": LOCAL_ONLY,
            "namespace": RETURN,
        },
        output_fields={
            "work_profile": RETURN,
            "policy_template_publication_plan": RETURN,
            "policy_distribution_source_resolution": RETURN,
        },
        card_returning=True,
    ),
    "jikuo.propose_starter_manifest_publication_plan": _tool(
        name="jikuo.propose_starter_manifest_publication_plan",
        description=(
            "Build a no-write starter-pack manifest publication plan for one package "
            "policy template ref. This does not activate user-project policies or run "
            "starter initialization."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "template_ref": RETURN,
            "starter_pack_id": RETURN,
        },
        output_fields={
            "work_profile": RETURN,
            "starter_manifest_publication_plan": RETURN,
        },
        card_returning=True,
    ),
    "jikuo.get_configuration_status": _tool(
        name="jikuo.get_configuration_status",
        description=(
            "Return the first-use and ongoing JIKUO configuration review as "
            "structured data plus a chat-ready governance card."
        ),
        input_fields={"project_root": LOCAL_ONLY},
        output_fields={
            "configuration_status": RETURN,
            "configuration_review": RETURN,
            "work_profile": RETURN,
        },
        card_returning=True,
        stage="C1",
        write_mode="no-write",
    ),
    "jikuo.get_activation_settings": _tool(
        name="jikuo.get_activation_settings",
        description=(
            "Return current project activation settings status without writing files."
        ),
        input_fields={"project_root": LOCAL_ONLY},
        output_fields={"activation_settings": RETURN},
        card_returning=True,
        stage="C1",
        write_mode="no-write",
    ),
    "jikuo.plan_activation_settings_update": _tool(
        name="jikuo.plan_activation_settings_update",
        description=(
            "Build a no-write activation settings update plan for user review. "
            "This does not write .jikuo/activation_settings.yaml."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "trigger_mode": RETURN,
            "effective_enforcement_level": RETURN,
            "clients": RETURN,
        },
        output_fields={"activation_settings_plan": RETURN},
        card_returning=True,
        stage="C1",
        write_mode="no-write",
    ),
    "jikuo.apply_activation_settings_update": _tool(
        name="jikuo.apply_activation_settings_update",
        description=(
            "Apply one explicitly approved project activation settings update. "
            "Requires confirm_apply=true and an approval_phrase after the user "
            "reviews the activation settings plan."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "trigger_mode": RETURN,
            "effective_enforcement_level": RETURN,
            "clients": RETURN,
            "confirm_apply": RETURN,
            "approval_phrase": REDACT_REQUIRED,
        },
        output_fields={
            "write_performed": RETURN,
            "target_result_schema": RETURN,
            "activation_settings_result": RETURN,
            "approval_record": RETURN,
            "refusal_reasons": RETURN,
            "written_refs": RETURN,
        },
        card_returning=True,
        stage="C2",
        write_mode="guarded-write",
    ),
    "jikuo.route_user_request": _tool(
        name="jikuo.route_user_request",
        description=(
            "Classify one user turn through the JIKUO conversation-turn router. "
            "Returns required obligations and MCP follow-up tool suggestions without "
            "writing governance files or storing raw transcripts. "
            f"{HOST_SEMANTIC_INTENT_ARGUMENT_GUIDANCE}"
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "user_phrase": REDACT_OPTIONAL,
            "host_semantic_intent": REDACT_OPTIONAL,
            "trigger_mode": RETURN,
            "task_title": REDACT_OPTIONAL,
            "summary": REDACT_OPTIONAL,
        },
        output_fields={
            "conversation_router": RETURN,
            "classified_obligations": RETURN,
            "required_followup_tools": RETURN,
            "mcp_followup_tools": RETURN,
            "work_profile": RETURN,
            "semantic_intent_evidence": RETURN,
        },
        card_returning=True,
        stage="R1",
        write_mode="no-write",
    ),
    "jikuo.propose_policy_suggestions": _tool(
        name="jikuo.propose_policy_suggestions",
        description=(
            "Review one user turn for proactive policy suggestions. Returns "
            "reviewable candidates and compact evidence without writing policy files "
            "or storing raw transcripts. "
            f"{HOST_SEMANTIC_INTENT_ARGUMENT_GUIDANCE}"
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "user_phrase": REDACT_OPTIONAL,
            "host_semantic_intent": REDACT_OPTIONAL,
            "trigger_mode": RETURN,
            "task_title": REDACT_OPTIONAL,
            "summary": REDACT_OPTIONAL,
        },
        output_fields={
            "conversation_router": RETURN,
            "policy_suggestion_review": RETURN,
            "policy_candidate_count": RETURN,
            "mcp_followup_tools": RETURN,
            "work_profile": RETURN,
            "semantic_intent_evidence": RETURN,
        },
        card_returning=True,
        stage="R1",
        write_mode="no-write",
    ),
    "jikuo.probe_sampling_semantic_intent": _tool(
        name="jikuo.probe_sampling_semantic_intent",
        description=(
            "Probe whether the current MCP client supports Sampling for compact "
            "semantic-intent classification, then route the user turn through "
            "JIKUO with the sampled host_semantic_intent when available. This "
            "is no-write and must not be treated as strict mounted proof."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "user_phrase": REDACT_OPTIONAL,
            "trigger_mode": RETURN,
            "task_title": REDACT_OPTIONAL,
            "summary": REDACT_OPTIONAL,
            "source_client": RETURN,
            "model_hint": RETURN,
            "max_tokens": RETURN,
        },
        output_fields={
            "conversation_router": RETURN,
            "classified_obligations": RETURN,
            "required_followup_tools": RETURN,
            "mcp_followup_tools": RETURN,
            "work_profile": RETURN,
            "semantic_intent_evidence": RETURN,
            "sampling_semantic_intent": RETURN,
            "host_semantic_intent": RETURN,
        },
        card_returning=True,
        stage="S1",
        write_mode="no-write",
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
            "replacement_trigger_event": RETURN,
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
    "jikuo.apply_policy_template_publication": _tool(
        name="jikuo.apply_policy_template_publication",
        description=(
            "Publish one explicitly approved project policy as a package policy template "
            "through the guarded agent_flow apply boundary. Requires source_policy, "
            "confirm_apply=true, and an approval_phrase after the publication plan is reviewed."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "source_policy": LOCAL_ONLY,
            "distribution_decision": RETURN,
            "source_project_ref": REDACT_OPTIONAL,
            "starter_pack_id": RETURN,
            "rationale": REDACT_OPTIONAL,
            "target_dir": LOCAL_ONLY,
            "namespace": RETURN,
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
        stage="B4",
        write_mode="guarded-write",
    ),
    "jikuo.apply_starter_manifest_publication": _tool(
        name="jikuo.apply_starter_manifest_publication",
        description=(
            "Publish one explicitly approved package policy template ref into a starter-pack "
            "manifest through the guarded agent_flow apply boundary. Requires template_ref, "
            "confirm_apply=true, and an approval_phrase after the manifest plan is reviewed."
        ),
        input_fields={
            "project_root": LOCAL_ONLY,
            "template_ref": RETURN,
            "starter_pack_id": RETURN,
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
        stage="B5",
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
