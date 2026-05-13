# SPRINT_050_WO-PER-JIKUO-CORE-20: Project Context Binding And Policy Template Portability

> **Status**: Draft contract, ready for user review
> **Product meaning**: make JIKUO policy templates portable across projects by separating reusable rule intent from project-local document and directory bindings.
> **Scope rule**: define the contract only; do not create `.jikuo/project_context.yaml`, write resolver code, import templates, migrate packages, or implement MCP in this slice.

## 1. Why This Slice Exists

`JIKUO-MCP-01` must not expose NarrativeSystem-specific paths as a public tool interface.

Reusable policies need three layers:

- policy template: project-independent rule intent
- project context binding: project-specific role-to-path mapping
- resolved policy: runtime view after roles are safely resolved

`JIKUO-PKG-00` separated tool-owned assets from user-project-local state. `CORE-20` defines the project-local binding contract that makes reusable policy templates possible.

## 2. In Scope

This slice defines:

- `.jikuo/project_context.yaml` shape
- `jikuo.policy_template.v0`
- `jikuo.resolved_policy.v0`
- reference categories: `role://`, `pkg://`, `project://`, and external URL
- path safety requirements
- template import / binding flow at contract level
- relationship to policy store and `CONTRACT_REFS`

## 3. Out Of Scope

This slice must not:

- write `.jikuo/project_context.yaml`
- implement resolver code
- implement path checks in `policy_store.py`
- fix `CONTRACT_REFS`
- create policy templates in the store
- add template marketplace behavior
- implement signature / trust chain
- add telemetry
- implement frontend wizard
- move files into a package
- implement MCP server / adapter

## 4. Deliverables

- `docs/jikuo/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- this work order
- task-map updates for `JIKUO-CORE-20`
- execution-mount updates so future SEC / CORE-20B / MCP tasks mount the contract

## 5. Acceptance Cases

Review acceptance:

- Can a policy template refer to `role://document/latest_backlog` without naming a NarrativeSystem path?
- Can a project bind that role to its own relative path in future `.jikuo/project_context.yaml`?
- Does the contract reject path escape outside project root?
- Does it distinguish JIKUO-owned `pkg://` refs from project-owned `role://` / `project://` refs?
- Does it make clear that resolved policy is a runtime projection, not a new active policy source?
- Does it leave `SEC-01`, `CORE-20B`, package extraction, and MCP implementation out of this slice?

## 6. Testing Requirements

Unit tests:

- not required for this contract-only slice.
- future resolver implementation must test role lookup, missing binding, unsafe binding, and project-root escape refusal.

Integration tests:

- not required for this contract-only slice.
- future implementation must test reusable template resolution against temporary projects with different document layouts.

Smoke tests:

- run existing `agent_flow_tests.py` and `policy_store_tests.py` after updating docs.
- run no-write `agent_flow.py propose` with task-scope evidence for this work order.

Human review:

- confirm this contract is understandable to a future non-NarrativeSystem user.
- confirm it does not turn into a broad package extraction, security system, marketplace, UI, or MCP implementation.

## 7. Next Task

If accepted, continue to:

- `JIKUO-SEC-01`: trust, privacy, provenance, namespace, principal, telemetry, and timestamp baseline.

Do not jump directly to MCP until `PKG-01` minimal package extraction and `CORE-20B` resource-reference hygiene are resolved or explicitly deferred.
