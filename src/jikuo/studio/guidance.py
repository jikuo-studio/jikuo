"""Stable Studio guidance-link registry and resolver.

This module is read-only. It turns maintainer-authored documentation link
registry entries into deterministic read-model records for Studio.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .. import policy_templates


GUIDANCE_REGISTRY_SCHEMA = "jikuo.studio.guidance_registry.v0"
GUIDANCE_LINK_SCHEMA = "jikuo.studio.guidance_link.v0"
FIRST_RUN_GUIDANCE_SCHEMA = "jikuo.studio.first_run_guidance.v0"
GUIDANCE_REGISTRY_REF = "docs/registry/guidance_links.yaml"
VALID_COVERAGE_STATUS = {"exact", "partial", "missing"}
VALID_LINK_STATUS = {"ok", "missing", "broken"}


def product_source_root() -> Path:
    return Path(__file__).resolve().parents[3]


def guidance_authority_root(project_root: Path) -> tuple[Path, str]:
    project_registry = project_root / GUIDANCE_REGISTRY_REF
    if project_registry.is_file():
        return project_root, "project_docs"
    source_root = product_source_root()
    if (source_root / GUIDANCE_REGISTRY_REF).is_file():
        return source_root, "product_source_docs"
    return project_root, "missing"


def markdown_has_stable_anchor(markdown_text: str, anchor_id: str) -> bool:
    escaped = re.escape(anchor_id)
    patterns = [
        rf"<a\s+[^>]*(?:id|name)=['\"]{escaped}['\"]",
        rf"\{{#\s*{escaped}\s*\}}",
    ]
    return any(re.search(pattern, markdown_text) for pattern in patterns)


def missing_guidance(readiness_key: str) -> dict[str, Any]:
    title = readiness_key.replace("_", " ").title()
    return {
        "schema": GUIDANCE_LINK_SCHEMA,
        "guidance_id": f"first_run.{readiness_key}",
        "readiness_key": readiness_key,
        "title": title,
        "guidance_label": "Guidance not documented yet",
        "doc_ref": None,
        "doc_path": None,
        "anchor_id": None,
        "href": None,
        "doc_title": None,
        "coverage_status": "missing",
        "link_status": "missing",
        "missing_note": "No guidance registry entry is available for this first-run item.",
        "reason": "No maintainer-authored guidance mapping is available.",
        "source": {
            "registry_ref": GUIDANCE_REGISTRY_REF,
            "authority_root": None,
            "authority_root_kind": "missing",
        },
        "non_effects": [
            "does_not_infer_document_semantics",
            "does_not_scrape_docs_in_the_frontend",
            "does_not_write_guidance_registry",
        ],
    }


def resolve_guidance_entry(
    entry: dict[str, Any],
    *,
    authority_root: Path,
    authority_root_kind: str,
) -> dict[str, Any]:
    readiness_key = str(entry.get("readiness_key") or "")
    guidance_id = str(entry.get("guidance_id") or f"first_run.{readiness_key}")
    doc_path = str(entry.get("doc_path") or "")
    anchor_id = str(entry.get("anchor_id") or "")
    coverage_status = str(entry.get("coverage_status") or "missing")
    if coverage_status not in VALID_COVERAGE_STATUS:
        coverage_status = "missing"
    doc_ref = f"{doc_path}#{anchor_id}" if doc_path and anchor_id else doc_path or None
    href = doc_ref
    link_status = "missing" if coverage_status == "missing" else "ok"
    broken_reason: str | None = None

    if coverage_status != "missing":
        if not doc_path:
            link_status = "broken"
            broken_reason = "doc_path_missing"
        else:
            resolved_doc = authority_root / doc_path
            if not resolved_doc.is_file():
                link_status = "broken"
                broken_reason = "doc_missing"
            elif anchor_id:
                try:
                    markdown_text = resolved_doc.read_text(encoding="utf-8")
                except OSError:
                    markdown_text = ""
                if not markdown_has_stable_anchor(markdown_text, anchor_id):
                    link_status = "broken"
                    broken_reason = "anchor_missing"
    if link_status != "ok":
        href = None

    resolved = {
        "schema": GUIDANCE_LINK_SCHEMA,
        "guidance_id": guidance_id,
        "readiness_key": readiness_key,
        "title": str(entry.get("title") or readiness_key.replace("_", " ").title()),
        "guidance_label": str(entry.get("guidance_label") or "Open guidance"),
        "doc_ref": doc_ref,
        "doc_path": doc_path or None,
        "anchor_id": anchor_id or None,
        "href": href,
        "doc_title": str(entry.get("doc_title") or "") or None,
        "coverage_status": coverage_status,
        "link_status": link_status,
        "broken_reason": broken_reason,
        "missing_note": str(entry.get("missing_note") or ""),
        "reason": str(entry.get("reason") or ""),
        "source": {
            "registry_ref": GUIDANCE_REGISTRY_REF,
            "authority_root": str(authority_root),
            "authority_root_kind": authority_root_kind,
        },
        "non_effects": [
            "does_not_infer_document_semantics",
            "does_not_scrape_docs_in_the_frontend",
            "does_not_write_guidance_registry",
        ],
    }
    return resolved


def build_guidance_registry(*, project_root: Path) -> dict[str, Any]:
    authority_root, authority_root_kind = guidance_authority_root(project_root)
    registry_path = authority_root / GUIDANCE_REGISTRY_REF
    if not registry_path.is_file():
        return {
            "schema": GUIDANCE_REGISTRY_SCHEMA,
            "status": "missing",
            "registry_ref": GUIDANCE_REGISTRY_REF,
            "authority_root": str(authority_root),
            "authority_root_kind": authority_root_kind,
            "entries": [],
            "entry_count": 0,
            "ok_count": 0,
            "broken_count": 0,
            "missing_count": 0,
            "warnings": ["guidance_registry_missing"],
            "writes_performed": False,
        }
    try:
        raw = policy_templates.read_yaml_subset(registry_path)
    except Exception as exc:
        return {
            "schema": GUIDANCE_REGISTRY_SCHEMA,
            "status": "invalid",
            "registry_ref": GUIDANCE_REGISTRY_REF,
            "authority_root": str(authority_root),
            "authority_root_kind": authority_root_kind,
            "entries": [],
            "entry_count": 0,
            "ok_count": 0,
            "broken_count": 0,
            "missing_count": 0,
            "warnings": [f"guidance_registry_invalid: {exc}"],
            "writes_performed": False,
        }
    raw_entries = raw.get("entries") if isinstance(raw, dict) else None
    entries = [
        resolve_guidance_entry(
            entry,
            authority_root=authority_root,
            authority_root_kind=authority_root_kind,
        )
        for entry in (raw_entries or [])
        if isinstance(entry, dict)
    ]
    broken_count = sum(1 for entry in entries if entry["link_status"] == "broken")
    missing_count = sum(1 for entry in entries if entry["link_status"] == "missing")
    status = "available" if not broken_count else "degraded"
    return {
        "schema": GUIDANCE_REGISTRY_SCHEMA,
        "status": status,
        "registry_ref": GUIDANCE_REGISTRY_REF,
        "authority_root": str(authority_root),
        "authority_root_kind": authority_root_kind,
        "schema_version": raw.get("schema_version") if isinstance(raw, dict) else None,
        "entries": entries,
        "entry_count": len(entries),
        "ok_count": sum(1 for entry in entries if entry["link_status"] == "ok"),
        "broken_count": broken_count,
        "missing_count": missing_count,
        "warnings": [],
        "writes_performed": False,
    }


def first_run_guidance_map(*, project_root: Path) -> dict[str, Any]:
    registry = build_guidance_registry(project_root=project_root)
    by_key = {
        entry["readiness_key"]: entry
        for entry in registry.get("entries") or []
        if entry.get("readiness_key")
    }
    return {
        "schema": FIRST_RUN_GUIDANCE_SCHEMA,
        "status": registry.get("status"),
        "registry_ref": registry.get("registry_ref"),
        "authority_root": registry.get("authority_root"),
        "authority_root_kind": registry.get("authority_root_kind"),
        "entry_count": registry.get("entry_count", 0),
        "ok_count": registry.get("ok_count", 0),
        "broken_count": registry.get("broken_count", 0),
        "missing_count": registry.get("missing_count", 0),
        "by_key": by_key,
        "non_effects": [
            "does_not_infer_guidance_coverage",
            "does_not_scan_docs_from_frontend",
            "does_not_write_project_files",
        ],
    }


def attach_first_run_guidance(
    first_run: dict[str, Any],
    *,
    project_root: Path,
) -> dict[str, Any]:
    guidance_map = first_run_guidance_map(project_root=project_root)
    by_key = guidance_map.get("by_key") or {}

    def attach(step: dict[str, Any]) -> dict[str, Any]:
        record = dict(step)
        key = str(record.get("key") or "")
        record["guidance"] = dict(by_key.get(key) or missing_guidance(key))
        return record

    enriched = dict(first_run)
    enriched["guidance"] = {
        key: dict(value)
        for key, value in by_key.items()
        if isinstance(value, dict)
    }
    enriched["guidance_registry"] = {
        key: value
        for key, value in guidance_map.items()
        if key != "by_key"
    }
    enriched["required_steps"] = [
        attach(step)
        for step in first_run.get("required_steps") or []
        if isinstance(step, dict)
    ]
    enriched["recommended_steps"] = [
        attach(step)
        for step in first_run.get("recommended_steps") or []
        if isinstance(step, dict)
    ]
    enriched["blockers"] = [
        attach(step)
        for step in first_run.get("blockers") or []
        if isinstance(step, dict)
    ]
    return enriched
