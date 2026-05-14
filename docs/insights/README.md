# JIKUO Development Insights

This directory stores development insights that are useful to keep, but are not
always ready to become active task-map items or approved policies.

An insight can later be:

- promoted to the productization task map
- promoted to an approved policy
- kept as deferred context
- closed as superseded or no longer relevant

## Files

- `insights_registry.yaml`: durable registry of insight records.
- `INSIGHT-*.md`: one file per insight, with context, classification, and follow-up.

## Classification

Use these classifications before changing task or policy documents:

- `task_candidate`: should probably become a task-map item or work order.
- `policy_candidate`: should probably become an approved or proposed policy.
- `insight_only`: useful context, not currently actionable.
- `deferred`: intentionally parked for later review.
- `promoted_to_task`: already moved into the task map or a work order.
- `promoted_to_policy`: already written into the policy store.

The registry is intentionally lightweight. It is a thinking surface, not an
execution gate.
