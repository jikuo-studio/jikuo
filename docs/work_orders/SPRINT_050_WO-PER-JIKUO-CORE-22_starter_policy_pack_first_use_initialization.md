# SPRINT_050_WO-PER-JIKUO-CORE-22: Starter Policy Pack First-Use Initialization

> **Status**: Implemented MVP, ready for review
> **Product meaning**: let a new project start with useful report-only JIKUO policies instead of an empty policy store.
> **Scope rule**: initialize curated starter policies only after explicit approval; do not execute policy actions, enable gates, collect telemetry, or expose MCP.

## 1. Why This Slice Exists

`CORE-21` made incubating-project approved policies reusable as redacted package templates.

The product path for ordinary users should not require them to know any source project directory or run template extraction commands. First use should offer a curated starter pack:

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

## 4. Scenario-Chain-Atom Registration Evidence

This slice belongs to the `starter_policy_pack_first_use` scenario chain.

User scenario:

- A new project starts using JIKUO and needs useful report-only policies immediately, without knowing the incubating source project or running template extraction commands.

Operation chain:

1. User asks the desktop agent to initialize or enable JIKUO.
2. `agent_flow.py propose --event initialize_jikuo` renders a no-write starter policy pack card.
3. The card shows project-state status, policy-store status, starter policy list, write set, approval boundary, and non-effects.
4. User explicitly approves the starter initialization effect.
5. `agent_flow.py apply --operation starter_policy_pack_init` performs the guarded write.
6. The starter writer creates missing project state / registry mounts only when needed, creates approved report-only starter policy records, updates the policy-store manifest, and verifies starter policies are active.
7. Later task-start proposals can evaluate those starter policies as report-only guidance.

Registered atoms:

- `CAP-AGENT-FLOW-01`: desktop-agent no-write proposal runner.
- `CAP-STARTER-POLICY-PACK-INIT-01`: starter pack manifest loading, no-write plan, and guarded initialization target.
- `CAP-AGENT-FLOW-APPLY-STARTER-POLICY-PACK-01`: desktop-agent guarded apply route for starter initialization.
- `CAP-PROJECT-STATE-WRITE-01`: project-state creation used only when the target project is missing state.
- `CAP-POLICY-STORE-STATUS-01`: post-plan / post-write policy-store visibility.
- `CAP-POLICY-TEMPLATE-EXTRACT-01`: upstream source of curated package templates.

Policy review evidence:

- Satisfies `scenario_chain_atom_registration_evidence` for CORE-22 by registering the user scenario, operation chain, and atom IDs here and in the productization task map.

## 5. Out Of Scope

- No gate or blocking enforcement.
- No policy action execution.
- No task-session evidence persistence.
- No telemetry or external network behavior.
- No MCP or frontend implementation.
- No automatic overwrite of existing active policies.

## 6. Implemented Surfaces

The user-facing path is the desktop-agent flow: proposal cards first, guarded apply only after explicit approval. The direct starter CLI remains an internal/dev verification surface.

```powershell
python -B -m jikuo.agent_flow propose --event initialize_jikuo --project-root "<target project>" --format json
python -B -m jikuo.agent_flow apply --operation starter_policy_pack_init --project-root "<target project>" --confirm-apply --approval-phrase "<exact user phrase as spoken>" --format json
python -B -m jikuo.starter_policies plan-init --project-root "<target project>" --format json
python -B -m jikuo.starter_policies init --project-root "<target project>" --confirm-starter-init --approval-phrase "<exact user phrase as spoken>" --format json
```

## 7. Verification

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

## 8. Follow-Up

- Project-context resolver for template import / binding.
- MCP wrapper only after the starter and resolver paths are stable.
