# INSIGHT-2026-05-15: Task-Session Concurrent Write Guard

> **Classification**: `task_candidate`
> **Status**: open
> **Created**: 2026-05-15
> **Related surface**: `src/jikuo/task_session.py`

## Insight

Task-session update helpers should protect a single task-session file from
parallel write attempts.

During MCP Stage A adapter development, two guarded task-session updates were
started concurrently against the same session file. On Windows this produced a
file-lock race: one update reported a temporary-file replace error and another
reported failed post-write verification. The affected session file was not
recoverable from the filesystem, so the slice had to create a fresh task-session
record and continue with serialized updates.

## Why It Matters

JIKUO's task-session record is intended to be durable process memory. If desktop
agents, future MCP tools, or helper scripts can write the same session in
parallel, the harness can lose the very audit trail it is meant to preserve.

## Possible Future Task

Add a guarded write serialization mechanism for task-session updates:

- refuse concurrent updates to the same task-session file, or
- use a per-session lock file with clear stale-lock recovery semantics, and
- add regression coverage for parallel update attempts.

Until this is implemented, JIKUO self-bootstrap work should update one
task-session file serially.
