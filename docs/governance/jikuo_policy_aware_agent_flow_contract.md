# JIKUO Policy-Aware Agent Flow Contract

> **Date**: 2026-05-11
> **Status**: Desktop-operating-skeleton contract; fallback runner projection implemented in `JIKUO-AGENT-08`; read-only policy-store status projection implemented in `JIKUO-CORE-08`; exact lifecycle trigger evaluation implemented in `JIKUO-CORE-09`; report-only evidence matching implemented in `JIKUO-CORE-10`; guarded evidence persistence proposal bridge implemented in `JIKUO-CORE-11`; explicit task-session evidence ingestion implemented in `JIKUO-CORE-12`; explicit-input condition evaluation implemented in `JIKUO-CORE-13`; proposal-only policy write-plan projection implemented in `JIKUO-CORE-14`; guarded initial policy-store write implemented in `JIKUO-CORE-15`; guarded active-store append implemented in `JIKUO-CORE-16`; guarded policy decision records implemented in `JIKUO-CORE-17`
> **Purpose**: define how future `agent_flow.py propose` should project triggered policies, required actions, evidence status, and policy-store state into Codex / Claude desktop APP chat.
> **Primary user surface**: Codex / Claude desktop APP chat.
> **JIKUO layer**: desktop_operating_skeleton
> **Consumes kernel contracts**: `jikuo_configurable_rule_trigger_policy.md`; `jikuo_rule_action_evidence_model.md`; `jikuo_policy_store_configuration_flow.md`
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 中文摘要

CORE-05/06/07 定义了 policy 内核三件事：

- 规则如何触发。
- 触发后需要哪些 action/evidence。
- 用户批准后的 policy 将来如何存储和配置。

AGENT-07 回到桌面 APP 主流程，回答：未来 Agent 调用 `agent_flow.py propose` 时，应该怎样把这些 policy 信息投影成用户能看的聊天卡片。

本合同本身不创建 task session，`agent_flow.py propose` 不做 durable write。`JIKUO-AGENT-08` 已实现最小 fallback projection；`JIKUO-CORE-08` 已实现只读 policy store status projection；`JIKUO-CORE-09` 已实现 exact lifecycle trigger evaluation；`JIKUO-CORE-10` 已实现 report-only evidence matching；`JIKUO-CORE-11` 已实现 guarded evidence persistence proposal；`JIKUO-CORE-12` 已实现显式 task-session evidence ingestion；`JIKUO-CORE-13` 已实现显式输入 condition evaluation；`JIKUO-CORE-14` 已实现 proposal-only policy write-plan projection；`JIKUO-CORE-15` 已实现 guarded initial policy-store write；`JIKUO-CORE-16` 已实现 guarded active-store append；`JIKUO-CORE-17` 已实现 guarded policy decision record。但 `agent_flow.py propose` 仍不做 durable write、automatic evidence write、action execution、revision/supersession、broad evidence ingestion 或 gate。

---

## 2. Product Meaning

JIKUO must not stop at "rules exist somewhere".

When a user asks the desktop agent to start or review a task, the agent should eventually show:

- which policies were considered
- which policies triggered
- why they triggered
- which actions are required
- which evidence exists
- which evidence is missing
- whether policy store is unavailable, missing, stale, or active
- what the safest next action is

This contract makes policy awareness visible in the same Codex / Claude desktop APP chat instead of forcing the user to inspect CLI output or raw YAML.

---

## 3. JIKUO Layer Boundary

Current layer:

- `desktop_operating_skeleton`

This contract is allowed to define:

- policy-aware proposal envelope
- policy-store status projection
- triggered policy projection
- required action projection
- evidence and missing-evidence projection
- policy write-plan card projection
- refusal and fallback behavior when no policy store exists
- trace fields for loop step ids, atom ids, policy ids, action ids, and evidence ids
- downstream `agent_flow.py` implementation requirements

This contract is not allowed to:

- change CORE-05 / CORE-06 / CORE-07 kernel semantics
- implement durable policy-store writes from `agent_flow.py propose`
- automatically persist policy evidence
- ingest persisted policy evidence from implicit or broad sources
- implement advanced condition evaluation beyond explicit task metadata and path conditions
- execute required actions
- modify `src/jikuo/agent_flow.py` beyond read-only status projection, report-only exact lifecycle trigger evaluation, report-only evidence matching, explicit condition evaluation, evidence persistence proposal, explicit evidence ingestion, and proposal-only write-plan cards
- create `.jikuo/policies/`
- create `.jikuo/task_sessions/`
- execute durable writes
- install Skill / MCP / Plugin / frontend / gate behavior
- evaluate product-output quality

---

## 4. Kernel Compatibility

This contract must consume the kernel objects without redefining them:

- `jikuo.configurable_rule_policy.v0`
- `jikuo.policy_action.v0`
- `jikuo.evidence_requirement.v0`
- `jikuo.policy_evidence.v0`
- `jikuo.missing_evidence_report.v0`
- `jikuo.policy_store_manifest.v0`
- `jikuo.policy_proposal.v0`

Compatibility rules:

- policy-aware proposals should reference policy ids rather than copying full policy bodies by default
- proposal cards may include compact snapshots for review, but snapshots are not the policy source of truth
- missing policy store should be reported as `policy_store_status: missing`, not silently treated as no obligations
- no policy should be considered active solely because it was proposed in chat
- no durable write should happen in `propose`

---

## 5. Deferred Implementation Backlog

This document supports later tasks but does not implement the full kernel path:

- full policy-aware `agent_flow.py propose` implementation with automatic evidence persistence, action execution, and advanced condition evaluation
- durable policy store revision / supersession adapter
- broader policy condition evaluator
- broad policy evidence ingestion beyond explicit task-session `policy_evidence:*` snapshots
- policy proposal / missing-evidence card renderer
- MCP wrapper exposing policy-aware proposal
- Skill / Plugin / frontend packaging
- gate enforcement adapter

---

## 6. Policy-Aware Proposal Envelope

Future `agent_flow.py propose` output should extend `jikuo.agent_flow_proposal.v0` with policy sections.

Minimal shape:

```yaml
schema: "jikuo.agent_flow_proposal.v1"
proposal_id: "proposal_..."
event: "task_start"
loop_trace: []
atom_trace: []
policy_context:
  policy_store_status: "unavailable | missing | initialized | stale | conflict | active"
  active_policy_refs: []
  policy_snapshot_ref: null
  policy_eval_status: "not_evaluated | evaluated | partial | refused | error"
  policy_evidence_check_status: "not_evaluated | checked | refused | error"
triggered_policies: []
required_actions: []
evidence_status: []
missing_evidence_reports: []
cards: []
write_effect:
  effect: "no durable write is performed by agent_flow.py propose"
  non_effects:
    - "does not create .jikuo/policies/"
    - "does not create .jikuo/task_sessions/"
    - "does not update .jikuo/project_state.yaml"
```

Rules:

- `proposal_id` remains stable for the proposal render only.
- `policy_context` must be present even when no policy store exists.
- policy-aware sections may be empty, but absence must be explained by status fields.
- `write_effect` must keep proposal mode explicitly no-write.

---

## 7. Policy Store Status Projection

Future runner should report one of these statuses:

| Status | Meaning | User-Facing Meaning |
|---|---|---|
| `unavailable` | policy store feature is disabled or cannot be inspected | JIKUO can show baseline governance, but project policies are not available yet |
| `missing` | feature exists but no store is initialized | user may initialize policy store in a later guarded flow |
| `initialized` | store exists but no active policies matched | no active project policy triggered |
| `stale` | manifest or refs are stale | review needed before trusting policy results |
| `conflict` | duplicate or conflicting policy refs | policy evaluation refused |
| `active` | store exists and active policies were evaluated | policy-aware projection is available |

Current runner status:

- read-only store status may be `missing`, `initialized`, `stale`, `conflict`, or `active`
- exact lifecycle trigger evaluation may return `evaluated`, `not_evaluated`, or `refused`
- explicit-input condition evaluation may return `checked` or `not_evaluated`
- report-only evidence matching may return `checked`, `not_evaluated`, or `refused`
- explicit task-session evidence ingestion may supply `policy_evidence:*` snapshots to report-only matching when a session id is provided
- proposal-only policy write planning may return `jikuo.policy_write_plan.v0` cards without creating `.jikuo/policies/`
- guarded policy-store writing, active-store append, and policy decision records exist in `policy_store.py write-policy`, but remain outside `agent_flow.py propose`

This avoids pretending policy execution or automatic desktop apply exists before automatic evidence persistence, active-store evolution, action executor, or gate implementation.

---

## 8. Triggered Policy Projection

Triggered policy projection item:

```yaml
policy_ref: "POLICY-..."
policy_title: "..."
version: 1
source: "project_approved_policy | scenario_package_default | kernel_default"
trigger_ref: "TRG-..."
trigger_reason: "task_lifecycle_event matched task_start"
status: "triggered | not_triggered | review_required | refused | error"
confidence: "tool_verified | inferred | manual_review_required"
```

Rules:

- `trigger_reason` must be compact and user-readable.
- `confidence` should distinguish tool-backed evaluation from agent inference.
- pending proposals must not appear as triggered active policies.

---

## 9. Required Action Projection

Required action projection item:

```yaml
action_ref: "ACT-..."
policy_ref: "POLICY-..."
action_type: "read_reference"
phase: "task_start"
target:
  kind: "document"
  ref: "docs/..."
status: "not_started | proposed | in_progress | completed | skipped | refused | failed | not_applicable"
write_boundary:
  write_effect: "none"
  approval_required: false
next_action: "read_reference"
```

Rules:

- actions should reference CORE-06 action types.
- write actions must show approval requirement before a user can approve anything.
- desktop cards should group actions by policy and lifecycle phase.

---

## 10. Evidence Projection

Evidence projection item:

```yaml
requirement_ref: "EVDREQ-..."
action_ref: "ACT-..."
policy_ref: "POLICY-..."
required_type: "checker_result"
current_status: "ok | review_required | missing | not_applicable | failed | error"
evidence_refs: []
summary: "No matching checker result found."
```

Rules:

- evidence status must use CORE-06 vocabulary.
- `review_required` should be shown as a user review need, not a silent failure.
- `missing` should include the next safest action.

---

## 11. Missing Evidence Card Requirements

Future desktop cards should show:

- policy title and id
- missing evidence type
- related action
- why it is missing
- recommended next action
- whether the next action is no-write or guarded-write
- whether user approval is needed

Card requirements:

- keep routine review in desktop APP chat
- avoid raw chat dumps
- avoid vague approval prompts
- keep report-only findings distinct from blocking gates

---

## 12. Fallback Behavior

When policy store is missing or evaluator / checker coverage is unavailable:

- proposal should still run baseline no-write atoms
- output should say policy-aware evaluation is not evaluated
- output should not claim no policies triggered
- output should suggest the next implementation/configuration step

Example fallback summary:

```text
Policy-aware evaluation: not_evaluated.
Reason: policy store is missing, no policy matched this lifecycle event, or no matching produced evidence exists.
Baseline JIKUO proposal still ran no-write project/task atoms.
```

---

## 13. Trace Requirements

Future trace should include:

- loop step ids
- atom ids
- policy ids
- trigger ids
- action ids
- evidence requirement ids
- missing evidence report ids
- policy store status
- evaluation status

Trace rule:

- trace ids are for audit and debugging; desktop cards may show compact summaries only.

---

## 14. Downstream Implementation Requirements

Before implementing full policy evaluation in `agent_flow.py`, a future implementation work order should define:

- exact input flags for policy-aware mode
- how policy store root is discovered
- how missing or stale policy store is reported
- whether checker output is composed in `agent_flow.py` or delegated
- JSON compatibility with existing `jikuo.agent_flow_proposal.v0`
- tests proving `propose` remains no-write
- tests proving missing policy store does not claim success

---

## 15. Non-Goals

This contract and the current proposal runner do not implement:

- advanced condition evaluation
- automatic evidence persistence
- broader condition evaluation beyond explicit task metadata and path conditions
- broad evidence ingestion beyond explicit task-session `policy_evidence:*` snapshots
- full policy-aware `agent_flow.py` action/evidence evaluation
- durable policy store writes from proposal mode
- policy revision, supersession, or rollback
- card renderer code
- MCP / Skill / Plugin / frontend integration
- gate enforcement
- runtime narrative-engine behavior

---

## 16. Acceptance Rule

This contract is acceptable if it makes clear:

- how future `agent_flow.py propose` will expose policy awareness
- how unavailable policy infrastructure is shown honestly
- how triggered policies, actions, evidence, and missing evidence appear in desktop chat
- how no-write proposal mode remains safe
- which later implementation tasks remain required
