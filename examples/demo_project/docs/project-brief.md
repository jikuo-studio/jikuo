# Demo Project Brief

The demo project represents a small release-notes assistant for an internal
tool. It is deliberately simple so users can focus on JIKUO setup rather than
the application domain.

## Goal

Prepare a short release note from a product brief, a decision log, and a
release checklist.

## Current Scope

- Keep the release note concise.
- Record user-visible decisions in `docs/decision-log.md`.
- Check `docs/release-checklist.md` before declaring the work complete.
- Treat JIKUO policies as report-only unless a user explicitly enables a gate.

## Non-goals

- This demo does not ship an application.
- This demo does not prove strict mounted execution.
- This demo does not provide private maintainer documents or runtime history.
