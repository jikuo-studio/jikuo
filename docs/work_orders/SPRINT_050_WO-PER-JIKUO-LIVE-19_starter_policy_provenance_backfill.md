# SPRINT_050_WO-PER-JIKUO-LIVE-19: Starter Policy Provenance Backfill

> **Status**: Implemented and ready for user review on 2026-05-15
> **Product meaning**: make official starter policies carry explicit package provenance before MCP exposes first-use initialization flows.
> **Scope rule**: backfill provenance metadata for package-owned starter policies; do not implement MCP, policy signing, marketplace trust, remote transport privacy, or new policy behavior in this slice.

## 1. Why This Slice Now

`JIKUO-ARCH-03` found that `starter_policies.build_starter_init_plan(...)` and `initialize_starter_pack(...)` were structured enough for MCP wrapping, but the starter policies did not carry the SEC-01 provenance field shape.

That means a future MCP caller could initialize useful starter rules while the resulting approved policies still looked like unknown-source records. For a governance harness, unknown-source starter policies are not acceptable as a default first-use path.

## 2. Decision

Official starter policy records now use package-owned provenance:

```yaml
provenance:
  schema: "jikuo.policy_provenance.v0"
  source: "verified_jikuo_official"
  source_ref: "pkg://jikuo/policy_templates/..."
  starter_pack_ref: "engineering_governance"
  imported_at_utc: null
  reviewed_by:
    principal_id: "jikuo_package_maintainers"
    principal_type: "package_maintainer"
  review_wall_required: false
  signed_by: null
  verified_at_utc: null
```

This source value means "bundled with this JIKUO package as an official starter asset." It does not claim third-party marketplace signing, remote trust attestation, or team review.

## 3. Implementation

Updated `src/jikuo/starter_policies.py`:

- added `jikuo.policy_provenance.v0` metadata for starter policies
- added `verified_jikuo_official` as the official starter-pack provenance source
- exposed provenance in `plan-init` starter policy summaries
- wrote the same provenance into guarded starter policy initialization outputs

Updated tests:

- `tests/starter_policies_tests.py` now verifies plan summaries include official provenance
- guarded init tests verify all written approved starter policies contain the provenance block

Updated main docs:

- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/governance/jikuo_productization_task_map.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-SEC-01_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-ARCH-03_mcp_pre_implementation_api_neutrality_review.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MCP-01_mcp_wrapper_mvp.md`
- `.jikuo/project_context.yaml`
- `docs/README.md`

## 4. Scenario-Chain-Atom Registration Evidence

| User-facing chain | Operation chain | Required atoms | Acceptance boundary |
|---|---|---|---|
| Starter policy provenance backfill | load official starter pack -> copy template policy into starter policy record -> attach package-owned provenance -> expose provenance in plan summary -> guarded init writes approved policy with provenance -> future MCP wrapper can refuse missing provenance | `CAP-STARTER-POLICY-PROVENANCE-01`; `CAP-STARTER-POLICY-PACK-INIT-01`; `CAP-TRUST-PRIVACY-PROVENANCE-BASELINE-01`; `CAP-MCP-PREIMPLEMENTATION-API-NEUTRALITY-REVIEW-01` | provenance metadata only; no MCP adapter/server code; no signing; no marketplace trust; no new policy actions |

## 5. Acceptance Criteria

- `plan-init` reports provenance for every starter policy.
- Guarded starter initialization writes provenance into every approved starter policy.
- `source_ref` remains `pkg://jikuo/...` and never leaks incubating-source project paths.
- SEC-01 distinguishes `verified_jikuo_official` from future third-party `verified` trust.
- `JIKUO-ARCH-03` no longer lists starter provenance as an MCP blocker.
- MCP implementation remains blocked on response privacy classification and revised MCP-01 acceptance.
