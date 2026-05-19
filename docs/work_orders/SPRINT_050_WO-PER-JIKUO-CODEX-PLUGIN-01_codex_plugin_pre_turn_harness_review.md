# SPRINT_050_WO-PER-JIKUO-CODEX-PLUGIN-01: Codex Plugin Pre-Turn Harness Review

> **Status**: Level 1 project-local proof files implemented and local stdin smoke passed; official Codex hook surface reviewed on 2026-05-19; GUI proof and strict mounted acceptance still pending.
> **Date**: 2026-05-16
> **Product meaning**: Determine whether a Codex plugin can make JIKUO run before every user turn, or whether it should only ship as an instruction / MCP setup aid. This prevents JIKUO from claiming strict mounted behavior that Codex cannot actually enforce.

## 1. Why This Task Exists

JIKUO can expose MCP tools and install Codex instructions, but those surfaces are
not automatically strict mounted execution.

The missing question is:

> Can a Codex plugin intercept or participate in every user turn before the
> model performs ordinary work?

If yes, a Codex plugin may become a strict mounted adapter candidate. If no, the
Codex plugin should be limited to instruction-packaging, MCP configuration,
proof capture, and runtime verification shortcuts.

## 2. Scope

This task verifies and designs Codex host-boundary behavior. It now includes a
project-local `UserPromptSubmit` proof hook, but it still does not implement a
packaged Codex plugin integration.

In scope:

- inspect the currently supported Codex plugin surfaces
- distinguish skills / instructions from pre-turn hooks
- determine whether a plugin can call `jikuo.route_user_request` before every user turn
- identify what proof is required before marking Codex as strict mounted capable
- design a safe fallback plugin that improves setup without claiming strictness

Out of scope:

- implementing a packaged plugin
- claiming Codex strict mounted support before proof
- adding Codex plugin behavior to the JIKUO kernel
- bypassing MCP / activation settings / runtime visibility contracts

## 3. Candidate Outcomes

| Outcome | Meaning | Product Posture |
|---|---|---|
| `strict_pre_turn_supported` | Codex plugin has a stable pre-turn hook or equivalent host boundary | Codex plugin may be promoted to first strict mounted adapter candidate |
| `instruction_only_supported` | Plugin can provide skills, instructions, MCP setup, or UI affordances but cannot force pre-turn execution | Ship as onboarding / proof / helper plugin only; show `degraded_instruction_only` for mounted mode |
| `unsupported_or_unstable` | Plugin API is unavailable, private, or unstable for this use | Do not build Codex plugin yet; keep using MCP + instruction proof |

## 4. Acceptance Evidence

Before this task can be accepted, record:

- Codex app / CLI version and OS
- plugin manifest capabilities actually available
- whether pre-turn or user-prompt hook behavior exists
- whether the plugin can call local MCP or CLI before the model answers
- whether the same runtime card is visible in chat and `.jikuo/runtime/last_card.md`
- whether failure to call JIKUO is visible to the user
- final classification: strict adapter candidate, instruction-only plugin, or deferred

## 4.1 Official Codex Hook Surface Review

Reviewed on 2026-05-19 against the official OpenAI Codex documentation:

- Codex hooks are enabled by default and can be configured through
  `hooks.json` or inline `[hooks]` tables in `config.toml`.
- Codex looks for hook configuration in user-level and project-level locations,
  including `~/.codex/hooks.json`, `~/.codex/config.toml`,
  `<repo>/.codex/hooks.json`, and `<repo>/.codex/config.toml`.
- Project-local hooks load only when the project `.codex/` layer is trusted.
- `UserPromptSubmit` is a turn-scoped hook. It receives the current `prompt`
  before it is sent to the model, plus common fields such as `cwd`,
  `session_id`, `turn_id`, and `permission_mode`.
- `UserPromptSubmit` can add model-visible `additionalContext` or block the
  prompt, which makes it a plausible proof surface for JIKUO pre-turn routing.
- Plugin-bundled hooks are opt-in in the current release and require
  `[features].plugin_hooks = true`; therefore the first proof should use
  project-local `.codex/` hook configuration rather than a plugin bundle.
- `PreToolUse` can help enforce later tool-stage checks, but it is not a
  complete enforcement boundary and should not be treated as the primary
  mounted proof.

Source refs:

- `https://developers.openai.com/codex/hooks`
- `https://developers.openai.com/codex/mcp`
- `https://developers.openai.com/codex/plugins/build`

## 4.2 Minimal UserPromptSubmit Proof Design

This proof design has now entered the Level 1 implementation slice. The checked
in `.codex/` files prove only the local adapter shape; they do not prove that
the Codex GUI has loaded and trusted the hook until a real GUI run records the
pre-turn card and completion-review card.

### Hook Input

The proof hook consumes Codex `UserPromptSubmit` stdin JSON:

- `hook_event_name`: must be `UserPromptSubmit`;
- `prompt`: current user prompt;
- `cwd`: Codex session working directory, used to locate the project root;
- `session_id` and `turn_id`: recorded only as compact proof metadata;
- `permission_mode`: recorded as proof context.

The proof must not read or persist the full transcript. `transcript_path` is
not a stable interface and must not be used as the primary input.

### Semantic Classification Boundary

The hook remains thin, but it must make the semantic-classification boundary
explicit. A mounted hook that only forwards a prompt to the current
deterministic keyword router proves trigger stability, not semantic
classification quality.

The intended cooperation model is:

1. A host AI semantic classifier, when available before governance evaluation,
   produces a compact `host_semantic_intent` object.
2. The hook passes that object to JIKUO with the prompt or prompt summary,
   project root, client id, turn id, and trigger mode.
3. JIKUO owns final work-profile projection, policy-scope matching, evidence
   checks, and runtime-card rendering.
4. Deterministic keyword/path/tool signals remain fallback and conflict
   evidence. They are not the preferred classifier when a trustworthy host AI
   semantic intent is available.

The hook must not directly decide which policies apply. It may provide or
request semantic classification, but JIKUO remains the policy-distribution
authority.

Target compact shape:

```yaml
host_semantic_intent:
  schema: jikuo.host_semantic_intent.v0
  source_client: codex
  source_event: UserPromptSubmit
  provider: host_ai | jikuo_semantic_classifier | heuristic_fallback
  lifecycle_event: conversation_turn
  multi_intent: true | false
  primary_intent_ref: intent_1
  constraints:
    - no_file_write
    - no_commit
  intent_slices:
    - id: intent_1
      policy_scopes: [discussion]
      intent_class: design_discussion
      operation_class: design_review
      output_class: explanation
      rationale_summary: compact slice explanation
    - id: intent_2
      policy_scopes: [editing]
      intent_class: implementation_request
      operation_class: documentation_update
      output_class: repository_change
      rationale_summary: compact slice explanation
  work_profile:
    policy_scopes: [discussion | editing | progress_summary]
    intent_class: implementation_request | design_discussion | progress_summary | other
    operation_class: code_change | documentation_update | design_review | no_change | other
    output_class: repository_change | explanation | summary | other
  confidence: high | medium | low | unavailable
  rationale_summary: compact explanation without raw prompt text
```

`intent_slices` are optional for single-intent turns and required when the host
AI identifies multiple user intents. JIKUO must aggregate the final
`work_profile.policy_scopes` from the union of slice scopes, then preserve each
slice for card explanation and future execution planning. `primary_intent_ref`
is used only for ordering and summaries; it must not suppress other slice
scopes during policy distribution.

When a turn contains a negative constraint such as "do not edit files" or "only
discuss", the host semantic intent should record it in `constraints`. JIKUO
should keep the discussion scope as final and may record deterministic editing
keywords as conflict evidence, but it must not promote the turn to an editing
policy scope solely because the phrase contains words like "change" or "fix".

Examples:

```yaml
# "先解释方案，然后更新文档，最后总结进度"
host_semantic_intent:
  multi_intent: true
  primary_intent_ref: update_docs
  intent_slices:
    - id: explain_design
      policy_scopes: [discussion]
      intent_class: design_explanation
      operation_class: read_only
      output_class: explanation
    - id: update_docs
      policy_scopes: [editing]
      intent_class: implementation_request
      operation_class: documentation_update
      output_class: repository_change
    - id: summarize_progress
      policy_scopes: [progress_summary]
      intent_class: progress_summary
      operation_class: summarize
      output_class: summary
```

```yaml
# "只讨论怎么改，不要动文件"
host_semantic_intent:
  multi_intent: false
  constraints: [no_file_write]
  intent_slices:
    - id: discuss_change
      policy_scopes: [discussion]
      intent_class: design_discussion
      operation_class: no_change
      output_class: explanation
```

Implementation target for the later code slice:

- add an optional `host_semantic_intent` input to the conversation-turn router,
  agent-flow CLI, MCP adapter, and Codex hook proof script;
- normalize it into a schema-checked dict without storing raw prompt text;
- merge it inside `work_profile.build_work_profile()` before deterministic
  fallback;
- surface final `classification_basis`, `semantic_intent_status`,
  `intent_slices`, `constraints`, and conflicts in runtime cards;
- leave `policy_store.evaluate_work_profile_applicability()` consuming only the
  final `lifecycle_event` and aggregate `policy_scopes`.

Proof levels:

- Level 1, mounted invocation proof: `UserPromptSubmit` reliably calls JIKUO
  before model work and injects card links. This can pass even if
  `host_semantic_intent` is unavailable.
- Level 2, semantic-intent proof: the adapter supplies a model-quality
  `host_semantic_intent`, or clearly records that no host-time AI semantic
  provider exists for Codex yet.

Do not claim AI-semantic policy routing for Codex until Level 2 passes. If
Codex hooks expose only the raw prompt at `UserPromptSubmit` time, record the
semantic-intent provider as unavailable and keep deterministic routing as an
honest fallback.

### JIKUO Call

The proof script should call the local no-write router before the model works:

```powershell
python -B -m jikuo.agent_flow propose --event conversation_turn --project-root "<PROJECT_ROOT>" --trigger-mode mounted --user-phrase-stdin --format json
```

The CLI path is the first proof target because a hook command is an external
process. A later adapter may prefer MCP `jikuo.route_user_request` if the host
offers a reliable in-process MCP client boundary to hooks.

Proof notes should record only card links, status, and compact summaries. They
must not persist the full prompt text. The current hook passes the prompt to the
local CLI over stdin, not through process arguments. A later reusable hook pack
may still replace the CLI hop with MCP or an in-process API when the host offers
a reliable boundary.

### Hook Output

On success, the hook returns JSON with `hookSpecificOutput.additionalContext`
containing:

- JIKUO mounted pre-turn router status;
- semantic-intent status: `provided`, `unavailable`, or `heuristic_fallback`;
- latest card path;
- history card path;
- required follow-up tools, if any;
- instruction that durable writes remain guarded.

On failure:

- if mounted mode is required, return a visible block or warning instead of
  silently continuing;
- if the project is not configured for mounted mode, return degraded context
  that tells the model and user that JIKUO was callable but not strict.

### Success Criteria

- A new `conversation_turn` history card is written before the assistant starts
  substantive work.
- The hook output injects the latest JIKUO runtime links into model-visible
  context.
- The proof records whether semantic classification came from host AI,
  JIKUO semantic classifier, deterministic fallback, or no provider.
- A no-op turn still produces a visible `mounted_idle_tick`.
- A turn that requires follow-up reports the required JIKUO tool names before
  implementation proceeds.
- JIKUO failure is visible to the user; there is no silent bypass.

### Failure Criteria

- Codex does not run the hook in the GUI or CLI surface under test.
- The hook runs after the model has already started work.
- The hook cannot locate a stable project root.
- No runtime card is produced.
- The proof depends on Windows-only shell behavior or a private Codex API.
- The proof claims AI-semantic classification while only deterministic keyword
  routing actually ran.

### Implemented Level 1 Proof Files

Approved on 2026-05-19 for the first implementation slice:

- `<repo>/.codex/hooks.json`;
- `<repo>/.codex/hooks/jikuo_user_prompt_submit.py`;
- `<repo>/.codex/hooks/README.md`;
- `tests/codex_hook_tests.py`.

These files implement the thin Codex adapter:

- parse Codex `UserPromptSubmit` stdin JSON;
- locate the project root;
- call no-write `agent_flow propose --event conversation_turn`;
- return `hookSpecificOutput.additionalContext` with runtime links, policy
  counts, missing-evidence counts, and guarded-write reminders;
- report `semantic_intent_status=unavailable` until a later semantic proof
  adds host or classifier intent.

The hook is intentionally not a policy engine. It must not decide active-policy
applicability, perform durable writes, persist raw prompts, or claim
AI-semantic routing. The current implementation passes the prompt transiently
to the local CLI over stdin via `--user-phrase-stdin`, so prompt text is not
placed in the child process argument list.

An accepted proof note under `docs/integrations/proofs/` is still pending and
must be based on a real Codex GUI run, not only unit tests.

Current local verification:

- `python -B -m unittest tests.codex_hook_tests tests.document_registry_tests`
  passes.
- `.codex/hooks.json` parses as JSON.
- A local stdin smoke call to `.codex/hooks/jikuo_user_prompt_submit.py`
  returns `hookSpecificOutput.additionalContext` and creates a
  `conversation_turn` runtime history card.
- `agent_flow propose --user-phrase-stdin` is covered by regression tests and
  is the preferred Codex hook transport for prompt text.

This verification proves the script behavior only. It does not prove the Codex
GUI has loaded, trusted, or executed the hook.

## 4.3 Codex GUI End-To-End Trigger Flow

When the Codex hook, semantic-intent, and multi-intent work is implemented, the
Codex GUI path should behave as one governed turn pipeline:

1. User submits a prompt in Codex GUI.
2. Codex fires the project-local `UserPromptSubmit` hook before the model starts
   substantive work.
3. The hook reads only the minimum required context: project root, current
   prompt or prompt stream, session id, turn id, permission mode, and activation
   settings.
4. The hook obtains `host_semantic_intent` if a host AI or dedicated classifier
   is available at hook time. If not, it records
   `semantic_intent_status=unavailable`.
5. The hook calls JIKUO no-write routing, initially through
   `agent_flow propose --event conversation_turn`, later through a stable
   lifecycle-runner entry if accepted.
6. JIKUO builds the final work profile by merging explicit lifecycle context,
   host semantic intent, intent slices, negative constraints, deterministic
   path / keyword / tool signals, activation settings, and registry context.
7. JIKUO policy distribution uses only the final lifecycle event and aggregate
   policy scopes. Hook-supplied intent is evidence for the final classifier, not
   direct policy authority.
8. JIKUO writes runtime visibility: latest card, state summary, history card,
   lifecycle card links, semantic-intent status, final work profile, triggered
   policies, missing evidence, and required follow-up tools.
9. The hook returns Codex `additionalContext` containing the JIKUO runtime links,
   semantic-intent status, final scopes, triggered-policy summary, and required
   follow-up tools.
10. Codex starts the actual response or implementation with that JIKUO context
    already mounted.
11. During the turn, Codex may call MCP or CLI tools for guarded actions,
    evidence updates, or additional lifecycle checks. The hook itself never
    performs durable writes.
12. Before final delivery or commit, Codex runs `completion_review` so main-doc
    maintenance, evidence gaps, lifecycle links, and progress-summary business
    meaning are visible.
13. The final user response includes the relevant lifecycle card links and a
    concise summary of triggered policies, missing evidence, changes, and tests.

End-to-end acceptance requires all of the following:

- `UserPromptSubmit` fires before model work and cannot silently bypass JIKUO in
  mounted mode.
- The pre-turn card is visible through Codex injected context and
  `.jikuo/runtime/history/`.
- Semantic intent is reported as `provided`, `unavailable`, or
  `heuristic_fallback`; false AI-semantic claims are proof failures.
- Multi-intent prompts preserve `intent_slices`, aggregate policy scopes, and
  per-slice runtime-card explanation.
- Negative constraints such as `no_file_write` prevent keyword-only editing
  promotion when the host semantic intent is sufficiently confident.
- Codex receives required follow-up tools before implementation proceeds.
- Completion review produces a later lifecycle card and shows unresolved
  evidence status instead of relying on the last pre-turn card alone.
- Proof notes record card links, status, compact summaries, and pass/fail
  observations without storing raw prompts or raw transcripts.

## 4.4 Cross-Client Adapter Shape

The proof should keep a shared adapter contract separate from client-specific
glue:

| Concept | Shared contract | Client-specific glue |
|---|---|---|
| Input event | `user_turn_submitted` with current prompt and project root | Codex `UserPromptSubmit`, Claude hook event, Cursor extension event, VS Code extension event |
| Semantic input | optional `host_semantic_intent` with source, confidence, scopes, and compact rationale | host AI metadata, a client-side classifier call, or explicit `unavailable` |
| JIKUO call | no-write `conversation_turn` router, preferably MCP when reliable, CLI fallback otherwise | client config and process launch details |
| Output | allow / block / degraded plus runtime card links and follow-up tools | Codex `additionalContext`, Claude hook output, IDE notification / injected context |
| Failure | visible degradation or refusal, never silent bypass | host-specific UI or hook failure channel |
| Durable writes | never performed by the hook | guarded MCP / CLI tools only after user approval |

This keeps Codex as the first proof target without turning Codex behavior into
the JIKUO architecture.

## 5. Dependencies

- `JIKUO-INTG-03`: strict mounted harness adapter contract
- `JIKUO-INIT-02`: reviewed configuration onboarding
- `docs/integrations/mcp_client_proof_playbook.md`: cross-client proof workflow
- private GitHub preview clone proof for realistic user setup

## 6. Boundary

Until this task is accepted with proof, Codex should be described as:

> MCP-capable and instruction-configurable, but not proven as a strict pre-turn
> mounted harness.

Additional boundaries:

- Do not treat checked-in `.codex/` proof files as accepted strict-mounted
  behavior until the GUI proof is recorded.
- Do not use plugin-bundled hooks as the first proof path because plugin hooks
  are opt-in.
- Do not claim `PreToolUse` alone proves strict mounted behavior; it is a later
  tool-stage guardrail, not the user-turn entry point.
- Do not persist raw prompts or transcripts as proof evidence.
