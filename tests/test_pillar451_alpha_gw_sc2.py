# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 451 — α_GW SC2 Interval Narrowing."""
import pytest
from src.core.pillar451_alpha_gw_sc2_narrowing import (
    PILLAR_STATUS, VERSION,
    ALPHA_GW_5D, ALPHA_GW_P280_LOW, ALPHA_GW_P280_HIGH, ALPHA_GW_P280_WIDTH,
    N_FLUX, K_CS, R_BRAIDED,
    Z_TRANSFER_MIN, Z_TRANSFER_MAX,
    alpha_gw_5d_prediction, uv_correction_10d, nt_constraint_shift,
    narrowed_interval, sc2_status, pillar_report,
)


class TestConstants:
    def test_p280_interval_ordering(self):
        assert ALPHA_GW_P280_LOW < ALPHA_GW_P280_HIGH

    def test_p280_width_positive(self):
        assert ALPHA_GW_P280_WIDTH > 0

    def test_n_flux_37(self):
        assert N_FLUX == 37

    def test_r_braided(self):
        assert abs(R_BRAIDED - 0.0315) < 1e-4

    def test_transfer_range(self):
        assert Z_TRANSFER_MIN < 1.0 < Z_TRANSFER_MAX


class TestAlphaGW5D:
    def test_returns_dict(self):
        r = alpha_gw_5d_prediction()
        assert isinstance(r, dict)

    def test_has_calibrated_value(self):
        r = alpha_gw_5d_prediction()
        assert 'alpha_gw_calibrated' in r

    def test_calibrated_in_p280_range(self):
        r = alpha_gw_5d_prediction()
        # Calibrated to P280 central value
        central = (ALPHA_GW_P280_LOW + ALPHA_GW_P280_HIGH) / 2
        assert abs(r['alpha_gw_calibrated'] - central) < 1e-20


class TestUVCorrection:
    def test_negligible(self):
        r = uv_correction_10d()
        assert r['is_negligible'] is True

    def test_sub_leading(self):
        r = uv_correction_10d()
        assert r['fraction_change'] < 0.001

    def test_n_flux_used(self):
        r = uv_correction_10d()
        assert r['n_flux'] == N_FLUX


class TestNtConstraintShift:
    def test_n_t_negative(self):
        r = nt_constraint_shift()
        assert r['n_t'] < 0  # tensor tilt must be negative

    def test_n_t_value(self):
        r = nt_constraint_shift()
        expected_nt = -R_BRAIDED / 8.0
        assert abs(r['n_t'] - expected_nt) < 1e-10

    def test_pivot_shift_zero(self):
        r = nt_constraint_shift()
        assert r['shift_at_k_pivot'] == 0.0


class TestNarrowedInterval:
    def test_new_interval_inside_p280(self):
        r = narrowed_interval()
        low, high = r['new_interval']
        # New interval should be within or near P280 interval
        assert low >= ALPHA_GW_P280_LOW - 1e-12
        assert high <= ALPHA_GW_P280_HIGH + 1e-12

    def test_new_width_lt_p280_width(self):
        r = narrowed_interval()
        assert r['new_width'] < r['p280_width']

    def test_width_reduction_positive(self):
        r = narrowed_interval()
        assert r['width_reduction_frac'] > 0

    def test_uv_consistency_certified(self):
        r = narrowed_interval()
        assert r['uv_consistency_certified'] is True

    def test_honest_outcome_present(self):
        r = narrowed_interval()
        assert 'honest_outcome' in r


class TestSC2Status:
    def test_sc2_label_present(self):
        r = sc2_status()
        assert 'sc2_label' in r

    def test_uv_safe(self):
        r = sc2_status()
        assert r['uv_safe'] is True

    def test_falsification_unchanged(self):
        r = sc2_status()
        assert r['falsification_unchanged'] is True

    def test_new_interval_present(self):
        r = sc2_status()
        assert 'new_interval_1e10' in r


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 451

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS
