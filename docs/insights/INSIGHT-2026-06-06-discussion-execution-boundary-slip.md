# INSIGHT-2026-06-06: Discussion And Execution Boundary Slip

## Classification

- Classification: `deferred`
- Status: `deferred`
- Captured during: CLI enhanced workflow and Studio trace follow-up discussion
- Immediate decision: record the phenomenon as an insight; do not promote the
  earlier concrete pre-execution gate proposal into a task or policy yet
- Related insights:
  - `docs/insights/INSIGHT-2026-06-03-gui-subscription-semantic-intent-return-gap.md`
  - `docs/insights/INSIGHT-2026-06-05-gui-cli-turn-anchor-propagation-boundary.md`
  - `docs/insights/INSIGHT-2026-05-17-conservative-task-classification-routing.md`
- Related policies:
  - `.jikuo/policies/approved/POLICY-jikuo-discussion-first-no-write-boundary.yaml`
  - `.jikuo/policies/approved/POLICY-jikuo-implementation-intent-routing-before-change.yaml`

## Observation

A user turn phrased as a discussion request about whether Policy Trace could
gain a Document Trace-style round selector was handled by the host AI as an
implementation request. The host AI supplied semantic intent that allowed
workspace modification and then directly edited code.

The later audit showed that the discussion-first no-write policy did trigger,
but it was only surfaced as report-only policy evidence. JIKUO recorded and
displayed the policy state; it did not and should not independently decide the
turn's natural-language semantics or block the host AI's tool execution.

## Boundary Exposed

The failure mode was not that JIKUO misclassified the turn by itself. The
failure mode was that the host AI classified an ambiguous discussion/execution
turn as executable work before policy evidence could meaningfully influence the
actual tool-use boundary.

This exposes a product boundary between:

- semantic intent supplied by the host AI;
- JIKUO's deterministic policy trigger and evidence display;
- the host/client execution layer that decides whether tool calls and workspace
  writes are allowed.

## Deferred Question

The immediate if/then-style pre-execution gate proposal is too concrete and may
not generalize well. The deeper question is how to represent discussion versus
execution boundaries in a way that is semantic, reviewable, and extensible
without becoming a brittle keyword or rule ladder.

Future exploration should look for a more general mechanism that can:

- preserve ambiguity instead of collapsing it too early into editing intent;
- make discussion/execution boundary evidence visible before action;
- let user confirmation, policy evidence, and host semantic classification
  converge without forcing JIKUO to become an AI semantic judge;
- avoid turning every governance nuance into a hard-coded action rule.

## Business Meaning

This insight matters because users need to trust that "let's discuss whether
this should be done" and "please implement this" remain distinct interaction
modes. If the host AI collapses those modes too aggressively, JIKUO can still
show the policy evidence afterward, but the user's control over when work
starts is weakened.

For now this is retained as deferred design context rather than an approved
policy, work order, or implementation plan.
