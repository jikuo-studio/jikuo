# JIKUO MCP Client Configuration Examples

> Status: Stage A configuration examples and smoke-log companion.
> Scope: local stdio MCP clients only; Stage B1 task-session evidence guarded
> write is enabled after explicit user approval. Stage B2 / B3 policy-store
> writes remain blocked.

## Purpose

This file records reusable client configuration examples for the JIKUO MCP Stage A server.

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

## Codex Desktop / Codex CLI

Use the same stdio command and arguments when Codex exposes an MCP settings UI or CLI configuration surface:

```text
command = "<PYTHON_EXE>"
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
cwd = "<PROJECT_ROOT>"
```

Record the exact Codex configuration path or command in `JIKUO-MCP-01` when a stable shareable Codex configuration surface is identified.

## Stage A Smoke Checklist

For a configured client:

1. Tool discovery includes the 8 Stage A no-write tools.
2. `jikuo.get_runtime_status_card` returns `status=ok`.
3. `card_markdown` begins with `## Policy runtime status`.
4. `.jikuo/runtime/last_card.md` contains the same single-card Markdown for `jikuo.get_runtime_status_card`.
5. `jikuo show --last-card` shows the same card.
6. No `.jikuo/policies/`, `.jikuo/task_sessions/`, or `.jikuo/project_state.yaml` write is caused by the no-write Stage A call.

## Stage B1 Smoke Checklist

For `jikuo.apply_task_session_evidence_update`:

1. Tool discovery lists the 8 Stage A tools plus `jikuo.apply_task_session_evidence_update`.
2. `jikuo.apply_policy_evolution_write` and `jikuo.apply_policy_template_activation` are not listed.
3. Calling the tool without `confirm_apply=true` is refused and does not modify the target task-session file.
4. Calling the tool without `approval_phrase` is refused and does not modify the target task-session file.
5. Calling the tool with a valid `session_id`, evidence fields, `confirm_apply=true`, and approval phrase appends exactly one evidence item to the target task-session.
6. The success path does not write `.jikuo/policies/` and does not update `.jikuo/project_state.yaml`.
7. The returned `card_markdown` and `.jikuo/runtime/last_card.md` surface the guarded apply result.

Stage B2 / B3 guarded policy-store writes remain blocked until separately accepted.

## Verified So Far

- Official Python MCP SDK `ClientSession` stdio smoke passed in a separate Codex window.
- The server listed the 8 Stage A tools and successfully called `jikuo.get_runtime_status_card`.
- User verified real desktop-client smoke from Codex Desktop on 2026-05-15.
- User verified real desktop-client smoke from Claude Desktop on 2026-05-15.
- Local client and test byproducts may remain under ignored project paths such as `.claude/` and `tmp/`; they are not Stage A source artifacts.
- Stage B1 `jikuo.apply_task_session_evidence_update` was implemented after explicit user approval.
- Official Python MCP SDK `ClientSession` stdio smoke listed 9 tools, called the Stage B1 tool successfully, and confirmed Stage B2 / B3 tools were not exposed.
- Stage B2 / B3 guarded policy-store writes remain blocked until separately accepted.
