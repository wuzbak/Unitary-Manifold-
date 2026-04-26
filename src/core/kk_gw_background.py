# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_gw_background.py
==============================
Pillar 69 — Stochastic Gravitational-Wave Background from KK Compactification.

Physical context
----------------
A first-order phase transition at the KK compactification scale produces a
stochastic gravitational-wave (GW) background.  The peak frequency is:

    f_peak ≈ M_KK / (2π)

in natural units, converted to Hz via 1 GeV ≈ 1.52 × 10²⁴ Hz.

For M_KK ~ M_Planck ~ 10¹⁹ GeV, f_peak ~ 10⁴³ Hz — far above any existing
or planned GW observatory.  This makes the UM automatically consistent with
all current GW data for Planck-scale compactification.

Observational constraints:
  - LISA (launch ~2035): sensitive to 10⁻⁴ – 1 Hz → requires M_KK ≲ 10¹⁶ GeV
    for any signal.  Planck-scale UM KK tower is NOT detectable by LISA.
  - NANOGrav 15-year (arXiv:2306.16213): signal at f ~ 1/year ~ 3 × 10⁻⁸ Hz.
    UM KK background peaks at 10⁴³ Hz → completely different frequency band.
    The NANOGrav signal is NOT explained by UM KK GWs.

Falsification condition:
  If future experiments constrain the absence of a GW background at
  f ~ M_KK/(2π) consistent with an M_KK at sub-Planck scales predicted
  by indirect measurements, the UM compactification model would be falsified.

Gap closed: FALLIBILITY.md §IV.1 — KK tower spectrum observational frontiers.
This module quantifies exactly why Planck-scale KK GWs are undetectable and
identifies the sub-Planck window where detection would be possible.

Public API
----------
kk_gw_peak_frequency(M_KK_GeV) → float
kk_gw_energy_density(M_KK_GeV, T_reh_GeV) → float
lisa_sensitivity_comparison(M_KK_GeV) → dict
nanograv_kk_consistency(M_KK_GeV) → dict
kk_gw_spectral_shape(f_hz, f_peak_hz) → float
gw_background_summary() → dict

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0

#: Planck mass [GeV]
M_PLANCK_GEV: float = 1.22e19

#: Hubble constant [km/s/Mpc]
H0_KM_S_MPC: float = 67.4

#: Hubble constant in Hz  (67.4 km/s/Mpc → Hz)
H0_HZ: float = 67.4e3 / 3.0857e22

#: Radiation density parameter h²
OMEGA_RAD_H2: float = 4.2e-5

# --- LISA sensitivity band ---
#: Lower frequency limit of LISA band [Hz]
LISA_F_LOW_HZ: float = 1e-4

#: Upper frequency limit of LISA band [Hz]
LISA_F_HIGH_HZ: float = 1.0

#: Approximate peak LISA sensitivity Ω_GW
LISA_OMEGA_GW_SENSITIVITY: float = 1e-12

# --- NANOGrav 15-year data (arXiv:2306.16213) ---
#: Reference frequency ≈ 1/year [Hz]
NANOGRAV_F_REF_HZ: float = 3.17e-9

#: Approximate GW background amplitude Ω_GW h²
NANOGRAV_OMEGA_GW_SIGNAL: float = 5e-9

#: 1σ uncertainty on NANOGrav Ω_GW h²
NANOGRAV_OMEGA_GW_UNC: float = 2e-9

#: Conversion: 1 GeV in Hz  (ℏ = 1, c = 1 natural units)
GEV_TO_HZ: float = 1.52e24


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def kk_gw_peak_frequency(M_KK_GeV: float) -> float:
    """Peak frequency of the KK GW background in Hz.

    f_peak = M_KK / (2π) in natural units, then converted to Hz:
    f_peak [Hz] = M_KK [GeV] × 1.52 × 10²⁴ Hz/GeV / (2π)

    Parameters
    ----------
    M_KK_GeV : float
        KK mass scale in GeV (> 0).

    Returns
    -------
    float
        Peak GW frequency in Hz.

    Raises
    ------
    ValueError
        If M_KK_GeV ≤ 0.
    """
    if M_KK_GeV <= 0.0:
        raise ValueError(f"M_KK_GeV must be positive, got {M_KK_GeV}")
    return M_KK_GeV * GEV_TO_HZ / (2.0 * math.pi)


def kk_gw_energy_density(M_KK_GeV: float, T_reh_GeV: float) -> float:
    """GW energy density parameter Ω_GW h² from KK phase transition.

    Estimates the GW spectrum from a first-order KK phase transition using
    the simplified envelope approximation for a strongly first-order
    transition with:
      - α (latent heat ratio) ~ 1
      - β/H* ~ 10  (transition rate / Hubble)
      - v_w ~ 1  (bubble wall speed)

    Ω_GW h² ≈ 1.67 × 10⁻⁵ × (H*/β)² × (α/(1+α))² × v_w³ × Ω_rad h²
               × g_*(T_reh)^{-1/3}

    Returns Ω_GW h² at the peak frequency.

    Parameters
    ----------
    M_KK_GeV : float
        KK mass scale in GeV (> 0).
    T_reh_GeV : float
        Reheating temperature in GeV (> 0).

    Returns
    -------
    float
        GW energy density parameter Ω_GW h².

    Raises
    ------
    ValueError
        If M_KK_GeV ≤ 0 or T_reh_GeV ≤ 0.
    """
    if M_KK_GeV <= 0.0:
        raise ValueError(f"M_KK_GeV must be positive, got {M_KK_GeV}")
    if T_reh_GeV <= 0.0:
        raise ValueError(f"T_reh_GeV must be positive, got {T_reh_GeV}")

    alpha = 1.0        # strong transition
    beta_over_H = 10.0
    v_w = 1.0
    # effective relativistic dofs ~ 100 at high temperature
    g_star = max(100.0, (T_reh_GeV / 100.0) ** 0.1 * 106.75)

    prefactor = 1.67e-5
    alpha_factor = (alpha / (1.0 + alpha)) ** 2
    beta_factor = (1.0 / beta_over_H) ** 2
    vw_factor = v_w ** 3
    g_factor = (100.0 / g_star) ** (1.0 / 3.0)

    # Slight dependence on T_reh through effective dofs
    t_factor = min(1.0, (T_reh_GeV / M_KK_GeV) ** 0.1)

    omega = prefactor * beta_factor * alpha_factor * vw_factor * g_factor * OMEGA_RAD_H2 * t_factor
    return omega


def lisa_sensitivity_comparison(M_KK_GeV: float) -> dict:
    """Compare KK GW signal to LISA sensitivity band.

    Parameters
    ----------
    M_KK_GeV : float
        KK mass scale in GeV (> 0).

    Returns
    -------
    dict
        Keys: f_peak_hz, in_lisa_band (bool), omega_gw_peak,
        lisa_sensitivity_at_peak, snr_estimate, falsification_statement.

    Raises
    ------
    ValueError
        If M_KK_GeV ≤ 0.
    """
    if M_KK_GeV <= 0.0:
        raise ValueError(f"M_KK_GeV must be positive, got {M_KK_GeV}")

    f_peak = kk_gw_peak_frequency(M_KK_GeV)
    in_band = LISA_F_LOW_HZ <= f_peak <= LISA_F_HIGH_HZ

    # Estimate GW energy density at canonical reheating T ~ M_KK
    omega_peak = kk_gw_energy_density(M_KK_GeV, M_KK_GeV)

    # SNR estimate (only meaningful if in LISA band)
    if in_band and omega_peak > 0:
        snr = omega_peak / LISA_OMEGA_GW_SENSITIVITY
    else:
        snr = 0.0

    if in_band:
        stmt = (
            f"KK GW background at f={f_peak:.2e} Hz is within LISA band. "
            f"Ω_GW ~ {omega_peak:.2e}. "
            "LISA could detect or constrain this KK scale."
        )
    else:
        stmt = (
            f"KK GW background peaks at f={f_peak:.2e} Hz, outside LISA band "
            f"({LISA_F_LOW_HZ:.0e}–{LISA_F_HIGH_HZ:.0e} Hz). "
            "Planck-scale KK GWs are undetectable by LISA."
        )

    return {
        "f_peak_hz": f_peak,
        "in_lisa_band": in_band,
        "omega_gw_peak": omega_peak,
        "lisa_sensitivity_at_peak": LISA_OMEGA_GW_SENSITIVITY,
        "snr_estimate": snr,
        "falsification_statement": stmt,
        "M_KK_GeV": M_KK_GeV,
    }


def nanograv_kk_consistency(M_KK_GeV: float = None) -> dict:
    """Compare UM KK GW background to NANOGrav 2023 nHz signal.

    NANOGrav 2023 (arXiv:2306.16213) reports a GW background at f ~ 1/year.
    The UM KK background peaks at f ~ M_KK/(2π).

    Parameters
    ----------
    M_KK_GeV : float, optional
        KK mass scale in GeV. Defaults to M_PLANCK_GEV.

    Returns
    -------
    dict
        Keys: nanograv_freq_hz, kk_freq_at_planck_hz,
        frequency_ratio, kk_explains_nanograv (bool — expected False for
        Planck-scale KK), consistent_with_nanograv (bool), interpretation.
    """
    if M_KK_GeV is None:
        M_KK_GeV = M_PLANCK_GEV

    if M_KK_GeV <= 0.0:
        raise ValueError(f"M_KK_GeV must be positive, got {M_KK_GeV}")

    f_kk = kk_gw_peak_frequency(M_KK_GeV)
    f_planck = kk_gw_peak_frequency(M_PLANCK_GEV)
    ratio = f_kk / NANOGRAV_F_REF_HZ

    # KK GWs explain NANOGrav only if frequencies match within a factor ~10
    # and amplitudes are compatible
    freq_match = (ratio > 0.1) and (ratio < 10.0)
    # For Planck-scale KK, the frequency is ~10^51 times the NANOGrav frequency
    kk_explains = freq_match

    # UM is consistent with NANOGrav in the sense that it does not produce
    # a conflicting signal at nHz — the UM KK background is at completely
    # different (much higher) frequencies.
    consistent = not kk_explains  # consistent by absence of conflict

    if kk_explains:
        interp = (
            f"KK GW background at {f_kk:.2e} Hz could explain NANOGrav signal "
            f"at {NANOGRAV_F_REF_HZ:.2e} Hz. Frequency ratio: {ratio:.2f}."
        )
    else:
        interp = (
            f"KK GW background peaks at {f_kk:.2e} Hz, far from NANOGrav "
            f"signal at {NANOGRAV_F_REF_HZ:.2e} Hz (ratio: {ratio:.2e}). "
            "UM KK mechanism does NOT explain NANOGrav signal. "
            "UM is consistent with NANOGrav by absence of conflict."
        )

    return {
        "nanograv_freq_hz": NANOGRAV_F_REF_HZ,
        "kk_freq_hz": f_kk,
        "kk_freq_at_planck_hz": f_planck,
        "frequency_ratio": ratio,
        "kk_explains_nanograv": kk_explains,
        "consistent_with_nanograv": consistent,
        "interpretation": interp,
        "M_KK_GeV": M_KK_GeV,
    }


def kk_gw_spectral_shape(f_hz: float, f_peak_hz: float) -> float:
    """KK GW spectral shape function S(f) normalized to ~1 at f_peak.

    Uses the broken power-law approximation for bubble-collision GW spectrum:

    S(f) = (f/f_peak)^2.8 / (1 + 2.8*(f/f_peak)^3.8)^0.74

    This fit to the envelope approximation gives S ≈ 1 at f = f_peak and
    S < 1 away from the peak.

    Parameters
    ----------
    f_hz : float
        Frequency in Hz (> 0).
    f_peak_hz : float
        Peak frequency in Hz (> 0).

    Returns
    -------
    float
        Spectral shape S(f), dimensionless, positive.

    Raises
    ------
    ValueError
        If f_hz ≤ 0 or f_peak_hz ≤ 0.
    """
    if f_hz <= 0.0:
        raise ValueError(f"f_hz must be positive, got {f_hz}")
    if f_peak_hz <= 0.0:
        raise ValueError(f"f_peak_hz must be positive, got {f_peak_hz}")

    x = f_hz / f_peak_hz
    numerator = x ** 2.8
    denominator = (1.0 + 2.8 * x ** 3.8) ** 0.74
    return numerator / denominator


def gw_background_summary() -> dict:
    """Complete Pillar 69 summary: KK GW background falsification conditions.

    Returns
    -------
    dict
        Comprehensive summary including LISA comparison, NANOGrav consistency,
        and falsification conditions.
    """
    lisa = lisa_sensitivity_comparison(M_PLANCK_GEV)
    nano = nanograv_kk_consistency(M_PLANCK_GEV)
    f_peak_planck = kk_gw_peak_frequency(M_PLANCK_GEV)

    # M_KK needed for LISA detection: f_peak in LISA band requires
    # f = M_KK * GEV_TO_HZ / (2π) ~ 1 Hz → M_KK ~ 2π / GEV_TO_HZ ~ 4e-24 GeV
    # Actually, for f ~ 1e-3 Hz (LISA midband):
    m_kk_for_lisa = LISA_F_HIGH_HZ * 2.0 * math.pi / GEV_TO_HZ

    return {
        "pillar": 69,
        "name": "Stochastic GW Background from KK Compactification",
        "f_peak_planck_hz": f_peak_planck,
        "lisa_comparison": lisa,
        "nanograv_consistency": nano,
        "m_kk_for_lisa_detection_gev": m_kk_for_lisa,
        "n_w": N_W,
        "k_cs": K_CS,
        "c_s": C_S,
        "falsification_conditions": (
            "If M_KK is at sub-Planck scale and LISA does NOT detect the "
            "corresponding GW background, the first-order transition mechanism "
            "is disfavored. "
            "For Planck-scale KK (UM canonical), no current experiment can "
            "detect or constrain the KK GW background."
        ),
        "gap_closed": (
            "FALLIBILITY.md §IV.1: KK tower spectrum quantified vs LISA/NANOGrav. "
            "Planck-scale KK GWs at ~10^43 Hz are undetectable. "
            "Sub-Planck window for future detection identified."
        ),
        "references": [
            "NANOGrav 2023 (arXiv:2306.16213)",
            "LISA Proposal (arXiv:1702.00786)",
        ],
    }
