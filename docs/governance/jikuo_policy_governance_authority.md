# JIKUO Policy Governance Authority

> **Status**: Draft authority for JIKUO policy-governance design.
> **Created**: 2026-05-17
> **Purpose**: keep policy lifecycle, scope, trigger routing, hint handling, and distribution rules in one mounted document so future agents do not reconstruct policy governance from stale chat memory or scattered work-order fragments.
> **Non-goal**: this document does not activate, edit, deprecate, supersede, distribute, or implement any policy by itself.

---

## 1. Authority

This document is the current human-readable authority for JIKUO policy governance.
It complements, but does not replace:

- `.jikuo/policies/manifest.yaml`: active project-local policy-store index.
- `docs/governance/jikuo_configurable_rule_trigger_policy.md`: configurable trigger-policy contract.
- `docs/governance/jikuo_policy_store_configuration_flow.md`: policy-store lifecycle and guarded write contract.
- `docs/governance/jikuo_policy_aware_agent_flow_contract.md`: policy-aware proposal and card projection contract.
- `docs/insights/INSIGHT-2026-05-17-conservative-task-classification-routing.md`: originating insight for conservative task classification.
- `docs/insights/INSIGHT-2026-05-17-work-unit-task-association-boundary.md`: deferred data-architecture insight for future task-to-runtime execution association.
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-20_policy_dead_zone_detection.md`: policy dead-zone visibility work.
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLTRIG-03_policy_scope_evaluator_consumption.md`: registered evaluator-consumption task with dead-zone evidence and stop boundary.
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLTRIG-04_scope_first_policy_triggering.md`: compatibility slice that makes scope-only policies trigger from work-profile scope instead of brittle lifecycle-node invocation.

When these documents appear to conflict, use this document for policy-governance
direction and use the lower-level contracts for current implemented storage,
schema, and command details.

---

## 2. Policy Governance Is Broader Than Document Governance

Document-registry governance is only one policy-governance use case.

JIKUO policy governance covers at least:

- how policy candidates are discovered from repeated user needs;
- how policy candidates become reviewable plans;
- how approved policies enter a project-local policy store;
- how active policies are triggered without relying on agent memory;
- how missing or mismatched triggers are surfaced;
- how policy evidence is recorded without raw chat capture;
- how policies are deprecated, superseded, or excluded from a task;
- how official policy templates and starter packs are distributed without
  overwriting user-owned policies.

Policy governance must not be reduced to a single domain policy such as
`DOCREG-01B3`. Domain policies are examples that consume this governance model.

---

## 3. Lifecycle Model

JIKUO policy lifecycle states should remain explicit:

1. `observed_need`: a repeated user need, correction, product principle, or risk is noticed.
2. `insight`: the idea is recorded without changing active policy.
3. `policy_candidate`: JIKUO proposes that the idea could become a policy.
4. `policy_plan`: a no-write proposal describes trigger, action, evidence, scope, and risk.
5. `approved_active_policy`: an explicit guarded apply writes an active policy.
6. `deprecated_policy`: an active policy is intentionally removed from active refs.
7. `superseded_policy`: a replacement policy has been reviewed and activated.

No natural-language discussion, insight capture, task map update, or starter-pack
sync may skip the guarded boundary between `policy_plan` and
`approved_active_policy`.

### 3.1 User Interaction Execution Model

Every user message creates a user-turn boundary. If the AI does anything with
that message--answers, reads files, searches, analyzes, edits, proposes policy,
or prepares a handoff--JIKUO should be able to model that work as a governed
processing instance.

`LIFECYCLE-01B` treats the first implemented MVP processing surface as an
`observed_lifecycle`: a record-only runtime projection created only after JIKUO
is actually invoked for a turn. It is not a lifecycle runner, not a durable task
session, not a `work_order_id`, and not DATA-01 append-only event authority.

The user-facing work lifecycle should be small and hard to miss:

1. `conversation_turn`: the user message enters the governed project. JIKUO
   routes, classifies, detects initialization needs, and records compact
   evidence without storing raw chat transcripts.
2. `task_start`: the AI begins processing that turn. This is not synonymous
   with code editing and is not synonymous with a durable task-session write.
   A `task_start` may be discussion, research, read-only inspection, local
   command execution, documentation work, code editing, configuration, or
   policy-governance work.
3. `completion_review`: the AI is ready to return work to the user. JIKUO
   checks policy runtime status, evidence, main-document obligations, and
   summary / business-meaning obligations before user-visible delivery.

This model separates lifecycle from work nature:

```text
User turn -> conversation_turn -> task_start -> completion_review
                         \          \              \
                          \          work_profile   evidence/status review
                           route/config review
```

`task_session_start` is a durable evidence-carrier decision inside a governed
task. It must remain guarded and explicit. It must not be treated as the only
meaning of `task_start`.

Important distinction:

- `work_profile.lifecycle_event` says where this work unit is in the lifecycle;
- `work_profile.policy_scopes` says what kind of work is being performed;
- a governed work unit should traverse the lifecycle, while the scope should
  remain available to the later completion review.

Design correction recorded on 2026-05-22:

- `task_start` may remain as an observed execution marker. It can show that the
  agent has begun processing a turn, and it can still carry task-session /
  work-routing / start-processing projection evidence.
- `task_start` should not be treated as the business source of policy
  applicability for intent-driven policies. User intent, policy scope, mounted
  runtime context, guarded-write context, and final response contract are the
  policy-distribution concerns.
- Therefore `task_start + discussion` may appear together as two independent
  facts: processing has begun, and the work nature is discussion. The former
  should not cause or suppress the latter.
- Current code still allows policies to declare lifecycle events through
  `applies_to_work_profile.lifecycle_events`; that is a compatibility boundary,
  not the long-term policy-routing model.

Current implementation gap and safety boundary:

- today, `agent_flow` and MCP proposal calls evaluate one explicitly requested
  event at a time;
- a policy scoped to `completion_review` can therefore be correct but invisible
  if no completion-review call is made;
- future `work_order_id -> work_unit_id -> proposal/card` association must not
  be guessed from recent cards, task titles, or changed paths;
- `INSIGHT-2026-05-17-work-unit-task-association-boundary` records that this
  heavier data-architecture correction is deferred until a strict client hook or
  adapter can prove reliable JIKUO invocation.

Current code still exposes several tool-specific events such as
`configuration_review`, `policy_evolution_plan`, `policy_template_import_plan`,
and `evidence_review`. Those names are implementation surfaces, not a reason to
expand the core user-work lifecycle. Future projection work should preserve
existing tool compatibility while adding a `work_profile.lifecycle_event` that
uses the three user-work lifecycle values above.

---

### 3.2 Focused Policy Management Boundary

Near-term policy management should stay lightweight while lifecycle data is
still not explicit enough to support high-quality policy insight.

For the current MVP, policy management means:

1. keep the two formerly held user-authored candidates active through the
   guarded policy-write records that created them;
2. design official distribution boundaries so reusable policies can become
   package templates or starter-pack entries without copying JIKUO dogfood
   policies into user projects.

It does not yet mean building a heavy durable candidate-disposition registry or
asking JIKUO to generate new policy insights from incomplete lifecycle data.
Runtime `policy_candidate` cards remain report-only evidence and cannot become
active policies by themselves.

The two held candidates in `DOCREG-01` became the first manual activation set on
2026-05-22:

- `POLICY-jikuo-first-principles-critical-alignment`
- `POLICY-jikuo-data-model-drift-alarm`

For the first activation pass, do not add new policy-name-like scope values for
these candidates. Use the existing stable scope classes:

- first-principles / critical alignment belongs to `discussion`;
- data-model drift alarm belongs to `editing`.

The narrower behavior is expressed through policy title, required action,
required evidence, and `process_contract` / `response_contract` text. This keeps
`policy_scopes` as broad routing classes instead of turning them into policy
identifiers.

Both were written as `active_report_only` through no-write policy plans,
explicit user approval, and guarded policy writer output. Future changes should
use guarded policy evolution rather than direct YAML edits. Do not invent a
separate candidate lifecycle before `LIFECYCLE-01` makes turn lifecycle facts
more explicit.

---

## 4. Policy Scope Classes

JIKUO should avoid many fragile task categories. Too many fine-grained classes
increase policy miss risk because one misclassification can route work outside
the intended policy set.

The current abstract policy-scope classes are:

| Class | Meaning | Minimum policy posture |
|---|---|---|
| `discussion` | Design, explanation, analysis, trade-off review, decision support, or conceptual review. | Low-risk discussion governance, proactive policy suggestion, business-meaning visibility where relevant. |
| `editing` | Code, documentation, configuration, tests, commits, release work, migration, deletion, archive, or any durable project change. | Stricter editing governance, task-session binding, main-document checks, verification/evidence obligations. |
| `progress_summary` | Progress, todo, status, roadmap, handoff, or business-meaning summary. | Progress-summary business meaning and taskmap / insight / follow-up distinction. |
| `other` | Unclear, mixed, low-confidence, or not-yet-modeled user turn. | Must not mean no-op; conservatively expands at least to `discussion + editing`. |

The design goal is not perfect classification. The design goal is to prevent
silent policy miss.

Scope naming rule:

- `policy_scopes` should name stable work / risk / response contexts, not the
  title of a specific policy.
- A policy-specific concept such as first-principles critique or data-model
  boundary review should normally appear as `process_contract`, required
  action, required evidence, and response obligation.
- Add a new scope only when several policies need the same reusable routing
  context and the existing `discussion`, `editing`, and `progress_summary`
  classes are demonstrably too broad.

---

## 5. Routing Ownership

Host adapters and AI clients must not be the authority for policy scope.

| Layer | Responsibility |
|---|---|
| Host hook / MCP client / Studio | Ensure the user turn enters JIKUO when the project is mounted. |
| AI agent | Provide a structured semantic hint when invoking JIKUO. |
| JIKUO core router | Combine the hint with deterministic signals and conservative fallback. |
| Policy evaluator | Match active policies against the resulting policy scopes and event context. |
| User | Review, correct, approve, reject, or defer policy changes and durable writes. |

The AI agent can help with semantic interpretation, but JIKUO core must produce
the auditable classification result.

Policy routing maps user intent to policy scope. It should not treat the
agent's internal `see / think / act / speak` loop as the primary classification
axis. Those verbs are dynamic execution and reporting vocabulary: they explain
which context was read, which reasoning or tools were used, and what evidence
must be reported. The auditable routing result remains the final
`work_profile.policy_scopes` produced by JIKUO.

Policy can still govern method and reasoning. "What the user wants the agent to
achieve" is a policy concern, and "how the user wants the agent to think,
evaluate, sequence, or decide" is also a policy concern. JIKUO should represent
that second class as `process_contract` in router / card explanation before
making it an evaluator input.

The response is the policy-governed delivery surface. Universal policies may
shape every response, such as runtime-card visibility, guarded-write reminders,
or missing-evidence disclosure. Current-intent policies add obligations for the
specific scope, such as changed files and tests for `editing`, business meaning
for `progress_summary`, or assumptions and trade-offs for `discussion`. If a
turn includes side effects, the same policy scope must govern the action before
and during execution, not only the final wording.

The same separation applies to lifecycle markers. `conversation_turn`,
`task_start`, and `completion_review` can describe when a projection was
produced. They are not, by themselves, the reason a reasoning, data-modeling,
response, mounted-mode, or guarded-write policy should apply. Long-term policy
distribution should be modeled as:

```text
user_intent + runtime_context + response_contract
  -> policy_scope / required_actions / required_evidence
```

where `runtime_context` includes facts such as mounted mode, guarded writes,
tool effects, and final response delivery.

---

## 6. Hint + Signal + Fallback Model

Policy routing should be:

> **hint-assisted, deterministic-checked, and fallback-expanded.**

### 6.1 Inputs

JIKUO should combine three input classes:

1. `agent_hint`: semantic interpretation supplied by the invoking AI.
2. `deterministic_signals`: keywords, command shape, changed paths, added paths,
   tool names, write intent, and explicit task metadata.
3. `fallback_rules`: conservative expansion when signals are missing, weak, or
   conflicting.

### 6.2 Agent hint

AI calls should provide a structured hint where possible:

```json
{
  "agent_hint": {
    "requested_outcome": "explain the design without editing files",
    "process_contract": [
      "align concepts before implementation details",
      "critique the proposal against the business goal"
    ],
    "intent_class": ["discussion"],
    "operation_class": ["no_tool"],
    "output_class": ["answer"],
    "execution_boundary": "read_only",
    "response_contract": ["explain recommendation", "name assumptions"],
    "confidence": "medium",
    "reason": "user is asking for design judgement, not asking to edit files",
    "expected_write_effect": "none"
  }
}
```

The hint is required for good UX because the AI understands natural-language
context better than a keyword router. However, it is not sufficient for
governance because it can be wrong, vague, or overly optimistic.

### 6.3 Deterministic signals

JIKUO core should detect hard signals that cannot be downgraded by an AI hint.

Examples that imply at least `editing`:

- words such as implement, modify, fix, migrate, delete, update docs, test,
  commit, release, archive, or continue the next development task;
- supplied `changed_paths` or `added_paths`;
- write-mode or guarded-write tool calls;
- code, docs, configuration, registry, policy-store, or task-session target paths;
- git operations that change repository state.

Examples that imply `progress_summary`:

- progress, todo, status, summary, roadmap, business meaning, handoff.

Examples that imply `discussion`:

- discuss, explain, compare, evaluate, "what do you think", design review,
  conceptual question, risk analysis.

### 6.4 Priority rule

Routing priority is not "one source overrides another." It is:

1. collect AI hint and deterministic signals;
2. apply deterministic hard-signal minimums;
3. let AI hint add semantic context;
4. merge scopes instead of narrowing them when sources disagree;
5. run fallback expansion last when confidence is low or conflict exists.

Hard signals prevent downgrade. AI hint improves understanding. Fallback prevents
policy miss.

### 6.5 Fallback rule

If the classification is `other`, mixed, low confidence, or conflicting:

```text
policy_scopes = ["discussion", "editing"]
fallback_expanded = true
```

`other` must never mean "no policy applies."

### 6.6 Work-profile output shape

The router should eventually produce an auditable `work_profile`. This is the
bridge between lifecycle event and policy triggering:

```json
{
  "work_profile": {
    "schema": "jikuo.work_profile.v0",
    "lifecycle_event": "task_start",
    "intent_class": ["discussion"],
    "operation_class": ["read_only"],
    "output_class": ["plan"],
    "policy_scopes": ["discussion"],
    "basis": {
      "agent_hint": {
        "intent_class": ["discussion"],
        "operation_class": ["read_only"]
      },
      "deterministic_signals": [
        {
          "signal": "user_requested_code_inspection",
          "minimum_operation_class": "read_only"
        }
      ],
      "fallback": "not_expanded"
    },
    "confidence": "medium",
    "fallback_expanded": false
  }
}
```

If sources conflict or confidence is low, `fallback_expanded` should become
`true` and `policy_scopes` should expand conservatively:

```json
{
  "work_profile": {
    "lifecycle_event": "task_start",
    "intent_class": ["other"],
    "operation_class": ["local_command"],
    "output_class": ["answer"],
    "policy_scopes": ["discussion", "editing"],
    "confidence": "low",
    "fallback_expanded": true
  }
}
```

`work_profile` is distinct from current conversation-turn follow-up obligations
such as `task_start`, `completion_review`, `configuration_review`, or
`policy_suggestion_review`. Follow-up obligations say which tool may be useful
next. `work_profile` says what kind of governed work is happening and which
policy scopes should be considered.

`requested_outcome`, `process_contract`, `execution_boundary`, and
`response_contract` may appear as router/card explanation fields when AI
semantic input is available. They are not a replacement for `policy_scopes`,
and they are not POLTRIG-03 evaluator inputs. Until a reviewed schema slice
says otherwise, the evaluator still consumes only
`work_profile.lifecycle_event` and `work_profile.policy_scopes`, with exact
policy conditions as additional filters.

`semantic_intent_classification_evidence` is the report-only bridge between
this authority and host-AI behavior. It does not perform classification and it
does not expand evaluator inputs. Instead, it records whether a compact
`host_semantic_intent` or dedicated provider was required and supplied for the
current `work_profile`. Pure `discussion` turns may remain fallback-only, while
`editing`, `progress_summary`, and project-state-changing work should surface
`required=true`; if no semantic provider supplied intent, the card must show
`status=missing` or `fallback_only` and a follow-up to rerun routing with
compact `host_semantic_intent`.

Current architecture review conclusion: the main gap is contract enforcement,
not the scope taxonomy. The minimum hardening now implemented turns missing
semantic intent for selected governed editing / write-capable MCP entry points
into a no-write `semantic_intent_precondition` / `precondition_unmet` tool
response that asks the host AI to classify and re-call with compact
`host_semantic_intent`. This does not affect pure discussion fallback, does not
call a model from JIKUO, does not expand evaluator inputs, and does not change
the MVP scope set.

The two held user-authored policy candidates are examples of process-contract
policy needs:

- `POLICY-CANDIDATE-first-principles-critical-alignment` constrains how the
  agent should reason before accepting a proposal.
- `POLICY-CANDIDATE-data-model-drift-alarm` constrains how the agent should
  evaluate field/schema/layer growth before adding structure.

Under the corrected model, these candidates should not depend on whether a
separate `task_start` projection happened. Their applicability is a function of
the user intent / policy scope and the required process contract. The first
lightweight implementation shape is `conversation_turn` plus scope-only
`applies_to_work_profile`, which preserves `task_start` as an observed marker
instead of a distribution cause.

### 6.7 Policy-Contract Field Consumption Proof

`requested_outcome`, `process_contract`, `execution_boundary`, and
`response_contract` are useful only when the system can show where they were
used. Until a separate reviewed slice changes evaluator scope, their proof of
effect must be staged, not implied.

| Proof level | Meaning | Minimum evidence |
|---|---|---|
| Visible projection | JIKUO received or derived the field and rendered it without storing raw prompt text. | Work-profile / runtime-card field display, state summary, or history card. |
| Planning use | The agent used the field to shape the visible plan or work order before acting. | Plan text, task-start summary, or guarded proposal that names the relevant contract. |
| Evidence verification | A policy required proof that the contract was followed, and completion review checked it. | `required_evidence` item with `ok`, `missing`, `deferred`, or `not_applicable` status. |
| Boundary enforcement or flagging | The field blocked, gated, or visibly flagged an action that would violate the contract. | No-write/guarded-write result, missing-evidence report, conflict report, or explicit stop. |

The field-specific target is:

- `requested_outcome`: prove that the reported result addresses the user's
  intended outcome, not only the literal command shape.
- `process_contract`: prove that the required reasoning or evaluation method
  happened through a named evidence type, such as
  `first_principles_alignment_evidence` or
  `data_model_boundary_review_evidence`.
- `execution_boundary`: prove that allowed effects, guarded effects, and blocked
  effects were respected.
- `response_contract`: prove that the final answer included the promised
  evidence, risks, assumptions, card links, or follow-up decisions.

This proof ladder keeps the architecture light. The evaluator consumes the
current evaluation event as a runtime surface and `work_profile.policy_scopes`
as the business applicability signal. A declared
`work_profile.lifecycle_event` is consumed only when the policy author declares
`lifecycle_events`. Policy authors express the richer contract through required
actions, required evidence, and runtime-card explanation.

---

## 7. Trigger Governance

JIKUO should distinguish:

- `event`: the current implemented tool or lifecycle event name. Existing code
  still accepts broad names such as `configuration_review`,
  `policy_evolution_plan`, and `policy_template_import_plan` for compatibility.
- `work_profile.lifecycle_event`: the user-work lifecycle stage:
  `conversation_turn`, `task_start`, or `completion_review`.
- `policy_scope`: the conservative class used to decide which policy groups
  apply, such as `discussion`, `editing`, `progress_summary`, or fallback-expanded
  `discussion + editing`;
- `condition_context`: supplied task metadata such as changed paths, JIKUO layer,
  policy refs, task session refs, or evidence refs.

Policy miss often happens when these are conflated. A precise event with a
missing or over-narrow scope can still produce zero triggered policies.

The preferred future direction is for policies to declare scope applicability:

```yaml
applies_to_work_profile:
  - policy_scopes: ["editing"]
```

or:

```yaml
applies_to_work_profile:
  - lifecycle_events: ["completion_review"]
    policy_scopes: ["progress_summary"]
```

The evaluator can then match policies against `policy_scopes` generated by the
router instead of depending only on brittle exact `task_type` or `jikuo_layer`
values.

Practical rule:

```text
implemented event routes the current tool path;
work_profile.lifecycle_event says where this sits in the user-work lifecycle;
work_profile.policy_scopes says which policy groups should be considered;
declared lifecycle_events are optional hard filters for policies that truly
belong to a lifecycle node;
conditions and evidence decide whether a specific policy is satisfied.
```

Current compatibility behavior:

- Exact event matches still evaluate first, preserving legacy and checkpoint
  policies.
- Scope-only policies (`policy_scopes` declared and `lifecycle_events` empty)
  can now match from the current work profile even when the policy's declared
  trigger event is only a compatibility anchor.
- A declared `lifecycle_events` value still gates policy applicability. This is
  useful for existing task-session, runtime-card, and completion-review
  policies, but it is too strong for intent-driven reasoning policies.
- Intent-driven reasoning policies should use `conversation_turn` plus
  scope-only applicability unless a lifecycle filter is genuinely part of the
  policy.

2026-06-03 correction:

- `POLICY-jikuo-progress-summary-business-meaning` is an intent / response
  obligation, not a completion-review-only lifecycle checkpoint.
- Its `applies_to_work_profile` now uses scope-only
  `policy_scopes: ["progress_summary"]` while retaining the existing
  completion-review trigger as a compatibility anchor.
- This lets host-AI follow-up routing for "summarize progress / output todos"
  trigger the business-meaning obligation from `conversation_turn`,
  `task_start`, or `completion_review` without adding new scope names,
  evaluator inputs, policy actions, evidence types, or enforcement behavior.
- The Codex hook may instruct the host AI to submit compact
  `host_semantic_intent` after the host has read the turn, but that remains a
  cooperative transport contract. It is not hook-time semantic classification
  and not proof of strict mounted lifecycle orchestration.

---

## 8. Policy Dead-Zone Relationship

LIVE-20 detects when governance appears to run but no policy triggers.

This authority document defines the complementary fix direction:

- do not add more fragile categories as the first response;
- add a small policy-scope layer;
- require AI hints where available;
- enforce deterministic hard-signal minimums;
- conservatively expand uncertain work into broader policy scopes;
- surface the resulting classification in runtime cards.

A zero-trigger result after fallback expansion is stronger evidence of a true
coverage gap than a zero-trigger result from an under-specified task context.

---

## 9. Policy Distribution Boundary

User projects must not receive JIKUO self-bootstrap policies by pulling the
JIKUO development repository.

Policy sources should remain separated:

| Category | Intended use | Distribution posture |
|---|---|---|
| `project_local` | User-owned active project policy store in `.jikuo/policies/approved`. | Never overwritten by updates; changes require local guarded writes or guarded evolution. |
| `jikuo_dogfood` | Policies that govern JIKUO's own development and self-bootstrap work. | Not shipped directly to user projects. Must be reviewed before becoming reusable. |
| `official_starter` | Small, broadly useful policies suitable for first-use starter packs. | Offered as opt-in preview, then guarded activation in the target project. |
| `optional_template` | Scenario-specific reusable policy templates. | Imported through no-write preview and guarded activation; not default. |
| `deprecated` / `superseded` | Historical policy records retained for audit. | Not recommended for new activation. |
| `insight` / `candidate` | Ideas, repeated needs, or candidate policies before approval. | Report-only; cannot become active without no-write plan and guarded approval. |

Official updates may offer new starter packs or template revisions, but must not
overwrite user-approved local policies. Catalog sync must remain opt-in and
reviewable.

MVP distribution flow:

```text
active or candidate policy
-> distribution review
-> dogfood-only / official_starter / optional_template / deferred
-> user-project no-write preview
-> guarded activation
```

Distribution review must answer:

- whether the policy is JIKUO-specific dogfood or reusable user value;
- which projects or scenarios the policy is appropriate for;
- what source policy / proposal / decision records prove provenance;
- whether activation would conflict with existing user-owned local policies;
- which evidence type proves the policy is working after activation.

Distribution review is implemented first as a no-write CLI report:

```powershell
python -B -m jikuo.policy_templates review-distribution `
  --source-policy ".jikuo/policies/approved/<POLICY-ID>.yaml" `
  --decision dogfood_only|official_starter|optional_template|deferred `
  --format json
```

The report schema is `jikuo.policy_distribution_review.v0`. The command may
recommend template extraction, optional template activation, or starter-pack
review, but it cannot publish templates, mutate starter manifests, activate user
project policies, or rewrite the source policy.

Reusable outcomes then use a separate guarded publication boundary. The
no-write plan is:

```powershell
python -B -m jikuo.policy_templates plan-publication `
  --source-policy ".jikuo/policies/approved/<POLICY-ID>.yaml" `
  --decision optional_template|official_starter `
  --format json
```

The guarded apply is:

```powershell
python -B -m jikuo.policy_templates publish-template `
  --source-policy ".jikuo/policies/approved/<POLICY-ID>.yaml" `
  --decision optional_template|official_starter `
  --confirm-publish-template `
  --approval-phrase "<exact user phrase as spoken>" `
  --format json
```

These produce `jikuo.policy_template_publication_plan.v0` and
`jikuo.policy_template_publication_result.v0`. They may write package-owned
policy templates, but they must not activate user-project policies, must not
update starter-pack manifests, and must not copy `.jikuo/policies/approved`
files into starter packs. `official_starter` publication leaves starter-pack
manifest inclusion as a separate guarded follow-up.

Starter-pack manifest inclusion also has its own boundary:

```powershell
python -B -m jikuo.starter_policies plan-publish-template `
  --template-ref "pkg://jikuo/policy_templates/engineering_governance/<TEMPLATE>.yaml" `
  --pack-id engineering_governance `
  --format json
```

```powershell
python -B -m jikuo.starter_policies publish-template `
  --template-ref "pkg://jikuo/policy_templates/engineering_governance/<TEMPLATE>.yaml" `
  --pack-id engineering_governance `
  --confirm-manifest-publication `
  --approval-phrase "<exact user phrase as spoken>" `
  --format json
```

These produce `jikuo.starter_pack_manifest_publication_plan.v0` and
`jikuo.starter_pack_manifest_publication_result.v0`. They may update only a
package-owned starter manifest. They must reject non-template refs, project-local
`.jikuo/policies` refs, duplicate template refs, and duplicate starter policy
IDs; they must not initialize or activate policies in any user project.

GUI and MCP users should not be expected to provide internal policy labels or
file paths. The user-facing distribution path must support natural-language
requests:

```text
user natural-language request
-> host AI interprets requested policy purpose
-> JIKUO receives policy_query or an explicit policy_ref/source_policy
-> deterministic active-policy source resolution
-> distribution review card, or candidate-list refusal when ambiguous
```

The current MCP / agent-flow surface is
`jikuo.propose_policy_distribution_review` and
`agent_flow propose --event policy_distribution_review`. These surfaces accept
`policy_ref`, `source_policy`, or natural-language `policy_query`, then return a
no-write `jikuo.policy_distribution_review.v0` card when exactly one active
policy resolves. If no unique match exists, they return
`jikuo.policy_distribution_source_resolution.v0` with candidates and refusal
reasons. This resolver is auditable deterministic matching over active policy
metadata and content; it is not the same as AI semantic intent parsing. A host
AI may help turn the user's natural language into a compact `policy_query`, but
JIKUO must refuse ambiguity rather than guessing the source policy.

Active-policy maintenance outcomes:

| Situation | Required path |
|---|---|
| Policy is too broad | Guarded evolution with scope narrowing or supersession. |
| Policy is duplicated | Merge conceptually, then deprecate or supersede through guarded evolution. |
| Policy is JIKUO-only | Mark dogfood-only in distribution review; do not publish as starter. |
| Policy is reusable | Convert to official starter or optional template only after review. |
| Policy is no longer useful | Deprecate through guarded evolution while preserving audit records. |

---

## 9.5 Scope Metadata Migration

`applies_to_work_profile` is policy distribution metadata. Adding or updating it
on an already-approved policy may be performed as a single in-place metadata
migration when the same change does not alter:

- `triggers`;
- `conditions`;
- `required_actions`;
- `required_evidence`;
- `enforcement`;
- policy status, version, supersession, or deprecation state.

Such migrations must be recorded in the governing work order and git commit as a
bounded backfill list. They do not require one `POLICYPROPOSAL-*` or
`POLICYDECISION-*` record per policy because the existing action/evidence and
enforcement contract remains unchanged. Any change to observable policy
obligations, enforcement, or existing trigger/condition semantics must still use
the guarded policy evolution path.

---

## 10. Current Implementation Gap

Current JIKUO has:

- exact lifecycle event matching for legacy and checkpoint policies;
- scope-first matching for scope-only intent-driven policies;
- report-only condition evaluation;
- policy runtime status cards;
- conversation-turn router follow-up obligations;
- proactive policy-suggestion review evidence;
- policy dead-zone per-card classification;
- no-write `work_profile` projection on proposal and MCP responses;
- lightweight `task_start` processing projection that is separate from guarded
  `task_session_start` creation;
- policy `applies_to_work_profile` declarations consumed by the evaluator for
  `work_profile.policy_scopes` and, when declared, `work_profile.lifecycle_event`,
  with exact conditions preserved as additional filters;
- runtime cards that show work-profile inputs and scope-match reports for
  triggered-policy decisions;
- two formerly held `DOCREG-01` policy candidates activated as
  `active_report_only` through no-write plans and guarded policy writer output;
- lightweight official distribution design covering source categories,
  distribution review, and active-policy maintenance outcomes;
- no-write `policy_templates review-distribution` reports that classify a
  policy as dogfood-only, official starter, optional template, or deferred
  without publishing or activating it;
- no-write `policy_templates plan-publication` reports and guarded
  `publish-template` writes that convert reviewed reusable policies into
  package-owned templates without activating user projects or mutating starter
  packs;
- no-write `starter_policies plan-publish-template` reports and guarded
  `publish-template` writes that append reviewed package template refs to
  package-owned starter manifests without initializing user projects;
- no-write `policy_distribution_review` agent-flow / MCP proposal cards that
  let GUI clients request the same review by `policy_ref`, `source_policy`, or
  natural-language `policy_query`, with ambiguity refusal instead of hidden
  guessing;
- no-write `policy_template_publication_plan` and
  `starter_manifest_publication_plan` agent-flow / MCP proposal cards, plus
  guarded `policy_template_publication` and `starter_manifest_publication`
  agent-flow / MCP apply paths;
- no-write `jikuo.policy_management_status.v0` read model through CLI and MCP
  so GUI/front-end surfaces can inspect active policies, package templates,
  starter manifests, distribution state, and available guarded follow-ups from
  one backend source;
- MCP surfaces for route, status, proposals, and guarded writes.

Current JIKUO does not yet have:

- lifecycle-node completion orchestration that ensures a pulled-up JIKUO turn
  reaches completion review in addition to task start;
- structured `agent_hint` input on every router path;
- full hint/signal/fallback routing detail in runtime cards and structured
  execution events;
- strict host adapters that guarantee every user turn supplies the hint and calls
  JIKUO before the model response.

These are policy-governance tasks, not document-registry tasks.

---

## 11. Implementation Sequence

Recommended future slices:

1. `POLTRIG-01A`: add `work_profile` projection for proposal output only. It
   must include `agent_hint`, deterministic signals, `intent_class`,
   `operation_class`, `output_class`, `policy_scopes`, confidence, and fallback
   expansion. It must not change evaluator behavior. Current implementation
   status: projected in `agent_flow` proposals and MCP proposal / router
   responses; policy-store matching is intentionally unchanged.
2. `POLTRIG-01B`: separate lightweight `task_start` processing from durable
   `task_session_start`. `task_start` should represent AI processing of the
   user turn; task-session creation remains guarded and explicit. Current
   implementation status: `task_start` proposals produce a no-write
   `task_start_processing` card, `task_start_processing_evidence`, and
   `CAP-TASK-START-PROCESSING-01` trace before any task-session binding,
   deferral, preview, or guarded apply path. Policy evaluator behavior remains
   unchanged.
3. `POLTRIG-02`: let policies declare `applies_to_work_profile` while preserving
   existing event / condition behavior. Completed as the report-only bridge that
   surfaced declarations before evaluator consumption.
4. `POLTRIG-03`: make the evaluator match policy scopes and keep exact condition
   checks as additional filters. Registered work order:
   `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLTRIG-03_policy_scope_evaluator_consumption.md`;
   current implementation consumes only `work_profile.lifecycle_event` and
   `work_profile.policy_scopes`. `intent_class`, `operation_class`, and
   `output_class` remain explanatory projection fields until a later reviewed
   slice.
5. `POLTRIG-04`: make scope-only intent-driven policies scope-first. Registered
   work order:
   `docs/work_orders/SPRINT_050_WO-PER-JIKUO-POLTRIG-04_scope_first_policy_triggering.md`;
   current implementation keeps exact event matches for legacy / checkpoint
   policies, but lets policies with `policy_scopes` and empty
   `lifecycle_events` match from `work_profile.policy_scopes` even when the
   current evaluation surface is a different JIKUO event.
6. `LIFECYCLE-01`: current priority. Define and implement the record-only
   observed lifecycle projection so that when JIKUO is pulled up, lifecycle
   nodes that actually produced cards stay visible from the latest card. This is
   about lifecycle observability; it is not a lifecycle runner and not a promise
   that GUI clients can force JIKUO invocation before hooks are proven.
7. `POLICY-MGMT-01`: keep the policy-management MVP lightweight. Current status:
   two user-authored candidates are active report-only policies; the closeout
   design now defines policy source categories, official distribution flow, and
   active-policy maintenance outcomes. No-write distribution review is available
   through CLI, agent-flow proposal, and MCP, including natural-language
   `policy_query` source resolution with ambiguity refusal. Guarded
   package-template publication and starter-pack manifest publication are
   available through CLI, agent-flow, and MCP plan/apply surfaces without
   building a heavy candidate-disposition registry before lifecycle facts are
   explicit. A no-write policy-management status read model is also available
   through `python -B -m jikuo policy-management status` and
   `jikuo.get_policy_management_status` for future GUI/global configuration
   surfaces.
8. `POLTRIG-05`: update MCP and host adapter surfaces to require or strongly
   encourage agent hints.
9. `POLTRIG-06`: surface hint/signal/fallback basis in runtime cards and
   structured execution events.
10. `POLCAT-01`: keep self-bootstrap policy promotion hard-gated so official
   starter packs are selected, reviewed, and opt-in. This is a distribution
   boundary dependency of `POLICY-MGMT-01`, not a substitute for candidate
   promotion and held-candidate cleanup.

`DOCREG-01B3` is deferred. Do not add a duplicate completion-review registry
policy while `POLICY-jikuo-main-doc-mount-maintenance` covers the current
main-document completion check, unless a separate registry-specific checker,
evidence type, and user-visible need are approved.

---

## 12. Candidate Policies Activated From Held Set

The previous held candidates are now active report-only policy-store entries:

- `POLICY-jikuo-first-principles-critical-alignment`
- `POLICY-jikuo-data-model-drift-alarm`

See
`docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md`
section "Held Policy-Governance Candidates" for the current candidate text.

Current status:

- both candidates are active as `active_report_only`;
- both are scoped to `POLICY-MGMT-01` as the first manual activation set;
- first-principles uses `conversation_turn` plus scope-only `discussion`;
- data-model drift uses `conversation_turn` plus scope-only `editing`;
- future outcomes are: keep, narrow, merge, supersede, or deprecate through
  guarded policy evolution;
- no heavier candidate registry should be introduced before `LIFECYCLE-01`
  clarifies lifecycle facts.

This authority document keeps the principle: concept alignment and root-cause
reasoning precede implementation detail acceptance, and data-model drift must
be treated as an architecture warning before adding more fields or layers.

---

## 13. Review Rule

Before implementing or activating a policy-governance change, check this document
and report whether the change affects:

- lifecycle state;
- policy source or distribution boundary;
- trigger event;
- policy scope class;
- AI hint handling;
- deterministic hard-signal handling;
- fallback expansion;
- policy evidence;
- runtime visibility.

If the change affects any of those, update this document or state why it remains
unchanged before closing the slice.
