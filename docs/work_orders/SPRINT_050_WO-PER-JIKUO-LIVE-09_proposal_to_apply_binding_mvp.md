# SPRINT_050_WO-PER-JIKUO-LIVE-09: Proposal-To-Apply Binding MVP

> **Status**: Implemented, ready for user review
> **Product meaning**: prevents a desktop Agent from applying a policy evolution write that does not match the proposal ref the user reviewed.

## 1. Scope

This slice tightens the existing `agent_flow.py apply --operation policy_evolution_write` path.

It does:

- require `--proposal-ref` for policy evolution apply
- rebuild the deterministic policy evolution plan from the apply arguments
- compare the supplied proposal ref with the expected plan proposal ref
- refuse durable writes when the proposal ref is missing or mismatched
- expose the binding result in `jikuo.agent_flow_apply_result.v0`

It does not:

- reuse an already persisted proposal snapshot as the write source
- implement in-place policy revision
- implement rollback
- add MCP / Skill / Plugin packaging
- promote any report-only rule into a blocking gate

## 2. Chain

User scenario:

- A Codex / Claude desktop APP user reviews a policy evolution proposal card, then approves applying that exact proposal.

Operation chain:

1. `agent_flow.py propose --event policy_evolution_plan ...` or `policy_store.py plan-evolution ...` produces a proposal ref.
2. The user approves applying that proposal.
3. The Agent calls `agent_flow.py apply --operation policy_evolution_write --proposal-ref "<approved proposal ref>" ...`.
4. `agent_flow.py` rebuilds the deterministic plan from the apply arguments.
5. If the supplied proposal ref is missing or mismatched, apply refuses before writing.
6. If the proposal ref matches and approval is present, the existing guarded policy evolution writer runs.
7. The result card reports `proposal_binding`, written paths, and verification status.

## 3. Bridge Object

`jikuo.agent_flow_apply_result.v0` now includes:

```yaml
proposal_binding:
  required: true
  status: "ok | missing | mismatch"
  provided_ref: "<approved proposal ref>"
  expected_ref: "<deterministic proposal ref>"
  match_basis: "deterministic_policy_evolution_plan_ref"
```

## 4. Tests

Unit / integration:

- `python -B tools/jikuo/agent_flow_tests.py`
- `python -B tools/jikuo/policy_store_tests.py`

Regression cases:

- missing proposal ref refuses before write
- mismatched proposal ref refuses before write
- matching proposal ref allows approved supersession and read-back

Smoke:

- generate a plan in a temporary fixture
- apply with matching `--proposal-ref`
- verify `status` / `evaluate` read back only the replacement policy

## 5. Residual Risk

This MVP binds apply to the deterministic proposal ref generated from the current arguments. It does not yet treat an already persisted proposal snapshot as the canonical write source. If future UX requires "apply exactly this persisted snapshot even if current arguments differ", implement that as a separate guarded writer slice.
