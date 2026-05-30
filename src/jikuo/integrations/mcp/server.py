"""Official Python MCP SDK server wrapper for JIKUO MCP tools."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import Any, Callable

try:
    from mcp.server.fastmcp import Context as FastMCPContext  # type: ignore
except ImportError:  # pragma: no cover - server startup reports the SDK error.
    FastMCPContext = Any  # type: ignore

from . import adapter, sampling_semantic, schemas


SERVER_NAME = "JIKUO"
DISPLAY_CONTRACT = """\
CRITICAL DISPLAY CONTRACT:
The returned card_markdown field is JIKUO governance output and MUST be shown
to the user verbatim before any other commentary. Do not summarize, paraphrase,
or omit it. The display_verification field tells the user where to verify the
same card out-of-band if the client display fails.
"""

FastMCPFactory = Callable[..., Any]


def load_fastmcp_class() -> FastMCPFactory:
    """Load the official Python MCP SDK FastMCP server class lazily."""

    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "The official Python MCP SDK is required to run jikuo-mcp. "
            "Install the project with its declared dependencies, or install "
            "the SDK package with: python -m pip install mcp"
        ) from exc
    return FastMCP


def tool_description(tool: dict[str, Any]) -> str:
    """Return an MCP tool description with display rules embedded."""

    description = str(tool.get("description") or "").strip()
    if not tool.get("card_returning"):
        return description
    return f"{description}\n\n{DISPLAY_CONTRACT}".strip()


def _call(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    default_transport: str,
) -> dict[str, Any]:
    return adapter.call_tool(
        tool_name,
        arguments,
        transport=default_transport,
    )


def register_stage_a_tools(
    server: Any,
    *,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Register Stage A no-write MCP tools on a FastMCP server."""

    tool_definitions = {tool["name"]: tool for tool in adapter.list_tools()}

    @server.tool(
        name="jikuo.status",
        description=tool_description(tool_definitions["jikuo.status"]),
    )
    def jikuo_status(project_root: str | None = None) -> dict[str, Any]:
        return _call(
            "jikuo.status",
            {"project_root": project_root},
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.get_policy_management_status",
        description=tool_description(
            tool_definitions["jikuo.get_policy_management_status"]
        ),
    )
    def jikuo_get_policy_management_status(
        project_root: str | None = None,
        starter_pack_id: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.get_policy_management_status",
            {
                "project_root": project_root,
                "starter_pack_id": starter_pack_id,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.get_runtime_status",
        description=tool_description(tool_definitions["jikuo.get_runtime_status"]),
    )
    def jikuo_get_runtime_status(project_root: str | None = None) -> dict[str, Any]:
        return _call(
            "jikuo.get_runtime_status",
            {"project_root": project_root},
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.get_runtime_status_card",
        description=tool_description(tool_definitions["jikuo.get_runtime_status_card"]),
    )
    def jikuo_get_runtime_status_card(project_root: str | None = None) -> dict[str, Any]:
        return _call(
            "jikuo.get_runtime_status_card",
            {"project_root": project_root},
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.get_display_card",
        description=tool_description(tool_definitions["jikuo.get_display_card"]),
    )
    def jikuo_get_display_card(project_root: str | None = None) -> dict[str, Any]:
        return _call(
            "jikuo.get_display_card",
            {"project_root": project_root},
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.propose_task_start",
        description=tool_description(tool_definitions["jikuo.propose_task_start"]),
    )
    def jikuo_propose_task_start(
        project_root: str | None = None,
        task_title: str | None = None,
        task_type: str | None = None,
        jikuo_layer: str | None = None,
        changed_paths: list[str] | None = None,
        added_paths: list[str] | None = None,
        summary: str | None = None,
        owner_agent: str | None = None,
        work_routing_category: str | None = None,
        work_routing_summary: str | None = None,
        task_session_decision: str | None = None,
        task_session_defer_reason: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.propose_task_start",
            {
                "project_root": project_root,
                "task_title": task_title,
                "task_type": task_type,
                "jikuo_layer": jikuo_layer,
                "changed_paths": changed_paths or [],
                "added_paths": added_paths or [],
                "summary": summary,
                "owner_agent": owner_agent,
                "work_routing_category": work_routing_category,
                "work_routing_summary": work_routing_summary,
                "task_session_decision": task_session_decision,
                "task_session_defer_reason": task_session_defer_reason,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.propose_policy_write_plan",
        description=tool_description(tool_definitions["jikuo.propose_policy_write_plan"]),
    )
    def jikuo_propose_policy_write_plan(
        project_root: str | None = None,
        policy_ref: str | None = None,
        policy_title: str | None = None,
        policy_source_ref: str | None = None,
        policy_trigger_event: str | None = None,
        policy_task_type: str | None = None,
        policy_jikuo_layer: str | None = None,
        policy_changed_path_pattern: str | None = None,
        policy_added_path_pattern: str | None = None,
        policy_work_profile_lifecycle_events: list[str] | None = None,
        policy_work_profile_policy_scopes: list[str] | None = None,
        policy_action_type: str | None = None,
        policy_evidence_type: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.propose_policy_write_plan",
            {
                "project_root": project_root,
                "policy_ref": policy_ref,
                "policy_title": policy_title,
                "policy_source_ref": policy_source_ref,
                "policy_trigger_event": policy_trigger_event,
                "policy_task_type": policy_task_type,
                "policy_jikuo_layer": policy_jikuo_layer,
                "policy_changed_path_pattern": policy_changed_path_pattern,
                "policy_added_path_pattern": policy_added_path_pattern,
                "policy_work_profile_lifecycle_events": (
                    policy_work_profile_lifecycle_events or []
                ),
                "policy_work_profile_policy_scopes": (
                    policy_work_profile_policy_scopes or []
                ),
                "policy_action_type": policy_action_type,
                "policy_evidence_type": policy_evidence_type,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.propose_policy_evolution_plan",
        description=tool_description(
            tool_definitions["jikuo.propose_policy_evolution_plan"]
        ),
    )
    def jikuo_propose_policy_evolution_plan(
        project_root: str | None = None,
        policy_ref: str | None = None,
        policy_evolution_operation: str | None = None,
        feedback_type: str | None = None,
        summary: str | None = None,
        policy_source_ref: str | None = None,
        replacement_policy_ref: str | None = None,
        replacement_title: str | None = None,
        replacement_trigger_event: str | None = None,
        replacement_task_type: str | None = None,
        replacement_jikuo_layer: str | None = None,
        replacement_changed_path_pattern: str | None = None,
        replacement_added_path_pattern: str | None = None,
        replacement_action_type: str | None = None,
        replacement_evidence_type: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.propose_policy_evolution_plan",
            {
                "project_root": project_root,
                "policy_ref": policy_ref,
                "policy_evolution_operation": policy_evolution_operation,
                "feedback_type": feedback_type,
                "summary": summary,
                "policy_source_ref": policy_source_ref,
                "replacement_policy_ref": replacement_policy_ref,
                "replacement_title": replacement_title,
                "replacement_trigger_event": replacement_trigger_event,
                "replacement_task_type": replacement_task_type,
                "replacement_jikuo_layer": replacement_jikuo_layer,
                "replacement_changed_path_pattern": replacement_changed_path_pattern,
                "replacement_added_path_pattern": replacement_added_path_pattern,
                "replacement_action_type": replacement_action_type,
                "replacement_evidence_type": replacement_evidence_type,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.propose_policy_distribution_review",
        description=tool_description(
            tool_definitions["jikuo.propose_policy_distribution_review"]
        ),
    )
    def jikuo_propose_policy_distribution_review(
        project_root: str | None = None,
        policy_ref: str | None = None,
        source_policy: str | None = None,
        policy_query: str | None = None,
        distribution_decision: str | None = None,
        source_project_ref: str | None = None,
        starter_pack_id: str | None = None,
        rationale: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.propose_policy_distribution_review",
            {
                "project_root": project_root,
                "policy_ref": policy_ref,
                "source_policy": source_policy,
                "policy_query": policy_query,
                "distribution_decision": distribution_decision,
                "source_project_ref": source_project_ref,
                "starter_pack_id": starter_pack_id,
                "rationale": rationale,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.propose_policy_template_publication_plan",
        description=tool_description(
            tool_definitions["jikuo.propose_policy_template_publication_plan"]
        ),
    )
    def jikuo_propose_policy_template_publication_plan(
        project_root: str | None = None,
        policy_ref: str | None = None,
        source_policy: str | None = None,
        policy_query: str | None = None,
        distribution_decision: str | None = None,
        source_project_ref: str | None = None,
        starter_pack_id: str | None = None,
        rationale: str | None = None,
        target_dir: str | None = None,
        namespace: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.propose_policy_template_publication_plan",
            {
                "project_root": project_root,
                "policy_ref": policy_ref,
                "source_policy": source_policy,
                "policy_query": policy_query,
                "distribution_decision": distribution_decision,
                "source_project_ref": source_project_ref,
                "starter_pack_id": starter_pack_id,
                "rationale": rationale,
                "target_dir": target_dir,
                "namespace": namespace,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.propose_starter_manifest_publication_plan",
        description=tool_description(
            tool_definitions["jikuo.propose_starter_manifest_publication_plan"]
        ),
    )
    def jikuo_propose_starter_manifest_publication_plan(
        project_root: str | None = None,
        template_ref: str | None = None,
        starter_pack_id: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.propose_starter_manifest_publication_plan",
            {
                "project_root": project_root,
                "template_ref": template_ref,
                "starter_pack_id": starter_pack_id,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.propose_policy_template_import_plan",
        description=tool_description(
            tool_definitions["jikuo.propose_policy_template_import_plan"]
        ),
    )
    def jikuo_propose_policy_template_import_plan(
        project_root: str | None = None,
        template: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.propose_policy_template_import_plan",
            {"project_root": project_root, "template": template},
            default_transport=default_transport,
        )

    return server


def register_configuration_tools(
    server: Any,
    *,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Register no-write configuration review MCP tools."""

    tool_definitions = {tool["name"]: tool for tool in adapter.list_tools()}

    @server.tool(
        name="jikuo.get_configuration_status",
        description=tool_description(tool_definitions["jikuo.get_configuration_status"]),
    )
    def jikuo_get_configuration_status(
        project_root: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.get_configuration_status",
            {"project_root": project_root},
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.get_activation_settings",
        description=tool_description(tool_definitions["jikuo.get_activation_settings"]),
    )
    def jikuo_get_activation_settings(
        project_root: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.get_activation_settings",
            {"project_root": project_root},
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.plan_activation_settings_update",
        description=tool_description(
            tool_definitions["jikuo.plan_activation_settings_update"]
        ),
    )
    def jikuo_plan_activation_settings_update(
        project_root: str | None = None,
        trigger_mode: str | None = None,
        effective_enforcement_level: str | None = None,
        clients: list[str] | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.plan_activation_settings_update",
            {
                "project_root": project_root,
                "trigger_mode": trigger_mode,
                "effective_enforcement_level": effective_enforcement_level,
                "clients": clients or [],
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.apply_activation_settings_update",
        description=tool_description(
            tool_definitions["jikuo.apply_activation_settings_update"]
        ),
    )
    def jikuo_apply_activation_settings_update(
        project_root: str | None = None,
        trigger_mode: str | None = None,
        effective_enforcement_level: str | None = None,
        clients: list[str] | None = None,
        confirm_apply: bool = False,
        approval_phrase: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.apply_activation_settings_update",
            {
                "project_root": project_root,
                "trigger_mode": trigger_mode,
                "effective_enforcement_level": effective_enforcement_level,
                "clients": clients or [],
                "confirm_apply": confirm_apply,
                "approval_phrase": approval_phrase,
            },
            default_transport=default_transport,
        )

    return server


def register_router_tools(
    server: Any,
    *,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Register no-write conversation routing MCP tools."""

    tool_definitions = {tool["name"]: tool for tool in adapter.list_tools()}

    @server.tool(
        name="jikuo.route_user_request",
        description=tool_description(tool_definitions["jikuo.route_user_request"]),
    )
    def jikuo_route_user_request(
        project_root: str | None = None,
        user_phrase: str | None = None,
        host_semantic_intent: dict[str, Any] | None = None,
        trigger_mode: str | None = None,
        task_title: str | None = None,
        summary: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.route_user_request",
            {
                "project_root": project_root,
                "user_phrase": user_phrase,
                "host_semantic_intent": host_semantic_intent,
                "trigger_mode": trigger_mode,
                "task_title": task_title,
                "summary": summary,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.propose_policy_suggestions",
        description=tool_description(
            tool_definitions["jikuo.propose_policy_suggestions"]
        ),
    )
    def jikuo_propose_policy_suggestions(
        project_root: str | None = None,
        user_phrase: str | None = None,
        host_semantic_intent: dict[str, Any] | None = None,
        trigger_mode: str | None = None,
        task_title: str | None = None,
        summary: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.propose_policy_suggestions",
            {
                "project_root": project_root,
                "user_phrase": user_phrase,
                "host_semantic_intent": host_semantic_intent,
                "trigger_mode": trigger_mode,
                "task_title": task_title,
                "summary": summary,
            },
            default_transport=default_transport,
        )

    return server


async def _sample_semantic_intent(
    *,
    ctx: Any,
    user_phrase: str | None,
    task_title: str | None,
    summary: str | None,
    source_client: str,
    model_hint: str | None,
    max_tokens: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        from mcp import types as mcp_types  # type: ignore
    except ImportError:
        semantic_intent = sampling_semantic.unavailable_host_semantic_intent(
            reason="mcp_sdk_types_unavailable",
            source_client=source_client,
        )
        return semantic_intent, sampling_semantic.sampling_report(
            status="unavailable",
            errors=["mcp_sdk_types_unavailable"],
        )

    try:
        prompt = sampling_semantic.build_sampling_prompt(
            user_phrase=user_phrase,
            task_title=task_title,
            summary=summary,
        )
        model_preferences = None
        if model_hint:
            model_preferences = mcp_types.ModelPreferences(
                hints=[mcp_types.ModelHint(name=model_hint)],
                intelligencePriority=0.7,
                speedPriority=0.2,
                costPriority=0.1,
            )
        result = await ctx.session.create_message(
            messages=[
                mcp_types.SamplingMessage(
                    role="user",
                    content=mcp_types.TextContent(type="text", text=prompt),
                )
            ],
            system_prompt=(
                "You are classifying a user turn for JIKUO governance routing. "
                "Return compact JSON only and do not repeat the user's raw prompt."
            ),
            include_context="none",
            max_tokens=max(200, min(int(max_tokens or 700), 2000)),
            temperature=0,
            model_preferences=model_preferences,
            related_request_id=getattr(ctx, "request_id", None),
        )
    except Exception as exc:  # pragma: no cover - exact client errors vary.
        error_text = f"{type(exc).__name__}: {exc}"
        if user_phrase and len(user_phrase.strip()) >= 8:
            error_text = error_text.replace(user_phrase.strip(), "<REDACTED_PROMPT_ECHO>")
        semantic_intent = sampling_semantic.unavailable_host_semantic_intent(
            reason=error_text,
            source_client=source_client,
        )
        return semantic_intent, sampling_semantic.sampling_report(
            status="unavailable",
            errors=[error_text],
        )
    return sampling_semantic.parse_sampling_response(
        result,
        user_phrase=user_phrase,
        source_client=source_client,
    )


def register_sampling_tools(
    server: Any,
    *,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Register client-mediated MCP Sampling proof tools."""

    tool_definitions = {tool["name"]: tool for tool in adapter.list_tools()}

    @server.tool(
        name="jikuo.probe_sampling_semantic_intent",
        description=tool_description(
            tool_definitions["jikuo.probe_sampling_semantic_intent"]
        ),
    )
    async def jikuo_probe_sampling_semantic_intent(
        project_root: str | None = None,
        user_phrase: str | None = None,
        trigger_mode: str | None = None,
        task_title: str | None = None,
        summary: str | None = None,
        source_client: str | None = None,
        model_hint: str | None = None,
        max_tokens: int = 700,
        ctx: FastMCPContext | None = None,
    ) -> dict[str, Any]:
        if ctx is None:
            return _call(
                "jikuo.probe_sampling_semantic_intent",
                {
                    "project_root": project_root,
                    "user_phrase": user_phrase,
                    "trigger_mode": trigger_mode,
                    "task_title": task_title,
                    "summary": summary,
                    "source_client": source_client,
                    "model_hint": model_hint,
                    "max_tokens": max_tokens,
                },
                default_transport=default_transport,
            )
        semantic_intent, sampling_report = await _sample_semantic_intent(
            ctx=ctx,
            user_phrase=user_phrase,
            task_title=task_title,
            summary=summary,
            source_client=source_client or "mcp_client",
            model_hint=model_hint,
            max_tokens=max_tokens,
        )
        response = _call(
            "jikuo.route_user_request",
            {
                "project_root": project_root,
                "user_phrase": user_phrase,
                "host_semantic_intent": semantic_intent,
                "trigger_mode": trigger_mode,
                "task_title": task_title,
                "summary": summary,
            },
            default_transport=default_transport,
        )
        response["tool_name"] = "jikuo.probe_sampling_semantic_intent"
        response["stage"] = schemas.tool_definition(
            "jikuo.probe_sampling_semantic_intent"
        )["stage"]
        response["field_classification"] = schemas.response_field_classification(
            "jikuo.probe_sampling_semantic_intent"
        )
        return sampling_semantic.attach_sampling_result(
            response,
            report=sampling_report,
            semantic_intent=semantic_intent,
            user_phrase=user_phrase,
        )

    return server


def register_stage_b1_tools(
    server: Any,
    *,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Register accepted Stage B1 guarded-write MCP tools."""

    tool_definitions = {tool["name"]: tool for tool in adapter.list_tools()}

    @server.tool(
        name="jikuo.apply_task_session_evidence_update",
        description=tool_description(
            tool_definitions["jikuo.apply_task_session_evidence_update"]
        ),
    )
    def jikuo_apply_task_session_evidence_update(
        project_root: str | None = None,
        session_id: str | None = None,
        evidence_kind: str | None = None,
        evidence_ref: str | None = None,
        summary: str | None = None,
        evidence_status: str | None = None,
        owner_agent: str | None = None,
        confirm_apply: bool = False,
        approval_phrase: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.apply_task_session_evidence_update",
            {
                "project_root": project_root,
                "session_id": session_id,
                "evidence_kind": evidence_kind,
                "evidence_ref": evidence_ref,
                "summary": summary,
                "evidence_status": evidence_status,
                "owner_agent": owner_agent,
                "confirm_apply": confirm_apply,
                "approval_phrase": approval_phrase,
            },
            default_transport=default_transport,
        )

    return server


def register_stage_b2_tools(
    server: Any,
    *,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Register accepted Stage B2 guarded policy-evolution MCP tools."""

    tool_definitions = {tool["name"]: tool for tool in adapter.list_tools()}

    @server.tool(
        name="jikuo.apply_policy_evolution_write",
        description=tool_description(
            tool_definitions["jikuo.apply_policy_evolution_write"]
        ),
    )
    def jikuo_apply_policy_evolution_write(
        project_root: str | None = None,
        policy_ref: str | None = None,
        proposal_ref: str | None = None,
        policy_evolution_operation: str | None = None,
        feedback_type: str | None = None,
        summary: str | None = None,
        policy_source_ref: str | None = None,
        replacement_policy_ref: str | None = None,
        replacement_title: str | None = None,
        replacement_trigger_event: str | None = None,
        replacement_task_type: str | None = None,
        replacement_jikuo_layer: str | None = None,
        replacement_changed_path_pattern: str | None = None,
        replacement_added_path_pattern: str | None = None,
        replacement_action_type: str | None = None,
        replacement_evidence_type: str | None = None,
        owner_agent: str | None = None,
        confirm_apply: bool = False,
        approval_phrase: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.apply_policy_evolution_write",
            {
                "project_root": project_root,
                "policy_ref": policy_ref,
                "proposal_ref": proposal_ref,
                "policy_evolution_operation": policy_evolution_operation,
                "feedback_type": feedback_type,
                "summary": summary,
                "policy_source_ref": policy_source_ref,
                "replacement_policy_ref": replacement_policy_ref,
                "replacement_title": replacement_title,
                "replacement_trigger_event": replacement_trigger_event,
                "replacement_task_type": replacement_task_type,
                "replacement_jikuo_layer": replacement_jikuo_layer,
                "replacement_changed_path_pattern": replacement_changed_path_pattern,
                "replacement_added_path_pattern": replacement_added_path_pattern,
                "replacement_action_type": replacement_action_type,
                "replacement_evidence_type": replacement_evidence_type,
                "owner_agent": owner_agent,
                "confirm_apply": confirm_apply,
                "approval_phrase": approval_phrase,
            },
            default_transport=default_transport,
        )

    return server


def register_stage_b3_tools(
    server: Any,
    *,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Register accepted Stage B3 guarded policy-template activation MCP tools."""

    tool_definitions = {tool["name"]: tool for tool in adapter.list_tools()}

    @server.tool(
        name="jikuo.apply_policy_template_activation",
        description=tool_description(
            tool_definitions["jikuo.apply_policy_template_activation"]
        ),
    )
    def jikuo_apply_policy_template_activation(
        project_root: str | None = None,
        template: str | None = None,
        owner_agent: str | None = None,
        confirm_apply: bool = False,
        approval_phrase: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.apply_policy_template_activation",
            {
                "project_root": project_root,
                "template": template,
                "owner_agent": owner_agent,
                "confirm_apply": confirm_apply,
                "approval_phrase": approval_phrase,
            },
            default_transport=default_transport,
        )

    return server


def register_policy_publication_tools(
    server: Any,
    *,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Register guarded policy publication MCP tools."""

    tool_definitions = {tool["name"]: tool for tool in adapter.list_tools()}

    @server.tool(
        name="jikuo.apply_policy_template_publication",
        description=tool_description(
            tool_definitions["jikuo.apply_policy_template_publication"]
        ),
    )
    def jikuo_apply_policy_template_publication(
        project_root: str | None = None,
        source_policy: str | None = None,
        distribution_decision: str | None = None,
        source_project_ref: str | None = None,
        starter_pack_id: str | None = None,
        rationale: str | None = None,
        target_dir: str | None = None,
        namespace: str | None = None,
        owner_agent: str | None = None,
        confirm_apply: bool = False,
        approval_phrase: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.apply_policy_template_publication",
            {
                "project_root": project_root,
                "source_policy": source_policy,
                "distribution_decision": distribution_decision,
                "source_project_ref": source_project_ref,
                "starter_pack_id": starter_pack_id,
                "rationale": rationale,
                "target_dir": target_dir,
                "namespace": namespace,
                "owner_agent": owner_agent,
                "confirm_apply": confirm_apply,
                "approval_phrase": approval_phrase,
            },
            default_transport=default_transport,
        )

    @server.tool(
        name="jikuo.apply_starter_manifest_publication",
        description=tool_description(
            tool_definitions["jikuo.apply_starter_manifest_publication"]
        ),
    )
    def jikuo_apply_starter_manifest_publication(
        project_root: str | None = None,
        template_ref: str | None = None,
        starter_pack_id: str | None = None,
        owner_agent: str | None = None,
        confirm_apply: bool = False,
        approval_phrase: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            "jikuo.apply_starter_manifest_publication",
            {
                "project_root": project_root,
                "template_ref": template_ref,
                "starter_pack_id": starter_pack_id,
                "owner_agent": owner_agent,
                "confirm_apply": confirm_apply,
                "approval_phrase": approval_phrase,
            },
            default_transport=default_transport,
        )

    return server


def create_server(
    *,
    fastmcp_cls: FastMCPFactory | None = None,
    default_transport: str = schemas.LOCAL_STDIO_TRANSPORT,
) -> Any:
    """Create a FastMCP server and register accepted JIKUO MCP tools."""

    factory = fastmcp_cls if fastmcp_cls is not None else load_fastmcp_class()
    server = factory(
        SERVER_NAME,
        instructions=(
            "JIKUO is a deterministic governance harness. Card-returning tools "
            "must surface card_markdown verbatim and provide out-of-band "
            "verification paths."
        ),
    )
    register_stage_a_tools(server, default_transport=default_transport)
    register_configuration_tools(server, default_transport=default_transport)
    register_router_tools(server, default_transport=default_transport)
    register_sampling_tools(server, default_transport=default_transport)
    register_stage_b1_tools(server, default_transport=default_transport)
    register_stage_b2_tools(server, default_transport=default_transport)
    register_stage_b3_tools(server, default_transport=default_transport)
    return register_policy_publication_tools(server, default_transport=default_transport)


def _adapter_transport_for_run(run_transport: str) -> str:
    if run_transport == "stdio":
        return schemas.LOCAL_STDIO_TRANSPORT
    return schemas.UNKNOWN_TRANSPORT


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the JIKUO MCP server with the official Python SDK.",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help="MCP transport passed to FastMCP.run().",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    server = create_server(
        default_transport=_adapter_transport_for_run(str(args.transport)),
    )
    if args.transport == "stdio":
        server.run()
    else:
        server.run(transport=args.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
