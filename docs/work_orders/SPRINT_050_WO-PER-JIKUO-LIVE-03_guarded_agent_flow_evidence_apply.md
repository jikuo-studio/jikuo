# SPRINT 050 WO-PER-JIKUO-LIVE-03: Guarded Agent Flow Evidence Apply

> **Kernel compatibility**: extends `agent_flow.py` from proposal-only into one narrow guarded apply path without adding gates, policy supersession, frontend UI, or broad command execution.
> **Current slice**: apply an explicitly approved task-session evidence append through the desktop runner.
> **User scenario**: A Codex / Claude desktop APP user sees a proposal card for policy evidence or policy feedback and approves the exact write effect in chat.
> **Runtime chain**: proposal card shows guarded task-session evidence update -> user approves exact effect -> desktop agent invokes `agent_flow.py apply` -> runner calls the existing `task_session.py` guarded update atom -> result is returned to chat.
> **Canonical source**: `SPRINT_050_WO-PER-JIKUO-LIVE-02_policy_feedback_record_proposal_bridge.md`; `jikuo_productization_task_map.md`; task-session guarded update atom.
> **Bridge object**: `jikuo.agent_flow_apply_result.v0`.

## Product Meaning

This slice removes one remaining CLI-shaped seam from the desktop-primary workflow.

Before this slice, JIKUO could generate a safe command proposal, but the apply path was still external to `agent_flow.py`. After this slice, the desktop agent has a deterministic local entry point for an approved task-session evidence append.

## User Scenario / Operation Chain / Atomic Operation

User scenario:

- The user reviews a proposal card and approves persisting compact policy evidence or policy feedback.

Operation chain:

- proposal card -> explicit approval phrase -> `agent_flow.py apply` -> guarded task-session evidence update -> apply result returned in chat.

Atomic operation:

- `CAP-AGENT-FLOW-APPLY-TASK-EVIDENCE-01`: guarded task-session evidence apply through the desktop runner.

Development-map registration:

- registered in `docs/jikuo/governance/jikuo_productization_task_map.md` under Atomic Capability Registry.

## Scope

In scope:

- add `agent_flow.py apply`
- support only `task_session_evidence_update`
- require `--confirm-apply`
- require `--approval-phrase`
- wrap the existing `task_session.update_task_session(... patch_kind="evidence")`
- return a structured `jikuo.agent_flow_apply_result.v0`
- test refusal without approval
- test approved write against a temporary fixture copy

Out of scope:

- broad shell command execution
- policy-store writes through `agent_flow.py apply`
- completion / handoff / verification apply
- proposal persistence
- frontend UI
- gates or enforcement promotion

## Implementation Status

Status:

- implemented and ready for user review.
- `agent_flow.py apply --operation task_session_evidence_update` now applies a guarded task-session evidence append after explicit approval.
- tests verify refusal without approval and successful writes only against a temporary project copy.

Observed verification:

```powershell
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
```

## Residual Risk

This is intentionally a narrow apply path. The runner still cannot safely apply arbitrary command proposals or policy-store changes. Future apply operations should be added one at a time with their own approval boundary and regression tests.
