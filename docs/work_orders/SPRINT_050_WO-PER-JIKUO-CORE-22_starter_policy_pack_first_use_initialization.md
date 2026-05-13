# SPRINT_050_WO-PER-JIKUO-CORE-22: Starter Policy Pack First-Use Initialization

> **Status**: Implemented MVP, ready for review
> **Product meaning**: let a new project start with useful report-only JIKUO policies instead of an empty policy store.
> **Scope rule**: initialize curated starter policies only after explicit approval; do not execute policy actions, enable gates, collect telemetry, or expose MCP.

## 1. Why This Slice Exists

`CORE-21` made NarrativeSystem-approved policies reusable as package templates.

The product path for ordinary users should not require them to know the NarrativeSystem source directory or run template extraction commands. First use should offer a curated starter pack:

- desktop workflow acceptance card and summary
- pre-delivery unit / integration / smoke tests
- pre-development scenario-chain and atom registration
- task-scope control before packaging

These starter policies are report-only guidance. They help the user start work with better process visibility without turning JIKUO into a blocking gate.

## 2. Mounted Context

- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-21_policy_template_extraction_import_mvp.md`
- `src/jikuo/policy_templates/engineering_governance/*.yaml`
- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/governance/jikuo_trust_privacy_provenance_baseline.md`

## 3. In Scope

- Add an `engineering_governance` starter pack manifest.
- Plan first-use starter initialization without writing.
- Project first-use starter initialization through desktop-agent cards.
- Apply first-use starter initialization through `agent_flow.py apply` after approval.
- Show whether project state and policy store already exist.
- Show the starter policies and write set before approval.
- Guarded initialization may create:
  - `docs/governance/rule_registry.yaml` when missing as the initial project governance mount
  - `.jikuo/project_state.yaml` when missing
  - `.jikuo/policies/approved/*.yaml`
  - `.jikuo/policies/proposals/*.yaml`
  - `.jikuo/policies/decisions/*.yaml`
  - `.jikuo/policies/manifest.yaml`

## 4. Out Of Scope

- No gate or blocking enforcement.
- No policy action execution.
- No task-session evidence persistence.
- No telemetry or external network behavior.
- No MCP or frontend implementation.
- No automatic overwrite of existing active policies.

## 5. Implemented Surfaces

The user-facing path is the desktop-agent flow: proposal cards first, guarded apply only after explicit approval. The direct starter CLI remains an internal/dev verification surface.

```powershell
python -B -m jikuo.agent_flow propose --event initialize_jikuo --project-root "<target project>" --format json
python -B -m jikuo.agent_flow apply --operation starter_policy_pack_init --project-root "<target project>" --confirm-apply --approval-phrase "<exact user phrase as spoken>" --format json
python -B -m jikuo.starter_policies plan-init --project-root "<target project>" --format json
python -B -m jikuo.starter_policies init --project-root "<target project>" --confirm-starter-init --approval-phrase "<exact user phrase as spoken>" --format json
```

## 6. Verification

```powershell
python -B -m unittest tests.starter_policies_tests
python -B -m unittest discover -s tests -p "*_tests.py"
```

Expected:

- plan mode is no-write
- init refuses missing confirmation / approval
- guarded init creates project state and starter policy store in a fresh project
- starter policies are active report-only after init
- no gate or policy action is executed

## 7. Follow-Up

- Project-context resolver for template import / binding.
- MCP wrapper only after the starter and resolver paths are stable.
