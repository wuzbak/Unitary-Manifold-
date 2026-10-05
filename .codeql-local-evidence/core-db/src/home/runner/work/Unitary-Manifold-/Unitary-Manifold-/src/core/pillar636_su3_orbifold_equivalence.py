# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Conditional SU(5) orbifold projection, not a derivation from metric parity.

Reflection makes the tensor component G_mu5 odd. It does not supply an
internal gauge bundle, bulk SU(5), or a lift P of reflection to that bundle.
Given SU(5), A_mu(-y) = P A_mu(y) P^-1 and A_5(-y) = -P A_5(y) P^-1
are consistent for each involution below, with identical spacetime reflection.
Their fixed Lie algebras have different dimensions, hence are inequivalent.
Use the same P at both ends of the interval for these examples; independently
chosen endpoint lifts would instead leave the intersection of fixed algebras.
"""
from __future__ import annotations

from typing import Any, Dict, List

PILLAR_NUMBER = 636
PILLAR_STATUS = "CONDITIONAL_SU5_PROJECTION_NOT_METRIC_DERIVED"
PILLAR_TITLE = "Conditional SU(5) Orbifold Projection and Nonuniqueness"
VERSION = "v20.9"
N_W = 5
K_CS = 74
SU5_RANK = 4
SM_GAUGE_GROUP = "SU(3)_C × SU(2)_L × U(1)_Y"
HEAVY_GAUGE_BOSONS = ["X_mu", "Y_mu"]
M_KK_GEV = 1042.0  # Legacy illustrative scale, not determined by parity.
Z2_ODD_BC_REUSE = False
SU3_STATUS_BEFORE = "SUBSTANTIALLY_CLOSED"
SU3_STATUS_AFTER = PILLAR_STATUS


def su5_involution(negative: int) -> Dict[str, Any]:
    """Compute the fixed algebra of Ad(diag(+1,...,+1,-1,...,-1)).

    An even number of minus signs gives determinant +1, so P is itself in
    SU(5), not merely U(5). Off-diagonal E_ij has parity p_i p_j; all four
    traceless diagonal generators are even. The 0, 2, 4 examples exhaust
    these diagonal adjoint involutions up to conjugacy and P -> -P.
    """
    if not isinstance(negative, int) or isinstance(negative, bool) or negative not in (0, 2, 4):
        raise ValueError("negative must be 0, 2, or 4")
    positive = 5 - negative
    signs = (1,) * positive + (-1,) * negative
    even = positive**2 + negative**2 - 1
    algebra = {
        0: "su(5)",
        2: "su(3) ⊕ su(2) ⊕ u(1)",
        4: "su(4) ⊕ u(1)",
    }[negative]
    group = {
        0: "SU(5)",
        2: "S(U(3) × U(2)) ≅ (SU(3) × SU(2) × U(1))/Z6",
        4: "S(U(1) × U(4)) ≅ (SU(4) × U(1))/Z4",
    }[negative]
    return {
        "diagonal": signs,
        "adjoint_parities": tuple(tuple(a * b for b in signs) for a in signs),
        "determinant": 1,
        "involution_squared": 1,
        "even_generators": even,
        "odd_generators": 24 - even,
        "invariant_algebra": algebra,
        "fixed_group_in_SU5": group,
        "bulk_group_assumed": "SU(5)",
        "same_metric_reflection": True,
    }


def z2_boundary_condition() -> Dict[str, Any]:
    """Separate coordinate tensor parity from the additional internal lift."""
    return {
        "condition": "G_{μ5}(x, −y) = −G_{μ5}(x, y)",
        "source_pillar": "70-D",
        "used_for_n_w_selection": False,
        "reused_for_su5_projection": False,
        "internal_lift_required": "P, with Ad(P)^2 = 1",
        "conditional_on": "SU(5) bulk and P = diag(1,1,1,-1,-1)",
        "z2_parity_map": {
            "Z2_even_modes": ["A_mu_SU3", "A_mu_SU2", "A_mu_U1"],
            "Z2_odd_modes": ["X_mu", "Y_mu"],
        },
    }


def su5_decomposition() -> Dict[str, Any]:
    """Retain the useful 12+12 decomposition conditional on the chosen lift."""
    projection = su5_involution(2)
    return {
        "su5_generators": 24,
        "sm_generators_even": projection["even_generators"],
        "heavy_generators_odd": projection["odd_generators"],
        "heavy_mass_gev": None,
        "illustrative_kk_scale_gev": M_KK_GEV,
        "sm_group": SM_GAUGE_GROUP,
        "global_group": projection["fixed_group_in_SU5"],
        "heavy_bosons": HEAVY_GAUGE_BOSONS,
        "odd_vector_zero_modes_absent": True,
        "decoupled_at_low_energy": "conditional on energy below the KK gap",
        "mass_gap_requires": "interval size, warp factor and endpoint conditions",
        "conditional_on": z2_boundary_condition()["conditional_on"],
    }


def orbifold_equivalence_theorem() -> Dict[str, Any]:
    """Legacy API: return a counterexample to the old equivalence claim."""
    return {
        "theorem": "metric_reflection_does_not_select_internal_involution",
        "premise": "SU(5) bulk is an additional assumption",
        "z2_bc": z2_boundary_condition(),
        "su5_decomposition": su5_decomposition(),
        "inequivalent_lifts": [su5_involution(n) for n in (0, 2, 4)],
        "equivalence_established": False,
        "lean4_proof_status": "NO_FUNCTIONAL_ANALYTIC_PROOF",
        "functional_analysis_complete": False,
    }


def residual_open() -> Dict[str, Any]:
    return {
        "open_item": "A physical principle selecting the gauge bundle and internal lift P",
        "required_for": "an internal derivation, rather than conditional SU(5) projection",
        "status": "UNDERDETERMINED_BY_METRIC_REFLECTION",
        "nominated_method": "additional physical assumptions, not arithmetic proxies",
        "impact_if_proved": "selection must exclude the inequivalent admissible lifts",
    }


def what_is_claimed() -> List[str]:
    return [
        "Conditional on SU(5) and diag(1,1,1,-1,-1), the fixed algebra is su(3)⊕su(2)⊕u(1).",
        "The even/odd adjoint dimensions are 12/12 for that choice.",
        "The same metric reflection admits fixed algebras of dimensions 24, 12 and 16.",
        "For simply connected bulk SU(5), the SM-like fixed group has a Z6 quotient.",
    ]


def what_is_NOT_claimed() -> List[str]:
    return [
        "Metric reflection does not derive SU(5), the internal lift, or n_w.",
        "No equivalence between metric tensor parity and internal gauge conjugation is proved.",
        "Neither the KK mass gap nor the global gauge group follows from Lie-algebra dimensions alone.",
    ]


def pillar_report() -> Dict[str, Any]:
    return {
        "pillar": PILLAR_NUMBER, "title": PILLAR_TITLE, "status": PILLAR_STATUS,
        "version": VERSION, "adjacent_track": False,
        "z2_boundary_condition": z2_boundary_condition(),
        "su5_decomposition": su5_decomposition(),
        "orbifold_equivalence_theorem": orbifold_equivalence_theorem(),
        "residual_open": residual_open(),
        "status_before": SU3_STATUS_BEFORE, "status_after": SU3_STATUS_AFTER,
        "what_is_claimed": what_is_claimed(), "what_is_NOT_claimed": what_is_NOT_claimed(),
        "toe_score_delta": 0.0, "hardgate_score_delta": 0.0,
    }
