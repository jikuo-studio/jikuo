# JIKUO Codex Hook Proof

This directory contains the project-local Codex `UserPromptSubmit` proof hook.
It is a thin adapter, not a policy engine.

The hook does four things:

1. Reads minimal Codex hook input from stdin.
2. Locates the project root.
3. Calls `python -B -m jikuo.agent_flow propose --event conversation_turn` in
   no-write mode.
4. Returns Codex `hookSpecificOutput.additionalContext` with JIKUO card links,
   policy counts, missing evidence counts, and the next required actions.

It does not create task sessions, policies, evidence records, commits, or proof
notes. Durable writes remain behind guarded JIKUO commands.

## Current Proof Level

This is a Level 1 mounted invocation proof:

- `UserPromptSubmit` should run before substantive Codex model work.
- JIKUO should produce a `conversation_turn` runtime card.
- Codex should receive the card links through `additionalContext`.
- `semantic_intent_status` is reported as `unavailable`.

Do not claim AI-semantic routing from this hook. A later slice must add a
host-semantic-intent or dedicated semantic-classifier input before JIKUO can
prefer AI semantics over deterministic fallback.

## Privacy Boundary

The hook does not write the raw prompt or transcript to hook-owned files. The
prompt is passed transiently to the local JIKUO CLI over stdin with
`--user-phrase-stdin`, so the raw prompt is not placed in the child process
argument list. A later reusable adapter can still replace the CLI hop with an
MCP or in-process API call when the host provides a reliable boundary.

## Configuration

The project-local hook is registered by `.codex/hooks.json`.

Codex must trust the project `.codex/` layer before non-managed hooks run. Use
the Codex hook review UI or `/hooks` in CLI builds that expose it.

Optional environment variables:

- `JIKUO_HOOK_PYTHON`: Python executable used to invoke JIKUO. Defaults to the
  interpreter running the hook.
- `JIKUO_HOOK_TRIGGER_MODE`: trigger mode passed to JIKUO. Defaults to
  `mounted`.
- `JIKUO_HOOK_TIMEOUT_SECONDS`: subprocess timeout. Defaults to `20`.

## Acceptance Boundary

This file existing in the repository is not proof by itself. A Codex GUI proof
is accepted only after a real prompt shows:

- the hook ran before model work;
- a new `.jikuo/runtime/history/*.md` card was produced;
- Codex received `additionalContext` with runtime links;
- failure is visible rather than silent;
- a later completion-review card is linked before final delivery.
