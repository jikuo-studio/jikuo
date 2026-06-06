# JIKUO CLI Enhanced Handoff

Date: 2026-06-05
Project root: `D:\personal_project\Jikuo`
Current baseline commit: `f0c0473 GUI version: harden Codex hook turn anchors`

This document is the durable handoff for restarting Codex CLI work on the JIKUO CLI enhanced governance shell. It is not an audit receipt and does not include raw chat transcript text.

## Startup Prompt For New Codex Session

Use this prompt when starting a fresh Codex CLI session:

```text
请先读取：
1. docs/governance/JIKUO_CLI_ENHANCED_HANDOFF.md
2. .jikuo/runtime/state_summary.json
3. 最新的 .jikuo/runtime/history/*.md
4. git log -1 --oneline
5. git status --short

然后继续 JIKUO CLI enhanced 版本设计与实现，不要从头重新分析。注意：JIKUO 本身不是 AI，不自己判断语义；语义判断由宿主 AI 提供，JIKUO 只负责记录、合并、触发 policy、展示证据。
```

## Current Repo State

- GUI baseline has been committed as `f0c0473 GUI version: harden Codex hook turn anchors`.
- That commit touched:
  - `.codex/hooks/jikuo_user_prompt_submit.py`
  - `src/jikuo/turn_anchor.py`
  - `tests/codex_hook_tests.py`
  - `docs/governance/jikuo_execution_mounts.md`
  - `docs/registry/capabilities.yaml`
  - `docs/registry/scenario_chains.yaml`
  - `docs/registry/work_orders.yaml`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-HOSTADAPT-01_host_adapter_contract.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MVP-01_work_receipt_and_configuration_mvp.md`
- Current untracked items observed before this handoff write:
  - `.tmp/`
  - `test.md`
- Treat those untracked items as pre-existing/unrelated unless the user explicitly asks to process them.
- Tests previously run for the GUI baseline: `python -m unittest tests.codex_hook_tests` passed 15 tests. `pytest` was unavailable in this environment.

## Current Codex CLI Permission Configuration

The user asked to make Codex CLI closer to GUI auto-approval while retaining boundaries. The local Codex config outside the repo was updated at `C:\Users\DELL\.codex\config.toml`:

```toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
approvals_reviewer = "auto_review"

[sandbox_workspace_write]
network_access = false
writable_roots = ['D:\personal_project\Jikuo', 'D:\tmp']
```

Backup created:

```text
C:\Users\DELL\.codex\config.toml.bak-20260605T225818
```

This affects future Codex CLI sessions. It does not preserve conversation memory by itself.

## Stable Product Direction

JIKUO's core direction is unchanged:

- JIKUO is not an AI.
- JIKUO must not infer semantic intent by itself.
- Host AI provides compact semantic intent evidence.
- JIKUO records, merges, evaluates policy triggers, displays evidence, and produces receipts.

The goal is not to create separate GUI and CLI governance systems. The goal is one shared data model, with CLI providing stronger lifecycle orchestration where the execution loop is controllable.

## GUI Versus CLI Boundary

GUI subscription environment is suitable for:

- Visual configuration.
- Policy and document rule CRUD.
- Runtime receipt viewing.
- Risk and gap display.
- Light governance when host AI cooperates.

CLI wrapper / launcher / harness is suitable for:

- Stable turn anchor propagation across all calls.
- Semantic intent gate before governed actions.
- Automatic task_start and completion_review lifecycle calls.
- Git baseline/final observation.
- Stronger work receipt generation.
- Reliable execution envelope injection without relying on the AI to remember fields.

## Existing Model Pieces To Reuse

Do not replace these with a separate CLI-only model:

- `turn_anchor` already exists and should remain the identity core for a user turn.
- `host_semantic_intent` is the host AI semantic classification carrier.
- `work_profile` is the merged policy-facing projection.
- `runtime_visibility` writes visible runtime cards and state summaries.
- `agent_flow propose --event task_start` and `--event completion_review` are the existing lifecycle proposal surfaces.
- `.codex/hooks/jikuo_user_prompt_submit.py` is the current GUI/Codex hook entry point.

Important implementation files to inspect next:

- `src/jikuo/turn_anchor.py`
- `src/jikuo/work_profile.py`
- `src/jikuo/runtime_visibility.py`
- `src/jikuo/agent_flow.py`
- `src/jikuo/integrations/host_adapter_contract.py`
- `src/jikuo/integrations/mcp/schemas.py`
- `.codex/hooks/jikuo_user_prompt_submit.py`

## Known Current Behavior

At the start of a GUI/Codex turn, mounted hooks often report semantic intent as fallback or unavailable. This is expected because the hook runs before the host AI has understood the user's request.

For recent turns, the host AI later supplied compact semantic intent through JIKUO follow-up calls. The visible latest card may still look like fallback if another status/config card overwrote `.jikuo/runtime/last_card.md`. Use `.jikuo/runtime/history/*.md` to inspect lifecycle history instead of relying only on the latest card.

Completion review currently depends on the AI or host flow calling:

```powershell
python -B -m jikuo.agent_flow propose --event completion_review --project-root "D:\personal_project\Jikuo" --format json
```

CLI enhanced should make that an automatic runner step.

## Requirement Gap: Semantic Search To Execution Evidence

The user's earlier requirement is: semantic search should find the corresponding turn and its execution evidence.

Current implementation does not fully satisfy that requirement:

- The raw user input is not durably persisted by the hook-owned files.
- JIKUO stores/projections focus on `turn_anchor`, prompt digest/hash, redacted summaries, runtime cards, and policy evidence.
- This is privacy-preserving but insufficient for semantic search over original user phrasing.

Needed design:

- Add a private turn input index shared by GUI and CLI.
- Store raw user input in a private/local store, not in public audit evidence cards.
- Link each indexed input to:
  - `turn_anchor`
  - `session_id`
  - `turn_id`
  - `prompt_sha256`
  - `received_at`
  - `project_root`
  - host semantic intent refs
  - task_start refs
  - completion_review refs
  - receipt refs
  - git baseline/final refs where available
- Audit evidence should expose only redacted summaries, hashes, and references unless explicitly authorized.
- Semantic search can query the private input index, then display the linked execution evidence without directly exposing the raw prompt in the audit chain.

This should be treated as a first-class CLI enhanced work item, not a separate GUI-only feature.

## Proposed Shared Execution Envelope

Design an `execution_envelope` as a wrapper around existing fields, not as a replacement for `turn_anchor`.

Candidate shape:

```yaml
schema: jikuo.execution_envelope.v0
envelope_id: env_...
session_id: ...
turn_id: ...
turn_anchor:
  schema: jikuo.turn_anchor.v0
  anchor_id: ...
  prompt_sha256: ...
  project_root: ...
prompt_digest:
  algorithm: sha256
  value: ...
received_at_utc: ...
project_root: ...
host_semantic_intent:
  status: provided | unavailable | failed
  provider: host_ai
lifecycle:
  state: received | semantic_classified | routed | task_started | executing | verified | completion_reviewed | receipt_ready | failed
git_observation:
  baseline_ref: ...
  final_ref: ...
receipt_ref: ...
privacy:
  raw_prompt_storage: none | private_index
  raw_prompt_exposed_in_audit: false
```

The envelope's job is to carry stable identity and lifecycle context through the CLI runner. It should be consumable by existing JIKUO functions and runtime cards.

## Proposed Lifecycle State Machine

Use one fixed state machine across GUI and CLI, with CLI able to enforce more transitions:

1. `received`
   - User input accepted.
   - `turn_anchor` and prompt digest available.

2. `semantic_classified`
   - Host AI has produced compact semantic intent.
   - JIKUO has not inferred meaning by itself.

3. `routed`
   - JIKUO router/proposal evaluated obligations from host intent and deterministic policy context.

4. `task_started`
   - `task_start` lifecycle card exists.
   - Optional task-session binding is created or explicitly deferred.

5. `executing`
   - Host AI performs tool calls, file edits, tests, or commands.

6. `verified`
   - Tests, checks, or file review have run where applicable.

7. `completion_reviewed`
   - JIKUO completion review has run.
   - Git final observation is available when inside a git repo.

8. `receipt_ready`
   - Final user-facing receipt can link planned writes, declared writes, observed writes, policy state, and lifecycle cards.

9. `failed`
   - Runner failed or completion_review failed.
   - Failure becomes an explicit delivery gap.

GUI may only observe a subset and mark lifecycle status as partial. CLI should enforce the full flow.

## CLI Enhanced Implementation Plan

1. Document and formalize shared schemas.
   - Add schema docs for `execution_envelope` and lifecycle state.
   - Clarify that `turn_anchor` remains the stable identity object.
   - Define compatibility rules for GUI partial observation.

2. Add private turn input index.
   - Store original user input privately for semantic retrieval.
   - Keep audit evidence redacted by default.
   - Link input records to turn anchors and runtime evidence.
   - Add tests for privacy flags and search linkage.

3. Build CLI runner prototype.
   - Receive user prompt.
   - Create or load execution envelope.
   - Ask host AI for compact semantic intent before action.
   - Call JIKUO router/task_start with injected `turn_anchor`.
   - Capture git baseline.
   - Let host AI execute the work.
   - Capture git final state.
   - Run completion_review automatically.
   - Emit receipt or explicit failure.

4. Reuse existing JIKUO proposal surfaces.
   - Do not fork a separate CLI-only policy path.
   - Extend `agent_flow` inputs only where the shared model needs new fields.

5. Improve runtime evidence display.
   - Show lifecycle completeness: observed, partial, missing, failed.
   - Distinguish AI-declared writes, git-observed writes, and mixed/uncertain sources.
   - Link completion receipts to private turn input index records without exposing raw prompts.

6. Add tests.
   - Unit tests for envelope normalization.
   - Unit tests for lifecycle state transitions.
   - Tests for GUI partial lifecycle behavior.
   - Tests for CLI enforced lifecycle behavior.
   - Tests for raw input privacy and semantic search references.

## Immediate Next Steps After Restart

1. Read this handoff document first.
2. Read `.jikuo/runtime/state_summary.json` and the newest `.jikuo/runtime/history/*.md`.
3. Run `git log -1 --oneline` and `git status --short`.
4. Inspect the existing model/code files listed above.
5. Draft the shared schema update for `execution_envelope` and lifecycle state.
6. Add the private turn input index to the development plan before writing implementation code.

## Guardrails For The Next Session

- Do not treat GUI and CLI as two separate systems.
- Do not make JIKUO infer semantic meaning.
- Do not expose raw prompt text in audit cards by default.
- Do not rely on `.jikuo/runtime/last_card.md` alone; it can be overwritten.
- Do not treat pre-existing untracked `.tmp/` or `test.md` as evidence of the next implementation unless they are intentionally touched.
- If workspace files are changed, run completion_review before final response.
