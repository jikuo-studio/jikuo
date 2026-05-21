# SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01: Policy Management MVP

> **Status**: Policy writer scope-field prerequisite implemented; held-candidate activation remains review-only.
> **Date**: 2026-05-18
> **JIKUO layer**: policy governance / policy distribution.
> **Business meaning**: JIKUO's first usable version needs the current user-authored candidate policies to enter active scope through the existing guarded flow, and it needs a clear official distribution boundary so useful policies can reach user projects without copying JIKUO dogfood policies or overwriting user-owned local policies.

---

## 1. Authority

This work order is the lightweight policy-management anchor. `LIFECYCLE-01` is
the current foundation priority because lifecycle facts are still not explicit
enough to support heavier policy insight or candidate-history modeling.

This work order complements:

- `docs/governance/jikuo_policy_governance_authority.md`;
- `docs/governance/jikuo_policy_store_configuration_flow.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-CATALOG-01_self_bootstrap_policy_promotion_review.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md` section `3.1 Held Policy-Governance Candidates`;
- `.jikuo/policies/manifest.yaml`.

It does not activate policy records by itself.

---

## 2. Lightweight MVP Boundary

The policy-management MVP is intentionally small for now:

| Loop | Required result | Why it matters |
|---|---|---|
| Held-candidate activation | The two user-authored held candidates move through existing no-write policy plan and guarded apply / merge / reject / defer outcomes. | The current candidates are explicit user requirements; they do not need a new heavy candidate registry before activation. |
| Official distribution design | Reviewed package templates and starter packs can be offered to user projects through opt-in preview and guarded activation. | Keeps JIKUO self-bootstrap policies separate from user-owned project policies. |

Runtime `policy_candidate` cards remain report-only evidence. They should not
drive automatic policy creation until lifecycle infrastructure can provide
better context and history.

---

## 3. Current Inputs

Completed prerequisites:

- `POLTRIG-01A`: work-profile no-write projection;
- `POLTRIG-01B`: lightweight `task_start` separated from guarded
  `task_session_start`;
- `POLTRIG-02`: `applies_to_work_profile` declaration bridge;
- `POLTRIG-03`: evaluator consumes `work_profile.lifecycle_event` and
  `work_profile.policy_scopes` while preserving exact conditions as additional
  filters;
- `POLICY-CATALOG-01`: starter policy source-boundary guard is implemented.
- `CAP-POLICY-STORE-WRITE-PROPOSE-01`: policy write plans can now include
  `applies_to_work_profile.lifecycle_events` and
  `applies_to_work_profile.policy_scopes` in no-write plans and guarded
  writer command previews.

Held cleanup set:

- `POLICY-CANDIDATE-first-principles-critical-alignment`;
- `POLICY-CANDIDATE-data-model-drift-alarm`.

These two candidates are intentionally not active. They should be resolved only
through explicit no-write policy plans and guarded apply / evolution decisions.
They are also the first concrete examples of `process_contract` policy needs:
they govern how the agent should reason, critique, and evaluate model boundaries
before accepting a proposed solution or adding structure.

For these candidates, "the process-contract field took effect" must be
evidence-based, while trigger distribution should still be scope-aware.
`POLICY-MGMT-01A` should produce no-write plans that define:

- `first_principles_alignment_evidence` for the echo-chamber / first-principles
  candidate;
- `data_model_boundary_review_evidence` for the data-model drift candidate;
- the required final-response obligations that prove the response contract was
  honored.
- `applies_to_work_profile` lifecycle/scope filters narrow enough to avoid
  broad `task_start` noise before the policy is activated.

---

## 4. Implementation Sequence

Recommended smallest slices:

1. `LIFECYCLE-01`: current priority before policy activation work. Make
   invoked-turn lifecycle nodes complete consistently when JIKUO is pulled up.
2. `POLICY-MGMT-01A`: produce no-write policy plans for the two held
   process-contract candidates using the existing policy-plan path with
   `applies_to_work_profile` lifecycle/scope filters. No active-policy write
   until approved.
3. `POLICY-MGMT-01B`: apply or merge each held candidate only after explicit
   user approval and guarded apply / evolution.
4. `POLICY-MGMT-01C`: define official distribution review: dogfood-only,
   official-starter, optional-template, or deferred, preserving package
   provenance and local-policy ownership.

### 4.1 Current Held-Candidate Plan Shapes

The current no-write review shapes are:

| Candidate | Proposed policy ref | Trigger distribution | Required evidence |
|---|---|---|---|
| First-principles / critical alignment | `POLICY-jikuo-first-principles-critical-alignment` | `task_start` with `policy_scopes: ["discussion"]` | `first_principles_alignment_evidence` |
| Data-model drift alarm | `POLICY-jikuo-data-model-drift-alarm` | `task_start` with `policy_scopes: ["discussion", "editing"]` | `data_model_boundary_review_evidence` |

These are review artifacts only. They do not activate the policies or write
`.jikuo/policies/approved` until the user approves an exact guarded write.

---

## 5. Stop Boundaries

- Do not write `.jikuo/policies/approved` from this planning slice.
- Do not mark a held candidate active without a no-write policy plan, explicit
  user approval, and guarded apply.
- Do not build a new heavy candidate-disposition registry before `LIFECYCLE-01`
  makes lifecycle facts and node completion more explicit.
- Do not copy `.jikuo/policies/approved` into official starter packs.
- Do not overwrite user-owned local policy files or active refs during official
  distribution.
- Do not change evaluator behavior in this work order without a separate
  POLTRIG review.
- Do not use `docs/governance/jikuo_productization_task_map.md` as the source of
  truth for this task.
- Do not add a duplicate DOCREG completion policy while the current
  main-document completion policy covers governed slice closeout.

---

## 6. Acceptance For This Planning Slice

- `docs/governance/jikuo_policy_governance_authority.md` names the MVP boundary
  and held-candidate activation rule.
- `docs/governance/jikuo_execution_mounts.md` names `LIFECYCLE-01` as the
  current priority and keeps this work order lightweight.
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md`
  keeps the two held candidates but points their cleanup to this work order.
- `docs/registry/work_orders.yaml`, `docs/registry/capabilities.yaml`, and
  `docs/registry/mount_sets.yaml` expose this task to future sessions.
- `docs/governance/jikuo_productization_task_map.md` remains untouched except
  for explicitly approved projection maintenance.
