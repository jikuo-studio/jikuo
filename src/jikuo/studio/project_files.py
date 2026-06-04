"""No-write project-file inventory for JIKUO Studio."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

if __package__:
    from .. import project_state
    from . import document_rules
else:  # pragma: no cover - direct script fallback for ad hoc inspection
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from jikuo import project_state
    from jikuo.studio import document_rules


PROJECT_FILE_INVENTORY_SCHEMA = "jikuo.studio.project_file_inventory.v0"
DEFAULT_MAX_ITEMS = 500
DOCUMENT_SUFFIXES = {".md", ".markdown", ".yaml", ".yml", ".json", ".txt"}
SKIPPED_DIRS = {
    ".claude",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "browser_profiles",
    "build",
    ".codex_tmp",
    "dist",
    "node_modules",
}
INCLUDED_JIKUO_FILES = {(".jikuo", "project_context.yaml")}


def utc_from_timestamp(value: float) -> str:
    return (
        datetime.fromtimestamp(value, timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".json":
        return "json"
    if suffix == ".txt":
        return "text"
    return "document"


def should_include_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in DOCUMENT_SUFFIXES


def should_skip_path(project_root: Path, path: Path) -> bool:
    relative_parts = path.relative_to(project_root).parts
    if not relative_parts:
        return False
    if relative_parts[0] == ".jikuo":
        return relative_parts not in INCLUDED_JIKUO_FILES
    return any(part in SKIPPED_DIRS for part in relative_parts)


def path_membership(context: dict[str, Any], path_ref: str) -> dict[str, Any]:
    roles = document_rules.document_roles(context)
    completion_paths = {
        str(item.get("path") or "")
        for item in document_rules.existing_completion_checks(context)
        if isinstance(item, dict)
    }
    authority_paths = set(document_rules.existing_authority_refs(context))
    role_refs = [
        str(role)
        for role, record in sorted(roles.items())
        if isinstance(record, dict) and str(record.get("path") or "") == path_ref
    ]
    return {
        "context_role_refs": role_refs,
        "is_context_document": bool(role_refs),
        "is_completion_check": path_ref in completion_paths,
        "is_governance_reference": path_ref in authority_paths,
    }


def iter_project_document_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in project_root.rglob("*"):
        if should_skip_path(project_root, path):
            continue
        if should_include_file(path):
            files.append(path)
    return sorted(files, key=lambda item: file_sort_key(project_root, item))


def file_sort_key(project_root: Path, path: Path) -> tuple[int, str]:
    path_ref = path.relative_to(project_root).as_posix()
    if path_ref == "README.md":
        return (0, path_ref)
    if path_ref == "docs/README.md":
        return (1, path_ref)
    if path_ref.startswith("docs/"):
        return (2, path_ref)
    if path_ref == ".jikuo/project_context.yaml":
        return (3, path_ref)
    if path_ref.startswith(".jikuo/"):
        return (5, path_ref)
    if path_ref.startswith(".codex/"):
        return (6, path_ref)
    return (4, path_ref)


def build_project_file_inventory(
    *,
    project_root: Path | None = None,
    max_items: int = DEFAULT_MAX_ITEMS,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    context, context_errors = document_rules.load_project_context(resolved_root)
    warnings: list[dict[str, Any]] = list(context_errors)
    files = iter_project_document_files(resolved_root)
    truncated = len(files) > max_items
    items: list[dict[str, Any]] = []
    skipped_during_scan = 0
    for path in files[:max_items]:
        path_ref = path.relative_to(resolved_root).as_posix()
        try:
            stat = path.stat()
        except OSError as exc:
            skipped_during_scan += 1
            warnings.append(
                {
                    "code": "project_file_disappeared_during_scan",
                    "path": path_ref,
                    "message": f"Skipped file because it changed during inventory scan: {exc}",
                    "severity": "warning",
                }
            )
            continue
        items.append(
            {
                "path": path_ref,
                "label": path.name,
                "file_kind": file_kind(path),
                "size_bytes": stat.st_size,
                "modified_at_utc": utc_from_timestamp(stat.st_mtime),
                "document_rules_membership": path_membership(context, path_ref),
            }
        )
    return {
        "schema": PROJECT_FILE_INVENTORY_SCHEMA,
        "status": "degraded" if context_errors or skipped_during_scan else "available",
        "project_root": str(resolved_root),
        "item_count": len(items),
        "total_candidate_count": len(files),
        "skipped_during_scan_count": skipped_during_scan,
        "truncated": truncated,
        "max_items": max_items,
        "items": items,
        "warnings": warnings,
        "write_mode": "no-write-read-model",
        "writes_performed": False,
        "write_allowed_by_command": False,
        "non_effects": [
            "does_not_write_project_context",
            "does_not_mutate_document_rules",
            "does_not_read_raw_chat_transcripts",
        ],
    }
