# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 826 — KK Tower Heat-Kernel Regularization."""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.special import zeta as riemann_zeta

from src.core.pillar826_kk_tower_heat_kernel_regularization import (
    CASIMIR_ENERGY_COEFFICIENT,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_W,
    K_CS,
    PHI_0,
    PILLAR_GATE_ISW,
    PILLAR_GATE_TOWER,
    PILLAR_NUMBER,
    R_KK_DEFAULT,
    T55_ZETA_COEFFICIENT,
    TRAPPING_COEFFICIENT,
    ZETA_M1,
    ZETA_M3,
    TowerStressEnergyResult,
    dark_radiation_trapping_rate,
    kk_tower_casimir_check,
    kk_tower_regulated_summary,
    kk_tower_isw_correction,
    tower_heat_kernel_tmunu,
    tower_mode_convergence_rate,
    unitarity_buffer_factor,
)


class TestPillar826Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 826

    def test_gate_tower(self):
        assert PILLAR_GATE_TOWER == "KK_TOWER_HEAT_KERNEL_REGULATED"

    def test_gate_isw(self):
        assert PILLAR_GATE_ISW == "KK_TOWER_ISW_EXPONENTIALLY_BOUNDED"

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi_0(self):
        assert PHI_0 == 37.0

    def test_kcs_from_braid(self):
        assert K_CS == N_W**2 + 7**2

    def test_lean4_count(self):
        assert LEAN4_THEOREM_COUNT == 35

    def test_lean4_before(self):
        assert LEAN4_TOTAL_BEFORE == 1506

    def test_lean4_after(self):
        assert LEAN4_TOTAL_AFTER == 1541

    def test_lean4_accumulates(self):
        assert LEAN4_TOTAL_AFTER == LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

    def test_zeta_m3_value(self):
        # ζ(−3) = 1/120
        assert abs(float(ZETA_M3) - 1.0 / 120.0) < 1e-12

    def test_zeta_m1_value(self):
        # ζ(−1) = −1/12
        assert abs(float(ZETA_M1) - (-1.0 / 12.0)) < 1e-12

    def test_t55_coefficient(self):
        # T55_ZETA_COEFFICIENT = ζ(−3) = 1/120
        assert abs(T55_ZETA_COEFFICIENT - 1.0 / 120.0) < 1e-12

    def test_casimir_coefficient(self):
        assert abs(CASIMIR_ENERGY_COEFFICIENT - 1.0 / 120.0) < 1e-12

    def test_trapping_coefficient(self):
        # n_w²/K_CS = 25/74
        expected = N_W**2 / K_CS
        assert abs(TRAPPING_COEFFICIENT - expected) < 1e-12

    def test_trapping_positive(self):
        assert TRAPPING_COEFFICIENT > 0


class TestTowerHeatKernelTmunu:
    def test_basic_call(self):
        result = tower_heat_kernel_tmunu()
        assert isinstance(result, TowerStressEnergyResult)

    def test_t55_positive(self):
        result = tower_heat_kernel_tmunu()
        assert result.T55 > 0

    def test_t00_positive(self):
        result = tower_heat_kernel_tmunu()
        assert result.T00 > 0

    def test_tii_positive(self):
        result = tower_heat_kernel_tmunu()
        assert result.T_ii > 0

    def test_t55_formula(self):
        R = 1.0
        result = tower_heat_kernel_tmunu(phi=PHI_0, R_KK=R)
        expected_T55 = float(ZETA_M3) / (2.0 * R**4)
        assert abs(result.T55 - expected_T55) < 1e-12

    def test_t00_formula(self):
        R = 1.0
        result = tower_heat_kernel_tmunu(phi=PHI_0, R_KK=R)
        expected_T00 = float(ZETA_M3) / (4.0 * R**4)
        assert abs(result.T00 - expected_T00) < 1e-12

    def test_t55_t00_ratio(self):
        result = tower_heat_kernel_tmunu()
        # T55 = ζ/(2R⁴), T00 = ζ/(4R⁴) → T55/T00 = 2
        assert abs(result.T55 / result.T00 - 2.0) < 1e-10

    def test_t00_tii_ratio(self):
        result = tower_heat_kernel_tmunu()
        # T00 = ζ/(4R⁴), Tii = ζ/(12R⁴) → T00/Tii = 3
        assert abs(result.T00 / result.T_ii - 3.0) < 1e-10

    def test_gate_returned(self):
        result = tower_heat_kernel_tmunu()
        assert result.gate == PILLAR_GATE_TOWER

    def test_zeta_m3_in_result(self):
        result = tower_heat_kernel_tmunu()
        assert abs(result.zeta_m3 - 1.0 / 120.0) < 1e-12

    def test_r_scaling(self):
        R1 = 1.0
        R2 = 2.0
        r1 = tower_heat_kernel_tmunu(phi=PHI_0, R_KK=R1)
        r2 = tower_heat_kernel_tmunu(phi=PHI_0, R_KK=R2)
        # T55 ~ 1/R⁴
        assert abs(r1.T55 / r2.T55 - (R2 / R1)**4) < 1e-10

    def test_phi_scaling(self):
        # Effective R ~ phi/phi0 * R_KK
        r1 = tower_heat_kernel_tmunu(phi=PHI_0, R_KK=1.0)
        r2 = tower_heat_kernel_tmunu(phi=2 * PHI_0, R_KK=1.0)
        # R_eff doubles → T55 drops by factor 16
        assert abs(r1.T55 / r2.T55 - 16.0) < 1e-8

    def test_invalid_phi(self):
        with pytest.raises(ValueError):
            tower_heat_kernel_tmunu(phi=-1.0)

    def test_invalid_R(self):
        with pytest.raises(ValueError):
            tower_heat_kernel_tmunu(R_KK=-1.0)

    def test_invalid_sUV(self):
        with pytest.raises(ValueError):
            tower_heat_kernel_tmunu(s_UV=-1.0)


class TestKKTowerISWCorrection:
    def test_basic_call(self):
        result = kk_tower_isw_correction()
        assert isinstance(result, dict)

    def test_sub_threshold(self):
        result = kk_tower_isw_correction(ell=100.0)
        assert result["is_sub_threshold"]

    def test_gate(self):
        result = kk_tower_isw_correction()
        assert result["gate"] == PILLAR_GATE_ISW

    def test_correction_positive(self):
        result = kk_tower_isw_correction()
        assert result["delta_cl_over_cl"] >= 0

    def test_suppression_exp_negative(self):
        result = kk_tower_isw_correction()
        assert result["suppression_exp"] < 0

    def test_m1_over_H_large(self):
        result = kk_tower_isw_correction(H_inf=1e-5)
        # m_1 = 1/R_KK = 1 at defaults; H = 1e-5 → ratio = 1e5
        assert result["m1_over_H"] > 1e4

    def test_sub_threshold_all_ell(self):
        for ell in [2, 10, 100, 1000]:
            result = kk_tower_isw_correction(ell=float(ell))
            assert result["is_sub_threshold"], f"ell={ell} not sub-threshold"

    def test_total_series_bound_finite(self):
        result = kk_tower_isw_correction()
        assert np.isfinite(result["total_series_bound"])

    def test_invalid_ell(self):
        with pytest.raises(ValueError):
            kk_tower_isw_correction(ell=0.5)


class TestDarkRadiationTrappingRate:
    def test_basic_call(self):
        result = dark_radiation_trapping_rate()
        assert isinstance(result, dict)

    def test_is_irreversible(self):
        result = dark_radiation_trapping_rate(E_event=2.0)
        assert result["is_irreversible"]

    def test_delta_trap_value(self):
        result = dark_radiation_trapping_rate()
        assert abs(result["delta_trap"] - N_W**2 / K_CS) < 1e-12

    def test_dark_radiation_rate_positive(self):
        result = dark_radiation_trapping_rate(E_event=2.0)
        assert result["dE_DR_dt"] >= 0

    def test_entropy_production_positive(self):
        result = dark_radiation_trapping_rate(E_event=2.0)
        assert result["dS_DR_dt"] >= 0

    def test_zero_event_energy(self):
        result = dark_radiation_trapping_rate(E_event=0.0)
        assert result["dE_DR_dt"] == 0.0

    def test_invalid_energy(self):
        with pytest.raises(ValueError):
            dark_radiation_trapping_rate(E_event=-1.0)

    def test_m_kk_from_R(self):
        R = 2.0
        result = dark_radiation_trapping_rate(R_KK=R)
        assert abs(result["m_KK"] - PHI_0 / (R * PHI_0)) < 1e-10


class TestUnitarityBufferFactor:
    def test_basic_call(self):
        result = unitarity_buffer_factor()
        assert isinstance(result, dict)

    def test_buffer_at_zero_energy(self):
        # At E→0, no modes are above threshold, B_finite = 1
        result = unitarity_buffer_factor(E=1e-10)
        assert result["buffer_factor_finite_N"] == 1.0

    def test_buffer_regulated_formula(self):
        # B_reg = 1 − x²/12 with x = E * R_KK
        E, R = 0.5, 1.0
        result = unitarity_buffer_factor(E=E, R_KK=R)
        expected = max(0.0, 1.0 - (E * R)**2 / 12.0)
        assert abs(result["buffer_factor_regulated"] - expected) < 1e-10

    def test_saturation_energy_formula(self):
        R = 1.0
        result = unitarity_buffer_factor(E=1.0, R_KK=R)
        expected_sat = math.sqrt(12.0) / R
        assert abs(result["E_sat_unitarity"] - expected_sat) < 1e-10

    def test_buffer_non_negative(self):
        for E in [0.1, 1.0, 2.0]:
            result = unitarity_buffer_factor(E=E)
            assert result["buffer_factor_regulated"] >= 0
            assert result["buffer_factor_finite_N"] >= 0

    def test_invalid_energy(self):
        with pytest.raises(ValueError):
            unitarity_buffer_factor(E=0.0)

    def test_gate(self):
        result = unitarity_buffer_factor()
        assert result["gate"] == "KK_UNITARITY_BUFFER_QUANTIFIED"


class TestKKTowerCasimirCheck:
    def test_basic_call(self):
        result = kk_tower_casimir_check()
        assert isinstance(result, dict)

    def test_ratio_match(self):
        result = kk_tower_casimir_check()
        assert result["ratio_match"]

    def test_t55_positive(self):
        result = kk_tower_casimir_check()
        assert result["T55_regulated"] > 0

    def test_casimir_negative(self):
        result = kk_tower_casimir_check()
        assert result["rho_casimir"] < 0

    def test_ratio_formula(self):
        result = kk_tower_casimir_check()
        expected = 90.0 / (240.0 * math.pi**2)
        assert abs(result["expected_ratio"] - expected) < 1e-12

    def test_zeta_m3_in_result(self):
        result = kk_tower_casimir_check()
        assert abs(result["zeta_m3"] - 1.0 / 120.0) < 1e-12


class TestTowerModeConvergence:
    def test_basic_call(self):
        result = tower_mode_convergence_rate(N_modes=10)
        assert isinstance(result, dict)

    def test_divergence_confirmed(self):
        result = tower_mode_convergence_rate(N_modes=15)
        assert result["divergence_without_regulation_confirmed"]

    def test_partial_sums_length(self):
        N = 10
        result = tower_mode_convergence_rate(N_modes=N)
        assert len(result["partial_sums"]) == N

    def test_regulated_limit_positive(self):
        result = tower_mode_convergence_rate()
        assert result["zeta_regulated_limit"] > 0


class TestKKTowerRegulatedSummary:
    def test_basic_call(self):
        result = kk_tower_regulated_summary()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = kk_tower_regulated_summary()
        assert result["pillar"] == 826

    def test_gates_closed(self):
        result = kk_tower_regulated_summary()
        assert PILLAR_GATE_TOWER in result["gates_closed"]
        assert PILLAR_GATE_ISW in result["gates_closed"]

    def test_isw_sub_threshold(self):
        result = kk_tower_regulated_summary()
        assert result["isw_correction_sub_threshold"]

    def test_dark_radiation_irreversible(self):
        result = kk_tower_regulated_summary()
        assert result["dark_radiation_is_irreversible"]

    def test_casimir_ratio_match(self):
        result = kk_tower_regulated_summary()
        assert result["casimir_ratio_match"]

    def test_lean4_total(self):
        result = kk_tower_regulated_summary()
        assert result["lean4_total_after"] == 1541

    def test_remaining_open_honest(self):
        result = kk_tower_regulated_summary()
        assert len(result["remaining_open"]) >= 1

    def test_t55_positive(self):
        result = kk_tower_regulated_summary()
        assert result["T55_regulated"] > 0

    def test_unitarity_buffer_non_negative(self):
        result = kk_tower_regulated_summary()
        assert result["unitarity_buffer_regulated"] >= 0
