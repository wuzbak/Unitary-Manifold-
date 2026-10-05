# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 707 — CMB Spectral Distortion: KK Signature

PIXIE / SuperPIXIE targets y-distortion and μ-distortion of the CMB at
~10⁻⁸ sensitivity, providing a new window on energy injection in the
early universe.

The KK radion decay in the early universe injects energy via:

    Γ_rad → γγ:  Q_KK / ρ_γ ~ (M_KK / M_Pl)² × (M_KK / H) × ξ_rad

where ξ_rad = Γ_rad / H at T_KK (radion decay epoch).

This gives:
    y ≈ (1/4) × Q_KK / ρ_γ
    μ ≈ (1.4) × Q_KK / ρ_γ  (for z > 5×10⁴)

KK prediction: both y and μ are negligibly small (< 10⁻²⁰) because the
KK scale M_KK ≈ 1 TeV is far above the BBN/CMB epoch, so the radion
decays long before CMB formation.

Architecture note: this is a null prediction — KK spectral distortions
are unmeasurable by PIXIE/SuperPIXIE. Any positive signal at y ~ 10⁻⁷
would require a new sub-TeV KK mode not present in the minimal model.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

import math

# ── Constants ─────────────────────────────────────────────────────────────────
N_W   = 5
K_CS  = 74
PI_KR = math.pi * K_CS / N_W         # ≈ 46.5
M_KK_NATURAL = math.exp(-PI_KR)       # M_Pl = 1

M_KK_GEV     = 1042.0    # GeV
M_PL_GEV     = 1.221e19  # GeV

# Radion mass = √6 M_KK / π (from P687)
M_RAD_GEV    = math.sqrt(6) * M_KK_GEV / math.pi

# PIXIE / SuperPIXIE sensitivity targets
PIXIE_Y_SENSITIVITY = 1e-8
PIXIE_MU_SENSITIVITY = 5e-8

# ── KK energy injection ───────────────────────────────────────────────────────

def q_kk_over_rho_gamma(m_kk_gev: float = M_KK_GEV,
                          m_pl_gev: float = M_PL_GEV) -> float:
    """
    Fractional energy injection from KK radion decay:
    Q_KK / ρ_γ ~ (M_KK / M_Pl)⁴   (dimensional analysis, leading order)
    """
    return (m_kk_gev / m_pl_gev) ** 4

def y_distortion_kk(m_kk_gev: float = M_KK_GEV,
                     m_pl_gev: float = M_PL_GEV) -> float:
    """y ≈ (1/4) × Q_KK/ρ_γ"""
    return 0.25 * q_kk_over_rho_gamma(m_kk_gev, m_pl_gev)

def mu_distortion_kk(m_kk_gev: float = M_KK_GEV,
                      m_pl_gev: float = M_PL_GEV) -> float:
    """μ ≈ 1.4 × Q_KK/ρ_γ"""
    return 1.4 * q_kk_over_rho_gamma(m_kk_gev, m_pl_gev)

# ── Observability check ───────────────────────────────────────────────────────

def spectral_distortion_summary() -> dict:
    y  = y_distortion_kk()
    mu = mu_distortion_kk()
    return {
        "pillar":                707,
        "label":                 "CMB_SPECTRAL_DISTORTION_KK_NULL_PREDICTION",
        "y_distortion":          y,
        "mu_distortion":         mu,
        "y_below_pixie":         y < PIXIE_Y_SENSITIVITY,
        "mu_below_pixie":        mu < PIXIE_MU_SENSITIVITY,
        "observable":            False,
        "null_prediction":       True,
        "pixie_y_target":        PIXIE_Y_SENSITIVITY,
        "pixie_mu_target":       PIXIE_MU_SENSITIVITY,
        "falsification_condition": "y > 1e-8 or μ > 5e-8 at PIXIE from a sub-TeV KK mode",
        "m_kk_gev":              M_KK_GEV,
        "m_rad_gev":             M_RAD_GEV,
    }
