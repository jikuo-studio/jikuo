# INSIGHT-2026-05-16: Studio And Dashboard Frontend Architecture

> **Classification**: promoted_to_task
> **Status**: promoted
> **Related task**: `JIKUO-STUDIO-01`

## Observation

JIKUO now has a stable local governance kernel, runtime visibility files, CLI
inspection, and an MCP wrapper with no-write and guarded-write tools. The next
product question is not whether to build a frontend, but how to avoid making a
future frontend into a second governance kernel.

The current product posture is:

- desktop-agent-first interaction remains the primary operating loop
- `.jikuo/` project-local artifacts remain the canonical state
- MCP / CLI / public adapter APIs remain the callable action boundary
- runtime cards and audit files remain available out-of-band
- dashboard / Studio UI is post-MCP product architecture, not part of the
  current MCP wrapper scope

## Dashboard Versus Studio

Dashboard and Studio should be treated as related but distinct surfaces.

Dashboard:

- shows current runtime status, latest card, state summary, and history
- helps users verify what the agent did without depending on chat cooperation
- should start as read-only
- should be useful even when no advanced product configuration exists

Studio:

- provides a broader workbench for policy configuration, audit review, template
  import, rule evolution, task-session history, and future integration health
- may later expose guarded actions, but only through the existing proposal /
  approval / apply boundary
- should not become the only place to confirm ordinary task-level decisions

## Design Principle

Build Studio as a projection and control shell over stable JIKUO contracts, not
as a new source of truth.

The frontend should not directly own:

- policy trigger semantics
- evidence matching semantics
- approval boundaries
- durable write rules
- privacy classification
- MCP tool behavior

The frontend may own:

- layout
- navigation
- filters
- human-friendly grouping
- panel registration
- action affordance presentation
- visual comparison of existing canonical records

If Studio and the kernel disagree, project-local canonical state wins.

## Change-Friendly Architecture

Prefer this shape:

```text
src/jikuo/studio/
  view_models.py      # canonical .jikuo state -> stable UI JSON
  registry.py         # panel and action registration
  actions.py          # guarded action descriptors

src/jikuo/integrations/studio_web/
  server.py           # local read-only / guarded-action HTTP surface
  static_or_app/      # frontend shell
```

The important boundary is not the exact frontend framework. The important
boundary is that the frontend consumes view models and invokes registered
actions instead of parsing arbitrary files or writing `.jikuo/` records itself.

## View-Model Layer

Add a stable projection layer before a large UI exists.

Candidate view models:

- `RuntimeStatusView`
- `PolicyStoreView`
- `TaskSessionIndexView`
- `EvidenceTimelineView`
- `ActionProposalView`
- `IntegrationHealthView`
- `TemplateCatalogView`

These views can be consumed by:

- a local web dashboard
- future Studio UI
- MCP status tools
- Agent SDK adapters
- tests and fixture snapshots

This preserves flexibility if the on-disk `.jikuo/` layout changes later.

## Panel Registry

Studio should add product areas through registered panels rather than hard-coded
page logic.

A panel definition should include:

- `panel_id`
- title
- data provider
- action refs
- required privacy level
- empty state
- status badges
- renderer type

Likely initial panels:

- Runtime
- Policies
- Task Sessions
- Evidence Timeline
- MCP / Client Integrations
- Templates

Likely later panels:

- Rule Evolution
- Rollback
- Team / Hosted State
- Agent SDK Adapters
- Audit Analytics

## Action Registry

Any user-visible write operation should be represented as a registered action.

An action definition should include:

- `action_id`
- write effect summary
- required approval evidence
- confirmation requirement
- target operation
- privacy classification
- card output contract
- rollback posture, if available

The frontend should render the action and collect approval, but the actual write
must go through an existing guarded apply path such as `agent_flow`, MCP, or a
future public adapter API.

This lets future tools such as policy rollback, template activation, evidence
append, or index refresh appear in Studio without custom write logic scattered
across UI components.

## Recommended Phases

Phase 0: current file and CLI visibility

- `.jikuo/runtime/last_card.md`
- `.jikuo/runtime/state_summary.json`
- runtime history
- `jikuo show`

Phase 1: local read-only dashboard

- render runtime status, latest card, policy summary, task-session index, and
  audit history
- no durable writes except optional runtime view refresh
- no direct policy editing

Phase 2: Studio shell

- introduce panel registry
- introduce view-model providers
- introduce action registry without enabling broad writes

Phase 3: guarded Studio actions

- expose approved actions through the same proposal / approval / apply boundary
  already used by the MCP wrapper
- include card links and runtime verification after every action

Phase 4: packaged or hosted product surfaces

- consider desktop shell, hosted dashboard, or team workspace only after the
  local Studio contract is stable
- keep local project state and privacy boundaries explicit

## Framework Posture

The framework should be chosen after the view-model and action boundaries are
accepted.

Reasonable options:

- simple local HTTP + static HTML for a tiny read-only dashboard
- React / Vite for a richer Studio shell
- Tauri or Electron only after product interaction patterns stabilize
- hosted UI only after licensing, privacy, and team-state boundaries are
  explicit

Avoid choosing the heavy shell first. The first stable contract should be the
projection and action model, not the renderer.

## Designs To Avoid

Avoid:

- parsing Markdown cards as business data
- making Studio the only place to confirm common task-level decisions
- letting frontend components write `.jikuo/policies/` or `.jikuo/task_sessions/`
  directly
- binding the dashboard to one desktop client
- duplicating policy evaluation in JavaScript
- starting with a large desktop shell before the product workflows stabilize

## Routing Decision

Promoted on 2026-05-31 into
`docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-01_global_console_and_configuration_shell.md`.

The promoted task keeps the core insight: Studio should be a modular projection
and guarded control shell over JIKUO's canonical local state and stable tool
contracts. The promoted scope is explicitly JIKUO-wide, not a policy-management
only frontend.
