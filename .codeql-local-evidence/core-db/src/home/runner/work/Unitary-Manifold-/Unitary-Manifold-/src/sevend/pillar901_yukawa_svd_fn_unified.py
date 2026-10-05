# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 901 — YUKAWA_SVD_FN_UNIFIED.

This synthesis compares the older orbifold-SVD flavour textures against the new
FN-dressed matrices.  The relevant question is not whether every observable is
already perfect, but whether the FN layer moves the quark sector closer to PDG
without hiding remaining lepton-sector tension.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from src.core.yukawa_orbifold_bc_texture import ckm_from_svd, pmns_from_svd
from src.sevend.pillar888_ckm_7d_fn_correction import CKM_FN_MATRIX, THETA_12_FN, THETA_13_FN, THETA_23_FN
from src.sevend.pillar890_pmns_fn_bridge import PMNS_FN_MATRIX

PILLAR_NUMBER: int = 901
PILLAR_GATE: str = "YUKAWA_SVD_FN_UNIFIED"

PDG_CKM: tuple[float, float, float] = (13.04, 0.201, 2.38)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "CKM_FN_UNIFIED",
    "PMNS_FN_UNIFIED",
    "YUKAWA_UNIFIED_GATE",
    "STATUS_LABEL",
    "yukawa_svd_fn_summary",
]

_BASE_CKM = ckm_from_svd()
_BASE_PMNS = pmns_from_svd()
CKM_FN_UNIFIED: np.ndarray = CKM_FN_MATRIX
PMNS_FN_UNIFIED: np.ndarray = PMNS_FN_MATRIX
BASE_CKM_DISTANCE: float = sum(abs(_BASE_CKM[f"theta_{index}_deg"] - target) for index, target in zip((12, 13, 23), PDG_CKM))
FN_CKM_DISTANCE: float = sum(abs(angle - target) for angle, target in zip((THETA_12_FN, THETA_13_FN, THETA_23_FN), PDG_CKM))
YUKAWA_UNIFIED_GATE: str = "FN_IMPROVES_CKM" if FN_CKM_DISTANCE < BASE_CKM_DISTANCE else "FN_DOES_NOT_IMPROVE_CKM"
STATUS_LABEL: str = "PARTIAL" if FN_CKM_DISTANCE < BASE_CKM_DISTANCE else "TENSION_PERSISTS"


def yukawa_svd_fn_summary() -> dict[str, Any]:
    """Return the machine-readable Yukawa/FN synthesis summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": YUKAWA_UNIFIED_GATE,
        "ckm_svd_status": _BASE_CKM["status"],
        "pmns_svd_status": _BASE_PMNS["status"],
        "base_ckm_distance": BASE_CKM_DISTANCE,
        "fn_ckm_distance": FN_CKM_DISTANCE,
        "ckm_fn_unified_abs": np.abs(CKM_FN_UNIFIED).tolist(),
        "pmns_fn_unified_abs": np.abs(PMNS_FN_UNIFIED).tolist(),
        "epistemic_status": (
            "The FN layer is treated as an incremental synthesis step.  Improvement in CKM distance is reported, "
            "while any remaining PMNS-angle mismatch stays visible."
        ),
    }
