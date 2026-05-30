# SPRINT_050_WO-PER-JIKUO-MCP-01: MCP Wrapper MVP

> **Status**: MCP MVP body implemented and release-smoked; Stage A server wrapper accepted; Stage B1 task-session evidence guarded-write tool implemented after explicit user approval; Stage B2 policy evolution guarded-write tool implemented and externally smoke-accepted; Stage B3 policy-template activation guarded-write tool implemented and externally smoke-accepted; post-MVP configuration status, activation settings read / plan / apply, router tools, no-write MCP Sampling semantic-provider probe, policy publication bridge tools, and policy-management status read model implemented
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

Stage A exposes only no-write / card-returning operations. Post-MVP read-only
configuration status uses the same no-governance-write boundary. These tools
may update `.jikuo/runtime/` when they produce runtime visibility, but they must
not create `.jikuo/policies/`, create `.jikuo/task_sessions/`, or update
`.jikuo/project_state.yaml`.

| No-write MCP tool | Wrapped atom | Write mode | Product role |
|---|---|---|---|
| `jikuo.status` | `CAP-POLICY-STORE-STATUS-01` | no-write | inspect whether project-local policy store is active / missing / stale / conflict |
| `jikuo.get_policy_management_status` | `CAP-POLICY-MANAGEMENT-STATUS-READ-01` | no-write | return the Policy Management MVP read model for GUI/front-end surfaces, including active policies, package templates, starter manifests, and available guarded follow-ups |
| `jikuo.get_runtime_status` | `CAP-POLICY-STORE-STATUS-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01` | no governance write | return current policy runtime status as structured data |
| `jikuo.get_runtime_status_card` | `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01` | no governance write; may update `.jikuo/runtime/` | return only the chat-ready runtime status card |
| `jikuo.get_display_card` | `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write | return the latest or requested display card markdown only |
| `jikuo.propose_task_start` | `CAP-AGENT-FLOW-01` plus live policy evaluation atoms | no governance write; may update `.jikuo/runtime/` | return structured task-start proposal data plus card refs / display directives |
| `jikuo.propose_policy_write_plan` | `CAP-POLICY-STORE-WRITE-PROPOSE-01` | no governance write; may update `.jikuo/runtime/` | return proposed policy-store write data plus card refs / display directives before any durable policy write |
| `jikuo.propose_policy_evolution_plan` | `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01` | no governance write; may update `.jikuo/runtime/` | return refinement / deprecation / supersession plan data, including replacement trigger event, plus card refs / display directives before any durable write |
| `jikuo.propose_policy_template_import_plan` | `CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01` | no governance write; may update `.jikuo/runtime/` | return resolved template binding data plus card refs / display directives |
| `jikuo.get_configuration_status` | `CAP-CONFIGURATION-REVIEW-01` | no governance write; may update `.jikuo/runtime/` | return first-use configuration review state plus card refs / display directives |
| `jikuo.get_activation_settings` | `CAP-MCP-ACTIVATION-SETTINGS-READ-PLAN-01` | no governance write; may update `.jikuo/runtime/` | return current project activation settings status |
| `jikuo.plan_activation_settings_update` | `CAP-MCP-ACTIVATION-SETTINGS-READ-PLAN-01` | no governance write; may update `.jikuo/runtime/` | return a reviewed activation settings update plan without writing `.jikuo/activation_settings.yaml` |
| `jikuo.route_user_request` | `CAP-CONVERSATION-TURN-ROUTER-01`; `CAP-MCP-CONVERSATION-ROUTER-SURFACE-01` | no governance write; may update `.jikuo/runtime/` | classify one user turn into JIKUO obligations and MCP follow-up tools |
| `jikuo.propose_policy_suggestions` | `CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01`; `CAP-MCP-CONVERSATION-ROUTER-SURFACE-01` | no governance write; may update `.jikuo/runtime/` | return reviewable policy-candidate suggestions from a user turn without writing policy files |
| `jikuo.probe_sampling_semantic_intent` | `CAP-MCP-SAMPLING-SEMANTIC-PROVIDER-01`; `CAP-HOST-SEMANTIC-INTENT-WORK-PROFILE-01`; `CAP-CONVERSATION-TURN-ROUTER-01` | no governance write; may update `.jikuo/runtime/` | ask a Sampling-capable MCP client for compact semantic intent, then route the turn through JIKUO; cleanly reports unavailable when Sampling is unsupported |

Stage B exposes guarded write operations only after Stage A acceptance gates pass.
Stage B1 is accepted for task-session evidence writes. Stage B2 is accepted for
policy evolution deprecation / supersession writes with proposal-ref binding.
Stage B3 is accepted for one resolved policy-template activation after the user
reviews the template import plan and supplies confirmation plus approval phrase.

| Stage B MCP tool | Wrapped atom | Write mode | Product role |
|---|---|---|---|
| `jikuo.apply_task_session_evidence_update` | `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01` | guarded write | append one explicitly approved task-session evidence item |
| `jikuo.apply_policy_evolution_write` | `CAP-POLICY-EVOLUTION-APPLY-BINDING-01` and `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01` | guarded write | apply one approved policy deprecation / supersession only when proposal ref, replacement trigger event, confirmation, and approval phrase match |
| `jikuo.apply_policy_template_activation` | `CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01` | guarded write | activate one approved resolved template only after bindings, confirmation, and approval phrase match |

Post-MVP configuration writes expose a separate guarded settings surface. This
tool is not a Stage A no-write tool; it writes only the reviewed activation
settings file after explicit user confirmation.

| Configuration guarded-write MCP tool | Wrapped atom | Write mode | Product role |
|---|---|---|---|
| `jikuo.apply_activation_settings_update` | `CAP-MCP-ACTIVATION-SETTINGS-APPLY-01` | guarded write | write reviewed activation settings only after confirmation and approval phrase |

Display response contract for card-returning tools:

```json
{
  "display": {
    "must_show_verbatim": ["card_markdown"],
    "card_priority_order": [
      "policy_runtime_status",
      "conversation_turn_router",
      "configuration_review",
      "policy_suggestion_review",
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
- dashboard / Studio UI beyond runtime card links
- Codex Plugin packaging
- product-output quality judgment
- hidden writes outside the existing guarded apply operations

## 6. Scenario Chain And Atom Composition

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Inspect project governance state | Agent calls `jikuo.status`; Agent returns structured status and short summary | `CAP-POLICY-STORE-STATUS-01` | no-write; no `.jikuo` creation |
| Inspect policy-management distribution state | Agent calls `jikuo.get_policy_management_status`; Agent returns active-policy / template / starter-pack read model | `CAP-POLICY-MANAGEMENT-STATUS-READ-01` | no-write; no runtime, policy, starter, or project-state write |
| Display latest card | Agent calls `jikuo.get_display_card` or `jikuo.get_runtime_status_card`; Agent outputs `card_markdown` verbatim | `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; card can be verified out of band |
| Start governed work | Agent calls `jikuo.propose_task_start`; result includes proposal data, policy context, triggered policies, missing evidence, display directives, and runtime card refs | `CAP-AGENT-FLOW-01`, `CAP-LIVE-DESKTOP-POLICY-EVAL-01`, condition / evidence atoms, `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; runtime snapshot may update |
| Configure a new rule | Agent calls `jikuo.propose_policy_write_plan`; user reviews generated policy and write effects through a display card | `CAP-POLICY-STORE-WRITE-PROPOSE-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; runtime snapshot may update |
| Evolve an existing rule | Agent calls `jikuo.propose_policy_evolution_plan`; user reviews deprecation / supersession effect and replacement trigger event through a display card | `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; runtime snapshot may update |
| Adopt a reusable policy template | Agent calls `jikuo.propose_policy_template_import_plan`; user reviews resolved bindings, write targets, and generated activation command | `CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01`, `CAP-POLICY-TEMPLATE-IMPORT-PLAN-01`, `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no governance write; runtime snapshot may update |
| Persist approved evidence | Agent calls `jikuo.apply_task_session_evidence_update` with confirmation and approval phrase | `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01` | guarded write to explicit task-session only |
| Apply approved rule evolution | Agent calls `jikuo.apply_policy_evolution_write` with proposal ref, confirmation, and approval phrase | `CAP-POLICY-EVOLUTION-APPLY-BINDING-01`, `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01` | guarded write only after proposal binding passes |
| Apply approved policy-template activation | Agent calls `jikuo.apply_policy_template_activation` with template path, confirmation, and approval phrase | `CAP-POLICY-TEMPLATE-ACTIVATE-01`, `CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01` | guarded write only after bindings resolve |
| Probe client semantic sampling | Agent calls `jikuo.probe_sampling_semantic_intent`; MCP server requests `sampling/createMessage` from the client when supported, then routes through JIKUO | `CAP-MCP-SAMPLING-SEMANTIC-PROVIDER-01`, `CAP-HOST-SEMANTIC-INTENT-WORK-PROFILE-01`, `CAP-CONVERSATION-TURN-ROUTER-01` | no governance write; not strict mounted proof; prompt echoes must be redacted from returned proof data |

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
- [x] User accepts the revised `JIKUO-MCP-01` Stage A scope as the implementation scope.
- [x] First fixture project for Stage A MCP integration tests is selected: `src/jikuo/fixtures/policy_store_active_project`.
- [x] MCP SDK dependency posture is decided: keep `adapter.py` SDK-free, use the official SDK only in `server.py`, and declare the official Python `mcp` SDK dependency for the MCP server entry point.
- [x] First implementation slice created code under `src/jikuo/integrations/mcp/` only.

Stage A implementation progress:

- [x] `src/jikuo/integrations/mcp/schemas.py` defines the 8 Stage A tools, Stage B non-exposed guarded tools, display directives, and response field classifications.
- [x] `src/jikuo/integrations/mcp/adapter.py` dispatches Stage A tool calls to structured core APIs without importing an MCP SDK or calling CLI `main()`.
- [x] Card-producing Stage A adapter responses include `card_markdown`, display directives, `runtime_snapshot_ref`, and `display_verification`.
- [x] Unknown / non-local transports sanitize local project paths from returned payloads; explicit `local_stdio` may return `local_paths`.
- [x] Unit coverage verifies Stage A tool listing, no hidden task-session / policy writes, runtime-only visibility updates, card-only runtime status output, latest-card retrieval, and privacy sanitization.
- [x] Local SDK availability was checked on 2026-05-15: neither `mcp` nor `modelcontextprotocol` is importable in the current Python environment.
- [x] User approved declaring the official Python MCP SDK dependency (`mcp`) and implementing `src/jikuo/integrations/mcp/server.py`.
- [x] `pyproject.toml` declares dependency `mcp` and exposes `jikuo-mcp = "jikuo.integrations.mcp.server:main"`.
- [x] `src/jikuo/integrations/mcp/server.py` lazily imports `mcp.server.fastmcp.FastMCP`, registers the 8 Stage A tools, embeds the display contract in card-returning tool descriptions, and delegates all tool behavior to `adapter.call_tool`.
- [x] Server-wrapper unit coverage uses a fake FastMCP object so registration, display-contract descriptions, and adapter delegation remain testable without the SDK installed in the current environment.
- [x] Real SDK import / module-entry smoke passed after installing the declared dependency in the user environment: `mcp.server.fastmcp.FastMCP` imports, `create_server()` returns a real `FastMCP` instance, and `python -B -m jikuo.integrations.mcp.server --help` works.
- [x] Official Python SDK `ClientSession` stdio smoke passed in an external Codex window: `python -B -m jikuo.integrations.mcp.server` listed the 8 Stage A tools and called `jikuo.get_runtime_status_card`.
- [x] External smoke found that `get_runtime_status_card.card_markdown` returned a single policy card while `.jikuo/runtime/last_card.md` and `jikuo show --last-card` showed the full proposal; fixed by making the card-only tool persist the same single-card Markdown to runtime visibility.
- [x] Unit coverage verifies `jikuo.get_runtime_status_card.card_markdown`, `.jikuo/runtime/last_card.md`, and `runtime_visibility.load_last_card()` are byte-for-byte equal for the card-only runtime status call.
- [x] Stage A client configuration examples are recorded in `docs/integrations/mcp_client_configuration_examples.md`.
- [x] Real desktop-client configuration smoke and two-client release gate passed by user verification in Codex Desktop and Claude Desktop on 2026-05-15; local temporary directories may remain under ignored project paths such as `.claude/` and `tmp/`.
- [x] Stage B1 user approval recorded on 2026-05-15: implement only `jikuo.apply_task_session_evidence_update`; do not implement policy evolution or policy-template activation tools in that slice.
- [x] `src/jikuo/integrations/mcp/schemas.py` exposes the 8 Stage A tools plus the accepted Stage B1 guarded-write tool.
- [x] `src/jikuo/integrations/mcp/adapter.py` wraps `agent_flow.build_apply_result(operation="task_session_evidence_update")`, preserves the guarded confirmation / approval phrase boundary, writes only the target task-session on success, and updates runtime visibility for the returned apply card.
- [x] `src/jikuo/integrations/mcp/server.py` registers `jikuo.apply_task_session_evidence_update` through the official FastMCP wrapper while continuing to delegate behavior to the SDK-free adapter.
- [x] Unit coverage verifies Stage B1 refusal without confirmation / approval phrase, success after approval, no policy-store or project-state writes, approval phrase non-disclosure, runtime visibility projection, and continued non-registration for Stage B3.
- [x] Official Python SDK `ClientSession` stdio smoke passed for Stage B1: during the B1 slice, the server listed 9 tools, exposed `jikuo.apply_task_session_evidence_update`, did not expose Stage B2 / B3 tools, and successfully appended one task-session evidence item without returning the approval phrase.
- [x] Stage B2 user approval recorded on 2026-05-15: continue MCP Stage B by exposing only `jikuo.apply_policy_evolution_write`; dashboard / Studio UI remains deferred, and current visibility relies on card markdown plus runtime card links.
- [x] During the Stage B2 slice, `src/jikuo/integrations/mcp/schemas.py` exposed `jikuo.apply_policy_evolution_write` as the accepted Stage B2 guarded-write tool while `jikuo.apply_policy_template_activation` remained absent from the MCP tool list.
- [x] `src/jikuo/integrations/mcp/adapter.py` wraps `agent_flow.build_apply_result(operation="policy_evolution_write")`, preserves proposal-ref binding, confirmation, and approval phrase checks, and updates runtime visibility for the returned apply card.
- [x] `src/jikuo/integrations/mcp/server.py` registers `jikuo.apply_policy_evolution_write` through the official FastMCP wrapper while continuing to delegate behavior to the SDK-free adapter.
- [x] Unit coverage verifies Stage B2 refusal without confirmation / approval phrase / proposal ref, success after proposal-bound approval, no task-session writes, approval phrase non-disclosure, runtime visibility projection, and continued non-registration for Stage B3.
- [x] External Claude-assisted Stage B2 acceptance on 2026-05-16 passed: adapter and FastMCP wrapper both listed 10 tools, `jikuo.apply_policy_evolution_write` refused unapproved calls, applied one proposal-bound supersession with `proposal_binding.status=ok`, did not create `.jikuo/task_sessions/`, did not leak the raw approval phrase, wrote `.jikuo/runtime/last_card.md` in the fixture project, and kept `jikuo.apply_policy_template_activation` absent from the tool list during that slice.
- [x] Stage B3 user approval recorded on 2026-05-16: continue MCP Stage B by exposing `jikuo.apply_policy_template_activation`; license route remains deferred and dashboard / Studio UI remains out of scope.
- [x] `src/jikuo/integrations/mcp/schemas.py` exposes `jikuo.apply_policy_template_activation` as the accepted Stage B3 guarded-write tool.
- [x] `src/jikuo/integrations/mcp/adapter.py` wraps `agent_flow.build_apply_result(operation="policy_template_activation")`, preserves confirmation and approval phrase checks, activates only one resolved template, and updates runtime visibility for the returned apply card.
- [x] `src/jikuo/integrations/mcp/server.py` registers `jikuo.apply_policy_template_activation` through the official FastMCP wrapper while continuing to delegate behavior to the SDK-free adapter.
- [x] Unit coverage verifies Stage B3 refusal without confirmation / approval phrase, success after approval, no task-session writes, approval phrase non-disclosure, runtime visibility projection, and project-local approved policy activation.
- [x] External Claude Code GUI acceptance on 2026-05-16 passed: adapter and FastMCP wrapper both listed 11 tools, `jikuo.apply_policy_template_activation` refused unapproved calls without creating `.jikuo/policies/`, activated one resolved template after approval, wrote proposal snapshot / approved policy / decision record / manifest, did not create `.jikuo/task_sessions/`, did not leak the raw approval phrase, wrote `.jikuo/runtime/last_card.md` in the fixture project, and showed no GUI MCP client tool-list cache issue.
- [x] MCP client configuration examples were updated after Stage B3 to describe the current 11-tool MVP surface, Stage B2 / B3 smoke checks, guarded write boundaries, approval phrase redaction checks, and fixture-first apply-path guidance.
- [x] Final local official SDK release smoke passed on 2026-05-16: a Python MCP `ClientSession` launched `python -B -m jikuo.integrations.mcp.server`, listed all 11 MVP tools, called `jikuo.get_runtime_status_card` against a temporary fixture project, and confirmed returned `card_markdown` matched `.jikuo/runtime/last_card.md`.
- [x] Post-MVP configuration status read surface implemented: `jikuo.get_configuration_status` wraps `agent_flow propose --event configuration_review`, returns `jikuo.configuration_review.v0`, and writes only runtime visibility.
- [x] Post-MVP activation settings read / plan surface implemented: `jikuo.get_activation_settings` returns `jikuo.activation_settings_status.v0`; `jikuo.plan_activation_settings_update` returns `jikuo.activation_settings_plan.v0`; neither writes `.jikuo/activation_settings.yaml`; this initially expanded tool discovery to 14 tools before the guarded apply surface was accepted.
- [x] Post-MVP activation settings guarded apply surface implemented after explicit user approval: `jikuo.apply_activation_settings_update` refuses without confirmation / approval phrase, writes only `.jikuo/activation_settings.yaml` on success, redacts the raw approval phrase, and previously expanded tool discovery to 15 tools before router tools were accepted.
- [x] Post-MVP router surface implemented after configuration acceptance: `jikuo.route_user_request` wraps the no-write `conversation_turn` router and returns MCP follow-up tools; `jikuo.propose_policy_suggestions` exposes `jikuo.proactive_policy_suggestion_review.v0` candidates; both preserve display directives, runtime links, SEC-02 field classification, and no-write boundaries; current tool discovery expanded to 17 tools before the Sampling probe slice.
- [x] MCP Sampling semantic provider proof implemented as a no-write post-MVP tool: `jikuo.probe_sampling_semantic_intent` uses the official SDK `ctx.session.create_message()` path when a client supports `sampling/createMessage`, asks for compact `host_semantic_intent`, redacts prompt echoes from returned proof data, routes through existing `jikuo.route_user_request`, and reports `sampling_semantic_intent.status=unavailable` when Sampling is unsupported or invalid; current tool discovery expands to 18 tools.
- [x] Local official SDK smoke on 2026-05-20 listed 18 tools, verified the Sampling tool input schema does not expose the injected `ctx` parameter, and called `jikuo.probe_sampling_semantic_intent` through `ClientSession`; the local client returned `sampling_semantic_intent.status=unavailable` and did not echo the probe prompt.
- [x] Policy distribution review GUI/MCP proposal surface implemented as a no-write post-MVP tool: `jikuo.propose_policy_distribution_review` accepts `policy_ref`, `source_policy`, or natural-language `policy_query`, resolves candidate active policies without writing files, returns a visible distribution review card, and keeps template export / starter publication as separate guarded follow-up; this expanded tool discovery to 19 tools.
- [x] Policy publication bridge surface implemented as post-MVP tools: `jikuo.propose_policy_template_publication_plan` / `jikuo.apply_policy_template_publication` expose package-template publication through no-write review plus guarded apply, while `jikuo.propose_starter_manifest_publication_plan` / `jikuo.apply_starter_manifest_publication` expose starter-manifest publication as a separate guarded path; this previously expanded tool discovery to 23 tools.
- [x] Policy-management status read model implemented as a no-write post-MVP tool: `jikuo.get_policy_management_status` returns active policy inventory, package-template inventory, starter-pack manifest state, distribution-state summaries, and available guarded follow-up operations for GUI/front-end use; current source tool discovery expands to 24 tools.

Stage A desktop-client acceptance log:

- 2026-05-15: user verified the Stage A MCP server from Codex Desktop and Claude Desktop desktop applications.
- Evidence boundary: this is user-verified desktop smoke, not a captured tool log from this Codex thread.
- Expected local byproducts: desktop-client and test-environment temporary directories under ignored paths, including `.claude/` and `tmp/`.
- Acceptance effect: satisfies the two-client Stage A desktop smoke release gate.
- Non-effect: does not accept or start Stage B guarded-write tools.

SDK dependency decision record:

- official reference used for dependency posture: `https://modelcontextprotocol.io/docs/sdk`
- official Python SDK package / import path to verify before `server.py`: `mcp`
- expected server wrapper import path from official Python SDK examples: `mcp.server.fastmcp.FastMCP`
- current local environment result: `importlib.util.find_spec("mcp") == None`
- user decision on 2026-05-15: approve declaring the official Python MCP SDK dependency and implementing `server.py`
- current implementation decision: do not hand-roll an MCP protocol server; `server.py` is a thin official-SDK wrapper over the SDK-free adapter boundary
- pyproject status: runtime dependency `mcp` is declared; the user environment installed `mcp 1.27.1` during this slice for smoke verification

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
- For `jikuo.get_runtime_status_card`, chat, `.jikuo/runtime/last_card.md`, and `jikuo show --last-card` must expose the same single-card Markdown byte-for-byte.
- For broader proposal tools, chat, `.jikuo/runtime/last_card.md`, and `jikuo show --last-card` must expose the same complete proposal Markdown with policy runtime status first when present.
- If the Agent fails to paste `card_markdown`, it must surface `display_verification.user_can_verify_with` so the user can open the out-of-band card.

## 8. Testing Requirements

Unit tests:

- tool name registry and input schema mapping
- `adapter.py` imports and runs without the MCP SDK installed
- no-write proposal calls do not write
- guarded apply calls refuse without confirmation and approval phrase
- policy evolution apply refuses mismatched proposal refs, including mismatches caused by a different replacement trigger event
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
- `jikuo.propose_policy_evolution_plan` returns a proposal ref in the policy evolution plan card
- `jikuo.apply_task_session_evidence_update` refuses without confirmation / approval phrase and succeeds only against an explicit task-session after approval
- official SDK stdio smoke verifies the Stage B1 tool through a real MCP `ClientSession`
- `jikuo.apply_policy_evolution_write` refuses without confirmation / approval phrase / proposal ref and succeeds only against a copied temporary fixture with a matching proposal ref
- `jikuo.apply_policy_template_activation` refuses without confirmation / approval phrase and succeeds only against a project with resolved `.jikuo/project_context.yaml` bindings
- external acceptance artifacts may be stored under ignored `tmp/` paths and must not be treated as product source

Smoke tests:

- Stage A MCP tool list exposes only the 8 no-write / card / proposal tools
- one no-write MCP call returns `chat_ready_markdown` plus structured result
- one card-only MCP call returns a compact Markdown card that should be shown verbatim
- the card-only runtime status call writes that same compact Markdown card to `.jikuo/runtime/last_card.md`
- `jikuo.propose_task_start` returns `cards[]` containing `policy_runtime_status` when the wrapped runner produced one
- card-producing tools render `policy_runtime_status` before task-session / lifecycle cards when the wrapped runner produced one
- no root `.jikuo/policies/` or `.jikuo/task_sessions/` is created during no-write smoke
- card-producing no-write tools update only the `.jikuo/runtime/` visibility channel when runtime visibility is enabled
- the same no-write call yields matching policy runtime status through chat, `.jikuo/runtime/last_card.md`, and `jikuo show --last-card`
- no-write tool latency is recorded; local desktop target is `< 3s`
- client configuration examples are available for users to reproduce local stdio setup without depending on this development machine's environment

Human semantic review:

- confirm the desktop chat result is understandable to a non-CLI user
- confirm the Agent did not summarize away the returned `chat_ready_markdown`
- confirm `policy_runtime_status` appears in the first visible card position before lifecycle, task-session, or write-plan cards
- confirm `display_verification` gives the user an obvious recovery path if the Agent omits the card
- confirm at least two available MCP-compatible desktop clients were tried before accepting Stage A for release, or that missing client access was explicitly recorded
- confirm approval boundaries are visible
- confirm this slice feels like packaging stable atoms, not expanding the governance kernel

Final MCP MVP body smoke:

- official SDK `ClientSession` can discover all 11 MVP tools
- `jikuo.get_runtime_status_card` returns the expected compact runtime status card
- the temporary fixture project's `.jikuo/runtime/last_card.md` matches the returned card Markdown
- no Stage A no-write call writes policy or task-session state

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

Post-MVP expansion remains separate:

- no MCP B4 or broader guarded-write tool should be added without explicit user approval
- dashboard / Studio, Agent SDK adapters, per-client hook packs, Plugin packaging, rollback, broader condition vocabulary, and gates remain outside MCP MVP body scope
