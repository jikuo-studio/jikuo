# Jikuo Task Session Schema

> **Schema version**: `jikuo.task_session.v0`  
> **Source work order**: `SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`  
> **Status**: Draft, task-session contract  
> **Current application track**: engineering-governance scenario package  

---

## 1. Purpose

> **中文注释**：这是未来 task-session sidecar、桌面卡片、辅助 CLI、前端审计视图共同消费的数据契约。它不是当前实现。

The task-session schema describes one governed AI task run.

It preserves:

- task identity
- scenario chain
- changed surfaces
- triggered rule results
- required document mounts
- evidence snapshots
- verification summary
- user decisions
- completion state
- handoff state
- audit trail
- supersession links

It does not:

- create task-session storage
- change checker behavior
- implement document-mount resolution
- implement desktop-agent cards
- implement CLI commands
- implement frontend views
- promote report-only checks into gates
- judge product-output quality

---

## 2. Top-Level Shape

```yaml
schema_version: "jikuo.task_session.v0"
kind: "jikuo_task_session"
session:
  id: ""
  status: "draft"
  created_at: ""
  updated_at: ""
  owner_surface: "unknown"
  project_root: ""
  work_order_ref: ""
  task_intent: ""
scenario:
  chain_id: ""
  task_context: []
  classification_confidence: "unknown"
  source_note: ""
changed_surfaces: []
rule_results: []
document_mounts: []
evidence_snapshots: []
verification:
  commands: []
  results: []
  not_run: []
  residual_risks: []
user_decisions: []
completion:
  proposed: false
  status: "not_proposed"
  summary: ""
  governance_status: "review"
  missing_items: []
  accepted_by_user: false
handoff:
  ready: false
  summary_ref: ""
  required_reads: []
  pending_decisions: []
  missing_evidence: []
  next_agent_assumptions: []
audit_trail: []
supersession:
  supersedes: []
  superseded_by: ""
  reason: ""
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

## 3. Session Object

| Field | Required | Type | Meaning |
|---|---:|---|---|
| `session.id` | yes | string | Stable task-session id |
| `session.status` | yes | enum | Current task-session lifecycle state |
| `session.created_at` | yes | string | ISO-8601 timestamp when session was created |
| `session.updated_at` | yes | string | ISO-8601 timestamp when session was last changed |
| `session.owner_surface` | yes | enum | Surface that currently owns the session |
| `session.project_root` | yes | string | Project root path or project id |
| `session.work_order_ref` | no | string | Related work-order document, if any |
| `session.task_intent` | yes | string | User-facing task intent |

Allowed `session.status` values:

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

Allowed `session.owner_surface` values:

- `codex_desktop`
- `claude_desktop`
- `auxiliary_cli`
- `future_frontend`
- `ci_or_bot`
- `unknown`

Lifecycle constraints:

- `accepted` requires at least one `user_decisions` item with `decision_type: "acceptance"`.
- `superseded` requires `supersession.superseded_by` or `supersession.reason`.
- `handoff_ready` requires `handoff.ready: true`.

---

## 4. Scenario Object

| Field | Required | Type | Meaning |
|---|---:|---|---|
| `scenario.chain_id` | yes | string | Scenario-chain id from the accepted scenario-chain model |
| `scenario.task_context` | yes | list string | Task contexts used for rule or document mount resolution |
| `scenario.classification_confidence` | yes | enum | How certain the classification is |
| `scenario.source_note` | no | string | Short note about how the scenario was classified |

Allowed `classification_confidence` values:

- `explicit`
- `inferred`
- `review`
- `unknown`

Recommended initial `chain_id` values:

- `project_onboarding`
- `natural_language_rule_candidate`
- `required_reference_pack`
- `work_order_start`
- `mainline_change`
- `design_or_schema_change`
- `audit_execution`
- `task_completion_acceptance`
- `cross_agent_handoff`
- `rule_evolution`
- `gate_promotion_review`
- `scenario_package_extension`

---

## 5. Changed Surface Item

```yaml
- path: ""
  change_kind: "unknown"
  surface_type: "unknown"
  declared_context: []
```

Required keys:

- `path`
- `change_kind`
- `surface_type`
- `declared_context`

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

---

## 6. Rule Result Item

```yaml
- rule_id: ""
  title: ""
  source_registry: ""
  triggered: true
  level: "warning"
  phase: "report_only"
  evidence_status: "review"
  blocking_enforced: false
  message: ""
```

Required keys:

- `rule_id`
- `title`
- `triggered`
- `level`
- `phase`
- `evidence_status`
- `blocking_enforced`

The item should reuse `jikuo.result.v0` vocabulary from `JIKUO-CORE-01`.

Allowed `evidence_status` values:

- `ok`
- `missing`
- `review`
- `not_applicable`
- `error`

Rule:

- `level` and `phase` describe rule severity and automation phase.
- `blocking_enforced` states whether this run actually blocked work.
- Report-only obligations should keep `blocking_enforced: false`.

---

## 7. Document Mount Item

```yaml
- mount_id: ""
  mount_layer: "task_session"
  role: "required_reference"
  document_ref: ""
  required_when: []
  status: "required"
  evidence_note: ""
  freshness_status: "unknown"
  missing_behavior: "report_missing"
```

Required keys:

- `mount_id`
- `mount_layer`
- `role`
- `document_ref`
- `required_when`
- `status`
- `freshness_status`
- `missing_behavior`

Allowed `mount_layer` values:

- `kernel`
- `product`
- `project`
- `scenario_package`
- `sprint`
- `work_order`
- `task_session`
- `operation`
- `handoff`

Allowed `role` values:

- `source_ref`
- `required_reference`
- `evidence_carrier`
- `output_target`
- `index_entry`
- `handoff_reference`
- `policy_reference`
- `design_context`
- `testing_context`

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

Allowed `missing_behavior` values:

- `report_missing`
- `review_required`
- `not_applicable_with_note`
- `future_gate_candidate`

Rule:

- A missing required document is reported, not silently ignored.
- Missing behavior remains report-only unless a later gate work order explicitly approves blocking behavior.

---

## 8. Evidence Snapshot Item

```yaml
- evidence_id: ""
  source_rule_id: ""
  evidence_type: "required_document"
  target_ref: ""
  status: "review"
  observed_value: ""
  note: ""
```

Required keys:

- `evidence_id`
- `evidence_type`
- `target_ref`
- `status`

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

- Evidence `ok` means the evidence carrier exists or a deterministic check passed.
- Evidence `ok` does not judge product-output quality.
- Evidence correctness may still require human governance review.

---

## 9. Verification Object

```yaml
verification:
  commands: []
  results: []
  not_run: []
  residual_risks: []
```

Command result item:

```yaml
- command: ""
  exit_code: 0
  summary: ""
  output_ref: ""
```

Required command-result keys:

- `command`
- `exit_code`
- `summary`

Rule:

- Verification results are separate from user acceptance.
- Not-run reasons should be explicit.
- Command success does not imply governance completion.

---

## 10. User Decision Item

```yaml
- decision_id: ""
  decision_type: "acceptance"
  phrase: "<exact user phrase as spoken>"
  surface: "codex_desktop"
  applies_to: []
  durability: "task_local"
  recorded_at: ""
  note: ""
```

Required keys:

- `decision_id`
- `decision_type`
- `phrase`
- `surface`
- `applies_to`
- `durability`
- `recorded_at`

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

Rule:

- `phrase` stores the user's exact natural-language phrase.
- The user is not required to use a fixed command phrase.
- High-risk durable changes require explicit scope and later approved implementation paths.

---

## 11. Completion Object

```yaml
completion:
  proposed: false
  status: "not_proposed"
  summary: ""
  governance_status: "review"
  missing_items: []
  accepted_by_user: false
```

Allowed `completion.status` values:

- `not_proposed`
- `ready_for_review`
- `accepted`
- `revision_requested`
- `deferred`
- `abandoned`

Allowed `governance_status` values:

- `ok`
- `missing`
- `review`
- `not_applicable`
- `error`

Rule:

- Completion must separate work outcome, verification outcome, governance evidence outcome, document mount outcome, and user acceptance.

---

## 12. Handoff Object

```yaml
handoff:
  ready: false
  summary_ref: ""
  required_reads: []
  pending_decisions: []
  missing_evidence: []
  next_agent_assumptions: []
```

Required keys:

- `ready`
- `required_reads`
- `pending_decisions`
- `missing_evidence`
- `next_agent_assumptions`

Rule:

- A handoff should reference project-local documents or session records when possible.
- A receiving agent should not rely only on chat memory.

---

## 13. Audit Trail Item

```yaml
- event_id: ""
  event_type: "session_created"
  actor_surface: "codex_desktop"
  timestamp: ""
  summary: ""
```

Required keys:

- `event_id`
- `event_type`
- `actor_surface`
- `timestamp`
- `summary`

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

---

## 14. Supersession Object

```yaml
supersession:
  supersedes: []
  superseded_by: ""
  reason: ""
```

Rule:

- Supersession must preserve old session history.
- A restarted, abandoned, or corrected task should not delete prior evidence.
- Supersession is not the same as acceptance.

---

## 15. Compatibility Rules

- `jikuo.task_session.v0` may embed snapshots of `jikuo.result.v0` rule-result concepts.
- Rule metadata should remain derived from the registry and registry view model.
- Document mounts should follow `JIKUO-SCENARIO-CHAIN-01` roles and layers.
- Unknown fields should be preserved by future import/export tooling when possible.
- Future frontend or CLI projections must not infer approval from absent user decisions.
- Future gate adapters must not promote report-only session evidence into blocking behavior without explicit approval.

---

## 16. Boundary

This schema is allowed to help users and agents audit process execution.

It is not allowed to:

- judge product-output quality
- replace human acceptance
- silently activate rules
- silently promote report-only checks into gates
- require fixed command phrases for ordinary user approval
- replace source documents, INS entries, accepted work orders, or registry source files
