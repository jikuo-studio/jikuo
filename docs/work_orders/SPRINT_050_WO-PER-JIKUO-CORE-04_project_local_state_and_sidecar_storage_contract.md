# SPRINT_050_WO-PER-JIKUO-CORE-04: Project Local State And Sidecar Storage Contract

> **Date**: 2026-05-04  
> **Status**: Accepted by user for downstream report-only sidecar bootstrap planning  
> **Primary sprint**: Sprint 050 / JIKUO productization incubation  
> **Task type**: productization / project-local state contract / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`; `SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`; `SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`; `SPRINT_050_WO-PER-JIKUO-FLOW-01_engineering_governance_user_journey_and_interaction_flow.md`; `SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`; `SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`; `SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`  
> **Current slice**: storage contract only; no `.jikuo/` directory creation, sidecar file creation, storage adapter, renderer, CLI, frontend, checker, gate, registry migration, or runtime implementation  
> **User scenario**: A Codex / Claude desktop APP user needs JIKUO governance state to persist across agent turns and app handoffs without relying on chat memory, while keeping every durable write auditable and user-approved when it changes rules or task ownership.  
> **Runtime chain**: project discovery -> state root resolution -> accepted contract lookup -> sidecar object proposal -> user decision -> durable project-local record -> desktop card projection -> next-agent handoff.  
> **Canonical source**: accepted work orders, accepted schema documents, `rule_registry.yaml`, checker output, task-session schema, desktop-agent card contract, and explicit user acceptance records.  
> **Bridge object**: `JikuoProjectLocalStateV0`; `JikuoProjectSidecarLayoutV0`; `JikuoDurableGovernanceRecordV0`.  
> **Consumer projection**: Codex / Claude desktop APP governance cards, future auxiliary CLI reports, future frontend configuration/audit views, future handoff summaries, and future gate feasibility analysis.  
> **Lifecycle**: proposed layout -> user review -> accepted storage contract -> future report-only sidecar implementation -> future read/write adapters -> future UI / gate integration only after separate approval.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Question

> **中文注释**：这张工单回答“机括的项目状态未来应该放在哪里、如何被 Codex 和 Claude 共享、哪些东西可以持久化”。

JIKUO is intended to work inside the user's active AI-development flow, especially Codex and Claude desktop APP sessions.

That means governance state cannot live only in:

- chat memory
- one agent's transient context
- a frontend database that the desktop agent cannot see
- a CLI-only output that the user does not naturally operate
- unreviewed side effects hidden inside scripts

The system needs a project-local state contract before any storage implementation.

This work order defines the contract for future sidecar state. It does not create the sidecar.

---

## 2. Scope

> **中文注释**：本工单只定义未来 sidecar 的语义边界和数据类别，不实现写入。

This slice covers:

- project-local governance state ownership
- sidecar layout proposal
- canonical source hierarchy
- durable object families
- write-safety rules
- desktop-agent continuity rules
- privacy and exact-phrase capture rules
- compatibility and migration boundaries
- relationship to existing JIKUO schemas and work orders

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md` acceptance status

---

## 3. Out Of Scope

> **中文注释**：这里非常重要：不因为讨论存储契约，就偷偷开始实现存储。

This slice does not:

- create `.jikuo/`
- create sidecar JSON / YAML / SQLite files
- modify `rule_registry.yaml`
- implement a storage adapter
- implement a desktop card renderer
- implement Codex / Claude adapter behavior
- implement a CLI command
- implement frontend configuration, control, or audit views
- implement hook, pre-commit, pre-push, CI, or task-stop gates
- modify narrative runtime code
- modify Sprint 049 memory lifecycle implementation
- evaluate product-output quality

Boundary declaration:

- `sprint_049_memory_lifecycle_boundary`: this governance contract must not implement or redesign the suspended Sprint 049 memory lifecycle track.

---

## 4. Audit References

> **中文注释**：这些是本工单必须尊重的上游契约。

Required references:

- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `docs/jikuo/schemas/rule_registry_view_model.schema.md`
- `docs/jikuo/schemas/task_session.schema.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-02_ui_ready_rule_registry_model.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-03_task_session_and_evidence_model.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SCENARIO-CHAIN-01_governance_scenario_chain_and_document_mounting_model.md`

---

## 5. Pre-Audit

> **中文注释**：先把可能的危险点摆出来，避免未来实现时把“便利”误认为“契约”。

Risk observations:

- If state is chat-only, cross-agent continuity depends on memory and prompt compliance.
- If state is frontend-only, Codex / Claude desktop users lose continuity unless they switch tools.
- If state writes are silent, JIKUO becomes another source of invisible process drift.
- If approvals are stored without target/effect, later agents cannot tell what was actually accepted.
- If exact user phrases are treated as fixed commands, the system becomes brittle and unfriendly.
- If sidecar records become canonical over accepted docs, governance can drift away from reviewable source documents.

Design response:

- durable state must be project-local and inspectable
- durable writes must be typed and versioned
- rule-changing writes must be proposal-first
- accepted documents and schemas remain the canonical contract
- sidecar records store runtime/task evidence and decisions, not unreviewed product truth

---

## 6. Canonical Source Hierarchy

> **中文注释**：sidecar 不是新的真相源，而是运行记录和投影缓存的地方。

Canonical hierarchy:

1. Explicit user acceptance records in the active task conversation or accepted work order.
2. Accepted work-order documents and accepted schema documents.
3. `rule_registry.yaml` for rule definitions until a future migration is separately approved.
4. Report-only checker output for computed rule results.
5. Future project-local sidecar records for task sessions, decisions, handoffs, proposals, and audit events.
6. Desktop cards and frontend views as projections only.
7. Chat summaries as non-canonical convenience unless persisted as typed records.

Sidecar records must not override accepted contracts. They can only point to them, snapshot them, or propose updates to them.

---

## 7. Bridge Objects

> **中文注释**：这里定义未来实现时要围绕哪些对象写，而不是让每个工具自己发明存储格式。

### 7.1 `JikuoProjectLocalStateV0`

Purpose:

- describe the project-local governance state for one repository or workspace.

Required fields:

- `schema`: fixed value `jikuo.project_local_state.v0`
- `project_id`
- `project_root`
- `jikuo_state_root`
- `active_scenario_packages`
- `accepted_contract_refs`
- `registry_ref`
- `latest_task_session_refs`
- `latest_rule_proposal_refs`
- `latest_handoff_ref`
- `compatibility`

### 7.2 `JikuoProjectSidecarLayoutV0`

Purpose:

- declare where future sidecar records would live.

Required fields:

- `schema`: fixed value `jikuo.sidecar_layout.v0`
- `state_root`
- `object_roots`
- `naming_rules`
- `retention_rules`
- `write_policy`
- `read_policy`

### 7.3 `JikuoDurableGovernanceRecordV0`

Purpose:

- provide a shared envelope for future durable runtime records.

Required fields:

- `schema`
- `record_id`
- `record_kind`
- `created_at`
- `created_by`
- `source_task_session_id`
- `source_refs`
- `supersedes`
- `superseded_by`
- `status`
- `payload`

---

## 8. Future Sidecar Layout Proposal

> **中文注释**：下面只是未来布局提案，本工单不会创建这些目录。

Future default root:

```text
.jikuo/
```

Future conceptual layout:

```text
.jikuo/
  project_state.yaml
  registry_views/
  task_sessions/
  rule_proposals/
  document_mounts/
  user_decisions/
  handoffs/
  audit_events/
  card_projections/
  cache/
```

Rules:

- `.jikuo/project_state.yaml` would be a lightweight index, not a full database.
- `cache/` would never be canonical.
- `card_projections/` would be reproducible convenience output when possible.
- `task_sessions/`, `user_decisions/`, and `audit_events/` would be append-friendly.
- rule changes would remain proposal-first until accepted into the canonical registry or work-order docs.

No directory or file in this layout is created by this work order.

---

## 9. Durable Object Families

> **中文注释**：这些是未来 sidecar 可能保存的对象类别，不等于现在就要保存。

Future sidecar may persist:

- project state index
- task sessions
- evidence snapshots
- checker result snapshots
- document mount snapshots
- rule-change proposals
- rule-view projections
- user decisions and acceptance records
- handoff summaries
- audit events
- card projection snapshots
- supersession records
- cache records with explicit non-canonical status

Future sidecar must not persist as canonical truth:

- unreviewed chat summaries
- product-output quality judgments
- hidden rule changes
- hidden gate promotions
- narrative runtime state
- Sprint 049 memory lifecycle state

---

## 10. Write Policy

> **中文注释**：写入策略要比数据格式更重要；否则 sidecar 很快会变成新的脏状态源。

Default write posture:

- proposal-first for rule changes, document-mount changes, gate changes, and scenario-package changes
- append-friendly for audit events and user decisions
- no silent overwrite of accepted records
- supersession instead of mutation when meaning changes
- atomic write required for future implementation
- explicit owner/session fields required for active task records
- conflict status required when two agents write incompatible records

Allowed future write classes:

- `draft`: proposed, not accepted
- `active`: current task/session record
- `accepted`: explicitly accepted by user or by accepted contract
- `superseded`: replaced by a later accepted record
- `archived`: retained for audit, not active
- `cache`: reproducible or disposable

---

## 11. Read Policy

> **中文注释**：读状态时要知道哪些能当依据，哪些只是帮助理解。

Future readers must:

- load accepted contracts before sidecar runtime records
- treat sidecar card projections as non-canonical
- treat cache records as disposable
- surface missing or stale sidecar records as `review`, not as silent success
- show source document refs when projecting state to desktop cards
- preserve unknown fields for forward compatibility

Future readers must not:

- assume chat memory is durable state
- infer user acceptance from vague agreement unless a target and effect are recorded
- use stale rule-view projections when the registry has changed
- hide supersession conflicts

---

## 12. Desktop APP Continuity

> **中文注释**：这部分回应你的核心使用习惯：主要在 Codex / Claude 桌面 APP 里连续工作。

Codex and Claude desktop APP continuity should work by:

- reading the same project-local state root
- projecting the same task-session / rule / document-mount records into desktop cards
- preserving exact user decision phrases as evidence, not as required command syntax
- writing future handoff summaries as typed records rather than relying only on chat summaries
- making missing state visible in chat before proceeding

Example user phrase capture:

```yaml
phrase: "<exact user phrase as spoken>"
decision_target: "SPRINT_050_WO-PER-JIKUO-CORE-04"
decision_effect: "accepted_for_downstream_storage_implementation_planning"
```

The phrase stores what the user actually said. It is not a required command format.

---

## 13. Privacy And Minimal Capture

> **中文注释**：机括不应该把聊天原文全量塞进 sidecar；它只应保存治理需要的最小证据。

Future sidecar storage should:

- store exact user phrases only for explicit decisions, approvals, rejections, or scope changes
- avoid raw chat dumps by default
- prefer structured summaries with source refs
- avoid storing secrets or environment dumps
- keep project-local paths relative when possible
- allow future export/import without leaking unrelated project data
- mark sensitive fields if a future schema needs them

---

## 14. Compatibility And Migration

> **中文注释**：先承认版本会演进，未来实现才不会靠硬编码赌运气。

Compatibility rules:

- every durable object has a `schema` value
- readers preserve unknown fields
- writers must not down-convert records silently
- migrations require a proposal record and acceptance when they change meaning
- storage-root migration requires explicit user approval
- cache can be dropped and rebuilt
- accepted docs remain readable without sidecar tooling

---

## 15. Relationship To Existing Contracts

> **中文注释**：CORE-04 是连接器，不替代前面的对象。

Relationship map:

| Upstream contract | CORE-04 relationship |
|---|---|
| `JIKUO-CORE-01` structured result model | checker/result snapshots can be stored as future durable records |
| `JIKUO-CORE-02` registry view model | registry projections may be stored, but `rule_registry.yaml` remains canonical |
| `JIKUO-SCENARIO-CHAIN-01` document mount model | document mount snapshots become a future object family |
| `JIKUO-CORE-03` task session schema | task sessions are the primary future runtime record |
| `JIKUO-AGENT-01` desktop card contract | cards are projections from durable records, not durable truth by themselves |

---

## 16. Testing Governance Declaration

> **中文注释**：这是存储契约，不是存储实现；所以测试重点是流程与边界，而非读写代码。

Required test layers for this slice:

- `unit`: N/A because no parser, writer, reader, serializer, or storage adapter is implemented.
- `integration`: N/A because no sidecar files, CLI, frontend, desktop adapter, checker integration, gate, or runtime integration is implemented.
- `workflow_orchestration`: required by contract review; lifecycle must cover discovery, proposal, user decision, durable record, projection, handoff, and supersession.
- `semantic_regression`: N/A because this slice does not change product behavior or narrative behavior.
- `smoke`: required; run the report-only checker against this new work order and updated index.
- `human_review`: required for canonical-source hierarchy, write policy, privacy/minimal-capture policy, and desktop-continuity fit.
- `human governance review`: required before any `.jikuo/` implementation, storage adapter, renderer, CLI, frontend, or gate work.

---

## 17. Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| C4-DC-01 | Define product question | Section 1 exists |
| C4-DC-02 | Declare scope and out-of-scope boundaries | Sections 2 and 3 exist |
| C4-DC-03 | Include audit references | Section 4 exists |
| C4-DC-04 | Define canonical source hierarchy | Section 6 exists |
| C4-DC-05 | Define bridge objects | Section 7 exists |
| C4-DC-06 | Define future sidecar layout proposal without creating files | Section 8 exists |
| C4-DC-07 | Define durable object families | Section 9 exists |
| C4-DC-08 | Define write and read policies | Sections 10 and 11 exist |
| C4-DC-09 | Address desktop APP continuity | Section 12 exists |
| C4-DC-10 | Address privacy and compatibility | Sections 13 and 14 exist |
| C4-DC-11 | Declare testing-governance layers | Section 16 exists |
| C4-DC-12 | Run report-only checker smoke | Verification log records checker result |

---

## 18. Acceptance Gate

> **中文注释**：这是 CORE-04 的暂停点。验收后，才能规划真正的 sidecar 实现。

This work order is ready for user review when:

- it defines where project-local governance state would live
- it preserves accepted docs and schemas as canonical contracts
- it defines future sidecar object families without creating storage
- it defines write safety, read safety, supersession, and conflict boundaries
- it supports Codex / Claude desktop APP continuity
- it does not require fixed user command phrases
- it does not approve storage, renderer, adapter, CLI, frontend, gate, checker, registry migration, or runtime implementation
- checker smoke has been run

Do not continue to `.jikuo/` implementation, storage adapter implementation, card renderer implementation, Codex/Claude adapter behavior, CLI bridge, frontend views, gate implementation, registry migration, or Sprint 050 runtime hardening until the user accepts this storage contract.

---

## 19. Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md
```

Result:

- registry validation passed
- triggered `R-001`, `R-002`, `R-003`, `R-004`, `R-006`, and `R-012`
- required deterministic work-order fields / sections reported `OK`
- Sprint index document requirement reported `OK`
- remaining declarations and audit bundle fields reported `REVIEW`
- exit code `0`
- report-only posture preserved

---

## 20. User Acceptance Record

> **中文注释**：用户继续推进，表示 CORE-04 可作为 SIDECAR-01 的上游契约；这不是创建 `.jikuo/` 或写 sidecar 的授权。

Decision:

- accepted for downstream `JIKUO-SIDECAR-01` report-only project-state bootstrap planning

Recorded effect:

- project-local state and sidecar storage contract may be used as an upstream implementation boundary
- future implementation planning may reference `JikuoProjectLocalStateV0`, `JikuoProjectSidecarLayoutV0`, and `JikuoDurableGovernanceRecordV0`
- no `.jikuo/` creation, sidecar write, storage adapter, renderer, CLI product surface, frontend, gate, checker migration, registry migration, or runtime implementation is approved by this acceptance
