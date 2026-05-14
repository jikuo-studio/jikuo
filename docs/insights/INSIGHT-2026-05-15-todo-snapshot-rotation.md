# INSIGHT-2026-05-15: Todo Snapshot Rotation

> **Classification**: `deferred`
> **Status**: deferred
> **Created**: 2026-05-15
> **Related task**: `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-18_previous_latest_todo_snapshot_posture.md`

## Observed Situation

JIKUO templates can express a need to compare the latest todo map with a previous
todo map. In the standalone repository, the temporary `previous_todo_map` binding
pointed at the same file as `latest_todo_map`.

That made project context look complete while the actual previous snapshot did not
exist. Any policy depending on a real latest-vs-previous delta would be easy to
misread as satisfied.

## Decision

For v0, previous/latest todo comparison is disabled.

`.jikuo/project_context.yaml` keeps `latest_todo_map` bound to the active task map,
but sets `previous_todo_map.path` to `null` with status
`not_implemented_in_v0`.

## Future Capability

Snapshot rotation should become a later explicit capability, not an incidental
side effect of task start or completion.

Candidate future behavior:

- create immutable todo snapshots under a project-owned snapshot directory
- update `previous_todo_map` only through a guarded rotation operation
- record which work order or completion event caused the rotation
- let policies compare latest vs previous only when both bindings resolve to
  distinct snapshot artifacts

## Current Boundary

Until that capability exists, no policy requiring a real previous/latest todo
delta should be considered fully satisfied by the standalone repository context.
