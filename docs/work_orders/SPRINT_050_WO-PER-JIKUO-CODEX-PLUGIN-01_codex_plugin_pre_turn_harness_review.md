# SPRINT_050_WO-PER-JIKUO-CODEX-PLUGIN-01: Codex Plugin Pre-Turn Harness Review

> **Status**: Level 1 project-local proof files implemented and local stdin smoke passed; host semantic-intent input and work-profile merge path implemented for CLI / MCP / Codex hook proof; MCP Sampling semantic-provider probe implemented as an optional client-mediated proof path; AI semantic routing MVP contract anchored in `JIKUO-AI-SEMROUTE-01`; official Codex hook surface reviewed on 2026-05-19; Codex GUI `additionalContext` visibility has been observed; a 2026-05-28 GUI probe exposed nested-Python subprocess timeout, so the hook now defaults to in-process JIKUO invocation; fresh GUI smoke accepted the in-process pre-turn additionalContext path; host-time semantic provider acceptance, multi-intent semantic proof, and full lifecycle strict-mounted acceptance still pending.
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

`JIKUO-AI-SEMROUTE-01` is the MVP authority for the semantic-routing shape.
The Codex hook can invoke JIKUO and inject `additionalContext`; it cannot, by
itself, force the host AI to classify the turn before tool invocation. Host
semantic intent is accepted only when the host AI, a client-mediated Sampling
provider, or a future wrapper / plugin supplies a compact
`host_semantic_intent` object.

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

Semantic routing should map user intent to policy scope, not internal agent
verbs directly:

```text
user_intent -> policy_scope -> process_contract -> execution_boundary -> response_contract
```

The host or classifier may describe what the user wants, what constraints the
user set, and what output evidence the user expects. JIKUO then compiles that
input into final `work_profile.policy_scopes` and visible runtime explanation.
The agent's dynamic `see / think / act / speak` loop is execution vocabulary:
it explains how work is performed and reported, but it is not the primary
policy-scope axis. Policy can still govern how the agent thinks, evaluates,
and sequences work through `process_contract`. The final answer is always
governed by universal response policies plus the policies selected for the
current user intent.

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
      user_expression: short user phrase, not the full prompt
      policy_scopes: [discussion]
      intent_class: design_discussion
      operation_class: design_review
      output_class: explanation
      requested_outcome: compare options without repository writes
      process_contract: align concepts and critique the proposal before implementation details
      execution_boundary: read-only
      response_contract: explain recommendation, risks, and open questions
      rationale_summary: compact slice explanation
    - id: intent_2
      user_expression: short user phrase, not the full prompt
      policy_scopes: [editing]
      intent_class: implementation_request
      operation_class: documentation_update
      output_class: repository_change
      requested_outcome: update project documentation
      process_contract: keep source-of-truth, projection, and transitional-cache boundaries explicit
      execution_boundary: repository writes allowed after governed pre-work
      response_contract: report changed files, checks, evidence, and card links
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

For the MVP, valid aggregate `policy_scopes` remain only `discussion`,
`editing`, and `progress_summary`. More specific ideas such as
first-principles alignment, data-model boundary review, distribution review, or
verification are expressed as policy titles, required actions, evidence types,
and response contracts, not as new scope labels.

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
- normalize it into a prompt-free schema-checked dict;
- merge it inside `work_profile.build_work_profile()` before deterministic
  fallback affects final policy scopes;
- surface `semantic_intent_status`, `intent_slices`, `constraints`, and
  deterministic/semantic conflicts in runtime cards;
- leave `policy_store.evaluate_work_profile_applicability()` consuming only the
  final `lifecycle_event` and aggregate `policy_scopes`.

Implemented on 2026-05-19 as the Level 2A local semantic-input slice:

- `agent_flow propose` accepts `--host-semantic-intent-json`;
- MCP `jikuo.route_user_request` and `jikuo.propose_policy_suggestions` accept
  `host_semantic_intent`;
- the Codex proof hook accepts `host_semantic_intent` / `hostSemanticIntent` in
  hook stdin and forwards the compact object to JIKUO;
- `work_profile.build_work_profile()` records the normalized semantic object in
  `basis.host_semantic_intent`, uses aggregate semantic policy scopes, preserves
  `intent_slices`, honors negative constraints such as `no_file_write`, and
  records keyword/semantic conflicts;
- deterministic fallback now includes broader Chinese and English keyword
  coverage for discussion, research, editing, progress, configuration, and
  policy-governance turns, plus no-edit natural-language constraints such as
  "only discuss" and "do not edit files";
- runtime markdown renders semantic status, provider, constraints, slice count,
  conflict count, and the policy-contract fields
  (`requested_outcome`, `process_contract`, `execution_boundary`,
  `response_contract`) when provided.

This is not yet Codex GUI AI-semantic proof. It only means JIKUO can consume a
compact semantic classification when a host or classifier provides one. If no
provider is available, the hook still reports `semantic_intent_status` as
`unavailable` and deterministic routing remains the honest fallback.

If semantic classification is wrong, Codex should not rely on a special
correction workflow. The user can correct the interpretation in ordinary
natural language, producing a new `conversation_turn` that JIKUO routes again.
The prior card remains runtime history, not a durable binding that must be
rolled back.

Contract-field proof for the Codex GUI chain is narrower than general policy
proof. The hook only transports and surfaces fields; it must not decide policy
applicability. Acceptance for later slices should show:

- `requested_outcome`, `process_contract`, `execution_boundary`, and
  `response_contract` are present in the compact semantic payload or honestly
  absent;
- JIKUO renders the normalized fields in card/state output without raw prompt
  persistence; implemented for local runtime-card projection on 2026-05-21;
- the agent plan or completion summary names how the relevant contract shaped
  work;
- any hard effect boundary is enforced through no-write, guarded-write, or
  missing-evidence reporting in JIKUO, not inside the hook script.

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

### MCP Sampling Provider Probe

MCP Sampling is a useful Level 2B probe, not a replacement for the Codex hook.
The official MCP Sampling model lets a server send `sampling/createMessage` to
the MCP client during a tool call, while the client keeps control over model
access, model selection, permissions, and human review.

JIKUO now exposes `jikuo.probe_sampling_semantic_intent` for this purpose:

- it asks a Sampling-capable MCP client for compact
  `host_semantic_intent`;
- it routes the same turn through existing JIKUO `conversation_turn` logic with
  that semantic intent when available;
- it reports `sampling_semantic_intent.status=provided`, `unavailable`, or
  `invalid`;
- it redacts exact prompt echoes from returned proof data;
- it remains no-write except for normal `.jikuo/runtime/` visibility.

This can prove that a client can act as a semantic provider during an MCP tool
call. It cannot prove that Codex runs JIKUO before model work. Strict mounted
Codex proof still requires `UserPromptSubmit` or an equivalent host boundary to
fire before substantive model execution and inject the JIKUO card context.

### JIKUO Call

The proof script should call the local no-write router before the model works.
The current project-local hook defaults to the in-process API equivalent of:

```powershell
python -B -m jikuo.agent_flow propose --event conversation_turn --project-root "<PROJECT_ROOT>" --trigger-mode mounted --user-phrase-stdin --format json
```

The CLI form remains a diagnostic fallback behind
`JIKUO_HOOK_EXECUTION_MODE=subprocess`. It is not the preferred GUI path after
the 2026-05-28 observation showed that Codex can load the hook and inject
visible degradation while the nested Python CLI call still times out.
A later adapter may prefer MCP `jikuo.route_user_request` if the host offers a
reliable in-process MCP client boundary to hooks.

Proof notes should record only card links, status, and compact summaries. They
must not persist the full prompt text. The current hook passes the prompt to
the local JIKUO in-process API by default; in subprocess diagnostic mode, it
passes the prompt to the local CLI over stdin, not through process arguments.
A later reusable hook pack may still replace the project-local API call with
MCP when the host offers a reliable boundary.

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
- call no-write `agent_flow` `conversation_turn` routing in-process by
  default, with subprocess CLI retained as an explicit diagnostic mode;
- return `hookSpecificOutput.additionalContext` with runtime links, policy
  counts, missing-evidence counts, and guarded-write reminders;
- report `semantic_intent_status=unavailable` until a later semantic proof
  adds host or classifier intent.

The hook is intentionally not a policy engine. It must not decide active-policy
applicability, perform durable writes, persist raw prompts, or claim
AI-semantic routing. The current implementation passes the prompt transiently
to the local in-process JIKUO API by default. If
`JIKUO_HOOK_EXECUTION_MODE=subprocess` is set, prompt text is passed over stdin
via `--user-phrase-stdin` and is not placed in the child process argument list.

The current implementation also passes compact `host_semantic_intent` through
`--host-semantic-intent-json` when the hook input contains that field. The hook
does not generate that semantic intent by itself; it only transports and labels
it so JIKUO can merge it into the final work profile.

A proof note under `docs/integrations/proofs/` now accepts the narrower Codex
GUI pre-turn `additionalContext` injection surface for the 2026-05-21 observed
environment. A later 2026-05-28 observation showed a GUI subprocess timeout
regression/degradation and triggered the in-process remediation. Full
strict-mounted lifecycle proof is still pending and must be based on a real
Codex GUI run that also links completion-review lifecycle output, not only unit
tests.

Current Codex Desktop observation:

- `docs/integrations/proofs/PROOF-2026-05-21-codex-gui-hook-current-thread-observation.md`
  records the 2026-05-21 current-thread observation. Before hook enablement, no
  automatic hook-produced pre-turn card was observed before manual JIKUO calls.
  After the user enabled the Codex GUI hook, the hook first injected visible
  degraded context but the JIKUO command timed out. This proved hook invocation
  and visible degradation.
- Timeout remediation updated the hook-owned JIKUO subprocess timeout to 70
  seconds and the Codex hook wrapper timeout to 90 seconds. A fresh GUI probe
  then showed successful JIKUO `additionalContext` before the assistant answer,
  with `semantic_intent_status=unavailable`, one triggered policy, zero missing
  evidence, and history card
  `.jikuo/runtime/history/20260521T004612Z_proposal_264d3469ea.md`.
- A 2026-05-28 GUI probe again showed visible JIKUO `additionalContext`, but
  the mounted context was degraded: `JIKUO command timed out after 70s;
  python=C:\Python314\python.exe`. This proves the hook surface was loaded and
  visible, but the nested Python CLI call is not stable enough as the default
  GUI path.
- `docs/integrations/proofs/PROOF-2026-05-28-codex-gui-hook-subprocess-timeout.md`
  records the timeout observation and remediation boundary.
- The current remediation keeps the visible failure boundary and changes the
  default project-local hook call to in-process JIKUO invocation. Subprocess CLI
  remains available only through `JIKUO_HOOK_EXECUTION_MODE=subprocess` for
  diagnostics.
- Fresh GUI success after the in-process remediation is accepted for the
  project-local pre-turn `additionalContext` path. The proof does not accept
  host-time AI-semantic routing, multi-intent semantic slicing, or full
  lifecycle strict-mounted behavior.

Current local verification:

- `python -B -m unittest tests.codex_hook_tests tests.document_registry_tests`
  passes.
- `.codex/hooks.json` parses as JSON.
- A local stdin smoke call to `.codex/hooks/jikuo_user_prompt_submit.py`
  returns `hookSpecificOutput.additionalContext` and creates a
  `conversation_turn` runtime history card.
- in-process hook invocation is covered by regression tests and local stdin
  smoke; `agent_flow propose --user-phrase-stdin` remains covered as the
  subprocess diagnostic fallback.

This local verification proves the script behavior. The Codex GUI observation
above separately proves that the enabled project-local hook can inject pre-turn
JIKUO `additionalContext`, including visible degradation for failed subprocess
diagnostic paths and successful in-process remediation. This still does not
prove host-time AI-semantic routing or full lifecycle strict-mounted behavior.

## 4.3 Codex GUI End-To-End Trigger Flow

When the remaining semantic-intent, multi-intent, and lifecycle-runner work is
implemented, the Codex GUI path should behave as one governed turn pipeline:

1. User submits a prompt in Codex GUI.
2. Codex fires the project-local `UserPromptSubmit` hook before the model starts
   substantive work.
3. The hook reads only the minimum required context: project root, current
   prompt or prompt stream, session id, turn id, permission mode, and activation
   settings.
4. The hook obtains `host_semantic_intent` if a host AI or dedicated classifier
   is available at hook time. If not, it records
   `semantic_intent_status=unavailable`.
5. The hook calls JIKUO no-write routing through the in-process `agent_flow`
   API by default, or through subprocess CLI only in diagnostic mode. A later
   stable lifecycle-runner entry may replace this once accepted.
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
13. The final user response includes a concise summary of triggered policies,
    missing evidence, changes, and tests, then ends with an `Observed Lifecycle`
    footer that lists the relevant lifecycle card links as `node_name:
    card_link`.

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
