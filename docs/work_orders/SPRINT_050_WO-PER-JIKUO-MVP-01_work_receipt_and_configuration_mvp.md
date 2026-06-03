# SPRINT_050_WO-PER-JIKUO-MVP-01: Work Receipt And Configuration MVP

> **Status**: Planned MVP work-order sequence.
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

- expected documents and write candidates from configuration and plans;
- declared planned writes from the host AI / no-write plan;
- actual writes observed by JIKUO through read-only git inspection during
  completion review;
- gaps such as actual write not planned, planned write not observed, and
  count-only evidence;
- limits such as mixed attribution and no proof of model understanding.

## 4. Integrated Insights

This MVP sequence absorbs the useful parts of existing insights without
expanding the architecture.

| Insight | MVP handling |
|---|---|
| `INSIGHT-2026-06-03-runtime-history-card-itemized-document-evidence-gap` | Drives the work receipt model. MVP implements write-side observed evidence first and keeps true observed-read telemetry deferred. |
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
  in planned writes;
- declared-only and git-observed evidence remain distinguishable;
- runtime card non-effects honestly say git was inspected by the completion
  review adapter, not by the pure comparison engine.

### `MVP-RECEIPT-03`: Runtime Work Receipt Projection

Project a compact work receipt into existing runtime visibility.

Preferred first shape:

```text
state_summary.artifact_assurance
state_summary.work_receipt_preview
history card Work Receipt section
```

Fields:

- expected reads;
- declared planned writes;
- git observed actual writes;
- gaps;
- evidence strengths;
- attribution limits.

Acceptance:

- latest runtime summary exposes a receipt preview;
- old count-only history cards remain compatible;
- receipt display never claims AI understanding;
- no DATA-01 event ledger is required for this slice.

### `MVP-RECEIPT-04`: Studio Work Receipt Viewer

Upgrade the current Round Document Trace section rather than creating a new
frontend architecture.

Panels:

- round selector;
- Expected;
- Declared / Planned;
- Observed;
- Gaps;
- Limits.

Priority display:

- actual writes observed by git;
- actual writes not planned;
- planned writes not observed;
- count-only evidence;
- mixed or uncertain attribution.

Acceptance:

- selecting a round still binds all details to that round;
- `actual_write_not_planned` is visible without reading chat history;
- evidence labels distinguish configured, declared, git observed, and
  count-only;
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
- CLI command example;
- MCP/tool instruction wording for host AI;
- optional Studio action descriptor for "Run completion review" if a no-write
  or guarded boundary already exists;
- README or quickstart note for testers.

Acceptance:

- a host AI receives an explicit completion receipt obligation before it starts
  substantive work;
- if the host AI performs workspace writes, it is instructed to run
  `python -B -m jikuo.agent_flow propose --event completion_review --project-root
  <project-root> --format json` before final response;
- if completion review cannot run, the host AI must report the missing or failed
  receipt instead of implying a receipt exists;
- a tester can produce a receipt after an AI task without relying on a hidden
  automatic lifecycle runner;
- docs state that full lifecycle automation is deferred.

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
3. `MVP-RECEIPT-03`
4. `MVP-RECEIPT-04`
5. `MVP-RECEIPT-05`
6. `MVP-CONFIG-01`
7. `MVP-CONFIG-02`
8. `MVP-CONFIG-03`
9. `MVP-CONFIG-04`
10. `MVP-CONFIG-05`
11. `MVP-RELEASE-01`

`MVP-CONFIG-01` may start in parallel with `MVP-RECEIPT-01` if capacity allows,
but receipt observation should be proven early because it carries the core MVP
value.

## 8. Mount Requirements

Mount this work order with:

- `.jikuo/project_context.yaml`;
- `docs/governance/jikuo_execution_mounts.md`;
- `docs/governance/jikuo_document_evidence_chain_design.md`;
- `docs/insights/INSIGHT-2026-06-03-runtime-history-card-itemized-document-evidence-gap.md`;
- `docs/insights/INSIGHT-2026-05-19-completion-review-evidence-bridge-gap.md`;
- `docs/insights/INSIGHT-2026-05-21-lifecycle-sequencing-owner-gap.md`;
- `docs/insights/INSIGHT-2026-05-21-from-lifecycle-to-action-grammar.md`;
- `docs/registry/work_orders.yaml`;
- `docs/registry/mount_sets.yaml`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-01_global_console_and_configuration_shell.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DATA-01_structured_execution_event_ledger_and_analytics_contract.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01_policy_management_mvp.md`.

The structured mount bundle is `MOUNT-MVP-WORK-RECEIPT-CONFIGURATION`.
