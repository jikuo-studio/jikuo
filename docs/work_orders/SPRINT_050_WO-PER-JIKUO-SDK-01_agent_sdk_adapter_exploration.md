# SPRINT_050_WO-PER-JIKUO-SDK-01: Agent SDK And Agentic Platform Adapter Exploration

> **Status**: Draft, pre-MCP architecture exploration
> **Product meaning**: explore how Agent SDKs and agentic development platforms can help JIKUO grow into orchestrated development workflows without replacing the JIKUO kernel, MCP wrapper, policy store, or runtime visibility authority.
> **Scope rule**: leave extension points before MCP implementation; do not introduce a required dependency on any single vendor SDK or platform in this slice.

## 1. Why This Slice Now

JIKUO is approaching its MCP wrapper. Before that wrapper becomes mature, the product should understand whether Agent SDKs and agentic development platforms change the long-term adapter shape.

Current official references show related but different shapes:

- OpenAI Agents SDK: agents, tools, handoffs, guardrails, sessions, tracing, and MCP-backed tools.
  - `https://openai.github.io/openai-agents-python/`
  - `https://openai.github.io/openai-agents-python/agents/`
  - `https://openai.github.io/openai-agents-python/mcp/`
  - `https://openai.github.io/openai-agents-python/tracing/`
  - `https://openai.github.io/openai-agents-python/guardrails/`
- Claude Agent SDK: Claude Code's agent loop, context management, built-in tools, MCP, permissions, hooks, subagents, sessions, structured output, checkpointing, and observability exposed as SDK surfaces.
  - `https://code.claude.com/docs/en/agent-sdk/overview`
- Google Agent Development Kit (ADK): an open agent development framework with agents, tools, multi-agent orchestration, graph workflows, evaluation, deployment, and model/provider adapters.
  - `https://adk.dev/`
- Google Antigravity: an agentic development platform / IDE with editor, terminal, browser, manager surface, asynchronous multi-agent work, and review artifacts. It is not treated as a plain SDK in this task.
  - `https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/`
- Vercel AI SDK: a JavaScript / TypeScript framework for building AI agents and agentic applications with tools, step control, middleware, MCP client support, and UI streaming surfaces.
  - `https://ai-sdk.dev/docs/agents/overview`
  - `https://ai-sdk.dev/docs/ai-sdk-core/mcp-tools`

For JIKUO, the useful question is not "should an SDK or platform replace MCP or the kernel?" The useful question is:

- where should JIKUO keep stable local governance authority?
- where can vendor SDKs or platforms become optional orchestration adapters?
- what extension points must MCP and instruction distribution preserve so future SDK / platform integration does not require rewriting the kernel?

## 2. User Scenario

A JIKUO developer wants to use agentic development workflows before JIKUO has a fully mature MCP surface.

The developer needs JIKUO to remain:

- deterministic after activation
- visible through chat-ready cards and `.jikuo/runtime/`
- auditable through local evidence and policy records
- portable across clients rather than locked to one orchestration runtime

At the same time, the developer wants to know whether an SDK or agentic platform layer could later coordinate specialized agents such as:

- governance / policy agent
- implementation agent
- documentation agent
- review / verification agent

## 3. In Scope

This exploration should produce a short architecture decision record or updated task-map section that:

- maps cross-vendor primitives to JIKUO concepts:
  - Agents -> specialized governance / implementation / review roles
  - Tools / built-in tools / platform tool use -> calls into JIKUO CLI or MCP tools
  - Handoffs -> controlled transfer between specialized development roles
  - Permissions / hooks / guardrails -> optional validation around SDK-side or platform-side tool calls, not a replacement for JIKUO policy evidence
  - Tracing / observability / artifacts / checkpointing -> development review surfaces, not authoritative JIKUO audit storage unless explicitly imported as evidence
- compares at least OpenAI Agents SDK, Claude Agent SDK, Google ADK, Google Antigravity, and Vercel AI SDK at the level of product implications
- records capability differences rather than assuming hook / callback parity across all SDKs
- defines whether the first SDK path should consume the future JIKUO MCP server rather than call private internals directly
- identifies packaging implications such as optional extras per adapter family rather than a required dependency
- adds MCP implementation constraints that preserve SDK compatibility:
  - stable structured tool schemas
  - card-only runtime status tools
  - explicit display directives
  - local runtime snapshot refs
  - privacy-return boundaries
- updates `JIKUO-INTG-01` instruction guidance if SDK- or platform-specific runner instructions are useful later

## 4. Out Of Scope

This slice must not implement:

- an Agent SDK runner
- an Antigravity-specific pack, hook, or workspace setup
- an OpenAI-hosted workflow
- replacement policy evaluation
- replacement evidence checking
- replacement `.jikuo/runtime/` audit files
- SDK traces as official JIKUO evidence
- direct dependency installation
- client-specific plugin packaging
- MCP wrapper implementation
- JavaScript / TypeScript package implementation for Vercel AI SDK

## 5. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Agent SDK / platform extension posture review | user asks how Agent SDKs and agentic platforms affect JIKUO -> maintainer reviews official OpenAI / Claude / Google ADK / Antigravity / Vercel references -> maps agents / tools / handoffs / guardrails / permissions / tracing / artifacts / MCP client support to JIKUO atoms -> records optional adapter posture -> updates MCP / INTG extension constraints | `CAP-AGENTS-SDK-ADAPTER-EXPLORATION-01`; `CAP-INTEGRATION-NEUTRALITY-CONTRACT-01`; `CAP-MCP-AGENT-FLOW-WRAPPER-01`; `CAP-MCP-RUNTIME-STATUS-CARD-01`; `CAP-UNIVERSAL-INSTRUCTION-FILE-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | docs-only; no dependency, no hosted runtime, no new write path |

## 6. Acceptance Criteria

- The task map names `JIKUO-SDK-01` as a pre-MCP / MCP-adjacent exploration item.
- MCP implementation remains blocked until the SDK extension posture is accepted or explicitly deferred.
- The accepted posture states that the JIKUO kernel remains authoritative for policy, evidence, approvals, and runtime visibility.
- The accepted posture compares OpenAI Agents SDK, Claude Agent SDK, Google ADK, Google Antigravity, and Vercel AI SDK separately enough that SDK frameworks, JS/TS app frameworks, and IDE/platform flows are not conflated.
- The accepted posture treats hooks / callbacks / guardrails as adapter-specific enforcement enhancements, not a universal SDK guarantee.
- The accepted posture states whether future SDK / platform integrations should consume JIKUO through MCP, CLI, or a public adapter API.
- Any future SDK tracing, platform artifact, checkpoint, or observability use is classified as development review material unless separately promoted into JIKUO evidence through an approved policy.
- No required runtime dependency on OpenAI Agents SDK, Claude Agent SDK, Google ADK, Vercel AI SDK, or Antigravity is added by this slice.

## 7. Notes For Later Implementation

Likely future shape if approved:

- JIKUO core stays local and deterministic.
- MCP remains the stable cross-client tool layer.
- Vendor SDKs may become optional orchestration layers that call JIKUO MCP tools.
- Agentic IDEs / platforms such as Antigravity may become client environments where JIKUO instructions, MCP tools, runtime card links, and local audit files need to be visible.
- SDK traces, platform artifacts, screenshots, browser recordings, and checkpoints can help development review, but `.jikuo/runtime/`, policy-store decisions, task-session evidence, and explicit approval records remain the product audit source.

Potential future backlog placeholders after MCP stabilizes:

- `JIKUO-INTG-CLAUDE-AGENT-SDK-01`
- `JIKUO-INTG-OPENAI-AGENTS-SDK-01`
- `JIKUO-INTG-GOOGLE-ADK-01`
- `JIKUO-INTG-VERCEL-AI-SDK-01`
- `JIKUO-INTG-ANTIGRAVITY-01`
