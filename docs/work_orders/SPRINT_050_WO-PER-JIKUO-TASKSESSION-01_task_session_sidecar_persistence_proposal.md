# SPRINT_050_WO-PER-JIKUO-TASKSESSION-01: Task Session Sidecar Persistence Proposal

> **Date**: 2026-05-04
> **Status**: Accepted by user; dry-run task-session helper implemented and accepted for downstream write-mode proposal planning
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / task-session persistence proposal / governance work order
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md`; `SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md`; `SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`; `docs/jikuo/schemas/task_session.schema.md`
> **Current slice**: dry-run task-session helper implemented; no `.jikuo/task_sessions/` directory creation, task-session file creation, project-state index update, storage adapter, desktop adapter, frontend, gate, checker migration, registry migration, or narrative runtime change
> **User scenario**: A Codex / Claude desktop APP user wants each governed AI task to leave a compact, structured, project-local record of triggered rules, required references, evidence, verification, user decisions, completion status, and handoff state without relying on chat memory or dumping raw conversation logs.
> **Runtime chain**: task intent -> task-session draft -> required document mount snapshot -> rule/checker result snapshot -> evidence snapshot -> verification snapshot -> user decision record -> completion state -> handoff summary -> optional project-state index update.
> **Canonical source**: accepted `JIKUO-CORE-03` task-session model, `task_session.schema.md`, accepted project-state sidecar bootstrap, accepted work orders, `rule_registry.yaml`, checker output, and explicit user acceptance records.
> **Bridge object**: `JikuoTaskSessionPersistencePlanV0`; `JikuoTaskSessionSidecarRecordV0`; existing `JikuoTaskSessionV0`.
> **Consumer projection**: Codex / Claude desktop APP task cards, future auxiliary local helper output, future frontend audit view, future handoff summaries, and future gate feasibility analysis.
> **Lifecycle**: persistence proposal -> user review -> accepted task-session write boundary -> future report-only/draft implementation -> future controlled session writes -> indexed / archived / superseded.
> **Testing layers**: unit, integration, workflow/orchestration, smoke, human governance review; semantic regression N/A.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“机括如何记录一次 AI 工作过程”，但不把 sidecar 变成聊天日志。

JIKUO now has:

- a project-local bootstrap state file at `.jikuo/project_state.yaml`
- a report-only project-state helper
- an accepted task-session data model
- desktop-agent projection contracts

The next useful persistence layer is a task session.

A task session should answer:

- what work was attempted?
- which governance scenario chain applied?
- which references were required?
- which rules/checks were triggered?
- which evidence was produced or missing?
- which user decisions were recorded?
- what was verified?
- what should the next agent know?

It should not become a raw transcript archive.

---

## 2. Scope

> **中文注释**：这里只定义 task-session sidecar 怎么写，暂不实现写入。

This implementation covers:

- future task-session sidecar root planning
- file naming and identity rules
- minimal session record shape
- capture/minimal-retention rules
- write and update policy boundary
- project-state index update boundary
- desktop-agent projection expectations
- refusal and supersession rules
- dry-run start plan helper and tests

Implemented targets:

- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`
- `tools/jikuo/fixtures/task_session_ready_project/.jikuo/project_state.yaml`

Implemented command shapes:

```powershell
python -B tools/jikuo/task_session.py start --dry-run --task-title "<task title>" --format json
python -B tools/jikuo/task_session.py status --session-id "<session id>" --format json
```

Future write command remains out of scope:

```powershell
python -B tools/jikuo/task_session.py start --write --task-title "<task title>" --confirm-create-task-session --format json
```

Mainline changed in this implementation slice:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md` acceptance status
- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`
- `tools/jikuo/fixtures/task_session_ready_project/.jikuo/project_state.yaml`

---

## 3. Out Of Scope

> **中文注释**：不要让“任务记录”偷偷扩成全量日志、审查系统或自动 gate。

This implementation does not approve:

- creating `.jikuo/task_sessions/`
- writing task-session files
- updating `.jikuo/project_state.yaml`
- persisting audit events outside task-session records
- persisting rule proposals
- persisting handoff files outside task-session records
- dumping raw chat transcripts
- storing secrets or environment dumps
- evaluating product-output quality
- implementing Codex / Claude desktop adapter behavior
- implementing frontend audit views
- implementing gates
- changing checker enforcement
- modifying `rule_registry.yaml`
- changing narrative runtime code
- changing Sprint 049 memory lifecycle behavior

Boundary declaration:

- `sprint_049_memory_lifecycle_boundary`: this work order must not implement memory lifecycle or narrative memory state.

---

## 4. Audit References

> **中文注释**：task session 必须服从已验收的数据模型和 sidecar 边界。

Required references:

- `docs/jikuo/schemas/task_session.schema.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md`
- `.jikuo/project_state.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 5. Pre-Audit

> **中文注释**：task session 是机括真正开始“接住过程”的地方，最容易被误做成日志系统。

Risks:

- task-session persistence becomes raw chat logging
- user decisions are stored without target/effect
- evidence is recorded as prose with no source paths
- project-state index is updated before the session file is valid
- failed tasks leave active sessions that future agents treat as accepted
- task-session records grow into product-output judgement records
- repeated agents create overlapping sessions for the same task without ownership/supersession

Mitigations:

- store structured task fields, not raw chat
- store exact user phrases only for decisions
- require source refs for evidence and document mounts
- keep product-output quality judgement out of scope
- require owner/session identity and lifecycle status
- write session file first, then update project-state index only after verification
- use supersession instead of silent mutation when meaning changes

---

## 6. Sidecar Location And Naming

> **中文注释**：路径必须稳定，且不要和项目代码混在一起。

Future task-session root:

```text
.jikuo/task_sessions/
```

Future file naming proposal:

```text
.jikuo/task_sessions/<UTC timestamp>_<task slug>_<short id>.yaml
```

Example:

```text
.jikuo/task_sessions/20260504T154233Z_tasksession_sidecar_persistence_a1b2c3.yaml
```

Rules:

- task-session files are append-friendly records with explicit lifecycle status
- filenames must be deterministic enough for humans to scan and unique enough to avoid collision
- `short id` should be derived from session identity, not random chat text
- project root paths in records should be absolute only when needed; source refs should prefer repo-relative paths
- no task-session file should overwrite an existing file

---

## 7. Task Session Record Shape

> **中文注释**：这里不是重新发明 schema，而是把现有 `JikuoTaskSessionV0` 映射到 sidecar 写入边界。

`JikuoTaskSessionSidecarRecordV0` fields:

```yaml
schema: "jikuo.task_session.v0"
session:
  session_id: "<stable id>"
  task_title: "<short task title>"
  owner_agent: "codex | claude | other"
  created_at: "<UTC timestamp>"
  updated_at: "<UTC timestamp>"
  lifecycle_status: "draft | active | completion_proposed | accepted | revision_requested | superseded | archived"
scenario:
  scenario_chain_id: "<scenario id>"
  scenario_package: "engineering_governance"
changed_surfaces: []
rule_results: []
document_mounts: []
evidence_snapshots: []
verification: []
user_decisions: []
completion:
  status: "not_started | in_progress | proposed | accepted | revision_requested"
handoff:
  summary: null
audit_trail: []
supersession:
  supersedes: []
  superseded_by: null
```

Required initial fields:

- `schema`
- `session.session_id`
- `session.task_title`
- `session.owner_agent`
- `session.created_at`
- `session.lifecycle_status`
- `scenario.scenario_package`
- `completion.status`

---

## 8. Capture Policy

> **中文注释**：记录“治理过程”，不保存“聊天全部内容”。

Allowed capture:

- task title / task intent summary
- changed path list
- required reference file list
- rule/checker result snapshots
- evidence statuses
- verification commands and summarized results
- explicit user decisions with exact phrase, target, and effect
- completion state
- handoff summary
- supersession links

Disallowed capture by default:

- raw chat transcript
- hidden chain-of-thought
- secrets, tokens, environment dumps, or credentials
- product-output quality judgement
- narrative runtime state
- unrelated local filesystem inventory
- user phrase capture without a decision target/effect

Phrase capture rule:

```yaml
phrase: "<exact user phrase as spoken>"
decision_target: "<explicit target>"
decision_effect: "<explicit effect>"
```

The phrase stores what the user actually said. It is not a required command format.

---

## 9. Write And Update Policy

> **中文注释**：task session 会变化，但不能随手覆盖关键语义。

Future write policy:

- creating a new task session requires project state to be initialized
- session creation should be explicit at task start or first governed action
- session file creation uses no-overwrite behavior
- routine evidence additions may append/update structured fields within the same active session
- user decisions must be append-friendly and preserve exact target/effect
- lifecycle transitions must be explicit
- accepted completion must not be silently changed to draft
- meaning-changing corrections should use supersession or audit-trail entries

Future update categories:

- `append_evidence`
- `record_checker_result`
- `record_user_decision`
- `update_completion_status`
- `write_handoff_summary`
- `supersede_session`

Not allowed without later work order:

- automatic every-message logging
- background daemon writes
- multi-session merging
- cross-project session migration
- gate-driven blocking behavior

---

## 10. Project-State Index Boundary

> **中文注释**：`.jikuo/project_state.yaml` 是索引，不是日志。更新它必须很克制。

Future task-session implementation may propose updating:

```yaml
latest_task_session_refs:
  - ".jikuo/task_sessions/<session file>.yaml"
```

Rules:

- update project-state index only after the task-session file is successfully written and verified
- preserve existing unknown fields
- never rewrite accepted contract refs unless a separate contract update is approved
- never use project-state index as the only copy of task-session content
- if project-state index update fails after session file write, report partial success and next action
- do not store full session content inside `project_state.yaml`

---

## 11. Desktop-Agent Projection

> **中文注释**：用户主要在 Codex / Claude 桌面 APP 中连续工作，所以 task session 要能被压缩成清楚的状态卡。

Task-start card should show:

- session id
- task title
- owner agent
- required references
- triggered or expected governance rules
- evidence currently missing
- whether anything was persisted

Completion card should show:

- session id
- completion status
- changed surfaces
- verification summary
- missing/review evidence
- user decisions recorded
- handoff summary availability

Card rule:

- cards are projections, not canonical truth
- source session path must be shown when a session record exists
- missing persistence should be visible as `review`, not hidden in prose

---

## 12. Refusal And Supersession Rules

> **中文注释**：宁可拒绝写，也不要写出一个未来 Agent 会误信的状态。

Future task-session write must refuse when:

- `.jikuo/project_state.yaml` is missing or stale
- session id collides with an existing file
- task title is empty
- owner agent is unknown
- required schema version is unsupported
- target session is not active and update kind requires active status
- update attempts to overwrite an accepted user decision
- update attempts to remove evidence without supersession

Supersession must be used when:

- task ownership changes after a handoff conflict
- a session was created for the wrong task
- evidence was attached to the wrong session
- completion status was accepted in error
- a later work order replaces the persistence contract

---

## 13. Testing Governance Declaration

> **中文注释**：未来实现时，测试重点是结构化、可恢复、可拒绝，而不是“能写一个文件就算完成”。

Required test layers for future implementation:

- `unit`: required for session id generation, filename validation, schema shape, capture policy validation, lifecycle transition validation, project-state index update planning, and refusal matrix.
- `integration`: required for isolated project roots covering missing project state, initialized project state, session create dry-run, session create write, duplicate session refusal, invalid lifecycle update refusal, project-state index update, and partial-failure reporting.
- `workflow_orchestration`: required for task start -> evidence snapshot -> checker result -> user decision -> completion -> handoff summary.
- `semantic_regression`: N/A because this slice does not change product behavior or narrative behavior.
- `smoke`: required; run future task-session helper commands, existing project-state helper status, and report-only governance checker.
- `human_review`: required before implementation because this is the first persistent record of governed AI task execution.

---

## 14. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| T1-DC-01 | Define product question | Section 1 exists |
| T1-DC-02 | Declare scope and out-of-scope boundaries | Sections 2 and 3 exist |
| T1-DC-03 | Include audit references | Section 4 exists |
| T1-DC-04 | Define sidecar location and naming | Section 6 exists |
| T1-DC-05 | Define task-session record shape | Section 7 exists |
| T1-DC-06 | Define capture policy | Section 8 exists |
| T1-DC-07 | Define write/update policy | Section 9 exists |
| T1-DC-08 | Define project-state index boundary | Section 10 exists |
| T1-DC-09 | Define desktop projection and refusal rules | Sections 11 and 12 exist |
| T1-DC-10 | Declare testing-governance layers | Section 13 exists |
| T1-DC-11 | Run report-only checker smoke | Verification log records checker result |

---

## 15. Acceptance Gate

> **中文注释**：这是 TASKSESSION-01 dry-run helper 的实现验收点。验收后才考虑 task-session write mode。

This implementation is ready for user review when:

- it clearly distinguishes task-session persistence from raw chat logging
- it defines `.jikuo/task_sessions/` location and file naming
- it maps to `JikuoTaskSessionV0` / `task_session.schema.md`
- it defines allowed and disallowed capture
- it protects exact user phrases with target/effect
- it defines project-state index update as a controlled boundary
- it defines refusal and supersession rules
- it implements dry-run start/status only
- it defines tests for dry-run/refusal/status paths
- it does not implement task-session writing
- checker smoke has been run

Do not create `.jikuo/task_sessions/`, write task-session files, update `.jikuo/project_state.yaml`, add desktop adapters, add frontend views, add gates, migrate registry, or change runtime until the user accepts a later work order.

---

## 16. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md
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
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session.py start --dry-run --task-title "Task Session Sidecar Persistence" --format json
python -B tools/jikuo/task_session.py status --session-id task_missing_session_00000000 --format json
Test-Path -Path D:\personal_project\NarrativeSystem\.jikuo\task_sessions
Get-Content -Encoding UTF8 -Path D:\personal_project\NarrativeSystem\.jikuo\project_state.yaml
```

Implementation verification result:

- `task_session_tests.py`: 6 tests passed
- `start --dry-run`: returned `jikuo.task_session_start_plan.v0`
- `report_only`: `true`
- `project_state_status`: `initialized`
- `write_allowed_by_command`: `false`
- `can_start`: `true`
- `would_create.schema`: `jikuo.task_session.v0`
- capture policy reports `raw_chat_transcript: disallowed`
- `status --session-id task_missing_session_00000000`: returned `jikuo.task_session_status.v0` with `session_status: not_found`
- `.jikuo/task_sessions/` existence check returned `False`
- `.jikuo/project_state.yaml` still has `latest_task_session_refs: []`

Implementation governance checker command:

```powershell
python -B tools/audit/check_rule_registry.py --added tools/jikuo/task_session.py --added tools/jikuo/task_session_tests.py --added tools/jikuo/fixtures/task_session_ready_project/.jikuo/project_state.yaml --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md
```

Implementation governance checker result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, and `R-004`
- required deterministic work-order fields reported `OK`
- testing-governance section reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved

Implemented files:

- `tools/jikuo/task_session.py`
- `tools/jikuo/task_session_tests.py`
- `tools/jikuo/fixtures/task_session_ready_project/.jikuo/project_state.yaml`

Still not implemented:

- `.jikuo/task_sessions/` creation
- task-session file write
- project-state index update
- audit-event persistence
- rule-proposal persistence
- desktop adapter
- frontend
- gate
- checker migration
- registry migration
- narrative runtime change

---

## 17. Implementation Acceptance Record

> **中文注释**：用户继续推进，表示 TASKSESSION-01 可实现 dry-run helper；这不是 task-session 写入授权。

Decision:

- accepted for implementation of dry-run task-session start/status helper

Implemented effect:

- added `tools/jikuo/task_session.py`
- added `tools/jikuo/task_session_tests.py`
- added a static initialized-project fixture for task-session planning
- dry-run start plans now expose the future session id, target session path, `JikuoTaskSessionV0` record draft, source refs, and capture policy
- status reports are read-only and return `not_found` when no persisted session exists
- `.jikuo/task_sessions/` was not created
- `.jikuo/project_state.yaml` was not updated

Still not approved:

- `start --write`
- `.jikuo/task_sessions/` creation
- task-session file writes
- project-state index update
- automatic chat logging
- desktop adapter
- frontend
- gate
- checker migration
- registry migration
- narrative runtime change

---

## 18. Downstream Acceptance Record

> **中文注释**：用户已接受 dry-run helper，可以继续规划 write mode；这仍然不是写入授权。

Decision:

- accepted for downstream `JIKUO-TASKSESSION-02` write-mode proposal planning

Downstream effect:

- `TASKSESSION-01` dry-run start/status behavior may be treated as the upstream preview contract
- future write-mode planning may reference the existing `jikuo.task_session_start_plan.v0` shape
- future write-mode planning may reference the existing no-raw-chat capture policy

Still not approved by this acceptance:

- `start --write`
- `.jikuo/task_sessions/` creation
- task-session file writes
- project-state index update
- automatic chat logging
- desktop adapter
- frontend
- gate
- checker migration
- registry migration
- narrative runtime change
