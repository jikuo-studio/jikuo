# Codex GUI Hook Subprocess Timeout Observation

- Date: 2026-05-28
- Client: Codex Desktop App
- Project root: `D:\personal_project\Jikuo`
- Proof status: `accepted_in_process_pre_turn_additional_context`
- Fresh in-process remediation status: `accepted`
- Raw prompt stored: `false`

## Compact Turn Summary

The user refreshed and trusted the Codex project-local hook, then submitted a
hook trigger smoke prompt. Codex showed JIKUO `additionalContext`, proving that
the GUI loaded and ran the hook, but the context was degraded:

```text
JIKUO command timed out after 70s; python=C:\Python314\python.exe
```

This means the host-boundary invocation surface worked, while the nested
Python subprocess used by the hook was not stable enough as the default GUI
execution path.

## Boundary Interpretation

This observation proves:

- Codex GUI can load the project-local `UserPromptSubmit` hook after trust;
- the hook can inject visible `additionalContext` before the assistant answer;
- failures are visible rather than silent.

This observation does not prove:

- successful JIKUO no-write routing for that GUI turn;
- host-time AI semantic intent;
- multi-intent semantic routing;
- full lifecycle strict-mounted behavior.

## Remediation

The project-local hook now defaults to in-process JIKUO invocation:

- call `jikuo.agent_flow.build_proposal(...)`;
- wrap it with `jikuo.agent_flow.proposal_with_chat_ready_markdown(...)`;
- keep subprocess CLI only as an explicit diagnostic mode with
  `JIKUO_HOOK_EXECUTION_MODE=subprocess`.

The privacy boundary is unchanged: the hook must not persist the raw prompt or
transcript in hook-owned files. In-process mode passes the prompt transiently
in memory; subprocess diagnostic mode passes it over stdin, not as a command
argument.

## Fresh GUI Probe After In-Process Remediation

After the hook default changed from nested Python subprocess to in-process
JIKUO invocation, the user submitted fresh Codex GUI smoke turns. Codex showed
successful injected JIKUO context before the assistant response.

Observed injected context included:

- `JIKUO mounted pre-turn ran before substantive model work.`
- `Trigger mode: mounted.`
- `Semantic intent status: unavailable.`
- `Work profile: lifecycle_event=conversation_turn; policy_scopes=discussion.`
- `Triggered policy count: 2.`
- `Missing evidence report count: 1.`
- History card:
  `.jikuo/runtime/history/20260528T111346Z_proposal_264d3469ea.md`

This accepts the in-process project-local Codex `UserPromptSubmit` hook path as
a working pre-turn additional-context injection path for this repository.

It still does not prove host-time AI semantic routing, multi-intent semantic
slicing, or full lifecycle strict-mounted behavior.

## Next Required Proof Step

Record a later completion-review card for the same governed work once the
accepted lifecycle proof path is exercised. A degraded timeout message should
remain treated as a failed proof for any future subprocess diagnostic path.
