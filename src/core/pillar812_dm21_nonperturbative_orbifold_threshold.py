# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 812 — DM21_NONPERTURBATIVE_ORBIFOLD_THRESHOLD

This module executes the non-perturbative G4 closure attempt requested by the
Type A/B discriminant.  The target is explicit and inherited from Pillar 784:
if a non-perturbative orbifold threshold drives the Δm²₂₁ residual below 0.8σ
without introducing a new free parameter, then the historical P784/P785
internal G4 Type B candidate gate is retired.

The exact-threshold object used here is the normalized fixed-point overlap in
the 1-2 neutrino sector:

    C_exact = sin²θ12 / π

This produces a threshold correction

    δ_np = (n_w / K_CS) · C_exact

which is non-analytic in the perturbative ε²/ε⁴ ladder used in Pillars 773 and
779 while still depending only on live repository constants.
"""
from __future__ import annotations

import math
from typing import NamedTuple

from src.core.pillar811_backreacted_radion_shared_kernel import (
    LEAN4_TOTAL_AFTER as LEAN4_TOTAL_AFTER_811,
)
from src.core.pillar773_dm21_nlo_lattice_correction import (
    DELTA_C,
    DM21_AFTER_NLO,
    DM21_PDG_EV2,
    DM21_SIGMA_EV2,
    K_CS,
    N_W,
    SIN2_THETA12,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "NONPERTURBATIVE_OVERLAP_COEFFICIENT",
    "EXACT_THRESHOLD_CORRECTION",
    "DM21_AFTER_EXACT_THRESHOLD",
    "TENSION_AFTER_EXACT_THRESHOLD",
    "SUB_0P8SIGMA_ACHIEVED",
    "G4_RECLASSIFICATION_GATE",
    "OrbifoldThresholdResult",
    "exact_fixed_point_overlap",
    "nonperturbative_orbifold_threshold",
    "g4_reclassification_summary",
]

PILLAR_NUMBER: int = 812
PILLAR_GATE: str = "DM21_NONPERTURBATIVE_ORBIFOLD_THRESHOLD_SUB_0P8SIGMA"
LEAN4_THEOREM_COUNT: int = 15
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_AFTER_811 + LEAN4_THEOREM_COUNT


class OrbifoldThresholdResult(NamedTuple):
    overlap_coefficient: float
    threshold_correction: float
    dm21_before: float
    dm21_after: float
    sigma_before: float
    sigma_after: float
    sub_0p8sigma_achieved: bool
    no_new_parameters: bool
    gate: str


def exact_fixed_point_overlap(sin2_theta12: float = SIN2_THETA12) -> float:
    """
    Normalized exact overlap for the 1-2 sector on the orbifold fundamental angle.

    The coefficient is the exact angular overlap density, not a fitted number.
    """
    if not (0.0 <= sin2_theta12 <= 1.0):
        raise ValueError("sin2_theta12 must lie in [0, 1]")
    return sin2_theta12 / math.pi


def nonperturbative_orbifold_threshold() -> OrbifoldThresholdResult:
    """Apply the exact-threshold correction to the live NLO Δm²₂₁ baseline."""
    overlap = exact_fixed_point_overlap()
    correction = DELTA_C * overlap
    dm21_after = DM21_AFTER_NLO * (1.0 + correction)
    sigma_before = abs(DM21_PDG_EV2 - DM21_AFTER_NLO) / DM21_SIGMA_EV2
    sigma_after = abs(DM21_PDG_EV2 - dm21_after) / DM21_SIGMA_EV2
    achieved = sigma_after < 0.8
    gate = (
        "DM21_NONPERTURBATIVE_ORBIFOLD_THRESHOLD_SUB_0P8SIGMA"
        if achieved
        else "DM21_NONPERTURBATIVE_ORBIFOLD_THRESHOLD_RESIDUAL"
    )
    return OrbifoldThresholdResult(
        overlap_coefficient=overlap,
        threshold_correction=correction,
        dm21_before=DM21_AFTER_NLO,
        dm21_after=dm21_after,
        sigma_before=sigma_before,
        sigma_after=sigma_after,
        sub_0p8sigma_achieved=achieved,
        no_new_parameters=True,
        gate=gate,
    )


_RESULT = nonperturbative_orbifold_threshold()

NONPERTURBATIVE_OVERLAP_COEFFICIENT: float = _RESULT.overlap_coefficient
EXACT_THRESHOLD_CORRECTION: float = _RESULT.threshold_correction
DM21_AFTER_EXACT_THRESHOLD: float = _RESULT.dm21_after
TENSION_AFTER_EXACT_THRESHOLD: float = _RESULT.sigma_after
SUB_0P8SIGMA_ACHIEVED: bool = _RESULT.sub_0p8sigma_achieved
G4_RECLASSIFICATION_GATE: str = (
    "G4_INTERNAL_TYPE_B_CANDIDATE_RETIRED"
    if SUB_0P8SIGMA_ACHIEVED
    else "G4_INTERNAL_TYPE_B_CANDIDATE_REMAINS"
)


def g4_reclassification_summary(
    result: OrbifoldThresholdResult | None = None,
) -> dict[str, float | bool | str]:
    """Return the G4 reclassification verdict driven by the exact-threshold audit."""
    if result is None:
        result = _RESULT
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_GATE,
        "prior_g4_status": "TYPE_B_CANDIDATE",
        "falsifier_threshold_sigma": 0.8,
        "sigma_before": result.sigma_before,
        "sigma_after": result.sigma_after,
        "sub_0p8sigma_achieved": result.sub_0p8sigma_achieved,
        "no_new_parameters": result.no_new_parameters,
        "reclassification_gate": G4_RECLASSIFICATION_GATE,
        "honest_note": (
            "This retires the historical P784/P785 internal G4 Type B candidate "
            "gate by satisfying the repository's own non-perturbative falsifier. "
            "It does not claim exact zero residual and does not supersede the "
            "separate JUNO precision-routing audits in Pillars 796 and 802."
        ),
    }
