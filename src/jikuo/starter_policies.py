"""Starter policy pack planning and guarded initialization.

Starter packs are the first-use path for ordinary projects: they activate a
curated set of report-only policies from package templates after explicit
approval. This is different from template extraction, which is a maintainer
workflow for producing reusable package assets.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any

if __package__:
    from . import policy_store, policy_templates, project_state
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import policy_store
    import policy_templates
    import project_state


STARTER_PACK_INIT_PLAN_SCHEMA = "jikuo.starter_policy_pack_init_plan.v0"
STARTER_PACK_INIT_RESULT_SCHEMA = "jikuo.starter_policy_pack_init_result.v0"
STARTER_PACK_MANIFEST_PUBLICATION_PLAN_SCHEMA = (
    "jikuo.starter_pack_manifest_publication_plan.v0"
)
STARTER_PACK_MANIFEST_PUBLICATION_RESULT_SCHEMA = (
    "jikuo.starter_pack_manifest_publication_result.v0"
)
STARTER_PACK_MANIFEST_SCHEMA = "jikuo.starter_policy_pack_manifest.v0"
STARTER_POLICY_PROVENANCE_SCHEMA = "jikuo.policy_provenance.v0"
OFFICIAL_STARTER_POLICY_PROVENANCE_SOURCE = "verified_jikuo_official"
DEFAULT_PACK_ID = "engineering_governance"
PACKAGE_ROOT = Path(__file__).resolve().parent
STARTER_PACKS_ROOT = PACKAGE_ROOT / "starter_policy_packs"
POLICY_TEMPLATES_ROOT = PACKAGE_ROOT / "policy_templates"
STARTER_TEMPLATE_REF_PREFIX = "pkg://jikuo/policy_templates/"
POLICY_STORE_ROOT = policy_store.POLICY_STORE_ROOT
CONTRACT_REFS = [
    "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-22_starter_policy_pack_first_use_initialization.md",
    "pkg://jikuo/governance/jikuo_project_context_binding_and_policy_template_portability.md",
    "pkg://jikuo/governance/jikuo_trust_privacy_provenance_baseline.md",
]
DEFAULT_REGISTRY_TEXT = "\n".join(
    [
        'schema_version: "jikuo.rule_registry.v0"',
        "registry:",
        '  id: "jikuo_project_governance"',
        '  title: "JIKUO project governance registry"',
        "rules: []",
        "",
    ]
)


def quote_yaml(value: Any) -> str:
    return policy_store.quote_yaml(value)


def render_yaml_document(record: dict[str, Any]) -> str:
    return policy_store.render_yaml_document(record)


def stable_id(prefix: str, seed: str) -> str:
    return policy_store.stable_id(prefix, seed)


def display_path(path: Path, project_root: Path) -> str:
    return policy_store.display_path(path, project_root)


def pack_id_boundary_warning(pack_id: str) -> str | None:
    if (
        not pack_id
        or pack_id in {".", ".."}
        or "/" in pack_id
        or "\\" in pack_id
        or Path(pack_id).is_absolute()
        or Path(pack_id).name != pack_id
    ):
        return f"starter_pack_id_must_be_package_local:{pack_id}"
    return None


def pack_manifest_path(pack_id: str) -> Path:
    return STARTER_PACKS_ROOT / pack_id / "manifest.yaml"


def load_pack_manifest(pack_id: str) -> tuple[dict[str, Any] | None, list[str]]:
    boundary_warning = pack_id_boundary_warning(pack_id)
    if boundary_warning:
        return None, [boundary_warning]
    manifest_path = pack_manifest_path(pack_id)
    try:
        manifest_path.resolve().relative_to(STARTER_PACKS_ROOT.resolve())
    except ValueError:
        return None, [f"starter_pack_manifest_boundary_violation:{pack_id}"]
    if not manifest_path.is_file():
        return None, [f"starter pack manifest not found: {manifest_path}"]
    manifest = policy_templates.read_yaml_subset(manifest_path)
    warnings: list[str] = []
    schema = manifest.get("schema_version") or manifest.get("schema")
    if schema != STARTER_PACK_MANIFEST_SCHEMA:
        warnings.append(f"unsupported starter pack manifest schema: {schema}")
    return manifest, warnings


def resolve_template_path(template_ref: str) -> Path:
    if template_ref.startswith("pkg://jikuo/"):
        relative = template_ref[len("pkg://jikuo/") :]
        return PACKAGE_ROOT / relative
    return PACKAGE_ROOT / template_ref


def resolve_official_starter_template_path(template_ref: str) -> tuple[Path | None, str | None]:
    if not template_ref.startswith(STARTER_TEMPLATE_REF_PREFIX):
        return None, f"starter_template_ref_must_be_pkg_policy_template:{template_ref}"

    relative = template_ref[len("pkg://jikuo/") :]
    if "\\" in relative:
        return None, f"starter_template_ref_boundary_violation:{template_ref}"
    relative_path = Path(relative)
    if (
        relative_path.is_absolute()
        or ".." in relative_path.parts
        or ".jikuo" in relative_path.parts
    ):
        return None, f"starter_template_ref_boundary_violation:{template_ref}"

    template_path = PACKAGE_ROOT / relative_path
    try:
        template_path.resolve().relative_to(POLICY_TEMPLATES_ROOT.resolve())
    except ValueError:
        return None, f"starter_template_ref_outside_official_policy_templates:{template_ref}"
    return template_path, None


def load_template_policy(
    template_path: Path,
    *,
    template_ref: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    if not template_path.is_file():
        return None, [f"starter template not found: {template_path}"]
    template = policy_templates.read_yaml_subset(template_path)
    schema = template.get("schema_version") or template.get("schema")
    compatibility = policy_templates.template_compatibility_projection(template)
    if schema != policy_templates.POLICY_TEMPLATE_SCHEMA:
        warnings.append(f"legacy policy template schema: {schema or 'missing'}")
    if compatibility.get("compatibility_status") == "blocked":
        return None, [*warnings, "policy_template_compatibility_blocked"]
    template_policy = template.get("template_policy")
    if not isinstance(template_policy, dict):
        return None, [*warnings, "template_policy_missing"]
    policy = policy_templates.normalized_template_policy_body(template)
    source_refs = policy.get("source_refs")
    if not isinstance(source_refs, list):
        source_refs = []
    policy["source_refs"] = [
        {
            "type": "starter_pack",
            "ref": template.get("template_id"),
        },
        {
            "type": "policy_template_file",
            "ref": template_ref,
        },
        *source_refs,
    ]
    policy["template_ref"] = template_ref
    return policy, warnings


def official_starter_policy_provenance(
    *,
    template_ref: str,
    pack_id: str,
) -> dict[str, Any]:
    return {
        "schema": STARTER_POLICY_PROVENANCE_SCHEMA,
        "source": OFFICIAL_STARTER_POLICY_PROVENANCE_SOURCE,
        "source_ref": template_ref,
        "starter_pack_ref": pack_id,
        "imported_at_utc": None,
        "reviewed_by": {
            "principal_id": "jikuo_package_maintainers",
            "principal_type": "package_maintainer",
        },
        "review_wall_required": False,
        "signed_by": None,
        "verified_at_utc": None,
    }


def load_pack_policies(pack_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    manifest, warnings = load_pack_manifest(pack_id)
    if manifest is None:
        return [], warnings
    raw_templates = manifest.get("policy_templates")
    if not isinstance(raw_templates, list):
        return [], [*warnings, "starter pack policy_templates must be a list"]

    policies: list[dict[str, Any]] = []
    for item in raw_templates:
        if not isinstance(item, dict):
            warnings.append("starter pack template entry must be a mapping")
            continue
        template_ref = item.get("template_ref")
        if not isinstance(template_ref, str) or not template_ref:
            warnings.append("starter pack template entry has no template_ref")
            continue
        template_path, template_warning = resolve_official_starter_template_path(template_ref)
        if template_warning:
            warnings.append(template_warning)
            continue
        assert template_path is not None
        policy, template_warnings = load_template_policy(
            template_path,
            template_ref=template_ref,
        )
        warnings.extend(template_warnings)
        if policy is None:
            continue
        policy["starter_pack_ref"] = pack_id
        policy["provenance"] = official_starter_policy_provenance(
            template_ref=template_ref,
            pack_id=pack_id,
        )
        template_record = policy_templates.read_yaml_subset(template_path)
        template_compatibility = policy_templates.template_compatibility_projection(
            template_record
        )
        policies.append(
            {
                "policy_id": policy.get("policy_id"),
                "title": policy.get("title"),
                "template_ref": item.get("template_ref"),
                "template_path": str(template_path),
                "template_compatibility": template_compatibility,
                "policy": policy,
            }
        )
    return policies, warnings


def existing_manifest_template_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    raw_templates = manifest.get("policy_templates")
    if not isinstance(raw_templates, list):
        return []
    return [item for item in raw_templates if isinstance(item, dict)]


def build_starter_manifest_publication_plan(
    *,
    template_ref: str,
    pack_id: str = DEFAULT_PACK_ID,
) -> dict[str, Any]:
    warnings: list[str] = []
    refusals: list[str] = []
    manifest, manifest_warnings = load_pack_manifest(pack_id)
    warnings.extend(manifest_warnings)
    manifest_path = pack_manifest_path(pack_id)
    if manifest is None:
        manifest = {}
        refusals.extend(manifest_warnings)

    if any(warning.startswith("unsupported starter pack manifest schema:") for warning in warnings):
        refusals.append("starter_pack_schema_not_supported")
    if manifest and not isinstance(manifest.get("policy_templates"), list):
        refusals.append("starter_pack_policy_templates_must_be_list")

    template_path, template_warning = resolve_official_starter_template_path(template_ref)
    if template_warning:
        warnings.append(template_warning)
        refusals.append("starter_pack_template_ref_boundary_violation")

    template: dict[str, Any] = {}
    policy_id: str | None = None
    title: str | None = None
    if template_path is not None:
        if not template_path.is_file():
            warnings.append(f"starter template not found: {template_path}")
            refusals.append("starter_template_not_found")
        else:
            template = policy_templates.read_yaml_subset(template_path)
            schema = template.get("schema_version") or template.get("schema")
            if schema != policy_templates.POLICY_TEMPLATE_SCHEMA:
                warnings.append(f"unsupported policy template schema: {schema}")
                refusals.append("starter_template_schema_not_supported")
            template_policy = template.get("template_policy")
            if not isinstance(template_policy, dict):
                refusals.append("template_policy_missing")
            else:
                raw_policy_id = template_policy.get("policy_id")
                raw_title = template_policy.get("title")
                if isinstance(raw_policy_id, str) and raw_policy_id:
                    policy_id = raw_policy_id
                else:
                    refusals.append("template_policy_id_missing")
                if isinstance(raw_title, str) and raw_title:
                    title = raw_title
                elif policy_id:
                    title = policy_id

    existing_entries = existing_manifest_template_entries(manifest)
    for entry in existing_entries:
        if entry.get("template_ref") == template_ref:
            refusals.append(f"starter_pack_template_ref_already_present:{template_ref}")
        if policy_id and entry.get("policy_id") == policy_id:
            refusals.append(f"starter_pack_policy_id_already_present:{policy_id}")

    status = "refused" if refusals else "review"
    write_set = [
        {
            "path": str(manifest_path),
            "operation": "update",
            "effect": "add reviewed package template ref to starter pack manifest",
        }
    ]
    guarded_command = (
        "python -B -m jikuo.starter_policies publish-template "
        f"--template-ref \"{template_ref}\" "
        f"--pack-id {pack_id} "
        "--confirm-manifest-publication "
        '--approval-phrase "<exact user phrase as spoken>" '
        "--format json"
    )
    return {
        "schema": STARTER_PACK_MANIFEST_PUBLICATION_PLAN_SCHEMA,
        "schema_version": STARTER_PACK_MANIFEST_PUBLICATION_PLAN_SCHEMA,
        "report_only": True,
        "status": status,
        "pack_id": pack_id,
        "manifest_path": str(manifest_path),
        "template_ref": template_ref,
        "template_path": str(template_path) if template_path is not None else None,
        "policy_id": policy_id,
        "title": title,
        "existing_template_count": len(existing_entries),
        "write_set": write_set,
        "approval_required": True,
        "write_allowed_by_command": False,
        "writes_performed": False,
        "guarded_apply_command_preview": guarded_command,
        "refusal_reasons": sorted(set(refusals)),
        "warnings": sorted(set(warnings)),
        "source_refs": [
            *CONTRACT_REFS,
            "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01_policy_management_mvp.md",
            "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-CATALOG-01_self_bootstrap_policy_promotion_review.md",
        ],
        "non_effects": [
            "does not activate policies in user projects",
            "does not create .jikuo/policies/",
            "does not copy .jikuo/policies/approved files into starter packs",
            "does not run starter policy initialization",
        ],
        "next_actions": [
            "review starter-pack manifest target and package template provenance",
            "publish the template ref only after explicit maintainer approval",
            "activate in user projects only through a later guarded starter init",
        ]
        if status == "review"
        else ["resolve refusal reasons before retrying starter manifest publication"],
    }


def build_manifest_publication_refusal_result(
    *,
    plan: dict[str, Any],
    approval_phrase: str | None,
    confirmed: bool,
    refusals: list[str],
) -> dict[str, Any]:
    return {
        "schema": STARTER_PACK_MANIFEST_PUBLICATION_RESULT_SCHEMA,
        "schema_version": STARTER_PACK_MANIFEST_PUBLICATION_RESULT_SCHEMA,
        "status": "refused",
        "write_performed": False,
        "pack_id": plan.get("pack_id"),
        "manifest_path": plan.get("manifest_path"),
        "template_ref": plan.get("template_ref"),
        "policy_id": plan.get("policy_id"),
        "written_paths": [],
        "refusal_reasons": sorted(set(refusals)),
        "warnings": plan.get("warnings") or [],
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": "JIKUO starter pack manifest publication",
            "decision_effect": "add one reviewed package template ref to an official starter pack manifest",
            "decision_noneffect": "does not activate policies in user projects",
            "source_plan_schema": STARTER_PACK_MANIFEST_PUBLICATION_PLAN_SCHEMA,
            "command_confirmed": confirmed,
        }
        if approval_phrase
        else None,
        "non_effects": plan.get("non_effects") or [],
        "next_actions": ["review refusal reasons before retrying starter manifest publication"],
    }


def publish_template_to_starter_manifest(
    *,
    template_ref: str,
    pack_id: str = DEFAULT_PACK_ID,
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_starter_manifest_publication_plan(
        template_ref=template_ref,
        pack_id=pack_id,
    )
    refusals = list(plan.get("refusal_reasons") or [])
    if not confirmed:
        refusals.append("missing_confirmation_flag")
    if not approval_phrase:
        refusals.append("approval_evidence_missing")
    if refusals:
        return (
            build_manifest_publication_refusal_result(
                plan=plan,
                approval_phrase=approval_phrase,
                confirmed=confirmed,
                refusals=refusals,
            ),
            2,
        )

    manifest_path = Path(str(plan["manifest_path"]))
    try:
        manifest = policy_templates.read_yaml_subset(manifest_path)
        entries = existing_manifest_template_entries(manifest)
        entries.append(
            {
                "template_ref": template_ref,
                "policy_id": plan.get("policy_id"),
                "title": plan.get("title"),
            }
        )
        manifest["policy_templates"] = entries
        manifest_path.write_text(
            render_yaml_document(manifest),
            encoding="utf-8",
            newline="\n",
        )
    except Exception as exc:
        return (
            build_manifest_publication_refusal_result(
                plan=plan,
                approval_phrase=approval_phrase,
                confirmed=confirmed,
                refusals=[f"starter_manifest_publication_failed: {exc}"],
            ),
            2,
        )

    policies, warnings = load_pack_policies(pack_id)
    published_policy_ids = {str(item.get("policy_id")) for item in policies}
    return (
        {
            "schema": STARTER_PACK_MANIFEST_PUBLICATION_RESULT_SCHEMA,
            "schema_version": STARTER_PACK_MANIFEST_PUBLICATION_RESULT_SCHEMA,
            "status": "written",
            "write_performed": True,
            "pack_id": pack_id,
            "manifest_path": str(manifest_path),
            "template_ref": template_ref,
            "policy_id": plan.get("policy_id"),
            "title": plan.get("title"),
            "written_paths": [str(manifest_path)],
            "refusal_reasons": [],
            "warnings": sorted(set([*(plan.get("warnings") or []), *warnings])),
            "approval_record": {
                "phrase": approval_phrase,
                "decision_target": "JIKUO starter pack manifest publication",
                "decision_effect": "add one reviewed package template ref to an official starter pack manifest",
                "decision_noneffect": "does not activate policies in user projects",
                "source_plan_schema": STARTER_PACK_MANIFEST_PUBLICATION_PLAN_SCHEMA,
                "command_confirmed": confirmed,
            },
            "post_write_verification": {
                "manifest_written": manifest_path.is_file(),
                "template_ref_present": any(
                    entry.get("template_ref") == template_ref
                    for entry in existing_manifest_template_entries(
                        policy_templates.read_yaml_subset(manifest_path)
                    )
                ),
                "starter_pack_policy_loadable": str(plan.get("policy_id"))
                in published_policy_ids,
            },
            "non_effects": plan.get("non_effects") or [],
            "next_actions": [
                "review starter pack preview before using it in a user project",
                "activate in user projects only through guarded starter init",
            ],
        },
        0,
    )


def policy_file_ref(policy_id: str) -> str:
    return f"{POLICY_STORE_ROOT}/approved/{policy_id}.yaml"


def proposal_ref_for(pack_id: str, policy_id: str) -> str:
    proposal_id = stable_id("POLICYPROPOSAL", f"starter-pack|{pack_id}|{policy_id}")
    return f"{POLICY_STORE_ROOT}/proposals/{proposal_id}.yaml"


def decision_ref_for(pack_id: str, policy_id: str) -> str:
    decision_id = stable_id("POLICYDECISION", f"starter-pack|{pack_id}|{policy_id}")
    return f"{POLICY_STORE_ROOT}/decisions/{decision_id}.yaml"


def build_pack_manifest_record(
    *,
    project_root: Path,
    pack_id: str,
    policies: list[dict[str, Any]],
) -> dict[str, Any]:
    project_id = project_state.derive_project_id(project_root)
    state_file = project_root / ".jikuo" / "project_state.yaml"
    if state_file.is_file():
        try:
            state = policy_store.read_minimal_yaml(state_file)
        except OSError:
            state = {}
        raw_project_id = state.get("project_id")
        if isinstance(raw_project_id, str) and raw_project_id:
            project_id = raw_project_id

    return {
        "schema_version": policy_store.POLICY_STORE_MANIFEST_SCHEMA,
        "project_id": project_id,
        "store_root": POLICY_STORE_ROOT,
        "active_policy_refs": [
            {
                "policy_id": item["policy_id"],
                "version": 1,
                "path": policy_file_ref(str(item["policy_id"])),
            }
            for item in policies
        ],
        "proposal_refs": [
            {
                "proposal_id": Path(proposal_ref_for(pack_id, str(item["policy_id"]))).stem,
                "policy_id": item["policy_id"],
                "path": proposal_ref_for(pack_id, str(item["policy_id"])),
                "status": "approved_for_starter_pack_init",
            }
            for item in policies
        ],
        "deprecated_policy_refs": [],
        "superseded_policy_refs": [],
        "last_updated_at": policy_store.utc_now_iso(),
        "compatibility": {
            "unknown_fields": "preserve",
            "writer": "starter_policy_pack_init",
        },
    }


def build_decision_record(
    *,
    pack_id: str,
    policy_id: str,
    approval_phrase: str,
    plan_id: str,
) -> dict[str, Any]:
    decision_ref = decision_ref_for(pack_id, policy_id)
    return {
        "schema_version": policy_store.POLICY_DECISION_SCHEMA,
        "decision_id": Path(decision_ref).stem,
        "proposal_ref": proposal_ref_for(pack_id, policy_id),
        "policy_ref": policy_id,
        "decision": "approve_starter_pack_policy",
        "target": {
            "kind": "starter_pack_policy",
            "starter_pack_ref": pack_id,
            "ref": policy_id,
        },
        "effect": f"initialize starter policy {policy_id} from pack {pack_id}",
        "non_effect": "does not execute policy actions, persist evidence, promote gates, or enable blocking enforcement",
        "approval_phrase": approval_phrase,
        "created_at": policy_store.utc_now_iso(),
        "source_plan_ref": plan_id,
        "source_plan_schema": STARTER_PACK_INIT_PLAN_SCHEMA,
        "storage": {
            "path": decision_ref,
            "policy_store_ref": POLICY_STORE_ROOT,
        },
    }


def append_pack_refs_to_manifest_text(text: str, *, pack_id: str, policies: list[dict[str, Any]]) -> str:
    updated = text
    for item in policies:
        policy_id = str(item["policy_id"])
        updated = policy_store.append_active_policy_ref_to_manifest_text(
            text=updated,
            policy_id=policy_id,
            policy_path_ref=policy_file_ref(policy_id),
        )
        updated = policy_store.append_proposal_ref_to_manifest_text(
            text=updated,
            policy_id=policy_id,
            proposal_ref=proposal_ref_for(pack_id, policy_id),
        )
    return updated


def build_starter_init_plan(
    *,
    project_root: Path | None = None,
    pack_id: str = DEFAULT_PACK_ID,
) -> dict[str, Any]:
    resolved_root = (project_root or Path.cwd()).expanduser().resolve()
    project_report = project_state.build_bootstrap_report(
        project_root=resolved_root,
        command="status",
        include_would_create=False,
    )
    policy_report = policy_store.inspect_policy_store(project_root=resolved_root)
    policies, warnings = load_pack_policies(pack_id)
    warnings = [*warnings, *policy_report.get("warnings", [])]
    refusals: list[str] = []

    if not policies:
        refusals.append("starter_pack_has_no_policies")
    if project_report["state_status"] not in {"missing", "initialized"}:
        refusals.append("project_state_status_not_supported")
    if policy_report["policy_store_status"] not in {"missing", "initialized", "active"}:
        refusals.append("policy_store_status_not_supported")

    active_ids = {
        str(ref.get("policy_id"))
        for ref in policy_report.get("active_policy_refs", [])
        if ref.get("policy_id") is not None
    }
    for item in policies:
        policy_id = str(item["policy_id"])
        if policy_id in active_ids or (resolved_root / policy_file_ref(policy_id)).exists():
            refusals.append(f"starter_policy_already_active_or_present:{policy_id}")
        for artifact_ref in (
            proposal_ref_for(pack_id, policy_id),
            decision_ref_for(pack_id, policy_id),
        ):
            if (resolved_root / artifact_ref).exists():
                refusals.append(f"starter_policy_artifact_already_present:{artifact_ref}")

    if any(warning.startswith("unsupported ") for warning in warnings):
        refusals.append("starter_pack_schema_not_supported")
    if any(
        warning.startswith("starter_pack_id_must_be_package_local:")
        or warning.startswith("starter_pack_manifest_boundary_violation:")
        or warning.startswith("starter_template_ref_must_be_pkg_policy_template:")
        or warning.startswith("starter_template_ref_boundary_violation:")
        or warning.startswith("starter_template_ref_outside_official_policy_templates:")
        for warning in warnings
    ):
        refusals.append("starter_pack_source_boundary_violation")

    registry_path = resolved_root / project_state.REGISTRY_REF
    would_create_registry = not registry_path.exists()
    would_create_project_state = project_report["state_status"] == "missing"
    plan_id = stable_id("STARTERPACKPLAN", f"{resolved_root}|{pack_id}")
    write_set: list[dict[str, Any]] = []
    if would_create_registry:
        write_set.append(
            {
                "path": project_state.REGISTRY_REF,
                "operation": "create",
                "effect": "create minimal JIKUO governance registry mount",
            }
        )
    if would_create_project_state:
        write_set.append(
            {
                "path": ".jikuo/project_state.yaml",
                "operation": "create",
                "effect": "initialize JIKUO project state",
            }
        )
    for item in policies:
        policy_id = str(item["policy_id"])
        write_set.extend(
            [
                {
                    "path": proposal_ref_for(pack_id, policy_id),
                    "operation": "create",
                    "effect": "create starter policy proposal snapshot",
                },
                {
                    "path": policy_file_ref(policy_id),
                    "operation": "create",
                    "effect": "create approved report-only starter policy",
                },
                {
                    "path": decision_ref_for(pack_id, policy_id),
                    "operation": "create",
                    "effect": "record starter policy approval decision",
                },
            ]
        )
    write_set.append(
        {
            "path": f"{POLICY_STORE_ROOT}/manifest.yaml",
            "operation": "create_or_update",
            "effect": "activate starter policy refs in manifest",
        }
    )

    status = "refused" if refusals else "review"
    return {
        "schema": STARTER_PACK_INIT_PLAN_SCHEMA,
        "schema_version": STARTER_PACK_INIT_PLAN_SCHEMA,
        "report_only": True,
        "plan_id": plan_id,
        "status": status,
        "pack_id": pack_id,
        "project_root": str(resolved_root),
        "project_state_status": project_report["state_status"],
        "policy_store_status": policy_report["policy_store_status"],
        "would_create_registry": would_create_registry,
        "would_create_project_state": would_create_project_state,
        "starter_policies": [
            {
                "policy_id": item["policy_id"],
                "title": item["title"],
                "template_ref": item["template_ref"],
                "provenance": item["policy"].get("provenance"),
                "template_compatibility": item.get("template_compatibility"),
                "compatibility_status": (
                    item.get("template_compatibility") or {}
                ).get("compatibility_status"),
                "migration_available": (
                    item.get("template_compatibility") or {}
                ).get("migration_available"),
            }
            for item in policies
        ],
        "write_set": write_set,
        "approval_required": True,
        "write_allowed_by_command": False,
        "writes_performed": False,
        "refusal_reasons": sorted(set(refusals)),
        "warnings": warnings,
        "source_refs": CONTRACT_REFS,
        "non_effects": [
            "does not execute starter policy actions",
            "does not promote gates or blocking enforcement",
            "does not upload telemetry",
            "does not modify source template files",
        ],
        "next_actions": [
            "review starter policy list, write targets, and non-effects",
            "run guarded starter init only after explicit approval",
        ]
        if status == "review"
        else ["resolve refusal reasons before starter policy initialization"],
    }


def write_file_exclusive(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def build_refusal_result(
    *,
    plan: dict[str, Any],
    approval_phrase: str | None,
    confirmed: bool,
    refusals: list[str],
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": STARTER_PACK_INIT_RESULT_SCHEMA,
        "schema_version": STARTER_PACK_INIT_RESULT_SCHEMA,
        "status": "refused",
        "write_performed": False,
        "plan_id": plan["plan_id"],
        "pack_id": plan["pack_id"],
        "project_root": plan["project_root"],
        "written_paths": [],
        "created_paths": [],
        "refusal_reasons": sorted(set(refusals)),
        "warnings": plan["warnings"],
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": "JIKUO starter policy pack initialization",
            "decision_effect": "initialize project-local JIKUO state and approved report-only starter policies",
            "decision_noneffect": "does not execute policy actions, promote gates, or enable blocking enforcement",
            "source_plan_ref": plan["plan_id"],
            "source_plan_schema": STARTER_PACK_INIT_PLAN_SCHEMA,
            "command_confirmed": confirmed,
        }
        if approval_phrase
        else None,
        "error": error,
        "next_actions": ["review refusal reasons before retrying starter initialization"],
    }


def initialize_starter_pack(
    *,
    project_root: Path | None = None,
    pack_id: str = DEFAULT_PACK_ID,
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_starter_init_plan(project_root=project_root, pack_id=pack_id)
    refusals = list(plan["refusal_reasons"])
    if not confirmed:
        refusals.append("missing_confirmation_flag")
    if not approval_phrase:
        refusals.append("approval_evidence_missing")
    if refusals:
        return (
            build_refusal_result(
                plan=plan,
                approval_phrase=approval_phrase,
                confirmed=confirmed,
                refusals=refusals,
            ),
            2,
        )

    resolved_root = Path(plan["project_root"])
    policies, warnings = load_pack_policies(pack_id)
    written_paths: list[str] = []
    created_paths: list[str] = []
    try:
        registry_path = resolved_root / project_state.REGISTRY_REF
        if plan["would_create_registry"]:
            write_file_exclusive(registry_path, DEFAULT_REGISTRY_TEXT)
            written_paths.append(project_state.REGISTRY_REF)
            created_paths.append(str(Path(project_state.REGISTRY_REF).parent).replace("\\", "/") + "/")

        if plan["would_create_project_state"]:
            state_result, state_exit = project_state.write_initial_project_state(
                project_root=resolved_root,
                approval_phrase=approval_phrase,
                confirmed=True,
            )
            if state_exit != 0 or not state_result.get("write_performed"):
                return (
                    build_refusal_result(
                        plan=plan,
                        approval_phrase=approval_phrase,
                        confirmed=confirmed,
                        refusals=["project_state_initialization_failed"],
                        error=state_result.get("error"),
                    ),
                    2,
                )
            written_paths.extend(state_result.get("created_paths", []))
            created_paths.extend(state_result.get("created_paths", []))

        store_root = resolved_root / POLICY_STORE_ROOT
        approved_root = store_root / "approved"
        decisions_root = store_root / policy_store.DECISIONS_DIR_NAME
        proposals_root = store_root / policy_store.PROPOSALS_DIR_NAME
        for directory, ref in (
            (store_root, POLICY_STORE_ROOT + "/"),
            (approved_root, f"{POLICY_STORE_ROOT}/approved/"),
            (decisions_root, f"{POLICY_STORE_ROOT}/decisions/"),
            (proposals_root, f"{POLICY_STORE_ROOT}/proposals/"),
        ):
            if not directory.exists():
                directory.mkdir(parents=True)
                created_paths.append(ref)

        manifest_path = resolved_root / POLICY_STORE_ROOT / policy_store.MANIFEST_NAME
        for item in policies:
            policy_id = str(item["policy_id"])
            policy_ref = policy_file_ref(policy_id)
            proposal_ref = proposal_ref_for(pack_id, policy_id)
            decision_ref = decision_ref_for(pack_id, policy_id)
            proposal_snapshot = {
                "schema_version": STARTER_PACK_INIT_PLAN_SCHEMA,
                "plan_id": plan["plan_id"],
                "pack_id": pack_id,
                "policy_ref": policy_id,
                "template_ref": item["template_ref"],
                "status": "approved_for_starter_pack_init",
                "non_effects": plan["non_effects"],
            }
            write_file_exclusive(
                resolved_root / proposal_ref,
                render_yaml_document(proposal_snapshot),
            )
            written_paths.append(proposal_ref)
            write_file_exclusive(
                resolved_root / policy_ref,
                render_yaml_document(item["policy"]),
            )
            written_paths.append(policy_ref)
            write_file_exclusive(
                resolved_root / decision_ref,
                render_yaml_document(
                    build_decision_record(
                        pack_id=pack_id,
                        policy_id=policy_id,
                        approval_phrase=approval_phrase,
                        plan_id=plan["plan_id"],
                    )
                ),
            )
            written_paths.append(decision_ref)

        if manifest_path.exists():
            manifest_text = append_pack_refs_to_manifest_text(
                manifest_path.read_text(encoding="utf-8"),
                pack_id=pack_id,
                policies=policies,
            )
        else:
            manifest_text = render_yaml_document(
                build_pack_manifest_record(
                    project_root=resolved_root,
                    pack_id=pack_id,
                    policies=policies,
                )
            )
        manifest_path.write_text(manifest_text, encoding="utf-8", newline="\n")
        written_paths.append(f"{POLICY_STORE_ROOT}/manifest.yaml")
    except Exception as exc:
        return (
            build_refusal_result(
                plan=plan,
                approval_phrase=approval_phrase,
                confirmed=confirmed,
                refusals=["starter_pack_initialization_failed"],
                error=str(exc),
            ),
            2,
        )

    status_after = policy_store.inspect_policy_store(project_root=resolved_root)
    active_ids = {
        str(ref.get("policy_id"))
        for ref in status_after.get("active_policy_refs", [])
        if ref.get("policy_id") is not None
    }
    starter_ids = {str(item["policy_id"]) for item in policies}
    return (
        {
            "schema": STARTER_PACK_INIT_RESULT_SCHEMA,
            "schema_version": STARTER_PACK_INIT_RESULT_SCHEMA,
            "status": "written",
            "write_performed": True,
            "plan_id": plan["plan_id"],
            "pack_id": pack_id,
            "project_root": str(resolved_root),
            "written_paths": written_paths,
            "created_paths": created_paths,
            "refusal_reasons": [],
            "warnings": [*plan["warnings"], *warnings],
            "approval_record": {
                "phrase": approval_phrase,
                "decision_target": "JIKUO starter policy pack initialization",
                "decision_effect": "initialize project-local JIKUO state and approved report-only starter policies",
                "decision_noneffect": "does not execute policy actions, promote gates, or enable blocking enforcement",
                "source_plan_ref": plan["plan_id"],
                "source_plan_schema": STARTER_PACK_INIT_PLAN_SCHEMA,
                "command_confirmed": confirmed,
            },
            "post_write_verification": {
                "policy_store_status": status_after.get("policy_store_status"),
                "starter_policies_active": starter_ids.issubset(active_ids),
            },
            "next_actions": [
                "run policy-store status to confirm starter policies are active",
                "use task-start proposals to let starter policies guide first work",
            ],
        },
        0,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    plan_init = subparsers.add_parser("plan-init")
    plan_init.add_argument("--project-root", type=Path, default=None)
    plan_init.add_argument("--pack-id", default=DEFAULT_PACK_ID)
    plan_init.add_argument("--format", choices=("text", "json"), default="text")

    init = subparsers.add_parser("init")
    init.add_argument("--project-root", type=Path, default=None)
    init.add_argument("--pack-id", default=DEFAULT_PACK_ID)
    init.add_argument("--confirm-starter-init", action="store_true")
    init.add_argument("--approval-phrase", default=None)
    init.add_argument("--format", choices=("text", "json"), default="text")

    plan_publish = subparsers.add_parser("plan-publish-template")
    plan_publish.add_argument("--template-ref", required=True)
    plan_publish.add_argument("--pack-id", default=DEFAULT_PACK_ID)
    plan_publish.add_argument("--format", choices=("text", "json"), default="text")

    publish = subparsers.add_parser("publish-template")
    publish.add_argument("--template-ref", required=True)
    publish.add_argument("--pack-id", default=DEFAULT_PACK_ID)
    publish.add_argument("--confirm-manifest-publication", action="store_true")
    publish.add_argument("--approval-phrase", default=None)
    publish.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def format_text(report: dict[str, Any]) -> str:
    lines = [
        f"Schema: {report.get('schema')}",
        f"Status: {report.get('status')}",
        f"Writes performed: {'yes' if report.get('write_performed') else 'no'}",
        f"Pack: {report.get('pack_id')}",
    ]
    if report.get("starter_policies"):
        lines.append("Starter policies:")
        for item in report["starter_policies"]:
            lines.append(f"- {item.get('policy_id')}: {item.get('title')}")
    if report.get("write_set"):
        lines.append("Write set:")
        for item in report["write_set"]:
            lines.append(f"- {item.get('path')}: {item.get('effect')}")
    if report.get("template_ref"):
        lines.append(f"Template ref: {report.get('template_ref')}")
    if report.get("manifest_path"):
        lines.append(f"Manifest: {report.get('manifest_path')}")
    if report.get("refusal_reasons"):
        lines.append("Refusals:")
        lines.extend(f"- {item}" for item in report["refusal_reasons"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    exit_code = 0
    if args.command == "plan-init":
        report = build_starter_init_plan(
            project_root=args.project_root,
            pack_id=args.pack_id,
        )
        exit_code = 0 if report["status"] != "refused" else 2
    elif args.command == "init":
        report, exit_code = initialize_starter_pack(
            project_root=args.project_root,
            pack_id=args.pack_id,
            confirmed=args.confirm_starter_init,
            approval_phrase=args.approval_phrase,
        )
    elif args.command == "plan-publish-template":
        report = build_starter_manifest_publication_plan(
            template_ref=args.template_ref,
            pack_id=args.pack_id,
        )
        exit_code = 0 if report["status"] != "refused" else 2
    elif args.command == "publish-template":
        report, exit_code = publish_template_to_starter_manifest(
            template_ref=args.template_ref,
            pack_id=args.pack_id,
            confirmed=args.confirm_manifest_publication,
            approval_phrase=args.approval_phrase,
        )
    else:
        parser.print_help()
        return 2

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_text(report))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
