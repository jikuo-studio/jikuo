# JIKUO Codex Hook Proof

This directory contains the project-local Codex `UserPromptSubmit` proof hook.
It is a thin adapter, not a policy engine.

The hook does four things:

1. Reads minimal Codex hook input from stdin.
2. Locates the project root and normalizes the turn through
   `jikuo.host_adapter.turn_input.v0`.
3. Calls JIKUO no-write `conversation_turn` routing. By default this uses the
   in-process `jikuo.agent_flow` API to avoid GUI nested-Python subprocess
   hangs; `JIKUO_HOOK_EXECUTION_MODE=subprocess` keeps the old CLI path for
   diagnostics.
4. Returns Codex `hookSpecificOutput.additionalContext` with JIKUO card links,
   policy counts, missing evidence counts, the next required actions, and a
   `jikuo.host_adapter.turn_result.v0` summary.

It does not create task sessions, policies, evidence records, commits, or proof
notes. Durable writes remain behind guarded JIKUO commands.

## Current Proof Level

This is a Level 1 mounted invocation proof plus a local Level 2A semantic-input
transport path:

- `UserPromptSubmit` should run before substantive Codex model work.
- JIKUO should produce a `conversation_turn` runtime card.
- Codex should receive the card links through `additionalContext`.
- The project-local hook should consume the shared Host Adapter Turn
  Input/Result contract before rendering Codex-specific context.
- If hook stdin contains compact `host_semantic_intent` /
  `hostSemanticIntent`, the hook forwards it to JIKUO for final work-profile
  projection.
- If no compact semantic intent is supplied, `semantic_intent_status` is
  reported as `unavailable`.

Do not claim Codex GUI AI-semantic routing from this hook. The current code can
transport and label semantic intent, but it does not generate host-time AI
classification by itself. A real GUI proof must still show whether Codex can
provide that semantic object before JIKUO runs.

The project-local Codex GUI proof has shown that `additionalContext` can be
injected before the assistant answer. A 2026-05-28 GUI probe also showed that
the old nested-Python subprocess path can time out even when the hook itself is
loaded and visible, so the hook now defaults to in-process JIKUO invocation.
Fresh GUI acceptance after this remediation is now accepted for the pre-turn
additional-context surface. Linked completion-review, semantic-provider, and
multi-intent proofs remain pending.

## Privacy Boundary

The hook does not write the raw prompt or transcript to hook-owned files. The
prompt is passed transiently to the local JIKUO in-process API by default. In
explicit subprocess diagnostic mode, it is passed to the local CLI over stdin
with `--user-phrase-stdin`, so the raw prompt is not placed in the child
process argument list. A later reusable adapter can still replace the
project-local API call with MCP or another host-provided boundary.

Compact `host_semantic_intent` is passed through the CLI argument list when
present. That object must contain only classification metadata and compact
rationale, never the raw prompt or transcript.

## Configuration

The project-local hook is registered by `.codex/hooks.json`.

Codex must trust the project `.codex/` layer before non-managed hooks run. Use
the Codex hook review UI or `/hooks` in CLI builds that expose it.

Optional environment variables:

- `JIKUO_HOOK_PYTHON`: Python executable used to invoke JIKUO. Defaults to the
  interpreter running the hook. This only applies in subprocess diagnostic
  mode.
- `JIKUO_HOOK_EXECUTION_MODE`: `in_process` by default; set to `subprocess` or
  `cli` only for diagnostics.
- `JIKUO_HOOK_TRIGGER_MODE`: trigger mode passed to JIKUO. Defaults to
  `mounted`.
- `JIKUO_HOOK_TIMEOUT_SECONDS`: subprocess timeout. Defaults to `70` and only
  applies in subprocess diagnostic mode. The project-local Codex hook wrapper
  currently allows `90` seconds so a cold Python/JIKUO startup can finish
  before Codex reports hook failure.

## Acceptance Boundary

This file existing in the repository is not proof by itself. A Codex GUI
pre-turn surface proof is accepted only after a real prompt shows:

- the hook ran before model work;
- a new `.jikuo/runtime/history/*.md` card was produced;
- Codex received `additionalContext` with runtime links;
- failure is visible rather than silent;

Full strict-mounted lifecycle proof additionally needs a later
completion-review card linked before final delivery.
