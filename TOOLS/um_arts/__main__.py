# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Run with python -m TOOLS.um_arts; execution requires pytest, not extra tooling."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import VERSION
from .capture import capture_command, evaluate_report
from .engine import import_artifact, plan, resume, run
from .evidence import EvidenceError, read_json
from .reporting import dashboard, report


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(
        description="Evidence-first regression orchestration; configs are trusted execution input.")
    cli.add_argument("--version", action="version", version=f"UM-ARTS {VERSION}")
    commands = cli.add_subparsers(dest="command", required=True)
    planning = commands.add_parser("plan", help="Collect structured identities and seal an execution plan")
    planning.add_argument("--root", type=Path, default=Path.cwd())
    planning.add_argument("--store", type=Path, default=Path(".um-arts"))
    planning.add_argument("--config", type=Path)
    planning.add_argument("--adapter", choices=["um", "generic"], default="um")
    planning.add_argument("--mode", choices=["full", "changed"], default="full")
    running = commands.add_parser("run", help="Execute a compatible sealed plan")
    running.add_argument("--plan", type=Path, required=True)
    continuing = commands.add_parser("resume", help="Create a new attempt, reusing only validated successes")
    continuing.add_argument("--attempt", type=Path, required=True)
    for name in ["verify", "report", "dashboard"]:
        reading = commands.add_parser(name, help="Read evidence without executing project/artifact commands")
        reading.add_argument("--attempt", type=Path, required=True)
        if name != "verify":
            reading.add_argument("--baseline", type=Path)
            reading.add_argument("--output", type=Path, required=name == "dashboard")
    importing = commands.add_parser("import", help="Verify and copy artifacts without executing commands")
    importing.add_argument("--artifact", type=Path, required=True)
    importing.add_argument("--store", type=Path, required=True)
    capturing = commands.add_parser("capture", help="Evaluate an existing CI pytest receipt; never rerun tests")
    capture_modes = capturing.add_mutually_exclusive_group(required=True)
    capture_modes.add_argument("--report", type=Path)
    capture_modes.add_argument("--output", type=Path)
    capturing.add_argument("--returncode", type=int)
    capturing.add_argument("--root", "--repo", type=Path, default=Path.cwd())
    capturing.add_argument("--timeout-seconds", "--timeout", type=float, default=600)
    capturing.add_argument("--expected-nodes", type=Path)
    capturing.add_argument("--timed-out", action="store_true")
    capturing.add_argument("--collection-only", action="store_true", default=None)
    capturing.add_argument("wrapped_command", nargs=argparse.REMAINDER)
    return cli


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = plan(args.root, args.store, args.config, args.adapter, args.mode)
        elif args.command == "run":
            result = run(args.plan)
        elif args.command == "resume":
            result = resume(args.attempt.resolve())
        elif args.command == "import":
            result = import_artifact(args.artifact.resolve(), args.store.resolve())
        elif args.command == "capture":
            if args.output:
                command = args.wrapped_command
                if command and command[0] == "--":
                    command = command[1:]
                if args.returncode is not None or args.expected_nodes or args.timed_out \
                        or args.collection_only:
                    raise EvidenceError("Evaluation-only capture options cannot wrap commands")
                result = capture_command(command, args.output, args.root, args.timeout_seconds)
            else:
                if args.wrapped_command or args.returncode is None:
                    raise EvidenceError("Report evaluation requires --returncode and no command")
                result = evaluate_report(args.report, returncode=args.returncode,
                                         timed_out=args.timed_out, collection_only=args.collection_only,
                                         expected_nodeids=(read_json(args.expected_nodes)
                                                           if args.expected_nodes else None))
        else:
            result = report(args.attempt.resolve(), getattr(args, "baseline", None))
            output = getattr(args, "output", None)
            if output:
                if output.resolve().is_relative_to(args.attempt.resolve()):
                    raise EvidenceError("Reports must be written outside immutable attempts")
                output.parent.mkdir(parents=True, exist_ok=True)
                with output.open("x", encoding="utf-8") as stream:
                    stream.write(dashboard(result) if args.command == "dashboard"
                                 else json.dumps(result, sort_keys=True, indent=2))
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0 if result["status"] in {"ready", "passed", "command_passed", "collection_passed"} else 2
    except (EvidenceError, OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
