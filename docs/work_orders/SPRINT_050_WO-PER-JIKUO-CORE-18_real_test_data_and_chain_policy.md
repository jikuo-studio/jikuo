# SPRINT 050 WO-PER-JIKUO-CORE-18: Real Test Data And Real Chain Policy

> **Kernel compatibility**: adds an approved report-only policy that requires real test data and real execution-chain evidence during testing-governance work, instead of treating preview-template placeholders as acceptance evidence.
> **Current slice**: a loadable policy fixture and regression tests only; no production root `.jikuo/` write, no gate, no desktop adapter change, and no code-level placeholder blocker.
> **User scenario**: A Codex / Claude desktop APP user notices that an acceptance card can appear to pass while the agent only copied a preview placeholder. The user wants the working rule to be governed by JIKUO policy instead of probabilistic instruction memory.
> **Runtime chain**: task_start -> policy-store evaluate -> task metadata/path conditions match -> required action projected -> missing real-chain evidence reported -> evidence can satisfy the rule only when supplied as explicit produced evidence.
> **Canonical source**: `tools/jikuo/fixtures/policy_store_real_chain_testing_project/.jikuo/policies/approved/POLICY-real-test-data-and-chain.yaml`.
> **Bridge object**: approved `jikuo.configurable_rule_policy.v0`; `jikuo.policy_trigger_eval_report.v0`; `jikuo.missing_evidence_report.v0`.

## Product Semantics

Testing acceptance must not be satisfied by copying preview templates, placeholder phrases, or shape-only examples.

For governed testing work, the required evidence is that the agent used concrete test data and exercised the relevant chain being claimed. A proposal card or placeholder can guide the user, but it is not evidence that the chain worked.

中文注释：这条规则来自本轮纠偏。正确层次不是先给所有代码加硬编码拦截，而是先把“真实测试数据 + 真实链路”变成会被 JIKUO policy evaluator 加载的工程规则。

## Scope

In scope:

- add a report-only approved policy fixture
- require `verify_real_test_data_and_real_chain`
- require `real_test_data_and_chain_evidence`
- prove the policy is loaded by `policy_store.py evaluate`
- prove missing evidence and satisfied evidence paths

Out of scope:

- production project-root `.jikuo/` creation
- code-level placeholder rejection in all guarded writers
- automatic desktop-chat phrase capture
- gate / blocking enforcement
- semantic judgement of product output quality

## Implemented Policy

Policy id:

- `POLICY-real-test-data-and-chain`

Trigger:

- `task_start`

Conditions:

- `task_type_is: work_order_delivery`
- `jikuo_layer_is: testing_governance`
- `changed_path_matches: tools/jikuo/**`

Required action:

- `verify_real_test_data_and_real_chain`

Required evidence:

- `real_test_data_and_chain_evidence`

## Acceptance Evidence

Required:

- `policy_store.py evaluate` reports the policy as triggered for matching testing-governance context.
- Without produced evidence, the report includes missing `real_test_data_and_chain_evidence`.
- With produced evidence, the report marks the evidence status `ok`.

Validation commands:

```powershell
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/policy_store.py evaluate --event task_start --project-root tools/jikuo/fixtures/policy_store_real_chain_testing_project --task-type work_order_delivery --jikuo-layer testing_governance --changed-path tools/jikuo/policy_store_tests.py --format json
```

Observed:

- `policy_store_tests.py`: passed; 21 tests.
- evaluator smoke: returned `policy_store_status: active`, `policy_eval_status: evaluated`, triggered `POLICY-real-test-data-and-chain`, and reported missing `real_test_data_and_chain_evidence` when no evidence was supplied.

## Residual Risk

This policy is currently report-only. It makes fake acceptance visible when the evaluator is run with the right context, but it does not yet force every desktop task to invoke the evaluator, nor does it prevent a writer from accepting a placeholder phrase. Those belong to later desktop invocation / guarded apply / gate work.
