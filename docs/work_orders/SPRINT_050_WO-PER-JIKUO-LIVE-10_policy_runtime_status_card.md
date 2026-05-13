# SPRINT_050_WO-PER-JIKUO-LIVE-10: Policy Runtime Status Card

> **Product meaning**: make policy trigger state visible as a first-class desktop card, so users can see whether rules triggered, which rules triggered, which active rules did not trigger, and what evidence is missing.
> **Kernel compatibility**: reuses existing report-only policy-store status, trigger evaluation, condition evaluation, and evidence checking; it does not add a gate, executor, or new policy kernel semantics.
> **Current slice**: `agent_flow.py propose` appends a `policy_runtime_status` card after policy evaluation for supported events.
> **User scenario**: A desktop Agent user initializes or starts governed JIKUO work and needs the core policy runtime to be visible instead of hidden in structured JSON.
> **Runtime chain**: desktop event -> `agent_flow.py propose` -> active policy evaluation -> policy runtime status card -> same-chat user review.
> **Bridge object**: `jikuo.policy_runtime_status.v0`; `jikuo.agent_flow_card.v0`.

## Product Semantics

JIKUO's core value is not only storing starter policies. It must make policy runtime state perceptible during work.

Every governed proposal should show a compact policy status surface:

- active policy count
- triggered policy count
- triggered policy refs and titles
- non-triggered active policy refs and compact reasons when known
- required action count
- evidence status count
- missing evidence count and missing evidence types
- lightweight feedback options count

This is a visibility slice. It does not decide whether work may proceed.

## Scope

In scope:

- add a visible `policy_runtime_status` card to `agent_flow.py propose`
- keep existing top-level `policy_context`, `triggered_policies`, `required_actions`, `evidence_status`, and `missing_evidence_reports`
- summarize non-triggered active policies from condition reports where possible
- add regression tests that the card exists for active policy stores and starter-init proposals

Out of scope:

- automatic gate enforcement
- automatic policy action execution
- frontend UI
- MCP wrapper implementation
- changing starter policy semantics
- persisting policy feedback automatically

## Scenario-Chain-Atom Registration Evidence

Scenario chain:

- chain_id: `policy_runtime_visibility`
- user scenario: a desktop Agent user wants to see whether JIKUO rules actually triggered during a governed task
- operation chain: agent invokes `agent_flow.py propose` -> policy store is inspected -> active policies are evaluated -> policy runtime card is appended -> user sees triggered and non-triggered policy state in chat

Registered atoms:

- `CAP-LIVE-DESKTOP-POLICY-EVAL-01`
- `CAP-POLICY-STORE-STATUS-01`
- `CAP-POLICY-TRIGGER-EVALUATE-01`
- `CAP-POLICY-CONDITION-EVALUATOR-01`
- `CAP-POLICY-EVIDENCE-CHECK-01`
- `CAP-POLICY-RUNTIME-STATUS-CARD-01`

Evidence:

- This work order declares the scenario chain and atom list.
- `jikuo_productization_task_map.md` registers the same chain and new runtime-status card atom.
- `agent_flow_tests.py` asserts `policy_runtime_status` appears in proposal cards.

## Acceptance Evidence

Required:

- `agent_flow.py propose --event task_start` against an active policy-store fixture includes a `policy_runtime_status` card.
- The card reports active policy count, triggered policy count, non-triggered policy count, and missing evidence count.
- `agent_flow.py propose --event initialize_jikuo` against a fresh project includes a `policy_runtime_status` card showing missing policy store and zero active policies.
- Existing proposal cards remain first in `cards`, so existing desktop proposal surfaces do not break.
- Proposal mode remains no-write.

Validation command:

```powershell
$env:PYTHONPATH='src'
python -B -m unittest tests.agent_flow_tests
python -B -m unittest discover -s tests -p "*_tests.py"
```
