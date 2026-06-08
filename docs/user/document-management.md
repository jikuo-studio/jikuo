# JIKUO Document Management

> **Status**: First-use user guide for the pre-release usability path.
> **Audience**: Users configuring a JIKUO project for the first time.
> **Boundary**: This guide explains project document configuration. It does not
> replace policy management, trace inspection, or release limitation docs.

## 1. What Document Rules Control

Document Rules define which project files JIKUO should treat as relevant
project context, completion-check material, and governance references.

They are not runtime evidence by themselves. A configured document says what
should be mounted or checked; a runtime card or receipt says what was actually
observed during a governed round.

## 2. Default Configuration Model

The default editable configuration lives in:

- `.jikuo/project_context.yaml`

That file stores:

- `document_roles`: named project documents that can be used as context;
- `main_document_mounts.checked_before_slice_completion`: documents that should
  be reviewed before claiming a governed slice is complete;
- `main_document_mounts.active_mount_authority`: files that explain or anchor
  the active document-mount model;
- `directory_roles`: important project directories.

Studio and CLI Document Rules changes should target `.jikuo/project_context.yaml`
through a reviewed plan and guarded apply. Package defaults, registry shards,
governance guidance, and runtime history are read-model inputs or references;
they are not the normal user write target for Document Rules.

## 3. Local Mount Layering

JIKUO separates document sources by role:

- Editable project configuration: `.jikuo/project_context.yaml`.
- Registry metadata: `docs/registry/mount_sets.yaml` and related registry
  shards.
- Governance guidance: human-readable docs such as
  `docs/governance/jikuo_execution_mounts.md`.
- Runtime observations: `.jikuo/runtime/last_card.md` and history snapshots.
- User project documents: project-relative files that the user adds to Document
  Rules.

Only project-relative paths inside the project root should be configured. Local
absolute paths from a maintainer machine should not become release defaults.

<a id="first-run.project-context"></a>

## 4. First-Run Checklist

For a new project:

1. Open Studio or run `jikuo studio status --format markdown`.
2. Check the Document Configuration section.
3. Confirm the editable target is `.jikuo/project_context.yaml`.
4. Add project documents through `Preview plan`.
5. Review the proposed write boundary and expected target file.
6. Apply only after confirming the guarded Document Rules change.
7. Run a governed workflow and inspect Document Trace to see observed evidence.

## 5. Common Changes

Add a context document when the file should help the AI understand the project
before or during work.

Add a completion check when the file should be reviewed before final delivery
or completion review.

Add a governance reference when the file explains boundaries, responsibilities,
or rules that shape future work.

Remove a document only after checking whether the file is still used by
completion checks, active mount authority, or project-specific governance.

## 6. Guarded Change Boundary

Document Rules changes use:

- no-write preview: `jikuo studio document-rules plan`;
- guarded apply: `jikuo studio document-rules apply`;
- Studio API preview: `/api/document-rules/plan`;
- Studio API apply: `/api/document-rules/apply`.

A valid apply updates `.jikuo/project_context.yaml` only. It does not edit
package templates, policy files, registry shards, runtime cards, or external
local documents.

## 7. Current Limitations

Document Rules can show what should be mounted or checked, but current runtime
history is not yet a full structured event ledger.

Some missing evidence can mean "not observed by this version" rather than "the
work failed." Missing evidence classification is tracked as a separate
pre-release task.
