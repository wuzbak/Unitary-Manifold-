# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/collective_braid.py
====================================
The Collective Braid: Moiré Alignment, Coherence Agreement, Ripple Effect,
and the Observer as Stabilising Medium.

Background
----------
The Seed Protocol answers the question of *survival*: how does the system
preserve its core knowledge when everything goes wrong?  This module answers
the complementary question: what happens when the system *thrives*?

When a biological observer completes the Handshake and germination succeeds,
the Pentad does not simply return to its previous state.  If the new operator's
alignment is simultaneously **novel** (not a repetition of a past orbit) and
**coherent** (non-contradictory), the system instantiates a *Moiré Superlattice*:
a new stable layer of reality built on the same (5,7) topological bones but
never before expressed.

Furthermore, because the five bodies are maximally coupled (ρ = 35/37), a
single operator's re-alignment immediately propagates across the entire
coupling matrix.  This is the **Ripple Effect**: stabilising one orbit
mathematically lowers the instability noise for every other body in the
collective manifold, making it easier for others to find their own resonance.

The Collective Braid
---------------------
When multiple individual operators each achieve their own (5,7) alignment,
their individual Pentads join into a **Collective Braid**.  Each new aligned
thread stiffens the fabric:

    collective_c_s_floor(n) = min(1.0, c_s + n × (c_s / 7))

where the divisor 7 is the n_layer spectral-damper capacity.  With n = 7
fully aligned operators the collective floor reaches 2 × c_s ≈ 0.65; with
n ≥ 15 it saturates to 1.0 (perfect collective stability).

This is the mathematical content of the observation that one person's genuine
alignment "stiffens the fabric of reality" for those around them.  It is not
mysticism; it is eigenvalue arithmetic.

The Observer Effect
--------------------
An external observer who "holds the space" for another — who sees that
person's potential alignment before they themselves can see it — acts as a
Trust Field proxy.  Their brain_phi contributes a measurable τ_observer to
the subject's coupling field, lowering the energy cost of reaching the
Harmonic State.  The minimum brain_phi required to be a net stabiliser is
OBSERVER_MIN_PHI = TRUST_PHI_MIN.

The Moiré Superlattice
-----------------------
The product novelty_factor × coherence_score determines whether a new
alignment creates a genuinely new layer of reality (score ≥
NOVELTY_COHERENCE_THRESHOLD) or merely retraces a previous orbit (score
below threshold).  The distinction matters: the universe responds to
*coherent novelty*, not to incoherent novelty (chaos) or coherent repetition
(stagnation).

Public API
----------
MOIRE_ALIGNMENT_TOL : float
    ΔI_{human,univ} below which Geometric Recognition ("the click") is
    considered achieved.

OBSERVER_MIN_PHI : float
    Minimum brain_phi for an external observer to be a net stabiliser.

NOVELTY_COHERENCE_THRESHOLD : float
    Minimum novelty × coherence product for a Moiré Superlattice to be seeded.

moire_alignment_score(system) → float
    ΔI_{human,univ}: the Information Gap between Human intent and Universe.
    Zero = perfect Geometric Recognition.

is_moire_aligned(system, tol) → bool
    True iff ΔI_{human,univ} < tol.

coherence_score(system) → float
    How coherent the Human's intent is as a Master Frequency for Ψ_univ.
    Returns a value in [0, 1] where 1 = perfect coherence.

coherence_agreement(system, tol) → bool
    True iff coherence_score ≥ (1 − tol).

multi_dimensional_coherence(system) → float
    Alignment between the 4D action layer (Ψ_brain) and 5D potential (Ψ_univ).
    Returns a value in [0, 1].

ripple_effect(system, delta_phi_human) → float
    Change in λ_min of the coupling matrix when Human's φ shifts by
    delta_phi_human.  Positive = stabilising ripple for the whole manifold.

collective_stability_floor(n_aligned) → float
    Estimated global c_s floor raised by n_aligned individual operators.

observer_trust_field(observer_phi) → float
    Effective Trust Field contribution from an external "holding-the-space"
    observer.  Returns τ_observer ∈ [0, 1].

is_net_stabiliser(observer_phi) → bool
    True iff the observer's brain_phi is above OBSERVER_MIN_PHI.

moire_superlattice_score(novelty_factor, coherence) → float
    Novelty × Coherence product ∈ [0, 1].

is_superlattice_seeded(novelty_factor, coherence) → bool
    True iff moire_superlattice_score ≥ NOVELTY_COHERENCE_THRESHOLD.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple

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
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
    pentad_pairwise_gaps,
)
from five_seven_architecture import C_S_STABILITY_FLOOR
from src.consciousness.coupled_attractor import ManifoldState


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: ΔI_{human,univ} below which Geometric Recognition is achieved.
MOIRE_ALIGNMENT_TOL: float = 1e-3

#: Minimum brain_phi for an external observer to be a net stabiliser
#: (same as the Trust floor — below this the observer adds noise).
OBSERVER_MIN_PHI: float = TRUST_PHI_MIN

#: Minimum novelty × coherence product for a Moiré Superlattice to be seeded.
NOVELTY_COHERENCE_THRESHOLD: float = 0.10

#: Divisor used in collective stability calculation: n_layer = 7.
_N_LAYER_CAPACITY: int = 7


# ---------------------------------------------------------------------------
# Moiré Alignment
# ---------------------------------------------------------------------------

def moire_alignment_score(system: PentadSystem) -> float:
    """ΔI_{human,univ} — the Information Gap between Human intent and Universe.

    This is the primary diagnostic for Geometric Recognition.  When this
    value drops to zero the Human's intent and the Universe's radion have
    locked into phase — the "Moiré interference patterns vanish."

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    float — ΔI_{human,univ} = |φ_human² − φ_univ²| ≥ 0
    """
    gaps = pentad_pairwise_gaps(system)
    return float(
        gaps.get(
            (PentadLabel.UNIV, PentadLabel.HUMAN),
            gaps.get((PentadLabel.HUMAN, PentadLabel.UNIV), 0.0),
        )
    )


def is_moire_aligned(
    system: PentadSystem,
    tol: float = MOIRE_ALIGNMENT_TOL,
) -> bool:
    """True iff ΔI_{human,univ} < tol — the "click" of Geometric Recognition.

    Parameters
    ----------
    system : PentadSystem
    tol    : float — alignment tolerance (default MOIRE_ALIGNMENT_TOL = 1e-3)

    Returns
    -------
    bool
    """
    return bool(moire_alignment_score(system) < tol)


# ---------------------------------------------------------------------------
# Coherence Score
# ---------------------------------------------------------------------------

def coherence_score(system: PentadSystem) -> float:
    """How coherent the Human's intent is as a Master Frequency for Ψ_univ.

    A "coherent" Human is one whose radion φ_human is non-contradictory with
    respect to φ_univ.  The coherence is measured as:

        coherence = 1 − ΔI_{human,univ} / φ_univ²

    Clamped to [0, 1].  At coherence = 1 the Human's intent and the
    Universe's radion are perfectly aligned; the Universe "agrees" by
    allowing its constants to settle into the stable orbit the Human defines.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    float — coherence ∈ [0, 1]
    """
    phi_univ = float(system.bodies[PentadLabel.UNIV].phi)
    denom = phi_univ ** 2
    if denom < 1e-12:
        return 0.0
    gap = moire_alignment_score(system)
    return float(max(0.0, 1.0 - gap / denom))


def coherence_agreement(
    system: PentadSystem,
    tol: float = 1e-3,
) -> bool:
    """True iff the Human provides a coherent Master Frequency for Ψ_univ.

    The Universe "agrees" (locks into the Human's frequency as a fixed point)
    iff coherence_score ≥ 1 − tol.

    Parameters
    ----------
    system : PentadSystem
    tol    : float — maximum allowed deviation from perfect coherence (1e-3)

    Returns
    -------
    bool
    """
    return bool(coherence_score(system) >= (1.0 - tol))


# ---------------------------------------------------------------------------
# Multi-Dimensional Coherence
# ---------------------------------------------------------------------------

def multi_dimensional_coherence(system: PentadSystem) -> float:
    """Alignment between the 4D action layer (Ψ_brain) and 5D potential (Ψ_univ).

    The "two shapes recognising each other": the biological observer's
    embodied action (Ψ_brain, 4D) and the full physical manifold (Ψ_univ,
    5D) aligning their radions.

        4D_coherence = 1 − |φ_brain² − φ_univ²| / max(φ_brain², φ_univ²)

    When this reaches 1 the observer is no longer merely inside the manifold;
    their local frequency *is* the manifold frequency.  The Information Gap
    between who you are and what you are capable of vanishes.

    Parameters
    ----------
    system : PentadSystem

    Returns
    -------
    float — 4D/5D coherence ∈ [0, 1]
    """
    phi_brain = float(system.bodies[PentadLabel.BRAIN].phi)
    phi_univ  = float(system.bodies[PentadLabel.UNIV].phi)
    denom = max(phi_brain ** 2, phi_univ ** 2)
    if denom < 1e-12:
        return 0.0
    gap = abs(phi_brain ** 2 - phi_univ ** 2)
    return float(max(0.0, 1.0 - gap / denom))


# ---------------------------------------------------------------------------
# Ripple Effect
# ---------------------------------------------------------------------------

def ripple_effect(
    system: PentadSystem,
    delta_phi_human: float,
) -> float:
    """Change in ΔI_{human,univ} when the Human's φ shifts by delta_phi_human.

    The "Ripple Effect" is most directly measured as the reduction in the
    Human–Universe Information Gap (the Moiré alignment score).  When the
    human aligns — moves their φ toward φ_univ — the Information Gap drops,
    the universe "agrees," and the orbit tightens via the near-maximal
    coupling ρ = 35/37.

    Return convention (positive = improvement):

        ripple = moire_score_before − moire_score_after

        > 0 → aligning shift; the Information Gap shrinks
              (the human is moving toward the universe — stabilising ripple)
        < 0 → misaligning shift; the Information Gap grows
              (the human is moving away — destabilising ripple)
        = 0 → neutral (Human φ was already perfectly aligned or clamped)

    Parameters
    ----------
    system          : PentadSystem — baseline state.
    delta_phi_human : float — proposed change in the Human body's radion.

    Returns
    -------
    float — reduction in ΔI_{human,univ} (positive = stabilising ripple)
    """
    score_before = moire_alignment_score(system)

    old_human = system.bodies[PentadLabel.HUMAN]
    new_phi   = float(np.clip(old_human.phi + delta_phi_human, 0.0, 2.0))
    new_human = ManifoldState(
        node=old_human.node,
        phi=new_phi,
        n1=old_human.n1,
        n2=old_human.n2,
        k_cs=old_human.k_cs,
        label=old_human.label,
    )
    new_bodies = dict(system.bodies)
    new_bodies[PentadLabel.HUMAN] = new_human
    perturbed = PentadSystem(
        bodies=new_bodies,
        beta=system.beta,
        grace_steps=system.grace_steps,
        grace_decay=system.grace_decay,
        _trust_reservoir=system._trust_reservoir,
        _grace_elapsed=system._grace_elapsed,
    )

    score_after = moire_alignment_score(perturbed)
    return float(score_before - score_after)


# ---------------------------------------------------------------------------
# Collective Stability Floor
# ---------------------------------------------------------------------------

def collective_stability_floor(n_aligned: int) -> float:
    """Estimated global c_s floor raised by n_aligned individual operators.

    Each aligned individual Pentad contributes a marginal stability increment
    of BRAIDED_SOUND_SPEED / N_LAYER (where N_LAYER = 7 is the spectral-
    damper capacity of the (5,7) architecture):

        floor(n) = min(1.0, c_s + n × (c_s / 7))

    With n = 7 fully aligned operators the collective floor ≈ 2 × c_s.
    With n ≥ 15 it saturates to 1.0 (perfect collective stability).

    This is the eigenvalue arithmetic behind the observation that one person's
    alignment "stiffens the fabric of reality" for others: each additional
    stable thread in the Collective Braid raises the global eigenvalue floor,
    making Pentagonal Collapse harder to achieve.

    Parameters
    ----------
    n_aligned : int — number of aligned individual operators (≥ 0).

    Returns
    -------
    float — collective c_s floor ∈ [BRAIDED_SOUND_SPEED, 1.0]
    """
    if n_aligned < 1:
        return float(BRAIDED_SOUND_SPEED)
    increment = BRAIDED_SOUND_SPEED * float(n_aligned) / float(_N_LAYER_CAPACITY)
    return float(min(1.0, BRAIDED_SOUND_SPEED + increment))


# ---------------------------------------------------------------------------
# Observer Trust Field
# ---------------------------------------------------------------------------

def observer_trust_field(observer_phi: float) -> float:
    """Effective Trust Field contribution from an external observer.

    When an observer "holds the space" for another — seeing that person's
    potential alignment before they themselves can — the observer's brain_phi
    acts as a proxy Trust injection into the subject's coupling field.

    The effective contribution is the observer's φ clamped to [0, 1].  An
    observer whose φ is below OBSERVER_MIN_PHI = TRUST_PHI_MIN adds noise
    rather than stability (they are not yet sufficiently aligned themselves
    to stabilise another).

    Parameters
    ----------
    observer_phi : float — the external observer's brain/intent radion.

    Returns
    -------
    float — τ_observer ∈ [0, 1]
    """
    return float(np.clip(float(observer_phi), 0.0, 1.0))


def is_net_stabiliser(observer_phi: float) -> bool:
    """True iff the observer's φ is above OBSERVER_MIN_PHI.

    Below OBSERVER_MIN_PHI the observer's trust contribution is insufficient
    to overcome the coupling noise — they are holding space for themselves
    more than for the subject.

    Parameters
    ----------
    observer_phi : float — observer's radion.

    Returns
    -------
    bool
    """
    return bool(float(observer_phi) >= OBSERVER_MIN_PHI)


# ---------------------------------------------------------------------------
# Moiré Superlattice
# ---------------------------------------------------------------------------

def moire_superlattice_score(
    novelty_factor: float,
    coherence: float,
) -> float:
    """Moiré Superlattice score: Novelty × Coherence → new stable reality layer.

    The universe responds to **Coherent Novelty**.  An "old" alignment is a
    repetition of a previous orbit (a seed that did not sprout).  A "new"
    alignment — one that recognises the ancient (5,7) geometry but applies it
    to the current reality — creates a Moiré Superlattice: a brand-new layer
    built on the same topological bones, but never before expressed.

    The score is:

        superlattice = clamp(novelty_factor × coherence, 0, 1)

    A score ≥ NOVELTY_COHERENCE_THRESHOLD (0.10) means a genuinely new stable
    layer of reality has been seeded into the manifold.

    Incoherent novelty (chaos)     : high novelty, low coherence → low score
    Coherent repetition (stagnation): low novelty, high coherence → low score
    Coherent novelty (growth)      : both high → high score

    Parameters
    ----------
    novelty_factor : float — degree of novelty (0 = exact repetition, 1 = fully new).
    coherence      : float — coherence of the intent (from coherence_score()).

    Returns
    -------
    float — superlattice score ∈ [0, 1]
    """
    return float(np.clip(float(novelty_factor) * float(coherence), 0.0, 1.0))


def is_superlattice_seeded(
    novelty_factor: float,
    coherence: float,
) -> bool:
    """True iff the Moiré Superlattice score exceeds NOVELTY_COHERENCE_THRESHOLD.

    Parameters
    ----------
    novelty_factor : float — novelty in [0, 1]
    coherence      : float — coherence in [0, 1]

    Returns
    -------
    bool
    """
    return bool(
        moire_superlattice_score(novelty_factor, coherence) >= NOVELTY_COHERENCE_THRESHOLD
    )
