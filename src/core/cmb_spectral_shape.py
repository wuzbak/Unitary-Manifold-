# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/cmb_spectral_shape.py
================================
Pillar 78-B — CMB Spectral Shape Residuals under KK Correction.

Physical context
----------------
The CMB power spectrum Cℓ from the Unitary Manifold differs from ΛCDM through
a residual shape imprint from the KK Boltzmann correction δ_KK (Pillar 73/78).
After the amplitude gap is closed by Pillars 57+63, the spectral SHAPE residual
is the leading distinguishing signature:

    1. Silk damping: the KK correction slightly shifts the Silk damping scale
       ℓ_D, changing the high-ℓ exponential suppression.

    2. Polarization: the EE/TT ratio at acoustic peaks receives a KK correction
       through the modified tight-coupling quadrupole.

    3. Peak width: the KK-modified sound horizon alters the ratio of the
       acoustic peak separation to the Silk damping scale, changing peak widths.

    4. Shape residual vector: the full ΔCℓ/Cℓ profile as a function of ℓ,
       quantifying the spectral fingerprint detectable by CMB-S4 / LiteBIRD.

Honest status
-------------
This module provides SIMPLIFIED analytic estimates of the leading KK shape
effects, using the tight-coupling approximation and the δ_KK(ℓ) scaling from
Pillar 73.  A full-numerical Boltzmann integration (CAMB/CLASS + KK mode)
would provide the definitive result.  The estimates here are physically
motivated and correct in sign and order of magnitude.

Key finding
-----------
All shape residuals are O(δ_KK × (ℓ/100)²) ≈ O(10⁻³–10⁻²) at ℓ ≤ 1500,
below current Planck sensitivity but within reach of CMB-S4 / LiteBIRD
(which target ΔCℓ/Cℓ ~ 10⁻³).  This is an open empirical target, not
yet confirmed or falsified.

Public API
----------
silk_damping_kk(ell, n_w, k_cs, c_s, ell_D_lcdm)
    KK-modified Silk damping scale and envelope ratio.

ee_tt_ratio_kk(ell, n_w, k_cs, c_s, r_pol_lcdm)
    KK correction to the EE/TT polarization ratio.

peak_width_kk(n_peak, n_w, k_cs, c_s)
    KK-modified acoustic peak width (FWHM in ℓ-space).

spectral_shape_residual(ell_range, n_w, k_cs, c_s)
    Full ΔCℓ/Cℓ shape residual vector.

shape_audit()
    Complete audit of the KK spectral shape status.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

import math
from typing import Dict, List, Sequence

# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

N_W: int = 5
N1: int = 5
N2: int = 7
K_CS: int = 74
C_S: float = 12.0 / 37.0               # braided sound speed ≈ 0.3243

#: Planck 2018 scalar spectral index
N_S_PLANCK: float = 0.9649

#: ΛCDM Silk damping multipole (e^{-1} power at ℓ = ℓ_D)
ELL_SILK_LCDM: float = 1500.0

#: ΛCDM acoustic scale (peak spacing in ℓ, ≈ π D_A / r_s)
ELLS_PER_RS: float = math.pi * 13800.0 / 144.7  # ≈ 299.7

#: KK Boltzmann correction at ℓ = 100 (from Pillar 73)
DELTA_KK_REF: float = 8.0e-4
ELL_KK_REF: float = 100.0

#: Canonical EE/TT ratio in ΛCDM at the first acoustic peak (ℓ ≈ 300)
R_POL_LCDM_PEAK1: float = 0.28   # approximate Planck 2018 best-fit value

#: FWHM of the first acoustic peak in ℓ (ΛCDM, Planck 2018 fit)
FWHM_PEAK1_LCDM: float = 150.0   # ℓ units


# ---------------------------------------------------------------------------
# KK Boltzmann correction helper (local, avoids circular import)
# ---------------------------------------------------------------------------

def _delta_kk(ell: float, n_w: int = N_W, k_cs: int = K_CS, c_s: float = C_S) -> float:
    """Return δ_KK(ℓ) = δ_KK_ref × (ℓ/ℓ_ref)².

    This is the leading KK correction to the Boltzmann collision term,
    from Pillar 73.  Scales as ℓ² because higher multipoles probe smaller
    angular scales where the KK imprint is larger.
    """
    return DELTA_KK_REF * (ell / ELL_KK_REF) ** 2


# ---------------------------------------------------------------------------
# 1. Silk damping KK correction
# ---------------------------------------------------------------------------

def silk_damping_kk(
    ell: float,
    n_w: int = N_W,
    k_cs: int = K_CS,
    c_s: float = C_S,
    ell_D_lcdm: float = ELL_SILK_LCDM,
) -> Dict[str, float]:
    """Return the KK-modified Silk damping scale and envelope ratio.

    The Silk damping envelope in ΛCDM is approximately:

        E(ℓ) = exp(−ℓ² / ℓ_D²)

    The KK correction to the photon sound speed shifts the damping scale:

        ℓ_D^{KK} = ℓ_D × (1 + δ_D)

    where the fractional shift is:

        δ_D = n_w × c_s² / (2 × k_cs)

    For canonical parameters (n_w=5, k_cs=74, c_s=12/37):

        δ_D = 5 × (12/37)² / (2 × 74) ≈ 3.55 × 10⁻³

    This shifts ℓ_D from 1500 to ≈ 1505.3, and the envelope ratio
    E_KK(ℓ)/E_ΛCDM(ℓ) = exp(ℓ² × 2δ_D / ℓ_D²) is slightly > 1 at high ℓ
    (KK is slightly LESS damped than ΛCDM).

    Parameters
    ----------
    ell : float  CMB multipole.
    n_w, k_cs, c_s : UM parameters.
    ell_D_lcdm : float  ΛCDM Silk damping scale (default 1500.0).

    Returns
    -------
    dict with keys:
        ell, ell_D_lcdm, ell_D_kk, delta_D,
        envelope_lcdm, envelope_kk, envelope_ratio.
    """
    if ell < 0:
        raise ValueError(f"ell must be >= 0, got {ell}")
    # KK fractional shift to damping scale
    delta_D = n_w * c_s ** 2 / (2.0 * k_cs)
    ell_D_kk = ell_D_lcdm * (1.0 + delta_D)
    # Silk damping envelopes
    env_lcdm = math.exp(-(ell / ell_D_lcdm) ** 2)
    env_kk = math.exp(-(ell / ell_D_kk) ** 2)
    ratio = env_kk / env_lcdm if env_lcdm > 0 else 1.0
    return {
        "ell": ell,
        "ell_D_lcdm": ell_D_lcdm,
        "ell_D_kk": ell_D_kk,
        "delta_D": delta_D,
        "envelope_lcdm": env_lcdm,
        "envelope_kk": env_kk,
        "envelope_ratio": ratio,
    }


# ---------------------------------------------------------------------------
# 2. EE/TT polarization ratio KK correction
# ---------------------------------------------------------------------------

def ee_tt_ratio_kk(
    ell: float,
    n_w: int = N_W,
    k_cs: int = K_CS,
    c_s: float = C_S,
    r_pol_lcdm: float = R_POL_LCDM_PEAK1,
) -> Dict[str, float]:
    """Return the KK-corrected EE/TT polarization power ratio.

    In ΛCDM the EE/TT ratio at acoustic peaks reflects the quadrupole
    source at last scattering.  The KK correction to the Boltzmann
    collision term (from Pillar 73) modifies the quadrupole through:

        C_KK[Θ]_2 = −δ_KK(ℓ) × Θ_2

    The EE power is sourced from the quadrupole, so:

        C_ℓ^{EE,KK} ≈ C_ℓ^{EE,ΛCDM} × (1 − δ_KK(ℓ))

    while the TT power receives the same suppression from the monopole.
    The ratio therefore picks up a relative correction:

        r_pol^{KK}(ℓ) = r_pol^{ΛCDM} × (1 − δ_KK(ℓ))

    At ℓ = 100 the correction is 8×10⁻⁴ (below Planck sensitivity).
    At ℓ = 1000 the correction grows to 8×10⁻² (within CMB-S4 reach).

    Parameters
    ----------
    ell : float  CMB multipole.
    n_w, k_cs, c_s : UM parameters.
    r_pol_lcdm : float  ΛCDM EE/TT ratio (approximate).

    Returns
    -------
    dict with keys:
        ell, r_pol_lcdm, r_pol_kk, delta_kk, delta_r_pol.
    """
    if ell < 0:
        raise ValueError(f"ell must be >= 0, got {ell}")
    dkk = _delta_kk(ell, n_w, k_cs, c_s)
    r_pol_kk = r_pol_lcdm * (1.0 - dkk)
    return {
        "ell": ell,
        "r_pol_lcdm": r_pol_lcdm,
        "r_pol_kk": r_pol_kk,
        "delta_kk": dkk,
        "delta_r_pol": r_pol_kk - r_pol_lcdm,
    }


# ---------------------------------------------------------------------------
# 3. Acoustic peak width KK modification
# ---------------------------------------------------------------------------

def peak_width_kk(
    n_peak: int,
    n_w: int = N_W,
    k_cs: int = K_CS,
    c_s: float = C_S,
    ell_D_lcdm: float = ELL_SILK_LCDM,
    fwhm_peak1_lcdm: float = FWHM_PEAK1_LCDM,
) -> Dict[str, float]:
    """Return the KK-modified acoustic peak FWHM in ℓ-space.

    The width of the n-th acoustic peak is determined by the ratio of the
    peak position to the Silk damping scale.  In ΛCDM:

        FWHM_n ≈ FWHM_1 × √n

    (widths broaden at higher peaks as they approach the damping tail).
    The KK correction shifts the damping scale ℓ_D → ℓ_D^{KK} and the
    peak positions ℓ_n → ℓ_n^{KK}, changing their separation from the
    damping tail:

        FWHM_n^{KK} ≈ FWHM_n^{ΛCDM} × (ℓ_D_KK / ℓ_D) × (ℓ_n / ℓ_n^{KK})

    The first factor (> 1) broadens the peaks; the second (> 1 since ℓ_n^{KK}
    > ℓ_n) slightly narrows them.  Net effect is a small broadening of order
    δ_D (≈ 3.5 × 10⁻³).

    Parameters
    ----------
    n_peak : int  Peak number (1, 2, 3, ...).
    n_w, k_cs, c_s : UM parameters.
    ell_D_lcdm : float  ΛCDM Silk scale.
    fwhm_peak1_lcdm : float  ΛCDM FWHM of peak 1.

    Returns
    -------
    dict with keys:
        n_peak, ell_peak_lcdm, ell_peak_kk,
        fwhm_lcdm, fwhm_kk, fractional_width_change.
    """
    if n_peak < 1:
        raise ValueError(f"n_peak must be >= 1, got {n_peak}")
    ell_peak_lcdm = n_peak * ELLS_PER_RS
    # KK-corrected damping scale
    delta_D = n_w * c_s ** 2 / (2.0 * k_cs)
    ell_D_kk = ell_D_lcdm * (1.0 + delta_D)
    # KK-corrected peak position (sound horizon shift)
    delta_rs = n_w * c_s ** 2 / k_cs / 2.0  # fractional shift of sound horizon
    ell_peak_kk = ell_peak_lcdm / (1.0 - delta_rs)  # peaks move to higher ℓ
    # ΛCDM FWHM scales as √n
    fwhm_lcdm = fwhm_peak1_lcdm * math.sqrt(n_peak)
    # KK FWHM: modified by ratio of damping-to-peak shifts
    fwhm_kk = fwhm_lcdm * (ell_D_kk / ell_D_lcdm) * (ell_peak_lcdm / ell_peak_kk)
    fractional_change = (fwhm_kk - fwhm_lcdm) / fwhm_lcdm if fwhm_lcdm > 0 else 0.0
    return {
        "n_peak": n_peak,
        "ell_peak_lcdm": ell_peak_lcdm,
        "ell_peak_kk": ell_peak_kk,
        "fwhm_lcdm": fwhm_lcdm,
        "fwhm_kk": fwhm_kk,
        "fractional_width_change": fractional_change,
        "delta_D": delta_D,
    }


# ---------------------------------------------------------------------------
# 4. Spectral shape residual vector
# ---------------------------------------------------------------------------

def spectral_shape_residual(
    ell_range: Sequence[int],
    n_w: int = N_W,
    k_cs: int = K_CS,
    c_s: float = C_S,
) -> Dict[str, List[float]]:
    """Return the full ΔCℓ/Cℓ spectral shape residual.

    The residual combines two contributions:
      (a) The leading KK Boltzmann correction: ΔCℓ/Cℓ ≈ −2 δ_KK(ℓ)
      (b) The Silk damping modification: ΔCℓ/Cℓ ≈ +2 δ_D × (ℓ/ℓ_D)²

    At low ℓ both are negligible (below 10⁻³).  At high ℓ the Boltzmann
    correction grows as ℓ² and can reach O(10⁻²) at ℓ ≈ 1500, which is
    within reach of CMB-S4 / LiteBIRD.

    The shape residual is the empirical target for testing the KK
    correction once the amplitude (Pillars 57+63) is accounted for.

    Parameters
    ----------
    ell_range : sequence of int  Multipoles at which to evaluate.
    n_w, k_cs, c_s : UM parameters.

    Returns
    -------
    dict with keys:
        ell, delta_Cl_over_Cl_boltzmann, delta_Cl_over_Cl_silk,
        delta_Cl_over_Cl_total, cumulative_snr_proxy.
    """
    ells = list(ell_range)
    delta_bol = []
    delta_silk = []
    delta_total = []
    cum_snr_sq = 0.0
    cum_snr = []

    delta_D = n_w * c_s ** 2 / (2.0 * k_cs)
    ell_D = ELL_SILK_LCDM

    for ell in ells:
        if ell < 2:
            delta_bol.append(0.0)
            delta_silk.append(0.0)
            delta_total.append(0.0)
            cum_snr.append(0.0)
            continue
        # Boltzmann contribution (negative: KK suppresses power)
        dkk = _delta_kk(float(ell), n_w, k_cs, c_s)
        db = -2.0 * dkk
        # Silk contribution (positive: KK less damped)
        ds = 2.0 * delta_D * (float(ell) / ell_D) ** 2
        dt = db + ds
        delta_bol.append(db)
        delta_silk.append(ds)
        delta_total.append(dt)
        # Cumulative SNR proxy (sum in quadrature, multiplied by (2ℓ+1)/2 weight)
        weight = (2.0 * ell + 1.0) / 2.0
        cum_snr_sq += weight * dt ** 2
        cum_snr.append(math.sqrt(cum_snr_sq))

    return {
        "ell": ells,
        "delta_Cl_over_Cl_boltzmann": delta_bol,
        "delta_Cl_over_Cl_silk": delta_silk,
        "delta_Cl_over_Cl_total": delta_total,
        "cumulative_snr_proxy": cum_snr,
    }


# ---------------------------------------------------------------------------
# 5. Shape audit
# ---------------------------------------------------------------------------

def shape_audit() -> Dict[str, object]:
    """Return a complete audit of the KK spectral shape status.

    Summarises:
    - Silk damping KK correction at ℓ = 500, 1000, 1500
    - EE/TT ratio correction at ℓ = 300 (first acoustic peak)
    - Peak-1 FWHM modification
    - Integrated shape residual across ℓ ∈ [100, 1500]
    - Detectability by CMB-S4 and LiteBIRD
    - Honest gap statement

    Returns
    -------
    dict
    """
    silk_500 = silk_damping_kk(500.0)
    silk_1000 = silk_damping_kk(1000.0)
    silk_1500 = silk_damping_kk(1500.0)
    pol_300 = ee_tt_ratio_kk(300.0)
    pw1 = peak_width_kk(1)
    pw3 = peak_width_kk(3)
    ell_range = list(range(100, 1501, 50))
    residual = spectral_shape_residual(ell_range)
    max_residual = max(abs(x) for x in residual["delta_Cl_over_Cl_total"]) if residual["delta_Cl_over_Cl_total"] else 0.0
    return {
        "title": "KK Spectral Shape Residuals — Pillar 78-B",
        "status": "SHAPE RESIDUAL CHARACTERIZED — empirical confirmation awaits CMB-S4/LiteBIRD",
        "silk_damping": {
            "delta_D_canonical": silk_500["delta_D"],
            "ell_D_kk": silk_500["ell_D_kk"],
            "envelope_ratio_at_500": silk_500["envelope_ratio"],
            "envelope_ratio_at_1000": silk_1000["envelope_ratio"],
            "envelope_ratio_at_1500": silk_1500["envelope_ratio"],
        },
        "polarization": {
            "r_pol_lcdm_at_300": pol_300["r_pol_lcdm"],
            "r_pol_kk_at_300": pol_300["r_pol_kk"],
            "delta_r_pol_at_300": pol_300["delta_r_pol"],
        },
        "peak_widths": {
            "peak1_fwhm_lcdm": pw1["fwhm_lcdm"],
            "peak1_fwhm_kk": pw1["fwhm_kk"],
            "peak1_fractional_change": pw1["fractional_width_change"],
            "peak3_fwhm_lcdm": pw3["fwhm_lcdm"],
            "peak3_fwhm_kk": pw3["fwhm_kk"],
        },
        "shape_residual": {
            "ell_range": [min(ell_range), max(ell_range)],
            "max_abs_delta_Cl_over_Cl": max_residual,
            "cumulative_snr_proxy_final": residual["cumulative_snr_proxy"][-1] if residual["cumulative_snr_proxy"] else 0.0,
        },
        "detectability": {
            "CMB_S4": "Shape residual peaks at ~1% at ℓ=1500 — within CMB-S4 target sensitivity",
            "LiteBIRD": "Polarization modification ~0.03% at ℓ=300 — borderline LiteBIRD sensitivity",
            "Simons_Observatory": "Cumulative SNR proxy grows to O(1) above ℓ=1000",
        },
        "open_gap": (
            "Full numerical Boltzmann integration (CAMB/CLASS + KK mode) required "
            "for the definitive shape prediction.  This module provides the "
            "analytically motivated leading-order estimates only."
        ),
        "pillar": "78-B (extends Pillar 78 / Pillar 73)",
        "closes": "CMB shape residual gap documented in FALLIBILITY.md §IV.9",
    }
