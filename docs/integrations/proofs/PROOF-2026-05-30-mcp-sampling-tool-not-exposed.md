# MCP Sampling Tool Not Exposed Observation

- Date: 2026-05-30
- Client: separate Codex / AI GUI session with JIKUO MCP configured
- Project root: `D:\personal_project\Jikuo`
- Proof status: `not_accepted_tool_not_exposed`
- Raw prompt stored: `false`

## Compact Turn Summary

The user asked another AI GUI session to test MCP Sampling by calling
`jikuo.probe_sampling_semantic_intent`. That session reported that the tool was
not present in its available MCP tool surface.

Reported result:

- tool exists in that session: `false`
- `sampling_semantic_intent.status`: `unavailable`
- `host_semantic_intent.status`: `unavailable`
- semantic provider: `unavailable`
- `work_profile.policy_scopes`: `discussion, progress_summary`
- history card:
  `.jikuo/runtime/history/20260530T090824Z_proposal_264d3469ea.md`
- raw prompt leakage observed: `false`

## Local Source Check

The repository source at this point exposes the Sampling probe in the MCP
schema inventory:

- local exposed tool count: `19`
- `jikuo.probe_sampling_semantic_intent` present in local
  `schemas.EXPOSED_TOOL_NAMES`: `true`

This means the external observation is not evidence that JIKUO source lacks the
Sampling probe. It is evidence that the tested client session did not expose
the current MCP tool surface.

## Boundary Interpretation

This observation accepts:

- the tested client did not expose `jikuo.probe_sampling_semantic_intent`;
- no Sampling provider proof was produced by that session;
- the returned routing remained deterministic/fallback with semantic status
  unavailable.

This observation does not accept:

- MCP Sampling unsupported by the client protocol in general;
- JIKUO Sampling probe failure;
- host-time AI semantic routing;
- wrapper/plugin provider behavior.

The next diagnostic step is MCP client/tool-surface refresh, not semantic model
quality debugging.

## Next Required Proof Step

Before testing Sampling itself, refresh or restart the target MCP client/server
and verify that the client tool inventory includes
`jikuo.probe_sampling_semantic_intent`.

Only after the tool is visible should the user run the Sampling smoke again and
classify the result as:

- `provided`: client-mediated semantic provider works;
- `unavailable`: tool exists, but client rejects or lacks Sampling support;
- `invalid`: client returns malformed semantic JSON.
