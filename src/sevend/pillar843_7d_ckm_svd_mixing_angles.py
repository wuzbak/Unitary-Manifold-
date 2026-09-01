# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 843 — CKM_7D_SVD_MIXING_PARTIAL_CLOSURE

7D flavour-closure proxy built on the Yukawa SVD texture chain.

Honest status
-------------
This is a PARTIAL closure.  The 7D geometry fixes the hierarchical structure:
the discrete torsion sector fixes the CKM CP phase geometrically, while the
fixed-point bulk-mass ladder gives exponentially ordered Yukawa ratios.  The
exact PDG central values still require sub-leading Froggatt-Nielsen / UV
texture input, so this module only claims correct hierarchy and order of
magnitude.
"""
from __future__ import annotations

import math
from typing import Final

from src.sevend.discrete_torsion_cp import DELTA_CP_GEO_RAD

PILLAR_NUMBER: Final[int] = 843
PILLAR_GATE: Final[str] = "CKM_7D_SVD_MIXING_PARTIAL_CLOSURE"

N_W: Final[int] = 5
K_CS: Final[int] = 74
PI_KR: Final[float] = 37.0

THETA_12_PDG_DEG: Final[float] = 13.04
THETA_23_PDG_DEG: Final[float] = 2.36
THETA_13_PDG_DEG: Final[float] = 0.201

LEAN4_THEOREM_COUNT: Final[int] = 25
LEAN4_TOTAL_AFTER: Final[int] = 1976

_C_L_VALUES: Final[tuple[float, float, float]] = (
    1.0 * N_W / K_CS,
    2.0 * N_W / K_CS,
    3.0 * N_W / K_CS,
)
_DELTA_C_12: Final[float] = _C_L_VALUES[1] - _C_L_VALUES[0]
_DELTA_C_23: Final[float] = _C_L_VALUES[2] - _C_L_VALUES[1]
_DELTA_C_13: Final[float] = _C_L_VALUES[2] - _C_L_VALUES[0]


def left_bulk_mass_ladder() -> tuple[float, float, float]:
    """Return the canonical 7D fixed-point LH bulk-mass ladder."""
    return _C_L_VALUES


def yukawa_ratio(delta_c_l: float, pi_kr: float = PI_KR) -> float:
    """Return the SVD-inspired Yukawa eigenvalue ratio exp(-πkR Δc_L)."""
    if delta_c_l <= 0.0:
        raise ValueError("delta_c_l must be positive")
    return math.exp(-pi_kr * delta_c_l)


def mixing_angle_deg(effective_delta_c_l: float, pi_kr: float = PI_KR) -> float:
    """Return a CKM mixing angle in degrees from the proxy ratio.

    We interpret sqrt(y_i / y_j) as the sine of the mixing angle and use
    θ = asin(sqrt(exp(-πkR Δc_L))).  For the 2–3 and 1–3 entries we use the
    cumulative SVD-mismatch suppression appropriate to higher-order sector
    misalignment:

      θ12 : Δ_eff = Δ12
      θ23 : Δ_eff = Δ12 + Δ23
      θ13 : Δ_eff = Δ12 + Δ23 + Δ13
    """
    ratio = yukawa_ratio(effective_delta_c_l, pi_kr=pi_kr)
    return math.degrees(math.asin(math.sqrt(ratio)))


THETA_12_DEG: Final[float] = mixing_angle_deg(_DELTA_C_12)
THETA_23_DEG: Final[float] = mixing_angle_deg(_DELTA_C_12 + _DELTA_C_23)
THETA_13_DEG: Final[float] = mixing_angle_deg(_DELTA_C_12 + _DELTA_C_23 + _DELTA_C_13)
DELTA_CP_DEG: Final[float] = math.degrees(DELTA_CP_GEO_RAD)


def _comparison(theory_deg: float, pdg_deg: float) -> dict[str, float]:
    factor = theory_deg / pdg_deg
    residual = abs(theory_deg - pdg_deg) / pdg_deg
    return {
        "theory_deg": theory_deg,
        "pdg_deg": pdg_deg,
        "residual_fraction": residual,
        "residual_percent": residual * 100.0,
        "factor_vs_pdg": factor,
    }


def ckm_7d_mixing_summary() -> dict[str, object]:
    """Return the machine-readable 7D CKM mixing-angle certificate."""
    c1, c2, c3 = left_bulk_mass_ladder()
    comparisons = {
        "theta_12": _comparison(THETA_12_DEG, THETA_12_PDG_DEG),
        "theta_23": _comparison(THETA_23_DEG, THETA_23_PDG_DEG),
        "theta_13": _comparison(THETA_13_DEG, THETA_13_PDG_DEG),
    }
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "pi_kR": PI_KR,
        "c_l_values": {"c1": c1, "c2": c2, "c3": c3},
        "delta_c_l": {
            "delta_12": _DELTA_C_12,
            "delta_23": _DELTA_C_23,
            "delta_13": _DELTA_C_13,
        },
        "angles_deg": {
            "theta_12": THETA_12_DEG,
            "theta_23": THETA_23_DEG,
            "theta_13": THETA_13_DEG,
            "delta_cp": DELTA_CP_DEG,
        },
        "comparisons": comparisons,
        "hierarchy_correct": THETA_12_DEG > THETA_23_DEG > THETA_13_DEG > 0.0,
        "all_within_factor_two_of_pdg": all(
            0.5 <= comp["factor_vs_pdg"] <= 2.0 for comp in comparisons.values()
        ),
        "epistemic_status": (
            "PARTIAL: geometry fixes CKM ordering and O(1) magnitudes; "
            "sub-leading FN / UV charges still needed for exact PDG centroids."
        ),
        "remaining_open": [
            "CKM_7D_EXACT_ANGLES_OPEN: sub-leading FN charges / UV phases not fixed",
            "CKM_7D_COMPLEX_TEXTURE_OPEN: full complex Yukawa texture still proxy-level",
        ],
        "lean4_theorems": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "THETA_12_DEG",
    "THETA_23_DEG",
    "THETA_13_DEG",
    "THETA_12_PDG_DEG",
    "THETA_23_PDG_DEG",
    "THETA_13_PDG_DEG",
    "DELTA_CP_DEG",
    "PI_KR",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "left_bulk_mass_ladder",
    "yukawa_ratio",
    "mixing_angle_deg",
    "ckm_7d_mixing_summary",
]
