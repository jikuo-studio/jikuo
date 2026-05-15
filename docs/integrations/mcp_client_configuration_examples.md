# JIKUO MCP Client Configuration Examples

> Status: Stage A configuration examples and smoke-log companion.
> Scope: local stdio MCP clients only; no Stage B guarded-write tools are enabled.

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

This repository has not yet verified a hot-loadable Codex Desktop MCP configuration surface in the current environment. If Codex exposes an MCP settings UI or CLI configuration, use the same stdio command and arguments:

```text
command = "<PYTHON_EXE>"
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
cwd = "<PROJECT_ROOT>"
```

Record the exact Codex configuration path or command in `JIKUO-MCP-01` after it is verified in a real Codex client.

## Stage A Smoke Checklist

For a configured client:

1. Tool discovery lists exactly the 8 Stage A tools.
2. `jikuo.get_runtime_status_card` returns `status=ok`.
3. `card_markdown` begins with `## Policy runtime status`.
4. `.jikuo/runtime/last_card.md` contains the same single-card Markdown for `jikuo.get_runtime_status_card`.
5. `jikuo show --last-card` shows the same card.
6. No `.jikuo/policies/`, `.jikuo/task_sessions/`, or `.jikuo/project_state.yaml` write is caused by the no-write Stage A call.

Stage B guarded-write tools remain blocked until Stage A release gates are accepted.

## Verified So Far

- Official Python MCP SDK `ClientSession` stdio smoke passed in a separate Codex window.
- The server listed the 8 Stage A tools and successfully called `jikuo.get_runtime_status_card`.
- Current Codex Desktop session did not expose a hot-loadable MCP client configuration surface, so real desktop-client configuration remains pending client access.
