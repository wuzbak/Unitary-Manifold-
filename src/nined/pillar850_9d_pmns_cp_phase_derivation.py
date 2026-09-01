# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 850 — PMNS_CP_9D_PARTIAL_DERIVATION

9D partial derivation of the leptonic Dirac CP phase.

Honest status
-------------
This is PARTIAL.  The torsion structure fixes the phase branch, while the
seesaw correction remains model-dependent.  The prompt-level arithmetic points
to the supplementary Z₃ branch (ε=2, raw phase 4π/3), which after the seesaw
suppression lands near the PDG central value ~197°.
"""
from __future__ import annotations

import math
from typing import Final

from src.sevend.discrete_torsion_cp import PHI_HOLONOMY_RAD

PILLAR_NUMBER: Final[int] = 850
PILLAR_GATE: Final[str] = "PMNS_CP_9D_PARTIAL_DERIVATION"

DM21_EV2: Final[float] = 7.42e-5
DM31_EV2: Final[float] = 2.51e-3
LEPTON_TORSION_BRANCH_RAD: Final[float] = 2.0 * PHI_HOLONOMY_RAD

SEESAW_CORRECTION: Final[float] = math.sqrt(DM21_EV2 / DM31_EV2)
_DELTA_PMNS_GEO_RAD: Final[float] = LEPTON_TORSION_BRANCH_RAD * (1.0 - SEESAW_CORRECTION)
DELTA_PMNS_GEO_DEG: Final[float] = math.degrees(_DELTA_PMNS_GEO_RAD)

DELTA_PMNS_PDG_DEG: Final[float] = 197.0
DELTA_PMNS_PDG_ERR_DEG: Final[float] = 25.0
IN_PDG_1SIGMA: Final[bool] = (
    abs(DELTA_PMNS_GEO_DEG - DELTA_PMNS_PDG_DEG) <= DELTA_PMNS_PDG_ERR_DEG
)

LEAN4_THEOREM_COUNT: Final[int] = 20
LEAN4_TOTAL_AFTER: Final[int] = 2046


def seesaw_correction() -> float:
    """Return sqrt(Δm²21 / Δm²31)."""
    return SEESAW_CORRECTION


def pmns_cp_phase_deg() -> float:
    """Return the 9D geometric PMNS CP phase in degrees."""
    return DELTA_PMNS_GEO_DEG


def pmns_cp_9d_summary() -> dict[str, object]:
    """Return the machine-readable 9D PMNS CP certificate."""
    residual_deg = abs(DELTA_PMNS_GEO_DEG - DELTA_PMNS_PDG_DEG)
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "lepton_torsion_branch_deg": math.degrees(LEPTON_TORSION_BRANCH_RAD),
        "seesaw_correction": SEESAW_CORRECTION,
        "delta_pmns_geo_deg": DELTA_PMNS_GEO_DEG,
        "delta_pmns_pdg_deg": DELTA_PMNS_PDG_DEG,
        "delta_pmns_pdg_err_deg": DELTA_PMNS_PDG_ERR_DEG,
        "residual_deg": residual_deg,
        "in_pdg_1sigma": IN_PDG_1SIGMA,
        "epistemic_status": (
            "PARTIAL: torsion branch fixed geometrically, seesaw factor remains "
            "model-dependent even though the central value lands within PDG 1σ."
        ),
        "remaining_open": [
            "PMNS_CP_9D_SEESAW_MODEL_OPEN: exact correction factor not uniquely fixed",
            "PMNS_CP_9D_FULL_TEXTURE_OPEN: full lepton texture derivation remains open",
        ],
        "lean4_theorems": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "DELTA_PMNS_GEO_DEG",
    "DELTA_PMNS_PDG_DEG",
    "DELTA_PMNS_PDG_ERR_DEG",
    "SEESAW_CORRECTION",
    "IN_PDG_1SIGMA",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "seesaw_correction",
    "pmns_cp_phase_deg",
    "pmns_cp_9d_summary",
]
