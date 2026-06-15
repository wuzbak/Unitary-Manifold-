# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 485 — CMB Acoustic Peak Positions Boltzmann Audit."""
from __future__ import annotations

import math

from src.core.pillar485_cmb_peak_positions_boltzmann_audit import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    C_S,
    D_A_MPC,
    R_S_LCDM_MPC,
    DELTA_KK,
    R_S_KK_MPC,
    PLANCK_PEAKS,
    kk_sound_horizon_correction,
    um_peak_positions,
    planck_peak_data,
    peak_residuals,
    peak3_named_residual,
    boltzmann_audit_summary,
    peak_significance,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'CMB_PEAK_POSITIONS_BOLTZMANN_AUDIT_QUANTIFIED_RESIDUAL'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 485

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-10

    def test_d_a_mpc_reasonable(self):
        # D_A to last scattering ~13-14 Gpc
        assert 12000 < D_A_MPC < 16000

    def test_r_s_lcdm_mpc(self):
        # Sound horizon ~147 Mpc
        assert abs(R_S_LCDM_MPC - 147.09) < 0.1

    def test_delta_kk_small(self):
        # KK correction should be < 0.5%
        assert abs(DELTA_KK) < 0.005

    def test_r_s_kk_close_to_lcdm(self):
        assert abs(R_S_KK_MPC - R_S_LCDM_MPC) / R_S_LCDM_MPC < 0.005

    def test_planck_peaks_has_6_entries(self):
        assert len(PLANCK_PEAKS) == 6

    def test_planck_peaks_ordered(self):
        for i, p in enumerate(PLANCK_PEAKS, 1):
            assert p['n'] == i


class TestKKSoundHorizonCorrection:
    def setup_method(self):
        self.corr = kk_sound_horizon_correction()

    def test_returns_dict(self):
        assert isinstance(self.corr, dict)

    def test_delta_kk_matches(self):
        assert abs(self.corr['delta_kk'] - DELTA_KK) < 1e-15

    def test_delta_kk_negligible(self):
        assert self.corr['negligible'] is True

    def test_below_planck_precision(self):
        assert self.corr['below_planck_precision'] is True

    def test_has_formula(self):
        assert 'formula' in self.corr

    def test_r_s_kk(self):
        assert abs(self.corr['r_s_kk_mpc'] - R_S_KK_MPC) < 1e-8

    def test_has_note(self):
        assert 'note' in self.corr

    def test_delta_kk_pct_small(self):
        assert abs(self.corr['delta_kk_pct']) < 0.5


class TestUMPeakPositions:
    def setup_method(self):
        self.peaks = um_peak_positions()

    def test_returns_list(self):
        assert isinstance(self.peaks, list)

    def test_six_peaks(self):
        assert len(self.peaks) == 6

    def test_peak_numbers_sequential(self):
        for i, p in enumerate(self.peaks, 1):
            assert p['n'] == i

    def test_first_peak_near_220(self):
        # First acoustic peak should be near ℓ ≈ 220 (with baryonic phase offsets)
        assert 200 < self.peaks[0]['ell_kk'] < 260

    def test_peaks_increasing(self):
        for i in range(len(self.peaks) - 1):
            assert self.peaks[i]['ell_kk'] < self.peaks[i + 1]['ell_kk']

    def test_kk_correction_small(self):
        for p in self.peaks:
            frac = abs(p['delta_ell_kk_frac'])
            assert frac < 0.01  # < 1%

    def test_proportional_spacing(self):
        # Peak n is at (n - phi_n) × ell_A, so ratio to peak 1 is (n-phi_n)/(1-phi_1)
        # Peaks increase monotonically (not exactly integer multiples due to phase offsets)
        ell_values = [p['ell_kk'] for p in self.peaks]
        for i in range(len(ell_values) - 1):
            assert ell_values[i] < ell_values[i + 1]


class TestPlanckPeakData:
    def setup_method(self):
        self.data = planck_peak_data()

    def test_returns_list(self):
        assert isinstance(self.data, list)

    def test_six_peaks(self):
        assert len(self.data) == 6

    def test_first_peak_ell(self):
        assert abs(self.data[0]['ell'] - 220.0) < 1.0

    def test_all_have_sigma(self):
        for p in self.data:
            assert p['sigma'] > 0

    def test_uncertainties_increase(self):
        # Later peaks have larger uncertainties
        sigmas = [p['sigma'] for p in self.data]
        assert sigmas[-1] > sigmas[0]


class TestPeakResiduals:
    def setup_method(self):
        self.residuals = peak_residuals()

    def test_returns_list(self):
        assert isinstance(self.residuals, list)

    def test_six_residuals(self):
        assert len(self.residuals) == 6

    def test_all_have_required_fields(self):
        for r in self.residuals:
            for key in ['n', 'ell_um', 'ell_planck', 'sigma_planck',
                        'residual', 'significance_sigma', 'consistent']:
                assert key in r

    def test_significance_non_negative(self):
        for r in self.residuals:
            assert r['significance_sigma'] >= 0

    def test_consistent_when_significance_less_than_2(self):
        for r in self.residuals:
            if r['significance_sigma'] < 2.0:
                assert r['consistent'] is True
            else:
                assert r['consistent'] is False

    def test_peak1_residual_small(self):
        peak1 = self.residuals[0]
        # Residual should be small after KK correction (< 15 ℓ-units at peak 1)
        assert abs(peak1['residual']) < 15


class TestPeak3NamedResidual:
    def setup_method(self):
        self.named = peak3_named_residual()

    def test_returns_dict(self):
        assert isinstance(self.named, dict)

    def test_peak_n_is_3(self):
        assert self.named['peak_n'] == 3

    def test_has_residual_name(self):
        assert 'residual_name' in self.named
        assert 'PEAK3' in self.named['residual_name']

    def test_is_not_falsifier(self):
        assert self.named['is_falsifier'] is False

    def test_has_reason_not_falsifier(self):
        assert len(self.named['reason_not_falsifier']) > 50

    def test_has_closure_path(self):
        assert 'closure_path' in self.named
        assert len(self.named['closure_path']) > 20

    def test_epistemic_status(self):
        assert 'NAMED_RESIDUAL' in self.named['epistemic_status']

    def test_has_ell_values(self):
        assert 'ell_um' in self.named
        assert 'ell_planck' in self.named


class TestBoltzmannAuditSummary:
    def setup_method(self):
        self.summary = boltzmann_audit_summary()

    def test_returns_dict(self):
        assert isinstance(self.summary, dict)

    def test_n_peaks_6(self):
        assert self.summary['n_peaks_computed'] == 6

    def test_n_consistent_plus_inconsistent(self):
        assert (
            self.summary['n_consistent'] + self.summary['n_inconsistent']
            == self.summary['n_peaks_computed']
        )

    def test_max_significance_positive(self):
        assert self.summary['max_significance_sigma'] > 0

    def test_dominant_peak_number(self):
        assert 1 <= self.summary['dominant_residual_peak'] <= 6

    def test_not_a_falsifier(self):
        assert self.summary['not_a_falsifier'] is True

    def test_gap_type(self):
        assert 'BOLTZMANN' in self.summary['gap_type']

    def test_has_verdict(self):
        assert 'overall_verdict' in self.summary
        assert 'QUANTIFIED_RESIDUAL' in self.summary['overall_verdict']

    def test_required_tool(self):
        assert 'CLASS' in self.summary['required_tool'] or 'CAMB' in self.summary['required_tool']


class TestPeakSignificance:
    def test_returns_float(self):
        sig = peak_significance(1)
        assert isinstance(sig, float)

    def test_positive(self):
        for n in range(1, 7):
            assert peak_significance(n) >= 0

    def test_invalid_peak_raises(self):
        import pytest
        with pytest.raises(ValueError):
            peak_significance(7)

    def test_peak3_has_nonzero_significance(self):
        assert peak_significance(3) > 0


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 485

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_has_constants(self):
        c = self.report['constants']
        assert c['n_w'] == N_W
        assert c['k_cs'] == K_CS

    def test_has_kk_correction(self):
        assert 'kk_correction' in self.report

    def test_has_um_predictions(self):
        assert 'um_peak_predictions' in self.report
        assert len(self.report['um_peak_predictions']) == 6

    def test_has_residuals(self):
        assert 'residuals' in self.report
        assert len(self.report['residuals']) == 6

    def test_has_named_residual(self):
        assert 'named_residual' in self.report

    def test_previous_and_new_status(self):
        assert 'previous_status' in self.report
        assert 'OPEN' in self.report['previous_status']
        assert 'new_status' in self.report
        assert 'QUANTIFIED_RESIDUAL' in self.report['new_status']

    def test_has_verdict(self):
        assert 'verdict' in self.report
