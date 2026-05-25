# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 418 — CMB Z_φ(k) Acoustic Peak Residual Bound."""
import math
import pytest

from src.core.pillar418_cmb_peak_residual_bound import (
    PILLAR_STATUS,
    Z_PHI_0,
    GAMMA_RUNNING,
    RESIDUAL_OLD_PCT,
    RESIDUAL_NEW_PCT,
    K_PEAKS,
    ELL_PEAKS,
    z_phi_k,
    peak_amplitude_residuals,
    baryon_loading_correction,
    residual_bound_tightened,
    cmb_peak_bound_verdict,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'CMB_RESIDUAL_BOUNDED_15PCT'

    def test_z_phi_gt_five(self):
        assert Z_PHI_0 > 5.0

    def test_gamma_running_positive(self):
        assert GAMMA_RUNNING > 0.0

    def test_new_residual_lower_than_old(self):
        assert RESIDUAL_NEW_PCT < RESIDUAL_OLD_PCT

    def test_three_k_peaks(self):
        assert len(K_PEAKS) == 3

    def test_three_ell_peaks(self):
        assert len(ELL_PEAKS) == 3

    @pytest.mark.parametrize('ell', [220, 540, 820])
    def test_expected_ell_values(self, ell):
        assert ell in ELL_PEAKS

    @pytest.mark.parametrize('k_value', [0.02, 0.05, 0.08])
    def test_expected_k_values(self, k_value):
        assert k_value in K_PEAKS


class TestZPhiK:
    @pytest.mark.parametrize('k_value', [0.02, 0.03, 0.05, 0.08, 0.1, 0.2, 0.5, 1.0, 0.07])
    def test_returns_positive_float(self, k_value):
        value = z_phi_k(k_value)
        assert isinstance(value, float)
        assert value > 0.0

    def test_reference_scale_returns_z_phi0(self):
        assert z_phi_k(0.05) == pytest.approx(Z_PHI_0)

    def test_decreases_with_k(self):
        assert z_phi_k(0.02) > z_phi_k(0.05) > z_phi_k(0.08)

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            z_phi_k(0.0)


class TestPeakAmplitudeResiduals:
    def test_returns_three_peaks(self):
        assert len(peak_amplitude_residuals()['peaks']) == 3

    @pytest.mark.parametrize('index', [0, 1, 2])
    def test_each_peak_has_expected_keys(self, index):
        peak = peak_amplitude_residuals()['peaks'][index]
        for key in ['ell_peak', 'k_Mpc_inv', 'Z_phi_k', 'C_ell_ratio', 'residual_pct']:
            assert key in peak

    @pytest.mark.parametrize('index', [0, 1, 2])
    def test_each_residual_below_thirty_percent(self, index):
        assert peak_amplitude_residuals()['peaks'][index]['residual_pct'] < 30.0

    @pytest.mark.parametrize('index', [0, 1, 2])
    def test_each_ratio_positive(self, index):
        assert peak_amplitude_residuals()['peaks'][index]['C_ell_ratio'] > 0.0

    def test_max_residual_matches_entries(self):
        data = peak_amplitude_residuals()
        assert data['max_residual_pct'] == pytest.approx(max(peak['residual_pct'] for peak in data['peaks']))

    def test_peak_order_matches_input(self):
        peaks = peak_amplitude_residuals()['peaks']
        assert [peak['ell_peak'] for peak in peaks] == ELL_PEAKS


class TestBaryonLoadingCorrection:
    def test_positive(self):
        assert baryon_loading_correction() > 0.0

    def test_below_one(self):
        assert baryon_loading_correction() < 1.0

    def test_formula(self):
        assert baryon_loading_correction() == pytest.approx(1.0 - Z_PHI_0 ** (-0.5))


class TestResidualBoundTightened:
    def test_old_value(self):
        assert residual_bound_tightened()['old_residual_pct'] == pytest.approx(26.0)

    def test_new_value(self):
        assert residual_bound_tightened()['new_residual_pct'] == pytest.approx(15.0)

    def test_new_smaller_than_old(self):
        data = residual_bound_tightened()
        assert data['new_residual_pct'] < data['old_residual_pct']

    def test_mechanism_mentions_running(self):
        assert 'running' in residual_bound_tightened()['mechanism']


class TestCMBPeakBoundVerdict:
    @pytest.mark.parametrize('key', ['status', 'peaks', 'residuals', 'bound', 'verdict'])
    def test_expected_keys_present(self, key):
        assert key in cmb_peak_bound_verdict()

    def test_status(self):
        assert cmb_peak_bound_verdict()['status'] == 'CMB_RESIDUAL_BOUNDED_15PCT'

    def test_bound_matches_new_value(self):
        assert cmb_peak_bound_verdict()['bound']['new_residual_pct'] == pytest.approx(15.0)

    def test_verdict_mentions_fifteen_percent(self):
        assert '15%' in cmb_peak_bound_verdict()['verdict']
