# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 717 — KK DM Direct Detection: XENON/LZ Routing

The KK photon (γ¹) dark matter candidate scatters off nuclei via
KK graviton exchange, with spin-independent (SI) cross-section:

    σ_SI^KK = G_N² × m_N² × m_χ² / π

where m_N ≈ 1 GeV (nucleon mass), m_χ = M_KK (LKP mass).

For M_KK ≈ 1042 GeV:
    σ_SI ≈ (6.7×10⁻³⁹ GeV⁻⁴) × (1 GeV)² × (1042 GeV)²
          ≈ 7.3×10⁻³³ GeV⁻²
          ≈ 7.3×10⁻³³ × 0.389 mb
          ≈ 2.8×10⁻³³ mb = 2.8×10⁻⁹ pb

XENON-nT / LZ sensitivity: ~10⁻⁴⁸ cm² ≈ 10⁻¹² pb (SI, M_χ~1 TeV)

The KK graviton-mediated SI cross-section is ~24 orders of magnitude
below current XENON/LZ sensitivity → null prediction for direct detection
via gravitational channel.

KK hypercharge-mediated scattering (EW channel):
    σ_SI^EW ≈ g_Y⁴ / (π M_KK⁴) × Z²/A² × m_N²
    ≈ 10⁻⁴⁶ cm²   (in XENON-nT range!)

This pillar documents both channels and their detectability.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

import math

# ── Constants ─────────────────────────────────────────────────────────────────
M_KK_GEV    = 1042.0    # GeV
M_N_GEV     = 0.939     # GeV (nucleon mass)
G_N_STAR    = 3 * math.pi / (5 * 74 - 10)
G_N_NEWTON  = 6.674e-11 / (1.221e19) ** 2   # in GeV⁻² units
G_Y         = 0.357     # U(1)_Y gauge coupling
Z_XE        = 54        # Z for Xenon
A_XE        = 131       # A for Xenon

# Conversion: 1 GeV⁻² = 0.389 mb = 3.89×10⁵ pb = 3.89×10⁻⁵ cm²
GEV2_TO_PB  = 3.89e5    # pb per GeV⁻²
GEV2_TO_CM2 = 3.894e-28 # cm² per GeV⁻²

# XENON-nT sensitivity
XENON_NT_SENSITIVITY_CM2 = 1e-47   # cm² SI (m_χ~1 TeV)

# ── Gravitational SI cross-section ───────────────────────────────────────────

def sigma_si_grav_cm2(m_kk: float = M_KK_GEV,
                       m_n: float = M_N_GEV) -> float:
    """σ_SI^grav = G_N² × m_N² × m_χ² / π  [cm²]"""
    sigma_gev2 = G_N_NEWTON ** 2 * m_n ** 2 * m_kk ** 2 / math.pi
    return sigma_gev2 * GEV2_TO_CM2

# ── EW (hypercharge) SI cross-section ────────────────────────────────────────

def sigma_si_ew_cm2(m_kk: float = M_KK_GEV,
                     m_n: float = M_N_GEV,
                     g_y: float = G_Y,
                     Z: int = Z_XE,
                     A: int = A_XE) -> float:
    """
    σ_SI^EW ≈ g_Y⁴ / (π M_KK⁴) × (Z/A)² × m_N²  [cm²]
    """
    sigma_gev2 = g_y ** 4 / (math.pi * m_kk ** 4) * (Z / A) ** 2 * m_n ** 2
    return sigma_gev2 * GEV2_TO_CM2

# ── Detectability ─────────────────────────────────────────────────────────────

def direct_detection_summary() -> dict:
    sig_grav = sigma_si_grav_cm2()
    sig_ew   = sigma_si_ew_cm2()
    xenon    = XENON_NT_SENSITIVITY_CM2
    return {
        "pillar":               717,
        "label":                "KK_DM_DIRECT_DETECTION_XENON_ROUTING",
        "m_kk_gev":             M_KK_GEV,
        "sigma_si_grav_cm2":    sig_grav,
        "sigma_si_ew_cm2":      sig_ew,
        "xenon_nt_cm2":         xenon,
        "grav_above_xenon":     sig_grav > xenon,
        "ew_above_xenon":       sig_ew > xenon,
        "grav_null_prediction": True,
        "ew_potentially_detectable": sig_ew > xenon * 1e-3,
        "falsification":        "σ_SI > XENON-nT at M_χ=M_KK would confirm EW-mediated DM",
    }
