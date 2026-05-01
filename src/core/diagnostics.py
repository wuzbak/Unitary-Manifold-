# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/diagnostics.py
=======================
High-level diagnostic helpers for the Unitary Manifold CMB pipeline.

This module bridges the low-level physics functions in ``transfer.py`` and
``inflation.py`` with the observational tolerance validation layer.  It
provides six consolidated entry-points that map directly onto the required
API surface identified during the pre-implementation inspection:

Required API  →  Implementation
─────────────────────────────────────────────────────────────────────────
compute_cmb_spectra        wraps angular_power_spectrum + dl_from_cl
extract_observables        wraps effective_phi0_kk + ns_from_phi0 +
                              triple_constraint + chi2_planck
compute_chi2_landscape     2-D parameter scan over chi2_planck
compute_polarization_ratios  wraps tb_eb_spectrum → frequency ratios
estimate_numerical_error   compares Cₗ at two k-grid resolutions
convergence_check          Richardson-style convergence over n_k sequence
─────────────────────────────────────────────────────────────────────────

Units and consistency
---------------------
* nₛ              — dimensionless, range ~ [0.9, 1.0]
* ells            — non-negative integers ≥ 2
* Cₗ              — dimensionless angular power spectrum
* Dₗ              — μK² (Planck convention: ℓ(ℓ+1)Cₗ/(2π) × T_CMB²)
* β₀              — **radians** (all internal calculations; convert to degrees
                    only for comparison with observational tables)
* φ₀_bare         — Planck units (M_Pl = 1)
* chi2, chi2_dof  — dimensionless
* relative error  — dimensionless fraction, e.g. 0.01 = 1 %
* pol ratio       — dimensionless ratio C_TB(ν₁)/C_TB(ν₂)

Public API
----------
compute_cmb_spectra(ns, ells, n_k, ...)
    Cₗ and Dₗ for a given nₛ and multipole list.

extract_observables(phi0_bare, n_winding, k_cs, alpha_em, r_c,
                    phi_min_phys, ells, n_k)
    Full causal chain → (nₛ, r, β_deg, α, χ², χ²/dof, n_dof).

compute_chi2_landscape(phi0_grid, n_winding_values, ells, n_k)
    2-D χ² surface over (φ₀_bare, n_w) parameter space.

compute_polarization_ratios(ells, nu_array, beta_0, ns, nu_ref_idx,
                            n_k, frequency_achromatic)
    Frequency ratios C_TB(νᵢ)/C_TB(ν_ref) and C_EB(νᵢ)/C_EB(ν_ref).

estimate_numerical_error(ns, ells, n_k_coarse, n_k_fine)
    Per-multipole relative Cₗ error between coarse and fine k-grids.

convergence_check(ns, ells, n_k_sequence)
    Convergence table and flag as n_k → ∞.
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

from typing import List, Sequence

import numpy as np

from .inflation import (
    effective_phi0_kk,
    ns_from_phi0,
    triple_constraint,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
)

from .transfer import (
    angular_power_spectrum,
    dl_from_cl,
    chi2_planck,
    tb_eb_spectrum,
    PLANCK_2018_DL_REF,
    PLANCK_2018_COSMO,
)

# ---------------------------------------------------------------------------
# Internal defaults
# ---------------------------------------------------------------------------

_ELLS_DEFAULT: List[int] = sorted(PLANCK_2018_DL_REF.keys())
_N_K_DEFAULT: int = 600
_ALPHA_EM_DEFAULT: float = 1.0 / 137.036


# ===========================================================================
# 1. compute_cmb_spectra
# ===========================================================================

def compute_cmb_spectra(
    ns: float,
    ells: Sequence[int] | None = None,
    n_k: int = _N_K_DEFAULT,
    As: float = PLANCK_2018_COSMO["As"],
    k_pivot: float = PLANCK_2018_COSMO["k_pivot"],
    chi_star: float = PLANCK_2018_COSMO["chi_star"],
    rs_star: float = PLANCK_2018_COSMO["rs_star"],
    k_silk: float = PLANCK_2018_COSMO["k_silk"],
    silk_exponent: float = PLANCK_2018_COSMO["silk_exponent"],
    T_cmb_K: float = PLANCK_2018_COSMO["T_cmb_K"],
) -> dict:
    """Compute CMB TT power spectra Cₗ and Dₗ for a given nₛ.

    Convenience wrapper around :func:`~.transfer.angular_power_spectrum` and
    :func:`~.transfer.dl_from_cl` that bundles the outputs into a single
    labelled dict and validates inputs.

    Parameters
    ----------
    ns        : float            — scalar spectral index nₛ (dimensionless)
    ells      : sequence of int  — multipoles to evaluate (default: Planck
                                   reference multipoles from PLANCK_2018_DL_REF)
    n_k       : int              — number of log-spaced k points (accuracy
                                   control; default 600)
    As        : float            — primordial amplitude Aₛ [dimensionless]
    k_pivot   : float            — pivot wavenumber [Mpc⁻¹]
    chi_star  : float            — comoving distance to last scattering [Mpc]
    rs_star   : float            — sound horizon at recombination [Mpc]
    k_silk    : float            — Silk damping wavenumber [Mpc⁻¹]
    silk_exponent : float        — Silk damping exponent
    T_cmb_K   : float            — CMB temperature [K] (for Dₗ conversion)

    Returns
    -------
    dict with keys:

    ``ells``  : ndarray, shape (n_ell,) int   — multipoles
    ``Cl``    : ndarray, shape (n_ell,) float — dimensionless power spectrum Cₗ
    ``Dl``    : ndarray, shape (n_ell,) float — power spectrum Dₗ [μK²]
    ``ns``    : float                          — input nₛ (echoed)
    ``n_k``   : int                            — k-grid resolution used

    Raises
    ------
    ValueError
        If nₛ is not finite, ells is empty, or n_k < 50.
    """
    if not np.isfinite(ns):
        raise ValueError(f"ns={ns!r} must be finite.")
    if n_k < 50:
        raise ValueError(f"n_k={n_k!r} must be ≥ 50 for reliable integration.")
    if ells is None:
        ells = _ELLS_DEFAULT
    ells_arr = np.asarray(ells, dtype=int)
    if len(ells_arr) == 0:
        raise ValueError("ells must contain at least one multipole.")

    Cl = angular_power_spectrum(
        ells_arr, ns, As=As, k_pivot=k_pivot, chi_star=chi_star,
        rs_star=rs_star, k_silk=k_silk, silk_exponent=silk_exponent,
        n_k=n_k,
    )
    Dl = dl_from_cl(ells_arr, Cl, T_cmb_K=T_cmb_K)
    return {
        "ells": ells_arr,
        "Cl":   Cl,
        "Dl":   Dl,
        "ns":   float(ns),
        "n_k":  int(n_k),
    }


# ===========================================================================
# 2. extract_observables
# ===========================================================================

def extract_observables(
    phi0_bare: float = 1.0,
    n_winding: int = 5,
    k_cs: int = 74,
    alpha_em: float = _ALPHA_EM_DEFAULT,
    r_c: float = 12.0,
    phi_min_phys: float | None = None,
    ells: Sequence[int] | None = None,
    n_k: int = _N_K_DEFAULT,
) -> dict:
    """Run the full causal chain and return all CMB observables.

    Executes the pipeline::

        φ₀_bare, n_w → KK Jacobian → φ₀_eff
                     → ns_from_phi0 → (nₛ, r, ε, η)
                     → triple_constraint → β_deg
                     → α = φ₀⁻²
                     → compute_cmb_spectra → Cₗ, Dₗ
                     → chi2_planck → χ², χ²/dof

    Parameters
    ----------
    phi0_bare   : float — bare FTUM radion vev (Planck units; default 1.0)
    n_winding   : int   — KK winding number (default 5 for flat S¹/Z₂)
    k_cs        : int   — Chern–Simons level (default 74)
    alpha_em    : float — fine-structure constant (default 1/137.036)
    r_c         : float — compactification radius (Planck units; default 12.0)
    phi_min_phys: float — physical GW minimum for Δφ; if None, computed from
                          the RS Jacobian with k=1, r_c as given.
    ells        : sequence of int — multipoles for χ² comparison (default:
                  Planck reference table multipoles)
    n_k         : int   — k-grid resolution for CMB integration (default 600)

    Returns
    -------
    dict with keys:

    ``phi0_eff``  : float — effective 4D inflaton vev after KK Jacobian
    ``ns``        : float — scalar spectral index nₛ
    ``r``         : float — tensor-to-scalar ratio r = 16ε
    ``epsilon``   : float — slow-roll parameter ε
    ``eta``       : float — slow-roll parameter η
    ``beta_deg``  : float — birefringence angle β [degrees]
    ``alpha``     : float — nonminimal coupling α = φ₀⁻²
    ``chi2``      : float — total χ² vs Planck 2018
    ``chi2_dof``  : float — reduced χ²/dof
    ``n_dof``     : int   — number of matched multipoles
    ``Dl``        : ndarray — predicted Dₗ [μK²] at the reference multipoles
    ``ells``      : ndarray — multipoles used for χ²

    Raises
    ------
    ValueError via underlying functions for unphysical inputs.
    """
    from .inflation import jacobian_rs_orbifold, field_displacement_gw

    phi0_eff = effective_phi0_kk(phi0_bare, n_winding)

    if phi_min_phys is None:
        J_rs = jacobian_rs_orbifold(1.0, r_c)
        phi_min_phys = J_rs * 18.0   # canonical bare minimum × RS Jacobian

    result = triple_constraint(
        phi0_eff=phi0_eff,
        k_cs=k_cs,
        alpha_em=alpha_em,
        r_c=r_c,
        phi_min_phys=float(phi_min_phys),
    )
    alpha = float(phi0_bare ** -2)

    spectra = compute_cmb_spectra(result["ns"], ells=ells, n_k=n_k)
    chi2, chi2_dof, n_dof = chi2_planck(spectra["ells"], spectra["Dl"])

    return {
        "phi0_eff":  float(phi0_eff),
        "ns":        result["ns"],
        "r":         result["r"],
        "epsilon":   result["epsilon"],
        "eta":       result["eta"],
        "beta_deg":  result["beta_deg"],
        "g_agg":     result["g_agg"],
        "delta_phi": result["delta_phi"],
        "alpha":     alpha,
        "chi2":      chi2,
        "chi2_dof":  chi2_dof,
        "n_dof":     n_dof,
        "Dl":        spectra["Dl"],
        "ells":      spectra["ells"],
    }


# ===========================================================================
# 3. compute_chi2_landscape
# ===========================================================================

def compute_chi2_landscape(
    phi0_grid: Sequence[float],
    n_winding_values: Sequence[int],
    ells: Sequence[int] | None = None,
    n_k: int = _N_K_DEFAULT,
) -> dict:
    """Compute a 2-D χ² landscape over (φ₀_bare, n_winding) parameter space.

    For each point (φ₀_bare, n_w) in the grid, computes the predicted nₛ and
    evaluates χ² against the Planck 2018 Dₗ reference table.

    Parameters
    ----------
    phi0_grid         : sequence of float — φ₀_bare values to scan (Planck units)
    n_winding_values  : sequence of int   — winding numbers to scan
    ells              : sequence of int   — multipoles for χ² (default: Planck table)
    n_k               : int               — k-grid resolution (default 600)

    Returns
    -------
    dict with keys:

    ``phi0_grid``       : ndarray, shape (n_phi,)        — input φ₀ values
    ``n_winding_values``: ndarray, shape (n_w,) int      — input winding numbers
    ``ns_matrix``       : ndarray, shape (n_phi, n_w)    — predicted nₛ at each point
    ``chi2_matrix``     : ndarray, shape (n_phi, n_w)    — χ² at each point
    ``chi2_dof_matrix`` : ndarray, shape (n_phi, n_w)    — χ²/dof at each point
    ``best_phi0``       : float — φ₀_bare at the χ² minimum
    ``best_n_winding``  : int   — n_winding at the χ² minimum
    ``best_chi2``       : float — minimum χ² value
    """
    phi0_arr = np.asarray(phi0_grid, dtype=float)
    nw_arr   = np.asarray(n_winding_values, dtype=int)
    n_phi = len(phi0_arr)
    n_w   = len(nw_arr)

    if ells is None:
        ells = _ELLS_DEFAULT
    ells_arr = np.asarray(ells, dtype=int)

    ns_matrix       = np.empty((n_phi, n_w))
    chi2_matrix     = np.empty((n_phi, n_w))
    chi2_dof_matrix = np.empty((n_phi, n_w))

    for i, phi0 in enumerate(phi0_arr):
        for j, nw in enumerate(nw_arr):
            phi0_eff = effective_phi0_kk(float(phi0), int(nw))
            ns, _, _, _ = ns_from_phi0(phi0_eff)
            spectra = compute_cmb_spectra(ns, ells=ells_arr, n_k=n_k)
            chi2, chi2_dof, _ = chi2_planck(ells_arr, spectra["Dl"])
            ns_matrix[i, j]       = ns
            chi2_matrix[i, j]     = chi2
            chi2_dof_matrix[i, j] = chi2_dof

    best_flat = int(np.argmin(chi2_matrix))
    best_i, best_j = divmod(best_flat, n_w)
    # NOTE: with the simplified SW+acoustic transfer function the returned
    # best_phi0 / best_n_winding reflect the *amplitude-driven* χ² minimum
    # (lower nₛ partially compensates the ~5–7× amplitude underprediction).
    # They do NOT represent the Planck-favoured parameter point.  Use this
    # result only for *relative* Δχ² comparisons, not for absolute inference.

    return {
        "phi0_grid":        phi0_arr,
        "n_winding_values": nw_arr,
        "ns_matrix":        ns_matrix,
        "chi2_matrix":      chi2_matrix,
        "chi2_dof_matrix":  chi2_dof_matrix,
        "best_phi0":        float(phi0_arr[best_i]),
        "best_n_winding":   int(nw_arr[best_j]),
        "best_chi2":        float(chi2_matrix[best_i, best_j]),
    }


# ===========================================================================
# 4. compute_polarization_ratios
# ===========================================================================

def compute_polarization_ratios(
    ells: Sequence[int],
    nu_array: Sequence[float],
    beta_0: float,
    ns: float,
    nu_ref_idx: int = 0,
    n_k: int = _N_K_DEFAULT,
    frequency_achromatic: bool = True,
) -> dict:
    """Compute frequency-ratio spectra C_TB(ν)/C_TB(ν_ref) and C_EB analogues.

    Calls :func:`~.transfer.tb_eb_spectrum` and normalises all frequency
    channels against the reference channel at index ``nu_ref_idx``.

    Parameters
    ----------
    ells               : sequence of int   — multipoles ℓ
    nu_array           : sequence of float — observing frequencies [GHz]
    beta_0             : float             — birefringence angle β₀ [**radians**]
    ns                 : float             — scalar spectral index nₛ
    nu_ref_idx         : int               — index of reference frequency in nu_array
                                             (default 0)
    n_k                : int               — k-grid resolution (default 600)
    frequency_achromatic : bool            — True → UL-axion; False → Faraday

    Returns
    -------
    dict with keys:

    ``ells``          : ndarray, shape (n_ell,)
    ``nu_array``      : ndarray, shape (n_nu,)
    ``nu_ref``        : float — reference frequency [GHz]
    ``ratio_TB``      : ndarray, shape (n_ell, n_nu) — C_TB(ν)/C_TB(ν_ref);
                        column at nu_ref_idx is 1.0 by construction
    ``ratio_EB``      : ndarray, shape (n_ell, n_nu) — C_EB(ν)/C_EB(ν_ref)
    ``C_TE``          : ndarray, shape (n_ell,)
    ``C_EE``          : ndarray, shape (n_ell,)
    ``C_TB``          : ndarray, shape (n_ell, n_nu) — raw TB spectra
    ``C_EB``          : ndarray, shape (n_ell, n_nu) — raw EB spectra
    ``frequency_achromatic`` : bool

    Raises
    ------
    ValueError if nu_ref_idx is out of range or any C_TB reference column is
    identically zero (β₀ = 0).
    """
    nu_arr   = np.asarray(nu_array, dtype=float)
    ells_arr = np.asarray(ells,     dtype=int)

    if nu_ref_idx < 0 or nu_ref_idx >= len(nu_arr):
        raise ValueError(
            f"nu_ref_idx={nu_ref_idx!r} out of range for nu_array of "
            f"length {len(nu_arr)}."
        )

    out = tb_eb_spectrum(
        ells=ells_arr, nu_array=nu_arr,
        beta_0=beta_0, ns=ns,
        n_k=n_k,
        frequency_achromatic=frequency_achromatic,
    )

    C_TB_ref = out["C_TB"][:, nu_ref_idx]   # shape (n_ell,)
    C_EB_ref = out["C_EB"][:, nu_ref_idx]

    # Build ratio arrays; guard against division by zero at C_TE sign changes
    ratio_TB = np.empty_like(out["C_TB"])
    ratio_EB = np.empty_like(out["C_EB"])
    for i in range(len(ells_arr)):
        if abs(C_TB_ref[i]) < 1e-40:
            ratio_TB[i, :] = np.nan
        else:
            ratio_TB[i, :] = out["C_TB"][i, :] / C_TB_ref[i]
        if abs(C_EB_ref[i]) < 1e-40:
            ratio_EB[i, :] = np.nan
        else:
            ratio_EB[i, :] = out["C_EB"][i, :] / C_EB_ref[i]

    return {
        "ells":                  ells_arr,
        "nu_array":              nu_arr,
        "nu_ref":                float(nu_arr[nu_ref_idx]),
        "ratio_TB":              ratio_TB,
        "ratio_EB":              ratio_EB,
        "C_TE":                  out["C_TE"],
        "C_EE":                  out["C_EE"],
        "C_TB":                  out["C_TB"],
        "C_EB":                  out["C_EB"],
        "frequency_achromatic":  bool(frequency_achromatic),
    }


# ===========================================================================
# 5. estimate_numerical_error
# ===========================================================================

def estimate_numerical_error(
    ns: float,
    ells: Sequence[int] | None = None,
    n_k_coarse: int = 300,
    n_k_fine: int = 1200,
) -> dict:
    """Estimate the per-multipole numerical integration error in CMB spectra.

    Computes Cₗ (and Dₗ) at two k-grid resolutions and reports both a
    raw relative Cₗ error **and** the physically meaningful χ²-weighted Dₗ
    error — |ΔDₗ| / σₗ — where σₗ is the Planck 2018 1-σ uncertainty at
    each matched multipole.  The χ²-weighted metric is the correct tolerance
    measure: a value < 1 means the numerical error is sub-Planck.

    **Source of σₗ**: the uncertainties come from ``PLANCK_2018_DL_REF``
    (``transfer.py``), which stores approximate Planck 2018 TT 1-σ values
    taken from arXiv:1807.06209 (Table 1 / Fig. 1), rounded to the nearest
    5 μK².  These are *real* observational uncertainties, not 10%-of-Dₗ
    placeholders.  The rounded figures are adequate for deciding whether
    numerical errors are sub-Planck, but they should be replaced with
    the precise published Planck 2018 band-power uncertainties before using
    ``chi2_error_per_ell`` for any absolute inference.

    At Silk-damped high-ℓ multipoles the raw relative Cₗ error can be large
    (Cₗ → 0), but the **absolute** Dₗ difference remains negligible compared
    with σₗ.  Always use ``chi2_error_per_ell`` for observational relevance.

    Parameters
    ----------
    ns         : float     — scalar spectral index
    ells       : sequence  — multipoles; defaults to Planck reference table
    n_k_coarse : int       — coarse k-grid size (default 300)
    n_k_fine   : int       — fine k-grid size (default 1200)

    Returns
    -------
    dict with keys:

    ``ells``                : ndarray, shape (n_ell,)
    ``Cl_coarse``           : ndarray — Cₗ at n_k_coarse
    ``Cl_fine``             : ndarray — Cₗ at n_k_fine
    ``Dl_coarse``           : ndarray — Dₗ at n_k_coarse [μK²]
    ``Dl_fine``             : ndarray — Dₗ at n_k_fine [μK²]
    ``abs_Dl_error``        : ndarray — |Dₗ_fine − Dₗ_coarse| [μK²]
    ``chi2_error_per_ell``  : ndarray — |ΔDₗ|/σₗ at Planck-matched ells
                              (NaN for ells not in the Planck table)
    ``max_chi2_error``      : float — max |ΔDₗ|/σₗ over matched multipoles
    ``total_chi2_error``    : float — Σ (ΔDₗ/σₗ)² — numerical χ² contribution
    ``rel_error_cl``        : ndarray — |Cₗ_fine − Cₗ_coarse| / |Cₗ_fine|
                              (raw; meaningful only where |Cₗ| ≫ 0)

    Raises
    ------
    ValueError if n_k_fine ≤ n_k_coarse.
    """
    if n_k_fine <= n_k_coarse:
        raise ValueError(
            f"n_k_fine={n_k_fine} must be > n_k_coarse={n_k_coarse}."
        )
    if ells is None:
        ells = _ELLS_DEFAULT
    ells_arr = np.asarray(ells, dtype=int)

    res_c = compute_cmb_spectra(ns, ells=ells_arr, n_k=n_k_coarse)
    res_f = compute_cmb_spectra(ns, ells=ells_arr, n_k=n_k_fine)

    Dl_c = res_c["Dl"]
    Dl_f = res_f["Dl"]
    abs_Dl_error = np.abs(Dl_f - Dl_c)

    # Chi²-weighted error: |ΔDₗ| / σₗ at Planck reference multipoles
    chi2_error_per_ell = np.full(len(ells_arr), np.nan)
    chi2_error_sum = 0.0
    for i, ell in enumerate(ells_arr):
        if int(ell) in PLANCK_2018_DL_REF:
            _, sigma = PLANCK_2018_DL_REF[int(ell)]
            chi2_error_per_ell[i] = abs_Dl_error[i] / sigma
            chi2_error_sum += (abs_Dl_error[i] / sigma) ** 2

    matched = chi2_error_per_ell[~np.isnan(chi2_error_per_ell)]
    max_chi2_error = float(np.max(matched)) if len(matched) > 0 else np.nan

    # Raw relative Cₗ error (supplementary; large at Silk-damped ells)
    Cl_c = res_c["Cl"]
    Cl_f = res_f["Cl"]
    denom = np.where(np.abs(Cl_f) > 1e-40, np.abs(Cl_f), 1e-40)
    rel_error_cl = np.abs(Cl_f - Cl_c) / denom

    return {
        "ells":               ells_arr,
        "Cl_coarse":          Cl_c,
        "Cl_fine":            Cl_f,
        "Dl_coarse":          Dl_c,
        "Dl_fine":            Dl_f,
        "abs_Dl_error":       abs_Dl_error,
        "chi2_error_per_ell": chi2_error_per_ell,
        "max_chi2_error":     max_chi2_error,
        "total_chi2_error":   float(chi2_error_sum),
        "rel_error_cl":       rel_error_cl,
    }


# ===========================================================================
# 6. convergence_check
# ===========================================================================

def convergence_check(
    ns: float,
    ells: Sequence[int] | None = None,
    n_k_sequence: Sequence[int] = (200, 400, 800, 1600),
    convergence_tol: float = 1.0,
) -> dict:
    """Check χ²-weighted convergence of Dₗ as k-grid resolution increases.

    Computes Dₗ at each resolution in ``n_k_sequence`` and measures the
    successive χ²-weighted step size Σ [(Dₗⁿ⁺¹ − Dₗⁿ)/σₗ]².  This is the
    physically meaningful convergence criterion: a value < ``convergence_tol``
    (default 1.0, i.e. one Planck 1σ unit) means the numerical integration has
    converged to sub-observational precision.

    Parameters
    ----------
    ns              : float         — scalar spectral index
    ells            : sequence      — multipoles (default: Planck table)
    n_k_sequence    : sequence int  — increasing k-grid sizes (must be sorted)
    convergence_tol : float         — threshold for convergence in χ² units
                                      (default 1.0; Δχ² ~ 1 = 1σ)

    Returns
    -------
    dict with keys:

    ``ells``            : ndarray, shape (n_ell,)
    ``n_k_sequence``    : list of int
    ``Cl_table``        : ndarray, shape (n_levels, n_ell) — Cₗ at each n_k
    ``Dl_table``        : ndarray, shape (n_levels, n_ell) — Dₗ [μK²] at each n_k
    ``step_chi2``       : ndarray, shape (n_levels−1,)
                          Σ [(ΔDₗ/σₗ)²] between consecutive levels
                          (sum over Planck-matched multipoles only)
    ``step_rel_errors`` : ndarray, shape (n_levels−1, n_ell)
                          per-multipole |Cₗ_next − Cₗ_prev| / |Cₗ_next|
                          (raw; large at Silk-damped ells)
    ``converged``       : bool — True iff step_chi2[-1] < convergence_tol
    ``convergence_tol`` : float — input tolerance (echoed)

    Raises
    ------
    ValueError if n_k_sequence is not strictly increasing or has < 2 entries.
    """
    n_k_seq = list(n_k_sequence)
    if len(n_k_seq) < 2:
        raise ValueError("n_k_sequence must have at least 2 entries.")
    if any(n_k_seq[i] >= n_k_seq[i + 1] for i in range(len(n_k_seq) - 1)):
        raise ValueError("n_k_sequence must be strictly increasing.")

    if ells is None:
        ells = _ELLS_DEFAULT
    ells_arr = np.asarray(ells, dtype=int)

    n_levels = len(n_k_seq)
    n_ell    = len(ells_arr)
    Cl_table = np.empty((n_levels, n_ell))
    Dl_table = np.empty((n_levels, n_ell))

    for level, n_k in enumerate(n_k_seq):
        res = compute_cmb_spectra(ns, ells=ells_arr, n_k=n_k)
        Cl_table[level] = res["Cl"]
        Dl_table[level] = res["Dl"]

    # χ²-weighted step convergence: Σ (ΔDₗ/σₗ)² at Planck-matched multipoles
    step_chi2       = np.empty(n_levels - 1)
    step_rel_errors = np.empty((n_levels - 1, n_ell))

    for s in range(n_levels - 1):
        Dl_prev = Dl_table[s]
        Dl_next = Dl_table[s + 1]
        chi2_step = 0.0
        for i, ell in enumerate(ells_arr):
            if int(ell) in PLANCK_2018_DL_REF:
                _, sigma = PLANCK_2018_DL_REF[int(ell)]
                chi2_step += ((Dl_next[i] - Dl_prev[i]) / sigma) ** 2
        step_chi2[s] = chi2_step

        # Raw relative Cₗ step error (supplementary)
        Cl_prev = Cl_table[s]
        Cl_next = Cl_table[s + 1]
        denom = np.where(np.abs(Cl_next) > 1e-40, np.abs(Cl_next), 1e-40)
        step_rel_errors[s] = np.abs(Cl_next - Cl_prev) / denom

    converged = bool(step_chi2[-1] < convergence_tol)

    return {
        "ells":             ells_arr,
        "n_k_sequence":     n_k_seq,
        "Cl_table":         Cl_table,
        "Dl_table":         Dl_table,
        "step_chi2":        step_chi2,
        "step_rel_errors":  step_rel_errors,
        "converged":        converged,
        "convergence_tol":  float(convergence_tol),
    }
