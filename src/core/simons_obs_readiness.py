# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Simons Observatory β-readiness forecast harness (v10.28)."""
from __future__ import annotations

from typing import Dict

__all__ = [
    "BETA_MODE_SHADOW",
    "BETA_MODE_PRIMARY",
    "SIMONS_SIGMA_BETA",
    "beta_mode_separation_sigma",
    "simons_discrimination_forecast",
]

BETA_MODE_SHADOW: float = 0.273
BETA_MODE_PRIMARY: float = 0.331
SIMONS_SIGMA_BETA: float = 0.05


def beta_mode_separation_sigma(sigma_beta: float = SIMONS_SIGMA_BETA) -> float:
    """Return separation significance between the two UM β modes."""
    return abs(BETA_MODE_PRIMARY - BETA_MODE_SHADOW) / sigma_beta


def simons_discrimination_forecast(sigma_beta: float = SIMONS_SIGMA_BETA) -> Dict[str, object]:
    """Return readiness forecast for sector discrimination at Simons precision."""
    separation = beta_mode_separation_sigma(sigma_beta)
    if separation >= 3.0:
        verdict = "DISCRIMINATING"
    elif separation >= 2.0:
        verdict = "MARGINALLY_DISCRIMINATING"
    else:
        verdict = "CONSISTENT_NOT_DISCRIMINATING"

    return {
        "experiment": "Simons Observatory",
        "sigma_beta_deg": sigma_beta,
        "beta_shadow_deg": BETA_MODE_SHADOW,
        "beta_primary_deg": BETA_MODE_PRIMARY,
        "mode_separation_sigma": separation,
        "verdict": verdict,
        "note": "σβ≈0.05° can test window consistency and begin early branch pressure.",
    }
