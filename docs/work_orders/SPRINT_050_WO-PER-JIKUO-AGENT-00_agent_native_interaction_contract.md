# SPRINT_050_WO-PER-JIKUO-AGENT-00: Desktop-Agent-First Interaction Contract

> **Date**: 2026-05-04  
> **Status**: Accepted by user; upstream desktop-agent-first contract for `JIKUO-CORE-01`  
> **Primary sprint**: Sprint 050 / contract-first hardening incubation  
> **Task type**: productization / interaction contract / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance productization; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`  
> **Current slice**: Part 1 accepted; `JIKUO-CORE-01` may use this as desktop-agent-first interaction input  
> **User scenario**: A Codex / Claude desktop APP user needs routine governance confirmations to happen inside the active chat workflow while preserving a shared project-local governance state; CLI support is auxiliary, not the primary interface.  
> **Runtime chain**: Project-local governance state -> desktop-agent card/report -> user approval phrase in Codex / Claude chat -> approval record -> optional agent-invoked CLI or frontend projection -> handoff summary.  
> **Canonical source**: accepted `JIKUO-PRD-01` current engineering-governance track and desktop-agent-first interaction posture.  
> **Bridge object**: desktop-agent card, approval, and handoff contract.  
> **Consumer projection**: `JIKUO-CORE-01`, future desktop card renderer, auxiliary CLI bridge, and frontend surfaces.  
> **Lifecycle**: accepted interaction contract; future surface changes require explicit supersession before adapter or frontend implementation.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 产品口径

> **中文注释**：本工单回答“机括如何不打断 Codex / Claude 桌面 APP 用户的连续性”。CLI 是辅助 bridge，不是主要界面。

The product-facing problem is that `机括` must work where the user already works.

For the current target user, primary surfaces are:

- Codex Desktop
- Claude Desktop

Supporting surfaces are:

- agent-invoked local report/checker commands
- optional Codex / Claude CLI for users who prefer terminal workflows
- later optional frontend

The product posture is:

- desktop-agent-first
- project-local state as the continuity anchor
- CLI as auxiliary bridge / fallback, not the default user interface
- frontend as configuration, control, and audit surface
- routine approvals available in the active Codex / Claude desktop chat flow when safe

Expected visible outcome after this contract is accepted:

- future desktop-agent, auxiliary CLI, and frontend work share the same card vocabulary
- user approvals have a minimum record shape
- Codex / Claude handoff has a defined summary shape
- frontend scope is clearer because common confirmations are not frontend-only

---

## 2. 技术口径

> **中文注释**：这是契约，不是实现。它只规定未来表面如何读写同一套治理对象。

Mainline changed:

- `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md` status / acceptance record

Mainline explicitly not changed:

- runtime narrative engine
- `tools/audit/check_rule_registry.py`
- `rule_registry.yaml`
- `.codex/AGENTS.md`
- Codex adapter behavior
- Claude adapter behavior
- CLI commands
- frontend implementation
- hooks, CI, task-stop, or blocking gates

Canonical source:

- accepted `JIKUO-PRD-01` desktop-agent-first interaction model

Bridge object:

- this desktop-agent-first interaction contract

Consumer projection:

- later `JIKUO-CORE-01` structured result model
- later `JIKUO-CORE-03` task session and evidence model
- later `JIKUO-AGENT-01` adapter/prompt integration
- later `JIKUO-UI-01` and `JIKUO-UI-02`

Lifecycle:

- Part 1 defines contract shapes
- user review accepts or revises the contract
- later implementation work may consume accepted shapes but must not silently change them

Rollback / supersession:

- if user rejects card or approval shape, revise this work order before CORE/AGENT implementation
- if later implementation needs a new field, add a supersession note rather than silently changing existing card semantics

---

## 3. Scope

Part 1 defines:

- desktop-agent-first interaction principles
- project-local canonical state boundary
- card contract families
- approval phrase contract
- approval record minimum fields
- auxiliary CLI bridge role
- Codex / Claude handoff summary shape
- frontend-vs-agent surface decision rules
- safety boundaries and non-goals

Part 1 may name conceptual CLI commands and files, but it must not implement them or choose final storage schema.

---

## 4. Out Of Scope

> **中文注释**：这些都不能在本片里做。尤其不能把契约写成真实命令、hook 或前端实现。

This work order does not:

- implement CLI commands
- implement Codex or Claude adapter behavior
- modify `.codex/AGENTS.md`
- modify `tools/audit/check_rule_registry.py`
- modify `rule_registry.yaml`
- create `.jikuo/` storage
- implement frontend UI
- implement JSON result output
- implement task session storage
- implement hooks, CI, task-stop, or blocking gates
- modify runtime narrative engine code
- define product-output quality evaluation rules
- implement Sprint 049 memory lifecycle work

Sprint 049 memory lifecycle boundary:

- this contract may use lifecycle language for governance objects only
- it must not implement or absorb Sprint 049 memory lifecycle features

---

## 5. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/sprints/insights/INDEX.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`
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

> **中文注释**：事前审计结论：可以定义桌面 APP 优先的交互契约；不能直接改 agent 规则、CLI、checker 或前端。

Task target:

- define how `机括` renders governance interactions in Codex / Claude desktop APP workflows while preserving canonical project-local state; CLI remains an auxiliary bridge

Compliance status:

- aligned with `JIKUO-PRD-01` because desktop-agent-first is now the refined product interaction posture
- aligned with `JIKUO-UX-00` because it maps product surfaces back to atomic actions
- aligned with `05B` because cards and approvals are materialized governance surfaces, not product-output judgments
- aligned with `05D` and `05F` because no checker behavior or gate behavior changes in this slice

Required adjustments:

- keep all examples about engineering governance, not domain content review
- keep approvals explicit enough to be auditable
- keep frontend and CLI as optional for routine confirmations
- do not choose final storage schema in this slice

---

## 7. Contract Principles

> **中文注释**：这些原则是后续 Codex / Claude 桌面 APP、辅助 CLI bridge 和前端都要遵守的共同契约。

1. Codex / Claude desktop APP chat is the primary user interaction path.
2. Project-local canonical state wins over any single chat history.
3. Desktop-agent cards are projections, not canonical truth.
4. User approval must identify the target being approved.
5. Routine confirmations may happen in chat when the card is explicit.
6. Ambiguous approval phrases should become follow-up questions, not silent writes.
7. CLI should be agent-invoked or optional unless the user explicitly chooses a terminal workflow.
8. CLI and frontend must render the same underlying governance object when possible.
9. Blocking behavior is not part of this contract unless a future gate work order explicitly promotes it.
10. Product-output quality conclusions stay outside this contract.

---

## 8. Project-Local Canonical State Boundary

> **中文注释**：这里先定义边界，不选最终目录名。真正 `.jikuo/` 或 schema 要等 CORE 工单。

Canonical governance state should eventually include:

- active rule records
- candidate rule records
- approval records
- task session records
- evidence records
- rule supersession records
- adapter projection metadata

This contract does not choose final storage:

- it may later be `.jikuo/`
- it may later extend `docs/scenarios/.../governance/`
- it may later use another project-local location

Minimum invariant:

- Codex Desktop, Claude Desktop, auxiliary CLI tools, and frontend should treat project-local governance state as the durable source of truth.
- Chat messages may reference, propose, or approve governance objects, but chat memory is not canonical storage.

---

## 9. Desktop-Agent Card Families

> **中文注释**：卡片是 Codex / Claude 桌面 APP 对话里的小界面。它们应该足够结构化，让用户不用切前端或 CLI 也能安全批准。

All cards should include:

- card type
- card id
- target object id or candidate id
- current phase
- proposed user action
- allowed responses
- evidence or consequence summary
- storage effect if accepted

| Card family | Purpose | Typical user action | Storage effect |
|---|---|---|---|
| Rule Confirmation Card | Review an AI-proposed rule before activation | accept, edit, reject, defer | creates or updates rule decision record |
| Task Start Governance Card | Show active rules relevant to a task before work begins | acknowledge, ask for adjustment, add one-time constraint | creates task-start context record |
| Missing Evidence Card | Show triggered obligations without enough evidence | provide evidence, defer, request fix | updates evidence or follow-up record |
| Completion Acceptance Card | Review task completion against triggered governance obligations | accept, request changes, defer | creates task acceptance record |
| Rule Evolution Card | Review a rule promotion, pause, rollback, or supersession | approve, revise, reject | creates supersession or promotion record |
| Handoff Summary Card | Carry governance context between Codex and Claude | use summary, refresh state, request repair | creates or references handoff record |

---

## 10. Approval Phrase Contract

> **中文注释**：普通用户不应该被迫输入复杂命令，但批准语句必须足够明确，不能靠 AI 猜。

Approval phrases have three levels.

| Level | Meaning | Allowed use |
|---|---|---|
| explicit approval | names the decision and target | persistent rule activation, enforcement promotion, task acceptance with missing evidence |
| context-bound approval | short approval immediately after a clear card | routine task acceptance, report-only rule confirmation, one-time task constraint |
| ambiguous approval | unclear target or effect | must trigger a clarification question |

Examples of explicit approval:

- `批准：激活为 project rule，phase=report_only`
- `批准：本次任务完成，记录缺失证据为 follow-up`
- `拒绝：不写入项目规则`
- `暂停：作为 one-time constraint，不持久化`

Examples of context-bound approval:

- `同意`
- `通过`
- `请继续`

Context-bound approval is valid only when:

- the immediately preceding card states exactly what will be recorded
- there is only one pending approval target
- the operation is not enforcement promotion beyond report-only
- the operation is not global agent-rule modification

Ambiguous approval handling:

- if multiple cards are pending, ask which one the user means
- if the storage effect is unclear, restate the effect and ask for confirmation
- if enforcement would become blocking, require explicit approval

---

## 11. Approval Record Minimum Fields

> **中文注释**：批准不是一句聊天记忆。它必须落成可审计记录。

Approval record must include at least:

- approval id
- card id
- target object id
- decision
- exact user phrase
- source surface
- actor label
- timestamp
- storage effect
- enforcement effect
- rollback availability

Source surface examples:

- `codex_desktop_chat`
- `claude_desktop_chat`
- `codex_cli`
- `claude_cli`
- `local_cli`
- `frontend`

Actor label may be simple in early MVP:

- `human_user`

This contract does not define authentication or identity verification.

---

## 12. Auxiliary CLI Bridge Contract

> **中文注释**：CLI 是给 agent 或高级用户调用的本地状态/报告 bridge，不是本产品对 Codex / Claude 桌面用户的主要交互界面。

Conceptual CLI roles:

- render governance cards as text
- read project-local governance state
- report triggered obligations
- validate card/approval record shape
- append accepted approval records when explicitly instructed by the user or by an authorized desktop-agent flow
- export handoff summaries

Conceptual commands may later look like:

- `jikuo report`
- `jikuo render-card`
- `jikuo propose-rule`
- `jikuo record-approval`
- `jikuo handoff`

These commands are examples only.

This work order does not implement them.

CLI should not:

- infer approval without explicit input
- promote report-only rules to blocking
- become the only way to complete routine approvals
- become the default interaction surface for Codex / Claude desktop users
- bypass the same approval record shape required by chat and frontend

---

## 13. Codex / Claude Handoff Summary Shape

> **中文注释**：handoff 的目标是让用户在 Codex 和 Claude 之间切换时，机括状态不断线。

Handoff summary should include:

- product / project name
- active governance pack
- active project rules
- current task if any
- pending cards
- triggered obligations if any
- missing evidence if any
- last accepted decision
- forbidden next steps
- recommended next step
- canonical state reference

Handoff summary should not include:

- full raw logs by default
- hidden chain-of-thought or private reasoning
- product-output quality conclusions
- unconfirmed candidate rules as if they were active

Handoff user experience:

- source agent produces a concise handoff card
- target agent reads the handoff and canonical state reference
- target agent reports whether it can continue, needs refresh, or sees conflicts

---

## 14. Frontend Vs Agent Surface Decision Rules

> **中文注释**：不是所有事情都要进前端。这里先定义什么适合在 agent 内完成，什么适合前端。

Use desktop-agent chat/cards when:

- the user is already in a Codex / Claude task
- the decision is local to the current task
- the card has a single clear target
- approval does not promote enforcement beyond report-only
- user continuity matters more than visual browsing

Use CLI when:

- a deterministic report is needed
- another agent needs portable state
- the desktop agent needs a local bridge to read/write/report state
- the user explicitly wants a quick terminal check
- scripts or future adapters need a stable text/JSON interface

Use frontend when:

- many rules need browsing or bulk editing
- history and audit trails need visual review
- cross-task comparison is needed
- enforcement promotion requires a deliberate review surface
- non-technical users need safer guided editing than raw files

Use future gate only when:

- report-only false positives are understood
- rollback exists
- user explicitly approves promotion
- the target rule has stable structured evidence

---

## 15. Safety Boundaries

> **中文注释**：desktop-agent-first 并不等于随便在聊天里改规则。这里是防漂移边界。

Desktop-agent surfaces must not:

- silently activate candidate rules
- silently change enforcement phase
- silently write global agent rules
- accept ambiguous approval when multiple targets are pending
- claim frontend approval happened when it did not
- treat product-output quality conclusions as engineering-governance facts

Desktop-agent surfaces should:

- show the storage effect before asking for approval
- require explicit approval for persistent or high-impact changes
- include rollback notes when rules are changed
- make missing evidence visible without prematurely blocking
- allow the user to continue work inside Codex / Claude desktop APPs when safe

---

## 16. Testing Governance Declaration

> **中文注释**：这是交互契约文档，不改变任何工具或产品行为。

Required test layers for this slice:

- `unit`: N/A because no code changes are planned.
- `integration`: N/A because no CLI, frontend, checker, hook, CI, or adapter integration is planned.
- `workflow/orchestration`: required by contract review and card/approval chain consistency review.
- `semantic regression`: N/A because no product behavior changes.
- `smoke`: required; run the report-only checker against the new work order path.
- `human semantic review`: N/A for product semantics because this slice does not change product behavior or product content evaluation.
- `human governance review`: required for approval phrase boundaries, handoff shape, and frontend-vs-desktop-agent rules.

---

## 17. Part 1 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P1-DC-01 | Define desktop-agent-first interaction principles | Section 7 exists |
| P1-DC-02 | Define project-local canonical state boundary | Section 8 exists |
| P1-DC-03 | Define card families | Section 9 exists |
| P1-DC-04 | Define approval phrase contract | Section 10 exists |
| P1-DC-05 | Define approval record fields | Section 11 exists |
| P1-DC-06 | Define auxiliary CLI bridge role | Section 12 exists |
| P1-DC-07 | Define Codex / Claude handoff shape | Section 13 exists |
| P1-DC-08 | Define frontend-vs-desktop-agent decision rules | Section 14 exists |
| P1-DC-09 | Preserve implementation boundary | No CLI, adapter, frontend, checker, registry, hook, CI, `.codex/AGENTS.md`, or runtime code is changed |
| P1-DC-10 | Run report-only checker smoke | Verification log records checker result |

---

## 18. Acceptance Gate For Part 1

> **中文注释**：这是 `JIKUO-AGENT-00` 的第一片暂停点。你验收后，才继续 CORE/result model 或更细的 agent adapter 设计。

Part 1 is ready for user review when:

- desktop-agent-first is expressed as an interaction contract
- card families are clear enough for future Codex / Claude desktop rendering
- approval phrase boundaries protect against accidental writes
- CLI is positioned as an auxiliary bridge, not the primary interface
- Codex / Claude handoff shape is defined
- frontend remains optional for routine confirmations
- no implementation has been added
- checker smoke has been run

Do not continue to `JIKUO-CORE-01`, `JIKUO-AGENT-01`, CLI implementation, frontend design, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 1 contract.

---

## 19. Part 1 Verification Log

> **中文注释**：这里记录 Part 1 实际跑过的检查。checker 仍然只是 report-only。

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md
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

## 20. Part 1 Acceptance Record

> **中文注释**：用户已确认继续，因此本交互契约可以作为 `JIKUO-CORE-01` 的上游输入。仍不代表 CLI、adapter、前端、gate 或 checker JSON 输出已经被批准实现。

Acceptance:

- user accepted the revised Part 1 contract by saying `请继续`
- `JIKUO-CORE-01` may start from the desktop-agent-first interaction contract

Still not accepted:

- Codex / Claude adapter implementation
- CLI command implementation
- checker JSON output implementation
- frontend implementation
- gate implementation
- `.codex/AGENTS.md` promotion
- Sprint 050 runtime hardening changes under this productization task
