# JIKUO-POLICY-CATALOG-01: Self-Bootstrap Policy Promotion Review

> **Status**: Accepted for code-level hardening; first boundary implementation in progress  
> **Date**: 2026-05-16  
> **User scenario**: A user installs or updates JIKUO and must never have JIKUO's own dogfood policies silently copied over, merged into, or used to overwrite the user's project-local policies.  
> **Business meaning**: Protects ordinary users from accidental policy takeover while still allowing useful JIKUO self-bootstrap practices to be reviewed and promoted into official starter packs or optional templates.

---

## Problem

JIKUO has two different policy stores:

- JIKUO's own self-bootstrap store: `.jikuo/policies/approved`
- A user's project-local store: `<user project>/.jikuo/policies/approved`

These must never be treated as the same distribution channel.

The official policy distribution path is:

1. package-owned templates under `src/jikuo/policy_templates/`
2. package-owned starter pack manifests under `src/jikuo/starter_policy_packs/`
3. guarded user approval
4. writes into the user's own `.jikuo/policies/`

JIKUO's self-bootstrap `.jikuo/policies/` may provide promotion candidates, but it is not itself a package distribution source.

---

## Hard Boundary

This work order requires code-level enforcement, not semantic agent discipline.

Starter policy initialization MUST:

- accept official starter sources only from `pkg://jikuo/policy_templates/...`
- reject `.jikuo/policies/...` as a starter source, even inside the JIKUO repo
- reject relative path escape, absolute path, source-project paths, and non-template package paths
- create or append only the explicitly reviewed starter policies
- refuse collisions with existing user policy IDs or starter artifacts
- preserve existing user policy files and active manifest refs
- require explicit confirmation and approval evidence before writing

Starter policy initialization MUST NOT:

- read JIKUO self-bootstrap `.jikuo/policies/approved` as a starter source
- bulk sync JIKUO's dogfood policies into user projects
- overwrite a user's existing policy file
- replace a user's manifest active refs with the starter pack's refs
- treat Git pull / package update as policy activation

---

## Promotion Workflow

Self-bootstrap policies can become reusable only through an explicit review:

| Classification | Meaning |
|---|---|
| `dogfood_only` | Stays only in JIKUO's own `.jikuo/policies`; never distributed to users |
| `official_starter` | Promoted into the default starter pack after review |
| `optional_template` | Added to the template catalog but not enabled by default |
| `deferred` | Useful idea, but not ready for distribution |

Each promoted policy must become a package template first. It may then be referenced by a starter pack manifest. The user's active policy store changes only through the guarded starter/template activation path.

---

## Current Implementation Slice

This slice hardens starter initialization:

- starter pack IDs are constrained to package-local manifests
- starter pack entries are constrained to `pkg://jikuo/policy_templates/...`
- project-local `.jikuo/policies` refs are refused as starter sources
- tests prove starter init appends to an existing user policy store without overwriting the user's policy

The item-by-item promotion audit of all JIKUO self-bootstrap policies remains a follow-on task.

---

## Acceptance

- `python -B -m unittest tests.starter_policies_tests`
- a bad starter manifest pointing at `pkg://jikuo/.jikuo/policies/approved/...` produces no policies and reports a source-boundary warning
- `plan-init --pack-id ..` refuses with `starter_pack_source_boundary_violation`
- guarded starter init into a project with an existing user policy preserves the existing policy text and leaves it active
- official starter pack still initializes only reviewed package templates
