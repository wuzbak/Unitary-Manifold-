# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 714 — KK Dark Matter Relic Density

Toy WIMP freeze-out estimate for a supplied KK-photon benchmark.
M_KK = 1042 GeV and g_KK = 0.63 are inputs, not geometric derivations.

Relic density calculation (WIMP freeze-out):
    Ω_DM h² ≈ 0.1 pb / ⟨σv⟩

The KK photon annihilation cross-section:
    ⟨σv⟩ ≈ g_KK⁴ / (16π M_KK²)   (s-wave, non-relativistic)

where g_KK = 0.63 is an effective benchmark coupling, not the measured
hypercharge coupling.

For M_KK ≈ 1042 GeV:
    ⟨σv⟩ ≈ 0.63⁴ / (16π × 1042²) GeV⁻² ≈ 2.886×10⁻⁹ GeV⁻²
           ≈ 1.124 pb

Ω_KK h² ≈ 0.089, about 74% of the observed 0.12.

This rough inverse-cross-section prescription does not solve freeze-out
or establish the missing abundance; corrections are not guaranteed to close it.
"""

import math

# ── Constants ─────────────────────────────────────────────────────────────────
M_KK_GEV     = 1042.0    # GeV
G_KK         = 0.63      # supplied effective coupling
OMEGA_DM_H2  = 0.120     # Planck 2018 observed dark matter relic density

# 1 pb = 1000 fb; 1 GeV⁻² = 3.894e8 pb.
PB_PER_GEV2  = 3.894e8
GEV2_PER_PB  = 1.0 / PB_PER_GEV2

# ── Annihilation cross-section ────────────────────────────────────────────────

def sigma_v_kk_gev2(m_kk: float = M_KK_GEV,
                     g_kk: float = G_KK) -> float:
    """⟨σv⟩ = g_KK⁴ / (16π M_KK²)  in GeV⁻²"""
    if not math.isfinite(m_kk) or m_kk <= 0:
        raise ValueError("Mass must be finite and positive in GeV")
    if not math.isfinite(g_kk) or g_kk < 0:
        raise ValueError("Effective coupling must be finite and nonnegative")
    return g_kk ** 4 / (16 * math.pi * m_kk ** 2)

def sigma_v_kk_pb(m_kk: float = M_KK_GEV,
                   g_kk: float = G_KK) -> float:
    """⟨σv⟩ in pb"""
    return sigma_v_kk_gev2(m_kk, g_kk) * PB_PER_GEV2

# ── Relic density ─────────────────────────────────────────────────────────────

def omega_kk_h2(m_kk: float = M_KK_GEV,
                 g_kk: float = G_KK) -> float:
    """Ω_KK h² ≈ 0.1 pb / ⟨σv⟩[pb]"""
    sv = sigma_v_kk_pb(m_kk, g_kk)
    return 0.1 / sv if sv > 0 else math.inf

def relic_density_summary(m_kk: float = M_KK_GEV,
                           g_kk: float = G_KK) -> dict:
    sv_pb    = sigma_v_kk_pb(m_kk, g_kk)
    omega    = omega_kk_h2(m_kk, g_kk)
    ratio    = omega / OMEGA_DM_H2
    return {
        "pillar":              714,
        "label":               "KK_DARK_MATTER_RELIC_DENSITY_TIGHTENING_16",
        "m_kk_gev":            m_kk,
        "sigma_v_pb":          sv_pb,
        "omega_kk_h2":         omega,
        "omega_dm_obs":        OMEGA_DM_H2,
        "ratio_to_observed":   ratio,
        "within_factor_2":     0.5 < ratio < 2.0,
        "model_scope":         "supplied KK-photon toy WIMP benchmark; not a mass derivation",
        "architecture_limit":  "Approximate inverse-cross-section freeze-out prescription; "
                               "thermal history and missing abundance unresolved (Tightening 16)",
        "tightening":          16,
    }
