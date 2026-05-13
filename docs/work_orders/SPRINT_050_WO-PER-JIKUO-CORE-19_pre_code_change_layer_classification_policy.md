# SPRINT 050 WO-PER-JIKUO-CORE-19: Pre-Code-Change Layer Classification Policy

> **Kernel compatibility**: adds a report-only policy that requires a layer classification before code-change work, so the agent first decides whether the issue is a governance-method problem that should add/change policy, or a design/implementation problem that should change code.
> **Current slice**: a loadable approved policy fixture and regression tests only; no production root `.jikuo/` write, no automatic desktop invocation, no gate, and no code-level blocker.
> **User scenario**: A Codex / Claude desktop APP user catches that an agent started changing code when the better first move was to add or refine a governance rule.
> **Runtime chain**: task_start -> policy-store evaluate -> code-change metadata/path conditions match -> required classification action projected -> missing classification evidence reported -> supplied classification evidence satisfies the rule.
> **Canonical source**: `tools/jikuo/fixtures/policy_store_real_chain_testing_project/.jikuo/policies/approved/POLICY-pre-code-change-layer-classification.yaml`.
> **Bridge object**: approved `jikuo.configurable_rule_policy.v0`; `jikuo.policy_trigger_eval_report.v0`; `jikuo.missing_evidence_report.v0`.

## Product Semantics

Before changing code, the agent must classify the problem layer:

- `governance_method`: the issue is caused by missing, vague, or unmounted engineering governance; the first response should add, revise, or load policy/rules.
- `design_implementation`: the policy/rule already exists and the implementation is wrong or incomplete; changing code is appropriate.
- `mixed_or_unclear`: the agent should surface the ambiguity before making durable implementation changes.

This rule is deliberately upstream of code edits. It does not decide product quality; it decides which engineering response path is safer.

## Scope

In scope:

- add a report-only approved policy fixture
- require `classify_governance_vs_implementation_before_code_change`
- require `governance_vs_implementation_classification_evidence`
- prove missing-evidence and satisfied-evidence paths through `policy_store.py evaluate`

Out of scope:

- blocking code edits automatically
- deciding the classification with an LLM inside the policy evaluator
- production project-root policy writes
- desktop adapter / Skill / MCP integration
- gate enforcement

## Implemented Policy

Policy id:

- `POLICY-pre-code-change-layer-classification`

Trigger:

- `task_start`

Conditions:

- `task_type_is: code_change`
- `jikuo_layer_is: implementation_governance`
- `changed_path_matches: tools/jikuo/**`

Required action:

- `classify_governance_vs_implementation_before_code_change`

Required evidence:

- `governance_vs_implementation_classification_evidence`

## Acceptance Evidence

Required:

- `policy_store.py evaluate` reports the policy as triggered for matching code-change context.
- Without produced evidence, the report includes missing `governance_vs_implementation_classification_evidence`.
- With produced evidence, the report marks the evidence status `ok`.

Validation command:

```powershell
python -B tools/jikuo/policy_store_tests.py
```

Observed:

- `policy_store_tests.py`: passed after adding missing and satisfied evidence cases.

## Residual Risk

This policy is report-only. It makes the required pre-code-change decision visible when the evaluator is invoked, but it does not yet guarantee that every desktop-app task invokes the evaluator before edits. That belongs to later desktop invocation / guarded apply / gate work.
