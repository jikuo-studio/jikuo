# Runtime Card UTF-8 Semantic Field Proof

- Date recorded: 2026-05-31
- Client path: local SDK-free MCP adapter smoke
- Project root: temporary local project
- Proof status: `accepted_runtime_card_utf8_semantic_fields`
- Raw prompt stored: `false`

## Compact Turn Summary

The previous cooperative Codex GUI MCP router proof showed mojibake in pasted
Chinese `requested_outcome` and `response_contract` text. This smoke checks
whether JIKUO itself corrupts those fields when rendering and writing runtime
cards.

The smoke called `jikuo.route_user_request` with compact
`host_semantic_intent` containing Chinese semantic contract fields, then read
the generated `.jikuo/runtime/last_card.md` back as UTF-8.

## Observed JIKUO Result

Observed result:

- response `card_markdown` contained the Chinese `requested_outcome`: `true`
- written `last_card.md` contained the Chinese `requested_outcome`: `true`
- written `last_card.md` contained the Chinese `response_contract`: `true`
- `work_profile.basis.host_semantic_intent.status=provided`
- `semantic_intent_evidence.status=ok`

Regression coverage:

- `tests.mcp_adapter_tests.MCPStageAAdapterTests.test_route_user_request_preserves_utf8_semantic_contract_fields`

## Boundary Interpretation

This proof accepts:

- JIKUO runtime-card rendering preserves UTF-8 semantic contract fields;
- `.jikuo/runtime/last_card.md` is written in UTF-8 for these fields;
- the observed mojibake is more likely in the external GUI paste / terminal /
  attachment display chain than in JIKUO runtime storage.

This proof does not accept:

- every downstream GUI, terminal, clipboard, or attachment viewer rendering
  UTF-8 correctly;
- automatic hook-time semantic classification;
- MCP Sampling provider support.

## Next Required Proof Step

If mojibake appears again, capture the same card path and compare:

- direct UTF-8 read of `.jikuo/runtime/last_card.md`;
- the GUI-displayed text;
- the pasted/attached text.

Only treat it as a JIKUO runtime bug if the direct UTF-8 file read is already
corrupted.
