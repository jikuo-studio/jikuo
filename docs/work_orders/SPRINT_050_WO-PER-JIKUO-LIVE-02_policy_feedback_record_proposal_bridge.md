# SPRINT 050 WO-PER-JIKUO-LIVE-02: Policy Feedback Record Proposal Bridge

> **Kernel compatibility**: extends the desktop proposal flow after `JIKUO-LIVE-01` without adding gates, policy supersession, automatic writes, or frontend UI.
> **Current slice**: convert explicit user feedback on a triggered policy into a guarded task-session evidence append proposal.
> **User scenario**: A Codex / Claude desktop APP user sees a triggered policy in chat and wants to mark it as not applicable, deferred, or needing scope narrowing without switching to CLI.
> **Runtime chain**: policy evaluation card shows feedback options -> user gives explicit feedback -> desktop agent invokes `agent_flow.py propose --event policy_feedback_record` -> runner renders a guarded task-session evidence append proposal -> user may approve the exact write later.
> **Canonical source**: `SPRINT_050_WO-PER-JIKUO-LIVE-01_policy_evaluation_goes_live_in_desktop_chat.md`; `jikuo_policy_aware_agent_flow_contract.md`; task-session evidence model.
> **Bridge object**: task-session evidence append proposal with `evidence_kind: policy_feedback:<feedback_type>`.

## Product Meaning

This slice gives users a safe escape hatch when a policy trigger is noisy or contextually wrong.

The runner does not persist feedback by itself. It only turns explicit feedback into a reviewable guarded command proposal, keeping Codex / Claude desktop APP as the primary interaction surface.

## Scope

In scope:

- add `policy_feedback_record` as an `agent_flow.py propose` event
- support `not_applicable`, `defer`, and `needs_scope_narrowing`
- require explicit session, policy, feedback type, and summary or user phrase
- render a guarded task-session evidence append command proposal
- keep `agent_flow.py propose` no-write
- test refusal when feedback lacks a real summary or user phrase

Out of scope:

- automatic feedback persistence
- policy revision / supersession
- enforcement gates
- frontend UI
- judging whether the user's feedback is correct

## Implementation Status

Status:

- implemented and ready for user review.
- `agent_flow.py propose --event policy_feedback_record` now renders a guarded task-session evidence append proposal.
- feedback is represented as `policy_feedback:<feedback_type>` evidence.
- proposal mode still performs no durable write.

Observed verification:

```powershell
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/agent_flow.py propose --event policy_feedback_record --session-id task_policy_evidence_probe --policy-ref POLICY-real-test-data-and-chain --feedback-type not_applicable --summary "User marked this triggered policy as not applicable for this task." --project-root tools\jikuo\fixtures\policy_evidence_session_project
```

## Residual Risk

This records feedback as task-session evidence rather than a first-class policy revision. That is intentional for this slice. Later work should decide whether accepted feedback becomes a policy refinement, a one-time exemption, or a supersession candidate.
