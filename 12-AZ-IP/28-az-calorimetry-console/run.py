#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Calorimetry Console (Product 28)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_calorimetry_console import generate_run_sheet, COPTracker


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ Calorimetry Console")
    sub = parser.add_subparsers(dest="command", required=True)

    sheet_cmd = sub.add_parser("run-sheet", help="Generate a calorimetry run-sheet")
    sheet_cmd.add_argument("--loading-target", type=float, default=0.875)
    sheet_cmd.add_argument("--hold-minutes", type=int, default=120)

    track_cmd = sub.add_parser("track", help="Report a COP reading")
    track_cmd.add_argument("--power-in-w", type=float, required=True)
    track_cmd.add_argument("--power-out-w", type=float, required=True)

    args = parser.parse_args(argv)

    if args.command == "run-sheet":
        sheet = generate_run_sheet(loading_target=args.loading_target, hold_minutes=args.hold_minutes)
        print(json.dumps(sheet.to_dict(), indent=2))
        return 0

    if args.command == "track":
        tracker = COPTracker()
        tracker.ingest(0.0, args.power_in_w, args.power_out_w)
        print(json.dumps(tracker.to_report(), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
