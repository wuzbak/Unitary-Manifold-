# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 420 — ADM lapse slow-roll closure."""
import pytest

from src.core.pillar420_adm_lapse_dynamical import (
    PILLAR_STATUS,
    ADM_LAPSE_STATUS,
    PHI0_FULL,
    N_W,
    C_S,
    slow_roll_epsilon_braid,
    lapse_deviation_slow_roll,
    adm_lapse_slow_roll_derivation,
    adm_lapse_dynamical_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'ADM_LAPSE_SLOW_ROLL_CLOSED'

    def test_adm_status(self):
        assert ADM_LAPSE_STATUS == 'ADM_LAPSE_SLOW_ROLL_CLOSED'

    def test_phi0(self):
        assert PHI0_FULL == pytest.approx(31.416)

    def test_nw(self):
        assert N_W == 5

    def test_cs(self):
        assert C_S == pytest.approx(12 / 37)


class TestSlowRollEpsilonBraid:
    def test_positive(self):
        assert slow_roll_epsilon_braid(PHI0_FULL, N_W) > 0

    def test_expected_value(self):
        assert slow_roll_epsilon_braid(PHI0_FULL, N_W) == pytest.approx(6 / PHI0_FULL ** 2)

    def test_expected_range(self):
        assert 0.006 < slow_roll_epsilon_braid(PHI0_FULL, N_W) < 0.0062

    def test_invalid_phi0_raises(self):
        with pytest.raises(ValueError):
            slow_roll_epsilon_braid(0.0, N_W)

    def test_invalid_nw_raises(self):
        with pytest.raises(ValueError):
            slow_roll_epsilon_braid(PHI0_FULL, 0)


class TestLapseDeviationSlowRoll:
    def test_half_of_epsilon(self):
        eps = slow_roll_epsilon_braid(PHI0_FULL, N_W)
        assert lapse_deviation_slow_roll(eps) == pytest.approx(eps / 2)

    def test_expected_range(self):
        assert 0.003 < lapse_deviation_slow_roll(slow_roll_epsilon_braid(PHI0_FULL, N_W)) < 0.0031


class TestAdmLapseSlowRollDerivation:
    def test_returns_dict(self):
        assert isinstance(adm_lapse_slow_roll_derivation(), dict)

    def test_status(self):
        assert adm_lapse_slow_roll_derivation()['status'] == 'ADM_LAPSE_SLOW_ROLL_CLOSED'

    def test_epsilon_matches_function(self):
        assert adm_lapse_slow_roll_derivation()['epsilon_braid'] == pytest.approx(slow_roll_epsilon_braid(PHI0_FULL, N_W))

    def test_delta_n_matches_function(self):
        data = adm_lapse_slow_roll_derivation()
        assert data['delta_n_scalar'] == pytest.approx(lapse_deviation_slow_roll(data['epsilon_braid']))

    def test_total_bound_equals_epsilon(self):
        data = adm_lapse_slow_roll_derivation()
        assert data['total_gauge_invariant_bound'] == pytest.approx(data['epsilon_braid'])

    def test_hamiltonian_constraint_present(self):
        assert 'H =' in adm_lapse_slow_roll_derivation()['hamiltonian_constraint']


class TestAdmLapseDynamicalVerdict:
    def test_returns_dict(self):
        assert isinstance(adm_lapse_dynamical_verdict(), dict)

    def test_status(self):
        assert adm_lapse_dynamical_verdict()['status'] == 'ADM_LAPSE_SLOW_ROLL_CLOSED'

    def test_previous_status(self):
        assert adm_lapse_dynamical_verdict()['previous_status'] == 'XIV.3_RESIDUAL_ESTIMATED'

    def test_new_status(self):
        assert adm_lapse_dynamical_verdict()['new_status'] == 'ADM_LAPSE_SLOW_ROLL_CLOSED'

    def test_scalar_deviation_copied(self):
        assert adm_lapse_dynamical_verdict()['delta_n_scalar'] == pytest.approx(adm_lapse_slow_roll_derivation()['delta_n_scalar'])

    def test_total_bound_copied(self):
        assert adm_lapse_dynamical_verdict()['total_gauge_invariant_bound'] == pytest.approx(adm_lapse_slow_roll_derivation()['total_gauge_invariant_bound'])

    def test_verdict_mentions_bssn(self):
        assert 'BSSN' in adm_lapse_dynamical_verdict()['verdict']
