# SPRINT_050_WO-PER-JIKUO-CORE-21: Policy Template Extraction And Import MVP

> **Status**: Implemented for extract/export and no-write import planning MVP, import activation remains guarded follow-up
> **Product meaning**: turn proven project-local approved policies into reusable JIKUO policy templates without directly activating them in another project.
> **Scope rule**: no marketplace, no signature verification, no telemetry, no MCP, no automatic policy activation, and no writes to `.jikuo/policies/` during template extraction.

## 1. Why This Slice Exists

NarrativeSystem contains approved JIKUO policies that are useful beyond that project:

- desktop workflow acceptance card and summary
- pre-delivery unit / integration / smoke tests
- pre-development scenario-chain and atom registration
- task-scope control before packaging

Those records should not be copied into JIKUO as active local policies. They should first become reusable templates with provenance, portability status, and required bindings.

## 2. Mounted Context

- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-20B_resource_reference_hygiene.md`
- `D:\personal_project\NarrativeSystem\.jikuo\policies\approved\*.yaml`

## 3. In Scope

- Inspect an approved-policy source directory.
- Build a no-write template extraction plan from one approved policy.
- Preserve source policy provenance and SHA-256.
- Preserve nested policy fields used by current approved policies.
- Infer basic required bindings such as `role://document/latest_todo_map` and `role://document/previous_todo_map`.
- Export a template into the package template directory only with `--confirm-export-template` and an approval phrase.
- Include exported templates in package data.
- Preview template import against a target project without writing, including unresolved binding status.

## 4. Out Of Scope

- Do not import templates into a project policy store.
- Do not activate templates as approved policies.
- Do not write `.jikuo/project_context.yaml`.
- Do not implement template signing, marketplace trust, MCP, Plugin, frontend UI, or gates.
- Do not rewrite the NarrativeSystem policy store.

## 5. Implemented CLI

```powershell
python -B -m jikuo.policy_templates inspect-source --source-dir "<approved policy dir>" --format json
python -B -m jikuo.policy_templates plan-extract --source-policy "<policy yaml>" --source-project-ref NarrativeSystem --format json
python -B -m jikuo.policy_templates export-template --source-policy "<policy yaml>" --source-project-ref NarrativeSystem --confirm-export-template --approval-phrase "<exact user phrase as spoken>" --format json
python -B -m jikuo.policy_templates plan-import --template "<policy template yaml>" --project-root "<target project>" --format json
```

## 6. Verification

```powershell
python -B -m unittest tests.policy_templates_tests
python -B -m unittest discover -s tests -p "*_tests.py"
```

Expected:

- template extraction plans are no-write
- template export refuses missing confirmation / approval
- template export writes package templates but never creates `.jikuo/policies/`
- template import planning reports missing project-context bindings without writing

## 7. Follow-Up

- implement project-context resolver for `role://`, `project://`, and `pkg://`
- implement guarded template import / bind / resolve plan
- implement guarded activation from resolved template to approved project policy
- expose the stable template flow through MCP after portability and privacy boundaries are settled
