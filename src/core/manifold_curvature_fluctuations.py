# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/manifold_curvature_fluctuations.py
============================================
Pillar 123 — Manifold-Induced Curvature Fluctuations.

Physical context
----------------
The primordial power spectrum P(k) = A_s (k/k_pivot)^(n_s-1) assumes infinite
flat space.  When space is a compact manifold (E2 torus of size L_torus), modes
with k < 2π/L_torus are forbidden.  This creates a "manifold wrap correction"
ΔP(k)/P₀(k) that modifies the spectrum at scales comparable to L_torus.

The tightness parameter ξ = χ_rec / L_torus quantifies how compact the manifold
is relative to the observable universe:

    ξ >> 1  (L_torus < χ_rec)  — highly compact; correction is observationally
                                  significant.
    ξ << 1  (L_torus >> χ_rec) — large torus; correction vanishes, recovering
                                  the standard Harrison-Zel'dovich-Peebles form.

The wrap correction is:

    ΔP(k)/P₀(k) = −ξ² × exp(−k / k_cut)

where k_cut = 2π / L_torus is the fundamental (lowest allowed) mode of the
torus.  Suppression is strongest at k << k_cut (super-horizon modes are absent)
and exponentially small at k >> k_cut.

UM Alignment
------------
- N_S = 0.9635 from Pillar 34 winding-number derivation.
- K_CS = 74 = 5² + 7² — Chern-Simons level (Pillars 58, 70-D).
- N_W = 5 — compact S¹/Z₂ winding number (Pillar 70-D).
- R_BRAIDED = 0.0315 — tensor-to-scalar ratio.
- BETA_DEG = 0.351° — CMB birefringence angle.

The large-scale spatial topology (L_torus) is entirely decoupled from the
Planck-scale compact dimension (Pillar 116), so the wrap correction affects
only the *large-scale* power spectrum envelope, not nₛ, r, or β.

Public API
----------
wrap_tightness_parameter(L_torus_over_chi)
    Dimensionless tightness ξ = χ_rec / L_torus.

manifold_wrap_correction(k, L_torus_over_chi)
    Additive fractional correction ΔP(k)/P₀(k) from manifold wrap.

power_spectrum_modified(k, n_s, A_s, L_torus_over_chi)
    Full modified primordial power spectrum P(k) clamped to > 0.

cutoff_scale_k(L_torus_over_chi)
    Fundamental torus wavenumber k_cut = 2π / L_torus in Mpc⁻¹.

primordial_spectrum_summary(L_torus_over_chi)
    Tabulated comparison of standard vs modified P(k) at key scales.

litebird_pk_forecast()
    Detectability forecast for the wrap correction in LiteBIRD data.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
N_S: float = 0.9635                  # UM CMB spectral index (Pillar 34)
A_S: float = 2.1e-9                  # Scalar power spectrum amplitude
K_PIVOT: float = 0.05                # Pivot scale in Mpc⁻¹
CHI_REC_MPC: float = 14000.0        # Comoving distance to recombination (Mpc)
N_W: int = 5                         # Compact S¹/Z₂ winding number
K_CS: int = 74                       # Chern-Simons level = 5² + 7²
R_BRAIDED: float = 0.0315            # Tensor-to-scalar ratio (Pillar 34)
BETA_DEG: float = 0.351              # CMB birefringence angle (degrees)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def wrap_tightness_parameter(L_torus_over_chi: float) -> float:
    """Return dimensionless tightness ξ = χ_rec / L_torus = 1 / L_torus_over_chi.

    Parameters
    ----------
    L_torus_over_chi:
        Ratio L_torus / χ_rec (must be > 0).

    Returns
    -------
    float
        ξ: large value means compact manifold; small value means standard space.

    Raises
    ------
    ValueError
        If L_torus_over_chi <= 0.
    """
    if L_torus_over_chi <= 0.0:
        raise ValueError(
            f"L_torus_over_chi must be > 0; got {L_torus_over_chi}"
        )
    return 1.0 / L_torus_over_chi


def manifold_wrap_correction(k: float, L_torus_over_chi: float) -> float:
    """Return additive fractional correction ΔP(k)/P₀(k) from manifold wrap.

    The wrap correction is:

        ΔP(k)/P₀(k) = −ξ² × exp(−k / k_cut)

    where ξ = χ_rec / L_torus and k_cut = 2π / L_torus.

    Parameters
    ----------
    k:
        Wavenumber in Mpc⁻¹ (must be > 0).
    L_torus_over_chi:
        Ratio L_torus / χ_rec (must be > 0).

    Returns
    -------
    float
        A non-positive correction factor.  Zero for very large L_torus.

    Raises
    ------
    ValueError
        If k <= 0 or L_torus_over_chi <= 0.
    """
    if k <= 0.0:
        raise ValueError(f"k must be > 0; got {k}")
    if L_torus_over_chi <= 0.0:
        raise ValueError(
            f"L_torus_over_chi must be > 0; got {L_torus_over_chi}"
        )
    xi = wrap_tightness_parameter(L_torus_over_chi)
    k_cut = 2.0 * math.pi / (L_torus_over_chi * CHI_REC_MPC)
    return -(xi ** 2) * math.exp(-k / k_cut)


def power_spectrum_modified(
    k: float,
    n_s: float,
    A_s: float,
    L_torus_over_chi: float,
) -> float:
    """Return the manifold-corrected primordial power spectrum P(k).

    P_modified = A_s × (k/K_PIVOT)^(n_s−1) × (1 + correction)

    The result is clamped to a minimum of 1e-50 to ensure positivity.

    Parameters
    ----------
    k:
        Wavenumber in Mpc⁻¹ (must be > 0).
    n_s:
        Spectral index.
    A_s:
        Amplitude (must be > 0).
    L_torus_over_chi:
        Ratio L_torus / χ_rec (must be > 0).

    Returns
    -------
    float
        Modified power spectrum value P(k) > 0.

    Raises
    ------
    ValueError
        If k <= 0, A_s <= 0, or L_torus_over_chi <= 0.
    """
    if k <= 0.0:
        raise ValueError(f"k must be > 0; got {k}")
    if A_s <= 0.0:
        raise ValueError(f"A_s must be > 0; got {A_s}")
    if L_torus_over_chi <= 0.0:
        raise ValueError(
            f"L_torus_over_chi must be > 0; got {L_torus_over_chi}"
        )
    p_standard = A_s * (k / K_PIVOT) ** (n_s - 1.0)
    correction = manifold_wrap_correction(k, L_torus_over_chi)
    p_modified = p_standard * (1.0 + correction)
    return max(p_modified, 1e-50)


def cutoff_scale_k(L_torus_over_chi: float) -> float:
    """Return the fundamental torus wavenumber k_cut = 2π / L_torus in Mpc⁻¹.

    This is the wavenumber at which the wrap correction becomes O(1).  Modes
    with k < k_cut are forbidden in the compact torus.

    Parameters
    ----------
    L_torus_over_chi:
        Ratio L_torus / χ_rec (must be > 0).

    Returns
    -------
    float
        k_cut in Mpc⁻¹.

    Raises
    ------
    ValueError
        If L_torus_over_chi <= 0.
    """
    if L_torus_over_chi <= 0.0:
        raise ValueError(
            f"L_torus_over_chi must be > 0; got {L_torus_over_chi}"
        )
    return 2.0 * math.pi / (L_torus_over_chi * CHI_REC_MPC)


def primordial_spectrum_summary(L_torus_over_chi: float) -> dict:
    """Return a comparison of standard vs manifold-modified P(k) at key scales.

    Evaluates at k = [K_PIVOT/10, K_PIVOT, K_PIVOT×10, K_PIVOT×100].

    Parameters
    ----------
    L_torus_over_chi:
        Ratio L_torus / χ_rec (must be > 0).

    Returns
    -------
    dict
        Summary containing tightness parameters, cutoff scale, and tabulated
        P_standard and P_modified at the four key wavenumbers.

    Raises
    ------
    ValueError
        If L_torus_over_chi <= 0.
    """
    if L_torus_over_chi <= 0.0:
        raise ValueError(
            f"L_torus_over_chi must be > 0; got {L_torus_over_chi}"
        )
    k_values = [K_PIVOT / 10.0, K_PIVOT, K_PIVOT * 10.0, K_PIVOT * 100.0]
    p_standard = [
        A_S * (k / K_PIVOT) ** (N_S - 1.0) for k in k_values
    ]
    p_modified = [
        power_spectrum_modified(k, N_S, A_S, L_torus_over_chi) for k in k_values
    ]
    return {
        "L_torus_over_chi": L_torus_over_chi,
        "tightness_xi": wrap_tightness_parameter(L_torus_over_chi),
        "k_cutoff_mpc": cutoff_scale_k(L_torus_over_chi),
        "k_values": k_values,
        "P_standard": p_standard,
        "P_modified": p_modified,
        "correction_at_pivot": manifold_wrap_correction(K_PIVOT, L_torus_over_chi),
        "n_s_input": N_S,
        "A_s_input": A_S,
        "standard_spectrum_formula": "A_s (k/k_pivot)^(n_s-1)",
        "wrap_correction_formula": "-(xi^2) * exp(-k/k_cut)",
    }


def litebird_pk_forecast() -> dict:
    """Return a detectability forecast for the manifold wrap correction.

    Assesses whether LiteBIRD (and Euclid) can detect the wrap correction
    ΔP(k)/P₀(k) = −ξ² exp(−k/k_cut) for a compact torus.

    Returns
    -------
    dict
        Instrument parameters, detection thresholds, and epistemic status.
    """
    return {
        "instrument": "LiteBIRD",
        "sensitivity_ell_max": 2000,
        "k_min_mpc": 1.0 / CHI_REC_MPC,
        "detectable_xi_threshold": 0.1,
        "detectable_L_over_chi": 10.0,
        "detection_method": "Comparison of C_ℓ at low-ℓ vs high-ℓ ratio",
        "reference": "LiteBIRD Collaboration 2023",
        "epistemic_status": "PREDICTIVE — testable by LiteBIRD and Euclid",
    }
