# INSIGHT-2026-05-17: Self-Bootstrap Harness Workspace Boundary

> **Classification**: promoted_to_task
> **Status**: promoted
> **Captured**: 2026-05-17
> **Promoted task**: `JIKUO-SELF-BOOTSTRAP-03`

## Core Idea

JIKUO self-bootstrap development may need to separate the harness workspace from
the source workspace.

Instead of treating the JIKUO source repository root as both the governance
harness and the governed source target, a future self-bootstrap proof should
test a parent workspace layout:

```text
JikuoWorkspace/
  .jikuo/                 # harness state, activation settings, runtime cards
  JIKUO.md / AGENTS.md    # client instructions for the mounted workspace
  source/
    jikuo/                # the JIKUO source repository being governed
```

## Why It Matters

Strict mounted execution is a host-boundary problem. If an AI GUI opens the same
directory that contains both the governance harness state and the source code,
it is harder to tell whether JIKUO is acting as an external harness or as an
optional tool inside the project being edited.

A parent harness workspace could make self-bootstrap closer to the product's
target use case: JIKUO governs a project from a workspace boundary, while the
project source remains an explicit target.

## Questions To Resolve

- Does `.jikuo/activation_settings.yaml` belong to the harness workspace, the
  source repository, or both?
- Should runtime cards be written at the harness level, the source-project
  level, or mirrored?
- Should policy stores and task sessions be workspace-wide, per source project,
  or dual-scoped?
- Should MCP tools accept both `project_root` and `target_project_root`?
- Can Codex / Claude GUI mounted behavior work more reliably when the GUI opens
  the parent harness workspace?

## Current Decision

Do not move the current repository or source tree as part of this insight.

Promote the idea to a spike work order that tests the layout and records the
project-root / target-root model before any directory migration or user-facing
setup change.

