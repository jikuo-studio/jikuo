# SPRINT_050_WO-PER-JIKUO-CORE-17: Policy Decision Record MVP

> **Date**: 2026-05-12
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / guarded policy decision persistence
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: packaging_surface; frontend_surface; gate_enforcement; policy proposal persistence; policy revision engine; supersession / rollback engine
> **Kernel compatibility**: extends guarded policy-store writes so every successful policy create / append writes a compact `jikuo.policy_decision.v0` record; preserves proposal mode as no-write; does not persist pending proposals, revise policies, supersede policies, execute actions, auto-persist evidence, or promote gates
> **Deferred kernel backlog refs**: policy proposal persistence; policy revision; supersession; deprecation; rollback; guarded `agent_flow.py apply`; `CAP-MCP-TOOL-01`; `CAP-CODEX-SKILL-01`; frontend configuration console
> **Preceded by**: CORE-15 guarded policy store write MVP; CORE-16 active policy store append MVP.
> **Current slice**: `policy_store.py write-policy` writes a durable policy decision record next to the approved policy and manifest after explicit confirmation and approval.
> **User scenario**: A Codex / Claude desktop APP user approves a policy-store write and later needs to audit what was approved, what changed, and what did not change.
> **Runtime chain**: no-write plan -> explicit approval -> guarded policy write -> policy decision record -> manifest update -> status/evaluate read-back.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`, CORE-15 guarded writer, CORE-16 append writer.
> **Bridge object**: `jikuo.policy_write_plan.v0`; `jikuo.policy_write_result.v0`; `jikuo.policy_decision.v0`.
> **Consumer projection**: Codex / Claude desktop APP chat, future MCP response, future Skill / Plugin wrapper, future frontend audit surface.
> **Lifecycle**: guarded policy create / append -> durable decision record -> later proposal persistence / revision / supersession / rollback.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

CORE-15 and CORE-16 made policy storage writable. This slice makes each successful policy write auditable.

Visible business value:

- a stored policy is connected to the approval phrase that authorized it
- write effect and non-effect are preserved as a compact decision record
- append remains separate from revision / supersession
- future audit UI can show why a policy entered the store without mining chat history

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- add `.jikuo/policies/decisions/`
- add a decision record path to `policy_write_plan.write_set`
- write one `jikuo.policy_decision.v0` record during guarded `write-policy`
- report `decision_record_ref` and `decision_record_written` in `policy_write_result`
- refuse decision-record target collision

This slice is not allowed to:

- persist pending policy proposals
- make `agent_flow.py propose` write files
- implement guarded `agent_flow.py apply`
- revise existing policies
- supersede existing policies
- deprecate existing policies
- roll back policies
- execute policy actions
- auto-persist policy evidence
- implement MCP / Skill / Plugin / frontend / gate behavior

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- treating policy decisions as audit records, not active policy sources
- keeping approved policy files and manifest as the active lookup source
- writing decision records only inside guarded write mode
- preserving proposal mode as no-write
- leaving proposal persistence and policy evolution deferred

---

## 4. Deferred Kernel Backlog

Still deferred:

- pending policy proposal persistence
- proposal / decision linking beyond the stable proposal ref already captured in the write plan
- policy revision
- supersession
- deprecation
- rollback
- guarded `agent_flow.py apply`
- MCP / Skill / Plugin packaging
- frontend configuration / audit console
- gate enforcement

---

## 5. Scope

Implemented:

- `jikuo.policy_decision.v0` record writer
- `.jikuo/policies/decisions/POLICYDECISION-*.yaml`
- write-plan `write_set` entry for the decision record
- guarded write result fields: `decision_record_ref`; `post_write_verification.decision_record_written`
- cleanup of the decision record if manifest update fails before completion

---

## 6. Out Of Scope

Not implemented:

- proposal persistence
- decision registry / manifest index
- decision review UI
- automatic desktop apply
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
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-15_guarded_policy_store_write_mvp.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-16_active_policy_store_append_mvp.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `policy_store_tests.py` verifies write-plan decision record targets and successful decision record persistence.

`integration`:

- limited; no `agent_flow.py propose` durable write is introduced.

`workflow / orchestration`:

- required; smoke must prove guarded write -> decision record -> status/evaluate read-back.

`semantic regression`:

- N/A because this slice governs process policy persistence, not product-output content.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify root `.jikuo/policies/` and `.jikuo/task_sessions/` are not created by proposal or tests.

`human governance review`:

- required; user reviews whether decision records are correctly separated from proposal persistence and policy evolution.

---

## 9. Delivery Criteria

- Policy write plan includes a decision record write target.
- Guarded initial policy write creates a decision record.
- Guarded active-store append creates a decision record.
- Write result reports the decision record path.
- Post-write verification reports the decision record exists.
- Proposal mode remains no-write.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts decision records as audit records, not active policy sources
- tests pass
- checker smoke passes
- no root `.jikuo/policies/` is created by proposal or tests
- proposal persistence, revision, supersession, rollback, MCP, Skill, Plugin, frontend, guarded apply, and gate work remain deferred

Do not implement proposal persistence or policy evolution until this decision-record slice is accepted or revised.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
python -B tools/jikuo/project_state_tests.py
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-17_policy_decision_record_mvp.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/jikuo/governance/jikuo_policy_store_configuration_flow.md --changed docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-17_policy_decision_record_mvp.md
git diff --check -- tools/jikuo/policy_store.py tools/jikuo/policy_store_tests.py docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-17_policy_decision_record_mvp.md docs/jikuo/governance/jikuo_productization_task_map.md docs/jikuo/governance/jikuo_execution_mounts.md docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md docs/jikuo/governance/jikuo_policy_store_configuration_flow.md docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md
```

Result:

- `policy_store_tests.py`: passed; 19 tests
- `agent_flow_tests.py`: passed; 8 tests
- `task_session_tests.py`: passed; 24 tests
- `task_session_cards_tests.py`: passed; 4 tests
- `project_state_tests.py`: passed; 11 tests
- report-only checker: exited 0; `R-006`, `R-012`, and `R-013` triggered as report-only obligations with required fields / sections / documents OK and manual declarations in REVIEW where expected
- `git diff --check`: exited 0; only CRLF conversion warnings were reported
- temp smoke project: guarded write returned `written`; `decision_record_ref` pointed to `.jikuo/policies/decisions/POLICYDECISION-*.yaml`; `decision_record_written` was true; status reported 1 active ref; root `.jikuo/policies` and `.jikuo/task_sessions` remained absent
