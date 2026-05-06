# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""claims/mp_me_ratio — Machine-readable falsification claim.

The proton-to-electron mass ratio m_p/m_e = K_CS²/N_c = 74²/3 ≈ 1825.3 is
a GEOMETRIC PREDICTION of the Unitary Manifold (Pillar 202).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from .claim import (
    FALSIFICATION_CONDITION,
    MP_ME_GEO,
    MP_ME_PDG,
    MP_ME_RESIDUAL_PCT,
    KILL_THRESHOLD_PCT,
    K_CS,
    N_C,
    evaluate_measurement,
)

__all__ = [
    "FALSIFICATION_CONDITION",
    "MP_ME_GEO",
    "MP_ME_PDG",
    "MP_ME_RESIDUAL_PCT",
    "KILL_THRESHOLD_PCT",
    "K_CS",
    "N_C",
    "evaluate_measurement",
]
