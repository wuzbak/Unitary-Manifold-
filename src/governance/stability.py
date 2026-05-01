# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/governance/stability.py
============================
Stable Governance as a Lyapunov-Stable FTUM Fixed Point — Pillar 19c.

Theory
------
A government is stable if small perturbations — policy errors, elections,
economic shocks — are corrected by the system's own φ-restoring forces:
checks and balances, judicial review, free press, and civil society.

In FTUM language, define the Lyapunov function:

    V = (φ_actual − φ_optimal)²

Stability requires dV/dt < 0, i.e., deviations from the optimal governance
φ are damped rather than amplified.  A well-designed institutional framework
ensures that the restoring force

    F_restore = −dV/dφ = −2(φ_actual − φ_optimal)

is always active, pulling the system back toward the fixed point after each
perturbation.

What makes a good governance system
-------------------------------------
Separation of powers
    Distributes φ across three independent basins (executive, legislative,
    judicial) that mutually error-correct.  If one basin is perturbed, the
    other two exert a restoring force.

Independent judiciary
    Provides B_μ-insulated φ-measurement of law: judicial decisions are not
    contaminated by the political noise field of the moment.

Civil society and free press
    Distributed φ sensors that provide early-warning signals of deviations
    from the governance fixed point.  The more sensors, the lower the
    detection threshold for backsliding.

Term limits and rotation
    Prevents the single-fixed-point collapse that would arise if the same
    actor controlled the governance attractor indefinitely.

Rule of law
    φ applies equally regardless of identity: symmetry in φ-space.  When the
    powerful can escape consequences, the φ-field becomes anisotropic and the
    fixed point shifts.

Economic pluralism
    Prevents φ-concentration in the economic sphere from spilling over into
    political φ-capture, which would destabilise the social contract.

International cooperation
    φ-coupling across borders creates a shared stability basin: mutual
    interest in the other's stability raises the energy cost of defection.

Failure modes
-------------
1. Democratic backsliding: slow erosion of institutional φ, often below the
   detection threshold of any single sensor until the system is near the
   authoritarian attractor.

2. Coup / sudden state capture: discontinuous φ-jump that relocates the
   governance attractor to a new basin from which the Lyapunov restoring
   force may not be sufficient to recover.

3. Constitutional hardening: inability to update φ-rules as conditions change
   → brittleness; the system becomes a rigid fixed point that fractures rather
   than flexes under perturbation.

4. Partisan capture of judiciary: corrupts the B_μ-insulated error-correction
   mechanism, removing a key restoring force from the Lyapunov system.

5. Media capture: loss of the distributed φ sensor network, eliminating
   early-warning capability and allowing small deviations to compound
   undetected.

Actionable best practices
--------------------------
- Constitutional design with strong countermajoritarian protections:
  high-threshold amendment procedures ensure the rule-set is not casually
  altered by transient majorities.
- Independent electoral commissions: remove B_μ partisan noise from the
  φ-measurement of elections.
- Robust civil society funding and protection: maintain the density of
  distributed φ sensors.
- Anti-monopoly media ownership laws: prevent single-actor media capture.
- Graduated early-warning indicators (V-Dem index analog): detect the onset
  of backsliding before the system crosses the bifurcation point.

Public API
----------
lyapunov_stability(phi_actual, phi_optimal) -> float
    V = (phi_actual - phi_optimal)**2.

checks_balance_score(executive_phi, legislative_phi, judicial_phi) -> float
    CBS = 1 - std([e, l, j]) / (mean([e, l, j]) + 1e-30),  clipped [0, 1].

democratic_backsliding_rate(phi_t0, phi_t1, dt) -> float
    rate = (phi_t0 - phi_t1) / (dt + 1e-30)  positive = backsliding.

institutional_resilience(n_veto_players, phi_civil_society) -> float
    resilience = n_veto_players * phi_civil_society.

rule_of_law_index(phi_application_variance, phi_mean) -> float
    RLI = 1 - phi_application_variance / (phi_mean**2 + 1e-30).

term_limit_benefit(phi_incumbency_advantage, n_terms_without_limit) -> float
    benefit = phi_incumbency_advantage * n_terms_without_limit.

coup_risk(phi_military_autonomy, phi_civilian_oversight) -> float
    risk = phi_military_autonomy / (phi_civilian_oversight + 1e-30),
    clipped [0, 1].

economic_pluralism_index(phi_values) -> float
    EPI = 1 - std(phi_values) / (mean(phi_values) + 1e-30),  clipped [0, 1].

international_cooperation_phi(bilateral_agreements, phi_per_agreement) -> float
    phi_int = bilateral_agreements * phi_per_agreement.

governance_quality_score(rule_of_law, checks_balance, civil_society_phi,
                          press_freedom, electoral_integrity) -> float
    score = (rule_of_law + checks_balance + civil_society_phi
             + press_freedom + electoral_integrity) / 5.
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

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Lyapunov stability
# ---------------------------------------------------------------------------

def lyapunov_stability(
    phi_actual: float,
    phi_optimal: float,
) -> float:
    """Lyapunov function value V = (φ_actual − φ_optimal)².

    A governance system is Lyapunov-stable when V is close to zero and dV/dt
    is negative.  V = 0 means perfect attainment of the governance optimum;
    V > 0 quantifies the squared deviation from it.

    Parameters
    ----------
    phi_actual  : float — current governance φ.
    phi_optimal : float — target governance φ at the fixed point.

    Returns
    -------
    V : float — Lyapunov function value (≥ 0).
    """
    return float((phi_actual - phi_optimal) ** 2)


# ---------------------------------------------------------------------------
# Checks and balances
# ---------------------------------------------------------------------------

def checks_balance_score(
    executive_phi: float,
    legislative_phi: float,
    judicial_phi: float,
) -> float:
    """Balance of φ across the three branches of government.

    A perfectly balanced system has equal φ in each branch.  Concentration of
    φ in one branch increases the standard deviation and lowers the score.

        CBS = 1 − std([e, l, j]) / (mean([e, l, j]) + ε),  clipped to [0, 1]

    Parameters
    ----------
    executive_phi   : float — executive branch φ (≥ 0).
    legislative_phi : float — legislative branch φ (≥ 0).
    judicial_phi    : float — judicial branch φ (≥ 0).

    Returns
    -------
    CBS : float — checks-and-balance score ∈ [0, 1].

    Raises
    ------
    ValueError
        If any branch φ is negative.
    """
    for name, val in [
        ("executive_phi", executive_phi),
        ("legislative_phi", legislative_phi),
        ("judicial_phi", judicial_phi),
    ]:
        if val < 0.0:
            raise ValueError(f"{name} must be >= 0, got {val!r}")
    arr = np.array([executive_phi, legislative_phi, judicial_phi], dtype=float)
    raw = 1.0 - np.std(arr) / (np.mean(arr) + _NUMERICAL_EPSILON)
    return float(np.clip(raw, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Democratic backsliding and institutional resilience
# ---------------------------------------------------------------------------

def democratic_backsliding_rate(
    phi_t0: float,
    phi_t1: float,
    dt: float,
) -> float:
    """Rate of democratic backsliding (positive = worsening).

    A positive rate indicates the governance φ has declined from time 0 to
    time 1, i.e., democratic quality has eroded:

        rate = (φ_t0 − φ_t1) / (Δt + ε)

    Parameters
    ----------
    phi_t0 : float — governance φ at the earlier time.
    phi_t1 : float — governance φ at the later time.
    dt     : float — elapsed time (≥ 0).

    Returns
    -------
    rate : float — backsliding rate (positive = backsliding).

    Raises
    ------
    ValueError
        If dt is negative.
    """
    if dt < 0.0:
        raise ValueError(f"dt must be >= 0, got {dt!r}")
    return float((phi_t0 - phi_t1) / (dt + _NUMERICAL_EPSILON))


def institutional_resilience(
    n_veto_players: float,
    phi_civil_society: float,
) -> float:
    """Resilience of a governance system to shocks.

    Veto players are institutional actors with the power to block unilateral
    change (courts, opposition parties, upper chambers, independent agencies).
    Civil society provides a distributed sensing and resistance capacity.
    Together they multiply resilience:

        resilience = n_veto_players × φ_civil_society

    Parameters
    ----------
    n_veto_players     : float — number of effective veto players (≥ 0).
    phi_civil_society  : float — civil society φ (≥ 0).

    Returns
    -------
    resilience : float — institutional resilience score (≥ 0).

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if n_veto_players < 0.0:
        raise ValueError(f"n_veto_players must be >= 0, got {n_veto_players!r}")
    if phi_civil_society < 0.0:
        raise ValueError(f"phi_civil_society must be >= 0, got {phi_civil_society!r}")
    return float(n_veto_players * phi_civil_society)


# ---------------------------------------------------------------------------
# Rule of law, term limits, and coup risk
# ---------------------------------------------------------------------------

def rule_of_law_index(
    phi_application_variance: float,
    phi_mean: float,
) -> float:
    """Rule-of-law index based on consistency of φ application.

    The rule of law requires that φ (enforcement, rights, penalties) is
    applied consistently regardless of identity.  Variance in application
    signals discriminatory or arbitrary enforcement.

        RLI = 1 − φ_variance / (φ_mean² + ε)

    A perfect rule of law (zero variance) gives RLI = 1; high variance
    gives RLI < 1 or even negative, indicating systemic inequality.

    Parameters
    ----------
    phi_application_variance : float — variance in φ application (≥ 0).
    phi_mean                 : float — mean φ applied across cases (≥ 0).

    Returns
    -------
    RLI : float — rule-of-law index.

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if phi_application_variance < 0.0:
        raise ValueError(
            f"phi_application_variance must be >= 0, got {phi_application_variance!r}"
        )
    if phi_mean < 0.0:
        raise ValueError(f"phi_mean must be >= 0, got {phi_mean!r}")
    return float(
        1.0 - phi_application_variance / (phi_mean ** 2 + _NUMERICAL_EPSILON)
    )


def term_limit_benefit(
    phi_incumbency_advantage: float,
    n_terms_without_limit: float,
) -> float:
    """φ benefit recovered by imposing term limits.

    Without term limits an incumbent accumulates a φ-incumbency advantage that
    crowds out challenger φ and narrows the democratic attractor basin.  The
    accumulated distortion grows with each term:

        benefit = φ_incumbency_advantage × n_terms_without_limit

    Parameters
    ----------
    phi_incumbency_advantage : float — per-term incumbency φ advantage (≥ 0).
    n_terms_without_limit    : float — number of terms served (≥ 0).

    Returns
    -------
    benefit : float — total φ distortion removed by term limits (≥ 0).

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if phi_incumbency_advantage < 0.0:
        raise ValueError(
            f"phi_incumbency_advantage must be >= 0, got {phi_incumbency_advantage!r}"
        )
    if n_terms_without_limit < 0.0:
        raise ValueError(
            f"n_terms_without_limit must be >= 0, got {n_terms_without_limit!r}"
        )
    return float(phi_incumbency_advantage * n_terms_without_limit)


def coup_risk(
    phi_military_autonomy: float,
    phi_civilian_oversight: float,
) -> float:
    """Risk of a military coup, clipped to [0, 1].

    When military φ-autonomy is high relative to civilian oversight φ, the
    probability of a coup (sudden authoritarian attractor jump) rises:

        risk = φ_military_autonomy / (φ_civilian_oversight + ε),  clipped [0, 1]

    Parameters
    ----------
    phi_military_autonomy  : float — military φ-autonomy (≥ 0).
    phi_civilian_oversight : float — civilian oversight φ (≥ 0).

    Returns
    -------
    risk : float — coup risk ∈ [0, 1].

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if phi_military_autonomy < 0.0:
        raise ValueError(
            f"phi_military_autonomy must be >= 0, got {phi_military_autonomy!r}"
        )
    if phi_civilian_oversight < 0.0:
        raise ValueError(
            f"phi_civilian_oversight must be >= 0, got {phi_civilian_oversight!r}"
        )
    raw = phi_military_autonomy / (phi_civilian_oversight + _NUMERICAL_EPSILON)
    return float(np.clip(raw, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Economic pluralism and international cooperation
# ---------------------------------------------------------------------------

def economic_pluralism_index(
    phi_values: np.ndarray | list[float],
) -> float:
    """Herfindahl-analog index of economic φ pluralism, clipped to [0, 1].

    Economic concentration reduces governance stability by enabling φ-rich
    actors to capture political institutions.  The index:

        EPI = 1 − std(φ) / (mean(φ) + ε),  clipped to [0, 1]

    EPI = 1 means a perfectly equal distribution (maximum pluralism);
    EPI → 0 means extreme concentration.

    Parameters
    ----------
    phi_values : array-like — φ values across economic actors (non-empty).

    Returns
    -------
    EPI : float — economic pluralism index ∈ [0, 1].

    Raises
    ------
    ValueError
        If phi_values is empty.
    """
    arr = np.asarray(phi_values, dtype=float)
    if arr.size == 0:
        raise ValueError("phi_values must be non-empty.")
    raw = 1.0 - np.std(arr) / (np.mean(arr) + _NUMERICAL_EPSILON)
    return float(np.clip(raw, 0.0, 1.0))


def international_cooperation_phi(
    bilateral_agreements: float,
    phi_per_agreement: float,
) -> float:
    """Total φ contributed to stability by international cooperation.

    Each bilateral or multilateral agreement couples the φ-fields of the
    participating states, raising the energy cost of defection and expanding
    the shared stability basin:

        φ_int = bilateral_agreements × φ_per_agreement

    Parameters
    ----------
    bilateral_agreements : float — number of active agreements (≥ 0).
    phi_per_agreement    : float — φ contributed per agreement (≥ 0).

    Returns
    -------
    phi_int : float — total international cooperation φ (≥ 0).

    Raises
    ------
    ValueError
        If either argument is negative.
    """
    if bilateral_agreements < 0.0:
        raise ValueError(
            f"bilateral_agreements must be >= 0, got {bilateral_agreements!r}"
        )
    if phi_per_agreement < 0.0:
        raise ValueError(f"phi_per_agreement must be >= 0, got {phi_per_agreement!r}")
    return float(bilateral_agreements * phi_per_agreement)


# ---------------------------------------------------------------------------
# Composite governance quality
# ---------------------------------------------------------------------------

def governance_quality_score(
    rule_of_law: float,
    checks_balance: float,
    civil_society_phi: float,
    press_freedom: float,
    electoral_integrity: float,
) -> float:
    """Composite governance quality score.

    Averages five key φ-dimensions of governance quality:

        score = (rule_of_law + checks_balance + civil_society_phi
                 + press_freedom + electoral_integrity) / 5

    Each component should be normalised to [0, 1] before calling this
    function for the aggregate to be interpretable on a [0, 1] scale.

    Parameters
    ----------
    rule_of_law         : float — rule-of-law φ component.
    checks_balance      : float — checks-and-balance φ component.
    civil_society_phi   : float — civil society φ component.
    press_freedom       : float — press-freedom φ component.
    electoral_integrity : float — electoral integrity φ component.

    Returns
    -------
    score : float — composite governance quality score.
    """
    return float(
        (rule_of_law + checks_balance + civil_society_phi
         + press_freedom + electoral_integrity) / 5.0
    )
