#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Materials Screening Engine (Product 30)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_materials_screening_engine import MaterialCandidate, rank_candidates

_DEMO_CANDIDATES = [
    MaterialCandidate("graphene", alpha=0.3, omega_lo_mev=180.0, m_band_me=0.02, epsilon_r=2.5),
    MaterialCandidate("MoS2", alpha=0.45, omega_lo_mev=50.0, m_band_me=0.5, epsilon_r=4.0),
    MaterialCandidate("hBN", alpha=2.1, omega_lo_mev=170.0, m_band_me=0.3, epsilon_r=5.0),
]


def main(argv: list[str] | None = None) -> int:
    print(json.dumps(rank_candidates(_DEMO_CANDIDATES), indent=2))
    print(
        "Demo candidates only — replace with a real Materials Project band-"
        "structure/dielectric-response query before trusting rankings."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
