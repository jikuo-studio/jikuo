# SPRINT_050_WO-PER-JIKUO-POLTRIG-03: Policy Scope Evaluator Consumption

> **Status**: Implemented and verified; evaluator consumes lifecycle_events and policy_scopes only.
> **Date**: 2026-05-17
> **JIKUO layer**: policy governance / trigger routing.
> **Business meaning**: JIKUO policy triggering must stop relying on under-specified task context that can leave active policies untriggered for real governed work. The evaluator should eventually consume declared work-profile scope only after the dead-zone evidence, report-only projections, and task-start boundaries are mounted together.

---

## 1. Originating Problem

Policy-trigger work began because a real downstream project could call JIKUO and
show an active policy store while repeated policy runtime checks still produced
zero triggered policies. That is a product failure, not only an implementation
gap: users can believe governance is active when the trigger context is missing
or mismatched.

`POLTRIG-01A`, `POLTRIG-01B`, and `POLTRIG-02` intentionally stopped short of
changing evaluator behavior. They made the relevant facts visible first:

- `work_profile` proposal projection;
- lightweight `task_start_processing` separated from durable
  `task_session_start`;
- report-only `applies_to_work_profile` declarations on policies.

## 2. Required Context Bundle

Use `MOUNT-POLICY-TRIGGER-DEAD-ZONE-REPAIR` before implementing or reviewing
this slice.

Required source documents:

- `docs/governance/jikuo_policy_governance_authority.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-20_policy_dead_zone_detection.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-21_governed_slice_task_session_resolution.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md`

## 3. Originating Evidence

Primary evidence:

- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-20_policy_dead_zone_detection.md`
  section `7. Initial Evidence`.

That evidence records NarrativeSystem runtime history where policy runtime cards
showed active policies and repeated zero-trigger results because the event,
activation state, or supplied task context did not match active policy
conditions. A manual check with matching task context proved the engine could
trigger, so the missing layer was trigger-context modeling and routing, not the
existence of policy files.

## 4. Intended Direction

`CAP-POLICY-TRIGGER-EVALUATE-01` and
`CAP-POLICY-CONDITION-EVALUATOR-01` should eventually use declared work-profile
scope as evaluator input, with exact condition checks preserved as additional
filters.

This slice starts from the report-only declaration produced by
`CAP-POLICY-WORK-PROFILE-APPLICABILITY-01` and the dead-zone visibility from
`CAP-POLICY-DEAD-ZONE-DETECTION-01`.

Accepted POLTRIG-03 evaluator boundary:

- `work_profile.lifecycle_event` and `work_profile.policy_scopes` become hard
  inputs when a policy declares `applies_to_work_profile`.
- Exact event triggers still gate the policy first.
- Exact conditions remain additional filters after work-profile applicability
  matches.
- Missing `applies_to_work_profile` remains a legacy-compatible policy path.
- `intent_class`, `operation_class`, and `output_class` remain explanatory in
  this slice and must not block or trigger policies yet.

Approved policy metadata backfill:

- active policy backfill is limited to `applies_to_work_profile`;
- no `triggers`, `conditions`, `required_actions`, `required_evidence`,
  `enforcement`, status, version, supersession, or deprecation fields are changed;
- the governing audit record is this POLTRIG-03 work order plus the git commit,
  following the scope metadata migration rule in
  `docs/governance/jikuo_policy_governance_authority.md`.

## 5. Non-Goals

- Do not make `intent_class`, `operation_class`, or `output_class` hard
  evaluator gates in this slice.
- Do not make `task_start_processing` satisfy durable task-session binding
  evidence.
- Do not change approved policy actions, evidence, enforcement level, or exact
  conditions in this slice. Approved policy edits are limited to explicit
  `applies_to_work_profile` metadata backfill requested for POLTRIG-03
  compatibility.
- Do not add new task sequencing, open-item facts, capability metadata, or
  registry authority to the legacy task map.
- Do not implement DATA event-ledger persistence in this slice.

## 6. Stop Boundary

Before broadening evaluator behavior beyond the accepted POLTRIG-03 boundary,
state the proposed evaluator behavior in terms of:

- which `work_profile` fields become inputs;
- how `applies_to_work_profile` is matched;
- how exact conditions remain additional filters;
- how fallback expansion prevents under-specified work from silently falling
  into a zero-trigger state;
- what remains report-only.

Implementation of the accepted POLTRIG-03 boundary may proceed; broader behavior
changes require a new review.
