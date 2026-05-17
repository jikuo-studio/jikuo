# INSIGHT-2026-05-17: Conservative Task Classification Routing

> **Classification**: promoted_to_task
> **Status**: promoted
> **Captured**: 2026-05-17
> **Promoted task**: Policy-governance routing simplification, queued in `JIKUO-DOCREG-01`

## Core Idea

JIKUO should treat natural-language task approval as enough to start or
continue a governed task.

When a user says "continue", "do the next task", "first do A then B", or the
equivalent in natural language, the harness should not add another heavy
approval layer before creating or binding the task-session execution carrier.

The important decision is not whether JIKUO should run. In mounted work, JIKUO
should run. The important decision is how the turn should be classified so the
right policies can be evaluated.

## Routing Principle

Use a simple task classification model:

- `discussion`: design, explanation, decision support, analysis, or review.
- `editing`: code, documentation, configuration, test, commit, or release work.
- `progress_summary`: progress, todo, status, or business-meaning summary.
- `other`: unclear or mixed task.

When classification is uncertain, route conservatively. `other` should not mean
"no policy applies." It should expand the policy scope at least to the
discussion and editing policy sets, because discussion is the lower-risk floor
and editing carries the stricter governance obligations.

## Why It Matters

Over-layered approval models make JIKUO feel heavy and can reintroduce
probabilistic execution: the more branches the agent must choose from, the more
likely a governed task silently falls through.

The better product posture is:

- every governed user turn enters the harness;
- task classification is visible and recorded;
- policy scope is deterministic once the classification is chosen;
- uncertain classification expands policy scope instead of reducing it;
- durable high-risk governance writes still need explicit approval, but normal
  task-session execution is the default carrier for work.

## Questions To Resolve Later

- Should task-session creation become automatic for mounted task execution, or
  should it remain a guarded write with a lighter approval model?
- Which policies belong to `discussion`, `editing`, `progress_summary`, and
  `other` scopes?
- Should policy definitions express required task classifications directly?
- How should runtime cards explain conservative expansion without overwhelming
  non-engineering users?

## Current Decision

Do not implement this in the current documentation-registry slice.

Record it as a policy-governance task to revisit when JIKUO reaches the policy
trigger / task-session governance section of the transitional task list.
