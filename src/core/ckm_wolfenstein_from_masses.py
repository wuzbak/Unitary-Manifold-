# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0

"""Pillar 106 — CKM Wolfenstein λ_W from fermion-mass-fitted RS c-values.

Epistemic Status
----------------
CONSTRAINED — c_R bulk-mass parameters are FITTED to PDG fermion masses;
c_L bulk-mass parameters are GEOMETRIC (from 6D T²/Z₃ spectrum, Pillar 6D-2).

Key result
----------
    λ_W = sqrt(m_d / m_s) = 0.22361
    PDG Wolfenstein λ = 0.22650
    Residual: 1.28%  (< 5% threshold)

Why CONSTRAINED and not GEOMETRIC_PREDICTION
--------------------------------------------
The c_L values are derived from the 6D orbifold geometry (no free parameters).
However the c_R values are determined by inverting the RS mass formula with PDG
masses as inputs — six fitted numbers (three up-type, three down-type).  Since
free parameters are consumed to reproduce the mass spectrum, the resulting λ_W is
not a pure prediction.

Physical derivation path
------------------------
The Randall-Sundrum zero-mode wavefunction at the IR brane is:

    f_IR(c) = √|1-2c| · exp((½-c)·πkR) / √|exp((1-2c)·πkR) - 1|

    Special case c = ½:  f_IR = 1/√(2·πkR)

Fermion masses arise from the 5D Yukawa coupling integrated over the extra
dimension with an IR-brane Higgs:

    m_i  =  Y5 · v_EW · f_IR(c_L^{(i)}) · f_IR(c_R^{(i)})

where c_L^{(i)} is fixed by 6D geometry and c_R^{(i)} is fitted.

The left-handed doublet SU(2) constraint means c_L is SHARED by up- and down-
type quarks of the same generation.  Inverting gives:

    f_IR(c_R^{d,u}_{(i)})  =  m_{d,u_i} / (Y5^{d,u} · v_EW · f_IR(c_L^{(i)}))

The Wolfenstein λ_W is the 1-2 generation CKM mixing angle.  In the RS model
with rank-1 dominance and next-order correction from c_R mismatch, it reduces
to the Fritzsch relation:

    λ_W  =  √(m_d / m_s)
          =  √[ f_IR(c_L^{(2)}) · f_IR(c_R^{d}_{(2)})
               ─────────────────────────────────────── ]
               √[ f_IR(c_L^{(1)}) · f_IR(c_R^{d}_{(1)}) ]

    Result: λ_W = 0.22361   PDG: 0.22650   Residual: 1.28%

This is identical to the Fritzsch (1978) relation, rederived here from the RS
wavefunction hierarchy imposed by the 6D c_L spectrum.

Honest residuals for higher CKM elements
-----------------------------------------
    V_us ≈ 0.2236  PDG 0.22650   residual  1.3%   ← primary result
    V_cb ~ 0.1495  PDG 0.04221   residual  254%   ← NOT reproduced
    V_ub ~ 0.0334  PDG 0.003690  residual  806%   ← NOT reproduced

V_cb and V_ub require sub-leading RS corrections beyond the Fritzsch texture.
This module makes no claim on those elements.

Fixed parameters (inputs)
--------------------------
    πkR   = 37         (from Goldberger-Wise / UM braid resonance)
    n_w   = 5          (winding number)
    k_CS  = 74         (Chern-Simons level, = 5² + 7²)
    v_EW  = 246 000 MeV (electroweak VEV)

PDG masses used (MS-bar at M_Z, MeV)
--------------------------------------
    m_u = 2.16   m_c = 1273.0   m_t = 172 760.0
    m_d = 4.67   m_s = 93.4     m_b = 4 180.0

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from scipy.optimize import brentq

__all__ = [
    # Constants
    "N_W", "K_CS", "PI_KR", "V_EW_MEV",
    "C_L_6D",
    "PDG_WOLFENSTEIN_LAMBDA",
    "PDG_MASSES_MEV",
    "EPISTEMIC_STATUS",
    # Core RS functions
    "rs_wavefunction_ir",
    "invert_rs_wavefunction",
    # c_L spectrum
    "cl_spectrum_6d",
    # c_R fitting
    "fit_cr_sector",
    # CKM derivation
    "fritzsch_wolfenstein_lambda",
    "wolfenstein_from_cr_mismatch",
    "ckm_fritzsch_estimate",
    # Report
    "pillar_106_report",
]

# ---------------------------------------------------------------------------
# Repository constants
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74
PI_KR: float = float(K_CS) / 2.0       # = 37.0  (πkR, Goldberger-Wise)
V_EW_MEV: float = 246_000.0            # electroweak VEV [MeV]

# 6D c_L spectrum: c_L^{(i)} = ½ + i · n_w/k_CS  for i = 0, 1, 2
_SPACING: float = float(N_W) / float(K_CS)   # = 5/74
C_L_6D: Tuple[float, float, float] = (
    0.5,
    0.5 + _SPACING,
    0.5 + 2.0 * _SPACING,
)

# PDG Wolfenstein λ (PDG 2024)
PDG_WOLFENSTEIN_LAMBDA: float = 0.22650

# PDG quark masses [MeV] (MS-bar at M_Z)
PDG_MASSES_MEV: Dict[str, float] = {
    "m_u": 2.16,
    "m_c": 1273.0,
    "m_t": 172_760.0,
    "m_d": 4.67,
    "m_s": 93.4,
    "m_b": 4_180.0,
}

EPISTEMIC_STATUS: str = (
    "CONSTRAINED — c_R fitted from PDG masses; c_L geometric (6D T²/Z₃). "
    "λ_W residual 1.28% < 5% gate.  V_cb, V_ub NOT reproduced at leading order."
)


# ---------------------------------------------------------------------------
# RS zero-mode wavefunction at the IR brane  (uses math, not numpy)
# ---------------------------------------------------------------------------

def rs_wavefunction_ir(c: float, pi_kr: float = PI_KR) -> float:
    """RS zero-mode wavefunction profile evaluated at the IR brane.

    f_IR(c) = √|1-2c| · exp((½-c)·πkR) / √|exp((1-2c)·πkR) - 1|

    Special case c = ½:  f_IR = 1/√(2·πkR).

    For |exponent| > 700 an analytic limit is used to avoid overflow:
      · (1-2c)·πkR ≫ 0 (c < ½, IR-localised):  f_IR → √|1-2c|
      · (1-2c)·πkR ≪ 0 (c > ½, UV-localised):  f_IR → 0 exponentially

    Parameters
    ----------
    c : float       Bulk mass parameter (dimensionless, units of AdS curvature k).
    pi_kr : float   πkR compactification modulus (default 37).

    Returns
    -------
    float  Non-negative wavefunction value.
    """
    if abs(c - 0.5) < 1e-10:
        return 1.0 / math.sqrt(2.0 * pi_kr)

    a = (0.5 - c) * pi_kr           # half-exponent; a = b/2
    b = (1.0 - 2.0 * c) * pi_kr    # full exponent

    sqrt_fac = math.sqrt(abs(1.0 - 2.0 * c))

    if b > 700.0:
        # c << ½, IR-localised limit: exp(b) → ∞, denominator → exp(a)
        return sqrt_fac

    if b < -700.0:
        # c >> ½, UV-localised limit: exp(b) → 0, exp(a) → 0
        return 0.0

    try:
        num = sqrt_fac * math.exp(a)
    except OverflowError:
        return sqrt_fac

    exp_b = math.exp(b)
    denom = math.sqrt(abs(exp_b - 1.0))
    if denom < 1e-300:
        return 0.0

    return num / denom


# ---------------------------------------------------------------------------
# Numerical inversion of f_IR
# ---------------------------------------------------------------------------

def invert_rs_wavefunction(
    f_target: float,
    pi_kr: float = PI_KR,
    tol: float = 1e-12,
) -> float:
    """Find c such that rs_wavefunction_ir(c, pi_kr) = f_target.

    f_IR is strictly monotone decreasing from +∞ (c → -∞) to 0 (c → +∞),
    so a unique solution exists for any f_target > 0.

    Parameters
    ----------
    f_target : float  Desired wavefunction value (must be > 0).
    pi_kr : float     πkR (default 37).
    tol : float       Absolute tolerance for brentq root-finder.

    Returns
    -------
    float  Bulk mass parameter c such that f_IR(c) ≈ f_target.

    Raises
    ------
    ValueError  If f_target ≤ 0.
    """
    if f_target <= 0.0:
        raise ValueError(f"f_target must be > 0, got {f_target}")

    # The midpoint c = 0.5 gives f_IR ≈ 0.116 for πkR = 37.
    # Start bracket from c = 0.5 and expand.
    lo = hi = 0.5

    if rs_wavefunction_ir(lo, pi_kr) < f_target:
        # Need c < 0.5 (IR-localised side)
        while rs_wavefunction_ir(lo, pi_kr) < f_target:
            lo -= 1.0
        hi = lo + 1.0
    else:
        # Need c > 0.5 (UV-localised side)
        while rs_wavefunction_ir(hi, pi_kr) > f_target:
            hi += 1.0
        lo = hi - 1.0

    return float(brentq(
        lambda c_: rs_wavefunction_ir(c_, pi_kr) - f_target,
        lo, hi, xtol=tol,
    ))


# ---------------------------------------------------------------------------
# 6D c_L spectrum
# ---------------------------------------------------------------------------

def cl_spectrum_6d(n_w: int = N_W, k_cs: int = K_CS) -> Dict[str, object]:
    """Return the three 6D c_L values and their associated wavefunction overlaps.

    c_L^{(i)} = ½ + i · n_w/k_CS   for i = 0, 1, 2.

    Generation ordering (heaviest to lightest):
        i=0: top / bottom    (IR-critical, f_IR maximal)
        i=1: charm / strange
        i=2: up   / down     (UV-localised, f_IR minimal)

    Parameters
    ----------
    n_w : int   Winding number (default 5).
    k_cs : int  Chern-Simons level (default 74).

    Returns
    -------
    dict with c_L values, wavefunction overlaps, and derivation metadata.
    """
    spacing = float(n_w) / float(k_cs)
    cl = tuple(0.5 + i * spacing for i in range(3))
    fl = tuple(rs_wavefunction_ir(c) for c in cl)
    return {
        "n_w": n_w,
        "k_cs": k_cs,
        "pi_kr": float(k_cs) / 2.0,
        "spacing": spacing,
        "c_L": cl,
        "f_IR_cL": fl,
        "adjacent_ratio_01": fl[1] / fl[0] if fl[0] > 0 else 0.0,
        "adjacent_ratio_12": fl[2] / fl[1] if fl[1] > 0 else 0.0,
        "formula": "c_L^{(i)} = ½ + i·n_w/k_CS",
        "source": "6D T²/Z₃ fixed-point spectrum (Pillar 6D-2)",
        "free_parameters": 0,
    }


# ---------------------------------------------------------------------------
# c_R fitting from PDG masses
# ---------------------------------------------------------------------------

def fit_cr_sector(
    m_heavy_mev: float,
    m_mid_mev: float,
    m_light_mev: float,
    c_L: Tuple[float, float, float] = C_L_6D,
    pi_kr: float = PI_KR,
    v_mev: float = V_EW_MEV,
    c_R_heavy: float = 0.5,
) -> Dict[str, object]:
    """Fit c_R bulk-mass parameters for one quark sector from PDG masses.

    Strategy
    ---------
    Fix the overall 5D Yukawa scale Y5 by anchoring the heaviest generation
    to c_R^{(0)} = 0.5 (symmetric IR-flat profile), then invert the RS mass
    formula for the two lighter generations:

        m_i = Y5 · v_EW · f_IR(c_L^{(i)}) · f_IR(c_R^{(i)})

    Note: c_R^{(0)} = 0.5 is a choice, not a prediction.  Y5 absorbs the
    remaining freedom in the overall scale.

    Parameters
    ----------
    m_heavy_mev : float  Mass of heaviest generation (e.g. m_t or m_b) [MeV].
    m_mid_mev   : float  Mass of middle generation   (e.g. m_c or m_s) [MeV].
    m_light_mev : float  Mass of lightest generation (e.g. m_u or m_d) [MeV].
    c_L         : tuple  Three c_L values (gen 0, 1, 2).
    pi_kr       : float  πkR (default 37).
    v_mev       : float  Electroweak VEV [MeV] (default 246 000).
    c_R_heavy   : float  Assumed c_R for the heaviest generation (default 0.5).

    Returns
    -------
    dict with fitted c_R values, target f_IR values, Y5, and fit residuals.
    """
    fL = [rs_wavefunction_ir(c, pi_kr) for c in c_L]
    fR_heavy = rs_wavefunction_ir(c_R_heavy, pi_kr)

    # Overall Yukawa scale anchored to heaviest generation
    Y5 = m_heavy_mev / (v_mev * fL[0] * fR_heavy)

    # Target f_IR values for the two lighter generations
    fR_target_mid   = m_mid_mev   / (Y5 * v_mev * fL[1])
    fR_target_light = m_light_mev / (Y5 * v_mev * fL[2])

    # Invert to get c_R
    c_R_mid   = invert_rs_wavefunction(fR_target_mid,   pi_kr)
    c_R_light = invert_rs_wavefunction(fR_target_light, pi_kr)

    # Verify round-trip
    m_mid_check   = Y5 * v_mev * fL[1] * rs_wavefunction_ir(c_R_mid,   pi_kr)
    m_light_check = Y5 * v_mev * fL[2] * rs_wavefunction_ir(c_R_light, pi_kr)

    return {
        "c_L": list(c_L),
        "c_R": [c_R_heavy, c_R_mid, c_R_light],
        "f_IR_cL": fL,
        "f_IR_cR": [fR_heavy, fR_target_mid, fR_target_light],
        "Y5": Y5,
        "masses_input_mev": [m_heavy_mev, m_mid_mev, m_light_mev],
        "masses_check_mev": [m_heavy_mev, m_mid_check, m_light_check],
        "residuals_pct": [
            0.0,
            abs(m_mid_check   - m_mid_mev)   / m_mid_mev   * 100.0,
            abs(m_light_check - m_light_mev) / m_light_mev * 100.0,
        ],
        "c_R_heavy_assumed": c_R_heavy,
        "free_parameters": 3,  # Y5 + c_R_mid + c_R_light (all from PDG masses)
        "epistemic": "FITTED — c_R inverted from PDG masses",
    }


# ---------------------------------------------------------------------------
# Fritzsch Wolfenstein λ
# ---------------------------------------------------------------------------

def fritzsch_wolfenstein_lambda(
    m_d_mev: float = PDG_MASSES_MEV["m_d"],
    m_s_mev: float = PDG_MASSES_MEV["m_s"],
) -> Dict[str, object]:
    """Compute Wolfenstein λ via the Fritzsch relation λ_W = √(m_d / m_s).

    Physical derivation
    -------------------
    In a rank-1-dominant Yukawa texture (RS leading order), the 1-2 generation
    CKM rotation angle θ_C is generated by the next-order correction from the
    down-type c_R hierarchy.  The dominant contribution is:

        tan θ_C  ≈  √(m_d / m_s)        [Fritzsch 1978]

    and for small θ_C:  λ_W = sin θ_C ≈ tan θ_C ≈ √(m_d / m_s).

    In the RS / UM framework this is equivalent to:

        λ_W = √[ f_IR(c_L^{(2)}) · f_IR(c_R^d_{(2)})
                ───────────────────────────────────── ]
                  f_IR(c_L^{(1)}) · f_IR(c_R^d_{(1)})

    because the numerator equals m_d / (Y5·v) and denominator equals m_s / (Y5·v).

    Parameters
    ----------
    m_d_mev : float   Down quark mass [MeV] (PDG default 4.67).
    m_s_mev : float   Strange quark mass [MeV] (PDG default 93.4).

    Returns
    -------
    dict with lambda_wolfenstein, theta_cabibbo_deg, pdg_lambda, residual_pct,
         and epistemic label.
    """
    lam = math.sqrt(m_d_mev / m_s_mev)
    theta_deg = math.degrees(math.asin(min(lam, 1.0)))
    residual_pct = abs(lam - PDG_WOLFENSTEIN_LAMBDA) / PDG_WOLFENSTEIN_LAMBDA * 100.0

    return {
        "lambda_wolfenstein": lam,
        "theta_cabibbo_deg": theta_deg,
        "pdg_lambda": PDG_WOLFENSTEIN_LAMBDA,
        "residual_pct": residual_pct,
        "formula": "lambda_W = sqrt(m_d / m_s)",
        "epistemic": (
            "CONSTRAINED — Fritzsch relation from RS rank-1 texture; "
            "m_d, m_s are PDG inputs."
        ),
        "gate_5pct": residual_pct < 5.0,
    }


# ---------------------------------------------------------------------------
# Wolfenstein λ from c_R mismatch (explicit RS derivation)
# ---------------------------------------------------------------------------

def wolfenstein_from_cr_mismatch(
    c_L: Tuple[float, float, float] = C_L_6D,
    cr_d_mid: float | None = None,
    cr_d_light: float | None = None,
    m_d_mev: float = PDG_MASSES_MEV["m_d"],
    m_s_mev: float = PDG_MASSES_MEV["m_s"],
    m_b_mev: float = PDG_MASSES_MEV["m_b"],
    pi_kr: float = PI_KR,
    v_mev: float = V_EW_MEV,
) -> Dict[str, object]:
    """Derive Wolfenstein λ_W from the down-type c_R mismatch.

    The CKM 1-2 mixing angle in the RS model is:

        λ_W  =  √[ f_IR(c_L^{(2)}) · f_IR(c_R^d_{(2)})
                  ─────────────────────────────────────── ]
                   f_IR(c_L^{(1)}) · f_IR(c_R^d_{(1)})

    This is the explicit RS wavefunction version of the Fritzsch relation.

    If cr_d_mid / cr_d_light are not provided they are fitted from PDG masses.

    Parameters
    ----------
    c_L            : tuple  Three 6D c_L values.
    cr_d_mid       : float  c_R for the strange quark (fitted if None).
    cr_d_light     : float  c_R for the down quark (fitted if None).
    m_d_mev        : float  Down quark mass [MeV].
    m_s_mev        : float  Strange quark mass [MeV].
    m_b_mev        : float  Bottom quark mass [MeV] (used to anchor Y5).
    pi_kr          : float  πkR (default 37).
    v_mev          : float  EW VEV [MeV].

    Returns
    -------
    dict with lambda_wolfenstein, c_R values, f_IR values, residual_pct.
    """
    fit = fit_cr_sector(m_b_mev, m_s_mev, m_d_mev, c_L, pi_kr, v_mev)

    if cr_d_mid is None:
        cr_d_mid = fit["c_R"][1]
    if cr_d_light is None:
        cr_d_light = fit["c_R"][2]

    fL_1 = rs_wavefunction_ir(c_L[1], pi_kr)
    fL_2 = rs_wavefunction_ir(c_L[2], pi_kr)
    fR_d1 = rs_wavefunction_ir(cr_d_mid,   pi_kr)
    fR_d2 = rs_wavefunction_ir(cr_d_light, pi_kr)

    # λ_W from RS wavefunction product ratio
    ratio = (fL_2 * fR_d2) / (fL_1 * fR_d1)
    lam = math.sqrt(abs(ratio))
    residual_pct = abs(lam - PDG_WOLFENSTEIN_LAMBDA) / PDG_WOLFENSTEIN_LAMBDA * 100.0

    # Decompose contribution
    fL_ratio = fL_2 / fL_1 if fL_1 > 0 else 0.0
    fR_ratio = fR_d2 / fR_d1 if fR_d1 > 0 else 0.0

    return {
        "lambda_wolfenstein": lam,
        "pdg_lambda": PDG_WOLFENSTEIN_LAMBDA,
        "residual_pct": residual_pct,
        "c_L": list(c_L),
        "c_R_d": [fit["c_R"][0], cr_d_mid, cr_d_light],
        "f_IR_cL_1": fL_1,
        "f_IR_cL_2": fL_2,
        "f_IR_cR_d1": fR_d1,
        "f_IR_cR_d2": fR_d2,
        "fL_ratio_21": fL_ratio,
        "fR_ratio_21": fR_ratio,
        "product_ratio": ratio,
        "formula": "lambda_W = sqrt(fIR(cL_2)*fIR(cR_d2) / (fIR(cL_1)*fIR(cR_d1)))",
        "equals_fritzsch": "= sqrt(m_d / m_s) by construction",
        "gate_5pct": residual_pct < 5.0,
        "epistemic": (
            "CONSTRAINED — c_R mismatch from PDG-fitted masses; "
            "c_L geometric (6D).  λ_W equivalent to Fritzsch relation."
        ),
    }


# ---------------------------------------------------------------------------
# Full CKM Fritzsch estimate (3×3, analytic)
# ---------------------------------------------------------------------------

def ckm_fritzsch_estimate(
    m_u_mev: float = PDG_MASSES_MEV["m_u"],
    m_c_mev: float = PDG_MASSES_MEV["m_c"],
    m_t_mev: float = PDG_MASSES_MEV["m_t"],
    m_d_mev: float = PDG_MASSES_MEV["m_d"],
    m_s_mev: float = PDG_MASSES_MEV["m_s"],
    m_b_mev: float = PDG_MASSES_MEV["m_b"],
) -> Dict[str, object]:
    """Fritzsch-texture CKM estimates for all three mixing angles.

    Angle formulae from rank-1 Yukawa texture with RS-motivated c_R hierarchy:

        |V_us| ≈ √(m_d / m_s)               [dominant, 1-2 mixing]
        |V_cb| ≈ √(m_s / m_b)               [23 mixing, larger residual]
        |V_ub| ≈ √(m_d / m_b)               [13 mixing, larger residual]

    Only V_us (= Wolfenstein λ) is within 5% of PDG.  V_cb and V_ub are
    included for completeness with explicit honest residuals.

    Parameters
    ----------
    m_u_mev ... m_b_mev : PDG quark masses [MeV].

    Returns
    -------
    dict with V_us, V_cb, V_ub, angles, PDG comparisons, residuals.
    """
    V_us = math.sqrt(m_d_mev / m_s_mev)
    V_cb = math.sqrt(m_s_mev / m_b_mev)
    V_ub = math.sqrt(m_d_mev / m_b_mev)

    # PDG values (Wolfenstein λ, A, ρ, η)
    pdg_V_us = 0.22650
    pdg_V_cb = 0.04221
    pdg_V_ub = 0.003690

    def _residual(val, ref):
        return abs(val - ref) / ref * 100.0 if ref > 0 else float("inf")

    def _angle_deg(v):
        return math.degrees(math.asin(min(abs(v), 1.0)))

    return {
        "V_us": V_us,
        "V_cb": V_cb,
        "V_ub": V_ub,
        "theta_12_deg": _angle_deg(V_us),
        "theta_23_deg": _angle_deg(V_cb),
        "theta_13_deg": _angle_deg(V_ub),
        "pdg_V_us": pdg_V_us,
        "pdg_V_cb": pdg_V_cb,
        "pdg_V_ub": pdg_V_ub,
        "residual_V_us_pct": _residual(V_us, pdg_V_us),
        "residual_V_cb_pct": _residual(V_cb, pdg_V_cb),
        "residual_V_ub_pct": _residual(V_ub, pdg_V_ub),
        "gate_5pct_V_us": _residual(V_us, pdg_V_us) < 5.0,
        "gate_5pct_V_cb": _residual(V_cb, pdg_V_cb) < 5.0,
        "gate_5pct_V_ub": _residual(V_ub, pdg_V_ub) < 5.0,
        "formulae": {
            "V_us": "sqrt(m_d / m_s)",
            "V_cb": "sqrt(m_s / m_b)",
            "V_ub": "sqrt(m_d / m_b)",
        },
        "honest_note": (
            "V_us within 5% gate (CONSTRAINED).  "
            "V_cb and V_ub require sub-leading RS corrections — NOT reproduced here."
        ),
    }


# ---------------------------------------------------------------------------
# c_R sensitivity analysis
# ---------------------------------------------------------------------------

def cr_sensitivity_table(
    pi_kr: float = PI_KR,
    delta_c: float = 0.01,
) -> List[Dict[str, float]]:
    """Return sensitivity of λ_W to ±δc variations in c_R values.

    For each c_R of the down sector (strange and down quarks), compute
    how much λ_W shifts when c_R is varied by ±delta_c.

    Parameters
    ----------
    pi_kr   : float  πkR (default 37).
    delta_c : float  Variation size (default 0.01).

    Returns
    -------
    list of dicts with c_R label, nominal c_R, delta_lambda, sensitivity.
    """
    fit = fit_cr_sector(
        PDG_MASSES_MEV["m_b"],
        PDG_MASSES_MEV["m_s"],
        PDG_MASSES_MEV["m_d"],
        C_L_6D, pi_kr,
    )
    fL_1 = rs_wavefunction_ir(C_L_6D[1], pi_kr)
    fL_2 = rs_wavefunction_ir(C_L_6D[2], pi_kr)
    cr_d1_nom = fit["c_R"][1]
    cr_d2_nom = fit["c_R"][2]
    lam_nom = math.sqrt(
        (fL_2 * rs_wavefunction_ir(cr_d2_nom, pi_kr))
        / (fL_1 * rs_wavefunction_ir(cr_d1_nom, pi_kr))
    )

    rows = []
    for label, cr_nom, which in [
        ("c_R^d_1 (strange)", cr_d1_nom, "d1"),
        ("c_R^d_2 (down)",   cr_d2_nom, "d2"),
    ]:
        for sign, name in [(+1, "+δc"), (-1, "-δc")]:
            if which == "d1":
                cr_d1 = cr_nom + sign * delta_c
                cr_d2 = cr_d2_nom
            else:
                cr_d1 = cr_d1_nom
                cr_d2 = cr_nom + sign * delta_c
            fR1 = rs_wavefunction_ir(cr_d1, pi_kr)
            fR2 = rs_wavefunction_ir(cr_d2, pi_kr)
            ratio = (fL_2 * fR2) / (fL_1 * fR1)
            lam_var = math.sqrt(abs(ratio)) if ratio > 0 else 0.0
            rows.append({
                "parameter": label,
                "variation": name,
                "c_R_nominal": cr_nom,
                "c_R_varied": cr_nom + sign * delta_c,
                "lambda_nominal": lam_nom,
                "lambda_varied": lam_var,
                "delta_lambda": lam_var - lam_nom,
            })
    return rows


# ---------------------------------------------------------------------------
# Pillar 106 report
# ---------------------------------------------------------------------------

def pillar_106_report() -> Dict[str, object]:
    """Comprehensive Pillar 106 status report.

    Returns
    -------
    dict with status, derivation results, residuals, and honest caveats.
    """
    cl_spec = cl_spectrum_6d()
    down_fit = fit_cr_sector(
        PDG_MASSES_MEV["m_b"],
        PDG_MASSES_MEV["m_s"],
        PDG_MASSES_MEV["m_d"],
        C_L_6D,
    )
    up_fit = fit_cr_sector(
        PDG_MASSES_MEV["m_t"],
        PDG_MASSES_MEV["m_c"],
        PDG_MASSES_MEV["m_u"],
        C_L_6D,
    )
    fritzsch = fritzsch_wolfenstein_lambda()
    mismatch = wolfenstein_from_cr_mismatch()
    ckm = ckm_fritzsch_estimate()

    lam_w = fritzsch["lambda_wolfenstein"]
    residual = fritzsch["residual_pct"]

    return {
        "module": "ckm_wolfenstein_from_masses",
        "pillar": 106,
        "status": "CONSTRAINED",
        "epistemic": EPISTEMIC_STATUS,
        "lambda_wolfenstein": lam_w,
        "pdg_lambda": PDG_WOLFENSTEIN_LAMBDA,
        "residual_pct": residual,
        "gate_5pct_passed": residual < 5.0,
        "formula": "lambda_W = sqrt(m_d / m_s) = sqrt(fIR_L2*fIR_R2 / (fIR_L1*fIR_R1))",
        "cl_spectrum": cl_spec,
        "down_sector_fit": down_fit,
        "up_sector_fit": up_fit,
        "fritzsch_result": fritzsch,
        "cr_mismatch_result": mismatch,
        "ckm_fritzsch": ckm,
        "y5_down": down_fit["Y5"],
        "y5_up":   up_fit["Y5"],
        "y5_down_natural": 0.5 < down_fit["Y5"] < 4.0,
        "y5_up_natural":   0.5 < up_fit["Y5"]   < 4.0,
        "improvements_over_pillar_104": [
            "Uses 6D geometric c_L (not birefringence c_L)",
            "Fits c_R from PDG masses via RS inversion (not hardcoded)",
            "Achieves 1.28% residual vs 0.22650 PDG (was ×8 off)",
        ],
        "honest_gaps": [
            "c_R values are FITTED (6 parameters), not derived",
            "Y5_up ≈ 52 — top quark Yukawa unnaturally large in this RS scheme",
            "V_cb, V_ub NOT reproduced at leading Fritzsch order",
            "CP-violating phase δ not addressed",
            "Full CKM matrix requires anarchic 5D Yukawa (beyond rank-1)",
        ],
        "pillar_104_lambda_w": 0.029,
        "pillar_106_lambda_w": lam_w,
        "pdg_lambda_w": PDG_WOLFENSTEIN_LAMBDA,
        "improvement_factor": PDG_WOLFENSTEIN_LAMBDA / 0.029,
    }
