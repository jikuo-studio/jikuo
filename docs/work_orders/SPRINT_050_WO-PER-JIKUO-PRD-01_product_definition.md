# SPRINT_050_WO-PER-JIKUO-PRD-01: Product Definition

> **Date**: 2026-05-03  
> **Updated**: 2026-05-04  
> **Status**: Accepted by user; revised desktop-agent-first input for `JIKUO-AGENT-00`  
> **Primary sprint**: Sprint 050 / contract-first hardening incubation  
> **Task type**: productization / PRD / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance productization; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`  
> **Current slice**: Part 1 accepted; `JIKUO-AGENT-00` may use this as product-definition input  
> **User scenario**: In the current engineering-governance track, an AI-primary software/application/system developer wants their working-method preferences to become visible, confirmable, auditable project governance rather than fragile prompt memory.  
> **Runtime chain**: User preference -> rule candidate -> user confirmation -> active governance object -> task trigger -> evidence report -> user acceptance -> rule evolution.  
> **Canonical source**: accepted process-governance product vision and accepted `JIKUO-UX-00` current-track scenario/action map.  
> **Bridge object**: this PRD product definition.  
> **Consumer projection**: `JIKUO-AGENT-00`, `JIKUO-CORE-01`, later schema, UI, agent integration, and gate feasibility work.  
> **Lifecycle**: accepted current-track PRD baseline; future scenario packages require explicit PRD supersession or package-specific PRD slices.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 产品口径

> **中文注释**：本 PRD 第一版定义的是机括的第一个落地场景：AI 工程治理。长期愿景更抽象：机括是 AI 核心过程治理内核。

Long-term product vision:

`机括` is an AI-primary process governance kernel.

It can govern any AI-centered process where human intent, AI execution, rule obligations, evidence, approval, state sedimentation, and rule evolution must stay explicit.

Current application track:

`机括` is first being developed as an AI-primary engineering governance product.

In this track, it helps people who mainly rely on AI to develop software, applications, tools, automation, or technical systems turn working-method preferences into:

- visible rule objects
- explicit trigger conditions
- evidence expectations
- human approval points
- task completion reports
- auditable rule evolution history

Product promise:

- users should not have to trust that an AI agent remembered every project rule
- users should be able to say a working-method preference in ordinary language
- AI may propose a structured rule, but the user must confirm before it becomes active
- active rules should appear at task start, task completion, and rule-evolution moments
- users should be able to complete common approvals inside their active Codex / Claude desktop APP workflow without switching to a separate frontend or terminal-first flow

Short product definition:

`机括` is a governance layer for AI-led processes. Its first application package turns engineering project methods into checkable and reviewable operating objects across chat, reports, cards, future UI, and future gates.

Future scenario-package direction:

- engineering governance is the first package
- creative-process governance may be a later package
- research / knowledge-production governance may be later packages
- AI application plugin governance may be a later packaging form

Boundary:

- the kernel manages process rules, triggers, evidence, approvals, lifecycle, audit, and evolution
- scenario packages define domain-specific rules and surfaces
- the kernel should not directly judge product-output quality, aesthetic quality, or creative value

---

## 2. 技术口径

> **中文注释**：PRD 这里继承 UX-00 的场景/动作地图；后续 CORE/UI/GATE 只能消费这个定义，不应该绕过它直接实现。

Mainline changed:

- `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md` status / acceptance record

Mainline explicitly not changed:

- runtime narrative engine
- `tools/audit/check_rule_registry.py`
- `rule_registry.yaml`
- `.codex/AGENTS.md`
- hooks, CI, or task-stop gates
- frontend implementation

Canonical source:

- accepted `JIKUO-UX-00` target user, scenario, atomic action, and product surface map

Bridge object:

- this PRD product definition

Consumer projection:

- later `JIKUO-CORE-01` structured result model
- later `JIKUO-AGENT-00` desktop-agent-first interaction contract
- later `JIKUO-CORE-02` UI-ready registry model
- later `JIKUO-CORE-03` task session and evidence model
- later `JIKUO-UI-01` and `JIKUO-UI-02`
- later `JIKUO-GATE-01`

Lifecycle:

- Part 1 defines product identity and MVP loop
- user review accepts or revises the PRD baseline
- later work orders may implement data models, adapters, UI, or gates only from accepted PRD slices

Rollback / supersession:

- if user rejects the MVP loop, revise this PRD before creating CORE/UI/GATE work
- if later implementation proves a PRD assumption wrong, record a PRD supersession note instead of silently changing downstream scope

---

## 3. Scope

Part 1 defines:

- current-track target users and non-target users
- product problem
- product promise
- first MVP loop
- rule object lifecycle
- human approval model
- desktop-agent-first interaction model
- user-friendly surfaces
- non-goals and boundary rules
- first success criteria
- handoff to CORE/UI/GATE work

Part 1 is allowed to use existing NarrativeSystem governance assets as incubation examples, but it must keep `机括` broader than this repository and broader than engineering alone.

---

## 4. Out Of Scope

> **中文注释**：这不是实现工单。尤其不能把 PRD 误当成前端开工令或 gate 开工令。

This work order does not:

- implement frontend UI
- define visual design
- implement JSON checker output
- implement task session storage
- implement git hooks, CI, task-stop, or blocking gates
- modify `.codex/AGENTS.md`
- modify `rule_registry.yaml`
- modify runtime narrative engine code
- implement Sprint 049 memory lifecycle work
- define product-output quality evaluation rules
- serve end users of an AI-built application

Sprint 049 memory lifecycle boundary:

- this PRD may use lifecycle as a governance analogy
- it must not implement or absorb Sprint 049 memory lifecycle features

---

## 5. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/sprints/insights/INDEX.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`
- `SPRINT_050_WO-PER-WORKTREE-05A_auditable_engine_evidence_model.md`
- `SPRINT_050_WO-PER-WORKTREE-05B_rule_materialization_matrix.md`
- `SPRINT_050_WO-PER-WORKTREE-05C_rule_registry_schema.md`
- `SPRINT_050_WO-PER-WORKTREE-05D_local_audit_checker_report_only.md`
- `SPRINT_050_WO-PER-WORKTREE-05E_ai_agent_operating_kernel.md`
- `SPRINT_050_WO-PER-WORKTREE-05F_gate_feasibility.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/agent_operating_kernel.md`

---

## 6. Pre-Audit

> **中文注释**：事前审计结论：可以写 PRD 第一片；不能直接跳到 UI、CORE、gate 或 runtime hardening。

Task target:

- define `机括` product identity and MVP loop from the accepted `JIKUO-UX-00` scenario/action map

Compliance status:

- aligned with `JIKUO-UX-00` because it starts from target users, scenarios, atomic actions, and product surfaces
- aligned with `05B` because it treats rules as materializable governance objects
- aligned with `05D` and `05F` because current checker and gate posture remains report-only and non-blocking
- aligned with the engineering/product boundary because the PRD does not judge product-output quality

Required adjustments:

- keep product users limited to AI-primary development users
- keep the MVP loop smaller than full UI or full gate implementation
- require user confirmation before any AI-proposed rule becomes active
- keep future blocking gates behind explicit approval and rollback planning

---

## 7. Target Users

> **中文注释**：这里的目标用户是当前工程治理轨道的目标用户；机括长期愿景允许后续再定义创作、研究等其他场景包用户。

Current-track primary users:

- AI-primary solo developers
- non-professional technical founders
- AI-assisted maintainers of complex projects
- small AI-native teams

Current-track user jobs:

- start AI work in an existing or new project without losing project discipline
- express working-method preferences without writing YAML manually
- know which rules were triggered by a task
- know what evidence exists before accepting AI work
- convert repeated AI-development failures into long-term governance
- transfer governance context across agents

Non-target users for the current engineering-governance track:

- final users of the software being built
- domain creators using the software for content generation
- product-output reviewers who do not govern development workflow

---

## 8. Product Problem

> **中文注释**：问题不是“AI 不够聪明”，而是 AI 主责开发时，工作方法没有稳定的载体。

AI-primary development creates a governance gap:

- project rules live in long documents, prompts, memory, or scattered chat history
- AI agents may follow rules inconsistently across sessions
- users often notice violations only after reviewing outcomes
- custom user preferences are easy to say but hard to turn into durable project behavior
- gating too early creates friction and false blocking
- leaving everything as prose creates drift

The product problem:

- make working-method rules explicit enough to be triggered, reported, reviewed, and evolved
- keep users in control of rule activation and enforcement
- avoid forcing non-professional users to operate raw engineering configuration files

---

## 9. Core Product Principles

> **中文注释**：这些原则会约束后续 CORE、UI 和 gate。它们是产品原则，不是代码实现。

1. AI proposes, user confirms, system records.
2. Rules are layered objects, not prompt fragments.
3. Report-only comes before blocking.
4. Every promotion to stronger enforcement needs approval and rollback.
5. Product-output judgment remains human or domain-review owned.
6. Frontend is one surface, not the product itself.
7. The smallest useful loop must work in chat/report form before full UI.
8. Governance should reduce user anxiety, not make the user manage another opaque system.
9. Codex / Claude desktop APP interaction is the primary continuity path; CLI and standalone frontend are supporting surfaces.

---

## 10. First MVP Loop

> **中文注释**：第一版 MVP 不追求“大而全控制台”，只验证最小闭环：说出规则、确认规则、任务触发、收尾验收。

The first MVP loop:

`express preference -> propose rule -> confirm rule -> trigger during task -> report evidence -> user accepts or requests changes`

Step definition:

| Step | User-visible moment | System responsibility |
|---|---|---|
| Express preference | User says how they want AI to work | Capture and classify the preference |
| Propose rule | AI presents a rule candidate | Show layer, trigger, evidence, and enforcement phase |
| Confirm rule | User accepts, edits, rejects, or defers | Record decision and only activate accepted rules |
| Trigger during task | User starts or continues a development task | Match task context against active rules |
| Report evidence | AI prepares completion | Show triggered rules and evidence status |
| Accept or request changes | User reviews completion | Record acceptance, missing evidence, or follow-up |

MVP success condition:

- a non-professional AI-primary project builder can configure at least one project rule without editing raw YAML, then see that rule affect a later task report.

---

## 11. MVP Surface Boundary

> **中文注释**：第一版可以不是完整前端。我们先让产品闭环成立，再决定哪些部分需要界面。

MVP surfaces:

- conversational setup
- natural-language rule extraction
- rule confirmation card or structured confirmation summary
- task-start checklist
- task-completion acceptance report
- report-only checker output

Not MVP surfaces:

- full visual rule configuration console
- full run-control dashboard
- audit analytics dashboard
- blocking gate adapter
- CI / branch protection integration

Reason:

- the core value is not “has a UI”
- the core value is “rules become confirmable, triggerable, reportable, and evolvable”

---

## 12. Desktop-Agent-First Interaction Model

> **中文注释**：机括不能强迫用户离开 Codex / Claude 桌面 APP 的主工作流。CLI 可以存在，但它是辅助 bridge / fallback，不是默认主界面。

Interaction principle:

- desktop-agent-first.
- CLI as auxiliary bridge / fallback.
- frontend for configuration, control, audit, and evolution views.

Canonical state:

- durable governance state should live in project-local artifacts, not in any single agent chat history
- Codex Desktop and Claude Desktop are the primary user interaction surfaces
- optional Codex / Claude CLI, local CLI utilities, and future frontend should read from or write to the same governance state through defined contracts

Primary user path:

`user works in Codex or Claude desktop APP -> agent reads governance state -> agent renders a card/report in chat -> user approves or rejects in chat -> agent records the decision -> optional CLI/frontend projection shows the same state later`

Allowed desktop-agent interactions:

- rule confirmation in chat
- task-start governance summary in chat
- missing-evidence report in chat
- completion acceptance in chat
- rule evolution proposal in chat
- portable handoff summary between Codex and Claude desktop APP sessions

Auxiliary CLI bridge role:

- CLI should act as a state/report utility or agent-invoked bridge, not as the ordinary user's main product surface
- CLI may generate rule reports, validate state, print cards, and write accepted decisions only when explicitly instructed or authorized by a desktop-agent flow
- CLI should not require the user to leave the active Codex / Claude desktop APP unless the current agent cannot safely perform the operation

Frontend role:

- frontend is optional for the MVP loop
- frontend is most useful for visual configuration, audit history, cross-task review, and later evolution dashboards
- frontend should not be the only way to confirm common task-level decisions

Continuity requirement:

- the same rule, evidence, and approval object must render consistently across desktop chat, CLI/report, and future frontend
- if different surfaces disagree, project-local canonical state wins

Out of scope for this PRD slice:

- implementing adapters for Codex or Claude
- implementing CLI commands
- implementing frontend synchronization
- choosing the final on-disk `.jikuo` schema

---

## 13. Rule Object Lifecycle

> **中文注释**：规则必须有生命周期。否则它仍然只是提示词，只是写得更漂亮一点。

Rule lifecycle:

1. `captured`
2. `candidate`
3. `user_confirmed`
4. `active_report_only`
5. `observed_in_tasks`
6. `revised_or_superseded`
7. `promoted_or_retired`

Required lifecycle properties:

- source statement
- proposed interpretation
- layer
- trigger
- evidence expectation
- enforcement phase
- confirmation record
- supersession history
- rollback path when enforcement changes

Rule activation invariant:

- no AI-proposed rule becomes active without user confirmation.

Enforcement promotion invariant:

- no report-only rule becomes blocking without explicit approval, false-positive review, and rollback plan.

---

## 14. Human Approval Model

> **中文注释**：机括不能替用户做关键判断，但它必须让“哪里需要用户判断”变得清楚。

Human approval is required for:

- activating a project rule
- promoting enforcement beyond report-only
- accepting task completion when missing evidence exists
- changing or retiring a persistent rule
- changing global agent operating rules

Human approval is not required for:

- AI proposing a candidate rule
- checker reporting triggered obligations
- generating a task-start checklist
- generating a task-completion report
- rendering a rule in a different product surface

Approval record should include:

- who approved
- what was approved
- when it was approved
- what changed
- whether rollback is available

---

## 15. Product Modes

> **中文注释**：机括对普通用户友好的方式，不只有前端。对话、卡片、报告、轻命令都可以是产品入口。

| Mode | User-friendly role | MVP status |
|---|---|---|
| Conversational steward | Helps users express rules in ordinary language | MVP |
| Rule confirmation card | Prevents AI-proposed rules from silently becoming active | MVP |
| Task-start checklist | Shows what rules matter before work begins | MVP |
| Completion acceptance report | Shows triggered rules and evidence before acceptance | MVP |
| Report-only local checker | Provides deterministic trigger/evidence visibility | MVP incubation |
| Desktop-agent handoff summary | Lets users move between Codex and Claude desktop APP sessions without losing governance context | MVP candidate |
| Auxiliary CLI report | Lets agents or terminal-preferring users print the same governance state without opening a frontend | MVP candidate |
| Frontend rule console | Lets users edit rules visually | Later |
| Run-control console | Shows task sessions and missing evidence live | Later |
| Evolution dashboard | Shows rule history and promotion candidates | Later |
| Gate adapter | Connects mature rules to blocking workflows | Later |

---

## 16. Non-Goals

> **中文注释**：非目标要写清楚，否则机括会膨胀成“所有 AI 工作管理工具”。

`机括` is not:

- a general prompt library
- a code generation agent
- a project management suite
- a final product-quality judge
- a content-creation quality evaluator
- a replacement for human acceptance
- a blocking gate system by default
- a NarrativeSystem-only internal tool

`机括` should not:

- make product-output quality conclusions
- silently activate AI-proposed rules
- silently promote report-only checks into blocking gates
- require raw YAML editing for ordinary users once user-facing surfaces exist
- require a standalone frontend for routine confirmations that can safely happen inside Codex or Claude
- hide rule evolution history

---

## 17. First Success Criteria

> **中文注释**：这些是产品闭环是否成立的早期判断，不是代码测试用例。

Part 1 product success criteria:

- target users can understand what `机括` is in one sentence
- the MVP loop is smaller than full UI or gate implementation
- user custom rules require confirmation before activation
- active rules can be surfaced at task start and completion
- missing evidence can be reported without prematurely blocking
- rule evolution has a lifecycle and approval model
- common approvals can happen through desktop-agent cards or summaries
- the PRD does not drift into product-output quality judgment

---

## 18. Handoff To Next Work

> **中文注释**：PRD 验收后，下一步不一定立刻写前端。更稳的是先定义 desktop-agent-first contract 和结构化 result/session schema。

After Part 1 acceptance, reasonable next work orders are:

- `JIKUO-AGENT-00`: desktop-agent-first interaction contract for Codex / Claude desktop APP continuity, with CLI as auxiliary bridge
- `JIKUO-CORE-01`: structured result model for rule triggers and evidence statuses
- `JIKUO-CORE-02`: UI-ready rule registry model
- `JIKUO-CORE-03`: task session and evidence model
- `JIKUO-AGENT-01`: agent integration / handoff prompts
- later `JIKUO-UI-01`: rule configuration console
- later `JIKUO-GATE-01`: gate adapters only after report-only behavior matures

Recommended next step:

- `JIKUO-AGENT-00`, because the product must first define how Codex / Claude desktop APP interactions preserve continuity without requiring a standalone frontend or terminal-first workflow.

---

## 19. Testing Governance Declaration

> **中文注释**：这是产品定义文档，不改变叙事引擎行为，也不实现任何工具。

Required test layers for this slice:

- `unit`: N/A because no code changes are planned.
- `integration`: N/A because no frontend, checker integration, hook, CI, or runtime integration is planned.
- `workflow/orchestration`: required by PRD review and UX-to-PRD consistency review.
- `semantic regression`: N/A because no product behavior changes.
- `smoke`: required; run the report-only checker against the new PRD work order path.
- `human semantic review`: N/A for product semantics because this slice does not change product behavior or product content evaluation.
- `human governance review`: required for product boundary, MVP loop, non-goals, and handoff readiness.

---

## 20. Part 1 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P1-DC-01 | Define product identity | Section 1 exists |
| P1-DC-02 | Define target and non-target users | Section 7 exists |
| P1-DC-03 | Define product problem and principles | Sections 8 and 9 exist |
| P1-DC-04 | Define first MVP loop | Section 10 exists |
| P1-DC-05 | Define MVP surface boundary | Section 11 exists |
| P1-DC-06 | Define desktop-agent-first interaction model | Section 12 exists |
| P1-DC-07 | Define rule lifecycle and human approval model | Sections 13 and 14 exist |
| P1-DC-08 | Define non-goals | Section 16 exists |
| P1-DC-09 | Define next-work handoff | Section 18 exists |
| P1-DC-10 | Preserve implementation boundary | No runtime, checker, registry, hook, CI, `.codex/AGENTS.md`, or frontend code is changed |
| P1-DC-11 | Run report-only checker smoke | Verification log records checker result |

---

## 21. Acceptance Gate For Part 1

> **中文注释**：这是 PRD 第一片暂停点。你验收后，才进入 CORE/result model 或继续补 PRD 更细章节。

Part 1 is ready for user review when:

- product identity is clear
- target users remain AI-primary development users
- first MVP loop is understandable and small
- frontend and gate are not treated as immediate implementation
- Codex / Claude desktop APP interaction is recognized as the main continuity path for target users
- user confirmation remains required for rule activation
- product-output quality judgment remains out of scope
- next-work recommendation is clear
- checker smoke has been run

Do not continue to `JIKUO-AGENT-00`, `JIKUO-CORE-01`, UI design, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 1 PRD.

---

## 22. Part 1 Acceptance Record

> **中文注释**：用户已确认继续，因此 PRD 第一片可作为 `JIKUO-AGENT-00` 输入。仍不代表 UI、gate 或实现已被批准。

Acceptance:

- user accepted the revised Part 1 PRD by saying `请继续`
- `JIKUO-AGENT-00` may start from the desktop-agent-first interaction model

Still not accepted:

- Codex / Claude adapter implementation
- CLI command implementation
- frontend implementation
- core schema implementation
- gate implementation
- `.codex/AGENTS.md` promotion
- Sprint 050 runtime hardening changes under this productization task

---

## 23. Part 1 Verification Log

> **中文注释**：这里记录 PRD 第一片实际跑过的检查。checker 仍然只是 report-only。

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md
```

Result:

- registry validation passed
- triggered `R-006` and `R-012`
- required fields and sections for `R-006` reported `OK`
- Sprint index document for `R-012` reported `OK`
- `sprint_index_entry` declaration remained `REVIEW`
- exit code `0`
- report-only posture preserved
