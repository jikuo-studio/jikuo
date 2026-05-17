# INSIGHT-2026-05-17: Work-Unit Task Association Boundary

> **Classification**: deferred
> **Status**: deferred
> **Captured**: 2026-05-17

## Core Idea

JIKUO needs a future way to associate runtime proposals and lifecycle cards with
the registered task they belong to. Without that association, proposal history is
useful as a recent runtime log, but weak as a per-task execution record.

The desired future chain is:

```text
work_order_id -> work_unit_id -> proposal_id / lifecycle card / evidence
```

However, adding these fields before JIKUO can reliably force every governed turn
through the client hook / mounted harness would create a worse risk: incorrect
association. A missing association is visible; a wrong association can make a
task appear reviewed, completed, or evidence-backed when the card actually
belongs to different work.

## Design Boundary

Do not implement a heavy work-unit execution index until strict client mounting
is proven for at least one host path.

Future implementation should follow these constraints:

- `work_order_id` must come from explicit user input, an accepted registry
  context, or a confirmed follow-up tool chain.
- `work_unit_id` must be generated only inside a confirmed task context.
- `completion_review` should bind to the same `work_unit_id`; an unbound
  completion review may produce a card but must not satisfy a registered task.
- association state must be explicit, for example `confirmed`, `unbound`, or
  `manual_backfill`.
- heuristic guessing must not satisfy task completion, policy evidence, or
  registry execution records.
- historical runtime cards should not be rewritten; at most, later indexes may
  point to them with `manual_backfill` status.

## Why It Matters

This keeps JIKUO from creating a false audit trail.

The product needs task-level execution traceability, but traceability is only
valuable if the binding is trustworthy. Until hook / adapter proof can ensure
that JIKUO consistently sees the full lifecycle of a work unit, the safer
posture is to record this as a deferred architecture insight and keep current
runtime cards as visible but non-authoritative operation history.

## Questions To Resolve Later

- Which host hook or adapter can guarantee a pre-turn and pre-completion JIKUO
  call?
- Should `work_unit_id` live in DATA-01 execution events, runtime projections,
  work-order registry entries, or all three?
- What is the minimum explicit input required to bind a proposal to a
  `work_order_id`?
- Should task execution refs be stored in a separate generated index instead of
  hand-editing work-order entries?
- How should manual backfill be reviewed without rewriting historical cards?

## Current Decision

Do not promote this to an implementation work order yet.

Record the model and safety boundary as an insight. Revisit after Codex / Claude
hook proof or another strict mounted adapter demonstrates that JIKUO can invoke
the router and completion review reliably enough to avoid false associations.
