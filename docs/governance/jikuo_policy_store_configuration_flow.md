# JIKUO Policy Store And User Configuration Flow

> **Date**: 2026-05-11
> **Status**: Draft kernel storage/configuration contract / read-only status adapter implemented in `JIKUO-CORE-08`; exact lifecycle trigger evaluator implemented in `JIKUO-CORE-09`; report-only evidence matching implemented in `JIKUO-CORE-10`; policy condition evaluator implemented in `JIKUO-CORE-13`; proposal-only policy write plan implemented in `JIKUO-CORE-14`; guarded initial policy-store write implemented in `JIKUO-CORE-15`; guarded active-store append implemented in `JIKUO-CORE-16`; guarded policy decision records implemented in `JIKUO-CORE-17`; first real governance-policy fixtures implemented in `JIKUO-CORE-18` / `JIKUO-CORE-19`; guarded policy deprecation implemented in `JIKUO-LIVE-06`; guarded policy supersession implemented in `JIKUO-LIVE-07`
> **Purpose**: define where approved configurable policies should live in the future, how users approve or revise them, and how policy lifecycle remains auditable without relying on raw chat memory.
> **Primary user surface**: Codex / Claude desktop APP chat.
> **JIKUO layer**: configurable_rule_kernel
> **Depends on**: `jikuo_configurable_rule_trigger_policy.md`; `jikuo_rule_action_evidence_model.md`; CORE-04 project-local state and sidecar storage contract
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 中文摘要

CORE-05 定义 policy 触发语义。CORE-06 定义 action/evidence 语义。CORE-07 定义 policy 被用户批准后，未来应该如何存储、配置、修订、废弃和回滚。

这份文档定义 policy store 契约；`JIKUO-CORE-08` 已实现只读 status adapter；`JIKUO-CORE-09` 已实现 exact lifecycle trigger evaluator；`JIKUO-CORE-10` 已实现 report-only evidence matching；`JIKUO-CORE-15` / `JIKUO-CORE-16` 已实现受控 initial write 与 active-store append；`JIKUO-CORE-17` 已实现受控 policy decision record。但 proposal-only 路径仍不创建 `.jikuo/policies/`，不自动写 policy，不持久化 evidence，不实现 UI / CLI / MCP / Skill / Plugin / gate。

它解决的问题是：

- 用户可以用自然语言表达规则偏好。
- Agent 可以把偏好提炼成 policy proposal。
- 用户可以在 Codex / Claude 桌面 APP 聊天里批准、修改、拒绝或延后。
- 只有明确批准后的 policy 才能进入 future approved policy store。
- pending proposal、active policy、deprecated policy、superseded policy 必须分层。
- 后续 Agent 不应靠记忆执行规则，而应读取已批准 policy。

---

## 2. Product Meaning

JIKUO is useful only if ordinary users can configure durable process rules without becoming YAML maintainers.

The product should support this flow:

- user states a working-method preference
- agent proposes a structured policy candidate
- user reviews the candidate in the same desktop APP chat
- user approves, revises, rejects, or defers
- a future guarded writer persists the approved policy
- later agents and tools read the approved policy instead of relying on conversation memory

This contract defines the future policy store and configuration flow so that later implementation does not invent storage semantics ad hoc.

### Policy Management Expectations

Policy management is the product capability that lets a user or developer turn a real working-method insight into a durable, inspectable process rule.

The policy system should support:

- policy origins from user preference, incident review, governance correction, product design, or self-dogfooding
- explicit separation between candidate policy, approved policy, policy decision, and execution evidence
- scenario mounting through trigger, scope, condition, required action, and required evidence fields
- report-only evaluation before any blocking gate is introduced
- visible missing evidence instead of hidden agent judgement
- policy evolution through revision, supersession, deprecation, rollback, or scope narrowing
- tests that prove a policy is loaded, triggered, and evidence-checked in a real evaluator path

CORE-18 and CORE-19 are concrete examples of this capability. Their rule contents are not universal policy-management mechanics; they are project-approved governance policies derived from real JIKUO self-development corrections. In particular, CORE-19 is a pre-code-change governance classification principle carried by report-only policy evidence, not a standalone implementation feature.

---

## 3. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This contract is allowed to define:

- policy store source hierarchy
- proposed future `.jikuo/policies/` layout
- policy proposal object
- approved policy record object
- policy decision record object
- policy write plan / write result contracts
- revision, deprecation, supersession, and rollback rules
- desktop APP configuration flow
- future UI / MCP / Skill / Plugin projection requirements

This contract and the current adapters are not allowed to:

- create `.jikuo/policies/` from read-only or proposal-only paths
- update `.jikuo/project_state.yaml`
- write approved policies without `--confirm-write-policy` and `--approval-phrase`
- revise or roll back policies
- deprecate or supersede policies from read-only / proposal-only paths
- append a policy from `agent_flow.py propose` or any other proposal-only path
- execute required policy actions
- persist required evidence satisfaction
- implement broader condition inference beyond explicit supplied metadata / paths
- implement UI / Skill / MCP / Plugin / gate behavior
- edit `.codex/AGENTS.md`
- promote any policy into blocking enforcement
- evaluate product-output quality

---

## 4. Kernel Compatibility

This contract must remain compatible with:

- CORE-04 project-local state and sidecar storage contract
- CORE-05 configurable policy trigger contract
- CORE-06 action/evidence model
- current task-session sidecar contracts
- desktop-agent-first operation loop
- future policy-aware runner
- future policy evidence checker
- future frontend configuration console

Compatibility requirements:

- approved policies must be distinct from pending proposals
- active policy lookup must not depend on chat memory
- every durable policy write must have target, effect, non-effect, and approval evidence
- policy store records must preserve unknown fields for forward compatibility
- policy snapshots in task sessions are evidence/projection, not the policy source of truth
- frontend and desktop agent must consume the same policy objects

---

## 5. Deferred Kernel Backlog

This contract supports later tasks but does not implement them:

- `JIKUO-AGENT-07_policy_aware_agent_flow_proposal`
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`
- revision / rollback implementation beyond guarded active-store append, guarded deprecation, and guarded supersession
- persisted policy proposal card / decision renderer
- installable Codex Skill
- MCP tool wrapper
- Codex Plugin
- frontend configuration / audit surfaces
- gate enforcement adapter

---

## 6. Policy Store Source Hierarchy

Policy sources should be resolved in this order:

1. `kernel_default_policy`: bundled kernel-level defaults.
2. `scenario_package_default_policy`: selected scenario package defaults, such as engineering governance.
3. `project_approved_policy`: approved project-local user policies.
4. `work_order_policy_snapshot`: a snapshot used for one task or work order.
5. `task_session_policy_snapshot`: evidence of what policy set was active during one task session.
6. `policy_proposal`: pending candidate; never active until approved.
7. `desktop_card_projection`: non-canonical display.
8. `chat_summary`: non-canonical convenience.

Rules:

- active policy execution should use approved policy sources only
- proposals are not active policies
- task-session snapshots help audit what happened; they must not silently mutate approved policy
- desktop cards and frontend views are projections only

---

## 7. Future Store Layout Proposal

Future layout:

```text
.jikuo/
  policies/
    manifest.yaml
    approved/
      POLICY-<slug>.yaml
    decisions/
      POLICYDECISION-<id>.yaml
    proposals/
      POLICYPROPOSAL-<id>.yaml
    deprecated/
      POLICY-<slug>-v<N>.yaml
    superseded/
      POLICY-<slug>-v<N>.yaml
```

This layout is a proposal only. This document does not create these paths.

Layout rules:

- `manifest.yaml` indexes policy ids and active versions
- `approved/` contains active or report-only approved policies
- `decisions/` contains compact audit records for guarded policy writes
- `proposals/` contains pending policy proposals that are not active
- `deprecated/` contains policies intentionally retired
- `superseded/` contains prior versions replaced by newer approved versions
- writers must not overwrite existing policies without creating a revision/supersession record

---

## 8. Policy Store Manifest: `jikuo.policy_store_manifest.v0`

Minimal shape:

```yaml
schema_version: "jikuo.policy_store_manifest.v0"
project_id: "..."
store_root: ".jikuo/policies"
active_policy_refs:
  - policy_id: "POLICY-..."
    version: 1
    path: ".jikuo/policies/approved/POLICY-....yaml"
proposal_refs:
  - proposal_id: "POLICYPROPOSAL-..."
    path: ".jikuo/policies/proposals/POLICYPROPOSAL-....yaml"
deprecated_policy_refs: []
superseded_policy_refs: []
last_updated_at: "ISO-8601"
compatibility:
  unknown_fields: "preserve"
```

Rules:

- manifest is an index, not the full source of policy semantics
- unknown fields must be preserved by future writers
- duplicate active policy ids should refuse
- stale manifest should produce review status, not silent success

---

## 9. Policy Proposal: `jikuo.policy_proposal.v0`

Minimal shape:

```yaml
schema_version: "jikuo.policy_proposal.v0"
proposal_id: "POLICYPROPOSAL-..."
status: "draft | rendered | revised | accepted_for_write | rejected | deferred | superseded"
source:
  type: "user_natural_language | required_reference_file | agent_instruction_doc | design_doc_contract | work_order_contract"
  ref: "<exact user phrase as spoken>"
proposed_policy:
  schema_version: "jikuo.configurable_rule_policy.v0"
  policy_id: "POLICY-..."
  version: 1
review:
  rendered_to_desktop_chat: true
  changed_by_user: false
  reviewer_notes: []
decision:
  user_decision: null
  approval_phrase: null
write_plan_ref: null
```

Rules:

- a proposal is not active
- a proposal can be revised multiple times before approval
- approval must name the exact write target and effect
- rejected proposals may be retained only as compact governance records, not raw chat

---

## 10. Approved Policy Record

Approved policy records use the CORE-05 `jikuo.configurable_rule_policy.v0` shape plus storage metadata.

Additional required fields:

```yaml
storage:
  policy_store_ref: ".jikuo/policies"
  path: ".jikuo/policies/approved/POLICY-....yaml"
  checksum: null
  created_by: "agent | user | tool"
approval:
  approved_by: "user"
  approval_phrase: "<exact user phrase as spoken>"
  approved_at: "ISO-8601"
  approved_effect: "create approved project policy POLICY-..."
  non_effect: "does not execute actions, run gates, or modify runtime product behavior"
revision:
  version: 1
  supersedes: []
  superseded_by: null
```

Rules:

- an approved policy is durable configuration, not evidence of execution
- creating an approved policy does not execute the policy
- policy execution evidence belongs to CORE-06 evidence objects and future task sessions
- enforcement phase remains separate from approval

---

## 11. Policy Decision Record: `jikuo.policy_decision.v0`

Minimal shape:

```yaml
schema_version: "jikuo.policy_decision.v0"
decision_id: "POLICYDECISION-..."
proposal_ref: "POLICYPROPOSAL-..."
policy_ref: "POLICY-..."
decision: "approve_write | request_revision | reject | defer | deprecate | supersede"
target:
  kind: "policy_proposal | approved_policy | manifest"
  ref: "POLICY-..."
effect: "..."
non_effect: "..."
approval_phrase: "<exact user phrase as spoken>"
created_at: "ISO-8601"
storage:
  path: ".jikuo/policies/decisions/POLICYDECISION-....yaml"
  policy_store_ref: ".jikuo/policies"
```

Rules:

- every durable policy write needs a decision record
- decision records must preserve target and effect
- one approval must not authorize multiple hidden writes
- exact phrases are examples of captured evidence, not fixed commands users must memorize
- decision records are audit records, not active policy sources

---

## 12. Policy Write Plan: `jikuo.policy_write_plan.v0`

Minimal shape:

```yaml
schema_version: "jikuo.policy_write_plan.v0"
plan_id: "POLICYWRITEPLAN-..."
operation: "create_policy | revise_policy | deprecate_policy | supersede_policy | update_manifest"
proposal_ref: "POLICYPROPOSAL-..."
policy_ref: "POLICY-..."
preflight:
  project_state_initialized: true
  store_exists: false
  target_collision: false
  manifest_stale: false
  approval_present: false
write_set:
  - path: ".jikuo/policies/approved/POLICY-....yaml"
    effect: "create approved policy file"
non_effects:
  - "does not execute policy"
  - "does not create task-session evidence"
  - "does not promote gates"
approval_required: true
```

Rules:

- write plans are previews until explicitly approved
- writers must refuse target collisions unless supersession is explicit
- writers must preserve unknown fields
- manifest updates should be separate or explicitly included in the write set
- a plan must be renderable as a desktop approval card

---

## 13. Policy Write Result: `jikuo.policy_write_result.v0`

Minimal shape:

```yaml
schema_version: "jikuo.policy_write_result.v0"
plan_ref: "POLICYWRITEPLAN-..."
status: "written | refused | failed | dry_run"
written_paths: []
refused_reason: null
post_write_verification:
  reread_ok: false
  manifest_updated: false
  active_policy_resolvable: false
created_at: "ISO-8601"
```

Rules:

- write result must report exactly what changed
- failed partial writes require cleanup or explicit review
- successful writes must be re-read before reported as active
- dry-run results must not create files

---

## 14. Desktop APP Configuration Flow

Primary flow:

1. User states a working-method preference or required reference rule in Codex / Claude desktop APP chat.
2. Agent classifies it as a policy candidate, not an active rule.
3. Agent renders a compact policy proposal card in the same chat.
4. User approves, revises, rejects, or defers.
5. If approved for planning, the current proposal-only runner prepares a write plan without writing files.
6. Agent renders write target, effect, non-effect, and approval requirement.
7. User approves the specific write effect.
8. The guarded writer writes approved policy and manifest only after technical confirmation.
9. Agent renders write result and active policy summary.

UX rules:

- routine configuration should not require the user to leave the desktop APP chat
- advanced CLI may exist as fallback, not primary path
- frontend configuration may later make editing easier, but it must use the same policy objects
- users should not need to memorize exact command phrases

---

## 15. Revision, Deprecation, Supersession, Rollback

Policy lifecycle states:

- `draft`
- `proposal_rendered`
- `approved_report_only`
- `active_report_only`
- `revision_requested`
- `deprecated`
- `superseded`
- `rollback_requested`

Rules:

- revisions create a new version
- supersession must name the previous policy/version
- deprecation does not delete history
- rollback restores or reactivates a prior approved version through a new decision record
- enforcement promotion is not rollback; it belongs to a later gate work order

No-write evolution planning:

```yaml
schema_version: "jikuo.policy_evolution_plan.v0"
plan_id: "POLICYEVO-..."
operation: "refine_policy | deprecate_policy | supersede_policy"
status: "review | refused"
target_policy_ref: "POLICY-..."
feedback:
  feedback_type: "not_applicable | defer | needs_scope_narrowing"
  summary: "..."
future_write_boundary:
  requires_new_proposal: true
  requires_decision_record: true
  requires_guarded_writer: true
  writer_implemented: false
```

Rules:

- evolution plans are review objects, not durable policy mutations
- a plan must name an active target policy
- a plan must not deprecate, supersede, revise, or roll back anything by itself
- actual evolution writers must be guarded by a separate approval and decision record

Implemented guarded evolution writer:

- `deprecate_policy` is supported as a narrow guarded writer
- deprecation moves the target policy out of `active_policy_refs` and into `deprecated_policy_refs`
- deprecation does not delete or rewrite the policy file
- deprecation writes a proposal snapshot and a decision record
- `supersede_policy` is supported as a narrow guarded writer
- supersession requires `replacement_policy_ref` to point at an already existing
  replacement policy
- supersession does not create or edit replacement policy content
- supersession moves the target policy out of `active_policy_refs` and into `superseded_policy_refs`
- if the existing replacement policy is approved but not active, supersession
  may add it to `active_policy_refs`
- if the existing replacement policy is already active, supersession must not
  duplicate the active ref
- supersession leaves the original policy file available for audit
- supersession writes a proposal snapshot and a decision record
- replacement policy creation, import, activation, or editing belongs to a
  separate guarded workflow before supersession
- `refine_policy`, in-place revision, and rollback remain plan-only until separate guarded writers exist

Supersession non-effects:

- does not generate replacement policy content
- does not modify the replacement policy body
- does not judge semantic equivalence between the old and replacement policies
- does not use `replacement_title`, trigger, scope, action, or evidence fields
  as hidden replacement-content creation inputs

---

## 16. Import From AGENTS / Long Documents

Import posture:

- AGENTS / CLAUDE / long docs are candidate sources, not automatic active policy stores
- extraction should produce policy proposals for user review
- users may approve extracted policy candidates one by one or as a named bundle in a future flow
- raw long prose should remain source reference, not become unreviewed machine policy

Safety rules:

- do not bulk-import into active policy without explicit approval
- do not rewrite `.codex/AGENTS.md` in this flow
- preserve source refs so later reviewers know why a policy exists

---

## 17. Relationship To Existing Registry

Current `rule_registry.yaml` remains the existing engineering-governance registry source.

Future policy store relationship:

- kernel/scenario default rules may continue to live in accepted docs or registry files
- project-approved user policies may live in future `.jikuo/policies/approved/`
- checker migration from registry-only to policy-store-aware behavior requires a later work order
- registry and policy store must not fork silently

Migration rule:

- moving any current registry rule into policy store requires explicit migration plan, diff, approval, and rollback.

---

## 18. Non-Goals

This contract and current MVP tool path still do not implement:

- policy proposal persistence
- policy revision, supersession, deprecation, or rollback
- proposal record persistence
- import/extraction from AGENTS
- advanced policy condition evaluation
- evidence persistence or action execution
- UI / Skill / MCP / Plugin packaging
- gate enforcement
- narrative-engine runtime behavior

---

## 19. Acceptance Rule

This contract is acceptable if it makes the following clear:

- where future approved policies should live
- why proposals are not active policies
- how users approve, revise, reject, or defer policy candidates
- how durable writes preserve target/effect/non-effect
- how revision, deprecation, supersession, and rollback work
- how desktop APP remains the primary configuration surface
- why no policy write implementation is approved by this slice
