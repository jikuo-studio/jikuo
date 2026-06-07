# JIKUO Trace And Evidence

> **Status**: First-use user guide for pre-release trace inspection.
> **Audience**: Users inspecting Policy Trace, Document Trace, turn anchors, and
> missing evidence in Studio or CLI status output.
> **Boundary**: This guide explains what JIKUO records and displays. It does
> not make report-only policies blocking, infer semantic intent, or replace
> policy definitions.

## 1. What Trace Views Show

JIKUO trace views are read-only runtime projections.

Policy Trace shows which policies triggered for a retained runtime round, which
actions and evidence were expected, and which policy evidence reports are still
missing.

Document Trace shows document obligations, observed read/write evidence, write
activity, completion-check applicability, and document evidence gaps for a
selected runtime round.

Both views are grouped by runtime round. A round usually corresponds to a
recorded lifecycle event such as `conversation_turn`, `task_start`, or
`completion_review`.

## 2. Turn Anchors

A turn anchor is the non-AI identity JIKUO receives from the host adapter for a
user turn. It can include an anchor id, session id, turn id, and prompt digest
status.

Turn anchors let Studio group Policy Trace and Document Trace records from the
same user turn without storing raw prompts or transcripts.

If a turn anchor is unavailable, JIKUO can still show retained runtime records,
but the grouping is weaker. That is a trace limitation, not proof that the work
failed.

## 3. Semantic Intent Evidence

JIKUO is not an AI semantic classifier.

The host AI may provide compact semantic intent before governed work. JIKUO
records that evidence, merges it into the work profile, evaluates policy
triggers, and displays the result.

If semantic intent is missing or fallback-only, policy routing may still be
visible, but the trace should be read as degraded evidence. JIKUO did not infer
hidden model intent.

## 4. Missing Evidence Is Classified

`missing` is still the raw fact: a runtime round did not include an expected
evidence item. The classification explains why the missing item may exist.

Current categories:

- `host_semantic_intent_missing`: the host AI did not provide or retain compact
  semantic intent evidence.
- `policy_evidence_not_recorded`: a triggered policy expected structured
  evidence, but the runtime round did not record a matching evidence item.
- `policy_scope_review_needed`: a broad report-only policy may have triggered
  outside the user's intended scope.
- `document_read_observation_limit`: a configured read obligation has no
  observed read proof; the current version may not capture read evidence fully.
- `document_write_evidence_gap`: expected, planned, or actual write evidence is
  not aligned for the selected round.
- `applicability_not_evaluated`: a completion-check candidate still needs an
  applicable, unchanged, deferred, or not-applicable decision.
- `no_comparable_trace`: the selected round has no structured trace of that
  type.
- `unknown_missing_evidence`: the runtime data is not structured enough to
  classify the gap more precisely.

The classification does not satisfy the evidence. It does not change a policy
result from missing to ok. It only makes the missing state easier to triage.

For the release-boundary explanation of why many `missing` reports are expected
in the current version, see `docs/user/limitations.md`. The short version is:
JIKUO keeps unverifiable facts visible instead of silently treating them as
proven or failed.

## 5. How To Inspect A Round

1. Open Studio with `jikuo studio serve`.
2. In Policy Trace, choose a runtime round from the dropdown.
3. Check the turn anchor, lifecycle event, triggered policies, and missing
   evidence classification.
4. In Document Trace, choose the matching runtime round.
5. Check expected documents, observed evidence, write activity, gaps, and
   unchecked applicability.
6. If a missing item is classified as a product or observation limit, treat it
   as a known limitation to disclose. If it is classified as missing policy or
   write evidence, record the evidence or update the governed work.

## 6. Current Limits

Runtime history is not yet a full DATA-01 event ledger.

Read evidence is weaker than write evidence in the current version. A missing
read observation can mean JIKUO did not capture proof, not that the host AI did
not read a file.

Many policies are report-only. A missing evidence report is visible and should
be reviewed, but it is not automatically a blocking gate unless the policy and
host integration explicitly enforce that gate.

Strict pre-turn behavior requires a host adapter. MCP tools and instruction
files alone do not prove mounted execution before every user turn.

The full current-boundary guide is `docs/user/limitations.md`. It explains how
to distinguish feature boundaries, required user configuration, missing host
semantic evidence, future product work, and genuine workflow evidence gaps.
