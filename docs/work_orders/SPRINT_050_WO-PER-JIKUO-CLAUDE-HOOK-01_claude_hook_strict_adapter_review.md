# SPRINT_050_WO-PER-JIKUO-CLAUDE-HOOK-01: Claude Hook Strict Adapter Review

> **Status**: Planned; do not implement before Claude host proof and explicit user approval.
> **Date**: 2026-05-17
> **Product meaning**: Determine whether a Claude hook-capable host can make JIKUO run before every user turn, so users who choose mounted mode are not relying on instruction-following alone.

## 1. Why This Task Exists

JIKUO can expose MCP tools and install `CLAUDE.md`, but that only makes the
harness available to Claude. It does not prove that Claude calls JIKUO before
every user turn.

The missing question is:

> Can a Claude hook-capable host run `jikuo.route_user_request` before the model
> handles each ordinary user turn, surface the runtime card, and visibly fail or
> degrade when JIKUO cannot run?

If yes, Claude hook support becomes a strict mounted adapter candidate. If no,
Claude support remains MCP + instruction + proof only until another host
boundary is available.

## 2. Scope

This task verifies and designs, but does not yet implement, a Claude hook
adapter.

In scope:

- identify which Claude host surfaces expose a stable user-turn or prompt-submit
  hook
- distinguish `CLAUDE.md` instruction behavior from hook-enforced pre-turn
  execution
- determine whether the hook can call local MCP or CLI before the model answers
- test whether the hook can surface `card_markdown`, runtime links, and failure
  status back to the user
- define the proof required before marking Claude as strict mounted capable
- design the fallback posture for Claude clients that only support MCP plus
  instructions

Out of scope:

- implementing the hook adapter
- claiming Claude strict mounted support before proof
- adding Claude-specific behavior to the JIKUO kernel
- bypassing activation settings, MCP / CLI routing, runtime visibility, or
  guarded-write approval contracts

## 3. Candidate Outcomes

| Outcome | Meaning | Product Posture |
|---|---|---|
| `strict_pre_turn_supported` | The Claude host has a stable pre-turn hook or equivalent host boundary | Claude hook adapter may become a strict mounted adapter implementation slice |
| `instruction_only_supported` | Claude can use MCP, `CLAUDE.md`, setup prompts, or proof helpers but cannot force pre-turn execution | Keep Claude as onboarding / MCP / proof support and show `degraded_instruction_only` for mounted mode |
| `unsupported_or_unstable` | Hook behavior is unavailable, private, or unstable for this use | Do not build a Claude hook adapter yet; keep using MCP + instruction proof |

## 4. Acceptance Evidence

Before this task can be accepted, record:

- Claude host name, version, OS, and configuration path
- hook event name and when it fires relative to the model turn
- whether the hook can read the current project root and activation settings
- whether the hook can call MCP `jikuo.route_user_request` or CLI fallback
- whether `card_markdown` or runtime links are visible to the user
- whether `.jikuo/runtime/last_card.md` and `jikuo show --last-card` match the
  surfaced card
- whether failure to call JIKUO is visible rather than silently bypassed
- whether no raw transcript, approval phrase, or local-only field leaks
- final classification: strict adapter candidate, instruction-only support, or
  deferred

## 5. Dependencies

- `JIKUO-INTG-03`: strict mounted harness adapter contract
- `JIKUO-INIT-02`: reviewed configuration onboarding
- `JIKUO-MCP-01`: MCP router / policy-suggestion surfaces
- `docs/integrations/mcp_client_proof_playbook.md`: cross-client proof workflow
- private GitHub preview clone proof for realistic user setup

## 6. Boundary

Until this task is accepted with proof, Claude should be described as:

> MCP-capable and instruction-configurable, but not proven as a strict pre-turn
> mounted harness.
