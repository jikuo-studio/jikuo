# INSIGHT-2026-05-16: Proactive Policy Suggestion Metapolicy

> **Classification**: promoted_to_policy
> **Status**: resolved
> **Related policy**: `.jikuo/policies/approved/POLICY-jikuo-conversation-level-proactive-policy-suggestion.yaml`

## Observation

Some user needs appear first as repeated interaction patterns rather than as
explicit policy requests.

In the current JIKUO development thread, the user repeatedly asked for progress,
remaining todo items, and the business meaning behind technical tasks. That
pattern is not just a one-time formatting preference. It reveals a stable
working need: technical implementation status should be translated into product
or business meaning so the user can steer development without decoding internal
engineering language.

If JIKUO waits for the user to say "please make this a policy," it misses one of
the most useful governance moments. The assistant should notice repeated
friction, preference, clarification, or correction patterns and propose a policy
candidate for review.

## Metapolicy Shape

The useful policy is not to automatically write every inferred preference. The
useful policy is to require the agent to produce a reviewable policy suggestion
when repeated interaction evidence is strong enough.

The suggestion should include:

- the repeated user pattern that triggered the suggestion
- the proposed policy text
- the intended scope
- likely benefits
- possible side effects or overreach
- a clear choice to approve, revise, defer, record as insight, or ignore

This keeps the user in control while still letting JIKUO learn from the way work
actually unfolds.

## Boundaries

The agent must not:

- store raw chat transcripts as policy evidence by default
- treat a single casual preference as a durable rule
- write or activate an inferred policy without explicit user approval
- hide the difference between a policy candidate, insight, follow-up, and task
- turn temporary emotional tone into a permanent governance rule

The agent may:

- use explicit user-provided summaries of repeated patterns
- cite compact, non-sensitive interaction summaries
- propose a policy candidate in chat
- register the idea as an insight if the user is not ready to make it active

## Example

Repeated user pattern:

- the user asks for progress summaries several times
- the user asks that todo items be connected to business meaning
- the user says technical wording alone is hard to follow

Potential policy candidate:

```text
When reporting JIKUO progress, taskmap status, next steps, or acceptance
results, the agent should include the business meaning of each major item and
avoid only reporting implementation mechanics.
```

## Routing Decision

This insight was first promoted into an active report-only self-bootstrap policy:

- `POLICY-jikuo-proactive-policy-suggestion-metapolicy`

That first policy made the review obligation visible at task start. It was later
superseded by:

- `POLICY-jikuo-conversation-level-proactive-policy-suggestion`

The current policy is intentionally report-only and now triggers on
`conversation_turn`. It does not implement automatic session mining, background
polling, or policy activation.

Future product work may add a structured policy-suggestion feature, but that is
separate from this policy activation.

## Follow-up Finding: Trigger Scope Is Too Narrow

The first active policy is useful as a report-only carrier, but it is not enough
for the product behavior the user actually wants.

The user clarified that policy extraction can happen during any interaction with
an AI, not only during task start or implementation work. A repeated request for
progress, todo items, and business meaning is itself a policy-candidate signal
when it appears across turns.

That means the stable implementation should not be "add more task-start
phrasing." It should introduce a conversation-level routing layer:

- semantic mode: the desktop Agent calls JIKUO when natural-language intent seems
  relevant
- mounted harness mode: once selected, JIKUO runs before every user turn and
  returns an explicit router / policy status result, including no-op results
- conversation-turn router: classifies ordinary user turns into task, policy,
  insight, follow-up, deferred, or no-op obligations
- policy-suggestion review: creates compact evidence and reviewable policy
  candidates without storing raw chat transcripts

The conversation-turn event and router contract now exist, and the task-start
policy has been superseded by a conversation-level policy. The core product gap
for policy evidence has been closed by `CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01`:
every `conversation_turn` proposal now emits compact
`proactive_policy_suggestion_review_evidence` and a candidate/no-candidate card
without relying on final prose or raw transcript capture.

The remaining gap is product surfacing: MCP, SDK, and mounted-harness adapters
still need first-class router / policy-suggestion tools so clients can call this
path consistently.
