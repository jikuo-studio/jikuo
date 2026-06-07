# JIKUO Current Limitations

> **Status**: Pre-release user guide.
> **Audience**: Users deciding whether a visible `missing` report means a
> configuration issue, a current product boundary, future product work, or a
> genuine workflow evidence gap.
> **Boundary**: This guide explains current limits. It does not satisfy missing
> evidence, infer semantic intent, or make report-only policies blocking.

## 1. How To Read Missing Evidence

In the current version, a visible `missing` report is not automatically a
product defect.

`missing` means JIKUO did not receive a matching proof item for the selected
runtime round. Sometimes that points to work that still needs evidence. Often
in this pre-release version it means JIKUO is exposing a feature boundary: the
system cannot prove a fact yet, so it keeps the gap visible instead of silently
treating the fact as proven.

That distinction matters. A user should not have to guess whether JIKUO failed
or whether the current product deliberately cannot prove a specific kind of
evidence.

## 2. Boundary Categories

### Host Semantic Intent

JIKUO is not the semantic judge. The host AI supplies compact semantic intent;
JIKUO records it, merges it into the work profile, triggers policies, and shows
evidence.

If semantic intent is missing, unavailable, or fallback-only, the current round
does not have proven host-AI semantic evidence. That is a boundary of the
integration path, not proof that the user request was misunderstood.

User action: configure the host adapter or workflow to pass
`host_semantic_intent` before governed work when semantic proof matters.

### Report-only Policies

Many starter and pre-release policies are report-only. They make governance
expectations visible, but they do not block execution unless a stronger gate is
explicitly configured.

If a report-only policy shows missing evidence, read it as a review signal
first. The policy might need evidence, a not-applicable decision, or narrower
scope. It is not automatically a failed workflow.

User action: review the policy scope, record evidence, mark the policy not
applicable, or narrow the policy before treating the report as blocking.

### Runtime History

Runtime history is currently based on retained runtime visibility cards and
state summaries. It is not yet the full DATA-01 event ledger.

Older rounds may have counts, lifecycle labels, or policy data without complete
structured details. That can produce missing classifications such as
`no_comparable_trace`.

User action: inspect adjacent lifecycle rounds and treat missing historical
structure as an observability limit.

### Observed-read Evidence

Write-side evidence is more mature than read-side proof. JIKUO can often
compare required, planned, declared, and git-observed writes. It cannot yet
prove every document read with the same strength.

If a configured read obligation has no observed read evidence, that can mean
JIKUO did not capture proof. It does not prove the host AI ignored the document.

User action: capture explicit read evidence when read proof is required for the
workflow.

### Document Trace Comparability

Document Trace needs structured artifact assurance for the selected runtime
round. When that structure is unavailable, Studio can report that no comparable
trace exists.

That means the structured comparison is unavailable for that round. It is not
direct proof that no document was considered.

User action: inspect the runtime card and adjacent lifecycle rounds, or run a
workflow that emits artifact assurance for the relevant lifecycle.

### Completion And Final Evidence

Some completion-review, progress-summary, and final-response policy
obligations are declared before every evidence producer is fully automated.

This can make missing evidence visible even when the human-facing answer
contains the required business meaning. The missing report remains useful: it
records the automation gap that still needs product work.

User action: include the required business meaning in summaries and keep the
visible missing report as backlog evidence until the producer exists.

### Strict Mounted Execution

MCP tools and instruction files make JIKUO available, but strict mounted
execution requires a host adapter or hook that calls JIKUO before the user turn.

If mounted proof is missing, do not treat MCP availability as strict pre-turn
enforcement.

User action: use a mounted-capable host adapter when strict pre-turn execution
is part of the product promise.

## 3. What Users Should Do

Use the classification as a triage layer:

- If the cause is a configuration boundary, configure the missing integration or
  project setting.
- If the cause is a feature boundary, keep the report visible and treat it as
  known product debt.
- If the cause is report-only policy scope, review whether the policy should
  apply to that lifecycle.
- If the cause is genuine workflow evidence, record the evidence or update the
  work.

The raw `missing` fact should stay visible in every case. The classification
explains the gap; it does not erase it.

## 4. Related Guides

- `docs/user/trace-and-evidence.md`: how to inspect Policy Trace, Document
  Trace, turn anchors, and missing-evidence classifications.
- `docs/user/document-management.md`: how Document Rules configure local
  project documents and completion checks.
