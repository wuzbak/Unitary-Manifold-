# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 417 — N₂ cycle assignment."""
import pytest

from src.core.pillar417_n2_cycle_assignment import (
    PILLAR_STATUS,
    N2_SELECTION_STATUS,
    N_W,
    K_CS,
    N2,
    BRAIDED_SOUND_SPEED,
    kcs_partner_winding,
    winding_energy,
    cycle_assignment_uniqueness,
    n2_derivation_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'DERIVED_FROM_WINDING_TENSION'

    def test_n2_status(self):
        assert N2_SELECTION_STATUS == 'DERIVED_FROM_WINDING_TENSION'

    def test_nw(self):
        assert N_W == 5

    def test_kcs(self):
        assert K_CS == 74

    def test_n2(self):
        assert N2 == 7

    def test_sound_speed(self):
        assert BRAIDED_SOUND_SPEED == pytest.approx(12 / 37)


class TestKcsPartnerWinding:
    def test_returns_7_for_n1_5(self):
        assert kcs_partner_winding(5, 74) == 7

    def test_returns_none_when_not_square(self):
        assert kcs_partner_winding(6, 74) is None

    def test_returns_none_when_remainder_negative(self):
        assert kcs_partner_winding(9, 74) is None


class TestWindingEnergy:
    def test_formula(self):
        assert winding_energy(5, 7, 74) == pytest.approx((25 + 49 - 70) / 74)

    def test_positive(self):
        assert winding_energy(5, 7, 74) > 0

    def test_small_for_canonical_pair(self):
        assert winding_energy(5, 7, 74) < 0.1


class TestCycleAssignmentUniqueness:
    def test_returns_dict(self):
        assert isinstance(cycle_assignment_uniqueness(5, 74), dict)

    def test_partner_found(self):
        assert cycle_assignment_uniqueness(5, 74)['n_partner'] == 7

    def test_unique_solution(self):
        assert cycle_assignment_uniqueness(5, 74)['unique_integer_solution'] is True

    def test_step_width_two(self):
        assert cycle_assignment_uniqueness(5, 74)['step_width'] == 2

    def test_tension_over_k(self):
        assert cycle_assignment_uniqueness(5, 74)['tension_over_k'] == pytest.approx(2 * BRAIDED_SOUND_SPEED)

    def test_energy_copied(self):
        assert cycle_assignment_uniqueness(5, 74)['normalized_energy'] == pytest.approx(winding_energy(5, 7, 74))


class TestVerdict:
    def test_returns_dict(self):
        assert isinstance(n2_derivation_verdict(), dict)

    def test_status(self):
        assert n2_derivation_verdict()['admission_xiii4_status'] == 'DERIVED_FROM_WINDING_TENSION'

    def test_n1_and_n2(self):
        verdict = n2_derivation_verdict()
        assert verdict['n1'] == 5
        assert verdict['n2'] == 7

    def test_kcs_stored(self):
        assert n2_derivation_verdict()['K_cs'] == 74

    def test_verdict_mentions_unique(self):
        assert 'unique' in n2_derivation_verdict()['verdict']
