# SPRINT_050_WO-PER-JIKUO-CODEX-PLUGIN-01: Codex Plugin Pre-Turn Harness Review

> **Status**: Planned; do not implement before client proof and explicit user approval.
> **Date**: 2026-05-16
> **Product meaning**: Determine whether a Codex plugin can make JIKUO run before every user turn, or whether it should only ship as an instruction / MCP setup aid. This prevents JIKUO from claiming strict mounted behavior that Codex cannot actually enforce.

## 1. Why This Task Exists

JIKUO can expose MCP tools and install Codex instructions, but those surfaces are
not automatically strict mounted execution.

The missing question is:

> Can a Codex plugin intercept or participate in every user turn before the
> model performs ordinary work?

If yes, a Codex plugin may become a strict mounted adapter candidate. If no, the
Codex plugin should be limited to instruction-packaging, MCP configuration,
proof capture, and runtime verification shortcuts.

## 2. Scope

This task verifies and designs, but does not yet implement, a Codex plugin
integration.

In scope:

- inspect the currently supported Codex plugin surfaces
- distinguish skills / instructions from pre-turn hooks
- determine whether a plugin can call `jikuo.route_user_request` before every user turn
- identify what proof is required before marking Codex as strict mounted capable
- design a safe fallback plugin that improves setup without claiming strictness

Out of scope:

- implementing the plugin
- claiming Codex strict mounted support before proof
- adding Codex plugin behavior to the JIKUO kernel
- bypassing MCP / activation settings / runtime visibility contracts

## 3. Candidate Outcomes

| Outcome | Meaning | Product Posture |
|---|---|---|
| `strict_pre_turn_supported` | Codex plugin has a stable pre-turn hook or equivalent host boundary | Codex plugin may be promoted to first strict mounted adapter candidate |
| `instruction_only_supported` | Plugin can provide skills, instructions, MCP setup, or UI affordances but cannot force pre-turn execution | Ship as onboarding / proof / helper plugin only; show `degraded_instruction_only` for mounted mode |
| `unsupported_or_unstable` | Plugin API is unavailable, private, or unstable for this use | Do not build Codex plugin yet; keep using MCP + instruction proof |

## 4. Acceptance Evidence

Before this task can be accepted, record:

- Codex app / CLI version and OS
- plugin manifest capabilities actually available
- whether pre-turn or user-prompt hook behavior exists
- whether the plugin can call local MCP or CLI before the model answers
- whether the same runtime card is visible in chat and `.jikuo/runtime/last_card.md`
- whether failure to call JIKUO is visible to the user
- final classification: strict adapter candidate, instruction-only plugin, or deferred

## 5. Dependencies

- `JIKUO-INTG-03`: strict mounted harness adapter contract
- `JIKUO-INIT-02`: reviewed configuration onboarding
- `docs/integrations/mcp_client_proof_playbook.md`: cross-client proof workflow
- private GitHub preview clone proof for realistic user setup

## 6. Boundary

Until this task is accepted with proof, Codex should be described as:

> MCP-capable and instruction-configurable, but not proven as a strict pre-turn
> mounted harness.

