# SPRINT 050 WO-PER-JIKUO-LIVE-01: Policy Evaluation Goes Live In Desktop Chat

> **Kernel compatibility**: composes existing report-only policy-store status, trigger evaluation, condition evaluation, and evidence checking into the desktop APP proposal flow.
> **Current slice**: make policy evaluation visible in `agent_flow.py propose` cards for task-start style flows; no gate, no automatic durable write, no production root `.jikuo/` creation, no policy supersession, and no frontend.
> **User scenario**: A Codex / Claude desktop APP user starts a governed task and wants to see which project policies triggered, which actions are required, and which evidence is missing without switching to CLI.
> **Runtime chain**: user task request -> desktop agent invokes `agent_flow.py propose` -> runner evaluates active policy store -> proposal card shows triggered policies / required actions / missing evidence -> user can provide evidence, defer, or mark the policy as not applicable.
> **Canonical source**: `jikuo_policy_store_configuration_flow.md`, `jikuo_policy_aware_agent_flow_contract.md`, `SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`, CORE-18, CORE-19.
> **Bridge object**: `jikuo.agent_flow_proposal.v1.policy_context`; `jikuo.policy_trigger_eval_report.v0`; `jikuo.missing_evidence_report.v0`.

## Product Meaning

This is the first slice where ordinary desktop users should feel that JIKUO is active in the conversation.

The goal is not to block work. The goal is to show, in the same chat, that the agent has checked active policies and can explain what governance evidence is missing.

## Scope

In scope:

- call report-only policy evaluation automatically from relevant `agent_flow.py propose` task-start flows
- pass explicit task metadata such as `task_type`, `jikuo_layer`, `changed_path`, and `added_path`
- show active policy store status, triggered policies, required actions, evidence status, and missing evidence in the proposal card
- keep all writes disabled in proposal mode
- add a minimal feedback / exemption projection such as `not_applicable`, `defer`, or `needs_scope_narrowing`
- test with CORE-18 / CORE-19 style real governance policies

Out of scope:

- blocking gates
- full policy refinement or supersession
- automatic evidence persistence
- automatic `agent_flow.py apply`
- frontend configuration UI
- MCP / Skill / Plugin packaging
- judging product-output quality

## Required Inputs

The runner should accept or derive:

- `event`
- `project_root`
- `task_title`
- `task_type`
- `jikuo_layer`
- `changed_path`
- `added_path`
- optional produced evidence
- optional task-session id for evidence ingestion

## Card Projection

The desktop proposal card should include:

- policy store status
- policy evaluation status
- triggered policy count
- triggered policy refs and titles
- required action refs and action types
- evidence status summary
- missing evidence reports
- no-write boundary
- suggested next action
- minimal policy feedback options

## Minimal Feedback / Exemption

The first feedback path should be light and report-only.

Allowed feedback examples:

- `not_applicable`: user says this policy does not apply to the current task
- `defer`: user wants to continue without satisfying the evidence now
- `needs_scope_narrowing`: policy triggered too broadly and should be refined later

This slice should project feedback options in the card. It should not persist feedback or revise policies yet.

## Acceptance Evidence

Required tests:

- `agent_flow.py propose` triggers policy evaluation for a fixture active policy store.
- CORE-18 style testing-governance policy appears as triggered when matching metadata is supplied.
- CORE-19 style code-change policy appears as triggered when matching metadata is supplied.
- Missing evidence appears in the same proposal card.
- Supplying produced evidence changes evidence status to `ok`.
- Proposal mode performs no durable writes and does not create root `.jikuo/policies` or `.jikuo/task_sessions`.

Required commands:

```powershell
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/policy_store_tests.py
git diff --check -- tools/jikuo/agent_flow.py tools/jikuo/agent_flow_tests.py docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-01_policy_evaluation_goes_live_in_desktop_chat.md docs/jikuo/governance/jikuo_productization_task_map.md docs/jikuo/governance/jikuo_policy_store_configuration_flow.md
```

## Implementation Status

Status:

- implemented and ready for user review.
- `agent_flow.py propose` now accepts inline produced evidence and passes it into report-only policy evidence matching.
- desktop proposal markdown now shows policy feedback options when policies trigger.
- CORE-18 / CORE-19 style fixture policies are covered by `agent_flow_tests.py` using the real policy evaluator path.
- proposal mode remains no-write and does not persist feedback, exemptions, evidence, policy revisions, or task-session files.

Observed verification:

```powershell
python -B tools/jikuo/agent_flow_tests.py
python -B tools/jikuo/policy_store_tests.py
python -B tools/jikuo/agent_flow.py propose --event task_start --task-title "Real Chain Policy Probe" --project-root tools\jikuo\fixtures\policy_store_real_chain_testing_project --task-type work_order_delivery --jikuo-layer testing_governance --changed-path tools/jikuo/policy_store_tests.py
```

## Residual Risk

This slice may surface false positives quickly because real policies are now visible in the normal desktop flow. That is expected. The slice should keep feedback lightweight so users can flag over-triggering without needing a full policy-supersession workflow.
