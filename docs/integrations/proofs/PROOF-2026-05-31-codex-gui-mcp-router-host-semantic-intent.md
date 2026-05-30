# Codex GUI MCP Router Host Semantic Intent Proof

- Date recorded: 2026-05-31
- Observed runtime card timestamp: 2026-05-30T12:58:21Z
- Client: separate Codex GUI session with JIKUO MCP configured
- Project root: `D:\personal_project\Jikuo`
- Proof status: `accepted_cooperative_gui_mcp_router_host_semantic_intent`
- Raw prompt stored: `false`

## Compact Turn Summary

The user asked a separate Codex GUI session to call JIKUO
`route_user_request` and pass compact `host_semantic_intent` for a no-edit
discussion smoke. The tested session reported that the router tool exposed the
`host_semantic_intent` argument and successfully passed a compact host-AI
semantic classification into JIKUO.

This proof accepts the cooperative GUI MCP router path. It does not claim that
the Codex hook automatically generated semantic intent before model work.

## Observed JIKUO Result

History card:

`.jikuo/runtime/history/20260530T125821Z_proposal_eac5ed540d.md`

Observed result:

- `host_semantic_intent` argument visible in `route_user_request`: `true`
- compact semantic intent successfully passed: `true`
- `semantic_intent_status=provided`
- `provider=host_ai`
- `semantic_intent_evidence.status=ok`
- `work_profile.basis.host_semantic_intent.status=provided`
- `work_profile.policy_scopes=discussion`
- triggered policies:
  - `POLICY-jikuo-conversation-level-proactive-policy-suggestion`
  - `POLICY-jikuo-first-principles-critical-alignment`
- missing evidence count: `1`

## Boundary Interpretation

This proof accepts:

- the Codex GUI MCP tool surface can expose `host_semantic_intent` on
  `jikuo.route_user_request`;
- a cooperative host AI can pass compact semantic intent through the MCP router
  tool;
- JIKUO records the semantic intent as provided and marks
  `semantic_intent_classification_evidence` as `ok`;
- policy distribution can use the resulting aggregate `work_profile` scopes.

This proof does not accept:

- automatic hook-time semantic classification;
- MCP Sampling provider support;
- wrapper/plugin provider control;
- host semantic intent being guaranteed on every turn;
- full lifecycle strict-mounted behavior.

## Encoding Note

The pasted proof text showed mojibake for some Chinese `requested_outcome` and
`response_contract` fields. The semantic status and links remained readable.
Treat this as a follow-up encoding/proof-display issue, not as a failed
semantic-intent transport proof.

## Next Required Proof Step

Two follow-up paths remain:

- test whether MCP Sampling can provide semantic intent when the client
  supports `sampling/createMessage`;
- design a wrapper/plugin path that obtains or requires compact semantic
  intent before JIKUO routing when stronger guarantees are needed.
