# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 862 — 7D CKM mixing angles from the bulk mass SVD.

The CKM matrix is obtained without any fitted parameter as

    V_CKM = U_L(up)ᵀ · U_L(down),

where U_L is the left singular-vector matrix of the Pillar 861 bulk mass
matrix in each sector.  Angles are extracted in the standard PDG
parametrisation:

    s₁₃ = |V₁₃|,  θ₁₂ = atan2(|V₁₂|, |V₁₁|),  θ₂₃ = atan2(|V₂₃|, |V₃₃|).

Honest status
-------------
The gate is computed, not asserted.  Every angle is compared to PDG with an
explicit σ tension; the gate is

    CKM_7D_MIXING_PARTIAL_CLOSURE   if all three angles sit within 2σ,
    CKM_7D_PARTIAL_TENSION          otherwise.

With the canonical charges c_up = (0, ½, 1) and c_down = (0, ¼, ¾) only θ₁₂
lands within ~10% of PDG; θ₁₃ and θ₂₃ are in tension, and that is reported as
a tension rather than absorbed by tuning.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import (
    C_DOWN,
    C_UP,
    EPSILON_WARP,
    bulk_mass_matrix,
)

PILLAR_NUMBER: int = 862

LEAN4_THEOREM_COUNT: int = 30
LEAN4_TOTAL_BEFORE: int = 2221
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

THETA_12_PDG_DEG: float = 13.04
THETA_12_PDG_ERR_DEG: float = 0.05
THETA_13_PDG_DEG: float = 0.201
THETA_13_PDG_ERR_DEG: float = 0.011
THETA_23_PDG_DEG: float = 2.38
THETA_23_PDG_ERR_DEG: float = 0.06

TWO_SIGMA: float = 2.0

GATE_PARTIAL_CLOSURE: str = "CKM_7D_MIXING_PARTIAL_CLOSURE"
GATE_PARTIAL_TENSION: str = "CKM_7D_PARTIAL_TENSION"

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "GATE_PARTIAL_CLOSURE",
    "GATE_PARTIAL_TENSION",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "THETA_12_DEG",
    "THETA_13_DEG",
    "THETA_23_DEG",
    "THETA_12_PDG_DEG",
    "THETA_13_PDG_DEG",
    "THETA_23_PDG_DEG",
    "CKM_MATRIX_ABS",
    "ALL_WITHIN_2SIGMA",
    "REMAINING_OPEN",
    "left_rotation",
    "ckm_matrix",
    "mixing_angles_deg",
    "tension_sigma",
    "ckm_7d_mixing_angles_summary",
]


def left_rotation(c_values: tuple[float, float, float]) -> np.ndarray:
    """Return the left singular-vector matrix U_L for a bulk mass sector."""
    u, _, _ = np.linalg.svd(bulk_mass_matrix(c_values))
    return u


def ckm_matrix(
    c_up: tuple[float, float, float] = C_UP,
    c_down: tuple[float, float, float] = C_DOWN,
) -> np.ndarray:
    """Return V_CKM = U_L(up)ᵀ U_L(down)."""
    return left_rotation(c_up).T @ left_rotation(c_down)


def mixing_angles_deg(
    c_up: tuple[float, float, float] = C_UP,
    c_down: tuple[float, float, float] = C_DOWN,
) -> dict[str, float]:
    """Return the standard-parametrisation CKM angles in degrees."""
    v = np.abs(ckm_matrix(c_up, c_down))
    s13 = min(1.0, float(v[0, 2]))
    return {
        "theta_12": math.degrees(math.atan2(float(v[0, 1]), float(v[0, 0]))),
        "theta_13": math.degrees(math.asin(s13)),
        "theta_23": math.degrees(math.atan2(float(v[1, 2]), float(v[2, 2]))),
    }


def tension_sigma(theory_deg: float, pdg_deg: float, pdg_err_deg: float) -> float:
    """Return |theory − PDG| / σ_PDG."""
    if pdg_err_deg <= 0.0:
        raise ValueError("pdg_err_deg must be positive")
    return abs(theory_deg - pdg_deg) / pdg_err_deg


CKM_MATRIX: np.ndarray = ckm_matrix()
CKM_MATRIX_ABS: np.ndarray = np.abs(CKM_MATRIX)
_ANGLES: dict[str, float] = mixing_angles_deg()
THETA_12_DEG: float = _ANGLES["theta_12"]
THETA_13_DEG: float = _ANGLES["theta_13"]
THETA_23_DEG: float = _ANGLES["theta_23"]

SIGMA_12: float = tension_sigma(THETA_12_DEG, THETA_12_PDG_DEG, THETA_12_PDG_ERR_DEG)
SIGMA_13: float = tension_sigma(THETA_13_DEG, THETA_13_PDG_DEG, THETA_13_PDG_ERR_DEG)
SIGMA_23: float = tension_sigma(THETA_23_DEG, THETA_23_PDG_DEG, THETA_23_PDG_ERR_DEG)

ALL_WITHIN_2SIGMA: bool = bool(
    SIGMA_12 <= TWO_SIGMA and SIGMA_13 <= TWO_SIGMA and SIGMA_23 <= TWO_SIGMA
)
PILLAR_GATE: str = GATE_PARTIAL_CLOSURE if ALL_WITHIN_2SIGMA else GATE_PARTIAL_TENSION

UNITARITY_RESIDUAL: float = float(
    np.max(np.abs(CKM_MATRIX.T @ CKM_MATRIX - np.eye(3)))
)

REMAINING_OPEN: list[str] = [
    "CKM_7D_EXACT_ANGLES_OPEN: θ₁₃ and θ₂₃ remain in tension with PDG; "
    "sub-leading Froggatt-Nielsen charges are still required.",
    "CKM_7D_SECTOR_ALIGNMENT_OPEN: relative up/down orbifold alignment is fixed "
    "by the canonical charge ladder rather than derived.",
]


def ckm_7d_mixing_angles_summary() -> dict[str, Any]:
    """Return the machine-readable 7D CKM mixing-angle certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "epsilon_warp": EPSILON_WARP,
        "ckm_matrix_abs": CKM_MATRIX_ABS.tolist(),
        "unitarity_residual": UNITARITY_RESIDUAL,
        "angles_deg": {
            "theta_12": THETA_12_DEG,
            "theta_13": THETA_13_DEG,
            "theta_23": THETA_23_DEG,
        },
        "pdg_deg": {
            "theta_12": THETA_12_PDG_DEG,
            "theta_13": THETA_13_PDG_DEG,
            "theta_23": THETA_23_PDG_DEG,
        },
        "tension_sigma": {
            "theta_12": SIGMA_12,
            "theta_13": SIGMA_13,
            "theta_23": SIGMA_23,
        },
        "residual_fraction": {
            "theta_12": abs(THETA_12_DEG - THETA_12_PDG_DEG) / THETA_12_PDG_DEG,
            "theta_13": abs(THETA_13_DEG - THETA_13_PDG_DEG) / THETA_13_PDG_DEG,
            "theta_23": abs(THETA_23_DEG - THETA_23_PDG_DEG) / THETA_23_PDG_DEG,
        },
        "all_within_2sigma": ALL_WITHIN_2SIGMA,
        "theta_12_within_ten_percent": abs(THETA_12_DEG - THETA_12_PDG_DEG) / THETA_12_PDG_DEG < 0.10,
        "epistemic_status": (
            "PARTIAL_TENSION: the parameter-free SVD reproduces θ₁₂ at the ~10% "
            "level, while θ₁₃ and θ₂₃ are registered as open tensions."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
