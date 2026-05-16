# SPRINT_050_WO-PER-JIKUO-INTG-01: Universal Instruction File Distribution

> **Status**: Implemented and accepted on 2026-05-14, pre-MCP companion for cross-client behavior
> **Product meaning**: distribute the JIKUO harness display contract through project-level instruction files used by multiple desktop Agent clients.
> **Scope rule**: provide generic instruction-file generation and sync; do not depend on a single client hook or plugin.

## 1. Why This Slice Now

MCP improves tool invocation, but model behavior still depends partly on client instructions. JIKUO needs a universal instruction source that explains:

- when to invoke JIKUO
- that returned governance cards must be displayed verbatim
- where the user can independently verify runtime status

Client-specific hooks remain useful, but they are a later enhancement layer.

## 2. User Scenario

- A project initializes JIKUO.
- JIKUO creates or updates a canonical `JIKUO.md` instruction file.
- The user or agent syncs the instruction into supported client-specific files.
- Agents that read project instructions learn the same harness display contract.

## 3. In Scope

Create and maintain:

- `JIKUO.md`: canonical project-level JIKUO instruction file
- `jikuo install --client codex`: sync compatible content into `AGENTS.md`
- `jikuo install --client claude-code`: sync compatible content into `CLAUDE.md`
- `jikuo install --client cursor`: sync compatible content into `.cursorrules`
- `jikuo install --client vscode-copilot`: sync compatible content into `.github/copilot-instructions.md`
- `jikuo install --client continue`: sync compatible content into `.continuerules`
- `jikuo install --all`: detect known client files and propose/sync supported instruction targets
- `jikuo install --trigger-mode ask|semantic|mounted`: write the client-facing JIKUO activation mode into the managed instruction block

## 4. Required Instruction Content

The canonical instruction file must include:

- JIKUO is a deterministic harness once activated.
- The Agent must call the runner or MCP tool for covered flows.
- Returned governance card markdown must be shown verbatim before commentary.
- Runtime visibility files and `jikuo show` are user verification channels.
- Guarded writes require explicit approval phrases and technical confirmation.
- First-use activation settings must be visible: trigger mode, MCP availability, card display, runtime links, guarded-write approval boundary, starter policy initialization, and project-context bindings.

## 5. Out Of Scope

- client-specific hooks
- Codex Plugin packaging
- Claude Code Skill packaging
- Cursor extension packaging
- MCP implementation
- dashboard UI

## 6. Acceptance Criteria

- `JIKUO.md` can be generated without overwriting unrelated user content.
- Client-specific sync is explicit and reviewable.
- The generated instructions name both chat-ready cards and out-of-band runtime verification.
- No client-specific integration becomes a prerequisite for baseline JIKUO visibility.

## 7. Implemented Result

Implemented on 2026-05-14.

Implementation:

- `src/jikuo/integrations/instruction_files.py` provides the integration-layer planner and guarded writer.
- `jikuo install` exposes the flow through the top-level CLI.
- default mode is review-only and writes nothing.
- write mode requires `--write`, `--confirm-install`, and `--approval-phrase`.
- generated files use managed blocks bounded by `# BEGIN JIKUO MANAGED INSTRUCTIONS` and `# END JIKUO MANAGED INSTRUCTIONS`, preserving unrelated existing content.
- `--all` detects existing supported client instruction files and always includes canonical `JIKUO.md`.
- generated instructions now include activation settings and can pin `ask`, `semantic`, or `mounted` trigger mode per client.
- `vscode-copilot` is supported as a client target through `.github/copilot-instructions.md`.

Verification:

- `tests/instruction_files_tests.py` covers no-write planning, guarded write refusal, content-preserving sync, trigger-mode managed-block content, VS Code Copilot target selection, `--all` detection, and top-level CLI JSON output.
- This slice does not implement MCP, client hooks, plugins, dashboard UI, or Agent SDK runners.
