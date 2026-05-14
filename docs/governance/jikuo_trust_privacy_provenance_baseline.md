# JIKUO Trust Privacy Provenance Baseline

> **Date**: 2026-05-13
> **Status**: Draft trust / privacy / provenance contract / no runtime implementation
> **Purpose**: define the minimum trust, privacy, provenance, namespace, principal, telemetry, and timestamp fields required before reusable templates or MCP tools cross project / user boundaries.
> **Primary user surface**: Codex / Claude desktop APP chat.
> **JIKUO layer**: trust_foundation / portability_foundation
> **Depends on**: `JIKUO-PKG-00`; `JIKUO-CORE-20`

---

## 1. Product Meaning

Cross-project portability is not only a path-resolution problem.

When JIKUO policy templates and MCP tools become reusable across machines, users, and projects, they become a trust surface.

This contract declares the minimum fields and defaults needed before MCP implementation:

- where a template came from
- who approved an action
- what data may leave the local machine through an MCP response
- how ids avoid cross-project collisions
- whether telemetry exists and what the default is
- how events are ordered across local writes

This slice defines contracts only. It does not implement auth, signing, telemetry, file locking, template import, or MCP.

## 2. Baseline Rule

JIKUO should be safe by default.

Default posture:

- imported templates require human review before approval
- local project paths must not escape project root
- sensitive local data stays local unless explicitly classified for return
- telemetry is off by default
- every guarded write records a principal field, even if MVP principal is only `local_user`
- every durable event records UTC time and a local monotonic sequence when available

## 2A. Visibility Baseline

JIKUO visibility must not depend on any single desktop client cooperating.

Every critical JIKUO runtime state projection MUST exist on at least two independent channels:

1. Agent-displayable chat-ready output.
2. User-accessible out-of-band output, such as a local file, CLI view, or dashboard.

If only the chat channel exists, the governed flow is incomplete and should be treated as a governance failure because the user cannot independently verify whether the Agent displayed the card faithfully.

Implementation requirements:

- MCP tools that return governance cards must also make the latest card available through the out-of-band runtime visibility channel.
- Runtime state must be queryable through a local command such as `jikuo show`.
- Out-of-band snapshots must avoid raw chat transcripts, raw approval phrases, and unredacted local file content.
- Client-specific hooks, plugins, or settings are optional enhancement layers, not baseline dependencies.
- Future dashboards or notifications may build on the same local runtime projection, but they must not replace the file / CLI verification baseline.

## 2B. Integration Neutrality Baseline

JIKUO core capability must not depend on any single client, protocol, Agent SDK, IDE, or platform.

Core code owns policy, evidence, approvals, guarded apply semantics, and local runtime visibility. Integration adapters may expose those capabilities through MCP, Agent SDK plugins, IDE platforms, CLI affordances, instruction files, hooks, callbacks, or future protocols, but the adapters must not become the only place where governance semantics exist.

Implementation requirements:

- Protocol-, SDK-, client-, IDE-, and platform-specific logic belongs under `src/jikuo/integrations/`.
- Core modules under `src/jikuo/` must remain callable without importing integration packages.
- Integration adapters may depend on core APIs; core APIs must not depend on integration adapters.
- Shared display contracts may live in core only when they are protocol-neutral and can be consumed by CLI, MCP, Agent SDK, UI, or future integrations.
- MCP is the preferred cross-client tool protocol, but MCP is still an adapter layer, not the kernel.
- Hooks, guardrails, callbacks, checkpoints, traces, or platform artifacts may strengthen enforcement or review, but they do not replace JIKUO policy evidence, approval records, or `.jikuo/runtime/` visibility unless a later approved policy imports them as evidence.

## 3. Template Provenance

Reusable templates need provenance fields.

Minimal shape:

```yaml
provenance:
  schema: "jikuo.policy_provenance.v0"
  source: "local | imported | community | verified_jikuo_official | verified"
  source_ref: "..."
  starter_pack_ref: null
  imported_at_utc: null
  reviewed_by:
    principal_id: "local_user"
    principal_type: "local_user"
  review_wall_required: true
  signed_by: null
  verified_at_utc: null
```

Rules:

- `local` templates may still require review before activation
- `imported` and `community` templates must require review before approval
- `verified_jikuo_official` is reserved for package-owned starter policies and templates bundled with the installed JIKUO package; it does not imply third-party marketplace signing
- official starter policies may set `review_wall_required: false` when the starter-pack initialization itself remains guarded by explicit approval and confirmation
- `verified` remains a future third-party trust level, not implemented by this slice
- `signed_by` and `verified_at_utc` are reserved fields; this slice does not implement signing
- provenance must be visible in future template review cards
- MCP tools must not expose starter policies that are missing provenance once starter policy flows enter MCP scope

## 4. Principal And Authority

Approval records must identify who approved an action.

MVP principal:

```yaml
principal:
  principal_id: "local_user"
  principal_type: "local_user"
  display_name: null
  authority_source: "local_desktop_session"
```

Future principal types:

- `local_user`
- `team_member`
- `agent`
- `service_account`

Rules:

- `approval_phrase` is not an identity system
- MVP may set principal to `local_user`
- future team / CI / service-account flows must not rewrite old approval records to add identity semantics retroactively
- agent actions on behalf of a user should preserve both agent identity and approving principal when implemented later

## 5. Privacy Boundary

MCP tools may return data to a desktop client. That makes response shape a privacy boundary.

Every future MCP-facing result should classify fields as one of:

- `returned_to_client`
- `stays_local`
- `redacted_before_return`

Minimal shape:

```yaml
privacy:
  default_return_policy: "return_explicit_projection_only"
  returned_to_client:
    - "card_summary"
    - "policy_status"
  stays_local:
    - "raw_local_file_content"
    - "approval_phrase_raw"
  redaction:
    enabled: true
    redacted_fields:
      - "approval_phrase"
```

Rules:

- raw chat transcripts should not be returned by default
- raw approval phrases should not be returned unless explicitly needed for a local audit display
- tool results should prefer compact projections over raw local records
- future MCP implementation must define response-level privacy classification before returning project-local records

## 6. Namespace And ID Stability

Portable templates need namespaced ids.

Minimal shape:

```yaml
identity:
  namespace: "local"
  id: "POLICY-mvp-scope-control"
  fully_qualified_id: "local/POLICY-mvp-scope-control"
```

Rules:

- MVP namespace may default to `local`
- future shared templates must not rely on bare ids alone
- policy ids, template ids, capability ids, and decision ids should preserve namespace fields when crossing projects
- display labels may be short; stored refs should be unambiguous

## 7. Telemetry Boundary

MVP telemetry default:

```yaml
telemetry:
  mode: "off"
  opt_in_required: true
  collects: []
  never_collect:
    - "raw_chat"
    - "approval_phrase"
    - "local_file_content"
    - "secrets"
```

Rules:

- this slice does not implement telemetry
- no external telemetry should exist before an explicit opt-in design is approved
- future telemetry cards must show what is collected and how to disable it
- local audit logs are not telemetry unless they leave the machine

## 8. Time And Causal Order

Cross-machine clocks may drift. MVP records should still make local order explicit.

Minimal shape:

```yaml
time:
  timestamp_utc: "ISO-8601"
  timestamp_source: "local_clock"
  monotonic_seq: null
```

Rules:

- `timestamp_utc` is required for durable records
- `timestamp_source` should start as `local_clock`
- `monotonic_seq` is reserved for local strictly increasing event order
- vector clocks and distributed ordering are out of scope

## 9. Concurrency Baseline

Future MCP clients may run concurrently against the same project.

Baseline contract:

```yaml
concurrency:
  write_lock_required_for_guarded_writes: true
  lock_ref: ".jikuo/.lock"
  conflict_policy: "refuse_on_conflict"
  generation_check: "planned"
```

Rules:

- this slice does not implement locks
- future guarded writers should refuse conflicting writes rather than last-write-wins
- lock and generation checks belong to later implementation slices

## 10. Path And Binding Safety

Path safety is primarily defined by `JIKUO-CORE-20`.

SEC-01 adds the trust posture:

- imported templates must not gain trust because their paths resolve
- path resolution success is not approval
- path escape refusal should be visible in review cards
- sensitive directories outside project root must not be used as evidence sources in portable templates without a future explicit external-path capability

## 11. MCP Implications

Before MCP implementation:

- MCP tool schemas should include project root / context profile fields only where needed
- MCP responses should expose privacy-classified projections
- write-capable MCP tools should preserve principal, approval phrase boundary, and proposal-ref binding
- MCP server logs must not pollute stdout protocol traffic
- MCP implementation must not return raw sidecar records when a compact card projection is enough

## 12. Non-Goals

This contract does not implement:

- authentication
- authorization
- cryptographic signature verification
- template marketplace trust levels
- telemetry collection
- file locks
- generation checks
- redaction engine
- MCP server or adapter code
- package extraction
- frontend privacy console

## 13. Acceptance Rule

This contract is acceptable if it makes the following clear:

- templates need provenance before reuse
- approval needs a principal field even in single-user MVP
- MCP responses need explicit privacy return boundaries
- ids need namespace fields before cross-project sharing
- telemetry default is off
- durable events need UTC time and future local monotonic sequence
- concurrency is a known future write-safety concern, not silently ignored
