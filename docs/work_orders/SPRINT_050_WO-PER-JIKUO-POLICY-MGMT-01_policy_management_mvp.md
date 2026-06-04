# SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01: Policy Management MVP

> **Status**: Two held candidates activated as `active_report_only`; Policy Management MVP closeout design, no-write distribution review with GUI/MCP natural-language source resolution, guarded package-template publication CLI plus agent-flow/MCP bridge, guarded starter-pack manifest publication CLI plus agent-flow/MCP bridge, no-write policy-management status read model, Studio package-template publication/activation guarded bridges, real-policy distribution smoke, and first real optional package-template publication for `POLICY-jikuo-data-model-drift-alarm` implemented. Follow-up semantic-precondition hardening fixed the missing-intent gap found by that smoke.
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
| Policy-management read model | A no-write status surface returns active policies, package templates, starter manifests, distribution-state summaries, and available guarded follow-ups. | Gives the future GUI/global configuration view one stable backend source instead of requiring users or host AI to inspect scattered files. |

Runtime `policy_candidate` cards remain report-only evidence. They should not
drive automatic policy creation until lifecycle infrastructure can provide
better context and history.

Real-policy smoke note (2026-05-31): `POLICY-jikuo-data-model-drift-alarm`
was validated as an `optional_template` candidate. Status read, distribution
review with host semantic intent, publication plan, guarded refusal, and
temporary-directory guarded write all passed. The smoke also found a
precondition gap: missing `host_semantic_intent` on
`jikuo.propose_policy_distribution_review` returned `not_required` instead of
`semantic_intent_precondition`. The follow-up fix treats selected MCP proposal
tools as tool-level semantic-contract entry points, so missing semantic intent
is refused before no-write policy-management planning proceeds.

Real publication note (2026-05-31): after explicit user approval, the guarded
package-template publication path wrote
`src/jikuo/policy_templates/engineering_governance/POLICYTEMPLATE-local-policy-jikuo-data-model-drift-alarm.yaml`.
The policy-management read model now reports `package_template_count=5`,
`POLICY-jikuo-data-model-drift-alarm` as
`distribution_state=package_template_available`, and
`included_in_starter_packs=[]`. This confirms the first reusable policy package
asset can be published without mutating starter manifests or activating a user
project.

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
4. `POLICY-MGMT-01G`: expose the policy-management status read model for
   GUI/front-end use. Completed as a no-write CLI/MCP surface.

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

Activation completed on 2026-05-22 after explicit user approval in the
development session. The approval phrase is preserved in the guarded decision
records; this work order records only the fact of approval and the artifact
refs.

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

### 4.2 Policy Source Categories

Policy management must not treat all active policies as distributable product
assets. The MVP categories are:

| Category | Meaning | MVP handling |
|---|---|---|
| `project_local` | Active policy owned by the current project. | Keep in `.jikuo/policies/approved`; never overwrite from package updates. |
| `jikuo_dogfood` | Policy used to govern JIKUO's own development. | Not distributable until explicitly reviewed. |
| `official_starter` | Broad policy appropriate for new projects. | Offer through starter-pack preview and guarded activation. |
| `optional_template` | Scenario-specific reusable policy. | Offer through template import preview and guarded activation. |
| `deprecated` / `superseded` | Audit-retained historical record. | Keep for traceability; do not recommend for activation. |
| `insight` / `candidate` | Report-only idea before approval. | Needs no-write plan and guarded approval before active use. |

### 4.3 Official Distribution Flow

The MVP distribution flow is intentionally small:

```text
active or candidate policy
-> distribution review
-> dogfood-only / official_starter / optional_template / deferred
-> user-project no-write preview
-> guarded activation
```

Distribution review must record:

- source policy, proposal, decision, and manifest refs;
- target category and why it is reusable or dogfood-only;
- expected target projects or scenarios;
- conflict posture when a user project already has a local policy with the same
  purpose;
- evidence type that proves the policy works after activation.

No official distribution path may directly copy JIKUO's current
`.jikuo/policies/approved` files into user projects. Reusable policies must be
converted into package templates or starter-pack entries first, then resolved
through no-write preview in the target project.

The current no-write implementation is:

```powershell
python -B -m jikuo.policy_templates review-distribution `
  --source-policy ".jikuo/policies/approved/<POLICY-ID>.yaml" `
  --decision dogfood_only|official_starter|optional_template|deferred `
  --format json
```

This command only produces a `jikuo.policy_distribution_review.v0` report. It
does not export a package template, update a starter-pack manifest, activate a
policy in a user project, or rewrite the source policy. `official_starter` and
`optional_template` outcomes route to the existing template extraction /
template activation or starter-pack initialization paths; they are not
publication by themselves.

### 4.3.1 Guarded Template Publication

`optional_template` and `official_starter` distribution outcomes may be
published into package-owned policy templates only after a second guarded step.

The no-write publication plan is:

```powershell
python -B -m jikuo.policy_templates plan-publication `
  --source-policy ".jikuo/policies/approved/<POLICY-ID>.yaml" `
  --decision optional_template|official_starter `
  --format json
```

The guarded publication apply is:

```powershell
python -B -m jikuo.policy_templates publish-template `
  --source-policy ".jikuo/policies/approved/<POLICY-ID>.yaml" `
  --decision optional_template|official_starter `
  --confirm-publish-template `
  --approval-phrase "<exact user phrase as spoken>" `
  --format json
```

These commands produce `jikuo.policy_template_publication_plan.v0` and
`jikuo.policy_template_publication_result.v0`. Publication writes only a
reviewed package template under `src/jikuo/policy_templates/...`; it does not
activate a user-project policy, does not update starter-pack manifests, and
does not copy `.jikuo/policies/approved` into starter packs.

For `official_starter`, template publication leaves
`starter_pack_manifest_change_status: follow_up_required`. Starter-pack manifest
publication is a separate guarded step so the product can review default starter
inclusion independently from template availability.

### 4.3.2 Guarded Starter-Pack Manifest Publication

After a reviewed `official_starter` policy has been published as a package
template, it may be added to a starter pack manifest through a package-maintainer
guarded path.

The no-write manifest publication plan is:

```powershell
python -B -m jikuo.starter_policies plan-publish-template `
  --template-ref "pkg://jikuo/policy_templates/engineering_governance/<TEMPLATE>.yaml" `
  --pack-id engineering_governance `
  --format json
```

The guarded manifest publication apply is:

```powershell
python -B -m jikuo.starter_policies publish-template `
  --template-ref "pkg://jikuo/policy_templates/engineering_governance/<TEMPLATE>.yaml" `
  --pack-id engineering_governance `
  --confirm-manifest-publication `
  --approval-phrase "<exact user phrase as spoken>" `
  --format json
```

These commands produce `jikuo.starter_pack_manifest_publication_plan.v0` and
`jikuo.starter_pack_manifest_publication_result.v0`. They may update only the
package-owned starter manifest, and they continue to reject `.jikuo/policies`
refs, relative path escapes, absolute paths, duplicate template refs, and
duplicate starter policy IDs. They do not initialize a user project and do not
activate policies outside the later guarded starter-init path.

GUI / MCP users normally will not know a policy file path or `POLICY-*` id.
The user-facing path is therefore:

```text
user natural-language request
-> host AI interprets the requested policy purpose
-> JIKUO receives policy_query or an explicit policy_ref/source_policy
-> JIKUO resolves a single active policy or returns candidates
-> no-write distribution review card
-> guarded export / starter publication / activation follow-up
```

The MCP / agent-flow proposal surface is:

```powershell
python -B -m jikuo.agent_flow propose `
  --event policy_distribution_review `
  --distribution-policy-query "natural-language policy purpose" `
  --distribution-decision dogfood_only|official_starter|optional_template|deferred `
  --format json
```

`jikuo.propose_policy_distribution_review` exposes the same no-write surface to
MCP clients. It accepts `policy_ref`, `source_policy`, or natural-language
`policy_query`. The host AI may translate the user's natural-language request
into a compact `policy_query`, but the current JIKUO resolver is deterministic
candidate matching, not an LLM semantic classifier. If the query does not match
exactly one active policy, JIKUO returns a candidate list and refusal reasons
instead of silently binding the review to the wrong policy.

CLI callers may use `--policy-ref` or the clearer
`--distribution-policy-ref` alias when the host AI has already selected the
source policy. Both flags resolve through the same explicit-policy-ref path.

### 4.4 Policy-Management Status Read Model

The MVP backend now exposes a read-only state model for future GUI and global
configuration surfaces:

```powershell
python -B -m jikuo policy-management status --format json
```

and through MCP:

```text
jikuo.get_policy_management_status
```

The report schema is `jikuo.policy_management_status.v0`. It reads only:

- project-local active policy refs from `.jikuo/policies/manifest.yaml`;
- package-owned policy templates under `src/jikuo/policy_templates/...`;
- package-owned starter-pack manifests under
  `src/jikuo/starter_policy_packs/...`.

It does not publish templates, update starter manifests, activate user-project
policies, write runtime cards, or change evaluator behavior. Its business role
is to give a thin front-end one stable backend source for "what policies exist,
what templates are available, what starter packs include, and which guarded
follow-up operation is next."

### 4.5 Active-Policy Maintenance Outcomes

Once a policy is active, maintenance uses guarded evolution, not direct edits.

| Situation | Required path |
|---|---|
| Too broad | Narrow scope or supersede through guarded evolution. |
| Duplicate or overlapping | Merge conceptually, then supersede / deprecate one record. |
| JIKUO-only | Mark dogfood-only in distribution review. |
| Reusable | Promote to official starter or optional template after review. |
| Obsolete | Deprecate through guarded evolution. |

### 4.6 MVP Closeout Acceptance

Policy Management MVP closeout is accepted when:

- candidate-to-active path is demonstrated through the two activated policies;
- policy source categories are documented in this work order and the governance
  authority;
- official distribution flow is documented as opt-in preview plus guarded
  activation;
- `python -B -m jikuo.policy_templates review-distribution ...` produces a
  no-write review report for dogfood-only, official-starter, optional-template,
  or deferred outcomes;
- `python -B -m jikuo.policy_templates plan-publication ...` and
  `publish-template ... --confirm-publish-template --approval-phrase ...`
  produce no-write publication plans and guarded package-template publication
  results for reusable outcomes without activating user-project policies;
- `python -B -m jikuo.starter_policies plan-publish-template ...` and
  `publish-template ... --confirm-manifest-publication --approval-phrase ...`
  produce no-write starter-manifest publication plans and guarded manifest
  updates for package template refs without initializing user projects;
- `python -B -m jikuo.agent_flow propose --event policy_distribution_review ...`
  and MCP `jikuo.propose_policy_distribution_review` expose the same no-write
  review to GUI clients, including natural-language `policy_query` resolution
  with ambiguity refusal;
- `python -B -m jikuo.agent_flow propose --event policy_template_publication_plan ...`
  and MCP `jikuo.propose_policy_template_publication_plan` expose package-template
  publication as a no-write visible card, while guarded apply remains
  `agent_flow apply --operation policy_template_publication` or MCP
  `jikuo.apply_policy_template_publication`;
- `python -B -m jikuo.agent_flow propose --event starter_manifest_publication_plan ...`
  and MCP `jikuo.propose_starter_manifest_publication_plan` expose starter-pack
  manifest publication as a separate no-write visible card, while guarded apply
  remains `agent_flow apply --operation starter_manifest_publication` or MCP
  `jikuo.apply_starter_manifest_publication`;
- `python -B -m jikuo policy-management status ...` and MCP
  `jikuo.get_policy_management_status` expose the no-write
  `jikuo.policy_management_status.v0` read model for GUI/front-end use;
- active-policy maintenance outcomes are documented;
- registry capability metadata points future implementation to this closeout
  design.

---

## 5. Stop Boundaries

- Do not directly edit the activated policy YAML files to change semantics;
  future narrowing, merging, or deprecation must use guarded policy evolution.
- Do not add duplicate replacement policies for these candidates without first
  reviewing whether guarded evolution is the correct path.
- Do not publish JIKUO dogfood policies as official starter policies without
  distribution review.
- Do not treat starter-pack or template availability as user-project activation.
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

## 6. Acceptance For MVP Closeout Documentation

- `docs/governance/jikuo_policy_governance_authority.md` names the MVP boundary
  and records the candidate activation result.
- The same governance authority defines policy source categories, distribution
  review flow, and active-policy maintenance outcomes.
- `docs/governance/jikuo_execution_mounts.md` names `LIFECYCLE-01` as the
  current priority and keeps this work order lightweight.
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md`
  preserves the candidate origin text and records that both candidates are now
  active report-only policies.
- `docs/registry/work_orders.yaml`, `docs/registry/capabilities.yaml`, and
  `docs/registry/mount_sets.yaml` expose this task to future sessions.
- `CAP-POLICY-DISTRIBUTION-MVP-01` and
  `CAP-POLICY-DISTRIBUTION-REVIEW-01` point future implementation to this
  design and the no-write distribution review surfaces instead of treating
  distribution as direct copy.
- `docs/governance/jikuo_productization_task_map.md` remains untouched except
  for explicitly approved projection maintenance.
