# SPRINT_050_WO-PER-JIKUO-CORE-21: Policy Template Extraction And Import MVP

> **Status**: Implemented for extract/export and no-write import planning MVP; `JIKUO-CORE-23` now implements project-context resolution and guarded template activation.
> **Product meaning**: turn proven project-local approved policies into reusable JIKUO policy templates without directly activating them in another project.
> **Scope rule**: no marketplace, no signature verification, no telemetry, no MCP, no automatic policy activation, and no writes to `.jikuo/policies/` during template extraction.

## 1. Why This Slice Exists

An incubating project contains approved JIKUO policies that are useful beyond that project:

- desktop workflow acceptance card and summary
- pre-delivery unit / integration / smoke tests
- pre-development scenario-chain and atom registration
- task-scope control before packaging

Those records should not be copied into JIKUO as active local policies. They should first become reusable templates with provenance, portability status, and required bindings.

## 2. Mounted Context

- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-20B_resource_reference_hygiene.md`
- source approved-policy directory supplied by the maintainer during extraction

## 3. In Scope

- Inspect an approved-policy source directory.
- Build a no-write template extraction plan from one approved policy.
- Preserve source policy ID and SHA-256 provenance without exposing the incubating project name, local path, or original user utterance in exported package templates.
- Preserve nested policy fields used by current approved policies.
- Infer basic required bindings such as `role://document/latest_todo_map` and `role://document/previous_todo_map`.
- Export a template into the package template directory only with `--confirm-export-template` and an approval phrase.
- Include exported templates in package data.
- Preview template import against a target project without writing, including project-context binding status.

## 4. Scenario-Chain-Atom Registration Evidence

This slice belongs to the `policy_template_seed_extraction` scenario chain.

User scenario:

- A JIKUO maintainer has proven approved policies in an incubating project and wants reusable package templates without activating those policies in the target project.

Operation chain:

1. Inspect the source approved-policy directory.
2. Build a no-write extraction plan for each candidate policy.
3. Export a package template only after explicit confirmation and approval phrase.
4. Preview import into a target project without writing.
5. Report unresolved project-context bindings before any activation work.

Registered atoms:

- `CAP-POLICY-TEMPLATE-EXTRACT-01`: implemented extraction, guarded export, and no-write import planning.
- `CAP-POLICY-TEMPLATE-PORTABILITY-01`: contract source for template / binding / resolved-policy portability.
- `CAP-PROJECT-CONTEXT-BINDING-01`: contract source for resolver and guarded import / bind / activate.
- `CAP-TRUST-PRIVACY-PROVENANCE-BASELINE-01`: provenance and cross-project safety baseline for portable templates.

Policy review evidence:

- Satisfies `scenario_chain_atom_registration_evidence` for the template-extraction part of CORE-21/22 by registering the scenario chain and atom IDs in this work order and in the productization task map.

## 5. Out Of Scope

- Do not import templates into a project policy store in this CORE-21 extraction slice.
- Do not activate templates as approved policies in this CORE-21 extraction slice.
- Do not write `.jikuo/project_context.yaml`.
- Do not implement template signing, marketplace trust, MCP, Plugin, frontend UI, or gates.
- Do not rewrite the incubating project's policy store.
- Do not expose incubating-project local paths, project identity, or raw source policy `source_refs` in package templates.

## 6. Implemented CLI

```powershell
python -B -m jikuo.policy_templates inspect-source --source-dir "<approved policy dir>" --format json
python -B -m jikuo.policy_templates plan-extract --source-policy "<policy yaml>" --source-project-ref "<private source project ref>" --format json
python -B -m jikuo.policy_templates export-template --source-policy "<policy yaml>" --source-project-ref "<private source project ref>" --confirm-export-template --approval-phrase "<exact user phrase as spoken>" --format json
python -B -m jikuo.policy_templates plan-import --template "<policy template yaml>" --project-root "<target project>" --format json
```

`JIKUO-CORE-23` adds the guarded activation follow-up:

```powershell
python -B -m jikuo.policy_templates activate-template --template "<policy template yaml>" --project-root "<target project>" --confirm-activate-template --approval-phrase "<exact user phrase as spoken>" --format json
```

`JIKUO-CORE-24` exposes the same adoption flow through the desktop harness:

```powershell
python -B -m jikuo.agent_flow propose --event policy_template_import_plan --template "<policy template yaml>" --project-root "<target project>" --format json
python -B -m jikuo.agent_flow apply --operation policy_template_activation --template "<policy template yaml>" --project-root "<target project>" --confirm-apply --approval-phrase "<exact user phrase as spoken>" --format json
```

## 7. Verification

```powershell
python -B -m unittest tests.policy_templates_tests
python -B -m unittest discover -s tests -p "*_tests.py"
```

Expected:

- template extraction plans are no-write
- template export refuses missing confirmation / approval
- exported package templates redact source project identity, local paths, and original source refs
- template export writes package templates but never creates `.jikuo/policies/`
- template import planning reports project-context binding status without writing

## 8. Follow-Up

- add a desktop-agent / `agent_flow.py` card bridge for template import and activation
- expose the stable template flow through MCP after portability and privacy boundaries are settled
