# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 674 — NP-BC-7 Sub-gap T: ADM path-integral measure obstruction.

STATUS: NP_BC7_SUBGAP_T_ADM_PATH_INTEGRAL_MEASURE_OBSTRUCTION_FORMALISED

Background
----------
This hardgate NP-BC-7 module formalises the honest ADM superspace measure
obstruction on the 5D KK orbifold. The radion sector is Gaussian near the
Goldberger-Wise-stabilised vacuum, but the full 3-metric measure still requires
an external ultraviolet regulator.
"""
from __future__ import annotations

import math
from typing import Any, Dict

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "ADJACENT_TRACK",
    "LEAN4_NEW_FILE",
    "LEAN4_THEOREM_COUNT",
    "SUBGAP_T_STATUS",
    "DEWITT_METRIC_FORMULA",
    "RADION_SECTOR_GAUSSIAN",
    "M_PHI_GEV",
    "Z_PHI_ONE_LOOP_FORMULA",
    "FULL_3METRIC_SECTOR_OBSTRUCTION",
    "ADM_MEASURE_OBSTRUCTION_TYPE",
    "UV_REGULATOR_OPTIONS",
    "PROVED_COMPONENTS",
    "dewitt_metric_orbifold",
    "radion_partition_function",
    "full_3metric_obstruction",
    "proved_components",
    "remaining_gap_assessment",
    "lean4_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 674
PILLAR_STATUS: str = "NP_BC7_SUBGAP_T_ADM_PATH_INTEGRAL_MEASURE_OBSTRUCTION_FORMALISED"
PILLAR_TITLE: str = "NP-BC-7 Sub-gap T — ADM Path Integral Measure Obstruction Formalised"
VERSION: str = "v21.0"
ADJACENT_TRACK: bool = False

LEAN4_NEW_FILE: Dict[str, Any] = {
    "path": "lean4/UnitaryManifold/NPBC7SubgapT.lean",
    "theorems": 11,
}
LEAN4_THEOREM_COUNT: Dict[str, int] = {
    "total_previous": 354,
    "total_new": 11,
    "total": 365,
}
SUBGAP_T_STATUS: str = "ADM_PATH_INTEGRAL_MEASURE_OBSTRUCTION_FORMALISED"
DEWITT_METRIC_FORMULA: str = "G^{ijkl} = g^{ik}g^{jl} + g^{il}g^{jk} - g^{ij}g^{kl}"
RADION_SECTOR_GAUSSIAN: bool = True
M_PHI_GEV: float = 765.0
Z_PHI_ONE_LOOP_FORMULA: str = "(m_phi / (2*pi))**(1/2)"
FULL_3METRIC_SECTOR_OBSTRUCTION: bool = True
ADM_MEASURE_OBSTRUCTION_TYPE: str = "ADM_MEASURE_OBSTRUCTION"
UV_REGULATOR_OPTIONS: list[str] = [
    "Regge_calculus",
    "CDT_causal_dynamical_triangulation",
]
PROVED_COMPONENTS: list[str] = [
    "dewitt_metric_definition",
    "orbifold_decomposition",
    "z2_projection_riem_s1_z2",
    "radion_sector_gaussian_measure",
    "radion_partition_function_oneloop",
    "full_3metric_sector_identified",
    "uv_regulator_required",
    "regge_calculus_option_named",
    "cdt_option_named",
    "adm_measure_obstruction_stated",
    "adm_path_integral_measure_certificate",
]


def dewitt_metric_orbifold() -> Dict[str, Any]:
    """Return the DeWitt metric decomposition on the 5D KK orbifold."""
    return {
        "formula": DEWITT_METRIC_FORMULA,
        "sectors": ["Riem(M3)", "Riem(S1/Z2)", "dilaton_field_space"],
        "z2_projection": "odd orbifold modes projected out",
        "kk_adds_radion_sector": True,
    }


def radion_partition_function() -> Dict[str, Any]:
    """Return the Gaussian radion one-loop partition-function data."""
    z_phi_value = (M_PHI_GEV / (2.0 * math.pi)) ** 0.5
    return {
        "m_phi_gev": M_PHI_GEV,
        "formula": Z_PHI_ONE_LOOP_FORMULA,
        "z_phi_value": z_phi_value,
        "sector_gaussian": RADION_SECTOR_GAUSSIAN,
    }


def full_3metric_obstruction() -> Dict[str, Any]:
    """Return the full 3-metric measure obstruction."""
    return {
        "obstruction_type": ADM_MEASURE_OBSTRUCTION_TYPE,
        "uv_regulator_options": UV_REGULATOR_OPTIONS,
        "obstruction_formalised": True,
        "community_level_open_problem": True,
    }


def proved_components() -> list[str]:
    """Return the eleven Lean4-proved algebraic kernel components."""
    return PROVED_COMPONENTS


def remaining_gap_assessment() -> Dict[str, Any]:
    """Return the honest remaining-gap assessment for Sub-gap T."""
    return {
        "full_path_integral_claimed": False,
        "radion_sector_gaussian": RADION_SECTOR_GAUSSIAN,
        "full_3metric_sector_obstruction": FULL_3METRIC_SECTOR_OBSTRUCTION,
        "community_level_open_problem": True,
        "honest_note": (
            "The radion measure is controlled near phi_0, but the full ADM superspace "
            "measure still requires a UV regulator such as Regge calculus or CDT."
        ),
    }


def lean4_certificate() -> Dict[str, Any]:
    """Return the Lean4 certificate metadata for Sub-gap T."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "lean4_file": LEAN4_NEW_FILE["path"],
        "new_theorems": LEAN4_NEW_FILE["theorems"],
        "lean4_total_previous": LEAN4_THEOREM_COUNT["total_previous"],
        "lean4_total_after": LEAN4_THEOREM_COUNT["total"],
        "proved_components": len(PROVED_COMPONENTS),
        "obstruction_type": ADM_MEASURE_OBSTRUCTION_TYPE,
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 674 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": ADJACENT_TRACK,
        "dewitt_metric_orbifold": dewitt_metric_orbifold(),
        "radion_partition_function": radion_partition_function(),
        "full_3metric_obstruction": full_3metric_obstruction(),
        "proved_components": proved_components(),
        "remaining_gap_assessment": remaining_gap_assessment(),
        "lean4_certificate": lean4_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
