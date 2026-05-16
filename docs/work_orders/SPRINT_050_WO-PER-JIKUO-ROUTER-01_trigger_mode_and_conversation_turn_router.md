# SPRINT 050 WO-PER-JIKUO-ROUTER-01: Trigger Mode And Conversation-Turn Router

> **Status**: Accepted
> **Layer**: Process governance / product architecture
> **Depends on**: `JIKUO-MCP-01` MVP body, `JIKUO-INTG-01`, `JIKUO-SDK-01`, `POLICY-jikuo-proactive-policy-suggestion-metapolicy`
> **Blocks**: `CAP-CONVERSATION-TURN-ROUTER-01`, `CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01`, MCP router tools, mounted harness adapters

## 1. User Problem

JIKUO currently becomes visible only when the active desktop Agent or MCP client
chooses to call it. That is acceptable for explicit task starts, but it is not
enough for policy extraction from ordinary conversation.

The user clarified that repeated needs, corrections, and preferences can appear
in any AI interaction. For example, repeatedly asking for progress, todo items,
and business meaning is not merely a wording preference; it is a policy-candidate
signal.

The product must therefore support two explicit trigger modes:

- semantic mode: the Agent chooses when natural language seems to require JIKUO
- mounted harness mode: once selected, JIKUO runs before every user turn and
  returns an auditable router / policy status result, even when no action is
  required

## 2. Scope

This work order defines the accepted contract only. It does not implement the
router.

In scope:

- define trigger-mode vocabulary
- define the `conversation_turn` event
- define the no-write router output shape
- define how policy-suggestion review is requested
- define how no-op results remain visible and auditable
- define future MCP / Agent SDK / Studio adapter expectations

Out of scope:

- writing or activating inferred policies
- storing raw chat transcripts
- changing the active proactive metapolicy before router behavior exists
- building Studio / dashboard UI
- adding client-specific hooks
- making mounted mode the default

## 3. Trigger Modes

### Semantic Mode

Semantic mode is the lightweight adoption path.

The desktop Agent reads user intent and calls JIKUO when it believes governance
may be relevant. This mode is useful for first adoption, ordinary desktop
workflows, and clients that cannot force a pre-turn hook.

Limitation:

- the Agent may forget to call JIKUO
- a correct policy may not trigger because JIKUO was never invoked
- final summaries may still omit runtime-card links unless instructions are
  followed

### Mounted Harness Mode

Mounted harness mode is the strict path.

Once a project or session selects this mode, every user turn must pass through a
JIKUO router before the Agent proceeds. The router must return one of:

- continue with no JIKUO action required
- task start / task continuation proposal required
- policy-suggestion review required
- completion / acceptance review required
- guarded write proposal required
- clarification required
- refused because prerequisites are missing

Mounted mode is a product / integration behavior. It should be implemented by
adapters such as MCP router tools, Agent SDK wrappers, local proxy / Studio
entry, or client hooks. It must not make the core kernel depend on one client.

## 4. Conversation-Turn Router Contract

Future capability:

- `CAP-CONVERSATION-TURN-ROUTER-01`

Future event:

- `conversation_turn`

Future CLI / core entry:

```powershell
python -B -m jikuo.agent_flow propose --event conversation_turn --user-phrase "<user turn summary>" --format json
```

Future MCP tool:

```text
jikuo.route_user_request
```

Required output fields:

- `schema`
- `trigger_mode`
- `router_status`
- `classified_obligations`
- `policy_runtime_status`
- `required_followup_tools`
- `display_verification`
- `chat_ready_markdown`
- `write_effect`
- `non_effects`

The router must be no-write. Runtime visibility files may update.

## 5. Policy-Suggestion Review Contract

Future capability:

- `CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01`

Future MCP tool:

```text
jikuo.propose_policy_suggestions
```

The policy-suggestion review should produce compact evidence:

- repeated user pattern summary
- proposed policy candidate
- intended scope
- benefit
- side effect / overreach risk
- recommended routing: approve / revise / defer / insight / ignore

It must not:

- write an approved policy
- store raw chat transcripts by default
- treat a one-off user tone preference as a durable rule
- hide whether the result is taskmap, policy, insight, follow-up, or deferred

## 6. Current Proactive Metapolicy Position

`POLICY-jikuo-proactive-policy-suggestion-metapolicy` is accepted as an active
report-only governance principle, but its current `task_start` trigger is too
narrow.

Do not apply the supersession to a `conversation_turn` policy until the router
contract and at least a no-write router path exist. Otherwise the replacement
policy would still depend on clients remembering to call the right event.

Interim rule:

- keep the current policy active and honest as a narrow evidence hook
- use runtime cards and taskmap docs to show that the product mechanism remains
  planned, not complete
- when the router exists, supersede with a conversation-level policy

## 7. Scenario-Chain-Atom Registration Evidence

| Chain ID | User Scenario | Operation Chain | Registered Atoms |
|---|---|---|---|
| `conversation_level_policy_suggestion` | A user repeatedly expresses a need during ordinary conversation and expects JIKUO to notice the policy-candidate pattern | user turn arrives -> router classifies trigger mode and obligations -> policy-suggestion review produces compact evidence and candidate cards -> user chooses approve / revise / defer / insight / ignore -> guarded write remains separate | `CAP-JIKUO-TRIGGER-MODE-01`; `CAP-CONVERSATION-TURN-ROUTER-01`; `CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01`; `CAP-PROGRESS-SUMMARY-BUSINESS-MEANING-POLICY-01`; `CAP-MCP-AGENT-FLOW-WRAPPER-01` |
| `mounted_harness_pre_turn` | A project chooses strict harness mode and expects every user turn to receive an auditable no-op or obligation result | mounted adapter receives user turn -> calls router before Agent planning -> router returns no-op / obligation / clarification / refusal -> Agent displays card and follows required next tool | `CAP-JIKUO-TRIGGER-MODE-01`; `CAP-CONVERSATION-TURN-ROUTER-01`; `CAP-DESKTOP-CHAT-HARNESS-SURFACE-01`; `CAP-RUNTIME-VISIBILITY-CHANNEL-01`; `CAP-AGENTS-SDK-ADAPTER-EXPLORATION-01` |

## 8. Acceptance Criteria

- taskmap registers `CAP-JIKUO-TRIGGER-MODE-01`, `CAP-CONVERSATION-TURN-ROUTER-01`, and `CAP-PROACTIVE-POLICY-SUGGESTION-REVIEW-01`
- execution mounts describe semantic mode and mounted harness mode honestly
- no active policy is presented as solving conversation-level extraction before router support exists
- future implementation has a no-write router path before any guarded write path
- future MCP router tools preserve display directives, runtime links, and SEC-02 privacy classification
- future mounted harness adapters remain integration-specific and do not become kernel dependencies

## 9. Business Meaning

This slice protects JIKUO's core product promise: policies should be visible,
auditable, and hard to accidentally skip.

For users, the benefit is practical. They can choose a lightweight mode when
they want low friction, or a strict harness mode when they need dependable
governance on every interaction.
