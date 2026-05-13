# SPRINT_050_WO-PER-JIKUO-CORE-01: Structured Result Model

> **Date**: 2026-05-04  
> **Status**: Accepted by user; upstream structured result model for `JIKUO-CORE-02`  
> **Primary sprint**: Sprint 050 / contract-first hardening incubation  
> **Task type**: productization / core data model / governance documentation work order  
> **Parent direction**: `机括` AI-primary process governance productization; current engineering-governance application track  
> **Preceded by**: `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`; `SPRINT_050_WO-PER-WORKTREE-05D_local_audit_checker_report_only.md`  
> **Current slice**: Part 3 accepted; `JIKUO-CORE-02` may use this result model and JSON output as upstream input  
> **User scenario**: A Codex / Claude desktop APP user needs the same triggered governance obligations to appear consistently in chat cards, local reports, handoff summaries, and future frontend views.  
> **Runtime chain**: Rule registry + explicit task inputs -> report-only checker semantics -> structured result envelope -> desktop-agent card / auxiliary CLI report / future frontend projection -> user review or approval.  
> **Canonical source**: accepted `JIKUO-AGENT-00` interaction contract and `WORKTREE-05D` report-only checker semantics.  
> **Bridge object**: `JikuoResultEnvelopeV0`.  
> **Consumer projection**: default text report, optional JSON output, future desktop cards, auxiliary CLI bridge, handoff summaries, and frontend views.  
> **Lifecycle**: result schema v0; future field changes require schema-version supersession and compatibility review.  
> **Testing layers**: documentation review, workflow/orchestration review, report-only checker smoke, human governance review.  
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 产品口径

> **中文注释**：这一片回答“机括的检查结果到底长什么样”。没有这个对象，桌面卡片、CLI、前端会各自解释文本报告，迟早分叉。

The product-facing problem is that `机括` now has:

- a rule registry
- a report-only checker
- a desktop-agent-first interaction contract
- a future frontend direction

But the result of a governance check is still mainly a human-readable text report.

If the project moves forward without a structured result model:

- Codex / Claude desktop cards may parse prose differently
- auxiliary CLI reports may drift from future frontend state
- handoff summaries may omit evidence status or approval boundaries
- later gates may accidentally treat report-only warnings as blocking decisions
- users may see inconsistent governance state across surfaces

Expected visible change after this work order is accepted:

- future `机括` consumers can share one result object
- desktop-agent cards can render triggered obligations without inventing their own schema
- CLI / report / frontend surfaces can stay projections of the same canonical result
- exit-code and blocking semantics remain explicitly report-only until a later approved gate task

---

## 2. 技术口径

> **中文注释**：本工单只定义数据契约，不改 checker 代码。它给后续 JSON 输出、桌面卡片和前端打地基。

Mainline changed:

- this work order document
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md` acceptance record

Mainline explicitly not changed:

- `tools/audit/check_rule_registry.py`
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- runtime narrative engine
- Codex / Claude adapters
- CLI commands
- frontend implementation
- hooks, CI, task-stop gates, or blocking enforcement
- `.codex/AGENTS.md`

Canonical source:

- `rule_registry.yaml` for rule identity, trigger surfaces, evidence requirements, enforcement level, and automation phase
- current `check_rule_registry.py` report semantics for validation status, triggered obligations, and evidence check vocabulary
- accepted `JIKUO-AGENT-00` for desktop-agent-first projection requirements

Bridge object:

- conceptual `JikuoResultEnvelopeV0`

Consumer projection:

- Codex / Claude desktop-agent cards
- auxiliary CLI report / future JSON output
- handoff summary
- future frontend configuration, control, and audit views

Lifecycle:

- explicit task input is collected
- registry is loaded and validated
- triggered obligations are evaluated
- result envelope is produced
- one or more projections render the envelope
- user review or approval may create a separate approval record

Rollback / supersession:

- because Part 1 does not implement code, rollback is doc-level supersession
- later implementation must declare schema version compatibility and migration behavior
- future blocking gate work must not reuse this model as implicit approval to enforce failures

Propagation surfaces:

- Part 1: documentation only
- Later: checker JSON output, desktop-agent card renderer, auxiliary CLI bridge, frontend

Observability:

- every result must preserve enough fields for a user or agent to answer:
  - which registry was read
  - which inputs were evaluated
  - which rules triggered
  - what evidence was found, missing, or needs review
  - whether any blocking behavior was actually enforced

---

## 3. 对照关系

| Product / governance goal | Structured result responsibility |
|---|---|
| Keep desktop APP as the primary user surface | Result envelope must be renderable as compact chat cards |
| Avoid CLI / frontend drift | CLI, frontend, and chat must project the same envelope |
| Preserve report-only safety | Exit policy separates process exit code from governance severity |
| Make missing evidence visible | Evidence checks have explicit status and message fields |
| Prevent accidental approval writes | Result envelope reports obligations only; approval records are separate objects |
| Support handoff between Codex and Claude | Envelope includes stable identifiers and summary fields suitable for handoff |
| Enable later UI without raw prose parsing | Rule, evidence, declaration, and document checks are structured fields |

---

## 4. Scope

Part 1 defines:

- result envelope shape
- obligation item shape
- evidence check status vocabulary
- severity and automation phase projection
- declaration / manual-review representation
- exit-code policy
- consumer projection rules
- compatibility with the current text-only checker
- testing and acceptance criteria

Part 1 may use JSON-like examples, but it must not implement JSON output.

---

## 5. Out Of Scope

This work order does not:

- implement checker JSON output
- change checker parsing or validation behavior
- change `rule_registry.yaml`
- change `rule_registry.schema.md`
- implement desktop-agent cards
- implement Codex / Claude adapters
- implement CLI commands
- implement frontend UI
- implement approval record storage
- implement hooks, CI, task-stop gates, or blocking enforcement
- change narrative runtime behavior
- define product-output quality evaluation rules

---

## 6. Audit References

Fixed references:

- `.codex/AGENTS.md`
- `docs/scenarios/interactive_novel/testing/TESTING_GOVERNANCE.md`

Dynamic references:

- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`
- `tools/audit/check_rule_registry.py`
- `SPRINT_050_WO-PER-WORKTREE-05C_rule_registry_schema.md`
- `SPRINT_050_WO-PER-WORKTREE-05D_local_audit_checker_report_only.md`
- `SPRINT_050_WO-PER-JIKUO-PRD-01_product_definition.md`
- `SPRINT_050_WO-PER-JIKUO-AGENT-00_agent_native_interaction_contract.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/scenarios/interactive_novel/sprints/SPRINT_050_20260409.md`

---

## 7. Pre-Audit

> **中文注释**：事前审计结论：可以定义 result model；不能把它偷换成 checker JSON 实现或 gate 实现。

Task target:

- define a stable structured result contract for `机括` governance checks

Compliance status:

- aligned with `JIKUO-AGENT-00` because desktop-agent cards need a shared object
- aligned with `05D` because current checker remains report-only
- aligned with `05F` because no blocking gate is introduced
- aligned with product boundary because result status reports engineering-governance evidence, not product-output quality

Required adjustments:

- keep approval records separate from result envelopes
- keep exit-code policy explicit
- use `review` for manual governance review, not product semantic judgment
- stop before implementation

---

## 8. Existing Inputs

> **中文注释**：result model 不是凭空发明；它从当前 checker 文本报告和 registry schema 中抽取稳定字段。

Current checker report already exposes:

- registry path
- registry validation status
- rule count
- input changed paths
- input added paths
- input work order paths
- git pathspecs
- triggered rules
- rule id, title, level, phase
- matched changed paths
- matched added paths
- required context
- required work-order fields
- required sections
- required documents
- declarations
- audit bundle fields
- evidence check lines
- report message
- report-only exit behavior

Current registry schema already defines:

- rule identity
- rule status
- source references
- materialization types
- trigger mode and path patterns
- evidence requirements
- enforcement level
- enforcement phase
- target consumer
- review owner

---

## 9. Result Model Principles

1. Same object, multiple renderers.
2. The result envelope reports; it does not approve.
3. Rule severity and actual enforcement are separate.
4. Report-only obligations must not change process exit code.
5. Manual review status must be explicit, not hidden in prose.
6. Desktop-agent cards should be able to render without parsing terminal text.
7. Future frontend should not need a different interpretation of triggered rules.
8. Unknown future fields should not break older renderers if required v0 fields are present.

---

## 10. Top-Level Result Envelope V0

> **中文注释**：这是概念结构，不是本轮要写入代码的 JSON 输出。

Conceptual shape:

```json
{
  "schema_version": "jikuo.result.v0",
  "kind": "jikuo_rule_audit_result",
  "generated_at": "ISO-8601 timestamp",
  "producer": {
    "name": "check_rule_registry",
    "mode": "report_only",
    "version": "optional"
  },
  "workspace": {
    "root": "optional absolute path",
    "cwd": "optional absolute path"
  },
  "invocation": {
    "changed_paths": [],
    "added_paths": [],
    "work_order_paths": [],
    "git_pathspecs": []
  },
  "registry": {
    "path": "",
    "validation_status": "pass",
    "schema_version": "optional",
    "rule_count": 0,
    "errors": []
  },
  "summary": {
    "triggered_rule_count": 0,
    "obligation_count": 0,
    "missing_evidence_count": 0,
    "review_count": 0,
    "tool_exit_code": 0,
    "governance_blocking_enforced": false
  },
  "obligations": [],
  "declarations": [],
  "messages": [],
  "exit_policy": {}
}
```

Required v0 fields:

- `schema_version`
- `kind`
- `producer`
- `invocation`
- `registry`
- `summary`
- `obligations`
- `exit_policy`

Optional v0 fields:

- `generated_at`
- `workspace`
- `declarations`
- `messages`

---

## 11. Obligation Item V0

Conceptual shape:

```json
{
  "rule_id": "R-006",
  "title": "New work order documents must include required sections",
  "status": "active",
  "level": "blocking",
  "phase": "report_only",
  "matched_paths": {
    "changed": [],
    "added": []
  },
  "required_context": "new_work_order_doc",
  "requirements": {
    "work_order_fields": [],
    "sections": [],
    "documents": [],
    "declarations": [],
    "audit_bundle_fields": []
  },
  "evidence_checks": [],
  "message": "",
  "consumer_hint": "desktop_card"
}
```

Required v0 fields:

- `rule_id`
- `title`
- `level`
- `phase`
- `matched_paths`
- `requirements`
- `evidence_checks`
- `message`

Optional v0 fields:

- `status`
- `required_context`
- `consumer_hint`
- `source_refs`

---

## 12. Evidence Check V0

Conceptual shape:

```json
{
  "kind": "work_order_field",
  "target": "Status",
  "status": "ok",
  "detail": "OK field: Status",
  "source_path": "optional path",
  "review_owner": "optional"
}
```

Allowed `kind` values:

- `registry_validation`
- `work_order_field`
- `work_order_section`
- `required_document`
- `declaration`
- `audit_bundle_field`
- `manual_review`
- `tool_error`

Allowed `status` values:

- `ok`
- `missing`
- `review`
- `not_applicable`
- `error`

Status meanings:

| Status | Meaning |
|---|---|
| `ok` | Deterministic evidence was found |
| `missing` | Required deterministic evidence was not found |
| `review` | The obligation requires human governance review or later structured evidence |
| `not_applicable` | The evidence type does not apply to this invocation |
| `error` | The tool could not evaluate the evidence reliably |

`review` must not mean product-output quality judgment. It means engineering-governance evidence cannot be fully resolved by the current tool.

---

## 13. Severity, Phase, And Exit Policy

> **中文注释**：这里防止“规则级别是 blocking”被误读成“当前命令已经会阻塞”。

Rule severity comes from registry `enforcement.level`:

- `warning`
- `blocking`
- `review_required`

Automation phase comes from registry `enforcement.phase`:

- `report_only`
- `local_gate_candidate`
- `pre_commit_candidate`
- `ci_candidate`

Exit policy v0:

```json
{
  "tool_exit_code": 0,
  "governance_blocking_enforced": false,
  "triggered_obligations_change_exit_code": false,
  "validation_errors_change_exit_code": true,
  "phase": "report_only"
}
```

Rules:

- triggered obligations do not change the process exit code while phase is `report_only`
- registry parse or validation errors may still produce tool failure
- future gate work must explicitly supersede this policy before using obligation severity as a blocking exit code
- desktop cards must show both `level` and `phase` when the distinction matters

---

## 14. Declaration And Manual Review Representation

Declarations are statements that the current tool can surface but cannot fully verify.

Example:

```json
{
  "id": "sprint_index_entry",
  "status": "review",
  "message": "manual or later structured evidence check",
  "required_by_rule_id": "R-012"
}
```

Rules:

- declarations must be attached to the rule that requires them
- declarations must not be silently converted into `ok`
- desktop cards should display `review` items separately from `missing` items
- future frontend may let the user attach review evidence, but that is not part of Part 1

---

## 15. Consumer Projection Rules

Desktop-agent card projection:

- show summary first
- group obligations by rule id
- show `level` and `phase` together
- show missing evidence and review items plainly
- never imply user approval from result generation

Auxiliary CLI / report projection:

- may render text or JSON later
- must not invent fields that conflict with the envelope
- should preserve full obligation detail for debugging

Future frontend projection:

- may group by task, rule, evidence status, or time
- must preserve canonical rule ids and evidence statuses
- must not treat `review` as `ok`

Handoff projection:

- should include summary, triggered rule ids, missing evidence count, review count, and whether enforcement was applied
- should omit bulky path lists unless needed for the next agent

---

## 16. Compatibility With Current Text Checker

> **中文注释**：当前 checker 不需要改；这里先把文本报告里的稳定语义映射出来。

| Current text report concept | Result envelope field |
|---|---|
| `registry: ...` | `registry.path` |
| `validation: PASS` | `registry.validation_status` |
| `rules: N` | `registry.rule_count` |
| `input changed paths` | `invocation.changed_paths` |
| `input added paths` | `invocation.added_paths` |
| `input work order paths` | `invocation.work_order_paths` |
| `git pathspecs` | `invocation.git_pathspecs` |
| `triggered rules: N` | `summary.triggered_rule_count` |
| `[REPORT] R-006 ...` | `obligations[].rule_id/title` |
| `level: blocking` | `obligations[].level` |
| `phase: report_only` | `obligations[].phase` |
| `matched changed paths` | `obligations[].matched_paths.changed` |
| `matched added paths` | `obligations[].matched_paths.added` |
| `required sections` | `obligations[].requirements.sections` |
| `OK field` | `evidence_checks[].status = ok` |
| `REVIEW declaration` | `evidence_checks[].status = review` |
| `report-only: triggered obligations do not change the exit code` | `exit_policy.triggered_obligations_change_exit_code = false` |

---

## 17. Testing Governance Declaration

> **中文注释**：这是核心数据契约文档，不改变 checker 行为，也不改变叙事引擎行为。

Required test layers for this slice:

- `unit`: N/A because no parser, serializer, or checker code is implemented.
- `integration`: N/A because no CLI, frontend, adapter, hook, CI, or runtime integration is implemented.
- `workflow/orchestration`: required by contract review; the model must preserve desktop-agent-first flow and report-only boundaries.
- `semantic regression`: N/A because no product behavior or narrative behavior changes.
- `smoke`: required; run the report-only checker against the new work order path.
- `human semantic review`: N/A for product semantics because this slice does not change product behavior or product content evaluation.
- `human governance review`: required for result vocabulary, exit-policy clarity, and consumer projection safety.

---

## 18. Part 1 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P1-DC-01 | Define product / technical / mapping views | Sections 1, 2, and 3 exist |
| P1-DC-02 | Preserve no-implementation boundary | Sections 4 and 5 exist |
| P1-DC-03 | Define top-level result envelope | Section 10 exists |
| P1-DC-04 | Define obligation item shape | Section 11 exists |
| P1-DC-05 | Define evidence status vocabulary | Section 12 exists |
| P1-DC-06 | Define severity, phase, and exit policy | Section 13 exists |
| P1-DC-07 | Define declaration/manual-review representation | Section 14 exists |
| P1-DC-08 | Define consumer projection rules | Section 15 exists |
| P1-DC-09 | Map current checker text concepts to result fields | Section 16 exists |
| P1-DC-10 | Declare testing-governance layers | Section 17 exists |
| P1-DC-11 | Run report-only checker smoke | Verification log records checker result |

---

## 19. Acceptance Gate For Part 1

> **中文注释**：这是 `JIKUO-CORE-01` 的第一片暂停点。你验收后，才进入 JSON 输出实现或更细的 schema 对齐。

Part 1 is ready for user review when:

- the result envelope is small enough to implement
- desktop-agent, CLI, frontend, and handoff projections can share the same object
- severity and exit-code policy cannot be confused with active blocking gates
- evidence `review` is clearly governance review, not product-output review
- approval records remain outside the result envelope
- no implementation has been added
- checker smoke has been run

Do not continue to checker JSON output implementation, frontend implementation, CLI implementation, adapter implementation, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 1 contract.

---

## 20. Part 1 Verification Log

> **中文注释**：这里记录 Part 1 实际跑过的检查。checker 仍然只是 report-only。

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md
```

Result:

- registry validation passed
- triggered `R-006` and `R-012`
- required fields and sections for `R-006` reported `OK`
- Sprint index document for `R-012` reported `OK`
- `sprint_index_entry` declaration remained `REVIEW`
- exit code `0`
- report-only posture preserved

---

## 29. Part 2 Acceptance Record

> **中文注释**：用户已确认继续，因此 Part 2 的 JSON 输出实现计划可以进入最小代码实现。仍不代表 CLI 包、前端、adapter、gate 或 runtime 改动被批准。

Acceptance:

- user accepted Part 2 by saying `请继续`
- Part 3 may implement optional checker JSON output

Still not accepted:

- standalone `jikuo` CLI package
- desktop-agent card renderer implementation
- Codex / Claude adapter implementation
- frontend implementation
- gate implementation
- `.codex/AGENTS.md` promotion
- Sprint 050 runtime hardening changes under this productization task

---

## 30. Part 3 Implementation Summary

> **中文注释**：Part 3 是第一片真正代码实现，但边界很窄：只给现有 checker 加可选 JSON 输出。

### 产品口径

The accepted result model is now available as an explicit checker output mode.

Visible change:

- existing users can keep using the default text report
- agents and future UI work can request `--format json`
- triggered obligations still do not block work in report-only mode
- JSON output can be parsed without scraping human-readable prose

### 技术口径

Mainline changed:

- `tools/audit/check_rule_registry.py`
- `tools/audit/check_rule_registry_json_output_tests.py`

Mainline explicitly not changed:

- `rule_registry.yaml`
- `rule_registry.schema.md`
- CLI package / command name
- desktop-agent adapter
- frontend
- hook / CI / task-stop gate
- runtime narrative engine

Implemented behavior:

- added `--format text|json`
- default remains `text`
- added `JikuoResultEnvelopeV0` builder helpers
- added JSON renderer with `ensure_ascii=False`
- preserved current text report behavior for default mode
- preserved report-only exit policy
- added unit/integration coverage for the envelope and JSON mode

### 对照关系

| Product / governance goal | Implemented behavior |
|---|---|
| Keep current users unblocked | `--format` defaults to `text` |
| Support future desktop cards | JSON includes `summary`, `obligations`, `evidence_checks`, and `declarations` |
| Avoid accidental gate behavior | `summary.governance_blocking_enforced` remains `false`; report-only obligations still exit `0` |
| Avoid CLI redesign | The existing checker gained only an output-format option |
| Keep results auditable | JSON preserves rule ids, level, phase, paths, requirements, and evidence statuses |

---

## 31. Part 3 Testing Governance Declaration

Required test layers for this implementation slice:

- `unit`: covered by `test_result_envelope_preserves_report_only_policy`.
- `integration`: covered by invoking checker JSON mode through `subprocess`.
- `workflow/orchestration`: covered by verifying new work-order path triggers `R-006` and `R-012`.
- `semantic regression`: N/A because no product or narrative behavior changes.
- `smoke`: covered by py_compile, default text command, JSON command, and JSON parse field checks.
- `human semantic review`: N/A for product semantics because this remains engineering-governance tooling.
- `human governance review`: required to confirm JSON output does not imply approval or gate enforcement.

---

## 32. Part 3 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P3-DC-01 | Record Part 2 acceptance | Section 29 exists |
| P3-DC-02 | Add explicit JSON output mode | `--format json` is accepted |
| P3-DC-03 | Preserve default text output | `--format` defaults to `text` |
| P3-DC-04 | Emit one parseable result envelope | JSON smoke parses as one object |
| P3-DC-05 | Preserve report-only exit policy | JSON shows `governance_blocking_enforced = false`; triggered obligations exit `0` |
| P3-DC-06 | Preserve triggered rule visibility | JSON obligations include `R-006` and `R-012` for a new key work order |
| P3-DC-07 | Add unit/integration coverage | `tools/audit/check_rule_registry_json_output_tests.py` exists and passes |
| P3-DC-08 | Avoid CLI/frontend/gate/runtime expansion | Only checker, test, and documentation files are changed |

---

## 33. Acceptance Gate For Part 3

> **中文注释**：这是 Part 3 的暂停点。你验收后，才考虑 CORE-02、desktop-card renderer、CLI bridge 或前端。

Part 3 is ready for user review when:

- default text mode still works
- JSON mode parses and reports the accepted result envelope fields
- report-only exit behavior is preserved
- unit/integration smoke passes
- related documentation records the extension
- no CLI package, frontend, adapter, gate, or runtime behavior is added

Do not continue to `JIKUO-CORE-02`, desktop-agent card renderer, CLI bridge, frontend, gate implementation, or Sprint 050 runtime hardening until the user accepts this Part 3 implementation.

---

## 34. Part 3 Verification Log

Commands run:

```powershell
python -B -m py_compile tools/audit/check_rule_registry.py tools/audit/check_rule_registry_json_output_tests.py
```

Result:

- syntax check passed

```powershell
python -B -m unittest tools.audit.check_rule_registry_json_output_tests
```

Result:

- ran 3 tests
- result `OK`

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md
```

Result:

- registry validation passed
- triggered `R-006` and `R-012`
- exit code `0`
- report-only posture preserved

```powershell
python -B tools/audit/check_rule_registry.py --format json --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md
```

Result:

- emitted parseable `jikuo.result.v0`
- triggered `R-006` and `R-012`
- `summary.governance_blocking_enforced` was `false`
- `exit_policy.triggered_obligations_change_exit_code` was `false`

```powershell
$json = python -B tools/audit/check_rule_registry.py --format json --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md
$obj = $json | ConvertFrom-Json
```

Result:

- parsed JSON successfully
- `schema_version = jikuo.result.v0`
- `triggered = 2`
- `blocking_enforced = False`
- `exit_changes = False`
- `rules = R-006,R-012`

---

## 35. Part 3 Acceptance Record

> **中文注释**：用户已确认继续机括任务，因此 Part 3 的可选 checker JSON 输出实现可以作为 `JIKUO-CORE-02` 的上游输入。仍不代表 CLI bridge、前端或 gate 被批准实现。

Acceptance:

- user accepted Part 3 by saying `继续机括的任务`
- `JIKUO-CORE-02` may start from the accepted structured result model and optional checker JSON output

Still not accepted:

- standalone `jikuo` CLI package
- desktop-agent card renderer implementation
- frontend implementation
- gate implementation
- `.codex/AGENTS.md` promotion
- Sprint 050 runtime hardening changes under this productization task

---

## 21. Part 1 Acceptance Record

> **中文注释**：用户已确认继续，因此 Part 1 的 result model contract 可以作为 Part 2 JSON 输出实现计划的上游输入。Part 1 自身不代表 checker 代码已被批准修改。

Acceptance:

- user accepted Part 1 by saying `请继续`
- Part 2 may define the JSON output implementation plan

Not accepted by Part 1 alone:

- checker JSON output implementation
- desktop-agent card renderer implementation
- CLI command implementation
- frontend implementation
- gate implementation
- `.codex/AGENTS.md` promotion
- Sprint 050 runtime hardening changes under this productization task

---

## 22. Part 2 Product / Technical / Mapping Views

> **中文注释**：Part 2 不是写代码，而是把“如果下一步要写 JSON 输出，最小安全改动是什么”说清楚。

### 产品口径

The product-facing problem is that the accepted result model is still only a contract.

Before implementation, `机括` needs a narrow plan that prevents the first JSON output slice from accidentally becoming:

- a CLI redesign
- a frontend API
- a blocking gate
- a replacement for desktop-agent cards
- a parser-breaking change to current text reports

Expected visible change after Part 2 acceptance:

- the next code slice can add structured output with a bounded scope
- existing text report users are not forced to change workflow
- desktop-agent and future frontend work get a stable first implementation target
- report-only behavior remains the default safety posture

### 技术口径

Mainline to change in the later implementation slice:

- `tools/audit/check_rule_registry.py`

Mainline explicitly not changed by Part 2:

- no checker code in this planning slice
- no registry schema changes
- no rule content changes
- no CLI command package
- no frontend
- no adapter
- no gate
- no runtime narrative engine behavior

Canonical source:

- accepted Part 1 `JikuoResultEnvelopeV0`

Bridge object:

- internal dictionary or small typed builder that represents `JikuoResultEnvelopeV0`

Consumer projection:

- existing text renderer
- new optional JSON renderer

Lifecycle:

- Part 2 accepted
- later implementation adds a result builder
- later implementation keeps current text output as default
- later implementation adds explicit JSON opt-in
- later tests compare text behavior and JSON parseability

Rollback / supersession:

- if JSON output causes friction, remove or disable the optional JSON flag without changing registry behavior
- if result fields prove insufficient, supersede `schema_version` rather than silently changing v0 semantics

### 对照关系

| Product / governance goal | Later implementation requirement |
|---|---|
| Keep current users unblocked | Default output remains the current text report |
| Support desktop-agent cards | JSON output exposes `summary`, `obligations`, and `evidence_checks` |
| Avoid accidental gate behavior | Triggered obligations still exit `0` in report-only mode |
| Avoid CLI redesign | Add only an output-format option, not a new command surface |
| Keep results auditable | JSON preserves rule ids, level, phase, matched paths, requirements, and evidence statuses |

---

## 23. Part 2 Proposed JSON Output Contract

Recommended option:

- add an explicit output flag such as `--format text|json`
- default remains `text`
- `json` prints one `JikuoResultEnvelopeV0` object to stdout
- stderr should remain reserved for unexpected tool/runtime errors when practical

Accepted output modes:

- `text`: current behavior
- `json`: structured result envelope

Rejected for the first implementation slice:

- replacing text output
- adding a standalone `jikuo` CLI command
- writing persistent result files
- streaming partial JSON events
- adding frontend API endpoints
- changing rule matching behavior

JSON formatting guidance:

- deterministic key order where practical
- `ensure_ascii=False` so Chinese paths or messages remain readable
- stable `schema_version = "jikuo.result.v0"`
- include `exit_policy` in every successful JSON result
- include `producer.mode = "report_only"`

---

## 24. Part 2 Implementation Steps For Later Code Slice

1. Extract current report facts into a result object before rendering.
2. Add a text renderer that preserves current text output semantics.
3. Add a JSON renderer for the same result object.
4. Add an argparse option for output format with default `text`.
5. Ensure triggered report-only obligations still return exit code `0`.
6. Ensure registry validation errors still fail deterministically.
7. Add tests or smoke commands that parse JSON and compare key text-mode behavior.

Implementation should avoid:

- changing YAML parser behavior unless required for JSON output
- changing trigger matching behavior
- changing evidence detection behavior
- adding persistence
- adding hidden approval records
- adding blocking gates

---

## 25. Part 2 Testing Governance Declaration

> **中文注释**：这里声明的是后续代码实现需要满足的测试层级；Part 2 本身仍是文档计划。

Required test layers for the later implementation slice:

- `unit`: required for result builder and JSON renderer if introduced as separable functions.
- `integration`: required for running checker in text and JSON modes against controlled paths.
- `workflow/orchestration`: required to verify `R-006` and `R-012` remain visible for new work-order docs.
- `semantic regression`: N/A because no product or narrative behavior should change.
- `smoke`: required for default text mode and explicit JSON mode.
- `human semantic review`: N/A for product semantics because this remains engineering-governance tooling.
- `human governance review`: required to confirm JSON output does not imply approval or gate enforcement.

Minimum implementation smoke commands:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md
```

```powershell
python -B tools/audit/check_rule_registry.py --format json --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md
```

Expected checks:

- text mode remains readable and report-only
- JSON mode parses as one object
- `schema_version` is `jikuo.result.v0`
- `summary.governance_blocking_enforced` is `false`
- `exit_policy.triggered_obligations_change_exit_code` is `false`
- triggered obligations include `R-006` and `R-012` for a new key work order path

---

## 26. Part 2 Delivery Criteria

| ID | Requirement | Verification |
|---|---|---|
| P2-DC-01 | Record Part 1 acceptance | Section 21 exists |
| P2-DC-02 | Define product / technical / mapping views for JSON output implementation | Section 22 exists |
| P2-DC-03 | Keep default text output unchanged as the planned posture | Section 23 states default `text` |
| P2-DC-04 | Define JSON output opt-in boundary | Section 23 defines explicit `json` mode |
| P2-DC-05 | Define later implementation steps | Section 24 exists |
| P2-DC-06 | Declare later implementation test layers | Section 25 exists |
| P2-DC-07 | Preserve no-code boundary for Part 2 | No checker, registry, CLI, frontend, gate, or runtime code is changed in this slice |
| P2-DC-08 | Run report-only checker smoke on this work order | Verification log records checker result |

---

## 27. Acceptance Gate For Part 2

> **中文注释**：这是 Part 2 的暂停点。你验收后，才可以进入真正的 checker JSON 输出实现。

Part 2 is ready for user review when:

- default text output remains the planned default
- JSON output is explicit opt-in
- report-only exit policy remains unchanged
- no CLI package, frontend, adapter, gate, or runtime behavior is pulled into the slice
- later implementation test layers are declared
- checker smoke has been run against the planning doc

Do not continue to checker JSON output implementation until the user accepts this Part 2 plan.

---

## 28. Part 2 Verification Log

Commands to run:

```powershell
python -B tools/audit/check_rule_registry.py --added docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md --work-order docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-01_structured_result_model.md
```

Result:

- registry validation passed
- triggered `R-006` and `R-012`
- required fields and sections for `R-006` reported `OK`
- Sprint index document for `R-012` reported `OK`
- `sprint_index_entry` declaration remained `REVIEW`
- exit code `0`
- report-only posture preserved
