# INSIGHT-2026-05-14: Harness Card Surfacing Gap

> **Classification**: `promoted_to_task`
> **Status**: promoted
> **Created**: 2026-05-14
> **Related policy**: `.jikuo/policies/approved/POLICY-jikuo-deterministic-harness-chat-return.yaml`

## Observed Situation

After `JIKUO-CORE-24`, `agent_flow.py` could generate visible markdown cards for
template import planning and policy runtime status. The assistant still replied
with a normal summary and did not paste the generated card back to the user.

The card existed in the runner output, but the user could not perceive it in the
desktop chat.

## Analysis

This exposes a product gap between three layers:

- kernel capability: `agent_flow.py` can generate cards and `chat_ready_markdown`
- bridge surface: current desktop workflow still invokes the runner through CLI
- enforcement layer: the assistant is not yet forced by MCP or another wrapper to
  return `chat_ready_markdown` as the primary artifact

The existing deterministic-harness policy can detect that card surfacing is a
required action. It cannot by itself prevent a non-wrapped assistant response
from summarizing the result away.

## Classification

This has been promoted from a `task_candidate` into pre-MCP task-map work.

The policy principle already exists:

- JIKUO is a deterministic harness once activated.
- Policy runtime status and cards must be visible and auditable.

The missing work is implementation / integration across general layers:

- out-of-band runtime files / CLI that users can inspect without client cooperation
- MCP display-card tools and display directives that make omission easy to notice
- universal instruction files that describe the display contract for multiple agents

## Follow-Up Candidate

Promoted tasks:

- `JIKUO-LIVE-12`: out-of-band runtime visibility channels.
- `JIKUO-MCP-01`: runtime status card / display-card MCP tools and display directives.
- `JIKUO-INTG-01`: universal instruction file distribution.

Dashboard, OS notifications, and per-client packs remain follow-up layers unless
the user explicitly promotes them.
