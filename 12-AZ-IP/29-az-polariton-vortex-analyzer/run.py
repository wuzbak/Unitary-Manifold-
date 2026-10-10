#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Polariton Vortex Analyzer (Product 29)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_polariton_vortex_analyzer._repo import ensure_repo_on_path

ensure_repo_on_path()
from src.materials.polariton_vortex import critical_angle_deg  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    print(json.dumps({"predicted_critical_angle_deg": critical_angle_deg()}, indent=2))
    print(
        "This CLI reports the prediction curve only. Feed real pump-probe "
        "frames to az_polariton_vortex_analyzer.extract_feature_velocity_curve() "
        "and compare_to_prediction() for an actual comparison."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
