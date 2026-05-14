# SPRINT_050_WO-PER-JIKUO-LIVE-14: Completion Review Policy-Only Surfacing

> **Status**: Draft, pre-MCP harness quality follow-up
> **Product meaning**: make slice-completion policy checks visible even when task-session lifecycle state is unavailable.
> **Scope rule**: fix completion-review surfacing in the local harness; do not implement MCP.

## 1. Why This Slice Exists

During INTG-01 completion, `POLICY-jikuo-main-doc-mount-maintenance` correctly triggered on `completion_review` and its evidence matched.

However, `agent_flow.py propose --event completion_review` still returned top-level `refused` because the task-session lifecycle preview required an existing task-session root / session file.

That mixes two different concerns:

- policy-only completion review: should show triggered policies, evidence status, and runtime links
- task-session lifecycle update preview: may be unavailable when no task session exists

If these remain coupled, a successful policy audit can look like a failed harness run.

## 2. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Completion-review policy-only surfacing | user challenges whether completion policies ran -> agent invokes `completion_review` -> main-document policy triggers -> evidence is matched -> runtime card shows policy success even if task-session lifecycle preview is unavailable -> task-session issue remains visible as non-blocking context | `CAP-COMPLETION-REVIEW-POLICY-ONLY-SURFACE-01`; `CAP-MAIN-DOC-MOUNT-MAINTENANCE-01`; `CAP-POLICY-RUNTIME-STATUS-CARD-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01` | local harness only; no automatic task-session creation; no MCP implementation |

## 3. In Scope

- Allow `completion_review` to produce a successful policy runtime card when policy evidence is satisfied, even if task-session lifecycle preview is unavailable.
- Keep task-session lifecycle refusal visible as a separate card or warning.
- Preserve `.jikuo/runtime/last_card.md`, `state_summary.json`, and history output.
- Add regression coverage for completion-review main-document evidence without requiring `.jikuo/task_sessions/`.

## 4. Out Of Scope

- creating task sessions automatically
- changing approval requirements for guarded lifecycle writes
- MCP implementation
- dashboard UI
- plugin or client-hook behavior

## 5. Acceptance Criteria

- `agent_flow.py propose --event completion_review ... --produced-evidence-type main_document_mount_maintenance_evidence ...` reports `POLICY-jikuo-main-doc-mount-maintenance` as triggered.
- Missing evidence count is zero when main-document evidence is supplied.
- The top-level proposal status is not `refused` solely because task-session lifecycle preview is unavailable.
- The task-session lifecycle unavailability remains visible as separate non-blocking context.
- Runtime links point to the completion-review card.
