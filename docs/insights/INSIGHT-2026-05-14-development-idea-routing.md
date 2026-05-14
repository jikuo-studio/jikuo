# INSIGHT-2026-05-14: Development Idea Routing

> **Classification**: `promoted_to_policy`
> **Status**: superseded
> **Created**: 2026-05-14
> **Related policy**: `.jikuo/policies/approved/POLICY-jikuo-development-idea-routing.yaml`
> **Superseded by**: `.jikuo/policies/approved/POLICY-jikuo-implementation-intent-routing-before-change.yaml`

## Insight

During JIKUO development, new development ideas should not remain only in chat.
They should be classified before they affect the project:

- if the idea changes what should be built, update the task map or create a work order
- if the idea changes how work must be governed, create or update a policy
- if the idea is valuable but not ready for execution, capture it in `docs/insights`

## Why It Matters

JIKUO development creates ideas at the same time as it creates product behavior.
Without a routing rule, useful ideas can become hidden assumptions, accidental
scope creep, or forgotten design context.

## Operational Shape

When a development idea appears:

1. Classify it as `task_candidate`, `policy_candidate`, `insight_only`, or `deferred`.
2. Update the corresponding document surface.
3. Reference the update in the delivery summary.

This insight was first promoted to an approved policy. Its narrower policy was
later deprecated when the intent was folded into the consolidated
implementation-intent routing policy.
