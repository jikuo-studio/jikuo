# SPRINT_050_WO-PER-JIKUO-MCP-01: MCP Wrapper MVP

> **Status**: Draft, blocked until pre-MCP portability / security / package / visibility foundation is accepted
> **Product meaning**: formally move the next phase from more kernel expansion to an MCP wrapper MVP, so desktop Agents can call JIKUO through a stable tool surface while users remain in their desktop AI client.
> **Scope rule**: wrap stable atoms only; do not add new governance capability in this slice.

## 1. Why This Slice Now

`JIKUO-LIVE-09` completed the last pre-MCP safety lock: a guarded policy evolution apply must bind to the proposal ref reviewed by the user.

The next useful product step is therefore not another kernel feature. It is to expose the stable runner and guarded apply paths through MCP, so MCP-compatible desktop Agents can call JIKUO consistently without asking ordinary users to switch to CLI helper orchestration.

This work order freezes the MCP MVP boundary before implementation starts.

Implementation is intentionally blocked until these pre-MCP foundations are accepted:

- `JIKUO-PKG-00`: package boundary and extraction plan
- `JIKUO-CORE-20`: project context binding and policy template portability
- `JIKUO-SEC-01`: trust, privacy, provenance, namespace, principal, telemetry, and timestamp baseline
- `JIKUO-PKG-01`: minimal package extraction before `CORE-20B`
- `JIKUO-CORE-20B`: resource-reference and `CONTRACT_REFS` hygiene inside the extracted package boundary
- `JIKUO-CORE-23`: project-context resolver and guarded template activation, or an explicit decision to keep template activation outside the first MCP wrapper
- `JIKUO-CORE-24`: desktop `agent_flow.py` bridge for template import planning and guarded activation, or an explicit decision to keep template activation outside the first MCP wrapper
- `JIKUO-LIVE-12`: out-of-band runtime visibility files, `jikuo show` CLI, and `client_display_links` accepted on 2026-05-14
- `JIKUO-INTG-01`: universal instruction file distribution, or an explicit user decision to defer cross-client instruction sync
- `JIKUO-ARCH-02`: integration neutrality and `src/jikuo/integrations/` layout, or an explicit user decision to defer integration layout cleanup
- `JIKUO-ARCH-03`: MCP pre-implementation API neutrality review, or an explicit user decision to defer the review
- `JIKUO-SDK-01`: Agent SDK / agentic platform extension posture, or an explicit user decision to defer SDK ecosystem planning
- starter policy provenance backfill / fallback rule before starter policies are exposed through MCP
- `.jikuo/project_context.yaml` previous-todo binding must not pretend to provide a real previous snapshot unless snapshot rotation exists

## 2. User Scenario

Primary scenario:

- The user stays in their desktop AI client chat.
- The user asks for a governed task, policy proposal, or approved policy evolution.
- The Agent invokes a JIKUO MCP tool internally.
- The MCP tool returns structured result fields, a display contract, and a card ref when applicable.
- Card-producing MCP tools update the out-of-band runtime visibility snapshot.
- The Agent calls a card-only display tool or uses the returned card field and pastes it before any commentary.
- If the Agent fails to paste the card, the user can inspect the latest runtime card through `jikuo show --last-card` or `.jikuo/runtime/last_card.md`.
- The user approves, rejects, or asks for modification in chat.

This preserves the Desktop App Primary Operating Loop. MCP is the callable tool layer, not a new user-facing workflow that requires the user to run terminal commands.

## 3. Protocol Fit

Reference sources:

- Official MCP SDK page: `https://modelcontextprotocol.io/docs/sdk`
- Official MCP transports spec: `https://modelcontextprotocol.io/specification/2025-11-25/basic/transports`
- Official MCP tools spec: `https://modelcontextprotocol.io/specification/2025-11-25/server/tools`

MVP protocol posture:

- use MCP tools rather than resources / prompts as the primary wrapper surface
- prefer `stdio` first for local desktop client integration
- keep all stdout protocol traffic MCP-compliant; logs must not pollute stdout
- return both `chat_ready_markdown` and structured result fields where the SDK supports structured content
- return explicit display directives for card fields
- expose card-only tools for the latest display card / runtime status card so Agents have less room to summarize away governance status
- write the latest card projection to the out-of-band runtime visibility channel when a card-producing tool runs
- preserve `policy_runtime_status` as a visible first-screen card when it exists in the wrapped proposal
- keep human approval visible for sensitive write-capable tools
- resolve project-specific document and policy bindings before tool execution; MCP tools must not depend on NarrativeSystem hardcoded paths
- distinguish fields that may be returned to the MCP client from fields that must stay local
- implement MCP under `src/jikuo/integrations/mcp/` so MCP is an adapter layer rather than part of the core kernel

## 4. In Scope

Expose these stable operations through a narrow MCP surface:

| MCP tool | Wrapped atom | Write mode | Product role |
|---|---|---|---|
| `jikuo.status` | `CAP-POLICY-STORE-STATUS-01` | no-write | inspect whether project-local policy store is active / missing / stale / conflict |
| `jikuo.get_runtime_status` | `CAP-POLICY-STORE-STATUS-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01` | no governance write | return current policy runtime status as structured data |
| `jikuo.get_runtime_status_card` | `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01` | no governance write; may update `.jikuo/runtime/` | return only the chat-ready runtime status card |
| `jikuo.get_display_card` | `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write | return the latest or requested display card markdown only |
| `jikuo.propose_task_start` | `CAP-AGENT-FLOW-01` plus live policy evaluation atoms | no governance write; may update `.jikuo/runtime/` | return structured task-start proposal data plus card refs / display directives |
| `jikuo.propose_policy_write_plan` | `CAP-POLICY-STORE-WRITE-PROPOSE-01` | no governance write; may update `.jikuo/runtime/` | return proposed policy-store write data plus card refs / display directives before any durable policy write |
| `jikuo.propose_policy_evolution_plan` | `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01` | no governance write; may update `.jikuo/runtime/` | return refinement / deprecation / supersession plan data plus card refs / display directives before any durable write |
| `jikuo.propose_policy_template_import_plan` | `CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01` | no governance write; may update `.jikuo/runtime/` | return resolved template binding data plus card refs / display directives |
| `jikuo.apply_task_session_evidence_update` | `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01` | guarded write | append one explicitly approved task-session evidence item |
| `jikuo.apply_policy_evolution_write` | `CAP-POLICY-EVOLUTION-APPLY-BINDING-01` and `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01` | guarded write | apply one approved policy deprecation / supersession only when proposal ref, confirmation, and approval phrase match |
| `jikuo.apply_policy_template_activation` | `CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01` | guarded write | activate one approved resolved template only after bindings, confirmation, and approval phrase match |

Display response contract for card-returning tools:

```json
{
  "display": {
    "must_show_verbatim": ["card_markdown"],
    "card_priority_order": [
      "policy_runtime_status",
      "task_session_completion_acceptance",
      "task_session_start_preview"
    ],
    "may_summarize": ["data_details"],
    "do_not_show": ["debug_trace"],
    "priority": "first_in_response"
  },
  "card_markdown": "## Policy Runtime Status\n\n| Status | Count |\n|---|---:|\n| Active | 6 |\n| Triggered | 1 |\n| Missing Evidence | 0 |\n",
  "runtime_snapshot_ref": ".jikuo/runtime/last_card.md"
}
```

Tool descriptions for card-only tools must state that `card_markdown` is governance output and must be displayed verbatim before commentary. This is not a replacement for out-of-band visibility; it is the MCP-facing display contract.

## 5. Out Of Scope

This slice must not implement:

- new policy condition vocabulary
- new evidence ingestion model
- broad action executor
- automatic gate / blocking enforcement
- durable rollback writer
- in-place policy revision writer
- frontend configuration console
- Codex Plugin packaging
- product-output quality judgment
- hidden writes outside the existing guarded apply operations

## 6. Scenario Chain And Atom Composition

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Inspect project governance state | Agent calls `jikuo.status`; Agent returns structured status and short summary | `CAP-POLICY-STORE-STATUS-01` | no-write; no `.jikuo` creation |
| Display latest card | Agent calls `jikuo.get_display_card` or `jikuo.get_runtime_status_card`; Agent outputs `card_markdown` verbatim | `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; card can be verified out of band |
| Start governed work | Agent calls `jikuo.propose_task_start`; result includes proposal data, policy context, triggered policies, missing evidence, display directives, and runtime card refs | `CAP-AGENT-FLOW-01`, `CAP-LIVE-DESKTOP-POLICY-EVAL-01`, condition / evidence atoms, `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; runtime snapshot may update |
| Configure a new rule | Agent calls `jikuo.propose_policy_write_plan`; user reviews generated policy and write effects through a display card | `CAP-POLICY-STORE-WRITE-PROPOSE-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; runtime snapshot may update |
| Evolve an existing rule | Agent calls `jikuo.propose_policy_evolution_plan`; user reviews deprecation / supersession effect through a display card | `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; runtime snapshot may update |
| Adopt a reusable policy template | Agent calls `jikuo.propose_policy_template_import_plan`; user reviews resolved bindings, write targets, and generated activation command | `CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01`, `CAP-POLICY-TEMPLATE-IMPORT-PLAN-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; runtime snapshot may update |
| Persist approved evidence | Agent calls `jikuo.apply_task_session_evidence_update` with confirmation and approval phrase | `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01` | guarded write to explicit task-session only |
| Apply approved rule evolution | Agent calls `jikuo.apply_policy_evolution_write` with proposal ref, confirmation, and approval phrase | `CAP-POLICY-EVOLUTION-APPLY-BINDING-01`, `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01` | guarded write only after proposal binding passes |
| Apply approved policy-template activation | Agent calls `jikuo.apply_policy_template_activation` with template path, confirmation, and approval phrase | `CAP-POLICY-TEMPLATE-ACTIVATE-01`, `CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01` | guarded write only after bindings resolve |

## 7. Implementation Plan

Recommended implementation slices:

0. Confirm `PKG-00`, `CORE-20`, `SEC-01`, `PKG-01`, `CORE-20B`, `CORE-23`, `CORE-24`, `LIVE-12` Phase 1, `INTG-01`, `ARCH-02`, `ARCH-03`, `SDK-01`, starter provenance handling, and any approved minimal package extraction prerequisites are complete or explicitly deferred with user approval.
1. Create a testable MCP adapter boundary under `src/jikuo/integrations/mcp/` that maps tool names and arguments to package-safe `agent_flow.py` / `policy_store.py` behavior.
2. Add card-only and runtime-status-card tool adapters before broader proposal tools.
3. Add display directives, `card_priority_order`, and out-of-band runtime snapshot refs to card-producing tool responses.
4. Add an MCP server wrapper using the official Python SDK when available; if the SDK is not available locally, stop at the adapter boundary and record the dependency decision rather than hand-rolling a non-compliant server.
5. Add unit tests for tool schema / argument validation / approval refusal / privacy field classification / display contract shape.
6. Add integration tests against temporary fixture copies for no-write proposals, resolved project context, runtime visibility snapshots, and guarded apply paths.
7. Add smoke verification for tool discovery and one no-write card-only tool call.
8. Update universal and client-specific instruction packs to prefer MCP when available, while keeping `agent_flow.py` as a fallback.

## 8. Testing Requirements

Unit tests:

- tool name registry and input schema mapping
- no-write proposal calls do not write
- guarded apply calls refuse without confirmation and approval phrase
- policy evolution apply refuses mismatched proposal refs

Integration tests:

- `jikuo.status` against active / missing policy-store fixtures
- `jikuo.propose_task_start` against `policy_store_active_project`
- `jikuo.get_runtime_status_card` returns card markdown only plus display directives
- `jikuo.get_display_card` returns the last runtime card from `.jikuo/runtime/`
- card-producing proposal tools return display directives where `card_priority_order[0]` is `policy_runtime_status`
- `jikuo.propose_policy_write_plan` returns a no-write card
- `jikuo.propose_policy_evolution_plan` returns a proposal ref
- `jikuo.apply_policy_evolution_write` succeeds only in a copied temporary fixture with matching proposal ref

Smoke tests:

- MCP tool list exposes only the scoped MVP tools
- one no-write MCP call returns `chat_ready_markdown` plus structured result
- one card-only MCP call returns a compact Markdown card that should be shown verbatim
- `jikuo.propose_task_start` returns `cards[]` containing `policy_runtime_status` when the wrapped runner produced one
- card-producing tools render `policy_runtime_status` before task-session / lifecycle cards when the wrapped runner produced one
- no root `.jikuo/policies/` or `.jikuo/task_sessions/` is created during no-write smoke
- card-producing no-write tools update only the `.jikuo/runtime/` visibility channel when runtime visibility is enabled

Human semantic review:

- confirm the desktop chat result is understandable to a non-CLI user
- confirm the Agent did not summarize away the returned `chat_ready_markdown`
- confirm `policy_runtime_status` appears in the first visible card position before lifecycle, task-session, or write-plan cards
- confirm approval boundaries are visible
- confirm this slice feels like packaging stable atoms, not expanding the governance kernel

## 9. Acceptance Criteria

- The work order, task map, and execution mounts all identify `JIKUO-MCP-01` as the scoped MCP implementation slice, blocked until pre-MCP foundations are accepted.
- The planned implementation path is `src/jikuo/integrations/mcp/`, not root-level `src/jikuo/mcp_server.py` or `src/jikuo/mcp_adapter.py`.
- The MCP MVP tool list is frozen before code implementation starts.
- No-write proposal tools return chat-ready text plus structured fields, and policy runtime status remains first-screen visible when present.
- Card-only tools return compact card Markdown and display directives.
- Card-producing tools also update the out-of-band runtime visibility channel or explicitly report why runtime visibility is disabled.
- No new governance capability is introduced by this work order.
- The future implementation has explicit unit / integration / smoke / human review requirements.
- MCP implementation is blocked until the pre-MCP portability / security / package / visibility foundation is accepted or explicitly deferred.
