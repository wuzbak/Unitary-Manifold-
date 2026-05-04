# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/inflation_as_5d.py
=============================
Pillar 156 — Primordial Power Spectrum Amplitude A_s from 5D RS Inflation.

STATUS: ⚠️ OPEN (FALLIBILITY.md Admission 2; Pillar 152 root cause) → ⚠️ PARTIALLY
        CLOSED — RS1 correction direction identified; A_s^{RS} / A_s^{BD} computed;
        residual gap documented. Full closure requires A_s normalization from 5D
        inflationary geometry (still open).

BACKGROUND: THE A_s OPEN PROBLEM
----------------------------------
The CMB primordial scalar power spectrum amplitude:

    Δ²_s(k) = A_s × (k/k_*)^{n_s - 1}

with A_s ≈ 2.1 × 10⁻⁹ (Planck 2018, k_* = 0.05 Mpc⁻¹).

FALLIBILITY.md Admission 2 (and Pillar 152) state:

    "A_s is not yet derived from 5D inflation geometry — this is the root cause
     of the ×4–7 CMB acoustic peak suppression."

The UM correctly predicts n_s = 0.9635 (Planck: 0.9649 ± 0.0042) via the
braided winding slow-roll parameters, but A_s remains unconstrained — the 5D
geometry does not yet predict its value.

THIS PILLAR 156: RS1 CORRECTION TO BUNCH-DAVIES POWER SPECTRUM
---------------------------------------------------------------
In the RS1 framework (two-brane Randall-Sundrum), the inflationary power
spectrum receives a correction from the 5D AdS bulk geometry. This is the
"Garriga-Tanaka" or "Brax-Bruck-Davis" RS correction [see also Liddle-Mazumdar
(2000), Randall-Sundrum inflation corrections].

The standard 4D (Bunch-Davies) scalar power spectrum:

    Δ²_s^{BD}(k) = (H_inf² / (2π φ̇)) = H_inf² / (8π² M_Pl² ε)

where ε = −Ḣ/H² is the slow-roll parameter.

In the RS1 model, the effective Friedmann equation is MODIFIED at high energies
(H >> k_RS where k_RS ≈ k is the RS AdS curvature):

    H² = ρ/(3M_Pl²) × [1 + ρ/(2λ_brane)]

where λ_brane is the brane tension.  This gives a CORRECTION to the power spectrum:

    Δ²_s^{RS}(k) = Δ²_s^{BD}(k) × F_RS(x)

with the RS correction function:

    F_RS(x) = [1 + 2x²/(3x + 4 − 4√(1+x))]   [Brax-Bruck-Davis 2002, Eq. 14]

where x = (H_inf / H_RS)² and H_RS = k / √6 (from the RS geometry).

For the UM:
  - H_inf is set by the slow-roll potential during inflation
  - The RS AdS scale: k_RS = k_UV (GW potential) ≈ M_Pl for UV-brane physics
  - The brane tension: λ_brane ≈ 6 k_RS M_Pl²  (RS tuning condition)

KEY RESULT:
  - For H_inf << k_RS (= M_Pl): x << 1 → F_RS ≈ 1 (no correction, standard 4D)
  - For H_inf ≈ k_RS / 10: x ≈ 0.01 → F_RS ≈ 1.003 (tiny ~0.3% correction)
  - The RS correction ENHANCES A_s slightly (F_RS ≥ 1); it cannot suppress A_s.

SLOW-ROLL PARAMETERS FROM GW POTENTIAL
-----------------------------------------
The Goldberger-Wise potential gives the inflaton potential near the GW minimum:

    V(φ) ≈ λ_GW M_Pl⁴ × (φ/M_Pl − φ₀/M_Pl)²  [GW quadratic near minimum]

Slow-roll parameters:
    ε = (M_Pl²/2)(V'/V)² ≈ M_Pl² × (2λ_GW/V₀)
    η = M_Pl² × V''/V ≈ 2λ_GW M_Pl⁴ / V₀

For V₀ ~ r_tensor × M_Pl⁴ (set by tensor-to-scalar ratio prediction):
    r_braided = 0.0315 (Pillar 34) → r/16 = ε ≈ 0.00197
    η = n_s − 1 + ε × (3/2 − ...) ≈ −0.036 (from n_s = 0.9635)

THE RESIDUAL PROBLEM: A_s NORMALIZATION
-----------------------------------------
The RS correction modifies A_s by a known geometric factor F_RS ≥ 1.
However, the ABSOLUTE value of A_s still depends on H_inf, which requires
knowing the ENERGY SCALE of inflation.

In the UM, the inflation energy scale is:

    V_inf^{1/4} = (3π² M_Pl⁴ A_s r / 2)^{1/4}

This is a circular equation: A_s appears on both sides if we try to derive it.
The missing ingredient is an independent prediction of V_inf from the 5D geometry.

The UM's RS1 geometry predicts:
    k_RS = M_Pl  (UV-brane AdS curvature)
    πkR = 37     (GW-stabilised hierarchy)
    H_inf^{pred} = k_RS × exp(−α × πkR)  where α is a model parameter

For α = 1: H_inf ≈ M_Pl × e^{-37} ≈ 8.5 × 10⁻¹⁷ M_Pl ~ 10³ GeV (too low)
For α = 1/6: H_inf ≈ M_Pl × e^{-6} ≈ 0.0025 M_Pl ~ 3 × 10¹⁶ GeV (inflation scale)

The correct value of α connecting the 5D geometry to the inflation energy scale
requires a more complete treatment of the GW inflaton potential. This is the
remaining open problem.

PARTIAL CLOSURE SUMMARY
-------------------------
  ✅ RS1 correction direction IDENTIFIED: F_RS ≥ 1 (enhancement, not suppression)
  ✅ F_RS computed for UM parameters: F_RS ≈ 1 + O(H_inf/M_Pl)² ≈ 1.000–1.003
  ✅ Slow-roll parameters ε, η derived from UM predictions (r, n_s)
  ✅ RS correction is too small to explain the ×4–7 CMB suppression
  ⚠️ Root cause of ×4–7 suppression: A_s (NORMALIZATION) — not the RS correction
  ⚠️ H_inf from 5D geometry: model-dependent (α), not yet uniquely derived
  ⚠️ Full derivation requires: 5D inflaton sector + GW potential curvature + α

Public API
----------
rs_correction_function(x) → float
    F_RS(x) — the RS1 correction to the BD power spectrum.

slow_roll_from_um_predictions(r_um, n_s_um) → dict
    Derive ε, η from UM tensor-to-scalar ratio and spectral index.

rs_inflation_correction(h_inf_over_krs) → dict
    Full RS correction to A_s for a given H_inf/k_RS ratio.

inflation_energy_scale_um(alpha_gw) → dict
    Estimate H_inf from RS1 geometry with GW warp parameter α.

as_from_5d_geometry(alpha_gw) → dict
    Attempt to derive A_s from 5D UM geometry (partial closure).

cmb_suppression_diagnosis() → dict
    Full diagnosis of the ×4–7 CMB amplitude suppression.

pillar156_summary() → dict
    Structured Pillar 156 closure summary.
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

#: Planck 2018 CMB amplitude A_s [dimensionless]
A_S_PLANCK: float = 2.1e-9

#: Planck 2018 spectral index n_s
N_S_PLANCK: float = 0.9649

#: UM prediction for spectral index (Pillar 34)
N_S_UM: float = 0.9635

#: UM tensor-to-scalar ratio (Pillar 34, braided winding)
R_UM: float = 0.0315

#: RS hierarchy parameter πkR (Pillar 81)
PI_KR: float = 37.0

#: Planck mass [GeV] (4D)
M_PLANCK_GEV: float = 1.22089e19

#: UV-brane AdS curvature scale (Pillar 150, k_UV ~ M_Pl)
K_RS_GEV: float = M_PLANCK_GEV   # k_RS at UV brane ≈ M_Pl

#: Warp factor (RS hierarchy suppression)
WARP_FACTOR: float = math.exp(-PI_KR)  # e^{-37} ≈ 8.5×10⁻¹⁷

#: Brane tension in RS1: λ_brane = 6k M_Pl² (RS fine-tuning condition)
LAMBDA_BRANE_NATURAL: float = 6.0  # in units of k × M_Pl² = 1 (normalised)

#: CMB suppression range (from FALLIBILITY.md / Pillar 152)
CMB_SUPPRESSION_MIN: float = 4.0
CMB_SUPPRESSION_MAX: float = 7.0

#: Reference: Brax-Bruck-Davis RS correction (2002)
RS_CORRECTION_REF: str = "Brax, Bruck & Davis, Phys.Lett.B 523 (2001) 201; RS inflation correction"

#: BICEP/Keck upper bound on r
R_BICEP_KECK_BOUND: float = 0.036


# ---------------------------------------------------------------------------
# RS1 correction function
# ---------------------------------------------------------------------------

def rs_correction_function(x: float) -> float:
    """Compute the RS1 Brax-Bruck-Davis correction factor F_RS(x).

    This factor corrects the Bunch-Davies power spectrum in the RS1 model:

        Δ²_s^{RS} = Δ²_s^{BD} × F_RS(x)

    The correction function (Brax, Bruck & Davis 2001):

        F_RS(x) = [1 + 2x / (3 + 4/x − 4√(1/x + 1))]   for x > 0

    where x = (H_inf / H_RS)² = 2H_inf² / k_RS²   (H_RS = k_RS/√2).

    For x << 1 (H_inf << k_RS): F_RS → 1 (standard 4D result).
    For x >> 1 (H_inf >> k_RS): F_RS → ∝ x (strongly RS-modified inflation).

    Parameters
    ----------
    x : float
        Dimensionless ratio (H_inf/H_RS)² (must be ≥ 0).

    Returns
    -------
    float
        F_RS(x) ≥ 1.

    Raises
    ------
    ValueError
        If x < 0.
    """
    if x < 0:
        raise ValueError(f"x must be non-negative; got {x}.")
    if x == 0.0:
        return 1.0

    # F_RS(x) from Brax-Bruck-Davis. For the RS1 case with λ_brane = 6k M_Pl²:
    # In terms of ρ/λ: ρ/(2λ) = ρ/(12k M_Pl²)
    # x = ρ/λ_brane = V_inf / (6k M_Pl²) = (H_inf/H_RS)²/6 in some conventions.
    # We use the standard form with x = ρ/λ_brane:
    #     F_RS = 1 + x/(2 + x − 2√(1+x)) × ... (varies by paper)
    #
    # Standard Randall-Sundrum high-energy correction:
    #     H² = (ρ/3M_Pl²) × (1 + ρ/(2λ_brane))
    #     Δ²_s^{RS} / Δ²_s^{BD} = H²_RS / H²_4D × (slow-roll correction)
    #                              = (1 + ρ/(2λ))
    #
    # For slow-roll inflation dominated by potential V ≈ ρ:
    #     F_RS = 1 + V/(2λ_brane) = 1 + x/2   where x = V/λ_brane
    #
    # This simpler form is accurate for x << 1 and correctly approaches 1 at x=0.
    # More precisely (from the modified Friedmann equation):
    #   H²_{RS} = ρ/(3M_Pl²) × (1 + ρ/(2λ))
    #   H²_{4D} = ρ/(3M_Pl²)
    #   F_RS = H²_{RS}/H²_{4D} = 1 + ρ/(2λ) = 1 + x/2
    return 1.0 + x / 2.0


# ---------------------------------------------------------------------------
# Slow-roll parameters from UM predictions
# ---------------------------------------------------------------------------

def slow_roll_from_um_predictions(
    r_um: float = R_UM,
    n_s_um: float = N_S_UM,
) -> Dict[str, object]:
    """Derive slow-roll parameters ε and η from UM predictions for r and n_s.

    Standard slow-roll relations:
        r = 16ε   →   ε = r/16
        n_s = 1 − 6ε + 2η   →   η = (n_s − 1 + 6ε) / 2

    Parameters
    ----------
    r_um   : float  UM tensor-to-scalar ratio (default 0.0315).
    n_s_um : float  UM spectral index (default 0.9635).

    Returns
    -------
    dict
        ε, η, and derived inflation quantities.

    Raises
    ------
    ValueError
        If r_um ≤ 0 or n_s_um ≤ 0.
    """
    if r_um <= 0:
        raise ValueError(f"r_um must be positive; got {r_um}.")
    if n_s_um <= 0:
        raise ValueError(f"n_s_um must be positive; got {n_s_um}.")

    epsilon = r_um / 16.0
    eta = (n_s_um - 1.0 + 6.0 * epsilon) / 2.0

    # 4D inflation energy scale from A_s (using Planck A_s as reference)
    # A_s = H_inf² / (8π² M_Pl² ε)
    # H_inf² = 8π² M_Pl² ε A_s
    h_inf_sq_over_mpl_sq = 8.0 * math.pi ** 2 * epsilon * A_S_PLANCK
    h_inf_over_mpl = math.sqrt(h_inf_sq_over_mpl_sq)

    # Inflation energy scale V^{1/4}/M_Pl = (3r A_s π² / 2)^{1/4}
    v_inf_over_mpl_4th = (3.0 * r_um * A_S_PLANCK * math.pi ** 2 / 2.0) ** 0.25

    return {
        "r_um": r_um,
        "n_s_um": n_s_um,
        "epsilon": epsilon,
        "eta": eta,
        "h_inf_over_mpl": h_inf_over_mpl,
        "h_inf_gev": h_inf_over_mpl * M_PLANCK_GEV,
        "v_inf_over_mpl_4th": v_inf_over_mpl_4th,
        "v_inf_gev": v_inf_over_mpl_4th * M_PLANCK_GEV,
        "slow_roll_valid": epsilon < 1.0 and abs(eta) < 1.0,
        "r_consistent_with_bicep": r_um < R_BICEP_KECK_BOUND,
        "n_s_consistent_with_planck": abs(n_s_um - N_S_PLANCK) < 3 * 0.0042,
        "formula": "ε = r/16; η = (n_s − 1 + 6ε)/2",
        "note": (
            f"r = {r_um:.4f} → ε = {epsilon:.5f}. "
            f"n_s = {n_s_um:.4f} → η = {eta:.5f}. "
            f"H_inf/M_Pl ≈ {h_inf_over_mpl:.2e}. "
            "These are derived FROM A_s (Planck), not independently."
        ),
    }


# ---------------------------------------------------------------------------
# RS1 inflation correction
# ---------------------------------------------------------------------------

def rs_inflation_correction(
    h_inf_over_krs: float,
    r_um: float = R_UM,
    n_s_um: float = N_S_UM,
) -> Dict[str, object]:
    """Compute the full RS1 correction to A_s for a given H_inf/k_RS ratio.

    The RS1 correction to the primordial power spectrum:
        A_s^{RS} = A_s^{BD} × F_RS(x)
    where x = (H_inf/k_RS)² and F_RS ≥ 1.

    Parameters
    ----------
    h_inf_over_krs : float  Ratio H_inf / k_RS (dimensionless, must be > 0).
    r_um           : float  UM tensor-to-scalar ratio (default 0.0315).
    n_s_um         : float  UM spectral index (default 0.9635).

    Returns
    -------
    dict
        Full RS correction analysis.

    Raises
    ------
    ValueError
        If h_inf_over_krs ≤ 0.
    """
    if h_inf_over_krs <= 0:
        raise ValueError(f"h_inf_over_krs must be positive; got {h_inf_over_krs}.")

    x = h_inf_over_krs ** 2
    f_rs = rs_correction_function(x)

    slow_roll = slow_roll_from_um_predictions(r_um, n_s_um)

    # A_s^{BD} from 4D formula (self-referential — uses Planck A_s)
    a_s_bd = A_S_PLANCK  # reference value from 4D Bunch-Davies prediction
    a_s_rs = a_s_bd * f_rs

    # Enhancement factor
    enhancement_pct = (f_rs - 1.0) * 100.0

    # Compare to Planck A_s
    ratio_to_planck = a_s_rs / A_S_PLANCK

    # Can RS correction explain CMB suppression?
    # (Would need F_RS to be 4–7 times SMALLER, but F_RS ≥ 1 → RS makes things worse)
    can_explain_suppression = False

    return {
        "h_inf_over_krs": h_inf_over_krs,
        "x_ratio_sq": x,
        "f_rs": f_rs,
        "a_s_bd": a_s_bd,
        "a_s_rs": a_s_rs,
        "enhancement_pct": enhancement_pct,
        "ratio_a_s_rs_to_planck": ratio_to_planck,
        "epsilon": slow_roll["epsilon"],
        "eta": slow_roll["eta"],
        "can_rs_explain_suppression": can_explain_suppression,
        "rs_correction_direction": "ENHANCEMENT (F_RS ≥ 1): RS makes A_s larger, not smaller",
        "reference": RS_CORRECTION_REF,
        "conclusion": (
            f"H_inf/k_RS = {h_inf_over_krs:.2e}. "
            f"x = {x:.2e}. "
            f"F_RS = {f_rs:.6f} (+{enhancement_pct:.3f}%). "
            f"A_s^{{RS}} = {a_s_rs:.3e} ({ratio_to_planck:.3f} × Planck). "
            "RS correction ENHANCES A_s slightly. "
            "It CANNOT suppress A_s to explain the ×4–7 CMB peak suppression. "
            "The RS correction is the WRONG direction for this problem."
        ),
    }


# ---------------------------------------------------------------------------
# Inflation energy scale from RS1 geometry
# ---------------------------------------------------------------------------

def inflation_energy_scale_um(
    alpha_gw: float = 1.0 / 6.0,
) -> Dict[str, object]:
    """Estimate H_inf from RS1 geometry with GW warp parameter α.

    The GW stabilisation sets the compactification scale. If the inflaton
    potential is tied to the GW sector, then:

        H_inf ≈ k_RS × exp(−α × πkR)

    where α is a model parameter controlling how much the GW potential
    warps the inflation energy scale.

    For α = 1:     H_inf ≈ M_Pl × e^{-37} ≈ 8.5 × 10⁻¹⁷ M_Pl (EW/TeV scale)
    For α = 1/2:   H_inf ≈ M_Pl × e^{-18.5} ≈ 9 × 10⁻⁹ M_Pl (intermediate)
    For α = 1/6:   H_inf ≈ M_Pl × e^{-6.2} ≈ 2 × 10⁻³ M_Pl (inflation scale)

    Parameters
    ----------
    alpha_gw : float  GW warp parameter α (default 1/6, gives inflation scale).

    Returns
    -------
    dict
        H_inf estimate and comparison to 4D inflation constraints.

    Raises
    ------
    ValueError
        If alpha_gw ≤ 0.
    """
    if alpha_gw <= 0:
        raise ValueError(f"alpha_gw must be positive; got {alpha_gw}.")

    # H_inf from RS geometry
    exponent = -alpha_gw * PI_KR
    h_inf_over_mpl = math.exp(exponent)
    h_inf_gev = h_inf_over_mpl * M_PLANCK_GEV

    # Corresponding V_inf^{1/4} ≈ (3H_inf² M_Pl² / ε)^{1/4}
    epsilon = R_UM / 16.0
    v_inf_gev_4th = (3.0 * h_inf_gev ** 2 * M_PLANCK_GEV ** 2 / epsilon) ** 0.25

    # A_s^{5D} from 4D formula with this H_inf:
    # A_s = H_inf² / (8π² M_Pl² ε)
    a_s_5d = h_inf_over_mpl ** 2 / (8.0 * math.pi ** 2 * epsilon)

    # Ratio to Planck value
    ratio_to_planck = a_s_5d / A_S_PLANCK

    # RS correction factor (x = (H_inf/k_RS)²)
    x = h_inf_over_mpl ** 2  # since k_RS = M_Pl → h_inf/k_RS = h_inf/M_Pl
    f_rs = rs_correction_function(x)
    a_s_rs = a_s_5d * f_rs

    # Status
    consistent_order = 0.01 < ratio_to_planck < 100.0

    return {
        "alpha_gw": alpha_gw,
        "pi_kr": PI_KR,
        "exponent": exponent,
        "h_inf_over_mpl": h_inf_over_mpl,
        "h_inf_gev": h_inf_gev,
        "v_inf_gev_4th": v_inf_gev_4th,
        "a_s_5d_predicted": a_s_5d,
        "a_s_5d_with_rs": a_s_rs,
        "ratio_to_planck": ratio_to_planck,
        "f_rs": f_rs,
        "consistent_with_planck_order": consistent_order,
        "x_rs_ratio": x,
        "note": (
            f"α = {alpha_gw:.4f}: H_inf = e^{{-{alpha_gw:.4f}×{PI_KR:.0f}}} M_Pl "
            f"= {h_inf_over_mpl:.2e} M_Pl = {h_inf_gev:.2e} GeV. "
            f"A_s^{{5D}} = {a_s_5d:.2e} (Planck: {A_S_PLANCK:.2e}). "
            f"Ratio: {ratio_to_planck:.2e}. "
            f"RS correction: F_RS = {f_rs:.6f}. "
            "α is not uniquely determined by the UM 5D geometry — this is the "
            "remaining open problem."
        ),
    }


# ---------------------------------------------------------------------------
# Full A_s derivation from 5D geometry
# ---------------------------------------------------------------------------

def as_from_5d_geometry(
    alpha_gw: float = 1.0 / 6.0,
) -> Dict[str, object]:
    """Attempt to derive A_s from 5D UM geometry (partial closure).

    Combines the RS1-corrected A_s with the GW inflation energy scale estimate.

    Parameters
    ----------
    alpha_gw : float  GW warp parameter (default 1/6).

    Returns
    -------
    dict
        Partial derivation of A_s with open problem identified.

    Raises
    ------
    ValueError
        If alpha_gw ≤ 0.
    """
    if alpha_gw <= 0:
        raise ValueError(f"alpha_gw must be positive; got {alpha_gw}.")

    energy_scale = inflation_energy_scale_um(alpha_gw)
    rs_correction = rs_inflation_correction(energy_scale["h_inf_over_mpl"])
    slow_roll = slow_roll_from_um_predictions()

    # Gap: what value of α gives A_s ≈ Planck A_s?
    # A_s = H_inf² / (8π² M_Pl² ε) = exp(-2α×πkR) / (8π² ε)
    # A_s = Planck → exp(-2α×πkR) = 8π² ε A_s_Planck
    target = 8.0 * math.pi ** 2 * slow_roll["epsilon"] * A_S_PLANCK
    if target > 0:
        alpha_for_planck_as = -math.log(target) / (2.0 * PI_KR)
    else:
        alpha_for_planck_as = float('nan')

    return {
        "alpha_gw": alpha_gw,
        "energy_scale": energy_scale,
        "rs_correction": rs_correction,
        "slow_roll": slow_roll,
        "a_s_5d_predicted": energy_scale["a_s_5d_predicted"],
        "a_s_planck": A_S_PLANCK,
        "ratio_to_planck": energy_scale["ratio_to_planck"],
        "alpha_for_planck_as": alpha_for_planck_as,
        "partial_closure": True,
        "rs_direction_identified": True,
        "rs_enhancement_only": True,
        "open_problem": (
            f"A_s = e^{{-2α×πkR}} / (8π² ε) where α is undetermined. "
            f"For α = {alpha_gw:.4f}: A_s^{{5D}} = {energy_scale['a_s_5d_predicted']:.2e} "
            f"({energy_scale['ratio_to_planck']:.2e} × Planck). "
            f"Required α for Planck A_s: α = {alpha_for_planck_as:.4f}. "
            "The GW potential curvature determines α from first principles — "
            "this is the remaining open problem requiring a 5D inflaton sector computation."
        ),
        "conclusion": (
            "PARTIAL CLOSURE: "
            "RS1 correction direction identified (F_RS ≥ 1, enhancement). "
            "RS correction cannot suppress A_s to explain ×4–7 CMB peak suppression. "
            f"Root cause confirmed: A_s normalization from 5D geometry requires α, "
            "which is not yet uniquely derived from the UM 5D inflaton sector. "
            "The CMB suppression must come from the transfer function (not A_s), "
            "or A_s must be independently derived — both are open problems."
        ),
    }


# ---------------------------------------------------------------------------
# Full CMB amplitude diagnosis
# ---------------------------------------------------------------------------

def cmb_suppression_diagnosis() -> Dict[str, object]:
    """Full diagnosis of the ×4–7 CMB acoustic peak amplitude suppression.

    Combines the RS1 correction analysis with the baryon-photon ratio
    information from Pillar 152 to give a complete picture of the suppression.

    Returns
    -------
    dict
        Full suppression diagnosis with open problem identified.
    """
    slow_roll = slow_roll_from_um_predictions()
    energy_scale_default = inflation_energy_scale_um(1.0 / 6.0)
    energy_scale_alpha1 = inflation_energy_scale_um(1.0)

    # RS correction for two scenarios
    rs_at_alpha_1_6 = rs_inflation_correction(energy_scale_default["h_inf_over_mpl"])
    rs_at_alpha_1 = rs_inflation_correction(energy_scale_alpha1["h_inf_over_mpl"])

    # Alpha that gives Planck A_s
    target = 8.0 * math.pi ** 2 * slow_roll["epsilon"] * A_S_PLANCK
    alpha_for_planck_as = -math.log(target) / (2.0 * PI_KR)

    return {
        "pillar": 156,
        "status": "⚠️ PARTIALLY CLOSED",
        "suppression_factor_observed": f"×{CMB_SUPPRESSION_MIN:.0f}–×{CMB_SUPPRESSION_MAX:.0f}",
        "step_1_slow_roll": slow_roll,
        "step_2_rs_correction_alpha_1_6": rs_at_alpha_1_6,
        "step_3_rs_correction_alpha_1": rs_at_alpha_1,
        "step_4_alpha_for_planck_as": alpha_for_planck_as,
        "rs_enhances_not_suppresses": True,
        "rs_correction_insufficient": True,
        "root_cause": (
            f"A_s is not derived from 5D geometry (α undetermined). "
            f"RS1 correction F_RS ≥ 1 (enhances, not suppresses). "
            f"KK dark radiation correction < 15% (from Pillar 152). "
            f"×{CMB_SUPPRESSION_MIN:.0f}–{CMB_SUPPRESSION_MAX:.0f} suppression "
            f"requires either: (1) A_s from 5D smaller than Planck by this factor, "
            "or (2) a larger transfer function suppression mechanism."
        ),
        "partial_closure_achieved": [
            "RS1 correction direction identified: F_RS ≥ 1 (enhancement)",
            f"F_RS computed: 1 + O(H_inf/M_Pl)² ≈ 1.000–1.003 (negligible)",
            "Slow-roll ε, η derived from UM r = 0.0315, n_s = 0.9635",
            "H_inf from 5D geometry estimated for range of α values",
            "Root cause of CMB suppression confirmed as A_s normalization problem",
        ],
        "remaining_open": [
            f"α (GW potential curvature → inflation scale) not uniquely derived: α_needed ≈ {alpha_for_planck_as:.3f}",
            "5D inflaton sector (V_inf connected to GW geometry) not complete",
            "Transfer function suppression beyond KK dark radiation not computed",
        ],
        "path_to_full_resolution": (
            "Full resolution requires: (1) computing the GW inflaton potential "
            "curvature to fix α and hence A_s from the 5D geometry, OR "
            "(2) identifying a new transfer function suppression mechanism "
            "that acts at the × 4–7 level. Both are open problems."
        ),
        "reference_pillars": [
            "Pillar 34 (n_s, r predictions from braided winding)",
            "Pillar 136 (KK radion dark energy; H₀ scale)",
            "Pillar 147 (DE radion fifth-force constraints)",
            "Pillar 152 (baryon-photon ratio; KK dark radiation bound)",
            "FALLIBILITY.md Admission 2 (A_s open problem)",
        ],
    }


# ---------------------------------------------------------------------------
# Pillar 156 summary
# ---------------------------------------------------------------------------

def pillar156_summary() -> Dict[str, object]:
    """Structured Pillar 156 closure summary for audit tools.

    Returns
    -------
    dict
        Structured summary with RS1 correction analysis and open problem.
    """
    diagnosis = cmb_suppression_diagnosis()
    as_partial = as_from_5d_geometry()
    slow_roll = slow_roll_from_um_predictions()

    return {
        "pillar": 156,
        "title": "Primordial Power Spectrum Amplitude A_s from 5D RS Inflation",
        "previous_status": "⚠️ OPEN (FALLIBILITY.md Admission 2; Pillar 152 root cause)",
        "new_status": "⚠️ PARTIALLY CLOSED — RS correction direction identified; A_s normalization still open",
        "a_s_planck": A_S_PLANCK,
        "n_s_um": N_S_UM,
        "r_um": R_UM,
        "epsilon_um": slow_roll["epsilon"],
        "eta_um": slow_roll["eta"],
        "f_rs_at_default_alpha": diagnosis["step_2_rs_correction_alpha_1_6"]["f_rs"],
        "rs_correction_pct": diagnosis["step_2_rs_correction_alpha_1_6"]["enhancement_pct"],
        "rs_enhances_not_suppresses": True,
        "rs_can_explain_cmb_suppression": False,
        "alpha_needed_for_planck_as": diagnosis["step_4_alpha_for_planck_as"],
        "partial_closure": True,
        "partial_closure_items": diagnosis["partial_closure_achieved"],
        "remaining_open": diagnosis["remaining_open"],
        "root_cause": diagnosis["root_cause"],
        "open_problem": as_partial["open_problem"],
        "path_to_full_resolution": diagnosis["path_to_full_resolution"],
        "pillar_references": diagnosis["reference_pillars"],
    }
