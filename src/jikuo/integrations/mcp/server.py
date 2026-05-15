"""Official Python MCP SDK server wrapper for JIKUO MCP tools."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import Any, Callable

from . import adapter, schemas


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
    register_stage_b1_tools(server, default_transport=default_transport)
    return register_stage_b2_tools(server, default_transport=default_transport)


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
