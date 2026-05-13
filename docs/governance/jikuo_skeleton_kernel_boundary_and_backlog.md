# JIKUO Skeleton / Kernel Boundary And Backlog

> **Date**: 2026-05-09  
> **Status**: Project-local boundary contract / backlog mount  
> **Purpose**: keep current JIKUO work honest about whether it is building the desktop operating skeleton, the configurable rule kernel, packaging surfaces, frontend surfaces, or enforcement gates.  
> **Primary user surface**: Codex / Claude desktop APP chat.  
> **Boundary**: This document does not implement the configurable rule kernel; it makes the boundary and future backlog visible.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 中文摘要

这份文档解决一个“机括自己也会遗忘”的问题：

- 当前我们主要在搭桌面 APP 操作骨架。
- 机括真正要解决的核心问题，是把 AGENTS / 文档 / 用户偏好里的规则变成代码级触发、执行、证据与批准。
- 骨架层必须兼容未来规则内核，但不能假装已经实现规则内核。
- 后续每个 JIKUO 工单都应该声明自己在哪一层、不是哪一层、如何兼容内核层、哪些内核任务仍被挂起。

这不是新的执行引擎，而是后续 JIKUO 任务的层级罗盘。

---

## 2. Layer Taxonomy

### 2.1 `desktop_operating_skeleton`

Purpose:

- define how users invoke JIKUO from Codex / Claude desktop APP chat
- compose no-write proposals
- render cards back into chat
- preserve approval boundaries
- keep CLI as internal helper / fallback

Examples:

- Desktop App Primary Operating Loop
- desktop-agent invocation contract
- `agent_flow.py propose`
- project-local desktop-agent instruction pack

Must not claim:

- user-configurable rule execution is implemented
- custom policy persistence is implemented
- rule actions / evidence are automatically enforced

### 2.2 `configurable_rule_kernel`

Purpose:

- turn user preferences, AGENTS rules, governance docs, sprint docs, and design docs into structured rules
- decide when rules trigger
- produce required actions and evidence obligations
- report missing evidence
- support report-only / warning / blocking / approval-gate phases

Examples:

- configurable trigger policy
- rule action and evidence model
- policy store and user configuration flow
- policy-aware `agent_flow.py`

### 2.3 `packaging_surface`

Purpose:

- package stable skeleton/kernel semantics into installable surfaces
- reduce setup friction without changing semantics

Examples:

- Codex Skill
- MCP tool wrapper
- Codex Plugin

Must not:

- redefine approval boundaries
- hide no-write / write-mode differences
- fork rule semantics from the kernel

### 2.4 `frontend_surface`

Purpose:

- provide visual configuration, control, and audit surfaces
- make rule editing and process review easier for ordinary users

Examples:

- rule configuration console
- run-control console
- evolution/audit dashboard

### 2.5 `gate_enforcement`

Purpose:

- promote mature report-only obligations into blocking hooks, CI, or task-stop gates only after false-positive and rollback risks are understood

Must not:

- turn report-only rules into blockers without explicit accepted work order
- block human work without clear override and recovery path

---

## 3. Required JIKUO Work Order Fields

Every future JIKUO work order should declare these fields in the header metadata:

```markdown
> **JIKUO layer**: desktop_operating_skeleton | configurable_rule_kernel | packaging_surface | frontend_surface | gate_enforcement
> **Current slice is not**: ...
> **Kernel compatibility**: ...
> **Deferred kernel backlog refs**: ...
```

The field values should be short, explicit, and reviewable.

Recommended interpretation:

- `JIKUO layer` says what layer the task actually changes.
- `Current slice is not` says which nearby layers must not be silently absorbed.
- `Kernel compatibility` says what shape must remain open for the future rule kernel.
- `Deferred kernel backlog refs` says which future kernel tasks remain unresolved.

---

## 4. Skeleton Compatibility Rules

When a task belongs to `desktop_operating_skeleton`, it should preserve these compatibility points:

- trigger / event names should remain explicit enough for future policy-trigger matching
- proposal output should be able to carry future `policy_refs`, `triggered_rules`, `required_actions`, and `missing_evidence`
- approval boundaries should distinguish process-action approval from future rule-change approval
- card output should be able to show which rules triggered and which evidence is missing
- no-write preview should remain separate from guarded writes
- ordinary users should stay in Codex / Claude desktop APP chat for routine flows

The skeleton may expose future hook points, but it must not implement or fake the rule kernel.

---

## 5. Kernel Backlog

The configurable rule kernel remains pending. Current backlog:

| Backlog ID | Purpose | Depends on | Product meaning |
|---|---|---|---|
| `JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy` | Define how user rules become structured trigger / condition / action / evidence policies | skeleton event model | Turns AGENTS-style probabilistic instructions into explicit policy candidates; contract implemented and ready for user review |
| `JIKUO-CORE-06_rule_action_and_evidence_model` | Define required actions, evidence objects, missing-evidence reports, and enforcement phases | CORE-05 | Makes "rule was triggered and executed" inspectable; contract implemented and ready for user review |
| `JIKUO-CORE-07_policy_store_and_user_configuration_flow` | Define where approved user policies live and how users approve / revise them | CORE-05, CORE-06 | Lets ordinary users configure project rules without editing raw YAML first; contract implemented and ready for user review |
| `JIKUO-AGENT-07_policy_aware_agent_flow_proposal` | Extend future `agent_flow.py propose` output to include triggered policy refs and required actions | CORE-05, CORE-06, CORE-07 | Makes desktop proposal cards show why JIKUO is asking for work; projection contract implemented and ready for user review |
| `JIKUO-AGENT-08_policy_aware_agent_flow_fallback` | Implement policy-unavailable fallback fields in `agent_flow.py propose` without evaluating policies | AGENT-07, CORE-05, CORE-06, CORE-07 | Makes missing policy infrastructure visible in the desktop proposal card; full store/evaluator/checker implementation still deferred |
| `JIKUO-CORE-08_read_only_policy_store_inspection` | Inspect project-local policy store status and approved refs without writing or evaluating policies | CORE-07, AGENT-07, AGENT-08 | Lets desktop proposals see whether policy configuration is missing, initialized, stale, conflict, or active; trigger evaluator and evidence checker still deferred |
| `JIKUO-CORE-09_policy_trigger_evaluator_mvp` | Evaluate exact lifecycle-event policy triggers and project required actions without writing or checking evidence | CORE-05, CORE-06, CORE-07, CORE-08, AGENT-08 | Lets desktop proposals show which approved policies triggered for this lifecycle event; condition evaluator, evidence checker, action executor, and gates still deferred |
| `JIKUO-CORE-10_policy_evidence_checker_mvp` | Match required evidence against inline produced evidence without writing or gating | CORE-06, CORE-09 | Lets desktop proposals show whether required evidence is missing or satisfied by runner-produced evidence; evidence persistence and gates still deferred |
| `JIKUO-CORE-11_policy_evidence_persistence_proposal_bridge` | Convert explicit policy evidence refs into guarded task-session evidence append command proposals without writing | CORE-10, TASKSESSION-04 | Lets users persist reviewed policy evidence through an approval boundary instead of manually composing update commands |
| `JIKUO-CORE-12_policy_evidence_ingestion_mvp` | Read explicit task-session `policy_evidence:*` snapshots into report-only evidence matching without writing | CORE-10, CORE-11, TASKSESSION-04 | Lets later policy checks reuse approved compact evidence from task sessions instead of relying on chat memory |
| `JIKUO-CORE-13_policy_condition_evaluator_mvp` | Evaluate explicit task metadata and path conditions before projecting required actions | CORE-05, CORE-09, CORE-10, CORE-12 | Makes project rules precise enough to avoid firing on unrelated tasks while staying report-only |
| `JIKUO-CORE-14_policy_write_plan_proposal_mvp` | Render policy-store write targets, proposed policy, preflight, and non-effects before durable policy writing exists | CORE-07, CORE-08, CORE-13 | Lets ordinary desktop APP users review how a rule would enter project policy storage before approving any writer |
| `JIKUO-CORE-15_guarded_policy_store_write_mvp` | Create the first approved report-only policy and manifest after explicit confirmation and approval | CORE-07, CORE-08, CORE-14 | Moves a reviewed rule from chat/proposal into project-local policy storage without making proposal mode write files |
| `JIKUO-CORE-16_active_policy_store_append_mvp` | Append a second approved report-only policy to an active store after explicit confirmation and approval | CORE-15 | Lets a project accumulate multiple approved rules while keeping append distinct from revision, supersession, and rollback |
| `JIKUO-CORE-17_policy_decision_record_mvp` | Persist one compact decision record for each successful guarded policy create / append write | CORE-15, CORE-16 | Lets future audit surfaces trace an active policy back to an explicit approved write effect without mining chat history |
| `JIKUO-CHECKER-02_policy_execution_evidence_checker` | Ingest broader checker/task-session evidence and verify triggered policies across task lifecycle | CORE-06, CORE-10, CORE-11, CORE-12, CORE-13, CORE-14, CORE-15, CORE-16, CORE-17 | Moves rule execution from memory/probability toward code-visible evidence across more sources |

These backlog items are not approved for implementation by this document.

---

## 6. Checker Hook

`R-013` in `rule_registry.yaml` should report future JIKUO work orders that do not declare:

- `JIKUO layer`
- `Current slice is not`
- `Kernel compatibility`
- `Deferred kernel backlog refs`
- `JIKUO Layer Boundary`
- `Kernel Compatibility`
- `Deferred Kernel Backlog`

This is report-only. It is a reminder and evidence surface, not a blocking gate.

---

## 7. Agent Flow Projection Hook

Future `agent_flow.py propose` work may project the layer boundary into proposal cards:

```text
Current JIKUO layer: desktop_operating_skeleton
Not implementing now: configurable_rule_kernel
Kernel compatibility required: yes
Deferred kernel backlog: CORE-05 / CORE-06 / CORE-07
```

This is not implemented in the current skeleton.

---

## 8. Acceptance Rule

Future JIKUO work should not be considered complete if it silently changes layers.

If a task starts as skeleton work but begins implementing configurable rule behavior, it should pause and create or update the relevant kernel work order.

If a packaging surface needs to change runner semantics, it should pause and update the skeleton / kernel contract first.
