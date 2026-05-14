# SPRINT_050_WO-PER-JIKUO-LIVE-12: Out-of-band Runtime Visibility Channels

> **Status**: Draft, pre-MCP blocker for visibility foundation
> **Product meaning**: make JIKUO runtime status independently visible even when a desktop Agent fails to paste a card into chat.
> **Scope rule**: add user-accessible runtime visibility channels; do not implement MCP, dashboard UI, OS notifications, gates, or broad action execution in Phase 1.

## 1. Why This Slice Now

`JIKUO-LIVE-10` and `JIKUO-LIVE-11` made policy runtime cards and `chat_ready_markdown` available. That is necessary, but not sufficient. A desktop Agent can still summarize, omit, or fail to surface the card.

JIKUO visibility must therefore not depend on any single client cooperating. Every critical runtime state projection needs a second, user-accessible channel.

## 2. User Scenario

- A user asks a desktop Agent to run a governed JIKUO flow.
- The Agent invokes JIKUO.
- JIKUO returns chat-ready output and also writes a local runtime visibility snapshot.
- If the Agent does not show the card, the user can run a JIKUO show command or open the runtime file to verify the last status.

## 3. Phase 1 Scope

Create an out-of-band runtime visibility channel:

- `.jikuo/runtime/last_card.md`
- `.jikuo/runtime/state_summary.json`
- `.jikuo/runtime/history/<timestamp>.md`

Add read-only CLI views:

- `jikuo show`
- `jikuo show --last-card`

Phase 1 may define, but should not implement, HTML rendering and dashboard hosting.

## 4. Phase 2 / Follow-up Scope

Strong follow-up candidates:

- `.jikuo/runtime/last_card.html`
- `jikuo dashboard` read-only local web view
- `jikuo watch` terminal refresh
- optional OS notifications for missing evidence, policy supersession, or other high-signal events

These are useful but do not block the first out-of-band visibility foundation.

## 5. Required Design Boundaries

- Runtime visibility writes are local projection writes, not policy-store writes.
- No-write governance proposals must remain no policy/task-session writes; if they update `.jikuo/runtime/`, the response must label that as a runtime visibility side effect.
- Runtime snapshots must not store raw chat transcripts or raw approval phrases.
- Runtime snapshots should prefer compact cards and policy runtime summaries.
- Runtime files must live under the target project root and must not escape `.jikuo/runtime/`.

## 6. Acceptance Criteria

- Every `agent_flow.py propose` path that returns a card can also persist the latest runtime card snapshot.
- The latest policy runtime summary is queryable without relying on the Agent chat response.
- `jikuo show --last-card` returns the same card content that the Agent should have displayed.
- Tests prove runtime visibility writes are confined to `.jikuo/runtime/`.
- Existing guarded-write approval requirements remain unchanged.
