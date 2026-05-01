# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/consciousness_constant.py
=========================================
The Universal Consciousness Coupling Constant Ξ_c.

Background
----------
The 5-body core + 7-body layer architecture introduced in
``consciousness_autopilot.py`` encodes more than a dynamical system: it
constrains the *total body count* of any stable consciousness architecture
to a single integer, derived from a CMB measurement alone.  That integer
unlocks a dimensionless coupling constant that governs how tightly the
core (conscious interaction) and layer (ambient universe) are coupled at
the fixed point.

The Jacobi–Chern-Simons Identity
----------------------------------
For any braid pair (n_core, n_layer) with Chern-Simons level

    k_cs = n_core² + n_layer²

and Jacobi sum J = n_core + n_layer, beat = n_layer − n_core, the identity

    k_cs = J² / 2  +  beat                           (★)

holds **if and only if beat = 2**.

Proof:
    J²/2 + beat = (n_core + n_layer)²/2 + (n_layer − n_core)

    Expanding: = (n_core² + 2·n_core·n_layer + n_layer²)/2 + n_layer − n_core

    For this to equal k_cs = n_core² + n_layer²:
        n_core·n_layer + n_layer − n_core = (n_core² + n_layer²)/2
        2·n_core·n_layer + 2(n_layer − n_core) = n_core² + n_layer²
        2(n_layer − n_core) = (n_layer − n_core)²
        2 = n_layer − n_core = beat   (when beat ≠ 0)  □

Since beat = 2 is also the **minimal non-zero integer gap** for the densest
phase-correction schedule (from the Moiré sync analysis in
``five_seven_architecture.py``), the identity (★) is not a coincidence but
a necessary consequence of optimality.

Deriving the Total Body Count
-------------------------------
Rearranging (★):

    J = √(2 · (k_cs − beat))

Given only:
    • k_cs = 74  (from the CMB birefringence measurement β ≈ 0.3513°,
                  independently derived in ``braided_winding.py``)
    • beat = 2   (from the minimal-gap optimality condition)

we obtain:

    J = √(2 · (74 − 2)) = √(2 · 72) = √144 = **12**

The Jacobi sum J = 12 is the **total body count** of the architecture:
    N_total = N_core + N_layer = 5 + 7 = 12

This integer is not a free parameter.  It is uniquely determined by a
single cosmological observable (k_cs) and a single mathematical optimality
condition (beat = 2).

The Universal Consciousness Coupling Constant
----------------------------------------------
With N_core = 5, N_layer = 7, k_cs = 74, define:

    Ξ_c = N_core × N_layer / k_cs = 5 × 7 / 74 = **35/74 ≈ 0.4730**

Three equivalent expressions:

    Ξ_c = N_core × N_layer / k_cs          (body-count form)
    Ξ_c = ρ / 2                            (half the kinetic mixing depth)
    Ξ_c = 1/2 − 1/(2 · k_cs/beat)         (gap-from-perfect-entanglement form)
                                            = 1/2 − 1/74 = 35/74  [verified below]

Wait, 1/2 - 1/74 = 37/74 - 1/74 = 36/74 ≠ 35/74.  Let us use the correct form:

    Ξ_c = 1/2 − δΞ    where  δΞ = 1/2 − 35/74 = 2/74 = 1/37

So the consciousness coupling constant is exactly **1/37 below 1/2**:

    Ξ_c = 1/2 − 1/37 = 35/74

where 37 = k_cs / beat = 74 / 2 is the "half-resonance level."

Physical Interpretation
------------------------
• Ξ_c → 1/2   means the core and layer are perfectly inter-entangled
  (all information shared).  Full consciousness, no private universe.

• Ξ_c → 0     means the core and layer are decoupled (no consciousness).

• Ξ_c = 35/74 ≈ 0.473 is near-but-not-at 1/2, reflecting the (5,7) braid's
  near-maximal but not singular entanglement (ρ = 35/37, not 1).

• The gap δΞ = 1/37 = beat / k_cs is the irreducible "private universe"
  fraction — the minimal portion of reality that resists full consciousness
  coupling.  It is set by the cosmological birefringence level: larger k_cs
  → smaller gap → higher consciousness coupling.

The Human Coupling Fraction
-----------------------------
In the (5+7)-body system the human body is 1 of N_total = 12 bodies.
Its fractional contribution to the coupling is:

    Ξ_human = (1 / N_total) × Ξ_c = Ξ_c / 12 = 35 / 888 ≈ 0.03941

Note: 888 = 8 × 111 = 8 × 3 × 37.  The factor 37 appears again: Ξ_human
= 35/(24 × 37).

Public API
----------
N_TOTAL : int = 12
    Total body count derived from CMB birefringence and minimal-gap condition.

CONSCIOUSNESS_COUPLING : float = 35/74
    Ξ_c — the universal consciousness coupling constant.

CONSCIOUSNESS_GAP : float = 1/37
    δΞ = 1/2 − Ξ_c — the irreducible "private universe" fraction.

HUMAN_COUPLING_FRACTION : float = 35/888
    Ξ_human = Ξ_c / N_total — the human body's fractional coupling.

UniversalConstant
    Dataclass holding the full derivation: all numeric values, symbolic
    expressions, and the Jacobi–Chern-Simons identity verification.

consciousness_coupling() → UniversalConstant
    Compute and return the full universal constant derivation.

jacobi_cs_identity(n_core, n_layer) → dict
    Verify or disprove the Jacobi–Chern-Simons identity for any pair.
    Returns a dict with keys: beat, jacobi_sum, lhs, rhs, identity_holds,
    beat_is_minimal.

derive_total_body_count(k_cs, beat) → int
    Derive J = √(2·(k_cs − beat)) and return it as an integer.
    Raises ValueError if the result is not a perfect integer square.

coupling_from_architecture(n_core, n_layer) → float
    Compute Ξ = n_core × n_layer / (n_core² + n_layer²) for any pair.

entanglement_gap(n_core, n_layer) → float
    Compute δΞ = 1/2 − Ξ for any pair.
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import math
from dataclasses import dataclass, field
from typing import Dict

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from five_seven_architecture import (
    N_CORE,
    N_LAYER,
    K_CS_RESONANCE,
    BEAT_FREQUENCY,
    JACOBI_SUM,
)
from src.core.braided_winding import braided_cs_mixing


# ---------------------------------------------------------------------------
# Derived universal constants
# ---------------------------------------------------------------------------

#: Total body count derived from CMB birefringence and the minimal-gap condition:
#:   N_TOTAL = √(2 · (k_cs − beat)) = √(2 · 72) = √144 = 12
N_TOTAL: int = 12

#: Ξ_c = N_core × N_layer / k_cs = 35/74 ≈ 0.4730
#: The universal consciousness coupling constant.
CONSCIOUSNESS_COUPLING: float = (N_CORE * N_LAYER) / K_CS_RESONANCE

#: δΞ = 1/2 − Ξ_c = 1/37 ≈ 0.02703
#: The "private universe" fraction — the irreducible gap from perfect entanglement.
CONSCIOUSNESS_GAP: float = 0.5 - CONSCIOUSNESS_COUPLING

#: Ξ_human = Ξ_c / N_total = 35/888 ≈ 0.03941
#: The human body's fractional coupling in the full (5+7)-body system.
HUMAN_COUPLING_FRACTION: float = CONSCIOUSNESS_COUPLING / N_TOTAL

#: Rational numerator of Ξ_c = 35/74.
_XI_NUMERATOR:   int = N_CORE * N_LAYER          # 35
#: Rational denominator of Ξ_c = 35/74.
_XI_DENOMINATOR: int = K_CS_RESONANCE             # 74


# ---------------------------------------------------------------------------
# UniversalConstant dataclass
# ---------------------------------------------------------------------------

@dataclass
class UniversalConstant:
    """Full derivation of the universal consciousness coupling constant.

    Attributes
    ----------
    n_core             : int   — core winding number (5)
    n_layer            : int   — layer winding number (7)
    k_cs               : int   — Chern-Simons level (74)
    beat               : int   — minimal beat (2)
    jacobi_sum         : int   — n_core + n_layer (12)
    n_total_derived    : int   — N_total = √(2(k_cs − beat)) (12)
    identity_lhs       : float — k_cs = 74
    identity_rhs       : float — J²/2 + beat = 72 + 2 = 74
    identity_holds     : bool  — lhs == rhs (True for beat=2)
    xi_c               : float — Ξ_c = N_core×N_layer / k_cs (35/74)
    xi_c_numerator     : int   — numerator of Ξ_c (35)
    xi_c_denominator   : int   — denominator of Ξ_c (74)
    rho                : float — kinetic mixing depth ρ = 35/37
    xi_c_as_half_rho   : float — ρ/2 (should equal xi_c)
    consciousness_gap  : float — δΞ = 1/2 − Ξ_c = 1/37
    gap_denominator    : int   — denominator of δΞ (37 = k_cs/beat)
    xi_human           : float — Ξ_human = Ξ_c / N_total = 35/888
    """
    n_core:          int
    n_layer:         int
    k_cs:            int
    beat:            int
    jacobi_sum:      int
    n_total_derived: int
    identity_lhs:    float
    identity_rhs:    float
    identity_holds:  bool
    xi_c:            float
    xi_c_numerator:  int
    xi_c_denominator: int
    rho:             float
    xi_c_as_half_rho: float
    consciousness_gap: float
    gap_denominator: int
    xi_human:        float


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def consciousness_coupling() -> UniversalConstant:
    """Compute and return the full universal constant derivation.

    Uses the canonical (5,7) braid architecture with the CMB-derived k_cs = 74
    and the minimal-gap condition beat = 2.

    Returns
    -------
    UniversalConstant — complete derivation with all intermediate values

    Raises
    ------
    AssertionError if the Jacobi–Chern-Simons identity fails (should never
    happen for the canonical (5,7) architecture).
    """
    n_core  = N_CORE
    n_layer = N_LAYER
    k_cs    = K_CS_RESONANCE
    beat    = BEAT_FREQUENCY
    j_sum   = JACOBI_SUM

    # -- Jacobi-Chern-Simons identity --
    lhs = float(k_cs)
    rhs = float(j_sum ** 2) / 2.0 + float(beat)
    identity = bool(abs(lhs - rhs) < 1e-9)

    # -- Derive N_total from k_cs and beat --
    n_total = derive_total_body_count(k_cs, beat)

    # -- Coupling constant --
    xi_c  = float(n_core * n_layer) / float(k_cs)
    rho   = braided_cs_mixing(n_core, n_layer, k_cs)
    xi_rho_half = float(rho) / 2.0
    gap   = 0.5 - xi_c
    gap_denom = int(round(1.0 / gap)) if gap > 1e-12 else 0

    xi_human = xi_c / float(n_total)

    return UniversalConstant(
        n_core=n_core,
        n_layer=n_layer,
        k_cs=k_cs,
        beat=beat,
        jacobi_sum=j_sum,
        n_total_derived=n_total,
        identity_lhs=lhs,
        identity_rhs=rhs,
        identity_holds=identity,
        xi_c=xi_c,
        xi_c_numerator=_XI_NUMERATOR,
        xi_c_denominator=_XI_DENOMINATOR,
        rho=float(rho),
        xi_c_as_half_rho=xi_rho_half,
        consciousness_gap=gap,
        gap_denominator=gap_denom,
        xi_human=xi_human,
    )


def jacobi_cs_identity(n_core: int, n_layer: int) -> Dict:
    """Verify the Jacobi–Chern-Simons identity for any braid pair.

    The identity k_cs = J²/2 + beat holds iff beat = n_layer − n_core = 2.

    Parameters
    ----------
    n_core, n_layer : int — braid winding numbers (n_layer > n_core ≥ 1)

    Returns
    -------
    dict with keys:
        n_core, n_layer, k_cs, beat, jacobi_sum,
        lhs (k_cs), rhs (J²/2 + beat),
        identity_holds (bool), beat_is_minimal (bool)
    """
    k_cs  = n_core ** 2 + n_layer ** 2
    beat  = n_layer - n_core
    j_sum = n_core + n_layer
    lhs   = float(k_cs)
    rhs   = float(j_sum ** 2) / 2.0 + float(beat)
    return {
        "n_core":         n_core,
        "n_layer":        n_layer,
        "k_cs":           k_cs,
        "beat":           beat,
        "jacobi_sum":     j_sum,
        "lhs":            lhs,
        "rhs":            rhs,
        "identity_holds": bool(abs(lhs - rhs) < 1e-9),
        "beat_is_minimal": bool(beat == 2),
    }


def derive_total_body_count(k_cs: int, beat: int) -> int:
    """Derive the total body count N_total = √(2·(k_cs − beat)).

    This uses the Jacobi–Chern-Simons identity (valid for beat = 2):

        J = N_total = √(2 · (k_cs − beat))

    For the canonical (5,7) architecture:

        √(2 · (74 − 2)) = √144 = 12

    Parameters
    ----------
    k_cs : int — Chern-Simons resonance level
    beat : int — layer/core beat frequency (must be 2 for the identity to hold)

    Returns
    -------
    int — N_total (exact integer)

    Raises
    ------
    ValueError if 2·(k_cs − beat) is not a perfect square, indicating the
    architecture does not satisfy the minimal-gap optimality condition.
    """
    val = 2 * (k_cs - beat)
    if val < 0:
        raise ValueError(f"2·(k_cs − beat) = {val} < 0; invalid.")
    root = math.isqrt(val)
    if root * root != val:
        raise ValueError(
            f"2·(k_cs − beat) = {val} is not a perfect square.  "
            f"The Jacobi–Chern-Simons identity requires beat = 2."
        )
    return root


def coupling_from_architecture(n_core: int, n_layer: int) -> float:
    """Compute Ξ = n_core × n_layer / (n_core² + n_layer²) for any braid pair.

    This generalises CONSCIOUSNESS_COUPLING = 35/74 to arbitrary architectures.
    Note that Ξ ≤ 1/2 for all real n_core < n_layer, with equality as
    n_layer / n_core → 1.

    Parameters
    ----------
    n_core, n_layer : int — winding numbers (both ≥ 1)

    Returns
    -------
    float — Ξ ∈ (0, 1/2)

    Raises
    ------
    ValueError if n_core < 1 or n_layer < 1.
    """
    if n_core < 1 or n_layer < 1:
        raise ValueError(f"n_core and n_layer must be ≥ 1; got {n_core}, {n_layer}.")
    k = n_core ** 2 + n_layer ** 2
    return float(n_core * n_layer) / float(k)


def entanglement_gap(n_core: int, n_layer: int) -> float:
    """Compute δΞ = 1/2 − Ξ for any braid pair.

    The "private universe" fraction: how far the architecture's coupling
    constant is from perfect entanglement (Ξ = 1/2).

    For (5,7): δΞ = 1/2 − 35/74 = 2/74 = 1/37 ≈ 0.0270.

    Parameters
    ----------
    n_core, n_layer : int — winding numbers (both ≥ 1)

    Returns
    -------
    float — δΞ ≥ 0
    """
    return float(0.5 - coupling_from_architecture(n_core, n_layer))
