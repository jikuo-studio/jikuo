# SPRINT_050_WO-PER-JIKUO-SEC-02: MCP Response Privacy Classification Baseline

> **Status**: Implemented and ready for user review on 2026-05-15
> **Product meaning**: prevent MCP responses from leaking local paths, raw approval phrases, raw sidecar records, or user/project content when JIKUO becomes callable by desktop clients.
> **Scope rule**: contract and checklist only; do not implement MCP adapter/server code, redaction code, auth, telemetry, dashboard, or remote transport behavior in this slice.

## 1. Why This Slice Now

`JIKUO-ARCH-03` accepted the core API neutrality review and left two blockers before MCP implementation:

- response-level privacy classification for local paths, approval data, and raw sidecar records
- user acceptance of the revised `JIKUO-MCP-01` implementation scope

`JIKUO-LIVE-19` resolved the starter policy provenance blocker. The remaining privacy blocker needs to be explicit before any MCP tool starts serializing JIKUO results.

## 2. Decision

MCP-facing responses use field-level privacy classification:

| Classification | Meaning |
|---|---|
| `return` | Safe compact projection for MCP response. |
| `local_only` | Useful locally, omitted for remote or unknown transport. |
| `redact_required` | Sensitive value replaced with `<REDACTED>`. |
| `redact_optional` | Summary returned by default; full content requires explicit local-only mode. |

Safe defaults:

- IDs, refs, statuses, counts, timestamps, compact summaries, and relative project paths are `return`.
- Absolute local paths, raw sidecar records, raw chat transcripts, and raw local file content are `local_only`.
- Approval phrase values and secrets are `redact_required`.
- Evidence full content and user-provided excerpts are `redact_optional`.

## 3. Implementation

Updated `docs/governance/jikuo_trust_privacy_provenance_baseline.md`:

- replaced the coarse privacy boundary with field-level classifications
- added default classifications by field kind
- split runtime display links into relative `return` refs and absolute `local_only` paths
- required card-only tools to avoid embedding raw approval phrases, transcripts, or local file content

Updated `JIKUO-MCP-01`:

- added a pre-implementation startup checklist
- added field-level privacy classification to testing requirements
- added user-experience acceptance standards before implementation begins

Updated active mounts and task map:

- registered `JIKUO-SEC-02`
- registered `CAP-MCP-RESPONSE-PRIVACY-CLASSIFICATION-01`
- removed response privacy classification as an unresolved blocker once this slice is accepted

## 4. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| MCP response privacy classification baseline | identify response fields -> classify fields as return / local_only / redact_required / redact_optional -> update SEC-01 -> update MCP startup checklist -> keep MCP implementation blocked until accepted | `CAP-MCP-RESPONSE-PRIVACY-CLASSIFICATION-01`; `CAP-TRUST-PRIVACY-PROVENANCE-BASELINE-01`; `CAP-MCP-PREIMPLEMENTATION-API-NEUTRALITY-REVIEW-01`; `CAP-MCP-AGENT-FLOW-WRAPPER-01` | docs/checklist only; no MCP adapter/server code; no redaction implementation; no remote transport implementation |

## 5. Acceptance Criteria

- SEC-01 defines the four MCP response classifications.
- SEC-01 defines default classification by field kind.
- Runtime display links distinguish relative returnable refs from absolute local-only paths.
- MCP-01 startup checklist requires response privacy classification before code implementation.
- MCP-01 testing requirements include field classification, local-only omission, and redaction checks.
- The task map and execution mounts no longer list response privacy classification as an unaddressed blocker once this slice is accepted.
