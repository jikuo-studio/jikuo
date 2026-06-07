# SPRINT 050 WO-PER-JIKUO-LIVE-07: Guarded Policy Supersession Writer MVP

> **Kernel compatibility**: adds one narrow durable policy-evolution writer after no-write evolution planning and guarded deprecation; does not implement in-place revision, rollback, gates, frontend UI, Skill, MCP, or Plugin packaging.
> **Current slice**: allow an approved active policy to be superseded by a newly approved replacement policy.
> **User scenario**: A user decides an active policy is useful in spirit but too broad, so it should be replaced by a narrower policy instead of simply deprecated.
> **Runtime chain**: evolution plan -> explicit approval -> `write-evolution` guarded supersession -> replacement approved policy / proposal snapshot / decision record / manifest lifecycle refs -> status/evaluate read-back.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`; `jikuo_productization_task_map.md`.
> **Bridge object**: `jikuo.policy_evolution_plan.v0`.

## Product Meaning

This slice gives rules a safe replacement path.

Before this slice, an approved policy could be deprecated, but correcting an over-broad policy meant either leaving the noisy policy active or retiring it without a successor. After this slice, the user can approve a replacement policy, keep the old policy available for audit, and let the replacement become the active trigger source.

## User Scenario / Operation Chain / Atomic Operation

User scenario:

- The user confirms an active policy should remain conceptually valid but needs narrower scope or clearer obligations.

Operation chain:

- policy evolution plan -> approval phrase -> guarded supersession writer -> replacement approved policy -> proposal snapshot -> decision record -> manifest `superseded_policy_refs` -> status/evaluate read-back.

Atomic operation:

- `CAP-POLICY-SUPERSESSION-WRITE-01`: guarded policy supersession writer.

Development-map registration:

- registered in `docs/jikuo/governance/jikuo_productization_task_map.md` under Atomic Capability Registry.

## Scope

In scope:

- extend `policy_store.py write-evolution` to support `supersede_policy`
- create one replacement approved policy file after explicit approval
- update manifest by moving target policy from `active_policy_refs` to `superseded_policy_refs`
- keep the old policy file available for audit
- create policy evolution proposal snapshot
- create policy decision record with `decision: supersede`
- render a guarded supersession command proposal from `agent_flow.py propose --event policy_evolution_plan`
- test proposal rendering and successful supersession in temporary fixture copies

Out of scope:

- revising a policy in place
- rollback
- deleting policy files
- moving policy files into another directory
- automatic policy narrowing inference
- gates or enforcement promotion
- frontend UI
- Skill / MCP / Plugin packaging

## Implementation Status

Status:

- implemented and ready for user review.
- `deprecate_policy` and `supersede_policy` are supported by the guarded evolution writer.
- `refine_policy`, in-place revision, and rollback remain plan-only.

Observed verification:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
```

## Residual Risk

Current implementation note: supersession now links the target policy to an
already existing replacement policy. Replacement policy content must be created,
imported, activated, or edited through a separate guarded workflow before the
supersede operation. Supersession does not infer a narrower replacement from
user prose, inspect semantic equivalence, generate replacement content, or edit
the replacement policy body. Side-by-side comparison remains later
productization work.
