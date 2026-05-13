# SPRINT_050_WO-PER-JIKUO-FLOW-02: Desktop App Primary Operating Loop

> **Date**: 2026-05-05  
> **Status**: Accepted; updated with AGENT-06 instruction-pack composition  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / primary user operation chain / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`; `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`; `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`; `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`; `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`; `SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md`  
> **Current slice**: primary desktop-app operating loop contract only; no adapter, skill, MCP server, frontend, gate, automatic write, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user wants to use JIKUO during ordinary AI-assisted project work without switching to CLI or frontend for routine task start, rule review, evidence review, approval, completion, or handoff.  
> **Runtime chain**: user speaks in desktop APP -> agent classifies JIKUO scenario -> agent invokes internal JIKUO atom/tool if needed -> agent renders card/summary in chat -> user approves/rejects/modifies in chat -> agent applies only explicitly approved guarded action -> agent renders result/handoff in chat -> project-local state is updated only by approved actions.  
> **Canonical source**: accepted product positioning, desktop-agent-first contract, scenario-chain/document-mounting model, user journey model, task-session command contracts, and the correction that helper/CLI artifacts are atoms rather than the user-facing chain.  
> **Bridge object**: `JikuoDesktopPrimaryOperatingLoopV0`; `JikuoDesktopAgentActionContractV0`.  
> **Consumer projection**: Codex / Claude desktop APP workflow instructions, future Codex skill/plugin, future Claude MCP/tool package, future CLI fallback, future frontend configuration/control/audit surfaces.  
> **Lifecycle**: draft primary loop -> user review -> accepted first user operation chain -> later AGENT-04 invocation contract / skill or plugin planning.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Correction

> **中文注释**：这张工单修正一个顺序错误：我们已经拆出了很多原子动作，但还没有把它们重新组合成用户真正使用的第一条主链路。

The previous JIKUO work produced useful atoms:

- project-state inspection
- guarded project-state write
- task-session start plan
- guarded task-session write
- task-session index refresh
- evidence / verification / completion / handoff updates
- desktop card projection helper

But atoms are not the product experience.

The product-facing primary operation chain must start and end inside the user's active desktop APP conversation:

- Codex Desktop
- Claude Desktop

CLI and frontend are supporting surfaces:

- CLI is an internal bridge for agents or an advanced-user fallback.
- Frontend is for configuration, browsing, control, and audit history.
- Neither should be required for routine daily JIKUO operation.

The first accepted user operation chain should therefore be:

`Desktop App Primary Operating Loop`

This loop recomposes the existing atoms into an actual user path.

---

## 2. Technical Boundary

> **中文注释**：本工单只重排链路和任务优先级，不实现 adapter、skill、MCP、前端或自动写入。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md`
- `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`
- `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`

Mainline explicitly not changed:

- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_cards.py`
- `.jikuo/project_state.yaml`
- `.jikuo/task_sessions/`
- `.codex/AGENTS.md`
- Codex adapter behavior
- Claude adapter behavior
- skill/plugin/MCP implementation
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine

Canonical source:

- accepted `JIKUO-UX-00`
- accepted `JIKUO-PRD-01`
- accepted `JIKUO-AGENT-00`
- draft `JIKUO-FLOW-01`
- accepted `JIKUO-SCENARIO-CHAIN-01`
- implemented task-session atoms
- implemented card projection atom

Bridge object:

- `JikuoDesktopPrimaryOperatingLoopV0`
- `JikuoDesktopAgentActionContractV0`

Consumer projection:

- next AGENT work order
- future Codex / Claude instructions
- future skill/plugin/MCP wrapper
- future CLI fallback
- future frontend views

Lifecycle:

- define the primary loop
- user reviews the loop
- accepted loop becomes the first user operation chain
- later work maps internal atoms to this loop
- adapter/skill/MCP/frontend work remains blocked until this loop is accepted

Rollback / supersession:

- if the user rejects the loop, revise this work order before more helper or adapter implementation
- helper artifacts remain internal atoms and must not be presented as the primary user path
- future task order must preserve this loop unless explicitly superseded

Propagation surfaces:

- productization task map
- Sprint index
- FLOW-01 correction note
- SCENARIO-CHAIN-01 correction note
- AGENT-03 correction note

Observability:

- future implementation should record which desktop APP initiated the loop, which internal atom was invoked, what card/summary was shown, what exact user phrase approved or rejected, what guarded action was applied, and what result was shown back in chat

---

## 3. Scope

This work order defines:

- the first user operation chain
- the difference between user operation chain and internal atoms
- desktop-app primary surface rules
- the main operating loop
- common sub-loops
- atom-to-loop recomposition map
- revised task order
- affected document updates
- acceptance criteria

---

## 4. Out Of Scope

This work order does not:

- implement Codex / Claude adapter behavior
- implement a Codex skill
- implement a Claude MCP server
- implement automatic shell invocation
- implement frontend screens
- modify task-session helper behavior
- create task-session files
- update project-state index
- promote report-only checks into gates
- judge product-output quality
- change runtime narrative-engine behavior

---

## 5. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`
- `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`
- `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_cards.py`
- `SPRINT_050_20260409.md`

---

## 6. Pre-Audit

Task target:

- re-order JIKUO productization around the desktop APP primary operating loop

Compliance status:

- aligned with UX/scenario-first methodology because atoms are recomposed into the first user operation chain
- aligned with desktop-agent-first posture because ordinary operation stays in Codex / Claude desktop APP
- aligned with current implementation boundary because helper/CLI artifacts remain internal atoms
- aligned with testing governance because this is workflow/orchestration documentation, not product-output judgement

Required adjustments:

- task map must name this loop as the next decision point
- Sprint index must link this work order
- AGENT-03 must be reframed as an internal atom, not a user-facing operating path
- FLOW-01 and SCENARIO-CHAIN-01 must record this correction

---

## 7. Desktop App Primary Operating Loop

The primary loop:

1. User states intent inside Codex / Claude desktop APP.
2. Agent classifies whether the intent triggers JIKUO governance.
3. Agent internally invokes the relevant JIKUO atom when needed.
4. Agent renders the result as chat-native summary or card.
5. User approves, rejects, defers, or asks to modify inside the same chat.
6. Agent applies only the explicitly approved guarded action.
7. Agent renders the action result in chat.
8. Agent continues the task under the updated governance state.
9. Agent renders completion / missing evidence / handoff in chat.

Hard user-experience rule:

- routine use must not require the user to open CLI
- routine use must not require the user to open a frontend
- routine use must not require the user to edit raw YAML

---

## 8. Common Sub-Loops

### 8.1 Project Enable / Inspect

User phrase examples:

- `"<exact user phrase as spoken>"`

Desktop loop:

- user asks whether JIKUO is active
- agent internally inspects project state
- agent reports initialized / missing / conflict in chat
- user approves initialization only if a write is proposed

Internal atoms:

- `project_state.py status`
- `project_state.py init --dry-run`
- guarded `project_state.py init --write` only after explicit approval

### 8.2 Rule Preference Capture

Desktop loop:

- user states a working-method preference
- agent proposes a rule candidate in chat
- user accepts, revises, or rejects
- durable registry write remains a later guarded action

Internal atoms:

- rule registry view model
- future rule proposal object
- future rule proposal persistence

### 8.3 Required Reference / Document Mount

Desktop loop:

- user says certain files must be consulted for a class of work
- agent proposes document mounts in chat
- user confirms layer and scope
- future tasks use the mount as required context

Internal atoms:

- scenario-chain model
- document mount model
- future mount persistence

### 8.4 Task Start

Desktop loop:

- user starts or continues a task
- agent generates task governance summary/card in chat
- user approves durable task-session creation only if needed
- task proceeds without the user opening CLI

Internal atoms:

- `task_session.py start --dry-run`
- `task_session_cards.py start-preview`
- guarded `task_session.py start --write`

### 8.5 In-Task Evidence / Obligation Review

Desktop loop:

- agent notices evidence, verification, or missing obligation
- agent summarizes it in chat
- user can ask for more detail or defer
- guarded append happens only after explicit approval when persistence is needed

Internal atoms:

- `task_session.py update --dry-run`
- `task_session_cards.py update-preview`
- guarded evidence / verification append

### 8.6 Approval / Durable Action

Desktop loop:

- agent presents target, effect, and non-effect
- user responds in natural language
- agent records exact user phrase
- agent applies only the specific approved effect
- agent reports result back in chat

Internal atoms:

- approval capture object
- guarded write commands
- result card projection

### 8.7 Completion / Handoff

Desktop loop:

- agent presents completion or handoff summary in chat
- user accepts, revises, defers, or requests handoff
- agent records only approved completion / handoff state
- next desktop agent continues from the summary and required reads

Internal atoms:

- guarded completion update
- guarded handoff update
- future handoff card

### 8.8 Rule Evolution

Desktop loop:

- repeated friction or missing evidence becomes a rule-change suggestion
- agent proposes change in chat
- user approves only proposal or durable rule update explicitly

Internal atoms:

- future audit/event records
- future rule proposal persistence
- future frontend audit dashboard

---

## 9. Loop Composition Map

> **中文注释**：本节管理“这条用户链路由哪些原子能力组合而成”。原子本身只在 task map 的 `Atomic Capability Registry` 定义；这里仅引用 `CAP-*` ID，避免重复定义和文档漂移。

### 9.1 Composition Management Policy

Loop composition is worth managing when:

- the loop is user-visible
- the loop may call durable-write atoms
- the loop defines approval, completion, handoff, or audit boundaries
- the loop is an input to `agent_flow.py`, Skill, MCP, plugin, or frontend work
- changing one atom could alter the loop's user-facing behavior or safety boundary

Loop composition does not need to track:

- private helper functions
- temporary implementation details
- low-level parser / serializer internals
- code paths that cannot affect user-visible state, write boundaries, approval, or handoff

Source-of-truth rule:

- atom definition lives in `docs/jikuo/governance/jikuo_productization_task_map.md` section `Atomic Capability Registry`
- loop composition lives in the relevant loop work order, starting with this `JIKUO-FLOW-02`
- loop composition must reference atom IDs instead of duplicating atom definitions
- when an atom is changed, affected loop rows should be reviewed
- when a loop row is changed, required atom status and approval boundaries should be checked
- future runtime trace should report both loop step id and atom IDs used

### 9.2 Desktop Primary Loop Composition

| Loop Step ID | User-Visible Step | Atom IDs Used | Atom Mode | Approval Boundary | Product Meaning |
|---|---|---|---|---|---|
| `DPL-01` | User speaks in Codex / Claude desktop APP | `CAP-AGENT-INVOCATION-01` | contract | no durable write | Gives the user a low-friction way to start JIKUO without leaving chat |
| `DPL-02` | Agent classifies JIKUO scenario | `CAP-AGENT-INVOCATION-01`; `CAP-AGENT-FLOW-01`; `CAP-DESKTOP-AGENT-INSTRUCTION-01` | contract / implemented no-write runner / implemented instruction | no durable write | Turns user intent into an explicit invocation scenario instead of relying on vague memory |
| `DPL-03` | Agent inspects project JIKUO state | `CAP-PROJECT-STATE-STATUS-01`; `CAP-PROJECT-STATE-INIT-DRYRUN-01` | no-write | approval only if project-state write is proposed later | Shows whether JIKUO can run and what setup is missing |
| `DPL-04` | Agent previews task/session state | `CAP-TASK-STATUS-01`; `CAP-TASK-START-DRYRUN-01`; `CAP-TASK-INDEX-DRYRUN-01`; `CAP-TASK-UPDATE-DRYRUN-01` | no-write | approval only if a lifecycle write is proposed later | Lets the user see task governance state before persistence |
| `DPL-05` | Agent detects rule obligations, audit needs, or policy configuration previews | `CAP-RULE-REGISTRY-01`; `CAP-CHECKER-01`; `CAP-CHECKER-JSON-01`; `CAP-POLICY-STORE-STATUS-01`; `CAP-POLICY-TRIGGER-EVALUATE-01`; `CAP-POLICY-CONDITION-EVALUATOR-01`; `CAP-POLICY-STORE-WRITE-PROPOSE-01`; `CAP-POLICY-EVIDENCE-CHECK-01`; `CAP-POLICY-EVIDENCE-INGEST-01` | no-write / report-only | no blocking approval in current phase; future policy writer needs separate approval | Makes relevant governance obligations, policy-store readiness, exact lifecycle-trigger matches, explicit condition status, policy write targets, persisted task-session evidence, and evidence status visible without turning them into gates |
| `DPL-06` | Agent renders card / summary in chat | `CAP-CARD-TASKSESSION-01`; `CAP-AGENT-INVOCATION-01` | no-write projection | no durable write | Keeps routine review inside the desktop APP conversation |
| `DPL-07` | User approves, rejects, defers, or modifies | `CAP-AGENT-INVOCATION-01`; `CAP-AGENT-FLOW-01` proposal boundary | contract / proposal-only runner | exact effect must be selected before write; unified apply not implemented | Prevents one vague approval from applying to multiple hidden actions |
| `DPL-08` | Agent applies approved project-state write if requested | `CAP-PROJECT-STATE-WRITE-01` | guarded write | explicit approval required | Creates initial JIKUO project state only when the user approves that specific effect |
| `DPL-09` | Agent applies approved task-session creation if requested | `CAP-TASK-START-WRITE-01` | guarded write | explicit approval required | Creates one compact task-session record without raw chat logging |
| `DPL-10` | Agent applies approved index refresh if requested | `CAP-TASK-INDEX-REFRESH-01` | guarded write | separate explicit approval required | Updates project-state latest session refs without creating sessions |
| `DPL-10A` | Agent applies approved policy-store create / append if requested | `CAP-POLICY-STORE-WRITE-01`; `CAP-POLICY-STORE-APPEND-01`; `CAP-POLICY-DECISION-WRITE-01` | guarded write | separate explicit approval required for each policy id and write target | Moves reviewed rules into project policy storage and records the approval decision while keeping first-write and active-store append distinct from revision |
| `DPL-11` | Agent proposes or applies approved evidence / verification update if requested | `CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01`; `CAP-TASK-EVIDENCE-APPEND-01`; `CAP-TASK-VERIFICATION-APPEND-01` | no-write proposal / guarded write | explicit session id and approval required | Turns reviewed policy evidence into a concrete persistence proposal, then records compact process evidence only after approval |
| `DPL-12` | Agent applies approved completion / handoff if requested | `CAP-TASK-COMPLETE-01`; `CAP-TASK-HANDOFF-01` | guarded write | completion and handoff are separate effects unless explicitly combined later | Lets the user close or transfer the task with auditable state |
| `DPL-13` | Agent reports result back in chat | `CAP-CARD-TASKSESSION-01`; `CAP-AGENT-FLOW-01`; `CAP-DESKTOP-AGENT-INSTRUCTION-01` | projection / implemented no-write runner / implemented instruction | no new write unless another card is approved | Confirms what happened, what did not happen, and what remains pending |
| `DPL-14` | Future instruction/tool layers smooth invocation | `CAP-DESKTOP-AGENT-INSTRUCTION-01`; `CAP-CODEX-SKILL-01`; `CAP-MCP-TOOL-01`; `CAP-CODEX-PLUGIN-01` | implemented project-local instruction / planned packaged surfaces | must preserve the same approval boundaries | Improves usability without changing the underlying safety contract |

### 9.3 Atom Recomposition Inventory

| Atom ID | Atom | Current Status | Desktop Loop Role | User Should Directly Run? |
|---|---|---|---|---|
| `CAP-PROJECT-STATE-STATUS-01` | `project_state.py status` | implemented | internal project-state inspection | no |
| `CAP-PROJECT-STATE-INIT-DRYRUN-01` | `project_state.py init --dry-run` | implemented | internal initialization preview | no |
| `CAP-PROJECT-STATE-WRITE-01` | `project_state.py init --write` | implemented guarded | approved project-state creation | no |
| `CAP-TASK-START-DRYRUN-01` | `task_session.py start --dry-run` | implemented | internal task-session preview | no |
| `CAP-TASK-START-WRITE-01` | `task_session.py start --write` | implemented guarded | approved task-session creation | no |
| `CAP-TASK-STATUS-01` | `task_session.py status` | implemented | internal task-session inspection | no |
| `CAP-TASK-INDEX-DRYRUN-01` | `task_session.py index --dry-run` | implemented | internal index preview | no |
| `CAP-TASK-INDEX-REFRESH-01` | `task_session.py index --refresh` | implemented guarded | approved index refresh | no |
| `CAP-TASK-UPDATE-DRYRUN-01` | `task_session.py update --dry-run` | implemented | internal lifecycle preview | no |
| `CAP-TASK-EVIDENCE-APPEND-01` | `task_session.py update --append-evidence` | implemented guarded | approved evidence persistence | no |
| `CAP-TASK-VERIFICATION-APPEND-01` | `task_session.py update --append-verification` | implemented guarded | approved verification persistence | no |
| `CAP-TASK-COMPLETE-01` | `task_session.py complete` | implemented guarded | approved completion persistence | no |
| `CAP-TASK-HANDOFF-01` | `task_session.py handoff` | implemented guarded | approved handoff persistence | no |
| `CAP-CARD-TASKSESSION-01` | `task_session_cards.py` | implemented no-write | internal card projection atom | no |
| `CAP-AGENT-INVOCATION-01` | `JIKUO-AGENT-04` | draft contract | desktop loop trigger and rendering contract | yes, through chat |
| `CAP-AGENT-FLOW-01` | `agent_flow.py propose` | implemented no-write | deterministic local proposal runner | no |
| `CAP-DESKTOP-AGENT-INSTRUCTION-01` | project-local desktop-agent instruction pack | implemented no-write instruction | smoother Codex / Claude desktop invocation before packaging | yes, through chat |
| `CAP-POLICY-STORE-STATUS-01` | `policy_store.py status` | implemented no-write | internal policy-store readiness inspection | no |
| `CAP-POLICY-TRIGGER-EVALUATE-01` | `policy_store.py evaluate --event` | implemented no-write | internal exact lifecycle trigger evaluation and required-action projection | no |
| `CAP-POLICY-CONDITION-EVALUATOR-01` | `policy_store.py evaluate --task-type --jikuo-layer --changed-path`; `agent_flow.py propose` metadata args | implemented no-write | internal condition narrowing before required-action projection | no |
| `CAP-POLICY-STORE-WRITE-PROPOSE-01` | `policy_store.py plan-write`; `agent_flow.py propose --event policy_write_plan` | implemented no-write proposal | projects policy-store write targets and non-effects before durable policy writing exists | no |
| `CAP-POLICY-STORE-WRITE-01` | `policy_store.py write-policy --confirm-write-policy --approval-phrase` | implemented guarded initial write | creates the first approved report-only policy store only after explicit approval | no |
| `CAP-POLICY-STORE-APPEND-01` | `policy_store.py write-policy --confirm-write-policy --approval-phrase` against an active store | implemented guarded append | appends one new approved report-only policy to an active store while preserving existing active refs | no |
| `CAP-POLICY-DECISION-WRITE-01` | `policy_store.py write-policy --confirm-write-policy --approval-phrase` | implemented guarded write audit | records the approval decision for each successful policy create / append | no |
| `CAP-POLICY-EVIDENCE-CHECK-01` | `policy_store.py evaluate --event --produced-evidence-json` / evidence flags | implemented no-write | internal required-evidence matching and missing-evidence projection | no |
| `CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01` | `agent_flow.py propose --event policy_evidence_record` | implemented no-write proposal | converts explicit policy evidence refs into guarded task-session evidence append command proposal | no |
| `CAP-POLICY-EVIDENCE-INGEST-01` | `policy_store.py evaluate --task-session-id`; `agent_flow.py propose --event policy_evidence_check` | implemented no-write | reads explicit persisted task-session policy evidence into report-only matching | no |
| `CAP-CODEX-SKILL-01` | future installable Codex Skill | not implemented | packaged Codex desktop invocation | yes, through chat |
| `CAP-MCP-TOOL-01` | future MCP wrapper | not implemented | cross-client tool invocation | yes, through chat |
| `CAP-CODEX-PLUGIN-01` | future Codex Plugin | not implemented | Codex-side productized packaging | yes, through chat |
| future frontend | future UI | not implemented | configuration/control/audit surface | optional |

---

## 10. Revised Task Order

Accepted immediate sequence:

1. Create `JIKUO-AGENT-04: Desktop Agent Invocation Contract`.
2. Implement a local deterministic `agent_flow.py`.
3. Add a project-local lightweight desktop-agent instruction pack so Codex / Claude can invoke the local flow more consistently before any installable Skill.
4. Decide whether the next packaging slice is installable Codex Skill, MCP wrapper, or guarded `apply` planning.
5. Wrap `agent_flow.py` as an MCP tool when runner and instruction semantics are stable, prioritizing Claude / cross-client consistency.
6. Consider a Codex Plugin only after runner / MCP semantics are stable.

Important ordering correction:

- `JIKUO-AGENT-03` is useful as an internal atom.
- It is not the user-facing operating loop.
- More helper code should not be added until the desktop primary loop is accepted.
- frontend preview should not precede the desktop invocation contract.
- pure natural-language auto-trigger should not be the only trigger path.

Execution mount:

- `docs/jikuo/governance/jikuo_execution_mounts.md`

---

## 11. Testing Governance Declaration

- `unit`: N/A because no code is implemented in this slice.
- `integration`: N/A because no adapter, skill, MCP, frontend, or storage integration is implemented.
- `workflow/orchestration`: required; the loop must cover project inspect, rule preference, document mount, task start, evidence review, approval, completion, handoff, and rule evolution.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against this new work order and updated planning docs.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for user operation clarity, surface priority, and atom-to-chain recomposition.

---

## 12. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| F2-DC-01 | Declare deterministic work-order header fields | Header exists |
| F2-DC-02 | State product correction | Section 1 exists |
| F2-DC-03 | Define Desktop App Primary Operating Loop | Section 7 exists |
| F2-DC-04 | Define common sub-loops | Section 8 exists |
| F2-DC-05 | Map atoms back to the user chain with loop step ids, atom ids, atom mode, approval boundary, and product meaning | Section 9 exists |
| F2-DC-06 | Reorder downstream tasks | Section 10 exists |
| F2-DC-07 | Declare testing-governance layers | Section 11 exists |
| F2-DC-08 | Update productization task map | Verification log records checker result |
| F2-DC-09 | Update Sprint index | Verification log records checker result |
| F2-DC-10 | Add correction notes to affected upstream docs | Verification log records changed docs |

---

## 13. Acceptance Gate

User review should confirm:

- this is the first user operation chain for JIKUO
- routine use starts and completes inside Codex / Claude desktop APP
- CLI/helper commands are internal atoms, not the primary user path
- frontend is optional for configuration/control/audit, not required for daily operation
- existing atoms are recomposed into the loop rather than becoming separate product flows
- next implementation should target desktop-agent invocation behavior, not more standalone helper output

Do not continue to desktop adapter, skill/plugin/MCP implementation, frontend preview, auto-start, or additional helper expansion until the user accepts this primary operating loop.

---

## 14. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md --added docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md
```

Expected result:

- report-only checker exits `0`
- deterministic work-order fields and sections report `OK`
- Sprint index document evidence reports `OK`
- manual declaration and runtime audit bundle fields may remain `REVIEW`

Actual result:

- report-only checker exited `0`
- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- `user_scenario`, `runtime_chain`, `canonical_source`, `bridge_object`, `consumer_projection`, `lifecycle`, required work-order fields, required sections, and Sprint index document evidence reported `OK`
- runtime audit bundle fields and manual declarations remained `REVIEW`, as expected for this report-only governance slice
- root `.jikuo/task_sessions/` remained absent
- root `.jikuo/project_state.yaml` still had `latest_task_session_refs: []`

Composition map addendum result:

- `Loop Composition Map` added to Section 9 with loop step ids, atom ids, atom mode, approval boundary, and product meaning
- `Atomic Capability Registry` remains in `jikuo_productization_task_map.md`; Section 9 references `CAP-*` ids instead of redefining atoms
- report-only checker exited `0` for the addendum check
- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, and `R-004`
- required work-order fields reported `OK`; runtime audit bundle fields and manual declarations remained `REVIEW`, as expected for this documentation-only slice
- root `.jikuo/task_sessions/` remained absent
- root `.jikuo/project_state.yaml` still had `latest_task_session_refs: []`

---

## 15. Acceptance Record And Execution Mount

> **中文注释**：用户接受了以 `JIKUO-AGENT-04 -> agent_flow.py -> Skill / Agent 指引 -> MCP tool -> Codex Plugin` 为主线的后续方案。本记录把它固化为后续执行顺序。

Decision:

- user accepted the Desktop App Primary Operating Loop direction and the staged implementation sequence

Accepted sequence:

1. `JIKUO-AGENT-04: Desktop Agent Invocation Contract`
2. local deterministic `agent_flow.py`
3. project-local lightweight desktop-agent instruction pack
4. installable Codex Skill / MCP wrapper / guarded `apply` planning decision
5. MCP tool wrapper for Claude / cross-client consistency
6. Codex Plugin for later productized Codex-side experience

Execution mount:

- `docs/jikuo/governance/jikuo_execution_mounts.md`

Downstream rule:

- future JIKUO productization tasks should mount `jikuo_execution_mounts.md` before deciding the next task
- helper-only expansion, frontend preview, MCP implementation, or Codex Plugin work should not jump ahead of `JIKUO-AGENT-04`

Still not accepted:

- implementing `agent_flow.py` before `JIKUO-AGENT-04`
- implementing MCP before runner semantics are defined
- implementing Codex Plugin before MCP / runner semantics stabilize
- requiring ordinary users to run CLI commands
- relying on pure natural-language automatic trigger as the only trigger path
