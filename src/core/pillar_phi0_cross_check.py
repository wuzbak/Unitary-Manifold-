# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Independent φ₀ cross-check using a holographic-boundary route."""

from __future__ import annotations

import math
from typing import Dict

from src.core.phi0_closure import (
    C_S,
    K_CS,
    N_WINDING,
    NS_TARGET,
    phi0_eff_from_ns,
)

BOUNDARY_PERIODICITY_FACTOR: float = 2.0 * math.pi
HOLOGRAPHIC_BOUNDARY_CORRECTION: float = math.sqrt(1.0 + 1.0 / (4.0 * K_CS))


def phi0_from_pillar56() -> float:
    return phi0_eff_from_ns(NS_TARGET, n_winding=N_WINDING)


def phi0_from_holographic_boundary(
    n_winding: int = N_WINDING,
    k_cs: int = K_CS,
) -> float:
    if n_winding <= 0:
        raise ValueError("n_winding must be positive.")
    if k_cs <= 0:
        raise ValueError("k_cs must be positive.")
    correction = math.sqrt(1.0 + 1.0 / (4.0 * k_cs))
    return BOUNDARY_PERIODICITY_FACTOR * n_winding * correction


def phi0_cross_check_relative_error(
    phi0_reference: float | None = None,
    phi0_boundary: float | None = None,
) -> float:
    ref = phi0_reference if phi0_reference is not None else phi0_from_pillar56()
    bdy = phi0_boundary if phi0_boundary is not None else phi0_from_holographic_boundary()
    if ref <= 0:
        raise ValueError("phi0_reference must be positive.")
    return abs(ref - bdy) / ref


def phi0_cross_check_summary() -> Dict[str, object]:
    phi0_ref = phi0_from_pillar56()
    phi0_bdy = phi0_from_holographic_boundary()
    rel_err = phi0_cross_check_relative_error(phi0_reference=phi0_ref, phi0_boundary=phi0_bdy)

    return {
        "n_winding": N_WINDING,
        "k_cs": K_CS,
        "c_s": C_S,
        "phi0_pillar56": phi0_ref,
        "phi0_holographic_boundary": phi0_bdy,
        "relative_error": rel_err,
        "agreement_lt_1pct": rel_err < 0.01,
        "independent_path_note": (
            "Path A uses the Pillar-56 spectral-index inversion; Path B uses the "
            "holographic boundary periodicity with finite-k_cs correction."
        ),
        "remaining_open_note": (
            "This cross-check verifies consistency of two routes; a full holographic"
            " derivation directly from boundary action data remains future work."
        ),
    }


PHI0_CROSS_CHECK_RELATIVE_ERROR: float = phi0_cross_check_relative_error()


__all__ = [
    "BOUNDARY_PERIODICITY_FACTOR",
    "HOLOGRAPHIC_BOUNDARY_CORRECTION",
    "PHI0_CROSS_CHECK_RELATIVE_ERROR",
    "phi0_from_pillar56",
    "phi0_from_holographic_boundary",
    "phi0_cross_check_relative_error",
    "phi0_cross_check_summary",
]
