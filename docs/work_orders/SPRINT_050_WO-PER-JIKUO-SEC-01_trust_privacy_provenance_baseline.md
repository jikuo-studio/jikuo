# SPRINT_050_WO-PER-JIKUO-SEC-01: Trust Privacy Provenance Baseline

> **Status**: Draft contract, ready for user review
> **Product meaning**: define the social trust and safety fields JIKUO needs before reusable policy templates or MCP tools cross project, user, or machine boundaries.
> **Scope rule**: contract only; do not implement auth, signing, telemetry, redaction, locking, template import, package extraction, or MCP in this slice.

## 1. Why This Slice Exists

`JIKUO-CORE-20` made policies portable by separating template intent from project-local binding.

Portability creates a trust surface:

- templates may be imported
- approvals may happen across users or machines
- MCP responses may leave the local tool process
- ids may collide across template sources
- future telemetry could damage trust if added without an explicit boundary

`SEC-01` defines minimum baseline fields and defaults before MCP implementation continues.

## 2. In Scope

This slice defines:

- template provenance fields
- principal / approval authority fields
- privacy boundary classes for MCP-facing results
- namespace and fully qualified id fields
- telemetry default policy
- timestamp and local causal-order fields
- concurrency lock baseline as a future write-safety requirement
- MCP implications for response projection and approval boundaries

## 3. Out Of Scope

This slice must not:

- implement authentication
- implement authorization
- implement signature verification
- import templates
- collect telemetry
- implement redaction
- implement file locks or generation checks
- change approval writer behavior
- change policy-store runtime behavior
- move package files
- implement MCP server / adapter code
- build frontend privacy controls

## 4. Deliverables

- `docs/jikuo/governance/jikuo_trust_privacy_provenance_baseline.md`
- this work order
- task-map updates for `JIKUO-SEC-01`
- execution-mount updates so future `CORE-20B`, package extraction, and MCP tasks mount this contract

## 5. Acceptance Cases

Review acceptance:

- Does the contract state telemetry is off by default?
- Does every future approval record have a `principal` field, even if MVP uses `local_user`?
- Does a template have provenance fields before import / approval?
- Do MCP-facing results distinguish `returned_to_client`, `stays_local`, and `redacted_before_return`?
- Do portable ids have `namespace` and `fully_qualified_id` fields?
- Do durable records include `timestamp_utc`, `timestamp_source`, and future `monotonic_seq`?
- Does concurrency appear as a future guarded-write requirement without implementing locks in this slice?

## 6. Testing Requirements

Unit tests:

- not required for this contract-only slice.
- future implementation must test privacy classification, principal preservation, namespace stability, and telemetry-off default.

Integration tests:

- not required for this contract-only slice.
- future MCP implementation must test that raw local sidecar fields are not returned when only a compact projection is intended.

Smoke tests:

- run existing `agent_flow_tests.py` and `policy_store_tests.py` after updating docs.
- run no-write `agent_flow.py propose` with task-scope evidence for this work order.

Human review:

- confirm the trust baseline is understandable to a future external user.
- confirm it does not expand into a full auth, telemetry, marketplace, frontend, or MCP implementation.

## 7. Next Task

If accepted, continue to:

- `JIKUO-PKG-01`: minimal package extraction.
- `JIKUO-CORE-20B`: resource-reference and `CONTRACT_REFS` hygiene inside the extracted package boundary.

Do not return to MCP implementation until `PKG-01` and `CORE-20B` are complete or explicitly deferred.
