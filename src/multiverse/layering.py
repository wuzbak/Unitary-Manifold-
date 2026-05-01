# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/multiverse/layering.py
===========================
Big Bang Layering — braiding event mechanics and branch lossiness.

Background (Q29 in BIG_QUESTIONS.md)
--------------------------------------
The hypothesis that the Big Bang was a *collision of two main branches*
(parallel universes) is superseded by the **layering picture**: the two
winding modes n_w = 5 and n_w = 7 are *layers of the same compact S¹/Z₂
dimension*, not separate manifolds.  The "Big Bang event" is the
**Chern–Simons resonance locking** — the moment the geometry reached the
critical compactification radius R at which the CS level k_cs = 5² + 7² = 74
activates, coupling the two winding layers into a single entangled braid state.

Pre-braiding and post-braiding states
--------------------------------------
Before the CS coupling activates each winding layer evolves independently:

    Mode n₁ carries kinetic energy  E₁ = n₁² / R²
    Mode n₂ carries kinetic energy  E₂ = n₂² / R²
    Total pre-braiding energy:  E_pre = (n₁² + n₂²) / R²  =  k_cs / R²

After the CS coupling activates the two modes braid.  The kinetic sector
mixes with parameter  ρ = 2n₁n₂/k_cs, creating:

    Adiabatic mode:   E_adiabatic = k_cs × c_s / R²     (drives inflation)
    Isocurvature mode: E_iso      = k_cs × (1 − c_s) / R²  (thermalised away)

where c_s = √(1 − ρ²) = (n₂² − n₁²) / k_cs.

Energy is conserved in total (E_adiabatic + E_iso = E_pre).  The Big Bang
releases the isocurvature mode as a thermalisation event; the adiabatic mode
is the inflationary field configuration.

For (n₁, n₂) = (5, 7): c_s = 12/37, so:
    E_adiabatic / E_pre = 12/37 ≈ 32.4 %  (drives slow-roll inflation)
    E_iso       / E_pre = 25/37 ≈ 67.6 %  (Big Bang thermalisation)

Branch lossiness from radion dynamics
--------------------------------------
The information-theoretic lossiness of a branch is related to how far the
branch's effective radion value φ_branch deviates from the canonical FTUM
fixed-point value φ_star.  The information current J^μ_inf = φ² u^μ is
conserved (∇_μ J^μ_inf = 0) precisely when φ = φ_star throughout the
evolution.

For a branch with primary winding n₁ the 5D → 4D Jacobian gives:

    φ_branch = J_KK(n₁) × φ₀_bare  =  n₁ × 2π × √φ₀_bare

The branch lossiness is:

    L(n₁, φ_star) = |1 − (φ_branch / φ_star)²|

L = 0 when φ_branch = φ_star (canonically satisfied only by n₁ = 5 with
φ_star ≈ effective_phi0_kk(1.0, 5) ≈ 31.42).

Public API
----------
BraidingEventResult
    Dataclass holding the pre- and post-braiding energy partition and the
    key thermodynamic quantities of the Big Bang layering event.

WalkingLayerState
    Dataclass representing the state of the compact dimension before or
    after the CS coupling activates.

big_bang_braiding_event(n1, n2) -> BraidingEventResult
    Compute the energy partition, CS locking, and thermodynamic quantities
    for the braiding event between winding layers n₁ and n₂.

branch_lossiness(branch, phi_star) -> float
    Compute L = |1 − (φ_branch / φ_star)²| for a BranchRecord.

layer_pair_resonance_check(n1, n2) -> dict
    Verify the SOS resonance identity and related consistency checks for
    an arbitrary (n₁, n₂) pair.

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
from dataclasses import dataclass
from typing import Optional

import numpy as np

from ..core.braided_winding import (
    braided_cs_mixing,
    braided_sound_speed,
    resonant_kcs,
    braided_ns_r,
    R_BICEP_KECK_95,
)
from ..core.inflation import (
    effective_phi0_kk,
    PLANCK_NS_CENTRAL,
)
from .branch_catalog import BranchRecord


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Default bare radion vev at the FTUM fixed point (φ₀_bare = 1 in Planck units)
PHI0_BARE_DEFAULT: float = 1.0

#: Canonical n₁ = 5 effective phi_star (used as the lossless reference)
_PHI_STAR_CANONICAL: float = float(effective_phi0_kk(PHI0_BARE_DEFAULT, 5))


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class WalkingLayerState:
    """State of the compact dimension's winding layers at one epoch.

    Represents a snapshot of the n₁ and n₂ winding modes, either before
    (is_braided=False) or after (is_braided=True) the CS coupling activates.

    Attributes
    ----------
    n1, n2      : int   — winding numbers
    k_cs        : int   — 0 before braiding; n₁²+n₂² after
    is_braided  : bool  — True iff the CS resonance locking has occurred
    c_s         : float — adiabatic sound speed (0 before braiding)
    rho         : float — kinetic mixing parameter (0 before braiding)
    phi_n1      : float — 4D effective radion for layer n₁  (φ_branch)
    phi_n2      : float — 4D effective radion for layer n₂
    phi0_bare   : float — bare radion vev supplied to the KK Jacobian
    """

    n1: int
    n2: int
    k_cs: int
    is_braided: bool
    c_s: float
    rho: float
    phi_n1: float
    phi_n2: float
    phi0_bare: float


@dataclass
class BraidingEventResult:
    """Result of the Big Bang braiding event between two winding layers.

    Produced by :func:`big_bang_braiding_event`.

    Attributes
    ----------
    n1, n2              : int   — winding numbers
    k_cs                : int   — Chern–Simons level = n₁² + n₂²
    is_sos_resonance    : bool  — True iff k_cs == n₁² + n₂² (always True here)
    rho                 : float — kinetic mixing parameter ρ = 2n₁n₂/k_cs
    c_s                 : float — braided adiabatic sound speed
    energy_pre          : float — total pre-braiding KE in units 1/R²  (= k_cs)
    energy_adiabatic    : float — adiabatic mode energy post-braiding  (= k_cs × c_s)
    energy_isocurvature : float — isocurvature energy thermalised away  (= k_cs × (1−c_s))
    adiabatic_fraction  : float — fraction of energy in adiabatic mode  (= c_s)
    iso_fraction        : float — fraction thermalised away             (= 1 − c_s)
    ns_prediction       : float — CMB scalar spectral index from the adiabatic mode
    r_prediction        : float — effective tensor-to-scalar ratio
    before_state        : WalkingLayerState — pre-braiding snapshot
    after_state         : WalkingLayerState — post-braiding snapshot
    """

    n1: int
    n2: int
    k_cs: int
    is_sos_resonance: bool
    rho: float
    c_s: float
    energy_pre: float
    energy_adiabatic: float
    energy_isocurvature: float
    adiabatic_fraction: float
    iso_fraction: float
    ns_prediction: float
    r_prediction: float
    before_state: WalkingLayerState
    after_state: WalkingLayerState


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def big_bang_braiding_event(
    n1: int,
    n2: int,
    phi0_bare: float = PHI0_BARE_DEFAULT,
) -> BraidingEventResult:
    """Compute the energy partition of the Big Bang CS braiding event.

    Models the transition from two independent winding layers (n₁, n₂) to
    a single entangled braid state when the compactification radius R reaches
    the critical value at which the Chern–Simons level k_cs = n₁² + n₂² locks.

    Energy is partitioned as:

        E_pre           = k_cs / R²                (pre-braiding; R = 1 used)
        E_adiabatic     = k_cs × c_s               (post-braiding inflation driver)
        E_isocurvature  = k_cs × (1 − c_s)         (thermalised — Big Bang heat)
        adiabatic_fraction = c_s,  iso_fraction = 1 − c_s

    Parameters
    ----------
    n1       : int   — primary winding number (≥ 1)
    n2       : int   — secondary winding number (> n1)
    phi0_bare: float — bare radion vev at FTUM fixed point (default 1.0)

    Returns
    -------
    BraidingEventResult

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    if n1 < 1:
        raise ValueError(f"n1={n1} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2} must be strictly greater than n1={n1}.")

    k_cs = resonant_kcs(n1, n2)           # = n1² + n2²
    rho  = braided_cs_mixing(n1, n2, k_cs)
    c_s  = braided_sound_speed(n1, n2, k_cs)

    # CMB observables from the adiabatic mode
    pred = braided_ns_r(n1, n2, phi0_bare=phi0_bare, k_cs=k_cs)

    # Energy partition (R = 1 Planck units throughout)
    e_pre    = float(k_cs)
    e_adiab  = float(k_cs) * c_s
    e_iso    = float(k_cs) * (1.0 - c_s)

    phi_n1 = float(effective_phi0_kk(phi0_bare, n1))
    phi_n2 = float(effective_phi0_kk(phi0_bare, n2))

    before = WalkingLayerState(
        n1=n1, n2=n2,
        k_cs=0,
        is_braided=False,
        c_s=0.0,
        rho=0.0,
        phi_n1=phi_n1,
        phi_n2=phi_n2,
        phi0_bare=phi0_bare,
    )
    after = WalkingLayerState(
        n1=n1, n2=n2,
        k_cs=k_cs,
        is_braided=True,
        c_s=c_s,
        rho=rho,
        phi_n1=phi_n1,
        phi_n2=phi_n2,
        phi0_bare=phi0_bare,
    )

    return BraidingEventResult(
        n1=n1,
        n2=n2,
        k_cs=k_cs,
        is_sos_resonance=True,      # always True: k_cs was set from resonant_kcs
        rho=rho,
        c_s=c_s,
        energy_pre=e_pre,
        energy_adiabatic=e_adiab,
        energy_isocurvature=e_iso,
        adiabatic_fraction=c_s,
        iso_fraction=1.0 - c_s,
        ns_prediction=pred.ns,
        r_prediction=pred.r_eff,
        before_state=before,
        after_state=after,
    )


def branch_lossiness(branch: BranchRecord,
                     phi_star: Optional[float] = None) -> float:
    """Compute the information-theoretic lossiness of a branch.

    The lossiness is defined via the information current J^μ_inf = φ² u^μ:

        L = |1 − (φ_branch / φ_star)²|

    where

        φ_branch = effective_phi0_kk(phi0_bare=1.0, n_winding=n₁)
                 = n₁ × 2π × √φ₀_bare        (KK Jacobian at n_w = n₁)

    and φ_star is the canonical FTUM fixed-point value (default:
    effective_phi0_kk(1.0, 5) ≈ 31.42 for the (5, 7) lossless branch).

    L = 0 exactly when φ_branch = φ_star, i.e. when n₁ = 5 and
    φ_star = _PHI_STAR_CANONICAL.  All other branches have L > 0.

    Parameters
    ----------
    branch   : BranchRecord — branch to evaluate (uses branch.n1)
    phi_star : float or None — reference fixed-point φ*; defaults to the
               canonical value effective_phi0_kk(1.0, 5) ≈ 31.42

    Returns
    -------
    float — L ≥ 0; L = 0 iff φ_branch == φ_star exactly

    Raises
    ------
    ValueError if phi_star ≤ 0.
    """
    if phi_star is None:
        phi_star = _PHI_STAR_CANONICAL

    if phi_star <= 0.0:
        raise ValueError(f"phi_star={phi_star!r} must be positive.")

    phi_branch = float(effective_phi0_kk(PHI0_BARE_DEFAULT, branch.n1))
    return float(abs(1.0 - (phi_branch / phi_star) ** 2))


def layer_pair_resonance_check(n1: int, n2: int) -> dict:
    """Verify the SOS resonance identity and related consistency checks.

    Computes and returns a structured dict confirming:
    - SOS identity:         k_cs == n₁² + n₂²
    - Beat frequency:       n₂ − n₁  (minimal integer gap = 2 for canonical)
    - Total winding:        n₁ + n₂  (Jacobi sum)
    - Sound speed formula:  c_s == (n₂ − n₁)(n₁ + n₂) / k_cs
    - Energy conservation:  E_adiabatic + E_iso == E_pre (within float precision)

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    dict with keys:
        n1, n2, k_cs, beat, jacobi_sum, c_s_formula, c_s_computed,
        c_s_match, energy_conserved, sos_identity_holds
    """
    if n1 < 1:
        raise ValueError(f"n1={n1} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2} must be strictly greater than n1={n1}.")

    k_cs = resonant_kcs(n1, n2)
    c_s_computed = braided_sound_speed(n1, n2, k_cs)
    c_s_formula = float((n2**2 - n1**2) / k_cs)

    evt = big_bang_braiding_event(n1, n2)
    energy_conserved = bool(
        abs(evt.energy_adiabatic + evt.energy_isocurvature - evt.energy_pre)
        < 1e-12 * max(1.0, evt.energy_pre)
    )

    return {
        "n1": n1,
        "n2": n2,
        "k_cs": k_cs,
        "beat": n2 - n1,
        "jacobi_sum": n1 + n2,
        "c_s_formula": c_s_formula,
        "c_s_computed": c_s_computed,
        "c_s_match": bool(abs(c_s_formula - c_s_computed) < 1e-12),
        "energy_conserved": energy_conserved,
        "sos_identity_holds": bool(k_cs == n1**2 + n2**2),
    }
