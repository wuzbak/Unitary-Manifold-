# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/ep_violation.py
=========================
Pillar 37 — Equivalence Principle Violation from the Non-Frozen KK Radion.

Physical context
----------------
The Weak Equivalence Principle (WEP) states that all test bodies fall with
the same acceleration in a gravitational field, regardless of their
composition.  This has been tested to extraordinary precision by the
Eöt-Wash torsion-balance experiments:

    η_EW < 2 × 10⁻¹³     (Bergé et al. 2023, Schlamminger et al. 2008)

where the Eötvös parameter is:

    η = 2 |a₁ − a₂| / |a₁ + a₂|                                   [1]

In the Unitary Manifold framework, the **non-frozen KK radion** (φ ≠ φ₀)
mediates a universal scalar fifth force that couples to the trace of the
stress-energy tensor:

    F_φ = −α_φ × G M / r² × e^{−r/λ_φ}                            [2]

Because the trace coupling is ∝ m_i (mass density), this force is universal
at leading order — it does not violate the WEP.  However, the KK photon A_μ
couples to **baryon number** B, not to mass, so it produces composition-
dependent accelerations.

The Eötvös parameter from the A_μ channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For two test bodies with baryon-to-mass ratios (B/μ)₁ and (B/μ)₂:

    η_KK = α_A × |Δ(B/μ)| × e^{−r/λ_A}                           [3]

where
    α_A = 2            (KK photon coupling to baryon number, relative to G)
    Δ(B/μ) = |(B/μ)₁ − (B/μ)₂|   (composition difference)
    λ_A = R            (KK photon Yukawa range = compactification radius)

For the radion channel (scalar, universal coupling α_φ = 2/3):
    η_φ = 0  (no WEP violation to leading order — universal coupling)

However, the **non-minimal coupling** of the radion to curvature (ξ R φ²)
introduces a small composition-dependent correction:

    η_φ^(NMC) ≈ ξ × α_φ × Δ(B/μ) × (Δm/m)_gravitational            [4]

where Δ(m/m)_grav is the gravitational binding-energy fraction (≈ 10⁻⁵ for
laboratory bodies).

Experimental targets
~~~~~~~~~~~~~~~~~~~~~
- Current Eöt-Wash bound: η < 2 × 10⁻¹³ (Be–Ti comparison at 1 cm)
- STE-QUEST satellite target: η < 10⁻¹⁵ (hydrogen–rubidium at 100 μm)

The UM prediction for the canonical (5,7) branch with R = 10⁻³⁰ m (sub-
Planck compactification):

    η_KK ≈ α_A × |Δ(B/μ)| × e^{−r/R}

For laboratory separations r ≫ R, this is exponentially suppressed:

    η_KK ≈ α_A × |Δ(B/μ)| × exp(−r × m_KK)

If m_KK ≳ 20 meV (λ_A ≲ 10 μm), then for r = 1 cm:

    η_KK < 10⁻⁵⁰   (unobservably small)

**However**, if the radion is very light (m_φ ≲ 20 meV), the radion Yukawa
is within Eöt-Wash range.  In this light-radion scenario, the non-minimal
coupling to curvature generates a WEP violation:

    η_φ^(NMC) ≈ 2/3 × ξ × Δ(B/μ) × ε_grav

This module computes all these predictions and their relation to current
and future EP tests.

Composition differences
~~~~~~~~~~~~~~~~~~~~~~~~
Representative Eötvös-parameter target materials:

    Material pair          Δ(B/μ)
    ──────────────────────────────
    Be–Ti                  0.0032    (Schlamminger et al. 2008)
    Cu–Pb                  0.0010
    Al–Pt                  0.0034
    H–Rb                   0.0014    (STE-QUEST target)
    ─────────────────────────────────────────────────────────

All quantities are in **natural (Planck) units**: ħ = c = G = k_B = 1.

Public API
----------
eotvos_parameter_kk(alpha, delta_b_over_mu, r, yukawa_lambda)
    Eötvös parameter η from the KK Yukawa channel.

eotvos_parameter_radion_nmc(xi, delta_b_over_mu, epsilon_grav)
    Eötvös parameter from non-minimal radion coupling to curvature.

radion_fifth_force(M_source, r, m_phi, alpha)
    Acceleration from the radion fifth force on a test mass.

composition_dependence_kk(n1, n2, R, r, materials)
    Compute η for a list of material pairs given a KK compactification.

ep_violation_in_eot_wash_range(m_phi, alpha)
    Check whether the radion fifth force is within Eöt-Wash sensitivity.

equivalence_principle_summary(m_phi, R, r, delta_b_over_mu)
    Full summary of EP predictions for both channels.

eotvos_cylinder_condition(phi, phi0, alpha, delta_b_over_mu, r, lambda_phi)
    WEP violation as a function of radion displacement from φ₀.

wep_constraint_on_radion_mass(alpha, delta_b_over_mu, r, eta_bound)
    Lower bound on the radion mass from WEP tests.

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
from typing import Sequence


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: KK photon coupling to baryon number (relative to gravity)
ALPHA_KK_PHOTON: float = 2.0

#: Radion (scalar) universal coupling to matter (relative to gravity)
ALPHA_RADION: float = 2.0 / 3.0

#: Representative composition differences Δ(B/μ) for standard test material pairs
DELTA_B_MU: dict = {
    "Be-Ti":  0.0032,
    "Cu-Pb":  0.0010,
    "Al-Pt":  0.0034,
    "H-Rb":   0.0014,
    "Be-Al":  0.0010,
    "Pt-Ti":  0.0018,
}

#: Current Eöt-Wash upper bound on η (Schlamminger et al. 2008; Bergé et al. 2023)
EOT_WASH_ETA_BOUND: float = 2.0e-13

#: STE-QUEST satellite projected sensitivity on η
STE_QUEST_ETA_TARGET: float = 1.0e-15

#: Non-minimal coupling constant ξ (default: conformal value 1/6)
XI_CONFORMAL: float = 1.0 / 6.0

#: Gravitational binding energy fraction for laboratory bodies
EPSILON_GRAV_LAB: float = 1.0e-5   # ΔE_grav/m c² ≈ 10⁻⁵ for cm-scale bodies

#: Canonical braid parameters
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74
C_S_CANONICAL: float = 12.0 / 37.0


# ---------------------------------------------------------------------------
# eotvos_parameter_kk
# ---------------------------------------------------------------------------

def eotvos_parameter_kk(
    alpha: float,
    delta_b_over_mu: float,
    r: float,
    yukawa_lambda: float,
) -> float:
    """Eötvös parameter η from a KK Yukawa channel.

    For a Yukawa fifth force coupling to baryon number with strength α:

        η = α × |Δ(B/μ)| × e^{−r/λ}                               [3]

    Parameters
    ----------
    alpha           : float — coupling strength relative to gravity (> 0)
    delta_b_over_mu : float — |Δ(B/μ)| composition difference (≥ 0)
    r               : float — test-mass separation in Planck units (> 0)
    yukawa_lambda   : float — Yukawa range in Planck units (> 0)

    Returns
    -------
    eta : float ≥ 0

    Raises
    ------
    ValueError if alpha ≤ 0, delta_b_over_mu < 0, r ≤ 0, or yukawa_lambda ≤ 0.
    """
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    if delta_b_over_mu < 0.0:
        raise ValueError(f"delta_b_over_mu must be ≥ 0, got {delta_b_over_mu!r}")
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if yukawa_lambda <= 0.0:
        raise ValueError(f"yukawa_lambda must be > 0, got {yukawa_lambda!r}")
    return alpha * delta_b_over_mu * math.exp(-r / yukawa_lambda)


# ---------------------------------------------------------------------------
# eotvos_parameter_radion_nmc
# ---------------------------------------------------------------------------

def eotvos_parameter_radion_nmc(
    xi: float,
    delta_b_over_mu: float,
    epsilon_grav: float = EPSILON_GRAV_LAB,
) -> float:
    """Eötvös parameter from non-minimal coupling of the radion to curvature.

    The non-minimal coupling term ξ R φ² in the 5D action generates a
    composition-dependent acceleration at the level:

        η_φ^(NMC) ≈ |ξ| × α_φ × |Δ(B/μ)| × ε_grav

    where ε_grav is the fractional gravitational self-energy of the test bodies.

    This is non-zero even for a universal (baryon-number-independent) coupling
    because the curvature-coupling mixes internal structure with the radion vev.

    Parameters
    ----------
    xi              : float — non-minimal coupling constant (−∞ < ξ < ∞)
    delta_b_over_mu : float — |Δ(B/μ)| composition difference (≥ 0)
    epsilon_grav    : float — gravitational binding energy fraction (> 0,
                              default 10⁻⁵ for laboratory-scale bodies)

    Returns
    -------
    eta_nmc : float ≥ 0

    Raises
    ------
    ValueError if delta_b_over_mu < 0 or epsilon_grav ≤ 0.
    """
    if delta_b_over_mu < 0.0:
        raise ValueError(f"delta_b_over_mu must be ≥ 0, got {delta_b_over_mu!r}")
    if epsilon_grav <= 0.0:
        raise ValueError(f"epsilon_grav must be > 0, got {epsilon_grav!r}")
    return abs(xi) * ALPHA_RADION * delta_b_over_mu * epsilon_grav


# ---------------------------------------------------------------------------
# radion_fifth_force
# ---------------------------------------------------------------------------

def radion_fifth_force(
    M_source: float,
    r: float,
    m_phi: float,
    alpha: float = ALPHA_RADION,
) -> float:
    """Radial acceleration on a unit test mass from the radion fifth force.

    The radion-mediated force on a test mass m=1 at separation r from a
    source of mass M_source is:

        a_φ = α × G M_source / r² × e^{−r/λ_φ}      (Planck units: G = 1)
            = α × M_source / r² × e^{−r m_φ}

    Parameters
    ----------
    M_source : float — source mass in Planck units (> 0)
    r        : float — test-mass separation in Planck units (> 0)
    m_phi    : float — radion mass in Planck units (> 0)
    alpha    : float — coupling strength (default ALPHA_RADION = 2/3)

    Returns
    -------
    a_phi : float ≥ 0 — radial acceleration (Planck units, magnitude)

    Raises
    ------
    ValueError if M_source ≤ 0, r ≤ 0, or m_phi ≤ 0.
    """
    if M_source <= 0.0:
        raise ValueError(f"M_source must be > 0, got {M_source!r}")
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    return alpha * M_source / (r ** 2) * math.exp(-r * m_phi)


# ---------------------------------------------------------------------------
# composition_dependence_kk
# ---------------------------------------------------------------------------

def composition_dependence_kk(
    n1: int,
    n2: int,
    R: float,
    r: float,
    materials: Sequence[str] = ("Be-Ti", "Cu-Pb", "Al-Pt", "H-Rb"),
) -> dict:
    """Compute η for multiple material pairs from KK-photon Yukawa coupling.

    Parameters
    ----------
    n1        : int   — primary winding number (≥ 1)
    n2        : int   — secondary winding number (> n1)
    R         : float — compactification radius in Planck units (> 0)
    r         : float — test-mass separation in Planck units (> 0)
    materials : list[str] — material pair keys from DELTA_B_MU dict

    Returns
    -------
    dict mapping each material pair key to its η prediction.

    Raises
    ------
    ValueError if n1 < 1, n2 ≤ n1, R ≤ 0, or r ≤ 0.
    KeyError if a material pair key is not in DELTA_B_MU.
    """
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be ≥ 1.")
    if n2 <= n1:
        raise ValueError(f"n2={n2!r} must be > n1={n1!r}.")
    if R <= 0.0:
        raise ValueError(f"R must be > 0, got {R!r}")
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    lambda_A = R   # KK photon range = R
    results = {}
    for mat in materials:
        delta = DELTA_B_MU[mat]
        results[mat] = eotvos_parameter_kk(ALPHA_KK_PHOTON, delta, r, lambda_A)
    return results


# ---------------------------------------------------------------------------
# ep_violation_in_eot_wash_range
# ---------------------------------------------------------------------------

def ep_violation_in_eot_wash_range(m_phi: float, alpha: float) -> dict:
    """Check whether the radion fifth force is within Eöt-Wash sensitivity.

    Eöt-Wash tests at r ≈ 1 cm = 6.187 × 10²⁶ L_Pl.  The signal is:

        η ≈ alpha × Δ(B/μ) × exp(−r × m_phi)

    Using Δ(B/μ) = 0.0032 (Be-Ti) and the current bound η < 2 × 10⁻¹³.

    Parameters
    ----------
    m_phi : float — radion mass in Planck units (> 0)
    alpha : float — coupling strength (> 0)

    Returns
    -------
    dict with keys
        'm_phi'             — radion mass
        'alpha'             — coupling
        'lambda_phi_planck' — Yukawa range in Planck units
        'r_eot_wash_planck' — Eöt-Wash separation in Planck units
        'eta_predicted'     — predicted η at r = 1 cm
        'eta_bound'         — Eöt-Wash bound on η
        'detectable'        — True if eta_predicted > eta_bound
        'suppression'       — exp(−r × m_phi) (Yukawa suppression factor)

    Raises
    ------
    ValueError if m_phi ≤ 0 or alpha ≤ 0.
    """
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    # 1 cm in Planck units: 1e-2 m / 1.616e-35 m ≈ 6.19e32 L_Pl
    r_eot = 1.0e-2 / 1.616255e-35
    lambda_phi = 1.0 / m_phi
    delta_b_mu = DELTA_B_MU["Be-Ti"]
    suppression = math.exp(-r_eot / lambda_phi)
    eta = alpha * delta_b_mu * suppression
    return {
        "m_phi": m_phi,
        "alpha": alpha,
        "lambda_phi_planck": lambda_phi,
        "r_eot_wash_planck": r_eot,
        "eta_predicted": eta,
        "eta_bound": EOT_WASH_ETA_BOUND,
        "detectable": eta > EOT_WASH_ETA_BOUND,
        "suppression": suppression,
    }


# ---------------------------------------------------------------------------
# equivalence_principle_summary
# ---------------------------------------------------------------------------

def equivalence_principle_summary(
    m_phi: float,
    R: float,
    r: float,
    delta_b_over_mu: float = DELTA_B_MU["Be-Ti"],
) -> dict:
    """Full summary of EP predictions for both Yukawa channels.

    Parameters
    ----------
    m_phi           : float — radion mass in Planck units (> 0)
    R               : float — compactification radius in Planck units (> 0)
    r               : float — test-mass separation in Planck units (> 0)
    delta_b_over_mu : float — |Δ(B/μ)| composition difference (default Be-Ti)

    Returns
    -------
    dict with keys
        'eta_radion_channel'   — η from radion scalar channel (= 0, universal)
        'eta_kk_channel'       — η from KK-photon vector channel
        'eta_radion_nmc'       — η from non-minimal coupling (conformal ξ=1/6)
        'eta_total'            — dominant contribution (max of above)
        'eot_wash_bound'       — current Eöt-Wash bound
        'ste_quest_target'     — STE-QUEST projected sensitivity
        'currently_detectable' — True if eta_total > EOT_WASH_ETA_BOUND
        'ste_quest_detectable' — True if eta_total > STE_QUEST_ETA_TARGET
        'cylinder_condition'   — 'frozen: η_radion = 0' or 'dynamical: η ≠ 0'

    Raises
    ------
    ValueError if m_phi ≤ 0, R ≤ 0, r ≤ 0, or delta_b_over_mu < 0.
    """
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    if R <= 0.0:
        raise ValueError(f"R must be > 0, got {R!r}")
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if delta_b_over_mu < 0.0:
        raise ValueError(f"delta_b_over_mu must be ≥ 0, got {delta_b_over_mu!r}")

    lambda_phi = 1.0 / m_phi
    lambda_A   = R

    # Radion channel: universal coupling → η = 0 at leading order
    eta_radion = 0.0

    # KK-photon channel: couples to baryon number → composition-dependent
    eta_kk = eotvos_parameter_kk(ALPHA_KK_PHOTON, delta_b_over_mu, r, lambda_A)

    # Non-minimal coupling correction to radion channel
    eta_nmc = eotvos_parameter_radion_nmc(
        XI_CONFORMAL, delta_b_over_mu, EPSILON_GRAV_LAB
    )

    eta_total = max(abs(eta_radion), abs(eta_kk), abs(eta_nmc))

    return {
        "eta_radion_channel": eta_radion,
        "eta_kk_channel": eta_kk,
        "eta_radion_nmc": eta_nmc,
        "eta_total": eta_total,
        "eot_wash_bound": EOT_WASH_ETA_BOUND,
        "ste_quest_target": STE_QUEST_ETA_TARGET,
        "currently_detectable": eta_total > EOT_WASH_ETA_BOUND,
        "ste_quest_detectable": eta_total > STE_QUEST_ETA_TARGET,
        "cylinder_condition": (
            "frozen (cylinder condition): η_radion = 0 exactly"
            if eta_nmc < 1.0e-20 else
            "dynamical radion: η_NMC ≠ 0"
        ),
    }


# ---------------------------------------------------------------------------
# eotvos_cylinder_condition
# ---------------------------------------------------------------------------

def eotvos_cylinder_condition(
    phi: float,
    phi0: float,
    alpha: float,
    delta_b_over_mu: float,
    r: float,
    lambda_phi: float,
) -> float:
    """WEP violation as a function of radion displacement from the cylinder condition.

    When φ = φ₀ (cylinder condition), the radion is frozen and η = 0.
    When φ ≠ φ₀ the deviation δ_cyl = |φ − φ₀|/φ₀ sources an additional
    Yukawa with strength proportional to δ_cyl:

        η_cyl(φ) = α × |Δ(B/μ)| × δ_cyl(φ) × e^{−r/λ_φ}

    Parameters
    ----------
    phi             : float — current radion value (> 0)
    phi0            : float — GW vacuum value (> 0)
    alpha           : float — coupling strength (> 0)
    delta_b_over_mu : float — composition difference (≥ 0)
    r               : float — separation in Planck units (> 0)
    lambda_phi      : float — Yukawa range in Planck units (> 0)

    Returns
    -------
    eta_cyl : float ≥ 0

    Raises
    ------
    ValueError if phi ≤ 0, phi0 ≤ 0, alpha ≤ 0, delta_b_over_mu < 0,
                 r ≤ 0, or lambda_phi ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0, got {phi0!r}")
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    if delta_b_over_mu < 0.0:
        raise ValueError(f"delta_b_over_mu must be ≥ 0, got {delta_b_over_mu!r}")
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if lambda_phi <= 0.0:
        raise ValueError(f"lambda_phi must be > 0, got {lambda_phi!r}")
    delta_cyl = abs(phi - phi0) / phi0
    return alpha * delta_b_over_mu * delta_cyl * math.exp(-r / lambda_phi)


# ---------------------------------------------------------------------------
# wep_constraint_on_radion_mass
# ---------------------------------------------------------------------------

def wep_constraint_on_radion_mass(
    alpha: float,
    delta_b_over_mu: float,
    r: float,
    eta_bound: float = EOT_WASH_ETA_BOUND,
) -> float:
    """Minimum radion mass from WEP constraints.

    The WEP bound η < η_bound with signal η ≈ α |Δ(B/μ)| exp(−r/λ) gives:

        exp(−r/λ) < η_bound / (α |Δ(B/μ)|)
        −r/λ < ln(η_bound / (α |Δ(B/μ)|))
        λ < −r / ln(η_bound / (α |Δ(B/μ)|))
        m_φ > −ln(η_bound / (α |Δ(B/μ)|)) / r

    This is the minimum radion mass required for the fifth force to be
    undetectable at the given separation r.

    Parameters
    ----------
    alpha           : float — coupling strength (> 0)
    delta_b_over_mu : float — composition difference (> 0)
    r               : float — test-mass separation in Planck units (> 0)
    eta_bound       : float — WEP bound on η (default Eöt-Wash 2 × 10⁻¹³)

    Returns
    -------
    m_phi_min : float — minimum radion mass (Planck units, > 0)
                        Returns 0 if no constraint (eta_bound ≥ alpha × Δ(B/μ))

    Raises
    ------
    ValueError if alpha ≤ 0, delta_b_over_mu ≤ 0, r ≤ 0, or eta_bound ≤ 0.
    """
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    if delta_b_over_mu <= 0.0:
        raise ValueError(f"delta_b_over_mu must be > 0, got {delta_b_over_mu!r}")
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if eta_bound <= 0.0:
        raise ValueError(f"eta_bound must be > 0, got {eta_bound!r}")
    ratio = eta_bound / (alpha * delta_b_over_mu)
    if ratio >= 1.0:
        # Bound is already satisfied for any mass
        return 0.0
    # ln(ratio) < 0, so m_min = -ln(ratio) / r > 0
    return -math.log(ratio) / r
