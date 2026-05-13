# SPRINT_050_WO-PER-JIKUO-PKG-00: Package Boundary And Extraction Plan

> **Status**: Draft, ready for user review
> **Product meaning**: separate "JIKUO as a reusable tool package" from "a user's project-local `.jikuo/` state" before project-context portability, security hardening, physical extraction, or MCP implementation begins.
> **Scope rule**: define the package boundary and migration plan only; do not move files, create a new repository, change imports, or implement MCP in this slice.

## 1. Why This Slice Exists

`JIKUO-MCP-01` exposed a packaging problem: MCP should wrap a reusable JIKUO kernel, not NarrativeSystem-specific paths and assumptions.

Before implementing MCP, JIKUO needs a clear boundary between:

- tool-owned code and bundled resources
- user-project-local state and policies
- project-specific document bindings
- future package installation / development-mode installation

Without this boundary, `CORE-20` project-context binding and `MCP-01` wrapper work would keep inheriting the current mixed identity: JIKUO is both a tool under development and a governance layer inside NarrativeSystem.

## 2. In Scope

This work order defines:

- the future JIKUO package boundary
- what should eventually move into a standalone package
- what must remain in the user project
- how bundled JIKUO contract docs should be referenced
- how project-specific docs should be referenced
- what must not be migrated automatically
- the phased extraction sequence
- acceptance criteria for starting `CORE-20`

## 3. Out Of Scope

This slice must not:

- create a new repository
- move files
- change Python imports
- create `pyproject.toml`
- package or publish JIKUO
- modify `.jikuo/` project data
- implement `project_context.yaml`
- fix `CONTRACT_REFS`
- implement MCP server / adapter code
- add frontend, Plugin, gate, telemetry collection, or template marketplace behavior

## 4. Boundary Model

Tool package candidates:

- `tools/jikuo/*.py`
- `tools/jikuo/*_tests.py`
- `tools/jikuo/fixtures/**` after fixture paths are made package-safe
- `docs/jikuo/governance/**` that describe JIKUO's own contracts
- `docs/jikuo/schemas/**`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-*.md` as product-development history or package docs, subject to later pruning

User-project-local state that must remain in the consuming project:

- `.jikuo/project_state.yaml`
- `.jikuo/policies/**`
- `.jikuo/task_sessions/**`
- project-specific binding files such as future `.jikuo/project_context.yaml`
- project-specific task evidence, approvals, decisions, and local policy choices

Reference categories:

| Reference category | Example | Future reference form |
|---|---|---|
| JIKUO bundled contract | policy-store configuration flow | `pkg://jikuo/governance/...` |
| User project document role | latest backlog / previous backlog | `role://document/latest_backlog` resolved by `.jikuo/project_context.yaml` |
| User project path | local work order file | relative path under `project_root` after escape checks |
| External source | official MCP docs | URL plus provenance metadata |

## 5. Pre-MCP Foundation Sequence

Recommended order after this work order:

1. `JIKUO-CORE-20`: define project context binding, policy template portability, path escape rules, and resolved policy concepts.
2. `JIKUO-SEC-01`: define trust, privacy, provenance, namespace, principal, telemetry, and timestamp baseline fields.
3. `JIKUO-PKG-01`: perform minimal package extraction after the boundary, portability, and trust baseline are accepted.
4. `JIKUO-CORE-20B`: remove or neutralize hardcoded NarrativeSystem document references such as `CONTRACT_REFS` inside the extracted package boundary.
5. `JIKUO-MCP-01`: implement MCP wrapper against package-safe APIs and resolved project context.

## 6. Acceptance Criteria

- The task map identifies `JIKUO-PKG-00` as the next task before `CORE-20` and `MCP-01`.
- `JIKUO-MCP-01` is marked blocked until portability / security / package foundation is accepted.
- Tool-owned resources and project-local state are separated in writing.
- Future resource reference forms are declared: bundled package refs, role-based refs, relative project refs, and external refs.
- Physical migration remains explicitly out of scope for this slice.

## 7. Testing / Review Requirements

Unit tests:

- not required for this planning-only slice.

Integration tests:

- not required; no runtime behavior changes.

Smoke checks:

- verify task-start scope-control policy can be satisfied for this work-order delivery.
- verify existing JIKUO runner and policy-store tests still pass if docs are updated.

Human review:

- confirm the boundary matches the intended future product shape.
- confirm NarrativeSystem `.jikuo/` data remains a user-project asset and must not be moved during package extraction.
