# INSIGHT-2026-06-03: Completed Chain And Atom History Backfill

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: scenario-chain and atom registration guidance follow-up
- Not promoted to a work order in this slice

## Observation

JIKUO now has an active guide for registering complete user operation chains and
their implementing atoms:

- readable user chain in the corresponding work order, flow, or design document;
- structured chain entry in `docs/registry/scenario_chains.yaml`;
- atom definitions in `docs/registry/capabilities.yaml`;
- mount coverage in project context and mount sets.

That guide improves future feature work, but it does not automatically repair
already completed work. Many existing JIKUO slices were developed before the
new registration guide existed. Their user-facing chains and internal atoms are
spread across accepted work orders, implementation notes, registry shards,
runtime cards, and legacy projections.

The result is a historical migration gap:

```text
completed feature history:
  work orders / flow docs / runtime evidence / capability rows

new expected structure:
  corresponding document -> scenario_chains entry -> capability refs -> mount coverage
```

Without a dedicated backfill, future AI sessions may correctly follow the new
process for new work while still missing the historical user chains and atom
composition that already exist.

## Product Meaning

This is not just documentation cleanup. Backfilling the history would let JIKUO
answer product and governance questions such as:

- which user workflows already exist;
- which atoms implement each workflow;
- which completed features lack a complete user-chain record;
- which registry entries are atom-only and need scenario-chain context;
- which work orders are the corresponding documents for historical features.

It would also make Studio and future registry views more useful because they
could show feature chains instead of only atom lists.

## Desired Future Behavior

A future migration slice should:

- inventory completed user-facing JIKUO features;
- identify the corresponding document for each feature without relying on the
  legacy task map as registry authority;
- backfill structured entries in `docs/registry/scenario_chains.yaml`;
- link those entries to existing `CAP-*` rows in
  `docs/registry/capabilities.yaml`;
- add or update capability rows only when a stable atom is missing;
- verify each corresponding document and registry shard is covered by the active
  mount model;
- record explicit "checked unchanged" evidence for historical features whose
  current work order already contains enough user-chain detail.

## Candidate Inputs

Start with:

- `docs/governance/jikuo_scenario_chain_and_atom_registration_guide.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-UX-00_user_scenarios_and_atomic_action_map.md`;
- `docs/registry/scenario_chains.yaml`;
- `docs/registry/capabilities.yaml`;
- `docs/registry/work_orders.yaml`;
- recent Studio work orders and capability rows.

## Boundary

Do not perform this migration opportunistically inside unrelated feature work.
Do not use `docs/governance/jikuo_productization_task_map.md` as new registry
authority. Treat it only as a legacy projection that can help locate historical
clues when cross-checked against accepted work orders and registry shards.

This insight records the backfill need only.
