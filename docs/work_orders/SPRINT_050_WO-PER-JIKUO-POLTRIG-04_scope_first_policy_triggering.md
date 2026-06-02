# SPRINT_050_WO-PER-JIKUO-POLTRIG-04: Scope-First Policy Triggering

> **Status**: Implemented and verified as a compatibility slice.
> **Date**: 2026-06-02
> **JIKUO layer**: policy governance / trigger routing.
> **Business meaning**: Policy triggering is JIKUO's core value. Intent-driven policies must not depend on unstable lifecycle-node invocation such as whether `task_start` or `completion_review` happened to be called. The evaluator must let work-profile scope carry the business trigger while preserving legacy lifecycle-event policies.

---

## 1. Originating Problem

`POLTRIG-03` made `work_profile.lifecycle_event` and
`work_profile.policy_scopes` hard evaluator inputs when a policy declared
`applies_to_work_profile`, but exact trigger events still gated every policy
first.

That left a mismatch:

- current host / MCP surfaces do not guarantee `conversation_turn ->
  task_start -> completion_review` ordering;
- user intent is better represented by policy scope / action grammar than by a
  lifecycle node;
- a scope-only policy such as "editing work should review data-model drift" can
  still be missed if it is declared under `conversation_turn` and the current
  evaluation surface is `task_start`.

This is not a single-policy problem. It is a trigger model problem.

## 2. Accepted Model

JIKUO now distinguishes:

| Concept | Meaning |
|---|---|
| `event` | The current evaluation surface or tool path. It decides when the evaluator runs. |
| `work_profile.lifecycle_event` | The observed user-work node, used only when a policy explicitly declares lifecycle filters. |
| `work_profile.policy_scopes` | The business trigger basis for intent-driven policies. |
| `conditions` | Additional exact filters after applicability has matched. |
| `required_evidence` | The proof that the policy's required action was satisfied, deferred, or not applicable. |

Scope-first policies use:

```yaml
triggers:
  - trigger_id: "TRG-conversation-turn"
    type: "task_lifecycle_event"
    event: "conversation_turn"
applies_to_work_profile:
  - lifecycle_events: []
    policy_scopes: ["editing"]
```

The `conversation_turn` trigger remains a compatibility anchor and default
evaluation surface. It is not the policy's business applicability cause.

Checkpoint policies can still use lifecycle filters:

```yaml
applies_to_work_profile:
  - lifecycle_events: ["completion_review"]
    policy_scopes: ["progress_summary"]
```

Those policies intentionally belong to a lifecycle node and should remain gated
by it.

## 3. Implemented Behavior

The evaluator now uses two trigger modes:

1. `event_exact`: legacy and checkpoint behavior. A policy whose trigger event
   matches the current `event` is evaluated normally.
2. `work_profile_scope`: if no exact event matches and the policy declares
   scope-only applicability (`policy_scopes` present, `lifecycle_events` empty),
   the evaluator uses the declared trigger as an anchor and evaluates
   `work_profile.policy_scopes`.

When a scope-first policy triggers through the second mode, the runtime report
records:

- `trigger_match_mode: "work_profile_scope"`;
- `declared_trigger_event`;
- `evaluation_event`;
- a trigger reason that says the work-profile scope matched during the current
  evaluation surface.

This keeps reports honest: the policy did not trigger because a lifecycle node
matched; it triggered because the work profile matched the policy scope.

## 4. Compatibility

- Policies without `applies_to_work_profile` remain legacy event-exact policies.
- Policies with `applies_to_work_profile.lifecycle_events` remain lifecycle
  filtered.
- Exact `conditions` remain additional filters.
- `intent_class`, `operation_class`, `output_class`, requested outcome,
  execution boundary, and response contract remain projection / evidence fields
  rather than direct evaluator keys.
- Existing active policies are not migrated in this slice.

## 5. Verification

Implemented regression coverage:

- `tests.policy_store_tests.PolicyStoreStatusTests.test_scope_only_work_profile_applicability_does_not_require_event_or_lifecycle_match`
- `tests.agent_flow_tests.AgentFlowProposalTests.test_scope_only_policy_distribution_is_not_blocked_by_task_start_event`

Those tests prove that a policy declared with `conversation_turn` plus
scope-only `policy_scopes: ["editing"]` can trigger from a `task_start`
evaluation surface when the work profile is `editing`.

## 6. Follow-Up

- Update policy writers / templates to describe `conversation_turn` as a
  compatibility anchor for scope-first policies.
- Review active intent-driven policies and migrate only those that should be
  scope-first.
- Add the capability/atom-registration policy as a scope-first editing policy
  after user review.
- Do not broaden evaluator inputs beyond `policy_scopes` and optional
  `lifecycle_events` until runtime evidence shows the MVP scope taxonomy is too
  coarse.
