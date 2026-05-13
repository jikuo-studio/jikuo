# SPRINT_050_WO-PER-JIKUO-AGENT-08: Policy-Aware Agent Flow Fallback

> **Date**: 2026-05-11
> **Status**: Implemented, ready for user review
> **Primary sprint**: Sprint 050 / JIKUO productization incubation
> **Task type**: productization / desktop operating skeleton / implementation slice
> **Parent direction**: `机括` AI-primary process governance kernel; current engineering-governance application track
> **JIKUO layer**: desktop_operating_skeleton
> **Current slice is not**: configurable_rule_kernel; packaging_surface; frontend_surface; gate_enforcement
> **Kernel compatibility**: implements the AGENT-07 fallback projection without reading policy stores, evaluating policies, checking evidence, or creating policy sidecars; keeps CORE-05 / CORE-06 / CORE-07 semantics deferred and visible
> **Deferred kernel backlog refs**: `CAP-POLICY-STORE-ADAPTER-01`; `CAP-POLICY-AWARE-FLOW-IMPLEMENTATION-01`; `CAP-POLICY-EVIDENCE-CHECKER-01`; `JIKUO-CHECKER-02_policy_execution_evidence_checker`
> **Preceded by**: AGENT-05 local deterministic no-write runner; AGENT-07 policy-aware proposal contract; CORE-05 configurable rule trigger policy; CORE-06 rule action/evidence model; CORE-07 policy store/configuration flow.
> **Current slice**: `agent_flow.py propose` emits a policy-aware v1 proposal envelope with explicit unavailable policy context and empty policy/action/evidence arrays; no policy evaluation, no store adapter, no evidence checker, no guarded write.
> **User scenario**: A Codex / Claude desktop APP user invokes JIKUO in chat and needs the returned proposal to say clearly whether configurable policy execution is active or unavailable, without needing to inspect CLI internals.
> **Runtime chain**: desktop event -> `agent_flow.py propose` -> baseline no-write atom composition -> policy-unavailable fallback projection -> Markdown / JSON proposal -> same-chat user review.
> **Canonical source**: AGENT-07 contract, `jikuo_policy_aware_agent_flow_contract.md`, CORE-05 / CORE-06 / CORE-07 contracts, AGENT-05 runner, FLOW-02 Desktop App Primary Operating Loop.
> **Bridge object**: `jikuo.agent_flow_proposal.v1`; `policy_context`; `triggered_policies`; `required_actions`; `evidence_status`; `missing_evidence_reports`.
> **Consumer projection**: Codex / Claude desktop APP chat cards, future MCP response, future Skill / Plugin wrapper, future frontend run-control and audit surfaces.
> **Lifecycle**: accepted projection contract -> fallback implementation -> user review -> later full store/evaluator/checker implementation.
> **Testing layers**: unit, workflow/orchestration, smoke, checker smoke, human governance review.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. Product Meaning

> **中文注释**：这一步不是“真正执行用户规则”，而是让桌面 APP 卡片不会假装规则已经执行。它把“规则内核还没接入”变成稳定字段，方便用户、Agent、未来 UI 和 MCP 都看见。

Before this slice, `agent_flow.py propose` could produce a governed task proposal, but policy-aware fields existed only as a contract.

After this slice, every proposal can explicitly report:

- policy store status is unavailable
- policy evaluation was not run
- no active policies were triggered
- no policy-required actions were produced
- no policy evidence was checked

Visible business value:

- desktop users get honest process status in the same chat
- future UI / MCP / Skill work can rely on a stable v1 envelope
- missing policy infrastructure is not mistaken for successful policy execution
- the skeleton remains compatible with the later configurable-rule kernel

---

## 2. JIKUO Layer Boundary

Current layer:

- `desktop_operating_skeleton`

This slice is allowed to:

- update `tools/jikuo/agent_flow.py`
- update `tools/jikuo/agent_flow_tests.py`
- emit `jikuo.agent_flow_proposal.v1`
- include `previous_schema: jikuo.agent_flow_proposal.v0`
- include policy-aware fallback fields
- render policy context in Markdown
- verify no `.jikuo/policies/` or `.jikuo/task_sessions/` root is created by propose mode
- update task map, Sprint index, execution mounts, and skeleton/kernel backlog notes

This slice is not allowed to:

- read `.jikuo/policies/`
- create `.jikuo/policies/`
- evaluate policy triggers
- execute required policy actions
- check policy evidence
- persist policy evidence
- create `.jikuo/task_sessions/`
- implement guarded `agent_flow.py apply`
- install Skill / MCP / Plugin / frontend / gate behavior
- change runtime narrative-engine behavior
- evaluate product-output quality

---

## 3. Kernel Compatibility

This slice preserves kernel compatibility by:

- using the AGENT-07 proposal fields without redefining CORE-05 / CORE-06 / CORE-07 semantics
- exposing policy infrastructure status as `unavailable`
- exposing evaluation status as `not_evaluated`
- returning empty policy/action/evidence arrays rather than fabricating policy results
- keeping `agent_flow.py propose` report-only and no-write
- leaving store adapter, evaluator, and evidence checker implementation to later kernel work

---

## 4. Deferred Kernel Backlog

Still deferred:

- `CAP-POLICY-STORE-ADAPTER-01`: approved policy persistence implementation and store adapter
- `CAP-POLICY-AWARE-FLOW-IMPLEMENTATION-01`: full policy-aware runner with store discovery and trigger evaluation
- `CAP-POLICY-EVIDENCE-CHECKER-01`: policy execution evidence checker
- `JIKUO-CHECKER-02_policy_execution_evidence_checker`
- policy proposal / missing-evidence card renderer
- task-session policy evidence persistence
- Skill / MCP / Plugin / frontend / gate adapters

---

## 5. Scope

This work order implements:

- `agent_flow.py` proposal schema bump to `jikuo.agent_flow_proposal.v1`
- `policy_context` fallback projection
- empty `triggered_policies`, `required_actions`, `evidence_status`, and `missing_evidence_reports` arrays
- Markdown `Policy Context` rendering
- focused regression assertions in `agent_flow_tests.py`
- minimal planning/index updates for the new capability

---

## 6. Out Of Scope

This work order does not implement:

- policy store discovery
- policy trigger evaluation
- action execution
- evidence checking
- evidence persistence
- policy sidecar storage
- guarded `apply`
- Skill / MCP / Plugin / frontend packaging
- gate enforcement
- narrative runtime changes

---

## 7. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md`
- `docs/jikuo/governance/jikuo_configurable_rule_trigger_policy.md`
- `docs/jikuo/governance/jikuo_rule_action_evidence_model.md`
- `docs/jikuo/governance/jikuo_policy_store_configuration_flow.md`
- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-07_policy_aware_agent_flow_proposal.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 8. Testing Governance Declaration

`unit`:

- required; `agent_flow_tests.py` verifies v1 schema and fallback policy fields.

`integration`:

- limited; no external store / MCP / Skill / UI integration exists in this slice.

`workflow / orchestration`:

- required; proposal output must still compose no-write atoms and now include policy fallback context.

`semantic regression`:

- N/A because this slice governs process projection, not product-output content or narrative runtime behavior.

`smoke`:

- run `agent_flow_tests.py` and adjacent JIKUO helper tests.
- run report-only checker against this work order and updated docs.
- verify no `.jikuo/policies/` and no `.jikuo/task_sessions/` root records are created.

`human governance review`:

- required; user reviews whether the fallback output is honest and useful before full policy execution work begins.

---

## 9. Delivery Criteria

- `agent_flow.py` emits `jikuo.agent_flow_proposal.v1`.
- Proposal JSON includes `previous_schema`.
- Proposal JSON includes `policy_context`.
- Proposal JSON includes empty policy/action/evidence/missing-evidence arrays.
- Markdown proposal includes `Policy Context`.
- Fallback reports `policy_store_status: unavailable`.
- Fallback reports `policy_eval_status: not_evaluated`.
- Tests verify no policy or task-session sidecar root is created.
- Task map registers `JIKUO-AGENT-08` and the implemented fallback atom.
- Execution mounts and Sprint index reflect the new current runner state.
- Report-only checker validation passes.

---

## 10. Acceptance Gate

This slice may be accepted only if:

- user accepts that this is fallback visibility, not real policy execution
- test suite passes
- checker smoke passes
- no `.jikuo/policies/` or `.jikuo/task_sessions/` directory is created by this slice
- future full policy implementation remains explicitly deferred

Do not proceed to policy store adapter, policy trigger evaluator, policy evidence checker, guarded `apply`, Skill, MCP, Plugin, frontend, or gate work until this fallback slice is accepted or revised.

---

## 11. Verification Log

Commands run:

```powershell
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/task_session_cards_tests.py
python -B tools/jikuo/task_session_tests.py
python -B tools/jikuo/project_state_tests.py
```

Result:

- `agent_flow_tests.py`: passed; 3 tests
- `task_session_cards_tests.py`: passed; 4 tests
- `task_session_tests.py`: passed; 24 tests
- `project_state_tests.py`: passed; 11 tests

```powershell
python -B tools/jikuo/agent_flow.py propose --event task_start --task-title "Policy Fallback Probe" --project-root tools/jikuo/fixtures/task_session_ready_project --format markdown
```

Result:

- returned a same-chat Markdown proposal
- included `Policy Context`
- reported `Policy store status: unavailable`
- reported `Policy eval status: not_evaluated`
- reported `Writes performed: false`

```powershell
Test-Path -Path .jikuo\policies
Test-Path -Path .jikuo\task_sessions
```

Result:

- both returned `False`

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-08_policy_aware_agent_flow_fallback.md --changed tools/jikuo/agent_flow.py --changed tools/jikuo/agent_flow_tests.py --changed docs/jikuo/governance/jikuo_productization_task_map.md --changed docs/jikuo/governance/jikuo_execution_mounts.md --changed docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md --changed docs/jikuo/governance/jikuo_policy_aware_agent_flow_contract.md --changed docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-AGENT-08_policy_aware_agent_flow_fallback.md
```

Result:

- registry validation passed
- triggered `R-006`, `R-012`, and `R-013`
- `R-006` required work-order fields and sections reported `OK`
- `R-012` Sprint index document requirement reported `OK`; manual `sprint_index_entry` declaration remained `REVIEW`, as expected for report-only manual evidence
- `R-013` layer / kernel fields and sections reported `OK`; manual `skeleton_kernel_boundary_declaration` remained `REVIEW`, as expected for report-only manual evidence

---

## 12. Current Acceptance Record

Decision:

- implemented, ready for user review

Still not approved:

- policy store adapter
- policy trigger evaluator
- policy execution evidence checker
- policy evidence persistence
- guarded `agent_flow.py apply`
- Skill / MCP / Plugin packaging
- frontend implementation
- gate or blocking enforcement
- `.codex/AGENTS.md` promotion
- runtime narrative-engine changes
