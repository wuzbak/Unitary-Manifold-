# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 889 — JARLSKOG_7D_NLO_FN.

The FN-corrected CKM mixing angles of Pillar 888 are combined with the 7D
discrete-torsion CP phase to evaluate the Jarlskog invariant via the explicit
four-index definition J = Im(V_ud V_cs V_us* V_cd*).

Honest status
-------------
The Jarlskog magnitude is only upgraded if the FN-corrected value comes within
a factor of two of the PDG benchmark.  Otherwise the sign and direction of any
improvement are reported while the magnitude gap remains open.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from src.sevend.pillar863_cp_violation_7d_torsion import DELTA_CP_NLO_RAD
from src.sevend.pillar864_jarlskog_invariant_7d import J_PDG, J_PDG_ERR
from src.sevend.pillar888_ckm_7d_fn_correction import THETA_12_FN, THETA_13_FN, THETA_23_FN

PILLAR_NUMBER: int = 889
PILLAR_GATE: str = "JARLSKOG_7D_NLO_FN"

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "J_FN",
    "J_PDG",
    "RATIO_J_FN_VS_PDG",
    "JARLSKOG_GATE",
    "STATUS_LABEL",
    "ckm_fn_complex_matrix",
    "jarlskog_invariant",
    "jarlskog_fn_summary",
]


def ckm_fn_complex_matrix(
    theta_12_deg: float = THETA_12_FN,
    theta_13_deg: float = THETA_13_FN,
    theta_23_deg: float = THETA_23_FN,
    delta_rad: float = DELTA_CP_NLO_RAD,
) -> np.ndarray:
    """Return the FN-corrected complex CKM matrix in the PDG parametrisation."""
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


def jarlskog_invariant(v_ckm: np.ndarray | None = None) -> float:
    """Return J = Im(V_ud V_cs V_us* V_cd*)."""
    matrix = ckm_fn_complex_matrix() if v_ckm is None else v_ckm
    if matrix.shape != (3, 3):
        raise ValueError("v_ckm must be 3x3")
    return float(np.imag(matrix[0, 0] * matrix[1, 1] * np.conj(matrix[0, 1]) * np.conj(matrix[1, 0])))


CKM_FN_COMPLEX: np.ndarray = ckm_fn_complex_matrix()
J_FN: float = jarlskog_invariant(CKM_FN_COMPLEX)
RATIO_J_FN_VS_PDG: float = J_FN / J_PDG
J_TENSION_SIGMA: float = abs(J_FN - J_PDG) / J_PDG_ERR
JARLSKOG_GATE: str = "JARLSKOG_7D_NLO_FN_IMPROVED" if abs(RATIO_J_FN_VS_PDG - 1.0) < 0.5 else "MAGNITUDE_OPEN"
STATUS_LABEL: str = "PARTIAL" if JARLSKOG_GATE.endswith("IMPROVED") else "TENSION_PERSISTS"


def jarlskog_fn_summary() -> dict[str, Any]:
    """Return the machine-readable FN-corrected Jarlskog summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "fn_verdict": JARLSKOG_GATE,
        "j_fn": J_FN,
        "j_pdg": J_PDG,
        "ratio_j_fn_vs_pdg": RATIO_J_FN_VS_PDG,
        "j_tension_sigma": J_TENSION_SIGMA,
        "angles_deg": {
            "theta_12": THETA_12_FN,
            "theta_13": THETA_13_FN,
            "theta_23": THETA_23_FN,
        },
        "delta_cp_deg": math.degrees(DELTA_CP_NLO_RAD),
        "sign_correct": J_FN > 0.0,
        "epistemic_status": (
            "FN-corrected J is reported with the explicit four-index invariant. "
            "Magnitude improvement is only claimed when it lands within a factor of two of PDG."
        ),
    }
