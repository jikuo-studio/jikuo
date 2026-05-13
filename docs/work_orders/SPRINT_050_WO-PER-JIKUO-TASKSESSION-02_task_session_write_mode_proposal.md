# SPRINT_050_WO-PER-JIKUO-TASKSESSION-02: Task Session Write Mode Proposal

> **Date**: 2026-05-04
> **Status**: Accepted by user; guarded write mode implemented and ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / task-session write-mode proposal / governance work order
> **Parent direction**: JIKUO AI-primary process governance kernel; current engineering-governance application track
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md`; `SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md`; `SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`; `docs/jikuo/schemas/task_session.schema.md`; `.jikuo/project_state.yaml`
> **Current slice**: guarded write-mode implementation; no automatic task-session writing, no project-root task-session file created during verification, no project-state index update, storage adapter, desktop adapter, frontend, gate, checker migration, registry migration, or narrative runtime change
> **User scenario**: A Codex / Claude desktop APP user wants a governed AI task to become a durable, compact, project-local process record only after the task-start contract is clear and the write boundary is explicit; the record must support future handoff and audit without storing raw chat logs.
> **Runtime chain**: initialized project state -> dry-run task-session start plan -> desktop-agent review / user acceptance -> write preflight -> task-session file creation -> post-write verification -> optional later project-state index update.
> **Canonical source**: accepted `TASKSESSION-01` dry-run helper behavior, `task_session.schema.md`, `.jikuo/project_state.yaml`, accepted JIKUO contracts, `rule_registry.yaml`, checker output, and explicit user acceptance records.
> **Bridge object**: `JikuoTaskSessionWritePlanV0`; `JikuoTaskSessionWriteResultV0`; `JikuoTaskSessionSidecarRecordV0`.
> **Consumer projection**: Codex / Claude desktop APP task-start cards, future auxiliary local helper output, future frontend audit view, future handoff summaries, and future gate feasibility analysis.
> **Lifecycle**: write-mode proposal -> user review -> accepted write boundary -> future implementation -> controlled session file write -> verified / refused / superseded -> later index update proposal.
> **Testing layers**: unit, integration, workflow/orchestration, smoke, human governance review; semantic regression N/A because this work order governs engineering process records rather than judging product output quality.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“什么时候可以把一次 AI 工作写成机括的项目本地过程记忆”。它不回答“这次工作结果好不好”，也不把聊天记录保存成日志。

`TASKSESSION-01` proved that JIKUO can generate a dry-run task-session plan without writing files.

The next product question is:

- when is a dry-run plan allowed to become a durable task-session sidecar record?
- which approval and technical confirmation must exist before writing?
- what must be refused to prevent accidental process-state pollution?
- how can the first write remain useful to desktop APP users without becoming raw transcript capture?

This matters because JIKUO needs process continuity across Codex / Claude desktop sessions. The durable record should remember the governed task shape, required references, evidence status, decisions, verification, and handoff state.

It should not remember everything the user and agent said.

---

## 2. Scope

> **中文注释**：本工单只定义 write mode 的契约，不实现写入。它把未来实现要守的边界先钉住。

This proposal covers:

- write-mode approval boundary
- write command shape
- write plan object
- write result object
- task-session file path and no-overwrite policy
- preflight refusal matrix
- post-write verification requirements
- desktop-agent projection expectations
- future implementation test plan

Future implementation target, if accepted later:

```powershell
python -B tools/jikuo/task_session.py start --write --task-title "<task title>" --confirm-create-task-session --approval-phrase "<exact user phrase as spoken>" --format json
```

The existing dry-run command remains the safe preview path:

```powershell
python -B tools/jikuo/task_session.py start --dry-run --task-title "<task title>" --format json
```

---

## 3. Out Of Scope

> **中文注释**：这里刻意把容易扩张的内容挡住，避免“写一个 session 文件”变成整套产品一次性落地。

This work order does not approve:

- code implementation
- `.jikuo/task_sessions/` directory creation
- task-session file creation
- `.jikuo/project_state.yaml` index update
- automatic chat transcript logging
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

> **中文注释**：这些是本次写入契约必须参考的源，不是因为它们会被全部复制进 sidecar，而是因为它们决定写入边界。

Required references:

- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `.jikuo/project_state.yaml`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`

Current project-local state:

- `.jikuo/project_state.yaml` exists
- `.jikuo/task_sessions/` does not exist
- `latest_task_session_refs` is empty

---

## 5. Pre-Audit

> **中文注释**：当前系统已经能预演，但还不能写入。这个状态是有意保持的安全边界。

Observed current behavior:

- `tools/jikuo/task_session.py start --dry-run` produces `jikuo.task_session_start_plan.v0`
- `tools/jikuo/task_session.py status` is read-only
- missing persisted sessions return `session_status: not_found`
- dry-run output exposes the future target path and draft `jikuo.task_session.v0` record
- capture policy marks raw chat transcript as disallowed
- `.jikuo/task_sessions/` is still absent
- `.jikuo/project_state.yaml` is still not indexing any task session

Risk if write mode is implemented without this contract:

- task sessions may become chat logs instead of process records
- sessions may be written without clear user-facing effect
- duplicate session ids may overwrite prior process history
- project-state indexes may drift from actual sidecar files
- desktop APP users may not know what became durable

---

## 6. Approval / Activation Contract

> **中文注释**：机括的批准不是固定咒语，而是“用户说过什么、批准了什么目标、会产生什么写入效果”三者同时可审计。

Write mode requires two layers:

- human-facing approval evidence
- technical confirmation flag

Human-facing approval evidence must capture:

- approval target: task-session file creation
- expected effect: create one compact task-session sidecar record
- non-effect: no raw chat transcript capture
- exact user phrase as spoken, represented in examples as `"<exact user phrase as spoken>"`
- approving agent or surface
- timestamp if available

Technical confirmation flag:

```powershell
--confirm-create-task-session
```

The future implementation must refuse `--write` if the confirmation flag is absent.

The command flag is not a replacement for human approval. It is a guard against accidental invocation.

---

## 7. Write Plan Object

> **中文注释**：先输出计划，再执行写入。这样桌面 APP 用户能看到“会写什么”，而不是只看到命令成功。

`JikuoTaskSessionWritePlanV0` should include:

- `schema`: `jikuo.task_session_write_plan.v0`
- `project_root`
- `project_state_path`
- `project_state_status`
- `session_id`
- `session_path`
- `task_title`
- `record_schema`: `jikuo.task_session.v0`
- `source_refs`
- `capture_policy`
- `approval_required`
- `technical_confirmation_required`
- `would_create_directory`
- `would_create_file`
- `would_update_project_state_index`
- `refusal_reasons`
- `warnings`

For this first write-mode proposal:

- `would_create_directory` may be `true` when `.jikuo/task_sessions/` is absent
- `would_create_file` may be `true` after all preflight checks pass
- `would_update_project_state_index` must be `false`

---

## 8. Write Result Object

> **中文注释**：写入结果也要是结构化对象，让未来前端、handoff、审计面板都能读懂。

`JikuoTaskSessionWriteResultV0` should include:

- `schema`: `jikuo.task_session_write_result.v0`
- `operation`: `task_session_start_write`
- `status`: `written`, `refused`, or `error`
- `session_id`
- `session_path`
- `created_directory`
- `created_file`
- `updated_project_state_index`
- `verification`
- `approval_evidence`
- `refusal_reasons`
- `warnings`
- `next_actions`

For the first write-mode implementation:

- `updated_project_state_index` must remain `false`
- `next_actions` should mention that project-state index update requires a later accepted work order

---

## 9. Preflight Rules

> **中文注释**：这些拒绝条件是产品安全阀。它们让“任务过程记忆”不会被不完整、不明确或重复的写入污染。

Write mode must refuse when:

- project state is missing
- project state schema is unsupported
- project root in `.jikuo/project_state.yaml` does not match the current project root
- `.jikuo/task_sessions` exists as a file instead of a directory
- generated `session_id` collides with an existing file
- `--confirm-create-task-session` is absent
- task title is empty or whitespace-only
- source refs required by the draft record cannot be resolved
- write target escapes `.jikuo/task_sessions/`
- the planned record contains a raw chat transcript field
- approval evidence is missing when the future command requires persisted approval evidence

Write mode may warn, but not necessarily refuse, when:

- task title is unusually long
- optional evidence fields are not yet populated
- optional timestamps are unavailable
- current git worktree is dirty

Dirty worktree alone must not be a refusal reason because JIKUO often governs work that is in progress.

---

## 10. File Creation And No-Overwrite Policy

> **中文注释**：第一次 session 写入要像创建账本条目，不像覆盖草稿。能新增，不能悄悄改旧记录。

Future implementation must:

- create `.jikuo/task_sessions/` only after preflight passes
- write exactly one new task-session file
- refuse if the target file already exists
- avoid overwriting any existing sidecar file
- verify the written file by reading it back
- return a structured result

Recommended file naming:

```text
.jikuo/task_sessions/<session_id>.yaml
```

Recommended write behavior:

- generate deterministic-enough session id from timestamp and sanitized task title
- resolve target path under `.jikuo/task_sessions/`
- open the target with exclusive create semantics
- write YAML with stable field order where practical
- read back and validate required top-level fields

---

## 11. Project-State Index Update Boundary

> **中文注释**：本轮建议先只写 session 文件，不同时更新项目索引。业务意义是先证明“单条过程记忆”可靠，再处理“全局索引一致性”。

This proposal deliberately keeps project-state index update out of the first write-mode implementation.

First accepted implementation, if approved later:

- may create `.jikuo/task_sessions/`
- may create one task-session file
- must not update `.jikuo/project_state.yaml`

Later work order should decide:

- when `latest_task_session_refs` is updated
- whether index update is part of `start --write` or a separate `index --refresh` operation
- how to preserve unknown project-state fields
- how to recover from session-write success but index-update failure
- how many recent session refs should be retained

This separation reduces coupling and keeps the first durable task-session write auditable.

---

## 12. Desktop Projection

> **中文注释**：对 Codex / Claude 桌面 APP 用户来说，这一步最终应该表现为一张清楚的任务开始卡，而不是要求用户理解 YAML 写入细节。

A desktop-agent projection should show:

- task title
- session id
- target path
- capture policy summary
- required references snapshot
- whether raw chat transcript capture is disallowed
- whether project-state index update is excluded
- approval target
- expected write effect
- exact user phrase field if approval has been given

The projection should make clear:

- this creates a compact process record
- this does not judge task quality
- this does not store raw chat logs
- this does not enable gates
- this does not update the global latest-session index in the first slice

---

## 13. Refusal / Supersession

> **中文注释**：拒绝不是失败，而是防止过程状态变脏。supersession 是为了让未来任务变更有清楚的继承关系。

Refusal cases must be visible in the result object.

Examples:

- `project_state_missing`
- `unsupported_project_state_schema`
- `project_root_mismatch`
- `task_sessions_path_conflict`
- `session_id_collision`
- `missing_confirmation_flag`
- `empty_task_title`
- `target_path_escape`
- `raw_chat_transcript_disallowed`
- `approval_evidence_missing`

Supersession remains out of first implementation but must be reserved by schema fields:

- `supersedes`
- `superseded_by`
- `supersession_reason`

The first implementation should not silently edit a previous session to mark supersession.

---

## 14. Testing Governance Declaration

> **中文注释**：本工单的测试对象是工程过程记录写入，不是叙事输出质量。

Required testing layers for future implementation:

- unit: session id generation, target path resolution, preflight refusal reasons, no raw transcript field, empty title handling
- integration: initialized project fixture, missing project state fixture, path conflict fixture, collision fixture, successful write fixture
- workflow/orchestration: dry-run preview -> accepted write command -> post-write status -> no project-state index update
- smoke: real workspace command that proves `.jikuo/task_sessions/<session_id>.yaml` is created only when write mode is explicitly invoked
- human governance review: confirm approval target/effect/non-effect are clear in desktop-facing output

Semantic regression cases:

- N/A for product-output semantics

Governance regression cases:

- write mode without `--confirm-create-task-session` must refuse
- write mode must not create raw chat transcript fields
- write mode must not overwrite an existing session file
- write mode must not update `.jikuo/project_state.yaml` in the first slice
- missing project state must refuse before creating `.jikuo/task_sessions/`

---

## 15. Delivery Criteria

> **中文注释**：如果用户接受这张工单，下一步也仍然只做一个很小的可验收实现。

This proposal is ready for user acceptance when:

- write-mode product purpose is clear
- out-of-scope boundaries are explicit
- approval and technical confirmation are separated
- write plan and write result objects are defined
- refusal matrix is defined
- project-state index update is deferred
- testing layers are declared
- no code or sidecar task-session writes have been performed

Future implementation should be considered complete only when:

- unit/integration/workflow/smoke tests pass
- `.jikuo/task_sessions/` is only created by explicit write mode
- exactly one task-session file is created per accepted write
- status can read the persisted session
- `.jikuo/project_state.yaml` remains unchanged in the first slice
- checker/governance evidence is recorded

---

## 16. Acceptance Gate

> **中文注释**：本工单已被用户以“请继续”接受并进入实现。实现仍然保持最小写入边界。

Accepting this work order approves:

- implementing `tools/jikuo/task_session.py start --write`
- requiring `--confirm-create-task-session`
- creating `.jikuo/task_sessions/` only during accepted write mode
- creating one new task-session YAML file
- keeping project-state index update out of this slice
- adding tests for the write/refusal behavior

Accepting this work order does not approve:

- automatic task-session writes for every task
- raw chat transcript capture
- `.jikuo/project_state.yaml` index updates
- desktop adapter implementation
- frontend implementation
- gate implementation
- audit-event persistence
- rule-proposal persistence
- runtime narrative changes

---

## 17. Verification Log

Planned checker command:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md
```

Result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved
- no `.jikuo/task_sessions/` directory was created
- `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Existing helper regression command:

```powershell
python -B tools/jikuo/task_session_tests.py
```

Existing helper regression result:

- superseded by implementation regression below
- `.jikuo/task_sessions/` still does not exist in the project root after the test run
- `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Implementation regression command:

```powershell
python -B tools/jikuo/task_session_tests.py
```

Implementation regression result:

- 10 tests passed
- dry-run start still does not write
- `start --write` without confirmation / approval refuses with structured result
- `start --write --confirm-create-task-session --approval-phrase "<exact user phrase as spoken>"` creates one task-session YAML file in an isolated test project
- duplicate deterministic session target refuses with `session_id_collision`
- project-root mismatch refuses with `project_root_mismatch`
- `status` can read a persisted task-session summary
- project-state index update remains `false`
- root `.jikuo/task_sessions/` was not created during verification
- root `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Implementation governance checker command:

```powershell
python -B tools/audit/check_rule_registry.py --added tools/jikuo/task_session.py --added tools/jikuo/task_session_tests.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md
```

Implementation governance checker result:

- registry validation passed
- triggered `R-006` and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declaration reported `REVIEW`
- exit code `0`
- report-only governance posture preserved

Implemented files:

- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`

Still not implemented:

- automatic task-session writes for every task
- root project task-session creation for this current Codex task
- `.jikuo/project_state.yaml` index update
- audit-event persistence
- rule-proposal persistence
- desktop adapter
- frontend
- gate
- checker migration
- registry migration
- narrative runtime change

---

## 18. Implementation Acceptance Record

> **中文注释**：这次实现把“过程记忆写入”做成一个受控基础动作，但还没有把它自动接进每个任务。

Decision:

- user accepted this work order by asking to continue after the review point

Implemented effect:

- `tools/jikuo/task_session.py start --write` implemented
- `--confirm-create-task-session` is required for write mode
- `--approval-phrase "<exact user phrase as spoken>"` is required as approval evidence
- write mode creates `.jikuo/task_sessions/` only inside the selected project root and only after preflight passes
- write mode creates exactly one new task-session YAML file per successful invocation
- write mode refuses overwrite / collision
- write mode refuses project-root mismatch
- write mode does not update `.jikuo/project_state.yaml`
- `status` can read persisted task-session summaries

Product effect:

- JIKUO now has a reusable guarded action for turning a task-start plan into one durable process-memory record.
- This is still not automatic task lifecycle management.

Next recommended work order:

- `JIKUO-TASKSESSION-03`: project-state task-session index update and repair/refresh policy

---

## 19. Downstream Acceptance Record

> **中文注释**：用户已要求继续，可以把本实现作为下游索引刷新工单的输入；这仍然不是索引写入授权。

Decision:

- accepted for downstream `JIKUO-TASKSESSION-03` project-state task-session index update proposal planning

Downstream effect:

- `TASKSESSION-02` guarded task-session write mode may be treated as the upstream session-file creation contract
- `TASKSESSION-03` may define how existing session files become discoverable from `.jikuo/project_state.yaml`
- `TASKSESSION-03` may propose `index --dry-run` and `index --refresh`

Still not approved by this acceptance:

- `.jikuo/project_state.yaml` index update implementation
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
- narrative runtime change
