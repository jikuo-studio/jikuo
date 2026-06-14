# JIKUO

JIKUO is a local process-governance layer for AI-assisted software work.

It is built for teams and solo maintainers who want an AI coding agent's work
to leave inspectable receipts: what the user asked for, which policies were in
scope, which evidence was observed, what is still missing, and where the same
runtime card can be verified outside the chat response.

The current release is a source-available noncommercial preview. It is useful
for evaluating the product loop, local CLI, read-only Studio console, MCP
tools, starter policy templates, runtime cards, and guarded write plans. It is
not yet a polished SaaS product, a hosted service, or a strict enforcement
layer unless a host adapter is actually calling JIKUO at the right lifecycle
points.

The current MCP MVP exposes 24 local stdio tools across no-write
status/cards/proposals, first-use configuration review, activation settings,
conversation routing, policy suggestion review, MCP Sampling semantic-provider
probing, and guarded-write apply paths.

This repository is licensed for noncommercial use under the PolyForm
Noncommercial License 1.0.0. Commercial use, commercial hosted service use,
production business use, and brand/IP terms require a separate written
agreement.

## Why It Exists

AI coding sessions often end with a summary that is hard to audit. JIKUO makes
the process state visible while keeping the host AI responsible for semantic
judgment.

In the current preview, JIKUO focuses on three practical questions:

- What governance context was active for this work?
- What evidence did the local project actually receive?
- Which gaps are configuration issues, report-only policy signals, product
  boundaries, or real workflow evidence gaps?

## What You Can See Today

The first public preview is intentionally local and inspection-first:

- `jikuo doctor` shows first-run readiness, configuration gaps, integration
  posture, and diagnostics without writing project state.
- `jikuo show` and `.jikuo/runtime/last_card.md` show the latest runtime card
  that a user can verify outside the chat UI.
- `jikuo studio serve` opens a local read-only Studio console backed by the
  same backend read models as the CLI.
- Policy Trace explains triggered policies, missing evidence, and report-only
  boundaries for the selected runtime round.
- Document Rules explain which project documents are configured as context,
  completion checks, or governance references.
- Guarded apply tools preview write paths and approval phrases before changing
  durable `.jikuo/` state.

The normal evaluation path is: install from source, run `jikuo doctor`, open
Studio, review activation settings and starter policies, run one small governed
AI work turn, then inspect the Work receipt and visible missing-evidence
classification.

## Current Boundaries

These limits are part of the preview contract:

- JIKUO does not decide semantic intent by itself. The host AI supplies compact
  semantic intent when available.
- Studio is currently a local read-only console, not a hosted product
  dashboard.
- MCP availability is not the same as strict mounted execution. Strict mounted
  behavior requires a host adapter or hook that calls JIKUO before the relevant
  user turn.
- Many starter policies are report-only. Missing evidence is visible, but it is
  not automatically a blocking failure.
- Runtime history is not yet the full DATA-01 structured event ledger.
- There is no public marketing site yet; this README is the primary public
  landing surface for the preview.

See [`docs/user/limitations.md`](docs/user/limitations.md) for the complete
user-facing limitations guide.

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

### Current Platform Status

JIKUO preview is currently developed and primarily validated on Windows, using
local Python virtual environments and stdio MCP clients. The core Python
package and MCP server are intended to be portable, but macOS and Linux MCP
client setup paths are not yet covered by the same release-validation evidence.
Treat non-Windows MCP use as preview-level until dedicated setup notes and CI
coverage are added.

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

### Try The Local Studio First

After installing, start the local read-only Studio console against the project
you want to inspect:

```powershell
.\.venv\Scripts\jikuo.exe studio serve --project-root <your-project> --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/` to inspect first-run readiness, activation
settings, starter policies, Document Rules, runtime receipts, Policy Trace,
Document Trace, and current limitations.

Studio is local and read-only by default. Guarded configuration changes still
require preview, an explicit approval phrase, and the matching apply action.

Inspect first-run readiness and current runtime receipts:

```powershell
.\.venv\Scripts\jikuo.exe doctor --format markdown
.\.venv\Scripts\jikuo.exe show
.\.venv\Scripts\jikuo.exe configure status --format markdown
.\.venv\Scripts\jikuo.exe studio status --format markdown
```

Try the non-private demo starter project before pointing JIKUO at your own
documents:

```powershell
.\.venv\Scripts\jikuo.exe doctor --project-root examples/demo_project --format markdown
.\.venv\Scripts\jikuo.exe studio status --project-root examples/demo_project --format markdown
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

The validated preview MCP setup is local stdio on Windows. For desktop client
configuration, prefer an explicit virtual-environment executable instead of
relying on the client's inherited `PATH`:

```powershell
<JIKUO_HOME>\.venv\Scripts\jikuo-mcp.exe
```

or the equivalent module entry point:

```powershell
<JIKUO_HOME>\.venv\Scripts\python.exe -B -m jikuo.integrations.mcp.server
```

Use a stable local checkout path for `<JIKUO_HOME>` and avoid committing
maintainer-local paths such as `D:\personal_project\Jikuo` into another
project's shared client configuration.

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
- [`examples/demo_project/`](examples/demo_project/): non-private starter
  project for learning first-run readiness, starter policy preview, Document
  Rules, and Studio status without maintainer-local documents.
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
