# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/psychology/behavior.py
===========================
Behavior as φ-Field Driven Action Selection — Pillar 24.
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
import numpy as np

_EPS = 1e-30


def motivation_phi_drive(phi_need: float, phi_satiation: float) -> float:
    """Motivational drive as unsatisfied φ-need.

    drive = max(0, phi_need − phi_satiation)

    Parameters
    ----------
    phi_need      : float — φ required to satisfy need (must be ≥ 0)
    phi_satiation : float — φ already acquired (must be ≥ 0)

    Returns
    -------
    drive : float ≥ 0
    """
    if phi_need < 0.0:
        raise ValueError(f"phi_need must be ≥ 0, got {phi_need!r}")
    if phi_satiation < 0.0:
        raise ValueError(f"phi_satiation must be ≥ 0, got {phi_satiation!r}")
    return float(max(0.0, phi_need - phi_satiation))


def reward_phi_signal(phi_obtained: float, phi_expected: float) -> float:
    """Dopaminergic reward prediction error.

    RPE = phi_obtained − phi_expected

    Parameters
    ----------
    phi_obtained : float — φ obtained from action outcome
    phi_expected : float — φ predicted by prior model

    Returns
    -------
    RPE : float (positive = better than expected)
    """
    return float(phi_obtained - phi_expected)


def habit_phi_formation(phi_action: float, n_repetitions: int,
                         tau_habit: float = 30.0) -> float:
    """Habit strength as accumulated φ over repeated actions.

    strength = phi_action × (1 − exp(−n_repetitions / tau_habit))

    Parameters
    ----------
    phi_action    : float — φ reinforcement per repetition (must be ≥ 0)
    n_repetitions : int   — number of repetitions (must be ≥ 0)
    tau_habit     : float — repetitions to reach habit asymptote (default 30, must be > 0)

    Returns
    -------
    strength : float ∈ [0, phi_action]
    """
    if phi_action < 0.0:
        raise ValueError(f"phi_action must be ≥ 0, got {phi_action!r}")
    if n_repetitions < 0:
        raise ValueError(f"n_repetitions must be ≥ 0, got {n_repetitions!r}")
    if tau_habit <= 0.0:
        raise ValueError(f"tau_habit must be > 0, got {tau_habit!r}")
    return float(phi_action * (1.0 - math.exp(-n_repetitions / tau_habit)))


def decision_phi_threshold(phi_evidence: float, phi_threshold: float,
                            B_noise: float) -> bool:
    """Whether accumulated evidence φ exceeds decision threshold.

    decide = phi_evidence ≥ phi_threshold + B_noise × z_criterion

    Parameters
    ----------
    phi_evidence  : float — accumulated evidence φ
    phi_threshold : float — decision criterion φ
    B_noise       : float — noise floor (must be ≥ 0)

    Returns
    -------
    decide : bool — True if evidence exceeds threshold
    """
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return bool(phi_evidence >= phi_threshold + B_noise)


def risk_phi_tolerance(phi_certain: float, phi_gamble: float,
                        prob_win: float) -> float:
    """Expected value difference between gamble and certain option.

    EV_diff = prob_win × phi_gamble − phi_certain

    Positive → prefer gamble (risk-seeking); negative → prefer certain (risk-averse).

    Parameters
    ----------
    phi_certain : float — φ value of certain option (must be ≥ 0)
    phi_gamble  : float — φ value of winning gamble (must be ≥ 0)
    prob_win    : float — probability of winning ∈ [0, 1]

    Returns
    -------
    EV_diff : float
    """
    if phi_certain < 0.0:
        raise ValueError(f"phi_certain must be ≥ 0, got {phi_certain!r}")
    if phi_gamble < 0.0:
        raise ValueError(f"phi_gamble must be ≥ 0, got {phi_gamble!r}")
    if not (0.0 <= prob_win <= 1.0):
        raise ValueError(f"prob_win must be in [0,1], got {prob_win!r}")
    return float(prob_win * phi_gamble - phi_certain)


def altruism_phi(phi_cost_self: float, phi_benefit_other: float,
                  kin_coefficient: float = 0.5) -> float:
    """Hamilton's rule: altruism is favoured when r × B > C.

    net_phi = kin_coefficient × phi_benefit_other − phi_cost_self

    Parameters
    ----------
    phi_cost_self       : float — φ cost to actor (must be ≥ 0)
    phi_benefit_other   : float — φ benefit to recipient (must be ≥ 0)
    kin_coefficient     : float — genetic relatedness ∈ [0, 1] (default 0.5)

    Returns
    -------
    net_phi : float (positive → altruism favoured)
    """
    if phi_cost_self < 0.0:
        raise ValueError(f"phi_cost_self must be ≥ 0, got {phi_cost_self!r}")
    if phi_benefit_other < 0.0:
        raise ValueError(f"phi_benefit_other must be ≥ 0, got {phi_benefit_other!r}")
    if not (0.0 <= kin_coefficient <= 1.0):
        raise ValueError(f"kin_coefficient must be in [0,1], got {kin_coefficient!r}")
    return float(kin_coefficient * phi_benefit_other - phi_cost_self)


def aggression_phi_trigger(phi_frustration: float, phi_inhibition: float,
                            B_noise: float) -> float:
    """Aggression likelihood as frustration minus inhibition, noise-adjusted.

    aggression = max(0, (phi_frustration − phi_inhibition) / (B_noise + ε))

    Parameters
    ----------
    phi_frustration : float — accumulated frustration φ (must be ≥ 0)
    phi_inhibition  : float — self-regulatory inhibition φ (must be ≥ 0)
    B_noise         : float — contextual noise (must be ≥ 0)

    Returns
    -------
    aggression : float ≥ 0
    """
    if phi_frustration < 0.0:
        raise ValueError(f"phi_frustration must be ≥ 0, got {phi_frustration!r}")
    if phi_inhibition < 0.0:
        raise ValueError(f"phi_inhibition must be ≥ 0, got {phi_inhibition!r}")
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(max(0.0, (phi_frustration - phi_inhibition) / (B_noise + _EPS)))


def emotional_phi_regulation(phi_arousal: float, regulation_efficacy: float) -> float:
    """Residual emotional arousal φ after regulation.

    phi_regulated = phi_arousal × (1 − regulation_efficacy)

    Parameters
    ----------
    phi_arousal         : float — initial emotional arousal φ (must be ≥ 0)
    regulation_efficacy : float — regulation success ∈ [0, 1]

    Returns
    -------
    phi_regulated : float ≥ 0
    """
    if phi_arousal < 0.0:
        raise ValueError(f"phi_arousal must be ≥ 0, got {phi_arousal!r}")
    if not (0.0 <= regulation_efficacy <= 1.0):
        raise ValueError(f"regulation_efficacy must be in [0,1], got {regulation_efficacy!r}")
    return float(phi_arousal * (1.0 - regulation_efficacy))


def behavioral_phi_flexibility(n_strategies: int, phi_per_strategy: float) -> float:
    """Behavioural repertoire φ as total available strategy space.

    phi_flex = n_strategies × phi_per_strategy

    Parameters
    ----------
    n_strategies    : int   — number of available strategies (must be ≥ 0)
    phi_per_strategy: float — φ value per strategy (must be ≥ 0)

    Returns
    -------
    phi_flex : float
    """
    if n_strategies < 0:
        raise ValueError(f"n_strategies must be ≥ 0, got {n_strategies!r}")
    if phi_per_strategy < 0.0:
        raise ValueError(f"phi_per_strategy must be ≥ 0, got {phi_per_strategy!r}")
    return float(n_strategies * phi_per_strategy)


def social_conformity_phi(phi_individual: float, phi_group_norm: float,
                           conformity_weight: float = 0.5) -> float:
    """Weighted blend of individual and group φ under social conformity.

    phi_out = (1 − w) × phi_individual + w × phi_group_norm

    Parameters
    ----------
    phi_individual   : float — individual's own φ preference
    phi_group_norm   : float — group norm φ
    conformity_weight: float — weight on group norm ∈ [0, 1] (default 0.5)

    Returns
    -------
    phi_out : float
    """
    if not (0.0 <= conformity_weight <= 1.0):
        raise ValueError(f"conformity_weight must be in [0,1], got {conformity_weight!r}")
    return float((1.0 - conformity_weight) * phi_individual +
                 conformity_weight * phi_group_norm)
