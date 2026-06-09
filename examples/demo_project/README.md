# JIKUO Demo Starter Project

This is a small, non-private project for trying the JIKUO first-run loop
without using the maintainer's local documents.

The demo intentionally starts with project documents and Document Rules, but
without activation settings, instruction files, runtime receipts, or active
starter policies. Those gaps let a new user see what JIKUO reports before setup
and practice the guarded first-run paths.

## Try The Readiness Checks

Run these commands from the JIKUO repository root:

```powershell
python -B -m jikuo doctor --project-root examples/demo_project --format markdown
python -B -m jikuo configure status --project-root examples/demo_project --format markdown
python -B -m jikuo studio status --project-root examples/demo_project --format markdown
```

Expected first-run shape:

- project context is present;
- Document Rules can read the demo documents;
- activation settings still need review;
- starter policies still need preview and guarded activation;
- runtime receipts are not present until a JIKUO-producing command or host turn
  writes them.

You may also see registry-shard diagnostics. The demo focuses on first-run
product use, not the full JIKUO product-development registry used by this
repository.

## Preview Starter Policy Activation

Preview the official starter policy pack without writing files:

```powershell
python -B -m jikuo.starter_policies plan-init --project-root examples/demo_project --format text
```

The preview shows which policy snapshots, decision records, project state, and
policy manifest files would be written. Apply it only after reviewing the plan
and providing the required approval phrase.

## Preview A Document Rules Change

The demo has one optional document that is not required. Preview adding it as a
context document:

```powershell
python -B -m jikuo studio document-rules plan --project-root examples/demo_project --add-context-doc docs/workflow-notes.md --format markdown
```

This command is no-write. It demonstrates that Document Rules changes go
through preview/apply instead of browser-side edits.

## Open Studio Against The Demo

```powershell
python -B -m jikuo studio serve --project-root examples/demo_project --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/`.

The demo is not a template generator and does not claim strict mounted
execution. It is a public training project for inspecting the current product
loop.
