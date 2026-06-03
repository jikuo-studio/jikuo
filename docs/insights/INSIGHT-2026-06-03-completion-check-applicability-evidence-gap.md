# INSIGHT-2026-06-03: Completion-Check Applicability Evidence Gap

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: Studio Round Document Trace wording review
- Not promoted to a work order in this slice
- Related insight:
  `docs/insights/INSIGHT-2026-06-03-runtime-history-card-itemized-document-evidence-gap.md`

## Observation

Studio Round Document Trace currently receives completion-check candidates from
`.jikuo/project_context.yaml` `main_document_mounts.checked_before_slice_completion`.
These records are intentionally conservative: each configured document is a
candidate that should be considered before slice completion, but the runtime
projection does not yet preserve a per-document decision saying whether that
candidate was applicable to the specific round.

Because no per-document applicability evidence is available, the projector marks
completion-check candidates as `not_evaluated`. This is honest, but the Studio
summary previously allowed those unevaluated candidates to look like ordinary
reconciliation gaps when they were added into the visible `Gaps` total.

The correct semantic distinction is:

- a `gap` is an observed reconciliation problem, such as a required companion
  write that was not observed;
- an `unchecked applicability` item is a configured completion-check candidate
  that still needs a round-specific applicability decision;
- an unchecked item is not itself evidence that a document was wrongly skipped.

## Product Meaning

Users need to understand whether JIKUO found a real evidence mismatch or merely
does not yet know whether a configured completion-check candidate applied to the
selected round. Mixing these concepts makes the receipt feel more alarming than
the evidence supports.

For example, a round may have:

- `Gaps: 0 items`;
- `Unchecked applicability: 11 items`.

That means no concrete reconciliation gaps were reported, while 11 configured
completion-check candidates still lack itemized applicability decisions.

## Desired Future Behavior

Future completion review should be able to attach a per-document applicability
record to each completion-check candidate, with at least:

- document path or document registry ref;
- source rule that made it a completion-check candidate;
- applicability status: `applicable`, `not_applicable`, `satisfied`, or
  `unknown`;
- reason for the decision;
- evidence producer, such as host AI declaration, guarded apply, git observation,
  work-order rule, policy rule, or reviewer annotation;
- optional trigger source linking code, policy, registry, document, or work-order
  changes to the document that should be checked;
- observed write operation when applicable.

Studio should then show completion-check status separately from reconciliation
gaps:

- configured candidates;
- unchecked applicability;
- applicable and satisfied;
- applicable but missing required evidence;
- not applicable with reason.

## Candidate Follow-Up

Design a small structured evidence shape for completion-check applicability and
wire it into the completion-review runtime projection without changing the
artifact assurance engine's pure reconciliation boundary.

Candidate source areas:

- `src/jikuo/studio/artifact_assurance.py`;
- `src/jikuo/agent_flow.py`;
- `src/jikuo/runtime_visibility.py`;
- `src/jikuo/studio/global_status.py`;
- `src/jikuo/integrations/studio_web/server.py`;
- `docs/governance/jikuo_document_evidence_chain_design.md`;
- `.jikuo/project_context.yaml`.

## Boundary

Do not treat an unevaluated completion-check candidate as a concrete gap. Do
not infer applicability from aggregate counts. Until itemized applicability
evidence exists, Studio should say the candidate is unchecked rather than
claiming it is satisfied or violated.
