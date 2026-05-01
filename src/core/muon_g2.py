# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/muon_g2.py
====================
Pillar 51 — Muon Anomalous Magnetic Moment: KK and ALP Analysis.

Physical motivation
--------------------
The muon anomalous magnetic moment a_μ = (g_μ − 2)/2 has been measured
to extraordinary precision by the Fermilab Muon g−2 collaboration.  The
final result (June 3, 2025):

    a_μ^exp = (116 592 070.5 ± 146) × 10⁻¹²  [127 ppb precision]

The discrepancy with the data-driven SM prediction:

    Δa_μ ≈ +261 × 10⁻¹¹  (~5σ vs WP2023 data-driven)
    Δa_μ ≈ +12 × 10⁻¹¹   (~1σ vs BMW+ lattice QCD)

This module computes the Unitary Manifold contributions to a_μ:

1. **KK graviton loop correction** (ADD / RS2 mechanism) — negligible because
   M_KK ~ M_Pl/r_c ~ 10¹⁸ GeV, giving δa_μ^KK ~ 10⁻⁴¹.

2. **ALP-mediated Barr–Zee two-loop diagram** — the birefringence ALP
   (axion-like particle) with g_aγγ = k_cs · α_EM / (2π² r_c) could
   contribute if it has a non-zero Yukawa coupling to muons.  The UM
   does not derive y_μ; this function returns an upper bound.

3. **B_μ dark photon mass bound** — the compactification gauge field B_μ
   could act as a dark photon mediator.  Its mass from the Goldberger–Wise
   mechanism is estimated, and the coupling to SM fermions is bounded by
   the birefringence measurement.

All results confirm the conclusion in FALLIBILITY.md §VII: the UM KK
correction is ~30 orders of magnitude too small to explain the anomaly.
The module is provided for completeness and transparency.

Public API
----------
kk_graviton_correction(m_mu_GeV, M_KK_GeV, c_s) → float
    δa_μ from the one-loop KK graviton tower.

alp_barr_zee_upper_bound(k_cs, r_c, y_mu_max, m_alp_GeV, m_f_GeV) → float
    Upper bound on δa_μ from the ALP-mediated Barr–Zee diagram.

bmu_dark_photon_mass_estimate(phi0_eff, r_c) → float
    Estimate of the B_μ zero-mode mass from Goldberger–Wise potential.

bmu_coupling_from_birefringence(beta_deg, k_cs, r_c) → float
    Upper bound on B_μ–SM fermion coupling from the birefringence angle.

full_mu_g2_report() → dict
    Complete summary of all UM contributions to a_μ at canonical parameters.

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
from typing import Dict

# ---------------------------------------------------------------------------
# Physical constants (SI / natural hybrid; all energies in GeV)
# ---------------------------------------------------------------------------

#: Fine-structure constant (dimensionless)
ALPHA_EM: float = 1.0 / 137.035999084

#: Reduced Planck mass [GeV]
M_PL_GEV: float = 2.435e18

#: Muon mass [GeV]
M_MU_GEV: float = 0.105658375

#: Electron mass [GeV]
M_E_GEV: float = 0.000510999

#: Tau mass [GeV]
M_TAU_GEV: float = 1.77686

# ---------------------------------------------------------------------------
# Canonical UM parameters
# ---------------------------------------------------------------------------

#: Winding number (n_w = 5, S¹/Z₂ orbifold)
N_W: int = 5

#: Braided Chern–Simons level k_cs = 5² + 7² = 74
K_CS: int = 74

#: Compactification radius r_c [M_Pl⁻¹] (KK radius, Planck units)
R_C_PLANCK: float = 12.0

#: Braided sound speed c_s = 12/37
C_S: float = 12.0 / 37.0

# Derived: first KK mass M_KK_1 = M_Pl / r_c  [GeV]
M_KK_1_GEV: float = M_PL_GEV / R_C_PLANCK   # ≈ 2.029 × 10¹⁷ GeV

# ---------------------------------------------------------------------------
# Experimental / SM reference values
# ---------------------------------------------------------------------------

#: Final Fermilab result (June 2025), central value × 10¹¹
#: (standard physics notation; a_μ = 116592070.5 × 10⁻¹¹ ≈ 1.1659 × 10⁻³)
A_MU_EXP_1E11: float = 116_592_070.5
#: Combined experimental uncertainty × 10¹¹
A_MU_EXP_UNC_1E11: float = 146.0

#: SM data-driven (WP2023) prediction × 10¹¹
A_MU_SM_DD_1E11: float = 116_591_810.0
#: SM data-driven uncertainty × 10¹¹
A_MU_SM_DD_UNC_1E11: float = 43.0

#: SM lattice QCD (BMW+) prediction × 10¹¹
A_MU_SM_LATTICE_1E11: float = 116_591_954.0
#: SM lattice QCD uncertainty × 10¹¹
A_MU_SM_LATTICE_UNC_1E11: float = 55.0

#: Data-driven discrepancy Δa_μ × 10¹¹
DELTA_A_MU_DD_1E11: float = 261.0

#: Significance vs data-driven SM (σ)
SIGNIFICANCE_DD: float = 5.0

#: Significance vs lattice QCD SM (σ)
SIGNIFICANCE_LATTICE: float = 1.0


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def kk_graviton_correction(
    m_mu_GeV: float = M_MU_GEV,
    M_KK_GeV: float = M_KK_1_GEV,
    c_s: float = C_S,
) -> float:
    """Return δa_μ from the one-loop KK graviton tower (ADD/RS mechanism).

    The Arkani-Hamed–Dimopoulos–Dvali formula for the leading KK spin-2
    graviton correction is:

        δa_μ^KK ≈ (α_EM / π) × (m_μ / M_KK_1)² × F_spin2(c_s)

    where F_spin2 is an O(1) form factor that depends on the braid sound
    speed c_s.  We use F_spin2(c_s) = 1 + c_s² as a conservative upper
    bound (for c_s = 12/37 this gives F ≈ 1.105).

    Parameters
    ----------
    m_mu_GeV : float
        Muon mass in GeV (default: 0.10566 GeV).
    M_KK_GeV : float
        First KK mass M_KK_1 = M_Pl / r_c in GeV (default: M_Pl/12).
    c_s : float
        Braided sound speed (default: 12/37).

    Returns
    -------
    float
        δa_μ^KK (dimensionless, typical value ~10⁻⁴¹).
    """
    if M_KK_GeV <= 0:
        raise ValueError(f"M_KK_GeV must be > 0, got {M_KK_GeV}")
    if m_mu_GeV <= 0:
        raise ValueError(f"m_mu_GeV must be > 0, got {m_mu_GeV}")
    ratio_sq = (m_mu_GeV / M_KK_GeV) ** 2
    F_spin2 = 1.0 + c_s ** 2
    return (ALPHA_EM / math.pi) * ratio_sq * F_spin2


def alp_barr_zee_upper_bound(
    k_cs: int = K_CS,
    r_c: float = R_C_PLANCK,
    y_mu_max: float = 1.0,
    m_alp_GeV: float = 1e-3,
    m_f_GeV: float = M_TAU_GEV,
) -> float:
    """Return an upper bound on δa_μ from the ALP-mediated Barr–Zee diagram.

    The two-loop Barr–Zee contribution from an ALP of mass m_a with
    axion–photon coupling g_aγγ and Yukawa coupling y_μ to the muon is:

        δa_μ^BZ ≈ (α_EM × y_μ × g_aγγ × m_μ² ) / (4π³ × m_a²) × h(z_f)

    where z_f = (m_f / m_a)² and h(z) = ∫ f(z)/z is the Barr–Zee loop
    function.  For m_f ≫ m_a (heavy loop fermion), h(z) → ln(z)/2.
    For a light ALP with m_a ≪ m_f, this gives an IR-enhanced contribution.

    The UM determines g_aγγ from the Chern–Simons coupling:

        g_aγγ = k_cs × α_EM / (2π² × r_c × M_Pl)     [in natural units]

    but does NOT determine y_μ (the ALP–muon Yukawa).  This function
    returns the upper bound obtained by setting y_μ = y_mu_max.

    Parameters
    ----------
    k_cs : int
        Chern–Simons level (default: 74).
    r_c : float
        Compactification radius in Planck units (default: 12).
    y_mu_max : float
        Maximum allowed ALP–muon Yukawa (default: 1.0; perturbative limit).
    m_alp_GeV : float
        ALP mass in GeV (default: 1e-3 GeV = 1 MeV; light ALP regime).
    m_f_GeV : float
        Loop fermion mass in GeV (default: tau mass 1.777 GeV).

    Returns
    -------
    float
        Upper bound on |δa_μ^BZ| (dimensionless).
    """
    if m_alp_GeV <= 0:
        raise ValueError(f"m_alp_GeV must be > 0, got {m_alp_GeV}")
    if m_f_GeV <= 0:
        raise ValueError(f"m_f_GeV must be > 0, got {m_f_GeV}")
    if r_c <= 0:
        raise ValueError(f"r_c must be > 0, got {r_c}")
    # g_aγγ in units of GeV⁻¹ (converting M_Pl from Planck units to GeV)
    g_agg = k_cs * ALPHA_EM / (2.0 * math.pi ** 2 * r_c * M_PL_GEV)   # GeV⁻¹

    # Barr–Zee loop function h(z) ≈ ln(z)/2 for z ≫ 1
    z_f = (m_f_GeV / m_alp_GeV) ** 2
    if z_f > 1.0:
        h_z = 0.5 * math.log(z_f)
    else:
        # Exact limit for z ≤ 1: h(z) = ∫₀¹ dx (1-x)/x · ln[(1-x)/x + z/x]
        # Approximate with h(z) ≈ 1 - z (light fermion, heavy ALP)
        h_z = max(1.0 - z_f, 1e-10)

    # δa_μ^BZ upper bound
    delta_a_mu = (
        ALPHA_EM * y_mu_max * g_agg * M_MU_GEV ** 2
        / (4.0 * math.pi ** 3 * m_alp_GeV ** 2)
        * h_z
    )
    return abs(delta_a_mu)


def bmu_dark_photon_mass_estimate(
    phi0_eff: float = 31.42,
    r_c: float = R_C_PLANCK,
) -> float:
    """Estimate the B_μ zero-mode mass from the Goldberger–Wise potential.

    The KK gauge field B_μ (fifth-dimension gauge boson) acquires a mass
    from the Goldberger–Wise moduli-stabilisation potential.  The leading
    estimate of the zero-mode mass in Planck units is:

        m_B ≈ (1 / r_c) × exp(−π × k × r_c × φ₀_eff)

    evaluated at the FTUM fixed point φ₀_eff.  In the large-moduli regime
    this mass is Planck-scale suppressed.

    Parameters
    ----------
    phi0_eff : float
        Effective 4D radion vev (default: 31.42, FTUM fixed point).
    r_c : float
        Compactification radius in Planck units (default: 12).

    Returns
    -------
    float
        Estimated B_μ zero-mode mass in Planck units.
    """
    if r_c <= 0:
        raise ValueError(f"r_c must be > 0, got {r_c}")
    if phi0_eff <= 0:
        raise ValueError(f"phi0_eff must be > 0, got {phi0_eff}")
    # Goldberger–Wise suppression: exponentially light compared to M_KK
    exponent = math.pi * r_c * phi0_eff
    # Clamp to prevent exp() underflow (Python's exp() underflows around -700)
    if exponent > 700:
        return 0.0
    return (1.0 / r_c) * math.exp(-exponent)


def bmu_coupling_from_birefringence(
    beta_deg: float = 0.331,
    k_cs: int = K_CS,
    r_c: float = R_C_PLANCK,
) -> float:
    """Bound on the B_μ–SM fermion effective coupling from the birefringence angle.

    The birefringence angle β relates to the axion–photon coupling as:

        β = (g_aγγ / 2) × ∫ B · dl    →    g_aγγ ~ 2β / (B_CMB × L_Hubble)

    We use the Chern–Simons relation g_aγγ = k_cs × α_EM / (2π² r_c M_Pl)
    to derive a dimensionless effective coupling ε_B from the requirement
    that the B_μ contribution to β does not exceed the observed β:

        ε_B ≤ β [rad] / (π × k_cs / 4)

    This is an O(1) upper bound; the exact value requires knowledge of the
    ALP-to-B_μ mixing angle, which is not derived in the UM.

    Parameters
    ----------
    beta_deg : float
        Observed/predicted birefringence angle in degrees (default: 0.331°).
    k_cs : int
        Chern–Simons level (default: 74).
    r_c : float
        Compactification radius [Planck units] (default: 12).

    Returns
    -------
    float
        Upper bound on the effective B_μ–SM coupling (dimensionless).
    """
    beta_rad = math.radians(beta_deg)
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs}")
    denominator = math.pi * k_cs / 4.0
    return beta_rad / denominator


def full_mu_g2_report(
    m_mu_GeV: float = M_MU_GEV,
    M_KK_GeV: float = M_KK_1_GEV,
    c_s: float = C_S,
    k_cs: int = K_CS,
    r_c: float = R_C_PLANCK,
    y_mu_max: float = 1.0,
    m_alp_GeV: float = 1e-3,
    m_f_GeV: float = M_TAU_GEV,
    phi0_eff: float = 31.42,
    beta_deg: float = 0.331,
) -> dict:
    """Return a complete summary of all UM contributions to a_μ.

    Parameters
    ----------
    See individual function docstrings for parameter definitions.

    Returns
    -------
    dict with keys:

    ``delta_a_mu_kk``          : float — KK graviton loop correction (~10⁻⁴¹)
    ``delta_a_mu_bz_upper``    : float — ALP Barr–Zee upper bound
    ``bmu_mass_planck``        : float — B_μ zero-mode mass [M_Pl]
    ``bmu_coupling_bound``     : float — B_μ–SM coupling upper bound
    ``ratio_kk_to_anomaly``    : float — δa_μ^KK / Δa_μ_data_driven
    ``a_mu_exp``               : float — experimental central value
    ``delta_a_mu_data_driven`` : float — data-driven discrepancy
    ``sigma_data_driven``      : float — significance vs data-driven SM
    ``sigma_lattice_qcd``      : float — significance vs lattice QCD
    ``um_can_explain_anomaly`` : bool  — False (KK correction negligible)
    ``um_is_falsified``        : bool  — False (UM is not a TeV-scale model)
    ``summary``                : str   — human-readable assessment
    """
    delta_kk = kk_graviton_correction(m_mu_GeV, M_KK_GeV, c_s)
    delta_bz = alp_barr_zee_upper_bound(k_cs, r_c, y_mu_max, m_alp_GeV, m_f_GeV)
    m_bmu    = bmu_dark_photon_mass_estimate(phi0_eff, r_c)
    eps_bmu  = bmu_coupling_from_birefringence(beta_deg, k_cs, r_c)

    # Δa_μ (data-driven) in natural units (×1)
    delta_dd = DELTA_A_MU_DD_1E11 * 1e-11
    ratio_kk = delta_kk / delta_dd if delta_dd > 0 else float("inf")

    return {
        "delta_a_mu_kk":          delta_kk,
        "delta_a_mu_bz_upper":    delta_bz,
        "bmu_mass_planck":        m_bmu,
        "bmu_coupling_bound":     eps_bmu,
        "ratio_kk_to_anomaly":    ratio_kk,
        "a_mu_exp":               A_MU_EXP_1E11 * 1e-11,
        "delta_a_mu_data_driven": delta_dd,
        "sigma_data_driven":      SIGNIFICANCE_DD,
        "sigma_lattice_qcd":      SIGNIFICANCE_LATTICE,
        "um_can_explain_anomaly": False,
        "um_is_falsified":        False,
        "M_KK_1_GeV":             M_KK_GeV,
        "m_mu_GeV":               m_mu_GeV,
        "summary": (
            "The UM KK graviton correction to a_mu is ~{:.1e}, "
            "approximately {:.0e} times smaller than the data-driven "
            "discrepancy Delta_a_mu ~ {:.1e}.  The UM is not falsified "
            "by the muon g-2 anomaly because it was designed at the "
            "Planck scale, not the TeV scale.  The ALP Barr-Zee upper "
            "bound (|y_mu| <= {:.1f}) is {:.1e}.".format(
                delta_kk, ratio_kk, delta_dd, y_mu_max, delta_bz
            )
        ),
    }


def orders_of_magnitude_below_anomaly(
    m_mu_GeV: float = M_MU_GEV,
    M_KK_GeV: float = M_KK_1_GEV,
    c_s: float = C_S,
) -> float:
    """Return the number of orders of magnitude by which δa_μ^KK is below Δa_μ.

    Useful for asserting that the KK correction is definitively negligible.

    Returns
    -------
    float
        log10(Δa_μ_data_driven / δa_μ^KK) > 0.
    """
    delta_kk = kk_graviton_correction(m_mu_GeV, M_KK_GeV, c_s)
    delta_dd = DELTA_A_MU_DD_1E11 * 1e-11
    if delta_kk <= 0:
        return float("inf")
    return math.log10(delta_dd / delta_kk)
