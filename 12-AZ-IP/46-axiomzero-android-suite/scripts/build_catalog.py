#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Synchronize Product 46's offline Android catalog from Product 45's canonical build."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the bundled asset is stale")
    args = parser.parse_args()
    suite = Path(__file__).resolve().parents[1]
    root = suite.parents[1]
    source = root / "12-AZ-IP" / "45-axiomzero-pc-suite" / "catalog" / "products.json"
    target = suite / "app" / "src" / "main" / "assets" / "products.json"
    if not source.is_file():
        print(f"Canonical catalog is unavailable: {source}", file=sys.stderr)
        return 1
    expected = source.read_bytes()
    if args.check:
        if not target.is_file() or target.read_bytes() != expected:
            print(f"{target} is stale; run python scripts/build_catalog.py.", file=sys.stderr)
            return 1
        print("Android product catalog is current.")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(expected)
    print(f"Copied the canonical product catalog to {target}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
