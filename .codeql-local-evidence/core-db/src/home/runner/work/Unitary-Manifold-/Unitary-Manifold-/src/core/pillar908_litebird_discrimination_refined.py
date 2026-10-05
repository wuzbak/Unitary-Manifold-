# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 908 — LITEBIRD_DISCRIMINATION_REFINED.

A refined three-hypothesis forecast compares the canonical (5,7) birefringence
branch against the shadow (5,6) branch and the null hypothesis β=0 using a
simple Gaussian Bayes-factor proxy.
"""
from __future__ import annotations

import math
from typing import Any

PILLAR_NUMBER: int = 908
PILLAR_GATE: str = "LITEBIRD_DISCRIMINATION_REFINED"
STATUS_LABEL: str = "PARTIAL"

BETA_57: float = 0.331
BETA_56_SHADOW: float = 0.273
SIGMA_LITEBIRD: float = 0.035

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "BETA_57",
    "BETA_56_SHADOW",
    "SIGMA_LITEBIRD",
    "BAYES_FACTOR_57_VS_0",
    "BAYES_FACTOR_57_VS_56",
    "DISCRIMINATION_GATE",
    "STATUS_LABEL",
    "discrimination_summary",
]


def gaussian_bayes_factor(observed: float, model_a: float, model_b: float, sigma: float = SIGMA_LITEBIRD) -> float:
    """Return a Gaussian likelihood-ratio proxy between two point hypotheses."""
    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    chi_a = (observed - model_a) ** 2 / sigma**2
    chi_b = (observed - model_b) ** 2 / sigma**2
    return math.exp((chi_b - chi_a) / 2.0)


BAYES_FACTOR_57_VS_0: float = gaussian_bayes_factor(BETA_57, BETA_57, 0.0)
BAYES_FACTOR_57_VS_56: float = gaussian_bayes_factor(BETA_57, BETA_57, BETA_56_SHADOW)
DISCRIMINATION_GATE: str = "DISCRIMINATION_READY" if BAYES_FACTOR_57_VS_0 > 10.0 else "FORECAST_WEAK"


def discrimination_summary() -> dict[str, Any]:
    """Return the machine-readable LiteBIRD discrimination forecast."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "beta_57": BETA_57,
        "beta_56_shadow": BETA_56_SHADOW,
        "sigma_litebird": SIGMA_LITEBIRD,
        "bayes_factor_57_vs_0": BAYES_FACTOR_57_VS_0,
        "bayes_factor_57_vs_56": BAYES_FACTOR_57_VS_56,
        "discrimination_gate": DISCRIMINATION_GATE,
        "delta_beta_over_sigma": abs(BETA_57 - BETA_56_SHADOW) / SIGMA_LITEBIRD,
        "epistemic_status": (
            "LiteBIRD is forecast to strongly separate β≈0.331° from β=0 and moderately separate it from the 0.273° shadow branch.  This remains a forecast only."
        ),
    }
