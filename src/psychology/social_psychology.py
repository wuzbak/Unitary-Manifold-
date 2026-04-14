# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/psychology/social_psychology.py
=====================================
Social Psychology as φ-Field Group Dynamics — Pillar 24.
"""

from __future__ import annotations
import math
import numpy as np

_EPS = 1e-30


def group_phi_cohesion(phi_values: np.ndarray) -> float:
    """Group cohesion as inverse variance in member φ values.

    cohesion = mean(φ) / (std(φ) + ε)

    Parameters
    ----------
    phi_values : ndarray — φ values of group members (non-empty)

    Returns
    -------
    cohesion : float
    """
    arr = np.asarray(phi_values, dtype=float)
    if arr.size == 0:
        raise ValueError("phi_values must not be empty")
    return float(np.mean(arr) / (np.std(arr) + _EPS))


def social_phi_influence(phi_source: float, n_ties: int,
                          decay: float = 0.5) -> float:
    """Social influence φ decaying with network distance.

    influence = phi_source × decay^n_ties

    Parameters
    ----------
    phi_source : float — source agent's φ (must be ≥ 0)
    n_ties     : int   — number of social ties (hops) from source (must be ≥ 0)
    decay      : float — decay per hop ∈ (0, 1] (default 0.5)

    Returns
    -------
    influence : float
    """
    if phi_source < 0.0:
        raise ValueError(f"phi_source must be ≥ 0, got {phi_source!r}")
    if n_ties < 0:
        raise ValueError(f"n_ties must be ≥ 0, got {n_ties!r}")
    if not (0.0 < decay <= 1.0):
        raise ValueError(f"decay must be in (0,1], got {decay!r}")
    return float(phi_source * decay ** n_ties)


def prejudice_phi(phi_outgroup: float, phi_ingroup: float) -> float:
    """Prejudice as systematic undervaluation of outgroup φ.

    prejudice = (phi_ingroup − phi_outgroup) / (phi_ingroup + ε)

    Parameters
    ----------
    phi_outgroup : float — ascribed φ to outgroup (must be ≥ 0)
    phi_ingroup  : float — ascribed φ to ingroup (must be ≥ 0)

    Returns
    -------
    prejudice : float ∈ [0, 1) (higher = more biased)
    """
    if phi_outgroup < 0.0:
        raise ValueError(f"phi_outgroup must be ≥ 0, got {phi_outgroup!r}")
    if phi_ingroup < 0.0:
        raise ValueError(f"phi_ingroup must be ≥ 0, got {phi_ingroup!r}")
    return float(np.clip((phi_ingroup - phi_outgroup) / (phi_ingroup + _EPS), 0.0, 1.0))


def conformity_phi_pressure(phi_individual: float, phi_majority: float,
                             n_majority: int) -> float:
    """Asch-effect conformity pressure on an individual.

    pressure = n_majority × |phi_majority − phi_individual| / (phi_individual + ε)

    Parameters
    ----------
    phi_individual : float — individual's φ position (must be ≥ 0)
    phi_majority   : float — majority group's φ position
    n_majority     : int   — majority size (must be ≥ 0)

    Returns
    -------
    pressure : float ≥ 0
    """
    if phi_individual < 0.0:
        raise ValueError(f"phi_individual must be ≥ 0, got {phi_individual!r}")
    if n_majority < 0:
        raise ValueError(f"n_majority must be ≥ 0, got {n_majority!r}")
    return float(n_majority * abs(phi_majority - phi_individual) / (phi_individual + _EPS))


def leadership_phi(phi_vision: float, phi_communication: float,
                    phi_execution: float) -> float:
    """Leadership effectiveness as combined φ of three core dimensions.

    leadership = phi_vision × phi_communication × phi_execution  (geometric mean)

    Parameters
    ----------
    phi_vision        : float — visionary φ capacity (must be ≥ 0)
    phi_communication : float — communication φ capacity (must be ≥ 0)
    phi_execution     : float — execution φ capacity (must be ≥ 0)

    Returns
    -------
    leadership : float ≥ 0
    """
    for name, v in [("phi_vision", phi_vision), ("phi_communication", phi_communication),
                    ("phi_execution", phi_execution)]:
        if v < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {v!r}")
    return float((phi_vision * phi_communication * phi_execution) ** (1.0 / 3.0))


def trust_phi_network(phi_direct: float, phi_indirect: float,
                       reputation_weight: float = 0.3) -> float:
    """Network trust combining direct and indirect (reputation) φ.

    trust = (1 − w) × phi_direct + w × phi_indirect

    Parameters
    ----------
    phi_direct        : float — direct experience trust φ
    phi_indirect      : float — reputation-based trust φ
    reputation_weight : float — weight on indirect trust ∈ [0, 1] (default 0.3)

    Returns
    -------
    trust : float
    """
    if not (0.0 <= reputation_weight <= 1.0):
        raise ValueError(f"reputation_weight must be in [0,1], got {reputation_weight!r}")
    return float((1.0 - reputation_weight) * phi_direct + reputation_weight * phi_indirect)


def crowd_phi_dynamics(phi_individual: float, n_crowd: int,
                        amplification: float = 1.5) -> float:
    """Crowd φ-amplification of individual behaviour.

    phi_crowd = phi_individual × amplification × sqrt(n_crowd)

    Parameters
    ----------
    phi_individual : float — individual baseline φ (must be ≥ 0)
    n_crowd        : int   — crowd size (must be ≥ 1)
    amplification  : float — social facilitation factor (must be > 0)

    Returns
    -------
    phi_crowd : float
    """
    if phi_individual < 0.0:
        raise ValueError(f"phi_individual must be ≥ 0, got {phi_individual!r}")
    if n_crowd < 1:
        raise ValueError(f"n_crowd must be ≥ 1, got {n_crowd!r}")
    if amplification <= 0.0:
        raise ValueError(f"amplification must be > 0, got {amplification!r}")
    return float(phi_individual * amplification * math.sqrt(n_crowd))


def social_identity_phi(phi_ingroup: float, phi_personal: float,
                         identity_salience: float = 0.5) -> float:
    """Weighted social vs. personal identity φ.

    phi_id = identity_salience × phi_ingroup + (1 − identity_salience) × phi_personal

    Parameters
    ----------
    phi_ingroup        : float — ingroup identity φ
    phi_personal       : float — personal identity φ
    identity_salience  : float — social identity salience ∈ [0, 1] (default 0.5)

    Returns
    -------
    phi_id : float
    """
    if not (0.0 <= identity_salience <= 1.0):
        raise ValueError(f"identity_salience must be in [0,1], got {identity_salience!r}")
    return float(identity_salience * phi_ingroup + (1.0 - identity_salience) * phi_personal)


def cooperation_phi(phi_mutual_gain: float, phi_defection_gain: float,
                     probability_cooperate: float) -> float:
    """Expected φ from a mixed-strategy cooperation game.

    EV = prob_cooperate × phi_mutual_gain + (1 − prob_cooperate) × phi_defection_gain

    Parameters
    ----------
    phi_mutual_gain      : float — φ gain from mutual cooperation
    phi_defection_gain   : float — φ gain from defection when other cooperates
    probability_cooperate: float — probability of cooperation ∈ [0, 1]

    Returns
    -------
    EV : float
    """
    if not (0.0 <= probability_cooperate <= 1.0):
        raise ValueError(f"probability_cooperate must be in [0,1], got {probability_cooperate!r}")
    return float(probability_cooperate * phi_mutual_gain +
                 (1.0 - probability_cooperate) * phi_defection_gain)


def social_phi_entropy(phi_distribution: np.ndarray) -> float:
    """Shannon entropy of social φ distribution across a population.

    H = −Σ p_i ln(p_i)

    Parameters
    ----------
    phi_distribution : ndarray — φ values across population (must be ≥ 0)

    Returns
    -------
    H : float ≥ 0
    """
    arr = np.asarray(phi_distribution, dtype=float)
    if np.any(arr < 0.0):
        raise ValueError("phi_distribution must be ≥ 0")
    total = arr.sum() + _EPS
    p = arr / total
    return float(-np.sum(p * np.log(p + _EPS)))
