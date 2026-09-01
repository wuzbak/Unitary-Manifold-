# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 864 — JARLSKOG_INVARIANT_7D_COMPUTED

Parameter-free Jarlskog invariant from the 7D geometry.

The complex CKM matrix is reconstructed in the standard PDG parametrisation
from the Pillar 862 mixing angles and the Pillar 863 torsion CP phase, and the
Jarlskog invariant is then evaluated directly as

    J = Im(V_us · V_cb · V_ub* · V_cs*).

The rephasing-invariant identity

    J = c₁₂ c₂₃ c₁₃² s₁₂ s₂₃ s₁₃ sin δ

is used as an independent cross-check of the numerical evaluation.

Honest status
-------------
COMPUTED, not closed.  Because θ₁₃ and θ₂₃ are in tension (Pillar 862), the
resulting J inherits those tensions.  The sign and the order of magnitude are
correct; the magnitude ratio against PDG is reported explicitly and is not
absorbed into a fudge factor.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from src.sevend.pillar862_ckm_7d_mixing_angles import (
    THETA_12_DEG,
    THETA_13_DEG,
    THETA_23_DEG,
)
from src.sevend.pillar863_cp_violation_7d_torsion import DELTA_CP_NLO_RAD

PILLAR_NUMBER: int = 864
PILLAR_GATE: str = "JARLSKOG_INVARIANT_7D_COMPUTED"

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 2276
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

J_PDG: float = 3.08e-5
J_PDG_ERR: float = 0.15e-5

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "J_PDG",
    "J_PDG_ERR",
    "J_7D",
    "J_IDENTITY",
    "J_RATIO_VS_PDG",
    "J_TENSION_SIGMA",
    "J_SIGN_CORRECT",
    "J_ORDER_OF_MAGNITUDE_WITHIN_TEN",
    "REMAINING_OPEN",
    "ckm_complex_matrix",
    "jarlskog_from_matrix",
    "jarlskog_identity",
    "jarlskog_invariant_7d_summary",
]

REMAINING_OPEN: list[str] = [
    "JARLSKOG_7D_ANGLE_TENSION_OPEN: J inherits the θ₁₃/θ₂₃ tensions of Pillar 862.",
    "JARLSKOG_7D_PHASE_CONVENTION_OPEN: only the Dirac phase is included; "
    "Majorana-type phases play no role in the quark sector but are not audited here.",
]


def ckm_complex_matrix(
    theta_12_deg: float = THETA_12_DEG,
    theta_13_deg: float = THETA_13_DEG,
    theta_23_deg: float = THETA_23_DEG,
    delta_rad: float = DELTA_CP_NLO_RAD,
) -> np.ndarray:
    """Return the complex CKM matrix in the standard PDG parametrisation."""
    s12, c12 = math.sin(math.radians(theta_12_deg)), math.cos(math.radians(theta_12_deg))
    s13, c13 = math.sin(math.radians(theta_13_deg)), math.cos(math.radians(theta_13_deg))
    s23, c23 = math.sin(math.radians(theta_23_deg)), math.cos(math.radians(theta_23_deg))
    phase = complex(math.cos(delta_rad), math.sin(delta_rad))
    return np.array(
        [
            [c12 * c13, s12 * c13, s13 * phase.conjugate()],
            [
                -s12 * c23 - c12 * s23 * s13 * phase,
                c12 * c23 - s12 * s23 * s13 * phase,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * phase,
                -c12 * s23 - s12 * c23 * s13 * phase,
                c23 * c13,
            ],
        ],
        dtype=complex,
    )


def jarlskog_from_matrix(v: np.ndarray | None = None) -> float:
    """Return J = Im(V_us V_cb V_ub* V_cs*) from a complex CKM matrix."""
    matrix = ckm_complex_matrix() if v is None else v
    if matrix.shape != (3, 3):
        raise ValueError("CKM matrix must be 3×3")
    v_us = matrix[0, 1]
    v_cb = matrix[1, 2]
    v_ub = matrix[0, 2]
    v_cs = matrix[1, 1]
    return float(np.imag(v_us * v_cb * np.conj(v_ub) * np.conj(v_cs)))


def jarlskog_identity(
    theta_12_deg: float = THETA_12_DEG,
    theta_13_deg: float = THETA_13_DEG,
    theta_23_deg: float = THETA_23_DEG,
    delta_rad: float = DELTA_CP_NLO_RAD,
) -> float:
    """Return J from the rephasing-invariant trigonometric identity."""
    t12, t13, t23 = (
        math.radians(theta_12_deg),
        math.radians(theta_13_deg),
        math.radians(theta_23_deg),
    )
    return (
        math.cos(t12)
        * math.cos(t23)
        * math.cos(t13) ** 2
        * math.sin(t12)
        * math.sin(t23)
        * math.sin(t13)
        * math.sin(delta_rad)
    )


CKM_COMPLEX: np.ndarray = ckm_complex_matrix()
J_7D: float = jarlskog_from_matrix(CKM_COMPLEX)
J_IDENTITY: float = jarlskog_identity()
J_RATIO_VS_PDG: float = J_7D / J_PDG
J_TENSION_SIGMA: float = abs(J_7D - J_PDG) / J_PDG_ERR
J_SIGN_CORRECT: bool = J_7D > 0.0
J_ORDER_OF_MAGNITUDE_WITHIN_TEN: bool = 0.1 <= abs(J_RATIO_VS_PDG) <= 10.0
IDENTITY_CROSS_CHECK_OK: bool = abs(J_7D - J_IDENTITY) < 1e-12


def jarlskog_invariant_7d_summary() -> dict[str, Any]:
    """Return the machine-readable Jarlskog certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "angles_deg": {
            "theta_12": THETA_12_DEG,
            "theta_13": THETA_13_DEG,
            "theta_23": THETA_23_DEG,
        },
        "delta_cp_rad": DELTA_CP_NLO_RAD,
        "j_7d": J_7D,
        "j_identity": J_IDENTITY,
        "identity_cross_check_ok": IDENTITY_CROSS_CHECK_OK,
        "j_pdg": J_PDG,
        "j_pdg_err": J_PDG_ERR,
        "j_ratio_vs_pdg": J_RATIO_VS_PDG,
        "j_tension_sigma": J_TENSION_SIGMA,
        "j_sign_correct": J_SIGN_CORRECT,
        "j_order_of_magnitude_within_ten": J_ORDER_OF_MAGNITUDE_WITHIN_TEN,
        "parameter_free": True,
        "epistemic_status": (
            "COMPUTED: J is obtained with no free parameters, but it inherits the "
            "Pillar 862 angle tensions; the magnitude ratio against PDG is reported "
            "rather than tuned away."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
