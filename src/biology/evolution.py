# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/biology/evolution.py
=========================
Evolution as FTUM Gradient Flow — Pillar: Biology.

Fitness landscape = FTUM landscape over genotype space
-------------------------------------------------------
The Walker-Pearson UEUM operator U acts on the space of possible genotypes
exactly as it acts on the space of field configurations: every genotype is
a point in the φ-configuration space, and fitness is a scalar functional
of that point.  The fitness landscape is therefore:

    f(φ) = exp(−(φ − φ_opt)² / (2 σ²))

a Gaussian peak centred on the optimal entanglement capacity φ_opt.

Selection pressure = gradient ∇S_U in the UEUM geodesic equation
-----------------------------------------------------------------
Natural selection pushes the population toward higher φ exactly as the
UEUM operator pushes a field configuration toward the nearest FTUM fixed
point.  The selection gradient is:

    ∇f = df/dφ = −(φ − φ_opt) / σ² · f(φ)

pointing toward φ_opt from either side of the peak.

Species = stable FTUM fixed points; extinction = fixed-point annihilation
--------------------------------------------------------------------------
A species is a stable cluster of genotypes around a local fitness maximum
— a FTUM fixed point.  Extinction corresponds to the disappearance of that
fixed point: the landscape changes until φ_species < φ_min, the minimum
viable φ below which the fixed point no longer exists.

Evolution by natural selection
-------------------------------
Each generation the population centroid moves along the fitness gradient:

    φ_new = φ + η ∇f(φ)

where η is the learning rate (selection intensity × generation time).

Genetic drift
-------------
Neutral evolution is a random walk on the FTUM landscape:

    φ_drift = φ + ε,   ε ~ Normal(0, σ_drift²)

Mutation rate
-------------
The B_μ Irreversibility Field drives genetic change.  Stronger B_μ →
higher chemical reactivity → higher point-mutation probability:

    μ_mut = μ_base × (1 + |B|)

Public API
----------
fitness_landscape(phi_values, phi_optimal, width)
    Gaussian fitness peak f(φ) = exp(−(φ − φ_opt)² / (2 width²)).

selection_gradient(phi, phi_optimal, width)
    Gradient of fitness landscape ∇f(φ).

ftum_evolution_step(phi_pop, phi_optimal, learning_rate, width)
    One gradient-ascent generation on the FTUM fitness landscape.

genetic_drift(phi_pop, sigma_drift, seed)
    Random walk on the FTUM landscape (neutral evolution).

mutation_rate(B_strength, base_rate)
    μ_mut = base_rate × (1 + B_strength).

species_distance(phi_a, phi_b)
    Euclidean distance |φ_a − φ_b| between two FTUM fixed points.

extinction_criterion(phi_species, phi_min)
    True iff φ_species < φ_min (fixed point annihilated → extinction).

population_entropy(phi_pop)
    Shannon entropy of the φ-distribution across the population.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_WIDTH_DEFAULT: float = 1.0
_PHI_MIN_DEFAULT: float = 0.01
_BASE_RATE_DEFAULT: float = 1e-8
_ENTROPY_BINS: int = 20
_ENTROPY_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Fitness landscape
# ---------------------------------------------------------------------------

def fitness_landscape(
    phi_values: np.ndarray,
    phi_optimal: float,
    width: float = _WIDTH_DEFAULT,
) -> np.ndarray:
    """Gaussian fitness peak over genotype space.

    The FTUM fitness functional assigns a real-valued fitness to each
    genotype φ:

        f(φ) = exp(−(φ − φ_opt)² / (2 width²))

    The peak is at φ_opt; the width σ controls how sharply fitness falls
    off away from the optimum (analogous to the basin radius of a FTUM
    fixed point).

    Parameters
    ----------
    phi_values  : ndarray — φ coordinates across genotype space
    phi_optimal : float   — optimal φ (peak of the fitness landscape)
    width       : float   — landscape width σ (must be > 0)

    Returns
    -------
    f : ndarray, same shape as phi_values — fitness values ∈ (0, 1]

    Raises
    ------
    ValueError
        If width ≤ 0.
    """
    if width <= 0.0:
        raise ValueError(f"width must be > 0, got {width!r}")
    phi_arr = np.asarray(phi_values, dtype=float)
    return np.exp(-0.5 * ((phi_arr - phi_optimal) / width) ** 2)


def selection_gradient(
    phi: np.ndarray,
    phi_optimal: float,
    width: float = _WIDTH_DEFAULT,
) -> np.ndarray:
    """Gradient of the fitness landscape (selection pressure direction).

    The derivative of the Gaussian fitness peak with respect to φ:

        ∇f = df/dφ = −(φ − φ_opt) / width² · f(φ)

    Points toward φ_opt from both sides; vanishes exactly at the peak.

    Parameters
    ----------
    phi         : ndarray — current φ values of the population
    phi_optimal : float   — optimal φ
    width       : float   — landscape width σ (default 1)

    Returns
    -------
    grad_f : ndarray, same shape as phi
    """
    phi_arr = np.asarray(phi, dtype=float)
    f = fitness_landscape(phi_arr, phi_optimal, width)
    return -(phi_arr - phi_optimal) / (width**2) * f


def ftum_evolution_step(
    phi_pop: np.ndarray,
    phi_optimal: float,
    learning_rate: float = 0.01,
    width: float = _WIDTH_DEFAULT,
) -> np.ndarray:
    """One gradient-ascent generation on the FTUM fitness landscape.

    Models one generation of natural selection as a gradient-ascent step
    on the FTUM fitness functional:

        φ_new = φ + η · ∇f(φ)

    where η is the selection intensity (learning rate).

    Parameters
    ----------
    phi_pop       : ndarray — current φ values of the population
    phi_optimal   : float   — fitness peak φ_opt
    learning_rate : float   — selection intensity η (default 0.01)
    width         : float   — landscape width σ (default 1)

    Returns
    -------
    phi_new : ndarray, same shape as phi_pop
    """
    phi_arr = np.asarray(phi_pop, dtype=float)
    grad = selection_gradient(phi_arr, phi_optimal, width)
    return phi_arr + learning_rate * grad


def genetic_drift(
    phi_pop: np.ndarray,
    sigma_drift: float,
    seed: int | None = None,
) -> np.ndarray:
    """Random walk on the FTUM landscape (neutral genetic drift).

    Adds Gaussian noise to every individual's φ — models stochastic
    variation in small populations where selection is overwhelmed by
    random sampling:

        φ_drift = φ + ε,   ε ~ Normal(0, σ_drift²)

    Parameters
    ----------
    phi_pop     : ndarray — current φ values of the population
    sigma_drift : float   — drift standard deviation σ_drift
    seed        : int or None — random seed (default None)

    Returns
    -------
    phi_drift : ndarray, same shape as phi_pop
    """
    phi_arr = np.asarray(phi_pop, dtype=float)
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=0.0, scale=sigma_drift, size=phi_arr.shape)
    return phi_arr + noise


def mutation_rate(
    B_strength: float,
    base_rate: float = _BASE_RATE_DEFAULT,
) -> float:
    """Mutation rate amplified by the B_μ Irreversibility Field.

    Stronger local B_μ → higher chemical reactivity → higher point-mutation
    probability:

        μ_mut = μ_base × (1 + |B|)

    Parameters
    ----------
    B_strength : float — local B_μ field magnitude (must be ≥ 0)
    base_rate  : float — baseline mutation rate μ_base (default 1e-8)

    Returns
    -------
    mu : float — effective mutation rate (≥ base_rate)

    Raises
    ------
    ValueError
        If B_strength < 0.
    """
    if B_strength < 0.0:
        raise ValueError(f"B_strength must be ≥ 0, got {B_strength!r}")
    return float(base_rate * (1.0 + B_strength))


def species_distance(phi_a: float, phi_b: float) -> float:
    """Distance between two FTUM fixed points (species).

    Species are identified with stable FTUM fixed points in the φ
    configuration space.  Their distance is simply:

        d = |φ_a − φ_b|

    Parameters
    ----------
    phi_a : float — φ of species A
    phi_b : float — φ of species B

    Returns
    -------
    d : float — non-negative species distance
    """
    return float(abs(phi_a - phi_b))


def extinction_criterion(
    phi_species: float,
    phi_min: float = _PHI_MIN_DEFAULT,
) -> bool:
    """Extinction test: fixed-point annihilation below φ_min.

    A species goes extinct when its characteristic φ falls below the
    minimum viable φ — the threshold below which the FTUM fixed point
    ceases to exist:

        extinct = (φ_species < φ_min)

    Parameters
    ----------
    phi_species : float — characteristic φ of the species
    phi_min     : float — minimum viable φ (default 0.01)

    Returns
    -------
    bool — True iff the species is extinct
    """
    return bool(phi_species < phi_min)


def population_entropy(phi_pop: np.ndarray) -> float:
    """Shannon entropy of the φ-distribution across the population.

    Measures the diversity of the population by binning individual φ
    values into 20 histogram bins and computing:

        S_pop = −∑ p_i log p_i   (nats, base e)

    where p_i are the normalised bin probabilities.  A monomorphic
    population (all φ identical) gives S_pop ≈ 0; a maximally spread
    population gives S_pop ≈ log(20).

    Parameters
    ----------
    phi_pop : ndarray — φ values of the population

    Returns
    -------
    S_pop : float — Shannon entropy (≥ 0)
    """
    phi_arr = np.asarray(phi_pop, dtype=float)
    counts, _ = np.histogram(phi_arr, bins=_ENTROPY_BINS)
    p = counts / (counts.sum() + _ENTROPY_EPSILON)
    p = np.clip(p, _ENTROPY_EPSILON, None)
    return float(-np.sum(p * np.log(p)))
