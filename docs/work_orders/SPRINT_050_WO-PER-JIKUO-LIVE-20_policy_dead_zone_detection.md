# SPRINT_050_WO-PER-JIKUO-LIVE-20: Policy Dead-Zone Detection

> **Status**: LIVE-20A implemented; history-threshold scanning and broader surfacing remain planned.
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

JIKUO needs to distinguish these cases visibly. LIVE-20A implements the first
per-card classification directly inside the policy runtime status card. It does
not yet scan historical sequences or compute project-level thresholds.

## 3. Implemented Slice: LIVE-20A

Implemented in:

- `src/jikuo/agent_flow.py`
- `tests/agent_flow_tests.py`

When the policy store is active, at least one active policy exists, and
`triggered_policy_count == 0`, the `policy_runtime_status` payload may include:

```yaml
policy_dead_zone:
  schema: "jikuo.policy_dead_zone_classification.v0"
  status: "detected"
  classification: "<classification>"
  severity: "info|warning"
```

Current classifications:

| Classification | Meaning | Severity |
|---|---|---|
| `non_governance_event` | A tool such as `policy_write_plan`, setup, status, or template planning ran; this is not proof that task work was governed | `info` |
| `route_followup_required` | `conversation_turn` routed the user turn but the task-start / completion follow-up still needs to run | `warning` |
| `missing_or_mismatched_task_context` | A governed event ran, but `task_type` or `jikuo_layer` did not match active policy conditions | `warning` |
| `condition_mismatch` | A governed event ran, but other supplied condition context such as changed paths did not match | `warning` |
| `policy_coverage_gap` | A governed event ran and no active policy reported matching trigger / condition coverage | `warning` |
| `unknown_event_no_trigger` | The event is not yet classified by LIVE-20 | `warning` |

The card remains no-write. It changes visibility only: warning classifications
turn the policy runtime card into `review`, and next actions tell the user how to
rerun or classify the gap.

## 4. Remaining Scope For Discussion

The first slice is per-card detection. Still discuss the next layer before
coding:

- runtime visibility layer: detect repeated zero-trigger history and surface a warning in `jikuo show`
- MCP layer: include the same `policy_dead_zone` field in status / card responses wherever policy runtime status is returned
- router layer: when task context is missing, ask for `task_type` / `jikuo_layer` before policy evaluation
- starter-policy layer: add optional starter policies for analysis, archive, migration, and documentation cleanup
- dashboard / Studio layer: later show coverage gaps over time

## 5. Candidate Acceptance Criteria

Before the full LIVE-20 task is accepted, decide:

- what threshold counts as repeated zero-trigger behavior
- whether route/status calls should count toward the threshold
- how to classify no-trigger cards by event type
- where to show the warning: chat card, runtime file, CLI, MCP response, or all of them
- whether the first fix is detection only or also starter policy expansion

## 6. Non-Goals

- Do not treat every `triggered_policy_count=0` as failure.
- Do not create policies automatically.
- Do not modify user project policies without guarded approval.
- Do not claim strict mounted execution unless a host adapter actually runs JIKUO before each turn.

## 7. Initial Evidence

Observed in:

- `D:\personal_project\NarrativeSystem\.jikuo\runtime\history`

Representative finding:

- Six `policy_write_plan` calls between `20260516T135221Z` and `20260516T135616Z` produced zero triggered policies because active policies did not target policy-write planning events. LIVE-20A classifies this shape as `non_governance_event`.
- `20260516T161740Z_proposal_30257f9e32.md` was a mounted `conversation_turn` router call with `activation_settings_status: missing`; it found `task_start` follow-up was required, but the policy runtime card still showed 10 active policies and 0 triggered. LIVE-20A classifies this shape as `route_followup_required`.
- `20260516T161824Z_proposal_17342b25c9.md` was a `task_start` for "Analyze NarrativeSystem development blockers" with `task_type: analysis` and `jikuo_layer: design_review`; active NarrativeSystem policies expected `code_change`, `workflow_acceptance`, or `work_order_delivery`, so 10 policies remained untriggered. LIVE-20A classifies this shape as `missing_or_mismatched_task_context`.
- A manual read-only check with `task_start`, `task_type=code_change`, and `jikuo_layer=implementation_governance` did trigger `POLICY-pre-development-scenario-chain-atom-registration`, proving the engine can trigger when context matches.

## 8. Tests

Implemented acceptance tests:

- `tests.agent_flow_tests.AgentFlowProposalTests.test_policy_dead_zone_classifies_task_context_mismatch`
- `tests.agent_flow_tests.AgentFlowProposalTests.test_policy_dead_zone_classifies_policy_write_plan_as_non_governance`
