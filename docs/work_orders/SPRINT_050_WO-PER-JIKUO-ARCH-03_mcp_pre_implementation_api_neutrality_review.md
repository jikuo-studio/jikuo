# SPRINT_050_WO-PER-JIKUO-ARCH-03: MCP Pre-Implementation API Neutrality Review

> **Status**: Accepted on 2026-05-15, pre-MCP review complete
> **Product meaning**: verify that the first MCP wrapper can consume stable JIKUO core APIs without making MCP, any Agent SDK, or any desktop client part of the governance kernel.
> **Scope rule**: review and document the API boundary only; do not implement the MCP adapter, MCP server, Agent SDK plugin, hook, dashboard, or new governance capability in this slice.

## 1. Why This Slice Now

`JIKUO-ARCH-02` accepted the integration-neutral layout rule and anchored future MCP code under `src/jikuo/integrations/mcp/`.

Before implementation starts, the core surfaces need one more check:

- can integrations call structured functions rather than scrape CLI stdout?
- can card-producing paths return chat-ready output and update `.jikuo/runtime/`?
- can policy and template flows preserve local approval, evidence, and privacy boundaries?
- are any remaining blockers explicit enough to stop MCP exposure before they become hidden product debt?

## 2. Reviewed Surfaces

Reviewed code and package assets:

- `src/jikuo/agent_flow.py`
- `src/jikuo/policy_store.py`
- `src/jikuo/runtime_visibility.py`
- `src/jikuo/policy_templates.py`
- `src/jikuo/starter_policies.py`
- `src/jikuo/policy_templates/engineering_governance/*.yaml`
- `src/jikuo/starter_policy_packs/engineering_governance/manifest.yaml`
- `src/jikuo/integrations/`

Review evidence:

- Task-session: `.jikuo/task_sessions/task_20260514T170932Z_mcp_pre_implementation_api_neutrality_review_82553d04.yaml`
- Task-start policy runtime triggered `POLICY-jikuo-task-session-binding-at-slice-start` with no missing evidence.
- No MCP adapter/server files were created.

## 3. Findings

| Surface | Neutrality finding | MCP implication |
|---|---|---|
| `agent_flow.build_proposal(...)` | Pass. Returns structured dictionaries and accepts explicit `project_root`, `task_type`, `jikuo_layer`, path scope, produced evidence, and task-session refs without requiring CLI parsing. | MCP proposal tools should call this core function or a small package facade, then attach MCP display directives outside the kernel. |
| `agent_flow.proposal_with_chat_ready_markdown(...)` | Pass with caution. Produces `chat_ready_markdown`, client display links, and runtime visibility snapshots through a core helper. | MCP card-producing tools should reuse this path to keep chat output and out-of-band files synchronized. |
| `agent_flow.build_apply_result(...)` | Pass. Guarded apply semantics remain structured and explicit; writes require confirmation and approval phrase. | MCP write-capable tools must preserve the same confirmation, approval phrase, and proposal-ref binding boundaries. |
| `policy_store.inspect_policy_store(...)` / `evaluate_policy_triggers(...)` | Pass. Policy store inspection and report-only evaluation return structured reports without stdout scraping. | `jikuo.status` and runtime-status tools can wrap these functions directly. |
| `policy_store.build_policy_write_plan(...)` / `build_policy_evolution_plan(...)` | Pass. Proposal paths are no-write, structured, and already separate from guarded writers. | MCP plan tools can expose proposal cards without introducing new policy mutation semantics. |
| `runtime_visibility.prepare_agent_flow_snapshot(...)` / `persist_prepared_agent_flow_snapshot(...)` | Pass. Runtime visibility is local, project-root confined, and reusable outside CLI. | Card-producing MCP tools should call this core path or the existing proposal output helper. |
| `runtime_visibility.build_client_display_links(...)` | Pass for local desktop use; privacy caution for remote transports. Absolute local paths are useful for clickable desktop links but must be treated as local-only if a future non-local MCP transport appears. | First MCP MVP should assume local desktop `stdio`; any remote transport must add explicit response privacy classification before exposing local paths. |
| `policy_templates.build_import_plan(...)` / `activate_template_from_plan(...)` | Pass. Template import is structured, binding-aware, and guarded for activation. | MCP template import tools can wrap the plan/apply path after starter provenance handling is accepted. |
| `starter_policies.build_starter_init_plan(...)` / `initialize_starter_pack(...)` | Mostly pass. Starter init is structured and guarded, but the starter templates do not yet carry the SEC-01 `provenance` field shape. | Starter policies must not be exposed through MCP until provenance is backfilled or an explicit missing-provenance fallback is accepted. |
| `src/jikuo/integrations/` | Pass. Client instruction sync already lives under integrations; core modules do not import integration adapters. | MCP implementation should create its adapter under `src/jikuo/integrations/mcp/` and should not add MCP-specific logic to `agent_flow.py` or `policy_store.py`. |

## 4. API Decision

No new core facade is required before the first MCP adapter slice.

The first MCP implementation may wrap these stable callable surfaces:

- `policy_store.inspect_policy_store`
- `policy_store.evaluate_policy_triggers`
- `agent_flow.build_proposal`
- `agent_flow.proposal_with_chat_ready_markdown`
- `agent_flow.build_apply_result`
- `agent_flow.apply_result_with_chat_ready_markdown`
- `runtime_visibility.load_state_summary`
- `runtime_visibility.load_last_card`
- `policy_templates.build_import_plan`
- `starter_policies.build_starter_init_plan`

The MCP adapter must not call CLI `main()` functions as its normal integration path.

## 5. Remaining Blockers Before MCP Implementation

This review does not clear every MCP blocker.

Still blocking MCP implementation unless accepted or explicitly deferred:

1. Starter policy provenance backfill or missing-provenance fallback.
2. Response-level privacy classification for MCP-returned local paths, approval data, and raw sidecar records.
3. User acceptance of the revised `JIKUO-MCP-01` scope.

Resolved after this review:

- `JIKUO-ARCH-03` was accepted by the user on 2026-05-15.
- `JIKUO-LIVE-18` disabled the fake previous/latest todo same-file binding for v0 and deferred real snapshot rotation as a future capability.

## 6. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| MCP pre-implementation API neutrality review | maintainer starts governed review -> task-session binding policy triggers -> core API surfaces are inspected -> findings are recorded -> MCP remains blocked until review / provenance / snapshot / privacy decisions are accepted | `CAP-MCP-PREIMPLEMENTATION-API-NEUTRALITY-REVIEW-01`; `CAP-INTEGRATION-NEUTRALITY-CONTRACT-01`; `CAP-MCP-AGENT-FLOW-WRAPPER-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01`; `CAP-TASK-SESSION-BINDING-EVIDENCE-01` | docs-only review; no MCP adapter/server code; no dependency change; no new write path beyond the approved task-session record |

## 7. Acceptance Criteria

- The task map registers `JIKUO-ARCH-03` and `CAP-MCP-PREIMPLEMENTATION-API-NEUTRALITY-REVIEW-01`.
- The reviewed core APIs are named as the only acceptable first MCP adapter call surfaces.
- The review explicitly says the MCP adapter must not call CLI `main()` as its normal path.
- Remaining blockers are visible before MCP implementation starts.
- No MCP adapter, server, SDK plugin, client hook, dashboard, or new governance capability is implemented in this slice.

## 8. Accepted Result

Accepted by the user on 2026-05-15.

Accepted decisions:

- MCP must remain an adapter over structured JIKUO core APIs.
- The first MCP adapter must not call CLI `main()` functions or scrape stdout as its normal integration path.
- Remaining pre-MCP blockers stay visible until accepted, implemented, or explicitly deferred.
