# SPRINT_050_WO-PER-JIKUO-HOSTADAPT-01: Host Adapter Contract

> **Status**: Contract scaffold implemented for cross-client input/result normalization, raw prompt redaction, Codex project-local hook consumption, and Codex GUI contract-line projection proof. Selected governed editing / write-capable MCP entry points now return no-write `semantic_intent_precondition` feedback when `host_semantic_intent` is missing, and an external Codex GUI MCP proposal-tool smoke accepted direct `host_semantic_intent` re-call passthrough. Host-specific wrappers/plugins remain future slices.
> **Date**: 2026-05-28
> **JIKUO layer**: integration / strict mounted harness.
> **Business meaning**: JIKUO should be portable across Codex, Claude, Cursor, VS Code, and future wrappers without baking one client's hook behavior into the core governance model.

## 1. Purpose

This work order defines the thin host adapter contract between an AI host and
JIKUO. The contract is intentionally smaller than any specific client:

```text
host event
-> host adapter turn input
-> JIKUO no-write routing / runtime visibility
-> host adapter turn result
-> client-specific display or degradation channel
```

The goal is to keep JIKUO's protocol portable while allowing every host to use
its own hook, plugin, extension, or wrapper mechanism.

## 2. Layer Split

| Layer | Portable? | Responsibility |
|---|---:|---|
| JIKUO core | yes | normalize work profile, evaluate policies, write runtime cards, keep durable writes guarded |
| Host adapter contract | yes | define common input/result fields, privacy posture, and proof status |
| Host adapter implementation | no | map Codex, Claude, Cursor, VS Code, or another host's API into the common contract |
| Host semantic provider | partially | provide compact `host_semantic_intent` when the host can do so before or during JIKUO routing |

The contract must remain usable even when no AI semantic provider is available.
In that case the adapter reports `semantic_intent_status=unavailable`, and
JIKUO uses deterministic fallback/conflict evidence honestly.

## 3. Turn Input Contract

Schema: `jikuo.host_adapter.turn_input.v0`

Minimum fields:

```yaml
client_id: "codex" # codex | claude | cursor | vscode_copilot | agent_sdk | other
client_event: "UserPromptSubmit"
project_root: "D:/personal_project/Jikuo"
session_id: "host session id if available"
turn_id: "host turn id if available"
trigger_mode: "mounted" # mounted | semantic | ask
user_turn_summary: "<redacted_user_turn> or compact summary"
user_turn_summary_status: "provided_redacted" # provided_compact | provided_redacted | not_provided
host_semantic_intent:
  status: "provided" # provided | unavailable | invalid | heuristic_fallback
```

Privacy rules:

- The adapter may receive a raw prompt or prompt stream from the host.
- The normalized contract must not persist the raw prompt or transcript.
- If only raw prompt is available, output `user_turn_summary:
  <redacted_user_turn>` and `user_turn_summary_status: provided_redacted`.
- Short `host_semantic_intent.intent_slices[].user_expression` may be rendered
  when supplied as compact semantic metadata.
- Raw prompt echoes in failure summaries must be replaced with
  `<REDACTED_PROMPT_ECHO>`.

Implementation placeholder:

- `src/jikuo/integrations/host_adapter_contract.py`
- `tests/host_adapter_contract_tests.py`

The placeholder normalizes input and result dictionaries only. It does not run
hooks, call a model, decide policy applicability, or perform durable writes.

## 4. Turn Result Contract

Schema: `jikuo.host_adapter.turn_result.v0`

Minimum fields:

```yaml
status: "ok" # ok | degraded | blocked
semantic_intent_status: "provided" # provided | unavailable | invalid | heuristic_fallback
card_links:
  - "[last_card.md](D:/.../.jikuo/runtime/last_card.md)"
policy_trigger_summary:
  triggered_policy_count: 2
missing_evidence_summary:
  missing_evidence_count: 1
next_required_actions:
  - "jikuo.propose_task_start"
failure_summary: null
```

The result is display/proof data. It is not policy evidence by itself and does
not satisfy missing evidence requirements unless a separate policy explicitly
accepts an adapter proof evidence item.

## 5. Provider Levels

| Level | Meaning | Current status |
|---|---|---|
| L1 mounted invocation | adapter calls JIKUO before host work and injects links/context | Codex project-local hook accepted for in-process pre-turn additionalContext |
| L2A semantic transport | adapter can pass explicit compact `host_semantic_intent` when available | implemented locally in CLI/MCP/Codex hook proof paths |
| L2B client-mediated Sampling | JIKUO asks a Sampling-capable client for semantic intent during a tool call | MCP probe implemented; real client support pending |
| L3 host-time provider | wrapper/plugin controls a classifier before JIKUO routing | future; not proven |
| L4 full lifecycle strict mounted | pre-turn plus completion-review linkage is guaranteed and visible | future; not proven |

Do not collapse these levels. A Codex hook that injects `additionalContext`
does not prove host-time semantic classification. A Sampling response does not
prove pre-turn strict mounting.

## 5.1 Semantic Contract Enforcement Gap

The host adapter contract currently transports semantic intent when supplied
and honestly reports `semantic_intent_status=unavailable` when it is missing.
That is correct but incomplete for governed editing / write-capable work.

The accepted implementation is a tool-side precondition, not a thicker adapter:

- if a pure discussion turn lacks `host_semantic_intent`, the adapter may allow
  deterministic fallback and report the degraded basis;
- if a governed editing / write-capable entry point lacks valid
  `host_semantic_intent`, selected JIKUO MCP entry points return a no-write
  `semantic_intent_precondition` / `precondition_unmet` result with the compact
  schema and ask the host AI to classify and re-call;
- those selected proposal tools accept `host_semantic_intent` directly on the
  re-call, so the host adapter contract is not limited to router-only tools;
- external Codex GUI MCP smoke on 2026-05-31 accepted that direct re-call path
  with `status=review`, `host_semantic_intent.status=provided`,
  `semantic_intent_evidence.status=ok`, and no returned precondition;
- this precondition must not call a model, decide policy applicability, or
  persist raw prompt text;
- wrapper / plugin work remains future work after this lighter contract is
  tried in real GUI / MCP use.

## 6. Codex Implementation Path

### Current accepted path: project-local hook

Current files:

- `.codex/hooks.json`
- `.codex/hooks/jikuo_user_prompt_submit.py`
- `.codex/hooks/README.md`

Accepted capability:

```text
Codex UserPromptSubmit
-> project-local hook
-> Host Adapter Turn Input normalization
-> in-process JIKUO conversation_turn routing
-> Host Adapter Turn Result normalization
-> additionalContext with runtime links and policy summary
```

Accepted status:

- pre-turn `additionalContext` is visible in Codex GUI;
- in-process invocation avoids nested-Python timeout observed on 2026-05-28;
- the project-local hook maps stdin into `jikuo.host_adapter.turn_input.v0`
  and renders a `jikuo.host_adapter.turn_result.v0` summary;
- a 2026-05-28 Codex GUI smoke showed that contract summary line in model
  `additionalContext`, with history card
  `.jikuo/runtime/history/20260528T122001Z_proposal_264d3469ea.md`;
- failures remain visible instead of silent.

Not accepted:

- the hook cannot access current-turn model reasoning before the model runs;
- host-time semantic provider is still unavailable;
- full lifecycle strict-mounted proof is still pending.

### Feasible next Codex steps

1. Continue returning `semantic_intent_status=unavailable` unless a real
   provider supplies compact `host_semantic_intent`.
2. Add an optional explicit semantic-intent field for future Codex wrapper or
   plugin channels. The project-local hook may transport it, but must not claim
   it generated the semantic classification.
3. Use MCP Sampling as an optional Codex-adjacent probe when the client supports
   it. Sampling is useful classifier evidence, not strict pre-turn proof.
4. Only promote Codex to host-time semantic provider after a wrapper/plugin or
   official host capability proves:
   - classifier runs before JIKUO routing;
   - `semantic_intent_status=provided` appears in runtime cards;
   - intent slices are visible;
   - raw prompt is not persisted;
   - policy scopes affect policy distribution through the existing evaluator
     boundary.

### Future Codex wrapper/plugin path

The stable target is:

```text
user prompt
-> Codex wrapper/plugin receives turn
-> wrapper/plugin obtains host_semantic_intent from host AI or classifier
-> wrapper/plugin normalizes Host Adapter Turn Input
-> wrapper/plugin calls JIKUO
-> wrapper/plugin injects additionalContext/runtime links
-> Codex model performs the user task
-> completion_review produces linked lifecycle output before final delivery
```

This future wrapper/plugin may be packaged differently from project-local
hooks, but it should reuse the same contract fields.

## 7. Stop Boundaries

- Do not make this contract call a model.
- Do not make this contract decide policy applicability.
- Do not persist raw prompts or transcripts in normalized adapter records.
- Do not treat Codex-specific hook behavior as the architecture for all hosts.
- Do not claim L3 host-time semantic provider acceptance until a real provider
  smoke proves it.
- Do not claim L4 strict lifecycle acceptance until pre-turn and
  completion-review cards are linked for the same governed work.
- Do not treat `semantic_intent_status=unavailable` as acceptable for selected
  governed editing / write-capable MCP entry points; return the precondition
  card instead.

## 8. Acceptance Criteria

- `host_adapter_contract.normalize_turn_input()` redacts raw prompt input.
- `host_adapter_contract.normalize_turn_result()` redacts raw prompt echoes in
  failure summaries.
- Codex current path consumes the Host Adapter Turn Input/Result contract and
  remains represented as accepted pre-turn invocation with semantic provider
  still unavailable.
- Registry and mount-set docs identify this work order as the cross-client
  adapter contract anchor.
- No evaluator, policy-store, or durable-write behavior changes in this slice.
