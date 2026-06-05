"""Private local turn-input index for linking prompts to execution evidence.

This module may store raw user input, but only under the project-local private
area and only when explicitly confirmed. Public proposal/runtime outputs should
use the redacted refs produced by ``public_record_ref`` or ``build_index_ref``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

if __package__:
    from . import execution_envelope, project_state, turn_anchor as turn_anchor_model
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import execution_envelope
    import project_state
    import turn_anchor as turn_anchor_model


PRIVATE_TURN_INPUT_INDEX_SCHEMA = "jikuo.private_turn_input_index.v0"
PRIVATE_TURN_INPUT_RECORD_SCHEMA = "jikuo.private_turn_input_record.v0"
PRIVATE_TURN_INPUT_INDEX_REF_SCHEMA = "jikuo.private_turn_input_index_ref.v0"
PRIVATE_DIR_REF = ".jikuo/private"
INDEX_REF = ".jikuo/private/turn_inputs.jsonl"
PRIVATE_GITIGNORE = "*\n!.gitignore\n"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _stable_text_bytes(value: str) -> bytes:
    return value.encode("utf-8", errors="surrogatepass")


def digest_text(value: str) -> str:
    return hashlib.sha256(_stable_text_bytes(value)).hexdigest()


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        text = _string_or_none(item)
        if text and text not in output:
            output.append(text)
    return output


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
    except ValueError:
        return False
    return True


def resolve_project_root(project_root: Path | str | None) -> Path:
    if project_root is not None:
        return Path(str(project_root)).resolve()
    return project_state.discover_project_root(project_root=None).resolve()


def private_root_for(project_root: Path | str | None) -> Path:
    root = resolve_project_root(project_root)
    private_root = (root / ".jikuo" / "private").resolve()
    if not is_relative_to(private_root, root):
        raise ValueError("private turn input root escaped project root")
    return private_root


def index_path_for(project_root: Path | str | None) -> Path:
    index_path = private_root_for(project_root) / "turn_inputs.jsonl"
    if not is_relative_to(index_path.resolve(), private_root_for(project_root)):
        raise ValueError("private turn input index escaped private root")
    return index_path


def record_id_for(
    *,
    project_root: Path | str | None,
    raw_user_input: str | None,
    turn_anchor: dict[str, Any],
) -> str:
    prompt_sha256 = (
        _string_or_none(turn_anchor.get("prompt_sha256"))
        or (digest_text(raw_user_input) if raw_user_input else None)
    )
    return execution_envelope.stable_id(
        "input",
        [
            str(resolve_project_root(project_root)),
            _string_or_none(turn_anchor.get("anchor_id")),
            _string_or_none(turn_anchor.get("session_id")),
            _string_or_none(turn_anchor.get("turn_id")),
            prompt_sha256,
        ],
    )


def build_index_ref(
    *,
    project_root: Path | str | None,
    turn_anchor: dict[str, Any] | None,
    raw_input_present: bool,
    record_id: str | None = None,
    prompt_sha256: str | None = None,
    write_performed: bool = False,
) -> dict[str, Any]:
    anchor = turn_anchor_model.normalize_turn_anchor(turn_anchor)
    root = resolve_project_root(project_root)
    digest = prompt_sha256 or _string_or_none(anchor.get("prompt_sha256"))
    if not raw_input_present:
        status = "no_raw_input_available"
    elif record_id or anchor.get("status") == "available" or digest:
        status = "available_for_private_storage"
    else:
        status = "insufficient_turn_identity"
    return {
        "schema": PRIVATE_TURN_INPUT_INDEX_REF_SCHEMA,
        "status": status,
        "project_root": str(root),
        "index_ref": INDEX_REF,
        "record_id": record_id,
        "turn_anchor_id": anchor.get("anchor_id"),
        "session_id": anchor.get("session_id"),
        "turn_id": anchor.get("turn_id"),
        "prompt_sha256": digest,
        "write_performed": write_performed,
        "privacy": {
            "storage_scope": "project_private_local",
            "raw_prompt_persisted": write_performed,
            "raw_prompt_exposed_in_audit": False,
            "raw_transcript_exposed_in_audit": False,
        },
        "non_effects": [
            "does_not_call_llm_provider",
            "does_not_infer_semantic_intent",
            "does_not_expose_raw_prompt_in_public_cards",
        ],
    }


def _compact_semantic_ref(raw: dict[str, Any] | None) -> dict[str, Any]:
    return execution_envelope.compact_host_semantic_intent_ref(raw)


def build_record(
    *,
    project_root: Path | str | None,
    raw_user_input: str,
    turn_anchor: dict[str, Any] | None,
    host_semantic_intent: dict[str, Any] | None = None,
    source_client: str | None = None,
    source_event: str | None = None,
    runtime_refs: list[str] | None = None,
    task_start_refs: list[str] | None = None,
    completion_review_refs: list[str] | None = None,
    receipt_refs: list[str] | None = None,
    git_baseline_ref: str | None = None,
    git_final_ref: str | None = None,
    received_at_utc: str | None = None,
) -> dict[str, Any]:
    raw_text = _string_or_none(raw_user_input)
    if raw_text is None:
        raise ValueError("raw_user_input is required for private index records")
    root = resolve_project_root(project_root)
    anchor = turn_anchor_model.normalize_turn_anchor(turn_anchor)
    raw_digest = digest_text(raw_text)
    prompt_sha256 = _string_or_none(anchor.get("prompt_sha256")) or raw_digest
    record_id = record_id_for(
        project_root=root,
        raw_user_input=raw_text,
        turn_anchor={**anchor, "prompt_sha256": prompt_sha256},
    )
    return {
        "schema": PRIVATE_TURN_INPUT_RECORD_SCHEMA,
        "record_id": record_id,
        "project_root": str(root),
        "source_client": _string_or_none(source_client),
        "source_event": _string_or_none(source_event),
        "received_at_utc": _string_or_none(received_at_utc) or utc_now_iso(),
        "raw_user_input": raw_text,
        "raw_input_sha256": raw_digest,
        "prompt_sha256": prompt_sha256,
        "turn_anchor": anchor,
        "host_semantic_intent_ref": _compact_semantic_ref(host_semantic_intent),
        "execution_evidence_refs": {
            "runtime_refs": _string_list(runtime_refs),
            "task_start_refs": _string_list(task_start_refs),
            "completion_review_refs": _string_list(completion_review_refs),
            "receipt_refs": _string_list(receipt_refs),
        },
        "git_observation_refs": {
            "baseline_ref": _string_or_none(git_baseline_ref),
            "final_ref": _string_or_none(git_final_ref),
        },
        "privacy": {
            "storage_scope": "project_private_local",
            "raw_prompt_persisted": True,
            "raw_prompt_exposed_in_audit": False,
            "raw_transcript_exposed_in_audit": False,
        },
    }


def public_record_ref(record: dict[str, Any]) -> dict[str, Any]:
    anchor = turn_anchor_model.normalize_turn_anchor(record.get("turn_anchor"))
    return build_index_ref(
        project_root=record.get("project_root"),
        turn_anchor=anchor,
        raw_input_present=True,
        record_id=_string_or_none(record.get("record_id")),
        prompt_sha256=_string_or_none(record.get("prompt_sha256")),
        write_performed=bool((record.get("privacy") or {}).get("raw_prompt_persisted")),
    ) | {
        "received_at_utc": _string_or_none(record.get("received_at_utc")),
        "host_semantic_intent_ref": record.get("host_semantic_intent_ref") or {},
        "execution_evidence_refs": record.get("execution_evidence_refs") or {},
        "git_observation_refs": record.get("git_observation_refs") or {},
    }


def ensure_private_store(project_root: Path | str | None) -> Path:
    private_root = private_root_for(project_root)
    private_root.mkdir(parents=True, exist_ok=True)
    gitignore = private_root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(PRIVATE_GITIGNORE, encoding="utf-8", newline="\n")
    return private_root


def append_turn_input_record(
    *,
    project_root: Path | str | None,
    raw_user_input: str,
    turn_anchor: dict[str, Any] | None,
    host_semantic_intent: dict[str, Any] | None = None,
    source_client: str | None = None,
    source_event: str | None = None,
    runtime_refs: list[str] | None = None,
    task_start_refs: list[str] | None = None,
    completion_review_refs: list[str] | None = None,
    receipt_refs: list[str] | None = None,
    git_baseline_ref: str | None = None,
    git_final_ref: str | None = None,
    confirm_store_raw_input: bool = False,
    approval_phrase: str | None = None,
) -> dict[str, Any]:
    if not confirm_store_raw_input or not _string_or_none(approval_phrase):
        anchor = turn_anchor_model.normalize_turn_anchor(turn_anchor)
        return {
            "schema": PRIVATE_TURN_INPUT_INDEX_SCHEMA,
            "status": "refused",
            "write_performed": False,
            "private_turn_input_ref": build_index_ref(
                project_root=project_root,
                turn_anchor=anchor,
                raw_input_present=bool(_string_or_none(raw_user_input)),
            ),
            "refusal_reasons": [
                "confirm_store_raw_input_and_approval_phrase_required",
            ],
            "privacy": {
                "raw_prompt_persisted": False,
                "raw_prompt_exposed_in_audit": False,
            },
        }

    record = build_record(
        project_root=project_root,
        raw_user_input=raw_user_input,
        turn_anchor=turn_anchor,
        host_semantic_intent=host_semantic_intent,
        source_client=source_client,
        source_event=source_event,
        runtime_refs=runtime_refs,
        task_start_refs=task_start_refs,
        completion_review_refs=completion_review_refs,
        receipt_refs=receipt_refs,
        git_baseline_ref=git_baseline_ref,
        git_final_ref=git_final_ref,
    )
    ensure_private_store(project_root)
    index_path = index_path_for(project_root)
    with index_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")
    return {
        "schema": PRIVATE_TURN_INPUT_INDEX_SCHEMA,
        "status": "ok",
        "write_performed": True,
        "project_root": str(resolve_project_root(project_root)),
        "index_ref": INDEX_REF,
        "record": public_record_ref(record),
        "private_turn_input_ref": public_record_ref(record),
        "privacy": {
            "raw_prompt_persisted": True,
            "raw_prompt_exposed_in_audit": False,
            "raw_transcript_exposed_in_audit": False,
        },
    }


def read_private_records(
    *,
    project_root: Path | str | None,
    include_raw: bool = False,
) -> list[dict[str, Any]]:
    index_path = index_path_for(project_root)
    if not index_path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        records.append(record if include_raw else public_record_ref(record))
    return records


def search_private_turn_inputs(
    *,
    project_root: Path | str | None,
    query_text: str,
) -> dict[str, Any]:
    query = (_string_or_none(query_text) or "").lower()
    if not query:
        matches: list[dict[str, Any]] = []
    else:
        matches = []
        for record in read_private_records(project_root=project_root, include_raw=True):
            raw_text = str(record.get("raw_user_input") or "").lower()
            prompt_sha = str(record.get("prompt_sha256") or "").lower()
            if query in raw_text or query in prompt_sha:
                matches.append(public_record_ref(record))
    return {
        "schema": PRIVATE_TURN_INPUT_INDEX_SCHEMA,
        "status": "ok",
        "search_mode": "literal_private_index",
        "project_root": str(resolve_project_root(project_root)),
        "index_ref": INDEX_REF,
        "match_count": len(matches),
        "matches": matches,
        "privacy": {
            "raw_prompt_read_from_private_index": True,
            "raw_prompt_returned": False,
            "raw_prompt_exposed_in_audit": False,
        },
        "non_effects": [
            "does_not_call_llm_provider",
            "does_not_perform_semantic_inference",
            "does_not_write_files",
        ],
    }


def build_status_report(project_root: Path | str | None) -> dict[str, Any]:
    index_path = index_path_for(project_root)
    record_count = 0
    if index_path.is_file():
        record_count = len(
            [line for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        )
    return {
        "schema": PRIVATE_TURN_INPUT_INDEX_SCHEMA,
        "status": "available" if index_path.is_file() else "missing",
        "project_root": str(resolve_project_root(project_root)),
        "index_ref": INDEX_REF,
        "record_count": record_count,
        "privacy": {
            "storage_scope": "project_private_local",
            "raw_prompt_exposed_in_audit": False,
        },
    }


def format_report(report: dict[str, Any]) -> str:
    lines = [
        "# JIKUO Private Turn Input Index",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Project root: `{report.get('project_root')}`",
        f"- Index ref: `{report.get('index_ref', INDEX_REF)}`",
    ]
    if "record_count" in report:
        lines.append(f"- Record count: `{report.get('record_count')}`")
    if "match_count" in report:
        lines.append(f"- Match count: `{report.get('match_count')}`")
    if report.get("write_performed") is not None:
        lines.append(f"- Write performed: `{str(report.get('write_performed')).lower()}`")
    privacy = report.get("privacy") or {}
    if privacy:
        lines.extend(
            [
                "",
                "## Privacy",
                "",
                (
                    "- Raw prompt exposed in audit: "
                    f"`{str(privacy.get('raw_prompt_exposed_in_audit', False)).lower()}`"
                ),
            ]
        )
        if privacy.get("raw_prompt_returned") is not None:
            lines.append(
                "- Raw prompt returned: "
                f"`{str(privacy.get('raw_prompt_returned')).lower()}`"
            )
    matches = report.get("matches") or []
    if matches:
        lines.extend(["", "## Matches", ""])
        for item in matches:
            lines.append(
                "- "
                f"`{item.get('record_id')}` / "
                f"anchor=`{item.get('turn_anchor_id') or 'unavailable'}` / "
                f"prompt_sha256=`{item.get('prompt_sha256') or 'unavailable'}`"
            )
    refusals = report.get("refusal_reasons") or []
    if refusals:
        lines.extend(["", "## Refusal Reasons", ""])
        lines.extend(f"- `{item}`" for item in refusals)
    return "\n".join(lines).rstrip() + "\n"


def _json_arg(value: str | None, *, label: str) -> dict[str, Any] | None:
    if value is None:
        return None
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{label} must be valid JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise SystemExit(f"{label} must decode to an object")
    return decoded


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect or update the private JIKUO turn input index.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status")
    status.add_argument("--project-root", type=Path, default=None)
    status.add_argument("--format", choices=("markdown", "json"), default="markdown")

    append = subparsers.add_parser("append")
    append.add_argument("--project-root", type=Path, default=None)
    append.add_argument("--raw-input", default=None)
    append.add_argument("--raw-input-stdin", action="store_true")
    append.add_argument("--turn-anchor-json", default=None)
    append.add_argument("--host-semantic-intent-json", default=None)
    append.add_argument("--source-client", default=None)
    append.add_argument("--source-event", default=None)
    append.add_argument("--runtime-ref", action="append", default=[])
    append.add_argument("--task-start-ref", action="append", default=[])
    append.add_argument("--completion-review-ref", action="append", default=[])
    append.add_argument("--receipt-ref", action="append", default=[])
    append.add_argument("--git-baseline-ref", default=None)
    append.add_argument("--git-final-ref", default=None)
    append.add_argument("--confirm-store-raw-input", action="store_true")
    append.add_argument("--approval-phrase", default=None)
    append.add_argument("--format", choices=("markdown", "json"), default="markdown")

    search = subparsers.add_parser("search")
    search.add_argument("--project-root", type=Path, default=None)
    search.add_argument("--query", required=True)
    search.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "status":
        report = build_status_report(args.project_root)
    elif args.command == "search":
        report = search_private_turn_inputs(
            project_root=args.project_root,
            query_text=args.query,
        )
    else:
        raw_input = args.raw_input
        if args.raw_input_stdin:
            if raw_input:
                parser.error("--raw-input and --raw-input-stdin are mutually exclusive")
            raw_input = sys.stdin.read().rstrip("\r\n")
        if not raw_input:
            parser.error("append requires --raw-input or --raw-input-stdin")
        report = append_turn_input_record(
            project_root=args.project_root,
            raw_user_input=raw_input,
            turn_anchor=_json_arg(args.turn_anchor_json, label="--turn-anchor-json"),
            host_semantic_intent=_json_arg(
                args.host_semantic_intent_json,
                label="--host-semantic-intent-json",
            ),
            source_client=args.source_client,
            source_event=args.source_event,
            runtime_refs=args.runtime_ref,
            task_start_refs=args.task_start_ref,
            completion_review_refs=args.completion_review_ref,
            receipt_refs=args.receipt_ref,
            git_baseline_ref=args.git_baseline_ref,
            git_final_ref=args.git_final_ref,
            confirm_store_raw_input=args.confirm_store_raw_input,
            approval_phrase=args.approval_phrase,
        )
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report(report), end="")
    return 0 if report.get("status") != "refused" else 2


if __name__ == "__main__":
    sys.exit(main())
