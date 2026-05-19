# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 231 — LISA Ω_GW preregistration package.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

from typing import Dict

ADJACENCY_TRACK_LABEL = "NON_HARDGATE_ADJACENT"


def omega_gw_preregistration_bounds() -> Dict[str, float]:
    return {
        "f_min_hz": 1.0e-4,
        "f_max_hz": 1.0,
        "alert_sigma": 3.0,
    }


def pillar231_preregistration_packet() -> Dict[str, object]:
    b = omega_gw_preregistration_bounds()
    return {
        "pillar": 231,
        "title": "LISA Ω_GW Preregistration Package",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "bounds": b,
        "status": "PREREGISTERED",
        "routing_instruction": "Run LISA ingest and update falsifier feed within 30 days of release.",
        "non_hardgate_statement": "Adjacent pre-registration packet only.",
    }
