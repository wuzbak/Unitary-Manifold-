# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 423 — Wheeler-DeWitt Mini-Superspace Quantum Closure."""
import math
import pytest

from src.core.pillar423_wdw_minisuperspace import (
    PILLAR_STATUS,
    N_W,
    K_CS,
    C_S,
    PHI_STAR,
    compute_lambda_eff,
    hartle_hawking_amplitude,
    ftum_fixed_point_quantum_variance,
    wdw_minisuperspace_verdict,
    honest_caveats,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'MINI_SUPERSPACE_QUANTUM_CLOSURE'

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-10

    def test_phi_star(self):
        assert abs(PHI_STAR - 2.0 * math.pi * 5) < 1e-8


class TestComputeLambdaEff:
    def test_returns_positive(self):
        assert compute_lambda_eff() > 0.0

    def test_small_compared_to_unity(self):
        # λ_eff in Planck units should be small (φ* >> 1)
        assert compute_lambda_eff() < 1.0

    def test_increases_with_c_s(self):
        lam_default = compute_lambda_eff(c_s=12.0 / 37.0)
        lam_larger = compute_lambda_eff(c_s=0.5)
        assert lam_larger > lam_default

    def test_decreases_with_larger_n_w(self):
        lam_5 = compute_lambda_eff(n_w=5)
        lam_7 = compute_lambda_eff(n_w=7)
        assert lam_7 < lam_5


class TestHartleHawkingAmplitude:
    def test_returns_negative_log(self):
        # For a > 0, log amplitude should be negative (exponential decay)
        assert hartle_hawking_amplitude(1.0) < 0.0

    def test_zero_at_a_equals_zero(self):
        assert hartle_hawking_amplitude(0.0) == 0.0

    def test_more_negative_at_larger_a(self):
        amp1 = hartle_hawking_amplitude(1.0)
        amp2 = hartle_hawking_amplitude(2.0)
        assert amp2 < amp1

    def test_raises_on_negative_a(self):
        with pytest.raises(ValueError):
            hartle_hawking_amplitude(-1.0)

    def test_raises_on_zero_lambda(self):
        with pytest.raises(ValueError):
            hartle_hawking_amplitude(1.0, lambda_eff=0.0)


class TestFtumFixedPointQuantumVariance:
    def test_returns_dict(self):
        assert isinstance(ftum_fixed_point_quantum_variance(), dict)

    @pytest.mark.parametrize('key', ['phi_star', 'variance_ratio', 'variance_ratio_pct',
                                     'ftum_fixed_point_stable'])
    def test_expected_keys(self, key):
        assert key in ftum_fixed_point_quantum_variance()

    def test_variance_ratio_very_small(self):
        # Should be much less than 1e-3 (fixed point is stable)
        var = ftum_fixed_point_quantum_variance()
        assert var['variance_ratio'] < 1e-3

    def test_fixed_point_stable_true(self):
        assert ftum_fixed_point_quantum_variance()['ftum_fixed_point_stable'] is True

    def test_phi_star_correct(self):
        var = ftum_fixed_point_quantum_variance()
        assert abs(var['phi_star'] - PHI_STAR) < 1e-8


class TestWdwMinisuperspaceVerdict:
    def test_returns_dict(self):
        assert isinstance(wdw_minisuperspace_verdict(), dict)

    def test_status(self):
        assert wdw_minisuperspace_verdict()['status'] == 'MINI_SUPERSPACE_QUANTUM_CLOSURE'

    @pytest.mark.parametrize('key', ['lambda_eff', 'a_dS', 'phi_star', 'quantum_variance',
                                     'ftum_consistent_quantum_solution', 'verdict'])
    def test_expected_keys(self, key):
        assert key in wdw_minisuperspace_verdict()

    def test_ftum_consistent(self):
        assert wdw_minisuperspace_verdict()['ftum_consistent_quantum_solution'] is True

    def test_a_ds_positive(self):
        assert wdw_minisuperspace_verdict()['a_dS'] > 0.0

    def test_lambda_eff_positive(self):
        assert wdw_minisuperspace_verdict()['lambda_eff'] > 0.0

    def test_verdict_is_string(self):
        assert isinstance(wdw_minisuperspace_verdict()['verdict'], str)


class TestHonestCaveats:
    def test_returns_dict(self):
        assert isinstance(honest_caveats(), dict)

    @pytest.mark.parametrize('key', ['mini_superspace_approximation',
                                     'full_wdw_status', 'adjacent_track_label'])
    def test_expected_keys(self, key):
        assert key in honest_caveats()

    def test_adjacent_track_label_contains_adjacent(self):
        assert 'ADJACENT' in honest_caveats()['adjacent_track_label']

    def test_full_wdw_status_mentions_open(self):
        assert 'open' in honest_caveats()['full_wdw_status'].lower()
