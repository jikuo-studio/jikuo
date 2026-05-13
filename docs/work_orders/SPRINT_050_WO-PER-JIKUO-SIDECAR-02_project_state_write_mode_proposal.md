# SPRINT_050_WO-PER-JIKUO-SIDECAR-02: Project State Write Mode Proposal

> **Date**: 2026-05-04  
> **Status**: Accepted by user; initial project-state write mode implemented and project root state initialized; accepted for downstream task-session persistence proposal planning  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / sidecar write-mode proposal / governance work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md`; `SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`; `SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`  
> **Current slice**: initial project-state write mode implemented; `.jikuo/project_state.yaml` created for project-local JIKUO bootstrap state; no task-session persistence, audit-event persistence, rule-proposal persistence, general storage adapter, renderer, CLI product surface, frontend, checker gate, registry migration, or narrative runtime change  
> **User scenario**: A Codex / Claude desktop APP user has reviewed the report-only bootstrap result and wants a future agent to initialize JIKUO project-local state only after an explicit, auditable approval, with no overwrite or hidden persistence.  
> **Runtime chain**: report-only bootstrap result -> desktop-agent approval card -> exact user approval phrase -> write-mode preflight -> atomic project-state initialization -> post-write verification -> audit-ready summary.  
> **Canonical source**: accepted `JIKUO-CORE-04`, implemented `JIKUO-SIDECAR-01` report-only helper, accepted work orders and schema documents, `rule_registry.yaml`, and explicit user acceptance records.  
> **Bridge object**: `JikuoProjectStateWritePlanV0`; `JikuoProjectStateWriteResultV0`; `JikuoProjectLocalStateV0`.  
> **Consumer projection**: Codex / Claude desktop APP approval card, future auxiliary local helper output, future task-session evidence, future frontend setup/audit view.  
> **Lifecycle**: write-mode proposal -> user review -> accepted write boundary -> future implementation work order -> explicit user approval per write -> project-state file initialized -> verified / failed / superseded.  
> **Testing layers**: unit, integration, workflow/orchestration, smoke, human governance review; semantic regression N/A.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“什么时候才可以真的创建 `.jikuo/project_state.yaml`，以及怎么保证不是偷偷写”。

`JIKUO-SIDECAR-01` intentionally stopped at report-only status and dry-run bootstrap.

The next dangerous boundary is write mode.

If JIKUO creates `.jikuo/project_state.yaml`, that becomes the first durable project-local governance state. This is useful for cross-agent continuity, but it also creates new risks:

- hidden persistence
- mistaken acceptance
- accidental overwrite
- ambiguous ownership
- write behavior that feels like a CLI side effect instead of a desktop-agent-visible decision

This work order defines and records the initial write-mode contract.

---

## 2. Scope

> **中文注释**：这里只定义写入阀门，不打开阀门。

This implementation covers:

- when write mode is allowed
- which user approval must exist before a write
- which command flags a future helper must require
- which preflight checks must pass
- how initial project-state creation should be atomic
- how no-overwrite behavior should work
- what post-write verification must report
- what tests are required before implementation acceptance

Implementation target:

- extend `tools/jikuo/project_state.py`
- extend `tools/jikuo/project_state_tests.py`

Implemented command shape:

```powershell
python -B tools/jikuo/project_state.py init --write --confirm-create-project-state --format json
```

Mainline changed in this implementation slice:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md` acceptance status
- `tools/jikuo/project_state.py`
- `tools/jikuo/project_state_tests.py`
- `.jikuo/project_state.yaml`

---

## 3. Out Of Scope

> **中文注释**：本工单不创建 `.jikuo/`。它只定义未来创建时的安全条件。

This implementation does not approve:

- overwriting `.jikuo/project_state.yaml`
- writing any additional sidecar files beyond the initial project-state file
- writing task sessions, audit events, user decisions, handoffs, rule proposals, or card projections
- implementing a general storage adapter
- implementing a product CLI surface beyond the local helper
- implementing Codex / Claude adapter behavior
- implementing a card renderer
- implementing a frontend setup screen
- modifying `rule_registry.yaml`
- modifying the checker into a gate
- changing narrative runtime code
- changing Sprint 049 memory lifecycle behavior

Boundary declaration:

- `sprint_049_memory_lifecycle_boundary`: this work order must not implement memory lifecycle or narrative memory state.

---

## 4. Audit References

> **中文注释**：写入契约必须依赖已验收的只读探针和存储契约。

Required references:

- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 5. Pre-Audit

> **中文注释**：写 sidecar 是机括从“观察者”变成“状态参与者”的第一步，所以要谨慎。

Risks:

- write mode becomes a hidden side effect of normal task execution
- agent treats vague continuation as approval to create durable state
- `.jikuo/` exists for unrelated reasons and is overwritten or reused unsafely
- write succeeds but post-write verification is skipped
- future agents trust a file whose schema or source refs are stale
- CLI confirmation token is mistaken for fixed user phrase

Mitigations:

- require an explicit desktop-agent approval record before write
- require a technical confirmation flag in the helper command
- never infer approval from generic continuation
- allow initial write only when state root is absent
- fail instead of writing when `.jikuo/` exists without `project_state.yaml`
- verify the written file immediately after creation
- emit a structured write result

---

## 6. Approval Contract

> **中文注释**：用户不需要说固定口令；但系统必须记录“批准了什么、会产生什么后果”。

Future write mode requires two separate layers:

- human approval evidence
- technical command confirmation

Human approval evidence must include:

- `decision_target`: `JIKUO project-state initialization`
- `decision_effect`: `create .jikuo/project_state.yaml`
- `source_report_schema`: `jikuo.project_state_bootstrap_report.v0`
- `source_report_state_status`: `missing`
- `phrase`: `"<exact user phrase as spoken>"`

Technical command confirmation may use a fixed flag:

- `--confirm-create-project-state`

The fixed flag is not a required user phrase. It is only a tool-level guard so accidental command invocation fails.

Generic user continuations such as `"<exact user phrase as spoken>"` are valid only when the desktop-agent card clearly states the target and effect. They must not be reinterpreted as blanket approval for unrelated writes.

---

## 7. Write Plan Object

> **中文注释**：真正写入前，要先能展示“准备写什么”。

`JikuoProjectStateWritePlanV0` fields:

```yaml
schema: "jikuo.project_state_write_plan.v0"
report_only: false
write_kind: "initial_project_state"
project_root: "<absolute project root>"
state_root: "<absolute project root>/.jikuo"
state_file: "<absolute project root>/.jikuo/project_state.yaml"
preflight_state_status: "missing"
requires_human_approval: true
requires_command_confirmation: true
no_overwrite: true
atomic_write: true
would_write:
  schema: "jikuo.project_local_state.v0"
source_refs: []
approval_record_ref: null
warnings: []
```

Rules:

- plan generation itself must not write files
- `preflight_state_status` must be computed by the existing report-only helper
- `would_write` must match the `would_create` draft from the accepted bootstrap report unless explicitly superseded
- `approval_record_ref` is required for actual write execution once task-session persistence exists

---

## 8. Write Result Object

> **中文注释**：写完之后不能只说“成功”，必须说明写了哪里、写入前后状态是什么。

`JikuoProjectStateWriteResultV0` fields:

```yaml
schema: "jikuo.project_state_write_result.v0"
write_performed: true
write_kind: "initial_project_state"
project_root: "<absolute project root>"
state_root: "<absolute project root>/.jikuo"
state_file: "<absolute project root>/.jikuo/project_state.yaml"
preflight_state_status: "missing"
post_write_state_status: "initialized"
created_paths:
  - ".jikuo/"
  - ".jikuo/project_state.yaml"
overwritten_paths: []
approval_record:
  phrase: "<exact user phrase as spoken>"
  decision_target: "JIKUO project-state initialization"
  decision_effect: "create .jikuo/project_state.yaml"
source_refs: []
warnings: []
next_actions: []
```

Rules:

- `overwritten_paths` must remain empty for initial write mode
- `post_write_state_status` must be computed by re-reading the file
- result must distinguish `write_performed: false` failures from successful writes
- failed writes must report cleanup status if temporary files or directories were created

---

## 9. Preflight Rules

> **中文注释**：如果前置条件不干净，宁愿失败，不要“帮用户处理一下”。

Future write mode may proceed only when all conditions are true:

- project root resolves successfully
- report-only helper returns `state_status: missing`
- `.jikuo/` does not exist
- `--write` is present
- `--confirm-create-project-state` is present
- desktop-agent approval record exists in the active task evidence
- approval target and effect match project-state initialization
- source bootstrap report is not stale relative to current project root
- `rule_registry.yaml` source ref exists

Future write mode must fail when:

- `.jikuo/` already exists
- `.jikuo` exists as a file
- `.jikuo/project_state.yaml` already exists
- project root cannot be resolved
- approval is absent, ambiguous, or targets another action
- source report says `initialized`, `stale_schema`, `conflict`, or `unsafe`

---

## 10. Atomic Write And Rollback

> **中文注释**：第一次写入也要像真正的状态迁移一样严肃。

Proposed atomic sequence:

1. Re-run `status`.
2. Verify `state_status: missing` and `.jikuo/` absent.
3. Create `.jikuo/`.
4. Write `.jikuo/project_state.yaml.tmp`.
5. Flush and close the temporary file.
6. Move temporary file to `.jikuo/project_state.yaml` only if the target does not exist.
7. Re-run `status`.
8. Emit write result.

Rollback / cleanup rules:

- if directory creation succeeds but file write fails, remove only the newly created `.jikuo/` if it is still empty
- if temporary file exists after failure, remove only the known temporary file
- never delete pre-existing `.jikuo/`
- never overwrite `project_state.yaml`
- if cleanup fails, report `cleanup_status: failed` and exact path

---

## 11. Desktop-Agent Projection

> **中文注释**：写入批准应该主要发生在 Codex / Claude 桌面 APP 里，而不是要求用户理解 CLI flag。

Future desktop card should show:

- action: initialize JIKUO project state
- path to be created: `.jikuo/project_state.yaml`
- writes to be performed: yes
- overwritten paths: none
- source bootstrap status: missing
- approval effect: project will gain durable JIKUO governance state
- not included: task sessions, audit events, gates, frontend, runtime changes

Example projection:

```text
JIKUO write proposal: initialize project state
Will create: .jikuo/project_state.yaml
Will overwrite: nothing
Requires approval: yes
This does not enable gates or write task sessions.
```

---

## 12. Testing Governance Declaration

> **中文注释**：未来实现 write mode 时，测试重点不是“能写”，而是“只有在该写时才写、任何模糊情况都不写”。

Required test layers for future implementation:

- `unit`: required for approval validation, command confirmation validation, preflight classification, write plan construction, write result construction, and no-overwrite failure paths.
- `integration`: required for temporary isolated workspace cases covering absent state root, existing state root, existing state file, conflicting `.jikuo` file, stale schema file, failed approval, missing confirmation flag, successful initial write, and post-write verification.
- `workflow_orchestration`: required for status -> dry-run -> approval evidence -> write plan -> write result -> desktop summary.
- `semantic_regression`: N/A because this slice does not change product behavior or narrative behavior.
- `smoke`: required; run status, init dry-run, write-mode tests, and report-only governance checker after implementation.
- `human_review`: required before any implementation because this is the first durable JIKUO sidecar write.

---

## 13. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| S2-DC-01 | Define product question | Section 1 exists |
| S2-DC-02 | Declare scope and out-of-scope boundaries | Sections 2 and 3 exist |
| S2-DC-03 | Include audit references | Section 4 exists |
| S2-DC-04 | Define approval contract | Section 6 exists |
| S2-DC-05 | Define write plan and write result objects | Sections 7 and 8 exist |
| S2-DC-06 | Define preflight rules | Section 9 exists |
| S2-DC-07 | Define atomic write and rollback rules | Section 10 exists |
| S2-DC-08 | Define desktop-agent projection | Section 11 exists |
| S2-DC-09 | Declare testing-governance layers | Section 12 exists |
| S2-DC-10 | Run report-only checker smoke | Verification log records checker result |

---

## 14. Acceptance Gate

> **中文注释**：这是 SIDECAR-02 实现后的验收点。下一步不能自动扩大到 task session 或 audit event 写入。

This implementation is ready for user review when:

- it distinguishes user approval phrase from technical confirmation flag
- it keeps fixed command flags out of the user interaction contract
- it allows write only for initial project-state creation
- it rejects overwrite and ambiguous state
- it defines preflight, atomic write, cleanup, and post-write verification
- it defines tests for both success and refusal paths
- it does not approve any additional persistence layer
- checker smoke has been run

Do not add task-session persistence, audit-event persistence, rule-proposal persistence, general storage adapter, card renderer, Codex/Claude adapter behavior, frontend, gates, registry migration, or runtime changes until the user accepts a later work order.

---

## 15. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md
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
$phrase = @'
请继续
如果你想要创建项目根目录也是可以的，注意路径和引用的正确性，避免项目创建、文件移动带来的错误
'@
python -B tools/jikuo/project_state.py init --write --confirm-create-project-state --approval-phrase $phrase --format json
python -B tools/jikuo/project_state.py status --format json
$phrase = 'repeat should fail'; python -B tools/jikuo/project_state.py init --write --confirm-create-project-state --approval-phrase $phrase --format json
Test-Path -Path D:\personal_project\NarrativeSystem\.jikuo\project_state.yaml
```

Implementation verification result:

- `project_state_tests.py`: 11 tests passed
- initial write returned `jikuo.project_state_write_result.v0`
- `write_performed`: `true`
- `preflight_state_status`: `missing`
- `post_write_state_status`: `initialized`
- `created_paths`: `.jikuo/`, `.jikuo/project_state.yaml`
- `overwritten_paths`: `[]`
- approval record stored the exact user phrase from the accepting turn
- post-write `status --format json` returned `state_status: initialized`
- repeated write returned exit code `1`, `write_performed: false`, `preflight_state_status: initialized`, and `overwritten_paths: []`
- `.jikuo/project_state.yaml` existence check returned `True`

Final governance checker command:

```powershell
python -B tools/audit/check_rule_registry.py --added .jikuo/project_state.yaml --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md --added tools/jikuo/fixtures/write_ready_project/docs/scenarios/interactive_novel/governance/rule_registry.yaml --changed tools/jikuo/project_state.py --changed tools/jikuo/project_state_tests.py --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md
```

Final governance checker result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved

Created project-state file:

- `.jikuo/project_state.yaml`

Still not implemented:

- task-session persistence
- audit-event persistence
- user-decision persistence
- handoff persistence
- rule-proposal persistence
- general storage adapter
- card renderer
- Codex / Claude adapter behavior
- frontend
- gate
- checker migration
- registry migration
- narrative runtime change

---

## 16. Implementation Acceptance Record

> **中文注释**：用户继续推进，表示 SIDECAR-02 的实现可作为 TASKSESSION-01 的上游输入；这不是 task-session 写入授权。

Decision:

- accepted for downstream `JIKUO-TASKSESSION-01` task-session sidecar persistence proposal planning

Recorded effect:

- `.jikuo/project_state.yaml` may be treated as initialized project-local JIKUO bootstrap state
- `tools/jikuo/project_state.py status` may be used to verify project-state readiness before task-session planning
- future task-session persistence proposal may reference `latest_task_session_refs` as an index boundary
- no `.jikuo/task_sessions/` creation, task-session write, audit-event persistence, rule-proposal persistence, storage adapter, desktop adapter, frontend, gate, checker migration, registry migration, or runtime implementation is approved by this acceptance
