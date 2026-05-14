# SPRINT_050_WO-PER-JIKUO-LIVE-12: Out-of-band Runtime Visibility Channels

> **Status**: Phase 1 accepted on 2026-05-14
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

## 3A. Phase 1 Implementation Delivered

Implemented package artifacts:

- `src/jikuo/runtime_visibility.py`: writes `last_card.md`, `state_summary.json`, and timestamped history cards under `.jikuo/runtime/`.
- `src/jikuo/runtime_visibility.py`: builds `client_display_links` with absolute Markdown targets for the latest card, state summary, and history card.
- `src/jikuo/agent_flow.py`: attaches runtime visibility reports and client display links to proposal JSON / Markdown output, and labels runtime projection as a side effect distinct from governance writes.
- `src/jikuo/cli.py` and `src/jikuo/__main__.py`: expose `jikuo show` and `python -B -m jikuo show`.
- `pyproject.toml`: adds the `jikuo` console script entry point.
- `.gitignore`: ignores local `.jikuo/runtime/` projection files.
- `tests/runtime_visibility_tests.py`: verifies snapshot writes, `jikuo show`, fixture non-mutation, and runtime-path confinement.

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
- Every card-producing `agent_flow.py propose` JSON / Markdown response exposes a `client_display_links` block so desktop clients can show direct local links to the latest runtime card.
- The latest policy runtime summary is queryable without relying on the Agent chat response.
- `jikuo show --last-card` returns the same card content that the Agent should have displayed.
- Tests prove runtime visibility writes are confined to `.jikuo/runtime/`.
- Existing guarded-write approval requirements remain unchanged.

## 7. Acceptance Record

Accepted on 2026-05-14 after verifying the Phase 1 scope:

- `.jikuo/runtime/last_card.md`
- `.jikuo/runtime/state_summary.json`
- `.jikuo/runtime/history/<timestamp>.md`
- `jikuo show`
- `jikuo show --last-card`
- `client_display_links`

Verification evidence:

- `python -B -m unittest discover -s tests -p "*_tests.py"`: 115 tests passed.
- `python -B -m jikuo show`: rendered runtime status with `JIKUO Runtime Links`.
- Implementation commit: `87a3ec6 jikuo: surface runtime card links`.
