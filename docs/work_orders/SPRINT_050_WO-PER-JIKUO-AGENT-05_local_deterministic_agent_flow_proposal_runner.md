# SPRINT_050_WO-PER-JIKUO-AGENT-05: Local Deterministic Agent Flow Proposal Runner

> **Date**: 2026-05-05  
> **Status**: Accepted as no-write proposal runner for downstream instruction-pack planning  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / local deterministic runner / no-write implementation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: accepted `JIKUO-AGENT-04` desktop-agent invocation contract; `JIKUO-FLOW-02` Loop Composition Map; implemented project-state, task-session, and card projection atoms  
> **Current slice**: minimal local deterministic `agent_flow.py propose` path only; no guarded `apply`, Skill, MCP server, plugin, frontend, automatic write, gate, checker migration, registry migration, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user asks the agent to use JIKUO; the agent needs one deterministic local no-write runner that can compose existing atoms and return a chat-ready proposal without asking the user to run helper commands manually.  
> **Runtime chain**: desktop chat intent -> accepted invocation scenario -> `agent_flow.py propose` -> no-write atom composition -> card / summary projection -> Markdown or JSON output -> user reviews in chat -> later explicit approval before any guarded write.  
> **Canonical source**: accepted `JIKUO-AGENT-04`, `JIKUO-FLOW-02` Loop Composition Map, Atomic Capability Registry in `jikuo_productization_task_map.md`, and existing helper contracts.  
> **Bridge object**: `jikuo.agent_flow_proposal.v0`; `jikuo.agent_trigger_decision.v0`; loop step id / atom id trace.  
> **Consumer projection**: Codex / Claude desktop APP chat, future Codex Skill / Agent instruction, future MCP tool, future Codex Plugin, future frontend run-control/audit surfaces.  
> **Lifecycle**: implemented no-write proposal runner -> user reviews concrete output -> accepted runner may become input for Skill / MCP planning; guarded `apply` remains a later contract.  
> **Testing layers**: unit, workflow/orchestration, smoke, no-write smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：这一步把机括从“Agent 理论上应该调用若干 helper”推进到“Agent 有一个确定的本地入口可以调用”。用户仍然在桌面 APP 里看结果，不需要切到 CLI。

Before this slice:

- task-session and card atoms existed
- Desktop App Primary Operating Loop existed
- desktop invocation contract existed
- but there was no single local runner for a desktop agent to call

This slice adds:

- `tools/jikuo/agent_flow.py`
- `tools/jikuo/agent_flow_tests.py`
- a no-write `propose` command
- Markdown output for desktop chat
- JSON output for future MCP / frontend
- loop step id and atom id trace

Visible product effect:

- the agent can call one local deterministic command and paste the result into chat
- the user sees what JIKUO inspected and what card was produced
- no durable write happens in proposal mode
- `apply`, Skill, MCP, plugin, and frontend remain later work

---

## 2. Technical Boundary

Mainline changed:

- `tools/jikuo/agent_flow.py`
- `tools/jikuo/agent_flow_tests.py`
- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md`

Mainline explicitly not changed:

- guarded `agent_flow.py apply`
- existing project-state write behavior
- existing task-session write behavior
- existing card projection behavior
- `tools/audit/check_rule_registry.py`
- `.codex/AGENTS.md`
- `.jikuo/project_state.yaml`
- `.jikuo/task_sessions/`
- Skill installation
- MCP server implementation
- Codex Plugin implementation
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine code

Canonical source:

- accepted `JIKUO-AGENT-04`
- accepted `JIKUO-FLOW-02` Loop Composition Map
- Atomic Capability Registry
- existing helper function contracts

Bridge object:

- `jikuo.agent_flow_proposal.v0`
- `jikuo.agent_trigger_decision.v0`
- loop step id / atom id trace

Consumer projection:

- Markdown for desktop APP chat
- JSON for future MCP / frontend

Lifecycle:

- agent calls `propose`
- runner composes no-write atoms
- runner returns cards / trace
- user reviews in chat
- guarded write remains separate and unavailable in this slice

Rollback / supersession:

- if output shape is rejected, revise `agent_flow.py` before Skill / MCP work
- if a later `apply` path needs new trace fields, supersede this work order explicitly
- do not silently turn proposal mode into write mode

Propagation surfaces:

- local runner
- runner tests
- task map registry
- execution mount
- Sprint index

Observability:

- proposal output exposes trigger decision, loop id, loop step ids, atom ids, atom mode, cards, approval boundary, and write-effect summary

---

## 3. Scope

This work order implements:

- `agent_flow.py propose`
- event normalization for status, task start, task continue, index, evidence, verification, completion, handoff, and audit placeholder
- no-write project-state status composition
- no-write task-session start preview composition
- no-write task-session index preview composition
- no-write task-session continuation / lifecycle preview composition
- generic refusal cards for missing task title, missing session id, and unsupported events
- Markdown proposal rendering
- JSON proposal rendering
- loop step id / atom id trace
- tests for task start, project status, and missing session id refusal

---

## 4. Out Of Scope

This work order does not:

- implement guarded `apply`
- execute project-state write
- execute task-session write
- execute task-session index refresh
- execute evidence / verification / completion / handoff writes
- run checker composition with changed-path input
- install or modify Codex Skill
- implement MCP server
- implement Codex Plugin
- implement frontend screens
- update `.codex/AGENTS.md`
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
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md`
- `tools/jikuo/project_state.py`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_cards.py`
- `tools/jikuo/agent_flow.py`
- `tools/jikuo/agent_flow_tests.py`
- `tools/audit/check_rule_registry.py`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 6. Pre-Audit

Task target:

- implement the smallest local deterministic no-write runner that composes existing atoms for the Desktop App Primary Operating Loop

Compliance status:

- aligned with `JIKUO-AGENT-04` because it provides a deterministic local entry point after the invocation contract
- aligned with `JIKUO-FLOW-02` because it reports loop step ids and atom ids
- aligned with no-write safety because `propose` never calls guarded write atoms
- aligned with desktop-agent-first posture because Markdown output can be pasted into the same desktop chat
- aligned with product-output boundary because it governs process state, not product quality

Required adjustments:

- keep proposal mode read-only
- expose trace fields for future audit
- reuse existing helper functions instead of duplicating policy
- keep guarded `apply` out of scope

---

## 7. Implemented Commands

Main command:

```powershell
python -B tools/jikuo/agent_flow.py propose --event task_start --task-title "<task title>" --project-root "<project root>" --format markdown
```

Supported output:

- `--format markdown`
- `--format json`

Supported proposal events:

- `status`
- `task_start`
- `task_continue`
- `index`
- `evidence`
- `verification`
- `completion`
- `handoff`
- `audit`

Current audit behavior:

- `audit` returns a review card explaining that changed-path checker composition is not yet included in the minimal proposal path

---

## 8. Proposal Object

Top-level schema:

```yaml
schema: "jikuo.agent_flow_proposal.v0"
report_only: true
runner_mode: "propose"
status: "ok|review|refused"
loop_id: "Desktop App Primary Operating Loop"
trigger_decision: {}
atom_trace: []
cards: []
approval_boundary: {}
write_effect: {}
next_actions: []
```

Safety invariants:

- `report_only` is always `true`
- `runner_mode` is `propose`
- `write_effect.writes_performed` is `false`
- `approval_boundary.guarded_apply_available` is `false`
- no durable-write atom is called

---

## 9. Testing Governance Declaration

- `unit`: required; runner tests assert proposal schema, event mapping, no-write behavior, and refusal behavior.
- `integration`: limited; runner imports existing project-state, task-session, and card projection helper functions.
- `workflow/orchestration`: required; tests cover status, task start, and refusal loop paths.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run runner tests, card tests, task-session tests, and report-only checker.
- `no-write smoke`: required; verify root `.jikuo/task_sessions/` remains absent and root `latest_task_session_refs` remains unchanged.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for whether Markdown proposal feels suitable inside Codex / Claude desktop APP chat.

---

## 10. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| A5-DC-01 | Add local deterministic no-write runner | `tools/jikuo/agent_flow.py` exists |
| A5-DC-02 | Support `propose` command | CLI test covers `propose` |
| A5-DC-03 | Compose task-start atoms | Test covers `task_start` JSON |
| A5-DC-04 | Compose project-status atoms | Test covers `status` Markdown |
| A5-DC-05 | Refuse missing session id without write | Test covers `task_continue` refusal |
| A5-DC-06 | Emit loop step ids and atom ids | Test asserts atom ids |
| A5-DC-07 | Preserve no-write behavior | No-write smoke records root state |
| A5-DC-08 | Update task map / execution mount / Sprint index | Verification log records checker result |
| A5-DC-09 | Run report-only checker smoke | Verification log records checker result |

---

## 11. Acceptance Gate

User review should confirm:

- `agent_flow.py propose` output is understandable in Codex / Claude desktop APP chat
- the runner feels like one clear internal invocation point
- loop step id / atom id trace is useful rather than noisy
- no-write proposal behavior is clear
- refusal behavior is acceptable
- guarded `apply` should remain later or be planned separately

After acceptance, downstream work may add a project-local instruction pack, but guarded `apply`, installable Skill, MCP, plugin, frontend, and gate implementation remain separate decisions.

---

## 12. Verification Log

Commands to run:

```powershell
python -B tools/jikuo/agent_flow_tests.py
```

```powershell
python -B tools/jikuo/task_session_cards_tests.py
```

```powershell
python -B tools/jikuo/task_session_tests.py
```

```powershell
python -B tools/audit/check_rule_registry.py --added tools/jikuo/agent_flow.py --added tools/jikuo/agent_flow_tests.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md
```

```powershell
Test-Path D:\personal_project\NarrativeSystem\.jikuo\task_sessions
Select-String -Path D:\personal_project\NarrativeSystem\.jikuo\project_state.yaml -Pattern 'latest_task_session_refs' -Context 0,1
```

Actual result:

- `python -B tools/jikuo/agent_flow_tests.py` passed: 3 tests
- `python -B tools/jikuo/task_session_cards_tests.py` passed: 4 tests
- `python -B tools/jikuo/task_session_tests.py` passed: 24 tests
- `python -B tools/jikuo/project_state_tests.py` passed: 11 tests
- real root smoke command produced a Markdown `JIKUO Agent Flow Proposal`
- real root smoke output included `Writes performed: false`
- real root smoke output included loop step ids `DPL-03`, `DPL-04`, and `DPL-06`
- real root smoke output included atom ids `CAP-PROJECT-STATE-STATUS-01`, `CAP-TASK-START-DRYRUN-01`, and `CAP-CARD-TASKSESSION-01`
- report-only checker exited `0`
- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required work-order fields and required sections reported `OK`
- Sprint index document requirement reported `OK`
- runtime audit bundle fields and manual declarations remained `REVIEW`, as expected for this documentation / runner slice
- root `.jikuo/task_sessions/` remained absent
- root `.jikuo/project_state.yaml` still had `latest_task_session_refs: []`

---

## 13. Current Acceptance Record

> **中文注释**：这是已实现待验收切片。验收后才决定做 guarded `apply`，还是先做轻量 Skill / Agent 指引。

Decision:

- accepted for downstream lightweight desktop-agent instruction-pack planning after desktop chat validation

Still not approved in this slice:

- guarded `agent_flow.py apply`
- installable Codex Skill or global Agent instruction promotion
- MCP tool wrapper
- Codex Plugin
- frontend implementation
- automatic durable write
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
