# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_lesson_plan.py
====================================
Unit tests for the Lesson Plan: Individual Alignment Diagnostic.

Covers:
  - Constants: SMALLEST_MOVE_STEP, ALIGNMENT_THRESHOLDS keys
  - AlignmentLevel: all five string constants defined and distinct
  - GapLabel: all four string constants defined and distinct
  - AlignmentDiagnosis: field types, level semantics
  - SmallestMove: field types, delta sign, suggested_phi clamp
  - diagnose_alignment: default system, fully aligned system,
                        uncoupled (zero-trust) system, each dominant gap
  - smallest_move: trust-first rule, dominant gap selection,
                   non-univ body preferred, step parameter respected
  - lesson_plan_for: returns (AlignmentDiagnosis, SmallestMove) pair,
                     consistent with individual calls
"""

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
import pytest
import numpy as np

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from lesson_plan import (
    SMALLEST_MOVE_STEP,
    ALIGNMENT_THRESHOLDS,
    AlignmentLevel,
    GapLabel,
    AlignmentDiagnosis,
    SmallestMove,
    diagnose_alignment,
    smallest_move,
    lesson_plan_for,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
)
from src.consciousness.coupled_attractor import ManifoldState
from src.multiverse.fixed_point import MultiverseNode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def default_system():
    return PentadSystem.default()


def _set_phi(system: PentadSystem, label: str, phi: float) -> PentadSystem:
    """Return a copy with one body's φ replaced."""
    new_bodies = dict(system.bodies)
    old = system.bodies[label]
    new_bodies[label] = ManifoldState(
        node=old.node, phi=float(phi),
        n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
    )
    return PentadSystem(bodies=new_bodies, beta=system.beta)


@pytest.fixture
def zero_trust_system(default_system):
    return _set_phi(default_system, PentadLabel.TRUST, 0.0)


@pytest.fixture
def fully_aligned_system(default_system):
    """All five φ set equal — every gap is zero, trust is healthy."""
    phi = 0.8
    s = default_system
    for label in PENTAD_LABELS:
        s = _set_phi(s, label, phi)
    return s


@pytest.fixture
def intent_reality_dominant(default_system):
    """φ_human far from φ_univ; other gaps small."""
    s = default_system
    s = _set_phi(s, PentadLabel.UNIV,  1.0)
    s = _set_phi(s, PentadLabel.HUMAN, 0.1)   # gap = |0.01 - 1.0| = 0.99
    s = _set_phi(s, PentadLabel.BRAIN, 1.0)   # mind_body gap = 0
    s = _set_phi(s, PentadLabel.AI,    0.1)   # intent_skill gap = 0 (same as human)
    return s


@pytest.fixture
def mind_body_dominant(default_system):
    """φ_brain far from φ_univ; intent matches univ; intent_skill small."""
    s = default_system
    s = _set_phi(s, PentadLabel.UNIV,  1.0)
    s = _set_phi(s, PentadLabel.HUMAN, 1.0)   # intent_reality gap = 0
    s = _set_phi(s, PentadLabel.AI,    1.0)   # intent_skill gap = 0
    s = _set_phi(s, PentadLabel.BRAIN, 0.1)   # mind_body gap = 0.99
    return s


@pytest.fixture
def intent_skill_dominant(default_system):
    """φ_AI far from φ_human; intent and univ match each other; brain matches."""
    s = default_system
    s = _set_phi(s, PentadLabel.UNIV,  1.0)
    s = _set_phi(s, PentadLabel.HUMAN, 1.0)   # intent_reality gap = 0
    s = _set_phi(s, PentadLabel.BRAIN, 1.0)   # mind_body gap = 0
    s = _set_phi(s, PentadLabel.AI,    0.1)   # intent_skill gap = 0.99
    return s


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_smallest_move_step_positive(self):
        assert SMALLEST_MOVE_STEP > 0.0

    def test_alignment_thresholds_has_three_keys(self):
        expected = {GapLabel.INTENT_REALITY, GapLabel.MIND_BODY, GapLabel.INTENT_SKILL}
        assert set(ALIGNMENT_THRESHOLDS.keys()) == expected

    def test_all_thresholds_positive(self):
        for val in ALIGNMENT_THRESHOLDS.values():
            assert val > 0.0


# ---------------------------------------------------------------------------
# AlignmentLevel
# ---------------------------------------------------------------------------

class TestAlignmentLevel:
    def test_all_five_defined(self):
        assert AlignmentLevel.ALIGNED
        assert AlignmentLevel.NEAR_ALIGNED
        assert AlignmentLevel.DEVELOPING
        assert AlignmentLevel.MISALIGNED
        assert AlignmentLevel.UNCOUPLED

    def test_all_distinct(self):
        levels = [
            AlignmentLevel.ALIGNED,
            AlignmentLevel.NEAR_ALIGNED,
            AlignmentLevel.DEVELOPING,
            AlignmentLevel.MISALIGNED,
            AlignmentLevel.UNCOUPLED,
        ]
        assert len(set(levels)) == 5


# ---------------------------------------------------------------------------
# GapLabel
# ---------------------------------------------------------------------------

class TestGapLabel:
    def test_all_four_defined(self):
        assert GapLabel.INTENT_REALITY
        assert GapLabel.MIND_BODY
        assert GapLabel.INTENT_SKILL
        assert GapLabel.TRUST_FLOOR

    def test_all_distinct(self):
        labels = [
            GapLabel.INTENT_REALITY,
            GapLabel.MIND_BODY,
            GapLabel.INTENT_SKILL,
            GapLabel.TRUST_FLOOR,
        ]
        assert len(set(labels)) == 4


# ---------------------------------------------------------------------------
# diagnose_alignment — field types and basic invariants
# ---------------------------------------------------------------------------

class TestDiagnoseAlignmentTypes:
    def test_returns_alignment_diagnosis(self, default_system):
        result = diagnose_alignment(default_system)
        assert isinstance(result, AlignmentDiagnosis)

    def test_gaps_non_negative(self, default_system):
        d = diagnose_alignment(default_system)
        assert d.intent_reality_gap >= 0.0
        assert d.mind_body_gap >= 0.0
        assert d.intent_skill_gap >= 0.0

    def test_trust_value_in_unit_interval(self, default_system):
        d = diagnose_alignment(default_system)
        assert 0.0 <= d.trust_value <= 1.0

    def test_coherence_in_unit_interval(self, default_system):
        d = diagnose_alignment(default_system)
        assert 0.0 <= d.coherence <= 1.0

    def test_moire_score_non_negative(self, default_system):
        d = diagnose_alignment(default_system)
        assert d.moire_score >= 0.0

    def test_four_d_coherence_in_unit_interval(self, default_system):
        d = diagnose_alignment(default_system)
        assert 0.0 <= d.four_d_coherence <= 1.0

    def test_alignment_level_is_known_constant(self, default_system):
        d = diagnose_alignment(default_system)
        valid = {
            AlignmentLevel.ALIGNED,
            AlignmentLevel.NEAR_ALIGNED,
            AlignmentLevel.DEVELOPING,
            AlignmentLevel.MISALIGNED,
            AlignmentLevel.UNCOUPLED,
        }
        assert d.alignment_level in valid

    def test_dominant_gap_is_known_label(self, default_system):
        d = diagnose_alignment(default_system)
        valid = {
            GapLabel.INTENT_REALITY,
            GapLabel.MIND_BODY,
            GapLabel.INTENT_SKILL,
            GapLabel.TRUST_FLOOR,
        }
        assert d.dominant_gap in valid

    def test_guidance_is_nonempty_string(self, default_system):
        d = diagnose_alignment(default_system)
        assert isinstance(d.guidance, str)
        assert len(d.guidance) > 10

    def test_significant_gaps_is_list(self, default_system):
        d = diagnose_alignment(default_system)
        assert isinstance(d.significant_gaps, list)

    def test_superlattice_flag_is_bool(self, default_system):
        d = diagnose_alignment(default_system)
        assert isinstance(d.superlattice_flag, bool)


# ---------------------------------------------------------------------------
# diagnose_alignment — alignment level semantics
# ---------------------------------------------------------------------------

class TestDiagnoseAlignmentLevels:
    def test_fully_aligned_system_is_aligned(self, fully_aligned_system):
        d = diagnose_alignment(fully_aligned_system)
        assert d.alignment_level == AlignmentLevel.ALIGNED
        assert d.significant_gaps == []

    def test_zero_trust_is_uncoupled(self, zero_trust_system):
        d = diagnose_alignment(zero_trust_system)
        assert d.alignment_level == AlignmentLevel.UNCOUPLED
        assert d.trust_margin < 0.0

    def test_intent_reality_dominant_gap(self, intent_reality_dominant):
        d = diagnose_alignment(intent_reality_dominant)
        assert d.dominant_gap == GapLabel.INTENT_REALITY
        assert GapLabel.INTENT_REALITY in d.significant_gaps

    def test_mind_body_dominant_gap(self, mind_body_dominant):
        d = diagnose_alignment(mind_body_dominant)
        assert d.dominant_gap == GapLabel.MIND_BODY
        assert GapLabel.MIND_BODY in d.significant_gaps

    def test_intent_skill_dominant_gap(self, intent_skill_dominant):
        d = diagnose_alignment(intent_skill_dominant)
        assert d.dominant_gap == GapLabel.INTENT_SKILL
        assert GapLabel.INTENT_SKILL in d.significant_gaps

    def test_fully_aligned_has_no_significant_gaps(self, fully_aligned_system):
        d = diagnose_alignment(fully_aligned_system)
        assert d.significant_gaps == []

    def test_intent_reality_gap_formula(self, default_system):
        phi_h = default_system.bodies[PentadLabel.HUMAN].phi
        phi_u = default_system.bodies[PentadLabel.UNIV].phi
        expected = abs(phi_h ** 2 - phi_u ** 2)
        d = diagnose_alignment(default_system)
        assert math.isclose(d.intent_reality_gap, expected, rel_tol=1e-9)

    def test_mind_body_gap_formula(self, default_system):
        phi_b = default_system.bodies[PentadLabel.BRAIN].phi
        phi_u = default_system.bodies[PentadLabel.UNIV].phi
        expected = abs(phi_b ** 2 - phi_u ** 2)
        d = diagnose_alignment(default_system)
        assert math.isclose(d.mind_body_gap, expected, rel_tol=1e-9)

    def test_intent_skill_gap_formula(self, default_system):
        phi_h = default_system.bodies[PentadLabel.HUMAN].phi
        phi_a = default_system.bodies[PentadLabel.AI].phi
        expected = abs(phi_h ** 2 - phi_a ** 2)
        d = diagnose_alignment(default_system)
        assert math.isclose(d.intent_skill_gap, expected, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# smallest_move — field types and invariants
# ---------------------------------------------------------------------------

class TestSmallestMoveTypes:
    def test_returns_smallest_move(self, default_system):
        result = smallest_move(default_system)
        assert isinstance(result, SmallestMove)

    def test_target_body_is_pentad_label(self, default_system):
        m = smallest_move(default_system)
        assert m.target_body in PENTAD_LABELS

    def test_suggested_phi_clamped(self, default_system):
        m = smallest_move(default_system)
        assert 0.0 <= m.suggested_phi <= 2.0

    def test_delta_matches_suggested_minus_current(self, default_system):
        m = smallest_move(default_system)
        assert math.isclose(m.suggested_phi, m.current_phi + m.delta, rel_tol=1e-9)

    def test_instruction_is_nonempty_string(self, default_system):
        m = smallest_move(default_system)
        assert isinstance(m.instruction, str)
        assert len(m.instruction) > 10


# ---------------------------------------------------------------------------
# smallest_move — trust-first rule
# ---------------------------------------------------------------------------

class TestSmallestMoveTrustFirst:
    def test_zero_trust_targets_trust_body(self, zero_trust_system):
        m = smallest_move(zero_trust_system)
        assert m.target_body == PentadLabel.TRUST

    def test_zero_trust_raises_phi_trust(self, zero_trust_system):
        m = smallest_move(zero_trust_system)
        assert m.delta > 0.0
        assert m.suggested_phi > m.current_phi

    def test_trust_instruction_mentions_trust(self, zero_trust_system):
        m = smallest_move(zero_trust_system)
        assert "trust" in m.instruction.lower()


# ---------------------------------------------------------------------------
# smallest_move — dominant gap selection
# ---------------------------------------------------------------------------

class TestSmallestMoveDominantGap:
    def test_intent_reality_dominant_moves_human(self, intent_reality_dominant):
        # φ_human=0.1 < φ_univ=1.0 — should raise φ_human
        m = smallest_move(intent_reality_dominant)
        assert m.target_body == PentadLabel.HUMAN
        assert m.delta > 0.0

    def test_mind_body_dominant_moves_brain(self, mind_body_dominant):
        # φ_brain=0.1 < φ_univ=1.0 — should raise φ_brain
        m = smallest_move(mind_body_dominant)
        assert m.target_body == PentadLabel.BRAIN
        assert m.delta > 0.0

    def test_intent_skill_dominant_moves_under_expressed(self, intent_skill_dominant):
        # φ_AI=0.1 < φ_human=1.0 — should raise φ_AI
        m = smallest_move(intent_skill_dominant)
        assert m.target_body == PentadLabel.AI
        assert m.delta > 0.0

    def test_step_parameter_respected(self, default_system):
        custom_step = 0.02
        m = smallest_move(default_system, step=custom_step)
        assert math.isclose(abs(m.delta), custom_step, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# lesson_plan_for
# ---------------------------------------------------------------------------

class TestLessonPlanFor:
    def test_returns_tuple_of_two(self, default_system):
        result = lesson_plan_for(default_system)
        assert len(result) == 2

    def test_first_element_is_diagnosis(self, default_system):
        d, _ = lesson_plan_for(default_system)
        assert isinstance(d, AlignmentDiagnosis)

    def test_second_element_is_move(self, default_system):
        _, m = lesson_plan_for(default_system)
        assert isinstance(m, SmallestMove)

    def test_consistent_with_individual_calls(self, default_system):
        d_direct = diagnose_alignment(default_system)
        m_direct = smallest_move(default_system)
        d_wrap, m_wrap = lesson_plan_for(default_system)
        assert d_wrap.alignment_level == d_direct.alignment_level
        assert m_wrap.target_body == m_direct.target_body

    def test_step_forwarded_to_smallest_move(self, default_system):
        custom_step = 0.03
        _, m = lesson_plan_for(default_system, step=custom_step)
        assert math.isclose(abs(m.delta), custom_step, rel_tol=1e-9)
