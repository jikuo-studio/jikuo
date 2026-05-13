# SPRINT_050_WO-PER-JIKUO-AGENT-02: Desktop-Agent Task-Session Workflow Cards And Command Composition

> **Date**: 2026-05-05
> **Status**: Draft, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / desktop-agent workflow card contract / governance documentation work order
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`; `SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`; `SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md`; `SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md`; `SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md`; `docs/jikuo/schemas/task_session.schema.md`
> **Current slice**: desktop-agent task-session workflow card and command-composition contract only; no renderer, adapter, automatic write, frontend, gate, checker migration, registry migration, or runtime implementation
> **User scenario**: A Codex / Claude desktop APP user wants task-session start, index refresh, evidence append, verification append, completion, and handoff actions to appear as understandable chat workflow cards before any guarded local command is run.
> **Runtime chain**: task intent -> task-session dry-run command -> desktop workflow card -> exact user approval phrase if a write is requested -> guarded helper command -> structured command result -> evidence / completion / handoff card -> optional next-agent summary.
> **Canonical source**: accepted task-session contracts, `tools/jikuo/task_session.py` structured command outputs, accepted desktop card projection contract, and explicit user decisions.
> **Bridge object**: `JikuoDesktopTaskSessionWorkflowCardV0`; `JikuoDesktopCommandProposalV0`; `JikuoDesktopApprovalCaptureV0`; `JikuoDesktopHandoffWorkflowCardV0`.
> **Consumer projection**: Codex Desktop chat, Claude Desktop chat, future auxiliary CLI markdown, future frontend preview, and future audit view.
> **Lifecycle**: draft workflow contract -> user review -> accepted workflow contract -> later renderer / adapter / helper implementation proposal.
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, no-write root state smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“机括的 task-session 命令怎样在 Codex / Claude 桌面 APP 里成为用户能理解、能批准、能追踪的一组操作卡片”。

`JIKUO-TASKSESSION-02`, `JIKUO-TASKSESSION-03`, and `JIKUO-TASKSESSION-04` now define guarded local actions:

- create one task-session file
- refresh the project-state latest task-session index
- append evidence
- append verification
- complete a task session
- write a handoff summary

Those commands are useful, but the current primary user surface is not a terminal-first workflow.

The product problem is:

- the user works mainly in Codex / Claude desktop APP chat
- the user should not need to manually remember every helper flag
- the user should still see the exact write target, effect, and non-effect
- the agent should not silently turn a chat instruction into a durable write
- future frontend and CLI projections should not drift from the desktop workflow

This work order defines the desktop-agent workflow card layer that sits above task-session commands.

Product effect:

- task-session infrastructure becomes usable as a chat-native governance workflow
- the user can approve a specific local effect without learning the full CLI surface
- agent behavior remains auditable because each proposed write has a card, command proposal, target, effect, non-effect, and exact phrase capture policy

---

## 2. Technical Boundary

> **中文注释**：这是契约层，不是适配器实现。它只定义后续 Codex / Claude 桌面 APP 应该怎样展示、组合和请求批准。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md` downstream acceptance record

Mainline explicitly not changed:

- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`
- `tools/audit/check_rule_registry.py`
- `docs/jikuo/schemas/task_session.schema.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `.jikuo/project_state.yaml`
- `.jikuo/task_sessions/`
- `.codex/AGENTS.md`
- Codex adapter behavior
- Claude adapter behavior
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine

Canonical source:

- accepted `JIKUO-AGENT-00`
- accepted `JIKUO-AGENT-01`
- accepted `JIKUO-TASKSESSION-02`
- accepted `JIKUO-TASKSESSION-03`
- accepted `JIKUO-TASKSESSION-04`
- current `tools/jikuo/task_session.py` command contracts
- accepted task-session schema
- explicit user decisions

Bridge objects:

- `JikuoDesktopTaskSessionWorkflowCardV0`
- `JikuoDesktopCommandProposalV0`
- `JikuoDesktopApprovalCaptureV0`
- `JikuoDesktopHandoffWorkflowCardV0`

Consumer projection:

- Codex Desktop chat
- Claude Desktop chat
- future auxiliary CLI markdown
- future frontend preview
- future audit view

Lifecycle:

- agent detects task-session-relevant action
- agent runs or proposes the no-write preview where applicable
- desktop workflow card is shown
- user may approve a specific write effect in natural language
- if approved, agent composes the guarded command using the exact phrase
- structured command output is summarized back into a workflow card
- future task-session state remains project-local canonical state, not chat memory

Rollback / supersession:

- if later implementation needs a new field, supersede this contract explicitly
- if a card hides write effect or non-effect, it must be revised before adapter implementation
- if the user rejects this workflow, return to task-session command contracts before building a renderer

Propagation surfaces:

- this work order
- productization task map
- Sprint index
- future card projection helper
- future desktop-agent prompt / adapter
- future CLI markdown projection
- future frontend task-session view

Observability:

- future implementation should record card id, card kind, source command output, proposed command, approval target, approval effect, non-effect, exact user phrase when approved, command result schema, and refusal reasons.

---

## 3. Scope

This work order defines:

- task-session workflow card principles
- shared workflow card envelope
- command proposal shape
- approval capture shape
- task start workflow card
- task-session write approval card
- project-state index refresh card
- evidence append card
- verification append card
- completion acceptance card
- handoff card
- refusal / error card
- command-composition rules for desktop agents
- desktop continuity rules
- testing-governance declaration

---

## 4. Out Of Scope

This work order does not:

- implement a card renderer
- implement Codex / Claude adapter behavior
- modify `.codex/AGENTS.md`
- modify task-session helper code
- add new task-session commands
- create root `.jikuo/task_sessions/`
- write or refresh root `.jikuo/project_state.yaml`
- implement automatic task-session creation for every task
- implement raw chat transcript capture
- implement frontend screens
- implement hooks, CI, task-stop gates, or blocking enforcement
- judge product-output quality
- change runtime narrative-engine behavior

---

## 5. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`
- `tools/audit/check_rule_registry.py`
- `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`
- `SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md`
- `SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md`
- `SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md`
- `SPRINT_050_20260409.md`

---

## 6. Pre-Audit

> **中文注释**：事前审计结论：可以定义桌面工作流卡片和命令组合规则；不能直接让 Agent 自动写入，也不能把 CLI 当成主要用户体验。

Task target:

- define desktop-agent task-session workflow cards and command composition over the accepted task-session helper commands

Compliance status:

- aligned with desktop-agent-first posture because Codex / Claude desktop APP chat remains the primary user surface
- aligned with task-session lifecycle contracts because cards only project existing start, index, update, complete, and handoff actions
- aligned with guarded write policy because every durable effect requires explicit target/effect/non-effect display
- aligned with current report-only posture because no gate or blocking behavior is introduced
- aligned with product-output boundary because cards govern process state, not product-output quality

Required adjustments:

- do not require the user to type raw CLI commands for ordinary use
- use dry-run / preview before write-capable flows where possible
- record examples of user phrases as `"<exact user phrase as spoken>"`
- distinguish approval target, write effect, and non-effect
- keep command proposal separate from command execution result
- keep `.jikuo/project_state.yaml` index refresh separate from task-session creation

---

## 7. Workflow Principles

1. Desktop APP chat is the primary operating surface.
2. CLI commands are an agent-invoked bridge or advanced-user fallback, not the primary UX.
3. Every durable write must be preceded by a workflow card that states target, effect, and non-effect.
4. A workflow card may propose a command, but the command is not approved until the user gives an explicit approval phrase.
5. A single user approval should map to one card and one durable effect.
6. A dry-run or no-write preview should be used before write-capable task-session flows when available.
7. Command output should be summarized as structured result, not treated as free-form proof.
8. Chat memory is not canonical storage.
9. Product-output quality judgement remains out of scope.
10. Future frontend and CLI projections should consume the same card and command proposal vocabulary.

---

## 8. Shared Workflow Card Envelope

Conceptual shape:

```yaml
card:
  schema: "jikuo.desktop_task_session_workflow_card.v0"
  card_id: ""
  card_kind: "task_session_start_preview"
  status: "review"
  title: ""
  user_facing_summary: ""
  source_refs: []
  task_session_refs: []
  command_proposal: null
  approval_request: null
  write_effect:
    target: ""
    effect: ""
    non_effects: []
  shown_inputs: []
  shown_outputs: []
  refusal_reasons: []
  next_actions: []
```

Required envelope fields:

- `schema`
- `card_id`
- `card_kind`
- `status`
- `title`
- `user_facing_summary`
- `source_refs`
- `write_effect`
- `next_actions`

Allowed `status` values:

- `ok`
- `review`
- `missing`
- `refused`
- `error`
- `not_applicable`

Allowed `card_kind` values:

- `task_session_start_preview`
- `task_session_write_approval`
- `task_session_write_result`
- `task_session_index_refresh`
- `task_session_evidence_append`
- `task_session_verification_append`
- `task_session_completion_acceptance`
- `task_session_handoff`
- `task_session_refusal`

Display rule:

- show the user-facing summary first
- show target/effect/non-effect before any approval request
- show command preview only after the semantic effect is clear
- show refusal reasons instead of command preview when preflight refuses

---

## 9. Command Proposal Object

Conceptual shape:

```yaml
command_proposal:
  schema: "jikuo.desktop_command_proposal.v0"
  command_kind: "task_session_start_write"
  command_preview: ""
  expected_result_schema: "jikuo.task_session_write_result.v0"
  writes:
    - path: ".jikuo/task_sessions/<session_id>.yaml"
  does_not_write:
    - ".jikuo/project_state.yaml"
  requires_user_approval: true
  required_flags:
    - "--confirm-create-task-session"
    - "--approval-phrase"
  approval_phrase_placeholder: "\"<exact user phrase as spoken>\""
```

Required fields:

- `schema`
- `command_kind`
- `command_preview`
- `expected_result_schema`
- `writes`
- `does_not_write`
- `requires_user_approval`
- `required_flags`
- `approval_phrase_placeholder`

Command proposal rules:

- command preview must not hide write paths
- command preview must not merge multiple durable effects into one approval
- command preview must preserve the exact approval phrase when execution is requested
- command preview must identify when a command is dry-run only
- command preview must identify when a command will not write root project state

---

## 10. Approval Capture Object

Conceptual shape:

```yaml
approval_capture:
  schema: "jikuo.desktop_approval_capture.v0"
  card_id: ""
  approval_target: ""
  approval_effect: ""
  approval_non_effects: []
  exact_user_phrase: "<exact user phrase as spoken>"
  approval_surface: "codex_desktop_or_claude_desktop"
  approved_command_kind: ""
```

Required fields:

- `schema`
- `card_id`
- `approval_target`
- `approval_effect`
- `approval_non_effects`
- `exact_user_phrase`
- `approval_surface`
- `approved_command_kind`

Approval capture rules:

- ordinary use should not require fixed command phrases
- examples must use the placeholder `"<exact user phrase as spoken>"`
- ambiguous approval must trigger clarification
- multiple pending approval cards must not share one vague approval
- approval for task-session creation does not approve index refresh
- approval for evidence append does not approve completion
- approval for completion does not approve handoff unless the card explicitly states the combined effect and the user confirms that combined effect

---

## 11. Workflow Card Families

### 11.1 Task Start Preview Card

Purpose:

- show the user what task session would be created before any write occurs

Must show:

- task title / intent
- owner agent
- project root
- proposed session id
- proposed session file
- root project-state status
- whether this is dry-run only
- next possible approval action

Must not:

- imply that a task-session file already exists
- update `.jikuo/project_state.yaml`
- capture raw chat transcript

### 11.2 Task-Session Write Approval Card

Purpose:

- request user approval before creating one compact task-session file

Must show:

- target: task-session file creation
- effect: create one compact task-session sidecar record
- non-effect: do not capture raw chat transcript
- non-effect: do not update project-state latest-session index
- command preview
- exact phrase capture policy

### 11.3 Task-Session Write Result Card

Purpose:

- report whether guarded task-session file creation succeeded or refused

Must show:

- session id
- file path if created
- result schema
- refusal reasons if refused
- whether project-state index was unchanged
- next optional action: index refresh preview

### 11.4 Project-State Index Refresh Card

Purpose:

- preview or request approval to refresh `.jikuo/project_state.yaml` `latest_task_session_refs`

Must show:

- current indexed refs
- discovered task-session refs
- target: project-state latest-session index
- effect: update only `latest_task_session_refs`
- non-effect: do not create task-session files
- backup / preserve-unknown-fields policy when relevant

### 11.5 Evidence Append Card

Purpose:

- append compact process evidence to an existing explicit task session

Must show:

- target session id
- evidence kind
- evidence summary
- source refs
- target: task-session evidence snapshots
- effect: append compact evidence
- non-effect: do not capture raw chat transcript
- refusal reasons for terminal sessions or ambiguous session ids

### 11.6 Verification Append Card

Purpose:

- append verification command/result summary to an existing explicit task session

Must show:

- target session id
- command or check summary
- result status
- residual risks or not-run notes if available
- target: task-session verification list
- effect: append compact verification evidence
- non-effect: do not change completion acceptance

### 11.7 Completion Acceptance Card

Purpose:

- record user acceptance, revision request, deferment, or abandonment for an explicit task session

Must show:

- target session id
- proposed completion status
- user decision type
- exact phrase capture policy
- target: task-session completion and user decision fields
- effect: set completion state and append user decision
- non-effect: do not judge product-output quality
- non-effect: do not automatically create handoff unless separately approved

### 11.8 Handoff Card

Purpose:

- prepare the next agent or later session to continue from a compact process summary

Must show:

- target session id
- handoff summary
- required reads
- pending decisions
- missing evidence
- next-agent assumptions
- target: task-session handoff field
- effect: write compact handoff summary
- non-effect: do not reopen accepted completion

### 11.9 Refusal / Error Card

Purpose:

- make unsafe, stale, ambiguous, or unsupported workflow states visible

Must show:

- attempted action
- refusal reasons
- source command result or preflight result
- what was not written
- suggested safe next action

Must not:

- offer a write command when preflight refused
- hide ambiguous session selection

---

## 12. Command Composition Rules

Task start:

```powershell
python -B tools/jikuo/task_session.py start --dry-run --task-title "<task title>" --owner-agent codex --format json
```

Guarded task-session creation:

```powershell
python -B tools/jikuo/task_session.py start --write --task-title "<task title>" --owner-agent codex --confirm-create-task-session --approval-phrase "<exact user phrase as spoken>" --format json
```

Index preview:

```powershell
python -B tools/jikuo/task_session.py index --dry-run --format json
```

Guarded index refresh:

```powershell
python -B tools/jikuo/task_session.py index --refresh --confirm-update-project-state-index --approval-phrase "<exact user phrase as spoken>" --format json
```

Lifecycle dry-run:

```powershell
python -B tools/jikuo/task_session.py update --dry-run --session-id "<session id>" --format json
```

Guarded evidence append:

```powershell
python -B tools/jikuo/task_session.py update --append-evidence --session-id "<session id>" --evidence-kind "<evidence kind>" --evidence-ref "<evidence ref>" --summary "<evidence summary>" --confirm-update-task-session --approval-phrase "<exact user phrase as spoken>" --format json
```

Guarded verification append:

```powershell
python -B tools/jikuo/task_session.py update --append-verification --session-id "<session id>" --command-name "<command summary>" --summary "<result summary>" --confirm-update-task-session --approval-phrase "<exact user phrase as spoken>" --format json
```

Guarded completion:

```powershell
python -B tools/jikuo/task_session.py complete --session-id "<session id>" --status accepted --summary "<decision summary>" --confirm-complete-task-session --approval-phrase "<exact user phrase as spoken>" --format json
```

Guarded handoff:

```powershell
python -B tools/jikuo/task_session.py handoff --session-id "<session id>" --summary "<handoff summary>" --confirm-update-task-session --approval-phrase "<exact user phrase as spoken>" --format json
```

Composition constraints:

- `start --write` must not imply `index --refresh`
- `index --refresh` must not imply task-session creation
- `update --append-evidence` must not imply completion
- `complete` must not imply handoff
- `handoff` must not alter accepted completion
- every guarded command must include the explicit session id where the helper supports it
- every command proposal should be preceded by a card that explains the effect in product terms

---

## 13. Desktop Continuity Rules

> **中文注释**：这部分是为了让 Codex / Claude 桌面 APP 的体验连续，但不把聊天记录误当成 canonical state。

When the user continues in the same desktop APP:

- the agent may summarize the current workflow card state
- the agent should prefer project-local task-session state over chat memory if a session exists
- the agent should ask for clarification if multiple write cards are pending
- the agent should not auto-run a write command from a stale card

When switching from Codex to Claude or Claude to Codex:

- handoff card should list required reads and pending decisions
- incoming agent should restate which task-session id it is continuing
- incoming agent should not assume a task-session write happened unless the project-local file exists

When no task-session exists:

- the agent may show a start preview card
- the agent must not claim the task is already governed by a durable task session

---

## 14. Testing Governance Declaration

> **中文注释**：本工单不改代码，所以测试重点是契约审计、链路完整性、无写入确认，而不是产品输出内容评价。

- `unit`: N/A because no renderer, adapter, parser, serializer, or helper code is implemented.
- `integration`: N/A because no desktop APP adapter, frontend, CLI bridge, checker migration, or storage change is implemented.
- `workflow/orchestration`: required by contract review; card families must cover start preview, write approval, write result, index refresh, evidence append, verification append, completion, handoff, and refusal.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against this new work order and updated planning docs.
- `no-write smoke`: required; verify root `.jikuo/task_sessions/` remains absent and root `latest_task_session_refs` remains unchanged.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for approval target clarity, effect/non-effect clarity, desktop continuity, and command-composition safety.

---

## 15. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| A2-DC-01 | Declare deterministic work-order header fields | Header exists |
| A2-DC-02 | Define product question and product effect | Section 1 exists |
| A2-DC-03 | Define technical boundary and non-goals | Sections 2 and 4 exist |
| A2-DC-04 | Define audit references and pre-audit | Sections 5 and 6 exist |
| A2-DC-05 | Define workflow card envelope | Section 8 exists |
| A2-DC-06 | Define command proposal object | Section 9 exists |
| A2-DC-07 | Define approval capture object | Section 10 exists |
| A2-DC-08 | Define task-session workflow card families | Section 11 exists |
| A2-DC-09 | Define command-composition rules | Section 12 exists |
| A2-DC-10 | Define desktop continuity rules | Section 13 exists |
| A2-DC-11 | Declare testing-governance layers | Section 14 exists |
| A2-DC-12 | Preserve no-implementation boundary | Sections 2, 4, and 16 exist |
| A2-DC-13 | Run report-only checker smoke | Verification log records checker result |
| A2-DC-14 | Run no-write root state smoke | Verification log records no-write result |

---

## 16. Acceptance Gate

User review should confirm:

- task-session workflow cards are useful for Codex / Claude desktop APP users
- cards distinguish command proposal from command execution result
- every durable write has explicit target, effect, and non-effect
- approval phrase examples use `"<exact user phrase as spoken>"`
- CLI remains auxiliary and agent-invoked for ordinary use
- no renderer, adapter, automatic write, frontend, gate, checker migration, registry migration, or runtime implementation is silently approved

Do not continue to renderer, Codex/Claude adapter behavior, automated task-session creation, frontend preview, gate implementation, or Sprint 050 runtime hardening from this slice until the user accepts this workflow-card contract.

---

## 17. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md
```

```powershell
Test-Path D:\personal_project\NarrativeSystem\.jikuo\task_sessions
Select-String -Path D:\personal_project\NarrativeSystem\.jikuo\project_state.yaml -Pattern 'latest_task_session_refs' -Context 0,1
```

Expected result:

- report-only checker exits `0`
- deterministic work-order checks pass or report review-only items
- root `.jikuo/task_sessions/` remains absent
- root `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Actual result:

- report-only checker exited `0`
- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- `user_scenario`, `runtime_chain`, `canonical_source`, `bridge_object`, `consumer_projection`, `lifecycle`, required work-order fields, required sections, and Sprint index document evidence reported `OK`
- runtime audit bundle fields and manual declarations remained `REVIEW`, as expected for this report-only governance slice
- root `.jikuo/task_sessions/` remains absent
- root `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

---

## 18. Acceptance Record

> **中文注释**：用户继续推进本线，因此本契约被接受为 `JIKUO-AGENT-03` 的上游输入。接受契约不等于批准自动桌面适配器或前端。

Decision:

- user accepted this workflow-card contract for downstream minimal card projection helper implementation by asking to continue

Accepted downstream input:

- desktop workflow card envelope
- command proposal object
- approval capture object
- start / index / evidence / verification / completion / handoff / refusal card families
- command-composition principle that every durable write must show target, effect, and non-effect before approval
- no-write smoke expectation for projection-only helper work

Still not approved:

- Codex / Claude desktop adapter behavior
- automatic task-session creation
- automatic task-session lifecycle capture
- frontend task-session preview
- gate or blocking enforcement
- runtime narrative-engine changes
