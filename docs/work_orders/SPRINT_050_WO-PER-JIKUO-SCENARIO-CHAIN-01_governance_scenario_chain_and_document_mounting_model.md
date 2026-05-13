# SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01: Governance Scenario Chain And Document Mounting Model

> **Date**: 2026-05-04  
> **Status**: Accepted by user for downstream CORE-03 planning  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / scenario-chain audit / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`; `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`; `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`; `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`; `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`; `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`  
> **Current slice**: common governance scenario chains and document mounting model only; no frontend, CLI, adapter, checker, gate, registry migration, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user needs JIKUO to decide which governance chain is active, which rules apply, which reference documents must be consulted, and which evidence must be produced for a task.  
> **Runtime chain**: user/task intent -> scenario classification -> rule trigger resolution -> document mount resolution -> evidence obligation rendering -> task execution -> completion review -> acceptance/handoff/audit trail.  
> **Canonical source**: accepted JIKUO product definition, desktop-agent-first contract, structured result model, UI-ready registry view-model schema, FLOW-01 draft, and current report-only checker baseline.  
> **Bridge object**: `JikuoGovernanceScenarioChainV0`; `JikuoDocumentMountV0`.  
> **Consumer projection**: desktop-agent governance cards, future task-session records, future auxiliary CLI reports, future frontend configuration/control/audit views, and future rule-candidate proposal cards.  
> **Lifecycle**: scenario-chain draft -> user review -> accepted chain contract -> later FLOW-01 adjustment if needed -> CORE-03 task-session model and adapter/UI planning.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张文档回答“机括自己如何按场景链路被设计”，以及“用户指定的必读文档如何挂到正确层级”。

JIKUO is being built to govern AI-primary work. That creates a self-bootstrap requirement:

- the narrative engine hardening work needs JIKUO-style governance
- JIKUO itself must also be designed through scenario chains and auditable primitives
- users must be able to mount required reference documents onto the right layer of a rule or task

The risk is recursive overbuild:

- building a governance product before the governed work can continue
- turning every product question into another meta-governance feature
- mixing user-facing product flow, registry schema, checker behavior, frontend UI, and gate behavior in one step

This work order avoids that by defining only:

- common scenario chains
- reusable atomic governance actions
- a document mounting model
- how those map to the current rule registry and future task-session model

It does not implement persistence, UI, adapters, or gates.

---

## 2. Technical Boundary

> **中文注释**：本工单只补机括自身的“场景链路总图”和“文档挂载模型”。它不是代码实现，也不是规则自动启用。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

Mainline explicitly not changed:

- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `docs/jikuo/schemas/rule_registry_view_model.schema.md`
- `tools/audit/check_rule_registry.py`
- checker JSON output behavior
- desktop-agent card renderer
- CLI bridge commands
- frontend implementation
- task-session storage
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine
- `.codex/AGENTS.md`

Canonical source:

- accepted `JIKUO-PRD-01`
- accepted `JIKUO-AGENT-00`
- accepted `JIKUO-CORE-01`
- accepted `JIKUO-CORE-02`
- draft `JIKUO-FLOW-01`
- current report-only checker baseline from `WORKTREE-05D`

Bridge objects:

- conceptual `JikuoGovernanceScenarioChainV0`
- conceptual `JikuoDocumentMountV0`

Consumer projection:

- desktop-agent task-start governance summaries
- rule-candidate cards
- completion/evidence reports
- handoff summaries
- future task-session records
- future frontend audit/configuration views
- future auxiliary CLI reports

Lifecycle:

- user or project context introduces a governance need
- agent classifies the scenario chain
- matching rules are resolved
- required documents are mounted
- evidence obligations are rendered
- task proceeds under report-only visibility
- user accepts, requests revision, defers, or turns friction into a rule-evolution proposal
- later task-session storage records the resolved chain and document mounts

Rollback / supersession:

- this document may be superseded by a later accepted chain model
- later implementation must preserve report-only defaults unless separately approved
- document mounts must be auditable and removable, not hidden prompt lore

Propagation surfaces:

- this document
- productization task map
- Sprint index
- future FLOW-01 revisions if accepted
- future CORE-03 task-session schema
- future rule candidate and registry proposal models

Observability:

- future implementation should record scenario chain id, resolved rules, resolved document mounts, missing documents, evidence status, user decisions, and handoff summary references

---

## 3. Scope

This work order defines:

- common JIKUO engineering-governance scenario chains
- the atomic governance actions shared by those chains
- document mount roles and layers
- how required reference files differ from rule source references and output documents
- how mounted documents map to current registry fields
- how mounted documents should affect future CORE-03 task-session records
- delivery criteria and acceptance gate

---

## 4. Out Of Scope

This work order does not:

- implement document-mount storage
- implement rule-candidate persistence
- modify the current registry
- modify the checker
- implement desktop-agent cards
- implement CLI bridge commands
- implement frontend screens
- implement task-session storage
- implement import/export tooling
- implement hooks, CI, task-stop gates, or blocking enforcement
- change narrative runtime behavior
- judge product-output quality
- define product-content semantic review rules

---

## 5. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `docs/jikuo/schemas/rule_registry_view_model.schema.md`
- `tools/audit/check_rule_registry.py`
- `SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`
- `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`
- `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 6. Pre-Audit

> **中文注释**：这是一次自举审计。机括要服务引擎治理，但机括本身不能因为自举而无限展开。

Task target:

- define JIKUO scenario chains and document mounting without implementing new tooling

Compliance status:

- aligned with scenario-first methodology because it starts from user/task scenarios
- aligned with desktop-agent-first posture because ordinary use remains inside Codex / Claude desktop APP chat
- aligned with CORE-01 because evidence status remains structured but report-only
- aligned with CORE-02 because rule fields and document obligations need user-facing labels later
- aligned with product boundary because it governs process construction and change, not product-output quality

Required adjustments:

- treat required reference files as document mounts, not as a new trigger type
- keep trigger resolution separate from required document resolution
- keep document mounts visible in task start, evidence report, completion, and handoff
- defer persistence, UI, adapter, and gate work

---

## 7. Common Scenario Chain Map

> **中文注释**：这些是当前总设计下常见链路。它们不是 UI 功能清单，而是后续 task session、规则候选、文档挂载和审计报告的上游场景图。

| Chain id | User situation | Trigger shape | Business chain | Primary artifacts | Typical document mounts |
|---|---|---|---|---|---|
| `project_onboarding` | User wants JIKUO to inspect or enable governance for a project | User asks to enable/inspect JIKUO or project governance assets are detected | discover governance state -> summarize posture -> identify missing setup -> propose next step | onboarding summary, setup report | product definition, current registry, checker docs, project rule docs |
| `natural_language_rule_candidate` | User expresses a working-method preference | User says a repeatable process rule in ordinary language | extract intent -> classify rule layer -> propose rule candidate -> user accept/edit/reject/defer | rule candidate card, proposal note | source conversation, related policy docs, design docs that justify the rule |
| `required_reference_pack` | User specifies files that must be consulted for a class of work | User says certain tasks must reference sprint/design/audit docs | classify task context -> create document mount proposal -> attach to rule/task layer -> report required docs on future tasks | document mount card, required reference pack | sprint file, related design docs, AGENTS/agent rule docs, testing governance |
| `work_order_start` | User starts or continues a work order | New/changed work-order doc or explicit task start | classify task -> resolve triggered rules -> resolve document mounts -> render task-start governance summary | task-start governance card | current sprint index, upstream work orders, relevant design docs |
| `mainline_change` | Agent edits runtime, prompt, state, review, or orchestration code | Changed paths or declared mainline context | classify changed surface -> trigger rule checks -> collect source/bridge/projection/testing evidence -> report gaps | evidence status report, verification summary | hardening baseline, testing governance, relevant architecture docs |
| `design_or_schema_change` | User asks to define or change product/design/schema contracts | Design/schema/work-order path changes or explicit design context | identify canonical source -> declare bridge/projection/lifecycle -> define rollback/supersession -> update indexes | design contract, schema note, index update | PRD, schema docs, registry/view-model docs, scenario-chain docs |
| `audit_execution` | User asks for review, audit, or delivery validation | Audit/review command, work completion, or reviewer task | resolve audit scope -> mount required references -> perform pre/mid/post audit -> report evidence and missing items | audit report, review findings, acceptance gate note | sprint file, AGENTS, related design docs, work order, testing docs |
| `task_completion_acceptance` | Work is ready for user review | Agent proposes completion or user asks for summary | summarize changes -> report verification -> report governance evidence -> record user decision | completion acceptance card, acceptance record | work order, checker output, verification logs, changed docs |
| `cross_agent_handoff` | User moves between Codex and Claude desktop APPs | User asks to continue elsewhere or current task pauses | emit handoff summary -> reference canonical docs -> state pending decisions -> next agent rehydrates context | handoff summary | task state, current work order, triggered rules, missing evidence |
| `rule_evolution` | Repeated friction suggests a rule should change | User says a rule should be added/changed or evidence repeatedly missing | identify pattern -> propose rule change -> require approval -> record rollback/supersession needs | rule evolution proposal, approval note | source rule docs, registry schema, prior task evidence |
| `gate_promotion_review` | A report-only rule may become stronger | User or audit asks to promote enforcement | inspect false positives -> define rollback -> require explicit approval -> keep gate separate from rule definition | gate feasibility note, approval record | checker logs, prior reports, gate feasibility work order |
| `scenario_package_extension` | JIKUO is applied beyond engineering governance | Future creative/research/process package requested | identify package boundary -> preserve kernel semantics -> add package fields/templates -> avoid redefining enforcement | package definition, extension contract | package PRD, scenario docs, kernel rule docs |

---

## 8. Atomic Governance Actions

Common chains should be composed from smaller actions:

| Action | Responsibility | Must remain separable from |
|---|---|---|
| `discover_governance_state` | Find registry, checker, product map, work orders, and existing task state | rule creation, gate enforcement |
| `classify_scenario_chain` | Decide which chain is active for this task | product-output evaluation |
| `resolve_triggered_rules` | Match task context / paths / declarations to rules | required document resolution |
| `resolve_document_mounts` | Find required references, output docs, evidence carriers, and index docs | trigger matching |
| `render_governance_summary` | Explain obligations in desktop chat | persistence or gate behavior |
| `collect_evidence_status` | Mark evidence as `ok`, `missing`, `review`, `not_applicable`, or `error` | deciding product quality |
| `run_report_only_checker` | Produce deterministic report when supported | blocking task execution |
| `record_user_decision` | Capture accept/edit/reject/defer phrases and context | inferring approval from silence |
| `emit_handoff_summary` | Let another desktop agent continue from project-local state | relying only on conversation memory |
| `propose_rule_evolution` | Turn repeated friction into a rule-change candidate | direct registry write-back |
| `supersede_document_mount` | Retire or replace outdated required references | deleting audit history |

These actions are the primitive layer that prevents composite features from becoming opaque.

---

## 9. Document Mounting Model

> **中文注释**：用户指定“每次做某类任务必须参考哪些文件”，在机括里不是新 trigger，而是 document mount。trigger 决定何时生效，mount 决定生效后必须读/写/引用哪些文档。

Conceptual object:

```yaml
kind: "jikuo_document_mount"
mount_id: ""
mount_layer: "work_order"
role: "required_reference"
document_ref: ""
required_when: []
evidence_expectation: ""
freshness_policy: "current_or_explicitly_superseded"
review_owner: ""
missing_behavior: "report_missing"
surface: "desktop_agent_card"
```

Required fields:

- `mount_id`
- `mount_layer`
- `role`
- `document_ref`
- `required_when`
- `evidence_expectation`
- `freshness_policy`
- `missing_behavior`

Allowed `mount_layer` values for current planning:

- `kernel`
- `product`
- `project`
- `scenario_package`
- `sprint`
- `work_order`
- `task_session`
- `operation`
- `handoff`

Allowed `role` values:

- `source_ref`
- `required_reference`
- `evidence_carrier`
- `output_target`
- `index_entry`
- `handoff_reference`
- `policy_reference`
- `design_context`
- `testing_context`

Allowed `missing_behavior` values:

- `report_missing`
- `review_required`
- `not_applicable_with_note`
- `future_gate_candidate`

Default rule:

- missing required documents are report-only until a later gate work order explicitly approves blocking behavior.

---

## 10. Document Mount Roles

| Role | Meaning | Current registry mapping | Example |
|---|---|---|---|
| `source_ref` | Explains where the rule came from | `rule.source_refs` | A work order or accepted design note that created the rule |
| `required_reference` | Must be consulted when the rule or task context applies | `evidence.required_documents` plus later task-session mount record | Current sprint file, AGENTS, design docs |
| `evidence_carrier` | Must contain proof that work met an obligation | `evidence.required_sections`, `evidence.declarations`, later task-session evidence | Work order sections, verification log |
| `output_target` | Document that must be updated by the task | future proposal / task-session output tracking | Sprint index, schema doc, PRD |
| `index_entry` | Index document that must link the new artifact | `evidence.required_documents` plus declaration | Sprint index entry for a new work order |
| `handoff_reference` | Document another agent must read before continuing | later handoff summary field | Work order, task session, missing evidence report |
| `policy_reference` | Standing method/policy document | `required_reference` with project/kernel layer | AGENTS, testing governance |
| `design_context` | Design source that constrains a change | `required_reference` or `source_ref` depending on use | PRD, schema, architecture doc |
| `testing_context` | Testing policy or fixture source that constrains validation | `required_reference` / `evidence_carrier` | TESTING_GOVERNANCE, semantic test template |

---

## 11. Common Document Mount Patterns

### 11.1 Project Method Pack

Purpose:

- keep standing project methods visible without relying on agent memory

Typical mounts:

- `.codex/AGENTS.md` or active agent execution rules
- testing governance
- governance rule registry and schema

Typical chain:

- task starts -> method pack is discovered -> only relevant obligations are summarized -> missing reference is reported

### 11.2 Sprint Context Pack

Purpose:

- bind a task to current sprint intent and accepted constraints

Typical mounts:

- current sprint index
- current work order
- relevant hardening baseline
- relevant insight docs

Typical chain:

- work order starts -> sprint pack resolves -> agent reports upstream assumptions and non-goals

### 11.3 Design / Schema Pack

Purpose:

- make design and data-contract changes reference their canonical design source

Typical mounts:

- PRD
- schema docs
- view-model docs
- related architecture notes

Typical chain:

- design/schema task starts -> design pack resolves -> source/bridge/projection/lifecycle declarations are required

### 11.4 Audit Execution Pack

Purpose:

- support review and delivery validation without inventing requirements late

Typical mounts:

- current sprint file
- work order
- AGENTS / method rules
- relevant design docs
- checker output
- verification logs

Typical chain:

- audit starts -> reference pack resolves -> pre-audit records scope and refs -> mid-audit records encountered obligations -> post-audit records outcome and missing evidence

### 11.5 Handoff Pack

Purpose:

- allow Codex and Claude desktop APP workflows to continue from project-local evidence

Typical mounts:

- current work order
- task summary
- triggered obligations
- missing evidence report
- accepted/deferred user decisions

Typical chain:

- handoff requested -> handoff pack resolves -> outgoing agent writes summary -> incoming agent rehydrates and states assumptions

### 11.6 Rule Evolution Pack

Purpose:

- ensure rule changes are auditable and reversible

Typical mounts:

- original rule source refs
- current registry schema
- prior task evidence
- proposed rule change
- rollback/supersession note

Typical chain:

- friction repeats -> rule evolution proposed -> approval required -> registry change remains proposal-first

---

## 12. Example: Three-Phase Audit As A Mounted Chain

> **中文注释**：这是用户刚才举的场景，但这里只作为一个通用链路样例，不把整张文档缩窄成这一个需求。

User intent:

- every work-order delivery should perform pre-audit, mid-audit, and post-audit
- required references include the sprint file, related documents, AGENTS, and relevant design files

Modeling:

```yaml
scenario_chain: "audit_execution"
trigger:
  required_context:
    - "work_order_delivery"
document_mounts:
  - role: "required_reference"
    mount_layer: "sprint"
    document_ref: "current sprint file"
  - role: "policy_reference"
    mount_layer: "project"
    document_ref: ".codex/AGENTS.md or active agent rules"
  - role: "design_context"
    mount_layer: "work_order"
    document_ref: "related design / schema / PRD documents"
evidence:
  required_sections:
    - "Pre-Audit"
    - "Mid-Audit"
    - "Post-Audit"
  declarations:
    - "audit_references_reviewed"
    - "pre_audit_completed"
    - "mid_audit_completed"
    - "post_audit_completed"
enforcement:
  phase: "report_only"
```

Expected desktop-agent behavior:

- at task start, show that audit references are required
- during work, report whether pre/mid/post audit evidence exists
- at completion, report missing evidence instead of silently claiming compliance
- if the user accepts, record acceptance in the future task session

---

## 13. Mapping To Existing Registry Fields

Current registry fields already cover most of this model:

| Need | Existing field | Gap |
|---|---|---|
| Why a rule exists | `source_refs` | Sufficient for rule source |
| When a rule applies | `trigger.changed_paths`, `trigger.added_paths`, `trigger.required_context` | Needs richer task-context classification later |
| Required reference files | `evidence.required_documents` | Needs role/layer/freshness metadata later |
| Required work-order sections | `evidence.required_sections` | Sufficient for headings |
| Required statements | `evidence.declarations` | Needs structured declaration evidence later |
| Runtime audit fields | `evidence.audit_bundle_fields` | Future task-session implementation needed |
| Human approval | `evidence.approval_record`, `evidence.user_acceptance_record` | Future exact phrase/context capture needed |
| Owner/reviewer | `review.owner` | Sufficient as first model |

Conclusion:

- document mounting does not require a new trigger type
- later registry/view-model work may add mount descriptors or sidecar metadata
- CORE-03 should snapshot resolved document mounts per task

---

## 14. CORE-03 Implications

`JIKUO-CORE-03` should include fields or projections for:

- `scenario_chain_id`
- `task_context`
- `triggered_rules`
- `resolved_document_mounts`
- `required_references`
- `reference_status`
- `evidence_status`
- `missing_documents`
- `user_decisions`
- `handoff_references`
- `rule_evolution_candidates`

It should be able to answer:

- which scenario chain was active
- which documents the task was required to consult
- which documents were actually consulted or updated
- which evidence was missing
- what the user accepted, rejected, deferred, or asked to revise
- what another desktop agent must read to continue safely

---

## 15. Surface Decision Rules

Desktop APP chat should show:

- active scenario chain
- required reference pack
- triggered rules
- missing documents
- evidence status
- user decision options
- handoff references

Auxiliary CLI should support:

- deterministic checker report
- exportable task-session or mount snapshot later
- machine-readable missing evidence output

Future frontend should support:

- editing document mounts visually
- browsing scenario chains
- comparing rule/document mount versions
- inspecting task-session audit history

Do not require frontend for:

- routine task start
- routine audit reference reporting
- routine completion review
- cross-agent handoff

Do not make CLI the default path for:

- approvals
- ordinary rule explanation
- natural-language rule candidate review

---

## 16. Testing Governance Declaration

> **中文注释**：这是链路/文档挂载契约，不改变 runtime 行为，也不评价产品输出内容。

Required test layers for this slice:

- `unit`: N/A because no parser, serializer, mount resolver, card renderer, or storage code is implemented.
- `integration`: N/A because no UI, CLI, adapter, checker, registry migration, or runtime integration is implemented.
- `workflow/orchestration`: required by contract review; scenario chains and document mounts must cover common user paths.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against this new work order and updated index.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for scenario coverage, document mount layer/role clarity, CORE-03 readiness, and recursion boundary.

---

## 17. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| SC-DC-01 | Define product question and recursion boundary | Section 1 exists |
| SC-DC-02 | Preserve no-implementation boundary | Sections 2, 3, and 4 exist |
| SC-DC-03 | Include audit references | Section 5 exists |
| SC-DC-04 | Declare pre-audit | Section 6 exists |
| SC-DC-05 | Define common scenario chain map | Section 7 exists |
| SC-DC-06 | Define atomic governance actions | Section 8 exists |
| SC-DC-07 | Define document mounting model | Section 9 exists |
| SC-DC-08 | Define document mount roles and patterns | Sections 10 and 11 exist |
| SC-DC-09 | Include three-phase audit as one example, not the only chain | Section 12 exists |
| SC-DC-10 | Map model to existing registry fields | Section 13 exists |
| SC-DC-11 | Declare CORE-03 implications | Section 14 exists |
| SC-DC-12 | Preserve desktop-agent-first surface posture | Section 15 exists |
| SC-DC-13 | Declare testing-governance layers | Section 16 exists |
| SC-DC-14 | Run report-only checker smoke | Verification log records checker result |

---

## 18. Acceptance Gate

> **中文注释**：这是进入 CORE-03 之前的又一个小暂停点。你验收后，我们再把任务会话模型里的 scenario chain、document mounts 和 evidence snapshot 做成数据契约。

This work order is ready for user review when:

- common JIKUO scenario chains are explicit
- document mounts are separated from trigger rules
- common document mount roles and layers are clear
- the three-phase audit case is covered without narrowing the product to that case
- current registry fields are mapped without forcing immediate schema changes
- CORE-03 has concrete upstream requirements
- no implementation has been silently approved
- checker smoke has been run

Do not continue to task-session schema implementation, document-mount storage, rule-candidate persistence, desktop card implementation, CLI bridge, frontend design, registry migration, gate implementation, or Sprint 050 runtime hardening until the user accepts this scenario-chain and document-mounting contract.

---

## 19. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md
```

Result:

- registry validation passed
- triggered `R-006` and `R-012`
- required new-work-order fields and sections reported `OK`
- Sprint index document requirement reported `OK`
- `sprint_index_entry` declaration remained `REVIEW`
- exit code `0`
- report-only posture preserved

---

## 20. Acceptance Record

> **中文注释**：用户确认继续，因此本工单可作为 `JIKUO-FLOW-01` 轻量调整和 `JIKUO-CORE-03` 的上游输入。审批/验收记录里的 `phrase` 字段应保存用户原话，例如 `"<exact user phrase as spoken>"`，而不是要求用户使用固定口令。该验收不代表批准 document-mount storage、rule-candidate persistence、CLI、前端、gate、adapter 或 runtime 实现。

Acceptance:

- common scenario chains may be used as upstream planning context
- document mounts may be treated as the conceptual model for required reference files
- `JIKUO-CORE-03` should include task-session fields for scenario chain, resolved document mounts, evidence status, user decisions, and handoff references

Still not accepted:

- modifying `rule_registry.yaml`
- modifying checker behavior
- implementing document-mount persistence
- implementing task-session storage
- implementing desktop-agent cards
- implementing CLI bridge commands
- implementing frontend screens
- implementing gate behavior
- changing Sprint 050 runtime narrative engine behavior

---

## 21. Follow-Up Correction: First User Operation Chain

> **中文注释**：本工单定义的是场景链与 document mount 原子模型，不等于完整用户操作链。后续确认第一条用户操作链应单独命名为 Desktop App Primary Operating Loop。

Correction:

- scenario chains and document mounts remain upstream atoms
- the first user operation chain is `JIKUO-FLOW-02: Desktop App Primary Operating Loop`
- ordinary use should start and complete inside Codex / Claude desktop APP
- CLI/helper commands should be invoked internally by agents unless the user explicitly chooses an advanced CLI path

Downstream requirement:

- future task order should place `JIKUO-FLOW-02` before more adapter, skill/plugin, MCP, frontend, or helper expansion work
