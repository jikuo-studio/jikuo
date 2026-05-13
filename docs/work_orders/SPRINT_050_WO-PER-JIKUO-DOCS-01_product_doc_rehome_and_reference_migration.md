# SPRINT_050_WO-PER-JIKUO-DOCS-01: Product Doc Rehome And Reference Migration

> **Date**: 2026-05-11
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / documentation architecture / reference migration
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: desktop_operating_skeleton
> **Current slice is not**: configurable_rule_kernel; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: preserves existing JIKUO work-order and governance contracts while moving their canonical location; updates checker path triggers so future JIKUO work remains visible after the directory migration
> **Deferred kernel backlog refs**: `CAP-POLICY-STORE-ADAPTER-01`; `CAP-POLICY-AWARE-FLOW-IMPLEMENTATION-01`; `CAP-POLICY-EVIDENCE-CHECKER-01`; installable Skill / MCP / Plugin packaging
> **Current slice**: move JIKUO-owned development docs from interactive-novel Sprint/governance folders into `docs/jikuo/`, update references, and keep non-JIKUO historical/context docs in place.
> **User scenario**: A user or agent continuing JIKUO development needs one product-native documentation home instead of hunting through NarrativeSystem Sprint directories.
> **Runtime chain**: no runtime chain; documentation/source layout only.
> **Canonical source**: user-approved boundary that only JIKUO-owned development files should move, while historical source-context docs stay in place.
> **Bridge object**: `docs/jikuo/` directory layout and migrated reference paths.
> **Consumer projection**: future JIKUO work orders, execution mounts, checker reports, code constants, fixtures, task-session/project-state sidecars, and desktop-agent instructions.
> **Lifecycle**: identify JIKUO-owned docs -> move files -> update path references -> update checker triggers -> verify no stale old-path references remain.
> **Testing layers**: path-reference smoke, checker smoke, JIKUO unit/workflow smoke, human governance review.

---

## 1. Product Meaning

> **中文注释**：这一步不是“整理文件夹好看一点”。它把机括从 Sprint 050 的副产物位置，推进成有自己开发目录、自己入口、自己引用体系的产品线。

Before this slice, JIKUO product docs were mixed into:

- `docs/scenarios/interactive_novel/sprints/`
- `docs/scenarios/interactive_novel/governance/`

After this slice:

- JIKUO work orders live in `docs/jikuo/work_orders/`
- JIKUO governance/product contracts live in `docs/jikuo/governance/`
- JIKUO schemas live in `docs/jikuo/schemas/`

NarrativeSystem historical docs stay where they are.

---

## 2. JIKUO Layer Boundary

Current layer:

- `desktop_operating_skeleton`

This slice is allowed to:

- move JIKUO-owned work-order docs
- move JIKUO-owned governance/product docs
- move JIKUO-owned schema docs
- update path references in docs, tools, tests, fixtures, and `.jikuo/project_state.yaml`
- update checker rule path triggers for future JIKUO docs
- add a `docs/jikuo/README.md`

This slice is not allowed to:

- move NarrativeSystem runtime docs
- move Sprint 049 / Sprint 050 historical source-context docs
- move `rule_registry.yaml`
- move `rule_registry.schema.md`
- move `agent_operating_kernel.md`
- change policy semantics
- change task-session runtime semantics
- change narrative-engine behavior
- implement Skill / MCP / Plugin / frontend / gate behavior

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- keeping JIKUO work-order metadata and required sections intact after moving files
- updating `R-013` JIKUO path triggers to the new product directory
- extending `R-006` and `R-012` so new `docs/jikuo/work_orders/*.md` files remain visible to the checker
- keeping rule source documents and NarrativeSystem governance source files in place when they are not JIKUO-owned product docs

---

## 4. Deferred Kernel Backlog

Still deferred:

- policy store adapter
- full policy-aware agent flow implementation
- policy execution evidence checker
- guarded `agent_flow.py apply`
- installable Skill
- MCP tool wrapper
- Codex Plugin
- frontend rule/run-control/audit surface
- gate enforcement

---

## 5. Scope

This work order covers:

- `docs/jikuo/README.md`
- JIKUO work-order relocation
- JIKUO governance/product contract relocation
- JIKUO schema relocation
- reference updates across docs, tools, `.jikuo`, and fixtures
- checker trigger updates for new JIKUO paths
- smoke tests and stale-reference checks

---

## 6. Out Of Scope

This work order does not cover:

- content rewrites beyond path/reference migration
- policy execution
- schema redesign
- task-session storage redesign
- frontend design
- MCP / Plugin implementation
- runtime narrative-engine changes
- migration of historical NarrativeSystem docs that merely mention JIKUO

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/README.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- run JIKUO helper tests that depend on moved path constants.

`integration`:

- run checker JSON output tests because checker rule paths changed.

`workflow / orchestration`:

- verify `agent_flow.py propose` still returns a same-chat proposal after path migration.

`semantic regression`:

- N/A because this is documentation/source layout and process-governance plumbing, not product-output content.

`smoke`:

- run stale-reference searches for old JIKUO doc paths.
- run `check_rule_registry.py` on this new work order.
- run `git diff --check`.

`human governance review`:

- required; user reviews whether the moved directory boundary matches the intended product boundary.

---

## 9. Delivery Criteria

- JIKUO product docs exist under `docs/jikuo/`.
- JIKUO-owned work orders are no longer in the interactive-novel Sprint directory.
- JIKUO-owned governance/product docs are no longer in the interactive-novel governance directory.
- JIKUO-owned schemas are under `docs/jikuo/schemas/`.
- Old JIKUO doc path references are updated or intentionally absent.
- Checker rules recognize new JIKUO work-order paths.
- Code/tests/fixtures reference the new paths.
- JIKUO tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- the user accepts the product-doc boundary
- moved files remain discoverable from `docs/jikuo/README.md`
- no historical NarrativeSystem source-context docs were moved by mistake
- checker smoke passes
- no unrelated local/sidecar changes are staged or committed

---

## 11. Verification Log

Commands run:

```powershell
rg -n "<legacy JIKUO doc path patterns for old Sprint/governance locations>" docs tools .jikuo -g "*"
```

Result:

- no old full-path JIKUO references were found

```powershell
rg --files docs/scenarios/interactive_novel/sprints | rg "SPRINT_050_WO-PER-JIKUO-"
rg --files docs/scenarios/interactive_novel/governance | rg "(^|\\)(jikuo_|task_session\.schema|rule_registry_view_model\.schema)"
```

Result:

- no JIKUO-owned docs remain in the old Sprint/governance directories

```powershell
python -B tools/audit/check_rule_registry_json_output_tests.py
python -B tools/jikuo/project_state_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
python -B tools/jikuo/agent_flow_tests.py
```

Result:

- all tests passed

```powershell
python -B tools/jikuo/agent_flow.py propose --event status --project-root . --format json
```

Result:

- proposal returned `jikuo.agent_flow_proposal.v1`
- project state was read as initialized
- proposal remained no-write

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-DOCS-01_product_doc_rehome_and_reference_migration.md --changed docs/jikuo/README.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/scenarios/interactive_novel/governance/rule_registry.yaml --changed tools/audit/check_rule_registry_json_output_tests.py --changed tools/jikuo/project_state.py --changed tools/jikuo/task_session.py --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-DOCS-01_product_doc_rehome_and_reference_migration.md
```

Result:

- registry validation passed
- triggered `R-006`, `R-012`, and `R-013`
- work-order required fields/sections reported `OK`
- Sprint index required document reported `OK`
- JIKUO layer/kernel fields and sections reported `OK`
- manual declarations remained `REVIEW`, as expected for report-only checker behavior

```powershell
git diff --cached --check
```

Result:

- passed; only existing global git ignore permission warnings were reported

---

## 12. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- moving NarrativeSystem historical context docs into JIKUO
- moving the generic rule registry source
- Skill / MCP / Plugin / frontend / gate implementation
- runtime narrative-engine changes
