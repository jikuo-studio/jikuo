# JIKUO Scenario Chain And Atom Registration Guide

> **Status**: Active governance guidance.
> **Created**: 2026-06-02
> **Purpose**: define how future JIKUO work records complete user operation chains and the atomic capabilities that implement them.
> **Primary consumers**: Codex / Claude desktop agents, future Studio registry views, policy completion evidence, and document-registry tooling.

---

## 1. Purpose

JIKUO features must not be registered only as implementation atoms.

When a feature changes how a user actually uses JIKUO, the work must record:

- the user-facing chain;
- the internal operation chain;
- the atom or capability IDs used by each step;
- the write and approval boundary for each step;
- the corresponding document that owns the human-readable chain;
- the mount coverage that lets future AI sessions find the right documents.

This guide makes that registration repeatable without hard-coding a single
document path into policy text.

---

## 2. Authority Split

Use three coordinated sources instead of one oversized document.

1. The corresponding work order, flow, or design document owns the readable
   narrative: why the feature exists, who uses it, what changed, and the real
   user action chain.
2. `docs/registry/scenario_chains.yaml` owns the structured chain entry:
   scenario ID, user outcome, steps, atom refs, and approval boundaries.
3. `docs/registry/capabilities.yaml` owns the atom definitions: capability ID,
   implementation surface, write effect, approval boundary, and verification
   status.

The legacy productization task map is only an L3 projection. Do not add new
task sequencing, open-item facts, capability metadata, or registry authority
there by default.

---

## 3. When Registration Is Required

Perform scenario-chain and atom registration when work introduces or changes:

- a user-facing workflow, screen, command, MCP tool, Studio panel, or approval
  path;
- a new stable internal atom that future chains can reuse;
- a changed approval or write boundary;
- a changed mapping between a user-visible action and internal JIKUO behavior;
- a policy or governance rule that asks for feature atom registration evidence.

If a slice only fixes a narrow implementation defect and does not affect the
user operation chain or reusable atoms, record that the registration surfaces
were checked and no change was needed.

---

## 4. Registration Procedure

### 4.1 Resolve The Corresponding Document

Do not choose the document from memory or from a hard-coded policy path.

Resolve the corresponding document from:

- `.jikuo/project_context.yaml` document roles;
- `docs/registry/work_orders.yaml` task entries and required mount sets;
- `docs/registry/registry_index.yaml` shard authority;
- the active work order or accepted flow document;
- `docs/governance/jikuo_execution_mounts.md` mount guidance.

The corresponding document should be the place where a future reader would
expect to understand the feature's actual user path. It may be a work order,
flow document, design contract, or future product-surface document.

### 4.2 Restore The User Operation Chain

In the corresponding document, record the feature as a user-facing chain. A good
chain answers:

- what the user is trying to accomplish;
- where the user starts;
- what visible step happens next;
- what JIKUO does internally;
- which atom IDs the step uses;
- whether the step is read-only, no-write, guarded write, or automatic write;
- what evidence or runtime trace should be visible afterward.

### 4.3 Register The Structured Scenario Chain

Add or update a `docs/registry/scenario_chains.yaml` entry. The current draft
registry may keep seed entries simple, but complete entries should move toward
this shape:

```yaml
- id: "SCENARIO-EXAMPLE"
  title: "Readable scenario title"
  status: "implemented"
  user_outcome: "What the user can now accomplish."
  corresponding_document_refs:
    - "resolved/document/path.md"
  mount_coverage:
    status: "verified"
    refs:
      - "MOUNT-EXAMPLE"
  steps:
    - step_id: "EXAMPLE-01"
      user_action: "What the user does."
      visible_result: "What the user sees."
      operation_chain: "What JIKUO does internally."
      atom_refs:
        - "<registered CAP id>"
      approval_boundary: "read_only"
      evidence_outputs:
        - "runtime_card_or_registry_ref"
  capability_refs:
    - "<registered CAP id>"
```

Keep `capability_refs` as a forward edge to atom definitions. Do not duplicate
the atom definition inside the chain entry.

### 4.4 Register Atom Definitions

Add or update `docs/registry/capabilities.yaml` for each stable atom.

An atom should be small enough to be reused by multiple chains, but large enough
to have a meaningful entry point and verification boundary. Avoid splitting a
single UI affordance into many pseudo-atoms unless those parts can be reused
independently.

Each atom entry should declare at least:

- `id`;
- `title`;
- `status`;
- `owner_layer`;
- `entry_point`;
- `write_effect`;
- `approval`;
- `metadata_status`.

### 4.5 Verify Mount Coverage

Before completion, verify that the corresponding document and structured
registry shards are discoverable through the active mount model.

At minimum, check:

- `.jikuo/project_context.yaml` for document roles and main-document completion
  scope;
- `docs/registry/mount_sets.yaml` for reusable mount bundles;
- `docs/governance/jikuo_execution_mounts.md` for required mount guidance.

If the corresponding document is not in scope, update the document role or mount
set through the appropriate guarded Document Rules / registry path.

### 4.6 Record Evidence

Feature atom registration evidence should name:

- the corresponding document used;
- the scenario chain ID;
- the capability IDs added or updated;
- the mount set or document role that covers those documents;
- any checked surface that did not need a change.

---

## 5. Anti-Patterns

Do not:

- register only `CAP-*` IDs and call the user chain complete;
- copy atom definitions into scenario-chain rows;
- use `docs/governance/jikuo_productization_task_map.md` as new registry
  authority;
- hard-code a specific work-order path into a reusable policy;
- let a frontend panel become a second governance kernel;
- skip mount coverage and rely on future AI memory.

---

## 6. Minimal Completion Checklist

Before closing a feature slice that affects user operation:

- corresponding document selected and in mount scope;
- readable user operation chain recorded or confirmed unchanged;
- `docs/registry/scenario_chains.yaml` updated or explicitly checked unchanged;
- `docs/registry/capabilities.yaml` updated or explicitly checked unchanged;
- mount coverage verified through project context or mount sets;
- completion evidence reports the document refs, scenario ID, atom IDs, and
  verification status.
