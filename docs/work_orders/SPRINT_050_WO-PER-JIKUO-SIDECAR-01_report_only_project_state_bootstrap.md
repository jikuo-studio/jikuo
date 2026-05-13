# SPRINT_050_WO-PER-JIKUO-SIDECAR-01: Report-Only Project State Bootstrap

> **Date**: 2026-05-04  
> **Status**: Accepted by user; report-only status / dry-run helper implemented and accepted for downstream write-mode proposal planning  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / sidecar bootstrap implementation proposal / governance work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`; `SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`; `SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`  
> **Current slice**: report-only implementation completed for `status` and `init --dry-run`; no `.jikuo/` directory creation, sidecar file creation, write mode, storage adapter, renderer, CLI product surface, frontend, checker gate, registry migration, or narrative runtime change  
> **User scenario**: A Codex / Claude desktop APP user wants the project to expose whether JIKUO project-local state is initialized, missing, stale, or unsafe to write before any agent starts persisting governance records.  
> **Runtime chain**: project root discovery -> CORE-04 contract lookup -> sidecar root resolution -> report-only project-state inspection -> optional dry-run bootstrap proposal -> desktop-agent summary -> user acceptance before write implementation.  
> **Canonical source**: accepted `JIKUO-CORE-04` storage contract, accepted work orders and schema documents, `rule_registry.yaml`, and report-only checker baseline.  
> **Bridge object**: `JikuoProjectStateBootstrapReportV0`; future `JikuoProjectLocalStateV0` draft.  
> **Consumer projection**: Codex / Claude desktop APP summary, future auxiliary local command output, future frontend project setup screen, and future sidecar implementation tests.  
> **Lifecycle**: draft implementation proposal -> user review -> accepted implementation boundary -> report-only bootstrap tool -> later write mode only after explicit acceptance.  
> **Testing layers**: unit, integration, workflow/orchestration, smoke, human governance review; semantic regression N/A.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“真正开始 sidecar 之前，怎么安全地知道项目状态是否已经准备好”。

`JIKUO-CORE-04` defines the project-local state contract, but implementation should not jump directly to writing `.jikuo/`.

The first implementation slice should answer:

- where would the JIKUO state root be?
- is it currently absent, initialized, stale, conflicted, or unsafe to write?
- what project-state object would be created if the user later approves initialization?
- can Codex / Claude show that state in chat without requiring the user to operate a frontend?

This work order proposes a report-only bootstrap slice before durable writes.

---

## 2. Scope

> **中文注释**：这个工单是实现前的边界说明；验收后才可以写工具代码。

This slice implements:

- a minimal project-state bootstrap report object
- a local helper command shape
- default dry-run behavior
- no-overwrite and no-silent-write rules
- test coverage for path resolution, bootstrap report generation, state classification, dry-run no-write behavior, and write-mode rejection
- desktop-agent summary expectations

Implemented target:

- `tools/jikuo/project_state.py`
- `tools/jikuo/project_state_tests.py`
- `tools/jikuo/fixtures/**`

Implemented command shape:

```powershell
python -B tools/jikuo/project_state.py status --format text
python -B tools/jikuo/project_state.py status --format json
python -B tools/jikuo/project_state.py init --dry-run --format json
```

Write mode remains intentionally not implemented:

```powershell
python -B tools/jikuo/project_state.py init --write
```

Mainline changed in this implementation slice:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md` acceptance status
- `tools/jikuo/project_state.py`
- `tools/jikuo/project_state_tests.py`
- `tools/jikuo/fixtures/**`

---

## 3. Out Of Scope

> **中文注释**：默认先 report-only。真正写 `.jikuo/` 是下一道门，不在这个待审核工单里直接发生。

This proposal does not approve:

- creating `.jikuo/`
- writing `.jikuo/project_state.yaml`
- writing task sessions, audit events, user decisions, handoffs, or card projections
- implementing a general storage adapter
- modifying `rule_registry.yaml`
- modifying the checker into a gate
- implementing a frontend setup screen
- implementing Codex / Claude desktop adapter behavior
- implementing a product CLI surface beyond a local developer helper
- changing narrative runtime code
- changing Sprint 049 memory lifecycle behavior

Boundary declaration:

- `sprint_049_memory_lifecycle_boundary`: this work order must not implement memory lifecycle or narrative memory state.

---

## 4. Audit References

> **中文注释**：这个实现型工单必须受 CORE-04 约束，而不是自己发明状态模型。

Required references:

- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 5. Pre-Audit

> **中文注释**：第一个 sidecar 实现很容易越界，所以先把风险写在前面。

Primary risks:

- a helper command silently creates `.jikuo/` without user understanding
- a future write mode overwrites user-edited project state
- a bootstrap report is mistaken for canonical acceptance
- YAML/JSON shape drifts from `JIKUO-CORE-04`
- desktop cards summarize state without exposing source paths

Mitigations:

- first accepted implementation should default to `status` and `init --dry-run`
- `--write` should remain a later explicit acceptance point
- all output should declare `report_only: true`
- no existing sidecar file should be overwritten
- source contract references should be included in the report object

---

## 6. Proposed Bootstrap Report Object

> **中文注释**：第一步不是保存状态，而是稳定地报告“如果要保存，会保存什么”。

`JikuoProjectStateBootstrapReportV0` fields:

```yaml
schema: "jikuo.project_state_bootstrap_report.v0"
report_only: true
project_root: "<absolute project root>"
state_root: "<absolute project root>/.jikuo"
state_file: "<absolute project root>/.jikuo/project_state.yaml"
state_status: "missing | initialized | stale_schema | conflict | unsafe"
write_allowed_by_command: false
would_create:
  schema: "jikuo.project_local_state.v0"
  project_id: "<derived project id>"
  accepted_contract_refs: []
  registry_ref: "docs/scenarios/interactive_novel/governance/rule_registry.yaml"
  latest_task_session_refs: []
  latest_rule_proposal_refs: []
  latest_handoff_ref: null
source_refs: []
warnings: []
next_actions: []
```

Rules:

- `state_status` is computed, not guessed from chat.
- `would_create` is a proposal only.
- `write_allowed_by_command` must be `false` for `status` and `init --dry-run`.
- `source_refs` must point to accepted contracts and registry files.
- warnings must be explicit if an existing `.jikuo/` path is a file, unreadable, or contains an unsupported schema.

---

## 7. Proposed Helper Behavior

> **中文注释**：这不是产品 CLI 体验，只是未来 Codex/Claude 可以调用的本地辅助工具。

`status` should:

- discover the project root from current working directory or explicit `--project-root`
- resolve the future sidecar root
- report whether `.jikuo/project_state.yaml` exists
- validate only top-level schema if the file exists
- never create or modify files

`init --dry-run` should:

- produce the `would_create` object
- include source refs
- include warnings
- never create or modify files

`init --write` should:

- remain out of scope for the first implementation unless separately accepted
- require no-overwrite behavior if later approved
- fail if `.jikuo/project_state.yaml` already exists
- emit an audit-friendly result object if later approved

---

## 8. Desktop-Agent Projection

> **中文注释**：用户主要在 Codex / Claude 桌面 APP 里看结果，所以 helper 输出必须能被压缩成一句清楚的卡片。

A desktop-agent summary should show:

- project root
- state status
- future sidecar path
- whether anything was written
- source contract refs
- warnings
- next recommended action

Example card text:

```text
JIKUO project state: missing
Sidecar path: .jikuo/project_state.yaml
Writes performed: no
Next action: review bootstrap proposal before enabling write mode
```

---

## 9. Rollback, Supersession, And Observability

> **中文注释**：哪怕第一步不写状态，也要提前定义回滚和可观察性边界。

Rollback / supersession declaration:

- no rollback is needed for `status` or `init --dry-run` because they do not write files
- future write mode must use no-overwrite behavior and explicit supersession records for meaning changes

Propagation surface declaration:

- local helper output
- desktop-agent summary
- future task-session bootstrap evidence
- future frontend setup view

Observability surface declaration:

- command exit code
- structured JSON output
- text summary
- warnings list
- report-only checker smoke record in the work order

---

## 10. Testing Governance Declaration

> **中文注释**：如果这个工单被验收，下一步实现不能只跑 py_compile；必须证明没有偷偷写文件。

Required test layers for the proposed implementation:

- `unit`: required for path resolution, project id derivation, bootstrap report construction, state-status classification, and no-write defaults.
- `integration`: required for temporary project roots covering missing state, existing valid state, existing stale schema, unsafe `.jikuo` path, and dry-run no-write behavior.
- `workflow_orchestration`: required for the full status -> dry-run proposal -> desktop summary chain.
- `semantic_regression`: N/A because this slice does not change product behavior or narrative behavior.
- `smoke`: required; run the helper status/dry-run command after implementation and run the report-only checker against the work order.
- `human_review`: required for confirming that no write mode, gate, adapter, frontend, or runtime change was silently included.

---

## 11. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| S1-DC-01 | Define product question | Section 1 exists |
| S1-DC-02 | Declare scope and out-of-scope boundaries | Sections 2 and 3 exist |
| S1-DC-03 | Include audit references | Section 4 exists |
| S1-DC-04 | Define report object | Section 6 exists |
| S1-DC-05 | Define helper behavior | Section 7 exists |
| S1-DC-06 | Define desktop-agent projection | Section 8 exists |
| S1-DC-07 | Declare rollback, propagation, and observability surfaces | Section 9 exists |
| S1-DC-08 | Declare testing-governance layers | Section 10 exists |
| S1-DC-09 | Preserve no-write boundary | Sections 2, 3, 6, and 7 exist |
| S1-DC-10 | Run report-only checker smoke | Verification log records checker result |

---

## 12. Acceptance Gate

> **中文注释**：这是 SIDECAR-01 的审核点。你验收后，下一步才真正写 `tools/jikuo/project_state.py`。

This work order is ready for user review when:

- the proposed implementation defaults to report-only status and dry-run behavior
- `.jikuo/` creation remains out of scope
- `init --write` remains out of scope unless separately accepted
- the bootstrap report object is explicit enough for desktop-agent projection
- tests include no-write verification
- no frontend, gate, adapter, checker migration, registry migration, or runtime change is included
- checker smoke has been run

Do not implement `tools/jikuo/project_state.py`, create `.jikuo/`, write sidecar files, or add write mode until the user accepts this work order.

---

## 13. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md
```

Result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved

Implementation verification commands:

```powershell
python -B tools/jikuo/project_state_tests.py
python -B tools/jikuo/project_state.py status --format text
python -B tools/jikuo/project_state.py init --dry-run --format json
Test-Path -Path D:\personal_project\NarrativeSystem\.jikuo
```

Implementation verification result:

- `project_state_tests.py`: 7 tests passed
- `status --format text`: returned `State status: missing`, `Writes performed: no`, and `Write allowed by command: no`
- `init --dry-run --format json`: returned `report_only: true`, `state_status: missing`, `write_allowed_by_command: false`, and a `would_create` draft
- root `.jikuo/` existence check returned `False`
- `init --write` remains unimplemented; `init` without `--dry-run` is rejected

Post-implementation governance checker command:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md --added tools/jikuo/project_state.py --added tools/jikuo/project_state_tests.py --added tools/jikuo/fixtures/missing_project/README.md --added tools/jikuo/fixtures/initialized_project/.jikuo/project_state.yaml --added tools/jikuo/fixtures/stale_project/.jikuo/project_state.yaml --added tools/jikuo/fixtures/conflict_project/.jikuo --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md
```

Post-implementation governance checker result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved

Testing note:

- initial dynamic temporary-directory tests failed because the current Windows sandbox denied access to runtime-created test directories
- tests were changed to static read-only fixtures under `tools/jikuo/fixtures/**` so the test suite verifies state classification without creating sidecar directories during test execution

---

## 14. User Acceptance And Implementation Record

> **中文注释**：用户继续推进，表示 SIDECAR-01 可以实现 report-only helper；这仍然不是写入 `.jikuo/` 的授权。

Decision:

- accepted for implementation of report-only `status` and `init --dry-run`

Implemented effect:

- added `tools/jikuo/project_state.py`
- added `tools/jikuo/project_state_tests.py`
- added static fixtures under `tools/jikuo/fixtures/**`
- report object uses `jikuo.project_state_bootstrap_report.v0`
- `status` and `init --dry-run` never create or modify files
- root `.jikuo/` was not created

Still not approved:

- `.jikuo/` creation
- `.jikuo/project_state.yaml` write
- `init --write`
- general storage adapter
- card renderer
- Codex / Claude adapter behavior
- product CLI surface
- frontend
- gate
- checker migration
- registry migration
- narrative runtime change

---

## 15. Implementation Acceptance Record

> **中文注释**：用户继续推进，表示 SIDECAR-01 的只读实现可作为 SIDECAR-02 的上游输入；这仍然不是写入 `.jikuo/` 的授权。

Decision:

- accepted for downstream `JIKUO-SIDECAR-02` project-state write-mode proposal planning

Recorded effect:

- `tools/jikuo/project_state.py status` may be treated as the accepted report-only state probe
- `tools/jikuo/project_state.py init --dry-run` may be treated as the accepted project-state draft generator
- future write-mode proposal may reference `jikuo.project_state_bootstrap_report.v0`
- no `.jikuo/` creation, `.jikuo/project_state.yaml` write, `init --write`, storage adapter, renderer, Codex/Claude adapter behavior, frontend, gate, checker migration, registry migration, or runtime implementation is approved by this acceptance
