# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Consolidated, material-parameter-agnostic screening formula.

Input: band-structure / dielectric-response parameters for a candidate
material. Output: predicted polaron properties, metamaterial flags, and the
framework's fixed critical half-angle, plus a divergence score usable to
rank candidates against each other.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from src.materials.froehlich_polaron import (  # noqa: E402
    N_W_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    froehlich_alpha_um,
    polaron_binding_energy_ev,
    polaron_effective_mass_ratio,
    polaron_radius_nm,
)
from src.materials.metamaterials import epsilon_phi_near_zero, negative_phi_index  # noqa: E402
from src.materials.polariton_vortex import critical_angle_deg  # noqa: E402

#: UM-predicted canonical Froehlich coupling constant, material-independent.
ALPHA_UM_CANONICAL = froehlich_alpha_um(N_W_CANONICAL, N1_CANONICAL, N2_CANONICAL)

#: Framework's fixed critical half-angle (material-independent; see
#: polariton_vortex.py). Reported for context alongside each candidate.
CRITICAL_ANGLE_DEG = critical_angle_deg()


@dataclass(frozen=True)
class MaterialCandidate:
    """Minimal band-structure / dielectric-response description of a
    candidate material, sufficient to drive the consolidated formulas."""

    name: str
    alpha: float
    omega_lo_mev: float
    m_band_me: float
    epsilon_r: float
    mu_r: float = 1.0


def screen_candidate(candidate: MaterialCandidate) -> dict:
    """Run the consolidated polaron + metamaterial formula set against one
    candidate material and return a single result dict."""
    binding_energy_ev = polaron_binding_energy_ev(candidate.alpha, candidate.omega_lo_mev)
    effective_mass_ratio = polaron_effective_mass_ratio(candidate.alpha)
    radius_nm = polaron_radius_nm(candidate.omega_lo_mev, candidate.m_band_me)
    neg_index = negative_phi_index(candidate.epsilon_r, candidate.mu_r)
    eps_near_zero = epsilon_phi_near_zero(candidate.epsilon_r)
    alpha_divergence = abs(candidate.alpha - ALPHA_UM_CANONICAL)

    return {
        "name": candidate.name,
        "polaron_binding_energy_ev": binding_energy_ev,
        "polaron_effective_mass_ratio": effective_mass_ratio,
        "polaron_radius_nm": radius_nm,
        "negative_phi_index": neg_index,
        "epsilon_near_zero": eps_near_zero,
        "predicted_critical_angle_deg": CRITICAL_ANGLE_DEG,
        "alpha_um_canonical": ALPHA_UM_CANONICAL,
        "alpha_divergence_from_um": alpha_divergence,
    }


def rank_candidates(candidates: List[MaterialCandidate]) -> List[dict]:
    """Screen every candidate and rank by alpha divergence from the UM
    canonical value, descending — the materials whose measured Froehlich
    coupling would most cleanly separate from the UM-predicted value make
    the best new falsification targets, per article-354 direction #3."""
    if not candidates:
        raise ValueError("candidates must not be empty")
    results = [screen_candidate(c) for c in candidates]
    results.sort(key=lambda r: r["alpha_divergence_from_um"], reverse=True)
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank
    return results
