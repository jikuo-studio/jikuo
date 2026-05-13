# SPRINT_050_WO-PER-JIKUO-FLOW-01: Engineering Governance User Journey And Interaction Flow

> **Date**: 2026-05-04  
> **Status**: Draft / aligned with accepted scenario-chain and document-mounting model  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / interaction contract / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`; `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`; `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`; `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`; `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`; `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`  
> **Current slice**: user journey and interaction flow only; no frontend, CLI, adapter, checker, gate, registry migration, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user who mainly relies on AI for project development needs `机括` to make task rules, evidence, approvals, and handoff state visible without forcing routine work through a separate frontend or terminal-first workflow.  
> **Runtime chain**: user intent -> scenario-chain classification -> rule trigger report -> document mount resolution -> desktop-agent governance summary -> evidence collection -> user approval / deferral -> task completion record -> handoff summary -> future audit view.  
> **Canonical source**: accepted JIKUO product definition, desktop-agent-first interaction contract, structured result model, UI-ready registry view-model schema, and the current report-only checker baseline.  
> **Bridge object**: `JikuoEngineeringGovernanceUserJourneyV0`.  
> **Consumer projection**: Codex / Claude desktop APP chat cards, future auxiliary CLI reports, future frontend configuration/control/audit views, and future task-session records.  
> **Lifecycle**: journey draft -> user review -> accepted interaction contract -> later CORE-03 task-session model and adapter/UI planning.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答一个很朴素的问题：开发到现在，用户实际怎么使用机括？

The current JIKUO track has defined:

- product positioning
- desktop-agent-first posture
- structured checker result
- UI-ready registry projection

But it has not yet made the ordinary user journey concrete enough.

This work order defines the engineering-governance track as an end-to-end use flow:

- how a user starts using JIKUO in an existing project
- how a natural-language working-method preference becomes a rule candidate
- how required reference files become document mounts rather than hidden prompt lore
- how a task starts with visible governance context
- how evidence and missing obligations are shown during work
- how the user accepts, defers, rejects, or evolves governance state
- how Codex and Claude desktop APP workflows hand off state without turning CLI or frontend into the required primary path

This is intentionally earlier than `JIKUO-CORE-03`.

If the user journey is not explicit before the task-session model is designed, `CORE-03` may become a storage-first model rather than a product-use model.

---

## 2. Technical Boundary

> **中文注释**：本工单只定义使用路径与交互契约，不实现任何新功能。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md` acceptance status

Mainline explicitly not changed:

- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `docs/jikuo/schemas/rule_registry_view_model.schema.md`
- `tools/audit/check_rule_registry.py`
- checker JSON output behavior
- desktop-agent card renderer
- CLI bridge commands
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine
- `.codex/AGENTS.md`

Canonical source:

- accepted `JIKUO-PRD-01` product boundary
- accepted `JIKUO-AGENT-00` desktop-agent-first interaction contract
- accepted `JIKUO-CORE-01` structured result model
- accepted `JIKUO-CORE-02` registry view-model schema
- current report-only checker baseline from `WORKTREE-05D`

Bridge object:

- conceptual `JikuoEngineeringGovernanceUserJourneyV0`

Consumer projection:

- Codex / Claude desktop APP chat summaries
- future desktop-agent cards
- future auxiliary CLI reports
- future frontend configuration/control/audit views
- future task-session evidence records

Lifecycle:

- project has no active JIKUO state
- user introduces a governance preference or starts a task
- agent checks existing registry / checker / docs
- agent renders a governance summary
- task produces evidence and approvals
- task completion records accepted, deferred, or missing governance items
- handoff summary lets another desktop agent continue
- future audit views consume accumulated task-session records

Rollback / supersession:

- this document may be superseded by a later accepted interaction-flow version
- later implementation must not silently replace desktop-agent-first posture with CLI-first or frontend-only posture
- later state changes must preserve report-only defaults unless separately approved

Propagation surfaces:

- this document
- productization task map
- Sprint index
- future `CORE-03` task-session schema
- future agent card / frontend / CLI projection contracts

Observability:

- future implementation should record which user flow was active, which rule obligations were shown, which evidence was missing, which approval phrase was accepted, and which handoff summary was produced

---

## 3. Scope

This work order defines:

- the first-use journey for an existing project
- natural-language rule-candidate flow
- task-start governance flow
- in-task evidence flow
- task-completion and acceptance flow
- cross-agent handoff flow between Codex and Claude desktop APPs
- auxiliary CLI and frontend roles
- user-facing interaction artifacts
- state names needed by later `CORE-03`
- delivery criteria and acceptance gate

---

## 4. Out Of Scope

This work order does not:

- implement task-session storage
- implement rule-candidate storage
- implement desktop cards
- implement CLI bridge commands
- implement frontend screens
- implement checker changes
- implement registry view-builder code
- implement rule import/export
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
- `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 6. Pre-Audit

> **中文注释**：这是一张“先把使用链路画出来”的工单。它不应该抢跑成 UI、CLI 或 gate 实现。

Task target:

- define the engineering-governance user journey for JIKUO before task-session modeling

Compliance status:

- aligned with desktop-agent-first posture because Codex / Claude desktop APP chat remains the primary operating path
- aligned with CORE-01 because checker results need a user-facing flow
- aligned with CORE-02 because rule registry view models need a concrete editing / proposal journey
- aligned with report-only governance because missing evidence is visible but not automatically blocking
- aligned with product boundary because this flow governs the development process, not product-output quality

Required adjustments:

- insert `JIKUO-FLOW-01` before `JIKUO-CORE-03`
- align the flow with `JIKUO-SCENARIO-CHAIN-01` so task-session records can preserve scenario chain and document mount state
- keep CLI auxiliary
- keep frontend as later configuration/control/audit surface
- keep user approval explicit
- avoid implementation claims

---

## 7. User Journey V0

### 7.1 First Enable / Project Onboarding

User situation:

- the user is developing a project mainly through Codex / Claude desktop APPs
- the project already has docs, rules, or preferences scattered across prompts, task notes, and conversation memory
- the user wants those rules to become inspectable and repeatable

Expected flow:

1. User asks the desktop agent to enable or inspect JIKUO for the project.
2. Agent looks for project-local governance assets.
3. Agent reports whether a registry, checker, product map, and task-session state exist.
4. Agent explains the current posture as report-only unless a later gate has been explicitly approved.
5. Agent offers a short next action: inspect rules, propose a rule, start governed task, or view missing setup.

Primary surface:

- Codex / Claude desktop APP chat

Auxiliary surfaces:

- CLI may run the checker or export a report
- future frontend may show setup status visually

---

### 7.2 Natural-Language Preference To Rule Candidate

User situation:

- the user says a working-method preference in ordinary language
- example shape: "I want every task that touches core state to declare source, bridge, projection, and lifecycle."

Expected flow:

1. Agent identifies that the statement may be a governance preference.
2. Agent distinguishes rule trigger intent from document-mount intent.
3. Agent proposes a rule candidate instead of silently treating the sentence as permanent instruction.
4. Agent shows the candidate in a compact confirmation card.
5. User accepts, edits, rejects, or defers the candidate.
6. Accepted candidates become pending or active registry changes only through an approved later persistence mechanism.

The candidate card should show:

- proposed rule title
- trigger surface
- required document mounts, if any
- required evidence
- enforcement phase
- review owner
- whether approval is required
- what will not happen yet

Valid user decisions should include:

- accept as a candidate
- accept for this task only
- revise before accepting
- defer
- reject

This flow must not:

- infer permanent approval from casual agreement
- write to registry without a proposal boundary
- promote a report-only rule to a gate
- hide required reference files inside agent memory instead of showing them as document mounts

---

### 7.3 Task Start Governance Summary

User situation:

- the user asks the agent to do a development task
- the task may touch files, docs, runtime behavior, or governance contracts

Expected flow:

1. Agent identifies the likely changed / added surfaces.
2. Agent classifies the likely scenario chain.
3. Agent resolves triggered rules and required document mounts.
4. Agent runs or conceptually applies report-only governance checks when available.
5. Agent renders a task-start governance summary in chat.
6. User sees what obligations and required references may be triggered before work proceeds too far.
7. Agent continues unless the user asks to pause, revise scope, or gather missing context first.

The task-start summary should show:

- task intent
- likely affected surfaces
- triggered or likely-triggered rules
- resolved required references / document mounts
- evidence expected by those rules
- current enforcement posture
- explicit non-goals
- whether a human approval checkpoint is expected

This flow is not a blocking task-stop gate unless a later gate work order approves that behavior.

---

### 7.4 In-Task Evidence Flow

User situation:

- the agent is doing work and governance evidence becomes relevant

Expected flow:

1. Agent keeps a lightweight evidence list while working.
2. Agent records which required fields or sections are satisfied.
3. Agent records which required reference documents were consulted or still missing.
4. Agent marks missing or review-only evidence explicitly.
5. Agent does not invent evidence merely to satisfy a checklist.
6. Agent gives short progress updates when a governance obligation changes.

Evidence states should reuse the CORE-01 vocabulary:

- `ok`
- `missing`
- `review`
- `not_applicable`
- `error`

The user should not need to read raw YAML to understand the current evidence state.

---

### 7.5 Task Completion / Acceptance Flow

User situation:

- work is ready for review

Expected flow:

1. Agent summarizes actual changes.
2. Agent summarizes verification.
3. Agent reports active scenario chain, resolved document mounts, triggered obligations, and evidence status.
4. User accepts, requests missing evidence, asks for revisions, or defers completion.
5. Accepted completion can become a task-session record in later `CORE-03`.

The completion card should distinguish:

- work outcome
- verification outcome
- governance evidence outcome
- required reference / document-mount outcome
- user acceptance state
- known residual risks
- recommended next step

Acceptance phrases should be ordinary desktop-chat phrases, but future implementation must record the exact phrase and context before treating it as durable approval.

---

### 7.6 Cross-Agent Handoff Flow

User situation:

- the user moves between Codex desktop APP and Claude desktop APP
- the user wants continuity without manually reconstructing governance state

Expected flow:

1. Current agent emits a handoff summary.
2. Handoff summary references project-local canonical documents and current report state.
3. Next agent reads the same project-local state instead of relying only on chat memory.
4. Next agent states what it believes is accepted, pending, deferred, or out of scope.

Handoff summary should include:

- current task id or work-order id when available
- accepted product posture
- active rule or checker posture
- changed / added paths
- triggered obligations
- resolved document mounts and missing references
- missing or review evidence
- pending user decisions
- explicit "do not do" boundaries

This flow is the main reason desktop-agent-first cannot be replaced by a CLI-only path.

---

## 8. Interaction Artifacts

> **中文注释**：这些是未来卡片、CLI 报告、前端视图可以共用的交互对象；本工单只命名，不实现。

V0 artifact inventory:

| Artifact | Primary surface | Purpose |
|---|---|---|
| `onboarding_summary` | desktop chat | Explain current project governance setup |
| `rule_candidate_card` | desktop chat / future frontend | Let the user review a proposed rule |
| `task_start_governance_card` | desktop chat | Show likely triggered obligations before work proceeds |
| `evidence_status_report` | desktop chat / CLI / future frontend | Show required, missing, review, and satisfied evidence |
| `document_mount_report` | desktop chat / CLI / future frontend | Show which required references apply, which were consulted, and which are missing |
| `completion_acceptance_card` | desktop chat | Separate work result, verification result, and governance evidence |
| `rule_evolution_proposal_card` | desktop chat / future frontend | Turn repeated friction or missing evidence into a rule-change proposal |
| `handoff_summary` | desktop chat / markdown report | Let another desktop agent continue safely |

All artifacts should be renderable as plain text first.

Future frontend can make them visual, but routine use should remain possible in Codex / Claude desktop APP chat.

---

## 9. State Names Needed By CORE-03

`CORE-03` should be designed around actual user-flow states, not only storage tables.

Minimum state vocabulary:

| State | Meaning |
|---|---|
| `no_active_governance_state` | Project has no active JIKUO state or it has not been discovered |
| `governance_setup_detected` | Registry, checker, or governance docs exist |
| `rule_candidate_proposed` | Agent proposed a rule candidate from user intent |
| `rule_candidate_deferred` | User deferred the candidate |
| `rule_candidate_rejected` | User rejected the candidate |
| `rule_candidate_accepted_for_task` | User accepted the rule only for the current task |
| `rule_candidate_accepted_for_registry_proposal` | User accepted candidate as a future registry proposal |
| `task_session_started` | A governed task has begun |
| `scenario_chain_resolved` | A task has been classified into a governance scenario chain |
| `document_mounts_resolved` | Required references or document mounts have been resolved for the task |
| `obligation_triggered` | A rule obligation is triggered or likely triggered |
| `evidence_missing` | Required evidence is missing |
| `evidence_review_required` | Evidence requires human governance review |
| `task_completion_proposed` | Agent believes work is ready for user review |
| `task_completion_accepted` | User accepted completion |
| `task_completion_revision_requested` | User requested changes |
| `rule_evolution_proposed` | Task friction produced a possible rule change |
| `handoff_ready` | A cross-agent handoff summary exists |

---

## 10. Surface Decision Rules

Desktop APP chat should handle:

- ordinary task-start summaries
- rule-candidate explanation
- lightweight evidence reports
- user approval and deferral
- completion acceptance
- cross-agent handoff text

Auxiliary CLI should handle:

- deterministic report generation
- explicit checker invocation
- exportable JSON or text
- agent-readable bridge output

Future frontend should handle:

- persistent rule configuration
- large audit history
- visual comparison of rule versions
- task-session browsing
- dashboards and trend views

Do not require the frontend for:

- starting a normal governed task
- accepting a simple task completion
- reading a short missing-evidence report
- handing off from Codex to Claude

Do not make CLI the default user path for:

- approvals
- routine confirmations
- ordinary task review
- user-facing rule explanation

---

## 11. Candidate User Phrases

> **中文注释**：这些是未来实现可参考的短语，不是本工单批准的解析器。

Candidate approval phrases:

- "接受这条规则候选"
- "这次任务先按这个规则执行"
- "先暂存，不启用"
- "拒绝这条规则"
- "这个任务验收通过"
- "补齐证据后再结束"
- "把这次失败转成规则候选"
- "生成交接摘要"

Future implementation must record:

- exact user phrase
- surrounding task context
- affected rule or task id
- surface where approval happened
- whether approval is durable or task-local

---

## 12. Relationship To CORE-03

`JIKUO-CORE-03` should follow this work order.

CORE-03 should model:

- task session identity
- changed / added paths
- triggered obligations
- scenario chain id
- resolved document mounts
- required references and missing references
- evidence statuses
- user approval events
- acceptance records
- handoff summaries
- audit trail

CORE-03 should not invent a task-session object that cannot explain:

- what the user saw
- what the user approved
- what was missing
- what was deferred
- what another desktop agent needs to continue

---

## 13. Testing Governance Declaration

> **中文注释**：这是交互/流程契约，不改变 runtime 行为，也不评价产品输出内容。

Required test layers for this slice:

- `unit`: N/A because no parser, serializer, card renderer, or storage code is implemented.
- `integration`: N/A because no UI, CLI, adapter, checker, registry migration, or runtime integration is implemented.
- `workflow/orchestration`: required by contract review; the user journey must support desktop-agent-first task start, evidence flow, acceptance, and handoff.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against this new work order and updated index.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for user journey completeness, approval boundaries, CLI/frontend positioning, and CORE-03 readiness.

---

## 14. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| FLOW-DC-01 | Define the product question | Section 1 exists |
| FLOW-DC-02 | Preserve no-implementation boundary | Sections 2, 3, and 4 exist |
| FLOW-DC-03 | Define first-use onboarding flow | Section 7.1 exists |
| FLOW-DC-04 | Define natural-language rule-candidate flow | Section 7.2 exists |
| FLOW-DC-05 | Define task-start governance summary flow | Section 7.3 exists |
| FLOW-DC-06 | Define in-task evidence flow | Section 7.4 exists |
| FLOW-DC-07 | Define task-completion acceptance flow | Section 7.5 exists |
| FLOW-DC-08 | Define Codex / Claude desktop handoff flow | Section 7.6 exists |
| FLOW-DC-09 | Define interaction artifacts | Section 8 exists |
| FLOW-DC-10 | Define CORE-03 state vocabulary | Section 9 exists |
| FLOW-DC-11 | Preserve desktop-agent-first, CLI-auxiliary, frontend-later posture | Section 10 exists |
| FLOW-DC-12 | Declare testing-governance layers | Section 13 exists |
| FLOW-DC-13 | Run report-only checker smoke | Verification log records checker result |

---

## 15. Acceptance Gate

> **中文注释**：这是进入 CORE-03 之前的暂停点。你验收后，我们再把“任务会话与证据模型”做成数据契约。

This work order is ready for user review when:

- a normal user can understand how JIKUO is used inside Codex / Claude desktop APP workflows
- rule-candidate, task-start, evidence, acceptance, and handoff flows are concrete
- CLI remains auxiliary and frontend remains later configuration/control/audit surface
- user approval is explicit and auditable
- no implementation has been silently approved
- CORE-03 has clear upstream flow states
- checker smoke has been run

Do not continue to task-session schema implementation, desktop card implementation, CLI bridge, frontend design, registry migration, gate implementation, or Sprint 050 runtime hardening until the user accepts this flow contract.

---

## 17. Follow-Up Correction: Primary Operation Loop

> **中文注释**：后续讨论确认，`FLOW-01` 的用户旅程仍偏“对象与状态链路”，还需要一条更上层的用户操作主链路，把已拆出的原子动作重新组合成桌面 APP 内的实际使用流程。

Correction:

- `FLOW-01` remains useful as engineering-governance journey context
- it should not be treated as the complete primary user operation chain
- the first concrete user operation chain is now separated into `JIKUO-FLOW-02: Desktop App Primary Operating Loop`

Downstream requirement:

- future agent, helper, skill/plugin, MCP, frontend, or gate work should be ordered after `JIKUO-FLOW-02` acceptance
- helper/CLI commands must be treated as internal atoms unless the user explicitly chooses an advanced CLI workflow

---

## 18. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md
```

Result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved
