"""Top-level JIKUO command dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from . import runtime_visibility
    from .integrations import instruction_files
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from jikuo import runtime_visibility
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
        default="ask",
        help="Instruction-file activation mode to write or preview.",
    )
    install.add_argument("--write", action="store_true")
    install.add_argument("--confirm-install", action="store_true")
    install.add_argument("--approval-phrase", default=None)
    install.add_argument("--format", choices=("markdown", "json"), default="markdown")
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
        install_args.extend(["--trigger-mode", args.trigger_mode])
        if args.write:
            install_args.append("--write")
        if args.confirm_install:
            install_args.append("--confirm-install")
        if args.approval_phrase:
            install_args.extend(["--approval-phrase", args.approval_phrase])
        install_args.extend(["--format", args.format])
        return instruction_files.main(install_args)
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
