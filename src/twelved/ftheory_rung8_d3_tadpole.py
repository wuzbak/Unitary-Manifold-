# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 578 — DBP Rung 8: D3-Tadpole Charge Cancellation Consistency.

🔵 ADJACENT TRACK — not hardgate physics.

STATUS: FTHEORY_RUNG8_D3_TADPOLE_CHARGE_CANCELLATION_ADJACENT

This module closes the reference-CY4 tadpole consistency check needed by the
Rung 8 F-theory scaffold.  It is a consistency identity, not a derivation of
the braid invariant k_CS from tadpole physics.
"""

from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "EPISTEMIC_STATUS",
    "VERSION",
    "CY4_CHI",
    "N_D3",
    "K_CS",
    "TADPOLE_RATIO",
    "tadpole_cancellation_check",
    "braid_tadpole_consistency",
    "g4_flux_bound",
    "kill_switch_check",
    "pillar_report",
]

PILLAR_NUMBER: int = 578
PILLAR_STATUS: str = "FTHEORY_RUNG8_D3_TADPOLE_CHARGE_CANCELLATION_ADJACENT"
PILLAR_TITLE: str = "DBP Rung 8: D3-Tadpole Charge Cancellation Consistency"
EPISTEMIC_STATUS: str = "ADJACENT_TRACK"
VERSION: str = "v20.1"

CY4_CHI: int = 1_820_160
N_D3: int = 75_840
K_CS: int = 74
TADPOLE_RATIO: float = 74.0 / 24.0


def tadpole_cancellation_check(
    n_d3: int = N_D3,
    n_flux_units: int = 0,
    chi_cy4: int = CY4_CHI,
) -> Dict[str, object]:
    """Check N_D3 + N_flux = χ(CY4)/24 using the scaffold flux proxy N_flux = n²/2."""
    if n_d3 < 0 or n_flux_units < 0:
        raise ValueError("n_d3 and n_flux_units must be non-negative")
    rhs = chi_cy4 / 24.0
    n_flux = (n_flux_units**2) / 2.0
    lhs = n_d3 + n_flux
    residual = rhs - lhs
    return {
        "check": "tadpole_cancellation_check",
        "chi_over_24": rhs,
        "n_d3": n_d3,
        "n_flux_units": n_flux_units,
        "n_flux_proxy": n_flux,
        "lhs": lhs,
        "residual": residual,
        "exact_reference_identity": (n_d3 * 24 == chi_cy4) and (n_flux_units == 0),
        "pass": abs(residual) < 1e-12,
        "honest_status": "Reference CY4 tadpole verified exactly in the zero-flux limit.",
    }


def braid_tadpole_consistency() -> Dict[str, object]:
    """Check the algebraic compatibility between the braid invariant and tadpole identity."""
    ratio = (K_CS * N_D3) / CY4_CHI
    return {
        "check": "braid_tadpole_consistency",
        "k_cs_times_nd3_over_chi": ratio,
        "expected_ratio": TADPOLE_RATIO,
        "ratio_equals_37_over_12": abs(ratio - (37.0 / 12.0)) < 1e-15,
        "pass": abs(ratio - TADPOLE_RATIO) < 1e-15,
        "honest_status": (
            "The ratio is consistent with the reference CY4 identity, but it does "
            "not derive k_CS from tadpole cancellation."
        ),
    }


def g4_flux_bound(n_flux_units: int = 0) -> Dict[str, object]:
    """Return the reference-CY4 G4-flux capacity under the scaffold proxy."""
    if n_flux_units < 0:
        raise ValueError("n_flux_units must be non-negative")
    tadpole_capacity = CY4_CHI / 24.0
    n_flux_proxy = (n_flux_units**2) / 2.0
    remaining_capacity = tadpole_capacity - n_flux_proxy
    return {
        "check": "g4_flux_bound",
        "n_flux_units": n_flux_units,
        "n_flux_proxy": n_flux_proxy,
        "tadpole_capacity": tadpole_capacity,
        "remaining_capacity_for_d3": remaining_capacity,
        "max_flux_units_proxy": math.isqrt(int(2 * tadpole_capacity)),
        "allowed": remaining_capacity >= 0.0,
        "pass": remaining_capacity >= 0.0,
    }


def kill_switch_check() -> bool:
    """Return True only if the tadpole identity remains an honest consistency check."""
    tadpole = tadpole_cancellation_check()
    braid = braid_tadpole_consistency()
    flux = g4_flux_bound()
    return bool(
        tadpole["pass"]
        and tadpole["exact_reference_identity"]
        and braid["pass"]
        and flux["pass"]
    )


def pillar_report() -> Dict[str, object]:
    """Return the full Pillar 578 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "epistemic_status": EPISTEMIC_STATUS,
        "constants": {
            "cy4_chi": CY4_CHI,
            "n_d3": N_D3,
            "k_cs": K_CS,
            "tadpole_ratio": TADPOLE_RATIO,
        },
        "tadpole_cancellation": tadpole_cancellation_check(),
        "braid_tadpole_consistency": braid_tadpole_consistency(),
        "g4_flux_bound": g4_flux_bound(),
        "kill_switch_pass": kill_switch_check(),
    }
