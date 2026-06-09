"""Top-level JIKUO command dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from . import (
        activation_settings,
        configuration_review,
        doctor,
        policy_management_status,
        private_turn_input_index,
        runtime_visibility,
    )
    from .integrations import instruction_files
    from .integrations.studio_web import server as studio_web_server
    from .studio import document_rules, global_status
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jikuo import (
        activation_settings,
        configuration_review,
        doctor,
        policy_management_status,
        private_turn_input_index,
        runtime_visibility,
    )
    from jikuo.integrations import instruction_files
    from jikuo.integrations.studio_web import server as studio_web_server
    from jikuo.studio import document_rules, global_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JIKUO command line interface.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show", help="Show JIKUO runtime status.")
    show.add_argument("--project-root", type=Path, default=None)
    show.add_argument("--last-card", action="store_true")
    show.add_argument("--format", choices=("markdown", "json"), default="markdown")
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Run terminal diagnostics for install, configuration, MCP, Studio, and runtime readiness.",
    )
    doctor_parser.add_argument("--project-root", type=Path, default=None)
    doctor_parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
    )
    install = subparsers.add_parser(
        "install",
        help="Install JIKUO project instruction files.",
    )
    install.add_argument("--project-root", type=Path, default=None)
    install.add_argument(
        "--client",
        choices=instruction_files.SYNC_CLIENTS,
        action="append",
        default=[],
    )
    install.add_argument("--all", action="store_true")
    install.add_argument(
        "--trigger-mode",
        choices=instruction_files.TRIGGER_MODE_CHOICES,
        default=None,
        help="Instruction-file activation mode to write or preview.",
    )
    install.add_argument("--write", action="store_true")
    install.add_argument("--confirm-install", action="store_true")
    install.add_argument("--approval-phrase", default=None)
    install.add_argument("--format", choices=("markdown", "json"), default="markdown")
    settings = subparsers.add_parser(
        "settings",
        help="Inspect or update JIKUO activation settings.",
    )
    settings.add_argument("settings_command", choices=("status", "plan", "apply"))
    settings.add_argument("--project-root", type=Path, default=None)
    settings.add_argument(
        "--trigger-mode",
        choices=activation_settings.TRIGGER_MODE_CHOICES,
        default="ask",
    )
    settings.add_argument(
        "--effective-enforcement-level",
        choices=activation_settings.ENFORCEMENT_LEVELS,
        default="instruction_only",
    )
    settings.add_argument("--client", action="append", default=[])
    settings.add_argument("--confirm-apply", action="store_true")
    settings.add_argument("--approval-phrase", default=None)
    settings.add_argument("--format", choices=("markdown", "json"), default="markdown")
    configure = subparsers.add_parser(
        "configure",
        help="Review JIKUO first-use and ongoing configuration status.",
    )
    configure.add_argument("configure_command", choices=("status", "review"))
    configure.add_argument("--project-root", type=Path, default=None)
    configure.add_argument("--format", choices=("markdown", "json"), default="markdown")
    policy_management = subparsers.add_parser(
        "policy-management",
        help="Inspect JIKUO policy-management status.",
    )
    policy_management.add_argument("policy_management_command", choices=("status",))
    policy_management.add_argument("--project-root", type=Path, default=None)
    policy_management.add_argument(
        "--starter-pack-id",
        default=policy_management_status.DEFAULT_STARTER_PACK_ID,
    )
    policy_management.add_argument("--template-dir", type=Path, default=None)
    policy_management.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
    )
    turn_input_index = subparsers.add_parser(
        "turn-input-index",
        help="Inspect or update the private local turn input index.",
    )
    turn_input_index.add_argument(
        "turn_input_index_command",
        choices=("status", "append", "search"),
    )
    turn_input_index.add_argument("--project-root", type=Path, default=None)
    turn_input_index.add_argument("--raw-input", default=None)
    turn_input_index.add_argument("--raw-input-stdin", action="store_true")
    turn_input_index.add_argument("--turn-anchor-json", default=None)
    turn_input_index.add_argument("--host-semantic-intent-json", default=None)
    turn_input_index.add_argument("--source-client", default=None)
    turn_input_index.add_argument("--source-event", default=None)
    turn_input_index.add_argument("--runtime-ref", action="append", default=[])
    turn_input_index.add_argument("--task-start-ref", action="append", default=[])
    turn_input_index.add_argument("--completion-review-ref", action="append", default=[])
    turn_input_index.add_argument("--receipt-ref", action="append", default=[])
    turn_input_index.add_argument("--git-baseline-ref", default=None)
    turn_input_index.add_argument("--git-final-ref", default=None)
    turn_input_index.add_argument("--query", default=None)
    turn_input_index.add_argument("--confirm-store-raw-input", action="store_true")
    turn_input_index.add_argument("--approval-phrase", default=None)
    turn_input_index.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
    )
    studio = subparsers.add_parser(
        "studio",
        help="Inspect JIKUO Studio/global-console read models.",
    )
    studio.add_argument("studio_command", choices=("status", "serve", "document-rules"))
    studio.add_argument("studio_subcommand", nargs="?", choices=("plan", "apply"))
    studio.add_argument("--project-root", type=Path, default=None)
    studio.add_argument("--format", choices=("markdown", "json"), default="markdown")
    studio.add_argument("--host", default=studio_web_server.DEFAULT_HOST)
    studio.add_argument("--port", type=int, default=studio_web_server.DEFAULT_PORT)
    studio.add_argument("--add-context-doc", action="append", default=[])
    studio.add_argument("--remove-context-doc", action="append", default=[])
    studio.add_argument("--add-completion-check", action="append", default=[])
    studio.add_argument("--remove-completion-check", action="append", default=[])
    studio.add_argument("--add-governance-reference", action="append", default=[])
    studio.add_argument("--remove-governance-reference", action="append", default=[])
    studio.add_argument("--completion-update-rule", default=None)
    studio.add_argument("--plan-json-file", type=Path, default=None)
    studio.add_argument("--plan-json-stdin", action="store_true")
    studio.add_argument("--confirm-apply", action="store_true")
    studio.add_argument("--approval-phrase", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show":
        runtime_args = []
        if args.project_root is not None:
            runtime_args.extend(["--project-root", str(args.project_root)])
        if args.last_card:
            runtime_args.append("--last-card")
        runtime_args.extend(["--format", args.format])
        return runtime_visibility.main(runtime_args)
    if args.command == "doctor":
        doctor_args = []
        if args.project_root is not None:
            doctor_args.extend(["--project-root", str(args.project_root)])
        doctor_args.extend(["--format", args.format])
        return doctor.main(doctor_args)
    if args.command == "install":
        install_args = []
        if args.project_root is not None:
            install_args.extend(["--project-root", str(args.project_root)])
        for client in args.client:
            install_args.extend(["--client", client])
        if args.all:
            install_args.append("--all")
        if args.trigger_mode:
            install_args.extend(["--trigger-mode", args.trigger_mode])
        if args.write:
            install_args.append("--write")
        if args.confirm_install:
            install_args.append("--confirm-install")
        if args.approval_phrase:
            install_args.extend(["--approval-phrase", args.approval_phrase])
        install_args.extend(["--format", args.format])
        return instruction_files.main(install_args)
    if args.command == "settings":
        settings_args = [args.settings_command]
        if args.project_root is not None:
            settings_args.extend(["--project-root", str(args.project_root)])
        if args.settings_command in {"plan", "apply"}:
            settings_args.extend(["--trigger-mode", args.trigger_mode])
            settings_args.extend(
                ["--effective-enforcement-level", args.effective_enforcement_level]
            )
            for client in args.client:
                settings_args.extend(["--client", client])
        if args.settings_command == "apply":
            if args.confirm_apply:
                settings_args.append("--confirm-apply")
            if args.approval_phrase:
                settings_args.extend(["--approval-phrase", args.approval_phrase])
        settings_args.extend(["--format", args.format])
        return activation_settings.main(settings_args)
    if args.command == "configure":
        configure_args = [args.configure_command]
        if args.project_root is not None:
            configure_args.extend(["--project-root", str(args.project_root)])
        configure_args.extend(["--format", args.format])
        return configuration_review.main(configure_args)
    if args.command == "policy-management":
        status_args = [args.policy_management_command]
        if args.project_root is not None:
            status_args.extend(["--project-root", str(args.project_root)])
        if args.starter_pack_id is not None:
            status_args.extend(["--starter-pack-id", str(args.starter_pack_id)])
        if args.template_dir is not None:
            status_args.extend(["--template-dir", str(args.template_dir)])
        status_args.extend(["--format", args.format])
        return policy_management_status.main(status_args)
    if args.command == "turn-input-index":
        index_args = [args.turn_input_index_command]
        if args.project_root is not None:
            index_args.extend(["--project-root", str(args.project_root)])
        if args.turn_input_index_command == "append":
            if args.raw_input:
                index_args.extend(["--raw-input", args.raw_input])
            if args.raw_input_stdin:
                index_args.append("--raw-input-stdin")
            if args.turn_anchor_json:
                index_args.extend(["--turn-anchor-json", args.turn_anchor_json])
            if args.host_semantic_intent_json:
                index_args.extend(
                    ["--host-semantic-intent-json", args.host_semantic_intent_json]
                )
            if args.source_client:
                index_args.extend(["--source-client", args.source_client])
            if args.source_event:
                index_args.extend(["--source-event", args.source_event])
            for ref in args.runtime_ref:
                index_args.extend(["--runtime-ref", ref])
            for ref in args.task_start_ref:
                index_args.extend(["--task-start-ref", ref])
            for ref in args.completion_review_ref:
                index_args.extend(["--completion-review-ref", ref])
            for ref in args.receipt_ref:
                index_args.extend(["--receipt-ref", ref])
            if args.git_baseline_ref:
                index_args.extend(["--git-baseline-ref", args.git_baseline_ref])
            if args.git_final_ref:
                index_args.extend(["--git-final-ref", args.git_final_ref])
            if args.confirm_store_raw_input:
                index_args.append("--confirm-store-raw-input")
            if args.approval_phrase:
                index_args.extend(["--approval-phrase", args.approval_phrase])
        if args.turn_input_index_command == "search":
            if not args.query:
                parser.error("turn-input-index search requires --query")
            index_args.extend(["--query", args.query])
        index_args.extend(["--format", args.format])
        return private_turn_input_index.main(index_args)
    if args.command == "studio":
        if args.studio_command == "status":
            studio_args = [args.studio_command]
            if args.project_root is not None:
                studio_args.extend(["--project-root", str(args.project_root)])
            studio_args.extend(["--format", args.format])
            return global_status.main(studio_args)
        if args.studio_command == "serve":
            serve_args = ["serve", "--host", args.host, "--port", str(args.port)]
            if args.project_root is not None:
                serve_args.extend(["--project-root", str(args.project_root)])
            return studio_web_server.main(serve_args)
        if args.studio_command == "document-rules":
            if args.studio_subcommand not in {"plan", "apply"}:
                parser.error("studio document-rules requires `plan` or `apply`")
            plan_args = [args.studio_subcommand]
            if args.project_root is not None:
                plan_args.extend(["--project-root", str(args.project_root)])
            if args.studio_subcommand == "plan":
                for path_ref in args.add_context_doc:
                    plan_args.extend(["--add-context-doc", path_ref])
                for path_ref in args.remove_context_doc:
                    plan_args.extend(["--remove-context-doc", path_ref])
                for path_ref in args.add_completion_check:
                    plan_args.extend(["--add-completion-check", path_ref])
                for path_ref in args.remove_completion_check:
                    plan_args.extend(["--remove-completion-check", path_ref])
                for path_ref in args.add_governance_reference:
                    plan_args.extend(["--add-governance-reference", path_ref])
                for path_ref in args.remove_governance_reference:
                    plan_args.extend(["--remove-governance-reference", path_ref])
                if args.completion_update_rule:
                    plan_args.extend(["--completion-update-rule", args.completion_update_rule])
            if args.studio_subcommand == "apply":
                if args.plan_json_file is not None:
                    plan_args.extend(["--plan-json-file", str(args.plan_json_file)])
                if args.plan_json_stdin:
                    plan_args.append("--plan-json-stdin")
                if args.confirm_apply:
                    plan_args.append("--confirm-apply")
                if args.approval_phrase:
                    plan_args.extend(["--approval-phrase", args.approval_phrase])
            plan_args.extend(["--format", args.format])
            return document_rules.main(plan_args)
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
