# INSIGHT-2026-05-14: Agent SDK And Agentic Platform Extension Path

> **Classification**: promoted_to_task
> **Status**: promoted
> **Promoted task**: `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SDK-01_agent_sdk_adapter_exploration.md`

## Observation

Agent SDKs and agentic development platforms introduce higher-level runtimes around agents, tools, handoffs, permissions, guardrails, sessions, MCP-backed tools, tracing, artifacts, and checkpoints.

This matters to JIKUO before the MCP wrapper is fully mature, because JIKUO's future users may run development workflows through agent orchestration rather than a single desktop-chat agent.

The initial exploration should include at least:

- OpenAI Agents SDK
- Claude Agent SDK
- Google Agent Development Kit
- Google Antigravity as an agentic development platform, not merely an SDK
- Vercel AI SDK as a JavaScript / TypeScript agentic application framework

## Product Interpretation

Agent SDKs and agentic platforms should not replace JIKUO's kernel. JIKUO still owns:

- policy trigger evaluation
- evidence requirements and matching
- guarded approval boundaries
- `.jikuo/runtime/` visibility
- task maps, insights, and durable local audit records

The likely useful role is optional orchestration or client environment support:

- a governance agent can invoke JIKUO status / card tools
- implementation and documentation agents can receive handoffs after governance evidence is visible
- SDK guardrails, permissions, hooks, and platform review artifacts can add development-time checks around tool calls
- SDK tracing, checkpoints, and platform artifacts can help debugging but should not become authoritative evidence by default

## Routing Decision

This insight is promoted to task-map work as `JIKUO-SDK-01` because it affects MCP extension points, instruction distribution, package dependency posture, and future desktop / IDE / SDK / JS application integration posture.

It is not a code implementation task yet. The immediate work is to record the architecture posture and make sure MCP / instruction-distribution planning leaves enough room for future optional SDK adapters and agentic platform environments.
