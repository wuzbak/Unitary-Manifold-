# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 414 — γ L2 final bound."""
import math
import pytest

from src.core.pillar414_gamma_l2_final_bound import (
    PILLAR_STATUS,
    L2_STATUS,
    K_CS,
    PHI0_FULL,
    GAMMA_THEORY,
    GAMMA_FIT,
    GAMMA_GAP,
    unitarity_bound_g_braid,
    precise_condensate_gamma,
    combined_l2_budget,
    l2_final_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'L2_NP_RESIDUAL_BOUNDED_FINAL'

    def test_l2_status(self):
        assert L2_STATUS == 'L2_NP_RESIDUAL_BOUNDED_FINAL'

    def test_kcs(self):
        assert K_CS == 74

    def test_phi0_full(self):
        assert PHI0_FULL == pytest.approx(31.416)

    def test_gamma_gap(self):
        assert GAMMA_GAP == pytest.approx(GAMMA_FIT - GAMMA_THEORY)

    def test_gamma_gap_positive(self):
        assert GAMMA_GAP > 0


class TestUnitarityBoundGBraid:
    def test_returns_dict(self):
        assert isinstance(unitarity_bound_g_braid(), dict)

    def test_formula(self):
        data = unitarity_bound_g_braid()
        assert data['g_braid_max'] == pytest.approx(2 * math.pi / math.sqrt(K_CS))

    def test_reasonable_value(self):
        assert 0.72 < unitarity_bound_g_braid()['g_braid_max'] < 0.74

    def test_unitarity_saturated(self):
        assert unitarity_bound_g_braid()['unitarity_saturated'] is True


class TestPreciseCondensateGamma:
    def test_returns_dict(self):
        assert isinstance(precise_condensate_gamma(), dict)

    def test_uses_unitarity_by_default(self):
        data = precise_condensate_gamma()
        assert data['g_braid_fixed'] == pytest.approx(unitarity_bound_g_braid()['g_braid_max'])

    def test_fluctuation_relative_formula(self):
        data = precise_condensate_gamma(1.0)
        assert data['fluctuation_relative'] == pytest.approx(math.pi ** 2 / (2 * K_CS))

    def test_delta_gamma_positive(self):
        assert precise_condensate_gamma()['delta_gamma_zm_max'] > 0

    def test_delta_gamma_expected_range(self):
        data = precise_condensate_gamma()
        assert 0.024 < data['delta_gamma_zm_max'] < 0.025

    def test_gap_fraction_subunit(self):
        data = precise_condensate_gamma()
        assert 0.75 < data['gamma_gap_fraction'] < 0.8

    def test_c1_zm_positive(self):
        assert precise_condensate_gamma()['c1_zm_precise'] > 0

    def test_g_braid_scaling(self):
        d1 = precise_condensate_gamma(0.3)
        d2 = precise_condensate_gamma(0.6)
        assert d2['delta_gamma_zm_max'] == pytest.approx(2 * d1['delta_gamma_zm_max'])

    def test_formula_string_present(self):
        assert 'π²' in precise_condensate_gamma()['formula']


class TestCombinedL2Budget:
    def test_returns_dict(self):
        assert isinstance(combined_l2_budget(), dict)

    def test_c1_km_stored(self):
        assert combined_l2_budget()['c1_km'] == pytest.approx(3.02)

    def test_c1_total_stored(self):
        assert combined_l2_budget()['c1_total'] == pytest.approx(12.5)

    def test_g_braid_max_copied(self):
        assert combined_l2_budget()['g_braid_max'] == pytest.approx(unitarity_bound_g_braid()['g_braid_max'])

    def test_delta_gamma_zm_consistent(self):
        assert combined_l2_budget()['delta_gamma_zm_max'] == pytest.approx(precise_condensate_gamma()['delta_gamma_zm_max'])

    def test_combined_fraction_expected_range(self):
        assert 0.77 < combined_l2_budget()['combined_fraction'] < 0.79

    def test_remaining_fraction_expected_range(self):
        assert 0.21 < combined_l2_budget()['remaining_fraction'] < 0.23

    def test_fractions_sum_to_one(self):
        data = combined_l2_budget()
        assert data['combined_fraction'] + data['remaining_fraction'] == pytest.approx(1.0)

    def test_remaining_origin_mentions_lattice(self):
        assert 'lattice' in combined_l2_budget()['remaining_origin']


class TestL2FinalVerdict:
    def test_returns_dict(self):
        assert isinstance(l2_final_verdict(), dict)

    def test_status_final(self):
        assert l2_final_verdict()['status'] == 'L2_NP_RESIDUAL_BOUNDED_FINAL'

    def test_previous_status(self):
        assert l2_final_verdict()['previous_status'] == 'L2_CONDENSATE_ZERO_MODE_VIABLE'

    def test_new_status(self):
        assert l2_final_verdict()['new_status'] == 'L2_NP_RESIDUAL_BOUNDED_FINAL'

    def test_combined_fraction_matches_budget(self):
        assert l2_final_verdict()['combined_fraction'] == pytest.approx(combined_l2_budget()['combined_fraction'])

    def test_remaining_fraction_matches_budget(self):
        assert l2_final_verdict()['remaining_fraction'] == pytest.approx(combined_l2_budget()['remaining_fraction'])

    def test_delta_gamma_copied(self):
        assert l2_final_verdict()['delta_gamma_zm_max'] == pytest.approx(combined_l2_budget()['delta_gamma_zm_max'])

    def test_verdict_mentions_78_percent(self):
        assert '78%' in l2_final_verdict()['verdict']

    def test_verdict_mentions_22_percent(self):
        assert '22%' in l2_final_verdict()['verdict']

    def test_not_closed(self):
        assert l2_final_verdict()['status'] != 'CLOSED'
