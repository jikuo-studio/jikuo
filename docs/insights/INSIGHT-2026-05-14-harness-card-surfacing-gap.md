# INSIGHT-2026-05-14: Harness Card Surfacing Gap

> **Classification**: `task_candidate`
> **Status**: captured
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

This is a `task_candidate`, not a new policy candidate yet.

The policy principle already exists:

- JIKUO is a deterministic harness once activated.
- Policy runtime status and cards must be visible and auditable.

The missing work is likely implementation / integration:

- MCP wrapper or equivalent desktop-agent wrapper should make `chat_ready_markdown`
  the mandatory returned artifact.
- The agent instruction pack may need a stricter response checklist, but that
  remains weaker than tool-level enforcement.

## Follow-Up Candidate

Potential task:

- `JIKUO-LIVE-12` or `JIKUO-MCP-01` sub-slice: enforce chat-ready card surfacing
  at the client/tool boundary so runner output cannot be silently summarized.

This insight should remain captured until the next task-map review decides
whether to promote it into an active work order.
