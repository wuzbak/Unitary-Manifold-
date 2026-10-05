# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 898 — QUARK_MASS_RATIOS_7D_FN.

Quark mass hierarchies are estimated from the FN charge ladders and the 7D warp
suppression via

    mᵢ/mⱼ = ε^|qᵢ-qⱼ| exp[-2(c_L^(i)-c_L^(j)) πkR].

Honest status
-------------
This is an order-of-magnitude audit only.  If the geometric FN+warp hierarchy
overshoots the PDG ratios badly, the mismatch is reported directly as tension.
"""
from __future__ import annotations

import math
from typing import Any

from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import PI_K_R
from src.sevend.pillar887_fn_charge_assignment import (
    FN_CHARGES_DOWN,
    FN_CHARGES_UP,
    FN_EPSILON,
    ORBIFOLD_C_LEFT_DOWN,
    ORBIFOLD_C_LEFT_UP,
)

PILLAR_NUMBER: int = 898
PILLAR_GATE: str = "QUARK_MASS_RATIOS_7D_FN"

PDG_UP_RATIOS: tuple[float, float, float] = (1.0, 550.0, 260000.0)
PDG_DOWN_RATIOS: tuple[float, float, float] = (1.0, 20.0, 1000.0)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "QUARK_UP_RATIOS",
    "QUARK_DOWN_RATIOS",
    "QUARK_RATIOS_GATE",
    "STATUS_LABEL",
    "quark_mass_ratios_summary",
]


def ratio_factor(c_light: float, c_heavy: float, q_light: int, q_heavy: int) -> float:
    """Return the inverse light/heavy hierarchy factor for one pair."""
    return 1.0 / (FN_EPSILON ** abs(q_light - q_heavy) * math.exp(-2.0 * (c_light - c_heavy) * PI_K_R))


QUARK_UP_RATIOS: tuple[float, float, float] = (
    1.0,
    ratio_factor(ORBIFOLD_C_LEFT_UP[0], ORBIFOLD_C_LEFT_UP[1], FN_CHARGES_UP[0], FN_CHARGES_UP[1]),
    ratio_factor(ORBIFOLD_C_LEFT_UP[0], ORBIFOLD_C_LEFT_UP[2], FN_CHARGES_UP[0], FN_CHARGES_UP[2]),
)
QUARK_DOWN_RATIOS: tuple[float, float, float] = (
    1.0,
    ratio_factor(ORBIFOLD_C_LEFT_DOWN[0], ORBIFOLD_C_LEFT_DOWN[1], FN_CHARGES_DOWN[0], FN_CHARGES_DOWN[1]),
    ratio_factor(ORBIFOLD_C_LEFT_DOWN[0], ORBIFOLD_C_LEFT_DOWN[2], FN_CHARGES_DOWN[0], FN_CHARGES_DOWN[2]),
)

UP_WITHIN_FACTOR5 = all(0.2 <= theory / target <= 5.0 for theory, target in zip(QUARK_UP_RATIOS[1:], PDG_UP_RATIOS[1:]))
DOWN_WITHIN_FACTOR5 = all(0.2 <= theory / target <= 5.0 for theory, target in zip(QUARK_DOWN_RATIOS[1:], PDG_DOWN_RATIOS[1:]))
QUARK_RATIOS_GATE: str = "QUARK_MASS_RATIOS_ORDER_OF_MAGNITUDE" if UP_WITHIN_FACTOR5 and DOWN_WITHIN_FACTOR5 else "TENSION"
STATUS_LABEL: str = "PARTIAL" if QUARK_RATIOS_GATE.endswith("MAGNITUDE") else "TENSION_PERSISTS"


def quark_mass_ratios_summary() -> dict[str, Any]:
    """Return the machine-readable quark FN mass-ratio audit."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": QUARK_RATIOS_GATE,
        "quark_up_ratios": list(QUARK_UP_RATIOS),
        "quark_down_ratios": list(QUARK_DOWN_RATIOS),
        "pdg_up_ratios": list(PDG_UP_RATIOS),
        "pdg_down_ratios": list(PDG_DOWN_RATIOS),
        "up_within_factor5": UP_WITHIN_FACTOR5,
        "down_within_factor5": DOWN_WITHIN_FACTOR5,
        "epistemic_status": (
            "The raw FN+warp hierarchy is audited against PDG with no fitted rescue parameter. "
            "Large overshoots remain explicit tension rather than synthetic closure."
        ),
    }
