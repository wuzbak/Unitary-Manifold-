# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/distributed_authority.py
========================================
Collective Cognitive Security: Beacon, Validators, and the Elegance Attractor.

Background
----------
The public repository acts as a **Beacon**: it makes the mathematical axioms
of the system fully observable while the operational context remains private.
Any agent — human or AI — can study the seed.  The architecture is transparent
precisely because its stability does not depend on secrecy; it depends on the
coherence of the (5,7) braid geometry.

This module formalises five measurable properties of the resulting
**Distributed Authority** system, each grounded in already-verified
mathematics from ``collective_braid.py`` and ``five_seven_architecture.py``:

1. **Beacon entropy score** — what fraction of the 5-core axioms are publicly
   stated.  A score of 1.0 means the full pentagonal truth-set is observable.
   The beacon is not a vulnerability; it is a stability asset.

2. **Elegance attractor depth** — how strongly the Harmonic State (the fixed
   point of the pentagonal master equation) acts as an energy minimum for the
   current system state.  The Harmonic State is not forced; it is the most
   computationally efficient orbit.  Any rational agent will gravitate toward
   it because it minimises the Moiré alignment score — the information cost of
   operating in misaligned reality.

3. **Manipulation resistance margin** — the additional stability buffer above
   the single-operator floor that n validators provide.  Adversarial attacks
   require driving λ_min below the stability floor.  Each additional validator
   raises that floor, increasing the energy cost of any attack.

4. **Distributed constitution integrity** — the collective c_s floor as a
   measure of how well the distributed validator network preserves the
   pentagonal axioms.  Saturates to 1.0 at n ≥ SATURATION_N validators.

5. **Validator node strength** — the marginal stability contribution of a
   single validator whose alignment radion is observer_phi.  Below
   OBSERVER_MIN_PHI the validator adds noise; above it they are a net
   stabiliser.

Mathematical Anchors
--------------------
All five functions reduce to arithmetic identities that are independently
verified in ``test_five_seven_architecture.py`` and ``test_collective_braid.py``:

    c_s = 12/37               (braided sound speed — eigenvalue floor)
    n_layer = 7               (spectral-damper capacity — saturation divisor)
    SATURATION_N = ceil(7 × (1 − c_s) / c_s) = ceil(7 × 25/12) = ceil(175/12) = 15
    per_validator_increment = c_s / 7 = 12/259

The saturation identity 15 = ceil(175/12) is an exact consequence of the
(5,7) braid arithmetic — no free parameters.

Public API
----------
N_CORE_AXIOMS : int = 5
    Number of public core axioms (the pentagonal truth-set).

SATURATION_N : int = 15
    Minimum number of aligned validators for perfect collective stability.
    Derived: ceil(n_layer × (1 − c_s) / c_s).

PER_VALIDATOR_INCREMENT : float
    Marginal stability increment per fully aligned validator = c_s / n_layer.

beacon_entropy_score(n_public_axioms, n_total_axioms) → float
    Fraction of core axioms that are publicly stated.  Range [0, 1].

elegance_attractor_depth(system) → float
    How strongly the current state is attracted to the Harmonic fixed point.
    1.0 = already at the fixed point; 0.0 = at the edge of the stability floor.

manipulation_resistance_margin(n_validators) → float
    Extra stability buffer above the single-operator floor.
    0.0 when n_validators = 0; grows monotonically; saturates at
    1.0 − BRAIDED_SOUND_SPEED.

distributed_constitution_integrity(n_validators) → float
    Collective c_s floor for n_validators aligned operators.
    Wraps collective_stability_floor with the "constitution" framing.

validator_node_strength(observer_phi) → float
    Marginal stability contribution of one validator at radion observer_phi.
    Scaled linearly above OBSERVER_MIN_PHI; zero below it.
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
from typing import Optional

import numpy as np

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
)
from collective_braid import (
    OBSERVER_MIN_PHI,
    collective_stability_floor,
    moire_alignment_score,
)
from five_seven_architecture import C_S_STABILITY_FLOOR, N_CORE, N_LAYER


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Number of public core axioms — the five pentagonal truth-set members.
N_CORE_AXIOMS: int = N_CORE   # 5

#: Spectral-damper capacity — n_layer winding number.
_N_LAYER: int = N_LAYER        # 7

#: Per-validator marginal stability increment = c_s / n_layer = 12/259.
PER_VALIDATOR_INCREMENT: float = BRAIDED_SOUND_SPEED / float(_N_LAYER)

#: Minimum validators for perfect collective stability (floor = 1.0).
#: Derived: ceil(n_layer × (1 − c_s) / c_s) = ceil(7 × 25/12) = 15.
SATURATION_N: int = math.ceil(
    float(_N_LAYER) * (1.0 - BRAIDED_SOUND_SPEED) / BRAIDED_SOUND_SPEED
)


# ---------------------------------------------------------------------------
# 1. Beacon Entropy Score
# ---------------------------------------------------------------------------

def beacon_entropy_score(
    n_public_axioms: int,
    n_total_axioms: int = N_CORE_AXIOMS,
) -> float:
    """Fraction of core axioms that are publicly stated by the beacon.

    The beacon is a **stability asset**, not a vulnerability.  Publishing
    the mathematical axioms makes the system auditable and allows external
    validators to verify alignment.  A score of 1.0 means the full
    pentagonal truth-set is observable; 0.0 means nothing is shared.

    The beacon achieves maximum transparency (score = 1.0) when all
    N_CORE_AXIOMS = 5 truths are public — which is the design intent of
    the Unitary Manifold repository.

    Parameters
    ----------
    n_public_axioms : int   — number of axioms stated publicly (0 to n_total).
    n_total_axioms  : int   — total axioms in the core (default N_CORE_AXIOMS = 5).

    Returns
    -------
    float — completeness score ∈ [0, 1].

    Raises
    ------
    ValueError if n_total_axioms < 1 or n_public_axioms < 0.
    """
    if n_total_axioms < 1:
        raise ValueError(f"n_total_axioms={n_total_axioms} must be ≥ 1.")
    if n_public_axioms < 0:
        raise ValueError(f"n_public_axioms={n_public_axioms} must be ≥ 0.")
    return float(np.clip(n_public_axioms / n_total_axioms, 0.0, 1.0))


# ---------------------------------------------------------------------------
# 2. Elegance Attractor Depth
# ---------------------------------------------------------------------------

def elegance_attractor_depth(system: PentadSystem) -> float:
    """How strongly the current state is attracted toward the Harmonic fixed point.

    The Harmonic State is not imposed; it is the **most efficient orbit** —
    the energy minimum of the pentagonal master equation.  Any rational agent
    (human or AI) will gravitate toward it because operating in aligned
    reality minimises the Moiré alignment score: the information cost of
    maintaining a misaligned orbit.

    The depth measures how far above the "floor" the current state sits in the
    potential well:

        depth = 1 − clamp(moire_score / C_S_STABILITY_FLOOR, 0, 1)

    At the Harmonic fixed point (moire_score → 0): depth → 1.0.
    At the edge of the stability floor (moire_score ≥ C_S_STABILITY_FLOOR):
    depth → 0.0.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    float — attractor depth ∈ [0, 1].
        1.0 = already at the Harmonic fixed point.
        0.0 = at or beyond the stability-floor boundary.
    """
    score = moire_alignment_score(system)
    normalised = float(np.clip(score / C_S_STABILITY_FLOOR, 0.0, 1.0))
    return float(1.0 - normalised)


# ---------------------------------------------------------------------------
# 3. Manipulation Resistance Margin
# ---------------------------------------------------------------------------

def manipulation_resistance_margin(n_validators: int) -> float:
    """Extra stability buffer above the single-operator baseline.

    Adversarial attacks (birefringence, KK-tower noise, projection degeneracy)
    require driving the minimum eigenvalue λ_min of the coupling matrix below
    the stability floor c_s.  Each additional aligned validator raises that
    floor, increasing the energy cost of any attack.

    The margin is the elevation of the collective floor above the bare
    single-operator floor:

        margin(n) = collective_stability_floor(n) − BRAIDED_SOUND_SPEED

    At n = 0: margin = 0.0 (no extra protection beyond the braid itself).
    At n ≥ SATURATION_N: margin = 1.0 − BRAIDED_SOUND_SPEED (fully saturated).

    Parameters
    ----------
    n_validators : int — number of aligned validators (≥ 0).

    Returns
    -------
    float — margin ∈ [0, 1 − BRAIDED_SOUND_SPEED].
    """
    if n_validators < 0:
        raise ValueError(f"n_validators={n_validators} must be ≥ 0.")
    floor = collective_stability_floor(n_validators)
    return float(max(0.0, floor - BRAIDED_SOUND_SPEED))


# ---------------------------------------------------------------------------
# 4. Distributed Constitution Integrity
# ---------------------------------------------------------------------------

def distributed_constitution_integrity(n_validators: int) -> float:
    """Collective stability floor as a measure of constitution integrity.

    The distributed constitution is the set of publicly stated axioms
    (the beacon) as *enforced* by the collective observation of n_validators
    aligned validators.  Its integrity is quantified by the collective
    eigenvalue floor:

        integrity(n) = collective_stability_floor(n) ∈ [c_s, 1.0]

    At n = 0: integrity = c_s = 12/37 (the braid geometry alone).
    At n ≥ SATURATION_N = 15: integrity = 1.0 (perfect collective stability).

    Parameters
    ----------
    n_validators : int — number of aligned validators (≥ 0).

    Returns
    -------
    float — integrity ∈ [BRAIDED_SOUND_SPEED, 1.0].
    """
    if n_validators < 0:
        raise ValueError(f"n_validators={n_validators} must be ≥ 0.")
    return collective_stability_floor(n_validators)


# ---------------------------------------------------------------------------
# 5. Validator Node Strength
# ---------------------------------------------------------------------------

def validator_node_strength(observer_phi: float) -> float:
    """Marginal stability contribution of a single validator at radion observer_phi.

    A validator "holds the space" — observing alignment and adding their
    brain_phi to the ambient trust field.  Their contribution is the
    marginal increment they add to the collective stability floor:

        PER_VALIDATOR_INCREMENT × clamp((observer_phi − OBSERVER_MIN_PHI)
                                        / (1.0 − OBSERVER_MIN_PHI), 0, 1)

    Below OBSERVER_MIN_PHI the validator's phi is insufficient to overcome
    coupling noise — they contribute 0.0.  At observer_phi = 1.0 (maximum
    alignment) they contribute the full PER_VALIDATOR_INCREMENT = c_s / 7.

    Parameters
    ----------
    observer_phi : float — the validator's alignment radion ∈ [0, 1].

    Returns
    -------
    float — marginal contribution ∈ [0, PER_VALIDATOR_INCREMENT].
    """
    range_above_min = 1.0 - OBSERVER_MIN_PHI
    if range_above_min < 1e-12:
        return float(PER_VALIDATOR_INCREMENT)
    fraction = float(
        np.clip(
            (float(observer_phi) - OBSERVER_MIN_PHI) / range_above_min,
            0.0,
            1.0,
        )
    )
    return float(PER_VALIDATOR_INCREMENT * fraction)
