# SPRINT_050_WO-PER-JIKUO-CORE-20B: Resource Reference Hygiene

> **Status**: Implemented, ready for user review
> **Product meaning**: remove the most visible NarrativeSystem-era path assumptions from the extracted JIKUO package, so desktop cards and policy reports can be used from a package boundary before MCP wrapping.
> **Scope rule**: package-owned references and command previews only; do not implement full project-context binding resolution, template import, MCP server, frontend UI, Plugin packaging, gates, telemetry, auth, signing, or marketplace behavior in this slice.

## 1. Why This Slice Exists

After `JIKUO-PKG-01`, the package can run from `D:\personal_project\Jikuo`, but some outputs still exposed old incubation paths:

- `tools/jikuo/*.py` in generated command previews
- `docs/jikuo/**` in package-owned source refs
- producer tool refs that described JIKUO as a project-local script

Those paths are not portable because JIKUO is now a package and NarrativeSystem is only one consuming project.

## 2. In Scope

- Convert package-owned contract/source refs to `pkg://jikuo/...`.
- Convert guarded command previews to package module invocation, such as `python -B -m jikuo.task_session`.
- Convert policy-store write/evolution command previews to `python -B -m jikuo.policy_store`.
- Convert runner producer tool ref to `python -B -m jikuo.agent_flow`.
- Keep project-local refs, such as `.jikuo/**`, project policy paths, and consuming-project registry refs, as project data.
- Add regression tests that reject `tools/jikuo` command previews in package-facing cards.

## 3. Out Of Scope

- No full `project_context.yaml` resolver.
- No `pkg://` dereference implementation through `importlib.resources`.
- No template import / bind command.
- No MCP server or adapter.
- No cleanup of historical docs that mention `tools/jikuo/**` as migration history.
- No mutation of NarrativeSystem `.jikuo/**`.

## 4. Implemented Changes

Code:

- `src/jikuo/project_state.py`: JIKUO-owned contract refs now use `pkg://jikuo/...`; the consuming-project registry ref is marked `project://...`.
- `src/jikuo/task_session.py`: task-session work-order and schema refs now use `pkg://jikuo/...`.
- `src/jikuo/policy_store.py`: policy-store contract refs now use `pkg://jikuo/...`; task-session ingestion producer tool ref uses package module form.
- `src/jikuo/task_session_cards.py`: task-session command previews now use `python -B -m jikuo.task_session`.
- `src/jikuo/agent_flow.py`: agent producer ref and policy-store command previews now use package module form.

Tests:

- command preview regression tests assert `python -B -m jikuo.task_session` or `python -B -m jikuo.policy_store`.
- command preview regression tests reject `tools/jikuo`.
- source-ref regression tests assert `pkg://jikuo/...` for package-owned refs.

## 5. Verification

Unit / integration:

```powershell
python -B -m unittest discover -s tests -p "*_tests.py"
```

Result:

- 88 tests passed.

Smoke:

```powershell
$env:PYTHONPATH='src'; python -B -m jikuo.agent_flow propose --event task_start --task-title "CORE-20B package-safe smoke" --project-root src\jikuo\fixtures\policy_store_active_project --format json
$env:PYTHONPATH='src'; python -B -m jikuo.policy_store status --project-root src\jikuo\fixtures\policy_store_active_project --format json
rg -n "tools/jikuo|docs/jikuo" src\jikuo
```

Result:

- `agent_flow` package-module smoke returned no-write proposal output.
- `policy_store` package-module smoke returned `pkg://jikuo/...` source refs.
- package source search found no `tools/jikuo` or `docs/jikuo` references.

## 6. Remaining Follow-Up

Later portability work should still add:

- `pkg://` dereference through package resources.
- `project_context.yaml` role resolution.
- template import / binding / resolved-policy implementation.
- MCP privacy projection over package-safe results.

## 7. Next Task

If accepted, proceed to the MCP adapter boundary or the project-context resolver implementation, depending on whether the user wants to start MCP with the current package-safe refs or finish `project_context.yaml` resolution first.
