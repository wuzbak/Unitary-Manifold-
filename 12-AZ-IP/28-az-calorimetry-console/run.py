#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Calorimetry Console (Product 28)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_calorimetry_console import generate_run_sheet, COPTracker, import_measurements


def _write_artifact(path: Path, payload: str) -> None:
    staging = path.with_name(f".{path.name}.{uuid4().hex}.pending")
    created = False
    try:
        with staging.open("x", encoding="utf-8") as output:
            created = True
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        # A hard link publishes the complete file atomically without replacing
        # an existing destination, even when another importer races us.
        os.link(staging, path)
    finally:
        if created:
            staging.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ Calorimetry Console")
    sub = parser.add_subparsers(dest="command", required=True)

    sheet_cmd = sub.add_parser("run-sheet", help="Generate a calorimetry run-sheet")
    sheet_cmd.add_argument("--loading-target", type=float, default=0.875)
    sheet_cmd.add_argument("--hold-minutes", type=int, default=120)

    track_cmd = sub.add_parser("track", help="Report a COP reading")
    track_cmd.add_argument("--power-in-w", type=float, required=True)
    track_cmd.add_argument("--power-out-w", type=float, required=True)

    import_cmd = sub.add_parser("import-run", help="Validate instrument CSV and write a provenance artifact")
    import_cmd.add_argument("--csv", type=Path, required=True)
    import_cmd.add_argument("--metadata", type=Path, required=True)
    import_cmd.add_argument("--output", type=Path, required=True)

    serve_cmd = sub.add_parser("serve", help="Run the console as a live HTTP product")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8128)

    args = parser.parse_args(argv)

    if args.command == "import-run":
        try:
            report = import_measurements(args.csv, args.metadata)
            payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
            _write_artifact(args.output, payload)
        except (OSError, ValueError) as exc:
            parser.exit(2, f"import-run: {exc}\n")
        return 0

    if args.command == "run-sheet":
        sheet = generate_run_sheet(loading_target=args.loading_target, hold_minutes=args.hold_minutes)
        print(json.dumps(sheet.to_dict(), indent=2))
        return 0

    if args.command == "track":
        tracker = COPTracker()
        tracker.ingest(0.0, args.power_in_w, args.power_out_w)
        print(json.dumps(tracker.to_report(), indent=2))
        return 0

    if args.command == "serve":
        from az_calorimetry_console.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
