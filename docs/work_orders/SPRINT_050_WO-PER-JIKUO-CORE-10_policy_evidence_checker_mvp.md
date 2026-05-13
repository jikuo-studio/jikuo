# SPRINT_050_WO-PER-JIKUO-CORE-10: Policy Evidence Checker MVP

> **Date**: 2026-05-12
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / implementation slice
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: desktop_operating_skeleton; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: implements only report-only evidence matching for triggered project policies; does not execute actions, persist evidence, write policy/task-session state, or promote gates
> **Deferred kernel backlog refs**: `CAP-POLICY-CONDITION-EVALUATOR-01`; `CAP-POLICY-STORE-WRITE-01`; `CAP-POLICY-EVIDENCE-PERSIST-01`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`
> **Preceded by**: CORE-06 rule action/evidence model; CORE-07 policy store/configuration flow; CORE-08 read-only policy store inspection; CORE-09 policy trigger evaluator MVP.
> **Current slice**: `policy_store.py evaluate --event <event>` can match `required_evidence` against supplied inline produced evidence; PowerShell-friendly evidence flags are available for manual smoke; `agent_flow.py propose` supplies runner-produced `card_rendered` evidence for task-start proposal cards.
> **User scenario**: A Codex / Claude desktop APP user starts a governed task and needs JIKUO to show not only which policy triggered, but whether the proposal card itself satisfies the policy's required evidence.
> **Runtime chain**: desktop event -> `agent_flow.py propose` -> policy-store inspection -> exact trigger evaluation -> required action projection -> runner-produced evidence -> report-only evidence matching -> same-chat user review.
> **Canonical source**: `jikuo_rule_action_evidence_model.md`, `jikuo_policy_aware_agent_flow_contract.md`, CORE-09 trigger evaluator MVP, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.policy_trigger_eval_report.v0.policy_evidence_check_status`; `jikuo.agent_flow_proposal.v1.evidence_status`; `jikuo.missing_evidence_report.v0`.
> **Consumer projection**: Codex / Claude desktop APP chat cards, future MCP response, future Skill / Plugin wrapper, future frontend run-control and audit surfaces.
> **Lifecycle**: trigger evaluator MVP -> evidence checker MVP -> user review -> later evidence persistence / condition evaluator / write adapter implementation.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

This slice moves JIKUO from "a rule triggered and required an action" to "the system can report whether visible process evidence satisfies that required action."

Visible business value:

- missing required evidence becomes explicit instead of silent
- runner-produced evidence can satisfy a policy requirement without durable writes
- desktop proposal cards can show evidence status and missing evidence reports
- the user can distinguish "action required" from "evidence already present"

Important boundary:

- evidence matching is deterministic and report-only
- no evidence is persisted
- no action is executed because evidence is missing
- no missing evidence report blocks delivery by itself
- no gate behavior is introduced

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- extend `tools/jikuo/policy_store.py`
- extend `tools/jikuo/policy_store_tests.py`
- extend `tools/jikuo/agent_flow.py`
- extend `tools/jikuo/agent_flow_tests.py`
- project policy `required_evidence`
- match supplied inline `produced_evidence`
- generate `evidence_status`
- generate `missing_evidence_reports`
- let `agent_flow.py propose` supply no-write `card_rendered` evidence for rendered task-start cards
- update task map, execution mounts, loop composition, Sprint index, and policy-aware contracts

This slice is not allowed to:

- execute policy actions
- persist evidence to task sessions
- write approved policies or proposals
- evaluate advanced policy conditions
- create `.jikuo/policies/`
- create `.jikuo/task_sessions/`
- implement guarded `agent_flow.py apply`
- install Skill / MCP / Plugin / frontend / gate behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- consuming CORE-06 `required_evidence` vocabulary
- keeping evidence requirements distinct from produced evidence
- using `card_rendered` evidence only when the runner actually renders a card
- reporting missing evidence as report-only review information
- preserving write/effect/non-effect boundaries
- keeping persistence and gates deferred

---

## 4. Deferred Kernel Backlog

Still deferred:

- `CAP-POLICY-CONDITION-EVALUATOR-01`: non-lifecycle conditions such as path matches, document mounts, work-order metadata, and checker results
- `CAP-POLICY-EVIDENCE-PERSIST-01`: guarded evidence persistence into task-session sidecars
- `CAP-POLICY-STORE-WRITE-01`: guarded policy proposal / approved-policy write mode
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`: broader checker composition and report ingestion
- policy proposal card renderer
- task-session policy snapshot persistence
- Skill / MCP / Plugin / frontend / gate adapters

---

## 5. Scope

Implemented:

- `policy_evidence_check_status`
- `evidence_status` projection
- `missing_evidence_reports` projection
- inline `--produced-evidence-json` support for `policy_store.py evaluate`
- PowerShell-friendly inline evidence flags for manual smoke
- deterministic evidence matching by evidence type and action/action type
- `agent_flow.py` task-start `card_rendered` evidence production
- `CAP-POLICY-EVIDENCE-CHECK-01` atom trace
- Markdown sections for evidence status and missing evidence reports
- tests for missing and satisfied card-rendered evidence

---

## 6. Out Of Scope

Not implemented:

- evidence persistence
- evidence ingestion from task-session sidecars
- checker-result parsing
- condition evaluation beyond lifecycle event exact match
- action execution
- policy writes
- guarded `apply`
- MCP / Skill / Plugin / frontend packaging
- gates or blocking enforcement

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-09_policy_trigger_evaluator_mvp.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `policy_store_tests.py` verifies missing evidence and satisfied inline evidence.

`integration`:

- required; `agent_flow_tests.py` verifies `agent_flow.py propose` supplies `card_rendered` evidence and projects evidence status.

`workflow / orchestration`:

- required; Markdown proposal must show evidence check status, evidence status, missing evidence count, and no-write boundaries.

`semantic regression`:

- N/A because this slice governs process evidence, not product-output content or narrative runtime behavior.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify root `.jikuo/policies/`, root `.jikuo/task_sessions/`, and fixture task sessions are not created.

`human governance review`:

- required; user reviews whether evidence matching is understandable and honest before evidence persistence or gates.

---

## 9. Delivery Criteria

- `policy_store.py evaluate --event task_start` reports missing `card_rendered` evidence when no produced evidence is supplied.
- `policy_store.py evaluate --event task_start --produced-evidence-json ...` or equivalent evidence flags report evidence status `ok` for matching card evidence.
- `agent_flow.py propose --event task_start` supplies runner-produced card evidence and reports evidence status `ok`.
- `CAP-POLICY-EVIDENCE-CHECK-01` appears in atom trace.
- Missing evidence reports remain report-only.
- No durable write is performed.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts that evidence matching is deterministic evidence/action matching, not AI judgment
- tests pass
- checker smoke passes
- no root `.jikuo/policies/` or `.jikuo/task_sessions/` directory is created
- no fixture task-session directory is created
- evidence persistence, condition evaluator, policy write adapter, Skill, MCP, Plugin, frontend, and gate work remain explicitly deferred

Do not proceed to evidence persistence, condition evaluation, policy write mode, guarded `agent_flow.py apply`, Skill, MCP, Plugin, frontend, or gate work until this evidence checker MVP is accepted or revised.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
```

Result:

- `policy_store_tests.py`: passed; 8 tests
- `agent_flow_tests.py`: passed; 4 tests

Additional checker and adjacent helper verification should be recorded before final acceptance.
