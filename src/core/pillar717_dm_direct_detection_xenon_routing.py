# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 717 — KK DM Direct Detection: XENON/LZ Routing

Dimensional toy contact-scattering benchmarks, not KK-graviton derivations:
    σ_contact = C² μ_Nχ² / π,  [C] = GeV⁻².
For the gravitational-strength toy choose C = G_N = 1/M_Pl².
This is not long-range graviton exchange, whose momentum dependence, spin
structure and recoil spectrum are unspecified.

The EW toy retains σ = g_Y⁴ (Z/A)² m_N² / (π M_KK⁴).
Its nuclear normalization and mediator assumptions are not derived.
M_KK = 1042 GeV is supplied; neither toy establishes exclusion or discovery.
The XENON sensitivity is only an approximate benchmark at that mass.
"""

import math

# ── Constants ─────────────────────────────────────────────────────────────────
M_KK_GEV    = 1042.0    # GeV
M_N_GEV     = 0.939     # GeV (nucleon mass)
G_N_STAR    = 3 * math.pi / (5 * 74 - 10)
G_N_NEWTON  = 1.0 / (1.221e19) ** 2   # GeV⁻², unreduced Planck mass
G_Y         = 0.357     # U(1)_Y gauge coupling
Z_XE        = 54        # Z for Xenon
A_XE        = 131       # A for Xenon

# Conversion: 1 GeV⁻² = 0.3894 mb = 3.894e8 pb = 3.894e-28 cm²
GEV2_TO_PB  = 3.894e8   # pb per GeV⁻²
GEV2_TO_CM2 = 3.894e-28 # cm² per GeV⁻²

# XENON-nT sensitivity
XENON_NT_SENSITIVITY_CM2 = 1e-47   # cm² SI (m_χ~1 TeV)

# ── Gravitational SI cross-section ───────────────────────────────────────────

def sigma_si_grav_cm2(m_kk: float = M_KK_GEV,
                       m_n: float = M_N_GEV) -> float:
    """Toy contact σ = G_N² μ_Nχ² / π [cm²], not graviton exchange."""
    if not all(math.isfinite(m) and m > 0 for m in (m_kk, m_n)):
        raise ValueError("Masses must be finite and positive in GeV")
    mu = m_n * m_kk / (m_n + m_kk)
    sigma_gev2 = G_N_NEWTON ** 2 * mu ** 2 / math.pi
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
    if not all(math.isfinite(m) and m > 0 for m in (m_kk, m_n)):
        raise ValueError("Masses must be finite and positive in GeV")
    if not math.isfinite(g_y) or g_y < 0:
        raise ValueError("Effective coupling must be finite and nonnegative")
    if not all(math.isfinite(x) for x in (Z, A)) or A <= 0 or not 0 <= Z <= A:
        raise ValueError("Nuclear benchmark requires 0 <= Z <= A and A > 0")
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
        "grav_null_prediction": sig_grav < xenon,
        "ew_potentially_detectable": sig_ew > xenon * 1e-3,
        "model_scope":          "dimensional contact-scattering toys, not KK derivations",
        "detector_comparison_scope": "supplied sensitivity benchmark only; not a likelihood exclusion",
        "architecture_limit":  "Mediator/spin structure, nuclear response and detector "
                                "likelihood unresolved; benchmark comparisons only",
        "falsification":        "XENON excess alone cannot confirm EW-mediated KK DM; "
                                "a specified recoil model and likelihood are required",
    }
