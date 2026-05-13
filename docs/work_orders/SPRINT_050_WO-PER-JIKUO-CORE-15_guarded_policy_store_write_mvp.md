# SPRINT_050_WO-PER-JIKUO-CORE-15: Guarded Policy Store Write MVP

> **Date**: 2026-05-12
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / guarded policy-store write
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: packaging_surface; frontend_surface; gate_enforcement; rule evolution engine; broad policy editor
> **Kernel compatibility**: adds a guarded initial policy-store writer that requires explicit command confirmation and exact approval phrase; keeps `agent_flow.py propose` no-write; does not execute policy actions, auto-persist evidence, supersede policies, roll back policies, or promote gates
> **Deferred kernel backlog refs**: active-store append / revision / supersession / rollback; persisted proposal records; guarded `agent_flow.py apply`; `CAP-MCP-TOOL-01`; `CAP-CODEX-SKILL-01`; frontend configuration console
> **Preceded by**: CORE-07 policy store and user configuration flow; CORE-08 read-only policy-store inspection; CORE-14 policy write plan proposal MVP.
> **Current slice**: `policy_store.py write-policy` can create the first approved report-only project policy and manifest after explicit approval; `agent_flow.py propose --event policy_write_plan` shows the guarded command preview without executing it.
> **User scenario**: A Codex / Claude desktop APP user has reviewed a policy write plan and explicitly approves turning it into a project-local approved policy.
> **Runtime chain**: policy write plan -> exact approval phrase -> guarded writer -> approved policy file + manifest -> read-back status/evaluator verification.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`, `jikuo_configurable_rule_trigger_policy.md`, `jikuo_rule_action_evidence_model.md`, CORE-14 write-plan proposal, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.policy_write_plan.v0`; `jikuo.policy_write_result.v0`; approved `jikuo.configurable_rule_policy.v0`; `jikuo.policy_store_manifest.v0`.
> **Consumer projection**: Codex / Claude desktop APP chat, future MCP response, future Skill / Plugin wrapper, future frontend configuration surface.
> **Lifecycle**: no-write write plan proposal -> explicit approval -> guarded initial write -> read-only status/evaluate verification -> later active-store append / revision / supersession.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

This slice closes the first real policy loop:

- user expresses a rule
- JIKUO renders a policy write plan
- user reviews the plan
- user explicitly approves the write
- JIKUO writes the first approved report-only policy
- later policy evaluation can read and trigger that policy

Visible business value:

- important project rules can move from chat memory into project-local policy storage
- writes require a technical confirmation flag and exact approval phrase
- proposal mode remains safe and no-write
- the written policy is immediately readable by the existing status/evaluate atoms

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- add `policy_store.py write-policy`
- create `.jikuo/policies/` only when the guarded writer is explicitly invoked
- create one approved policy file
- create or update an empty initialized manifest for the first active policy
- refuse missing confirmation / missing approval
- refuse existing policy collision
- verify the written policy through `policy_store.py status` and `policy_store.py evaluate`
- expose the guarded command preview in `agent_flow.py propose --event policy_write_plan`

This slice is not allowed to:

- make `agent_flow.py propose` write files
- write policies without `--confirm-write-policy`
- write policies without `--approval-phrase`
- append to arbitrary active stores with multiple policies
- revise, supersede, deprecate, or roll back policies
- persist pending proposal / decision records
- execute policy actions
- auto-persist policy evidence
- implement MCP / Skill / Plugin / frontend / gate behavior

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- using CORE-07 write-plan / write-result vocabulary
- preserving proposal mode as no-write
- separating plan review from durable write execution
- keeping the first writer limited to initial / empty policy-store cases
- making post-write read-back verification part of the result
- leaving active-store append, supersession, rollback, MCP, Skill, Plugin, frontend, and gate behavior deferred

---

## 4. Deferred Kernel Backlog

Still deferred:

- active policy-store append with unknown-field preservation
- policy proposal persistence
- user decision record persistence
- policy revision / supersession / deprecation / rollback
- guarded `agent_flow.py apply`
- MCP / Skill / Plugin packaging
- frontend configuration console
- gate enforcement

---

## 5. Scope

Implemented:

- `policy_store.py write-policy`
- `--confirm-write-policy`
- `--approval-phrase`
- `jikuo.policy_write_result.v0`
- initial approved policy file creation
- initial manifest creation
- collision refusal
- post-write read-back status verification
- evaluator verification that the new policy triggers
- `agent_flow.py` command preview for future approved write

---

## 6. Out Of Scope

Not implemented:

- automatic write from `agent_flow.py propose`
- direct desktop apply command
- active-store append beyond initial / empty store MVP
- proposal / decision persistence
- policy revision / supersession / rollback
- action execution
- automatic evidence persistence
- UI / MCP / Skill / Plugin / gate

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-14_policy_write_plan_proposal_mvp.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `policy_store_tests.py` verifies missing approval refusal, guarded write success, collision refusal, and evaluator read-back.

`integration`:

- required; `agent_flow_tests.py` verifies the policy write-plan card exposes a guarded command preview while remaining no-write.

`workflow / orchestration`:

- required; smoke must prove plan -> guarded write -> status/evaluate read-back.

`semantic regression`:

- N/A because this slice governs process policy persistence, not product-output content.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify root `.jikuo/policies/` is not created by tests or proposal mode.

`human governance review`:

- required; user reviews whether the approval boundary and initial-writer limitation are acceptable before active-store append or desktop apply work.

---

## 9. Delivery Criteria

- Missing confirmation or approval refuses without writing.
- Guarded write creates approved policy and manifest in a temp project.
- Written policy is readable by `policy_store.py status`.
- Written policy can trigger through `policy_store.py evaluate`.
- Re-running the same policy write refuses collision.
- `agent_flow.py propose --event policy_write_plan` stays no-write and shows guarded command preview.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts that this is an initial guarded writer, not full rule evolution
- tests pass
- checker smoke passes
- no root `.jikuo/policies/` is created by proposal or tests
- active-store append, proposal persistence, revision, supersession, rollback, MCP, Skill, Plugin, frontend, guarded apply, and gate work remain deferred

Do not implement active-store append or desktop apply until this guarded initial writer is accepted or revised.

---

## 11. Verification Log

Commands run so far:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
python -B tools/jikuo/project_state_tests.py
python -B tools/jikuo/agent_flow.py propose --event policy_write_plan --policy-ref POLICY-work-order-pre-task-review --policy-title "Work-order pre-task review card" --policy-source-ref "<exact user phrase as spoken>" --policy-task-type work_order_delivery --policy-jikuo-layer configurable_rule_kernel --project-root tools/jikuo/fixtures/task_session_ready_project --format markdown
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-15_guarded_policy_store_write_mvp.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/jikuo/governance/jikuo_policy_store_configuration_flow.md --changed docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-15_guarded_policy_store_write_mvp.md
```

Result:

- `policy_store_tests.py`: passed; 18 tests
- `agent_flow_tests.py`: passed; 8 tests
- `task_session_tests.py`: passed; 24 tests
- `task_session_cards_tests.py`: passed; 4 tests
- `project_state_tests.py`: passed; 11 tests
- `agent_flow.py propose --event policy_write_plan` smoke rendered a no-write card with guarded `write-policy` command preview.
- checker smoke passed in report-only mode; `R-006` fields/sections OK, `R-012` Sprint index document present with manual declaration review, and `R-013` JIKUO layer/kernel fields/sections OK with manual declaration review.
- root `.jikuo/policies/` and fixture `.jikuo/policies/` remained absent after proposal smoke.
