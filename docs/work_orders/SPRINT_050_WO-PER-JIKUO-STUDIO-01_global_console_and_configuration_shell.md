# SPRINT_050_WO-PER-JIKUO-STUDIO-01: Global Console And Configuration Shell

> **Status**: `JIKUO-STUDIO-01A` global status read model and `JIKUO-STUDIO-01B` panel/action registries implemented as no-write Python/CLI backend surfaces. Local frontend and guarded Studio actions remain planned.
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

Implementation status (2026-05-31): implemented in
`src/jikuo/studio/global_status.py`, exposed through
`python -B -m jikuo studio status --format json|markdown`, and covered by
`tests/studio_global_status_tests.py`.

Acceptance:

- returns runtime, activation, configuration, integration, policy-management,
  registry, diagnostics, pending-decision, and available-action summaries;
- does not write `.jikuo/`, policy files, starter manifests, or runtime cards;
- includes source refs and read-model limitations;
- has CLI and tests.

### `JIKUO-STUDIO-01B`: Panel And Action Registry

Implement panel and action descriptors that the future UI can render.

Implementation status (2026-06-01): implemented in
`src/jikuo/studio/panels.py` and `src/jikuo/studio/actions.py`, consumed by
`src/jikuo/studio/global_status.py`, and covered by
`tests/studio_panel_action_registry_tests.py`.

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

## 9. `JIKUO-STUDIO-01A` Concrete Landing Plan

`JIKUO-STUDIO-01A` is the first implementation slice because it gives
the future frontend one stable backend object before any UI framework is chosen.

### 9.1 Implementation Boundary

Implemented as a read-only Python module and CLI surface only:

```text
src/jikuo/studio/
  __init__.py
  global_status.py

tests/
  studio_global_status_tests.py
```

Optional later, but not required in `01A`:

```text
src/jikuo/integrations/mcp/...
```

Do not create `src/jikuo/integrations/studio_web/` in `01A`. The frontend waits
until the read model shape is accepted.

### 9.2 Public Contract

Implemented read model builder:

```python
build_global_status(project_root: Path | None = None) -> dict
```

Implemented CLI route:

```text
python -B -m jikuo studio status --project-root <path> --format json|markdown
```

The CLI may be wired through `src/jikuo/cli.py` if the existing command surface
supports it cleanly. If the root CLI would become noisy, use
`python -B -m jikuo.studio.global_status status ...` for `01A` and defer root
CLI polish.

No MCP tool is included in `01A`; MCP exposure can be a follow-up once the JSON
contract has tests.

### 9.3 Data Sources

Use existing backend APIs where available. Do not reimplement their business
rules in Studio code.

| Summary field | Preferred source |
|---|---|
| `runtime_summary` | `runtime_visibility` helpers or `.jikuo/runtime/state_summary.json` with defensive missing-file handling |
| `activation_summary` | `activation_settings.build_status_report` |
| `configuration_summary` | `configuration_review.build_configuration_review` |
| `policy_management_summary` | `policy_management_status.build_status_report` or current equivalent |
| `registry_summary` | `docs/registry/work_orders.yaml`, `capabilities.yaml`, `mount_sets.yaml`, `registry_index.yaml` |
| `integration_health` | existing proof / status records where structured; otherwise return explicit `unknown` records |
| `diagnostics` | aggregate warnings and degraded statuses from the above sources |
| `pending_user_decisions` | activation required decisions, configuration review decisions, and policy-management follow-ups |
| `available_actions` | read-only descriptors for known plan/apply families, not executable UI actions yet |

If a source is missing or unparseable, return a degraded section and a diagnostic
instead of raising for ordinary user-facing status calls.

### 9.4 Output Shape

The first schema should stay compact and UI-friendly:

```yaml
schema: "jikuo.studio.global_status.v0"
status: "available|degraded|unavailable"
project_root: "<path>"
generated_at_utc: "<timestamp>"
summaries:
  runtime: {}
  activation: {}
  configuration: {}
  policy_management: {}
  registry: {}
  integrations: {}
pending_user_decisions: []
available_actions: []
diagnostics: []
card_links: {}
source_refs: []
read_model_limitations: []
privacy:
  raw_prompt_stored: false
  transcript_stored: false
writes_performed: false
non_effects: []
```

Keep large source payloads out of the default response. Each summary should
provide counts, status labels, important refs, and next actions. The future UI
can drill into domain-specific read models when needed.

### 9.5 Status Rules

Use predictable aggregate status:

- `available`: required local sources loaded and no critical source is missing;
- `degraded`: at least one optional source is missing, stale, or unparseable,
  but the overall console can still render;
- `unavailable`: project root cannot be resolved or core project context cannot
  be read.

Diagnostics should include:

- missing activation settings;
- unreviewed activation defaults;
- missing runtime state;
- stale or missing MCP / hook proof records when detectable;
- unavailable Sampling or semantic-provider proof;
- registry parse errors;
- permission warnings that affect visibility.

### 9.6 Available Actions In `01A`

`01A` should return action descriptors as previews only. They are not executable
by the Studio layer yet.

Initial descriptors:

- `studio.configuration.review`;
- `studio.activation_settings.plan_update`;
- `studio.policy_management.status`;
- `studio.policy_distribution.review`;
- `studio.policy_template.plan_publication`;
- `studio.policy_template.activate`;
- `studio.starter_manifest.plan_publication`;
- `studio.runtime.open_latest_card`.

Each descriptor should include:

- `action_id`;
- `domain`;
- `title`;
- `write_mode`;
- `plan_surface`;
- `apply_surface` when applicable;
- `write_effect`;
- `approval_required`;
- `source_ref`;
- `status`.

The frontend can render these before action execution exists.

### 9.7 Tests

Add focused tests before any UI work:

- missing / temporary project root returns `unavailable` or `degraded` without
  writing files;
- normal JIKUO repo returns schema `jikuo.studio.global_status.v0` and
  `writes_performed=false`;
- activation summary includes missing or reviewed activation status;
- policy management summary includes active policy and template counts;
- diagnostics collect at least one known degraded condition when activation
  settings are missing;
- available actions include the initial read-only descriptors;
- no raw prompt or transcript fields appear in serialized output;
- CLI `--format json` returns parseable JSON;
- CLI `--format markdown` renders a short human summary.

### 9.8 Acceptance For `01A`

`01A` is complete only when:

- the read model can be consumed by tests, CLI, and future UI code without
  scraping Markdown cards;
- no durable write occurs during status generation;
- source refs and read-model limitations are visible;
- degraded state is explicit rather than silently ignored;
- full test discovery remains green.

---

## 10. Non-Goals

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

## 11. Dependency Notes

The global console depends on the current JIKUO backend becoming more readable,
not more autonomous.

Current reusable foundations:

- runtime visibility cards and observed lifecycle projection;
- activation settings and configuration review;
- policy-management status read model;
- guarded policy/template/starter operations;
- MCP and hook proof records;
- document registry shards and mount sets.

Known gaps after `01A`/`01B` implementation:

- panel and action registries exist as read-only descriptors, but they do not
  execute actions or host a frontend yet;
- action descriptors are embedded in `jikuo.studio.global_status.v0` for
  frontend convenience and also available through `jikuo.studio.action_registry.v0`;
- integration health is distributed across proof docs, runtime cards, and MCP
  tool inventory, so `01A` reports conservative proof status rather than strict
  GUI truth;
- DATA-01 event ledger is not implemented, so analytics must remain limited to
  existing runtime projections.

---

## 12. Business Acceptance

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
