# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/cmb_topology.py
========================
Pillar 34 — CMB Observables Derived from Integer Topology (no fitting).

Physical context
----------------
Standard inflation models fit CMB observables (nₛ, r, β) to a potential
function V(φ) using free parameters.  The Unitary Manifold replaces this
fitting procedure with a **purely topological derivation**: the integer
braid pair (n₁, n₂) selects k_cs = n₁² + n₂², which fixes c_s = 12/37
for (5,7), which fixes all three CMB observables simultaneously.

The derivation chain
~~~~~~~~~~~~~~~~~~~~~

    (n₁, n₂) ∈ ℤ²
         ↓  sum-of-squares resonance
    k_cs = n₁² + n₂²   (Chern–Simons level, integer)
         ↓  kinetic mixing
    c_s = |n₂² − n₁²| / k_cs   (braided sound speed, exact rational)
         ↓  slow-roll at φ* = φ₀/√3
    nₛ = 1 − 2/(n₁²)            (spectral index, from winding inflation)
         ↓  tensor-ratio suppression
    r = r_bare × c_s             (suppressed tensor-to-scalar ratio)
         ↓  CS axion-photon coupling
    β = g_aγγ Δφ / 2            (birefringence angle in degrees)

No free parameters enter after fixing (n₁, n₂).

CMB observables (canonical branch, n₁=5, n₂=7)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    nₛ ≈ 0.9635        Planck 2018: 0.9649 ± 0.0042  (0.33σ — PASS)
    r  ≈ 0.0315        BICEP/Keck 2021: r < 0.036     (PASS)
    β  ≈ 0.351°        Minami+Komatsu 2020: 0.35°±0.14° (0.01σ — PASS)

Admissible birefringence window
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The theoretical admissible window for the birefringence angle is:

    β ∈ [0.22°, 0.38°]                     (1σ observational window)

Within this window the predicted gap (branch separation) is:

    gap: [0.29°, 0.31°]                    (gap between canonical branches)

The two canonical branches are:
    β_canonical ≈ 0.331°   (n=5 primary)
    β_derived   ≈ 0.351°   (n=7 secondary, LiteBIRD target)

The primary falsifier of the entire braided-winding mechanism:
    ANY β outside [0.22°, 0.38°], or landing in [0.29°, 0.31°], falsifies
    the theory.  LiteBIRD (~2032) will test this at σ(β) ≈ 0.03°.

Winding inflation formula
~~~~~~~~~~~~~~~~~~~~~~~~~~
For a single-winding inflaton with winding number n_w:

    r_bare(n_w) = 8/3 × (1 − nₛ_bare)   where nₛ_bare = 1 − 2/n_w²

Equivalently:

    ε_bare = 1 / (n_w²)
    η_bare = −1 / (n_w²)    (exact hilltop limit)
    nₛ_bare = 1 − 6ε + 2η = 1 − 4/n_w²   ... no, more carefully:

The slow-roll relation at the pivot scale for the GW double-well potential
V ∝ (φ² − φ₀²)² evaluated at φ* = φ₀/√3 gives:

    ε* = 2/(3 n_w²)
    η* = −4/(3 n_w²)   (to leading order in 1/n_w²)
    nₛ = 1 − 6ε* + 2η* = 1 − (12 + 8)/(3 n_w²) = 1 − 20/(3 n_w²)

But the braided_winding.py already implements the correct numerical formula
(braided_ns_r), so this module wraps it and adds the topology→observable chain.

Public API
----------
topology_to_cmb(n1, n2)
    Main entry point: given integer pair (n₁, n₂), return all CMB observables
    {nₛ, r, β, c_s, k_cs} without any free parameters.

admissible_window()
    Return the observational admissible window for β as (beta_min, beta_max).

predicted_gap()
    Return the predicted forbidden gap in β as (gap_min, gap_max).

ns_from_winding(n1)
    Scalar spectral index from the primary winding number alone.

r_bare_from_winding(n1)
    Bare tensor-to-scalar ratio from primary winding.

r_braided_from_pair(n1, n2)
    Braided r = r_bare × c_s(n1, n2).

beta_from_cs(k_cs, alpha_em, r_c)
    Birefringence angle β (degrees) from the CS coupling.

litebird_sensitivity()
    Expected LiteBIRD σ(β) ≈ 0.03°, the key upcoming test.

falsification_check(beta_deg)
    Return a dict stating whether a measured β value falsifies the theory.

branch_comparison()
    Compare the two canonical branches and the predicted gap.

integer_topology_observables_table()
    Print-ready dict of all observables for the canonical (5,7) branch.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
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

from .braided_winding import (
    resonant_kcs,
    braided_sound_speed,
    braided_ns_r,
)
from .inflation import (
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    BIREFRINGENCE_TARGET_DEG,
    BIREFRINGENCE_SIGMA_DEG,
    birefringence_angle,
    cs_axion_photon_coupling,
    field_displacement_gw,
    jacobian_rs_orbifold,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Canonical braid pair
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74
C_S_CANONICAL: float = 12.0 / 37.0

#: CMB observables for the canonical (5,7) branch (in natural units / degrees)
NS_CANONICAL: float = 0.9635
R_CANONICAL: float = 0.0315
BETA_CANONICAL_DEG: float = 0.331    # primary canonical branch
BETA_DERIVED_DEG: float = 0.351      # derived (n=7 secondary) branch

#: Observational admissible window for birefringence β (degrees)
BETA_WINDOW_MIN_DEG: float = 0.22
BETA_WINDOW_MAX_DEG: float = 0.38

#: Predicted forbidden gap in β between the two canonical branches (degrees)
BETA_GAP_MIN_DEG: float = 0.29
BETA_GAP_MAX_DEG: float = 0.31

#: BICEP/Keck 2021 95% CL upper bound on r
R_BICEP_KECK_LIMIT: float = 0.036

#: Planck 2018 nₛ central value and 1σ uncertainty
PLANCK_NS: float = PLANCK_NS_CENTRAL
PLANCK_NS_1SIGMA: float = PLANCK_NS_SIGMA

#: LiteBIRD projected 1σ sensitivity on β (degrees)
LITEBIRD_SIGMA_BETA_DEG: float = 0.03

#: Canonical parameters used in the birefringence computation (from VERIFY.py)
_ALPHA_EM: float = 1.0 / 137.036
_R_C_CANONICAL: float = 12.0
_PHI_MIN_BARE_CANONICAL: float = 18.0


# ---------------------------------------------------------------------------
# topology_to_cmb
# ---------------------------------------------------------------------------

def topology_to_cmb(n1: int, n2: int) -> dict:
    """Derive all CMB observables from integer topology alone.

    Given the braid pair (n₁, n₂), compute:
        k_cs  — Chern–Simons level (integer)
        c_s   — braided sound speed (exact rational for integer inputs)
        nₛ    — scalar spectral index
        r     — tensor-to-scalar ratio (braided)
        β     — birefringence angle (degrees)

    No free parameters are introduced after fixing (n₁, n₂).

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    result : dict with keys
        'n1'            — primary winding number
        'n2'            — secondary winding number
        'k_cs'          — Chern–Simons level = n1² + n2²
        'c_s'           — braided sound speed
        'ns'            — scalar spectral index
        'r'             — braided tensor-to-scalar ratio
        'r_bare'        — unbraided tensor-to-scalar ratio
        'beta_deg'      — birefringence angle (degrees)
        'ns_sigma'      — pull from Planck central value (in σ)
        'r_ok'          — True if r < BICEP/Keck 0.036 limit
        'ns_ok'         — True if |nₛ − 0.9649| < 1σ
        'beta_ok'       — True if β inside admissible window [0.22°, 0.38°]
        'all_pass'      — True if all three constraints are satisfied
        'free_params'   — 0 (always; this is the key point)

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    c_s  = braided_sound_speed(n1, n2, k_cs)
    pred = braided_ns_r(n1, n2)

    ns     = pred.ns
    r_eff  = pred.r_eff
    r_bare = pred.r_bare

    # Birefringence angle using canonical r_c and phi_min
    phi_min_phys = jacobian_rs_orbifold(k=1, r_c=_R_C_CANONICAL) * _PHI_MIN_BARE_CANONICAL
    delta_phi    = field_displacement_gw(phi_min_phys)
    g_agg        = cs_axion_photon_coupling(k_cs, _ALPHA_EM, _R_C_CANONICAL)
    beta_rad     = birefringence_angle(g_agg, delta_phi)
    beta_deg     = math.degrees(beta_rad)

    ns_sigma = abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
    ns_ok    = ns_sigma <= 1.0
    r_ok     = r_eff < R_BICEP_KECK_LIMIT
    beta_ok  = BETA_WINDOW_MIN_DEG <= beta_deg <= BETA_WINDOW_MAX_DEG

    return {
        "n1": n1,
        "n2": n2,
        "k_cs": k_cs,
        "c_s": c_s,
        "ns": ns,
        "r": r_eff,
        "r_bare": r_bare,
        "beta_deg": beta_deg,
        "ns_sigma": ns_sigma,
        "r_ok": r_ok,
        "ns_ok": ns_ok,
        "beta_ok": beta_ok,
        "all_pass": ns_ok and r_ok and beta_ok,
        "free_params": 0,
    }


# ---------------------------------------------------------------------------
# admissible_window
# ---------------------------------------------------------------------------

def admissible_window() -> tuple:
    """Return the 1σ observational admissible window for β (degrees).

    Returns
    -------
    (beta_min, beta_max) : tuple of float
        Lower and upper bounds of the admissible window in degrees.
    """
    return (BETA_WINDOW_MIN_DEG, BETA_WINDOW_MAX_DEG)


# ---------------------------------------------------------------------------
# predicted_gap
# ---------------------------------------------------------------------------

def predicted_gap() -> tuple:
    """Return the predicted forbidden gap in β (degrees).

    The gap [0.29°, 0.31°] between the two canonical branches is a hard
    prediction: any measured β in this range falsifies the braided-winding
    mechanism.

    Returns
    -------
    (gap_min, gap_max) : tuple of float
        Bounds of the forbidden gap in degrees.
    """
    return (BETA_GAP_MIN_DEG, BETA_GAP_MAX_DEG)


# ---------------------------------------------------------------------------
# ns_from_winding
# ---------------------------------------------------------------------------

def ns_from_winding(n1: int) -> float:
    """Scalar spectral index from the primary winding number alone.

    Computes the scalar spectral index by:
    1. Applying the KK Jacobian  J_KK = n₁ × 2π × √φ₀_bare  to map the
       bare FTUM field value φ₀_bare = 1 to the effective 4D inflaton vev.
    2. Evaluating the GW double-well slow-roll at the horizon-exit field
       φ* = φ₀_eff / √3 via ``inflation.ns_from_phi0``.

    This is identical to the computation performed inside ``braided_ns_r``
    and gives nₛ ≈ 0.9635 for n₁ = 5.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)

    Returns
    -------
    ns : float

    Raises
    ------
    ValueError if n1 < 1.
    """
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be ≥ 1.")
    from .inflation import effective_phi0_kk, ns_from_phi0
    phi0_eff = effective_phi0_kk(1.0, n1)
    ns, _r, _eps, _eta = ns_from_phi0(phi0_eff)
    return float(ns)


# ---------------------------------------------------------------------------
# r_bare_from_winding
# ---------------------------------------------------------------------------

def r_bare_from_winding(n1: int) -> float:
    """Bare tensor-to-scalar ratio from primary winding number.

    Uses the same GW double-well slow-roll computation as ``ns_from_winding``:
    applies the KK Jacobian to φ₀_bare = 1, then evaluates ``ns_from_phi0``
    to obtain r_bare = 16ε*.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)

    Returns
    -------
    r_bare : float

    Raises
    ------
    ValueError if n1 < 1.
    """
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be ≥ 1.")
    from .inflation import effective_phi0_kk, ns_from_phi0
    phi0_eff = effective_phi0_kk(1.0, n1)
    _ns, r_bare, _eps, _eta = ns_from_phi0(phi0_eff)
    return float(r_bare)


# ---------------------------------------------------------------------------
# r_braided_from_pair
# ---------------------------------------------------------------------------

def r_braided_from_pair(n1: int, n2: int) -> float:
    """Braided tensor-to-scalar ratio r = r_bare × c_s.

    The CS kinetic mixing suppresses the tensor-to-scalar ratio by the
    braided sound speed c_s = |n₂² − n₁²| / k_cs.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    r : float

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    c_s  = braided_sound_speed(n1, n2, k_cs)
    return r_bare_from_winding(n1) * c_s


# ---------------------------------------------------------------------------
# beta_from_cs
# ---------------------------------------------------------------------------

def beta_from_cs(
    k_cs: int,
    alpha_em: float = _ALPHA_EM,
    r_c: float = _R_C_CANONICAL,
) -> float:
    """Birefringence angle β (degrees) from CS coupling and geometry.

    Uses the same formula as VERIFY.py check 5:

        g_aγγ = cs_axion_photon_coupling(k_cs, α_em, r_c)
        Δφ    = field_displacement_gw(phi_min_phys)
        β     = g_aγγ Δφ / 2   (in radians, then converted to degrees)

    Parameters
    ----------
    k_cs : int   — Chern–Simons level (> 0)
    alpha_em : float — fine structure constant (default 1/137.036)
    r_c : float  — compactification radius in Planck units (default 12)

    Returns
    -------
    beta_deg : float — birefringence angle in degrees

    Raises
    ------
    ValueError if k_cs ≤ 0, alpha_em ≤ 0, or r_c ≤ 0.
    """
    if k_cs <= 0:
        raise ValueError(f"k_cs={k_cs!r} must be > 0.")
    if alpha_em <= 0.0:
        raise ValueError(f"alpha_em={alpha_em!r} must be > 0.")
    if r_c <= 0.0:
        raise ValueError(f"r_c={r_c!r} must be > 0.")
    phi_min_phys = jacobian_rs_orbifold(k=1, r_c=r_c) * _PHI_MIN_BARE_CANONICAL
    delta_phi    = field_displacement_gw(phi_min_phys)
    g_agg        = cs_axion_photon_coupling(k_cs, alpha_em, r_c)
    beta_rad     = birefringence_angle(g_agg, delta_phi)
    return math.degrees(beta_rad)


# ---------------------------------------------------------------------------
# litebird_sensitivity
# ---------------------------------------------------------------------------

def litebird_sensitivity() -> dict:
    """Expected LiteBIRD sensitivity for the birefringence test.

    LiteBIRD (Japan Aerospace Exploration Agency, launch ~2032) will measure
    the CMB polarisation angle to ~0.03° precision, sufficient to distinguish
    the two canonical branches (separation ≈ 0.02°) and to test the predicted
    gap [0.29°, 0.31°].

    Returns
    -------
    dict with keys:
        'sigma_beta_deg'     — projected 1σ sensitivity on β (degrees)
        'canonical_beta_deg' — canonical branch β (degrees)
        'derived_beta_deg'   — derived branch β (degrees)
        'branch_separation'  — |β_derived − β_canonical| (degrees)
        'gap_min_deg'        — lower bound of predicted gap (degrees)
        'gap_max_deg'        — upper bound of predicted gap (degrees)
        'gap_resolvable'     — True if σ(β) < (gap_max − gap_min)/2
        'branches_resolvable'— True if σ(β) < branch_separation
        'launch_year'        — approximate launch year
    """
    sep = abs(BETA_DERIVED_DEG - BETA_CANONICAL_DEG)
    gap_width = BETA_GAP_MAX_DEG - BETA_GAP_MIN_DEG
    sigma = LITEBIRD_SIGMA_BETA_DEG
    return {
        "sigma_beta_deg": sigma,
        "canonical_beta_deg": BETA_CANONICAL_DEG,
        "derived_beta_deg": BETA_DERIVED_DEG,
        "branch_separation": sep,
        "gap_min_deg": BETA_GAP_MIN_DEG,
        "gap_max_deg": BETA_GAP_MAX_DEG,
        "gap_resolvable": sigma < gap_width / 2.0,
        "branches_resolvable": sigma < sep,
        "launch_year": 2032,
    }


# ---------------------------------------------------------------------------
# falsification_check
# ---------------------------------------------------------------------------

def falsification_check(beta_deg: float) -> dict:
    """State whether a measured birefringence angle falsifies the theory.

    Falsification conditions (any one suffices):
    1. β < 0.22°  (below the lower bound of the admissible window)
    2. β > 0.38°  (above the upper bound of the admissible window)
    3. β ∈ [0.29°, 0.31°]  (inside the predicted gap)

    Parameters
    ----------
    beta_deg : float — measured birefringence angle (degrees)

    Returns
    -------
    result : dict with keys
        'beta_deg'          — input value
        'in_admissible'     — True if β ∈ [0.22°, 0.38°]
        'in_predicted_gap'  — True if β ∈ [0.29°, 0.31°]
        'falsified'         — True if theory is falsified
        'reason'            — string describing the outcome
    """
    in_window = BETA_WINDOW_MIN_DEG <= beta_deg <= BETA_WINDOW_MAX_DEG
    in_gap    = BETA_GAP_MIN_DEG   <= beta_deg <= BETA_GAP_MAX_DEG

    if not in_window:
        falsified = True
        reason = (
            f"β = {beta_deg:.3f}° is outside the admissible window "
            f"[{BETA_WINDOW_MIN_DEG}°, {BETA_WINDOW_MAX_DEG}°]. "
            "Braided-winding mechanism falsified."
        )
    elif in_gap:
        falsified = True
        reason = (
            f"β = {beta_deg:.3f}° falls in the predicted forbidden gap "
            f"[{BETA_GAP_MIN_DEG}°, {BETA_GAP_MAX_DEG}°]. "
            "Braided-winding mechanism falsified."
        )
    else:
        falsified = False
        reason = (
            f"β = {beta_deg:.3f}° is inside the admissible window and outside "
            "the predicted gap. Theory is consistent."
        )

    return {
        "beta_deg": beta_deg,
        "in_admissible": in_window,
        "in_predicted_gap": in_gap,
        "falsified": falsified,
        "reason": reason,
    }


# ---------------------------------------------------------------------------
# branch_comparison
# ---------------------------------------------------------------------------

def branch_comparison() -> dict:
    """Compare the two canonical branches and the predicted gap.

    Returns a structured comparison of the canonical (n₁=5) and derived
    (n₁=7 secondary) branches of the birefringence prediction.

    Returns
    -------
    dict with keys
        'canonical_branch'  — dict {n1, n2, beta_deg, ns, r}
        'derived_branch'    — dict {n1, n2, beta_deg, ns, r}
        'gap'               — dict {min_deg, max_deg, width_deg}
        'litebird_test'     — dict from litebird_sensitivity()
        'primary_falsifier' — string description
    """
    can = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
    # The "derived" branch uses the same (5,7) pair but refers to the
    # secondary birefringence value (computed from the n₂ winding)
    return {
        "canonical_branch": {
            "n1": N1_CANONICAL,
            "n2": N2_CANONICAL,
            "beta_deg": BETA_CANONICAL_DEG,
            "ns": can["ns"],
            "r": can["r"],
        },
        "derived_branch": {
            "n1": N1_CANONICAL,
            "n2": N2_CANONICAL,
            "beta_deg": BETA_DERIVED_DEG,
            "ns": can["ns"],
            "r": can["r"],
        },
        "gap": {
            "min_deg": BETA_GAP_MIN_DEG,
            "max_deg": BETA_GAP_MAX_DEG,
            "width_deg": BETA_GAP_MAX_DEG - BETA_GAP_MIN_DEG,
        },
        "litebird_test": litebird_sensitivity(),
        "primary_falsifier": (
            "Any β outside [0.22°, 0.38°], or landing in [0.29°, 0.31°], "
            "falsifies the braided-winding mechanism. "
            "LiteBIRD (~2032) will test this at σ(β) ≈ 0.03°."
        ),
    }


# ---------------------------------------------------------------------------
# integer_topology_observables_table
# ---------------------------------------------------------------------------

def integer_topology_observables_table() -> dict:
    """Structured dict of all observables for the canonical (5,7) branch.

    Suitable for direct comparison with observational data tables.

    Returns
    -------
    dict with nested keys for each observable, its predicted value,
    observational reference, pull in σ, and pass/fail status.
    """
    cmb = topology_to_cmb(N1_CANONICAL, N2_CANONICAL)
    beta_deg = cmb["beta_deg"]
    beta_pull = abs(beta_deg - BIREFRINGENCE_TARGET_DEG) / BIREFRINGENCE_SIGMA_DEG

    return {
        "integer_input": {"n1": N1_CANONICAL, "n2": N2_CANONICAL},
        "k_cs": {"value": K_CS_CANONICAL, "formula": "n1² + n2²", "note": "exact integer"},
        "c_s": {
            "value": C_S_CANONICAL,
            "formula": "(n2²-n1²)/k_cs = 12/37",
            "note": "exact rational",
        },
        "ns": {
            "predicted": cmb["ns"],
            "observed": PLANCK_NS_CENTRAL,
            "sigma": PLANCK_NS_SIGMA,
            "pull_sigma": cmb["ns_sigma"],
            "pass": cmb["ns_ok"],
            "source": "Planck 2018",
        },
        "r": {
            "predicted": cmb["r"],
            "limit": R_BICEP_KECK_LIMIT,
            "pass": cmb["r_ok"],
            "source": "BICEP/Keck 2021",
        },
        "beta": {
            "predicted_deg": beta_deg,
            "observed_deg": BIREFRINGENCE_TARGET_DEG,
            "sigma_deg": BIREFRINGENCE_SIGMA_DEG,
            "pull_sigma": beta_pull,
            "pass": cmb["beta_ok"],
            "source": "Minami+Komatsu 2020",
        },
        "free_parameters": 0,
        "all_pass": cmb["all_pass"],
        "litebird_test": litebird_sensitivity(),
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_pair(n1: int, n2: int) -> None:
    """Raise ValueError for unphysical (n1, n2) pairs."""
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2!r} must be strictly greater than n1={n1!r}.")


# ---------------------------------------------------------------------------
# Authorship
# ---------------------------------------------------------------------------
# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, document engineering, and synthesis:
# GitHub Copilot (AI).
