# JIKUO Configurable Rule Trigger Policy

> **Date**: 2026-05-11
> **Status**: Draft kernel policy contract / no runtime implementation
> **Purpose**: define how configurable user rules become triggerable, reviewable process policies before policy execution code, storage, UI, Skill, MCP, Plugin, or gates are implemented.
> **Primary user surface**: Codex / Claude desktop APP chat.
> **JIKUO layer**: configurable_rule_kernel
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 中文摘要

这份文档解决机括最初的问题：用户把重要规则写进 AGENTS、设计文档、sprint 文档或聊天偏好里，但 Agent 执行时靠“记得”，所以遵循概率不稳定。

本契约的目标不是立刻实现自动执行，而是先定义一条清晰链路：

- 用户规则偏好、项目文档、场景包默认规则进入 policy candidate。
- policy candidate 经用户批准后，成为可触发 policy。
- policy 触发后，必须产生 required actions 和 required evidence。
- Agent / checker / future MCP / frontend 只消费 policy projection，不重新解释长文档。
- 任何 gate 或 blocking enforcement 都必须另开工单，并保留 rollback / override 路径。

本阶段只定义规则内核的触发与执行策略契约，不实现 policy store、policy-aware `agent_flow.py`、MCP、Skill、Plugin、frontend 或 gate。

---

## 2. Product Meaning

JIKUO should not rely on an AI agent remembering long instructions.

Important process rules should become explicit policy objects that can be:

- triggered by known events
- mapped to required actions
- checked for required evidence
- rendered back to the user in desktop APP chat
- approved, revised, deprecated, or promoted through an auditable lifecycle

For ordinary users, this means:

- they can state working-method preferences in natural language
- they can attach required reference files without editing raw YAML
- the agent can propose a structured rule candidate
- later tool-backed flows can show exactly why a rule triggered and what evidence is missing

This policy contract is the bridge between the current desktop operating skeleton and the future rule execution kernel.

---

## 3. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This contract is allowed to define:

- policy source types
- trigger source types
- condition vocabulary
- required action vocabulary
- required evidence vocabulary
- document mount semantics inside policies
- approval and lifecycle boundaries
- projection surfaces for desktop agent, checker, MCP, frontend, and gates

This contract is not allowed to:

- persist approved policies
- implement automatic policy execution
- implement policy-aware `agent_flow.py`
- implement a Skill, MCP tool, Plugin, frontend, or gate
- edit `.codex/AGENTS.md`
- turn report-only obligations into blocking enforcement
- judge product-output quality or domain content quality

---

## 4. Kernel Compatibility

This policy contract must remain compatible with:

- `JIKUO-FLOW-02` Desktop App Primary Operating Loop
- `JIKUO-AGENT-04` desktop invocation contract
- `JIKUO-AGENT-05` no-write `agent_flow.py propose`
- `JIKUO-AGENT-06` project-local instruction pack
- `JIKUO-ARCH-01` skeleton / kernel boundary
- future `JIKUO-CORE-06` required action and evidence model
- future `JIKUO-CORE-07` policy store and user configuration flow
- future `JIKUO-AGENT-07` policy-aware proposal cards
- future `JIKUO-CHECKER-02` policy execution evidence checker

Compatibility requirements:

- skeleton event names must be addressable as policy triggers
- policy output must be projectable into same-chat cards
- required actions must be distinguishable from evidence that proves the actions happened
- document mounts must be first-class policy inputs, not buried in prose
- every durable policy change must require explicit user approval
- every enforcement promotion must remain separate from policy definition

---

## 5. Deferred Kernel Backlog

This document only completes the first contract slice for:

- `JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy`

Still deferred:

- `JIKUO-CORE-06_rule_action_and_evidence_model`
- `JIKUO-CORE-07_policy_store_and_user_configuration_flow`
- `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`
- installable Codex Skill packaging
- MCP tool wrapper
- Codex Plugin
- frontend rule configuration console
- gate enforcement adapter

---

## 6. Policy Source Types

A policy may be proposed from one or more sources.

| Source Type | Meaning | User-Friendly Path | Canonical Risk |
|---|---|---|---|
| `kernel_default` | built-in JIKUO process rule | bundled with JIKUO | must not become engineering-only |
| `scenario_package_default` | default rule for an application package, such as engineering governance | selected package | must not redefine kernel semantics |
| `project_registry` | approved project-local policy / registry entry | existing project config | must preserve version and approval history |
| `user_natural_language` | user states a working-method preference in chat | agent proposes candidate card | must not become active without approval |
| `required_reference_file` | user names a file that must be consulted for a task class | document mount proposal | must distinguish trigger from reference |
| `work_order_contract` | a work order declares required sections, references, or lifecycle | work-order metadata | must not silently affect unrelated tasks |
| `design_doc_contract` | a design doc defines process obligations | mounted design reference | must be scoped to declared task class |
| `agent_instruction_doc` | existing AGENTS / CLAUDE / instruction file contains process rules | import/proposal flow | must avoid blindly importing long prose |

Important distinction:

- a source explains where a policy candidate came from
- a trigger explains when a policy should fire
- a document mount explains what must be read, referenced, or updated once the policy fires

---

## 7. Trigger Source Types

Triggers are explicit signals. They should be cheap for tools to detect and easy for users to understand.

| Trigger Type | Example Signal | Intended Use |
|---|---|---|
| `explicit_user_invocation` | user says `"<exact user phrase as spoken>"` | user deliberately starts JIKUO or asks for governed mode |
| `agent_suggested_event` | agent notices task start, completion, handoff, or rule preference | agent asks whether to run JIKUO flow |
| `task_lifecycle_event` | `task_start`, `mid_task_review`, `pre_delivery`, `handoff` | lifecycle-bound policies such as three-phase audit |
| `changed_path_match` | a changed path matches `src/**` or `docs/**` | file-surface policies |
| `added_path_match` | a new work order or schema file is added | template/index policies |
| `document_mount_presence` | a task session has required references mounted | policies that depend on mounted docs |
| `work_order_metadata_match` | work order declares `Task type`, `JIKUO layer`, or testing layers | work-order governance policies |
| `checker_result` | report-only checker reports missing evidence | follow-up evidence policies |
| `approval_event` | user approves a policy candidate or guarded write | durable-change policies |

Trigger rules:

- critical policies should have at least one deterministic trigger
- pure natural-language memory is not a trigger by itself
- agent-suggested triggers may improve smoothness but must not be the only path for critical obligations
- document references are not automatically triggers unless explicitly configured as such

---

## 8. Policy Condition Vocabulary

Conditions narrow a trigger.

Recommended first vocabulary:

- `task_type_is`
- `jikuo_layer_is`
- `changed_path_matches`
- `added_path_matches`
- `required_reference_mounted`
- `work_order_field_present`
- `work_order_section_present`
- `task_session_exists`
- `task_session_state_is`
- `approval_phrase_present`
- `checker_obligation_status_is`
- `enforcement_phase_is`

Condition rules:

- conditions must be inspectable from declared task metadata, changed paths, sidecar state, checker output, or explicit user approval
- conditions should not require the agent to infer user mood, product quality, or domain-content quality
- ambiguous conditions should produce `review_required`, not automatic execution

---

## 9. Required Action Vocabulary

Required actions are what the agent or tool must do after a policy triggers.

First-slice action vocabulary:

- `read_reference`
- `render_pre_task_review`
- `render_mid_task_review`
- `render_pre_delivery_review`
- `run_report_only_checker`
- `run_declared_test`
- `record_evidence_snapshot`
- `record_verification_snapshot`
- `ask_user_for_approval`
- `propose_policy_candidate`
- `propose_document_mount`
- `update_declared_document`
- `prepare_handoff_summary`

Action rules:

- required actions must be explicit enough to become checklist items
- action execution and durable writes are separate concepts
- actions that write files or state must declare approval boundary and non-effect
- an action may be satisfied manually, but the evidence must say so

---

## 10. Required Evidence Vocabulary

Required evidence proves that a triggered policy was handled.

First-slice evidence vocabulary:

- `reference_read`
- `card_rendered`
- `checker_result`
- `test_result`
- `document_updated`
- `document_reviewed`
- `approval_recorded`
- `task_session_evidence_appended`
- `handoff_recorded`
- `exemption_declared`
- `not_applicable_reason`

Evidence rules:

- evidence should name the policy id and action id it satisfies
- evidence should include enough compact detail to audit the process without storing raw chat logs
- exact user approval phrases should be recorded as `"<exact user phrase as spoken>"`
- missing evidence should be reportable before any blocking gate exists

---

## 11. Document Mount Policy

Document mounts are first-class policy inputs.

A user may say that a task class must reference specific files. JIKUO should treat this as a policy candidate with required reference mounts.

Example user statement:

`"<exact user phrase as spoken>"`

Policy interpretation:

- source type: `user_natural_language`
- trigger type: `task_lifecycle_event`
- condition: `task_type_is: work_order_delivery`
- required actions:
  - `read_reference`
  - `render_pre_task_review`
  - `render_mid_task_review`
  - `render_pre_delivery_review`
- document mounts:
  - sprint file
  - AGENTS / project instruction file or extracted rule subset
  - related design document
  - related work order
- required evidence:
  - `reference_read`
  - `card_rendered`
  - `checker_result`
  - `document_updated` when the policy requires document sync

Document mount rules:

- a mounted document may be a source, a required reference, an evidence carrier, an output target, or a handoff reference
- these roles must not be collapsed into one vague "context" field
- future UI should let users add mounts without editing raw YAML
- future desktop-agent cards should show why a mounted file is required

---

## 12. Bridge Object: `jikuo.configurable_rule_policy.v0`

Minimal shape:

```yaml
schema_version: "jikuo.configurable_rule_policy.v0"
policy_id: "POLICY-..."
version: 1
status: "draft_candidate | approved_report_only | active_report_only | deprecated | superseded"
title: "..."
scenario_package: "engineering_governance"
source_refs:
  - type: "user_natural_language"
    ref: "<exact user phrase as spoken>"
scope:
  project_id: "..."
  task_types:
    - "work_order_delivery"
triggers:
  - trigger_id: "TRG-..."
    type: "task_lifecycle_event"
    event: "pre_delivery"
conditions:
  - type: "task_type_is"
    value: "work_order_delivery"
document_mounts:
  - mount_id: "DOC-..."
    role: "required_reference"
    layer: "work_order"
    path: "docs/..."
required_actions:
  - action_id: "ACT-..."
    type: "render_pre_delivery_review"
    approval_required: false
required_evidence:
  - evidence_id: "EVD-..."
    type: "card_rendered"
    satisfies_action: "ACT-..."
enforcement:
  phase: "report_only"
  level: "review_required"
lifecycle:
  created_from: "policy_candidate"
  approved_by: null
  supersedes: []
projection:
  desktop_card: true
  checker: true
  frontend: true
```

Rules:

- the policy object is a bridge contract, not the storage format yet
- approved storage location is deferred to `JIKUO-CORE-07`
- action/evidence details may be expanded by `JIKUO-CORE-06`
- `agent_flow.py` may later project triggered policies, but this document does not implement that projection

---

## 13. Enforcement Phase Policy

Policy definition and enforcement promotion are separate.

Allowed first phases:

- `draft_candidate`
- `approved_report_only`
- `active_report_only`
- `local_gate_candidate`
- `approval_gate_candidate`
- `deprecated`
- `superseded`

Promotion rules:

- no policy starts as blocking
- report-only false positives should be observed before promotion
- promotion requires explicit user approval and rollback plan
- override and recovery path must exist before blocking enforcement
- engineering package policies must not redefine the process kernel

---

## 14. Desktop-Agent Projection

Future desktop cards should be able to show:

- policy id and title
- why it triggered
- required actions
- required document mounts
- satisfied evidence
- missing evidence
- whether approval is required
- exact target and non-effect for any proposed write
- next suggested action

Current implementation status:

- no current tool projects this policy contract yet
- current `agent_flow.py propose` may remain no-write and policy-unaware until `JIKUO-AGENT-07`
- this document only reserves the projection shape

---

## 15. Non-Goals

This contract does not implement:

- policy candidate extraction from AGENTS / CLAUDE / long docs
- policy persistence
- policy-aware `agent_flow.py`
- automatic action execution
- evidence checking
- UI configuration
- Skill / MCP / Plugin packaging
- gate enforcement
- narrative-engine runtime behavior
- product-output quality review

---

## 16. Acceptance Rule

This contract is acceptable if it makes the following clear:

- how user rules become structured policy candidates
- how approved policies can later trigger deterministically
- how required references differ from triggers
- how required actions differ from evidence
- why current skeleton work remains compatible with the future rule kernel
- which later tasks must implement store, execution, evidence checking, projection, and UI

