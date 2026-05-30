# SPRINT_050_WO-PER-JIKUO-AI-SEMROUTE-01: AI Semantic Routing MVP

> **Status**: Design accepted; first projection slice implemented for short `user_expression`, MVP scope filtering, ordered `intent_slices` card rendering, Codex hook wording, no-write smoke for `semantic_intent_status=provided`, raw `user_phrase` redaction in trigger/router projections, local policy-distribution proof that host semantic scopes select different scope-aware policies, and explicit Codex-host-AI semantic-intent transport proof. Real automatic GUI / MCP semantic provider smoke and any evaluator expansion remain pending.
> **Date**: 2026-05-28
> **JIKUO layer**: integration / policy distribution.
> **Business meaning**: JIKUO should stay thin. The host AI understands the user's natural-language intent; JIKUO receives a compact semantic object, records it, explains policy routing, and keeps deterministic fallback honest.

## 1. Purpose

AI semantic routing is not a request to make the JIKUO server into another
general-purpose model. The MVP establishes a stable contract:

```text
host AI understands the user turn
-> host AI provides compact host_semantic_intent
-> JIKUO normalizes, displays, records, and merges it into work_profile
-> policy distribution continues through stable policy scopes
```

The design keeps the shell thin and lets model capability remain where it
already exists: in Codex, Claude, a client-mediated Sampling provider, or a
future wrapper / plugin.

## 2. Non-Goals

- Do not claim every GUI turn already includes host AI semantic intent.
- Do not claim MCP server code can control what the host AI thinks before the
  host calls MCP.
- Do not build a separate correction / reroute workflow for misclassification.
- Do not expand the MVP `policy_scopes` taxonomy.
- Do not make `intent_slices`, `requested_outcome`, `execution_boundary`, or
  `response_contract` direct policy-evaluator inputs in this slice.

## 3. Input Source Model

The MVP recognizes three input paths:

| Path | Meaning | Status |
|---|---|---|
| Host-provided semantic intent | The host AI supplies `host_semantic_intent` when invoking JIKUO. | Main contract. Soft-guaranteed until a wrapper / plugin controls the host flow. |
| MCP Sampling | JIKUO asks a Sampling-capable MCP client for a compact semantic classification during a tool call. | Enhancement path. Not pre-MCP and not strict mounted proof. |
| Deterministic fallback | JIKUO uses keyword, path, tool, and explicit event signals. | Honest fallback and conflict evidence, not AI semantic routing. |

Codex hook `additionalContext` can prompt the host AI to provide semantic
intent in future calls, but the hook itself does not make the host AI classify
the turn before the model sees it. A wrapper / plugin is more stable because it
can control the host event pipeline:

```text
user submits turn
-> wrapper / plugin runs classifier
-> wrapper / plugin calls JIKUO with host_semantic_intent
-> wrapper / plugin injects JIKUO card links / next actions
-> host AI performs the task
```

The current MVP should therefore prove the input contract before heavier
wrapper / plugin work.

`JIKUO-HOSTADAPT-01` defines that input contract at the cross-client adapter
layer. AI semantic routing should reuse `jikuo.host_adapter.turn_input.v0` for
host input normalization and keep `host_semantic_intent` as compact classifier
evidence inside that envelope.

## 4. Host Semantic Intent Shape

Minimum accepted shape:

```yaml
host_semantic_intent:
  schema: "jikuo.host_semantic_intent.v0"
  provider: "codex" # codex | claude | mcp_sampling | manual_test | other
  status: "provided" # provided | unavailable | heuristic_fallback
  confidence: "medium" # low | medium | high | unavailable
  policy_scopes:
    - "discussion"
  intent_slices:
    - index: 1
      user_expression: "short user phrase, not the full prompt"
      policy_scopes: ["discussion"]
      requested_outcome: "what result the user wants"
      execution_boundary: "allowed / blocked effects or approval boundaries"
      response_contract: "what the final answer must report"
```

`user_expression` may be rendered in runtime cards, but it must be a short
phrase or compact excerpt. Do not persist the full prompt or raw transcript as
semantic proof.

## 5. Scope Taxonomy

MVP `policy_scopes` stay limited to:

```text
discussion
editing
progress_summary
```

Do not add `planning`, `review`, `verification`, `distribution`,
`first_principles_alignment`, or `data_model_boundary_review` as MVP scopes.
Those are policy names, process contracts, evidence types, or output contracts,
not routing categories.

Examples:

- `POLICY-jikuo-first-principles-critical-alignment` belongs to
  `discussion`;
- `POLICY-jikuo-data-model-drift-alarm` belongs to `editing`.

## 6. Multi-Intent Turns

One user turn may contain multiple intents. Represent them as ordered
`intent_slices`:

```yaml
intent_slices:
  - index: 1
    user_expression: "review the data-model policy"
    policy_scopes: ["discussion"]
    requested_outcome: "decide whether it is suitable as optional_template"
    execution_boundary: "no durable write before approval"
    response_contract: "explain recommendation, risks, and next step"
  - index: 2
    user_expression: "if suitable, produce distribution review"
    policy_scopes: ["editing"]
    requested_outcome: "produce no-write distribution review"
    execution_boundary: "guarded write only after approval"
    response_contract: "include policy ref, decision, evidence, and card links"
```

The host AI owns the slice order. JIKUO records and explains the order, but it
does not automatically orchestrate every slice in this MVP.

Aggregate `work_profile.policy_scopes` should be the union of valid slice
scopes, unless explicit negative constraints remove or gate a scope.

## 7. Evaluator Boundary

MVP evaluator inputs remain intentionally narrow:

```text
consumed by evaluator:
- final lifecycle_event
- aggregate policy_scopes
- existing exact conditions

not directly consumed by evaluator in this MVP:
- intent_slices
- user_expression
- requested_outcome
- execution_boundary
- response_contract
```

The richer fields are consumed by router explanation, runtime cards, planning,
required actions, response obligations, and evidence checks. They should prove
usefulness before they become evaluator inputs.

## 8. How "Think / Speak" Policies Land

Rules about how the AI should think or speak are policies, not classification
labels. When such a policy triggers, it should be visible in three places:

1. Runtime card: why the policy triggered and which intent slice it relates to.
2. Evidence: a compact evidence item such as
   `first_principles_alignment_evidence` or
   `data_model_boundary_review_evidence`.
3. Final response: the answer actually follows the required reasoning or
   reporting contract.

This does not prove private cognition. It proves observable behavior:
alignment, critique, boundary review, explanation, and evidence reporting.

## 9. Misclassification Handling

Do not build a dedicated correction workflow for the MVP. If the user notices
misclassification, the user naturally corrects it in the next turn. That next
turn is an ordinary `conversation_turn`, and the host AI / JIKUO route again.

Old classifications remain in runtime history as the prior projection. They do
not need rollback unless later evidence shows normal follow-up turns are
insufficient.

## 10. Acceptance Criteria

MVP design acceptance requires:

- documentation states that hook `additionalContext` does not itself guarantee
  host-time semantic classification;
- documentation states that MCP Sampling is an enhancement path, not strict
  mounted proof;
- `host_semantic_intent` shape keeps short `user_expression` and does not store
  raw prompts;
- `policy_scopes` remain `discussion`, `editing`, and `progress_summary`;
- multi-intent turns use ordered `intent_slices`;
- evaluator consumption stays limited to final lifecycle event, aggregate
  scopes, and existing exact conditions;
- future wrapper / plugin work reuses the same `host_semantic_intent` contract.

## 11. Next Implementation Slice

The first code slice did not change policy evaluator behavior. It verified the
existing host-semantic-intent pipeline against this MVP contract:

- `work_profile.normalize_host_semantic_intent` keeps `user_expression` as a
  short projection and filters `policy_scopes` to the MVP taxonomy;
- `agent_flow` Work Profile Markdown renders ordered `intent_slices` with
  scope, short expression, requested outcome, execution boundary, and response
  contract details when present;
- the Codex `UserPromptSubmit` hook `additionalContext` tells the host AI how
  to pass compact `host_semantic_intent` later without claiming the hook itself
  forces host-time classification;
- focused tests cover short expression preservation, invalid scope filtering,
  multi-intent order preservation, and raw prompt omission from hook output.

Follow-up smoke in this slice verified that a compact `host_semantic_intent`
can project `semantic_intent_status=provided`, aggregate MVP scopes, and ordered
intent slices while redacting the raw `user_phrase` from trigger/router
projections. The runtime card may render short `user_expression` values, but
`trigger_decision.user_phrase` and `conversation_router.input_summary` must
remain `<redacted_user_phrase>` when the source is the current user prompt.

Follow-up distribution proof verified that the compact semantic object is
consumed, not merely displayed. The regression
`tests.agent_flow_tests.AgentFlowProposalTests.test_host_semantic_intent_scopes_change_policy_distribution`
uses the same user phrase with two different host-provided semantic scopes:

- `policy_scopes=["discussion"]` triggers
  `POLICY-jikuo-first-principles-critical-alignment`;
- `policy_scopes=["editing"]` triggers
  `POLICY-jikuo-data-model-drift-alarm`.

This proves the current MVP consumption path:

```text
host_semantic_intent.policy_scopes
-> work_profile.policy_scopes
-> existing policy applies_to_work_profile scope match
-> different triggered policy set
```

This is still not host-time AI semantic-provider acceptance. The test supplies
a compact semantic object directly to JIKUO; a future GUI / wrapper / Sampling
proof must show how that object is produced by the host or client.

An explicit host-AI provider proof was accepted on 2026-05-30:

- Proof note:
  `docs/integrations/proofs/PROOF-2026-05-30-explicit-host-ai-semantic-intent.md`;
- Runtime card:
  `.jikuo/runtime/history/20260530T090029Z_proposal_8156c71d76.md`;
- Provider: `codex_host_ai_explicit`;
- Status: `semantic_intent_status=provided`;
- Result: `work_profile.policy_scopes=editing,progress_summary`;
- Triggered policies:
  `POLICY-jikuo-conversation-level-proactive-policy-suggestion` and
  `POLICY-jikuo-data-model-drift-alarm`;
- Missing evidence count: `0`.

This proves a cooperative explicit-provider path in which the host AI
classifies the user turn and passes compact semantic intent when invoking
JIKUO. It still does not prove that the Codex GUI hook can automatically obtain
semantic intent before the model runs.

An external MCP Sampling smoke attempt on 2026-05-30 did not reach Sampling
itself because the target client session did not expose
`jikuo.probe_sampling_semantic_intent`. The repository source exposed 19 MCP
tools locally and included the probe in `schemas.EXPOSED_TOOL_NAMES`, so the
observation is recorded as client/tool-surface-not-exposed rather than
Sampling-provider failure:

- Proof note:
  `docs/integrations/proofs/PROOF-2026-05-30-mcp-sampling-tool-not-exposed.md`;
- Reported history card:
  `.jikuo/runtime/history/20260530T090824Z_proposal_264d3469ea.md`;
- Reported semantic status: `unavailable`;
- Next diagnostic: refresh or restart the target MCP client/server until the
  probe tool is visible, then rerun the Sampling smoke.

Remaining implementation work:

- run GUI / MCP smoke tests with automatic host-provided or Sampling-provided
  semantic intent, not only local no-write or cooperative explicit-provider
  semantic objects;
- decide whether wrapper / plugin work should make host-time classification
  mandatory before JIKUO invocation;
- keep richer fields out of evaluator inputs until real smoke evidence shows a
  need for more than aggregate `policy_scopes`.
