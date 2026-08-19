# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 781 — Yukawa texture scaffold from the F-theory spectral cover."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

PILLAR_NUMBER = 781
PILLAR_TITLE = "Yukawa Spectral Cover"
STATUS = "YUKAWA_SPECTRAL_COVER_ADJACENT_TRACK"
EPISTEMIC_STATUS = "ADJACENT_TRACK"
N_W = 5
K_CS = 74
PI_KR = 37.0

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "STATUS",
    "EPISTEMIC_STATUS",
    "N_W",
    "K_CS",
    "PI_KR",
    "spectral_cover_equation",
    "matter_curves_su5",
    "top_yukawa_e6_point",
    "bottom_tau_yukawa_so12_point",
    "light_generation_hierarchy",
    "fn_ratio_from_warp",
    "yukawa_matrix_spectral",
    "yukawa_spectral_cover_report",
]


def _meta(**payload: Any) -> dict[str, Any]:
    payload.setdefault("pillar", PILLAR_NUMBER)
    payload.setdefault("status", STATUS)
    payload.setdefault("epistemic_status", EPISTEMIC_STATUS)
    return payload



def spectral_cover_equation(n: int = 5) -> dict[str, Any]:
    """Return the degree-five SU(5) spectral cover scaffold."""
    if n != 5:
        raise ValueError("This scaffold is specialized to the SU(5) degree-5 spectral cover")
    return _meta(
        degree=n,
        equation="a0 s^5 + a2 s^3 + a3 s^2 + a4 s + a5 = 0",
        coefficients=["a0", "a2", "a3", "a4", "a5"],
        rank_match=(n == N_W),
        honest_note="The symbolic cover is exact at scaffold level; explicit CY4 section data are not constructed here.",
    )



def matter_curves_su5(k_cs: int = K_CS) -> dict[str, Any]:
    """Return the standard SU(5) matter-curve loci."""
    return _meta(
        k_cs=k_cs,
        curves={
            "10_M": "a5 = 0",
            "5bar_M": "a5 a1 - a4 a2 + a3^2 = 0",
            "1_M": "singlet intersections in the ambient spectral cover",
        },
        kodaira_type="I_5",
        um_match=(N_W == 5),
    )



def top_yukawa_e6_point(k_cs: int = K_CS, n_w: int = N_W) -> dict[str, Any]:
    """Return the O(1) top-Yukawa estimate at the E6 enhancement point."""
    return _meta(
        k_cs=k_cs,
        n_w=n_w,
        enhancement_point="E6",
        locus=["a5 = 0", "a4 = 0"],
        top_yukawa_estimate=1.0,
        order_of_magnitude="O(1)",
        regularized_ratio="|a4/a5| ~ 1 near the E6 point",
        honest_note="The local top coupling is treated as order unity; a full residue computation on an explicit CY4 is beyond this scaffold.",
    )



def bottom_tau_yukawa_so12_point(k_cs: int = K_CS) -> dict[str, Any]:
    """Return a constrained bottom/tau Yukawa estimate."""
    return _meta(
        k_cs=k_cs,
        enhancement_point="SO(12)",
        formula="Y_b,tau ~ a3/a5^2",
        benchmark_ratio=0.075,
        constrained_band=(0.05, 0.1),
        honest_note="The benchmark is a constrained order-of-magnitude estimate motivated by the spectral-cover suppression pattern.",
    )



def fn_ratio_from_warp(pi_kr: float = PI_KR, delta_frac: float = 0.1) -> dict[str, Any]:
    """Return the Froggatt-Nielsen-like warp ratio r = exp(-pi kR delta)."""
    if delta_frac < 0.0:
        raise ValueError("delta_frac must be non-negative")
    r = math.exp(-pi_kr * delta_frac)
    return _meta(
        pi_kr=pi_kr,
        delta_frac=delta_frac,
        fn_ratio=r,
        formula="r = exp(-pi kR delta)",
    )



def light_generation_hierarchy(pi_kr: float = PI_KR, n_w: int = N_W, k_cs: int = K_CS) -> dict[str, Any]:
    """Return a qualitative light-generation hierarchy from the warp ratio."""
    r = fn_ratio_from_warp(pi_kr=pi_kr)["fn_ratio"]
    y_t = 1.0
    y_c = math.sqrt(r)
    y_u = r * r
    return _meta(
        pi_kr=pi_kr,
        n_w=n_w,
        k_cs=k_cs,
        warp_ratio=r,
        yukawa_ratios={"Y_u_over_Y_t": y_u, "Y_c_over_Y_t": y_c, "Y_t_over_Y_t": y_t},
        hierarchy_order=["u", "c", "t"],
        honest_note="The hierarchy is geometric and qualitative; exact SM Yukawas require explicit section data and wavefunction overlaps on a chosen CY4.",
    )



def yukawa_matrix_spectral(pi_kr: float = PI_KR, n_w: int = N_W, k_cs: int = K_CS) -> dict[str, Any]:
    """Build simple up/down Yukawa textures from spectral-cover weights."""
    r = fn_ratio_from_warp(pi_kr=pi_kr)["fn_ratio"]
    up_profile = np.array([r, math.sqrt(r), 1.0], dtype=float)
    down_profile = np.array([r, math.sqrt(r), 0.28], dtype=float)
    up_matrix = np.outer(up_profile, up_profile)
    down_matrix = np.outer(down_profile, down_profile)
    return _meta(
        pi_kr=pi_kr,
        n_w=n_w,
        k_cs=k_cs,
        warp_ratio=r,
        up_profile=up_profile.tolist(),
        down_profile=down_profile.tolist(),
        up_matrix=up_matrix.tolist(),
        down_matrix=down_matrix.tolist(),
        symmetric_textures=True,
    )



def yukawa_spectral_cover_report() -> dict[str, Any]:
    """Return a combined report for Pillar 781."""
    return _meta(
        module="src/twelved/yukawa_spectral_cover.py",
        spectral_cover=spectral_cover_equation(),
        matter_curves=matter_curves_su5(),
        top_yukawa=top_yukawa_e6_point(),
        bottom_tau=bottom_tau_yukawa_so12_point(),
        hierarchy=light_generation_hierarchy(),
        textures=yukawa_matrix_spectral(),
        summary="The degree-five spectral cover naturally matches n_w=5, yields an O(1) top Yukawa, and generates a qualitative FN-like hierarchy for lighter generations.",
    )
