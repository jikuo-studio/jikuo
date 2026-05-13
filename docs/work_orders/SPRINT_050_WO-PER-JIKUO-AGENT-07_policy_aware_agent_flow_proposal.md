# SPRINT_050_WO-PER-JIKUO-AGENT-07: Policy-Aware Agent Flow Proposal

> **Date**: 2026-05-11
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / desktop operating skeleton / policy-aware proposal contract
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: desktop_operating_skeleton
> **Current slice is not**: configurable_rule_kernel; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: consumes CORE-05 / CORE-06 / CORE-07 policy contracts without redefining kernel semantics; preserves no-write proposal boundary and future policy-aware runner implementation path
> **Deferred kernel backlog refs**: `JIKUO-CHECKER-02_policy_execution_evidence_checker`; policy-aware `agent_flow.py` implementation; policy store adapter implementation
> **Preceded by**: AGENT-05 local deterministic no-write runner; CORE-05 configurable rule trigger policy; CORE-06 rule action/evidence model; CORE-07 policy store/configuration flow.
> **Current slice**: policy-aware proposal projection contract only; no `agent_flow.py` code change, no policy-store read, no trigger evaluator, no evidence checker, no Skill, no MCP, no Plugin, no frontend, no gate, and no durable write.
> **User scenario**: A Codex / Claude desktop APP user starts or reviews a governed task and needs the same chat card to show whether policy-aware evaluation is available, which policies triggered, which actions/evidence are required, and what evidence is missing.
> **Runtime chain**: desktop event -> future `agent_flow.py propose` -> baseline no-write atom composition -> policy context projection -> triggered policy/action/evidence/missing-evidence projection -> same-chat card -> user review before any guarded write.
> **Canonical source**: `jikuo_policy_aware_agent_flow_contract.md`, `jikuo_configurable_rule_trigger_policy.md`, `jikuo_rule_action_evidence_model.md`, `jikuo_policy_store_configuration_flow.md`, AGENT-05 runner contract, and FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.agent_flow_proposal.v1`; policy context projection; triggered policy projection; required action projection; evidence status projection.
> **Consumer projection**: future policy-aware `agent_flow.py`, future desktop-agent cards, future MCP tool, future Skill / Plugin packaging, future frontend run-control/audit surfaces.
> **Lifecycle**: contract draft -> user review -> accepted policy-aware proposal contract -> downstream runner implementation / checker integration planning.
> **Testing layers**: documentation review, workflow/orchestration review, checker smoke, no-write smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：AGENT-07 把前面三层规则内核契约接回用户真正会看的地方：Codex / Claude 桌面 APP 聊天里的 proposal 卡片。它不做执行，只定义未来卡片怎样诚实显示 policy 状态。

The product problem:

- CORE-05 / CORE-06 / CORE-07 define policy semantics
- current `agent_flow.py propose` can render baseline no-write governance cards
- but it does not yet show policy-store status, triggered policies, required actions, or missing evidence

This slice defines how future policy-aware proposals should look.

Visible business value:

- users can see policy obligations inside the same desktop chat
- missing policy infrastructure is reported honestly as unavailable
- no policy proposal is mistaken for an active policy
- future runner / MCP / UI work has one projection contract

---

## 2. JIKUO Layer Boundary

Current layer:

- `desktop_operating_skeleton`

This slice is allowed to:

- define `jikuo.agent_flow_proposal.v1` policy-aware projection expectations
- define policy-store status projection
- define triggered policy projection
- define required action projection
- define evidence and missing-evidence projection
- define fallback behavior when policy infrastructure is unavailable
- define downstream implementation requirements for future `agent_flow.py`
- update task map, execution mounts, Sprint index, and skeleton/kernel backlog status

This slice is not allowed to:

- change CORE-05 / CORE-06 / CORE-07 kernel semantics
- modify `tools/jikuo/agent_flow.py`
- read `.jikuo/policies/`
- create `.jikuo/policies/`
- create `.jikuo/task_sessions/`
- implement policy trigger evaluation
- implement evidence checking
- execute durable writes
- install Skill / MCP / Plugin / frontend / gate behavior
- change runtime narrative-engine behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- referencing kernel ids rather than copying full policy objects by default
- treating snapshots as projections, not sources of truth
- reporting missing policy infrastructure as `unavailable`
- refusing to treat pending policy proposals as active policies
- keeping `propose` mode explicitly no-write
- preserving downstream space for checker and store adapter implementation

---

## 4. Deferred Kernel Backlog

This slice does not implement policy-aware runtime behavior.

Deferred tasks:

- policy-aware `agent_flow.py` implementation
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`
- policy store adapter implementation
- policy trigger evaluator
- policy proposal / missing-evidence card renderer

Packaging and surface tasks remain deferred:

- installable Codex Skill
- MCP tool wrapper
- Codex Plugin
- frontend rule/run-control/audit surfaces
- gate enforcement adapter

---

## 5. Scope

This work order implements:

- `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- task-map updates registering `JIKUO-AGENT-07` and the policy-aware proposal contract capability
- execution-mount updates for future policy-aware runner / MCP / Skill / Plugin / frontend work
- Sprint index entries for the work order and contract
- skeleton/kernel backlog status update
- report-only checker verification

---

## 6. Out Of Scope

This work order does not:

- modify `tools/jikuo/agent_flow.py`
- modify `tools/jikuo/agent_flow_tests.py`
- implement `jikuo.agent_flow_proposal.v1`
- implement policy store discovery
- implement policy trigger evaluation
- implement evidence checking
- persist policy snapshots
- create or update `.jikuo/policies/`
- create or update `.jikuo/task_sessions/`
- modify `.jikuo/project_state.yaml`
- implement UI / Skill / MCP / Plugin / gate adapters
- promote report-only rules into blockers
- alter runtime narrative-engine behavior

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- N/A for this slice because no runner code or schema validator is implemented.

`integration`:

- N/A because no Skill, MCP, Plugin, frontend, store adapter, checker integration, or gate integration is implemented.

`workflow / orchestration`:

- required; review that the projection chain covers policy store status -> triggered policies -> required actions -> evidence status -> missing evidence -> same-chat card.

`semantic regression`:

- N/A because this slice governs process projection, not product-output content or narrative runtime behavior.

`smoke`:

- run report-only checker against the new work order and updated planning docs.
- verify no `.jikuo/policies/` and no `.jikuo/task_sessions/` root records are created by this slice.

`human governance review`:

- required; user reviews whether policy-aware proposal cards would make rule execution visible without pretending execution exists.

---

## 9. Projection Summary

The new contract defines:

- `jikuo.agent_flow_proposal.v1`
- `policy_context`
- `policy_store_status`
- `triggered_policies`
- `required_actions`
- `evidence_status`
- `missing_evidence_reports`
- fallback behavior when policy infrastructure is unavailable
- trace requirements for policy ids, action ids, evidence ids, loop step ids, and atom ids

---

## 10. Delivery Criteria

- Policy-aware agent flow contract exists.
- Work order declares the required JIKUO layer / kernel compatibility fields.
- Proposal envelope extension is defined.
- Policy store status projection is defined.
- Triggered policy / required action / evidence / missing evidence projections are defined.
- Fallback behavior honestly reports unavailable policy infrastructure.
- Task map registers `JIKUO-AGENT-07` and a policy-aware proposal contract capability atom.
- Execution mounts point future runner, MCP, Skill, Plugin, frontend, and checker work to this contract.
- Sprint index links the work order and governance contract.
- Report-only checker validation passes.
- No `.jikuo/policies/` or `.jikuo/task_sessions/` directory is created.

---

## 11. Acceptance Gate

This slice may be accepted only if:

- the user agrees that future desktop proposal cards can expose policy state clearly
- the user agrees that unavailable policy infrastructure is shown honestly
- the user agrees that this slice does not fake policy execution
- the user agrees that implementation remains deferred to a later work order
- checker smoke passes
- no `.jikuo/policies/` or `.jikuo/task_sessions/` directory is created

Do not proceed to policy-aware `agent_flow.py` implementation, CHECKER-02, store adapter, Skill, MCP, Plugin, frontend, guarded `apply`, or gates until this contract is accepted or revised.

---

## 12. Verification Log

Commands run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-07_policy_aware_agent_flow_proposal.md --added docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-07_policy_aware_agent_flow_proposal.md
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
git diff --check -- docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-07_policy_aware_agent_flow_proposal.md docs/jikuo/governance/jikuo_productization_task_map.md docs/jikuo/governance/jikuo_execution_mounts.md docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md
```

Result:

- passed; only line-ending conversion warnings were reported for existing tracked markdown files

---

## 13. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- policy-aware `agent_flow.py` implementation
- policy trigger evaluator
- policy execution evidence checker
- policy store adapter
- policy proposal / missing-evidence card renderer
- Skill / MCP / Plugin packaging
- frontend implementation
- guarded `agent_flow.py apply`
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
