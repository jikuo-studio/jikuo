# SPRINT_050_WO-PER-JIKUO-MVP-01: Work Receipt And Configuration MVP

> **Status**: Planned MVP work-order sequence; configuration surface now includes policy read UI, guarded policy evolution/refinement, guarded active-policy package-template publication, and guarded package-template activation slices.
> **Date**: 2026-06-03
> **JIKUO layer**: product slice / Studio surface / runtime evidence projection.
> **Business meaning**: Ship a small usable JIKUO version where a test user can configure documents and policies, let the host AI work, and then inspect an independently checkable AI work receipt without trusting the AI's chat summary.

---

## 1. Goal

The MVP should prove one user-facing loop:

```text
configure document and policy checklist
  -> host AI performs work
  -> JIKUO completion review observes available evidence
  -> Studio shows expected vs observed work receipt
  -> user adjusts the checklist when gaps are visible
```

This work order intentionally keeps JIKUO as a thin shell. It does not add an
LLM, a second governance kernel, a full lifecycle runner, or a smart
configuration editor.

## 2. Architecture Boundary

Keep the existing architecture.

- `src/jikuo/agent_flow.py`: orchestration and runtime proposal boundary.
- `src/jikuo/studio/artifact_assurance.py`: pure comparison engine; it must not
  inspect git, read files, or mutate state.
- `src/jikuo/runtime_visibility.py`: runtime card, history, and state summary
  persistence.
- `src/jikuo/studio/global_status.py`: Studio read model over canonical state.
- `src/jikuo/integrations/studio_web/server.py`: thin local frontend; it must
  display read models and guarded actions without owning governance semantics.
- `src/jikuo/studio/document_rules.py`: Document Rules plan/apply surface.
- `src/jikuo/policy_store.py` and policy-management read models: policy status,
  template, and guarded policy operations.

New MVP logic should plug into those layers rather than replace them.

## 3. Product Surfaces

The MVP has two simple user surfaces.

### Surface A: Configuration CRUD

Users can configure what JIKUO should care about:

- context documents;
- completion-check documents;
- governance references;
- active policies from already available policies/templates.

No intelligent recommendation is included in the configuration surface. The
host AI may suggest choices in chat, but JIKUO stores and displays only
explicit user-approved configuration.

### Surface B: Work Receipt Viewer

Users can inspect what happened:

- expected documents and required companion writes from configuration,
  work orders, registries, and policies;
- declared writes from the host AI / no-write plan;
- actual writes observed by JIKUO through read-only git inspection during
  completion review;
- path-level file lists for required companion writes, declared writes,
  actual writes, and gaps whenever comparable item evidence exists;
- gaps such as required companion write not observed, declared write not
  observed, actual write not declared, obligation not projected, and count-only
  evidence;
- limits such as mixed attribution and no proof of model understanding.

## 4. Integrated Insights

This MVP sequence absorbs the useful parts of existing insights without
expanding the architecture.

| Insight | MVP handling |
|---|---|
| `INSIGHT-2026-06-03-runtime-history-card-itemized-document-evidence-gap` | Drives the work receipt model. MVP implements write-side observed evidence first and keeps true observed-read telemetry deferred. |
| `INSIGHT-2026-06-03-completion-check-applicability-evidence-gap` | Keeps completion-check applicability separate from concrete reconciliation gaps. MVP fixes Studio wording now and defers itemized per-document applicability decisions. |
| `INSIGHT-2026-05-19-completion-review-evidence-bridge-gap` | Completion review should surface receipt and gap evidence so policy/runtime cards do not stay blind after real work occurred. |
| `INSIGHT-2026-05-21-lifecycle-sequencing-owner-gap` | MVP does not build a lifecycle runner. It adds explicit host-AI/manual completion-review invocation guidance. |
| `INSIGHT-2026-05-21-from-lifecycle-to-action-grammar` | MVP treats completion review as a lightweight checkpoint, not a rigid lifecycle engine. |
| `INSIGHT-2026-06-03-completed-chain-atom-history-backfill` | New MVP features should register scenario chains and atoms as they are implemented. Historical backfill is deferred. |
| `INSIGHT-2026-06-02-scope-first-execution-event-first-authoring-gap` | Do not solve MVP by changing policy evaluator keys or scope semantics. |

## 5. Work Order Sequence

The sequence has two parallel tracks: receipt value and configuration usability.
Receipt risk is addressed first because it is the core product promise.

### `MVP-RECEIPT-01`: Git Actual Write Observation Adapter

Add a small read-only adapter that observes working-tree writes during
completion review.

Capability:

- `CAP-RUNTIME-WRITE-OBSERVATION-01`

Likely module:

```text
src/jikuo/runtime_write_observation.py
```

Responsibilities:

- run `git status --porcelain`;
- optionally run `git diff --name-status`;
- emit `observed_actual_write_set`;
- label each item with `source_kind=git_diff`;
- label attribution as `mixed_or_uncertain` by default;
- map operations to `added`, `modified`, `deleted`, `renamed`, or `unknown`.

Non-goals:

- no writes;
- no git reset / checkout / cleanup;
- no file-content read for understanding;
- no changes to `artifact_assurance.py`.

Acceptance:

- unreported changed files can be observed as actual writes;
- deleted and added files are represented;
- untracked test files can be reported without being staged or modified;
- tests cover clean, modified, added, deleted, renamed/unknown, and non-git
  project states.

### `MVP-RECEIPT-02`: Completion Review Uses Git Observed Actual Writes

Wire the adapter into `agent_flow.py` completion review only.

Capability:

- `CAP-RUNTIME-WRITE-OBSERVATION-COMPLETION-REVIEW-01`

Behavior:

- preserve host/agent `changed_paths` as declared evidence;
- add git-observed actual writes as independent observed evidence;
- feed observed actual writes into the existing artifact assurance input;
- keep `artifact_assurance.py` pure.

Acceptance:

- `actual_write_not_planned` can trigger when git observes a file not present
  in declared/planned writes, as a legacy gap until companion-write obligation
  projection is available;
- declared-only and git-observed evidence remain distinguishable;
- runtime card non-effects honestly say git was inspected by the completion
  review adapter, not by the pure comparison engine.

### `MVP-RECEIPT-02A`: Required Companion Write Obligation Projection

Implementation status:

- first deterministic projector implemented in
  `src/jikuo/companion_write_obligations.py`;
- `completion_review` now feeds projected companion writes into the existing
  artifact-assurance comparison without making `artifact_assurance.py` inspect
  git or infer by itself;
- Studio Round Document Trace now separates required companion writes, declared
  writes, and actual writes in the selected-round view;
- runtime cards and Studio now expose companion projection trigger count and
  ignored actual-write count, so a dirty workspace item such as a non-governance
  scratch file can be distinguished from a missing companion obligation;
- host-semantic follow-up wording and the progress-summary business-meaning
  policy now align with the same receipt model: a user asking for progress /
  todo output should produce `progress_summary` semantic evidence and trigger
  the business-meaning obligation by scope, not only after a completion-review
  lifecycle event;
- future refinements still need better round attribution/baselines and more
  precise trigger rules.

Project the governance files that should be updated because a class of work
happened. This is the receipt value behind the old planned-vs-actual write
count: not "how many files did the AI say it would write", but "which companion
governance files were required, and were they actually written."

Capabilities:

- `CAP-RUNTIME-COMPANION-WRITE-OBLIGATION-01`
- `CAP-STUDIO-COMPANION-WRITE-RECEIPT-VIEW-01`

Likely module:

```text
src/jikuo/companion_write_obligations.py
```

Inputs:

- observed actual-write paths and operations from `MVP-RECEIPT-01/02`;
- mounted work order and active policy context;
- registry guidance from `docs/registry/*.yaml`;
- document evidence-chain design rules;
- optional host-declared write evidence.

Outputs:

- itemized `required_companion_write_set` with path, operation, source kind,
  source ref, trigger type, trigger source, and reason;
- `declared_write_set` remains separate and uses existing planned-write evidence
  for compatibility;
- explicit `governance_write_obligation_not_projected` gap when a trigger signal
  exists but no concrete companion path can be resolved.

Initial trigger classes:

- `feature_or_code_change`: requires the corresponding user action-chain and
  atomic capability registration evidence;
- `new_document`: requires the corresponding document registry or mount guidance
  registration;
- `work_order_progress`: requires work order progress and registry projection
  updates when the slice status changes;
- `policy_or_evaluator_change`: requires the corresponding policy/evaluator
  registry, tests, and governance guidance to stay in sync;
- `registry_change`: requires related scenario/capability/work-order registry
  consistency where applicable.

Non-goals:

- no automatic companion writes;
- no LLM-based classification inside JIKUO;
- no universal hard-coded document path inside policy text;
- no change to `artifact_assurance.py` purity;
- no DATA-01 event ledger requirement.

Acceptance:

- a receipt can show concrete paths for required companion writes, declared
  writes, actual writes, and write gaps;
- `planned writes = 0` no longer hides the distinction between "no declared
  plan" and "no required companion obligations were projected";
- if code or document changes are observed but no companion write obligations
  are projected, Studio shows that as a review gap instead of silently reporting
  zero planned writes;
- if a required companion file is not actually written, Studio shows the exact
  missing path and the reason it was required;
- the projector resolves paths from mounted context, registry/work-order
  authority, or active policy references rather than storing a single global
  hard-coded path list in policy text.

### `MVP-RECEIPT-03`: Runtime Work Receipt Projection

Project a compact work receipt into existing runtime visibility.

Preferred first shape:

```text
state_summary.artifact_assurance
state_summary.work_receipt_preview
history card Work Receipt section
.jikuo/runtime/history/<round>.json structured state snapshot
```

Fields:

- expected reads;
- required companion writes;
- declared writes;
- git observed actual writes;
- gaps;
- evidence strengths;
- attribution limits.

Acceptance:

- latest runtime summary exposes a receipt preview;
- old count-only history cards remain compatible;
- each new history card has a matching structured state-summary snapshot, so a
  later non-completion runtime turn does not erase the latest completion
  receipt's itemized path evidence;
- receipt display never claims AI understanding;
- receipt data preserves itemized path lists whenever the producer had itemized
  evidence;
- no DATA-01 event ledger is required for this slice.

### `MVP-RECEIPT-04`: Studio Work Receipt Viewer

Upgrade the current Round Document Trace section rather than creating a new
frontend architecture.

Capability:

- `CAP-STUDIO-LATEST-COMPLETION-RECEIPT-01`
- `CAP-STUDIO-COMPANION-WRITE-RECEIPT-VIEW-01`

Panels:

- round selector;
- Expected;
- Required companion writes;
- Declared writes;
- Observed;
- Gaps;
- Limits.

Priority display:

- required companion writes and whether each path was observed;
- actual writes observed by git;
- actual writes not declared;
- declared writes not observed;
- governance write obligations not projected;
- count-only evidence;
- mixed or uncertain attribution.

Acceptance:

- selecting a round still binds all details to that round;
- the default selected round prefers the latest `completion_review` receipt when
  one exists, while still showing the latest runtime turn separately;
- if latest `state_summary.json` is overwritten by a later non-completion round,
  Studio loads the selected receipt's per-history state snapshot before falling
  back to count-only Markdown parsing;
- required companion write gaps, actual writes without declarations, and
  obligation-not-projected gaps are visible without reading chat history;
- evidence labels distinguish configured, declared, git observed, and
  count-only;
- path-level lists are visible for every required companion, declared, observed,
  and gap set that has itemized evidence;
- the Round Document Trace summary shows concrete `Gaps` separately from
  `Unchecked applicability` so completion-check candidates without per-document
  applicability evidence are not presented as reconciliation failures;
- the Expected, Observed, and Gaps detail columns use labeled subpanels so
  different evidence classes remain scannable when path lists become long;
- `+ N more` overflow rows can be expanded in place so users can inspect the
  full itemized receipt when path-level evidence exists;
- Studio does not infer paths from counts.

### `MVP-RECEIPT-05`: Completion Review Invocation Path

Document and expose the first practical way to run completion review.

MVP reality:

- pre-turn host hooks run before AI reads or writes;
- no full completion-review runner exists;
- host AI must call completion review at the end when it performed workspace
  writes; Studio/manual invocation remains a fallback, not the primary product
  loop.

Capability:

- `CAP-CODEX-HOOK-COMPLETION-RECEIPT-INSTRUCTION-01`

Deliverables:

- Codex hook `additionalContext` instruction that tells the host AI to run
  `completion_review` after file creation, edits, deletion, generated outputs,
  git staging, commits, or guarded project writes;
- universal instruction-file managed block wording that carries the same
  completion receipt obligation into `JIKUO.md` and synced client instruction
  files;
- CLI command example;
- PowerShell stop-parsing example for inline `--host-semantic-intent-json`;
- MCP/tool instruction wording for host AI;
- optional Studio action descriptor for "Run completion review" if a no-write
  or guarded boundary already exists;
- README or quickstart note for testers.

Acceptance:

- a host AI receives an explicit completion receipt obligation before it starts
  substantive work, either from the Codex hook additionalContext or from the
  managed instruction file it has loaded;
- if the host AI performs workspace writes, it is instructed to run
  `python -B -m jikuo.agent_flow propose --event completion_review --project-root
  <project-root> --format json` before final response;
- if completion review cannot run, the host AI must report the missing or failed
  receipt instead of implying a receipt exists;
- Windows PowerShell users can pass compact host semantic intent JSON without
  quote loss by using `python --% -B -m jikuo.agent_flow propose ...`;
- a tester can produce a receipt after an AI task without relying on a hidden
  automatic lifecycle runner;
- docs state that full lifecycle automation is deferred.

### `MVP-RECEIPT-06`: Semantic Intent Coverage Visibility

Expose the GUI subscription semantic-intent return gap without changing the
thin-shell architecture.

MVP reality:

- the pre-turn hook can mount JIKUO before the model answers;
- the hook cannot force true host-AI semantic classification after model
  understanding and before action;
- any scope can therefore slip through unless the host AI cooperatively returns
  compact `host_semantic_intent`.

Capability:

- `CAP-SEMANTIC-INTENT-COVERAGE-RUNTIME-01`

Deliverables:

- INS:
  `docs/insights/INSIGHT-2026-06-03-gui-subscription-semantic-intent-return-gap.md`;
- runtime `state_summary.semantic_intent_coverage` projection;
- Studio Overview semantic coverage card;
- selected Round Document Trace semantic coverage label;
- diagnostics when semantic coverage is `missing`, `fallback_only`, or
  `degraded`.

Acceptance:

- host-provided semantic intent is shown as `complete`;
- missing required semantic evidence is shown as `missing`;
- deterministic fallback is shown as `fallback_only`;
- Studio does not claim strict GUI semantic gating;
- policy evaluator inputs and scope taxonomy are unchanged.

### `MVP-CONFIG-01`: Document Rules CRUD Frontend Completion

Complete the thin frontend for Document Rules over the existing plan/apply
backend.

Scope:

- add context documents;
- add completion-check documents;
- add governance references;
- remove/unselect existing items;
- preview plan;
- guarded apply through the existing confirmation path.

Acceptance:

- users can configure the document checklist without editing YAML;
- all writes still go through `.jikuo/project_context.yaml` guarded apply;
- no smart suggestions or generated configuration are added.

### `MVP-CONFIG-02`: Policy Configuration Frontend MVP

Expose a minimal policy management surface in Studio.

Scope:

- list active policies;
- list available package templates / starter options already known to the
  policy-management read model;
- activate or deactivate/supersede through existing guarded plan/apply
  boundaries when available;
- show source and effect before any apply.

Acceptance:

- users can activate an existing policy/template without hand-editing policy
  files;
- no policy generation or AI recommendation is included;
- source category and write effect are visible.

Implementation status:

- first read-only Studio slice implemented with
  `/api/policy-management/status`;
- Studio lists active policies, proposal refs, package templates, starter
  packs, template coverage, policy-without-template counts, read-model
  limitations, and guarded operation descriptors;
- selected active-policy current configuration is visible through trigger
  profile, policy scopes, lifecycle events, condition filters, required
  actions, and required evidence;
- scope-first policy posture is visible through `policy_scopes`,
  lifecycle-event tags, `scope-first` labels when no lifecycle event is
  declared, and policy-management option sets for controlled UI fields;
- `studio.policy_evolution.plan` is registered as a guarded action descriptor
  for later deactivation, supersession, and trigger-condition planning;
- no-write policy evolution preview is implemented through
  `/api/policy-management/evolution/plan`, allowing Studio users to select an
  active policy and preview deprecation, refinement, or supersession write
  sets before any guarded apply;
- policy evolution preview now uses controlled trigger-profile fields for
  `policy_scopes`, `lifecycle_events`, and trigger mode; the same
  replacement work-profile fields are accepted by Studio, `agent_flow`, CLI,
  and MCP proposal/apply plumbing while preserving existing no-write and
  guarded boundaries;
- Studio guarded policy evolution apply is implemented through
  `/api/policy-management/evolution/apply` for core-writer-supported
  deprecation, trigger-profile refinement, and supersession operations; the UI
  disables apply when fields change after preview, posts the reviewed proposal
  ref with confirmation and approval evidence, and the backend verifies the
  proposal ref still matches the current payload before calling the existing
  guarded writer;
- trigger-profile refinement uses a narrow guarded writer that updates only
  `version`, `triggers`, `conditions`, and `applies_to_work_profile` on the
  target approved policy, writes proposal/decision records, updates manifest
  active version/proposal refs, and rereads the policy to verify the applied
  profile;
- Studio template activation is implemented through
  `/api/policy-management/template-activation/plan` and
  `/api/policy-management/template-activation/apply`; the UI lets users select
  an available package template, preview resolved project-context bindings and
  the four-item policy-store write set, disables apply if selection changes,
  checks the reviewed `plan_id`, and delegates to the existing guarded template
  activation writer after confirmation;
- template activation now stable-dedupes resolved policy `source_refs` by
  `(type, ref)`, preserving template, template-file, and project-context
  provenance while preventing repeated source rows in approved policies;
- remaining work: build the actual guarded interaction surfaces for active
  policy deactivation beyond deprecation/supersession, policy-to-template
  publication, starter-manifest publication, and broader policy editing beyond
  the currently supported policy evolution operations.

### `MVP-CONFIG-03`: Configuration Review Panel Closeout

Turn configuration review into a practical tester-facing checklist.

Scope:

- show configuration status;
- show missing or degraded setup items;
- link to Document Rules and policy configuration actions;
- show integration/hook status without overclaiming strict mounted behavior.

Acceptance:

- users can tell whether JIKUO is ready enough to produce a work receipt;
- degraded hook or completion-review automation status is visible.

### `MVP-CONFIG-04`: Configuration To Receipt Linkage

Make the loop between configuration and work receipt visible.

Scope:

- after Document Rules or policy changes, refresh Studio global status;
- show which configured documents will influence expected reads/candidates;
- in the receipt viewer, link gaps back to configuration surfaces where
  reasonable.

Acceptance:

- a tester can see why a gap exists and which configuration surface can change
  future expectations;
- no frontend-owned governance semantics are introduced.

### `MVP-CONFIG-05`: Configuration UX Release Polish

Make configuration CRUD usable enough for test users.

Scope:

- empty states;
- validation errors;
- refused-plan messages;
- confirmation copy;
- success refresh;
- local-only privacy copy.

Acceptance:

- a user can complete setup with minimal README help;
- errors explain the guarded boundary and next action.

### `MVP-RELEASE-01`: Private Test Release Gate

Prepare a usable private preview.

Scope:

- README quickstart;
- known limitations;
- license/release posture review;
- privacy sweep for runtime sidecars/cards;
- brand/IP checklist;
- basic smoke checklist for Studio and completion review.

Acceptance:

- test users know what is supported;
- proprietary/license and privacy caveats are explicit before broader sharing.

## 6. Deferred Work

Defer these until the MVP receipt and configuration loop is usable:

- true observed-read telemetry;
- host read telemetry;
- DATA-01 event ledger persistence;
- full lifecycle runner;
- multi-agent attribution;
- policy evaluator key/scope changes;
- intelligent configuration suggestions;
- hosted UI or desktop packaging;
- rollback.

## 7. Initial Implementation Order

1. `MVP-RECEIPT-01`
2. `MVP-RECEIPT-02`
3. `MVP-RECEIPT-02A`
4. `MVP-RECEIPT-03`
5. `MVP-RECEIPT-04`
6. `MVP-RECEIPT-05`
7. `MVP-RECEIPT-06`
8. `MVP-CONFIG-01`
9. `MVP-CONFIG-02`
10. `MVP-CONFIG-03`
11. `MVP-CONFIG-04`
12. `MVP-CONFIG-05`
13. `MVP-RELEASE-01`

`MVP-CONFIG-01` may start in parallel with `MVP-RECEIPT-01` if capacity allows,
but receipt observation should be proven early because it carries the core MVP
value.

## 8. Mount Requirements

Mount this work order with:

- `.jikuo/project_context.yaml`;
- `docs/governance/jikuo_execution_mounts.md`;
- `docs/governance/jikuo_document_evidence_chain_design.md`;
- `docs/insights/INSIGHT-2026-06-03-runtime-history-card-itemized-document-evidence-gap.md`;
- `docs/insights/INSIGHT-2026-06-03-gui-subscription-semantic-intent-return-gap.md`;
- `docs/insights/INSIGHT-2026-05-19-completion-review-evidence-bridge-gap.md`;
- `docs/insights/INSIGHT-2026-05-21-lifecycle-sequencing-owner-gap.md`;
- `docs/insights/INSIGHT-2026-05-21-from-lifecycle-to-action-grammar.md`;
- `docs/registry/work_orders.yaml`;
- `docs/registry/mount_sets.yaml`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-01_global_console_and_configuration_shell.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DATA-01_structured_execution_event_ledger_and_analytics_contract.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01_policy_management_mvp.md`.

The structured mount bundle is `MOUNT-MVP-WORK-RECEIPT-CONFIGURATION`.
