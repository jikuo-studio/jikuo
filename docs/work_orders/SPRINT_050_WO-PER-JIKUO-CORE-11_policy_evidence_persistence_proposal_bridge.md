# SPRINT_050_WO-PER-JIKUO-CORE-11: Policy Evidence Persistence Proposal Bridge

> **Date**: 2026-05-12
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / desktop runner bridge
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: bridges CORE-10 evidence status to the existing guarded task-session evidence append path; does not auto-write evidence, execute actions, write policies, or promote gates
> **Deferred kernel backlog refs**: `CAP-POLICY-CONDITION-EVALUATOR-01`; `CAP-POLICY-STORE-WRITE-01`; `CAP-POLICY-EVIDENCE-INGEST-01`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`
> **Preceded by**: CORE-10 policy evidence checker MVP; TASKSESSION-04 lifecycle/evidence append; FLOW-02 Desktop App Primary Operating Loop.
> **Current slice**: `agent_flow.py propose --event policy_evidence_record ...` converts explicit policy evidence refs into a guarded `task_session.py update --append-evidence` command proposal.
> **User scenario**: A Codex / Claude desktop APP user has reviewed a policy evidence status item and wants a safe, explicit, auditable way to persist that compact evidence into a selected task session.
> **Runtime chain**: policy evidence status -> user/agent selects explicit refs -> `policy_evidence_record` proposal -> guarded task-session evidence append command -> same-chat approval loop -> later explicit write.
> **Canonical source**: `jikuo_rule_action_evidence_model.md`, `jikuo_policy_aware_agent_flow_contract.md`, TASKSESSION-04 lifecycle update, CORE-10 evidence checker MVP, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.agent_flow_proposal.v1`; `task_session_evidence_append` desktop card; existing `jikuo.task_session_update_result.v0` write result after future approval.
> **Consumer projection**: Codex / Claude desktop APP chat cards, future MCP response, future Skill / Plugin wrapper, future frontend audit surfaces.
> **Lifecycle**: evidence checker MVP -> persistence proposal bridge -> user review -> explicit guarded append -> later evidence ingestion and audit views.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

This slice connects "evidence is visible" to "evidence can be safely recorded" without making persistence automatic.

Visible business value:

- the user does not need to hand-compose `task_session.py update --append-evidence`
- policy evidence persistence is proposed in the same desktop APP chat
- target session, policy, action, requirement, evidence kind, and evidence ref must be explicit
- the generated command still requires explicit approval and technical confirmation

Important boundary:

- `agent_flow.py propose` remains no-write
- no evidence is persisted until the user approves and an explicit guarded command is run
- no policy action is executed
- no gate behavior is introduced

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- extend `tools/jikuo/agent_flow.py`
- extend `tools/jikuo/agent_flow_tests.py`
- add a fixture with an existing task session for no-write proposal testing
- add `policy_evidence_record` as a supported desktop runner event
- generate a guarded task-session evidence append command proposal
- add `CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01` atom trace
- update task map, execution mounts, loop composition, Sprint index, and policy-aware docs

This slice is not allowed to:

- run the generated guarded update command automatically
- persist evidence from `agent_flow.py propose`
- create task sessions
- write approved policies or proposals
- evaluate advanced policy conditions
- execute policy actions
- install Skill / MCP / Plugin / frontend / gate behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- reusing the existing TASKSESSION-04 guarded evidence append path
- keeping policy evidence refs compact and explicit
- keeping evidence persistence separate from evidence checking
- preserving user approval as the write boundary
- keeping `.jikuo/project_state.yaml` index updates out of this bridge
- keeping gate behavior deferred

---

## 4. Deferred Kernel Backlog

Still deferred:

- `CAP-POLICY-EVIDENCE-INGEST-01`: read persisted task-session evidence back into policy evidence evaluation
- `CAP-POLICY-CONDITION-EVALUATOR-01`: non-lifecycle conditions such as path matches, document mounts, work-order metadata, and checker results
- `CAP-POLICY-STORE-WRITE-01`: guarded policy proposal / approved-policy write mode
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`: broader checker composition and report ingestion
- Skill / MCP / Plugin / frontend / gate adapters

---

## 5. Scope

Implemented:

- `policy_evidence_record` event alias
- explicit `--policy-ref`, `--action-ref`, and `--requirement-ref` args
- guarded `task_session.py update --append-evidence` command proposal
- `CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01` atom trace
- refusal card when required refs are missing
- fixture with existing task session
- workflow test proving proposal is no-write and includes approval flags

---

## 6. Out Of Scope

Not implemented:

- automatic evidence persistence
- reading persisted policy evidence back into CORE-10 matching
- checker-result ingestion
- condition evaluation beyond lifecycle event exact match
- action execution
- policy writes
- guarded `agent_flow.py apply`
- MCP / Skill / Plugin / frontend packaging
- gates or blocking enforcement

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-10_policy_evidence_checker_mvp.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `agent_flow_tests.py` verifies policy evidence persistence proposal fields and no-write behavior.

`integration`:

- limited; existing `task_session_tests.py` verifies guarded evidence append behavior.

`workflow / orchestration`:

- required; Markdown proposal must show guarded command proposal, approval phrase placeholder, and no-write boundary.

`semantic regression`:

- N/A because this slice governs process evidence persistence, not product-output content or narrative runtime behavior.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify the fixture task-session file is unchanged after proposal.

`human governance review`:

- required; user reviews whether the persistence proposal is understandable and sufficiently explicit before any apply/gate work.

---

## 9. Delivery Criteria

- `agent_flow.py propose --event policy_evidence_record ...` returns `jikuo.agent_flow_proposal.v1`.
- Proposal includes `CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01`.
- Proposal includes a guarded `task_session.py update --append-evidence` command.
- Command includes `--confirm-update-task-session` and `--approval-phrase`.
- Proposal does not modify the target task-session file.
- Missing required refs produce a refusal card.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts that policy evidence persistence is proposal-only in `agent_flow.py`
- tests pass
- checker smoke passes
- no unapproved task-session write occurs
- evidence ingestion, condition evaluator, policy write adapter, Skill, MCP, Plugin, frontend, and gate work remain explicitly deferred

Do not proceed to evidence ingestion, condition evaluation, policy write mode, guarded `agent_flow.py apply`, Skill, MCP, Plugin, frontend, or gate work until this persistence proposal bridge is accepted or revised.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
```

Result:

- `agent_flow_tests.py`: passed; 5 tests
- `task_session_tests.py`: passed; 24 tests

Additional checker and adjacent helper verification should be recorded before final acceptance.
