# Explicit Host AI Semantic Intent Provider Proof

- Date: 2026-05-30
- Client: Codex Desktop App
- Project root: `D:\personal_project\Jikuo`
- Proof status: `accepted_explicit_host_ai_semantic_intent_transport`
- Raw prompt stored: `false`

## Compact Turn Summary

The user asked Codex to commit any current changes and continue work. No
uncommitted changes were present. Codex, acting as the host AI inside the
development session, classified the turn as an editing plus progress-summary
request and passed a compact `host_semantic_intent` object into JIKUO.

This proof does not rely on the Codex hook generating semantic intent before
the model runs. It proves the cooperative explicit-provider path: when the host
AI supplies compact semantic intent, JIKUO accepts, normalizes, displays, and
uses it for policy distribution through existing `policy_scopes`.

## Observed JIKUO Result

History card:

`.jikuo/runtime/history/20260530T090029Z_proposal_8156c71d76.md`

Observed result:

- `semantic_intent_status=provided`
- `provider=codex_host_ai_explicit`
- `work_profile.policy_scopes=editing,progress_summary`
- triggered policies:
  - `POLICY-jikuo-conversation-level-proactive-policy-suggestion`
  - `POLICY-jikuo-data-model-drift-alarm`
- missing evidence count: `0`

The proof supplied `data_model_boundary_review_evidence` because the explicit
editing scope correctly triggered the data-model boundary policy. The evidence
recorded that this proof does not add schema fields, does not expand evaluator
inputs, and uses existing policy-scope matching only.

## Boundary Interpretation

This proof accepts:

- the explicit host-AI semantic-intent transport path;
- JIKUO work-profile projection with `semantic_intent_status=provided`;
- policy distribution from compact semantic scope through existing evaluator
  inputs.

This proof does not accept:

- automatic Codex GUI hook semantic classification;
- host-time provider enforcement before model work;
- MCP Sampling client support;
- wrapper/plugin provider control;
- full lifecycle strict-mounted behavior.

## Next Required Proof Step

Verify a client-mediated provider path:

- MCP Sampling returns `sampling_semantic_intent.status=provided`; or
- a wrapper/plugin obtains compact semantic intent before JIKUO routing.

Until then, deterministic fallback remains honest fallback, and explicit
host-AI semantic intent remains a cooperative development-session path rather
than a forced GUI hook capability.
