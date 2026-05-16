# INSIGHT-2026-05-16: GUI Agent-Assisted Onboarding Prompt

> **Classification**: deferred  
> **Status**: deferred  
> **Related future task**: `JIKUO-ONBOARD-01`

## Observation

The current MCP client proof path is realistic for private preview validation,
but it still asks the user to run several PowerShell commands:

- clone or download JIKUO
- create a Python virtual environment
- install the package
- verify `jikuo` and `jikuo-mcp`
- configure the desktop AI client
- run proof prompts

That is acceptable for developer-assisted proof, but it is not the desired
ordinary user experience. The target user may be someone with strong product
judgment and clear AI-collaboration needs, but limited engineering comfort.

## Product Insight

Before JIKUO has a full GUI installer or Studio onboarding flow, a good
intermediate product surface is a copy-paste prompt for GUI agents.

The recommended path should become:

1. The user opens a GUI AI client such as Codex, Claude Code, Cursor, or VS Code
   Copilot Agent mode.
2. The user pastes a JIKUO onboarding prompt.
3. The GUI agent performs or guides the setup:
   - clone private/public JIKUO repo or use a downloaded folder
   - create the virtual environment
   - install JIKUO
   - generate or explain MCP configuration
   - verify 17 MCP tools
   - call runtime-card and router proof tools
   - paste the proof result back into chat
4. The user only confirms sensitive or durable steps, such as GitHub
   authentication, dependency installation, config-file writes, or client
   restart.

The command-line path remains available as the transparent fallback and
debugging route, but it should not be the only guided path.

## Design Boundary

This insight does not approve implementation yet.

It should not immediately add:

- installer code
- Studio UI
- client-specific hooks
- automatic MCP config writes
- public release docs that imply command-line setup is the final product UX

It should later influence:

- `docs/integrations/mcp_client_proof_playbook.md`
- a future `docs/integrations/gui_agent_onboarding_prompt.md`
- `JIKUO-ONBOARD-01`
- future Studio / installer design

## Business Meaning

This bridges the gap between "JIKUO is technically usable" and "a non-engineer
can start with JIKUO through the AI client they already use."

It preserves the current private-preview proof discipline while reducing the
felt burden on users. The onboarding prompt can become both:

- a first-use guide
- a proof artifact showing that GUI clients can help users install and mount
  JIKUO without the user personally understanding every command

## Deferred Follow-Up

When this is promoted, define an accepted onboarding prompt that:

- states the user's goal in plain language
- tells the GUI agent which steps require explicit user approval
- forbids storing GitHub credentials or tokens in project files
- supports private GitHub clone and future public package install
- includes a command-line fallback section
- verifies 17 MCP tools
- verifies `jikuo.get_runtime_status_card`
- verifies `jikuo.route_user_request`
- verifies `.jikuo/runtime/last_card.md` or `jikuo show --last-card`
- records whether strict mounted mode is actually supported or only
  instruction-level

