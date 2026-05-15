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
- `JIKUO-LIVE-19`: starter policy provenance backfill accepted before starter policies are exposed through MCP
- `JIKUO-SEC-02`: MCP response privacy classification baseline accepted before any MCP response is serialized
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

Stage A exposes only no-write / card-returning operations. These tools may update `.jikuo/runtime/` when they produce runtime visibility, but they must not create `.jikuo/policies/`, create `.jikuo/task_sessions/`, or update `.jikuo/project_state.yaml`.

| Stage A MCP tool | Wrapped atom | Write mode | Product role |
|---|---|---|---|
| `jikuo.status` | `CAP-POLICY-STORE-STATUS-01` | no-write | inspect whether project-local policy store is active / missing / stale / conflict |
| `jikuo.get_runtime_status` | `CAP-POLICY-STORE-STATUS-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01` | no governance write | return current policy runtime status as structured data |
| `jikuo.get_runtime_status_card` | `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01` | no governance write; may update `.jikuo/runtime/` | return only the chat-ready runtime status card |
| `jikuo.get_display_card` | `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write | return the latest or requested display card markdown only |
| `jikuo.propose_task_start` | `CAP-AGENT-FLOW-01` plus live policy evaluation atoms | no governance write; may update `.jikuo/runtime/` | return structured task-start proposal data plus card refs / display directives |
| `jikuo.propose_policy_write_plan` | `CAP-POLICY-STORE-WRITE-PROPOSE-01` | no governance write; may update `.jikuo/runtime/` | return proposed policy-store write data plus card refs / display directives before any durable policy write |
| `jikuo.propose_policy_evolution_plan` | `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01` | no governance write; may update `.jikuo/runtime/` | return refinement / deprecation / supersession plan data plus card refs / display directives before any durable write |
| `jikuo.propose_policy_template_import_plan` | `CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01` | no governance write; may update `.jikuo/runtime/` | return resolved template binding data plus card refs / display directives |

Stage B exposes guarded write operations only after Stage A acceptance gates pass.

| Stage B MCP tool | Wrapped atom | Write mode | Product role |
|---|---|---|---|
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
  "runtime_snapshot_ref": ".jikuo/runtime/last_card.md",
  "display_verification": {
    "card_id": "card_47577af64e",
    "runtime_snapshot_path_relative": ".jikuo/runtime/last_card.md",
    "snapshot_written_at_utc": "2026-05-15T00:00:00Z",
    "user_can_verify_with": [
      "jikuo show --last-card",
      "open .jikuo/runtime/last_card.md"
    ]
  }
}
```

Tool descriptions for card-only tools must state that `card_markdown` is governance output and must be displayed verbatim before commentary. If an Agent fails to display `card_markdown`, it must at least surface the `display_verification.user_can_verify_with` path so the user can independently inspect the latest card. This is not a replacement for out-of-band visibility; it is the MCP-facing display contract.

`display_verification.card_id`, `display_verification.runtime_snapshot_path_relative`, `display_verification.snapshot_written_at_utc`, and `display_verification.user_can_verify_with` are `return` fields. Absolute runtime paths remain `local_only` and may be returned only for explicit local desktop `stdio`.

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

0. Confirm `PKG-00`, `CORE-20`, `SEC-01`, `PKG-01`, `CORE-20B`, `CORE-23`, `CORE-24`, `LIVE-12` Phase 1, `INTG-01`, `ARCH-02`, `ARCH-03`, `SDK-01`, `LIVE-19`, `SEC-02`, revised MCP scope acceptance, and any approved minimal package extraction prerequisites are complete or explicitly deferred with user approval.
1. Stage A: create a testable MCP adapter boundary under `src/jikuo/integrations/mcp/` that maps tool names and arguments to package-safe `agent_flow.py` / `policy_store.py` behavior without depending on the MCP SDK.
2. Stage A: add `schemas.py` and adapter tests for the 8 no-write / card / proposal tools.
3. Stage A: add card-only and runtime-status-card tool adapters before broader proposal tools.
4. Stage A: add display directives, `card_priority_order`, `display_verification`, and out-of-band runtime snapshot refs to card-producing tool responses.
5. Stage A: add an MCP server wrapper using the official Python SDK when available; if the SDK is not available locally, stop at the adapter boundary and record the dependency decision rather than hand-rolling a non-compliant server.
6. Stage A: add unit tests for tool schema / argument validation / privacy field classification / display contract shape.
7. Stage A: add integration tests against temporary fixture copies for no-write proposals, resolved project context, runtime visibility snapshots, and the selected active-policy fixture.
8. Stage A: add smoke verification for tool discovery and one no-write card-only tool call.
9. Stage A: update universal and client-specific instruction packs or example configs to prefer MCP when available, while keeping `agent_flow.py` as a fallback.
10. Stage A release gate: verify chat / file / CLI consistency, no hidden governance writes, latency baseline, and at least two available MCP-compatible desktop clients.
11. Stage B: implement guarded write tools only after Stage A gates are accepted.

Stage A module layout:

```text
src/jikuo/integrations/mcp/
  __init__.py
  adapter.py   # pure tool-name to core-API dispatch; importable and testable without MCP SDK
  schemas.py   # tool input/output schema and field classification definitions
  server.py    # MCP protocol wrapper; imports the official SDK only here
```

The first fixture project for Stage A integration tests is `src/jikuo/fixtures/policy_store_active_project`, because it contains an active policy store and can exercise policy evaluation, task-start proposal rendering, card generation, and runtime visibility without requiring guarded writes.

Stage A acceptance gates:

- all 8 Stage A tools pass unit / integration / smoke tests
- no Stage A tool creates `.jikuo/policies/`, creates `.jikuo/task_sessions/`, or updates `.jikuo/project_state.yaml`
- card-producing Stage A tools update only `.jikuo/runtime/` when runtime visibility is enabled
- chat output, `.jikuo/runtime/last_card.md`, and `jikuo show --last-card` expose the same policy runtime status for the same no-write call
- `policy_runtime_status` is the first visible card whenever the wrapped runner produced it
- each no-write tool has a measured latency baseline; `< 3s` is the target for local desktop use
- at least two available MCP-compatible desktop clients are tested before Stage A is accepted for release; if a target client is unavailable, the acceptance log must record the environment limitation rather than silently passing
- supported client MCP configuration examples are recorded with the acceptance artifacts

Stage B must not begin until the Stage A acceptance gates are complete or explicitly revised by the user.

## 7A. MCP Implementation Startup Checklist

MCP implementation must not start until each item is checked, accepted, or explicitly deferred by the user:

- [x] `JIKUO-ARCH-03` API neutrality review accepted.
- [x] `JIKUO-LIVE-16` keeps `policy_runtime_status` first in card display order.
- [x] `JIKUO-LIVE-17` keeps task-session index refresh independent and visible through `jikuo show`.
- [x] `JIKUO-LIVE-18` disables fake previous/latest todo snapshot binding.
- [x] `JIKUO-LIVE-19` backfills official starter policy provenance.
- [x] `JIKUO-SEC-02` defines field-level MCP response privacy classification.
- [ ] User accepts the revised `JIKUO-MCP-01` scope as the implementation scope.
- [x] First fixture project for Stage A MCP integration tests is selected: `src/jikuo/fixtures/policy_store_active_project`.
- [x] MCP SDK dependency posture is decided: keep `adapter.py` SDK-free, use the official SDK only in `server.py` if locally available, and stop at the adapter boundary if unavailable.
- [ ] First implementation PR/slice confirms it will create code under `src/jikuo/integrations/mcp/` only.

Field-level response privacy requirements for the implementation slice:

- every MCP response schema identifies `return`, `local_only`, `redact_required`, and `redact_optional` fields
- `local_only` fields are returned only for explicit local desktop `stdio`
- remote or unknown transports omit `local_only` fields
- `redact_required` fields are never returned as raw values
- starter policy tools refuse or omit records missing provenance

First user-experience acceptance standard:

- In an MCP-compatible desktop client, a governed task-start call must display `policy_runtime_status` before lifecycle or task-session cards.
- The user must be able to open `.jikuo/runtime/last_card.md` or run `jikuo show --last-card` to verify the same card out of band.
- A no-write MCP call must not create `.jikuo/policies/`, `.jikuo/task_sessions/`, or update `.jikuo/project_state.yaml`; only runtime visibility files may update when a card is produced.
- For a single no-write MCP call, chat, `.jikuo/runtime/last_card.md`, and `jikuo show --last-card` must expose the same policy runtime status.
- If the Agent fails to paste `card_markdown`, it must surface `display_verification.user_can_verify_with` so the user can open the out-of-band card.

## 8. Testing Requirements

Unit tests:

- tool name registry and input schema mapping
- `adapter.py` imports and runs without the MCP SDK installed
- no-write proposal calls do not write
- guarded apply calls refuse without confirmation and approval phrase
- policy evolution apply refuses mismatched proposal refs
- every response field is classified as `return`, `local_only`, `redact_required`, or `redact_optional`
- `redact_required` fields replace raw values before return
- `local_only` fields are omitted for non-local or unknown transports
- `display_verification` returns only relative paths / card ids / timestamps / verification commands unless the transport is explicit local desktop `stdio`

Integration tests:

- `jikuo.status` against active / missing policy-store fixtures
- `jikuo.propose_task_start` against `policy_store_active_project`
- `jikuo.get_runtime_status_card` returns card markdown only plus display directives
- `jikuo.get_display_card` returns the last runtime card from `.jikuo/runtime/`
- card-producing proposal tools return display directives where `card_priority_order[0]` is `policy_runtime_status`
- card-producing proposal tools return relative runtime refs as `return` and absolute local paths as `local_only`
- card-producing proposal tools return `display_verification` with user-verifiable commands
- starter policy tools refuse or omit missing-provenance records
- `jikuo.propose_policy_write_plan` returns a no-write card
- `jikuo.propose_policy_evolution_plan` returns a proposal ref
- `jikuo.apply_policy_evolution_write` succeeds only in a copied temporary fixture with matching proposal ref

Smoke tests:

- Stage A MCP tool list exposes only the 8 no-write / card / proposal tools
- one no-write MCP call returns `chat_ready_markdown` plus structured result
- one card-only MCP call returns a compact Markdown card that should be shown verbatim
- `jikuo.propose_task_start` returns `cards[]` containing `policy_runtime_status` when the wrapped runner produced one
- card-producing tools render `policy_runtime_status` before task-session / lifecycle cards when the wrapped runner produced one
- no root `.jikuo/policies/` or `.jikuo/task_sessions/` is created during no-write smoke
- card-producing no-write tools update only the `.jikuo/runtime/` visibility channel when runtime visibility is enabled
- the same no-write call yields matching policy runtime status through chat, `.jikuo/runtime/last_card.md`, and `jikuo show --last-card`
- no-write tool latency is recorded; local desktop target is `< 3s`

Human semantic review:

- confirm the desktop chat result is understandable to a non-CLI user
- confirm the Agent did not summarize away the returned `chat_ready_markdown`
- confirm `policy_runtime_status` appears in the first visible card position before lifecycle, task-session, or write-plan cards
- confirm `display_verification` gives the user an obvious recovery path if the Agent omits the card
- confirm at least two available MCP-compatible desktop clients were tried before accepting Stage A for release, or that missing client access was explicitly recorded
- confirm approval boundaries are visible
- confirm this slice feels like packaging stable atoms, not expanding the governance kernel

## 9. Acceptance Criteria

- The work order, task map, and execution mounts all identify `JIKUO-MCP-01` as the scoped MCP implementation slice, blocked until pre-MCP foundations are accepted.
- The planned implementation path is `src/jikuo/integrations/mcp/`, not root-level `src/jikuo/mcp_server.py` or `src/jikuo/mcp_adapter.py`.
- The MCP MVP tool list is frozen before code implementation starts.
- Stage A and Stage B are separated: Stage A contains the 8 no-write / card / proposal tools; Stage B contains the 3 guarded write tools and cannot start before Stage A gates pass.
- No-write proposal tools return chat-ready text plus structured fields, and policy runtime status remains first-screen visible when present.
- Card-only tools return compact card Markdown and display directives.
- Card-producing tools also update the out-of-band runtime visibility channel or explicitly report why runtime visibility is disabled, and include `display_verification` recovery paths.
- No new governance capability is introduced by this work order.
- The future implementation has explicit unit / integration / smoke / human review requirements.
- MCP implementation is blocked until the pre-MCP portability / security / package / visibility foundation is accepted or explicitly deferred.
