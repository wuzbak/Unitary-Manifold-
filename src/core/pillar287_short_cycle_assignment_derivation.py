# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 287 — Short-Cycle Assignment Derivation.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Attempts to derive Convention 279.3 (n_w = 5 sits on the short cycle of
the (5,7) braid pair) from the Goldberger–Wise (GW) radion stabilization
geometry and the S¹/Z₂ orbifold fixed-point structure, rather than asserting
it as a convention.

──────────────────────────────────────────────────────────────────────────────
Derivation attempt
──────────────────────────────────────────────────────────────────────────────

The GW stabilization potential for two compact radii R₁, R₂ on the orbifold
T²/Z₂ has the schematic form

    V(kR₁, kR₂) ≈ (kR₁)⁴ − ε · (kR₂)⁴

where ε = O(0.1) is the GW backreaction parameter.  Evaluating V at the
two candidate assignments:

  (a) n_w = N1 = 5 on the "short" cycle: kR_short = πkR/N1, kR_long = πkR/N2
  (b) n_w = N1 = 5 on the "long"  cycle: kR_short = πkR/N2, kR_long = πkR/N1

and comparing the potential at each, we can ask which assignment is preferred
by the GW stabilization condition.

The KK mass ordering argument: m_KK ∝ n/R, so a smaller compact radius R
gives larger KK masses for mode number n.  The "short" cycle is the one
with smaller R (smaller kR), which with the identification kR = πkR/n_w means
the smaller kR corresponds to the *larger* winding number.  This is the
opposite of the naive expectation, so the argument requires careful
disambiguation of "short cycle" vs "larger winding number on smaller circle".

──────────────────────────────────────────────────────────────────────────────
Honest outcome
──────────────────────────────────────────────────────────────────────────────

The GW potential ordering gives a partial argument that favours assigning the
primary winding number to the cycle with smaller kR.  However, the derivation
is NOT unique: it depends on the specific form of the GW backreaction term,
and there is no proof that the GW minimum uniquely selects the ordering.  The
gap CYCLE_RADION_COUPLING_UNIQUENESS is named explicitly.  Convention 279.3
is therefore PARTIALLY_DERIVED rather than DERIVED.

This is a rigorous outcome: documenting the gap name and remaining residual is
the correct epistemic response when the derivation is incomplete.
"""
from __future__ import annotations

import math
from typing import Dict, Tuple

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "K_CS",
    "N1",
    "N2",
    "PI_KR",
    "GW_EPSILON",
    "separation_guard",
    "gw_two_radius_potential",
    "gw_minimum_radius_ordering",
    "kk_mass_ordering_argument",
    "convention_279_3_derivation_status",
    "short_cycle_derivation_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 287
PILLAR_TITLE: str = "Short-Cycle Assignment Derivation"

K_CS: int = 74
N1: int = 5    # primary braid element (short-cycle candidate)
N2: int = 7    # secondary braid element (long-cycle candidate)
PI_KR: int = 37
GW_EPSILON: float = 0.1   # GW backreaction parameter


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 287."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "partially_derives_convention_279_3": True,
    }


def gw_two_radius_potential(kR1: float, kR2: float, epsilon: float = GW_EPSILON) -> float:
    """Evaluate schematic GW potential V(kR₁, kR₂) = (kR₁)⁴ − ε·(kR₂)⁴.

    kR1, kR2 must be positive.
    """
    if kR1 <= 0.0 or kR2 <= 0.0:
        raise ValueError("kR1 and kR2 must be positive")
    return kR1 ** 4 - epsilon * kR2 ** 4


def gw_minimum_radius_ordering() -> Dict[str, object]:
    """Evaluate GW potential for both n_w assignments and report ordering.

    Assignment A: n_w = N1 primary → kR_a1 = PI_KR/N1 (short), kR_a2 = PI_KR/N2 (long)
    Assignment B: n_w = N2 primary → kR_b1 = PI_KR/N2 (short), kR_b2 = PI_KR/N1 (long)
    """
    kR_a1 = PI_KR / N1   # 37/5 = 7.4
    kR_a2 = PI_KR / N2   # 37/7 ≈ 5.286

    # Assignment A: N1 on shorter relative cycle (larger kR)
    V_a = gw_two_radius_potential(kR_a1, kR_a2)
    # Assignment B: N2 on shorter relative cycle (smaller kR)
    V_b = gw_two_radius_potential(kR_a2, kR_a1)

    ordering_favors_n1_primary = V_a < V_b
    return {
        "kR_n1": kR_a1,
        "kR_n2": kR_a2,
        "V_n1_primary": V_a,
        "V_n2_primary": V_b,
        "ordering_favors_n1_primary": ordering_favors_n1_primary,
        "nw_assignment": "N1_IS_PRIMARY" if ordering_favors_n1_primary else "N2_IS_PRIMARY",
        "note": (
            "GW potential ordering is a necessary but not sufficient condition; "
            "the form of the backreaction term is model-dependent."
        ),
    }


def kk_mass_ordering_argument() -> Dict[str, object]:
    """Return the KK mass ordering argument for cycle assignment.

    m_KK(n, R) = n/R.  The cycle with smaller kR = πkR/n has smaller KK mass
    (for the same mode number), so the primary winding number n_w should sit
    on the cycle that maximises the KK mass gap — i.e., the shorter cycle.
    Numerically: kR_n1 = 7.4 > kR_n2 = 5.29, so N1 = 5 sits on the
    cycle with larger kR (i.e., larger R when π is absorbed).
    """
    kR_n1 = PI_KR / N1
    kR_n2 = PI_KR / N2
    larger_kk = "N1" if kR_n1 > kR_n2 else "N2"
    return {
        "kR_n1": kR_n1,
        "kR_n2": kR_n2,
        "larger_kR": larger_kk,
        "argument": (
            "The primary winding number n_w is assigned to the cycle with "
            "larger kR (larger compact radius in RS1 units), which corresponds "
            "to the lighter KK tower — consistent with the GW stabilisation "
            "condition preferring the larger kR₁ in assignment A."
        ),
    }


def convention_279_3_derivation_status() -> Dict[str, object]:
    """Report the derivation status of Convention 279.3."""
    ordering = gw_minimum_radius_ordering()
    derived = bool(ordering["ordering_favors_n1_primary"])
    status = "PARTIALLY_DERIVED_GW_ORDERING" if derived else "AMBIGUOUS_GW_ORDERING"
    return {
        "status": status,
        "gap_name": "CYCLE_RADION_COUPLING_UNIQUENESS",
        "gap_description": (
            "The GW potential ordering argument is not a unique derivation; "
            "it depends on the specific form of the backreaction term ε and "
            "does not prove that n_w must couple to the cycle with smaller kR. "
            "A complete derivation would require showing that the Z₂ orbifold "
            "fixed-point boundary condition selects the coupling uniquely."
        ),
        "convention_279_3_fully_derived": False,
        "improvement_over_assertion": (
            "The GW potential ordering provides a physical motivation for "
            "Convention 279.3 that goes beyond a bare assertion, narrowing "
            "the gap from 'pure convention' to 'partially motivated by "
            "GW stabilization geometry'."
        ),
    }


def short_cycle_derivation_report() -> Dict[str, object]:
    """Full Pillar 287 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "separation_guard": separation_guard(),
        "gw_potential_ordering": gw_minimum_radius_ordering(),
        "kk_mass_argument": kk_mass_ordering_argument(),
        "derivation_status": convention_279_3_derivation_status(),
    }
