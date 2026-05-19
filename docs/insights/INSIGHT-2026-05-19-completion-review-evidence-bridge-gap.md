# INSIGHT-2026-05-19: Completion Review Evidence Bridge Gap

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: `LIFECYCLE-01` planning and Codex hook proof preparation
- Not promoted to implementation in this slice

## Observation

During a documentation-planning slice, `completion_review` correctly triggered
`POLICY-jikuo-main-doc-mount-maintenance`. The affected main documents and
registries had already been updated and committed, but the runtime card still
reported missing `main_document_mount_maintenance_evidence`.

The human workflow was correct. The structured policy evidence path was not.
JIKUO had no automatic bridge from "the maintainer checked and updated the main
document mount" to "append or project matcher-readable
`main_document_mount_maintenance_evidence` for the completion policy."

## Product Meaning

This is a lifecycle/evidence orchestration gap. A policy can fire at the right
completion node and the work can be genuinely done, while the visible card still
reports missing evidence because the evidence append path is not integrated into
the lifecycle runner.

That creates noise for the user and weakens trust in completion-review cards:
the card is technically honest about missing structured evidence, but it cannot
distinguish "the user forgot the check" from "the check happened, but JIKUO did
not record it in the policy-evidence surface."

## Desired Future Behavior

Future lifecycle work should make the distinction explicit:

- completion-review policy trigger status remains separate from task-session
  lifecycle status;
- main-document maintenance evidence is recorded as a structured evidence item
  when the main-document check is performed;
- the evidence item references the checked documents or a compact summary of why
  no document update was needed;
- the card reports whether evidence was produced automatically by the lifecycle
  runner, supplied manually, or deferred as missing;
- no durable task session is required merely to make completion-review evidence
  visible.

## Boundary

Do not fix this by requiring every slice to create a durable task session. Do
not infer evidence from a commit alone. The evidence bridge should be designed
inside `LIFECYCLE-01` after the invoked-turn lifecycle model is reviewed.

This insight records the bug and follow-up need only.
