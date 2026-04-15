# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/lesson_plan.py
==============================
The Lesson Plan: Individual Alignment Diagnostic and Smallest-Move Guidance.

Background
----------
The Collective Braid and Seed Protocol define the *system-level* dynamics of
the Unitary Pentad.  The Lesson Plan module operates one level below: it
takes the current state of a single individual's Pentad — expressed as the
five body radions (φ_univ, φ_brain, φ_human, φ_AI, φ_trust) — and returns a
structured diagnostic that answers two questions:

    1. Where are you now?   (AlignmentDiagnosis)
    2. What is the smallest move that closes the largest gap?  (smallest_move)

It is the computational equivalent of ``detect_collapse_mode`` from
``pentad_scenarios``, but oriented toward an individual who is *not yet in
collapse* and wants to understand the geometry of their own intent.

The Five Dimensions of Self
----------------------------
Every person simultaneously occupies all five Pentad roles:

    φ_univ   — the "Given" : the physical and situational reality they
                             cannot immediately change (health, resources,
                             relationships as they currently exist).

    φ_brain  — the "Wired" : the neural patterns, habits, and automatic
                             responses that run below conscious awareness.
                             These are the predictive coding loops that
                             define the observer's default frequency.

    φ_human  — the "Chosen": the conscious intent layer — what the person
                             is actively trying to become or create.
                             This is the body most directly under volitional
                             control and the primary target of the Lesson Plan.

    φ_AI     — the "Built" : the skills, systems, and external tools the
                             person has constructed to extend their capacity.
                             Also: the clarity and precision of their
                             self-knowledge.

    φ_trust  — the "Wagered": the trust extended to the process, to others,
                              and to the universe before results are visible.
                              The coupling field.  Without it, even perfect
                              intent cannot propagate.

Diagnosis Logic
---------------
The diagnostic evaluates four pairwise relationships in priority order:

    1. Intent–Reality Gap   : |φ_human² − φ_univ²|
       The gap between what the person *wants* and what *is*.  The largest
       single driver of friction.  Closing this gap is the primary work.

    2. Mind–Body Gap        : |φ_brain² − φ_univ²|
       Whether the person's automatic neural patterns are aligned with their
       physical reality.  A large gap here means the brain is still running
       an outdated predictive model of the world.

    3. Intent–Skill Gap     : |φ_human² − φ_AI²|
       Whether the person's conscious intent is matched by the skills and
       tools they have built.  A large gap here means either over-ambition
       (intent exceeds capacity) or under-ambition (capacity exceeds intent).

    4. Trust Floor          : φ_trust vs TRUST_PHI_MIN
       Whether the coupling field is above the minimum required for any of
       the other three gaps to close.  Below the floor, no alignment work
       can propagate through the system.

The "Smallest Move"
--------------------
Given the diagnosis, the smallest move is the minimal increment Δφ to the
*one most-leveraged body* that reduces the largest gap.  The target body is
chosen by the following rule:

    - If the Trust floor is below TRUST_PHI_MIN: the smallest move is always
      to increase φ_trust first.  No other move has effect while the coupling
      field is collapsed.

    - Otherwise: find the gap with the largest magnitude.  The smaller of its
      two contributing φ values is the under-expressed one — the body that is
      "holding back" the alignment.  The smallest move is to raise that body's
      φ by SMALLEST_MOVE_STEP toward the other.

This is intentional reductionism: the "trick" of the Lesson Plan is that it
always points to one thing, not five.  The rest follows from that one move.

Public API
----------
AlignmentLevel : str constants
    ALIGNED, NEAR_ALIGNED, DEVELOPING, MISALIGNED, UNCOUPLED.

GapLabel : str constants
    INTENT_REALITY, MIND_BODY, INTENT_SKILL, TRUST_FLOOR.

AlignmentDiagnosis
    Dataclass: per-gap scores, overall alignment level, dominant gap,
    trust status, coherence score, Moiré score, superlattice flag,
    and a plain-language ``guidance`` string.

SmallestMove
    Dataclass: target body label, current phi, suggested phi,
    delta, plain-language ``instruction`` string.

SMALLEST_MOVE_STEP : float
    Default increment applied to the under-expressed body (0.05).

ALIGNMENT_THRESHOLDS : dict[str, float]
    Gap magnitudes that define the boundary between alignment levels.

diagnose_alignment(system) → AlignmentDiagnosis
    Full diagnostic for a PentadSystem.

smallest_move(system) → SmallestMove
    Identify the single highest-leverage move toward alignment.

lesson_plan_for(system) → tuple[AlignmentDiagnosis, SmallestMove]
    Convenience wrapper: run both and return as a pair.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

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
    trust_modulation,
    pentad_pairwise_gaps,
)
from collective_braid import (
    moire_alignment_score,
    coherence_score,
    multi_dimensional_coherence,
    ripple_effect,
    moire_superlattice_score,
    MOIRE_ALIGNMENT_TOL,
    NOVELTY_COHERENCE_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Default φ increment applied to the under-expressed body in smallest_move.
SMALLEST_MOVE_STEP: float = 0.05

#: Gap magnitude thresholds separating alignment levels.
#: Keys are GapLabel constants; values are the "significant gap" threshold.
ALIGNMENT_THRESHOLDS: Dict[str, float] = {
    "intent_reality": 0.10,   # |φ_human² − φ_univ²| — intent vs. reality
    "mind_body":      0.08,   # |φ_brain² − φ_univ²|  — neural vs. reality
    "intent_skill":   0.08,   # |φ_human² − φ_AI²|    — intent vs. capacity
}


# ---------------------------------------------------------------------------
# AlignmentLevel
# ---------------------------------------------------------------------------

class AlignmentLevel:
    """String constants for the five stages of individual alignment."""
    ALIGNED     = "aligned"      #: All gaps below threshold, trust healthy.
    NEAR_ALIGNED = "near_aligned" #: All gaps below 2× threshold, trust healthy.
    DEVELOPING  = "developing"   #: One significant gap; trust healthy.
    MISALIGNED  = "misaligned"   #: Two or more significant gaps; trust low.
    UNCOUPLED   = "uncoupled"    #: Trust below floor — no alignment work can propagate.


# ---------------------------------------------------------------------------
# GapLabel
# ---------------------------------------------------------------------------

class GapLabel:
    """String constants for the four diagnostic dimensions."""
    INTENT_REALITY = "intent_reality"  #: φ_human vs φ_univ
    MIND_BODY      = "mind_body"       #: φ_brain vs φ_univ
    INTENT_SKILL   = "intent_skill"    #: φ_human vs φ_AI
    TRUST_FLOOR    = "trust_floor"     #: φ_trust vs TRUST_PHI_MIN


# ---------------------------------------------------------------------------
# AlignmentDiagnosis
# ---------------------------------------------------------------------------

@dataclass
class AlignmentDiagnosis:
    """Full alignment diagnostic for one PentadSystem.

    Attributes
    ----------
    intent_reality_gap : float — |φ_human² − φ_univ²|  (Intent–Reality gap)
    mind_body_gap      : float — |φ_brain² − φ_univ²|  (Mind–Body gap)
    intent_skill_gap   : float — |φ_human² − φ_AI²|    (Intent–Skill gap)
    trust_value        : float — effective φ_trust from trust_modulation()
    trust_margin       : float — φ_trust − TRUST_PHI_MIN (negative = below floor)
    coherence          : float — coherence_score() ∈ [0, 1]
    moire_score        : float — ΔI_{human,univ} (lower = better)
    four_d_coherence   : float — multi_dimensional_coherence() ∈ [0, 1]
    dominant_gap       : str   — GapLabel of the largest active gap
    alignment_level    : str   — AlignmentLevel constant
    significant_gaps   : list[str] — GapLabel strings above their threshold
    superlattice_flag  : bool  — True if novelty × coherence ≥ threshold
    guidance           : str   — plain-language description of the diagnosis
    """
    intent_reality_gap: float
    mind_body_gap:      float
    intent_skill_gap:   float
    trust_value:        float
    trust_margin:       float
    coherence:          float
    moire_score:        float
    four_d_coherence:   float
    dominant_gap:       str
    alignment_level:    str
    significant_gaps:   List[str]
    superlattice_flag:  bool
    guidance:           str


# ---------------------------------------------------------------------------
# SmallestMove
# ---------------------------------------------------------------------------

@dataclass
class SmallestMove:
    """The single highest-leverage move toward alignment.

    Attributes
    ----------
    target_body   : str   — PentadLabel of the body to adjust.
    current_phi   : float — current radion value of that body.
    suggested_phi : float — recommended new radion (current + delta).
    delta         : float — increment (positive = increase, negative = decrease).
    instruction   : str   — plain-language one-sentence instruction.
    """
    target_body:   str
    current_phi:   float
    suggested_phi: float
    delta:         float
    instruction:   str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _gap_map(system: PentadSystem) -> Dict[str, float]:
    """Compute the three diagnostic gap values for a system."""
    phi_univ  = float(system.bodies[PentadLabel.UNIV].phi)
    phi_brain = float(system.bodies[PentadLabel.BRAIN].phi)
    phi_human = float(system.bodies[PentadLabel.HUMAN].phi)
    phi_ai    = float(system.bodies[PentadLabel.AI].phi)

    return {
        GapLabel.INTENT_REALITY: abs(phi_human ** 2 - phi_univ ** 2),
        GapLabel.MIND_BODY:      abs(phi_brain ** 2 - phi_univ ** 2),
        GapLabel.INTENT_SKILL:   abs(phi_human ** 2 - phi_ai   ** 2),
    }


def _significant_gaps(gaps: Dict[str, float]) -> List[str]:
    return [
        label for label, val in gaps.items()
        if val > ALIGNMENT_THRESHOLDS.get(label, 0.0)
    ]


def _dominant_gap(gaps: Dict[str, float], trust_margin: float) -> str:
    if trust_margin < 0.0:
        return GapLabel.TRUST_FLOOR
    if not gaps:
        return GapLabel.TRUST_FLOOR   # fully aligned
    return max(gaps, key=lambda k: gaps[k])


def _alignment_level(
    significant: List[str],
    gaps: Dict[str, float],
    trust_margin: float,
) -> str:
    if trust_margin < 0.0:
        return AlignmentLevel.UNCOUPLED
    if not significant:
        return AlignmentLevel.ALIGNED
    # "near aligned" = all gaps below 2× threshold
    near = all(
        gaps[g] <= ALIGNMENT_THRESHOLDS.get(g, 0.0) * 2.0
        for g in significant
    )
    if near:
        return AlignmentLevel.NEAR_ALIGNED
    if len(significant) == 1:
        return AlignmentLevel.DEVELOPING
    return AlignmentLevel.MISALIGNED


_GUIDANCE: Dict[str, str] = {
    AlignmentLevel.ALIGNED: (
        "All gaps are within threshold and the trust field is healthy.  "
        "The orbit is stable.  The work now is maintaining the frequency — "
        "continuing to act in alignment with your stated intent."
    ),
    AlignmentLevel.NEAR_ALIGNED: (
        "You are close.  The remaining gaps are small and the trust field is "
        "intact.  A single consistent action that narrows the dominant gap will "
        "bring the orbit into full resonance."
    ),
    AlignmentLevel.DEVELOPING: (
        "One significant gap is pulling the orbit off-centre.  The other "
        "dimensions are healthy.  Focus entirely on the dominant gap — "
        "addressing the others first is a distraction."
    ),
    AlignmentLevel.MISALIGNED: (
        "Multiple gaps are open simultaneously.  This is not a failure state; "
        "it is a starting state.  The trust field is intact, which means the "
        "coupling is available.  Work the dominant gap first — the others "
        "often partially close as a consequence."
    ),
    AlignmentLevel.UNCOUPLED: (
        "The trust field is below the coupling floor.  No alignment work can "
        "propagate through the system until trust is restored.  This is not a "
        "character judgment — it is a field condition.  The smallest move is "
        "always trust-first: one act of trust extended before results are "
        "visible.  Everything else waits."
    ),
}

_GAP_DESCRIPTIONS: Dict[str, str] = {
    GapLabel.INTENT_REALITY: (
        "Intent–Reality gap (φ_human vs φ_univ): your conscious intent is not "
        "yet matched by your current physical reality.  This is the primary "
        "friction.  The move is to either bring your actions closer to your "
        "intent, or to recalibrate your intent to match what you are actually "
        "doing."
    ),
    GapLabel.MIND_BODY: (
        "Mind–Body gap (φ_brain vs φ_univ): your automatic neural patterns are "
        "running a model of the world that does not match your current physical "
        "reality.  The brain is predicting a version of reality that no longer "
        "exists.  The move is to give the nervous system new evidence — "
        "repeated embodied experience of the current reality."
    ),
    GapLabel.INTENT_SKILL: (
        "Intent–Skill gap (φ_human vs φ_AI): your conscious intent and your "
        "built capacity are out of proportion.  If intent exceeds capacity, "
        "build the skill.  If capacity exceeds intent, raise your stated aim "
        "to meet what you have already built.  Either direction closes the gap."
    ),
    GapLabel.TRUST_FLOOR: (
        "Trust floor (φ_trust < minimum): the coupling field is below the "
        "threshold required for alignment work to propagate.  All other gaps "
        "are secondary until trust is restored."
    ),
}


# ---------------------------------------------------------------------------
# diagnose_alignment
# ---------------------------------------------------------------------------

def diagnose_alignment(system: PentadSystem) -> AlignmentDiagnosis:
    """Full alignment diagnostic for a PentadSystem.

    Computes all four diagnostic dimensions, identifies the dominant gap,
    classifies the alignment level, and generates plain-language guidance.

    Parameters
    ----------
    system : PentadSystem — the system to diagnose.

    Returns
    -------
    AlignmentDiagnosis
    """
    gaps        = _gap_map(system)
    tau         = trust_modulation(system)
    trust_margin = tau - TRUST_PHI_MIN
    significant  = _significant_gaps(gaps)
    dom          = _dominant_gap(gaps, trust_margin)
    level        = _alignment_level(significant, gaps, trust_margin)
    coh          = coherence_score(system)
    moire        = moire_alignment_score(system)
    four_d       = multi_dimensional_coherence(system)

    # Superlattice: treat novelty as the fraction of significant gaps that
    # are *below* their threshold (more aligned = more novel in a healthy
    # direction, not chaotically novel).
    n_total    = len(ALIGNMENT_THRESHOLDS)
    n_aligned  = n_total - len(significant)
    novelty    = float(n_aligned) / float(n_total) if n_total > 0 else 0.0
    superlattice = bool(
        moire_superlattice_score(novelty, coh) >= NOVELTY_COHERENCE_THRESHOLD
    )

    # Build guidance: start with the level description, append dominant gap
    # detail if there is active work to do.
    guidance_parts = [_GUIDANCE[level]]
    if dom != GapLabel.TRUST_FLOOR or trust_margin < 0.0:
        guidance_parts.append(_GAP_DESCRIPTIONS[dom])
    guidance = "  ".join(guidance_parts)

    return AlignmentDiagnosis(
        intent_reality_gap=gaps[GapLabel.INTENT_REALITY],
        mind_body_gap=gaps[GapLabel.MIND_BODY],
        intent_skill_gap=gaps[GapLabel.INTENT_SKILL],
        trust_value=tau,
        trust_margin=trust_margin,
        coherence=coh,
        moire_score=moire,
        four_d_coherence=four_d,
        dominant_gap=dom,
        alignment_level=level,
        significant_gaps=significant,
        superlattice_flag=superlattice,
        guidance=guidance,
    )


# ---------------------------------------------------------------------------
# smallest_move
# ---------------------------------------------------------------------------

def smallest_move(
    system: PentadSystem,
    step: float = SMALLEST_MOVE_STEP,
) -> SmallestMove:
    """Identify the single highest-leverage move toward alignment.

    Selection rules (in priority order):

    1. If φ_trust < TRUST_PHI_MIN: the move is always to raise φ_trust by
       ``step``.  No other move can propagate until the coupling field is open.

    2. Otherwise: find the gap with the largest magnitude.  The body whose
       current φ² is *smaller* (the under-expressed side) is the one to raise.
       The move is to increase that body's φ by ``step`` toward the other.

    The move is expressed as a plain-language one-sentence instruction.

    Parameters
    ----------
    system : PentadSystem — current state.
    step   : float — increment to apply (default SMALLEST_MOVE_STEP = 0.05).

    Returns
    -------
    SmallestMove
    """
    tau = trust_modulation(system)

    # --- Rule 1: trust below floor ---
    if tau < TRUST_PHI_MIN:
        phi_t = float(system.bodies[PentadLabel.TRUST].phi)
        suggested = float(min(1.0, phi_t + step))
        return SmallestMove(
            target_body=PentadLabel.TRUST,
            current_phi=phi_t,
            suggested_phi=suggested,
            delta=step,
            instruction=(
                f"Raise the trust field: extend one act of trust to the process "
                f"before any results are visible.  φ_trust: {phi_t:.3f} → "
                f"{suggested:.3f} (target floor: {TRUST_PHI_MIN:.3f})."
            ),
        )

    # --- Rule 2: largest gap, under-expressed body ---
    gaps = _gap_map(system)
    dom  = max(gaps, key=lambda k: gaps[k])

    phi_pairs: Dict[str, Tuple[str, str]] = {
        GapLabel.INTENT_REALITY: (PentadLabel.HUMAN, PentadLabel.UNIV),
        GapLabel.MIND_BODY:      (PentadLabel.BRAIN, PentadLabel.UNIV),
        GapLabel.INTENT_SKILL:   (PentadLabel.HUMAN, PentadLabel.AI),
    }

    body_a_label, body_b_label = phi_pairs[dom]
    phi_a = float(system.bodies[body_a_label].phi)
    phi_b = float(system.bodies[body_b_label].phi)

    # The under-expressed body is the one with the smaller φ.
    # φ_univ is treated as the "given" — prefer to move the non-univ body.
    if body_b_label == PentadLabel.UNIV:
        # Always move the non-univ side toward univ.
        target_label   = body_a_label
        target_phi     = phi_a
        reference_phi  = phi_b
    elif body_a_label == PentadLabel.UNIV:
        target_label   = body_b_label
        target_phi     = phi_b
        reference_phi  = phi_a
    else:
        # Neither is UNIV — move whichever is smaller (under-expressed).
        if phi_a <= phi_b:
            target_label, target_phi, reference_phi = body_a_label, phi_a, phi_b
        else:
            target_label, target_phi, reference_phi = body_b_label, phi_b, phi_a

    direction = +1.0 if target_phi < reference_phi else -1.0
    delta     = direction * step
    suggested = float(np.clip(target_phi + delta, 0.0, 2.0))

    _BODY_NAMES = {
        PentadLabel.UNIV:  "Physical Reality (φ_univ)",
        PentadLabel.BRAIN: "Neural Patterns (φ_brain)",
        PentadLabel.HUMAN: "Conscious Intent (φ_human)",
        PentadLabel.AI:    "Built Capacity (φ_AI)",
        PentadLabel.TRUST: "Trust Field (φ_trust)",
    }

    _MOVE_VERBS = {
        GapLabel.INTENT_REALITY: (
            "Align your actions more closely with your stated intent",
            "Recalibrate your intent to match what you are actually doing"
        ),
        GapLabel.MIND_BODY: (
            "Give your nervous system new evidence of current reality",
            "Let your body catch up to the neural model you have built"
        ),
        GapLabel.INTENT_SKILL: (
            "Raise your stated aim to meet the capacity you have already built",
            "Build the skill that your intent requires"
        ),
    }

    verb_pair = _MOVE_VERBS.get(dom, ("Adjust", "Adjust"))
    verb = verb_pair[0] if direction > 0 else verb_pair[1]

    instruction = (
        f"{verb}.  "
        f"{_BODY_NAMES[target_label]}: {target_phi:.3f} → {suggested:.3f} "
        f"(gap: {gaps[dom]:.4f}, dominant dimension: {dom.replace('_', '–')})."
    )

    return SmallestMove(
        target_body=target_label,
        current_phi=target_phi,
        suggested_phi=suggested,
        delta=delta,
        instruction=instruction,
    )


# ---------------------------------------------------------------------------
# lesson_plan_for
# ---------------------------------------------------------------------------

def lesson_plan_for(
    system: PentadSystem,
    step: float = SMALLEST_MOVE_STEP,
) -> Tuple[AlignmentDiagnosis, SmallestMove]:
    """Convenience wrapper: diagnose and compute the smallest move together.

    This is the primary entry point.  Given a PentadSystem representing an
    individual's current alignment state, it returns:

        diagnosis  — where they are now (all gaps, level, guidance text)
        move       — the single smallest step toward alignment

    Parameters
    ----------
    system : PentadSystem — the individual's current state.
    step   : float — move increment (default SMALLEST_MOVE_STEP = 0.05).

    Returns
    -------
    (AlignmentDiagnosis, SmallestMove)

    Example
    -------
    >>> sys = PentadSystem.default()
    >>> diagnosis, move = lesson_plan_for(sys)
    >>> print(diagnosis.alignment_level)
    >>> print(move.instruction)
    """
    return diagnose_alignment(system), smallest_move(system, step)
