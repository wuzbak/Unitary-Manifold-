#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Live-Data Harness (Product 40)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_live_data_harness import LiveDataError, fetch_earthquake_summary


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="AZ Live-Data Harness")
    parser.add_argument("--serve", action="store_true", help="run as a live HTTP product instead")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8140)
    args = parser.parse_args(argv)

    if args.serve:
        from az_live_data_harness.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    import json

    try:
        result = fetch_earthquake_summary()
    except LiveDataError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 2 if result["stale"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
