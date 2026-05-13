# JIKUO Product Development Docs

> **Status**: Canonical JIKUO product documentation entry.
> **Boundary**: This directory contains JIKUO's own product-development assets. It does not absorb NarrativeSystem sprint history or documents that merely mention JIKUO as context.

---

## 1. Purpose

> **中文注释**：这里是机括自己的开发目录，不是叙事引擎 Sprint 文档的替代品。历史来源仍留在原 Sprint 文档里；机括自己的工单、契约、schema、执行挂载在这里继续演进。

`docs/jikuo/` is the product documentation home for `机括`.

JIKUO remains incubated inside NarrativeSystem for now, but its own product assets are no longer stored as Sprint-local files.

---

## 2. Directory Layout

- `docs/jikuo/work_orders/`: JIKUO product work orders and implementation slices.
- `docs/jikuo/governance/`: JIKUO product maps, execution mounts, kernel/skeleton boundaries, policy contracts, and agent instruction contracts.
- `docs/jikuo/schemas/`: JIKUO-owned schema and view-model contracts.

---

## 3. What Stays Outside

The following remain outside this directory unless a later work order explicitly promotes them:

- NarrativeSystem Sprint 049 / Sprint 050 historical docs.
- Interactive-novel runtime design docs.
- General engineering governance documents that are still used by NarrativeSystem directly.
- `docs/scenarios/interactive_novel/governance/rule_registry.yaml`.
- `docs/scenarios/interactive_novel/governance/rule_registry.schema.md`.
- `docs/scenarios/interactive_novel/governance/agent_operating_kernel.md`.

---

## 4. Current Entry Points

- `docs/jikuo/governance/jikuo_execution_mounts.md`
- `docs/jikuo/governance/jikuo_productization_task_map.md`
- `docs/jikuo/governance/jikuo_skeleton_kernel_boundary_and_backlog.md`
- `docs/jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-FLOW-02_desktop_app_primary_operating_loop.md`

---

## 5. Migration Rule

When a future task creates JIKUO-owned docs:

- put work orders under `docs/jikuo/work_orders/`
- put durable contracts under `docs/jikuo/governance/`
- put schemas under `docs/jikuo/schemas/`
- update references in code, tests, sidecar state, fixtures, Sprint indexes, and checker rules
- keep historical NarrativeSystem context in place unless the document itself is a JIKUO product asset
