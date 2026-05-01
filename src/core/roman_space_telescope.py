# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/roman_space_telescope.py
===================================
Pillar 66 — Nancy Grace Roman Space Telescope: UM Falsification Forecasts.

Mission context
---------------
The Nancy Grace Roman Space Telescope (formerly WFIRST) is NASA's next flagship
infrared space observatory, scheduled for launch in September 2026.  Its 2.4 m
primary mirror and 300-megapixel Wide Field Instrument (WFI) delivers a field of
view ~200× larger than HST's infrared camera, enabling:

1. **High Latitude Wide Area Survey (HLWAS)** — 2 000 deg² of wide-field
   imaging and grism spectroscopy:
   - Weak gravitational lensing (WL): ~500 million galaxy shapes, σ_shape ≈ 0.26.
   - Galaxy clustering / BAO: ~30 million Hα emitters at 1 < z < 2.
   - Type Ia supernovae: ~20 000 calibrated light curves at z = 0.1–3.

2. **Galactic Bulge Time-Domain Survey** — microlensing exoplanet census
   (less directly relevant to UM dark energy tests; not modelled here).

3. **Coronagraphic Instrument (CGI)** — direct imaging of nearby exoplanets.

Unitary Manifold dark energy prediction
----------------------------------------
The Unitary Manifold (UM) predicts a specific dark energy equation of state
(EoS) from the stabilised KK zero-mode of the compact fifth dimension.  The
stress tensor of the slowly-rolling radion field gives:

    w_KK  =  −1  +  (2/3) × c_s²

where the braided sound speed c_s = (n₂² − n₁²)/(n₁² + n₂²) = 12/37 is
fixed by the (5, 7) winding resonance selected by the Planck nₛ data (Pillar 7):

    c_s       =  12/37          ≈  0.3243
    c_s²      =  (12/37)²       ≈  0.1052
    w_KK      =  −1 + 2/3 × (12/37)²  ≈  −0.9302    [no free parameters]

In the CPL parameterisation w(z) = w₀ + wₐ z/(1+z), the UM predicts:

    w₀  =  w_KK ≈ −0.9302    (constant; KK zero-mode is stabilised)
    wₐ  =  0                  (zero running; no further compactification)

Status of DESI cross-check (April 2026):
    DESI DR2 (w₀CDM):   w₀ = −0.92 ± 0.09   →  |w_KK − w₀| < 0.1σ  ✅
    DESI (w₀wₐCDM):     w₀ = −0.76 ± 0.09, wₐ = −0.63 ± 0.28
                         UM wₐ = 0 is within 2.25σ of DESI wₐ.
    This is a mild tension; the formal 2027 DESI 47M-galaxy analysis is decisive.

Roman as UM falsifier
---------------------
Roman will measure:

* **σ(w₀) ~ 0.02** from weak lensing alone (√N-scaling, Fisher-matrix estimate).
* **σ(wₐ) ~ 0.07** from WL + spectroscopic BAO combined.
* **σ(H₀) ~ 0.5 km/s/Mpc** from ~20 000 calibrated SNe Ia.
* **σ(S₈) ~ 0.003** from cosmic shear power spectrum.

At Roman's precision level:
    - If |w₀_Roman − w_KK| > 3σ(w_Roman), the UM dark-energy prediction is
      falsified.
    - If |wₐ_Roman| > 3σ(wₐ_Roman), the wₐ = 0 prediction is falsified.
    - If S₈_Roman is inconsistent at >3σ with the UM-modified S₈, the KK
      matter power spectrum (Pillar 59) is falsified.

S₈ parameter and KK suppression
---------------------------------
The S₈ tension between Planck (S₈ ≈ 0.832) and weak-lensing surveys
(KiDS-1000 / DES Y3: S₈ ≈ 0.759–0.776) is well documented.  The KK
suppression of the matter power spectrum (Pillar 59) reduces σ₈ by:

    δσ₈ / σ₈  ≈  −½ × f_braid  ≈  −7.1 × 10⁻⁴

where f_braid = c_s² / k_CS ≈ 1.42 × 10⁻³.  This shift is negligible compared
to the ~8% S₈ tension, so the UM does not resolve the S₈ tension.  The KK
suppression is documented here as an honest upper bound on UM's contribution.

BAO at z ~ 1.5 (Roman spectroscopic survey)
--------------------------------------------
Roman's grism spectrograph will measure Hα emission-line redshifts at
1 < z < 2, complementing DESI's primary z < 1.6 coverage.  The fractional
BAO shift from the braided KK sound speed is (Pillar 59, eq. [6]):

    Δr_BAO / r_BAO  ≈  ½ × f_braid  ≈  7.1 × 10⁻⁴

This is ~0.07% — far below Roman's projected ~0.3% BAO distance precision at
z ~ 1.5.  Roman cannot detect this shift with current forecasts.

Honest limitations
------------------
* All σ(w) and σ(S₈) forecasts use simplified Fisher-matrix / √N scalings
  calibrated to published Roman Science Book projections.  Full forecasts
  require multi-z-bin Fisher matrices, shear calibration, photo-z nuisances,
  intrinsic alignments, and baryonic feedback marginalisation.
* The UM w_KK formula uses the slow-roll approximation.  Higher-order
  corrections to the KK equation of state are not computed.
* The S₈ tension in the UM is not resolved by the KK suppression (δS₈/S₈ ~ 0.07%).
* Roman cannot detect the BAO shift Δr/r ~ 7 × 10⁻⁴ at z ~ 1.5 with current
  survey specifications.
* Hubble tension: UM does not predict H₀ from first principles (cosmological
  constant problem).

Public API
----------
N_W : int
    UM winding number = 5.

K_CS : int
    Chern-Simons level k_cs = 74 = 5² + 7².

C_S : float
    Braided radion sound speed = 12/37.

C_S_SQUARED : float
    c_s² = (12/37)².

W_KK : float
    UM dark energy equation of state = −1 + (2/3) c_s² ≈ −0.9302.

W_A_KK : float
    UM CPL running parameter wₐ = 0 (stabilised zero-mode).

F_BRAID : float
    KK radion pressure fraction = c_s² / k_CS ≈ 1.42 × 10⁻³.

ROMAN_SURVEY_AREA_DEG2 : float
    Roman HLWAS survey area ≈ 2 000 deg².

ROMAN_F_SKY : float
    Effective sky fraction ≈ 0.0485.

ROMAN_N_GALAXIES_WL : int
    Expected WL source galaxies ≈ 500 million.

ROMAN_N_SNE : int
    Expected calibrated Type Ia SNe ≈ 20 000.

ROMAN_N_SPEC_GALAXIES : int
    Expected Hα spec-z galaxies at 1 < z < 2 ≈ 30 million.

roman_um_dark_energy_eos(n1, n2) → float
    UM dark energy EoS w_KK for winding numbers (n₁, n₂).

roman_cpl_w_at_z(w0, wa, z) → float
    CPL parameterisation w(z) = w₀ + wₐ z/(1+z).

roman_wl_sigma_w(n_gals, f_sky, sigma_shape) → float
    Forecast σ(w) from Roman weak lensing.

roman_wl_sigma_s8(n_gals, f_sky, sigma_shape) → float
    Forecast σ(S₈) from Roman cosmic shear.

roman_sne_sigma_h0(n_sne, sigma_mu, calib_floor) → float
    Forecast σ(H₀) from Roman Type Ia supernovae.

roman_bao_sigma_w(n_spec, f_sky, z_eff) → float
    Forecast σ(w) from Roman spectroscopic BAO at z ~ 1.5.

roman_combined_sigma_w(sigma_wl, sigma_bao) → float
    Combined σ(w) from WL and BAO in quadrature.

roman_bao_shift_kk() → float
    UM fractional BAO shift Δr_BAO/r_BAO from KK radion.

roman_s8_kk(s8_lcdm, f_braid) → float
    KK-modified S₈ = s8_lcdm × (1 − ½ f_braid).

roman_um_w_tension_audit(sigma_roman_w) → dict
    Tension audit: UM w_KK vs. forecast Roman constraint.

roman_um_s8_audit(s8_wl_surveys, sigma_s8) → dict
    S₈ tension: UM KK prediction vs. weak-lensing measurements.

roman_falsification_conditions() → dict
    Explicit conditions that would falsify the UM using Roman data.

roman_summary() → dict
    Complete Pillar 66 audit.

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
from typing import Any, Dict

# ---------------------------------------------------------------------------
# UM / KK constants
# ---------------------------------------------------------------------------

#: Winding number from Planck nₛ selection (Pillar 7)
N_W: int = 5

#: Secondary winding from (5, 7) braid resonance (Pillar 27/58)
N_W2: int = 7

#: Chern-Simons level k_cs = 5² + 7² = 74 (Pillar 39)
K_CS: int = N_W ** 2 + N_W2 ** 2        # 74

#: Braided radion sound speed c_s = (7²−5²)/(7²+5²) = 24/74 = 12/37 (Pillar 7)
C_S: float = (N_W2 ** 2 - N_W ** 2) / (N_W2 ** 2 + N_W ** 2)   # 12/37

#: c_s²
C_S_SQUARED: float = C_S ** 2

#: KK radion pressure fraction f_braid = c_s² / k_CS (Pillar 49)
F_BRAID: float = C_S_SQUARED / K_CS     # ≈ 1.42 × 10⁻³

#: UM dark energy equation of state w_KK = −1 + (2/3) c_s² (Pillar 38)
#: Source: hubble_tension.py :: kk_equation_of_state(5, 7)
W_KK: float = -1.0 + (2.0 / 3.0) * C_S_SQUARED   # ≈ −0.9302

#: UM CPL wₐ parameter = 0 (stabilised KK zero-mode; no EoS running)
W_A_KK: float = 0.0

#: UM canonical spectral index (Pillar 56)
NS_UM: float = 0.9635

#: UM tensor-to-scalar ratio (Pillar 27)
R_BRAIDED: float = 0.0315

# ---------------------------------------------------------------------------
# Observational reference values
# ---------------------------------------------------------------------------

#: DESI DR2 (April 2026) single-w (w₀CDM) central value
W0_DESI_DR2: float = -0.92
SIGMA_W0_DESI_DR2: float = 0.09

#: DESI (w₀wₐCDM) best-fit parameters (DR1+DR2 combined)
W0_DESI_W0WA: float = -0.76
WA_DESI_W0WA: float = -0.63
SIGMA_W0_DESI_W0WA: float = 0.09
SIGMA_WA_DESI_W0WA: float = 0.28

#: Planck 2018 S₈ central value and uncertainty
S8_PLANCK: float = 0.832
SIGMA_S8_PLANCK: float = 0.013

#: KiDS-1000 / DES Y3 combined S₈ (weak lensing)
S8_WEAK_LENSING: float = 0.759
SIGMA_S8_WEAK_LENSING: float = 0.024

#: ΛCDM / Planck 2018 σ₈ fiducial value (Pillar 59)
SIGMA8_LCDM: float = 0.811

#: Planck 2018 Ω_m
OMEGA_M_PLANCK: float = 0.3153

#: H₀ reference (local, H0DN April 2026)
H0_LOCAL: float = 73.50     # km/s/Mpc
H0_CMB: float = 67.4        # km/s/Mpc

# ---------------------------------------------------------------------------
# Roman Space Telescope survey specifications
# (Reference: Roman Science Book, 2019–2024 updates; NASA mission page)
# ---------------------------------------------------------------------------

#: Roman HLWAS survey area [deg²]
ROMAN_SURVEY_AREA_DEG2: float = 2_000.0

#: Full sky area [deg²]
FULL_SKY_DEG2: float = 41_253.0

#: Roman effective sky fraction f_sky = 2000 / 41253
ROMAN_F_SKY: float = ROMAN_SURVEY_AREA_DEG2 / FULL_SKY_DEG2   # ≈ 0.0485

#: Expected WL source galaxies (~500 million over 2000 deg², ~250 gal/arcmin²)
ROMAN_N_GALAXIES_WL: int = 500_000_000

#: Per-galaxy shape noise (intrinsic + measurement; Roman NIR bands)
ROMAN_SIGMA_SHAPE: float = 0.26

#: Expected calibrated Type Ia SNe from Roman SN survey
ROMAN_N_SNE: int = 20_000

#: Intrinsic SN distance-modulus dispersion [mag]
ROMAN_SIGMA_MU: float = 0.12

#: Systematic calibration floor on σ(H₀) from Roman SNe [km/s/Mpc]
ROMAN_H0_CALIB_FLOOR: float = 0.30

#: Expected spectroscopic Hα galaxies at 1 < z < 2 (grism survey)
ROMAN_N_SPEC_GALAXIES: int = 30_000_000

#: Effective redshift of Roman spectroscopic BAO sample
ROMAN_Z_EFF_SPEC: float = 1.5

#: Roman spectroscopic minimum redshift
ROMAN_Z_MIN_SPEC: float = 1.0

#: Roman spectroscopic maximum redshift
ROMAN_Z_MAX_SPEC: float = 2.0

#: Pixel scale [arcsec/pixel]
ROMAN_PIXEL_SCALE_ARCSEC: float = 0.11

#: Primary mirror diameter [m]
ROMAN_MIRROR_M: float = 2.4

#: Field-of-view multiplier relative to HST WFC3-IR
ROMAN_FOV_X_HUBBLE: float = 200.0

#: Launch year / month
ROMAN_LAUNCH_YEAR: int = 2026
ROMAN_LAUNCH_MONTH: int = 9     # September 2026

# ---------------------------------------------------------------------------
# Fisher-matrix calibration coefficients
# Calibrated so that Roman's baseline survey parameters yield published
# forecast precisions: σ(w) ~ 0.02 (WL), σ(w) ~ 0.05 (BAO), σ(S₈) ~ 0.003.
# ---------------------------------------------------------------------------

#: WL coefficient C_w: σ(w) = C_w × (σ_shape/0.26) / √(N_gal × f_sky)
#: Calibrated: 100 / √(5×10⁸ × 0.0485) ≈ 100 / 4924 ≈ 0.0203
_WL_W_COEFF: float = 100.0

#: WL S₈ coefficient C_s8: σ(S₈) = C_s8 × (σ_shape/0.26) / √(N_gal × f_sky)
#: Calibrated: 14.8 / √(5×10⁸ × 0.0485) ≈ 14.8 / 4924 ≈ 0.003
_WL_S8_COEFF: float = 14.8

#: BAO coefficient C_bao: σ(w) = C_bao / √(N_spec × f_sky) × (1+z_eff)/2
#: Calibrated so that Roman baseline (N_spec=3×10⁷, f_sky=0.0485, z_eff=1.5)
#: yields σ(w)_BAO ≈ 0.05, consistent with Roman Science Book forecast.
#: C_bao = 0.05 × √(3×10⁷ × 0.0485) × 2/(1+1.5) ≈ 48.24
_BAO_W_COEFF: float = 48.24

#: H₀ reference value for SNe forecast [km/s/Mpc]
_H0_REFERENCE: float = 70.0


# ---------------------------------------------------------------------------
# Core physics functions
# ---------------------------------------------------------------------------

def roman_um_dark_energy_eos(n1: int = N_W, n2: int = N_W2) -> float:
    """Return the UM dark energy equation of state w_KK for winding (n₁, n₂).

    The KK zero-mode equation of state follows from the slow-roll stress tensor
    of the stabilised radion field on the compact S¹/Z₂ dimension:

        c_s = (n₂² − n₁²) / (n₁² + n₂²)

        w_KK = −1 + (2/3) × c_s²

    For the canonical (5, 7) branch: w_KK ≈ −0.9302.

    Parameters
    ----------
    n1 : int — smaller winding number (default 5)
    n2 : int — larger winding number (default 7)

    Returns
    -------
    float
        w_KK (dimensionless; w = −1 for ΛCDM).

    Raises
    ------
    ValueError
        If n1 or n2 are not positive integers with n2 > n1.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"Winding numbers must be positive; got n1={n1}, n2={n2}")
    if n2 <= n1:
        raise ValueError(f"Require n2 > n1; got n1={n1}, n2={n2}")
    cs = (n2 ** 2 - n1 ** 2) / (n2 ** 2 + n1 ** 2)
    return -1.0 + (2.0 / 3.0) * cs ** 2


def roman_cpl_w_at_z(w0: float, wa: float, z: float) -> float:
    """Evaluate the CPL dark energy equation of state at redshift z.

    The Chevallier–Polarski–Linder (CPL) parameterisation is:

        w(z) = w₀ + wₐ × z / (1 + z)

    UM prediction: w₀ = w_KK ≈ −0.9302,  wₐ = 0.

    Parameters
    ----------
    w0 : float — present-day EoS w₀
    wa : float — running parameter wₐ
    z  : float — redshift (z ≥ 0)

    Returns
    -------
    float
        w(z) at the requested redshift.

    Raises
    ------
    ValueError
        If z < 0.
    """
    if z < 0.0:
        raise ValueError(f"Redshift z must be ≥ 0; got {z!r}")
    return w0 + wa * z / (1.0 + z)


def roman_wl_sigma_w(
    n_gals: int = ROMAN_N_GALAXIES_WL,
    f_sky: float = ROMAN_F_SKY,
    sigma_shape: float = ROMAN_SIGMA_SHAPE,
) -> float:
    """Forecast 1σ uncertainty on w from Roman weak gravitational lensing.

    Simplified Fisher-matrix estimate:

        σ(w)  ≈  C_w × (σ_shape / 0.26) / √(N_gal × f_sky)

    Calibrated so that the Roman baseline (N_gal = 5×10⁸, f_sky = 0.0485,
    σ_shape = 0.26) yields σ(w) ≈ 0.02, consistent with the Roman Science
    Book forecast.

    Parameters
    ----------
    n_gals      : int   — WL source galaxies (default 5×10⁸)
    f_sky       : float — effective sky fraction (default 0.0485)
    sigma_shape : float — per-galaxy shape noise (default 0.26)

    Returns
    -------
    float
        Forecast σ(w) from WL.

    Raises
    ------
    ValueError
        If n_gals ≤ 0 or f_sky ∉ (0, 1].
    """
    if n_gals <= 0:
        raise ValueError(f"n_gals must be > 0; got {n_gals!r}")
    if not 0.0 < f_sky <= 1.0:
        raise ValueError(f"f_sky must be in (0, 1]; got {f_sky!r}")
    if sigma_shape <= 0.0:
        raise ValueError(f"sigma_shape must be > 0; got {sigma_shape!r}")
    return _WL_W_COEFF * (sigma_shape / 0.26) / math.sqrt(float(n_gals) * f_sky)


def roman_wl_sigma_s8(
    n_gals: int = ROMAN_N_GALAXIES_WL,
    f_sky: float = ROMAN_F_SKY,
    sigma_shape: float = ROMAN_SIGMA_SHAPE,
) -> float:
    """Forecast 1σ uncertainty on S₈ from Roman cosmic shear.

    Simplified Fisher-matrix estimate:

        σ(S₈)  ≈  C_s8 × (σ_shape / 0.26) / √(N_gal × f_sky)

    Calibrated so that the Roman baseline yields σ(S₈) ≈ 0.003.

    Parameters
    ----------
    n_gals      : int   — WL source galaxies (default 5×10⁸)
    f_sky       : float — effective sky fraction (default 0.0485)
    sigma_shape : float — per-galaxy shape noise (default 0.26)

    Returns
    -------
    float
        Forecast σ(S₈).

    Raises
    ------
    ValueError
        If n_gals ≤ 0 or f_sky ∉ (0, 1].
    """
    if n_gals <= 0:
        raise ValueError(f"n_gals must be > 0; got {n_gals!r}")
    if not 0.0 < f_sky <= 1.0:
        raise ValueError(f"f_sky must be in (0, 1]; got {f_sky!r}")
    if sigma_shape <= 0.0:
        raise ValueError(f"sigma_shape must be > 0; got {sigma_shape!r}")
    return _WL_S8_COEFF * (sigma_shape / 0.26) / math.sqrt(float(n_gals) * f_sky)


def roman_sne_sigma_h0(
    n_sne: int = ROMAN_N_SNE,
    sigma_mu: float = ROMAN_SIGMA_MU,
    calib_floor: float = ROMAN_H0_CALIB_FLOOR,
) -> float:
    """Forecast 1σ uncertainty on H₀ from Roman Type Ia supernovae.

    Statistical precision:

        σ_stat(H₀) = H₀_ref × (ln 10 / 5) × σ_μ / √N_SN

    Total uncertainty adds the systematic calibration floor in quadrature:

        σ_total(H₀) = √(σ_stat² + σ_floor²)

    Parameters
    ----------
    n_sne       : int   — calibrated SN Ia light curves (default 20 000)
    sigma_mu    : float — intrinsic distance-modulus scatter [mag] (default 0.12)
    calib_floor : float — systematic floor on σ(H₀) [km/s/Mpc] (default 0.30)

    Returns
    -------
    float
        Forecast σ(H₀) [km/s/Mpc].

    Raises
    ------
    ValueError
        If n_sne ≤ 0 or sigma_mu ≤ 0 or calib_floor < 0.
    """
    if n_sne <= 0:
        raise ValueError(f"n_sne must be > 0; got {n_sne!r}")
    if sigma_mu <= 0.0:
        raise ValueError(f"sigma_mu must be > 0; got {sigma_mu!r}")
    if calib_floor < 0.0:
        raise ValueError(f"calib_floor must be ≥ 0; got {calib_floor!r}")
    sigma_frac = (math.log(10.0) / 5.0) * sigma_mu
    stat = _H0_REFERENCE * sigma_frac / math.sqrt(float(n_sne))
    return math.sqrt(stat ** 2 + calib_floor ** 2)


def roman_bao_sigma_w(
    n_spec: int = ROMAN_N_SPEC_GALAXIES,
    f_sky: float = ROMAN_F_SKY,
    z_eff: float = ROMAN_Z_EFF_SPEC,
) -> float:
    """Forecast 1σ uncertainty on w from Roman spectroscopic BAO at z ~ 1.5.

    Simplified Fisher-matrix estimate for a single-w EoS from BAO distance
    measurements at an effective redshift z_eff:

        σ(w)_BAO  ≈  C_bao / √(N_spec × f_sky)  ×  (1 + z_eff) / 2

    The (1+z_eff)/2 factor accounts for the approximate reduction in BAO
    constraining power at higher redshifts where shot noise increases.
    Calibrated so that the Roman baseline yields σ(w)_BAO ≈ 0.05.

    Parameters
    ----------
    n_spec : int   — spectroscopic Hα galaxies (default 3×10⁷)
    f_sky  : float — effective sky fraction (default 0.0485)
    z_eff  : float — effective BAO redshift (default 1.5)

    Returns
    -------
    float
        Forecast σ(w) from spectroscopic BAO.

    Raises
    ------
    ValueError
        If n_spec ≤ 0 or f_sky ∉ (0, 1] or z_eff < 0.
    """
    if n_spec <= 0:
        raise ValueError(f"n_spec must be > 0; got {n_spec!r}")
    if not 0.0 < f_sky <= 1.0:
        raise ValueError(f"f_sky must be in (0, 1]; got {f_sky!r}")
    if z_eff < 0.0:
        raise ValueError(f"z_eff must be ≥ 0; got {z_eff!r}")
    base = _BAO_W_COEFF / math.sqrt(float(n_spec) * f_sky)
    return base * (1.0 + z_eff) / 2.0


def roman_combined_sigma_w(sigma_wl: float, sigma_bao: float) -> float:
    """Combine WL and BAO σ(w) constraints in inverse quadrature.

    Assumes the two probes are uncorrelated:

        σ_combined  =  1 / √( 1/σ_wl² + 1/σ_bao² )

    Parameters
    ----------
    sigma_wl  : float — σ(w) from weak lensing
    sigma_bao : float — σ(w) from spectroscopic BAO

    Returns
    -------
    float
        Combined σ(w).

    Raises
    ------
    ValueError
        If either sigma is ≤ 0.
    """
    if sigma_wl <= 0.0:
        raise ValueError(f"sigma_wl must be > 0; got {sigma_wl!r}")
    if sigma_bao <= 0.0:
        raise ValueError(f"sigma_bao must be > 0; got {sigma_bao!r}")
    return 1.0 / math.sqrt(1.0 / sigma_wl ** 2 + 1.0 / sigma_bao ** 2)


def roman_bao_shift_kk() -> float:
    """Return the UM fractional BAO shift Δr_BAO/r_BAO from the KK radion.

    From Pillar 59 (matter_power_spectrum.py), eq. [6]:

        Δr_BAO / r_BAO  ≈  ½ × f_braid  =  ½ × c_s² / k_CS

    This is the small sub-percent shift from the braided KK sound speed on the
    BAO standard ruler.  The shift is far below Roman's ~0.3% BAO precision at
    z ~ 1.5.

    Returns
    -------
    float
        Δr_BAO / r_BAO ≈ 7.1 × 10⁻⁴.
    """
    return 0.5 * F_BRAID


def roman_s8_kk(
    s8_lcdm: float = S8_PLANCK,
    f_braid: float = F_BRAID,
) -> float:
    """Return the KK-modified S₈ parameter.

    The KK suppression of the matter power spectrum (Pillar 59) reduces σ₈ by
    a fractional amount ½ f_braid, which propagates linearly to S₈:

        S₈_KK  ≈  S₈_ΛCDM × (1 − ½ f_braid)

    For the canonical UM: S₈_KK ≈ 0.832 × (1 − 7.1 × 10⁻⁴) ≈ 0.8314.

    Parameters
    ----------
    s8_lcdm : float — ΛCDM / Planck S₈ reference (default 0.832)
    f_braid : float — KK radion pressure fraction (default F_BRAID ≈ 1.42 × 10⁻³)

    Returns
    -------
    float
        KK-modified S₈_KK.

    Raises
    ------
    ValueError
        If s8_lcdm ≤ 0 or f_braid < 0.
    """
    if s8_lcdm <= 0.0:
        raise ValueError(f"s8_lcdm must be > 0; got {s8_lcdm!r}")
    if f_braid < 0.0:
        raise ValueError(f"f_braid must be ≥ 0; got {f_braid!r}")
    return s8_lcdm * (1.0 - 0.5 * f_braid)


def roman_um_w_tension_audit(
    sigma_roman_w: float,
    w_roman_central: float = W0_DESI_DR2,
) -> Dict[str, Any]:
    """Audit the tension between the UM w_KK prediction and a Roman-like constraint.

    Computes:
        - UM w_KK = −1 + (2/3) c_s² ≈ −0.9302
        - Tension = |w_KK − w_Roman| / σ_Roman
        - Whether the UM is consistent at < 1σ, 2σ, 3σ

    Parameters
    ----------
    sigma_roman_w   : float — forecast 1σ uncertainty on w from Roman
    w_roman_central : float — central value of Roman w constraint (default DESI DR2)

    Returns
    -------
    dict with keys:
        ``w_kk``            : float — UM prediction ≈ −0.9302
        ``w_roman``         : float — Roman/DESI central value
        ``sigma_roman``     : float — Roman 1σ on w
        ``tension_sigma``   : float — |w_KK − w_Roman| / σ_Roman
        ``consistent_1s``   : bool  — tension < 1σ
        ``consistent_2s``   : bool  — tension < 2σ
        ``consistent_3s``   : bool  — tension < 3σ
        ``falsified_3s``    : bool  — True if tension > 3σ (UM disfavored)
        ``honest_status``   : str
        ``summary``         : str

    Raises
    ------
    ValueError
        If sigma_roman_w ≤ 0.
    """
    if sigma_roman_w <= 0.0:
        raise ValueError(f"sigma_roman_w must be > 0; got {sigma_roman_w!r}")
    tension = abs(W_KK - w_roman_central) / sigma_roman_w
    c1 = tension < 1.0
    c2 = tension < 2.0
    c3 = tension < 3.0
    if c1:
        status = "CONSISTENT (<1σ) — UM w_KK lies within Roman 1σ band"
    elif c2:
        status = "MILD TENSION (1–2σ) — UM w_KK lies outside 1σ but within 2σ"
    elif c3:
        status = "TENSION (2–3σ) — UM w_KK disfavored at 2–3σ"
    else:
        status = "FALSIFIED (>3σ) — UM w_KK is excluded by Roman at >3σ"
    return {
        "w_kk":          W_KK,
        "w_roman":       w_roman_central,
        "sigma_roman":   sigma_roman_w,
        "tension_sigma": tension,
        "consistent_1s": c1,
        "consistent_2s": c2,
        "consistent_3s": c3,
        "falsified_3s":  not c3,
        "honest_status": status,
        "summary": (
            f"UM predicts w_KK = {W_KK:.4f}; Roman-level precision σ(w) = "
            f"{sigma_roman_w:.4f} at central value w = {w_roman_central:.4f}. "
            f"Tension = {tension:.2f}σ.  Status: {status}"
        ),
    }


def roman_um_s8_audit(
    s8_wl_surveys: float = S8_WEAK_LENSING,
    sigma_s8: float = SIGMA_S8_WEAK_LENSING,
) -> Dict[str, Any]:
    """Audit the S₈ tension: UM KK prediction vs. weak-lensing measurements.

    The UM predicts a negligibly small KK suppression of S₈:

        S₈_KK ≈ S₈_Planck × (1 − ½ f_braid)  ≈  0.8314

    This does not resolve the ~3σ tension between Planck (S₈ ≈ 0.832) and
    weak-lensing surveys (KiDS-1000/DES Y3: S₈ ≈ 0.759 ± 0.024).

    Parameters
    ----------
    s8_wl_surveys : float — weak-lensing S₈ central value (default 0.759)
    sigma_s8      : float — weak-lensing σ(S₈) (default 0.024)

    Returns
    -------
    dict with keys:
        ``s8_lcdm``         : float — Planck / ΛCDM S₈ ≈ 0.832
        ``s8_kk``           : float — KK-modified S₈ ≈ 0.8314
        ``kk_shift``        : float — |S₈_KK − S₈_ΛCDM| ≈ 5.9 × 10⁻⁴
        ``s8_wl_surveys``   : float — KiDS-1000/DES Y3 measurement
        ``sigma_s8``        : float — measurement uncertainty
        ``tension_planck_wl``: float — (S₈_Planck − S₈_WL) / σ (Planck tension)
        ``kk_resolves_tension``: bool — False (shift is negligible)
        ``honest_status``   : str
        ``summary``         : str

    Raises
    ------
    ValueError
        If sigma_s8 ≤ 0.
    """
    if sigma_s8 <= 0.0:
        raise ValueError(f"sigma_s8 must be > 0; got {sigma_s8!r}")
    s8_kk = roman_s8_kk()
    kk_shift = abs(s8_kk - S8_PLANCK)
    tension_planck_wl = (S8_PLANCK - s8_wl_surveys) / sigma_s8
    resolves = kk_shift > 0.5 * abs(S8_PLANCK - s8_wl_surveys)
    return {
        "s8_lcdm":              S8_PLANCK,
        "s8_kk":                s8_kk,
        "kk_shift":             kk_shift,
        "s8_wl_surveys":        s8_wl_surveys,
        "sigma_s8":             sigma_s8,
        "tension_planck_wl":    tension_planck_wl,
        "kk_resolves_tension":  resolves,
        "honest_status": (
            "NOT RESOLVED — KK suppression δS₈/S₈ ≈ 0.07% is negligible "
            "compared to the ~8% S₈ tension."
        ),
        "summary": (
            f"Planck S₈ = {S8_PLANCK:.3f}; KiDS-1000/DES Y3 S₈ = "
            f"{s8_wl_surveys:.3f} ± {sigma_s8:.3f} "
            f"({tension_planck_wl:.1f}σ tension).  "
            f"UM KK shift: S₈_KK = {s8_kk:.4f} (shift = {kk_shift:.2e}).  "
            "The KK suppression does not resolve the S₈ tension — it is "
            "documented here as an upper bound on UM's contribution."
        ),
    }


def roman_falsification_conditions() -> Dict[str, Any]:
    """Enumerate the conditions under which Roman data would falsify the UM.

    Returns
    -------
    dict with keys:
        ``w_kk_prediction``       : float — UM w_KK ≈ −0.9302
        ``wa_kk_prediction``      : float — UM wₐ = 0
        ``bao_shift_prediction``  : float — Δr/r ≈ 7.1 × 10⁻⁴
        ``falsifiers`` : list[dict] — each with 'condition', 'threshold', 'status'
        ``primary_falsifier``     : str — the most decisive test
        ``summary``               : str

    Notes
    -----
    These are the primary falsification criteria using Roman alone (at planned
    survey specifications):
    1. w₀ tension:    |w₀_Roman − w_KK| > 3 σ(w)_Roman with σ(w) ~ 0.02
    2. wₐ tension:    |wₐ_Roman − 0| > 3 σ(wₐ)_Roman with σ(wₐ) ~ 0.07
    3. S₈ tension:    |S₈_Roman − S₈_KK| > 3 σ(S₈)_Roman with σ(S₈) ~ 0.003
    4. BAO shift:     Δr/r_Roman > 3 × 0.003 = 0.009 at z ~ 1.5 (not detectable)
    5. wₐ ≠ 0:        A confirmed wₐ ≠ 0 at > 3σ would require new physics beyond
                      the stabilised KK zero-mode.
    """
    sigma_w = roman_wl_sigma_w()
    sigma_s8 = roman_wl_sigma_s8()
    bao_shift = roman_bao_shift_kk()
    # approximate combined sigma_wa from WL + BAO
    sigma_wa_approx = 0.07
    return {
        "w_kk_prediction":      W_KK,
        "wa_kk_prediction":     W_A_KK,
        "bao_shift_prediction": bao_shift,
        "falsifiers": [
            {
                "probe":     "Weak lensing w₀",
                "condition": f"|w₀_Roman − {W_KK:.4f}| > 3σ",
                "threshold": 3.0 * sigma_w,
                "sigma_forecast": sigma_w,
                "status":    "TESTABLE — Roman WL reaches ~0.02 precision on w₀",
            },
            {
                "probe":     "CPL wₐ running",
                "condition": f"|wₐ_Roman − 0| > 3σ with σ(wₐ) ~ {sigma_wa_approx:.2f}",
                "threshold": 3.0 * sigma_wa_approx,
                "sigma_forecast": sigma_wa_approx,
                "status":    "TESTABLE — Roman WL+BAO combination reaches σ(wₐ) ~ 0.07",
            },
            {
                "probe":     "Cosmic shear S₈",
                "condition": f"|S₈_Roman − {roman_s8_kk():.4f}| > 3σ",
                "threshold": 3.0 * sigma_s8,
                "sigma_forecast": sigma_s8,
                "status":    (
                    "TESTABLE — but KK shift is negligible; S₈ falsification "
                    "requires the Planck–WL discrepancy to be resolved first"
                ),
            },
            {
                "probe":     "BAO distance shift",
                "condition": "Δr/r_Roman > 0.009 at z ~ 1.5",
                "threshold": 0.009,
                "sigma_forecast": 0.003,
                "status":    (
                    f"NOT DETECTABLE — UM shift Δr/r ≈ {bao_shift:.2e} is "
                    "~4× below Roman's ~0.3% BAO precision"
                ),
            },
        ],
        "primary_falsifier": (
            "Dark energy equation of state: if Roman WL + BAO combined measure "
            f"w₀ that differs from w_KK = {W_KK:.4f} by more than 3σ(w) ~ 0.06, "
            "or confirm wₐ ≠ 0 at > 3σ, the UM stabilised-KK dark energy "
            "prediction is falsified.  Roman is expected to reach σ(w) ~ 0.02 "
            "from WL alone and σ(wₐ) ~ 0.07 from WL+BAO."
        ),
        "summary": (
            "Roman Space Telescope is the primary near-term falsifier of the UM "
            "dark energy prediction w_KK ≈ −0.9302 (wₐ = 0).  At Roman's "
            "design sensitivity, it can exclude the UM at >3σ if the true w₀ "
            "is outside [w_KK − 0.06, w_KK + 0.06] ≈ [−0.99, −0.87].  "
            "S₈ and BAO shift tests provide complementary but weaker constraints.  "
            "Note: UM does not predict H₀ from first principles."
        ),
    }


def roman_summary() -> Dict[str, Any]:
    """Complete Pillar 66 audit: Roman Space Telescope UM falsification forecasts.

    Returns
    -------
    dict with keys:
        ``pillar``              : int   — 66
        ``title``               : str
        ``mission``             : str   — mission description
        ``w_kk``                : float — UM dark energy EoS ≈ −0.9302
        ``wa_kk``               : float — UM CPL running = 0
        ``ns_um``               : float — UM spectral index
        ``r_braided``           : float — UM tensor-to-scalar
        ``f_braid``             : float — KK pressure fraction
        ``sigma_w_wl``          : float — forecast σ(w) from Roman WL
        ``sigma_w_bao``         : float — forecast σ(w) from Roman BAO
        ``sigma_w_combined``    : float — forecast combined σ(w)
        ``sigma_s8``            : float — forecast σ(S₈) from Roman WL
        ``sigma_h0_sne``        : float — forecast σ(H₀) from Roman SNe [km/s/Mpc]
        ``bao_shift``           : float — UM BAO shift Δr/r
        ``s8_kk``               : float — KK-modified S₈
        ``s8_resolves_tension`` : bool  — False (KK shift is negligible)
        ``desi_dr2_w0_tension_sigma`` : float — current DESI tension with UM w_KK
        ``primary_falsifier``   : str
        ``honest_gaps``         : list[str]
        ``reference``           : str
    """
    sigma_w_wl = roman_wl_sigma_w()
    sigma_w_bao = roman_bao_sigma_w()
    sigma_w_comb = roman_combined_sigma_w(sigma_w_wl, sigma_w_bao)
    sigma_s8 = roman_wl_sigma_s8()
    sigma_h0 = roman_sne_sigma_h0()
    bao_shift = roman_bao_shift_kk()
    s8_kk = roman_s8_kk()
    desi_tension = abs(W_KK - W0_DESI_DR2) / SIGMA_W0_DESI_DR2
    return {
        "pillar":          66,
        "title":           (
            "Pillar 66 — Nancy Grace Roman Space Telescope: UM Falsification Forecasts"
        ),
        "mission":         (
            "NASA flagship infrared observatory (2.4 m, 300 Mpx WFI), launch Sept 2026. "
            "HLWAS: 2000 deg², ~500M galaxy WL shapes, ~30M Hα spec-z at 1<z<2, "
            "~20 000 calibrated Type Ia SNe."
        ),
        "w_kk":                    W_KK,
        "wa_kk":                   W_A_KK,
        "ns_um":                   NS_UM,
        "r_braided":               R_BRAIDED,
        "f_braid":                 F_BRAID,
        "sigma_w_wl":              sigma_w_wl,
        "sigma_w_bao":             sigma_w_bao,
        "sigma_w_combined":        sigma_w_comb,
        "sigma_s8":                sigma_s8,
        "sigma_h0_sne":            sigma_h0,
        "bao_shift":               bao_shift,
        "s8_kk":                   s8_kk,
        "s8_resolves_tension":     False,
        "desi_dr2_w0_tension_sigma": desi_tension,
        "primary_falsifier": (
            "Roman WL+BAO combined w₀ and wₐ measurement (σ(w)~0.02, σ(wₐ)~0.07). "
            "Falsified if |w₀_Roman − w_KK| > 3σ or |wₐ_Roman| > 3σ(wₐ)."
        ),
        "honest_gaps": [
            "σ(w) and σ(S₈) use simplified Fisher-matrix scalings; full forecasts "
            "require multi-z-bin Fisher matrices and nuisance-parameter marginalisation.",
            "w_KK = −1 + (2/3) c_s² uses slow-roll approximation; higher-order "
            "corrections to KK EoS are not computed.",
            "S₈ tension (Planck vs. KiDS-1000/DES) is NOT resolved by the UM "
            "(KK shift δS₈/S₈ ≈ 0.07%).",
            "BAO shift Δr/r ≈ 7.1 × 10⁻⁴ is undetectable by Roman's ~0.3% precision.",
            "UM does not predict H₀ from first principles; the Hubble tension remains "
            "unsolved in the UM framework.",
            "DESI wₐ = −0.63 ± 0.28 is a 2.25σ tension with UM wₐ = 0; formal 2027 "
            "DESI 47M-galaxy results will clarify whether wₐ ≠ 0 is confirmed.",
        ],
        "reference": (
            "NASA Roman Science Book (2019; arXiv:1503.03757); "
            "Roman mission: https://science.nasa.gov/mission/roman-space-telescope/; "
            "DESI DR2 (April 2026); Pillar 38 (observational_frontiers.py); "
            "Pillar 59 (matter_power_spectrum.py)."
        ),
    }
