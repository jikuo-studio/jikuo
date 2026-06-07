# SPRINT_050_WO-PER-JIKUO-REL-01: External Release License Decision

> **Status**: Noncommercial preview license selected and implemented; package metadata now uses `PolyForm-Noncommercial-1.0.0`.
> **Product meaning**: make the external release posture reviewable before publishing JIKUO to users outside the private development workspace.
> **Scope rule**: this document records the license decision and implementation posture. It is still an engineering/product record, not legal advice.

## 0. Implemented Decision

The user chose a noncommercial public preview posture before GitHub
publication. The implementation uses the SPDX-listed PolyForm Noncommercial
License 1.0.0 rather than a hand-written custom license.

Implemented files:

- `LICENSE.md`: project license notice, SPDX identifier, canonical license URL,
  and required notice.
- `pyproject.toml`: package metadata changed from `Proprietary` to
  `PolyForm-Noncommercial-1.0.0`.
- `README.md`: GitHub-facing license section changed from "no public rights
  granted yet" to source-available noncommercial preview language.

Non-effects:

- No commercial use right is granted.
- No hosted service, production business use, trademark, contribution, or
  brand/IP terms are granted.
- No source-level SPDX header convention is introduced yet.

## 1. Why This Slice Now

JIKUO now has a product-facing README, CI, developer extras, and an MCP wrapper that has passed Stage A, Stage B1, and Stage B2 acceptance. The next release-readiness item in the task map is the external release license.

Before this decision, the package metadata was:

```toml
license = { text = "Proprietary" }
```

That was an acceptable private-development default, but it was not enough for a public PyPI / GitHub release where users, contributors, and downstream integrators need a clear rights boundary.

## 2. Non-Legal Product Decision Frame

This document is an engineering and product planning brief, not legal advice.

The decision has three practical dimensions:

- adoption: how easily can other developers try, fork, package, or embed JIKUO?
- contribution: can external users contribute patches without a license mismatch?
- business boundary: which parts, if any, should remain closed, paid, or governed by a separate commercial agreement?

## 3. Official Reference Anchors

Use standard identifiers and canonical license texts rather than hand-written license names.

- SPDX License List: `https://spdx.org/licenses/`
- SPDX MIT License: `https://spdx.org/licenses/MIT.html`
- SPDX Apache License 2.0: `https://spdx.org/licenses/Apache-2.0.html`
- Apache Software Foundation Apache License 2.0 page: `https://www.apache.org/licenses/LICENSE-2.0.html`

SPDX is useful here because it provides standardized short identifiers and canonical URLs. Apache's official page names `Apache-2.0` as the SPDX short identifier and marks Apache License 2.0 as OSI approved.

## 4. Candidate Postures

| Option | Metadata | Product posture | Good fit when | Tradeoff |
|---|---|---|---|---|
| Keep proprietary | `Proprietary` | private / controlled release | JIKUO is not ready for public redistribution or outside contributions | blocks open-source adoption and makes external contribution awkward |
| MIT | `MIT` | very permissive open-source core | maximum adoption and minimal license complexity are more important than patent-explicit wording | less explicit patent language than Apache-2.0 |
| Apache-2.0 | `Apache-2.0` | permissive open-source core with stronger enterprise signal | JIKUO wants open-source adoption, external contributions, and a clearer patent grant posture | slightly longer compliance surface than MIT |
| Open-core split | core `Apache-2.0` or `MIT`; commercial extras separate | open kernel plus paid integrations / Studio / hosting | kernel trust and ecosystem adoption matter, while advanced product surfaces may be monetized | requires clear package/module boundaries before publishing |
| Source-available noncommercial preview | `PolyForm-Noncommercial-1.0.0` | public inspection and noncommercial use, commercial terms reserved | users should be able to inspect and try JIKUO while the product keeps commercial rights separate | not OSI open source; external contribution and commercial-use terms still need explicit handling |

## 5. JIKUO-Specific Read

JIKUO's kernel is trust-oriented infrastructure: policy evaluation, runtime visibility, MCP adapters, guarded writes, and local audit artifacts. Users need to inspect and trust these parts.

That points toward an open core for the package kernel if the product goal is broad adoption across desktop AI clients and Agent SDK ecosystems. If open core is chosen, `Apache-2.0` is the conservative default candidate because JIKUO is intended to become infrastructure consumed by other developer tools.

This was only a planning recommendation until the user selected a concrete
license. After that selection, this work order records the implemented
noncommercial preview posture.

## 6. Decision Required

The implemented choice is source-available noncommercial preview:

- metadata: `PolyForm-Noncommercial-1.0.0`
- canonical terms: `https://polyformproject.org/licenses/noncommercial/1.0.0/`
- product posture: noncommercial public preview, with commercial terms reserved

Earlier candidate choices kept for audit context:

1. Keep `Proprietary` for now.
2. Switch the whole package to `MIT`.
3. Switch the whole package to `Apache-2.0`.
4. Adopt open-core posture: package kernel under `Apache-2.0` or `MIT`, with future Studio / hosted / premium integrations under a separate commercial license.

If the project later changes to MIT, Apache-2.0, or open core, the follow-up
implementation should:

- update `pyproject.toml`
- add the appropriate `LICENSE` file
- update root `README.md`
- update release-readiness notes in the task map
- consider source-level SPDX headers only if the project later adopts that convention

## 7. Acceptance Criteria

- The task map and registry record the selected noncommercial preview posture.
- Package metadata uses `PolyForm-Noncommercial-1.0.0`.
- `LICENSE.md` exists and points to the canonical PolyForm Noncommercial
  License 1.0.0 terms.
- README states the noncommercial preview posture and reserves commercial,
  brand/IP, and contribution terms.
- The brief keeps earlier candidate options visible for audit context without
  pretending to provide legal advice.
