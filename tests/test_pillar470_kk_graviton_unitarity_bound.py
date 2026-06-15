# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 470 — KK graviton unitarity bound."""
from __future__ import annotations

import pytest

from src.core.pillar470_kk_graviton_unitarity_bound import (
    PILLAR_STATUS,
    VERSION,
    kk_correction_magnitude,
    kk_scale,
    named_limitation,
    partial_wave_amplitude,
    pillar_report,
    unitarity_bound_check,
    unitarity_proof_steps,
    unitarity_threshold,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'KK_GRAVITON_UNITARITY_BOUND_PROVED'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_kk_scale_positive(self):
        assert kk_scale() > 0

    def test_kk_scale_mev_conversion(self):
        assert kk_scale() == pytest.approx(1.1e-10)


class TestKKCorrection:
    def test_zero_at_zero_energy(self):
        assert kk_correction_magnitude(0.0) == pytest.approx(0.0)

    def test_quadratic_scaling(self):
        assert kk_correction_magnitude(4.0, m_kk_gev=2.0) == pytest.approx(1.0)

    def test_non_negative(self):
        assert kk_correction_magnitude(1.0) >= 0

    def test_reject_negative_s(self):
        with pytest.raises(ValueError):
            kk_correction_magnitude(-1.0)

    def test_reject_nonpositive_mkk(self):
        with pytest.raises(ValueError):
            kk_correction_magnitude(1.0, m_kk_gev=0.0)


class TestPartialWaveAmplitude:
    def setup_method(self):
        self.low = partial_wave_amplitude(1.0, J=0, m_kk_gev=10.0)
        self.high = partial_wave_amplitude(25.0, J=0, m_kk_gev=10.0)

    def test_returns_dict(self):
        assert isinstance(self.low, dict)

    def test_contains_a_abs(self):
        assert 'a_j_abs' in self.low

    def test_contains_a_sq(self):
        assert 'a_j_sq' in self.low

    def test_contains_tree_level(self):
        assert 'tree_level_abs' in self.low

    def test_contains_correction(self):
        assert 'kk_correction' in self.low

    def test_low_energy_unitary(self):
        assert self.low['unitary'] is True

    def test_high_energy_still_unitary_for_benchmark(self):
        assert self.high['unitary'] is True

    def test_amplitude_grows_with_s(self):
        assert self.high['a_j_abs'] > self.low['a_j_abs']

    def test_amplitude_decreases_with_j(self):
        j0 = partial_wave_amplitude(25.0, J=0, m_kk_gev=10.0)
        j2 = partial_wave_amplitude(25.0, J=2, m_kk_gev=10.0)
        assert j2['a_j_abs'] < j0['a_j_abs']

    def test_below_threshold_true(self):
        assert partial_wave_amplitude(9.0, J=0, m_kk_gev=10.0)['below_kk_threshold'] is True

    def test_below_threshold_false(self):
        assert partial_wave_amplitude(121.0, J=0, m_kk_gev=10.0)['below_kk_threshold'] is False

    def test_a_sq_matches_square(self):
        assert self.low['a_j_sq'] == pytest.approx(self.low['a_j_abs'] ** 2)

    def test_reject_negative_s(self):
        with pytest.raises(ValueError):
            partial_wave_amplitude(-1.0)

    def test_reject_negative_j(self):
        with pytest.raises(ValueError):
            partial_wave_amplitude(1.0, J=-1)

    def test_reject_nonpositive_mkk(self):
        with pytest.raises(ValueError):
            partial_wave_amplitude(1.0, m_kk_gev=0.0)


class TestUnitarityBoundCheck:
    def test_theorem_applies_below_threshold(self):
        result = unitarity_bound_check(1.0, m_kk_gev=10.0)
        assert result['theorem_applies'] is True

    def test_valid_regime_false_above_threshold(self):
        result = unitarity_bound_check(11.0, m_kk_gev=10.0)
        assert result['valid_regime'] is False

    def test_still_unitary_for_benchmark(self):
        result = unitarity_bound_check(11.0, m_kk_gev=10.0)
        assert result['unitary'] is True

    def test_reject_negative_energy(self):
        with pytest.raises(ValueError):
            unitarity_bound_check(-1.0)


class TestProofMetadata:
    def test_proof_steps_count(self):
        assert len(unitarity_proof_steps()) == 4

    def test_step_1_mentions_zero_mode(self):
        assert 'zero-mode' in unitarity_proof_steps()['step_1']

    def test_step_2_mentions_einstein_hilbert(self):
        assert 'Einstein-Hilbert' in unitarity_proof_steps()['step_2']

    def test_step_3_mentions_e_over_mkk(self):
        assert '(E/M_KK)^2' in unitarity_proof_steps()['step_3']

    def test_step_4_mentions_a_j(self):
        assert '|a_J|' in unitarity_proof_steps()['step_4']

    def test_threshold_relation(self):
        assert unitarity_threshold()['relation'] == 'E ~ M_Pl'

    def test_threshold_positive(self):
        assert unitarity_threshold()['e_threshold_gev'] > 1e18

    def test_limitation_status(self):
        assert named_limitation()['status'] == 'NAMED_LIMITATION'

    def test_limitation_mentions_perturbative(self):
        assert 'perturbative' in named_limitation()['statement']


class TestReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 470

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_scale(self):
        assert self.report['kk_scale_gev'] == pytest.approx(kk_scale())

    def test_contains_proof_steps(self):
        assert 'proof_steps' in self.report

    def test_contains_threshold(self):
        assert 'threshold' in self.report

    def test_contains_limitation(self):
        assert 'limitation' in self.report
