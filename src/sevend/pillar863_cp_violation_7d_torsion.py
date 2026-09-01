# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 863 — CP_VIOLATION_7D_PARTIAL_DERIVATION

Quark-sector Dirac CP phase from 7D discrete torsion.

Leading order
-------------
The Z₃ discrete torsion class of H¹(T²/Z₃, U(1)) gives the raw holonomy
φ = 2π/3, and the physically observable unitarity-triangle angle is the
supplementary phase (Pillar R2 / ``src.sevend.discrete_torsion_cp``)

    δ_CP^LO = π − 2π/3 = π/3 ≈ 1.0472 rad.

Braid correction
----------------
The S¹/Z₂ factor of the 7D geometry contributes a first-order braid
correction of relative size n_w/K_CS = 5/74, giving

    δ_CP^NLO = (π/3) · (1 + n_w/K_CS) ≈ 1.1180 rad.

The correction *size* is geometric; its precise coefficient is a leading-order
estimate and is registered as open.

PDG comparison
--------------
    δ_CP^PDG = 1.20 ± 0.08 rad.

Both the LO and NLO values sit inside 2σ; the pillar is nevertheless graded
PARTIAL because the NLO coefficient is not derived to all orders.
"""
from __future__ import annotations

import math
from typing import Any

from src.sevend.discrete_torsion_cp import DELTA_CP_GEO_RAD, PHI_HOLONOMY_RAD
from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import (
    K_CS,
    N_W,
    THETA_TORSION_7D,
)

PILLAR_NUMBER: int = 863
PILLAR_GATE: str = "CP_VIOLATION_7D_PARTIAL_DERIVATION"

LEAN4_THEOREM_COUNT: int = 25
LEAN4_TOTAL_BEFORE: int = 2251
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

TORSION_ORDER: int = 3
BRAID_CORRECTION: float = N_W / K_CS
DELTA_CP_LO_RAD: float = DELTA_CP_GEO_RAD
DELTA_CP_NLO_RAD: float = DELTA_CP_LO_RAD * (1.0 + BRAID_CORRECTION)
DELTA_CP_LO_DEG: float = math.degrees(DELTA_CP_LO_RAD)
DELTA_CP_NLO_DEG: float = math.degrees(DELTA_CP_NLO_RAD)

DELTA_CP_PDG_RAD: float = 1.20
DELTA_CP_PDG_ERR_RAD: float = 0.08

REMAINING_OPEN: list[str] = [
    "CP_7D_NLO_COEFFICIENT_OPEN: the braid correction coefficient n_w/K_CS is a "
    "leading-order estimate, not an all-orders derivation.",
    "CP_7D_SECTOR_UNIVERSALITY_OPEN: quark and lepton torsion branches are "
    "treated separately (Pillar 850 / Pillar 876) and not unified here.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "TORSION_ORDER",
    "BRAID_CORRECTION",
    "DELTA_CP_LO_RAD",
    "DELTA_CP_NLO_RAD",
    "DELTA_CP_LO_DEG",
    "DELTA_CP_NLO_DEG",
    "DELTA_CP_PDG_RAD",
    "DELTA_CP_PDG_ERR_RAD",
    "SIGMA_LO",
    "SIGMA_NLO",
    "WITHIN_2SIGMA_LO",
    "WITHIN_2SIGMA_NLO",
    "REMAINING_OPEN",
    "torsion_holonomy_rad",
    "supplementary_phase_rad",
    "braid_corrected_phase_rad",
    "tension_sigma",
    "cp_violation_7d_summary",
]


def torsion_holonomy_rad(order: int = TORSION_ORDER) -> float:
    """Return the raw Z_n discrete-torsion holonomy 2π/n."""
    if order <= 0:
        raise ValueError("order must be positive")
    return 2.0 * math.pi / order


def supplementary_phase_rad(order: int = TORSION_ORDER) -> float:
    """Return the observable unitarity-triangle phase π − 2π/n."""
    return math.pi - torsion_holonomy_rad(order)


def braid_corrected_phase_rad(
    order: int = TORSION_ORDER,
    n_w: int = N_W,
    k_cs: int = K_CS,
) -> float:
    """Return the braid-corrected CP phase (π − 2π/n)(1 + n_w/K_CS)."""
    if n_w <= 0 or k_cs <= 0:
        raise ValueError("n_w and k_cs must be positive")
    return supplementary_phase_rad(order) * (1.0 + n_w / k_cs)


def tension_sigma(
    theory_rad: float,
    pdg_rad: float = DELTA_CP_PDG_RAD,
    pdg_err_rad: float = DELTA_CP_PDG_ERR_RAD,
) -> float:
    """Return the tension in σ between a theory phase and the PDG value."""
    if pdg_err_rad <= 0.0:
        raise ValueError("pdg_err_rad must be positive")
    return abs(theory_rad - pdg_rad) / pdg_err_rad


SIGMA_LO: float = tension_sigma(DELTA_CP_LO_RAD)
SIGMA_NLO: float = tension_sigma(DELTA_CP_NLO_RAD)
WITHIN_2SIGMA_LO: bool = SIGMA_LO <= 2.0
WITHIN_2SIGMA_NLO: bool = SIGMA_NLO <= 2.0
NLO_IMPROVES: bool = SIGMA_NLO < SIGMA_LO


def cp_violation_7d_summary() -> dict[str, Any]:
    """Return the machine-readable 7D CP-violation certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "torsion_order": TORSION_ORDER,
        "phi_holonomy_rad": PHI_HOLONOMY_RAD,
        "theta_torsion_7d": THETA_TORSION_7D,
        "braid_correction": BRAID_CORRECTION,
        "delta_cp_lo_rad": DELTA_CP_LO_RAD,
        "delta_cp_nlo_rad": DELTA_CP_NLO_RAD,
        "delta_cp_lo_deg": DELTA_CP_LO_DEG,
        "delta_cp_nlo_deg": DELTA_CP_NLO_DEG,
        "delta_cp_pdg_rad": DELTA_CP_PDG_RAD,
        "delta_cp_pdg_err_rad": DELTA_CP_PDG_ERR_RAD,
        "tension_sigma_lo": SIGMA_LO,
        "tension_sigma_nlo": SIGMA_NLO,
        "within_2sigma_lo": WITHIN_2SIGMA_LO,
        "within_2sigma_nlo": WITHIN_2SIGMA_NLO,
        "nlo_improves": NLO_IMPROVES,
        "epistemic_status": (
            "PARTIAL: the Z₃ torsion branch fixes the phase geometrically and both "
            "the LO and braid-corrected values land inside PDG 2σ, but the "
            "correction coefficient is only leading order."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
