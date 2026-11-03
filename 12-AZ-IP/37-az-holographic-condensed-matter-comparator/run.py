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
from az_holographic_condensed_matter_comparator.references import MAX_CSV_BYTES, compare_reference_csv


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Holographic condensed-matter comparator")
    parser.add_argument("--n-max", type=int, default=3)
    parser.add_argument("--references-csv", type=Path, help="UTF-8 CSV with name,delta,source headers")
    parser.add_argument("--serve", action="store_true", help="run as a live HTTP product instead")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8137)
    args = parser.parse_args(argv)

    if args.serve:
        if args.references_csv:
            parser.error("--references-csv cannot be combined with --serve; upload through the dashboard")
        from az_holographic_condensed_matter_comparator.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    try:
        if args.references_csv:
            with args.references_csv.open("rb") as stream:
                data = stream.read(MAX_CSV_BYTES + 1)
            if len(data) > MAX_CSV_BYTES:
                raise ValueError(f"CSV must be at most {MAX_CSV_BYTES} UTF-8 bytes")
            result = compare_reference_csv(data.decode("utf-8-sig"), n_max=args.n_max)
        else:
            result = compare_kk_tower_to_all_benchmarks(n_max=args.n_max)
    except (ValueError, OSError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

