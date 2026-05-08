# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 102 — Gravitational Waves from Brane Dynamics.

Extends the Unitary Manifold beyond the 101-pillar core to cover gravitational
wave signals arising from brane dynamics: brane-brane collisions, radion
oscillations, and the stochastic KK-graviton tower background.

Key results
-----------
* Brane collision peak frequency: f_peak ≈ 1.66 × 10²⁶ Hz  (M_KK ≈ 1042 GeV)
  → far above LISA/LIGO; within LHC energy range.
* Radion GW power: P_GW set by G_N × m_r² × Γ_r²  (m_r ≈ 69.9 GeV).
* Stochastic KK background: Ω_GW ~ (M_KK/M_Pl)² × N_KK  (~ 10⁻³⁰ range).

ARCHITECTURE_LIMIT: All brane-GW frequencies sit in the kHz–GHz–PHz range,
far above current detector bands.  Detection requires future high-frequency
GW observatories (≫ kHz).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "PILLAR_NUMBER",
    "M_PL_GEV",
    "PI_KR",
    "K_CS",
    "M_KK_GEV",
    "M_RADION_GEV",
    "F_PEAK_BRANE_GEV",
    "F_PEAK_HZ",
    "OMEGA_GW_KK",
    "pillar102_gw_spectrum",
    "radion_gw_signal",
    "kk_graviton_gw_background",
    "pillar102_summary",
]

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

PILLAR_NUMBER: int = 102

M_PL_GEV: float = 1.2209e19          # Planck mass [GeV]
PI_KR: float = 37.0                   # = K_CS / 2
K_CS: int = 74

M_KK_GEV: float = M_PL_GEV * math.exp(-PI_KR)   # ≈ 1042 GeV

# Radion mass from GW correction factor
M_RADION_GEV: float = M_KK_GEV / math.sqrt(6.0 * PI_KR)   # ≈ 69.9 GeV

# GW peak frequency from brane collision (in GeV, then Hz)
F_PEAK_BRANE_GEV: float = M_KK_GEV / (2.0 * math.pi)      # ≈ 166 GeV
F_PEAK_HZ: float = F_PEAK_BRANE_GEV * 1e9 * 1.6e-19 / 6.626e-34  # convert to Hz

# Stochastic background dimensionless amplitude
OMEGA_GW_KK: float = (M_KK_GEV / M_PL_GEV) ** 2 * PI_KR


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def pillar102_gw_spectrum(bubble_nucleation_rate_over_H4: float = 1.0) -> Dict:
    """Compute the GW spectrum from a brane-brane collision event.

    Parameters
    ----------
    bubble_nucleation_rate_over_H4 : float
        Ratio of bubble nucleation rate to H⁴ (dimensionless).  Default is 1.0
        (order-unity estimate).

    Returns
    -------
    dict
        Keys: ``f_peak_gev``, ``f_peak_hz``, ``omega_gw_peak``,
        ``m_kk_gev``, ``pillar``, ``status``.
    """
    omega_gw_peak = (M_KK_GEV / M_PL_GEV) ** 4 * bubble_nucleation_rate_over_H4

    return {
        "pillar": PILLAR_NUMBER,
        "m_kk_gev": M_KK_GEV,
        "f_peak_gev": F_PEAK_BRANE_GEV,
        "f_peak_hz": F_PEAK_HZ,
        "bubble_nucleation_rate_over_H4": bubble_nucleation_rate_over_H4,
        "omega_gw_peak": omega_gw_peak,
        "status": "ARCHITECTURE_LIMIT — f_peak >> LISA/LIGO band",
        "note": (
            f"f_peak ≈ {F_PEAK_HZ:.2e} Hz (requires future high-frequency GW detector); "
            "within LHC energy range at M_KK ≈ 1042 GeV."
        ),
    }


def radion_gw_signal(decay_rate_gev: float | None = None) -> Dict:
    """Compute the GW power from radion oscillations/decay.

    Parameters
    ----------
    decay_rate_gev : float or None
        Radion decay rate Γ_r [GeV].  Defaults to ``M_RADION_GEV / (8π)``
        (narrow-width approximation).

    Returns
    -------
    dict
        Keys: ``m_radion_gev``, ``decay_rate_gev``, ``gw_power_estimate``,
        ``g_newton_gev2``, ``pillar``, ``status``.
    """
    if decay_rate_gev is None:
        decay_rate_gev = M_RADION_GEV / (8.0 * math.pi)

    # Newton's constant in GeV⁻² units: G_N = 1 / M_Pl² (Planck units)
    g_newton_gev2 = 1.0 / M_PL_GEV ** 2

    # GW power (order-of-magnitude): P_GW ~ G_N m_r² Γ_r²
    gw_power_estimate = g_newton_gev2 * M_RADION_GEV ** 2 * decay_rate_gev ** 2

    return {
        "pillar": PILLAR_NUMBER,
        "m_radion_gev": M_RADION_GEV,
        "decay_rate_gev": decay_rate_gev,
        "g_newton_gev2": g_newton_gev2,
        "gw_power_estimate": gw_power_estimate,
        "status": "ARCHITECTURE_LIMIT — radion GW undetectable at current sensitivity",
        "note": (
            f"m_r ≈ {M_RADION_GEV:.2f} GeV; P_GW ~ G_N m_r² Γ_r² ≈ {gw_power_estimate:.2e} "
            "(natural units).  Detection requires dedicated high-frequency GW infrastructure."
        ),
    }


def kk_graviton_gw_background(n_kk: int | None = None) -> Dict:
    """Compute the stochastic GW background from the KK graviton tower.

    Parameters
    ----------
    n_kk : int or None
        Number of KK modes in the tower.  Defaults to ``int(PI_KR)`` = 37.

    Returns
    -------
    dict
        Keys: ``n_kk``, ``omega_gw_kk``, ``m_kk_gev``, ``pi_kr``,
        ``pillar``, ``status``.
    """
    if n_kk is None:
        n_kk = int(PI_KR)

    omega_gw = (M_KK_GEV / M_PL_GEV) ** 2 * n_kk

    return {
        "pillar": PILLAR_NUMBER,
        "m_kk_gev": M_KK_GEV,
        "pi_kr": PI_KR,
        "n_kk": n_kk,
        "omega_gw_kk": omega_gw,
        "omega_gw_kk_reference": OMEGA_GW_KK,
        "status": "ARCHITECTURE_LIMIT — Ω_GW far below LISA sensitivity (~10⁻¹²)",
        "note": (
            f"Ω_GW ~ (M_KK/M_Pl)² × N_KK ≈ {omega_gw:.2e}; "
            "LISA sensitivity floor ≈ 10⁻¹²; detection requires future observatories."
        ),
    }


def pillar102_summary() -> Dict:
    """Return a structured summary of Pillar 102.

    Returns
    -------
    dict
        Top-level summary with ``pillar``, ``title``, ``status``,
        ``m_kk_gev``, ``m_radion_gev``, ``omega_gw_kk``, ``f_peak_hz``,
        ``architecture_limit``, and ``sub_results`` containing all three
        component results.
    """
    gw_spectrum = pillar102_gw_spectrum()
    radion_signal = radion_gw_signal()
    kk_background = kk_graviton_gw_background()

    return {
        "pillar": PILLAR_NUMBER,
        "title": "Gravitational Waves from Brane Dynamics",
        "status": "ARCHITECTURE_LIMIT_CERTIFIED",
        "m_kk_gev": M_KK_GEV,
        "m_radion_gev": M_RADION_GEV,
        "f_peak_hz": F_PEAK_HZ,
        "omega_gw_kk": OMEGA_GW_KK,
        "architecture_limit": (
            "All brane-GW signals sit at f >> kHz (brane collision: f_peak ~ 10²⁶ Hz). "
            "The stochastic KK background Ω_GW ~ 10⁻³⁰ is far below LISA sensitivity. "
            "Detection requires future high-frequency GW detectors."
        ),
        "sub_results": {
            "brane_collision_gw": gw_spectrum,
            "radion_gw": radion_signal,
            "kk_stochastic_background": kk_background,
        },
    }
