# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import math

import pytest

from src.core.pillar816_alphas_nlo_winding_audit import (
    ALPHA_S_PDG,
    ALPHA_S_PDG_UNCERTAINTY,
    ALPHA_S_UM_ROUTE_A,
    B0_QCD,
    DELTA_PHI_OVER_M5,
    G2_FLOOR_LOWER_BOUND,
    G2_FLOOR_UPPER_BOUND,
    GAMMA_V,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    M_KK_GEV,
    M_Z_GEV,
    N_F_QUARKS,
    N_W,
    PILLAR_GATE,
    PILLAR_NUMBER,
    SWAMPLAND_BOUND,
    T_F_QUARK,
    TYPE_B_CONFIRMED,
    AlphaSAuditResult,
    RouteResult,
    alphas_nlo_winding_route_e,
    alphas_route_a,
    backreacted_mkk,
    backreacted_radion_alphas_shift,
    compute_full_alphas_audit,
    dglap_run_down,
    swampland_uncertainty,
)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 816

    def test_lean4_accounting(self):
        assert LEAN4_THEOREM_COUNT == 15
        assert LEAN4_TOTAL_AFTER == 1386

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_alpha_s_pdg(self):
        assert abs(ALPHA_S_PDG - 0.1179) < 1e-15

    def test_alpha_s_um_route_a(self):
        assert abs(ALPHA_S_UM_ROUTE_A - 0.068) < 1e-15

    def test_delta_phi_negative(self):
        assert DELTA_PHI_OVER_M5 < 0.0

    def test_delta_phi_value(self):
        assert abs(DELTA_PHI_OVER_M5 - (-32.2)) < 1e-15

    def test_swampland_bound(self):
        assert abs(SWAMPLAND_BOUND - 30.0) < 1e-15

    def test_swampland_tension(self):
        assert abs(DELTA_PHI_OVER_M5) > SWAMPLAND_BOUND

    def test_gamma_v(self):
        assert abs(GAMMA_V - 0.5) < 1e-15

    def test_b0_qcd(self):
        assert abs(B0_QCD - (11.0 - 2.0 * N_F_QUARKS / 3.0)) < 1e-15

    def test_b0_value(self):
        assert abs(B0_QCD - 7.0) < 1e-15

    def test_n_f_quarks(self):
        assert N_F_QUARKS == 6

    def test_t_f_quark(self):
        assert abs(T_F_QUARK - 0.5) < 1e-15

    def test_m_z(self):
        assert abs(M_Z_GEV - 91.19) < 1e-10

    def test_m_kk(self):
        assert abs(M_KK_GEV - 1000.0) < 1e-10


class TestDGLAPRunDown:
    def test_returns_smaller_value(self):
        alpha_high = 0.11
        alpha_low = dglap_run_down(alpha_high, M_KK_GEV, M_Z_GEV)
        assert alpha_low < alpha_high

    def test_formula_manual(self):
        alpha_high = 0.11
        m_h, m_l = 1000.0, 91.19
        log_r = math.log(m_h**2 / m_l**2)
        expected = alpha_high / (1.0 + (B0_QCD / (2.0 * math.pi)) * alpha_high * log_r)
        result = dglap_run_down(alpha_high, m_h, m_l)
        assert abs(result - expected) < 1e-15

    def test_large_separation(self):
        alpha_mz = dglap_run_down(0.11, 1000.0, 91.19)
        # One-loop DGLAP from 0.11 at 1 TeV to M_Z gives ~0.069
        assert 0.05 < alpha_mz < 0.12

    def test_raises_on_inverted_scales(self):
        with pytest.raises(ValueError):
            dglap_run_down(0.11, 91.19, 1000.0)

    def test_asymptotic_freedom(self):
        # Higher scale → smaller coupling
        alpha_1 = dglap_run_down(0.11, 1000.0, 91.19)
        alpha_2 = dglap_run_down(0.11, 10000.0, 91.19)
        assert alpha_1 > alpha_2


class TestBackreactedMKK:
    def test_returns_positive(self):
        assert backreacted_mkk() > 0.0

    def test_larger_than_nominal(self):
        # Δφ < 0 → V_eff < V₀ → M_KK^eff > M_KK^(0)
        assert backreacted_mkk() > M_KK_GEV

    def test_formula(self):
        expected = M_KK_GEV * math.exp(-DELTA_PHI_OVER_M5 * GAMMA_V)
        assert abs(backreacted_mkk() - expected) < 1e-6

    def test_custom_params(self):
        mkk_eff = backreacted_mkk(mkk_nominal=1000.0, delta_phi_over_m5=-1.0, gamma_v=0.5)
        assert abs(mkk_eff - 1000.0 * math.exp(0.5)) < 1e-6


class TestAlphaSRouteA:
    def test_returns_named_tuple(self):
        result = alphas_route_a()
        assert isinstance(result, RouteResult)

    def test_name(self):
        assert alphas_route_a().name == "Route_A_AdS_QCD"

    def test_predicted_below_pdg(self):
        assert alphas_route_a().alpha_s_predicted < ALPHA_S_PDG

    def test_residual_above_40_percent(self):
        assert alphas_route_a().residual_percent >= 40.0

    def test_residual_fraction_positive(self):
        assert alphas_route_a().residual_fraction > 0.0

    def test_mechanism_contains_adS(self):
        assert "AdS" in alphas_route_a().mechanism


class TestAlphaSNLOWindingRouteE:
    def test_returns_named_tuple(self):
        result = alphas_nlo_winding_route_e()
        assert isinstance(result, RouteResult)

    def test_name(self):
        assert "Winding" in alphas_nlo_winding_route_e().name

    def test_residual_positive(self):
        assert alphas_nlo_winding_route_e().residual_fraction > 0.0

    def test_mechanism_contains_nlo(self):
        assert "NLO" in alphas_nlo_winding_route_e().mechanism

    def test_prediction_in_reasonable_range(self):
        pred = alphas_nlo_winding_route_e().alpha_s_predicted
        assert 0.05 < pred < 0.15

    def test_residual_above_35_percent(self):
        # Still a structural floor
        result = alphas_nlo_winding_route_e()
        assert result.residual_percent >= 35.0


class TestBackreactedRadionAlphaSShift:
    def test_returns_two_values(self):
        alpha_mz, shift = backreacted_radion_alphas_shift()
        assert isinstance(alpha_mz, float)
        assert isinstance(shift, float)

    def test_alpha_mz_positive(self):
        alpha_mz, _ = backreacted_radion_alphas_shift()
        assert alpha_mz > 0.0

    def test_shift_is_small(self):
        _, shift = backreacted_radion_alphas_shift()
        # Back-reacted M_KK is huge → different running → shift should be small
        # relative to α_s itself
        assert abs(shift) < ALPHA_S_PDG


class TestSwamplandUncertainty:
    def test_positive_when_above_bound(self):
        unc = swampland_uncertainty(delta_phi=-32.0, swampland_bound=30.0)
        assert unc > 0.0

    def test_zero_when_below_bound(self):
        unc = swampland_uncertainty(delta_phi=-25.0, swampland_bound=30.0)
        assert unc == 0.0

    def test_percent_scale(self):
        unc = swampland_uncertainty()
        assert 0.0 <= unc < 10.0  # should be a small percent


class TestComputeFullAlphaSAudit:
    def test_returns_named_tuple(self):
        result = compute_full_alphas_audit()
        assert isinstance(result, AlphaSAuditResult)

    def test_routes_non_empty(self):
        result = compute_full_alphas_audit()
        assert len(result.routes) >= 2

    def test_type_b_confirmed(self):
        result = compute_full_alphas_audit()
        assert result.type_b_confirmed

    def test_gate_is_type_b(self):
        result = compute_full_alphas_audit()
        assert "TYPE_B" in result.gate

    def test_floor_lower_positive(self):
        result = compute_full_alphas_audit()
        assert result.floor_lower_percent > 0.0

    def test_floor_upper_ge_lower(self):
        result = compute_full_alphas_audit()
        assert result.floor_upper_percent >= result.floor_lower_percent

    def test_floor_in_reasonable_range(self):
        result = compute_full_alphas_audit()
        assert 35.0 <= result.floor_lower_percent <= result.floor_upper_percent <= 60.0

    def test_backreacted_mkk_large(self):
        result = compute_full_alphas_audit()
        assert result.backreacted_mkk_gev > M_KK_GEV

    def test_open_items_registered(self):
        result = compute_full_alphas_audit()
        assert len(result.open_items) >= 3

    def test_swampland_in_open_items(self):
        result = compute_full_alphas_audit()
        assert any("SWAMPLAND" in item for item in result.open_items)

    def test_nnlo_in_open_items(self):
        result = compute_full_alphas_audit()
        assert any("NNLO" in item for item in result.open_items)


class TestModuleLevelGates:
    def test_pillar_gate(self):
        assert "TYPE_B" in PILLAR_GATE

    def test_type_b_confirmed_bool(self):
        assert TYPE_B_CONFIRMED is True

    def test_floor_lower_bound(self):
        assert G2_FLOOR_LOWER_BOUND >= 39.0

    def test_floor_upper_bound(self):
        assert G2_FLOOR_UPPER_BOUND >= G2_FLOOR_LOWER_BOUND
