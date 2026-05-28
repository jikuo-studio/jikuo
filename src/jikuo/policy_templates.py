"""Policy template extraction and export helpers.

The helpers in this module turn a project-approved policy into a reusable
template proposal. Plan paths are no-write. Export paths are guarded by an
explicit confirmation flag and approval phrase, and they write package template
files rather than activating policies in a project store.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

if __package__:
    from . import policy_store
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import policy_store


POLICY_TEMPLATE_SCHEMA = "jikuo.policy_template.v0"
POLICY_TEMPLATE_EXTRACT_PLAN_SCHEMA = "jikuo.policy_template_extract_plan.v0"
POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA = "jikuo.policy_template_import_plan.v0"
POLICY_TEMPLATE_EXPORT_RESULT_SCHEMA = "jikuo.policy_template_export_result.v0"
POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA = "jikuo.policy_template_activation_result.v0"
POLICY_TEMPLATE_SOURCE_INSPECTION_SCHEMA = "jikuo.policy_template_source_inspection.v0"
POLICY_DISTRIBUTION_REVIEW_SCHEMA = "jikuo.policy_distribution_review.v0"
POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA = "jikuo.policy_distribution_source_resolution.v0"
PROJECT_CONTEXT_SCHEMA = "jikuo.project_context.v0"
RESOLVED_POLICY_SCHEMA = "jikuo.resolved_policy.v0"
PROJECT_CONTEXT_REF = ".jikuo/project_context.yaml"
DEFAULT_NAMESPACE = "local"
DEFAULT_TEMPLATE_SUBDIR = Path("src") / "jikuo" / "policy_templates" / "engineering_governance"
REDACTED_SOURCE_PROJECT_REF = "redacted"
CONTRACT_REFS = [
    "pkg://jikuo/governance/jikuo_project_context_binding_and_policy_template_portability.md",
    "pkg://jikuo/governance/jikuo_trust_privacy_provenance_baseline.md",
    "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-20_project_context_binding_and_policy_template_portability.md",
]
POLICY_DISTRIBUTION_DECISIONS = {
    "dogfood_only",
    "official_starter",
    "optional_template",
    "deferred",
}
POLICY_DISTRIBUTION_CONTRACT_REFS = [
    *CONTRACT_REFS,
    "pkg://jikuo/governance/jikuo_policy_governance_authority.md",
    "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-MGMT-01_policy_management_mvp.md",
    "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-POLICY-CATALOG-01_self_bootstrap_policy_promotion_review.md",
]


def unquote_scalar(value: str) -> Any:
    return policy_store.unquote_scalar(value)


def quote_yaml(value: Any) -> str:
    return policy_store.quote_yaml(value)


def render_yaml_document(record: dict[str, Any]) -> str:
    return policy_store.render_yaml_document(record)


def stable_id(prefix: str, seed: str) -> str:
    return policy_store.stable_id(prefix, seed)


def slug_token(value: str) -> str:
    return policy_store.slug_token(value)


def line_indent(raw_line: str) -> int:
    return len(raw_line) - len(raw_line.lstrip(" "))


def yaml_value_lines(path: Path) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        lines.append((line_indent(raw_line), raw_line.strip()))
    return lines


def parse_yaml_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    current_indent, text = lines[index]
    if current_indent < indent:
        return {}, index
    if text.startswith("-"):
        return parse_yaml_list(lines, index, current_indent)
    return parse_yaml_mapping(lines, index, current_indent)


def parse_yaml_mapping(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        current_indent, text = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            index += 1
            continue
        if text.startswith("-"):
            break
        if ":" not in text:
            index += 1
            continue
        key, value = text.split(":", 1)
        key = key.strip()
        value = value.strip()
        index += 1
        if value:
            result[key] = unquote_scalar(value)
            continue
        if index < len(lines) and lines[index][0] > current_indent:
            child, index = parse_yaml_block(lines, index, lines[index][0])
            result[key] = child
        else:
            result[key] = []
    return result, index


def parse_yaml_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        current_indent, text = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            index += 1
            continue
        if not text.startswith("-"):
            break
        item_text = text[1:].strip()
        index += 1
        if not item_text:
            if index < len(lines) and lines[index][0] > current_indent:
                child, index = parse_yaml_block(lines, index, lines[index][0])
                result.append(child)
            else:
                result.append(None)
            continue
        if ":" in item_text:
            key, value = item_text.split(":", 1)
            item: dict[str, Any] = {key.strip(): unquote_scalar(value.strip())}
            if index < len(lines) and lines[index][0] > current_indent:
                child, index = parse_yaml_mapping(lines, index, lines[index][0])
                if isinstance(child, dict):
                    item.update(child)
            result.append(item)
            continue
        result.append(unquote_scalar(item_text))
    return result, index


def read_yaml_subset(path: Path) -> dict[str, Any]:
    lines = yaml_value_lines(path)
    if not lines:
        return {}
    parsed, _ = parse_yaml_block(lines, 0, lines[0][0])
    return parsed if isinstance(parsed, dict) else {}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def template_id_for_policy(policy_id: str, namespace: str) -> str:
    return f"POLICYTEMPLATE-{slug_token(namespace)}-{slug_token(policy_id)}"


def template_filename(template_id: str) -> str:
    return f"{template_id}.yaml"


def iter_scalar_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(iter_scalar_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(iter_scalar_strings(item))
        return strings
    return []


def looks_like_project_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    if normalized.startswith(("/", "../", "./")):
        return True
    if len(value) >= 3 and value[1] == ":" and value[2] in {"\\", "/"}:
        return True
    project_prefixes = (
        ".jikuo/",
        "docs/",
        "src/",
        "tests/",
        "tools/",
    )
    return normalized.startswith(project_prefixes)


def accepted_portable_ref(value: str) -> bool:
    return value.startswith(("role://", "pkg://", "https://", "http://", "user_policy:"))


def detect_project_refs(policy: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for value in iter_scalar_strings(policy):
        if accepted_portable_ref(value):
            continue
        if looks_like_project_path(value):
            refs.append(value)
    return sorted(set(refs))


def binding_record(binding_id: str, role_ref: str, summary: str) -> dict[str, Any]:
    return {
        "binding_id": binding_id,
        "role_ref": role_ref,
        "required": True,
        "summary": summary,
    }


def infer_required_bindings(policy: dict[str, Any]) -> list[dict[str, Any]]:
    bindings: dict[str, dict[str, Any]] = {}
    text = "\n".join(iter_scalar_strings(policy)).lower()
    if "latest todo map" in text:
        bindings["role://document/latest_todo_map"] = binding_record(
            "BIND-latest-todo-map",
            "role://document/latest_todo_map",
            "Resolve the current project todo map before applying this template.",
        )
    if "previous todo map" in text:
        bindings["role://document/previous_todo_map"] = binding_record(
            "BIND-previous-todo-map",
            "role://document/previous_todo_map",
            "Resolve the previous project todo map when scope-delta evidence is required.",
        )

    for condition in policy.get("conditions") or []:
        if not isinstance(condition, dict):
            continue
        pattern = condition.get("pattern")
        if not isinstance(pattern, str):
            continue
        normalized = pattern.replace("\\", "/")
        if normalized.startswith("docs/work_orders"):
            bindings["role://directory/work_orders"] = binding_record(
                "BIND-work-orders",
                "role://directory/work_orders",
                "Resolve the project work-order directory for path-sensitive policy matching.",
            )
        elif looks_like_project_path(normalized):
            role = f"role://directory/{slug_token(normalized.split('/', 1)[0])}"
            bindings[role] = binding_record(
                f"BIND-{slug_token(role)}",
                role,
                f"Resolve project-local path pattern {normalized}.",
            )
    return list(bindings.values())


def public_source_ref(policy_id: str) -> str:
    return f"redacted://local_project_policy/{slug_token(policy_id)}"


def normalize_template_policy(policy: dict[str, Any], template_id: str) -> dict[str, Any]:
    template_policy = deepcopy(policy)
    template_policy["source_refs"] = [
        {
            "type": "policy_template",
            "ref": template_id,
        },
    ]
    return template_policy


def build_template_record(
    *,
    source_policy_path: Path,
    namespace: str = DEFAULT_NAMESPACE,
    source_project_ref: str | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    if not source_policy_path.is_file():
        return None, [f"source policy does not exist: {source_policy_path}"]

    try:
        policy = read_yaml_subset(source_policy_path)
    except OSError as exc:
        return None, [f"source policy cannot be read: {exc}"]

    schema = policy.get("schema_version") or policy.get("schema")
    if schema != policy_store.POLICY_SCHEMA:
        warnings.append(f"unsupported source policy schema: {schema}")
    policy_id = policy.get("policy_id")
    title = policy.get("title")
    if not isinstance(policy_id, str) or not policy_id:
        warnings.append("source policy has no policy_id")
        policy_id = "POLICY-unresolved"
    if not isinstance(title, str) or not title:
        warnings.append("source policy has no title")
        title = policy_id

    template_id = template_id_for_policy(policy_id, namespace)
    template_policy_preview = normalize_template_policy(policy, template_id)
    project_refs = detect_project_refs(template_policy_preview)
    required_bindings = infer_required_bindings(template_policy_preview)
    portability_status = "portable"
    if project_refs:
        portability_status = "binding_required"
        warnings.append("project-local refs require binding before template import")
    if schema != policy_store.POLICY_SCHEMA:
        portability_status = "review_required"

    template = {
        "schema_version": POLICY_TEMPLATE_SCHEMA,
        "template_id": template_id,
        "namespace": namespace,
        "version": 1,
        "title": title,
        "source": {
            "type": "local_project_policy",
            "ref": public_source_ref(policy_id),
            "source_project_ref": REDACTED_SOURCE_PROJECT_REF,
            "source_policy_id": policy_id,
            "source_sha256": file_sha256(source_policy_path),
            "privacy": {
                "local_path": "redacted",
                "project_identity": "redacted",
                "source_refs": "redacted",
            },
        },
        "portability": {
            "status": portability_status,
            "detected_project_refs": project_refs,
            "warnings": warnings,
        },
        "required_bindings": required_bindings,
        "template_policy": normalize_template_policy(
            policy,
            template_id,
        ),
    }
    return template, warnings


def build_extract_plan(
    *,
    source_policy_path: Path,
    target_dir: Path | None = None,
    namespace: str = DEFAULT_NAMESPACE,
    source_project_ref: str | None = None,
) -> dict[str, Any]:
    resolved_source = source_policy_path.expanduser().resolve()
    template, warnings = build_template_record(
        source_policy_path=resolved_source,
        namespace=namespace,
        source_project_ref=source_project_ref,
    )
    refusals: list[str] = []
    if template is None:
        template = {}
        refusals.extend(warnings)
    elif warnings and any(item.startswith("unsupported source policy schema") for item in warnings):
        refusals.append("unsupported_source_policy_schema")

    resolved_target_dir = (target_dir or DEFAULT_TEMPLATE_SUBDIR).expanduser()
    template_id = template.get("template_id") or "POLICYTEMPLATE-unresolved"
    target_file = resolved_target_dir / template_filename(str(template_id))
    status = "refused" if refusals else "review"
    return {
        "schema": POLICY_TEMPLATE_EXTRACT_PLAN_SCHEMA,
        "schema_version": POLICY_TEMPLATE_EXTRACT_PLAN_SCHEMA,
        "report_only": True,
        "status": status,
        "source_policy_path": str(resolved_source),
        "source_project_ref": source_project_ref,
        "target_template_path": str(target_file),
        "target_template_ref": f"pkg://jikuo/policy_templates/engineering_governance/{template_filename(str(template_id))}",
        "namespace": namespace,
        "proposed_template": template,
        "approval_required_for_export": True,
        "write_allowed_by_command": False,
        "writes_performed": False,
        "refusal_reasons": refusals,
        "warnings": warnings,
        "source_refs": CONTRACT_REFS,
        "non_effects": [
            "does not activate the template as a project policy",
            "does not write .jikuo/policies/",
            "does not create project_context bindings",
            "does not resolve role:// refs",
        ],
        "next_actions": [
            "review the proposed template and provenance fields",
            "export the template only with explicit confirmation and approval",
            "import into a project only through a later guarded binding and policy write flow",
        ]
        if status == "review"
        else ["resolve refusal reasons before exporting a policy template"],
    }


def source_category_for_policy(source_policy_path: Path, policy: dict[str, Any]) -> str:
    normalized_path = source_policy_path.as_posix()
    status = policy.get("status")
    if "/.jikuo/policies/approved/" in normalized_path:
        return "project_local_active"
    if status == "active_report_only":
        return "active_report_only"
    if status in {"candidate", "proposed", "draft"}:
        return "candidate"
    return "unknown"


def source_refs_summary(policy: dict[str, Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for item in policy.get("source_refs") or []:
        if not isinstance(item, dict):
            continue
        summaries.append(
            {
                "type": item.get("type"),
                "ref": item.get("ref"),
            }
        )
    return summaries


def policy_ref_to_approved_path(project_root: Path, policy_ref: str) -> Path:
    filename = policy_ref if policy_ref.endswith(".yaml") else f"{policy_ref}.yaml"
    return project_root / policy_store.POLICY_STORE_ROOT / "approved" / filename


def _query_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]+", text.lower())
    return [token for token in tokens if len(token) >= 2]


def _policy_search_text(policy_path: Path, policy: dict[str, Any]) -> str:
    parts: list[str] = [
        str(policy.get("policy_id") or ""),
        str(policy.get("title") or ""),
        str(policy.get("status") or ""),
        str(policy_path),
    ]
    parts.extend(iter_scalar_strings(policy.get("source_refs") or []))
    parts.extend(iter_scalar_strings(policy.get("required_actions") or []))
    parts.extend(iter_scalar_strings(policy.get("required_evidence") or []))
    parts.extend(iter_scalar_strings(policy.get("applies_to_work_profile") or []))
    return " ".join(parts).lower()


def _policy_query_score(query: str, policy_path: Path, policy: dict[str, Any]) -> int:
    haystack = _policy_search_text(policy_path, policy)
    tokens = _query_tokens(query)
    if not tokens:
        return 0
    score = 0
    policy_id = str(policy.get("policy_id") or "").lower()
    title = str(policy.get("title") or "").lower()
    for token in tokens:
        if token in title:
            score += 6
        if token in policy_id:
            score += 5
        if token in haystack:
            score += 2
    if query.strip().lower() in title or query.strip().lower() in policy_id:
        score += 10
    return score


def active_distribution_policy_candidates(project_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    resolved_root = project_root.expanduser().resolve()
    report = policy_store.inspect_policy_store(project_root=resolved_root)
    candidates: list[dict[str, Any]] = []
    warnings = list(report.get("warnings") or [])
    for ref in report.get("active_policy_refs") or []:
        if not isinstance(ref, dict):
            continue
        raw_path = ref.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            continue
        policy_path = (resolved_root / raw_path).resolve()
        policy = read_yaml_subset(policy_path) if policy_path.is_file() else {}
        candidates.append(
            {
                "policy_id": policy.get("policy_id") or ref.get("policy_id"),
                "title": policy.get("title") or ref.get("title"),
                "status": policy.get("status") or ref.get("status"),
                "path": str(policy_path),
                "source_refs_summary": source_refs_summary(policy),
            }
        )
    return candidates, warnings


def resolve_distribution_source_policy(
    *,
    project_root: Path,
    policy_ref: str | None = None,
    source_policy_path: Path | None = None,
    policy_query: str | None = None,
    max_candidates: int = 5,
) -> dict[str, Any]:
    resolved_root = project_root.expanduser().resolve()
    warnings: list[str] = []
    refusals: list[str] = []
    if source_policy_path is not None:
        resolved_source = source_policy_path.expanduser().resolve()
        return {
            "schema": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "schema_version": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "status": "resolved" if resolved_source.is_file() else "refused",
            "resolution_basis": "explicit_source_policy_path",
            "source_policy_path": str(resolved_source),
            "policy_ref": policy_ref,
            "policy_query": policy_query,
            "candidates": [],
            "refusal_reasons": []
            if resolved_source.is_file()
            else [f"source policy does not exist: {resolved_source}"],
            "warnings": warnings,
            "non_effects": [
                "does not write files",
                "does not activate policy distribution",
            ],
        }

    if policy_ref:
        resolved_source = policy_ref_to_approved_path(resolved_root, policy_ref).resolve()
        return {
            "schema": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "schema_version": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "status": "resolved" if resolved_source.is_file() else "refused",
            "resolution_basis": "explicit_policy_ref",
            "source_policy_path": str(resolved_source),
            "policy_ref": policy_ref,
            "policy_query": policy_query,
            "candidates": [],
            "refusal_reasons": []
            if resolved_source.is_file()
            else [f"policy ref did not resolve to an approved policy: {policy_ref}"],
            "warnings": warnings,
            "non_effects": [
                "does not write files",
                "does not activate policy distribution",
            ],
        }

    candidates, store_warnings = active_distribution_policy_candidates(resolved_root)
    warnings.extend(store_warnings)
    if not policy_query:
        return {
            "schema": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "schema_version": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "status": "needs_policy_selection",
            "resolution_basis": "no_policy_query_supplied",
            "source_policy_path": None,
            "policy_ref": None,
            "policy_query": policy_query,
            "candidates": candidates[:max_candidates],
            "refusal_reasons": ["policy_ref_or_policy_query_required"],
            "warnings": warnings,
            "non_effects": [
                "does not write files",
                "does not activate policy distribution",
            ],
        }

    scored: list[tuple[int, dict[str, Any]]] = []
    for candidate in candidates:
        path = Path(str(candidate.get("path") or ""))
        policy = read_yaml_subset(path) if path.is_file() else {}
        score = _policy_query_score(policy_query, path, policy)
        if score > 0:
            scored.append((score, {**candidate, "match_score": score}))
    scored.sort(key=lambda item: item[0], reverse=True)
    ranked = [item for _, item in scored[:max_candidates]]
    if not ranked:
        refusals.append("policy_query_did_not_match_active_policy")
        return {
            "schema": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "schema_version": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "status": "needs_policy_selection",
            "resolution_basis": "policy_query_no_match",
            "source_policy_path": None,
            "policy_ref": None,
            "policy_query": policy_query,
            "candidates": candidates[:max_candidates],
            "refusal_reasons": refusals,
            "warnings": warnings,
            "non_effects": [
                "does not write files",
                "does not activate policy distribution",
            ],
        }

    top_score = int(ranked[0].get("match_score") or 0)
    tied = [item for item in ranked if int(item.get("match_score") or 0) == top_score]
    if len(tied) > 1:
        return {
            "schema": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "schema_version": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
            "status": "needs_policy_selection",
            "resolution_basis": "policy_query_ambiguous",
            "source_policy_path": None,
            "policy_ref": None,
            "policy_query": policy_query,
            "candidates": ranked,
            "refusal_reasons": ["policy_query_matched_multiple_policies"],
            "warnings": warnings,
            "non_effects": [
                "does not write files",
                "does not activate policy distribution",
            ],
        }

    return {
        "schema": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
        "schema_version": POLICY_DISTRIBUTION_SOURCE_RESOLUTION_SCHEMA,
        "status": "resolved",
        "resolution_basis": "policy_query_unique_match",
        "source_policy_path": ranked[0].get("path"),
        "policy_ref": ranked[0].get("policy_id"),
        "policy_query": policy_query,
        "candidates": ranked,
        "refusal_reasons": [],
        "warnings": warnings,
        "non_effects": [
            "does not write files",
            "does not activate policy distribution",
        ],
    }


def distribution_path_for_decision(
    *,
    decision: str,
    target_template_ref: str | None,
    starter_pack_id: str,
) -> dict[str, Any]:
    if decision == "dogfood_only":
        return {
            "category": "dogfood_only",
            "template_export_required": False,
            "starter_pack_manifest_change_required": False,
            "user_project_activation_allowed": False,
            "path": [
                "record distribution review as dogfood-only",
                "keep policy active only in the source project if still useful",
            ],
        }
    if decision == "official_starter":
        return {
            "category": "official_starter",
            "template_export_required": True,
            "starter_pack_manifest_change_required": True,
            "target_template_ref": target_template_ref,
            "starter_pack_id": starter_pack_id,
            "user_project_activation_allowed": "guarded_starter_init_only",
            "path": [
                "run policy template extraction review",
                "export a package template only after explicit maintainer approval",
                "review starter-pack manifest addition separately",
                "activate in a user project only through guarded starter initialization",
            ],
        }
    if decision == "optional_template":
        return {
            "category": "optional_template",
            "template_export_required": True,
            "starter_pack_manifest_change_required": False,
            "target_template_ref": target_template_ref,
            "user_project_activation_allowed": "guarded_template_activation_only",
            "path": [
                "run policy template extraction review",
                "export a package template only after explicit maintainer approval",
                "offer import through no-write template preview",
                "activate in a user project only through guarded template activation",
            ],
        }
    return {
        "category": "deferred",
        "template_export_required": False,
        "starter_pack_manifest_change_required": False,
        "user_project_activation_allowed": False,
        "path": [
            "record deferred distribution review",
            "revisit after clearer product fit or project evidence exists",
        ],
    }


def build_distribution_review(
    *,
    source_policy_path: Path,
    decision: str,
    target_dir: Path | None = None,
    namespace: str = DEFAULT_NAMESPACE,
    source_project_ref: str | None = None,
    starter_pack_id: str = "engineering_governance",
    rationale: str | None = None,
) -> dict[str, Any]:
    resolved_source = source_policy_path.expanduser().resolve()
    warnings: list[str] = []
    refusals: list[str] = []
    if decision not in POLICY_DISTRIBUTION_DECISIONS:
        refusals.append(f"unsupported_distribution_decision:{decision}")
    if not resolved_source.is_file():
        policy: dict[str, Any] = {}
        refusals.append(f"source policy does not exist: {resolved_source}")
    else:
        policy = read_yaml_subset(resolved_source)

    schema = policy.get("schema_version") or policy.get("schema")
    if policy and schema != policy_store.POLICY_SCHEMA:
        refusals.append(f"unsupported source policy schema: {schema}")
    policy_id = policy.get("policy_id")
    if policy and (not isinstance(policy_id, str) or not policy_id):
        refusals.append("source_policy_id_missing")

    extract_plan: dict[str, Any] | None = None
    target_template_ref: str | None = None
    portability: dict[str, Any] = {}
    required_binding_count = 0
    if policy and decision in {"official_starter", "optional_template"}:
        extract_plan = build_extract_plan(
            source_policy_path=resolved_source,
            target_dir=target_dir,
            namespace=namespace,
            source_project_ref=source_project_ref,
        )
        warnings.extend(extract_plan.get("warnings") or [])
        target_template_ref = extract_plan.get("target_template_ref")
        proposed_template = extract_plan.get("proposed_template")
        if isinstance(proposed_template, dict):
            raw_portability = proposed_template.get("portability")
            portability = raw_portability if isinstance(raw_portability, dict) else {}
            required_bindings = proposed_template.get("required_bindings")
            required_binding_count = len(required_bindings) if isinstance(required_bindings, list) else 0
        if extract_plan.get("status") == "refused":
            refusals.append("policy_template_extraction_not_reviewable")

    status = "refused" if refusals else "review"
    distribution_path = distribution_path_for_decision(
        decision=decision,
        target_template_ref=target_template_ref,
        starter_pack_id=starter_pack_id,
    )
    return {
        "schema": POLICY_DISTRIBUTION_REVIEW_SCHEMA,
        "schema_version": POLICY_DISTRIBUTION_REVIEW_SCHEMA,
        "report_only": True,
        "status": status,
        "source_policy_path": str(resolved_source),
        "source_policy_sha256": file_sha256(resolved_source) if resolved_source.is_file() else None,
        "source_category": source_category_for_policy(resolved_source, policy) if policy else "unknown",
        "source_project_ref": source_project_ref,
        "policy_id": policy_id,
        "title": policy.get("title"),
        "policy_status": policy.get("status"),
        "source_refs_summary": source_refs_summary(policy),
        "distribution_decision": decision,
        "review_rationale": rationale,
        "distribution_path": distribution_path,
        "template_portability": {
            "status": portability.get("status"),
            "detected_project_ref_count": len(portability.get("detected_project_refs") or []),
            "warning_count": len(portability.get("warnings") or []),
            "required_binding_count": required_binding_count,
        }
        if decision in {"official_starter", "optional_template"}
        else None,
        "review_obligations": [
            "decide whether the policy is JIKUO dogfood-only or reusable",
            "preserve provenance and privacy boundaries before publication",
            "do not copy project-local .jikuo/policies/approved files into starter packs",
            "do not activate anything in a user project from this review",
        ],
        "approval_required_for_publication": decision in {"official_starter", "optional_template"},
        "write_allowed_by_command": False,
        "writes_performed": False,
        "refusal_reasons": sorted(set(refusals)),
        "warnings": warnings,
        "source_refs": POLICY_DISTRIBUTION_CONTRACT_REFS,
        "non_effects": [
            "does not export a package template",
            "does not update starter pack manifests",
            "does not create or activate project policies",
            "does not supersede, deprecate, or rewrite the source policy",
        ],
        "next_actions": distribution_path["path"]
        if status == "review"
        else ["resolve refusal reasons before retrying distribution review"],
    }


def build_export_refusal_result(
    *,
    plan: dict[str, Any],
    approval_phrase: str | None,
    confirmed: bool,
    refusals: list[str],
) -> dict[str, Any]:
    return {
        "schema": POLICY_TEMPLATE_EXPORT_RESULT_SCHEMA,
        "schema_version": POLICY_TEMPLATE_EXPORT_RESULT_SCHEMA,
        "status": "refused",
        "write_performed": False,
        "source_policy_path": plan["source_policy_path"],
        "target_template_path": plan["target_template_path"],
        "template_ref": plan["target_template_ref"],
        "created_paths": [],
        "written_paths": [],
        "refusal_reasons": refusals,
        "warnings": plan["warnings"],
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": "JIKUO policy template export",
            "decision_effect": "write one reusable policy template file into the package template directory",
            "decision_noneffect": "does not activate the template in any project policy store",
            "source_plan_schema": POLICY_TEMPLATE_EXTRACT_PLAN_SCHEMA,
            "command_confirmed": confirmed,
        }
        if approval_phrase
        else None,
        "next_actions": ["review refusal reasons before retrying template export"],
    }


def export_template_from_plan(
    *,
    source_policy_path: Path,
    target_dir: Path | None = None,
    namespace: str = DEFAULT_NAMESPACE,
    source_project_ref: str | None = None,
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_extract_plan(
        source_policy_path=source_policy_path,
        target_dir=target_dir,
        namespace=namespace,
        source_project_ref=source_project_ref,
    )
    refusals = list(plan["refusal_reasons"])
    target_path = Path(plan["target_template_path"])
    if not confirmed:
        refusals.append("missing technical confirmation flag")
    if not approval_phrase:
        refusals.append("missing approval phrase evidence")
    if target_path.exists():
        refusals.append("target_template_already_exists")
    if refusals:
        return (
            build_export_refusal_result(
                plan=plan,
                approval_phrase=approval_phrase,
                confirmed=confirmed,
                refusals=refusals,
            ),
            2,
        )

    created_paths: list[str] = []
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        created_paths.append(str(target_path.parent))
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        fd = os.open(target_path, flags)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(render_yaml_document(plan["proposed_template"]))
            handle.flush()
            os.fsync(handle.fileno())
    except Exception as exc:
        return (
            {
                **build_export_refusal_result(
                    plan=plan,
                    approval_phrase=approval_phrase,
                    confirmed=confirmed,
                    refusals=[f"template_export_failed: {exc}"],
                ),
                "warnings": [*plan["warnings"], f"template export failed: {exc}"],
            },
            2,
        )

    result = {
        "schema": POLICY_TEMPLATE_EXPORT_RESULT_SCHEMA,
        "schema_version": POLICY_TEMPLATE_EXPORT_RESULT_SCHEMA,
        "status": "written",
        "write_performed": True,
        "source_policy_path": plan["source_policy_path"],
        "target_template_path": str(target_path),
        "template_ref": plan["target_template_ref"],
        "created_paths": created_paths,
        "written_paths": [str(target_path)],
        "refusal_reasons": [],
        "warnings": plan["warnings"],
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": "JIKUO policy template export",
            "decision_effect": "write one reusable policy template file into the package template directory",
            "decision_noneffect": "does not activate the template in any project policy store",
            "source_plan_schema": POLICY_TEMPLATE_EXTRACT_PLAN_SCHEMA,
            "command_confirmed": confirmed,
        },
        "post_write_verification": {
            "template_written": target_path.is_file(),
            "template_schema": read_yaml_subset(target_path).get("schema_version")
            if target_path.is_file()
            else None,
        },
        "next_actions": [
            "review exported template before importing it into any project",
            "use a later guarded import/bind flow to activate a template as a project policy",
        ],
    }
    return result, 0


def build_import_plan(
    *,
    template_path: Path,
    project_root: Path | None = None,
) -> dict[str, Any]:
    resolved_template = template_path.expanduser().resolve()
    resolved_project_root = (
        project_root.expanduser().resolve() if project_root is not None else Path.cwd().resolve()
    )
    warnings: list[str] = []
    refusals: list[str] = []
    if not resolved_template.is_file():
        refusals.append(f"template does not exist: {resolved_template}")
        template: dict[str, Any] = {}
    else:
        template = read_yaml_subset(resolved_template)

    schema = template.get("schema_version") or template.get("schema")
    if template and schema != POLICY_TEMPLATE_SCHEMA:
        refusals.append(f"unsupported template schema: {schema}")
    context, project_context_status, context_warnings = load_project_context(
        resolved_project_root
    )
    warnings.extend(context_warnings)
    if project_context_status == "refused":
        refusals.append("project_context_not_readable")

    required_bindings = template.get("required_bindings")
    if not isinstance(required_bindings, list):
        required_bindings = []
        if template:
            warnings.append("template required_bindings must be a list")

    binding_status: list[dict[str, Any]] = []
    for binding in required_bindings:
        if not isinstance(binding, dict):
            continue
        binding_status.append(
            resolve_binding(
                binding=binding,
                context=context,
                project_root=resolved_project_root,
            )
        )

    template_policy = template.get("template_policy")
    if not isinstance(template_policy, dict):
        template_policy = {}
        if template:
            refusals.append("template_policy_missing")

    resolved_policy_preview = build_resolved_policy_preview(
        template=template,
        template_path=resolved_template,
        project_root=resolved_project_root,
        binding_status=binding_status,
    )
    policy_id = resolved_policy_preview.get("policy_id")
    if not isinstance(policy_id, str) or not policy_id:
        if template:
            refusals.append("resolved_policy_id_missing")
        policy_id = "POLICY-unresolved"

    policy_report = policy_store.inspect_policy_store(project_root=resolved_project_root)
    warnings.extend(policy_report.get("warnings", []))
    if policy_report["policy_store_status"] not in {"missing", "initialized", "active"}:
        refusals.append("policy_store_status_not_supported_for_template_activation")
    active_ids = {
        str(item.get("policy_id"))
        for item in policy_report.get("active_policy_refs", [])
        if item.get("policy_id") is not None
    }
    policy_path_ref = policy_file_ref(policy_id)
    policy_path = resolved_project_root / policy_path_ref
    template_id = str(template.get("template_id") or "POLICYTEMPLATE-unresolved")
    proposal_ref = activation_proposal_ref(template_id, policy_id)
    decision_ref = activation_decision_ref(template_id, policy_id)
    artifact_refs = [policy_path_ref, proposal_ref, decision_ref]
    if policy_id in active_ids or policy_path.exists():
        refusals.append("resolved_policy_already_active_or_present")
    for ref in artifact_refs[1:]:
        if (resolved_project_root / ref).exists():
            refusals.append(f"template_activation_artifact_already_present:{ref}")

    missing_required_bindings = [
        item
        for item in binding_status
        if item.get("required") and item.get("status") != "resolved"
    ]
    status = "refused" if refusals else ("missing_binding" if missing_required_bindings else "review")
    resolved_policy = {
        "schema": RESOLVED_POLICY_SCHEMA,
        "schema_version": RESOLVED_POLICY_SCHEMA,
        "template_ref": template.get("template_id"),
        "project_context_ref": PROJECT_CONTEXT_REF,
        "status": "resolved" if status == "review" else status,
        "resolved_bindings": binding_status,
        "resolution_trace": {
            "project_root": str(resolved_project_root),
            "rejected_refs": [
                item
                for item in binding_status
                if item.get("status") in {"unsafe_binding", "unsupported_ref"}
            ],
            "warnings": warnings,
        },
        "resolved_policy": resolved_policy_preview,
    }
    write_set = [
        {
            "path": proposal_ref,
            "operation": "create",
            "effect": "create template activation proposal snapshot",
        },
        {
            "path": policy_path_ref,
            "operation": "create",
            "effect": "create approved policy resolved from template",
        },
        {
            "path": decision_ref,
            "operation": "create",
            "effect": "record template activation approval decision",
        },
        {
            "path": f"{policy_store.POLICY_STORE_ROOT}/{policy_store.MANIFEST_NAME}",
            "operation": "create_or_update",
            "effect": "activate resolved policy ref in manifest",
        },
    ]
    return {
        "schema": POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
        "schema_version": POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
        "plan_id": stable_id(
            "POLICYTEMPLATEIMPORT",
            f"{resolved_template}|{resolved_project_root}|{template.get('template_id')}",
        ),
        "report_only": True,
        "status": status,
        "template_path": str(resolved_template),
        "template_ref": template.get("template_id"),
        "project_root": str(resolved_project_root),
        "project_context_ref": PROJECT_CONTEXT_REF,
        "project_context_status": project_context_status,
        "policy_store_status": policy_report["policy_store_status"],
        "binding_status": binding_status,
        "resolved_policy": resolved_policy,
        "resolved_policy_preview": resolved_policy_preview,
        "proposal_ref": proposal_ref,
        "decision_record_ref": decision_ref,
        "write_set": write_set,
        "approval_required_for_activation": True,
        "write_allowed_by_command": False,
        "writes_performed": False,
        "refusal_reasons": sorted(set(refusals)),
        "warnings": warnings,
        "source_refs": CONTRACT_REFS,
        "non_effects": [
            "does not write .jikuo/policies/",
            "does not approve or activate the policy",
            "does not write .jikuo/project_context.yaml",
            "does not resolve missing role bindings in this MVP",
        ],
        "next_actions": [
            "create or review project_context bindings for unresolved roles",
            "run a later guarded template activation flow only after bindings are visible",
        ]
        if status == "missing_binding"
        else [
            "review the resolved policy preview before any guarded policy-store write",
            "run guarded template activation only after explicit approval",
        ],
    }


def inspect_source_dir(source_dir: Path) -> dict[str, Any]:
    resolved_dir = source_dir.expanduser().resolve()
    warnings: list[str] = []
    candidates: list[dict[str, Any]] = []
    if not resolved_dir.is_dir():
        return {
            "schema": POLICY_TEMPLATE_SOURCE_INSPECTION_SCHEMA,
            "schema_version": POLICY_TEMPLATE_SOURCE_INSPECTION_SCHEMA,
            "report_only": True,
            "source_dir": str(resolved_dir),
            "status": "refused",
            "candidate_count": 0,
            "candidates": [],
            "warnings": [f"source dir does not exist: {resolved_dir}"],
            "source_refs": CONTRACT_REFS,
        }

    for path in sorted(resolved_dir.glob("*.yaml")):
        try:
            record = read_yaml_subset(path)
        except OSError as exc:
            warnings.append(f"cannot read {path}: {exc}")
            continue
        schema = record.get("schema_version") or record.get("schema")
        if schema != policy_store.POLICY_SCHEMA:
            continue
        policy_id = record.get("policy_id")
        title = record.get("title")
        template_id = template_id_for_policy(str(policy_id), DEFAULT_NAMESPACE)
        candidates.append(
            {
                "path": str(path),
                "policy_id": policy_id,
                "title": title,
                "template_id": template_id,
                "portability_status": (
                    build_template_record(source_policy_path=path)[0] or {}
                ).get("portability", {}).get("status"),
            }
        )

    return {
        "schema": POLICY_TEMPLATE_SOURCE_INSPECTION_SCHEMA,
        "schema_version": POLICY_TEMPLATE_SOURCE_INSPECTION_SCHEMA,
        "report_only": True,
        "source_dir": str(resolved_dir),
        "status": "review",
        "candidate_count": len(candidates),
        "candidates": candidates,
        "warnings": warnings,
        "source_refs": CONTRACT_REFS,
        "next_actions": [
            "run plan-extract for each candidate before exporting package templates",
        ],
    }


def project_context_path(project_root: Path) -> Path:
    return project_root / PROJECT_CONTEXT_REF


def load_project_context(project_root: Path) -> tuple[dict[str, Any] | None, str, list[str]]:
    path = project_context_path(project_root)
    if not path.exists():
        return None, "missing", []
    if not path.is_file():
        return None, "refused", ["project_context_path_is_not_a_file"]
    context = read_yaml_subset(path)
    schema = context.get("schema_version") or context.get("schema")
    warnings: list[str] = []
    if schema != PROJECT_CONTEXT_SCHEMA:
        warnings.append(f"unsupported project_context schema: {schema}")
        return context, "refused", warnings
    return context, "present", warnings


def template_file_ref(template_path: Path, project_root: Path) -> str:
    resolved_template = template_path.resolve()
    try:
        package_relative = resolved_template.relative_to(Path(__file__).resolve().parent)
        return f"pkg://jikuo/{package_relative.as_posix()}"
    except ValueError:
        pass
    try:
        project_relative = resolved_template.relative_to(project_root.resolve())
        return f"project://{project_relative.as_posix()}"
    except ValueError:
        return f"redacted://local_template_file/{file_sha256(resolved_template)}"


def role_section_and_name(role_ref: str) -> tuple[str | None, str | None]:
    if role_ref.startswith("role://document/"):
        return "document_roles", role_ref[len("role://document/") :]
    if role_ref.startswith("role://directory/"):
        return "directory_roles", role_ref[len("role://directory/") :]
    return None, None


def resolve_bound_project_path(
    *,
    project_root: Path,
    raw_path: str,
    expected_kind: str | None = None,
) -> dict[str, Any]:
    if Path(raw_path).is_absolute():
        return {
            "status": "unsafe_binding",
            "resolved_ref": None,
            "target_exists": False,
            "reason": "absolute paths are not allowed in project_context bindings",
        }
    resolved_path, path_error = policy_store.resolve_project_path(project_root, raw_path)
    if path_error or resolved_path is None:
        return {
            "status": "unsafe_binding",
            "resolved_ref": None,
            "target_exists": False,
            "reason": path_error or "path could not be resolved",
        }
    target_exists = resolved_path.exists()
    resolved_ref = display_project_ref(resolved_path, project_root)
    if expected_kind == "document_roles" and not resolved_path.is_file():
        return {
            "status": "missing_target",
            "resolved_ref": resolved_ref,
            "target_exists": target_exists,
            "reason": "document role target is not an existing file",
        }
    if expected_kind == "directory_roles" and not resolved_path.is_dir():
        return {
            "status": "missing_target",
            "resolved_ref": resolved_ref,
            "target_exists": target_exists,
            "reason": "directory role target is not an existing directory",
        }
    return {
        "status": "resolved",
        "resolved_ref": resolved_ref,
        "target_exists": target_exists,
        "reason": "binding resolved inside project root",
    }


def display_project_ref(path: Path, project_root: Path) -> str:
    return policy_store.display_path(path, project_root)


def resolve_pkg_ref(ref: str) -> dict[str, Any]:
    if not ref.startswith("pkg://jikuo/"):
        return {
            "status": "unsupported_ref",
            "resolved_ref": None,
            "target_exists": False,
            "reason": "unsupported package ref",
        }
    relative = ref[len("pkg://jikuo/") :]
    package_path = Path(__file__).resolve().parent / relative
    return {
        "status": "resolved" if package_path.exists() else "missing_target",
        "resolved_ref": ref,
        "target_exists": package_path.exists(),
        "reason": (
            "package ref resolved inside JIKUO package"
            if package_path.exists()
            else "package ref target is missing"
        ),
    }


def resolve_binding(
    *,
    binding: dict[str, Any],
    context: dict[str, Any] | None,
    project_root: Path,
) -> dict[str, Any]:
    role_ref = binding.get("role_ref")
    required = bool(binding.get("required", True))
    base = {
        "binding_id": binding.get("binding_id"),
        "role_ref": role_ref,
        "required": required,
        "summary": binding.get("summary"),
        "resolved_ref": None,
        "target_exists": False,
    }
    if not isinstance(role_ref, str) or not role_ref:
        return {**base, "status": "missing_binding", "reason": "binding has no role_ref"}
    if role_ref.startswith("pkg://"):
        return {**base, **resolve_pkg_ref(role_ref)}
    if role_ref.startswith("project://"):
        resolution = resolve_bound_project_path(
            project_root=project_root,
            raw_path=role_ref[len("project://") :],
        )
        return {**base, **resolution}

    section, role_name = role_section_and_name(role_ref)
    if section is None or role_name is None:
        return {**base, "status": "unsupported_ref", "reason": "unsupported role ref"}
    if context is None:
        return {**base, "status": "missing_binding", "reason": "project_context_missing"}
    role_map = context.get(section)
    if not isinstance(role_map, dict):
        return {
            **base,
            "status": "missing_binding",
            "reason": f"project_context has no {section}",
        }
    entry = role_map.get(role_name)
    if isinstance(entry, dict):
        raw_path = entry.get("path")
    else:
        raw_path = entry
    if not isinstance(raw_path, str) or not raw_path:
        return {
            **base,
            "status": "missing_binding",
            "reason": f"project_context has no path for {role_ref}",
        }
    resolution = resolve_bound_project_path(
        project_root=project_root,
        raw_path=raw_path,
        expected_kind=section,
    )
    return {**base, **resolution}


def replace_exact_refs(value: Any, resolution_map: dict[str, str]) -> Any:
    if isinstance(value, str):
        return resolution_map.get(value, value)
    if isinstance(value, list):
        return [replace_exact_refs(item, resolution_map) for item in value]
    if isinstance(value, dict):
        return {
            key: replace_exact_refs(item, resolution_map)
            for key, item in value.items()
        }
    return value


def build_resolved_policy_preview(
    *,
    template: dict[str, Any],
    template_path: Path,
    project_root: Path,
    binding_status: list[dict[str, Any]],
) -> dict[str, Any]:
    template_policy = template.get("template_policy")
    if not isinstance(template_policy, dict):
        return {}
    resolution_map = {
        str(item["role_ref"]): str(item["resolved_ref"])
        for item in binding_status
        if item.get("status") == "resolved"
        and item.get("role_ref")
        and item.get("resolved_ref")
    }
    policy = replace_exact_refs(deepcopy(template_policy), resolution_map)
    source_refs = policy.get("source_refs")
    if not isinstance(source_refs, list):
        source_refs = []
    template_ref = template.get("template_id")
    policy["source_refs"] = [
        {
            "type": "policy_template",
            "ref": template_ref,
        },
        {
            "type": "policy_template_file",
            "ref": template_file_ref(template_path, project_root),
        },
        {
            "type": "project_context",
            "ref": PROJECT_CONTEXT_REF,
        },
        *source_refs,
    ]
    policy["template_ref"] = template_ref
    policy["project_context_ref"] = PROJECT_CONTEXT_REF
    policy["resolved_bindings"] = [
        {
            "role_ref": item.get("role_ref"),
            "resolved_ref": item.get("resolved_ref"),
            "resolution_status": item.get("status"),
        }
        for item in binding_status
    ]
    return policy


def policy_file_ref(policy_id: str) -> str:
    return f"{policy_store.POLICY_STORE_ROOT}/approved/{policy_id}.yaml"


def activation_proposal_ref(template_id: str, policy_id: str) -> str:
    proposal_id = stable_id("POLICYPROPOSAL", f"template-activation|{template_id}|{policy_id}")
    return f"{policy_store.POLICY_STORE_ROOT}/proposals/{proposal_id}.yaml"


def activation_decision_ref(template_id: str, policy_id: str) -> str:
    decision_id = stable_id("POLICYDECISION", f"template-activation|{template_id}|{policy_id}")
    return f"{policy_store.POLICY_STORE_ROOT}/{policy_store.DECISIONS_DIR_NAME}/{decision_id}.yaml"


def build_activation_decision_record(
    *,
    template_id: str,
    policy_id: str,
    proposal_ref: str,
    decision_ref: str,
    approval_phrase: str,
    plan_id: str,
) -> dict[str, Any]:
    return {
        "schema_version": policy_store.POLICY_DECISION_SCHEMA,
        "decision_id": Path(decision_ref).stem,
        "proposal_ref": proposal_ref,
        "policy_ref": policy_id,
        "decision": "approve_policy_template_activation",
        "target": {
            "kind": "policy_template_activation",
            "template_ref": template_id,
            "ref": policy_id,
        },
        "effect": f"activate template {template_id} as approved policy {policy_id}",
        "non_effect": "does not execute policy actions, persist evidence, promote gates, or modify package templates",
        "approval_phrase": approval_phrase,
        "created_at": policy_store.utc_now_iso(),
        "source_plan_ref": plan_id,
        "source_plan_schema": POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
        "storage": {
            "path": decision_ref,
            "policy_store_ref": policy_store.POLICY_STORE_ROOT,
        },
    }


def write_file_exclusive(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def build_activation_refusal_result(
    *,
    plan: dict[str, Any],
    approval_phrase: str | None,
    confirmed: bool,
    refusals: list[str],
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA,
        "schema_version": POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA,
        "status": "refused",
        "write_performed": False,
        "plan_id": plan.get("plan_id"),
        "template_ref": plan.get("template_ref"),
        "policy_ref": (plan.get("resolved_policy_preview") or {}).get("policy_id"),
        "project_root": plan.get("project_root"),
        "written_paths": [],
        "created_paths": [],
        "refusal_reasons": sorted(set(refusals)),
        "warnings": plan.get("warnings", []),
        "approval_record": {
            "phrase": approval_phrase,
            "decision_target": "JIKUO policy template activation",
            "decision_effect": "activate one resolved template as an approved report-only project policy",
            "decision_noneffect": "does not execute policy actions, promote gates, or modify package templates",
            "source_plan_ref": plan.get("plan_id"),
            "source_plan_schema": POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
            "command_confirmed": confirmed,
        }
        if approval_phrase
        else None,
        "error": error,
        "next_actions": ["review refusal reasons before retrying template activation"],
    }


def activate_template_from_plan(
    *,
    template_path: Path,
    project_root: Path | None = None,
    confirmed: bool = False,
    approval_phrase: str | None = None,
) -> tuple[dict[str, Any], int]:
    plan = build_import_plan(template_path=template_path, project_root=project_root)
    refusals = list(plan["refusal_reasons"])
    if plan["status"] != "review":
        refusals.append("template_import_plan_not_resolved")
    if not confirmed:
        refusals.append("missing_confirmation_flag")
    if not approval_phrase:
        refusals.append("approval_evidence_missing")
    if refusals:
        return (
            build_activation_refusal_result(
                plan=plan,
                approval_phrase=approval_phrase,
                confirmed=confirmed,
                refusals=refusals,
            ),
            2,
        )

    resolved_root = Path(plan["project_root"])
    resolved_policy = plan["resolved_policy_preview"]
    policy_id = str(resolved_policy["policy_id"])
    template_id = str(plan["template_ref"])
    proposal_ref = str(plan["proposal_ref"])
    decision_ref = str(plan["decision_record_ref"])
    policy_ref = policy_file_ref(policy_id)
    manifest_ref = f"{policy_store.POLICY_STORE_ROOT}/{policy_store.MANIFEST_NAME}"
    written_paths: list[str] = []
    created_paths: list[str] = []

    try:
        store_root = resolved_root / policy_store.POLICY_STORE_ROOT
        for directory_ref in (
            policy_store.POLICY_STORE_ROOT,
            f"{policy_store.POLICY_STORE_ROOT}/approved",
            f"{policy_store.POLICY_STORE_ROOT}/{policy_store.PROPOSALS_DIR_NAME}",
            f"{policy_store.POLICY_STORE_ROOT}/{policy_store.DECISIONS_DIR_NAME}",
        ):
            directory = resolved_root / directory_ref
            if not directory.exists():
                directory.mkdir(parents=True)
                created_paths.append(f"{directory_ref}/")

        proposal_snapshot = {
            "schema_version": POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
            "plan_id": plan["plan_id"],
            "template_ref": template_id,
            "policy_ref": policy_id,
            "project_context_ref": PROJECT_CONTEXT_REF,
            "status": "approved_for_template_activation",
            "resolved_bindings": plan["binding_status"],
            "non_effects": plan["non_effects"],
        }
        write_file_exclusive(
            resolved_root / proposal_ref,
            render_yaml_document(proposal_snapshot),
        )
        written_paths.append(proposal_ref)
        write_file_exclusive(
            resolved_root / policy_ref,
            render_yaml_document(resolved_policy),
        )
        written_paths.append(policy_ref)
        write_file_exclusive(
            resolved_root / decision_ref,
            render_yaml_document(
                build_activation_decision_record(
                    template_id=template_id,
                    policy_id=policy_id,
                    proposal_ref=proposal_ref,
                    decision_ref=decision_ref,
                    approval_phrase=approval_phrase,
                    plan_id=plan["plan_id"],
                )
            ),
        )
        written_paths.append(decision_ref)

        manifest_path = resolved_root / manifest_ref
        if manifest_path.exists():
            manifest_text = policy_store.append_active_policy_ref_to_manifest_text(
                text=manifest_path.read_text(encoding="utf-8"),
                policy_id=policy_id,
                policy_path_ref=policy_ref,
            )
            manifest_text = policy_store.append_proposal_ref_to_manifest_text(
                text=manifest_text,
                policy_id=policy_id,
                proposal_ref=proposal_ref,
            )
        else:
            manifest_text = render_yaml_document(
                policy_store.build_policy_manifest_record(
                    project_root=resolved_root,
                    policy_id=policy_id,
                    policy_path_ref=policy_ref,
                    proposal_ref=proposal_ref,
                )
            )
        manifest_path.write_text(manifest_text, encoding="utf-8", newline="\n")
        written_paths.append(manifest_ref)
    except Exception as exc:
        return (
            build_activation_refusal_result(
                plan=plan,
                approval_phrase=approval_phrase,
                confirmed=confirmed,
                refusals=["template_activation_failed"],
                error=str(exc),
            ),
            2,
        )

    status_after = policy_store.inspect_policy_store(project_root=resolved_root)
    active_ids = {
        str(item.get("policy_id"))
        for item in status_after.get("active_policy_refs", [])
        if item.get("policy_id") is not None
    }
    return (
        {
            "schema": POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA,
            "schema_version": POLICY_TEMPLATE_ACTIVATION_RESULT_SCHEMA,
            "status": "written",
            "write_performed": True,
            "plan_id": plan["plan_id"],
            "template_ref": template_id,
            "policy_ref": policy_id,
            "project_root": str(resolved_root),
            "proposal_ref": proposal_ref,
            "decision_record_ref": decision_ref,
            "written_paths": written_paths,
            "created_paths": created_paths,
            "refusal_reasons": [],
            "warnings": plan["warnings"],
            "approval_record": {
                "phrase": approval_phrase,
                "decision_target": "JIKUO policy template activation",
                "decision_effect": "activate one resolved template as an approved report-only project policy",
                "decision_noneffect": "does not execute policy actions, promote gates, or modify package templates",
                "source_plan_ref": plan["plan_id"],
                "source_plan_schema": POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
                "command_confirmed": confirmed,
            },
            "post_write_verification": {
                "policy_store_status": status_after.get("policy_store_status"),
                "policy_active": policy_id in active_ids,
                "proposal_snapshot_written": (resolved_root / proposal_ref).is_file(),
                "decision_record_written": (resolved_root / decision_ref).is_file(),
            },
            "next_actions": [
                "run policy-store status to confirm the activated template policy is active",
                "use task-start proposals to inspect the activated policy trigger behavior",
            ],
        },
        0,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    inspect_source = subparsers.add_parser("inspect-source")
    inspect_source.add_argument("--source-dir", type=Path, required=True)
    inspect_source.add_argument("--format", choices=("text", "json"), default="text")

    plan_extract = subparsers.add_parser("plan-extract")
    plan_extract.add_argument("--source-policy", type=Path, required=True)
    plan_extract.add_argument("--target-dir", type=Path, default=None)
    plan_extract.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    plan_extract.add_argument("--source-project-ref", default=None)
    plan_extract.add_argument("--format", choices=("text", "json"), default="text")

    export_template = subparsers.add_parser("export-template")
    export_template.add_argument("--source-policy", type=Path, required=True)
    export_template.add_argument("--target-dir", type=Path, default=None)
    export_template.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    export_template.add_argument("--source-project-ref", default=None)
    export_template.add_argument("--confirm-export-template", action="store_true")
    export_template.add_argument("--approval-phrase", default=None)
    export_template.add_argument("--format", choices=("text", "json"), default="text")

    review_distribution = subparsers.add_parser("review-distribution")
    review_distribution.add_argument("--source-policy", type=Path, required=True)
    review_distribution.add_argument(
        "--decision",
        choices=sorted(POLICY_DISTRIBUTION_DECISIONS),
        required=True,
    )
    review_distribution.add_argument("--target-dir", type=Path, default=None)
    review_distribution.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    review_distribution.add_argument("--source-project-ref", default=None)
    review_distribution.add_argument("--starter-pack-id", default="engineering_governance")
    review_distribution.add_argument("--rationale", default=None)
    review_distribution.add_argument("--format", choices=("text", "json"), default="text")

    plan_import = subparsers.add_parser("plan-import")
    plan_import.add_argument("--template", type=Path, required=True)
    plan_import.add_argument("--project-root", type=Path, default=None)
    plan_import.add_argument("--format", choices=("text", "json"), default="text")

    activate_template = subparsers.add_parser("activate-template")
    activate_template.add_argument("--template", type=Path, required=True)
    activate_template.add_argument("--project-root", type=Path, default=None)
    activate_template.add_argument("--confirm-activate-template", action="store_true")
    activate_template.add_argument("--approval-phrase", default=None)
    activate_template.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def format_text(report: dict[str, Any]) -> str:
    lines = [
        f"Schema: {report.get('schema')}",
        f"Status: {report.get('status')}",
        f"Writes performed: {'yes' if report.get('write_performed') else 'no'}",
    ]
    if report.get("candidate_count") is not None:
        lines.append(f"Candidate count: {report['candidate_count']}")
        for candidate in report.get("candidates", []):
            lines.append(f"- {candidate.get('policy_id')}: {candidate.get('title')}")
    if report.get("target_template_path"):
        lines.append(f"Target template: {report['target_template_path']}")
    if report.get("template_ref"):
        lines.append(f"Template ref: {report['template_ref']}")
    if report.get("distribution_decision"):
        lines.append(f"Distribution decision: {report['distribution_decision']}")
    if report.get("distribution_path"):
        path = report["distribution_path"]
        lines.append(f"Distribution category: {path.get('category')}")
        if path.get("target_template_ref"):
            lines.append(f"Target template ref: {path.get('target_template_ref')}")
    if report.get("binding_status"):
        lines.append("Bindings:")
        for binding in report["binding_status"]:
            lines.append(
                f"- {binding.get('role_ref')}: {binding.get('status')} ({binding.get('reason')})"
            )
    if report.get("refusal_reasons"):
        lines.append("Refusals:")
        lines.extend(f"- {item}" for item in report["refusal_reasons"])
    if report.get("warnings"):
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in report["warnings"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    exit_code = 0
    if args.command == "inspect-source":
        report = inspect_source_dir(args.source_dir)
    elif args.command == "plan-extract":
        report = build_extract_plan(
            source_policy_path=args.source_policy,
            target_dir=args.target_dir,
            namespace=args.namespace,
            source_project_ref=args.source_project_ref,
        )
        exit_code = 0 if report["status"] != "refused" else 2
    elif args.command == "export-template":
        report, exit_code = export_template_from_plan(
            source_policy_path=args.source_policy,
            target_dir=args.target_dir,
            namespace=args.namespace,
            source_project_ref=args.source_project_ref,
            confirmed=args.confirm_export_template,
            approval_phrase=args.approval_phrase,
        )
    elif args.command == "review-distribution":
        report = build_distribution_review(
            source_policy_path=args.source_policy,
            decision=args.decision,
            target_dir=args.target_dir,
            namespace=args.namespace,
            source_project_ref=args.source_project_ref,
            starter_pack_id=args.starter_pack_id,
            rationale=args.rationale,
        )
        exit_code = 0 if report["status"] != "refused" else 2
    elif args.command == "plan-import":
        report = build_import_plan(
            template_path=args.template,
            project_root=args.project_root,
        )
        exit_code = 0 if report["status"] != "refused" else 2
    elif args.command == "activate-template":
        report, exit_code = activate_template_from_plan(
            template_path=args.template,
            project_root=args.project_root,
            confirmed=args.confirm_activate_template,
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
