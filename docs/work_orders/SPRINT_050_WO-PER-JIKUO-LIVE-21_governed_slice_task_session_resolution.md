# SPRINT_050_WO-PER-JIKUO-LIVE-21: Governed Slice Task-Session Resolution

> **Status**: Implemented on 2026-05-17, pending review  
> **Product meaning**: governed work must not silently proceed without a task-session decision. The harness must visibly resolve the lifecycle carrier as bound, user-decision-required, or explicitly deferred.  
> **Scope rule**: repair local self-bootstrap / agent-flow behavior only; do not implement strict host hooks, dashboard, or broad policy-condition redesign in this slice.

## 1. Why This Slice Exists

`JIKUO-LIVE-15` introduced task-session binding at task start, but the active policy was still scoped to code-change / implementation-governance conditions.

That meant documentation governance, registry planning, analytics-contract planning, and other meaningful governed slices could show a task-session preview card while the policy itself did not trigger. In practice, an agent could continue work after saying "I will not create a task-session without approval" without recording whether the session was bound, approved for creation, or explicitly deferred.

The user identified the gap: creating a task-session remains a guarded write, but task-session handling itself must be a workflow obligation.

## 2. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Governed slice task-session resolution | user starts non-trivial governed work -> `agent_flow.py propose --event task_start` inspects task-session binding state -> runner projects one of `existing_session_bound`, `needs_user_decision`, or `explicitly_deferred` -> policy evaluator triggers `POLICY-jikuo-task-session-binding-at-slice-start` for any task_start -> policy evidence exposes the resolution state -> guarded apply may create a session only after explicit approval | `CAP-TASK-START-DRYRUN-01`; `CAP-CARD-TASKSESSION-01`; `CAP-TASK-SESSION-BINDING-EVIDENCE-01`; `CAP-POLICY-TRIGGER-EVALUATE-01`; `CAP-POLICY-EVIDENCE-CHECK-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | no silent task-session write; no claim of strict host enforcement; no broad condition-system redesign |

## 3. In Scope

- Broaden `POLICY-jikuo-task-session-binding-at-slice-start` so it triggers on every `task_start`, not only code-change slices.
- Keep durable task-session creation guarded behind `agent_flow.py apply --operation task_session_start --confirm-apply --approval-phrase ...`.
- Mark task-session start previews as `needs_user_decision` instead of treating the unresolved preview as plain `ok`.
- Add an explicit no-write deferral path for lightweight slices:
  `agent_flow.py propose --event task_start --task-session-decision defer --task-session-defer-reason "..."`
- Include task-session resolution details in task-start cards and `task_session_binding_evidence`.
- Add tests covering documentation-governance task starts and explicit deferral.

## 4. Out Of Scope

- strict mounted host adapter implementation
- Codex / Claude hook installation
- dashboard / Studio UI
- broad policy-condition language redesign
- automatic task-session creation
- task-session project-state index refresh

## 5. Acceptance Criteria

- A documentation or registry governance `task_start` triggers `POLICY-jikuo-task-session-binding-at-slice-start`.
- A normal task-start preview produces `task_session_binding_evidence` with `current_status=needs_user_decision`.
- Binding an existing session still produces `current_status=ok`.
- Explicit task-session deferral produces `current_status=explicitly_deferred` and does not write `.jikuo/task_sessions/`.
- The active policy accepts `ok`, `needs_user_decision`, and `explicitly_deferred` as visible resolution evidence statuses.
- Focused tests and full `unittest discover` pass.

## 6. Remaining Follow-Up

- Later policy-trigger redesign should review condition semantics separately; this slice only removes an over-narrow condition from one self-bootstrap policy.
- Strict Codex / Claude hooks must eventually prevent agents from continuing past a `needs_user_decision` state without surfacing the decision boundary.
