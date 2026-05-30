"""Policy-management status read model.

This module provides a no-write backend surface for GUI and MCP clients. It
collects the active project policy store, package-owned policy templates, and
starter-pack manifests into one compact status report without publishing,
activating, or evolving policies.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

if __package__:
    from . import policy_store, policy_templates, project_state, starter_policies
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import policy_store
    import policy_templates
    import project_state
    import starter_policies


POLICY_MANAGEMENT_STATUS_SCHEMA = "jikuo.policy_management_status.v0"
DEFAULT_TEMPLATE_DIR = Path("policy_templates") / "engineering_governance"
DEFAULT_STARTER_PACK_ID = starter_policies.DEFAULT_PACK_ID
SOURCE_REFS = [
    "pkg://jikuo/governance/jikuo_policy_governance_authority.md",
    "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01_policy_management_mvp.md",
]


def package_root() -> Path:
    return Path(__file__).resolve().parent


def template_dir_path(template_dir: Path | None = None) -> Path:
    if template_dir is not None:
        return template_dir.expanduser().resolve()
    return package_root() / DEFAULT_TEMPLATE_DIR


def package_ref(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(package_root().resolve())
    except ValueError:
        return f"redacted://local_package_file/{policy_templates.file_sha256(resolved)}"
    return f"pkg://jikuo/{relative.as_posix()}"


def load_package_templates(
    *,
    template_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    resolved_dir = template_dir_path(template_dir)
    warnings: list[str] = []
    templates: list[dict[str, Any]] = []
    try:
        resolved_dir.relative_to((package_root() / "policy_templates").resolve())
    except ValueError:
        return [], [f"template_dir_outside_package_policy_templates:{resolved_dir}"]
    if not resolved_dir.exists():
        return [], [f"policy_template_dir_missing:{resolved_dir}"]
    if not resolved_dir.is_dir():
        return [], [f"policy_template_dir_not_directory:{resolved_dir}"]

    for path in sorted(resolved_dir.glob("*.yaml")):
        try:
            record = policy_templates.read_yaml_subset(path)
        except OSError as exc:
            warnings.append(f"policy_template_not_readable:{path}:{exc}")
            continue
        schema = record.get("schema_version") or record.get("schema")
        if schema != policy_templates.POLICY_TEMPLATE_SCHEMA:
            warnings.append(f"unsupported_policy_template_schema:{path}:{schema}")
            continue
        template_policy = record.get("template_policy")
        if not isinstance(template_policy, dict):
            template_policy = {}
            warnings.append(f"policy_template_missing_template_policy:{path}")
        templates.append(
            {
                "template_id": record.get("template_id"),
                "template_ref": package_ref(path),
                "template_path": str(path),
                "namespace": record.get("namespace"),
                "version": record.get("version"),
                "title": record.get("title"),
                "template_policy_id": template_policy.get("policy_id"),
                "template_policy_title": template_policy.get("title"),
                "template_policy_status": template_policy.get("status"),
                "portability_status": (record.get("portability") or {}).get("status")
                if isinstance(record.get("portability"), dict)
                else None,
                "required_binding_count": len(record.get("required_bindings") or []),
                "included_in_starter_packs": [],
            }
        )
    return templates, warnings


def iter_starter_manifest_paths(pack_id: str | None) -> list[Path]:
    if pack_id:
        return [starter_policies.pack_manifest_path(pack_id)]
    root = starter_policies.STARTER_PACKS_ROOT
    if not root.exists() or not root.is_dir():
        return []
    return sorted(root.glob("*/manifest.yaml"))


def load_starter_pack_summaries(
    *,
    pack_id: str | None = DEFAULT_STARTER_PACK_ID,
) -> tuple[list[dict[str, Any]], list[str]]:
    packs: list[dict[str, Any]] = []
    warnings: list[str] = []
    for manifest_path in iter_starter_manifest_paths(pack_id):
        current_pack_id = manifest_path.parent.name
        manifest, manifest_warnings = starter_policies.load_pack_manifest(current_pack_id)
        warnings.extend(manifest_warnings)
        if manifest is None:
            packs.append(
                {
                    "pack_id": current_pack_id,
                    "status": "missing_or_invalid",
                    "manifest_path": str(manifest_path),
                    "manifest_ref": package_ref(manifest_path)
                    if manifest_path.exists()
                    else None,
                    "template_count": 0,
                    "policy_templates": [],
                    "warnings": manifest_warnings,
                }
            )
            continue
        entries = starter_policies.existing_manifest_template_entries(manifest)
        packs.append(
            {
                "pack_id": manifest.get("pack_id") or current_pack_id,
                "status": "available" if not manifest_warnings else "review",
                "title": manifest.get("title"),
                "description": manifest.get("description"),
                "manifest_path": str(manifest_path),
                "manifest_ref": package_ref(manifest_path),
                "template_count": len(entries),
                "policy_templates": [
                    {
                        "template_ref": item.get("template_ref"),
                        "policy_id": item.get("policy_id"),
                        "title": item.get("title"),
                    }
                    for item in entries
                ],
                "warnings": manifest_warnings,
            }
        )
    return packs, warnings


def starter_membership_by_template(
    starter_packs: list[dict[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    output: dict[str, list[dict[str, str]]] = {}
    for pack in starter_packs:
        pack_id = str(pack.get("pack_id") or "")
        for item in pack.get("policy_templates") or []:
            if not isinstance(item, dict):
                continue
            template_ref = item.get("template_ref")
            if not isinstance(template_ref, str) or not template_ref:
                continue
            output.setdefault(template_ref, []).append(
                {
                    "pack_id": pack_id,
                    "policy_id": str(item.get("policy_id") or ""),
                    "title": str(item.get("title") or ""),
                }
            )
    return output


def active_policy_distribution_summary(
    active_policy: dict[str, Any],
    *,
    templates_by_policy_id: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    policy_id = str(active_policy.get("policy_id") or "")
    matching_templates = templates_by_policy_id.get(policy_id, [])
    template_refs = [str(item.get("template_ref")) for item in matching_templates]
    in_starter = [
        pack
        for template in matching_templates
        for pack in template.get("included_in_starter_packs") or []
    ]
    if in_starter:
        state = "starter_pack_available"
    elif matching_templates:
        state = "package_template_available"
    else:
        state = "active_project_policy_only"
    return {
        "policy_id": policy_id,
        "title": active_policy.get("title"),
        "status": active_policy.get("status"),
        "path": active_policy.get("path"),
        "distribution_state": state,
        "package_template_refs": template_refs,
        "starter_pack_refs": in_starter,
        "next_actions": [
            "review distribution decision before publication",
            "plan package-template publication only for reusable outcomes",
        ]
        if state == "active_project_policy_only"
        else [
            "review package template before importing into a user project",
            "use guarded starter/template activation for user-project adoption",
        ],
    }


def build_policy_management_status(
    *,
    project_root: Path | None = None,
    starter_pack_id: str | None = DEFAULT_STARTER_PACK_ID,
    template_dir: Path | None = None,
) -> dict[str, Any]:
    resolved_root = project_state.discover_project_root(project_root=project_root)
    policy_report = policy_store.inspect_policy_store(project_root=resolved_root)
    templates, template_warnings = load_package_templates(template_dir=template_dir)
    starter_packs, starter_warnings = load_starter_pack_summaries(pack_id=starter_pack_id)
    membership = starter_membership_by_template(starter_packs)
    for template in templates:
        template["included_in_starter_packs"] = membership.get(
            str(template.get("template_ref") or ""),
            [],
        )

    templates_by_policy_id: dict[str, list[dict[str, Any]]] = {}
    for template in templates:
        policy_id = template.get("template_policy_id")
        if isinstance(policy_id, str) and policy_id:
            templates_by_policy_id.setdefault(policy_id, []).append(template)

    active_policy_distribution = [
        active_policy_distribution_summary(
            active_policy,
            templates_by_policy_id=templates_by_policy_id,
        )
        for active_policy in policy_report.get("active_policy_refs") or []
        if isinstance(active_policy, dict)
    ]
    active_with_templates = [
        item
        for item in active_policy_distribution
        if item["distribution_state"] != "active_project_policy_only"
    ]
    active_without_templates = [
        item
        for item in active_policy_distribution
        if item["distribution_state"] == "active_project_policy_only"
    ]

    warnings = [
        *(policy_report.get("warnings") or []),
        *template_warnings,
        *starter_warnings,
    ]
    status = "review" if warnings else "available"
    return {
        "schema": POLICY_MANAGEMENT_STATUS_SCHEMA,
        "schema_version": POLICY_MANAGEMENT_STATUS_SCHEMA,
        "report_only": True,
        "status": status,
        "project_root": str(resolved_root),
        "write_allowed_by_command": False,
        "writes_performed": False,
        "policy_store": {
            "status": policy_report.get("policy_store_status"),
            "manifest_ref": policy_report.get("manifest_ref"),
            "active_policy_count": len(policy_report.get("active_policy_refs") or []),
            "proposal_ref_count": len(policy_report.get("proposal_refs") or []),
            "deprecated_policy_ref_count": len(
                policy_report.get("deprecated_policy_refs") or []
            ),
            "superseded_policy_ref_count": len(
                policy_report.get("superseded_policy_refs") or []
            ),
            "active_policies": policy_report.get("active_policy_refs") or [],
        },
        "package_templates": {
            "template_dir": str(template_dir_path(template_dir)),
            "template_count": len(templates),
            "templates": templates,
        },
        "starter_packs": {
            "requested_pack_id": starter_pack_id,
            "pack_count": len(starter_packs),
            "packs": starter_packs,
        },
        "active_policy_distribution": active_policy_distribution,
        "summary_counts": {
            "active_policy_count": len(policy_report.get("active_policy_refs") or []),
            "package_template_count": len(templates),
            "starter_pack_count": len(starter_packs),
            "starter_template_ref_count": sum(
                len(pack.get("policy_templates") or []) for pack in starter_packs
            ),
            "active_policy_with_package_template_count": len(active_with_templates),
            "active_policy_without_package_template_count": len(active_without_templates),
        },
        "available_operations": [
            {
                "operation": "distribution_review",
                "surface": "jikuo.propose_policy_distribution_review",
                "write_mode": "no-write",
            },
            {
                "operation": "policy_template_publication_plan",
                "surface": "jikuo.propose_policy_template_publication_plan",
                "write_mode": "no-write",
            },
            {
                "operation": "policy_template_publication",
                "surface": "jikuo.apply_policy_template_publication",
                "write_mode": "guarded-write",
            },
            {
                "operation": "starter_manifest_publication_plan",
                "surface": "jikuo.propose_starter_manifest_publication_plan",
                "write_mode": "no-write",
            },
            {
                "operation": "starter_manifest_publication",
                "surface": "jikuo.apply_starter_manifest_publication",
                "write_mode": "guarded-write",
            },
        ],
        "read_model_limitations": [
            "distribution review decisions are report-only unless separately recorded",
            "package template availability is not user-project activation",
            "starter manifest inclusion is not user-project initialization",
            "natural-language policy selection still depends on host AI or deterministic candidate matching",
        ],
        "non_effects": [
            "does not publish package templates",
            "does not update starter-pack manifests",
            "does not activate or rewrite user-project policies",
            "does not change policy evaluator behavior",
        ],
        "warnings": sorted(set(str(item) for item in warnings)),
        "source_refs": SOURCE_REFS,
        "next_actions": [
            "use this read model as the backend source for a thin policy-management UI",
            "run no-write distribution review before publishing any reusable policy",
            "keep user-project activation behind template import or starter-init guarded flows",
        ],
    }


def format_markdown(report: dict[str, Any]) -> str:
    counts = report.get("summary_counts") or {}
    lines = [
        "# JIKUO Policy Management Status",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Schema: `{report.get('schema')}`",
        f"- Project root: `{report.get('project_root')}`",
        f"- Active policies: `{counts.get('active_policy_count')}`",
        f"- Package templates: `{counts.get('package_template_count')}`",
        f"- Starter packs: `{counts.get('starter_pack_count')}`",
        f"- Starter template refs: `{counts.get('starter_template_ref_count')}`",
        f"- Active policies with package templates: `{counts.get('active_policy_with_package_template_count')}`",
        f"- Active policies without package templates: `{counts.get('active_policy_without_package_template_count')}`",
        "",
        "## Active Policy Distribution",
    ]
    for item in report.get("active_policy_distribution") or []:
        lines.append(
            f"- `{item.get('policy_id')}` / `{item.get('distribution_state')}` / "
            f"{item.get('title') or ''}"
        )
    lines.extend(["", "## Package Templates"])
    for item in (report.get("package_templates") or {}).get("templates") or []:
        starter_packs = item.get("included_in_starter_packs") or []
        pack_text = ", ".join(str(pack.get("pack_id")) for pack in starter_packs) or "none"
        lines.append(
            f"- `{item.get('template_ref')}` / policy=`{item.get('template_policy_id')}` / "
            f"starter_packs=`{pack_text}`"
        )
    lines.extend(["", "## Starter Packs"])
    for pack in (report.get("starter_packs") or {}).get("packs") or []:
        lines.append(
            f"- `{pack.get('pack_id')}` / templates=`{pack.get('template_count')}` / "
            f"status=`{pack.get('status')}`"
        )
    if report.get("warnings"):
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend(["", "## Next Actions"])
    lines.extend(f"- {item}" for item in report.get("next_actions") or [])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect JIKUO policy-management status.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status")
    status.add_argument("--project-root", type=Path, default=None)
    status.add_argument("--starter-pack-id", default=DEFAULT_STARTER_PACK_ID)
    status.add_argument("--template-dir", type=Path, default=None)
    status.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "status":
        report = build_policy_management_status(
            project_root=args.project_root,
            starter_pack_id=args.starter_pack_id,
            template_dir=args.template_dir,
        )
        if args.format == "markdown":
            print(format_markdown(report), end="")
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("status") in {"available", "review"} else 2
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
