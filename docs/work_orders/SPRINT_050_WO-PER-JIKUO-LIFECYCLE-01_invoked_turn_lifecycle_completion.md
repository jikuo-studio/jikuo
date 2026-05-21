# SPRINT_050_WO-PER-JIKUO-LIFECYCLE-01: Invoked-Turn Lifecycle Completion

> **Status**: LIFECYCLE-01B observed lifecycle record implemented; LIFECYCLE-01C action-grammar checkpoint contract under design; no lifecycle runner or durable event ledger.
> **Date**: 2026-05-18
> **JIKUO layer**: process governance / runtime visibility / policy governance.
> **Business meaning**: Once JIKUO is invoked for a user turn, the user should see which lifecycle nodes actually produced cards and policy/evidence status. The next design step is to keep JIKUO lightweight by expressing AI work as an action grammar plus minimum checkpoints instead of a heavy fixed process. This is different from forcing every GUI client to invoke JIKUO or adding a lifecycle runner; host hook proof remains a separate adapter task.

---

## 1. Authority

This work order is the current lifecycle foundation anchor. It is created
because recent work showed that event-by-event cards can hide prior lifecycle
facts: a final `completion_review` card can be correct by itself while the user
cannot see the earlier `conversation_turn` or `task_start` policy state unless
the runtime records and links the node cards that actually occurred.

This work order depends on:

- `docs/governance/jikuo_execution_mounts.md`;
- `docs/governance/jikuo_policy_governance_authority.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-LIVE-14_completion_review_policy_only_surfacing.md`;
- `docs/work_orders/SPRINT_050_WO-PER-JIKUO-DATA-01_structured_execution_event_ledger_and_analytics_contract.md`;
- `docs/insights/INSIGHT-2026-05-17-work-unit-task-association-boundary.md`;
- `docs/insights/INSIGHT-2026-05-19-completion-review-evidence-bridge-gap.md`.

It does not use `docs/governance/jikuo_productization_task_map.md` as task
authority. That file remains a legacy L3 human-readable projection.

---

## 2. Problem

JIKUO currently has useful individual lifecycle surfaces:

- `conversation_turn` can route user intent and policy-suggestion review;
- `task_start` can project lightweight task processing and task-session
  binding/defer/preview state;
- `completion_review` can surface completion policies and evidence without
  requiring a durable task session.

The missing product behavior is node completion. A JIKUO-invoked turn should
not leave lifecycle obligations invisible simply because the last runtime card
belongs to the final node. The user should be able to inspect the lifecycle
chain for the current governed turn, including which policies fired at each
node and which evidence is still missing.

---

## 3. Current Boundary

Accepted boundary for this work order:

- JIKUO does not force GUI clients to invoke it. Strict host mounting remains
  adapter proof work.
- Once JIKUO is invoked, JIKUO is responsible for recording and surfacing the
  lifecycle nodes that actually produced runtime cards. LIFECYCLE-01B does not
  force missing nodes to run.
- Lifecycle is the process axis. Work-profile scopes describe the nature of the
  work and must not be treated as lifecycle stages.
- Durable `task_session_id` is optional. An observed lifecycle record can exist
  without creating or binding a task session.
- Long-lived `work_order_id` association must not be inferred from recent
  proposals, cards, paths, or titles. If used, it must come from explicit
  registry/task context or a reviewed association model.
- DATA-01 event-ledger work is the future source-of-truth layer. This work
  order may design for that future, but must not pretend that runtime Markdown
  cards are already a durable execution ledger.

---

## 4. Model Review Questions

These questions define the broader lifecycle model. LIFECYCLE-01B answers them
with a narrow record-only implementation; any future runner or durable
correlation model must return to this review surface.

| Topic | Question to settle |
|---|---|
| Business object | Is the first-class object an invoked turn, a lifecycle instance, or a work unit? |
| Correlation | What identifier links `conversation_turn`, `task_start`, `completion_review`, runtime cards, and future DATA-01 events without falsely binding them to a work order? |
| Node set | Which lifecycle nodes are recommended for the first MVP, and which remain optional or future? |
| Scope inheritance | Which facts are inherited across nodes, and which are recomputed at each node? |
| Policy evaluation | Which policies must run at each node, and how should node-local evidence be reported? |
| Evidence bridge | How does an actually performed main-document check become structured `main_document_mount_maintenance_evidence` without requiring a durable task session or inferring evidence from commits? |
| Runtime projection | Which card links and structured fields are enough before DATA-01B durable event writes exist? |
| Task association | When, if ever, can a lifecycle instance bind to a durable `task_session_id` or `work_order_id`? |

---

## 4.1 Accepted LIFECYCLE-01B Record-Only Model

The first implemented object for the MVP is an `observed_lifecycle` runtime
projection.

An `observed_lifecycle` starts only after JIKUO is actually invoked by a host
hook, MCP tool, CLI command, or agent-side tool call. It does not prove that the
host forced JIKUO to run before every user turn, and it does not prove that every
recommended lifecycle node has executed. It only says: these lifecycle cards were
actually observed for the current governed turn, and the user should be able to
inspect them from the latest card.

Business rule:

```text
host/user turn enters JIKUO
  -> runtime cards are produced by existing JIKUO calls
  -> observed lifecycle node links are carried forward
  -> latest card shows observed nodes, missing recommended nodes, and card links
```

This object is intentionally lighter than a lifecycle runner, lighter than a
durable task session, and lighter than the future DATA-01 event ledger. It is a
runtime/process projection that prevents the user from seeing only the final
card while earlier node checks are hidden.

### 4.1.0 Known Architecture Gap: Sequencing Owner

LIFECYCLE-01B exposed a separate architecture gap: MCP tools and `agent_flow`
do not guarantee lifecycle node ordering.

Current responsibility split:

- MCP exposes callable tool surfaces.
- `agent_flow` handles one invoked event and produces a node-local governance
  projection.
- `runtime_visibility` records cards that actually happened.

No current layer owns the full turn sequence:

```text
conversation_turn -> task_start -> completion_review
```

This means an `observed_lifecycle` can honestly show `conversation_turn` and
`completion_review` while missing `task_start` if the host, MCP caller, or agent
did not explicitly invoke the task-start tool. That is not a rendering failure
and not a policy-evaluator failure. It is a lifecycle orchestration gap.

Future work must define a sequencing owner before claiming lifecycle
completeness. Candidate owners include a thin host hook runner, a JIKUO
`lifecycle_runner` command called by hooks, or a hybrid harness that forces
pre-turn and pre-final checks while JIKUO validates missing nodes.

Tracked insight:
`docs/insights/INSIGHT-2026-05-21-lifecycle-sequencing-owner-gap.md`.

### 4.1.0A Architecture Calibration: Action Grammar

LIFECYCLE-01B also raised a broader design correction: fixed lifecycle may be
the wrong primary abstraction for AI work.

AI work is better understood as an action grammar. Different user turns compose
the same small verbs in different orders:

```text
see -> classify -> trigger policy -> think -> act -> observe -> think -> act -> report
```

Examples:

- "What do you think?" may only need `see -> think -> report`.
- "Update docs and commit" needs `see -> classify -> trigger policy -> think
  -> act -> verify -> report`.

Semantic-routing calibration:

- policy routing starts from user intent, then produces policy scope, execution
  boundary, and response contract;
- "what the user wants the agent to do" and "how the user wants the agent to
  think / evaluate / proceed" are both policy concerns; the second class should
  be represented as `process_contract` before it becomes any evaluator input;
- the action grammar explains how the AI reads context, reasons, acts, observes
  results, and reports evidence;
- `see / think / act / report` are not the primary policy-scope categories,
  because they can repeat and interleave inside one governed turn;
- every governed turn reports back to the user, so `report` is the delivery
  surface shaped by policy rather than a standalone scope;
- when `act` has repository, policy, registry, or other durable side effects,
  policy must govern the action before and during execution, not only the final
  summary.

This means LIFECYCLE should not become a heavy fixed process diagram. It should
stay a minimum sustainable governance layer: enough checkpoints to keep context,
intent, policy triggers, execution, evidence, and reporting aligned, without
forcing every turn through the same rigid route.

Initial action grammar:

| Verb | Meaning | JIKUO surface |
|---|---|---|
| see | mount user context, configured docs, inferred relevant docs, and runtime cards | DOCREG, mount sets, hook context |
| classify | determine user intent from AI semantic input plus fallback signals | `work_profile`, router, semantic provider |
| trigger | distribute applicable policies from user intent, policy scope, and context | `policy_store`, runtime cards |
| think | reason, design, compare alternatives, and plan under policy constraints | Agent reasoning, visible plan when useful |
| act | call tools, edit files, run tests, update docs, produce evidence | MCP tools, CLI, guarded apply paths |
| report | summarize results, evidence, missing items, and follow-ups | runtime cards, progress summary, observed footer |

Tracked insight:
`docs/insights/INSIGHT-2026-05-21-from-lifecycle-to-action-grammar.md`.

### 4.1.0B LIFECYCLE-01C Minimum Checkpoint Contract

LIFECYCLE-01C turns the action grammar into a small operational contract. It
does not add a new runner. It defines the minimum checkpoints that a host,
agent, or future runner must make visible when JIKUO is invoked.

The contract is intentionally action-oriented:

| Checkpoint | Required verbs | Purpose | Expected surface |
|---|---|---|---|
| pre-work | see, classify, trigger | mount relevant context, classify the turn, and surface applicable policies before substantive work | `conversation_turn` card, work profile, policy trigger summary |
| governed-work | think, act | perform reasoning and tool work under the visible policy/evidence constraints | agent reasoning, tool calls, optional task-start card |
| pre-final | see, trigger, report | re-check completion obligations, evidence, main-document maintenance, and user-facing summary before final delivery or commit closure | `completion_review` card, missing evidence report, observed lifecycle footer |

Minimum invariants:

- A final response for governed JIKUO work should include an `Observed
  Lifecycle` footer when runtime links are available.
- Missing recommended nodes must be reported as missing observations, not
  silently fabricated.
- Policy distribution uses the final work-profile classification for the active
  node; AI semantic classification can improve that input but remains a
  separate reviewed dependency.
- Deterministic keyword/path/tool signals are fallback and conflict evidence,
  not a substitute for an AI semantic classifier.
- Completion evidence remains explicit. It is satisfied only by structured
  produced evidence or an approved evidence bridge, not by recent commits,
  changed files, or proposal history alone.
- `work_order_id`, `task_session_id`, and future DATA event ids remain explicit
  bindings. They must not be inferred from card titles, paths, or recent
  history.
- Contract fields are proved through visible projection, planning use,
  evidence verification, and boundary enforcement/flagging. They are not treated
  as direct evaluator inputs in this work order.

LIFECYCLE-01C acceptance:

- this section is readable as the governing design for the next implementation
  slice;
- it explains why JIKUO uses checkpoints rather than a rigid lifecycle runner;
- it names the three required checkpoints and their expected surfaces;
- it preserves the LIFECYCLE-01B record-only runtime boundary;
- it leaves AI semantic routing and lifecycle sequencing owner implementation
  for separate reviewed slices.

### 4.1.1 Lifecycle Versus Scope

Lifecycle nodes answer "where is this governed turn in the process?"

Work-profile scopes answer "what kind of work is being done?"

The MVP must preserve this separation:

- `conversation_turn`, `task_start`, and `completion_review` are lifecycle
  nodes;
- `discussion`, `editing`, `progress_summary`, and fallback-expanded scope
  combinations are policy-distribution scopes;
- a turn can be classified as `editing` at `conversation_turn` and should still
  trigger conversation-turn policies whose scope includes `editing`;
- a later `completion_review` must be allowed to inherit the aggregate work
  scope while recomputing completion-node evidence.

### 4.1.2 Recommended MVP Nodes

The recommended observed lifecycle chain for an invoked governed work turn is:

1. `conversation_turn`: route the current user turn, classify work profile, and
   surface configuration or follow-up obligations.
2. `task_start`: record that governed processing began, including task-session
   binding / explicit deferral / preview status without requiring a durable
   task-session write.
3. `completion_review`: before final delivery or commit closure, run
   completion-scoped policies and evidence checks, including main-document and
   progress-summary obligations where applicable.

In LIFECYCLE-01B these nodes are recommended, not guaranteed. If a node is not
observed, the runtime should report it as a missing recommended event instead of
running it implicitly.

Optional or future nodes such as `configuration_review`, `evidence_review`,
`verification_review`, `pre_delivery`, and `handoff` may appear in the card
chain, but they are not required for the first observed-record contract.

### 4.1.3 Correlation Identifier

LIFECYCLE-01B should not introduce a new durable correlation identifier. It uses
existing runtime history card refs and `.jikuo/runtime/state_summary.json` as the
record-only correlation surface.

A later slice may introduce an `invoked_turn_id` or `lifecycle_run_id` only as a
runtime correlation field for cards and projections.

It must not be treated as:

- a durable `task_session_id`;
- a long-lived `work_order_id`;
- evidence that a registered work order has been completed;
- a DATA-01 append-only event id.

The safe initial binding posture is:

| Field | MVP posture |
|---|---|
| `lifecycle_run_id` / `invoked_turn_id` | deferred; LIFECYCLE-01B uses observed card refs instead |
| `task_session_id` | optional; only present when explicitly bound, created, or deferred through existing task-session surfaces |
| `work_order_id` | optional and explicit only; never inferred from titles, paths, recent cards, or proposal history |
| `proposal_id` / history card ref | node-local runtime proof; useful for inspection, not task authority |
| future DATA-01 `event_id` | deferred until DATA-01B+ runtime event writes are approved |

### 4.1.4 Inherited And Recomputed Facts

Facts carried forward across observed lifecycle cards in LIFECYCLE-01B:

- lifecycle card links from earlier observed nodes;
- node-local triggered policy count and missing evidence count;
- observed node order and missing recommended node list.

Facts recomputed by each actual node card:

- `work_profile.lifecycle_event`;
- node-local policy trigger and scope applicability;
- node-local exact conditions;
- node-local produced evidence and missing evidence;
- node card status and next required action.

This keeps the chain inspectable without freezing the whole turn into the first
router classification and without adding a runner that fabricates missing nodes.

### 4.1.5 Evidence Bridge Boundary

The completion evidence bridge should be explicit and report-only before it is
durable.

For the MVP, a `completion_review` may satisfy
`main_document_mount_maintenance_evidence` only when the caller supplies
structured produced evidence or a later explicitly approved bridge performs the
documented main-document check in the same process and emits a compact evidence
item.

LIFECYCLE-01B must not infer evidence from a commit, recent changed files, or
the mere existence of a history card.

Evidence output should distinguish:

- `auto_projected`: a future approved evidence bridge performed the check and
  projected structured evidence;
- `supplied`: the caller supplied structured produced evidence;
- `missing`: the policy required evidence and none was available;
- `deferred`: evidence cannot be produced without a later guarded or manual
  action.

### 4.1.6 Layering

The accepted layering for this model is:

| Layer | Role |
|---|---|
| Host hook / MCP / CLI | invokes JIKUO and passes minimal context; does not own governance logic |
| `agent_flow` proposal builders | continue to produce individual no-write node cards |
| `work_profile` | classifies lifecycle event plus policy scopes from host hints and deterministic signals |
| `policy_store` evaluator | evaluates active policies for each node; no special lifecycle-run authority |
| `runtime_visibility` | writes latest card, state summary, history cards, lifecycle card links, and `observed_lifecycle` |
| lifecycle runner / harness owner | future explicit owner of cross-node ordering; not implemented in LIFECYCLE-01B |
| DATA-01 event ledger | future append-only source of truth; not implemented in this slice |
| task session | optional durable task-sidecar; not required for observed lifecycle tracking |
| work order registry | long-lived task authority; explicit binding only |

### 4.1.7 LIFECYCLE-01B Implementation Boundary

The accepted lightweight implementation slice should:

- reuse existing `conversation_turn`, `task_start`, and `completion_review`
  proposal builders without adding a lifecycle orchestration command;
- record only lifecycle cards that actually happened;
- add an `observed_lifecycle` projection beside existing lifecycle card links;
- render the observed lifecycle as a final customer-facing footer in generated
  Markdown, using only `node_name: card_link` lines so the user can see the
  actual observed chain without opening the runtime card first;
- reset the observed record at `conversation_turn`, or at a direct `task_start`
  after a terminal observed node such as `completion_review` or `handoff`;
- carry observed card links through later node cards and non-lifecycle runtime
  snapshots;
- allow explicit task-session bind/create/defer state to pass through unchanged;
- surface completion evidence status without requiring task-session creation.

It should not claim that lifecycle completeness is guaranteed. Completeness
requires a later runner / harness sequencing owner.

Do not implement AI semantic routing as part of this slice. AI semantic routing
belongs to the host / classifier input design and must be reviewed separately
when this dependency order reaches that task.

---

## 5. Candidate Implementation Slices

These slices are planning markers only. They require model approval first.

1. `LIFECYCLE-01A`: document and approve the invoked-turn lifecycle business
   model, data structure, layers, and chain.
2. `LIFECYCLE-01B`: record the observed lifecycle nodes and card links that
   actually occurred; do not add a runner.
3. `LIFECYCLE-01C`: design the action-grammar / minimum-checkpoint contract for
   see, classify, trigger, think, act, and report before adding new code. This
   is the current design slice.
4. `LIFECYCLE-01D`: design the lifecycle sequencing owner only if the
   action-grammar review still needs a runner / harness contract.
5. `LIFECYCLE-01E`: make MCP responses expose the same observed lifecycle
   projection as the CLI/runtime projection.
6. `LIFECYCLE-01F`: align DATA-01B event records with the lifecycle correlation
   model, if the user approves event writes.
7. `LIFECYCLE-01G`: revisit strict host hooks after Codex and Claude adapter
   mechanisms are verified.

---

## 6. Stop Boundaries

- Do not add a lifecycle runner before a separate design review.
- Do not make task-session creation mandatory for observed lifecycle tracking.
- Do not infer `work_order_id` or durable task association from recent proposal
  history.
- Do not treat LIFECYCLE-01C checkpoints as automatic execution proof. They are
  an acceptance contract until a host, runner, or explicit agent workflow
  implements them.
- Do not build a heavy task knowledge graph in this work order.
- Do not claim GUI-client strict mounting is solved until host hook adapters are
  verified.
- Do not duplicate existing completion-review policy obligations.
- Do not expand the legacy task map with new task ordering or capability
  metadata.

---

## 7. Acceptance For This Planning Slice

- This work order exists and is registered in `docs/registry/work_orders.yaml`.
- An observed lifecycle capability is registered in
  `docs/registry/capabilities.yaml`.
- A lifecycle mount set is registered in `docs/registry/mount_sets.yaml`.
- `docs/governance/jikuo_execution_mounts.md` and
  `docs/governance/jikuo_policy_governance_authority.md` identify
  `LIFECYCLE-01` as the current foundation priority.
- LIFECYCLE-01B runtime changes must remain record-only: observed card links and
  observed/missing recommended node projection only.
