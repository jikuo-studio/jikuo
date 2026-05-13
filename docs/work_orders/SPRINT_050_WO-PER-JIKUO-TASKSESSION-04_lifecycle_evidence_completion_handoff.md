# SPRINT_050_WO-PER-JIKUO-TASKSESSION-04: Task-Session Lifecycle, Evidence, Completion, And Handoff Boundary

> **Date**: 2026-05-04
> **Status**: Accepted by user; lifecycle update dry-run / guarded append implemented and ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / task-session lifecycle update proposal / governance work order
> **Parent direction**: JIKUO AI-primary process governance kernel; current engineering-governance application track
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md`; `SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md`; `docs/jikuo/schemas/task_session.schema.md`; `tools/jikuo/task_session.py`
> **Current slice**: lifecycle/evidence/completion/handoff update implementation; no root task-session file update during verification, no root `.jikuo/task_sessions/` creation, no project-state index update, no automatic task-session writes, no storage adapter, desktop adapter, frontend, gate, checker migration, registry migration, or narrative runtime change
> **User scenario**: A Codex / Claude desktop APP user wants a governed task record to move from start/index into useful process memory: what evidence was produced, what checks were run, what the user accepted, what remains open, and what the next agent should know.
> **Runtime chain**: existing task-session ref -> selected session -> update dry-run plan -> stale-session / ownership preflight -> append evidence or verification -> record user decision -> set completion/handoff state -> verify updated session -> optional later index refresh.
> **Canonical source**: persisted task-session YAML files under `.jikuo/task_sessions/`, `task_session.schema.md`, checker output, explicit user decisions, accepted JIKUO sidecar contracts, and explicit user acceptance records.
> **Bridge object**: `JikuoTaskSessionUpdatePlanV0`; `JikuoTaskSessionUpdateResultV0`; `JikuoTaskSessionEvidencePatchV0`; `JikuoTaskSessionCompletionPatchV0`; `JikuoTaskSessionHandoffPatchV0`.
> **Consumer projection**: Codex / Claude desktop APP completion cards, future auxiliary local helper output, future frontend audit view, future handoff summaries, and future task-run control surfaces.
> **Lifecycle**: update proposal -> user review -> accepted update boundary -> future implementation -> dry-run update plan -> guarded append/update -> verified / refused / superseded.
> **Testing layers**: unit, integration, workflow/orchestration, smoke, human governance review; semantic regression N/A because this work order governs process-state updates rather than product output quality.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：前三步解决了“项目有状态入口、任务记录能创建、记录能被索引”。这张工单回答“这条任务记录如何随着实际工作变得有用”。

JIKUO currently has:

- project-local state bootstrap
- task-session dry-run start plan
- guarded task-session file creation
- guarded task-session index refresh

But a created task session is still mostly a start record.

The next product question is:

- how does a task session receive evidence after work happens?
- how are verification commands recorded?
- when does user acceptance become a durable decision?
- how is completion represented without pretending product quality was judged automatically?
- what should be handed off to the next Codex / Claude session?

Recommended product posture:

- treat lifecycle updates as append-oriented, targeted patches
- keep user decisions explicit and exact-phrase based
- record engineering evidence and verification, not raw chat transcripts
- keep product-output quality judgement outside automatic engineering governance

---

## 2. Scope

> **中文注释**：本工单只定义生命周期更新契约，不实现写入。它决定哪些内容未来可以追加到 session 里。

This proposal covers:

- task-session update command boundary
- update target selection rules
- evidence append contract
- verification append contract
- user decision append contract
- completion state contract
- handoff summary contract
- stale / wrong-session refusal matrix
- no raw transcript policy
- future implementation test plan

Implemented command shapes:

```powershell
python -B tools/jikuo/task_session.py update --dry-run --session-id "<session id>" --format json
python -B tools/jikuo/task_session.py update --append-evidence --session-id "<session id>" --evidence-kind "<kind>" --evidence-ref "<ref>" --confirm-update-task-session --approval-phrase "<exact user phrase as spoken>" --format json
python -B tools/jikuo/task_session.py complete --session-id "<session id>" --status accepted --summary "<summary>" --confirm-complete-task-session --approval-phrase "<exact user phrase as spoken>" --format json
python -B tools/jikuo/task_session.py handoff --session-id "<session id>" --summary "<handoff summary>" --confirm-update-task-session --approval-phrase "<exact user phrase as spoken>" --format json
```

The exact command surface may be split in implementation, but the underlying actions should remain distinct.

---

## 3. Out Of Scope

> **中文注释**：生命周期更新不是自动审美判断，也不是聊天记录归档，也不是每轮任务自动落盘。

This work order does not approve:

- code implementation
- task-session file updates
- automatic task-session writes for every task
- automatic project-state index refresh
- raw chat transcript capture
- product-output quality judgement
- editing prior task-session evidence except through explicit supersession
- deleting task-session files
- audit-event persistence as a separate object family
- rule-proposal persistence
- storage adapter abstraction
- Codex / Claude desktop adapter
- standalone frontend
- task-stop / pre-commit / CI gate
- checker migration
- registry migration
- narrative runtime change

---

## 4. Audit References

> **中文注释**：生命周期更新的源来自 task-session schema、checker 输出、用户明确验收和已有 session 文件，不来自“模型觉得应该记录什么”。

Required references:

- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `.jikuo/project_state.yaml`
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`

Current project-local state:

- `.jikuo/project_state.yaml` exists
- root `.jikuo/task_sessions/` does not exist
- `latest_task_session_refs` is empty

---

## 5. Pre-Audit

> **中文注释**：当前根项目没有实际 task-session，所以本工单不处理已有记录迁移。它定义未来有记录之后怎么安全更新。

Observed current behavior:

- `start --dry-run` previews a session
- `start --write` can create one session file when explicitly invoked
- `index --dry-run` previews discoverable refs
- `index --refresh` can update latest refs when explicitly invoked
- `status` can read persisted session summaries
- root project has no task-session file
- root project index remains empty

Risk if lifecycle update is implemented without this contract:

- agents may append evidence to the wrong session
- task sessions may become chat logs
- user acceptance may be implied instead of recorded
- verification may be confused with product-quality judgement
- handoff summaries may drift from actual completed work
- stale sessions may keep receiving updates after supersession

---

## 6. Update Target Selection

> **中文注释**：所有更新都必须指向明确 session，不能默认“最近一个”就写。未来桌面卡可以帮用户选择，但底层命令要清楚。

Future implementation should support:

- explicit `--session-id`
- optional selection from `latest_task_session_refs` in desktop-agent projection
- exact matched session path in dry-run output

First implementation should refuse when:

- session id is missing
- session id matches zero files
- session id matches more than one file
- matched file escapes `.jikuo/task_sessions/`
- matched file schema is unsupported
- session is already terminal unless update kind explicitly allows handoff clarification
- session owner does not match when owner guard is enabled

Default posture:

- do not update by implicit latest session
- do not update all sessions
- do not create a session during update

---

## 7. Patch Families

> **中文注释**：不同更新要拆成不同 patch，避免“完成任务”时顺手塞进一堆不清楚来源的内容。

Recommended patch families:

- `EvidencePatch`: append a structured evidence snapshot
- `VerificationPatch`: append command/check result evidence
- `UserDecisionPatch`: append exact user decision target/effect/non-effect
- `CompletionPatch`: update completion status and summary
- `HandoffPatch`: update handoff summary and next-action notes
- `SupersessionPatch`: reserved for later stale-session / replacement semantics

Each patch should include:

- patch id
- patch kind
- target session id
- source refs
- created_at
- actor / surface
- approval record if required
- expected fields changed
- non-effects

---

## 8. Evidence Append Contract

> **中文注释**：evidence 是工程过程证据，不是产品好坏评价。比如 checker 输出、测试命令、改动路径、审核记录。

Evidence append should support:

- checker result references
- test command summaries
- changed path summaries
- work-order verification logs
- user approval records
- manual review required notes

Evidence append must not support:

- raw chat transcript
- unrestricted model memory dump
- product-output quality judgement as an automatic result
- hidden private data not referenced by the user

Evidence records should include:

- `evidence_id`
- `evidence_kind`
- `source_ref`
- `summary`
- `status`: `ok`, `missing`, `review`, `not_applicable`, or `error`
- `recorded_at`
- `recorded_by`

---

## 9. Verification Append Contract

> **中文注释**：verification 记录“跑了什么、结果是什么、范围是什么”，不是笼统说“已验证”。

Verification append should include:

- command or checker name
- command scope
- result status
- exit code when available
- relevant output summary
- known limitations
- whether the verification is unit, integration, workflow, smoke, or human governance review

Verification append must refuse:

- empty verification summary
- missing command/check name for automated checks
- verification claimed as semantic/product review when no human review evidence exists

---

## 10. User Decision Contract

> **中文注释**：用户决定必须记录“说了什么、批准什么、不会产生什么效果”，避免一句“继续”被无限泛化。

User decisions should include:

- exact user phrase as spoken, represented in examples as `"<exact user phrase as spoken>"`
- decision target
- decision effect
- decision non-effect
- surface
- recorded_at
- related patch id

Some updates require explicit user decision:

- completion accepted
- handoff finalized
- supersession
- changing terminal status
- any update that writes user intent rather than tool evidence

Tool-generated evidence may be appendable with technical confirmation only, if a later work order accepts that boundary.

---

## 11. Completion Contract

> **中文注释**：完成态是工程任务状态，不代表产品输出自动达标。用户验收仍是显式 decision。

Completion status values:

- `not_started`
- `in_progress`
- `blocked`
- `ready_for_review`
- `accepted`
- `superseded`
- `abandoned`

First implementation should allow:

- `in_progress` -> `ready_for_review`
- `ready_for_review` -> `accepted`
- `in_progress` -> `blocked`
- any non-terminal -> `abandoned` with explicit decision

First implementation should refuse:

- terminal -> non-terminal without later supersession policy
- `accepted` without user decision evidence
- empty completion summary
- completion update on missing session

Completion summary should be concise and process-focused:

- what was changed
- what was verified
- what remains open
- next recommended action

---

## 12. Handoff Contract

> **中文注释**：handoff 是为了 Codex / Claude 桌面会话连续性，不是完整聊天转录。

Handoff should include:

- short summary
- current status
- relevant files changed or referenced
- verification status
- open risks / unresolved items
- next recommended action
- source session id

Handoff must not include:

- raw chat transcript
- speculative product-quality judgement
- unrelated user private context

Handoff may be updated after completion only when:

- it is marked as handoff clarification
- it does not change completion acceptance
- it records approval evidence if user intent is added

---

## 13. Stale / Wrong-Session Refusal

> **中文注释**：生命周期更新最大的风险是写错 session，所以拒绝条件要比创建文件更严格。

Update must refuse when:

- session id matches zero files
- session id matches multiple files
- session file schema is unsupported
- session id inside file does not match requested id
- session path escapes `.jikuo/task_sessions/`
- update patch has no target field changes
- update would remove existing evidence
- update would overwrite existing evidence by id
- update would change user decision text
- update would capture raw chat transcript
- update would mark accepted without explicit user decision evidence
- update would modify terminal session status without accepted supersession policy

Dirty worktree alone must not be a refusal reason.

---

## 14. Desktop Projection

> **中文注释**：桌面 APP 用户应该看到“这次会追加什么、影响什么、不影响什么”，而不是被迫理解 YAML patch。

Desktop-agent projection should show:

- target session id and title
- target file path
- current lifecycle status
- patch kind
- fields that would change
- evidence refs that would be appended
- approval target/effect/non-effect
- exact user phrase field if required
- refusal reasons
- post-update next action

Projection should distinguish:

- evidence append
- verification append
- completion acceptance
- handoff update
- supersession

---

## 15. Testing Governance Declaration

> **中文注释**：测试关注过程状态更新是否可靠，不评价产品输出内容。

Required testing layers for future implementation:

- unit: patch validation, session selection, terminal status rules, evidence id collision, raw transcript refusal
- integration: append evidence to isolated session, append verification, complete session, add handoff, wrong session refusal, duplicate match refusal
- workflow/orchestration: start session -> index refresh -> append evidence -> append verification -> complete -> handoff -> status reads updated summary
- smoke: real isolated workspace command proves update changes only the target task-session file
- human governance review: confirm desktop-facing output makes target/effect/non-effect clear

Semantic regression cases:

- N/A for product-output semantics

Governance regression cases:

- update without explicit session id must refuse
- completion accepted without user decision evidence must refuse
- update must not capture raw chat transcript
- update must not remove prior evidence
- handoff must not change accepted completion status unless a later policy approves it
- wrong-session / duplicate-session matches must refuse

---

## 16. Delivery Criteria

> **中文注释**：验收这张工单后，下一步仍然应该是小实现：先 dry-run patch，再受控 append/update。

This proposal is ready for user acceptance when:

- lifecycle product purpose is clear
- update target selection rules are explicit
- patch families are defined
- evidence / verification / decision / completion / handoff boundaries are separated
- stale / wrong-session refusal matrix is defined
- testing layers are declared
- no task-session update has been performed

Future implementation should be considered complete only when:

- unit/integration/workflow/smoke tests pass
- update dry-run can show proposed patch without writing
- guarded update refuses without required confirmation or approval evidence
- evidence append is append-only
- completion accepted requires explicit user decision evidence
- handoff update does not capture raw chat transcript
- checker/governance evidence is recorded

---

## 17. Acceptance Gate

> **中文注释**：本工单已被用户以“请继续”接受并进入实现。实现仍然保持显式 session-id 和受控追加边界。

Accepting this work order approves:

- implementing task-session update dry-run
- implementing guarded evidence append
- implementing guarded verification append
- implementing guarded completion update
- implementing guarded handoff update
- requiring explicit `--session-id`
- requiring approval evidence for user-decision and completion updates
- adding tests for append-only updates, wrong-session refusal, and no raw transcript capture

Accepting this work order does not approve:

- automatic task-session lifecycle updates for every task
- raw chat transcript capture
- product-output quality judgement
- automatic project-state index refresh
- supersession implementation
- audit-event persistence as a separate object family
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
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md
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

- 24 tests passed
- update dry-run selects an explicit session without writing
- evidence append refuses without confirmation / approval
- guarded evidence append updates only the target session file
- guarded verification append updates only the target session file
- accepted completion requires explicit user decision evidence
- guarded completion writes completion status and user decision
- guarded handoff writes handoff summary without changing project-state index
- terminal accepted sessions refuse late evidence append
- duplicate session matches refuse
- raw chat transcript marker refuses
- root `.jikuo/task_sessions/` was not created during verification
- root `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Root update dry-run smoke command:

```powershell
python -B tools/jikuo/task_session.py update --dry-run --session-id task_missing_session_00000000 --format json
```

Root update dry-run smoke result:

- returned `jikuo.task_session_update_plan.v0`
- `patch_kind`: `inspect`
- `would_update_task_session`: `false`
- `would_update_project_state_index`: `false`
- `refusal_reasons`: `task_sessions_root_missing`
- no root project write was performed

Implementation governance checker command:

```powershell
python -B tools/audit/check_rule_registry.py --added tools/jikuo/task_session.py --added tools/jikuo/task_session_tests.py --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md
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

- automatic task-session lifecycle updates for every task
- raw chat transcript capture
- product-output quality judgement
- automatic project-state index refresh
- supersession implementation
- audit-event persistence as a separate object family
- rule-proposal persistence
- desktop adapter
- frontend
- gate
- checker migration
- registry migration
- narrative runtime changes

---

## 19. Implementation Acceptance Record

> **中文注释**：这次实现让 task session 能承载任务推进过程，但还没有把这些动作自动接到每次 Codex / Claude 工作流里。

Decision:

- user accepted this work order by asking to continue after the review point

Implemented effect:

- `tools/jikuo/task_session.py update --dry-run` implemented
- `tools/jikuo/task_session.py update --append-evidence` implemented
- `tools/jikuo/task_session.py update --append-verification` implemented
- `tools/jikuo/task_session.py complete` implemented
- `tools/jikuo/task_session.py handoff` implemented
- all lifecycle write actions require explicit `--session-id`
- guarded lifecycle writes require technical confirmation and approval phrase
- evidence / verification append is append-only in the implemented path
- accepted completion requires explicit user decision evidence
- handoff update is allowed after completion without changing completion acceptance
- raw chat transcript markers are refused
- duplicate session matches are refused
- root project `.jikuo/task_sessions/` was not created during verification

Product effect:

- JIKUO now has a reusable guarded action set for turning a task-session file into a living process record: evidence, verification, completion, and handoff can be represented without raw chat logging.
- This is still not automatic desktop-agent workflow orchestration.

Next recommended work order:

- `JIKUO-AGENT-02`: desktop-agent task-session workflow cards and command composition

---

## 20. Downstream Acceptance Record

> **中文注释**：用户已经验收本实现结果，因此可以把它作为 `JIKUO-AGENT-02` 的上游命令契约。这里不代表自动桌面适配器已经被批准。

Decision:

- user accepted this work order for downstream `JIKUO-AGENT-02` planning by asking to continue after implementation review

Accepted upstream effects for downstream planning:

- task-session lifecycle dry-run exists
- guarded evidence append exists
- guarded verification append exists
- guarded completion exists
- guarded handoff exists
- explicit `--session-id` is required for lifecycle updates
- guarded lifecycle writes require confirmation flag and `--approval-phrase "<exact user phrase as spoken>"`
- raw chat transcript capture remains refused
- root project `.jikuo/task_sessions/` was not created during verification
- root project `.jikuo/project_state.yaml` index was not updated during verification

Still not approved:

- desktop adapter
- automatic task-session writes
- automatic evidence capture
- automatic project-state index refresh
- frontend
- gate
- checker migration
- registry migration
- runtime narrative-engine changes
