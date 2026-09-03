# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/observational_lane_freeze_registry.py
==============================================
Machine-readable freeze registry for observation-gated cosmology lanes.

This keeps r and w_a out of code-tuning loops and marks them as
external-data-gated architecture limits until new releases arrive.
"""

from __future__ import annotations

from typing import Dict

R_LANE_ID = "INFLATION_TENSOR_R"
WA_LANE_ID = "DARK_ENERGY_WA"


def observational_lane_freeze_registry() -> Dict[str, object]:
    """Return machine-checkable freeze status for r and w_a lanes."""
    return {
        "program": "OBSERVATION_GATED_FREEZE",
        "freeze_active": True,
        "lanes": {
            R_LANE_ID: {
                "status": "ARCH_LIMIT",
                "treatment": "FROZEN_UNTIL_NEW_DATA",
                "next_external_gate": "CMB-S4",
                "note": "Do not run code-parameter hunts for r inside locked (5,7) topology.",
            },
            WA_LANE_ID: {
                "status": "ARCH_LIMIT",
                "treatment": "FROZEN_UNTIL_NEW_DATA",
                "next_external_gate": "DESI DR3",
                "note": "Do not run code-parameter hunts for w_a inside frozen-radion 5D-EFT lane.",
            },
        },
    }
