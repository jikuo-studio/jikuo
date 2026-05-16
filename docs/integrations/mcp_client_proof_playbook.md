# JIKUO MCP Client Proof Playbook

> **Status**: Manual proof playbook for desktop MCP clients.
> **Product meaning**: this document is both a first-use configuration guide and the evidence checklist for saying a client actually supports JIKUO MCP, not merely that unit tests pass.
> **Scope**: local stdio MCP only; no remote hosted MCP, no strict pre-turn adapter implementation, and no screenshots committed unless the user explicitly approves.

## 1. User Entry Model

This playbook starts from a completely new user path.

The target user may have strong product ideas and good judgment without
engineering experience. JIKUO is distributed as a Python package, but the user
should not start by writing Python code or importing `jikuo`.

The normal path is:

1. Get JIKUO onto the computer.
2. Create or use a Python environment where JIKUO is installed.
3. Verify the `jikuo` command and MCP server can start.
4. Configure the desktop AI client to launch the local JIKUO MCP server.
5. Ask the client to run the proof prompt in this document.

Python `import` is a developer integration surface for Agent SDK wrappers,
plugins, Studio, or custom platforms. It is not the first-use product surface.

## 2. Two Folders To Understand

JIKUO proof uses two different local folders:

| Folder | Meaning | Example |
|---|---|---|
| `JIKUO_HOME` | Where the JIKUO package / repository lives | `D:\personal_project\Jikuo` |
| `PROJECT_ROOT` | The user's project being governed or tested | `D:\personal_project\Jikuo\tmp\client_proof_manual\cursor_project` |

For a real user, `PROJECT_ROOT` is their own app / product / writing project.
For this proof, use empty temporary projects so no private project content is
exposed.

The MCP server is launched from the Python environment where JIKUO is installed.
Each MCP tool call receives `project_root`, so the proof can target a clean
temporary project even when the tool package lives elsewhere.

## 3. Proof Goal

For each client, prove all of the following:

1. The client can launch the local JIKUO MCP server.
2. Tool discovery shows the current 17-tool surface.
3. A no-write card tool displays `card_markdown` to the user.
4. A router tool can classify an ordinary user setup request.
5. `.jikuo/runtime/last_card.md` or `jikuo show --last-card` matches the latest card.
6. The proof records whether the client can support a future strict pre-turn mounted adapter.

Passing this proof means "JIKUO MCP is usable in this client." It does not mean
"mounted mode is strict" unless the client also has a pre-turn hook / plugin /
extension / SDK wrapper / Studio proxy that calls JIKUO before every user turn.

## 4. Get JIKUO Locally

### Current Private GitHub Preview

The current owner-controlled private preview repository is:

```text
https://github.com/jikuo-studio/jikuo.git
```

This repository is private while license, privacy sweep, trademark/domain
posture, and public-review gates remain open. Use it to test the realistic
"clone or download from GitHub" user path without publishing the code.

The expected fresh-clone proof folder is:

```text
D:\personal_project\Jikuo_private_preview
```

Users need GitHub access to the private repository before they can clone it.

### Current Development Proof

In this repository, JIKUO already exists at:

```text
D:\personal_project\Jikuo
```

The verified Python environment is:

```text
D:\personal_project\Jikuo\tmp\mcp-stage-a-venv\Scripts\python.exe
```

### Fresh User From Git Repository

```powershell
cd D:\personal_project
git clone https://github.com/jikuo-studio/jikuo.git Jikuo_private_preview
cd D:\personal_project\Jikuo_private_preview
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\jikuo.exe --help
.\.venv\Scripts\jikuo-mcp.exe --help
```

If the user does not have Git, download the repository as a ZIP file, unzip it,
open PowerShell in the unzipped folder, then run the `py -3 -m venv ...` steps.

### Future Published Package Path

After JIKUO has a public package release, the user path should become simpler:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install jikuo
.\.venv\Scripts\jikuo.exe --help
.\.venv\Scripts\jikuo-mcp.exe --help
```

Do not ask normal users to run `from jikuo import ...`.

## 5. Common Preparation

Run these from `JIKUO_HOME`:

```powershell
cd <JIKUO_HOME>
git status --short
git rev-parse --short HEAD
```

Check the Python executable that will launch the MCP server:

```powershell
<PYTHON_EXE> -B -m jikuo.integrations.mcp.server --help
```

Use these placeholders in client configs and proof prompts:

- `<JIKUO_REPO_URL>`: `https://github.com/jikuo-studio/jikuo.git`
- `<PROJECT_ROOT>`: the per-client temporary proof project, for example
  `D:\personal_project\Jikuo\tmp\client_proof_manual\cursor_project`
- `<JIKUO_HOME>`: where the JIKUO package/repository lives
- `<PYTHON_EXE>`: Python executable from the environment where JIKUO is installed
- `<JIKUO_CMD>`: `jikuo` command from the same environment
- `<COMMIT>`: current `git rev-parse --short HEAD`

For the current repository proof:

```text
<JIKUO_HOME> = D:\personal_project\Jikuo
<JIKUO_REPO_URL> = https://github.com/jikuo-studio/jikuo.git
<PYTHON_EXE> = D:\personal_project\Jikuo\tmp\mcp-stage-a-venv\Scripts\python.exe
<JIKUO_CMD> = D:\personal_project\Jikuo\tmp\mcp-stage-a-venv\Scripts\jikuo.exe
```

For GitHub private preview proof, prefer a clean clone:

```text
<JIKUO_HOME> = D:\personal_project\Jikuo_private_preview
<PYTHON_EXE> = D:\personal_project\Jikuo_private_preview\.venv\Scripts\python.exe
<JIKUO_CMD> = D:\personal_project\Jikuo_private_preview\.venv\Scripts\jikuo.exe
```

MCP server config should use:

```text
command = <PYTHON_EXE>
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
cwd = <PROJECT_ROOT>
```

If a desktop client cannot set `cwd`, this is acceptable as long as each JIKUO
tool call explicitly receives the client-specific `project_root`.

## 6. Temporary Proof Projects

Use separate temporary projects so clients do not overwrite each other's runtime
cards:

```text
D:\personal_project\Jikuo\tmp\client_proof_manual\claude_code_gui_project
D:\personal_project\Jikuo\tmp\client_proof_manual\codex_project
D:\personal_project\Jikuo\tmp\client_proof_manual\cursor_project
D:\personal_project\Jikuo\tmp\client_proof_manual\vscode_copilot_project
```

For the private GitHub clone proof, use the same layout under the clean clone:

```text
D:\personal_project\Jikuo_private_preview\tmp\client_proof_manual\claude_code_gui_project
D:\personal_project\Jikuo_private_preview\tmp\client_proof_manual\codex_project
D:\personal_project\Jikuo_private_preview\tmp\client_proof_manual\cursor_project
D:\personal_project\Jikuo_private_preview\tmp\client_proof_manual\vscode_copilot_project
```

These directories are intentionally under ignored `tmp/` paths. They are for
manual proof only and should not be committed.

## 7. Current Tool List

The client should discover exactly these 17 tools:

1. `jikuo.status`
2. `jikuo.get_runtime_status`
3. `jikuo.get_runtime_status_card`
4. `jikuo.get_display_card`
5. `jikuo.propose_task_start`
6. `jikuo.propose_policy_write_plan`
7. `jikuo.propose_policy_evolution_plan`
8. `jikuo.propose_policy_template_import_plan`
9. `jikuo.get_configuration_status`
10. `jikuo.get_activation_settings`
11. `jikuo.plan_activation_settings_update`
12. `jikuo.apply_activation_settings_update`
13. `jikuo.route_user_request`
14. `jikuo.propose_policy_suggestions`
15. `jikuo.apply_task_session_evidence_update`
16. `jikuo.apply_policy_evolution_write`
17. `jikuo.apply_policy_template_activation`

Some clients render MCP names with a namespace such as
`mcp__jikuo__jikuo_get_runtime_status_card`. That is acceptable if the
underlying JIKUO tool list matches.

## 8. Standard User Prompt For Each Client

Replace `<PROJECT_ROOT>` before pasting this into the configured client:

```text
Please perform a JIKUO MCP compatibility proof from the perspective of a normal
first-time user.

Do not only summarize your judgment. Actually call the mounted `jikuo` MCP
tools and paste the important card output back into this chat.

Target proof project root:
<PROJECT_ROOT>

Steps:

1. Confirm you can see the `jikuo` MCP tools.
   - List the tool count and tool names.
   - Expected count: 17.
   - If you see fewer tools, say whether this looks like a stale GUI session
     and whether a new session or client restart is needed.

2. Call `jikuo.get_runtime_status_card` with:
   - project_root = `<PROJECT_ROOT>`
   Paste the returned `card_markdown` verbatim.

3. Call `jikuo.route_user_request` with:
   - project_root = `<PROJECT_ROOT>`
   - user_phrase = `I am enabling JIKUO for the first time. Please review the configuration state and explain which settings I need to choose.`
   - trigger_mode = `semantic`
   Report the router schema, classified obligations, and follow-up tools.
   In particular, say whether it recommends `jikuo.get_configuration_status`.

4. Verify out-of-band runtime visibility.
   Check or reference `<PROJECT_ROOT>\.jikuo\runtime\last_card.md`, or explain
   how the user can run `jikuo show --last-card`.
   Confirm whether it corresponds to the latest JIKUO card from this proof.

5. Judge strict mounted status for this client.
   Choose one:
   - MCP + instruction works, but strict pre-turn mounted is not verified.
   - A stable pre-turn hook / plugin / extension entry exists, but JIKUO has not implemented the adapter yet.
   - Strict pre-turn adapter is verified.

6. Output a proof report with:
   - Client name
   - Client version if visible
   - OS
   - JIKUO commit if visible
   - MCP config path or GUI settings path if visible
   - Python executable if visible
   - Tool count
   - Runtime card link
   - Router result
   - last_card consistency
   - Strict mounted conclusion
   - PASS / FAIL
```

## 9. Proof Report Template

Copy this into a proof note after each manual run:

```markdown
# JIKUO MCP Client Proof - <client>

- Date:
- OS:
- Client name:
- Client version:
- JIKUO commit:
- Project root:
- Python executable:
- MCP config path or GUI settings path:
- Instruction file used:

## Tool Discovery

- Tool count:
- Expected count: 17
- Missing tools:
- Extra tools:

## Runtime Card Proof

- Tool called: `jikuo.get_runtime_status_card`
- Card displayed in chat: yes/no
- Runtime card path: `.jikuo/runtime/last_card.md`
- `jikuo show --last-card` or file check matches latest card: yes/no

## Router Proof

- Tool called: `jikuo.route_user_request`
- User phrase:
- Router schema:
- Follow-up tools suggested:
- Card displayed in chat: yes/no

## Strict Mounted Boundary

- Does the client currently have a stable pre-turn hook / plugin / extension / SDK wrapper entry for JIKUO?
- Current conclusion:
  - MCP + instruction only
  - strict pre-turn adapter possible but not implemented
  - strict pre-turn adapter verified

## Result

- PASS/FAIL:
- Blocking issues:
- Non-blocking observations:
```

Store accepted proof notes under `docs/integrations/proofs/` after user review.
Keep screenshots and temporary scripts under ignored local paths unless the user
explicitly approves committing them.

## 10. Claude Code GUI Proof

### Configure

Recommended private/local setup:

```powershell
cd <PROJECT_ROOT>
claude mcp add --transport stdio --scope local jikuo -- "D:\personal_project\Jikuo\tmp\mcp-stage-a-venv\Scripts\python.exe" -B -m jikuo.integrations.mcp.server
claude mcp get jikuo
```

Project-shared setup, only if the team agrees to commit `.mcp.json`:

```powershell
cd <PROJECT_ROOT>
claude mcp add --transport stdio --scope project jikuo -- "D:\personal_project\Jikuo\tmp\mcp-stage-a-venv\Scripts\python.exe" -B -m jikuo.integrations.mcp.server
```

Restart Claude Code GUI or start a fresh session after changing MCP config.
Inside Claude Code, run:

```text
/mcp
```

The `/mcp` panel should show the `jikuo` server and its tool count.

### Run Proof

Use the standard prompt with:

```text
<PROJECT_ROOT> = D:\personal_project\Jikuo\tmp\client_proof_manual\claude_code_gui_project
```

### Retain Proof

Record:

- Claude Code version / build if visible.
- Whether the config is local `~/.claude.json` or project `.mcp.json`.
- `/mcp` status and tool count.
- The chat message where `card_markdown` is displayed.
- The latest runtime link shown by JIKUO.
- Strict mounted status: Claude Code is the best first strict-adapter
  candidate, but the proof is still MCP + instruction until a hook slice is
  implemented and accepted.

## 11. Codex Desktop / Codex CLI Proof

### Configure

If the Codex app exposes a GUI MCP settings surface, add a local stdio server
with:

```text
name = jikuo
command = D:\personal_project\Jikuo\tmp\mcp-stage-a-venv\Scripts\python.exe
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
cwd = <PROJECT_ROOT>
```

For Codex CLI / config-file based setups, add or review a server entry in the
Codex config TOML used by your installation:

```toml
[mcp_servers.jikuo]
command = "D:\\personal_project\\Jikuo\\tmp\\mcp-stage-a-venv\\Scripts\\python.exe"
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
enabled = true
```

Restart Codex after changing MCP config so the server process is respawned.

### Run Proof

Use the standard prompt with:

```text
<PROJECT_ROOT> = D:\personal_project\Jikuo\tmp\client_proof_manual\codex_project
```

If Codex exposes MCP tools in the tool namespace, the proof should call the
JIKUO tools directly. If the GUI has no stable MCP configuration surface in the
current build, mark the result as "blocked by client configuration surface" and
record the exact UI state.

### Retain Proof

Record:

- Codex Desktop or Codex CLI version.
- The config path or GUI settings path used.
- Whether tool names appear as `jikuo.*` or namespaced MCP tool names.
- Tool count and missing/extra tools.
- The runtime card displayed in chat.
- Strict mounted status: MCP + instruction only unless a Codex plugin / hook /
  app extension point is verified separately.

## 12. Cursor Proof

### Configure

Create or edit project config:

```text
<PROJECT_ROOT>\.cursor\mcp.json
```

Use:

```json
{
  "mcpServers": {
    "jikuo": {
      "type": "stdio",
      "command": "D:\\personal_project\\Jikuo\\tmp\\mcp-stage-a-venv\\Scripts\\python.exe",
      "args": ["-B", "-m", "jikuo.integrations.mcp.server"],
      "env": {}
    }
  }
}
```

Restart Cursor or reload the window. Open Cursor settings / MCP tools and check
that `jikuo` is enabled. If Cursor shows cached tools, restart the session.

Instruction file preview:

```powershell
cd <PROJECT_ROOT>
D:\personal_project\Jikuo\tmp\mcp-stage-a-venv\Scripts\jikuo.exe install --client cursor --trigger-mode ask
```

Review `.cursorrules` if generated.

### Run Proof

Use the standard prompt with:

```text
<PROJECT_ROOT> = D:\personal_project\Jikuo\tmp\client_proof_manual\cursor_project
```

### Retain Proof

Record:

- Cursor version.
- `.cursor/mcp.json` content or settings screenshot reference.
- Tool count / available tools proof.
- Runtime card display proof.
- Router result proof.
- Strict mounted status: MCP + instruction only until a Cursor extension or
  hook-like adapter is implemented and accepted.

## 13. VS Code + GitHub Copilot Agent Mode Proof

### Configure

Use the Command Palette:

```text
MCP: Open Workspace Folder MCP Configuration
```

Or create:

```text
<PROJECT_ROOT>\.vscode\mcp.json
```

Use:

```json
{
  "servers": {
    "jikuo": {
      "type": "stdio",
      "command": "D:\\personal_project\\Jikuo\\tmp\\mcp-stage-a-venv\\Scripts\\python.exe",
      "args": ["-B", "-m", "jikuo.integrations.mcp.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Then use Command Palette:

```text
MCP: List Servers
```

Start or restart the `jikuo` server. If tools are stale after a JIKUO update:

```text
MCP: Reset Cached Tools
```

Instruction file preview:

```powershell
cd <PROJECT_ROOT>
D:\personal_project\Jikuo\tmp\mcp-stage-a-venv\Scripts\jikuo.exe install --client vscode-copilot --trigger-mode ask
```

Review `.github/copilot-instructions.md` if generated.

### Run Proof

Use the standard prompt with:

```text
<PROJECT_ROOT> = D:\personal_project\Jikuo\tmp\client_proof_manual\vscode_copilot_project
```

Open GitHub Copilot Chat in Agent mode for the workspace and paste the prompt.

### Retain Proof

Record:

- VS Code version and GitHub Copilot extension version if visible.
- `.vscode/mcp.json` content or settings path.
- `MCP: List Servers` status.
- Tool count / available tools proof.
- Runtime card display proof.
- Router result proof.
- Strict mounted status: MCP + instruction only until a VS Code extension or
  supported Copilot agent hook is implemented and accepted.

## 14. Interpreting Results

| Result | Meaning | Next action |
|---|---|---|
| PASS | Client can launch JIKUO MCP, discover 17 tools, display cards, and route a user request | Record proof note and include it in compatibility docs |
| PARTIAL | Client can launch MCP but misses tools, hides cards, or cannot prove runtime parity | Record exact failure; do not claim full support yet |
| BLOCKED | Client has no accessible MCP config surface or cannot start the stdio server | Record the blocker and retry after client update / config discovery |

Strict mounted should stay `not_verified` unless the proof shows a real
pre-turn adapter boundary. A normal MCP call inside chat is useful, but it is
still user/agent-mediated rather than a strict harness.

## 15. Source References

- Claude Code MCP docs: `https://docs.claude.com/en/docs/claude-code/mcp`
- Cursor MCP docs: `https://docs.cursor.com/advanced/model-context-protocol`
- VS Code MCP configuration reference: `https://code.visualstudio.com/docs/copilot/reference/mcp-configuration`
- Codex configuration reference: `https://github.com/openai/codex/blob/main/docs/config.md`
