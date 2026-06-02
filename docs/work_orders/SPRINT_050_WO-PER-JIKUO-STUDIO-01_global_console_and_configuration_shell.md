# SPRINT_050_WO-PER-JIKUO-STUDIO-01: Global Console And Configuration Shell

> **Status**: `JIKUO-STUDIO-01A` global status read model, `JIKUO-STUDIO-01B` panel/action registries, `JIKUO-STUDIO-01C` local read-only console, `JIKUO-STUDIO-01D1` document-mount read model, `JIKUO-STUDIO-01D2` visible document-mount frontend section, and `JIKUO-STUDIO-01D3` configuration vocabulary mapping implemented as no-write Python/CLI/backend surfaces. `JIKUO-STUDIO-01D4` records the detailed Document Rules plan/apply design contract; `JIKUO-STUDIO-01D5` implements the first Document Rules no-write plan backend; `JIKUO-STUDIO-01D6` connects that plan to the local Studio page as a no-write preview; `JIKUO-STUDIO-01D7` separates editable configuration from governance guidance in the read model and UI; `JIKUO-STUDIO-01D8` implements minimal guarded apply for `.jikuo/project_context.yaml` Document Rules changes.
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
| Document Rules | Main documents, active rule sets, task context bundles, and legacy projection warnings. | project context plus document registry |
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
- document-mount and main-document review / update planning;
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

### 7.1 Customer Configuration Action Inventory

The global console is not only a status dashboard. It must let a customer see
which project-level choices exist, why they matter, and which guarded boundary
will apply before anything is changed.

Configuration actions should be grouped by customer goal, not by current
module layout:

| Domain | Customer question | Current source of truth | First Studio action posture |
|---|---|---|---|
| Project binding | Which local project is JIKUO governing? | `.jikuo/project_context.yaml`, `project_state` | read-only review first; guarded initialization remains separate |
| Activation | When should JIKUO be invoked, and how strict is it? | `.jikuo/activation_settings.yaml` | no-write plan plus guarded apply |
| Client setup | Which AI clients receive JIKUO instructions or hooks? | instruction files, MCP config examples, hook proof docs | no-write install preview plus guarded instruction sync |
| Document rules | Which documents should JIKUO use as context, completion checks, and governance references? | `.jikuo/project_context.yaml`, `docs/registry/mount_sets.yaml`, work-order `required_mount_sets` | design first; future no-write plan plus guarded apply |
| Main documents | Which documents must be checked before completion? | `.jikuo/project_context.yaml` `main_document_mounts`, execution mounts | design first; future no-write plan plus guarded apply |
| Policy management | Which policies are active, reusable, or distributable? | `.jikuo/policies/manifest.yaml`, package templates, starter manifests | existing read model, no-write plan, and guarded apply |
| Runtime visibility | What happened recently, and where are the cards? | `.jikuo/runtime/*` | read-only links and refresh diagnostics |
| Integration proof | Are MCP, hooks, Sampling, and semantic provider paths really available? | MCP inventory, hook proof notes, runtime cards | read-only proof view first; guarded install later |
| Diagnostics | What is degraded, missing, stale, or blocked? | aggregated read models | read-only repair suggestions, then explicit plan/apply |

Business meaning:

- customers should not need to know which YAML file owns a setting before they
  can understand or change it;
- AI assistants should not invent configuration actions from chat memory;
- guarded configuration actions must show source of truth, write effect,
  non-effect, and result-card links before apply;
- Studio remains a thin shell over canonical JIKUO state, not a second
  configuration kernel.

### 7.2 Document Mount Configuration Domain

Document mounting is a first-class customer configuration need.

Examples:

- selecting which product or project documents count as `main documents`;
- deciding which documents are required before task completion;
- choosing reusable mount sets for policy, registry, lifecycle, Studio, or
  integration work;
- attaching work orders to required context bundles and originating evidence;
- marking a document as source of truth, projection, legacy projection, or
  orientation-only.

The current source layers are:

| Layer | Current owner | Customer-facing meaning |
|---|---|---|
| L0 registry | `docs/registry/*.yaml` | available structured documents, mount sets, capabilities, and work-order anchors |
| L1 project context | `.jikuo/project_context.yaml` | project-local active document roles and main-document completion scope |
| L2 mount recipes | `docs/governance/jikuo_execution_mounts.md` plus `mount_sets.yaml` | task-context bundles and operating guidance |
| L3 projections | `README.md`, `docs/README.md`, legacy task map | readable orientation, not default authority for new configuration |

Future document-mount actions should therefore follow this path:

```text
read current document registry and project context
-> no-write document-mount plan
-> show added/removed/role-changed document refs and completion-check impact
-> guarded apply to project-local configuration only
-> refresh Studio global status and runtime card links
```

Initial action candidates:

| Action id | Purpose | Write boundary |
|---|---|---|
| `studio.document_mounts.review` | Show current document roles, mount sets, main-document scope, and legacy projections. | no-write |
| `studio.document_mounts.plan_update` | Preview changes to main documents, active mount sets, or task-context bundles. | no-write-plan |
| `studio.document_mounts.apply_update` | Apply an explicitly approved project-local document-mount update. | guarded write |

Non-goals for the first document-mount slice:

- do not regenerate the legacy task map;
- do not change policy evaluator behavior;
- do not create a heavy knowledge graph or hand-maintained reverse edges;
- do not silently rewrite package registry shards when the user only changes a
  project-local configuration;
- do not let the frontend write `.jikuo/project_context.yaml` directly.

### 7.3 User Configuration Language Contract

Studio must not expose internal architecture names as the primary user-facing
configuration language.

User-facing labels are stable product concepts. Internal refs are implementation
bindings that may move as the architecture changes. The read model therefore
publishes a vocabulary mapping:

```yaml
configuration_language_schema: "jikuo.studio.configuration_language.v0"
configuration_terms:
  - term_id: "document_rules"
    user_label: "Document rules"
    internal_refs:
      - ".jikuo/project_context.yaml document_roles"
      - ".jikuo/project_context.yaml main_document_mounts"
      - "docs/registry/mount_sets.yaml"
```

Frontend rules:

- render `user_label` and `user_description` by default;
- use `term_id` as the stable binding key;
- show `internal_refs` only as supporting source/debug information;
- never hard-code phrases such as `mount authority` or `write boundary` as the
  primary customer concept;
- if internal storage moves, update `internal_refs` while keeping the user term
  stable unless the product meaning truly changes.

### 7.4 Document Rules Plan / Apply Contract

`JIKUO-STUDIO-01D4` defines the future editable Document Rules flow before code
implementation. It is a design contract, not an implemented write surface.

Business goal:

- let customers configure the documents JIKUO should use as context,
  completion checks, and governance references;
- keep the user-facing terms stable even when the internal storage changes;
- keep every write behind a no-write plan and guarded apply boundary;
- prevent the local Studio UI from becoming a second configuration kernel.

#### 7.4.1 User Operations

The first editable Document Rules UI should support these user-level actions:

| User operation | Meaning | First implementation posture |
|---|---|---|
| Add context document | Add a document JIKUO should consider when orienting to the project. | plan-only then guarded apply |
| Remove context document | Stop treating a document as active context. | plan-only then guarded apply |
| Add completion check | Require JIKUO to inspect a document before claiming slice completion. | plan-only then guarded apply |
| Remove completion check | Stop requiring a document in completion-review checks. | plan-only then guarded apply |
| Add governance reference | Mark a document as explaining rules, policy, registry, or execution boundaries. | plan-only then guarded apply |
| Change document label / note | Update the user-facing reason a document is included. | plan-only then guarded apply |

The UI should group operations by user goal, not by YAML field name. Internal
labels such as `document_roles`, `main_document_mounts`, and `mount_sets` remain
support/debug details.

#### 7.4.2 Internal Mapping

The initial implementation should write only project-local configuration:

| User term | Current internal target | Notes |
|---|---|---|
| Context documents | `.jikuo/project_context.yaml document_roles` | Add or remove role bindings. |
| Completion checks | `.jikuo/project_context.yaml main_document_mounts.checked_before_slice_completion` | Preserve `update_required_when` text. |
| Governance references | `.jikuo/project_context.yaml document_roles` plus existing registry refs | Do not mutate package registry shards for local choices. |
| Rule sources | `.jikuo/project_context.yaml main_document_mounts.active_mount_authority` | Read-only in the first implementation unless explicitly approved later. |
| Rule sets | `docs/registry/mount_sets.yaml` | Read-only for D4 implementation; package registry edits require a separate registry task. |

The implementation may later move project-local document rules into a dedicated
file such as `.jikuo/document_rules.yaml`. If that happens, Studio must keep the
same `configuration_terms` and update only `internal_refs`.

#### 7.4.3 No-Write Plan Surface

Future plan command / tool:

```text
jikuo.plan_document_rules_update
```

Possible CLI shape:

```text
python -B -m jikuo studio document-rules plan \
  --add-context-doc docs/example.md \
  --add-completion-check docs/example.md \
  --completion-update-rule "product-facing docs changed" \
  --format json
```

Minimum request fields:

```yaml
schema: "jikuo.studio.document_rules_update_request.v0"
project_root: "<local path>"
operations:
  - operation_id: "op_1"
    operation_type: "add_context_document|remove_context_document|add_completion_check|remove_completion_check|add_governance_reference|update_note"
    path: "docs/example.md"
    user_label: "optional short label"
    update_required_when: "optional completion-check rule"
    reason: "optional user-facing reason"
host_semantic_intent: {}
```

Minimum no-write response:

```yaml
schema: "jikuo.studio.document_rules_update_plan.v0"
status: "review|refused|noop"
writes_performed: false
write_allowed_by_command: false
target_files:
  - ".jikuo/project_context.yaml"
proposed_changes:
  added_context_documents: []
  removed_context_documents: []
  added_completion_checks: []
  removed_completion_checks: []
  added_governance_references: []
  changed_notes: []
diff_preview:
  before: {}
  after: {}
validation:
  path_checks: []
  duplicate_checks: []
  authority_checks: []
  legacy_projection_checks: []
risks: []
non_effects:
  - "does_not_write_project_context"
  - "does_not_edit_registry_shards"
  - "does_not_regenerate_legacy_task_map"
  - "does_not_change_policy_evaluator_behavior"
approval:
  required: true
  approval_phrase_hint: "Approve Document Rules update"
client_display_links: {}
```

The no-write plan must be the only way the UI previews document-rule edits. The
frontend may keep temporary form state, but it must not compute canonical diffs
or write YAML directly.

#### 7.4.4 Validation Rules

The plan surface should reject or flag:

- paths outside the project root;
- absolute paths unless explicitly normalized into project-relative refs;
- missing files when the operation requires an existing document;
- duplicate context or completion-check entries;
- attempts to edit `docs/governance/jikuo_productization_task_map.md` as a new
  source of task ordering, open items, capability metadata, or registry
  authority;
- attempts to mutate `docs/registry/*.yaml` from the Document Rules UI;
- attempts to change policy evaluator behavior or active policies;
- operations without a clear user-facing reason when the write would add a new
  completion check.

No-write plans may return `status: "noop"` when the requested rule already
exists exactly as requested.

#### 7.4.5 Guarded Apply Surface

Guarded apply command / tool:

```text
jikuo.apply_document_rules_update
```

Possible CLI shape:

```text
python -B -m jikuo studio document-rules apply \
  --plan-ref ".jikuo/runtime/history/<plan-card>.md" \
  --confirm-apply \
  --approval-phrase "Approve Document Rules update" \
  --format json
```

Implementation status (2026-06-02): `JIKUO-STUDIO-01D8` implements the
minimal CLI/core and local web guarded apply path. The apply path consumes a
reviewed plan payload, checks the plan schema/status, verifies the reviewed
`.jikuo/project_context.yaml` fingerprint against the current file, requires
`--confirm-apply`, and requires the exact approval phrase
`Approve Document Rules update`.

Minimum apply contract:

```yaml
schema: "jikuo.studio.document_rules_update_apply_result.v0"
status: "applied|refused"
write_performed: true|false
target_files:
  - ".jikuo/project_context.yaml"
applied_operations: []
refusal_reasons: []
runtime_card_ref: ".jikuo/runtime/history/..."
non_effects:
  - "does_not_edit_registry_shards"
  - "does_not_regenerate_legacy_task_map"
  - "does_not_mutate_policies"
```

Guarded apply must refuse when:

- no reviewed plan payload or plan fingerprint is supplied;
- the approval phrase is missing or mismatched;
- `confirm_apply` is not true;
- the current source file fingerprint no longer matches the reviewed plan;
- the plan would write outside `.jikuo/project_context.yaml` or a future
  explicitly approved project-local document-rules file;
- the request tries to mutate package registry shards, active policies, starter
  manifests, runtime cards, or the legacy task map.

Current write target:

- `.jikuo/project_context.yaml` only.

Current non-targets:

- `docs/governance/jikuo_execution_mounts.md` remains governance guidance, not
  an editable Document Rules target;
- `docs/registry/*.yaml` remain registry authority, not edited from Document
  Rules;
- `docs/governance/jikuo_productization_task_map.md` remains a legacy
  projection and is not regenerated or promoted by this flow.

#### 7.4.6 Frontend Flow

The first interactive UI should follow this exact sequence:

1. render `Document Rules` from `summaries.document_mounts`;
2. let the user edit local form state only;
3. call `jikuo.plan_document_rules_update`;
4. render proposed changes, validation results, write effects, non-effects,
   and card links;
5. require an explicit approval phrase before apply controls are enabled;
6. call `jikuo.apply_document_rules_update`;
7. refresh `jikuo.studio.global_status.v0`;
8. show the apply result card and updated Document Rules section.

The UI must not hide a disabled action. If the plan/apply surface is unavailable
or degraded, Studio should show the reason and keep the section read-only.

#### 7.4.7 Tests And Acceptance

Design acceptance for D4 is this section plus registry updates. Implementation
acceptance for the future code slice should include:

- plan with add-context-doc returns `writes_performed=false`;
- plan with add-completion-check includes `update_required_when`;
- plan rejects paths outside the project root;
- plan refuses legacy task-map authority expansion;
- plan reports noop for duplicate entries;
- apply without approval phrase refuses;
- apply with stale source fingerprint refuses;
- apply with approval writes only the approved project-local target file;
- full test discovery remains green;
- `git diff --name-only -- docs/governance/jikuo_productization_task_map.md`
  remains empty unless the task explicitly approves projection repair;
- Studio Web refresh shows updated Document Rules after apply;
- completion-review runtime card includes document-rule update evidence.

#### 7.4.8 Explicit Non-Goals

D4 and its first implementation do not:

- implement a general knowledge graph;
- add DATA-01 event-ledger writes;
- make lifecycle node execution mandatory;
- mutate registry shards from the customer configuration UI;
- change policy evaluator matching fields;
- make Studio the only supported way to configure JIKUO;
- make hook / MCP mounted behavior stricter than proven by host adapters.

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

Implementation status (2026-06-01): implemented in
`src/jikuo/integrations/studio_web/server.py`, exposed through
`python -B -m jikuo studio serve --host 127.0.0.1 --port 8765`, and covered by
`tests/studio_web_server_tests.py`.

Acceptance:

- shows overview, runtime, configuration, integrations, policy/template summary,
  actions, and diagnostics;
- no guarded writes yet;
- does not parse Markdown cards as business data;
- does not require a specific AI GUI client.

### `JIKUO-STUDIO-01D0`: Configuration Action Inventory And Document-Mount Design

Record the customer configuration action inventory before adding editable UI.

Implementation status (2026-06-01): documented in this work order. No runtime
or frontend behavior is changed by this record.

Acceptance:

- customer configuration domains are listed by user goal;
- document mounting and main-document selection are treated as first-class
  configuration domains;
- source-of-truth and projection boundaries are explicit;
- guarded action candidates are named without implementing direct UI writes;
- future `01D` implementation has a clear target.

### `JIKUO-STUDIO-01D1`: Document-Mount Read Model

Project document mounting is now visible through the Studio global status
read model before any editable UI exists.

Implementation status (2026-06-01): implemented in
`src/jikuo/studio/global_status.py`, with panel/action descriptors in
`src/jikuo/studio/panels.py` and `src/jikuo/studio/actions.py`, and covered
by `tests/studio_global_status_tests.py` plus
`tests/studio_panel_action_registry_tests.py`.

Acceptance:

- `summaries.document_mounts` reads `.jikuo/project_context.yaml`
  `document_roles` and `main_document_mounts`;
- the summary reports active mount authority, completion-check documents,
  role counts, missing required roles, mount-set count, and Studio mount-set
  status;
- the summary publishes `configuration_terms` mapping user-facing language to
  internal refs;
- `studio.document_mounts` appears as a panel descriptor;
- `studio.document_mounts.review` is an available no-write action descriptor;
- `studio.document_mounts.plan_update` is registered but disabled until the
  guarded plan/apply surface exists;
- no project context, registry, policy, runtime, or legacy task-map write is
  performed by the read model.

### `JIKUO-STUDIO-01D2`: Document-Mount Frontend Section

Make the document-mount read model visible in the local Studio web console
instead of hiding it inside the generic panel/action lists.

Implementation status (2026-06-01): implemented in
`src/jikuo/integrations/studio_web/server.py` and covered by
`tests/studio_web_server_tests.py`.

Acceptance:

- the page contains a dedicated user-facing `Document Rules` section;
- the section displays document-role count, completion-check document count,
  missing required role count, and mount-set count;
- completion-check documents are shown with their status and update rule;
- current rule sources and disabled `studio.document_mounts.plan_update`
  reason are visible using user-facing labels;
- the page remains read-only and does not expose approval-phrase or apply UI.

### `JIKUO-STUDIO-01D3`: Configuration Vocabulary Mapping

Protect the local Studio UI from semantic drift by mapping stable customer
language to current internal architecture refs.

Implementation status (2026-06-01): implemented in
`src/jikuo/studio/global_status.py` and consumed by
`src/jikuo/integrations/studio_web/server.py`; covered by
`tests/studio_global_status_tests.py` and `tests/studio_web_server_tests.py`.

Acceptance:

- `summaries.document_mounts.configuration_language_schema` is
  `jikuo.studio.configuration_language.v0`;
- `configuration_terms` include `document_rules`, `completion_checks`,
  `rule_sources`, and `edit_status`;
- frontend binds to vocabulary terms for visible copy;
- internal refs remain available as support/debug metadata;
- primary frontend copy avoids internal architecture phrases such as
  `mount authority`.

### `JIKUO-STUDIO-01D4`: Document Rules Plan / Apply Design

Define the future no-write plan and guarded apply contract for editable
Document Rules before implementation starts.

Implementation status (2026-06-01): documented in section 7.4 of this work
order. No runtime code, MCP tool, or frontend apply control is implemented by
this slice. The first CLI/core no-write plan implementation is tracked
separately as `JIKUO-STUDIO-01D5`.

Acceptance:

- user operations are defined in customer language;
- internal targets are mapped to current project-local configuration files;
- the no-write plan response schema and non-effects are specified;
- the guarded apply refusal and write boundaries are specified;
- frontend flow is sequenced through plan, approval, apply, and refresh;
- tests for the future implementation are listed before code work begins;
- the legacy task map remains untouched.

### `JIKUO-STUDIO-01D5`: Document Rules No-Write Plan Backend

Implement the plan-only side of the section 7.4 contract:

```powershell
python -B -m jikuo studio document-rules plan `
  --add-context-doc docs/example.md `
  --add-completion-check docs/example.md `
  --add-governance-reference docs/governance/example.md `
  --format json
```

Implementation status (2026-06-01): `src/jikuo/studio/document_rules.py`
returns `jikuo.studio.document_rules_update_plan.v0` as a no-write plan. The
root CLI exposes it through `python -B -m jikuo studio document-rules plan`.
`src/jikuo/studio/actions.py` marks `studio.document_mounts.plan_update` as an
available no-write plan action while keeping apply as planned.

Acceptance:

- the plan reports target file `.jikuo/project_context.yaml`;
- context document, completion-check, and governance-reference additions are
  previewed without writes;
- duplicate requests return `noop` items instead of false changes;
- outside-root, missing-file, and legacy-task-map authority-expansion attempts
  are refused before any apply;
- `writes_performed=false` and `write_allowed_by_command=false`;
- apply remains unavailable until a separate guarded implementation slice.

### `JIKUO-STUDIO-01D6`: Document Rules Frontend Plan Preview

Expose the `JIKUO-STUDIO-01D5` no-write plan backend through the local Studio
web console without adding apply behavior:

```text
POST /api/document-rules/plan
```

Implementation status (2026-06-01): `src/jikuo/integrations/studio_web/server.py`
accepts JSON requests for context-document, completion-check, and rule-source
changes, calls `src/jikuo/studio/document_rules.py`, and returns
`jikuo.studio.document_rules_update_plan.v0`. The Studio page renders a compact
Document Rules preview form and displays status, diff preview, validation, and
approval boundary. The route returns structured `review`, `noop`, or `refused`
plans as successful no-write responses; only invalid JSON or unknown routes are
HTTP-level failures.

Acceptance:

- the page remains a no-write control shell, not an apply surface;
- the preview form uses customer-facing Document Rules language while the plan
  response retains internal target refs for verification;
- `POST /api/document-rules/plan` never writes `.jikuo/project_context.yaml`;
- refused validation, including outside-root paths, is visible in the plan
  response without writes;
- no approval phrase field or guarded apply button appears in this slice;
- the legacy task map remains untouched.

### `JIKUO-STUDIO-01D7`: Document Rules Source Semantics

Clarify the Document Rules source model before guarded apply is implemented.
The user-facing product principle is:

```text
structured configuration / registry = long-term source of truth
human-readable governance docs = guidance, help text, or projection
```

Implementation status (2026-06-01): `src/jikuo/studio/global_status.py`
classifies active mount authority entries into source kinds. The current
project-local editable configuration source is `.jikuo/project_context.yaml`.
`docs/governance/jikuo_execution_mounts.md` is rendered as governance guidance:
it explains program-level route and mount context, but it is not the target
that the Document Rules preview/apply flow edits.

Acceptance:

- the read model exposes `document_rule_sources` with `source_kind`,
  `editable_in_studio`, and `write_target` fields;
- `.jikuo/project_context.yaml` appears as `editable_configuration`;
- `docs/governance/jikuo_execution_mounts.md` appears as
  `governance_guidance`;
- the Studio page shows separate `Editable configuration` and
  `Governance guidance` sections instead of one ambiguous rule-source list;
- the UI does not imply that guidance documents are same-level configuration
  files;
- no project configuration, policy evaluator behavior, guarded apply, or legacy
  task-map projection changes are introduced by this slice.

### `JIKUO-STUDIO-01D8`: Document Rules Guarded Apply

Implement the minimal guarded apply path for reviewed Document Rules plans.

Implementation status (2026-06-02): implemented in
`src/jikuo/studio/document_rules.py`, the top-level
`python -B -m jikuo studio document-rules apply` CLI, and local Studio Web
`POST /api/document-rules/apply`.

Business meaning:

- users can move from "preview what this configuration change would do" to
  "explicitly approve this exact change" without editing YAML by hand;
- Studio remains a thin guarded control shell over canonical project config,
  not a second configuration kernel;
- governance guidance stays explanatory while structured project-local config
  remains the write target.

Acceptance:

- apply without `confirm_apply` or the approval phrase refuses and performs no
  write;
- apply with a stale `.jikuo/project_context.yaml` fingerprint refuses and
  performs no write;
- approved apply writes only `.jikuo/project_context.yaml`;
- successful apply can add/remove context document roles, completion checks,
  and active mount authority entries that were already represented in the
  reviewed plan;
- the local Studio page exposes an approval phrase input and guarded apply
  button only after a reviewable plan is present;
- `docs/governance/jikuo_productization_task_map.md`, `docs/registry/*.yaml`,
  active policies, package templates, starter manifests, and runtime cards are
  not mutated by Document Rules apply.

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
| `document_mounts_summary` | `.jikuo/project_context.yaml` document roles and `main_document_mounts`, plus `docs/registry/mount_sets.yaml` |
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
  document_mounts: {}
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

Known gaps after `01A`/`01B`/`01C` implementation:

- panel and action registries exist as read-only descriptors, but they do not
  execute actions;
- customer configuration domains are documented, and document-mount review is
  now available as a read-only Studio projection;
- document-mount data is visible in the local web console as a dedicated
  section;
- document-mount no-write planning is implemented as a CLI/core surface in
  `01D5`, but guarded apply and frontend editing controls are not implemented
  yet;
- action descriptors are embedded in `jikuo.studio.global_status.v0` for
  frontend convenience and also available through `jikuo.studio.action_registry.v0`;
- the local console is read-only and does not execute registered actions;
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
