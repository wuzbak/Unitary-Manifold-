# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 690 — Majorana Mass from Bulk Dirichlet BC Seesaw Kernel.

═══════════════════════════════════════════════════════════════════════════
SPRINT U — MAJORANA MASS KERNEL FROM BULK DIRICHLET BC SEESAW
═══════════════════════════════════════════════════════════════════════════

PRIOR STATE
────────────
  • Pillar 677: ν_R Dirichlet BC from Z₂ orbifold — DERIVED.
  • Pillar 689: Normal hierarchy predicted from c_{L,i} ordering.
  • The Majorana mass M_{Majorana} = x_1 × M_KK was stated but not computed
    as a full function of the c_ν bulk mass parameter.

THIS PILLAR (690) computes the Majorana seesaw kernel as a function of c_ν.

PHYSICS — MAJORANA SEESAW KERNEL FROM DIRICHLET BC
────────────────────────────────────────────────────
The right-handed neutrino ν_R satisfies Dirichlet BCs on both branes.
This means ν_R has NO zero mode — it is projected out.

The lowest KK mode of ν_R has mass:
    M_n^{ν_R}(c_ν) = x_n^{(c_ν)} × M_KK

where x_n^{(c_ν)} are the roots of the Bessel equation with the appropriate
boundary conditions for bulk mass parameter c_ν.

For the Dirichlet/Dirichlet (D/D) case (no zero mode):
    J_{c_ν − 1/2}(x_n) = 0   (UV brane: D BC)
    J_{c_ν + 1/2}(x_n e^{−π k R}) = 0   (IR brane, warp-corrected)

In the limit π k R → ∞ (large hierarchy), the dominant root is determined
by the UV brane BC:
    x_1^{(D/D)} ≈ j_{|c_ν − 1/2|, 1}   (first root of J_{|c_ν − 1/2|})

For c_ν ≈ 1/2 (approximately flat profile):
    j_{0, 1} ≈ 2.405   (first root of J_0 — Bessel)

For c_ν > 1 (UV-peaked):
    x_1^{(D/D)} → larger values (more UV-peaked, heavier KK mode)

SEESAW KERNEL
──────────────
The Majorana seesaw mass for generation i:

    m_{ν,i}^{seesaw} = (y_i v f_{L,i})² / M_{1}^{ν_R}

where M_1^{ν_R} = x_1^{(c_ν)} × M_KK.

THE KERNEL FUNCTION
────────────────────
    K_seesaw(c_ν) = 1 / (x_1^{(c_ν)} × M_KK)

Using the approximate Bessel root formula:
    x_1^{(c_ν)} ≈ j_{|c_ν − 1/2|, 1}

For c_ν ≈ 0.5 → j_{0,1} ≈ 2.405
For c_ν = 1.0 → j_{0.5, 1} ≈ π/2 ≈ 1.571 (Rayleigh guess)
For c_ν = 0.0 → j_{0.5, 1} ≈ π ≈ 3.14

CALIBRATED c_ν FROM DM² DATA
──────────────────────────────
From the DM31 closure (Δm²₃₁ = 2.4109×10⁻³ eV²) and the seesaw formula:
    m_{ν,3} ≈ √(Δm²₃₁) ≈ 49 meV (NH, assuming m_{ν,1} ≪ m_{ν,3})

    m_{ν,3} = (y_3 v f_{L,3})² / M_1^{ν_R}
    → M_1^{ν_R} = (y_3 v f_{L,3})² / m_{ν,3}

For y_3 ≈ y_τ (tau Yukawa from charged lepton sector), v = 246 GeV:
    y_τ × v ≈ m_τ = 1.777 GeV (lepton mass relation in RS1)

    M_1^{ν_R} ≈ (1.777)² / 0.049 eV × f_{L,3}²
              = 64.5 GeV² / (0.049 × 10⁻⁹ GeV) × f_{L,3}²
              = 1.316 × 10¹² GeV × f_{L,3}²

This is naturally at the GUT/seesaw scale for f_{L,3} ~ 1 (IR-peaked),
and M_1^{ν_R} = x_1 × M_KK → x_1 × M_KK ≈ 10¹² GeV requires M_KK ≈ 10¹² / x_1.

NOTE: This is NOT the RS1 TeV-scale M_KK from the hierarchy problem solution.
The neutrino seesaw requires a DIFFERENT mass scale — either:
  (a) A separate heavy ν_R sector (at high energy scale), OR
  (b) A Type II/III seesaw from higher-dim operators
  This is an architecture limit: the RS1 KK scale alone cannot generate
  the observed neutrino masses through a standard seesaw.

ARCHITECTURE LIMIT
───────────────────
The standard RS1 Dirichlet BC seesaw:
  M_1^{ν_R} = x_1 × M_KK ≈ 3.83 × 1042 GeV ≈ 4000 GeV

  m_{ν,3}^{KK-seesaw} = m_{Dirac,3}² / M_1^{ν_R}
                       ≈ (m_τ × f_{L,3} × f_{ν,3})² / (3.83 × M_KK)

For f_{L,3} × f_{ν,3} ≈ 1 (both IR-peaked):
    m_{ν,3}^{KK} ≈ (1.777 GeV)² / 4000 GeV ≈ 789 MeV ≫ 49 meV

This is the architecture limit: the KK seesaw produces neutrino masses
far too large. The observed ≈ 49 meV requires either:
  - Very UV-peaked ν_R (f_{ν,3} ≪ 1, suppressing the seesaw mass)
  - A Weinberg operator at the UV brane (higher-dim seesaw)
  - Dirac neutrino scenario (no Majorana mass)

STATUS: MAJORANA_SEESAW_ARCHITECTURE_LIMIT_DOCUMENTED
  KK Dirichlet BC seesaw is computed; architecture limit documented.
  The UM requires either UV-peaked ν_R or higher-dim operator for m_ν ≈ 49 meV.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "N_W",
    "K_CS",
    "M_KK_GEV",
    "M_NU3_TARGET_EV",
    "X1_BESSEL_D_APPROX",
    "M_MAJORANA_KK_GEV",
    "bessel_root_approximation",
    "seesaw_kernel",
    "kk_seesaw_neutrino_mass",
    "architecture_limit_analysis",
    "majorana_seesaw_certificate",
    "what_is_claimed",
    "what_is_NOT_claimed",
]

PILLAR_NUMBER: int = 690
PILLAR_STATUS: str = "MAJORANA_SEESAW_ARCHITECTURE_LIMIT_DOCUMENTED"
PILLAR_TITLE: str = "Majorana Mass from Bulk Dirichlet BC Seesaw Kernel"
VERSION: str = "v21.2"

N_W: int = 5
K_CS: int = 74

# Physical KK mass (from Pillar 681: M_KK ≈ 1042 GeV)
_M_PL_GEV: float = 1.2209e19
_PI_KR_PHYS: float = 37.0
M_KK_GEV: float = _M_PL_GEV * math.exp(-_PI_KR_PHYS)   # ≈ 1042 GeV

# Bessel roots for D/D boundary conditions
X1_BESSEL_D_APPROX: float = 3.8317   # first root of J_2 (used for c_ν ≈ 0.5 Dirichlet)
# For D/D: first zero of J_{c_ν - 1/2}; c_ν = 1/2 gives J_0: x = 2.4048
X1_BESSEL_J0: float = 2.4048   # first root of J_0 (c_ν = 1/2)

M_MAJORANA_KK_GEV: float = X1_BESSEL_J0 * M_KK_GEV   # ≈ 2509 GeV

# Physical neutrino target (NH, m_{ν,3} ≈ √Δm²₃₁)
DM31_EV2: float = 2.4109e-3
M_NU3_TARGET_EV: float = math.sqrt(DM31_EV2) * 1e3  # meV
M_NU3_TARGET_GEV: float = math.sqrt(DM31_EV2) * 1e-9  # GeV

# Tau lepton mass (leading seesaw Dirac mass in RS1)
M_TAU_GEV: float = 1.77686  # GeV


def bessel_root_approximation(c_nu: float) -> Dict[str, float]:
    """Approximate first Bessel root x_1^{(c_ν)} for the Dirichlet/Dirichlet BC.

    For |c_ν − 1/2| = ν order: j_{ν,1} (first root of J_ν).
    Uses approximation: j_{ν,1} ≈ ν + 1.8557 ν^{1/3} + ... (Abramowitz & Stegun)
    """
    nu_order = abs(c_nu - 0.5)
    if nu_order < 1e-3:
        x1 = X1_BESSEL_J0   # J_0 → 2.4048
    else:
        # Leading asymptotic for small ν: j_{ν,1} ≈ π/2 + ... or use AS formula
        # Simple interpolation: j_{0,1}=2.405, j_{1/2,1}=π≈3.14, j_{1,1}=3.832
        if nu_order <= 0.5:
            x1 = X1_BESSEL_J0 + nu_order * (math.pi - X1_BESSEL_J0) / 0.5
        elif nu_order <= 1.0:
            x1 = math.pi + (nu_order - 0.5) * (X1_BESSEL_D_APPROX - math.pi) / 0.5
        else:
            x1 = X1_BESSEL_D_APPROX + (nu_order - 1.0) * math.pi / 4.0

    return {
        "c_nu": c_nu,
        "nu_order": nu_order,
        "x1_approx": x1,
        "m_majorana_gev": x1 * M_KK_GEV,
        "formula": "x_1^{(c_ν)} = first root of J_{|c_ν − 1/2|}",
    }


def seesaw_kernel(c_nu: float = 0.5) -> Dict[str, float]:
    """Majorana seesaw kernel K(c_ν) = 1 / (x_1(c_ν) × M_KK)."""
    root = bessel_root_approximation(c_nu)
    m_majorana = root["m_majorana_gev"]
    kernel_gev_inv = 1.0 / m_majorana if m_majorana > 0 else float("inf")

    return {
        "c_nu": c_nu,
        "x1": root["x1_approx"],
        "m_majorana_gev": m_majorana,
        "m_kk_gev": M_KK_GEV,
        "kernel_gev_inv": kernel_gev_inv,
        "formula": "K_seesaw = 1 / (x_1(c_ν) × M_KK)",
    }


def kk_seesaw_neutrino_mass(
    c_nu: float = 0.5,
    f_l3: float = 1.0,
    f_nu3: float = 1.0,
) -> Dict[str, float]:
    """Compute KK seesaw ν mass for given wavefunction values."""
    kernel = seesaw_kernel(c_nu)
    # Dirac mass = y_τ × v × f_L × f_ν (RS1 bilinear)
    m_dirac_gev = M_TAU_GEV * f_l3 * f_nu3
    m_nu_gev = m_dirac_gev**2 * kernel["kernel_gev_inv"]
    m_nu_ev = m_nu_gev * 1e9  # GeV to eV

    return {
        "c_nu": c_nu,
        "f_l3": f_l3,
        "f_nu3": f_nu3,
        "m_dirac_gev": m_dirac_gev,
        "m_majorana_gev": kernel["m_majorana_gev"],
        "m_nu_gev": m_nu_gev,
        "m_nu_ev": m_nu_ev,
        "m_nu3_target_ev": M_NU3_TARGET_EV,
        "ratio_to_target": m_nu_ev / (M_NU3_TARGET_EV * 1e-3) if M_NU3_TARGET_EV > 0 else float("inf"),
        "architecture_limit": m_nu_ev > 1.0,   # > 1 eV is architecture limit
    }


def architecture_limit_analysis() -> Dict[str, object]:
    """Document the KK seesaw architecture limit for neutrino masses."""
    # Standard case: c_ν = 0.5, f_L × f_ν = 1 (both IR-peaked)
    standard = kk_seesaw_neutrino_mass(0.5, 1.0, 1.0)

    # Suppressed case: UV-peaked ν_R  (f_ν ≪ 1)
    # Required f_ν: m_nu = m_dirac² × f_ν² / M_Majorana = 49 meV
    m_nu_target_gev = M_NU3_TARGET_EV * 1e-3 * 1e-9  # 49 meV in GeV
    m_majorana = bessel_root_approximation(0.5)["m_majorana_gev"]
    # m_dirac = M_TAU × f_L = M_TAU (f_L = 1)
    m_dirac_sq = M_TAU_GEV**2
    f_nu_required_sq = m_nu_target_gev * m_majorana / m_dirac_sq
    f_nu_required = math.sqrt(f_nu_required_sq)

    return {
        "standard_case_f_nu_1": standard,
        "standard_m_nu_ev": standard["m_nu_ev"],
        "target_m_nu_ev": M_NU3_TARGET_EV * 1e-3,  # in eV
        "ratio_standard_to_target": standard["m_nu_ev"] / (M_NU3_TARGET_EV * 1e-3),
        "architecture_limit": True,
        "required_f_nu_suppression": f_nu_required,
        "required_f_nu_log": math.log(f_nu_required) if f_nu_required > 0 else float("inf"),
        "closure_path": (
            "UV-peaked ν_R with f_{ν,3} ≪ 1, OR higher-dim Weinberg operator, "
            "OR Dirac neutrino scenario"
        ),
        "status": "ARCHITECTURE_LIMIT — KK seesaw mass ≫ 49 meV for f_{ν} ≈ 1",
    }


def what_is_claimed() -> List[str]:
    return [
        "The Majorana seesaw kernel K(c_ν) = 1/(x_1(c_ν) × M_KK) is computed",
        "The KK Dirichlet BC seesaw produces m_ν ≫ 49 meV for IR-peaked ν_R — architecture limit",
        "Closing the seesaw requires UV-peaked ν_R (f_{ν,3} ≪ 1) or a Weinberg operator",
        "The required f_{ν,3} suppression is computed explicitly",
        "This is consistent with the normal hierarchy from Pillar 689 (UV-peaked ν_R)",
    ]


def what_is_NOT_claimed() -> List[str]:
    return [
        "The Majorana mass is uniquely determined by RS1 alone",
        "The absolute neutrino masses are derived ab initio",
        "The architecture limit is closed by this pillar",
    ]


def majorana_seesaw_certificate() -> Dict[str, object]:
    """Full Pillar 690 Majorana seesaw kernel certificate."""
    arch = architecture_limit_analysis()
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "version": VERSION,
        "status": PILLAR_STATUS,
        "m_kk_gev": M_KK_GEV,
        "x1_bessel_j0": X1_BESSEL_J0,
        "m_majorana_kk_gev": M_MAJORANA_KK_GEV,
        "architecture_limit": arch,
        "p_nu_mass_status": "ARCHITECTURE LIMIT — KK seesaw exceeds target; UV-peaked ν_R needed",
        "toe_impact": "0 — architecture limit documented; no ToE score change",
        "claimed": what_is_claimed(),
        "not_claimed": what_is_NOT_claimed(),
        "link_to_p689": "Normal hierarchy from UV-peaked c_L consistent with UV-peaked ν_R needed here",
    }
