# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Run with python -m um_arts; execution requires pytest, not extra tooling."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import VERSION
from .capture import capture_command, evaluate_report
from .engine import import_artifact, plan, resume, run
from .evidence import EvidenceError, read_json, write_json
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
    serving = commands.add_parser("serve", help="Launch the loopback-only operational dashboard")
    serving.add_argument("--root", type=Path, default=Path.cwd())
    serving.add_argument("--store", type=Path, default=Path(".um-arts"))
    serving.add_argument("--config", type=Path)
    serving.add_argument("--adapter", choices=["um", "generic"], default="um")
    serving.add_argument("--mode", choices=["full", "changed"], default="full")
    serving.add_argument("--host", default="127.0.0.1")
    serving.add_argument("--port", type=int, default=8765)
    inventory = commands.add_parser("inventory", help="Review repository-wide candidates without execution")
    inventory.add_argument("--root", type=Path, default=Path.cwd())
    inventory.add_argument("--output", type=Path)
    inventory.add_argument("--config-output", type=Path)
    inventory.add_argument("--suite", action="append")
    inventory.add_argument("--lean-project")
    assisting = commands.add_parser("assist", help="Retrieve bounded cited context; never change evidence gates")
    assisting.add_argument("--root", type=Path, default=Path.cwd())
    assisting.add_argument("--query", default="")
    assisting.add_argument("--paths", nargs="+")
    assisting.add_argument("--output", type=Path)
    source = assisting.add_mutually_exclusive_group()
    source.add_argument("--report", type=Path)
    source.add_argument("--attempt", type=Path)
    snapshotting = commands.add_parser("snapshot", help="Copy source explicitly for isolated regression execution")
    snapshotting.add_argument("--root", type=Path, default=Path.cwd())
    snapshotting.add_argument("--output", type=Path, required=True)
    certifying = commands.add_parser("certify", help="Reconcile explicit manifest evidence without execution")
    certifying.add_argument("--manifest", type=Path, required=True)
    return cli


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "serve":
            from .server import serve

            serve(args.root, args.store, args.config, args.adapter, args.mode, args.host, args.port)
            return 0
        elif args.command == "plan":
            result = plan(args.root, args.store, args.config, args.adapter, args.mode)
        elif args.command == "snapshot":
            from .isolation import snapshot

            result = snapshot(args.root, args.output)
        elif args.command == "certify":
            from .certification import certify

            result = certify(args.manifest)
        elif args.command == "inventory":
            from .inventory import (
                discover_inventory,
                execution_config,
                selection_boundary,
            )

            result = discover_inventory(args.root)
            if args.config_output:
                config = execution_config(result, args.suite, args.lean_project)
                result["selection_boundary"] = selection_boundary(result, args.suite, args.lean_project)
                write_json(args.config_output, config)
                result["configuration_output"] = str(args.config_output.resolve())
            elif args.suite or args.lean_project:
                raise EvidenceError("Inventory selection requires --config-output")
            if args.output:
                write_json(args.output, result)
            print(json.dumps(result, sort_keys=True, allow_nan=False))
            return 0
        elif args.command == "assist":
            from .assistance import diagnostic_packet, retrieve_context

            if args.attempt and args.output and args.output.resolve().is_relative_to(
                    args.attempt.resolve()):
                raise EvidenceError("Assistance packets must be written outside immutable attempts")
            if args.report or args.attempt:
                evidence = report(args.attempt.resolve()) if args.attempt else read_json(args.report)
                result = diagnostic_packet(args.root, evidence, args.query, args.paths)
            else:
                result = retrieve_context(args.root, args.query, args.paths)
            if args.output:
                write_json(args.output, result)
            print(json.dumps(result, sort_keys=True, allow_nan=False))
            return 0
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
        return 0 if result["status"] in {
            "ready", "passed", "command_passed", "collection_passed", "snapshot_ready",
        } else 2
    except (EvidenceError, OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
