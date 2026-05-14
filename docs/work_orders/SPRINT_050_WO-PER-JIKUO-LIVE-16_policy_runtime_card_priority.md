# SPRINT_050_WO-PER-JIKUO-LIVE-16: Policy Runtime Card Priority

> **Status**: Implemented and ready for user review on 2026-05-15
> **Product meaning**: make policy runtime status the first visible governance card whenever JIKUO returns chat-ready or runtime-card output.
> **Scope rule**: adjust existing runner display ordering only; do not implement MCP, MCP adapter/server code, dashboard, hooks, Agent SDK adapters, gates, or new policy execution behavior in this slice.

## 1. Why This Slice Now

`JIKUO-LIVE-10` made policy runtime status visible, and `JIKUO-LIVE-12` made runtime cards independently accessible through `.jikuo/runtime/`.

However, completion-review output could still render a task-session lifecycle card before the `policy_runtime_status` card in the `## Cards` section. That made the most important governance status easier for an Agent or user to miss.

Before MCP implementation, the existing runner must make the priority rule deterministic:

- policy runtime status is first-screen governance context when present
- card ordering must be explicit for future MCP display directives
- structured `cards[]` order should remain stable for existing programmatic callers

## 2. Implementation

Implemented in `src/jikuo/agent_flow.py`:

- Added protocol-neutral `display` directives to proposal JSON:
  - `schema: jikuo.display_directives.v0`
  - `must_show_verbatim: ["chat_ready_markdown"]`
  - `card_priority_order`, with `policy_runtime_status` first
  - `priority: first_in_response`
- Added deterministic Markdown display ordering for cards.
- Kept the underlying structured `cards[]` list unchanged so existing callers and tests that inspect first generated card continue to work.
- Moved the rendered `## Cards` section above detailed trigger / atom / evidence sections so the prioritized card appears in the first visible part of the runtime card.

Updated documents:

- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MCP-01_mcp_wrapper_mvp.md`
- `docs/governance/jikuo_productization_task_map.md`
- `docs/governance/jikuo_execution_mounts.md`
- `.jikuo/project_context.yaml`
- `docs/README.md`

## 3. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Policy runtime first-screen card priority | agent invokes existing runner -> runner builds proposal cards -> proposal attaches display directives -> chat-ready markdown sorts display cards by priority -> `.jikuo/runtime/last_card.md` receives the same prioritized card order -> user sees `policy_runtime_status` before lifecycle / task cards | `CAP-POLICY-RUNTIME-CARD-PRIORITY-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no MCP implementation; no new write path; structured card generation order remains unchanged |

## 4. Acceptance Criteria

- `policy_runtime_status` is first in `display.card_priority_order`.
- `chat_ready_markdown` renders `## Policy runtime status` before task-session lifecycle cards when the runtime status card exists.
- `chat_ready_markdown` renders the prioritized `## Cards` section before detailed trigger / atom / evidence sections.
- Runtime visibility snapshots use the same prioritized markdown.
- Existing structured `cards[]` ordering remains compatible with current callers.
- Regression tests cover the first-screen priority rule.

