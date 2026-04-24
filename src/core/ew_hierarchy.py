# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/ew_hierarchy.py
=========================
Pillar 50 — Electroweak Hierarchy Problem: Three Candidate Mechanisms.

Physical context
----------------
The Unitary Manifold predicts the natural electroweak (EW) scale from its
Kaluza-Klein geometry as

    M_EW_UM / M_Planck = √(c_s / k_cs) = √((12/37) / 74) ≈ 0.0662

corresponding to M_EW_UM ≈ 8.1 × 10¹⁷ GeV — fifteen orders of magnitude
above the observed Higgs VEV v = 246 GeV = 2.01 × 10⁻¹⁷ M_Planck.

Closing this ≈ 10¹⁵·⁵ gap (the **electroweak hierarchy problem**) requires a
geometric mechanism that exponentially compresses the natural EW scale.  This
module implements and quantifies three candidate mechanisms within the UM
framework, and documents honestly that each still requires parameter fine-tuning.

Mechanism 1 — Randall-Sundrum / Goldberger-Wise Warp Factor
------------------------------------------------------------
The Randall-Sundrum-1 (RS1) model resolves the hierarchy via an exponential
warp factor on the IR brane:

    Ω = exp(−kπR)   with   kπR ≈ ln(M_Planck / v_EW) ≈ 38.4

where k is the AdS₅ curvature and R is the extra-dimension radius.  The EW
scale is then M_EW = M_Planck × Ω.

In the UM, the Goldberger-Wise (GW) stabilisation potential (Pillar 28,
bh_remnant.py) enforces a lower bound φ ≥ φ_min on the radion.  If boundary
conditions set

    φ_min = φ₀ × (v_EW / M_Planck) ≈ φ₀ × 2.01 × 10⁻¹⁷

the GW floor mimics the RS1 warp compression.  The effective kπR of the GW
setup is gw_effective_kpi_R(φ_min, φ₀) = ln(φ₀ / φ_min), identical to RS1.

**Honest gap:** Both RS1 and GW require fine-tuning of one parameter (kR or
φ_min) to reproduce 246 GeV.  Neither explains *why* that parameter has the
required value; they provide the geometric *structure* for the hierarchy
without solving the fine-tuning problem.

Mechanism 2 — Einstein-Cartan-KK Torsion (EC-KK)
-------------------------------------------------
In the G₂-torsion model (Pinčák et al. 2026, Pillar 48), dimensional
reduction of the torsion generates a negative mass-squared term for the
Higgs-like scalar:

    μ²_T = κ_T × (n_w / k_cs)² × M_KK²   [Planck²]

The Higgs VEV from the Mexican-hat potential minimum:

    v_h = M_KK × (n_w / k_cs) × √(κ_T / (2λ_h))

where λ_h ≈ 0.129 is the Higgs quartic coupling (from m_H² = 2λ_h v² at
tree level in the SM).

To reproduce v_EW = 246 GeV with M_KK at the Planck scale requires

    κ_T_needed ≈ 2 × 0.129 × (v_EW / M_Pl)² × (k_cs / n_w)² / M_KK²
               ≈ 2.5 × 10⁻³³   (for M_KK = 1 M_Planck)

**Honest gap:** This extreme fine-tuning of κ_T is no less severe than RS1.
The torsion framework is implemented in Pillar 48 (torsion_remnant.py); this
module provides the EW-scale interpretation and the functions needed to
compute what κ_T is required.

Mechanism 3 — AdS₅/CFT₄ Tower Tuned to the EW Scale
------------------------------------------------------
The UM's AdS₅/CFT₄ tower (Pillar 40, ads_cft_tower.py) provides the right
geometric structure for an RS1-type hierarchy resolution, but its warp and
compactification parameters have not previously been tuned to the EW scale.

The tower KK masses are m_n = n / R (Planck units), dressed by the RS1 warp
factor g_n = exp(−k_rs × n × π × r_c) and the UM braided spectral weights
w_n = exp(−n² / k_cs):

    m_n^phys = (n / R) × g_n

The tower-weighted effective EW mass (warp-probability-weighted mean):

    M_EW^tower = (1/R) × Σ_n n × w_n × g_n² / Σ_n w_n × g_n

When n = 1 dominates (large kπR), M_EW^tower ≈ (1/R) × exp(−k_rs × π × r_c),
reproducing the RS1 result.  At moderate kπR, higher modes (n ≥ 2) contribute
with a braided-winding suppression w_n = exp(−n²/74), which is a UM-specific
signal absent from pure RS1.

Setting M_EW^tower = v_EW / M_Planck fixes one combination of (k_rs, r_c, R).
For R = 1 (AdS radius scale), the required IR brane curvature satisfies
k_rs × π × r_c = RS1_KPI_R_CANONICAL ≈ 38.4.

The braided-warp suppression ratio

    ρ_braid = Σ_n w_n × g_n / Σ_n g_n

measures how the braiding modifies the RS1 amplitude.  At canonical kπR it is
≈ exp(−1/k_cs) ≈ 0.987 (n=1 dominates).  At smaller kπR, the ratio departs
measurably from 1 and provides a testable UM signature.

IR brane radius:  R_IR = M_Planck / v_EW ≈ 4.97 × 10¹⁶  (Planck units).

At R = R_IR and L = 1 (AdS radius), the conformal dimension of every KK mode
collapses to Δ_n ≈ 4 (the zero-mode value), since (n × L / R_IR)² ≈ 0.  This
predicts a tower of marginal operators (Δ = 4) in the dual 4D CFT — a
falsifiable prediction of this mechanism.

**Honest gap:** Mechanism 3 still requires fine-tuning of the product
k_rs × r_c ≈ 12.2 (equivalently kπR ≈ 38.4).  No first-principles derivation
of this parameter is currently available within the UM.

Key constants
-------------
- UM_EW_SCALE_PLANCK ≈ 0.0662  (geometric natural scale, far above 246 GeV)
- OBSERVED_EW_SCALE_PLANCK ≈ 2.01 × 10⁻¹⁷
- HIERARCHY_GAP_LOG10 ≈ 15.52  (orders of magnitude to close)
- RS1_KPI_R_CANONICAL ≈ 38.44  (kπR for EW scale; shared by mechanisms 1 & 3)
- ADS5_KRS_RC_CANONICAL ≈ 12.23 (k_rs × r_c for k_rs = 1)
- ADS5_IR_RADIUS_PLANCK ≈ 4.97 × 10¹⁶ (compactification radius at EW scale)
- HIGGS_QUARTIC ≈ 0.1293 (SM tree-level: λ_h = m_H² / (2 v²))

All quantities are in natural Planck units (ħ = c = G = k_B = 1) unless
explicitly labelled GeV.

Public API
----------
um_ew_scale_planck(c_s, k_cs)
    UM geometric EW scale √(c_s/k_cs) ≈ 0.0662 M_Planck.

hierarchy_gap_log10(c_s, k_cs, higgs_vev_gev, m_planck_gev)
    log₁₀[(UM EW scale) / (observed EW scale)] ≈ 15.52.

Mechanism 1 — RS1 / GW warp:
  rs1_warp_factor(kpi_R)
  rs1_ew_scale_planck(kpi_R)
  rs1_ew_scale_gev(kpi_R, m_planck_gev)
  rs1_kpi_R_for_ew_scale(higgs_vev_gev, m_planck_gev)
  gw_phi_min_for_ew_scale(phi0, higgs_vev_gev, m_planck_gev)
  gw_effective_kpi_R(phi_min, phi0)

Mechanism 2 — EC-KK torsion:
  ec_kk_torsion_mass_sq(kappa_T, n_w, k_cs, m_kk)
  ec_kk_higgs_vev_planck(kappa_T, n_w, k_cs, m_kk, lambda_h)
  ec_kk_higgs_vev_gev(kappa_T, n_w, k_cs, m_kk, lambda_h, m_planck_gev)
  kappa_T_for_ew_scale(higgs_vev_gev, n_w, k_cs, m_kk, lambda_h, m_planck_gev)

Mechanism 3 — AdS₅ tower:
  ads5_ir_compactification_radius(higgs_vev_gev, m_planck_gev)
  ads5_krs_rc_for_ew_scale(higgs_vev_gev, m_planck_gev)
  ads5_ew_scale_planck(k_rs, r_c)
  ads5_r_c_for_ew_scale(k_rs, higgs_vev_gev, m_planck_gev)
  ads5_um_tower_weighted_ew_mass(k_rs, r_c, R, k_cs, n_max)
  ads5_braided_warp_suppression(k_rs, r_c, k_cs, n_max)
  ads5_conformal_dimension_at_ew(R_IR, L, n)

Comparison:
  HierarchyComparison  (dataclass)
  compare_hierarchy_mechanisms(phi0, higgs_vev_gev, m_planck_gev, n_w, k_cs,
                                m_kk, lambda_h, k_rs, n_max)

References
----------
Randall L., Sundrum R. (1999) "A Large Mass Hierarchy from a Small Extra
    Dimension", Phys. Rev. Lett. 83, 3370–3373.
Goldberger W., Wise M. (1999) "Moduli Stabilization with Bulk Fields",
    Phys. Rev. Lett. 83, 4922–4925.
Pinčák R. et al. (2026) Gen. Rel. Grav. 58 — torsion_remnant.py (Pillar 48).
ads_cft_tower.py (Pillar 40) — AdS₅/CFT₄ KK tower dictionary.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, Planck units unless stated)
# ---------------------------------------------------------------------------

N_W_CANONICAL: int = 5
K_CS_CANONICAL: int = 74
C_S_CANONICAL: float = 12.0 / 37.0        # braided sound speed (n₂²−n₁²)/k_CS

PLANCK_MASS_GEV: float = 1.220890e19      # Planck mass [GeV]
HIGGS_VEV_GEV: float = 246.0             # observed Higgs VEV [GeV]
HIGGS_MASS_GEV: float = 125.09           # Higgs boson pole mass [GeV]
# SM tree-level Higgs quartic: λ_h = m_H²/(2v²)
HIGGS_QUARTIC: float = HIGGS_MASS_GEV ** 2 / (2.0 * HIGGS_VEV_GEV ** 2)  # ≈ 0.1293

M_KK_PLANCK_CANONICAL: float = 1.0       # KK mass scale [Planck units]
ADS_RADIUS_PLANCK: float = 1.0           # AdS₅ radius L [Planck units]
N_MAX_TOWER: int = 20                    # default KK tower truncation
PHI0_CANONICAL: float = 1.0             # GW vacuum expectation value [Planck units]

# Derived EW hierarchy constants -------------------------------------------------

# UM geometric EW scale: sqrt(c_s / k_cs) = sqrt((12/37)/74) ≈ 0.06619
UM_EW_SCALE_PLANCK: float = math.sqrt(C_S_CANONICAL / K_CS_CANONICAL)

# Observed EW scale in Planck units: v_EW / M_Planck ≈ 2.015e-17
OBSERVED_EW_SCALE_PLANCK: float = HIGGS_VEV_GEV / PLANCK_MASS_GEV

# log₁₀ of the discrepancy: log₁₀(UM / observed) ≈ 15.52
HIERARCHY_GAP_LOG10: float = math.log10(
    UM_EW_SCALE_PLANCK / OBSERVED_EW_SCALE_PLANCK
)

# kπR needed to warp M_Planck down to v_EW:
#   exp(−kπR) = v_EW / M_Pl  →  kπR = ln(M_Pl / v_EW) ≈ 38.44
RS1_KPI_R_CANONICAL: float = math.log(PLANCK_MASS_GEV / HIGGS_VEV_GEV)

# k_rs × r_c for k_rs = 1: kπR = k_rs × π × r_c → r_c = kπR / π ≈ 12.23
ADS5_KRS_RC_CANONICAL: float = RS1_KPI_R_CANONICAL / math.pi

# IR compactification radius such that m_KK1 = v_EW / M_Pl:
#   m_1 = 1/R → R_IR = M_Pl / v_EW ≈ 4.97 × 10¹⁶  [Planck units]
ADS5_IR_RADIUS_PLANCK: float = PLANCK_MASS_GEV / HIGGS_VEV_GEV


# ---------------------------------------------------------------------------
# Shared utility
# ---------------------------------------------------------------------------

def um_ew_scale_planck(
    c_s: float = C_S_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """UM geometric electroweak scale √(c_s / k_cs) in Planck units.

    Derived from the braided-winding sector (Pillars 39, 41):

        M_EW_UM / M_Pl = √(c_s / k_cs) = √((12/37) / 74) ≈ 0.0662

    This is ≈ 8.1 × 10¹⁷ GeV — fifteen orders of magnitude above the
    observed Higgs VEV.

    Parameters
    ----------
    c_s : float
        Braided sound speed (default 12/37).
    k_cs : int
        Chern-Simons level (default 74).

    Returns
    -------
    float
        Dimensionless M_EW_UM / M_Planck > 0.

    Raises
    ------
    ValueError
        If c_s ≤ 0 or k_cs ≤ 0.
    """
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    return math.sqrt(c_s / k_cs)


def hierarchy_gap_log10(
    c_s: float = C_S_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """log₁₀ of (UM EW scale) / (observed EW scale) ≈ 15.52.

    Quantifies the electroweak hierarchy gap that any successful mechanism
    must close.  A positive value means the UM natural scale is above the
    observed scale.

    Parameters
    ----------
    c_s : float
        Braided sound speed (default 12/37).
    k_cs : int
        Chern-Simons level (default 74).
    higgs_vev_gev : float
        Observed Higgs VEV [GeV] (default 246).
    m_planck_gev : float
        Planck mass [GeV] (default 1.22 × 10¹⁹).

    Returns
    -------
    float
        log₁₀ ratio > 0.

    Raises
    ------
    ValueError
        If any parameter is non-positive.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if m_planck_gev <= 0.0:
        raise ValueError(f"m_planck_gev must be > 0, got {m_planck_gev!r}")
    um_scale = um_ew_scale_planck(c_s, k_cs)
    obs_scale = higgs_vev_gev / m_planck_gev
    return math.log10(um_scale / obs_scale)


# ---------------------------------------------------------------------------
# Mechanism 1 — RS1 / Goldberger-Wise Warp Factor
# ---------------------------------------------------------------------------

def rs1_warp_factor(kpi_R: float) -> float:
    """RS1 warp factor Ω = exp(−kπR) on the IR brane.

    The Randall-Sundrum model compresses the Planck scale to the EW scale
    via the exponential warp factor at the IR brane position y = πR:

        Ω = exp(−kπR)   →   M_EW = M_Planck × Ω

    Parameters
    ----------
    kpi_R : float
        Product kπR ≥ 0 (k = AdS curvature, R = extra-dimension radius).

    Returns
    -------
    float
        Warp factor Ω ∈ (0, 1].

    Raises
    ------
    ValueError
        If kpi_R < 0.
    """
    if kpi_R < 0.0:
        raise ValueError(f"kpi_R must be ≥ 0, got {kpi_R!r}")
    return math.exp(-kpi_R)


def rs1_ew_scale_planck(kpi_R: float) -> float:
    """EW / Planck scale ratio produced by RS1 warp factor: exp(−kπR).

    Identical in value to rs1_warp_factor(kpi_R); provided separately for
    clarity of physical interpretation.

    Parameters
    ----------
    kpi_R : float
        RS1 warp exponent kπR ≥ 0.

    Returns
    -------
    float
        M_EW / M_Planck = exp(−kπR).
    """
    return rs1_warp_factor(kpi_R)


def rs1_ew_scale_gev(
    kpi_R: float,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """EW scale in GeV produced by the RS1 warp mechanism.

        M_EW = M_Planck [GeV] × exp(−kπR)

    Parameters
    ----------
    kpi_R : float
        RS1 warp exponent kπR ≥ 0.
    m_planck_gev : float
        Planck mass in GeV (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        M_EW in GeV.

    Raises
    ------
    ValueError
        If kpi_R < 0 or m_planck_gev ≤ 0.
    """
    if m_planck_gev <= 0.0:
        raise ValueError(f"m_planck_gev must be > 0, got {m_planck_gev!r}")
    return m_planck_gev * rs1_warp_factor(kpi_R)


def rs1_kpi_R_for_ew_scale(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """kπR required for the RS1 warp factor to reproduce the observed EW scale.

        exp(−kπR) = v_EW / M_Planck
        kπR = ln(M_Planck / v_EW) ≈ 38.44

    Parameters
    ----------
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        kπR ≈ 38.44.

    Raises
    ------
    ValueError
        If either argument is non-positive or higgs_vev_gev ≥ m_planck_gev.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if m_planck_gev <= 0.0:
        raise ValueError(f"m_planck_gev must be > 0, got {m_planck_gev!r}")
    if higgs_vev_gev >= m_planck_gev:
        raise ValueError(
            f"higgs_vev_gev ({higgs_vev_gev!r}) must be < m_planck_gev "
            f"({m_planck_gev!r}); the hierarchy requires v_EW << M_Pl."
        )
    return math.log(m_planck_gev / higgs_vev_gev)


def gw_phi_min_for_ew_scale(
    phi0: float = PHI0_CANONICAL,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """GW radion floor φ_min that mimics RS1 warp compression to the EW scale.

    Setting

        φ_min = φ₀ × (v_EW / M_Planck)

    places the Goldberger-Wise lower bound at a value whose ratio to φ₀
    equals the EW/Planck hierarchy:

        φ_min / φ₀ = v_EW / M_Pl ≈ 2.01 × 10⁻¹⁷

    This corresponds to an effective kπR = ln(φ₀ / φ_min) ≈ 38.44 (see
    gw_effective_kpi_R), identical to the RS1 requirement.

    Parameters
    ----------
    phi0 : float
        GW vacuum expectation value in Planck units (> 0, default 1.0).
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        φ_min in Planck units (> 0, ≪ φ₀).

    Raises
    ------
    ValueError
        If phi0 ≤ 0, higgs_vev_gev ≤ 0, or m_planck_gev ≤ 0.
    """
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0, got {phi0!r}")
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if m_planck_gev <= 0.0:
        raise ValueError(f"m_planck_gev must be > 0, got {m_planck_gev!r}")
    return phi0 * (higgs_vev_gev / m_planck_gev)


def gw_effective_kpi_R(phi_min: float, phi0: float) -> float:
    """Effective kπR for a GW setup with a given radion floor.

        kπR_eff = ln(φ₀ / φ_min)

    When φ_min = gw_phi_min_for_ew_scale(φ₀), this returns RS1_KPI_R_CANONICAL.

    Parameters
    ----------
    phi_min : float
        GW radion floor (> 0).
    phi0 : float
        GW vacuum expectation value (> phi_min).

    Returns
    -------
    float
        Effective kπR ≥ 0.

    Raises
    ------
    ValueError
        If phi_min ≤ 0, phi0 ≤ 0, or phi0 ≤ phi_min.
    """
    if phi_min <= 0.0:
        raise ValueError(f"phi_min must be > 0, got {phi_min!r}")
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0, got {phi0!r}")
    if phi0 <= phi_min:
        raise ValueError(
            f"phi0 ({phi0!r}) must be > phi_min ({phi_min!r})."
        )
    return math.log(phi0 / phi_min)


# ---------------------------------------------------------------------------
# Mechanism 2 — Einstein-Cartan-KK Torsion
# ---------------------------------------------------------------------------

def ec_kk_torsion_mass_sq(
    kappa_T: float,
    n_w: int = N_W_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    m_kk: float = M_KK_PLANCK_CANONICAL,
) -> float:
    """Torsion-induced Higgs mass-squared from EC-KK dimensional reduction.

    In the Einstein-Cartan-KK hybrid, the spin-torsion contact interaction
    generates a negative mass-squared term for the Higgs-like scalar field
    upon dimensional reduction from 5D to 4D:

        μ²_T = κ_T × (n_w / k_cs)² × M_KK²   [Planck²]

    This term drives electroweak symmetry breaking when κ_T > 0.

    Parameters
    ----------
    kappa_T : float
        Torsion-Higgs coupling κ_T ≥ 0.
    n_w : int
        Winding number (default 5).
    k_cs : int
        Chern-Simons level (default 74).
    m_kk : float
        KK mass scale in Planck units (default 1.0).

    Returns
    -------
    float
        μ²_T ≥ 0 in Planck² units.

    Raises
    ------
    ValueError
        If kappa_T < 0, n_w ≤ 0, k_cs ≤ 0, or m_kk ≤ 0.
    """
    if kappa_T < 0.0:
        raise ValueError(f"kappa_T must be ≥ 0, got {kappa_T!r}")
    if n_w <= 0:
        raise ValueError(f"n_w must be > 0, got {n_w!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if m_kk <= 0.0:
        raise ValueError(f"m_kk must be > 0, got {m_kk!r}")
    return kappa_T * (n_w / k_cs) ** 2 * m_kk ** 2


def ec_kk_higgs_vev_planck(
    kappa_T: float,
    n_w: int = N_W_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    m_kk: float = M_KK_PLANCK_CANONICAL,
    lambda_h: float = HIGGS_QUARTIC,
) -> float:
    """Higgs VEV in Planck units from EC-KK torsion-induced EWSB.

    From the Mexican-hat potential minimum:

        v_h² = μ²_T / (2λ_h)
        v_h = M_KK × (n_w / k_cs) × √(κ_T / (2λ_h))

    Parameters
    ----------
    kappa_T : float
        Torsion-Higgs coupling κ_T ≥ 0.
    n_w : int
        Winding number (default 5).
    k_cs : int
        Chern-Simons level (default 74).
    m_kk : float
        KK mass scale [Planck units] (default 1.0).
    lambda_h : float
        Higgs quartic coupling (default m_H²/(2v²) ≈ 0.1293).

    Returns
    -------
    float
        v_h in Planck units (≥ 0).

    Raises
    ------
    ValueError
        If lambda_h ≤ 0 or any other parameter violates positivity.
    """
    if lambda_h <= 0.0:
        raise ValueError(f"lambda_h must be > 0, got {lambda_h!r}")
    mu_sq = ec_kk_torsion_mass_sq(kappa_T, n_w, k_cs, m_kk)
    return math.sqrt(mu_sq / (2.0 * lambda_h))


def ec_kk_higgs_vev_gev(
    kappa_T: float,
    n_w: int = N_W_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    m_kk: float = M_KK_PLANCK_CANONICAL,
    lambda_h: float = HIGGS_QUARTIC,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """Higgs VEV in GeV from EC-KK torsion-induced EWSB.

    Converts ec_kk_higgs_vev_planck to GeV:

        v_h [GeV] = v_h [Planck] × M_Planck [GeV]

    Parameters
    ----------
    kappa_T : float
        Torsion-Higgs coupling κ_T ≥ 0.
    n_w : int
        Winding number (default 5).
    k_cs : int
        Chern-Simons level (default 74).
    m_kk : float
        KK mass scale [Planck units] (default 1.0).
    lambda_h : float
        Higgs quartic coupling (default ≈ 0.1293).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        v_h in GeV (≥ 0).

    Raises
    ------
    ValueError
        If m_planck_gev ≤ 0.
    """
    if m_planck_gev <= 0.0:
        raise ValueError(f"m_planck_gev must be > 0, got {m_planck_gev!r}")
    return ec_kk_higgs_vev_planck(kappa_T, n_w, k_cs, m_kk, lambda_h) * m_planck_gev


def kappa_T_for_ew_scale(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    n_w: int = N_W_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    m_kk: float = M_KK_PLANCK_CANONICAL,
    lambda_h: float = HIGGS_QUARTIC,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """Torsion coupling κ_T needed to reproduce the observed EW scale v_EW.

    Inverting v_h = M_KK × (n_w/k_cs) × √(κ_T / (2λ_h)):

        κ_T = 2λ_h × (v_EW / M_KK)² × (k_cs / n_w)²
            = 2λ_h × (v_EW_planck / m_kk)² × (k_cs / n_w)²

    For M_KK = 1 M_Planck and canonical UM parameters:
        κ_T ≈ 2 × 0.1293 × (2.01 × 10⁻¹⁷)² × (74/5)² ≈ 2.5 × 10⁻³³

    This extreme fine-tuning is the honest measure of how far the torsion
    mechanism is from being a natural solution.

    Parameters
    ----------
    higgs_vev_gev : float
        Observed EW VEV [GeV] (default 246).
    n_w : int
        Winding number (default 5).
    k_cs : int
        Chern-Simons level (default 74).
    m_kk : float
        KK mass scale [Planck units] (default 1.0).
    lambda_h : float
        Higgs quartic coupling (default ≈ 0.1293).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        Required κ_T > 0 (extremely small for Planck-scale M_KK).

    Raises
    ------
    ValueError
        If any parameter violates positivity requirements.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if n_w <= 0:
        raise ValueError(f"n_w must be > 0, got {n_w!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if m_kk <= 0.0:
        raise ValueError(f"m_kk must be > 0, got {m_kk!r}")
    if lambda_h <= 0.0:
        raise ValueError(f"lambda_h must be > 0, got {lambda_h!r}")
    if m_planck_gev <= 0.0:
        raise ValueError(f"m_planck_gev must be > 0, got {m_planck_gev!r}")
    v_planck = higgs_vev_gev / m_planck_gev
    return 2.0 * lambda_h * (v_planck / m_kk) ** 2 * (k_cs / n_w) ** 2


# ---------------------------------------------------------------------------
# Mechanism 3 — AdS₅/CFT₄ Tower Tuned to the EW Scale
# ---------------------------------------------------------------------------

def ads5_ir_compactification_radius(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """IR brane compactification radius R_IR that places KK₁ at the EW scale.

    The first KK mass is m_1 = 1/R in Planck units.  Setting
    m_1 = v_EW / M_Planck gives:

        R_IR = M_Planck / v_EW ≈ 4.97 × 10¹⁶  [Planck units]

    At this radius the entire KK tower has masses starting at the EW scale;
    the RS1 warp factor is then not required to produce the hierarchy
    (the hierarchy is instead encoded in R itself).

    Parameters
    ----------
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        R_IR in Planck units ≫ 1.

    Raises
    ------
    ValueError
        If either argument is non-positive.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if m_planck_gev <= 0.0:
        raise ValueError(f"m_planck_gev must be > 0, got {m_planck_gev!r}")
    return m_planck_gev / higgs_vev_gev


def ads5_krs_rc_for_ew_scale(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """k_rs × r_c product that makes the RS1 warp factor equal v_EW / M_Planck.

    The RS1 warp factor exp(−k_rs × π × r_c) = v_EW / M_Planck gives:

        k_rs × r_c = ln(M_Planck / v_EW) / π ≈ 38.44 / π ≈ 12.23

    For k_rs = 1 (AdS curvature = 1 Planck unit), r_c ≈ 12.23 l_Planck.

    Parameters
    ----------
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        k_rs × r_c ≈ 12.23.

    Raises
    ------
    ValueError
        If either argument is non-positive.
    """
    return rs1_kpi_R_for_ew_scale(higgs_vev_gev, m_planck_gev) / math.pi


def ads5_ew_scale_planck(k_rs: float, r_c: float) -> float:
    """EW / Planck scale ratio from the AdS₅ RS1 warp factor exp(−k_rs π r_c).

        M_EW / M_Planck = exp(−k_rs × π × r_c)

    Equivalent to rs1_warp_factor(k_rs × π × r_c).

    Parameters
    ----------
    k_rs : float
        RS1 AdS curvature parameter (> 0).
    r_c : float
        IR brane position / extra-dimension radius (> 0).

    Returns
    -------
    float
        Dimensionless EW / Planck ratio ∈ (0, 1].

    Raises
    ------
    ValueError
        If k_rs ≤ 0 or r_c ≤ 0.
    """
    if k_rs <= 0.0:
        raise ValueError(f"k_rs must be > 0, got {k_rs!r}")
    if r_c <= 0.0:
        raise ValueError(f"r_c must be > 0, got {r_c!r}")
    return math.exp(-k_rs * math.pi * r_c)


def ads5_r_c_for_ew_scale(
    k_rs: float,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """IR brane position r_c that tunes the AdS₅ warp to the EW scale.

    From exp(−k_rs × π × r_c) = v_EW / M_Pl:

        r_c = ln(M_Pl / v_EW) / (k_rs × π)

    Parameters
    ----------
    k_rs : float
        RS1 AdS curvature parameter (> 0).
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        r_c in Planck units (> 0).

    Raises
    ------
    ValueError
        If k_rs ≤ 0 or either mass parameter is non-positive.
    """
    if k_rs <= 0.0:
        raise ValueError(f"k_rs must be > 0, got {k_rs!r}")
    kpi_R = rs1_kpi_R_for_ew_scale(higgs_vev_gev, m_planck_gev)
    return kpi_R / (k_rs * math.pi)


def ads5_um_tower_weighted_ew_mass(
    k_rs: float,
    r_c: float,
    R: float = ADS_RADIUS_PLANCK,
    k_cs: int = K_CS_CANONICAL,
    n_max: int = N_MAX_TOWER,
) -> float:
    """Braided-tower-weighted effective EW mass from the AdS₅/UM KK spectrum.

    Warp-probability-weighted mean over the tower of warped KK masses:

        p_n = w_n × g_n / Σ_m w_m × g_m
        m_n^phys = (n / R) × g_n
        M_eff = Σ_n p_n × m_n^phys
              = (1/R) × Σ_n n × w_n × g_n² / Σ_n w_n × g_n

    where w_n = exp(−n²/k_cs) (braided spectral weight, Pillar 40) and
    g_n = exp(−k_rs × n × π × r_c) (RS1 warp factor for mode n).

    When kπR = k_rs × π × r_c is large (canonical ≈ 38.44), the n = 1 mode
    dominates completely and M_eff ≈ (1/R) × exp(−kπR), reproducing the RS1
    result.  For smaller kπR, higher modes (n ≥ 2) contribute and the
    braided weights w_n produce a UM-specific deviation from pure RS1.

    Parameters
    ----------
    k_rs : float
        RS1 AdS curvature parameter (> 0).
    r_c : float
        IR brane position [Planck units] (> 0).
    R : float
        Compactification radius for KK masses m_n = n/R (default 1.0).
    k_cs : int
        Braided-winding resonance constant (default 74).
    n_max : int
        KK tower truncation (default 20).

    Returns
    -------
    float
        Tower-weighted effective EW mass in Planck units (> 0).

    Raises
    ------
    ValueError
        If k_rs ≤ 0, r_c ≤ 0, R ≤ 0, k_cs ≤ 0, or n_max < 1.
    """
    if k_rs <= 0.0:
        raise ValueError(f"k_rs must be > 0, got {k_rs!r}")
    if r_c <= 0.0:
        raise ValueError(f"r_c must be > 0, got {r_c!r}")
    if R <= 0.0:
        raise ValueError(f"R must be > 0, got {R!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if n_max < 1:
        raise ValueError(f"n_max must be >= 1, got {n_max!r}")

    numerator = 0.0
    denominator = 0.0
    for n in range(1, n_max + 1):
        w_n = math.exp(-n * n / k_cs)
        g_n = math.exp(-k_rs * n * math.pi * r_c)
        wg = w_n * g_n
        numerator += n * wg * g_n   # n × w_n × g_n²
        denominator += wg           # w_n × g_n
    if denominator == 0.0:
        return 0.0
    return numerator / (R * denominator)


def ads5_braided_warp_suppression(
    k_rs: float,
    r_c: float,
    k_cs: int = K_CS_CANONICAL,
    n_max: int = N_MAX_TOWER,
) -> float:
    """Braided / unbraided RS1 tower-sum ratio: ρ_braid = Σ w_n g_n / Σ g_n.

    Measures how the UM braided spectral weights w_n = exp(−n²/k_cs) modify
    the RS1 KK tower amplitude relative to the unweighted (pure RS1) sum.

    For large kπR (n = 1 dominates both sums):
        ρ_braid ≈ w_1 = exp(−1/k_cs) ≈ 0.987

    For small kπR (many modes contribute):
        ρ_braid < 1 but > exp(−n_max²/k_cs)

    A value ρ_braid ≠ 1 is a UM-specific observable: pure RS1 gives ρ = 1.

    Parameters
    ----------
    k_rs : float
        RS1 AdS curvature parameter (> 0).
    r_c : float
        IR brane position [Planck units] (> 0).
    k_cs : int
        Braided-winding resonance constant (default 74).
    n_max : int
        KK tower truncation (default 20).

    Returns
    -------
    float
        ρ_braid ∈ (0, 1].

    Raises
    ------
    ValueError
        If k_rs ≤ 0, r_c ≤ 0, k_cs ≤ 0, or n_max < 1.
    """
    if k_rs <= 0.0:
        raise ValueError(f"k_rs must be > 0, got {k_rs!r}")
    if r_c <= 0.0:
        raise ValueError(f"r_c must be > 0, got {r_c!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if n_max < 1:
        raise ValueError(f"n_max must be >= 1, got {n_max!r}")

    braided_sum = 0.0
    unbraided_sum = 0.0
    for n in range(1, n_max + 1):
        g_n = math.exp(-k_rs * n * math.pi * r_c)
        w_n = math.exp(-n * n / k_cs)
        braided_sum += w_n * g_n
        unbraided_sum += g_n
    if unbraided_sum == 0.0:
        return 1.0   # degenerate: both sums vanish; ratio is 1 by convention
    return braided_sum / unbraided_sum


def ads5_conformal_dimension_at_ew(
    R_IR: float,
    L: float,
    n: int,
) -> float:
    """Conformal dimension Δ_n at the EW-tuned IR compactification radius.

    From the AdS₅/CFT₄ dictionary (Pillar 40):

        Δ_n = 2 + √(4 + (n × L / R_IR)²)

    At R_IR = M_Planck / v_EW ≈ 4.97 × 10¹⁶ and L = 1 (Planck units):
        (n × L / R_IR)² ≈ n² × (2.01 × 10⁻¹⁷)² ≈ 0

    → Δ_n ≈ 4 for all n, i.e., every KK mode corresponds to a **marginal
    operator** (Δ = 4) in the dual 4D CFT.  This is the falsifiable
    prediction of mechanism 3: at the EW-tuned IR brane, the entire KK
    tower appears as a tower of marginal deformations of the CFT.

    Parameters
    ----------
    R_IR : float
        Compactification radius [Planck units] (> 0).
    L : float
        AdS radius [Planck units] (> 0).
    n : int
        KK mode number (≥ 0).

    Returns
    -------
    float
        Δ_n ≥ 4.

    Raises
    ------
    ValueError
        If R_IR ≤ 0, L ≤ 0, or n < 0.
    """
    if R_IR <= 0.0:
        raise ValueError(f"R_IR must be > 0, got {R_IR!r}")
    if L <= 0.0:
        raise ValueError(f"L must be > 0, got {L!r}")
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n!r}")
    return 2.0 + math.sqrt(4.0 + (n * L / R_IR) ** 2)


# ---------------------------------------------------------------------------
# Comparison dataclass and driver
# ---------------------------------------------------------------------------

@dataclass
class HierarchyComparison:
    """Summary of the UM electroweak hierarchy gap and three candidate mechanisms.

    Produced by :func:`compare_hierarchy_mechanisms`.

    Attributes
    ----------
    um_ew_scale_planck : float
        UM natural EW scale √(c_s/k_cs) ≈ 0.0662 M_Planck.
    observed_ew_scale_planck : float
        Observed v_EW / M_Planck ≈ 2.01 × 10⁻¹⁷.
    hierarchy_gap_log10 : float
        log₁₀[(UM EW scale) / (observed EW scale)] ≈ 15.52.

    rs1_kpi_R_needed : float
        kπR required for RS1 warp to reproduce v_EW ≈ 38.44.
    rs1_warp_factor_canonical : float
        exp(−kπR_needed) = v_EW / M_Planck ≈ 2.01 × 10⁻¹⁷.
    gw_phi_min_for_ew : float
        GW floor φ_min = φ₀ × (v_EW/M_Pl) that mimics RS1 compression.
    gw_phi_min_kpi_R : float
        ln(φ₀/φ_min) — effective kπR of the GW setup (= rs1_kpi_R_needed).

    ec_kappa_T_needed : float
        Torsion coupling κ_T required for v_h = 246 GeV ≈ 2.5 × 10⁻³³.
    ec_kappa_T_log10 : float
        log₁₀(κ_T_needed) — measures severity of torsion fine-tuning.
    ec_higgs_vev_gev_at_kappa1 : float
        Predicted v_h in GeV when κ_T = 1 and M_KK = 1 M_Planck.

    ads5_krs_rc_needed : float
        k_rs × r_c to warp to EW scale ≈ 12.23 (= kπR/π).
    ads5_tower_ew_mass_planck : float
        Braided-tower-weighted EW mass at canonical k_rs=1, r_c=ADS5_KRS_RC.
    ads5_ir_radius_planck : float
        R_IR = M_Pl / v_EW ≈ 4.97 × 10¹⁶.
    ads5_conformal_dim_n1_at_ew : float
        Δ₁ at R = R_IR, L = 1 (≈ 4.0 — marginal operator prediction).
    ads5_braided_suppression_canonical : float
        ρ_braid at canonical kπR ≈ 38.44 (≈ 0.987).

    mechanism1_requires_fine_tuning : bool
        True — kπR (or φ_min) requires manual tuning in mechanism 1.
    mechanism2_requires_fine_tuning : bool
        True — κ_T ≈ 2.5 × 10⁻³³ requires extreme fine-tuning.
    mechanism3_requires_fine_tuning : bool
        True — k_rs × r_c requires tuning in mechanism 3.
    any_mechanism_closed_gap : bool
        False — all three mechanisms provide geometric structure but not a
        natural (fine-tuning-free) derivation of 246 GeV.
    """

    um_ew_scale_planck: float
    observed_ew_scale_planck: float
    hierarchy_gap_log10: float

    rs1_kpi_R_needed: float
    rs1_warp_factor_canonical: float
    gw_phi_min_for_ew: float
    gw_phi_min_kpi_R: float

    ec_kappa_T_needed: float
    ec_kappa_T_log10: float
    ec_higgs_vev_gev_at_kappa1: float

    ads5_krs_rc_needed: float
    ads5_tower_ew_mass_planck: float
    ads5_ir_radius_planck: float
    ads5_conformal_dim_n1_at_ew: float
    ads5_braided_suppression_canonical: float

    mechanism1_requires_fine_tuning: bool
    mechanism2_requires_fine_tuning: bool
    mechanism3_requires_fine_tuning: bool
    any_mechanism_closed_gap: bool


def compare_hierarchy_mechanisms(
    phi0: float = PHI0_CANONICAL,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
    n_w: int = N_W_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    m_kk: float = M_KK_PLANCK_CANONICAL,
    lambda_h: float = HIGGS_QUARTIC,
    k_rs: float = 1.0,
    n_max: int = N_MAX_TOWER,
) -> HierarchyComparison:
    """Return a full comparison of all three EW hierarchy mechanisms.

    Parameters
    ----------
    phi0 : float
        GW vacuum expectation value [Planck units] (default 1.0).
    higgs_vev_gev : float
        Observed Higgs VEV [GeV] (default 246).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).
    n_w : int
        Winding number (default 5).
    k_cs : int
        Chern-Simons level (default 74).
    m_kk : float
        KK mass scale [Planck units] for mechanism 2 (default 1.0).
    lambda_h : float
        Higgs quartic coupling (default ≈ 0.1293).
    k_rs : float
        RS1 AdS curvature for mechanism 3 (default 1.0).
    n_max : int
        KK tower truncation (default 20).

    Returns
    -------
    HierarchyComparison
        Structured result with all mechanism outputs and honest gap summary.
    """
    c_s = C_S_CANONICAL   # module canonical value

    # Gap
    um_scale = um_ew_scale_planck(c_s, k_cs)
    obs_scale = higgs_vev_gev / m_planck_gev
    gap = math.log10(um_scale / obs_scale)

    # Mechanism 1
    kpi_R = rs1_kpi_R_for_ew_scale(higgs_vev_gev, m_planck_gev)
    warp = rs1_warp_factor(kpi_R)
    phi_min_ew = gw_phi_min_for_ew_scale(phi0, higgs_vev_gev, m_planck_gev)
    phi_min_kpi_R = gw_effective_kpi_R(phi_min_ew, phi0)

    # Mechanism 2
    kappa_needed = kappa_T_for_ew_scale(
        higgs_vev_gev, n_w, k_cs, m_kk, lambda_h, m_planck_gev
    )
    kappa_log10 = math.log10(kappa_needed) if kappa_needed > 0.0 else float("-inf")
    vev_at_kappa1 = ec_kk_higgs_vev_gev(1.0, n_w, k_cs, m_kk, lambda_h, m_planck_gev)

    # Mechanism 3
    krs_rc = ads5_krs_rc_for_ew_scale(higgs_vev_gev, m_planck_gev)
    r_c_canon = ads5_r_c_for_ew_scale(k_rs, higgs_vev_gev, m_planck_gev)
    tower_mass = ads5_um_tower_weighted_ew_mass(k_rs, r_c_canon, 1.0, k_cs, n_max)
    R_IR = ads5_ir_compactification_radius(higgs_vev_gev, m_planck_gev)
    delta_n1 = ads5_conformal_dimension_at_ew(R_IR, ADS_RADIUS_PLANCK, 1)
    braid_sup = ads5_braided_warp_suppression(k_rs, r_c_canon, k_cs, n_max)

    return HierarchyComparison(
        um_ew_scale_planck=um_scale,
        observed_ew_scale_planck=obs_scale,
        hierarchy_gap_log10=gap,
        rs1_kpi_R_needed=kpi_R,
        rs1_warp_factor_canonical=warp,
        gw_phi_min_for_ew=phi_min_ew,
        gw_phi_min_kpi_R=phi_min_kpi_R,
        ec_kappa_T_needed=kappa_needed,
        ec_kappa_T_log10=kappa_log10,
        ec_higgs_vev_gev_at_kappa1=vev_at_kappa1,
        ads5_krs_rc_needed=krs_rc,
        ads5_tower_ew_mass_planck=tower_mass,
        ads5_ir_radius_planck=R_IR,
        ads5_conformal_dim_n1_at_ew=delta_n1,
        ads5_braided_suppression_canonical=braid_sup,
        mechanism1_requires_fine_tuning=True,
        mechanism2_requires_fine_tuning=True,
        mechanism3_requires_fine_tuning=True,
        any_mechanism_closed_gap=False,
    )
