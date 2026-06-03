"""Read-only git working-tree write observation for runtime receipts.

The observer reports changed paths that are visible to git. It does not read
file contents, mutate the repository, or decide whether a change belongs to the
host AI, the user, or a previous round.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import Any


RUNTIME_WRITE_OBSERVATION_SCHEMA = "jikuo.runtime.write_observation.v0"
GIT_STATUS_SOURCE_REF = "git status --porcelain=v1 -z --untracked-files=all"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_git_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def operation_from_git_status(status: str) -> str:
    if status == "??":
        return "added"
    if "R" in status:
        return "renamed"
    if "D" in status:
        return "deleted"
    if "A" in status or "C" in status:
        return "added"
    if "M" in status or "T" in status:
        return "modified"
    return "unknown"


def _decode_git_output(output: bytes | str) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output


def parse_git_status_porcelain_z(output: bytes | str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    text = _decode_git_output(output)
    tokens = [token for token in text.split("\0") if token]
    items: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if len(token) < 4:
            warnings.append(
                {
                    "code": "malformed_git_status_token",
                    "token_excerpt": token[:20],
                }
            )
            continue

        git_status = token[:2]
        path = normalize_git_path(token[3:] if token[2] == " " else token[2:].lstrip())
        if not path:
            warnings.append(
                {
                    "code": "empty_git_status_path",
                    "git_status": git_status,
                }
            )
            continue

        previous_path: str | None = None
        if "R" in git_status or "C" in git_status:
            if index < len(tokens):
                previous_path = normalize_git_path(tokens[index])
                index += 1
            else:
                warnings.append(
                    {
                        "code": "missing_previous_path_for_git_status",
                        "git_status": git_status,
                        "path": path,
                    }
                )

        item = {
            "path": path,
            "operation": operation_from_git_status(git_status),
            "source_kind": "git_diff",
            "evidence_kind": "actual_write",
            "evidence_status": "observed",
            "attribution_status": "mixed_or_uncertain",
            "git_status": git_status,
            "source_ref": GIT_STATUS_SOURCE_REF,
            "reason": "read-only git working-tree observation",
        }
        if previous_path:
            item["previous_path"] = previous_path
        items.append(item)

    items.sort(key=lambda item: (str(item.get("path") or ""), str(item.get("git_status") or "")))
    return items, warnings


def unavailable_report(
    *,
    project_root: Path,
    reason: str,
    diagnostics: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema": RUNTIME_WRITE_OBSERVATION_SCHEMA,
        "schema_version": RUNTIME_WRITE_OBSERVATION_SCHEMA,
        "status": "unavailable",
        "project_root": str(project_root),
        "generated_at_utc": utc_now_iso(),
        "source_kind": "git_diff",
        "reason": reason,
        "diagnostics": diagnostics or [],
        "observed_actual_write_count": 0,
        "observed_actual_write_set": [],
        "observed_actual_write_paths": [],
        "attribution_status": "not_available",
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_write_files",
            "does_not_read_file_contents",
            "does_not_stage_or_commit",
            "does_not_reset_or_checkout",
            "does_not_prove_model_understanding",
            "does_not_assign_change_attribution",
        ],
    }


def observe_git_actual_writes(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    if not root.exists():
        return unavailable_report(
            project_root=root,
            reason="project_root_missing",
            diagnostics=[{"code": "project_root_missing", "path": str(root)}],
        )

    command = [
        "git",
        "-C",
        str(root),
        "-c",
        "core.excludesFile=",
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    ]
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
    except FileNotFoundError:
        return unavailable_report(
            project_root=root,
            reason="git_executable_unavailable",
            diagnostics=[{"code": "git_executable_unavailable"}],
        )
    except subprocess.TimeoutExpired:
        return unavailable_report(
            project_root=root,
            reason="git_status_timeout",
            diagnostics=[{"code": "git_status_timeout", "command_ref": GIT_STATUS_SOURCE_REF}],
        )

    stderr_text = _decode_git_output(completed.stderr).strip()
    if completed.returncode != 0:
        reason = "git_status_failed"
        if "not a git repository" in stderr_text.lower():
            reason = "not_git_worktree"
        return unavailable_report(
            project_root=root,
            reason=reason,
            diagnostics=[
                {
                    "code": reason,
                    "returncode": completed.returncode,
                    "stderr_excerpt": stderr_text[:500],
                    "command_ref": GIT_STATUS_SOURCE_REF,
                }
            ],
        )

    items, warnings = parse_git_status_porcelain_z(completed.stdout)
    if stderr_text:
        warnings.append(
            {
                "code": "git_status_stderr",
                "stderr_excerpt": stderr_text[:500],
            }
        )

    return {
        "schema": RUNTIME_WRITE_OBSERVATION_SCHEMA,
        "schema_version": RUNTIME_WRITE_OBSERVATION_SCHEMA,
        "status": "ok",
        "project_root": str(root),
        "generated_at_utc": utc_now_iso(),
        "source_kind": "git_diff",
        "command_ref": GIT_STATUS_SOURCE_REF,
        "observed_actual_write_count": len(items),
        "observed_actual_write_set": items,
        "observed_actual_write_paths": [str(item["path"]) for item in items],
        "attribution_status": "mixed_or_uncertain" if items else "not_applicable",
        "warnings": warnings,
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_write_files",
            "does_not_read_file_contents",
            "does_not_stage_or_commit",
            "does_not_reset_or_checkout",
            "does_not_prove_model_understanding",
            "does_not_assign_change_attribution",
        ],
    }
