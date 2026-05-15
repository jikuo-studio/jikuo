# INSIGHT-2026-05-15: Policy Evidence Prefix Footgun In Task-session Snapshots

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: `JIKUO-MCP-01` Stage A server wrapper implementation
- Not promoted to current task map in this slice

## Observation

During MCP Stage A server-wrapper completion review, a task-session snapshot was recorded with:

```yaml
evidence_kind: "main_document_mount_maintenance_evidence"
```

That looked correct to a human, but the policy evidence matcher did not accept it. The matcher ingests task-session evidence only when the kind uses the explicit policy-evidence prefix:

```yaml
evidence_kind: "policy_evidence:main_document_mount_maintenance_evidence"
```

After appending the prefixed evidence item, the same completion-review policy reported zero missing evidence.

## Product Meaning

This is a harness usability footgun. Users and agents can think they recorded the required evidence while the deterministic policy matcher correctly treats it as ordinary process evidence.

## Possible Future Work

- Add a clearer `task_session update` mode or flag for policy evidence snapshots.
- Warn when `evidence_kind` equals a known policy evidence requirement without the `policy_evidence:` prefix.
- Consider rendering this distinction in task-session cards so ordinary users can see whether evidence is human-only or policy-matchable.

## Boundary

This insight does not change the current MCP Stage A server-wrapper scope. It is captured as a future task candidate for task-session / policy-evidence ergonomics.
