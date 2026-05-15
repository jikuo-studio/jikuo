# JIKUO

JIKUO is an AI-primary process governance harness for desktop agents, MCP
clients, and future agent SDK integrations.

It helps an AI-assisted project make its working state visible: which policies
are active, which ones triggered, what evidence is missing, which task-session
is being worked, and where the user can independently verify the runtime card.

JIKUO is currently an early standalone package. Stage A MCP support is
implemented for no-write status, card, and proposal tools. Guarded-write MCP
tools remain blocked until explicitly accepted.

## What JIKUO Provides

- Project-local `.jikuo/` state for policies, task sessions, runtime cards, and
  project context.
- Policy runtime status cards that can be shown in chat and verified through
  `.jikuo/runtime/last_card.md` or `jikuo show`.
- Task-session records for durable process memory without capturing raw chat
  transcripts.
- Starter policy templates with provenance for first-use project bootstrap.
- A Stage A MCP server wrapper around stable no-write JIKUO atoms.
- Integration docs for desktop clients and future SDK adapters.

## Quickstart

From the repository root:

```powershell
python -m pip install -e ".[dev]"
python -B -m unittest discover -s tests -p "*_tests.py"
jikuo show
jikuo-mcp --help
```

For local source-tree development without an editable install:

```powershell
$env:PYTHONPATH='src'
python -B -m unittest discover -s tests -p "*_tests.py"
```

## MCP Stage A

The MCP server entry point is:

```powershell
python -B -m jikuo.integrations.mcp.server
```

or, after installation:

```powershell
jikuo-mcp
```

Stage A exposes eight no-write tools:

- `jikuo.status`
- `jikuo.get_runtime_status`
- `jikuo.get_runtime_status_card`
- `jikuo.get_display_card`
- `jikuo.propose_task_start`
- `jikuo.propose_policy_write_plan`
- `jikuo.propose_policy_evolution_plan`
- `jikuo.propose_policy_template_import_plan`

Client configuration examples live in
[`docs/integrations/mcp_client_configuration_examples.md`](docs/integrations/mcp_client_configuration_examples.md).

## Documentation Map

- [`docs/README.md`](docs/README.md): internal documentation layout and mount
  rules.
- [`docs/governance/jikuo_productization_task_map.md`](docs/governance/jikuo_productization_task_map.md):
  active task map and capability registry.
- [`docs/governance/jikuo_execution_mounts.md`](docs/governance/jikuo_execution_mounts.md):
  current execution mount set.
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

The current package metadata is `Proprietary`. The external release license is
an explicit product decision and has not been changed by the MCP Stage A work.
