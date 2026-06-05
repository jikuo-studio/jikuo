# JIKUO CLI Enhanced Execution Envelope

This note defines the shared GUI/CLI execution-envelope slice introduced for
the CLI enhanced governance shell. It is a schema and linkage layer, not a new
policy path and not an AI classifier.

## Boundary

- `turn_anchor` remains the stable turn identity object.
- Host AI supplies `host_semantic_intent` as compact semantic evidence.
- JIKUO records, normalizes, links, evaluates policy triggers, and displays
  evidence.
- JIKUO does not infer semantic intent and does not perform semantic search by
  itself.

## Execution Envelope

Schema: `jikuo.execution_envelope.v0`

The envelope wraps existing shared fields:

- `envelope_id`
- `project_root`
- `session_id`
- `turn_id`
- `turn_anchor`
- `prompt_digest`
- `host_semantic_intent`
- `lifecycle`
- `links`
- `git_observation`
- `privacy`

Lifecycle state is derived from explicit runner events:

- `conversation_turn` -> `routed`
- `task_start` -> `task_started`
- `task_continue` / `evidence_review` -> `executing`
- `verification_review` / `pre_delivery` -> `verified`
- `completion_review` -> `completion_reviewed`
- `handoff` -> `receipt_ready`

The envelope is projected into proposal JSON, runtime markdown, and
`state_summary.json`. Runtime projection only adds refs such as latest card,
history card, and state summary paths.

## Private Turn Input Index

Schema: `jikuo.private_turn_input_index.v0`

The private index lives at:

```text
.jikuo/private/turn_inputs.jsonl
```

The directory writes a local `.gitignore` that ignores private contents.

Records may store raw user input only when an explicit private-index write is
confirmed. Public evidence uses `jikuo.private_turn_input_index_ref.v0`, which
contains refs, hashes, turn anchor identity, and evidence links without raw
input text.

Default CLI search mode is `literal_private_index`. It reads the private index
locally and returns public refs only. Semantic retrieval can be implemented by
a host AI or host-side search provider over the private store, then handed back
to JIKUO as linked evidence refs.

## Privacy Rules

- Raw prompt is never written to runtime cards or `state_summary.json`.
- Raw prompt is never included in `host_semantic_intent`.
- Raw prompt storage, when enabled, is local/private and explicitly marked.
- Public cards may display `prompt_sha256`, `turn_anchor`, `envelope_id`, and
  private index refs.
