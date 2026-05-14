# 机括：AI-Primary Process Governance Productization Task Map

> **Date**: 2026-05-03  
> **Updated**: 2026-05-14
> **Status**: Draft task map / planning entry  
> **Source context**: Sprint 050 `WORKTREE-05` governance hardening  
> **Product name**: 机括  
> **Boundary**: This is a productization roadmap, not a runtime narrative-engine work order.
> **Current application track**: AI-primary engineering governance.

---

## 1. Product Positioning

> **中文注释**：机括的长期愿景不是单一工程管理工具，而是 AI 核心过程治理内核。当前开发方向仍然不变：先把工程治理作为第一个应用场景做实。

Long-term vision:

`机括` is an AI-primary process governance kernel.

It governs processes where human intent, AI execution, rule obligations, evidence, approval, state sedimentation, and rule evolution must stay explicit.

Kernel vs first scenario package principle:

> **中文注释**：`AI-primary engineering governance` 是机括当前第一条应用场景包，不是机括长期边界；后续工程任务可以优化这个场景包，但不能把机括重新定义成只服务工程开发的工具。

`JIKUO` is the process-governance kernel.

`AI-primary engineering governance` is the first scenario package built on that kernel.

The kernel manages reusable process primitives:

- human intent
- AI execution
- rule trigger
- evidence
- approval
- state
- handoff
- rollback
- rule evolution

The engineering package binds those primitives to software-development objects:

- work orders
- code changes
- tests
- documentation sync
- task sessions
- commits
- engineering handoff

A current-track task may optimize the engineering package, but it must not redefine the kernel as engineering-only.

Current application track:

`机括` is first being incubated as an AI-primary engineering governance product.

Current-track primary users:

- people who mainly rely on AI to develop software, applications, tools, or systems
- non-professional programmers who have concrete project-development needs and explicit working-method preferences
- solo developers, product founders, or small teams that need AI work to stay auditable, bounded, and repeatable

Not primary users for the current engineering-governance track:

- end users of an AI-built application
- creators who use the resulting application to produce domain content
- reviewers who only judge product output quality and do not govern the development process

Possible future scenario packages:

- creative process governance
- research process governance
- knowledge-production workflow governance
- product-operations workflow governance
- AI application plugin governance

The shared kernel should remain:

- rule lifecycle management
- trigger detection
- evidence reporting
- approval recording
- process-state audit
- rule evolution and supersession

In the current engineering track, it turns project rules from long prose and agent memory into:

- configurable rule records
- trigger conditions
- evidence requirements
- report-only or gate-ready enforcement phases
- human approval points
- audit and evolution history

Product interaction posture:

- desktop-agent-first
- Codex / Claude desktop APP chat is the primary user path
- CLI is an auxiliary bridge / fallback for agents or terminal-preferring users
- standalone frontend is a configuration, control, and audit surface, not the only operating surface

Harness principle:

- JIKUO is a tool-backed harness after activation, not a probabilistic prompt preference.
- Trigger discovery may be explicit or agent-suggested, but covered flows must call the runner / future MCP tool.
- Critical flow state must remain visible, traceable, and auditable in the same desktop chat.
- A governed response that hides policy runtime status, evidence state, write effects, approval boundaries, or atom trace is incomplete.

The first incubating use case is the source-project Sprint 050 governance hardening, but the product concept should remain broader than this repository and broader than engineering alone.

---

## 2. Current Incubation Base

> **中文注释**：这些已经是“机括机芯”的雏形，但目前仍是 the incubating source project 内部治理资产。

Already created in `WORKTREE-05` or incubated from it:

- `05A`: auditable engine evidence model
- `05B`: rule materialization matrix
- `05C`: rule registry schema and `rule_registry.yaml`
- `05D`: report-only local checker
- `05E Part 1`: standalone agent operating kernel draft, accepted by user
- `05E Part 2`: kernel promotion proposal, accepted by user
- `05F`: gate feasibility, awaiting user review
- `JIKUO-UX-00`: user scenario and atomic action map, Part 1 accepted by user
- `JIKUO-PRD-01`: product definition, MVP loop, and desktop-agent-first interaction model, Part 1 accepted by user
- `JIKUO-AGENT-00`: desktop-agent-first interaction contract, Part 1 accepted by user
- `JIKUO-CORE-01`: structured result model, Part 1 accepted by user; Part 2 accepted by user; Part 3 optional JSON output accepted by user
- `JIKUO-CORE-02`: UI-ready rule registry model, Part 1 accepted by user; Part 2 view-model schema accepted for downstream planning
- `JIKUO-FLOW-01`: engineering-governance user journey and interaction flow, draft aligned with accepted scenario-chain and document-mounting model
- `JIKUO-SCENARIO-CHAIN-01`: governance scenario chain and document mounting model, accepted by user for downstream `CORE-03` planning
- `JIKUO-FLOW-02`: Desktop App Primary Operating Loop, accepted by user as the first user operation chain and staged execution order input
- `JIKUO-CORE-03`: task session and evidence model, Part 1 accepted by user; Part 2 task-session schema accepted for downstream projection planning
- `JIKUO-AGENT-01`: desktop-agent card projection contract, accepted by user for downstream project-local state / sidecar storage planning
- `JIKUO-CORE-04`: project-local state and sidecar storage contract, accepted by user for downstream report-only sidecar bootstrap planning
- `JIKUO-SIDECAR-01`: report-only project state bootstrap, accepted by user; `status` / `init --dry-run` helper implemented and accepted for downstream write-mode proposal planning
- `JIKUO-SIDECAR-02`: project-state write mode, accepted by user; initial `.jikuo/project_state.yaml` created and accepted for downstream task-session persistence proposal planning
- `JIKUO-TASKSESSION-01`: task-session sidecar persistence, accepted by user; dry-run start/status helper implemented and accepted for downstream write-mode proposal planning
- `JIKUO-TASKSESSION-02`: task-session write mode, accepted by user; guarded `start --write` implementation complete and accepted for downstream index proposal planning; no project-state index updates created
- `JIKUO-TASKSESSION-03`: project-state task-session index update, accepted by user; `index --dry-run` / guarded `index --refresh` implemented and accepted for downstream lifecycle proposal planning; no root project index writes created
- `JIKUO-TASKSESSION-04`: task-session lifecycle / evidence / completion / handoff boundary, accepted by user; lifecycle update dry-run / guarded append implemented and accepted for downstream `JIKUO-AGENT-02` planning; no root task-session updates created
- `JIKUO-AGENT-02`: desktop-agent task-session workflow cards and command composition, accepted by user for downstream minimal card projection helper planning
- `JIKUO-AGENT-03`: minimal task-session card projection helper, implemented and ready for user review; no desktop adapter, automatic write, frontend, gate, checker migration, registry migration, or runtime implementation
- `JIKUO-AGENT-04`: desktop-agent invocation contract, accepted by user for downstream `agent_flow.py`; defines explicit triggers, agent-suggested triggers, internal atom invocation, chat rendering, approval loop, and refusal / ambiguity handling before runner implementation
- `JIKUO-AGENT-05`: local deterministic `agent_flow.py` proposal runner, accepted as no-write runner for downstream instruction-pack planning; composes existing no-write atoms into Markdown / JSON proposals with loop step id and atom id trace
- `JIKUO-AGENT-06`: lightweight desktop-agent instruction pack, implemented and ready for user review; tells Codex / Claude desktop APP agents when to call `agent_flow.py propose`, how to return cards in chat, and where the write boundary remains
- `JIKUO-ARCH-01`: skeleton / kernel boundary and kernel backlog, implemented and ready for user review; keeps current desktop-operating-skeleton work distinct from future configurable-rule-kernel work
- `JIKUO-CORE-05`: configurable rule trigger and execution policy, implemented and ready for user review; defines how user preferences, mounted reference docs, lifecycle events, changed paths, required actions, and required evidence become a future policy contract without implementing policy execution
- `JIKUO-CORE-06`: rule action and evidence model, implemented and ready for user review; defines action, evidence requirement, produced evidence, satisfaction matching, and missing-evidence report objects without implementing execution or persistence
- `JIKUO-CORE-07`: policy store and user configuration flow, implemented and ready for user review; defines future approved policy store, proposals, decisions, write plans/results, revision, deprecation, supersession, and rollback without creating policy storage
- `JIKUO-AGENT-07`: policy-aware agent flow proposal contract, implemented and ready for user review; defines how future desktop proposal cards project policy store status, triggered policies, required actions, evidence status, and missing evidence without changing `agent_flow.py`
- `JIKUO-AGENT-08`: policy-aware agent flow fallback, implemented and ready for user review; initially added the v1 policy-aware envelope and empty policy/action/evidence arrays; CORE-08 replaced the unavailable fallback with read-only store status while still avoiding sidecar writes
- `JIKUO-DOCS-01`: product doc rehome and reference migration, implemented and ready for user review; JIKUO-owned docs now live under `docs/` while source-project history remains outside active mounts unless explicitly promoted
- `JIKUO-CORE-08`: read-only policy store inspection, implemented and ready for user review; `policy_store.py status` inspects `.jikuo/policies/manifest.yaml` and approved refs without writing, while `agent_flow.py propose` projects store status
- `JIKUO-CORE-09`: policy trigger evaluator MVP, implemented and ready for user review; `policy_store.py evaluate` and `agent_flow.py propose` can report exact lifecycle-event policy matches and required actions without executing actions, checking evidence, writing policies, or creating sidecars
- `JIKUO-CORE-10`: policy evidence checker MVP, implemented and ready for user review; `policy_store.py evaluate` can match required evidence against supplied inline produced evidence, and `agent_flow.py propose` can satisfy `card_rendered` evidence from its own rendered task-start card without writing
- `JIKUO-CORE-11`: policy evidence persistence proposal bridge, implemented and ready for user review; `agent_flow.py propose --event policy_evidence_record` converts explicit policy evidence refs into a guarded task-session evidence append command proposal without writing
- `JIKUO-CORE-12`: policy evidence ingestion MVP, implemented and ready for user review; `policy_store.py evaluate --task-session-id ...` and `agent_flow.py propose --event policy_evidence_check --policy-event ... --session-id ...` can read persisted task-session policy evidence into report-only evidence matching without writing
- `JIKUO-CORE-13`: policy condition evaluator MVP, implemented and ready for user review; `policy_store.py evaluate` and `agent_flow.py propose` can evaluate explicit task metadata / path conditions before projecting required actions, without writing or gating
- `JIKUO-CORE-14`: policy write plan proposal MVP, implemented and ready for user review; `policy_store.py plan-write` and `agent_flow.py propose --event policy_write_plan` can render a no-write policy-store write plan before any durable policy write exists
- `JIKUO-CORE-15`: guarded policy store write MVP, implemented and ready for user review; `policy_store.py write-policy` can create the first approved report-only policy and manifest after explicit confirmation and approval, while `agent_flow.py propose` remains no-write
- `JIKUO-CORE-16`: active policy store append MVP, implemented and ready for user review; `policy_store.py write-policy` can append a second approved report-only policy to an active store after explicit confirmation and approval
- `JIKUO-CORE-17`: policy decision record MVP, implemented and ready for user review; `policy_store.py write-policy` writes a compact `jikuo.policy_decision.v0` record for successful guarded create / append writes
- `JIKUO-CORE-18`: real test data and real chain policy, implemented and ready for user review; adds a loadable approved report-only policy requiring concrete test data / execution-chain evidence for testing-governance work instead of accepting preview-template placeholders as proof
- `JIKUO-CORE-19`: pre-code-change governance classification principle, implemented and ready for user review through a report-only policy fixture; requires evidence that the agent first classified whether a code-change request primarily needs policy / governance-method work, code / design-implementation work, or explicit mixed/unclear handling
- `JIKUO-LIVE-01`: policy evaluation goes live in desktop chat, implemented and ready for user review; composes report-only policy evaluation into `agent_flow.py propose` cards so users can see triggered policies, required actions, missing evidence, and light feedback options without leaving Codex / Claude desktop APP chat
- `JIKUO-LIVE-02`: policy feedback record proposal bridge, implemented and ready for user review; turns explicit `not_applicable`, `defer`, or `needs_scope_narrowing` feedback into a guarded task-session evidence append proposal without writing in propose mode
- `JIKUO-LIVE-03`: guarded agent flow evidence apply, implemented and ready for user review; lets a desktop agent apply one explicitly approved task-session evidence append through `agent_flow.py apply` without broad command execution
- `JIKUO-LIVE-04`: policy proposal persistence, implemented and ready for user review; persists the approved policy write proposal snapshot so decision records point to an existing proposal file
- `JIKUO-LIVE-05`: policy evolution plan proposal, implemented and ready for user review; renders no-write refinement / deprecation / supersession plans for existing active policies before any policy evolution writer exists
- `JIKUO-LIVE-06`: guarded policy deprecation writer MVP, implemented and ready for user review; lets an explicitly approved active policy leave `active_policy_refs` and enter `deprecated_policy_refs` without deleting history
- `JIKUO-LIVE-07`: guarded policy supersession writer MVP, implemented and ready for user review; lets an explicitly approved replacement policy become active while the old active policy enters `superseded_policy_refs`
- `JIKUO-LIVE-08`: agent flow guarded policy evolution apply MVP, implemented and ready for user review; lets a desktop agent apply one explicitly approved policy deprecation / supersession through `agent_flow.py apply`
- `JIKUO-LIVE-09`: proposal-to-apply binding MVP, implemented and ready for user review; requires `agent_flow.py apply --operation policy_evolution_write` to include the proposal ref that the user reviewed, and refuses mismatched refs before any durable write
- `JIKUO-LIVE-10`: policy runtime status card, implemented and ready for user review; appends a visible `policy_runtime_status` card so triggered / non-triggered policies, required actions, and missing evidence are not hidden in structured proposal fields
- `JIKUO-LIVE-11`: deterministic harness chat return contract, implemented and ready for user review; adds `chat_ready_markdown` to JSON runner output and requires desktop / future MCP callers to surface tool-rendered cards rather than probabilistically summarize them away
- `JIKUO-LIVE-12`: out-of-band runtime visibility channels, Phase 1 accepted on 2026-05-14 as a pre-MCP visibility foundation; pairs chat-ready cards with `.jikuo/runtime/` snapshots, `jikuo show`, and client-display links so users can open the latest runtime card without relying on any single desktop Agent
- `JIKUO-LIVE-13`: taskmap / insight / follow-up evidence, accepted on 2026-05-14; `agent_flow.py propose --event task_start` now emits structured `work_routing` and `taskmap_insight_followup_distinction_evidence` so the self-bootstrap summary-distinction policy can be audited by the evidence checker
- `JIKUO-INTG-01`: universal instruction file distribution, implemented and accepted on 2026-05-14 as a pre-MCP companion; adds review-only and guarded `jikuo install` flows for canonical `JIKUO.md` plus client instruction sync without making client-specific hooks a baseline dependency
- `JIKUO-MCP-01`: MCP wrapper MVP work order, drafted and ready for user review; formally shifts the next slice from more kernel expansion to wrapping stable `agent_flow.py` / `policy_store.py` atoms for cross-client desktop Agent invocation
- `JIKUO-ARCH-02`: integration neutrality and `src/jikuo/integrations/` layout, accepted on 2026-05-14 as the immediate pre-MCP architecture contract; anchors protocol / SDK / client adapters outside the kernel before MCP implementation
- `JIKUO-SDK-01`: Agent SDK and agentic platform adapter exploration, accepted on 2026-05-14 as a pre-MCP / MCP-adjacent architecture posture; compares OpenAI Agents SDK, Claude Agent SDK, Google ADK, Google Antigravity, and Vercel AI SDK while preserving future orchestration extensibility without replacing the JIKUO kernel, MCP wrapper, or local runtime evidence authority
- `JIKUO-PKG-00`: package boundary and extraction plan, drafted and ready for user review; separates JIKUO tool-owned package assets from user-project-local `.jikuo/` state before CORE-20 or MCP implementation
- `JIKUO-CORE-20`: project context binding and policy template portability, draft contract ready for user review; separates reusable policy templates from project-specific document / directory bindings
- `JIKUO-SEC-01`: trust, privacy, provenance, namespace, principal, telemetry, and timestamp baseline, draft contract ready for user review
- `JIKUO-PKG-01`: minimal package extraction, initial local package created at `D:\personal_project\Jikuo` and ready for user review; now precedes resource-reference hygiene so `CORE-20B` happens inside the standalone package boundary
- `JIKUO-CORE-20B`: resource-reference and `CONTRACT_REFS` hygiene, implemented and ready for user review; package-owned refs now use `pkg://jikuo/...` and command previews use `python -B -m jikuo...`
- `JIKUO-CORE-21`: policy template extraction / export MVP, implemented from redacted incubating-project approved policy seeds; `JIKUO-CORE-23` extends the flow with project-context resolution and guarded activation
- `JIKUO-CORE-22`: starter policy pack first-use initialization, implemented as a guarded bootstrap path that activates curated report-only starter policies in a project
- `JIKUO-CORE-23`: project context template activation, implemented and ready for user review; `policy_templates.py` now resolves project-context bindings, rejects unsafe paths, previews `jikuo.resolved_policy.v0`, and guardedly activates one resolved template as an approved project policy
- `JIKUO-CORE-24`: agent flow template activation bridge, implemented and ready for user review; `agent_flow.py` now renders template import planning as a visible card and applies one approved template activation through `--operation policy_template_activation`

Current scenario-chain registrations:

| Chain ID | User Scenario | Operation Chain | Registered Atoms | Evidence |
|---|---|---|---|---|
| `policy_template_seed_extraction` | A JIKUO maintainer turns proven approved policies from an incubating project into reusable package templates without activating them in another project | inspect approved source -> plan extraction -> guarded package-template export -> no-write target import preview -> report unresolved bindings | `CAP-POLICY-TEMPLATE-EXTRACT-01`; `CAP-POLICY-TEMPLATE-PORTABILITY-01`; `CAP-PROJECT-CONTEXT-BINDING-01`; `CAP-TRUST-PRIVACY-PROVENANCE-BASELINE-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-21_policy_template_extraction_import_mvp.md` section `Scenario-Chain-Atom Registration Evidence` |
| `starter_policy_pack_first_use` | A new project starts using JIKUO and receives useful report-only starter policies without knowing source-project paths or raw template extraction commands | desktop initialize request -> `agent_flow.py propose` starter card -> user reviews write set and non-effects -> `agent_flow.py apply --operation starter_policy_pack_init` after approval -> project state / policy store initialized -> future task-start proposals evaluate starter policies | `CAP-AGENT-FLOW-01`; `CAP-STARTER-POLICY-PACK-INIT-01`; `CAP-AGENT-FLOW-APPLY-STARTER-POLICY-PACK-01`; `CAP-PROJECT-STATE-WRITE-01`; `CAP-POLICY-STORE-STATUS-01`; `CAP-POLICY-TEMPLATE-EXTRACT-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-22_starter_policy_pack_first_use_initialization.md` section `Scenario-Chain-Atom Registration Evidence` |
| `policy_runtime_visibility` | A desktop Agent user wants to see whether JIKUO rules actually triggered during governed work | agent invokes `agent_flow.py propose` -> policy store is inspected -> active policies are evaluated -> policy runtime card is appended -> user sees triggered and non-triggered policy state in chat | `CAP-LIVE-DESKTOP-POLICY-EVAL-01`; `CAP-POLICY-STORE-STATUS-01`; `CAP-POLICY-TRIGGER-EVALUATE-01`; `CAP-POLICY-CONDITION-EVALUATOR-01`; `CAP-POLICY-EVIDENCE-CHECK-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-10_policy_runtime_status_card.md` section `Scenario-Chain-Atom Registration Evidence` |
| `desktop_chat_harness_surfacing` | A desktop Agent user needs JIKUO output to behave like a strict harness result rather than an optional summary | agent invokes runner / future MCP tool -> tool returns structured result plus `chat_ready_markdown` -> agent posts the chat-ready markdown -> user sees policy runtime status, write boundaries, evidence state, and atom trace in chat | `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-AGENT-FLOW-01`; `CAP-MCP-AGENT-FLOW-WRAPPER-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-11_deterministic_harness_chat_return_contract.md` section `Scenario-Chain-Atom Registration Evidence` |
| `out_of_band_runtime_visibility` | A user needs to verify JIKUO runtime state even when the active Agent does not paste cards back into chat | agent / MCP invokes JIKUO -> card-producing result updates `.jikuo/runtime/last_card.md` and `state_summary.json` -> response exposes direct client-display links -> user runs `jikuo show` or opens the file -> latest policy runtime status is independently visible | `CAP-RUNTIME-VISIBILITY-CHANNEL-01`; `CAP-RUNTIME-SHOW-CLI-01`; `CAP-CLIENT-RUNTIME-LINK-SURFACE-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-12_out_of_band_runtime_visibility_channels.md` |
| `taskmap_insight_followup_evidence` | A JIKUO self-bootstrap user needs taskmap work, insights, and follow-ups distinguished as auditable evidence instead of assistant wording only | task-start proposal builds `work_routing` -> runner produces `taskmap_insight_followup_distinction_evidence` -> policy evaluator matches the evidence -> chat-ready output shows `Work Routing Evidence` -> final user summary can report taskmap / insight / follow-up separately | `CAP-TASKMAP-INSIGHT-FOLLOWUP-EVIDENCE-01`; `CAP-POLICY-EVIDENCE-CHECK-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-13_taskmap_insight_followup_evidence.md` |
| `universal_instruction_distribution` | A project wants multiple desktop Agent clients to follow the same JIKUO harness display contract | generate canonical `JIKUO.md` -> sync reviewed content into supported client instruction files -> agents learn card display and out-of-band verification rules -> client-specific hooks remain optional | `CAP-UNIVERSAL-INSTRUCTION-FILE-01`; `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INTG-01_universal_instruction_file_distribution.md` |
| `integration_neutrality_planning` | A JIKUO maintainer needs MCP / SDK / client wrappers to stay outside the governance kernel | review integration surfaces -> declare core-vs-integration boundary -> anchor MCP under `src/jikuo/integrations/mcp/` -> require API-neutrality review before implementation | `CAP-INTEGRATION-NEUTRALITY-CONTRACT-01`; `CAP-MCP-AGENT-FLOW-WRAPPER-01`; `CAP-AGENTS-SDK-ADAPTER-EXPLORATION-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-02_integration_neutrality_and_integrations_layout.md` |
| `agent_sdk_adapter_exploration` | A JIKUO maintainer needs to know how Agent SDKs and agentic development platforms affect future orchestration before the MCP wrapper hardens | review official OpenAI / Claude / Google ADK / Antigravity / Vercel references -> map SDK and platform agents / tools / handoffs / permissions / guardrails / tracing / artifacts / MCP client support to JIKUO atoms -> define optional adapter posture -> preserve MCP and instruction-distribution extension points | `CAP-AGENTS-SDK-ADAPTER-EXPLORATION-01`; `CAP-INTEGRATION-NEUTRALITY-CONTRACT-01`; `CAP-MCP-AGENT-FLOW-WRAPPER-01`; `CAP-MCP-RUNTIME-STATUS-CARD-01`; `CAP-UNIVERSAL-INSTRUCTION-FILE-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SDK-01_agent_sdk_adapter_exploration.md` |
| `policy_template_import_bind_activate` | A project adopts a reusable JIKUO policy template without copying private paths or activating unsafe bindings | template import plan -> project context read -> role bindings resolved -> unsafe / missing bindings reported -> resolved policy preview rendered -> guarded activation after approval -> active policy appears in policy-store status | `CAP-PROJECT-CONTEXT-RESOLVER-01`; `CAP-POLICY-TEMPLATE-IMPORT-PLAN-01`; `CAP-POLICY-TEMPLATE-ACTIVATE-01`; `CAP-POLICY-STORE-STATUS-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-23_project_context_template_activation.md` section `Scenario-Chain-Atom Registration Evidence` |
| `policy_template_desktop_activation_bridge` | A desktop Agent user adopts a reusable JIKUO policy template and sees bindings, write effects, and activation result in chat | template selected -> `agent_flow.py propose --event policy_template_import_plan` -> project context / bindings resolved -> import card with guarded command rendered -> `agent_flow.py apply --operation policy_template_activation` after approval -> policy-store activation result returned with `chat_ready_markdown` | `CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01`; `CAP-PROJECT-CONTEXT-RESOLVER-01`; `CAP-POLICY-TEMPLATE-IMPORT-PLAN-01`; `CAP-POLICY-TEMPLATE-ACTIVATE-01`; `CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-24_agent_flow_template_activation_bridge.md` section `Scenario-Chain-Atom Registration Evidence` |
| `main_document_mount_maintenance` | A JIKUO maintainer finishes a development slice and needs the active document mount scope to stay visible and current | task-start classification -> update standalone document roles and active mount docs -> register main-document completion scope -> completion review triggers main-document policy -> report checked documents and evidence | `CAP-MAIN-DOC-MOUNT-MAINTENANCE-01`; `CAP-PROJECT-CONTEXT-BINDING-01`; `CAP-EXEC-MOUNT-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01` | `.jikuo/project_context.yaml`; `docs/README.md`; `docs/governance/jikuo_execution_mounts.md`; this task-map section |

Current code / data artifacts:

- `docs/README.md`
- `docs/governance/rule_registry.yaml`
- `docs/schemas/task_session.schema.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_desktop_agent_instruction_pack.md`
- `docs/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/governance/jikuo_rule_action_evidence_model.md`
- `docs/governance/jikuo_policy_store_configuration_flow.md`
- `docs/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCS-01_product_doc_rehome_and_reference_migration.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-04_project_local_state_and_sidecar_storage_contract.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-01_report_only_project_state_bootstrap.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SIDECAR-02_project_state_write_mode_proposal.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-01_task_session_sidecar_persistence_proposal.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-02_task_session_write_mode_proposal.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-03_project_state_task_session_index_update.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-TASKSESSION-04_lifecycle_evidence_completion_handoff.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-02_desktop_agent_task_session_workflow_cards.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-03_minimal_task_session_card_projection_helper.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-05_local_deterministic_agent_flow_proposal_runner.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-06_lightweight_desktop_agent_instruction_pack.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-01_skeleton_kernel_boundary_and_kernel_backlog.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-06_rule_action_and_evidence_model.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-07_policy_store_and_user_configuration_flow.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-07_policy_aware_agent_flow_proposal.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-08_policy_aware_agent_flow_fallback.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-08_read_only_policy_store_inspection.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-09_policy_trigger_evaluator_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-10_policy_evidence_checker_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-11_policy_evidence_persistence_proposal_bridge.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-12_policy_evidence_ingestion_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-13_policy_condition_evaluator_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-14_policy_write_plan_proposal_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-15_guarded_policy_store_write_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-16_active_policy_store_append_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-17_policy_decision_record_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-18_real_test_data_and_chain_policy.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-19_pre_code_change_layer_classification_policy.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-20_project_context_binding_and_policy_template_portability.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SEC-01_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-01_policy_evaluation_goes_live_in_desktop_chat.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-02_policy_feedback_record_proposal_bridge.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-03_guarded_agent_flow_evidence_apply.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-04_policy_proposal_persistence.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-05_policy_evolution_plan_proposal.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-06_guarded_policy_deprecation_writer_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-07_guarded_policy_supersession_writer_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-08_agent_flow_guarded_policy_evolution_apply_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-09_proposal_to_apply_binding_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-10_policy_runtime_status_card.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-11_deterministic_harness_chat_return_contract.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-12_out_of_band_runtime_visibility_channels.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-13_taskmap_insight_followup_evidence.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INTG-01_universal_instruction_file_distribution.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MCP-01_mcp_wrapper_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-02_integration_neutrality_and_integrations_layout.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SDK-01_agent_sdk_adapter_exploration.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-PKG-00_package_boundary_and_extraction_plan.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-PKG-01_minimal_package_extraction.md`
- `.jikuo/project_context.yaml`
- `.jikuo/project_state.yaml`
- `.jikuo/policies/manifest.yaml`
- `docs/insights/insights_registry.yaml`
- `src/jikuo/project_state.py`
- `tests/project_state_tests.py`
- `src/jikuo/task_session.py`
- `tests/task_session_tests.py`
- `src/jikuo/task_session_cards.py`
- `tests/task_session_cards_tests.py`
- `src/jikuo/agent_flow.py`
- `tests/agent_flow_tests.py`
- `src/jikuo/runtime_visibility.py`
- `src/jikuo/cli.py`
- `src/jikuo/__main__.py`
- `tests/runtime_visibility_tests.py`
- `src/jikuo/policy_store.py`
- `tests/policy_store_tests.py`
- `src/jikuo/policy_templates.py`
- `tests/policy_templates_tests.py`
- `src/jikuo/starter_policies.py`
- `tests/starter_policies_tests.py`
- `src/jikuo/fixtures/**`

Current posture:

- report-only for governance gates and checker enforcement
- project-local JIKUO bootstrap state initialized in `.jikuo/project_state.yaml`
- guarded project-state and task-session sidecar write modes exist
- no root project task-session record has been created for the current Codex task
- no hook
- no CI gate
- no task-stop gate
- no frontend UI
- Desktop App Primary Operating Loop is accepted as the first user operation chain
- `jikuo_execution_mounts.md` is the current execution-order mount for future JIKUO tasks
- minimal no-write task-session card projection helper exists
- desktop-agent invocation contract is accepted for downstream `agent_flow.py`
- local deterministic `agent_flow.py propose` exists as no-write runner
- `agent_flow.py propose` emits a policy-aware v1 envelope with read-only policy-store status, report-only exact lifecycle trigger evaluation, and report-only evidence matching for runner-produced card evidence
- `agent_flow.py propose --event policy_evidence_record` can produce a guarded task-session evidence append command proposal from explicit policy evidence refs
- `agent_flow.py propose --event policy_evidence_check --policy-event ... --session-id ...` can read persisted task-session policy evidence and project satisfied evidence status without writing
- `agent_flow.py propose --task-type ... --jikuo-layer ... --changed-path ...` can project report-only condition reports before required actions are exposed
- `agent_flow.py propose --event policy_write_plan` can project a no-write policy-store write plan card before any durable policy writer exists
- `agent_flow.py propose` writes a local runtime visibility projection under `.jikuo/runtime/` and labels that side effect separately from governance writes
- `jikuo show`, `jikuo show --last-card`, and `client_display_links` can inspect or open the latest runtime summary and card without relying on desktop Agent chat behavior
- `policy_store.py write-policy` can create an initial approved report-only policy store only when a guarded command includes confirmation and approval evidence
- `policy_store.py write-policy` can append a new approved report-only policy to an already active store when the policy id is unique and approval evidence is present
- `policy_store.py write-policy` writes a compact policy decision record for successful guarded create / append writes
- a loadable approved policy fixture can require `real_test_data_and_chain_evidence` for testing-governance tasks, making template-copy / shape-only acceptance visible as missing evidence
- a loadable approved policy fixture can require `governance_vs_implementation_classification_evidence` before code-change work, making "should this be a rule or code change?" explicit
- project-local desktop-agent instruction pack exists for same-chat `agent_flow.py propose` invocation
- skeleton / kernel boundary and kernel backlog are mounted as project-local architecture guidance
- `R-013` report-only checker rule reports missing JIKUO layer / kernel compatibility declarations
- no installed Codex Skill yet
- no desktop task-session workflow adapter
- guarded `agent_flow.py apply` paths exist for explicit task-session evidence append and explicit policy deprecation / supersession writes, with proposal-ref binding required for policy evolution apply
- no automatic task-session / audit-event / rule-proposal sidecar persistence yet
- no `.jikuo/task_sessions/` directory yet
- no `.codex/AGENTS.md` promotion without explicit acceptance
- configurable rule trigger policy contract exists, a read-only policy-store status adapter exists, exact lifecycle trigger evaluation exists, a minimal evidence checker exists, a guarded evidence persistence proposal bridge exists, explicit task-session evidence ingestion exists, and a minimal condition evaluator exists; broader condition vocabulary, broader evidence ingestion, UI, Skill, Plugin, and gate remain unimplemented; MCP is scoped by `JIKUO-MCP-01` but blocked until portability / security / package foundations are accepted
- rule action/evidence model contract exists, and minimal report-only evidence matching plus guarded persistence proposal and explicit task-session evidence ingestion exist; no action execution, broader checker evidence ingestion, UI, Skill, Plugin, or gate exists yet; MCP remains packaging-only, but pre-MCP trust and portability foundations are now required
- policy store and user configuration flow contract exists; read-only policy-store status adapter, exact lifecycle trigger evaluation, condition evaluation, inline evidence matching, explicit task-session evidence ingestion, no-write write-plan proposal, guarded initial policy-store write, guarded active-store append, policy decision records, proposal persistence, no-write policy evolution planning, guarded deprecation writing, guarded supersession writing, and proposal-to-apply binding exist; durable revision / rollback writers, broader evidence ingestion, UI, Skill, Plugin, and gate remain unimplemented; MCP wrapper implementation is blocked until package boundary, project-context binding, trust baseline, and resource-reference hygiene are accepted
- policy-aware agent flow proposal contract exists, and `agent_flow.py` now emits policy-aware fields backed by read-only store inspection, exact lifecycle trigger evaluation, condition evaluation, runner-produced card evidence matching, explicit task-session evidence ingestion, policy write-plan proposal, starter policy pack initialization proposal, guarded command preview, and narrow guarded apply operations; `agent_flow.py propose` still performs no durable write, no automatic evidence persistence, no UI, Skill, Plugin, or gate
- real-test-data / real-chain acceptance policy exists as a report-only approved policy fixture; it exposes missing evidence but does not yet provide a gate or automatic desktop invocation
- pre-code-change governance classification principle exists as a report-only approved policy fixture; it exposes missing classification evidence but does not yet provide a gate or automatic desktop invocation
- next review point is `JIKUO-PKG-00`, which freezes the package boundary before project-context binding, security baseline, physical extraction, or MCP implementation starts

---

## 3. Atomic Capability Registry

> **中文注释**：这是当前机括原子能力注册表。先放在 task map 里，避免新增一张独立 registry 造成维护分裂。后续如果 `agent_flow.py` / MCP 需要机器读取，再从本章节抽取 YAML registry。

Registry policy:

- this section registers composable atoms, not user operation chains
- user-facing chains are defined by `JIKUO-FLOW-02` and later invocation contracts
- helpers / CLI commands are internal atoms unless the user explicitly chooses an advanced CLI path
- every durable-write atom must declare its write effect, non-effect, and approval requirement before use

Loop composition policy:

- atom definitions remain in this registry
- loop-to-atom composition lives in the relevant loop work order, starting with `JIKUO-FLOW-02` section `Loop Composition Map`
- loop composition maps must reference `CAP-*` IDs instead of restating atom definitions
- when an atom changes, affected loop composition rows should be reviewed
- when a loop changes, required atom status, approval boundary, and no-write / guarded-write mode should be checked
- future `agent_flow.py`, MCP, plugin, or frontend traces should report both loop step id and atom IDs used

| ID | Capability | Status | Entry Point | Role In Desktop Loop | Write Effect | Approval |
|---|---|---|---|---|---|---|
| `CAP-RULE-REGISTRY-01` | Rule registry source | implemented | `docs/governance/rule_registry.yaml` | source of governance obligations | none | N/A |
| `CAP-RULE-SCHEMA-01` | Rule registry schema | archived source-project contract | no standalone schema file is currently mounted; current active rules use `docs/governance/rule_registry.yaml` plus policy contracts | none | N/A |
| `CAP-CHECKER-01` | Report-only rule checker | archived source-project atom | current standalone report-only checks are handled by `python -B -m jikuo.agent_flow propose ...` and `python -B -m jikuo.policy_store evaluate ...` | none | N/A |
| `CAP-CHECKER-JSON-01` | Structured checker output | archived source-project atom | superseded for current JIKUO work by `jikuo.agent_flow_proposal.v1` JSON proposals | none | N/A |
| `CAP-PROJECT-STATE-STATUS-01` | Project-state status inspection | implemented | `python -B -m jikuo.project_state status` | internal project enablement check | none | N/A |
| `CAP-PROJECT-STATE-INIT-DRYRUN-01` | Project-state init preview | implemented | `python -B -m jikuo.project_state init --dry-run` | preview before project-state creation | none | N/A |
| `CAP-PROJECT-STATE-WRITE-01` | Guarded project-state creation | implemented guarded | `python -B -m jikuo.project_state init --write` | approved project-local JIKUO bootstrap | create `.jikuo/project_state.yaml` | required |
| `CAP-TASK-START-DRYRUN-01` | Task-session start preview | implemented | `python -B -m jikuo.task_session start --dry-run` | internal task-start planning atom | none | N/A |
| `CAP-TASK-START-WRITE-01` | Guarded task-session creation | implemented guarded | `python -B -m jikuo.task_session start --write` | approved task-session record creation | create one `.jikuo/task_sessions/<session>.yaml` | required |
| `CAP-TASK-STATUS-01` | Task-session status read | implemented | `python -B -m jikuo.task_session status` | continue / inspect existing governed task | none | N/A |
| `CAP-TASK-INDEX-DRYRUN-01` | Task-session index preview | implemented | `python -B -m jikuo.task_session index --dry-run` | preview project-state session refs | none | N/A |
| `CAP-TASK-INDEX-REFRESH-01` | Guarded task-session index refresh | implemented guarded | `python -B -m jikuo.task_session index --refresh` | approved project-state latest-session refs update | update `.jikuo/project_state.yaml` `latest_task_session_refs` | required |
| `CAP-TASK-UPDATE-DRYRUN-01` | Task-session lifecycle preview | implemented | `python -B -m jikuo.task_session update --dry-run` | preview evidence / verification / completion / handoff changes | none | N/A |
| `CAP-TASK-EVIDENCE-APPEND-01` | Guarded evidence append | implemented guarded | `python -B -m jikuo.task_session update --append-evidence` | approved process evidence persistence | append compact evidence to explicit task session | required |
| `CAP-TASK-VERIFICATION-APPEND-01` | Guarded verification append | implemented guarded | `python -B -m jikuo.task_session update --append-verification` | approved verification evidence persistence | append compact verification to explicit task session | required |
| `CAP-TASK-COMPLETE-01` | Guarded completion update | implemented guarded | `python -B -m jikuo.task_session complete` | approved task completion / user decision record | update explicit task-session completion and decision fields | required |
| `CAP-TASK-HANDOFF-01` | Guarded handoff update | implemented guarded | `python -B -m jikuo.task_session handoff` | approved cross-agent / future-session continuation summary | update explicit task-session handoff field | required |
| `CAP-CARD-TASKSESSION-01` | Task-session card projection | implemented no-write | `python -B -m jikuo.task_session_cards ...` | internal card rendering atom for desktop chat | none | N/A |
| `CAP-SCHEMA-TASKSESSION-01` | Task-session schema contract | accepted contract | `docs/schemas/task_session.schema.md` | common shape for task-session atoms and future UI/MCP | none | N/A |
| `CAP-FLOW-DESKTOP-LOOP-01` | Desktop App Primary Operating Loop | accepted contract | `SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md` | first user operation chain; recomposes atoms | none | N/A |
| `CAP-EXEC-MOUNT-01` | Execution-order mount | accepted contract | `docs/governance/jikuo_execution_mounts.md` | required context for future JIKUO tasks | none | N/A |
| `CAP-MAIN-DOC-MOUNT-MAINTENANCE-01` | Standalone main document mount maintenance | implemented governance mount | `.jikuo/project_context.yaml`; `docs/README.md`; `docs/governance/jikuo_execution_mounts.md`; `docs/governance/jikuo_productization_task_map.md`; `POLICY-jikuo-main-doc-mount-maintenance` | keeps active document paths and slice-completion check scope visible before each JIKUO development slice closes | docs / project context only | report-only completion evidence required |
| `CAP-AGENT-INVOCATION-01` | Desktop-agent invocation contract | accepted contract | `SPRINT_050_WO-PER-JIKUO-AGENT-04_desktop_agent_invocation_contract.md` | defines explicit triggers, suggested triggers, atom invocation, chat rendering, and approval loop | none | N/A |
| `CAP-AGENT-FLOW-01` | Local deterministic proposal runner | implemented no-write | `python -B -m jikuo.agent_flow propose ...` | composes existing atoms into chat-ready Markdown / JSON proposals with loop step id and atom id trace | none | N/A |
| `CAP-DESKTOP-AGENT-INSTRUCTION-01` | Project-local desktop-agent instruction pack | implemented no-write instruction | `docs/governance/jikuo_desktop_agent_instruction_pack.md` | tells desktop agents when to call `agent_flow.py propose` and how to return cards in chat | none | N/A |
| `CAP-ARCH-SKELETON-KERNEL-01` | Skeleton / kernel boundary and backlog | implemented report-only guidance | `docs/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`; `R-013` | keeps desktop skeleton work distinct from configurable rule kernel work | none | N/A |
| `CAP-POLICY-TRIGGER-CONTRACT-01` | Configurable rule trigger policy contract | implemented contract | `docs/governance/jikuo_configurable_rule_trigger_policy.md` | defines how future user-configurable policies trigger and require actions/evidence | none | N/A |
| `CAP-POLICY-ACTION-EVIDENCE-01` | Rule action and evidence model contract | implemented contract | `docs/governance/jikuo_rule_action_evidence_model.md` | defines future action obligations, evidence requirements, produced evidence, satisfaction matching, and missing-evidence reports | none | N/A |
| `CAP-POLICY-STORE-CONFIG-01` | Policy store and user configuration flow contract | implemented contract | `docs/governance/jikuo_policy_store_configuration_flow.md` | defines future approved policy store, proposals, decisions, write plans/results, revision, deprecation, supersession, and rollback | none | N/A |
| `CAP-POLICY-AWARE-FLOW-CONTRACT-01` | Policy-aware agent flow proposal contract | implemented contract | `docs/governance/jikuo_policy_aware_agent_flow_contract.md` | defines future desktop proposal projection for policy store status, triggered policies, actions, evidence, and missing evidence | none | N/A |
| `CAP-POLICY-AWARE-FLOW-FALLBACK-01` | Policy-aware agent flow fallback | implemented no-write | `python -B -m jikuo.agent_flow propose ...` | emits `jikuo.agent_flow_proposal.v1` with explicit policy context and empty policy/action/evidence arrays until evaluator/checker slices exist | none | N/A |
| `CAP-POLICY-STORE-STATUS-01` | Read-only policy-store inspection | implemented no-write | `python -B -m jikuo.policy_store status ...` | reports whether project-approved policy store is missing, initialized, stale, conflict, or active; consumed by `agent_flow.py propose` | none | N/A |
| `CAP-POLICY-TRIGGER-EVALUATE-01` | Policy trigger evaluator MVP | implemented no-write | `python -B -m jikuo.policy_store evaluate --event ...` | reports exact lifecycle-event policy matches and required actions; consumed by `agent_flow.py propose` | none | N/A |
| `CAP-POLICY-CONDITION-EVALUATOR-01` | Policy condition evaluator MVP | implemented no-write | `python -B -m jikuo.policy_store evaluate --event ... --task-type ... --jikuo-layer ... --changed-path ...`; `python -B -m jikuo.agent_flow propose ...` | narrows lifecycle-triggered policies using explicit task metadata and path conditions before projecting required actions | none | N/A |
| `CAP-POLICY-STORE-WRITE-PROPOSE-01` | Policy write plan proposal MVP | implemented no-write proposal | `python -B -m jikuo.policy_store plan-write ...`; `python -B -m jikuo.agent_flow propose --event policy_write_plan ...` | renders policy-store write targets, proposed policy, preflight, and non-effects before any durable policy writer exists | none in propose; future guarded writer may write policy files and manifest | approval required for future writer |
| `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01` | Policy evolution plan proposal | implemented no-write proposal | `python -B -m jikuo.policy_store plan-evolution ...`; `python -B -m jikuo.agent_flow propose --event policy_evolution_plan ...` | renders a no-write refinement / deprecation / supersession plan for an existing active policy before any evolution writer exists | none | N/A |
| `CAP-POLICY-PROPOSAL-PERSIST-01` | Guarded policy proposal snapshot persistence | implemented guarded write | `python -B -m jikuo.policy_store write-policy ... --confirm-write-policy --approval-phrase ...` | persists the reviewed `jikuo.policy_write_plan.v0` snapshot so policy decisions point to an existing proposal file | `.jikuo/policies/proposals/POLICYPROPOSAL-*.yaml`; manifest `proposal_refs` | same approval phrase and technical confirmation as the guarded policy write |
| `CAP-POLICY-STORE-WRITE-01` | Guarded policy store write MVP | implemented guarded initial write | `python -B -m jikuo.policy_store write-policy ... --confirm-write-policy --approval-phrase ...` | creates the first approved report-only policy and manifest after explicit approval, then verifies read-back through status/evaluate | `.jikuo/policies/approved/<policy>.yaml`; `.jikuo/policies/manifest.yaml` | approval phrase and technical confirmation required |
| `CAP-POLICY-STORE-APPEND-01` | Active policy store append MVP | implemented guarded append | `python -B -m jikuo.policy_store write-policy ... --confirm-write-policy --approval-phrase ...` against an active store | appends one new approved report-only policy ref while preserving existing active refs and unrelated manifest text | new `.jikuo/policies/approved/<policy>.yaml`; updated `.jikuo/policies/manifest.yaml` | approval phrase and technical confirmation required |
| `CAP-POLICY-DECISION-WRITE-01` | Policy decision record MVP | implemented guarded write audit | `python -B -m jikuo.policy_store write-policy ... --confirm-write-policy --approval-phrase ...` | records the approval decision, effect, and non-effect for each successful guarded policy create / append | `.jikuo/policies/decisions/POLICYDECISION-*.yaml` | same approval phrase and technical confirmation as the guarded policy write |
| `CAP-POLICY-DEPRECATION-WRITE-01` | Guarded policy deprecation writer MVP | implemented guarded write | `python -B -m jikuo.policy_store write-evolution --operation deprecate_policy ... --confirm-write-evolution --approval-phrase ...` | lets an approved active policy stop triggering by moving it from manifest `active_policy_refs` to `deprecated_policy_refs` while preserving audit history | `.jikuo/policies/proposals/POLICYEVOPROPOSAL-*.yaml`; `.jikuo/policies/decisions/POLICYDECISION-*.yaml`; `.jikuo/policies/manifest.yaml` | approval phrase and technical confirmation required |
| `CAP-POLICY-SUPERSESSION-WRITE-01` | Guarded policy supersession writer MVP | implemented guarded write | `python -B -m jikuo.policy_store write-evolution --operation supersede_policy ... --replacement-policy-id ... --confirm-write-evolution --approval-phrase ...` | replaces an active policy with a new approved policy while moving the old policy into manifest `superseded_policy_refs` | `.jikuo/policies/approved/<replacement>.yaml`; `.jikuo/policies/proposals/POLICYEVOPROPOSAL-*.yaml`; `.jikuo/policies/decisions/POLICYDECISION-*.yaml`; `.jikuo/policies/manifest.yaml` | approval phrase and technical confirmation required |
| `CAP-POLICY-REAL-CHAIN-ACCEPTANCE-01` | Real test data and real chain acceptance policy | implemented report-only policy | `python -B -m jikuo.policy_store evaluate --event task_start --task-type work_order_delivery --jikuo-layer testing_governance --changed-path tests/policy_store_tests.py ...` | requires concrete test data / execution-chain evidence so placeholder or preview-template copying is reported as missing evidence | none | evidence required: `real_test_data_and_chain_evidence` |
| `CAP-POLICY-PRE-CODE-CLASSIFICATION-01` | Pre-code-change governance classification principle | implemented report-only policy carrier | `python -B -m jikuo.policy_store evaluate --event task_start --task-type code_change --jikuo-layer implementation_governance --changed-path src/jikuo/policy_store.py ...` | makes the "policy/governance first, code/implementation first, or mixed/unclear" decision explicit before implementation edits; this is a governance principle, not a standalone feature | none | evidence required: `governance_vs_implementation_classification_evidence` |
| `CAP-LIVE-DESKTOP-POLICY-EVAL-01` | Policy evaluation in desktop chat | implemented no-write proposal | `python -B -m jikuo.agent_flow propose ...` | makes active policy evaluation visible in the same desktop proposal card, including triggered policies, missing evidence, inline evidence status, and lightweight feedback options | none | no persistence; feedback is report-only |
| `CAP-POLICY-RUNTIME-STATUS-CARD-01` | Policy runtime status card | implemented no-write card projection | `python -B -m jikuo.agent_flow propose ...` | appends a visible `policy_runtime_status` card so active, triggered, non-triggered, required-action, and missing-evidence status is not hidden in structured fields | none | no persistence; card projection only |
| `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01` | Deterministic harness chat return | implemented chat-ready projection | `python -B -m jikuo.agent_flow propose ... --format json`; `python -B -m jikuo.agent_flow apply ... --format json` | returns `chat_ready_markdown` alongside structured proposal / apply results so desktop agents and future MCP callers can surface tool-rendered cards instead of summarizing them away | none | no persistence; same-chat surfacing required |
| `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | Out-of-band runtime visibility channel | implemented runtime projection | `src/jikuo/runtime_visibility.py`; `.jikuo/runtime/last_card.md`; `.jikuo/runtime/state_summary.json`; `.jikuo/runtime/history/*.md` | gives users a client-independent place to inspect the latest JIKUO governance card and runtime summary | local runtime projection files only | no raw chat transcript or approval phrase |
| `CAP-RUNTIME-SHOW-CLI-01` | Runtime visibility CLI | implemented read-only CLI | `jikuo show`; `jikuo show --last-card`; `python -B -m jikuo show` | lets users inspect current runtime status without relying on Agent chat behavior | none | read-only |
| `CAP-CLIENT-RUNTIME-LINK-SURFACE-01` | Client runtime link surfacing | implemented chat-ready projection | `python -B -m jikuo.agent_flow propose ...`; `jikuo show` | returns absolute Markdown links for `.jikuo/runtime/last_card.md`, `state_summary.json`, and history cards so desktop clients can expose click targets even before MCP | none | links must stay confined under `.jikuo/runtime/` |
| `CAP-TASKMAP-INSIGHT-FOLLOWUP-EVIDENCE-01` | Taskmap / insight / follow-up distinction evidence | implemented no-write evidence projection | `python -B -m jikuo.agent_flow propose --event task_start ...` | emits structured `work_routing` and `taskmap_insight_followup_distinction_evidence` so the distinction policy can be matched by the evidence checker instead of depending only on final assistant wording | none | default category is `taskmap`; explicit category can be supplied with `--work-routing-category` |
| `CAP-POLICY-FEEDBACK-PERSIST-PROPOSE-01` | Policy feedback persistence proposal bridge | implemented no-write proposal | `python -B -m jikuo.agent_flow propose --event policy_feedback_record ...` | converts explicit user feedback on a triggered policy into a guarded task-session evidence append command proposal | none in propose; future guarded command writes one task-session file | approval required for generated command |
| `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01` | Agent flow guarded task-session evidence apply | implemented guarded apply | `python -B -m jikuo.agent_flow apply --operation task_session_evidence_update ... --confirm-apply --approval-phrase ...` | lets the desktop agent apply one explicitly approved task-session evidence append without exposing users to raw helper orchestration | explicit task-session file | approval phrase and technical confirmation required |
| `CAP-POLICY-EVOLUTION-APPLY-BINDING-01` | Proposal-to-apply binding check | implemented guarded preflight | `python -B -m jikuo.agent_flow apply --operation policy_evolution_write --proposal-ref <proposal-ref> ...` | refuses policy evolution apply when the proposal ref supplied at approval time does not match the deterministic policy evolution plan that will be written | none | proposal ref, approval phrase, and technical confirmation required |
| `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01` | Agent flow guarded policy evolution apply | implemented guarded apply | `python -B -m jikuo.agent_flow apply --operation policy_evolution_write --proposal-ref <proposal-ref> ... --confirm-apply --approval-phrase ...` | lets the desktop agent apply one explicitly approved policy deprecation / supersession without switching to the raw policy-store helper | policy proposal snapshot; decision record; approved replacement policy when superseding; manifest lifecycle refs | proposal ref, approval phrase, and technical confirmation required |
| `CAP-PACKAGE-BOUNDARY-PLAN-01` | Package boundary and extraction plan | planned by `JIKUO-PKG-00` | `docs/work_orders/SPRINT_050_WO-PER-JIKUO-PKG-00_package_boundary_and_extraction_plan.md` | separates tool-owned package assets from user-project-local `.jikuo/` state before portability and MCP implementation | none | N/A |
| `CAP-PROJECT-CONTEXT-BINDING-01` | Project context binding and role resolution | contract plus no-write resolver | `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`; `src/jikuo/policy_templates.py` | lets reusable policy templates bind to project-specific document / directory roles without hardcoded paths | resolver writes none; future guarded project-context binding writer remains separate | approval required for future binding writes |
| `CAP-POLICY-TEMPLATE-PORTABILITY-01` | Policy template / binding / resolved-policy portability | draft contract | `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md` | separates reusable policy intent from local project bindings so templates can travel across projects | none | review required before template approval |
| `CAP-TRUST-PRIVACY-PROVENANCE-BASELINE-01` | Trust, privacy, provenance, namespace, principal, telemetry, and timestamp baseline | draft contract | `docs/governance/jikuo_trust_privacy_provenance_baseline.md` | declares social trust and safety fields before templates or MCP responses cross project / user boundaries | none | user approval required for future telemetry or template import |
| `CAP-PACKAGE-EXTRACTION-01` | Minimal package extraction | initial local package created | `D:\personal_project\Jikuo`; `docs/work_orders/SPRINT_050_WO-PER-JIKUO-PKG-01_minimal_package_extraction.md` | makes JIKUO installable as a tool package while keeping `.jikuo/` data inside the consuming project | package files only; user project data must not move | user review required before cleanup or MCP |
| `CAP-CONTRACT-REF-HYGIENE-01` | Resource-reference and `CONTRACT_REFS` hygiene | implemented package-safe refs | `src/jikuo/*.py`; `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-20B_resource_reference_hygiene.md` | removes source-project hardcoded command/resource references from reusable tool code by using `pkg://jikuo/...` refs and `python -B -m jikuo...` command previews | none | tests enforce no legacy tool-path command previews |
| `CAP-POLICY-TEMPLATE-EXTRACT-01` | Policy template extraction, export, and no-write import planning MVP | implemented guarded package-template export plus no-write import preview | `src/jikuo/policy_templates.py`; `src/jikuo/policy_templates/engineering_governance/*.yaml` | converts approved project-local policies into reusable package templates with source policy ID / SHA-256 provenance, redacted source identity, and binding hints, then previews target-project import without activation | package template file only when export is confirmed; import planning writes nothing | approval phrase and technical confirmation required for export |
| `CAP-PROJECT-CONTEXT-RESOLVER-01` | Project context role resolver | implemented no-write resolver | `src/jikuo/policy_templates.py plan-import` | reads `.jikuo/project_context.yaml`, resolves `role://document/*`, `role://directory/*`, `project://...`, and `pkg://jikuo/...`, and reports missing / unsafe bindings before activation | none | unsafe or unresolved required bindings block activation |
| `CAP-POLICY-TEMPLATE-IMPORT-PLAN-01` | Policy template import and resolved-policy preview | implemented no-write plan | `python -B -m jikuo.policy_templates plan-import ...` | builds `jikuo.resolved_policy.v0` and `resolved_policy_preview` from a reusable template plus project-context bindings without writing policy-store files | none | activation requires separate guarded command |
| `CAP-POLICY-TEMPLATE-ACTIVATE-01` | Guarded policy template activation | implemented guarded write | `python -B -m jikuo.policy_templates activate-template ... --confirm-activate-template --approval-phrase ...` | activates one resolved template as an approved report-only project policy after bindings are visible and safe | `.jikuo/policies/proposals/*.yaml`; `.jikuo/policies/approved/*.yaml`; `.jikuo/policies/decisions/*.yaml`; `.jikuo/policies/manifest.yaml` | approval phrase and technical confirmation required |
| `CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01` | Agent flow policy-template import card bridge | implemented no-write proposal | `python -B -m jikuo.agent_flow propose --event policy_template_import_plan --template ...` | exposes template import planning, binding status, resolved-policy refs, write targets, and non-effects as a desktop-visible card with `chat_ready_markdown` | none | activation requires separate guarded `agent_flow.py apply` command |
| `CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01` | Agent flow guarded policy-template activation apply | implemented guarded apply | `python -B -m jikuo.agent_flow apply --operation policy_template_activation --template ... --confirm-apply --approval-phrase ...` | lets the desktop agent apply one explicitly approved template activation without exposing users to the lower-level template helper | `.jikuo/policies/proposals/*.yaml`; `.jikuo/policies/approved/*.yaml`; `.jikuo/policies/decisions/*.yaml`; `.jikuo/policies/manifest.yaml` | approval phrase and technical confirmation required |
| `CAP-STARTER-POLICY-PACK-INIT-01` | Starter policy pack first-use initialization | implemented guarded bootstrap | `src/jikuo/starter_policies.py`; `src/jikuo/starter_policy_packs/engineering_governance/manifest.yaml`; `python -B -m jikuo.agent_flow propose --event initialize_jikuo ...` | initializes a new project with curated report-only policies so first use is guided rather than empty | none in propose; guarded apply may create project registry mount, `.jikuo/project_state.yaml`, and `.jikuo/policies/**` starter policy records | approval phrase and technical confirmation required |
| `CAP-AGENT-FLOW-APPLY-STARTER-POLICY-PACK-01` | Agent flow guarded starter policy pack apply | implemented guarded apply | `python -B -m jikuo.agent_flow apply --operation starter_policy_pack_init --confirm-apply --approval-phrase ...` | lets the desktop agent apply one explicitly approved starter pack initialization without exposing users to raw template extraction or starter CLI orchestration | project registry mount, `.jikuo/project_state.yaml`, `.jikuo/policies/**` starter policy records | approval phrase and technical confirmation required |
| `CAP-UNIVERSAL-INSTRUCTION-FILE-01` | Universal instruction file distribution | implemented by `JIKUO-INTG-01` | `src/jikuo/integrations/instruction_files.py`; `jikuo install`; `JIKUO.md`; `AGENTS.md`; `CLAUDE.md`; `.cursorrules`; `.continuerules` | distributes JIKUO invocation, card-display, approval, and out-of-band verification rules across clients without relying on one client hook | instruction files only | default is review-only; guarded write requires `--write`, `--confirm-install`, and `--approval-phrase` |
| `CAP-INTEGRATION-NEUTRALITY-CONTRACT-01` | Integration neutrality and integrations layout | accepted by `JIKUO-ARCH-02` | `src/jikuo/integrations/` layout planned; SEC-01 baseline updated | keeps protocol / SDK / client / IDE adapters outside the JIKUO kernel so core APIs can be used by CLI, MCP, Agent SDKs, UI, and future integrations | none | integrations may depend on core APIs; core APIs must not depend on integrations |
| `CAP-MCP-AGENT-FLOW-WRAPPER-01` | MCP wrapper around stable JIKUO atoms | planned by `JIKUO-MCP-01` | `src/jikuo/integrations/mcp/adapter.py`; `src/jikuo/integrations/mcp/server.py` planned | exposes scoped status / proposal / display-card / guarded apply operations to MCP clients while preserving the Desktop App Primary Operating Loop and out-of-band runtime visibility | only the same guarded writes as underlying atoms; card-producing tools may update `.jikuo/runtime/` | same approval phrase, technical confirmation, proposal-ref binding, and display contract as underlying atoms |
| `CAP-MCP-RUNTIME-STATUS-CARD-01` | MCP runtime status card tool | planned by `JIKUO-MCP-01` | `jikuo.get_runtime_status_card` planned | returns compact card Markdown and display directives so Agents have a narrow card-only path to show policy runtime status | local runtime projection may update | card markdown must be shown verbatim |
| `CAP-AGENTS-SDK-ADAPTER-EXPLORATION-01` | Agent SDK and agentic platform adapter exploration | accepted by `JIKUO-SDK-01` | docs-only architecture posture accepted | maps OpenAI Agents SDK, Claude Agent SDK, Google ADK, Google Antigravity, and Vercel AI SDK agents / tools / handoffs / permissions / guardrails / tracing / artifacts / MCP support to JIKUO extension points while keeping the kernel and runtime audit authority local | none | SDKs and platforms remain optional unless a later approved implementation slice changes dependency posture |
| `CAP-POLICY-EVIDENCE-CHECK-01` | Policy evidence checker MVP | implemented no-write | `python -B -m jikuo.policy_store evaluate --event ... --produced-evidence-json ...`; `--produced-evidence-type ...` | matches policy required evidence against inline produced evidence and reports missing evidence; consumed by `agent_flow.py propose` for runner-rendered cards | none | N/A |
| `CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01` | Policy evidence persistence proposal bridge | implemented no-write proposal | `python -B -m jikuo.agent_flow propose --event policy_evidence_record ...` | converts explicit policy evidence refs into a guarded task-session evidence append command proposal | none in propose; future guarded command writes one task-session file | approval required for generated command |
| `CAP-POLICY-EVIDENCE-INGEST-01` | Policy evidence ingestion MVP | implemented no-write | `python -B -m jikuo.policy_store evaluate --event ... --task-session-id ...`; `python -B -m jikuo.agent_flow propose --event policy_evidence_check --policy-event ... --session-id ...` | reads persisted task-session `policy_evidence:*` snapshots and feeds them into report-only evidence matching | none | N/A |
| `CAP-TEST-PROJECT-STATE-01` | Project-state regression tests | implemented | `python -B tests/project_state_tests.py` | verifies project-state atom safety | none | N/A |
| `CAP-TEST-TASKSESSION-01` | Task-session regression tests | implemented | `python -B tests/task_session_tests.py` | verifies task-session atom safety | none | N/A |
| `CAP-TEST-CARDS-01` | Card projection regression tests | implemented | `python -B tests/task_session_cards_tests.py` | verifies card atom safety | none | N/A |

Known missing atoms:

- `CAP-CODEX-SKILL-01`: installable Codex Skill packaging, planned after project-local instruction pack review
- `CAP-PACKAGE-EXTRACTION-01`: initial local package created and ready for review, scoped by `JIKUO-PKG-01`
- `CAP-POLICY-TEMPLATE-PORTABILITY-01`: draft contract ready for review; extraction/export, no-write import planning, and guarded resolved-policy activation exist; broader trust / marketplace portability remains future work
- `CAP-TRUST-PRIVACY-PROVENANCE-BASELINE-01`: draft contract ready for review; future implementation still planned before MCP implementation
- `CAP-CONTRACT-REF-HYGIENE-01`: implemented package-owned `pkg://` refs and module command previews; general-purpose package resource dereferencing remains future work
- `CAP-INTEGRATION-NEUTRALITY-CONTRACT-01`: integration-neutrality contract and `src/jikuo/integrations/` layout, accepted by `JIKUO-ARCH-02` before MCP implementation
- `CAP-MCP-AGENT-FLOW-WRAPPER-01`: MCP wrapper around stable `agent_flow.py` / `policy_store.py` atoms, scoped by `JIKUO-MCP-01` but blocked by pre-MCP foundations
- `CAP-UNIVERSAL-INSTRUCTION-FILE-01`: cross-client instruction file generation / sync, implemented by `JIKUO-INTG-01`
- `CAP-MCP-RUNTIME-STATUS-CARD-01`: MCP card-only runtime status tool, scoped by revised `JIKUO-MCP-01`
- `CAP-AGENTS-SDK-ADAPTER-EXPLORATION-01`: Agent SDK and agentic platform optional orchestration adapter posture, accepted by `JIKUO-SDK-01` before MCP implementation hardens
- `CAP-CLAUDE-AGENT-SDK-INTEGRATION-01`: future Claude Agent SDK plugin / hook adapter after MCP stabilizes
- `CAP-OPENAI-AGENTS-SDK-INTEGRATION-01`: future OpenAI Agents SDK adapter after MCP stabilizes
- `CAP-GOOGLE-ADK-INTEGRATION-01`: future Google ADK adapter after MCP stabilizes
- `CAP-VERCEL-AI-SDK-INTEGRATION-01`: future Vercel AI SDK adapter after MCP stabilizes
- `CAP-ANTIGRAVITY-INTEGRATION-01`: future Antigravity client-environment pack after MCP / instruction distribution stabilizes
- `CAP-CODEX-PLUGIN-01`: Codex Plugin packaging, planned after MCP / runner semantics are stable
- broader policy conditions such as mounted documents, work-order metadata, checker results, approval events, or compound predicates
- broader evidence ingestion beyond explicit task-session `policy_evidence:*` snapshots
- durable revision / rollback writers beyond guarded active-store append, decision records, proposal persistence, no-write evolution planning, guarded deprecation, and guarded supersession

---

## 4. Immediate Remaining Work

> **中文注释**：先把当前基础闭环收完，再进入产品化。不要直接跳前端。

### 4.1 `WORKTREE-05E` Acceptance

Goal:

- review and accept or revise the standalone AI agent operating kernel.

Output:

- accepted `agent_operating_kernel.md`.

Status:

- complete; standalone draft accepted by user.

Do not:

- edit `.codex/AGENTS.md` without explicit approval.

### 4.2 `WORKTREE-05E Part 2`: Kernel Promotion Proposal

Goal:

- decide whether the kernel should be promoted into `.codex/AGENTS.md`, task prompts, or remain standalone.

Output:

- promotion proposal with exact target and rollback plan.

Status:

- complete; recommendation is to keep the kernel standalone for now and defer `.codex/AGENTS.md` promotion.

Do not:

- silently merge new rules into `.codex/AGENTS.md`.

### 4.3 `WORKTREE-05F`: Gate Feasibility

Goal:

- evaluate task-stop / pre-commit gate feasibility using the report-only checker.

Output:

- feasibility document and recommended safe gate posture.

Default posture:

- suggested or report-only first
- no immediate blocking

Status:

- current active decision point.

### 4.4 `WORKTREE-05` Wrap-Up

Goal:

- archive accepted statuses, verification, and lessons.

Output:

- Sprint index/status sync
- `DEV_EXPERIENCE.md` update if this line is accepted as complete
- optional commit boundary if requested

---

## 5. JIKUO Productization Workstreams

> **中文注释**：下面是产品化任务，而不是当前 Sprint 050 hardening 的直接实现任务。

### JIKUO-UX-00: User Scenarios And Atomic Action Map

Purpose:

- define the user-facing interaction paths before PRD and UI design.

Questions:

- Which development scenarios cause a user to need governance over AI work?
- Which user statements become project rules, task rules, or one-time constraints?
- Which runtime chains should be composed from smaller atomic actions?
- Which actions belong in conversation, cards, checker reports, frontend configuration, or future gates?

Deliverables:

- target user boundary
- core user scenario inventory
- scenario-to-interaction-path map
- atomic action taxonomy
- recomposable chain map
- product surface suitability map

Dependency:

- accepted positioning that `机括` governs AI-primary software/application/system development, not end-user content creation.

### JIKUO-PRD-01: Product Definition

Purpose:

- define `机括` as a standalone product concept.

Dependency:

- `JIKUO-UX-00` user scenario and atomic action map.

Questions:

- Who configures rules?
- Who consumes reports?
- Which decisions are automated?
- Which decisions require human approval?
- What is the difference between project rules, product-quality review, and engineering governance?

Deliverables:

- PRD
- personas
- core scenarios
- non-goals
- first MVP boundary

### JIKUO-AGENT-00: Desktop-Agent-First Interaction Contract

Purpose:

- define how `机括` works inside Codex / Claude desktop APP workflows without requiring a standalone frontend or terminal-first workflow for routine confirmations.

Questions:

- What card formats should agents render in Codex / Claude desktop APP chat?
- What user approval phrases are valid enough to record?
- What project-local state must every desktop agent, auxiliary CLI bridge, and future frontend read/write?
- How should Codex and Claude hand off governance context to each other?
- Which interactions can remain in desktop-agent chat, which need auxiliary CLI/report support, and which require a frontend?

Deliverables:

- desktop chat card contract
- approval phrase contract
- auxiliary CLI bridge contract
- project-local canonical state boundary
- Codex / Claude handoff summary shape
- frontend-vs-desktop-agent surface decision rules

Dependency:

- accepted `JIKUO-PRD-01` product definition and desktop-agent-first interaction model.

### JIKUO-CORE-01: Structured Result Model

Purpose:

- define the shared structured result object before checker JSON output, desktop-agent cards, CLI bridge, or frontend views are implemented.

Questions:

- What top-level envelope should represent one governance check result?
- What fields should a triggered obligation expose to desktop cards, CLI reports, handoff summaries, and future frontend views?
- How should evidence status distinguish `ok`, `missing`, `review`, `not_applicable`, and `error`?
- How should rule severity remain separate from actual blocking enforcement?
- Which current text-checker concepts map to future structured fields?

Deliverables:

- result envelope contract
- obligation item contract
- evidence status model
- warning / blocking / review-required severity projection
- stable exit-code policy
- consumer projection rules
- current text-report to result-field mapping
- JSON output implementation plan
- default text output preservation policy
- explicit JSON opt-in boundary
- optional `--format json` checker output
- result envelope unit/integration test coverage

Dependency:

- accepted report-only checker baseline from `05D`.
- accepted `JIKUO-AGENT-00` desktop-agent-first interaction contract.

### JIKUO-CORE-02: UI-Ready Rule Registry Model

Purpose:

- define the registry view model that lets future frontend forms, desktop-agent cards, and auxiliary CLI/report surfaces explain and propose rule edits without exposing raw YAML as the product interface.

Questions:

- Which registry fields are safe to edit, which require review, which are proposal-only, and which are read-only?
- What labels, descriptions, grouping, and danger levels should future surfaces share?
- What validation message shape should UI and desktop cards render?
- How should import/export preserve checker compatibility and approval boundaries?
- How can future non-engineering scenario packages extend the model without redefining kernel semantics?

Deliverables:

- `JikuoRuleRegistryViewModelV0` contract
- field group contract
- editability category model
- field descriptor shape
- validation message shape
- import / export boundary
- rule-change proposal boundary
- scenario-package extension boundary
- `rule_registry_view_model.schema.md`
- `jikuo.registry_view.v0` schema contract

Dependency:

- `JIKUO-CORE-01` result model or parallel schema review.
- accepted `rule_registry.yaml` / `rule_registry.schema.md` baseline from `05C`.

### JIKUO-FLOW-01: Engineering Governance User Journey And Interaction Flow

Purpose:

- define how a real Codex / Claude desktop APP user uses `机括` in the engineering-governance track before task-session storage, adapters, UI, or gates are designed.

Questions:

- How does a user first enable or inspect JIKUO in an existing project?
- How does a natural-language working-method preference become a rule candidate?
- What should the agent show at task start, during evidence collection, at completion, and during handoff?
- Which interactions stay in desktop APP chat, which are auxiliary CLI/report tasks, and which belong to later frontend surfaces?
- What user-flow states must `CORE-03` model?

Deliverables:

- onboarding flow
- rule-candidate flow
- task-start governance summary flow
- in-task evidence flow
- completion and acceptance flow
- Codex / Claude desktop handoff flow
- interaction artifact inventory
- `CORE-03` state vocabulary
- desktop-agent / CLI / frontend surface decision rules

Dependency:

- accepted `JIKUO-AGENT-00`, `JIKUO-CORE-01`, and `JIKUO-CORE-02`.

Ordering note:

- this should be reviewed before `JIKUO-CORE-03`, because task-session data should reflect the actual user journey instead of being designed storage-first.

### JIKUO-SCENARIO-CHAIN-01: Governance Scenario Chain And Document Mounting Model

Purpose:

- define JIKUO's own common business scenario chains and how required reference documents are mounted onto rules, tasks, work orders, handoffs, and future task sessions.

Questions:

- Which common governance chains exist beyond the single three-phase audit example?
- How does JIKUO distinguish trigger conditions from required reference documents?
- Which document roles exist: source refs, required references, evidence carriers, output targets, index entries, handoff references, policy refs, design context, and testing context?
- Which layers can documents be mounted to: kernel, product, project, scenario package, sprint, work order, task session, operation, and handoff?
- What must `CORE-03` record so future tasks can prove which documents were required and which evidence was produced?

Deliverables:

- common scenario chain map
- atomic governance action list
- document mount object shape
- document mount role and layer definitions
- common document mount patterns
- three-phase audit modeled as one example chain
- mapping to existing registry fields
- `CORE-03` implications

Dependency:

- accepted `JIKUO-CORE-01`, `JIKUO-CORE-02`, and draft `JIKUO-FLOW-01`.

Ordering note:

- this should be reviewed before `JIKUO-CORE-03`; if accepted, it may also require a light follow-up adjustment to `JIKUO-FLOW-01`.

Follow-up correction:

- this defines scenario-chain and document-mount atoms; `JIKUO-FLOW-02` recomposes those atoms into the first desktop-app user operation chain.

### JIKUO-FLOW-02: Desktop App Primary Operating Loop

Purpose:

- define JIKUO's first user operation chain: ordinary usage starts and completes inside Codex / Claude desktop APP, while CLI/helper/frontend surfaces remain internal, auxiliary, or later.

Questions:

- How does a user start using JIKUO from a desktop APP chat message?
- Which internal atoms should the agent invoke automatically?
- What must the agent render back into the same chat?
- How does the user approve, reject, defer, or modify without switching tools?
- Which actions remain internal helper calls, advanced CLI fallback, or future frontend surfaces?

Deliverables:

- Desktop App Primary Operating Loop
- common sub-loops for project inspect, rule preference, document mount, task start, evidence review, approval, completion, handoff, and rule evolution
- atom-to-loop recomposition map
- revised downstream task order
- correction notes for helper/CLI-first drift

Dependency:

- accepted `JIKUO-UX-00`, `JIKUO-PRD-01`, `JIKUO-AGENT-00`, and accepted scenario-chain/document-mount model.
- implemented helper atoms through `JIKUO-AGENT-03`.

Status:

- accepted by user as the first user operation chain and staged execution order input.
- adapter, skill/plugin, MCP server, automatic write, frontend, gate, checker migration, registry migration, and runtime implementation remain out of scope.

### JIKUO-CORE-03: Task Session And Evidence Model

Purpose:

- represent one AI task run as a governance session.

Deliverables:

- task session object
- changed paths
- triggered rules
- evidence checks
- human approvals
- acceptance records
- audit trail
- scenario chain snapshot
- document mount snapshot
- handoff and supersession state

Dependency:

- `05A` evidence model and `05D` checker behavior.
- accepted `JIKUO-FLOW-01` user journey and interaction flow.
- accepted `JIKUO-SCENARIO-CHAIN-01` scenario-chain and document-mounting model.

Status:

- Part 1 accepted by user.
- Part 2 created `docs/schemas/task_session.schema.md`; accepted by user for downstream projection planning.

### JIKUO-UI-01: Rule Configuration Console

Purpose:

- allow users to configure rules visually instead of editing YAML.

MVP surfaces:

- rule list
- trigger path editor
- evidence requirement editor
- enforcement phase selector
- exemption editor
- source reference viewer

Dependency:

- `JIKUO-CORE-02`.

### JIKUO-AGENT-01: Desktop Agent Card Projection Contract

Purpose:

- define how JIKUO result, registry-view, document-mount, and task-session objects should be projected as compact Codex / Claude desktop APP chat cards before renderer or adapter implementation.

Questions:

- Which card families are needed for onboarding, rule candidates, document mounts, task start, evidence, completion, rule evolution, and handoff?
- What fields must every card show to keep approval targets and persistence effects unambiguous?
- How should `missing`, `review`, `not_applicable`, and `error` be displayed?
- How should exact user phrases be captured without requiring fixed command phrases?
- Which information remains in desktop chat, which goes to auxiliary CLI reports, and which belongs to future frontend surfaces?

Deliverables:

- shared card envelope
- card family inventory
- required fields for each card family
- document-mount and evidence display rules
- approval phrase capture rules
- surface fallback rules

Dependency:

- accepted `JIKUO-AGENT-00`, `JIKUO-CORE-01`, `JIKUO-CORE-02`, and `JIKUO-CORE-03` Part 2.

Status:

- accepted by user for downstream project-local state / sidecar storage planning.

### JIKUO-CORE-04: Project Local State And Sidecar Storage Contract

Purpose:

- define where durable project-local JIKUO governance state should live, what object families may be persisted later, and how Codex / Claude desktop APP sessions can share continuity without relying on chat memory.

Questions:

- What remains canonical in accepted work orders, schema docs, registry files, and checker output?
- What may future sidecar records store as task evidence, decisions, handoffs, proposals, and projections?
- How should `.jikuo/` be treated as a future layout proposal without creating it in this slice?
- What write-safety, supersession, conflict, privacy, and compatibility rules are required before implementation?
- How should desktop-agent cards read from durable records while remaining projections only?

Deliverables:

- project-local state source hierarchy
- future sidecar layout proposal
- durable governance record envelope
- object family inventory
- write/read policy
- desktop APP continuity rules
- privacy and compatibility boundaries

Dependency:

- accepted `JIKUO-CORE-03` task-session schema and accepted `JIKUO-AGENT-01` desktop-agent card projection contract.

Status:

- accepted by user for downstream report-only sidecar bootstrap planning.

### JIKUO-SIDECAR-01: Report-Only Project State Bootstrap

Purpose:

- define the first safe implementation slice for project-local JIKUO state by reporting whether the future sidecar state is missing, initialized, stale, conflicted, or unsafe before any durable writes are allowed.

Questions:

- How should a helper discover the project root and future sidecar path?
- What should a bootstrap report contain before `.jikuo/` exists?
- How can `status` and `init --dry-run` prove that no files were created or modified?
- Which command shape is useful to Codex / Claude desktop agents without turning CLI into the primary UX?
- What tests are required before later write mode is considered?

Deliverables:

- report-only bootstrap object
- helper command proposal
- no-write policy
- desktop-agent summary shape
- implementation test plan

Dependency:

- accepted `JIKUO-CORE-04` project-local state and sidecar storage contract.

Status:

- accepted by user for report-only implementation.
- `src/jikuo/project_state.py` implemented with `status` and `init --dry-run`.
- accepted by user for downstream write-mode proposal planning.
- `init --write`, root `.jikuo/` creation, storage adapter, renderer, frontend, gate, and runtime changes remain out of scope.

### JIKUO-SIDECAR-02: Project State Write Mode Proposal

Purpose:

- define the safety contract for future initial creation of `.jikuo/project_state.yaml`, including explicit user approval, technical confirmation, no-overwrite behavior, atomic write, cleanup, post-write verification, and desktop-agent projection.

Questions:

- What user approval evidence is required before the first durable JIKUO project-state write?
- Which technical confirmation flag prevents accidental command invocation?
- When should write mode refuse to proceed?
- How should initial write avoid overwrite and handle cleanup?
- What structured result should future write mode emit?
- What tests must prove that ambiguous or unsafe states do not write?

Deliverables:

- approval contract
- write plan object
- write result object
- preflight refusal matrix
- atomic write / rollback contract
- desktop-agent projection
- future implementation test plan

Dependency:

- accepted `JIKUO-SIDECAR-01` report-only project-state bootstrap helper.

Status:

- accepted by user for initial write-mode implementation.
- `src/jikuo/project_state.py init --write --confirm-create-project-state` implemented.
- `.jikuo/project_state.yaml` created for initial project-local JIKUO state.
- repeated write is rejected and does not overwrite existing project state.
- accepted by user for downstream task-session persistence proposal planning.
- task-session persistence, audit-event persistence, rule-proposal persistence, storage adapter, renderer, frontend, gate, and runtime changes remain out of scope.

### JIKUO-TASKSESSION-01: Task Session Sidecar Persistence Proposal

Purpose:

- define how one governed AI task should be persisted as a compact project-local task session without turning JIKUO sidecar into raw chat logs.

Questions:

- Where should future task-session files live?
- Which fields from `JikuoTaskSessionV0` are required for the first persisted record?
- What may be captured, and what must not be captured?
- How should user decisions preserve exact phrases with target/effect?
- When may `.jikuo/project_state.yaml` index `latest_task_session_refs` be updated?
- What refusal and supersession rules prevent stale or ambiguous process state?

Deliverables:

- task-session sidecar root and naming rules
- task-session sidecar record shape
- capture/minimal-retention policy
- write/update policy
- project-state index boundary
- desktop-agent projection expectations
- refusal and supersession rules
- future implementation test plan

Dependency:

- accepted initialized project state from `JIKUO-SIDECAR-02`.

Status:

- accepted by user for dry-run helper implementation.
- `src/jikuo/task_session.py start --dry-run` implemented.
- `src/jikuo/task_session.py status` implemented.
- accepted by user for downstream write-mode proposal planning.
- `.jikuo/task_sessions/` creation, task-session file writes, project-state index updates, desktop adapter, frontend, gate, and runtime changes remain out of scope.

### JIKUO-TASKSESSION-02: Task Session Write Mode Proposal

Purpose:

- define when a dry-run task-session plan may become one durable, compact, project-local task-session sidecar record.

Questions:

- What approval evidence and technical confirmation are required before writing?
- Which preflight checks must refuse unsafe writes?
- How can the first write create a task-session file without also coupling project-state index updates?
- What desktop-agent projection makes the durable effect clear to a Codex / Claude desktop APP user?
- Which tests prove write mode cannot become raw chat logging or accidental overwrite?

Deliverables:

- write-mode approval contract
- `JikuoTaskSessionWritePlanV0`
- `JikuoTaskSessionWriteResultV0`
- preflight refusal matrix
- task-session file creation / no-overwrite policy
- project-state index update boundary
- future implementation test plan

Dependency:

- accepted `JIKUO-TASKSESSION-01` dry-run task-session helper.

Status:

- accepted by user for guarded write-mode implementation.
- `src/jikuo/task_session.py start --write` implemented.
- `--confirm-create-task-session` and `--approval-phrase "<exact user phrase as spoken>"` are required for write mode.
- write mode creates exactly one task-session YAML file after preflight passes.
- write mode refuses missing confirmation / approval, project-root mismatch, and session-id collision.
- `src/jikuo/task_session.py status` can read persisted task-session summaries.
- root project `.jikuo/task_sessions/` has not been created for the current Codex task.
- accepted by user for downstream index proposal planning.
- `.jikuo/project_state.yaml` index update remains out of scope.

### JIKUO-TASKSESSION-03: Project-State Task-Session Index Update

Purpose:

- define how `.jikuo/project_state.yaml` should discover, index, refresh, and repair task-session refs after task-session files exist.

Questions:

- Should `latest_task_session_refs` be updated during `start --write` or by a separate `index --refresh` action?
- How should unknown project-state fields be preserved?
- How should JIKUO recover when a session file exists but the index is stale?
- How many recent task-session refs should be retained?
- What refusal / backup behavior prevents project-state corruption?

Deliverables:

- index update contract
- refresh / repair policy
- no-overwrite / preserve-unknown-fields policy
- failure and rollback matrix
- tests for stale index, missing file, duplicate refs, and unknown-field preservation

Dependency:

- accepted `JIKUO-TASKSESSION-02` guarded task-session write mode.

Status:

- accepted by user for index dry-run / guarded refresh implementation.
- `src/jikuo/task_session.py index --dry-run` implemented.
- `src/jikuo/task_session.py index --refresh` implemented.
- `--confirm-update-project-state-index` and `--approval-phrase "<exact user phrase as spoken>"` are required for refresh mode.
- refresh updates only `.jikuo/project_state.yaml` `latest_task_session_refs`.
- refresh does not create task-session files.
- duplicate session ids refuse.
- root project `.jikuo/project_state.yaml` index has not been updated during verification.
- root project `.jikuo/task_sessions/` has not been created.
- accepted by user for downstream lifecycle / evidence / completion / handoff proposal planning.

### JIKUO-TASKSESSION-04: Task-Session Lifecycle Update, Evidence Append, Completion, And Handoff Boundary

Purpose:

- define how an existing task-session record can move beyond start/index into in-progress evidence, verification, user acceptance, completion, and handoff state.

Questions:

- Which task-session fields may be appended after session creation?
- Which updates require explicit user approval?
- How should evidence snapshots, verification results, and user decisions be appended without raw chat logging?
- How should completion and handoff state be represented for Codex / Claude desktop continuity?
- What refusal rules prevent stale or wrong-session updates?

Deliverables:

- task-session update command contract
- evidence append contract
- completion / acceptance contract
- handoff summary contract
- stale-session / wrong-session refusal matrix
- tests for append-only updates and no raw transcript capture

Dependency:

- accepted `JIKUO-TASKSESSION-03` project-state task-session index refresh.

Status:

- accepted by user for lifecycle update dry-run / guarded append implementation.
- `src/jikuo/task_session.py update --dry-run` implemented.
- `src/jikuo/task_session.py update --append-evidence` implemented.
- `src/jikuo/task_session.py update --append-verification` implemented.
- `src/jikuo/task_session.py complete` implemented.
- `src/jikuo/task_session.py handoff` implemented.
- all lifecycle write actions require explicit `--session-id`.
- guarded lifecycle writes require technical confirmation and approval phrase.
- accepted completion requires explicit user decision evidence.
- duplicate session matches and raw chat transcript markers refuse.
- root project `.jikuo/task_sessions/` has not been created.
- root project `.jikuo/project_state.yaml` index has not been updated during verification.
- accepted by user for downstream `JIKUO-AGENT-02` desktop-agent task-session workflow card planning.

### JIKUO-UI-02: Run Control Console

Purpose:

- let users see what a task triggered and what evidence is missing.

MVP surfaces:

- changed / added path input
- git pathspec input
- triggered rule list
- `OK` / `MISSING` / `REVIEW` / `GIT WARN`
- suggested next action

Dependency:

- `JIKUO-CORE-01` and `JIKUO-CORE-03`.

### JIKUO-AUDIT-01: Evolution Dashboard

Purpose:

- govern the governance system itself.

MVP surfaces:

- high-frequency rules
- frequent missing evidence
- rules with many `REVIEW` outcomes
- report-only rules eligible for promotion
- blocking rules that may be too heavy
- false-positive notes

Dependency:

- accumulated task session records.

### JIKUO-GATE-01: Gate Adapters

Purpose:

- connect stable checks to task-stop, pre-commit, pre-push, or CI.

Default rule:

- no rule moves beyond report-only without explicit approval and rollback plan.

Dependency:

- `WORKTREE-05F` feasibility and product-level approval.

### JIKUO-AGENT-02: Desktop-Agent Task-Session Workflow Cards And Command Composition

Purpose:

- define how accepted task-session commands become readable, approvable Codex / Claude desktop APP workflow cards before renderer or adapter implementation.

Questions:

- Which task-session actions need desktop workflow cards?
- What must a card show before a durable write is approved?
- How should command previews preserve target, effect, non-effect, and exact phrase capture?
- How does the agent compose dry-run, guarded write, index refresh, evidence append, verification append, completion, and handoff commands without making CLI the primary UX?
- How do refusal cards prevent stale, ambiguous, or unsafe session updates?

Deliverables:

- desktop workflow card envelope
- command proposal object
- approval capture object
- task start / write / index / evidence / verification / completion / handoff / refusal card families
- command-composition rules
- desktop continuity rules
- testing-governance declaration and no-write smoke expectation

Dependency:

- accepted `JIKUO-AGENT-01` desktop-agent card projection contract.
- accepted `JIKUO-TASKSESSION-02` / `JIKUO-TASKSESSION-03` / `JIKUO-TASKSESSION-04` command contracts and implementation behavior.

Status:

- accepted by user for downstream minimal card projection helper implementation.
- no renderer, Codex/Claude adapter, automatic task-session write, frontend, gate, checker migration, registry migration, or runtime implementation is approved in this slice.

### JIKUO-AGENT-03: Minimal Task-Session Card Projection Helper

Purpose:

- implement the smallest no-write helper that projects task-session plans/results into Markdown or JSON cards for Codex / Claude desktop APP review.

Questions:

- Does the rendered card make the approval target understandable?
- Does the rendered card make write effect and non-effect concrete?
- Does Markdown output feel usable inside desktop APP chat?
- Does JSON output preserve a future adapter/frontend path?
- Does the helper stay no-write during verification?

Deliverables:

- `src/jikuo/task_session_cards.py`
- `tests/task_session_cards_tests.py`
- start-preview card
- index-preview card
- update-preview card
- render-json path
- concrete user validation checklist

Dependency:

- accepted `JIKUO-AGENT-02` desktop-agent task-session workflow card contract.
- existing `src/jikuo/task_session.py` structured plan/result builders.

Status:

- implemented and ready for user review.
- generated cards are projections only.
- product correction: this helper is an internal atom, not the user-facing operating loop.
- no desktop adapter, automatic write, frontend, gate, checker migration, registry migration, or runtime implementation is approved in this slice.

### JIKUO-AGENT-04: Desktop Agent Invocation Contract

Purpose:

- define how a Codex / Claude desktop APP user explicitly triggers JIKUO, how the agent may suggest JIKUO, how internal atoms are called, how cards / summaries return to the same chat, and how approval / rejection / modification loops work before any deterministic runner is implemented.

Questions:

- Which low-cost trigger shortcuts should ordinary desktop APP users learn?
- When may the agent suggest JIKUO without making it feel like hidden automation?
- Which no-write atoms may the agent call to render a card or summary?
- Which durable-write atoms always require an explicit card and user approval?
- How should cards, refusals, ambiguity, and handoff be rendered in the same chat?
- What must `agent_flow.py` implement later, and what must it not become?

Deliverables:

- desktop invocation principles
- explicit trigger shortcut family
- agent-suggested trigger conditions
- trigger decision object
- invocation scenario families
- internal atom invocation rules
- chat rendering rules
- approval / rejection / modification loop
- refusal and ambiguity handling
- downstream `agent_flow.py` requirements

Dependency:

- accepted `JIKUO-FLOW-02` Desktop App Primary Operating Loop.
- implemented `JIKUO-AGENT-03` no-write card projection atom.
- accepted task-session and project-state sidecar contracts.

Status:

- accepted by user for downstream `agent_flow.py` implementation.
- no `agent_flow.py`, Skill, MCP server, Codex Plugin, frontend, automatic durable write, gate, checker migration, registry migration, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

### JIKUO-AGENT-05: Local Deterministic Agent Flow Proposal Runner

Purpose:

- implement the first local deterministic runner that a Codex / Claude desktop APP agent can call internally to compose existing no-write atoms into one chat-ready JIKUO proposal.

Questions:

- Can one local entry point produce a useful desktop chat proposal without requiring the user to run helper commands?
- Can the runner preserve loop step ids and atom ids for future trace / MCP / frontend use?
- Can proposal mode stay strictly no-write while still surfacing approval boundaries?
- Which events are enough for the first MVP: status, task start, continuation, index, evidence, verification, completion, handoff, and audit placeholder?

Deliverables:

- `src/jikuo/agent_flow.py`
- `tests/agent_flow_tests.py`
- no-write `propose` command
- Markdown proposal output
- JSON proposal output
- trigger decision object
- loop step id / atom id trace
- refusal cards for missing title / session id / unsupported events

Dependency:

- accepted `JIKUO-AGENT-04` desktop invocation contract.
- accepted `JIKUO-FLOW-02` Loop Composition Map.
- implemented project-state, task-session, and task-session card atoms.

Status:

- accepted as no-write runner for downstream lightweight desktop-agent instruction-pack planning.
- guarded `apply`, Codex Skill / Agent instruction, MCP server, Codex Plugin, frontend, automatic durable write, gate, checker migration, registry migration, `.codex/AGENTS.md` edit, and runtime implementation remain out of scope.

### JIKUO-AGENT-06: Lightweight Desktop Agent Instruction Pack

Purpose:

- create a compact project-local instruction pack that tells Codex / Claude desktop APP agents when to call `agent_flow.py propose`, how to return the proposal in chat, and where the no-write / guarded-write boundary remains.

Questions:

- Can desktop invocation become less dependent on long conversation memory without installing a global Skill yet?
- Can the instruction pack preserve desktop-app-primary operation while keeping CLI as an internal helper path?
- Can it prepare for future Codex Skill / MCP packaging without approving either one?

Deliverables:

- `docs/governance/jikuo_desktop_agent_instruction_pack.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-06_lightweight_desktop_agent_instruction_pack.md`
- task-map / execution-mount / Sprint-index updates

Dependency:

- accepted `JIKUO-AGENT-04` desktop invocation contract.
- accepted no-write `JIKUO-AGENT-05` local proposal runner.
- accepted `JIKUO-FLOW-02` Desktop App Primary Operating Loop.

Status:

- implemented and ready for user review.
- installable Codex Skill, MCP server, Codex Plugin, frontend, guarded `agent_flow.py apply`, automatic durable write, gate, checker migration, registry migration, `.codex/AGENTS.md` edit, and runtime implementation remain out of scope.

### JIKUO-ARCH-01: Skeleton / Kernel Boundary And Kernel Backlog

Purpose:

- keep current desktop operating skeleton work distinct from the future configurable rule kernel, while preserving explicit compatibility hooks.

Questions:

- Can future JIKUO tasks declare which layer they are changing before implementation?
- Can skeleton work preserve room for future policy refs, triggered rules, required actions, and missing evidence?
- Can the deferred configurable-rule-kernel backlog stay visible without being accidentally implemented inside skeleton / packaging work?

Deliverables:

- `docs/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-01_skeleton_kernel_boundary_and_kernel_backlog.md`
- `R-013` report-only checker rule
- task-map / execution-mount / Sprint-index updates

Dependency:

- user clarification that JIKUO's original problem is probabilistic AGENTS-rule execution.
- implemented desktop operating skeleton artifacts through `JIKUO-AGENT-06`.

Status:

- implemented and ready for user review.
- configurable rule kernel, policy-aware `agent_flow.py`, installable Skill, MCP server, Codex Plugin, frontend, guarded `agent_flow.py apply`, automatic durable write, gate, `.codex/AGENTS.md` edit, and runtime implementation remain out of scope.

### JIKUO-CORE-05: Configurable Rule Trigger And Execution Policy

Purpose:

- define how user preferences, required reference files, work-order contracts, design docs, AGENTS-style rules, lifecycle events, changed paths, required actions, and required evidence become a future configurable policy contract.

Questions:

- How does a natural-language working-method preference become a policy candidate instead of remaining probabilistic instruction prose?
- How are required reference files represented as document mounts rather than vague context?
- Which signals can deterministically trigger a policy?
- Which required actions and evidence should the future rule kernel expose before policy execution is implemented?
- How does the contract stay process-governance-kernel compatible instead of engineering-only?

Deliverables:

- `docs/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-05_configurable_rule_trigger_and_execution_policy.md`
- task-map / execution-mount / Sprint-index updates

Dependency:

- accepted `JIKUO-ARCH-01` skeleton / kernel boundary.
- existing desktop operating skeleton artifacts through `JIKUO-AGENT-06`.

Status:

- implemented and ready for user review.
- no policy store, policy-aware `agent_flow.py`, action/evidence execution model, policy evidence checker, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

### JIKUO-CORE-06: Rule Action And Evidence Model

Purpose:

- define how triggered policies produce concrete actions, evidence requirements, produced evidence, satisfaction checks, and missing-evidence reports.

Questions:

- What is the object shape for an action that a triggered policy requires?
- What evidence requirement proves an action has been handled?
- How does produced evidence refer back to policy, trigger, action, and requirement ids?
- How are `ok`, `review_required`, `missing`, `not_applicable`, `failed`, and `error` distinguished?
- How does missing evidence become visible without becoming a blocking gate?

Deliverables:

- `docs/governance/jikuo_rule_action_evidence_model.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-06_rule_action_and_evidence_model.md`
- task-map / execution-mount / Sprint-index updates

Dependency:

- accepted `JIKUO-CORE-05` configurable rule trigger policy.

Status:

- implemented and ready for user review.
- no action execution, evidence persistence, policy-aware `agent_flow.py`, policy evidence checker, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

### JIKUO-CORE-07: Policy Store And User Configuration Flow

Purpose:

- define where future approved project-local policies should live and how users approve, revise, reject, defer, deprecate, supersede, or roll them back without editing raw YAML as the primary path.

Questions:

- Where do approved user policies live after acceptance?
- How are pending proposals kept separate from active policies?
- What must a desktop APP approval card show before a durable policy write?
- How are revision, deprecation, supersession, and rollback represented?
- How does the policy store relate to current `rule_registry.yaml` and future task-session policy snapshots?

Deliverables:

- `docs/governance/jikuo_policy_store_configuration_flow.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-07_policy_store_and_user_configuration_flow.md`
- task-map / execution-mount / Sprint-index updates

Dependency:

- accepted `JIKUO-CORE-04` project-local state and sidecar storage contract.
- accepted `JIKUO-CORE-05` configurable rule trigger policy.
- accepted `JIKUO-CORE-06` rule action and evidence model.

Status:

- implemented and ready for user review.
- no `.jikuo/policies/` creation, policy proposal persistence, approved policy persistence, policy store adapter, policy-aware `agent_flow.py`, policy evidence checker, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

### JIKUO-AGENT-07: Policy-Aware Agent Flow Proposal

Purpose:

- define how future `agent_flow.py propose` should project policy store status, triggered policies, required actions, evidence status, and missing evidence into Codex / Claude desktop APP chat.

Questions:

- How does a proposal card show whether policy-aware evaluation is available?
- How are triggered policies, required actions, and evidence status projected without copying full policy store records?
- How does the runner avoid claiming "no policies triggered" when policy infrastructure is unavailable?
- What trace fields must future runner / MCP / frontend outputs preserve?
- Which implementation work remains deferred after the contract?

Deliverables:

- `docs/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-07_policy_aware_agent_flow_proposal.md`
- task-map / execution-mount / Sprint-index updates

Dependency:

- accepted `JIKUO-AGENT-05` no-write runner contract.
- accepted `JIKUO-CORE-05`, `JIKUO-CORE-06`, and `JIKUO-CORE-07`.

Status:

- implemented and ready for user review.
- no `agent_flow.py` code change, policy store adapter, trigger evaluator, evidence checker, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

### JIKUO-CORE-08: Read-Only Policy Store Inspection

Purpose:

- implement the first read-only policy-store status adapter so tools can see whether project-approved policies are missing, initialized, stale, conflict, or active.

Questions:

- Can the adapter inspect `.jikuo/policies/manifest.yaml` without creating policy storage?
- Can active approved policy refs be summarized compactly without copying full policy bodies into proposal cards?
- Can stale and conflict states be visible before policy evaluation exists?
- Can `agent_flow.py propose` consume store status while keeping `policy_eval_status: not_evaluated`?

Deliverables:

- `src/jikuo/policy_store.py`
- `tests/policy_store_tests.py`
- policy-store fixtures
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-08_read_only_policy_store_inspection.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- accepted `JIKUO-CORE-07` policy store and user configuration flow.
- accepted `JIKUO-AGENT-07` policy-aware proposal contract.
- implemented `JIKUO-AGENT-08` fallback proposal fields.

Status:

- implemented and ready for user review.
- no policy writes, trigger evaluation, action execution, evidence checking, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

### JIKUO-CORE-09: Policy Trigger Evaluator MVP

Purpose:

- implement the first report-only policy trigger evaluator so active approved policies can match exact desktop lifecycle events and project required actions into proposal cards.

Questions:

- Can a project-local active policy trigger on `task_start` without relying on Agent memory or keyword confidence?
- Can the evaluator stay honest by reporting exact event matching only, not semantic intent inference?
- Can `agent_flow.py propose` show triggered policies and required actions while still refusing action execution, evidence satisfaction, writes, and gates?
- Can this run without creating root `.jikuo/policies/` or `.jikuo/task_sessions/` directories?

Deliverables:

- `src/jikuo/policy_store.py evaluate`
- `CAP-POLICY-TRIGGER-EVALUATE-01` atom trace in `agent_flow.py propose`
- policy trigger evaluator unit / workflow tests
- active-policy fixture with a `task_start` lifecycle trigger
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-09_policy_trigger_evaluator_mvp.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-08` read-only policy store inspection.
- accepted `JIKUO-CORE-05` trigger semantics and `JIKUO-CORE-06` action/evidence vocabulary.
- implemented `JIKUO-AGENT-08` policy-aware proposal envelope.

Status:

- implemented and ready for user review.
- exact lifecycle-event matching and required-action projection exist.
- no condition evaluator, evidence checker, policy write adapter, action execution, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

### JIKUO-CORE-10: Policy Evidence Checker MVP

Purpose:

- implement the first report-only policy evidence checker so triggered policy `required_evidence` can be matched against inline produced evidence and projected into desktop proposal cards.

Questions:

- Can missing required evidence become visible without blocking delivery?
- Can runner-produced `card_rendered` evidence satisfy a `render_pre_task_review` action without durable writes?
- Can `agent_flow.py propose` show evidence status while still refusing action execution, evidence persistence, policy writes, and gates?
- Can this run without creating root `.jikuo/policies/` or `.jikuo/task_sessions/` directories?

Deliverables:

- `policy_evidence_check_status`
- `evidence_status` projection
- `missing_evidence_reports` projection
- `CAP-POLICY-EVIDENCE-CHECK-01` atom trace in `agent_flow.py propose`
- inline `--produced-evidence-json` support for `policy_store.py evaluate`
- tests for missing and satisfied evidence
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-10_policy_evidence_checker_mvp.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-09` exact lifecycle trigger evaluator.
- accepted `JIKUO-CORE-06` action/evidence model.
- implemented `JIKUO-AGENT-08` policy-aware proposal envelope.

Status:

- implemented and ready for user review.
- report-only evidence matching exists for inline produced evidence and task-start runner-rendered card evidence.
- no evidence persistence, condition evaluator, policy write adapter, action execution, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

### JIKUO-CORE-11: Policy Evidence Persistence Proposal Bridge

Purpose:

- bridge checked policy evidence into the existing guarded task-session evidence append workflow without making `agent_flow.py propose` write anything.

Questions:

- Can a user persist a reviewed policy evidence item without manually composing a long CLI command?
- Can the proposal require explicit session, policy, action, requirement, evidence kind, and evidence ref?
- Can the generated command preserve the existing `--confirm-update-task-session` and `--approval-phrase` write boundary?
- Can this run without modifying the target task-session file?

Deliverables:

- `policy_evidence_record` event alias
- `--policy-ref`, `--action-ref`, `--requirement-ref` args in `agent_flow.py propose`
- guarded `task_session.py update --append-evidence` command proposal
- `CAP-POLICY-EVIDENCE-PERSIST-PROPOSE-01` atom trace
- fixture with an existing task session for no-write proposal testing
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-11_policy_evidence_persistence_proposal_bridge.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-10` policy evidence checker MVP.
- implemented TASKSESSION-04 guarded evidence append.
- accepted FLOW-02 Desktop App Primary Operating Loop.

Status:

- implemented and ready for user review.
- policy evidence persistence proposal exists, but persistence still requires explicit guarded command execution after user approval.
- no evidence ingestion, condition evaluator, policy write adapter, action execution, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

---

### JIKUO-CORE-12: Policy Evidence Ingestion MVP

Purpose:

- read compact persisted policy evidence from an explicit task session back into report-only evidence evaluation without relying on chat memory.

Questions:

- Can a later policy check see evidence that was already approved and persisted to a task session?
- Can evidence ingestion stay explicit-session and no-write?
- Can persisted evidence satisfy the same required-evidence contract used by inline evidence?
- Can the desktop proposal show the evidence source refs without copying raw session bodies?

Deliverables:

- `--task-session-id` support in `policy_store.py evaluate`
- `policy_evidence_check` event alias in `agent_flow.py propose`
- `--policy-event` support for checking a target lifecycle event through the desktop runner
- persisted task-session `policy_evidence:*` ingestion
- `CAP-POLICY-EVIDENCE-INGEST-01` atom trace
- fixture with active policy store plus persisted task-session evidence
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-12_policy_evidence_ingestion_mvp.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-10` policy evidence checker MVP.
- implemented `JIKUO-CORE-11` policy evidence persistence proposal bridge.
- implemented TASKSESSION-04 guarded evidence append.
- accepted FLOW-02 Desktop App Primary Operating Loop.

Status:

- implemented and ready for user review.
- persisted policy evidence ingestion is explicit-session and report-only.
- no condition evaluator, policy write adapter, broader checker evidence ingestion, action execution, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

---

### JIKUO-CORE-13: Policy Condition Evaluator MVP

Purpose:

- evaluate a small deterministic subset of policy `conditions` before projecting required actions.

Questions:

- Can lifecycle-triggered policies be narrowed by explicit task metadata?
- Can path-based conditions use supplied changed / added path lists without scanning the filesystem?
- Can missing condition context produce `review_required` instead of silent success?
- Can condition reports be visible in the desktop proposal?

Deliverables:

- `--task-type`, `--jikuo-layer`, `--changed-path`, and `--added-path` support in `policy_store.py evaluate`
- matching condition metadata support in `agent_flow.py propose`
- first condition types: `task_type_is`, `jikuo_layer_is`, `changed_path_matches`, `added_path_matches`
- `condition_reports` in policy-store and agent-flow outputs
- `CAP-POLICY-CONDITION-EVALUATOR-01` atom trace
- fixture with an active conditioned policy
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-13_policy_condition_evaluator_mvp.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-09` exact lifecycle trigger evaluator.
- implemented `JIKUO-CORE-10` policy evidence checker MVP.
- implemented `JIKUO-CORE-12` policy evidence ingestion MVP.
- accepted FLOW-02 Desktop App Primary Operating Loop.

Status:

- implemented and ready for user review.
- condition evaluation is explicit-input and report-only.
- no policy write adapter, broader condition vocabulary, broader checker evidence ingestion, action execution, Skill, MCP, Plugin, frontend, guarded `apply`, gate, `.codex/AGENTS.md` edit, or runtime implementation is approved in this slice.

---

### JIKUO-CORE-14: Policy Write Plan Proposal MVP

Purpose:

- render a no-write `jikuo.policy_write_plan.v0` before any durable policy writer exists.

Questions:

- Does the card make policy target, effect, non-effect, and approval boundary clear enough for a desktop APP user?
- Is collision refusal honest enough before implementing revision / supersession?

Deliverables:

- `policy_store.py plan-write`
- `agent_flow.py propose --event policy_write_plan`
- `CAP-POLICY-STORE-WRITE-PROPOSE-01` atom trace
- target collision refusal without write
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-14_policy_write_plan_proposal_mvp.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-07` policy store and user configuration contract.
- implemented `JIKUO-CORE-08` read-only policy-store inspection.
- implemented `JIKUO-CORE-13` condition evaluator MVP.

Status:

- implemented and ready for user review.
- policy write plan is proposal-only and no-write.
- no durable policy writer, proposal persistence, guarded `apply`, Skill, MCP, Plugin, frontend, or gate is approved in this slice.

---

### JIKUO-CORE-15: Guarded Policy Store Write MVP

Purpose:

- create the first approved report-only policy store only after explicit command confirmation and approval evidence.

Questions:

- Is the guarded writer boundary clear enough for desktop APP use?
- Is the initial-writer limitation acceptable before active-store append / revision / supersession?

Deliverables:

- `policy_store.py write-policy`
- `jikuo.policy_write_result.v0`
- `--confirm-write-policy`
- `--approval-phrase`
- collision refusal
- post-write status / evaluate read-back verification
- guarded command preview in `agent_flow.py propose --event policy_write_plan`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-15_guarded_policy_store_write_mvp.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-07` policy store and user configuration contract.
- implemented `JIKUO-CORE-14` policy write plan proposal MVP.

Status:

- implemented and ready for user review.
- writer is guarded and intended for initial / empty policy-store cases.
- no active-store append, revision, supersession, rollback, automatic desktop apply, Skill, MCP, Plugin, frontend, or gate is approved in this slice.

---

### JIKUO-CORE-16: Active Policy Store Append MVP

Purpose:

- append a second approved report-only policy to an already active policy store after explicit command confirmation and approval evidence.

Questions:

- Is append clearly separated from revision / supersession?
- Does manifest append preserve existing active refs and unrelated manifest text well enough for this MVP?

Deliverables:

- active-store support in `policy_store.py write-policy`
- `append_policy` operation classification
- `CAP-POLICY-STORE-APPEND-01`
- manifest active-ref insertion
- duplicate policy refusal
- status / evaluate read-back for two active policies
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-16_active_policy_store_append_mvp.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-15` guarded policy store write MVP.

Status:

- implemented and ready for user review.
- append is guarded and distinct from revision / supersession.
- no policy revision, supersession, rollback, proposal persistence, automatic desktop apply, Skill, MCP, Plugin, frontend, or gate is approved in this slice.

---

### JIKUO-CORE-17: Policy Decision Record MVP

Purpose:

- persist a compact `jikuo.policy_decision.v0` record for each successful guarded policy create / append write.

Questions:

- Can a stored policy be traced back to the approval phrase and write effect without mining chat history?
- Can decision records remain audit records rather than active policy sources?
- Can decision persistence stay inside guarded write mode while `agent_flow.py propose` remains no-write?

Deliverables:

- `.jikuo/policies/decisions/POLICYDECISION-*.yaml`
- `CAP-POLICY-DECISION-WRITE-01`
- write-plan decision record target
- write-result `decision_record_ref`
- post-write verification for `decision_record_written`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-17_policy_decision_record_mvp.md`
- task-map / execution-mount / loop-composition / Sprint-index updates

Dependency:

- implemented `JIKUO-CORE-15` guarded policy store write MVP.
- implemented `JIKUO-CORE-16` active policy store append MVP.

Status:

- implemented and ready for user review.
- decision records are guarded write audit records, not proposal persistence or active policy sources.
- no policy proposal persistence, revision, supersession, rollback, automatic desktop apply, Skill, MCP, Plugin, frontend, or gate is approved in this slice.

### JIKUO-CORE-18: Real Test Data And Real Chain Policy

Purpose:

- make "tests must use real test data and exercise the real chain" a loadable JIKUO policy instead of an instruction the agent may or may not remember.

Questions:

- Can the policy evaluator load a rule that treats template-copy / shape-only acceptance as missing evidence?
- Can the rule be scoped to testing-governance work through existing task metadata and path conditions?
- Can inline produced evidence satisfy the rule only when it declares real test data / real chain verification?

Deliverables:

- approved report-only policy fixture `POLICY-real-test-data-and-chain`
- missing-evidence projection for `real_test_data_and_chain_evidence`
- regression tests for missing and satisfied evidence paths

Dependency:

- implemented `JIKUO-CORE-10` policy evidence checker MVP.
- implemented `JIKUO-CORE-13` policy condition evaluator MVP.

Status:

- implemented and ready for user review.
- this is report-only: no production root `.jikuo/` write, no code-level placeholder blocker, no automatic desktop invocation, and no gate.

### JIKUO-CORE-19: Pre-Code-Change Governance Classification Principle

Purpose:

- make "classify whether this is a policy / governance-method issue, a code / design-implementation issue, or mixed/unclear before changing code" a loadable JIKUO governance principle carried by report-only policy evidence.

Questions:

- Can the policy evaluator require a pre-code-change classification action?
- Can the rule be scoped to code-change work through existing task metadata and path conditions?
- Can supplied classification evidence satisfy the rule without changing code?

Deliverables:

- approved report-only policy fixture `POLICY-pre-code-change-layer-classification`
- missing-evidence projection for `governance_vs_implementation_classification_evidence`
- regression tests for missing and satisfied evidence paths

Dependency:

- implemented `JIKUO-CORE-10` policy evidence checker MVP.
- implemented `JIKUO-CORE-13` policy condition evaluator MVP.

Status:

- implemented and ready for user review.
- this is report-only: no production root `.jikuo/` write, no automatic desktop invocation, no code-level blocker, and no gate.

### JIKUO-LIVE-01: Policy Evaluation Goes Live In Desktop Chat

Purpose:

- make report-only policy evaluation visible in the normal Codex / Claude desktop APP proposal flow.

Questions:

- Can `agent_flow.py propose` automatically evaluate active policies for task-start style flows?
- Can the card show triggered policies, required actions, evidence status, and missing evidence without writing files?
- Can the card include a light feedback path for `not_applicable`, `defer`, or `needs_scope_narrowing` without implementing full supersession?

Deliverables:

- `agent_flow.py propose` policy evaluation integration for relevant task-start flows
- proposal-card projection for triggered policy/action/evidence status
- no-write tests using CORE-18 / CORE-19 style fixture policies
- lightweight feedback / exemption projection

Dependency:

- implemented `JIKUO-CORE-08` read-only policy store inspection.
- implemented `JIKUO-CORE-09` policy trigger evaluator MVP.
- implemented `JIKUO-CORE-10` policy evidence checker MVP.
- implemented `JIKUO-CORE-13` policy condition evaluator MVP.
- implemented `JIKUO-CORE-18` / `JIKUO-CORE-19` real governance policy fixtures.

Status:

- implemented and ready for user review.
- no gate, no automatic durable write, no feedback persistence, no full policy refinement, no Skill / MCP / Plugin / frontend in this slice.
- verified with `agent_flow_tests.py`, `policy_store_tests.py`, and a real fixture `agent_flow.py propose` markdown card.

---

### JIKUO-LIVE-02: Policy Feedback Record Proposal Bridge

Purpose:

- let desktop users turn explicit feedback on triggered policies into a guarded task-session evidence append proposal.

Questions:

- Can `agent_flow.py propose` accept `policy_feedback_record` without writing files?
- Can feedback distinguish `not_applicable`, `defer`, and `needs_scope_narrowing`?
- Can the runner require a real summary or user phrase instead of accepting a placeholder?

Deliverables:

- `agent_flow.py propose --event policy_feedback_record`
- guarded task-session evidence append command proposal
- no-write tests for successful feedback proposal
- refusal test when no real summary or user phrase is supplied

Dependency:

- implemented `JIKUO-LIVE-01` policy evaluation visible in desktop chat.
- implemented task-session evidence append proposal cards.

Status:

- implemented and ready for user review.
- no automatic persistence, no policy revision, no supersession, no gate, no frontend.
- verified with `agent_flow_tests.py` and a real fixture `agent_flow.py propose` markdown card.

---

### JIKUO-LIVE-03: Guarded Agent Flow Evidence Apply

Purpose:

- let desktop agents apply an explicitly approved task-session evidence append without asking users to manually run helper commands.

Questions:

- Can `agent_flow.py apply` keep the approval boundary explicit?
- Can the first apply path stay narrow instead of becoming arbitrary command execution?
- Can tests prove refusal without approval and successful writes only in a temporary project copy?

Deliverables:

- `agent_flow.py apply --operation task_session_evidence_update`
- structured `jikuo.agent_flow_apply_result.v0`
- atomic registry row for `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01`
- no-write/refusal test without approval
- guarded-write test against a temporary fixture copy

Dependency:

- implemented `JIKUO-LIVE-02` policy feedback proposal bridge.
- implemented task-session guarded evidence append atom.

Status:

- implemented and ready for user review.
- no broad command execution, no policy-store apply, no gate, no frontend.
- verified with `agent_flow_tests.py`, `task_session_tests.py`, and `task_session_cards_tests.py`.

---

### JIKUO-LIVE-04: Policy Proposal Persistence

Purpose:

- make policy-store write decisions auditable by persisting the approved proposal snapshot.

Questions:

- Does every future guarded `write-policy` create a proposal snapshot?
- Does the decision record's `proposal_ref` point to a real file?
- Does the manifest expose `proposal_refs` alongside active policy refs?

Deliverables:

- `.jikuo/policies/proposals/POLICYPROPOSAL-*.yaml`
- manifest `proposal_refs`
- `proposal_ref` and `proposal_snapshot_written` in write results
- updated policy-store regression tests

Dependency:

- implemented guarded policy-store write MVP.
- implemented policy decision records.

Status:

- implemented and ready for user review.
- no proposal editing, no revision / supersession, no rollback, no gate, no frontend.
- verified with `policy_store_tests.py`, `agent_flow_tests.py`, `task_session_tests.py`, `task_session_cards_tests.py`, and a temporary-project guarded write/status/evaluate acceptance chain.

---

### JIKUO-LIVE-05: Policy Evolution Plan Proposal

Purpose:

- make policy refinement / deprecation / supersession review visible before any durable policy evolution writer exists.

Questions:

- Can a desktop agent produce a no-write evolution plan for an active policy?
- Does the plan refuse unknown or inactive target policy refs?
- Does the plan keep actual revision / supersession out of scope until a guarded writer exists?

Deliverables:

- `jikuo.policy_evolution_plan.v0`
- `policy_store.py plan-evolution`
- `agent_flow.py propose --event policy_evolution_plan`
- atomic registry row for `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01`
- regression tests for policy-store and desktop proposal paths

Dependency:

- implemented live policy feedback options.
- implemented guarded policy feedback persistence path.
- implemented policy proposal persistence and decision records.

Status:

- implemented and ready for user review.
- no policy file writes, no manifest mutation, no deprecation, no supersession, no rollback, no gate, no frontend.
- verified with `policy_store_tests.py` and `agent_flow_tests.py`.

---

### JIKUO-LIVE-06: Guarded Policy Deprecation Writer MVP

Purpose:

- let an approved active policy stop triggering without deleting history.

Questions:

- Does the guarded writer refuse without explicit confirmation and approval phrase?
- Does `deprecate_policy` move the target policy from active refs to deprecated refs?
- Does `evaluate` no longer trigger the deprecated policy?

Deliverables:

- `policy_store.py write-evolution`
- guarded `deprecate_policy`
- manifest `deprecated_policy_refs` read-back
- policy evolution proposal snapshot and decision record
- `agent_flow.py propose --event policy_evolution_plan` deprecation command proposal
- regression tests for refusal and successful deprecation against temporary fixture copies

Dependency:

- implemented policy evolution plan proposal.
- implemented proposal persistence and policy decision records.

Status:

- implemented and ready for user review.
- only deprecation is supported as a durable evolution writer.
- no revision, no supersession, no rollback, no deletion, no gate, no frontend.
- verified with `policy_store_tests.py` and `agent_flow_tests.py`.

---

### JIKUO-LIVE-07: Guarded Policy Supersession Writer MVP

Purpose:

- let an active policy be replaced by a newly approved narrower policy without overwriting or deleting the old policy.

Questions:

- Does the guarded writer refuse without explicit confirmation and approval phrase?
- Does `supersede_policy` remove the target policy from active refs and add it to superseded refs?
- Does the replacement policy become the only active trigger source for the scoped condition?
- Does the desktop proposal card show the guarded supersession command before any write?

Deliverables:

- `policy_store.py write-evolution --operation supersede_policy`
- replacement approved policy creation
- manifest `superseded_policy_refs` read-back
- policy evolution proposal snapshot and decision record
- `agent_flow.py propose --event policy_evolution_plan` supersession command proposal
- regression tests for guarded supersession against temporary fixture copies

Dependency:

- implemented policy evolution plan proposal.
- implemented guarded deprecation writer.
- implemented proposal persistence and policy decision records.

Status:

- implemented and ready for user review.
- supersession is supported as a narrow guarded writer.
- no in-place revision, rollback, deletion, gate, frontend, Skill, MCP, or Plugin.
- verified with `policy_store_tests.py` and `agent_flow_tests.py`.

---

### JIKUO-LIVE-08: Agent Flow Guarded Policy Evolution Apply MVP

Purpose:

- let a desktop agent apply an explicitly approved policy deprecation or supersession through the single `agent_flow.py apply` entry point.

Questions:

- Does `agent_flow.py apply --operation policy_evolution_write` refuse without explicit confirmation and approval phrase?
- Does the apply path delegate only to the guarded policy evolution writer rather than opening arbitrary command execution?
- Does a successful supersession write still produce proposal snapshot, decision record, replacement policy, and manifest lifecycle refs?
- Does status/evaluate read-back confirm only the replacement policy remains active?

Deliverables:

- `agent_flow.py apply --operation policy_evolution_write`
- guarded delegation to `policy_store.write_policy_evolution_from_plan`
- policy evolution apply result projection in JSON / Markdown
- regression tests for refusal and successful supersession through `agent_flow.py apply`
- atomic registry row for `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01`

Dependency:

- implemented guarded policy deprecation writer.
- implemented guarded policy supersession writer.
- implemented guarded task-session evidence apply pattern.

Status:

- implemented and ready for user review.
- no arbitrary command execution, no in-place revision, no rollback, no gate, no frontend, no Skill, no MCP, no Plugin.
- verified with `agent_flow_tests.py`.

---

### JIKUO-LIVE-09: Proposal-To-Apply Binding MVP

Purpose:

- prevent a desktop agent from applying a policy evolution write that differs from the proposal ref the user reviewed and approved.

Questions:

- Does `agent_flow.py apply --operation policy_evolution_write` refuse when no proposal ref is supplied?
- Does it refuse when the supplied proposal ref does not match the deterministic policy evolution plan generated from the apply arguments?
- Does a successful supersession still write only after the supplied proposal ref matches the expected plan proposal ref?

Deliverables:

- `agent_flow.py apply --operation policy_evolution_write --proposal-ref <proposal-ref>`
- guarded preflight trace `CAP-POLICY-EVOLUTION-APPLY-BINDING-01`
- apply result `proposal_binding` block with provided / expected refs
- regression tests for missing, mismatched, and matching proposal refs
- atomic registry row for `CAP-POLICY-EVOLUTION-APPLY-BINDING-01`

Dependency:

- implemented no-write policy evolution plans.
- implemented guarded policy deprecation / supersession writers.
- implemented `agent_flow.py apply --operation policy_evolution_write`.

Status:

- implemented and ready for user review.
- no proposal snapshot reuse writer, no in-place revision, no rollback, no gate, no frontend, no Skill, no MCP, no Plugin.
- verified with `agent_flow_tests.py` and `policy_store_tests.py`.

---

### JIKUO-PKG-00: Package Boundary And Extraction Plan

Purpose:

- define the boundary between JIKUO as a reusable tool package and `.jikuo/` as user-project-local state.
- prevent project-context binding, security baseline, package extraction, and MCP work from inheriting source-project-specific assumptions.

Questions:

- Which files are tool-owned package candidates?
- Which files are user-project-local state and must remain in the consuming project?
- How should bundled JIKUO contract docs, project document roles, relative project paths, and external references be represented?
- What must not be physically migrated before the boundary is accepted?

Deliverables:

- work order `SPRINT_050_WO-PER-JIKUO-PKG-00_package_boundary_and_extraction_plan.md`
- planned atom `CAP-PACKAGE-BOUNDARY-PLAN-01`
- pre-MCP foundation sequence: `CORE-20`, `SEC-01`, `PKG-01`, `CORE-20B`, then `MCP-01`
- explicit non-goal: no repository creation, file moves, import changes, `.jikuo/` data migration, or MCP implementation

Dependency:

- implemented `JIKUO-MCP-01` draft surfaced the portability problem.
- current `policy_store.py` still has hardcoded `CONTRACT_REFS`, proving the package boundary is not clean yet.

Status:

- work order drafted and ready for user review.
- current next task.
- no files moved; no runtime behavior changed.

---

### JIKUO-CORE-20: Project Context Binding And Policy Template Portability

Purpose:

- define how reusable policy templates bind to project-specific documents, directories, and conventions without hardcoding one project's paths.
- introduce the template / binding / resolved-policy split required before MCP can expose portable JIKUO capabilities.

Questions:

- Can a template reference `role://document/latest_backlog` instead of a source-project path?
- Can a project bind roles to relative local paths through future `.jikuo/project_context.yaml`?
- Are JIKUO-owned package refs, project role refs, project path refs, and external refs distinct?
- Are path escape and unsafe binding states explicit?

Deliverables:

- governance contract `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- work order `SPRINT_050_WO-PER-JIKUO-CORE-20_project_context_binding_and_policy_template_portability.md`
- draft shapes for `jikuo.project_context.v0`, `jikuo.policy_template.v0`, and `jikuo.resolved_policy.v0`
- no-write acceptance and future resolver test requirements

Dependency:

- accepted package boundary from `JIKUO-PKG-00`.
- policy store and configurable trigger contracts.

Status:

- draft contract ready for user review.
- no `.jikuo/project_context.yaml` file created.
- no resolver code, package extraction, security baseline implementation, or MCP implementation.

---

### JIKUO-SEC-01: Trust Privacy Provenance Baseline

Purpose:

- define the minimum trust, privacy, provenance, namespace, principal, telemetry, and timestamp fields required before reusable templates or MCP tools cross project / user boundaries.
- make social trust and data-boundary assumptions explicit before MCP exposes JIKUO as a tool API.

Questions:

- Does every future template have provenance fields?
- Does every future approval record have a principal field, even in single-user MVP?
- Do MCP-facing results distinguish returned, local-only, and redacted fields?
- Are namespace and fully qualified ids defined before template sharing?
- Is telemetry off by default?
- Are timestamp and local causal-order fields reserved?

Deliverables:

- governance contract `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- work order `SPRINT_050_WO-PER-JIKUO-SEC-01_trust_privacy_provenance_baseline.md`
- contract shapes for provenance, principal, privacy, namespace, telemetry, time, and concurrency baseline fields
- no-write acceptance and future MCP / policy-store test requirements

Dependency:

- package boundary from `JIKUO-PKG-00`.
- portability contract from `JIKUO-CORE-20`.

Status:

- draft contract ready for user review.
- no auth, signing, telemetry, redaction, locks, package extraction, or MCP implementation.

---

### Pre-MCP Portability / Security / Package Foundation

Purpose:

- prevent MCP from freezing source-project-specific assumptions into a public tool API.
- make JIKUO portable across machines, users, and projects before exposing it through MCP.

Required sequence:

1. `JIKUO-PKG-00`: package boundary and extraction plan.
2. `JIKUO-CORE-20`: project context binding and policy template portability.
3. `JIKUO-SEC-01`: trust, privacy, provenance, namespace, principal, telemetry, and timestamp baseline.
4. `JIKUO-PKG-01`: minimal package extraction if approved.
5. `JIKUO-CORE-20B`: resource-reference and `CONTRACT_REFS` hygiene inside the extracted package boundary.
6. `JIKUO-MCP-01`: MCP wrapper implementation.

Scope rule:

- this foundation sequence may add contracts, schemas, and narrow hygiene fixes required for portability.
- it must not become a template marketplace, broad policy rewrite, full team identity system, cloud telemetry product, frontend console, or gate implementation.

---

### JIKUO-MCP-01: MCP Wrapper MVP

Purpose:

- formally move the next phase from additional kernel expansion to an MCP wrapper around stable JIKUO atoms.
- let Codex / Claude desktop Agents call JIKUO through a stable tool surface while ordinary users stay in chat.

Questions:

- Does the wrapper expose only stable status, proposal, and guarded apply operations?
- Does proposal mode stay no-write through MCP?
- Do guarded apply operations still require confirmation, exact approval phrase, and proposal-ref binding where applicable?
- Does the implementation avoid adding new governance capability, broad action execution, gates, UI, Plugin, rollback, or broader condition vocabulary?

Deliverables:

- work order `SPRINT_050_WO-PER-JIKUO-MCP-01_mcp_wrapper_mvp.md`
- planned atom `CAP-MCP-AGENT-FLOW-WRAPPER-01`
- scoped MCP tool list for status, task-start proposal, policy-write proposal, policy-evolution proposal, task-session evidence apply, and policy-evolution apply
- test requirements for unit, integration, smoke, and human desktop-chat review

Dependency:

- implemented local deterministic `agent_flow.py propose`.
- implemented guarded `agent_flow.py apply` for task-session evidence and policy evolution.
- implemented proposal-to-apply binding for policy evolution writes.
- implemented policy store status / trigger / condition / evidence report-only paths.
- accepted `JIKUO-PKG-00`, `JIKUO-CORE-20`, `JIKUO-SEC-01`, `JIKUO-PKG-01`, and `JIKUO-CORE-20B` or explicit user decision to defer a prerequisite.

Status:

- work order drafted; implementation blocked by pre-MCP portability / security / package foundation.
- implementation not started.
- no new kernel behavior, no rollback, no in-place revision, no gate, no frontend, no Skill, no Plugin.

---

## 6. Recommended Order

> **中文注释**：先机芯，再界面；先 report-only，再 gate；先产品定义，再抽象成通用产品。

Recommended next sequence:

1. Accept or revise `05F`.
2. Decide whether to return to Sprint 050 mainline hardening or continue the `机括` productization track.
3. Keep any real gate implementation separate from this feasibility decision.
4. Create `JIKUO-UX-00` before PRD, using scenario-first and atomic-action-first analysis.
5. Create `JIKUO-PRD-01` from the accepted UX/action map.
6. Create `JIKUO-AGENT-00` desktop-agent-first interaction contract before assuming frontend-first or CLI-first delivery.
7. Define `JIKUO-CORE-01` structured result model before implementing checker JSON output.
8. Implement `JIKUO-CORE-02` UI-ready registry model.
9. Review `JIKUO-SCENARIO-CHAIN-01` governance scenario chain and document mounting model.
10. Review or lightly adjust `JIKUO-FLOW-01` against the accepted scenario-chain model.
11. Review `JIKUO-CORE-03` task session and evidence model Part 1 and Part 2 schema.
12. Review `JIKUO-AGENT-01` desktop-agent card projection contract.
13. Review `JIKUO-CORE-04` project-local state and sidecar storage contract.
14. Review implemented `JIKUO-SIDECAR-01` report-only project state bootstrap helper.
15. Review implemented `JIKUO-SIDECAR-02` project-state write mode and initialized `.jikuo/project_state.yaml`.
16. Review implemented `JIKUO-TASKSESSION-01` dry-run task-session helper.
17. Review `JIKUO-TASKSESSION-02` task-session write-mode proposal.
18. Review implemented `JIKUO-TASKSESSION-02` guarded write mode.
19. Review `JIKUO-TASKSESSION-03` project-state task-session index update implementation.
20. `JIKUO-TASKSESSION-04` lifecycle/evidence/completion/handoff implementation accepted for downstream workflow-card planning.
21. `JIKUO-AGENT-02` desktop-agent task-session workflow cards and command composition accepted for downstream helper planning.
22. Treat `JIKUO-AGENT-03` minimal task-session card projection helper as an internal atom, not the user-facing operating path.
23. `JIKUO-FLOW-02` Desktop App Primary Operating Loop accepted as the first user operation chain.
24. Mount `docs/governance/jikuo_execution_mounts.md` before future JIKUO productization tasks.
25. `JIKUO-AGENT-04` desktop-agent invocation contract accepted for explicit triggers, agent-suggested triggers, internal atom invocation, chat rendering, and approval loop.
26. Review implemented local deterministic `agent_flow.py propose` runner.
27. `JIKUO-AGENT-06` lightweight desktop-agent instruction pack creates a project-local agent guide before any installable Skill.
28. `JIKUO-ARCH-01` skeleton / kernel boundary and kernel backlog keeps skeleton work honest before packaging or rule-kernel implementation.
29. `JIKUO-CORE-05` configurable rule trigger and execution policy defines the first policy-kernel contract before policy execution implementation.
30. `JIKUO-CORE-06` rule action and evidence model defines how triggered policy obligations become inspectable.
31. `JIKUO-CORE-07` policy store and user configuration flow defines where approved policies live and how users configure them.
32. `JIKUO-AGENT-07` policy-aware agent flow proposal defines how policy state should appear in desktop APP proposal cards.
33. `JIKUO-CORE-08` read-only policy store inspection lets the runner see whether project-approved policies are missing, initialized, stale, conflict, or active without evaluating them.
34. `JIKUO-CORE-09` policy trigger evaluator MVP lets the runner report exact lifecycle-event matches and required actions without executing actions, checking evidence, writing policies, or gating.
35. `JIKUO-CORE-10` policy evidence checker MVP lets the runner report whether required evidence is missing or satisfied by inline runner-produced evidence.
36. `JIKUO-CORE-11` policy evidence persistence proposal bridge lets the runner propose a guarded task-session evidence append command from explicit policy evidence refs.
37. `JIKUO-CORE-12` policy evidence ingestion MVP lets the runner read explicit task-session policy evidence into report-only evidence matching.
38. `JIKUO-CORE-13` policy condition evaluator MVP lets the runner narrow lifecycle-triggered policies by explicit task metadata and path conditions.
39. `JIKUO-CORE-14` policy write plan proposal MVP lets the runner render proposed policy-store write targets before a durable writer exists.
40. `JIKUO-CORE-15` guarded policy store write MVP lets an approved plan create the first approved report-only policy and manifest.
41. `JIKUO-CORE-16` active policy store append MVP lets the guarded writer add a second approved report-only policy to an active store.
42. `JIKUO-CORE-17` policy decision record MVP lets the guarded writer record who approved which policy-store write effect.
43. `JIKUO-CORE-18` real test data and real chain policy makes fake template-copy acceptance visible as missing evidence in report-only policy evaluation.
44. `JIKUO-CORE-19` pre-code-change governance classification principle makes the "policy/governance first, code/implementation first, or mixed/unclear?" decision visible before implementation edits.
45. Review `JIKUO-LIVE-01`, where policy evaluation now goes live in desktop proposal cards.
46. Review `JIKUO-LIVE-02`, where explicit policy feedback becomes a guarded task-session evidence append proposal.
47. Review `JIKUO-LIVE-03`, where explicitly approved task-session evidence updates can be applied through `agent_flow.py`.
48. Review `JIKUO-LIVE-04`, where future guarded policy writes persist proposal snapshots referenced by decision records.
49. Review `JIKUO-LIVE-05`, where active policies can produce no-write evolution plans for refinement, deprecation, or supersession.
50. Review `JIKUO-LIVE-06`, where active policies can be explicitly deprecated through a guarded writer.
51. Review `JIKUO-LIVE-07`, where active policies can be superseded by explicitly approved replacement policies.
52. Review `JIKUO-LIVE-08`, where approved policy evolution writes can be applied through `agent_flow.py apply`.
53. Review `JIKUO-LIVE-09`, where policy evolution apply must bind to the proposal ref reviewed by the user.
54. Review `JIKUO-LIVE-10`, where policy runtime status becomes a visible card instead of hidden structured fields.
55. Review `JIKUO-LIVE-11`, where runner JSON gains `chat_ready_markdown` and desktop / future MCP callers must surface tool-rendered cards as harness evidence.
56. Review `JIKUO-LIVE-12`, where runtime cards and summaries become visible through client-independent files and `jikuo show`.
57. Review `JIKUO-INTG-01`, where canonical `JIKUO.md` can be distributed into client instruction files without depending on one client hook.
58. Review `JIKUO-PKG-00`, where the package boundary separates tool-owned assets from user-project-local `.jikuo/` state.
59. Review `JIKUO-CORE-20`, where project context binding and policy template portability are made explicit.
60. Review `JIKUO-SEC-01`, where trust, privacy, provenance, namespace, principal, telemetry, timestamp, and visibility baseline fields are declared before MCP.
61. Review / execute `JIKUO-PKG-01` minimal package extraction after boundary, portability, and trust baseline foundations are accepted.
62. Implement `JIKUO-CORE-20B`, where hardcoded resource references such as `CONTRACT_REFS` are removed or neutralized inside the extracted package boundary.
63. Return to `JIKUO-MCP-01`, where the MCP wrapper MVP freezes a packaging-only scope around stable atoms, card-only display tools, and display directives.
64. Implement the MCP adapter / wrapper when the pre-MCP foundations are accepted, prioritizing cross-client consistency.
65. Consider Codex Plugin after runner / MCP semantics are stable.
66. Build `JIKUO-UI-01` rule configuration console after the desktop invocation line and policy configuration boundary are stable enough to preserve primary-surface continuity.
67. Build `JIKUO-UI-02` run control console after the desktop primary loop and configuration boundary are accepted.
68. Add `JIKUO-AUDIT-01` evolution dashboard.
69. Consider `JIKUO-GATE-01` only after report-only false positives are low.

Parallel option:

- After `05F`, the project may return to Sprint 050 mainline hardening (`WORKTREE-03`) before starting JIKUO UI work.

---

## 7. Boundary Rules

> **中文注释**：机括管理工程过程，不消费产品内容本身。

`机括` should not:

- judge product-quality conclusions
- decide whether a generated product output is good
- replace human acceptance
- silently promote report-only checks into blocking gates
- require users to edit raw YAML once the UI exists
- hide rule changes from audit history

`机括` should:

- make rules visible
- make triggers explicit
- make missing evidence obvious
- keep human approval as an auditable event
- allow rules to evolve safely
- provide rollback paths for enforcement changes
- keep routine confirmations available in the user's active Codex / Claude desktop APP workflow when safe

---

## 8. Relationship To Sprint 050 Hardening

> **中文注释**：这是从 Sprint 050 孵化出来的产品化方向，不要让它吞掉当前叙事引擎 hardening。

Sprint 050 mainline hardening still needs:

- retry baseline contract implementation
- continuity canonicalization hygiene
- pending ownership / supersession audit
- semantic regression cases
- eventual pre-narrative grounding design

`机括` can support those tasks by making their engineering obligations visible, but it should not replace the actual hardening implementation.

---

## 9. Current Decision Point

> **中文注释**：当前已经实现最小 no-write `agent_flow.py propose`，补充了项目内 desktop-agent instruction pack，新增了 skeleton / kernel boundary，完成 `CORE-05` 规则触发策略契约、`CORE-06` action/evidence model、`CORE-07` policy store/configuration flow，并完成 `AGENT-07` policy-aware proposal contract。新的暂停点是验收 policy-aware proposal contract，然后决定进入 runner 实现、evidence checker、store adapter，还是回到包装/调用层。

Open decision:

- Current pause point: review `JIKUO-SEC-01` before physical package extraction, resource-reference hygiene, or MCP implementation.

- `JIKUO-LIVE-01` includes automatic evaluation, card projection, inline produced evidence matching, and minimal non-persistent feedback / exemption projection.
- `JIKUO-LIVE-02` turns explicit policy feedback into a guarded task-session evidence append proposal without persisting in propose mode.
- `JIKUO-LIVE-03` applies one explicitly approved task-session evidence append through `agent_flow.py apply`.
- `JIKUO-LIVE-04` persists policy write proposal snapshots for future guarded policy writes.
- `JIKUO-LIVE-05` renders no-write policy evolution plans for active policies.
- `JIKUO-LIVE-06` deprecates active policies through an explicit guarded writer.
- `JIKUO-LIVE-07` supersedes active policies through an explicit guarded writer and replacement approved policy.
- `JIKUO-LIVE-08` applies approved policy evolution writes through `agent_flow.py apply`.
- `JIKUO-LIVE-09` binds policy evolution apply to the proposal ref reviewed by the user.
- `JIKUO-MCP-01` freezes a packaging-only MCP wrapper MVP around stable atoms but is blocked by pre-MCP foundations.
- `JIKUO-PKG-00` set the package boundary.
- `JIKUO-CORE-20` set the project context / template portability contract.
- `JIKUO-SEC-01` is the next review point for trust / privacy / provenance baseline.

If accepted:

- review / execute `JIKUO-PKG-01` minimal package extraction next, then implement `JIKUO-CORE-20B` inside the extracted package boundary.

If not accepted:

- refine the trust / privacy / provenance baseline before adding resource-reference hygiene, physical extraction, MCP, broader persistence, broader conditions, UI, Plugin, or gates.

---

## 10. Current Task Map Snapshot: 2026-05-14

> **中文注释**：这一节是当前执行入口。后续机括开发任务应先挂载本节，再参考上文完整历史地图。

Snapshot purpose:

- prevent the productization track from endlessly expanding the kernel before MCP packaging
- preserve both the previous todo map and the latest todo map
- make scope changes explicit before the next implementation slice starts

Latest mounted todo map:

- source: `docs/governance/jikuo_productization_task_map.md`
- current snapshot: `Current Task Map Snapshot: 2026-05-14`
- current pause point: revised integration-neutral `JIKUO-MCP-01` scope review and MCP pre-implementation API neutrality review; stop before MCP implementation for user discussion

Previous mounted todo map:

- source: `Recommended Order` and `Current Decision Point` before the 2026-05-13 scope-control update
- previous pause point: review `JIKUO-LIVE-08`, then choose among durable revision / rollback writer planning, broader apply operations, installable Skill, MCP wrapper planning, or broader condition vocabulary planning
- previous risk: too many valid downstream options kept pulling the track back into kernel expansion

Delta from previous todo map:

- `POLICY-task-scope-control-before-packaging` was added to require task-scope evidence before work-order delivery slices.
- `JIKUO-LIVE-09` was added as the final pre-MCP safety lock for policy evolution apply.
- `JIKUO-PKG-01` was promoted ahead of `CORE-20B`, so physical package extraction happens before resource-reference hygiene and prevents future fixes from inheriting source-project identity.
- MCP wrapper implementation is now blocked until package boundary, project-context binding, trust/security baseline, minimal package extraction, and resource-reference hygiene are accepted or explicitly deferred.
- MCP wrapper planning now treats visibility as a universal harness requirement: out-of-band runtime snapshots, narrow card tools, display directives, and universal instruction files are pre-MCP foundations rather than client-specific enhancements.
- The temporary same-file `previous_todo_map` binding is disabled in `.jikuo/project_context.yaml`; real previous/latest todo comparison requires future snapshot rotation.
- durable revision / rollback writers, broader apply operations, broader condition vocabulary, frontend, Plugin, and gates are deferred by default.

Completed in this snapshot:

- submit `JIKUO-LIVE-09` proposal-to-apply binding
- define `JIKUO-MCP-01` MCP wrapper MVP work order
- define `JIKUO-PKG-00` package boundary and extraction plan
- mark `JIKUO-MCP-01` implementation as blocked by pre-MCP portability / security / package foundation
- define `JIKUO-CORE-20` project context binding and policy template portability contract
- define `JIKUO-SEC-01` trust / privacy / provenance baseline contract
- draft `JIKUO-PKG-01` minimal package extraction work order and make it the next pre-MCP slice after SEC-01 review
- execute initial `JIKUO-PKG-01` local package extraction at `D:\personal_project\Jikuo`
- implement `JIKUO-LIVE-11` deterministic harness chat return contract so JSON runner output carries `chat_ready_markdown`
- implement `JIKUO-CORE-23` project-context resolver and guarded template activation in `policy_templates.py`
- implement `JIKUO-CORE-24` desktop `agent_flow.py` bridge for template import planning and guarded activation
- unify standalone repository main document mount paths under `docs/`, register `CAP-MAIN-DOC-MOUNT-MAINTENANCE-01`, and define the slice-completion main-document check scope
- draft and implement `JIKUO-LIVE-12` Phase 1 out-of-band runtime visibility channels as the next pre-MCP visibility foundation
- draft `JIKUO-INTG-01` universal instruction file distribution as the cross-client instruction foundation
- revise `JIKUO-MCP-01` scope to include card-only runtime status tools, display directives, and runtime visibility updates
- draft `JIKUO-SDK-01` Agent SDK and agentic platform adapter exploration as an MCP-adjacent architecture task so OpenAI / Claude / Google / Vercel SDKs and Antigravity-style platform orchestration can be assessed before MCP implementation hardens
- draft `JIKUO-ARCH-02` integration neutrality and `src/jikuo/integrations/` layout so MCP does not land as root-level kernel code
- accept `JIKUO-ARCH-02` integration neutrality and `JIKUO-SDK-01` Agent SDK / platform posture as pre-MCP baselines
- implement and accept `JIKUO-INTG-01` universal instruction file distribution through `src/jikuo/integrations/instruction_files.py` and `jikuo install`

Latest todo map:

Accepted precondition:

- `JIKUO-LIVE-12` Phase 1 out-of-band runtime visibility accepted on 2026-05-14: `.jikuo/runtime/last_card.md`, `.jikuo/runtime/state_summary.json`, runtime history, `jikuo show`, `jikuo show --last-card`, and `client_display_links`.
- `JIKUO-LIVE-13` taskmap / insight / follow-up evidence accepted on 2026-05-14: `work_routing`, `taskmap_insight_followup_distinction_evidence`, and zero missing evidence for the self-bootstrap summary-distinction policy in normal task-start proposals.
- `JIKUO-ARCH-02` integration neutrality accepted on 2026-05-14: integration-specific logic belongs under `src/jikuo/integrations/`, MCP is anchored under `src/jikuo/integrations/mcp/`, and core APIs must remain protocol-neutral.
- `JIKUO-SDK-01` Agent SDK / platform posture accepted on 2026-05-14: OpenAI Agents SDK, Claude Agent SDK, Google ADK, Vercel AI SDK, and Antigravity-style platforms remain optional adapter paths after MCP stabilizes.
- `JIKUO-INTG-01` universal instruction distribution accepted on 2026-05-14: `jikuo install` can plan and guarded-write canonical `JIKUO.md` plus supported client instruction files while preserving existing user content.

Open items:

1. Review / accept revised `JIKUO-MCP-01` visibility and integration-neutral scope: structured tools, card-only tools, `jikuo.get_runtime_status`, `jikuo.get_runtime_status_card`, `jikuo.get_display_card`, display directives, runtime snapshot refs, and implementation under `src/jikuo/integrations/mcp/`.
2. Run the MCP pre-implementation API neutrality review for `agent_flow.py`, `policy_store.py`, `runtime_visibility.py`, policy templates, and starter policies.
3. Decide whether `.jikuo/project_context.yaml` previous/latest todo comparison remains disabled for now or gets a future snapshot rotation work order.
4. Review / implement starter policy provenance backfill or an explicit missing-provenance fallback before starter policies are exposed through MCP.
5. Review / accept the updated SEC-01 visibility and integration neutrality baseline: critical JIKUO runtime state must have both chat-ready output and user-accessible out-of-band output, and integration-specific logic must stay outside the core kernel.
6. Review release-readiness follow-ups before external users: product-facing root README, license decision, minimal CI, pytest/dev extras.
7. Return to `JIKUO-MCP-01` implementation only after the above pre-MCP items are accepted or explicitly deferred; stop for user discussion before code implementation.
8. Keep the decision about whether new self-bootstrap policies enter built-in starter templates suspended until explicit user approval.
9. Defer dashboard, OS notifications, per-client hooks/packs, Agent SDK runner implementation, rollback, broader conditions, UI, Plugin, and gates unless explicitly promoted by user approval.
10. Keep future SDK / platform adapters as post-MCP placeholders: `JIKUO-INTG-CLAUDE-AGENT-SDK-01`, `JIKUO-INTG-OPENAI-AGENTS-SDK-01`, `JIKUO-INTG-GOOGLE-ADK-01`, `JIKUO-INTG-VERCEL-AI-SDK-01`, and `JIKUO-INTG-ANTIGRAVITY-01`.

MCP MVP scope freeze:

- include: policy-store status inspection
- include: `jikuo.get_runtime_status` structured runtime status inspection
- include: `jikuo.get_runtime_status_card` narrow card-only runtime status rendering
- include: `jikuo.get_display_card` narrow latest-card rendering
- include: task-start proposal rendering
- include: policy-write-plan proposal rendering
- include: policy-evolution-plan proposal rendering
- include: policy-template import-plan proposal rendering
- include: guarded task-session evidence apply
- include: guarded policy evolution apply with proposal-ref binding
- include: guarded policy-template activation apply
- require: MCP implementation lives under `src/jikuo/integrations/mcp/` and consumes integration-neutral core APIs
- require: card-producing MCP tools return display directives that identify verbatim card fields, summarizable fields, hidden debug fields, and response priority
- require: card-producing MCP tools update the out-of-band runtime visibility channel or explicitly report that runtime visibility is unavailable
- require: MCP schemas and card/display contracts remain usable by future optional Agent SDK / agentic platform adapters without making any one SDK or platform a kernel dependency
- require: no-write proposal mode remains no-write
- require: guarded apply still requires explicit approval phrase and technical confirmation
- require: all MCP calls return structured results suitable for desktop chat rendering
- require: no-write MCP proposal calls return `chat_ready_markdown` and preserve `policy_runtime_status` when present

MCP MVP non-goals:

- no frontend configuration console
- no Codex Plugin packaging
- no automatic gate / blocking enforcement
- no broad action executor
- no durable policy rollback writer
- no in-place policy revision writer
- no broad condition vocabulary expansion
- no hidden writes outside existing guarded apply operations

MCP implementation blockers:

- no MCP implementation before package boundary is accepted
- no MCP implementation before the package has a standalone local boundary or the user explicitly defers package extraction
- no MCP implementation before project-specific paths are represented as project-context bindings or package resources
- no MCP implementation before privacy return boundaries are declared
- no MCP implementation before `CONTRACT_REFS` hardcoded the incubating source project references are removed, neutralized, or explicitly classified as bundled package refs
- no MCP implementation before `JIKUO-LIVE-12` Phase 1 runtime visibility is accepted or explicitly deferred with a recorded chat-only risk
- `JIKUO-INTG-01` universal instruction distribution is accepted; MCP implementation still must preserve its instruction/display contract
- no MCP implementation before `JIKUO-ARCH-02` integration neutrality and `src/jikuo/integrations/` layout is accepted or explicitly deferred
- no MCP implementation before `JIKUO-SDK-01` Agent SDK extension posture is accepted or explicitly deferred
- no MCP exposure of starter policies before provenance backfill or a missing-provenance fallback rule is accepted
- no policy requiring previous/latest todo comparison may be treated as satisfied while `previous_todo_map` is disabled without snapshot rotation
