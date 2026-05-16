# SPRINT_050_WO-PER-JIKUO-INIT-02: Reviewed Configuration Onboarding

> **Status**: Implemented source-provenance core behavior and router surfacing.
> **Date**: 2026-05-16
> **Product meaning**: JIKUO must not treat implicit defaults as if the user had configured the project. First active use should make key setup choices visible, reviewable, and approval-bound.

## 1. Why This Slice Exists

MCP availability is not the same as JIKUO activation.

A project can have:

- a callable JIKUO MCP server
- an active policy store
- no `.jikuo/activation_settings.yaml`

Before this slice, that state could look like `desired_trigger_mode=ask` and
`effective_enforcement_level=instruction_only` without making clear that those
values were implicit defaults rather than user-reviewed configuration.

The root principle is:

> JIKUO must not disguise system defaults as user choices.

## 2. Configuration Source Provenance

Activation settings now distinguish:

| Source | Meaning |
|---|---|
| `implicit_default` | Runtime fallback used because the settings file is missing |
| `legacy_file_without_review_metadata` | A settings file exists, but does not record that the user reviewed its key fields |
| `user_reviewed_default` | User reviewed and accepted the default value |
| `user_configured` | User selected a non-default value |

Each reviewable field reports:

- `value`
- `source`
- `review_status`
- `reviewed_at_utc`
- `requires_user_review`
- `meaning`

Initial review scope:

- `desired_trigger_mode`
- `effective_enforcement_level`
- `strict_mounted_requires_adapter` (confirm-only for now; JIKUO should keep this true until a future contract explicitly changes the strict-mounted safety boundary)

## 3. Runtime Behavior

If activation settings are missing or unreviewed:

- `jikuo.get_activation_settings` returns `onboarding_required=true`
- `required_user_decisions` describes choices and meanings
- `jikuo.route_user_request` injects a `configuration_review` obligation before ordinary task execution when no explicit trigger-mode override was supplied
- no durable file is written

Only the guarded apply path can write `.jikuo/activation_settings.yaml`.

When the user confirms defaults, the file records `user_reviewed_default`.
When the user chooses a non-default value, the file records `user_configured`.

## 4. Strict Mounted Boundary

`mounted` still does not mean strict pre-turn execution unless a host adapter is
available.

The status surface distinguishes:

- `strict_mount_status=not_configured`
- `strict_mount_status=degraded_instruction_only`
- `strict_mount_status=strict_pre_turn_adapter`

## 5. Implemented Artifacts

- `src/jikuo/activation_settings.py`
- `src/jikuo/agent_flow.py`
- `src/jikuo/configuration_review.py`
- `tests/activation_settings_tests.py`
- `tests/configuration_review_tests.py`
- `tests/mcp_adapter_tests.py`

## 6. Acceptance

- Missing settings report `source=implicit_default` and `onboarding_required=true`.
- Existing settings without provenance report `source=legacy_file_without_review_metadata` and still require review.
- Guarded apply records either `user_reviewed_default` or `user_configured`.
- Router injects `configuration_review` when unreviewed activation settings are discovered during first active use.
- Explicit `--trigger-mode` remains an override for tests and deliberate calls.
- No path automatically writes `.jikuo/activation_settings.yaml` without guarded approval.
