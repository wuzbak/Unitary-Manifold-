#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Live-Data Harness (Product 40)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_live_data_harness import fetch_planck_n_s_via_harness, planck_n_s_verdict


def main(argv=None) -> int:
    fetch_result = fetch_planck_n_s_via_harness()
    print(f"fetch source: {fetch_result.source.value}")
    if fetch_result.error:
        print(f"fetch error (expected -> fallback used): {fetch_result.error}")
    verdict = planck_n_s_verdict()
    print(verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
