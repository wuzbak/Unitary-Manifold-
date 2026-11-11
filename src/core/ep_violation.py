# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/ep_violation.py
=========================
Pillar 37 — Equivalence Principle Violation from the Non-Frozen KK Radion.

The historical functions in this module are compatibility models, not
action-derived WEP exclusions. Their exponential-only force factors omit
the radial derivative factor (1+r/λ), and their couplings, source geometry,
and nonminimal-composition term are not established by the reduced action.
Neither vanishing vacuum displacement nor the cylinder condition rules out
a matter-sourced fifth force. See docs/physics/RADION_FIFTH_FORCE_AUDIT.md.

The physical Eotvos parameter is 2|a1-a2|/(|a1|+|a2|). A common
acceleration does not imply a differential WEP signal. For a conditional
homogeneous-sphere scalar model see
``isl_yukawa.homogeneous_sphere_eotvos_parameter``.

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
    """Legacy exponential-only acceleration proxy, not the Yukawa force.

    The historical expression for a unit test mass is:

        a_φ = α × G M_source / r² × e^{−r/λ_φ}      (Planck units: G = 1)
            = α × M_source / r² × e^{−r m_φ}

    The gradient of the corresponding potential also contains (1 + r*m_phi);
    this function retains its original behavior for compatibility.

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
    """Calculate a legacy exponential proxy, not an experimental verdict.

        η ≈ alpha × Δ(B/μ) × exp(−r × m_phi)

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
        'eta_proxy'         — legacy exponential proxy at assumed r = 1 cm
        'detectable'        — None; no validated verdict
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
        "status": "UNVALIDATED LEGACY PROXY; NO EXPERIMENTAL VERDICT",
        "eta_proxy": eta,
        "eta_predicted": None,
        "eta_bound_proxy": EOT_WASH_ETA_BOUND,
        "eta_bound": None,
        "detectable": None,
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
    """Legacy EP proxies; no validated physical or detectability verdict.

    Parameters
    ----------
    m_phi           : float — radion mass in Planck units (> 0)
    R               : float — compactification radius in Planck units (> 0)
    r               : float — test-mass separation in Planck units (> 0)
    delta_b_over_mu : float — |Δ(B/μ)| composition difference (default Be-Ti)

    Returns
    -------
    dict with keys
        'eta_*_proxy'          — assumed historical channel values
        'eta_total_proxy'      — maximum of proxy magnitudes, not a sum
        'eot_wash_bound_proxy' — historical assumed comparison value
        'ste_quest_target_proxy' — historical assumed target
        'currently_detectable' — None; not determined
        'ste_quest_detectable' — None; not determined
        'cylinder_condition'   — not determined by these inputs

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
        "status": "UNVALIDATED LEGACY PROXIES; NO EXPERIMENTAL VERDICT",
        "eta_radion_channel_proxy": eta_radion,
        "eta_kk_channel_proxy": eta_kk,
        "eta_radion_nmc_proxy": eta_nmc,
        "eta_total_proxy": eta_total,
        "eot_wash_bound_proxy": EOT_WASH_ETA_BOUND,
        "ste_quest_target_proxy": STE_QUEST_ETA_TARGET,
        "eta_radion_channel": None,
        "eta_kk_channel": None,
        "eta_radion_nmc": None,
        "eta_total": None,
        "eot_wash_bound": None,
        "ste_quest_target": None,
        "currently_detectable": None,
        "ste_quest_detectable": None,
        "cylinder_condition": "not determined by these inputs",
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
    """Historical displacement proxy, not a WEP or cylinder-condition test.

    It assumes, without a matter-action derivation, a signal proportional to
    displacement and an exponential-only force factor:

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
    """Return a mass threshold for the historical exponential-only proxy.

    The WEP bound η < η_bound with signal η ≈ α |Δ(B/μ)| exp(−r/λ) gives:

        exp(−r/λ) < η_bound / (α |Δ(B/μ)|)
        −r/λ < ln(η_bound / (α |Δ(B/μ)|))
        λ < −r / ln(η_bound / (α |Δ(B/μ)|))
        m_φ > −ln(η_bound / (α |Δ(B/μ)|)) / r

    This is not a physical WEP mass constraint or detectability analysis.

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
