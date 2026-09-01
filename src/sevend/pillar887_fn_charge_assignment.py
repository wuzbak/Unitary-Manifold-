# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 887 — FN_CHARGE_ASSIGNMENT_FROM_7D_MONODROMY.

Froggatt-Nielsen charge ladders are assigned from the T²/Z₂ orbifold monodromy
by rounding the geometric left-handed localisation data qᵢ = round(n_w c_L^(i)).
The four fixed points y = 0, πR, π, π+πR define the discrete monodromy sectors,
and the heaviest generation is required to carry the smallest non-negative
charge.  The resulting charge differences determine the overlap suppressions
ε^|Δqᵢⱼ| with ε identified with the Wolfenstein λ parameter.

Honest status
-------------
The charge ladders are fixed here as an executable monodromy assignment.  This
closes the bookkeeping problem of how FN suppressions are attached to the 7D
geometry, but it does not by itself guarantee phenomenological agreement for
mixing angles or mass ratios downstream.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import N_W

PILLAR_NUMBER: int = 887
PILLAR_GATE: str = "FN_CHARGE_ASSIGNMENT_FROM_7D_MONODROMY"
STATUS_LABEL: str = "RESOLVED"

FN_EPSILON: float = 0.2253
FIXED_POINTS_T2Z2: tuple[str, ...] = ("0", "πR", "π", "π+πR")

ORBIFOLD_C_LEFT_UP: tuple[float, float, float] = (0.8, 0.4, 0.0)
ORBIFOLD_C_LEFT_DOWN: tuple[float, float, float] = (1.0, 0.8, 0.6)
ORBIFOLD_C_LEFT_LEPTON: tuple[float, float, float] = (0.8, 0.6, 0.4)
ORBIFOLD_C_LEFT_NEUTRINO: tuple[float, float, float] = (0.4, 0.2, 0.0)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "STATUS_LABEL",
    "FN_EPSILON",
    "FIXED_POINTS_T2Z2",
    "FN_CHARGES_UP",
    "FN_CHARGES_DOWN",
    "FN_CHARGES_LEPTON",
    "FN_CHARGES_NEUTRINO",
    "charge_differences",
    "fn_suppression_matrix",
    "fn_charge_summary",
]


def _charges_from_c(c_values: tuple[float, float, float], n_w: int = N_W) -> tuple[int, int, int]:
    if len(c_values) != 3:
        raise ValueError("c_values must have length 3")
    charges = tuple(int(round(n_w * c_value)) for c_value in c_values)
    if not (charges[0] > charges[1] > charges[2] >= 0):
        raise ValueError("FN charges must satisfy q1 > q2 > q3 >= 0")
    return charges


def charge_differences(charges: tuple[int, int, int]) -> dict[str, int]:
    """Return the generation-wise FN charge differences Δqᵢⱼ."""
    if len(charges) != 3:
        raise ValueError("charges must have length 3")
    return {
        "dq12": charges[0] - charges[1],
        "dq13": charges[0] - charges[2],
        "dq23": charges[1] - charges[2],
    }


FN_CHARGES_UP: tuple[int, int, int] = _charges_from_c(ORBIFOLD_C_LEFT_UP)
FN_CHARGES_DOWN: tuple[int, int, int] = _charges_from_c(ORBIFOLD_C_LEFT_DOWN)
FN_CHARGES_LEPTON: tuple[int, int, int] = _charges_from_c(ORBIFOLD_C_LEFT_LEPTON)
FN_CHARGES_NEUTRINO: tuple[int, int, int] = _charges_from_c(ORBIFOLD_C_LEFT_NEUTRINO)


def fn_suppression_matrix(
    charges: tuple[int, int, int] = FN_CHARGES_DOWN,
    epsilon: float = FN_EPSILON,
) -> np.ndarray:
    """Return the symmetric FN suppression matrix ε^|Δqᵢⱼ|."""
    if len(charges) != 3:
        raise ValueError("charges must have length 3")
    if not 0.0 < epsilon < 1.0:
        raise ValueError("epsilon must lie in (0, 1)")
    return np.array(
        [[epsilon ** abs(charges[i] - charges[j]) for j in range(3)] for i in range(3)],
        dtype=float,
    )


def fn_charge_summary() -> dict[str, Any]:
    """Return the machine-readable FN charge assignment certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "n_w": N_W,
        "fixed_points_t2z2": list(FIXED_POINTS_T2Z2),
        "fn_epsilon": FN_EPSILON,
        "charges": {
            "up": list(FN_CHARGES_UP),
            "down": list(FN_CHARGES_DOWN),
            "lepton": list(FN_CHARGES_LEPTON),
            "neutrino": list(FN_CHARGES_NEUTRINO),
        },
        "charge_differences": {
            "up": charge_differences(FN_CHARGES_UP),
            "down": charge_differences(FN_CHARGES_DOWN),
            "lepton": charge_differences(FN_CHARGES_LEPTON),
            "neutrino": charge_differences(FN_CHARGES_NEUTRINO),
        },
        "suppression_matrices": {
            "up": fn_suppression_matrix(FN_CHARGES_UP).tolist(),
            "down": fn_suppression_matrix(FN_CHARGES_DOWN).tolist(),
            "lepton": fn_suppression_matrix(FN_CHARGES_LEPTON).tolist(),
            "neutrino": fn_suppression_matrix(FN_CHARGES_NEUTRINO).tolist(),
        },
        "epistemic_status": (
            "RESOLVED bookkeeping layer: the 7D monodromy now attaches explicit FN "
            "charge ladders and suppression factors to every flavour sector."
        ),
    }
