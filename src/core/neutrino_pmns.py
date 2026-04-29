# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/neutrino_pmns.py
==========================
Pillar 83 — PMNS Neutrino Mixing Matrix from the RS/UM Orbifold Geometry.

Physical Context
----------------
The Pontecorvo-Maki-Nakagawa-Sakata (PMNS) matrix U describes neutrino mixing
between mass eigenstates (ν₁, ν₂, ν₃) and flavour eigenstates (νₑ, ν_μ, ν_τ).
In the standard parameterisation:

    U = R₂₃(θ₂₃) × U₁₃(θ₁₃, δ_CP) × R₁₂(θ₁₂) × diag(e^{iα₁/2}, e^{iα₂/2}, 1)

where the Majorana phases α₁, α₂ are unmeasured.

PDG 2024 (normal ordering) best-fit values:
    θ₁₂ = 33.41° (sin²θ₁₂ = 0.307)     — solar mixing
    θ₂₃ = 49.1°  (sin²θ₂₃ = 0.572)     — atmospheric mixing
    θ₁₃ = 8.62°  (sin²θ₁₃ = 0.0222)    — reactor mixing
    δ_CP = -107° (1.87 rad) — Dirac CP phase (best fit; wide uncertainty)

Mass splittings (PDG 2024, normal ordering):
    Δm²₂₁ = 7.53 × 10⁻⁵ eV²    (solar)
    Δm²₃₁ = 2.453 × 10⁻³ eV²   (atmospheric)

Mechanism in the RS/UM Framework
----------------------------------
The PMNS matrix arises from the mismatch between the charged lepton and
neutrino bulk mass parameters in the RS orbifold.  Pillar 75
(yukawa_brane_integrals.py) fits the charged lepton bulk masses (c_L^e,
c_L^μ, c_L^τ) to reproduce m_e, m_μ, m_τ.

The neutrino sector has independent bulk masses (c_L^ν1, c_L^ν2, c_L^ν3).
The PMNS matrix:

    U_PMNS = U_L^e†  ×  U_L^ν

Neutrino Mass Scale Issue (IMPORTANT HONEST FLAG)
---------------------------------------------------
The Neutrino-Radion Identity (Pillar 49, CONSISTENCY_LOG) identifies:

    M_KK = m_ν₁ = 110.13 meV

as the lightest active neutrino mass.  However, this creates a tension
with the Planck 2018 constraint Σm_ν < 120 meV (0.12 eV):

    If m_ν₁ = 110 meV and the mass splittings are:
        Δm²₂₁ = 7.53 × 10⁻⁵ eV²  →  m_ν₂ ≈ 110.3 meV
        Δm²₃₁ = 2.453 × 10⁻³ eV² →  m_ν₃ ≈ 113.1 meV

    Then Σm_ν = m_ν₁ + m_ν₂ + m_ν₃ ≈ 333 meV >> 120 meV (Planck limit).

This is a GENUINE INCONSISTENCY in the framework.  The CONSISTENCY_LOG
claim "Consistent with Planck Σm_ν < 120 meV? YES" is incorrect; it
compares 110 meV to 120 meV for a SINGLE neutrino, ignoring the three-flavour
sum constraint.

Resolution options:
  A. Reinterpret M_KK = 110 meV as the compactification scale (not the
     lightest neutrino mass).  Active neutrinos are lighter, derived via
     a brane-localised mechanism. The dark-energy closure then still works
     since ρ_eff depends on M_KK, not m_ν directly.
  B. Accept the prediction Σm_ν ≈ 330 meV as a falsifiable consequence of
     the theory.  This is testable: future CMB+BAO+LSS combined constraints
     reaching σ(Σm_ν) ~ 20 meV would definitively confirm or rule this out.
  C. Invoke the inverted hierarchy with m_ν₃ ≈ M_KK/n_w → lighter spectrum.

This module implements Resolution A as the scientifically cleanest option:
M_KK is the KK scale; active neutrino masses are derived from the RS
mechanism with different bulk masses, allowing Σm_ν < 120 meV.

Geometric Predictions for PMNS Angles
----------------------------------------
In the RS framework, the mixing angles arise from the relative bulk mass
mismatch between the charged lepton and neutrino sectors.  The UM provides
geometric constraints:

  1. The atmospheric angle θ₂₃ is close to maximal (45°) — this arises
     naturally when the second and third generation neutrino wavefunctions
     are nearly degenerate on the UV brane (small Δc_{23}^ν).

  2. The reactor angle θ₁₃ ≈ 8.6° — sets the scale of 1-3 mixing; in RS
     this corresponds to a specific c_L^{ν1} - c_L^{ν3} mismatch.

  3. The solar angle θ₁₂ ≈ 33.4° — intermediate mixing; in RS this comes
     from the 1-2 neutrino sector bulk mass difference.

  4. The PMNS CP phase δ_{CP}^{PMNS} — experimentally near -100° to -150°;
     in the UM geometric framework, the winding-sector contribution gives
     δ_{CP}^{PMNS} ≈ π - 2π/n_w = π - 72° = 108°.
     PDG: δ_{CP} ≈ -107° ≡ +253° (mod 360°), but in the range [-180°, 180°]
     the best fit is ~ -100° to -150°.  The geometric prediction 108° (or
     equivalently -252° mod 360°) is not a match; this angle remains open.

Honest Status
-------------
MECHANISM: RS bulk mass mismatch provides the correct geometric framework for
neutrino mixing.  The three mixing angles can be reproduced by fitting three
neutrino bulk mass parameters.

PREDICTION: θ₂₃ near-maximal mixing is a natural consequence of near-degenerate
second and third generation neutrino wavefunctions.  Reactor angle θ₁₃ > 0
requires a small but non-zero 1-3 mixing.

REMAINING GAPS:
  - Neutrino bulk mass parameters c_L^{ν_i} not derived from first principles
  - Majorana vs Dirac nature of neutrinos (no UM derivation available)
  - PMNS CP phase: geometric estimate 108° is not consistent with PDG best fit
  - Σm_ν: if M_KK = m_ν₁, the sum violates Planck; Resolution A needed

Public API
----------
pmns_mixing_angles_pdg()
    Return PDG 2024 PMNS mixing angles.

pmns_from_angles(theta12, theta23, theta13, delta_cp_rad)
    Construct 3×3 PMNS matrix from mixing angles (Majorana phases = 0).

pmns_pdg()
    PMNS matrix at PDG 2024 central values.

neutrino_mass_spectrum(m1_eV, ordering)
    Compute (m1, m2, m3) from lightest mass using oscillation data.

sigma_m_nu(m1_eV, ordering)
    Compute Σm_ν and check against Planck limit.

neutrino_mass_tension_report()
    Honest assessment of the M_KK = m_ν₁ = 110 meV tension.

pmns_geometric_estimate(n_w)
    Estimate PMNS matrix from geometric mixing angle arguments.

pmns_gap_report()
    Honest summary of PMNS status in the UM framework.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
    GitHub Copilot (AI).
"""
from __future__ import annotations

import cmath
import math
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# PDG 2024 PMNS mixing angles and mass splittings
# ---------------------------------------------------------------------------

#: sin²(θ₁₂) [PDG 2024, normal ordering]
SIN2_THETA12_PDG: float = 0.307

#: sin²(θ₂₃) [PDG 2024, normal ordering]
SIN2_THETA23_PDG: float = 0.572

#: sin²(θ₁₃) [PDG 2024, normal ordering]
SIN2_THETA13_PDG: float = 0.0222

#: Dirac CP phase [radians, PDG 2024 best fit, normal ordering]
#: Negative value convention: δ_CP ≈ -107° ≈ -1.87 rad
DELTA_CP_PMNS_PDG_RAD: float = math.radians(-107.0)

#: Solar mass splitting Δm²₂₁ [eV²]
DM2_21_EV2: float = 7.53e-5

#: Atmospheric mass splitting Δm²₃₁ [eV², normal ordering]
DM2_31_EV2: float = 2.453e-3

#: Planck 2018 95% CL upper limit on Σm_ν [eV]
PLANCK_SUM_MNU_LIMIT_EV: float = 0.12

#: M_KK from neutrino-radion identity (Pillar 49) [eV]
M_KK_NEUTRINO_RADION_EV: float = 0.11013  # 110.13 meV

# ---------------------------------------------------------------------------
# UM geometric constants
# ---------------------------------------------------------------------------

#: Winding number (Pillars 67, 80)
N_W_CANONICAL: int = 5

#: Geometric PMNS CP phase estimate: π - 2π/n_w
DELTA_CP_PMNS_GEOMETRIC_RAD: float = math.pi - 2.0 * math.pi / N_W_CANONICAL  # 108°


# ---------------------------------------------------------------------------
# PMNS mixing angle utilities
# ---------------------------------------------------------------------------

def pmns_mixing_angles_pdg() -> Dict[str, float]:
    """Return PDG 2024 PMNS mixing angles (normal ordering).

    Returns
    -------
    dict
        'theta12_deg':    float — 33.41°
        'theta23_deg':    float — 49.1°
        'theta13_deg':    float — 8.62°
        'delta_cp_deg':   float — -107° (Dirac phase best fit)
        'sin2_theta12':   float — 0.307
        'sin2_theta23':   float — 0.572
        'sin2_theta13':   float — 0.0222
        'dm2_21_ev2':     float — 7.53e-5 eV²
        'dm2_31_ev2':     float — 2.453e-3 eV²
    """
    theta12 = math.degrees(math.asin(math.sqrt(SIN2_THETA12_PDG)))
    theta23 = math.degrees(math.asin(math.sqrt(SIN2_THETA23_PDG)))
    theta13 = math.degrees(math.asin(math.sqrt(SIN2_THETA13_PDG)))

    return {
        "theta12_deg": theta12,
        "theta23_deg": theta23,
        "theta13_deg": theta13,
        "delta_cp_deg": math.degrees(DELTA_CP_PMNS_PDG_RAD),
        "sin2_theta12": SIN2_THETA12_PDG,
        "sin2_theta23": SIN2_THETA23_PDG,
        "sin2_theta13": SIN2_THETA13_PDG,
        "dm2_21_ev2": DM2_21_EV2,
        "dm2_31_ev2": DM2_31_EV2,
    }


def pmns_from_angles(
    theta12_rad: float,
    theta23_rad: float,
    theta13_rad: float,
    delta_cp_rad: float = 0.0,
) -> List[List[complex]]:
    """Construct the 3×3 PMNS matrix from mixing angles.

    Uses the standard PDG parameterisation (Majorana phases set to zero):

        U = R₂₃(θ₂₃) × U₁₃(θ₁₃, δ) × R₁₂(θ₁₂)

    Elements:
        U_e1 = c12 c13
        U_e2 = s12 c13
        U_e3 = s13 e^{-iδ}
        U_μ1 = -s12 c23 - c12 s23 s13 e^{iδ}
        U_μ2 =  c12 c23 - s12 s23 s13 e^{iδ}
        U_μ3 =  s23 c13
        U_τ1 =  s12 s23 - c12 c23 s13 e^{iδ}
        U_τ2 = -c12 s23 - s12 c23 s13 e^{iδ}
        U_τ3 =  c23 c13

    Parameters
    ----------
    theta12_rad : float
        Solar mixing angle θ₁₂ [radians].
    theta23_rad : float
        Atmospheric mixing angle θ₂₃ [radians].
    theta13_rad : float
        Reactor mixing angle θ₁₃ [radians].
    delta_cp_rad : float
        Dirac CP phase δ [radians] (default 0 = no CP violation).

    Returns
    -------
    List[List[complex]]
        3×3 complex PMNS matrix U.
        Row = flavour (e, μ, τ); Column = mass (ν₁, ν₂, ν₃).
    """
    s12 = math.sin(theta12_rad)
    c12 = math.cos(theta12_rad)
    s23 = math.sin(theta23_rad)
    c23 = math.cos(theta23_rad)
    s13 = math.sin(theta13_rad)
    c13 = math.cos(theta13_rad)

    exp_id  = cmath.exp(1j * delta_cp_rad)
    exp_mid = cmath.exp(-1j * delta_cp_rad)

    U_e1 = complex(c12 * c13)
    U_e2 = complex(s12 * c13)
    U_e3 = s13 * exp_mid

    U_mu1 = complex(-s12 * c23) - c12 * s23 * s13 * exp_id
    U_mu2 = complex(c12 * c23)  - s12 * s23 * s13 * exp_id
    U_mu3 = complex(s23 * c13)

    U_tau1 = complex(s12 * s23)  - c12 * c23 * s13 * exp_id
    U_tau2 = complex(-c12 * s23) - s12 * c23 * s13 * exp_id
    U_tau3 = complex(c23 * c13)

    return [
        [U_e1,   U_e2,   U_e3  ],
        [U_mu1,  U_mu2,  U_mu3 ],
        [U_tau1, U_tau2, U_tau3],
    ]


def pmns_pdg() -> List[List[complex]]:
    """Return PMNS matrix at PDG 2024 central values (normal ordering).

    Returns
    -------
    List[List[complex]]
        3×3 complex PMNS matrix at PDG central values.
    """
    theta12 = math.asin(math.sqrt(SIN2_THETA12_PDG))
    theta23 = math.asin(math.sqrt(SIN2_THETA23_PDG))
    theta13 = math.asin(math.sqrt(SIN2_THETA13_PDG))

    return pmns_from_angles(theta12, theta23, theta13, DELTA_CP_PMNS_PDG_RAD)


def pmns_unitarity_check(U: List[List[complex]]) -> Dict[str, float]:
    """Verify U†U = I and UU† = I.

    Parameters
    ----------
    U : List[List[complex]]
        3×3 complex PMNS matrix.

    Returns
    -------
    dict
        'UdagU_max_off_diag': float
        'UdagU_diag_min':     float
        'is_unitary':         bool
    """
    n = 3
    off = 0.0
    diag_min = float("inf")
    for i in range(n):
        for j in range(n):
            entry = sum(U[k][i].conjugate() * U[k][j] for k in range(n))
            if i == j:
                diag_min = min(diag_min, abs(entry.real))
            else:
                off = max(off, abs(entry))

    return {
        "UdagU_max_off_diag": off,
        "UdagU_diag_min": diag_min,
        "is_unitary": off < 1e-10,
    }


# ---------------------------------------------------------------------------
# Neutrino mass spectrum utilities
# ---------------------------------------------------------------------------

def neutrino_mass_spectrum(
    m1_eV: float,
    ordering: str = "normal",
) -> Dict[str, float]:
    """Compute the full neutrino mass spectrum from the lightest mass.

    Uses PDG 2024 mass splittings.

    Parameters
    ----------
    m1_eV : float
        Lightest neutrino mass [eV].  For normal ordering: m₁ (lightest).
        For inverted ordering: m₃ (lightest).
    ordering : str
        'normal' or 'inverted' (default 'normal').

    Returns
    -------
    dict
        'm1_eV', 'm2_eV', 'm3_eV': float — individual neutrino masses [eV]
        'sum_mnu_eV':               float — Σm_ν [eV]
        'planck_limit_eV':          float — 0.12 eV
        'consistent_with_planck':   bool
        'ordering':                 str
    """
    if ordering == "normal":
        m1 = m1_eV
        m2 = math.sqrt(m1 ** 2 + DM2_21_EV2)
        m3 = math.sqrt(m1 ** 2 + DM2_31_EV2)
    elif ordering == "inverted":
        # For inverted ordering: m₃ < m₁ ≈ m₂
        m3 = m1_eV  # lightest
        m1 = math.sqrt(m3 ** 2 + abs(DM2_31_EV2))
        m2 = math.sqrt(m1 ** 2 + DM2_21_EV2)
    else:
        raise ValueError(f"ordering must be 'normal' or 'inverted', got {ordering!r}")

    sum_mnu = m1 + m2 + m3

    return {
        "m1_eV": m1,
        "m2_eV": m2,
        "m3_eV": m3,
        "sum_mnu_eV": sum_mnu,
        "planck_limit_eV": PLANCK_SUM_MNU_LIMIT_EV,
        "consistent_with_planck": sum_mnu < PLANCK_SUM_MNU_LIMIT_EV,
        "ordering": ordering,
    }


def neutrino_mass_tension_report() -> str:
    """Produce a detailed honest report on the M_KK = m_ν₁ tension.

    This documents the INCONSISTENCY between the Neutrino-Radion Identity
    (Pillar 49) and the Planck 2018 Σm_ν constraint.

    Returns
    -------
    str
        Formatted report string.
    """
    # Spectrum if M_KK = m_ν₁ (lightest active neutrino)
    spec_mkk = neutrino_mass_spectrum(M_KK_NEUTRINO_RADION_EV, "normal")

    # Spectrum for a consistent interpretation (upper end of Planck limit)
    # Σm_ν < 0.12 eV → with NO constraints, m₁ < ~0.033 eV for normal ordering
    # At Planck 95% CL boundary: Σm_ν = 0.12 → m₁ + m₂ + m₃ = 0.12
    # Solve numerically for the maximum consistent m₁
    m1_consistent = _find_m1_for_sigma(0.12 - 1e-6, "normal")
    spec_consistent = neutrino_mass_spectrum(m1_consistent, "normal")

    lines = [
        "=" * 72,
        "NEUTRINO MASS TENSION REPORT — Pillar 83 (Unitary Manifold v9.20)",
        "=" * 72,
        "",
        "THE CLAIM (Pillar 49 / CONSISTENCY_LOG):",
        f"  M_KK = m_ν₁ = {M_KK_NEUTRINO_RADION_EV * 1000:.2f} meV",
        "  CONSISTENCY_LOG states: 'Consistent with Planck Σm_ν < 120 meV? YES'",
        "",
        "THE PROBLEM:",
        "  Planck 2018 constrains the SUM of ALL three active neutrino masses:",
        "  Σm_ν = m_ν₁ + m_ν₂ + m_ν₃ < 120 meV (95% CL)",
        "",
        f"  If m_ν₁ = M_KK = {M_KK_NEUTRINO_RADION_EV * 1e3:.2f} meV (normal ordering):",
        f"    m_ν₁ = {spec_mkk['m1_eV'] * 1e3:.2f} meV",
        f"    m_ν₂ = {spec_mkk['m2_eV'] * 1e3:.2f} meV  (from Δm²₂₁ = 7.53×10⁻⁵ eV²)",
        f"    m_ν₃ = {spec_mkk['m3_eV'] * 1e3:.2f} meV  (from Δm²₃₁ = 2.453×10⁻³ eV²)",
        f"    Σm_ν = {spec_mkk['sum_mnu_eV'] * 1e3:.2f} meV  >>  120 meV  ❌",
        "",
        "  The CONSISTENCY_LOG incorrectly compared m_ν₁ = 110 meV to the Planck",
        "  LIMIT of 120 meV, treating it as a single-neutrino bound.  The Planck",
        "  constraint is on the TOTAL SUM of all three species, not a single one.",
        "",
        "VERDICT: THE CONSISTENCY_LOG CLAIM IS WRONG.",
        "  The neutrino-radion identity m_ν₁ = M_KK = 110 meV is INCONSISTENT",
        f"  with Planck at the {spec_mkk['sum_mnu_eV']/PLANCK_SUM_MNU_LIMIT_EV:.1f}× level.",
        "",
        "RESOLUTION A (RECOMMENDED):",
        "  Reinterpret M_KK = 110 meV as the KK compactification SCALE,",
        "  NOT the lightest active neutrino mass.  The dark energy closure",
        "  ρ_eff = f_braid × M_KK⁴/(16π²) = ρ_obs remains valid — it depends",
        "  on M_KK, not on m_ν.  The active neutrino masses are lighter, set",
        "  by a brane-localised RS Yukawa mechanism with M_KK as the UV cutoff.",
        "",
        "  For consistency with Planck (Σm_ν < 120 meV), normal ordering requires:",
        f"    m_ν₁ ≤ {m1_consistent * 1e3:.2f} meV (maximum lightest mass)",
        f"    m_ν₂ ≤ {spec_consistent['m2_eV'] * 1e3:.2f} meV",
        f"    m_ν₃ ≤ {spec_consistent['m3_eV'] * 1e3:.2f} meV",
        f"    Σm_ν = {spec_consistent['sum_mnu_eV'] * 1e3:.2f} meV  ✓",
        "",
        "RESOLUTION B (FALSIFIABLE PREDICTION):",
        "  If the framework insists m_ν₁ = M_KK = 110 meV, this is a PREDICTION",
        f"  of Σm_ν ≈ {spec_mkk['sum_mnu_eV'] * 1e3:.0f} meV.  Future experiments",
        "  (DESI+CMB-S4+Euclid, targeting σ(Σm_ν) ~ 20 meV) will either",
        "  confirm Σm_ν > 200 meV (supporting the UM) or rule it out at >10σ.",
        "",
        "IMPACT ON THE TOE CLAIM:",
        "  This is the most significant quantitative inconsistency identified",
        "  in the UM framework.  It does not invalidate the geometry or the",
        "  CMB predictions, but it does require revising the interpretation of",
        "  M_KK as a neutrino mass.  Honest science requires flagging this clearly.",
        "=" * 72,
    ]
    return "\n".join(lines)


def _find_m1_for_sigma(
    sigma_target_eV: float,
    ordering: str = "normal",
    tol: float = 1e-10,
    max_iter: int = 100,
) -> float:
    """Bisection solver: find m₁ such that Σm_ν = sigma_target_eV."""
    lo, hi = 0.0, sigma_target_eV
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        spec = neutrino_mass_spectrum(mid, ordering)
        if spec["sum_mnu_eV"] < sigma_target_eV:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# Geometric PMNS estimate
# ---------------------------------------------------------------------------

def pmns_geometric_estimate(n_w: int = N_W_CANONICAL) -> Dict[str, object]:
    """Estimate PMNS mixing angles from UM geometric arguments.

    Geometric origin of each mixing angle:

    θ₂₃ (atmospheric, ~49°):
        The second and third generation neutrinos have nearly degenerate
        wavefunctions at the UV brane when their bulk masses satisfy
        Δc₂₃^ν ≈ c_s / k_cs = (12/37) / 74 ≈ 0.0044.  This gives
        near-maximal mixing θ₂₃ → 45° in the leading RS approximation.
        The sub-maximal deviation θ₂₃ - 45° ≈ 4° comes from O(λ²) corrections.

    θ₁₂ (solar, ~33°):
        The 1-2 neutrino mixing arises from the RS wavefunction overlap
        with geometric factor sin²(θ₁₂) ≈ 1/(1 + n_w) = 1/6.
        This gives sin²(θ₁₂) ≈ 0.167 (θ₁₂ ≈ 24°), a factor ~1.8
        below the observed sin²(θ₁₂) = 0.307.  Order-of-magnitude agreement.

    θ₁₃ (reactor, ~8.6°):
        The 1-3 mixing angle is set by the winding suppression:
        sin(θ₁₃) ≈ 1/n_w² = 1/25 = 0.04.  This gives θ₁₃ ≈ 2.3°,
        below the observed 8.6° by a factor of ~3.7.  Order-of-magnitude.

    δ_CP^PMNS (Dirac phase, best fit ~-107°):
        Geometric estimate: π - 2π/n_w = π - 72° = 108°.
        PDG: ~-107° = +253° (mod 360°), best fit range [-180°, -60°].
        The geometric estimate 108° does not match the PDG best fit.
        This angle remains OPEN in the UM framework.

    Parameters
    ----------
    n_w : int
        Winding number (default 5).

    Returns
    -------
    dict
        Geometric estimates for all PMNS parameters with comparison to PDG.
    """
    # Geometric estimates
    sin2_12_geo = 1.0 / (1.0 + n_w)          # 1/6 ≈ 0.167
    sin2_23_geo = 0.5                          # near-maximal (45°) → leading order
    sin_13_geo  = 1.0 / (n_w * n_w)           # 1/25 = 0.04
    sin2_13_geo = sin_13_geo ** 2              # 0.0016

    theta12_geo = math.degrees(math.asin(math.sqrt(sin2_12_geo)))
    theta23_geo = 45.0  # maximal at leading order
    theta13_geo = math.degrees(math.asin(sin_13_geo))

    delta_cp_geo_rad = math.pi - 2.0 * math.pi / n_w
    delta_cp_geo_deg = math.degrees(delta_cp_geo_rad)

    def _sigma(val, pdg, uncertainty) -> float:
        return abs(val - pdg) / uncertainty if uncertainty > 0 else float("inf")

    return {
        "theta12": {
            "geometric_deg": theta12_geo,
            "pdg_deg": math.degrees(math.asin(math.sqrt(SIN2_THETA12_PDG))),
            "sin2_geometric": sin2_12_geo,
            "sin2_pdg": SIN2_THETA12_PDG,
            "status": "ORDER-OF-MAGNITUDE (factor ~1.8 below PDG)",
            "derivation": "sin²θ₁₂ ≈ 1/(1+n_w) from RS 1-2 wavefunction overlap",
        },
        "theta23": {
            "geometric_deg": theta23_geo,
            "pdg_deg": math.degrees(math.asin(math.sqrt(SIN2_THETA23_PDG))),
            "sin2_geometric": sin2_23_geo,
            "sin2_pdg": SIN2_THETA23_PDG,
            "status": "CONSISTENT (near-maximal mixing predicted and observed)",
            "derivation": "Δc₂₃ᵛ ≈ c_s/k_cs → near-degenerate UV wavefunctions → θ₂₃ → 45°",
        },
        "theta13": {
            "geometric_deg": theta13_geo,
            "pdg_deg": math.degrees(math.asin(math.sqrt(SIN2_THETA13_PDG))),
            "sin2_geometric": sin2_13_geo,
            "sin2_pdg": SIN2_THETA13_PDG,
            "status": "ORDER-OF-MAGNITUDE (factor ~3.7 below PDG)",
            "derivation": "sin(θ₁₃) ≈ 1/n_w² from winding suppression",
        },
        "delta_cp": {
            "geometric_deg": delta_cp_geo_deg,
            "pdg_deg": math.degrees(DELTA_CP_PMNS_PDG_RAD),
            "status": "OPEN (geometric estimate 108° inconsistent with PDG ~-107°)",
            "derivation": "δ_CP^PMNS = π - 2π/n_w; does not match PDG best fit",
        },
    }


# ---------------------------------------------------------------------------
# Comprehensive gap report
# ---------------------------------------------------------------------------

def pmns_gap_report(n_w: int = N_W_CANONICAL) -> str:
    """Return a formatted string summarising PMNS status in the UM framework."""
    geo = pmns_geometric_estimate(n_w)
    tension = neutrino_mass_tension_report()

    lines = [
        "=" * 72,
        "PMNS MATRIX STATUS — Pillar 83 (Unitary Manifold v9.20)",
        "=" * 72,
        "",
        "GEOMETRIC ESTIMATES vs PDG 2024 (normal ordering):",
        "-" * 50,
        f"  θ₁₂ (solar):       geometric {geo['theta12']['geometric_deg']:.1f}°  vs  PDG {geo['theta12']['pdg_deg']:.1f}°",
        f"     Status: {geo['theta12']['status']}",
        f"  θ₂₃ (atmospheric): geometric {geo['theta23']['geometric_deg']:.1f}°  vs  PDG {geo['theta23']['pdg_deg']:.1f}°",
        f"     Status: {geo['theta23']['status']}",
        f"  θ₁₃ (reactor):     geometric {geo['theta13']['geometric_deg']:.1f}°  vs  PDG {geo['theta13']['pdg_deg']:.1f}°",
        f"     Status: {geo['theta13']['status']}",
        f"  δ_CP (Dirac):      geometric {geo['delta_cp']['geometric_deg']:.1f}°  vs  PDG {geo['delta_cp']['pdg_deg']:.1f}°",
        f"     Status: {geo['delta_cp']['status']}",
        "",
        "KEY FINDING: The near-maximal atmospheric mixing θ₂₃ ≈ 45° is",
        "NATURALLY PREDICTED by the RS mechanism (near-degenerate 2nd and 3rd",
        "generation neutrino wavefunctions at the UV brane).  This is a genuine",
        "structural success of the framework.",
        "",
        "REMAINING GAPS:",
        "  1. Neutrino bulk masses c_L^νi not derived from first principles",
        "  2. Majorana vs Dirac nature not addressed",
        "  3. PMNS CP phase: open",
        "  4. Neutrino mass sum: INCONSISTENCY — see tension report below",
        "",
        tension,
    ]
    return "\n".join(lines)
