# SPRINT_050_WO-PER-JIKUO-SELF-BOOTSTRAP-03: Harness Workspace Boundary Spike

> **Status**: Planned; proof / design spike only.
> **Date**: 2026-05-17
> **Product meaning**: JIKUO is a harness, so self-bootstrap development should verify whether the harness state can live at a workspace boundary while the source repository is a governed child target.

## 1. Why This Task Exists

JIKUO self-bootstrap currently uses the repository root as both:

- the source tree being edited
- the local `.jikuo/` governance state
- the MCP / instruction mount root
- the runtime card and proof artifact root

That layout works for local development, but it does not fully test the product
model in which JIKUO governs a project from an explicit harness boundary.

If strict mounted adapters succeed, the AI GUI may be most reliable when it opens
a parent harness workspace that contains `.jikuo/`, client instructions, MCP
configuration, and one or more source repositories as governed targets.

## 2. Problem Statement

Before moving directories or changing user setup, JIKUO needs a spike that
answers whether a parent/child layout improves self-bootstrap execution without
breaking package development, MCP calls, runtime visibility, or policy storage.

Candidate layout:

```text
JikuoWorkspace/
  .jikuo/
  JIKUO.md
  AGENTS.md
  source/
    jikuo/
```

## 3. Scope

This spike should:

- model `harness_root` versus `target_project_root`
- test where activation settings, runtime cards, policy store, and task-session
  records should live
- verify whether MCP tools can route a user turn using the harness root while
  targeting a child source repository
- identify which code paths currently assume a single `project_root`
- compare Codex and Claude GUI behavior when opening the parent workspace versus
  the source repository directly
- produce a written recommendation before any migration

## 4. Non-Goals

- Do not move `src/jikuo/` or the repository root during this spike.
- Do not change GitHub remote layout.
- Do not implement multi-repository governance before the model is accepted.
- Do not claim strict mounted success without Codex / Claude hook proof.

## 5. Acceptance Criteria

- A temporary parent workspace proof exists and is documented.
- The proof records where `.jikuo/activation_settings.yaml`,
  `.jikuo/runtime/`, `.jikuo/policies/`, and `.jikuo/task_sessions/` should live.
- The proof states whether MCP calls need `target_project_root` in addition to
  `project_root`.
- The proof identifies all required code / docs changes before any real
  directory migration.
- The final recommendation is one of:
  - keep current single-root self-bootstrap
  - adopt parent harness workspace for self-bootstrap only
  - design a general multi-root harness model for users
  - defer until strict adapter proof is complete

## 6. Related Work

- `JIKUO-SELF-BOOTSTRAP-02`: stable self-bootstrap execution strategy
- `JIKUO-INTG-03`: strict mounted harness adapter contract
- `JIKUO-CODEX-PLUGIN-01`: Codex pre-turn harness proof
- `JIKUO-CLAUDE-HOOK-01`: Claude hook strict adapter proof
- `INSIGHT-2026-05-17-self-bootstrap-harness-workspace-boundary`

