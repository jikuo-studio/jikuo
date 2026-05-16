# SPRINT_050_WO-PER-JIKUO-INTG-02: Client Onboarding Settings And Trigger Mode Selection

> **Status**: Implemented core instruction-distribution support; project-level guarded settings persistence remains planned.
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

The current implemented support is instruction-file based:

```powershell
jikuo install --client codex --trigger-mode ask
jikuo install --client claude-code --trigger-mode semantic
jikuo install --client cursor --trigger-mode mounted
jikuo install --client vscode-copilot --trigger-mode ask
```

`ask` is the safest default for shared projects because it forces the client to
ask the user before the first governed turn.

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

## 5. Remaining Work

- Add guarded project-level persistence for default activation settings.
- Decide whether settings live in `.jikuo/project_context.yaml` first, then split into a dedicated settings file if the shape grows.
- Add MCP router surfaces for `jikuo.route_user_request` and policy-suggestion review.
- Implement the first strict mounted adapter, likely Claude Code `UserPromptSubmit`, after user approval.
- Update client proof docs as each client is verified.

