from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TextIO


DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_TRIGGER_MODE = "mounted"
HOOK_EVENT_NAME = "UserPromptSubmit"


class HookExecutionError(RuntimeError):
    """Raised when the JIKUO no-write pre-turn call cannot complete."""


@dataclass(frozen=True)
class HookInput:
    hook_event_name: str
    prompt: str
    cwd: Path
    session_id: str | None
    turn_id: str | None
    permission_mode: str | None
    model: str | None


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def extract_hook_input(payload: dict[str, Any], env: dict[str, str] | None = None) -> HookInput:
    env = env or os.environ
    cwd_value = _string_or_none(payload.get("cwd")) or env.get("PWD") or os.getcwd()
    return HookInput(
        hook_event_name=_string_or_none(payload.get("hook_event_name"))
        or _string_or_none(payload.get("hookEventName"))
        or "",
        prompt=_string_or_none(payload.get("prompt")) or "",
        cwd=Path(cwd_value),
        session_id=_string_or_none(payload.get("session_id"))
        or _string_or_none(payload.get("sessionId")),
        turn_id=_string_or_none(payload.get("turn_id")) or _string_or_none(payload.get("turnId")),
        permission_mode=_string_or_none(payload.get("permission_mode"))
        or _string_or_none(payload.get("permissionMode")),
        model=_string_or_none(payload.get("model")),
    )


def find_project_root(start: Path, script_path: Path | None = None) -> Path:
    candidates = [start.resolve()]
    if script_path is not None:
        resolved_script = script_path.resolve()
        candidates.append(resolved_script.parent)
        if len(resolved_script.parents) >= 3:
            candidates.append(resolved_script.parents[2])

    for candidate in candidates:
        current = candidate if candidate.is_dir() else candidate.parent
        for path in [current, *current.parents]:
            if (path / ".jikuo").exists():
                return path
            if (path / ".codex").exists() and (path / "pyproject.toml").exists():
                return path
            if (path / "src" / "jikuo").exists() and (path / "pyproject.toml").exists():
                return path

    return start.resolve()


def trigger_mode_from_env(env: dict[str, str] | None = None) -> str:
    env = env or os.environ
    return env.get("JIKUO_HOOK_TRIGGER_MODE") or DEFAULT_TRIGGER_MODE


def timeout_from_env(env: dict[str, str] | None = None) -> int:
    env = env or os.environ
    raw_value = env.get("JIKUO_HOOK_TIMEOUT_SECONDS")
    if not raw_value:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        value = int(raw_value)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return max(1, value)


def pythonpath_for_project(project_root: Path, env: dict[str, str]) -> str:
    src_path = project_root / "src"
    existing = env.get("PYTHONPATH")
    if src_path.exists():
        if existing:
            return str(src_path) + os.pathsep + existing
        return str(src_path)
    return existing or ""


def build_agent_flow_command(
    hook_input: HookInput,
    project_root: Path,
    trigger_mode: str,
    env: dict[str, str] | None = None,
) -> list[str]:
    env = env or os.environ
    python_exe = env.get("JIKUO_HOOK_PYTHON") or sys.executable
    command = [
        python_exe,
        "-B",
        "-m",
        "jikuo.agent_flow",
        "propose",
        "--event",
        "conversation_turn",
        "--project-root",
        str(project_root),
        "--trigger-mode",
        trigger_mode,
        "--format",
        "json",
    ]
    if hook_input.prompt:
        command.append("--user-phrase-stdin")
    return command


def run_agent_flow(
    hook_input: HookInput,
    project_root: Path,
    trigger_mode: str,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    process_env = dict(env or os.environ)
    pythonpath = pythonpath_for_project(project_root, process_env)
    if pythonpath:
        process_env["PYTHONPATH"] = pythonpath
    command = build_agent_flow_command(hook_input, project_root, trigger_mode, process_env)
    try:
        completed = subprocess.run(
            command,
            cwd=project_root,
            env=process_env,
            input=hook_input.prompt if hook_input.prompt else None,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_from_env(process_env),
            check=False,
        )
    except OSError as exc:
        raise HookExecutionError(f"JIKUO command could not start: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise HookExecutionError("JIKUO command timed out") from exc

    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip().splitlines()
        detail = stderr[-1] if stderr else "no stderr"
        raise HookExecutionError(f"JIKUO command failed with exit {completed.returncode}: {detail}")

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HookExecutionError("JIKUO command did not return JSON") from exc
    if not isinstance(result, dict):
        raise HookExecutionError("JIKUO command returned a non-object JSON value")
    return result


def _display_link(proposal: dict[str, Any], link_name: str) -> str | None:
    client_links = proposal.get("client_display_links")
    if not isinstance(client_links, dict):
        return None
    links = client_links.get("links")
    if not isinstance(links, dict):
        return None
    link = links.get(link_name)
    if not isinstance(link, dict):
        return None
    return _string_or_none(link.get("markdown")) or _string_or_none(link.get("ref"))


def _runtime_ref(proposal: dict[str, Any], key: str) -> str | None:
    runtime = proposal.get("runtime_visibility")
    if not isinstance(runtime, dict):
        return None
    return _string_or_none(runtime.get(key))


def _work_profile_summary(proposal: dict[str, Any]) -> str:
    work_profile = proposal.get("work_profile")
    if not isinstance(work_profile, dict):
        return "work_profile=unavailable"
    lifecycle = work_profile.get("lifecycle_event") or "unknown"
    scopes = work_profile.get("policy_scopes")
    if isinstance(scopes, list):
        scopes_text = ", ".join(str(item) for item in scopes) or "none"
    else:
        scopes_text = "unavailable"
    return f"lifecycle_event={lifecycle}; policy_scopes={scopes_text}"


def _required_followup_tools(proposal: dict[str, Any]) -> list[str]:
    router = proposal.get("conversation_router")
    if not isinstance(router, dict):
        return []
    tools = router.get("required_followup_tools")
    if not isinstance(tools, list):
        return []
    return [str(item) for item in tools if item]


def render_additional_context(
    proposal: dict[str, Any],
    hook_input: HookInput,
    project_root: Path,
    trigger_mode: str,
    semantic_intent_status: str,
) -> str:
    triggered = proposal.get("triggered_policies")
    triggered_count = len(triggered) if isinstance(triggered, list) else 0
    missing = proposal.get("missing_evidence_reports")
    missing_count = len(missing) if isinstance(missing, list) else 0
    latest = _display_link(proposal, "last_card") or _runtime_ref(proposal, "last_card_ref")
    history = _display_link(proposal, "history_card") or _runtime_ref(proposal, "history_ref")
    followups = _required_followup_tools(proposal)

    lines = [
        "JIKUO mounted pre-turn ran before substantive model work.",
        f"Trigger mode: {trigger_mode}.",
        f"Semantic intent status: {semantic_intent_status}.",
        "Semantic classification note: no host AI semantic intent was provided by this Level 1 hook proof; deterministic JIKUO routing may be used as fallback/conflict evidence.",
        f"Project root: {project_root}.",
        f"Session id: {hook_input.session_id or 'unavailable'}.",
        f"Turn id: {hook_input.turn_id or 'unavailable'}.",
        f"Work profile: {_work_profile_summary(proposal)}.",
        f"Triggered policy count: {triggered_count}.",
        f"Missing evidence report count: {missing_count}.",
        f"Latest card: {latest or 'unavailable'}.",
        f"History card: {history or 'unavailable'}.",
        "Required follow-up tools: " + (", ".join(followups) if followups else "none reported."),
        "Durable writes remain guarded; this hook must not create task sessions, policies, commits, or evidence writes by itself.",
        "Privacy boundary: the hook passes the prompt to JIKUO over stdin and does not persist the raw prompt or transcript in hook-owned files.",
    ]
    return "\n".join(lines)


def render_failure_context(error: Exception, hook_input: HookInput, project_root: Path) -> str:
    return "\n".join(
        [
            "JIKUO mounted pre-turn failed or degraded before substantive model work.",
            f"Project root: {project_root}.",
            f"Session id: {hook_input.session_id or 'unavailable'}.",
            f"Turn id: {hook_input.turn_id or 'unavailable'}.",
            f"Failure summary: {error}",
            "Do not claim strict-mounted JIKUO ran for this turn unless a later visible card proves it.",
            "Privacy boundary: the hook passes the prompt to JIKUO over stdin when available and does not persist the raw prompt or transcript in hook-owned files.",
        ]
    )


def hook_output(additional_context: str, *, system_message: str | None = None) -> dict[str, Any]:
    output: dict[str, Any] = {
        "hookSpecificOutput": {
            "hookEventName": HOOK_EVENT_NAME,
            "additionalContext": additional_context,
        }
    }
    if system_message:
        output["systemMessage"] = system_message
    return output


Runner = Callable[[HookInput, Path, str], dict[str, Any]]


def main(
    argv: list[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    runner: Runner | None = None,
    env: dict[str, str] | None = None,
) -> int:
    del argv
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    env = env or os.environ
    runner = runner or (lambda hook_input, project_root, trigger_mode: run_agent_flow(
        hook_input,
        project_root,
        trigger_mode,
        env,
    ))

    try:
        payload = json.load(stdin)
        if not isinstance(payload, dict):
            raise ValueError("hook stdin must be a JSON object")
        hook_input = extract_hook_input(payload, env)
    except Exception as exc:
        fallback_input = HookInput("", "", Path(env.get("PWD") or os.getcwd()), None, None, None, None)
        project_root = find_project_root(fallback_input.cwd, Path(__file__))
        output = hook_output(
            render_failure_context(exc, fallback_input, project_root),
            system_message="JIKUO hook could not parse Codex hook input.",
        )
        json.dump(output, stdout)
        stdout.write("\n")
        return 0

    project_root = find_project_root(hook_input.cwd, Path(__file__))
    trigger_mode = trigger_mode_from_env(env)

    if hook_input.hook_event_name != HOOK_EVENT_NAME:
        output = hook_output(
            render_failure_context(
                HookExecutionError(f"unsupported hook event {hook_input.hook_event_name!r}"),
                hook_input,
                project_root,
            ),
            system_message="JIKUO hook received an unexpected Codex hook event.",
        )
        json.dump(output, stdout)
        stdout.write("\n")
        return 0

    try:
        proposal = runner(hook_input, project_root, trigger_mode)
        output = hook_output(
            render_additional_context(
                proposal,
                hook_input,
                project_root,
                trigger_mode,
                semantic_intent_status="unavailable",
            )
        )
    except Exception as exc:
        output = hook_output(
            render_failure_context(exc, hook_input, project_root),
            system_message="JIKUO pre-turn check failed; strict mounted status is not proven for this turn.",
        )

    json.dump(output, stdout)
    stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
