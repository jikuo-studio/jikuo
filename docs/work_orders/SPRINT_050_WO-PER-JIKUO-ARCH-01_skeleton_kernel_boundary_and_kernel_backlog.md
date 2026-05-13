# SPRINT_050_WO-PER-JIKUO-ARCH-01: Skeleton / Kernel Boundary And Kernel Backlog

> **Date**: 2026-05-09  
> **Status**: Implemented, ready for user review  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / architecture boundary / report-only checker rule  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **JIKUO layer**: desktop_operating_skeleton  
> **Current slice is not**: configurable_rule_kernel; packaging_surface; frontend_surface; gate_enforcement  
> **Kernel compatibility**: preserve trigger/event abstraction, no-write proposal boundary, approval boundary, future policy refs / triggered rules / required actions / missing evidence hook points  
> **Deferred kernel backlog refs**: `JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy`; `JIKUO-CORE-06_rule_action_and_evidence_model`; `JIKUO-CORE-07_policy_store_and_user_configuration_flow`; `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`  
> **Preceded by**: AGENT-04 desktop invocation contract; AGENT-05 no-write runner; AGENT-06 project-local instruction pack; user clarification that JIKUO's original problem is probabilistic AGENTS-rule execution.  
> **Current slice**: boundary document, required mount update, backlog declaration, and report-only registry rule only.  
> **User scenario**: A user and desktop agent continue building JIKUO's invocation skeleton, but need a reliable reminder that the skeleton is not the configurable rule kernel and that future kernel compatibility must remain visible.  
> **Runtime chain**: JIKUO work begins -> execution mounts include skeleton/kernel boundary -> work order declares layer metadata -> report-only checker reports missing layer/kernel declarations -> user reviews whether the task stayed within its layer.  
> **Canonical source**: `jikuo_skeleton_kernel_boundary_and_backlog.md`, `jikuo_execution_mounts.md`, `jikuo_productization_task_map.md`, and `rule_registry.yaml`.  
> **Bridge object**: `jikuo.skeleton_kernel_boundary.v0`; `R-013` report-only rule.  
> **Consumer projection**: future JIKUO work orders, report-only checker output, future `agent_flow.py` policy-aware card projection, future Skill / MCP / plugin packaging.  
> **Lifecycle**: boundary contract -> mounted for future JIKUO tasks -> report-only checker reports missing declarations -> later kernel work may supersede backlog items explicitly.  
> **Testing layers**: documentation review, workflow/orchestration review, checker smoke, no-write smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：这一任务不是规则内核实现，而是给机括开发过程加一个“层级罗盘”。它让我们每次做 JIKUO 工单时都先声明：现在是在搭骨架、做内核、做包装、做前端，还是做 gate。

The original product problem:

- users put many rules into AGENTS / long docs
- AI follows them probabilistically
- important audit, testing, and process rules are missed

The current product risk:

- while building the desktop operating skeleton, we may forget that the configurable rule kernel is still pending
- or we may accidentally implement kernel behavior inside skeleton / packaging work without an explicit contract

This slice creates a visible boundary and a report-only checker reminder.

Visible product effect:

- future JIKUO work orders must say which layer they are working on
- skeleton work must preserve compatibility with future rule-kernel hooks
- pending kernel backlog remains visible instead of becoming conversational memory

---

## 2. JIKUO Layer Boundary

Current layer:

- `desktop_operating_skeleton`

This slice is allowed to:

- document skeleton / kernel boundaries
- register pending kernel backlog
- update execution mounts and task map
- add a report-only checker rule requiring layer/kernel declarations

This slice is not allowed to:

- implement configurable user policies
- persist user-defined rules
- infer required actions from user rules
- enforce triggered rules
- implement installable Skill / MCP / Plugin / frontend / gate behavior

---

## 3. Kernel Compatibility

This slice preserves future kernel compatibility by requiring future JIKUO work to declare:

- current JIKUO layer
- what layer is explicitly out of scope
- how the current slice keeps hook points open for policy refs / triggered rules / required actions / missing evidence
- which kernel backlog refs remain deferred

Compatibility notes:

- skeleton trigger/event names should remain policy-addressable
- proposal/card outputs should remain extendable with rule-trigger evidence
- approval boundaries should remain explicit before write behavior is added
- packaging layers should not fork semantics from the skeleton or future kernel

---

## 4. Deferred Kernel Backlog

Deferred configurable-rule-kernel tasks:

- `JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy`
- `JIKUO-CORE-06_rule_action_and_evidence_model`
- `JIKUO-CORE-07_policy_store_and_user_configuration_flow`
- `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`

These are not implemented in this slice.

---

## 5. Scope

This work order implements:

- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `R-013` report-only registry rule
- `tools/audit/check_rule_registry_json_output_tests.py` expectation update for the new `R-013` obligation
- task-map updates
- execution-mount updates
- Sprint index updates
- verification that no task-session sidecar write occurred

---

## 6. Out Of Scope

This work order does not:

- implement the configurable rule kernel
- implement user custom policy configuration
- implement rule execution actions
- implement policy persistence
- implement policy-aware `agent_flow.py`
- install a Codex Skill
- implement MCP, Plugin, frontend, or gates
- implement guarded `agent_flow.py apply`
- edit `.codex/AGENTS.md`
- create `.jikuo/task_sessions/`
- update `.jikuo/project_state.yaml`
- change runtime narrative engine behavior

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-06_lightweight_desktop_agent_instruction_pack.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `tools/audit/check_rule_registry.py`

---

## 8. Testing Governance Declaration

`unit`:

- `tools/audit/check_rule_registry_json_output_tests.py` should pass after updating expected triggered obligations to include `R-013`.

`integration`:

- N/A because no Skill, MCP, Plugin, frontend, or gate integration is implemented.

`workflow / orchestration`:

- run report-only checker against this new work order and confirm `R-013` reports the new layer/kernel fields as present.

`semantic regression`:

- N/A because this slice governs JIKUO process architecture, not narrative product output.

`smoke`:

- verify `.jikuo/task_sessions/` is still absent.
- verify `.jikuo/project_state.yaml` `latest_task_session_refs` remains empty.

`human governance review`:

- user reviews whether the boundary/backlog is enough to keep skeleton work and kernel work separated.

---

## 9. Delivery Criteria

- Boundary/backlog document exists.
- Execution mounts include the boundary document in the required mount set.
- Task map registers the boundary document and kernel backlog.
- `rule_registry.yaml` includes a report-only rule for future JIKUO layer/kernel declarations.
- Sprint index links the new work order and boundary document.
- No durable sidecar write occurs.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- the user agrees that it distinguishes skeleton work from configurable-rule-kernel work
- the user agrees that the deferred kernel backlog is visible enough
- report-only checker validation passes
- `R-013` reports this work order's layer/kernel fields as `OK`
- no task-session sidecar is created

Do not proceed to configurable rule kernel, installable Skill, MCP wrapper, Plugin, frontend, guarded `apply`, or gate implementation until the user accepts or revises this boundary.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/audit/check_rule_registry_json_output_tests.py
```

Result:

- passed, 3 tests
- JSON / text checker tests now expect `R-013` for JIKUO work-order additions

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-01_skeleton_kernel_boundary_and_kernel_backlog.md --changed docs/scenarios/interactive_novel/governance/rule_registry.yaml --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --changed tools/audit/check_rule_registry_json_output_tests.py --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-01_skeleton_kernel_boundary_and_kernel_backlog.md
```

Result:

- registry validation passed
- rule count: 9
- `R-006` required work-order fields and sections reported `OK`
- `R-012` Sprint index document requirement reported `OK`
- `R-013` layer / kernel fields and sections reported `OK`
- `R-013` manual declaration remained `REVIEW`, as expected for report-only manual evidence

No-write state checks:

- root `.jikuo/task_sessions/` remained absent
- `.jikuo/project_state.yaml` still had `latest_task_session_refs: []`

---

## 12. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- configurable rule kernel implementation
- user custom policy configuration
- policy-aware `agent_flow.py`
- policy execution checker
- installable Codex Skill
- MCP tool wrapper
- Codex Plugin
- frontend implementation
- guarded `agent_flow.py apply`
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
