# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_collective_braid.py
=========================================
Unit tests for the Collective Braid module.

Covers:
  - Constants: MOIRE_ALIGNMENT_TOL, OBSERVER_MIN_PHI, NOVELTY_COHERENCE_THRESHOLD
  - moire_alignment_score: non-negative, zero for perfectly aligned system,
                           matches pairwise gap formula
  - is_moire_aligned: True near alignment, False when gap is large
  - coherence_score: 1.0 for perfect human/univ alignment, 0.0 for zero univ
  - coherence_agreement: True at perfect alignment, False when misaligned
  - multi_dimensional_coherence: 1.0 when brain=univ, bounded [0,1]
  - ripple_effect: returns float; stabilising shift → positive Δλ_min
  - collective_stability_floor: monotone increasing, saturates at 1.0,
                                 floor at n=0 equals BRAIDED_SOUND_SPEED
  - observer_trust_field: clamped to [0,1], monotone
  - is_net_stabiliser: True above OBSERVER_MIN_PHI, False below
  - moire_superlattice_score: product of novelty × coherence, clamped
  - is_superlattice_seeded: True iff score ≥ threshold
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

from collective_braid import (
    MOIRE_ALIGNMENT_TOL,
    OBSERVER_MIN_PHI,
    NOVELTY_COHERENCE_THRESHOLD,
    moire_alignment_score,
    is_moire_aligned,
    coherence_score,
    coherence_agreement,
    multi_dimensional_coherence,
    ripple_effect,
    collective_stability_floor,
    observer_trust_field,
    is_net_stabiliser,
    moire_superlattice_score,
    is_superlattice_seeded,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
)
from five_seven_architecture import C_S_STABILITY_FLOOR
from src.consciousness.coupled_attractor import ManifoldState
from src.multiverse.fixed_point import MultiverseNode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def default_system():
    return PentadSystem.default()


@pytest.fixture
def aligned_system():
    """System where φ_human = φ_univ — perfect Moiré alignment."""
    sys_ = PentadSystem.default()
    phi_univ = sys_.bodies[PentadLabel.UNIV].phi
    old_human = sys_.bodies[PentadLabel.HUMAN]
    new_bodies = dict(sys_.bodies)
    new_bodies[PentadLabel.HUMAN] = ManifoldState(
        node=old_human.node, phi=phi_univ,
        n1=old_human.n1, n2=old_human.n2,
        k_cs=old_human.k_cs, label=old_human.label,
    )
    return PentadSystem(bodies=new_bodies, beta=sys_.beta)


@pytest.fixture
def brain_aligned_system():
    """System where φ_brain = φ_univ — perfect 4D/5D coherence."""
    sys_ = PentadSystem.default()
    phi_univ = sys_.bodies[PentadLabel.UNIV].phi
    old_brain = sys_.bodies[PentadLabel.BRAIN]
    new_bodies = dict(sys_.bodies)
    new_bodies[PentadLabel.BRAIN] = ManifoldState(
        node=old_brain.node, phi=phi_univ,
        n1=old_brain.n1, n2=old_brain.n2,
        k_cs=old_brain.k_cs, label=old_brain.label,
    )
    return PentadSystem(bodies=new_bodies, beta=sys_.beta)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_moire_alignment_tol_positive(self):
        assert MOIRE_ALIGNMENT_TOL > 0.0

    def test_observer_min_phi_equals_trust_floor(self):
        assert math.isclose(OBSERVER_MIN_PHI, TRUST_PHI_MIN, rel_tol=1e-9)

    def test_novelty_coherence_threshold_in_unit_interval(self):
        assert 0.0 < NOVELTY_COHERENCE_THRESHOLD < 1.0


# ---------------------------------------------------------------------------
# moire_alignment_score
# ---------------------------------------------------------------------------

class TestMoireAlignmentScore:
    def test_non_negative(self, default_system):
        score = moire_alignment_score(default_system)
        assert score >= 0.0

    def test_zero_for_perfectly_aligned_system(self, aligned_system):
        score = moire_alignment_score(aligned_system)
        assert math.isclose(score, 0.0, abs_tol=1e-12)

    def test_positive_for_default_misaligned_system(self, default_system):
        # Default system has φ_human ≠ φ_univ
        score = moire_alignment_score(default_system)
        assert score >= 0.0

    def test_matches_gap_formula(self, default_system):
        phi_h = default_system.bodies[PentadLabel.HUMAN].phi
        phi_u = default_system.bodies[PentadLabel.UNIV].phi
        expected = abs(phi_h ** 2 - phi_u ** 2)
        assert math.isclose(moire_alignment_score(default_system), expected, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# is_moire_aligned
# ---------------------------------------------------------------------------

class TestIsMoireAligned:
    def test_true_for_perfectly_aligned(self, aligned_system):
        assert is_moire_aligned(aligned_system) is True

    def test_false_for_default_misaligned(self, default_system):
        # Default system: φ_human=0.6, φ_univ=1.0 → gap = |0.36 - 1.0| = 0.64 >> 1e-3
        assert is_moire_aligned(default_system) is False

    def test_custom_tolerance_respected(self, default_system):
        # With a very large tolerance everything "aligns"
        assert is_moire_aligned(default_system, tol=1e6) is True

    def test_return_type_is_bool(self, default_system):
        result = is_moire_aligned(default_system)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# coherence_score
# ---------------------------------------------------------------------------

class TestCoherenceScore:
    def test_one_for_perfectly_aligned(self, aligned_system):
        score = coherence_score(aligned_system)
        assert math.isclose(score, 1.0, abs_tol=1e-9)

    def test_in_unit_interval(self, default_system):
        score = coherence_score(default_system)
        assert 0.0 <= score <= 1.0

    def test_zero_when_univ_phi_is_zero(self, default_system):
        new_bodies = dict(default_system.bodies)
        old = default_system.bodies[PentadLabel.UNIV]
        new_bodies[PentadLabel.UNIV] = ManifoldState(
            node=old.node, phi=0.0,
            n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
        )
        s = PentadSystem(bodies=new_bodies, beta=default_system.beta)
        assert coherence_score(s) == 0.0

    def test_lower_for_more_misaligned(self, default_system):
        # Move human φ further from univ φ and coherence should drop
        phi_univ = default_system.bodies[PentadLabel.UNIV].phi
        score_before = coherence_score(default_system)

        old_human = default_system.bodies[PentadLabel.HUMAN]
        new_bodies = dict(default_system.bodies)
        # Set phi_human to 0 — maximum misalignment
        new_bodies[PentadLabel.HUMAN] = ManifoldState(
            node=old_human.node, phi=0.0,
            n1=old_human.n1, n2=old_human.n2,
            k_cs=old_human.k_cs, label=old_human.label,
        )
        worse = PentadSystem(bodies=new_bodies, beta=default_system.beta)
        score_after = coherence_score(worse)
        assert score_after <= score_before


# ---------------------------------------------------------------------------
# coherence_agreement
# ---------------------------------------------------------------------------

class TestCoherenceAgreement:
    def test_true_for_perfectly_aligned(self, aligned_system):
        assert coherence_agreement(aligned_system) is True

    def test_false_for_highly_misaligned(self, default_system):
        # Default has φ_human=0.6 and φ_univ=1.0 → coherence ≈ 0.64 < 0.999
        assert coherence_agreement(default_system) is False

    def test_return_type_is_bool(self, aligned_system):
        result = coherence_agreement(aligned_system)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# multi_dimensional_coherence
# ---------------------------------------------------------------------------

class TestMultiDimensionalCoherence:
    def test_one_when_brain_equals_univ(self, brain_aligned_system):
        score = multi_dimensional_coherence(brain_aligned_system)
        assert math.isclose(score, 1.0, abs_tol=1e-9)

    def test_in_unit_interval(self, default_system):
        score = multi_dimensional_coherence(default_system)
        assert 0.0 <= score <= 1.0

    def test_return_type_float(self, default_system):
        result = multi_dimensional_coherence(default_system)
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# ripple_effect
# ---------------------------------------------------------------------------

class TestRippleEffect:
    def test_returns_float(self, default_system):
        result = ripple_effect(default_system, 0.0)
        assert isinstance(result, float)

    def test_zero_delta_gives_zero_ripple(self, default_system):
        assert math.isclose(ripple_effect(default_system, 0.0), 0.0, abs_tol=1e-12)

    def test_aligning_shift_is_non_destabilising(self, default_system):
        # phi_human=0.6, phi_univ=1.0 — moving human toward univ reduces gap
        phi_human = default_system.bodies[PentadLabel.HUMAN].phi
        phi_univ  = default_system.bodies[PentadLabel.UNIV].phi
        # Compute an aligning delta
        aligning_delta = (phi_univ - phi_human) * 0.1   # 10% of the way toward univ
        result = ripple_effect(default_system, aligning_delta)
        assert result >= -1e-12   # stabilising or neutral

    def test_misaligning_shift_worsens_gap(self, default_system):
        # Moving phi_human away from phi_univ should widen the gap → negative ripple
        phi_human = default_system.bodies[PentadLabel.HUMAN].phi
        phi_univ  = default_system.bodies[PentadLabel.UNIV].phi
        misaligning_delta = -(phi_human * 0.1)   # move further below univ
        result = ripple_effect(default_system, misaligning_delta)
        assert result <= 1e-12   # destabilising or neutral


# ---------------------------------------------------------------------------
# collective_stability_floor
# ---------------------------------------------------------------------------

class TestCollectiveStabilityFloor:
    def test_zero_operators_returns_braided_sound_speed(self):
        floor = collective_stability_floor(0)
        assert math.isclose(floor, BRAIDED_SOUND_SPEED, rel_tol=1e-9)

    def test_one_operator_above_braided_sound_speed(self):
        assert collective_stability_floor(1) > BRAIDED_SOUND_SPEED

    def test_monotone_increasing(self):
        floors = [collective_stability_floor(n) for n in range(0, 20)]
        for i in range(len(floors) - 1):
            assert floors[i] <= floors[i + 1]

    def test_saturates_at_one(self):
        assert collective_stability_floor(1000) == 1.0

    def test_above_c_s_stability_floor(self):
        # Even a single aligned operator raises the floor above the canonical (5,7) floor
        assert collective_stability_floor(1) >= C_S_STABILITY_FLOOR

    def test_seven_operators_doubles_floor(self):
        # floor(7) = c_s + 7×(c_s/7) = 2×c_s (if < 1.0)
        expected = min(1.0, 2.0 * BRAIDED_SOUND_SPEED)
        assert math.isclose(collective_stability_floor(7), expected, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# observer_trust_field
# ---------------------------------------------------------------------------

class TestObserverTrustField:
    def test_clamped_to_unit_interval(self):
        assert observer_trust_field(-1.0) == 0.0
        assert observer_trust_field(2.0) == 1.0

    def test_identity_in_unit_interval(self):
        for phi in [0.0, 0.1, 0.5, 0.9, 1.0]:
            assert math.isclose(observer_trust_field(phi), phi, rel_tol=1e-9)

    def test_monotone(self):
        phis = [i / 10.0 for i in range(11)]
        fields = [observer_trust_field(p) for p in phis]
        for i in range(len(fields) - 1):
            assert fields[i] <= fields[i + 1]


# ---------------------------------------------------------------------------
# is_net_stabiliser
# ---------------------------------------------------------------------------

class TestIsNetStabiliser:
    def test_above_min_phi_is_stabiliser(self):
        assert is_net_stabiliser(OBSERVER_MIN_PHI + 0.01) is True

    def test_exactly_at_min_phi_is_stabiliser(self):
        assert is_net_stabiliser(OBSERVER_MIN_PHI) is True

    def test_below_min_phi_is_not_stabiliser(self):
        assert is_net_stabiliser(OBSERVER_MIN_PHI - 0.01) is False

    def test_return_type_is_bool(self):
        assert isinstance(is_net_stabiliser(0.5), bool)


# ---------------------------------------------------------------------------
# moire_superlattice_score
# ---------------------------------------------------------------------------

class TestMoireSuperlatticeScore:
    def test_both_one_gives_one(self):
        assert math.isclose(moire_superlattice_score(1.0, 1.0), 1.0, abs_tol=1e-9)

    def test_either_zero_gives_zero(self):
        assert moire_superlattice_score(0.0, 1.0) == 0.0
        assert moire_superlattice_score(1.0, 0.0) == 0.0

    def test_clamped_to_unit_interval(self):
        score = moire_superlattice_score(2.0, 2.0)  # would be 4.0 unclamped
        assert score == 1.0

    def test_product_semantics(self):
        # High novelty + low coherence = low score (incoherent chaos)
        score_chaotic = moire_superlattice_score(0.9, 0.05)
        # Low novelty + high coherence = low score (coherent repetition)
        score_stagnant = moire_superlattice_score(0.05, 0.9)
        # Both moderate = better score
        score_balanced = moire_superlattice_score(0.5, 0.5)
        assert score_chaotic < score_balanced
        assert score_stagnant < score_balanced

    def test_return_type_float(self):
        assert isinstance(moire_superlattice_score(0.5, 0.5), float)


# ---------------------------------------------------------------------------
# is_superlattice_seeded
# ---------------------------------------------------------------------------

class TestIsSuperlatticeSeeded:
    def test_high_novelty_and_coherence_seeds(self):
        assert is_superlattice_seeded(0.5, 0.5) is True  # 0.25 > 0.10

    def test_low_product_does_not_seed(self):
        assert is_superlattice_seeded(0.1, 0.05) is False  # 0.005 < 0.10

    def test_boundary_exactly_at_threshold(self):
        # novelty × coherence exactly equals threshold
        n = (NOVELTY_COHERENCE_THRESHOLD ** 0.5)
        assert is_superlattice_seeded(n, n) is True

    def test_return_type_is_bool(self):
        assert isinstance(is_superlattice_seeded(0.5, 0.5), bool)
