# JIKUO Execution Mounts

> **Date**: 2026-05-05  
> **Status**: Accepted execution-order mount for JIKUO productization  
> **Purpose**: provide the current required execution order and mounted context for future JIKUO tasks.  
> **Primary user surface**: Codex / Claude desktop APP chat.  
> **Current application track**: AI-primary engineering governance.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 中文摘要

这份文档是后续继续“机括”产品化时必须优先挂载的执行路线文档。

当前已接受的路线是：

1. 先定义 `JIKUO-AGENT-04: Desktop Agent Invocation Contract`，确定触发词、Agent 调用、批准回路。
2. 再做 `agent_flow.py`，作为本地确定性主流程。
3. 再写轻量 Skill / Agent 指引，让 Codex 当前能更稳定地调用它。
4. 再把 `agent_flow.py` 包成 MCP tool，优先解决 Claude / 跨客户端一致性。
5. 最后再考虑 Codex Plugin，把 Codex 侧体验包装得更产品化。

核心原则：

- 用户日常使用机括时，主入口是 Codex / Claude 桌面 APP。
- CLI / helper 是 Agent 内部工具，不是普通用户主流程。
- Skill 负责让 Agent 知道该做什么。
- `agent_flow.py` 负责把流程变成确定性本地动作。
- MCP 负责让 Claude / 跨客户端稳定调用。
- Plugin 负责后续 Codex 产品化包装。

---

## 2. Required Mount Set For Future JIKUO Tasks

When continuing the JIKUO productization track, read this document first, then mount the relevant task-specific documents.

Always mount:

- `docs/jikuo/README.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/jikuo/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

Atomic capability registry:

- current registry location: `docs/jikuo/governance/jikuo_productization_task_map.md` section `Atomic Capability Registry`
- do not create a separate atomic-capability registry document unless the registry needs machine-readable extraction
- if machine-readable extraction becomes necessary, derive it from the task-map section rather than creating divergent sources of truth

Loop composition map:

- current first loop composition location: `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md` section `Loop Composition Map`
- use loop composition maps to understand which `CAP-*` atoms a user-facing loop depends on
- do not duplicate atom definitions inside loop maps; reference `CAP-*` IDs from the task-map registry
- future `agent_flow.py` and MCP work should preserve loop step ids and atom ids in trace output

Skeleton / kernel boundary:

- current boundary location: `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- every future JIKUO work order should declare its `JIKUO layer`, what it is not implementing, kernel compatibility notes, and deferred kernel backlog refs
- skeleton work may preserve future policy hook points, but must not claim configurable rule-kernel implementation
- `R-013` in `rule_registry.yaml` reports missing layer / kernel declarations in report-only mode

Configurable rule trigger policy:

- current policy contract location: `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- mount this document for future configurable-rule-kernel, policy-store, policy-aware runner, policy evidence checker, UI configuration, MCP, Skill, Plugin, or gate work
- this contract defines policy sources, triggers, conditions, required actions, required evidence, document mounts, lifecycle, and projection hooks
- this contract does not implement policy persistence, action execution, evidence checking, UI, Skill, MCP, Plugin, or gates

Rule action / evidence model:

- current action/evidence model location: `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- mount this document for future policy-aware runner, evidence checker, task-session evidence persistence, UI audit surface, MCP, Skill, Plugin, or gate work
- this model defines policy actions, evidence requirements, produced evidence, satisfaction matching, missing-evidence reports, and compact retention boundaries
- this model does not implement action execution, evidence persistence, policy-aware runner behavior, evidence checking, UI, Skill, MCP, Plugin, or gates

Policy store / user configuration flow:

- current policy store/configuration contract location: `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- mount this document for future policy-aware runner, policy store adapter, evidence checker, UI configuration, MCP, Skill, Plugin, or gate work
- this contract defines policy store source hierarchy, future `.jikuo/policies/` layout proposal, policy proposals, approved policy metadata, decision records, write plans/results, revision, deprecation, supersession, rollback, and desktop APP configuration flow
- current implementation includes a read-only status adapter, report-only trigger/condition/evidence evaluator, explicit task-session policy evidence ingestion, proposal-only policy write planning, guarded initial policy-store writing, guarded active-store append, and guarded policy decision records: `tools/jikuo/policy_store.py status`; `tools/jikuo/policy_store.py evaluate`; `tools/jikuo/policy_store.py plan-write`; `tools/jikuo/policy_store.py write-policy`
- read-only / proposal-only paths do not create `.jikuo/policies/`; the guarded writer may create `.jikuo/policies/` only with explicit confirmation and approval; no path executes actions, auto-persists evidence, updates `.jikuo/project_state.yaml`, or implements UI, Skill, MCP, Plugin, or gates

Policy-aware agent flow projection:

- current projection contract location: `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- mount this document before future `agent_flow.py` policy-aware implementation, MCP wrapper, Skill / Plugin packaging, frontend run-control, or checker integration work
- this contract defines policy context, policy store status, triggered policy, required action, evidence status, missing evidence, and fallback projection for desktop proposal cards
- the current runner implements read-only policy-store status projection, exact lifecycle trigger evaluation, report-only condition evaluation, report-only inline evidence matching, guarded persistence proposal, explicit task-session policy evidence ingestion, proposal-only policy write-plan cards, and guarded writer command previews from this contract
- this contract and fallback do not write policy stores, execute actions, persist evidence, or implement UI, Skill, MCP, Plugin, or gates

For desktop invocation work, also mount:

- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-06_lightweight_desktop_agent_instruction_pack.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-08_policy_aware_agent_flow_fallback.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-08_read_only_policy_store_inspection.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-09_policy_trigger_evaluator_mvp.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-10_policy_evidence_checker_mvp.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-11_policy_evidence_persistence_proposal_bridge.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-12_policy_evidence_ingestion_mvp.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-13_policy_condition_evaluator_mvp.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-14_policy_write_plan_proposal_mvp.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-15_guarded_policy_store_write_mvp.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-16_active_policy_store_append_mvp.md` after it exists
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-17_policy_decision_record_mvp.md` after it exists
- `docs/jikuo/governance/jikuo_desktop_agent_instruction_pack.md` after it exists
- `tools/jikuo/task_session_cards.py`
- `tools/jikuo/task_session.py`
- `tools/jikuo/policy_store.py`

For future MCP / plugin work, also mount:

- the accepted `JIKUO-AGENT-04` work order after user review
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-PKG-00_package_boundary_and_extraction_plan.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-20_project_context_binding_and_policy_template_portability.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SEC-01_trust_privacy_provenance_baseline.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-PKG-01_minimal_package_extraction.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-21_policy_template_extraction_import_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-22_starter_policy_pack_first_use_initialization.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-MCP-01_mcp_wrapper_mvp.md`
- any generated MCP / skill / plugin contract documents

For future policy template extraction / import work, also mount:

- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-21_policy_template_extraction_import_mvp.md`
- the source approved-policy directory when extracting local seeds, such as `D:\personal_project\NarrativeSystem\.jikuo\policies\approved`

For future starter policy pack / first-use initialization work, also mount:

- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-22_starter_policy_pack_first_use_initialization.md`
- `src/jikuo/starter_policy_packs/engineering_governance/manifest.yaml`
- `src/jikuo/policy_templates/engineering_governance/*.yaml`

---

## 3. Accepted Execution Order

### Step 1: `JIKUO-AGENT-04` Desktop Agent Invocation Contract

Goal:

- define how Codex / Claude desktop APP agents invoke JIKUO from the chat workflow.

Current status:

- accepted by user for downstream local deterministic `agent_flow.py` implementation.

Must define:

- explicit low-cost trigger phrases
- agent-suggested trigger conditions
- automatic internal helper invocation rules
- how cards / summaries are pasted back into the same chat
- approval / rejection / modification loop
- refusal and ambiguity handling
- no CLI requirement for ordinary users

Must not implement yet:

- `agent_flow.py`
- skill
- MCP server
- plugin
- frontend
- automatic durable write

### Step 2: Local Deterministic `agent_flow.py`

Goal:

- provide one local deterministic entry point for the desktop agent to call.

Current status:

- minimal no-write `propose` path implemented and accepted for downstream instruction-pack planning.
- policy-aware fallback projection, read-only policy-store discovery, exact lifecycle trigger evaluation, report-only condition evaluation, report-only inline evidence matching, desktop-visible live policy evaluation, guarded evidence persistence proposal, guarded policy feedback proposal, guarded task-session evidence apply through `agent_flow.py`, explicit task-session evidence ingestion, proposal-only policy write planning, guarded initial policy-store writing, guarded active-store append, guarded policy decision records, proposal persistence, no-write policy evolution planning, guarded deprecation writing, guarded supersession writing, and policy evolution proposal-to-apply binding are implemented; durable revision / rollback writers, broader action execution, broader condition/evidence ingestion, and gates remain deferred.

Expected shape:

```powershell
python -B tools/jikuo/agent_flow.py propose --event "<event>" --task-title "<task title>" --format markdown
```

Potential later shape:

```powershell
python -B tools/jikuo/agent_flow.py apply --card-id "<card id>" --approval-phrase "<exact user phrase as spoken>" --format json
```

Role:

- compose existing atoms
- return chat-ready cards / summaries
- validate approval target and effect
- refuse unsafe or ambiguous actions

Current implemented shape:

```powershell
python -B tools/jikuo/agent_flow.py propose --event task_start --task-title "<task title>" --format markdown
python -B tools/jikuo/agent_flow.py apply --operation task_session_evidence_update --confirm-apply --approval-phrase "<exact user phrase as spoken>" --format json
python -B tools/jikuo/agent_flow.py apply --operation policy_evolution_write --proposal-ref "<approved proposal ref>" --confirm-apply --approval-phrase "<exact user phrase as spoken>" --format json
```

Current boundary:

- proposal mode remains no-write
- guarded apply is limited to `task_session_evidence_update`, `policy_evolution_write`, and `starter_policy_pack_init`
- `policy_evolution_write` guarded apply requires a proposal ref that matches the deterministic plan before any write
- no arbitrary command execution
- emits loop step id and atom id trace
- emits `jikuo.agent_flow_proposal.v1` with read-only policy-store status, exact trigger evaluation, report-only condition evaluation, report-only evidence matching, guarded evidence persistence proposal, explicit task-session evidence ingestion, policy write-plan cards, no-write policy evolution-plan cards, and starter policy pack initialization cards where requested
- emits `jikuo.agent_flow_apply_result.v0` for narrow approved task-session evidence, policy evolution, and starter policy pack initialization apply paths

### Step 3: Lightweight Codex Skill / Agent Instruction

Goal:

- make Codex more likely to invoke `agent_flow.py` from the desktop APP workflow.

Current status:

- project-local desktop-agent instruction pack implemented and ready for user review.
- not installed as a Codex Skill.
- no `.codex/AGENTS.md` promotion.

Role:

- instruction layer
- trigger phrase convention
- no-code or low-code adoption layer

Boundary:

- improves compliance but does not provide deterministic execution by itself
- must call `agent_flow.py` or later MCP/tool layer for actual process logic
- current pack authorizes no-write `agent_flow.py propose` only
- installable Skill packaging remains a later decision

### Step 4: MCP Tool Wrapper

Goal:

- expose JIKUO as a stable tool API for Claude and cross-client consistency.

Current status:

- `JIKUO-MCP-01` work order is drafted but blocked by pre-MCP portability / security / package foundation.
- `JIKUO-PKG-00` is the current next task.
- implementation has not started.
- this step is packaging-only: wrap stable `agent_flow.py` / `policy_store.py` atoms without adding new governance capability.

Scoped MVP tool calls:

- `jikuo.status`
- `jikuo.propose_task_start`
- `jikuo.propose_policy_write_plan`
- `jikuo.propose_policy_evolution_plan`
- `jikuo.apply_task_session_evidence_update`
- `jikuo.apply_policy_evolution_write`

Role:

- reliable cross-client tool layer
- future Claude Desktop primary integration path
- shared API over the same local deterministic flow
- same-chat proposal / apply card rendering for desktop Agents

Boundary:

- no-write proposal paths remain no-write
- guarded apply paths preserve confirmation, approval phrase, and proposal-ref binding requirements
- no rollback, in-place revision, gate, frontend, Skill, Plugin, or broad action executor
- no MCP implementation before package boundary, project-context binding, privacy return boundaries, and hardcoded resource-reference hygiene are accepted or explicitly deferred

### Step 5: Codex Plugin

Goal:

- package the Codex-side experience more cleanly after the core invocation and tool layers are stable.

Role:

- productized Codex distribution / UX wrapper
- optional richer integration

Boundary:

- do not start here
- do not make Codex Plugin the core abstraction before MCP / local runner semantics are stable

### Current Kernel Branch: Configurable Rule Trigger Policy

Goal:

- define how user-configured rules become triggerable process policies before implementing policy execution.

Current status:

- `JIKUO-CORE-05` implemented as a contract and ready for user review.
- no policy store, policy-aware runner, evidence checker, UI, Skill, MCP, Plugin, or gate is implemented by this contract.

Role:

- preserve the original JIKUO product purpose: important rules should be code-visible policies, not probabilistic long-form instructions.
- provide the upstream contract for `JIKUO-CORE-06`, `JIKUO-CORE-07`, `JIKUO-AGENT-07`, and `JIKUO-CHECKER-02`.
- this branch may continue before packaging work when the project chooses to deepen the kernel rather than package the current skeleton.

### Current Kernel Branch: Rule Action And Evidence Model

Goal:

- define what a triggered policy requires the agent/tool/user to do, what evidence is expected, and how missing evidence is reported.

Current status:

- `JIKUO-CORE-06` implemented as a contract and ready for user review.
- no action execution, evidence persistence, evidence checker, policy-aware runner, UI, Skill, MCP, Plugin, or gate is implemented by this contract.

Role:

- make triggered policy compliance inspectable before any automation or gate exists.
- provide the upstream contract for `JIKUO-CORE-07`, `JIKUO-AGENT-07`, and `JIKUO-CHECKER-02`.

### Current Kernel Branch: Policy Store And User Configuration Flow

Goal:

- define how ordinary users configure durable project policies from desktop APP chat without relying on raw YAML as the primary interface.

Current status:

- `JIKUO-CORE-07` implemented as a contract and ready for user review.
- no `.jikuo/policies/` directory, policy persistence, store adapter, policy-aware runner, UI, Skill, MCP, Plugin, or gate is implemented by this contract.

Role:

- keep pending proposals separate from approved active policies.
- provide the upstream contract for `JIKUO-AGENT-07`, `JIKUO-CHECKER-02`, future store adapter, future UI configuration, and packaging surfaces.

### Current Skeleton Branch: Policy-Aware Agent Flow Projection

Goal:

- define how future desktop proposal cards expose policy store status, triggered policies, required actions, evidence status, and missing evidence.

Current status:

- `JIKUO-AGENT-07` implemented as a projection contract and ready for user review.
- `JIKUO-AGENT-08` implemented the no-write fallback projection in `agent_flow.py`.
- `JIKUO-CORE-08` implemented a read-only policy-store status adapter and connected it to `agent_flow.py propose`.
- `JIKUO-CORE-09` implemented exact lifecycle trigger evaluation and required-action projection in `policy_store.py evaluate` and `agent_flow.py propose`.
- `JIKUO-CORE-10` implemented report-only inline evidence matching and runner-produced `card_rendered` evidence projection.
- `JIKUO-CORE-11` implemented proposal-only policy evidence persistence bridge to the existing guarded task-session evidence append path.
- `JIKUO-CORE-12` implemented explicit task-session policy evidence ingestion for report-only matching.
- `JIKUO-CORE-13` implemented explicit-input policy condition evaluation for report-only matching.
- `JIKUO-CORE-14` implemented proposal-only policy write-plan cards.
- `JIKUO-CORE-15` implemented guarded initial policy-store writing.
- `JIKUO-CORE-16` implemented guarded active-store append.
- `JIKUO-CORE-17` implemented guarded policy decision records.
- proposal persistence, no-write policy evolution planning, guarded deprecation writing, guarded supersession writing, `agent_flow.py apply --operation policy_evolution_write`, and proposal-to-apply binding are implemented; durable revision / rollback writers, action executor, broader condition/evidence ingestion, UI, Skill, MCP, Plugin, and gate remain deferred.

Role:

- connect configurable-rule-kernel contracts back to Desktop App Primary Operating Loop.
- keep policy-unavailable states honest instead of silently treating missing infrastructure as successful policy evaluation.

---

## 4. Trigger Model

JIKUO should use a dual-trigger model.

Explicit user trigger:

- low learning cost
- reliable
- suitable for MVP

Examples:

- `"<exact user phrase as spoken>"`
- `"<exact user phrase as spoken>"`
- `"<exact user phrase as spoken>"`

Agent-suggested trigger:

- smoother experience
- not reliable enough as the only path
- should prompt the user when governance seems relevant

Examples:

- task start
- completion / delivery
- handoff
- rule preference
- required reference file declaration
- gate / enforcement promotion

Rule:

- critical JIKUO actions should not depend only on the agent remembering long-form instructions
- explicit trigger phrase and tool-backed invocation should be available for every critical loop

---

## 5. Surface Roles

Codex / Claude desktop APP:

- primary operation surface
- user intent
- cards / summaries
- approval / rejection / modification
- result reporting

CLI:

- internal bridge
- deterministic debugging path
- advanced-user fallback
- not the routine user path

Frontend:

- configuration
- control
- audit history
- browsing
- not required for ordinary task start / approval / handoff

Skill:

- instruction and behavior guidance
- low-cost adoption layer
- not deterministic enough alone

MCP:

- stable tool layer
- cross-client invocation path
- preferred long-term callable abstraction

Plugin:

- Codex-side packaging and product polish
- later, after runner / MCP semantics are stable

---

## 6. Current Next Task

Current next task:

- review `JIKUO-SEC-01` trust privacy provenance baseline
- then review `JIKUO-PKG-01` initial local package extraction before `CORE-20B`

Task goal:

- confirm that reusable templates and future MCP responses have explicit trust, privacy, provenance, namespace, principal, telemetry, and timestamp boundaries before implementation.

Acceptance target for `JIKUO-SEC-01`:

- work order exists at `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-SEC-01_trust_privacy_provenance_baseline.md`
- governance contract exists at `docs/jikuo/governance/jikuo_trust_privacy_provenance_baseline.md`
- provenance, principal, privacy, namespace, telemetry, time, and concurrency baseline fields are defined at contract level
- telemetry default is off
- MCP-facing result fields distinguish returned, local-only, and redacted data classes
- no auth, signing, telemetry, redaction, locks, package extraction, or MCP implementation is created by this slice
- `JIKUO-MCP-01` remains blocked until portability / security / package foundation is accepted or explicitly deferred
- rollback, broader conditions, UI, Plugin, and gates remain deferred

If accepted:

- review / accept `JIKUO-PKG-01` initial local package extraction next.
- after `PKG-01`, review `JIKUO-CORE-20B` resource-reference and `CONTRACT_REFS` hygiene inside the extracted package boundary.

If revised:

- update the SEC-01 trust / privacy baseline, task map, and mount docs before package extraction, CORE-20B, or MCP implementation.

---

## 7. Do Not Do Next

Do not do next:

- do not build frontend before `JIKUO-AGENT-04`
- do not expand helper-only CLI flow before desktop invocation is specified
- do not rely on pure natural-language automatic trigger as the only path
- do not implement configurable rule kernel behavior inside skeleton / packaging work
- do not implement `CORE-20B` resource-reference hygiene before package extraction unless the user explicitly defers `PKG-01`
- do not implement MCP before local invocation contract and `agent_flow.py` semantics are clear
- do not implement MCP before package extraction, project-context binding, privacy return boundaries, and hardcoded resource-reference hygiene are accepted or explicitly deferred
- do not build Codex Plugin before MCP / runner semantics stabilize
- do not promote gates or blocking behavior as part of this line
