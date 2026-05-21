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

- `README.md`
- `docs/README.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_productization_task_map.md` as a legacy L3 projection only; do not treat it as the source of truth for new task sequencing, open-item facts, capability metadata, or registry authority.
- `docs/governance/jikuo_policy_governance_authority.md`
- `docs/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`

Standalone path rule:

- Current active JIKUO product documents live under `docs/`; do not use legacy nested documentation roots for active mounts.
- Source-project history is not part of the active mount set unless explicitly promoted into this repository.
- Package-owned command previews should use `python -B -m jikuo...`; source references should point at `src/jikuo/...` or `pkg://jikuo/...` as appropriate.

Program-level roadmap anchor:

- New sessions must keep two context layers visible before making implementation choices: the program-level roadmap below, and the current slice / work-order anchors from `docs/registry/work_orders.yaml`.
- This anchor is intentionally short. It prevents new sessions from mistaking the current POLTRIG / DOCREG slice for the whole JIKUO roadmap.
- Do not move this anchor into `docs/governance/jikuo_productization_task_map.md`; that file is a legacy L3 projection, not the source for new task sequencing.
- Current program tracks:
  - MCP and client runtime: MCP MVP Stage A / B1 / B2 / B3 are implemented; remaining work is release proof, client compatibility expansion, and future router / adapter surfacing.
  - Strict mounted harness: Codex `UserPromptSubmit` hook proof is the current Codex host-boundary candidate, with Claude hook proof still tracked separately; MCP plus instruction files remain instruction-level, not strict mounted, until a host adapter proves otherwise. The Level 1 project-local Codex proof files now exist and local stdin smoke has passed, the local Level 2A input path can receive compact `host_semantic_intent` through CLI / MCP / Codex hook proof and merge it into `work_profile`, and the Level 2B MCP Sampling probe can ask a Sampling-capable client for compact semantic intent during a tool call. A trusted Codex GUI run on 2026-05-21 accepted the narrower pre-turn `additionalContext` injection surface after timeout remediation. Host-time semantic provider status, multi-intent semantic proof, and full lifecycle completion-review linkage remain pending. The hook proof must separately report mounted invocation status, semantic-intent status, multi-intent slice handling, and end-to-end GUI trigger flow: deterministic keyword routing is fallback/conflict evidence, not a substitute for host AI or dedicated semantic-classifier proof, MCP Sampling is optional classifier evidence rather than strict mounted proof, multi-intent turns must preserve per-slice explanation plus aggregate policy scopes, and full strict-mounted lifecycle proof still needs visible pre-turn plus completion-review lifecycle cards.
  - Lifecycle / action-grammar infrastructure: `LIFECYCLE-01` is now the current primary foundation task, but the direction is minimum sustainable governance rather than a heavy fixed lifecycle. LIFECYCLE-01B implements the lighter record-only direction: once JIKUO is invoked for a user turn, runtime visibility should show the lifecycle nodes that actually produced cards (`conversation_turn`, `task_start`, `completion_review`, plus optional nodes), the observed/missing recommended node status, and card links. Customer-facing generated Markdown should end with an `Observed Lifecycle` footer that lists only `node_name: card_link` lines for the observed cards. LIFECYCLE-01C is the current design slice: define the minimum checkpoint contract around `pre-work` (`see -> classify -> trigger`), `governed-work` (`think -> act`), and `pre-final` (`see -> trigger -> report`) without adding a runner. It does not force missing nodes to run, does not prove GUI clients forced invocation, and does not make checkpoint design count as execution proof; host hook proof remains separate. Known architecture gap: MCP tools are callable surfaces and `agent_flow` is a node-local proposal runner, so no current layer guarantees `conversation_turn -> task_start -> completion_review` ordering. Architecture calibration: fixed lifecycle may be too rigid for AI work; semantic routing should start from `user_intent -> policy_scope -> process_contract -> execution_boundary -> response_contract`, while `see / think / act / report` remains dynamic execution and evidence vocabulary. Contract-field effect must be proved through projection -> planning use -> evidence verification -> boundary enforcement/flagging, while evaluator consumption remains limited to final lifecycle event plus aggregate policy scopes. Track `INSIGHT-2026-05-21-lifecycle-sequencing-owner-gap` and `INSIGHT-2026-05-21-from-lifecycle-to-action-grammar` before designing a runner / harness sequencing owner.
  - Policy management: POLTRIG-01A / 01B / 02 / 03 are implemented. The near-term policy-management work is intentionally lightweight: activate the two held user-authored candidates through existing no-write plan / guarded apply paths, and design official distribution boundaries.
  - Document registry: DOCREG-01A / B1 / B2 are complete; DOCREG-01B3 is deferred unless a registry-specific completion checker need is approved, because the current main-document completion obligation already exists in policy governance.
  - Runtime data and analytics: DATA-01A defines execution-event fixtures and schema direction; runtime event emission, history scanning, dashboard / BI, and support-bundle export remain future slices.
  - Policy catalog and starter packs: official starter policy distribution must remain separate from JIKUO self-bootstrap policies, must never overwrite user-approved local policies, and remains opt-in.
  - Release and assets: GitHub private preview exists; license, trademark / domain posture, packaging, CI, PyPI, and public-review readiness remain explicit release decisions.
  - Product surfaces: Studio / dashboard, per-client hook packs, Agent SDK / ADK adapters, and OS notifications remain product expansion tracks after the harness and data model stabilize.
  - Self-bootstrap boundary: the parent harness workspace / child source repository layout is an accepted spike, not an approved source-tree migration.

Slice completion main document check:

- Before closing any JIKUO development slice, check `.jikuo/project_context.yaml`.
- Check `README.md` when the product-facing project status, quickstart, MCP surface, release posture, or GitHub preview path changes.
- Check `docs/README.md` when document roots, directory roles, or entry points change.
- Check `docs/governance/jikuo_execution_mounts.md` when required mounts, execution order, command previews, program-level roadmap anchor, or active context changes.
- Check `docs/governance/jikuo_policy_governance_authority.md` when policy lifecycle, source boundaries, trigger routing, task classification, AI hint, deterministic signal priority, fallback expansion, or policy distribution posture changes.
- Check `docs/governance/jikuo_productization_task_map.md` only when repairing projection text, projection links, frozen-section notices, or an explicitly approved regeneration. New task sequencing, open-item facts, capability metadata, and registry authority belong in the DOCREG work order or `docs/registry/*.yaml`.
- Check `docs/registry/registry_index.yaml` when registry shard authority, projection metadata, or impact-tag routing changes.
- Check `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md` while DOCREG is still in transition and registry scope or sequencing changes.
- Check `docs/insights/insights_registry.yaml` when a development idea is captured, promoted, resolved, or deferred.
- Check `.jikuo/policies/manifest.yaml` when approved, deprecated, superseded, or proposal policy refs change.
- If a checked main document does not need an update, report that it was checked and why the existing scope remains valid.

Task context bundles:

- For a registered work order, inspect `docs/registry/work_orders.yaml` before implementation and mount any `required_mount_sets`.
- Treat `originating_evidence_refs` as the root-cause evidence for why a task exists; read it before summarizing business meaning.
- Treat `authority_refs` as the accepted design boundary for the task.
- Treat `stop_boundaries` as review points, especially before evaluator, policy-store, registry-authority, or durable-write behavior changes.
- Keep these anchors sparse. Do not replace them with a hand-maintained reverse graph.

Atomic capability registry:

- legacy projection location: `docs/governance/jikuo_productization_task_map.md` section `Atomic Capability Registry`
- draft structured registry location: `docs/registry/capabilities.yaml`
- registry index: `docs/registry/registry_index.yaml`
- `JIKUO-DOCREG-01` remains the transitional authority for DOCREG sequencing while the draft registry is reviewed and stabilized

Loop composition map:

- current first loop composition location: `docs/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md` section `Loop Composition Map`
- use loop composition maps to understand which `CAP-*` atoms a user-facing loop depends on
- do not duplicate atom definitions inside loop maps; reference `CAP-*` IDs from the task-map registry
- future `agent_flow.py` and MCP work should preserve loop step ids and atom ids in trace output

Skeleton / kernel boundary:

- current boundary location: `docs/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- every future JIKUO work order should declare its `JIKUO layer`, what it is not implementing, kernel compatibility notes, and deferred kernel backlog refs
- skeleton work may preserve future policy hook points, but must not claim configurable rule-kernel implementation
- `R-013` in `rule_registry.yaml` reports missing layer / kernel declarations in report-only mode

Configurable rule trigger policy:

- current policy contract location: `docs/governance/jikuo_configurable_rule_trigger_policy.md`
- mount this document for future configurable-rule-kernel, policy-store, policy-aware runner, policy evidence checker, UI configuration, MCP, Skill, Plugin, or gate work
- this contract defines policy sources, triggers, conditions, required actions, required evidence, document mounts, lifecycle, and projection hooks
- this contract does not implement policy persistence, action execution, evidence checking, UI, Skill, MCP, Plugin, or gates

Rule action / evidence model:

- current action/evidence model location: `docs/governance/jikuo_rule_action_evidence_model.md`
- mount this document for future policy-aware runner, evidence checker, task-session evidence persistence, UI audit surface, MCP, Skill, Plugin, or gate work
- this model defines policy actions, evidence requirements, produced evidence, satisfaction matching, missing-evidence reports, and compact retention boundaries
- this model does not implement action execution, evidence persistence, policy-aware runner behavior, evidence checking, UI, Skill, MCP, Plugin, or gates

Policy store / user configuration flow:

- current policy store/configuration contract location: `docs/governance/jikuo_policy_store_configuration_flow.md`
- mount this document for future policy-aware runner, policy store adapter, evidence checker, UI configuration, MCP, Skill, Plugin, or gate work
- this contract defines policy store source hierarchy, future `.jikuo/policies/` layout proposal, policy proposals, approved policy metadata, decision records, write plans/results, revision, deprecation, supersession, rollback, and desktop APP configuration flow
- current implementation includes a read-only status adapter, report-only trigger/condition/evidence evaluator, explicit task-session policy evidence ingestion, proposal-only policy write planning, guarded initial policy-store writing, guarded active-store append, and guarded policy decision records: `python -B -m jikuo.policy_store status`; `python -B -m jikuo.policy_store evaluate`; `python -B -m jikuo.policy_store plan-write`; `python -B -m jikuo.policy_store write-policy`
- read-only / proposal-only paths do not create `.jikuo/policies/`; the guarded writer may create `.jikuo/policies/` only with explicit confirmation and approval; no path executes actions, auto-persists evidence, updates `.jikuo/project_state.yaml`, or implements UI, Skill, MCP, Plugin, or gates

Policy governance authority:

- current policy-governance authority location: `docs/governance/jikuo_policy_governance_authority.md`
- mount this document before discussing or changing policy lifecycle, source boundaries, policy catalog / starter-pack posture, trigger routing, task classification, AI hint handling, deterministic hard-signal priority, fallback expansion, or policy-scope matching
- this document defines the current product direction: policy routing is hint-assisted, deterministic-checked, and fallback-expanded; `other` / uncertain work must expand to at least discussion plus editing policy scopes instead of falling through to no-op
- this document does not activate, edit, deprecate, supersede, distribute, or implement policy records by itself

Policy-aware agent flow projection:

- current projection contract location: `docs/governance/jikuo_policy_aware_agent_flow_contract.md`
- mount this document before future `agent_flow.py` policy-aware implementation, MCP wrapper, Skill / Plugin packaging, frontend run-control, or checker integration work
- this contract defines policy context, policy store status, triggered policy, required action, evidence status, missing evidence, and fallback projection for desktop proposal cards
- the current runner implements read-only policy-store status projection, exact lifecycle trigger evaluation, report-only condition evaluation, report-only inline evidence matching, guarded persistence proposal, explicit task-session policy evidence ingestion, proposal-only policy write-plan cards, and guarded writer command previews from this contract
- this contract and fallback do not write policy stores, execute actions, persist evidence, or implement UI, Skill, MCP, Plugin, or gates

For desktop invocation work, also mount:

- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-01_desktop_agent_card_projection_contract.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-06_lightweight_desktop_agent_instruction_pack.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-08_policy_aware_agent_flow_fallback.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-08_read_only_policy_store_inspection.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-09_policy_trigger_evaluator_mvp.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-10_policy_evidence_checker_mvp.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-11_policy_evidence_persistence_proposal_bridge.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-12_policy_evidence_ingestion_mvp.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-13_policy_condition_evaluator_mvp.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-14_policy_write_plan_proposal_mvp.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-15_guarded_policy_store_write_mvp.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-16_active_policy_store_append_mvp.md` after it exists
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-17_policy_decision_record_mvp.md` after it exists
- `docs/governance/jikuo_desktop_agent_instruction_pack.md` after it exists
- `src/jikuo/task_session_cards.py`
- `src/jikuo/task_session.py`
- `src/jikuo/policy_store.py`

For future MCP / plugin work, also mount:

- the accepted `JIKUO-AGENT-04` work order after user review
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-PKG-00_package_boundary_and_extraction_plan.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-20_project_context_binding_and_policy_template_portability.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SEC-01_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-PKG-01_minimal_package_extraction.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-21_policy_template_extraction_import_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-22_starter_policy_pack_first_use_initialization.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-10_policy_runtime_status_card.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-11_deterministic_harness_chat_return_contract.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-12_out_of_band_runtime_visibility_channels.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-14_completion_review_policy_only_surfacing.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-15_self_bootstrap_task_session_binding.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-19_starter_policy_provenance_backfill.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SEC-02_mcp_response_privacy_classification_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INTG-01_universal_instruction_file_distribution.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MCP-01_mcp_wrapper_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-02_integration_neutrality_and_integrations_layout.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SDK-01_agent_sdk_adapter_exploration.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CODEX-PLUGIN-01_codex_plugin_pre_turn_harness_review.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CLAUDE-HOOK-01_claude_hook_strict_adapter_review.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SELF-BOOTSTRAP-03_harness_workspace_boundary_spike.md`
- any generated MCP / skill / plugin contract documents

For future policy template extraction / import work, also mount:

- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-21_policy_template_extraction_import_mvp.md`
- the source approved-policy directory when extracting local seeds; exported package templates must redact local source paths and source project identity
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-23_project_context_template_activation.md` for template import planning, resolver, and guarded activation work
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-24_agent_flow_template_activation_bridge.md` for desktop-visible template import planning and guarded `agent_flow.py apply`

For future source-project archive / migration handoff work, also mount:

- `docs/migration/NARRATIVESYSTEM_RESOURCE_POOL_HANDOFF.md`
- `docs/migration/narrativesystem_resource_pool_handoff.yaml`

For future starter policy pack / first-use initialization work, also mount:

- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-22_starter_policy_pack_first_use_initialization.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-19_starter_policy_provenance_backfill.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-CATALOG-01_self_bootstrap_policy_promotion_review.md`
- `src/jikuo/starter_policy_packs/engineering_governance/manifest.yaml`
- `src/jikuo/policy_templates/engineering_governance/*.yaml`

For future Dashboard / Studio frontend work, also mount:

- `docs/insights/INSIGHT-2026-05-16-studio-dashboard-frontend-architecture.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DATA-01_structured_execution_event_ledger_and_analytics_contract.md`
- `docs/schemas/execution_events_v0_draft.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-12_out_of_band_runtime_visibility_channels.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MCP-01_mcp_wrapper_mvp.md`

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
python -B -m jikuo.agent_flow propose --event "<event>" --task-title "<task title>" --format markdown
```

Potential later shape:

```powershell
python -B -m jikuo.agent_flow apply --card-id "<card id>" --approval-phrase "<exact user phrase as spoken>" --format json
```

Role:

- compose existing atoms
- return chat-ready cards / summaries
- return `chat_ready_markdown` in JSON output so desktop agents and future MCP wrappers can surface the same card text without reinterpretation
- validate approval target and effect
- refuse unsafe or ambiguous actions

Current implemented shape:

```powershell
python -B -m jikuo.agent_flow propose --event task_start --task-title "<task title>" --format markdown
python -B -m jikuo.agent_flow apply --operation task_session_evidence_update --confirm-apply --approval-phrase "<exact user phrase as spoken>" --format json
python -B -m jikuo.agent_flow apply --operation policy_evolution_write --proposal-ref "<approved proposal ref>" --confirm-apply --approval-phrase "<exact user phrase as spoken>" --format json
```

Current boundary:

- proposal mode remains no-write
- guarded apply is limited to `task_session_evidence_update`, `policy_evolution_write`, and `starter_policy_pack_init`
- `policy_evolution_write` guarded apply requires a proposal ref that matches the deterministic plan before any write
- no arbitrary command execution
- emits loop step id and atom id trace
- emits `chat_ready_markdown_schema: jikuo.chat_ready_markdown.v0` and `chat_ready_markdown` in JSON output for proposals and apply results
- emits `jikuo.agent_flow_proposal.v1` with read-only policy-store status, exact trigger evaluation, report-only condition evaluation, report-only evidence matching, visible policy runtime status cards, work-routing distinction evidence, guarded evidence persistence proposal, explicit task-session evidence ingestion, policy write-plan cards, no-write policy evolution-plan cards, and starter policy pack initialization cards where requested
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
- harness surfacing instruction: once JIKUO is activated, the agent must call the runner / MCP tool and return its `chat_ready_markdown` or Markdown cards in the same chat

Boundary:

- improves compliance but does not provide deterministic execution by itself
- must call `agent_flow.py` or later MCP/tool layer for actual process logic
- must not summarize away `policy_runtime_status`, write effects, approval boundaries, evidence state, or atom trace after tool execution
- current pack authorizes no-write `agent_flow.py propose` only
- installable Skill packaging remains a later decision

### Step 4: MCP Tool Wrapper

Goal:

- expose JIKUO as a stable tool API for Claude and cross-client consistency.

Current status:

- `JIKUO-MCP-01` work order is drafted but blocked by pre-MCP portability / security / package / visibility foundation.
- `JIKUO-LIVE-12` Phase 1 is accepted as the out-of-band runtime visibility baseline; `JIKUO-ARCH-02` is accepted as the integration-neutrality layout contract; `JIKUO-SDK-01` is accepted as the Agent SDK and agentic platform extension-posture review; `JIKUO-INTG-01` is implemented and accepted as the cross-client instruction foundation before MCP implementation.
- `JIKUO-LIVE-13` is accepted as the self-bootstrap evidence-quality slice; normal task-start proposals now satisfy the taskmap / insight / follow-up distinction evidence requirement.
- `JIKUO-LIVE-14` is accepted as the completion-review surfacing slice; completion-review policy evidence can now succeed visibly while task-session lifecycle unavailability remains separate review context.
- `JIKUO-LIVE-15` is accepted as the self-bootstrap task-session binding slice; task-start proposals now emit task-session binding evidence, `agent_flow.py apply --operation task_session_start` can create a guarded session, and the current LIVE-15 slice has a durable task-session record.
- implementation has not started.
- this step is packaging-only: wrap stable `agent_flow.py` / `policy_store.py` atoms without adding new governance capability.

Scoped MVP tool calls:

- `jikuo.status`
- `jikuo.get_runtime_status`
- `jikuo.get_runtime_status_card`
- `jikuo.get_display_card`
- `jikuo.propose_task_start`
- `jikuo.propose_policy_write_plan`
- `jikuo.propose_policy_evolution_plan`
- `jikuo.propose_policy_template_import_plan`
- `jikuo.apply_task_session_evidence_update`
- `jikuo.apply_policy_evolution_write`
- `jikuo.apply_policy_template_activation`

Role:

- reliable cross-client tool layer
- future MCP-compatible desktop integration path
- shared API over the same local deterministic flow
- same-chat proposal / apply card rendering for desktop Agents through `chat_ready_markdown`
- out-of-band runtime visibility through `.jikuo/runtime/` and `jikuo show`

Boundary:

- no-write proposal paths remain no-write
- guarded apply paths preserve confirmation, approval phrase, and proposal-ref binding requirements
- proposal tools must return structured results plus `chat_ready_markdown`; `policy_runtime_status` must remain visible when present
- card-producing tools must include display directives and update runtime visibility, or explicitly report that runtime visibility is unavailable
- no rollback, in-place revision, gate, frontend, Skill, Plugin, or broad action executor
- no MCP implementation before package boundary, project-context binding, hardcoded resource-reference hygiene, `JIKUO-LIVE-12`, `JIKUO-ARCH-02`, `JIKUO-SDK-01`, `JIKUO-LIVE-19` starter policy provenance backfill, `JIKUO-SEC-02` response privacy classification, and previous/latest todo snapshot posture are accepted or explicitly deferred; `JIKUO-INTG-01` is accepted and must be preserved by the MCP display contract

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

JIKUO should use a dual-trigger model for activation discovery, followed by deterministic harness execution.

Current implementation note:

- today, JIKUO still depends on the active desktop Agent or MCP client choosing to call the tool / command; a normal user message does not automatically enter the JIKUO runtime
- this means active policies can be correct but still invisible if the client does not invoke JIKUO
- policy extraction from repeated user needs should not be narrowed to `task_start`, `completion`, or any other work-order-only event; it can arise during any ordinary user turn

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
- once a flow is inside JIKUO coverage, card return is a harness obligation rather than a style choice
- governed execution is incomplete if triggered policies, non-triggered policies, missing evidence, approval boundaries, write effects, or atom trace are hidden from the same-chat result
- semantic trigger mode is allowed as a lightweight adoption path, but it must be described honestly as client / agent mediated
- mounted harness mode is the stricter product direction: once selected, JIKUO should run before every user turn and return an explicit router / policy status result, even when the result is "no JIKUO action required"
- strict mounted harness behavior should be implemented through integration adapters such as MCP router tools, Agent SDK wrappers, a local proxy / Studio entry, or per-client hooks; the JIKUO kernel should remain integration-neutral

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

- current dependency update: `POLICY-jikuo-proactive-policy-suggestion-metapolicy` has been superseded by `POLICY-jikuo-conversation-level-proactive-policy-suggestion`; the active policy now triggers on `conversation_turn`
- next dependency: implement proactive policy-suggestion review evidence so conversation-turn policy checks produce compact review evidence instead of remaining visibly missing
- next implementation: build the no-write `conversation_turn` router from accepted `JIKUO-ROUTER-01` before adding mounted-harness adapters
- accepted `JIKUO-LIVE-12` Phase 1 out-of-band runtime visibility
- accepted `JIKUO-LIVE-14` completion review policy-only surfacing
- accepted `JIKUO-LIVE-15` self-bootstrap task-session binding
- `JIKUO-ARCH-03` MCP pre-implementation API neutrality review is complete and accepted
- `JIKUO-MCP-01` MVP body Stage A / B1 / B2 / B3 is implemented and externally smoke-accepted; remaining MCP work is release proof / client compatibility / future router expansion, not the original MVP body

Task goal:

- make JIKUO trigger coverage explicit rather than hidden in agent judgment: semantic mode remains available, but the roadmap now needs a conversation-turn router and a future mounted harness path that can run before every user turn.

Accepted target for the current pre-MCP visibility review:

- `JIKUO-LIVE-12` writes `.jikuo/runtime/last_card.md`, `.jikuo/runtime/state_summary.json`, runtime history, exposes `jikuo show`, and returns `client_display_links` for direct desktop click targets
- `JIKUO-ARCH-02` is accepted and keeps integration-specific logic under `src/jikuo/integrations/` while anchoring MCP under `src/jikuo/integrations/mcp/`
- `JIKUO-ARCH-03` is accepted and verifies that the first MCP wrapper can call structured core APIs instead of CLI `main()` or stdout scraping; remaining acceptance blocker is revised `JIKUO-MCP-01`
- `JIKUO-LIVE-19` backfills `verified_jikuo_official` provenance onto official starter policies in plan and guarded initialization outputs, resolving the starter provenance MCP blocker
- `JIKUO-SEC-02` is accepted and defines field-level MCP response privacy classification and startup checklist requirements; MCP implementation must preserve this privacy contract
- `JIKUO-LIVE-16` makes `policy_runtime_status` the first visible governance card in chat-ready and runtime-card output while keeping structured `cards[]` order stable for callers
- `JIKUO-LIVE-17` keeps `latest_task_session_refs` as a separate guarded refresh and makes stale/current task-session index status visible through `jikuo show`
- `JIKUO-LIVE-18` disables the fake same-file `previous_todo_map` binding for v0 and records guarded snapshot rotation as a deferred future capability
- `JIKUO-MCP-01` includes `jikuo.get_runtime_status`, `jikuo.get_runtime_status_card`, `jikuo.get_display_card`, display directives, card priority order, runtime snapshot refs, `display_verification`, and integration-neutral implementation placement
- `JIKUO-MCP-01` is split into Stage A and Stage B: Stage A contains 8 no-write / card / proposal tools, while Stage B contains guarded write tools and cannot start until Stage A acceptance gates pass or are explicitly revised by the user
- `JIKUO-MCP-01` selects `src/jikuo/fixtures/policy_store_active_project` as the first Stage A integration fixture, requires SDK-free `adapter.py` plus schema definitions before protocol wrapping, and isolates the official MCP SDK to `server.py`
- `JIKUO-MCP-01` Stage A acceptance requires `jikuo.get_runtime_status_card` to show the same single-card Markdown through chat, `.jikuo/runtime/last_card.md`, and `jikuo show --last-card`; broader proposal tools may show full proposal Markdown, but policy runtime status must remain first when present
- `JIKUO-MCP-01` Stage A SDK-free adapter boundary is implemented: `src/jikuo/integrations/mcp/adapter.py`, `schemas.py`, and `tests/mcp_adapter_tests.py` expose the 8 no-write / card / proposal tools without importing MCP SDK code; `server.py` and real-client smoke are accepted for Stage A
- `JIKUO-MCP-01` official SDK availability was checked on 2026-05-15 and the user approved declaring the Python `mcp` dependency: `server.py` is implemented as a thin official FastMCP wrapper over the SDK-free adapter; real SDK import / module-entry smoke and official SDK `ClientSession` stdio smoke passed after installing `mcp 1.27.1` in a test environment, and desktop-client configuration smoke is accepted as user-verified in Codex Desktop and Claude Desktop
- `JIKUO-MCP-01` client setup examples now live at `docs/integrations/mcp_client_configuration_examples.md`; Codex / Claude MCP proof is accepted for current private-preview work, and the same examples remain the regression / expansion path for Cursor and VS Code + GitHub Copilot Agent Mode
- `JIKUO-MCP-01` Stage A desktop smoke is accepted as user-verified on 2026-05-15 for Codex Desktop and Claude Desktop, and both clients are treated as active private-preview MCP clients; Stage B2 policy evolution guarded-write is implemented and externally smoke-accepted, and Stage B3 policy-template activation is implemented after explicit user acceptance
- `JIKUO-MCP-01` Stage B1 is accepted and implemented for `jikuo.apply_task_session_evidence_update`; Stage B2 is accepted, implemented, and externally smoke-accepted on 2026-05-16 for `jikuo.apply_policy_evolution_write`; Stage B3 is accepted and implemented for `jikuo.apply_policy_template_activation`
- `JIKUO-MCP-01` Stage B1 official SDK smoke passed during the B1 slice: a Python MCP `ClientSession` listed 9 tools, called `jikuo.apply_task_session_evidence_update`, and confirmed Stage B2 / B3 tools were not exposed before later Stage B2 approval
- `JIKUO-MCP-01` Stage B2 Claude-assisted acceptance passed with adapter and FastMCP wrapper tool lists showing 10 tools, B2 refusal / apply paths working, no task-session side effects, no raw approval phrase leakage, fixture runtime card written, and Stage B3 still absent during that slice
- `JIKUO-MCP-01` Stage B3 Claude Code GUI acceptance passed: adapter and FastMCP wrapper exposed 11 tools including `jikuo.apply_policy_template_activation`; refusal and approved activation paths work, proposal / decision / approved policy / manifest writes are present, no task-session side effects occur, raw approval phrase is redacted, fixture runtime card output is written, and no GUI MCP client cache issue was observed
- `JIKUO-MCP-01` MCP MVP body release smoke passed on 2026-05-16: official SDK `ClientSession` discovered all 11 tools and verified `jikuo.get_runtime_status_card` runtime-card parity in a temporary fixture project
- JIKUO release-readiness baseline now includes a product-facing root `README.md`, `.[dev]` pytest extras in `pyproject.toml`, and `.github/workflows/test.yml`; the external release license remains an explicit user decision
- `JIKUO-REL-01` drafts the external release license decision brief; use it before changing `pyproject.toml`, adding a `LICENSE` file, or publishing outside the private workspace
- `JIKUO-INTG-01` is accepted and implements canonical `JIKUO.md` plus guarded client instruction sync without making client hooks mandatory
- `JIKUO-SDK-01` is accepted and defines OpenAI Agents SDK, Claude Agent SDK, Google ADK, Vercel AI SDK, and Google Antigravity-style agentic platforms as optional orchestration / client-environment adapters that consume JIKUO through MCP / CLI / public adapter APIs while local policy, evidence, approvals, and runtime visibility remain authoritative
- `JIKUO-ROUTER-01` is accepted: it defines semantic mode, mounted harness mode, the `conversation_turn` event, a no-write router output shape, implemented MCP router tools, and future Agent SDK / Studio / strict adapter expectations
- `JIKUO-LIVE-15` adds a self-bootstrap requirement that governed JIKUO development slices bind, create, or explicitly defer a task-session at task start; `.jikuo/project_state.yaml latest_task_session_refs` refresh remains a separate guarded action unless promoted later
- `JIKUO-LIVE-21` hardens that requirement so every governed `task_start`, including documentation / registry / data-contract slices, surfaces task-session resolution as `existing_session_bound`, `needs_user_decision`, or `explicitly_deferred`
- `INSIGHT-2026-05-17-work-unit-task-association-boundary` records the deferred data-architecture boundary: future `work_order_id -> work_unit_id -> proposal/card` links must be explicit and reliable; do not implement heavy association fields before Codex / Claude hook or another strict mounted adapter proves consistent invocation
- `JIKUO-MCP-01` prerequisites for Stage A, Stage B1, Stage B2, and Stage B3 are accepted, and MCP MVP body release smoke has passed; product-surface expansion remains a separate approval point
- `CAP-CONVERSATION-TURN-ROUTER-01` core no-write path is implemented in `agent_flow.py`: `python -B -m jikuo.agent_flow propose --event conversation_turn --user-phrase "<user turn>" --trigger-mode semantic|mounted --format json`
- `CAP-JIKUO-TRIGGER-MODE-01` now has an observable core difference: `semantic` with no matching obligation returns `no_jikuo_action_required`, while `mounted` with no matching obligation returns `mounted_idle_tick`
- `JIKUO-INTG-02` records the client-onboarding settings contract: `jikuo install --trigger-mode ask|semantic|mounted` can generate client instruction blocks that prompt or pin the activation mode, and `vscode-copilot` maps to `.github/copilot-instructions.md`
- `JIKUO-INTG-02` now has project-level guarded persistence: `jikuo settings plan|apply` manages `.jikuo/activation_settings.yaml`; `jikuo show`, `jikuo install`, and conversation-turn routing read it when no explicit mode override is supplied
- `JIKUO-INIT-01` records the first-use configuration review surface: `jikuo configure status|review`, `agent_flow propose --event configuration_review`, MCP `jikuo.get_configuration_status`, MCP activation settings read / plan tools, and guarded MCP `jikuo.apply_activation_settings_update` expose setup review and approved activation writes; mount `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INIT-01_first_use_configuration_review.md` for future router tools, Studio/dashboard setup views, or strict client-adapter onboarding work
- `JIKUO-INIT-02` records reviewed configuration onboarding: missing activation settings and legacy settings without review metadata are treated as unreviewed defaults, first active JIKUO use injects `configuration_review` before task work when no explicit trigger-mode override exists, and guarded activation apply records whether each key setting is a user-reviewed default or a user-configured value
- strict mounted behavior is not achieved by MCP plus instruction files alone; it requires a future pre-turn host adapter such as a Claude Code hook, Agent SDK wrapper, Studio/local proxy, Codex plugin, Cursor extension, or VS Code extension
- `JIKUO-INTG-03` records the strict mounted adapter contract: host adapters must read `.jikuo/activation_settings.yaml`, call JIKUO before each user turn in mounted mode, surface card markdown or runtime links, and visibly fail rather than silently bypass governance
- `JIKUO-CODEX-PLUGIN-01` records the Codex hook / plugin feasibility task: Level 1 project-local `UserPromptSubmit` proof files exist, and a 2026-05-21 trusted Codex GUI run accepted pre-turn `additionalContext` injection after timeout remediation; Codex MCP availability itself is already accepted, while host-time semantic provider proof, multi-intent semantic proof, and full lifecycle strict-mounted acceptance remain pending
- `JIKUO-CLAUDE-HOOK-01` records the Claude hook feasibility task: verify whether a Claude hook-capable host can run `jikuo.route_user_request` before every user turn, surface card markdown or runtime links, and visibly fail before claiming Claude strict mounted behavior; this track can be implemented alongside a Codex adapter if both prove stable
- `JIKUO-LIVE-20` records the policy dead-zone detection task: NarrativeSystem usage showed that mounted MCP access can coexist with around 10 active policies and repeated zero-trigger cards; LIVE-20A now classifies each zero-trigger policy runtime card as non-governance event, route follow-up required, missing/mismatched task context, condition mismatch, policy coverage gap, or unknown event before users trust the governance result
- `JIKUO-DATA-01` records the structured execution event-ledger and analytics contract: future dashboard, BI, support bundles, and audit views should read schema-versioned local execution events rather than scraping Markdown cards, while raw transcripts and remote telemetry remain out of scope
- `JIKUO-DOCREG-01` records the layered document-registry transition: until `docs/registry/registry_index.yaml` and first shards exist, it is the current task-list authority for DOCREG sequencing, registry scope, and the deferred self-bootstrap hierarchy item
- `JIKUO-SELF-BOOTSTRAP-02` records the stable self-bootstrap execution strategy task: JIKUO development should consistently invoke route/config/task-start/completion-review tooling, bind or explicitly defer task sessions, surface runtime card links, and check main docs before commits
- `JIKUO-SELF-BOOTSTRAP-03` records the harness workspace boundary spike: self-bootstrap should test whether JIKUO runs more truthfully from a parent harness workspace that owns `.jikuo/`, activation settings, runtime cards, and client instructions while treating the source repository as a governed child target; no source-tree migration is approved by this record
- `docs/integrations/mcp_client_proof_playbook.md` is the current manual proof guide for regression and expansion proof; Codex / Claude proof is accepted, while Cursor and VS Code + GitHub Copilot Agent Mode remain future compatibility targets before broad cross-client support is claimed
- `docs/migration/NARRATIVESYSTEM_RESOURCE_POOL_HANDOFF.md` records the 2026-05-16 JIKUO-side active reference migration: `docs/jikuo/` and `tools/jikuo/` in NarrativeSystem are no longer active JIKUO runtime / contract dependencies, while NarrativeSystem scenario registry and sprint index files still require a separate NarrativeSystem-side scan before archive decisions
- policy evolution proposal/apply surfaces now preserve non-default replacement triggers through `--replacement-trigger-event`, so a reviewed supersession can target `conversation_turn` without silently falling back to `task_start`
- dashboard / Studio UI, OS notifications, packaged per-client hook packs beyond accepted proof tasks, source-directory migration, rollback, broader conditions, UI, Plugin, and gates remain deferred; current MCP visibility relies on card markdown plus runtime card links
- `INSIGHT-2026-05-16-studio-dashboard-frontend-architecture` records the current frontend architecture posture for future `JIKUO-STUDIO-01`: projection-first view models, panel registration, guarded action registration, and canonical `.jikuo/` state remain the change-friendly boundary
- `POLICY-jikuo-conversation-level-proactive-policy-suggestion` is active report-only: repeated user needs, corrections, or preferences are reviewed as policy candidates at `conversation_turn` before they remain hidden chat behavior; automatic policy mining and activation remain deferred.
- `CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01` is implemented in the core conversation-turn proposal path and exposed through MCP `jikuo.propose_policy_suggestions`: it produces compact candidate/no-candidate `proactive_policy_suggestion_review_evidence` without storing raw transcripts. Remaining work is strict SDK / mounted-harness surfacing, not kernel policy evidence production.
- `POLICY-jikuo-progress-summary-business-meaning` is active report-only: completion summaries, progress summaries, and todo lists for JIKUO development must include the product or business meaning of major items, not only technical implementation details.

Accepted result:

- keep `JIKUO-LIVE-12` Phase 1 as the baseline runtime visibility foundation for MCP implementation.
- continue MCP Stage B only inside explicitly accepted guarded-write slices.

If revised:

- update the visibility baseline, task map, and mount docs before MCP implementation.

---

## 7. Do Not Do Next

Do not do next:

- do not build frontend before `JIKUO-AGENT-04`
- do not expand helper-only CLI flow before desktop invocation is specified
- do not rely on pure natural-language automatic trigger as the only path
- do not implement configurable rule kernel behavior inside skeleton / packaging work
- do not implement `CORE-20B` resource-reference hygiene before package extraction unless the user explicitly defers `PKG-01`
- do not implement MCP before local invocation contract and `agent_flow.py` semantics are clear
- do not implement MCP before package extraction, project-context binding, hardcoded resource-reference hygiene, out-of-band runtime visibility, integration neutrality, Agent SDK extension posture, universal instruction distribution, API neutrality review, starter policy provenance backfill, response privacy preservation, and revised MCP scope are accepted or explicitly deferred
- do not implement an Agents SDK runner before `JIKUO-SDK-01` is accepted and before MCP / instruction-distribution boundaries decide how SDK orchestration should call JIKUO
- do not build Codex Plugin before MCP / runner semantics stabilize
- do not promote gates or blocking behavior as part of this line
