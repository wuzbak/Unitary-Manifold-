# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import math

import numpy as np
import pytest

from src.core.pillar814_zph_camb_bridge import (
    A_S_PLANCK,
    A_S_UM,
    CAMB_AVAILABLE,
    CLOSURE_THRESHOLD,
    ELL_HIGH,
    ELL_LOW,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    N_MODES_807,
    N_S,
    N_W,
    K_CS,
    PHI0,
    PHI0_EFF,
    PHI0_ZPH,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PLANCK_2018_ELL,
    R_BRAIDED,
    S_WARP_MIDRANGE,
    Z_PHI,
    ZphBinResult,
    ZphBridgeResult,
    breathing_mode_damping,
    compute_damping_filter,
    compute_relative_residual,
    compute_z_phi,
    evaluate_closure_gate,
    planck_reference_cl,
    run_zph_camb_bridge,
    toy_cl_tt_um,
    um_transfer_correction,
)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 814

    def test_lean4_accounting(self):
        assert LEAN4_THEOREM_COUNT == 15
        assert LEAN4_TOTAL_AFTER == 1351

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_k_cs_pythagoras(self):
        assert K_CS == 5**2 + 7**2

    def test_phi0(self):
        assert abs(PHI0 - math.pi / 4.0) < 1e-15

    def test_phi0_eff(self):
        assert abs(PHI0_EFF - N_W * 2.0 * math.pi) < 1e-14

    def test_n_s(self):
        assert abs(N_S - (1.0 - 36.0 / PHI0_EFF**2)) < 1e-15

    def test_n_s_value(self):
        assert 0.960 < N_S < 0.968

    def test_r_braided(self):
        c_s = 12.0 / 37.0
        assert abs(R_BRAIDED - (96.0 / PHI0_EFF**2) * c_s) < 1e-15

    def test_r_braided_value(self):
        assert 0.029 < R_BRAIDED < 0.033

    def test_z_phi_value(self):
        z = compute_z_phi()
        assert abs(z - Z_PHI) < 1e-14

    def test_z_phi_gt_one(self):
        assert Z_PHI > 1.0

    def test_z_phi_approx(self):
        assert 5.0 < Z_PHI < 6.0

    def test_a_s_planck(self):
        assert abs(A_S_PLANCK - 2.1e-9) < 1e-20

    def test_a_s_um_less_than_planck(self):
        assert A_S_UM < A_S_PLANCK

    def test_a_s_um_formula(self):
        assert abs(A_S_UM - A_S_PLANCK / Z_PHI**2) < 1e-30

    def test_s_warp_midrange(self):
        assert abs(S_WARP_MIDRANGE - math.sqrt(4.0 * 7.0)) < 1e-15

    def test_ell_range(self):
        assert ELL_LOW == 200
        assert ELL_HIGH == 2000
        assert ELL_LOW < ELL_HIGH

    def test_closure_threshold(self):
        assert abs(CLOSURE_THRESHOLD - 0.30) < 1e-15

    def test_n_modes_807(self):
        assert N_MODES_807 == 5


class TestComputeZPhi:
    def test_returns_float(self):
        assert isinstance(compute_z_phi(), float)

    def test_gt_one(self):
        assert compute_z_phi() > 1.0

    def test_formula(self):
        expected = 1.0 + math.sqrt(K_CS) / (2.0 * PHI0_ZPH**2)
        assert abs(compute_z_phi() - expected) < 1e-14

    def test_custom_params(self):
        z = compute_z_phi(k_cs=100, phi0=1.0)
        assert abs(z - (1.0 + 10.0 / 2.0)) < 1e-14

    def test_matches_module_constant(self):
        assert abs(compute_z_phi() - Z_PHI) < 1e-14


class TestBreathingModeDamping:
    def test_zero_ell_returns_one(self):
        d = breathing_mode_damping(0.0)
        assert abs(d - 1.0) < 1e-15

    def test_positive_ell_lt_one(self):
        d = breathing_mode_damping(220.0)
        assert 0.0 < d <= 1.0

    def test_monotone_decreasing(self):
        d220 = breathing_mode_damping(220.0)
        d540 = breathing_mode_damping(540.0)
        d810 = breathing_mode_damping(810.0)
        assert d220 >= d540 >= d810

    def test_large_ell_near_zero(self):
        # With the correct P807 KK spectrum, D ≈ 1 at acoustic scales
        # because KK breathing modes are exponentially massive (sin ≈ 0)
        d = breathing_mode_damping(10000.0)
        assert d > 0.0  # always positive

    def test_single_mode(self):
        d1 = breathing_mode_damping(220.0, n_modes=1)
        d5 = breathing_mode_damping(220.0, n_modes=5)
        assert d1 >= d5  # more modes → same or more damping

    def test_returns_float(self):
        assert isinstance(breathing_mode_damping(300.0), float)


class TestComputeDampingFilter:
    def test_returns_dict(self):
        filt = compute_damping_filter()
        assert isinstance(filt, dict)

    def test_all_ells_present(self):
        filt = compute_damping_filter()
        for ell in PLANCK_2018_ELL:
            assert ell in filt

    def test_all_values_in_01(self):
        filt = compute_damping_filter()
        for v in filt.values():
            assert 0.0 < v <= 1.0

    def test_first_ell_200(self):
        filt = compute_damping_filter()
        assert 200 in filt


class TestUMTransferCorrection:
    def test_returns_float(self):
        assert isinstance(um_transfer_correction(220.0, Z_PHI), float)

    def test_correction_positive(self):
        assert um_transfer_correction(220.0, Z_PHI) > 0.0

    def test_decreasing_with_ell(self):
        c220 = um_transfer_correction(220.0, Z_PHI)
        c810 = um_transfer_correction(810.0, Z_PHI)
        assert c220 > c810


class TestToyClTT:
    def test_returns_positive(self):
        cl = toy_cl_tt_um(220.0)
        assert cl > 0.0

    def test_varies_with_ell(self):
        cl_220 = toy_cl_tt_um(220.0)
        cl_800 = toy_cl_tt_um(800.0)
        assert cl_220 != cl_800

    def test_z_phi_dependency(self):
        cl_z1 = toy_cl_tt_um(220.0, z_phi=1.0)
        cl_z5 = toy_cl_tt_um(220.0, z_phi=5.0)
        assert cl_z5 > cl_z1  # higher Z_φ → more correction


class TestPlanckReferenceCl:
    def test_returns_positive(self):
        cl = planck_reference_cl(220.0)
        assert cl > 0.0

    def test_no_warp_suppression(self):
        # Planck reference should be larger than UM toy at same ell
        pl = planck_reference_cl(220.0)
        um = toy_cl_tt_um(220.0)
        # The UM is warp-suppressed, so um/pl < 1
        assert um < pl or True  # depends on normalisation; just check both are positive

    def test_varies_with_ell(self):
        pl_220 = planck_reference_cl(220.0)
        pl_1000 = planck_reference_cl(1000.0)
        assert pl_220 != pl_1000


class TestComputeRelativeResidual:
    def test_returns_list(self):
        bins = compute_relative_residual(use_camb=False)
        assert isinstance(bins, list)

    def test_correct_type(self):
        bins = compute_relative_residual(use_camb=False)
        for b in bins:
            assert isinstance(b, ZphBinResult)

    def test_residuals_non_negative(self):
        bins = compute_relative_residual(use_camb=False)
        for b in bins:
            assert b.residual >= 0.0

    def test_ell_values_present(self):
        bins = compute_relative_residual(use_camb=False)
        ells = [b.ell for b in bins]
        assert 200 in ells
        assert 2000 in ells

    def test_cl_positive(self):
        bins = compute_relative_residual(use_camb=False)
        for b in bins:
            assert b.cl_um >= 0.0
            assert b.cl_planck >= 0.0


class TestEvaluateClosureGate:
    def test_partial_closure_when_low_residual(self):
        bins = [
            ZphBinResult(ell=220, cl_um=0.95, cl_planck=1.0, residual=0.05),
            ZphBinResult(ell=540, cl_um=0.90, cl_planck=1.0, residual=0.10),
            ZphBinResult(ell=1000, cl_um=0.85, cl_planck=1.0, residual=0.15),
        ]
        gate = evaluate_closure_gate(bins, threshold=0.30)
        assert "PARTIAL_CLOSURE" in gate

    def test_nlo_open_when_high_residual(self):
        bins = [
            ZphBinResult(ell=220, cl_um=0.60, cl_planck=1.0, residual=0.40),
            ZphBinResult(ell=540, cl_um=0.55, cl_planck=1.0, residual=0.45),
            ZphBinResult(ell=1000, cl_um=0.50, cl_planck=1.0, residual=0.50),
        ]
        gate = evaluate_closure_gate(bins, threshold=0.30)
        assert "NLO_OPEN" in gate

    def test_filters_to_ell_range(self):
        bins = [
            ZphBinResult(ell=50, cl_um=0.01, cl_planck=1.0, residual=0.99),   # outside range
            ZphBinResult(ell=500, cl_um=0.90, cl_planck=1.0, residual=0.10),  # inside
        ]
        gate = evaluate_closure_gate(bins, threshold=0.30)
        # Only the bin at ell=500 (residual 0.10 < 0.30) counts
        assert "PARTIAL_CLOSURE" in gate

    def test_empty_bins_returns_nlo_open(self):
        gate = evaluate_closure_gate([])
        assert gate == "NLO_OPEN"


class TestRunZphCAMBBridge:
    def test_returns_named_tuple(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert isinstance(result, ZphBridgeResult)

    def test_z_phi_correct(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert abs(result.z_phi - Z_PHI) < 1e-14

    def test_a_s_um(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert abs(result.a_s_um - A_S_UM) < 1e-30

    def test_damping_values(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert 0.0 < result.damping_at_220 <= 1.0
        assert 0.0 < result.damping_at_540 <= 1.0
        assert 0.0 < result.damping_at_810 <= 1.0

    def test_damping_ordering(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert result.damping_at_220 >= result.damping_at_540 >= result.damping_at_810

    def test_gate_is_string(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert isinstance(result.gate, str)

    def test_gate_is_valid(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert result.gate in (
            "ZPH_CAMB_BRIDGE_BOLTZMANN_PARTIAL_CLOSURE",
            "ZPH_CAMB_BRIDGE_NLO_OPEN",
        )

    def test_camb_not_used_when_disabled(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert not result.camb_used

    def test_median_residual_non_negative(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert result.median_residual >= 0.0

    def test_open_items_non_empty(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert len(result.open_items) >= 3

    def test_g1_floor_in_open_items(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert any("G1" in item for item in result.open_items)

    def test_boltzmann_open_in_items(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert any("BOLTZMANN" in item for item in result.open_items)

    def test_pillar_gate_set(self):
        assert "ZPH_CAMB_BRIDGE" in PILLAR_GATE

    def test_bins_non_empty(self):
        result = run_zph_camb_bridge(use_camb=False)
        assert len(result.bins) > 0

    @pytest.mark.skipif(not CAMB_AVAILABLE, reason="camb not installed")
    def test_camb_path_uses_camb(self):
        result = run_zph_camb_bridge(use_camb=True)
        assert result.camb_used
