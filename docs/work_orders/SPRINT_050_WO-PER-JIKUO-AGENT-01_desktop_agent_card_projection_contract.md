# SPRINT_050_WO-PER-JIKUO-AGENT-01: Desktop Agent Card Projection Contract

> **Date**: 2026-05-04  
> **Status**: Accepted by user for downstream project-local state / sidecar storage planning  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / desktop-agent projection / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`; `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`; `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`; `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`; `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`; `SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`  
> **Current slice**: card projection contract only; no renderer, adapter, storage, CLI, frontend, checker, gate, registry migration, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user needs JIKUO governance state to appear as compact, understandable chat cards that show what is being checked, what references are required, what evidence is missing, and what user decision would be recorded.  
> **Runtime chain**: result/session/schema objects -> card projection selection -> desktop-agent chat card -> user decision phrase -> future decision/session record -> handoff/audit projection.  
> **Canonical source**: accepted desktop-agent-first contract, structured result model, registry view model, task-session schema, scenario-chain/document-mounting model, and report-only checker baseline.  
> **Bridge object**: `JikuoDesktopAgentCardV0`.  
> **Consumer projection**: Codex / Claude desktop APP chat, future auxiliary CLI markdown report, future frontend card preview, and future handoff summaries.  
> **Lifecycle**: card projection draft -> user review -> accepted card contract -> later renderer/adapter planning.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“机括的数据对象如何在 Codex / Claude 桌面 APP 里被用户看见”。

JIKUO now has contracts for:

- structured checker results
- registry view model
- scenario chains
- document mounts
- task sessions

But the primary user surface is still the desktop agent chat.

If card projection is not defined before implementation:

- Codex and Claude may summarize governance state differently
- required references may disappear into prose
- `review` and `missing` evidence may be mixed together
- user approvals may be recorded without clear target or effect
- future frontend and CLI may drift from the desktop experience

This work order defines the compact card projection contract.

---

## 2. Technical Boundary

> **中文注释**：本工单只定义卡片投影，不实现卡片渲染器，不修改 agent 规则，不写入状态。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md` acceptance status

Mainline explicitly not changed:

- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `docs/jikuo/schemas/rule_registry_view_model.schema.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `tools/audit/check_rule_registry.py`
- checker JSON output behavior
- task-session storage
- desktop-agent card renderer
- Codex / Claude adapter behavior
- CLI bridge commands
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine
- `.codex/AGENTS.md`

Canonical source:

- accepted `JIKUO-AGENT-00`
- accepted `JIKUO-CORE-01`
- accepted `JIKUO-CORE-02`
- accepted `JIKUO-SCENARIO-CHAIN-01`
- accepted `JIKUO-CORE-03` Part 2 schema contract
- current report-only checker baseline from `WORKTREE-05D`

Bridge object:

- conceptual `JikuoDesktopAgentCardV0`

Consumer projection:

- Codex Desktop chat
- Claude Desktop chat
- future auxiliary CLI markdown report
- future frontend card preview
- future handoff summary

Lifecycle:

- governance object exists or is inferred from task context
- agent selects a card family
- card renders only the fields needed for the current user decision
- user decision phrase is recorded later as exact user phrase if accepted
- ambiguous decisions require clarification
- later renderer/adapter implementation must preserve this contract

Rollback / supersession:

- card contract may be superseded by a later accepted card schema
- future implementation must not silently change approval effect or persistence effect
- card examples remain projection examples, not canonical storage

Propagation surfaces:

- this work order
- productization task map
- Sprint index
- future card renderer
- future adapter/CLI/frontend projections

Observability:

- future implementation should record card type, card id, source object refs, shown obligations, shown document mounts, shown missing evidence, proposed decision, and exact user phrase if a decision is recorded

---

## 3. Scope

This work order defines:

- card projection principles
- shared card envelope
- card family inventory
- required fields for each card family
- evidence and document-mount display rules
- approval phrase capture rules
- handoff projection rules
- surface fallback rules
- delivery criteria and acceptance gate

---

## 4. Out Of Scope

This work order does not:

- implement a card renderer
- implement Codex / Claude adapters
- implement task-session storage
- implement CLI bridge commands
- implement frontend screens
- modify checker behavior
- modify registry data
- modify `.codex/AGENTS.md`
- implement hooks, CI, task-stop gates, or blocking enforcement
- change narrative runtime behavior
- judge product-output quality

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
- `docs/jikuo/schemas/task_session.schema.md`
- `tools/audit/check_rule_registry.py`
- `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`
- `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`
- `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 6. Pre-Audit

> **中文注释**：这是桌面卡片投影的事前审计。它只把已有对象投影给用户，不新增存储和自动门禁。

Task target:

- define how JIKUO governance objects should be projected as desktop-agent chat cards

Compliance status:

- aligned with desktop-agent-first posture because Codex / Claude desktop chat remains primary
- aligned with CORE-01 because cards project result envelopes rather than parsing prose
- aligned with CORE-03 because cards should show task-session state and future user-decision effects
- aligned with scenario-chain model because required references should be visible as document mounts
- aligned with report-only posture because cards may report missing evidence without blocking by default

Required adjustments:

- keep card projection separate from canonical storage
- show exact approval target and persistence effect
- preserve `review` vs `missing`
- avoid fixed required user command phrases
- defer renderer/adapter implementation

---

## 7. Card Projection Principles

1. Desktop-agent cards are projections, not canonical truth.
2. Cards must state their source object: result, registry view, task session, rule proposal, or handoff.
3. Cards should show only decision-relevant information first, with references to details.
4. Cards must distinguish `missing`, `review`, `not_applicable`, and `error`.
5. Cards must show `level` and `phase` together when enforcement could be misunderstood.
6. Cards must show required document mounts when they affect task completion.
7. Cards must state what user approval would record.
8. Cards must not imply fixed command phrases.
9. Cards must not judge product-output quality.
10. Cards must not promote report-only checks into blocking gates.

---

## 8. Shared Card Envelope

Conceptual shape:

```yaml
card:
  schema_version: "jikuo.desktop_card.v0"
  card_id: ""
  card_type: "task_start_governance"
  title: ""
  source_objects: []
  status: "review"
  summary: ""
  primary_items: []
  missing_items: []
  review_items: []
  proposed_user_actions: []
  persistence_effect: "none"
  exact_phrase_policy: "record_exact_user_phrase_if_approved"
```

Required fields:

- `schema_version`
- `card_id`
- `card_type`
- `title`
- `source_objects`
- `status`
- `summary`
- `proposed_user_actions`
- `persistence_effect`
- `exact_phrase_policy`

Allowed `status` values:

- `ok`
- `missing`
- `review`
- `not_applicable`
- `error`

Allowed `persistence_effect` values:

- `none`
- `task_local`
- `downstream_planning`
- `persistent_rule_candidate`
- `persistent_rule_change`
- `task_session_update`
- `handoff_record`
- `future_gate_candidate`

---

## 9. Card Family Inventory

| Card family | Primary source object | Purpose | Typical user decision |
|---|---|---|---|
| `onboarding_summary_card` | project governance discovery | Explain current JIKUO setup | choose next action |
| `rule_candidate_card` | registry view / proposed rule | Review AI-proposed rule before persistence | accept/edit/reject/defer |
| `document_mount_card` | document mount proposal | Review required reference pack | accept/edit/defer/reject |
| `task_start_governance_card` | task session draft + result envelope | Show active scenario, rules, required refs | acknowledge/adjust/add constraint |
| `evidence_status_card` | task session + result envelope | Show missing/review/ok evidence | provide evidence/request fix/defer |
| `completion_acceptance_card` | task session completion | Review work, verification, governance state | accept/request revision/defer |
| `rule_evolution_card` | rule/session evidence | Review rule promotion/pause/supersession | approve/revise/reject |
| `handoff_summary_card` | task session handoff | Continue between Codex and Claude | use/refresh/repair summary |

---

## 10. Rule Candidate Card

Required display fields:

- proposed rule title
- trigger surface
- required evidence
- required document mounts, if any
- enforcement level and phase
- review owner
- persistence effect
- what will not happen yet

Decision requirements:

- persistent rule changes require explicit approval or clear context-bound approval after a precise card.
- ambiguous approval triggers clarification.
- user phrase should later be stored as `"<exact user phrase as spoken>"`.

---

## 11. Document Mount Card

Required display fields:

- mount role
- mount layer
- document reference
- required-when context
- missing behavior
- freshness policy
- evidence expectation

Decision requirements:

- accepting a document mount means the reference is required under the displayed context.
- accepting a document mount does not change trigger conditions by itself.
- missing required references remain report-only unless later gate work approves blocking behavior.

---

## 12. Task Start Governance Card

Required display fields:

- task intent
- scenario chain id
- likely changed surfaces
- triggered or likely-triggered rules
- required references / document mounts
- evidence expected
- enforcement posture
- explicit non-goals

Decision requirements:

- ordinary acknowledgment may be context-bound when only one task-start card is pending.
- adding one-time constraints should be task-local by default.
- persistent rule creation must route through a rule candidate card.

---

## 13. Evidence Status Card

Required display fields:

- evidence items grouped by `missing`, `review`, `error`, and `ok`
- source rule ids
- related document mounts
- required sections or declarations
- suggested next action

Display rules:

- show `missing` before `review`
- do not collapse `review` into `ok`
- do not hide `not_applicable`; include a note when it matters
- do not claim completion if required evidence remains missing

---

## 14. Completion Acceptance Card

Required display fields:

- work outcome
- verification outcome
- triggered rule outcome
- document mount outcome
- evidence outcome
- missing or review items
- exact persistence effect if accepted

Decision requirements:

- acceptance records exact user phrase.
- acceptance target must be the task completion, not a hidden rule or gate change.
- completion with missing evidence must state that missing evidence remains recorded.

---

## 15. Rule Evolution Card

Required display fields:

- source friction or repeated missing evidence
- proposed rule change
- affected fields
- before/after enforcement level and phase, if relevant
- rollback/supersession note
- approval requirement

Decision requirements:

- rule evolution cannot be inferred from casual agreement.
- enforcement promotion beyond report-only requires explicit approval and rollback plan.
- direct registry write-back remains out of scope until a later implementation contract.

---

## 16. Handoff Summary Card

Required display fields:

- task/session id when available
- current scenario chain
- required reads
- triggered rules
- document mounts
- missing evidence
- pending decisions
- explicit do-not-do boundaries
- next-agent assumptions

Decision requirements:

- incoming agent should restate assumptions before continuing.
- handoff card is a projection over project-local state and task-session state.
- chat memory alone is not canonical.

---

## 17. Approval Phrase Capture

Cards should never require fixed command phrases for ordinary use.

If a decision is recorded later, the stored decision should preserve:

- exact user phrase as spoken
- card id
- source object ids
- decision type
- decision durability
- persistence effect
- surface
- timestamp

Conceptual field:

```yaml
phrase: "<exact user phrase as spoken>"
```

Ambiguous phrase handling:

- if there is no immediately preceding clear card, ask for clarification
- if multiple approval targets are pending, ask for clarification
- if the action changes persistent rules or gate behavior, require explicit scope

---

## 18. Surface Fallback Rules

Desktop APP chat should render:

- routine governance summaries
- rule/document-mount candidate cards
- evidence status
- completion acceptance
- handoff summaries

Auxiliary CLI may render:

- long-form report
- JSON/text output
- debug details

Future frontend may render:

- persistent rule editing
- task-session browsing
- audit dashboard
- card preview

Do not require frontend or CLI for:

- routine task-start summary
- ordinary report-only acknowledgment
- ordinary task completion review
- cross-agent handoff summary

---

## 19. Testing Governance Declaration

> **中文注释**：这是投影契约，不实现 renderer，也不评价产品输出内容。

Required test layers for this slice:

- `unit`: N/A because no card renderer, adapter, parser, serializer, or storage code is implemented.
- `integration`: N/A because no UI, CLI, adapter, checker, task-session storage, or runtime integration is implemented.
- `workflow/orchestration`: required by contract review; card families must cover task start, evidence, completion, rule/document-mount proposals, rule evolution, and handoff.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against this new work order and updated index.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for approval-target clarity, persistence-effect clarity, and desktop-agent-first usability.

---

## 20. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| A1-DC-01 | Define product question | Section 1 exists |
| A1-DC-02 | Preserve no-implementation boundary | Sections 2, 3, and 4 exist |
| A1-DC-03 | Include audit references | Section 5 exists |
| A1-DC-04 | Declare pre-audit | Section 6 exists |
| A1-DC-05 | Define card projection principles | Section 7 exists |
| A1-DC-06 | Define shared card envelope | Section 8 exists |
| A1-DC-07 | Define card family inventory | Section 9 exists |
| A1-DC-08 | Define core card family fields | Sections 10 through 16 exist |
| A1-DC-09 | Define approval phrase capture | Section 17 exists |
| A1-DC-10 | Define surface fallback rules | Section 18 exists |
| A1-DC-11 | Declare testing-governance layers | Section 19 exists |
| A1-DC-12 | Run report-only checker smoke | Verification log records checker result |

---

## 21. Acceptance Gate

> **中文注释**：这是 AGENT-01 的暂停点。你验收后，才考虑 renderer、adapter、CLI/report 或前端 card preview。

This work order is ready for user review when:

- card families cover the common desktop-agent governance interactions
- cards clearly distinguish projection from canonical state
- cards show required references and missing evidence
- approval targets and persistence effects are explicit
- fixed command phrases are not required
- CLI and frontend remain auxiliary/future surfaces
- no renderer, adapter, storage, CLI, frontend, gate, registry, or runtime implementation has been silently approved
- checker smoke has been run

Do not continue to card renderer implementation, Codex/Claude adapter behavior, CLI bridge, frontend preview, task-session storage, gate implementation, or Sprint 050 runtime hardening until the user accepts this card projection contract.

---

## 22. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md
```

Result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved

---

## 23. User Acceptance Record

> **中文注释**：用户继续推进，表示 AGENT-01 可作为后续 sidecar 规划输入；这不是 renderer、adapter 或存储实现授权。

Decision:

- accepted for downstream `JIKUO-CORE-04` project-local state and sidecar storage contract planning

Recorded effect:

- desktop-agent card projection contract may be used as an upstream projection contract
- future sidecar planning may reference `JikuoDesktopAgentCardV0`
- no renderer, adapter, storage, CLI, frontend, gate, checker, registry migration, or runtime implementation is approved by this acceptance
