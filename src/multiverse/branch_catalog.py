# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/multiverse/branch_catalog.py
=================================
Branch Catalog — lossless/lossy classification of all (n₁, n₂) winding branches.

Background (Q28 in BIG_QUESTIONS.md)
--------------------------------------
The compact S¹/Z₂ fifth dimension of the Unitary Manifold supports an infinite
discrete tower of winding modes labelled by positive integer pairs (n₁, n₂) with
n₁ < n₂.  For each pair the resonant Chern–Simons level is

    k_cs = n₁² + n₂²                                                 [SOS resonance]

giving braided sound speed

    c_s = (n₂² − n₁²) / k_cs   =  (n₂ − n₁)(n₁ + n₂) / (n₁² + n₂²)

and a unique triple of CMB observables (nₛ, r_eff, β).

The **lossless condition** — that the information current
J^μ_inf = φ² u^μ is exactly conserved (∇_μ J^μ_inf = 0) — requires that the
5D radion φ reaches the Goldberger–Wise minimum and the FTUM fixed point
U Ψ* = Ψ* is fully satisfied.  In the CMB sector this corresponds to the
branch simultaneously satisfying all three observational constraints:

    |nₛ − 0.9649| / 0.0042 ≤ 2          (Planck 2018 2σ window)
    r_eff < 0.036                         (BICEP/Keck 2021 95 % CL)
    |β − 0.35°| / 0.14° ≤ 1              (Minami–Komatsu 2020 1σ window)

Only the canonical (n₁, n₂) = (5, 7) branch satisfies all three without
any free-parameter tuning:

    nₛ = 0.9635   (0.33σ from Planck central)
    r   = 0.0315  (below BICEP/Keck limit of 0.036)
    β   = 0.351°  (inside 1σ window; k_cs=74 is the unique birefringence match)

Every other branch violates at least one constraint, making it *lossy*.

Loss function
-------------
For each branch the **loss function** is defined as the maximum normalised
violation across the three observational constraints:

    L_ns   = max(0,  |nₛ − 0.9649| / 0.0042 − 2.0)   (0 if within 2σ)
    L_r    = max(0,  (r_eff − 0.036) / 0.036)           (0 if satisfies BICEP)
    L_beta = max(0,  |β − 0.35°| / 0.14° − 1.0)         (0 if within 1σ)

    L = max(L_ns, L_r, L_beta)

L = 0 (lossless) iff all three constraints are simultaneously satisfied.
L > 0 (lossy) otherwise.

By construction the canonical (5, 7) branch has L = 0.  A numerical sweep over
all (n₁, n₂) pairs with n_max ≤ 20 confirms this is the **unique** lossless
branch in the catalog.

Public API
----------
BranchRecord
    Dataclass holding all CMB observables and the loss function for one branch.

classify_branch(n1, n2) -> BranchRecord
    Compute all observables and the loss function for a single (n₁, n₂) pair
    at the sum-of-squares resonance k_cs = n₁² + n₂².

full_branch_catalog(n_max) -> list[BranchRecord]
    Enumerate every ordered pair (n₁, n₂) with 1 ≤ n₁ < n₂ ≤ n_max and
    return the full list of BranchRecord objects, sorted by k_cs.

LOSSLESS_N1, LOSSLESS_N2, LOSSLESS_KCS
    Module-level constants for the canonical (5, 7) branch.

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
from dataclasses import dataclass
from typing import List

import numpy as np

from ..core.braided_winding import (
    braided_ns_r,
    braided_sound_speed,
    resonant_kcs,
    BraidedPrediction,
    _ALPHA_EM_CANONICAL,
    _R_C_CANONICAL,
    _canonical_phi_min_phys,
)
from ..core.inflation import (
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    BIREFRINGENCE_TARGET_DEG,
    BIREFRINGENCE_SIGMA_DEG,
    cs_axion_photon_coupling,
    field_displacement_gw,
    birefringence_angle,
)
from ..core.braided_winding import R_BICEP_KECK_95


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Canonical lossless branch winding numbers
LOSSLESS_N1: int = 5
LOSSLESS_N2: int = 7
#: Canonical Chern–Simons level  5² + 7² = 74
LOSSLESS_KCS: int = 74
#: Canonical braided sound speed  c_s = 12/37
LOSSLESS_CS: float = 12.0 / 37.0

# ---------------------------------------------------------------------------
# Loss-function tolerances (used in _compute_loss)
# ---------------------------------------------------------------------------

_NS_SIGMA_WINDOW: float = 2.0        # accept within 2σ of Planck nₛ
_BETA_SIGMA_WINDOW: float = 1.0      # accept within 1σ birefringence window


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class BranchRecord:
    """CMB observables and lossiness for a single braided (n₁, n₂) branch.

    Attributes
    ----------
    n1, n2       : int   — winding numbers (n₁ < n₂)
    k_cs         : int   — Chern–Simons level (= n₁² + n₂², SOS resonance)
    c_s          : float — braided adiabatic sound speed
    ns           : float — CMB scalar spectral index prediction
    r_eff        : float — effective tensor-to-scalar ratio
    beta_deg     : float — birefringence angle β  [degrees]
    ns_sigma     : float — |nₛ − 0.9649| / 0.0042  (Planck tension in σ)
    loss_function: float — combined normalised constraint violation L ≥ 0;
                           L = 0 means lossless (all three constraints satisfied)
    is_lossless  : bool  — True iff loss_function == 0
    """

    n1: int
    n2: int
    k_cs: int
    c_s: float
    ns: float
    r_eff: float
    beta_deg: float
    ns_sigma: float
    loss_function: float
    is_lossless: bool


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _birefringence_deg(k_cs: int) -> float:
    """Birefringence angle in degrees for a given CS level at canonical params.

    Uses the flat S¹/Z₂ formula with the canonical compactification radius
    r_c = 12 M_Pl⁻¹ and field displacement Δφ ≈ 5.38 M_Pl.
    """
    phi_min_phys = _canonical_phi_min_phys(_R_C_CANONICAL)
    g_agg = cs_axion_photon_coupling(k_cs, _ALPHA_EM_CANONICAL, _R_C_CANONICAL)
    delta_phi = field_displacement_gw(phi_min_phys)
    return float(np.degrees(birefringence_angle(g_agg, delta_phi)))


def _compute_loss(ns: float, r_eff: float, beta_deg: float) -> float:
    """Compute the branch loss function from three CMB observables.

    Returns the maximum normalised constraint violation:

        L_ns   = max(0, |nₛ−0.9649|/0.0042 − 2.0)
        L_r    = max(0, (r_eff − 0.036) / 0.036)
        L_beta = max(0, |β−0.35°|/0.14° − 1.0)
        L      = max(L_ns, L_r, L_beta)

    Parameters
    ----------
    ns      : float — spectral index
    r_eff   : float — tensor-to-scalar ratio
    beta_deg: float — birefringence angle [degrees]

    Returns
    -------
    float — L ≥ 0; L = 0 iff all constraints are satisfied
    """
    L_ns = max(0.0, abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
               - _NS_SIGMA_WINDOW)
    L_r = max(0.0, (r_eff - R_BICEP_KECK_95) / R_BICEP_KECK_95)
    L_beta = max(0.0, abs(beta_deg - BIREFRINGENCE_TARGET_DEG)
                 / BIREFRINGENCE_SIGMA_DEG - _BETA_SIGMA_WINDOW)
    return float(max(L_ns, L_r, L_beta))


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def classify_branch(n1: int, n2: int) -> BranchRecord:
    """Classify a single (n₁, n₂) branch and compute its loss function.

    Uses the sum-of-squares resonance CS level k_cs = n₁² + n₂².
    CMB spectral observables (nₛ, r_eff) come from
    :func:`src.core.braided_winding.braided_ns_r` using the dominant (n₁)
    winding mode for the slow-roll potential.
    The birefringence angle β is computed from the canonical flat S¹/Z₂
    formula at r_c = 12 M_Pl⁻¹.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    BranchRecord

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    if n1 < 1:
        raise ValueError(f"n1={n1} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2} must be strictly greater than n1={n1}.")

    k_cs = resonant_kcs(n1, n2)
    pred: BraidedPrediction = braided_ns_r(n1, n2, k_cs=k_cs)
    beta_deg = _birefringence_deg(k_cs)
    loss = _compute_loss(pred.ns, pred.r_eff, beta_deg)

    return BranchRecord(
        n1=n1,
        n2=n2,
        k_cs=k_cs,
        c_s=pred.c_s,
        ns=pred.ns,
        r_eff=pred.r_eff,
        beta_deg=beta_deg,
        ns_sigma=pred.ns_sigma,
        loss_function=loss,
        is_lossless=bool(loss == 0.0),
    )


def full_branch_catalog(n_max: int = 10) -> List[BranchRecord]:
    """Enumerate all (n₁, n₂) branches with 1 ≤ n₁ < n₂ ≤ n_max.

    Returns all branches sorted by ascending k_cs = n₁² + n₂².

    Parameters
    ----------
    n_max : int — maximum winding number to include (default 10)

    Returns
    -------
    list[BranchRecord] — full catalog, length = n_max × (n_max − 1) / 2

    Raises
    ------
    ValueError if n_max < 2.
    """
    if n_max < 2:
        raise ValueError(f"n_max={n_max} must be ≥ 2 (need at least one pair).")

    records: List[BranchRecord] = []
    for n1 in range(1, n_max):
        for n2 in range(n1 + 1, n_max + 1):
            records.append(classify_branch(n1, n2))

    records.sort(key=lambda r: r.k_cs)
    return records


def lossless_branches(catalog: List[BranchRecord]) -> List[BranchRecord]:
    """Return the subset of BranchRecord objects that are lossless (L = 0).

    Parameters
    ----------
    catalog : list[BranchRecord] — typically from :func:`full_branch_catalog`

    Returns
    -------
    list[BranchRecord] — only entries with is_lossless == True
    """
    return [r for r in catalog if r.is_lossless]


def catalog_summary(catalog: List[BranchRecord]) -> dict:
    """Return a summary dict for a branch catalog.

    Keys
    ----
    n_total        : int   — total number of branches
    n_lossless     : int   — number of lossless branches
    n_lossy        : int   — number of lossy branches
    lossless_pairs : list  — (n1, n2) tuples for lossless branches
    min_loss       : float — smallest loss value in the catalog
    max_loss       : float — largest loss value
    mean_loss      : float — arithmetic mean over all branches
    canonical_present : bool — True iff (5, 7) is in the catalog
    """
    n_total = len(catalog)
    lossless = lossless_branches(catalog)
    losses = [r.loss_function for r in catalog]
    canonical_in = any(r.n1 == LOSSLESS_N1 and r.n2 == LOSSLESS_N2
                       for r in catalog)
    return {
        "n_total": n_total,
        "n_lossless": len(lossless),
        "n_lossy": n_total - len(lossless),
        "lossless_pairs": [(r.n1, r.n2) for r in lossless],
        "min_loss": float(min(losses)) if losses else float("nan"),
        "max_loss": float(max(losses)) if losses else float("nan"),
        "mean_loss": float(sum(losses) / n_total) if losses else float("nan"),
        "canonical_present": canonical_in,
    }
