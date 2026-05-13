# JIKUO Project Context Binding And Policy Template Portability

> **Date**: 2026-05-13
> **Status**: Draft portability contract / no runtime implementation
> **Purpose**: define how reusable policy templates bind to project-specific documents, directories, and conventions without hardcoding one project's paths.
> **Primary user surface**: Codex / Claude desktop APP chat.
> **JIKUO layer**: configurable_rule_kernel / portability_foundation
> **Depends on**: `JIKUO-PKG-00`; policy store configuration flow; configurable rule trigger policy; rule action/evidence model

---

## 1. Product Meaning

JIKUO policies should be portable.

The same rule template should be reusable across projects, machines, and users, while each project supplies its own local document paths and conventions.

This contract separates:

- policy template: reusable rule intent
- project context binding: local project roles and paths
- resolved policy: runtime view after template roles are bound to local project context

This is required before MCP implementation because an MCP tool should expose JIKUO's reusable capability, not NarrativeSystem-specific file paths.

## 2. Core Principle

If a policy can be reused outside the current project, it must not hardcode project-specific paths.

Project-specific assumptions must be explicit bindings.

Examples:

- use `role://document/latest_backlog`, not `docs/jikuo/governance/jikuo_productization_task_map.md`
- use `role://directory/work_orders`, not `docs/jikuo/work_orders/`
- use `pkg://jikuo/governance/policy_store_configuration_flow`, not a consuming project's local copy of a JIKUO contract

## 3. Project Context: `jikuo.project_context.v0`

Future file location:

```text
.jikuo/project_context.yaml
```

Minimal shape:

```yaml
schema_version: "jikuo.project_context.v0"
project:
  project_id: "..."
  project_type: "generic"
  project_root_policy: "bindings_must_resolve_inside_project_root"
document_roles:
  latest_backlog:
    path: "docs/..."
    required: true
  previous_backlog:
    path: "docs/..."
    required: true
directory_roles:
  governance_docs:
    path: "docs/..."
  work_orders:
    path: "docs/..."
naming_conventions:
  work_order_pattern: "SPRINT_*_WO-*"
compatibility:
  unknown_fields: "preserve"
```

Rules:

- project context is user-project-local state
- project context is not bundled with the JIKUO tool package
- role paths are relative to `project_root` unless a later security-reviewed external reference type is introduced
- unknown fields must be preserved by future writers
- this contract defines the shape only; it does not create `.jikuo/project_context.yaml`

## 4. Policy Template: `jikuo.policy_template.v0`

Policy templates are reusable.

Minimal shape:

```yaml
schema_version: "jikuo.policy_template.v0"
template_id: "POLICYTEMPLATE-mvp-scope-control"
namespace: "local"
version: 1
title: "MVP scope control through latest and previous backlog"
source:
  type: "local | imported | community | verified"
  ref: "..."
required_bindings:
  - binding_id: "BIND-latest-backlog"
    role_ref: "role://document/latest_backlog"
    required: true
  - binding_id: "BIND-previous-backlog"
    role_ref: "role://document/previous_backlog"
    required: true
template_policy:
  schema_version: "jikuo.configurable_rule_policy.v0"
  policy_id: "POLICY-mvp-scope-control"
  source_refs:
    - type: "policy_template"
      ref: "POLICYTEMPLATE-mvp-scope-control"
```

Rules:

- templates may reference roles, package resources, and external URLs
- templates must not reference local project paths directly unless explicitly marked non-portable
- templates are not active project policies until approved or resolved into an approved project policy path
- template source / trust fields are finalized by `JIKUO-SEC-01`

## 5. Resolved Policy: `jikuo.resolved_policy.v0`

Resolved policy is a runtime view.

Minimal shape:

```yaml
schema_version: "jikuo.resolved_policy.v0"
template_ref: "POLICYTEMPLATE-mvp-scope-control"
project_context_ref: ".jikuo/project_context.yaml"
status: "resolved | missing_binding | unsafe_binding | review_required"
resolved_bindings:
  - role_ref: "role://document/latest_backlog"
    resolved_ref: "docs/..."
    resolution_status: "ok"
  - role_ref: "role://document/previous_backlog"
    resolved_ref: "docs/..."
    resolution_status: "ok"
resolution_trace:
  project_root: "<project root>"
  rejected_refs: []
  warnings: []
```

Rules:

- resolved policy is not the canonical policy template
- resolved policy is not a durable approval record by itself
- resolved policy must expose binding status and warnings
- missing or unsafe bindings produce review status, not silent success

## 6. Reference Types

Supported reference categories:

| Ref type | Meaning | Example | Portability rule |
|---|---|---|---|
| `role://document/<role>` | project-local document role | `role://document/latest_backlog` | resolved by `.jikuo/project_context.yaml` |
| `role://directory/<role>` | project-local directory role | `role://directory/work_orders` | resolved by `.jikuo/project_context.yaml` |
| `pkg://jikuo/<path>` | bundled JIKUO package resource | `pkg://jikuo/governance/...` | resolved inside installed JIKUO package |
| `project://<relative-path>` | explicit project-local path | `project://docs/...` | must stay inside project root |
| `https://...` | external source | official spec URL | must carry provenance metadata later |

Rules:

- `role://` is preferred in reusable templates
- `pkg://` is preferred for JIKUO-owned contract docs
- `project://` is acceptable for project-approved local policies, but weaker for template portability
- absolute local filesystem paths are not portable and should be refused or marked non-portable

## 7. Path Safety

Future resolvers must:

- normalize the project root
- normalize every bound path
- reject `..` path escape outside project root
- reject absolute paths unless a later explicit external-path capability is approved
- reject or review symlink escape when detectable
- report missing bindings as `missing_binding`
- report unsafe bindings as `unsafe_binding`
- avoid reading file contents during pure resolution unless a later action explicitly requires it

## 8. Template Import And Binding Flow

Future desktop APP flow:

1. User asks to add or import a reusable rule.
2. Agent renders a template review card.
3. Card lists required bindings by role, not raw local paths.
4. User supplies or confirms local paths for missing roles.
5. Agent proposes a guarded project-context binding write.
6. Resolver checks path safety and missing roles.
7. Agent renders resolved policy status in chat.
8. User approves a policy write only after template and bindings are visible.

This contract does not implement the flow.

## 9. Relationship To Existing Policy Store

Policy store currently loads project-approved policies from `.jikuo/policies`.

CORE-20 adds a portability layer before policy activation:

- template may be reusable
- binding is project-local
- resolved policy is runtime projection
- approved policy remains the active project source after user approval

Future policy store behavior:

- active policies may include `template_ref`
- decision records may include `project_context_ref`
- status/evaluate may report `resolved_context_status`
- source refs should support `role://`, `pkg://`, and `project://`

## 10. Relationship To `CONTRACT_REFS`

Current tool code has JIKUO contract references that are hardcoded as project-local docs.

This contract classifies that as a portability smell.

Future cleanup belongs to `JIKUO-CORE-20B` after `JIKUO-PKG-01` establishes the standalone package boundary.

Preferred replacement:

- JIKUO-owned docs use `pkg://jikuo/...`
- project-owned docs use `role://...` or `project://...`
- unavailable package resources degrade with explicit warning, not silent success

## 11. Non-Goals

This contract does not implement:

- `.jikuo/project_context.yaml` creation
- resolver code
- policy template import
- template marketplace
- signature verification
- telemetry
- team identity / authorization
- frontend wizard
- package extraction
- MCP server
- gate enforcement

## 12. Acceptance Rule

This contract is acceptable if it makes the following clear:

- why reusable policies must not hardcode project paths
- what belongs in project context
- how templates reference roles
- what a resolved policy is and is not
- how path escape is refused
- why MCP must wait for this layer before implementation
