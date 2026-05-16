# SPRINT_050_WO-PER-JIKUO-INTG-03: Strict Mounted Harness Adapter Contract

> **Status**: Contract / planning accepted; implementation deferred to client proof and later adapter slices.
> **Product meaning**: users who choose mounted mode should get real pre-turn JIKUO execution, not just an instruction that the host Agent may or may not follow.
> **Boundary**: this slice defines the adapter contract. It does not implement a Claude hook, Codex plugin, Cursor extension, VS Code extension, Studio proxy, or Agent SDK wrapper.

## 1. Why This Slice Exists

JIKUO now has:

- project activation settings in `.jikuo/activation_settings.yaml`
- visible `semantic` vs `mounted` router behavior
- MCP tools for configuration review, activation settings, conversation routing, and policy suggestions
- instruction files for Codex, Claude Code, Cursor, and VS Code Copilot

That is enough for a client to know how JIKUO should run. It is not enough to
guarantee that JIKUO runs before every user turn.

Strict mounted mode needs an adapter at the boundary where the user turn enters
the host environment.

## 2. Three-Layer Model

| Layer | Responsibility | Current state |
|---|---|---|
| Core | interpret trigger mode, route `conversation_turn`, produce cards, keep writes guarded | implemented |
| MCP / CLI surface | expose configuration, activation settings, router, policy suggestions, and guarded writes to clients | implemented |
| Host adapter | actually call JIKUO before each user turn when mounted mode is active | contract only |

The core must remain integration-neutral. It should not import or depend on a
specific desktop client, IDE, hook system, or Agent SDK.

## 3. Adapter Contract

A strict mounted adapter must:

1. Locate the project root and read `.jikuo/activation_settings.yaml`.
2. If `desired_trigger_mode` is `mounted`, call JIKUO before the host Agent
   handles each user turn.
3. Prefer MCP `jikuo.route_user_request` when available; use CLI
   `python -B -m jikuo.agent_flow propose --event conversation_turn` only as a
   fallback.
4. Pass only the current user turn or a compact user-turn summary. Do not store
   raw chat transcripts.
5. Surface `card_markdown` verbatim when the client can display it.
6. Always surface `.jikuo/runtime/last_card.md` or `jikuo show --last-card` as
   the out-of-band verification path when card display is incomplete.
7. Run required no-write follow-up tools, such as
   `jikuo.propose_policy_suggestions`, before implementation continues when the
   router asks for them.
8. Refuse or visibly degrade when mounted execution cannot run. A mounted
   adapter must not silently continue as if governance happened.
9. Keep durable writes behind existing guarded-write tools that require
   explicit confirmation and approval phrase.

## 4. Client Priority

| Client / host | Near-term route | Strict-mounted status |
|---|---|---|
| Claude Code GUI | MCP + `CLAUDE.md`, then hook proof when hook behavior is stable | best first strict adapter candidate |
| Codex Desktop / Codex CLI | MCP + `AGENTS.md` proof first | strict adapter depends on a stable plugin / hook / app extension point |
| Cursor | MCP + `.cursorrules` proof first | strict adapter depends on a stable extension / hook-like entry |
| VS Code + GitHub Copilot Agent mode | MCP + `.github/copilot-instructions.md` proof first | strict adapter likely needs a VS Code extension or supported agent hook |
| Agent SDK-built agents | wrapper package calls JIKUO before each user turn / agent step | useful for custom agents, not a replacement for desktop GUI proof |
| Studio / local proxy | product-owned entry point routes user turns through JIKUO first | strongest long-term control, deferred until product architecture stabilizes |

## 5. Acceptance Criteria For A Future Adapter Slice

- The adapter reads `.jikuo/activation_settings.yaml` and respects `ask`,
  `semantic`, and `mounted`.
- In mounted mode, a user turn with no obligation still produces a visible
  `mounted_idle_tick`.
- The same runtime card is visible through chat, `.jikuo/runtime/last_card.md`,
  and `jikuo show --last-card`.
- If JIKUO is unavailable, the client receives a visible failure card or clear
  failure message.
- No raw transcript, approval phrase, or local-only response field leaks outside
  the configured transport boundary.
- Guarded writes remain guarded; the adapter cannot convert no-write review
  into durable writes without explicit user approval.

## 6. Current Stop Point

The next slice is not more kernel work. It is client proof:

- verify the current 17-tool MCP surface in the selected GUI clients
- preserve proof artifacts for users
- record which clients support only MCP + instructions and which can support a
  true pre-turn adapter

Implementation of a strict adapter should wait until that proof identifies the
most reliable first host boundary.
