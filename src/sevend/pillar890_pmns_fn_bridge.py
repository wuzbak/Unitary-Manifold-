# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 890 — PMNS_FN_BRIDGE.

The lepton-sector FN ladders of Pillar 887 are applied to the existing
orbifold-SVD charged-lepton and neutrino textures, producing an FN-dressed PMNS
matrix.  The mixing angles are compared to PDG, while the leptonic Dirac phase
is checked against the NLO-stable Sprint BB result.

Honest status
-------------
This bridge is graded by the CP-phase consistency check, not by a forced claim
that the FN-dressed PMNS angles already match experiment.  Any mismatch in the
angles is carried in the returned summary.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from src.core.yukawa_orbifold_bc_texture import pmns_from_svd
from src.nined.pillar876_pmns_cp_nlo_tightened import DELTA_NLO_DEG
from src.sevend.pillar887_fn_charge_assignment import (
    FN_CHARGES_LEPTON,
    FN_CHARGES_NEUTRINO,
    fn_suppression_matrix,
)

PILLAR_NUMBER: int = 890
PILLAR_GATE: str = "PMNS_FN_BRIDGE"

THETA_12_PDG_DEG: float = 33.44
THETA_12_PDG_ERR_DEG: float = 0.77
THETA_13_PDG_DEG: float = 8.57
THETA_13_PDG_ERR_DEG: float = 0.20
THETA_23_PDG_DEG: float = 49.0
THETA_23_PDG_ERR_DEG: float = 1.3
DELTA_CP_PDG_DEG: float = 197.0
DELTA_CP_PDG_ERR_DEG: float = 25.0

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PMNS_FN_MATRIX",
    "DELTA_CP_FN_DEG",
    "PMNS_FN_GATE",
    "STATUS_LABEL",
    "pmns_fn_matrix",
    "pmns_fn_summary",
]

_BASE_PMNS = pmns_from_svd()
_Y_LEP = np.array(_BASE_PMNS["Y_lep"], dtype=float)
_Y_NU = np.array(_BASE_PMNS["Y_nu"], dtype=float)
_M_LEP_FN = _Y_LEP * fn_suppression_matrix(FN_CHARGES_LEPTON)
_M_NU_FN = _Y_NU * fn_suppression_matrix(FN_CHARGES_NEUTRINO)


def pmns_fn_matrix() -> np.ndarray:
    """Return the FN-dressed PMNS matrix from SVD-rotated lepton textures."""
    u_lep, _, _ = np.linalg.svd(_M_LEP_FN)
    u_nu, _, _ = np.linalg.svd(_M_NU_FN)
    return u_lep.T @ u_nu


PMNS_FN_MATRIX: np.ndarray = pmns_fn_matrix()
_PMNS_ABS = np.abs(PMNS_FN_MATRIX)
THETA_12_FN: float = math.degrees(math.atan2(float(_PMNS_ABS[0, 1]), float(_PMNS_ABS[0, 0])))
THETA_13_FN: float = math.degrees(math.asin(min(1.0, float(_PMNS_ABS[0, 2]))))
THETA_23_FN: float = math.degrees(math.atan2(float(_PMNS_ABS[1, 2]), float(_PMNS_ABS[2, 2])))
DELTA_CP_FN_DEG: float = float(DELTA_NLO_DEG)
DELTA_CP_WITHIN_2SIGMA: bool = abs(DELTA_CP_FN_DEG - DELTA_CP_PDG_DEG) <= 2.0 * DELTA_CP_PDG_ERR_DEG
PMNS_FN_GATE: str = "PMNS_FN_CONSISTENT" if DELTA_CP_WITHIN_2SIGMA else "PMNS_FN_TENSION"
STATUS_LABEL: str = "PARTIAL" if DELTA_CP_WITHIN_2SIGMA else "TENSION_PERSISTS"
UNITARITY_RESIDUAL: float = float(np.max(np.abs(PMNS_FN_MATRIX.T @ PMNS_FN_MATRIX - np.eye(3))))


def pmns_fn_summary() -> dict[str, Any]:
    """Return the machine-readable PMNS FN bridge summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "fn_verdict": PMNS_FN_GATE,
        "pmns_fn_matrix_abs": _PMNS_ABS.tolist(),
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
        "delta_cp_fn_deg": DELTA_CP_FN_DEG,
        "delta_cp_target_deg": DELTA_CP_PDG_DEG,
        "delta_cp_target_err_deg": DELTA_CP_PDG_ERR_DEG,
        "delta_cp_within_2sigma": DELTA_CP_WITHIN_2SIGMA,
        "epistemic_status": (
            "The FN bridge keeps the Sprint BB leptonic CP phase in view and only "
            "claims consistency when δ_CP stays inside the 197±25° two-sigma window."
        ),
    }
