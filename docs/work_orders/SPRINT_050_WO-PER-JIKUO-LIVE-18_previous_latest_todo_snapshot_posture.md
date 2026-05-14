# SPRINT_050_WO-PER-JIKUO-LIVE-18: Previous/Latest Todo Snapshot Posture

> **Status**: Implemented and ready for user review on 2026-05-15
> **Product meaning**: make the standalone repository honest about previous/latest todo comparison before MCP exposes project-context bindings.
> **Scope rule**: disable the fake previous-todo binding for v0 and record snapshot rotation as future work; do not implement snapshot rotation or MCP in this slice.

## 1. Why This Slice Now

`JIKUO-ARCH-03` found that `.jikuo/project_context.yaml` used the same file for
both `latest_todo_map` and `previous_todo_map`.

That was risky because a policy could appear to have both documents mounted even
though no historical snapshot existed. A latest-vs-previous comparison against the
same file is not a real delta.

Before MCP implementation, project context must not advertise a capability that
the standalone repository cannot actually perform.

## 2. Decision

Accepted v0 posture:

- `latest_todo_map` remains bound to `docs/governance/jikuo_productization_task_map.md`.
- `previous_todo_map` is disabled with `path: null`.
- `previous_todo_map.status` is `not_implemented_in_v0`.
- Snapshot rotation is deferred and captured as a development insight.
- Policies or templates that require a real previous/latest delta must not be
  treated as fully satisfied until a future snapshot rotation capability exists.

## 3. Implementation

Updated `.jikuo/project_context.yaml`:

- removed the same-file previous-todo fallback
- added `status: not_implemented_in_v0`
- added `replacement: future_snapshot_rotation`

Added:

- `docs/insights/INSIGHT-2026-05-15-todo-snapshot-rotation.md`
- registry entry in `docs/insights/insights_registry.yaml`
- regression coverage that prevents the standalone repository from silently
  restoring the same-file previous-todo binding

Updated main docs:

- `docs/README.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_productization_task_map.md`

## 4. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Previous/latest todo snapshot posture | review project context -> disable fake previous-todo binding -> record snapshot rotation as deferred insight -> update taskmap / mounts -> regression test guards against same-file fallback | `CAP-PROJECT-CONTEXT-BINDING-01`; `CAP-TODO-SNAPSHOT-POSTURE-01`; `CAP-MAIN-DOC-MOUNT-MAINTENANCE-01` | no snapshot rotation implementation; no MCP implementation; project-context binding remains honest |

## 5. Acceptance Criteria

- `.jikuo/project_context.yaml previous_todo_map.path` is `null`.
- `previous_todo_map.status` is `not_implemented_in_v0`.
- Snapshot rotation is recorded as deferred insight.
- Taskmap no longer lists previous/latest todo snapshot posture as an open blocker.
- Tests prevent the same-file previous-todo fallback from returning.
