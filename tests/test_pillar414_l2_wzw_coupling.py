# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 414 — L2 γ WZW Coupling Derivation."""
import math
import pytest

from src.core.pillar414_l2_wzw_coupling import (
    PILLAR_STATUS,
    L2_STATUS,
    K_CS,
    PHI0_FULL,
    GAMMA_THEORY,
    GAMMA_FIT,
    GAMMA_GAP,
    wzw_zero_mode_coupling,
    l2_wzw_delta_gamma,
    c1_wzw_budget,
    l2_wzw_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'L2_WZW_COUPLING_BOUNDED'

    def test_l2_status(self):
        assert L2_STATUS == 'L2_WZW_COUPLING_BOUNDED'

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi0_full(self):
        assert PHI0_FULL == pytest.approx(31.416)

    def test_gamma_theory(self):
        assert GAMMA_THEORY == pytest.approx(0.242)

    def test_gamma_fit(self):
        assert GAMMA_FIT == pytest.approx(0.273)

    def test_gamma_gap_formula(self):
        assert GAMMA_GAP == pytest.approx(GAMMA_FIT - GAMMA_THEORY)

    def test_gamma_gap_positive(self):
        assert GAMMA_GAP > 0.0


class TestWZWZeroModeCoupling:
    @pytest.mark.parametrize('k_cs', [74, 10, 20, 37, 148, 200, 1, 12, 95])
    def test_returns_expected_formula(self, k_cs):
        data = wzw_zero_mode_coupling(k_cs)
        assert data['g_braid_WZW'] == pytest.approx((k_cs + 2.0) / (2.0 * k_cs))

    @pytest.mark.parametrize('k_cs', [74, 37, 148, 20, 95, 11, 50, 99, 5])
    def test_conformal_dimension_formula(self, k_cs):
        data = wzw_zero_mode_coupling(k_cs)
        assert data['conformal_dim'] == pytest.approx(k_cs / (k_cs + 2.0))

    @pytest.mark.parametrize('key', ['K_cs', 'g_braid_WZW', 'conformal_dim', 'coupling_derivation'])
    def test_expected_keys_present(self, key):
        assert key in wzw_zero_mode_coupling()

    def test_canonical_value(self):
        assert wzw_zero_mode_coupling()['g_braid_WZW'] == pytest.approx(76.0 / 148.0)

    def test_coupling_is_order_one(self):
        value = wzw_zero_mode_coupling()['g_braid_WZW']
        assert 0.1 < value < 2.0

    def test_canonical_conformal_dimension_below_one(self):
        assert 0.0 < wzw_zero_mode_coupling()['conformal_dim'] < 1.0

    def test_larger_k_reduces_coupling_toward_half(self):
        low = wzw_zero_mode_coupling(10)['g_braid_WZW']
        high = wzw_zero_mode_coupling(148)['g_braid_WZW']
        assert low > high > 0.5

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            wzw_zero_mode_coupling(0)


class TestL2WZWDeltaGamma:
    @pytest.mark.parametrize('k_cs', [74, 37, 148, 20, 50, 99, 5, 12, 88])
    def test_delta_gamma_positive(self, k_cs):
        assert l2_wzw_delta_gamma(k_cs)['delta_gamma_zm'] > 0.0

    @pytest.mark.parametrize('k_cs', [74, 37, 148, 20, 50, 99, 88, 120, 200])
    def test_fraction_is_subunity_for_tested_scales(self, k_cs):
        assert l2_wzw_delta_gamma(k_cs)['gamma_gap_fraction'] < 1.0

    @pytest.mark.parametrize('key', ['K_cs', 'phi0', 'g_braid_WZW', 'zero_mode_variance_ratio', 'delta_gamma_zm', 'gamma_gap_fraction', 'c1_zm'])
    def test_expected_keys_present(self, key):
        assert key in l2_wzw_delta_gamma()

    def test_canonical_delta_gamma_value(self):
        expected = math.pi / (4.0 * K_CS) * (76.0 / 148.0)
        assert l2_wzw_delta_gamma()['delta_gamma_zm'] == pytest.approx(expected)

    def test_canonical_fraction_value(self):
        data = l2_wzw_delta_gamma()
        assert data['gamma_gap_fraction'] == pytest.approx(data['delta_gamma_zm'] / GAMMA_GAP)

    def test_canonical_c1_value(self):
        expected = (76.0 / 148.0) * K_CS / (2.0 * math.pi)
        assert l2_wzw_delta_gamma()['c1_zm'] == pytest.approx(expected)

    def test_phi0_argument_passes_through(self):
        assert l2_wzw_delta_gamma(phi0=40.0)['phi0'] == pytest.approx(40.0)

    def test_smaller_k_gives_larger_delta_gamma(self):
        assert l2_wzw_delta_gamma(37)['delta_gamma_zm'] > l2_wzw_delta_gamma(74)['delta_gamma_zm']


class TestC1WZWBudget:
    @pytest.mark.parametrize('key', ['c1_km', 'c1_zm_wzw', 'c1_total', 'fraction_explained', 'residual'])
    def test_expected_keys_present(self, key):
        assert key in c1_wzw_budget()

    def test_c1_km_value(self):
        assert c1_wzw_budget()['c1_km'] == pytest.approx(3.02)

    def test_c1_total_value(self):
        assert c1_wzw_budget()['c1_total'] == pytest.approx(12.5)

    def test_fraction_explained_above_half(self):
        assert c1_wzw_budget()['fraction_explained'] > 0.5

    def test_fraction_explained_matches_sum(self):
        data = c1_wzw_budget()
        assert data['fraction_explained'] == pytest.approx((data['c1_km'] + data['c1_zm_wzw']) / data['c1_total'])

    def test_residual_positive(self):
        assert c1_wzw_budget()['residual'] > 0.0

    def test_residual_less_than_total(self):
        data = c1_wzw_budget()
        assert data['residual'] < data['c1_total']

    def test_c1_zm_matches_delta_function(self):
        assert c1_wzw_budget()['c1_zm_wzw'] == pytest.approx(l2_wzw_delta_gamma()['c1_zm'])

    def test_explained_sum_below_total(self):
        data = c1_wzw_budget()
        assert data['c1_km'] + data['c1_zm_wzw'] < data['c1_total']


class TestL2WZWVerdict:
    @pytest.mark.parametrize('key', ['status', 'previous_status', 'gamma_theory', 'gamma_fit', 'g_braid_wzw', 'c1_explained_fraction', 'residual_bounded', 'verdict'])
    def test_expected_keys_present(self, key):
        assert key in l2_wzw_verdict()

    def test_status(self):
        assert l2_wzw_verdict()['status'] == 'L2_WZW_COUPLING_BOUNDED'

    def test_previous_status(self):
        assert l2_wzw_verdict()['previous_status'] == 'L2_CONDENSATE_ZERO_MODE_VIABLE'

    def test_gamma_values(self):
        verdict = l2_wzw_verdict()
        assert verdict['gamma_theory'] == pytest.approx(GAMMA_THEORY)
        assert verdict['gamma_fit'] == pytest.approx(GAMMA_FIT)

    def test_g_braid_matches_derivation(self):
        assert l2_wzw_verdict()['g_braid_wzw'] == pytest.approx(wzw_zero_mode_coupling()['g_braid_WZW'])

    def test_explained_fraction_above_half(self):
        assert l2_wzw_verdict()['c1_explained_fraction'] > 0.5

    def test_residual_is_bounded(self):
        assert l2_wzw_verdict()['residual_bounded'] is True

    def test_verdict_mentions_wzw(self):
        assert 'WZW' in l2_wzw_verdict()['verdict']
