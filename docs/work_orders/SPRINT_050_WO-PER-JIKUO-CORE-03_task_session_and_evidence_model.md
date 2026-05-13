# SPRINT_050_WO-PER-JIKUO-CORE-03: Task Session And Evidence Model

> **Date**: 2026-05-04  
> **Status**: Part 1 accepted by user; Part 2 task-session schema accepted for downstream projection planning  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / core data model / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-WORKTREE-05A_auditable_engine_evidence_model.md`; `SPRINT_050_WO-PER-WORKTREE-05D_local_audit_checker_report_only.md`; `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`; `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`; `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`; `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`  
> **Current slice**: Part 2 - task-session schema document; no storage, frontend, CLI, adapter, checker, gate, registry migration, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user needs one AI task run to leave a project-local, auditable record of scenario chain, triggered rules, required references, evidence status, approvals, verification, and handoff state.  
> **Runtime chain**: task intent -> task-session draft -> scenario chain snapshot -> changed surface snapshot -> rule result snapshot -> document mount snapshot -> evidence checks -> user decisions -> completion state -> handoff/audit trail.  
> **Canonical source**: accepted evidence model, report-only checker baseline, structured result model, UI-ready registry view model, FLOW-01 draft, and accepted SCENARIO-CHAIN-01.  
> **Bridge object**: `JikuoTaskSessionV0`; `JikuoEvidenceSnapshotV0`.  
> **Consumer projection**: desktop-agent task cards, auxiliary CLI reports, future frontend task/audit views, future handoff summaries, and future gate feasibility analysis.  
> **Lifecycle**: draft session -> active session -> completion proposed -> accepted / revision requested / deferred -> handoff ready -> archived audit record.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“机括如何记录一次 AI 任务”，让用户之后能看清任务为什么这样做、触发了哪些规则、缺了哪些证据。

JIKUO already has:

- report-only checker output
- structured result envelope
- UI-ready registry view model
- desktop-agent-first flow
- scenario-chain and document-mounting model

But it still needs a model for one concrete AI task run.

Without a task-session model:

- governance evidence remains scattered across chat, checker output, work orders, and memory
- Codex / Claude handoff still depends too much on conversation memory
- required reference files cannot be proven after the fact
- rule friction cannot be measured for later evolution
- frontend audit views have no stable data shape

This work order defines the minimum task-session contract before implementation.

---

## 2. Technical Boundary

> **中文注释**：本工单只定义数据契约，不实现存储或工具。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`
- `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`

Mainline explicitly not changed:

- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `docs/jikuo/schemas/rule_registry_view_model.schema.md`
- `tools/audit/check_rule_registry.py`
- checker JSON output behavior
- task-session storage
- desktop-agent card renderer
- CLI bridge commands
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine
- `.codex/AGENTS.md`

Canonical source:

- `WORKTREE-05A` auditable evidence model
- `WORKTREE-05D` report-only checker baseline
- accepted `JIKUO-CORE-01` structured result model
- accepted `JIKUO-CORE-02` registry view-model schema
- draft `JIKUO-FLOW-01`
- accepted `JIKUO-SCENARIO-CHAIN-01`

Bridge objects:

- conceptual `JikuoTaskSessionV0`
- conceptual `JikuoEvidenceSnapshotV0`

Consumer projection:

- desktop-agent task-start, progress, completion, and handoff cards
- future auxiliary CLI report output
- future frontend task-session browser
- future audit/evolution dashboard
- future gate feasibility analysis

Lifecycle:

- session is drafted when a task starts or a user asks for governed work
- session becomes active when scenario chain and initial obligations are resolved
- evidence snapshots are updated during work
- completion is proposed with verification and governance state
- user accepts, requests revision, rejects, or defers
- accepted/deferred state can be handed off or archived later

Rollback / supersession:

- Part 1 may be superseded by a later schema document
- future implementation must support session supersession when a task is restarted or abandoned
- user decisions must not be overwritten by later agent inference
- report-only records must not become blocking gate records without separate approval

Propagation surfaces:

- this work order
- productization task map
- Sprint index
- future task-session schema or sidecar
- future desktop-agent / CLI / frontend projections

Observability:

- future implementation should expose session id, scenario chain, triggered rules, document mounts, evidence statuses, user decisions, verification status, handoff readiness, and supersession links

---

## 3. Scope

Part 1 defines:

- task-session purpose and lifecycle
- top-level task-session object shape
- scenario-chain snapshot
- changed-surface snapshot
- rule-result snapshot
- document-mount snapshot
- evidence snapshot
- user-decision and approval snapshot
- completion and handoff state
- audit trail and supersession fields
- consumer projections
- delivery criteria and acceptance gate

---

## 4. Out Of Scope

This work order does not:

- implement task-session storage
- implement evidence parsing
- implement document-mount resolution
- modify registry files
- modify checker behavior
- implement desktop-agent cards
- implement CLI bridge commands
- implement frontend screens
- implement import/export tooling
- implement hooks, CI, task-stop gates, or blocking enforcement
- change narrative runtime behavior
- judge product-output quality
- define product-content semantic review rules

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
- `tools/audit/check_rule_registry.py`
- `SPRINT_050_WO-PER-WORKTREE-05A_auditable_engine_evidence_model.md`
- `SPRINT_050_WO-PER-WORKTREE-05D_local_audit_checker_report_only.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`
- `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`
- `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 6. Pre-Audit

> **中文注释**：这是 CORE-03 的事前审计：先定义任务会话记录，不做存储实现。

Task target:

- define the task-session and evidence model for one governed AI task

Compliance status:

- aligned with desktop-agent-first because the session records what the user saw in chat
- aligned with scenario-chain model because session stores scenario chain id and document mounts
- aligned with report-only checker because missing obligations are visible without changing exit behavior
- aligned with CORE-01 because session embeds structured result snapshots rather than inventing a second result vocabulary
- aligned with CORE-02 because rule metadata remains registry-derived and view-model-friendly

Required adjustments:

- keep task-session storage out of scope
- preserve report-only posture
- make user decisions explicit
- record required references as document mounts
- support cross-agent handoff without relying only on chat memory

---

## 7. Task Session Top-Level Shape V0

Conceptual shape:

```yaml
schema_version: "jikuo.task_session.v0"
kind: "jikuo_task_session"
session:
  id: ""
  status: "draft"
  created_at: ""
  updated_at: ""
  owner_surface: "codex_desktop"
  project_root: ""
  work_order_ref: ""
  task_intent: ""
scenario:
  chain_id: ""
  task_context: []
changed_surfaces: []
rule_results: []
document_mounts: []
evidence_snapshots: []
verification: {}
user_decisions: []
completion: {}
handoff: {}
audit_trail: []
supersession: {}
```

Required top-level keys:

- `schema_version`
- `kind`
- `session`
- `scenario`
- `changed_surfaces`
- `rule_results`
- `document_mounts`
- `evidence_snapshots`
- `verification`
- `user_decisions`
- `completion`
- `handoff`
- `audit_trail`
- `supersession`

---

## 8. Session Identity And Status

Session object:

```yaml
session:
  id: "jikuo-ts-..."
  status: "active"
  created_at: "ISO-8601"
  updated_at: "ISO-8601"
  owner_surface: "codex_desktop"
  project_root: "D:/personal_project/NarrativeSystem"
  work_order_ref: ""
  task_intent: ""
```

Allowed `status` values:

- `draft`
- `active`
- `completion_proposed`
- `accepted`
- `revision_requested`
- `deferred`
- `abandoned`
- `superseded`
- `handoff_ready`
- `archived`

Allowed `owner_surface` values:

- `codex_desktop`
- `claude_desktop`
- `auxiliary_cli`
- `future_frontend`
- `ci_or_bot`
- `unknown`

Rule:

- `accepted` must require a user decision record.
- `superseded` must require a supersession link.
- `handoff_ready` must include handoff references.

---

## 9. Scenario Chain Snapshot

Scenario snapshot:

```yaml
scenario:
  chain_id: "work_order_start"
  task_context:
    - "work_order_delivery"
  classification_confidence: "review"
  source_note: "Declared by user or inferred by agent at task start."
```

Allowed `classification_confidence` values:

- `explicit`
- `inferred`
- `review`
- `unknown`

Purpose:

- preserve which governance chain was active
- keep task context visible for future rule matching
- avoid treating every session as the same generic task

---

## 10. Changed Surface Snapshot

Changed surface item:

```yaml
- path: "docs/scenarios/interactive_novel/sprints/example.md"
  change_kind: "added"
  surface_type: "work_order_doc"
  declared_context:
    - "new_work_order_doc"
```

Allowed `change_kind` values:

- `added`
- `changed`
- `deleted`
- `renamed`
- `generated`
- `unknown`

Recommended `surface_type` values:

- `work_order_doc`
- `sprint_index`
- `governance_doc`
- `registry_doc`
- `checker_code`
- `runtime_code`
- `frontend_code`
- `test_code`
- `data_artifact`
- `unknown`

Purpose:

- give checker results and human review a shared surface inventory
- make task-start predictions and final changed paths comparable

---

## 11. Rule Result Snapshot

Rule result items should embed or reference `jikuo.result.v0` concepts from CORE-01.

Conceptual shape:

```yaml
- rule_id: "R-006"
  title: "New work order documents must include required sections"
  source_registry: "interactive_novel_engineering_governance"
  triggered: true
  level: "blocking"
  phase: "report_only"
  evidence_status: "ok"
  blocking_enforced: false
  message: ""
```

Required fields:

- `rule_id`
- `title`
- `triggered`
- `level`
- `phase`
- `evidence_status`
- `blocking_enforced`

Purpose:

- preserve the rule state seen during the task
- allow later audit to distinguish rule severity from actual enforcement
- support future dashboards without reparsing old text logs

---

## 12. Document Mount Snapshot

Document mount item:

```yaml
- mount_id: "dm-current-sprint"
  mount_layer: "sprint"
  role: "required_reference"
  document_ref: "docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md"
  required_when:
    - "work_order_delivery"
  status: "consulted"
  evidence_note: "Referenced as current sprint context."
  freshness_status: "current"
  missing_behavior: "report_missing"
```

Allowed `status` values:

- `required`
- `consulted`
- `missing`
- `not_applicable`
- `superseded`
- `review`
- `error`

Allowed `freshness_status` values:

- `current`
- `unknown`
- `stale`
- `superseded`
- `not_applicable`

Purpose:

- prove which reference files were required
- show whether the agent consulted them
- make missing reference files visible before completion
- support cross-agent handoff

---

## 13. Evidence Snapshot

Evidence item:

```yaml
- evidence_id: "ev-required-sections"
  source_rule_id: "R-006"
  evidence_type: "required_section"
  target_ref: "SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md"
  status: "ok"
  observed_value: "Scope, Out Of Scope, Audit References, Delivery Criteria, Acceptance Gate"
  note: ""
```

Allowed `evidence_type` values:

- `work_order_field`
- `required_section`
- `required_document`
- `declaration`
- `audit_bundle_field`
- `approval_record`
- `user_acceptance_record`
- `verification_result`
- `document_mount`
- `handoff_reference`

Allowed `status` values:

- `ok`
- `missing`
- `review`
- `not_applicable`
- `error`

Rule:

- evidence `ok` means the carrier exists or the deterministic check passed.
- evidence `ok` does not mean the product output is good.
- evidence correctness may still require human governance review.

---

## 14. Verification Snapshot

Verification object:

```yaml
verification:
  commands: []
  results: []
  not_run: []
  residual_risks: []
```

Command result item:

```yaml
- command: "python -B tools/audit/check_rule_registry.py ..."
  exit_code: 0
  summary: "registry validation passed; report-only posture preserved"
  output_ref: "inline_summary"
```

Purpose:

- keep technical verification separate from governance evidence
- preserve not-run reasons
- avoid treating command success as full task acceptance

---

## 15. User Decision And Approval Snapshot

User decision item:

```yaml
- decision_id: "ud-..."
  decision_type: "acceptance"
  phrase: "<exact user phrase as spoken>"
  surface: "codex_desktop"
  applies_to:
    - "SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01"
  durability: "downstream_planning"
  recorded_at: "ISO-8601"
  note: ""
```

Allowed `decision_type` values:

- `acceptance`
- `revision_requested`
- `defer`
- `reject`
- `task_local_rule_acceptance`
- `registry_proposal_acceptance`
- `gate_promotion_approval`
- `handoff_approval`

Allowed `durability` values:

- `task_local`
- `downstream_planning`
- `persistent_rule_candidate`
- `persistent_rule_change`
- `gate_change`
- `unknown`

Rules:

- approval must preserve the exact user phrase.
- approval must state what it applies to.
- durable registry or gate changes require a later approved implementation path.

---

## 16. Completion State

Completion object:

```yaml
completion:
  proposed: true
  status: "ready_for_review"
  summary: ""
  governance_status: "review"
  missing_items: []
  accepted_by_user: false
```

Allowed `governance_status` values:

- `ok`
- `missing`
- `review`
- `not_applicable`
- `error`

Completion must summarize:

- work outcome
- verification outcome
- triggered rule outcome
- document mount outcome
- evidence outcome
- user decision state

---

## 17. Handoff State

Handoff object:

```yaml
handoff:
  ready: false
  summary_ref: ""
  required_reads: []
  pending_decisions: []
  missing_evidence: []
  next_agent_assumptions: []
```

Purpose:

- let Codex and Claude desktop APPs continue from project-local state
- reduce reliance on long chat memory
- preserve explicit "do not do" boundaries

---

## 18. Audit Trail And Supersession

Audit event item:

```yaml
- event_id: "ae-..."
  event_type: "evidence_updated"
  actor_surface: "codex_desktop"
  timestamp: "ISO-8601"
  summary: ""
```

Allowed `event_type` values:

- `session_created`
- `scenario_resolved`
- `rule_results_recorded`
- `document_mounts_recorded`
- `evidence_updated`
- `verification_recorded`
- `user_decision_recorded`
- `completion_proposed`
- `handoff_ready`
- `session_superseded`
- `session_archived`

Supersession object:

```yaml
supersession:
  supersedes: []
  superseded_by: ""
  reason: ""
```

Purpose:

- support task restart, retry-like governance sessions, abandoned tasks, and corrected evidence without deleting history

---

## 19. Consumer Projections

Desktop-agent card projection:

- show task intent
- show scenario chain
- show required references
- show triggered rules
- show missing/review evidence
- show user decision options

Auxiliary CLI/report projection:

- show machine-readable session summary later
- export missing evidence and triggered obligations
- avoid collecting routine user approvals as the default path

Future frontend projection:

- browse task sessions
- inspect document mounts
- compare task evidence over time
- support audit/evolution dashboard

Gate feasibility projection:

- measure false positives and recurring missing evidence
- never infer gate readiness from one session

---

## 20. Testing Governance Declaration

> **中文注释**：这是核心数据契约文档，不改变 checker、UI、CLI 或 runtime 行为。

Required test layers for this slice:

- `unit`: N/A because no parser, serializer, storage, card renderer, or checker integration is implemented.
- `integration`: N/A because no UI, CLI, adapter, checker, registry migration, task-session storage, or runtime integration is implemented.
- `workflow/orchestration`: required by contract review; the model must cover task start, evidence update, completion, user decision, handoff, and supersession.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against this new work order and updated index.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for task-session field shape, document mount evidence, approval durability, handoff readiness, and report-only boundary.

---

## 21. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| C3-DC-01 | Define product question | Section 1 exists |
| C3-DC-02 | Preserve no-implementation boundary | Sections 2, 3, and 4 exist |
| C3-DC-03 | Include audit references | Section 5 exists |
| C3-DC-04 | Declare pre-audit | Section 6 exists |
| C3-DC-05 | Define top-level task-session shape | Section 7 exists |
| C3-DC-06 | Define identity/status lifecycle | Section 8 exists |
| C3-DC-07 | Define scenario and changed-surface snapshots | Sections 9 and 10 exist |
| C3-DC-08 | Define rule-result and document-mount snapshots | Sections 11 and 12 exist |
| C3-DC-09 | Define evidence and verification snapshots | Sections 13 and 14 exist |
| C3-DC-10 | Define user decision and completion snapshots | Sections 15 and 16 exist |
| C3-DC-11 | Define handoff, audit trail, and supersession | Sections 17 and 18 exist |
| C3-DC-12 | Define consumer projections | Section 19 exists |
| C3-DC-13 | Declare testing-governance layers | Section 20 exists |
| C3-DC-14 | Run report-only checker smoke | Verification log records checker result |

---

## 22. Acceptance Gate

> **中文注释**：这是 CORE-03 Part 1 的暂停点。你验收后，才考虑是否把它落成实际 schema/sidecar、adapter 或 UI。

Part 1 is ready for user review when:

- task session records what the user saw and what the system checked
- scenario chain and document mounts are first-class session snapshots
- rule results reuse CORE-01 vocabulary
- approvals preserve exact user phrase, scope, and durability
- completion separates work outcome, verification outcome, governance evidence, and user acceptance
- handoff and supersession are explicit
- no storage, checker, UI, CLI, gate, registry, or runtime implementation has been silently approved
- checker smoke has been run

Do not continue to task-session storage, schema sidecar, desktop card implementation, CLI bridge, frontend task-session browser, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 1 task-session contract.

---

## 23. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md
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

## 30. Part 2 Acceptance Record

> **中文注释**：用户确认继续，因此 Part 2 的 `jikuo.task_session.v0` schema 可以作为后续 desktop-agent card projection、sidecar planning、CLI/report planning 或 frontend audit view 的上游输入。该验收不代表批准 task-session storage、card renderer、adapter、CLI、前端、gate 或 runtime 实现。

Acceptance:

- `docs/jikuo/schemas/task_session.schema.md` may be used as an upstream schema contract.
- Desktop-agent card projection may now define how `jikuo.result.v0`, registry view fields, document mounts, and task-session fields appear in Codex / Claude desktop chat.

Still not accepted:

- creating actual task-session data
- implementing task-session storage
- implementing card renderer code
- implementing Codex / Claude adapters
- implementing CLI bridge commands
- implementing frontend views
- implementing gate behavior
- changing Sprint 050 runtime narrative engine behavior

---

## 24. Part 1 Acceptance Record

> **中文注释**：用户确认继续，因此 Part 1 的 task-session/evidence model 可以作为 Part 2 schema 文档的上游输入。该验收不代表批准 task-session storage、schema sidecar 数据、adapter、CLI、前端、gate 或 runtime 实现。

Acceptance:

- Part 1 task-session model may be used as the upstream contract for `jikuo.task_session.v0`.
- User-decision `phrase` examples should use placeholders such as `"<exact user phrase as spoken>"`, not fixed command phrases.
- Part 2 may create a schema document in `docs/scenarios/interactive_novel/governance/`.

Still not accepted:

- creating actual task-session data
- implementing task-session storage
- modifying checker behavior
- implementing desktop-agent cards
- implementing CLI bridge commands
- implementing frontend views
- implementing gate behavior
- changing Sprint 050 runtime narrative engine behavior

---

## 25. Part 2 Created Artifact

Created artifact:

- `docs/jikuo/schemas/task_session.schema.md`

Purpose:

- define `jikuo.task_session.v0`
- keep the task-session model as a shared contract for future sidecar data, desktop-agent cards, auxiliary CLI reports, frontend audit views, and gate-feasibility analysis
- define session identity, scenario snapshot, changed surfaces, rule results, document mounts, evidence, verification, user decisions, completion, handoff, audit trail, and supersession

Part 2 still does not:

- create actual task-session data
- implement task-session storage
- implement validation code
- implement desktop-agent cards
- implement CLI bridge commands
- implement frontend views
- implement checker changes
- implement gate behavior
- change runtime narrative engine behavior

---

## 26. Part 2 Testing Governance Declaration

Required test layers for this slice:

- `unit`: N/A because no parser, serializer, storage, validator, card renderer, or checker integration is implemented.
- `integration`: N/A because no UI, CLI, adapter, checker, registry migration, task-session storage, or runtime integration is implemented.
- `workflow/orchestration`: required by schema review; the schema must preserve task start, evidence update, completion, user decision, handoff, and supersession.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against this work order after creating the schema document.
- `human semantic review`: N/A because this slice does not evaluate product-output content.
- `human governance review`: required for task-session schema shape, user-decision phrase semantics, document-mount snapshot, and report-only boundary.

---

## 27. Part 2 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P2-DC-01 | Record Part 1 acceptance | Section 24 exists |
| P2-DC-02 | Create task-session schema document | `task_session.schema.md` exists |
| P2-DC-03 | Define top-level shape | Schema document Section 2 exists |
| P2-DC-04 | Define session and scenario objects | Schema document Sections 3 and 4 exist |
| P2-DC-05 | Define changed surface, rule result, document mount, and evidence shapes | Schema document Sections 5, 6, 7, and 8 exist |
| P2-DC-06 | Define verification, user decision, completion, handoff, audit trail, and supersession shapes | Schema document Sections 9 through 14 exist |
| P2-DC-07 | Preserve no-implementation boundary | No storage, checker, UI, CLI, gate, adapter, registry, or runtime code is changed |
| P2-DC-08 | Run report-only checker smoke | Verification log records checker result |

---

## 28. Acceptance Gate For Part 2

> **中文注释**：这是 Part 2 的暂停点。你验收后，才考虑是否进入实际 sidecar 数据规划、adapter/card projection、CLI/report 输出或前端 audit view。

Part 2 is ready for user review when:

- the schema document exists
- the schema preserves task-session lifecycle and evidence snapshots
- user-decision `phrase` is clearly the exact user phrase, not a fixed required command
- document mounts are included as first-class snapshots
- handoff and supersession are explicit
- no task-session storage, checker, UI, CLI, gate, adapter, registry, or runtime implementation has been changed
- checker smoke has been run

Do not continue to task-session storage, sidecar data generation, desktop card implementation, CLI bridge, frontend task-session browser, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 2 schema.

---

## 29. Part 2 Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --changed docs/jikuo/schemas/task_session.schema.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md
```

Result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, and `R-004`
- required deterministic work-order fields / sections reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved
