# SPRINT_050_WO-PER-JIKUO-UX-00: User Scenarios And Atomic Action Map

> **Date**: 2026-05-03
> **Status**: Accepted by user; upstream input for `JIKUO-PRD-01`
> **Primary sprint**: Sprint 050 / contract-first hardening incubation
> **Task type**: productization / UX architecture / governance documentation work order
> **Parent direction**: `机括` AI-primary process governance productization; current engineering-governance scenario package
> **Preceded by**: `docs/jikuo/governance/jikuo_productization_task_map.md`
> **Current slice**: Part 1 accepted; `JIKUO-PRD-01` may use this map as product-definition input
> **User scenario**: In the current engineering-governance scenario package, an AI-primary software/application/system developer needs a safe way to turn working-method preferences into auditable development governance before product design begins.
> **Runtime chain**: User development need -> governance scenario -> interaction path -> atomic action -> recomposable chain -> product surface candidate -> later PRD / schema / checker / UI work.
> **Canonical source**: accepted process-governance product vision and current engineering-governance scenario boundary.
> **Bridge object**: `JIKUO-UX-00` scenario/action map.
> **Consumer projection**: `JIKUO-PRD-01`, core schema work, result model work, frontend design, and agent integration.
> **Lifecycle**: accepted current-track scenario package; future non-engineering packages must be added by separate accepted scenario maps.
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 产品口径

> **中文注释**：本工单拆的是机括第一个落地场景：工程治理。它不否认机括未来可以管理创作、研究或其他 AI 核心过程，只是不在本片展开。

The product-facing problem is that `机括` should not start from UI screens or feature lists.

It must first define:

- who the user is
- which development scenarios create governance needs
- which user interactions trigger which chains
- which chains can be decomposed into atomic actions
- which atomic actions can later be recomposed into conversation, cards, checker reports, frontend configuration, or gates

Product-level vision:

- `机括` is an AI-primary process governance kernel
- engineering governance is the first scenario package
- later packages may govern creative processes, research workflows, knowledge-production processes, or AI application plugin workflows

Current-track target user:

- people who mainly rely on AI to develop software, applications, tools, or systems
- non-professional programmers with concrete project-development needs and explicit working-method preferences
- solo developers, product founders, and small teams that need AI work to stay bounded, auditable, and repeatable

Not the target user for this current engineering-governance scenario package:

- end users of the software built with AI
- domain creators using the resulting application
- reviewers who only evaluate product output quality without governing development process

Expected visible change after this work order is executed:

- `机括` product design starts from scenario chains instead of feature speculation
- future PRD and UI work inherits a stable map of user scenarios, atomic actions, and recomposable governance chains
- custom user rules are treated as confirmable governance objects, not as prompt fragments

---

## 2. 技术口径

> **中文注释**：这里沿用我们已经在叙事引擎 hardening 里建立的方法：先场景，后链路；先基础动作，后组合功能。

Mainline documents to be changed if this work order is accepted:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

Mainline explicitly not changed:

- runtime narrative engine
- `tools/audit/check_rule_registry.py`
- `rule_registry.yaml`
- `.codex/AGENTS.md`
- hooks, CI, or task-stop gates
- frontend implementation

Canonical source:

- confirmed target user boundary
- accepted user scenario and atomic action map

Bridge object:

- `JIKUO-UX-00` scenario/action map

Consumer projection:

- later `JIKUO-PRD-01`
- later core schema and result model work
- later frontend configuration and run-control design
- later agent integration and gate feasibility work

Lifecycle:

- draft work order
- user review
- accepted Part 1 execution
- scenario/action map becomes input to `JIKUO-PRD-01`

Rollback / supersession:

- if user rejects the target boundary or scenario taxonomy, revise this work order before mapping begins
- if later PRD work discovers a better scenario model, supersede the map explicitly rather than silently editing downstream assumptions

---

## 3. Scope

Part 1, if accepted, will define:

- target user boundary
- non-target-user boundary
- core AI-primary development governance scenarios
- scenario-to-interaction-path map
- atomic action taxonomy
- recomposable chain map
- product surface suitability map
- evidence needed before moving into PRD

The mapping must follow this sequence:

1. user scenario
2. interaction trigger
3. governance chain
4. atomic actions
5. recomposable chain variants
6. suitable product surfaces
7. future implementation candidates

---

## 4. Out Of Scope

> **中文注释**：本工单只做机括产品化前置分析，不实现具体产品，也不回到叙事引擎 runtime 修复。

This work order does not:

- implement frontend UI
- implement JSON checker output
- implement task session storage
- implement git hooks, CI, or blocking gates
- modify `.codex/AGENTS.md`
- modify runtime narrative engine code
- implement Sprint 049 memory lifecycle work
- define product-output quality evaluation rules
- treat end-user content creation as the primary `机括` use case

Sprint 049 memory lifecycle boundary:

- memory lifecycle may remain a motivating analogy for why governance needs lifecycle control
- this work order must not implement or absorb Sprint 049 memory lifecycle features

---

## 5. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/sprints/insights/INDEX.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_productization_task_map.md`
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

> **中文注释**：事前审计结论：可以进入机括产品化前置分析，但不能跳过用户场景，也不能直接设计 UI。

Task target:

- create the work order for `机括` user scenarios and atomic action mapping

Compliance status:

- aligned with `05A` because it starts from auditable evidence and operation chains
- aligned with `05B` because it treats user rules as materializable governance objects
- aligned with `05C` because future custom rules should eventually become structured registry records
- aligned with `05D` because report-only checker behavior remains unchanged
- aligned with `05E` because agent operating behavior remains standalone and not promoted
- aligned with `05F` because gate implementation remains separate from feasibility and UX mapping

Required adjustments:

- keep target users limited to AI-primary development users
- keep product-output evaluation outside engineering governance
- keep this slice documentation-only
- do not implement frontend, checker, registry, gate, or runtime changes

---

## 7. Initial Scenario Families To Map

> **中文注释**：这些只是待映射的场景族，不是最终 PRD 功能列表。真正的产品功能必须从这些链路和动作里推导。

Part 1 should map at least these scenario families:

- project setup: user wants to define how AI should work in a new or existing code project
- task start: user starts an AI development task and needs applicable rules to be surfaced
- rule capture: user states a working-method preference in natural language and needs AI to propose a structured rule candidate
- rule confirmation: user reviews, revises, accepts, or rejects a candidate rule before it becomes active
- task execution monitoring: AI performs work while triggered obligations and missing evidence remain visible
- task completion: AI reports which rules were triggered, which evidence exists, and which items need human acceptance
- failure-to-rule learning: a bad development experience is converted into a candidate long-term governance rule
- rule evolution: a rule is promoted, paused, narrowed, superseded, or rolled back with audit history
- adapter use: the same governance object is consumed by chat, task cards, checker output, UI, or future gates

---

## 8. Atomic Action Candidates

> **中文注释**：先拆基础动作，后面才能组合出 retry 这类复杂功能的治理等价物。产品化也应该遵守这个原则。

Part 1 should define atomic actions such as:

- capture user intent
- classify intent as project rule, task rule, one-time constraint, or non-rule note
- infer affected development surface
- propose structured rule candidate
- request user confirmation
- write accepted rule to the appropriate layer
- match rule triggers against a task
- report triggered obligations
- request or record evidence
- pause for human approval
- record acceptance or rejection
- supersede or rollback a rule
- produce an audit summary

Each atomic action should declare:

- input
- output
- owner
- persistence requirement
- human approval requirement
- candidate product surfaces

---

## 9. Product Surface Candidates

> **中文注释**：前端只是表面之一。普通用户还需要对话式、卡片式、报告式和轻命令式入口。

Part 1 should classify which actions are suitable for:

- conversational setup
- natural-language rule extraction
- rule confirmation card
- task-start checklist
- task-completion acceptance card
- checker report
- frontend rule configuration console
- frontend run-control console
- audit/evolution dashboard
- future gate adapter

The mapping should not assume that every useful action needs a full frontend screen in MVP.

---

## 10. Testing Governance Declaration

> **中文注释**：这是产品化/治理文档小片，不改变叙事引擎行为，也不评价产品输出质量。

Required test layers for this slice:

- `unit`: N/A because no code changes are planned.
- `integration`: N/A because no frontend, checker integration, hook, CI, or runtime integration is planned.
- `workflow/orchestration`: required by documentation review and scenario-chain consistency review.
- `semantic regression`: N/A because no product behavior changes.
- `smoke`: required; run the report-only checker against the new work order path.
- `human semantic review`: N/A for product semantics because this slice does not change product behavior or product content evaluation.
- `human governance review`: required for target user boundary, scenario families, and whether this can feed `JIKUO-PRD-01`.

---

## 11. Part 1 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P1-DC-01 | Define target and non-target users | User boundary section exists |
| P1-DC-02 | Define scenario families before UI or PRD | Scenario family map exists |
| P1-DC-03 | Define atomic action taxonomy | Atomic action section exists |
| P1-DC-04 | Map scenarios to interaction paths and recomposable chains | Scenario/action map exists |
| P1-DC-05 | Map actions to product surfaces without assuming frontend-first design | Product surface section exists |
| P1-DC-06 | Preserve governance boundary | No product-output quality judgment is introduced |
| P1-DC-07 | Preserve implementation boundary | No runtime, checker, registry, hook, CI, or frontend code is changed |
| P1-DC-08 | Run report-only checker smoke | Verification log records checker result |

---

## 12. Acceptance Gate For Draft

> **中文注释**：这是工单草案暂停点。你验收后，我才继续真正执行 `JIKUO-UX-00` 的 Part 1 场景/动作地图。

This draft is ready for user review when:

- the target user boundary is correct
- the scope is limited to pre-PRD UX/action mapping
- the scenario-first and atomic-action-first method is explicit
- implementation and product-output evaluation are out of scope
- checker smoke has been run

Do not continue to the full `JIKUO-UX-00` mapping, `JIKUO-PRD-01`, frontend design, gate implementation, or Sprint 050 runtime hardening until the user accepts this draft.

---

## 13. Draft Verification Log

> **中文注释**：这里记录草案阶段实际跑过的检查。checker 只报告触发义务，不阻塞任务。

Commands to run after draft creation:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md
```

Result:

- registry validation passed
- triggered `R-006` and `R-012`
- required fields and sections for `R-006` reported `OK`
- Sprint index document for `R-012` reported `OK`
- `sprint_index_entry` declaration remained `REVIEW`
- exit code `0`
- report-only posture preserved

---

## 14. Draft Acceptance Record

> **中文注释**：用户已确认继续，因此本文件从草案进入 Part 1 执行。这里记录接受边界，避免以后误以为本工单已经进入 PRD 或 UI。

Acceptance:

- user accepted the draft direction by saying `继续`
- Part 1 may execute scenario and atomic-action mapping

Still not accepted:

- `JIKUO-PRD-01`
- frontend design
- JSON/result model implementation
- task session storage
- gate implementation
- `.codex/AGENTS.md` promotion

---

## 15. Part 1 Target User Boundary

> **中文注释**：机括的用户不是“使用某个 AI 应用的人”，而是“用 AI 做项目开发的人”。这个边界会影响所有后续场景、界面和规则模板。

Primary user group:

- AI-primary project builders who use one or more AI agents to develop software, applications, tools, automation, or technical systems.

Representative user profiles:

| User profile | Development reality | Governance need |
|---|---|---|
| Solo product builder | Has product intent and can review results, but relies heavily on AI for implementation | Keep AI work bounded, explainable, and recoverable |
| Non-professional technical founder | Understands desired product behavior but is not fluent in codebase architecture | Turn working preferences into visible rules, checks, and approval points |
| AI-assisted maintainer | Maintains an existing project through repeated AI sessions | Prevent drift, forgotten constraints, accidental rewrites, and inconsistent task closure |
| Small AI-native team | Multiple people or agents touch the same project | Share rule state, evidence expectations, acceptance records, and escalation points |

Not target users for this product layer:

- creators using an AI-built application for domain output
- consumers who only interact with the final app
- product reviewers whose role is only to judge content or UX results

Boundary rule:

- `机括` may require evidence that a product-quality review happened, but it must not directly decide the product-quality conclusion.

---

## 16. Rule Source Layers

> **中文注释**：通用规则可以来自我们的动态文档；用户自己的规则可以由 AI 提炼，但必须经用户确认后才生效。

`机括` should treat rules as layered objects, not as one prompt blob.

| Layer | Source | Example development meaning | Activation model |
|---|---|---|---|
| Universal governance pack | Built-in dynamic documents and accepted methods | task boundary, evidence, no silent gate promotion, no unsafe revert | enabled by project or workspace preset |
| Project rule | User-confirmed project preference | core state changes must declare source / bridge / projection / lifecycle | persistent until paused, superseded, or removed |
| Task/session rule | User instruction for one task | this task is audit-only and must not modify code | active only for the current session or task |
| Adapter rule | Integration-specific behavior | run report-only checker before completion report in Codex Desktop | active when that adapter is used |
| Gate rule | Promoted governance requirement | blocking only after approval, false-positive review, and rollback plan | active only after explicit promotion |

Rule extraction chain:

`user natural-language preference -> AI proposes candidate rule -> user reviews layer / trigger / evidence / phase -> accepted rule is stored -> rule becomes visible to checker / cards / UI / reports`

Non-negotiable safety point:

- AI may propose a rule, but user confirmation is required before the rule becomes active.

---

## 17. Core Scenario Inventory

> **中文注释**：这些是机括的基础用户场景，不是功能清单。后续功能必须从这些场景和链路里推导。

| Scenario ID | Scenario | User trigger | Desired governance outcome |
|---|---|---|---|
| UX-S01 | Project setup | User starts using AI on a code project | Establish initial governance pack, project boundary, and rule storage location |
| UX-S02 | Existing project onboarding | User asks AI to continue work in a complex repo | Read current rule state, detect active task context, avoid accidental scope drift |
| UX-S03 | Natural-language rule capture | User states a working-method preference | Convert preference into a candidate rule with layer, trigger, evidence, and phase |
| UX-S04 | Rule confirmation | User reviews a candidate rule | Accept, revise, reject, defer, or mark it as one-time only |
| UX-S05 | Task start | User gives AI a development task | Surface relevant rules, triggered obligations, and expected evidence before work begins |
| UX-S06 | Task execution monitoring | AI changes files or decisions during work | Keep triggered rules and missing evidence visible without blocking prematurely |
| UX-S07 | Task completion | AI reports work as done | Show changed surfaces, triggered rules, evidence status, and required human acceptance |
| UX-S08 | Failure-to-rule learning | User notices an AI-development failure pattern | Convert the failure into a candidate long-term rule or adjustment |
| UX-S09 | Rule evolution | User wants to make a rule stricter, softer, narrower, or retired | Record supersession, rollback path, and reason for change |
| UX-S10 | Multi-agent continuity | User switches between Codex, Claude, or another agent | Carry governance context across agents through structured artifacts, not memory alone |
| UX-S11 | Adapter execution | User wants rules surfaced in a specific tool | Project the same governance object into chat, cards, checker, UI, or future gate |

---

## 18. Scenario To Interaction Path Map

> **中文注释**：这里把用户交互路径先拆出来。之后 UI 不应该凭空设计，而应该承接这些路径。

| Scenario ID | Interaction path | Atomic chain |
|---|---|---|
| UX-S01 | User selects or describes project type -> system proposes default governance pack -> user accepts baseline -> workspace stores active pack | A01 -> A02 -> A05 -> A06 -> A12 |
| UX-S02 | User opens existing repo -> system reads known governance artifacts -> system reports active rules and gaps -> user chooses continue / repair / ignore | A03 -> A04 -> A08 -> A11 -> A12 |
| UX-S03 | User says a working-method preference -> AI extracts candidate rule -> system classifies layer and trigger -> user receives confirmation card | A01 -> A02 -> A05 -> A06 -> A07 |
| UX-S04 | User reviews candidate rule -> edits trigger / evidence / phase -> accepts or rejects -> system records decision | A07 -> A09 -> A10 -> A12 |
| UX-S05 | User starts a task -> system matches task against active rules -> system reports obligations -> AI includes obligations in plan | A03 -> A04 -> A08 -> A13 -> A14 |
| UX-S06 | AI changes files or task scope -> system refreshes triggered obligations -> missing evidence remains visible -> escalation happens only when configured | A03 -> A04 -> A08 -> A13 -> A15 |
| UX-S07 | AI prepares completion -> system collects evidence -> report shows OK / MISSING / REVIEW -> user accepts, requests fix, or defers | A08 -> A13 -> A14 -> A16 -> A17 |
| UX-S08 | User describes a repeated failure -> AI proposes preventive candidate rule -> user chooses project rule or one-time reminder | A01 -> A02 -> A05 -> A07 -> A10 |
| UX-S09 | User changes a rule -> system records before/after -> superseded rule remains auditable -> affected adapters update projection | A09 -> A10 -> A12 -> A18 -> A19 |
| UX-S10 | User switches agent -> system exports governance context -> new agent reads active rules and current task evidence -> user sees continuity summary | A12 -> A19 -> A20 -> A21 |
| UX-S11 | User opens a product surface -> surface requests governance projection -> system renders only the relevant action subset | A19 -> A20 -> A21 |

---

## 19. Atomic Action Taxonomy

> **中文注释**：这是机括的“基础动作库”。复杂功能必须由这些动作组合出来，而不是每次重新写一套综合逻辑。

| ID | Atomic action | Input | Output | Owner | Persistence | Approval |
|---|---|---|---|---|---|---|
| A01 | Capture user intent | user text, selected task, current project context | raw intent record | user + AI | session | no |
| A02 | Classify intent | raw intent record | project rule / task rule / one-time constraint / non-rule note | AI proposes | session | review if rule-like |
| A03 | Read governance context | repo path, active task, known artifacts | active rule set and gaps | system | session | no |
| A04 | Infer affected development surface | task description, changed paths, work order type | affected surfaces | AI + checker | session | no |
| A05 | Propose structured rule candidate | classified intent, affected surface | candidate rule with trigger, evidence, phase, layer | AI | session | required before activation |
| A06 | Choose rule layer | candidate rule | universal / project / task / adapter / gate layer | user confirms | persistent if accepted | required |
| A07 | Render confirmation object | candidate rule | reviewable card or conversational summary | system | session | required |
| A08 | Match active triggers | task context, changed paths, added paths, rule registry | triggered obligations | checker/system | session | no |
| A09 | Edit rule candidate | user edits, candidate rule | revised candidate | user + AI | session | required |
| A10 | Record rule decision | candidate rule, user decision | accepted / rejected / deferred record | system | persistent for accepted or audited decisions | required |
| A11 | Report governance gap | active context, missing artifacts | visible warning or repair suggestion | system | session or audit log | no |
| A12 | Persist governance artifact | accepted rule, decision, or pack | stored rule / audit note / index link | system | persistent | depends on layer |
| A13 | Request evidence | triggered obligation | required evidence checklist | system | session | no |
| A14 | Attach evidence | test result, doc link, declaration, acceptance note | evidence record | AI + user | session or persistent | review if manual |
| A15 | Escalate missing evidence | missing evidence, enforcement phase | warning / review-required / block candidate | system | audit log | depends on phase |
| A16 | Produce task completion report | changed surfaces, triggered rules, evidence records | completion report | AI | session | user review |
| A17 | Record task acceptance | user response, completion report | accepted / needs changes / deferred | user + system | persistent | required |
| A18 | Supersede or rollback rule | existing rule, proposed change | supersession record or rollback record | user + system | persistent | required |
| A19 | Project governance object | active rule/evidence state, target surface | chat/card/checker/UI/gate projection | system | derived | no |
| A20 | Export/import agent context | governance state, adapter target | portable context bundle | system | session or persistent | no |
| A21 | Render user-readable summary | governance state, user role | concise current-state summary | system/AI | session | no |

---

## 20. Recomposable Chain Map

> **中文注释**：同一组基础动作可以组合成多条产品链路。这样以后做前端、checker、agent adapter 或 gate 时，不会各写一套互相漂移的逻辑。

### 20.1 Project Setup Chain

Purpose:

- help a user start governing AI development in a project.

Chain:

`A01 capture intent -> A02 classify -> A03 read context -> A05 propose baseline rules -> A07 confirm -> A10 record decision -> A12 persist`

First product surfaces:

- conversational setup
- rule confirmation card
- later frontend onboarding

### 20.2 Natural-Language Rule Extraction Chain

Purpose:

- turn user working-method preferences into confirmable governance objects.

Chain:

`A01 capture intent -> A02 classify -> A04 infer surface -> A05 propose rule -> A06 choose layer -> A07 render confirmation -> A09 edit -> A10 record decision -> A12 persist`

First product surfaces:

- chat-native rule extraction
- confirmation card
- later visual rule editor

### 20.3 Task Start Chain

Purpose:

- make applicable rules visible before AI work begins.

Chain:

`A03 read context -> A04 infer surface -> A08 match triggers -> A13 request evidence -> A21 render summary`

First product surfaces:

- task-start checklist
- agent operating kernel
- later run-control console

### 20.4 Task Completion Chain

Purpose:

- stop AI from declaring completion without surfacing triggered governance obligations.

Chain:

`A08 match triggers -> A13 request evidence -> A14 attach evidence -> A15 escalate missing evidence -> A16 produce completion report -> A17 record acceptance`

First product surfaces:

- task-completion acceptance card
- checker report
- later run-control console

### 20.5 Failure-To-Rule Learning Chain

Purpose:

- convert a repeated AI-development failure into a future rule candidate.

Chain:

`A01 capture user feedback -> A02 classify -> A05 propose rule candidate -> A07 confirm -> A10 record decision -> A12 persist`

First product surfaces:

- conversational after-action review
- rule confirmation card
- later audit/evolution dashboard

### 20.6 Rule Evolution Chain

Purpose:

- safely change governance without hidden rule drift.

Chain:

`A03 read context -> A18 supersede or rollback -> A10 record decision -> A12 persist -> A19 project updated rule -> A21 summarize change`

First product surfaces:

- audit/evolution dashboard
- visual rule editor
- later gate promotion workflow

### 20.7 Multi-Agent Continuity Chain

Purpose:

- let Codex, Claude, and future agents share governance context without relying on memory alone.

Chain:

`A03 read context -> A19 project governance object -> A20 export/import agent context -> A21 render user-readable summary`

First product surfaces:

- handoff prompt
- portable context bundle
- later agent adapter

---

## 21. Product Surface Suitability Map

> **中文注释**：这里不是 UI 设计稿，而是判断什么动作适合放在哪种用户表面。前端很重要，但不是唯一入口。

| Product surface | Best suited actions | Why it fits |
|---|---|---|
| Conversational setup | A01, A02, A05, A21 | lowest friction for non-professional users describing working methods |
| Natural-language rule extraction | A01, A02, A04, A05 | lets users speak in ordinary language while preserving structured output |
| Rule confirmation card | A06, A07, A09, A10 | makes AI-proposed rules reviewable before activation |
| Task-start checklist | A03, A04, A08, A13, A21 | surfaces obligations before the agent starts changing files |
| Task-completion acceptance card | A13, A14, A15, A16, A17 | lets users accept, request fixes, or defer with evidence visible |
| Checker report | A08, A11, A13, A15 | good for deterministic trigger and missing-evidence visibility |
| Frontend rule configuration console | A06, A09, A10, A12, A18 | useful once rule schema is stable enough for visual editing |
| Frontend run-control console | A03, A08, A13, A14, A16, A17 | useful once task session and result models exist |
| Audit/evolution dashboard | A10, A12, A17, A18, A21 | helps users see how rules change over time |
| Future gate adapter | A08, A13, A15, A17, A19 | safe only after report-only behavior, false positives, and rollback are understood |

MVP implication:

- start with conversational setup, confirmation cards, checker reports, and task-completion acceptance records
- do not require a full frontend to validate the product concept
- do not implement blocking gates before report-only evidence matures

---

## 22. Handoff To `JIKUO-PRD-01`

> **中文注释**：PRD 应该从这些链路里长出来，而不是直接写功能想象。这个交接点决定后续产品定义的输入。

`JIKUO-PRD-01` may start after this Part 1 is accepted.

Required PRD inputs from this map:

- target and non-target user definitions
- scenario inventory
- rule source layers
- atomic action taxonomy
- recomposable chains
- product surface suitability map
- non-goals around product-output quality judgment
- rule activation safety principle: AI proposes, user confirms, system records

PRD should not start from:

- frontend screens first
- gate implementation first
- generic prompt-management features
- domain-content creation workflows

Recommended first PRD question:

- what is the smallest user-visible `机括` loop that lets an AI-primary developer express a working-method preference, confirm it as a rule, see it triggered in a task, and review evidence at completion?

---

## 23. Part 1 Acceptance Gate

> **中文注释**：这是 Part 1 暂停点。你验收后，才进入 `JIKUO-PRD-01` 或继续拆更细的 UX 子图。

Part 1 is ready for user review when:

- target users are limited to AI-primary software/application/system development users
- rule source layers are explicit
- scenario families are mapped to interaction paths
- atomic actions have input, output, owner, persistence, and approval expectations
- recomposable chain variants are defined
- product surfaces are classified without assuming frontend-first delivery
- handoff conditions for `JIKUO-PRD-01` are clear
- report-only checker smoke has been run

Do not continue to `JIKUO-PRD-01`, frontend design, core schema implementation, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 1 map.

---

## 24. Part 1 Acceptance Record

> **中文注释**：用户已确认继续，因此 Part 1 场景/动作地图可作为 `JIKUO-PRD-01` 输入。仍不代表 UI、gate 或实现已被批准。

Acceptance:

- user accepted the Part 1 map by saying `请继续`
- `JIKUO-PRD-01` may start from this scenario/action map

Still not accepted:

- frontend design
- core schema implementation
- JSON/result model implementation
- task session storage
- gate implementation
- `.codex/AGENTS.md` promotion
- Sprint 050 runtime hardening changes under this productization task

---

## 25. Part 1 Verification Log

> **中文注释**：这里记录 Part 1 实际跑过的检查。checker 仍然只是 report-only。

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md
```

Result:

- registry validation passed
- triggered `R-006` and `R-012`
- required fields and sections for `R-006` reported `OK`
- Sprint index document for `R-012` reported `OK`
- `sprint_index_entry` declaration remained `REVIEW`
- exit code `0`
- report-only posture preserved
