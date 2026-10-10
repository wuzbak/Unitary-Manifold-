#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Phi-Debt Early Warning Library (Product 32)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_phi_debt_early_warning import run_recycling_dogfood


def main(argv: list[str] | None = None) -> int:
    steps = [(1.0, 0.9), (1.0, 0.85), (1.0, 0.7), (1.0, 0.6)]
    readings = run_recycling_dogfood(steps, capacity=1.0, discharge_rate=0.1)
    print(
        json.dumps(
            [{"time": r.time, "debt": r.debt, "status": r.status.value} for r in readings],
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
