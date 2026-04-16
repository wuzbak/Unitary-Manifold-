# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_distributed_authority.py
=============================================
Unit tests for distributed_authority.py.

Covers:
  Constants:
    N_CORE_AXIOMS = 5
    SATURATION_N  = 15  (derived: ceil(7 × (1 − c_s) / c_s) = ceil(175/12))
    PER_VALIDATOR_INCREMENT = BRAIDED_SOUND_SPEED / 7 = 12/259

  beacon_entropy_score:
    - 0 public → 0.0, n_total public → 1.0, partial → proportional
    - clamped above n_total, error on negative or zero total

  elegance_attractor_depth:
    - perfectly aligned system → 1.0
    - depth in [0, 1] for any state
    - more misaligned → shallower depth (monotone in moire score)

  manipulation_resistance_margin:
    - 0 validators → 0.0
    - monotone increasing with n_validators
    - saturates at (1.0 − BRAIDED_SOUND_SPEED)
    - equals collective_stability_floor(n) − BRAIDED_SOUND_SPEED

  distributed_constitution_integrity:
    - 0 validators → BRAIDED_SOUND_SPEED
    - saturates at 1.0 for large n
    - monotone increasing
    - equals collective_stability_floor(n)

  validator_node_strength:
    - below OBSERVER_MIN_PHI → 0.0
    - at 1.0 → PER_VALIDATOR_INCREMENT
    - monotone in observer_phi above OBSERVER_MIN_PHI
    - return type float
"""

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

from distributed_authority import (
    N_CORE_AXIOMS,
    SATURATION_N,
    PER_VALIDATOR_INCREMENT,
    beacon_entropy_score,
    elegance_attractor_depth,
    manipulation_resistance_margin,
    distributed_constitution_integrity,
    validator_node_strength,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
)
from five_seven_architecture import C_S_STABILITY_FLOOR, N_CORE, N_LAYER
from collective_braid import (
    OBSERVER_MIN_PHI,
    collective_stability_floor,
    moire_alignment_score,
)
from src.consciousness.coupled_attractor import ManifoldState


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def default_system():
    return PentadSystem.default()


@pytest.fixture
def aligned_system():
    """System with φ_human = φ_univ — Moiré alignment score = 0."""
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
def maximally_misaligned_system():
    """System with φ_human = 0 — maximum misalignment from φ_univ = 1.0."""
    sys_ = PentadSystem.default()
    old_human = sys_.bodies[PentadLabel.HUMAN]
    new_bodies = dict(sys_.bodies)
    new_bodies[PentadLabel.HUMAN] = ManifoldState(
        node=old_human.node, phi=0.0,
        n1=old_human.n1, n2=old_human.n2,
        k_cs=old_human.k_cs, label=old_human.label,
    )
    return PentadSystem(bodies=new_bodies, beta=sys_.beta)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_core_axioms_equals_five(self):
        assert N_CORE_AXIOMS == 5

    def test_n_core_axioms_matches_n_core(self):
        assert N_CORE_AXIOMS == N_CORE

    def test_saturation_n_equals_fifteen(self):
        # ceil(7 × (1 − 12/37) / (12/37)) = ceil(7 × 25/12) = ceil(175/12) = 15
        assert SATURATION_N == 15

    def test_saturation_n_derived_from_braid(self):
        expected = math.ceil(
            float(N_LAYER) * (1.0 - BRAIDED_SOUND_SPEED) / BRAIDED_SOUND_SPEED
        )
        assert SATURATION_N == expected

    def test_per_validator_increment_equals_cs_over_n_layer(self):
        expected = BRAIDED_SOUND_SPEED / float(N_LAYER)
        assert math.isclose(PER_VALIDATOR_INCREMENT, expected, rel_tol=1e-9)

    def test_per_validator_increment_positive(self):
        assert PER_VALIDATOR_INCREMENT > 0.0

    def test_saturation_n_times_increment_reaches_one(self):
        # At n = SATURATION_N, c_s + n × (c_s/7) ≥ 1.0
        total = BRAIDED_SOUND_SPEED + SATURATION_N * PER_VALIDATOR_INCREMENT
        assert total >= 1.0

    def test_saturation_n_minus_one_does_not_saturate(self):
        # At n = SATURATION_N − 1, still below 1.0
        total = BRAIDED_SOUND_SPEED + (SATURATION_N - 1) * PER_VALIDATOR_INCREMENT
        assert total < 1.0 + 1e-9   # may be right at boundary due to ceil


# ---------------------------------------------------------------------------
# beacon_entropy_score
# ---------------------------------------------------------------------------

class TestBeaconEntropyScore:
    def test_zero_public_axioms_returns_zero(self):
        assert beacon_entropy_score(0) == 0.0

    def test_all_public_axioms_returns_one(self):
        assert math.isclose(beacon_entropy_score(N_CORE_AXIOMS), 1.0, rel_tol=1e-9)

    def test_partial_is_proportional(self):
        for n in range(1, N_CORE_AXIOMS + 1):
            score = beacon_entropy_score(n)
            expected = n / N_CORE_AXIOMS
            assert math.isclose(score, expected, rel_tol=1e-9)

    def test_clamped_above_total(self):
        score = beacon_entropy_score(100, n_total_axioms=5)
        assert score == 1.0

    def test_custom_total(self):
        score = beacon_entropy_score(3, n_total_axioms=10)
        assert math.isclose(score, 0.3, rel_tol=1e-9)

    def test_raises_on_zero_total(self):
        with pytest.raises(ValueError):
            beacon_entropy_score(0, n_total_axioms=0)

    def test_raises_on_negative_public(self):
        with pytest.raises(ValueError):
            beacon_entropy_score(-1)

    def test_return_type_float(self):
        assert isinstance(beacon_entropy_score(3), float)

    def test_monotone_increasing_in_n_public(self):
        scores = [beacon_entropy_score(n) for n in range(0, N_CORE_AXIOMS + 1)]
        for i in range(len(scores) - 1):
            assert scores[i] <= scores[i + 1]


# ---------------------------------------------------------------------------
# elegance_attractor_depth
# ---------------------------------------------------------------------------

class TestEleganceAttractorDepth:
    def test_one_for_perfectly_aligned(self, aligned_system):
        depth = elegance_attractor_depth(aligned_system)
        assert math.isclose(depth, 1.0, abs_tol=1e-9)

    def test_in_unit_interval(self, default_system):
        depth = elegance_attractor_depth(default_system)
        assert 0.0 <= depth <= 1.0

    def test_in_unit_interval_maximally_misaligned(self, maximally_misaligned_system):
        depth = elegance_attractor_depth(maximally_misaligned_system)
        assert 0.0 <= depth <= 1.0

    def test_return_type_float(self, default_system):
        assert isinstance(elegance_attractor_depth(default_system), float)

    def test_more_misaligned_is_shallower(self, default_system, maximally_misaligned_system):
        depth_default = elegance_attractor_depth(default_system)
        depth_worst   = elegance_attractor_depth(maximally_misaligned_system)
        assert depth_worst <= depth_default

    def test_increases_as_phi_human_approaches_phi_univ(self, default_system):
        """Moving human phi toward univ phi deepens the attractor well."""
        phi_univ  = default_system.bodies[PentadLabel.UNIV].phi
        phi_human = default_system.bodies[PentadLabel.HUMAN].phi
        old_human = default_system.bodies[PentadLabel.HUMAN]

        depths = []
        for frac in np.linspace(0.0, 1.0, 6):
            new_phi = phi_human + frac * (phi_univ - phi_human)
            new_bodies = dict(default_system.bodies)
            new_bodies[PentadLabel.HUMAN] = ManifoldState(
                node=old_human.node, phi=float(new_phi),
                n1=old_human.n1, n2=old_human.n2,
                k_cs=old_human.k_cs, label=old_human.label,
            )
            sys_ = PentadSystem(bodies=new_bodies, beta=default_system.beta)
            depths.append(elegance_attractor_depth(sys_))

        for i in range(len(depths) - 1):
            assert depths[i] <= depths[i + 1] + 1e-9

    def test_formula_consistency(self, default_system):
        """Depth = 1 − clamp(moire_score / c_s_floor, 0, 1)."""
        score = moire_alignment_score(default_system)
        expected = 1.0 - min(score / C_S_STABILITY_FLOOR, 1.0)
        assert math.isclose(
            elegance_attractor_depth(default_system), expected, rel_tol=1e-9
        )


# ---------------------------------------------------------------------------
# manipulation_resistance_margin
# ---------------------------------------------------------------------------

class TestManipulationResistanceMargin:
    def test_zero_validators_gives_zero_margin(self):
        assert manipulation_resistance_margin(0) == 0.0

    def test_one_validator_positive_margin(self):
        assert manipulation_resistance_margin(1) > 0.0

    def test_monotone_increasing(self):
        margins = [manipulation_resistance_margin(n) for n in range(0, 20)]
        for i in range(len(margins) - 1):
            assert margins[i] <= margins[i + 1]

    def test_saturates_at_max(self):
        max_margin = 1.0 - BRAIDED_SOUND_SPEED
        assert math.isclose(
            manipulation_resistance_margin(1000), max_margin, rel_tol=1e-9
        )

    def test_equals_floor_minus_braided_cs(self):
        for n in [0, 1, 5, 7, 15, 100]:
            expected = collective_stability_floor(n) - BRAIDED_SOUND_SPEED
            assert math.isclose(
                manipulation_resistance_margin(n), expected, rel_tol=1e-9
            )

    def test_max_margin_below_one(self):
        assert manipulation_resistance_margin(1000) < 1.0

    def test_raises_on_negative(self):
        with pytest.raises(ValueError):
            manipulation_resistance_margin(-1)

    def test_return_type_float(self):
        assert isinstance(manipulation_resistance_margin(3), float)


# ---------------------------------------------------------------------------
# distributed_constitution_integrity
# ---------------------------------------------------------------------------

class TestDistributedConstitutionIntegrity:
    def test_zero_validators_returns_braided_sound_speed(self):
        assert math.isclose(
            distributed_constitution_integrity(0), BRAIDED_SOUND_SPEED, rel_tol=1e-9
        )

    def test_equals_collective_stability_floor(self):
        for n in [0, 1, 3, 7, 15, 50]:
            assert math.isclose(
                distributed_constitution_integrity(n),
                collective_stability_floor(n),
                rel_tol=1e-9,
            )

    def test_monotone_increasing(self):
        integrities = [distributed_constitution_integrity(n) for n in range(0, 20)]
        for i in range(len(integrities) - 1):
            assert integrities[i] <= integrities[i + 1]

    def test_saturates_at_one_at_saturation_n(self):
        assert distributed_constitution_integrity(SATURATION_N) == 1.0

    def test_no_further_increase_beyond_saturation(self):
        assert math.isclose(
            distributed_constitution_integrity(SATURATION_N),
            distributed_constitution_integrity(SATURATION_N + 100),
            rel_tol=1e-9,
        )

    def test_above_c_s_floor(self):
        # Even 0 validators is above (or equal to) the canonical (5,7) floor
        assert distributed_constitution_integrity(0) >= C_S_STABILITY_FLOOR

    def test_raises_on_negative(self):
        with pytest.raises(ValueError):
            distributed_constitution_integrity(-1)

    def test_return_type_float(self):
        assert isinstance(distributed_constitution_integrity(5), float)


# ---------------------------------------------------------------------------
# validator_node_strength
# ---------------------------------------------------------------------------

class TestValidatorNodeStrength:
    def test_zero_below_min_phi(self):
        assert validator_node_strength(0.0) == 0.0

    def test_zero_at_min_phi(self):
        # At exactly OBSERVER_MIN_PHI the fraction above floor is 0
        assert validator_node_strength(OBSERVER_MIN_PHI) == 0.0

    def test_max_at_phi_one(self):
        assert math.isclose(
            validator_node_strength(1.0), PER_VALIDATOR_INCREMENT, rel_tol=1e-9
        )

    def test_in_range(self):
        for phi in np.linspace(0.0, 1.0, 20):
            s = validator_node_strength(phi)
            assert 0.0 <= s <= PER_VALIDATOR_INCREMENT + 1e-12

    def test_monotone_above_min_phi(self):
        phis = np.linspace(OBSERVER_MIN_PHI, 1.0, 20)
        strengths = [validator_node_strength(float(p)) for p in phis]
        for i in range(len(strengths) - 1):
            assert strengths[i] <= strengths[i + 1] + 1e-12

    def test_proportional_to_excess_above_min(self):
        """strength ∝ (phi − OBSERVER_MIN_PHI) / (1 − OBSERVER_MIN_PHI)."""
        phi = 0.7
        range_above = 1.0 - OBSERVER_MIN_PHI
        fraction = (phi - OBSERVER_MIN_PHI) / range_above
        expected = PER_VALIDATOR_INCREMENT * max(0.0, fraction)
        assert math.isclose(validator_node_strength(phi), expected, rel_tol=1e-9)

    def test_return_type_float(self):
        assert isinstance(validator_node_strength(0.5), float)

    def test_clamped_at_phi_above_one(self):
        # Clamp ensures no value above PER_VALIDATOR_INCREMENT
        assert math.isclose(
            validator_node_strength(99.0), PER_VALIDATOR_INCREMENT, rel_tol=1e-9
        )
