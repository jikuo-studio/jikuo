"""Top-level JIKUO command dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from . import runtime_visibility
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import runtime_visibility


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JIKUO command line interface.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show", help="Show JIKUO runtime status.")
    show.add_argument("--project-root", type=Path, default=None)
    show.add_argument("--last-card", action="store_true")
    show.add_argument("--format", choices=("markdown", "json"), default="markdown")
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
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
