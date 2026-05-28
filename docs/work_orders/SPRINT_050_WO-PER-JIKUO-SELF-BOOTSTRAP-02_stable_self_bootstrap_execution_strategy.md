# SPRINT_050_WO-PER-JIKUO-SELF-BOOTSTRAP-02: Stable Self-Bootstrap Execution Strategy

> **Status**: Active self-bootstrap MCP/core-debug boundary policy is approved; report-only evidence bridge for MCP vs explicit core-debug path is implemented in `agent_flow`.
> **Date**: 2026-05-17
> **Product meaning**: JIKUO development must not depend on the assistant remembering to behave well. The project needs a stable self-bootstrap workflow that makes JIKUO itself run at the start, during, and end of governed development slices.

## 1. Why This Task Exists

During JIKUO self-development, the assistant sometimes followed the spirit of
JIKUO policies but did not consistently invoke JIKUO's own runtime tools before
working. That creates a dogfood gap:

- policies can exist but not be evaluated
- runtime cards can be skipped
- task-session binding can be forgotten
- main-document maintenance can be delayed
- users must notice and correct the workflow manually

This task records the need to make self-bootstrap execution stable and visible.

## 2. Problem Statement

JIKUO currently has:

- policy store evaluation
- runtime cards
- task-session binding
- activation settings
- conversation routing
- MCP tools
- instruction files

But without a strict host adapter, Codex and similar clients may still skip
JIKUO unless the assistant chooses to call it. Self-development therefore needs
a documented and eventually tool-supported workflow that reduces reliance on
assistant memory.

## 2.1 Deferred Work-Unit Association Insight

`JIKUO-SELF-BOOTSTRAP-02` is the dogfood workflow consumer. It defines how JIKUO
development should behave before strict host adapters are ready.

`INSIGHT-2026-05-17-work-unit-task-association-boundary` records a heavier
future data-architecture correction: proposals and lifecycle cards eventually
need a reliable `work_order_id -> work_unit_id -> proposal/card` association.

That correction is deferred until a Codex / Claude hook or another strict host
adapter proves that JIKUO can run consistently enough to avoid false task-card
associations. Until then, JIKUO development slices must manually run completion
review before commit or final answer and must treat missing completion evidence
as an unresolved review item, not as a harmless card detail.

## 2.2 MCP User Boundary And Evidence Bridge

Accepted on 2026-05-28: when JIKUO is being governed, the assistant should be
treated as a user of the JIKUO MCP surface. Direct CLI / core calls are still
valid during JIKUO core development and debugging, but they must be explicitly
labelled as a core-debug path.

This is now represented by the active report-only policy
`POLICY-jikuo-self-bootstrap-mcp-user-boundary`. The policy intentionally uses
a broad trigger because it is a self-bootstrap guardrail, not a narrow product
feature rule.

The first evidence bridge is intentionally thin:

- MCP `jikuo.propose_task_start` calls produce
  `jikuo_mcp_or_core_debug_path_evidence` with path `mcp`;
- CLI `agent_flow.py propose --event task_start` produces the same evidence
  only when invoked with `--governance-path core_debug`;
- unlabelled CLI / core calls do not satisfy the policy.

This keeps the rule practical while preserving the product boundary: governed
work should flow through the MCP user surface, and core-debug work must say that
it is core-debug work instead of silently bypassing JIKUO's user-facing
protocol.

## 3. Strategy Questions For Discussion

Discuss before coding:

- What is the minimum required JIKUO call at the start of every development slice?
- Should JIKUO self-development require `.jikuo/activation_settings.yaml` to be reviewed and written?
- Should a local helper command run `conversation_turn -> configuration_review/task_start -> runtime card link` as one explicit bootstrap step?
- Should task-session binding be mandatory before code edits, or can it be deferred with visible evidence?
- How should completion review be triggered before commit?
- How should the assistant surface the latest runtime card link in every final answer?
- Which parts belong in policy, CLI helper, MCP tool, Codex plugin, or future strict adapter?

## 4. Candidate Acceptance Criteria

- A self-bootstrap slice-start checklist exists and is mounted.
- JIKUO's own activation settings are reviewed rather than implicit defaults.
- The first tool call for a governed JIKUO development slice is a JIKUO route/config/task-start call unless explicitly deferred.
- Governed JIKUO task-start work produces either MCP-path evidence or an
  explicitly labelled core-debug-path evidence item.
- Runtime card links are shown to the user after governed JIKUO calls.
- Completion review and main-doc maintenance are checked before commit.
- The workflow is practical in Codex without requiring a finished strict pre-turn adapter.

## 5. Non-Goals

- Do not claim Codex strict mounted behavior without `JIKUO-CODEX-PLUGIN-01` proof.
- Do not solve policy dead-zone detection here; that is `JIKUO-LIVE-20`.
- Do not require new UI / Studio work before the CLI / MCP self-bootstrap path is clear.
