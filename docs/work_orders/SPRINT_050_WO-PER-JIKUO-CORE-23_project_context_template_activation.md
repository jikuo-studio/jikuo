# SPRINT_050_WO-PER-JIKUO-CORE-23: Project Context Template Activation

> **Status**: Implemented for project-context resolution, no-write import planning, and guarded template activation.
> **Product meaning**: let a reusable package policy template become a project-approved policy only after project-local bindings are visible, safe, and explicitly approved.
> **Scope rule**: resolve and activate one template through guarded local writes; do not add marketplace trust, signing, telemetry, MCP, frontend UI, gates, or automatic action execution.

## 1. Why This Slice Exists

`JIKUO-CORE-21` could extract and export reusable templates, but import planning still stopped at "project_context resolver is not implemented."

That was correct for the extraction MVP, but it left the product flow half-open:

- templates could be packaged
- starter packs could activate curated built-ins
- ordinary reusable templates still could not bind safely to a target project's local roles before activation

This slice closes the local atom-level gap before MCP. MCP should wrap a stable template activation boundary, not invent one.

## 2. Mounted Context

- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-21_policy_template_extraction_import_mvp.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-22_starter_policy_pack_first_use_initialization.md`
- active self-bootstrap policies in `.jikuo/policies/approved`

## 3. In Scope

- Read `.jikuo/project_context.yaml` using schema `jikuo.project_context.v0`.
- Resolve required `role://document/*` and `role://directory/*` bindings through project context.
- Resolve exact `project://...` refs safely inside the project root.
- Resolve `pkg://jikuo/...` refs inside the installed package.
- Reject absolute paths and path escapes as unsafe bindings.
- Report missing targets and unresolved required bindings without writing.
- Produce `jikuo.resolved_policy.v0` preview and `resolved_policy_preview`.
- Activate one resolved template policy only with `--confirm-activate-template` and an approval phrase.
- Write proposal snapshot, approved policy, decision record, and manifest refs for a guarded activation.

## 4. Scenario-Chain-Atom Registration Evidence

Scenario chain:

- chain_id: `policy_template_import_bind_activate`
- user scenario: a project wants to adopt a reusable JIKUO policy template without copying private paths or activating unsafe bindings
- operation chain: template import plan -> project context read -> role bindings resolved -> unsafe / missing bindings reported -> resolved policy preview rendered -> guarded activation after approval -> active policy appears in policy-store status

Registered atoms:

- `CAP-PROJECT-CONTEXT-RESOLVER-01`
- `CAP-POLICY-TEMPLATE-IMPORT-PLAN-01`
- `CAP-POLICY-TEMPLATE-ACTIVATE-01`
- `CAP-POLICY-STORE-STATUS-01`

Evidence:

- This work order declares the scenario chain and atom list.
- `jikuo_productization_task_map.md` registers the same chain and atoms.
- `policy_templates_tests.py` covers resolved bindings, unsafe path rejection, guarded activation refusal, and approved activation.

## 5. Implemented CLI

```powershell
python -B -m jikuo.policy_templates plan-import --template "<policy template yaml>" --project-root "<target project>" --format json
python -B -m jikuo.policy_templates activate-template --template "<policy template yaml>" --project-root "<target project>" --confirm-activate-template --approval-phrase "<exact user phrase as spoken>" --format json
```

## 6. Acceptance Evidence

Required:

- Missing `.jikuo/project_context.yaml` keeps required bindings unresolved and performs no writes.
- Valid document role bindings resolve to project-relative refs.
- `../` path escapes are reported as `unsafe_binding`.
- `activate-template` refuses without confirmation and approval phrase.
- Approved activation writes one approved policy, one proposal snapshot, one decision record, and a manifest ref.
- Activated policies retain `template_ref`, `project_context_ref`, and `resolved_bindings`.
- Existing extraction / starter-policy behavior remains unchanged.

Validation command:

```powershell
$env:PYTHONPATH='src'
python -B -m unittest tests.policy_templates_tests
python -B -m unittest discover -s tests -p "*_tests.py"
```

## 7. Follow-Up

- Desktop-agent / `agent_flow.py` card bridge for template import and activation is implemented by `JIKUO-CORE-24`.
- Expose template import planning and activation through MCP after the MCP adapter boundary exists.
- Decide separately whether any self-bootstrap policies should become built-in starter templates.
