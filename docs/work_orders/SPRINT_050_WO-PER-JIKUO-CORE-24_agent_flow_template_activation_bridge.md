# SPRINT_050_WO-PER-JIKUO-CORE-24: Agent Flow Template Activation Bridge

> **Status**: Implemented for desktop `agent_flow.py` template import planning and guarded activation.
> **Product meaning**: make reusable policy-template adoption visible in the desktop harness instead of requiring users or agents to know the lower-level `policy_templates.py` CLI.
> **Scope rule**: wrap existing CORE-23 import planning and guarded activation atoms in `agent_flow.py`; do not add MCP, marketplace trust, frontend UI, gates, or automatic policy action execution.

## 1. Why This Slice Exists

`JIKUO-CORE-23` made template activation technically possible, but the user-facing flow was still module-centric:

- `policy_templates.py plan-import` could build the resolved-policy preview
- `policy_templates.py activate-template` could write after approval
- the desktop harness did not yet show a first-class import card or guarded `agent_flow.py apply` operation

That creates a half-black-box product experience. JIKUO policy-template adoption must be visible, traceable, and auditable through the same harness surface as task start, starter pack initialization, and policy evolution.

## 2. Mounted Context

- `docs/governance/jikuo_desktop_agent_instruction_pack.md`
- `docs/governance/jikuo_execution_mounts.md`
- `docs/governance/jikuo_productization_task_map.md`
- `docs/governance/jikuo_project_context_binding_and_policy_template_portability.md`
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-23_project_context_template_activation.md`
- active self-bootstrap policies in `.jikuo/policies/approved`

## 3. In Scope

- Add `policy_template_import_plan` as an `agent_flow.py propose` event.
- Return a visible `policy_template_import_plan` card with binding status, resolved-policy preview refs, proposed write set, and non-effects.
- Generate a guarded `jikuo.agent_flow apply --operation policy_template_activation` command proposal when bindings resolve.
- Add `policy_template_activation` as an accepted guarded apply operation.
- Preserve confirmation and approval-phrase requirements from CORE-23.
- Keep proposal mode no-write and include the result in `chat_ready_markdown`.

## 4. Scenario-Chain-Atom Registration Evidence

Scenario chain:

- chain_id: `policy_template_desktop_activation_bridge`
- user scenario: a desktop Agent user adopts a reusable JIKUO policy template and sees bindings, write effects, and activation result in chat
- operation chain: user/agent selects template -> `agent_flow.py propose --event policy_template_import_plan` -> project context is resolved -> import card is rendered -> guarded `agent_flow.py apply --operation policy_template_activation` runs after approval -> approved policy appears in policy-store status

Registered atoms:

- `CAP-AGENT-FLOW-POLICY-TEMPLATE-IMPORT-PLAN-01`
- `CAP-PROJECT-CONTEXT-RESOLVER-01`
- `CAP-POLICY-TEMPLATE-IMPORT-PLAN-01`
- `CAP-POLICY-TEMPLATE-ACTIVATE-01`
- `CAP-AGENT-FLOW-APPLY-POLICY-TEMPLATE-ACTIVATION-01`

Evidence:

- This work order declares the desktop bridge chain and atom list.
- `jikuo_productization_task_map.md` registers the same chain and atoms.
- `agent_flow_tests.py` covers visible import-card proposal, refusal without approval, approved activation write, and no NarrativeSystem leakage in the activated policy.

## 5. Implemented CLI

```powershell
python -B -m jikuo.agent_flow propose --event policy_template_import_plan --template "<policy template yaml>" --project-root "<target project>" --format json
python -B -m jikuo.agent_flow apply --operation policy_template_activation --template "<policy template yaml>" --project-root "<target project>" --confirm-apply --approval-phrase "<exact user phrase as spoken>" --format json
```

## 6. Acceptance Evidence

Required:

- Import planning is visible as an `agent_flow.py` card and performs no writes.
- The card shows project-context status, binding status, resolved-policy refs, write targets, and non-effects.
- The generated activation command uses `python -B -m jikuo.agent_flow`, not the lower-level helper.
- Apply refuses without confirmation and approval phrase.
- Approved apply writes the same bounded policy-store artifacts as CORE-23.
- JSON output includes `chat_ready_markdown`.

Validation command:

```powershell
$env:PYTHONPATH='src'
python -B -m unittest tests.agent_flow_tests
python -B -m unittest discover -s tests -p "*_tests.py"
```

## 7. Follow-Up

- Return to `JIKUO-MCP-01` after reviewing / accepting CORE-24.
- Keep the decision about whether self-bootstrap policies enter built-in starter templates suspended until explicit user approval.
