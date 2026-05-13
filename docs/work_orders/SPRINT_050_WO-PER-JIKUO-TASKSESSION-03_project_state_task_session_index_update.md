# SPRINT_050_WO-PER-JIKUO-TASKSESSION-03: Project-State Task-Session Index Update

> **Date**: 2026-05-04  
> **Status**: Accepted by user; index dry-run / guarded refresh implemented and ready for user review  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / project-state index update proposal / governance work order  
> **Parent direction**: JIKUO AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md`; `SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md`; `SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`; `.jikuo/project_state.yaml`; `tools/jikuo/task_session.py`  
> **Current slice**: index dry-run / guarded refresh implementation; no root `.jikuo/project_state.yaml` index update during verification, no root `.jikuo/task_sessions/` creation, no task-session file creation by index refresh, no automatic task-session start, no storage adapter, desktop adapter, frontend, gate, checker migration, registry migration, or narrative runtime change  
> **User scenario**: A Codex / Claude desktop APP user has or will have task-session sidecar records and needs JIKUO to expose which recent task sessions belong to the project without scanning raw chat or relying on agent memory.  
> **Runtime chain**: task-session files exist -> index refresh plan -> project-state read / validation -> session file discovery -> latest ref selection -> guarded project-state update -> post-write verification -> desktop-agent summary.  
> **Canonical source**: persisted task-session YAML files under `.jikuo/task_sessions/`, `.jikuo/project_state.yaml`, accepted JIKUO sidecar contracts, `task_session.schema.md`, and explicit user acceptance records.  
> **Bridge object**: `JikuoTaskSessionIndexRefreshPlanV0`; `JikuoTaskSessionIndexRefreshResultV0`; `JikuoProjectStateTaskSessionRefV0`.  
> **Consumer projection**: Codex / Claude desktop APP project-state summary, future auxiliary local helper output, future frontend audit view, future handoff summaries, and future task-run control surfaces.  
> **Lifecycle**: index proposal -> user review -> accepted refresh boundary -> future implementation -> dry-run refresh plan -> guarded index update -> verified / refused / repaired / superseded.  
> **Testing layers**: unit, integration, workflow/orchestration, smoke, human governance review; semantic regression N/A because this work order governs process-state indexing rather than product output quality.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“机括如何知道项目里有哪些任务过程记录”。没有索引，task-session 文件只是散落文件；有索引，机括才能做交接、审计、前端列表和任务历史。

`TASKSESSION-02` made one guarded task-session file write possible.

The next product question is:

- how does project state discover existing task-session records?
- when may `.jikuo/project_state.yaml` be updated?
- should index update happen during `start --write`, or as a separate refresh action?
- how does JIKUO avoid corrupting project-state while updating a small list?
- what should desktop APP users see before and after an index refresh?

Recommended product posture:

- keep task-session file creation and project-state index update as separate base actions
- implement `index --dry-run` before `index --refresh`
- let future desktop-agent cards combine both actions when safe, but keep the underlying operations separately auditable

---

## 2. Scope

> **中文注释**：本工单只定义索引刷新契约，不实现写入。索引不是 session 本身，而是项目状态里的“最近任务记录入口”。

This proposal covers:

- index refresh product boundary
- command shape proposal
- project-state `latest_task_session_refs` update policy
- task-session discovery rules
- project-state preservation requirements
- preflight refusal matrix
- post-write verification requirements
- repair / refresh distinction
- desktop-agent projection expectations
- future implementation test plan

Implemented command shapes:

```powershell
python -B tools/jikuo/task_session.py index --dry-run --format json
python -B tools/jikuo/task_session.py index --refresh --confirm-update-project-state-index --approval-phrase "<exact user phrase as spoken>" --format json
```

---

## 3. Out Of Scope

> **中文注释**：这里继续挡住功能扩张。索引刷新不是自动任务生命周期，也不是前端，也不是 gate。

This work order does not approve:

- code implementation
- `.jikuo/project_state.yaml` modification
- root `.jikuo/task_sessions/` creation
- task-session file creation
- automatic index updates during `start --write`
- automatic task-session writes for every AI task
- audit-event persistence
- rule-proposal persistence
- storage adapter abstraction
- Codex / Claude desktop adapter
- standalone frontend
- task-stop / pre-commit / CI gate
- checker migration
- registry migration
- narrative runtime change
- product-output quality judgment

---

## 4. Audit References

> **中文注释**：索引的源不是聊天记录，而是已持久化的 session 文件和 project-state 文件。

Required references:

- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `.jikuo/project_state.yaml`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`

Current project-local state:

- `.jikuo/project_state.yaml` exists
- `.jikuo/task_sessions/` does not exist in the root project
- `latest_task_session_refs` is empty

---

## 5. Pre-Audit

> **中文注释**：当前没有根项目 session 文件，所以不存在“索引过期”问题。我们是在为未来已写入 session 后的发现能力立契约。

Observed current behavior:

- `start --dry-run` previews a task-session record
- `start --write` can create one session file only when explicitly invoked with confirmation and approval evidence
- `status` can discover persisted session summaries by session id
- `start --write` does not update `.jikuo/project_state.yaml`
- root `.jikuo/task_sessions/` has not been created for the current Codex task
- root `latest_task_session_refs` remains empty

Risk if index update is implemented without this contract:

- project-state may point at missing or invalid session files
- latest refs may drift from actual sidecar files
- unknown project-state fields may be lost during rewrite
- `start --write` may become too coupled and hard to rollback
- desktop APP users may not know whether a durable index was updated

---

## 6. Index Model

> **中文注释**：索引里不应该复制整个 session，只保留“可发现入口”。详细内容仍在 task-session 文件。

`latest_task_session_refs` should remain a compact list of refs.

Recommended ref shape for future schema evolution:

```yaml
latest_task_session_refs:
  - session_id: "<session id>"
    path: ".jikuo/task_sessions/<session id>.yaml"
    task_title: "<task title>"
    owner_agent: "codex"
    created_at: "2026-05-04T00:00:00Z"
    lifecycle_status: "started"
```

Compatibility note:

- current project-state file has `latest_task_session_refs: []`
- first implementation may upgrade this field from empty scalar list to object-list
- unknown project-state fields must be preserved
- unsupported existing non-empty shapes must refuse unless a later migration is approved

---

## 7. Refresh Action Boundary

> **中文注释**：建议先做独立 refresh，而不是把索引更新塞进 `start --write`。这样基础动作更细，未来组合也更稳。

Recommended first implementation:

- add `index --dry-run`
- add `index --refresh`
- do not change `start --write`
- do not make task-session writes automatically update project-state index

Why separate:

- session file creation and project-state update have different failure modes
- `start --write` can stay a small, reliable append-like action
- index refresh can repair stale or missing refs later
- desktop-agent cards can still present them as one product flow when safe

Future product flow:

- task-session write creates the durable process record
- index refresh makes the record discoverable from project state
- desktop APP shows both effects separately

---

## 8. Refresh Plan Object

> **中文注释**：refresh 也要先计划后写入，让用户知道 project_state 会怎么变。

`JikuoTaskSessionIndexRefreshPlanV0` should include:

- `schema`: `jikuo.task_session_index_refresh_plan.v0`
- `project_root`
- `project_state_path`
- `project_state_status`
- `task_sessions_root`
- `discovered_session_count`
- `discovered_session_refs`
- `current_latest_task_session_refs`
- `proposed_latest_task_session_refs`
- `would_update_project_state`
- `approval_required`
- `technical_confirmation_required`
- `unknown_fields_preserved`
- `refusal_reasons`
- `warnings`

Discovery should read task-session summaries, not full raw transcripts.

---

## 9. Refresh Result Object

> **中文注释**：写入结果要能告诉用户“索引是否真的变了、改了什么、有没有保留未知字段”。

`JikuoTaskSessionIndexRefreshResultV0` should include:

- `schema`: `jikuo.task_session_index_refresh_result.v0`
- `operation`: `task_session_index_refresh`
- `status`: `updated`, `no_change`, `refused`, or `error`
- `project_root`
- `project_state_path`
- `updated_project_state_index`
- `previous_latest_task_session_refs`
- `new_latest_task_session_refs`
- `preserved_unknown_fields`
- `backup_path`
- `verification`
- `approval_record`
- `refusal_reasons`
- `warnings`
- `next_actions`

The first implementation should not silently create session files.

---

## 10. Preflight Rules

> **中文注释**：索引更新是改 project-state，比写单个 session 文件风险更高，所以拒绝条件要更保守。

Refresh must refuse when:

- project state is missing
- project state schema is unsupported
- project root in `.jikuo/project_state.yaml` does not match the current project root
- `.jikuo/task_sessions` exists as a file instead of a directory
- `--confirm-update-project-state-index` is absent for refresh mode
- approval evidence is missing for refresh mode
- `latest_task_session_refs` contains an unsupported non-empty shape
- a discovered session file has unsupported schema
- a discovered session file is missing `session_id`
- a discovered session path escapes `.jikuo/task_sessions/`
- a duplicate `session_id` maps to multiple files
- project-state rewrite would drop unknown fields

Refresh may return `no_change` when:

- there are no task-session files and index is already empty
- discovered refs equal current refs

Dirty worktree alone must not be a refusal reason.

---

## 11. Preservation / Backup Policy

> **中文注释**：project_state 是项目本地入口，不能因为更新一个列表就丢其它字段。

Future implementation must:

- preserve unknown project-state fields
- preserve comments if practical; if not practical, declare comment-loss behavior before implementation
- avoid rewriting project-state when proposed refs equal current refs
- write through a temp file
- verify by reading back the updated field
- keep a backup before destructive rewrite if the writer cannot preserve exact formatting

Recommended first implementation posture:

- support the known project-state shape only
- refuse non-empty unknown `latest_task_session_refs` shapes
- preserve known fields and top-level unknown fields
- record whether formatting preservation is exact or normalized

---

## 12. Ref Selection Policy

> **中文注释**：索引应该是最近入口，不是全量数据库。全量记录仍然在 `.jikuo/task_sessions/`。

Recommended first policy:

- discover all `*.yaml` files under `.jikuo/task_sessions/`
- read session id, task title, owner agent, created_at, lifecycle_status
- sort by `created_at` descending, then path ascending
- retain the latest 20 refs by default
- ignore non-YAML files with a warning
- refuse duplicate session ids

Later work may add:

- archive policy
- filtered views
- scenario package grouping
- frontend pagination

---

## 13. Desktop Projection

> **中文注释**：用户不应该需要打开 YAML 才知道索引刷新会做什么。桌面 APP 里应显示“发现几条、将索引几条、会不会写 project_state”。

Desktop-agent projection should show:

- project state path
- task sessions root
- discovered session count
- proposed latest refs
- whether project-state would be updated
- whether unknown fields are preserved
- approval target and effect
- exact user phrase field if approval is given
- non-effects: no session creation, no raw chat logging, no gate

Example approval record should use:

```text
"<exact user phrase as spoken>"
```

---

## 14. Repair / Supersession

> **中文注释**：refresh 可以修复“索引落后于文件”的问题，但不能替用户判断旧 session 是否废弃。

Refresh may repair:

- empty index when session files exist
- stale refs pointing at missing files
- ordering drift
- missing compact metadata that can be read from session files

Refresh must not:

- edit task-session files
- mark sessions superseded
- delete missing files
- infer user acceptance of task completion

Supersession remains a task-session lifecycle action, not an index refresh action.

---

## 15. Testing Governance Declaration

> **中文注释**：测试关注 project-state 索引是否可靠，不评价产品输出内容。

Required testing layers for future implementation:

- unit: parse current refs, discover session files, sort refs, detect duplicates, preserve unknown fields
- integration: empty index with no sessions, empty index with one session, stale index, missing session file, duplicate session id, unsupported schema
- workflow/orchestration: write task session in isolated project -> dry-run index -> refresh index -> status/discovery verifies indexed ref
- smoke: real isolated workspace command proves refresh changes only project-state index and does not create session files
- human governance review: confirm desktop-facing output makes update target/effect/non-effect clear

Semantic regression cases:

- N/A for product-output semantics

Governance regression cases:

- refresh without `--confirm-update-project-state-index` must refuse
- refresh without approval phrase must refuse
- refresh must not create `.jikuo/task_sessions/`
- refresh must not create task-session files
- refresh must preserve existing project-state fields
- duplicate session ids must refuse

---

## 16. Delivery Criteria

> **中文注释**：验收这张工单后，下一步仍然应该是很小的实现：先 dry-run，再受控 refresh。

This proposal is ready for user acceptance when:

- index product purpose is clear
- refresh is separated from task-session write
- index ref shape is defined
- refresh plan and result objects are defined
- refusal matrix is defined
- preservation / backup policy is declared
- testing layers are declared
- no project-state index write has been performed

Future implementation should be considered complete only when:

- unit/integration/workflow/smoke tests pass
- `index --dry-run` can show proposed refs without writing
- `index --refresh` refuses without confirmation and approval evidence
- project-state index updates only when preflight passes
- unknown fields are preserved or refusal behavior is explicit
- no task-session files are created by index refresh
- checker/governance evidence is recorded

---

## 17. Acceptance Gate

> **中文注释**：本工单已被用户以“请继续”接受并进入实现。实现仍然保持最小索引边界。

Accepting this work order approves:

- implementing `tools/jikuo/task_session.py index --dry-run`
- implementing `tools/jikuo/task_session.py index --refresh`
- requiring `--confirm-update-project-state-index`
- requiring `--approval-phrase "<exact user phrase as spoken>"`
- updating only `.jikuo/project_state.yaml` `latest_task_session_refs` after preflight passes
- adding tests for dry-run, refresh, refusal, repair, and preservation behavior

Accepting this work order does not approve:

- automatic index update during `start --write`
- automatic task-session writes for every task
- task-session file creation during index refresh
- audit-event persistence
- rule-proposal persistence
- desktop adapter implementation
- frontend implementation
- gate implementation
- checker migration
- registry migration
- narrative runtime changes

---

## 18. Verification Log

Planned checker command:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md
```

Result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only governance posture preserved
- no root `.jikuo/task_sessions/` directory was created
- root `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Implementation regression command:

```powershell
python -B tools/jikuo/task_session_tests.py
```

Implementation regression result:

- 17 tests passed
- `index --dry-run` reports discovered sessions without writing
- `index --refresh` without confirmation / approval refuses with structured result
- guarded refresh updates only `latest_task_session_refs` in isolated test projects
- guarded refresh does not create task-session files
- duplicate session ids refuse with `duplicate_session_id`
- no-change refresh returns `no_change`
- unknown project-state top-level fields are preserved in the tested path
- root `.jikuo/task_sessions/` was not created during verification
- root `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Root dry-run smoke command:

```powershell
python -B tools/jikuo/task_session.py index --dry-run --format json
```

Root dry-run smoke result:

- returned `jikuo.task_session_index_refresh_plan.v0`
- `discovered_session_count`: `0`
- `would_update_project_state`: `false`
- `can_refresh`: `true`
- no root project write was performed

Implementation governance checker command:

```powershell
python -B tools/audit/check_rule_registry.py --added tools/jikuo/task_session.py --added tools/jikuo/task_session_tests.py --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md
```

Implementation governance checker result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, and `R-004`
- required deterministic work-order fields reported `OK`
- testing-governance section reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only governance posture preserved

Implemented files:

- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`

Still not implemented:

- automatic index update during `start --write`
- automatic task-session writes for every task
- task-session file creation during index refresh
- audit-event persistence
- rule-proposal persistence
- desktop adapter
- frontend
- gate
- checker migration
- registry migration
- narrative runtime changes

---

## 19. Implementation Acceptance Record

> **中文注释**：这次实现把“项目如何发现过程记录”做成受控基础动作，但还没有把它自动接进每个任务。

Decision:

- user accepted this work order by asking to continue after the review point

Implemented effect:

- `tools/jikuo/task_session.py index --dry-run` implemented
- `tools/jikuo/task_session.py index --refresh` implemented
- `--confirm-update-project-state-index` is required for refresh mode
- `--approval-phrase "<exact user phrase as spoken>"` is required as approval evidence
- refresh discovers compact task-session refs from `.jikuo/task_sessions/*.yaml`
- refresh updates only `.jikuo/project_state.yaml` `latest_task_session_refs`
- refresh refuses duplicate session ids
- refresh returns `no_change` when the index is already current
- refresh preserves tested unknown project-state top-level fields
- root project `.jikuo/project_state.yaml` was not updated during verification

Product effect:

- JIKUO now has a reusable guarded action for turning sidecar task-session files into project-level discoverable process-memory entry points.
- This is still not automatic task lifecycle management.

Next recommended work order:

- `JIKUO-TASKSESSION-04`: task-session lifecycle update, evidence append, completion, and handoff boundary

---

## 20. Downstream Acceptance Record

> **中文注释**：用户已要求继续，可以把本实现作为下游生命周期更新工单的输入；这仍然不是 task-session update 写入授权。

Decision:

- accepted for downstream `JIKUO-TASKSESSION-04` lifecycle / evidence / completion / handoff proposal planning

Downstream effect:

- `TASKSESSION-03` index dry-run / guarded refresh may be treated as the upstream project-level discovery contract
- `TASKSESSION-04` may define how an indexed or explicitly selected session receives evidence, verification, completion, and handoff updates
- `TASKSESSION-04` may propose update dry-run and guarded append/update actions

Still not approved by this acceptance:

- task-session update implementation
- automatic lifecycle updates for every task
- raw chat transcript capture
- product-output quality judgement
- automatic project-state index refresh
- supersession implementation
- audit-event persistence
- rule-proposal persistence
- desktop adapter
- frontend
- gate
- checker migration
- registry migration
- narrative runtime change
