# Codex GUI Hook Current-Thread Observation

- Date: 2026-05-21
- Client: Codex Desktop App
- Project root: `D:\personal_project\Jikuo`
- JIKUO commit under observation: `5c5a9bd`
- Proof status: `accepted_pre_turn_additional_context`
- Full strict lifecycle status: `pending_completion_review_runner`
- Raw prompt stored: `false`

## Compact Turn Summary

The user asked Codex to continue hook-related JIKUO work after the MCP Sampling
semantic-provider probe was committed, then enabled the project-local Codex
`UserPromptSubmit` hook and submitted probe turns to check whether JIKUO
`additionalContext` was visible before the assistant response.

## Expected Strict-Mounted Signal

If the project-local Codex `UserPromptSubmit` hook were loaded, trusted, and
executed before model work for this turn, the hook should have called JIKUO
before the assistant began substantive work and produced a new
`conversation_turn` runtime history card.

The hook should also have injected Codex `additionalContext` containing JIKUO
runtime links, semantic-intent status, triggered-policy count, missing-evidence
count, and required follow-up tools.

## Observed Runtime Evidence

Initial observation before hook enablement showed no automatic hook-produced
pre-turn card before manual JIKUO calls in the assistant workflow.

The first new cards observed after this turn were manual JIKUO calls:

- Conversation routing card:
  `.jikuo/runtime/history/20260521T002618Z_proposal_a72168f994.md`
- Task-start card:
  `.jikuo/runtime/history/20260521T002718Z_proposal_dd4b032caf.md`

These cards prove manual JIKUO invocation from the assistant workflow, not
Codex GUI strict-mounted behavior.

After the user enabled the project-local hook in Codex Settings -> Hooks, the
next turn did inject a visible hook degradation context:

```text
JIKUO mounted pre-turn failed or degraded before substantive model work.
Failure summary: JIKUO command timed out
```

This proved Codex GUI did load and execute the `UserPromptSubmit` hook, but the
JIKUO command did not complete in the configured timeout. It was not accepted
as successful pre-turn JIKUO execution because no successful JIKUO card was
mounted before model work.

The timeout remediation is to increase the hook-owned JIKUO subprocess timeout
to 70 seconds and the Codex hook wrapper timeout to 90 seconds, then rerun a
fresh GUI probe.

## Local Remediation Smoke

After the timeout change, a local stdin hook smoke succeeded and returned
`hookSpecificOutput.additionalContext` with a JIKUO history card:

- `.jikuo/runtime/history/20260521T004612Z_proposal_264d3469ea.md`

This confirms the hook script still works locally after the timeout change. It
did not replace the required Codex GUI proof.

## Fresh Codex GUI Probe After Timeout Remediation

The user then submitted a fresh Codex GUI probe turn and asked the assistant to
only confirm whether JIKUO `additionalContext` was visible. The assistant saw
successful injected context before answering.

Observed injected context included:

- `JIKUO mounted pre-turn ran before substantive model work.`
- `Trigger mode: mounted.`
- `Semantic intent status: unavailable.`
- `Work profile: lifecycle_event=conversation_turn; policy_scopes=discussion.`
- `Triggered policy count: 1.`
- `Missing evidence report count: 0.`
- History card:
  `.jikuo/runtime/history/20260521T004612Z_proposal_264d3469ea.md`

This accepts the Codex GUI `UserPromptSubmit` hook as a working pre-turn
additional-context injection path for this project-local proof configuration.
It does not prove host-time AI semantic routing, multi-intent semantic slicing,
or the future full lifecycle runner.

## Result

- Pre-turn hook invocation proven: `accepted`
- Injected `additionalContext` proven visible to Codex before work: `accepted`
- Host-time semantic provider proven: `false`
- Strict-mounted pre-turn surface: `accepted_for_project_local_codex_hook`
- Full lifecycle strict-mounted acceptance: `pending_completion_review_runner`

## Next Required Proof Step

Use a trusted Codex GUI environment that explicitly enables project-local hooks,
then record the remaining lifecycle and semantic-provider proof steps:

- a later `completion_review` card for the same governed work once the
  lifecycle runner exists;
- semantic-intent status as `provided`, `unavailable`, `invalid`, or
  `heuristic_fallback` when a host-time provider or classifier is available;
- multi-intent slice handling when the user turn contains more than one
  meaningful intent.

Only that end-to-end observation can promote Codex GUI from accepted pre-turn
additional-context proof to full strict-mounted lifecycle behavior.
