# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 266 — DESI wₐ: quantitative frozen-radion EoS bound from KK geometry.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Derives the quantitative prediction wₐ ≡ 0 from the frozen-radion mechanism
(m_r >> H₀). Provides explicit upper bound |wₐ|_max, DESI tension computation,
and DESI Y5 falsification projection. Honest: HIGH_TENSION at 2.07–2.75σ.
"""

import math

__all__ = [
    "radion_mass_gev",
    "radion_hubble_ratio",
    "frozen_wa_upper_bound",
    "desi_tension_sigma",
    "desi_y5_projection",
    "wa_falsification_threshold",
    "desi_wa_frozen_radion_report",
]

# ── Module constants ──────────────────────────────────────────────────────────
H0_GEV = 1.4436e-42          # Hubble constant today in GeV (H₀ = 67.4 km/s/Mpc)
M_KK_REFERENCE_GEV = 1e6     # 1 TeV reference Kaluza-Klein scale in GeV
M_RADION_FRACTION = 0.1      # m_r ≈ 0.1·M_KK (Goldberger-Wise mechanism)
W0_KK = -1.0                 # UM prediction: w₀ = -1 (frozen field)
WA_KK = 0.0                  # UM prediction: wₐ = 0 (frozen radion)

# DESI DR2 measurements
DESI_WA_CENTRAL_BAO = -0.62
DESI_WA_SIGMA_BAO = 0.30
DESI_WA_CENTRAL_COMBINED = -0.55
DESI_WA_SIGMA_COMBINED = 0.20

# Falsification threshold
FALSIFICATION_SIGMA = 3.0

# DESI Y5 forecast precision
DESI_Y5_SIGMA_WA = 0.15


# ── Physics functions ─────────────────────────────────────────────────────────

def radion_mass_gev(M_KK_gev: float, epsilon_gw: float = M_RADION_FRACTION**2) -> float:
    """Radion mass from Goldberger-Wise mechanism: m_r = sqrt(ε_GW) · M_KK.

    Parameters
    ----------
    M_KK_gev : float
        Kaluza-Klein mass scale in GeV.
    epsilon_gw : float
        Goldberger-Wise parameter ε_GW ∈ (0, 1); default = 0.01 (i.e. m_r = 0.1·M_KK).

    Returns
    -------
    float
        Radion mass in GeV.
    """
    if M_KK_gev <= 0:
        raise ValueError("M_KK_gev must be positive")
    if not (0 < epsilon_gw < 1):
        raise ValueError("epsilon_gw must be in (0, 1)")
    return math.sqrt(epsilon_gw) * M_KK_gev


def radion_hubble_ratio(M_KK_gev: float, epsilon_gw: float = M_RADION_FRACTION**2) -> float:
    """Ratio m_r / H₀ quantifying the frozen-field condition.

    For m_r >> H₀ the radion cannot evolve on the Hubble timescale ⟹ wₐ = 0.

    Returns
    -------
    float
        Dimensionless ratio m_r / H₀.  Should be ~ 10^43 for TeV-scale radion.
    """
    m_r = radion_mass_gev(M_KK_gev, epsilon_gw)
    return m_r / H0_GEV


def frozen_wa_upper_bound(
    M_KK_gev: float,
    epsilon_gw: float = M_RADION_FRACTION**2,
    f_radion: float = 1.0,
) -> float:
    """Upper bound on |wₐ| from frozen-radion EoM.

    From the linearised CPL analysis of the massive scalar field
    (φ̈ + 3Hφ̇ + m_r²φ = 0) with m_r >> H₀:

        |wₐ|_max = (H₀ / m_r)² · f_radion / 2

    The factor 1/2 comes from the coefficient in the linearised EoS expansion.
    f_radion ≤ 1 is the radion fraction of the total dark-energy density.

    Parameters
    ----------
    M_KK_gev : float
        KK mass scale in GeV.
    epsilon_gw : float
        Goldberger-Wise parameter.
    f_radion : float
        Fraction of dark energy carried by the radion (0 < f ≤ 1).

    Returns
    -------
    float
        |wₐ|_max — extraordinarily small for any TeV-scale radion.
    """
    if not (0 < f_radion <= 1.0):
        raise ValueError("f_radion must be in (0, 1]")
    ratio = radion_hubble_ratio(M_KK_gev, epsilon_gw)
    return f_radion / (2.0 * ratio**2)


def desi_tension_sigma(wa_pred: float, wa_obs: float, sigma_obs: float) -> float:
    """Tension in units of σ between prediction and observation.

    Parameters
    ----------
    wa_pred : float
        Theoretical prediction (wₐ = 0 for UM).
    wa_obs : float
        Observed central value.
    sigma_obs : float
        Observational 1σ uncertainty.

    Returns
    -------
    float
        |wa_pred - wa_obs| / sigma_obs
    """
    if sigma_obs <= 0:
        raise ValueError("sigma_obs must be positive")
    return abs(wa_pred - wa_obs) / sigma_obs


def desi_y5_projection(wa_central: float, sigma_y5: float = DESI_Y5_SIGMA_WA) -> dict:
    """Project DESI Y5 tension assuming current central value persists.

    Parameters
    ----------
    wa_central : float
        Best-fit wₐ from current data (expected to persist to Y5).
    sigma_y5 : float
        Forecast 1σ precision on wₐ at DESI Y5 (default 0.15).

    Returns
    -------
    dict
        Keys: sigma_y5, tension_y5_sigma, will_falsify, wa_central.
    """
    tension = desi_tension_sigma(WA_KK, wa_central, sigma_y5)
    return {
        "wa_central": wa_central,
        "sigma_y5": sigma_y5,
        "tension_y5_sigma": tension,
        "will_falsify": tension >= FALSIFICATION_SIGMA,
    }


def wa_falsification_threshold(sigma_target: float, sigma_obs: float) -> float:
    """Return the |wₐ| value at which tension equals sigma_target.

    |wₐ|_critical = sigma_target · sigma_obs

    Parameters
    ----------
    sigma_target : float
        Target tension (e.g. 3.0 for falsification).
    sigma_obs : float
        Observational 1σ uncertainty.

    Returns
    -------
    float
        Critical |wₐ| value.
    """
    return sigma_target * sigma_obs


def desi_wa_frozen_radion_report(M_KK_gev: float = M_KK_REFERENCE_GEV) -> dict:
    """Full Pillar 266 verdict: frozen-radion wₐ bound vs DESI DR2.

    Parameters
    ----------
    M_KK_gev : float
        KK mass scale in GeV (default 1 TeV).

    Returns
    -------
    dict
        Comprehensive report with all required Pillar 266 keys.
    """
    epsilon_gw = M_RADION_FRACTION**2

    m_r = radion_mass_gev(M_KK_gev, epsilon_gw)
    ratio = radion_hubble_ratio(M_KK_gev, epsilon_gw)
    wa_bound = frozen_wa_upper_bound(M_KK_gev, epsilon_gw)

    bao_sigma = desi_tension_sigma(WA_KK, DESI_WA_CENTRAL_BAO, DESI_WA_SIGMA_BAO)
    combined_sigma = desi_tension_sigma(WA_KK, DESI_WA_CENTRAL_COMBINED, DESI_WA_SIGMA_COMBINED)

    max_sigma = max(bao_sigma, combined_sigma)
    verdict = "FALSIFIED" if max_sigma >= FALSIFICATION_SIGMA else "HIGH_TENSION"

    y5_bao = desi_y5_projection(DESI_WA_CENTRAL_BAO)
    y5_combined = desi_y5_projection(DESI_WA_CENTRAL_COMBINED)
    desi_y5_risk = y5_bao["will_falsify"] or y5_combined["will_falsify"]

    crit_bao = wa_falsification_threshold(FALSIFICATION_SIGMA, DESI_WA_SIGMA_BAO)
    crit_combined = wa_falsification_threshold(FALSIFICATION_SIGMA, DESI_WA_SIGMA_COMBINED)

    return {
        # Radion physics
        "m_radion_gev": m_r,
        "m_radion_over_hubble": ratio,
        "epsilon_gw": epsilon_gw,
        # UM predictions
        "w0_prediction": W0_KK,
        "wa_prediction": WA_KK,
        "wa_upper_bound": wa_bound,
        # DESI tension
        "desi_tension_bao_sigma": bao_sigma,
        "desi_tension_combined_sigma": combined_sigma,
        "desi_wa_central_bao": DESI_WA_CENTRAL_BAO,
        "desi_wa_central_combined": DESI_WA_CENTRAL_COMBINED,
        # Verdict
        "verdict": verdict,
        # Falsification thresholds
        "wa_critical_bao": crit_bao,
        "wa_critical_combined": crit_combined,
        # Y5 projection
        "desi_y5_falsification_risk": desi_y5_risk,
        "desi_y5_tension_bao": y5_bao["tension_y5_sigma"],
        "desi_y5_tension_combined": y5_combined["tension_y5_sigma"],
        # Honest closure note
        "closure_note": (
            f"UM predicts wₐ ≡ 0 (frozen radion, m_r/H₀ ≈ {ratio:.2e} >> 1). "
            f"|wₐ|_max ≈ {wa_bound:.2e} — effectively exact zero. "
            f"DESI DR2 reports {bao_sigma:.2f}σ (BAO) / {combined_sigma:.2f}σ (combined) tension. "
            f"Verdict: {verdict}. "
            f"DESI Y5 falsification risk: {desi_y5_risk}. "
            "This is an honest open tension, not yet at 3σ falsification threshold."
        ),
    }
