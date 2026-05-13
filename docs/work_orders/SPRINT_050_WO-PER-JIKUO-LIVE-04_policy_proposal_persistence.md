# SPRINT 050 WO-PER-JIKUO-LIVE-04: Policy Proposal Persistence

> **Kernel compatibility**: completes the existing guarded policy write audit chain without adding policy revision, supersession, rollback, gates, frontend UI, or broader apply operations.
> **Current slice**: persist the reviewed policy write proposal snapshot when a guarded policy write is approved.
> **User scenario**: A user approves a policy-store write and later wants to audit what exact proposal was approved.
> **Runtime chain**: `plan-write` proposal -> user approval -> `write-policy` guarded writer -> proposal snapshot / approved policy / decision record / manifest refs are persisted.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`; `jikuo_productization_task_map.md`; existing `jikuo.policy_decision.v0` records.
> **Bridge object**: persisted `jikuo.policy_write_plan.v0` proposal snapshot referenced by `jikuo.policy_decision.v0.proposal_ref`.

## Product Meaning

This slice closes an audit gap in policy-store writes.

Before this slice, a decision record pointed to a `proposal_ref`, but the proposal snapshot itself was not written. After this slice, the approval decision, the proposal that was approved, the resulting policy, and the manifest reference all exist together.

## User Scenario / Operation Chain / Atomic Operation

User scenario:

- The user approves a new project policy and later reviews what was approved.

Operation chain:

- policy write plan -> approval phrase -> guarded policy write -> proposal snapshot -> approved policy -> decision record -> manifest proposal refs and active refs.

Atomic operation:

- `CAP-POLICY-PROPOSAL-PERSIST-01`: guarded policy proposal snapshot persistence.

Development-map registration:

- registered in `docs/jikuo/governance/jikuo_productization_task_map.md` under Atomic Capability Registry.

## Scope

In scope:

- add `PROPOSALS_DIR_NAME`
- include proposal snapshot in policy write plans
- create `.jikuo/policies/proposals/POLICYPROPOSAL-*.yaml` during guarded `write-policy`
- add proposal refs to manifest records
- include `proposal_ref` and `proposal_snapshot_written` in write results
- update regression tests for initial policy-store creation

Out of scope:

- editing persisted proposals
- proposal approval workflows beyond the existing guarded writer
- policy revision / supersession
- rollback
- frontend UI
- gates or enforcement promotion

## Implementation Status

Status:

- implemented and ready for user review.
- guarded `write-policy` now persists the proposal snapshot before writing the approved policy and decision record.
- decision records now point to an existing proposal file for new writes.

Observed verification:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
```

Observed real-chain acceptance:

- a temporary project without initialized project state refused the guarded policy write.
- after initializing the temporary project state, guarded `write-policy` wrote proposal snapshot, approved policy, decision record, and manifest.
- `policy_store.py status` read back an active policy store with `proposal_refs`.
- `policy_store.py evaluate` triggered the newly written policy from the temporary project.

## Residual Risk

Existing policy decision records created before this slice may still reference proposal paths that were not persisted at the time. This slice guarantees proposal persistence for future guarded policy writes; it does not retroactively reconstruct earlier proposals.
