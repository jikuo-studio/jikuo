"""Local deterministic JIKUO desktop-agent flow runner.

This runner composes existing atoms into chat-ready proposals and narrow
guarded apply operations. It is not a general command executor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__:
    from . import (
        activation_settings,
        companion_write_obligations,
        configuration_review,
        execution_envelope,
        policy_store,
        policy_templates,
        project_state,
        runtime_write_observation,
        runtime_visibility,
        starter_policies,
        task_session,
        task_session_cards,
        turn_anchor as turn_anchor_model,
        work_profile,
    )
    from .studio import artifact_assurance as studio_artifact_assurance
    from .studio import document_rules as studio_document_rules
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import activation_settings
    import companion_write_obligations
    import configuration_review
    import execution_envelope
    import policy_templates
    import project_state
    import policy_store
    import runtime_write_observation
    import runtime_visibility
    import starter_policies
    from jikuo.studio import artifact_assurance as studio_artifact_assurance
    from jikuo.studio import document_rules as studio_document_rules
    import task_session
    import task_session_cards
    import turn_anchor as turn_anchor_model
    import work_profile


PREVIOUS_PROPOSAL_SCHEMA = "jikuo.agent_flow_proposal.v0"
PROPOSAL_SCHEMA = "jikuo.agent_flow_proposal.v1"
APPLY_RESULT_SCHEMA = "jikuo.agent_flow_apply_result.v0"
GENERIC_CARD_SCHEMA = "jikuo.agent_flow_card.v0"
CHAT_READY_MARKDOWN_SCHEMA = "jikuo.chat_ready_markdown.v0"
TRIGGER_DECISION_SCHEMA = "jikuo.agent_trigger_decision.v0"
APPROVAL_PHRASE_PLACEHOLDER = "<exact user phrase as spoken>"
POLICY_STORE_STATUS_UNAVAILABLE = "unavailable"
POLICY_EVAL_STATUS_NOT_EVALUATED = "not_evaluated"
POLICY_CONDITION_EVAL_STATUS_NOT_EVALUATED = "not_evaluated"
POLICY_FEEDBACK_OPTIONS_SCHEMA = "jikuo.policy_feedback_options.v0"
POLICY_RUNTIME_STATUS_SCHEMA = "jikuo.policy_runtime_status.v0"
POLICY_DEAD_ZONE_CLASSIFICATION_SCHEMA = "jikuo.policy_dead_zone_classification.v0"
DISPLAY_DIRECTIVES_SCHEMA = "jikuo.display_directives.v0"
CONVERSATION_ROUTER_SCHEMA = "jikuo.conversation_turn_router.v0"
POLICY_SUGGESTION_REVIEW_SCHEMA = "jikuo.proactive_policy_suggestion_review.v0"
POLICY_FEEDBACK_TYPES = {"not_applicable", "defer", "needs_scope_narrowing"}
TRIGGER_MODES = {"mounted", "semantic"}
GOVERNANCE_PATHS = {"core_debug", "mcp"}
CARD_PRIORITY_ORDER = [
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
]
APPLY_OPERATIONS = {
    "policy_evolution_write",
    "policy_template_activation",
    "policy_template_publication",
    "starter_manifest_publication",
    "starter_policy_pack_init",
    "task_session_evidence_update",
    "task_session_start",
}
WORK_ROUTING_CATEGORIES = {
    "taskmap",
    "insight",
    "follow_up",
    "policy",
    "deferred",
    "mixed",
}
WORK_ROUTING_CATEGORY_ALIASES = {
    "task": "taskmap",
    "task_map": "taskmap",
    "task-map": "taskmap",
    "taskmap": "taskmap",
    "insight": "insight",
    "idea": "insight",
    "followup": "follow_up",
    "follow-up": "follow_up",
    "follow_up": "follow_up",
    "policy": "policy",
    "defer": "deferred",
    "deferred": "deferred",
    "mixed": "mixed",
}

POLICY_DEAD_ZONE_NON_GOVERNANCE_EVENTS = {
    "audit_report",
    "configuration_review",
    "index_preview",
    "policy_evolution_plan",
    "policy_distribution_review",
    "policy_feedback_record",
    "policy_template_publication_plan",
    "policy_template_import_plan",
    "policy_write_plan",
    "project_status",
    "starter_manifest_publication_plan",
    "starter_policy_pack_init",
    "task_continue",
}
POLICY_DEAD_ZONE_GOVERNED_WORK_EVENTS = {
    "completion_review",
    "evidence_review",
    "handoff",
    "pre_delivery",
    "task_start",
    "verification_review",
}

EVENT_ALIASES = {
    "turn": "conversation_turn",
    "conversation": "conversation_turn",
    "conversation_turn": "conversation_turn",
    "route_user_request": "conversation_turn",
    "configuration_review": "configuration_review",
    "configure": "configuration_review",
    "configure_status": "configuration_review",
    "init_review": "configuration_review",
    "setup_review": "configuration_review",
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
    "policy_distribution_review": "policy_distribution_review",
    "distribution_review": "policy_distribution_review",
    "policy_distribution": "policy_distribution_review",
    "policy_template_publication": "policy_template_publication_plan",
    "policy_template_publication_plan": "policy_template_publication_plan",
    "template_publication": "policy_template_publication_plan",
    "template_publication_plan": "policy_template_publication_plan",
    "starter_manifest_publication": "starter_manifest_publication_plan",
    "starter_manifest_publication_plan": "starter_manifest_publication_plan",
    "starter_pack_manifest_publication": "starter_manifest_publication_plan",
    "starter_pack_manifest_publication_plan": "starter_manifest_publication_plan",
    "starter_policy_pack_init": "starter_policy_pack_init",
    "starter_init": "starter_policy_pack_init",
    "initialize_jikuo": "starter_policy_pack_init",
    "policy_template_import": "policy_template_import_plan",
    "policy_template_import_plan": "policy_template_import_plan",
    "template_import": "policy_template_import_plan",
    "template_import_plan": "policy_template_import_plan",
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
    "CAP-TASK-START-PROCESSING-01",
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
    "CAP-POLICY-DISTRIBUTION-REVIEW-01",
    "CAP-POLICY-TEMPLATE-PUBLICATION-PLAN-01",
    "CAP-STARTER-MANIFEST-PUBLICATION-PLAN-01",
    "CAP-POLICY-EVIDENCE-CHECK-01",
    "CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01",
    "CAP-POLICY-FEEDBACK-PERSIST-PROPOSE-01",
    "CAP-POLICY-EVIDENCE-INGEST-01",
    "CAP-POLICY-STORE-WRITE-PROPOSE-01",
    "CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01",
    "CAP-POLICY-RUNTIME-STATUS-CARD-01",
    "CAP-RUNTIME-VISIBILITY-CHANNEL-01",
    "CAP-TASK-SESSION-RESOLUTION-01",
    "CAP-TASK-SESSION-BINDING-EVIDENCE-01",
    "CAP-TASKMAP-INSIGHT-FOLLOWUP-EVIDENCE-01",
    "CAP-STARTER-POLICY-PACK-INIT-01",
    "CAP-PROJECT-CONTEXT-RESOLVER-01",
    "CAP-POLICY-TEMPLATE-IMPORT-PLAN-01",
    "CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01",
    "CAP-CONVERSATION-TURN-ROUTER-01",
    "CAP-CONFIGURATION-REVIEW-01",
    "CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01",
    "CAP-HOST-SEMANTIC-INTENT-WORK-PROFILE-01",
    "CAP-SEMANTIC-INTENT-CLASSIFICATION-EVIDENCE-01",
    "CAP-SEMANTIC-INTENT-PRECONDITION-01",
    "CAP-RUNTIME-TURN-ANCHOR-PROJECTION-01",
    "CAP-EXECUTION-ENVELOPE-PROJECTION-01",
    "CAP-STUDIO-ARTIFACT-ASSURANCE-RUNTIME-CARD-01",
}

ARTIFACT_ASSURANCE_EVENTS = {
    "task_start",
    "evidence_review",
    "verification_review",
    "completion_review",
    "handoff",
}
ARTIFACT_READ_EVIDENCE_TYPES = {
    "artifact_read_evidence",
    "document_read_evidence",
    "document_mount_read_evidence",
}
ARTIFACT_PLANNED_WRITE_EVIDENCE_TYPES = {
    "artifact_write_plan_evidence",
    "document_write_plan_evidence",
    "planned_artifact_write_evidence",
}
ARTIFACT_ACTUAL_WRITE_EVIDENCE_TYPES = {
    "artifact_write_evidence",
    "document_write_evidence",
    "actual_artifact_write_evidence",
}
ARTIFACT_WRITE_APPLICABILITY_EVIDENCE_TYPES = {
    "artifact_write_applicability_evidence",
    "document_write_applicability_evidence",
    "completion_check_applicability_evidence",
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


def artifact_items_from_evidence(
    evidence_items: list[dict[str, Any]] | None,
    evidence_types: set[str],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for item in evidence_items or []:
        if not isinstance(item, dict):
            continue
        evidence_type = str(item.get("evidence_type") or item.get("type") or "")
        if evidence_type not in evidence_types:
            continue
        path = (
            item.get("path")
            or item.get("path_ref")
            or item.get("target")
            or item.get("ref")
        )
        if not path:
            continue
        record = {
            "path": path,
            "reason": item.get("summary") or item.get("reason"),
            "role": item.get("role"),
            "source_ref": item.get("source_ref") or "agent_flow.produced_evidence",
            "evidence_ref": item.get("evidence_id") or item.get("evidence_ref"),
            "plan_ref": item.get("plan_ref"),
            "applicability_status": item.get("applicability_status")
            or item.get("status"),
            "applicability_reason": item.get("applicability_reason")
            or item.get("summary"),
        }
        for metadata_key in (
            "source_kind",
            "evidence_kind",
            "evidence_status",
            "attribution_status",
            "operation",
            "previous_path",
            "git_status",
        ):
            if item.get(metadata_key) is not None:
                record[metadata_key] = item.get(metadata_key)
        output.append(record)
    return output


def artifact_items_from_paths(
    paths: list[str] | None,
    *,
    reason: str,
    source_ref: str,
    source_kind: str | None = None,
    evidence_kind: str | None = None,
    evidence_status: str | None = None,
    attribution_status: str | None = None,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for path in paths or []:
        item = {
            "path": path,
            "reason": reason,
            "source_ref": source_ref,
        }
        if source_kind:
            item["source_kind"] = source_kind
        if evidence_kind:
            item["evidence_kind"] = evidence_kind
        if evidence_status:
            item["evidence_status"] = evidence_status
        if attribution_status:
            item["attribution_status"] = attribution_status
        output.append(item)
    return output


def compact_git_write_observation(report: dict[str, Any] | None) -> dict[str, Any] | None:
    if not report:
        return None
    return {
        "schema": report.get("schema"),
        "status": report.get("status"),
        "reason": report.get("reason"),
        "source_kind": report.get("source_kind"),
        "command_ref": report.get("command_ref"),
        "observed_actual_write_count": report.get("observed_actual_write_count", 0),
        "observed_actual_write_set": report.get("observed_actual_write_set") or [],
        "observed_actual_write_paths": report.get("observed_actual_write_paths") or [],
        "attribution_status": report.get("attribution_status"),
        "warnings": report.get("warnings") or [],
        "diagnostics": report.get("diagnostics") or [],
        "non_effects": report.get("non_effects") or [],
    }


def nonempty_or_none(items: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
    return items if items else None


def path_keys_for_items(
    *,
    project_root: Path,
    items: list[dict[str, Any]],
) -> set[str]:
    keys: set[str] = set()
    for item in items:
        normalized, _ = studio_artifact_assurance.normalize_path_ref(
            project_root,
            item.get("path"),
        )
        if normalized:
            keys.add(normalized)
    return keys


def apply_write_applicability_to_candidates(
    *,
    project_root: Path,
    required_writes: list[dict[str, Any]],
    planned_writes: list[dict[str, Any]],
    actual_writes: list[dict[str, Any]],
    applicability_evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    planned_or_actual = path_keys_for_items(
        project_root=project_root,
        items=[*planned_writes, *actual_writes],
    )
    explicit: dict[str, dict[str, Any]] = {}
    for item in applicability_evidence:
        normalized, _ = studio_artifact_assurance.normalize_path_ref(
            project_root,
            item.get("path"),
        )
        if normalized:
            explicit[normalized] = item

    output: list[dict[str, Any]] = []
    for item in required_writes:
        normalized, _ = studio_artifact_assurance.normalize_path_ref(
            project_root,
            item.get("path"),
        )
        updated = dict(item)
        explicit_item = explicit.get(normalized or "")
        if explicit_item:
            explicit_status = explicit_item.get("applicability_status")
            if explicit_status == "ok":
                explicit_status = "applicable"
            updated["applicability_status"] = explicit_status
            updated["applicability_reason"] = explicit_item.get("applicability_reason")
            updated["evidence_ref"] = explicit_item.get("evidence_ref")
        elif normalized in planned_or_actual:
            updated["applicability_status"] = "applicable"
            updated["applicability_reason"] = (
                "candidate appeared in planned or actual write evidence for this slice"
            )
        output.append(updated)
    return output


def unavailable_artifact_assurance_report(
    *,
    project_root: Path | None,
    reason: str,
    diagnostics: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema": studio_artifact_assurance.ARTIFACT_ASSURANCE_SCHEMA,
        "schema_version": studio_artifact_assurance.ARTIFACT_ASSURANCE_SCHEMA,
        "status": "unavailable",
        "project_root": str(project_root) if project_root else None,
        "guarantee": "evidence_comparison_only",
        "reason": reason,
        "diagnostics": diagnostics or [],
        "inputs_supplied": {},
        "read_assurance": {
            "status": "unavailable",
            "required_read_count": 0,
            "read_evidence_count": 0,
            "required_read_set": [],
            "read_evidence_set": [],
            "required_not_read": [],
        },
        "write_assurance": {
            "status": "unavailable",
            "required_write_count": 0,
            "planned_write_count": 0,
            "actual_write_count": 0,
            "required_write_set": [],
            "write_candidate_count": 0,
            "write_candidate_set": [],
            "completion_check_candidate_count": 0,
            "completion_check_candidates": [],
            "completion_check_status": "unavailable",
            "completion_check_not_evaluated": [],
            "completion_check_not_applicable": [],
            "planned_write_set": [],
            "actual_write_set": [],
            "required_not_planned": [],
            "required_not_written": [],
            "planned_not_written": [],
            "unplanned_written": [],
        },
        "gap_report": {
            "status": "unavailable",
            "gap_count": 0,
            "read_gap_count": 0,
            "write_gap_count": 0,
            "completion_check_not_evaluated_count": 0,
            "read_gaps": [],
            "write_gaps": [],
            "invalid_refs": [],
        },
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_read_files_by_itself",
            "does_not_write_files",
            "does_not_inspect_git_by_itself",
            "does_not_prove_model_understanding",
            "does_not_replace_guarded_apply",
        ],
    }


def build_runtime_artifact_assurance_report(
    *,
    event: str | None,
    project_root: Path | None,
    changed_paths: list[str] | None,
    added_paths: list[str] | None,
    produced_evidence: list[dict[str, Any]] | None,
) -> dict[str, Any] | None:
    if event not in ARTIFACT_ASSURANCE_EVENTS:
        return None
    try:
        resolved_root = project_state.discover_project_root(project_root=project_root)
    except Exception as exc:
        return unavailable_artifact_assurance_report(
            project_root=project_root,
            reason=f"project_root_unavailable: {exc}",
        )

    context, context_errors = studio_document_rules.load_project_context(resolved_root)
    if context_errors:
        return unavailable_artifact_assurance_report(
            project_root=resolved_root,
            reason="project_context_unavailable",
            diagnostics=context_errors,
        )
    document_mounts = dict(context.get("main_document_mounts") or {})
    document_roles = context.get("document_roles") or {}
    if isinstance(document_roles, dict):
        document_mounts["roles"] = [
            {"role": role, **value}
            for role, value in document_roles.items()
            if isinstance(value, dict)
        ]
    supplied_paths = list(changed_paths or []) + list(added_paths or [])

    read_evidence = artifact_items_from_evidence(
        produced_evidence,
        ARTIFACT_READ_EVIDENCE_TYPES,
    )
    planned_writes = artifact_items_from_evidence(
        produced_evidence,
        ARTIFACT_PLANNED_WRITE_EVIDENCE_TYPES,
    )
    actual_writes = artifact_items_from_evidence(
        produced_evidence,
        ARTIFACT_ACTUAL_WRITE_EVIDENCE_TYPES,
    )
    declared_actual_writes = list(actual_writes)
    applicability_evidence = artifact_items_from_evidence(
        produced_evidence,
        ARTIFACT_WRITE_APPLICABILITY_EVIDENCE_TYPES,
    )
    if not planned_writes and event == "task_start":
        planned_writes = artifact_items_from_paths(
            supplied_paths,
            reason="agent-supplied task_start changed/added paths are treated as a plan preview",
            source_ref="agent_flow.changed_paths_or_added_paths",
        )
    if event in {"verification_review", "completion_review", "handoff"} and supplied_paths:
        declared_actual_writes.extend(
            artifact_items_from_paths(
                supplied_paths,
                reason="agent-supplied lifecycle review changed/added paths are declared write evidence",
                source_ref="agent_flow.changed_paths_or_added_paths",
                source_kind="declared",
                evidence_kind="actual_write",
                evidence_status="declared",
                attribution_status="agent_declared",
            )
        )
    if not actual_writes and event in {"verification_review", "handoff"}:
        actual_writes = artifact_items_from_paths(
            supplied_paths,
            reason="agent-supplied lifecycle review changed/added paths are treated as declared observed writes",
            source_ref="agent_flow.changed_paths_or_added_paths",
            source_kind="declared",
            evidence_kind="actual_write",
            evidence_status="declared",
            attribution_status="agent_declared",
        )
    git_write_observation = None
    git_observed_actual_writes: list[dict[str, Any]] = []
    if event == "completion_review":
        git_write_observation = runtime_write_observation.observe_git_actual_writes(
            resolved_root
        )
        if git_write_observation.get("status") == "ok":
            git_observed_actual_writes = list(
                git_write_observation.get("observed_actual_write_set") or []
            )
            actual_writes = git_observed_actual_writes
        elif not actual_writes:
            actual_writes = declared_actual_writes

    companion_projection = companion_write_obligations.project_required_companion_writes(
        project_root=resolved_root,
        observed_actual_writes=actual_writes,
        declared_writes=planned_writes,
        document_roles=document_roles if isinstance(document_roles, dict) else {},
    )
    required_companion_writes = list(
        companion_projection.get("required_companion_write_set") or []
    )
    required_writes = studio_artifact_assurance.required_writes_from_document_mounts(
        document_mounts
    )
    required_writes = [*required_writes, *required_companion_writes]
    required_writes = apply_write_applicability_to_candidates(
        project_root=resolved_root,
        required_writes=required_writes,
        planned_writes=planned_writes,
        actual_writes=actual_writes,
        applicability_evidence=applicability_evidence,
    )
    report = studio_artifact_assurance.build_document_artifact_assurance_report(
        project_root=resolved_root,
        required_reads=studio_artifact_assurance.required_reads_from_document_mounts(
            document_mounts
        ),
        read_evidence=nonempty_or_none(read_evidence),
        required_writes=required_writes,
        planned_writes=nonempty_or_none(planned_writes),
        actual_writes=nonempty_or_none(actual_writes),
    )
    write_assurance = report.setdefault("write_assurance", {})
    write_assurance["required_companion_write_count"] = len(required_companion_writes)
    write_assurance["required_companion_write_set"] = required_companion_writes
    write_assurance["declared_write_count"] = len(planned_writes)
    write_assurance["declared_write_set"] = planned_writes
    write_assurance["required_companion_not_observed"] = [
        item
        for item in write_assurance.get("required_not_written") or []
        if (item.get("expected") or {}).get("evidence_kind")
        == "required_companion_write"
    ]
    write_assurance["required_companion_not_declared"] = [
        item
        for item in write_assurance.get("required_not_planned") or []
        if (item.get("expected") or {}).get("evidence_kind")
        == "required_companion_write"
    ]
    gap_report = report.setdefault("gap_report", {})
    if companion_projection.get("unprojected_triggers"):
        projection_gaps = [
            {
                "gap_type": "governance_write_obligation_not_projected",
                "source_ref": item.get("source_ref"),
                "expected": item,
                "observed": None,
            }
            for item in companion_projection.get("unprojected_triggers") or []
        ]
        gap_report.setdefault("write_gaps", []).extend(projection_gaps)
        gap_report["write_gap_count"] = int(gap_report.get("write_gap_count") or 0) + len(
            projection_gaps
        )
        gap_report["gap_count"] = int(gap_report.get("gap_count") or 0) + len(
            projection_gaps
        )
        gap_report["status"] = "review"
        report["status"] = "review"
        write_assurance["status"] = "review"
    report["runtime_projection"] = {
        "schema": "jikuo.runtime_artifact_assurance_projection.v0",
        "event": event,
        "source": "agent_flow.propose",
        "persistence": "runtime_card_and_state_summary",
        "planned_write_source": "produced_evidence_or_task_start_changed_paths",
        "actual_write_source": (
            "git_status_observed"
            if event == "completion_review"
            and (git_write_observation or {}).get("status") == "ok"
            else "declared_lifecycle_evidence"
            if event == "completion_review"
            else "produced_evidence_or_lifecycle_changed_paths"
        ),
        "companion_write_obligations": companion_projection,
        "required_companion_write_count": len(required_companion_writes),
        "declared_actual_write_count": len(declared_actual_writes),
        "declared_actual_write_set": declared_actual_writes,
        "git_write_observation": compact_git_write_observation(git_write_observation),
        "read_evidence_source": "produced_evidence_only",
        "non_effects": [
            "does_not_force_file_reads",
            "artifact_assurance_engine_does_not_inspect_git_by_itself",
            "git_observation_does_not_read_file_contents",
            "does_not_persist_data01_events",
        ],
    }
    return report


def semantic_intent_precondition_unmet(
    semantic_intent_evidence: dict[str, Any],
) -> bool:
    """Return true when governed work needs host semantic intent before proceeding."""

    return bool(semantic_intent_evidence.get("required")) and str(
        semantic_intent_evidence.get("status") or ""
    ) in {"missing", "fallback_only"}


def semantic_intent_evidence_with_precondition_required(
    semantic_intent_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Require host semantic intent for selected MCP proposal entry points."""

    if not isinstance(semantic_intent_evidence, dict):
        semantic_intent_evidence = {}
    semantic_status = str(
        semantic_intent_evidence.get("semantic_intent_status") or "unavailable"
    )
    if semantic_status == "provided":
        return semantic_intent_evidence

    updated = dict(semantic_intent_evidence)
    reasons = [
        str(item)
        for item in (updated.get("reasons") or [])
        if str(item).strip()
    ]
    if "selected_mcp_entry_point_requires_host_semantic_intent" not in reasons:
        reasons.append("selected_mcp_entry_point_requires_host_semantic_intent")
    updated["required"] = True
    updated["status"] = (
        "fallback_only" if semantic_status == "heuristic_fallback" else "missing"
    )
    updated["semantic_intent_status"] = semantic_status
    updated["provider"] = str(updated.get("provider") or "unavailable")
    updated["reason"] = ",".join(reasons)
    updated["reasons"] = reasons
    updated["followup"] = "provide_host_semantic_intent_and_rerun_route"
    return updated


def build_semantic_intent_precondition_card(
    *,
    work_profile_projection: dict[str, Any],
    semantic_intent_evidence: dict[str, Any],
) -> dict[str, Any]:
    scopes = work_profile_projection.get("policy_scopes") or []
    reasons = semantic_intent_evidence.get("reasons") or []
    return generic_card(
        card_kind="semantic_intent_precondition",
        status="refused",
        title="Semantic intent precondition unmet",
        summary=(
            "Governed editing or write-capable work needs compact "
            "host_semantic_intent before JIKUO proceeds."
        ),
        shown_inputs=[
            f"semantic_intent_status: {semantic_intent_evidence.get('semantic_intent_status')}",
            f"semantic_intent_evidence_status: {semantic_intent_evidence.get('status')}",
            f"required: {str(semantic_intent_evidence.get('required')).lower()}",
            f"reason: {semantic_intent_evidence.get('reason')}",
            f"policy_scopes: {', '.join(str(item) for item in scopes) or 'none'}",
            f"required_reasons: {', '.join(str(item) for item in reasons) or 'none'}",
        ],
        shown_outputs=[
            (
                'minimum_host_semantic_intent: {"schema":"jikuo.host_semantic_intent.v0",'
                '"status":"provided","provider":"host_ai","policy_scopes":["discussion|editing|progress_summary"],'
                '"requested_outcome":"compact outcome","execution_boundary":"allowed or blocked effects",'
                '"response_contract":["what the answer must report"],"user_expression":"short phrase only"}'
            ),
            "pure_discussion_fallback: allowed",
            "evaluator_effect: none; this does not expand policy evaluator inputs",
        ],
        refusal_reasons=[
            "host_semantic_intent_required_for_governed_work",
            "semantic_intent_missing_or_fallback_only",
        ],
        next_actions=[
            (
                "classify the user request and re-call the same JIKUO tool with "
                "compact host_semantic_intent"
            ),
            "do not include the raw prompt or transcript in host_semantic_intent",
        ],
    )


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
    work_profile_projection: dict[str, Any] | None = None,
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
        work_profile=work_profile_projection,
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
        "work_profile": work_profile_projection,
        "work_profile_source": (
            "agent_flow_work_profile_projection"
            if work_profile_projection
            else None
        ),
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


def normalize_work_routing_category(value: str | None) -> str:
    if not value:
        return "taskmap"
    key = value.strip().lower().replace(" ", "_")
    normalized = WORK_ROUTING_CATEGORY_ALIASES.get(key)
    if normalized:
        return normalized
    if key in WORK_ROUTING_CATEGORIES:
        return key
    return "mixed"


def item_for_work_routing(
    *,
    category: str,
    task_title: str | None,
    summary: str | None,
) -> str:
    title = (task_title or "").strip()
    if title:
        return title
    text = (summary or "").strip()
    if text:
        return text
    return f"current {category} work"


def build_work_routing_distinction(
    *,
    event: str | None,
    task_title: str | None,
    summary: str | None,
    work_routing_category: str | None,
    work_routing_summary: str | None,
) -> dict[str, Any] | None:
    if event != "task_start":
        return None

    category = normalize_work_routing_category(work_routing_category)
    item = item_for_work_routing(
        category=category,
        task_title=task_title,
        summary=work_routing_summary or summary,
    )
    buckets = {
        "taskmap_items": [],
        "insight_items": [],
        "follow_up_items": [],
        "policy_items": [],
        "deferred_items": [],
    }
    if category == "taskmap":
        buckets["taskmap_items"].append(item)
    elif category == "insight":
        buckets["insight_items"].append(item)
    elif category == "follow_up":
        buckets["follow_up_items"].append(item)
    elif category == "policy":
        buckets["policy_items"].append(item)
    elif category == "deferred":
        buckets["deferred_items"].append(item)
    else:
        buckets["taskmap_items"].append(item)
        buckets["follow_up_items"].append(
            "review whether this mixed work should be split before final delivery"
        )

    routing_id = stable_id(
        "work_route",
        "|".join([event, category, item, work_routing_summary or summary or ""]),
    )
    if work_routing_summary:
        routing_summary = work_routing_summary
    elif category == "taskmap":
        routing_summary = (
            "Current governed work is classified as taskmap execution; insights "
            "and follow-ups must be reported separately when present."
        )
    else:
        routing_summary = (
            f"Current governed work is classified as {category}; taskmap items, "
            "insights, and follow-ups must stay distinct in user-facing summaries."
        )
    return {
        "schema": "jikuo.taskmap_insight_followup_distinction.v0",
        "routing_id": routing_id,
        "category": category,
        "classification_basis": (
            "agent_supplied_work_routing_category"
            if work_routing_category
            else "agent_flow_default_task_start_taskmap"
        ),
        "summary": routing_summary,
        **buckets,
        "user_summary_contract": (
            "Final governed-work summaries must distinguish taskmap work, "
            "captured insights, and follow-up/deferred items."
        ),
    }


def taskmap_insight_followup_evidence_for(
    *,
    event: str,
    work_routing: dict[str, Any],
) -> dict[str, Any]:
    return {
        "evidence_id": stable_id(
            "evidence",
            "|".join(
                [
                    event,
                    str(work_routing.get("routing_id") or "work_route"),
                    "distinguish_taskmap_insights_followups_in_user_summary",
                ]
            ),
        ),
        "evidence_type": "taskmap_insight_followup_distinction_evidence",
        "action_type": "distinguish_taskmap_insights_followups_in_user_summary",
        "source": {
            "kind": "agent_flow_work_routing_distinction",
            "ref": work_routing.get("routing_id"),
        },
        "producer": {
            "actor": "agent",
            "tool": "python -B -m jikuo.agent_flow",
        },
        "status": "ok",
        "summary": work_routing.get("summary"),
        "taskmap_insight_followup_distinction": work_routing,
    }


def task_session_binding_evidence_for(
    *,
    event: str,
    card: dict[str, Any],
) -> dict[str, Any]:
    task_session_refs = list(card.get("task_session_refs") or [])
    command = card.get("command_proposal") or {}
    resolution = dict(card.get("task_session_resolution") or {})
    binding_status = str(
        resolution.get("status")
        or card.get("task_session_binding_status")
        or (
            "needs_user_decision"
            if command.get("command_preview")
            else "binding_reviewed"
        )
    )
    evidence_status = (
        "ok"
        if binding_status == "existing_session_bound"
        else "explicitly_deferred"
        if binding_status == "explicitly_deferred"
        else "needs_user_decision"
        if binding_status in {"needs_user_decision", "guarded_create_proposed"}
        else "ok"
    )
    return {
        "evidence_id": stable_id(
            "evidence",
            "|".join(
                [
                    event,
                    str(card.get("card_id") or "task_session_start_preview"),
                    "bind_create_or_explicitly_defer_task_session",
                ]
            ),
        ),
        "evidence_type": "task_session_binding_evidence",
        "action_type": "bind_create_or_explicitly_defer_task_session",
        "source": {
            "kind": "agent_flow_card",
            "ref": card.get("card_id"),
        },
        "producer": {
            "actor": "agent",
            "tool": "python -B -m jikuo.agent_flow",
        },
        "status": evidence_status,
        "summary": (
            "agent_flow surfaced task-session binding handling for this slice: "
            f"{binding_status}"
        ),
        "task_session_binding": {
            "status": binding_status,
            "task_session_refs": task_session_refs,
            "command_kind": command.get("command_kind"),
            "approval_required": bool(command.get("requires_user_approval")),
            "resolution": resolution or None,
        },
    }


def task_start_processing_evidence_for(
    *,
    event: str,
    card: dict[str, Any],
) -> dict[str, Any]:
    resolution = dict(card.get("task_start_resolution") or {})
    return {
        "evidence_id": stable_id(
            "evidence",
            "|".join(
                [
                    event,
                    str(card.get("card_id") or "task_start_processing"),
                    "record_lightweight_task_start_processing",
                ]
            ),
        ),
        "evidence_type": "task_start_processing_evidence",
        "action_type": "record_lightweight_task_start_processing",
        "source": {
            "kind": "agent_flow_card",
            "ref": card.get("card_id"),
        },
        "producer": {
            "actor": "agent",
            "tool": "python -B -m jikuo.agent_flow",
        },
        "status": "ok",
        "summary": (
            "agent_flow recorded lightweight task_start processing without "
            "creating or requiring a durable task-session."
        ),
        "task_start_processing": resolution or None,
    }


def jikuo_mcp_or_core_debug_path_evidence_for(
    *,
    event: str,
    governance_path: str,
) -> dict[str, Any]:
    producer_tool = (
        "jikuo MCP adapter"
        if governance_path == "mcp"
        else "python -B -m jikuo.agent_flow"
    )
    summary = (
        "governed JIKUO work entered through the MCP adapter"
        if governance_path == "mcp"
        else "JIKUO core was invoked through an explicitly labelled core debug path"
    )
    return {
        "evidence_id": stable_id(
            "evidence",
            "|".join(
                [
                    event,
                    governance_path,
                    "use_mcp_path_for_governed_jikuo_work_or_explicitly_label_core_debug",
                ]
            ),
        ),
        "evidence_type": "jikuo_mcp_or_core_debug_path_evidence",
        "action_type": (
            "use_mcp_path_for_governed_jikuo_work_or_explicitly_label_core_debug"
        ),
        "source": {
            "kind": "jikuo_governance_invocation_path",
            "ref": governance_path,
        },
        "producer": {
            "actor": "agent",
            "tool": producer_tool,
        },
        "status": "ok",
        "summary": summary,
        "governance_path": {
            "path": governance_path,
            "boundary": (
                "mcp_user_path"
                if governance_path == "mcp"
                else "explicit_core_debug_path"
            ),
        },
    }


def proactive_policy_suggestion_evidence_for(
    *,
    event: str,
    card: dict[str, Any],
) -> dict[str, Any]:
    review = dict(card.get("policy_suggestion_review") or {})
    card_id = str(card.get("card_id") or "policy_suggestion_review")
    review_status = str(review.get("review_status") or "unknown")
    candidate_count = int(review.get("candidate_count") or 0)
    return {
        "evidence_id": stable_id(
            "evidence",
            "|".join(
                [
                    event,
                    card_id,
                    "review_repeated_user_interaction_patterns_for_policy_candidates",
                ]
            ),
        ),
        "evidence_type": "proactive_policy_suggestion_review_evidence",
        "action_type": "review_repeated_user_interaction_patterns_for_policy_candidates",
        "source": {
            "kind": "agent_flow_card",
            "ref": card_id,
        },
        "producer": {
            "actor": "agent",
            "tool": "python -B -m jikuo.agent_flow",
        },
        "status": "ok",
        "summary": (
            "agent_flow reviewed this conversation turn for repeated user needs "
            f"and found {candidate_count} policy candidate(s); "
            f"review_status={review_status}"
        ),
        "proactive_policy_suggestion_review": review,
    }


def progress_summary_business_meaning_evidence_for(
    *,
    event: str,
    work_profile_projection: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if event != "completion_review" or not isinstance(work_profile_projection, dict):
        return None

    scopes = work_profile_projection.get("policy_scopes") or []
    if "progress_summary" not in scopes:
        return None

    contract = work_profile_projection.get("policy_contract") or {}
    response_contract = contract.get("response_contract") or []
    requested_outcome = contract.get("requested_outcome")
    text_parts = [str(requested_outcome or "")]
    text_parts.extend(str(item) for item in response_contract)
    contract_text = " ".join(text_parts).lower()
    business_terms = (
        "business meaning",
        "business value",
        "product meaning",
        "product value",
        "\u4e1a\u52a1\u610f\u4e49",
        "\u4ea7\u54c1\u610f\u4e49",
    )
    if not any(term in contract_text for term in business_terms):
        return None

    return {
        "evidence_id": stable_id(
            "evidence",
            "|".join(
                [
                    event,
                    "progress_summary",
                    "include_business_meaning_in_progress_todo_summary",
                ]
            ),
        ),
        "evidence_type": "progress_summary_business_meaning_evidence",
        "action_type": "include_business_meaning_in_progress_todo_summary",
        "source": {
            "kind": "host_semantic_intent_policy_contract",
            "ref": "response_contract",
        },
        "producer": {
            "actor": "agent",
            "tool": "python -B -m jikuo.agent_flow",
        },
        "status": "ok",
        "summary": (
            "host semantic intent declares a completion progress-summary "
            "response contract that includes business or product meaning"
        ),
    }


def produced_policy_evidence_for(
    *,
    event: str | None,
    cards: list[dict[str, Any]],
    work_routing: dict[str, Any] | None = None,
    governance_path: str | None = None,
    work_profile_projection: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    summary_evidence = progress_summary_business_meaning_evidence_for(
        event=event or "",
        work_profile_projection=work_profile_projection,
    )

    if event == "conversation_turn":
        evidence: list[dict[str, Any]] = []
        for card in cards:
            if card.get("status") == "refused":
                continue
            if card.get("card_kind") == "policy_suggestion_review":
                evidence.append(
                    proactive_policy_suggestion_evidence_for(
                        event=event,
                        card=card,
                    )
                )
        return evidence

    if event != "task_start":
        return [summary_evidence] if summary_evidence else []

    evidence: list[dict[str, Any]] = []
    if summary_evidence:
        evidence.append(summary_evidence)
    normalized_governance_path = (
        governance_path.strip().lower().replace("-", "_")
        if isinstance(governance_path, str)
        else None
    )
    if normalized_governance_path in GOVERNANCE_PATHS:
        evidence.append(
            jikuo_mcp_or_core_debug_path_evidence_for(
                event=event,
                governance_path=normalized_governance_path,
            )
        )
    if work_routing:
        evidence.append(
            taskmap_insight_followup_evidence_for(
                event=event,
                work_routing=work_routing,
            )
        )
    for card in cards:
        if card.get("status") == "refused":
            continue
        if card.get("card_kind") == "task_start_processing":
            evidence.append(task_start_processing_evidence_for(event=event, card=card))
        if card.get("card_kind") in {"task_session_start_preview", "task_session_binding"}:
            evidence.append(
                task_session_binding_evidence_for(event=event, card=card)
            )
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
                    "tool": "python -B -m jikuo.agent_flow",
                },
                "status": "ok",
                "summary": "agent_flow rendered the task-start proposal card in chat",
            }
        )
    evidence.append(
        {
            "evidence_id": stable_id(
                "evidence",
                "|".join(
                    [
                        event,
                        "policy_runtime_status",
                        "render_policy_runtime_status_card_for_governed_flow",
                    ]
                ),
            ),
            "evidence_type": "policy_runtime_status_visibility_evidence",
            "action_type": "render_policy_runtime_status_card_for_governed_flow",
            "source": {
                "kind": "agent_flow_card_kind",
                "ref": "policy_runtime_status",
            },
            "producer": {
                "actor": "agent",
                "tool": "python -B -m jikuo.agent_flow",
            },
            "status": "ok",
            "summary": "agent_flow renders policy runtime status as a visible proposal card",
        }
    )
    evidence.append(
        {
            "evidence_id": stable_id(
                "evidence",
                "|".join(
                    [
                        event,
                        "client_runtime_links",
                        "surface_runtime_card_links_to_client",
                    ]
                ),
            ),
            "evidence_type": "client_runtime_card_link_surfacing_evidence",
            "action_type": "surface_runtime_card_links_to_client",
            "source": {
                "kind": "agent_flow_client_display_links",
                "ref": "client_display_links",
            },
            "producer": {
                "actor": "agent",
                "tool": "python -B -m jikuo.agent_flow",
            },
            "status": "ok",
            "summary": "agent_flow returns clickable runtime card links in chat-ready output",
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


def summarize_not_triggered_policies(
    *,
    active_policy_refs: list[dict[str, Any]],
    triggered_policies: list[dict[str, Any]],
    condition_reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    triggered_refs = {
        str(item.get("policy_ref"))
        for item in triggered_policies
        if item.get("policy_ref")
    }
    reports_by_policy: dict[str, list[dict[str, Any]]] = {}
    for report in condition_reports:
        policy_ref = str(report.get("policy_ref") or "")
        if policy_ref:
            reports_by_policy.setdefault(policy_ref, []).append(report)

    summaries: list[dict[str, Any]] = []
    for policy in active_policy_refs:
        policy_ref = str(policy.get("policy_id") or "")
        if not policy_ref or policy_ref in triggered_refs:
            continue
        reports = reports_by_policy.get(policy_ref, [])
        blockers = [
            report
            for report in reports
            if str(report.get("status") or "") != "matched"
        ]
        if blockers:
            reason = str(
                blockers[0].get("summary") or "policy conditions did not match"
            )
            reason_ref = blockers[0].get("condition_ref")
        elif reports:
            reason = "policy conditions were checked but no trigger was produced"
            reason_ref = reports[0].get("condition_ref")
        else:
            reason = "no matching trigger or condition report for this event"
            reason_ref = None
        summaries.append(
            {
                "policy_ref": policy_ref,
                "policy_title": policy.get("title"),
                "status": "not_triggered",
                "reason": reason,
                "reason_ref": reason_ref,
            }
        )
    return summaries


def summarize_missing_evidence(
    missing_evidence_reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    missing_items: list[dict[str, Any]] = []
    for report in missing_evidence_reports:
        for item in report.get("missing", []):
            missing_items.append(
                {
                    "policy_ref": report.get("policy_ref"),
                    "report_id": report.get("report_id"),
                    "requirement_ref": item.get("requirement_ref"),
                    "action_ref": item.get("action_ref"),
                    "required_type": item.get("required_type"),
                    "reason": item.get("reason"),
                }
            )
    return missing_items


def classify_policy_dead_zone(
    *,
    event: str | None,
    task_type: str,
    jikuo_layer: str,
    active_count: int,
    triggered_count: int,
    store_status: str,
    condition_reports: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if store_status != "active" or active_count == 0 or triggered_count > 0:
        return None

    normalized_event = event or "unknown"
    context_blockers = [
        report
        for report in condition_reports
        if str(report.get("status") or "") != "matched"
        and str(report.get("condition_type") or "")
        in {"task_type_is", "jikuo_layer_is"}
    ]
    work_profile_blockers = [
        report
        for report in condition_reports
        if str(report.get("status") or "") != "matched"
        and str(report.get("condition_type") or "") == "work_profile_applicability"
    ]
    other_blockers = [
        report
        for report in condition_reports
        if str(report.get("status") or "") != "matched"
    ]

    if normalized_event == "conversation_turn":
        classification = "route_followup_required"
        severity = "warning"
        reason = (
            "conversation_turn evaluated active policies directly; use the router "
            "follow-up task_start or completion_review call for governed work"
        )
        next_actions = [
            "call jikuo.propose_task_start or the router-listed follow-up tool before continuing task work",
            "keep conversation_turn as the routing step, not the final policy-governed work step",
        ]
    elif normalized_event in POLICY_DEAD_ZONE_NON_GOVERNANCE_EVENTS:
        classification = "non_governance_event"
        severity = "info"
        reason = (
            f"{normalized_event} is not normally a governed work event for project policies"
        )
        next_actions = [
            "do not treat this card as proof that task work was governed",
            "for actual work, run route_user_request and then task_start or completion_review with task context",
        ]
    elif normalized_event in POLICY_DEAD_ZONE_GOVERNED_WORK_EVENTS and context_blockers:
        first = context_blockers[0]
        classification = "missing_or_mismatched_task_context"
        severity = "warning"
        reason = str(first.get("summary") or "task context did not match active policies")
        next_actions = [
            "rerun the governed event with the task_type and jikuo_layer expected by relevant active policies",
            "if the work is genuinely outside existing policy scope, record a policy coverage gap or propose a new policy",
        ]
    elif normalized_event in POLICY_DEAD_ZONE_GOVERNED_WORK_EVENTS and work_profile_blockers:
        first = work_profile_blockers[0]
        classification = "work_profile_scope_mismatch"
        severity = "warning"
        reason = str(first.get("summary") or "work_profile did not match active policies")
        next_actions = [
            "review the work_profile projection and policy applies_to_work_profile declaration",
            "if the work should be governed, backfill or refine the policy scope declaration before relying on the no-trigger result",
        ]
    elif normalized_event in POLICY_DEAD_ZONE_GOVERNED_WORK_EVENTS and other_blockers:
        first = other_blockers[0]
        classification = "condition_mismatch"
        severity = "warning"
        reason = str(first.get("summary") or "policy conditions did not match")
        next_actions = [
            "review changed_path / added_path context and rerun with the specific paths being governed",
            "if no active policy should cover this work, record it as a healthy no-op or coverage gap explicitly",
        ]
    elif normalized_event in POLICY_DEAD_ZONE_GOVERNED_WORK_EVENTS:
        classification = "policy_coverage_gap"
        severity = "warning"
        reason = (
            f"{normalized_event} is a governed work event, but no active policy "
            "reported a matching trigger or condition"
        )
        next_actions = [
            "review whether the project needs policies for this work type",
            "consider starter-policy expansion or a reviewed project-local policy proposal",
        ]
    else:
        classification = "unknown_event_no_trigger"
        severity = "warning"
        reason = (
            f"{normalized_event} produced zero triggered policies, and JIKUO has "
            "no specific dead-zone classification for that event"
        )
        next_actions = [
            "rerun through route_user_request or a known governed work event",
            "record the event as a LIVE-20 classification gap if it represents real work",
        ]

    return {
        "schema": POLICY_DEAD_ZONE_CLASSIFICATION_SCHEMA,
        "status": "detected",
        "classification": classification,
        "severity": severity,
        "event": normalized_event,
        "task_type": task_type,
        "jikuo_layer": jikuo_layer,
        "active_policy_count": active_count,
        "triggered_policy_count": triggered_count,
        "reason": reason,
        "next_actions": next_actions,
    }


def build_policy_runtime_status_card(
    *,
    event: str | None,
    task_type: str,
    jikuo_layer: str,
    policy_context: dict[str, Any],
    triggered_policies: list[dict[str, Any]],
    required_actions: list[dict[str, Any]],
    condition_reports: list[dict[str, Any]],
    evidence_status: list[dict[str, Any]],
    missing_evidence_reports: list[dict[str, Any]],
    policy_feedback_options: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    active_policy_refs = list(policy_context.get("active_policy_refs", []))
    not_triggered = summarize_not_triggered_policies(
        active_policy_refs=active_policy_refs,
        triggered_policies=triggered_policies,
        condition_reports=condition_reports,
    )
    missing_evidence = summarize_missing_evidence(missing_evidence_reports)
    evidence_counts: dict[str, int] = {}
    for item in evidence_status:
        status = str(item.get("current_status") or "unknown")
        evidence_counts[status] = evidence_counts.get(status, 0) + 1

    active_count = len(active_policy_refs)
    triggered_count = len(triggered_policies)
    missing_count = len(missing_evidence)
    store_status = str(policy_context.get("policy_store_status") or "unavailable")
    dead_zone = classify_policy_dead_zone(
        event=event,
        task_type=task_type,
        jikuo_layer=jikuo_layer,
        active_count=active_count,
        triggered_count=triggered_count,
        store_status=store_status,
        condition_reports=condition_reports,
    )
    card_status = (
        "review"
        if missing_count > 0
        or store_status in {"stale", "conflict"}
        or (dead_zone and dead_zone.get("severity") == "warning")
        else "ok"
    )
    summary = (
        f"Policy runtime checked {active_count} active polic"
        f"{'y' if active_count == 1 else 'ies'}; "
        f"{triggered_count} triggered and {missing_count} evidence item"
        f"{'' if missing_count == 1 else 's'} are missing."
    )

    shown_inputs = [
        f"policy_store_status: {store_status}",
        f"policy_eval_status: {policy_context.get('policy_eval_status')}",
        f"condition_eval_status: {policy_context.get('policy_condition_eval_status')}",
        f"evidence_check_status: {policy_context.get('policy_evidence_check_status')}",
    ]
    work_profile_projection = policy_context.get("work_profile") or {}
    if work_profile_projection:
        shown_inputs.append(
            "work_profile: "
            f"{work_profile_projection.get('lifecycle_event')} / "
            f"scopes={work_profile_projection.get('policy_scopes')}"
        )
        semantic_evidence = work_profile_projection.get("semantic_intent_evidence") or {}
        if semantic_evidence:
            shown_inputs.append(
                "semantic_intent_evidence: "
                f"required={semantic_evidence.get('required')} / "
                f"status={semantic_evidence.get('status')} / "
                f"provider={semantic_evidence.get('provider')}"
            )
        contract = work_profile_projection.get("policy_contract") or {}
        active_contract_keys = [
            key
            for key in (
                "requested_outcome",
                "process_contract",
                "execution_boundary",
                "response_contract",
            )
            if contract.get(key)
        ]
        if active_contract_keys:
            shown_inputs.append(
                "work_profile_contract_fields: "
                f"{', '.join(active_contract_keys)}"
            )
    shown_outputs = [
        f"active_policy_count: {active_count}",
        f"triggered_policy_count: {triggered_count}",
        f"not_triggered_policy_count: {len(not_triggered)}",
        f"required_action_count: {len(required_actions)}",
        f"evidence_status_count: {len(evidence_status)}",
        f"missing_evidence_count: {missing_count}",
        f"policy_feedback_option_count: {len(policy_feedback_options)}",
    ]
    if dead_zone:
        shown_outputs.append(
            "policy_dead_zone: "
            f"{dead_zone['classification']} / {dead_zone['severity']} - "
            f"{dead_zone['reason']}"
        )
    for item in triggered_policies:
        title = item.get("policy_title") or item.get("policy_ref")
        shown_outputs.append(f"triggered_policy: {item.get('policy_ref')} ({title})")
        applicability = item.get("applies_to_work_profile") or {}
        if applicability:
            shown_outputs.append(
                "triggered_policy_work_profile_applicability: "
                f"{item.get('policy_ref')} / "
                f"{applicability.get('status')} / "
                f"evaluator_effect={applicability.get('evaluator_effect')}"
            )
        work_profile_match = item.get("work_profile_match") or {}
        if work_profile_match:
            observed = work_profile_match.get("observed") or {}
            shown_outputs.append(
                "triggered_policy_work_profile_match: "
                f"{item.get('policy_ref')} / "
                f"{work_profile_match.get('status')} / "
                f"matched_refs={work_profile_match.get('matched_refs')} / "
                f"fallback_expanded={observed.get('fallback_expanded')}"
            )
    for item in not_triggered:
        title = item.get("policy_title") or item.get("policy_ref")
        shown_outputs.append(
            f"not_triggered_policy: {item.get('policy_ref')} ({title}) - {item.get('reason')}"
        )
    for item in missing_evidence:
        shown_outputs.append(
            f"missing_evidence: {item.get('required_type')} for {item.get('policy_ref')}"
        )

    if missing_evidence:
        next_actions = [
            "supply the missing policy evidence, defer it explicitly, or mark the policy not applicable",
        ]
    elif triggered_policies:
        next_actions = ["continue with triggered policy actions visible in this proposal"]
    elif dead_zone:
        next_actions = list(dead_zone["next_actions"])
    elif store_status == "active":
        next_actions = ["continue; no active policy triggered for this event"]
    else:
        next_actions = list(policy_context.get("next_actions", []))

    card = generic_card(
        card_kind="policy_runtime_status",
        status=card_status,
        title="Policy runtime status",
        summary=summary,
        shown_inputs=shown_inputs,
        shown_outputs=shown_outputs,
        next_actions=next_actions,
    )
    card["policy_runtime_status"] = {
        "schema": POLICY_RUNTIME_STATUS_SCHEMA,
        "policy_store_status": store_status,
        "policy_eval_status": policy_context.get("policy_eval_status"),
        "policy_condition_eval_status": policy_context.get(
            "policy_condition_eval_status"
        ),
        "policy_evidence_check_status": policy_context.get(
            "policy_evidence_check_status"
        ),
        "active_policy_count": active_count,
        "triggered_policy_count": triggered_count,
        "not_triggered_policy_count": len(not_triggered),
        "required_action_count": len(required_actions),
        "evidence_status_count": len(evidence_status),
        "evidence_status_counts": evidence_counts,
        "missing_evidence_count": missing_count,
        "policy_feedback_option_count": len(policy_feedback_options),
        "triggered_policies": triggered_policies,
        "not_triggered_policies": not_triggered,
        "required_actions": required_actions,
        "missing_evidence": missing_evidence,
        "policy_feedback_options": policy_feedback_options,
    }
    if work_profile_projection:
        card["policy_runtime_status"]["work_profile"] = work_profile_projection
        card["policy_runtime_status"]["work_profile_source"] = policy_context.get(
            "work_profile_source"
        )
    if dead_zone:
        card["policy_runtime_status"]["policy_dead_zone"] = dead_zone
    trace = atom_trace(
        loop_step_id="DPL-06",
        atom_id="CAP-POLICY-RUNTIME-STATUS-CARD-01",
        mode="no-write",
        status=card_status,
        summary="projected policy runtime trigger and evidence status into a visible card",
    )
    return card, trace


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
    user_phrase_status = "provided_redacted" if user_phrase else "not_provided"
    user_phrase_projection = "<redacted_user_phrase>" if user_phrase else raw_event
    if event == "conversation_turn":
        return {
            "schema": TRIGGER_DECISION_SCHEMA,
            "trigger_source": "conversation_turn_router",
            "user_phrase": user_phrase_projection,
            "user_phrase_status": user_phrase_status,
            "invocation_scenario": event,
            "confidence": "event_match",
            "confidence_basis": "canonical_event_mapping",
            "trigger_match": {
                "status": trigger_match_status,
                "basis": "canonical_event_mapping",
                "raw_event": raw_event,
                "normalized_event": event,
            },
            "intent_classification": {
                "confidence": "heuristic_router",
                "basis": "deterministic_keyword_router_v0",
                "note": (
                    "agent_flow.py routes the supplied user turn into auditable "
                    "JIKUO obligations without storing raw chat transcript"
                ),
            },
            "execution_readiness": execution_readiness,
            "may_call_no_write_atoms": True,
            "may_request_guarded_write": bool(not refusals),
            "durable_write_approved": False,
            "required_clarification": refusals,
        }
    return {
        "schema": TRIGGER_DECISION_SCHEMA,
        "trigger_source": "explicit_user_shortcut"
        if user_phrase
        else "explicit_user_natural_language",
        "user_phrase": user_phrase_projection,
        "user_phrase_status": user_phrase_status,
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


def normalize_trigger_mode(
    trigger_mode: str | None,
    *,
    project_root: Path | None = None,
) -> str:
    if trigger_mode is None:
        mode, _source, _status = activation_settings.resolve_conversation_trigger_mode(
            project_root=project_root,
            requested_trigger_mode=None,
        )
        return mode
    mode = (trigger_mode or "semantic").strip().lower().replace("_", "-")
    aliases = {
        "mounted-harness": "mounted",
        "natural": "semantic",
        "natural-language": "semantic",
    }
    mode = aliases.get(mode, mode)
    if mode not in TRIGGER_MODES:
        return "semantic"
    return mode


def keyword_matches(text: str, keyword: str) -> bool:
    if keyword.isascii():
        pattern = rf"(?<![A-Za-z0-9_]){re.escape(keyword)}(?![A-Za-z0-9_])"
        return re.search(pattern, text) is not None
    return keyword in text


def classify_conversation_turn(
    *,
    trigger_mode: str,
    user_phrase: str | None,
    task_title: str | None,
    summary: str | None,
) -> tuple[dict[str, Any], list[str]]:
    input_text = (user_phrase or summary or task_title or "").strip()
    input_summary = "<redacted_user_phrase>" if user_phrase else input_text
    input_summary_status = "provided_redacted" if user_phrase else "provided_compact"
    if not input_text:
        router = {
            "schema": CONVERSATION_ROUTER_SCHEMA,
            "trigger_mode": trigger_mode,
            "router_status": "clarification_required",
            "input_summary": "",
            "input_summary_status": "missing",
            "classification_basis": "missing_user_turn",
            "classified_obligations": [
                {
                    "kind": "clarification_required",
                    "status": "required",
                    "reason": "conversation_turn requires --user-phrase, --summary, or --task-title",
                    "target_event": None,
                    "required_followup_tool": None,
                }
            ],
            "required_followup_tools": [],
            "privacy": {
                "raw_transcript_captured": False,
                "stored_input": "compact_user_supplied_turn_only",
            },
            "non_effects": [
                "does not create .jikuo/task_sessions/",
                "does not create .jikuo/policies/",
                "does not update .jikuo/project_state.yaml",
                "does not capture raw chat transcript",
            ],
        }
        return router, ["user_phrase_required_for_conversation_turn_router"]

    text = input_text.lower()
    obligation_specs = [
        (
            "configuration_review",
            {
                "keywords": {
                    "activation",
                    "configure",
                    "configuration",
                    "init",
                    "initialize",
                    "onboarding",
                    "semantic",
                    "setup",
                    "settings",
                    "trigger mode",
                    "mounted",
                },
                "reason": "user turn appears to request JIKUO setup or activation configuration review",
                "target_event": "configuration_review",
                "tool": "python -B -m jikuo.agent_flow propose --event configuration_review",
            },
        ),
        (
            "task_start",
            {
                "keywords": {
                    "start",
                    "continue",
                    "implement",
                    "build",
                    "fix",
                    "submit",
                    "commit",
                    "next task",
                    "继续",
                    "开始",
                    "执行",
                    "实现",
                    "修复",
                    "提交",
                    "推进",
                    "开发",
                },
                "reason": "user turn appears to request active task execution",
                "target_event": "task_start",
                "tool": "jikuo.propose_task_start",
            },
        ),
        (
            "completion_review",
            {
                "keywords": {
                    "complete",
                    "completion",
                    "acceptance",
                    "verify",
                    "review",
                    "验收",
                    "完成",
                    "检查",
                    "接受",
                },
                "reason": "user turn appears to request acceptance or completion review",
                "target_event": "completion_review",
                "tool": "python -B -m jikuo.agent_flow propose --event completion_review",
            },
        ),
        (
            "policy_suggestion_review",
            {
                "keywords": {
                    "policy",
                    "rule",
                    "principle",
                    "repeated",
                    "preference",
                    "need",
                    "每次",
                    "反复",
                    "多次",
                    "规则",
                    "原则",
                    "偏好",
                    "需求",
                    "应该",
                    "需要",
                    "以后",
                    "业务意义",
                    "进度",
                    "代办",
                },
                "reason": "user turn appears to contain a repeated need, preference, or policy candidate",
                "target_event": "policy_suggestion_review",
                "tool": None,
            },
        ),
        (
            "insight_or_follow_up_routing",
            {
                "keywords": {
                    "idea",
                    "insight",
                    "follow-up",
                    "followup",
                    "defer",
                    "想法",
                    "洞察",
                    "后续",
                    "暂缓",
                    "挂起",
                },
                "reason": "user turn appears to require taskmap / insight / follow-up classification",
                "target_event": "task_start",
                "tool": "jikuo.propose_task_start",
            },
        ),
    ]

    obligations: list[dict[str, Any]] = []
    followup_tools: list[str] = []
    for kind, spec in obligation_specs:
        matched = sorted(
            keyword for keyword in spec["keywords"] if keyword_matches(text, keyword)
        )
        if not matched:
            continue
        tool = spec["tool"]
        obligations.append(
            {
                "kind": kind,
                "status": "required",
                "reason": spec["reason"],
                "target_event": spec["target_event"],
                "required_followup_tool": tool,
                "matched_terms": matched,
            }
        )
        if tool and tool not in followup_tools:
            followup_tools.append(str(tool))

    if not obligations and trigger_mode == "mounted":
        obligations.append(
            {
                "kind": "mounted_idle_tick",
                "status": "ok",
                "reason": (
                    "mounted harness checked this turn and found no configured "
                    "JIKUO obligation"
                ),
                "target_event": None,
                "required_followup_tool": None,
                "matched_terms": [],
            }
        )

    if not obligations:
        obligations.append(
            {
                "kind": "no_jikuo_action_required",
                "status": "ok",
                "reason": "no configured router keyword matched this turn",
                "target_event": None,
                "required_followup_tool": None,
                "matched_terms": [],
            }
        )

    router_status = (
        "requires_action"
        if any(item["status"] == "required" for item in obligations)
        else "ok"
    )
    if obligations and obligations[0]["kind"] in {
        "mounted_idle_tick",
        "no_jikuo_action_required",
    }:
        router_status = "ok"

    router = {
        "schema": CONVERSATION_ROUTER_SCHEMA,
        "trigger_mode": trigger_mode,
        "router_status": router_status,
        "input_summary": input_summary,
        "input_summary_status": input_summary_status,
        "classification_basis": "deterministic_keyword_router_v0",
        "classified_obligations": obligations,
        "required_followup_tools": followup_tools,
        "privacy": {
            "raw_transcript_captured": False,
            "stored_input": "compact_user_supplied_turn_only",
        },
        "non_effects": [
            "does not create .jikuo/task_sessions/",
            "does not create .jikuo/policies/",
            "does not update .jikuo/project_state.yaml",
            "does not capture raw chat transcript",
        ],
    }
    return router, []


def build_policy_suggestion_review(
    *, router: dict[str, Any]
) -> dict[str, Any]:
    obligations = list(router.get("classified_obligations") or [])
    candidate_obligations = [
        obligation
        for obligation in obligations
        if obligation.get("kind") == "policy_suggestion_review"
        and obligation.get("status") == "required"
    ]
    input_summary = str(router.get("input_summary") or "")
    candidates: list[dict[str, Any]] = []
    for obligation in candidate_obligations:
        matched_terms = list(obligation.get("matched_terms") or [])
        candidate_id = stable_id(
            "policy_candidate",
            "|".join(
                [
                    input_summary,
                    ",".join(matched_terms),
                    "conversation_level_policy_suggestion",
                ]
            ),
        )
        candidates.append(
            {
                "candidate_id": candidate_id,
                "candidate_type": "policy_candidate",
                "title": "Conversation-level user need review",
                "trigger_event": "conversation_turn",
                "action_type": (
                    "review_repeated_user_interaction_patterns_for_policy_candidates"
                ),
                "evidence_type": "proactive_policy_suggestion_review_evidence",
                "intended_scope": (
                    "future turns in this project after explicit user approval"
                ),
                "benefit": (
                    "turn repeated user needs into explicit, reviewable governance"
                ),
                "overreach_risk": (
                    "a one-off preference could be over-promoted if accepted without review"
                ),
                "matched_terms": matched_terms,
                "confidence": "heuristic_keyword_signal",
                "recommended_routing": "policy_candidate_review",
                "available_user_decisions": [
                    "approve_as_policy_plan",
                    "revise",
                    "defer",
                    "record_as_insight",
                    "ignore",
                ],
            }
        )

    review_status = "candidate_detected" if candidates else "reviewed_no_candidate"
    return {
        "schema": POLICY_SUGGESTION_REVIEW_SCHEMA,
        "review_status": review_status,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "review_basis": router.get("classification_basis"),
        "source_router_status": router.get("router_status"),
        "source_obligation_kinds": [
            obligation.get("kind") for obligation in obligations
        ],
        "evidence_type": "proactive_policy_suggestion_review_evidence",
        "action_type": (
            "review_repeated_user_interaction_patterns_for_policy_candidates"
        ),
        "recommended_routing": (
            "review_candidate_with_user" if candidates else "no_policy_change"
        ),
        "privacy": {
            "raw_transcript_captured": False,
            "stored_input": "compact_user_supplied_turn_only",
        },
    }


def build_policy_suggestion_review_card(
    *, router: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    review = build_policy_suggestion_review(router=router)
    candidates = list(review["candidates"])
    card_status_value = "review" if candidates else "ok"
    shown_outputs = [
        f"review_status: {review['review_status']}",
        f"candidate_count: {review['candidate_count']}",
        f"recommended_routing: {review['recommended_routing']}",
        f"evidence_type: {review['evidence_type']}",
    ]
    for candidate in candidates:
        shown_outputs.append(
            "policy_candidate: "
            f"{candidate['candidate_id']} / {candidate['title']} / "
            f"routing={candidate['recommended_routing']}"
        )

    next_actions = (
        [
            "ask the user whether to approve, revise, defer, record as insight, or ignore the policy candidate"
        ]
        if candidates
        else [
            "continue; this turn was reviewed and no policy candidate needs user action"
        ]
    )
    card = generic_card(
        card_kind="policy_suggestion_review",
        status=card_status_value,
        title="Proactive policy-suggestion review",
        summary=(
            "JIKUO reviewed this conversation turn for repeated user needs "
            "without writing policy files or storing raw transcripts."
        ),
        shown_inputs=[
            f"source_router_status: {review['source_router_status']}",
            f"review_basis: {review['review_basis']}",
        ],
        shown_outputs=shown_outputs,
        next_actions=next_actions,
    )
    card["policy_suggestion_review"] = review
    trace = atom_trace(
        loop_step_id="DPL-05",
        atom_id="CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01",
        mode="no-write",
        status=card_status_value,
        summary=(
            "reviewed conversation turn for policy candidates and produced "
            "compact evidence without writing policy files"
        ),
    )
    return card, trace


def build_conversation_turn_cards(
    *,
    trigger_mode: str | None,
    user_phrase: str | None,
    task_title: str | None,
    summary: str | None,
    project_root: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    normalized_mode, trigger_mode_source, settings_status = (
        activation_settings.resolve_conversation_trigger_mode(
            project_root=project_root,
            requested_trigger_mode=trigger_mode,
        )
    )
    router, refusals = classify_conversation_turn(
        trigger_mode=normalized_mode,
        user_phrase=user_phrase,
        task_title=task_title,
        summary=summary,
    )
    router["trigger_mode_source"] = trigger_mode_source
    router["activation_settings"] = {
        "status": settings_status.get("status"),
        "desired_trigger_mode": settings_status.get("desired_trigger_mode"),
        "effective_enforcement_level": settings_status.get(
            "effective_enforcement_level"
        ),
        "strict_mount_status": settings_status.get("strict_mount_status"),
        "onboarding_required": bool(settings_status.get("onboarding_required")),
        "required_user_decision_count": len(
            settings_status.get("required_user_decisions") or []
        ),
        "configuration_required": bool(settings_status.get("configuration_required")),
    }
    should_prompt_activation_settings = (
        bool(settings_status.get("onboarding_required"))
        and trigger_mode is None
        and not refusals
    )
    if should_prompt_activation_settings and not any(
        obligation.get("kind") == "configuration_review"
        for obligation in router.get("classified_obligations") or []
    ):
        router["classified_obligations"] = [
            obligation
            for obligation in router.get("classified_obligations") or []
            if obligation.get("kind")
            not in {"mounted_idle_tick", "no_jikuo_action_required"}
        ]
        obligation = {
            "kind": "configuration_review",
            "status": "required",
            "reason": (
                "project activation settings still use implicit or unreviewed "
                "values; review configuration before assuming JIKUO is mounted "
                "or strict"
            ),
            "target_event": "configuration_review",
            "required_followup_tool": (
                "python -B -m jikuo.agent_flow propose --event configuration_review"
            ),
            "matched_terms": ["activation_settings_missing"],
        }
        router["classified_obligations"].insert(0, obligation)
        tools = list(router.get("required_followup_tools") or [])
        if obligation["required_followup_tool"] not in tools:
            tools.insert(0, obligation["required_followup_tool"])
        router["required_followup_tools"] = tools
        router["router_status"] = "requires_action"
    elif settings_status.get("strict_mount_status") == "degraded_instruction_only":
        router["mount_degradation"] = {
            "status": "degraded_instruction_only",
            "reason": (
                "mounted mode is configured but the project is still instruction-only "
                "until a host pre-turn adapter is available"
            ),
            "strict_pre_turn_guaranteed": False,
        }
    router_status = str(router["router_status"])
    card_status_value = (
        "refused"
        if refusals
        else "review"
        if router_status == "requires_action"
        else "ok"
    )
    obligations = list(router["classified_obligations"])
    followup_tools = list(router["required_followup_tools"])
    shown_outputs = [
        f"router_status: {router_status}",
        f"obligation_count: {len(obligations)}",
        f"classification_basis: {router['classification_basis']}",
    ]
    for obligation in obligations:
        shown_outputs.append(
            "obligation: "
            f"{obligation['kind']} / {obligation['status']} / "
            f"target={obligation.get('target_event')}"
        )
    for tool in followup_tools:
        shown_outputs.append(f"required_followup_tool: {tool}")

    if refusals:
        next_actions = ["provide --user-phrase or a compact user-turn summary"]
    elif followup_tools:
        next_actions = [
            "call the listed follow-up tool(s) before continuing user-visible work"
        ]
    elif any(
        obligation.get("kind") == "policy_suggestion_review"
        for obligation in obligations
    ):
        next_actions = [
            "review the policy-suggestion card before continuing user-visible work"
        ]
    else:
        next_actions = [
            "continue; no JIKUO follow-up tool is required for this turn"
        ]

    card = generic_card(
        card_kind="conversation_turn_router",
        status=card_status_value,
        title="Conversation-turn router",
        summary=(
            "JIKUO classified this user turn without writing durable project files."
        ),
        shown_inputs=[
            f"trigger_mode: {normalized_mode}",
            f"trigger_mode_source: {trigger_mode_source}",
            f"activation_settings_status: {settings_status.get('status')}",
            f"user_phrase_provided: {str(bool(user_phrase)).lower()}",
            f"summary_provided: {str(bool(summary)).lower()}",
            f"task_title_provided: {str(bool(task_title)).lower()}",
        ],
        shown_outputs=shown_outputs,
        refusal_reasons=refusals,
        next_actions=next_actions,
    )
    card["conversation_router"] = router
    trace = atom_trace(
        loop_step_id="DPL-05",
        atom_id="CAP-CONVERSATION-TURN-ROUTER-01",
        mode="no-write",
        status=card_status_value,
        summary="classified a user turn into JIKUO obligations without writing files",
    )
    cards = [card]
    traces = [trace]
    if not refusals:
        review_card, review_trace = build_policy_suggestion_review_card(router=router)
        cards.append(review_card)
        traces.append(review_trace)
    return cards, traces, refusals


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
    session_id: str | None,
    owner_agent: str,
    task_session_decision: str | None = None,
    task_session_defer_reason: str | None = None,
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

    processing_resolution = {
        "schema": "jikuo.task_start_resolution.v0",
        "status": "processing_started",
        "lifecycle_event": "task_start",
        "task_title": task_title,
        "durable_task_session_status": "separate_guarded_decision",
        "requires_task_session_write": False,
        "allowed_next_decisions": [
            "bind_existing_task_session",
            "approve_guarded_task_session_start",
            "explicitly_defer_task_session",
            "continue_lightweight_task_start",
        ],
    }
    processing_card = generic_card(
        card_kind="task_start_processing",
        status="ok",
        title="Task start processing",
        summary=(
            "Lightweight task_start processing is active without creating a "
            "durable task-session."
        ),
        shown_inputs=[
            f"project_root: {project_root}",
            f"task_title: {task_title}",
            f"session_id: {session_id or 'not_supplied'}",
        ],
        shown_outputs=[
            "lifecycle_event: task_start",
            "processing_status: processing_started",
            "task_session_start: separate_guarded_decision",
            "durable_write_performed: false",
        ],
        next_actions=[
            "continue lightweight task processing",
            "review task-session resolution separately before any durable session write",
        ],
    )
    processing_card["task_start_resolution"] = processing_resolution
    processing_traces = [
        atom_trace(
            loop_step_id="DPL-04",
            atom_id="CAP-TASK-START-PROCESSING-01",
            mode="no-write",
            status="ok",
            summary="recorded lightweight task_start processing separately from task-session start",
        )
    ]

    if session_id:
        status_report = task_session.build_status_report(
            project_root=project_root,
            session_id=session_id,
        )
        if status_report.get("session_status") == "found":
            card = generic_card(
                card_kind="task_session_binding",
                status="ok",
                title="Task-session binding",
                summary="An existing task-session is bound to this governed slice.",
                shown_inputs=[
                    f"project_root: {status_report.get('project_root')}",
                    f"session_id: {session_id}",
                ],
                shown_outputs=[
                    f"matches: {len(status_report.get('matched_paths', []))}",
                    *[
                        f"session_path: {match}"
                        for match in status_report.get("matched_paths", [])
                    ],
                ],
                next_actions=[
                    "use the bound task-session for evidence, completion, and handoff updates"
                ],
            )
            card["task_session_refs"] = [session_id]
            card["task_session_binding_status"] = "existing_session_bound"
            card["task_session_resolution"] = {
                "schema": "jikuo.task_session_resolution.v0",
                "status": "existing_session_bound",
                "decision": "bind_existing_task_session",
                "requires_user_decision": False,
                "allowed_next_decisions": ["continue_with_bound_task_session"],
            }
            traces = [
                atom_trace(
                    loop_step_id="DPL-04",
                    atom_id="CAP-TASK-STATUS-01",
                    mode="no-write",
                    status="found",
                    summary="verified explicit task-session binding for task start",
                ),
                atom_trace(
                    loop_step_id="DPL-06",
                    atom_id="CAP-CARD-TASKSESSION-01",
                    mode="no-write",
                    status=card_status(card),
                    summary="projected existing task-session binding into a desktop card",
                ),
            ]
            return [processing_card, card], processing_traces + traces, []
    if task_session_decision == "defer":
        if not task_session_defer_reason:
            refusal = "task_session_defer_reason_required"
            card = generic_card(
                card_kind="task_session_resolution_refusal",
                status="refused",
                title="Task-session defer needs a reason",
                summary=(
                    "Explicitly deferring task-session creation requires a compact "
                    "reason so the governed slice does not silently lose lifecycle context."
                ),
                refusal_reasons=[refusal],
                next_actions=[
                    "provide --task-session-defer-reason before explicitly deferring"
                ],
            )
            return [processing_card, card], processing_traces, [refusal]
        resolution = {
            "schema": "jikuo.task_session_resolution.v0",
            "status": "explicitly_deferred",
            "decision": "explicitly_defer_task_session",
            "requires_user_decision": False,
            "reason": task_session_defer_reason,
            "allowed_next_decisions": ["continue_without_task_session_for_this_slice"],
        }
        card = generic_card(
            card_kind="task_session_binding",
            status="review",
            title="Task-session resolution",
            summary=(
                "Task-session creation is explicitly deferred for this governed slice."
            ),
            shown_inputs=[
                f"project_root: {project_root}",
                f"task_title: {task_title}",
            ],
            shown_outputs=[
                "task_session_resolution_status: explicitly_deferred",
                f"defer_reason: {task_session_defer_reason}",
            ],
            next_actions=[
                "continue only in lightweight/no-session mode for this slice",
                "report the task-session deferral in the final user summary",
            ],
        )
        card["task_session_refs"] = []
        card["task_session_binding_status"] = "explicitly_deferred"
        card["task_session_resolution"] = resolution
        traces = [
            atom_trace(
                loop_step_id="DPL-04",
                atom_id="CAP-TASK-SESSION-RESOLUTION-01",
                mode="no-write",
                status="explicitly_deferred",
                summary="recorded explicit task-session deferral as no-write resolution evidence",
            ),
            atom_trace(
                loop_step_id="DPL-06",
                atom_id="CAP-CARD-TASKSESSION-01",
                mode="no-write",
                status=card_status(card),
                summary="projected explicit task-session deferral into a desktop card",
            ),
        ]
        return [processing_card, card], processing_traces + traces, []

    plan = task_session.build_start_plan(
        project_root=project_root,
        task_title=task_title,
        owner_agent=owner_agent,
    )
    card = task_session_cards.build_card(plan)
    if plan.get("can_start") and card.get("command_proposal"):
        card = dict(card)
        command = dict(card["command_proposal"])
        command["command_kind"] = "agent_flow_task_session_start"
        command["expected_result_schema"] = APPLY_RESULT_SCHEMA
        command["command_preview"] = " ".join(
            [
                "python -B -m jikuo.agent_flow apply",
                "--operation",
                command_arg("task_session_start"),
                "--task-title",
                command_arg(task_title),
                "--owner-agent",
                command_arg(owner_agent),
                "--project-root",
                command_arg(plan["project_root"]),
                "--confirm-apply",
                "--approval-phrase",
                command_arg(APPROVAL_PHRASE_PLACEHOLDER),
                "--format json",
            ]
        )
        command["required_flags"] = ["--confirm-apply", "--approval-phrase"]
        card["command_proposal"] = command
        if card.get("approval_request"):
            approval = dict(card["approval_request"])
            approval["approved_command_kind"] = "agent_flow_task_session_start"
            card["approval_request"] = approval
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
    return [processing_card, card], processing_traces + traces, []


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
        if event == "completion_review":
            card = generic_card(
                card_kind="task_session_lifecycle_unavailable",
                status="review",
                title="Task-session lifecycle context unavailable",
                summary=(
                    "Completion policy review can continue; no guarded lifecycle "
                    "update is ready without an explicit task-session id."
                ),
                refusal_reasons=[refusal],
                next_actions=[
                    "review completion policy status",
                    "provide --session-id only if a task-session lifecycle update is needed",
                ],
            )
            return [card], [], []
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
    if event == "completion_review" and card_status(card) == "refused":
        card = dict(card)
        card["status"] = "review"
        card["card_kind"] = "task_session_lifecycle_unavailable"
        card["title"] = "Task-session lifecycle context unavailable"
        card["user_facing_summary"] = (
            "Completion policy review can continue; no guarded lifecycle update "
            "is ready from this preview."
        )
        card["next_actions"] = [
            "review completion policy status",
            "resolve task-session context only if a lifecycle update is needed",
        ]
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
    policy_work_profile_lifecycle_events: list[str] | None,
    policy_work_profile_policy_scopes: list[str] | None,
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
        work_profile_lifecycle_events=policy_work_profile_lifecycle_events,
        work_profile_policy_scopes=policy_work_profile_policy_scopes,
        action_type=policy_action_type,
        evidence_type=policy_evidence_type,
    )
    write_outputs = [
        f"plan_id: {plan['plan_id']}",
        f"policy_ref: {plan['policy_ref']}",
        f"policy_store_status: {plan['policy_store_status']}",
        f"conditions: {len(plan['proposed_policy'].get('conditions', []))}",
    ]
    authoring_review = plan.get("authoring_review") or {}
    authoring_warnings = authoring_review.get("warnings") or []
    write_outputs.extend(
        [
            f"authoring_mode: {authoring_review.get('mode', 'unknown')}",
            "compatibility_trigger_event: "
            + str(authoring_review.get("compatibility_trigger_event") or "none"),
        ]
    )
    for warning in authoring_warnings:
        write_outputs.append(f"authoring_warning: {warning}")
    write_outputs.extend(
        f"would_write: {item['path']} ({item['effect']})"
        for item in plan["write_set"]
    )
    command_parts = [
        "python",
        "-B",
        "-m",
        "jikuo.policy_store",
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
        command_parts.extend(
            ["--changed-path-pattern", command_arg(policy_changed_path_pattern)]
        )
    if policy_added_path_pattern:
        command_parts.extend(
            ["--added-path-pattern", command_arg(policy_added_path_pattern)]
        )
    for lifecycle_event in policy_work_profile_lifecycle_events or []:
        command_parts.extend(
            ["--work-profile-lifecycle-event", command_arg(lifecycle_event)]
        )
    for policy_scope in policy_work_profile_policy_scopes or []:
        command_parts.extend(["--work-profile-policy-scope", command_arg(policy_scope)])
    shown_inputs = [
        f"policy_ref: {policy_ref}",
        f"policy_title: {policy_title}",
        f"authoring_mode: {authoring_review.get('mode', 'unknown')}",
        f"trigger_event: {policy_trigger_event}",
        f"action_type: {policy_action_type}",
        f"evidence_type: {policy_evidence_type}",
    ]
    if policy_work_profile_lifecycle_events:
        shown_inputs.append(
            "work_profile_lifecycle_events: "
            + ", ".join(policy_work_profile_lifecycle_events)
        )
    if policy_work_profile_policy_scopes:
        shown_inputs.append(
            "work_profile_policy_scopes: "
            + ", ".join(policy_work_profile_policy_scopes)
        )
    card = generic_card(
        card_kind="policy_write_plan",
        status=plan["status"],
        title="Policy write plan proposal",
        summary=(
            "A project policy write plan is ready for chat review; no policy files were written."
            if plan["status"] != "refused"
            else "Policy write plan could not be prepared safely."
        ),
        shown_inputs=shown_inputs,
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
    replacement_trigger_event: str,
    replacement_work_profile_lifecycle_events: list[str] | None,
    replacement_work_profile_policy_scopes: list[str] | None,
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
        replacement_trigger_event=replacement_trigger_event,
        replacement_work_profile_lifecycle_events=replacement_work_profile_lifecycle_events,
        replacement_work_profile_policy_scopes=replacement_work_profile_policy_scopes,
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
    shown_inputs = [
        f"policy_ref: {policy_ref}",
        f"operation: {operation}",
        f"feedback_type: {feedback_type}",
        f"summary: {summary}",
    ]
    if operation == "supersede_policy":
        shown_inputs.append(f"replacement_policy_ref: {replacement_policy_ref}")
    else:
        shown_inputs.extend([
            f"replacement_trigger_event: {replacement_trigger_event}",
            f"replacement_work_profile_lifecycle_events: {', '.join(replacement_work_profile_lifecycle_events or [])}",
            f"replacement_work_profile_policy_scopes: {', '.join(replacement_work_profile_policy_scopes or [])}",
        ])
    card = generic_card(
        card_kind="policy_evolution_plan",
        status=plan["status"],
        title="Policy evolution plan proposal",
        summary=(
            "A policy evolution plan is ready for chat review; no policy files were written."
            if plan["status"] != "refused"
            else "Policy evolution plan could not be prepared safely."
        ),
        shown_inputs=shown_inputs,
        shown_outputs=outputs,
        refusal_reasons=plan["refusal_reasons"],
        next_actions=plan["next_actions"],
    )
    card["policy_evolution_plan"] = plan
    if (
        operation in policy_store.POLICY_EVOLUTION_WRITE_SUPPORTED_OPERATIONS
        and plan["status"] != "refused"
    ):
        command_parts = [
            "python",
            "-B",
            "-m",
            "jikuo.policy_store",
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
        if operation == "refine_policy":
            if replacement_trigger_event:
                command_parts.extend([
                    "--replacement-trigger-event",
                    command_arg(replacement_trigger_event),
                ])
            for lifecycle_event in replacement_work_profile_lifecycle_events or []:
                command_parts.extend([
                    "--replacement-work-profile-lifecycle-event",
                    command_arg(lifecycle_event),
                ])
            for policy_scope in replacement_work_profile_policy_scopes or []:
                command_parts.extend([
                    "--replacement-work-profile-policy-scope",
                    command_arg(policy_scope),
                ])
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
        if operation == "supersede_policy":
            if replacement_policy_ref:
                command_parts.extend(["--replacement-policy-id", command_arg(replacement_policy_ref)])
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


def build_starter_policy_pack_init_cards(
    *,
    project_root: Path | None,
    starter_pack_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    plan = starter_policies.build_starter_init_plan(
        project_root=project_root,
        pack_id=starter_pack_id,
    )
    outputs = [
        f"plan_id: {plan['plan_id']}",
        f"pack_id: {plan['pack_id']}",
        f"project_state_status: {plan['project_state_status']}",
        f"policy_store_status: {plan['policy_store_status']}",
        f"starter_policy_count: {len(plan['starter_policies'])}",
        f"would_create_registry: {plan['would_create_registry']}",
        f"would_create_project_state: {plan['would_create_project_state']}",
    ]
    outputs.extend(
        f"starter_policy: {item['policy_id']} ({item['title']})"
        for item in plan["starter_policies"]
    )
    outputs.extend(
        f"would_write: {item['path']} ({item['effect']})"
        for item in plan["write_set"]
    )
    command_parts = [
        "python",
        "-B",
        "-m",
        "jikuo.agent_flow",
        "apply",
        "--operation",
        command_arg("starter_policy_pack_init"),
        "--project-root",
        command_arg(str(project_root or ".")),
        "--starter-pack-id",
        command_arg(starter_pack_id),
        "--confirm-apply",
        "--approval-phrase",
        command_arg(APPROVAL_PHRASE_PLACEHOLDER),
        "--format",
        "json",
    ]
    card = generic_card(
        card_kind="starter_policy_pack_init_plan",
        status=plan["status"],
        title="Starter policy pack initialization plan",
        summary=(
            "A starter policy pack can initialize this project with report-only policies after approval."
            if plan["status"] != "refused"
            else "Starter policy pack initialization could not be prepared safely."
        ),
        shown_inputs=[
            f"project_root: {project_root or '.'}",
            f"starter_pack_id: {starter_pack_id}",
        ],
        shown_outputs=outputs,
        refusal_reasons=plan["refusal_reasons"],
        next_actions=plan["next_actions"],
    )
    card["starter_policy_pack_init_plan"] = plan
    card["command_proposal"] = {
        "command_preview": " ".join(command_parts),
        "approval_required": True,
        "technical_confirmation_required": True,
        "writes_if_approved": [item["path"] for item in plan["write_set"]],
        "non_effects": plan["non_effects"],
    }
    card["write_effect"] = {
        "target": "JIKUO first-use starter policy initialization",
        "effect": "renders a starter policy pack initialization plan only; no durable write is performed",
        "non_effects": plan["non_effects"],
    }
    trace = atom_trace(
        loop_step_id="DPL-05",
        atom_id="CAP-STARTER-POLICY-PACK-INIT-01",
        mode="no-write",
        status=plan["status"],
        summary="built starter policy pack initialization plan without writing project files",
    )
    return [card], [trace], list(plan["refusal_reasons"])


def build_policy_template_import_plan_cards(
    *,
    project_root: Path | None,
    template_path: Path | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    if template_path is None:
        refusal = "template_required_for_policy_template_import_plan"
        card = generic_card(
            card_kind="policy_template_import_refusal",
            status="refused",
            title="Policy template import plan needs a template",
            summary="Template import planning requires an explicit reusable policy template path.",
            shown_inputs=[f"project_root: {project_root or '.'}"],
            refusal_reasons=[refusal],
            next_actions=["provide --template before retrying template import planning"],
        )
        trace = atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01",
            mode="no-write",
            status="refused",
            summary="refused policy-template import planning because no template path was provided",
        )
        return [card], [trace], [refusal]

    plan = policy_templates.build_import_plan(
        template_path=template_path,
        project_root=project_root,
    )
    binding_status = list(plan.get("binding_status", []))
    binding_counts: dict[str, int] = {}
    for item in binding_status:
        status = str(item.get("status") or "unknown")
        binding_counts[status] = binding_counts.get(status, 0) + 1

    outputs = [
        f"plan_id: {plan['plan_id']}",
        f"status: {plan['status']}",
        f"template_ref: {plan.get('template_ref')}",
        f"project_context_status: {plan['project_context_status']}",
        f"policy_store_status: {plan['policy_store_status']}",
        f"binding_count: {len(binding_status)}",
        f"resolved_binding_count: {binding_counts.get('resolved', 0)}",
        f"missing_binding_count: {sum(count for status, count in binding_counts.items() if status != 'resolved')}",
    ]
    preview = plan.get("resolved_policy_preview") or {}
    if preview.get("policy_id"):
        outputs.append(f"resolved_policy_ref: {preview.get('policy_id')}")
    outputs.append(f"proposal_ref: {plan.get('proposal_ref')}")
    outputs.append(f"decision_record_ref: {plan.get('decision_record_ref')}")
    outputs.extend(
        f"binding: {item.get('role_ref')} -> {item.get('status')} ({item.get('resolved_ref')})"
        for item in binding_status
    )
    outputs.extend(
        f"would_write: {item['path']} ({item['effect']})"
        for item in plan.get("write_set", [])
    )

    activation_blockers = (
        ["template_import_bindings_unresolved"]
        if plan["status"] == "missing_binding"
        else []
    )
    plan_refusals = list(plan["refusal_reasons"]) + activation_blockers
    card_status_value = "refused" if plan["status"] == "refused" else "review"
    card = generic_card(
        card_kind="policy_template_import_plan",
        status=card_status_value,
        title="Policy template import plan",
        summary=(
            "A reusable policy template is resolved against project context; activation still requires approval."
            if plan["status"] == "review"
            else "Policy template import needs resolved project-context bindings before activation."
            if plan["status"] == "missing_binding"
            else "Policy template import planning could not be prepared safely."
        ),
        shown_inputs=[
            f"project_root: {project_root or '.'}",
            f"template: {template_path}",
            f"project_context_ref: {policy_templates.PROJECT_CONTEXT_REF}",
        ],
        shown_outputs=outputs,
        refusal_reasons=plan_refusals,
        next_actions=plan["next_actions"],
    )
    card["policy_template_import_plan"] = plan
    card["write_effect"] = {
        "target": ".jikuo/policies/ (future guarded template activation target)",
        "effect": "renders a template import plan only; no durable write is performed",
        "non_effects": plan["non_effects"],
    }
    if plan["status"] == "review":
        command_parts = [
            "python",
            "-B",
            "-m",
            "jikuo.agent_flow",
            "apply",
            "--operation",
            command_arg("policy_template_activation"),
            "--project-root",
            command_arg(str(project_root or ".")),
            "--template",
            command_arg(str(template_path)),
            "--confirm-apply",
            "--approval-phrase",
            command_arg(APPROVAL_PHRASE_PLACEHOLDER),
            "--format",
            "json",
        ]
        card["command_proposal"] = {
            "command_preview": " ".join(command_parts),
            "approval_required": True,
            "technical_confirmation_required": True,
            "writes_if_approved": [
                item["path"] for item in plan.get("write_set", [])
            ],
            "non_effects": [
                "does not execute policy actions",
                "does not promote gates or blocking enforcement",
                "does not modify package template files",
                "does not write project_context bindings",
            ],
        }

    traces = [
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-PROJECT-CONTEXT-RESOLVER-01",
            mode="no-write",
            status=plan["project_context_status"],
            summary="resolved policy-template bindings through project_context without writing files",
        ),
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-POLICY-TEMPLATE-IMPORT-PLAN-01",
            mode="no-write",
            status=plan["status"],
            summary="built resolved-policy preview and guarded activation write set without writing files",
        ),
        atom_trace(
            loop_step_id="DPL-06",
            atom_id="CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01",
            mode="no-write",
            status=card_status_value,
            summary="projected policy-template import planning into a visible desktop card",
        ),
    ]
    return [card], traces, plan_refusals


def build_policy_distribution_review_cards(
    *,
    project_root: Path | None,
    policy_ref: str | None,
    source_policy_path: Path | None,
    policy_query: str | None,
    decision: str,
    source_project_ref: str | None,
    starter_pack_id: str,
    rationale: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    resolved_root = (project_root or Path.cwd()).expanduser().resolve()
    resolution = policy_templates.resolve_distribution_source_policy(
        project_root=resolved_root,
        policy_ref=policy_ref,
        source_policy_path=source_policy_path,
        policy_query=policy_query,
    )
    if resolution.get("status") != "resolved":
        candidates = resolution.get("candidates") or []
        outputs = [
            f"resolution_status: {resolution.get('status')}",
            f"resolution_basis: {resolution.get('resolution_basis')}",
            f"candidate_count: {len(candidates)}",
        ]
        outputs.extend(
            f"candidate: {item.get('policy_id')} ({item.get('title')}) score={item.get('match_score', 'n/a')}"
            for item in candidates
        )
        card = generic_card(
            card_kind="policy_distribution_source_resolution",
            status="review",
            title="Policy distribution source needs selection",
            summary=(
                "Natural-language policy selection did not resolve to exactly one active policy; "
                "choose a candidate before distribution review."
            ),
            shown_inputs=[
                f"project_root: {resolved_root}",
                f"policy_ref: {policy_ref or 'not_supplied'}",
                f"policy_query: {policy_query or 'not_supplied'}",
            ],
            shown_outputs=outputs,
            refusal_reasons=list(resolution.get("refusal_reasons") or []),
            next_actions=[
                "ask the host AI to select one candidate policy_id",
                "retry policy_distribution_review with policy_ref or a more specific policy_query",
            ],
        )
        card["policy_distribution_source_resolution"] = resolution
        card["write_effect"] = {
            "target": "none",
            "effect": "renders candidate policy choices only; no durable write is performed",
            "non_effects": resolution.get("non_effects") or [],
        }
        trace = atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-POLICY-DISTRIBUTION-REVIEW-01",
            mode="no-write",
            status=str(resolution.get("status") or "review"),
            summary="resolved natural-language policy distribution request to candidate policies without writing files",
        )
        return [card], [trace], list(resolution.get("refusal_reasons") or [])

    source_path = Path(str(resolution["source_policy_path"]))
    review = policy_templates.build_distribution_review(
        source_policy_path=source_path,
        decision=decision,
        source_project_ref=source_project_ref,
        starter_pack_id=starter_pack_id,
        rationale=rationale,
    )
    distribution_path = review.get("distribution_path") or {}
    portability = review.get("template_portability") or {}
    outputs = [
        f"resolution_basis: {resolution.get('resolution_basis')}",
        f"policy_id: {review.get('policy_id')}",
        f"title: {review.get('title')}",
        f"source_category: {review.get('source_category')}",
        f"distribution_decision: {review.get('distribution_decision')}",
        f"approval_required_for_publication: {review.get('approval_required_for_publication')}",
    ]
    if distribution_path.get("target_template_ref"):
        outputs.append(f"target_template_ref: {distribution_path.get('target_template_ref')}")
    if portability:
        outputs.append(f"template_portability_status: {portability.get('status')}")
        outputs.append(
            f"template_required_binding_count: {portability.get('required_binding_count')}"
        )

    card = generic_card(
        card_kind="policy_distribution_review",
        status=review["status"],
        title="Policy distribution review",
        summary=(
            "A policy distribution decision has been reviewed without publishing or activating the policy."
            if review["status"] != "refused"
            else "Policy distribution review could not be prepared safely."
        ),
        shown_inputs=[
            f"project_root: {resolved_root}",
            f"policy_ref: {policy_ref or resolution.get('policy_ref') or 'not_supplied'}",
            f"policy_query: {policy_query or 'not_supplied'}",
            f"decision: {decision}",
        ],
        shown_outputs=outputs,
        refusal_reasons=list(review.get("refusal_reasons") or []),
        next_actions=list(review.get("next_actions") or []),
    )
    card["policy_distribution_review"] = review
    card["policy_distribution_source_resolution"] = resolution
    card["write_effect"] = {
        "target": "none",
        "effect": "renders a distribution review only; no durable write is performed",
        "non_effects": review["non_effects"],
    }
    if decision in {"official_starter", "optional_template"} and review["status"] == "review":
        card["command_proposal"] = {
            "command_preview": " ".join(
                [
                    "python",
                    "-B",
                    "-m",
                    "jikuo.policy_templates",
                    "export-template",
                    "--source-policy",
                    command_arg(str(source_path)),
                    "--source-project-ref",
                    command_arg(source_project_ref or "JIKUO-dogfood"),
                    "--confirm-export-template",
                    "--approval-phrase",
                    command_arg(APPROVAL_PHRASE_PLACEHOLDER),
                    "--format",
                    "json",
                ]
            ),
            "approval_required": True,
            "technical_confirmation_required": True,
            "writes_if_approved": [str(distribution_path.get("target_template_ref") or "")],
            "non_effects": review["non_effects"],
        }
    trace = atom_trace(
        loop_step_id="DPL-05",
        atom_id="CAP-POLICY-DISTRIBUTION-REVIEW-01",
        mode="no-write",
        status=review["status"],
        summary="built policy distribution review without exporting templates or activating user policies",
    )
    return [card], [trace], list(review.get("refusal_reasons") or [])


def build_policy_template_publication_plan_cards(
    *,
    project_root: Path | None,
    policy_ref: str | None,
    source_policy_path: Path | None,
    policy_query: str | None,
    decision: str,
    source_project_ref: str | None,
    starter_pack_id: str,
    rationale: str | None,
    target_dir: Path | None,
    namespace: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    resolved_root = (project_root or Path.cwd()).expanduser().resolve()
    resolution = policy_templates.resolve_distribution_source_policy(
        project_root=resolved_root,
        policy_ref=policy_ref,
        source_policy_path=source_policy_path,
        policy_query=policy_query,
    )
    if resolution.get("status") != "resolved":
        candidates = resolution.get("candidates") or []
        card = generic_card(
            card_kind="policy_template_publication_source_resolution",
            status="review",
            title="Policy template publication needs a source policy",
            summary=(
                "Policy template publication did not resolve to exactly one active policy; "
                "choose a source before planning a package-template write."
            ),
            shown_inputs=[
                f"project_root: {resolved_root}",
                f"policy_ref: {policy_ref or 'not_supplied'}",
                f"policy_query: {policy_query or 'not_supplied'}",
            ],
            shown_outputs=[
                f"resolution_status: {resolution.get('status')}",
                f"resolution_basis: {resolution.get('resolution_basis')}",
                f"candidate_count: {len(candidates)}",
                *[
                    f"candidate: {item.get('policy_id')} ({item.get('title')}) score={item.get('match_score', 'n/a')}"
                    for item in candidates
                ],
            ],
            refusal_reasons=list(resolution.get("refusal_reasons") or []),
            next_actions=[
                "ask the host AI to select one candidate policy_id",
                "retry policy_template_publication_plan with policy_ref or a more specific policy_query",
            ],
        )
        card["policy_distribution_source_resolution"] = resolution
        card["write_effect"] = {
            "target": "none",
            "effect": "renders source-policy choices only; no durable write is performed",
            "non_effects": resolution.get("non_effects") or [],
        }
        return [card], [
            atom_trace(
                loop_step_id="DPL-05",
                atom_id="CAP-POLICY-TEMPLATE-PUBLICATION-PLAN-01",
                mode="no-write",
                status=str(resolution.get("status") or "review"),
                summary="resolved policy-template publication source candidates without writing files",
            )
        ], list(resolution.get("refusal_reasons") or [])

    source_path = Path(str(resolution["source_policy_path"]))
    plan = policy_templates.build_template_publication_plan(
        source_policy_path=source_path,
        decision=decision,
        target_dir=target_dir,
        namespace=namespace,
        source_project_ref=source_project_ref,
        starter_pack_id=starter_pack_id,
        rationale=rationale,
    )
    outputs = [
        f"resolution_basis: {resolution.get('resolution_basis')}",
        f"policy_id: {plan.get('policy_id')}",
        f"title: {plan.get('title')}",
        f"distribution_decision: {plan.get('distribution_decision')}",
        f"target_template_ref: {plan.get('target_template_ref')}",
        f"starter_pack_manifest_change_required: {plan.get('starter_pack_manifest_change_required')}",
        f"approval_required_for_publication: {plan.get('approval_required_for_publication')}",
    ]
    card = generic_card(
        card_kind="policy_template_publication_plan",
        status=plan["status"],
        title="Policy template publication plan",
        summary=(
            "A package policy template publication has been planned without writing files."
            if plan["status"] != "refused"
            else "Policy template publication could not be prepared safely."
        ),
        shown_inputs=[
            f"project_root: {resolved_root}",
            f"policy_ref: {policy_ref or resolution.get('policy_ref') or 'not_supplied'}",
            f"policy_query: {policy_query or 'not_supplied'}",
            f"decision: {decision}",
            f"target_dir: {target_dir or 'default_package_template_root'}",
            f"namespace: {namespace}",
        ],
        shown_outputs=outputs,
        refusal_reasons=list(plan.get("refusal_reasons") or []),
        next_actions=list(plan.get("next_actions") or []),
    )
    card["policy_template_publication_plan"] = plan
    card["policy_distribution_source_resolution"] = resolution
    card["write_effect"] = {
        "target": "none",
        "effect": "renders a package-template publication plan only; no durable write is performed",
        "non_effects": plan["non_effects"],
    }
    if plan["status"] == "review":
        preview_parts = [
            "python",
            "-B",
            "-m",
            "jikuo.agent_flow",
            "apply",
            "--operation",
            command_arg("policy_template_publication"),
            "--distribution-source-policy",
            command_arg(str(source_path)),
            "--distribution-decision",
            command_arg(decision),
            "--starter-pack-id",
            command_arg(starter_pack_id),
        ]
        if target_dir is not None:
            preview_parts.extend(["--publication-target-dir", command_arg(str(target_dir))])
        if namespace != policy_templates.DEFAULT_NAMESPACE:
            preview_parts.extend(["--publication-namespace", command_arg(namespace)])
        if source_project_ref:
            preview_parts.extend(["--distribution-source-project-ref", command_arg(source_project_ref)])
        if rationale:
            preview_parts.extend(["--distribution-rationale", command_arg(rationale)])
        preview_parts.extend(
            [
                "--confirm-apply",
                "--approval-phrase",
                command_arg(APPROVAL_PHRASE_PLACEHOLDER),
                "--format",
                "json",
            ]
        )
        card["command_proposal"] = {
            "command_kind": "agent_flow_policy_template_publication",
            "command_preview": " ".join(preview_parts),
            "expected_result_schema": APPLY_RESULT_SCHEMA,
            "approval_required": True,
            "technical_confirmation_required": True,
            "requires_user_approval": True,
            "writes_if_approved": [str(item.get("path")) for item in plan.get("write_set") or []],
            "non_effects": plan["non_effects"],
        }
    return [card], [
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-POLICY-TEMPLATE-PUBLICATION-PLAN-01",
            mode="no-write",
            status=plan["status"],
            summary="built package policy-template publication plan without writing files",
        )
    ], list(plan.get("refusal_reasons") or [])


def build_starter_manifest_publication_plan_cards(
    *,
    template_ref: str | None,
    starter_pack_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    if not template_ref:
        refusal = "template_ref_required_for_starter_manifest_publication"
        card = generic_card(
            card_kind="starter_manifest_publication_refusal",
            status="refused",
            title="Starter manifest publication needs a template ref",
            summary=(
                "A starter-pack manifest publication plan requires a package template ref."
            ),
            refusal_reasons=[refusal],
            next_actions=[
                "provide --template-ref before retrying starter manifest publication planning"
            ],
        )
        return [card], [
            atom_trace(
                loop_step_id="DPL-05",
                atom_id="CAP-STARTER-MANIFEST-PUBLICATION-PLAN-01",
                mode="no-write",
                status="refused",
                summary="refused starter manifest publication planning because no template_ref was provided",
            )
        ], [refusal]

    plan = starter_policies.build_starter_manifest_publication_plan(
        template_ref=template_ref,
        pack_id=starter_pack_id,
    )
    card = generic_card(
        card_kind="starter_manifest_publication_plan",
        status=plan["status"],
        title="Starter manifest publication plan",
        summary=(
            "A package starter manifest update has been planned without writing files."
            if plan["status"] != "refused"
            else "Starter manifest publication could not be prepared safely."
        ),
        shown_inputs=[
            f"starter_pack_id: {starter_pack_id}",
            f"template_ref: {template_ref}",
        ],
        shown_outputs=[
            f"manifest_path: {plan.get('manifest_path')}",
            f"policy_id: {plan.get('policy_id')}",
            f"title: {plan.get('title')}",
            f"existing_template_count: {plan.get('existing_template_count')}",
            f"approval_required: {plan.get('approval_required')}",
        ],
        refusal_reasons=list(plan.get("refusal_reasons") or []),
        next_actions=list(plan.get("next_actions") or []),
    )
    card["starter_manifest_publication_plan"] = plan
    card["write_effect"] = {
        "target": "none",
        "effect": "renders a starter-pack manifest publication plan only; no durable write is performed",
        "non_effects": plan["non_effects"],
    }
    if plan["status"] == "review":
        card["command_proposal"] = {
            "command_kind": "agent_flow_starter_manifest_publication",
            "command_preview": " ".join(
                [
                    "python",
                    "-B",
                    "-m",
                    "jikuo.agent_flow",
                    "apply",
                    "--operation",
                    command_arg("starter_manifest_publication"),
                    "--template-ref",
                    command_arg(template_ref),
                    "--starter-pack-id",
                    command_arg(starter_pack_id),
                    "--confirm-apply",
                    "--approval-phrase",
                    command_arg(APPROVAL_PHRASE_PLACEHOLDER),
                    "--format",
                    "json",
                ]
            ),
            "expected_result_schema": APPLY_RESULT_SCHEMA,
            "approval_required": True,
            "technical_confirmation_required": True,
            "requires_user_approval": True,
            "writes_if_approved": [str(item.get("path")) for item in plan.get("write_set") or []],
            "non_effects": plan["non_effects"],
        }
    return [card], [
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-STARTER-MANIFEST-PUBLICATION-PLAN-01",
            mode="no-write",
            status=plan["status"],
            summary="built starter-pack manifest publication plan without writing files",
        )
    ], list(plan.get("refusal_reasons") or [])


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


def build_configuration_review_cards(
    *, project_root: Path | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    review = configuration_review.build_configuration_review(project_root=project_root)
    summary = review.get("summary") or {}
    shown_outputs = [
        f"configuration_status: {review.get('status')}",
        f"ok_count: {summary.get('ok_count')}",
        f"review_count: {summary.get('review_count')}",
        f"blocked_count: {summary.get('blocked_count')}",
    ]
    for entry in review.get("items") or []:
        shown_outputs.append(
            f"{entry.get('key')}: {entry.get('status')} - {entry.get('current')}"
        )
    card = generic_card(
        card_kind="configuration_review",
        status=str(review.get("status") or "review"),
        title="JIKUO configuration review",
        summary=(
            "JIKUO checked first-use and ongoing configuration state without "
            "performing durable writes."
        ),
        shown_inputs=[
            f"project_root: {review.get('project_root')}",
            "review_scope: activation, instructions, runtime, MCP, project context, starter policies, guarded writes",
        ],
        shown_outputs=shown_outputs,
        next_actions=review.get("next_actions") or [],
    )
    card["configuration_review"] = review
    traces = [
        atom_trace(
            loop_step_id="DPL-05",
            atom_id="CAP-CONFIGURATION-REVIEW-01",
            mode="no-write",
            status=str(review.get("status") or "review"),
            summary="aggregated first-use JIKUO configuration state for user review",
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
    policy_work_profile_lifecycle_events: list[str] | None = None,
    policy_work_profile_policy_scopes: list[str] | None = None,
    policy_action_type: str = "render_pre_task_review",
    policy_evidence_type: str = "card_rendered",
    distribution_source_policy_path: Path | None = None,
    distribution_policy_query: str | None = None,
    distribution_decision: str = "deferred",
    distribution_rationale: str | None = None,
    distribution_source_project_ref: str | None = None,
    publication_target_dir: Path | None = None,
    publication_namespace: str = policy_templates.DEFAULT_NAMESPACE,
    policy_evolution_operation: str = "refine_policy",
    replacement_policy_ref: str | None = None,
    replacement_title: str | None = None,
    replacement_trigger_event: str = "task_start",
    replacement_work_profile_lifecycle_events: list[str] | None = None,
    replacement_work_profile_policy_scopes: list[str] | None = None,
    replacement_task_type: str | None = None,
    replacement_jikuo_layer: str | None = None,
    replacement_changed_path_pattern: str | None = None,
    replacement_added_path_pattern: str | None = None,
    replacement_action_type: str = "render_pre_task_review",
    replacement_evidence_type: str = "card_rendered",
    starter_pack_id: str = starter_policies.DEFAULT_PACK_ID,
    template_path: Path | None = None,
    template_ref: str | None = None,
    action_ref: str | None = None,
    requirement_ref: str | None = None,
    command_name: str | None = None,
    exit_code: int | None = None,
    verification_layer: str | None = None,
    completion_status: str | None = None,
    owner_agent: str = "codex",
    project_root: Path | None = None,
    user_phrase: str | None = None,
    trigger_mode: str | None = None,
    governance_path: str | None = None,
    host_semantic_intent: dict[str, Any] | None = None,
    turn_anchor: dict[str, Any] | None = None,
    private_turn_input_ref: dict[str, Any] | None = None,
    produced_evidence: list[dict[str, Any]] | None = None,
    enforce_semantic_intent_precondition: bool = False,
    work_routing_category: str | None = None,
    work_routing_summary: str | None = None,
    task_session_decision: str | None = None,
    task_session_defer_reason: str | None = None,
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
                next_actions=[
                    "retry with conversation_turn, status, task_start, task_continue, index, evidence, policy_distribution_review, policy_template_import_plan, verification, completion, handoff, or audit"
                ],
            )
        ]
        traces = []
        refusals = [refusal]
    elif event == "project_status":
        cards, traces, refusals = build_project_status_cards(project_root=project_root)
    elif event == "conversation_turn":
        cards, traces, refusals = build_conversation_turn_cards(
            trigger_mode=trigger_mode,
            user_phrase=user_phrase,
            task_title=task_title,
            summary=summary,
            project_root=project_root,
        )
    elif event == "configuration_review":
        cards, traces, refusals = build_configuration_review_cards(
            project_root=project_root,
        )
    elif event == "task_start":
        cards, traces, refusals = build_task_start_cards(
            project_root=project_root,
            task_title=task_title,
            session_id=session_id,
            owner_agent=owner_agent,
            task_session_decision=task_session_decision,
            task_session_defer_reason=task_session_defer_reason,
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
            policy_work_profile_lifecycle_events=policy_work_profile_lifecycle_events,
            policy_work_profile_policy_scopes=policy_work_profile_policy_scopes,
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
            replacement_trigger_event=replacement_trigger_event,
            replacement_work_profile_lifecycle_events=replacement_work_profile_lifecycle_events,
            replacement_work_profile_policy_scopes=replacement_work_profile_policy_scopes,
            replacement_task_type=replacement_task_type,
            replacement_jikuo_layer=replacement_jikuo_layer,
            replacement_changed_path_pattern=replacement_changed_path_pattern,
            replacement_added_path_pattern=replacement_added_path_pattern,
            replacement_action_type=replacement_action_type,
            replacement_evidence_type=replacement_evidence_type,
        )
    elif event == "policy_distribution_review":
        cards, traces, refusals = build_policy_distribution_review_cards(
            project_root=project_root,
            policy_ref=policy_ref,
            source_policy_path=distribution_source_policy_path,
            policy_query=distribution_policy_query,
            decision=distribution_decision,
            source_project_ref=distribution_source_project_ref,
            starter_pack_id=starter_pack_id,
            rationale=distribution_rationale,
        )
    elif event == "policy_template_publication_plan":
        cards, traces, refusals = build_policy_template_publication_plan_cards(
            project_root=project_root,
            policy_ref=policy_ref,
            source_policy_path=distribution_source_policy_path,
            policy_query=distribution_policy_query,
            decision=distribution_decision,
            source_project_ref=distribution_source_project_ref,
            starter_pack_id=starter_pack_id,
            rationale=distribution_rationale,
            target_dir=publication_target_dir,
            namespace=publication_namespace,
        )
    elif event == "starter_manifest_publication_plan":
        cards, traces, refusals = build_starter_manifest_publication_plan_cards(
            template_ref=template_ref,
            starter_pack_id=starter_pack_id,
        )
    elif event == "starter_policy_pack_init":
        cards, traces, refusals = build_starter_policy_pack_init_cards(
            project_root=project_root,
            starter_pack_id=starter_pack_id,
        )
    elif event == "policy_template_import_plan":
        cards, traces, refusals = build_policy_template_import_plan_cards(
            project_root=project_root,
            template_path=template_path,
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

    work_routing = build_work_routing_distinction(
        event=event,
        task_title=task_title,
        summary=summary,
        work_routing_category=work_routing_category,
        work_routing_summary=work_routing_summary,
    )
    work_profile_projection = work_profile.build_work_profile(
        raw_event=raw_event,
        normalized_event=event,
        user_phrase=user_phrase,
        task_title=task_title,
        summary=summary,
        task_type=task_type,
        jikuo_layer=jikuo_layer,
        changed_paths=changed_paths,
        added_paths=added_paths,
        host_semantic_intent=host_semantic_intent,
    )
    semantic_basis = (work_profile_projection.get("basis") or {}).get(
        "host_semantic_intent"
    ) or {}
    semantic_intent_evidence = (
        work_profile_projection.get("semantic_intent_evidence") or {}
    )
    turn_anchor_projection = (
        turn_anchor_model.normalize_turn_anchor(turn_anchor)
        if turn_anchor is not None
        else turn_anchor_model.turn_anchor_from_work_profile(work_profile_projection)
    )
    execution_envelope_projection = execution_envelope.build_execution_envelope(
        project_root=project_root,
        turn_anchor=turn_anchor_projection,
        host_semantic_intent=semantic_basis,
        lifecycle_event=event,
        lifecycle_state=execution_envelope.lifecycle_state_for_event(event),
        private_turn_input_ref=private_turn_input_ref,
    )
    traces.append(
        atom_trace(
            loop_step_id="DPL-06",
            atom_id="CAP-RUNTIME-TURN-ANCHOR-PROJECTION-01",
            mode="runtime-projection",
            status=str(turn_anchor_projection.get("status") or "missing"),
            summary=(
                "projected non-AI host turn anchor availability for runtime "
                "and Studio delivery-flow inspection"
            ),
        )
    )
    traces.append(
        atom_trace(
            loop_step_id="DPL-06",
            atom_id="CAP-EXECUTION-ENVELOPE-PROJECTION-01",
            mode="runtime-projection",
            status=str(execution_envelope_projection["lifecycle"]["state"]),
            summary=(
                "projected shared execution envelope from turn_anchor, host "
                "semantic intent evidence, and explicit lifecycle event"
            ),
        )
    )
    if enforce_semantic_intent_precondition:
        semantic_intent_evidence = semantic_intent_evidence_with_precondition_required(
            semantic_intent_evidence
        )
        work_profile_projection["semantic_intent_evidence"] = semantic_intent_evidence
    if semantic_basis.get("status") in {"provided", "heuristic_fallback"}:
        traces.append(
            atom_trace(
                loop_step_id="DPL-05",
                atom_id="CAP-HOST-SEMANTIC-INTENT-WORK-PROFILE-01",
                mode="no-write",
                status="ok",
                summary=(
                    "merged host semantic intent into the no-write work_profile "
                    "projection before policy distribution"
                ),
            )
        )
        if semantic_basis.get("evidence_source_kind") == "runtime_inherited":
            traces.append(
                atom_trace(
                    loop_step_id="DPL-06",
                    atom_id="CAP-RUNTIME-SEMANTIC-INTENT-INHERITANCE-01",
                    mode="runtime-projection",
                    status="ok",
                    summary=(
                        "inherited prompt-free host semantic intent evidence "
                        "from runtime state using a turn anchor or semantic ref"
                    ),
                )
            )
    if semantic_intent_evidence:
        traces.append(
            atom_trace(
                loop_step_id="DPL-05",
                atom_id="CAP-SEMANTIC-INTENT-CLASSIFICATION-EVIDENCE-01",
                mode="no-write",
                status=str(semantic_intent_evidence.get("status") or "unknown"),
                summary=(
                    "reported whether AI semantic intent classification was "
                    "required and supplied for this work profile"
                ),
            )
        )
    if enforce_semantic_intent_precondition and semantic_intent_precondition_unmet(
        semantic_intent_evidence
    ):
        cards.append(
            build_semantic_intent_precondition_card(
                work_profile_projection=work_profile_projection,
                semantic_intent_evidence=semantic_intent_evidence,
            )
        )
        traces.append(
            atom_trace(
                loop_step_id="DPL-05",
                atom_id="CAP-SEMANTIC-INTENT-PRECONDITION-01",
                mode="no-write",
                status="refused",
                summary=(
                    "returned a no-write precondition card requiring compact "
                    "host_semantic_intent before governed editing or "
                    "write-capable MCP entry points proceed"
                ),
            )
        )
        refusals.append("semantic_intent_precondition_unmet")
    if work_routing:
        traces.append(
            atom_trace(
                loop_step_id="DPL-05",
                atom_id="CAP-TASKMAP-INSIGHT-FOLLOWUP-EVIDENCE-01",
                mode="no-write",
                status="ok",
                summary=(
                    "classified current work as taskmap, insight, follow-up, "
                    "policy, deferred, or mixed structured evidence"
                ),
            )
        )
    if event == "task_start" and any(
        card.get("card_kind") in {"task_session_start_preview", "task_session_binding"}
        and card.get("status") != "refused"
        for card in cards
    ):
        task_resolution_status = "ok"
        if any(
            (card.get("task_session_resolution") or {}).get("status")
            == "needs_user_decision"
            for card in cards
        ):
            task_resolution_status = "review"
        elif any(
            (card.get("task_session_resolution") or {}).get("status")
            == "explicitly_deferred"
            for card in cards
        ):
            task_resolution_status = "explicitly_deferred"
        traces.append(
            atom_trace(
                loop_step_id="DPL-05",
                atom_id="CAP-TASK-SESSION-BINDING-EVIDENCE-01",
                mode="no-write",
                status=task_resolution_status,
                summary=(
                    "projected task-session binding handling as report-only "
                    "policy evidence"
                ),
            )
        )

    if event is not None:
        policy_eval_event = (
            normalize_event(policy_event or "")
            if event == "policy_evidence_check"
            else event
        )
        inline_produced_evidence = produced_policy_evidence_for(
            event=event,
            cards=cards,
            work_routing=work_routing,
            governance_path=governance_path,
            work_profile_projection=work_profile_projection,
        )
        inline_produced_evidence.extend(produced_evidence or [])
        artifact_assurance_report = build_runtime_artifact_assurance_report(
            event=event,
            project_root=project_root,
            changed_paths=changed_paths,
            added_paths=added_paths,
            produced_evidence=inline_produced_evidence,
        )
        if artifact_assurance_report:
            git_write_observation = (
                (artifact_assurance_report.get("runtime_projection") or {}).get(
                    "git_write_observation"
                )
                or {}
            )
            if git_write_observation:
                traces.append(
                    atom_trace(
                        loop_step_id="DPL-06",
                        atom_id="CAP-RUNTIME-WRITE-OBSERVATION-COMPLETION-REVIEW-01",
                        mode="runtime-observation",
                        status=str(git_write_observation.get("status") or "unknown"),
                        summary=(
                            "observed completion-review actual-write evidence through "
                            "the read-only git adapter"
                        ),
                    )
                )
            traces.append(
                atom_trace(
                    loop_step_id="DPL-06",
                    atom_id="CAP-STUDIO-ARTIFACT-ASSURANCE-RUNTIME-CARD-01",
                    mode="runtime-projection",
                    status=str(artifact_assurance_report.get("status") or "unknown"),
                    summary=(
                        "projected required/planned/actual document artifact "
                        "assurance into the runtime task card"
                    ),
                )
            )
        policy_context, policy_traces, policy_sections = build_policy_context(
            project_root=project_root,
            event=policy_eval_event or event,
            produced_evidence=inline_produced_evidence,
            task_session_id=session_id,
            task_type=task_type,
            jikuo_layer=jikuo_layer,
            changed_paths=changed_paths,
            added_paths=added_paths,
            work_profile_projection=work_profile_projection,
        )
        traces.extend(policy_traces)
    else:
        policy_context = build_policy_not_inspected_context()
        artifact_assurance_report = None
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
    if event is not None:
        policy_runtime_card, policy_runtime_trace = build_policy_runtime_status_card(
            event=event,
            task_type=task_type,
            jikuo_layer=jikuo_layer,
            policy_context=policy_context,
            triggered_policies=policy_sections["triggered_policies"],
            required_actions=policy_sections["required_actions"],
            condition_reports=policy_sections["condition_reports"],
            evidence_status=policy_sections["evidence_status"],
            missing_evidence_reports=policy_sections["missing_evidence_reports"],
            policy_feedback_options=policy_feedback_options,
        )
        cards.append(policy_runtime_card)
        traces.append(policy_runtime_trace)

    statuses = {str(card.get("status", "review")) for card in cards}
    status = "refused" if "refused" in statuses else "review" if "review" in statuses else "ok"
    atom_ids = [trace["atom_id"] for trace in traces]
    unsafe_atoms = sorted(set(atom_ids) - NO_WRITE_ATOMS - {"CAP-AGENT-FLOW-01"})
    conversation_router = next(
        (
            card.get("conversation_router")
            for card in cards
            if card.get("card_kind") == "conversation_turn_router"
        ),
        None,
    )
    guarded_apply_available = not refusals and event in {
        "policy_evolution_plan",
        "policy_evidence_record",
        "policy_feedback_record",
        "policy_template_import_plan",
        "starter_policy_pack_init",
        "task_start",
    }

    next_actions = next_actions_for(status=status, event=event)
    if semantic_intent_evidence.get("followup"):
        semantic_followup = (
            "provide compact host_semantic_intent and rerun JIKUO routing before "
            "claiming AI semantic routing for governed editing or progress work"
        )
        if semantic_followup not in next_actions:
            next_actions.insert(0, semantic_followup)

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
        "conversation_router": conversation_router,
        "work_profile": work_profile_projection,
        "semantic_intent_evidence": semantic_intent_evidence,
        "turn_anchor": turn_anchor_projection,
        "execution_envelope": execution_envelope_projection,
        "work_routing": work_routing,
        "artifact_assurance": artifact_assurance_report,
        "atom_trace": traces,
        "cards": cards,
        "approval_boundary": {
            "durable_write_approved": False,
            "guarded_apply_available": guarded_apply_available,
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
        "next_actions": next_actions,
    }


def next_actions_for(*, status: str, event: str | None) -> list[str]:
    if event is None:
        return ["retry with a supported event"]
    if status == "refused":
        return ["resolve refusal reasons before asking for a guarded action"]
    if event == "conversation_turn":
        return ["follow the conversation router obligations before continuing"]
    if event == "task_start":
        return ["review the task-start card in chat before approving any task-session write"]
    if event == "project_status":
        return ["continue with task_start when project state is ready"]
    if event == "policy_write_plan":
        return ["review policy write targets and non-effects before approving any future guarded writer"]
    if event == "policy_evolution_plan":
        return ["review policy evolution recommendation and any generated guarded command before approving a write"]
    if event == "policy_distribution_review":
        return ["review distribution category, source resolution, and non-effects before any template or starter publication"]
    if event == "policy_template_publication_plan":
        return ["review package template target, provenance, and generated guarded publication command before approving a write"]
    if event == "starter_manifest_publication_plan":
        return ["review starter manifest target and template provenance before approving a manifest update"]
    if event == "policy_template_import_plan":
        return ["review resolved bindings, write targets, and the generated guarded activation command before approving a write"]
    if event in {"evidence_review", "verification_review", "completion_review", "handoff"}:
        return ["review lifecycle preview before approving any task-session update"]
    return ["review this proposal in chat; no durable write has been performed"]


def build_apply_result(
    *,
    operation: str,
    project_root: Path | None,
    task_title: str | None,
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
    replacement_trigger_event: str = "task_start",
    replacement_work_profile_lifecycle_events: list[str] | None = None,
    replacement_work_profile_policy_scopes: list[str] | None = None,
    replacement_task_type: str | None = None,
    replacement_jikuo_layer: str | None = None,
    replacement_changed_path_pattern: str | None = None,
    replacement_added_path_pattern: str | None = None,
    replacement_action_type: str = "render_pre_task_review",
    replacement_evidence_type: str = "card_rendered",
    distribution_source_policy_path: Path | None = None,
    distribution_decision: str = "deferred",
    distribution_source_project_ref: str | None = None,
    distribution_rationale: str | None = None,
    publication_target_dir: Path | None = None,
    publication_namespace: str = policy_templates.DEFAULT_NAMESPACE,
    starter_pack_id: str = starter_policies.DEFAULT_PACK_ID,
    template_path: Path | None = None,
    template_ref: str | None = None,
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

    if operation == "task_session_start":
        target_result, exit_code = task_session.write_task_session(
            project_root=project_root,
            task_title=task_title or "",
            owner_agent=owner_agent,
            confirmed=confirmed,
            approval_phrase=approval_phrase,
        )
        write_performed = bool(target_result.get("write_performed"))
        traces.extend(
            [
                atom_trace(
                    loop_step_id="DPL-07",
                    atom_id="CAP-TASK-START-WRITE-01",
                    mode="guarded-write",
                    status=target_result.get("status", "unknown"),
                    summary="called guarded task-session start writer",
                ),
                atom_trace(
                    loop_step_id="DPL-07",
                    atom_id="CAP-AGENT-FLOW-APPLY-TASK-SESSION-START-01",
                    mode="guarded-write",
                    status=target_result.get("status", "unknown"),
                    summary="applied guarded task-session start through agent_flow.py",
                ),
            ]
        )
        approval_target = "JIKUO task-session file creation"
        approval_effect = "create one compact task-session sidecar record"
        approval_non_effects = [
            "does not update .jikuo/project_state.yaml latest_task_session_refs",
            "does not write policy files",
            "does not execute policy actions",
            "does not judge product output quality",
        ]
    elif operation == "task_session_evidence_update":
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
    elif operation == "starter_policy_pack_init":
        target_result, exit_code = starter_policies.initialize_starter_pack(
            project_root=project_root,
            pack_id=starter_pack_id,
            confirmed=confirmed,
            approval_phrase=approval_phrase,
        )
        write_performed = bool(target_result.get("write_performed"))
        traces.append(
            atom_trace(
                loop_step_id="DPL-07",
                atom_id="CAP-AGENT-FLOW-APPLY-STARTER-POLICY-PACK-01",
                mode="guarded-write",
                status=target_result.get("status", "unknown"),
                summary="applied guarded starter policy pack initialization through agent_flow.py",
            )
        )
        approval_target = "JIKUO starter policy pack initialization"
        approval_effect = f"initialize starter policy pack {starter_pack_id}"
        approval_non_effects = [
            "does not execute starter policy actions",
            "does not promote gates or blocking enforcement",
            "does not upload telemetry",
            "does not modify source template files",
        ]
    elif operation == "policy_template_activation":
        if template_path is None:
            target_result = {
                "schema": policy_templates.POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA,
                "schema_version": policy_templates.POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA,
                "status": "refused",
                "write_performed": False,
                "template_ref": None,
                "policy_ref": None,
                "written_paths": [],
                "refusal_reasons": [
                    "template_required_for_policy_template_activation"
                ],
                "warnings": [],
                "next_actions": [
                    "provide --template before retrying template activation"
                ],
            }
            exit_code = 2
        else:
            target_result, exit_code = policy_templates.activate_template_from_plan(
                template_path=template_path,
                project_root=project_root,
                confirmed=confirmed,
                approval_phrase=approval_phrase,
            )
        write_performed = bool(target_result.get("write_performed"))
        traces.extend(
            [
                atom_trace(
                    loop_step_id="DPL-07",
                    atom_id="CAP-POLICY-TEMPLATE-ACTIVATE-01",
                    mode="guarded-write",
                    status=target_result.get("status", "unknown"),
                    summary="called guarded policy-template activation writer",
                ),
                atom_trace(
                    loop_step_id="DPL-07",
                    atom_id="CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01",
                    mode="guarded-write",
                    status=target_result.get("status", "unknown"),
                    summary="applied guarded policy-template activation through agent_flow.py",
                ),
            ]
        )
        approval_target = "JIKUO policy template activation"
        approval_effect = (
            f"activate template {target_result.get('template_ref')} "
            f"as policy {target_result.get('policy_ref')}"
        )
        approval_non_effects = [
            "does not execute policy actions",
            "does not promote gates or blocking enforcement",
            "does not modify package template files",
            "does not write project_context bindings",
        ]
    elif operation == "policy_template_publication":
        if distribution_source_policy_path is None:
            target_result = {
                "schema": policy_templates.POLICY_TEMPLATE_PUBLICATION_RESULT_SCHEMA,
                "schema_version": policy_templates.POLICY_TEMPLATE_PUBLICATION_RESULT_SCHEMA,
                "status": "refused",
                "write_performed": False,
                "distribution_decision": distribution_decision,
                "source_policy_path": None,
                "target_template_path": None,
                "template_ref": None,
                "created_paths": [],
                "written_paths": [],
                "refusal_reasons": [
                    "source_policy_required_for_policy_template_publication"
                ],
                "warnings": [],
                "approval_record": None,
                "non_effects": [
                    "does not activate policies in user projects",
                    "does not update starter pack manifests",
                    "does not write package template files",
                ],
                "next_actions": [
                    "provide --distribution-source-policy before retrying template publication"
                ],
            }
            exit_code = 2
        else:
            target_result, exit_code = policy_templates.publish_template_from_distribution(
                source_policy_path=distribution_source_policy_path,
                decision=distribution_decision,
                target_dir=publication_target_dir,
                namespace=publication_namespace,
                source_project_ref=distribution_source_project_ref,
                starter_pack_id=starter_pack_id,
                rationale=distribution_rationale,
                confirmed=confirmed,
                approval_phrase=approval_phrase,
            )
        write_performed = bool(target_result.get("write_performed"))
        traces.extend(
            [
                atom_trace(
                    loop_step_id="DPL-07",
                    atom_id="CAP-POLICY-TEMPLATE-PUBLICATION-01",
                    mode="guarded-write",
                    status=target_result.get("status", "unknown"),
                    summary="called guarded package policy-template publication writer",
                ),
                atom_trace(
                    loop_step_id="DPL-07",
                    atom_id="CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-PUBLICATION-01",
                    mode="guarded-write",
                    status=target_result.get("status", "unknown"),
                    summary="applied guarded package policy-template publication through agent_flow.py",
                ),
            ]
        )
        approval_target = "JIKUO policy template publication"
        approval_effect = (
            f"publish package template {target_result.get('template_ref')}"
        )
        approval_non_effects = [
            "does not activate policies in user projects",
            "does not update starter pack manifests",
            "does not execute policy actions",
            "does not rewrite the source policy",
        ]
    elif operation == "starter_manifest_publication":
        if not template_ref:
            target_result = {
                "schema": starter_policies.STARTER_PACK_MANIFEST_PUBLICATION_RESULT_SCHEMA,
                "schema_version": starter_policies.STARTER_PACK_MANIFEST_PUBLICATION_RESULT_SCHEMA,
                "status": "refused",
                "write_performed": False,
                "pack_id": starter_pack_id,
                "manifest_path": None,
                "template_ref": None,
                "policy_id": None,
                "written_paths": [],
                "refusal_reasons": [
                    "template_ref_required_for_starter_manifest_publication"
                ],
                "warnings": [],
                "approval_record": None,
                "non_effects": [
                    "does not activate policies in user projects",
                    "does not initialize starter policies",
                    "does not create .jikuo/policies/",
                ],
                "next_actions": [
                    "provide --template-ref before retrying starter manifest publication"
                ],
            }
            exit_code = 2
        else:
            target_result, exit_code = starter_policies.publish_template_to_starter_manifest(
                template_ref=template_ref,
                pack_id=starter_pack_id,
                confirmed=confirmed,
                approval_phrase=approval_phrase,
            )
        write_performed = bool(target_result.get("write_performed"))
        traces.extend(
            [
                atom_trace(
                    loop_step_id="DPL-07",
                    atom_id="CAP-STARTER-MANIFEST-PUBLICATION-01",
                    mode="guarded-write",
                    status=target_result.get("status", "unknown"),
                    summary="called guarded starter-pack manifest publication writer",
                ),
                atom_trace(
                    loop_step_id="DPL-07",
                    atom_id="CAP-AGENT-FLOW-APPLY-STARTER-MANIFEST-PUBLICATION-01",
                    mode="guarded-write",
                    status=target_result.get("status", "unknown"),
                    summary="applied guarded starter-pack manifest publication through agent_flow.py",
                ),
            ]
        )
        approval_target = "JIKUO starter pack manifest publication"
        approval_effect = (
            f"add template ref {template_ref} to starter pack {starter_pack_id}"
        )
        approval_non_effects = [
            "does not activate policies in user projects",
            "does not initialize starter policies",
            "does not execute policy actions",
            "does not copy .jikuo/policies/approved files into starter packs",
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
            replacement_trigger_event=replacement_trigger_event,
            replacement_work_profile_lifecycle_events=replacement_work_profile_lifecycle_events,
            replacement_work_profile_policy_scopes=replacement_work_profile_policy_scopes,
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
                "unsupported_policy_evolution_writer_operation"
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
                replacement_trigger_event=replacement_trigger_event,
                replacement_work_profile_lifecycle_events=replacement_work_profile_lifecycle_events,
                replacement_work_profile_policy_scopes=replacement_work_profile_policy_scopes,
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
        if target.get("template_ref"):
            lines.append(f"- Template ref: `{target.get('template_ref')}`")
        if target.get("policy_ref"):
            lines.append(f"- Policy ref: `{target.get('policy_ref')}`")
        if target.get("proposal_ref"):
            lines.append(f"- Proposal ref: `{target.get('proposal_ref')}`")
        if target.get("decision_record_ref"):
            lines.append(
                f"- Decision record ref: `{target.get('decision_record_ref')}`"
            )
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


def add_runtime_visibility_projection(
    proposal: dict[str, Any],
    *,
    project_root: Path | None,
) -> dict[str, Any]:
    output = dict(proposal)
    output["atom_trace"] = list(proposal.get("atom_trace", []))
    output["write_effect"] = dict(proposal.get("write_effect", {}))
    prepared = runtime_visibility.prepare_agent_flow_snapshot(
        project_root=project_root,
        proposal=output,
    )
    report = dict(prepared)
    if prepared.get("status") != "skipped":
        report["status"] = "ok"
        report["write_performed"] = True
        report["reason"] = "runtime visibility snapshot written"
        output["atom_trace"].append(
            atom_trace(
                loop_step_id="DPL-06",
                atom_id="CAP-RUNTIME-VISIBILITY-CHANNEL-01",
                mode="runtime-projection",
                status="ok",
                summary="wrote latest JIKUO card and state summary to .jikuo/runtime",
            )
        )
    output["runtime_visibility"] = report
    output["client_display_links"] = runtime_visibility.build_client_display_links(report)
    output["execution_envelope"] = execution_envelope.with_runtime_visibility_refs(
        output.get("execution_envelope"),
        runtime_report=report,
    )
    output["write_effect"]["runtime_visibility_side_effect"] = {
        "write_performed": bool(report.get("write_performed")),
        "target": report.get("runtime_root_ref"),
        "last_card_ref": report.get("last_card_ref"),
        "state_summary_ref": report.get("state_summary_ref"),
        "history_ref": report.get("history_ref"),
        "client_display_links_status": output["client_display_links"].get("status"),
        "reason": report.get("reason"),
    }
    if prepared.get("status") != "skipped":
        runtime_visibility.persist_prepared_agent_flow_snapshot(
            proposal=output,
            card_markdown=render_markdown(output),
            prepared_report=prepared,
        )
    return output


def proposal_with_chat_ready_markdown(
    proposal: dict[str, Any],
    *,
    project_root: Path | None = None,
) -> dict[str, Any]:
    proposal_with_display = dict(proposal)
    proposal_with_display["display"] = build_display_directives()
    output = add_runtime_visibility_projection(
        proposal_with_display,
        project_root=project_root,
    )
    output["display"] = build_display_directives()
    output["chat_ready_markdown_schema"] = CHAT_READY_MARKDOWN_SCHEMA
    output["chat_ready_markdown"] = render_markdown(output)
    return output


def apply_result_with_chat_ready_markdown(report: dict[str, Any]) -> dict[str, Any]:
    output = dict(report)
    output["chat_ready_markdown_schema"] = CHAT_READY_MARKDOWN_SCHEMA
    output["chat_ready_markdown"] = render_apply_markdown(report)
    return output


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


def render_client_display_links(display_links: dict[str, Any]) -> list[str]:
    lines = ["## JIKUO Runtime Links", ""]
    links = display_links.get("links") or {}
    for key in ("last_card", "state_summary", "history_card"):
        item = links.get(key)
        if item:
            lines.append(f"- {item['label']}: {item['markdown']}")
    if not links:
        lines.append(f"- Status: `{display_links.get('status', 'unavailable')}`")
        if display_links.get("reason"):
            lines.append(f"- Reason: {display_links['reason']}")
    lines.append("")
    return lines


def render_observed_lifecycle_footer(display_links: dict[str, Any]) -> list[str]:
    lifecycle_links = display_links.get("lifecycle_card_links") or []
    if not lifecycle_links:
        return []
    lines = ["", "### Observed Lifecycle", ""]
    for item in lifecycle_links:
        lines.append(f"- `{item.get('lifecycle_event')}`: {item.get('markdown')}")
    return lines


def build_display_directives() -> dict[str, Any]:
    return {
        "schema": DISPLAY_DIRECTIVES_SCHEMA,
        "must_show_verbatim": ["chat_ready_markdown"],
        "card_priority_order": list(CARD_PRIORITY_ORDER),
        "may_summarize": ["structured_data"],
        "do_not_show": ["debug_trace"],
        "priority": "first_in_response",
        "reason": "policy_runtime_status is first-screen governance context when present",
    }


def cards_for_display(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = {card_kind: index for index, card_kind in enumerate(CARD_PRIORITY_ORDER)}
    fallback = len(CARD_PRIORITY_ORDER)
    return [
        card
        for _, card in sorted(
            enumerate(cards),
            key=lambda item: (
                priority.get(str(item[1].get("card_kind")), fallback),
                item[0],
            ),
        )
    ]


def render_cards(cards: list[dict[str, Any]]) -> list[str]:
    lines = ["## Cards", ""]
    for card in cards_for_display(cards):
        lines.append(render_card(card).rstrip())
        lines.append("")
    return lines


def render_work_routing(work_routing: dict[str, Any]) -> list[str]:
    lines = [
        "## Work Routing Evidence",
        "",
        f"- Category: `{work_routing.get('category')}`",
        f"- Routing id: `{work_routing.get('routing_id')}`",
        f"- Basis: `{work_routing.get('classification_basis')}`",
        f"- Summary: {work_routing.get('summary')}",
    ]
    bucket_labels = [
        ("taskmap_items", "Taskmap items"),
        ("insight_items", "Insight items"),
        ("follow_up_items", "Follow-up items"),
        ("policy_items", "Policy items"),
        ("deferred_items", "Deferred items"),
    ]
    for key, label in bucket_labels:
        values = work_routing.get(key) or []
        lines.append(f"- {label}: `{len(values)}`")
        lines.extend(f"  - {item}" for item in values)
    lines.append("")
    return lines


def render_work_profile(work_profile_projection: dict[str, Any]) -> list[str]:
    lines = [
        "## Work Profile",
        "",
        f"- Lifecycle event: `{work_profile_projection.get('lifecycle_event')}`",
        f"- Intent class: `{work_profile_projection.get('intent_class')}`",
        f"- Operation class: `{work_profile_projection.get('operation_class')}`",
        f"- Output class: `{work_profile_projection.get('output_class')}`",
        f"- Confidence: `{work_profile_projection.get('confidence')}`",
        "- Fallback expanded: "
        f"`{str(work_profile_projection.get('fallback_expanded', False)).lower()}`",
    ]
    scopes = work_profile_projection.get("policy_scopes") or []
    lines.append(f"- Policy scopes: `{', '.join(str(scope) for scope in scopes)}`")
    contract = work_profile_projection.get("policy_contract") or {}
    if contract:
        requested_outcome = contract.get("requested_outcome")
        if requested_outcome:
            lines.append(f"- Requested outcome: `{requested_outcome}`")
        process_contract = contract.get("process_contract") or []
        if process_contract:
            lines.append(
                "- Process contract: "
                f"`{'; '.join(str(item) for item in process_contract)}`"
            )
        execution_boundary = contract.get("execution_boundary")
        if execution_boundary:
            lines.append(f"- Execution boundary: `{execution_boundary}`")
        response_contract = contract.get("response_contract") or []
        if response_contract:
            lines.append(
                "- Response contract: "
                f"`{'; '.join(str(item) for item in response_contract)}`"
            )
    basis = work_profile_projection.get("basis") or {}
    semantic = basis.get("host_semantic_intent") or {}
    lines.append(f"- Semantic intent status: `{semantic.get('status', 'unavailable')}`")
    if semantic.get("provider"):
        lines.append(f"- Semantic provider: `{semantic.get('provider')}`")
    if semantic.get("evidence_source_kind"):
        lines.append(
            f"- Semantic evidence source: `{semantic.get('evidence_source_kind')}`"
        )
    if semantic.get("semantic_intent_ref"):
        lines.append(f"- Semantic intent ref: `{semantic.get('semantic_intent_ref')}`")
    inherited_from = semantic.get("inherited_from") or {}
    if isinstance(inherited_from, dict) and inherited_from.get("history_ref"):
        lines.append(f"- Semantic inherited from: `{inherited_from.get('history_ref')}`")
    semantic_evidence = work_profile_projection.get("semantic_intent_evidence") or {}
    if semantic_evidence:
        lines.extend(
            [
                "",
                "### Semantic Intent Evidence",
                "",
                f"- Required: `{str(semantic_evidence.get('required')).lower()}`",
                f"- Status: `{semantic_evidence.get('status')}`",
                f"- Provider: `{semantic_evidence.get('provider')}`",
                f"- Reason: `{semantic_evidence.get('reason')}`",
            ]
        )
        followup = semantic_evidence.get("followup")
        if followup:
            lines.append(f"- Next action: `{followup}`")
    constraints = semantic.get("constraints") or []
    if constraints:
        lines.append(
            f"- Semantic constraints: `{', '.join(str(item) for item in constraints)}`"
        )
    slices = semantic.get("intent_slices") or []
    if slices:
        lines.append(f"- Intent slices: `{len(slices)}`")
        for item in slices:
            if not isinstance(item, dict):
                continue
            slice_index = item.get("index") or "?"
            slice_id = item.get("id") or "intent"
            details = [
                f"id=`{slice_id}`",
            ]
            scopes = item.get("policy_scopes") or []
            if scopes:
                details.append(
                    "scopes=`" + ", ".join(str(scope) for scope in scopes) + "`"
                )
            user_expression = item.get("user_expression")
            if user_expression:
                details.append(f"user_expression=`{user_expression}`")
            requested_outcome = item.get("requested_outcome")
            if requested_outcome:
                details.append(f"requested_outcome=`{requested_outcome}`")
            execution_boundary = item.get("execution_boundary")
            if execution_boundary:
                details.append(f"execution_boundary=`{execution_boundary}`")
            response_contract = item.get("response_contract") or []
            if response_contract:
                details.append(
                    "response_contract=`"
                    + "; ".join(str(contract) for contract in response_contract)
                    + "`"
                )
            lines.append(f"  - `{slice_index}`: " + "; ".join(details))
    conflicts = basis.get("conflicts") or []
    if conflicts:
        lines.append(f"- Semantic/deterministic conflicts: `{len(conflicts)}`")
    signals = basis.get("deterministic_signals") or []
    lines.append(f"- Deterministic signals: `{len(signals)}`")
    lines.append("")
    return lines


def render_turn_anchor(turn_anchor_projection: dict[str, Any]) -> list[str]:
    if not turn_anchor_projection:
        return []
    lines = [
        "## Turn Anchor",
        "",
        f"- Status: `{turn_anchor_projection.get('status')}`",
    ]
    if turn_anchor_projection.get("anchor_id"):
        lines.append(f"- Anchor id: `{turn_anchor_projection.get('anchor_id')}`")
    if turn_anchor_projection.get("client_id"):
        lines.append(f"- Client: `{turn_anchor_projection.get('client_id')}`")
    if turn_anchor_projection.get("client_event"):
        lines.append(f"- Client event: `{turn_anchor_projection.get('client_event')}`")
    if turn_anchor_projection.get("session_id"):
        lines.append(f"- Session id: `{turn_anchor_projection.get('session_id')}`")
    if turn_anchor_projection.get("turn_id"):
        lines.append(f"- Turn id: `{turn_anchor_projection.get('turn_id')}`")
    if turn_anchor_projection.get("received_at_utc"):
        lines.append(f"- Received at: `{turn_anchor_projection.get('received_at_utc')}`")
    if turn_anchor_projection.get("prompt_digest_status"):
        lines.append(
            f"- Prompt digest: `{turn_anchor_projection.get('prompt_digest_status')}`"
        )
    if turn_anchor_projection.get("prompt_sha256"):
        digest = str(turn_anchor_projection.get("prompt_sha256"))
        lines.append(f"- Prompt sha256: `{digest}`")
    if turn_anchor_projection.get("identity_strength"):
        lines.append(
            f"- Identity strength: `{turn_anchor_projection.get('identity_strength')}`"
        )
    if turn_anchor_projection.get("gap_reason"):
        lines.append(f"- Gap reason: `{turn_anchor_projection.get('gap_reason')}`")
    lines.append(
        "- Privacy: `raw prompt is not included; raw transcript is not persisted`"
    )
    lines.append("")
    return lines


def render_execution_envelope(envelope: dict[str, Any]) -> list[str]:
    if not envelope:
        return []
    lifecycle = envelope.get("lifecycle") or {}
    privacy = envelope.get("privacy") or {}
    links = envelope.get("links") or {}
    private_ref = links.get("private_turn_input_ref") or {}
    runtime_refs = links.get("runtime_refs") or {}
    semantic = envelope.get("host_semantic_intent") or {}
    lines = [
        "## Execution Envelope",
        "",
        f"- Schema: `{envelope.get('schema')}`",
        f"- Envelope id: `{envelope.get('envelope_id')}`",
        f"- Lifecycle state: `{lifecycle.get('state')}`",
    ]
    if lifecycle.get("event"):
        lines.append(f"- Lifecycle event: `{lifecycle.get('event')}`")
    if envelope.get("session_id"):
        lines.append(f"- Session id: `{envelope.get('session_id')}`")
    if envelope.get("turn_id"):
        lines.append(f"- Turn id: `{envelope.get('turn_id')}`")
    lines.extend(
        [
            f"- Semantic intent status: `{semantic.get('status', 'unavailable')}`",
            f"- Semantic provider: `{semantic.get('provider', 'unavailable')}`",
            f"- Raw prompt storage: `{privacy.get('raw_prompt_storage', 'none')}`",
            (
                "- Raw prompt exposed in audit: "
                f"`{str(privacy.get('raw_prompt_exposed_in_audit', False)).lower()}`"
            ),
        ]
    )
    if private_ref:
        lines.append(
            f"- Private input record id: `{private_ref.get('record_id') or 'pending'}`"
        )
        lines.append(f"- Private input index ref: `{private_ref.get('index_ref')}`")
        lines.append(
            "- Private input write performed: "
            f"`{str(private_ref.get('write_performed', False)).lower()}`"
        )
    if runtime_refs:
        if runtime_refs.get("history_ref"):
            lines.append(f"- Runtime history ref: `{runtime_refs.get('history_ref')}`")
        if runtime_refs.get("state_summary_ref"):
            lines.append(
                f"- Runtime state summary ref: `{runtime_refs.get('state_summary_ref')}`"
            )
    lines.append("")
    return lines


def render_artifact_gap_lines(
    *,
    label: str,
    items: list[dict[str, Any]],
    limit: int = 8,
) -> list[str]:
    if not items:
        return [f"- {label}: `0`"]
    lines = [f"- {label}: `{len(items)}`"]
    for item in items[:limit]:
        path = item.get("path") or (item.get("expected") or {}).get("path")
        lines.append(f"  - `{item.get('gap_type')}` / `{path}`")
    if len(items) > limit:
        lines.append(f"  - ... {len(items) - limit} more")
    return lines


def render_artifact_assurance(report: dict[str, Any]) -> list[str]:
    gap_report = report.get("gap_report") or {}
    read = report.get("read_assurance") or {}
    write = report.get("write_assurance") or {}
    runtime_projection = report.get("runtime_projection") or {}
    lines = [
        "## Artifact Assurance",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Guarantee: `{report.get('guarantee')}`",
        f"- Runtime persistence: `{runtime_projection.get('persistence', 'runtime_card')}`",
        f"- Read assurance status: `{read.get('status')}`",
        f"- Write assurance status: `{write.get('status')}`",
        f"- Required reads: `{read.get('required_read_count', 0)}`",
        f"- Read evidence: `{read.get('read_evidence_count', 0)}`",
        f"- Completion-check documents: `{write.get('completion_check_candidate_count', 0)}`",
        f"- Completion-check documents not evaluated: `{len(write.get('completion_check_not_evaluated') or [])}`",
        f"- Required companion writes: `{write.get('required_companion_write_count', 0)}`",
        f"- Declared writes: `{write.get('declared_write_count', write.get('planned_write_count', 0))}`",
        f"- Applicable required writes: `{write.get('required_write_count', 0)}`",
        f"- Planned writes: `{write.get('planned_write_count', 0)}`",
        f"- Actual writes: `{write.get('actual_write_count', 0)}`",
        f"- Gap count: `{gap_report.get('gap_count', 0)}`",
    ]
    git_write_observation = runtime_projection.get("git_write_observation") or {}
    if git_write_observation:
        lines.extend(
            [
                f"- Actual write source: `{runtime_projection.get('actual_write_source')}`",
                f"- Declared actual writes: `{runtime_projection.get('declared_actual_write_count', 0)}`",
                f"- Git observed writes: `{git_write_observation.get('observed_actual_write_count', 0)}`",
                f"- Git observation status: `{git_write_observation.get('status')}`",
            ]
        )
    companion_projection = runtime_projection.get("companion_write_obligations") or {}
    if companion_projection:
        lines.extend(
            [
                f"- Companion projection status: `{companion_projection.get('status')}`",
                f"- Companion write triggers: `{companion_projection.get('trigger_count', 0)}`",
                f"- Companion ignored actual writes: `{companion_projection.get('ignored_item_count', 0)}`",
            ]
        )
    if report.get("reason"):
        lines.append(f"- Reason: {report['reason']}")
    lines.extend(
        render_artifact_gap_lines(
            label="Required reads without evidence",
            items=read.get("required_not_read") or [],
        )
    )
    lines.extend(
        render_artifact_gap_lines(
            label="Applicable required writes not planned",
            items=write.get("required_not_planned") or [],
        )
    )
    lines.extend(
        render_artifact_gap_lines(
            label="Applicable required writes not observed",
            items=write.get("required_not_written") or [],
        )
    )
    lines.extend(
        render_artifact_gap_lines(
            label="Required companion writes not observed",
            items=write.get("required_companion_not_observed") or [],
        )
    )
    if companion_projection:
        lines.extend(
            render_artifact_gap_lines(
                label="Companion ignored actual writes",
                items=companion_projection.get("ignored_items") or [],
            )
        )
    lines.extend(
        render_artifact_gap_lines(
            label="Planned writes not observed",
            items=write.get("planned_not_written") or [],
        )
    )
    lines.extend(
        render_artifact_gap_lines(
            label="Observed writes not planned",
            items=write.get("unplanned_written") or [],
        )
    )
    invalid_refs = gap_report.get("invalid_refs") or []
    if invalid_refs:
        lines.extend(render_artifact_gap_lines(label="Invalid refs", items=invalid_refs))
    non_effects = report.get("non_effects") or []
    if non_effects:
        lines.extend(["", "### Non-Effects", ""])
        lines.extend(f"- {item}" for item in non_effects)
    lines.append("")
    return lines


def render_markdown(proposal: dict[str, Any]) -> str:
    policy_context = proposal["policy_context"]
    lines = [
        "# JIKUO Agent Flow Proposal",
        "",
        f"- Status: `{proposal['status']}`",
        f"- Proposal id: `{proposal['proposal_id']}`",
        f"- Runner mode: `{proposal['runner_mode']}`",
        "- Writes performed: `false`",
        "- Guarded apply available: "
        f"`{str(proposal.get('approval_boundary', {}).get('guarded_apply_available', False)).lower()}`",
    ]
    runtime_report = proposal.get("runtime_visibility")
    if runtime_report:
        lines.extend(
            [
                "- Runtime visibility: "
                f"`{runtime_report.get('status')}` "
                f"(write_performed=`{str(runtime_report.get('write_performed', False)).lower()}`)",
                "",
                "## Runtime Visibility",
                "",
                f"- Last card: `{runtime_report.get('last_card_ref')}`",
                f"- State summary: `{runtime_report.get('state_summary_ref')}`",
            ]
        )
        if runtime_report.get("history_ref"):
            lines.append(f"- History card: `{runtime_report.get('history_ref')}`")
        if runtime_report.get("reason"):
            lines.append(f"- Reason: {runtime_report.get('reason')}")
    display_links = proposal.get("client_display_links")
    if display_links:
        lines.extend([""])
        lines.extend(render_client_display_links(display_links))
    work_profile_projection = proposal.get("work_profile")
    if work_profile_projection:
        lines.extend(render_work_profile(work_profile_projection))
    turn_anchor_projection = proposal.get("turn_anchor")
    if turn_anchor_projection:
        lines.extend(render_turn_anchor(turn_anchor_projection))
    execution_envelope_projection = proposal.get("execution_envelope")
    if execution_envelope_projection:
        lines.extend(render_execution_envelope(execution_envelope_projection))
    artifact_report = proposal.get("artifact_assurance")
    if artifact_report:
        lines.extend(render_artifact_assurance(artifact_report))
    work_routing = proposal.get("work_routing")
    if work_routing:
        lines.extend(render_work_routing(work_routing))
    lines.extend(render_cards(proposal["cards"]))
    lines.extend(
        [
            "",
            "## Trigger Decision",
            "",
        ]
    )
    lines.extend(
        [
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
    )
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
    lines.append("## Next Actions")
    lines.append("")
    lines.extend(f"- {item}" for item in proposal["next_actions"])
    if display_links:
        lines.extend(render_observed_lifecycle_footer(display_links))
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
    propose.add_argument(
        "--task-session-decision",
        choices=("defer",),
        default=None,
        help="Explicit no-write task-session resolution decision for task_start.",
    )
    propose.add_argument("--task-session-defer-reason", default=None)
    propose.add_argument("--policy-event", default=None)
    propose.add_argument("--task-type", default=None)
    propose.add_argument("--jikuo-layer", default=None)
    propose.add_argument("--changed-path", action="append", default=[])
    propose.add_argument("--added-path", action="append", default=[])
    propose.add_argument("--summary", default=None)
    propose.add_argument(
        "--work-routing-category",
        choices=sorted(WORK_ROUTING_CATEGORY_ALIASES),
        default=None,
    )
    propose.add_argument("--work-routing-summary", default=None)
    propose.add_argument("--evidence-kind", default=None)
    propose.add_argument("--evidence-ref", default=None)
    propose.add_argument(
        "--feedback-type",
        choices=sorted(POLICY_FEEDBACK_TYPES),
        default=None,
    )
    propose.add_argument("--policy-ref", default=None)
    propose.add_argument("--distribution-policy-ref", dest="policy_ref", default=None)
    propose.add_argument("--policy-title", default=None)
    propose.add_argument("--policy-source-ref", default=None)
    propose.add_argument("--policy-trigger-event", default="task_start")
    propose.add_argument("--policy-task-type", default=None)
    propose.add_argument("--policy-jikuo-layer", default=None)
    propose.add_argument("--policy-changed-path-pattern", default=None)
    propose.add_argument("--policy-added-path-pattern", default=None)
    propose.add_argument(
        "--policy-work-profile-lifecycle-event",
        action="append",
        default=[],
    )
    propose.add_argument(
        "--policy-work-profile-policy-scope",
        action="append",
        default=[],
    )
    propose.add_argument("--policy-action-type", default="render_pre_task_review")
    propose.add_argument("--policy-evidence-type", default="card_rendered")
    propose.add_argument("--distribution-source-policy", type=Path, default=None)
    propose.add_argument("--distribution-policy-query", default=None)
    propose.add_argument(
        "--distribution-decision",
        choices=sorted(policy_templates.POLICY_DISTRIBUTION_DECISIONS),
        default="deferred",
    )
    propose.add_argument("--distribution-rationale", default=None)
    propose.add_argument("--distribution-source-project-ref", default=None)
    propose.add_argument("--publication-target-dir", type=Path, default=None)
    propose.add_argument(
        "--publication-namespace",
        default=policy_templates.DEFAULT_NAMESPACE,
    )
    propose.add_argument(
        "--policy-evolution-operation",
        choices=sorted(policy_store.POLICY_EVOLUTION_OPERATIONS),
        default="refine_policy",
    )
    propose.add_argument("--replacement-policy-ref", default=None)
    propose.add_argument("--replacement-title", default=None)
    propose.add_argument("--replacement-trigger-event", default="task_start")
    propose.add_argument(
        "--replacement-work-profile-lifecycle-event",
        action="append",
        default=[],
    )
    propose.add_argument(
        "--replacement-work-profile-policy-scope",
        action="append",
        default=[],
    )
    propose.add_argument("--replacement-task-type", default=None)
    propose.add_argument("--replacement-jikuo-layer", default=None)
    propose.add_argument("--replacement-changed-path-pattern", default=None)
    propose.add_argument("--replacement-added-path-pattern", default=None)
    propose.add_argument("--replacement-action-type", default="render_pre_task_review")
    propose.add_argument("--replacement-evidence-type", default="card_rendered")
    propose.add_argument("--starter-pack-id", default=starter_policies.DEFAULT_PACK_ID)
    propose.add_argument("--template", type=Path, default=None)
    propose.add_argument("--template-ref", default=None)
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
    propose.add_argument(
        "--user-phrase-stdin",
        action="store_true",
        help="Read the user phrase from stdin instead of a command-line argument.",
    )
    propose.add_argument(
        "--host-semantic-intent-json",
        default=None,
        help="Compact host/classifier semantic intent JSON object; must not contain raw transcripts.",
    )
    propose.add_argument(
        "--inherit-semantic-intent",
        action="store_true",
        help=(
            "When no host semantic JSON is supplied, inherit prompt-free host "
            "semantic evidence from runtime state using --turn-anchor-json or "
            "--semantic-intent-ref."
        ),
    )
    propose.add_argument(
        "--semantic-intent-ref",
        default=None,
        help=(
            "Runtime semantic evidence reference to inherit, such as latest, "
            "anchor:<turn_anchor_id>, a proposal id, or a runtime history ref."
        ),
    )
    propose.add_argument(
        "--turn-anchor-json",
        default=None,
        help="Non-AI host turn anchor JSON object; must not contain raw prompt text.",
    )
    propose.add_argument(
        "--private-turn-input-ref-json",
        default=None,
        help="Redacted private turn input index ref; must not contain raw prompt text.",
    )
    propose.add_argument("--trigger-mode", choices=sorted(TRIGGER_MODES), default=None)
    propose.add_argument(
        "--governance-path",
        choices=sorted(GOVERNANCE_PATHS),
        default=None,
        help=(
            "Explicitly label this task_start as a JIKUO MCP path or a core debug "
            "path for self-bootstrap evidence matching."
        ),
    )
    propose.add_argument("--format", choices=("markdown", "json"), default="markdown")

    apply = subparsers.add_parser("apply")
    apply.add_argument("--operation", choices=sorted(APPLY_OPERATIONS), required=True)
    apply.add_argument("--task-title", default=None)
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
    apply.add_argument("--replacement-trigger-event", default="task_start")
    apply.add_argument(
        "--replacement-work-profile-lifecycle-event",
        action="append",
        default=[],
    )
    apply.add_argument(
        "--replacement-work-profile-policy-scope",
        action="append",
        default=[],
    )
    apply.add_argument("--replacement-task-type", default=None)
    apply.add_argument("--replacement-jikuo-layer", default=None)
    apply.add_argument("--replacement-changed-path-pattern", default=None)
    apply.add_argument("--replacement-added-path-pattern", default=None)
    apply.add_argument("--replacement-action-type", default="render_pre_task_review")
    apply.add_argument("--replacement-evidence-type", default="card_rendered")
    apply.add_argument("--distribution-source-policy", type=Path, default=None)
    apply.add_argument(
        "--distribution-decision",
        choices=sorted(policy_templates.POLICY_DISTRIBUTION_DECISIONS),
        default="deferred",
    )
    apply.add_argument("--distribution-source-project-ref", default=None)
    apply.add_argument("--distribution-rationale", default=None)
    apply.add_argument("--publication-target-dir", type=Path, default=None)
    apply.add_argument(
        "--publication-namespace",
        default=policy_templates.DEFAULT_NAMESPACE,
    )
    apply.add_argument("--starter-pack-id", default=starter_policies.DEFAULT_PACK_ID)
    apply.add_argument("--template", type=Path, default=None)
    apply.add_argument("--template-ref", default=None)
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
            task_title=args.task_title,
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
            replacement_trigger_event=args.replacement_trigger_event,
            replacement_work_profile_lifecycle_events=args.replacement_work_profile_lifecycle_event,
            replacement_work_profile_policy_scopes=args.replacement_work_profile_policy_scope,
            replacement_task_type=args.replacement_task_type,
            replacement_jikuo_layer=args.replacement_jikuo_layer,
            replacement_changed_path_pattern=args.replacement_changed_path_pattern,
            replacement_added_path_pattern=args.replacement_added_path_pattern,
            replacement_action_type=args.replacement_action_type,
            replacement_evidence_type=args.replacement_evidence_type,
            distribution_source_policy_path=args.distribution_source_policy,
            distribution_decision=args.distribution_decision,
            distribution_source_project_ref=args.distribution_source_project_ref,
            distribution_rationale=args.distribution_rationale,
            publication_target_dir=args.publication_target_dir,
            publication_namespace=args.publication_namespace,
            starter_pack_id=args.starter_pack_id,
            template_path=args.template,
            template_ref=args.template_ref,
            confirmed=args.confirm_apply,
            approval_phrase=args.approval_phrase,
        )
        if args.format == "json":
            print(
                json.dumps(
                    apply_result_with_chat_ready_markdown(report),
                    ensure_ascii=False,
                    indent=2,
                )
            )
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

    user_phrase = args.user_phrase
    if args.user_phrase_stdin:
        if user_phrase:
            parser.error("--user-phrase and --user-phrase-stdin are mutually exclusive")
        user_phrase = sys.stdin.read().rstrip("\r\n")

    host_semantic_intent: dict[str, Any] | None = None
    if args.host_semantic_intent_json:
        try:
            decoded_semantic_intent = json.loads(args.host_semantic_intent_json)
        except json.JSONDecodeError as exc:
            parser.error(f"--host-semantic-intent-json must be valid JSON: {exc}")
        if not isinstance(decoded_semantic_intent, dict):
            parser.error("--host-semantic-intent-json must decode to an object")
        host_semantic_intent = decoded_semantic_intent

    turn_anchor_input: dict[str, Any] | None = None
    if args.turn_anchor_json:
        try:
            decoded_turn_anchor = json.loads(args.turn_anchor_json)
        except json.JSONDecodeError as exc:
            parser.error(f"--turn-anchor-json must be valid JSON: {exc}")
        if not isinstance(decoded_turn_anchor, dict):
            parser.error("--turn-anchor-json must decode to an object")
        turn_anchor_input = decoded_turn_anchor

    private_turn_input_ref: dict[str, Any] | None = None
    if args.private_turn_input_ref_json:
        try:
            decoded_private_ref = json.loads(args.private_turn_input_ref_json)
        except json.JSONDecodeError as exc:
            parser.error(f"--private-turn-input-ref-json must be valid JSON: {exc}")
        if not isinstance(decoded_private_ref, dict):
            parser.error("--private-turn-input-ref-json must decode to an object")
        private_turn_input_ref = decoded_private_ref

    if host_semantic_intent is None and (
        args.inherit_semantic_intent or args.semantic_intent_ref
    ):
        host_semantic_intent = runtime_visibility.inherit_host_semantic_intent(
            project_root=args.project_root,
            turn_anchor_input=turn_anchor_input,
            semantic_intent_ref=args.semantic_intent_ref,
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
        policy_work_profile_lifecycle_events=args.policy_work_profile_lifecycle_event,
        policy_work_profile_policy_scopes=args.policy_work_profile_policy_scope,
        policy_action_type=args.policy_action_type,
        policy_evidence_type=args.policy_evidence_type,
        distribution_source_policy_path=args.distribution_source_policy,
        distribution_policy_query=args.distribution_policy_query,
        distribution_decision=args.distribution_decision,
        distribution_rationale=args.distribution_rationale,
        distribution_source_project_ref=args.distribution_source_project_ref,
        publication_target_dir=args.publication_target_dir,
        publication_namespace=args.publication_namespace,
        policy_evolution_operation=args.policy_evolution_operation,
        replacement_policy_ref=args.replacement_policy_ref,
        replacement_title=args.replacement_title,
        replacement_trigger_event=args.replacement_trigger_event,
        replacement_work_profile_lifecycle_events=args.replacement_work_profile_lifecycle_event,
        replacement_work_profile_policy_scopes=args.replacement_work_profile_policy_scope,
        replacement_task_type=args.replacement_task_type,
        replacement_jikuo_layer=args.replacement_jikuo_layer,
        replacement_changed_path_pattern=args.replacement_changed_path_pattern,
        replacement_added_path_pattern=args.replacement_added_path_pattern,
        replacement_action_type=args.replacement_action_type,
        replacement_evidence_type=args.replacement_evidence_type,
        starter_pack_id=args.starter_pack_id,
        template_path=args.template,
        template_ref=args.template_ref,
        action_ref=args.action_ref,
        requirement_ref=args.requirement_ref,
        command_name=args.command_name,
        exit_code=args.exit_code,
        verification_layer=args.verification_layer,
        completion_status=args.completion_status,
        owner_agent=args.owner_agent,
        project_root=args.project_root,
        user_phrase=user_phrase,
        trigger_mode=args.trigger_mode,
        governance_path=args.governance_path,
        host_semantic_intent=host_semantic_intent,
        turn_anchor=turn_anchor_input,
        private_turn_input_ref=private_turn_input_ref,
        produced_evidence=produced_evidence,
        work_routing_category=args.work_routing_category,
        work_routing_summary=args.work_routing_summary,
        task_session_decision=args.task_session_decision,
        task_session_defer_reason=args.task_session_defer_reason,
    )
    proposal_output = proposal_with_chat_ready_markdown(
        proposal,
        project_root=args.project_root,
    )
    if args.format == "json":
        print(
            json.dumps(
                proposal_output,
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(proposal_output["chat_ready_markdown"])
    return 0 if proposal["status"] != "refused" else 2


if __name__ == "__main__":
    sys.exit(main())
