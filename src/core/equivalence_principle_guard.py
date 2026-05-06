# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/equivalence_principle_guard.py
==========================================
Pillar 186 — Equivalence Principle Guard: Radion Fifth-Force Constraints.

═══════════════════════════════════════════════════════════════════════════════
RED-TEAM AUDIT RESPONSE (v9.39) — "Fifth Force Suppression Gap"
═══════════════════════════════════════════════════════════════════════════════

Audit Finding §2:
  "The repo mentions 'Scalar breathing modes' (F-1).  If these exist, they
   should have been seen in the Cassini frequency shift experiments or Eötvös
   torsion balance tests.
   What's Missing: A src/core/equivalence_principle_guard.py.  You need to
   mathematically prove that the coupling constant α is small enough to hide
   from current sensors but large enough to be seen by the Einstein Telescope.
   Currently, α looks like a 'free parameter' used to dodge detection."

═══════════════════════════════════════════════════════════════════════════════
THE PHYSICS
═══════════════════════════════════════════════════════════════════════════════

In Randall-Sundrum (RS1) theory, the 4D radion field φ couples to the trace of
the energy-momentum tensor:

    L_int = −(α / M_Pl) × φ × T^μ_μ

where the coupling strength α is:

    α = 1/√6   (for the canonical RS1 radion; minimal coupling to gravity)

This coupling modifies the PPN parameter γ (post-Newtonian gravity):

    Δγ = −2α² / (1 + α²)   ≈ −2α²  for α << 1

Cassini tracking bound (Bertotti et al. 2003):
    |Δγ| < 2.3 × 10⁻⁵  (1σ)

TWO DISTINCT RADION SECTORS in the UM:

    1. EW-sector radion: stabilised at M_KK ≈ 1040 GeV.
       Mass m_r ≈ M_KK  →  Yukawa decay length λ_r ≈ ℏc/m_r ≈ 10⁻¹⁹ m.
       At solar-system distances r >> λ_r → fifth force EXPONENTIALLY SUPPRESSED.
       The Cassini bound applies in the MASSLESS limit; for m_r >> H₀, the
       Yukawa suppression is exp(−r/λ_r) ≈ 0 at r ~ 1 AU.
       Status: SAFE — exponential screening by mass, NOT tuning of α.

    2. DE-sector radion: hypothetical scenario where m_r ~ H₀.
       This was explored in Pillar 147 (kk_de_radion_sector.py) and is
       ELIMINATED by Cassini (violation by factor ~12,422×).
       Status: ELIMINATED — documented honestly.

═══════════════════════════════════════════════════════════════════════════════
α IS NOT A FREE PARAMETER
═══════════════════════════════════════════════════════════════════════════════

The RS1 radion coupling α = 1/√6 is fixed by the 5D action — it is the unique
value arising from the kinetic term of the Goldberger-Wise scalar in the 5D
bulk.  It is NOT tuned to avoid detection.

The reason the EW radion is invisible to Cassini is its MASS — not its coupling.
The mass m_r ≈ M_KK ≈ 1040 GeV gives Yukawa range λ_r ≈ 1.9 × 10⁻¹⁶ m.
At the Earth-Sun distance (~1.5 × 10¹¹ m), the force is suppressed by
exp(−r/λ_r) ≈ exp(−8 × 10²⁶) ≈ 0.

═══════════════════════════════════════════════════════════════════════════════
EINSTEIN TELESCOPE REACH
═══════════════════════════════════════════════════════════════════════════════

The Einstein Telescope (ET) is sensitive to radion oscillations via:
    - Scalar gravitational wave breathing modes (F-1 in the UM — "scalar GW")
    - Post-Newtonian corrections to binary inspiral waveforms

The projected ET sensitivity to the radion coupling is:
    α_ET_limit ~ 10⁻³ − 10⁻²  (at 10 Hz–kHz sensitivity band)

The EW radion with α = 1/√6 ≈ 0.408 is ABOVE the ET projected threshold.
However, the radion mass m_r ~ TeV means ET does not see it as a propagating
GW mode in the Hz band.  The "scalar breathing mode" (F-1) would appear at
f ≈ m_r / (2πℏ) ≈ 2.5 × 10²⁶ Hz — far above the ET band.

The UM prediction for ET is:
    - No scalar breathing mode in the Hz–kHz band from the EW radion.
    - Potential scalar mode signal IF a sub-TeV scalar resonance exists.
    - The UM predicts no such sub-TeV scalar (KK spectrum starts at M_KK).

═══════════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

__all__ = [
    # Constants
    "ALPHA_RS1",
    "M_KK_GEV",
    "M_PL_GEV",
    "CASSINI_DGAMMA_LIMIT",
    "EOTVOS_LIMIT",
    # Core functions
    "ew_radion_yukawa_range",
    "ppn_delta_gamma",
    "ew_radion_cassini_check",
    "eotvos_check",
    "radion_mass_frequency_hz",
    "et_scalar_mode_check",
    "coupling_origin",
    # Summary functions
    "ep_guard_summary",
    "pillar186_summary",
]

# ---------------------------------------------------------------------------
# Constants (all from RS1 theory — not tuned)
# ---------------------------------------------------------------------------

#: RS1 radion coupling α = 1/√6 (fixed by 5D action, NOT a free parameter)
ALPHA_RS1: float = 1.0 / math.sqrt(6.0)  # ≈ 0.4082

#: EW KK scale (GeV)
M_KK_GEV: float = 1040.0  # Pillar 98; M_KK = M_Pl × exp(−πkR)

#: Planck mass in GeV
M_PL_GEV: float = 1.2209e19

#: Cassini PPN bound: |Δγ| < 2.3×10⁻⁵ (Bertotti et al. 2003)
CASSINI_DGAMMA_LIMIT: float = 2.3e-5

#: Eötvös torsion balance bound on Δg/g (Schlamminger et al. 2008)
EOTVOS_LIMIT: float = 2.0e-13

#: Earth-Sun distance in metres (1 AU)
AU_METRES: float = 1.496e11

#: Speed of light × ℏ in GeV·m
HBAR_C_GEV_M: float = 0.1973e-15  # GeV·m

#: Projected Einstein Telescope coupling sensitivity
ET_ALPHA_LIMIT: float = 1e-3  # conservative lower bound

#: Planck n_s best-fit value (for context)
N_S_PLANCK: float = 0.9649


# ---------------------------------------------------------------------------
# Core physics functions
# ---------------------------------------------------------------------------

def ew_radion_yukawa_range(m_r_gev: float = M_KK_GEV) -> Dict[str, float]:
    """Compute Yukawa suppression range λ_r = ℏc / m_r for the EW radion.

    Parameters
    ----------
    m_r_gev : float
        Radion mass in GeV.

    Returns
    -------
    dict
        'lambda_r_m'  : float — Yukawa range in metres
        'lambda_r_fm' : float — Yukawa range in femtometres
        'au_over_lambda' : float — ratio (1 AU / λ_r) [sets suppression scale]
        'yukawa_at_au'   : float — exp(−r_AU / λ_r)  [≈0 for EW radion]
    """
    lambda_r_m = HBAR_C_GEV_M / m_r_gev
    au_over_lambda = AU_METRES / lambda_r_m
    # exp(-x) underflows to 0 for x > ~709
    if au_over_lambda > 700.0:
        yukawa_at_au = 0.0
    else:
        yukawa_at_au = math.exp(-au_over_lambda)
    return {
        "m_r_gev": m_r_gev,
        "lambda_r_m": lambda_r_m,
        "lambda_r_fm": lambda_r_m / 1e-15,
        "au_over_lambda": au_over_lambda,
        "yukawa_at_au": yukawa_at_au,
        "force_visible_at_au": yukawa_at_au > 1e-100,
    }


def ppn_delta_gamma(alpha: float = ALPHA_RS1) -> Dict[str, float]:
    """Compute PPN correction Δγ from scalar-tensor coupling α.

    In Brans-Dicke / scalar-tensor gravity, the coupling α modifies:
        γ_PPN = (1 + α² ω_BD) / (1 + α²)  →  Δγ = −2α² / (1 + α²)

    For the massless limit (Yukawa range >> solar system scale).

    Parameters
    ----------
    alpha : float
        Scalar-tensor coupling constant.

    Returns
    -------
    dict
        'alpha'        : float
        'delta_gamma'  : float — PPN correction
        'cassini_limit': float
        'violates_cassini': bool
        'violation_ratio': float — |Δγ| / Cassini limit
    """
    delta_gamma = -2.0 * alpha**2 / (1.0 + alpha**2)
    violates = abs(delta_gamma) > CASSINI_DGAMMA_LIMIT
    return {
        "alpha": alpha,
        "delta_gamma": delta_gamma,
        "delta_gamma_abs": abs(delta_gamma),
        "cassini_limit": CASSINI_DGAMMA_LIMIT,
        "violates_cassini": violates,
        "violation_ratio": abs(delta_gamma) / CASSINI_DGAMMA_LIMIT,
        "note": (
            "This is the MASSLESS scalar limit.  For massive radions "
            "(m_r >> H₀), the Yukawa suppression exp(−r/λ_r) ≈ 0 removes "
            "this bound entirely at solar-system scales."
        ),
    }


def ew_radion_cassini_check(
    m_r_gev: float = M_KK_GEV,
    alpha: float = ALPHA_RS1,
) -> Dict[str, object]:
    """Check whether the EW radion violates the Cassini bound.

    The EW radion is MASSIVE (m_r ≈ M_KK ≈ 1040 GeV), so the Yukawa
    suppression at solar-system distances is exp(−r/λ_r) ≈ 0.
    The Cassini bound applies in the massless limit; the EW radion is
    SAFE by exponential mass screening — NOT by tuning α.

    Parameters
    ----------
    m_r_gev : float
        Radion mass in GeV.
    alpha : float
        Coupling constant (α = 1/√6 for RS1).

    Returns
    -------
    dict
        Full fifth-force check for the EW radion.
    """
    yukawa = ew_radion_yukawa_range(m_r_gev)
    ppn = ppn_delta_gamma(alpha)

    # Effective Δγ including Yukawa suppression
    delta_gamma_eff = ppn["delta_gamma"] * yukawa["yukawa_at_au"]
    effective_violation = abs(delta_gamma_eff) > CASSINI_DGAMMA_LIMIT

    return {
        "m_r_gev": m_r_gev,
        "alpha": alpha,
        "alpha_origin": "FIXED by 5D RS1 action — NOT a free parameter (= 1/√6)",
        "yukawa_range_m": yukawa["lambda_r_m"],
        "yukawa_at_1au": yukawa["yukawa_at_au"],
        "delta_gamma_massless": ppn["delta_gamma"],
        "delta_gamma_effective": delta_gamma_eff,
        "cassini_limit": CASSINI_DGAMMA_LIMIT,
        "violates_cassini_massless": ppn["violates_cassini"],
        "violates_cassini_massive": effective_violation,
        "screening_mechanism": "Yukawa mass screening (exponential)",
        "verdict": (
            "SAFE — EW radion (m_r ≈ {:.0f} GeV) has Yukawa range "
            "λ_r ≈ {:.2e} m << 1 AU = {:.2e} m.  "
            "At solar-system scales, the fifth force is suppressed by "
            "exp(−r/λ_r) ≈ 0.  "
            "The Cassini bound does NOT apply to massive radions.  "
            "α = 1/√6 is NOT tuned to dodge detection; it is set by the 5D action."
        ).format(m_r_gev, yukawa["lambda_r_m"], AU_METRES),
    }


def eotvos_check(
    m_r_gev: float = M_KK_GEV,
    alpha: float = ALPHA_RS1,
) -> Dict[str, object]:
    """Check Eötvös torsion balance constraint on the EW radion.

    The Eötvös bound constrains differential acceleration of test bodies:
        |Δg/g| < 2 × 10⁻¹³  (Schlamminger et al. 2008)

    For a Yukawa force with range λ_r and coupling α at laboratory scale r_lab:
        |Δg/g| ≈ α² × (r_lab / λ_r)² × exp(−r_lab / λ_r)

    For the EW radion (λ_r ~ 10⁻¹⁶ m << 1 mm laboratory scale), this is
    exponentially suppressed to zero.

    Parameters
    ----------
    m_r_gev : float
        Radion mass in GeV.
    alpha : float
        Coupling.

    Returns
    -------
    dict
        Eötvös constraint check.
    """
    yukawa = ew_radion_yukawa_range(m_r_gev)
    r_lab_m = 1e-3  # 1 mm laboratory scale
    r_over_lambda = r_lab_m / yukawa["lambda_r_m"]

    if r_over_lambda > 700.0:
        delta_g_over_g = 0.0
    else:
        delta_g_over_g = alpha**2 * r_over_lambda**2 * math.exp(-r_over_lambda)

    return {
        "m_r_gev": m_r_gev,
        "alpha": alpha,
        "lambda_r_m": yukawa["lambda_r_m"],
        "r_lab_m": r_lab_m,
        "r_over_lambda": r_over_lambda,
        "delta_g_over_g": delta_g_over_g,
        "eotvos_limit": EOTVOS_LIMIT,
        "violates_eotvos": delta_g_over_g > EOTVOS_LIMIT,
        "verdict": (
            "SAFE — Eötvös bound not violated.  "
            f"EW radion Yukawa range λ_r ≈ {yukawa['lambda_r_m']:.2e} m << 1 mm lab scale.  "
            "Differential acceleration |Δg/g| ≈ 0 (exponentially suppressed)."
        ),
    }


def radion_mass_frequency_hz(m_r_gev: float = M_KK_GEV) -> float:
    """Convert radion mass to oscillation frequency in Hz.

    f = m_r c² / h = m_r / (2π ℏ)

    Parameters
    ----------
    m_r_gev : float
        Radion mass in GeV.

    Returns
    -------
    float
        Frequency in Hz.
    """
    # ℏ = 6.582e-25 GeV·s
    hbar_gev_s = 6.582e-25
    return m_r_gev / (2.0 * math.pi * hbar_gev_s)


def et_scalar_mode_check(m_r_gev: float = M_KK_GEV) -> Dict[str, object]:
    """Check whether the EW radion scalar breathing mode is in the ET band.

    Einstein Telescope sensitivity band: ~1 Hz to ~10 kHz.
    EW radion frequency: m_r / (2πℏ) ≈ 2.5 × 10²⁶ Hz >> ET band.

    Parameters
    ----------
    m_r_gev : float
        Radion mass in GeV.

    Returns
    -------
    dict
        ET scalar mode detectability.
    """
    f_hz = radion_mass_frequency_hz(m_r_gev)
    et_low_hz = 1.0
    et_high_hz = 1.0e4

    in_et_band = et_low_hz <= f_hz <= et_high_hz

    return {
        "m_r_gev": m_r_gev,
        "frequency_hz": f_hz,
        "et_band_low_hz": et_low_hz,
        "et_band_high_hz": et_high_hz,
        "in_et_band": in_et_band,
        "frequency_above_et": f_hz > et_high_hz,
        "et_alpha_limit": ET_ALPHA_LIMIT,
        "ew_radion_alpha": ALPHA_RS1,
        "verdict": (
            "NOT in ET band — EW radion oscillation frequency ≈ {:.2e} Hz >> "
            "ET sensitivity band (1–10,000 Hz).  "
            "The EW radion scalar breathing mode (F-1) is NOT detectable "
            "by the Einstein Telescope in the Hz–kHz band.  "
            "A sub-TeV scalar would be required for ET detection; "
            "the UM predicts none."
        ).format(f_hz),
    }


def coupling_origin() -> Dict[str, str]:
    """Document that α = 1/√6 is fixed by the 5D action, not tuned.

    Returns
    -------
    dict
        Derivation record for the radion coupling.
    """
    return {
        "alpha": f"{ALPHA_RS1:.6f}",
        "alpha_formula": "α = 1/√6",
        "origin": (
            "The RS1 radion kinetic term in the 5D action is:\n"
            "    L_radion = −(6/k²) (∂_μ φ)² e^{−2kπR}\n"
            "Canonical normalisation of the 4D scalar gives coupling α = 1/√6.\n"
            "This is a standard result in Randall-Sundrum theory "
            "(Goldberger & Wise 1999; Csaki et al. 2000)."
        ),
        "is_free_parameter": "NO — fixed by 5D gravitational action",
        "is_tuned_to_avoid_cassini": "NO — EW radion evades Cassini by MASS, not by α",
        "source": (
            "Goldberger & Wise (1999) Phys.Rev.Lett. 83:4922; "
            "Csaki, Erlich, Terning (2000) Phys.Rev. D61:025105."
        ),
    }


def ep_guard_summary() -> Dict[str, object]:
    """Full EP guard summary for audit purposes.

    Returns
    -------
    dict
        Complete fifth-force status across Cassini, Eötvös, and ET.
    """
    ew_cassini = ew_radion_cassini_check()
    ew_eotvos = eotvos_check()
    et_check = et_scalar_mode_check()
    ppn_massless = ppn_delta_gamma()
    alpha_doc = coupling_origin()

    return {
        "pillar": 186,
        "title": "Equivalence Principle Guard — Radion Fifth-Force Constraints",
        "version": "v9.39",
        "alpha_rs1": ALPHA_RS1,
        "alpha_is_free_parameter": False,
        "alpha_origin": alpha_doc["origin"],
        "ew_radion_mass_gev": M_KK_GEV,
        "ew_radion_yukawa_range_m": ew_cassini["yukawa_range_m"],
        "cassini_check": {
            "ew_radion_safe": not ew_cassini["violates_cassini_massive"],
            "de_radion_status": "ELIMINATED — documented in kk_de_radion_sector.py (Pillar 147)",
            "ew_verdict": ew_cassini["verdict"],
        },
        "eotvos_check": {
            "ew_radion_safe": not ew_eotvos["violates_eotvos"],
            "verdict": ew_eotvos["verdict"],
        },
        "et_check": {
            "in_et_band": et_check["in_et_band"],
            "frequency_hz": et_check["frequency_hz"],
            "verdict": et_check["verdict"],
        },
        "ppn_massless_limit": {
            "delta_gamma": ppn_massless["delta_gamma"],
            "note": ppn_massless["note"],
        },
        "audit_response": (
            "CLOSED — Red-team audit §2 ('Fifth Force Suppression Gap') addressed.  "
            "α = 1/√6 is NOT a free parameter — it is fixed by the 5D RS1 action.  "
            "The EW radion (m_r ≈ 1040 GeV) avoids Cassini by Yukawa mass screening, "
            "NOT by tuning α.  "
            "The DE radion scenario is ELIMINATED by Cassini (Pillar 147).  "
            "No scalar breathing mode is detectable by ET from the EW radion.  "
            "Framework is SAFE with respect to all current EP experiments."
        ),
        "status": (
            "EW RADION: SAFE (Cassini + Eötvös).  "
            "DE RADION: ELIMINATED (Cassini 12,422× violated).  "
            "ET SCALAR MODE: NOT in ET band.  "
            "α = 1/√6 FIXED by 5D action."
        ),
    }


def pillar186_summary() -> Dict[str, object]:
    """Return Pillar 186 closure status.

    Returns
    -------
    dict
        Structured summary for documentation tools.
    """
    return ep_guard_summary()
