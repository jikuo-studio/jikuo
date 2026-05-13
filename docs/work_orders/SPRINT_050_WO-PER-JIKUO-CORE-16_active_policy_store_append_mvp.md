# SPRINT_050_WO-PER-JIKUO-CORE-16: Active Policy Store Append MVP

> **Date**: 2026-05-12
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / guarded active policy append
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: packaging_surface; frontend_surface; gate_enforcement; policy revision engine; supersession / rollback engine
> **Kernel compatibility**: extends the guarded policy-store writer from first-write initialization to active-store append; preserves proposal mode as no-write; appends one new active policy ref without rewriting unrelated manifest text; does not revise, supersede, deprecate, roll back, execute actions, auto-persist evidence, or promote gates
> **Deferred kernel backlog refs**: policy revision; supersession; deprecation; rollback; persisted proposal/decision records; guarded `agent_flow.py apply`; `CAP-MCP-TOOL-01`; `CAP-CODEX-SKILL-01`; frontend configuration console
> **Preceded by**: CORE-15 guarded policy store write MVP.
> **Current slice**: `policy_store.py write-policy` can append a second approved report-only policy to an already active policy store after explicit confirmation and approval.
> **User scenario**: A Codex / Claude desktop APP user already has one active project rule and wants to add another approved report-only rule.
> **Runtime chain**: active policy store -> no-write plan for new policy -> explicit approval -> guarded append -> manifest active refs include old and new policy -> status/evaluate read-back.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`, CORE-15 guarded writer, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.policy_write_plan.v0`; `jikuo.policy_write_result.v0`; approved `jikuo.configurable_rule_policy.v0`; updated `jikuo.policy_store_manifest.v0`.
> **Consumer projection**: Codex / Claude desktop APP chat, future MCP response, future Skill / Plugin wrapper, future frontend configuration surface.
> **Lifecycle**: initial guarded write -> guarded active append -> later revision / supersession / rollback.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

CORE-15 made the first approved project rule writable. This slice makes the policy store useful beyond the first rule.

Visible business value:

- users can add a second approved report-only rule to an existing policy store
- the existing active policy remains indexed
- the new policy becomes readable by `status` and triggerable by `evaluate`
- proposal mode still cannot write
- revision / supersession remains separate instead of being smuggled into append

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- extend `policy_store.py write-policy`
- allow `policy_store_status: active` when the policy id is new and target file is absent
- append one active policy ref to `manifest.yaml`
- preserve unrelated manifest text during append
- keep confirmation and approval requirements
- reject duplicate policy id / target collision
- verify appended policy through `status` and `evaluate`

This slice is not allowed to:

- make `agent_flow.py propose` write files
- revise existing policies
- supersede existing policies
- deprecate existing policies
- roll back policies
- persist proposal / decision records
- execute policy actions
- auto-persist policy evidence
- implement MCP / Skill / Plugin / frontend / gate behavior

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- treating append as a new policy, not a mutation of old policy semantics
- preserving existing manifest content through targeted text insertion
- refusing duplicate policy ids
- refusing target file collisions
- keeping post-write read-back verification
- leaving revision, supersession, rollback, and proposal persistence deferred

---

## 4. Deferred Kernel Backlog

Still deferred:

- policy revision
- supersession
- deprecation
- rollback
- proposal / decision persistence
- richer manifest writer with structured unknown-field preservation
- guarded `agent_flow.py apply`
- MCP / Skill / Plugin packaging
- frontend configuration console
- gate enforcement

---

## 5. Scope

Implemented:

- active-store append through `policy_store.py write-policy`
- append operation classification as `append_policy`
- manifest active ref insertion preserving unrelated text
- duplicate policy collision refusal
- status read-back with two active policy refs
- evaluate read-back that triggers only the matching appended policy

---

## 6. Out Of Scope

Not implemented:

- automatic append from `agent_flow.py propose`
- direct desktop apply command
- policy revision / supersession / rollback
- proposal / decision persistence
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
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-15_guarded_policy_store_write_mvp.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `policy_store_tests.py` verifies first write, second append, collision refusal, and status/evaluate read-back.

`integration`:

- limited; `agent_flow_tests.py` remains focused on no-write command preview because append execution is guarded by `policy_store.py`.

`workflow / orchestration`:

- required; smoke must prove first guarded write -> second guarded append -> status/evaluate read-back.

`semantic regression`:

- N/A because this slice governs process policy persistence, not product-output content.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify root `.jikuo/policies/` is not created by tests or proposal mode.

`human governance review`:

- required; user reviews whether append is correctly separated from revision / supersession before rule evolution work.

---

## 9. Delivery Criteria

- Active policy store accepts a second unique policy through guarded write.
- Existing active policy ref remains in manifest.
- New active policy ref is appended to manifest.
- Duplicate policy id refuses without modifying the policy file.
- Status read-back reports two active policy refs.
- Evaluate read-back can trigger the appended policy.
- Proposal mode remains no-write.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts append as distinct from revision / supersession
- tests pass
- checker smoke passes
- no root `.jikuo/policies/` is created by proposal or tests
- proposal persistence, revision, supersession, rollback, MCP, Skill, Plugin, frontend, guarded apply, and gate work remain deferred

Do not implement revision, supersession, rollback, or desktop apply until this append slice is accepted or revised.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
python -B tools/jikuo/project_state_tests.py
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-16_active_policy_store_append_mvp.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/jikuo/governance/jikuo_policy_store_configuration_flow.md --changed docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-16_active_policy_store_append_mvp.md
git diff --check -- tools/jikuo/policy_store.py tools/jikuo/policy_store_tests.py docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-16_active_policy_store_append_mvp.md docs/jikuo/governance/jikuo_productization_task_map.md docs/jikuo/governance/jikuo_execution_mounts.md docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md docs/jikuo/governance/jikuo_policy_store_configuration_flow.md docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md
```

Result:

- `policy_store_tests.py`: passed; 19 tests
- `agent_flow_tests.py`: passed; 8 tests
- `task_session_tests.py`: passed; 24 tests
- `task_session_cards_tests.py`: passed; 4 tests
- `project_state_tests.py`: passed; 11 tests
- report-only checker: exited 0; `R-006`, `R-012`, and `R-013` triggered as report-only obligations with required fields / sections / documents OK and manual declarations in REVIEW where expected
- `git diff --check`: exited 0; only CRLF conversion warnings were reported
- temp smoke project: first guarded write returned `create_policy` / `written`; second guarded write returned `append_policy` / `written`; `status` reported 2 active refs; `evaluate` triggered `POLICY-work-order-pre-task-review`; root `.jikuo/policies` and `.jikuo/task_sessions` remained absent
