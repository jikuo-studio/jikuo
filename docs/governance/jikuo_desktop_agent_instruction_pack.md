# JIKUO Desktop Agent Instruction Pack

> **Date**: 2026-05-09  
> **Status**: Project-local instruction pack; not installed as a Codex Skill  
> **Purpose**: help Codex / Claude desktop APP agents invoke JIKUO consistently from chat by calling the package `jikuo.agent_flow propose` runner and narrow approved `jikuo.agent_flow apply` operations.
> **Primary user surface**: Codex / Claude desktop APP chat.  
> **Boundary**: This file is an agent instruction layer over the deterministic package runner, not an installed Skill, not an MCP server, not a plugin, and not a gate.
> **Reading note**: English is the working source text; Chinese notes are added for review speed.

---

## 1. 中文摘要

这份文件解决的是一个很小但关键的问题：用户主要在 Codex / Claude 桌面 APP 里工作，所以 Agent 不应该要求用户切到 CLI 手动执行一组 helper。

本 instruction pack 告诉 Agent：

- 什么时候认为“机括”被触发
- 如何把用户意图映射到 `jikuo.agent_flow propose`
- 如何把 proposal 卡片贴回同一个聊天
- 哪些动作只是 no-write 预览
- 哪些写入动作当前不能假装已经有统一 `apply`
- 什么时候必须拒绝、澄清或说明未实现

---

## 2. Core Rule

When JIKUO applies, the desktop agent should keep the user in the active chat.

JIKUO is a tool-backed harness after activation, not a probabilistic prompt preference. Trigger discovery may be explicit or agent-suggested, but once a flow is inside JIKUO coverage the agent must call the runner or later MCP tool, surface the returned cards, and keep policy runtime status auditable.

The agent may call local no-write helpers and accepted guarded apply helpers internally, but should not ask the ordinary user to switch to CLI for routine JIKUO start, status, preview, review, apply, or handoff flows.

The current deterministic entry point is:

```powershell
python -B -m jikuo.agent_flow propose --event "<event>" --task-title "<task title>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown
```

Proposal mode is always no-write.

Guarded apply mode is available only for accepted operation names and explicit user approval.

---

## 3. Trigger Handling

Explicit user shortcuts:

| User shortcut | Agent event | Required argument | Expected behavior |
|---|---|---|---|
| `机括：开始` | `task_start` | task title or task summary | Call `jikuo.agent_flow propose`, then paste the proposal card into chat |
| `机括：继续` | `task_continue` | session id when continuing a persisted session | If missing session id, return the runner refusal card or ask one concise clarifying question |
| `机括：状态` | `status` | none | Call `jikuo.agent_flow propose --event status` and report project-local JIKUO state |
| `机括：审计` | `audit` | changed surface when available | Call the audit placeholder proposal; do not claim full checker composition unless implemented |
| `机括：验收` | `completion` | explicit task/session context | Preview completion review; do not write completion without explicit guarded write approval |
| `机括：交接` | `handoff` | explicit task/session context | Preview handoff review; do not write handoff without explicit guarded write approval |
| `机括：规则` | `status` or future rule proposal | rule preference text | Report that rule proposal persistence is not implemented unless a later work order adds it |
| `JIKUO: import policy template` | `policy_template_import_plan` | template path and project root | Call `jikuo.agent_flow propose`, show binding status and write targets, then wait for explicit approval before activation |

Agent-suggested trigger conditions:

- the user starts a new implementation task
- the user asks for a governed review / audit / handoff
- the user defines a repeated rule preference
- the task changes governance documents, rule registry, task-session data, sidecar state, agent instructions, MCP, plugin, or gate behavior
- the agent is about to deliver a non-trivial JIKUO work order or implementation result

When suggested rather than explicitly triggered, the agent should briefly state why JIKUO may apply and then run only no-write `propose` if safe. Once the runner returns, the result is mandatory process evidence; do not replace it with an informal summary.

---

## 4. Event Invocation Map

| Situation | Event | Safe command shape |
|---|---|---|
| User starts a governed task | `task_start` | `python -B -m jikuo.agent_flow propose --event task_start --task-title "<task title>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |
| User asks for project JIKUO state | `status` | `python -B -m jikuo.agent_flow propose --event status --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |
| User continues a known session | `task_continue` | `python -B -m jikuo.agent_flow propose --event task_continue --session-id "<session id>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |
| User previews index/session refs | `index` | `python -B -m jikuo.agent_flow propose --event index --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |
| User requests evidence review | `evidence` | `python -B -m jikuo.agent_flow propose --event evidence --session-id "<session id>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |
| User requests verification review | `verification` | `python -B -m jikuo.agent_flow propose --event verification --session-id "<session id>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |
| User requests completion review | `completion` | `python -B -m jikuo.agent_flow propose --event completion --session-id "<session id>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |
| User requests handoff review | `handoff` | `python -B -m jikuo.agent_flow propose --event handoff --session-id "<session id>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |
| User wants to adopt a reusable policy template | `policy_template_import_plan` | `python -B -m jikuo.agent_flow propose --event policy_template_import_plan --template "<policy template yaml>" --project-root "<absolute project root>" --user-phrase "<exact user phrase as spoken>" --format markdown` |

If a required argument is missing, prefer the runner refusal card when it can be produced. Otherwise ask one concise clarifying question.

Routine completion receipt for workspace writes:

- If the agent performs workspace writes in a turn, including file creation, edits, deletion, generated outputs, git staging, commits, or guarded project writes, run `python -B -m jikuo.agent_flow propose --event completion_review --project-root "<absolute project root>" --format json` after verification and before the final response, then surface the returned card Markdown.
- This is a host-AI instruction obligation and a practical MVP receipt path. It is not proof of a mounted post-turn hook or a full lifecycle runner.
- On Windows PowerShell, use `python --% -B -m jikuo.agent_flow propose ... --host-semantic-intent-json "{\"schema\":\"jikuo.host_semantic_intent.v0\",\"status\":\"provided\"}"` when passing inline JSON so PowerShell does not strip JSON quotes.
- Do not ask the ordinary user to run this routine receipt. If completion review cannot run or fails, say that the completion receipt is missing or failed.

---

## 5. Chat Return Contract

After invoking `jikuo.agent_flow propose`, paste the proposal in the same chat. If the runner or MCP wrapper returns `chat_ready_markdown`, return that text as the primary user-visible artifact.

Summaries may be added before or after the card, but they must not hide or replace:

- `policy_runtime_status` when present
- triggered and non-triggered policy state
- missing evidence reports
- approval boundaries and write / non-write effects
- loop step ids and atom ids

The response should include:

- proposal title or card title
- event / scenario detected
- whether writes were performed
- loop step ids and atom ids when the runner output exposes them
- approval boundary
- next safe action

For JIKUO productization work, also include one short product / business meaning line so the user can understand progress from a product perspective.

Do not say that the user must manually run the helper unless the user explicitly asks for the CLI command or an advanced debugging path.

Do not treat card surfacing as optional style. It is harness evidence: a governed flow without visible cards is incomplete even if the underlying runner executed successfully.

---

## 6. Approval And Write Boundary

Current no-write command:

- `jikuo.agent_flow propose`

Current guarded apply commands:

- `jikuo.agent_flow apply --operation task_session_evidence_update`
- `jikuo.agent_flow apply --operation policy_evolution_write --proposal-ref "<approved proposal ref>"`
- `jikuo.agent_flow apply --operation policy_template_activation --template "<policy template yaml>"`

Existing lower-level guarded helpers may exist, but this instruction pack does not authorize the agent to use them automatically unless they are explicitly wrapped by an accepted `jikuo.agent_flow apply` operation.

Before any durable write:

- the target object must be explicit
- policy evolution writes must include the proposal ref the user reviewed
- the write effect must be explicit
- the exact user approval phrase must be captured
- the command must be an already accepted guarded helper or an accepted `jikuo.agent_flow apply` operation
- the result must be reported back in the same chat

If the user approves a write that has no implemented safe command, the agent should say the write path is not implemented yet and propose the next planning or implementation slice.

---

## 7. Refusal Rules

Refuse or pause when:

- the requested JIKUO action would require hidden durable writes
- the user asks the agent to treat a vague approval as permission for multiple actions
- the requested action depends on MCP, plugin, frontend, automatic gate, or an apply operation that is not implemented
- the agent cannot identify the task/session target
- running a command would require access outside the project or a destructive action without approval

The refusal should be short, name the missing boundary, and offer the next safe no-write action.

---

## 8. Future Skill Projection

This file is deliberately shaped so it can later become the body reference for:

- a Codex Skill
- a Claude MCP tool instruction
- a Codex Plugin workflow hint

Do not install or promote it globally until a separate accepted work order approves:

- activation surface
- packaging location
- update policy
- regression tests
- rollback path
