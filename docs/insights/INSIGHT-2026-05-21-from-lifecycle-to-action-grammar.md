# INSIGHT-2026-05-21: From Lifecycle To Action Grammar

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: `LIFECYCLE-01B` architecture calibration
- Not promoted to implementation in this slice

## Observation

Fixed lifecycle may be the wrong primary abstraction for AI work.

User requests do not naturally map to one universal sequence such as start,
process, and end. They map to different combinations of actions. For example:

```text
"What do you think?"
  -> see -> think -> say

"Integrate the discussion, update docs, and commit."
  -> see -> think -> act -> verify -> say
```

For longer work, thinking and acting alternate:

```text
see -> classify -> trigger policy -> think -> act -> observe result
    -> think -> act -> verify -> report
```

If JIKUO turns this into a heavy fixed lifecycle, the governance mechanism may
consume the Agent's attention and make the Agent less capable. The better MVP
posture is minimum sustainable governance: enough structure to keep context,
intent, policy triggers, execution, and reporting aligned, without forcing every
turn through a rigid process diagram.

## Product Meaning

JIKUO exists because long-running AI collaboration drifts:

- the Agent may use stale or incomplete context;
- memory, role, and document versions may diverge;
- repeated changes can leave scattered, unproductized outputs;
- the final artifact may lose coherence even if individual edits are plausible.

The product goal is not lifecycle bureaucracy. The goal is to help the Agent:

1. see the right context;
2. classify the user's intent;
3. trigger relevant policies;
4. think under the right constraints;
5. act on the user's goal;
6. report results, gaps, and evidence clearly.

Those steps are an action grammar, not a single fixed lifecycle.

## Design Direction

Future lifecycle work should be reframed as an action grammar plus a small set
of checkpoints:

| Verb | Meaning | Current / future JIKUO surface |
|---|---|---|
| see | mount user context, configured docs, inferred relevant docs, and runtime cards | DOCREG, mount sets, hook context, work-order anchors |
| classify | determine user intent and work profile from AI semantic input plus fallback signals | `work_profile`, router, semantic provider |
| trigger | distribute applicable policies from intent, context, and action scope | `policy_store`, policy runtime cards |
| think | reason, design, compare alternatives, and plan under triggered policy constraints | Agent reasoning, visible plan when needed |
| act | call tools, edit files, run tests, update docs, produce evidence | MCP tools, CLI, guarded apply paths |
| report | summarize results, evidence, missing items, and follow-ups for the user | runtime cards, progress summary, observed footer |

The checkpoint contract should stay small:

- before substantive work, the Agent should see context and classify intent;
- before risky or durable action, relevant policies should be visible;
- before final delivery, the Agent should report changes, tests, missing
  evidence, and observed actions / cards.

## Boundary

Do not replace this insight with a new heavy schema immediately. Do not rename
all existing lifecycle fields until the action-grammar contract is reviewed.
Do not pretend `observed_lifecycle` proves a full process; it is still a
runtime card-link projection.

The current safe next step is documentation alignment. Code changes should wait
until the minimal action grammar, policy trigger contract, and hook / MCP
surfaces are reviewed.
