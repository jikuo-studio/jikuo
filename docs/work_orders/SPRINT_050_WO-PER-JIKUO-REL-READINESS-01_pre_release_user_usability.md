# SPRINT_050_WO-PER-JIKUO-REL-READINESS-01: Pre-release User Usability

> **Status**: Active pre-release work order; P0-01 through P0-09 and P1-01 through P1-03 accepted; P1-04 through P1-05 remain planned.
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

Documentation follows the mature open-source pattern of a short repository
entry point, a first-run guide, concepts, how-to guides, reference material, and
limitations. README remains the GitHub landing page; `docs/user/` is the
user-facing product guide layer; `docs/governance/`, `docs/registry/`, and
`docs/work_orders/` remain implementation and governance authority.

README update rule:

- P0-05, P0-06, and P0-07 may update README incrementally when a new
  user-facing guide, limitation, or evidence concept becomes relevant to the
  GitHub landing page.
- P0-08 owns the main README rewrite. It must make README a complete
  first-run entry point covering install, Studio startup, first-run
  configuration, starter policy activation, Document Rules, trace inspection,
  and receipt verification.
- P0-09 owns the README release audit. It must check private-path leakage,
  license posture, non-commercial-use language, public navigation, and links to
  `docs/user/*` before GitHub publication.
- A P0 item that creates or changes user-facing onboarding behavior must state
  whether README was updated, intentionally left unchanged, or deferred to
  P0-08/P0-09 with a reason.

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
| P0-05 | First-run Document Rules and document-management guide | Accepted | Users understand which local documents JIKUO reads, which files are editable configuration, and how to add their own docs safely. | First-run project context, Document Rules UI, and `docs/user/document-management.md` show editable targets, defaults, local mount layering, and guarded add/remove flow. |
| P0-06 | Evidence missing classification and trace guide | Accepted | Users can distinguish product limits from genuine missing work evidence instead of reading every `missing` as failure. | Missing evidence is classified by reason and surfaced in runtime / Studio read models; `docs/user/trace-and-evidence.md` explains Policy Trace, Document Trace, turn anchors, and missing classifications; README links or explicitly defers the trace guide entry. |
| P0-07 | Current limitation disclosure | Accepted | Users know what JIKUO does not yet prove, especially around semantic classification, mounted enforcement, report-only policy behavior, observed-read evidence, and why many `missing` reports are visible feature boundaries rather than hidden failures. | README, Studio limitations, `docs/user/limitations.md`, and `docs/user/trace-and-evidence.md` show the same limits in user-facing language; quickstart integration is deferred to P0-08. |
| P0-08 | Quickstart full flow | Accepted | A user can complete one end-to-end flow without reconstructing private development history. | `docs/user/getting-started.md` and the main README rewrite cover install, configure, starter policy activation, document rules, task run, completion review, and receipt inspection. |
| P0-09 | Local path and runtime publication audit | Accepted | Public release artifacts should not expose private machine paths, development-only runtime files, or implied license rights as product defaults. | Release audit lists publish-safe files, ignored runtime paths, intentional local-only examples, README release readiness, license boundary, public MCP configuration examples, and docs navigation readiness. |

## 3. P1 Release-support Checklist

| ID | Item | Status | Business meaning |
|---|---|---|---|
| P1-01 | Studio empty-state and diagnostics panel | Accepted | First-run users need visible next actions when project-local state is missing. |
| P1-02 | `jikuo doctor` or equivalent diagnostics | Accepted | Terminal users need one command that explains install, config, MCP, Studio, and runtime readiness. |
| P1-03 | Demo starter project | Accepted | Users need a non-private example project to learn the product loop. |
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

- temporary virtual environment: `<TEMP_DIR>\jikuo-p0-smoke-venv`;
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

## 9. Accepted Item: P0-05

P0-05 is accepted as of 2026-06-06.

Implemented behavior:

- expose which documents are read as project context, completion checks, and
  governance references;
- distinguish editable project-local configuration from package defaults and
  runtime-observed evidence;
- keep add/remove changes behind the existing Document Rules preview/apply path;
- show empty states and defaults without relying on the maintainer's local
  private document layout.
- provide a user-facing document-management guide under `docs/user/`;
- expose the guide and default configuration boundary in the Studio read model
  and thin frontend.
- update README and `docs/README.md` so `docs/user/` is a visible
  user-facing guide layer.

Documentation deliverables:

- `docs/user/document-management.md`: how-to guide for first-run Document Rules,
  local mount layering, guarded changes, and current evidence limits.
- `docs/README.md`: documentation-directory map including `docs/user/`.
- README documentation map entry for the Document Management guide.

Acceptance evidence:

- `python -m unittest tests.studio_global_status_tests tests.studio_web_server_tests tests.studio_document_rules_tests` passed with 54 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 388 tests;
- `git diff --check` reported only existing line-ending normalization warnings
  and no whitespace errors.

Business meaning:

P0-05 turns Document Rules from an internal configuration surface into a
first-use product path. A new user can see the editable target
`.jikuo/project_context.yaml`, understand the difference between project-local
configuration, governance guidance, registry metadata, runtime observations,
and user documents, and use the existing preview/apply flow without relying on
private maintainer-local document knowledge.

## 10. Accepted Item: P0-06

P0-06 is accepted as of 2026-06-06.

Implemented behavior:

- classify Policy Trace missing evidence reports without changing the original
  `missing` status;
- classify Document Trace gaps into no comparable trace, read observation
  limits, write evidence gaps, and unchecked applicability;
- expose classification summaries in Studio runtime read models and the thin
  frontend;
- keep classification explicitly non-semantic: it explains recorded evidence
  gaps, but does not infer intent, satisfy evidence, or make report-only
  policies blocking;
- provide `docs/user/trace-and-evidence.md` as the user-facing guide for Policy
  Trace, Document Trace, turn anchors, semantic intent evidence, and missing
  evidence categories;
- update README and `docs/README.md` so the trace/evidence guide is reachable
  from public documentation entry points.

Acceptance evidence:

- `python -m unittest tests.studio_global_status_tests tests.studio_web_server_tests`
  passed with 46 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 388 tests.

Business meaning:

P0-06 makes runtime gaps legible for first-use users. A new user can now tell
whether a `missing` report points to absent host semantic intent, unrecorded
policy evidence, a broad policy scope needing review, a current read-observation
limit, a document write evidence mismatch, unchecked completion applicability,
or the absence of a comparable trace. This prevents the product from presenting
every evidence gap as a generic failure while still keeping the underlying
missing fact visible.

## 11. Accepted Item: P0-07

P0-07 is accepted as of 2026-06-07.

Implemented behavior:

- explain that a visible `missing` report is not automatically a product defect;
  many reports are deliberate feature-boundary disclosures where JIKUO cannot
  yet prove a fact and therefore keeps the gap visible;
- separate current product boundaries from genuine missing work evidence, so a
  user can tell whether to configure something, supply host semantic evidence,
  wait for a future feature, or investigate a real workflow gap;
- keep the raw missing fact visible; classification and limitation text must not
  satisfy evidence, hide the report, or make report-only policies blocking;
- state that JIKUO is not the semantic judge. The host AI supplies compact
  semantic intent; JIKUO records, merges, triggers policy, and displays
  evidence;
- document why early projects may show many missing reports even when the
  product is operating as currently designed.

Documented missing-evidence causes:

- host semantic intent is unavailable, not propagated to a lifecycle, or not
  associated with a turn anchor;
- report-only policies are intentionally surfacing review requirements without
  blocking execution;
- runtime history is not yet a complete DATA-01 event ledger, so old rounds may
  lack comparable structured state;
- observed-read evidence is currently less mature than write-side git/status
  receipt evidence;
- Document Trace may lack a comparable trace for a round, which means the
  structured comparison is unavailable, not necessarily that the document was
  never considered;
- completion applicability and final/progress-summary evidence are not fully
  automated for every policy obligation;
- broad or newly activated policies can intentionally create missing evidence as
  a scope-review signal until their evidence producers are implemented or their
  scope is narrowed.

Documentation deliverables:

- `docs/user/limitations.md`: user-facing explanation of current product
  boundaries and missing-evidence causes;
- `docs/user/trace-and-evidence.md`: cross-link to limitations and clarify how
  missing classifications map to feature boundaries;
- README and `docs/README.md`: public navigation to the limitations guide;
- Studio read model `summaries.release_limitations`: authoritative backend
  projection of current limitation categories and missing-evidence boundary
  explanation;
- thin Studio frontend `Current Limitations` panel: renders
  `summaries.release_limitations` without frontend-owned governance logic.

Acceptance evidence:

- `python -m unittest tests.studio_global_status_tests tests.studio_web_server_tests`
  passed with 47 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 389 tests;
- `git diff --check` reported only existing line-ending normalization warnings
  and no whitespace errors;
- quickstart integration is explicitly deferred to P0-08 because
  `docs/user/getting-started.md` is owned by that item.

Business meaning:

P0-07 prevents a first-use trust failure. A user can now see that many
`missing` reports are intentional current-version boundary disclosures: JIKUO
cannot yet prove the fact, so it keeps the gap visible. The docs and Studio
read model distinguish feature boundaries, required user configuration, missing
host semantic evidence, future product work, and genuine workflow evidence gaps
without hiding the raw missing state.

Next item:

P0-09 has now accepted the private-path, runtime-publication, README release
posture, license-language, and public-navigation audit before GitHub
publication. The next release-support item is P1-01 Studio empty-state and
diagnostics panel refinement.

## 12. Accepted Item: P0-08

P0-08 is accepted as of 2026-06-07.

Implemented behavior:

- added `docs/user/getting-started.md` as the complete first-run guide;
- rewrote README quickstart into a first-run entry point instead of a private
  smoke-test-only command list;
- covered install, CLI checks, Studio startup, first-run readiness, activation
  settings, starter policy activation, Document Rules, one governed host-AI
  work turn, completion review, runtime receipts, Policy Trace, Document Trace,
  and missing-evidence boundaries;
- stated the semantic boundary in the first-run path: host AI supplies compact
  semantic intent; JIKUO records, merges, triggers policy, and displays
  evidence;
- added the getting-started guide to `docs/README.md`;
- exposed the getting-started guide through the Studio `document_mounts` read
  model as a stable user document reference and configuration-language term;
- kept the thin frontend bound to backend read models. No browser-side scan of
  scattered documentation or runtime files was added.

Documentation deliverables:

- `docs/user/getting-started.md`: first-run quickstart for install,
  configuration, starter policies, Document Rules, governed work, completion
  review, receipt inspection, and current limitations;
- README: GitHub-facing first-run entry point with a pointer to the full guide;
- `docs/README.md`: documentation index entry for the getting-started guide;
- Studio read model `summaries.document_mounts.user_docs`: authoritative user
  documentation list now includes the getting-started guide.

Acceptance evidence:

- `python -m unittest tests.studio_global_status_tests tests.studio_web_server_tests`
  passed with 47 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 389 tests;
- `git diff --check` reported only existing line-ending normalization warnings
  and no whitespace errors.

Business meaning:

P0-08 gives a first-time user a single coherent product path. Instead of
reverse-engineering private maintainer history, the user can install JIKUO,
open Studio, understand required setup, configure policies and documents
through guarded flows, run one host-AI governed turn, and inspect the resulting
receipts and missing-evidence boundaries.

Next item:

P0-09 has now accepted the repository publication-safety audit for private
local paths, runtime files, license and non-commercial-use language, public
docs navigation, and release-facing README wording.

## 13. Accepted Item: P0-09

P0-09 is accepted as of 2026-06-09.

Slice 1 implemented behavior:

- added `/.tmp/` to `.gitignore` so local Studio/cache scratch output is not
  accidentally staged for publication;
- replaced maintainer-local absolute paths in MCP client configuration and
  proof docs with user-safe placeholders such as `<JIKUO_HOME>`,
  `<PROJECT_ROOT>`, `<WORKSPACE>`, `<PYTHON_EXE>`, and `<JIKUO_CMD>`;
- clarified README license posture: the repository does not yet grant public,
  commercial, or non-commercial use rights until an explicit license or terms
  file and matching package metadata are accepted;
- kept historical governance/audit records unchanged in this slice instead of
  silently rewriting provenance.

Current audit findings:

- ignored runtime and local-only paths already include `.jikuo/runtime/`,
  `.claude/`, `.mcp.json`, `tmp/`, Python caches, generated package metadata,
  browser profiles, and dependency directories;
- `.tmp/` was a publish-safety gap and is now ignored;
- `test.md` was an untracked empty scratch file and was deleted after explicit
  user approval;
- `docs/registry/work_orders.yaml` now reflects P0-09 accepted status for the
  release-readiness work order;
- tracked `.jikuo/policies/proposals/*.yaml` records contain local
  `project_root` / policy-store provenance. Those files are governance audit
  records, so they must not be linked from the public user documentation
  surface or rewritten as part of public-doc cleanup. If public release later
  needs policy-proposal examples, create sanitized fixtures or exported
  examples instead of publishing live local provenance;
- internal governance and handoff docs still contain some historical
  maintainer-local references. They need a release navigation decision:
  publish as historical local-proof material, redact, or keep out of the public
  documentation surface;
- at the end of Slice 1, package metadata still used the old closed-source
  license text, and no public non-commercial license had been installed; Slice
  4 resolves that license-posture gap.

Slice 2 implemented behavior:

- exposed the current policy condition composition limit in user and governance
  documentation: multiple conditions are AND, and generic OR groups such as
  `any_of` / `one_of` are not supported yet;
- clarified that unsupported OR groups are a product boundary, not hidden
  semantic judgment by JIKUO;
- documented the current workaround: model alternative applicability routes as
  separate policies until explicit OR condition groups exist;
- kept the future design direction explicit: OR should be represented as
  auditable condition groups, with AND inside each route and clear Policy Trace
  output for the matched route and missing context.

Slice 3 implemented behavior:

- deleted the approved untracked scratch file `test.md`;
- recorded that `.jikuo/policies/proposals/*.yaml` live policy-proposal
  provenance is not part of the public documentation surface. Those records can
  remain project-local audit material, but public examples should be sanitized
  exports or fixtures rather than live local provenance;
- classified internal documentation by publication strategy:
  - user entry documents (`README.md`, `docs/README.md`, and `docs/user/**`)
    are public-facing and should avoid maintainer-local paths, private runtime
    references, and unexplained governance internals;
  - engineering governance documents (`docs/governance/**`,
    `docs/registry/**`, and active work orders) can be published as
    implementation material when they use placeholders for current setup
    instructions and clearly mark historical/local-proof content;
  - historical audit material, runtime cards, `.jikuo/policies/proposals/**`,
    handoffs, and local proof records should not be treated as user onboarding
    documentation. Publish only if there is an explicit redaction/export
    decision.

Business meaning:

P0-09 is protecting the first public GitHub impression. A user should not see
the maintainer's machine layout as the default product path, should not receive
local runtime/cache artifacts, and should see the explicit noncommercial
license boundary instead of guessing usage rights from repository visibility.
The condition composition disclosure also prevents users from assuming JIKUO
can express OR policy routing when the current evaluator only supports
conservative AND composition. The Slice 3, Slice 5, and Slice 7 publication
strategies prevent historical audit evidence from leaking into the public
onboarding path while preserving the integrity of local governance records.

Acceptance evidence for this slice:

- scoped scan of README, MCP configuration examples, MCP proof playbook, and
  this work order found no remaining maintainer-local project path or private
  preview checkout references in the targeted public surface;
- `git check-ignore -v .tmp .tmp\studio .tmp\openai-docs-cache tmp
  tmp\mcp-stage-a-venv .jikuo\runtime .claude .mcp.json` confirmed `.tmp/`,
  `tmp/`, `.jikuo/runtime/`, `.claude/`, and `.mcp.json` are ignored;
- `git diff --check` reported no whitespace errors, only existing CRLF
  normalization warnings;
- `python -B -m unittest discover -s tests -p "*_tests.py"` passed with 389
  tests after the initial document updates and again after the work-order
  registry sync;
- `completion_review` generated runtime history
  `.jikuo/runtime/history/20260607T042525Z_proposal_def0d1ec68.md`; it
  observed the work-order registry sync and still reports broader report-only
  companion gaps for `docs/registry/capabilities.yaml` and
  `docs/registry/scenario_chains.yaml`, which this slice intentionally did not
  edit because it added no new capability or scenario-chain contract.
- Slice 2 documentation update exposes the current lack of generic OR condition
  groups in `docs/user/policy-management.md`,
  `docs/user/limitations.md`, and
  `docs/governance/jikuo_configurable_rule_trigger_policy.md`.
- Slice 3 removed `test.md` and documented public-surface strategy for
  `.jikuo/policies/proposals/*.yaml`, user entry documents, engineering
  governance documents, and historical audit material in this work order and
  `docs/README.md`.
- Slice 4 implemented the source-available noncommercial preview license
  posture: `LICENSE.md` was added, `pyproject.toml` now uses
  `PolyForm-Noncommercial-1.0.0`, README license wording now grants
  noncommercial preview use under that license, and
  `JIKUO-REL-01` records the selected license posture.
- Slice 5 cleaned up public documentation navigation: root README now points
  users to `docs/user/**` and MCP configuration examples instead of presenting
  the MCP proof playbook as a first-run path; `docs/README.md` classifies
  `docs/integrations/mcp_client_proof_playbook.md` and
  `docs/integrations/proofs/**` as internal release-validation / historical
  audit material; the proof playbook and proof notes README now state that
  boundary explicitly.
- Slice 6 cleaned up the public MCP configuration example surface:
  `docs/integrations/mcp_client_configuration_examples.md` no longer describes
  the source checkout path as a private GitHub preview proof, uses
  `<JIKUO_REPO_URL>` as the public repository placeholder, and separates
  maintainer client proof artifacts / historical smoke notes from first-run MCP
  setup instructions.
- Slice 7 removed `docs/migration/NARRATIVESYSTEM_RESOURCE_POOL_HANDOFF.md`
  from the `docs/README.md` current entry-point list, kept `docs/migration/**`
  under the internal / historical-audit boundary, and completed the scoped
  public-surface scan for local paths, private-preview wording, ignored
  runtime/cache paths, and noncommercial license consistency.

## 14. Accepted Item: P1-01

P1-01 is accepted as of 2026-06-09.

Implemented behavior:

- first-run setup steps now carry a backend-authored `resolution` record with a
  deterministic bucket, action boundary, label, reason, and optional Studio
  anchor;
- first-run readiness now includes `resolution_buckets` counts for setup gaps
  that still need attention;
- the thin Studio frontend groups first-run setup gaps by
  `resolution.bucket` / `resolution_bucket` from the Studio read model instead
  of deriving buckets from browser-side key, title, or next-action string
  heuristics;
- current Studio-configurable gaps are separated from CLI/MCP, manual
  client-file setup, and unsupported-in-Studio gaps without reintroducing the
  removed global `Available Actions` or `Diagnostics` panels;
- the frontend still links to guidance through the existing guidance registry
  and does not scrape scattered docs or runtime files.

Acceptance evidence:

- `python -m unittest tests.studio_global_status_tests tests.studio_web_server_tests`
  passed with 50 tests;
- `tests.studio_global_status_tests` now asserts first-run resolution records
  for activation settings, Document Rules/project context, starter policies,
  instruction files, and runtime visibility;
- `tests.studio_web_server_tests` now asserts that the frontend consumes
  `record.resolution` / `record.resolution_bucket` and no longer contains the
  old browser-side `value.includes(...)` classification rules.

Business meaning:

P1-01 makes first-run guidance more trustworthy. A user can see which setup
gaps are currently resolvable in Studio and which must be handled by CLI/MCP,
manual client configuration, or future product work. The important governance
boundary is that Studio displays backend read-model classifications; the
frontend no longer invents its own interpretation of setup gaps.

## 15. Accepted Item: P1-02

P1-02 is accepted as of 2026-06-09.

Implemented behavior:

- added `jikuo doctor` as a terminal-first diagnostic command;
- added `jikuo-doctor` as a direct script entry point for installed
  environments;
- kept the command read-only and backed by
  `jikuo.studio.global_status.build_global_status` as the authoritative source;
- reports install / CLI availability, first-run readiness, activation settings,
  policy management, Document Rules, Studio, MCP server, runtime visibility,
  diagnostics, pending user decisions, card links, privacy posture, and
  non-effects;
- exposes both markdown and JSON output for humans and automation;
- keeps first-run blockers visible without writing `.jikuo/` state;
- adds the command to README and the first-run getting-started guide.

Acceptance evidence:

- `python -m unittest tests.doctor_tests` passed with 3 tests;
- `python -m unittest tests.doctor_tests tests.studio_global_status_tests tests.studio_web_server_tests`
  passed with 53 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 395
  tests;
- `git diff --check` reported no whitespace errors, only existing LF/CRLF
  normalization warnings;
- `python -B -m jikuo doctor --format markdown` rendered the terminal report
  with `writes_performed=false`, Studio global status as the source read model,
  first-run blockers, MCP review status, runtime links, and non-effects;
- `python -B -m jikuo doctor --format json` returned
  `schema=jikuo.doctor_report.v0`, `source_read_model.schema=jikuo.studio.global_status.v0`,
  `checks[*].schema=jikuo.doctor_check.v0`, and `writes_performed=false`.

Business meaning:

P1-02 gives terminal users a single readiness command instead of forcing them
to know which lower-level status command to run first. The important governance
boundary is that `doctor` does not become a second authority: it projects the
Studio global status read model, so CLI diagnostics, Studio readiness, and
first-run guidance stay aligned.

Next item:

The next release-support item is P1-03 demo starter project.

## 16. Accepted Item: P1-03

P1-03 is accepted as of 2026-06-09.

Implemented behavior:

- added `examples/demo_project/` as a non-private starter project;
- included a demo project brief, decision log, release checklist, optional
  workflow notes, and a project-local `.jikuo/project_context.yaml`;
- left activation settings, instruction files, runtime receipts, and active
  starter policies intentionally incomplete so first-run diagnostics still teach
  the setup path;
- documented commands for `jikuo doctor`, `jikuo configure status`,
  `jikuo studio status`, starter policy preview, Document Rules preview, and
  Studio serving against the demo project;
- linked the demo from README, `docs/user/getting-started.md`, and
  `docs/README.md`;
- registered `examples/` as a project directory role in
  `.jikuo/project_context.yaml`;
- adjusted `jikuo doctor` runtime readiness so missing runtime receipts show as
  `review` even when no policy missing-evidence count exists yet.

Acceptance evidence:

- `python -m unittest tests.demo_project_tests tests.doctor_tests tests.studio_global_status_tests`
  passed with 25 tests;
- `python -m unittest discover -s tests -p "*_tests.py"` passed with 399
  tests;
- `git diff --check` reported no whitespace errors, only existing LF/CRLF
  normalization warnings;
- `python -B -m jikuo doctor --project-root examples/demo_project --format markdown`
  rendered a no-write report with project context complete, Document Rules ok,
  activation/starter-policy blockers visible, and runtime receipts in review;
- `python -B -m jikuo doctor --project-root examples/demo_project --format json`
  returned `schema=jikuo.doctor_report.v0`, `writes_performed=false`, and
  `source_read_model.schema=jikuo.studio.global_status.v0`;
- `python -B -m jikuo studio status --project-root examples/demo_project --format json`
  returned the Studio global status read model for the demo project;
- `python -B -m jikuo.starter_policies plan-init --project-root examples/demo_project --format text`
  returned a review plan showing starter policies and guarded write targets;
- `python -B -m jikuo studio document-rules plan --project-root examples/demo_project --add-context-doc docs/workflow-notes.md --format markdown`
  returned a review plan with one proposed Document Rules change and
  `writes_performed=false`.

Business meaning:

P1-03 gives new users a safe project to inspect before they connect JIKUO to
their own documents. It demonstrates the real product loop: first-run readiness
is not hidden, Document Rules can read project documents, starter policy
activation is previewed before guarded apply, and runtime receipts are clearly
absent until a JIKUO-producing flow creates them. The demo also keeps the
frontend/read-model boundary intact because all acceptance checks use existing
CLI and Studio read models, not handwritten expectations in the frontend.

Next item:

The next release-support item is P1-04 policy template compatibility state.

## 17. Known Limits To Expose Before Release

- JIKUO does not perform semantic judgment by itself. Host AI supplies compact
  semantic intent when available; JIKUO records, merges, triggers policies, and
  displays evidence.
- Many policies are still report-only. A visible missing evidence report is not
  automatically a blocking gate unless the policy explicitly participates in a
  gate.
- Many `missing` reports are current feature-boundary disclosures, not hidden
  product failures. They mean JIKUO cannot yet prove the corresponding fact from
  authoritative evidence.
- Current runtime history is not yet a full DATA-01 event ledger.
- Observed-read evidence remains limited; write-side receipt evidence is more
  mature than read-side proof.
- Document Trace can report no comparable trace for a round when structured
  round-level evidence is unavailable.
- Final-response, progress-summary, and completion applicability evidence are
  still being backfilled across policies.
- Strict mounted behavior depends on a host adapter. Instruction-only or MCP-only
  setup must not be presented as guaranteed pre-turn execution.
- Policy conditions currently compose as AND. Generic OR condition groups such
  as `any_of` or `one_of` are not implemented yet; use separate policies for
  alternative applicability routes until explicit OR groups exist.
