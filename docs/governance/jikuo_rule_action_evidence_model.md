# JIKUO Rule Action And Evidence Model

> **Date**: 2026-05-11
> **Status**: Draft kernel model contract / no runtime implementation
> **Purpose**: define required action, evidence, evidence-satisfaction, and missing-evidence report objects for configurable JIKUO policies.
> **Primary user surface**: Codex / Claude desktop APP chat.
> **JIKUO layer**: configurable_rule_kernel
> **Depends on**: `jikuo_configurable_rule_trigger_policy.md`
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 中文摘要

CORE-05 回答“规则什么时候触发”。CORE-06 回答“触发以后，必须做什么，以及如何证明做过”。

这份文档把规则触发后的执行链拆成四类对象：

- `policy_action`: 被触发后需要执行的动作。
- `evidence_requirement`: 这个动作需要什么证据才算被处理过。
- `policy_evidence`: 实际产生的证据。
- `missing_evidence_report`: 证据缺失时给 Agent / 用户 / future checker / UI 的报告。

它不实现自动执行，不写 sidecar，不改 `agent_flow.py`，不做 gate。它只定义未来执行器、desktop card、checker、MCP、frontend 可以共同使用的动作与证据契约。

---

## 2. Product Meaning

JIKUO's original promise is not merely "rules are listed".

The useful product promise is:

- a rule can trigger
- the triggered rule produces concrete obligations
- each obligation has expected evidence
- missing evidence is visible before delivery or handoff
- users can approve, reject, exempt, or revise based on a clear record

This model makes "the agent should have done X" inspectable.

For ordinary users, the future experience should feel like:

- "This rule triggered because this task matches these conditions."
- "The agent needs to do these actions."
- "These actions have evidence."
- "These actions are still missing evidence."
- "This write/action needs your approval before it happens."

---

## 3. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This contract is allowed to define:

- required action object shape
- evidence requirement object shape
- policy evidence object shape
- missing evidence report shape
- action status and evidence status vocabulary
- satisfaction matching rules
- compact retention and privacy boundaries
- desktop / checker / frontend / MCP projection requirements

This contract is not allowed to:

- execute policy actions
- persist action or evidence records
- implement policy-aware `agent_flow.py`
- implement a policy evidence checker
- implement UI / Skill / MCP / Plugin / gate behavior
- edit `.codex/AGENTS.md`
- promote any report-only policy into blocking enforcement
- evaluate product-output quality

---

## 4. Kernel Compatibility

This model extends CORE-05 without changing its policy trigger semantics.

Compatibility requirements:

- every action should be traceable to `policy_id`, `trigger_id`, and optional `condition_id`
- every evidence item should be traceable to the action or requirement it satisfies
- action execution status must stay separate from evidence status
- write actions must expose write effect, non-effect, and approval boundary
- manual evidence must be allowed, but it should remain `review_required` unless later tooling can validate it
- missing evidence reports must remain usable in desktop chat before a frontend exists

---

## 5. Deferred Kernel Backlog

This contract supports later tasks but does not implement them:

- `JIKUO-CORE-07_policy_store_and_user_configuration_flow`
- `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`
- installable Codex Skill
- MCP tool wrapper
- Codex Plugin
- frontend configuration / audit surfaces
- gate enforcement adapter

---

## 6. Action Model: `jikuo.policy_action.v0`

Minimal shape:

```yaml
schema_version: "jikuo.policy_action.v0"
action_id: "ACT-..."
policy_ref: "POLICY-..."
trigger_ref: "TRG-..."
requirement_refs:
  - "EVDREQ-..."
type: "read_reference"
phase: "task_start | mid_task | pre_delivery | completion | handoff"
actor: "agent | user | tool | reviewer"
target:
  kind: "document | command | task_session | work_order | approval | card | handoff"
  ref: "docs/..."
inputs:
  document_refs: []
  command_refs: []
  policy_refs: []
execution:
  mode: "manual | agent_assisted | tool_backed | future_automatic"
  status: "not_started | proposed | in_progress | completed | skipped | refused | failed | not_applicable"
write_boundary:
  write_effect: "none"
  non_effect: "does not modify project files or sidecar state"
  approval_required: false
projection:
  desktop_card: true
  checker: true
  frontend: true
```

Rules:

- `action_id` must be stable within one policy execution instance.
- `type` must come from the accepted action vocabulary or an explicitly versioned extension.
- `target` must be concrete enough for the user to understand what will be done.
- `write_boundary` is required even when the write effect is `none`.
- a failed or skipped action may still produce evidence, but it does not satisfy completion unless the requirement allows that status.

---

## 7. First Action Type Catalog

| Action Type | Meaning | Typical Evidence | Write Boundary |
|---|---|---|---|
| `read_reference` | inspect a required mounted reference | `reference_read` | no write |
| `render_pre_task_review` | present task-start governance card | `card_rendered` | no write |
| `render_mid_task_review` | present mid-task governance card | `card_rendered` | no write |
| `render_pre_delivery_review` | present pre-delivery governance card | `card_rendered` | no write |
| `run_report_only_checker` | run a report-only checker or equivalent tool-backed inspection | `checker_result` | no write |
| `run_declared_test` | run a declared verification command | `test_result` | may write test artifacts; must declare |
| `record_evidence_snapshot` | persist compact evidence to an approved record | `task_session_evidence_appended` | guarded write |
| `record_verification_snapshot` | persist compact verification result to an approved record | `task_session_verification_appended` | guarded write |
| `ask_user_for_approval` | request approval for a specific target/effect | `approval_recorded` | no write by itself |
| `propose_policy_candidate` | render a candidate policy for review | `policy_candidate_rendered` | no write unless separately approved |
| `propose_document_mount` | render a required reference mount candidate | `document_mount_proposed` | no write unless separately approved |
| `update_declared_document` | update an accepted document target | `document_updated` | guarded or explicit file write |
| `prepare_handoff_summary` | prepare continuity summary for next agent/session | `handoff_recorded` | guarded write if persisted |

Catalog rules:

- new action types should be added by contract update, not ad hoc in implementation code
- actions that may write must declare approval and non-effect before execution
- action types should be process actions, not product-output quality judgments

---

## 8. Evidence Requirement Model: `jikuo.evidence_requirement.v0`

Minimal shape:

```yaml
schema_version: "jikuo.evidence_requirement.v0"
requirement_id: "EVDREQ-..."
policy_ref: "POLICY-..."
action_ref: "ACT-..."
required_type: "checker_result"
required_status:
  - "ok"
  - "review_required"
satisfaction:
  match_policy: true
  match_action: true
  match_target: true
  same_task_session: true
  allow_manual: true
  manual_status: "review_required"
retention:
  compact_summary_required: true
  raw_transcript_allowed: false
projection:
  desktop_card: true
  checker: true
  frontend: true
```

Rules:

- requirements define what evidence is needed; they are not the evidence itself
- requirements may allow manual evidence, but manual evidence should not silently become tool-verified evidence
- raw chat transcripts should not be required as evidence
- requirements should be scoped to task/session where possible

---

## 9. Evidence Model: `jikuo.policy_evidence.v0`

Minimal shape:

```yaml
schema_version: "jikuo.policy_evidence.v0"
evidence_id: "EVD-..."
evidence_type: "checker_result"
policy_ref: "POLICY-..."
action_ref: "ACT-..."
requirement_ref: "EVDREQ-..."
task_session_ref: null
source:
  kind: "tool_output | file_ref | user_approval | agent_summary | manual_note"
  ref: "..."
producer:
  actor: "agent | user | tool | reviewer"
  tool: "tools/audit/check_rule_registry.py"
status: "ok | missing | review_required | not_applicable | failed | error"
summary: "compact process evidence"
artifact_refs:
  - "docs/..."
approval:
  required: false
  phrase: null
privacy:
  raw_transcript_included: false
created_at: "ISO-8601"
```

Rules:

- evidence should be compact and process-oriented
- evidence should not store raw chat unless an explicit future privacy contract permits it
- evidence must identify which requirement it satisfies or why no requirement exists
- exact approval phrases should be recorded as `"<exact user phrase as spoken>"` when present
- evidence can be produced by tools, agents, users, or reviewers, but the producer must be explicit

---

## 10. Evidence Status Vocabulary

| Status | Meaning | Can Satisfy Requirement By Default |
|---|---|---|
| `ok` | requirement is satisfied by accepted evidence | yes |
| `review_required` | evidence exists but needs human review or cannot be tool-verified | only if requirement allows |
| `missing` | required evidence is absent | no |
| `not_applicable` | requirement does not apply and reason is recorded | only if requirement allows |
| `failed` | action ran but failed | no |
| `error` | evidence could not be evaluated | no |

Status rules:

- `review_required` is not failure; it is an explicit handoff to human judgment
- `not_applicable` must include a reason
- tool-verified evidence and manual evidence should stay distinguishable

---

## 11. Satisfaction Matching Rules

An evidence item satisfies a requirement only when:

- `policy_ref` matches
- `action_ref` matches, unless the requirement explicitly allows policy-level evidence
- `requirement_ref` matches or can be deterministically mapped
- target matches when the requirement declares target matching
- task/session scope matches when the requirement declares session matching
- evidence status is allowed by the requirement
- evidence was produced after the relevant trigger, unless the requirement allows pre-existing evidence

If any required match is ambiguous, the result should be:

- `review_required` when evidence exists but cannot be verified
- `missing` when no relevant evidence exists
- `error` when evaluation fails

---

## 12. Missing Evidence Report: `jikuo.missing_evidence_report.v0`

Minimal shape:

```yaml
schema_version: "jikuo.missing_evidence_report.v0"
report_id: "MER-..."
policy_ref: "POLICY-..."
trigger_ref: "TRG-..."
task_session_ref: null
missing:
  - requirement_ref: "EVDREQ-..."
    action_ref: "ACT-..."
    required_type: "checker_result"
    current_status: "missing"
    reason: "No matching checker_result evidence found for this action."
severity:
  policy_level: "warning | review_required | blocking"
  enforcement_phase: "report_only | local_gate_candidate | approval_gate_candidate | ci_candidate"
next_actions:
  - "run_report_only_checker"
  - "record_evidence_snapshot"
projection:
  desktop_card: true
  checker: true
  frontend: true
```

Rules:

- missing evidence reports do not block by themselves in report-only phase
- report severity and enforcement phase must stay separate
- a report should suggest the next safest action
- gate behavior requires a later explicit gate work order

---

## 13. Desktop Card Projection Requirements

Future cards should show:

- triggered policy title and id
- action list with status
- evidence requirements for each action
- evidence status for each requirement
- missing evidence and next suggested action
- approval requirement for write actions
- write effect and non-effect

Cards should avoid:

- raw chat dumps
- hidden tool actions
- vague approvals that could apply to multiple writes
- product-output quality judgments inside engineering governance cards

---

## 14. Storage And Retention Boundary

This model does not decide where evidence is stored.

Future `JIKUO-CORE-07` / task-session integration should decide:

- which evidence can live in sidecar task sessions
- which evidence remains transient card output
- which evidence references committed files or test outputs
- how long evidence records remain
- how superseded evidence is marked
- how privacy-sensitive details are redacted

Default retention posture:

- compact process summaries
- artifact references where possible
- no raw transcripts by default
- explicit approval for durable writes

---

## 15. Non-Goals

This contract does not implement:

- action execution
- evidence persistence
- automatic checker evaluation
- policy-aware `agent_flow.py`
- frontend forms
- Skill / MCP / Plugin packaging
- gate enforcement
- narrative-engine runtime behavior
- product-output quality review

---

## 16. Acceptance Rule

This model is acceptable if it makes the following inspectable:

- what action a triggered policy requires
- what evidence is expected
- what evidence was produced
- whether produced evidence satisfies the requirement
- what evidence is missing
- which next action is safest
- which writes require explicit approval

