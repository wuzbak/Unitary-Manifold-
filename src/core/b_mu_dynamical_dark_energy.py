# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""B_μ time-varying coupling audit for dynamical dark energy (AL-3 route)."""

from __future__ import annotations

import math
from typing import Callable, Dict

from src.core.de_equation_of_state_desi import DESI_DR2_WA

GAMMA0: float = 1.0
DESI_TARGET_WA: float = float(DESI_DR2_WA)  # ~ -0.55
WA_FIT_TOLERANCE: float = 0.2


def gamma_model_scaling(a: float, gamma0: float = GAMMA0) -> float:
    return gamma0 / max(a, 1e-12)


def gamma_model_powerlaw(a: float, n: float = -0.5, gamma0: float = GAMMA0) -> float:
    return gamma0 * (max(a, 1e-12) ** n)


def gamma_model_logarithmic(a: float, gamma0: float = GAMMA0) -> float:
    # Positive-definite logarithmic modulation on (0,1]
    return gamma0 / (1.0 + 0.3 * (0.0 if a <= 0 else math.log1p(1.0 / max(a, 1e-12))))


def _effective_wa_from_gamma_family(gamma_fn: Callable[[float], float]) -> float:
    """Estimate a w_a proxy from local logarithmic slope dlnΓ/dlna near a=1.

    Modeling assumption used in this lane: near the present epoch, the effective
    CPL-like slope parameter tracks the local Γ(a) logarithmic slope. This is a
    proxy identification, not a first-principles derivation.
    """
    a0, a1 = 0.8, 1.0
    g0 = max(gamma_fn(a0), 1e-16)
    g1 = max(gamma_fn(a1), 1e-16)
    return math.log(g1 / g0) / math.log(a1 / a0)


def evaluate_gamma_models_for_wa() -> Dict[str, object]:
    """Evaluate candidate Γ(a) families against DESI DR2 w_a target."""
    candidates = {
        "scaling_1_over_a": _effective_wa_from_gamma_family(gamma_model_scaling),
        "powerlaw_n_-0.5": _effective_wa_from_gamma_family(lambda a: gamma_model_powerlaw(a, n=-0.5)),
        "logarithmic": _effective_wa_from_gamma_family(gamma_model_logarithmic),
    }
    best_name = min(candidates, key=lambda k: abs(candidates[k] - DESI_TARGET_WA))
    best_wa = candidates[best_name]
    return {
        "target_wa": DESI_TARGET_WA,
        "candidates": candidates,
        "candidate_parameters": {
            "scaling_1_over_a": {"type": "gamma0/a"},
            "powerlaw_n_-0.5": {"type": "gamma0*a^n", "n": -0.5},
            "logarithmic": {"type": "gamma0/(1+0.3*log(1+1/a))"},
        },
        "best_model": best_name,
        "best_wa": best_wa,
        "best_abs_error": abs(best_wa - DESI_TARGET_WA),
        "status": "FITTED",
        "epistemic_note": (
            "Mechanism Γ(t)→w_a≠0 is framework-derived at action level; reported "
            "w_a values are slope-based proxies. Specific matching functional form "
            "and proxy-to-observable map remain FITTED until compactification "
            "dynamics derive them."
        ),
        "falsification": (
            "FAIL if no geometrically motivated Γ(a) family enters DESI DR2-preferred w_a band."
        ),
    }
