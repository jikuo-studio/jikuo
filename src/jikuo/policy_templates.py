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
POLICY_TEMPLATE_SOURCE_INSPECTION_SCHEMA = "jikuo.policy_template_source_inspection.v0"
DEFAULT_NAMESPACE = "local"
DEFAULT_TEMPLATE_SUBDIR = Path("src") / "jikuo" / "policy_templates" / "engineering_governance"
CONTRACT_REFS = [
    "pkg://jikuo/governance/jikuo_project_context_binding_and_policy_template_portability.md",
    "pkg://jikuo/governance/jikuo_trust_privacy_provenance_baseline.md",
    "pkg://jikuo/work_orders/SPRINT_050_WO-PER-JIKUO-CORE-20_project_context_binding_and_policy_template_portability.md",
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


def normalize_template_policy(policy: dict[str, Any], template_id: str, source_ref: str) -> dict[str, Any]:
    template_policy = deepcopy(policy)
    source_refs = template_policy.get("source_refs")
    if not isinstance(source_refs, list):
        source_refs = []
    template_policy["source_refs"] = [
        {
            "type": "policy_template",
            "ref": template_id,
        },
        {
            "type": "origin_policy",
            "ref": source_ref,
        },
        *source_refs,
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
    source_ref = str(source_policy_path)
    project_refs = detect_project_refs(policy)
    required_bindings = infer_required_bindings(policy)
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
            "ref": source_ref,
            "source_project_ref": source_project_ref,
            "source_policy_id": policy_id,
            "source_sha256": file_sha256(source_policy_path),
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
            source_ref,
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
    project_context_path = resolved_project_root / ".jikuo" / "project_context.yaml"
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
            {
                "binding_id": binding.get("binding_id"),
                "role_ref": binding.get("role_ref"),
                "required": bool(binding.get("required", True)),
                "status": "unresolved",
                "reason": (
                    "project_context resolver is not implemented in this MVP"
                    if project_context_path.exists()
                    else "project_context_missing"
                ),
            }
        )

    template_policy = template.get("template_policy")
    if not isinstance(template_policy, dict):
        template_policy = {}
        if template:
            refusals.append("template_policy_missing")

    resolved_policy_preview = deepcopy(template_policy)
    if resolved_policy_preview:
        resolved_policy_preview["source_refs"] = [
            {
                "type": "policy_template",
                "ref": template.get("template_id"),
            },
            {
                "type": "policy_template_file",
                "ref": str(resolved_template),
            },
        ]

    missing_required_bindings = [
        item
        for item in binding_status
        if item.get("required") and item.get("status") != "resolved"
    ]
    status = "refused" if refusals else ("missing_binding" if missing_required_bindings else "review")
    return {
        "schema": POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
        "schema_version": POLICY_TEMPLATE_IMPORT_PLAN_SCHEMA,
        "report_only": True,
        "status": status,
        "template_path": str(resolved_template),
        "template_ref": template.get("template_id"),
        "project_root": str(resolved_project_root),
        "project_context_ref": ".jikuo/project_context.yaml",
        "project_context_status": "present" if project_context_path.is_file() else "missing",
        "binding_status": binding_status,
        "resolved_policy_preview": resolved_policy_preview,
        "approval_required_for_activation": True,
        "write_allowed_by_command": False,
        "writes_performed": False,
        "refusal_reasons": refusals,
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

    plan_import = subparsers.add_parser("plan-import")
    plan_import.add_argument("--template", type=Path, required=True)
    plan_import.add_argument("--project-root", type=Path, default=None)
    plan_import.add_argument("--format", choices=("text", "json"), default="text")
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
    elif args.command == "plan-import":
        report = build_import_plan(
            template_path=args.template,
            project_root=args.project_root,
        )
        exit_code = 0 if report["status"] != "refused" else 2
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
