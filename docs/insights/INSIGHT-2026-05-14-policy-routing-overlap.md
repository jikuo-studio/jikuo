# INSIGHT-2026-05-14: Policy Routing Overlap

> **Classification**: `promoted_to_policy`
> **Status**: resolved
> **Created**: 2026-05-14
> **Related policies**:
> - `.jikuo/policies/approved/POLICY-jikuo-policy-vs-code-before-implementation.yaml`
> - `.jikuo/policies/approved/POLICY-jikuo-development-idea-routing.yaml`
> - `.jikuo/policies/approved/POLICY-jikuo-implementation-intent-routing-before-change.yaml`

## Observation

Two active policies currently trigger on the same broad slice:

- task type: `code_change`
- JIKUO layer: `implementation_governance`
- event: `task_start`

The first policy asks the agent to classify whether a change is governance /
policy or implementation / code before editing.

The second policy asks the agent to classify development ideas into task,
policy, insight, or deferred buckets and update the matching documentation.

## Analysis

The policies are not identical, but their trigger surfaces are overlapping.
That creates two required evidence items for many JIKUO implementation tasks,
even when no new development idea has appeared.

The stronger product shape is probably one combined routing policy:

- classify whether the change is policy, code, docs, task-map work, insight, or mixed
- route each discovered idea to task, policy, insight, or deferred
- require evidence that the matching document surface was updated

## Recommendation

Do not keep both original policies active long term.

Preferred follow-up:

1. Create one superseding policy such as
   `POLICY-jikuo-implementation-intent-routing-before-change`.
2. Move both existing intents into that single policy.
3. Mark `POLICY-jikuo-policy-vs-code-before-implementation` as superseded.
4. Mark `POLICY-jikuo-development-idea-routing` as superseded or deprecated.

If only one current policy can remain active before that consolidation, keep
`POLICY-jikuo-policy-vs-code-before-implementation` active because it is the
broader pre-change guard, and make `POLICY-jikuo-development-idea-routing`
non-active after its intent is folded into the replacement.

## Resolution

Policy-store writes have been performed with explicit user approval:

- activated `POLICY-jikuo-implementation-intent-routing-before-change`
- deprecated `POLICY-jikuo-policy-vs-code-before-implementation`
- deprecated `POLICY-jikuo-development-idea-routing`

The consolidated policy now carries the active intent-routing check.
