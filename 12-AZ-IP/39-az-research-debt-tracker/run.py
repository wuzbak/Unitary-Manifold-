#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Research-Debt Tracker (Product 39)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_research_debt_tracker import load_um_gaps_into_tracker


def main(argv=None) -> int:
    tracker = load_um_gaps_into_tracker()
    score = tracker.health_score()
    print(json.dumps(score.__dict__, indent=2))
    for item in tracker.open_items():
        print(f"- [{item.severity}] {item.item_id}: {item.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
