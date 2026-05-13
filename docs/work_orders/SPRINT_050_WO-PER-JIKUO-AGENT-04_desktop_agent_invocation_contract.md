# SPRINT_050_WO-PER-JIKUO-AGENT-04: Desktop Agent Invocation Contract

> **Date**: 2026-05-05  
> **Status**: Accepted by user for downstream `agent_flow.py` implementation  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / desktop-agent invocation contract / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `JIKUO-FLOW-02` Desktop App Primary Operating Loop; `JIKUO-AGENT-00` desktop-agent-first interaction contract; `JIKUO-AGENT-01` card projection contract; `JIKUO-AGENT-02` task-session workflow cards; `JIKUO-AGENT-03` minimal no-write card projection helper; `jikuo_execution_mounts.md`  
> **Current slice**: desktop-agent invocation contract only; no `agent_flow.py`, Skill, MCP server, plugin, frontend, automatic write, gate, registry migration, checker migration, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user wants to trigger JIKUO inside the active chat, let the agent call internal governance atoms when appropriate, review the resulting card or summary in the same chat, and approve or reject any durable write without switching to CLI for routine work.  
> **Runtime chain**: user chat intent -> explicit JIKUO trigger or agent-suggested trigger -> desktop agent classifies invocation scenario -> desktop agent may call no-write internal atoms -> desktop agent renders card/summary in the same chat -> user approves, rejects, defers, or modifies -> desktop agent may execute only the explicitly approved guarded action -> desktop agent reports result / missing evidence / handoff in the same chat.  
> **Canonical source**: accepted Desktop App Primary Operating Loop, accepted card/task-session contracts, implemented no-write card projection helper, project-local state contracts, and explicit user decisions in chat.  
> **Bridge object**: `JikuoDesktopAgentInvocationContractV0`; `JikuoAgentTriggerDecisionV0`; `JikuoDesktopInvocationCardV0`; `JikuoDesktopApprovalLoopV0`.  
> **Consumer projection**: Codex Desktop chat instructions, Claude Desktop chat instructions, future `agent_flow.py`, future Codex Skill / Agent instruction, future MCP tool, future Codex Plugin, future CLI fallback, future frontend configuration/control/audit views.  
> **Lifecycle**: draft invocation contract -> user review -> accepted invocation contract -> `agent_flow.py` planning -> Skill / Agent instruction planning -> MCP tool planning -> plugin / frontend planning.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, no-write root state smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：这张工单回答“用户在 Codex / Claude 桌面 APP 里到底怎么启动机括”。它不是再造一个 helper，而是把已有原子能力接回用户的日常操作链路。

Before this slice, JIKUO already had:

- project-state atoms
- task-session atoms
- guarded write atoms
- card projection atoms
- a Desktop App Primary Operating Loop

But the user-facing start point was still not explicit enough.

The product problem is:

- the user mainly works in Codex / Claude desktop APP chat
- helper commands are useful atoms, but not the ordinary user path
- pure natural-language expectation is too probabilistic for critical governance actions
- frontend is useful later, but should not be required for routine task start, approval, completion, or handoff
- the user needs a low-cost way to say "use JIKUO now" and see the result in the same chat

This work order defines the desktop invocation contract:

- explicit low-cost trigger shortcuts
- agent-suggested trigger conditions
- no-write internal atom invocation rules
- guarded-write approval boundaries
- chat-native card / summary rendering
- ambiguity and refusal behavior
- handoff and continuation expectations

Visible product effect after acceptance:

- the user can know when JIKUO is active
- the agent has a concrete invocation rule instead of relying on long memory
- routine operation stays in the desktop APP chat
- `agent_flow.py` can be implemented as a deterministic local runner against a stable contract

---

## 2. Technical Boundary

> **中文注释**：本工单只定义调用契约，不实现调用器。也就是说，它告诉 Agent 什么时候该调用、能调用什么、必须怎么展示和等待批准，但不新增真正执行主流程的代码。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

Mainline explicitly not changed:

- `tools/jikuo/agent_flow.py`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_cards.py`
- `tools/jikuo/project_state.py`
- `tools/audit/check_rule_registry.py`
- `.codex/AGENTS.md`
- `.jikuo/project_state.yaml`
- `.jikuo/task_sessions/`
- Codex adapter behavior
- Claude adapter behavior
- Skill installation
- MCP server implementation
- Codex Plugin implementation
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine code

Canonical source:

- accepted `JIKUO-FLOW-02` Desktop App Primary Operating Loop
- accepted `JIKUO-AGENT-00` desktop-agent-first interaction contract
- accepted `JIKUO-AGENT-01` card projection contract
- accepted `JIKUO-AGENT-02` task-session workflow card contract
- implemented `JIKUO-AGENT-03` no-write card projection atom
- accepted task-session and project-state sidecar contracts
- explicit user approval inside the active desktop APP chat

Bridge objects:

- `JikuoDesktopAgentInvocationContractV0`
- `JikuoAgentTriggerDecisionV0`
- `JikuoDesktopInvocationCardV0`
- `JikuoDesktopApprovalLoopV0`

Consumer projection:

- current Codex / Claude desktop APP agent behavior guidance
- future deterministic `agent_flow.py`
- future Codex Skill / Agent instruction
- future MCP tool wrapper
- future Codex Plugin
- future frontend rule / audit / run-control views

Lifecycle:

- user intent appears in desktop chat
- trigger is explicit or agent-suggested
- agent classifies invocation scenario
- agent may call no-write atoms immediately when safe
- agent renders card / summary in the same chat
- user approves, rejects, defers, or modifies
- durable write runs only after explicit approval
- result or refusal is rendered back into the same chat

Rollback / supersession:

- if users reject the trigger model, revise this document before implementing `agent_flow.py`
- if later `agent_flow.py` needs a new trigger state, supersede this contract explicitly
- if Skill / MCP / plugin behavior differs from this contract, update this contract or record an explicit downstream divergence
- never silently promote chat hints into durable writes

Propagation surfaces:

- this work order
- productization task map
- execution mount
- Sprint index
- future runner contract
- future Skill / MCP / plugin instructions

Observability:

- future implementation should expose trigger source, invocation scenario, called atom, card id, approval target, exact user phrase when approved, executed command kind, refusal reason, and resulting state reference

---

## 3. Scope

This work order defines:

- desktop invocation principles
- explicit trigger shortcuts
- agent-suggested trigger conditions
- trigger decision object
- invocation scenario families
- internal atom invocation rules
- card / summary rendering rules
- approval / rejection / modification loop
- refusal and ambiguity handling
- desktop continuity and handoff rules
- `agent_flow.py` downstream requirements
- testing-governance declaration

---

## 4. Out Of Scope

This work order does not:

- implement `agent_flow.py`
- implement automatic shell invocation
- install or modify a Codex Skill
- implement an MCP server
- implement a Codex Plugin
- implement frontend screens
- create task-session files
- update `.jikuo/project_state.yaml`
- run guarded writes automatically
- change checker behavior
- migrate rule registry behavior
- edit `.codex/AGENTS.md`
- promote report-only checks into gates
- judge product-output quality
- change narrative runtime behavior

---

## 5. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md`
- `tools/jikuo/project_state.py`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_cards.py`
- `tools/audit/check_rule_registry.py`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 6. Pre-Audit

> **中文注释**：事前审计结论：可以定义桌面调用契约；不能跳到实现 runner、Skill、MCP 或前端；也不能把“AI 应该记得”当成可靠触发机制。

Task target:

- define how Codex / Claude desktop APP agents invoke JIKUO from ordinary chat workflow before implementing a deterministic local runner

Compliance status:

- aligned with Desktop App Primary Operating Loop because ordinary user operation remains in the active desktop chat
- aligned with atomic capability registry because existing helpers remain internal atoms, not direct user workflow
- aligned with approval safety because guarded writes still require target/effect/non-effect and explicit user approval
- aligned with report-only posture because this slice does not add gates or blocking behavior
- aligned with product-output boundary because this governs engineering process, not output quality evaluation

Required adjustments:

- define actual low-cost trigger shortcuts without making them the only valid user phrasing
- separate explicit trigger from agent-suggested trigger
- let no-write atoms run when safe, but require approval for durable writes
- render cards / summaries back into the same chat
- preserve CLI as internal bridge / advanced fallback only
- keep `agent_flow.py` as the next implementation slice, not this slice

---

## 7. Invocation Principles

1. Desktop APP chat is the primary invocation surface.
2. The user should be able to explicitly start JIKUO with a short, learnable trigger.
3. The agent may suggest JIKUO when the current task matches known governance scenarios.
4. Critical invocation must not depend only on the agent remembering long prose instructions.
5. No-write inspection and preview atoms may be called by the agent when they only produce a report/card.
6. Durable writes require a card, explicit target/effect/non-effect, and user approval.
7. CLI commands are internal atoms or advanced fallback, not routine user steps.
8. The agent must return cards / summaries in the same desktop chat.
9. Ambiguity must stop the write path and ask for clarification.
10. Product-output quality judgement remains outside this invocation contract.

---

## 8. Explicit Trigger Shortcuts

> **中文注释**：这里定义的是推荐快捷触发词，不是说用户只能逐字这么说。目标是给普通用户一个低学习成本入口，也给 Agent 一个明确可执行的信号。

Supported shortcut family:

| User intent | Recommended shortcut | Agent response |
|---|---|---|
| Start JIKUO for a new task | `机括：开始` | classify task-start governance scenario and show start card / summary |
| Continue under JIKUO | `机括：继续` | inspect current project/task state and show continuation summary |
| Show current JIKUO state | `机括：状态` | inspect project-state / task-session state with no-write atoms |
| Review before completion | `机括：验收` | show completion / missing evidence / verification summary |
| Prepare handoff | `机括：交接` | show handoff card / required reads / pending decisions |
| Run governance audit for current task | `机括：审计` | run report-only checker / relevant no-write previews when applicable |
| Configure or propose a rule | `机括：规则` | route to rule candidate / document mount / governance preference flow |

Shortcut rules:

- shortcuts are recommended interaction handles, not mandatory exact-only phrases
- natural-language equivalents may trigger the same intent when the agent can classify them confidently
- if confidence is low, the agent should ask whether the user wants to start JIKUO
- examples of recorded approval phrases must still use `"<exact user phrase as spoken>"`
- shortcut recognition alone never approves a durable write

---

## 9. Agent-Suggested Trigger Conditions

The agent should suggest JIKUO when the user intent likely involves:

- starting a substantial coding / design / documentation task
- continuing a previously governed task
- accepting completion or asking "what is left"
- switching between Codex and Claude
- declaring required reference documents
- asking for a rule, preference, working method, or audit obligation to be remembered
- changing a schema, contract, governance rule, or project-local state
- requesting gate / enforcement / blocking behavior
- asking to stage, commit, release, or produce a handoff
- touching JIKUO productization itself

Suggested-trigger wording:

- the agent should briefly state why JIKUO might apply
- the agent should ask for approval before creating durable state
- the agent may run no-write inspection first when that only improves the proposed card

Example pattern:

```text
This looks like a governed task start. I can run the JIKUO no-write preview and show the card here before any write.
```

Do not:

- silently create task-session files from a suggestion
- silently update project-state index from a suggestion
- treat "continue" as approval for every pending card
- use keyword-only matching as the future implementation model

---

## 10. Trigger Decision Object

Conceptual shape:

```yaml
trigger_decision:
  schema: "jikuo.agent_trigger_decision.v0"
  trigger_source: "explicit_user_shortcut"
  user_phrase: "<exact user phrase as spoken>"
  invocation_scenario: "task_start"
  confidence: "event_match"
  confidence_basis: "canonical_event_mapping"
  trigger_match:
    status: "matched"
    basis: "canonical_event_mapping"
  intent_classification:
    confidence: "not_evaluated_by_runner"
    basis: "agent_supplied_event_arg"
  execution_readiness: "ready"
  may_call_no_write_atoms: true
  may_request_guarded_write: true
  durable_write_approved: false
  required_clarification: []
```

Required fields:

- `schema`
- `trigger_source`
- `user_phrase`
- `invocation_scenario`
- `confidence`
- `confidence_basis`
- `trigger_match`
- `intent_classification`
- `execution_readiness`
- `may_call_no_write_atoms`
- `may_request_guarded_write`
- `durable_write_approved`
- `required_clarification`

Allowed `trigger_source` values:

- `explicit_user_shortcut`
- `explicit_user_natural_language`
- `agent_suggested`
- `handoff_resume`
- `internal_followup`

Allowed `invocation_scenario` values:

- `project_status`
- `task_start`
- `task_continue`
- `rule_candidate`
- `document_mount`
- `evidence_review`
- `completion_review`
- `handoff`
- `audit_report`
- `enforcement_change`
- `ambiguous`

---

## 11. Invocation Scenario Families

### 11.1 Project Status

Purpose:

- tell the user whether JIKUO project-local state exists and what can be done next

Allowed no-write atoms:

- `project_state.py status`
- `project_state.py init --dry-run`
- task-session status / index dry-run when project state exists

Durable writes:

- project-state init requires explicit approval and guarded command

### 11.2 Task Start

Purpose:

- start governance for a substantial AI-assisted work item

Allowed no-write atoms:

- task-session start dry-run
- task-session start-preview card
- report-only checker when changed paths or work-order paths are known

Durable writes:

- task-session creation requires explicit approval
- project-state index refresh remains a separate approval

### 11.3 Task Continue

Purpose:

- continue an existing governed task without relying on chat memory alone

Allowed no-write atoms:

- task-session status
- project-state status
- index dry-run
- card projection from existing task-session data

Durable writes:

- evidence, verification, completion, or handoff append require explicit target session id and approval

### 11.4 Rule Candidate

Purpose:

- turn a user-stated working preference into a candidate governance rule

Allowed no-write atoms:

- rule candidate card
- required evidence / trigger summary
- affected layer summary

Durable writes:

- persistent rule activation remains out of scope until a later rule-persistence contract

### 11.5 Document Mount

Purpose:

- make required reference files visible for a task or rule layer

Allowed no-write atoms:

- document mount card
- required-read list
- missing-reference report

Durable writes:

- persistent document-mount record remains out of scope unless a later contract approves it

### 11.6 Completion Review

Purpose:

- summarize work result, verification, triggered obligations, missing evidence, and user decision target

Allowed no-write atoms:

- checker report-only run
- card projection
- task-session update dry-run

Durable writes:

- completion update requires explicit session id and approval
- completion approval does not imply handoff approval

### 11.7 Handoff

Purpose:

- carry governance continuity between Codex, Claude, or later sessions

Allowed no-write atoms:

- task-session status
- handoff preview
- required reads summary

Durable writes:

- handoff write requires explicit approval

---

## 12. Internal Atom Invocation Rules

> **中文注释**：这里把“Agent 可自动调用什么”和“必须等用户批准什么”分开。这样用户不用切 CLI，但写入边界仍然硬。

The desktop agent may call these no-write atoms without separate user approval when they are needed to render a card or summary:

- project-state status
- project-state init dry-run
- task-session status
- task-session start dry-run
- task-session index dry-run
- task-session update dry-run
- task-session card projection helper
- report-only rule checker

The desktop agent must not call these durable-write atoms until the user explicitly approves the specific card/effect:

- project-state init write
- task-session start write
- task-session index refresh
- task-session evidence append
- task-session verification append
- task-session completion update
- task-session handoff update
- any future rule persistence write
- any future enforcement promotion write

The desktop agent must refuse or ask for clarification when:

- multiple approval cards are pending
- session id is ambiguous
- write target is not shown
- effect and non-effect were not shown
- user phrase is context-bound but the preceding card is stale
- requested action is outside the accepted JIKUO productization sequence
- requested action would require frontend / MCP / plugin / gate behavior not yet implemented

---

## 13. Chat Rendering Rules

Every JIKUO invocation response in desktop chat should include:

- trigger source
- invocation scenario
- what was inspected or projected
- whether any durable write is proposed
- approval target if a write is proposed
- effect and non-effect
- next safe actions

Short chat card pattern:

```markdown
**机括卡片**
触发：...
场景：...
已检查：...
建议动作：...
写入影响：...
不会做：...
需要你确认：...
```

Rendering rules:

- show user-facing meaning before command details
- show no-write status before approval request
- show refusal reasons instead of command preview when preflight refuses
- avoid making CLI commands the center of the user experience
- keep detailed command preview available for auditability

---

## 14. Approval / Rejection / Modification Loop

The loop:

1. Agent renders card / summary.
2. User approves, rejects, defers, or asks to modify inside the same chat.
3. Agent maps the response to one card id and one effect.
4. If approved and durable, agent runs only the corresponding guarded action.
5. Agent reports the result in the same chat.
6. If rejected or deferred, agent records no durable write unless a separate accepted record path exists.

Approval rules:

- one approval maps to one card and one durable effect
- exact user phrase should be preserved as `"<exact user phrase as spoken>"`
- context-bound approval is allowed only for the immediately preceding clear card
- persistent rule changes and enforcement promotion require explicit scope
- task-session creation does not approve project-state index refresh
- completion does not approve handoff
- handoff does not reopen completion

Modification rules:

- user edits to card content should produce a revised card, not immediate write
- if the target changes, prior approval request is superseded
- if the effect changes, approval must be requested again

---

## 15. Refusal And Ambiguity Handling

The agent must refuse or clarify instead of proceeding when:

- no project-local state exists and the requested action requires it
- task-session id is missing or ambiguous
- project root is unclear
- user asks for a durable write but no card has shown target/effect/non-effect
- the action would write raw chat transcript
- the action would evaluate product-output quality as engineering-governance fact
- the action would promote a report-only rule into a gate without approved gate contract
- the requested next step jumps ahead of the accepted execution order

Refusal card must show:

- attempted action
- refusal reason
- what was not written
- safe next action

---

## 16. Desktop Continuity And Handoff

When continuing in the same desktop APP:

- agent should state whether JIKUO is active for the current task
- agent should prefer project-local task-session state over chat memory if it exists
- agent should re-render a concise status card when context may be stale

When switching between Codex and Claude:

- source agent should produce a handoff card
- target agent should read the handoff and required local references
- target agent should restate current session id and pending approvals
- target agent must not assume a write happened unless the project-local record exists

When no task-session exists:

- agent may offer a start preview
- agent must not claim durable governance is already active

---

## 17. Downstream `agent_flow.py` Requirements

`agent_flow.py` should be planned only after this contract is accepted.

Minimum future commands may include:

```powershell
python -B tools/jikuo/agent_flow.py propose --event "<event>" --task-title "<task title>" --format markdown
```

```powershell
python -B tools/jikuo/agent_flow.py apply --card-id "<card id>" --approval-phrase "<exact user phrase as spoken>" --format json
```

The runner should:

- compose existing atoms
- follow `JIKUO-FLOW-02` section `Loop Composition Map`
- report loop step ids and atom ids in structured trace output
- default to no-write proposal mode
- render chat-ready Markdown
- return JSON for future MCP / frontend consumers
- validate approval target before running a guarded write
- preserve exact approval phrase
- refuse ambiguous or stale cards
- avoid becoming a new parallel policy engine

The runner should not:

- invent new rule semantics
- judge product-output quality
- bypass task-session helper confirmations
- write raw chat transcript
- implement frontend-only configuration
- implement MCP or plugin behavior directly

---

## 18. Testing Governance Declaration

> **中文注释**：本工单是调用契约文档，不改代码。测试重点是链路完整性、规则触发报告、无写入确认，而不是产品输出内容评价。

- `unit`: N/A because no parser, runner, adapter, MCP tool, plugin, or frontend code is implemented.
- `integration`: N/A because no desktop APP adapter, local runner, storage adapter, or tool server is implemented.
- `workflow/orchestration`: required by contract review; trigger -> atom invocation -> card rendering -> approval loop -> refusal / result reporting must be covered by the document.
- `semantic regression`: N/A because no narrative/product runtime behavior changes.
- `smoke`: required; run report-only checker against this new work order and updated planning docs.
- `no-write smoke`: required; verify root `.jikuo/task_sessions/` remains absent and root `latest_task_session_refs` remains unchanged.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for trigger clarity, approval boundary clarity, desktop continuity, and no-CLI routine use.

---

## 19. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| A4-DC-01 | Declare deterministic work-order header fields | Header exists |
| A4-DC-02 | Define product meaning and user-facing problem | Section 1 exists |
| A4-DC-03 | Preserve no-implementation boundary | Sections 2 and 4 exist |
| A4-DC-04 | Include audit references and pre-audit | Sections 5 and 6 exist |
| A4-DC-05 | Define invocation principles | Section 7 exists |
| A4-DC-06 | Define explicit trigger shortcuts | Section 8 exists |
| A4-DC-07 | Define agent-suggested trigger conditions | Section 9 exists |
| A4-DC-08 | Define trigger decision object | Section 10 exists |
| A4-DC-09 | Define invocation scenario families | Section 11 exists |
| A4-DC-10 | Define internal atom invocation rules | Section 12 exists |
| A4-DC-11 | Define chat rendering and approval loop | Sections 13 and 14 exist |
| A4-DC-12 | Define refusal, continuity, and downstream runner requirements | Sections 15 through 17 exist |
| A4-DC-13 | Declare testing-governance layers | Section 18 exists |
| A4-DC-14 | Update productization task map, execution mount, and Sprint index | Verification log records changed docs |
| A4-DC-15 | Run report-only checker smoke | Verification log records checker result |
| A4-DC-16 | Preserve no-write root state | Verification log records no-write result |

---

## 20. Acceptance Gate

This work order is ready for user review when:

- the user can understand the recommended JIKUO trigger shortcuts
- the user can see that shortcut phrases are helpers, not rigid mandatory commands
- agent-suggested trigger conditions are concrete enough for future runner / skill planning
- no-write atoms and durable-write atoms are separated
- chat rendering and approval loop keep routine use inside Codex / Claude desktop APP
- refusal and ambiguity handling prevent stale or hidden writes
- `agent_flow.py` requirements are clear enough for the next implementation slice
- no runner, Skill, MCP, plugin, frontend, gate, checker migration, registry migration, `.codex/AGENTS.md` edit, or runtime change is silently approved

Do not continue to `agent_flow.py`, Skill / Agent instruction, MCP tool, Codex Plugin, frontend, or gate implementation until the user accepts or revises this invocation contract.

---

## 21. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md
```

```powershell
Test-Path D:\personal_project\NarrativeSystem\.jikuo\task_sessions
Select-String -Path D:\personal_project\NarrativeSystem\.jikuo\project_state.yaml -Pattern 'latest_task_session_refs' -Context 0,1
```

Expected result:

- report-only checker exits `0`
- deterministic work-order fields and required sections pass
- root `.jikuo/task_sessions/` remains absent
- root `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Actual result:

- report-only checker exited `0`
- registry validation passed
- triggered `R-006` and `R-012`
- `Status`, `Primary sprint`, `Task type`, `Scope`, `Out Of Scope`, `Audit References`, `Delivery Criteria`, and `Acceptance Gate` reported `OK`
- Sprint index document requirement reported `OK`
- `sprint_index_entry` remained `REVIEW`, as expected for the current report-only checker
- root `.jikuo/task_sessions/` remained absent
- root `.jikuo/project_state.yaml` still had `latest_task_session_refs: []`

Composition map addendum result:

- downstream `agent_flow.py` requirements now explicitly say the runner should follow `JIKUO-FLOW-02` section `Loop Composition Map`
- future structured trace should report loop step ids and atom ids
- report-only checker exited `0` for the addendum check
- root `.jikuo/task_sessions/` remained absent
- root `.jikuo/project_state.yaml` still had `latest_task_session_refs: []`

---

## 22. Current Acceptance Record

> **中文注释**：用户已要求继续，因此本调用契约可作为 `agent_flow.py` 的上游契约。接受本契约不等于批准 Skill、MCP、Plugin、前端或自动写入。

Decision:

- user accepted this desktop-agent invocation contract for downstream local deterministic `agent_flow.py` implementation by asking to continue

Still not approved:

- Codex Skill / Agent instruction
- MCP tool wrapper
- Codex Plugin
- frontend implementation
- automatic durable write
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
