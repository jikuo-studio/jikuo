# SPRINT 050 WO-PER-JIKUO-LIVE-05: Policy Evolution Plan Proposal

> **Kernel compatibility**: adds a no-write policy-evolution planning atom before any revision, supersession, deprecation, rollback, gate, frontend, Skill, MCP, or Plugin work.
> **Current slice**: make policy refinement / supersession review visible in desktop chat without changing durable policy state.
> **User scenario**: A user or agent notices an approved policy is too broad, not applicable, or likely needs replacement, and wants a safe next-step proposal before changing the policy store.
> **Runtime chain**: policy feedback / user observation -> active policy lookup -> no-write evolution plan -> desktop card review -> future guarded revision / supersession writer.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`; `jikuo_productization_task_map.md`.
> **Bridge object**: `jikuo.policy_evolution_plan.v0`.

## Product Meaning

This slice prevents policy governance from becoming one-way accumulation.

Before this slice, a policy could be written, triggered, and receive feedback, but there was no deterministic proposal object for "what should happen to this policy next". After this slice, the desktop agent can show a no-write refinement / deprecation / supersession plan before any durable policy change exists.

## User Scenario / Operation Chain / Atomic Operation

User scenario:

- The user sees a policy trigger that is too broad, not applicable, or obsolete.

Operation chain:

- user observation or feedback -> target active policy -> `plan-evolution` -> desktop proposal card -> user review -> future guarded writer.

Atomic operation:

- `CAP-POLICY-EVOLUTION-PLAN-PROPOSE-01`: policy evolution plan proposal.

Development-map registration:

- registered in `docs/jikuo/governance/jikuo_productization_task_map.md` under Atomic Capability Registry.

## Scope

In scope:

- add `jikuo.policy_evolution_plan.v0`
- add `policy_store.py plan-evolution`
- add `agent_flow.py propose --event policy_evolution_plan`
- support no-write operations: `refine_policy`, `deprecate_policy`, `supersede_policy`
- support feedback hints: `not_applicable`, `defer`, `needs_scope_narrowing`
- refuse missing or inactive target policy refs
- keep proposal mode write-free
- add regression tests for policy-store and desktop-agent projections

Out of scope:

- writing revised policies
- moving policies into `deprecated/` or `superseded/`
- manifest mutation
- rollback
- gates or enforcement promotion
- frontend UI
- Skill / MCP / Plugin packaging

## Implementation Status

Status:

- implemented and ready for user review.
- `policy_store.py plan-evolution` builds a no-write evolution plan for an active policy.
- `agent_flow.py propose --event policy_evolution_plan` renders the plan as a desktop proposal card.

Observed verification:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
```

## Residual Risk

This slice does not modify policies. The next downstream risk is designing a guarded writer for actual revision / supersession without making policy evolution too easy to apply accidentally.
