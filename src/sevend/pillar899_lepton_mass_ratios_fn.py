# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 899 — LEPTON_MASS_RATIOS_7D_FN.

Charged-lepton hierarchies are estimated with the same FN+warp ratio formula
used for the quark sector, now applied to the lepton monodromy charges.

Honest status
-------------
This pillar reports whether the geometric hierarchy reaches order-of-magnitude
agreement only.  Failure to do so is preserved as tension.
"""
from __future__ import annotations

import math
from typing import Any

from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import PI_K_R
from src.sevend.pillar887_fn_charge_assignment import FN_CHARGES_LEPTON, FN_EPSILON, ORBIFOLD_C_LEFT_LEPTON

PILLAR_NUMBER: int = 899
PILLAR_GATE: str = "LEPTON_MASS_RATIOS_7D_FN"

PDG_LEPTON_RATIOS: tuple[float, float, float] = (1.0, 207.0, 3477.0)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEPTON_RATIOS",
    "LEPTON_RATIOS_GATE",
    "STATUS_LABEL",
    "lepton_mass_ratios_summary",
]


def ratio_factor(c_light: float, c_heavy: float, q_light: int, q_heavy: int) -> float:
    """Return the inverse light/heavy hierarchy factor for one lepton pair."""
    return 1.0 / (FN_EPSILON ** abs(q_light - q_heavy) * math.exp(-2.0 * (c_light - c_heavy) * PI_K_R))


LEPTON_RATIOS: tuple[float, float, float] = (
    1.0,
    ratio_factor(ORBIFOLD_C_LEFT_LEPTON[0], ORBIFOLD_C_LEFT_LEPTON[1], FN_CHARGES_LEPTON[0], FN_CHARGES_LEPTON[1]),
    ratio_factor(ORBIFOLD_C_LEFT_LEPTON[0], ORBIFOLD_C_LEFT_LEPTON[2], FN_CHARGES_LEPTON[0], FN_CHARGES_LEPTON[2]),
)
LEPTON_RATIOS_GATE: str = (
    "LEPTON_MASS_RATIOS_ORDER_OF_MAGNITUDE"
    if all(0.2 <= theory / target <= 5.0 for theory, target in zip(LEPTON_RATIOS[1:], PDG_LEPTON_RATIOS[1:]))
    else "TENSION"
)
STATUS_LABEL: str = "PARTIAL" if LEPTON_RATIOS_GATE.endswith("MAGNITUDE") else "TENSION_PERSISTS"


def lepton_mass_ratios_summary() -> dict[str, Any]:
    """Return the machine-readable charged-lepton mass-ratio audit."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": LEPTON_RATIOS_GATE,
        "lepton_ratios": list(LEPTON_RATIOS),
        "pdg_lepton_ratios": list(PDG_LEPTON_RATIOS),
        "within_factor5": all(0.2 <= theory / target <= 5.0 for theory, target in zip(LEPTON_RATIOS[1:], PDG_LEPTON_RATIOS[1:])),
        "ratio_span": LEPTON_RATIOS[2] / LEPTON_RATIOS[1],
        "epistemic_status": (
            "The geometric charged-lepton hierarchy is compared to PDG without tuning. "
            "Any severe mismatch remains a registered tension."
        ),
    }
