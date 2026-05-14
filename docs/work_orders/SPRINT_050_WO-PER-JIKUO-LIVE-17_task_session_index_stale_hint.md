# SPRINT_050_WO-PER-JIKUO-LIVE-17: Task-Session Index Stale Hint

> **Status**: Implemented and ready for user review on 2026-05-15
> **Product meaning**: keep `latest_task_session_refs` as an explicit guarded refresh while making stale project-state indexes visible in `jikuo show`.
> **Scope rule**: adjust runtime visibility / CLI inspection only; do not auto-refresh `.jikuo/project_state.yaml`, do not implement MCP, and do not change task-session write semantics in this slice.

## 1. Why This Slice Now

The MCP pre-implementation review left one decision open: whether `.jikuo/project_state.yaml latest_task_session_refs` should be updated implicitly during task start, or remain a separate guarded refresh.

The accepted direction for now is:

- task-session start remains a guarded sidecar write
- project-state index refresh remains a separate guarded action
- users should not have to remember this manually
- `jikuo show` should report when the index is stale and show the review / refresh commands

This keeps the "no hidden write" boundary intact while removing the semi-black-box feeling around stale task-session discovery.

## 2. Implementation

Implemented in `src/jikuo/runtime_visibility.py`:

- Added `jikuo.task_session_index_status.v0`.
- `jikuo show --format json` now attaches `task_session_index` from the existing task-session index refresh planner.
- Markdown `jikuo show` now renders a `Task-Session Index` section.
- When discovered task-session files differ from `latest_task_session_refs`, the status is `stale` and the output includes:
  - a dry-run review command
  - a guarded refresh command with approval phrase placeholder

No project-state write is performed by `jikuo show`.

## 3. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Task-session index stale hint | user runs `jikuo show` -> runtime visibility loads latest state summary -> task-session index refresh planner compares current latest refs with discovered session files -> show output renders current / stale status and review / refresh commands | `CAP-RUNTIME-SHOW-CLI-01`; `CAP-TASK-INDEX-REFRESH-01`; `CAP-TASK-SESSION-INDEX-STALE-HINT-01` | read-only; no `.jikuo/project_state.yaml` mutation; refresh remains separate and approval-gated |

## 4. Acceptance Criteria

- `jikuo show --format json` includes `task_session_index`.
- Stale index state reports `status: stale`.
- Markdown output includes `## Task-Session Index`.
- Stale output includes both `index --dry-run` and guarded `index --refresh` commands.
- `jikuo show` does not mutate `.jikuo/project_state.yaml`.
- Tests cover stale-index visibility.
