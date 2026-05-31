# SPRINT_050_WO-PER-JIKUO-STUDIO-01: Global Console And Configuration Shell

> **Status**: Planned; design anchor accepted for a JIKUO-wide thin frontend. No frontend or backend implementation is included by this document.
> **Date**: 2026-05-31
> **JIKUO layer**: product surface / view-model projection / guarded configuration control.
> **Business meaning**: Users should not need to reconstruct JIKUO's global state from chat alone. A thin JIKUO console should make activation, runtime, policy, template, integration, diagnostics, and guarded configuration status visible in one place while preserving the existing kernel and guarded-write boundaries.

---

## 1. Authority

This work order promotes
`docs/insights/INSIGHT-2026-05-16-studio-dashboard-frontend-architecture.md`
from an insight into an implementation planning anchor.

It must be mounted with:

- `.jikuo/project_context.yaml`;
- `docs/governance/jikuo_execution_mounts.md`;
- `docs/registry/*.yaml`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01_policy_management_mvp.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INTG-03_strict_mounted_harness_adapter_contract.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DATA-01_structured_execution_event_ledger_and_analytics_contract.md`;
- `docs/insights/INSIGHT-2026-05-16-studio-dashboard-frontend-architecture.md`.

---

## 2. Scope Correction

The target is not a policy-management frontend.

The target is a JIKUO global console:

- a single place to inspect whether JIKUO is configured, mounted, and healthy;
- a visual view over the latest runtime cards and observed lifecycle;
- a configuration surface for activation settings and future client adapters;
- a policy and template surface as one domain among several;
- an operations surface that can request no-write plans and guarded apply calls;
- a diagnostics surface for missing semantic intent, stale MCP tools, hook
  failures, permission warnings, and unreviewed settings.

Policy management remains one panel in the console. It must not define the whole
frontend architecture.

---

## 3. Product Principle

Build the frontend as a projection and guarded control shell over stable JIKUO
contracts, not as a new governance kernel.

The frontend may own:

- layout;
- navigation;
- filtering and grouping;
- panel registration;
- action affordance presentation;
- visual comparison of existing canonical records;
- local form state before a no-write plan is generated.

The frontend must not own:

- policy trigger semantics;
- policy evaluator behavior;
- evidence matching semantics;
- approval boundaries;
- durable write rules;
- privacy classification;
- MCP tool behavior;
- direct `.jikuo/` writes.

If the frontend and kernel disagree, project-local canonical state wins.

---

## 4. Minimum Architecture

Use this shape:

```text
JIKUO kernel, local files, CLI, MCP, guarded apply tools
        |
        v
stable view models + action registry
        |
        v
thin local console
```

The first stable contract is the backend projection and action model, not the
renderer framework.

Recommended package layout when implementation starts:

```text
src/jikuo/studio/
  global_status.py      # canonical state -> jikuo.studio.global_status.v0
  panels.py             # panel registry and visibility metadata
  actions.py            # no-write / guarded action descriptors
  view_models.py        # shared projection helpers

src/jikuo/integrations/studio_web/
  server.py             # local HTTP surface over read models and action plans
  static_or_app/        # thin frontend shell
```

The exact renderer is deferred. A simple local HTTP surface and static or small
React/Vite shell is preferred before considering Electron, Tauri, or hosted UI.

---

## 5. Global View Model

`JIKUO-STUDIO-01A` should implement a no-write read model:
`jikuo.studio.global_status.v0`.

It should aggregate existing sources instead of re-parsing business logic in the
frontend:

| Area | Existing source | UI purpose |
|---|---|---|
| Runtime | `.jikuo/runtime/last_card.md`, `state_summary.json`, history cards, `jikuo show` | Show latest card, observed lifecycle, triggered policy counts, and missing evidence. |
| Activation | `activation_settings` status / plan / apply | Show trigger mode, enforcement level, strict-mounted posture, and required user decisions. |
| Configuration review | `configuration_review` | Show first-use and ongoing setup gaps. |
| Policy management | `policy_management_status` | Show active policies, package templates, starter packs, distribution state, and available follow-ups. |
| Integrations | MCP tool inventory, hook proof notes, sampling probe status, proof playbook results | Show whether Codex / Claude / Cursor / VS Code surfaces are actually connected. |
| Registry | `docs/registry/*.yaml`, project context, mount sets | Show known work orders, capability status, and required mounts without using legacy task-map authority. |
| Data / analytics | DATA-01 schema and future runtime event ledger | Reserve a dashboard-ready slot without pretending the event ledger exists today. |
| Diagnostics | runtime warnings, permission warnings, stale tool counts, missing semantic intent | Make system health visible outside chat. |

Minimum fields:

```yaml
schema: "jikuo.studio.global_status.v0"
project_root: "<local path>"
generated_at_utc: "<timestamp>"
runtime_summary: {}
configuration_summary: {}
activation_summary: {}
integration_health: {}
policy_management_summary: {}
registry_summary: {}
diagnostics: []
pending_user_decisions: []
available_actions: []
card_links: {}
privacy:
  raw_prompt_stored: false
  transcript_stored: false
non_effects:
  - "does_not_write_project_state"
  - "does_not_mutate_policies"
  - "does_not_update_starter_manifests"
  - "does_not_activate_user_project_policies"
```

---

## 6. Initial Panels

`JIKUO-STUDIO-01B` should define panel registry metadata before UI screens are
implemented.

Initial panels:

| Panel | Purpose | First data provider |
|---|---|---|
| Overview | One-screen project health and pending decisions. | `jikuo.studio.global_status.v0` |
| Runtime | Latest card, state summary, history, observed lifecycle. | runtime visibility read model |
| Configuration | Activation settings and configuration review. | activation / configuration status |
| Integrations | MCP tools, hook status, client proof status, semantic provider status. | integration health projection |
| Policies And Templates | Active policies, package templates, starter packs, distribution state. | policy-management status |
| Actions | Available no-write plans and guarded apply operations. | action registry |
| Diagnostics | Warnings and likely repair paths. | global diagnostics projection |

Later panels:

- task sessions;
- evidence timeline;
- policy evolution;
- rollback;
- support bundle / analytics;
- team or hosted state.

---

## 7. Action Registry

The frontend should never write canonical state directly. It should render
registered actions and call the existing no-write / guarded boundaries.

An action descriptor should include:

```yaml
action_id: "studio.activation_settings.update"
domain: "configuration"
title: "Update activation settings"
write_mode: "guarded"
plan_surface: "jikuo.plan_activation_settings_update"
apply_surface: "jikuo.apply_activation_settings_update"
write_effect: "writes .jikuo/activation_settings.yaml"
required_approval:
  confirm_flag: true
  approval_phrase: true
privacy_classification: "local_only"
card_output_contract: "must return card link and state refresh hint"
preconditions: []
non_effects: []
rollback_posture: "manual follow-up plan"
```

Initial action families:

- configuration review and activation settings update;
- policy template import planning and activation;
- policy distribution review and package-template publication;
- starter manifest publication;
- task-session evidence append;
- runtime refresh / diagnostics read.

Every guarded action must preserve the existing sequence:

1. user edits form state;
2. backend returns no-write plan;
3. UI displays write effect, non-effects, risks, and card links;
4. user confirms approval phrase;
5. backend calls guarded apply;
6. UI refreshes global status and shows result card.

---

## 8. Implementation Slices

### `JIKUO-STUDIO-01A`: Global Status Read Model

Implement `jikuo.studio.global_status.v0` as a no-write backend read model.

Acceptance:

- returns runtime, activation, configuration, integration, policy-management,
  registry, diagnostics, pending-decision, and available-action summaries;
- does not write `.jikuo/`, policy files, starter manifests, or runtime cards;
- includes source refs and read-model limitations;
- has CLI and tests.

### `JIKUO-STUDIO-01B`: Panel And Action Registry

Implement panel and action descriptors that the future UI can render.

Acceptance:

- each panel has a provider ref, empty-state text, privacy level, and action refs;
- each action has plan/apply surfaces, write effects, approval requirements, and
  non-effects;
- descriptors are usable by MCP, CLI, and local web surfaces.

### `JIKUO-STUDIO-01C`: Local Read-Only Console

Implement the smallest local UI over the global status read model.

Acceptance:

- shows overview, runtime, configuration, integrations, policy/template summary,
  actions, and diagnostics;
- no guarded writes yet;
- does not parse Markdown cards as business data;
- does not require a specific AI GUI client.

### `JIKUO-STUDIO-01D`: Guarded Configuration Actions

Enable selected guarded actions in the console after action registry acceptance.

Acceptance:

- action plan is visible before apply;
- approval phrase is required for writes;
- result card links are displayed after apply;
- failures are shown as structured diagnostics.

---

## 9. Non-Goals

This work order does not approve:

- implementing a frontend before the global read model exists;
- direct frontend writes to `.jikuo/`;
- duplicating policy evaluation in JavaScript;
- replacing MCP / CLI / public adapter APIs;
- making Studio the only way to use JIKUO;
- hosted telemetry or team state;
- Electron / Tauri packaging;
- a policy-only frontend that ignores activation, integrations, runtime, and
  diagnostics.

---

## 10. Dependency Notes

The global console depends on the current JIKUO backend becoming more readable,
not more autonomous.

Current reusable foundations:

- runtime visibility cards and observed lifecycle projection;
- activation settings and configuration review;
- policy-management status read model;
- guarded policy/template/starter operations;
- MCP and hook proof records;
- document registry shards and mount sets.

Known gaps before implementation:

- no `jikuo.studio.global_status.v0` exists yet;
- no panel registry exists yet;
- no action registry exists yet;
- integration health is distributed across proof docs, runtime cards, and MCP
  tool inventory;
- DATA-01 event ledger is not implemented, so analytics must remain limited to
  existing runtime projections.

---

## 11. Business Acceptance

This task is valuable when a user can answer, from one local surface:

- Is JIKUO configured and mounted?
- What did JIKUO last see and report?
- Which policies/templates/starter packs exist and what can be done next?
- Which client integrations are proven, degraded, or missing?
- Which guarded actions are available, what would they write, and what approval
  is required?
- What warnings or missing decisions need attention?

The first implementation should stop at read-only visibility unless the action
registry has already made write effects reviewable and guarded.
