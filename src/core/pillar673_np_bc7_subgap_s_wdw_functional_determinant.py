# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 673 — NP-BC-7 Sub-gap S: WdW functional determinant obstruction.

STATUS: NP_BC7_SUBGAP_S_WDW_FUNCTIONAL_DETERMINANT_OBSTRUCTION_FORMALISED

Background
----------
This hardgate NP-BC-7 module formalises the honest obstruction in the full
Wheeler-DeWitt functional determinant. The minisuperspace truncation remains
tractable, while the inhomogeneous full functional integral acquires a named
Seeley-DeWitt divergence structure on the 5D Kaluza-Klein background.
"""
from __future__ import annotations

from typing import Any, Dict

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "ADJACENT_TRACK",
    "BRAIDED_SOUND_SPEED",
    "K_CS",
    "N_W",
    "LEAN4_NEW_FILE",
    "LEAN4_THEOREM_COUNT",
    "SUBGAP_S_STATUS",
    "SEELEY_DEWITT_COEFFICIENTS",
    "OBSTRUCTION_TYPE",
    "MINISUPERSPACE_TRACTABLE",
    "FULL_FUNCTIONAL_INTEGRAL_DIVERGES",
    "PROVED_COMPONENTS",
    "seeley_dewitt_heat_kernel",
    "z2_projection_effect",
    "proved_components",
    "remaining_gap_assessment",
    "lean4_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 673
PILLAR_STATUS: str = "NP_BC7_SUBGAP_S_WDW_FUNCTIONAL_DETERMINANT_OBSTRUCTION_FORMALISED"
PILLAR_TITLE: str = "NP-BC-7 Sub-gap S — WdW Functional Determinant Obstruction Formalised"
VERSION: str = "v21.0"
ADJACENT_TRACK: bool = False

BRAIDED_SOUND_SPEED: float = 12.0 / 37.0
K_CS: int = 74
N_W: int = 5

LEAN4_NEW_FILE: Dict[str, Any] = {
    "path": "lean4/UnitaryManifold/NPBC7SubgapS.lean",
    "theorems": 12,
}
LEAN4_THEOREM_COUNT: Dict[str, int] = {
    "total_previous": 342,
    "total_new": 12,
    "total": 354,
}
SUBGAP_S_STATUS: str = "WDW_FUNCTIONAL_DETERMINANT_OBSTRUCTION_FORMALISED"
SEELEY_DEWITT_COEFFICIENTS: Dict[str, str] = {
    "a0": "Vol(M)",
    "a2": "integral_R_over_6",
    "a4": "curvature_squared_integral",
}
OBSTRUCTION_TYPE: str = "SEELEY_DEWITT_OBSTRUCTION"
MINISUPERSPACE_TRACTABLE: bool = True
FULL_FUNCTIONAL_INTEGRAL_DIVERGES: bool = True
PROVED_COMPONENTS: list[str] = [
    "operator_algebra_minus_nabla2_plus_m2",
    "z2_projection_odd_mode_elimination",
    "kk_tower_a4_coefficient",
    "seeley_dewitt_a0_vol_m",
    "seeley_dewitt_a2_integral_r",
    "seeley_dewitt_a4_curvature_squared",
    "minisuperspace_finite_dimensional",
    "full_functional_divergence_structure",
    "kk_correction_to_a4_named",
    "braid_structure_constant_in_a4",
    "obstruction_formally_stated",
    "seeley_dewitt_obstruction_certificate",
]


def seeley_dewitt_heat_kernel() -> Dict[str, Any]:
    """Return the named one-loop heat-kernel obstruction data."""
    return {
        "formula": "log det'(-nabla^2 + m^2) ~ sum_k a_(2k) * Lambda^(5-2k)",
        "a0_coeff": SEELEY_DEWITT_COEFFICIENTS["a0"],
        "a2_coeff": SEELEY_DEWITT_COEFFICIENTS["a2"],
        "a4_coeff": SEELEY_DEWITT_COEFFICIENTS["a4"],
        "minisuperspace_tractable": MINISUPERSPACE_TRACTABLE,
        "full_functional_diverges": FULL_FUNCTIONAL_INTEGRAL_DIVERGES,
        "obstruction_type": OBSTRUCTION_TYPE,
        "divergence_structure_named": True,
    }


def z2_projection_effect() -> Dict[str, Any]:
    """Return the Z₂ orbifold projection effect on the KK heat-kernel tower."""
    kk_prefactor = N_W**2 * K_CS
    return {
        "z2_eliminates_odd_modes": True,
        "kk_tower_contribution_to_a4": "even-mode KK tower shifts curvature_squared_integral",
        "kk_correction_coefficient": f"{kk_prefactor} * curvature_squared_prefactor",
        "kk_correction_coefficient_numeric": kk_prefactor,
    }


def proved_components() -> list[str]:
    """Return the twelve Lean4-proved algebraic kernel components."""
    return PROVED_COMPONENTS


def remaining_gap_assessment() -> Dict[str, Any]:
    """Return the honest remaining-gap assessment for Sub-gap S."""
    return {
        "full_quantization_claimed": False,
        "obstruction_formalised": True,
        "minisuperspace_remains_tractable": MINISUPERSPACE_TRACTABLE,
        "community_level_open_problem": True,
        "honest_note": (
            "The full inhomogeneous Wheeler-DeWitt determinant is not claimed to be solved. "
            "What is claimed is the precise naming of the Seeley-DeWitt obstruction while "
            "preserving tractable minisuperspace control."
        ),
    }


def lean4_certificate() -> Dict[str, Any]:
    """Return the Lean4 certificate metadata for Sub-gap S."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "lean4_file": LEAN4_NEW_FILE["path"],
        "new_theorems": LEAN4_NEW_FILE["theorems"],
        "lean4_total_previous": LEAN4_THEOREM_COUNT["total_previous"],
        "lean4_total_after": LEAN4_THEOREM_COUNT["total"],
        "proved_components": len(PROVED_COMPONENTS),
        "obstruction_type": OBSTRUCTION_TYPE,
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 673 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": ADJACENT_TRACK,
        "seeley_dewitt_heat_kernel": seeley_dewitt_heat_kernel(),
        "z2_projection_effect": z2_projection_effect(),
        "proved_components": proved_components(),
        "remaining_gap_assessment": remaining_gap_assessment(),
        "lean4_certificate": lean4_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
