# INSIGHT-2026-05-21: Lifecycle Sequencing Owner Gap

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: `LIFECYCLE-01B` observed lifecycle footer review
- Not promoted to implementation in this slice

## Observation

JIKUO currently has event tools and event-local proposal builders, but no
component owns the cross-event sequence of a governed user turn.

MCP tools expose callable entry points such as `route_user_request`,
`propose_task_start`, and completion-review proposal paths. `agent_flow`
generates a complete no-write governance projection after one of those entries
is called: work profile, policy trigger results, evidence status, cards, and
runtime visibility.

Neither layer guarantees that the entries are called in lifecycle order:

```text
conversation_turn -> task_start -> completion_review
```

As a result, `observed_lifecycle` can honestly show only the cards that actually
happened, while still missing a recommended node such as `task_start`.

## Product Meaning

This is not a rendering bug and not a policy-evaluator bug. It is an
architecture gap in lifecycle orchestration.

The current system can make each node auditable after it is invoked, but it
cannot yet guarantee process completeness for a full user turn. A user may see
a final completion card and card links, but that does not prove the full
lifecycle was executed unless a runner, host hook, or harness enforced the
sequence.

This matters because policy trust depends on both:

- node-local correctness: each card correctly evaluates policies and evidence
  for its own event;
- turn-level completeness: the expected nodes were actually invoked before
  final delivery.

LIFECYCLE-01B only solves the first visible record layer. The second requires a
separate owner.

## Desired Future Behavior

A future lifecycle sequencing design should define one explicit owner for
turn-level process completeness. Candidate owners include:

- a thin host hook runner that calls JIKUO nodes in order;
- a JIKUO `lifecycle_runner` command called by host hooks;
- a hybrid harness where the host forces pre-turn and pre-final calls while
  JIKUO validates missing nodes before final display.

The owner should decide:

- when `conversation_turn` runs;
- when router output requires `task_start`;
- whether missing `task_start` blocks, warns, or remains observed-only;
- when `completion_review` is mandatory before final delivery or commit;
- how missing lifecycle nodes are surfaced without fabricating cards;
- how AI semantic routing and deterministic fallback feed the sequence.

## Boundary

Do not solve this by making MCP tools secretly call each other unless that is an
explicitly designed runner contract. Do not make `agent_flow` pretend it has
guaranteed lifecycle completeness when it only handled one event. Do not infer
missing node execution from the final card, a commit, or recent history.

The safe current behavior is to keep `observed_lifecycle` honest: it records
only the lifecycle cards that actually happened and can report missing
recommended nodes.

This insight records the follow-up architecture need only.
