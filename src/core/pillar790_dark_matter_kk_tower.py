# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 790 — DARK_MATTER_KK_TOWER

Non-hardgate warped-scale toy tower. The implemented hierarchy is
k R_5 π = log(M_Pl/M_EW), with supplied k/M_Pl = 0.1. The mass ansatz
M_n = n k exp(-k R_5 π) gives M_1 = 24.622 GeV, not 1 TeV.
It is not the unwarped n/R_5 spectrum or a derived graviton eigenvalue
problem; N_W and K_CS do not determine the implemented hierarchy.

The separate 1 TeV benchmark and historical mass/relic windows are retained
as supplied constants for compatibility, not predictions or uncertainties.
The certificate evaluates its central quantities at the computed first mode.

Scattering uses the dimensional toy σ = (g m_N/M²)² [TeV⁻²], with
g = k/M_Pl. Annihilation uses π α²/M² with α = g²/(4π), and the rough
relic prescription Ω h² = 0.1 pb / σv. No constants are fitted to Planck.
1 TeV⁻² = 3.894e-34 cm² = 389.4 pb.

Only an approximate supplied XENON reference at 1 TeV is available.
Other masses have no detector assessment unless a limit is explicitly
supplied. Comparisons are not confidence-level exclusions. Mediator/spin
structure, abundance rescaling, thermal history, mass uncertainties and
mass-dependent detector response remain unresolved.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
N_W = 5                   # braided winding number
K_CS = 74                 # Chern-Simons level (5² + 7²)
M_PL_GEV = 1.2209e19     # Planck mass [GeV]
M_EW_GEV = 246.22        # electroweak VEV [GeV]
HBAR_C_GEV_M = 1.9733e-16  # ħc in GeV·m

# RS1 warp parameters
K_ADS_OVER_MPL = 0.1     # k/M_Pl (AdS curvature, typical RS1 value)
# k·R_5·π determined by hierarchy:
K_R_PI = math.log(M_PL_GEV / M_EW_GEV)  # ≈ 38.4

# Supplied historical benchmark, not computed spectrum or uncertainty bounds.
M_KK_TEV_CENTRAL = 1.0
M_KK_TEV_LOW = 0.8
M_KK_TEV_HIGH = 1.3

# Direct detection
SIGMA_SI_CM2 = 6.0e-47        # supplied historical benchmark, not computed
XENON_NT_LIMIT_CM2_1TEV = 8.0e-47   # XENON-nT 1-tonne-year limit at 1 TeV (approx.)
XENON_NT_EXCLUSION_TEV = 0.5  # legacy value; NOT an exclusion threshold

# Thermal relic
OMEGA_DM_H2_PLANCK = 0.120    # Planck 2018 central value
OMEGA_DM_H2_PLANCK_TOLERANCE = 0.001
# Historical supplied range, not an output of thermal_relic_density.
OMEGA_DM_H2_ESTIMATE_LOW = 0.09
OMEGA_DM_H2_ESTIMATE_HIGH = 0.14

PILLAR_STATUS = "DM_KK_CANDIDATE_QUANTIFIED"
PILLAR_NUMBER = 790
GATE = "DM_KK_CANDIDATE_QUANTIFIED"
TEV2_TO_CM2 = 3.894e-34
TEV2_TO_PB = 389.4


# ---------------------------------------------------------------------------
# Core physics functions
# ---------------------------------------------------------------------------

def compactification_radius_m() -> float:
    """
    5D compactification radius R_5 in metres.

    From RS1: k·R_5·π = log(M_Pl/M_EW)
    R_5 = log(M_Pl/M_EW) / (k·π)
    k = K_ADS_OVER_MPL · M_Pl
    """
    k_gev = K_ADS_OVER_MPL * M_PL_GEV  # GeV
    r5_gev_inv = K_R_PI / (k_gev * math.pi)
    return r5_gev_inv * HBAR_C_GEV_M  # metres


def kk_mass_gev(n: int = 1) -> float:
    """
    n-th KK mode mass in GeV.

    M_n = n · k · e^{−k R_5 π}
    """
    k_gev = K_ADS_OVER_MPL * M_PL_GEV
    return n * k_gev * math.exp(-K_R_PI)


def spin_independent_cross_section_cm2(m_kk_tev: float = M_KK_TEV_CENTRAL) -> float:
    """
    Spin-independent KK–nucleon cross-section estimate [cm²].

    Dimensional toy σ_SI = (g_KK · m_n / M_KK²)² [TeV⁻²].
    No mediator, spin or nuclear-response derivation is provided.
    """
    g_kk = K_ADS_OVER_MPL  # dimensionless coupling
    if not math.isfinite(m_kk_tev) or m_kk_tev <= 0:
        raise ValueError("Mass must be finite and positive in TeV")
    m_n_tev = 0.938e-3  # nucleon mass in TeV
    sigma_tev_neg2 = (g_kk * m_n_tev / m_kk_tev ** 2) ** 2
    return sigma_tev_neg2 * TEV2_TO_CM2


def thermal_relic_density(m_kk_tev: float = M_KK_TEV_CENTRAL) -> float:
    """
    Approximate thermal relic density Ω_DM h².

    Ω h² ≈ 0.1 pb / ⟨σv⟩
    ⟨σv⟩ ~ π·α_KK² / M_KK²  (KK annihilation to SM, tree level)
    α_KK ~ (k/M_Pl)² / (4π) ~ 8×10⁻⁴
    """
    if not math.isfinite(m_kk_tev) or m_kk_tev <= 0:
        raise ValueError("Mass must be finite and positive in TeV")
    alpha_kk = (K_ADS_OVER_MPL ** 2) / (4.0 * math.pi)
    sigma_v_pb = math.pi * alpha_kk ** 2 / (m_kk_tev ** 2) * TEV2_TO_PB
    omega_h2 = 0.1 / sigma_v_pb
    return omega_h2


def is_xenon_nt_excluded(m_kk_tev: float, sigma_si: Optional[float] = None,
                         *, limit_cm2: Optional[float] = None) -> Optional[bool]:
    """
    Legacy name for a toy cross-section/reference-limit comparison.
    Return None without a limit at this mass; no blanket mass exclusion.
    A supplied limit must match the caller's mass and scattering convention.
    """
    if not math.isfinite(m_kk_tev) or m_kk_tev <= 0:
        raise ValueError("Mass must be finite and positive in TeV")
    if sigma_si is None:
        sigma_si = spin_independent_cross_section_cm2(m_kk_tev)
    if not math.isfinite(sigma_si) or sigma_si < 0:
        raise ValueError("Cross-section must be finite and nonnegative in cm²")
    if limit_cm2 is None:
        if not math.isclose(m_kk_tev, 1.0, rel_tol=1e-12):
            return None
        limit_cm2 = XENON_NT_LIMIT_CM2_1TEV
    if not math.isfinite(limit_cm2) or limit_cm2 <= 0:
        raise ValueError("Detector reference must be finite and positive in cm²")
    return sigma_si > limit_cm2


# ---------------------------------------------------------------------------
# KK Tower scan
# ---------------------------------------------------------------------------

@dataclass
class KKModeEntry:
    mode_n: int
    mass_tev: float
    sigma_si_cm2: float
    omega_h2: float
    xenon_excluded: Optional[bool]
    relic_consistent: bool


def scan_kk_tower(n_modes: int = 5) -> list:
    """Return KK tower entries for modes n = 1..n_modes."""
    entries = []
    for n in range(1, n_modes + 1):
        m_tev = kk_mass_gev(n) * 1e-3
        sigma = spin_independent_cross_section_cm2(m_tev)
        omega = thermal_relic_density(m_tev)
        excluded = is_xenon_nt_excluded(m_tev, sigma)
        relic_ok = abs(omega - OMEGA_DM_H2_PLANCK) <= OMEGA_DM_H2_PLANCK_TOLERANCE
        entries.append(KKModeEntry(
            mode_n=n,
            mass_tev=m_tev,
            sigma_si_cm2=sigma,
            omega_h2=omega,
            xenon_excluded=excluded,
            relic_consistent=relic_ok,
        ))
    return entries


# ---------------------------------------------------------------------------
# Dark Matter KK Certificate
# ---------------------------------------------------------------------------

@dataclass
class DarkMatterKKCertificate:
    """Machine-readable DM KK tower certificate."""
    pillar: int = PILLAR_NUMBER
    status: str = PILLAR_STATUS
    gate: str = GATE

    # Central prediction
    m_kk_tev_central: float = field(default_factory=lambda: kk_mass_gev() * 1e-3)
    m_kk_tev_low: Optional[float] = None
    m_kk_tev_high: Optional[float] = None
    supplied_benchmark_mass_tev: float = M_KK_TEV_CENTRAL
    r5_metres: float = 0.0
    k_r_pi: float = K_R_PI

    # Couplings and detection
    sigma_si_cm2_central: Optional[float] = None
    xenon_nt_limit_cm2: Optional[float] = None
    xenon_nt_exclusion_below_tev: Optional[float] = None
    is_excluded_central: Optional[bool] = None
    below_xenon_limit: Optional[bool] = None

    # Relic
    omega_h2_central: Optional[float] = None
    omega_h2_estimate_low: Optional[float] = None
    omega_h2_estimate_high: Optional[float] = None
    omega_h2_planck: float = OMEGA_DM_H2_PLANCK
    relic_consistent: bool = False

    # Tower
    kk_tower: list = field(default_factory=list)

    # Architecture limit
    architecture_limit: str = (
        "Warped mass ansatz and dimensional scattering/annihilation toys only; "
        "mediator/spin structure, thermal history, abundance rescaling, mass "
        "uncertainty and detector limit at computed mass are unresolved."
    )

    # Falsification
    falsification_condition: str = (
        "The toy relic abundance can be compared with Planck but is not a "
        "precision prediction. XENON exclusion requires a mass-dependent "
        "limit and specified recoil/abundance model; no mass-only falsifier."
    )
    pre_registered_experiments: list = field(default_factory=lambda: [
        "XENON-nT (ongoing)", "LZ (2026)", "HL-LHC Run-4 (2029)"
    ])

    failures: int = 0


def compute_dm_kk_certificate() -> DarkMatterKKCertificate:
    """Compute and return the DM KK tower certificate."""
    cert = DarkMatterKKCertificate()
    cert.r5_metres = compactification_radius_m()
    mass = cert.m_kk_tev_central
    cert.sigma_si_cm2_central = spin_independent_cross_section_cm2(mass)
    cert.is_excluded_central = is_xenon_nt_excluded(mass, cert.sigma_si_cm2_central)
    cert.below_xenon_limit = (
        None if cert.is_excluded_central is None else not cert.is_excluded_central
    )
    cert.omega_h2_central = thermal_relic_density(mass)
    cert.relic_consistent = (
        abs(cert.omega_h2_central - OMEGA_DM_H2_PLANCK) <= OMEGA_DM_H2_PLANCK_TOLERANCE
    )
    cert.kk_tower = scan_kk_tower()
    return cert


def get_dm_kk_dict() -> Dict[str, object]:
    """Return DM KK certificate as a plain dict."""
    cert = compute_dm_kk_certificate()
    return {
        "pillar": cert.pillar,
        "status": cert.status,
        "gate": cert.gate,
        "m_kk_tev_central": cert.m_kk_tev_central,
        "supplied_benchmark_mass_tev": cert.supplied_benchmark_mass_tev,
        "m_kk_tev_window": [cert.m_kk_tev_low, cert.m_kk_tev_high],
        "sigma_si_cm2_central": cert.sigma_si_cm2_central,
        "xenon_nt_exclusion_below_tev": cert.xenon_nt_exclusion_below_tev,
        "below_xenon_nt_limit": cert.below_xenon_limit,
        "omega_h2_range": [cert.omega_h2_estimate_low, cert.omega_h2_estimate_high],
        "omega_h2_central": cert.omega_h2_central,
        "is_excluded_central": cert.is_excluded_central,
        "detector_assessment": "unsupported at computed mass",
        "model_scope": "warped mass ansatz and dimensional scattering/annihilation toys",
        "relic_consistent_with_planck": cert.relic_consistent,
        "architecture_limit": cert.architecture_limit,
        "falsification_condition": cert.falsification_condition,
        "pre_registered_experiments": cert.pre_registered_experiments,
    }


DM_KK_CERTIFICATE = get_dm_kk_dict()


def run_pillar790() -> DarkMatterKKCertificate:
    """Entry point: compute and return the DM KK tower certificate."""
    return compute_dm_kk_certificate()
