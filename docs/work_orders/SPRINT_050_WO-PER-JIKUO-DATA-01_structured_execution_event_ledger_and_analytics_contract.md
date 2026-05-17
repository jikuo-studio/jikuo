# SPRINT_050_WO-PER-JIKUO-DATA-01: Structured Execution Event Ledger and Analytics Contract

> **Status**: DATA-01A implemented; event schema and fixtures only, no runtime writes.
> **Date**: 2026-05-17
> **JIKUO layer**: runtime visibility / analytics contract.
> **Business meaning**: future dashboard, BI, bug diagnosis, user support, and audit review need stable structured execution data. JIKUO must not make future analytics depend on parsing Markdown cards or raw chat transcripts.

---

## 1. Why This Task Exists

JIKUO already emits chat-ready cards, runtime summaries, task-session YAML, policies, activation settings, and MCP responses. These are useful operational surfaces, but they are not yet a stable execution ledger for future dashboard / BI features.

If analytics is added later without a data contract, the product will be forced to reverse-engineer Markdown, one-off JSON projections, and client-specific proof artifacts. That would make bug reports hard to diagnose and make dashboards brittle.

The product direction is:

- collect local structured execution facts first;
- derive cards, status summaries, CLI output, MCP responses, dashboard views, and bug-report bundles from those facts;
- preserve privacy by default and avoid raw transcript capture.

---

## 2. Current Data Structures

Current useful structures:

- `agent_flow` proposal object: rich structured proposal data including trigger decision, cards, policy context, atom trace, write effects, runtime visibility, and display links. It is not yet a normalized append-only event stream.
- `.jikuo/runtime/last_card.md`: latest human-facing Markdown projection. It is excellent for users and poor as the canonical BI source.
- `.jikuo/runtime/state_summary.json`: latest structured runtime projection. It is useful for current state, but it is overwritten and loses sequence context.
- `.jikuo/runtime/history/*.md`: append-like Markdown proof history. It is useful for user verification, but hard for BI to query reliably.
- `.jikuo/task_sessions/*.yaml`: durable task-sidecar state. It captures lifecycle and evidence records, but does not capture every route decision, policy evaluation, adapter degradation, or runtime projection event.
- `.jikuo/policies/**`: policy store, proposals, decisions, approved policies, and manifests. These are governance configuration and history, not execution telemetry.
- `.jikuo/activation_settings.yaml`: project activation truth source. Runtime events should carry an activation snapshot or ref so later diagnosis can distinguish semantic, mounted, degraded, and strict adapter contexts.
- MCP adapter results: structured client-facing responses with display directives and field classification. They are useful surfaces, but should not be the only persistence model.

---

## 3. Problem Statement

JIKUO needs one canonical structured execution record layer that later projections can derive from.

Current gaps:

- `last_card.md` and history Markdown are readable but not analytics-native.
- `state_summary.json` is latest-state only.
- proposal JSON has useful detail but is not persistently appended as a normalized event stream.
- bug reports need stable correlation IDs across route -> task_start -> policy_eval -> runtime card -> guarded write.
- MCP privacy classification exists for response fields, but not yet as a general local event-ledger requirement.
- future dashboard / BI cannot reliably compute dead-zone rate, missing-evidence trends, guarded-write refusal/apply ratio, adapter degradation rate, or task-session completion health without structured events.

---

## 4. Design Principles

- Event-first, projection-second: cards and dashboards are derived views, not the canonical execution facts.
- Local append-only by default: the first implementation should write local records only.
- Schema-versioned records: every event includes `schema`, `schema_version`, and compatibility posture.
- Stable correlation IDs: records should support `event_id`, `run_id`, `proposal_id`, `task_session_id`, `policy_eval_id`, `tool_call_id`, `adapter_id`, and `source_surface` where applicable.
- Field-level privacy: every event field must be classifiable as `return`, `local_only`, `redact_required`, or `redact_optional`.
- No raw transcript by default: user turns may be summarized or hashed where needed, but raw chat history is not the baseline.
- Deterministic projections: `last_card.md`, `state_summary.json`, `jikuo show`, MCP status, future dashboard panels, and bug-report exports should read the same facts.
- Redacted bug-report bundles: support should come from explicit redacted exports, not screenshots or manual copy-paste.
- Unknown fields preserved: downstream readers must tolerate additive event fields.

---

## 5. Candidate Event Types

Initial event families to review before implementation:

- `jikuo.execution_started`
- `jikuo.conversation_turn_routed`
- `jikuo.configuration_reviewed`
- `jikuo.activation_settings_read`
- `jikuo.activation_settings_planned`
- `jikuo.activation_settings_applied`
- `jikuo.task_start_proposed`
- `jikuo.task_session_started`
- `jikuo.task_session_updated`
- `jikuo.task_session_completed`
- `jikuo.policy_runtime_evaluated`
- `jikuo.policy_dead_zone_detected`
- `jikuo.policy_suggestion_reviewed`
- `jikuo.guarded_write_requested`
- `jikuo.guarded_write_refused`
- `jikuo.guarded_write_applied`
- `jikuo.mcp_tool_called`
- `jikuo.runtime_card_written`
- `jikuo.adapter_degraded`
- `jikuo.error_reported`

---

## 6. Candidate Storage Model

Baseline candidate:

- `.jikuo/events/YYYYMMDD.jsonl`: local append-only structured execution ledger.
- `.jikuo/runtime/state_summary.json`: latest projection derived from recent events and current state.
- `.jikuo/runtime/history/*.md`: human proof projection derived from event-backed cards.
- Future optional projections: `.jikuo/analytics/*.json`, SQLite, DuckDB, or Studio-specific cached view models generated from events.

This task does not approve remote telemetry, a dashboard database, or any cloud sync.

---

## 7. Implementation Slices

- `DATA-01A`: finalize schema shape and add schema fixtures; no behavior change.
- `DATA-01B`: persist one event for `agent_flow` proposal / policy runtime evaluation.
- `DATA-01C`: include event refs in runtime cards and `state_summary.json`.
- `DATA-01D`: add `jikuo events inspect/export` for redacted support bundles.
- `DATA-01E`: let future dashboard / BI read event-ledger projections instead of parsing Markdown.

---

## 8. Acceptance Criteria

For `DATA-01A`:

- current data structures are documented and classified as source state, projection, or candidate event source.
- event schema fixture names and required IDs are reviewed.
- privacy classification rules are linked to SEC-02.
- dashboard / BI are explicitly out of scope.
- no runtime behavior changes are made.

For later implementation slices:

- no-write calls remain no-write except approved runtime/event projections.
- every event record has a schema version and correlation identifiers.
- runtime cards expose an event ref or projection ref.
- export surfaces redact local-only and approval-sensitive fields.

---

## 9. Non-Goals

- No remote telemetry by default.
- No raw chat transcript capture.
- No dashboard implementation in this task.
- No analytics warehouse dependency.
- No automatic policy creation from analytics.
- No hidden governance writes.

---

## 10. Discussion Questions

- Should the canonical ledger live under `.jikuo/events/` or `.jikuo/runtime/events/`?
- Which records are event facts, and which are projections?
- Should `agent_flow` persist full proposal JSON, normalized event records, or both?
- How large can local event logs become before rotation or compaction is needed?
- What is the safest bug-report export format for non-engineer users?
- Which metrics are product-critical for v0: dead-zone rate, missing-evidence rate, guarded-write refusal/apply ratio, adapter degradation rate, task-session completion health, or first-use setup completion?

---

## 11. Current Recommendation Before Claude Review

Do not implement dashboard / BI yet.

Implement `DATA-01A` first: schema fixtures and event taxonomy only. Then decide whether `DATA-01B` should write normalized JSONL events from `agent_flow`, `runtime_visibility`, or a new small `execution_events.py` core module.

---

## 12. DATA-01A Implementation Record

Implemented on 2026-05-17:

- `docs/schemas/execution_events_v0_draft.md`;
- `src/jikuo/fixtures/events/example_execution_started.jsonl`;
- `src/jikuo/fixtures/events/example_conversation_turn_routed.jsonl`;
- `src/jikuo/fixtures/events/example_policy_runtime_evaluated.jsonl`;
- `src/jikuo/fixtures/events/example_guarded_write_refused.jsonl`;
- `src/jikuo/fixtures/events/example_guarded_write_applied.jsonl`;
- `src/jikuo/fixtures/events/example_adapter_degraded.jsonl`;
- `src/jikuo/fixtures/events/example_execution_completed.jsonl`;
- `src/jikuo/fixtures/events/example_run_with_correlation.jsonl`;
- `tests/execution_events_schema_tests.py`.

First-batch event family:

- `jikuo.execution_started`;
- `jikuo.conversation_turn_routed`;
- `jikuo.policy_runtime_evaluated`;
- `jikuo.guarded_write_refused`;
- `jikuo.guarded_write_applied`;
- `jikuo.adapter_degraded`;
- `jikuo.execution_completed`.

Explicitly not implemented:

- no `src/jikuo/execution_events.py`;
- no `.jikuo/events/` creation;
- no runtime emit path;
- no dashboard / BI / support-bundle export command.

Verification:

- `python -B -m unittest tests.execution_events_schema_tests` passed.
