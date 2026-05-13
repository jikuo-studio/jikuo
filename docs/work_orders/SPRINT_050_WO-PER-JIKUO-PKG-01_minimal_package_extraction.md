# SPRINT_050_WO-PER-JIKUO-PKG-01: Minimal Package Extraction

> **Status**: Initial extraction executed, ready for user review
> **Product meaning**: make JIKUO a standalone local package before MCP work, so the future MCP wrapper exposes a reusable tool kernel instead of NarrativeSystem-specific scripts and paths.
> **Scope rule**: plan and execute the minimal package extraction only after explicit approval; do not implement MCP, template marketplace, telemetry, auth, signing, frontend UI, Plugin packaging, gates, rollback, or new governance kernel behavior in this slice.

## 1. Why This Slice Exists

`JIKUO-PKG-00`, `JIKUO-CORE-20`, and `JIKUO-SEC-01` clarified a boundary problem:

- JIKUO should become a reusable governance tool package.
- NarrativeSystem should become a consuming project and dogfooding user.
- `.jikuo/` project state, policies, task sessions, decisions, and local evidence must remain in the consuming project.
- Future MCP should wrap package-safe APIs, not scripts that only work because they live inside NarrativeSystem.

The previous order placed `CORE-20B` resource-reference hygiene before physical extraction. That order is now corrected: extraction comes first, then `CORE-20B` fixes hardcoded references inside the standalone package boundary.

## 2. Current Slice

This work order covers a minimal local extraction to a sibling project, tentatively:

```text
D:\personal_project\Jikuo
```

Expected package shape:

```text
Jikuo/
  pyproject.toml
  src/
    jikuo/
      __init__.py
      agent_flow.py
      policy_store.py
      project_state.py
      task_session.py
      task_session_cards.py
      fixtures/
  tests/
  docs/
    governance/
    schemas/
    work_orders/
```

NarrativeSystem remains the first consuming project:

```text
NarrativeSystem/
  .jikuo/
  docs/scenarios/...
```

## 3. In Scope

- Create the standalone local JIKUO project after filesystem approval.
- Copy tool-owned JIKUO code from `tools/jikuo/**` into package-owned modules.
- Copy JIKUO-owned docs from `docs/jikuo/**` into package docs.
- Keep NarrativeSystem `.jikuo/**` data in NarrativeSystem.
- Add a minimal `pyproject.toml` for local editable development.
- Adjust imports inside the new package so tests can run from the standalone project.
- Preserve existing CLI behavior through package entry points or documented module invocation.
- Run unit, integration, and smoke tests for the extracted package.
- Update NarrativeSystem docs to say it now consumes JIKUO as an external local package after acceptance.

## 4. Out Of Scope

- Do not delete original NarrativeSystem files during the first extraction pass unless a separate cleanup step is approved.
- Do not move `.jikuo/**` project-local state.
- Do not rewrite NarrativeSystem governance history.
- Do not implement MCP.
- Do not fix all `CONTRACT_REFS` or resource reference semantics in this slice; that belongs to `JIKUO-CORE-20B` after extraction.
- Do not implement template import, template signing, telemetry collection, auth, lock files, frontend UI, Codex Plugin, gates, rollback writers, or broader condition vocabulary.

## 5. Migration Method

Preferred first pass:

1. Create a sibling package directory after explicit filesystem approval.
2. Copy, do not move, the existing tool-owned code and docs.
3. Make package imports work in the extracted project.
4. Run extracted package tests.
5. Verify NarrativeSystem `.jikuo/**` data is untouched.
6. Record any NarrativeSystem-side bridge needed for local development.

Why copy first:

- reduces risk to the active NarrativeSystem workspace
- keeps rollback simple
- lets us compare old and new behavior
- avoids deleting historical incubation files before the package has proven itself

## 6. Acceptance Criteria

- A standalone local JIKUO package exists outside NarrativeSystem after approval.
- The package has a minimal Python package structure and test entry points.
- Existing JIKUO unit / integration / smoke tests pass from the package context or have documented migration gaps.
- NarrativeSystem `.jikuo/**` remains in place and is not copied into the package.
- NarrativeSystem-specific project files are not treated as bundled package resources.
- The next task is `JIKUO-CORE-20B` inside the extracted package boundary.

## 6.1 Initial Extraction Result

Executed local package target:

```text
D:\personal_project\Jikuo
```

Created:

- `pyproject.toml`
- `src/jikuo/*.py`
- `src/jikuo/fixtures/**`
- `src/jikuo/__init__.py`
- `tests/*_tests.py`
- `docs/**`
- `README.md`

Preserved:

- `D:\personal_project\NarrativeSystem\.jikuo/**` remains a consuming-project asset and was not copied into the package.
- Original incubation files under NarrativeSystem remain in place for review and comparison.

Adjusted:

- copied modules now support both direct script invocation and package-module imports.
- copied tests now point at `src/jikuo/**` and package-local fixtures.

Verified:

- package test suite: `python -B -m unittest discover -s tests -p "*_tests.py"` passed, 88 tests.
- extracted `agent_flow.py propose` smoke passed with `writes_performed=false`.
- extracted `policy_store.py status` smoke passed against the package-local active-policy fixture.
- package-module smoke passed with `python -B -m jikuo.agent_flow ...` using `PYTHONPATH=src`.

Known follow-up gaps for `JIKUO-CORE-20B`:

- some generated command previews still point to `tools/jikuo/*.py`; these should become package-safe command references or entry-point based previews.
- `CONTRACT_REFS` and source refs still use project-relative `docs/jikuo/**` paths; these should become bundled package refs or role-based project refs.
- tests intentionally still contain legacy-path fixture strings because they verify policy condition behavior; `CORE-20B` should separate fixture data from package-owned command/resource references.

## 7. Testing Requirements

Unit tests:

- run the extracted package equivalent of `agent_flow_tests.py`.
- run the extracted package equivalent of `policy_store_tests.py`.

Integration tests:

- run a package-context `agent_flow.py propose --event task_start` against a fixture project.
- run a package-context policy status / evaluate read against a fixture project.

Smoke tests:

- verify no-write proposal mode still reports `writes_performed=false`.
- verify guarded write paths still require explicit confirmation and approval phrase.
- verify NarrativeSystem `.jikuo/**` was not modified by extraction.

Human semantic review:

- confirm the package boundary matches the product intent: JIKUO is the tool, NarrativeSystem is a consuming project.
- confirm MCP remains blocked until package extraction and `CORE-20B` are accepted.

## 8. Next Task

After `JIKUO-PKG-01` is accepted and executed, proceed to:

- `JIKUO-CORE-20B`: resource-reference and `CONTRACT_REFS` hygiene inside the standalone package boundary.

Do not start `JIKUO-MCP-01` implementation until `PKG-01` and `CORE-20B` are accepted or explicitly deferred.
