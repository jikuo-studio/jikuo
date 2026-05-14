# SPRINT_050_WO-PER-JIKUO-LIVE-11: Deterministic Harness Chat Return Contract

> **Product meaning**: JIKUO is a tool-backed harness after activation, not a probabilistic prompt preference. Critical policy flow state must be visible, traceable, and auditable in the same desktop chat.
> **Kernel compatibility**: reuses the existing local deterministic runner and policy runtime card; it does not add gates, automatic action execution, new condition vocabulary, or broader writes.
> **Current slice**: `agent_flow.py` JSON output now carries `chat_ready_markdown` so MCP / desktop-agent callers can return the exact card surface instead of relying on agent summarization.
> **User scenario**: A desktop Agent calls JIKUO during governed work and must show the user the policy runtime card, approval boundary, write effects, and atom trace without asking the user to inspect CLI JSON.
> **Runtime chain**: desktop event -> JIKUO runner or future MCP tool -> structured result plus `chat_ready_markdown` -> same-chat card surfacing -> user review / approval / audit.
> **Bridge objects**: `jikuo.chat_ready_markdown.v0`; `jikuo.agent_flow_proposal.v1`; `jikuo.agent_flow_apply_result.v0`; `jikuo.policy_runtime_status.v0`.

## Product Semantics

The trigger model has two phases:

1. Activation discovery: the agent or user decides whether a desktop workflow is inside JIKUO coverage.
2. Harness execution: once inside coverage, the runner / MCP tool must be invoked and its returned cards must be surfaced.

Only the first phase may be suggestive. The second phase is a harness obligation.

A governed desktop response is incomplete when:

- JIKUO was invoked but `policy_runtime_status` was not shown when present
- the agent replaced returned cards with an informal summary
- approval boundaries or write / non-write effects were hidden
- atom trace and evidence state were dropped from the user-visible result
- MCP or JSON integration returned structured fields but no chat-ready surface

## Scope

In scope:

- add `chat_ready_markdown_schema: jikuo.chat_ready_markdown.v0` to JSON proposal / apply output
- add `chat_ready_markdown` to JSON proposal / apply output
- update the desktop-agent instruction pack to require card surfacing after runner invocation
- update the MCP work order so future tools return chat-ready text plus structured results
- register the harness chat-return chain and atom in the task map

Out of scope:

- automatic gate enforcement
- automatic policy action execution
- frontend card renderer
- MCP server implementation
- starter policy semantics
- durable policy writes beyond existing guarded apply paths

## Scenario-Chain-Atom Registration Evidence

Scenario chain:

- chain_id: `desktop_chat_harness_surfacing`
- user scenario: a desktop Agent has invoked JIKUO and must return the tool-rendered governance surface to the user instead of summarizing it away
- operation chain: agent invokes runner / future MCP tool -> tool returns structured result plus `chat_ready_markdown` -> agent posts the chat-ready markdown -> user sees policy runtime status, write boundaries, and atom trace in chat

Registered atoms:

- `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`
- `CAP-POLICY-RUNTIME-STATUS-CARD-01`
- `CAP-AGENT-FLOW-01`
- `CAP-MCP-AGENT-FLOW-WRAPPER-01`

Evidence:

- This work order declares the scenario chain and atom list.
- `jikuo_productization_task_map.md` registers the same chain and atom.
- `agent_flow_tests.py` asserts JSON proposal / apply output includes `chat_ready_markdown`.

## Acceptance Evidence

Required:

- `agent_flow.py propose --format json` includes `chat_ready_markdown_schema`.
- `agent_flow.py propose --format json` includes a Markdown string headed by `# JIKUO Agent Flow Proposal`.
- A proposal against an active policy-store fixture includes `## Policy runtime status` in `chat_ready_markdown`.
- `agent_flow.py apply --format json` includes `chat_ready_markdown_schema`.
- Existing Markdown output remains the direct chat-ready surface.
- Proposal mode remains no-write.

Validation command:

```powershell
$env:PYTHONPATH='src'
python -B -m unittest tests.agent_flow_tests
python -B -m unittest discover -s tests -p "*_tests.py"
```
