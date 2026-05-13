# SPRINT_050_WO-PER-JIKUO-CORE-07: Policy Store And User Configuration Flow

> **Date**: 2026-05-11
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / policy store contract
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: desktop_operating_skeleton; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: defines future approved policy store, proposal, decision, write-plan, write-result, revision, deprecation, supersession, and rollback contracts while preserving desktop-first approval and no-write boundaries
> **Deferred kernel backlog refs**: `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`
> **Preceded by**: CORE-04 project-local state and sidecar storage contract; CORE-05 configurable rule trigger policy; CORE-06 rule action and evidence model.
> **Current slice**: policy store and user configuration flow contract only; no policy files, no store adapter, no proposal persistence, no policy-aware runner, no Skill, no MCP, no Plugin, no frontend, no gate, and no automatic durable write.
> **User scenario**: A Codex / Claude desktop APP user wants to turn natural-language working-method preferences or required-reference declarations into durable project policies without editing raw YAML or relying on agent memory.
> **Runtime chain**: user states preference -> agent proposes policy candidate -> user approves/revises/rejects/defers in chat -> future guarded writer previews write plan -> user approves exact write effect -> future store writes approved policy -> future agents read approved policy.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`, `jikuo_configurable_rule_trigger_policy.md`, `jikuo_rule_action_evidence_model.md`, CORE-04 storage contract, `jikuo_execution_mounts.md`, and `jikuo_productization_task_map.md`.
> **Bridge object**: `jikuo.policy_store_manifest.v0`; `jikuo.policy_proposal.v0`; `jikuo.policy_decision.v0`; `jikuo.policy_write_plan.v0`; `jikuo.policy_write_result.v0`
> **Consumer projection**: future policy-aware `agent_flow.py`, future desktop-agent policy proposal cards, future store adapter, future checker evidence reports, future MCP tool, future frontend configuration surfaces, and later gate adapters after explicit approval.
> **Lifecycle**: contract draft -> user review -> accepted store/config flow -> downstream policy-aware runner / evidence checker / store implementation planning.
> **Testing layers**: documentation review, workflow/orchestration review, checker smoke, no-write smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：CORE-07 的业务意义是把“用户想要的规则”从聊天里的偏好，变成未来可持续生效的项目 policy。但这一工单仍然只定义契约，不写入 policy store。

The product problem:

- CORE-05 and CORE-06 define what policies mean
- but users still need a safe way to approve, revise, reject, and persist policies
- without a store contract, later implementation could accidentally treat pending proposals, chat memory, or desktop cards as active policies

This slice defines the future policy store and user configuration flow.

Visible business value:

- ordinary users can configure rules from desktop APP chat
- pending proposals stay separate from active policies
- approved policy writes require explicit target/effect/non-effect approval
- future agents can read approved policies rather than relying on long prompts
- future UI / MCP / Skill / Plugin work has a shared storage contract

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- define future `.jikuo/policies/` layout proposal
- define policy store source hierarchy
- define policy proposal object
- define approved policy storage metadata
- define policy decision record object
- define policy write plan/result objects
- define revision, deprecation, supersession, and rollback rules
- define desktop APP policy configuration flow
- update task map, execution mounts, Sprint index, and skeleton/kernel backlog status

This slice is not allowed to:

- create `.jikuo/policies/`
- update `.jikuo/project_state.yaml`
- write policy files
- implement a policy store adapter
- implement policy-aware `agent_flow.py`
- implement policy proposal cards
- install a Codex Skill
- implement MCP, Plugin, frontend, or gates
- edit `.codex/AGENTS.md`
- create `.jikuo/task_sessions/`
- change runtime narrative-engine behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

This slice preserves future kernel compatibility by:

- separating pending proposals from approved active policies
- keeping active policy lookup project-local and tool-readable
- preserving exact approval target/effect/non-effect for durable writes
- treating task-session policy snapshots as evidence, not active policy source
- making desktop APP and future frontend consume the same policy objects
- preserving registry migration as a later explicit work order

---

## 4. Deferred Kernel Backlog

This slice does not complete the configurable rule kernel.

Deferred tasks:

- `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`
- policy store adapter implementation
- policy proposal card renderer

Packaging and surface tasks remain deferred:

- installable Codex Skill
- MCP tool wrapper
- Codex Plugin
- frontend rule configuration / audit console
- gate enforcement adapter

---

## 5. Scope

This work order implements:

- `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- task-map updates registering `JIKUO-CORE-07` and the policy store/configuration capability
- execution-mount updates for future policy store, configuration, and policy-aware runner work
- Sprint index entries for the work order and policy store contract
- skeleton/kernel backlog status update
- report-only checker verification

---

## 6. Out Of Scope

This work order does not:

- create `.jikuo/policies/`
- persist proposals or policies
- add policy refs to `.jikuo/project_state.yaml`
- implement policy write commands
- modify `tools/jikuo/agent_flow.py`
- modify `tools/audit/check_rule_registry.py`
- import AGENTS / CLAUDE docs into active policies
- implement UI / Skill / MCP / Plugin / gate adapters
- promote report-only rules into blockers
- alter runtime narrative-engine behavior

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- N/A for this slice because no parser, writer, store adapter, or policy-aware runner is implemented.

`integration`:

- N/A because no Skill, MCP, Plugin, frontend, storage adapter, checker integration, or gate integration is implemented.

`workflow / orchestration`:

- required; review that the flow covers proposal, revision, approval, write plan, write result, active policy lookup, deprecation, supersession, and rollback.

`semantic regression`:

- N/A because this slice governs process policy configuration, not product-output content or narrative runtime behavior.

`smoke`:

- run report-only checker against the new work order and updated planning docs.
- verify no `.jikuo/policies/` and no `.jikuo/task_sessions/` root records are created by this slice.

`human governance review`:

- required; user reviews whether the store/configuration contract lets ordinary users configure rules without raw YAML while preserving approval boundaries.

---

## 9. Store / Configuration Summary

The new contract defines:

- policy store source hierarchy
- future `.jikuo/policies/` layout proposal
- `jikuo.policy_store_manifest.v0`
- `jikuo.policy_proposal.v0`
- approved policy storage metadata
- `jikuo.policy_decision.v0`
- `jikuo.policy_write_plan.v0`
- `jikuo.policy_write_result.v0`
- desktop APP configuration flow
- revision / deprecation / supersession / rollback rules
- AGENTS / long-doc import safety rules
- registry migration boundary

---

## 10. Delivery Criteria

- Policy store/configuration flow document exists.
- Work order declares the required JIKUO layer / kernel compatibility fields.
- Policy store source hierarchy is defined.
- Future store layout is proposed without creating files.
- Proposal, decision, write plan, write result, and approved policy storage metadata are defined.
- Desktop APP configuration flow is defined.
- Revision, deprecation, supersession, and rollback rules are defined.
- Task map registers `JIKUO-CORE-07` and a new policy store/configuration capability atom.
- Execution mounts point future policy-aware runner, evidence checker, UI, MCP, Skill, Plugin, and gate work to this contract.
- Sprint index links the work order and governance contract.
- Report-only checker validation passes.
- No `.jikuo/policies/` or `.jikuo/task_sessions/` directory is created.

---

## 11. Acceptance Gate

This slice may be accepted only if:

- the user agrees that pending proposals are clearly separated from approved active policies
- the user agrees that ordinary configuration remains desktop APP first
- the user agrees that durable policy writes require exact target/effect/non-effect approval
- the user agrees that the future store layout is reasonable as a contract but not yet implemented
- checker smoke passes
- no `.jikuo/policies/` or `.jikuo/task_sessions/` directory is created

Do not proceed to AGENT-07, CHECKER-02, store adapter implementation, Skill, MCP, Plugin, frontend, guarded `apply`, or gates until this contract is accepted or revised.

---

## 12. Verification Log

Commands run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-07_policy_store_and_user_configuration_flow.md --added docs/jikuo/governance/jikuo_policy_store_configuration_flow.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-07_policy_store_and_user_configuration_flow.md
```

Result:

- registry validation passed
- rule count: 9
- triggered `R-006`, `R-012`, and `R-013`
- `R-006` required work-order fields and sections reported `OK`
- `R-012` Sprint index document requirement reported `OK`; manual `sprint_index_entry` declaration remained `REVIEW`, as expected for report-only manual evidence
- `R-013` layer / kernel fields and sections reported `OK`; manual `skeleton_kernel_boundary_declaration` remained `REVIEW`, as expected for report-only manual evidence

```powershell
Test-Path -Path .jikuo\policies
Test-Path -Path .jikuo\task_sessions
```

Result:

- both returned `False`; no policy store or task-session sidecar root was created by this slice

```powershell
git diff --check -- docs/jikuo/governance/jikuo_policy_store_configuration_flow.md docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-07_policy_store_and_user_configuration_flow.md docs/jikuo/governance/jikuo_productization_task_map.md docs/jikuo/governance/jikuo_execution_mounts.md docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md
```

Result:

- passed; only line-ending conversion warnings were reported for existing tracked markdown files

---

## 13. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- policy proposal persistence
- approved policy persistence
- policy store adapter
- policy-aware `agent_flow.py`
- policy execution evidence checker
- user configuration UI
- Skill / MCP / Plugin packaging
- guarded `agent_flow.py apply`
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
