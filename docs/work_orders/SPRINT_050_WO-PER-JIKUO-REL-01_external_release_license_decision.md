# SPRINT_050_WO-PER-JIKUO-REL-01: External Release License Decision

> **Status**: Decision brief drafted; package metadata remains `Proprietary` until the user explicitly chooses a license.
> **Product meaning**: make the external release posture reviewable before publishing JIKUO to users outside the private development workspace.
> **Scope rule**: this slice does not change `pyproject.toml`, add a `LICENSE` file, or grant any new rights. It only prepares the decision surface.

## 1. Why This Slice Now

JIKUO now has a product-facing README, CI, developer extras, and an MCP wrapper that has passed Stage A, Stage B1, and Stage B2 acceptance. The next release-readiness item in the task map is the external release license.

The current package metadata is:

```toml
license = { text = "Proprietary" }
```

That is an acceptable private-development default, but it is not enough for a public PyPI / GitHub release where users, contributors, and downstream integrators need a clear rights boundary.

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

## 5. JIKUO-Specific Read

JIKUO's kernel is trust-oriented infrastructure: policy evaluation, runtime visibility, MCP adapters, guarded writes, and local audit artifacts. Users need to inspect and trust these parts.

That points toward an open core for the package kernel if the product goal is broad adoption across desktop AI clients and Agent SDK ecosystems. If open core is chosen, `Apache-2.0` is the conservative default candidate because JIKUO is intended to become infrastructure consumed by other developer tools.

This is only a planning recommendation. The repository must not change license metadata until the user approves the concrete license.

## 6. Decision Required

Choose one:

1. Keep `Proprietary` for now.
2. Switch the whole package to `MIT`.
3. Switch the whole package to `Apache-2.0`.
4. Adopt open-core posture: package kernel under `Apache-2.0` or `MIT`, with future Studio / hosted / premium integrations under a separate commercial license.

If option 2, 3, or 4 is chosen, the follow-up implementation should:

- update `pyproject.toml`
- add the appropriate `LICENSE` file
- update root `README.md`
- update release-readiness notes in the task map
- consider source-level SPDX headers only if the project later adopts that convention

## 7. Acceptance Criteria

- The task map links this decision brief from the external release license open item.
- Package metadata remains unchanged until explicit user decision.
- No `LICENSE` file is created by this brief.
- The brief names the candidate options and tradeoffs without pretending to make the legal decision.

