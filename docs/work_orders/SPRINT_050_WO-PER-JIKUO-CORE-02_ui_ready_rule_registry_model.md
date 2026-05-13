# SPRINT_050_WO-PER-JIKUO-CORE-02: UI-Ready Rule Registry Model

> **Date**: 2026-05-04  
> **Status**: Part 1 accepted by user; Part 2 view-model schema accepted for downstream planning  
> **Primary sprint**: Sprint 050 / contract-first hardening incubation  
> **Task type**: productization / core data model / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance productization; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`; `SPRINT_050_WO-PER-WORKTREE-05C_rule_registry_schema.md`  
> **Current slice**: Part 2 - view-model schema document; no registry data migration, frontend, CLI, adapter, gate, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user or future frontend user needs project rules to be editable through safe labels, grouped fields, validation messages, and approval boundaries instead of raw YAML knowledge.  
> **Runtime chain**: Existing rule registry -> UI-ready registry view model -> rule form / desktop card / auxiliary CLI projection -> user review -> future import/export or rule update flow.  
> **Canonical source**: accepted `rule_registry.yaml`, `rule_registry.schema.md`, `JIKUO-PRD-01`, and `JIKUO-CORE-01` result model.  
> **Bridge object**: `JikuoRuleRegistryViewModelV0`.  
> **Consumer projection**: future frontend rule console, desktop-agent rule cards, auxiliary CLI/report views, and later import/export tooling.  
> **Lifecycle**: view model v0; future editable registry changes require explicit migration, compatibility, and approval records.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 产品口径

> **中文注释**：这一片回答“规则如何从给工具读的 YAML，变成普通用户和桌面 agent 都能安全理解、编辑、确认的对象”。

The product-facing problem is that `rule_registry.yaml` is now usable by tooling, but it is not yet a user-facing rule model.

Raw YAML is not enough for `机括` because ordinary AI-primary users need:

- readable labels
- field grouping
- help text
- safe defaults
- validation messages
- review boundaries
- import/export stability
- clear edit permissions

If this is skipped:

- future frontend work may expose raw internal fields directly
- Codex / Claude desktop cards may invent different labels and explanations
- rule editing may silently alter enforcement semantics
- scenario packages may fork incompatible registry interpretations
- users may think they are editing a harmless description while changing trigger or gate behavior

Expected visible change after Part 1 acceptance:

- downstream UI / card / CLI work has a shared registry view model
- editable fields are separated from read-only or dangerous fields
- labels and help text become part of the contract
- validation errors are designed before implementation
- the current YAML registry remains unchanged

---

## 2. 技术口径

> **中文注释**：本工单只定义 view model，不迁移 YAML，不写前端，不实现编辑器。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md` acceptance record

Mainline explicitly not changed:

- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `tools/audit/check_rule_registry.py`
- checker JSON output behavior
- desktop-agent card renderer
- CLI command package
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- runtime narrative engine
- `.codex/AGENTS.md`

Canonical source:

- accepted `rule_registry.yaml`
- accepted `rule_registry.schema.md`
- accepted `JIKUO-PRD-01` process-governance product boundary
- accepted `JIKUO-CORE-01` result model and optional JSON output

Bridge object:

- conceptual `JikuoRuleRegistryViewModelV0`

Consumer projection:

- future frontend rule configuration console
- desktop-agent rule proposal / confirmation cards
- auxiliary CLI or report views
- later import/export and migration tooling

Lifecycle:

- registry is loaded
- view model is generated or interpreted
- user sees grouped fields and safe descriptions
- future edit flow creates a change proposal
- user approval creates an approval record
- later implementation writes back to registry only through an accepted import/export or migration contract

Rollback / supersession:

- because Part 1 does not implement code, rollback is doc-level supersession
- future implementation must preserve raw registry compatibility
- future schema changes must declare migration behavior and rollback plan

Propagation surfaces:

- Part 1: documentation only
- Later: schema metadata, frontend forms, desktop cards, auxiliary CLI projections

Observability:

- future tools should report which rule fields were shown, changed, validated, approved, and written back

---

## 3. 对照关系

| Product / governance goal | UI-ready registry responsibility |
|---|---|
| Let users configure rules safely | Separate editable, review-only, and read-only fields |
| Keep desktop and frontend aligned | Provide one view model vocabulary for labels, help text, and grouping |
| Prevent accidental enforcement changes | Mark enforcement and gate-related fields as approval-sensitive |
| Support future scenario packages | Keep kernel fields separate from package-specific extensions |
| Preserve checker compatibility | Do not change raw registry v0.1 in this slice |
| Support useful errors | Define validation error shape before UI implementation |
| Keep approval explicit | Rule changes become proposals before they become active writes |

---

## 4. Scope

Part 1 defines:

- registry view model goals
- UI field groups
- field editability categories
- label and help-text contract
- validation message shape
- import/export boundary
- rule-change proposal boundary
- scenario-package extension boundary
- delivery criteria and acceptance gate

Part 1 may include conceptual JSON/YAML-like examples, but it must not change actual registry files.

---

## 5. Out Of Scope

This work order does not:

- modify `rule_registry.yaml`
- modify `rule_registry.schema.md`
- implement frontend forms
- implement desktop-agent cards
- implement CLI commands
- implement registry import/export
- implement rule-change approval storage
- implement validation code
- implement migration code
- implement hooks, CI, task-stop gates, or blocking enforcement
- change checker JSON output behavior
- change narrative runtime behavior
- define product-output quality evaluation rules

---

## 6. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `tools/audit/check_rule_registry.py`
- `SPRINT_050_WO-PER-WORKTREE-05C_rule_registry_schema.md`
- `SPRINT_050_WO-PER-WORKTREE-05D_local_audit_checker_report_only.md`
- `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 7. Pre-Audit

> **中文注释**：事前审计结论：可以定义 UI-ready registry view model；不能直接改 registry 或做前端。

Task target:

- define a UI-ready registry model for future safe editing and rendering

Compliance status:

- aligned with `JIKUO-CORE-01` because structured results need rule metadata that future cards/UI can explain
- aligned with `05C` because raw registry remains the canonical rule storage contract
- aligned with desktop-agent-first because view model must serve chat cards before frontend-only assumptions
- aligned with process-governance vision because kernel fields are separated from scenario-package extensions

Required adjustments:

- keep rule changes as proposals, not direct writes
- mark enforcement changes as approval-sensitive
- avoid product-output quality evaluation fields
- stop before implementation

---

## 8. Existing Registry Is Tool-Ready, Not UI-Ready

Current registry v0.1 is good at:

- stable rule ids
- rule titles
- trigger path patterns
- evidence requirements
- enforcement level and phase
- exemptions
- target consumer
- review owner

It is not yet enough for user-facing editing because it does not define:

- field labels
- field descriptions
- form grouping
- editability
- safe defaults
- validation severity
- change-review requirements
- scenario-package extensions
- localized display strings
- import/export compatibility

---

## 9. View Model Principles

1. Raw registry remains the canonical storage contract.
2. View model is a projection, not a second source of truth.
3. User edits create proposals before writes.
4. Enforcement and gate-related fields are approval-sensitive.
5. Human-readable labels must not replace stable machine keys.
6. UI fields must reveal whether they affect trigger, evidence, enforcement, exemption, or review behavior.
7. Scenario packages may extend fields, but must not redefine kernel semantics.
8. Product-output quality judgment remains outside the kernel.

---

## 10. View Model Top-Level Shape V0

Conceptual shape:

```json
{
  "schema_version": "jikuo.registry_view.v0",
  "kind": "jikuo_rule_registry_view_model",
  "source_registry": {
    "path": "docs/scenarios/interactive_novel/governance/rule_registry.yaml",
    "schema_version": "0.1",
    "registry_id": "interactive_novel_engineering_governance"
  },
  "package": {
    "id": "engineering_governance",
    "label": "Engineering Governance",
    "kernel_version": "optional"
  },
  "field_groups": [],
  "rules": [],
  "validation": {},
  "import_export": {}
}
```

Required v0 fields:

- `schema_version`
- `kind`
- `source_registry`
- `package`
- `field_groups`
- `rules`
- `validation`
- `import_export`

---

## 11. Field Groups

Recommended groups:

| Group id | User-facing label | Purpose |
|---|---|---|
| `identity` | Rule Identity | Stable id, title, status, source refs |
| `trigger` | When This Rule Applies | Paths, contexts, and future trigger surfaces |
| `evidence` | What Evidence Is Required | Work-order fields, sections, documents, declarations, audit fields |
| `enforcement` | How Strong The Rule Is | Conceptual level and current automation phase |
| `exemptions` | When This Rule Does Not Apply | Allowed exemptions and required notes |
| `review` | Who Must Review | Owner and human acceptance requirements |
| `package_extension` | Scenario Package Fields | Domain-specific additions for future packages |

Every field group should have:

- stable `id`
- label
- description
- field list
- display order

---

## 12. Field Editability Categories

Allowed categories:

- `editable_safe`
- `editable_requires_review`
- `proposal_only`
- `read_only`
- `hidden_system`

Category meanings:

| Category | Meaning |
|---|---|
| `editable_safe` | User may edit with ordinary confirmation because the field does not change trigger or enforcement semantics |
| `editable_requires_review` | User may propose an edit, but it needs governance review before write-back |
| `proposal_only` | UI may collect a proposed change, but direct write-back is not allowed in the first editing workflow |
| `read_only` | UI displays the field but does not allow editing |
| `hidden_system` | Field should not be shown in ordinary user-facing forms |

Default category recommendations:

- `id`: `read_only`
- `title`: `editable_requires_review`
- `status`: `editable_requires_review`
- `source_refs`: `editable_requires_review`
- `materialization_types`: `proposal_only`
- `trigger.*`: `proposal_only`
- `evidence.*`: `editable_requires_review`
- `enforcement.level`: `proposal_only`
- `enforcement.phase`: `proposal_only`
- `exemptions.*`: `editable_requires_review`
- `target.*`: `read_only`
- `review.*`: `editable_requires_review`

---

## 13. Field Descriptor Shape

Conceptual shape:

```json
{
  "path": "enforcement.phase",
  "label": "Automation Phase",
  "description": "How far this rule is connected to automation.",
  "group": "enforcement",
  "value_type": "enum",
  "enum_values": [],
  "editability": "proposal_only",
  "requires_approval": true,
  "danger_level": "high",
  "default_value": "report_only",
  "validation": []
}
```

Required descriptor fields:

- `path`
- `label`
- `description`
- `group`
- `value_type`
- `editability`
- `requires_approval`
- `danger_level`

Allowed `danger_level` values:

- `low`
- `medium`
- `high`

---

## 14. Validation Message Shape

Conceptual shape:

```json
{
  "field_path": "trigger.changed_paths",
  "severity": "error",
  "code": "empty_trigger",
  "message": "At least one trigger surface is required before the rule can become active.",
  "suggested_fix": "Add a changed path, added path, or manual trigger context."
}
```

Allowed severity values:

- `info`
- `warning`
- `error`
- `review_required`

Validation messages should be:

- user-readable
- field-specific where possible
- stable enough for desktop cards and frontend views
- careful not to imply product-output quality judgment

---

## 15. Import / Export Boundary

Part 1 defines only boundaries.

Future import/export should:

- preserve stable rule ids
- preserve source refs
- preserve unknown fields when possible
- refuse direct write-back for `proposal_only` fields without approval
- report validation messages before write-back
- create a change proposal object before modifying registry files

Future import/export should not:

- silently change `enforcement.phase`
- silently promote report-only rules into gates
- drop unknown scenario-package extension fields
- merge user edits without a review/approval record

---

## 16. Rule Change Proposal Boundary

Rule edits should flow through a proposal object.

Conceptual shape:

```json
{
  "kind": "jikuo_rule_change_proposal",
  "proposal_id": "",
  "rule_id": "",
  "source_surface": "desktop_agent_card",
  "changes": [],
  "validation_messages": [],
  "approval_required": true,
  "rollback_note": ""
}
```

This work order does not implement proposal storage.

---

## 17. Scenario Package Extension Boundary

> **中文注释**：这里承接“机括不只服务工程治理”的愿景，但不在本片实现创作场景。

Kernel fields:

- identity
- trigger
- evidence
- enforcement
- exemptions
- target
- review

Scenario packages may add:

- package labels
- package-specific field descriptors
- domain-specific trigger helpers
- domain-specific evidence helper text
- domain-specific templates

Scenario packages must not:

- redefine kernel enforcement semantics
- treat product-output quality as deterministic checker truth
- bypass approval for persistent rule activation
- silently convert report-only obligations into gates

Creative-process package example:

- A future creative package may define fields such as `canon_surface`, `draft_state`, or `continuity_review_required`.
- Those fields would still flow through the same kernel concepts: trigger, evidence, approval, lifecycle, and supersession.
- This example is directional only; it is not a Sprint 050 implementation scope.

---

## 18. Testing Governance Declaration

> **中文注释**：这是核心数据契约文档，不改变 registry、checker、前端或 runtime 行为。

Required test layers for this slice:

- `unit`: N/A because no parser, serializer, or validation code is implemented.
- `integration`: N/A because no UI, CLI, adapter, checker, or registry migration is implemented.
- `workflow/orchestration`: required by contract review; editability and approval-sensitive boundaries must be clear.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against the new work order path.
- `human semantic review`: N/A for product semantics because this slice does not change product behavior or product content evaluation.
- `human governance review`: required for field editability, enforcement safety, import/export boundary, and scenario-package extension boundary.

---

## 19. Part 1 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P1-DC-01 | Define product / technical / mapping views | Sections 1, 2, and 3 exist |
| P1-DC-02 | Preserve no-implementation boundary | Sections 4 and 5 exist |
| P1-DC-03 | Define UI-ready top-level view model | Section 10 exists |
| P1-DC-04 | Define field groups | Section 11 exists |
| P1-DC-05 | Define field editability categories | Section 12 exists |
| P1-DC-06 | Define field descriptor shape | Section 13 exists |
| P1-DC-07 | Define validation message shape | Section 14 exists |
| P1-DC-08 | Define import/export boundary | Section 15 exists |
| P1-DC-09 | Define rule-change proposal boundary | Section 16 exists |
| P1-DC-10 | Define scenario-package extension boundary | Section 17 exists |
| P1-DC-11 | Declare testing-governance layers | Section 18 exists |
| P1-DC-12 | Run report-only checker smoke | Verification log records checker result |

---

## 20. Acceptance Gate For Part 1

> **中文注释**：这是 `JIKUO-CORE-02` 的第一片暂停点。你验收后，才进入 schema metadata、registry migration 或 UI 设计。

Part 1 is ready for user review when:

- registry view model is clearly a projection, not a second source of truth
- editable, proposal-only, read-only, and approval-sensitive fields are separated
- enforcement changes cannot be mistaken for safe ordinary edits
- validation messages are shaped for frontend and desktop-agent surfaces
- scenario-package extensions are allowed without expanding current implementation scope
- no registry, checker, UI, CLI, gate, or runtime code has been changed
- checker smoke has been run

Do not continue to registry metadata implementation, registry migration, frontend implementation, desktop-agent cards, CLI bridge, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 1 contract.

---

## 21. Part 1 Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md
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

## 22. Part 1 Acceptance Record

> **中文注释**：用户已确认继续，因此 Part 1 的 UI-ready registry model contract 可以作为 Part 2 schema sidecar 的上游输入。仍不代表 registry migration、前端或编辑器已被批准实现。

Acceptance:

- user accepted Part 1 by saying `请继续`
- Part 2 may define a view-model schema document

Still not accepted:

- modifying `rule_registry.yaml`
- modifying `rule_registry.schema.md`
- implementing frontend forms
- implementing desktop-agent rule cards
- implementing CLI bridge commands
- implementing import/export tooling
- implementing gate behavior
- Sprint 050 runtime hardening changes under this productization task

---

## 23. Part 2 Created Artifact

Created artifact:

- `docs/jikuo/schemas/rule_registry_view_model.schema.md`

Purpose:

- define `jikuo.registry_view.v0`
- keep the UI-ready registry model as a projection over `rule_registry.yaml`
- define field groups, descriptors, editability, validation messages, import/export boundaries, and compatibility rules

Part 2 still does not:

- create actual view-model data
- migrate the raw registry
- implement validation code
- implement write-back
- implement UI, CLI, adapter, gate, or runtime behavior

---

## 24. Part 2 Testing Governance Declaration

Required test layers for this slice:

- `unit`: N/A because no parser, serializer, or validation code is implemented.
- `integration`: N/A because no registry migration, UI, CLI, adapter, checker, or runtime integration is implemented.
- `workflow/orchestration`: required by schema review; sidecar schema must preserve proposal-before-write and approval-sensitive boundaries.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against this work order after creating the schema document.
- `human semantic review`: N/A for product semantics because this slice does not change product behavior or product content evaluation.
- `human governance review`: required for sidecar schema shape, editability defaults, import/export contract, and scenario-package compatibility.

---

## 25. Part 2 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P2-DC-01 | Record Part 1 acceptance | Section 22 exists |
| P2-DC-02 | Create view-model schema document | `rule_registry_view_model.schema.md` exists |
| P2-DC-03 | Define top-level shape | Schema document Section 2 exists |
| P2-DC-04 | Define package and field-group shapes | Schema document Sections 4 and 5 exist |
| P2-DC-05 | Define field descriptor and default editability recommendations | Schema document Sections 6 and 7 exist |
| P2-DC-06 | Define validation message and import/export contracts | Schema document Sections 8 and 9 exist |
| P2-DC-07 | Preserve no-implementation boundary | No registry, checker, UI, CLI, gate, or runtime code is changed |
| P2-DC-08 | Run report-only checker smoke | Verification log records checker result |

---

## 26. Acceptance Gate For Part 2

> **中文注释**：这是 Part 2 的暂停点。你验收后，才考虑是否生成实际 sidecar YAML、实现 registry view builder，或进入 CORE-03。

Part 2 is ready for user review when:

- the schema document exists
- the schema makes raw registry the canonical source
- editability defaults protect enforcement and trigger fields
- import/export remains proposal-first and approval-sensitive
- scenario-package extension rules are clear
- no registry data, checker code, frontend, CLI, gate, or runtime behavior is changed
- checker smoke has been run

Do not continue to actual sidecar data, registry view builder implementation, registry migration, frontend, CLI bridge, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 2 schema.

---

## 27. Part 2 Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --changed docs/jikuo/schemas/rule_registry_view_model.schema.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md
```

Result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, and `R-004`
- required deterministic work-order fields / sections reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved

---

## 28. Part 2 Acceptance Record

> **中文注释**：用户要求继续开发任务后，本文件将 Part 2 记录为已可作为后续规划输入。该验收不代表批准 sidecar 数据生成、registry migration、前端、CLI、gate 或 runtime 实现。

Acceptance:

- Part 2 view-model schema may be used as upstream context for later JIKUO planning.
- The next accepted planning slice is `JIKUO-FLOW-01`, which clarifies how a real engineering-governance user uses JIKUO before `CORE-03` task-session modeling.

Still not accepted:

- creating actual registry view-model data
- modifying `rule_registry.yaml`
- modifying `rule_registry.schema.md`
- implementing registry view builder code
- implementing desktop-agent cards
- implementing CLI bridge commands
- implementing frontend forms
- implementing gate behavior
- changing Sprint 050 runtime narrative engine behavior
