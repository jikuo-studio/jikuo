# JIKUO Document Evidence Chain Design

> **Status**: Draft design linked to
> `INSIGHT-2026-06-03-runtime-history-card-itemized-document-evidence-gap`.
> **Date**: 2026-06-03
> **Purpose**: define a concrete backend and Studio frontend direction for
> auditable AI document consumption and editing evidence.
> **Boundary**: This design does not claim to prove model understanding. It
> defines observable evidence records and reconciliation views only.

---

## 1. Problem

JIKUO can configure documents that an AI should consider, and Studio can now
show round-level document trace counts. The current evidence model is still too
weak for reliable audit.

Two gaps are linked:

1. A runtime history card may preserve counts such as planned writes, actual
   writes, required reads, completion-check candidates, and gap counts, while
   omitting path-level item evidence. For newer receipts, the write-side counts
   must be separated into required companion writes, declared writes, and actual
   writes so the user can see which governance files were required and which
   files actually changed.
2. Even when a document is mounted or read by a tool, JIKUO cannot prove the AI
   cognitively understood or used it.

The design target is therefore an evidence chain, not a mental-state proof:

```text
expected documents
  -> observed reads
  -> cited or decision-bound refs
  -> required companion writes
  -> declared writes
  -> actual writes
  -> reconciliation gaps
  -> completion evidence
```

## 2. Product Principle

JIKUO should say what is knowable.

Do not display:

- "AI understood this document";
- "AI read this document" when only configuration required it;
- "No changes happened" when only itemized evidence is missing;
- per-round document paths inferred from current git diff alone.

Display instead:

- configured document obligations;
- observed tool or mounted-context reads;
- model-declared citations and decision bindings;
- required companion writes projected from governance rules;
- declared writes from the host AI or guarded plans;
- actual writes;
- gaps between those sets;
- explicit evidence limits.

## 3. Backend Contract

Add a structured runtime sidecar for each card-producing round:

```text
.jikuo/runtime/evidence/<round_id>.document_evidence_chain.json
```

Draft schema:

```yaml
schema: "jikuo.document_evidence_chain.v0"
round_id: "<runtime round id>"
lifecycle_event: "conversation_turn | task_start | completion_review | ..."
proposal_id: "<proposal id when available>"
source_card_ref: ".jikuo/runtime/history/<round>.md"
generated_at_utc: "<timestamp>"
status: "not_evaluated | partial | review | ok"
guarantee: "observable_evidence_only"

expected_read_set: []
observed_read_set: []
cited_read_refs: []
decision_bound_refs: []
required_companion_write_set: []
declared_write_set: []
actual_write_set: []
reconciliation: {}
evidence_strength_summary: {}
limits: []
non_effects: []
```

### 3.1 Document Reference Shape

Use one compact shape for document refs across sets:

```yaml
path: "docs/example.md"
path_ref: "docs/example.md#section-optional"
document_role: "project_context | work_order | policy | ..."
source_kind: "document_rules | work_order | policy | registry_rule | user_instruction | tool_observation | agent_declaration | guarded_apply | git_diff"
source_ref: "<config path, card ref, tool call id, policy id, or task ref>"
reason: "Why this document matters for this round."
```

### 3.2 Observed Read Evidence

`observed_read_set` records observable access, not understanding:

```yaml
- path: "docs/work_orders/example.md"
  evidence_kind: "observed_read"
  evidence_status: "observed"
  producer: "read_wrapper | mcp_tool | studio_backend | host_adapter"
  read_at_utc: "<timestamp>"
  content_hash: "sha256:..."
  range:
    mode: "full_file | line_range | byte_range | unknown"
    start_line: 1
    end_line: 120
  reason: "Mounted work order for this slice."
```

If a client cannot instrument reads, it may provide `declared` evidence, but
that status must remain weaker than `observed_read`.

### 3.3 Citation And Decision Binding

`cited_read_refs` records visible model output references:

```yaml
- path_ref: "docs/governance/example.md#4-boundary"
  evidence_kind: "cited"
  source_ref: ".jikuo/runtime/history/<round>.md"
  summary: "The final answer cited the boundary section."
```

`decision_bound_refs` records explicit links between a document and a plan,
refusal, design choice, or write decision:

```yaml
- decision_id: "DEC-001"
  decision_type: "plan | refusal | design_choice | write_decision"
  path_ref: "docs/work_orders/example.md#acceptance"
  summary: "Acceptance criteria required a no-write first slice."
```

This is still a declaration unless backed by observed reads or citations.

### 3.4 Required Companion Write Obligations

`required_companion_write_set` is the primary write-side governance set. It is
not the AI's free-form plan. It records files that JIKUO expects to be updated
because a class of work happened and a mounted policy, work order, registry, or
document rule says a companion update is required.

Examples:

- a new feature or code path requires user action-chain and atomic capability
  registration updates;
- a new document requires the corresponding document registry or mount guidance
  to include it;
- work order progress requires the active work order and relevant registry
  projection to be updated;
- policy, evaluator, or document-registry changes require the matching registry,
  tests, and governance guidance to stay in sync.

The projector should resolve concrete paths from mounted configuration,
registries, work orders, or active policies. A policy may say "register the
corresponding document" or "update the corresponding atom registry" without
hard-coding a universal path; the receipt still has to show the resolved path
when a comparable path is available.

```yaml
- id: "RCW-001"
  path: "docs/registry/capabilities.yaml"
  operation: "modify"
  evidence_kind: "required_companion_write"
  source_kind: "policy | work_order | registry_rule | document_rule | user_instruction"
  source_ref: "POLICY-jikuo-atom-registration-after-feature-change"
  trigger:
    type: "feature_or_code_change | new_document | work_order_progress | policy_change | registry_change"
    source_ref: "<observed write path, work-order slice, policy id, or decision id>"
  reason: "A new atomic capability must be registered after the feature slice."
```

### 3.5 Declared Planned Write Evidence

`declared_write_set` records what the host AI or a guarded plan says it expects
to write. This is useful evidence, but it is weaker than required companion
write obligations because it is agent-declared.

```yaml
- path: "src/jikuo/example.py"
  operation: "add | modify | delete | migrate | check_only"
  evidence_kind: "declared_write"
  source_kind: "agent_plan | no_write_plan | guarded_apply_plan"
  reason: "Implement document evidence chain builder."
  bound_read_refs:
    - "docs/governance/jikuo_document_evidence_chain_design.md"
  approval_boundary: "none | guarded_apply | user_confirmation"
```

For backward compatibility, existing `planned_write_set` values may be displayed
as declared writes until the runtime schema is migrated.

### 3.6 Actual Write Evidence

After a file change, the runtime sidecar should preserve itemized actual write
evidence:

```yaml
- path: "src/jikuo/example.py"
  operation: "add | modify | delete"
  evidence_kind: "actual_write"
  source_kind: "apply_patch | guarded_apply | formatter | user_supplied | git_diff"
  before_hash: "sha256:..."
  after_hash: "sha256:..."
  diff_ref: ".jikuo/runtime/evidence/<round>.diff"
  bound_required_companion_write_id: "RCW-001"
  bound_declared_write_id: "DW-001"
  attribution_status: "round_attributed | mixed_or_uncertain | user_supplied"
```

Git diff can support attribution, but it must not be the only source when
multiple rounds or user edits may be interleaved.

## 4. Evidence Strength

Expose evidence strength as first-class data:

| Strength | Meaning |
|---|---|
| `configured` | Required by Document Rules, work order, policy, or user instruction. |
| `declared` | The AI or host agent claimed the document was read or used. |
| `observed_read` | A tool or mounted-context path accessed the document. |
| `cited` | Output visibly referenced the document or section. |
| `decision_bound` | A plan, decision, refusal, or write decision links to the document. |
| `write_bound` | A required companion, declared, or actual write links to document evidence. |
| `verified` | Review or tests found no contradiction with the referenced constraints. |

The summary should report the strongest evidence per document without hiding
weaker or missing links.

## 5. Reconciliation

The reconciliation block compares sets and emits explicit gaps:

```yaml
reconciliation:
  status: "review"
  gaps:
    - gap_type: "expected_read_without_observed_read"
      path: "docs/example.md"
      severity: "review"
      summary: "Configured as required, but no observed read evidence exists."
    - gap_type: "observed_read_without_citation_or_decision"
      path: "docs/example.md"
      severity: "info"
      summary: "Read was observed, but no output citation or decision binding exists."
    - gap_type: "declared_write_without_actual_write"
      path: "src/example.py"
      severity: "review"
    - gap_type: "actual_write_without_declaration"
      path: "src/example.py"
      severity: "review"
    - gap_type: "required_companion_write_without_actual_write"
      path: "docs/registry/capabilities.yaml"
      severity: "review"
      summary: "Governance rules required this companion update, but no actual write evidence exists."
    - gap_type: "actual_write_without_required_companion_obligation"
      path: "src/example.py"
      severity: "info"
      summary: "The file changed, but it is not itself a required companion governance write."
    - gap_type: "governance_write_obligation_not_projected"
      source_ref: "<trigger source>"
      severity: "review"
      summary: "A trigger signal existed, but no concrete required companion write was projected."
    - gap_type: "write_without_read_or_decision_basis"
      path: "src/example.py"
      severity: "review"
    - gap_type: "count_only_history_card"
      source_ref: ".jikuo/runtime/history/<round>.md"
      severity: "info"
```

## 6. Runtime Producer Plan

Implement in slices.

1. `document_evidence_chain.py`
   - Build the schema object from configured obligations, caller-supplied
     evidence, and existing artifact assurance fields.
   - No writes by itself.
2. `agent_flow.py`
   - Accept compact read/write evidence inputs.
   - Emit chain summary in Markdown cards.
   - Write sidecar through the existing runtime visibility channel when card
     history is already written.
3. `runtime_visibility.py`
   - Link latest sidecar refs into `state_summary.json`.
   - Preserve history card as display surface, not data source.
4. `global_status.py`
   - Expose `summaries.runtime.document_evidence_chains`.
   - Preserve fallback for older rounds that have count-only cards.
5. Completion review
   - Use reconciliation gaps as completion evidence inputs.
   - Never mark missing read proof as proof of failure; mark it as missing
     observable evidence.

## 7. Studio Frontend Design

Rename or extend the current `Round Document Trace` section into
`Document Evidence Chain`.

Keep round selection at the top. The default remains latest round. Selecting a
round must bind all detail panels to the same `round_id`.

### 7.1 Summary Strip

Cards:

- round;
- evidence status;
- strongest read evidence;
- required companion / declared / actual writes;
- reconciliation gaps;
- limits.

Avoid terms such as "understood". Use "observable evidence" language.

### 7.2 Obligations Panel

Shows:

- expected reads;
- completion-check candidates;
- governance refs;
- source of each obligation.

Badges:

- `configured`;
- `policy`;
- `work order`;
- `user instruction`.

### 7.3 Read Evidence Panel

Rows group by document path.

Columns:

- expected;
- observed read;
- cited;
- decision-bound;
- strongest evidence;
- source ref.

Empty-state examples:

- "Configured, no observed read evidence."
- "Observed read, no citation or decision binding."
- "Declared only; no tool-level evidence."

### 7.4 Write Evidence Panel

Rows group by path.

Columns:

- required companion operation;
- declared operation;
- actual operation;
- before/after hash status;
- bound read refs;
- attribution status.

Empty-state examples:

- "2 declared writes counted; item paths unavailable in this history card."
- "No required companion writes were projected for this round."
- "Actual write observed without a required companion obligation."
- "Required companion write was not observed."

### 7.5 Reconciliation Panel

Shows gap rows by type, severity, and source. This panel should be the user's
main "what needs attention" surface.

Primary gap types:

- missing observed read;
- read not cited or decision-bound;
- required companion write missing actual write;
- declared write missing actual write;
- actual write missing declaration;
- actual write outside required companion set;
- governance write obligation not projected;
- write missing read/decision basis;
- count-only evidence;
- no comparable runtime evidence.

### 7.6 Limits Panel

Always shows the epistemic boundary:

- no proof of model understanding;
- observable evidence only;
- count-only card if applicable;
- git diff is not round attribution by itself;
- raw prompt/transcript is not required for this evidence chain.

## 8. Data Compatibility

Older runtime history cards do not have sidecars. For those rounds:

- Studio should continue to show count-only evidence;
- path-level panels should say item paths are unavailable;
- reconciliation should include `count_only_history_card`;
- no backend should synthesize path-level evidence from counts.

## 9. Privacy And Storage

The sidecar should not store raw prompts or raw chat transcripts.

It may store:

- path refs;
- section refs;
- hashes;
- evidence summaries;
- compact decision summaries;
- source refs to existing cards or tools.

If content excerpts are needed later, they should be explicit, bounded, and
classified separately.

## 10. Open Decisions

- Should observed read evidence be collected only through explicit JIKUO read
  wrappers, or can host adapter read telemetry be accepted?
- How should sidecars represent multi-agent or user-edited mixed attribution?
- Should DATA-01 become the canonical event ledger for these records, or should
  the sidecar remain the first product slice?
- Which completion-review policies should treat missing observable reads as
  review-required evidence gaps?
- How much detail should Studio show by default before overwhelming users?

## 11. Initial Implementation Slices

- `STUDIO-01D16`: document evidence chain schema and no-write builder.
- `STUDIO-01D17`: runtime sidecar persistence through existing visibility
  channel.
- `STUDIO-01D18`: global status projection for recent evidence chains.
- `STUDIO-01D19`: Studio `Document Evidence Chain` frontend section.
- `STUDIO-01D20`: completion-review reconciliation evidence integration.
- Later DATA-01 slice: migrate or mirror sidecar records into a durable event
  ledger if accepted.

## 12. Related Records

- Insight:
  `docs/insights/INSIGHT-2026-06-03-runtime-history-card-itemized-document-evidence-gap.md`
- Studio work order:
  `docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-01_global_console_and_configuration_shell.md`
- DATA-01 planning:
  `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DATA-01_structured_execution_event_ledger_and_analytics_contract.md`
