# SPRINT_050_WO-PER-JIKUO-CORE-09: Policy Trigger Evaluator MVP

> **Date**: 2026-05-12
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / implementation slice
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: desktop_operating_skeleton; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: implements only report-only lifecycle trigger matching for active project policies; does not execute actions, check evidence, write policy/task-session state, or promote gates
> **Deferred kernel backlog refs**: `CAP-POLICY-EVIDENCE-CHECKER-01`; `CAP-POLICY-STORE-WRITE-01`; `CAP-POLICY-CONDITION-EVALUATOR-01`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`
> **Preceded by**: CORE-05 configurable rule trigger policy; CORE-06 rule action/evidence model; CORE-07 policy store/configuration flow; CORE-08 read-only policy store inspection.
> **Current slice**: `policy_store.py evaluate --event <event>` evaluates active policy `task_lifecycle_event` triggers by exact event match and projects `triggered_policies` / `required_actions`; `agent_flow.py propose` includes the results in same-chat proposal output.
> **User scenario**: A Codex / Claude desktop APP user starts a governed task and needs JIKUO to show which approved project policies triggered before any action execution or evidence checking happens.
> **Runtime chain**: desktop event -> `agent_flow.py propose` -> read-only policy-store inspection -> report-only lifecycle trigger evaluation -> triggered-policy/action projection -> baseline cards -> same-chat user review.
> **Canonical source**: `jikuo_configurable_rule_trigger_policy.md`, `jikuo_rule_action_evidence_model.md`, `jikuo_policy_store_configuration_flow.md`, `jikuo_policy_aware_agent_flow_contract.md`, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.policy_trigger_eval_report.v0`; `jikuo.agent_flow_proposal.v1.triggered_policies`; `jikuo.agent_flow_proposal.v1.required_actions`.
> **Consumer projection**: Codex / Claude desktop APP chat cards, future MCP response, future Skill / Plugin wrapper, future frontend run-control and audit surfaces.
> **Lifecycle**: read-only store status adapter -> trigger evaluator MVP -> user review -> later evidence checker / condition evaluator / write adapter implementation.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

This slice is the first point where JIKUO moves from "rules are visible" to "approved rules can trigger deterministically."

Visible business value:

- active policies can be evaluated against a task lifecycle event
- triggered policies are shown in the desktop APP proposal
- required actions are listed before execution
- the user can see that no action has been executed and no evidence has been checked yet

Important boundary:

- trigger evaluation is tool-backed exact matching, not AI semantic inference
- only `task_lifecycle_event` exact `event` matching is implemented
- action execution and evidence checking remain later slices
- no durable write is performed

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- extend `tools/jikuo/policy_store.py`
- extend `tools/jikuo/policy_store_tests.py`
- extend `tools/jikuo/agent_flow.py`
- extend `tools/jikuo/agent_flow_tests.py`
- evaluate active policy `task_lifecycle_event` triggers by exact event match
- project triggered policy refs
- project required action refs
- render triggered policies and required actions in Markdown proposal output
- update task map, execution mounts, loop composition, Sprint index, and policy-aware contracts

This slice is not allowed to:

- infer natural-language intent
- evaluate arbitrary policy conditions
- execute policy actions
- check or persist evidence
- produce missing-evidence reports
- create `.jikuo/policies/`
- write approved policies or proposals
- create `.jikuo/task_sessions/`
- implement guarded `agent_flow.py apply`
- install Skill / MCP / Plugin / frontend / gate behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- consuming active approved policy files from CORE-07
- using CORE-05 `task_lifecycle_event` trigger vocabulary
- projecting CORE-06-style required actions without executing them
- keeping `triggered_policies` distinct from `required_actions`
- leaving `evidence_status` and `missing_evidence_reports` empty until evidence-checker work
- preserving report-only and no-write behavior

---

## 4. Deferred Kernel Backlog

Still deferred:

- `CAP-POLICY-CONDITION-EVALUATOR-01`: non-lifecycle conditions such as path matches, document mounts, work-order metadata, and checker results
- `CAP-POLICY-EVIDENCE-CHECKER-01`: required evidence satisfaction and missing-evidence reports
- `CAP-POLICY-STORE-WRITE-01`: guarded policy proposal / approved-policy write mode
- policy proposal card renderer
- task-session policy snapshot persistence
- Skill / MCP / Plugin / frontend / gate adapters

---

## 5. Scope

Implemented:

- `policy_store.py evaluate --event <event>`
- `jikuo.policy_trigger_eval_report.v0`
- exact `task_lifecycle_event` matching
- required-action projection
- `agent_flow.py` integration
- `CAP-POLICY-TRIGGER-EVALUATE-01` atom trace
- Markdown sections for triggered policies and required actions
- tests for matching and non-matching lifecycle events

---

## 6. Out Of Scope

Not implemented:

- condition evaluation beyond lifecycle event exact match
- action execution
- evidence checking
- evidence persistence
- missing-evidence report generation
- policy writes
- guarded `apply`
- MCP / Skill / Plugin / frontend packaging
- gates or blocking enforcement

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-08_read_only_policy_store_inspection.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `policy_store_tests.py` verifies matching and non-matching lifecycle trigger evaluation.

`integration`:

- limited; `agent_flow_tests.py` verifies `agent_flow.py propose` projects triggered policies and required actions without writing.

`workflow / orchestration`:

- required; Markdown proposal must show policy evaluation status, triggered policies, required actions, and no-write boundaries.

`semantic regression`:

- N/A because this slice governs process policy triggering, not product-output content or narrative runtime behavior.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify root `.jikuo/policies/`, root `.jikuo/task_sessions/`, and fixture task sessions are not created.

`human governance review`:

- required; user reviews whether exact lifecycle trigger matching is understandable and honest before evidence checker or gates.

---

## 9. Delivery Criteria

- `policy_store.py evaluate --event task_start` returns `jikuo.policy_trigger_eval_report.v0`.
- Active fixture policy with `task_lifecycle_event: task_start` reports one triggered policy.
- Non-matching lifecycle event reports no triggered policies.
- Required actions are projected but not executed.
- `agent_flow.py propose` reports `policy_eval_status: evaluated` only when active policies are evaluated.
- `agent_flow.py propose` renders triggered policies and required actions in Markdown.
- `CAP-POLICY-TRIGGER-EVALUATE-01` appears in atom trace.
- Evidence arrays remain empty until evidence-checker work.
- No durable write is performed.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts that trigger matching is exact lifecycle event matching, not AI inference
- tests pass
- checker smoke passes
- no root `.jikuo/policies/` or `.jikuo/task_sessions/` directory is created
- no fixture task-session directory is created
- evidence checker, condition evaluator, policy write adapter, Skill, MCP, Plugin, frontend, and gate work remain explicitly deferred

Do not proceed to evidence checking, condition evaluation, policy write mode, guarded `agent_flow.py apply`, Skill, MCP, Plugin, frontend, or gate work until this trigger evaluator MVP is accepted or revised.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
```

Result:

- `policy_store_tests.py`: passed; 7 tests
- `agent_flow_tests.py`: passed; 4 tests

```powershell
python -B tools/jikuo/policy_store.py evaluate --event task_start --project-root tools/jikuo/fixtures/policy_store_active_project --format json
python -B tools/jikuo/agent_flow.py propose --event task_start --task-title "Policy Trigger Probe" --project-root tools/jikuo/fixtures/policy_store_active_project --format markdown
```

Result:

- policy trigger eval returned `jikuo.policy_trigger_eval_report.v0`
- `policy_eval_status: evaluated`
- `triggered_policies: 1`
- `required_actions: 1`
- proposal rendered `Triggered Policies` and `Required Actions`
- proposal still reported `Writes performed: false`

```powershell
Test-Path -Path .jikuo\policies
Test-Path -Path .jikuo\task_sessions
Test-Path -Path tools\jikuo\fixtures\policy_store_active_project\.jikuo\task_sessions
```

Result:

- all returned `False`

Additional checker and adjacent helper verification should be recorded before final acceptance.

---

## 12. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- policy condition evaluator
- policy execution evidence checker
- policy proposal / approved-policy write mode
- policy proposal renderer
- guarded `agent_flow.py apply`
- Skill / MCP / Plugin packaging
- frontend implementation
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
