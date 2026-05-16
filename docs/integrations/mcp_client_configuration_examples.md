# JIKUO MCP Client Configuration Examples

> Status: MCP MVP local stdio configuration examples and smoke-log companion.
> Scope: local stdio MCP clients only. Current MVP exposes 11 tools: 8 Stage A
> no-write / card / proposal tools plus Stage B1 / B2 / B3 guarded-write tools.

## Purpose

This file records reusable client configuration examples for the JIKUO MCP MVP
server and the smoke checks needed to verify a desktop client is seeing the
current tool surface.

Source references:

- Claude Code MCP docs: `https://code.claude.com/docs/en/mcp`
- Cursor MCP docs: `https://docs.cursor.com/advanced/model-context-protocol`
- OpenAI Docs MCP / Codex setup reference: `https://developers.openai.com/learn/docs-mcp`

Use these examples after installing JIKUO in the Python environment that will launch the server:

```powershell
python -m pip install -e .
```

The server entry point is:

```powershell
python -B -m jikuo.integrations.mcp.server
```

Prefer an explicit Python executable from a project virtual environment when configuring desktop clients. That avoids relying on the client process inheriting the same `PATH` or user-site packages as the terminal.

## Placeholders

- `<PROJECT_ROOT>`: absolute path to the project using JIKUO, for example `D:\personal_project\Jikuo`
- `<PYTHON_EXE>`: Python executable with `jikuo` and `mcp` installed, for example `<PROJECT_ROOT>\tmp\mcp-stage-a-venv\Scripts\python.exe`

## Trigger Mode And Client Onboarding

JIKUO has two trigger modes:

- `semantic`: the Agent calls JIKUO when a user turn appears to carry governed work.
- `mounted`: a supported client adapter calls JIKUO before every user turn and shows an auditable result, including `mounted_idle_tick` when nothing is required.

MCP configuration makes JIKUO tools available. Instruction files tell the Agent
when to use them. Neither one alone is a strict mounted harness unless the
client also has a pre-turn hook / plugin / SDK wrapper / Studio entry / local
proxy.

Use `jikuo install` to write the client-facing mode into instruction files:

```powershell
jikuo install --client codex --trigger-mode ask
jikuo install --client claude-code --trigger-mode semantic
jikuo install --client cursor --trigger-mode mounted
jikuo install --client vscode-copilot --trigger-mode ask
```

`ask` is the safest default: the client must ask the user to choose semantic or
mounted mode before the first governed turn.

## Claude Code

Claude Code supports adding stdio MCP servers from the CLI. Use a local or project scope depending on whether the configuration should stay private or be shared.

```powershell
claude mcp add-json jikuo '{ "type": "stdio", "command": "<PYTHON_EXE>", "args": ["-B", "-m", "jikuo.integrations.mcp.server"], "env": {} }'
```

If the server should be committed as project configuration, use Claude Code's project-scoped MCP configuration workflow and review the generated file before committing it.

## Claude Desktop

Claude Desktop uses the same local stdio server shape through its desktop MCP configuration file.

```json
{
  "mcpServers": {
    "jikuo": {
      "type": "stdio",
      "command": "<PYTHON_EXE>",
      "args": ["-B", "-m", "jikuo.integrations.mcp.server"],
      "env": {}
    }
  }
}
```

After updating the desktop configuration, restart Claude Desktop and ask it to call `jikuo.get_runtime_status_card`.

## Cursor

Cursor supports project-level MCP configuration in `.cursor/mcp.json`.

```json
{
  "mcpServers": {
    "jikuo": {
      "command": "<PYTHON_EXE>",
      "args": ["-B", "-m", "jikuo.integrations.mcp.server"],
      "env": {}
    }
  }
}
```

Keep `.cursor/mcp.json` uncommitted unless the team explicitly agrees to share the MCP server configuration.

Instruction target:

```powershell
jikuo install --client cursor --trigger-mode ask
```

Review `.cursorrules` after guarded install.

## VS Code + GitHub Copilot Agent Mode

VS Code / GitHub Copilot Agent mode can use MCP servers through VS Code MCP
configuration. For local stdio JIKUO use a project `.vscode/mcp.json`:

```json
{
  "servers": {
    "jikuo": {
      "type": "stdio",
      "command": "<PYTHON_EXE>",
      "args": ["-B", "-m", "jikuo.integrations.mcp.server"],
      "cwd": "<PROJECT_ROOT>"
    }
  }
}
```

Instruction target:

```powershell
jikuo install --client vscode-copilot --trigger-mode ask
```

Review `.github/copilot-instructions.md` after guarded install. Copilot Agent
mode should be asked to call `jikuo.get_runtime_status_card` first to verify the
tool surface.

## Codex Desktop / Codex CLI

Use the same stdio command and arguments when Codex exposes an MCP settings UI or CLI configuration surface:

```text
command = "<PYTHON_EXE>"
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
cwd = "<PROJECT_ROOT>"
```

Record the exact Codex configuration path or command in `JIKUO-MCP-01` when a stable shareable Codex configuration surface is identified.

Instruction target:

```powershell
jikuo install --client codex --trigger-mode ask
```

Review `AGENTS.md` after guarded install.

## Stage A Smoke Checklist

For a configured client:

1. Tool discovery includes the 8 Stage A no-write tools.
2. `jikuo.get_runtime_status_card` returns `status=ok`.
3. `card_markdown` begins with `## Policy runtime status`.
4. `.jikuo/runtime/last_card.md` contains the same single-card Markdown for `jikuo.get_runtime_status_card`.
5. `jikuo show --last-card` shows the same card.
6. No `.jikuo/policies/`, `.jikuo/task_sessions/`, or `.jikuo/project_state.yaml` write is caused by the no-write Stage A call.

## Current MVP Tool Discovery Checklist

For the current MVP, tool discovery should list exactly 11 tools:

1. `jikuo.status`
2. `jikuo.get_runtime_status`
3. `jikuo.get_runtime_status_card`
4. `jikuo.get_display_card`
5. `jikuo.propose_task_start`
6. `jikuo.propose_policy_write_plan`
7. `jikuo.propose_policy_evolution_plan`
8. `jikuo.propose_policy_template_import_plan`
9. `jikuo.apply_task_session_evidence_update`
10. `jikuo.apply_policy_evolution_write`
11. `jikuo.apply_policy_template_activation`

If a GUI client shows fewer tools after updating JIKUO, start a new client
session or restart the desktop application so it respawns the MCP server.

## Stage B1 Smoke Checklist

For `jikuo.apply_task_session_evidence_update`:

1. Calling the tool without `confirm_apply=true` is refused and does not modify the target task-session file.
2. Calling the tool without `approval_phrase` is refused and does not modify the target task-session file.
3. Calling the tool with a valid `session_id`, evidence fields, `confirm_apply=true`, and approval phrase appends exactly one evidence item to the target task-session.
4. The success path does not write `.jikuo/policies/` and does not update `.jikuo/project_state.yaml`.
5. The returned `card_markdown` and `.jikuo/runtime/last_card.md` surface the guarded apply result.

## Stage B2 Smoke Checklist

For `jikuo.apply_policy_evolution_write`:

1. Calling the tool without `confirm_apply=true` is refused.
2. Calling the tool without `approval_phrase` is refused.
3. Calling the tool without a matching `proposal_ref` is refused.
4. Supersession smoke should include `replacement_trigger_event` when the replacement policy must move away from the default `task_start` trigger.
5. Calling the tool with the proposal ref reviewed by the user, matching replacement fields, `confirm_apply=true`, and an approval phrase applies exactly one approved deprecation or supersession.
6. The success path does not create `.jikuo/task_sessions/`.
7. The response does not contain the raw approval phrase.
8. The returned `card_markdown` and `.jikuo/runtime/last_card.md` surface the guarded apply result.

Run B2 apply-path smoke against a copied temporary fixture unless the user is
intentionally approving a real project policy evolution.

## Stage B3 Smoke Checklist

For `jikuo.apply_policy_template_activation`:

1. Calling the tool without `confirm_apply=true` is refused.
2. Calling the tool without `approval_phrase` is refused.
3. Calling the tool against unresolved or unsafe project-context bindings is refused.
4. Calling the tool with a resolved template, `confirm_apply=true`, and an approval phrase writes exactly the approved policy activation artifacts.
5. The expected write set is limited to `.jikuo/policies/proposals/`, `.jikuo/policies/approved/`, `.jikuo/policies/decisions/`, `.jikuo/policies/manifest.yaml`, and `.jikuo/runtime/`.
6. The success path does not create `.jikuo/task_sessions/`.
7. The response does not contain the raw approval phrase.
8. The returned `card_markdown` and `.jikuo/runtime/last_card.md` surface the guarded apply result.

Run B3 apply-path smoke against a copied temporary fixture unless the user is
intentionally approving a real project policy-template activation.

## Verified So Far

- Official Python MCP SDK `ClientSession` stdio smoke passed in a separate Codex window.
- The server listed the 8 Stage A tools and successfully called `jikuo.get_runtime_status_card`.
- User verified real desktop-client smoke from Codex Desktop on 2026-05-15.
- User verified real desktop-client smoke from Claude Desktop on 2026-05-15.
- Local client and test byproducts may remain under ignored project paths such as `.claude/` and `tmp/`; they are not Stage A source artifacts.
- Stage B1 `jikuo.apply_task_session_evidence_update` was implemented after explicit user approval.
- Official Python MCP SDK `ClientSession` stdio smoke listed 9 tools, called the Stage B1 tool successfully, and confirmed Stage B2 / B3 tools were not exposed.
- Stage B2 `jikuo.apply_policy_evolution_write` was implemented after explicit user approval and externally smoke-accepted on 2026-05-16.
- Stage B3 `jikuo.apply_policy_template_activation` was implemented after explicit user approval and externally smoke-accepted in Claude Code GUI on 2026-05-16.
- Current GUI MCP smoke observed 11 tools and did not show a client tool-list cache issue after starting a fresh session.
- Final local official SDK release smoke passed on 2026-05-16 using `tmp/mcp-stage-a-venv/Scripts/python.exe`: `ClientSession` listed the 11-tool MVP surface and `jikuo.get_runtime_status_card` returned card Markdown matching `.jikuo/runtime/last_card.md` in a temporary fixture project.
