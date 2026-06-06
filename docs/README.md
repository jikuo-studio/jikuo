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
- `docs/user/`: user-facing guides for first-run setup, document management,
  policy management, trace inspection, and release limitations.
- `docs/governance/`: JIKUO product maps, execution mounts, kernel/skeleton boundaries, policy contracts, and agent instruction contracts.
- `docs/integrations/`: JIKUO integration examples, client configuration notes, and smoke-test companion artifacts.
- `docs/schemas/`: JIKUO-owned schema and view-model contracts.
- `docs/registry/`: draft machine-readable registries for work orders, capabilities, scenario chains, and mount sets.
- `docs/insights/`: captured development insights and their registry.
- `docs/migration/`: repository migration handoffs and source-project archive transition records.

---

## 3. What Stays Outside

The following remain outside this repository's active documentation mount unless a later work order explicitly promotes them:

- Source-project sprint histories.
- Domain runtime design docs from projects that use or incubated JIKUO.
- General engineering-governance documents owned by another project.

---

## 4. Current Entry Points

- `README.md`
- `docs/user/document-management.md`
- `docs/user/trace-and-evidence.md`
- `docs/README.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_productization_task_map.md` as a legacy
  human-readable projection only; structured task and capability authority
  lives in `docs/registry/`
- `docs/governance/jikuo_policy_governance_authority.md`
- `docs/governance/jikuo_scenario_chain_and_atom_registration_guide.md`
- `docs/governance/jikuo_document_evidence_chain_design.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-02_integration_neutrality_and_integrations_layout.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-03_mcp_pre_implementation_api_neutrality_review.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SDK-01_agent_sdk_adapter_exploration.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INTG-01_universal_instruction_file_distribution.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ROUTER-01_trigger_mode_and_conversation_turn_router.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INTG-02_client_onboarding_settings_and_trigger_mode.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-INTG-03_strict_mounted_harness_adapter_contract.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-14_completion_review_policy_only_surfacing.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-15_self_bootstrap_task_session_binding.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-16_policy_runtime_card_priority.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-17_task_session_index_stale_hint.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-18_previous_latest_todo_snapshot_posture.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-19_starter_policy_provenance_backfill.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-21_governed_slice_task_session_resolution.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SEC-02_mcp_response_privacy_classification_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CODEX-PLUGIN-01_codex_plugin_pre_turn_harness_review.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CLAUDE-HOOK-01_claude_hook_strict_adapter_review.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-20_policy_dead_zone_detection.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md`
- `docs/registry/registry_index.yaml`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DATA-01_structured_execution_event_ledger_and_analytics_contract.md`
- `docs/schemas/execution_events_v0_draft.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SELF-BOOTSTRAP-02_stable_self_bootstrap_execution_strategy.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SELF-BOOTSTRAP-03_harness_workspace_boundary_spike.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MVP-01_work_receipt_and_configuration_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-01_global_console_and_configuration_shell.md`
- `docs/insights/INSIGHT-2026-05-17-self-bootstrap-harness-workspace-boundary.md`
- `docs/integrations/mcp_client_configuration_examples.md`
- `docs/integrations/mcp_client_proof_playbook.md`
- `docs/migration/NARRATIVESYSTEM_RESOURCE_POOL_HANDOFF.md`

Current private GitHub preview remote for realistic clone/download proof:
`https://github.com/jikuo-studio/jikuo.git`. Keep it private until the
license, privacy sweep, and public-review IP gate are accepted.

---

## 5. Migration Rule

When a future task creates JIKUO-owned docs:

- put work orders under `docs/work_orders/`
- put user-facing first-run and product-operation guides under `docs/user/`
- put durable contracts under `docs/governance/`
- put integration examples and client-specific setup notes under `docs/integrations/`
- put schemas under `docs/schemas/`
- put machine-readable documentation registries under `docs/registry/`
- put development insights under `docs/insights/`
- put source-project archive / migration handoffs under `docs/migration/`
- update references in code, tests, sidecar state, fixtures, indexes, and checker rules
- keep source-project historical context outside active mounts unless the document itself is promoted as a JIKUO product asset

---

## 6. Slice Completion Main Document Check

Before closing each JIKUO development slice, check whether these main documents need updates:

- `.jikuo/project_context.yaml`
- `docs/registry/registry_index.yaml`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md` while DOCREG sequencing remains transitional
- `README.md`
- `docs/README.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_policy_governance_authority.md`
- `docs/governance/jikuo_scenario_chain_and_atom_registration_guide.md`
- `docs/governance/jikuo_productization_task_map.md`
- `docs/insights/insights_registry.yaml`
- `.jikuo/policies/manifest.yaml` when policy-store records changed

If no update is needed, report that the main document check was performed and why the scope stayed unchanged.
