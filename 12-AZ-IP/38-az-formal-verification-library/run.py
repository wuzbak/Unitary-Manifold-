#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Formal Verification Library (Product 38)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_formal_verification_library import require_z3, run_suite, PENTAD_SAFETY_PROPERTIES


def main(argv=None) -> int:
    require_z3()
    summary = run_suite(PENTAD_SAFETY_PROPERTIES)
    for result in summary["results"]:
        print(f"[{result.status}] {result.name}: {result.description}")
    print(f"\n{summary['n_pass']}/{summary['n_total']} passed")
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
