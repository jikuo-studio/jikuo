"""Local deterministic JIKUO desktop-agent flow runner.

This runner composes existing atoms into chat-ready proposals and narrow
guarded apply operations. It is not a general command executor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

if __package__:
    from . import project_state, policy_store, task_session, task_session_cards
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import project_state
    import policy_store
    import task_session
    import task_session_cards


PREVIOUS_PROPOSAL_SCHEMA = "jikuo.agent_flow_proposal.v0"
PROPOSAL_SCHEMA = "jikuo.agent_flow_proposal.v1"
APPLY_RESULT_SCHEMA = "jikuo.agent_flow_apply_result.v0"
GENERIC_CARD_SCHEMA = "jikuo.agent_flow_card.v0"
TRIGGER_DECISION_SCHEMA = "jikuo.agent_trigger_decision.v0"
APPROVAL_PHRASE_PLACEHOLDER = "<exact user phrase as spoken>"
POLICY_STORE_STATUS_UNAVAILABLE = "unavailable"
POLICY_EVAL_STATUS_NOT_EVALUATED = "not_evaluated"
POLICY_CONDITION_EVAL_STATUS_NOT_EVALUATED = "not_evaluated"
POLICY_FEEDBACK_OPTIONS_SCHEMA = "jikuo.policy_feedback_options.v0"
POLICY_FEEDBACK_TYPES = {"not_applicable", "defer", "needs_scope_narrowing"}
APPLY_OPERATIONS = {"policy_evolution_write", "task_session_evidence_update"}

EVENT_ALIASES = {
    "status": "project_status",
    "project_status": "project_status",
    "start": "task_start",
    "task_start": "task_start",
    "continue": "task_continue",
    "task_continue": "task_continue",
    "index": "index_preview",
    "index_preview": "index_preview",
    "evidence": "evidence_review",
    "evidence_review": "evidence_review",
    "policy_evidence": "policy_evidence_record",
    "policy_evidence_record": "policy_evidence_record",
    "policy_feedback": "policy_feedback_record",
    "policy_feedback_record": "policy_feedback_record",
    "policy_evidence_check": "policy_evidence_check",
    "policy_write_plan": "policy_write_plan",
    "configure_policy": "policy_write_plan",
    "policy_configure": "policy_write_plan",
    "policy_evolution_plan": "policy_evolution_plan",
    "policy_refinement_plan": "policy_evolution_plan",
    "refine_policy": "policy_evolution_plan",
    "verification": "verification_review",
    "verification_review": "verification_review",
    "completion": "completion_review",
    "completion_review": "completion_review",
    "handoff": "handoff",
    "audit": "audit_report",
    "audit_report": "audit_report",
}

NO_WRITE_ATOMS = {
    "CAP-PROJECT-STATE-STATUS-01",
    "CAP-PROJECT-STATE-INIT-DRYRUN-01",
    "CAP-TASK-START-DRYRUN-01",
    "CAP-TASK-STATUS-01",
    "CAP-TASK-INDEX-DRYRUN-01",
    "CAP-TASK-UPDATE-DRYRUN-01",
    "CAP-CARD-TASKSESSION-01",
    "CAP-CHECKER-01",
    "CAP-CHECKER-JSON-01",
    "CAP-POLICY-STORE-STATUS-01",
    "CAP-POLICY-TRIGGER-EVALUATE-01",
    "CAP-POLICY-CONDITION-EVALUATOR-01",
    "CAP-POLICY-EVIDENCE-CHECK-01",
    "CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01",
    "CAP-POLICY-FEEDBACK-PERSIST-PROPOSE-01",
    "CAP-POLICY-EVIDENCE-INGEST-01",
    "CAP-POLICY-STORE-WRITE-PROPOSE-01",
    "CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01",
}


def stable_id(prefix: str, seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}"


def normalize_event(event: str) -> str | None:
    key = event.strip().lower().replace(" ", "_").replace("-", "_")
    return EVENT_ALIASES.get(key)


def atom_trace(
    *,
    loop_step_id: str,
    atom_id: str,
    mode: str,
    status: str,
    summary: str,
) -> dict[str, Any]:
    return {
        "loop_step_id": loop_step_id,
        "atom_id": atom_id,
        "mode": mode,
        "status": status,
        "summary": summary,
    }


def generic_card(
    *,
    card_kind: str,
    status: str,
    title: str,
    summary: str,
    shown_inputs: list[str] | None = None,
    shown_outputs: list[str] | None = None,
    refusal_reasons: list[str] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    seed = "|".join([card_kind, title, summary])
    return {
        "schema": GENERIC_CARD_SCHEMA,
        "card_id": stable_id("card", seed),
        "card_kind": card_kind,
        "status": status,
        "title": title,
        "user_facing_summary": summary,
        "shown_inputs": shown_inputs or [],
        "shown_outputs": shown_outputs or [],
        "refusal_reasons": refusal_reasons or [],
        "next_actions": next_actions or [],
        "write_effect": {
            "target": "none",
            "effect": "no durable write is performed by agent_flow.py propose",
            "non_effects": [
                "does not create .jikuo/task_sessions/",
                "does not create .jikuo/policies/",
                "does not update .jikuo/project_state.yaml",
                "does not capture raw chat transcript",
            ],
        },
    }


def build_policy_context(
    *,
    project_root: Path | None,
    event: str,
    produced_evidence: list[dict[str, Any]] | None = None,
    task_session_id: str | None = None,
    task_type: str | None = None,
    jikuo_layer: str | None = None,
    changed_paths: list[str] | None = None,
    added_paths: list[str] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """Expose policy-store state plus no-write trigger/evidence evaluation."""

    report = policy_store.evaluate_policy_triggers(
        project_root=project_root,
        event=event,
        produced_evidence=produced_evidence,
        task_session_id=task_session_id,
        task_type=task_type,
        jikuo_layer=jikuo_layer,
        changed_paths=changed_paths,
        added_paths=added_paths,
    )
    if report["policy_store_status"] == "missing":
        next_actions = [
            "initialize policy store in a later guarded configuration flow",
            "keep using baseline no-write JIKUO proposal for this task",
        ]
    elif report["policy_store_status"] in {"stale", "conflict"}:
        next_actions = [
            "review policy store manifest and refs before policy-aware evaluation",
            "keep using baseline no-write JIKUO proposal for this task",
        ]
    elif report["policy_store_status"] == "active":
        next_actions = [
            "review triggered policy actions and evidence status",
            "keep using baseline no-write JIKUO proposal for this task",
        ]
    else:
        next_actions = list(report.get("next_actions", [])) or [
            "review triggered policy actions and evidence status"
        ]

    traces = [
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-POLICY-STORE-STATUS-01",
            mode="no-write",
            status=report["policy_store_status"],
            summary="inspected project-local policy-store status",
        ),
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-POLICY-TRIGGER-EVALUATE-01",
            mode="no-write",
            status=report["policy_eval_status"],
            summary="evaluated active policy triggers without executing actions",
        ),
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-POLICY-CONDITION-EVALUATOR-01",
            mode="no-write",
            status=report.get("policy_condition_eval_status", "not_evaluated"),
            summary="evaluated active policy conditions without executing actions",
        ),
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-POLICY-EVIDENCE-CHECK-01",
            mode="no-write",
            status=report["policy_evidence_check_status"],
            summary="matched required policy evidence against runner-produced evidence without writing",
        ),
    ]
    return {
        "policy_store_status": report["policy_store_status"],
        "active_policy_refs": report["active_policy_refs"],
        "policy_snapshot_ref": report["policy_snapshot_ref"],
        "policy_eval_status": report["policy_eval_status"],
        "policy_condition_eval_status": report.get("policy_condition_eval_status"),
        "policy_evidence_check_status": report["policy_evidence_check_status"],
        "task_session_id": report.get("task_session_id"),
        "evidence_source_refs": report.get("evidence_source_refs", []),
        "status_reason": report["status_reason"],
        "evidence_status_reason": report["evidence_status_reason"],
        "warnings": report["warnings"],
        "next_actions": next_actions,
    }, traces, {
        "triggered_policies": report["triggered_policies"],
        "required_actions": report["required_actions"],
        "condition_reports": report.get("condition_reports", []),
        "evidence_status": report["evidence_status"],
        "missing_evidence_reports": report["missing_evidence_reports"],
    }


def build_policy_not_inspected_context() -> dict[str, Any]:
    return {
        "policy_store_status": POLICY_STORE_STATUS_UNAVAILABLE,
        "active_policy_refs": [],
        "policy_snapshot_ref": None,
        "policy_eval_status": POLICY_EVAL_STATUS_NOT_EVALUATED,
        "policy_condition_eval_status": POLICY_CONDITION_EVAL_STATUS_NOT_EVALUATED,
        "policy_evidence_check_status": "not_evaluated",
        "task_session_id": None,
        "evidence_source_refs": [],
        "status_reason": "policy store was not inspected because the JIKUO event was unsupported",
        "evidence_status_reason": "policy evidence check was not run",
        "warnings": ["unsupported_event_prevented_policy_store_inspection"],
        "next_actions": ["retry with a supported event before policy-store inspection"],
    }


def produced_policy_evidence_for(
    *,
    event: str | None,
    cards: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if event != "task_start":
        return []

    evidence: list[dict[str, Any]] = []
    for card in cards:
        if card.get("status") == "refused":
            continue
        card_id = str(card.get("card_id") or "")
        evidence.append(
            {
                "evidence_id": stable_id(
                    "evidence",
                    "|".join([event, card_id, "render_pre_task_review"]),
                ),
                "evidence_type": "card_rendered",
                "action_type": "render_pre_task_review",
                "source": {
                    "kind": "agent_flow_card",
                    "ref": card_id or None,
                },
                "producer": {
                    "actor": "agent",
                    "tool": "tools/jikuo/agent_flow.py",
                },
                "status": "ok",
                "summary": "agent_flow rendered the task-start proposal card in chat",
            }
        )
    return evidence


def build_policy_feedback_options(
    *,
    triggered_policies: list[dict[str, Any]],
    missing_evidence_reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Project lightweight user feedback choices without persisting decisions."""

    if not triggered_policies:
        return []

    policy_refs = sorted(
        {
            str(item.get("policy_ref"))
            for item in triggered_policies
            if item.get("policy_ref")
        }
    )
    missing_evidence_types = sorted(
        {
            str(missing.get("required_type"))
            for report in missing_evidence_reports
            for missing in report.get("missing", [])
            if missing.get("required_type")
        }
    )
    missing_count = sum(
        len(report.get("missing", [])) for report in missing_evidence_reports
    )

    return [
        {
            "schema": POLICY_FEEDBACK_OPTIONS_SCHEMA,
            "feedback_type": "not_applicable",
            "status": "available_report_only",
            "applies_to_policy_refs": policy_refs,
            "effect": "mark the triggered policy as not applicable for this task in chat only",
            "persistence": "not_persisted_by_agent_flow_propose",
            "next_action": (
                "record a reviewed exemption in a later approved persistence slice "
                "if the user confirms it should be kept"
            ),
        },
        {
            "schema": POLICY_FEEDBACK_OPTIONS_SCHEMA,
            "feedback_type": "defer",
            "status": "available_report_only",
            "applies_to_policy_refs": policy_refs,
            "missing_evidence_count": missing_count,
            "missing_evidence_types": missing_evidence_types,
            "effect": "continue the task while keeping missing policy evidence visible in chat",
            "persistence": "not_persisted_by_agent_flow_propose",
            "next_action": "review missing evidence before final delivery or guarded apply",
        },
        {
            "schema": POLICY_FEEDBACK_OPTIONS_SCHEMA,
            "feedback_type": "needs_scope_narrowing",
            "status": "available_report_only",
            "applies_to_policy_refs": policy_refs,
            "effect": "flag this policy trigger as potentially too broad for later refinement",
            "persistence": "not_persisted_by_agent_flow_propose",
            "next_action": (
                "plan a future policy revision or supersession instead of editing "
                "the active policy during proposal mode"
            ),
        },
    ]


def trigger_decision_for(
    *,
    raw_event: str,
    event: str | None,
    user_phrase: str | None,
    refusals: list[str],
) -> dict[str, Any]:
    trigger_match_status = "matched" if event else "unmatched"
    execution_readiness = (
        "ready"
        if event and not refusals
        else "blocked"
        if event
        else "unsupported"
    )
    return {
        "schema": TRIGGER_DECISION_SCHEMA,
        "trigger_source": "explicit_user_shortcut"
        if user_phrase
        else "explicit_user_natural_language",
        "user_phrase": user_phrase or raw_event,
        "invocation_scenario": event or "ambiguous",
        "confidence": "event_match" if event else "unmatched",
        "confidence_basis": "canonical_event_mapping",
        "trigger_match": {
            "status": trigger_match_status,
            "basis": "canonical_event_mapping",
            "raw_event": raw_event,
            "normalized_event": event,
        },
        "intent_classification": {
            "confidence": "not_evaluated_by_runner",
            "basis": "agent_supplied_event_arg",
            "note": "agent_flow.py maps event args; it does not infer natural-language intent",
        },
        "execution_readiness": execution_readiness,
        "may_call_no_write_atoms": bool(event),
        "may_request_guarded_write": bool(event and not refusals),
        "durable_write_approved": False,
        "required_clarification": refusals,
    }


def card_status(card: dict[str, Any]) -> str:
    return str(card.get("status", "review"))


def build_project_status_cards(
    *, project_root: Path | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    report = project_state.build_bootstrap_report(
        project_root=project_root,
        command="status",
        include_would_create=False,
    )
    traces = [
        atom_trace(
            loop_step_id="DPL-03",
            atom_id="CAP-PROJECT-STATE-STATUS-01",
            mode="no-write",
            status=report["state_status"],
            summary="inspected JIKUO project-state status",
        )
    ]
    outputs = [
        f"project_root: {report['project_root']}",
        f"state_status: {report['state_status']}",
        f"state_file: {report['state_file']}",
    ]
    next_actions = list(report.get("next_actions", []))
    if report["state_status"] == "missing":
        draft = project_state.build_bootstrap_report(
            project_root=project_root,
            command="init",
            include_would_create=True,
        )
        traces.append(
            atom_trace(
                loop_step_id="DPL-03",
                atom_id="CAP-PROJECT-STATE-INIT-DRYRUN-01",
                mode="no-write",
                status=draft["state_status"],
                summary="built project-state init dry-run draft",
            )
        )
        would_create = draft.get("would_create") or {}
        outputs.append(f"would_create_schema: {would_create.get('schema')}")
        next_actions = list(draft.get("next_actions", next_actions))

    card = generic_card(
        card_kind="project_status",
        status="ok" if report["state_status"] == "initialized" else "review",
        title="JIKUO project status",
        summary="Project-local JIKUO state was inspected without writing files.",
        shown_outputs=outputs,
        refusal_reasons=list(report.get("warnings", [])),
        next_actions=next_actions,
    )
    return [card], traces, []


def build_task_start_cards(
    *,
    project_root: Path | None,
    task_title: str | None,
    owner_agent: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    if not task_title:
        refusal = "task_title_required_for_task_start"
        card = generic_card(
            card_kind="task_start_refusal",
            status="refused",
            title="Task start needs a title",
            summary="A task title is required before JIKUO can preview a task session.",
            refusal_reasons=[refusal],
            next_actions=["provide --task-title before retrying task_start"],
        )
        return [card], [], [refusal]

    plan = task_session.build_start_plan(
        project_root=project_root,
        task_title=task_title,
        owner_agent=owner_agent,
    )
    card = task_session_cards.build_card(plan)
    traces = [
        atom_trace(
            loop_step_id="DPL-03",
            atom_id="CAP-PROJECT-STATE-STATUS-01",
            mode="no-write",
            status=plan["project_state_status"],
            summary="inspected project state during task start planning",
        ),
        atom_trace(
            loop_step_id="DPL-04",
            atom_id="CAP-TASK-START-DRYRUN-01",
            mode="no-write",
            status="ok" if plan.get("can_start") else "refused",
            summary="built task-session start dry-run plan",
        ),
        atom_trace(
            loop_step_id="DPL-06",
            atom_id="CAP-CARD-TASKSESSION-01",
            mode="no-write",
            status=card_status(card),
            summary="projected task-session start plan into a desktop card",
        ),
    ]
    return [card], traces, []


def build_index_cards(
    *, project_root: Path | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    plan = task_session.build_index_refresh_plan(project_root=project_root)
    card = task_session_cards.build_card(plan)
    traces = [
        atom_trace(
            loop_step_id="DPL-04",
            atom_id="CAP-TASK-INDEX-DRYRUN-01",
            mode="no-write",
            status="ok" if plan.get("can_refresh") else "refused",
            summary="built task-session index dry-run plan",
        ),
        atom_trace(
            loop_step_id="DPL-06",
            atom_id="CAP-CARD-TASKSESSION-01",
            mode="no-write",
            status=card_status(card),
            summary="projected index plan into a desktop card",
        ),
    ]
    return [card], traces, []


def build_continue_cards(
    *,
    project_root: Path | None,
    session_id: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    if not session_id:
        refusal = "session_id_required_for_task_continue"
        card = generic_card(
            card_kind="task_continue_refusal",
            status="refused",
            title="Task continuation needs a session id",
            summary="A task-session id is required before JIKUO can continue a governed task.",
            refusal_reasons=[refusal],
            next_actions=["provide --session-id before retrying task_continue"],
        )
        return [card], [], [refusal]

    report = task_session.build_status_report(
        project_root=project_root,
        session_id=session_id,
    )
    traces = [
        atom_trace(
            loop_step_id="DPL-04",
            atom_id="CAP-TASK-STATUS-01",
            mode="no-write",
            status=report["session_status"],
            summary="inspected task-session status",
        )
    ]
    card = generic_card(
        card_kind="task_continue_status",
        status="ok" if report["session_status"] == "found" else "missing",
        title="Task-session continuation status",
        summary="Task-session status was inspected without writing files.",
        shown_inputs=[f"session_id: {session_id}"],
        shown_outputs=[
            f"session_status: {report['session_status']}",
            f"matched_paths: {len(report['matched_paths'])}",
        ],
        refusal_reasons=list(report.get("warnings", [])),
        next_actions=["continue from the matched task session"]
        if report["session_status"] == "found"
        else ["create or select an explicit task-session before continuing"],
    )
    return [card], traces, []


def patch_kind_for_event(event: str) -> str:
    if event == "evidence_review":
        return "evidence"
    if event == "verification_review":
        return "verification"
    if event == "completion_review":
        return "completion"
    if event == "handoff":
        return "handoff"
    return "inspect"


def build_update_cards(
    *,
    event: str,
    project_root: Path | None,
    session_id: str | None,
    summary: str | None,
    evidence_kind: str | None,
    evidence_ref: str | None,
    command_name: str | None,
    exit_code: int | None,
    verification_layer: str | None,
    completion_status: str | None,
    owner_agent: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    if not session_id:
        refusal = "session_id_required_for_lifecycle_preview"
        card = generic_card(
            card_kind="task_lifecycle_refusal",
            status="refused",
            title="Lifecycle preview needs a session id",
            summary="An explicit task-session id is required before lifecycle preview.",
            refusal_reasons=[refusal],
            next_actions=["provide --session-id before retrying lifecycle preview"],
        )
        return [card], [], [refusal]

    patch_kind = patch_kind_for_event(event)
    plan = task_session.build_task_session_update_plan(
        project_root=project_root,
        session_id=session_id,
        patch_kind=patch_kind,
        owner_agent=owner_agent,
        summary=summary,
        evidence_kind=evidence_kind,
        evidence_ref=evidence_ref,
        command_name=command_name,
        exit_code=exit_code,
        verification_layer=verification_layer,
        completion_status=completion_status or "ready_for_review",
    )
    card = task_session_cards.build_card(plan)
    traces = [
        atom_trace(
            loop_step_id="DPL-04",
            atom_id="CAP-TASK-UPDATE-DRYRUN-01",
            mode="no-write",
            status="ok" if plan.get("can_update") else "review",
            summary=f"built task-session {patch_kind} dry-run plan",
        ),
        atom_trace(
            loop_step_id="DPL-06",
            atom_id="CAP-CARD-TASKSESSION-01",
            mode="no-write",
            status=card_status(card),
            summary="projected lifecycle plan into a desktop card",
        ),
    ]
    return [card], traces, []


def build_policy_evidence_record_cards(
    *,
    project_root: Path | None,
    session_id: str | None,
    policy_ref: str | None,
    action_ref: str | None,
    requirement_ref: str | None,
    evidence_kind: str | None,
    evidence_ref: str | None,
    summary: str | None,
    owner_agent: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    refusals: list[str] = []
    if not session_id:
        refusals.append("session_id_required_for_policy_evidence_record")
    if not policy_ref:
        refusals.append("policy_ref_required_for_policy_evidence_record")
    if not action_ref:
        refusals.append("action_ref_required_for_policy_evidence_record")
    if not requirement_ref:
        refusals.append("requirement_ref_required_for_policy_evidence_record")
    if not evidence_kind:
        refusals.append("evidence_kind_required_for_policy_evidence_record")
    if not evidence_ref:
        refusals.append("evidence_ref_required_for_policy_evidence_record")

    if refusals:
        card = generic_card(
            card_kind="policy_evidence_record_refusal",
            status="refused",
            title="Policy evidence record needs explicit refs",
            summary=(
                "Policy evidence persistence proposal requires explicit session, "
                "policy, action, requirement, evidence kind, and evidence ref."
            ),
            refusal_reasons=refusals,
            next_actions=["provide explicit refs before proposing evidence persistence"],
        )
        trace = atom_trace(
            loop_step_id="DPL-11",
            atom_id="CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01",
            mode="no-write",
            status="refused",
            summary="refused policy evidence persistence proposal because required refs were missing",
        )
        return [card], [trace], refusals

    assert session_id is not None
    assert policy_ref is not None
    assert action_ref is not None
    assert requirement_ref is not None
    assert evidence_kind is not None
    assert evidence_ref is not None

    compact_summary = summary or (
        f"Policy evidence {evidence_kind} satisfies {requirement_ref} "
        f"for {policy_ref} / {action_ref}."
    )
    compact_ref = (
        f"policy_ref={policy_ref};action_ref={action_ref};"
        f"requirement_ref={requirement_ref};evidence_ref={evidence_ref}"
    )
    plan = task_session.build_task_session_update_plan(
        project_root=project_root,
        session_id=session_id,
        patch_kind="evidence",
        owner_agent=owner_agent,
        summary=compact_summary,
        evidence_kind=f"policy_evidence:{evidence_kind}",
        evidence_ref=compact_ref,
    )
    card = task_session_cards.build_card(plan)
    status = "ok" if plan.get("can_update") else "refused"
    traces = [
        atom_trace(
            loop_step_id="DPL-11",
            atom_id="CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01",
            mode="no-write",
            status=status,
            summary="built guarded task-session evidence persistence proposal from policy evidence refs",
        ),
        atom_trace(
            loop_step_id="DPL-04",
            atom_id="CAP-TASK-UPDATE-DRYRUN-01",
            mode="no-write",
            status=status,
            summary="built task-session evidence append dry-run plan",
        ),
        atom_trace(
            loop_step_id="DPL-06",
            atom_id="CAP-CARD-TASKSESSION-01",
            mode="no-write",
            status=card_status(card),
            summary="projected policy evidence persistence proposal into a desktop card",
        ),
    ]
    return [card], traces, list(plan.get("refusal_reasons", []))


def build_policy_feedback_record_cards(
    *,
    project_root: Path | None,
    session_id: str | None,
    policy_ref: str | None,
    feedback_type: str | None,
    summary: str | None,
    user_phrase: str | None,
    owner_agent: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    refusals: list[str] = []
    if not session_id:
        refusals.append("session_id_required_for_policy_feedback_record")
    if not policy_ref:
        refusals.append("policy_ref_required_for_policy_feedback_record")
    if not feedback_type:
        refusals.append("feedback_type_required_for_policy_feedback_record")
    elif feedback_type not in POLICY_FEEDBACK_TYPES:
        refusals.append("unsupported_policy_feedback_type")
    compact_summary = summary or user_phrase
    if not compact_summary:
        refusals.append("summary_or_user_phrase_required_for_policy_feedback_record")

    if refusals:
        card = generic_card(
            card_kind="policy_feedback_record_refusal",
            status="refused",
            title="Policy feedback record needs explicit refs",
            summary=(
                "Policy feedback proposal requires an explicit session, policy, "
                "feedback type, and user-facing summary."
            ),
            refusal_reasons=refusals,
            next_actions=["provide explicit feedback refs before proposing persistence"],
        )
        trace = atom_trace(
            loop_step_id="DPL-11",
            atom_id="CAP-POLICY-FEEDBACK-PERSIST-PROPOSE-01",
            mode="no-write",
            status="refused",
            summary="refused policy feedback persistence proposal because required refs were missing",
        )
        return [card], [trace], refusals

    assert session_id is not None
    assert policy_ref is not None
    assert feedback_type is not None
    assert compact_summary is not None

    feedback_ref = stable_id(
        "policy_feedback",
        "|".join([session_id, policy_ref, feedback_type, compact_summary]),
    )
    compact_ref = (
        f"policy_ref={policy_ref};feedback_type={feedback_type};"
        f"feedback_ref={feedback_ref}"
    )
    plan = task_session.build_task_session_update_plan(
        project_root=project_root,
        session_id=session_id,
        patch_kind="evidence",
        owner_agent=owner_agent,
        summary=compact_summary,
        evidence_kind=f"policy_feedback:{feedback_type}",
        evidence_ref=compact_ref,
    )
    card = task_session_cards.build_card(plan)
    status = "ok" if plan.get("can_update") else "refused"
    traces = [
        atom_trace(
            loop_step_id="DPL-11",
            atom_id="CAP-POLICY-FEEDBACK-PERSIST-PROPOSE-01",
            mode="no-write",
            status=status,
            summary="built guarded task-session evidence persistence proposal from policy feedback refs",
        ),
        atom_trace(
            loop_step_id="DPL-04",
            atom_id="CAP-TASK-UPDATE-DRYRUN-01",
            mode="no-write",
            status=status,
            summary="built task-session feedback evidence append dry-run plan",
        ),
        atom_trace(
            loop_step_id="DPL-06",
            atom_id="CAP-CARD-TASKSESSION-01",
            mode="no-write",
            status=card_status(card),
            summary="projected policy feedback persistence proposal into a desktop card",
        ),
    ]
    return [card], traces, list(plan.get("refusal_reasons", []))


def build_policy_evidence_check_cards(
    *,
    session_id: str | None,
    policy_event: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    refusals: list[str] = []
    if not session_id:
        refusals.append("session_id_required_for_policy_evidence_check")
    if not policy_event:
        refusals.append("policy_event_required_for_policy_evidence_check")

    card = generic_card(
        card_kind="policy_evidence_check",
        status="refused" if refusals else "review",
        title="Policy evidence check",
        summary=(
            "Policy evidence can be checked from an existing task session without writing files."
            if not refusals
            else "Policy evidence check needs an explicit task-session id and policy event."
        ),
        shown_inputs=[
            f"session_id: {session_id}",
            f"policy_event: {policy_event}",
        ],
        refusal_reasons=refusals,
        next_actions=[
            "review policy evidence status before proposing persistence or ingestion work"
            if not refusals
            else "provide --session-id and --policy-event before retrying"
        ],
    )
    trace = atom_trace(
        loop_step_id="DPL-05",
        atom_id="CAP-POLICY-EVIDENCE-INGEST-01",
        mode="no-write",
        status="refused" if refusals else "ok",
        summary="prepared policy evidence check using persisted task-session evidence",
    )
    return [card], [trace], refusals


def command_arg(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def build_policy_write_plan_cards(
    *,
    project_root: Path | None,
    policy_ref: str | None,
    policy_title: str | None,
    policy_source_ref: str | None,
    policy_trigger_event: str,
    policy_task_type: str | None,
    policy_jikuo_layer: str | None,
    policy_changed_path_pattern: str | None,
    policy_added_path_pattern: str | None,
    policy_action_type: str,
    policy_evidence_type: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    plan = policy_store.build_policy_write_plan(
        project_root=project_root,
        policy_id=policy_ref,
        title=policy_title,
        source_ref=policy_source_ref,
        trigger_event=policy_trigger_event,
        task_type=policy_task_type,
        jikuo_layer=policy_jikuo_layer,
        changed_path_pattern=policy_changed_path_pattern,
        added_path_pattern=policy_added_path_pattern,
        action_type=policy_action_type,
        evidence_type=policy_evidence_type,
    )
    write_outputs = [
        f"plan_id: {plan['plan_id']}",
        f"policy_ref: {plan['policy_ref']}",
        f"policy_store_status: {plan['policy_store_status']}",
        f"conditions: {len(plan['proposed_policy'].get('conditions', []))}",
    ]
    write_outputs.extend(
        f"would_write: {item['path']} ({item['effect']})"
        for item in plan["write_set"]
    )
    command_parts = [
        "python",
        "-B",
        "tools/jikuo/policy_store.py",
        "write-policy",
        "--project-root",
        command_arg(str(project_root or ".")),
        "--policy-id",
        command_arg(str(plan["policy_ref"])),
        "--title",
        command_arg(policy_title or ""),
        "--trigger-event",
        command_arg(policy_trigger_event),
        "--action-type",
        command_arg(policy_action_type),
        "--evidence-type",
        command_arg(policy_evidence_type),
        "--confirm-write-policy",
        "--approval-phrase",
        command_arg(APPROVAL_PHRASE_PLACEHOLDER),
    ]
    if policy_source_ref:
        command_parts.extend(["--source-ref", command_arg(policy_source_ref)])
    if policy_task_type:
        command_parts.extend(["--task-type", command_arg(policy_task_type)])
    if policy_jikuo_layer:
        command_parts.extend(["--jikuo-layer", command_arg(policy_jikuo_layer)])
    if policy_changed_path_pattern:
        command_parts.extend(["--changed-path-pattern", command_arg(policy_changed_path_pattern)])
    if policy_added_path_pattern:
        command_parts.extend(["--added-path-pattern", command_arg(policy_added_path_pattern)])
    card = generic_card(
        card_kind="policy_write_plan",
        status=plan["status"],
        title="Policy write plan proposal",
        summary=(
            "A project policy write plan is ready for chat review; no policy files were written."
            if plan["status"] != "refused"
            else "Policy write plan could not be prepared safely."
        ),
        shown_inputs=[
            f"policy_ref: {policy_ref}",
            f"policy_title: {policy_title}",
            f"trigger_event: {policy_trigger_event}",
            f"action_type: {policy_action_type}",
            f"evidence_type: {policy_evidence_type}",
        ],
        shown_outputs=write_outputs,
        refusal_reasons=plan["refusal_reasons"],
        next_actions=plan["next_actions"],
    )
    card["policy_write_plan"] = plan
    card["command_proposal"] = {
        "command_preview": " ".join(command_parts),
        "approval_required": True,
        "technical_confirmation_required": True,
        "writes_if_approved": [item["path"] for item in plan["write_set"]],
        "non_effects": plan["non_effects"],
    }
    card["write_effect"] = {
        "target": ".jikuo/policies/ (future guarded write target)",
        "effect": "renders a policy write plan only; no durable write is performed",
        "non_effects": plan["non_effects"],
    }
    trace = atom_trace(
        loop_step_id="DPL-05",
        atom_id="CAP-POLICY-STORE-WRITE-PROPOSE-01",
        mode="no-write",
        status=plan["status"],
        summary="built policy-store write plan proposal without writing policy files",
    )
    return [card], [trace], list(plan["refusal_reasons"])


def build_policy_evolution_plan_cards(
    *,
    project_root: Path | None,
    policy_ref: str | None,
    operation: str,
    feedback_type: str | None,
    summary: str | None,
    source_ref: str | None,
    replacement_policy_ref: str | None,
    replacement_title: str | None,
    replacement_task_type: str | None,
    replacement_jikuo_layer: str | None,
    replacement_changed_path_pattern: str | None,
    replacement_added_path_pattern: str | None,
    replacement_action_type: str,
    replacement_evidence_type: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    plan = policy_store.build_policy_evolution_plan(
        project_root=project_root,
        policy_id=policy_ref,
        operation=operation,
        feedback_type=feedback_type,
        summary=summary,
        source_ref=source_ref,
        replacement_policy_id=replacement_policy_ref,
        replacement_title=replacement_title,
        replacement_task_type=replacement_task_type,
        replacement_jikuo_layer=replacement_jikuo_layer,
        replacement_changed_path_pattern=replacement_changed_path_pattern,
        replacement_added_path_pattern=replacement_added_path_pattern,
        replacement_action_type=replacement_action_type,
        replacement_evidence_type=replacement_evidence_type,
    )
    outputs = [
        f"plan_id: {plan['plan_id']}",
        f"target_policy_ref: {plan['target_policy_ref']}",
        f"operation: {plan['operation']}",
        f"policy_store_status: {plan['policy_store_status']}",
    ]
    if plan.get("replacement_policy_ref"):
        outputs.append(f"replacement_policy_ref: {plan['replacement_policy_ref']}")
    outputs.extend(
        f"recommended_change: {item}"
        for item in plan["recommended_changes"]
    )
    card = generic_card(
        card_kind="policy_evolution_plan",
        status=plan["status"],
        title="Policy evolution plan proposal",
        summary=(
            "A policy evolution plan is ready for chat review; no policy files were written."
            if plan["status"] != "refused"
            else "Policy evolution plan could not be prepared safely."
        ),
        shown_inputs=[
            f"policy_ref: {policy_ref}",
            f"operation: {operation}",
            f"feedback_type: {feedback_type}",
            f"summary: {summary}",
            f"replacement_policy_ref: {replacement_policy_ref}",
            f"replacement_title: {replacement_title}",
        ],
        shown_outputs=outputs,
        refusal_reasons=plan["refusal_reasons"],
        next_actions=plan["next_actions"],
    )
    card["policy_evolution_plan"] = plan
    if operation in {"deprecate_policy", "supersede_policy"} and plan["status"] != "refused":
        command_parts = [
            "python",
            "-B",
            "tools/jikuo/policy_store.py",
            "write-evolution",
            "--project-root",
            command_arg(str(project_root or ".")),
            "--policy-id",
            command_arg(str(policy_ref)),
            "--operation",
            command_arg(operation),
            "--confirm-write-evolution",
            "--approval-phrase",
            command_arg(APPROVAL_PHRASE_PLACEHOLDER),
        ]
        if feedback_type:
            command_parts.extend(["--feedback-type", command_arg(feedback_type)])
        if summary:
            command_parts.extend(["--summary", command_arg(summary)])
        if source_ref:
            command_parts.extend(["--source-ref", command_arg(source_ref)])
        if operation == "supersede_policy":
            if replacement_policy_ref:
                command_parts.extend(["--replacement-policy-id", command_arg(replacement_policy_ref)])
            if replacement_title:
                command_parts.extend(["--replacement-title", command_arg(replacement_title)])
            if replacement_task_type:
                command_parts.extend(["--replacement-task-type", command_arg(replacement_task_type)])
            if replacement_jikuo_layer:
                command_parts.extend(["--replacement-jikuo-layer", command_arg(replacement_jikuo_layer)])
            if replacement_changed_path_pattern:
                command_parts.extend([
                    "--replacement-changed-path-pattern",
                    command_arg(replacement_changed_path_pattern),
                ])
            if replacement_added_path_pattern:
                command_parts.extend([
                    "--replacement-added-path-pattern",
                    command_arg(replacement_added_path_pattern),
                ])
            command_parts.extend(["--replacement-action-type", command_arg(replacement_action_type)])
            command_parts.extend(["--replacement-evidence-type", command_arg(replacement_evidence_type)])
        card["command_proposal"] = {
            "command_preview": " ".join(command_parts),
            "approval_required": True,
            "technical_confirmation_required": True,
            "writes_if_approved": [item["path"] for item in plan["write_set"]],
            "non_effects": plan["non_effects"],
        }
    card["write_effect"] = {
        "target": ".jikuo/policies/ (future guarded evolution writer target)",
        "effect": "renders a policy evolution plan only; no durable write is performed",
        "non_effects": plan["non_effects"],
    }
    trace = atom_trace(
        loop_step_id="DPL-05",
        atom_id="CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01",
        mode="no-write",
        status=plan["status"],
        summary="built policy evolution plan proposal without changing policy files",
    )
    return [card], [trace], list(plan["refusal_reasons"])


def build_audit_cards() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    card = generic_card(
        card_kind="audit_report_not_configured",
        status="review",
        title="Audit report needs explicit changed paths",
        summary=(
            "The minimal agent_flow.py propose runner does not run audit reports "
            "without explicit changed-path integration yet."
        ),
        next_actions=[
            "use the report-only checker directly for this slice",
            "plan checker composition in a later agent_flow.py extension",
        ],
    )
    traces = [
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-CHECKER-01",
            mode="planned-no-write",
            status="not_run",
            summary="audit checker composition is not included in the minimal propose path",
        )
    ]
    return [card], traces, []


def build_proposal(
    *,
    raw_event: str,
    task_title: str | None = None,
    session_id: str | None = None,
    policy_event: str | None = None,
    task_type: str | None = None,
    jikuo_layer: str | None = None,
    changed_paths: list[str] | None = None,
    added_paths: list[str] | None = None,
    summary: str | None = None,
    evidence_kind: str | None = None,
    evidence_ref: str | None = None,
    feedback_type: str | None = None,
    policy_ref: str | None = None,
    policy_title: str | None = None,
    policy_source_ref: str | None = None,
    policy_trigger_event: str = "task_start",
    policy_task_type: str | None = None,
    policy_jikuo_layer: str | None = None,
    policy_changed_path_pattern: str | None = None,
    policy_added_path_pattern: str | None = None,
    policy_action_type: str = "render_pre_task_review",
    policy_evidence_type: str = "card_rendered",
    policy_evolution_operation: str = "refine_policy",
    replacement_policy_ref: str | None = None,
    replacement_title: str | None = None,
    replacement_task_type: str | None = None,
    replacement_jikuo_layer: str | None = None,
    replacement_changed_path_pattern: str | None = None,
    replacement_added_path_pattern: str | None = None,
    replacement_action_type: str = "render_pre_task_review",
    replacement_evidence_type: str = "card_rendered",
    action_ref: str | None = None,
    requirement_ref: str | None = None,
    command_name: str | None = None,
    exit_code: int | None = None,
    verification_layer: str | None = None,
    completion_status: str | None = None,
    owner_agent: str = "codex",
    project_root: Path | None = None,
    user_phrase: str | None = None,
    produced_evidence: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    event = normalize_event(raw_event)
    cards: list[dict[str, Any]]
    traces: list[dict[str, Any]]
    refusals: list[str]

    if event is None:
        refusal = f"unsupported_event: {raw_event}"
        cards = [
            generic_card(
                card_kind="unsupported_event_refusal",
                status="refused",
                title="Unsupported JIKUO event",
                summary="The local runner cannot map this event to a known JIKUO loop.",
                refusal_reasons=[refusal],
                next_actions=["retry with status, task_start, task_continue, index, evidence, verification, completion, handoff, or audit"],
            )
        ]
        traces = []
        refusals = [refusal]
    elif event == "project_status":
        cards, traces, refusals = build_project_status_cards(project_root=project_root)
    elif event == "task_start":
        cards, traces, refusals = build_task_start_cards(
            project_root=project_root,
            task_title=task_title,
            owner_agent=owner_agent,
        )
    elif event == "index_preview":
        cards, traces, refusals = build_index_cards(project_root=project_root)
    elif event == "task_continue":
        cards, traces, refusals = build_continue_cards(
            project_root=project_root,
            session_id=session_id,
        )
    elif event in {"evidence_review", "verification_review", "completion_review", "handoff"}:
        cards, traces, refusals = build_update_cards(
            event=event,
            project_root=project_root,
            session_id=session_id,
            summary=summary,
            evidence_kind=evidence_kind,
            evidence_ref=evidence_ref,
            command_name=command_name,
            exit_code=exit_code,
            verification_layer=verification_layer,
            completion_status=completion_status,
            owner_agent=owner_agent,
        )
    elif event == "policy_write_plan":
        cards, traces, refusals = build_policy_write_plan_cards(
            project_root=project_root,
            policy_ref=policy_ref,
            policy_title=policy_title,
            policy_source_ref=policy_source_ref or user_phrase,
            policy_trigger_event=policy_trigger_event,
            policy_task_type=policy_task_type,
            policy_jikuo_layer=policy_jikuo_layer,
            policy_changed_path_pattern=policy_changed_path_pattern,
            policy_added_path_pattern=policy_added_path_pattern,
            policy_action_type=policy_action_type,
            policy_evidence_type=policy_evidence_type,
        )
    elif event == "policy_evolution_plan":
        cards, traces, refusals = build_policy_evolution_plan_cards(
            project_root=project_root,
            policy_ref=policy_ref,
            operation=policy_evolution_operation,
            feedback_type=feedback_type,
            summary=summary,
            source_ref=policy_source_ref,
            replacement_policy_ref=replacement_policy_ref,
            replacement_title=replacement_title,
            replacement_task_type=replacement_task_type,
            replacement_jikuo_layer=replacement_jikuo_layer,
            replacement_changed_path_pattern=replacement_changed_path_pattern,
            replacement_added_path_pattern=replacement_added_path_pattern,
            replacement_action_type=replacement_action_type,
            replacement_evidence_type=replacement_evidence_type,
        )
    elif event == "policy_evidence_record":
        cards, traces, refusals = build_policy_evidence_record_cards(
            project_root=project_root,
            session_id=session_id,
            policy_ref=policy_ref,
            action_ref=action_ref,
            requirement_ref=requirement_ref,
            evidence_kind=evidence_kind,
            evidence_ref=evidence_ref,
            summary=summary,
            owner_agent=owner_agent,
        )
    elif event == "policy_feedback_record":
        cards, traces, refusals = build_policy_feedback_record_cards(
            project_root=project_root,
            session_id=session_id,
            policy_ref=policy_ref,
            feedback_type=feedback_type,
            summary=summary,
            user_phrase=user_phrase,
            owner_agent=owner_agent,
        )
    elif event == "policy_evidence_check":
        normalized_policy_event = normalize_event(policy_event or "")
        cards, traces, refusals = build_policy_evidence_check_cards(
            session_id=session_id,
            policy_event=normalized_policy_event,
        )
    else:
        cards, traces, refusals = build_audit_cards()

    if event is not None:
        policy_eval_event = (
            normalize_event(policy_event or "")
            if event == "policy_evidence_check"
            else event
        )
        inline_produced_evidence = produced_policy_evidence_for(
            event=event,
            cards=cards,
        )
        inline_produced_evidence.extend(produced_evidence or [])
        policy_context, policy_traces, policy_sections = build_policy_context(
            project_root=project_root,
            event=policy_eval_event or event,
            produced_evidence=inline_produced_evidence,
            task_session_id=session_id if event == "policy_evidence_check" else None,
            task_type=task_type,
            jikuo_layer=jikuo_layer,
            changed_paths=changed_paths,
            added_paths=added_paths,
        )
        traces.extend(policy_traces)
    else:
        policy_context = build_policy_not_inspected_context()
        policy_sections = {
            "triggered_policies": [],
            "required_actions": [],
            "condition_reports": [],
            "evidence_status": [],
            "missing_evidence_reports": [],
        }
    policy_feedback_options = build_policy_feedback_options(
        triggered_policies=policy_sections["triggered_policies"],
        missing_evidence_reports=policy_sections["missing_evidence_reports"],
    )

    statuses = {str(card.get("status", "review")) for card in cards}
    status = "refused" if "refused" in statuses else "review" if "review" in statuses else "ok"
    atom_ids = [trace["atom_id"] for trace in traces]
    unsafe_atoms = sorted(set(atom_ids) - NO_WRITE_ATOMS - {"CAP-AGENT-FLOW-01"})

    return {
        "schema": PROPOSAL_SCHEMA,
        "previous_schema": PREVIOUS_PROPOSAL_SCHEMA,
        "proposal_id": stable_id(
            "proposal",
            "|".join([raw_event, task_title or "", session_id or "", summary or ""]),
        ),
        "report_only": True,
        "runner_mode": "propose",
        "status": status,
        "loop_id": "Desktop App Primary Operating Loop",
        "trigger_decision": trigger_decision_for(
            raw_event=raw_event,
            event=event,
            user_phrase=user_phrase,
            refusals=refusals,
        ),
        "policy_context": policy_context,
        "triggered_policies": policy_sections["triggered_policies"],
        "required_actions": policy_sections["required_actions"],
        "condition_reports": policy_sections["condition_reports"],
        "evidence_status": policy_sections["evidence_status"],
        "missing_evidence_reports": policy_sections["missing_evidence_reports"],
        "policy_feedback_options": policy_feedback_options,
        "atom_trace": traces,
        "cards": cards,
        "approval_boundary": {
            "durable_write_approved": False,
            "guarded_apply_available": False,
            "exact_user_phrase_placeholder": APPROVAL_PHRASE_PLACEHOLDER,
        },
        "write_effect": {
            "writes_performed": False,
            "write_allowed_by_command": False,
            "durable_write_atoms_called": [],
            "unsafe_atoms_detected": unsafe_atoms,
            "non_effects": [
                "does not create .jikuo/policies/",
                "does not create .jikuo/task_sessions/",
                "does not update .jikuo/project_state.yaml",
            ],
        },
        "next_actions": next_actions_for(status=status, event=event),
    }


def next_actions_for(*, status: str, event: str | None) -> list[str]:
    if event is None:
        return ["retry with a supported event"]
    if status == "refused":
        return ["resolve refusal reasons before asking for a guarded action"]
    if event == "task_start":
        return ["review the task-start card in chat before approving any task-session write"]
    if event == "project_status":
        return ["continue with task_start when project state is ready"]
    if event == "policy_write_plan":
        return ["review policy write targets and non-effects before approving any future guarded writer"]
    if event == "policy_evolution_plan":
        return ["review policy evolution recommendation and any generated guarded command before approving a write"]
    if event in {"evidence_review", "verification_review", "completion_review", "handoff"}:
        return ["review lifecycle preview before approving any task-session update"]
    return ["review this proposal in chat; no durable write has been performed"]


def build_apply_result(
    *,
    operation: str,
    project_root: Path | None,
    session_id: str | None,
    evidence_kind: str | None,
    evidence_ref: str | None,
    summary: str | None,
    evidence_status: str,
    owner_agent: str,
    policy_ref: str | None = None,
    proposal_ref: str | None = None,
    policy_evolution_operation: str = "deprecate_policy",
    feedback_type: str | None = None,
    policy_source_ref: str | None = None,
    replacement_policy_ref: str | None = None,
    replacement_title: str | None = None,
    replacement_task_type: str | None = None,
    replacement_jikuo_layer: str | None = None,
    replacement_changed_path_pattern: str | None = None,
    replacement_added_path_pattern: str | None = None,
    replacement_action_type: str = "render_pre_task_review",
    replacement_evidence_type: str = "card_rendered",
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    """Apply one explicitly approved guarded action through the desktop runner."""

    traces: list[dict[str, Any]] = []
    proposal_binding: dict[str, Any] = {
        "required": False,
        "status": "not_applicable",
        "provided_ref": proposal_ref,
        "expected_ref": None,
    }
    if operation not in APPLY_OPERATIONS:
        traces.append(
            atom_trace(
                loop_step_id="DPL-07",
                atom_id="CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01",
                mode="guarded-write",
                status="refused",
                summary="refused unsupported agent_flow.py apply operation",
            )
        )
        return {
            "schema": APPLY_RESULT_SCHEMA,
            "operation": operation,
            "status": "refused",
            "write_performed": False,
            "target_result_schema": None,
            "target_result": None,
            "proposal_binding": proposal_binding,
            "approval_boundary": {
                "confirmed": confirmed,
                "approval_phrase_present": bool(approval_phrase),
            },
            "atom_trace": traces,
            "refusal_reasons": ["unsupported_apply_operation"],
            "warnings": [],
            "next_actions": ["retry with a supported apply operation"],
        }, 2

    if operation == "task_session_evidence_update":
        target_result, exit_code = task_session.update_task_session(
            project_root=project_root,
            session_id=session_id,
            patch_kind="evidence",
            owner_agent=owner_agent,
            summary=summary,
            evidence_kind=evidence_kind,
            evidence_ref=evidence_ref,
            evidence_status=evidence_status,
            confirmed=confirmed,
            approval_phrase=approval_phrase,
        )
        write_performed = bool(target_result.get("updated_task_session"))
        traces.append(
            atom_trace(
                loop_step_id="DPL-07",
                atom_id="CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01",
                mode="guarded-write",
                status=target_result.get("status", "unknown"),
                summary="applied guarded task-session evidence update through agent_flow.py",
            )
        )
        approval_target = "JIKUO task-session lifecycle update"
        approval_effect = "append compact evidence to an explicit task session"
        approval_non_effects = [
            "does not update .jikuo/project_state.yaml",
            "does not write policy files",
            "does not execute policy actions",
            "does not judge product output quality",
        ]
    else:
        binding_plan = policy_store.build_policy_evolution_plan(
            project_root=project_root,
            policy_id=policy_ref,
            operation=policy_evolution_operation,
            feedback_type=feedback_type,
            summary=summary,
            source_ref=policy_source_ref,
            replacement_policy_id=replacement_policy_ref,
            replacement_title=replacement_title,
            replacement_task_type=replacement_task_type,
            replacement_jikuo_layer=replacement_jikuo_layer,
            replacement_changed_path_pattern=replacement_changed_path_pattern,
            replacement_added_path_pattern=replacement_added_path_pattern,
            replacement_action_type=replacement_action_type,
            replacement_evidence_type=replacement_evidence_type,
        )
        expected_proposal_ref = binding_plan.get("proposal_ref")
        proposal_binding = {
            "required": True,
            "status": "ok",
            "provided_ref": proposal_ref,
            "expected_ref": expected_proposal_ref,
            "match_basis": "deterministic_policy_evolution_plan_ref",
        }
        binding_refusals: list[str] = []
        if policy_evolution_operation not in policy_store.POLICY_EVOLUTION_WRITE_SUPPORTED_OPERATIONS:
            binding_refusals.append(
                "policy_evolution_writer_supports_deprecate_or_supersede_only"
            )
        if not confirmed:
            binding_refusals.append("missing_confirmation_flag")
        if not approval_phrase:
            binding_refusals.append("approval_evidence_missing")
        if not proposal_ref:
            binding_refusals.append("proposal_ref_required_for_policy_evolution_apply")
            proposal_binding["status"] = "missing"
        elif proposal_ref != expected_proposal_ref:
            binding_refusals.append("proposal_ref_mismatch_for_policy_evolution_apply")
            proposal_binding["status"] = "mismatch"
        traces.append(
            atom_trace(
                loop_step_id="DPL-07",
                atom_id="CAP-POLICY-EVOLUTION-APPLY-BINDING-01",
                mode="guarded-preflight",
                status=proposal_binding["status"],
                summary="checked policy evolution apply against the approved proposal ref",
            )
        )
        if binding_refusals:
            target_result = policy_store.build_policy_evolution_write_refusal_result(
                plan=binding_plan,
                refusal_reasons=sorted(
                    set(binding_refusals + list(binding_plan.get("refusal_reasons", [])))
                ),
                approval_phrase=approval_phrase,
            )
            exit_code = 2
        else:
            target_result, exit_code = policy_store.write_policy_evolution_from_plan(
                project_root=project_root,
                policy_id=policy_ref,
                operation=policy_evolution_operation,
                feedback_type=feedback_type,
                summary=summary,
                source_ref=policy_source_ref,
                replacement_policy_id=replacement_policy_ref,
                replacement_title=replacement_title,
                replacement_task_type=replacement_task_type,
                replacement_jikuo_layer=replacement_jikuo_layer,
                replacement_changed_path_pattern=replacement_changed_path_pattern,
                replacement_added_path_pattern=replacement_added_path_pattern,
                replacement_action_type=replacement_action_type,
                replacement_evidence_type=replacement_evidence_type,
                confirmed=confirmed,
                approval_phrase=approval_phrase,
            )
        write_performed = bool(target_result.get("write_performed"))
        traces.append(
            atom_trace(
                loop_step_id="DPL-07",
                atom_id="CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01",
                mode="guarded-write",
                status=target_result.get("status", "unknown"),
                summary="applied guarded policy evolution write through agent_flow.py",
            )
        )
        approval_target = "JIKUO policy evolution write"
        approval_effect = f"{policy_evolution_operation} {policy_ref}"
        approval_non_effects = [
            "does not execute policy actions",
            "does not promote gates",
            "does not persist task-session evidence",
            "does not judge product output quality",
        ]
    status = "applied" if write_performed else target_result.get("status", "refused")
    return {
        "schema": APPLY_RESULT_SCHEMA,
        "operation": operation,
        "status": status,
        "write_performed": write_performed,
        "target_result_schema": target_result.get("schema"),
        "target_result": target_result,
        "proposal_binding": proposal_binding,
        "approval_boundary": {
            "confirmed": confirmed,
            "approval_phrase_present": bool(approval_phrase),
            "approval_target": approval_target,
            "approval_effect": approval_effect,
            "approval_non_effects": approval_non_effects,
        },
        "atom_trace": traces,
        "refusal_reasons": target_result.get("refusal_reasons", []),
        "warnings": target_result.get("warnings", []),
        "next_actions": target_result.get("next_actions", []),
    }, exit_code


def render_apply_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# JIKUO Agent Flow Apply Result",
        "",
        f"- Status: `{report['status']}`",
        f"- Operation: `{report['operation']}`",
        f"- Writes performed: `{str(report['write_performed']).lower()}`",
        f"- Target result schema: `{report.get('target_result_schema')}`",
        "",
        "## Proposal Binding",
        "",
        f"- Required: `{str(report.get('proposal_binding', {}).get('required', False)).lower()}`",
        f"- Status: `{report.get('proposal_binding', {}).get('status')}`",
        f"- Provided ref: `{report.get('proposal_binding', {}).get('provided_ref')}`",
        f"- Expected ref: `{report.get('proposal_binding', {}).get('expected_ref')}`",
        "",
        "## Approval Boundary",
        "",
        f"- Confirmed: `{str(report['approval_boundary']['confirmed']).lower()}`",
        f"- Approval phrase present: `{str(report['approval_boundary']['approval_phrase_present']).lower()}`",
    ]
    for item in report["approval_boundary"].get("approval_non_effects", []):
        lines.append(f"- Non-effect: {item}")
    lines.extend(["", "## Atom Trace", ""])
    for trace in report["atom_trace"]:
        lines.append(
            f"- `{trace['loop_step_id']}` / `{trace['atom_id']}` / "
            f"`{trace['mode']}` / `{trace['status']}`: {trace['summary']}"
        )
    target = report.get("target_result") or {}
    if target:
        lines.extend(
            [
                "",
                "## Target Result",
                "",
                f"- Status: `{target.get('status')}`",
            ]
        )
        if target.get("operation"):
            lines.append(f"- Target operation: `{target.get('operation')}`")
        if target.get("policy_ref"):
            lines.append(f"- Policy ref: `{target.get('policy_ref')}`")
        if target.get("replacement_policy_ref"):
            lines.append(
                f"- Replacement policy ref: `{target.get('replacement_policy_ref')}`"
            )
        if target.get("session_id"):
            lines.append(f"- Session id: `{target.get('session_id')}`")
        if target.get("session_path"):
            lines.append(f"- Session path: `{target.get('session_path')}`")
        if target.get("patch_kind"):
            lines.append(f"- Patch kind: `{target.get('patch_kind')}`")
        if target.get("written_paths"):
            lines.append("- Written paths:")
            lines.extend(f"  - `{item}`" for item in target["written_paths"])
        patch = target.get("patch") or {}
        if patch:
            lines.append(f"- Patch id: `{patch.get('patch_id')}`")
            lines.append(f"- Evidence kind: `{patch.get('evidence_kind')}`")
    if report["refusal_reasons"]:
        lines.extend(["", "## Refusal Reasons", ""])
        lines.extend(f"- {item}" for item in report["refusal_reasons"])
    if report["next_actions"]:
        lines.extend(["", "## Next Actions", ""])
        lines.extend(f"- {item}" for item in report["next_actions"])
    return "\n".join(lines).rstrip() + "\n"


def render_generic_card(card: dict[str, Any]) -> str:
    lines = [
        f"## {card['title']}",
        "",
        f"- Status: `{card['status']}`",
        f"- Card kind: `{card['card_kind']}`",
        f"- Card id: `{card['card_id']}`",
        f"- Summary: {card['user_facing_summary']}",
        "",
        "### Write Effect",
        "",
        f"- Target: {card['write_effect']['target']}",
        f"- Effect: {card['write_effect']['effect']}",
    ]
    for item in card["write_effect"]["non_effects"]:
        lines.append(f"- Non-effect: {item}")
    if card["shown_inputs"]:
        lines.extend(["", "### Shown Inputs", ""])
        lines.extend(f"- {item}" for item in card["shown_inputs"])
    if card["shown_outputs"]:
        lines.extend(["", "### Shown Outputs", ""])
        lines.extend(f"- {item}" for item in card["shown_outputs"])
    if card.get("command_proposal"):
        command = card["command_proposal"]
        lines.extend(["", "### Command Proposal", ""])
        lines.append(f"- Approval required: `{str(command['approval_required']).lower()}`")
        lines.append(
            f"- Technical confirmation required: `{str(command['technical_confirmation_required']).lower()}`"
        )
        lines.append(f"- Command preview: `{command['command_preview']}`")
    if card["refusal_reasons"]:
        lines.extend(["", "### Refusal Reasons", ""])
        lines.extend(f"- {item}" for item in card["refusal_reasons"])
    if card["next_actions"]:
        lines.extend(["", "### Next Actions", ""])
        lines.extend(f"- {item}" for item in card["next_actions"])
    return "\n".join(lines) + "\n"


def render_card(card: dict[str, Any]) -> str:
    if card.get("schema") == task_session_cards.CARD_SCHEMA:
        return task_session_cards.render_markdown(card)
    return render_generic_card(card)


def render_markdown(proposal: dict[str, Any]) -> str:
    policy_context = proposal["policy_context"]
    lines = [
        "# JIKUO Agent Flow Proposal",
        "",
        f"- Status: `{proposal['status']}`",
        f"- Proposal id: `{proposal['proposal_id']}`",
        f"- Runner mode: `{proposal['runner_mode']}`",
        "- Writes performed: `false`",
        "- Guarded apply available: `false`",
        "",
        "## Trigger Decision",
        "",
        f"- Scenario: `{proposal['trigger_decision']['invocation_scenario']}`",
        f"- Source: `{proposal['trigger_decision']['trigger_source']}`",
        f"- Match confidence: `{proposal['trigger_decision']['confidence']}`",
        f"- Match basis: `{proposal['trigger_decision']['confidence_basis']}`",
        f"- Intent confidence: `{proposal['trigger_decision']['intent_classification']['confidence']}`",
        f"- Execution readiness: `{proposal['trigger_decision']['execution_readiness']}`",
        "",
        "## Policy Context",
        "",
        f"- Policy store status: `{policy_context['policy_store_status']}`",
        f"- Policy eval status: `{policy_context['policy_eval_status']}`",
        f"- Condition eval status: `{policy_context.get('policy_condition_eval_status')}`",
        f"- Evidence check status: `{policy_context['policy_evidence_check_status']}`",
        f"- Active policy refs: `{len(policy_context['active_policy_refs'])}`",
        f"- Task session id: `{policy_context.get('task_session_id')}`",
        f"- Evidence source refs: `{len(policy_context.get('evidence_source_refs', []))}`",
        f"- Triggered policies: `{len(proposal['triggered_policies'])}`",
        f"- Required actions: `{len(proposal['required_actions'])}`",
        f"- Condition reports: `{len(proposal.get('condition_reports', []))}`",
        f"- Evidence status: `{len(proposal['evidence_status'])}`",
        f"- Missing evidence reports: `{len(proposal['missing_evidence_reports'])}`",
        f"- Policy feedback options: `{len(proposal.get('policy_feedback_options', []))}`",
        f"- Reason: {policy_context['status_reason']}",
        f"- Evidence reason: {policy_context['evidence_status_reason']}",
        "",
        "## Atom Trace",
        "",
    ]
    if policy_context.get("evidence_source_refs"):
        atom_trace_index = lines.index("## Atom Trace")
        evidence_ref_lines = ["### Evidence Source Refs", ""]
        evidence_ref_lines.extend(
            f"- `{ref}`" for ref in policy_context["evidence_source_refs"]
        )
        evidence_ref_lines.append("")
        lines[atom_trace_index:atom_trace_index] = evidence_ref_lines
    if proposal["atom_trace"]:
        for trace in proposal["atom_trace"]:
            lines.append(
                f"- `{trace['loop_step_id']}` / `{trace['atom_id']}` / "
                f"`{trace['mode']}` / `{trace['status']}`: {trace['summary']}"
            )
    else:
        lines.append("- No atoms were called.")
    lines.append("")
    if proposal["triggered_policies"]:
        lines.append("## Triggered Policies")
        lines.append("")
        for item in proposal["triggered_policies"]:
            lines.append(
                f"- `{item['policy_ref']}` / `{item['trigger_ref']}` / "
                f"`{item['status']}` / `{item['confidence']}`: {item['trigger_reason']}"
            )
        lines.append("")
    if proposal["required_actions"]:
        lines.append("## Required Actions")
        lines.append("")
        for item in proposal["required_actions"]:
            lines.append(
                f"- `{item['action_ref']}` / `{item['action_type']}` / "
                f"`{item['status']}` / approval_required=`{str(item['write_boundary']['approval_required']).lower()}`"
            )
        lines.append("")
    if proposal.get("condition_reports"):
        lines.append("## Condition Reports")
        lines.append("")
        for item in proposal["condition_reports"]:
            lines.append(
                f"- `{item['condition_ref']}` / `{item.get('condition_type')}` / "
                f"`{item['status']}`: {item['summary']}"
            )
        lines.append("")
    if proposal["evidence_status"]:
        lines.append("## Evidence Status")
        lines.append("")
        for item in proposal["evidence_status"]:
            lines.append(
                f"- `{item['requirement_ref']}` / `{item['action_ref']}` / "
                f"`{item['required_type']}` / `{item['current_status']}`: {item['summary']}"
            )
        lines.append("")
    if proposal["missing_evidence_reports"]:
        lines.append("## Missing Evidence Reports")
        lines.append("")
        for item in proposal["missing_evidence_reports"]:
            lines.append(
                f"- `{item['report_id']}` / `{item['policy_ref']}` / "
                f"`{item['severity']['policy_level']}` / "
                f"missing=`{len(item['missing'])}`"
            )
        lines.append("")
    if proposal.get("policy_feedback_options"):
        lines.append("## Policy Feedback Options")
        lines.append("")
        for item in proposal["policy_feedback_options"]:
            lines.append(
                f"- `{item['feedback_type']}` / `{item['status']}` / "
                f"persistence=`{item['persistence']}`: {item['effect']}"
            )
        lines.append("")
    lines.append("## Cards")
    lines.append("")
    for card in proposal["cards"]:
        lines.append(render_card(card).rstrip())
        lines.append("")
    lines.append("## Next Actions")
    lines.append("")
    lines.extend(f"- {item}" for item in proposal["next_actions"])
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="No-write local deterministic JIKUO desktop-agent flow runner."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    propose = subparsers.add_parser("propose")
    propose.add_argument("--event", required=True)
    propose.add_argument("--task-title", default=None)
    propose.add_argument("--session-id", default=None)
    propose.add_argument("--policy-event", default=None)
    propose.add_argument("--task-type", default=None)
    propose.add_argument("--jikuo-layer", default=None)
    propose.add_argument("--changed-path", action="append", default=[])
    propose.add_argument("--added-path", action="append", default=[])
    propose.add_argument("--summary", default=None)
    propose.add_argument("--evidence-kind", default=None)
    propose.add_argument("--evidence-ref", default=None)
    propose.add_argument(
        "--feedback-type",
        choices=sorted(POLICY_FEEDBACK_TYPES),
        default=None,
    )
    propose.add_argument("--policy-ref", default=None)
    propose.add_argument("--policy-title", default=None)
    propose.add_argument("--policy-source-ref", default=None)
    propose.add_argument("--policy-trigger-event", default="task_start")
    propose.add_argument("--policy-task-type", default=None)
    propose.add_argument("--policy-jikuo-layer", default=None)
    propose.add_argument("--policy-changed-path-pattern", default=None)
    propose.add_argument("--policy-added-path-pattern", default=None)
    propose.add_argument("--policy-action-type", default="render_pre_task_review")
    propose.add_argument("--policy-evidence-type", default="card_rendered")
    propose.add_argument(
        "--policy-evolution-operation",
        choices=sorted(policy_store.POLICY_EVOLUTION_OPERATIONS),
        default="refine_policy",
    )
    propose.add_argument("--replacement-policy-ref", default=None)
    propose.add_argument("--replacement-title", default=None)
    propose.add_argument("--replacement-task-type", default=None)
    propose.add_argument("--replacement-jikuo-layer", default=None)
    propose.add_argument("--replacement-changed-path-pattern", default=None)
    propose.add_argument("--replacement-added-path-pattern", default=None)
    propose.add_argument("--replacement-action-type", default="render_pre_task_review")
    propose.add_argument("--replacement-evidence-type", default="card_rendered")
    propose.add_argument(
        "--produced-evidence-json",
        default=None,
        help="JSON list of inline produced evidence for report-only policy matching.",
    )
    propose.add_argument("--produced-evidence-id", default=None)
    propose.add_argument("--produced-evidence-type", default=None)
    propose.add_argument("--produced-evidence-action-type", default=None)
    propose.add_argument("--produced-evidence-status", default="ok")
    propose.add_argument("--produced-evidence-summary", default=None)
    propose.add_argument("--action-ref", default=None)
    propose.add_argument("--requirement-ref", default=None)
    propose.add_argument("--command-name", default=None)
    propose.add_argument("--exit-code", type=int, default=None)
    propose.add_argument("--verification-layer", default=None)
    propose.add_argument(
        "--completion-status",
        choices=sorted(task_session.COMPLETION_STATUSES),
        default=None,
    )
    propose.add_argument(
        "--owner-agent",
        choices=sorted(task_session.ALLOWED_OWNER_AGENTS),
        default="codex",
    )
    propose.add_argument("--project-root", type=Path, default=None)
    propose.add_argument("--user-phrase", default=None)
    propose.add_argument("--format", choices=("markdown", "json"), default="markdown")

    apply = subparsers.add_parser("apply")
    apply.add_argument("--operation", choices=sorted(APPLY_OPERATIONS), required=True)
    apply.add_argument("--session-id", default=None)
    apply.add_argument("--evidence-kind", default=None)
    apply.add_argument("--evidence-ref", default=None)
    apply.add_argument("--summary", default=None)
    apply.add_argument("--evidence-status", default="ok")
    apply.add_argument(
        "--owner-agent",
        choices=sorted(task_session.ALLOWED_OWNER_AGENTS),
        default="codex",
    )
    apply.add_argument("--policy-ref", default=None)
    apply.add_argument("--proposal-ref", default=None)
    apply.add_argument(
        "--policy-evolution-operation",
        choices=sorted(policy_store.POLICY_EVOLUTION_OPERATIONS),
        default="deprecate_policy",
    )
    apply.add_argument("--feedback-type", choices=sorted(POLICY_FEEDBACK_TYPES), default=None)
    apply.add_argument("--policy-source-ref", default=None)
    apply.add_argument("--replacement-policy-ref", default=None)
    apply.add_argument("--replacement-title", default=None)
    apply.add_argument("--replacement-task-type", default=None)
    apply.add_argument("--replacement-jikuo-layer", default=None)
    apply.add_argument("--replacement-changed-path-pattern", default=None)
    apply.add_argument("--replacement-added-path-pattern", default=None)
    apply.add_argument("--replacement-action-type", default="render_pre_task_review")
    apply.add_argument("--replacement-evidence-type", default="card_rendered")
    apply.add_argument("--project-root", type=Path, default=None)
    apply.add_argument("--confirm-apply", action="store_true")
    apply.add_argument("--approval-phrase", default=None)
    apply.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "apply":
        report, exit_code = build_apply_result(
            operation=args.operation,
            project_root=args.project_root,
            session_id=args.session_id,
            evidence_kind=args.evidence_kind,
            evidence_ref=args.evidence_ref,
            summary=args.summary,
            evidence_status=args.evidence_status,
            owner_agent=args.owner_agent,
            policy_ref=args.policy_ref,
            proposal_ref=args.proposal_ref,
            policy_evolution_operation=args.policy_evolution_operation,
            feedback_type=args.feedback_type,
            policy_source_ref=args.policy_source_ref,
            replacement_policy_ref=args.replacement_policy_ref,
            replacement_title=args.replacement_title,
            replacement_task_type=args.replacement_task_type,
            replacement_jikuo_layer=args.replacement_jikuo_layer,
            replacement_changed_path_pattern=args.replacement_changed_path_pattern,
            replacement_added_path_pattern=args.replacement_added_path_pattern,
            replacement_action_type=args.replacement_action_type,
            replacement_evidence_type=args.replacement_evidence_type,
            confirmed=args.confirm_apply,
            approval_phrase=args.approval_phrase,
        )
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(render_apply_markdown(report))
        return exit_code

    produced_evidence: list[dict[str, Any]] | None = None
    if args.produced_evidence_json:
        try:
            decoded = json.loads(args.produced_evidence_json)
        except json.JSONDecodeError as exc:
            parser.error(f"--produced-evidence-json must be valid JSON: {exc}")
        if not isinstance(decoded, list):
            parser.error("--produced-evidence-json must decode to a list")
        produced_evidence = decoded
    if (
        args.produced_evidence_id
        or args.produced_evidence_type
        or args.produced_evidence_action_type
    ):
        if not args.produced_evidence_type or not args.produced_evidence_action_type:
            parser.error(
                "--produced-evidence-type and --produced-evidence-action-type are required together"
            )
        if produced_evidence is None:
            produced_evidence = []
        produced_evidence.append(
            {
                "evidence_id": args.produced_evidence_id or "inline_evidence",
                "evidence_type": args.produced_evidence_type,
                "action_type": args.produced_evidence_action_type,
                "status": args.produced_evidence_status,
                "summary": args.produced_evidence_summary
                or "inline produced evidence supplied by agent_flow.py propose",
            }
        )

    proposal = build_proposal(
        raw_event=args.event,
        task_title=args.task_title,
        session_id=args.session_id,
        policy_event=args.policy_event,
        task_type=args.task_type,
        jikuo_layer=args.jikuo_layer,
        changed_paths=args.changed_path,
        added_paths=args.added_path,
        summary=args.summary,
        evidence_kind=args.evidence_kind,
        evidence_ref=args.evidence_ref,
        feedback_type=args.feedback_type,
        policy_ref=args.policy_ref,
        policy_title=args.policy_title,
        policy_source_ref=args.policy_source_ref,
        policy_trigger_event=args.policy_trigger_event,
        policy_task_type=args.policy_task_type,
        policy_jikuo_layer=args.policy_jikuo_layer,
        policy_changed_path_pattern=args.policy_changed_path_pattern,
        policy_added_path_pattern=args.policy_added_path_pattern,
        policy_action_type=args.policy_action_type,
        policy_evidence_type=args.policy_evidence_type,
        policy_evolution_operation=args.policy_evolution_operation,
        replacement_policy_ref=args.replacement_policy_ref,
        replacement_title=args.replacement_title,
        replacement_task_type=args.replacement_task_type,
        replacement_jikuo_layer=args.replacement_jikuo_layer,
        replacement_changed_path_pattern=args.replacement_changed_path_pattern,
        replacement_added_path_pattern=args.replacement_added_path_pattern,
        replacement_action_type=args.replacement_action_type,
        replacement_evidence_type=args.replacement_evidence_type,
        action_ref=args.action_ref,
        requirement_ref=args.requirement_ref,
        command_name=args.command_name,
        exit_code=args.exit_code,
        verification_layer=args.verification_layer,
        completion_status=args.completion_status,
        owner_agent=args.owner_agent,
        project_root=args.project_root,
        user_phrase=args.user_phrase,
        produced_evidence=produced_evidence,
    )
    if args.format == "json":
        print(json.dumps(proposal, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(proposal))
    return 0 if proposal["status"] != "refused" else 2


if __name__ == "__main__":
    sys.exit(main())
