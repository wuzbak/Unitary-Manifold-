# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar362_transplanckian_kk_quadrupole.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar362_transplanckian_kk_quadrupole import (
    PILLAR_NUMBER, PILLAR_STATUS, M_KK_EV, K_KK_MPC, K_ELL2_MPC, TAU0_MPC,
    BRAID_SUPPRESSION_PCT, OBSERVED_DEFICIT_PCT,
    separation_guard, kk_physical_wavenumber_mpc, quadrupole_wavenumber_mpc,
    scale_ratio_kk_to_ell2, transplanckian_power_correction,
    braid_quadrupole_suppression, quadrupole_deficit_analysis, pillar362_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 362
    def test_status(self): assert PILLAR_STATUS == "MECHANISM_INCONCLUSIVE"
    def test_m_kk_positive(self): assert M_KK_EV > 0
    def test_k_kk_much_larger_than_ell2(self): assert K_KK_MPC > K_ELL2_MPC * 1e10
    def test_braid_suppression(self): assert abs(BRAID_SUPPRESSION_PCT - 6.8) < 0.5
    def test_observed_deficit(self): assert 30 < OBSERVED_DEFICIT_PCT < 60


class TestScaleRatio:
    def test_ratio_huge(self):
        ratio = scale_ratio_kk_to_ell2()
        assert ratio > 1e15   # ~25 orders of magnitude

    def test_k_kk_large(self):
        k_kk = kk_physical_wavenumber_mpc()
        assert k_kk > 1.0   # [Mpc⁻¹] — much larger than CMB scales

    def test_k_ell2_tiny(self):
        k_ell2 = quadrupole_wavenumber_mpc()
        assert k_ell2 < 1e-3   # [Mpc⁻¹]


class TestTransplanckianCorrection:
    def test_zero_below_kk(self):
        # k < k_KK → no suppression of low-ℓ modes
        tc = transplanckian_power_correction(1e-4)  # k_ell2 << k_KK
        assert tc == 0.0

    def test_negative_above_kk(self):
        tc = transplanckian_power_correction(2 * K_KK_MPC, K_KK_MPC)
        assert tc < 0

    def test_ell2_not_affected(self):
        tc = transplanckian_power_correction(K_ELL2_MPC, K_KK_MPC)
        assert tc == 0.0  # ℓ=2 mode is far below k_KK


class TestBraidSuppression:
    def test_positive(self): assert braid_quadrupole_suppression() > 0
    def test_value(self): assert abs(braid_quadrupole_suppression() - 6.8) < 0.5


class TestDeficitAnalysis:
    def test_returns_dict(self): assert isinstance(quadrupole_deficit_analysis(), dict)
    def test_mechanism_inconclusive(self):
        result = quadrupole_deficit_analysis()
        assert "INCONCLUSIVE" in result["mechanism_verdict"]
    def test_open_gap(self):
        result = quadrupole_deficit_analysis()
        assert "OPEN" in result["open_gap_status"]
    def test_remaining_gap_positive(self):
        result = quadrupole_deficit_analysis()
        assert result["remaining_gap_pct"][0] > 0
        assert result["remaining_gap_pct"][1] > 0


class TestSummary:
    def test_pillar_362(self): assert pillar362_summary()["pillar"] == 362
    def test_status(self): assert pillar362_summary()["status"] == "MECHANISM_INCONCLUSIVE"
    def test_key_conclusion(self): assert "INCONCLUSIVE" in pillar362_summary()["key_conclusion"]


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_frontier(self): assert "FRONTIER_COMPUTATION" in separation_guard()
