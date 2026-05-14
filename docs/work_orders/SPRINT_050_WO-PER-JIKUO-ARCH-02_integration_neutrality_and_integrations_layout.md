# SPRINT_050_WO-PER-JIKUO-ARCH-02: Integration Neutrality And Integrations Layout

> **Status**: Accepted on 2026-05-14, immediate pre-MCP architecture contract
> **Product meaning**: keep JIKUO's governance kernel independent from any one client, protocol, Agent SDK, IDE, or platform integration.
> **Scope rule**: define boundaries and planned layout only; do not implement MCP, Agent SDK plugins, hooks, or client packs in this slice.

## 1. Why This Slice Now

`JIKUO-MCP-01` is close enough that directory placement now matters.

If the first MCP wrapper lands directly in `src/jikuo/`, it can accidentally make MCP a de facto part of the kernel. Later Claude Agent SDK, OpenAI Agents SDK, Google ADK, Vercel AI SDK, Antigravity-style platform, Codex, Cursor, or Claude Desktop integrations would then either copy MCP assumptions or force a cleanup.

This slice prevents that by declaring integration neutrality before implementation.

## 2. Integration Neutrality Rule

JIKUO core capability must be implemented in an integration-neutral way.

Core code under `src/jikuo/` owns:

- policy store inspection and evaluation
- evidence matching and evidence projection
- guarded approval and apply semantics
- task / insight / follow-up routing evidence
- runtime visibility projection to `.jikuo/runtime/`
- package-owned reusable templates and starter packs

Integration code must live under `src/jikuo/integrations/` when it depends on a specific protocol, SDK, client, IDE, or platform.

Planned integration layout:

```text
src/jikuo/
  agent_flow.py
  policy_store.py
  runtime_visibility.py
  ...
  integrations/
    mcp/
    claude_agent_sdk/
    openai_agents_sdk/
    google_adk/
    vercel_ai_sdk/
    antigravity/
    codex/
    claude_code/
    claude_desktop/
    cursor/
```

This layout is planned, not fully created by this slice.

## 3. Boundary Rules

1. Core APIs must be callable without importing any integration package.
2. Integration adapters may depend on core APIs, but core APIs must not depend on integration adapters.
3. Protocol-specific response shaping belongs in the relevant integration directory.
4. Shared display contracts may live in core only when they are protocol-neutral data structures.
5. MCP remains the preferred cross-client tool protocol, but it is still an integration adapter, not the kernel.
6. Agent SDK hooks, guardrails, callbacks, or platform artifacts are enhancement layers; they do not replace JIKUO policy evidence, approval records, or `.jikuo/runtime/` visibility.
7. Future SDK / platform adapters should consume JIKUO through MCP, CLI, or public package APIs rather than private module internals.

## 4. Immediate MCP-01 Consequence

`JIKUO-MCP-01` should be anchored under:

```text
src/jikuo/integrations/mcp/
```

Expected planned modules:

- `src/jikuo/integrations/mcp/adapter.py`
- `src/jikuo/integrations/mcp/server.py`
- `src/jikuo/integrations/mcp/schema.py` if schema isolation is needed

The MCP adapter can wrap stable core atoms, but it must not introduce new governance capability that only MCP can use.

## 5. API Neutrality Review

Before MCP implementation, review whether `agent_flow.py`, `policy_store.py`, `runtime_visibility.py`, and template / starter-pack APIs expose package-safe functions that can be called by:

- CLI
- MCP wrapper
- Agent SDK plugins
- Python import in developer-owned code
- future UI / dashboard surfaces

Review questions:

- Does the core API require command-line parsing to perform useful work?
- Does it return structured results without requiring stdout scraping?
- Does it allow integrations to attach display directives without changing policy evaluation?
- Does it preserve privacy classifications and local-only fields?
- Does it update runtime visibility through a core helper rather than an integration-specific side effect?

## 6. Out Of Scope

This slice must not implement:

- MCP server runtime
- Agent SDK plugins
- client hooks
- `JIKUO.md` sync
- dependency extras
- hosted orchestration
- new governance atoms

## 7. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Integration-neutral wrapper planning | maintainer reviews next MCP / SDK work -> declares core-vs-integration boundary -> anchors MCP path under `src/jikuo/integrations/mcp/` -> records API-neutrality review gate -> future wrappers consume core APIs without becoming kernel | `CAP-INTEGRATION-NEUTRALITY-CONTRACT-01`; `CAP-MCP-AGENT-FLOW-WRAPPER-01`; `CAP-AGENTS-SDK-ADAPTER-EXPLORATION-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | docs-only; no integration package implementation; no dependency change |

## 8. Acceptance Criteria

- The task map registers `JIKUO-ARCH-02` and `CAP-INTEGRATION-NEUTRALITY-CONTRACT-01`.
- `JIKUO-MCP-01` planned implementation path is updated from root-level `src/jikuo/mcp_*` modules to `src/jikuo/integrations/mcp/`.
- SEC-01 / trust baseline includes the Integration Neutrality Rule.
- MCP implementation is blocked until this contract is accepted or explicitly deferred.
- Agent SDK / platform plugins remain future work after MCP is stable.
- No source package dependencies, imports, or runtime behavior change in this slice.

## 9. Accepted Result

Accepted on 2026-05-14 as a pre-MCP architecture baseline.

Accepted decisions:

- JIKUO core remains integration-neutral.
- Integration-specific code belongs under `src/jikuo/integrations/`.
- `JIKUO-MCP-01` implementation is anchored under `src/jikuo/integrations/mcp/`.
- MCP, Agent SDKs, IDE platforms, client hooks, and instruction packs are adapters over core APIs, not the governance kernel.
- Hooks, callbacks, guardrails, traces, checkpoints, and platform artifacts are enhancement / review surfaces until a later approved policy imports them as evidence.

API-neutrality precheck:

- `agent_flow.build_proposal` and `agent_flow.build_apply_result` already return structured dictionaries and can be called without CLI stdout scraping.
- `policy_store.evaluate_policy_triggers`, `build_policy_write_plan`, and `build_policy_evolution_plan` already expose structured core behavior.
- `runtime_visibility.prepare_agent_flow_snapshot`, `persist_prepared_agent_flow_snapshot`, `load_state_summary`, and `load_last_card` provide reusable local visibility helpers.
- Future MCP / SDK adapters should call these core functions or a small facade over them, not CLI `main()` functions.
- The fuller MCP pre-implementation API neutrality review is tracked by `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-03_mcp_pre_implementation_api_neutrality_review.md`.
