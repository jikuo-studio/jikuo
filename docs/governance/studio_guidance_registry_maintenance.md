# Studio Guidance Registry Maintenance

> Status: Maintainer contract for Studio first-run guidance links.
> Scope: `docs/registry/guidance_links.yaml` and the Studio first-run
> readiness guidance projection.

---

## 1. Purpose

The Studio guidance registry maps stable first-run readiness keys to
maintainer-reviewed documentation links.

Studio must not discover setup guidance by scraping arbitrary documents or by
guessing from implementation code. The read model loads
`docs/registry/guidance_links.yaml`, validates that the referenced document and
anchor exist, and exposes the result to the frontend as structured guidance
metadata.

Business meaning: first-run setup remains understandable after documentation
changes because the frontend follows one reviewed registry instead of a set of
implicit path assumptions.

---

## 2. Authority Boundary

Authoritative source:

- `docs/registry/guidance_links.yaml`

Maintainer contract:

- `docs/governance/studio_guidance_registry_maintenance.md`

Rendered consumers:

- Studio first-run readiness read model
- Studio frontend first-run setup rows
- tests that validate registry references and link health

Non-authoritative sources:

- ad hoc markdown search results
- frontend hard-coded document paths
- runtime cards or local proof notes
- inferred setup meaning from implementation code

JIKUO does not classify the meaning of a document link. Maintainers classify
coverage through registry fields such as `coverage_status`, `reason`, and
`missing_note`. JIKUO only records, validates, merges, and displays the
structured mapping.

---

## 3. Entry Contract

Each registry entry should keep these fields:

- `guidance_id`: stable public identifier, for example
  `first_run.activation_settings`.
- `readiness_key`: key used by the first-run readiness read model.
- `title`: short configuration item name.
- `guidance_label`: link text rendered in Studio.
- `doc_path`: project-relative markdown document path.
- `anchor_id`: stable explicit anchor in the target document.
- `doc_title`: human-readable target document or section title.
- `coverage_status`: maintainer-authored coverage state.
- `reason`: why this document helps the configuration item.
- `missing_note`: follow-up needed when coverage is partial or missing.

The registry may include additional metadata, but frontend rendering should use
the read-model projection rather than reading the registry file directly.

---

## 4. Stable Anchor Rules

Target documents should use explicit stable HTML anchors:

```markdown
<a id="first-run.activation-settings"></a>
```

Rules:

- Keep anchor IDs stable across heading rewrites.
- Prefer `first-run.<readiness-key-with-dashes>` for first-run readiness links.
- Move the anchor with the relevant section if the document is reorganized.
- Do not rely only on generated markdown heading slugs.
- If a target section is deleted, update the registry in the same change.

---

## 5. Coverage Status

Allowed values:

- `exact`: the target section directly guides the user through this setup item.
- `partial`: the target section is useful but incomplete.
- `missing`: no adequate setup guide exists yet.

Rules:

- `coverage_status` is a maintainer decision, not a JIKUO semantic judgment.
- `partial` and `missing` entries must explain the gap in `missing_note`.
- Do not mark an entry `exact` only because the target file exists.
- Do not hide a setup gap by linking to a broad overview without a reason.

Business meaning: users can distinguish "this setup path is documented" from
"this product boundary is visible but still needs better documentation."

---

## 6. Resolver And Frontend Contract

The resolver should:

- load the registry from the configured project root when present;
- fall back to the product source registry only when project-local docs are not
  available;
- reject links outside the `docs/` tree;
- validate that `doc_path` exists;
- validate that `anchor_id` exists when supplied;
- return `link_status` and `broken_reason` in the read model.

The frontend should:

- render only the guidance metadata provided by the Studio read model;
- link to the read-only Studio markdown route or an equivalent read-model
  resolved target;
- show `partial` and `missing` states without embedding tutorial prose into the
  readiness card;
- avoid hard-coded first-run guidance document paths.

This preserves the Studio frontend authoritative data-source boundary.

---

## 7. Change Workflow

When adding or changing first-run guidance:

1. Add or move the target document section.
2. Add a stable explicit anchor.
3. Update `docs/registry/guidance_links.yaml`.
4. Set `coverage_status` honestly.
5. Add or update `missing_note` for incomplete coverage.
6. Run the Studio read-model and web tests.
7. Verify Studio renders the expected guidance label and link status.

When documentation moves:

1. Move the stable anchor with the content.
2. Update `doc_path`, `doc_title`, and `reason` if needed.
3. Keep the same `guidance_id` unless the setup item itself is replaced.
4. Let tests catch stale paths or missing anchors.

---

## 8. Validation Checklist

Before closing a change that affects first-run guidance, verify:

- every first-run readiness key has either a registry entry or an explicit
  missing coverage decision;
- every `doc_path` is project-relative and under `docs/`;
- every target document exists;
- every `anchor_id` exists in the target document;
- every `coverage_status` is one of `exact`, `partial`, or `missing`;
- every `partial` or `missing` entry has a useful `missing_note`;
- `docs/registry/registry_index.yaml` points to this maintenance contract.

---

## 9. Non-Effects

Maintaining the guidance registry does not:

- change activation settings;
- install client instruction files;
- configure an MCP server;
- activate starter policies;
- change document rules;
- satisfy missing runtime evidence;
- let JIKUO infer semantic intent from documentation text.

