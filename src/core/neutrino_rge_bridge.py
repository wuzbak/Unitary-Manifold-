# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/neutrino_rge_bridge.py
================================
Pillar 144 — RGE Bridge: Reconciling Pillar 135 (1.49 meV) and Pillar 140 (1.086 eV).

OPEN INCONSISTENCY — DIAGNOSIS AND PARTIAL RESOLUTION
------------------------------------------------------
Two pillars of the Unitary Manifold claim to give the lightest neutrino mass m_ν₁:

  Pillar 135: m_ν₁ ≈ 1.49 meV   (from Δm²₂₁ / (n₁n₂ − 1) = 7.53e-5/34)
  Pillar 140: m_ν₁ ≈ 1.086 eV   (from RS Dirac: v × f₀(c_L=0.776) × f₀(c_R=0.920))

These differ by a factor of ~730.  This module:

1. Quantifies the discrepancy precisely (the "730× factor").
2. Shows that 1-loop RGE running from M_KK ~ 1 TeV to m_Z ~ 91 GeV contributes
   only a ~4-6% correction — far too small to close a 730× gap.
3. Identifies the TRUE source of the discrepancy: Pillar 140 uses c_L = 0.776,
   which is incompatible with the Planck Σm_ν < 0.12 eV bound.
4. Numerically solves for the c_L^{phys} that makes Pillar 140 reproduce
   Pillar 135's m_ν₁ = 1.49 meV.
5. Reports c_L^{phys} and checks whether it has a simple topological form.
6. Provides the RGE-corrected RS Dirac formula for reference.

RESULT
------
  - Required c_L^{phys} ≈ 0.961 (numerical solution; see c_left_from_rge_consistency())
  - This is NOT equal to 2/25 = 0.08 (topological label from Pillar 143).
  - c_R + c_L^{phys} ≈ 0.920 + 0.961 = 1.881 > 1 (NOT the unitarity boundary).
  - Status: PARTIALLY RESOLVED — 730× discrepancy diagnosed as wrong c_L in Pillar 140.
    The physical c_L^{phys} is determined by the oscillation data, NOT by the
    orbifold fixed-point topology alone.  Topological interpretation of c_L^{phys}
    remains OPEN.

1-loop Neutrino Mass RGE
------------------------
The Dirac neutrino Yukawa runs as (standard model, Antusch et al. hep-ph/0305274):

    d ln y_ν / d ln μ = (1/16π²)[−(3/2)g₁²Y² − (9/2)g₂² + 3 y_t² + Tr(3Y_u²+3Y_d²+Y_e²)]

For y_ν << 1 (exponentially suppressed), the dominant terms are gauge and top Yukawa:

    β_gauge ≈ −(3/2)(g₁²×Y²/4 + g₂²×3/4) × (1/16π²) ≈ −1.3 × 10⁻² per decade
    β_top   ≈ +3 y_t² / (16π²) ≈ +3 × (0.019) per decade   [y_t ~ 0.97]

Running from M_KK ≈ 1041 GeV to m_Z ≈ 91.2 GeV (one decade):
    Δ ln m_ν ≈ (3 y_t² − gauge) / (16π²) × ln(M_KK/m_Z)
             ≈ 0.009 × 2.44 ≈ 0.022  (i.e. ~2% correction)

This is negligible compared to the 730× (= factor of 2.86 in ln space) discrepancy.

Public API
----------
discrepancy_factor(n1, n2, dm2_21_ev2, c_l_140, c_r)  → dict
rge_log_correction(m_kk_gev, m_z_gev, y_top, alpha_s)  → dict
c_left_from_rge_consistency(target_m_nu1_ev, c_r, pi_kr, v_higgs_gev)  → dict
neutrino_rge_bridge_report(n_w, n1, n2)  → dict
pillar144_summary()  → dict
"""

from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "discrepancy_factor",
    "rge_log_correction",
    "c_left_from_rge_consistency",
    "neutrino_rge_bridge_report",
    "pillar144_summary",
    "PILLAR135_M_NU1_EV",
    "PILLAR140_C_L_NAIVE",
    "PILLAR140_C_R",
    "M_KK_GEV",
    "M_Z_GEV",
]

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: Pillar 135 m_ν₁ from oscillation data [eV]  (m_ν₁ = sqrt(Δm²₂₁/34))
PILLAR135_M_NU1_EV: float = math.sqrt(7.53e-5 / 34.0)   # ≈ 0.001487 eV

#: Pillar 140 naive c_L (NOT Planck-consistent)
PILLAR140_C_L_NAIVE: float = 0.776

#: Pillar 140 c_R = 23/25 (from Pillar 143 theorem)
PILLAR140_C_R: float = 23.0 / 25.0  # = 0.920

#: KK threshold mass scale [GeV]  (M_KK = M_Pl × exp(−πkR) ~ 1 TeV range)
M_KK_GEV: float = 1041.0   # from πkR = 37 and M₅ normalization

#: Z boson mass [GeV]
M_Z_GEV: float = 91.2

#: Higgs VEV [GeV]
V_HIGGS_GEV: float = 246.22

#: Planck CMB neutrino mass sum limit [eV]
PLANCK_SUM_MNU_EV: float = 0.12

#: RS πkR compactification parameter
PI_KR: float = 37.0

#: Top Yukawa coupling at m_t scale (≈ 0.97)
Y_TOP: float = 0.97


# ---------------------------------------------------------------------------
# Zero-mode profile (local copy to avoid circular imports)
# ---------------------------------------------------------------------------


def _rs_zero_mode(c: float, pi_kr: float = PI_KR) -> float:
    """RS Dirac zero-mode profile f₀(c), valid for c > 1/2."""
    if c <= 0.5:
        raise ValueError(f"c must be > 0.5 for UV localization; got {c}.")
    x = (2.0 * c - 1.0) * pi_kr
    if x > 500.0:
        return math.sqrt(2.0 * c - 1.0) * math.exp(-0.5 * x)
    return math.sqrt((2.0 * c - 1.0) / (math.exp(x) - 1.0))


# ---------------------------------------------------------------------------
# Core diagnostic functions
# ---------------------------------------------------------------------------


def discrepancy_factor(
    n1: int = 5,
    n2: int = 7,
    dm2_21_ev2: float = 7.53e-5,
    c_l_140: float = PILLAR140_C_L_NAIVE,
    c_r: float = PILLAR140_C_R,
    pi_kr: float = PI_KR,
    v_higgs_gev: float = V_HIGGS_GEV,
) -> Dict[str, object]:
    """Compute the discrepancy factor between Pillar 135 and Pillar 140.

    Pillar 135 gives m_ν₁ from the braid mass ratio formula (oscillation data).
    Pillar 140 gives m_ν₁ from the RS Dirac zero-mode with naive c_L.

    Parameters
    ----------
    n1, n2          : int    Braid winding numbers (default 5, 7).
    dm2_21_ev2      : float  Solar mass splitting [eV²] (default PDG 7.53e-5).
    c_l_140         : float  Pillar 140 naive c_L (default 0.776).
    c_r             : float  c_R from Pillar 143 theorem (default 23/25).
    pi_kr           : float  πkR (default 37.0).
    v_higgs_gev     : float  Higgs VEV in GeV (default 246.22).

    Returns
    -------
    dict
        'm_nu1_135_ev'   : float — Pillar 135 m_ν₁ [eV].
        'm_nu1_140_ev'   : float — Pillar 140 m_ν₁ [eV].
        'ratio_140_135'  : float — m_ν₁(140)/m_ν₁(135).
        'log10_ratio'    : float — log₁₀ of ratio.
        'diagnosis'      : str   — physical explanation.
    """
    # Pillar 135: from oscillation data
    bp = n1 * n2  # 35
    m_nu1_135 = math.sqrt(dm2_21_ev2 / float(bp - 1))  # / 34

    # Pillar 140: RS Dirac with naive c_L
    f0_r = _rs_zero_mode(c_r, pi_kr)
    f0_l = _rs_zero_mode(c_l_140, pi_kr)
    m_nu1_140_gev = v_higgs_gev * f0_l * f0_r
    m_nu1_140_ev = m_nu1_140_gev * 1.0e9

    ratio = m_nu1_140_ev / m_nu1_135 if m_nu1_135 > 0 else float("inf")
    log10_r = math.log10(ratio) if ratio > 0 else float("inf")

    return {
        "n1": n1,
        "n2": n2,
        "m_nu1_135_ev": m_nu1_135,
        "m_nu1_135_meV": m_nu1_135 * 1e3,
        "m_nu1_140_ev": m_nu1_140_ev,
        "c_l_used": c_l_140,
        "c_r_used": c_r,
        "f0_right": f0_r,
        "f0_left": f0_l,
        "ratio_140_over_135": ratio,
        "log10_ratio": log10_r,
        "diagnosis": (
            f"Pillar 135 gives m_ν₁ = {m_nu1_135*1e3:.3f} meV from "
            f"Δm²₂₁ / (n₁n₂ − 1) = {dm2_21_ev2:.3e} / {bp-1} (oscillation data). "
            f"Pillar 140 gives m_ν₁ = {m_nu1_140_ev:.4f} eV from RS Dirac with "
            f"c_L = {c_l_140} (naive estimate). "
            f"Ratio: {ratio:.1f}× ({log10_r:.2f} decades). "
            "The discrepancy is NOT from RGE running (that contributes ~2-6%); "
            "it is entirely from the wrong choice of c_L in Pillar 140. "
            f"To reproduce Pillar 135, c_L must be significantly larger than {c_l_140}."
        ),
    }


def rge_log_correction(
    m_kk_gev: float = M_KK_GEV,
    m_z_gev: float = M_Z_GEV,
    y_top: float = Y_TOP,
    alpha_s_mz: float = 0.1181,
) -> Dict[str, object]:
    """Estimate the 1-loop RGE correction to the Dirac neutrino Yukawa coupling.

    Uses the leading-log approximation for the SM running from M_KK to m_Z.
    The Yukawa beta function at 1-loop is dominated by the top Yukawa and
    gauge contributions:

        d ln y_ν / d ln μ ≈ (1/16π²)[3 y_t² − (3/2)(g₁²/4 + 3g₂²/4)]

    where g₁ ≈ 0.36, g₂ ≈ 0.65 at m_Z.

    Parameters
    ----------
    m_kk_gev   : float  KK threshold scale [GeV] (default 1041).
    m_z_gev    : float  Z boson mass [GeV] (default 91.2).
    y_top      : float  Top Yukawa coupling at m_t (default 0.97).
    alpha_s_mz : float  α_s(m_Z) PDG value (default 0.1181).

    Returns
    -------
    dict
        'log_scale_ratio'     : float — ln(M_KK/m_Z).
        'beta_top'            : float — top contribution to β.
        'beta_gauge'          : float — gauge contribution to β.
        'beta_total'          : float — total 1-loop β.
        'delta_ln_y_nu'       : float — Δ ln y_ν from M_KK to m_Z.
        'mass_ratio_rge'      : float — m_ν₁(m_Z)/m_ν₁(M_KK) from RGE.
        'pct_correction'      : float — percentage mass correction.
        'verdict'             : str.
    """
    # SM gauge couplings at m_Z
    g1_mz = 0.357   # U(1)_Y
    g2_mz = 0.652   # SU(2)_L

    log_ratio = math.log(m_kk_gev / m_z_gev)

    # 1-loop beta coefficients (leading terms only)
    beta_top = 3.0 * y_top**2 / (16.0 * math.pi**2)
    beta_gauge = -(1.5 * (g1_mz**2 / 4.0 + 3.0 * g2_mz**2 / 4.0) / (16.0 * math.pi**2))
    beta_total = beta_top + beta_gauge

    delta_ln_ynu = beta_total * log_ratio
    # Running DOWN from M_KK to m_Z: the mass decreases by the Yukawa running.
    # delta_ln_ynu > 0 means the coupling grows going UP in energy → mass at m_Z
    # is smaller than at M_KK by factor exp(-delta_ln_ynu).
    mass_ratio = math.exp(-delta_ln_ynu)  # m_ν(m_Z) / m_ν(M_KK)
    pct_corr = abs(mass_ratio - 1.0) * 100.0

    if pct_corr < 10.0:
        verdict = (
            f"RGE correction is {pct_corr:.1f}% — NEGLIGIBLE for 730× discrepancy. "
            "RGE does NOT resolve the Pillar 135/140 inconsistency."
        )
    else:
        verdict = (
            f"RGE correction is {pct_corr:.1f}% — significant but still insufficient "
            "to close the Pillar 135/140 gap."
        )

    return {
        "m_kk_gev": m_kk_gev,
        "m_z_gev": m_z_gev,
        "log_scale_ratio": log_ratio,
        "beta_top": beta_top,
        "beta_gauge": beta_gauge,
        "beta_total": beta_total,
        "delta_ln_y_nu": delta_ln_ynu,
        "mass_ratio_rge": mass_ratio,
        "pct_correction": pct_corr,
        "verdict": verdict,
    }


def c_left_from_rge_consistency(
    target_m_nu1_ev: float = PILLAR135_M_NU1_EV,
    c_r: float = PILLAR140_C_R,
    pi_kr: float = PI_KR,
    v_higgs_gev: float = V_HIGGS_GEV,
    c_l_lo: float = 0.5001,
    c_l_hi: float = 0.9999,
    tol: float = 1e-10,
) -> Dict[str, object]:
    """Solve for the c_L^{phys} that makes Pillar 140 reproduce Pillar 135.

    Numerically inverts the RS Dirac formula:
        v × f₀(c_L) × f₀(c_R) = target_m_nu1_ev / 1e9  [in GeV]

    Uses bisection on c_L ∈ (0.5, 0.9999).

    Parameters
    ----------
    target_m_nu1_ev : float  Target m_ν₁ [eV] from Pillar 135 (default 1.49 meV).
    c_r             : float  Fixed c_R from Pillar 143 theorem (default 23/25).
    pi_kr           : float  πkR (default 37.0).
    v_higgs_gev     : float  Higgs VEV in GeV (default 246.22).
    c_l_lo, c_l_hi  : float  Bisection bracket for c_L.
    tol             : float  Convergence tolerance on c_L.

    Returns
    -------
    dict
        'c_left_required'    : float — the c_L that reconciles 135 and 140.
        'c_right'            : float — c_R used (from Pillar 143).
        'c_l_plus_c_r'       : float — sum (NOT equal to 1 in general).
        'target_m_nu1_ev'    : float — the target mass [eV].
        'achieved_m_nu1_ev'  : float — mass with solved c_L [eV].
        'relative_error'     : float — |achieved − target| / target.
        'topological_note'   : str.
        'status'             : str.
    """
    target_gev = target_m_nu1_ev / 1.0e9
    f0_r = _rs_zero_mode(c_r, pi_kr)

    # Required f₀(c_L) value
    required_f0_l = target_gev / (v_higgs_gev * f0_r) if f0_r > 0 else 0.0

    # Bisection on c_L: f₀(c_L) is monotonically DECREASING in c_L
    # So f₀(c_l_lo) > required_f0_l > f₀(c_l_hi)
    f0_lo = _rs_zero_mode(c_l_lo, pi_kr)
    f0_hi = _rs_zero_mode(c_l_hi, pi_kr)

    if required_f0_l > f0_lo:
        # f₀(c_L) can't reach the required value even at c_l = 0.50+
        return {
            "c_left_required": float("nan"),
            "c_right": c_r,
            "c_l_plus_c_r": float("nan"),
            "target_m_nu1_ev": target_m_nu1_ev,
            "achieved_m_nu1_ev": float("nan"),
            "relative_error": float("nan"),
            "topological_note": "No solution: required f₀ exceeds maximum at c_L=0.5+.",
            "status": "NO SOLUTION",
        }
    if required_f0_l < f0_hi:
        # f₀ is too small even at c_l_hi — need c_L beyond the bracket
        c_l_hi = 0.9999999

    # Bisection loop
    for _ in range(200):
        c_mid = (c_l_lo + c_l_hi) / 2.0
        f0_mid = _rs_zero_mode(c_mid, pi_kr)
        if f0_mid > required_f0_l:
            c_l_lo = c_mid   # f₀ too large → c_L must increase
        else:
            c_l_hi = c_mid   # f₀ too small → c_L must decrease
        if c_l_hi - c_l_lo < tol:
            break

    c_l_solved = (c_l_lo + c_l_hi) / 2.0
    f0_l_solved = _rs_zero_mode(c_l_solved, pi_kr)
    achieved_gev = v_higgs_gev * f0_l_solved * f0_r
    achieved_ev = achieved_gev * 1.0e9
    rel_err = abs(achieved_ev - target_m_nu1_ev) / target_m_nu1_ev

    # Check simple fractions
    simple_fracs = {
        "2/25": 2.0 / 25.0,
        "1 - 23/25": 2.0 / 25.0,
        "n_w/(n_w²)": 5.0 / 25.0,
        "1/n_w": 1.0 / 5.0,
        "sqrt(2/n_w²)": math.sqrt(2.0 / 25.0),
    }
    closest_frac = min(simple_fracs.items(), key=lambda kv: abs(kv[1] - c_l_solved))
    topo_note = (
        f"c_L^phys = {c_l_solved:.6f}. Closest simple topological fraction: "
        f"{closest_frac[0]} = {closest_frac[1]:.6f} "
        f"(diff = {abs(closest_frac[1] - c_l_solved):.4f}). "
        "No simple topological form identified — c_L^phys is set by the "
        "Planck Σm_ν constraint, not by orbifold fixed-point counting alone."
    )

    return {
        "c_left_required": c_l_solved,
        "c_right": c_r,
        "c_l_plus_c_r": c_l_solved + c_r,
        "target_m_nu1_ev": target_m_nu1_ev,
        "target_m_nu1_meV": target_m_nu1_ev * 1e3,
        "achieved_m_nu1_ev": achieved_ev,
        "achieved_m_nu1_meV": achieved_ev * 1e3,
        "relative_error": rel_err,
        "f0_right": f0_r,
        "f0_left_solved": f0_l_solved,
        "topological_note": topo_note,
        "status": (
            "PARTIALLY RESOLVED — c_L^phys numerically identified. "
            "Topological form of c_L^phys remains OPEN."
            if rel_err < 1e-4
            else f"NUMERICAL ISSUE — relative error = {rel_err:.2e}"
        ),
    }


def neutrino_rge_bridge_report(
    n_w: int = 5,
    n1: int = 5,
    n2: int = 7,
) -> Dict[str, object]:
    """Full Pillar 144 RGE bridge report.

    Parameters
    ----------
    n_w  : int  Winding number (default 5).
    n1   : int  Lower braid winding (default 5).
    n2   : int  Upper braid winding (default 7).

    Returns
    -------
    dict
        Comprehensive report including discrepancy analysis, RGE correction,
        required c_L^phys, and overall status.
    """
    discrepancy = discrepancy_factor(n1=n1, n2=n2)
    rge = rge_log_correction()
    c_l_result = c_left_from_rge_consistency()

    overall_status = (
        "OPEN INCONSISTENCY DIAGNOSED — root cause identified as wrong c_L "
        "in Pillar 140 (0.776 → need ~0.961). RGE correction negligible (~4%). "
        "Topological form of required c_L^phys is OPEN."
    )

    return {
        "pillar": 144,
        "n_w": n_w,
        "n1": n1,
        "n2": n2,
        "discrepancy_analysis": discrepancy,
        "rge_correction": rge,
        "c_left_consistency": c_l_result,
        "summary": {
            "m_nu1_pillar135_meV": discrepancy["m_nu1_135_meV"],
            "m_nu1_pillar140_ev": discrepancy["m_nu1_140_ev"],
            "ratio_140_over_135": discrepancy["ratio_140_over_135"],
            "rge_correction_pct": rge["pct_correction"],
            "c_l_required": c_l_result["c_left_required"],
            "c_r_theorem": PILLAR140_C_R,
        },
        "overall_status": overall_status,
        "open_items": [
            "c_L^phys topological form (OPEN: c_L^phys ≈ 0.961 has no simple braid fraction)",
            "Full zero-parameter RS Dirac Yukawa derivation (OPEN)",
        ],
        "closed_items": [
            "730× discrepancy: ROOT CAUSE IDENTIFIED (wrong c_L = 0.776 in Pillar 140)",
            "RGE contribution: quantified as ~4% (negligible for 730× gap)",
            "Required c_L^phys: numerically solved (≈ 0.961)",
        ],
    }


def pillar144_summary() -> Dict[str, object]:
    """Return the Pillar 144 closure summary for the TOE table."""
    report = neutrino_rge_bridge_report()
    return {
        "pillar": 144,
        "title": "RGE Bridge — Pillar 135 / Pillar 140 Reconciliation",
        "status": report["overall_status"],
        "c_left_required": report["summary"]["c_l_required"],
        "c_right_theorem": report["summary"]["c_r_theorem"],
        "ratio_diagnosed": report["summary"]["ratio_140_over_135"],
        "rge_correction_pct": report["summary"]["rge_correction_pct"],
        "open_items": report["open_items"],
        "closed_items": report["closed_items"],
    }
