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

from az_phi_debt_early_warning import run_recycling_dogfood


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ Phi-Debt Early Warning Library")
    sub = parser.add_subparsers(dest="command")
    serve_cmd = sub.add_parser("serve", help="Run the library as a live HTTP product")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8132)
    args = parser.parse_args(argv)

    if args.command == "serve":
        from az_phi_debt_early_warning.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    steps = [(1.0, 0.9), (1.0, 0.85), (1.0, 0.7), (1.0, 0.6)]
    readings = run_recycling_dogfood(steps, capacity=1.0, discharge_rate=0.1)
    print(
        json.dumps(
            [{"time": r.time, "debt": r.debt, "status": r.status.value} for r in readings],
            indent=2,
        )
    )
    print("Run `serve` to start the live HTTP product.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
