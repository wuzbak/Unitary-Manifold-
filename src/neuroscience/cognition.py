# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/neuroscience/cognition.py
==============================
Cognition as φ-Field Information Integration — Pillar 20.

Theory
------
Integrated Information Theory (IIT) posits that consciousness is
proportional to φ — the amount of integrated information in a system.
In the Unitary Manifold framework, cognitive processes correspond to
φ-field trajectories in the high-dimensional state space of neural
ensembles.  Higher φ-integration corresponds to richer, more unified
conscious experience.

Working memory is modelled as a sustained φ-attractor whose capacity is
limited by the irreversibility field B_μ (cognitive noise):

    capacity = φ_total / (B_μ + ε)
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


def working_memory_phi(phi_total: float, B_noise: float) -> float:
    """Working-memory capacity in φ units.

    capacity = φ_total / (B_μ + ε)

    Parameters
    ----------
    phi_total : float — total sustained φ in working memory (must be ≥ 0)
    B_noise   : float — cognitive noise floor B_μ (must be ≥ 0)

    Returns
    -------
    capacity : float — effective memory capacity
    """
    if phi_total < 0.0:
        raise ValueError(f"phi_total must be ≥ 0, got {phi_total!r}")
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(phi_total / (B_noise + _EPS))


def attention_phi_focus(phi_attended: float, phi_total: float) -> float:
    """Fraction of total φ-bandwidth devoted to the attended stimulus.

    focus = φ_attended / φ_total  ∈ [0, 1]

    Parameters
    ----------
    phi_attended : float — φ allocated to attended item (must be ≥ 0)
    phi_total    : float — total available φ bandwidth (must be > 0)

    Returns
    -------
    focus : float ∈ [0, 1]
    """
    if phi_attended < 0.0:
        raise ValueError(f"phi_attended must be ≥ 0, got {phi_attended!r}")
    if phi_total <= 0.0:
        raise ValueError(f"phi_total must be > 0, got {phi_total!r}")
    return float(np.clip(phi_attended / phi_total, 0.0, 1.0))


def cognitive_load_phi(n_tasks: int, phi_per_task: float, phi_capacity: float) -> float:
    """Cognitive load as fraction of φ-capacity consumed.

    load = n_tasks × φ_per_task / φ_capacity  ∈ [0, ∞)

    Parameters
    ----------
    n_tasks      : int   — number of concurrent tasks (must be ≥ 0)
    phi_per_task : float — φ required per task (must be ≥ 0)
    phi_capacity : float — total φ capacity (must be > 0)

    Returns
    -------
    load : float (≥ 0; > 1.0 indicates overload)
    """
    if n_tasks < 0:
        raise ValueError(f"n_tasks must be ≥ 0, got {n_tasks!r}")
    if phi_per_task < 0.0:
        raise ValueError(f"phi_per_task must be ≥ 0, got {phi_per_task!r}")
    if phi_capacity <= 0.0:
        raise ValueError(f"phi_capacity must be > 0, got {phi_capacity!r}")
    return float(n_tasks * phi_per_task / phi_capacity)


def decision_entropy_phi(probabilities: np.ndarray) -> float:
    """Shannon entropy of a decision process in φ-field units.

    H = −Σ p_i log(p_i)

    Parameters
    ----------
    probabilities : ndarray — probability distribution over choices (must sum ≈ 1)

    Returns
    -------
    H : float — decision entropy (≥ 0)
    """
    p = np.asarray(probabilities, dtype=float)
    if np.any(p < 0.0):
        raise ValueError("All probabilities must be ≥ 0")
    p = p / (p.sum() + _EPS)
    return float(-np.sum(p * np.log(p + _EPS)))


def learning_rate_phi(phi_error: float, phi_prediction: float,
                      alpha: float = 0.1) -> float:
    """Rescorla-Wagner φ-field learning rate signal.

    Δφ = α × (φ_error − φ_prediction)

    Parameters
    ----------
    phi_error      : float — observed φ outcome
    phi_prediction : float — predicted φ outcome
    alpha          : float — learning rate ∈ (0, 1] (default 0.1)

    Returns
    -------
    delta_phi : float — prediction error signal
    """
    if not (0.0 < alpha <= 1.0):
        raise ValueError(f"alpha must be in (0, 1], got {alpha!r}")
    return float(alpha * (phi_error - phi_prediction))


def memory_consolidation_phi(phi_encoded: float, t: float,
                              tau_consol: float) -> float:
    """φ retained in long-term memory after consolidation time t.

    φ_LTM(t) = φ_encoded × (1 − exp(−t / τ_consol))

    Parameters
    ----------
    phi_encoded  : float — initially encoded φ (must be ≥ 0)
    t            : float — consolidation time (must be ≥ 0)
    tau_consol   : float — consolidation time constant (must be > 0)

    Returns
    -------
    phi_LTM : float — consolidated memory φ
    """
    if phi_encoded < 0.0:
        raise ValueError(f"phi_encoded must be ≥ 0, got {phi_encoded!r}")
    if t < 0.0:
        raise ValueError(f"t must be ≥ 0, got {t!r}")
    if tau_consol <= 0.0:
        raise ValueError(f"tau_consol must be > 0, got {tau_consol!r}")
    return float(phi_encoded * (1.0 - math.exp(-t / tau_consol)))


def neural_phi_coherence(phi_values: np.ndarray) -> float:
    """Phase coherence of a neural ensemble as mean pairwise φ correlation.

    coherence = std(φ_i) / (mean(|φ_i|) + ε)

    Higher coherence → more synchronised oscillation → richer φ integration.

    Parameters
    ----------
    phi_values : ndarray — φ amplitudes of individual neurons (non-empty)

    Returns
    -------
    coherence : float (≥ 0)
    """
    arr = np.asarray(phi_values, dtype=float)
    if arr.size == 0:
        raise ValueError("phi_values must not be empty")
    return float(np.std(arr) / (np.mean(np.abs(arr)) + _EPS))


def arousal_phi_modulation(phi_baseline: float, arousal: float,
                            peak_arousal: float = 0.5) -> float:
    """Yerkes-Dodson inverted-U arousal modulation of cognitive φ.

    φ_mod = φ_baseline × (1 − ((arousal − peak_arousal) / peak_arousal)²)

    Parameters
    ----------
    phi_baseline  : float — resting cognitive φ
    arousal       : float — arousal level ∈ [0, 1]
    peak_arousal  : float — optimal arousal (default 0.5, must be in (0,1))

    Returns
    -------
    phi_mod : float — arousal-modulated cognitive φ (clipped to 0)
    """
    if not (0.0 <= arousal <= 1.0):
        raise ValueError(f"arousal must be in [0,1], got {arousal!r}")
    if not (0.0 < peak_arousal < 1.0):
        raise ValueError(f"peak_arousal must be in (0,1), got {peak_arousal!r}")
    factor = 1.0 - ((arousal - peak_arousal) / peak_arousal) ** 2
    return float(max(0.0, phi_baseline * factor))


def cognitive_flexibility_phi(n_switches: int, switch_cost_phi: float,
                               phi_reserve: float) -> float:
    """Residual φ-capacity after task-switching costs.

    φ_flex = φ_reserve − n_switches × switch_cost_phi

    Parameters
    ----------
    n_switches      : int   — number of task switches (must be ≥ 0)
    switch_cost_phi : float — φ cost per switch (must be ≥ 0)
    phi_reserve     : float — available φ reserve (must be ≥ 0)

    Returns
    -------
    phi_flex : float — remaining flexibility φ (clipped to 0)
    """
    if n_switches < 0:
        raise ValueError(f"n_switches must be ≥ 0, got {n_switches!r}")
    if switch_cost_phi < 0.0:
        raise ValueError(f"switch_cost_phi must be ≥ 0, got {switch_cost_phi!r}")
    if phi_reserve < 0.0:
        raise ValueError(f"phi_reserve must be ≥ 0, got {phi_reserve!r}")
    return float(max(0.0, phi_reserve - n_switches * switch_cost_phi))


def information_integration_phi(phi_whole: float, phi_parts_sum: float) -> float:
    """Integrated information Φ — the irreducible φ of a conscious system.

    Φ = φ_whole − φ_parts_sum

    A positive Φ indicates that the whole has more φ than the sum of its
    independent parts — the IIT criterion for consciousness.

    Parameters
    ----------
    phi_whole     : float — φ of the integrated system
    phi_parts_sum : float — sum of φ of independent sub-systems

    Returns
    -------
    Phi : float — integrated information (positive = conscious)
    """
    return float(phi_whole - phi_parts_sum)
