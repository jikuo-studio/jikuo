# SPRINT_050_WO-PER-JIKUO-CORE-05: Configurable Rule Trigger And Execution Policy

> **Date**: 2026-05-11
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / policy contract
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: desktop_operating_skeleton; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: defines policy trigger / action / evidence vocabulary while preserving desktop-agent projection, no-write proposal boundaries, future policy store, future evidence checker, and future gate promotion separation
> **Deferred kernel backlog refs**: `JIKUO-CORE-06_rule_action_and_evidence_model`; `JIKUO-CORE-07_policy_store_and_user_configuration_flow`; `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`
> **Preceded by**: AGENT-04 desktop invocation contract; AGENT-05 no-write runner; AGENT-06 project-local instruction pack; ARCH-01 skeleton / kernel boundary.
> **Current slice**: policy trigger and execution semantics contract only; no policy persistence, no policy-aware runner, no Skill, no MCP, no Plugin, no frontend, no gate, and no automatic durable write.
> **User scenario**: A Codex / Claude desktop APP user wants project rules, required reference files, audit habits, testing rules, and delivery obligations to trigger reliably instead of depending on whether the AI remembers long AGENTS-style instructions.
> **Runtime chain**: user or mounted docs express a rule preference -> agent proposes a policy candidate -> user approves later in a guarded flow -> future task lifecycle / changed paths / document mounts trigger the policy -> required actions and evidence are projected into chat / checker / future UI.
> **Canonical source**: `jikuo_configurable_rule_trigger_policy.md`, `jikuo_skeleton_kernel_boundary_and_backlog.md`, `jikuo_execution_mounts.md`, and `jikuo_productization_task_map.md`.
> **Bridge object**: `jikuo.configurable_rule_policy.v0`
> **Consumer projection**: future policy-aware `agent_flow.py`, future desktop-agent cards, future checker evidence reports, future MCP tool, future frontend configuration / audit surfaces, and later gate adapters after explicit approval.
> **Lifecycle**: contract draft -> user review -> accepted trigger policy contract -> downstream CORE-06 / CORE-07 / AGENT-07 / CHECKER-02 implementation planning.
> **Testing layers**: documentation review, workflow/orchestration review, checker smoke, no-write smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：这一块开始触碰机括真正的“规则内核”。它回答：用户说过的规则、要求挂载的文件、AGENTS 里的方法论，未来怎样从长文档概率执行，变成可触发、可检查、可批准、可演进的 policy。

The product problem:

- users already write important rules in AGENTS, sprint docs, design docs, and chat
- AI agents may follow those rules probabilistically
- the current desktop operating skeleton can start JIKUO flows, but it does not yet know how a configurable user rule becomes a triggered obligation

This slice defines the first policy contract that future tooling can implement.

Visible business value:

- required reference files become a policy feature, not a reminder hidden in prose
- lifecycle audits can become triggered required actions, not vague instructions
- future desktop cards can explain why a rule triggered and what evidence is missing
- future UI can configure rules without making ordinary users edit raw YAML

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- define configurable policy source types
- define trigger source types
- define policy condition vocabulary
- define required action vocabulary
- define required evidence vocabulary
- define document mount semantics in policies
- define `jikuo.configurable_rule_policy.v0`
- update task map, execution mounts, Sprint index, and skeleton/kernel backlog status

This slice is not allowed to:

- implement policy persistence
- implement policy-aware `agent_flow.py`
- automatically execute policy actions
- check policy evidence
- install a Codex Skill
- implement MCP, Plugin, frontend, or gates
- edit `.codex/AGENTS.md`
- create `.jikuo/task_sessions/`
- change runtime narrative-engine behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

The contract preserves compatibility with the existing skeleton by:

- treating desktop lifecycle events as future policy triggers
- keeping required actions separate from evidence
- keeping document mounts first-class and inspectable
- requiring explicit approval before any future durable policy change
- keeping report-only policy definition separate from later gate promotion
- reserving projection fields for future desktop cards and checker output

Future implementation work should not reinterpret this contract through free-form prose. It should consume explicit policy fields.

---

## 4. Deferred Kernel Backlog

This slice does not complete the configurable rule kernel.

Deferred tasks:

- `JIKUO-CORE-06_rule_action_and_evidence_model`
- `JIKUO-CORE-07_policy_store_and_user_configuration_flow`
- `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`

Packaging and surface tasks remain deferred:

- installable Codex Skill
- MCP tool wrapper
- Codex Plugin
- frontend rule configuration console
- gate enforcement adapter

---

## 5. Scope

This work order implements:

- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- task-map updates registering `JIKUO-CORE-05` and the new policy capability
- execution-mount updates for future configurable-rule-kernel work
- Sprint index entries for the work order and policy contract
- skeleton/kernel backlog status update
- report-only checker verification

---

## 6. Out Of Scope

This work order does not:

- parse AGENTS / CLAUDE / long docs into policy candidates
- persist approved policies
- implement user configuration UI
- implement policy-aware `agent_flow.py`
- implement policy evidence checking
- implement automatic document reading / updating
- implement guarded `agent_flow.py apply`
- install Skill / MCP / Plugin packaging
- promote any rule to a blocking gate
- edit `.codex/AGENTS.md`
- create or update task-session sidecar records
- alter runtime narrative-engine behavior

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- N/A for this slice because no executable policy engine is implemented.

`integration`:

- N/A because no Skill, MCP, Plugin, frontend, storage adapter, or policy-aware runner is implemented.

`workflow / orchestration`:

- required; review that the policy chain covers source -> trigger -> condition -> required action -> required evidence -> projection -> lifecycle.

`semantic regression`:

- N/A because this slice governs process policy semantics, not product-output content or narrative runtime behavior.

`smoke`:

- run report-only checker against the new work order and updated planning docs.
- verify no `.jikuo/task_sessions/` root record is created by this slice.

`human governance review`:

- required; user reviews whether the contract correctly addresses probabilistic rule execution without over-implementing the kernel.

---

## 9. Policy Contract Summary

The new policy contract defines:

- policy source types such as `user_natural_language`, `required_reference_file`, `work_order_contract`, and `agent_instruction_doc`
- trigger source types such as `task_lifecycle_event`, `changed_path_match`, `document_mount_presence`, and `checker_result`
- policy conditions such as `task_type_is`, `jikuo_layer_is`, and `required_reference_mounted`
- required actions such as `read_reference`, `render_pre_task_review`, `render_mid_task_review`, `render_pre_delivery_review`, and `run_report_only_checker`
- required evidence such as `reference_read`, `card_rendered`, `checker_result`, `test_result`, and `document_updated`
- a bridge object named `jikuo.configurable_rule_policy.v0`

---

## 10. Example Policy Interpretation

User statement:

`"<exact user phrase as spoken>"`

Possible policy candidate:

- source: user natural language
- trigger: task lifecycle event
- condition: work-order delivery
- required references: sprint file, instruction file or extracted rule subset, related design doc, related work order
- required actions: pre-task review, mid-task review, pre-delivery review
- required evidence: card rendered, reference read, checker result, document update when required
- enforcement: report-only until separately promoted

This is an example of policy interpretation, not a fixed command phrase the user must say.

---

## 11. Delivery Criteria

- Policy contract document exists.
- Work order declares the required JIKUO layer / kernel compatibility fields.
- Policy source, trigger, condition, action, evidence, document mount, lifecycle, and projection semantics are defined.
- Task map registers `JIKUO-CORE-05` and a new policy-trigger capability atom.
- Execution mounts point future configurable-rule-kernel work to the new policy contract.
- Sprint index links the work order and governance contract.
- Report-only checker validation passes.
- No task-session sidecar write occurs.

---

## 12. Acceptance Gate

This slice may be accepted only if:

- the user agrees that the policy contract addresses the original "AI follows rules probabilistically" problem
- the user agrees that required reference files are represented as document mounts rather than vague context
- the user agrees that the slice stays at contract level and does not fake policy execution
- checker smoke passes
- no `.jikuo/task_sessions/` directory is created

Do not proceed to CORE-06, CORE-07, AGENT-07, CHECKER-02, Skill, MCP, Plugin, frontend, guarded `apply`, or gates until this contract is accepted or revised.

---

## 13. Verification Log

Commands run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy.md --added docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy.md
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
git diff --check -- docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy.md docs/jikuo/governance/jikuo_productization_task_map.md docs/jikuo/governance/jikuo_execution_mounts.md docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md
```

Result:

- passed; only line-ending conversion warnings were reported for existing tracked markdown files

---

## 14. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- policy persistence
- policy-aware `agent_flow.py`
- action/evidence execution model implementation
- policy evidence checker
- user configuration UI
- Skill / MCP / Plugin packaging
- guarded `agent_flow.py apply`
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
