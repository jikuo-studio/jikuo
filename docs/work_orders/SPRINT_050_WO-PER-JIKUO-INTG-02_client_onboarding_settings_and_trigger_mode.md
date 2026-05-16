# SPRINT_050_WO-PER-JIKUO-INTG-02: Client Onboarding Settings And Trigger Mode Selection

> **Status**: Implemented core instruction-distribution support, project-level guarded activation settings persistence, and no-write MCP router surfaces.
> **Product meaning**: when users enable JIKUO in an AI client, they should be asked to choose the operating mode and other activation settings instead of inheriting hidden defaults.
> **Boundary**: instruction files can ask and record client-facing mode choices; strict mounted execution still requires a host adapter such as a hook, plugin, SDK wrapper, Studio entry, or local proxy.

## 1. Why This Slice Exists

JIKUO now distinguishes two operating postures:

- `semantic`: the Agent calls JIKUO when a user turn appears to carry governed work.
- `mounted`: JIKUO is expected to run before every user turn and record an auditable result, including idle ticks when nothing is required.

The mode choice affects user expectations. It must not remain an implicit chat
habit or a default buried in code.

## 2. Activation Settings

When a client first enables JIKUO, the user should review:

- trigger mode: `semantic`, `mounted`, or ask on first use
- MCP server availability
- card-display contract
- runtime visibility links
- guarded-write approval boundary
- starter policy initialization
- project-context bindings

The current implemented support has two layers.

Project-level guarded settings:

```powershell
jikuo settings plan --trigger-mode mounted --client claude-code
jikuo settings apply --trigger-mode mounted --client claude-code --confirm-apply --approval-phrase "<exact user phrase>"
```

The guarded apply writes only:

```text
.jikuo/activation_settings.yaml
```

The file is the project-local activation truth source for later MCP tools,
hooks, plugins, SDK wrappers, and Studio / proxy adapters. `jikuo show`,
`jikuo install`, and the conversation-turn router read it when no explicit mode
override is supplied.

Instruction-file support:

```powershell
jikuo install --client codex --trigger-mode ask
jikuo install --client claude-code --trigger-mode semantic
jikuo install --client cursor --trigger-mode mounted
jikuo install --client vscode-copilot --trigger-mode ask
```

`ask` is the safest default for shared projects because it forces the client to
ask the user before the first governed turn. If `--trigger-mode` is omitted,
`jikuo install` reads `.jikuo/activation_settings.yaml` and falls back to `ask`
when that file is missing.

## 3. Client Support Matrix

| Client | Current support | Trigger-mode specification | Strict mounted status |
|---|---|---|---|
| Codex Desktop / Codex CLI | MCP + `AGENTS.md` instruction block | `jikuo install --client codex --trigger-mode ask|semantic|mounted` | Not strict until a Codex plugin / hook / app adapter exists |
| Claude Code GUI | MCP + `CLAUDE.md`; future hook target | `jikuo install --client claude-code --trigger-mode ask|semantic|mounted` | Best first strict proof through `UserPromptSubmit` hook |
| Cursor | MCP + `.cursorrules` | `jikuo install --client cursor --trigger-mode ask|semantic|mounted` | Not strict until a Cursor extension / hook-like adapter exists |
| VS Code + GitHub Copilot Agent mode | MCP + `.github/copilot-instructions.md` | `jikuo install --client vscode-copilot --trigger-mode ask|semantic|mounted` | Not strict until a VS Code extension / agent hook-like adapter exists |

MCP plus instruction files means "available and instructed." It does not mean
"guaranteed to run before every user turn."

## 4. Core Behavior Difference

Core routing now exposes a visible difference between the modes:

- `semantic` with no matching obligation returns `no_jikuo_action_required`
- `mounted` with no matching obligation returns `mounted_idle_tick`

This makes mounted mode auditable even when no policy, task, insight, or
follow-up action is required.

## 5. Implemented Artifacts

- `src/jikuo/activation_settings.py`: no-write plan, guarded apply, status, rendering, and default resolution.
- `jikuo settings status|plan|apply`: top-level CLI entry.
- `jikuo show`: includes activation settings status.
- `jikuo install`: reads project activation settings when `--trigger-mode` is omitted.
- `agent_flow.py propose --event conversation_turn`: reads project activation settings when `--trigger-mode` is omitted; `ask` resolves to semantic behavior until a strict adapter asks the user.
- MCP router tools: `jikuo.route_user_request` and
  `jikuo.propose_policy_suggestions` expose the same no-write routing and
  policy-candidate review inside desktop AI clients.
- `tests/activation_settings_tests.py`: plan/apply/refusal/default-resolution/show coverage.

## 6. Remaining Work

- MCP router surfaces are now implemented: `jikuo.route_user_request` and
  `jikuo.propose_policy_suggestions`.
- MCP activation settings tools are now implemented: `jikuo.get_activation_settings`, `jikuo.plan_activation_settings_update`, and guarded `jikuo.apply_activation_settings_update`.
- Strict mounted adapter boundaries are recorded in
  `SPRINT_050_WO-PER-JIKUO-INTG-03_strict_mounted_harness_adapter_contract.md`.
- Complete client proof for Codex, Claude Code GUI, Cursor, and VS Code +
  GitHub Copilot Agent mode before choosing the first strict adapter host.
- Implement the first strict mounted adapter after client proof and explicit
  user approval.
- Update client proof docs as each client is verified.
