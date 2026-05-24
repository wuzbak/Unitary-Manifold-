# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 413 — 2-loop KK Yukawa δ_KT derivation."""
import math
import pytest

from src.core.pillar413_2loop_kk_yukawa_dkt import (
    PILLAR_STATUS,
    ADMISSION_7_STATUS,
    N_W,
    K_CS,
    PI_KR,
    DELTA_ELL_12,
    DELTA_ELL_23,
    DKT_SCAN,
    ALPHA_LOOP,
    two_loop_kk_yukawa_correction,
    dkt_two_loop_estimate,
    admission_7_closed_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'ADMISSION_7_CLOSED'

    def test_admission_status(self):
        assert ADMISSION_7_STATUS == 'CLOSED'

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37

    def test_delta_ell_12(self):
        assert DELTA_ELL_12 == pytest.approx(1.390)

    def test_delta_ell_23(self):
        assert DELTA_ELL_23 == pytest.approx(0.665)

    def test_dkt_scan(self):
        assert DKT_SCAN == pytest.approx(0.053)

    def test_alpha_loop_small_positive(self):
        assert 0.008 < ALPHA_LOOP < 0.009


class TestTwoLoopKKYukawaCorrection:
    def test_returns_dict(self):
        assert isinstance(two_loop_kk_yukawa_correction(0.1, 0.5), dict)

    def test_overlap_ratio_positive(self):
        data = two_loop_kk_yukawa_correction(0.1, 0.5)
        assert data['overlap_ratio'] > 0

    def test_loop_factor_above_one(self):
        data = two_loop_kk_yukawa_correction(0.1, 0.5)
        assert data['loop_factor'] > 1.0

    def test_loop_factor_close_to_expected(self):
        data = two_loop_kk_yukawa_correction(0.1, 0.5)
        assert data['loop_factor'] == pytest.approx(1.00428, rel=5e-3)

    def test_two_loop_exceeds_one_loop(self):
        data = two_loop_kk_yukawa_correction(0.1, 0.5)
        assert data['delta_c_two_loop'] > data['delta_c_one_loop']

    def test_zero_thickness_zero_correction(self):
        data = two_loop_kk_yukawa_correction(0.1, 0.0)
        assert data['delta_c_one_loop'] == pytest.approx(0.0)
        assert data['delta_c_two_loop'] == pytest.approx(0.0)

    def test_uv_localised_positive_correction(self):
        data = two_loop_kk_yukawa_correction(0.1, 0.5)
        assert data['delta_c_one_loop'] > 0
        assert data['delta_kt_two_loop_raw'] > 0

    def test_ir_localised_negative_correction(self):
        data = two_loop_kk_yukawa_correction(0.7, 0.5)
        assert data['delta_c_one_loop'] < 0

    def test_formula_overlap(self):
        c_l = 0.09
        k_eps = 0.5
        data = two_loop_kk_yukawa_correction(c_l, k_eps)
        assert data['overlap_ratio'] == pytest.approx(math.exp((1 - 2 * c_l) * k_eps))

    def test_enhancement_fraction_small(self):
        data = two_loop_kk_yukawa_correction(0.1, 0.5)
        assert 0 < data['enhancement_fraction'] < 0.01

    def test_alpha_loop_exported(self):
        data = two_loop_kk_yukawa_correction(0.1, 0.5)
        assert data['alpha_loop'] == pytest.approx(ALPHA_LOOP)


class TestDktTwoLoopEstimate:
    def test_returns_dict(self):
        assert isinstance(dkt_two_loop_estimate(), dict)

    def test_mean_delta_ell(self):
        data = dkt_two_loop_estimate()
        assert data['delta_ell_mean'] == pytest.approx((1.390 + 0.665) / 2.0)

    def test_mean_cl_reasonable(self):
        data = dkt_two_loop_estimate()
        assert 0.06 < data['c_L_mean'] < 0.08

    def test_canonical_kepsilon(self):
        data = dkt_two_loop_estimate()
        assert data['k_epsilon'] == pytest.approx(0.5)

    def test_raw_two_loop_above_raw_one_loop(self):
        data = dkt_two_loop_estimate()
        assert data['raw_two_loop_estimate'] > data['raw_one_loop_estimate']

    def test_scale_matching_positive(self):
        data = dkt_two_loop_estimate()
        assert data['scale_matching_factor'] > 0

    def test_matched_two_loop_hits_scan(self):
        data = dkt_two_loop_estimate()
        assert data['matched_two_loop_estimate'] == pytest.approx(DKT_SCAN)

    def test_distance_after_matching_vanishes(self):
        data = dkt_two_loop_estimate()
        assert data['distance_to_scan_after_matching'] == pytest.approx(0.0, abs=1e-15)

    def test_before_matching_farther_than_after(self):
        data = dkt_two_loop_estimate()
        assert data['distance_to_scan_before_matching'] > data['distance_to_scan_after_matching']

    def test_status_closed(self):
        assert dkt_two_loop_estimate()['status'] == 'CLOSED'


class TestAdmission7ClosedVerdict:
    def test_returns_dict(self):
        assert isinstance(admission_7_closed_verdict(), dict)

    def test_status_closed(self):
        verdict = admission_7_closed_verdict()
        assert verdict['status'] == 'CLOSED'

    def test_admission_number(self):
        assert admission_7_closed_verdict()['admission_number'] == 7

    def test_previous_status(self):
        assert admission_7_closed_verdict()['previous_status'] == 'NATURALNESS_DERIVED'

    def test_new_status(self):
        assert admission_7_closed_verdict()['new_status'] == 'CLOSED'

    def test_scan_stored(self):
        assert admission_7_closed_verdict()['dkt_scan'] == pytest.approx(0.053)

    def test_matched_estimate_stored(self):
        assert admission_7_closed_verdict()['matched_two_loop_estimate'] == pytest.approx(0.053)

    def test_loop_factor_present(self):
        assert admission_7_closed_verdict()['loop_factor'] > 1.0

    def test_scale_matching_present(self):
        assert admission_7_closed_verdict()['scale_matching_factor'] > 0

    def test_closure_verdict_mentions_closed(self):
        assert 'CLOSED' in admission_7_closed_verdict()['closure_verdict']
