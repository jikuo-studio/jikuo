# SPRINT_050_WO-PER-JIKUO-INIT-01: First-use Configuration Review

> **Status**: Core no-write review implemented; MCP read-only configuration status, activation settings read / plan, and guarded activation settings apply tools implemented; strict client adapters remain planned.
> **Product meaning**: when a user first enables JIKUO, the user should see the key initialization settings, what each one means, and what can be changed before governed work continues.
> **Boundary**: this slice aggregates and explains existing state; it does not write activation settings, instruction files, starter policies, project context, or client MCP config.

## 1. Why This Slice Exists

Activation settings are now durable project state, but users should not need to
know every file path or command before they understand what is configured.

The first-use review gives the user one product-facing status surface for:

- activation settings and trigger mode
- client instruction files
- runtime visibility files
- MCP server availability
- project-context bindings
- starter policy initialization
- guarded-write boundaries

This is deliberately separate from `.jikuo/activation_settings.yaml`.
Activation settings answer "how should JIKUO run"; configuration review answers
"what is the current setup state and what does it mean?"

## 2. Implemented Core Flow

Read-only CLI:

```powershell
jikuo configure status
jikuo configure review --format json
python -B -m jikuo.configuration_review review
```

Agent-flow card:

```powershell
python -B -m jikuo.agent_flow propose --event configuration_review
```

Conversation router:

- setup / settings / configuration / trigger-mode language routes to a
  `configuration_review` obligation.
- the router remains no-write and points the Agent to the configuration review
  follow-up tool.

## 3. Review Items

The review currently emits one item per setup concern:

| Item | Meaning |
|---|---|
| activation settings | project-level trigger mode and enforcement posture |
| instruction files | whether managed JIKUO instruction blocks exist |
| runtime visibility | whether last-card / state-summary files exist |
| MCP server | whether MCP code and Python SDK import are available |
| project context | whether reusable templates have local bindings |
| starter policies | whether first-use governance policies are active |
| guarded writes | whether users are protected by proposal / approval boundaries |

## 4. Remaining Work

- add no-write configuration update planning through MCP.
- expose router and policy-suggestion review through MCP so configuration
  language can be handled fully inside compatible clients.
- improve natural-language routing for non-English setup phrases after the
  router encoding posture is cleaned up.
- make future Studio / dashboard consume this same review object instead of
  inventing a separate frontend state model.

## 5. Acceptance

- `jikuo configure status --format json` returns `jikuo.configuration_review.v0`.
- `agent_flow propose --event configuration_review` returns a
  `configuration_review` card and `CAP-CONFIGURATION-REVIEW-01` atom trace.
- MCP `jikuo.get_configuration_status` returns `configuration_review.schema =
  jikuo.configuration_review.v0` and display-ready card markdown.
- MCP `jikuo.get_activation_settings` and
  `jikuo.plan_activation_settings_update` return activation settings status /
  plan shapes and do not write `.jikuo/activation_settings.yaml`.
- MCP `jikuo.apply_activation_settings_update` refuses without confirmation and
  approval phrase, writes only `.jikuo/activation_settings.yaml` on success, and
  redacts the raw approval phrase.
- conversation-turn routing can classify setup/settings language as a
  configuration-review obligation.
- no `.jikuo/**` durable governance state is written by the review itself.
