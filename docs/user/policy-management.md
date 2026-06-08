# JIKUO Policy Management

> **Status**: First-use user guide for current pre-release policy management.
> **Boundary**: This guide explains how users review and change local policy
> configuration. JIKUO records, merges, triggers, and displays evidence; it
> does not generate semantic judgments by itself.

## 1. What Policies Do

Policies describe governance expectations for a project. A policy can declare:

- when it applies, such as lifecycle event, policy scope, task type, JIKUO
  layer, or path pattern;
- what action is expected;
- what evidence would satisfy the action;
- whether the policy is report-only, deprecated, superseded, or a
  final-response gate.

The host AI supplies compact semantic intent when available. JIKUO uses that
host-provided evidence plus deterministic context such as turn anchors,
lifecycle events, changed paths, and policy files. JIKUO does not infer hidden
user intent from raw chat text.

<a id="first-run.starter-policies"></a>

## 2. First-use Policy Setup

For a new project, start with Studio Policy Configuration:

1. Review first-run readiness.
2. Activate a starter policy pack if baseline governance visibility is needed.
3. Inspect active policy status.
4. Run one small governed work turn.
5. Review Policy Trace and missing evidence classifications.

Starter policies are report-only baseline coverage. They do not make policies
blocking by themselves and do not turn JIKUO into a semantic classifier.

## 3. Active Policy Configuration

The current Studio `Proposed change` panel supports guarded changes for active
policies:

- `Refine trigger conditions`: update the selected policy's trigger profile,
  including scope, lifecycle event, and path filters.
- `Deprecate policy`: retire a policy without a successor.
- `Supersede policy`: retire a policy and record that an existing replacement
  policy takes over.
- `Update final-response gate`: decide whether triggered evidence for that
  policy must be surfaced in the final answer.

All durable changes follow the same review shape:

1. select the target policy;
2. choose the operation;
3. preview the plan;
4. review target policy, proposed effect, non-effects, expected write paths,
   and approval phrase;
5. apply the guarded change.

Preview is no-write. Apply requires explicit confirmation and approval evidence.

## 4. Path Filters

`changed_path_pattern` narrows a policy to explicit changed paths. It is useful
when a policy has a real asset boundary:

- documentation policy: `docs/**`;
- Studio frontend policy: `src/jikuo/integrations/studio_web/**`;
- policy-store policy: `.jikuo/policies/**`;
- template/starter policy: package policy-template directories.

Path filters are deterministic. The evaluator only compares supplied
`changed_paths` or `added_paths` against the configured pattern. If path context
is required but unavailable, the condition should be reviewed instead of being
treated as automatically satisfied.

Current condition composition is conservative: multiple conditions on one
policy are treated as AND. JIKUO does not yet support generic OR condition
groups such as `any_of` or `one_of`. If a rule needs alternative applicability
routes, create separate policies for the alternatives until explicit OR groups
exist. This keeps Policy Trace clear about which route triggered and prevents a
single broad condition from hiding missing path or task context.

Not every policy needs a path filter. Process policies such as "discussion
should not write files" or "progress summaries should explain business meaning"
may intentionally stay global because their trigger is workflow behavior rather
than a file ownership boundary.

## 5. Supersede Policy

`Deprecate` is termination. `Supersede` is replacement with lineage.

Supersede has two separate steps:

1. Make the replacement policy exist through a separate guarded workflow:
   manual YAML review, policy creation, template import, starter-pack
   activation, or another explicit policy configuration flow.
2. Run `Supersede policy` to link the old active policy to that existing
   replacement policy.

Supersede does not generate replacement content. It does not edit the
replacement policy body, infer semantic equivalence, or accept replacement
title, trigger, scope, action, or evidence fields as hidden content inputs.

The preview should show:

- target policy;
- existing replacement policy;
- supersession reason or feedback label;
- lineage: old policy -> `superseded_by` -> replacement policy;
- whether the replacement is already active or will be added to active refs;
- guarded write boundary, expected write paths, and approval phrase;
- non-effects, especially that replacement policy content is not created or
  edited.

## 6. Missing Evidence And Scope Review

Broad policies can produce many missing evidence reports. That can mean a real
workflow gap, but it can also mean the current policy is too broad or lacks a
path/scope filter.

Use missing evidence classification and Policy Trace to decide whether to:

- record missing evidence;
- refine trigger conditions;
- add a deterministic path filter;
- deprecate a no-longer-useful policy;
- create or activate a replacement policy, then supersede the old policy.

Missing evidence remains visible until the underlying evidence or configuration
is corrected. Classification explains the reason; it does not satisfy the
policy.
