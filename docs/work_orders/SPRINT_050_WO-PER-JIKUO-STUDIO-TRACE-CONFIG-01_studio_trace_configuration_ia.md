# SPRINT_050_WO-PER-JIKUO-STUDIO-TRACE-CONFIG-01: Studio Trace And Configuration IA

> **Status**: Accepted for implementation; first frontend grouping, policy trace read model, policy trace frontend, and Policy Trace round selector implemented.
> **Date**: 2026-06-06
> **JIKUO layer**: DPL-06 Studio / runtime visibility.
> **Business meaning**: Studio should make the governance model easy to read without changing governance facts. Trace views answer what happened in a turn or round. Configuration views answer what is currently configured and which guarded changes are being proposed.

## 1. Purpose

The current Studio page mixes runtime trace, current policy state, current
document state, and guarded configuration controls in the same visual flow. That
keeps the features available, but it makes the user's mental model unstable:

```text
Trace
-> read-only evidence that was observed for a turn or runtime round

Configuration
-> current policy/document configuration plus preview/apply guarded changes
```

This work order reorganizes the frontend around that distinction while keeping
the existing Document Rules and Policy Management functionality intact.

JIKUO remains a thin governance runtime:

- It does not infer semantic meaning by itself.
- Host AI supplies compact semantic intent when available.
- JIKUO records, merges, evaluates policy triggers, displays evidence, and
  exposes receipts.
- Studio renders those records; it must not turn UI grouping into new semantic
  judgment.

## 2. Target Information Architecture

Top-level Studio grouping:

| Area | View | Meaning |
|---|---|---|
| Trace | Policy Trace | Per turn anchor, show which policies triggered at lifecycle nodes. |
| Trace | Document Trace | Per runtime round, show expected documents, observed evidence, gaps, and writes. |
| Configuration | Policy Configuration | Current policy state, starter/template compatibility, and guarded policy changes. |
| Configuration | Document Configuration | Current document rule state and guarded Document Rules changes. |

The important behavior is separation, not feature deletion.

## 3. Policy Trace

Policy Trace is a read-only evidence browser. It should display the latest
turn anchor and lifecycle nodes such as:

```text
conversation_turn
task_start
completion_review
```

For each lifecycle node, show the recorded policy runtime evidence:

- triggered policy id and title
- trigger ref and trigger reason
- condition status
- matched work-profile refs
- required action ids/types
- evidence status and missing evidence count
- final-response gate impact when present
- links to the runtime history card/state summary

Business meaning: the user can see which policies were activated by the current
turn anchor, and at which lifecycle node, without reading raw markdown cards.

## 4. Document Trace

Document Trace keeps the current Round Document Trace model, but it should be
clearly scoped as document evidence, not a general governance dashboard.

Required behavior:

- Default select the latest round.
- Keep rounds sorted newest first.
- Display turn_anchor for every round. If unavailable, show an explicit default
  value such as `unavailable`.
- Keep the existing write indicator on round options, but avoid making the whole
  select background green.
- Show details for only the selected round:
  - Expected documents
  - Observed evidence
  - Gaps
  - Writes

Business meaning: document evidence becomes round-level and inspectable, which
reduces the risk of mistaking global/latest state for what happened in a
specific round.

## 5. Policy Configuration

Policy Configuration should keep the current Policy Management capabilities and
make the current state explicit before any proposed change.

Current state should include:

- active policy count and policy list
- policy scope/lifecycle metadata
- final_response_gate state
- package templates and starter pack membership
- template compatibility and migration availability

Proposed change should keep one preview/apply mental model:

```text
select operation
-> preview guarded plan
-> apply guarded change
-> show receipt/result
```

Final-response gate changes should stay inside this path; they are policy
metadata changes, not a separate quick-save toggle.

Business meaning: all policy metadata changes remain auditable and previewed,
including changes that affect final response obligations.

## 6. Document Configuration

Document Configuration should preserve existing controls:

- Preview a Document Rules change
- Add files to Document Rules
- Apply guarded document rule changes
- Display current document roles/rules/mount state

The UI should move these controls under the configuration area rather than
co-locating them with Document Trace evidence.

Business meaning: users can distinguish "what documents were required or
observed this round" from "how future document rules will be configured."

## 7. Implementation Slices

### Slice 1: Frontend regrouping

- Add a visible Studio grouping for Trace and Configuration.
- Place Document Trace under Trace.
- Place Policy Management under Policy Configuration.
- Place Document Rules controls under Document Configuration.
- Do not delete existing preview/apply controls.

Acceptance:

- Page still renders existing Policy Management and Document Rules controls.
- Round Document Trace appears under Document Trace.
- There is no duplicate or conflicting save path for final_response_gate.

Implemented capability:

- `CAP-STUDIO-TRACE-CONFIGURATION-IA-01`

### Slice 2: Policy Trace read model

- Expose a compact policy trace read model from existing runtime state/history.
- Group triggered policies by lifecycle event and turn_anchor.
- Include lifecycle card links and missing evidence counts.
- Keep this as projection only; do not make it a new policy evaluator.

Acceptance:

- UI shows latest turn anchor.
- UI lists triggered policies for observed lifecycle nodes.
- Missing evidence and runtime card links are visible.

Implemented capability:

- `CAP-STUDIO-POLICY-TRACE-READ-MODEL-01`

### Slice 3: Policy Trace UI

- Add a lifecycle selector or grouped lifecycle sections.
- Add a Document Trace-style policy trace round selector.
- Show policy trigger details without requiring raw markdown card inspection.
- Render empty states for missing lifecycle nodes.

Acceptance:

- `conversation_turn`, `task_start`, and `completion_review` are distinguishable.
- Selecting a policy trace round updates the runtime source, triggered policies, and evidence gaps detail panels.
- Missing lifecycle nodes show an empty state rather than stale data.

Implemented capability:

- `CAP-STUDIO-POLICY-TRACE-FRONTEND-01`

### Slice 4: Configuration status cleanup

- Split current policy status from proposed policy changes.
- Split current document status from proposed document changes.
- Keep starter/template compatibility states visible in Policy Configuration.

Acceptance:

- Current state panels are read-only.
- Proposed change panels are the only places with preview/apply controls.

### Slice 5: Focused tests

- Add or update HTML/read-model assertions for the new grouping.
- Assert Document Trace remains round-specific.
- Assert Policy Trace data is sourced from runtime state/history projection.
- Assert existing Document Rules and Policy Management controls still render.

## 8. Non-Goals

- Do not rewrite the policy evaluator.
- Do not add JIKUO-side semantic inference.
- Do not remove existing Document Rules capabilities.
- Do not silently migrate policy templates.
- Do not change final_response_gate semantics in this work order.

## 9. Verification Plan

Run focused tests first:

```powershell
python -m unittest tests.studio_global_status_tests tests.studio_web_server_tests
```

Then run broader regression when the slice touches shared read models:

```powershell
python -m unittest discover -s tests -p "*_tests.py"
```

Manual Studio check:

```text
http://127.0.0.1:8766/
```

Expected user-visible result:

- Trace and Configuration are visually distinct.
- Policy Trace answers which policies triggered for the current turn anchor.
- Document Trace answers which documents were expected/observed/gapped per
  round.
- Configuration panels remain the place for guarded preview/apply changes.
