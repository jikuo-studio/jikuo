# Getting Started With JIKUO

> **Status**: First-run user guide for the current pre-release package.
> **Boundary**: This guide describes the local JIKUO product loop. It does not
> claim strict mounted enforcement unless a host adapter is actually installed
> and calling JIKUO before the turn.

## 1. What This Flow Proves

Use this guide to take a fresh local checkout through one complete governed
workflow:

- install the package;
- open the CLI and Studio read-only console;
- inspect first-run readiness;
- configure activation settings;
- configure the MCP server and client instruction files;
- optionally enable the project-local Codex pre-turn hook;
- activate starter policies through a reviewed plan;
- review or update Document Rules;
- run a small governed work turn through a host AI client;
- inspect runtime receipts, Policy Trace, Document Trace, and missing evidence.

JIKUO is not the semantic judge. The host AI supplies compact semantic intent
when available. JIKUO records it, merges it with turn anchors and lifecycle
events, triggers matching policies, and displays evidence.

## 2. Install From Source

For the current source checkout:

```powershell
cd <workspace>
git clone https://github.com/jikuo-studio/jikuo.git
cd jikuo
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Check the installed entry points:

```powershell
.\.venv\Scripts\jikuo.exe --help
.\.venv\Scripts\jikuo-mcp.exe --help
```

For local development without an editable install:

```powershell
$env:PYTHONPATH='src'
python -B -m unittest discover -s tests -p "*_tests.py"
```

## 3. Try The Demo Starter Project

Before pointing JIKUO at your own documents, you can run the first-run checks
against the committed demo project:

```powershell
.\.venv\Scripts\jikuo.exe doctor --project-root examples/demo_project --format markdown
.\.venv\Scripts\jikuo.exe studio status --project-root examples/demo_project --format markdown
```

The demo includes public project documents and `.jikuo/project_context.yaml`.
It intentionally leaves activation settings, instruction files, active starter
policies, and runtime receipts incomplete so you can see how JIKUO explains
first-run gaps.
Some registry diagnostics are expected because the demo is a small user project,
not JIKUO's full product-development repository.

The demo guide is [`examples/demo_project/README.md`](../../examples/demo_project/README.md).

## 4. Inspect First-run Readiness

Run the first-use configuration review:

```powershell
.\.venv\Scripts\jikuo.exe doctor --format markdown
.\.venv\Scripts\jikuo.exe configure status --format markdown
```

Then inspect the Studio global read model:

```powershell
.\.venv\Scripts\jikuo.exe studio status --format markdown
```

The important first-run fields are:

- required blockers: setup items that prevent a normal first-use path;
- recommended actions: setup items that improve evidence quality or integration
  confidence;
- non-effects: what the read model did not do, especially that it did not write
  project state.

If a required blocker is visible, complete that guarded setup step before
claiming the project is ready.

`jikuo doctor` is the terminal-first summary. It uses the same Studio global
status read model as the frontend and reports install, first-run, activation,
policy, Document Rules, Studio, MCP, and runtime readiness without writing
project state.

## 5. Open Studio

Start the local read-only Studio console:

```powershell
.\.venv\Scripts\jikuo.exe studio serve --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/`.

Studio is intentionally thin. It should render the backend Studio read models
instead of reconstructing governance meaning in browser code.

<a id="first-run.activation-settings"></a>

## 6. Configure Activation Settings

Activation settings define how JIKUO should be invoked by a host:

- `ask`: the client should ask the user before the first governed turn;
- `semantic`: the host AI calls JIKUO when it classifies the user turn as
  governed work;
- `mounted`: a host adapter calls JIKUO before every user turn.

Use the Activation Settings surface in Studio, or an MCP client exposing:

- `jikuo.get_activation_settings`;
- `jikuo.plan_activation_settings_update`;
- `jikuo.apply_activation_settings_update`.

Preview the activation settings update first, review the expected write path
and approval phrase, then apply the guarded change. MCP availability or
instruction files alone do not prove strict mounted execution.

## 7. Configure MCP, Instructions, And Optional Hook

MCP setup works best after activation settings have been reviewed, because the
client instruction files need to know whether the project should ask first,
route semantically, or request mounted behavior.

Use this order for a continuous first-run setup:

1. Keep JIKUO installed at a stable local path.
2. Configure activation settings through preview and guarded apply.
3. Register the local stdio MCP server in the desktop client.
4. Restart the client so it reloads MCP tool discovery.
5. Verify a no-write JIKUO tool call.
6. Generate or review client instruction files.
7. Optionally enable the Codex project-local pre-turn hook.

The validated Windows preview MCP command is:

```text
command = "<JIKUO_HOME>\\.venv\\Scripts\\python.exe"
args = ["-B", "-m", "jikuo.integrations.mcp.server"]
cwd = "<PROJECT_ROOT>"
```

If the client can launch an installed executable directly, this form is also
acceptable:

```text
command = "<JIKUO_HOME>\\.venv\\Scripts\\jikuo-mcp.exe"
args = []
cwd = "<PROJECT_ROOT>"
```

After adding the server, restart the client and ask it to call:

```text
jikuo.get_runtime_status_card
```

Expected result:

- the client discovers the JIKUO tools;
- the response includes `card_markdown`;
- `.jikuo/runtime/last_card.md` is updated;
- no policy, task-session, or project-state guarded write is performed.

Then generate or refresh instruction files for the client:

```powershell
.\.venv\Scripts\jikuo.exe install --client codex --trigger-mode ask
```

Review the changed instruction file before committing it. Instruction files
tell the host AI when to call JIKUO; they do not prove strict mounted execution.

### Optional: Enable The Codex Pre-turn Hook

This repository includes a project-local Codex `UserPromptSubmit` proof hook:

- `.codex/hooks.json`
- `.codex/hooks/jikuo_user_prompt_submit.py`
- `.codex/hooks/README.md`

To use it in Codex, the user must trust the project `.codex/` layer through the
Codex hook review UI, or use `/hooks` in CLI builds that expose hook review.
After trust, submit a small test prompt in Codex.

Expected visible result:

- Codex receives additional context beginning with
  `JIKUO mounted pre-turn ran before substantive model work.`;
- the context shows a turn anchor, runtime card links, and any required
  follow-up tools;
- `.jikuo/runtime/history/*.md` receives a new `conversation_turn` card.

The hook is local and does not persist the raw prompt or transcript in
hook-owned files. It gives Codex a pre-turn JIKUO card and follow-up contract.
It is not a full lifecycle gate by itself: if the host AI writes files, it must
still run completion review before the final response.

If the client cannot run the hook, continue with MCP plus instruction files and
do not claim strict mounted execution. More detail:
[`docs/integrations/mcp_client_configuration_examples.md`](../integrations/mcp_client_configuration_examples.md)
and [`.codex/hooks/README.md`](../../.codex/hooks/README.md).

## 8. Activate Starter Policies

Open the Policy Configuration area in Studio and review the starter policy
pack status.

The first-use policy path is:

1. choose the starter pack;
2. preview the activation plan;
3. review included templates, report-only boundaries, expected write paths, and
   the approval phrase;
4. apply the guarded change;
5. refresh policy status and confirm active policies are visible.

Starter policies create baseline visibility. They do not make JIKUO infer
semantic intent and do not make report-only policies blocking by themselves.

After starter activation, use the same Policy Configuration area to preview and
apply active policy changes such as trigger refinement, deprecation,
supersession, and final-response gate updates. More detail:
[`docs/user/policy-management.md`](policy-management.md).

## 9. Review Document Rules

Open Document Rules in Studio before doing real work.

Document Rules answer these questions:

- which documents JIKUO uses as context;
- which documents are completion checks;
- which files are governance references;
- which configuration file Studio may update after a guarded apply.

The editable target is the project-local context file, currently
`.jikuo/project_context.yaml`. Package defaults and governance docs can explain
the setup, but Document Rules should not silently rewrite them.

For CLI-based review:

```powershell
.\.venv\Scripts\jikuo.exe studio document-rules plan --add-context-doc docs/user/getting-started.md --format markdown
```

Only apply a Document Rules plan after reviewing the generated plan JSON,
expected write path, and approval phrase.

More detail: [`docs/user/document-management.md`](document-management.md).

## 10. Run One Governed Work Turn

Use an AI host or MCP client that has access to the JIKUO tools. Ask for a
small, easy-to-verify change.

The host AI should provide compact semantic intent evidence for the turn, such
as policy scopes, requested outcome, execution boundary, response contract, and
a short redacted user expression. If a turn anchor is available, the host should
carry it into the task-start and completion-review calls.

JIKUO records the host-provided semantic intent and turn anchor. It does not
store raw prompts or transcripts, and it does not decide the semantics by
itself.

## 11. Run Completion Review And Inspect Receipts

After the work turn, inspect runtime receipts:

```powershell
.\.venv\Scripts\jikuo.exe show
.\.venv\Scripts\jikuo.exe show --last-card
.\.venv\Scripts\jikuo.exe studio status --format markdown
```

For source-tree adapter development, the completion review event is available
through the agent-flow CLI:

```powershell
.\.venv\Scripts\jikuo-agent-flow.exe propose --event completion_review --project-root <project-root> --semantic-intent-ref anchor:<turn_anchor> --inherit-semantic-intent --format json
```

In Studio, review:

- Policy Trace: which policies triggered for the selected round, what evidence
  is present, and what remains missing;
- Document Trace: expected documents, observed evidence, and gaps for the
  selected round;
- Current Limitations: why many visible `missing` reports are current product
  boundaries instead of hidden failures.

## 12. Understand Missing Evidence

The current version intentionally keeps missing evidence visible.

A missing report can mean:

- the host did not provide semantic intent or did not carry it into a lifecycle;
- the relevant policy is report-only;
- runtime history lacks a comparable structured round;
- observed-read proof is not yet as mature as write-side git/status evidence;
- completion applicability has not been fully automated for that policy;
- a broad or newly activated policy needs scope review.

This is a feature boundary, not automatically a defect. JIKUO cannot prove the
fact yet, so it exposes the gap.

More detail:

- [`docs/user/trace-and-evidence.md`](trace-and-evidence.md)
- [`docs/user/limitations.md`](limitations.md)

## 13. Done Criteria

A first-run project is ready for normal pre-release use when:

- `jikuo configure status` has no required first-run blockers;
- Studio opens and shows policy, document, runtime, and limitation summaries;
- the MCP client can call `jikuo.get_runtime_status_card`;
- client instruction files have been reviewed, or the user has explicitly
  chosen to stay MCP-only;
- any optional Codex hook is trusted and visibly producing pre-turn context
  before strict mounted behavior is claimed;
- starter policies have been reviewed and activated if the project needs the
  baseline pack;
- Document Rules point at the user's project documents;
- one governed work turn produces a visible runtime card;
- Policy Trace and Document Trace can be inspected by round;
- visible missing evidence is understood as either a configuration action, a
  host evidence gap, a current feature boundary, or a real workflow gap.
