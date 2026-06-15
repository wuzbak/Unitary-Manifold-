# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 445 — 2-Loop KK Yukawa / Admission 7 Full Closure."""
import math
import pytest
from src.core.pillar445_two_loop_kk_yukawa import (
    PILLAR_STATUS, VERSION, ADMISSION_7_STATUS,
    ALPHA_GUT, ALPHA_S_MKK, M_KK_GEV, PI_KR, N_W, K_CS, GAMMA_E, K_GRAV,
    DELTA_ELL_12_TARGET, DELTA_ELL_23_TARGET, DELTA_KT, P_R_FITTED,
    kk_graviton_yukawa_correction, kk_gauge_yukawa_correction,
    two_loop_kk_yukawa_total, fn_charge_shift_2loop,
    jarlskog_closure_check, p_r_from_2loop_yukawa, admission_7_status, pillar_report,
)


class TestPillarMetadata:
    def test_status_contains_admission7(self):
        assert 'ADMISSION7' in PILLAR_STATUS or 'TWOLOOP' in PILLAR_STATUS

    def test_version(self):
        assert VERSION == 'v13.8'

    def test_admission7_final_closed(self):
        assert ADMISSION_7_STATUS['final_status'] == 'FULLY_CLOSED'

    def test_alpha_gut_is_3_over_74(self):
        assert abs(ALPHA_GUT - 3/74) < 1e-6

    def test_constants_reasonable(self):
        assert N_W == 5
        assert K_CS == 74
        assert 0.5 < GAMMA_E < 0.6
        assert K_GRAV > 1.0


class TestKKGravitonCorrection:
    def test_returns_positive(self):
        delta = kk_graviton_yukawa_correction(1.0)
        assert delta > 0

    def test_linear_in_lambda(self):
        d1 = kk_graviton_yukawa_correction(1.0)
        d2 = kk_graviton_yukawa_correction(2.0)
        assert abs(d2 / d1 - 2.0) < 1e-10

    def test_larger_nkk_gives_larger_correction(self):
        d10 = kk_graviton_yukawa_correction(1.0, n_kk=10)
        d37 = kk_graviton_yukawa_correction(1.0, n_kk=37)
        assert d37 > d10

    def test_n_kk_default_is_37(self):
        # n_kk=37 is the N_flux value
        d_default = kk_graviton_yukawa_correction(1.0)
        d_37 = kk_graviton_yukawa_correction(1.0, n_kk=37)
        assert abs(d_default - d_37) < 1e-12


class TestKKGaugeCorrection:
    def test_zero_casimir_zero_correction(self):
        delta = kk_gauge_yukawa_correction(1.0, casimir_c_f=0.0)
        assert delta == 0.0

    def test_quark_casimir_positive(self):
        delta = kk_gauge_yukawa_correction(1.0, casimir_c_f=4.0/3.0)
        assert delta > 0

    def test_proportional_to_lambda(self):
        d1 = kk_gauge_yukawa_correction(1.0, casimir_c_f=4.0/3.0)
        d2 = kk_gauge_yukawa_correction(2.0, casimir_c_f=4.0/3.0)
        assert abs(d2 / d1 - 2.0) < 1e-10


class TestTwoLoopTotal:
    def test_total_is_sum(self):
        result = two_loop_kk_yukawa_total(1.0)
        expected_total = result['delta_grav'] + result['delta_gauge']
        assert abs(result['delta_total'] - expected_total) < 1e-12

    def test_correction_fraction_positive(self):
        result = two_loop_kk_yukawa_total(1.0)
        assert result['correction_fraction'] > 0

    def test_lambda_corrected_gt_bare(self):
        result = two_loop_kk_yukawa_total(1.0)
        assert result['lambda_corrected'] > result['lambda_bare']

    def test_n_kk_in_result(self):
        result = two_loop_kk_yukawa_total(1.0)
        assert result['n_kk'] == 37


class TestFNChargeShifts:
    def test_returns_shifts(self):
        shifts = fn_charge_shift_2loop()
        assert 'delta_ell_12_2loop' in shifts
        assert 'delta_ell_23_2loop' in shifts

    def test_shifts_finite(self):
        shifts = fn_charge_shift_2loop()
        assert math.isfinite(shifts['delta_ell_12_2loop'])
        assert math.isfinite(shifts['delta_ell_23_2loop'])

    def test_kt_correction_in_result(self):
        shifts = fn_charge_shift_2loop()
        assert 'delta_ell_12_with_kt' in shifts


class TestJarlskogClosure:
    def test_j_pdg_present(self):
        result = jarlskog_closure_check()
        assert 'J_PDG' in result
        assert result['J_PDG'] > 0

    def test_residuals_present(self):
        result = jarlskog_closure_check()
        assert 'residual_ell_12' in result
        assert 'residual_ell_23' in result

    def test_corrected_ell_present(self):
        result = jarlskog_closure_check()
        assert 'ell_12_corrected' in result
        assert 'ell_23_corrected' in result


class TestAdmission7:
    def test_final_status_fully_closed(self):
        status = admission_7_status()
        # final_status is in history dict
        final = status.get('final_status') or status['history']['final_status']
        assert final == 'FULLY_CLOSED'

    def test_current_status_closed(self):
        status = admission_7_status()
        assert 'CLOSED' in status['current_status']

    def test_p_r_uniquely_determined(self):
        status = admission_7_status()
        assert status['p_r_uniquely_determined'] is True

    def test_pillar_is_445(self):
        status = admission_7_status()
        assert status['pillar'] == 445

    def test_mechanism_described(self):
        status = admission_7_status()
        assert 'mechanism' in status
        assert len(status['mechanism']) > 0


class TestPRDerivation:
    def test_p_r_uniquely_determined(self):
        result = p_r_from_2loop_yukawa()
        assert result['uniquely_determined'] is True

    def test_p_r_2loop_present(self):
        result = p_r_from_2loop_yukawa()
        assert 'p_r_2loop' in result

    def test_p_r_finite(self):
        result = p_r_from_2loop_yukawa()
        assert math.isfinite(result['p_r_2loop'])


class TestPillarReport:
    def test_report_pillar(self):
        r = pillar_report()
        assert r['pillar'] == 445

    def test_report_status_contains_closed(self):
        r = pillar_report()
        assert 'CLOSED' in r['status'] or 'TWOLOOP' in r['status']

    def test_report_unblocked_list(self):
        r = pillar_report()
        assert 'unblocked' in r
        assert len(r['unblocked']) >= 1
