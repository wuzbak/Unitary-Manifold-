# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 416 — B_μ-corrected gluon amplitude."""
import math
import pytest

from src.core.pillar416_bmu_gluon_amplitude import (
    PILLAR_STATUS,
    ADMISSION_10_STATUS,
    PHI0,
    X1_BESSEL,
    ALPHA_S,
    bmu_classical_mixing_angle,
    bmu_graviton_coupling_suppression,
    gluon_gg_gkk_corrected_ratio,
    admission_10_derived_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'ADMISSION_10_CONSTRAINED_DERIVED'

    def test_admission_status(self):
        assert ADMISSION_10_STATUS == 'CONSTRAINED_DERIVED'

    def test_phi0(self):
        assert PHI0 == pytest.approx(31.416)

    def test_x1(self):
        assert X1_BESSEL == pytest.approx(3.83159)

    def test_alpha_s(self):
        assert ALPHA_S == pytest.approx(0.113)


class TestBmuClassicalMixingAngle:
    def test_formula(self):
        assert bmu_classical_mixing_angle(PHI0, X1_BESSEL) == pytest.approx(PHI0 ** 2 / X1_BESSEL ** 2)

    def test_large_mixing(self):
        assert bmu_classical_mixing_angle(PHI0, X1_BESSEL) > 60

    def test_smaller_for_larger_x1(self):
        assert bmu_classical_mixing_angle(PHI0, 5.0) < bmu_classical_mixing_angle(PHI0, X1_BESSEL)


class TestBmuGravitonCouplingSuppression:
    def test_formula(self):
        expected = 1.0 / (1.0 + PHI0 ** 2 / X1_BESSEL ** 2)
        assert bmu_graviton_coupling_suppression(PHI0, X1_BESSEL) == pytest.approx(expected)

    def test_small_positive(self):
        value = bmu_graviton_coupling_suppression(PHI0, X1_BESSEL)
        assert 0.014 < value < 0.015

    def test_suppression_decreases_with_phi0(self):
        assert bmu_graviton_coupling_suppression(40.0, X1_BESSEL) < bmu_graviton_coupling_suppression(PHI0, X1_BESSEL)

    def test_suppression_increases_with_x1(self):
        assert bmu_graviton_coupling_suppression(PHI0, 5.0) > bmu_graviton_coupling_suppression(PHI0, X1_BESSEL)


class TestCorrectedRatio:
    def test_returns_dict(self):
        assert isinstance(gluon_gg_gkk_corrected_ratio(), dict)

    def test_gs_squared_formula(self):
        data = gluon_gg_gkk_corrected_ratio()
        assert data['g_s_squared'] == pytest.approx(4 * math.pi * ALPHA_S)

    def test_direct_loop_nearly_one(self):
        data = gluon_gg_gkk_corrected_ratio()
        assert data['direct_loop_factor'] == pytest.approx(1.0, rel=1e-20)

    def test_classical_mixing_matches_function(self):
        data = gluon_gg_gkk_corrected_ratio()
        assert data['classical_mixing'] == pytest.approx(bmu_classical_mixing_angle(PHI0, X1_BESSEL))

    def test_suppression_matches_function(self):
        data = gluon_gg_gkk_corrected_ratio()
        assert data['suppression_factor'] == pytest.approx(bmu_graviton_coupling_suppression(PHI0, X1_BESSEL))

    def test_ratio_below_p403_bound(self):
        assert gluon_gg_gkk_corrected_ratio()['below_p403_bound'] is True

    def test_lhc_status_safe(self):
        assert gluon_gg_gkk_corrected_ratio()['lhc_status'] == 'SAFE'

    def test_sigma_ratio_expected_range(self):
        assert 0.014 < gluon_gg_gkk_corrected_ratio()['sigma_corrected_over_sigma_bare'] < 0.015


class TestAdmission10Verdict:
    def test_returns_dict(self):
        assert isinstance(admission_10_derived_verdict(), dict)

    def test_admission_number(self):
        assert admission_10_derived_verdict()['admission_number'] == 10

    def test_previous_status(self):
        assert admission_10_derived_verdict()['previous_status'] == 'CONSTRAINED_BOUNDED'

    def test_new_status(self):
        assert admission_10_derived_verdict()['new_status'] == 'CONSTRAINED_DERIVED'

    def test_lhc_status_safe(self):
        assert admission_10_derived_verdict()['lhc_status'] == 'SAFE'

    def test_suppression_factor_copied(self):
        assert admission_10_derived_verdict()['suppression_factor'] == pytest.approx(gluon_gg_gkk_corrected_ratio()['suppression_factor'])

    def test_verdict_mentions_1_5_percent(self):
        assert '1.5%' in admission_10_derived_verdict()['verdict']
