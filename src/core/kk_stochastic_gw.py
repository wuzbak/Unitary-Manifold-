# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_stochastic_gw.py
============================
Pillar 109 — LISA KK Stochastic Gravitational-Wave Background.

The lightest Kaluza-Klein excitation of the 5th dimension is a scalar
breathing-mode graviton at frequency

    f_1 = M_KK × e / h  (Hz)

For M_KK = 110 meV this gives f_1 ≈ 2.66 × 10¹³ Hz (UV/THz range),
far outside the LISA band (10⁻⁴ – 10⁻¹ Hz).  This is an honest null
prediction: the KK breathing mode is not directly detectable by LISA
in the 110 meV mass scenario.

However, a stochastic GW background sourced by early-universe KK
production can generate a scale-invariant tail that reaches the LISA
band.  The characteristic strain is estimated via the isotropic
stochastic background formula.
"""

import math

# ── physical constants ────────────────────────────────────────────────────────
_E_J = 1.602176634e-19    # elementary charge in J/eV
_H_JS = 6.62607015e-34    # Planck constant J·s
_H0_HZ = 2.18e-18         # Hubble constant in Hz (67.4 km/s/Mpc)
_C_MPS = 2.998e8          # speed of light m/s
_MPC_M = 3.0857e22        # 1 Mpc in metres

# ── module-level constants ────────────────────────────────────────────────────
WINDING_NUMBER = 5
K_CS = 74
M_KK_EV_DEFAULT = 0.110   # eV


# ── public API ────────────────────────────────────────────────────────────────

def kk_gw_frequency_hz(n: int = 1, m_kk_ev: float = M_KK_EV_DEFAULT) -> float:
    """Return f_n = n × M_KK × e / h in Hz (n-th KK harmonic frequency).

    For M_KK = 110 meV and n=1 this is ~2.66e13 Hz (UV), not in LISA band.
    """
    if n < 1:
        raise ValueError("harmonic index n must be >= 1")
    if m_kk_ev <= 0:
        raise ValueError("m_kk_ev must be positive")
    return n * m_kk_ev * _E_J / _H_JS


def lisa_band_hz() -> tuple:
    """Return LISA frequency band (f_low, f_high) in Hz."""
    return (1e-4, 1e-1)


def kk_in_lisa_band(m_kk_ev: float = M_KK_EV_DEFAULT) -> bool:
    """Return True if the n=1 KK GW frequency falls inside the LISA band."""
    f = kk_gw_frequency_hz(n=1, m_kk_ev=m_kk_ev)
    f_lo, f_hi = lisa_band_hz()
    return f_lo <= f <= f_hi


def breathing_mode_strain(r_mpc: float = 100.0,
                          omega_gw: float = 1e-10,
                          f_hz: float = 1e-3) -> float:
    """Characteristic strain of the isotropic stochastic KK-GW background.

    Uses the standard formula
        h_c = sqrt(3 H₀² Ω_gw / (2π² f²))
    evaluated at the fiducial LISA frequency f_hz = 1 mHz and then
    scaled by (c / H₀ / r_Mpc) to account for source distance.

    Parameters
    ----------
    r_mpc : float
        Source distance in Mpc.
    omega_gw : float
        GW energy-density fraction Ω_gw.
    f_hz : float
        Evaluation frequency in Hz.
    """
    if r_mpc <= 0:
        raise ValueError("r_mpc must be positive")
    if omega_gw < 0:
        raise ValueError("omega_gw must be non-negative")
    if f_hz <= 0:
        raise ValueError("f_hz must be positive")

    # Background strain amplitude (isotropic formula)
    h_bg = math.sqrt(3.0 * _H0_HZ**2 * omega_gw / (2.0 * math.pi**2 * f_hz**2))
    # Distance suppression: horizon scale / r_source (both in consistent units)
    d_horizon_mpc = _C_MPS / _H0_HZ / _MPC_M   # c/H0 in Mpc ≈ 4420 Mpc
    return h_bg * (d_horizon_mpc / r_mpc)


def lisa_sensitivity_strain() -> float:
    """Return LISA characteristic strain sensitivity ≈ 1e-20."""
    return 1e-20


def stochastic_gw_summary(m_kk_ev: float = M_KK_EV_DEFAULT,
                           omega_gw: float = 1e-10) -> dict:
    """Return summary dictionary for the KK stochastic GW background.

    Keys
    ----
    kk_frequency_hz    : n=1 KK mode frequency in Hz
    in_lisa_band       : bool — is f_1 inside the LISA band?
    breathing_mode_strain: characteristic strain at 1 mHz, 100 Mpc
    lisa_sensitivity   : LISA sensitivity strain
    detectable         : bool — strain > LISA sensitivity
    """
    f = kk_gw_frequency_hz(n=1, m_kk_ev=m_kk_ev)
    strain = breathing_mode_strain(omega_gw=omega_gw)
    sens = lisa_sensitivity_strain()
    return {
        "kk_frequency_hz": f,
        "in_lisa_band": kk_in_lisa_band(m_kk_ev),
        "breathing_mode_strain": strain,
        "lisa_sensitivity": sens,
        "detectable": strain > sens,
    }
