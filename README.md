# JIKUO

JIKUO is an AI-primary process governance harness for desktop agents, MCP
clients, and future agent SDK integrations.

It helps an AI-assisted project make its working state visible: which policies
are active, which ones triggered, what evidence is missing, which task-session
is being worked, and where the user can independently verify the runtime card.

JIKUO is currently an early standalone package in source-available
noncommercial preview. The current MCP MVP exposes 24 local stdio tools across
no-write status/cards/proposals, first-use configuration review, activation
settings, conversation routing, policy suggestion review, MCP Sampling
semantic-provider probing, and guarded-write apply paths.

This repository is licensed for noncommercial use under the PolyForm
Noncommercial License 1.0.0. Commercial use, commercial hosted service use,
production business use, and brand/IP terms require a separate written
agreement.

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
  diagnostics, pending-decision, panel-registry, and action-registry summaries
  without scraping Markdown cards.
- A local read-only Studio console exposed through `jikuo studio serve`, backed
  by the same Studio read models and not by frontend-owned governance logic.
- Public MCP configuration examples for supported desktop clients. Internal
  proof records exist for release validation, but they are not first-run user
  onboarding documents.
- Integration-neutral core APIs reserved for MCP, future Agent SDK wrappers,
  Studio, plugins, and client adapters.

## First-run Quickstart

The complete first-run flow lives in
[`docs/user/getting-started.md`](docs/user/getting-started.md). It covers
install, Studio startup, first-run configuration, starter policy activation,
Document Rules, one governed work turn, completion review, receipt inspection,
and current missing-evidence limits.

Install from the current source repository:

```powershell
cd <workspace>
git clone https://github.com/jikuo-studio/jikuo.git
cd jikuo
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\jikuo.exe --help
.\.venv\Scripts\jikuo-mcp.exe --help
```

Inspect first-run readiness and current runtime receipts:

```powershell
.\.venv\Scripts\jikuo.exe show
.\.venv\Scripts\jikuo.exe configure status --format markdown
.\.venv\Scripts\jikuo.exe studio status --format markdown
```

Run the local read-only Studio console:

```powershell
.\.venv\Scripts\jikuo.exe studio serve --host 127.0.0.1 --port 8765
```

Then complete these setup steps before treating the project as ready:

- review required first-run blockers and recommended setup actions;
- configure activation settings through preview and guarded apply;
- activate starter policies through preview and guarded apply when baseline
  policy coverage is needed;
- review Document Rules and point them at the user's project documents;
- run a small governed work turn through a host AI client that supplies compact
  semantic intent when available;
- inspect `jikuo show`, Policy Trace, Document Trace, Current Limitations, and
  completion-review receipts.

JIKUO does not perform semantic judgment by itself. The host AI supplies compact
semantic intent; JIKUO records it, merges it with turn anchors and lifecycle
events, triggers matching policies, and displays evidence.

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

Maintainer proof steps and retained proof records live under `docs/integrations/`.
They are release-validation evidence, not the first-run user path.

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

- [`README.md`](README.md): product-facing source-available noncommercial
  preview entry point.
- [`docs/README.md`](docs/README.md): internal documentation layout and mount
  rules.
- [`docs/user/getting-started.md`](docs/user/getting-started.md): first-run
  quickstart covering install, configuration, starter policies, Document Rules,
  governed work, completion review, and receipt inspection.
- [`docs/user/document-management.md`](docs/user/document-management.md):
  first-use guide for Document Rules, local mount layering, and guarded
  document configuration changes.
- [`docs/user/policy-management.md`](docs/user/policy-management.md):
  first-use guide for starter policies, active policy configuration,
  final-response gates, path filters, deprecation, and supersession.
- [`docs/user/trace-and-evidence.md`](docs/user/trace-and-evidence.md):
  guide for Policy Trace, Document Trace, turn anchors, and missing evidence
  classifications.
- [`docs/user/limitations.md`](docs/user/limitations.md): current product
  boundaries, including why many `missing` reports are visible boundary
  disclosures rather than hidden failures.
- [`docs/governance/jikuo_productization_task_map.md`](docs/governance/jikuo_productization_task_map.md):
  legacy human-readable roadmap projection.
- [`docs/registry/`](docs/registry/): draft structured registry shards for
  work orders, capabilities, scenario chains, and mount sets.
- [`docs/schemas/execution_events_v0_draft.md`](docs/schemas/execution_events_v0_draft.md):
  draft structured execution-event schema for future analytics.
- [`docs/governance/jikuo_execution_mounts.md`](docs/governance/jikuo_execution_mounts.md):
  current execution mount set.
- [`docs/integrations/mcp_client_configuration_examples.md`](docs/integrations/mcp_client_configuration_examples.md):
  user-safe MCP configuration examples using placeholders instead of
  maintainer-local paths.
- [`docs/work_orders/`](docs/work_orders/): accepted and in-progress work
  orders.
- [`docs/insights/`](docs/insights/): captured development insights and their
  registry.

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

JIKUO is distributed under the PolyForm Noncommercial License 1.0.0:

- SPDX identifier: `PolyForm-Noncommercial-1.0.0`
- License file: [`LICENSE.md`](LICENSE.md)
- Canonical terms: <https://polyformproject.org/licenses/noncommercial/1.0.0/>

This is a source-available noncommercial preview, not an OSI open-source
release. Commercial use, commercial hosted service use, production business
use, brand/IP rights, and contribution terms require separate written approval
or future project terms.
