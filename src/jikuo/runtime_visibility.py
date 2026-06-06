"""Out-of-band runtime visibility snapshots for JIKUO."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__:
    from . import activation_settings, project_state, task_session, turn_anchor
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import activation_settings
    import project_state
    import task_session
    import turn_anchor


RUNTIME_VISIBILITY_REPORT_SCHEMA = "jikuo.runtime_visibility_report.v0"
RUNTIME_STATE_SUMMARY_SCHEMA = "jikuo.runtime_state_summary.v0"
SEMANTIC_INTENT_COVERAGE_SCHEMA = "jikuo.semantic_intent_coverage.v0"
SEMANTIC_INTENT_EVIDENCE_SCHEMA = "jikuo.semantic_intent_evidence.v0"
CLIENT_DISPLAY_LINKS_SCHEMA = "jikuo.client_display_links.v0"
TASK_SESSION_INDEX_STATUS_SCHEMA = "jikuo.task_session_index_status.v0"
OBSERVED_LIFECYCLE_SCHEMA = "jikuo.observed_lifecycle.v0"
RUNTIME_DIR_REF = ".jikuo/runtime"
LAST_CARD_REF = ".jikuo/runtime/last_card.md"
STATE_SUMMARY_REF = ".jikuo/runtime/state_summary.json"
HISTORY_DIR_REF = ".jikuo/runtime/history"
PACKAGE_FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"
LIFECYCLE_EVENT_ORDER = [
    "conversation_turn",
    "configuration_review",
    "task_start",
    "task_continue",
    "evidence_review",
    "verification_review",
    "pre_delivery",
    "completion_review",
    "handoff",
]
LIFECYCLE_EVENTS = set(LIFECYCLE_EVENT_ORDER)
RECOMMENDED_OBSERVED_LIFECYCLE_EVENTS = [
    "conversation_turn",
    "task_start",
    "completion_review",
]
TERMINAL_LIFECYCLE_EVENTS = {"completion_review", "handoff"}


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def slugify_ref(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip()).strip("._-")
    return slug[:72] or "runtime_card"


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
    except ValueError:
        return False
    return True


def project_root_for(project_root: Path | None) -> Path:
    return project_state.discover_project_root(project_root=project_root)


def should_skip_runtime_write(project_root: Path) -> str | None:
    if is_relative_to(project_root.resolve(), PACKAGE_FIXTURES_ROOT.resolve()):
        return "package_fixture_project_is_read_only"
    return None


def runtime_root_for(project_root: Path) -> Path:
    runtime_root = (project_root / ".jikuo" / "runtime").resolve()
    resolved_root = project_root.resolve()
    if not is_relative_to(runtime_root, resolved_root):
        raise ValueError("runtime visibility root escaped project root")
    return runtime_root


def runtime_paths(project_root: Path, *, source_id: str) -> dict[str, Path]:
    runtime_root = runtime_root_for(project_root)
    history_root = runtime_root / "history"
    history_name = f"{utc_now_compact()}_{slugify_ref(source_id)}.md"
    history_state_summary_name = f"{Path(history_name).stem}.json"
    paths = {
        "runtime_root": runtime_root,
        "last_card": runtime_root / "last_card.md",
        "state_summary": runtime_root / "state_summary.json",
        "history_root": history_root,
        "history_card": history_root / history_name,
        "history_state_summary": history_root / history_state_summary_name,
    }
    for key, value in paths.items():
        if key == "runtime_root":
            continue
        if not is_relative_to(value.resolve(), runtime_root):
            raise ValueError(f"runtime visibility path escaped runtime root: {key}")
    return paths


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(text, encoding="utf-8", newline="\n")
    tmp_path.replace(path)


def find_policy_runtime_status(proposal: dict[str, Any]) -> dict[str, Any] | None:
    for card in reversed(proposal.get("cards", [])):
        status = card.get("policy_runtime_status")
        if isinstance(status, dict):
            return status
    return None


def string_items(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def work_profile_for_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    work_profile = proposal.get("work_profile")
    if not isinstance(work_profile, dict):
        work_profile = (proposal.get("policy_context") or {}).get("work_profile")
    if not isinstance(work_profile, dict):
        work_profile = (proposal.get("policy_runtime_status") or {}).get("work_profile")
    if not isinstance(work_profile, dict):
        return {}
    return work_profile


def semantic_parts_for_proposal(
    proposal: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    work_profile = work_profile_for_proposal(proposal)
    evidence = proposal.get("semantic_intent_evidence")
    if not isinstance(evidence, dict):
        evidence = work_profile.get("semantic_intent_evidence")
    if not isinstance(evidence, dict):
        evidence = {}
    basis = work_profile.get("basis") if isinstance(work_profile, dict) else {}
    if not isinstance(basis, dict):
        basis = {}
    host_intent = basis.get("host_semantic_intent")
    if not isinstance(host_intent, dict):
        host_intent = {}
    return work_profile, evidence, host_intent


def _short_hash(*parts: Any) -> str:
    material = "|".join(str(part or "") for part in parts)
    return hashlib.sha256(material.encode("utf-8", errors="surrogatepass")).hexdigest()[
        :16
    ]


def semantic_intent_ref_for(
    *,
    host_intent: dict[str, Any],
    anchor: dict[str, Any],
    proposal: dict[str, Any],
) -> str | None:
    direct = host_intent.get("semantic_intent_ref")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    if host_intent.get("status") not in {"provided", "heuristic_fallback"}:
        return None
    anchor_id = anchor.get("anchor_id") if anchor.get("status") == "available" else None
    proposal_id = proposal.get("proposal_id")
    if anchor_id:
        return f"sem_{_short_hash(anchor_id, proposal_id, host_intent.get('provider'))}"
    return f"sem_{_short_hash(proposal_id, host_intent.get('provider'), host_intent.get('status'))}"


def semantic_intent_evidence_for(proposal: dict[str, Any]) -> dict[str, Any]:
    work_profile, evidence, host_intent = semantic_parts_for_proposal(proposal)
    anchor = turn_anchor.turn_anchor_for_proposal(proposal)
    semantic_status = str(
        evidence.get("semantic_intent_status")
        or host_intent.get("status")
        or "unavailable"
    )
    evidence_status = str(evidence.get("status") or "unknown")
    provider = str(evidence.get("provider") or host_intent.get("provider") or "unavailable")
    source_kind = str(
        host_intent.get("evidence_source_kind")
        or (
            "heuristic_fallback"
            if semantic_status in {"heuristic_fallback", "fallback"}
            else "host_supplied"
            if semantic_status == "provided"
            else "unavailable"
        )
    )
    semantic_ref = semantic_intent_ref_for(
        host_intent=host_intent,
        anchor=anchor,
        proposal=proposal,
    )
    status = (
        "available"
        if semantic_status in {"provided", "heuristic_fallback"}
        and host_intent
        else "unavailable"
    )
    compact_host = dict(host_intent) if status == "available" else {}
    if compact_host:
        compact_host["semantic_intent_ref"] = semantic_ref
        compact_host.setdefault("evidence_source_kind", source_kind)
    return {
        "schema": SEMANTIC_INTENT_EVIDENCE_SCHEMA,
        "status": status,
        "semantic_intent_ref": semantic_ref,
        "evidence_source_kind": source_kind,
        "semantic_intent_status": semantic_status,
        "evidence_status": evidence_status,
        "provider": provider,
        "confidence": str(host_intent.get("confidence") or "unavailable"),
        "required": bool(evidence.get("required")),
        "policy_scopes": string_items(
            work_profile.get("policy_scopes") or host_intent.get("policy_scopes")
        ),
        "policy_contract": host_intent.get("policy_contract") or {},
        "turn_anchor": anchor,
        "host_semantic_intent": compact_host,
        "inherited_from": host_intent.get("inherited_from") or {},
        "privacy": {
            "raw_prompt_persisted": False,
            "raw_transcript_persisted": False,
            "raw_prompt_included": False,
        },
        "non_effects": [
            "does_not_call_llm_provider",
            "does_not_infer_semantic_intent",
            "does_not_include_raw_prompt_or_transcript",
            "does_not_change_policy_evaluator_results",
        ],
    }


def semantic_intent_coverage_for(proposal: dict[str, Any]) -> dict[str, Any]:
    work_profile, evidence, host_intent = semantic_parts_for_proposal(proposal)

    semantic_status = str(
        evidence.get("semantic_intent_status")
        or host_intent.get("status")
        or "unavailable"
    )
    evidence_status = str(evidence.get("status") or "unknown")
    provider = str(evidence.get("provider") or host_intent.get("provider") or "unavailable")
    required = bool(evidence.get("required"))
    fallback_expanded = bool(work_profile.get("fallback_expanded"))
    policy_scopes = string_items(
        work_profile.get("policy_scopes") or host_intent.get("policy_scopes")
    )
    source_kind = str(
        host_intent.get("evidence_source_kind")
        or (
            "heuristic_fallback"
            if semantic_status in {"heuristic_fallback", "fallback"}
            else "host_supplied"
            if semantic_status == "provided"
            else "unavailable"
        )
    )
    semantic_ref = semantic_intent_ref_for(
        host_intent=host_intent,
        anchor=turn_anchor.turn_anchor_for_proposal(proposal),
        proposal=proposal,
    )

    if semantic_status == "provided" and evidence_status == "ok":
        coverage_status = "complete"
        gap_reason = None
    elif semantic_status in {"heuristic_fallback", "fallback"} or fallback_expanded:
        coverage_status = "fallback_only"
        gap_reason = "deterministic_fallback_without_host_semantic_intent"
    elif semantic_status in {"unavailable", "missing"} and required:
        coverage_status = "missing"
        gap_reason = "host_ai_did_not_return_intent"
    elif semantic_status in {"unavailable", "missing"}:
        coverage_status = "degraded"
        gap_reason = "host_semantic_intent_unavailable_for_this_turn"
    else:
        coverage_status = "degraded"
        gap_reason = "semantic_intent_evidence_not_complete"

    return {
        "schema": SEMANTIC_INTENT_COVERAGE_SCHEMA,
        "coverage_status": coverage_status,
        "semantic_intent_status": semantic_status,
        "evidence_status": evidence_status,
        "provider": provider,
        "evidence_source_kind": source_kind,
        "semantic_intent_ref": semantic_ref,
        "required": required,
        "policy_scopes": policy_scopes,
        "fallback_expanded": fallback_expanded,
        "gap_reason": gap_reason,
        "risk_summary": (
            "host semantic intent was provided and policy routing has explicit "
            "host evidence"
            if coverage_status == "complete"
            else "policy routing may be degraded because host semantic intent "
            "was not provided as explicit evidence"
        ),
        "non_effects": [
            "does_not_call_llm_provider",
            "does_not_infer_hidden_model_intent",
            "does_not_change_policy_evaluator_results",
            "does_not_prove_strict_gui_semantic_gate",
        ],
    }


def build_state_summary(
    *,
    project_root: Path,
    proposal: dict[str, Any],
    runtime_report: dict[str, Any],
    updated_at_utc: str,
) -> dict[str, Any]:
    policy_runtime_status = find_policy_runtime_status(proposal)
    observed_lifecycle = runtime_report.get("observed_lifecycle") or observed_lifecycle_for_links(
        runtime_report.get("lifecycle_card_links", [])
    )
    return {
        "schema": RUNTIME_STATE_SUMMARY_SCHEMA,
        "updated_at_utc": updated_at_utc,
        "project_root": str(project_root),
        "source": {
            "schema": proposal.get("schema"),
            "proposal_id": proposal.get("proposal_id"),
            "runner_mode": proposal.get("runner_mode"),
            "status": proposal.get("status"),
            "event": (proposal.get("trigger_decision") or {}).get(
                "invocation_scenario"
            ),
        },
        "runtime_visibility": {
            "last_card_ref": runtime_report.get("last_card_ref"),
            "state_summary_ref": runtime_report.get("state_summary_ref"),
            "history_ref": runtime_report.get("history_ref"),
            "history_state_summary_ref": runtime_report.get(
                "history_state_summary_ref"
            ),
        },
        "client_display_links": build_client_display_links(runtime_report),
        "lifecycle_card_links": runtime_report.get("lifecycle_card_links", []),
        "observed_lifecycle": observed_lifecycle,
        "policy_runtime_status": policy_runtime_status,
        "work_profile": work_profile_for_proposal(proposal),
        "semantic_intent_coverage": semantic_intent_coverage_for(proposal),
        "semantic_intent_evidence": semantic_intent_evidence_for(proposal),
        "turn_anchor": turn_anchor.turn_anchor_for_proposal(proposal),
        "execution_envelope": proposal.get("execution_envelope"),
        "counts": {
            "card_count": len(proposal.get("cards", [])),
            "triggered_policy_count": len(proposal.get("triggered_policies", [])),
            "missing_evidence_count": len(proposal.get("missing_evidence_reports", [])),
            "required_action_count": len(proposal.get("required_actions", [])),
        },
        "triggered_policies": proposal.get("triggered_policies", []),
        "missing_evidence_reports": proposal.get("missing_evidence_reports", []),
        "artifact_assurance": proposal.get("artifact_assurance"),
        "write_boundary": {
            "governance_writes_performed": bool(
                (proposal.get("write_effect") or {}).get("writes_performed")
            ),
            "runtime_visibility_write_performed": bool(
                runtime_report.get("write_performed")
            ),
        },
    }


def rel_ref(path: Path, *, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return str(path)


def local_markdown_target(path: Path) -> str:
    return path.resolve().as_posix()


def int_or_zero(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def runtime_link_item(
    *,
    project_root: Path,
    key: str,
    label: str,
    ref: str | None,
) -> dict[str, Any] | None:
    if not ref:
        return None
    resolved = (project_root / ref).resolve()
    runtime_root = runtime_root_for(project_root)
    if not is_relative_to(resolved, runtime_root):
        raise ValueError(f"runtime display link escaped runtime root: {key}")
    target = local_markdown_target(resolved)
    return {
        "key": key,
        "label": label,
        "ref": ref,
        "path": str(resolved),
        "markdown_target": target,
        "markdown": f"[{Path(ref).name}]({target})",
    }


def lifecycle_event_for_snapshot(proposal: dict[str, Any]) -> str | None:
    trigger = proposal.get("trigger_decision") or {}
    event = trigger.get("invocation_scenario")
    if not event:
        source = proposal.get("source") or {}
        event = source.get("event")
    if not event:
        event = proposal.get("operation")
    if not event:
        return None
    event_text = str(event)
    if event_text not in LIFECYCLE_EVENTS:
        return None
    return event_text


def sort_lifecycle_card_links(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {event: index for index, event in enumerate(LIFECYCLE_EVENT_ORDER)}
    return sorted(
        items,
        key=lambda item: (
            order.get(str(item.get("lifecycle_event")), len(order)),
            str(item.get("updated_at_utc") or ""),
            str(item.get("ref") or ""),
        ),
    )


def observed_lifecycle_for_links(items: list[dict[str, Any]]) -> dict[str, Any]:
    events = [
        str(item.get("lifecycle_event"))
        for item in items
        if item.get("lifecycle_event") in LIFECYCLE_EVENTS
    ]
    missing = [
        event
        for event in RECOMMENDED_OBSERVED_LIFECYCLE_EVENTS
        if event not in events
    ]
    if not events:
        status = "empty"
    elif missing:
        status = "observed_partial"
    else:
        status = "observed_all_recommended_nodes"
    return {
        "schema": OBSERVED_LIFECYCLE_SCHEMA,
        "status": status,
        "guarantee": "observed_only_not_orchestrated",
        "recommended_events": list(RECOMMENDED_OBSERVED_LIFECYCLE_EVENTS),
        "observed_events": events,
        "missing_recommended_events": missing,
        "card_count": len(events),
        "non_effects": [
            "does_not_force_lifecycle_node_execution",
            "does_not_create_task_session_or_work_order_binding",
            "does_not_write_data01_event_ledger",
            "does_not_satisfy_policy_evidence_by_itself",
        ],
    }


def load_previous_lifecycle_card_links(project_root: Path) -> list[dict[str, Any]]:
    state_path = runtime_root_for(project_root) / "state_summary.json"
    if not state_path.is_file():
        return []
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    links = state.get("client_display_links") or {}
    previous = links.get("lifecycle_card_links") or state.get("lifecycle_card_links") or []
    output: list[dict[str, Any]] = []
    for raw_item in previous:
        if not isinstance(raw_item, dict):
            continue
        event = raw_item.get("lifecycle_event")
        ref = raw_item.get("ref")
        if not event or str(event) not in LIFECYCLE_EVENTS or not ref:
            continue
        item = runtime_link_item(
            project_root=project_root,
            key=f"lifecycle_{event}",
            label=str(raw_item.get("label") or f"{event} card"),
            ref=str(ref),
        )
        if not item:
            continue
        item["lifecycle_event"] = str(event)
        item["updated_at_utc"] = raw_item.get("updated_at_utc")
        item["triggered_policy_count"] = int_or_zero(
            raw_item.get("triggered_policy_count")
        )
        item["missing_evidence_count"] = int_or_zero(
            raw_item.get("missing_evidence_count")
        )
        output.append(item)
    return output


def lifecycle_card_link_for_snapshot(
    *,
    project_root: Path,
    proposal: dict[str, Any],
    runtime_report: dict[str, Any],
) -> dict[str, Any] | None:
    event = lifecycle_event_for_snapshot(proposal)
    history_ref = runtime_report.get("history_ref")
    if not event or not history_ref:
        return None
    item = runtime_link_item(
        project_root=project_root,
        key=f"lifecycle_{event}",
        label=f"{event} card",
        ref=str(history_ref),
    )
    if not item:
        return None
    item["lifecycle_event"] = event
    item["updated_at_utc"] = runtime_report.get("updated_at_utc")
    item["triggered_policy_count"] = len(proposal.get("triggered_policies", []))
    item["missing_evidence_count"] = len(proposal.get("missing_evidence_reports", []))
    return item


def should_reset_observed_lifecycle(
    current: dict[str, Any] | None,
    previous: list[dict[str, Any]],
) -> bool:
    if not current:
        return False
    event = str(current.get("lifecycle_event") or "")
    if event == "conversation_turn":
        return True
    previous_events = {
        str(item.get("lifecycle_event"))
        for item in previous
        if item.get("lifecycle_event") in LIFECYCLE_EVENTS
    }
    if event == "task_start" and (
        not previous_events or previous_events.intersection(TERMINAL_LIFECYCLE_EVENTS)
    ):
        return True
    return False


def lifecycle_card_links_for_snapshot(
    *,
    project_root: Path,
    proposal: dict[str, Any],
    runtime_report: dict[str, Any],
) -> list[dict[str, Any]]:
    current = lifecycle_card_link_for_snapshot(
        project_root=project_root,
        proposal=proposal,
        runtime_report=runtime_report,
    )
    previous = load_previous_lifecycle_card_links(project_root)
    if should_reset_observed_lifecycle(current, previous):
        previous = []
    if not current:
        return sort_lifecycle_card_links(previous)
    by_event = {item["lifecycle_event"]: item for item in previous}
    by_event[current["lifecycle_event"]] = current
    return sort_lifecycle_card_links(list(by_event.values()))


def build_client_display_links(runtime_report: dict[str, Any]) -> dict[str, Any]:
    lifecycle_links = runtime_report.get("lifecycle_card_links", [])
    observed_lifecycle = runtime_report.get(
        "observed_lifecycle"
    ) or observed_lifecycle_for_links(lifecycle_links)
    project_root_value = runtime_report.get("project_root")
    if not project_root_value:
        return {
            "schema": CLIENT_DISPLAY_LINKS_SCHEMA,
            "status": "unavailable",
            "reason": "runtime report has no project_root",
            "links": {},
            "lifecycle_card_links": lifecycle_links,
            "observed_lifecycle": observed_lifecycle,
        }
    if not runtime_report.get("write_performed"):
        return {
            "schema": CLIENT_DISPLAY_LINKS_SCHEMA,
            "status": "unavailable",
            "display_contract": (
                "Surface these local markdown links to the user whenever returning "
                "governed JIKUO runtime output."
            ),
            "links": {},
            "lifecycle_card_links": lifecycle_links,
            "observed_lifecycle": observed_lifecycle,
            "reason": runtime_report.get("reason"),
        }
    project_root = Path(str(project_root_value)).resolve()
    links = {
        "last_card": runtime_link_item(
            project_root=project_root,
            key="last_card",
            label="Latest card",
            ref=runtime_report.get("last_card_ref"),
        ),
        "state_summary": runtime_link_item(
            project_root=project_root,
            key="state_summary",
            label="State summary",
            ref=runtime_report.get("state_summary_ref"),
        ),
        "history_card": runtime_link_item(
            project_root=project_root,
            key="history_card",
            label="History card",
            ref=runtime_report.get("history_ref"),
        ),
        "history_state_summary": runtime_link_item(
            project_root=project_root,
            key="history_state_summary",
            label="History state summary",
            ref=runtime_report.get("history_state_summary_ref"),
        ),
    }
    return {
        "schema": CLIENT_DISPLAY_LINKS_SCHEMA,
        "status": "available",
        "display_contract": (
            "Surface these local markdown links to the user whenever returning "
            "governed JIKUO runtime output."
        ),
        "links": {key: value for key, value in links.items() if value is not None},
        "lifecycle_card_links": lifecycle_links,
        "observed_lifecycle": observed_lifecycle,
        "reason": runtime_report.get("reason"),
    }


def skipped_report(*, project_root: Path, reason: str) -> dict[str, Any]:
    return {
        "schema": RUNTIME_VISIBILITY_REPORT_SCHEMA,
        "status": "skipped",
        "write_performed": False,
        "reason": reason,
        "runtime_root_ref": RUNTIME_DIR_REF,
        "last_card_ref": LAST_CARD_REF,
        "state_summary_ref": STATE_SUMMARY_REF,
        "history_ref": None,
        "history_state_summary_ref": None,
        "lifecycle_card_links": [],
        "observed_lifecycle": observed_lifecycle_for_links([]),
        "project_root": str(project_root),
    }


def prepare_agent_flow_snapshot(
    *, project_root: Path | None, proposal: dict[str, Any]
) -> dict[str, Any]:
    resolved_root = project_root_for(project_root)
    skip_reason = should_skip_runtime_write(resolved_root)
    if skip_reason:
        return skipped_report(project_root=resolved_root, reason=skip_reason)

    paths = runtime_paths(
        resolved_root,
        source_id=str(proposal.get("proposal_id") or proposal.get("schema") or "proposal"),
    )
    updated_at = utc_now_iso()
    report = {
        "schema": RUNTIME_VISIBILITY_REPORT_SCHEMA,
        "status": "planned",
        "write_performed": False,
        "reason": "runtime visibility snapshot planned",
        "runtime_root_ref": rel_ref(paths["runtime_root"], project_root=resolved_root),
        "last_card_ref": rel_ref(paths["last_card"], project_root=resolved_root),
        "state_summary_ref": rel_ref(paths["state_summary"], project_root=resolved_root),
        "history_ref": rel_ref(paths["history_card"], project_root=resolved_root),
        "history_state_summary_ref": rel_ref(
            paths["history_state_summary"],
            project_root=resolved_root,
        ),
        "project_root": str(resolved_root),
        "updated_at_utc": updated_at,
    }
    report["lifecycle_card_links"] = lifecycle_card_links_for_snapshot(
        project_root=resolved_root,
        proposal=proposal,
        runtime_report=report,
    )
    report["observed_lifecycle"] = observed_lifecycle_for_links(
        report["lifecycle_card_links"]
    )
    return report


def persist_prepared_agent_flow_snapshot(
    *,
    proposal: dict[str, Any],
    card_markdown: str,
    prepared_report: dict[str, Any],
) -> dict[str, Any]:
    if prepared_report.get("status") == "skipped":
        return prepared_report

    resolved_root = Path(str(prepared_report["project_root"])).resolve()
    runtime_root = runtime_root_for(resolved_root)
    paths = {
        "last_card": (resolved_root / str(prepared_report["last_card_ref"])).resolve(),
        "state_summary": (
            resolved_root / str(prepared_report["state_summary_ref"])
        ).resolve(),
        "history_card": (resolved_root / str(prepared_report["history_ref"])).resolve(),
        "history_state_summary": (
            resolved_root / str(prepared_report["history_state_summary_ref"])
        ).resolve(),
    }
    for key, value in paths.items():
        if not is_relative_to(value, runtime_root):
            raise ValueError(f"runtime visibility path escaped runtime root: {key}")

    report = dict(prepared_report)
    report["status"] = "ok"
    report["write_performed"] = True
    report["reason"] = "runtime visibility snapshot written"
    state_summary = build_state_summary(
        project_root=resolved_root,
        proposal=proposal,
        runtime_report=report,
        updated_at_utc=str(report["updated_at_utc"]),
    )
    atomic_write_text(paths["last_card"], card_markdown)
    atomic_write_text(paths["history_card"], card_markdown)
    atomic_write_text(
        paths["state_summary"],
        json.dumps(state_summary, ensure_ascii=False, indent=2) + "\n",
    )
    atomic_write_text(
        paths["history_state_summary"],
        json.dumps(state_summary, ensure_ascii=False, indent=2) + "\n",
    )
    return report


def persist_agent_flow_snapshot(
    *,
    project_root: Path | None,
    proposal: dict[str, Any],
    card_markdown: str,
) -> dict[str, Any]:
    prepared = prepare_agent_flow_snapshot(project_root=project_root, proposal=proposal)
    return persist_prepared_agent_flow_snapshot(
        proposal=proposal,
        card_markdown=card_markdown,
        prepared_report=prepared,
    )


def load_state_summary(project_root: Path | None = None) -> dict[str, Any]:
    resolved_root = project_root_for(project_root)
    path = runtime_root_for(resolved_root) / "state_summary.json"
    if not path.is_file():
        return {
            "schema": RUNTIME_STATE_SUMMARY_SCHEMA,
            "status": "missing",
            "project_root": str(resolved_root),
            "state_summary_ref": STATE_SUMMARY_REF,
            "reason": "runtime state summary is missing",
        }
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "schema": RUNTIME_STATE_SUMMARY_SCHEMA,
            "status": "invalid",
            "project_root": str(resolved_root),
            "state_summary_ref": STATE_SUMMARY_REF,
            "reason": f"runtime state summary is invalid JSON: {exc}",
        }
    report.setdefault("status", "available")
    return report


def _history_state_summaries(project_root: Path) -> list[dict[str, Any]]:
    history_root = runtime_root_for(project_root) / "history"
    if not history_root.is_dir():
        return []
    summaries: list[dict[str, Any]] = []
    for path in sorted(history_root.glob("*.json"), key=lambda item: item.name, reverse=True):
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(state, dict):
            continue
        runtime = state.setdefault("runtime_visibility", {})
        if isinstance(runtime, dict):
            runtime.setdefault("history_state_summary_ref", rel_ref(path, project_root=project_root))
        summaries.append(state)
    return summaries


def _semantic_evidence_from_state(state: dict[str, Any]) -> dict[str, Any]:
    evidence = state.get("semantic_intent_evidence")
    if isinstance(evidence, dict):
        return evidence
    return semantic_intent_evidence_for(state)


def _anchor_matches(candidate: dict[str, Any], expected: dict[str, Any]) -> bool:
    if expected.get("status") != "available":
        return True
    if candidate.get("status") != "available":
        return False
    if expected.get("anchor_id") and candidate.get("anchor_id") == expected.get("anchor_id"):
        return True
    return bool(
        expected.get("session_id")
        and expected.get("turn_id")
        and candidate.get("session_id") == expected.get("session_id")
        and candidate.get("turn_id") == expected.get("turn_id")
    )


def _semantic_ref_matches(
    *,
    evidence: dict[str, Any],
    state: dict[str, Any],
    expected_anchor: dict[str, Any],
    semantic_intent_ref: str | None,
) -> bool:
    candidate_anchor = turn_anchor.normalize_turn_anchor(evidence.get("turn_anchor"))
    ref = str(semantic_intent_ref or "").strip()
    if not ref:
        return _anchor_matches(candidate_anchor, expected_anchor)
    if ref == "latest":
        return True
    if ref.startswith("anchor:"):
        anchor_id = ref.split(":", 1)[1]
        return bool(anchor_id and candidate_anchor.get("anchor_id") == anchor_id)
    runtime = state.get("runtime_visibility") or {}
    source = state.get("source") or {}
    return ref in {
        str(evidence.get("semantic_intent_ref") or ""),
        str(runtime.get("history_ref") or ""),
        str(runtime.get("history_state_summary_ref") or ""),
        str(source.get("proposal_id") or ""),
    }


def inherit_host_semantic_intent(
    *,
    project_root: Path | None,
    turn_anchor_input: dict[str, Any] | None = None,
    semantic_intent_ref: str | None = None,
) -> dict[str, Any] | None:
    """Load prompt-free host semantic intent previously stored in runtime state."""

    resolved_root = project_root_for(project_root)
    expected_anchor = turn_anchor.normalize_turn_anchor(turn_anchor_input)
    candidates = [load_state_summary(resolved_root)]
    candidates.extend(_history_state_summaries(resolved_root))
    for state in candidates:
        if not isinstance(state, dict) or state.get("status") in {"missing", "invalid"}:
            continue
        evidence = _semantic_evidence_from_state(state)
        if not isinstance(evidence, dict):
            continue
        if not _semantic_ref_matches(
            evidence=evidence,
            state=state,
            expected_anchor=expected_anchor,
            semantic_intent_ref=semantic_intent_ref,
        ):
            continue
        host = evidence.get("host_semantic_intent")
        if not isinstance(host, dict):
            continue
        if host.get("status") != "provided" or host.get("provider") != "host_ai":
            continue
        inherited = dict(host)
        semantic_ref = evidence.get("semantic_intent_ref")
        if semantic_ref:
            inherited["semantic_intent_ref"] = semantic_ref
        inherited["evidence_source_kind"] = "runtime_inherited"
        inherited.setdefault("turn_anchor", evidence.get("turn_anchor"))
        runtime = state.get("runtime_visibility") or {}
        source = state.get("source") or {}
        inherited["inherited_from"] = {
            "semantic_intent_ref": semantic_ref,
            "history_ref": runtime.get("history_ref"),
            "history_state_summary_ref": runtime.get("history_state_summary_ref"),
            "proposal_id": source.get("proposal_id"),
            "lifecycle_event": source.get("event"),
            "updated_at_utc": state.get("updated_at_utc"),
            "evidence_source_kind": evidence.get("evidence_source_kind"),
        }
        return inherited
    return None


def load_last_card(project_root: Path | None = None) -> tuple[str | None, dict[str, Any]]:
    resolved_root = project_root_for(project_root)
    path = runtime_root_for(resolved_root) / "last_card.md"
    if not path.is_file():
        return None, {
            "schema": RUNTIME_VISIBILITY_REPORT_SCHEMA,
            "status": "missing",
            "project_root": str(resolved_root),
            "last_card_ref": LAST_CARD_REF,
            "reason": "runtime last card is missing",
        }
    return path.read_text(encoding="utf-8"), {
        "schema": RUNTIME_VISIBILITY_REPORT_SCHEMA,
        "status": "available",
        "project_root": str(resolved_root),
        "last_card_ref": LAST_CARD_REF,
    }


def index_refresh_commands(project_root: Path) -> dict[str, str]:
    root = str(project_root)
    return {
        "dry_run": (
            'python -B -m jikuo.task_session index --dry-run '
            f'--project-root "{root}" --format json'
        ),
        "refresh": (
            'python -B -m jikuo.task_session index --refresh '
            f'--project-root "{root}" --confirm-update-project-state-index '
            '--approval-phrase "<exact user phrase as spoken>" --format json'
        ),
    }


def build_task_session_index_status(project_root: Path | None = None) -> dict[str, Any]:
    resolved_root = project_root_for(project_root)
    try:
        plan = task_session.build_index_refresh_plan(project_root=resolved_root)
    except Exception as exc:  # pragma: no cover - defensive display boundary
        return {
            "schema": TASK_SESSION_INDEX_STATUS_SCHEMA,
            "status": "unavailable",
            "project_root": str(resolved_root),
            "project_state_ref": ".jikuo/project_state.yaml",
            "reason": f"task-session index status unavailable: {exc}",
        }

    current_refs = plan.get("current_latest_task_session_refs") or []
    proposed_refs = plan.get("proposed_latest_task_session_refs") or []
    can_refresh = bool(plan.get("can_refresh"))
    needs_refresh = can_refresh and not task_session.refs_equal(current_refs, proposed_refs)
    if not can_refresh:
        status = "unavailable"
        reason = "task-session index refresh plan has refusal reasons"
    elif needs_refresh:
        status = "stale"
        reason = "latest_task_session_refs does not match discovered task-session files"
    else:
        status = "current"
        reason = "latest_task_session_refs already matches discovered task-session files"

    return {
        "schema": TASK_SESSION_INDEX_STATUS_SCHEMA,
        "status": status,
        "project_root": str(resolved_root),
        "project_state_ref": ".jikuo/project_state.yaml",
        "current_latest_task_session_ref_count": len(current_refs),
        "discovered_task_session_count": int(plan.get("discovered_session_count", 0)),
        "proposed_latest_task_session_ref_count": len(proposed_refs),
        "can_refresh": can_refresh,
        "would_update_project_state": needs_refresh,
        "refusal_reasons": plan.get("refusal_reasons", []),
        "warnings": plan.get("warnings", []),
        "commands": index_refresh_commands(resolved_root) if needs_refresh else {},
        "reason": reason,
    }


def attach_task_session_index_status(
    summary: dict[str, Any],
    *,
    project_root: Path | None = None,
) -> dict[str, Any]:
    output = dict(summary)
    output["task_session_index"] = build_task_session_index_status(
        project_root=project_root,
    )
    return output


def attach_activation_settings_status(
    summary: dict[str, Any],
    *,
    project_root: Path | None = None,
) -> dict[str, Any]:
    output = dict(summary)
    output["activation_settings"] = activation_settings.build_status_report(
        project_root=project_root,
    )
    return output


def format_state_summary(summary: dict[str, Any]) -> str:
    status = summary.get("status", "available")
    lines = [
        "# JIKUO Runtime Status",
        "",
        f"- Status: `{status}`",
        f"- Project root: `{summary.get('project_root')}`",
    ]
    if summary.get("updated_at_utc"):
        lines.append(f"- Updated at: `{summary['updated_at_utc']}`")
    runtime = summary.get("runtime_visibility") or {}
    last_ref = runtime.get("last_card_ref") or summary.get("last_card_ref") or LAST_CARD_REF
    state_ref = runtime.get("state_summary_ref") or summary.get("state_summary_ref") or STATE_SUMMARY_REF
    lines.extend(
        [
            f"- Last card: `{last_ref}`",
            f"- State summary: `{state_ref}`",
        ]
    )
    display_links = summary.get("client_display_links") or {}
    if display_links:
        lines.extend(["", "## JIKUO Runtime Links", ""])
        links = display_links.get("links") or {}
        for key in ("last_card", "state_summary", "history_card"):
            item = links.get(key)
            if item:
                lines.append(f"- {item['label']}: {item['markdown']}")
        if not links:
            lines.append(f"- Status: `{display_links.get('status', 'unavailable')}`")
            if display_links.get("reason"):
                lines.append(f"- Reason: {display_links['reason']}")
    semantic = summary.get("semantic_intent_coverage") or {}
    if semantic:
        lines.extend(
            [
                "",
                "## Semantic Intent Coverage",
                "",
                f"- Coverage status: `{semantic.get('coverage_status')}`",
                f"- Semantic intent status: `{semantic.get('semantic_intent_status')}`",
                f"- Evidence status: `{semantic.get('evidence_status')}`",
                f"- Provider: `{semantic.get('provider')}`",
                f"- Evidence source: `{semantic.get('evidence_source_kind', 'unavailable')}`",
                f"- Semantic intent ref: `{semantic.get('semantic_intent_ref') or 'unavailable'}`",
                f"- Required: `{str(semantic.get('required', False)).lower()}`",
                f"- Policy scopes: `{', '.join(semantic.get('policy_scopes') or []) or 'none'}`",
            ]
        )
        if semantic.get("gap_reason"):
            lines.append(f"- Gap reason: `{semantic.get('gap_reason')}`")
    anchor = summary.get("turn_anchor") or {}
    if anchor:
        lines.extend(
            [
                "",
                "## Turn Anchor",
                "",
                f"- Status: `{anchor.get('status')}`",
                f"- Anchor id: `{anchor.get('anchor_id') or 'unavailable'}`",
                f"- Label: `{turn_anchor.display_label(anchor)}`",
                f"- Identity strength: `{anchor.get('identity_strength')}`",
                f"- Prompt digest: `{anchor.get('prompt_digest_status')}`",
            ]
        )
        if anchor.get("gap_reason"):
            lines.append(f"- Gap reason: `{anchor.get('gap_reason')}`")
    envelope = summary.get("execution_envelope") or {}
    if envelope:
        lifecycle = envelope.get("lifecycle") or {}
        privacy = envelope.get("privacy") or {}
        links = envelope.get("links") or {}
        private_ref = links.get("private_turn_input_ref") or {}
        lines.extend(
            [
                "",
                "## Execution Envelope",
                "",
                f"- Envelope id: `{envelope.get('envelope_id')}`",
                f"- Lifecycle state: `{lifecycle.get('state')}`",
                f"- Lifecycle event: `{lifecycle.get('event')}`",
                f"- Raw prompt storage: `{privacy.get('raw_prompt_storage', 'none')}`",
                (
                    "- Raw prompt exposed in audit: "
                    f"`{str(privacy.get('raw_prompt_exposed_in_audit', False)).lower()}`"
                ),
            ]
        )
        if private_ref:
            lines.append(
                f"- Private input index ref: `{private_ref.get('index_ref')}`"
            )
            lines.append(
                f"- Private input record id: `{private_ref.get('record_id') or 'pending'}`"
            )
    artifact = summary.get("artifact_assurance") or {}
    if artifact:
        read = artifact.get("read_assurance") or {}
        write = artifact.get("write_assurance") or {}
        gaps = artifact.get("gap_report") or {}
        lines.extend(
            [
                "",
                "## Artifact Assurance",
                "",
                f"- Status: `{artifact.get('status')}`",
                f"- Read assurance status: `{read.get('status')}`",
                f"- Write assurance status: `{write.get('status')}`",
                f"- Required reads: `{read.get('required_read_count', 0)}`",
                f"- Read evidence: `{read.get('read_evidence_count', 0)}`",
                f"- Completion-check documents: `{write.get('completion_check_candidate_count', 0)}`",
                f"- Completion-check documents not evaluated: `{len(write.get('completion_check_not_evaluated') or [])}`",
                f"- Applicable required writes: `{write.get('required_write_count', 0)}`",
                f"- Planned writes: `{write.get('planned_write_count', 0)}`",
                f"- Actual writes: `{write.get('actual_write_count', 0)}`",
                f"- Gap count: `{gaps.get('gap_count', 0)}`",
            ]
        )
    task_session_index = summary.get("task_session_index") or {}
    if task_session_index:
        lines.extend(
            [
                "",
                "## Task-Session Index",
                "",
                f"- Status: `{task_session_index.get('status')}`",
                (
                    "- Indexed latest refs: "
                    f"`{task_session_index.get('current_latest_task_session_ref_count')}`"
                ),
                (
                    "- Discovered task sessions: "
                    f"`{task_session_index.get('discovered_task_session_count')}`"
                ),
            ]
        )
        if task_session_index.get("reason"):
            lines.append(f"- Reason: {task_session_index['reason']}")
        commands = task_session_index.get("commands") or {}
        if commands:
            lines.extend(
                [
                    "- Review command:",
                    f"  `{commands['dry_run']}`",
                    "- Refresh command:",
                    f"  `{commands['refresh']}`",
                ]
            )
    activation = summary.get("activation_settings") or {}
    if activation:
        lines.extend(
            [
                "",
                "## Activation Settings",
                "",
                f"- Status: `{activation.get('status')}`",
                f"- Desired trigger mode: `{activation.get('desired_trigger_mode')}`",
                f"- Effective enforcement: `{activation.get('effective_enforcement_level')}`",
                (
                    "- Strict mounted requires adapter: "
                    f"`{str(activation.get('strict_mounted_requires_adapter')).lower()}`"
                ),
            ]
        )
        if activation.get("reason"):
            lines.append(f"- Reason: {activation['reason']}")
    counts = summary.get("counts") or {}
    if counts:
        lines.extend(
            [
                "",
                "| Metric | Count |",
                "|---|---:|",
                f"| Cards | {counts.get('card_count', 0)} |",
                f"| Triggered policies | {counts.get('triggered_policy_count', 0)} |",
                f"| Missing evidence | {counts.get('missing_evidence_count', 0)} |",
                f"| Required actions | {counts.get('required_action_count', 0)} |",
            ]
        )
    policy_runtime_status = summary.get("policy_runtime_status") or {}
    if policy_runtime_status:
        lines.extend(
            [
                "",
                "## Policy Runtime Status",
                "",
                f"- Policy store: `{policy_runtime_status.get('policy_store_status')}`",
                f"- Policy eval: `{policy_runtime_status.get('policy_eval_status')}`",
                f"- Evidence check: `{policy_runtime_status.get('policy_evidence_check_status')}`",
                f"- Active policies: `{policy_runtime_status.get('active_policy_count')}`",
                f"- Triggered policies: `{policy_runtime_status.get('triggered_policy_count')}`",
                f"- Missing evidence: `{policy_runtime_status.get('missing_evidence_count')}`",
            ]
        )
    if summary.get("reason"):
        lines.extend(["", f"- Reason: {summary['reason']}"])
    lifecycle_links = display_links.get("lifecycle_card_links") or []
    if lifecycle_links:
        lines.extend(["", "### Observed Lifecycle", ""])
        for item in lifecycle_links:
            lines.append(f"- `{item.get('lifecycle_event')}`: {item.get('markdown')}")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect JIKUO runtime visibility.")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--last-card", action="store_true")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.last_card:
        card, report = load_last_card(project_root=args.project_root)
        if args.format == "json":
            output = dict(report)
            output["card_markdown"] = card
            print(json.dumps(output, ensure_ascii=False, indent=2))
        elif card is not None:
            print(card, end="" if card.endswith("\n") else "\n")
        else:
            print(format_state_summary(report), end="")
        return 0 if report["status"] == "available" else 2

    summary = attach_activation_settings_status(
        attach_task_session_index_status(
            load_state_summary(project_root=args.project_root),
            project_root=args.project_root,
        ),
        project_root=args.project_root,
    )
    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(format_state_summary(summary), end="")
    return 0 if summary.get("status") == "available" else 2


if __name__ == "__main__":
    sys.exit(main())
