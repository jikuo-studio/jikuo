# INSIGHT-2026-06-07: Studio Frontend Data Source Drift

## Classification

- Classification: `task_candidate`
- Status: `open`
- Captured during: pre-release Studio trace and evidence readiness work
- Immediate decision: record the concrete drift phenomenon; do not fix the
  Studio implementation in this insight slice
- Related insight:
  - `docs/insights/INSIGHT-2026-05-16-studio-dashboard-frontend-architecture.md`
- Related policy:
  - `.jikuo/policies/approved/POLICY-jikuo-studio-frontend-authoritative-data-source.yaml`
- Related task refs:
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-01_global_console_and_configuration_shell.md`
  - `docs/work_orders/SPRINT_050_WO-PER-JIKUO-STUDIO-TRACE-CONFIG-01_studio_trace_configuration_ia.md`
  - `src/jikuo/studio/global_status.py`
  - `src/jikuo/integrations/studio_web/server.py`

## Observation

Studio was intended to be a thin frontend over backend-owned read models. During
the trace and missing-evidence work, a concrete drift pattern appeared: some UI
questions began to look at runtime facts that existed outside the specific
Studio projection consumed by the panel.

The user-visible example was the `Missing classification` display. The frontend
could show an empty state such as `No missing evidence classification` while
real runtime state still contained missing evidence reports elsewhere, including
top-level runtime state summary data. That mismatch raised the question of
whether the frontend should pull from those scattered fields directly.

## Concrete Manifestations

- The Document Trace and Policy Trace UI render missing-classification empty
  states when the selected round or active gap projection lacks
  `missing_evidence_classification`.
- Related runtime evidence may still exist in other structures such as
  `state_summary["missing_evidence_reports"]`, which creates pressure for the
  frontend to read fallback locations directly.
- The frontend contains selection-level fallback logic such as choosing
  `selectedRound.missing_evidence_classification` and then
  `activeGap.missing_evidence_classification`. That is acceptable only while the
  backend read model owns all candidate fields and their semantics.
- If the frontend starts joining `summaries.runtime`, top-level runtime summary,
  history card details, or other scattered artifacts by itself, it becomes a
  second normalization layer rather than a thin renderer.

## Boundary Exposed

The problem is not that missing evidence exists. Missing evidence is an
intentional product boundary disclosure. The problem is that the frontend can
present an empty classification state when the backend has related evidence in
another shape.

That creates two risks:

- a user may read the empty UI state as "there is no classified evidence gap"
  even though the system only failed to project that classification into the
  panel's read model;
- future backend field changes can silently break the frontend if the browser
  has learned to search multiple runtime artifacts instead of consuming one
  stable Studio read model.

## Design Implication

The fix should not be browser-side scavenging. The backend Studio read model
should expose the complete panel contract, including classified missing
evidence, source status, and intentional empty-state reasons. The frontend
should render that contract and may only perform presentation-level selection,
filtering, or formatting.

If a panel needs data from `state_summary`, history snapshots, policy management
status, or document trace projections, the backend should normalize those
sources before they reach the frontend. The frontend should not decide which
runtime artifact is authoritative.

## Business Meaning

This insight matters because trust in JIKUO's Studio depends on users being able
to distinguish a real missing evidence gap from a projection gap. If the UI
silently hides evidence because it looked in the wrong projection, users may
mistake a product boundary for a clean state. If the UI compensates by reading
scattered files directly, JIKUO gains an unreviewed second governance surface.

Future iteration should normalize Studio panel data sources around authoritative
read-model fields before expanding trace UI behavior further.
