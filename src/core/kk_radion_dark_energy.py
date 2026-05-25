# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_radion_dark_energy.py
===================================
Pillar 136 — KK Radion Dark Energy: Corrected Equation of State.

Physical Context
----------------
The leading-order UM dark energy equation of state is:

    w_KK = −1 + (2/3) c_s²   with  c_s = 12/37  (braided sound speed)
         = −1 + (2/3) × (12/37)²  ≈  −0.9302

This sits 2.5–3.3σ from the Planck+BAO combined w = −1.03 ± 0.03 and is in
1–3σ tension depending on the analysis.

However, the w_KK formula is the **slow-roll approximation** for the KK zero-
mode.  The stabilised radion field acquires a potential V(r) from the Goldberger-
Wise mechanism, and this potential corrects the effective dark energy EoS.

Radion Potential Correction
----------------------------
When the radion field φ is stabilised near its GW minimum φ₀, it acts as a
quintessence-like scalar field with potential:

    V(φ) = V₀ × [1 + ε_GW × (φ/φ₀ − 1)² + ...]

where ε_GW << 1 is the small GW perturbation parameter.

At late times, if the radion mass satisfies m_r >> H₀ (the Hubble rate today),
the radion is frozen at φ₀ and effectively acts as a cosmological constant.
The deviation from w = −1 is then suppressed by (H₀/m_r)²:

    w_corrected = w_KK + Δw_radion

where:
    Δw_radion = +(1/3) × (H₀/m_r)² × c_s²    [correction toward w = −1]

The sign is positive: the radion correction moves w_corrected **toward** −1
compared to the slow-roll w_KK.

Radion Mass Estimate
---------------------
From the Goldberger-Wise mechanism, the radion mass in 4D Planck units is:

    m_r² ≈ λ_GW × M_KK²

where λ_GW ~ O(1) is the GW coupling and M_KK is the KK scale.

For M_KK ≈ 1000 GeV and H₀ ≈ 2.2 × 10⁻⁴² GeV:
    (H₀/m_r)² ≈ (2.2e-42 / 1000)² ≈ 4.8 × 10⁻⁹⁰ → Δw ≈ 0

The radion correction is completely negligible for the EW-sector radion.

However, a second relevant radion is the dark-energy radion: the compactification
radius R is stabilised at a very different scale.  The dark-energy KK mode has:

    M_KK^{DE} ≈ H₀ × 10^some_factor   (set by the cosmological constant problem)

If M_KK^{DE} ~ H₀, then (H₀/m_r)² ~ O(1) and the correction is significant.

The UM predicts two KK scales:
  1. EW radion: M_KK^{EW} ≈ 1 TeV (Pillar 81, RS hierarchy)
  2. DE radion: M_KK^{DE} ≈ H₀ × exp(πkR_DE) ~ meV (zero-point vacuum, Pillar 38)

For the dark energy sector, the relevant radion mass is set by the GW
stabilisation of the DE compactification:

    m_r^{DE} ≈ √λ_GW × M_KK^{DE}

If m_r^{DE} >> H₀ (which is the case for M_KK^{DE} >> H₀):
    Δw ≈ 0 and w_corrected = w_KK ≈ −0.9302

If m_r^{DE} ~ H₀ (near the oscillation threshold):
    The radion is rolling slowly → acts like quintessence → w moves toward −1

Honest Assessment
-----------------
The radion potential correction to w_KK is computed honestly here:
  - For M_KK >> H₀ (standard RS): correction is negligible, w ≈ w_KK ≈ −0.9302
  - For M_KK ~ H₀ (DE tuned): significant correction possible
  - The tension w_KK = −0.9302 vs Planck+BAO w ≈ −1.03 ± 0.03 is genuine
  - DESI DR2 gives w₀ = −0.92 ± 0.09 → w_KK falls WITHIN 1σ of DESI

The DESI DR2 result (April 2025) significantly reduces the tension:
    |w_KK − w₀_DESI| = |−0.9302 − (−0.92)| / 0.09 = 0.11σ  ← CONSISTENT ✅

The Planck+BAO combination (older constraint) gives higher tension.
The current observational status is dataset-dependent.

Result: w_KK is ⚠️ CONSTRAINED with radion correction.  The radion potential
analysis confirms that for M_KK >> H₀, the slow-roll formula w_KK = -1 + (2/3)c_s²
is the exact late-time attractor, and any correction is < 10⁻⁸⁵.

Public API
----------
kk_eos_leading_order(n1, n2) → float
    w_KK = −1 + (2/3) c_s² (leading order).

radion_mass_over_hubble(m_kk_gev, lambda_gw, h0_gev) → float
    m_r / H₀ ratio.

radion_eos_correction(m_kk_gev, lambda_gw, h0_gev, c_s_sq) → float
    Δw from radion potential correction.

kk_eos_corrected(n1, n2, m_kk_gev, lambda_gw, h0_gev) → dict
    w_corrected = w_KK + Δw with full derivation.

eos_tension_vs_datasets(n1, n2) → dict
    Tension of w_KK vs Planck+BAO, DESI DR2, and forecast Roman.

pillar136_summary() → dict
    Structured closure status.

Code architecture, test suites, document engineering, and synthesis:
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
from typing import Dict

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: Braided sound speed c_s = 12/37 (Pillar 38)
C_S_BRAID: float = 12.0 / 37.0

#: c_s² = (12/37)²
C_S_SQUARED: float = C_S_BRAID ** 2

#: Leading-order w_KK = −1 + (2/3) c_s²
W_KK_LEADING: float = -1.0 + (2.0 / 3.0) * C_S_SQUARED  # ≈ −0.9302

#: Canonical braided pair (Pillar 58)
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7

#: RS hierarchy πkR (Pillar 81)
PI_KR_CANONICAL: float = 37.0

#: EW KK mass scale [GeV] — from RS warp: M_Pl × exp(−πkR)
M_KK_EW_GEV: float = 1.22089e19 * math.exp(-PI_KR_CANONICAL)  # ≈ 1040 GeV

#: Hubble constant today H₀ [GeV] ≈ 2.18 × 10⁻⁴² GeV
H0_GEV: float = 2.184e-42  # from H₀ = 67.4 km/s/Mpc in natural units

#: GW coupling (natural; λ_GW ~ 1 in Planck units)
LAMBDA_GW_NATURAL: float = 1.0

#: Observational constraints on w
W_PLANCK_BAO_CENTRAL: float = -1.03     # Planck+BAO combined w
W_PLANCK_BAO_SIGMA: float = 0.03        # 1σ

#: DESI Year 3 / DR2 w₀CDM value (wₐ FORCED TO 0 in the DESI fit).
#: CIRCULAR COMPARISON WARNING (Pillar 421 Issue 3): comparing the UM's
#: w_KK = −0.9302 (which also has wₐ = 0) to this value is circular.
#: The DESI fitter and the UM both assume wₐ = 0, so agreement is
#: guaranteed by construction.  This gives 0.11σ — not an independent test.
#: Use W_DESI_DR2_CPL_W0 below for the correct comparison.
W_DESI_DR2_W0CDM_CENTRAL: float = -0.92   # w₀CDM (wₐ = 0 assumed)
W_DESI_DR2_W0CDM_SIGMA: float = 0.09      # 1σ
W_DESI_DR2_CENTRAL: float = W_DESI_DR2_W0CDM_CENTRAL  # backward-compat alias

#: DESI Year 3 / DR2 CPL w₀ (wₐ FREE in the DESI fit) — CORRECT comparison.
#: This is independent: DESI did not assume wₐ = 0 to obtain this value.
W_DESI_DR2_CPL_W0: float = -0.838    # CPL fit; wₐ free
W_DESI_DR2_CPL_W0_SIGMA: float = 0.072
W_DESI_DR2_SIGMA: float = W_DESI_DR2_CPL_W0_SIGMA  # backward-compat alias (CPL value)

W_ROMAN_FORECAST_CENTRAL: float = -1.0  # Roman forecast (nominal ΛCDM)
W_ROMAN_FORECAST_SIGMA: float = 0.02    # 1σ (forecast)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def kk_eos_leading_order(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
) -> float:
    """Compute the leading-order KK zero-mode EoS w_KK = −1 + (2/3)c_s².

    SCOPE NOTE (Pillar 421, Issue 2):
    This formula gives the equation of state of the INFLATIONARY KK zero-mode
    during the inflationary epoch.  It is NOT a prediction for today's dark
    energy.  The physically self-consistent frozen-radion dark energy prediction
    is w₀ = −1 (see pillar421_desi_cpl_consistency_audit.py).

    Parameters
    ----------
    n1, n2 : int  Braid winding numbers (default 5, 7).

    Returns
    -------
    float
        w_KK = −1 + (2/3)c_s² ≈ −0.9302 (inflationary epoch value).
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"Winding numbers must be positive; got n1={n1}, n2={n2}.")
    # c_s = 12/37 is the braided sound speed derived from the (5,7) braid
    # resonance condition (Pillar 38).  It is a derived constant of the UM
    # and does not depend on n1, n2 independently — the winding pair (n1, n2)
    # only enters through this fixed canonical value.
    c_s = C_S_BRAID
    return -1.0 + (2.0 / 3.0) * c_s ** 2


def radion_mass_over_hubble(
    m_kk_gev: float = M_KK_EW_GEV,
    lambda_gw: float = LAMBDA_GW_NATURAL,
    h0_gev: float = H0_GEV,
) -> float:
    """Compute the radion mass to Hubble ratio m_r / H₀.

    Radion mass: m_r² = λ_GW × M_KK²

    Parameters
    ----------
    m_kk_gev  : float  KK mass scale [GeV] (default EW: ~1040 GeV).
    lambda_gw : float  GW coupling (default 1.0).
    h0_gev    : float  Hubble constant [GeV] (default 2.18 × 10⁻⁴² GeV).

    Returns
    -------
    float
        m_r / H₀ (dimensionless; >> 1 means radion is frozen).
    """
    if m_kk_gev <= 0:
        raise ValueError(f"m_kk_gev must be positive; got {m_kk_gev}.")
    if lambda_gw <= 0:
        raise ValueError(f"lambda_gw must be positive; got {lambda_gw}.")
    if h0_gev <= 0:
        raise ValueError(f"h0_gev must be positive; got {h0_gev}.")
    m_r = math.sqrt(lambda_gw) * m_kk_gev
    return m_r / h0_gev


def radion_eos_correction(
    m_kk_gev: float = M_KK_EW_GEV,
    lambda_gw: float = LAMBDA_GW_NATURAL,
    h0_gev: float = H0_GEV,
    c_s_sq: float = C_S_SQUARED,
) -> float:
    """Compute the radion potential correction Δw to the dark energy EoS.

    For m_r >> H₀, the radion is frozen at its minimum and acts as a
    cosmological constant.  The deviation from the leading-order w_KK is:

        Δw ≈ +(1/3) × (H₀/m_r)² × c_s²    [→ 0 for m_r >> H₀]

    This correction is positive (moves w toward −1 from above).

    Parameters
    ----------
    m_kk_gev : float  KK mass scale [GeV].
    lambda_gw: float  GW coupling.
    h0_gev   : float  Hubble constant [GeV].
    c_s_sq   : float  Braided sound speed squared c_s².

    Returns
    -------
    float
        Δw (positive correction toward w = −1).
    """
    r = radion_mass_over_hubble(m_kk_gev, lambda_gw, h0_gev)
    # Δw = +(1/3)(H₀/m_r)² × c_s²
    return (1.0 / 3.0) * (1.0 / r) ** 2 * c_s_sq


def kk_eos_corrected(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
    m_kk_gev: float = M_KK_EW_GEV,
    lambda_gw: float = LAMBDA_GW_NATURAL,
    h0_gev: float = H0_GEV,
) -> Dict[str, object]:
    """Compute the corrected dark energy EoS w_corrected = w_KK + Δw_radion.

    Parameters
    ----------
    n1, n2    : int   Braid winding numbers (default 5, 7).
    m_kk_gev  : float KK mass [GeV] (default EW KK scale).
    lambda_gw : float GW coupling (default 1.0).
    h0_gev    : float Hubble constant [GeV] (default 2.18 × 10⁻⁴² GeV).

    Returns
    -------
    dict
        'w_leading'    : float — w_KK = −1 + (2/3)c_s².
        'delta_w'      : float — Δw_radion.
        'w_corrected'  : float — w_leading + delta_w.
        'm_r_over_h0'  : float — radion mass / H₀.
        'correction_negligible': bool — True if |Δw| < 1e-6.
        'derivation'   : str.
    """
    w_lead = kk_eos_leading_order(n1, n2)
    dw = radion_eos_correction(m_kk_gev, lambda_gw, h0_gev)
    w_corr = w_lead + dw
    r = radion_mass_over_hubble(m_kk_gev, lambda_gw, h0_gev)
    negligible = abs(dw) < 1e-6

    return {
        "n1": n1,
        "n2": n2,
        "c_s": C_S_BRAID,
        "c_s_sq": C_S_SQUARED,
        "w_leading": w_lead,
        "delta_w": dw,
        "w_corrected": w_corr,
        "m_kk_gev": m_kk_gev,
        "lambda_gw": lambda_gw,
        "m_r_over_h0": r,
        "correction_negligible": negligible,
        "derivation": (
            f"Leading: w_KK = −1 + (2/3)c_s² = −1 + (2/3)×{C_S_SQUARED:.5f} = {w_lead:.6f}.\n"
            f"Radion: m_r = √λ_GW × M_KK = √{lambda_gw}×{m_kk_gev:.1f} GeV.\n"
            f"m_r/H₀ = {r:.3e} (>> 1: radion frozen, correction negligible).\n"
            f"Δw = (1/3)(H₀/m_r)² c_s² = {dw:.3e}.\n"
            f"w_corrected = {w_corr:.8f}  ≈  w_KK = {w_lead:.8f}."
        ),
    }


def eos_tension_vs_datasets(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
) -> Dict[str, object]:
    """Compute tension of w_KK against multiple observational datasets.

    Pillar 421 corrections applied:
    - DESI CPL fit (w₀ free) used as primary comparison (non-circular).
    - DESI w₀CDM fit (wₐ forced to 0) labeled as circular comparison.
    - Frozen-radion coherent prediction (w₀ = −1) also computed.

    Datasets included:
      - Planck + BAO combined: w = −1.03 ± 0.03 (older; prior-dominated)
      - DESI Y3/DR2 CPL: w₀ = −0.838 ± 0.072 (correct; wₐ free in fit)
      - DESI Y3/DR2 w₀CDM: w₀ = −0.92 ± 0.09 (CIRCULAR — wₐ forced to 0)
      - Roman Space Telescope (forecast): w = −1.00 ± 0.02

    Parameters
    ----------
    n1, n2 : int  Braid winding numbers (default 5, 7).

    Returns
    -------
    dict
        Per-dataset tension dict with 'sigma' and 'consistent' fields.
    """
    w_pred = kk_eos_leading_order(n1, n2)
    w_pred_frozen = -1.0  # frozen-radion coherent prediction

    planck_sigma       = abs(w_pred - W_PLANCK_BAO_CENTRAL) / W_PLANCK_BAO_SIGMA
    desi_cpl_sigma     = abs(w_pred - W_DESI_DR2_CPL_W0) / W_DESI_DR2_CPL_W0_SIGMA
    desi_w0cdm_sigma   = abs(w_pred - W_DESI_DR2_W0CDM_CENTRAL) / W_DESI_DR2_W0CDM_SIGMA
    roman_sigma        = abs(w_pred - W_ROMAN_FORECAST_CENTRAL) / W_ROMAN_FORECAST_SIGMA
    # Frozen-radion coherent point
    frozen_desi_cpl_sigma = abs(w_pred_frozen - W_DESI_DR2_CPL_W0) / W_DESI_DR2_CPL_W0_SIGMA

    return {
        "w_predicted_inflationary_kk": w_pred,
        "w_predicted_frozen_radion_coherent": w_pred_frozen,
        "planck_bao": {
            "w_central": W_PLANCK_BAO_CENTRAL,
            "w_sigma": W_PLANCK_BAO_SIGMA,
            "sigma_tension": planck_sigma,
            "consistent_1sigma": planck_sigma <= 1.0,
            "consistent_2sigma": planck_sigma <= 2.0,
            "consistent_3sigma": planck_sigma <= 3.0,
            "label": "Planck+BAO",
            "note": "Prior-dominated; w = const assumption; superseded by DESI",
        },
        "desi_dr2_cpl": {
            "w_central": W_DESI_DR2_CPL_W0,
            "w_sigma": W_DESI_DR2_CPL_W0_SIGMA,
            "sigma_tension": desi_cpl_sigma,
            "consistent_1sigma": desi_cpl_sigma <= 1.0,
            "consistent_2sigma": desi_cpl_sigma <= 2.0,
            "consistent_3sigma": desi_cpl_sigma <= 3.0,
            "label": "DESI Y3/DR2 CPL (w₀ free)",
            "note": "CORRECT comparison: wₐ free in DESI fit (Pillar 421 Issue 3)",
            "is_circular": False,
        },
        "desi_dr2_w0cdm": {
            "w_central": W_DESI_DR2_W0CDM_CENTRAL,
            "w_sigma": W_DESI_DR2_W0CDM_SIGMA,
            "sigma_tension": desi_w0cdm_sigma,
            "consistent_1sigma": desi_w0cdm_sigma <= 1.0,
            "consistent_2sigma": desi_w0cdm_sigma <= 2.0,
            "label": "DESI Y3/DR2 w₀CDM (wₐ = 0 assumed)",
            "note": (
                "CIRCULAR comparison: DESI forced wₐ = 0 to obtain this value. "
                "The UM also has wₐ = 0.  Agreement here is not independent. "
                "Do NOT use this value for UM validation (Pillar 421 Issue 3)."
            ),
            "is_circular": True,
        },
        "frozen_radion_vs_desi_cpl": {
            "w_central": W_DESI_DR2_CPL_W0,
            "w_sigma": W_DESI_DR2_CPL_W0_SIGMA,
            "sigma_tension": frozen_desi_cpl_sigma,
            "w_predicted": w_pred_frozen,
            "label": "Frozen-radion coherent DE (w₀ = −1) vs DESI Y3/DR2 CPL",
            "note": (
                "The physically self-consistent UM frozen-radion dark energy "
                "prediction (w₀ = −1, wₐ = 0) compared to DESI CPL (correct). "
                "This gives 2.25σ on w₀ alone; joint 2D with ρ = −0.97 gives ~3.9σ."
            ),
        },
        "roman_forecast": {
            "w_central": W_ROMAN_FORECAST_CENTRAL,
            "w_sigma": W_ROMAN_FORECAST_SIGMA,
            "sigma_tension": roman_sigma,
            "consistent_1sigma": roman_sigma <= 1.0,
            "consistent_2sigma": roman_sigma <= 2.0,
            "consistent_3sigma": roman_sigma <= 3.0,
            "label": "Roman (forecast)",
        },
    }


def w0_experimental_landscape() -> Dict[str, object]:
    """Frame the UM w₀ prediction as a discriminant between competing datasets.

    Pillar 421 corrections applied:
    - Primary DESI comparison uses the CPL fit (w₀ = −0.838 ± 0.072; wₐ free).
    - The w₀CDM value (−0.92 ± 0.09) is documented as a circular comparison.
    - The frozen-radion coherent prediction (w₀ = −1) is included.
    - The 0.11σ claim (from the circular w₀CDM comparison) is removed.

    The UM has two w₀ values depending on which physical mechanism is cited:
      • w_KK = −0.9302 (inflationary-epoch formula; scope caveat applies)
      • w₀ = −1 (frozen-radion DE; physically self-consistent with wₐ = 0)

    Against DESI CPL:
      • w_KK gives 1.28σ tension (w₀ only; but mechanism is inflationary epoch)
      • w₀ = −1 gives 2.25σ tension on w₀ alone; ~3.9σ joint 2D

    Returns
    -------
    dict
        'w_predicted_kk'              : float
        'w_predicted_frozen_radion'   : float
        'datasets'                    : dict — per-experiment tensions
        'planck_desi_tension'         : float — internal Planck vs DESI tension in σ
        'um_position'                 : str
        'discriminant_status'         : str
        'roman_falsifier'             : str
    """
    w_pred_kk = W_KK_LEADING
    w_pred_frozen = -1.0

    # Per-dataset sigma tensions (using CPL as primary)
    planck_sigma        = abs(w_pred_kk - W_PLANCK_BAO_CENTRAL) / W_PLANCK_BAO_SIGMA
    desi_cpl_sigma      = abs(w_pred_kk - W_DESI_DR2_CPL_W0) / W_DESI_DR2_CPL_W0_SIGMA
    desi_w0cdm_sigma    = abs(w_pred_kk - W_DESI_DR2_W0CDM_CENTRAL) / W_DESI_DR2_W0CDM_SIGMA
    roman_sigma         = abs(w_pred_kk - W_ROMAN_FORECAST_CENTRAL) / W_ROMAN_FORECAST_SIGMA
    frozen_cpl_sigma    = abs(w_pred_frozen - W_DESI_DR2_CPL_W0) / W_DESI_DR2_CPL_W0_SIGMA

    # DES Y3 + Planck + BAO: w = −0.98 ± 0.06 (Abbott et al. 2022)
    w_des_y3 = -0.98
    sigma_des_y3 = 0.06
    des_sigma = abs(w_pred_kk - w_des_y3) / sigma_des_y3

    # Internal Planck vs DESI tension (CPL w₀)
    planck_desi_internal = abs(W_PLANCK_BAO_CENTRAL - W_DESI_DR2_CPL_W0) / math.sqrt(
        W_PLANCK_BAO_SIGMA**2 + W_DESI_DR2_CPL_W0_SIGMA**2
    )

    # Classify UM position using CPL comparison (non-circular)
    if desi_cpl_sigma < 1.5 and planck_sigma > 2.0:
        um_position = "DESI-preferred"
    elif planck_sigma < 1.0 and desi_cpl_sigma > 2.0:
        um_position = "Planck-preferred"
    else:
        um_position = "intermediate"

    return {
        "w_predicted_kk": w_pred_kk,
        "w_predicted_frozen_radion": w_pred_frozen,
        "datasets": {
            "planck_bao": {
                "w_central": W_PLANCK_BAO_CENTRAL,
                "w_sigma": W_PLANCK_BAO_SIGMA,
                "sigma_tension": planck_sigma,
                "label": "Planck+BAO",
                "note": "Tightest constraint; prior-dominated (w = const assumed)",
            },
            "desi_dr2_cpl": {
                "w_central": W_DESI_DR2_CPL_W0,
                "w_sigma": W_DESI_DR2_CPL_W0_SIGMA,
                "sigma_tension": desi_cpl_sigma,
                "label": "DESI Y3/DR2 CPL (w₀ free — CORRECT comparison)",
                "note": "Primary comparison; wₐ was free in the DESI fit",
                "is_circular": False,
            },
            "desi_dr2_w0cdm": {
                "w_central": W_DESI_DR2_W0CDM_CENTRAL,
                "w_sigma": W_DESI_DR2_W0CDM_SIGMA,
                "sigma_tension": desi_w0cdm_sigma,
                "label": "DESI Y3/DR2 w₀CDM (wₐ = 0 FORCED — CIRCULAR)",
                "note": (
                    "Circular: DESI assumed wₐ = 0 to get this number; "
                    "UM also has wₐ = 0.  Agreement is not independent. "
                    "The reported 0.11σ 'agreement' is an artifact (Pillar 421 Issue 3)."
                ),
                "is_circular": True,
            },
            "frozen_radion_vs_desi_cpl": {
                "w_central": W_DESI_DR2_CPL_W0,
                "w_sigma": W_DESI_DR2_CPL_W0_SIGMA,
                "sigma_tension": frozen_cpl_sigma,
                "w_predicted": w_pred_frozen,
                "label": "Frozen-radion DE (w₀ = −1) vs DESI CPL",
                "note": "Physically coherent single-mechanism UM prediction",
            },
            "des_y3_planck_bao": {
                "w_central": w_des_y3,
                "w_sigma": sigma_des_y3,
                "sigma_tension": des_sigma,
                "label": "DES Y3+Planck+BAO",
                "note": "Combined weak lensing + BAO",
            },
            "roman_forecast": {
                "w_central": W_ROMAN_FORECAST_CENTRAL,
                "w_sigma": W_ROMAN_FORECAST_SIGMA,
                "sigma_tension": roman_sigma,
                "label": "Roman (~2027, forecast)",
                "note": "σ(w₀) ≈ 0.02 forecast; corroborating instrument",
            },
        },
        "planck_desi_tension": planck_desi_internal,
        "um_position": um_position,
        "discriminant_status": (
            f"w_KK = {w_pred_kk:.4f} (inflationary-epoch formula) is {desi_cpl_sigma:.2f}σ "
            f"from DESI Y3/DR2 CPL w₀ = {W_DESI_DR2_CPL_W0} and {planck_sigma:.2f}σ from "
            f"Planck+BAO.  Planck and DESI disagree internally by "
            f"{planck_desi_internal:.2f}σ on w₀.  "
            f"The frozen-radion coherent UM prediction (w₀ = −1) is "
            f"{frozen_cpl_sigma:.2f}σ from DESI CPL w₀ (joint 2D ~3.9σ). "
            "Roman (~2027, σ(w₀)≈0.02) will serve as a corroborating instrument; "
            "DESI DR3 (late 2026) is the primary upcoming test. "
            "See Pillar 421 for complete corrected tension analysis."
        ),
        "roman_falsifier": (
            f"Roman: σ(w₀) ≈ 0.02. If w₀ measured outside [{w_pred_kk - 0.04:.3f}, "
            f"{w_pred_kk + 0.04:.3f}], inflationary w_KK is under pressure. "
            f"If w₀ measured outside [−1.04, −0.96], frozen-radion DE is under pressure."
        ),
    }


def pillar136_summary() -> Dict[str, object]:
    """Return a structured summary of Pillar 136 closure status.

    Updated by Pillar 421 audit to reflect corrected tension analysis and
    to use the non-circular DESI CPL comparison.

    Returns
    -------
    dict
        Full closure status for documentation and audit tools.
    """
    corrected = kk_eos_corrected()
    tensions = eos_tension_vs_datasets()

    # Correction negligible → w_corrected ≈ w_KK
    correction_negligible = corrected["correction_negligible"]
    w_final = corrected["w_corrected"]

    # Use CPL (non-circular) as primary comparison
    desi_cpl_consistent_2sigma = tensions["desi_dr2_cpl"]["consistent_2sigma"]
    planck_consistent_3sigma = tensions["planck_bao"]["consistent_3sigma"]
    frozen_cpl_sigma = tensions["frozen_radion_vs_desi_cpl"]["sigma_tension"]

    if desi_cpl_consistent_2sigma:
        best_status = (
            "⚠️ HIGH_TENSION — Pillar 421 corrected analysis: "
            f"w_KK (inflationary-epoch) = {W_KK_LEADING:.4f} is "
            f"{tensions['desi_dr2_cpl']['sigma_tension']:.2f}σ from DESI Y3/DR2 CPL w₀. "
            f"Frozen-radion coherent DE (w₀ = −1) is {frozen_cpl_sigma:.2f}σ on w₀ alone "
            "and ~3.9σ joint 2D.  wₐ = 0 vs DESI wₐ = −0.62 is ~2.07σ. "
            "The circular w₀CDM comparison (0.11σ) is no longer reported as validation."
        )
    elif planck_consistent_3sigma:
        best_status = "⚠️ OPEN — within 3σ of Planck+BAO; tension with DESI CPL"
    else:
        best_status = "⚠️ OPEN — TENSION outside 3σ with primary datasets"

    return {
        "pillar": 136,
        "title": "KK Radion Dark Energy — Corrected EoS (Pillar 421 audit applied)",
        "w_leading": W_KK_LEADING,
        "w_leading_scope": (
            "Inflationary-epoch KK zero-mode formula (NOT dark energy today). "
            "Frozen-radion coherent DE prediction: w₀ = −1 (Pillar 421)."
        ),
        "w_corrected": w_final,
        "delta_w": corrected["delta_w"],
        "correction_negligible": correction_negligible,
        "m_r_over_h0": corrected["m_r_over_h0"],
        "tensions": {
            "planck_bao_sigma": tensions["planck_bao"]["sigma_tension"],
            "desi_dr2_cpl_sigma": tensions["desi_dr2_cpl"]["sigma_tension"],
            "desi_dr2_w0cdm_sigma_circular": tensions["desi_dr2_w0cdm"]["sigma_tension"],
            "desi_dr2_w0cdm_is_circular": True,
            "frozen_radion_desi_cpl_sigma": frozen_cpl_sigma,
            "roman_sigma": tensions["roman_forecast"]["sigma_tension"],
        },
        "desi_cpl_consistent_2sigma": desi_cpl_consistent_2sigma,
        "planck_consistent_3sigma": planck_consistent_3sigma,
        "status": best_status,
        "toe_status": (
            f"⚠️ HIGH_TENSION: w_KK(infl) = {tensions['desi_dr2_cpl']['sigma_tension']:.2f}σ "
            f"from DESI Y3/DR2 CPL; frozen-radion DE ~3.9σ joint 2D; "
            f"wₐ = 0 is 2.07σ from DESI wₐ = −0.62. "
            "See Pillar 421 for complete corrected analysis."
        ),
        "falsifier": (
            "DESI DR3 (late 2026, full 5-year data, σ(wₐ)≈0.12): primary test. "
            "Roman Space Telescope (launch ~2027, σ(w₀)≈0.02): corroborating instrument. "
            f"If DR3 wₐ = 0 excluded at >3σ, the frozen-radion wₐ = 0 prediction is falsified."
        ),
        "key_formula": (
            "w_KK = −1 + (2/3) × c_s² = −1 + (2/3) × (12/37)² ≈ −0.9302 "
            "(INFLATIONARY EPOCH; see Pillar 421 Issue 2 for scope limitation)"
        ),
        "pillar421_reference": "Pillar 421 (DESI CPL internal-consistency audit — six-issue correction)",
    }
