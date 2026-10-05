# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 667 — Fermi-Hubbard Phase 5 2D KK braid geometry.

STATUS: FH_PHASE5_2D_BRAID_GEOMETRY_COMPUTED

Background
----------
This adjacent-track pillar records the UM-motivated 2D KK Fermi-Hubbard
geometry with next-nearest-neighbour braid hopping t' = c_s².  The goal is to
state the asymmetry and velocity predictions that a future production bridge
run would probe, without requiring a live XDiag install inside CI.
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "ADJACENT_TRACK",
    "C_S",
    "T_PRIME_NNN",
    "L_SIZES",
    "U_KK",
    "T_KK",
    "PARTICLE_HOLE_SYMMETRY_BROKEN",
    "FERMI_VELOCITY_C_S_LIMIT",
    "ROUTING_L4",
    "ROUTING_L6",
    "PHASE4_CONSISTENCY",
    "braid_geometry_parameters",
    "asymmetric_mott_lobe",
    "fermi_velocity_cs_limit",
    "pillar_report",
]

PILLAR_NUMBER: int = 667
PILLAR_STATUS: str = "FH_PHASE5_2D_BRAID_GEOMETRY_COMPUTED"
PILLAR_TITLE: str = "Fermi-Hubbard Phase 5 — 2D KK Braid Geometry"
VERSION: str = "v21.0"
ADJACENT_TRACK: bool = True

C_S: float = 12 / 37
T_PRIME_NNN: float = C_S**2
L_SIZES: List[int] = [4, 6]
U_KK: float = 74 / 5
T_KK: float = 12 / 37
PARTICLE_HOLE_SYMMETRY_BROKEN: bool = True
FERMI_VELOCITY_C_S_LIMIT: float = C_S
ROUTING_L4: str = "um_exact_dense"
ROUTING_L6: str = "bridge_crosscheck"
PHASE4_CONSISTENCY: str = "L2_CONDENSATE_ZERO_MODE_VIABLE"


def braid_geometry_parameters() -> Dict[str, Any]:
    """Return the 2D KK braid geometry parameter set."""
    return {
        "c_s": C_S,
        "t_kk": T_KK,
        "t_prime_nnn": T_PRIME_NNN,
        "u_kk": U_KK,
        "l_sizes": L_SIZES,
        "particle_hole_symmetry_broken": PARTICLE_HOLE_SYMMETRY_BROKEN,
        "routing_l4": ROUTING_L4,
        "routing_l6": ROUTING_L6,
    }


def asymmetric_mott_lobe() -> Dict[str, Any]:
    """Return the asymmetric Mott-lobe prediction from t' ≠ 0."""
    return {
        "t_over_u": T_KK / U_KK,
        "t_prime_over_u": T_PRIME_NNN / U_KK,
        "mott_lobe_asymmetric": PARTICLE_HOLE_SYMMETRY_BROKEN,
        "asymmetry_ratio": T_PRIME_NNN / T_KK,
        "critical_u_over_t": {
            "symmetric_reference": 40.0,
            "braid_geometry_estimate": U_KK / T_KK,
        },
        "phase4_consistency": PHASE4_CONSISTENCY,
        "honest_residual": (
            "Finite-size 2D critical-lobe extraction still requires production "
            "exact diagonalisation / bridge cross-checks."
        ),
    }


def fermi_velocity_cs_limit() -> Dict[str, Any]:
    """Return the Fermi-velocity-to-c_s limiting statement."""
    return {
        "c_s": C_S,
        "fermi_velocity_limit": FERMI_VELOCITY_C_S_LIMIT,
        "u_over_t": U_KK / T_KK,
        "consistency": True,
        "spinon_holon_separation_mechanism": (
            "Strong coupling drives spinon-holon separation so the effective "
            "low-energy velocity saturates at the braided sound-speed scale."
        ),
        "honest_residual": (
            "The limiting statement is analytical here; live many-body spectra "
            "require the bridge lane."
        ),
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 667 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": ADJACENT_TRACK,
        "braid_geometry_parameters": braid_geometry_parameters(),
        "asymmetric_mott_lobe": asymmetric_mott_lobe(),
        "fermi_velocity_cs_limit": fermi_velocity_cs_limit(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
