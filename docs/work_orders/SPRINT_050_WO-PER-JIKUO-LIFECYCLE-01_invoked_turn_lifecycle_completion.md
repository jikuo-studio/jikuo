# SPRINT_050_WO-PER-JIKUO-LIFECYCLE-01: Invoked-Turn Lifecycle Completion

> **Status**: Planned; business model and data model review before implementation.
> **Date**: 2026-05-18
> **JIKUO layer**: process governance / runtime visibility / policy governance.
> **Business meaning**: Once JIKUO is invoked for a user turn, the turn should complete its visible lifecycle nodes and node-scoped policy checks. This is different from forcing every GUI client to invoke JIKUO; host hook proof remains a separate adapter task.

---

## 1. Authority

This work order is the current lifecycle foundation anchor. It is created
because recent work showed that event-by-event cards can hide prior lifecycle
facts: a final `completion_review` card can be correct by itself while the user
cannot see the earlier `conversation_turn` or `task_start` policy state unless
those nodes are explicitly run and linked.

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
- Once JIKUO is invoked, JIKUO is responsible for completing the invoked turn's
  visible lifecycle nodes and card links.
- Lifecycle is the process axis. Work-profile scopes describe the nature of the
  work and must not be treated as lifecycle stages.
- Durable `task_session_id` is optional. A lifecycle can complete without
  creating or binding a task session.
- Long-lived `work_order_id` association must not be inferred from recent
  proposals, cards, paths, or titles. If used, it must come from explicit
  registry/task context or a reviewed association model.
- DATA-01 event-ledger work is the future source-of-truth layer. This work
  order may design for that future, but must not pretend that runtime Markdown
  cards are already a durable execution ledger.

---

## 4. Model Review Required Before Code

No implementation should start until these questions are reviewed:

| Topic | Question to settle |
|---|---|
| Business object | Is the first-class object an invoked turn, a lifecycle instance, or a work unit? |
| Correlation | What identifier links `conversation_turn`, `task_start`, `completion_review`, runtime cards, and future DATA-01 events without falsely binding them to a work order? |
| Node set | Which lifecycle nodes are mandatory for the first MVP, and which remain optional or future? |
| Scope inheritance | Which facts are inherited across nodes, and which are recomputed at each node? |
| Policy evaluation | Which policies must run at each node, and how should node-local evidence be reported? |
| Evidence bridge | How does an actually performed main-document check become structured `main_document_mount_maintenance_evidence` without requiring a durable task session or inferring evidence from commits? |
| Runtime projection | Which card links and structured fields are enough before DATA-01B durable event writes exist? |
| Task association | When, if ever, can a lifecycle instance bind to a durable `task_session_id` or `work_order_id`? |

---

## 5. Candidate Implementation Slices

These slices are planning markers only. They require model approval first.

1. `LIFECYCLE-01A`: document and approve the invoked-turn lifecycle business
   model, data structure, layers, and chain.
2. `LIFECYCLE-01B`: make the local agent-flow path complete the minimum node
   chain when JIKUO is invoked.
3. `LIFECYCLE-01C`: make MCP responses expose the same lifecycle chain and card
   links as the CLI/runtime projection.
4. `LIFECYCLE-01D`: align DATA-01B event records with the lifecycle correlation
   model, if the user approves event writes.
5. `LIFECYCLE-01E`: revisit strict host hooks after Codex and Claude adapter
   mechanisms are verified.

---

## 6. Stop Boundaries

- Do not modify lifecycle code before the model review is complete and this
  work order is updated with the accepted model.
- Do not make task-session creation mandatory for lifecycle completion.
- Do not infer `work_order_id` or durable task association from recent proposal
  history.
- Do not build a heavy task knowledge graph in this work order.
- Do not claim GUI-client strict mounting is solved until host hook adapters are
  verified.
- Do not duplicate existing completion-review policy obligations.
- Do not expand the legacy task map with new task ordering or capability
  metadata.

---

## 7. Acceptance For This Planning Slice

- This work order exists and is registered in `docs/registry/work_orders.yaml`.
- A lifecycle completion capability is registered in
  `docs/registry/capabilities.yaml`.
- A lifecycle mount set is registered in `docs/registry/mount_sets.yaml`.
- `docs/governance/jikuo_execution_mounts.md` and
  `docs/governance/jikuo_policy_governance_authority.md` identify
  `LIFECYCLE-01` as the current foundation priority.
- The model review is explicitly required before any code changes.
