#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Geometric Tori Transformer (Product 43)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_tori_transformer import run_toroidal_copy_demo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ Geometric Tori Transformer")
    sub = parser.add_subparsers(dest="command")
    serve_cmd = sub.add_parser("serve", help="Run the studio as a live HTTP product")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8143)
    demo_cmd = sub.add_parser("demo", help="Run the toroidal-copy training demo and print the report")
    demo_cmd.add_argument("--steps", type=int, default=200)
    args = parser.parse_args(argv)

    if args.command == "serve":
        from az_tori_transformer.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    steps = args.steps if args.command == "demo" else 200
    report = run_toroidal_copy_demo(steps=steps)
    trace = report.pop("loss_trace")
    print(json.dumps(report, indent=2))
    print(f"loss[0]={trace[0]:.4f}  loss[-1]={trace[-1]:.4f}")
    print(
        "This is a synthetic cyclic-copy architecture smoke test, not a "
        "language-modelling benchmark result. Run `serve` to start the live "
        "HTTP product."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
