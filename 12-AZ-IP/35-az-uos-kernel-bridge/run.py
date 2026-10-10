#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ UOS/AZ-KERNEL Bridge (Product 35)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_uos_kernel_bridge import validate_against_kk_channel_rs, GEODESIC_SCHEDULABLE_RUST_CONTRACT


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ UOS/AZ-KERNEL Bridge")
    sub = parser.add_subparsers(dest="command")
    serve_cmd = sub.add_parser("serve", help="Run the bridge as a live HTTP product")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8135)
    args = parser.parse_args(argv)

    if args.command == "serve":
        from az_uos_kernel_bridge.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    print(json.dumps(validate_against_kk_channel_rs(), indent=2))
    print(json.dumps([f.__dict__ for f in GEODESIC_SCHEDULABLE_RUST_CONTRACT], indent=2))
    print("Run `serve` to start the live HTTP product.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
