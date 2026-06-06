# SPRINT_050_WO-PER-JIKUO-REL-READINESS-01: Pre-release User Usability

> **Status**: Active pre-release work order; P0-01, P0-02, P0-03, and P0-04 accepted; P0-05 next.
> **Date**: 2026-06-06
> **JIKUO layer**: release readiness / first-use configuration / user-facing governance.
> **Business meaning**: before publishing JIKUO to GitHub, a new user should be able to install it, understand the initial configuration state, configure documents and starter policies, see known evidence limits, and complete a first governed workflow without relying on private local knowledge.

## 1. Objective

This work order tracks release-readiness work that directly affects whether a
new user can use the product.

It is not the full release checklist. License choice, repository polish, demo
assets, and deeper docs remain important, but this sequence prioritizes the
path where a user installs JIKUO, configures a project, runs governed work, and
understands the resulting evidence.

Stop rule for execution:

- complete one checklist item at a time;
- record the business meaning and acceptance evidence;
- stop and report progress before starting the next item.

## 2. P0 User-usability Checklist

| ID | Item | Status | Business meaning | Acceptance signal |
|---|---|---|---|---|
| P0-01 | Clean install and startup smoke | Accepted | A new user can install the package and open the CLI / Studio without private environment assumptions. | Editable install, CLI entry points, Studio HTTP smoke, and full unit suite pass. |
| P0-02 | First-run initialization and configuration status | Accepted | A new user can tell whether JIKUO is configured, what is missing, and which guarded action should happen next. | CLI and Studio expose a first-run status with required blockers, recommended actions, and no writes. |
| P0-03 | Policy starter pack minimum usable path | Accepted | Users can activate baseline policy coverage instead of starting from an empty policy store. | Starter pack status, preview activation, guarded apply, and post-activation policy visibility are documented and smoked. |
| P0-04 | Policy configuration changes through guarded plan | Accepted | Users understand that policy metadata changes are governed configuration changes, not ad hoc UI toggles. | Scope/lifecycle/trigger/final-response-gate changes all use preview then guarded apply. |
| P0-05 | Document Rules default configuration and local mount layering | Not started | Users understand which local documents JIKUO reads, which files are editable configuration, and how to add their own docs safely. | First-run project context and Document Rules UI show editable targets, defaults, and guarded add/remove flow. |
| P0-06 | Evidence missing classification | Not started | Users can distinguish product limits from genuine missing work evidence instead of reading every `missing` as failure. | Missing evidence is classified by reason and surfaced in runtime / Studio read models. |
| P0-07 | Current limitation disclosure | Not started | Users know what JIKUO does not yet prove, especially around semantic classification, mounted enforcement, and observed-read evidence. | README / quickstart / Studio limitations show the same limits in user-facing language. |
| P0-08 | Quickstart full flow | Not started | A user can complete one end-to-end flow without reconstructing private development history. | Quickstart covers install, configure, starter policy activation, document rules, task run, completion review, and receipt inspection. |
| P0-09 | Local path and runtime publication audit | Not started | Public release artifacts should not expose private machine paths or development-only runtime files as product defaults. | Release audit lists publish-safe files, ignored runtime paths, and any intentional local-only examples. |

## 3. P1 Release-support Checklist

| ID | Item | Status | Business meaning |
|---|---|---|---|
| P1-01 | Studio empty-state and diagnostics panel | Not started | First-run users need visible next actions when project-local state is missing. |
| P1-02 | `jikuo doctor` or equivalent diagnostics | Not started | Terminal users need one command that explains install, config, MCP, Studio, and runtime readiness. |
| P1-03 | Demo starter project | Not started | Users need a non-private example project to learn the product loop. |
| P1-04 | Policy template compatibility state | Not started | Older starter packs should remain readable while migrations stay explicit and guarded. |
| P1-05 | Final / summary evidence backfill | Not started | Completion summaries should satisfy final-response and progress-summary policies more consistently. |

## 4. P2 Later Productization

| ID | Item | Status | Business meaning |
|---|---|---|---|
| P2-01 | Full GUI onboarding wizard | Deferred | A guided UI can reduce setup friction after the CLI / read-model path is stable. |
| P2-02 | Document mount migration assistant | Deferred | Users with existing docs can migrate without hand-editing project context. |
| P2-03 | Deeper governance concept docs | Deferred | Advanced users need conceptual docs after the core first-use path works. |

## 5. Accepted Item: P0-01

P0-01 is accepted as of 2026-06-06.

Acceptance evidence:

- temporary virtual environment: `D:\tmp\jikuo-p0-smoke-venv`;
- `pip install -e ".[dev]"` completed successfully;
- `jikuo.exe --help` returned successfully;
- `jikuo-mcp.exe --help` returned successfully;
- `jikuo.exe show` returned successfully;
- `jikuo.exe studio status --format markdown` returned successfully and reported
  `degraded` only for expected first-use configuration gaps;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 384 tests;
- `jikuo.exe studio serve --host 127.0.0.1 --port 8770` served `/` with HTTP
  200 and rendered JIKUO content.

Business meaning:

P0-01 proves the package can be installed and started from a clean environment.
It does not prove that a first-time project is well configured; that is P0-02.

## 6. Accepted Item: P0-02

P0-02 is accepted as of 2026-06-06.

Implemented behavior:

- exposed a first-run status in the existing configuration review read model;
- classified required blockers separately from recommended setup actions;
- showed activation settings, project context, and starter policies as required
  first-use setup concerns;
- kept instruction files, runtime visibility, and MCP server state visible as
  recommended setup concerns;
- made the same status available through CLI / Studio read models and the thin
  Studio frontend;
- remained read-only.

Acceptance evidence:

- `python -m unittest tests.configuration_review_tests tests.studio_global_status_tests tests.studio_web_server_tests` passed with 49 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 385 tests;
- `python -m jikuo configure status --format markdown` rendered `## First Run`;
- `python -m jikuo configure status --format json` included
  `first_run.schema = jikuo.first_run_configuration_status.v0`;
- `python -m jikuo studio status --format json` exposed
  `summaries.configuration.first_run`;
- `git diff --check` reported no whitespace errors.

Business meaning:

P0-02 makes first-use readiness explicit instead of forcing the user to infer it
from scattered configuration warnings. The current JIKUO project now reports
`needs_configuration` because activation settings are still implicit; project
context and starter policies are complete. A blank project reports activation
settings, project context, and starter policies as required setup blockers.

## 7. Accepted Item: P0-03

P0-03 is accepted as of 2026-06-06.

Implemented behavior:

- added a Studio starter policy pack activation panel in Policy Configuration;
- exposed starter pack selection, pack details, included policies, compatibility,
  and report-only boundary;
- added no-write `/api/policy-management/starter-init/plan`;
- added guarded `/api/policy-management/starter-init/apply`;
- required preview before apply by checking the reviewed `plan_id`;
- refreshed policy-management status after successful apply so newly activated
  starter policies become visible;
- surfaced starter pack init operations in the policy-management read model;
- made starter packs, available templates, guarded operations, and read-model
  limitations visible instead of hidden in the thin frontend.

Acceptance evidence:

- `python -m unittest tests.starter_policies_tests tests.policy_management_status_tests tests.studio_web_server_tests` passed with 53 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 388 tests;
- `git diff --check` reported no whitespace errors.

Business meaning:

P0-03 turns starter policies from package metadata into a visible first-use
product path. A new user can preview baseline policy coverage, understand that
the starter policies are report-only and do not prove semantic intent or enable
blocking gates by themselves, apply the pack through a guarded writer, and then
see the resulting active policies in policy management.

## 8. Accepted Item: P0-04

P0-04 is accepted as of 2026-06-06.

Implemented behavior:

- added a backend no-write plan schema for `update_final_response_gate`;
- routed final-response-gate preview through
  `/api/policy-management/evolution/plan`;
- routed final-response-gate writes through
  `/api/policy-management/evolution/apply`;
- required the reviewed `plan_id` before guarded apply, matching the starter
  policy pack preview/apply pattern;
- removed the browser-side final-response-gate plan builder and the dedicated
  final-response-gate apply URL from the thin frontend;
- updated policy-management available operations so final-response-gate appears
  as `no-write-plan+guarded-write`, not a standalone small toggle writer;
- kept the existing dedicated writer function available for compatibility, but
  no longer exposes it as the Studio configuration path.

Acceptance evidence:

- `python -m unittest tests.policy_management_status_tests tests.studio_web_server_tests` passed with 38 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 388 tests.

Business meaning:

P0-04 stabilizes the user's mental model for policy configuration. A
final-response gate is now treated like other active-policy configuration:
first preview a backend plan, then apply a guarded write against the reviewed
policy file. This avoids presenting final-response-gate as a lightweight UI
save action when it actually changes compliance behavior in final answers.

## 9. Next Item: P0-05

P0-05 should make Document Rules defaults and local mount layering clear enough
for a new user.

Required behavior:

- expose which documents are read as project context, completion checks, and
  governance references;
- distinguish editable project-local configuration from package defaults and
  runtime-observed evidence;
- keep add/remove changes behind the existing Document Rules preview/apply path;
- show empty states and defaults without relying on the maintainer's local
  private document layout.

## 10. Known Limits To Expose Before Release

- JIKUO does not perform semantic judgment by itself. Host AI supplies compact
  semantic intent when available; JIKUO records, merges, triggers policies, and
  displays evidence.
- Many policies are still report-only. A visible missing evidence report is not
  automatically a blocking gate unless the policy explicitly participates in a
  gate.
- Current runtime history is not yet a full DATA-01 event ledger.
- Observed-read evidence remains limited; write-side receipt evidence is more
  mature than read-side proof.
- Strict mounted behavior depends on a host adapter. Instruction-only or MCP-only
  setup must not be presented as guaranteed pre-turn execution.
