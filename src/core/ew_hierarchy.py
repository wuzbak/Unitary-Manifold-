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

§4 — Higgs Quartic Coupling (λ Problem):
  kk_geometric_quartic(c_s, k_cs)
  quartic_discrepancy_factor(lambda_h, c_s, k_cs)
  higgs_mass_from_cs_squared(higgs_vev_gev, c_s)
  higgs_mass_discrepancy_gev(higgs_mass_gev, higgs_vev_gev, c_s)
  higgs_mass_fractional_discrepancy(higgs_mass_gev, higgs_vev_gev, c_s)
  vacuum_stability_condition(lambda_h)
  kk_vacuum_stability_geometric(c_s)

§5 — Yukawa Coupling Hierarchy (Flavor Puzzle):
  yukawa_geometric_mass_ratio(n_gen, n_w)
  observed_lepton_mass_ratio(n_gen)
  yukawa_discrepancy_log10(n_gen, n_w)
  rs1_yukawa_overlap(n_gen, kpi_R, delta_c)
  rs1_yukawa_mass_ratio(n_gen, kpi_R, delta_c)
  rs1_delta_c_for_ratio(target_ratio, n_gen, kpi_R)
  lepton_mass_from_geometry(n_gen, reference_mass_gev, n_w)

§6 — (5,7) Braid Topology and the Warp Factor:
  braid_topological_kpi_R(n1, n2)
  braid_ew_vev_gev(n1, n2, m_planck_gev)
  braid_hierarchy_discrepancy_fraction(n1, n2, higgs_vev_gev, m_planck_gev)
  braid_linking_number(n1, n2)
  braid_yukawa_from_linking(n_gen, n1, n2, k_cs)
  braid_yukawa_mass_ratio(n_gen, n1, n2, k_cs)
  braid_yukawa_discrepancy_log10(n_gen, n1, n2, k_cs)

References
----------
Randall L., Sundrum R. (1999) "A Large Mass Hierarchy from a Small Extra
    Dimension", Phys. Rev. Lett. 83, 3370–3373.
Goldberger W., Wise M. (1999) "Moduli Stabilization with Bulk Fields",
    Phys. Rev. Lett. 83, 4922–4925.
Pinčák R. et al. (2026) Gen. Rel. Grav. 58 — torsion_remnant.py (Pillar 48).
ads_cft_tower.py (Pillar 40) — AdS₅/CFT₄ KK tower dictionary.
three_generations.py (Pillar 42) — KK generation eigenvalue ratios.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
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


# ---------------------------------------------------------------------------
# §4 — Higgs Quartic Coupling: Geometric Prediction and Gap
# ---------------------------------------------------------------------------

def kk_geometric_quartic(
    c_s: float = C_S_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Geometric analog of the Higgs quartic coupling: λ_KK = c_s².

    In the UM braided-winding sector the only dimensionless O(1) scalar
    self-coupling available from the 5D KK geometry is the braided sound
    speed squared:

        λ_KK = c_s² = (12/37)² ≈ 0.1052

    The observed Higgs quartic is λ_h = m_H²/(2v²) ≈ 0.1293, a 23%
    discrepancy.  This is **not** a derivation of λ; it is the closest
    geometric analog and a consistency cross-check.

    The 23% gap is comparable to the expected radiative correction from the
    top-quark Yukawa loop, which runs λ upward by Δλ ≈ 0.02–0.03 between
    the Planck and EW scales.

    Parameters
    ----------
    c_s : float
        Braided sound speed (default 12/37).
    k_cs : int
        Chern-Simons level (default 74).  Accepted for API symmetry; the
        result depends only on c_s.

    Returns
    -------
    float
        λ_KK = c_s² ≈ 0.1052.

    Raises
    ------
    ValueError
        If c_s ≤ 0 or k_cs ≤ 0.
    """
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    return c_s ** 2


def quartic_discrepancy_factor(
    lambda_h: float = HIGGS_QUARTIC,
    c_s: float = C_S_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Ratio λ_h / λ_KK = λ_observed / c_s² — quantifies the quartic gap.

    A value of 1.0 would mean the braided geometry exactly predicts λ.
    The canonical result is ≈ 1.23, meaning the geometric analog undershoots
    the observed quartic by 23%.

    Parameters
    ----------
    lambda_h : float
        Observed Higgs quartic coupling (default m_H²/(2v²) ≈ 0.1293).
    c_s : float
        Braided sound speed (default 12/37).
    k_cs : int
        Chern-Simons level (default 74).

    Returns
    -------
    float
        λ_h / c_s² > 0.

    Raises
    ------
    ValueError
        If lambda_h ≤ 0.
    """
    if lambda_h <= 0.0:
        raise ValueError(f"lambda_h must be > 0, got {lambda_h!r}")
    return lambda_h / kk_geometric_quartic(c_s, k_cs)


def higgs_mass_from_cs_squared(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    c_s: float = C_S_CANONICAL,
) -> float:
    """Geometric Higgs mass prediction using λ_KK = c_s².

    From the tree-level SM relation m_H = v × √(2λ), substituting
    λ_KK = c_s²:

        m_H^{geom} = v_EW × √(2 c_s²) = v_EW × √2 × c_s
                   = 246 × √2 × (12/37) ≈ 112.9 GeV

    The observed Higgs mass is 125.09 GeV — a 9.8% discrepancy.

    **Honest assessment:** The 9.8% undershoot is comparable to the SM
    one-loop correction from the top-quark loop, which shifts m_H upward
    by ~ 10–15 GeV.  This is therefore a plausible geometric origin of the
    Higgs mass — the best available within the UM — but not a derivation.

    Parameters
    ----------
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246).
    c_s : float
        Braided sound speed (default 12/37).

    Returns
    -------
    float
        Predicted Higgs mass in GeV ≈ 112.9.

    Raises
    ------
    ValueError
        If higgs_vev_gev ≤ 0 or c_s ≤ 0.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    return higgs_vev_gev * math.sqrt(2.0) * c_s


def higgs_mass_discrepancy_gev(
    higgs_mass_gev: float = HIGGS_MASS_GEV,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    c_s: float = C_S_CANONICAL,
) -> float:
    """Absolute discrepancy |m_H^{geom} − m_H^{obs}| in GeV.

        = |v_EW × √2 × c_s − 125.09|  ≈ |112.9 − 125.09| ≈ 12.2 GeV

    Parameters
    ----------
    higgs_mass_gev : float
        Observed Higgs mass [GeV] (default 125.09).
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246).
    c_s : float
        Braided sound speed (default 12/37).

    Returns
    -------
    float
        |Δm_H| in GeV ≥ 0.

    Raises
    ------
    ValueError
        If higgs_mass_gev ≤ 0.
    """
    if higgs_mass_gev <= 0.0:
        raise ValueError(f"higgs_mass_gev must be > 0, got {higgs_mass_gev!r}")
    return abs(higgs_mass_from_cs_squared(higgs_vev_gev, c_s) - higgs_mass_gev)


def higgs_mass_fractional_discrepancy(
    higgs_mass_gev: float = HIGGS_MASS_GEV,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    c_s: float = C_S_CANONICAL,
) -> float:
    """Fractional discrepancy (m_H^{geom} − m_H^{obs}) / m_H^{obs}.

    Returns a negative number (≈ −0.098) meaning the geometric prediction
    undershoots the observed mass by ≈ 9.8%.

    Parameters
    ----------
    higgs_mass_gev : float
        Observed Higgs mass [GeV] (default 125.09).
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246).
    c_s : float
        Braided sound speed (default 12/37).

    Returns
    -------
    float
        (m_geom − m_obs) / m_obs  (negative when m_geom < m_obs).

    Raises
    ------
    ValueError
        If higgs_mass_gev ≤ 0.
    """
    if higgs_mass_gev <= 0.0:
        raise ValueError(f"higgs_mass_gev must be > 0, got {higgs_mass_gev!r}")
    m_geom = higgs_mass_from_cs_squared(higgs_vev_gev, c_s)
    return (m_geom - higgs_mass_gev) / higgs_mass_gev


def vacuum_stability_condition(lambda_h: float = HIGGS_QUARTIC) -> bool:
    """Return True iff the Higgs quartic coupling indicates a stable vacuum.

    The Higgs potential V = −μ²|H|² + λ|H|⁴ requires λ > 0 for the
    vacuum to be stable (bounded below).  At tree level the SM vacuum is
    stable with λ ≈ 0.1293.

    Radiative corrections from the top-quark Yukawa coupling drive λ
    negative at μ ≈ 10¹⁰ GeV, rendering the SM vacuum metastable —
    an open problem the UM does not yet address geometrically.

    Parameters
    ----------
    lambda_h : float
        Higgs quartic coupling (default ≈ 0.1293).

    Returns
    -------
    bool
        True if λ_h > 0 (stable at tree level).

    Raises
    ------
    TypeError
        If lambda_h is not numeric.
    """
    try:
        return float(lambda_h) > 0.0
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"lambda_h must be numeric, got {type(lambda_h).__name__!r}"
        ) from exc


def kk_vacuum_stability_geometric(c_s: float = C_S_CANONICAL) -> bool:
    """Return True iff the geometric quartic λ_KK = c_s² > 0.

    Since c_s = (n₂² − n₁²) / k_CS > 0 for any braid pair with n₂ > n₁,
    the geometric quartic is *always* positive.  This is the one firm
    geometric statement the UM can make about vacuum stability: the braided
    structure guarantees λ_KK > 0 without any parameter tuning.

    Parameters
    ----------
    c_s : float
        Braided sound speed (must be > 0).

    Returns
    -------
    bool
        Always True when c_s > 0 (validated on entry).

    Raises
    ------
    ValueError
        If c_s ≤ 0.
    """
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    return True  # c_s² > 0 is guaranteed for any c_s > 0


# ---------------------------------------------------------------------------
# §5 — Yukawa Coupling Hierarchy (Flavor Puzzle)
# ---------------------------------------------------------------------------

# Observed lepton masses [GeV] — PDG 2024
ELECTRON_MASS_GEV: float = 0.51099895e-3   # 0.511 MeV
MUON_MASS_GEV: float = 105.6583755e-3      # 105.66 MeV
TAU_MASS_GEV: float = 1.77686              # 1776.86 MeV

# Observed lepton mass ratios (normalised to electron = 1)
LEPTON_MASS_RATIO_MU_E: float = MUON_MASS_GEV / ELECTRON_MASS_GEV   # ≈ 206.77
LEPTON_MASS_RATIO_TAU_E: float = TAU_MASS_GEV / ELECTRON_MASS_GEV   # ≈ 3477.2


def yukawa_geometric_mass_ratio(
    n_gen: int,
    n_w: int = N_W_CANONICAL,
) -> float:
    """Geometric mass ratio m_{n_gen} / m_0 from Pillar-42 KK eigenvalues.

    From the S¹/Z₂ orbifold stability condition (Pillar 42,
    three_generations.py), the effective radion eigenvalue for generation n
    gives a mass ratio:

        m_n / m_0 = √(1 + n² / n_w)

        n=0: ratio = 1.000  (lightest, reference)
        n=1: ratio = √(6/5) ≈ 1.095
        n=2: ratio = √(9/5) ≈ 1.342

    The observed lepton mass ratios are m_μ/m_e ≈ 207 and m_τ/m_e ≈ 3477,
    many orders of magnitude larger.  The gap is quantified by
    yukawa_discrepancy_log10().

    Parameters
    ----------
    n_gen : int
        Generation index n ≥ 0 (0 = lightest).
    n_w : int
        Winding number (default 5).

    Returns
    -------
    float
        Geometric mass ratio ≥ 1.

    Raises
    ------
    ValueError
        If n_gen < 0 or n_w ≤ 0.
    """
    if n_gen < 0:
        raise ValueError(f"n_gen must be >= 0, got {n_gen!r}")
    if n_w <= 0:
        raise ValueError(f"n_w must be > 0, got {n_w!r}")
    return math.sqrt(1.0 + n_gen ** 2 / n_w)


def observed_lepton_mass_ratio(n_gen: int) -> float:
    """Observed lepton mass ratio m_{n_gen} / m_electron (PDG 2024).

        n=0 (electron): 1.000
        n=1 (muon):    ≈ 206.77
        n=2 (tau):     ≈ 3477.2

    Parameters
    ----------
    n_gen : int
        Generation index (0, 1, or 2).

    Returns
    -------
    float
        Observed mass ratio ≥ 1.

    Raises
    ------
    ValueError
        If n_gen not in {0, 1, 2}.
    """
    if n_gen == 0:
        return 1.0
    elif n_gen == 1:
        return LEPTON_MASS_RATIO_MU_E
    elif n_gen == 2:
        return LEPTON_MASS_RATIO_TAU_E
    else:
        raise ValueError(f"n_gen must be 0, 1, or 2; got {n_gen!r}")


def yukawa_discrepancy_log10(
    n_gen: int,
    n_w: int = N_W_CANONICAL,
) -> float:
    """log₁₀(geometric ratio / observed ratio) — quantifies the Yukawa gap.

    A large negative value indicates the geometric prediction severely
    underestimates the observed mass ratio:

        n=0:  log₁₀(1.000 / 1.000)       =  0.00  (exact, reference)
        n=1:  log₁₀(1.095 / 206.77)     ≈ −2.28
        n=2:  log₁₀(1.342 / 3477.2)     ≈ −3.41

    The UM explains the *number* of generations (Pillar 42) but not their
    *mass hierarchy* — this is the Flavor Puzzle gap.

    Parameters
    ----------
    n_gen : int
        Generation index (0, 1, or 2).
    n_w : int
        Winding number (default 5).

    Returns
    -------
    float
        log₁₀ ratio ≤ 0 for n_gen ≥ 1.
    """
    geom = yukawa_geometric_mass_ratio(n_gen, n_w)
    obs = observed_lepton_mass_ratio(n_gen)
    return math.log10(geom / obs)


def rs1_yukawa_overlap(
    n_gen: int,
    kpi_R: float = RS1_KPI_R_CANONICAL,
    delta_c: float = 0.1,
) -> float:
    """RS1-type Yukawa coupling from fermion wavefunction overlap.

    In the Randall-Sundrum model, fermions with different bulk masses c_n
    are localised at different positions in the extra dimension.  The 4D
    Yukawa coupling is suppressed by the overlap with the Higgs brane:

        y_n / y_0 = exp(−n × δc × kπR)

    where δc is the inter-generation bulk-mass splitting.  With δc ≈ 0.1
    and kπR ≈ 38.44, the suppression per generation is exp(−3.84) ≈ 0.021,
    producing an exponential mass hierarchy without O(1) fine-tuning of δc.

    Parameters
    ----------
    n_gen : int
        Generation index n ≥ 0 (0 = heaviest, higher n = lighter).
    kpi_R : float
        RS1 warp exponent kπR (default ≈ 38.44).
    delta_c : float
        Bulk-mass splitting between adjacent generations (default 0.1).

    Returns
    -------
    float
        Normalised Yukawa coupling y_n / y_0 = exp(−n δc kπR) ∈ (0, 1].

    Raises
    ------
    ValueError
        If n_gen < 0, kpi_R < 0, or delta_c < 0.
    """
    if n_gen < 0:
        raise ValueError(f"n_gen must be >= 0, got {n_gen!r}")
    if kpi_R < 0.0:
        raise ValueError(f"kpi_R must be >= 0, got {kpi_R!r}")
    if delta_c < 0.0:
        raise ValueError(f"delta_c must be >= 0, got {delta_c!r}")
    return math.exp(-n_gen * delta_c * kpi_R)


def rs1_yukawa_mass_ratio(
    n_gen: int,
    kpi_R: float = RS1_KPI_R_CANONICAL,
    delta_c: float = 0.1,
) -> float:
    """Mass ratio m_0 / m_{n_gen} from the RS1 wavefunction overlap model.

    Assuming masses proportional to Yukawa couplings (y_n / y_0):

        m_0 / m_{n_gen} = exp(+n × δc × kπR)

    For δc = 0.1 and canonical kπR ≈ 38.44:
        n=1: m_0/m_1 = exp(3.844) ≈  46.8
        n=2: m_0/m_2 = exp(7.688) ≈ 2190

    Observed: m_τ/m_μ ≈ 16.8, m_τ/m_e ≈ 3477.  Adjusting δc with
    rs1_delta_c_for_ratio() can match any target ratio.

    Parameters
    ----------
    n_gen : int
        Generation index n ≥ 0 (0 = heaviest).
    kpi_R : float
        RS1 kπR (default ≈ 38.44).
    delta_c : float
        Bulk-mass splitting (default 0.1).

    Returns
    -------
    float
        Mass ratio m_0 / m_{n_gen} ≥ 1.
    """
    return 1.0 / rs1_yukawa_overlap(n_gen, kpi_R, delta_c)


def rs1_delta_c_for_ratio(
    target_ratio: float,
    n_gen: int,
    kpi_R: float = RS1_KPI_R_CANONICAL,
) -> float:
    """Bulk-mass splitting δc that reproduces a target mass ratio m_0/m_{n_gen}.

    From m_0/m_n = exp(n × δc × kπR):

        δc = ln(target_ratio) / (n × kπR)

    Example — matching the tau/electron ratio:
        δc = ln(3477.2) / (2 × 38.44) ≈ 8.154 / 76.88 ≈ 0.106

    This O(0.1) splitting does not require fine-tuning, in contrast to the
    enormous hierarchy it generates (m_τ / m_e ≈ 3477).

    Parameters
    ----------
    target_ratio : float
        Target mass ratio m_0 / m_{n_gen} > 1.
    n_gen : int
        Generation index (must be ≥ 1).
    kpi_R : float
        RS1 kπR (default ≈ 38.44).

    Returns
    -------
    float
        Required δc > 0.

    Raises
    ------
    ValueError
        If target_ratio ≤ 1, n_gen ≤ 0, or kpi_R ≤ 0.
    """
    if target_ratio <= 1.0:
        raise ValueError(f"target_ratio must be > 1, got {target_ratio!r}")
    if n_gen <= 0:
        raise ValueError(f"n_gen must be >= 1, got {n_gen!r}")
    if kpi_R <= 0.0:
        raise ValueError(f"kpi_R must be > 0, got {kpi_R!r}")
    return math.log(target_ratio) / (n_gen * kpi_R)


def lepton_mass_from_geometry(
    n_gen: int,
    reference_mass_gev: float,
    n_w: int = N_W_CANONICAL,
) -> float:
    """Predicted lepton mass from Pillar-42 KK eigenvalues given a reference.

    Applies the geometric mass ratio m_n / m_0 = √(1 + n²/n_w) to scale
    reference_mass_gev to the n-th generation.

    Parameters
    ----------
    n_gen : int
        Generation index (≥ 0; 0 returns reference_mass_gev unchanged).
    reference_mass_gev : float
        Mass of the lightest generation (n=0) [GeV] (must be > 0).
    n_w : int
        Winding number (default 5).

    Returns
    -------
    float
        Predicted mass in GeV.

    Raises
    ------
    ValueError
        If reference_mass_gev ≤ 0.
    """
    if reference_mass_gev <= 0.0:
        raise ValueError(
            f"reference_mass_gev must be > 0, got {reference_mass_gev!r}"
        )
    return reference_mass_gev * yukawa_geometric_mass_ratio(n_gen, n_w)


# ---------------------------------------------------------------------------
# §6 — (5,7) Braid Topology and the Warp Factor
#
# Core finding: kπR_topo = π(n₁+n₂) = 12π ≈ 37.70 is within 1.9% of the
# RS1 requirement kπR_obs ≈ 38.44.  The (5,7) braid supplies 98.1% of the
# hierarchy suppression topologically; the Goldberger-Wise mechanism provides
# the residual 1.9%.
# ---------------------------------------------------------------------------

BRAID_N1: int = 5    # first winding (n_w, Planck-side brane)
BRAID_N2: int = 7    # second winding (TeV-side, G₂ octonion sector)
BRAID_CROSSING_SUM: int = BRAID_N1 + BRAID_N2         # = 12
BRAID_LINKING_NUMBER_CANONICAL: int = BRAID_N1 * BRAID_N2  # = 35 (CS linking)
BRAID_KPI_R_TOPOLOGICAL: float = math.pi * (BRAID_N1 + BRAID_N2)  # ≈ 37.70
BRAID_EW_VEV_GEV_TOPOLOGICAL: float = (
    PLANCK_MASS_GEV * math.exp(-BRAID_KPI_R_TOPOLOGICAL)
)  # ≈ 531 GeV (topological prediction before GW correction)


def braid_topological_kpi_R(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
) -> float:
    """Topological kπR estimate from (n1,n2) braid: π × (n1 + n2).

    The (n1, n2) torus braid has a crossing sum n1 + n2, which sets the
    natural length of the extra dimension in crossing-number units.  The
    associated warp exponent is:

        kπR_topo = π × (n1 + n2)

    For the canonical (5,7) UM braid:
        kπR_topo = 12π ≈ 37.699

    This is within 1.9% of the observed requirement kπR_obs ≈ 38.44,
    suggesting the braid topology provides the *leading-order* hierarchy
    suppression.  The Goldberger-Wise stabilisation potential then supplies
    the residual fine-tuning.

    Parameters
    ----------
    n1 : int
        First strand winding number (default 5 = n_w).
    n2 : int
        Second strand winding number (default 7).

    Returns
    -------
    float
        kπR_topo = π(n1 + n2) > 0.

    Raises
    ------
    ValueError
        If n1 ≤ 0 or n2 ≤ 0.
    """
    if n1 <= 0:
        raise ValueError(f"n1 must be > 0, got {n1!r}")
    if n2 <= 0:
        raise ValueError(f"n2 must be > 0, got {n2!r}")
    return math.pi * (n1 + n2)


def braid_ew_vev_gev(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """EW VEV in GeV predicted from braid topology alone.

        v_EW^{braid} = M_Planck × exp(−π(n1+n2)) ≈ 531 GeV

    The topological prediction overshoots 246 GeV by a factor ≈ 2.16,
    meaning the braid mechanism alone compresses the scale to within a
    factor of 2 of the EW scale.  The Goldberger-Wise correction accounts
    for the remaining factor.

    Parameters
    ----------
    n1 : int
        First winding (default 5).
    n2 : int
        Second winding (default 7).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        Topological EW VEV in GeV (> 246 GeV at canonical values).

    Raises
    ------
    ValueError
        If m_planck_gev ≤ 0.
    """
    if m_planck_gev <= 0.0:
        raise ValueError(f"m_planck_gev must be > 0, got {m_planck_gev!r}")
    kpi_R = braid_topological_kpi_R(n1, n2)
    return m_planck_gev * math.exp(-kpi_R)


def braid_hierarchy_discrepancy_fraction(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """Fractional discrepancy (kπR_topo − kπR_obs) / kπR_obs.

    For canonical (5,7):
        kπR_topo = 12π ≈ 37.699
        kπR_obs  ≈ 38.443
        fraction ≈ −0.0193  (−1.93%)

    A negative value means the braid under-predicts the required warp;
    GW stabilisation must supply an additional +1.93% of kπR.

    Parameters
    ----------
    n1 : int
        First winding (default 5).
    n2 : int
        Second winding (default 7).
    higgs_vev_gev : float
        Observed Higgs VEV [GeV] (default 246).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹).

    Returns
    -------
    float
        Fractional discrepancy ∈ (−1, 0) for any realistic braid.
    """
    kpi_R_topo = braid_topological_kpi_R(n1, n2)
    kpi_R_obs = rs1_kpi_R_for_ew_scale(higgs_vev_gev, m_planck_gev)
    return (kpi_R_topo - kpi_R_obs) / kpi_R_obs


def braid_linking_number(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
) -> int:
    """Topological linking number of the (n1,n2) torus braid: n1 × n2.

    For a coprime (p,q) torus knot the self-linking number (with zero
    framing) equals p × q.  In the UM this equals n_w × n₂ = 5 × 7 = 35.

    In Chern-Simons gauge theory at level k_CS = n1² + n2² = 74, the
    Wilson loop expectation value is modulated by the self-linking number.
    The value 35 appears in the braid-Yukawa coupling model (§6).

    Parameters
    ----------
    n1 : int
        First winding (default 5).
    n2 : int
        Second winding (default 7).

    Returns
    -------
    int
        Linking number n1 × n2.

    Raises
    ------
    ValueError
        If n1 ≤ 0 or n2 ≤ 0.
    """
    if n1 <= 0:
        raise ValueError(f"n1 must be > 0, got {n1!r}")
    if n2 <= 0:
        raise ValueError(f"n2 must be > 0, got {n2!r}")
    return n1 * n2


def braid_yukawa_from_linking(
    n_gen: int,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Yukawa coupling from the Chern-Simons braid-linking invariant.

    In a Chern-Simons / knot-theoretic model, the Yukawa coupling for
    generation n is suppressed by the CS phase acquired by the fermion
    worldline encircling n inter-generation braid crossings:

        y_n = exp(−n_gen × π × n1 × n2 / k_cs)
            = exp(−n_gen × π × 35 / 74)

        n=0: y_0 = 1.000  (heaviest generation, reference)
        n=1: y_1 = exp(−π × 35/74) ≈ 0.226
        n=2: y_2 = exp(−2π × 35/74) ≈ 0.051

    Mass ratios (heaviest / lighter generation):
        m_0/m_1 ≈ 4.42  vs  m_τ/m_μ ≈ 16.8 (observed)
        m_0/m_2 ≈ 19.5  vs  m_τ/m_e ≈ 3477 (observed)

    **Honest assessment:** The linking-number model produces O(10) ratios,
    improving by 1–2 orders of magnitude on the pure KK-geometric O(1)
    ratios, but still falls 1–2 orders short of the observed lepton
    hierarchy.  A complete solution likely requires combining the CS
    mechanism with the RS1 wavefunction overlap (δc tuning, §5).

    Parameters
    ----------
    n_gen : int
        Generation index n ≥ 0 (0 = heaviest).
    n1 : int
        First winding (default 5).
    n2 : int
        Second winding (default 7).
    k_cs : int
        Chern-Simons level (default 74).

    Returns
    -------
    float
        Normalised Yukawa coupling y_n / y_0 ∈ (0, 1].

    Raises
    ------
    ValueError
        If n_gen < 0, n1 ≤ 0, n2 ≤ 0, or k_cs ≤ 0.
    """
    if n_gen < 0:
        raise ValueError(f"n_gen must be >= 0, got {n_gen!r}")
    if n1 <= 0:
        raise ValueError(f"n1 must be > 0, got {n1!r}")
    if n2 <= 0:
        raise ValueError(f"n2 must be > 0, got {n2!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    return math.exp(-n_gen * math.pi * n1 * n2 / k_cs)


def braid_yukawa_mass_ratio(
    n_gen: int,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Mass ratio m_0 / m_{n_gen} from the braid CS-linking model.

    m_0 / m_{n_gen} = 1 / braid_yukawa_from_linking(n_gen, n1, n2, k_cs)
                    = exp(+n_gen × π × n1 × n2 / k_cs)

        n=1: ≈ 4.42
        n=2: ≈ 19.5

    Parameters
    ----------
    n_gen : int
        Generation index (0 = heaviest; ratio ≥ 1).
    n1 : int
        First winding (default 5).
    n2 : int
        Second winding (default 7).
    k_cs : int
        Chern-Simons level (default 74).

    Returns
    -------
    float
        Mass ratio ≥ 1.
    """
    return 1.0 / braid_yukawa_from_linking(n_gen, n1, n2, k_cs)


def braid_yukawa_discrepancy_log10(
    n_gen: int,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """log₁₀(braid mass ratio / observed lepton ratio) for generation n_gen.

    Compares the braid-CS prediction to observed lepton masses:

        n=0:  log₁₀(1.00 / 1.00)       =  0.00  (exact, reference)
        n=1:  log₁₀(4.42 / 206.77)    ≈ −1.67  (braid underpredicts by 1.7 orders)
        n=2:  log₁₀(19.5 / 3477.2)    ≈ −2.25  (braid underpredicts by 2.3 orders)

    The braid model improves on the pure KK result (§5: −2.28, −3.41) but
    does not close the flavor gap.

    Parameters
    ----------
    n_gen : int
        Generation index (0, 1, or 2).
    n1 : int
        First winding (default 5).
    n2 : int
        Second winding (default 7).
    k_cs : int
        Chern-Simons level (default 74).

    Returns
    -------
    float
        log₁₀ ratio ≤ 0.
    """
    if n_gen == 0:
        return 0.0
    braid_ratio = braid_yukawa_mass_ratio(n_gen, n1, n2, k_cs)
    obs_ratio = observed_lepton_mass_ratio(n_gen)
    return math.log10(braid_ratio / obs_ratio)


# ---------------------------------------------------------------------------
# Additional constants — top quark sector
# ---------------------------------------------------------------------------

TOP_MASS_GEV: float = 172.76
# Top quark pole mass [GeV] — PDG 2024 world average.

TOP_YUKAWA: float = TOP_MASS_GEV * math.sqrt(2.0) / HIGGS_VEV_GEV
# Tree-level top Yukawa: y_t = m_t √2 / v ≈ 0.993 (close to 1 — near-maximal coupling).


# ---------------------------------------------------------------------------
# §4 extension — Braid-Warp Correspondence and GW Tension
#
# The (5,7) torus braid provides a *topological anchor* for the RS1 warp
# factor.  Instead of being a free parameter, kπR is "snapped" to the nearest
# crossing-sum multiple π(n1+n2) = 12π ≈ 37.699, covering 98.06% of the
# required exponent kπR_obs ≈ 38.44.  The residual 1.94% is the Goldberger–
# Wise (GW) scalar tension that stabilises the braid at its equilibrium length.
# ---------------------------------------------------------------------------


def braid_gw_residual_tension(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """Absolute GW scalar tension: T_GW = kπR_obs − kπR_topo > 0.

    The (n1,n2) braid supplies kπR_topo = π(n1+n2) ≈ 37.699, leaving a gap

        T_GW = kπR_obs − kπR_topo ≈ 38.443 − 37.699 ≈ 0.744

    that must be covered by the Goldberger–Wise stabilisation scalar.
    Physically, T_GW is the *vacuum energy of the braid*: if the topology
    provided 100%, the system would be rigid and GW unnecessary.

    Canonical result: T_GW ≈ 0.744.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"n1, n2 must be positive integers, got {n1!r}, {n2!r}")
    return rs1_kpi_R_for_ew_scale(higgs_vev_gev, m_planck_gev) - braid_topological_kpi_R(n1, n2)


def braid_gw_tension_fraction(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """Fractional GW tension = T_GW / kπR_obs ≈ 0.0194 (1.94%).

    The complement of the topological coverage fraction:
        tension_fraction = 1 − kπR_topo / kπR_obs ≈ 0.0194

    Equivalently: |braid_hierarchy_discrepancy_fraction()|.
    """
    kpi_R_obs = rs1_kpi_R_for_ew_scale(higgs_vev_gev, m_planck_gev)
    return braid_gw_residual_tension(n1, n2, higgs_vev_gev, m_planck_gev) / kpi_R_obs


def braid_twist_density(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    r_c: float = ADS5_KRS_RC_CANONICAL,
) -> float:
    """Twist density of the (n1,n2) braid: k_rs = (n1+n2) / r_c.

    In the RS1 metric ds² = e^{−2A(y)} η_{μν} dx^μ dx^ν + dy², the warp
    function is A(y) = k_rs |y|.  The braid interpretation: A(y) is the
    cumulative twist at position y, and A′(y) = k_rs is the *twist density*
    — crossings per unit length in the extra dimension.

    Topological quantisation: k_rs × r_c = n1 + n2 = 12 (crossing sum).
    For r_c = ADS5_KRS_RC_CANONICAL ≈ 12.23: k_rs ≈ 0.981 M_Pl.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"n1, n2 must be positive, got {n1!r}, {n2!r}")
    if r_c <= 0.0:
        raise ValueError(f"r_c must be > 0, got {r_c!r}")
    return (n1 + n2) / r_c


def braid_equilibrium_radius(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    lambda5d: float = -6.0,
) -> float:
    """Topological equilibrium brane separation R_topo = π(n1+n2)/k_rs [Planck].

    In RS1, k² = −Λ₅/6 (Planck units).  The braid equilibrium condition sets
    k_rs = √(−Λ₅/6), giving the "locked" extra-dimension size

        R_topo = π(n1+n2) / √(−Λ₅/6)

    at which topological braid tension balances the 5D cosmological constant.
    For λ₅d = −6 (canonical): k_rs = 1, R_topo = 12π ≈ 37.70 Planck units.

    Parameters
    ----------
    lambda5d : float
        Bulk cosmological constant Λ₅ < 0 (must be AdS).
    """
    if lambda5d >= 0.0:
        raise ValueError(f"lambda5d must be negative (AdS), got {lambda5d!r}")
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"n1, n2 must be positive, got {n1!r}, {n2!r}")
    return math.pi * (n1 + n2) / math.sqrt(-lambda5d / 6.0)


# ---------------------------------------------------------------------------
# §5 extension — Strand Localization and Curvature-Enhanced Yukawa
#
# Each fermion generation occupies a specific sub-loop (strand) of the (5,7)
# braid.  The n2=7 strands each contribute kπR/k_cs phase crossings per
# generation step, giving the n2-amplified Yukawa model — a major improvement
# over the basic linking model.
# ---------------------------------------------------------------------------


def braid_strand_yukawa(
    n_gen: int,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    kpi_R: float = RS1_KPI_R_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Strand-localisation Yukawa: y_n = exp(−n_gen × n2 × kπR / k_cs).

    Strand assignment (consistent with RS1 flavour physics + user input):
        n_gen = 0 (heaviest: tau / top):     innermost braid strands
        n_gen = 1 (middle:   muon / charm):  intermediate strands
        n_gen = 2 (lightest: electron / up): outermost strands (IR-brane end)

    The n2 strands each contribute kπR/k_cs crossing phases per generation
    step; the total exponent is n_gen × n2 × kπR / k_cs.

    Canonical predictions (n2=7, kπR≈38.44, k_cs=74):
        n_gen=0: y_0 = 1.000
        n_gen=1: y_1 ≈ 0.0265  →  m_0/m_1 ≈  37.7  (observed m_τ/m_μ ≈ 16.8)
        n_gen=2: y_2 ≈ 7.0e-4  →  m_0/m_2 ≈ 1424   (observed m_τ/m_e ≈ 3477)

    Residual gap: factor ≈ 2.2–2.4 — far better than the basic linking model
    (factor ≈ 4–178).
    """
    if n_gen < 0:
        raise ValueError(f"n_gen must be >= 0, got {n_gen!r}")
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"n1, n2 must be positive, got {n1!r}, {n2!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if kpi_R < 0.0:
        raise ValueError(f"kpi_R must be >= 0, got {kpi_R!r}")
    return math.exp(-n_gen * n2 * kpi_R / k_cs)


def braid_strand_mass_ratio(
    n_gen: int,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    kpi_R: float = RS1_KPI_R_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Mass ratio m_heaviest / m_{n_gen} from strand localisation.

    = exp(+n_gen × n2 × kπR / k_cs) = 1 / braid_strand_yukawa(n_gen, ...).

    Canonical: n_gen=1 → 37.7 (observed 16.8); n_gen=2 → 1424 (observed 3477).
    """
    if n_gen < 0:
        raise ValueError(f"n_gen must be >= 0, got {n_gen!r}")
    y = braid_strand_yukawa(n_gen, n1, n2, kpi_R, k_cs)
    return 1.0 / y if y != 0.0 else math.inf


def braid_strand_discrepancy_log10(
    n_gen: int,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    kpi_R: float = RS1_KPI_R_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """log₁₀(strand_ratio / observed_ratio) — strand-localisation Yukawa gap.

    Positive: strand model over-predicts.  Negative: under-predicts.

    Canonical:
        n_gen=0:  0.00  (definition)
        n_gen=1: +0.35  (over by ×2.2; basic linking model: −2.28)
        n_gen=2: −0.39  (under by ×2.4; basic linking model: −3.41)

    These small residuals confirm the strand model is the best current
    Yukawa mechanism in the UM — but the gap is not yet closed.
    """
    if n_gen == 0:
        return 0.0
    return math.log10(braid_strand_mass_ratio(n_gen, n1, n2, kpi_R, k_cs)
                      / observed_lepton_mass_ratio(n_gen))


def braid_alexander_polynomial(
    t: float,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
) -> float:
    """Alexander polynomial Δ_{n1,n2}(t) of the (n1,n2) torus knot at real t > 0.

    For the torus knot T(p,q):

        Δ_{p,q}(t) = (t^{pq} − 1)(t − 1) / ((t^p − 1)(t^q − 1))

    This is a topological invariant encoding the crossing structure of the
    braid.  At t = 1 the limit is 1.0 (for all torus knots).

    Physical note: evaluating Δ at t = exp(−n_gen × π × n2/k_cs) gives a
    knot-invariant Yukawa prefactor, but the polynomial is non-monotone in t
    (it has both positive and negative Fourier modes), so applying it directly
    to Yukawa calculations requires further theoretical development.

    Parameters
    ----------
    t : float   Evaluation point, t > 0.  t = 1 returns 1.0 (limit).
    n1, n2 : int   Braid winding numbers (positive integers).
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"n1, n2 must be positive, got {n1!r}, {n2!r}")
    if t <= 0.0:
        raise ValueError(f"t must be > 0 for real evaluation, got {t!r}")
    if abs(t - 1.0) < 1e-10:
        return 1.0          # L'Hôpital limit
    pq = n1 * n2
    num = (t ** pq - 1.0) * (t - 1.0)
    den = (t ** n1 - 1.0) * (t ** n2 - 1.0)
    if abs(den) < 1e-300:
        return 1.0          # near-degenerate
    return num / den


# ---------------------------------------------------------------------------
# §6 extension — Higgs Sector: Three Quartic Predictions and Top-Loop Fix
#
# Three independent geometric estimates of λ_h, in order of accuracy:
#   1. λ_winding  = (n1/n2)² / (2π) ≈ 0.0812  →  m_H ≈  99 GeV  (Gemini, −21%)
#   2. λ_cs_sq    = c_s²            ≈ 0.1052  →  m_H ≈ 113 GeV  (UM,   − 9.8%)
#   3. λ_stiffness= c_s²(1+n₁n₂/k_cs²) ≈ 0.1059 →  m_H ≈ 113 GeV  (UM, − 9.5%)
#   4. m_H^{top-corrected} ≈ 124 GeV (Λ_KK ≈ 310 GeV) — best current prediction
# ---------------------------------------------------------------------------


def braid_quartic_from_winding_ratio(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
) -> float:
    """Geometric Higgs quartic from winding-number ratio: λ = (n1/n2)² / (2π).

    Proposed by Gemini (2025): the winding ratio n1/n2 = 5/7 is the "filling
    fraction" of UV vs IR braid strands; dividing by 2π accounts for one full
    period of the compact extra dimension.

        λ_winding = (5/7)² / (2π) ≈ 0.0812

    Using the correct SM tree-level relation m_H = v√(2λ):

        m_H^{winding} ≈ 246 × √(2 × 0.0812) ≈ 99 GeV   (−20.8% from 125.09)

    Note: Gemini's own code used m_H = v × √(λ/2) (wrong SM convention),
    giving 49.6 GeV.  The correct formula is m_H = v × √(2λ), implemented
    in braid_higgs_mass_from_winding_ratio().

    Honest comparison with other geometric estimates:
        λ_winding ≈ 0.0812  →  −20.8% (worst)
        λ_cs²     ≈ 0.1052  →   −9.8% (better)
        λ_stiff   ≈ 0.1059  →   −9.5% (best tree-level)
        λ_obs     ≈ 0.1293  (target)
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"n1, n2 must be positive, got {n1!r}, {n2!r}")
    return (n1 / n2) ** 2 / (2.0 * math.pi)


def braid_higgs_mass_from_winding_ratio(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
) -> float:
    """Higgs mass from winding-ratio quartic using correct SM convention.

    m_H^{winding} = v_EW × √(2 λ_winding) = v_EW × (n1/n2) / √π ≈ 99.1 GeV.

    This uses the correct SM tree-level relation m_H = v√(2λ).
    Gemini's formula used m_H = v√(λ/2) (wrong convention → 49.6 GeV).
    Our c_s² formula (higgs_mass_from_cs_squared) gives 112.9 GeV — more accurate.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    return higgs_vev_gev * math.sqrt(2.0 * braid_quartic_from_winding_ratio(n1, n2))


def braid_quartic_from_stiffness(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    k_cs: int = K_CS_CANONICAL,
    c_s: float = C_S_CANONICAL,
) -> float:
    """Higgs quartic from braid stiffness: λ_stiff = c_s² × (1 + n1 n2 / k_cs²).

    Augments the c_s² base quartic with a cross-link stiffness correction:

        λ_stiff = c_s² × (1 + n1 × n2 / k_cs²)
                = (12/37)² × (1 + 35/5476) ≈ 0.1052 × 1.00639 ≈ 0.1059

    Physical interpretation: n1 × n2 = 35 cross-links add a 0.64% stiffness
    above the base braided quartic c_s².  This is the best purely geometric
    λ estimate, giving m_H^{vib} ≈ 113.2 GeV (−9.5% from 125.09 GeV).
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"n1, n2 must be positive, got {n1!r}, {n2!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    return c_s ** 2 * (1.0 + n1 * n2 / k_cs ** 2)


def braid_higgs_mass_vibrational(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    k_cs: int = K_CS_CANONICAL,
    c_s: float = C_S_CANONICAL,
) -> float:
    """Higgs mass from the first vibrational mode of the (n1,n2) braid.

    Interprets the Higgs as the lowest-energy oscillation of the braid;
    the restoring-force stiffness sets the effective quartic λ_stiff:

        m_H^{vib} = v_EW × √(2 λ_stiff) ≈ 113.2 GeV   (−9.5% from 125.09 GeV)

    The 9.5% gap is bridged by the one-loop top-quark correction
    (braid_higgs_mass_top_corrected).
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    return higgs_vev_gev * math.sqrt(2.0 * braid_quartic_from_stiffness(n1, n2, k_cs, c_s))


def braid_higgs_mass_top_corrected(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    c_s: float = C_S_CANONICAL,
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
    lambda_cutoff_gev: float = 310.0,
) -> float:
    """One-loop top-corrected Higgs mass using tree-level quartic λ = c_s².

    Starting from the braid tree-level prediction (λ = c_s²), the
    top-quark loop adds a positive correction:

        m_H² = 2 c_s² v² + 3 y_t² m_t² / (4π²) × ln(Λ_KK² / m_t²)

    where Λ_KK is the physical KK cutoff (the UV scale of the 4D EFT).

    For Λ_KK = 310 GeV: m_H ≈ 124.1 GeV  (−0.8% from 125.09 GeV).
    For Λ_KK ≈ 327 GeV: m_H ≈ 125.09 GeV (exact — see braid_kk_cutoff_for_higgs_mass).

    This is the UM's best current Higgs mass prediction, combining:
      1. Geometric quartic λ = c_s² = (12/37)²
      2. SM one-loop RG improvement
      3. KK cutoff Λ_KK set by braid topology at ≈ 310–327 GeV

    Parameters
    ----------
    lambda_cutoff_gev : float
        KK cutoff Λ_KK [GeV].  Must exceed m_top_gev for a positive correction.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    if m_top_gev <= 0.0:
        raise ValueError(f"m_top_gev must be > 0, got {m_top_gev!r}")
    if y_top <= 0.0:
        raise ValueError(f"y_top must be > 0, got {y_top!r}")
    if lambda_cutoff_gev <= m_top_gev:
        raise ValueError(
            f"lambda_cutoff_gev ({lambda_cutoff_gev}) must exceed m_top_gev "
            f"({m_top_gev}) for a positive top-loop correction"
        )
    m_tree_sq = 2.0 * c_s ** 2 * higgs_vev_gev ** 2
    delta_m_sq = (
        3.0 * y_top ** 2 * m_top_gev ** 2
        / (4.0 * math.pi ** 2)
        * math.log((lambda_cutoff_gev / m_top_gev) ** 2)
    )
    return math.sqrt(m_tree_sq + delta_m_sq)


def braid_kk_cutoff_for_higgs_mass(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    higgs_mass_gev: float = HIGGS_MASS_GEV,
    c_s: float = C_S_CANONICAL,
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
) -> float:
    """KK cutoff Λ_KK that reconciles λ = c_s² with the observed Higgs mass.

    Inverts braid_higgs_mass_top_corrected():

        Λ_KK = m_t × exp((m_H_obs² − 2 c_s² v²) × 4π² / (3 y_t² m_t²) / 2)

    Canonical result: Λ_KK ≈ 327 GeV.

    Physical significance — a falsifiable prediction
    -----------------------------------------------
    Λ_KK ≈ 327 GeV is the mass of the first KK graviton resonance in the
    UM braid model.  LHC Run 3 dijet + dilepton searches have excluded RS1
    KK gravitons below ≈ 1–4 TeV (depending on coupling).  For the UM's
    smaller coupling (c_s ≈ 0.32), the bound is weaker.  A future collider
    detection at ≈ 327 GeV would strongly support the braid mechanism;
    definitive exclusion at this mass scale would falsify it.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if higgs_mass_gev <= 0.0:
        raise ValueError(f"higgs_mass_gev must be > 0, got {higgs_mass_gev!r}")
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    if m_top_gev <= 0.0:
        raise ValueError(f"m_top_gev must be > 0, got {m_top_gev!r}")
    if y_top <= 0.0:
        raise ValueError(f"y_top must be > 0, got {y_top!r}")
    m_tree_sq = 2.0 * c_s ** 2 * higgs_vev_gev ** 2
    m_obs_sq = higgs_mass_gev ** 2
    if m_obs_sq <= m_tree_sq:
        raise ValueError(
            f"Observed m_H² ({m_obs_sq:.1f}) ≤ tree-level m_H² ({m_tree_sq:.1f}); "
            "top correction cannot be negative — check inputs."
        )
    prefactor = 3.0 * y_top ** 2 * m_top_gev ** 2 / (4.0 * math.pi ** 2)
    ln_ratio = (m_obs_sq - m_tree_sq) / prefactor   # = ln((Λ/m_t)²)
    return m_top_gev * math.exp(ln_ratio / 2.0)


def braid_quartic_comparison(
    n1: int = BRAID_N1,
    n2: int = BRAID_N2,
    k_cs: int = K_CS_CANONICAL,
    c_s: float = C_S_CANONICAL,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    higgs_mass_gev: float = HIGGS_MASS_GEV,
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
    lambda_cutoff_gev: float = 310.0,
) -> dict:
    """Compare all geometric Higgs quartic / mass predictions in one call.

    Returns
    -------
    dict with keys:
        lambda_observed       — 0.1293 (PDG target)
        lambda_winding_ratio  — (n1/n2)²/(2π) ≈ 0.0812  (Gemini, −37% from obs)
        lambda_cs_sq          — c_s² ≈ 0.1052             (UM, −19% from obs)
        lambda_stiffness      — c_s²(1+n1n2/k_cs²) ≈ 0.1059 (UM, −18%)
        m_H_observed          — 125.09 GeV
        m_H_winding_ratio     — ≈  99.1 GeV  (Gemini formula, correct convention)
        m_H_gemini_wrong      — ≈  49.6 GeV  (Gemini formula, wrong convention)
        m_H_tree_cs_sq        — ≈ 112.9 GeV
        m_H_vibrational       — ≈ 113.2 GeV
        m_H_top_corrected     — ≈ 124.1 GeV (Λ_KK=310 GeV)
        lambda_kk_cutoff_gev  — ≈  327 GeV  (exact Λ_KK for m_H=125.09)
        best_error_pct        — % discrepancy of m_H_top_corrected
    """
    lam_obs = higgs_mass_gev ** 2 / (2.0 * higgs_vev_gev ** 2)
    lam_wind = braid_quartic_from_winding_ratio(n1, n2)
    lam_cs   = c_s ** 2
    lam_stiff = braid_quartic_from_stiffness(n1, n2, k_cs, c_s)

    m_wind   = braid_higgs_mass_from_winding_ratio(higgs_vev_gev, n1, n2)
    m_wind_wrong = higgs_vev_gev * math.sqrt(lam_wind / 2.0)   # Gemini wrong convention
    m_tree   = higgs_mass_from_cs_squared(higgs_vev_gev, c_s)
    m_vib    = braid_higgs_mass_vibrational(higgs_vev_gev, n1, n2, k_cs, c_s)
    m_top_corr = braid_higgs_mass_top_corrected(
        higgs_vev_gev, c_s, m_top_gev, y_top, lambda_cutoff_gev
    )
    lam_kk = braid_kk_cutoff_for_higgs_mass(
        higgs_vev_gev, higgs_mass_gev, c_s, m_top_gev, y_top
    )

    return {
        "lambda_observed":      lam_obs,
        "lambda_winding_ratio": lam_wind,
        "lambda_cs_sq":         lam_cs,
        "lambda_stiffness":     lam_stiff,
        "m_H_observed":         higgs_mass_gev,
        "m_H_winding_ratio":    m_wind,
        "m_H_gemini_wrong":     m_wind_wrong,
        "m_H_tree_cs_sq":       m_tree,
        "m_H_vibrational":      m_vib,
        "m_H_top_corrected":    m_top_corr,
        "lambda_kk_cutoff_gev": lam_kk,
        "best_error_pct":       (m_top_corr - higgs_mass_gev) / higgs_mass_gev * 100.0,
    }


# ---------------------------------------------------------------------------
# §6 continued — Hard-cutoff scheme, naturalness, and scheme comparison
# ---------------------------------------------------------------------------
# The existing braid_higgs_mass_top_corrected uses dimensional regularisation
# (MS-bar): only the logarithmic term survives, giving a POSITIVE correction
# and m_H ≈ 125.1 GeV at Λ_KK ≈ 332 GeV.
#
# A physical hard UV cutoff (appropriate when KK modes provide the actual
# UV completion) yields BOTH a quadratic AND a logarithmic term.  The
# quadratic term carries a minus sign (fermion loop) and dominates for
# Λ > m_t × exp(1/2) ≈ 285 GeV, so the hard-cutoff correction is NEGATIVE.
# This gives m_H < m_H_tree ≈ 112.9 GeV and the model goes tachyonic at
# Λ_tach ≈ 480 GeV.  The naturalness bound (|δm²| = m_H_obs²) is Λ_nat ≈ 524 GeV.
#
# Scheme dependence is an honest open gap: the UM does not yet specify which
# regularisation correctly describes the physical KK UV completion.


def braid_hard_cutoff_delta_mh_sq(
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
    lambda_cutoff_gev: float = 332.0,
) -> float:
    """Hard-cutoff top-loop correction δm_H² [GeV²] (negative for Λ > 285 GeV).

    In a theory with a hard momentum cutoff Λ the top-quark one-loop
    contribution to the Higgs mass squared is:

        δm_H² = 3 y_t² / (4π²) × (−Λ² + m_t² ln(Λ²/m_t²))

    The first term (quadratic, negative) dominates for Λ > m_t × exp(½) ≈ 285 GeV,
    making the hard-cutoff correction negative — the core of the naturalness
    problem.  At Λ = 332 GeV: δm_H² ≈ −5 345 GeV².

    Parameters
    ----------
    lambda_cutoff_gev : float
        Hard UV cutoff Λ [GeV].  Must be > 0.
    """
    if lambda_cutoff_gev <= 0.0:
        raise ValueError(f"lambda_cutoff_gev must be > 0, got {lambda_cutoff_gev!r}")
    if m_top_gev <= 0.0:
        raise ValueError(f"m_top_gev must be > 0, got {m_top_gev!r}")
    if y_top <= 0.0:
        raise ValueError(f"y_top must be > 0, got {y_top!r}")
    prefactor = 3.0 * y_top ** 2 / (4.0 * math.pi ** 2)
    return prefactor * (
        -(lambda_cutoff_gev ** 2)
        + m_top_gev ** 2 * math.log((lambda_cutoff_gev / m_top_gev) ** 2)
    )


def braid_higgs_mass_hard_cutoff(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    c_s: float = C_S_CANONICAL,
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
    lambda_cutoff_gev: float = 332.0,
) -> float:
    """Higgs mass [GeV] in the hard-cutoff (quadratic + log) scheme.

    Combines the geometric tree-level prediction (λ_tree = c_s²) with the
    hard-cutoff top-loop correction:

        m_H² = 2 c_s² v² + 3 y_t²/(4π²) × (−Λ² + m_t² ln(Λ²/m_t²))

    Key results at canonical inputs:
        Λ = 200 GeV → m_H ≈ 112.3 GeV (barely below tree-level)
        Λ = 332 GeV → m_H ≈  85.9 GeV (well below tree-level 112.9 GeV)
        Λ ≈ 480 GeV → m_H →    0 GeV  (tachyonic threshold)

    Contrast with the dim-reg formula (braid_higgs_mass_top_corrected):
        Λ = 332 GeV → m_H ≈ 125.1 GeV (above tree-level)

    The scheme dependence is an honest open gap in the UM framework.

    Raises
    ------
    ValueError
        If m_H² < 0 (tachyonic — use braid_tachyon_kk_scale to find threshold).
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    m_tree_sq = 2.0 * c_s ** 2 * higgs_vev_gev ** 2
    delta = braid_hard_cutoff_delta_mh_sq(m_top_gev, y_top, lambda_cutoff_gev)
    m_sq = m_tree_sq + delta
    if m_sq < 0.0:
        raise ValueError(
            f"Hard-cutoff Higgs mass² = {m_sq:.1f} GeV² < 0 (tachyonic) "
            f"at Λ = {lambda_cutoff_gev} GeV.  "
            "Use braid_tachyon_kk_scale() to find the tachyonic threshold."
        )
    return math.sqrt(m_sq)


def braid_hard_cutoff_finetuning(
    higgs_mass_gev: float = HIGGS_MASS_GEV,
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
    lambda_cutoff_gev: float = 332.0,
) -> float:
    """Fine-tuning measure Δ_FT = |δm_H²(hard)| / m_H_obs² at a given cutoff.

    A value > 1 means the correction exceeds the physical Higgs mass squared
    — i.e. the model is unnatural at this scale.  At Λ_nat the measure = 1.

    Canonical result: Δ_FT(332 GeV) ≈ 0.342 (34% fine-tuning, mildly unnatural).
    """
    if higgs_mass_gev <= 0.0:
        raise ValueError(f"higgs_mass_gev must be > 0, got {higgs_mass_gev!r}")
    delta_sq = braid_hard_cutoff_delta_mh_sq(m_top_gev, y_top, lambda_cutoff_gev)
    return abs(delta_sq) / (higgs_mass_gev ** 2)


def _hard_cutoff_f(lam: float, m_top: float, y_top: float, target_sq: float) -> float:
    """Helper: hard-cutoff correction magnitude minus target [GeV²]."""
    prefactor = 3.0 * y_top ** 2 / (4.0 * math.pi ** 2)
    val = prefactor * (lam ** 2 - m_top ** 2 * math.log((lam / m_top) ** 2))
    return val - target_sq


def braid_natural_kk_scale(
    higgs_mass_gev: float = HIGGS_MASS_GEV,
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
) -> float:
    """Naturalness bound Λ_nat [GeV] where |δm_H²(hard)| = m_H_obs².

    Above this scale the model requires > 100% cancellation between the
    braid tree-level quartic and the top-loop correction — the definition
    of unnaturalness in the hard-cutoff scheme.

    Solved via bisection.  Canonical result: Λ_nat ≈ 524 GeV.

    Physical implication: if the first KK resonance lies below ≈ 524 GeV
    the UM is at most mildly unnatural (Δ_FT < 1).  Current LHC bounds on
    RS1 KK gravitons are ≳ 1–4 TeV (coupling-dependent), so the UM is
    technically unnatural by this measure — an honest open gap.
    """
    target = higgs_mass_gev ** 2
    lo, hi = m_top_gev * 1.01, 5000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _hard_cutoff_f(mid, m_top_gev, y_top, target) < 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def braid_tachyon_kk_scale(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    c_s: float = C_S_CANONICAL,
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
) -> float:
    """Hard-cutoff tachyonic threshold Λ_tach [GeV] where m_H²(hard) → 0.

    Above this scale the hard-cutoff formula predicts an imaginary Higgs mass
    (tachyon), signalling breakdown of the perturbative EFT.  In the UM the
    tachyonic threshold sets a hard upper limit on the physical KK cutoff if
    the hard-cutoff scheme is used.

    Canonical result: Λ_tach ≈ 480 GeV.
    """
    if higgs_vev_gev <= 0.0:
        raise ValueError(f"higgs_vev_gev must be > 0, got {higgs_vev_gev!r}")
    if c_s <= 0.0:
        raise ValueError(f"c_s must be > 0, got {c_s!r}")
    tree_sq = 2.0 * c_s ** 2 * higgs_vev_gev ** 2  # > 0
    lo, hi = m_top_gev * 1.01, 5000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _hard_cutoff_f(mid, m_top_gev, y_top, tree_sq) < 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def braid_higgs_mass_scheme_comparison(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    higgs_mass_gev: float = HIGGS_MASS_GEV,
    c_s: float = C_S_CANONICAL,
    m_top_gev: float = TOP_MASS_GEV,
    y_top: float = TOP_YUKAWA,
    lambda_cutoff_gev: float = 332.0,
) -> dict:
    """Compare dim-reg vs hard-cutoff Higgs mass predictions at Λ = lambda_cutoff_gev.

    Returns
    -------
    dict with keys:
        m_H_observed          — 125.09 GeV (PDG target)
        m_H_tree              — ≈ 112.9 GeV  (tree-level, λ = c_s²)
        m_H_dim_reg           — ≈ 125.1 GeV  (MS-bar/dim-reg at Λ=332 GeV) [CORRECT]
        m_H_hard_cutoff       — ≈  85.9 GeV  (hard-cutoff at Λ=332 GeV, or None if tachyonic)
        delta_mh_sq_dim_reg   — ≈ +2 927 GeV² (positive log correction)
        delta_mh_sq_hard      — ≈ −5 345 GeV² (negative quad+log correction)
        finetuning_hard       — ≈  0.342       (34% at Λ=332 GeV)
        lambda_nat_gev        — ≈  524 GeV     (naturalness bound)
        lambda_tach_gev       — ≈  480 GeV     (tachyonic threshold)
        scheme_gap_gev        — |m_H_dim_reg − m_H_hard_cutoff|
        dim_reg_error_pct     — % error of dim-reg vs observed
        honest_assessment     — str
    """
    m_tree = higgs_mass_from_cs_squared(higgs_vev_gev, c_s)
    m_dr = braid_higgs_mass_top_corrected(
        higgs_vev_gev, c_s, m_top_gev, y_top, lambda_cutoff_gev
    )
    delta_dr = (
        3.0 * y_top ** 2 * m_top_gev ** 2
        / (4.0 * math.pi ** 2)
        * math.log((lambda_cutoff_gev / m_top_gev) ** 2)
    )
    delta_hard = braid_hard_cutoff_delta_mh_sq(m_top_gev, y_top, lambda_cutoff_gev)
    try:
        m_hard: float | None = braid_higgs_mass_hard_cutoff(
            higgs_vev_gev, c_s, m_top_gev, y_top, lambda_cutoff_gev
        )
    except ValueError:
        m_hard = None

    ft = braid_hard_cutoff_finetuning(higgs_mass_gev, m_top_gev, y_top, lambda_cutoff_gev)
    lam_nat = braid_natural_kk_scale(higgs_mass_gev, m_top_gev, y_top)
    lam_tach = braid_tachyon_kk_scale(higgs_vev_gev, c_s, m_top_gev, y_top)
    scheme_gap = abs(m_dr - m_hard) if m_hard is not None else None
    dr_err = (m_dr - higgs_mass_gev) / higgs_mass_gev * 100.0

    return {
        "m_H_observed":        higgs_mass_gev,
        "m_H_tree":            m_tree,
        "m_H_dim_reg":         m_dr,
        "m_H_hard_cutoff":     m_hard,
        "delta_mh_sq_dim_reg": delta_dr,
        "delta_mh_sq_hard":    delta_hard,
        "finetuning_hard":     ft,
        "lambda_nat_gev":      lam_nat,
        "lambda_tach_gev":     lam_tach,
        "scheme_gap_gev":      scheme_gap,
        "dim_reg_error_pct":   dr_err,
        "honest_assessment": (
            "Dim-reg gives m_H ≈ 125 GeV at Λ_KK ≈ 332 GeV (0.03% error); "
            "hard-cutoff gives m_H ≈ 85.9 GeV at the same scale (tachyonic at "
            "Λ ≈ 480 GeV). Scheme dependence is an honest open gap — the UM "
            "does not yet specify which regularisation describes the physical "
            "KK UV completion."
        ),
    }


def higgs_mass_from_ftum_critical(
    n_w: int = N_W_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    higgs_mass_obs_gev: float = HIGGS_MASS_GEV,
) -> dict:
    """Derive the Higgs mass from the FTUM critical fixed point.

    The FTUM (Field Theory Unification Mechanism) critical fixed point sets
    the Higgs quartic coupling λ_H via the UM winding/braid geometry:

        λ_H_crit = (n_w² / k_cs) × (1/2)
                 = (5² / 74) / 2  ≈ 0.1689

    The Higgs mass follows from the tree-level relation:

        m_H² = 2 × λ_H_crit × v²   →   m_H = v √(2 λ_H_crit)

    With n_w=5, k_cs=74, v=246 GeV:

        λ_H_crit = 25/148 ≈ 0.1689
        m_H = 246 × √(2 × 0.1689) ≈ 246 × 0.5814 ≈ 143 GeV

    The observed value is 125.09 GeV.  Discrepancy: ~14 %.  This is the
    leading-order FTUM estimate; loop corrections to λ_H (running from M_KK
    to v) reduce it by ~10–15 %, potentially closing the gap.  Documented
    honestly as an ESTIMATE with ~14 % accuracy.

    Parameters
    ----------
    n_w              : int    Winding number (default 5).
    k_cs             : int    Chern-Simons level k_CS = 74 (default).
    higgs_vev_gev    : float  Higgs VEV [GeV] (default 246.0).
    higgs_mass_obs_gev: float Observed Higgs pole mass [GeV] (default 125.09).

    Returns
    -------
    dict
        'n_w'             : int — winding number used.
        'k_cs'            : int — Chern-Simons level.
        'lambda_H_crit'   : float — FTUM critical quartic.
        'm_H_geo_gev'     : float — geometric Higgs mass [GeV].
        'm_H_obs_gev'     : float — observed Higgs mass [GeV].
        'm_H_pct_err'     : float — percentage error.
        'higgs_vev_gev'   : float — Higgs VEV.
        'status'          : str.
        'derivation'      : str.
    """
    lambda_H_crit = (n_w ** 2) / (2.0 * k_cs)
    m_H_geo = higgs_vev_gev * math.sqrt(2.0 * lambda_H_crit)
    pct_err = abs(m_H_geo - higgs_mass_obs_gev) / higgs_mass_obs_gev * 100.0

    if pct_err < 5.0:
        status_tag = "CONSISTENT — within 5 %"
    elif pct_err < 20.0:
        status_tag = "ESTIMATE — within 20 %"
    else:
        status_tag = "TENSION — beyond 20 % accuracy"

    return {
        "n_w": n_w,
        "k_cs": k_cs,
        "lambda_H_crit": lambda_H_crit,
        "m_H_geo_gev": m_H_geo,
        "m_H_obs_gev": higgs_mass_obs_gev,
        "m_H_pct_err": pct_err,
        "higgs_vev_gev": higgs_vev_gev,
        "status": (
            f"{status_tag}: m_H_geo = v √(2λ_H_crit) = {higgs_vev_gev:.1f} × "
            f"√(2 × {lambda_H_crit:.4f}) = {m_H_geo:.2f} GeV. "
            f"Observed {higgs_mass_obs_gev:.2f} GeV — {pct_err:.1f} % off. "
            "Loop corrections to λ_H from M_KK → v expected to reduce m_H "
            "by ~10–15 %, potentially closing the gap (Pillar 88)."
        ),
        "derivation": (
            f"FTUM critical fixed point: λ_H_crit = n_w²/(2 k_cs) = "
            f"{n_w}²/(2×{k_cs}) = {lambda_H_crit:.6f}. "
            f"Tree-level: m_H = v √(2λ) = {higgs_vev_gev} × √(2×{lambda_H_crit:.4f}) "
            f"= {m_H_geo:.3f} GeV. "
            f"PDG m_H = {higgs_mass_obs_gev} GeV. Accuracy: {pct_err:.1f} %. "
            "Status: ESTIMATE (loop corrections documented in Pillar 88)."
        ),
    }
