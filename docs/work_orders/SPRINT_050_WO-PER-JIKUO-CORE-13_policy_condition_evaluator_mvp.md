# SPRINT_050_WO-PER-JIKUO-CORE-13: Policy Condition Evaluator MVP

> **Date**: 2026-05-12
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / configurable rule kernel / policy condition evaluation
> **Parent direction**: `JIKUO` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: configurable_rule_kernel
> **Current slice is not**: packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: evaluates a small deterministic subset of policy `conditions` before projecting required actions; does not execute actions, write policies, auto-persist evidence, or promote gates
> **Deferred kernel backlog refs**: `CAP-POLICY-STORE-WRITE-01`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`; `CAP-MCP-TOOL-01`; `CAP-CODEX-SKILL-01`; guarded `agent_flow.py apply`
> **Preceded by**: CORE-09 exact lifecycle trigger evaluator; CORE-10 evidence checker MVP; CORE-12 evidence ingestion MVP; FLOW-02 Desktop App Primary Operating Loop.
> **Current slice**: `policy_store.py evaluate` and `agent_flow.py propose` accept explicit task metadata (`--task-type`, `--jikuo-layer`, `--changed-path`, `--added-path`) and evaluate matching policy conditions in report-only mode.
> **User scenario**: A Codex / Claude desktop APP user has active project policies that should fire only for certain task classes, JIKUO layers, or changed file surfaces.
> **Runtime chain**: lifecycle event -> active policy trigger -> deterministic condition evaluation -> triggered policy / required action projection -> evidence status projection -> no durable write.
> **Canonical source**: `jikuo_configurable_rule_trigger_policy.md`, `jikuo_rule_action_evidence_model.md`, `jikuo_policy_aware_agent_flow_contract.md`, CORE-09 / CORE-10 / CORE-12 runner slices, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.policy_trigger_eval_report.v0`; `jikuo.agent_flow_proposal.v1`; policy `conditions` records.
> **Consumer projection**: Codex / Claude desktop APP chat cards, future MCP response, future Skill / Plugin wrapper, future frontend audit surfaces.
> **Lifecycle**: exact lifecycle trigger evaluator -> condition evaluator MVP -> later broader condition vocabulary / policy write mode / MCP.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

This slice makes policies less blunt.

Before this slice, an active policy could fire on an exact lifecycle event such as `task_start`. After this slice, a policy can say:

- fire on `task_start`
- only when `task_type` is `work_order_delivery`
- only when `jikuo_layer` is `configurable_rule_kernel`
- only when a changed path matches `docs/jikuo/**`

Visible business value:

- project rules become more precise without relying on the agent's memory
- unrelated tasks are less likely to receive irrelevant governance obligations
- ambiguous condition inputs become `review_required`, not silent success
- ordinary desktop flow remains no-write and report-only

---

## 2. JIKUO Layer Boundary

Current layer:

- `configurable_rule_kernel`

This slice is allowed to:

- extend `tools/jikuo/policy_store.py`
- extend `tools/jikuo/agent_flow.py`
- extend `tools/jikuo/policy_store_tests.py`
- extend `tools/jikuo/agent_flow_tests.py`
- add a fixture with an active policy using `conditions`
- support `task_type_is`
- support `jikuo_layer_is`
- support `changed_path_matches`
- support `added_path_matches`
- expose `condition_reports` in JSON and Markdown proposal output
- add `CAP-POLICY-CONDITION-EVALUATOR-01` atom trace
- update task map, execution mounts, loop composition, Sprint index, and policy-aware docs

This slice is not allowed to:

- write policy files
- create or update task sessions
- execute policy actions
- auto-persist evidence
- infer product-output quality
- evaluate user mood or domain-content quality
- implement compound predicates, checker-result conditions, document-mount presence, work-order field parsing, or approval-event conditions
- install Skill / MCP / Plugin / frontend / gate behavior

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- consuming the existing `conditions` vocabulary from CORE-05
- treating conditions as trigger narrowing, not required evidence
- keeping unsupported or missing-input conditions as `review_required`
- projecting condition reports separately from triggered policies and evidence status
- only projecting required actions after all configured conditions match
- keeping condition evaluation report-only
- keeping policy store writes and enforcement promotion deferred

---

## 4. Deferred Kernel Backlog

Still deferred:

- `CAP-POLICY-STORE-WRITE-01`: guarded policy proposal / approved-policy write mode
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`: broader checker composition and report ingestion
- compound conditions such as `all`, `any`, and `not`
- document-mount presence conditions
- work-order metadata / section parsing conditions
- checker-result conditions
- approval-event conditions
- guarded `agent_flow.py apply`
- Skill / MCP / Plugin / frontend / gate adapters

---

## 5. Scope

Implemented:

- `policy_store.py evaluate --task-type ... --jikuo-layer ... --changed-path ... --added-path ...`
- `agent_flow.py propose --task-type ... --jikuo-layer ... --changed-path ... --added-path ...`
- condition reports for matched, not-matched, and review-required states
- positive fixture where all conditions match and the policy triggers
- negative fixture coverage where a condition misses and the policy does not trigger
- missing-context fixture coverage where conditions require review and the policy does not trigger
- Markdown proposal section for condition reports
- `CAP-POLICY-CONDITION-EVALUATOR-01` atom trace

---

## 6. Out Of Scope

Not implemented:

- policy write mode
- automatic condition inference from task prose
- compound predicates
- checker-result condition ingestion
- document-mount condition evaluation
- action execution
- automatic evidence persistence
- guarded `agent_flow.py apply`
- MCP / Skill / Plugin / frontend packaging
- gates or blocking enforcement

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-09_policy_trigger_evaluator_mvp.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-10_policy_evidence_checker_mvp.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-12_policy_evidence_ingestion_mvp.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `policy_store_tests.py` verifies matched, not-matched, and review-required condition states.

`integration`:

- limited; `agent_flow_tests.py` verifies condition reports are projected through desktop proposal composition.

`workflow / orchestration`:

- required; Markdown proposal must show condition reports, policy trigger result, evidence status, and no-write boundary.

`semantic regression`:

- N/A because this slice governs process policy conditions, not product-output content or narrative runtime behavior.

`smoke`:

- run adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify the fixture project does not create task-session files.

`human governance review`:

- required; user reviews whether the first condition vocabulary is understandable and sufficiently bounded before policy write mode, MCP, Skill, guarded apply, or gate work.

---

## 9. Delivery Criteria

- Matching conditions produce `condition_reports` with `status: matched`.
- Matching conditions allow the lifecycle-triggered policy to project required actions.
- Non-matching conditions prevent required-action projection.
- Missing condition context produces `review_required`, not silent success.
- `agent_flow.py propose` includes `CAP-POLICY-CONDITION-EVALUATOR-01`.
- `agent_flow.py propose` remains no-write.
- Tests and checker smoke pass.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts the first condition vocabulary as intentionally small
- tests pass
- checker smoke passes
- no unapproved task-session or policy write occurs
- policy write adapter, broader condition vocabulary, Skill, MCP, Plugin, frontend, guarded apply, and gate work remain explicitly deferred

Do not proceed to policy write mode, guarded `agent_flow.py apply`, Skill, MCP, Plugin, frontend, or gate work until this condition evaluator slice is accepted or revised.

---

## 11. Verification Log

Commands run so far:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/task_session_cards_tests.py
python -B tools/jikuo/project_state_tests.py
python -B tools/jikuo/policy_store.py evaluate --event task_start --project-root tools/jikuo/fixtures/policy_store_condition_project --task-type work_order_delivery --jikuo-layer configurable_rule_kernel --changed-path docs/jikuo/work_orders/SPRINT_050_probe.md --format json
python -B tools/jikuo/agent_flow.py propose --event task_start --task-title "Condition Probe" --project-root tools/jikuo/fixtures/policy_store_condition_project --task-type work_order_delivery --jikuo-layer configurable_rule_kernel --changed-path docs/jikuo/work_orders/SPRINT_050_probe.md --format markdown
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-13_policy_condition_evaluator_mvp.md --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-13_policy_condition_evaluator_mvp.md
git diff --check -- tools/jikuo/policy_store.py tools/jikuo/agent_flow.py tools/jikuo/policy_store_tests.py tools/jikuo/agent_flow_tests.py docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-13_policy_condition_evaluator_mvp.md docs/jikuo/governance/jikuo_productization_task_map.md docs/jikuo/governance/jikuo_execution_mounts.md docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md
```

Result:

- `policy_store_tests.py`: passed; 13 tests
- `agent_flow_tests.py`: passed; 7 tests
- `task_session_tests.py`: passed; 24 tests
- `task_session_cards_tests.py`: passed; 4 tests
- `project_state_tests.py`: passed; 11 tests
- `policy_store.py evaluate` smoke returned `policy_condition_eval_status: checked`, three matched condition reports, one triggered policy, and one required action.
- `agent_flow.py propose` smoke rendered `Condition Reports` in Markdown and included `CAP-POLICY-CONDITION-EVALUATOR-01`; proposal remained no-write.
- checker smoke passed in report-only mode; `R-006` fields/sections OK, `R-012` Sprint index document present with manual declaration review, and `R-013` JIKUO layer/kernel fields/sections OK with manual declaration review.
- `git diff --check` passed; only line-ending warnings were reported.
- root `.jikuo/task_sessions/`, root `.jikuo/policies/`, and fixture `.jikuo/task_sessions/` remained absent.
