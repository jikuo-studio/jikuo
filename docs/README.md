# JIKUO Product Development Docs

> **Status**: Canonical JIKUO product documentation entry.
> **Boundary**: This directory contains JIKUO's own product-development assets. It does not absorb incubating-source project history or documents that merely mention JIKUO as context.

---

## 1. Purpose

`docs/` is the product documentation home for JIKUO.

JIKUO now uses this standalone repository as its active product-development home. Historical source-project context is not part of the active mount set.

---

## 2. Directory Layout

- `docs/work_orders/`: JIKUO product work orders and implementation slices.
- `docs/governance/`: JIKUO product maps, execution mounts, kernel/skeleton boundaries, policy contracts, and agent instruction contracts.
- `docs/schemas/`: JIKUO-owned schema and view-model contracts.
- `docs/insights/`: captured development insights and their registry.

---

## 3. What Stays Outside

The following remain outside this repository's active documentation mount unless a later work order explicitly promotes them:

- Source-project sprint histories.
- Domain runtime design docs from projects that use or incubated JIKUO.
- General engineering-governance documents owned by another project.

---

## 4. Current Entry Points

- `docs/README.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_productization_task_map.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-02_integration_neutrality_and_integrations_layout.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-03_mcp_pre_implementation_api_neutrality_review.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SDK-01_agent_sdk_adapter_exploration.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INTG-01_universal_instruction_file_distribution.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-14_completion_review_policy_only_surfacing.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-15_self_bootstrap_task_session_binding.md`

---

## 5. Migration Rule

When a future task creates JIKUO-owned docs:

- put work orders under `docs/work_orders/`
- put durable contracts under `docs/governance/`
- put schemas under `docs/schemas/`
- put development insights under `docs/insights/`
- update references in code, tests, sidecar state, fixtures, indexes, and checker rules
- keep source-project historical context outside active mounts unless the document itself is promoted as a JIKUO product asset

---

## 6. Slice Completion Main Document Check

Before closing each JIKUO development slice, check whether these main documents need updates:

- `.jikuo/project_context.yaml`
- `docs/README.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_productization_task_map.md`
- `docs/insights/insights_registry.yaml`
- `.jikuo/policies/manifest.yaml` when policy-store records changed

If no update is needed, report that the main document check was performed and why the scope stayed unchanged.
