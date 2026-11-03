#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Formal Verification Library (Product 38)."""

from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_formal_verification_library import (
    PENTAD_SAFETY_PROPERTIES,
    require_z3,
    run_declarative_property,
    run_suite,
)


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Formal verification library")
    parser.add_argument("--serve", action="store_true", help="run as a live HTTP product instead")
    parser.add_argument("--property-json", type=Path, help="run a bounded declarative property from JSON")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8138)
    args = parser.parse_args(argv)

    if args.serve:
        from az_formal_verification_library.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    if args.property_json is not None:
        try:
            spec = json.loads(args.property_json.read_text(encoding="utf-8"))
            result = run_declarative_property(spec)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
            parser.error(str(exc))
        print(json.dumps(result.__dict__, sort_keys=True))
        return 0 if result.status == "PASS" else 1

    require_z3()
    summary = run_suite(PENTAD_SAFETY_PROPERTIES)
    for result in summary["results"]:
        print(f"[{result.status}] {result.name}: {result.description}")
    print(f"\n{summary['n_pass']}/{summary['n_total']} passed")
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
