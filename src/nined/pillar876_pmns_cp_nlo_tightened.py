# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 876 — PMNS_CP_NLO_STABLE

Next-to-leading-order (two-loop torsion) correction to the 9D geometric
leptonic CP phase of Pillar 850.

The leading-order phase δ_PMNS^LO comes from the doubled holonomy branch with
the seesaw correction.  The two-loop discrete-torsion correction is suppressed
by the square of the braid ratio,

    δ_NLO = δ_LO · (1 + (n_w / K_CS)²) ,   (n_w/K_CS)² = (5/74)² ≈ 4.566 × 10⁻³,

so the NLO shift is under one degree.  The gate is ``PMNS_CP_NLO_STABLE`` when
the shift is below the 5° stability threshold, otherwise
``PMNS_CP_NLO_UNSTABLE``.
"""
from __future__ import annotations

import math
from typing import Any

from src.nined.pillar850_9d_pmns_cp_phase_derivation import (
    DELTA_PMNS_GEO_DEG,
    DELTA_PMNS_PDG_DEG,
    DELTA_PMNS_PDG_ERR_DEG,
)

PILLAR_NUMBER: int = 876

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 2531
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

N_W: int = 5
K_CS: int = 74
NLO_SUPPRESSION: float = (N_W / K_CS) ** 2
STABILITY_THRESHOLD_DEG: float = 5.0

REMAINING_OPEN: list[str] = [
    "PMNS_CP_NNLO_OPEN: three-loop torsion corrections are not computed.",
    "PMNS_CP_EXPERIMENTAL_OPEN: δ_CP^PMNS is measured to only ±25°; a decisive "
    "test awaits DUNE and Hyper-Kamiokande.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "N_W",
    "K_CS",
    "NLO_SUPPRESSION",
    "STABILITY_THRESHOLD_DEG",
    "DELTA_LO_DEG",
    "DELTA_NLO_DEG",
    "NLO_SHIFT_DEG",
    "NLO_STABLE",
    "SIGMA_LO",
    "SIGMA_NLO",
    "NLO_IMPROVES",
    "NLO_WITHIN_1SIGMA",
    "REMAINING_OPEN",
    "nlo_correction_factor",
    "delta_pmns_nlo_deg",
    "tension_sigma",
    "pmns_cp_nlo_summary",
]


def nlo_correction_factor(n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Return the two-loop torsion correction factor 1 + (n_w/k_CS)²."""
    if k_cs <= 0:
        raise ValueError("k_cs must be positive")
    return 1.0 + (n_w / k_cs) ** 2


def delta_pmns_nlo_deg(delta_lo_deg: float = DELTA_PMNS_GEO_DEG) -> float:
    """Return the NLO-corrected leptonic CP phase in degrees."""
    return delta_lo_deg * nlo_correction_factor()


def tension_sigma(
    predicted_deg: float,
    observed_deg: float = DELTA_PMNS_PDG_DEG,
    sigma_deg: float = DELTA_PMNS_PDG_ERR_DEG,
) -> float:
    """Return |predicted − observed| / σ in degrees."""
    if sigma_deg <= 0.0:
        raise ValueError("sigma_deg must be positive")
    return abs(predicted_deg - observed_deg) / sigma_deg


DELTA_LO_DEG: float = float(DELTA_PMNS_GEO_DEG)
DELTA_NLO_DEG: float = delta_pmns_nlo_deg()
NLO_SHIFT_DEG: float = abs(DELTA_NLO_DEG - DELTA_LO_DEG)
NLO_STABLE: bool = NLO_SHIFT_DEG < STABILITY_THRESHOLD_DEG
SIGMA_LO: float = tension_sigma(DELTA_LO_DEG)
SIGMA_NLO: float = tension_sigma(DELTA_NLO_DEG)
NLO_IMPROVES: bool = SIGMA_NLO < SIGMA_LO
NLO_WITHIN_1SIGMA: bool = SIGMA_NLO < 1.0
PILLAR_GATE: str = "PMNS_CP_NLO_STABLE" if NLO_STABLE else "PMNS_CP_NLO_UNSTABLE"


def pmns_cp_nlo_summary() -> dict[str, Any]:
    """Return the machine-readable PMNS CP NLO stability certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "n_w": N_W,
        "k_cs": K_CS,
        "nlo_suppression": NLO_SUPPRESSION,
        "nlo_correction_factor": nlo_correction_factor(),
        "delta_lo_deg": DELTA_LO_DEG,
        "delta_nlo_deg": DELTA_NLO_DEG,
        "delta_nlo_rad": math.radians(DELTA_NLO_DEG),
        "nlo_shift_deg": NLO_SHIFT_DEG,
        "stability_threshold_deg": STABILITY_THRESHOLD_DEG,
        "nlo_stable": NLO_STABLE,
        "delta_pdg_deg": DELTA_PMNS_PDG_DEG,
        "delta_pdg_err_deg": DELTA_PMNS_PDG_ERR_DEG,
        "sigma_lo": SIGMA_LO,
        "sigma_nlo": SIGMA_NLO,
        "nlo_improves": NLO_IMPROVES,
        "nlo_within_1sigma": NLO_WITHIN_1SIGMA,
        "epistemic_status": (
            "PARTIAL_CLOSURE: the NLO torsion correction shifts δ_CP^PMNS by "
            "under one degree, so the Pillar 850 geometric derivation is stable "
            "at two loops. The phase itself remains a partial derivation."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
