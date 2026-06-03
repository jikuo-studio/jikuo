# INSIGHT-2026-06-03: AI Document Consumption And Editing Evidence Chain Gap

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: Studio Round Document Trace consistency review and document-consumption assurance discussion
- Not promoted to a work order in this slice
- Related design draft:
  `docs/governance/jikuo_document_evidence_chain_design.md`

## Observation

Studio can now keep the selected round card and the detail panels bound to the
same runtime round. That exposed a deeper runtime evidence gap:

- history cards may preserve aggregate counts such as planned writes, actual
  writes, required reads, completion-check candidates, and gap counts;
- the same history cards may not preserve itemized document-path evidence for
  those counts;
- therefore Studio can honestly show that items were counted while also saying
  the detailed item paths are unavailable in the history card.
- the write-side product value is sharper than generic planned-vs-actual
  comparison: when code, document, policy, registry, or work-order changes
  happen, JIKUO should show which companion governance files were required by
  policy/work-order/registry rules and whether those exact files were actually
  updated.

This is not proof that no documents were written. It means the runtime/history
card evidence did not retain enough path-level detail for Studio to reconstruct
which documents were planned, changed, added, deleted, or observed for that
specific round.

The related read-side problem is even more fundamental: JIKUO cannot prove an
AI cognitively consumed or understood a document. It can only collect observable
evidence that the document was required, fetched through a tool or mounted
context, cited or used in a declared decision, and not contradicted by the final
result. A trustworthy design must therefore treat "AI read the document" as an
evidence chain, not as a mental-state proof.

The combined gap is:

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

Today, parts of that chain are represented as counts, runtime card text, or
agent declarations, but not yet as a durable per-round structured evidence
record with path-level read/write attribution.

## Product Meaning

Users reasonably expect a round trace to answer:

- which documents were expected to be read;
- which documents were actually accessed through observable tooling;
- which documents the AI claims influenced a decision;
- which companion governance documents were required for write;
- which documents the AI or guarded plan declared for write;
- which documents were actually written;
- whether each write was an addition, modification, or deletion;
- which evidence source produced the claim.

Aggregate counts alone are useful for high-level status, but they are not
enough for a trustworthy document trace. If Studio filled the missing detail
from current git diff or local filesystem inspection, it could create false
round attribution when multiple rounds, user edits, or uncommitted changes are
interleaved.

Likewise, if JIKUO presents a required document as "read" without separating
configuration, tool access, citation, decision binding, and result alignment,
it can overstate what is actually knowable about AI behavior.

## Desired Future Behavior

Future runtime evidence should preserve per-round itemized document evidence
alongside aggregate counts and should distinguish evidence strength.

At minimum, each relevant round should be able to expose:

- `expected_read_set` with source refs from Document Rules, work orders,
  policies, and explicit user instructions;
- `required_read_set` with document refs or paths;
- `observed_read_set` with path, file hash, read time, line or byte range, and
  read reason when the read passed through observable tooling;
- `cited_read_refs` for documents named or cited in the model output;
- `decision_bound_refs` for documents explicitly linked to a plan, refusal,
  design choice, or write decision;
- `required_companion_write_set` with path, intended operation, source rule,
  trigger source, and reason;
- `declared_write_set` with path, intended operation, and source;
- `actual_write_set` with path, observed operation, and source;
- write operation type such as added, modified, deleted, or unchanged;
- before/after hashes or patch refs when available;
- evidence kind, evidence status, and producer;
- whether the evidence came from agent declaration, guarded apply, runtime
  projection, git diff, or another explicit source.

History-card Markdown can remain a human display surface, but Studio should
have a structured runtime source or sidecar record for path-level trace details.

Evidence strength should be explicit, for example:

- `configured`: the document was required by configuration or policy;
- `declared`: the AI claimed it read or used the document;
- `observed_read`: a tool or mounted-context path accessed the document;
- `cited`: the model output referenced the document or a specific section;
- `decision_bound`: a plan or decision explicitly depends on the document;
- `write_bound`: a required companion, declared, or actual write is linked to
  document evidence;
- `verified`: review or tests found no contradiction with the referenced
  document constraints.

No label should imply proof of internal model understanding.

Completion review should reconcile:

- expected reads vs observed reads;
- observed reads vs cited or decision-bound refs;
- required companion writes vs actual writes;
- declared writes vs actual writes;
- actual writes without a declaration;
- required companion writes that did not happen;
- trigger signals that did not project a concrete companion-write obligation;
- writes without an observable read/citation/decision basis;
- final results that contradict required context.

## Candidate Follow-Up

Investigate a future slice that extends runtime artifact assurance so
`agent_flow` and completion review can persist a round-level evidence chain for
AI document consumption and editing. The near-term MVP path should project
`required_companion_write_set`, `declared_write_set`, and `actual_write_set`
without requiring DATA-01 event-ledger persistence.

Initial design draft:

- `docs/governance/jikuo_document_evidence_chain_design.md`

Candidate source areas:

- `src/jikuo/agent_flow.py`;
- `src/jikuo/runtime_visibility.py`;
- `src/jikuo/studio/artifact_assurance.py`;
- `src/jikuo/studio/global_status.py`;
- `src/jikuo/integrations/studio_web/server.py`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-01_global_console_and_configuration_shell.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DATA-01_structured_execution_event_ledger_and_analytics_contract.md`.

## Boundary

Do not treat current git diff as equivalent to per-round document evidence.
Do not make Studio infer missing document paths from aggregate counts. Studio
should continue to expose count-only history cards honestly until runtime
evidence preserves path-level detail.

Do not claim that JIKUO can prove AI understanding or cognitive consumption of
context. The goal is a transparent, auditable, falsifiable evidence chain over
observable document obligations, accesses, citations, decisions, writes, and
reconciliation gaps.
