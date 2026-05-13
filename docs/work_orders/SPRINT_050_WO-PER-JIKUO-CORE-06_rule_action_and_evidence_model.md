# SPRINT_050_WO-PER-JIKUO-CORE-06: Rule Action And Evidence Model

> **Date**: 2026-05-11
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / action-evidence contract
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: desktop_operating_skeleton; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: extends CORE-05 policies with explicit action, evidence requirement, policy evidence, and missing-evidence report objects while preserving no-write proposal boundaries, future policy store, future policy-aware runner, and future gate separation
> **Deferred kernel backlog refs**: `JIKUO-CORE-07_policy_store_and_user_configuration_flow`; `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`
> **Preceded by**: CORE-05 configurable rule trigger and execution policy; ARCH-01 skeleton / kernel boundary.
> **Current slice**: action/evidence model contract only; no policy persistence, no action execution, no evidence checker, no Skill, no MCP, no Plugin, no frontend, no gate, and no automatic durable write.
> **User scenario**: A Codex / Claude desktop APP user wants triggered governance rules to show what the agent must do and what evidence proves the work was handled, instead of relying on the agent saying it complied.
> **Runtime chain**: policy triggers -> policy produces required actions -> actions declare evidence requirements -> future tools collect policy evidence -> missing evidence report is projected into chat / checker / future UI.
> **Canonical source**: `jikuo_rule_action_evidence_model.md`, `jikuo_configurable_rule_trigger_policy.md`, `jikuo_skeleton_kernel_boundary_and_backlog.md`, `jikuo_execution_mounts.md`, and `jikuo_productization_task_map.md`.
> **Bridge object**: `jikuo.policy_action.v0`; `jikuo.evidence_requirement.v0`; `jikuo.policy_evidence.v0`; `jikuo.missing_evidence_report.v0`
> **Consumer projection**: future policy-aware `agent_flow.py`, future desktop-agent cards, future checker evidence reports, future task-session sidecar records, future MCP tool, future frontend audit surfaces, and later gate adapters after explicit approval.
> **Lifecycle**: contract draft -> user review -> accepted action/evidence model -> downstream CORE-07 / AGENT-07 / CHECKER-02 implementation planning.
> **Testing layers**: documentation review, workflow/orchestration review, checker smoke, no-write smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：CORE-06 的业务意义是把“规则触发后应该做什么”拆成可检查对象。它不是让 Agent 多写承诺，而是让未来工具能指出：哪条 action 已完成、哪条 evidence 缺失、哪一步需要用户批准。

The product problem:

- CORE-05 can say a policy triggered and requires actions/evidence
- but action and evidence need their own object model before tools can inspect compliance
- otherwise JIKUO would still depend on natural-language claims like "I reviewed it"

This slice defines the shared action/evidence contract.

Visible business value:

- triggered rules can become checklists with evidence requirements
- desktop cards can show missing evidence without a frontend
- future checker can compare requirements against produced evidence
- future task-session records can store compact process evidence without raw chat logs
- write actions can expose write effect, non-effect, and approval requirement

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- define `jikuo.policy_action.v0`
- define `jikuo.evidence_requirement.v0`
- define `jikuo.policy_evidence.v0`
- define `jikuo.missing_evidence_report.v0`
- define first action type catalog
- define evidence status vocabulary
- define satisfaction matching rules
- define desktop card projection expectations
- update task map, execution mounts, Sprint index, and skeleton/kernel backlog status

This slice is not allowed to:

- implement action execution
- implement evidence persistence
- implement policy-aware `agent_flow.py`
- implement policy execution evidence checker
- install a Codex Skill
- implement MCP, Plugin, frontend, or gates
- edit `.codex/AGENTS.md`
- create `.jikuo/task_sessions/`
- change runtime narrative-engine behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

This slice preserves future kernel compatibility by:

- keeping action execution status separate from evidence status
- requiring actions to declare target, write effect, non-effect, and approval boundary
- requiring evidence to reference policy/action/requirement ids
- allowing manual evidence while marking it `review_required` unless tooling can verify it
- keeping missing-evidence reports usable in desktop APP chat before frontend exists
- keeping report-only severity separate from future gate enforcement

---

## 4. Deferred Kernel Backlog

This slice does not complete the configurable rule kernel.

Deferred tasks:

- `JIKUO-CORE-07_policy_store_and_user_configuration_flow`
- `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`

Packaging and surface tasks remain deferred:

- installable Codex Skill
- MCP tool wrapper
- Codex Plugin
- frontend rule configuration / audit console
- gate enforcement adapter

---

## 5. Scope

This work order implements:

- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- task-map updates registering `JIKUO-CORE-06` and the new action/evidence capability
- execution-mount updates for future action/evidence and checker work
- Sprint index entries for the work order and model contract
- skeleton/kernel backlog status update
- report-only checker verification

---

## 6. Out Of Scope

This work order does not:

- execute policy actions
- persist evidence
- add action/evidence records to `.jikuo/project_state.yaml`
- create `.jikuo/task_sessions/`
- modify `tools/jikuo/agent_flow.py`
- modify `tools/audit/check_rule_registry.py`
- implement policy evidence checking
- implement UI / Skill / MCP / Plugin / gate adapters
- promote report-only rules into blockers
- alter runtime narrative-engine behavior

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- N/A for this slice because no executable action/evidence checker is implemented.

`integration`:

- N/A because no Skill, MCP, Plugin, frontend, storage adapter, or policy-aware runner is implemented.

`workflow / orchestration`:

- required; review that the model covers policy action -> evidence requirement -> produced evidence -> satisfaction -> missing evidence report.

`semantic regression`:

- N/A because this slice governs process policy evidence, not product-output content or narrative runtime behavior.

`smoke`:

- run report-only checker against the new work order and updated planning docs.
- verify no `.jikuo/task_sessions/` root record is created by this slice.

`human governance review`:

- required; user reviews whether the model makes triggered policy compliance inspectable without over-implementing the execution layer.

---

## 9. Model Summary

The new model defines:

- `jikuo.policy_action.v0`
- `jikuo.evidence_requirement.v0`
- `jikuo.policy_evidence.v0`
- `jikuo.missing_evidence_report.v0`
- first action type catalog
- evidence status vocabulary
- evidence satisfaction matching rules
- desktop card projection requirements
- compact retention and privacy boundary

---

## 10. Delivery Criteria

- Action/evidence model document exists.
- Work order declares the required JIKUO layer / kernel compatibility fields.
- Action object, evidence requirement object, policy evidence object, and missing evidence report object are defined.
- Action type catalog and evidence status vocabulary are defined.
- Evidence satisfaction rules distinguish `ok`, `review_required`, `missing`, `not_applicable`, `failed`, and `error`.
- Task map registers `JIKUO-CORE-06` and a new action/evidence capability atom.
- Execution mounts point future action/evidence, policy-aware runner, checker, and UI work to the new model.
- Sprint index links the work order and governance model.
- Report-only checker validation passes.
- No task-session sidecar write occurs.

---

## 11. Acceptance Gate

This slice may be accepted only if:

- the user agrees that triggered policy compliance is now inspectable at contract level
- the user agrees that actions and evidence are separated clearly
- the user agrees that missing evidence can be reported without becoming a gate
- the user agrees that the slice stays at contract level and does not fake execution
- checker smoke passes
- no `.jikuo/task_sessions/` directory is created

Do not proceed to CORE-07, AGENT-07, CHECKER-02, Skill, MCP, Plugin, frontend, guarded `apply`, or gates until this contract is accepted or revised.

---

## 12. Verification Log

Commands run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-06_rule_action_and_evidence_model.md --added docs/jikuo/governance/jikuo_rule_action_evidence_model.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-06_rule_action_and_evidence_model.md
```

Result:

- registry validation passed
- rule count: 9
- triggered `R-006`, `R-012`, and `R-013`
- `R-006` required work-order fields and sections reported `OK`
- `R-012` Sprint index document requirement reported `OK`; manual `sprint_index_entry` declaration remained `REVIEW`, as expected for report-only manual evidence
- `R-013` layer / kernel fields and sections reported `OK`; manual `skeleton_kernel_boundary_declaration` remained `REVIEW`, as expected for report-only manual evidence

```powershell
Test-Path -Path .jikuo\task_sessions
```

Result:

- returned `False`; no task-session sidecar root was created by this slice

```powershell
git diff --check -- docs/jikuo/governance/jikuo_rule_action_evidence_model.md docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-06_rule_action_and_evidence_model.md docs/jikuo/governance/jikuo_productization_task_map.md docs/jikuo/governance/jikuo_execution_mounts.md docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md
```

Result:

- passed; only line-ending conversion warnings were reported for existing tracked markdown files

---

## 13. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- policy/action/evidence persistence
- policy-aware `agent_flow.py`
- policy execution evidence checker
- user configuration UI
- Skill / MCP / Plugin packaging
- guarded `agent_flow.py apply`
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
