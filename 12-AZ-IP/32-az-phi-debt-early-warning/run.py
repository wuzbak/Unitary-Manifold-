#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Phi-Debt Early Warning Library (Product 32)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_phi_debt_early_warning.api import dispatch_api_request


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ Phi-Debt Early Warning Library")
    sub = parser.add_subparsers(dest="command", required=True)
    serve_cmd = sub.add_parser("serve", help="Run the library as a live HTTP product")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8132)
    monitor_cmd = sub.add_parser("monitor", help="Analyze explicitly supplied debt observations")
    monitor_cmd.add_argument("--capacity", type=float, required=True)
    monitor_cmd.add_argument("--discharge-rate", type=float, required=True)
    monitor_cmd.add_argument("--warning-fraction", type=float, default=0.8)
    monitor_cmd.add_argument(
        "--steps",
        required=True,
        help="Comma-separated amount:dt observations, e.g. '0.5:1,0.2:1'",
    )
    args = parser.parse_args(argv)

    if args.command == "serve":
        from az_phi_debt_early_warning.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    try:
        result = dispatch_api_request(
            "/api/monitor",
            {
                "capacity": [str(args.capacity)],
                "discharge_rate": [str(args.discharge_rate)],
                "warning_fraction": [str(args.warning_fraction)],
                "steps": [args.steps],
            },
        )
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
