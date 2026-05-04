# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_de_wa_cpl.py
==========================
Pillar 155 — KK Dark Energy wₐ from Radion Potential Evolution (CPL Analysis).

STATUS: ⚠️ OPEN (from Pillar 151 'remaining_open') → ⚠️ ANALYSED — UM gives
        wₐ ≈ 0 (stationary); DESI DR2 prefers wₐ ≈ −0.62. Tension documented.

CONTEXT FROM PILLAR 151
-----------------------
Pillar 151 (de_equation_of_state_desi.py) established that the UM prediction
w_KK = −0.9302 is within 1.3σ of the DESI DR2 2025 central value w₀ = −0.838.

However, Pillar 151 "remaining_open" explicitly states:

    "The wₐ parameter (time evolution of w) is currently zero in the UM
    (w = constant).  DESI DR2 prefers wₐ < 0 (darkening DE).  The UM
    single-component KK zero-mode gives constant w_KK — this is a remaining
    discrepancy with DESI DR2 CPL fit."

This Pillar 155 provides the systematic analysis of wₐ from the KK radion
potential, following the CPL (Chevallier-Polarski-Linder) parametrisation:

    w(a) = w₀ + wₐ(1 − a)   where a = 1/(1+z) is the scale factor.

RADION AS QUINTESSENCE: GOLDBERGER-WISE POTENTIAL
---------------------------------------------------
The Goldberger-Wise (GW) stabilisation mechanism generates a potential for
the radion field φ (the 4D effective field describing fluctuations of the
compactification radius R):

    V(φ) ≈ V₀ × [1 + ε_GW × (φ/φ₀ − 1)² + O(ε_GW²)]

where:
  V₀ = vacuum energy density ≈ H₀² M_Pl²   (tuned to observed Λ)
  φ₀ = stabilised GW minimum
  ε_GW = GW perturbation parameter ~ (m_r/H_inf)² × (k²/M_Pl²) << 1

The GW radion mass in 4D units:
    m_r² = 2 ε_GW V₀ / φ₀² = ε_GW H₀² M_Pl² / φ₀²

For the KK dark energy sector (NOT the EW sector; the EW radion has m_r >> H₀
and decouples completely from dark energy dynamics):

CASE: COSMOLOGICAL RADION (m_r comparable to H₀)
-------------------------------------------------
If m_r ~ n × H₀ with n ≥ 1, the radion evolves on cosmological timescales.
For n >> 1, the field oscillates rapidly → acts as dark matter, not dark energy.
For n = O(1), the field evolves slowly → quintessence.

The slow-roll quintessence EoS for a potential V(φ) near its minimum:

    w ≈ −1 + (φ̇²/2) / V(φ)

For a massive field near its minimum with m_r = n H₀:
    φ̇² / (2V) ≈ (m_r/H)² × (Δφ/M_Pl)²   [from slow-roll equations]

    → 1 + w ≈ (m_r/H)² × (Δφ/M_Pl)²

where Δφ = φ − φ₀ is the displacement from the GW minimum.

COMPUTING wₐ FROM SLOW-ROLL EVOLUTION
---------------------------------------
The CPL parameter wₐ parametrises the evolution of w(a) with the scale factor:

    wₐ = −dw/da |_{a=1}

For a quintessence field rolling down the GW potential from an initial
displacement Δφ_i at z_i = 2 (a_i = 1/3) to z = 0 (a = 1):

    1 + w(a) = (m_r/H(a))² × (Δφ(a)/M_Pl)²

The slow-roll evolution:
    dΔφ/da ≈ −(m_r/H)² × Δφ × (1/H)  [slow-roll equation of motion]

For a cosmological constant background H ≈ H₀ (late-time de Sitter):
    Δφ(a) ≈ Δφ_i × exp(−(m_r/H₀)² × (a − a_i) / (3H₀a³/²))

[Leading order slow roll approximation valid for m_r < 3H₀]

The key result: for the GW-stabilised radion at m_r >> H₀ (as in the RS/UM
framework with M_KK = 1 TeV >> H₀ ~ 10⁻³³ eV):

    1 + w ≈ 0   to extremely high precision (field is frozen at φ₀)
    wₐ ≈ 0

This confirms: the UM KK zero-mode gives w_KK = −0.9302 EXACTLY CONSTANT
with wₐ = 0 (to precision << 10⁻⁸⁰).

THE TENSION WITH DESI DR2
--------------------------
DESI DR2 (CPL parametrisation, BAO + CMB + SNe):
    w₀ = −0.838 ± 0.072
    wₐ = −0.62 ± 0.30   [84 < ΔN_eff < 250 approximation; ~2σ from wₐ = 0]

The UM gives:
    w₀ = w_KK = −0.9302  [within 1.3σ of DESI w₀ ✅]
    wₐ = 0               [2.1σ from DESI wₐ = −0.62 ± 0.30 ⚠️]

The wₐ tension is GENUINE and cannot be resolved by the single-component
KK zero-mode (the GW stabilisation freezes the radion at m_r >> H₀).

RESOLUTION PATHS
----------------
1. Multi-component KK spectrum: Higher KK modes contribute to the effective DE
   density with a spectrum of effective w values. The time-weighted average could
   produce a small effective wₐ. Not computed in current UM.

2. KK mode summation: Summing over KK tower modes n = 1, 2, 3, ... with
   masses m_n = n × M_KK × e^{-πkR} produces an effective wₐ from the
   differential rolling of modes. Preliminary estimate: wₐ^{KK} ~ O(e^{-2πkR}).
   This is exponentially small (< 10⁻³²) and cannot explain DESI wₐ.

3. Quintessence from a different geometric sector: A bulk field in the RS
   geometry distinct from the radion could generate dynamical DE. This is
   outside the current UM 5D action and would require extending the model.

STATUS: wₐ = 0 is the UM prediction. The ~2.1σ tension with DESI DR2 wₐ is
documented as an HONEST OPEN PROBLEM. The KK multi-mode correction gives
|wₐ^{KK}| < 10⁻³² — far too small to explain DESI. Full resolution requires
a new geometric sector or a multi-component KK analysis.

Public API
----------
um_cpl_w0() → float
    UM prediction w₀ = w_KK = −1 + (2/3) c_s².

um_cpl_wa() → float
    UM prediction wₐ = 0 (frozen radion).

kk_wa_from_multi_mode(n_modes, m_kk_gev, h0_gev) → dict
    Estimate wₐ contribution from KK tower summation (schematic).

gw_radion_wa_slow_roll(m_r_over_h0, delta_phi_over_mpl, a_i, a_f) → dict
    Compute wₐ from GW radion slow-roll evolution between scale factors a_i and a_f.

cpl_tension_analysis() → dict
    Sigma-tension of (w₀, wₐ)_UM vs DESI DR2 CPL constraints.

pillar155_summary() → dict
    Structured Pillar 155 closure summary.
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

#: Braided sound speed c_s = 12/37 (Pillar 15-B)
C_S_BRAIDED: float = 12.0 / 37.0

#: UM dark energy EoS w₀ = w_KK = −1 + (2/3) c_s²
W_KK: float = -1.0 + (2.0 / 3.0) * C_S_BRAIDED ** 2

#: UM wₐ prediction (frozen radion: wₐ = 0 exactly)
W_A_UM: float = 0.0

#: RS geometry parameter πkR (Pillar 81)
PI_KR: float = 37.0

#: EW KK mass scale [GeV] (RS hierarchy: M_KK ≈ M_Pl × exp(−πkR))
M_PLANCK_GEV: float = 1.22089e19
M_KK_EW_GEV: float = M_PLANCK_GEV * math.exp(-PI_KR)  # ≈ 1 TeV

#: Hubble constant today H₀ [GeV]
H0_GEV: float = 2.184e-42  # 67.4 km/s/Mpc in natural units

#: DESI DR2 CPL constraints (BAO + CMB + SNe, arXiv:2503.14738)
DESI_DR2_W0: float = -0.838
DESI_DR2_W0_SIGMA: float = 0.072
DESI_DR2_WA: float = -0.62
DESI_DR2_WA_SIGMA: float = 0.30

#: Planck 2018 + BAO (old comparison; superseded by DESI DR2)
PLANCK_BAO_W: float = -1.03
PLANCK_BAO_W_SIGMA: float = 0.03

#: DESI DR2 reference
DESI_DR2_REF: str = "DESI Collaboration (2025), arXiv:2503.14738, DESI DR2 Key Paper"

#: GW coupling (natural units)
LAMBDA_GW: float = 1.0

#: Warp suppression factor for KK multi-mode wₐ estimate
_WARP_FACTOR: float = math.exp(-PI_KR)  # e^{-37} ≈ 8.5×10⁻¹⁷

#: Effective initial displacement scale (Δφ/M_Pl at high z)
DELTA_PHI_OVER_MPL_DEFAULT: float = 0.01  # conservative, sub-Planckian

#: Redshift range for wₐ integration (DESI window z = 0 to 2)
Z_DESI_MIN: float = 0.0
Z_DESI_MAX: float = 2.0
A_DESI_MIN: float = 1.0 / (1.0 + Z_DESI_MAX)   # a = 1/3
A_DESI_MAX: float = 1.0 / (1.0 + Z_DESI_MIN)    # a = 1


# ---------------------------------------------------------------------------
# UM CPL predictions
# ---------------------------------------------------------------------------

def um_cpl_w0() -> float:
    """Return the UM prediction for the CPL w₀ parameter.

    The UM dark energy equation of state from the braided KK zero-mode:
        w₀ = w_KK = −1 + (2/3) c_s²   with c_s = 12/37

    This is the leading-order slow-roll result for the KK zero-mode acting
    as a quintessence-like field (Pillar 136).

    Returns
    -------
    float
        w₀ = W_KK ≈ −0.9302.
    """
    return W_KK


def um_cpl_wa() -> float:
    """Return the UM prediction for the CPL wₐ parameter.

    The GW-stabilised radion has mass m_r >> H₀ (for M_KK = 1 TeV and
    H₀ ≈ 10⁻³³ eV, the ratio m_r/H₀ ≈ 10⁶⁰).  A frozen radion at its
    GW minimum gives w = const = w_KK everywhere → wₐ = 0 exactly.

    Returns
    -------
    float
        wₐ = 0.0 (frozen radion, to precision << 10⁻⁸⁰).
    """
    return W_A_UM


# ---------------------------------------------------------------------------
# GW radion slow-roll wₐ computation
# ---------------------------------------------------------------------------

def gw_radion_wa_slow_roll(
    m_r_over_h0: float,
    delta_phi_over_mpl: float = DELTA_PHI_OVER_MPL_DEFAULT,
    a_i: float = A_DESI_MIN,
    a_f: float = A_DESI_MAX,
) -> Dict[str, object]:
    """Compute wₐ from GW radion slow-roll evolution.

    For a radion with mass m_r = (m_r_over_h0) × H₀ rolling from initial
    displacement Δφ = delta_phi_over_mpl × M_Pl, the leading-order
    slow-roll contribution to wₐ in the CPL parametrisation is:

        1 + w(a) ≈ (m_r/H₀)² × (Δφ(a)/M_Pl)²   [near potential minimum]

        wₐ = −d(w+1)/d(1−a)|_{a=1}

    For m_r >> H₀ (frozen field: Δφ(a) ≈ const):
        1 + w ≈ const → wₐ ≈ 0

    For m_r ~ H₀ (quintessence regime):
        The field rolls significantly over the DESI redshift window.

    Parameters
    ----------
    m_r_over_h0       : float  Radion mass in units of H₀ (must be > 0).
    delta_phi_over_mpl: float  Initial field displacement Δφ/M_Pl (default 0.01).
    a_i               : float  Initial scale factor (default 1/3, z=2).
    a_f               : float  Final scale factor (default 1.0, z=0).

    Returns
    -------
    dict
        wₐ, w₀, regime classification, and derivation details.

    Raises
    ------
    ValueError
        If m_r_over_h0 ≤ 0, delta_phi_over_mpl < 0, a_i ≤ 0, or a_f ≤ a_i.
    """
    if m_r_over_h0 <= 0:
        raise ValueError(f"m_r_over_h0 must be positive; got {m_r_over_h0}.")
    if delta_phi_over_mpl < 0:
        raise ValueError(f"delta_phi_over_mpl must be non-negative; got {delta_phi_over_mpl}.")
    if a_i <= 0:
        raise ValueError(f"a_i must be positive; got {a_i}.")
    if a_f <= a_i:
        raise ValueError(f"a_f = {a_f} must be greater than a_i = {a_i}.")

    n = m_r_over_h0

    # Classify regime based on m_r/H₀.
    # The slow-roll approximation (quintessence) requires m_r < 3H₀ (n < 3).
    # For n > 3: the field is NOT in slow roll → it either oscillates rapidly
    # (dark matter-like, w ≈ 0) or is frozen at its GW minimum (w = −1, wₐ = 0).
    #
    # In the GW-stabilised radion scenario, the field sits at its minimum with
    # Δφ_initial ≈ 0 → w = −1 exactly, wₐ = 0 for ALL n > 3.
    #
    # Slow-roll formula (valid only for n < 3):
    #   1 + w(a) ≈ (n²/9) × (Δφ(a)/M_Pl)²
    #   Δφ(a) decays as Δφ_i × exp(−n² × (a − a_i) / 3)   [de Sitter slow roll]

    if n > 3.0:
        # Frozen / oscillating regime: slow-roll formula does not apply.
        # For GW-stabilised radion at its minimum: Δφ ≈ 0 → w = −1 → wₐ = 0.
        one_plus_w_i = 0.0
        one_plus_w_f = 0.0
        exponent_f = float('-inf')
    else:
        # Slow-roll regime: 1+w ≈ (n²/9) × (Δφ/M_Pl)²
        exponent_f = -(n ** 2) * (a_f - a_i) / 3.0
        if exponent_f < -700.0:
            delta_phi_f_over_mpl = 0.0
        else:
            delta_phi_f_over_mpl = delta_phi_over_mpl * math.exp(exponent_f)
        one_plus_w_i = (n ** 2 / 9.0) * delta_phi_over_mpl ** 2
        one_plus_w_f = (n ** 2 / 9.0) * delta_phi_f_over_mpl ** 2

    w_at_a_i = -1.0 + one_plus_w_i
    w_at_a_f = -1.0 + one_plus_w_f

    # CPL: w(a) = w₀ + wₐ(1 − a)
    # At a = a_f ≈ 1: w₀ ≈ w(a=1) = w_at_a_f
    # At a = a_i: w(a_i) = w₀ + wₐ(1 − a_i)
    # → wₐ = (w(a_i) − w₀) / (1 − a_i)
    w0_cpl = w_at_a_f
    if abs(1.0 - a_i) > 1e-12:
        wa_cpl = (w_at_a_i - w0_cpl) / (1.0 - a_i)
    else:
        wa_cpl = 0.0

    # Classify regime
    if n > 1e3:
        regime = "FROZEN (m_r >> H₀): field is frozen at GW minimum → wₐ = 0"
    elif n > 3.0:
        regime = "OSCILLATING (m_r > 3H₀): slow-roll fails → w averaged to 0 or −1"
    elif n > 1.0:
        regime = "TRANSITION (H₀ < m_r < 3H₀): near slow-roll boundary"
    else:
        regime = "ROLLING (m_r < H₀): quintessence regime — significant wₐ"

    return {
        "m_r_over_h0": m_r_over_h0,
        "delta_phi_over_mpl": delta_phi_over_mpl,
        "a_i": a_i,
        "a_f": a_f,
        "one_plus_w_at_a_i": one_plus_w_i,
        "one_plus_w_at_a_f": one_plus_w_f,
        "w_at_a_i": w_at_a_i,
        "w_at_a_f": w_at_a_f,
        "w0_cpl": w0_cpl,
        "wa_cpl": wa_cpl,
        "regime": regime,
        "frozen": n > 3.0,
        "exponent_for_phi_decay": exponent_f,
        "slow_roll_valid": n <= 3.0,
        "conclusion": (
            f"m_r = {m_r_over_h0:.2e} × H₀. "
            f"Slow-roll valid (n ≤ 3): {n <= 3.0}. "
            f"Δφ/M_Pl = {delta_phi_over_mpl:.3e}. "
            f"w(z=2) = {w_at_a_i:.4f}, w(z=0) = {w_at_a_f:.4f}. "
            f"CPL: w₀ = {w0_cpl:.4f}, wₐ = {wa_cpl:.4e}. "
            f"Regime: {regime.split(':')[0]}."
        ),
    }


# ---------------------------------------------------------------------------
# KK multi-mode wₐ estimate
# ---------------------------------------------------------------------------

def kk_wa_from_multi_mode(
    n_modes: int = 3,
    m_kk_gev: float = M_KK_EW_GEV,
    h0_gev: float = H0_GEV,
) -> Dict[str, object]:
    """Estimate wₐ contribution from KK tower mode summation (schematic).

    The KK tower has modes m_n = n × M_KK^{eff} (n = 1, 2, 3, ...).
    Each mode contributes to the effective DE density with a slightly
    different equation of state. The time-averaged contribution gives a
    schematic wₐ estimate.

    For M_KK >> H₀ (as in the RS1 model): each mode is frozen with
    m_n/H₀ >> 1, and the effective wₐ from mode n is suppressed by
    (H₀/m_n)^N where N >> 1.

    Leading estimate:
        wₐ^{KK} ~ (H₀/M_KK)² × (some_geometric_factor)

    Parameters
    ----------
    n_modes  : int    Number of KK modes to sum (default 3).
    m_kk_gev : float  KK mass scale [GeV] (default EW KK scale ≈ 1 TeV).
    h0_gev   : float  Hubble constant today [GeV] (default 2.184×10⁻⁴² GeV).

    Returns
    -------
    dict
        Schematic wₐ estimate from KK mode summation.

    Raises
    ------
    ValueError
        If n_modes < 1, m_kk_gev ≤ 0, or h0_gev ≤ 0.
    """
    if n_modes < 1:
        raise ValueError(f"n_modes must be at least 1; got {n_modes}.")
    if m_kk_gev <= 0:
        raise ValueError(f"m_kk_gev must be positive; got {m_kk_gev}.")
    if h0_gev <= 0:
        raise ValueError(f"h0_gev must be positive; got {h0_gev}.")

    ratio = h0_gev / m_kk_gev  # H₀/M_KK << 1

    # Each mode n contributes wₐ_n ~ (H₀/m_n)² = (H₀/(n × M_KK))²
    # Sum: wₐ^{KK} ~ (H₀/M_KK)² × Σ(1/n²) ~ (H₀/M_KK)² × π²/6
    mode_contributions = []
    wa_total = 0.0
    for n in range(1, n_modes + 1):
        wa_n = ratio ** 2 / n ** 2
        wa_total += wa_n
        mode_contributions.append({
            "mode_n": n,
            "m_n_gev": n * m_kk_gev,
            "m_n_over_h0": n * m_kk_gev / h0_gev,
            "wa_n_schematic": wa_n,
        })

    # Log10 of ratio for display
    log10_ratio = math.log10(ratio) if ratio > 0 else float('-inf')
    log10_wa = math.log10(abs(wa_total)) if wa_total > 0 else float('-inf')

    return {
        "n_modes": n_modes,
        "m_kk_gev": m_kk_gev,
        "h0_gev": h0_gev,
        "h0_over_m_kk": ratio,
        "log10_h0_over_m_kk": log10_ratio,
        "wa_kk_total_schematic": wa_total,
        "log10_wa_kk": log10_wa,
        "mode_contributions": mode_contributions,
        "sufficient_for_desi": abs(wa_total) > abs(DESI_DR2_WA) * 0.01,
        "conclusion": (
            f"KK multi-mode wₐ estimate for {n_modes} modes: "
            f"|wₐ^{{KK}}| ~ (H₀/M_KK)² = {ratio:.2e}² ~ {wa_total:.2e}. "
            f"DESI DR2 requires |wₐ| ≈ {abs(DESI_DR2_WA):.2f}. "
            f"KK multi-mode wₐ is {abs(DESI_DR2_WA) / max(wa_total, 1e-300):.2e}× "
            f"too small to explain DESI. "
            "KK tower summation cannot resolve the wₐ tension."
        ),
    }


# ---------------------------------------------------------------------------
# Full CPL tension analysis
# ---------------------------------------------------------------------------

def cpl_tension_analysis() -> Dict[str, object]:
    """Compute sigma-tension of UM (w₀, wₐ) vs DESI DR2 CPL constraints.

    Returns
    -------
    dict
        Full tension analysis including w₀ and wₐ components.
    """
    w0_um = um_cpl_w0()
    wa_um = um_cpl_wa()

    # w₀ tension vs DESI DR2
    tension_w0 = abs(w0_um - DESI_DR2_W0) / DESI_DR2_W0_SIGMA
    consistent_w0 = tension_w0 < 2.0

    # wₐ tension vs DESI DR2
    tension_wa = abs(wa_um - DESI_DR2_WA) / DESI_DR2_WA_SIGMA
    consistent_wa = tension_wa < 2.0

    # w₀ tension vs Planck+BAO (old)
    tension_w0_planck = abs(w0_um - PLANCK_BAO_W) / PLANCK_BAO_W_SIGMA

    # Combined chi-squared (assuming diagonal covariance, approximate)
    chi_sq_desi = tension_w0 ** 2 + tension_wa ** 2
    tension_combined = math.sqrt(chi_sq_desi)

    # KK multi-mode wₐ estimate
    kk_wa = kk_wa_from_multi_mode()

    # GW radion wₐ for the EW radion (completely frozen)
    gw_radion = gw_radion_wa_slow_roll(M_KK_EW_GEV / H0_GEV)

    return {
        "um_prediction": {
            "w0": w0_um,
            "wa": wa_um,
            "c_s_braided": C_S_BRAIDED,
            "mechanism": "w₀ = −1 + (2/3)c_s²; wₐ = 0 (frozen radion at m_r >> H₀)",
        },
        "desi_dr2_constraint": {
            "w0_central": DESI_DR2_W0,
            "w0_sigma": DESI_DR2_W0_SIGMA,
            "wa_central": DESI_DR2_WA,
            "wa_sigma": DESI_DR2_WA_SIGMA,
            "reference": DESI_DR2_REF,
        },
        "tension_w0_desi": {
            "tension_sigma": tension_w0,
            "consistent": consistent_w0,
            "status": "CONSISTENT ✅" if consistent_w0 else f"TENSION {tension_w0:.1f}σ ⚠️",
        },
        "tension_wa_desi": {
            "tension_sigma": tension_wa,
            "consistent": consistent_wa,
            "status": "CONSISTENT ✅" if consistent_wa else f"TENSION {tension_wa:.1f}σ ⚠️",
            "note": (
                f"UM predicts wₐ = 0 (frozen radion). "
                f"DESI DR2: wₐ = {DESI_DR2_WA} ± {DESI_DR2_WA_SIGMA}. "
                f"Tension: {tension_wa:.1f}σ."
            ),
        },
        "tension_w0_planck_bao": {
            "dataset": "Planck 2018 + BAO",
            "tension_sigma": tension_w0_planck,
            "note": "Old comparison; Planck+BAO assumes w = const = −1 (ΛCDM prior)",
        },
        "combined_tension_desi": {
            "chi_sq": chi_sq_desi,
            "combined_sigma": tension_combined,
            "note": "Approximate, assuming diagonal covariance in (w₀, wₐ) plane",
        },
        "kk_multimode_wa": kk_wa,
        "gw_radion_ew_sector": gw_radion,
        "summary": (
            f"UM CPL: w₀ = {w0_um:.4f}, wₐ = {wa_um:.1f}. "
            f"DESI DR2: w₀ = {DESI_DR2_W0} ± {DESI_DR2_W0_SIGMA}, "
            f"wₐ = {DESI_DR2_WA} ± {DESI_DR2_WA_SIGMA}. "
            f"w₀ tension: {tension_w0:.1f}σ ({'✅' if consistent_w0 else '⚠️'}). "
            f"wₐ tension: {tension_wa:.1f}σ ({'✅' if consistent_wa else '⚠️'}). "
            "The wₐ = 0 prediction is genuine: the GW-frozen radion cannot evolve "
            "over cosmological timescales. KK multi-mode correction: |wₐ^{KK}| ~ "
            f"{kk_wa['wa_kk_total_schematic']:.2e} — negligible. "
            "wₐ tension with DESI is an HONEST OPEN PROBLEM."
        ),
    }


# ---------------------------------------------------------------------------
# Pillar 155 summary
# ---------------------------------------------------------------------------

def pillar155_summary() -> Dict[str, object]:
    """Structured Pillar 155 closure summary for audit tools.

    Returns
    -------
    dict
        Structured summary with (w₀, wₐ) UM predictions and tensions.
    """
    tensions = cpl_tension_analysis()
    kk_wa = tensions["kk_multimode_wa"]

    return {
        "pillar": 155,
        "title": "KK Dark Energy wₐ from Radion Potential Evolution (CPL Analysis)",
        "previous_status": "⚠️ OPEN (documented in Pillar 151 'remaining_open')",
        "new_status": "⚠️ ANALYSED — wₐ = 0 (UM prediction); ~2.1σ tension with DESI",
        "um_w0": W_KK,
        "um_wa": W_A_UM,
        "desi_dr2_w0": DESI_DR2_W0,
        "desi_dr2_wa": DESI_DR2_WA,
        "tension_w0_sigma": tensions["tension_w0_desi"]["tension_sigma"],
        "tension_wa_sigma": tensions["tension_wa_desi"]["tension_sigma"],
        "w0_consistent_with_desi": tensions["tension_w0_desi"]["consistent"],
        "wa_consistent_with_desi": tensions["tension_wa_desi"]["consistent"],
        "kk_multimode_wa_schematic": kk_wa["wa_kk_total_schematic"],
        "kk_correction_negligible": not kk_wa["sufficient_for_desi"],
        "mechanism": (
            "c_s = 12/37 → w₀ = w_KK = −0.9302. "
            "GW-stabilised radion at m_r = M_KK ≈ 1 TeV >> H₀ → frozen field → wₐ = 0. "
            f"KK multi-mode correction: |wₐ^{{KK}}| ~ {kk_wa['wa_kk_total_schematic']:.2e} ≈ 0."
        ),
        "open_problem": (
            "wₐ = 0 is the honest UM prediction. "
            f"DESI DR2 requires wₐ = {DESI_DR2_WA} ± {DESI_DR2_WA_SIGMA}. "
            f"Tension: ~{tensions['tension_wa_desi']['tension_sigma']:.1f}σ. "
            "Resolution requires a new geometric sector in the 5D UM action "
            "(e.g., bulk quintessence field distinct from the GW radion) — "
            "outside the current UM single-component KK zero-mode description."
        ),
        "pillar_references": [
            "Pillar 136 (KK radion dark energy, w_KK computation)",
            "Pillar 147 (DE radion eliminated by fifth-force)",
            "Pillar 151 (DESI DR2 reconciliation; wₐ open problem documented)",
            "Pillar 81 (RS geometry, πkR = 37, M_KK scale)",
            "DESI DR2 (2025, arXiv:2503.14738)",
        ],
    }
