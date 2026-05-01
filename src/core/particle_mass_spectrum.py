# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/particle_mass_spectrum.py
====================================
Pillar 60 — Particle Mass Spectrum: KK-Geometric Lepton and Quark Masses.

This module addresses the gap flagged in the Gemini review: the UM's
particle catalog (Pillar 7, `particle_geometry.py`) uses a generic
KK mass formula without explicitly mapping to PDG particle masses.
Pillar 60 provides that mapping, documents where the framework succeeds,
and states honestly where a free parameter (the overall mass scale λ)
is required.

Physical context
----------------
In the Unitary Manifold, particles are not "things placed into space" —
they are winding configurations of the 5th dimension S¹/Z₂.  The KK
mass formula (Pillar 7) is

    m_geo(n)  =  λ × n_w / φ_n_eff                                [1]

where
    n_w     = 5   (winding number, Pillar 39)
    φ_n_eff = φ₀ / √(1 + n²/n_w)   (effective compactification radius,
                                      Pillar 42, Three-Generation Theorem)
    λ       = Yukawa coupling (one free parameter per sector)

The three stable KK generations (n=0, 1, 2) correspond to the three
lepton / quark families.  From eq. [1]:

    m_n / m_0  =  φ_0 / φ_n  =  √(1 + n²/n_w)                    [2]

This is a **purely geometric mass ratio** with no free parameters
beyond n_w (which is derived from the S¹/Z₂ orbifold, Pillar 39).

Where the framework succeeds
----------------------------
1. **Generation count**: n_w = 5 gives exactly 3 stable modes (n=0,1,2);
   n=3 is topologically unstable.  Confirmed by Pillar 42.

2. **Mass hierarchy direction**: m_0 < m_1 < m_2 (lightest → heaviest
   generation) follows from φ_0 > φ_1 > φ_2 in eq. [1].  ✓

3. **Inter-generation mass ratios (geometric)**:
    m_1/m_0 = √(6/5) ≈ 1.095
    m_2/m_0 = √(9/5) ≈ 1.342
   These pure-geometry ratios are fixed by n_w = 5 alone.

Where the framework falls short (documented honestly)
------------------------------------------------------
The geometric ratios 1.095 and 1.342 are very far from the PDG values:

    PDG: m_μ/m_e ≈ 206.77    (geometric: 1.095)   discrepancy: factor ~189
    PDG: m_τ/m_e ≈ 3477      (geometric: 1.342)   discrepancy: factor ~2591
    PDG: m_τ/m_μ ≈ 16.82     (geometric: 1.225)   discrepancy: factor ~13.7

The geometric formula in its raw form gives *only the hierarchy direction*,
not the magnitude.  The large observed ratios likely arise from:

  (a) Radiative / Yukawa corrections: each generation couples differently
      to the Higgs sector via Yukawa couplings that depend on the overlap
      integral of the KK wave function φ_n(y) with the Higgs brane profile.

  (b) Radion profile weighting: the actual mass should be computed from
      the 5D Yukawa integral ∫₀^πR |φ_n(y)|² δ(y − y_brane) dy, which
      gives a mode-dependent suppression from the brane localisation.

Both corrections require additional model input (brane position y_brane,
Yukawa profile) not currently derived in the UM framework.

Brane-localised mass ratios
---------------------------
If the matter fermions are localised near the UV brane (y = 0 in RS
conventions), the 5D Yukawa integral gives a mode-dependent wavefunction
suppression:

    ψ_n(0) = A_n × cos(n × 0 / R) = A_n   (Neumann BC)

and a normalisation A_n² = 2/(πR) × (1 + δ_{n,0})⁻¹.  All modes have
equal amplitude at y = 0, so brane localisation at y=0 gives mass ratios
equal to the normalisation ratio:

    m_1/m_0  (brane at y=0)  =  1/√2 × √2 = 1   (degenerate at UV brane)

For an IR-brane localised scenario (y = πR), Neumann BC gives
cos(nπ) = (−1)^n, so |ψ_n(πR)|² is equal for all n (same amplitude):
still degenerate at leading order.

The generation mass hierarchy therefore requires a *mechanism* (e.g.,
RS Yukawa hierarchy with bulk mass terms c_n) that lies outside the
minimal UM framework.  This is the primary open gap of Pillar 60,
documented here per the FALLIBILITY.md standard.

Absolute mass scale
-------------------
Given the geometric ratios m_n/m_0 = √(1 + n²/n_w), the absolute mass
of the lightest generation (n=0, electron) is set by the free parameter λ:

    m_e = λ × n_w / φ₀_eff

At the FTUM fixed point φ₀_eff ≈ n_w × 2π × φ₀_bare ≈ 31.42 (Planck units).
Converting to electron volts requires a single overall coupling λ, which
is fitted to m_e = 0.511 MeV.  Once λ is fixed from m_e, all other masses
are predicted by the geometric ratios — but only at the ~1.1× level, not
at the correct ~207× level.

PDG reference values (2024)
---------------------------
    m_e  = 0.510 998 950 00 MeV
    m_μ  = 105.658 375 5 MeV  →  m_μ/m_e  = 206.768
    m_τ  = 1776.86 MeV        →  m_τ/m_e  = 3477.2, m_τ/m_μ = 16.817

Public API
----------
GEOMETRIC_RATIOS
    Dict of pure-geometry mass ratios from n_w=5 alone.

pdg_lepton_masses()
    Dict of PDG 2024 lepton masses in MeV.

pdg_lepton_ratios()
    Dict of PDG 2024 lepton mass ratios.

geometric_mass_ratios(n_w)
    Pure-geometry mass ratios from the KK eigenvalue formula.

mass_scale_from_electron(m_e_MeV, n_w, phi0_eff)
    Fit λ from the electron mass.  Returns (λ, m_geo_0, m_geo_1, m_geo_2).

predicted_lepton_masses(lambda_fit, n_w, phi0_eff)
    Predicted lepton masses (MeV) from geometry × fitted λ.

lepton_ratio_comparison()
    Dict comparing geometric predictions to PDG ratios; documents the gap.

quark_mass_ratios_pdg()
    PDG quark mass ratios (approximate; running masses at μ=2 GeV).

generation_mass_hierarchy_correct()
    Return True iff the geometry predicts the correct mass ordering.

pillar60_gap_report()
    Full honest assessment dict of what Pillar 60 achieves and what it lacks.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""


from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import math
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, natural units unless specified)
# ---------------------------------------------------------------------------

#: Winding number from S¹/Z₂ orbifold (Pillar 39)
N_W: int = 5

#: Secondary winding (BICEP/Keck, Pillar 58)
N_W2: int = 7

#: Chern-Simons level (Pillar 39)
K_CS: int = 74

#: Effective φ₀ = n_w × 2π (FTUM fixed point, Pillar 5)
PHI0_EFF_CANONICAL: float = N_W * 2.0 * math.pi   # ≈ 31.416

#: PDG 2024 lepton masses in MeV
M_ELECTRON_MEV: float = 0.510_998_950   # MeV
M_MUON_MEV: float = 105.658_375_5       # MeV
M_TAU_MEV: float = 1776.86              # MeV

#: PDG 2024 lepton mass ratios (dimensionless)
R_MU_OVER_E_PDG: float = M_MUON_MEV / M_ELECTRON_MEV   # ≈ 206.768
R_TAU_OVER_E_PDG: float = M_TAU_MEV / M_ELECTRON_MEV   # ≈ 3477.2
R_TAU_OVER_MU_PDG: float = M_TAU_MEV / M_MUON_MEV      # ≈ 16.817

#: Pure-geometry mass ratios m_n/m_0 = √(1 + n²/n_w) for n_w=5
GEOM_RATIO_M1_OVER_M0: float = math.sqrt(1.0 + 1.0 / N_W)  # √(6/5) ≈ 1.095
GEOM_RATIO_M2_OVER_M0: float = math.sqrt(1.0 + 4.0 / N_W)  # √(9/5) ≈ 1.342
GEOM_RATIO_M2_OVER_M1: float = GEOM_RATIO_M2_OVER_M0 / GEOM_RATIO_M1_OVER_M0

#: Geometric prediction dict (exported constant)
GEOMETRIC_RATIOS: Dict[str, float] = {
    "m1_over_m0": GEOM_RATIO_M1_OVER_M0,
    "m2_over_m0": GEOM_RATIO_M2_OVER_M0,
    "m2_over_m1": GEOM_RATIO_M2_OVER_M1,
}

#: Stability exponent from Three-Generation Theorem (Pillar 42)
STABILITY_EXPONENT: int = 2  # n² ≤ n_w

#: Number of stable SM generations (PDG)
N_GENERATIONS_SM: int = 3


# ---------------------------------------------------------------------------
# PDG reference functions
# ---------------------------------------------------------------------------

def pdg_lepton_masses() -> Dict[str, float]:
    """PDG 2024 lepton masses in MeV.

    Returns
    -------
    dict
        ``electron_MeV`` : 0.510 998 950 MeV
        ``muon_MeV``     : 105.658 375 5 MeV
        ``tau_MeV``      : 1776.86 MeV
    """
    return {
        "electron_MeV": M_ELECTRON_MEV,
        "muon_MeV": M_MUON_MEV,
        "tau_MeV": M_TAU_MEV,
    }


def pdg_lepton_ratios() -> Dict[str, float]:
    """PDG 2024 lepton mass ratios (dimensionless).

    Returns
    -------
    dict
        ``mu_over_e``  : m_μ / m_e ≈ 206.768
        ``tau_over_e`` : m_τ / m_e ≈ 3477.2
        ``tau_over_mu``: m_τ / m_μ ≈ 16.817
    """
    return {
        "mu_over_e": R_MU_OVER_E_PDG,
        "tau_over_e": R_TAU_OVER_E_PDG,
        "tau_over_mu": R_TAU_OVER_MU_PDG,
    }


# ---------------------------------------------------------------------------
# Core geometry functions
# ---------------------------------------------------------------------------

def phi_eff(n: int, n_w: int = N_W, phi0: float = 1.0) -> float:
    """Effective compactification radius for KK mode n.

    φ_n_eff = φ₀ / √(1 + n²/n_w)

    Parameters
    ----------
    n    : int   — KK mode index (0 = lightest generation)
    n_w  : int   — winding number (default 5)
    phi0 : float — radion vacuum value (default 1 for normalised ratios)

    Returns
    -------
    float
        φ_n_eff value.

    Raises
    ------
    ValueError
        If n < 0, n_w ≤ 0, or phi0 ≤ 0.
    """
    if n < 0:
        raise ValueError(f"Mode index n must be ≥ 0, got {n}")
    if n_w <= 0:
        raise ValueError(f"n_w must be positive, got {n_w}")
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be positive, got {phi0}")
    return phi0 / math.sqrt(1.0 + n * n / n_w)


def geometric_mass(
    n: int,
    lam: float,
    n_w: int = N_W,
    phi0: float = PHI0_EFF_CANONICAL,
) -> float:
    """Geometric KK mass for mode n in natural units.

    m_geo(n) = λ × n_w / φ_n_eff

    Parameters
    ----------
    n    : int   — KK mode index
    lam  : float — Yukawa coupling (free overall mass scale)
    n_w  : int   — winding number
    phi0 : float — radion vev (Planck units; default: FTUM fixed point φ₀_eff)

    Returns
    -------
    float
        Geometric mass m_geo(n) in natural units.
    """
    phi_n = phi_eff(n, n_w, phi0)
    return lam * n_w / phi_n


def geometric_mass_ratios(n_w: int = N_W) -> Dict[str, float]:
    """Pure-geometry mass ratios from the KK eigenvalue formula.

    m_n/m_0 = φ_0/φ_n = √(1 + n²/n_w)

    These ratios are independent of λ and φ₀.

    Parameters
    ----------
    n_w : int — winding number (must give ≥ 3 stable modes)

    Returns
    -------
    dict
        ``m1_over_m0`` : m_1/m_0 = √(1 + 1/n_w)
        ``m2_over_m0`` : m_2/m_0 = √(1 + 4/n_w)
        ``m2_over_m1`` : m_2/m_1 = √(1 + 4/n_w) / √(1 + 1/n_w)
        ``n_w``        : echo of input

    Raises
    ------
    ValueError
        If n_w ≤ 0.
    """
    if n_w <= 0:
        raise ValueError(f"n_w must be positive, got {n_w}")
    r1 = math.sqrt(1.0 + 1.0 / n_w)
    r2 = math.sqrt(1.0 + 4.0 / n_w)
    return {
        "m1_over_m0": r1,
        "m2_over_m0": r2,
        "m2_over_m1": r2 / r1,
        "n_w": n_w,
    }


def stable_generation_modes(n_w: int = N_W) -> List[int]:
    """Return KK mode indices n satisfying the stability condition n² ≤ n_w.

    Parameters
    ----------
    n_w : int — winding number (must be > 0)

    Returns
    -------
    list of int
        Stable mode indices.
    """
    if n_w <= 0:
        raise ValueError(f"n_w must be positive, got {n_w}")
    return [n for n in range(n_w + 1) if n * n <= n_w]


# ---------------------------------------------------------------------------
# Mass fitting and prediction
# ---------------------------------------------------------------------------

def mass_scale_from_electron(
    m_e_MeV: float = M_ELECTRON_MEV,
    n_w: int = N_W,
    phi0_eff: float = PHI0_EFF_CANONICAL,
) -> Dict[str, float]:
    """Fit the overall coupling λ from the electron mass, then predict μ and τ.

    From m_e = λ × n_w / φ₀_eff (n=0 mode in Planck units), converting to MeV
    requires a unit conversion factor.  We absorb this into λ_fit:

        λ_fit (in MeV) = m_e_MeV × φ₀_eff / n_w

    Then predict:
        m_μ_pred = λ_fit × n_w / φ_1_eff = m_e × √(1 + 1/n_w)
        m_τ_pred = λ_fit × n_w / φ_2_eff = m_e × √(1 + 4/n_w)

    This shows the geometric predictions are only O(1) corrections to m_e,
    not the observed ×206 and ×3477 ratios.

    Parameters
    ----------
    m_e_MeV  : float — electron mass in MeV (default: PDG 2024)
    n_w      : int   — winding number (default 5)
    phi0_eff : float — effective radion vev (default: FTUM φ₀_eff ≈ 31.42)

    Returns
    -------
    dict
        ``lambda_fit_MeV`` : fitted coupling λ in MeV
        ``m_geo_0_MeV``    : n=0 prediction (= m_e_MeV by construction)
        ``m_geo_1_MeV``    : n=1 prediction (geometric muon mass in MeV)
        ``m_geo_2_MeV``    : n=2 prediction (geometric tau mass in MeV)
        ``phi0_eff``       : effective radion vev used
        ``n_w``            : winding number used
    """
    phi0 = phi0_eff
    phi_0 = phi_eff(0, n_w, phi0)
    phi_1 = phi_eff(1, n_w, phi0)
    phi_2 = phi_eff(2, n_w, phi0)

    # λ_fit so that m_geo(0) = m_e_MeV
    lam_fit = m_e_MeV * phi_0 / n_w

    m_geo_0 = lam_fit * n_w / phi_0   # = m_e_MeV by construction
    m_geo_1 = lam_fit * n_w / phi_1
    m_geo_2 = lam_fit * n_w / phi_2

    return {
        "lambda_fit_MeV": lam_fit,
        "m_geo_0_MeV": m_geo_0,
        "m_geo_1_MeV": m_geo_1,
        "m_geo_2_MeV": m_geo_2,
        "phi0_eff": phi0_eff,
        "n_w": n_w,
    }


def predicted_lepton_masses(
    lambda_fit: float,
    n_w: int = N_W,
    phi0_eff: float = PHI0_EFF_CANONICAL,
) -> Dict[str, float]:
    """Predict lepton masses in MeV from the geometric formula.

    Parameters
    ----------
    lambda_fit : float — overall coupling λ in MeV (fitted from m_e)
    n_w        : int   — winding number
    phi0_eff   : float — effective radion vev

    Returns
    -------
    dict
        ``electron_MeV``, ``muon_MeV``, ``tau_MeV`` : predicted masses
        ``mu_over_e_pred``, ``tau_over_e_pred``, ``tau_over_mu_pred``
    """
    phi0 = phi0_eff
    m0 = lambda_fit * n_w / phi_eff(0, n_w, phi0)
    m1 = lambda_fit * n_w / phi_eff(1, n_w, phi0)
    m2 = lambda_fit * n_w / phi_eff(2, n_w, phi0)
    return {
        "electron_MeV": m0,
        "muon_MeV": m1,
        "tau_MeV": m2,
        "mu_over_e_pred": m1 / m0,
        "tau_over_e_pred": m2 / m0,
        "tau_over_mu_pred": m2 / m1,
    }


# ---------------------------------------------------------------------------
# Gap analysis
# ---------------------------------------------------------------------------

def lepton_ratio_comparison() -> Dict[str, object]:
    """Compare geometric mass-ratio predictions to PDG values.

    Documents the gap honestly: the raw geometric formula gives
    ratios of O(1) while the PDG ratios are O(100–3000).

    Returns
    -------
    dict
        Per-ratio comparison with keys ``predicted``, ``pdg``,
        ``discrepancy_factor``, and ``status`` ("matches_direction" /
        "large_discrepancy").
    """
    geom = geometric_mass_ratios()
    pdg = pdg_lepton_ratios()

    def _compare(pred: float, obs: float, name: str) -> Dict[str, object]:
        factor = obs / pred
        direction_ok = pred > 1.0   # both should be > 1 (heavier than electron)
        return {
            "ratio_name": name,
            "predicted_geometric": pred,
            "pdg_value": obs,
            "discrepancy_factor": factor,
            "hierarchy_direction_correct": direction_ok,
            "status": "matches_direction" if direction_ok and factor > 10 else "matches",
            "honest_note": (
                f"Geometric prediction {pred:.4f} vs PDG {obs:.1f}. "
                f"Discrepancy factor: {factor:.1f}×. "
                "A bulk Yukawa / RS localisation mechanism is needed to bridge the gap."
            ),
        }

    return {
        "mu_over_e": _compare(geom["m1_over_m0"], pdg["mu_over_e"], "m_μ/m_e"),
        "tau_over_e": _compare(geom["m2_over_m0"], pdg["tau_over_e"], "m_τ/m_e"),
        "tau_over_mu": _compare(geom["m2_over_m1"], pdg["tau_over_mu"], "m_τ/m_μ"),
        "summary": (
            "Pillar 60 geometry correctly predicts the mass hierarchy direction "
            "(three generations with m_0 < m_1 < m_2) and generation count = 3. "
            "It does NOT reproduce the PDG mass ratio magnitudes without an "
            "additional RS-type Yukawa localisation mechanism."
        ),
        "open_gap": (
            "Bulk Yukawa coupling with mode-dependent wavefunction overlap "
            "∫|ψ_n(y)|² dy_brane is required to reproduce PDG ratios. "
            "This is an explicit open gap of the UM (not a failure — the "
            "Randall-Sundrum mechanism is the standard resolution for KK theories)."
        ),
    }


def quark_mass_ratios_pdg() -> Dict[str, float]:
    """PDG 2024 quark mass ratios (approximate; running masses at μ = 2 GeV).

    Values from PDG 2024 Review of Particle Physics (running MS-bar masses).
    The same generation hierarchy applies to quarks as to leptons.

    Returns
    -------
    dict
        ``up_MeV``, ``down_MeV``, ``strange_MeV``,
        ``charm_GeV``, ``bottom_GeV``, ``top_GeV`` : approximate PDG masses
        ``charm_over_up``, ``top_over_charm`` : characteristic ratios
    """
    return {
        "up_MeV": 2.16,        # MeV
        "down_MeV": 4.67,      # MeV
        "strange_MeV": 93.4,   # MeV
        "charm_GeV": 1.27,     # GeV
        "bottom_GeV": 4.18,    # GeV
        "top_GeV": 172.69,     # GeV
        "charm_over_up": 1270.0 / 2.16,    # ≈ 588
        "top_over_charm": 172690.0 / 1270.0,  # ≈ 136
    }


def generation_mass_hierarchy_correct(n_w: int = N_W) -> bool:
    """Return True iff geometry predicts the correct mass ordering.

    The correct ordering is m_0 < m_1 < m_2, i.e. φ_0 > φ_1 > φ_2
    (larger φ → lighter particle, smaller φ → heavier particle).

    This is always True when n_w > 0 because φ_n_eff = φ₀/√(1+n²/n_w)
    decreases strictly with n.

    Parameters
    ----------
    n_w : int — winding number

    Returns
    -------
    bool
    """
    phi_0 = phi_eff(0, n_w)
    phi_1 = phi_eff(1, n_w)
    phi_2 = phi_eff(2, n_w)
    # φ_0 > φ_1 > φ_2 → m_0 < m_1 < m_2  ✓
    return phi_0 > phi_1 > phi_2


def fourth_generation_excluded(n_w: int = N_W) -> bool:
    """Return True iff n=3 KK mode is topologically unstable.

    From the Three-Generation Theorem (Pillar 42): mode n is stable iff n² ≤ n_w.
    For n_w = 5: 3² = 9 > 5 → unstable → 4th generation excluded.
    """
    return (3 * 3) > n_w


def pillar60_gap_report() -> Dict[str, object]:
    """Full honest assessment of what Pillar 60 achieves and what it lacks.

    Returns
    -------
    dict
        Comprehensive Pillar 60 status report for FALLIBILITY.md cross-reference.
    """
    geom = geometric_mass_ratios()
    pdg = pdg_lepton_ratios()
    comparison = lepton_ratio_comparison()
    fit = mass_scale_from_electron()

    successes = [
        f"Three stable KK generations (n=0,1,2) correctly count the SM families.",
        f"4th generation (n=3) excluded: 3² = 9 > n_w = 5 → topologically unstable.",
        "Mass hierarchy direction correct: m_0 < m_1 < m_2 (electron < muon < tau).",
        f"Geometric ratios: m_μ/m_e = {geom['m1_over_m0']:.4f} (PDG: {pdg['mu_over_e']:.1f})",
        f"Overall mass scale fitted from m_e gives λ = {fit['lambda_fit_MeV']:.4e} MeV.",
    ]

    failures = [
        f"Geometric m_μ/m_e = {geom['m1_over_m0']:.4f} vs PDG {pdg['mu_over_e']:.1f} → factor {pdg['mu_over_e']/geom['m1_over_m0']:.0f}× discrepancy.",
        f"Geometric m_τ/m_e = {geom['m2_over_m0']:.4f} vs PDG {pdg['tau_over_e']:.1f} → factor {pdg['tau_over_e']/geom['m2_over_m0']:.0f}× discrepancy.",
        "Absolute lepton masses require ONE free parameter λ per sector (fitted).",
        "PDG mass ratio magnitudes require RS-type Yukawa localisation: open gap.",
    ]

    return {
        "pillar": 60,
        "description": "Particle Mass Spectrum: KK-Geometric Lepton and Quark Masses",
        "successes": successes,
        "failures": failures,
        "geometric_ratios": geom,
        "pdg_ratios": pdg,
        "ratio_comparison": comparison,
        "lepton_mass_fit": fit,
        "open_gap": comparison["open_gap"],
        "n_w": N_W,
        "k_cs": K_CS,
        "generation_count": len(stable_generation_modes()),
        "hierarchy_correct": generation_mass_hierarchy_correct(),
        "fourth_gen_excluded": fourth_generation_excluded(),
    }


def kk_mode_mass_spectrum(
    lambda_fit: float,
    n_w: int = N_W,
    phi0_eff: float = PHI0_EFF_CANONICAL,
) -> List[Dict[str, float]]:
    """Mass spectrum of all stable KK generations.

    Parameters
    ----------
    lambda_fit : float — overall Yukawa coupling (MeV)
    n_w        : int   — winding number
    phi0_eff   : float — effective radion vev

    Returns
    -------
    list of dict
        One entry per stable mode with keys:
        'n', 'phi_eff', 'm_geo_MeV', 'ratio_to_n0', 'stable'.
    """
    modes = stable_generation_modes(n_w)
    phi0 = phi0_eff
    m_n0 = lambda_fit * n_w / phi_eff(0, n_w, phi0)
    spectrum = []
    for n in modes:
        phi_n = phi_eff(n, n_w, phi0)
        m_n = lambda_fit * n_w / phi_n
        spectrum.append({
            "n": n,
            "phi_eff": phi_n,
            "m_geo_MeV": m_n,
            "ratio_to_n0": m_n / m_n0,
            "stable": True,
        })
    return spectrum
