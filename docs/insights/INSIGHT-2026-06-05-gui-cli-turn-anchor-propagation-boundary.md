# INSIGHT-2026-06-05: GUI And CLI Turn-Anchor Propagation Boundary

## Classification

- Classification: `deferred`
- Status: `deferred`
- Captured during: Studio runtime evidence and turn-anchor propagation review
- Immediate decision: do not deepen GUI-only cross-call turn-anchor inheritance
  for the MVP
- Related insights:
  - `docs/insights/INSIGHT-2026-06-03-gui-subscription-semantic-intent-return-gap.md`
  - `docs/insights/INSIGHT-2026-05-21-lifecycle-sequencing-owner-gap.md`
- Related work orders:
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-HOSTADAPT-01_host_adapter_contract.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIFECYCLE-01_invoked_turn_lifecycle_completion.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MVP-01_work_receipt_and_configuration_mvp.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CODEX-PLUGIN-01_codex_plugin_pre_turn_harness_review.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SDK-01_agent_sdk_adapter_exploration.md`

## Observation

In GUI subscription mode, JIKUO can create or retain a turn anchor at the first
host-adapter or hook entry. Later MCP or CLI calls in the same
assistant-visible interaction do not naturally receive that anchor unless the
host explicitly passes it again.

This means a Studio overview anchor is useful identity evidence, but it is not
strict proof that every later tool call, policy proposal, or
`completion_review` receipt belonged to the same GUI turn. A later receipt can
still report a missing or retained-only anchor even when an earlier
`conversation_turn` record had one.

## Current Defect

- `UserPromptSubmit` runs before AI work and can generate or surface a
  prompt-free turn anchor.
- Subsequent MCP tool calls receive only their explicit arguments; the GUI
  client does not automatically pass the prior hook's anchor.
- Manual or host-invoked `completion_review` can therefore lose the anchor
  unless the host AI deliberately includes it.
- Runtime or history fallback can display a retained anchor, but that is weaker
  than explicit same-turn propagation and must be labeled as retained evidence.
- Current GUI hook proof is also degraded by UTF-8 surrogate rendering failures,
  so strict mounted GUI propagation must not be claimed as proven.

## Product Boundary

The GUI MVP should expose this limitation instead of hiding it behind
probabilistic inheritance. For GUI users, cross-call turn identity should be
presented as evidence with source strength:

- explicit host argument: strongest;
- runtime cache or active adapter context: best effort;
- retained history summary: weakest;
- missing: honest absence of proof.

Deeper GUI-only inheritance work is deferred. The current product boundary is
`instruction-guided + evidence-visible + gap-auditable`, not strict same-turn
control.

This GUI limitation is not unique to turn anchors. It also applies to semantic
intent return, lifecycle sequencing, automatic completion review, and any
future feature that requires the host client to preserve context across
independent calls.

## CLI Extension Path

A future CLI or wrapper adapter can implement this more robustly if JIKUO owns
the execution loop:

```text
user input
-> wrapper creates turn_anchor
-> wrapper passes turn_anchor to JIKUO routing / proposal calls
-> AI or host action runs inside that wrapper context
-> wrapper invokes completion_review before final receipt
-> receipt records turn_anchor source as explicit wrapper context
```

The stronger guarantee comes from host-loop ownership, not from the CLI surface
by itself. A CLI that merely calls independent commands would have the same
boundary as the GUI; a CLI/wrapper that owns the turn lifecycle can provide a
stable propagation path.

## Follow-Up

When CLI-version work starts, revisit this insight and design:

- current-turn anchor storage and explicit propagation in the host adapter
  contract;
- automatic `completion_review` invocation in a controlled finalization step;
- source-strength labels for explicit, active-context, retained, and missing
  anchors;
- Studio/runtime cards that disclose GUI limitations and CLI/wrapper
  capabilities without overstating either mode.

Until then, do not spend MVP time on deeper GUI-only turn-anchor inheritance.
