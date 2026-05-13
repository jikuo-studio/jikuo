# SPRINT_050_WO-PER-JIKUO-MCP-01: MCP Wrapper MVP

> **Status**: Draft, blocked until pre-MCP portability / security / package foundation is accepted
> **Product meaning**: formally move the next phase from more kernel expansion to an MCP wrapper MVP, so desktop Agents can call JIKUO through a stable tool surface while users remain in Codex / Claude desktop chat.
> **Scope rule**: wrap stable atoms only; do not add new governance capability in this slice.

## 1. Why This Slice Now

`JIKUO-LIVE-09` completed the last pre-MCP safety lock: a guarded policy evolution apply must bind to the proposal ref reviewed by the user.

The next useful product step is therefore not another kernel feature. It is to expose the stable runner and guarded apply paths through MCP, so Claude / cross-client desktop Agents can call JIKUO consistently without asking ordinary users to switch to CLI helper orchestration.

This work order freezes the MCP MVP boundary before implementation starts.

Implementation is intentionally blocked until these pre-MCP foundations are accepted:

- `JIKUO-PKG-00`: package boundary and extraction plan
- `JIKUO-CORE-20`: project context binding and policy template portability
- `JIKUO-SEC-01`: trust, privacy, provenance, namespace, principal, telemetry, and timestamp baseline
- `JIKUO-PKG-01`: minimal package extraction before `CORE-20B`
- `JIKUO-CORE-20B`: resource-reference and `CONTRACT_REFS` hygiene inside the extracted package boundary

## 2. User Scenario

Primary scenario:

- The user stays in Codex / Claude desktop APP chat.
- The user asks for a governed task, policy proposal, or approved policy evolution.
- The Agent invokes a JIKUO MCP tool internally.
- The Agent pastes the resulting proposal / apply card and a short summary back into the same chat.
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
- return both chat-ready text and structured result fields where the SDK supports structured content
- keep human approval visible for sensitive write-capable tools
- resolve project-specific document and policy bindings before tool execution; MCP tools must not depend on NarrativeSystem hardcoded paths
- distinguish fields that may be returned to the MCP client from fields that must stay local

## 4. In Scope

Expose these stable operations through a narrow MCP surface:

| MCP tool | Wrapped atom | Write mode | Product role |
|---|---|---|---|
| `jikuo.status` | `CAP-POLICY-STORE-STATUS-01` | no-write | inspect whether project-local policy store is active / missing / stale / conflict |
| `jikuo.propose_task_start` | `CAP-AGENT-FLOW-01` plus live policy evaluation atoms | no-write | render task-start proposal card with triggered policies and evidence status |
| `jikuo.propose_policy_write_plan` | `CAP-POLICY-STORE-WRITE-PROPOSE-01` | no-write | render a proposed policy-store write card before any durable write |
| `jikuo.propose_policy_evolution_plan` | `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01` | no-write | render refinement / deprecation / supersession plan before any durable write |
| `jikuo.apply_task_session_evidence_update` | `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01` | guarded write | append one explicitly approved task-session evidence item |
| `jikuo.apply_policy_evolution_write` | `CAP-POLICY-EVOLUTION-APPLY-BINDING-01` and `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01` | guarded write | apply one approved policy deprecation / supersession only when proposal ref, confirmation, and approval phrase match |

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
| Start governed work | Agent calls `jikuo.propose_task_start`; result includes proposal card, policy context, triggered policies, missing evidence | `CAP-AGENT-FLOW-01`, `CAP-LIVE-DESKTOP-POLICY-EVAL-01`, condition / evidence atoms | no-write; user sees card in chat |
| Configure a new rule | Agent calls `jikuo.propose_policy_write_plan`; user reviews generated policy and write effects | `CAP-POLICY-STORE-WRITE-PROPOSE-01` | no-write proposal only |
| Evolve an existing rule | Agent calls `jikuo.propose_policy_evolution_plan`; user reviews deprecation / supersession effect | `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01` | no-write proposal only |
| Persist approved evidence | Agent calls `jikuo.apply_task_session_evidence_update` with confirmation and approval phrase | `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01` | guarded write to explicit task-session only |
| Apply approved rule evolution | Agent calls `jikuo.apply_policy_evolution_write` with proposal ref, confirmation, and approval phrase | `CAP-POLICY-EVOLUTION-APPLY-BINDING-01`, `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01` | guarded write only after proposal binding passes |

## 7. Implementation Plan

Recommended implementation slices:

0. Confirm `PKG-00`, `CORE-20`, `SEC-01`, `PKG-01`, `CORE-20B`, and any approved minimal package extraction prerequisites are complete or explicitly deferred with user approval.
1. Create a testable MCP adapter boundary that maps tool names and arguments to package-safe `agent_flow.py` / `policy_store.py` behavior.
2. Add an MCP server wrapper using the official Python SDK when available; if the SDK is not available locally, stop at the adapter boundary and record the dependency decision rather than hand-rolling a non-compliant server.
3. Add unit tests for tool schema / argument validation / approval refusal / privacy field classification.
4. Add integration tests against temporary fixture copies for no-write proposals, resolved project context, and guarded apply paths.
5. Add smoke verification for tool discovery and one no-write tool call.
6. Update the desktop-agent instruction pack to prefer MCP when available, while keeping `agent_flow.py` as a fallback.

## 8. Testing Requirements

Unit tests:

- tool name registry and input schema mapping
- no-write proposal calls do not write
- guarded apply calls refuse without confirmation and approval phrase
- policy evolution apply refuses mismatched proposal refs

Integration tests:

- `jikuo.status` against active / missing policy-store fixtures
- `jikuo.propose_task_start` against `policy_store_active_project`
- `jikuo.propose_policy_write_plan` returns a no-write card
- `jikuo.propose_policy_evolution_plan` returns a proposal ref
- `jikuo.apply_policy_evolution_write` succeeds only in a copied temporary fixture with matching proposal ref

Smoke tests:

- MCP tool list exposes only the scoped MVP tools
- one no-write MCP call returns chat-ready text plus structured result
- no root `.jikuo/policies/` or `.jikuo/task_sessions/` is created during no-write smoke

Human semantic review:

- confirm the desktop chat result is understandable to a non-CLI user
- confirm approval boundaries are visible
- confirm this slice feels like packaging stable atoms, not expanding the governance kernel

## 9. Acceptance Criteria

- The work order, task map, and execution mounts all identify `JIKUO-MCP-01` as the scoped MCP implementation slice, blocked until pre-MCP foundations are accepted.
- The MCP MVP tool list is frozen before code implementation starts.
- No new governance capability is introduced by this work order.
- The future implementation has explicit unit / integration / smoke / human review requirements.
- MCP implementation is blocked until the pre-MCP portability / security / package foundation is accepted or explicitly deferred.
