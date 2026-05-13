# SPRINT_050_WO-PER-JIKUO-AGENT-03: Minimal Task-Session Card Projection Helper

> **Date**: 2026-05-05  
> **Status**: Implemented, ready for user review  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / desktop-agent card projection helper / report-only implementation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md`; `SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md`; `tools/jikuo/task_session.py`  
> **Current slice**: minimal no-write task-session card projection helper; no desktop adapter, automatic write, frontend, gate, checker migration, registry migration, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user wants to inspect a concrete JIKUO task-session workflow card before approving any durable task-session write.  
> **Runtime chain**: task-session helper plan/result -> no-write card projection helper -> Markdown or JSON desktop card -> user governance review -> later explicit approval before guarded command execution.  
> **Canonical source**: accepted `JIKUO-AGENT-02` card contract and existing `tools/jikuo/task_session.py` structured outputs.  
> **Bridge object**: `jikuo.desktop_task_session_workflow_card.v0`; `jikuo.desktop_command_proposal.v0`; `jikuo.desktop_approval_capture.v0`.  
> **Consumer projection**: Codex / Claude desktop APP chat, auxiliary CLI markdown output, future frontend preview.  
> **Lifecycle**: implemented helper -> user reviews concrete card output -> accepted helper may become input for later adapter / renderer planning.  
> **Testing layers**: unit, workflow/orchestration, smoke, no-write smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：这一步把“卡片契约”变成用户能实际看到的卡片样机。你参与验证时，可以直接看卡片是否说清楚了批准边界。

Before this slice, JIKUO had:

- guarded task-session commands
- a desktop workflow-card contract

But the user still could not inspect the actual card that a desktop agent would show.

This slice adds a minimal no-write projection helper:

- it reads or builds existing task-session plans
- it projects them into Markdown or JSON cards
- it shows target, effect, non-effect, command proposal, approval phrase placeholder, refusal reasons, and next actions
- it does not write `.jikuo/task_sessions/`
- it does not update `.jikuo/project_state.yaml`

Concrete user validation is now possible:

- the user can review whether the card is understandable
- the user can review whether the write target is explicit enough
- the user can review whether the non-effects prevent accidental over-approval
- the user can review whether the card feels suitable for Codex / Claude desktop APP chat

---

## 2. Technical Boundary

> **中文注释**：这是最小 projection helper，不是桌面 adapter。它能生成卡片文本，但不会自动接入 Codex / Claude，也不会替用户批准写入。

Mainline changed:

- `tools/jikuo/task_session_cards.py`
- `tools/jikuo/task_session_cards_tests.py`
- this work order document
- `SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md` acceptance record and command example hygiene
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

Mainline explicitly not changed:

- `tools/jikuo/task_session.py` behavior
- `.jikuo/project_state.yaml`
- `.jikuo/task_sessions/`
- `.codex/AGENTS.md`
- Codex adapter behavior
- Claude adapter behavior
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine

Canonical source:

- accepted `JIKUO-AGENT-02`
- existing `task_session.py` plan/result schemas

Bridge object:

- `jikuo.desktop_task_session_workflow_card.v0`
- `jikuo.desktop_command_proposal.v0`
- `jikuo.desktop_approval_capture.v0`

Consumer projection:

- Markdown card for desktop APP chat
- JSON card for future adapter/frontend consumption

Lifecycle:

- helper generates no-write projection
- user reviews concrete card output
- later work may implement a renderer, adapter, or frontend preview only after explicit acceptance

Rollback / supersession:

- remove or revise `tools/jikuo/task_session_cards.py` if the card shape is rejected
- do not change task-session write commands from this slice
- future helper changes must preserve no-write default unless a separate write-capable adapter work order is accepted

Propagation surfaces:

- helper code
- helper tests
- work-order docs
- productization task map
- Sprint index

Observability:

- generated card exposes card id, card kind, status, source refs, task-session refs, write effect, command proposal, approval capture, refusal reasons, and next actions

---

## 3. Scope

This work order implements:

- `start-preview` card projection
- `index-preview` card projection
- `update-preview` card projection for inspect/evidence/verification preview paths
- `render-json` projection from an existing task-session JSON plan
- Markdown output for desktop APP review
- JSON output for future structured consumers
- tests for start preview, refusal card, index preview Markdown, and render-json

---

## 4. Out Of Scope

This work order does not:

- run guarded write commands
- create task-session files
- refresh project-state index
- capture raw chat transcript
- judge product-output quality
- implement Codex / Claude adapter behavior
- implement frontend screens
- implement gate behavior
- migrate checker or registry behavior
- alter narrative runtime code

---

## 5. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md`
- `SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`
- `tools/jikuo/task_session_cards.py`
- `tools/jikuo/task_session_cards_tests.py`
- `tools/audit/check_rule_registry.py`
- `SPRINT_050_20260409.md`

---

## 6. Pre-Audit

Task target:

- implement a minimal no-write task-session card projection helper for desktop-agent review

Compliance status:

- aligned with desktop-agent-first posture because the helper outputs Markdown suitable for Codex / Claude chat
- aligned with guarded write policy because cards show target, effect, non-effect, and approval phrase placeholder
- aligned with no-write safety because the helper only builds projections and never writes project state
- aligned with product boundary because cards govern process evidence, not product-output quality

Required adjustments:

- fix `AGENT-02` command examples so they match current `task_session.py` flags
- keep helper output deterministic enough for tests
- keep JSON output available for future adapter/frontend work
- preserve root no-write state during verification

---

## 7. Implemented Helper

Command:

```powershell
python -B tools/jikuo/task_session_cards.py start-preview --task-title "<task title>" --project-root "<project root>" --format markdown
```

Purpose:

- build a task-session start plan using existing helper logic
- project it into a desktop card
- show command proposal for guarded `start --write`
- perform no writes

Command:

```powershell
python -B tools/jikuo/task_session_cards.py index-preview --project-root "<project root>" --format markdown
```

Purpose:

- build a project-state task-session index preview
- show whether refresh is needed
- perform no writes

Command:

```powershell
python -B tools/jikuo/task_session_cards.py update-preview --session-id "<session id>" --project-root "<project root>" --summary "<summary>" --format markdown
```

Purpose:

- build an update preview card for an explicit task-session id
- show refusal when the session cannot be safely selected
- perform no writes

Command:

```powershell
python -B tools/jikuo/task_session_cards.py render-json --input "<task-session-output.json>" --format markdown
```

Purpose:

- render an existing task-session JSON plan into a desktop card
- support future agent chains that run `task_session.py --format json` first and render after

---

## 8. Concrete User Validation

> **中文注释**：这里是你下一步可以直接参与的验证方式。你不需要读代码，只需要看卡片是否适合作为桌面 APP 里的确认界面。

Recommended user review command:

```powershell
python -B tools/jikuo/task_session_cards.py start-preview --task-title "JIKUO desktop card validation" --project-root D:\personal_project\NarrativeSystem --format markdown
```

User review checklist:

- Does the card clearly say this is only a preview?
- Does the card clearly identify the target task-session file?
- Does the card clearly say it would not update `.jikuo/project_state.yaml`?
- Does the card clearly say it would not capture raw chat transcript?
- Does the command proposal feel understandable enough for Codex / Claude desktop APP chat?
- Is `"<exact user phrase as spoken>"` clear as an approval placeholder rather than a required literal user sentence?
- Would you feel safe approving or rejecting the proposed write based on this card?

Expected no-write result:

- `.jikuo/task_sessions/` remains absent unless a separate guarded write is explicitly approved
- `.jikuo/project_state.yaml` `latest_task_session_refs` remains unchanged

---

## 9. Testing Governance Declaration

- `unit`: required; card projection functions are covered through CLI-level unit-style tests.
- `integration`: limited; helper imports existing `task_session.py` plan builders and renders their outputs.
- `workflow/orchestration`: required; tests cover start preview, refusal card, index preview, and render-json projection.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run helper tests and report-only checker.
- `no-write smoke`: required; verify root `.jikuo/task_sessions/` remains absent and root `latest_task_session_refs` remains unchanged.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required; user should review whether card target/effect/non-effect and approval wording are understandable.

---

## 10. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| A3-DC-01 | Add no-write card projection helper | `tools/jikuo/task_session_cards.py` exists |
| A3-DC-02 | Support Markdown and JSON card output | CLI tests assert both paths |
| A3-DC-03 | Render start-preview card | Test covers start preview |
| A3-DC-04 | Render refusal card | Test covers missing project refusal |
| A3-DC-05 | Render index-preview card | Test covers index Markdown |
| A3-DC-06 | Render existing JSON plan | Test covers `render-json` |
| A3-DC-07 | Preserve no-write behavior | No-write smoke records root state |
| A3-DC-08 | Update AGENT-02 command examples to match implementation | Doc patch exists |
| A3-DC-09 | Declare concrete user validation checklist | Section 8 exists |
| A3-DC-10 | Run report-only checker | Verification log records checker result |

---

## 11. Acceptance Gate

User review should confirm:

- concrete card output is understandable in a desktop APP chat context
- approval target, effect, and non-effect are clear
- refusal card behavior is acceptable
- command proposal wording is not too CLI-heavy for ordinary users
- no-write safety is preserved

Do not continue to automatic adapter behavior, task-session auto-start, frontend preview, or gate behavior until the user accepts this helper output.

---

## 12. Verification Log

Commands to run:

```powershell
python -B tools/jikuo/task_session_cards_tests.py
```

```powershell
python -B tools/jikuo/task_session_cards.py start-preview --task-title "JIKUO desktop card validation" --project-root D:\personal_project\NarrativeSystem --format markdown
```

```powershell
python -B tools/audit/check_rule_registry.py --added tools/jikuo/task_session_cards.py --added tools/jikuo/task_session_cards_tests.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md
```

```powershell
Test-Path D:\personal_project\NarrativeSystem\.jikuo\task_sessions
Select-String -Path D:\personal_project\NarrativeSystem\.jikuo\project_state.yaml -Pattern 'latest_task_session_refs' -Context 0,1
```

Current implementation result:

- `python -B tools/jikuo/task_session_cards_tests.py` passed after fixing refusal-card projection
- `python -B tools/jikuo/task_session_tests.py` passed, preserving existing task-session helper behavior
- report-only checker exited `0`
- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- `user_scenario`, `runtime_chain`, `canonical_source`, `bridge_object`, `consumer_projection`, `lifecycle`, required work-order fields, required sections, and Sprint index document evidence reported `OK`
- runtime audit bundle fields and manual declarations remained `REVIEW`, as expected for this report-only governance slice
- sample start-preview Markdown was generated without writing root task-session files
- root `.jikuo/task_sessions/` remained absent
- root `.jikuo/project_state.yaml` still had `latest_task_session_refs: []`

---

## 13. Product Correction Note

> **中文注释**：本实现被保留为“内部原子能力”，但不能被误认为用户主流程。用户不应该为了看机括卡片而切换到 CLI。

Correction:

- this helper is an internal atom for agents, skills, plugins, MCP tools, or advanced debugging
- it is not the primary user operation path
- a Codex / Claude desktop APP user should not be required to run this command manually during routine work

Downstream requirement:

- `JIKUO-FLOW-02` must define the `Desktop App Primary Operating Loop` before more helper expansion, adapter behavior, frontend preview, or auto-start work continues
- future agent-facing work should invoke this helper internally and paste the resulting card into the same desktop APP chat

Still useful:

- the helper proves that task-session cards can be generated deterministically
- the helper remains a testable atom that future desktop-agent invocation can call
