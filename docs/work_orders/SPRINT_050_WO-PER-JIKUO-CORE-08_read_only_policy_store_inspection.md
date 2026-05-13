# SPRINT_050_WO-PER-JIKUO-CORE-08: Read-Only Policy Store Inspection

> **Date**: 2026-05-11
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / implementation slice
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: desktop_operating_skeleton; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: implements read-only policy-store discovery/status projection from CORE-07 without writing policy files, activating proposals, evaluating triggers, executing actions, checking evidence, or promoting gates
> **Deferred kernel backlog refs**: `CAP-POLICY-STORE-WRITE-01`; `CAP-POLICY-TRIGGER-EVALUATOR-01`; `CAP-POLICY-EVIDENCE-CHECKER-01`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`
> **Preceded by**: CORE-05 configurable rule trigger policy; CORE-06 rule action/evidence model; CORE-07 policy store/configuration flow; AGENT-07 policy-aware projection contract; AGENT-08 fallback projection.
> **Current slice**: `policy_store.py status` inspects `.jikuo/policies/manifest.yaml` and approved refs in report-only mode; `agent_flow.py propose` uses the status in `policy_context` while keeping `policy_eval_status: not_evaluated`.
> **User scenario**: A Codex / Claude desktop APP user invokes JIKUO and needs to know whether project-level rule configuration exists and is readable, without leaving chat or trusting agent memory.
> **Runtime chain**: desktop event -> `agent_flow.py propose` -> no-write policy-store inspection -> policy context projection -> baseline proposal cards -> same-chat user review.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`, `jikuo_policy_aware_agent_flow_contract.md`, CORE-05 / CORE-06 contracts, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.policy_store_status.v0`; `jikuo.agent_flow_proposal.v1.policy_context`.
> **Consumer projection**: Codex / Claude desktop APP chat cards, future MCP response, future Skill / Plugin wrapper, future frontend run-control and audit surfaces.
> **Lifecycle**: policy store contract -> read-only status adapter -> user review -> later trigger evaluator / evidence checker / write adapter implementation.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

This slice turns "user-configured rules may exist someday" into an inspectable project state.

Visible business value:

- the desktop proposal can now distinguish missing, initialized, stale, conflict, and active policy-store states
- users can see whether a project has approved policy configuration without opening raw YAML
- agents can stop pretending missing policy infrastructure is the same as "no rules apply"
- later trigger evaluation and evidence checking get a stable read-only input

Important boundary:

- this is not policy execution
- this is not policy configuration write mode
- this is not evidence checking
- this is not a gate

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- add `tools/jikuo/policy_store.py`
- add `tools/jikuo/policy_store_tests.py`
- add policy-store fixtures
- inspect `.jikuo/policies/manifest.yaml`
- inspect approved policy refs listed by the manifest
- report `missing`, `initialized`, `stale`, `conflict`, or `active`
- update `agent_flow.py propose` to project the read-only status
- update task map, execution mounts, loop composition, Sprint index, and kernel backlog notes

This slice is not allowed to:

- create `.jikuo/policies/`
- create or update `manifest.yaml`
- write approved policies or proposals
- import AGENTS / CLAUDE prose into active policies
- evaluate policy triggers
- execute required actions
- check policy evidence
- persist evidence
- create `.jikuo/task_sessions/`
- implement guarded `agent_flow.py apply`
- install Skill / MCP / Plugin / frontend / gate behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- consuming CORE-07 store layout without redefining proposal/write semantics
- treating pending proposals as inactive
- returning compact approved policy refs instead of copying full policy bodies into proposal cards
- preserving `policy_eval_status: not_evaluated`
- keeping active policy lookup separate from trigger evaluation
- reporting stale/conflict states as review needs, not success

---

## 4. Deferred Kernel Backlog

Still deferred:

- `CAP-POLICY-STORE-WRITE-01`: guarded policy proposal / approved-policy write mode
- `CAP-POLICY-TRIGGER-EVALUATOR-01`: evaluate lifecycle/path/document triggers
- `CAP-POLICY-EVIDENCE-CHECKER-01`: check required evidence for triggered actions
- policy proposal card renderer
- task-session policy snapshot persistence
- Skill / MCP / Plugin / frontend / gate adapters

---

## 5. Scope

Implemented:

- `tools/jikuo/policy_store.py`
- `tools/jikuo/policy_store_tests.py`
- policy-store fixtures for missing, initialized, active, stale, and conflict states
- `agent_flow.py` policy context integration
- `CAP-POLICY-STORE-STATUS-01` atom trace
- task-session source-ref path cleanup for moved JIKUO work orders
- planning/index updates for the new read-only capability

---

## 6. Out Of Scope

Not implemented:

- policy writes
- policy proposal extraction
- policy trigger evaluation
- policy action execution
- policy evidence checking
- policy evidence persistence
- MCP / Skill / Plugin / frontend packaging
- gates or blocking enforcement

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `policy_store_tests.py` verifies missing, initialized, active, stale, and conflict policy-store states.

`integration`:

- limited; `agent_flow_tests.py` verifies `agent_flow.py propose` consumes policy-store status without evaluating policies or writing sidecars.

`workflow / orchestration`:

- required; proposal output must show policy-store status in the desktop loop trace and `policy_context`.

`semantic regression`:

- N/A because this slice governs process state, not product-output content or narrative runtime behavior.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify root `.jikuo/policies/` and `.jikuo/task_sessions/` are not created.

`human governance review`:

- required; user reviews whether this read-only adapter is a safe bridge from configuration contracts toward real policy execution.

---

## 9. Delivery Criteria

- `policy_store.py status` exists and is read-only.
- Missing policy store reports `missing` without creating directories.
- Empty manifest reports `initialized`.
- Valid approved refs report `active`.
- Missing approved refs report `stale`.
- Duplicate active policy ids report `conflict`.
- `agent_flow.py propose` includes policy-store status in `policy_context`.
- `agent_flow.py propose` still reports `policy_eval_status: not_evaluated`.
- `triggered_policies`, `required_actions`, `evidence_status`, and `missing_evidence_reports` remain empty until later evaluator/checker slices.
- `CAP-POLICY-STORE-STATUS-01` appears in atom trace for supported events.
- Task map, execution mounts, loop composition, Sprint index, and kernel backlog are updated.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts that policy-store inspection is not policy execution
- tests pass
- checker smoke passes
- no root `.jikuo/policies/` or `.jikuo/task_sessions/` directory is created
- future trigger evaluator, evidence checker, write adapter, Skill, MCP, Plugin, frontend, and gate work remain explicitly deferred

Do not proceed to policy trigger evaluation, evidence checking, policy write mode, guarded `agent_flow.py apply`, Skill, MCP, Plugin, frontend, or gate work until this read-only adapter slice is accepted or revised.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
python -B tools/jikuo/project_state_tests.py
```

Result:

- `policy_store_tests.py`: passed; 5 tests
- `agent_flow_tests.py`: passed; 4 tests
- `task_session_tests.py`: passed; 24 tests
- `task_session_cards_tests.py`: passed; 4 tests
- `project_state_tests.py`: passed; 11 tests

```powershell
python -B tools/jikuo/policy_store.py status --project-root tools/jikuo/fixtures/policy_store_active_project --format json
```

Result:

- returned `jikuo.policy_store_status.v0`
- reported `policy_store_status: active`
- reported `policy_eval_status: not_evaluated`
- returned one active approved policy ref

```powershell
python -B tools/jikuo/agent_flow.py propose --event task_start --task-title "Policy Store Probe" --project-root tools/jikuo/fixtures/policy_store_active_project --format markdown
```

Result:

- returned a same-chat Markdown proposal
- included `Policy Context`
- reported `Policy store status: active`
- reported `Policy eval status: not_evaluated`
- reported `CAP-POLICY-STORE-STATUS-01` in atom trace
- reported `Writes performed: false`

```powershell
Test-Path -Path .jikuo\policies
Test-Path -Path .jikuo\task_sessions
```

Result:

- both returned `False`

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-08_read_only_policy_store_inspection.md --added tools/jikuo/policy_store.py --added tools/jikuo/policy_store_tests.py --added tools/jikuo/fixtures/policy_store_initialized_project/.jikuo/project_state.yaml --added tools/jikuo/fixtures/policy_store_initialized_project/.jikuo/policies/manifest.yaml --added tools/jikuo/fixtures/policy_store_active_project/.jikuo/project_state.yaml --added tools/jikuo/fixtures/policy_store_active_project/.jikuo/policies/manifest.yaml --added tools/jikuo/fixtures/policy_store_active_project/.jikuo/policies/approved/POLICY-three-phase-audit.yaml --added tools/jikuo/fixtures/policy_store_stale_project/.jikuo/project_state.yaml --added tools/jikuo/fixtures/policy_store_stale_project/.jikuo/policies/manifest.yaml --added tools/jikuo/fixtures/policy_store_conflict_project/.jikuo/project_state.yaml --added tools/jikuo/fixtures/policy_store_conflict_project/.jikuo/policies/manifest.yaml --added tools/jikuo/fixtures/policy_store_conflict_project/.jikuo/policies/approved/POLICY-duplicate-a.yaml --added tools/jikuo/fixtures/policy_store_conflict_project/.jikuo/policies/approved/POLICY-duplicate-b.yaml --changed tools/jikuo/agent_flow.py --changed tools/jikuo/agent_flow_tests.py --changed tools/jikuo/task_session.py --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md --changed docs/jikuo/governance/jikuo_policy_store_configuration_flow.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-08_read_only_policy_store_inspection.md
```

Result:

- registry validation passed
- triggered `R-006`, `R-012`, and `R-013`
- `R-006` required fields and sections reported `OK`
- `R-012` Sprint index document requirement reported `OK`; manual `sprint_index_entry` declaration remained `REVIEW`, as expected for report-only manual evidence
- `R-013` layer / kernel fields and sections reported `OK`; manual `skeleton_kernel_boundary_declaration` remained `REVIEW`, as expected for report-only manual evidence

---

## 12. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- policy trigger evaluator
- policy execution evidence checker
- policy proposal / approved-policy write mode
- policy proposal renderer
- guarded `agent_flow.py apply`
- Skill / MCP / Plugin packaging
- frontend implementation
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
