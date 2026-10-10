#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Holographic Condensed-Matter Comparator (Product 37)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_holographic_condensed_matter_comparator import compare_kk_tower_to_all_benchmarks


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Holographic condensed-matter comparator")
    parser.add_argument("--n-max", type=int, default=3)
    parser.add_argument("--serve", action="store_true", help="run as a live HTTP product instead")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8137)
    args = parser.parse_args(argv)

    if args.serve:
        from az_holographic_condensed_matter_comparator.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    print(json.dumps(compare_kk_tower_to_all_benchmarks(n_max=args.n_max), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

