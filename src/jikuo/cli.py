"""Top-level JIKUO command dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from . import activation_settings, configuration_review, runtime_visibility
    from .integrations import instruction_files
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jikuo import activation_settings, configuration_review, runtime_visibility
    from jikuo.integrations import instruction_files


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
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
