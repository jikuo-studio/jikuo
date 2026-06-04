# INSIGHT-2026-06-04: Thin-shell Policy Candidate Generation Workflow

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: proactive policy-suggestion product discussion
- Related insight:
  - `docs/insights/INSIGHT-2026-05-16-proactive-policy-suggestion-metapolicy.md`
- Related policy:
  - `.jikuo/policies/approved/POLICY-jikuo-conversation-level-proactive-policy-suggestion.yaml`
- Related work orders:
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ROUTER-01_trigger_mode_and_conversation_turn_router.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AI-SEMROUTE-01_ai_semantic_routing_mvp.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-HOSTADAPT-01_host_adapter_contract.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01_policy_management_mvp.md`

## Observation

The phrase "JIKUO produces policy candidates" can be misleading under the
thin-shell architecture.

JIKUO must not run its own LLM, mine raw chat transcripts, or pretend to
semantically understand repeated user needs by itself. If candidate generation
means semantic interpretation, the host AI owns that step. JIKUO's proper role
is narrower: receive compact semantic signals or already structured evidence,
turn them into durable candidate records, deduplicate them, attach evidence,
and make the pending candidate visible for user review.

The current `POLICY-jikuo-conversation-level-proactive-policy-suggestion` can
trigger a report-only proactive review and produce candidate/no-candidate
runtime evidence. That is not yet the same as a durable policy-candidate
workflow. A candidate can still disappear after one turn because there is no
stable candidate inbox, no pending-candidate injection into future runtime
context, and no Studio decision surface for approve / revise / defer / record
as insight / ignore.

## Candidate Sources

JIKUO can safely produce a candidate record from three bounded sources:

- host-AI semantic signal: the host AI supplies a compact
  `host_policy_signal` or equivalent summary after understanding a turn or
  compact history;
- deterministic structured evidence: repeated INS entries, repeated policy
  feedback labels, repeated completion-review gaps, repeated task summaries, or
  repeated runtime warnings can be counted and grouped without semantic
  inference;
- explicit user instruction: a user says to remember, solidify, register, or
  convert a rule into policy / template form.

Only the first source performs semantic interpretation, and that interpretation
belongs to the host AI. JIKUO should store the signal's status, provider,
coverage, and evidence references instead of storing raw prompt text.

## Desired Workflow

```text
host AI notices a repeated need or explicit policy-like rule
-> host AI submits compact policy signal to JIKUO
-> JIKUO creates or updates a candidate record
-> JIKUO deduplicates related candidates and links INS / runtime evidence
-> JIKUO exposes pending candidates in runtime status and Studio
-> user chooses approve, revise, defer, record as insight, or ignore
-> guarded policy / template writers remain separate
```

The product value is not that JIKUO "understands" the conversation. The value is
that JIKUO converts one-off host-AI noticing into durable, reviewable, auditable
pending work.

## Candidate Record Shape

A future candidate store can start small:

```yaml
candidate_id: "POLICYCAND-..."
title: "Discussion-first no-write boundary"
candidate_rule: "When the user is only discussing or asking, do not edit files until an explicit edit request appears."
source_evidence:
  - kind: "host_policy_signal"
    ref: ".jikuo/runtime/history/..."
  - kind: "insight"
    ref: "docs/insights/..."
confidence: "medium"
status: "pending_user_review"
suggested_actions:
  - "record_as_insight"
  - "draft_policy"
  - "ignore"
non_effects:
  - "does_not_activate_policy"
  - "does_not_store_raw_transcript"
  - "does_not_replace_user_approval"
```

## Product Implication

The next clean implementation path is not to make JIKUO smarter. It is to add a
small durable candidate workflow around the existing router / policy-suggestion
review:

- preserve candidate records beyond a single proposal card;
- show pending candidates in Studio and runtime context;
- require future host-AI turns to notice unresolved candidate records;
- keep approve / activate / template publication behind guarded write flows;
- expose semantic coverage so users can tell whether a candidate came from host
  AI interpretation, deterministic grouping, or explicit instruction.

This keeps the product aligned with the thin-shell boundary while making the
proactive policy-suggestion policy visibly useful.
