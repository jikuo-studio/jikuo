# SPRINT_050_WO-PER-JIKUO-LIVE-20: Policy Dead-Zone Detection

> **Status**: Planned; discuss implementation strategy before coding.
> **Date**: 2026-05-17
> **Product meaning**: JIKUO must not let users believe governance is working when active policies repeatedly evaluate to zero triggered policies. A project can be "MCP callable" and "policy store active" while still operating in a policy dead zone.

## 1. Why This Task Exists

During NarrativeSystem private-preview usage, `.jikuo/runtime/history` showed
multiple runtime cards where:

- policy store was active
- active policy count was greater than zero
- `triggered_policy_count` stayed at `0`
- `missing_evidence_count` also stayed at `0`

That means JIKUO was running, but no policy was governing the actual work being
performed. This is different from a healthy "no issues found" result.

## 2. Problem Statement

A zero-trigger card can mean several very different things:

| Case | Meaning |
|---|---|
| Healthy no-op | The event is intentionally outside policy scope |
| Wrong invocation | The client called a status / policy-write / route tool instead of task-start or completion-review |
| Missing context | `task_type`, `jikuo_layer`, or changed paths were omitted or wrong |
| Policy coverage gap | The project has no policies for analysis, migration, archive, documentation cleanup, or other real work types |
| Not initialized | Activation settings are missing or unreviewed, so users may think JIKUO is mounted when it is only callable |

JIKUO needs to distinguish these cases visibly.

## 3. Proposed Scope For Discussion

Do not implement yet. Discuss the right layer first:

- runtime visibility layer: detect repeated zero-trigger history and surface a warning in `jikuo show`
- MCP layer: include a `policy_dead_zone_warning` field in status / card responses
- router layer: when task context is missing, ask for `task_type` / `jikuo_layer` before policy evaluation
- starter-policy layer: add optional starter policies for analysis, archive, migration, and documentation cleanup
- dashboard / Studio layer: later show coverage gaps over time

## 4. Candidate Acceptance Criteria

Before this task is accepted, decide:

- what threshold counts as repeated zero-trigger behavior
- whether route/status calls should count toward the threshold
- how to classify no-trigger cards by event type
- where to show the warning: chat card, runtime file, CLI, MCP response, or all of them
- whether the first fix is detection only or also starter policy expansion

## 5. Non-Goals

- Do not treat every `triggered_policy_count=0` as failure.
- Do not create policies automatically.
- Do not modify user project policies without guarded approval.
- Do not claim strict mounted execution unless a host adapter actually runs JIKUO before each turn.

## 6. Initial Evidence

Observed in:

- `D:\personal_project\NarrativeSystem\.jikuo\runtime\history`

Representative finding:

- `policy_write_plan` calls produced zero triggered policies because active policies did not target that event.
- `task_start` with insufficient or mismatched `task_type` / `jikuo_layer` also produced zero triggered policies.
- A manual read-only check with `task_start`, `task_type=code_change`, and `jikuo_layer=implementation_governance` did trigger `POLICY-pre-development-scenario-chain-atom-registration`, proving the engine can trigger when context matches.

