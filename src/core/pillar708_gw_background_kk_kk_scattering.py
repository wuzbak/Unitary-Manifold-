# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 708 — Gravitational Wave Background from KK-KK Scattering

KK graviton pairs annihilating to graviton radiation produce a stochastic
gravitational wave background (SGWB) with peak frequency:

    f_peak ≈ M_KK / (2π)   [in Planck-frequency units]

converted to physical frequency:
    f_peak_Hz ≈ M_KK_GeV × (1.546×10²⁴) Hz

For M_KK ≈ 1042 GeV:
    f_peak ≈ 1.61×10²⁷ Hz   (far above any detector band)

The KK-KK gravitational wave energy density:
    Ω_GW h² ≈ (G_N × M_KK²)² × (M_KK / M_Pl)⁴

This is a null prediction for LIGO / LISA / PTA bands — the KK signal
peaks ~10¹⁵ Hz above the LISA band.

However, a first-order phase transition at T ~ M_KK could produce
a SGWB in the decihertz band via bubble nucleation. This is computed
as the architecture-limit estimate.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

import math

# ── Constants ─────────────────────────────────────────────────────────────────
M_KK_GEV   = 1042.0      # GeV
M_PL_GEV   = 1.221e19    # GeV
G_N_STAR   = 3 * math.pi / (5 * 74 - 10)    # ≈ 0.02618

# Hz per GeV (in natural units: 1 GeV = 1.546×10²⁴ Hz / (2π))
GEV_TO_HZ  = 1.546e24 / (2 * math.pi)

# LISA / ET / PTA frequency bands (Hz)
LISA_F_RANGE  = (1e-4, 1e-1)
ET_F_RANGE    = (1.0, 1e4)
PTA_F_RANGE   = (1e-9, 1e-6)

# ── Peak frequency ────────────────────────────────────────────────────────────

def f_peak_kk_hz(m_kk_gev: float = M_KK_GEV) -> float:
    """f_peak = M_KK / (2π) in Hz"""
    return m_kk_gev * GEV_TO_HZ

def omega_gw_h2(m_kk_gev: float = M_KK_GEV,
                 m_pl_gev: float = M_PL_GEV,
                 g_n_star: float = G_N_STAR) -> float:
    """
    Ω_GW h² ≈ (G_N* × M_KK² / M_Pl²)² × (M_KK / M_Pl)⁴
    """
    r = m_kk_gev / m_pl_gev
    return (g_n_star * r ** 2) ** 2 * r ** 4

# ── Phase transition SGWB (bubble nucleation estimate) ────────────────────────

def gw_bubble_nucleation_peak_hz(m_kk_gev: float = M_KK_GEV) -> float:
    """
    SGWB from a first-order PT at T ~ M_KK:
        f_bubble ≈ 1.65×10⁻⁵ Hz × (T_* / 100 GeV) × (g*/100)^(1/6)
    For T_* = M_KK = 1042 GeV, g* = 100:
        f_bubble ≈ 1.65×10⁻⁵ × (1042/100) ≈ 1.7×10⁻⁴ Hz
    """
    T_star = m_kk_gev   # GeV
    g_star = 100.0
    f_bubble = 1.65e-5 * (T_star / 100.0) * (g_star / 100.0) ** (1/6)
    return f_bubble

# ── GW background summary ─────────────────────────────────────────────────────

def gw_background_summary() -> dict:
    f_peak = f_peak_kk_hz()
    omega  = omega_gw_h2()
    f_bub  = gw_bubble_nucleation_peak_hz()
    return {
        "pillar":              708,
        "label":               "GW_BACKGROUND_KK_KK_SCATTERING",
        "f_peak_kk_hz":        f_peak,
        "omega_gw_h2":         omega,
        "f_bubble_hz":         f_bub,
        "lisa_band_hz":        LISA_F_RANGE,
        "f_peak_in_lisa_band": LISA_F_RANGE[0] <= f_peak <= LISA_F_RANGE[1],
        "f_bubble_in_lisa_band": LISA_F_RANGE[0] <= f_bub <= LISA_F_RANGE[1],
        "direct_kk_null":      True,
        "bubble_in_lisa":      LISA_F_RANGE[0] <= f_bub <= LISA_F_RANGE[1],
        "falsification_condition": "SGWB at f~0.1–1 mHz inconsistent with PT at M_KK",
        "m_kk_gev":            M_KK_GEV,
    }
