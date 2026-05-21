# SPRINT_050_WO-PER-JIKUO-CORE-14: Policy Write Plan Proposal MVP

> **Date**: 2026-05-12
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / policy write planning
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: packaging_surface; frontend_surface; gate_enforcement; durable policy-store writer
> **Kernel compatibility**: renders a no-write policy-store write plan with explicit target, effect, non-effect, preflight, and approval boundary; does not create `.jikuo/policies/`, write approved policies, update manifest, execute actions, persist evidence, or promote gates
> **Deferred kernel backlog refs**: `CAP-POLICY-STORE-WRITE-01`; guarded `agent_flow.py apply`; `CAP-MCP-TOOL-01`; `CAP-CODEX-SKILL-01`; broader policy proposal editor; frontend configuration console
> **Preceded by**: CORE-07 policy store and user configuration flow; CORE-08 read-only policy-store inspection; CORE-09 trigger evaluator; CORE-13 condition evaluator; FLOW-02 Desktop App Primary Operating Loop.
> **Current slice**: `policy_store.py plan-write` and `agent_flow.py propose --event policy_write_plan` prepare a policy write plan card in report-only mode.
> **User scenario**: A Codex / Claude desktop APP user asks JIKUO to configure a durable project rule, but should first see what policy would be written, where it would be written, and what is not being changed.
> **Runtime chain**: user rule intent -> agent prepares structured policy candidate arguments -> policy write plan -> desktop proposal card -> user review -> future guarded writer only after explicit approval.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`, `jikuo_configurable_rule_trigger_policy.md`, `jikuo_rule_action_evidence_model.md`, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.policy_write_plan.v0`; `jikuo.agent_flow_proposal.v1`; `policy_write_plan` desktop card.
> **Consumer projection**: Codex / Claude desktop APP chat, future MCP response, future Skill / Plugin wrapper, future frontend configuration surface.
> **Lifecycle**: no-write write plan proposal -> user review -> later guarded policy-store writer -> later MCP / Skill / frontend.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

This slice adds the missing bridge between "I want this rule" and "JIKUO writes a durable project policy."

Visible business value:

- ordinary desktop APP users can review a future policy write without editing YAML
- the system exposes target files before any policy store write exists
- the difference between proposal, plan, and durable write remains explicit
- future writer work can be implemented against a stable plan object instead of inventing write semantics ad hoc

This is still a skeleton-safe kernel slice: it prepares the plan, not the write.

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- add `policy_store.py plan-write`
- add `agent_flow.py propose --event policy_write_plan`
- produce `jikuo.policy_write_plan.v0`
- render a desktop card with policy ref, preflight, write set, non-effects, and refusal reasons
- detect target policy collisions without writing
- test that no `.jikuo/policies/` directory is created by proposal-only flows
- register `CAP-POLICY-STORE-WRITE-PROPOSE-01`

This slice is not allowed to:

- implement durable `CAP-POLICY-STORE-WRITE-01`
- create `.jikuo/policies/`
- write approved policy files
- write policy proposals
- update `manifest.yaml`
- execute required actions
- auto-persist evidence
- implement guarded `agent_flow.py apply`
- implement Skill / MCP / Plugin / frontend / gate behavior

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- using the CORE-07 `jikuo.policy_write_plan.v0` contract
- keeping pending proposals distinct from approved active policies
- keeping write effects and non-effects visible before approval
- keeping `approval_present: false` in this no-write plan
- refusing obvious target collisions before any writer exists
- preserving future paths for revision, supersession, rollback, MCP, Skill, Plugin, and frontend

---

## 4. Deferred Kernel Backlog

Still deferred:

- `CAP-POLICY-STORE-WRITE-01`: guarded durable policy-store write implementation
- writing pending proposal records
- user decision records
- approval phrase persistence
- manifest unknown-field preservation writer
- policy revision / supersession / rollback implementation
- broader natural-language policy extraction
- guarded `agent_flow.py apply`
- Skill / MCP / Plugin / frontend / gate adapters

---

## 5. Scope

Implemented:

- `policy_store.py plan-write`
- `agent_flow.py propose --event policy_write_plan`
- derived or explicit policy id support
- task metadata / path condition projection into proposed policy
- target collision refusal
- `CAP-POLICY-STORE-WRITE-PROPOSE-01` atom trace
- JSON and Markdown-visible card projection
- no-write regression tests

---

## 6. Out Of Scope

Not implemented:

- actual policy-store writes
- automatic policy extraction from arbitrary prose
- proposal persistence
- approval capture
- apply mode
- frontend editor
- MCP / Skill / Plugin packaging
- gate enforcement

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
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `policy_store_tests.py` verifies plan creation and collision refusal without writes.

`integration`:

- required; `agent_flow_tests.py` verifies desktop proposal projection and atom trace.

`workflow / orchestration`:

- required; Markdown smoke must show a policy write plan card, write set, non-effects, and no-write boundary.

`semantic regression`:

- N/A because this slice governs process policy configuration, not product-output content.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify root `.jikuo/policies/` is not created.

`human governance review`:

- required; user reviews whether the policy write plan card is understandable before durable writer work.

---

## 9. Delivery Criteria

- `policy_store.py plan-write` returns `jikuo.policy_write_plan.v0`.
- The plan includes preflight, write set, non-effects, proposed policy, and approval boundary.
- Existing target collision is refused before any write.
- `agent_flow.py propose --event policy_write_plan` renders the plan as a desktop card.
- `CAP-POLICY-STORE-WRITE-PROPOSE-01` appears in atom trace.
- Proposal-only commands do not create `.jikuo/policies/`.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- the user accepts the card as a readable pre-write review surface
- tests pass
- checker smoke passes
- no root policy store is created
- durable writer, proposal persistence, apply mode, MCP, Skill, Plugin, frontend, and gate work remain explicitly deferred

Do not implement durable policy-store writes until this proposal-only write plan slice is accepted or revised.

---

## 11. Verification Log

Commands run so far:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
python -B tools/jikuo/project_state_tests.py
python -B tools/jikuo/policy_store.py plan-write --project-root tools/jikuo/fixtures/task_session_ready_project --policy-id POLICY-three-phase-audit --title "Three-phase task audit" --source-ref "<exact user phrase as spoken>" --task-type work_order_delivery --jikuo-layer configurable_rule_kernel --changed-path-pattern docs/jikuo/** --format json
python -B tools/jikuo/agent_flow.py propose --event policy_write_plan --policy-ref POLICY-three-phase-audit --policy-title "Three-phase task audit" --policy-source-ref "<exact user phrase as spoken>" --policy-task-type work_order_delivery --policy-jikuo-layer configurable_rule_kernel --policy-changed-path-pattern docs/jikuo/** --project-root tools/jikuo/fixtures/task_session_ready_project --format markdown
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-14_policy_write_plan_proposal_mvp.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/jikuo/governance/jikuo_policy_store_configuration_flow.md --changed docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-14_policy_write_plan_proposal_mvp.md
```

Result:

- `policy_store_tests.py`: passed; 15 tests
- `agent_flow_tests.py`: passed; 8 tests
- `task_session_tests.py`: passed; 24 tests
- `task_session_cards_tests.py`: passed; 4 tests
- `project_state_tests.py`: passed; 11 tests
- `policy_store.py plan-write` smoke returned `jikuo.policy_write_plan.v0`, `status: review`, two future write targets, `writes_performed: false`, and three proposed conditions.
- `agent_flow.py propose --event policy_write_plan` smoke rendered a `policy_write_plan` card and included `CAP-POLICY-STORE-WRITE-PROPOSE-01`; proposal remained no-write.
- checker smoke passed in report-only mode; `R-006` fields/sections OK, `R-012` Sprint index document present with manual declaration review, and `R-013` JIKUO layer/kernel fields/sections OK with manual declaration review.
- root `.jikuo/policies/` and fixture `.jikuo/policies/` remained absent.

## 9.1 Work-Profile Applicability Follow-Up

On 2026-05-21, `CAP-POLICY-STORE-WRITE-PROPOSE-01` was extended so no-write
policy plans and guarded writer command previews can include:

- `--work-profile-lifecycle-event`;
- `--work-profile-policy-scope`.

The generated policy YAML uses `applies_to_work_profile` with inline scalar
lists so the project-local minimal YAML reader can round-trip the field before
the evaluator consumes it. This follow-up does not change evaluator behavior,
does not activate any held candidate policy, and does not perform durable
policy writes by itself.
