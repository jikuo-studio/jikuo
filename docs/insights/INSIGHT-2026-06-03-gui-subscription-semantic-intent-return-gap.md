# INSIGHT-2026-06-03: GUI Subscription Semantic Intent Return Gap

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: GUI subscription semantic-routing gap review
- Immediate MVP response: strengthen host-AI behavior instructions and expose
  semantic-intent coverage in runtime and Studio
- Related work orders:
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-AI-SEMROUTE-01_ai_semantic_routing_mvp.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-HOSTADAPT-01_host_adapter_contract.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-MVP-01_work_receipt_and_configuration_mvp.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-01_global_console_and_configuration_shell.md`

## Observation

In GUI subscription mode, JIKUO can run a pre-turn hook and can expose MCP /
proposal tools, but it cannot force the host AI to return
`host_semantic_intent` after the model has understood the user turn and before
the model starts acting or answering.

This gap is not specific to progress summaries. Any semantic category can slip
through if the host AI directly answers or directly edits without a JIKUO
follow-up call:

- `discussion` may remain an unverified default;
- `editing` may happen before scope-first policy routing receives host semantic
  evidence;
- `progress_summary` may miss the business-meaning obligation;
- policy work may bypass guarded proposal preconditions;
- completion review may run without the semantic context that explains why the
  work was done.

The root boundary is that current Codex GUI integration provides a reliable
pre-turn surface, but not a strict post-understanding / pre-action gate. JIKUO
therefore cannot honestly claim strict semantic gating in GUI subscription
mode.

## Product Meaning

The MVP should not hide this limitation. The current product promise should be:

```text
instruction-guided + evidence-visible + gap-auditable
```

not:

```text
strict semantic gate
```

Users should be able to see whether a round had host-provided semantic intent,
whether policy routing was complete, and whether JIKUO fell back to missing or
heuristic evidence. That turns a hidden trust gap into an auditable product
signal.

## Desired MVP Behavior

Near-term MVP slices should do both behavior strengthening and risk exposure:

- strengthen hook and instruction wording so governed turns ask the host AI to
  return compact `host_semantic_intent` before acting or final response;
- preserve `semantic_intent_evidence` and a simplified coverage status in
  runtime state summaries;
- show semantic-intent coverage in Studio as `complete`, `missing`,
  `fallback_only`, or `degraded`;
- keep MCP/proposal tool preconditions for governed editing, policy work,
  progress summaries, and completion review;
- include semantic coverage in completion receipts so a work receipt can say
  whether its policy routing had host semantic evidence.

## Deferred Strict Closure

Strict closure requires a host adapter, wrapper, plugin, or SDK runner that
controls the execution order:

```text
user turn
-> host AI semantic classification
-> JIKUO policy routing
-> AI action / file writes / answer
-> completion_review receipt
```

That is deferred for GUI subscription mode unless the host provides a
post-understanding / pre-action hook, or the product adopts an API / SDK runner.
