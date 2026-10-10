#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Domain Experts Pack (Product 34)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_domain_experts_pack import MATERIALS_EXPERT, SPECTROSCOPY_EXPERT


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "serve":
        import argparse

        serve_parser = argparse.ArgumentParser(prog="run.py serve")
        serve_parser.add_argument("--host", default="127.0.0.1")
        serve_parser.add_argument("--port", type=int, default=8134)
        args = serve_parser.parse_args(argv[1:])

        from az_domain_experts_pack.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    query = " ".join(argv) if argv else "polariton vortex critical angle"
    MATERIALS_EXPERT.build()
    SPECTROSCOPY_EXPERT.build()
    print(
        json.dumps(
            {
                "materials_science": MATERIALS_EXPERT.query(query),
                "atomic_spectroscopy": SPECTROSCOPY_EXPERT.query(query),
            },
            indent=2,
        )
    )
    print("Run `serve` to start the live HTTP product.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
