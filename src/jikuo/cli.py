"""Top-level JIKUO command dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from . import (
        activation_settings,
        configuration_review,
        policy_management_status,
        runtime_visibility,
    )
    from .integrations import instruction_files
    from .studio import global_status
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jikuo import (
        activation_settings,
        configuration_review,
        policy_management_status,
        runtime_visibility,
    )
    from jikuo.integrations import instruction_files
    from jikuo.studio import global_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JIKUO command line interface.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show", help="Show JIKUO runtime status.")
    show.add_argument("--project-root", type=Path, default=None)
    show.add_argument("--last-card", action="store_true")
    show.add_argument("--format", choices=("markdown", "json"), default="markdown")
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
    studio = subparsers.add_parser(
        "studio",
        help="Inspect JIKUO Studio/global-console read models.",
    )
    studio.add_argument("studio_command", choices=("status",))
    studio.add_argument("--project-root", type=Path, default=None)
    studio.add_argument("--format", choices=("markdown", "json"), default="markdown")
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
    if args.command == "studio":
        studio_args = [args.studio_command]
        if args.project_root is not None:
            studio_args.extend(["--project-root", str(args.project_root)])
        studio_args.extend(["--format", args.format])
        return global_status.main(studio_args)
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
