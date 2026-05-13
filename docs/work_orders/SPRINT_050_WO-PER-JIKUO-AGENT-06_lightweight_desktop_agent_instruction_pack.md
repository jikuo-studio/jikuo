# SPRINT_050_WO-PER-JIKUO-AGENT-06: Lightweight Desktop Agent Instruction Pack

> **Date**: 2026-05-09  
> **Status**: Implemented, ready for user review  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / desktop-agent instruction layer / no-write adoption work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: accepted `JIKUO-AGENT-04` desktop-agent invocation contract; implemented and desktop-validated `JIKUO-AGENT-05` no-write `agent_flow.py propose` runner; `JIKUO-FLOW-02` Loop Composition Map.  
> **Current slice**: project-local lightweight desktop-agent instruction pack only; no installed Codex Skill, MCP server, plugin, frontend, automatic write, guarded `agent_flow.py apply`, gate, checker migration, registry migration, `.codex/AGENTS.md` edit, or runtime implementation.  
> **User scenario**: A Codex / Claude desktop APP user invokes JIKUO in chat; the agent needs a short, project-local instruction pack that tells it when to call `agent_flow.py propose`, how to render the result back in chat, and where the write boundary is.  
> **Runtime chain**: desktop chat intent -> explicit or suggested JIKUO trigger -> agent instruction pack -> `agent_flow.py propose` -> no-write proposal card -> same-chat user review -> later explicit separate approval for any durable write.  
> **Canonical source**: accepted `JIKUO-AGENT-04`, implemented `JIKUO-AGENT-05`, `JIKUO-FLOW-02`, Atomic Capability Registry in `jikuo_productization_task_map.md`, and `jikuo_execution_mounts.md`.  
> **Bridge object**: `jikuo.desktop_agent_instruction_pack.v0`; future Codex Skill / MCP instruction input.  
> **Consumer projection**: current Codex / Claude desktop APP agent behavior guidance, future Codex Skill, future MCP tool, future Codex Plugin, future frontend run-control/audit surfaces.  
> **Lifecycle**: project-local instruction pack -> user review -> possible promotion into installable Skill or MCP wrapper in a separate accepted work order.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, no-write smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：这一小步不是“再造一个 helper”，而是把已有 helper 接回桌面 APP 的用户操作流。它让 Agent 更不容易忘记：用户说“机括：开始”时，应该自己内部调用 `agent_flow.py propose`，然后把卡片贴回聊天。

Before this slice:

- `agent_flow.py propose` existed
- the user could validate a real proposal card inside desktop chat
- but the invocation behavior still lived mostly in long work orders and the active conversation

This slice adds:

- a compact project-local desktop-agent instruction pack
- explicit trigger-to-event mapping
- safe command shapes for `agent_flow.py propose`
- chat return contract
- write boundary and refusal rules
- future Skill / MCP projection boundary

Visible product effect:

- the ordinary user path remains Codex / Claude desktop APP chat
- the agent has a short operational guide instead of relying on memory
- no durable write happens
- installable Skill / MCP / plugin work remains later and reviewable

---

## 2. Technical Boundary

Mainline changed:

- `docs/jikuo/governance/jikuo_desktop_agent_instruction_pack.md`
- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md`

Mainline explicitly not changed:

- `tools/jikuo/agent_flow.py`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_cards.py`
- `tools/jikuo/project_state.py`
- `tools/audit/check_rule_registry.py`
- `.codex/AGENTS.md`
- Codex global skills directory
- `.jikuo/project_state.yaml`
- `.jikuo/task_sessions/`
- MCP server implementation
- Codex Plugin implementation
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine code

Canonical source:

- accepted desktop invocation contract
- implemented no-write proposal runner
- accepted desktop primary operating loop
- task-map atomic capability registry
- execution mount

Bridge object:

- `jikuo.desktop_agent_instruction_pack.v0`

Consumer projection:

- current desktop-agent behavior guidance
- future installable Skill body/reference
- future MCP instruction and tool documentation

Lifecycle:

- agent reads / mounts the instruction pack
- agent invokes `agent_flow.py propose` internally when JIKUO applies
- agent returns proposal in the same chat
- user reviews
- any durable write remains separate

Rollback / supersession:

- if the instruction pack causes noisy over-triggering, revise trigger conditions before Skill / MCP packaging
- if `agent_flow.py` event names change, update this file and this work order together
- if a future Skill or MCP tool changes behavior, supersede this instruction pack explicitly

Observability:

- command shapes preserve `event`, `project-root`, `user-phrase`, optional `task-title`, and optional `session-id`
- chat return contract requires write-effect and approval-boundary reporting

---

## 3. Scope

This work order implements:

- a project-local desktop-agent instruction pack
- explicit trigger handling rules
- event invocation map for current `agent_flow.py propose`
- same-chat return contract
- approval and write boundary guidance
- refusal rules
- future Skill projection boundary
- task-map / execution-mount / Sprint-index updates

---

## 4. Out Of Scope

This work order does not:

- install a Codex Skill
- edit `.codex/AGENTS.md`
- implement an MCP server
- implement a Codex Plugin
- implement guarded `agent_flow.py apply`
- change any lower-level guarded write helper
- create `.jikuo/task_sessions/`
- update `.jikuo/project_state.yaml`
- implement frontend screens
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
- `docs/jikuo/governance/jikuo_desktop_agent_instruction_pack.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md`
- `tools/jikuo/agent_flow.py`
- `tools/jikuo/agent_flow_tests.py`
- `tools/audit/check_rule_registry.py`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 6. Pre-Audit

Task target:

- add a lightweight project-local agent instruction pack after the no-write runner is validated in desktop chat

Compliance status:

- aligned with desktop-agent-first posture because routine operation remains in chat
- aligned with Skill Creator guidance because the instruction pack stays concise and does not duplicate all source contracts
- aligned with contract-first hardening because this defines invocation behavior before installing a Skill or MCP tool
- aligned with no-write safety because it only instructs `agent_flow.py propose`
- aligned with `.codex/AGENTS.md` boundary because no global rule promotion is made

Required adjustments:

- keep the pack short enough to act as a future Skill reference
- make the write boundary explicit
- update registry / mount docs so downstream work knows this atom exists

---

## 7. Implemented Artifact

Instruction pack:

- `docs/jikuo/governance/jikuo_desktop_agent_instruction_pack.md`

Current safe command shape:

```powershell
python -B tools/jikuo/agent_flow.py propose --event "<event>" --task-title "<task title>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown
```

Supported current events:

- `status`
- `task_start`
- `task_continue`
- `index`
- `evidence`
- `verification`
- `completion`
- `handoff`
- `audit`

---

## 8. Testing Governance Declaration

`unit`:

- N/A because no parser or runtime code changed.

`integration`:

- N/A because no installed Skill, MCP server, plugin, frontend, or adapter is implemented.

`workflow / orchestration`:

- review that the instruction pack maps desktop triggers to the current `agent_flow.py propose` event surface.

`semantic regression`:

- N/A because this slice governs process invocation, not narrative product output.

`smoke`:

- run one no-write `agent_flow.py propose --event task_start` command after docs are updated.

`human governance review`:

- user reviews whether the instruction pack is readable and safe enough before any Skill / MCP packaging.

---

## 9. Delivery Criteria

- `jikuo_desktop_agent_instruction_pack.md` exists and is concise.
- It maps explicit user shortcuts to current `agent_flow.py propose` events.
- It tells agents to return cards in the same desktop chat.
- It says `agent_flow.py propose` is no-write.
- It states unified guarded `agent_flow.py apply` is not available.
- It does not edit `.codex/AGENTS.md`.
- It does not install a Skill.
- It updates task map, execution mount, and Sprint index.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- the user agrees that the instruction pack is readable enough for desktop-agent use
- the user agrees that project-local instruction is the right intermediate step before installable Skill / MCP packaging
- verification confirms no durable JIKUO sidecar write occurred
- report-only checker obligations are either satisfied or explicitly recorded as manual review items

Do not proceed to installable Codex Skill, MCP wrapper, Codex Plugin, guarded `agent_flow.py apply`, frontend, or gate implementation until this slice is accepted or revised.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/jikuo/agent_flow_tests.py
```

Result:

- passed, 3 tests

```powershell
python -B tools/jikuo/agent_flow.py propose --event task_start --task-title "JIKUO AGENT-06 instruction pack smoke" --project-root "D:\personal_project\NarrativeSystem" --user-phrase "<exact user phrase as spoken>" --format markdown
```

Result:

- returned a no-write proposal
- `Writes performed: false`
- `Guarded apply available: false`
- emitted `DPL-03`, `DPL-04`, and `DPL-06` atom trace entries

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/governance/jikuo_desktop_agent_instruction_pack.md --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-06_lightweight_desktop_agent_instruction_pack.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-06_lightweight_desktop_agent_instruction_pack.md
```

Initial result:

- registry validation passed
- missing `Delivery Criteria` and `Acceptance Gate` sections were reported
- this work order was updated to add both sections

Follow-up result after section fix:

- registry validation passed
- `R-006` required work-order fields and sections all reported `OK`
- `R-012` Sprint index document requirement reported `OK`
- runtime audit bundle fields and manual declarations remained `REVIEW`, as expected for this documentation / instruction slice

No-write state checks:

- root `.jikuo/task_sessions/` remained absent
- `.jikuo/project_state.yaml` still had `latest_task_session_refs: []`

---

## 12. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- installable Codex Skill
- MCP tool wrapper
- Codex Plugin
- guarded `agent_flow.py apply`
- frontend implementation
- automatic durable write
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
