# SPRINT 050 WO-PER-JIKUO-LIVE-08: Agent Flow Guarded Policy Evolution Apply MVP

> **Kernel compatibility**: adds one narrow desktop-agent apply path over existing guarded policy evolution writers; does not implement arbitrary command execution, in-place revision, rollback, gates, frontend UI, Skill, MCP, or Plugin packaging.
> **Current slice**: apply approved policy deprecation / supersession through `agent_flow.py apply`.
> **User scenario**: A desktop APP user approves a policy evolution proposal and expects the Agent to complete the guarded write without switching the user to a raw helper command.
> **Runtime chain**: evolution proposal -> explicit approval -> `agent_flow.py apply --operation policy_evolution_write` -> guarded `policy_store` writer -> proposal snapshot / decision record / manifest lifecycle refs -> status/evaluate read-back.
> **Canonical source**: `jikuo_execution_mounts.md`; `jikuo_productization_task_map.md`; `jikuo_policy_store_configuration_flow.md`.
> **Bridge object**: `jikuo.agent_flow_apply_result.v0`.

## Product Meaning

This slice keeps the desktop APP as the primary operating surface after policy evolution is approved.

Before this slice, `agent_flow.py propose` could show the user a guarded policy evolution command, but the actual write still lived behind the raw `policy_store.py write-evolution` helper. After this slice, the desktop Agent can call one deterministic apply entry point, while the tool still refuses without explicit confirmation and approval phrase.

## User Scenario / Operation Chain / Atomic Operation

User scenario:

- The user approves a policy deprecation or supersession proposal in Codex / Claude desktop chat.

Operation chain:

- policy evolution proposal -> approval phrase -> `agent_flow.py apply --operation policy_evolution_write` -> delegated guarded policy evolution writer -> write result card -> status/evaluate read-back.

Atomic operation:

- `CAP-AGENT-FLOW-APPLY-POLICY-EVOLUTION-01`: agent flow guarded policy evolution apply.

Development-map registration:

- registered in `docs/jikuo/governance/jikuo_productization_task_map.md` under Atomic Capability Registry.

## Scope

In scope:

- add `policy_evolution_write` to the `agent_flow.py apply` operation whitelist
- delegate to `policy_store.write_policy_evolution_from_plan`
- preserve explicit confirmation and approval phrase requirements
- expose target result schema, written paths, policy refs, and replacement policy refs in apply results
- test refusal without approval
- test successful supersession through `agent_flow.py apply` against a temporary fixture copy

Out of scope:

- arbitrary command execution
- automatic approval
- in-place policy revision
- rollback
- action execution
- gates or enforcement promotion
- frontend UI
- Skill / MCP / Plugin packaging

## Implementation Status

Status:

- implemented and ready for user review.
- `agent_flow.py apply` supports `task_session_evidence_update` and `policy_evolution_write`.
- policy evolution apply supports the guarded operations already supported by `policy_store.py write-evolution`.

Observed verification:

```powershell
python -B tools/jikuo/agent_flow_tests.py
```

## Residual Risk

The apply path still relies on explicit structured arguments. It does not yet bind a specific proposal id to the apply request or verify that every argument exactly matches a rendered proposal card. A later slice should add stronger proposal-to-apply binding before any blocking gate or broader automation is introduced.
