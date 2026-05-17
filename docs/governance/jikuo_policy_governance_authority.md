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
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-20_policy_dead_zone_detection.md`: policy dead-zone visibility work.

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

Current code still exposes several tool-specific events such as
`configuration_review`, `policy_evolution_plan`, `policy_template_import_plan`,
and `evidence_review`. Those names are implementation surfaces, not a reason to
expand the core user-work lifecycle. Future projection work should preserve
existing tool compatibility while adding a `work_profile.lifecycle_event` that
uses the three user-work lifecycle values above.

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
    "intent_class": ["discussion"],
    "operation_class": ["no_tool"],
    "output_class": ["answer"],
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
applies_to_task_classes:
  - editing
```

or:

```yaml
applies_to_task_classes:
  - discussion
  - progress_summary
```

The evaluator can then match policies against `policy_scopes` generated by the
router instead of depending only on brittle exact `task_type` or `jikuo_layer`
values.

Practical rule:

```text
implemented event routes the current tool path;
work_profile.lifecycle_event says where this sits in the user-work lifecycle;
work_profile.policy_scopes says which policy groups should be considered;
conditions and evidence decide whether a specific policy is satisfied.
```

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

| Source | Intended use |
|---|---|
| JIKUO self-bootstrap policy store | Governs JIKUO's own development only. |
| Official starter packs / catalog | Reviewed reusable policy templates that users may opt into. |
| Project-local `.jikuo/policies/approved` | User-owned active project policy store. |
| Imported templates | Resolved into project-local policy proposals before activation. |
| Insights | Ideas or candidates, not active policies. |

Official updates may offer new starter packs or template revisions, but must not
overwrite user-approved local policies. Catalog sync must remain opt-in and
reviewable.

---

## 10. Current Implementation Gap

Current JIKUO has:

- exact lifecycle event matching;
- report-only condition evaluation;
- policy runtime status cards;
- conversation-turn router follow-up obligations;
- proactive policy-suggestion review evidence;
- policy dead-zone per-card classification;
- no-write `work_profile` projection on proposal and MCP responses;
- lightweight `task_start` processing projection that is separate from guarded
  `task_session_start` creation;
- policy `applies_to_work_profile` declarations surfaced in policy-store status,
  trigger reports, and runtime cards as report-only metadata;
- MCP surfaces for route, status, proposals, and guarded writes.

Current JIKUO does not yet have:

- structured `agent_hint` input on every router path;
- the `discussion` / `editing` / `progress_summary` / `other` policy-scope layer
  as evaluator input;
- evaluator support for scope-based triggering;
- runtime cards that show hint/signal/fallback routing;
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
   existing event / condition behavior. Current implementation status:
   policy-store status, trigger evaluation, and runtime policy cards surface
   `applies_to_work_profile` as `declared_report_only`; the evaluator does not
   consume it, and mismatched declarations do not change trigger results.
4. `POLTRIG-03`: make the evaluator match policy scopes and keep exact condition
   checks as additional filters.
5. `POLTRIG-04`: update MCP and host adapter surfaces to require or strongly
   encourage agent hints.
6. `POLTRIG-05`: surface hint/signal/fallback basis in runtime cards and
   structured execution events.
7. `POLCAT-01`: keep self-bootstrap policy promotion hard-gated so official
   starter packs are selected, reviewed, and opt-in.

`DOCREG-01B3` may still proceed as a domain-specific completion-review policy,
but it should be treated as a consumer of this policy-governance model, not as
the model itself.

---

## 12. Candidate Policies Held For Later Activation

The current held candidates are maintained in the transitional task-sequencing
authority, not as active policy-store entries:

- `POLICY-CANDIDATE-first-principles-critical-alignment`
- `POLICY-CANDIDATE-data-model-drift-alarm`

See
`docs/work_orders/SPRINT_050_WO-PER-JIKUO-DOCREG-01_layered_document_registry.md`
section "Held Policy-Governance Candidates" for the current candidate text.

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
