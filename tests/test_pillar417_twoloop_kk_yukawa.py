# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 417 — 2-Loop KK Yukawa Jarlskog Closure."""
import math
import pytest

from src.core.pillar417_twoloop_kk_yukawa import (
    PILLAR_STATUS,
    ADMISSION_7_STATUS,
    N_W,
    K_CS,
    N_C,
    PI_KR,
    ALPHA_3_MKK,
    C_F,
    DELTA_C,
    alpha_3_kk,
    twoloop_yukawa_correction,
    admission7_twoloop_verdict,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'TWOLOOP_SUBLEADING_ADMISSION7_CLOSED'

    def test_admission_status(self):
        assert ADMISSION_7_STATUS == 'CLOSED'

    def test_alpha_value(self):
        assert ALPHA_3_MKK == pytest.approx(3.0 / 74.0)

    def test_alpha_approx(self):
        assert ALPHA_3_MKK == pytest.approx(0.04054, abs=1e-4)

    def test_c_f_value(self):
        assert C_F == pytest.approx(4.0 / 3.0)

    def test_c_f_approx(self):
        assert C_F == pytest.approx(1.3333333, rel=1e-6)

    def test_delta_c(self):
        assert DELTA_C == pytest.approx(5.0 / 74.0)

    @pytest.mark.parametrize('constant', [N_W, K_CS, N_C, PI_KR])
    def test_core_constants_positive(self, constant):
        assert constant > 0


class TestAlpha3KK:
    def test_function_matches_constant(self):
        assert alpha_3_kk() == pytest.approx(ALPHA_3_MKK)

    def test_function_positive(self):
        assert alpha_3_kk() > 0.0

    def test_function_below_one(self):
        assert alpha_3_kk() < 1.0


class TestTwoLoopYukawaCorrection:
    @pytest.mark.parametrize('key', ['c_L', 'pi_kr', 'f_rs', 'delta_y_twoloop', 'delta_cL_twoloop', 'delta_fraction_lattice', 'subleading_factor'])
    def test_expected_keys_present(self, key):
        assert key in twoloop_yukawa_correction()

    @pytest.mark.parametrize('c_l', [0.094, 0.05, 0.1, 0.2, 0.3, 0.01, 0.15, 0.08, 0.12])
    def test_delta_y_positive(self, c_l):
        assert twoloop_yukawa_correction(c_L=c_l)['delta_y_twoloop'] > 0.0

    @pytest.mark.parametrize('c_l', [0.094, 0.05, 0.1, 0.2, 0.3, 0.01, 0.15, 0.08, 0.12])
    def test_delta_fraction_small(self, c_l):
        assert twoloop_yukawa_correction(c_L=c_l)['delta_fraction_lattice'] < 0.01

    @pytest.mark.parametrize('c_l', [0.094, 0.05, 0.1, 0.2, 0.3, 0.01, 0.15, 0.08, 0.12])
    def test_subleading_factor_large(self, c_l):
        assert twoloop_yukawa_correction(c_L=c_l)['subleading_factor'] > 50.0

    def test_canonical_delta_fraction_matches_prompt_scale(self):
        assert twoloop_yukawa_correction()['delta_fraction_lattice'] == pytest.approx(2.4e-4, rel=0.15)

    def test_f_rs_is_one_point_five(self):
        assert twoloop_yukawa_correction()['f_rs'] == pytest.approx(1.5)

    def test_canonical_delta_y_small(self):
        assert twoloop_yukawa_correction()['delta_y_twoloop'] < 0.02

    def test_canonical_delta_cl_tiny(self):
        assert twoloop_yukawa_correction()['delta_cL_twoloop'] < 1e-4


class TestAdmission7Verdict:
    @pytest.mark.parametrize('key', ['admission_number', 'previous_status', 'new_status', 'status', 'delta_KT_LO', 'delta_2loop_fraction', 'subleading_by_factor', 'verdict'])
    def test_expected_keys_present(self, key):
        assert key in admission7_twoloop_verdict()

    def test_admission_number(self):
        assert admission7_twoloop_verdict()['admission_number'] == 7

    def test_new_status_closed(self):
        assert admission7_twoloop_verdict()['new_status'] == 'CLOSED'

    def test_status_label(self):
        assert admission7_twoloop_verdict()['status'] == 'TWOLOOP_SUBLEADING_ADMISSION7_CLOSED'

    def test_subleading_by_more_than_fifty(self):
        assert admission7_twoloop_verdict()['subleading_by_factor'] > 50.0

    def test_verdict_mentions_closed(self):
        assert 'CLOSED' in admission7_twoloop_verdict()['verdict']
