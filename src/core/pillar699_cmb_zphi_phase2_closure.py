# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar699_cmb_zphi_phase2_closure.py
=============================================
Pillar 699 — CMB Z_phi Phase 2 Closure

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

PILLAR_NUMBER = 699
PILLAR_STATUS = "PHASE2_CLOSED"

N_W = 5
K_CS = 74
C_S = 12.0 / 37.0
DELTA_KK = 8.0e-4
Z_PHI_PHASE1 = 5.30
OBSERVED_SUPPRESSION_CENTRAL = 5.5

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "N_W",
    "K_CS",
    "C_S",
    "DELTA_KK",
    "Z_PHI_PHASE1",
    "OBSERVED_SUPPRESSION_CENTRAL",
    "zphi_phase2_total",
    "suppression_coverage",
    "zphi_closure_status",
]


def zphi_phase2_total() -> Dict[str, float]:
    """Return Phase 1, Phase 2, and combined Z_phi factors."""
    z_phi_phase2 = 1.0 + N_W * C_S ** 2 / (4.0 * math.pi ** 2)
    z_phi_total = Z_PHI_PHASE1 * z_phi_phase2
    return {
        "z_phi_phase1": Z_PHI_PHASE1,
        "z_phi_phase2": z_phi_phase2,
        "z_phi_total": z_phi_total,
        "phase2_formula_value": N_W * C_S ** 2 / (4.0 * math.pi ** 2),
    }


def suppression_coverage() -> Dict[str, float]:
    """Compare the Phase 2 closure amplitude to the observed suppression."""
    totals = zphi_phase2_total()
    predicted_factor = totals["z_phi_total"]
    predicted_ratio = 1.0 / predicted_factor
    observed_ratio = 1.0 / OBSERVED_SUPPRESSION_CENTRAL
    coverage_fraction = min(predicted_ratio, observed_ratio) / max(predicted_ratio, observed_ratio)
    normalization_residual = predicted_ratio - observed_ratio
    return {
        "predicted_suppression_factor": predicted_factor,
        "observed_suppression_factor": OBSERVED_SUPPRESSION_CENTRAL,
        "predicted_amplitude_ratio": predicted_ratio,
        "observed_amplitude_ratio": observed_ratio,
        "coverage_fraction": coverage_fraction,
        "coverage_percent": coverage_fraction * 100.0,
        "normalization_residual": normalization_residual,
    }


def zphi_closure_status() -> Dict[str, object]:
    """Return the Phase 2 closure verdict."""
    totals = zphi_phase2_total()
    coverage = suppression_coverage()
    fraction = coverage["coverage_fraction"]
    if fraction > 0.80:
        status = "PHASE2_CLOSED"
    elif fraction >= 0.50:
        status = "PARTIAL"
    else:
        status = "ARCHITECTURE_LIMIT"
    return {
        "pillar": PILLAR_NUMBER,
        "status": status,
        "z_phi": totals,
        "coverage": coverage,
        "honesty_label": "CENTRAL_SUPPRESSION_5P5_USED",
    }
