# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 888 — CKM_7D_FN_CORRECTION.

The Pillar 861 bulk mass textures are dressed by Froggatt-Nielsen overlap
suppression factors ε^|Δqᵢⱼ| derived in Pillar 887.  Separate up- and
down-sector SVDs then yield a corrected CKM matrix.

Honest status
-------------
The FN layer improves the 7D CKM hierarchy relative to the older SVD closure,
but the resulting angle triplet is still compared directly to PDG.  Closure is
only reported if all three angles land within 2σ; otherwise the wrong ordering
or wrong magnitudes remain registered as tension.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import C_DOWN, C_UP, bulk_mass_matrix
from src.sevend.pillar862_ckm_7d_mixing_angles import (
    THETA_12_PDG_DEG,
    THETA_12_PDG_ERR_DEG,
    THETA_13_PDG_DEG,
    THETA_13_PDG_ERR_DEG,
    THETA_23_PDG_DEG,
    THETA_23_PDG_ERR_DEG,
    tension_sigma,
)
from src.sevend.pillar887_fn_charge_assignment import (
    FN_CHARGES_DOWN,
    FN_CHARGES_UP,
    fn_suppression_matrix,
)

PILLAR_NUMBER: int = 888
PILLAR_GATE: str = "CKM_7D_FN_CORRECTION"

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "CKM_FN_MATRIX",
    "THETA_12_FN",
    "THETA_13_FN",
    "THETA_23_FN",
    "CKM_7D_FN_GATE",
    "STATUS_LABEL",
    "corrected_bulk_mass_matrix",
    "ckm_fn_matrix",
    "ckm_fn_correction_summary",
]


def corrected_bulk_mass_matrix(
    c_values: tuple[float, float, float],
    charges: tuple[int, int, int],
) -> np.ndarray:
    """Return the FN-corrected 7D bulk mass matrix for one flavour sector."""
    return bulk_mass_matrix(c_values) * fn_suppression_matrix(charges)


M_UP_FN: np.ndarray = corrected_bulk_mass_matrix(C_UP, FN_CHARGES_UP)
M_DOWN_FN: np.ndarray = corrected_bulk_mass_matrix(C_DOWN, FN_CHARGES_DOWN)


def ckm_fn_matrix() -> np.ndarray:
    """Return the CKM matrix reconstructed from FN-corrected SVDs."""
    u_up, _, _ = np.linalg.svd(M_UP_FN)
    u_down, _, _ = np.linalg.svd(M_DOWN_FN)
    return u_up.T @ u_down


CKM_FN_MATRIX: np.ndarray = ckm_fn_matrix()
_CKM_FN_ABS = np.abs(CKM_FN_MATRIX)
THETA_12_FN: float = math.degrees(math.atan2(float(_CKM_FN_ABS[0, 1]), float(_CKM_FN_ABS[0, 0])))
THETA_13_FN: float = math.degrees(math.asin(min(1.0, float(_CKM_FN_ABS[0, 2]))))
THETA_23_FN: float = math.degrees(math.atan2(float(_CKM_FN_ABS[1, 2]), float(_CKM_FN_ABS[2, 2])))

SIGMA_12_FN: float = tension_sigma(THETA_12_FN, THETA_12_PDG_DEG, THETA_12_PDG_ERR_DEG)
SIGMA_13_FN: float = tension_sigma(THETA_13_FN, THETA_13_PDG_DEG, THETA_13_PDG_ERR_DEG)
SIGMA_23_FN: float = tension_sigma(THETA_23_FN, THETA_23_PDG_DEG, THETA_23_PDG_ERR_DEG)
ALL_WITHIN_2SIGMA: bool = all(sigma <= 2.0 for sigma in (SIGMA_12_FN, SIGMA_13_FN, SIGMA_23_FN))
CKM_7D_FN_GATE: str = "RESOLVED" if ALL_WITHIN_2SIGMA else "TENSION_PERSISTS"
STATUS_LABEL: str = CKM_7D_FN_GATE
UNITARITY_RESIDUAL: float = float(np.max(np.abs(CKM_FN_MATRIX.T @ CKM_FN_MATRIX - np.eye(3))))
PDG_DISTANCE_DEG: float = (
    abs(THETA_12_FN - THETA_12_PDG_DEG)
    + abs(THETA_13_FN - THETA_13_PDG_DEG)
    + abs(THETA_23_FN - THETA_23_PDG_DEG)
)


def ckm_fn_correction_summary() -> dict[str, Any]:
    """Return the machine-readable CKM FN-correction summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "fn_verdict": CKM_7D_FN_GATE,
        "m_up_fn": M_UP_FN.tolist(),
        "m_down_fn": M_DOWN_FN.tolist(),
        "ckm_fn_matrix_abs": _CKM_FN_ABS.tolist(),
        "unitarity_residual": UNITARITY_RESIDUAL,
        "angles_deg": {
            "theta_12": THETA_12_FN,
            "theta_13": THETA_13_FN,
            "theta_23": THETA_23_FN,
        },
        "pdg_deg": {
            "theta_12": THETA_12_PDG_DEG,
            "theta_13": THETA_13_PDG_DEG,
            "theta_23": THETA_23_PDG_DEG,
        },
        "tension_sigma": {
            "theta_12": SIGMA_12_FN,
            "theta_13": SIGMA_13_FN,
            "theta_23": SIGMA_23_FN,
        },
        "all_within_2sigma": ALL_WITHIN_2SIGMA,
        "pdg_distance_deg": PDG_DISTANCE_DEG,
        "epistemic_status": (
            "TENSION_PERSISTS unless all three corrected angles fit PDG within 2σ. "
            "The result is reported numerically with no tuned rescue term."
        ),
    }
