# NarrativeSystem Resource Pool Handoff

> **Scan date**: 2026-05-16  
> **JIKUO branch**: `codex/jikuo-core-20b`  
> **Source project**: `D:\personal_project\NarrativeSystem`  
> **JIKUO repo**: `D:\personal_project\Jikuo`  
> **Status**: partial archive handoff; JIKUO-side active references are cleared, NarrativeSystem-side live usage is not assessed in this scan.

---

## Purpose

This handoff marks the close of the JIKUO independent-repository active reference migration.

JIKUO was incubated inside NarrativeSystem, but the standalone package must not treat NarrativeSystem's `docs/jikuo/`, `tools/jikuo/`, old sprint index, or old rule registry paths as active runtime or contract authority.

This scan only covers `D:\personal_project\Jikuo`. It does not modify `D:\personal_project\NarrativeSystem`.

---

## Scanned Patterns

- `D:\personal_project\NarrativeSystem`
- `D:/personal_project/NarrativeSystem`
- `NarrativeSystem`
- `docs/jikuo`
- `tools/jikuo`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `python -B tools/jikuo`
- package-safe replacement posture:
  - `python -B -m jikuo...`
  - `jikuo show`
  - `jikuo configure status`
  - `pkg://jikuo/...`

Representative scan command:

```powershell
rg -n "D:\\personal_project\\NarrativeSystem|D:/personal_project/NarrativeSystem|NarrativeSystem|docs/jikuo|tools/jikuo|docs/scenarios/interactive_novel/governance/rule_registry.yaml|docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md|python -B tools/jikuo" docs src tests -g '!tmp/**' -g '!.git/**' -g '!.jikuo/runtime/**'
```

---

## Result

Remaining active NarrativeSystem references: **no**.

| Type | Remaining | Decision |
|---|---:|---|
| `active_runtime_reference` | 0 | No runtime code, CLI, MCP server, or package entry point depends on NarrativeSystem paths. |
| `active_contract_reference` | 0 | Current JIKUO contract examples and fixture project-state authority refs now point to standalone repo paths or `pkg://jikuo/...`. |
| `historical_provenance` | present | Kept. Historical work orders may mention the incubating source project, old commands, or old docs as migration history. |
| `fixture_only` | present | Kept. Some tests and fixture policies intentionally retain old-shaped changed-path examples for compatibility / regression behavior. They do not read NarrativeSystem files. |
| `no_action_needed` | present | Kept. Negative assertions that reject `tools/jikuo`, `docs/jikuo`, or `NarrativeSystem` are protective tests, not dependencies. |

---

## Migrated Active References

The following JIKUO-side active-looking references were migrated:

- `docs/governance/jikuo_policy_aware_agent_flow_contract.md`
  - from old implementation path `tools/jikuo/agent_flow.py`
  - to current source path `src/jikuo/agent_flow.py`
- `docs/schemas/rule_registry_view_model.schema.md`
  - from old source registry example `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
  - to standalone JIKUO registry example `docs/governance/rule_registry.yaml`
- `src/jikuo/fixtures/*/.jikuo/project_state.yaml`
  - from old `docs/jikuo/...` / old Narrative registry refs
  - to `pkg://jikuo/...` and `docs/governance/rule_registry.yaml`

Package-facing code was already migrated before this scan:

- command previews use `python -B -m jikuo...`
- runtime status uses `jikuo show`
- configuration review uses `jikuo configure status`
- package-owned source refs use `pkg://jikuo/...`

---

## Remaining References By Type

### active_runtime_reference

None found.

### active_contract_reference

None remaining after this slice.

### historical_provenance

Historical work orders under `docs/work_orders/SPRINT_050_WO-PER-JIKUO-*.md` may mention:

- old `docs/jikuo/...` paths
- old `tools/jikuo/...` paths
- old Sprint 050 / NarrativeSystem provenance
- historical `python -B tools/jikuo/...` commands

These documents record how JIKUO was extracted. They are not active runtime instructions.

### fixture_only

The following fixture-shaped references remain intentionally non-authoritative:

- `tests/*_tests.py` values that use old `docs/jikuo/**` or `tools/jikuo/**` strings as compatibility / regression inputs.
- `src/jikuo/fixtures/*/.jikuo/policies/approved/*.yaml` changed-path patterns that exercise old-shaped path matching.

These references do not load files from `D:\personal_project\NarrativeSystem`.

### no_action_needed

Protective tests that assert package-facing output does not expose old paths are kept, for example:

- `assertNotIn("tools/jikuo", ...)`
- `assertNotIn("NarrativeSystem", ...)`
- checks that source refs do not start with `docs/jikuo/`

---

## Files Changed In JIKUO

- `docs/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/schemas/rule_registry_view_model.schema.md`
- `src/jikuo/fixtures/policy_evidence_session_project/.jikuo/project_state.yaml`
- `src/jikuo/fixtures/policy_store_active_project/.jikuo/project_state.yaml`
- `src/jikuo/fixtures/policy_store_condition_project/.jikuo/project_state.yaml`
- `src/jikuo/fixtures/policy_store_conflict_project/.jikuo/project_state.yaml`
- `src/jikuo/fixtures/policy_store_initialized_project/.jikuo/project_state.yaml`
- `src/jikuo/fixtures/policy_store_real_chain_testing_project/.jikuo/project_state.yaml`
- `src/jikuo/fixtures/policy_store_stale_project/.jikuo/project_state.yaml`
- `src/jikuo/fixtures/task_session_ready_project/.jikuo/project_state.yaml`
- `.jikuo/project_context.yaml`
- `docs/README.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_productization_task_map.md`
- `docs/migration/NARRATIVESYSTEM_RESOURCE_POOL_HANDOFF.md`
- `docs/migration/narrativesystem_resource_pool_handoff.yaml`

---

## NarrativeSystem Paths Now Safe To Archive

From the JIKUO independent repository perspective, these paths are safe to move into a NarrativeSystem-side JIKUO incubation resource pool:

- `D:\personal_project\NarrativeSystem\docs\jikuo\`
- `D:\personal_project\NarrativeSystem\tools\jikuo\`

The standalone JIKUO repo no longer treats those paths as active runtime or contract authority.

---

## NarrativeSystem Paths That Must Not Yet Be Archived By This Handoff Alone

Do not archive these solely based on this JIKUO-side scan:

- `D:\personal_project\NarrativeSystem\docs\scenarios\interactive_novel\governance\rule_registry.yaml`
- `D:\personal_project\NarrativeSystem\docs\scenarios\interactive_novel\sprints\SPRINT_050_20260409.md`

They are no longer active JIKUO dependencies, but they may still be live NarrativeSystem documents. A later NarrativeSystem-side write plan should scan and classify that project before moving them.

---

## Verification

- `rg` package-code scan found no old NarrativeSystem-era paths in active `src/jikuo` code outside fixture directories.
- `python -B -m unittest discover -s tests -p "*_tests.py"` passed: 174 tests.
- `git diff --check` passed.
- Completion-review policy evidence was checked with:
  - `main_document_mount_maintenance_evidence`: ok
  - `progress_summary_business_meaning_evidence`: ok
  - missing evidence reports: 0

---

## Recommended Archive Marker Text

Use this marker when archiving the old NarrativeSystem JIKUO incubation pool:

```text
Archived JIKUO incubation resource pool.

Do not treat this directory as the active JIKUO runtime, CLI, MCP, policy-template, or documentation authority.
Use the standalone JIKUO package/repository instead:
- commands: python -B -m jikuo..., jikuo show, jikuo configure status, jikuo-mcp
- package refs: pkg://jikuo/...
- repository docs: D:\personal_project\Jikuo\docs\

This archive may be used as historical provenance or template-mining input only after privacy/provenance review.
```
