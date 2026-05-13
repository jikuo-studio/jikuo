# Jikuo Rule Registry View Model Schema

> **Schema version**: `jikuo.registry_view.v0`  
> **Source registry schema**: `rule_registry.schema.md` / registry schema `0.1`  
> **Status**: Draft, UI-ready projection contract  
> **Source work order**: `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`  
> **Current application track**: engineering-governance scenario package  

---

## 1. Purpose

> **中文注释**：这是未来前端、桌面卡片、辅助 CLI 共同消费的 registry view-model schema。它不是新的 rule registry source of truth。

The rule registry view model describes how raw registry rules should be rendered, explained, validated, and proposed for editing across `机括` surfaces.

It is a projection contract over `rule_registry.yaml`.

It does not:

- replace `rule_registry.yaml`
- change checker behavior
- permit direct write-back
- promote report-only rules into gates
- judge product-output quality

---

## 2. Top-Level Shape

```yaml
schema_version: "jikuo.registry_view.v0"
kind: "jikuo_rule_registry_view_model"
source_registry:
  path: "docs/scenarios/interactive_novel/governance/rule_registry.yaml"
  schema_version: "0.1"
  registry_id: "interactive_novel_engineering_governance"
package:
  id: "engineering_governance"
  label: "Engineering Governance"
  description: ""
field_groups: []
field_descriptors: []
validation_catalog: []
import_export:
  preserves_unknown_fields: true
  direct_write_allowed: false
  proposal_required: true
```

Required top-level keys:

- `schema_version`
- `kind`
- `source_registry`
- `package`
- `field_groups`
- `field_descriptors`
- `validation_catalog`
- `import_export`

---

## 3. Source Registry Object

| Field | Required | Type | Meaning |
|---|---:|---|---|
| `source_registry.path` | yes | string | Repository-relative path to the canonical registry |
| `source_registry.schema_version` | yes | string | Raw registry schema version |
| `source_registry.registry_id` | yes | string | Stable registry id |

The view model must not be treated as canonical when it conflicts with the source registry.

---

## 4. Package Object

| Field | Required | Type | Meaning |
|---|---:|---|---|
| `package.id` | yes | string | Scenario package id |
| `package.label` | yes | string | User-facing package name |
| `package.description` | yes | string | Short package explanation |

Current package:

- `engineering_governance`

Future packages may include:

- `creative_process_governance`
- `research_process_governance`
- `knowledge_production_governance`

Future packages may extend descriptors, but they must not redefine kernel enforcement semantics.

---

## 5. Field Group Shape

```yaml
- id: "enforcement"
  label: "Enforcement"
  description: "How strong the rule is and how far automation has been connected."
  order: 40
  fields:
    - "enforcement.level"
    - "enforcement.phase"
```

Required field-group keys:

- `id`
- `label`
- `description`
- `order`
- `fields`

Recommended group ids:

- `identity`
- `trigger`
- `evidence`
- `enforcement`
- `exemptions`
- `review`
- `package_extension`

---

## 6. Field Descriptor Shape

```yaml
- path: "enforcement.phase"
  label: "Automation Phase"
  description: "How far this rule is connected to automation."
  group: "enforcement"
  value_type: "enum"
  enum_values:
    - value: "report_only"
      label: "Report Only"
      description: "Report obligations without blocking work."
  editability: "proposal_only"
  requires_approval: true
  danger_level: "high"
  default_value: "report_only"
  validation_codes:
    - "phase_promotion_requires_approval"
```

Required descriptor keys:

- `path`
- `label`
- `description`
- `group`
- `value_type`
- `editability`
- `requires_approval`
- `danger_level`

Allowed `value_type` values:

- `string`
- `boolean`
- `enum`
- `list_string`
- `list_enum`
- `path_glob_list`
- `object`

Allowed `editability` values:

- `editable_safe`
- `editable_requires_review`
- `proposal_only`
- `read_only`
- `hidden_system`

Allowed `danger_level` values:

- `low`
- `medium`
- `high`

---

## 7. Default Descriptor Recommendations

| Field path | Group | Editability | Danger |
|---|---|---|---|
| `id` | `identity` | `read_only` | `high` |
| `title` | `identity` | `editable_requires_review` | `medium` |
| `status` | `identity` | `editable_requires_review` | `medium` |
| `source_refs` | `identity` | `editable_requires_review` | `medium` |
| `materialization_types` | `identity` | `proposal_only` | `high` |
| `trigger.mode` | `trigger` | `proposal_only` | `high` |
| `trigger.changed_paths` | `trigger` | `proposal_only` | `high` |
| `trigger.added_paths` | `trigger` | `proposal_only` | `high` |
| `trigger.required_context` | `trigger` | `editable_requires_review` | `medium` |
| `evidence.work_order_fields` | `evidence` | `editable_requires_review` | `medium` |
| `evidence.required_sections` | `evidence` | `editable_requires_review` | `medium` |
| `evidence.required_documents` | `evidence` | `editable_requires_review` | `medium` |
| `evidence.declarations` | `evidence` | `editable_requires_review` | `medium` |
| `evidence.audit_bundle_fields` | `evidence` | `proposal_only` | `high` |
| `enforcement.level` | `enforcement` | `proposal_only` | `high` |
| `enforcement.phase` | `enforcement` | `proposal_only` | `high` |
| `enforcement.report_message` | `enforcement` | `editable_requires_review` | `medium` |
| `exemptions.allowed_when` | `exemptions` | `editable_requires_review` | `medium` |
| `exemptions.required_note` | `exemptions` | `editable_requires_review` | `medium` |
| `target.consumer` | `review` | `read_only` | `high` |
| `target.later_work_order` | `review` | `read_only` | `medium` |
| `review.owner` | `review` | `editable_requires_review` | `medium` |
| `review.requires_human_acceptance` | `review` | `editable_requires_review` | `medium` |

---

## 8. Validation Message Shape

```yaml
- code: "phase_promotion_requires_approval"
  severity: "review_required"
  field_path: "enforcement.phase"
  message: "Changing automation phase requires explicit approval and rollback planning."
  suggested_fix: "Create a rule-change proposal instead of direct write-back."
```

Required validation message keys:

- `code`
- `severity`
- `field_path`
- `message`
- `suggested_fix`

Allowed severity values:

- `info`
- `warning`
- `error`
- `review_required`

---

## 9. Import / Export Contract

Import/export tools must:

- read the canonical registry first
- preserve unknown raw registry fields when possible
- refuse direct write-back for `proposal_only` fields
- surface validation messages before write-back
- create a rule-change proposal before modifying registry files
- preserve `source_refs`
- preserve rule ids

Import/export tools must not:

- silently change `enforcement.phase`
- silently change `enforcement.level`
- drop unknown package extension fields
- infer approval from user intent text
- treat view-model labels as canonical field names

---

## 10. Change Proposal Link

The view model should produce proposals shaped like:

```yaml
kind: "jikuo_rule_change_proposal"
proposal_id: ""
rule_id: ""
source_surface: "desktop_agent_card"
changes: []
validation_messages: []
approval_required: true
rollback_note: ""
```

Proposal storage is out of scope for this schema.

---

## 11. Compatibility Rules

- `jikuo.registry_view.v0` targets raw registry schema `0.1`.
- Unknown fields in raw registry should be preserved.
- New view-model descriptor fields require schema documentation update.
- New scenario packages require package-specific descriptor sections or sidecars.
- Gate-related fields remain proposal-only until a later approved gate work order.

---

## 12. Boundary

This schema is allowed to help users understand and propose changes to process-governance rules.

It is not allowed to:

- make product-output quality judgments
- activate rules without approval
- promote report-only checks into gates
- replace source documents, INS entries, or accepted work orders
- bypass human acceptance where approval is required
