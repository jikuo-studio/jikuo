# SPRINT_050_WO-PER-JIKUO-INTG-03: Strict Mounted Harness Adapter Contract

> **Status**: Contract / planning accepted; implementation deferred to client proof and later adapter slices.
> **Product meaning**: users who choose mounted mode should get real pre-turn JIKUO execution, not just an instruction that the host Agent may or may not follow.
> **Boundary**: this slice defines the adapter contract. It does not implement a Claude hook, Codex plugin, Cursor extension, VS Code extension, Studio proxy, or Agent SDK wrapper.

## 1. Why This Slice Exists

JIKUO now has:

- project activation settings in `.jikuo/activation_settings.yaml`
- visible `semantic` vs `mounted` router behavior
- MCP tools for configuration review, activation settings, conversation routing, and policy suggestions
- instruction files for Codex, Claude Code, Cursor, and VS Code Copilot

That is enough for a client to know how JIKUO should run. It is not enough to
guarantee that JIKUO runs before every user turn.

Strict mounted mode needs an adapter at the boundary where the user turn enters
the host environment.

## 2. Three-Layer Model

| Layer | Responsibility | Current state |
|---|---|---|
| Core | interpret trigger mode, route `conversation_turn`, produce cards, keep writes guarded | implemented |
| MCP / CLI surface | expose configuration, activation settings, router, policy suggestions, and guarded writes to clients | implemented |
| Host adapter | actually call JIKUO before each user turn when mounted mode is active | contract only |

The core must remain integration-neutral. It should not import or depend on a
specific desktop client, IDE, hook system, or Agent SDK.

MCP availability is not enough to make a host strict. If activation settings
are missing, JIKUO reports `strict_mount_status=not_configured`. If mounted mode
is configured without a pre-turn adapter, JIKUO reports
`strict_mount_status=degraded_instruction_only`. In both cases the user must see
that JIKUO is callable but not guaranteed to run before every turn.

## 3. Adapter Contract

A strict mounted adapter must:

1. Locate the project root and read `.jikuo/activation_settings.yaml`.
2. If `desired_trigger_mode` is `mounted`, call JIKUO before the host Agent
   handles each user turn.
3. Prefer MCP `jikuo.route_user_request` when available; use CLI
   `python -B -m jikuo.agent_flow propose --event conversation_turn` only as a
   fallback.
4. Pass only the current user turn or a compact user-turn summary. Do not store
   raw chat transcripts.
5. Surface `card_markdown` verbatim when the client can display it.
6. Always surface `.jikuo/runtime/last_card.md` or `jikuo show --last-card` as
   the out-of-band verification path when card display is incomplete.
7. Run required no-write follow-up tools, such as
   `jikuo.propose_policy_suggestions`, before implementation continues when the
   router asks for them.
8. Refuse or visibly degrade when mounted execution cannot run. A mounted
   adapter must not silently continue as if governance happened.
9. Keep durable writes behind existing guarded-write tools that require
   explicit confirmation and approval phrase.

## 3.1 Shared Proof Contract

Every client proof should use the same conceptual adapter contract even when
the host-specific hook mechanism differs:

| Field | Meaning |
|---|---|
| `client_id` | `codex`, `claude`, `cursor`, `vscode_copilot`, `agent_sdk`, or another explicit host id |
| `client_event` | the host event that fires before user-turn handling, such as Codex `UserPromptSubmit` |
| `project_root` | explicit root passed to JIKUO; do not infer from recent cards |
| `user_turn_summary` | current prompt or compact summary, never a stored raw transcript |
| `host_semantic_intent` | optional compact AI semantic classification from the host or a classifier provider; include source, confidence, aggregate scopes, optional `intent_slices`, constraints, and compact rationale when available |
| `trigger_mode` | `mounted`, `semantic`, or `ask`, read from activation settings when available |
| `jikuo_call` | MCP `jikuo.route_user_request` when reliable, CLI `python -B -m jikuo.agent_flow propose --event conversation_turn` as fallback |
| `display_result` | card markdown or runtime links surfaced back to the user / model |
| `failure_result` | visible block or degradation; silent bypass is a proof failure |

## 3.2 Classification Cooperation Contract

Strict mounted adapters must separate three responsibilities:

- Host / classifier semantic judgment: classify the user turn with AI-level
  semantics when the host can provide it before governance evaluation.
- Adapter transport: pass that compact classification to JIKUO and surface the
  returned card links. The adapter does not decide policy applicability.
- JIKUO authority: merge host semantic intent, deterministic signals, explicit
  lifecycle events, activation settings, and registry context into the final
  work profile used for policy distribution.

Final classification precedence should be explicit and visible:

1. Explicit user-approved lifecycle or guarded command context.
2. Host AI semantic intent or a dedicated JIKUO semantic classifier result,
   when available with sufficient confidence.
3. Deterministic keyword/path/tool signals as fallback and conflict evidence.
4. Conservative fallback with degraded status when neither AI nor deterministic
   signals are sufficient.

If AI semantic intent and deterministic signals disagree, the runtime card
should show the conflict instead of silently picking one. The policy evaluator
must consume the final JIKUO work profile, not raw host claims.

### 3.2.1 Intent-To-Scope Contract

The semantic-routing contract is:

```text
user_intent -> policy_scope -> execution_boundary -> response_contract
```

This is intentionally different from treating the agent's internal action
grammar as the policy-routing source:

- `user_intent` is what the user is asking the AI to accomplish, including
  explicit constraints such as "do not edit files" or "commit the change".
- `policy_scope` is the governed distribution class that determines which
  active policies should be considered. Examples include `discussion`,
  `editing`, `progress_summary`, `verification`, `document_governance`, and
  `policy_management`.
- `execution_boundary` states what effects are allowed, blocked, or require
  explicit confirmation before the agent acts.
- `response_contract` states what the final answer must report: evidence,
  changed files, tests, missing evidence, card links, follow-up decisions, or
  business meaning.

`see`, `think`, `act`, and `speak/report` are still useful as dynamic execution
and evidence vocabulary, but they are not the primary policy-scope taxonomy.
Every turn eventually speaks back to the user, so "speak" cannot be the scope
by itself. The response is the policy-governed delivery surface: universal
policies and current-intent policies shape what must be said. When an `act`
step has real side effects, the same policy scope must also govern execution
before and during the action, not only the final report.

MCP Sampling is an optional classifier-provider route under this contract. It
allows the JIKUO MCP server to request `sampling/createMessage` from a client
during a tool call, but the client controls model access, model choice,
permissions, and any human review. Therefore:

- Sampling can provide `host_semantic_intent` for policy distribution quality;
- Sampling support or failure must be reported as explicit classifier evidence;
- Sampling unavailable must fall back to deterministic routing without claiming
  AI-semantic routing;
- Sampling by itself is not a strict mounted adapter, because an MCP tool call
  is still user/model-mediated unless a separate host hook invokes it before
  ordinary model work.

Multi-intent turns are normal and must be modeled explicitly. One user turn has
one lifecycle position, but it may contain multiple intent slices:

```yaml
host_semantic_intent:
  multi_intent: true
  primary_intent_ref: update_docs
  intent_slices:
    - id: discuss_design
      policy_scopes: [discussion]
      intent_class: design_discussion
      operation_class: read_only
      output_class: explanation
    - id: update_docs
      policy_scopes: [editing]
      intent_class: implementation_request
      operation_class: documentation_update
      output_class: repository_change
      requested_outcome: update mounted-hook documentation
      execution_boundary: repository writes allowed after governed pre-work
      response_contract: report changed docs, checks, card links, and follow-ups
    - id: summarize
      policy_scopes: [progress_summary]
      intent_class: progress_summary
      operation_class: summarize
      output_class: summary
```

JIKUO must aggregate final policy scopes from the union of intent-slice scopes,
unless an explicit negative constraint removes or gates a scope. `primary` is
only a summary/order hint; it must not block other slices from policy
distribution. The runtime card should show both the aggregate final
`work_profile` and the per-slice explanation so users can see why several
policies triggered from one instruction.

Negative constraints have to be represented separately from keyword signals.
For example, "only discuss how to change this, do not edit files" should produce
`constraints: [no_file_write]`, final scope `discussion`, and a conflict note if
editing keywords were detected. It should not become an editing task solely
because deterministic keywords include "change".

Minimum implementation checklist for a later code slice:

- add `host_semantic_intent` input to CLI, MCP adapter schemas, and hook proof
  payloads; implemented for the local Level 2A input slice on 2026-05-19;
- add schema normalization for `intent_slices`, aggregate scopes, constraints,
  confidence, provider, and compact rationale; implemented as prompt-free
  `basis.host_semantic_intent`;
- merge host semantic intent in `work_profile.build_work_profile()` ahead of
  keyword fallback; implemented for final aggregate scopes and negative
  constraints;
- record deterministic keyword/path/tool agreement or conflict in
  `basis.deterministic_signals` / `basis.conflicts`; implemented for
  keyword-vs-constraint conflicts, with bilingual keyword fallback coverage for
  Chinese and English user turns;
- keep policy evaluator input stable: final `lifecycle_event` plus aggregate
  `policy_scopes`;
- keep `requested_outcome`, `execution_boundary`, and `response_contract` as
  router / card explanation fields until a separate reviewed slice decides
  whether they need schema enforcement;
- add runtime-card rendering and tests for single-intent, multi-intent,
  negative-constraint, host-unavailable fallback, and host/keyword conflict;
  local tests now cover host-provided single-intent, multi-intent, and
  negative-constraint conflicts, while real host-time provider proof remains
  pending.

The proof conclusion should distinguish:

- MCP availability;
- instruction-following reliability;
- host-level pre-turn hook availability;
- host-time AI semantic-intent availability;
- actual JIKUO router execution before model work.

Only the last item can support a strict mounted claim.

## 3.3 End-To-End Client Trigger Contract

An accepted strict client adapter must prove more than hook discovery. The
end-to-end governed turn is:

1. Host receives a user turn.
2. Host pre-turn boundary runs before model work.
3. Adapter collects minimal context and activation settings.
4. Adapter provides or honestly marks semantic intent status.
5. Adapter calls JIKUO no-write routing / lifecycle start.
6. JIKUO produces final work profile and policy distribution.
7. Adapter surfaces card links, triggered-policy summary, missing evidence, and
   follow-up tools back to the host model / user.
8. Host executes the actual work while honoring the mounted JIKUO context.
9. Guarded writes remain behind existing approval-based tools.
10. Completion review runs before final delivery or commit and produces a later
    lifecycle card.

This contract is client-neutral. Codex may use `UserPromptSubmit` and
`additionalContext`; Claude, Cursor, VS Code, Agent SDK wrappers, or a Studio
entry point may use different host mechanics. The required observable behavior
is the same: JIKUO must run before substantive work, the model must see the
result, and completion evidence must be visible before closure.

Minimum observable artifacts for an end-to-end proof:

- pre-turn history card for the user prompt;
- injected or displayed card link before model work;
- semantic-intent status and final aggregate policy scopes;
- visible per-slice explanation for multi-intent turns;
- visible conflict or fallback when deterministic signals disagree or are the
  only classifier;
- completion-review history card for the same governed turn;
- final response or proof note linking both lifecycle cards;
- no raw prompt / transcript persisted as proof evidence.

## 4. Client Priority

| Client / host | Near-term route | Strict-mounted status |
|---|---|---|
| Claude Code GUI | MCP + `CLAUDE.md`, then hook proof when hook behavior is stable | best first strict adapter candidate |
| Codex Desktop / Codex CLI | MCP + `AGENTS.md` proof first | strict adapter depends on a stable plugin / hook / app extension point |
| Cursor | MCP + `.cursorrules` proof first | strict adapter depends on a stable extension / hook-like entry |
| VS Code + GitHub Copilot Agent mode | MCP + `.github/copilot-instructions.md` proof first | strict adapter likely needs a VS Code extension or supported agent hook |
| Agent SDK-built agents | wrapper package calls JIKUO before each user turn / agent step | useful for custom agents, not a replacement for desktop GUI proof |
| Studio / local proxy | product-owned entry point routes user turns through JIKUO first | strongest long-term control, deferred until product architecture stabilizes |

## 5. Acceptance Criteria For A Future Adapter Slice

- The adapter reads `.jikuo/activation_settings.yaml` and respects `ask`,
  `semantic`, and `mounted`.
- If `.jikuo/activation_settings.yaml` is missing, the adapter or router
  surfaces a configuration review instead of silently falling back to normal
  task execution.
- If mounted mode is requested but no pre-turn adapter is active, the client
  surfaces a degraded / non-strict status.
- If host AI semantic intent is unavailable, the client records
  `semantic_intent_status=unavailable` and JIKUO may use deterministic fallback;
  this must not be described as AI-semantic routing.
- If one user instruction contains discussion, editing, and summary intents,
  the final work profile includes all relevant aggregate scopes and the runtime
  card shows per-slice intent explanations.
- In mounted mode, a user turn with no obligation still produces a visible
  `mounted_idle_tick`.
- The same runtime card is visible through chat, `.jikuo/runtime/last_card.md`,
  and `jikuo show --last-card`.
- If JIKUO is unavailable, the client receives a visible failure card or clear
  failure message.
- No raw transcript, approval phrase, or local-only response field leaks outside
  the configured transport boundary.
- Guarded writes remain guarded; the adapter cannot convert no-write review
  into durable writes without explicit user approval.

## 6. Current Stop Point

The next slice is not more kernel work. It is client proof:

- verify the current 18-tool MCP surface in the selected GUI clients
- verify Codex `UserPromptSubmit` hook proof as the current first Codex
  host-boundary candidate
- preserve proof artifacts for users
- record which clients support only MCP + instructions and which can support a
  true pre-turn adapter

Implementation of a strict adapter should wait until that proof identifies the
most reliable first host boundary.
