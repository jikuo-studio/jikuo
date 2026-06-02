# INSIGHT-2026-06-02: Scope-First Execution, Event-First Authoring Gap

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: `POLTRIG-04` follow-up authoring review
- Not promoted to a work order in this slice

## Observation

JIKUO's policy evaluator has moved to scope-first behavior for scope-only
policies, but the policy authoring toolchain still presents an event-first
shape. This can make host agents and policy authors accidentally design new
policies as lifecycle/event-gated policies even when the intended trigger is a
work action scope such as `editing` or `discussion`.

The specific residue is:

- `src/jikuo/policy_store.py` still requires `trigger_event` in policy write
  plans and defaults it to `task_start`;
- `src/jikuo/integrations/mcp/adapter.py` still defaults
  `policy_trigger_event` to `task_start` when the caller omits it;
- `src/jikuo/agent_flow.py` policy-write proposal cards previously surfaced
  `trigger_event` as a primary shown input before explaining whether
  `applies_to_work_profile` is scope-only or lifecycle-gated;
- tests still preserve legacy and lifecycle-gated authoring examples, which is
  correct for compatibility but can reinforce the old mental model if no
  authoring-mode evidence is displayed.

The result is a governance UX mismatch:

```text
execution/evaluator layer:
  work_profile.policy_scopes -> scope-only policy applicability

authoring/tooling layer:
  trigger_event -> lifecycle-looking policy plan -> optional scopes
```

That mismatch does not mean the evaluator is still old. It means the write path
can keep reintroducing old trigger semantics by adding
`applies_to_work_profile.lifecycle_events` or by making the compatibility
trigger look like the real policy trigger.

## Current Mitigation

The low-risk mitigation added in this slice is a no-write authoring review
projection on policy write plans:

- `authoring_review.mode`: `scope_only`, `lifecycle_gated`, or
  `legacy_event_exact`;
- `authoring_review.compatibility_trigger_event`: the existing trigger anchor,
  shown as compatibility metadata;
- `authoring_review.hard_gated_by_lifecycle`: whether declared
  `lifecycle_events` will hard-gate applicability;
- `authoring_review.warnings`: currently includes
  `lifecycle_events_hard_gate_policy_applicability` and
  `policy_has_no_work_profile_scope_filter` when applicable.

`agent_flow` policy-write cards now surface this mode and warning without
changing policy schema, evaluator behavior, CLI compatibility, or active policy
records.

## Future Direction

A later, more thorough slice should decide whether to:

- rename or visually demote `trigger_event` to `compatibility_trigger_event`
  on authoring surfaces;
- make scope-first policy authoring the default for intent-driven policies;
- require explicit confirmation before adding `work_profile_lifecycle_events`
  to a policy that already has `policy_scopes`;
- add a reusable policy/template requiring policy-authoring evidence to state
  whether a proposed policy is `scope_only`, `lifecycle_gated`, or
  `legacy_event_exact`;
- revisit MCP argument defaults so omitted policy trigger anchors no longer
  imply `task_start` as the first authoring thought.

## Boundary

Do not change the evaluator or migrate existing active policies as part of this
insight. Legacy event-exact and lifecycle-gated policies remain valid
compatibility cases. The immediate concern is authoring visibility: make the
policy trigger mode explicit before writing or publishing policy records.
