# SPRINT_050_WO-PER-JIKUO-LIVE-15: Self-Bootstrap Task-Session Binding

> **Status**: Implemented and accepted on 2026-05-14, pre-MCP harness quality follow-up
> **Product meaning**: every governed development slice must bind, create, or explicitly defer a task-session before lifecycle evidence can be trusted.
> **Scope rule**: local harness and self-bootstrap policy only; do not implement MCP.

## 1. Why This Slice Exists

`JIKUO-LIVE-14` separated policy completion review from task-session lifecycle preview, which made policy evidence visible even when `.jikuo/task_sessions/` was missing.

That fix exposed a deeper self-bootstrap gap: JIKUO development had active policy and runtime visibility, but no durable task-session for the current slice.

Without a task-session binding, completion / evidence / handoff lifecycle records have no stable carrier. This breaks the audit chain that JIKUO is meant to enforce.

## 2. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Self-bootstrap task-session binding | user starts a governed JIKUO development slice -> runner checks task-session binding state -> runner surfaces either existing binding, guarded creation path, or explicit defer path -> policy evidence records that binding was handled -> approved apply creates one task-session through `agent_flow.py` -> completion review can target the created session | `CAP-TASK-SESSION-BINDING-EVIDENCE-01`; `CAP-TASK-START-DRYRUN-01`; `CAP-AGENT-FLOW-APPLY-TASK-SESSION-START-01`; `CAP-TASK-START-WRITE-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no silent durable write; no MCP implementation; guarded apply requires explicit user phrase |

## 3. In Scope

- Add an active self-bootstrap policy requiring task-session binding handling at task start.
- Make `agent_flow.py propose --event task_start` produce structured `task_session_binding_evidence` when it surfaces a guarded creation path.
- Add `agent_flow.py apply --operation task_session_start` as a narrow guarded wrapper over existing task-session start write.
- Keep `.jikuo/project_state.yaml latest_task_session_refs` refresh as a visible next action unless explicitly implemented in a later slice.
- Create a task-session for the current LIVE-15 self-bootstrap work through guarded apply.

## 4. Out Of Scope

- automatic silent task-session creation
- automatic project-state index refresh
- MCP implementation
- dashboard UI
- task-session rollback or deletion

## 5. Acceptance Criteria

- `task_start` proposals for governed JIKUO development can show task-session binding handling as policy evidence.
- Active policy evaluation can require `task_session_binding_evidence` without depending on final assistant wording.
- `agent_flow.py apply --operation task_session_start` refuses without confirmation and approval phrase.
- `agent_flow.py apply --operation task_session_start` creates exactly one `.jikuo/task_sessions/<session>.yaml` after explicit approval.
- Current repository has a durable task-session for this LIVE-15 slice.
- Runtime links point to the latest governed card.

## 6. Implemented Result

- Added active policy `POLICY-jikuo-task-session-binding-at-slice-start`.
- `agent_flow.py propose --event task_start` now emits `task_session_binding_evidence` when it surfaces a guarded task-session creation path.
- `agent_flow.py propose --event task_start --session-id ...` now treats an existing task-session as an explicit binding and emits the same evidence type.
- Task-start cards now propose `python -B -m jikuo.agent_flow apply --operation task_session_start ...` instead of only the lower-level task-session helper.
- `agent_flow.py apply --operation task_session_start` refuses without approval and writes one compact task-session after explicit approval.
- Current slice session: `.jikuo/task_sessions/task_20260514T130539Z_jikuo_live_15_self_bootstrap_task_session_bindin_aa0dd272.yaml`.
- Follow-up retained: `.jikuo/project_state.yaml latest_task_session_refs` refresh remains a separate guarded action unless promoted later.
- Follow-up hardening accepted in `JIKUO-LIVE-21`: the active task-session binding policy now applies to every governed `task_start`, and unresolved task-session previews surface as `needs_user_decision` rather than plain `ok`.
