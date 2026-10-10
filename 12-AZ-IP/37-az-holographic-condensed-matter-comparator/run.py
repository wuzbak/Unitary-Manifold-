#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Holographic Condensed-Matter Comparator (Product 37)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_holographic_condensed_matter_comparator import compare_kk_tower_to_all_benchmarks


def main(argv=None) -> int:
    print(json.dumps(compare_kk_tower_to_all_benchmarks(n_max=3), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
