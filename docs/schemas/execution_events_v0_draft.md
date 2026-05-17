# JIKUO Execution Events Schema v0 Draft

> **Schema version**: `jikuo.execution_event.v0_draft`
> **Status**: DATA-01A fixture contract only.

## Purpose

Future Dashboard, Studio, BI, support-bundle, and audit views need structured
execution facts. They should not depend on parsing Markdown runtime cards, raw
chat transcripts, or latest-only state summaries.

DATA-01A defines example records only. It does not approve runtime event
persistence, remote telemetry, dashboard implementation, or a new write path.

## Storage Direction

Later slices may append local JSONL records under:

```text
.jikuo/events/YYYYMMDD.jsonl
```

Do not place canonical append-only events under `.jikuo/runtime/`; runtime is a
projection area for cards, latest summaries, and human proof surfaces.

## Required Envelope

Every event record must include:

| Field | Meaning |
|---|---|
| `schema` | `jikuo.execution_event.v0_draft` during DATA-01A. |
| `event_type` | One of the initial event types below. |
| `event_id` | Stable event id. |
| `run_id` | Correlation id for a user turn or tool invocation run. |
| `monotonic_seq` | Per-run monotonic integer. |
| `wall_clock_utc` | UTC timestamp. |
| `source_surface` | `cli`, `mcp`, `adapter`, `hook`, `studio`, or `test_fixture`. |
| `field_classification` | Field-level privacy classification map. |
| `payload` | Event-specific compact facts. |

Optional correlation fields:

- `proposal_id`
- `task_session_id`
- `policy_eval_id`
- `tool_call_id`
- `adapter_id`

## Initial Event Types

DATA-01A fixtures cover:

- `jikuo.execution_started`
- `jikuo.conversation_turn_routed`
- `jikuo.policy_runtime_evaluated`
- `jikuo.guarded_write_refused`
- `jikuo.guarded_write_applied`
- `jikuo.adapter_degraded`
- `jikuo.execution_completed`

`policy_dead_zone_classification` is a field inside
`jikuo.policy_runtime_evaluated`, not a separate first-batch event.

Task-session lifecycle events are intentionally not first-batch event types:
task-session YAML remains source state. Execution events may reference a
`task_session_id` or guarded write result without duplicating the full session.

## Privacy Classes

Event fields use the SEC-02 privacy vocabulary:

- `return`
- `local_only`
- `redact_required`
- `redact_optional`

DATA-01B or later must define concrete export profiles before support bundles
exist. Candidate profiles:

- `local_full_v0`: local operator view; includes local-only refs.
- `support_bundle_v0`: redacted support export; removes local-only fields and
  hashes or redacts sensitive values.
- `public_bug_report_v0`: minimal user-sharable facts, no local paths, no raw
  inputs, no approval phrases.

## Compatibility

Readers must tolerate:

- unknown event types;
- additive payload fields;
- truncated final JSONL lines;
- missing optional correlation ids;
- out-of-order wall-clock timestamps when `monotonic_seq` is available.
