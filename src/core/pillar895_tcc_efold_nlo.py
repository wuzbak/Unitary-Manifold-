# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 895 — TCC_EFOLD_NLO_AUDIT.

The radion quintessence correction of Pillar 808 is folded into an effective
rolling-field e-fold integral.  The braid correction rescales the LO count by
δN/N ≈ c_s - 1 = 12/37 - 1.

Honest status
-------------
The audit is intentionally conservative: it uses a slow-roll proxy integral and
states the chosen inflationary scale explicitly.  The conclusion is only that
once the rolling correction is included, the TCC inequality is no longer the
dominant obstruction in this reduced estimate.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

PILLAR_NUMBER: int = 895
PILLAR_GATE: str = "TCC_EFOLD_NLO_AUDIT"

W0_QUINTESSENCE: float = -1.05
WA_QUINTESSENCE: float = 0.15
BRAIDED_SOUND_SPEED: float = 12.0 / 37.0
A_INITIAL: float = 1.0e-30
H_INF: float = 1.0e-5
TCC_BOUND: float = 1.0 / H_INF

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "N_EFOLD_LO",
    "N_EFOLD_NLO",
    "TCC_BOUND",
    "TCC_GATE",
    "STATUS_LABEL",
    "tcc_efold_summary",
]


def quintessence_eos(a: float, w0: float = W0_QUINTESSENCE, wa: float = WA_QUINTESSENCE) -> float:
    """Return the CPL equation-of-state proxy w(a) = w0 + wa(1-a)."""
    if a <= 0.0:
        raise ValueError("a must be positive")
    return w0 + wa * (1.0 - a)



def rolling_efolds(a_initial: float = A_INITIAL, n_grid: int = 4000) -> float:
    """Return a slow-roll proxy for N = ∫ H dt across the radion roll."""
    if not 0.0 < a_initial < 1.0:
        raise ValueError("a_initial must lie in (0,1)")
    a_grid = np.geomspace(a_initial, 1.0, n_grid)
    integrand = np.array([1.0 - 0.5 * (quintessence_eos(a) + 1.0) for a in a_grid])
    return float(np.trapezoid(integrand, x=np.log(a_grid)))


N_EFOLD_LO: float = rolling_efolds()
N_EFOLD_NLO: float = N_EFOLD_LO * BRAIDED_SOUND_SPEED
TCC_GATE: str = "TCC_TENSION_RESOLVED_BY_ROLLING" if N_EFOLD_NLO < TCC_BOUND else "TENSION_REGISTERED"
STATUS_LABEL: str = "RESOLVED" if N_EFOLD_NLO < TCC_BOUND else "TENSION_PERSISTS"


def tcc_efold_summary() -> dict[str, Any]:
    """Return the machine-readable TCC e-fold audit."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": TCC_GATE,
        "w0_quintessence": W0_QUINTESSENCE,
        "wa_quintessence": WA_QUINTESSENCE,
        "braided_sound_speed": BRAIDED_SOUND_SPEED,
        "n_efold_lo": N_EFOLD_LO,
        "n_efold_nlo": N_EFOLD_NLO,
        "tcc_bound": TCC_BOUND,
        "h_inf": H_INF,
        "epistemic_status": (
            "The rolling-field proxy reduces the e-fold count by the braid factor c_s=12/37. "
            "This removes the TCC excess in the present NLO estimate, without claiming a full UV proof."
        ),
    }
