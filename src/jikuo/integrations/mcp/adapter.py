"""SDK-free MCP Stage A adapter for JIKUO core APIs."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ... import agent_flow, policy_store, runtime_visibility
from . import schemas


def list_tools() -> list[dict[str, Any]]:
    """Return Stage A MCP tool metadata without importing an MCP SDK."""

    return schemas.build_tool_list()


def _path_or_none(value: Any) -> Path | None:
    if value is None:
        return None
    if isinstance(value, Path):
        return value
    return Path(str(value))


def _project_root_from(
    arguments: dict[str, Any],
    *,
    project_root: Path | str | None,
) -> Path | None:
    explicit_root = project_root if project_root is not None else arguments.get("project_root")
    return _path_or_none(explicit_root)


def _transport_from(arguments: dict[str, Any], transport: str | None) -> str:
    value = transport if transport is not None else arguments.get("transport")
    return str(value or schemas.UNKNOWN_TRANSPORT)


def _root_strings(project_root: Path | None) -> tuple[str, ...]:
    if project_root is None:
        return ()
    resolved = project_root.resolve()
    values = {
        str(resolved),
        resolved.as_posix(),
    }
    return tuple(sorted(values, key=len, reverse=True))


def _sanitize_string(value: str, *, project_root: Path | None, transport: str) -> str:
    if schemas.transport_allows_local_only(transport):
        return value
    output = value
    for root in _root_strings(project_root):
        output = output.replace(root, "<LOCAL_PROJECT_ROOT>")
    return output


def _sanitize_for_transport(
    value: Any,
    *,
    project_root: Path | None,
    transport: str,
) -> Any:
    if isinstance(value, str):
        return _sanitize_string(value, project_root=project_root, transport=transport)
    if isinstance(value, list):
        return [
            _sanitize_for_transport(item, project_root=project_root, transport=transport)
            for item in value
        ]
    if isinstance(value, tuple):
        return [
            _sanitize_for_transport(item, project_root=project_root, transport=transport)
            for item in value
        ]
    if isinstance(value, dict):
        return {
            str(key): _sanitize_for_transport(
                item,
                project_root=project_root,
                transport=transport,
            )
            for key, item in value.items()
        }
    return value


def _runtime_report_from(data: dict[str, Any]) -> dict[str, Any]:
    report = data.get("runtime_visibility")
    if isinstance(report, dict):
        return report
    return {}


def _first_card_id(data: dict[str, Any]) -> str | None:
    cards = data.get("cards")
    if not isinstance(cards, list):
        return None
    for preferred in schemas.CARD_PRIORITY_ORDER:
        for card in cards:
            if isinstance(card, dict) and card.get("card_kind") == preferred:
                return str(card.get("card_id") or "")
    for card in cards:
        if isinstance(card, dict) and card.get("card_id"):
            return str(card["card_id"])
    return None


def _display_verification(
    *,
    data: dict[str, Any],
    runtime_report: dict[str, Any],
) -> dict[str, Any]:
    last_ref = str(runtime_report.get("last_card_ref") or runtime_visibility.LAST_CARD_REF)
    return {
        "schema": schemas.DISPLAY_VERIFICATION_SCHEMA,
        "card_id": _first_card_id(data),
        "runtime_snapshot_path_relative": last_ref,
        "state_summary_path_relative": str(
            runtime_report.get("state_summary_ref") or runtime_visibility.STATE_SUMMARY_REF
        ),
        "snapshot_written_at_utc": runtime_report.get("updated_at_utc"),
        "user_can_verify_with": [
            "jikuo show --last-card",
            f"open {last_ref}",
        ],
    }


def _local_paths(
    *,
    project_root: Path | None,
    runtime_report: dict[str, Any],
    transport: str,
) -> dict[str, str] | None:
    if not schemas.transport_allows_local_only(transport) or project_root is None:
        return None
    resolved_root = project_root.resolve()
    output = {"project_root": str(resolved_root)}
    for key, ref_key in (
        ("last_card", "last_card_ref"),
        ("state_summary", "state_summary_ref"),
        ("history_card", "history_ref"),
    ):
        ref = runtime_report.get(ref_key)
        if ref:
            output[key] = str((resolved_root / str(ref)).resolve())
    return output


def _base_response(
    *,
    tool_name: str,
    status: str,
    data_details: dict[str, Any],
    project_root: Path | None,
    transport: str,
    card_markdown: str | None = None,
    chat_ready_markdown: str | None = None,
    runtime_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tool = schemas.tool_definition(tool_name)
    runtime = runtime_report or _runtime_report_from(data_details)
    response: dict[str, Any] = {
        "schema": schemas.ADAPTER_RESULT_SCHEMA,
        "tool_name": tool_name,
        "stage": tool["stage"],
        "status": status,
        "write_mode": tool["write_mode"],
        "transport": transport,
        "display": schemas.build_display_directives(),
        "data_details": deepcopy(data_details),
        "field_classification": schemas.response_field_classification(tool_name),
    }
    if card_markdown is not None:
        response["card_markdown"] = card_markdown
    if chat_ready_markdown is not None:
        response["chat_ready_markdown"] = chat_ready_markdown
    if runtime:
        response["runtime_snapshot_ref"] = runtime.get("last_card_ref")
        response["display_verification"] = _display_verification(
            data=data_details,
            runtime_report=runtime,
        )
        local_paths = _local_paths(
            project_root=project_root,
            runtime_report=runtime,
            transport=transport,
        )
        if local_paths is not None:
            response["local_paths"] = local_paths
    return _sanitize_for_transport(
        response,
        project_root=project_root,
        transport=transport,
    )


def _proposal_response(
    *,
    tool_name: str,
    raw_event: str,
    arguments: dict[str, Any],
    project_root: Path | None,
    transport: str,
    **kwargs: Any,
) -> dict[str, Any]:
    proposal = agent_flow.build_proposal(
        raw_event=raw_event,
        project_root=project_root,
        **kwargs,
    )
    with_markdown = agent_flow.proposal_with_chat_ready_markdown(
        proposal,
        project_root=project_root,
    )
    markdown = str(with_markdown.get("chat_ready_markdown") or "")
    return _base_response(
        tool_name=tool_name,
        status=str(with_markdown.get("status") or "review"),
        data_details=with_markdown,
        project_root=project_root,
        transport=transport,
        card_markdown=markdown,
        chat_ready_markdown=markdown,
        runtime_report=_runtime_report_from(with_markdown),
    )


def _runtime_status_card_response(
    *,
    project_root: Path | None,
    transport: str,
) -> dict[str, Any]:
    proposal = agent_flow.build_proposal(
        raw_event="project_status",
        project_root=project_root,
    )
    with_markdown = agent_flow.proposal_with_chat_ready_markdown(
        proposal,
        project_root=project_root,
    )
    cards = with_markdown.get("cards") or []
    policy_card = next(
        (
            card
            for card in cards
            if isinstance(card, dict) and card.get("card_kind") == "policy_runtime_status"
        ),
        None,
    )
    card_markdown = (
        agent_flow.render_card(policy_card)
        if isinstance(policy_card, dict)
        else str(with_markdown.get("chat_ready_markdown") or "")
    )
    return _base_response(
        tool_name="jikuo.get_runtime_status_card",
        status=str(with_markdown.get("status") or "review"),
        data_details=with_markdown,
        project_root=project_root,
        transport=transport,
        card_markdown=card_markdown,
        chat_ready_markdown=card_markdown,
        runtime_report=_runtime_report_from(with_markdown),
    )


def call_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    *,
    project_root: Path | str | None = None,
    transport: str | None = None,
) -> dict[str, Any]:
    """Call a Stage A JIKUO MCP tool through structured core APIs.

    This function intentionally does not import or require an MCP SDK. The future
    protocol server should call this adapter and then wrap the returned shape.
    """

    schemas.tool_definition(tool_name)
    args = dict(arguments or {})
    resolved_root = _project_root_from(args, project_root=project_root)
    resolved_transport = _transport_from(args, transport)

    if tool_name == "jikuo.status":
        report = policy_store.inspect_policy_store(project_root=resolved_root)
        root = Path(str(report["project_root"]))
        response = _base_response(
            tool_name=tool_name,
            status=str(report.get("policy_store_status") or "unknown"),
            data_details=report,
            project_root=root,
            transport=resolved_transport,
        )
        response["policy_store_status"] = report.get("policy_store_status")
        return response

    if tool_name == "jikuo.get_runtime_status":
        summary = runtime_visibility.attach_task_session_index_status(
            runtime_visibility.load_state_summary(project_root=resolved_root),
            project_root=resolved_root,
        )
        root = Path(str(summary["project_root"]))
        markdown = runtime_visibility.format_state_summary(summary)
        response = _base_response(
            tool_name=tool_name,
            status=str(summary.get("status") or "available"),
            data_details=summary,
            project_root=root,
            transport=resolved_transport,
            card_markdown=markdown,
            chat_ready_markdown=markdown,
            runtime_report={
                "last_card_ref": runtime_visibility.LAST_CARD_REF,
                "state_summary_ref": runtime_visibility.STATE_SUMMARY_REF,
                "project_root": str(root),
                "updated_at_utc": summary.get("updated_at_utc"),
            },
        )
        response["runtime_status"] = response["data_details"]
        return response

    if tool_name == "jikuo.get_runtime_status_card":
        return _runtime_status_card_response(
            project_root=resolved_root,
            transport=resolved_transport,
        )

    if tool_name == "jikuo.get_display_card":
        card_markdown, report = runtime_visibility.load_last_card(
            project_root=resolved_root,
        )
        root = Path(str(report["project_root"]))
        markdown = card_markdown or ""
        return _base_response(
            tool_name=tool_name,
            status=str(report.get("status") or "missing"),
            data_details=report,
            project_root=root,
            transport=resolved_transport,
            card_markdown=markdown,
            chat_ready_markdown=markdown,
            runtime_report=report,
        )

    if tool_name == "jikuo.propose_task_start":
        return _proposal_response(
            tool_name=tool_name,
            raw_event="task_start",
            arguments=args,
            project_root=resolved_root,
            transport=resolved_transport,
            task_title=args.get("task_title"),
            session_id=args.get("session_id"),
            task_type=args.get("task_type"),
            jikuo_layer=args.get("jikuo_layer"),
            changed_paths=list(args.get("changed_paths") or []),
            added_paths=list(args.get("added_paths") or []),
            summary=args.get("summary"),
            owner_agent=str(args.get("owner_agent") or "codex"),
            work_routing_category=args.get("work_routing_category"),
            work_routing_summary=args.get("work_routing_summary"),
        )

    if tool_name == "jikuo.propose_policy_write_plan":
        return _proposal_response(
            tool_name=tool_name,
            raw_event="policy_write_plan",
            arguments=args,
            project_root=resolved_root,
            transport=resolved_transport,
            policy_ref=args.get("policy_ref"),
            policy_title=args.get("policy_title"),
            policy_source_ref=args.get("policy_source_ref"),
            policy_trigger_event=str(args.get("policy_trigger_event") or "task_start"),
            policy_task_type=args.get("policy_task_type"),
            policy_jikuo_layer=args.get("policy_jikuo_layer"),
            policy_changed_path_pattern=args.get("policy_changed_path_pattern"),
            policy_added_path_pattern=args.get("policy_added_path_pattern"),
            policy_action_type=str(
                args.get("policy_action_type") or "render_pre_task_review"
            ),
            policy_evidence_type=str(args.get("policy_evidence_type") or "card_rendered"),
        )

    if tool_name == "jikuo.propose_policy_evolution_plan":
        return _proposal_response(
            tool_name=tool_name,
            raw_event="policy_evolution_plan",
            arguments=args,
            project_root=resolved_root,
            transport=resolved_transport,
            policy_ref=args.get("policy_ref"),
            policy_evolution_operation=str(
                args.get("policy_evolution_operation") or "refine_policy"
            ),
            feedback_type=args.get("feedback_type"),
            summary=args.get("summary"),
            policy_source_ref=args.get("policy_source_ref"),
            replacement_policy_ref=args.get("replacement_policy_ref"),
            replacement_title=args.get("replacement_title"),
            replacement_task_type=args.get("replacement_task_type"),
            replacement_jikuo_layer=args.get("replacement_jikuo_layer"),
            replacement_changed_path_pattern=args.get("replacement_changed_path_pattern"),
            replacement_added_path_pattern=args.get("replacement_added_path_pattern"),
            replacement_action_type=str(
                args.get("replacement_action_type") or "render_pre_task_review"
            ),
            replacement_evidence_type=str(
                args.get("replacement_evidence_type") or "card_rendered"
            ),
        )

    if tool_name == "jikuo.propose_policy_template_import_plan":
        return _proposal_response(
            tool_name=tool_name,
            raw_event="policy_template_import_plan",
            arguments=args,
            project_root=resolved_root,
            transport=resolved_transport,
            template_path=_path_or_none(args.get("template")),
        )

    raise ValueError(f"unsupported MCP Stage A tool: {tool_name}")
