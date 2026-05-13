# SPRINT 050 WO-PER-JIKUO-LIVE-06: Guarded Policy Deprecation Writer MVP

> **Kernel compatibility**: adds one narrow durable policy-evolution writer after no-write evolution planning; does not implement revision, supersession, rollback, gates, frontend UI, Skill, MCP, or Plugin packaging.
> **Current slice**: allow an approved active policy to be deprecated through a guarded writer.
> **User scenario**: A user decides an active policy should stop triggering for future tasks.
> **Runtime chain**: evolution plan -> explicit approval -> `write-evolution` guarded deprecation -> proposal snapshot / decision record / manifest lifecycle refs -> status/evaluate read-back.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`; `jikuo_productization_task_map.md`.
> **Bridge object**: `jikuo.policy_evolution_plan.v0`.

## Product Meaning

This slice gives rules a safe exit path.

Before this slice, an approved policy could trigger and could produce an evolution plan, but it could not be durably retired by the tool. After this slice, an active policy can be deprecated through an explicit guarded write while preserving the policy file and audit history.

## User Scenario / Operation Chain / Atomic Operation

User scenario:

- The user confirms an active policy is no longer applicable and should stop triggering.

Operation chain:

- policy evolution plan -> approval phrase -> guarded deprecation writer -> proposal snapshot -> decision record -> manifest `deprecated_policy_refs` -> status/evaluate read-back.

Atomic operation:

- `CAP-POLICY-DEPRECATION-WRITE-01`: guarded policy deprecation writer.

Development-map registration:

- registered in `docs/jikuo/governance/jikuo_productization_task_map.md` under Atomic Capability Registry.

## Scope

In scope:

- add `policy_store.py write-evolution`
- support guarded `deprecate_policy`
- create policy evolution proposal snapshot
- create policy decision record with `decision: deprecate`
- update manifest by moving target policy from `active_policy_refs` to `deprecated_policy_refs`
- expose `deprecated_policy_refs` in policy-store status
- render a guarded deprecation command proposal from `agent_flow.py propose --event policy_evolution_plan`
- test refusal without approval and successful deprecation in a temporary fixture copy

Out of scope:

- revising a policy in place
- superseding one policy with another
- rollback
- deleting policy files
- moving policy files into another directory
- gates or enforcement promotion
- frontend UI
- Skill / MCP / Plugin packaging

## Implementation Status

Status:

- implemented and ready for user review.
- only `deprecate_policy` is supported by the guarded writer.
- at the LIVE-06 slice boundary, `refine_policy` and `supersede_policy` remain plan-only.
- later update: `JIKUO-LIVE-07` implements guarded `supersede_policy`.

Observed verification:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
```

## Residual Risk

Deprecation currently keeps the approved policy file in place and removes it from active refs. A later slice should decide whether deprecated policy files stay in `approved/` with manifest lifecycle refs only, or are moved into a dedicated `deprecated/` directory through another guarded writer.
