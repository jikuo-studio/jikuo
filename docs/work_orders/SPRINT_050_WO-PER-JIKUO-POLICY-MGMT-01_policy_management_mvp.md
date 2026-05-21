# SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01: Policy Management MVP

> **Status**: Two held candidates activated as `active_report_only`; official distribution design remains next.
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

This work order records the activation path and acceptance evidence; durable
policy writes are performed only by the guarded policy writer.

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

Held cleanup set, now activated:

- `POLICY-CANDIDATE-first-principles-critical-alignment`;
- `POLICY-CANDIDATE-data-model-drift-alarm`.

These two candidates were activated on 2026-05-22 through explicit no-write
policy plans and guarded policy-writer approval. They are also the first
concrete examples of `process_contract` policy needs:
they govern how the agent should reason, critique, and evaluate model boundaries
before accepting a proposed solution or adding structure.

Scope decision recorded on 2026-05-21: do not expand the policy-scope taxonomy
for these two candidates yet. They should use the existing stable scope classes:
the first-principles / critical-alignment candidate belongs to `discussion`, and
the data-model drift candidate belongs to `editing`. Their specific behavior
remains expressed by policy title, required action, required evidence, and
process / response contract text rather than by policy-name-like scope values.

Lifecycle correction recorded on 2026-05-22: `task_start` may remain an
observed execution marker, but it should not be the source of applicability for
these intent-driven policies. The intended routing basis is user intent plus
policy scope, runtime context, and response / process contract. The current
writer / evaluator path can express the first lightweight form of that design:
`conversation_turn` trigger plus scope-only `applies_to_work_profile`
(`lifecycle_events: []`, `policy_scopes: [...]`). These plans were approved by
the user and written through the guarded writer.

For these candidates, "the process-contract field took effect" must be
evidence-based, while trigger distribution should still be scope-aware.
`POLICY-MGMT-01A` should produce no-write plans that define:

- `first_principles_alignment_evidence` for the echo-chamber / first-principles
  candidate;
- `data_model_boundary_review_evidence` for the data-model drift candidate;
- the required final-response obligations that prove the response contract was
  honored.
- scope-only `applies_to_work_profile` filters narrow enough to avoid broad
  `task_start` noise before the policy is activated.

---

## 4. Implementation Sequence

Recommended smallest slices:

1. `POLICY-MGMT-01A`: produce no-write policy plans for the two held
   process-contract candidates using the existing policy-plan path with
   scope-only `applies_to_work_profile` filters. Completed.
2. `POLICY-MGMT-01B`: apply or merge each held candidate only after explicit
   user approval and guarded apply / evolution. Completed for the first two
   held candidates.
3. `POLICY-MGMT-01C`: define official distribution review: dogfood-only,
   official-starter, optional-template, or deferred, preserving package
   provenance and local-policy ownership.

### 4.1 Held-Candidate Plan Shapes

The current no-write review shapes use the implemented lightweight target:
`conversation_turn` as the user-turn trigger plus scope-only
`applies_to_work_profile`. They review title, action, evidence, write set, and
scope choice without depending on a separate `task_start` projection.

| Candidate | Proposed policy ref | Trigger distribution | Required evidence |
|---|---|---|---|
| First-principles / critical alignment | `POLICY-jikuo-first-principles-critical-alignment` | `conversation_turn` with scope-only `policy_scopes: ["discussion"]` | `first_principles_alignment_evidence` |
| Data-model drift alarm | `POLICY-jikuo-data-model-drift-alarm` | `conversation_turn` with scope-only `policy_scopes: ["editing"]` | `data_model_boundary_review_evidence` |

These no-write plans were review artifacts until the user approved the guarded
write.

Current no-write plan artifacts generated after the 2026-05-22 lifecycle /
scope separation decision:

| Candidate | Plan id | Runtime card |
|---|---|---|
| First-principles / critical alignment | `POLICYWRITEPLAN-1c88cb3e7c` | `.jikuo/runtime/history/20260521T163657Z_proposal_b39d277e5d.md` |
| Data-model drift alarm | `POLICYWRITEPLAN-8cfb13f8a2` | `.jikuo/runtime/history/20260521T163707Z_proposal_f0603a790d.md` |

The first plan proposes `conversation_turn` plus `policy_scopes:
["discussion"]`; the second proposes `conversation_turn` plus `policy_scopes:
["editing"]`. Both have `lifecycle_events: []` in
`applies_to_work_profile`, so they do not depend on `task_start` as a policy
applicability cause.

Activation completed on 2026-05-22 with approval phrase: "好的，请更新两个候选policy至激活状态".

| Candidate | Proposal snapshot | Decision record | Active policy |
|---|---|---|---|
| First-principles / critical alignment | `.jikuo/policies/proposals/POLICYPROPOSAL-44eae831b1.yaml` | `.jikuo/policies/decisions/POLICYDECISION-39cdfe5e92.yaml` | `.jikuo/policies/approved/POLICY-jikuo-first-principles-critical-alignment.yaml` |
| Data-model drift alarm | `.jikuo/policies/proposals/POLICYPROPOSAL-2df0d0aeb7.yaml` | `.jikuo/policies/decisions/POLICYDECISION-c773dfc651.yaml` | `.jikuo/policies/approved/POLICY-jikuo-data-model-drift-alarm.yaml` |

Evaluator smoke after activation:

- `conversation_turn` + `policy_scopes: ["discussion"]` triggers
  `POLICY-jikuo-first-principles-critical-alignment`;
- `conversation_turn` + `policy_scopes: ["editing"]` triggers
  `POLICY-jikuo-data-model-drift-alarm`;
- `conversation_turn` + both scopes triggers both policies.

---

## 5. Stop Boundaries

- Do not directly edit the activated policy YAML files to change semantics;
  future narrowing, merging, or deprecation must use guarded policy evolution.
- Do not add duplicate replacement policies for these candidates without first
  reviewing whether guarded evolution is the correct path.
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
  and records the candidate activation result.
- `docs/governance/jikuo_execution_mounts.md` names `LIFECYCLE-01` as the
  current priority and keeps this work order lightweight.
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md`
  preserves the candidate origin text and records that both candidates are now
  active report-only policies.
- `docs/registry/work_orders.yaml`, `docs/registry/capabilities.yaml`, and
  `docs/registry/mount_sets.yaml` expose this task to future sessions.
- `docs/governance/jikuo_productization_task_map.md` remains untouched except
  for explicitly approved projection maintenance.
