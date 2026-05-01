# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/psychology/cognition.py
============================
Cognition as φ-Field Information Processing — Pillar 24: Psychology.

Theory
------
In the Unitary Manifold, a mind is a φ-attractor network.  Perception is
the mapping of external φ-signals onto internal state vectors; attention
selects which φ-dimensions receive the irreversibility-field drive.
Cognitive biases are systematic deformations of the φ-landscape that
steer trajectories away from maximum-information fixed-points.
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


def cognitive_phi_load(n_items: int, phi_per_item: float,
                        phi_capacity: float) -> float:
    """Cognitive load as fraction of φ-capacity consumed.

    load = n_items × phi_per_item / phi_capacity

    Parameters
    ----------
    n_items      : int   — items being processed (must be ≥ 0)
    phi_per_item : float — φ cost per item (must be ≥ 0)
    phi_capacity : float — total φ processing capacity (must be > 0)

    Returns
    -------
    load : float (> 1.0 = overloaded)
    """
    if n_items < 0:
        raise ValueError(f"n_items must be ≥ 0, got {n_items!r}")
    if phi_per_item < 0.0:
        raise ValueError(f"phi_per_item must be ≥ 0, got {phi_per_item!r}")
    if phi_capacity <= 0.0:
        raise ValueError(f"phi_capacity must be > 0, got {phi_capacity!r}")
    return float(n_items * phi_per_item / phi_capacity)


def perception_snr_phi(phi_stimulus: float, B_noise: float) -> float:
    """Perceptual signal-to-noise ratio.

    SNR = phi_stimulus / (B_noise + ε)

    Parameters
    ----------
    phi_stimulus : float — stimulus φ intensity (must be ≥ 0)
    B_noise      : float — perceptual noise floor (must be ≥ 0)

    Returns
    -------
    SNR : float
    """
    if phi_stimulus < 0.0:
        raise ValueError(f"phi_stimulus must be ≥ 0, got {phi_stimulus!r}")
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(phi_stimulus / (B_noise + _EPS))


def attention_bandwidth_phi(phi_attended: float, phi_total: float) -> float:
    """Fraction of perceptual bandwidth allocated to attended stimulus.

    bandwidth = phi_attended / phi_total ∈ [0, 1]

    Parameters
    ----------
    phi_attended : float — attended φ (must be ≥ 0)
    phi_total    : float — total perceptual φ (must be > 0)

    Returns
    -------
    bandwidth : float ∈ [0, 1]
    """
    if phi_attended < 0.0:
        raise ValueError(f"phi_attended must be ≥ 0, got {phi_attended!r}")
    if phi_total <= 0.0:
        raise ValueError(f"phi_total must be > 0, got {phi_total!r}")
    return float(np.clip(phi_attended / phi_total, 0.0, 1.0))


def memory_phi_trace(phi_encoded: float, t: float, tau: float = 24.0) -> float:
    """Memory trace decay following Ebbinghaus forgetting curve.

    φ_trace(t) = phi_encoded × exp(−t / tau)

    Parameters
    ----------
    phi_encoded : float — initially encoded φ (must be ≥ 0)
    t           : float — elapsed time in hours (must be ≥ 0)
    tau         : float — forgetting time constant (default 24 hours, must be > 0)

    Returns
    -------
    phi_trace : float
    """
    if phi_encoded < 0.0:
        raise ValueError(f"phi_encoded must be ≥ 0, got {phi_encoded!r}")
    if t < 0.0:
        raise ValueError(f"t must be ≥ 0, got {t!r}")
    if tau <= 0.0:
        raise ValueError(f"tau must be > 0, got {tau!r}")
    return float(phi_encoded * math.exp(-t / tau))


def reasoning_phi(phi_premises: float, phi_inference_cost: float) -> float:
    """Net φ available after reasoning costs.

    phi_conclusion = phi_premises − phi_inference_cost

    Parameters
    ----------
    phi_premises      : float — φ information in premises (must be ≥ 0)
    phi_inference_cost: float — φ spent on inference (must be ≥ 0)

    Returns
    -------
    phi_conclusion : float (clipped to 0)
    """
    if phi_premises < 0.0:
        raise ValueError(f"phi_premises must be ≥ 0, got {phi_premises!r}")
    if phi_inference_cost < 0.0:
        raise ValueError(f"phi_inference_cost must be ≥ 0, got {phi_inference_cost!r}")
    return float(max(0.0, phi_premises - phi_inference_cost))


def problem_solving_phi(phi_goal: float, phi_current: float,
                         phi_repertoire: float) -> float:
    """φ-distance to a goal state divided by available solution φ.

    difficulty = (phi_goal − phi_current) / (phi_repertoire + ε)

    Parameters
    ----------
    phi_goal       : float — target φ state
    phi_current    : float — current φ state
    phi_repertoire : float — available problem-solving φ (must be ≥ 0)

    Returns
    -------
    difficulty : float
    """
    if phi_repertoire < 0.0:
        raise ValueError(f"phi_repertoire must be ≥ 0, got {phi_repertoire!r}")
    return float((phi_goal - phi_current) / (phi_repertoire + _EPS))


def creativity_phi(phi_associations: float, phi_constraints: float) -> float:
    """Creative output φ as remote associations minus cognitive constraints.

    creativity = phi_associations − phi_constraints

    Parameters
    ----------
    phi_associations : float — φ of available associative connections (must be ≥ 0)
    phi_constraints  : float — φ of inhibitory cognitive constraints (must be ≥ 0)

    Returns
    -------
    creativity : float (higher → more creative, clipped to 0)
    """
    if phi_associations < 0.0:
        raise ValueError(f"phi_associations must be ≥ 0, got {phi_associations!r}")
    if phi_constraints < 0.0:
        raise ValueError(f"phi_constraints must be ≥ 0, got {phi_constraints!r}")
    return float(max(0.0, phi_associations - phi_constraints))


def metacognition_phi(phi_actual: float, phi_perceived: float) -> float:
    """Metacognitive accuracy: match between actual and perceived φ.

    accuracy = 1 − |phi_actual − phi_perceived| / (phi_actual + ε)

    Parameters
    ----------
    phi_actual    : float — true cognitive φ level (must be ≥ 0)
    phi_perceived : float — self-estimated φ level (must be ≥ 0)

    Returns
    -------
    accuracy : float ∈ [0, 1]
    """
    if phi_actual < 0.0:
        raise ValueError(f"phi_actual must be ≥ 0, got {phi_actual!r}")
    if phi_perceived < 0.0:
        raise ValueError(f"phi_perceived must be ≥ 0, got {phi_perceived!r}")
    acc = 1.0 - abs(phi_actual - phi_perceived) / (phi_actual + _EPS)
    return float(np.clip(acc, 0.0, 1.0))


def executive_phi_function(phi_inhibition: float, phi_updating: float,
                            phi_shifting: float) -> float:
    """Composite executive function φ from three core components.

    EF = phi_inhibition + phi_updating + phi_shifting

    Parameters
    ----------
    phi_inhibition : float — response inhibition φ (must be ≥ 0)
    phi_updating   : float — working memory updating φ (must be ≥ 0)
    phi_shifting   : float — task-switching φ (must be ≥ 0)

    Returns
    -------
    EF : float
    """
    for name, v in [("phi_inhibition", phi_inhibition),
                    ("phi_updating", phi_updating),
                    ("phi_shifting", phi_shifting)]:
        if v < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {v!r}")
    return float(phi_inhibition + phi_updating + phi_shifting)


def cognitive_phi_bias(phi_true: float, phi_biased: float) -> float:
    """Magnitude of cognitive bias as deviation from true φ estimate.

    bias = phi_biased − phi_true

    Parameters
    ----------
    phi_true   : float — Bayesian optimal φ estimate
    phi_biased : float — biased φ estimate

    Returns
    -------
    bias : float (positive = overestimate, negative = underestimate)
    """
    return float(phi_biased - phi_true)
