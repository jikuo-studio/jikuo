# JIKUO

JIKUO is an AI-primary process governance harness for desktop agents, MCP
clients, and future agent SDK integrations.

It helps an AI-assisted project make its working state visible: which policies
are active, which ones triggered, what evidence is missing, which task-session
is being worked, and where the user can independently verify the runtime card.

JIKUO is currently an early standalone package in private preview. The current
MCP MVP exposes 24 local stdio tools across no-write status/cards/proposals,
first-use configuration review, activation settings, conversation routing,
policy suggestion review, MCP Sampling semantic-provider probing, and
guarded-write apply paths.

This repository is not a public release yet. The package metadata remains
`Proprietary` while the external source-available preview license and brand/IP
gate are being decided.

## What JIKUO Provides

- Project-local `.jikuo/` state for policies, task sessions, runtime cards, and
  project context.
- Policy runtime status cards that can be shown in chat and verified through
  `.jikuo/runtime/last_card.md` or `jikuo show`.
- Task-session records for durable process memory without capturing raw chat
  transcripts.
- Starter policy templates with provenance for first-use project bootstrap.
- A local stdio MCP server exposing 24 tools for status, cards, proposals,
  configuration review, activation settings, routing, MCP Sampling semantic
  provider probing, and guarded writes.
- A no-write Studio global status read model exposed through
  `jikuo studio status`, so a future thin console can read runtime,
  activation, configuration, integration, policy-management, registry,
  diagnostics, pending-decision, and action-preview summaries without scraping
  Markdown cards.
- Accepted private-preview MCP use in Codex and Claude, plus proof docs for
  Cursor, VS Code + GitHub Copilot Agent mode, and regression checks.
- Integration-neutral core APIs reserved for MCP, future Agent SDK wrappers,
  Studio, plugins, and client adapters.

## Quickstart

For private GitHub preview proof:

```powershell
cd D:\personal_project
git clone https://github.com/jikuo-studio/jikuo.git Jikuo_private_preview
cd D:\personal_project\Jikuo_private_preview
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\jikuo.exe --help
.\.venv\Scripts\jikuo-mcp.exe --help
.\.venv\Scripts\jikuo.exe show
.\.venv\Scripts\jikuo.exe studio status --format markdown
```

For local source-tree development without an editable install:

```powershell
$env:PYTHONPATH='src'
python -B -m unittest discover -s tests -p "*_tests.py"
```

## MCP MVP

The MCP server entry point is:

```powershell
python -B -m jikuo.integrations.mcp.server
```

or, after installation:

```powershell
jikuo-mcp
```

The current MCP surface exposes 24 tools:

Status, cards, and no-write proposals:

- `jikuo.status`
- `jikuo.get_policy_management_status`
- `jikuo.get_runtime_status`
- `jikuo.get_runtime_status_card`
- `jikuo.get_display_card`
- `jikuo.propose_task_start`
- `jikuo.propose_policy_write_plan`
- `jikuo.propose_policy_evolution_plan`
- `jikuo.propose_policy_distribution_review`
- `jikuo.propose_policy_template_publication_plan`
- `jikuo.propose_starter_manifest_publication_plan`
- `jikuo.propose_policy_template_import_plan`

First-use configuration and activation settings:

- `jikuo.get_configuration_status`
- `jikuo.get_activation_settings`
- `jikuo.plan_activation_settings_update`
- `jikuo.apply_activation_settings_update`

Conversation routing and policy suggestion review:

- `jikuo.route_user_request`
- `jikuo.propose_policy_suggestions`

MCP Sampling semantic provider proof:

- `jikuo.probe_sampling_semantic_intent`

Guarded-write apply tools:

- `jikuo.apply_task_session_evidence_update`
- `jikuo.apply_policy_evolution_write`
- `jikuo.apply_policy_template_activation`
- `jikuo.apply_policy_template_publication`
- `jikuo.apply_starter_manifest_publication`

Guarded-write tools require explicit confirmation and an approval phrase. They
must not silently create durable `.jikuo/` state without user approval.

MCP configuration examples live in
[`docs/integrations/mcp_client_configuration_examples.md`](docs/integrations/mcp_client_configuration_examples.md).

Manual client proof steps live in
[`docs/integrations/mcp_client_proof_playbook.md`](docs/integrations/mcp_client_proof_playbook.md).

## Trigger Modes

JIKUO supports three activation postures in user-facing setup:

- `ask`: the client should ask the user to choose before the first governed
  turn.
- `semantic`: the agent calls JIKUO when a user turn appears to carry governed
  work.
- `mounted`: a host adapter calls JIKUO before every user turn.

MCP plus instruction files makes tools available, but it is not strict mounted
execution by itself. Strict mounted execution requires a future client hook,
plugin, Agent SDK wrapper, Studio/local proxy, or other host adapter that calls
JIKUO before each user turn.

## Documentation Map

- [`README.md`](README.md): product-facing private preview entry point.
- [`docs/README.md`](docs/README.md): internal documentation layout and mount
  rules.
- [`docs/governance/jikuo_productization_task_map.md`](docs/governance/jikuo_productization_task_map.md):
  legacy human-readable roadmap projection.
- [`docs/registry/`](docs/registry/): draft structured registry shards for
  work orders, capabilities, scenario chains, and mount sets.
- [`docs/schemas/execution_events_v0_draft.md`](docs/schemas/execution_events_v0_draft.md):
  draft structured execution-event schema for future analytics.
- [`docs/governance/jikuo_execution_mounts.md`](docs/governance/jikuo_execution_mounts.md):
  current execution mount set.
- [`docs/work_orders/`](docs/work_orders/): accepted and in-progress work
  orders.
- [`docs/insights/`](docs/insights/): captured development insights and their
  registry.
- [`docs/integrations/mcp_client_proof_playbook.md`](docs/integrations/mcp_client_proof_playbook.md):
  fresh-clone proof workflow for supported desktop AI clients.

## Development

Run the full test suite:

```powershell
python -B -m unittest discover -s tests -p "*_tests.py"
```

Pytest is available as a developer entry point after installing `.[dev]`:

```powershell
pytest
```

## License

The current package metadata is `Proprietary`. The external release license is
an explicit product decision and has not changed yet.

Current product direction is a private GitHub preview followed by a possible
source-available community preview. Public review should wait until the license,
brand notice, contribution terms, privacy sweep, and IP gate are accepted.
