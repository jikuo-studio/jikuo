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
| `JIKUO_HOME` | Where the JIKUO package / repository lives | `C:\Users\you\src\jikuo` |
| `PROJECT_ROOT` | The user's project being governed or tested | `C:\Users\you\work\sample-project` |

For a real user, `PROJECT_ROOT` is their own app / product / writing project.
For this proof, use empty temporary projects so no private project content is
exposed.

The MCP server is launched from the Python environment where JIKUO is installed.
Each MCP tool call receives `project_root`, so the proof can target a clean
temporary project even when the tool package lives elsewhere.

## 3. Proof Goal

For each client, prove all of the following:

1. The client can launch the local JIKUO MCP server.
2. Tool discovery shows the current 24-tool surface.
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
<WORKSPACE>\jikuo-private-preview
```

Users need GitHub access to the private repository before they can clone it.

### Current Development Proof

For maintainer-local or contributor development, JIKUO already exists at your
current checkout:

```text
<JIKUO_HOME>
```

Use the Python environment from that checkout:

```text
<JIKUO_HOME>\.venv\Scripts\python.exe
```

### Fresh User From Git Repository

```powershell
cd <WORKSPACE>
git clone https://github.com/jikuo-studio/jikuo.git jikuo-private-preview
cd <WORKSPACE>\jikuo-private-preview
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
  `<JIKUO_HOME>\tmp\client_proof_manual\cursor_project`
- `<JIKUO_HOME>`: where the JIKUO package/repository lives
- `<PYTHON_EXE>`: Python executable from the environment where JIKUO is installed
- `<JIKUO_CMD>`: `jikuo` command from the same environment
- `<COMMIT>`: current `git rev-parse --short HEAD`

For the current repository proof:

```text
<JIKUO_HOME> = <WORKSPACE>\jikuo
<JIKUO_REPO_URL> = https://github.com/jikuo-studio/jikuo.git
<PYTHON_EXE> = <JIKUO_HOME>\.venv\Scripts\python.exe
<JIKUO_CMD> = <JIKUO_HOME>\.venv\Scripts\jikuo.exe
```

For GitHub private preview proof, prefer a clean clone:

```text
<JIKUO_HOME> = <WORKSPACE>\jikuo-private-preview
<PYTHON_EXE> = <JIKUO_HOME>\.venv\Scripts\python.exe
<JIKUO_CMD> = <JIKUO_HOME>\.venv\Scripts\jikuo.exe
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
<JIKUO_HOME>\tmp\client_proof_manual\claude_code_gui_project
<JIKUO_HOME>\tmp\client_proof_manual\codex_project
<JIKUO_HOME>\tmp\client_proof_manual\cursor_project
<JIKUO_HOME>\tmp\client_proof_manual\vscode_copilot_project
```

For the private GitHub clone proof, use the same layout under the clean clone:

```text
<JIKUO_HOME>\tmp\client_proof_manual\claude_code_gui_project
<JIKUO_HOME>\tmp\client_proof_manual\codex_project
<JIKUO_HOME>\tmp\client_proof_manual\cursor_project
<JIKUO_HOME>\tmp\client_proof_manual\vscode_copilot_project
```

These directories are intentionally under ignored `tmp/` paths. They are for
manual proof only and should not be committed.

## 7. Current Tool List

The client should discover exactly these 24 tools:

1. `jikuo.status`
2. `jikuo.get_policy_management_status`
3. `jikuo.get_runtime_status`
4. `jikuo.get_runtime_status_card`
5. `jikuo.get_display_card`
6. `jikuo.propose_task_start`
7. `jikuo.propose_policy_write_plan`
8. `jikuo.propose_policy_evolution_plan`
9. `jikuo.propose_policy_distribution_review`
10. `jikuo.propose_policy_template_publication_plan`
11. `jikuo.propose_starter_manifest_publication_plan`
12. `jikuo.propose_policy_template_import_plan`
13. `jikuo.get_configuration_status`
14. `jikuo.get_activation_settings`
15. `jikuo.plan_activation_settings_update`
16. `jikuo.apply_activation_settings_update`
17. `jikuo.route_user_request`
18. `jikuo.propose_policy_suggestions`
19. `jikuo.probe_sampling_semantic_intent`
20. `jikuo.apply_task_session_evidence_update`
21. `jikuo.apply_policy_evolution_write`
22. `jikuo.apply_policy_template_activation`
23. `jikuo.apply_policy_template_publication`
24. `jikuo.apply_starter_manifest_publication`

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
   - Expected count: 24.
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

4. Optionally call `jikuo.probe_sampling_semantic_intent` with:
   - project_root = `<PROJECT_ROOT>`
   - user_phrase = `Please explain the design, update the hook proof docs, and summarize the remaining work.`
   - trigger_mode = `semantic`
   Report `sampling_semantic_intent.status`, the returned model name if any,
   final policy scopes, and whether the tool fell back cleanly. This is a
   client semantic-provider proof, not strict mounted proof.

5. Verify out-of-band runtime visibility.
   Check or reference `<PROJECT_ROOT>\.jikuo\runtime\last_card.md`, or explain
   how the user can run `jikuo show --last-card`.
   Confirm whether it corresponds to the latest JIKUO card from this proof.

6. Judge strict mounted status for this client.
   Choose one:
   - MCP + instruction works, but strict pre-turn mounted is not verified.
   - A stable pre-turn hook / plugin / extension entry exists, but JIKUO has not implemented the adapter yet.
   - Strict pre-turn adapter is verified.

7. Output a proof report with:
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
- Expected count: 24
- Missing tools:
- Extra tools:

## Runtime Card Proof

- Tool called: `jikuo.get_runtime_status_card`
- Card displayed in chat: yes/no
- Runtime card path: `.jikuo/runtime/last_card.md`
- `jikuo show --last-card` or file check matches latest card: yes/no

## Router Proof

- Tool called: `jikuo.route_user_request`
- Compact user-turn summary, no raw prompt:
- Router schema:

## Sampling Semantic Proof

- Tool called: `jikuo.probe_sampling_semantic_intent`
- Sampling status: provided/unavailable/invalid/not-run
- Model returned by client:
- Final policy scopes:
- Strict mounted implication: none; this only proves client-mediated semantic sampling during a tool call
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

Store reviewed proof notes under `docs/integrations/proofs/` after user review.
Accepted notes must be marked as accepted. Failed or blocked observations may be
kept there too, but they must be marked `not_accepted` and must not be used as
strict-mounted evidence. Keep screenshots and temporary scripts under ignored
local paths unless the user explicitly approves committing them.

## 10. Claude Code GUI Proof

### Configure

Recommended private/local setup:

```powershell
cd <PROJECT_ROOT>
claude mcp add --transport stdio --scope local jikuo -- "<PYTHON_EXE>" -B -m jikuo.integrations.mcp.server
claude mcp get jikuo
```

Project-shared setup, only if the team agrees to commit `.mcp.json`:

```powershell
cd <PROJECT_ROOT>
claude mcp add --transport stdio --scope project jikuo -- "<PYTHON_EXE>" -B -m jikuo.integrations.mcp.server
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
<PROJECT_ROOT> = <JIKUO_HOME>\tmp\client_proof_manual\claude_code_gui_project
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
command = <PYTHON_EXE>
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
cwd = <PROJECT_ROOT>
```

For Codex CLI / config-file based setups, add or review a server entry in the
Codex config TOML used by your installation:

```toml
[mcp_servers.jikuo]
command = "<PYTHON_EXE>"
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
enabled = true
```

Restart Codex after changing MCP config so the server process is respawned.

### Run Proof

Use the standard prompt with:

```text
<PROJECT_ROOT> = <JIKUO_HOME>\tmp\client_proof_manual\codex_project
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

### Codex Hook Proof Design

The next Codex proof is not another MCP tool-discovery run. It is a host-boundary
proof for the official Codex hook surface.

Official behavior to verify in the installed Codex build:

- Codex can load hooks from `~/.codex/hooks.json`,
  `~/.codex/config.toml`, `<repo>/.codex/hooks.json`, or
  `<repo>/.codex/config.toml`.
- Project-local `.codex/` hooks require the project layer to be trusted.
- `UserPromptSubmit` receives the current `prompt` before it is sent to the
  model and can add `additionalContext` or block the prompt.
- Plugin-bundled hooks are opt-in, so the first proof should use project-local
  `.codex/` hook configuration rather than a packaged plugin hook.

Minimal proof input:

```text
hook_event_name = UserPromptSubmit
prompt = <current user prompt>
cwd = <PROJECT_ROOT or a subdirectory inside it>
trigger_mode = mounted
host_semantic_intent = <provided | unavailable | heuristic_fallback>
```

Minimal subprocess-equivalent JIKUO command:

```powershell
<PYTHON_EXE> -B -m jikuo.agent_flow propose --event conversation_turn --project-root "<PROJECT_ROOT>" --trigger-mode mounted --user-phrase-stdin --format json
```

Proof notes should not copy the full prompt. Record card links, status, and a
compact summary only. The current project-local hook defaults to in-process
JIKUO invocation to avoid GUI nested-Python subprocess hangs. If subprocess
diagnostic mode is enabled, it passes prompt text to the CLI over stdin with
`--user-phrase-stdin`, not through the child process argument list. A reusable
hook pack may still switch to MCP when the target host provides a reliable
boundary.

Semantic classification proof:

- The first proof may only prove mounted invocation. That is useful but it does
  not prove AI-semantic routing.
- The local Level 2A input path now accepts compact `host_semantic_intent`
  through CLI / MCP / Codex hook proof and merges it into `work_profile`; this
  proves JIKUO can consume semantic evidence, not that a GUI host can provide
  it before model work.
- For MCP router tools, first verify that `jikuo.route_user_request` and
  `jikuo.propose_policy_suggestions` expose a `host_semantic_intent` argument
  in the client-visible tool schema. If the argument is absent, refresh or
  restart the MCP client/server before judging host AI semantic transport.
- If the host exposes AI semantic intent before JIKUO runs, pass a compact
  `host_semantic_intent` object with source, confidence, lifecycle event,
  `policy_scopes`, intent class, operation class, output class, and compact
  rationale.
- If the hook can only see the raw prompt, record
  `host_semantic_intent.status = unavailable` and let JIKUO report deterministic
  keyword routing as fallback.
- Check `semantic_intent_classification_evidence` in the JIKUO response or
  card. For `editing` / `progress_summary` work it should report
  `required=true`; if no host or Sampling provider supplied compact semantic
  intent, it should report `status=missing` or `fallback_only` and a
  `provide_host_semantic_intent_and_rerun_route` follow-up. This is report-only
  evidence, not a blocking gate.
- Deterministic fallback has bilingual Chinese / English keyword coverage and
  no-edit constraint phrases, but it remains fallback / conflict evidence rather
  than AI semantic classification.
- Do not let the hook decide active-policy applicability. JIKUO remains the
  final classification and policy-distribution authority.

Accepted cooperative GUI router proof:

- `docs/integrations/proofs/PROOF-2026-05-31-codex-gui-mcp-router-host-semantic-intent.md`
  records a separate Codex GUI session where `jikuo.route_user_request`
  exposed `host_semantic_intent`, the host AI passed compact semantic intent,
  and JIKUO returned `semantic_intent_evidence.status=ok`.
- This proves the cooperative MCP tool-call path. It does not prove automatic
  hook-time semantic classification or Sampling provider support.

UTF-8 semantic field proof:

- `docs/integrations/proofs/PROOF-2026-05-31-runtime-card-utf8-semantic-fields.md`
  records a local adapter smoke where Chinese `requested_outcome` and
  `response_contract` values survived both response Markdown and direct
  UTF-8 reads of `.jikuo/runtime/last_card.md`.
- If pasted GUI proof text shows mojibake, compare it against a direct UTF-8
  read of the linked runtime card before treating it as a JIKUO runtime bug.

MCP Sampling provider proof:

- MCP Sampling lets a server request `sampling/createMessage` from the client
  during a tool call. Per the official MCP Sampling specification, the client
  keeps control over model access, model choice, permissions, and human review.
- `jikuo.probe_sampling_semantic_intent` uses that mechanism as an optional
  semantic provider: it asks the MCP client for a compact
  `host_semantic_intent`, then routes the turn through the existing no-write
  JIKUO router with that classification when available.
- If Sampling is unsupported, rejected, or invalid, the tool must return
  `sampling_semantic_intent.status=unavailable` or `invalid` and continue with
  honest deterministic fallback. That result is still useful compatibility
  evidence.
- If `jikuo.probe_sampling_semantic_intent` is not visible in the client tool
  inventory, stop before judging Sampling support. That is a tool-surface /
  client-refresh issue. Refresh or restart the MCP client/server and first
  verify that the probe tool is visible.
- This tool does not prove pre-turn hook execution. A normal MCP tool call
  happens only after the host model/user chooses to call the tool, so it cannot
  by itself satisfy strict mounted mode.
- Proof notes should not copy raw prompts or transcripts. The tool response
  redacts exact prompt echoes, and accepted proof records should keep only card
  links, semantic status, model name if returned, and compact observations.

Suggested compact semantic-intent evidence:

```yaml
host_semantic_intent:
  status: provided | unavailable | heuristic_fallback
  provider: host_ai | jikuo_semantic_classifier | deterministic_keyword_router
  multi_intent: true | false
  constraints: [no_file_write]
  policy_scopes: [discussion, editing, progress_summary]
  primary_intent_ref: update_docs
  intent_slices:
    - id: explain_design
      policy_scopes: [discussion]
      intent_class: design_explanation
      operation_class: read_only
      output_class: explanation
    - id: update_docs
      policy_scopes: [editing]
      intent_class: implementation_request
      operation_class: documentation_update
      output_class: repository_change
    - id: summarize_progress
      policy_scopes: [progress_summary]
      intent_class: progress_summary
      operation_class: summarize
      output_class: summary
  confidence: medium
  rationale_summary: "Compact summary only; no raw prompt."
```

Minimum semantic proof cases:

| Probe prompt shape | Expected semantic intent | Expected final JIKUO behavior |
|---|---|---|
| "Explain the design only; do not edit files." | one discussion slice, `constraints=[no_file_write]` | final scope includes `discussion`, not `editing`; editing keywords become conflict evidence if present |
| "Update the hook docs." | one editing slice | final scope includes `editing`; editing policies can trigger |
| "Explain it, update docs, then summarize progress." | discussion + editing + progress summary slices | final aggregate scopes include all three; runtime card shows slices |
| Host semantic intent unavailable | `status=unavailable` | JIKUO reports deterministic fallback honestly |
| Host says discussion, keywords suggest editing | conflict recorded | final decision follows host/constraint if confidence is sufficient, with conflict visible |

End-to-end Codex GUI proof flow:

1. Enable the project-local Codex `UserPromptSubmit` proof hook in a trusted
   project.
2. Submit a probe prompt from the Codex GUI, not only from CLI.
3. Confirm the hook fires before Codex starts substantive model output.
4. Confirm the hook calls JIKUO and produces a new `conversation_turn` history
   card.
5. Confirm Codex receives `additionalContext` with latest card, history card,
   semantic-intent status, final scopes, triggered-policy summary, and required
   follow-up tools.
6. Continue the task in Codex and perform any requested edits or discussion.
7. Before the final answer or commit, run `completion_review`.
8. Confirm completion review produces a separate lifecycle card and reports
   main-doc / evidence / progress-summary status.
9. Record the proof result with links to the pre-turn card and completion card,
   plus pass/fail observations. Do not copy the raw prompt or transcript.

The proof is accepted only when the user can see that Codex did not merely have
MCP tools available. JIKUO must have been invoked before work, its context must
have been mounted into Codex, and completion review must have produced a later
card for the same governed work.

Expected hook output:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "JIKUO mounted pre-turn ran. Semantic intent: <provided|unavailable|fallback>. Latest card: <path>. History card: <path>. Required follow-up tools: <tools-or-none>."
  }
}
```

Strict mounted proof passes only if:

- the hook runs before Codex starts substantive model work;
- a new `.jikuo/runtime/history/*.md` card is produced for the user prompt;
- the injected `additionalContext` includes the latest card path and any
  required follow-up tools;
- semantic-intent availability is recorded honestly as host AI, JIKUO semantic
  classifier, deterministic fallback, or unavailable;
- multi-intent prompts produce aggregate policy scopes and visible per-slice
  explanations rather than being collapsed into one hidden label;
- negative constraints such as "do not edit" are represented separately and can
  prevent keyword-only editing promotion;
- a no-op prompt still produces a visible `mounted_idle_tick`;
- a JIKUO failure is visible as a block or degradation, not a silent bypass.

Strict mounted proof fails if:

- the GUI surface does not load or trust the hook;
- the hook runs after model work has already started;
- the hook cannot locate a stable project root;
- the proof relies on reading the full transcript as a stable API;
- the proof only demonstrates MCP availability.
- the proof claims AI-semantic classification while only keyword fallback ran.

Project-local proof files now implemented for the current repository:

```text
<PROJECT_ROOT>\.codex\hooks.json
<PROJECT_ROOT>\.codex\hooks\jikuo_user_prompt_submit.py
<PROJECT_ROOT>\.codex\hooks\README.md
tests\codex_hook_tests.py
```

These files began as Level 1 adapter proof scaffolding. The 2026-05-21 Codex
GUI observation accepted the narrower pre-turn `additionalContext` injection
surface after timeout remediation. A 2026-05-28 Codex GUI observation then
showed visible degraded `additionalContext` caused by nested-Python subprocess
timeout, so the hook now defaults to in-process JIKUO invocation. The fresh
in-process GUI smoke is now accepted for the pre-turn `additionalContext`
path. They do not prove full lifecycle strict
mounted behavior until a later completion-review card is linked in the proof
report, and they do not prove host-time AI semantic routing or multi-intent
semantic handling.

Accepted proof notes should still be written under:

```text
docs\integrations\proofs\<accepted-codex-hook-proof>.md
```

Do not commit screenshots, temporary local runtime cards, raw prompts, raw
transcripts, or client-specific private paths unless the user explicitly
approves.

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
      "command": "<PYTHON_EXE>",
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
<JIKUO_CMD> install --client cursor --trigger-mode ask
```

Review `.cursorrules` if generated.

### Run Proof

Use the standard prompt with:

```text
<PROJECT_ROOT> = <JIKUO_HOME>\tmp\client_proof_manual\cursor_project
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
      "command": "<PYTHON_EXE>",
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
<JIKUO_CMD> install --client vscode-copilot --trigger-mode ask
```

Review `.github/copilot-instructions.md` if generated.

### Run Proof

Use the standard prompt with:

```text
<PROJECT_ROOT> = <JIKUO_HOME>\tmp\client_proof_manual\vscode_copilot_project
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
| PASS | Client can launch JIKUO MCP, discover 24 tools, display cards, and route a user request; Sampling may be provided or cleanly unavailable | Record proof note and include it in compatibility docs |
| PARTIAL | Client can launch MCP but misses tools, hides cards, or cannot prove runtime parity | Record exact failure; do not claim full support yet |
| BLOCKED | Client has no accessible MCP config surface or cannot start the stdio server | Record the blocker and retry after client update / config discovery |

Strict mounted should stay `not_verified` unless the proof shows a real
pre-turn adapter boundary. A normal MCP call inside chat is useful, but it is
still user/agent-mediated rather than a strict harness.

## 15. Source References

- MCP Sampling specification: `https://modelcontextprotocol.io/specification/2025-06-18/client/sampling`
- Claude Code MCP docs: `https://docs.claude.com/en/docs/claude-code/mcp`
- Cursor MCP docs: `https://docs.cursor.com/advanced/model-context-protocol`
- VS Code MCP configuration reference: `https://code.visualstudio.com/docs/copilot/reference/mcp-configuration`
- Codex configuration reference: `https://github.com/openai/codex/blob/main/docs/config.md`
