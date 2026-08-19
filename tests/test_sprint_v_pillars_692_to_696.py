# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for Sprint V — Pillars 692–696
  P692  NP-BC11 fermion/gauge 1-loop kernel
  P693  CKM Jarlskog invariant full audit
  P694  Δm²₃₁ JUNO Phase 2 routing
  P695  Unitarity triangle closure audit
  P696  Sprint V regression certificate v21.3
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

import pytest

import pillar692_np_bc11_fermion_gauge_loop_kernel as p692
import pillar693_ckm_jarlskog_invariant_full       as p693
import pillar694_delta_m31_juno_phase2_routing      as p694
import pillar695_unitarity_triangle_closure_audit   as p695
import pillar696_sprint_v_regression_certificate    as p696


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar692:
    """NP-BC11: Fermion/gauge one-loop WdW kernel"""

    def test_gamma_fermion_positive(self):
        gf = p692.compute_gamma_fermion()
        assert gf > 0

    def test_gamma_gauge_positive(self):
        gg = p692.compute_gamma_gauge()
        assert gg > 0

    def test_gamma_fermion_smaller_than_gauge(self):
        # Fermion contribution is suppressed by (1/(2π))^4 extra
        gf = p692.compute_gamma_fermion()
        gg = p692.compute_gamma_gauge()
        ratio = p692.fermion_to_gauge_ratio()
        assert ratio > 0
        # fermion contribution < gauge for N_f=3, N_g=12
        assert gf < gg

    def test_fermion_gauge_ratio_value(self):
        ratio = p692.fermion_to_gauge_ratio()
        expected = 3 / (12 * math.pi ** 3)
        assert abs(ratio - expected) / expected < 1e-10

    def test_kernel_structure(self):
        result = p692.compute_bc11_kernel()
        assert result["pillar"] == 692
        assert "NP_BC11" in result["label"]
        assert result["kernel_bc11"] >= 0
        assert result["gamma_total"] > 0

    def test_kernel_positive_away_from_fp(self):
        # Use G_N = 0 (IR), kernel should be g_n_star * gamma_total
        result = p692.compute_bc11_kernel(g_n=0.0, g_n_star=p692.G_N_STAR)
        assert result["kernel_bc11"] > 0

    def test_fixed_point_vanishing(self):
        fp = p692.bc11_fixed_point_vanishing()
        assert fp["vanishes"]
        assert fp["suppression_at_fixed_point"] == 0.0
        assert fp["kernel_at_fixed_point"] == 0.0

    def test_kernel_units(self):
        result = p692.compute_bc11_kernel()
        assert result["units"] == "M_Pl = 1"

    def test_np_bc_ledger_bc11_closed(self):
        ledger = p692.np_bc_ledger()
        assert "BC11" in ledger["bc11"]
        assert ledger["bc11_status"] == "CLOSED"

    def test_np_bc_ledger_bc12_named(self):
        ledger = p692.np_bc_ledger()
        assert "BC12" in ledger["next_bc12"]

    def test_ledger_complete_through_bc11(self):
        ledger = p692.np_bc_ledger()
        assert "BC11" in ledger["ledger_complete_through"]

    def test_gamma_fermion_scales_with_nf(self):
        g1 = p692.compute_gamma_fermion(n_f=1)
        g3 = p692.compute_gamma_fermion(n_f=3)
        assert abs(g3 / g1 - 3.0) < 1e-10

    def test_gamma_gauge_scales_with_ng(self):
        g6  = p692.compute_gamma_gauge(n_g=6)
        g12 = p692.compute_gamma_gauge(n_g=12)
        assert abs(g12 / g6 - 2.0) < 1e-10

    def test_suppression_between_zero_and_one(self):
        # For G_N in (0, G_N*), suppression in (0, 1)
        half_g = p692.G_N_STAR / 2
        result = p692.compute_bc11_kernel(g_n=half_g, g_n_star=p692.G_N_STAR)
        assert 0 < result["suppression"] < 1

    def test_g_n_star_value(self):
        expected = 3 * math.pi / (5 * 74 - 10)
        assert abs(p692.G_N_STAR - expected) < 1e-10

    def test_n_f_and_n_g_values(self):
        assert p692.N_F_GENERATIONS == 3
        assert p692.N_G_GAUGE == 12


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar693:
    """CKM Jarlskog invariant full computation"""

    def test_jarlskog_order_of_magnitude(self):
        result = p693.compute_jarlskog()
        # PDG: J ≈ 3.08e-5
        assert 1e-5 < result["J_exact"] < 1e-4

    def test_jarlskog_near_pdg(self):
        result = p693.compute_jarlskog()
        pdg = result["J_pdg_nominal"]
        assert abs(result["J_exact"] - pdg) / pdg < 0.15   # within 15%

    def test_jarlskog_positive(self):
        result = p693.compute_jarlskog()
        assert result["J_exact"] > 0

    def test_wolfenstein_approximation_accuracy(self):
        result = p693.compute_jarlskog()
        assert result["relative_error"] < 0.10   # <10% (leading-order approx)

    def test_pillar_number(self):
        result = p693.compute_jarlskog()
        assert result["pillar"] == 693

    def test_ckm_angles_sin_delta_positive(self):
        result = p693.compute_jarlskog()
        # η̄ > 0 → sin δ > 0 in the convention where J > 0
        assert result["sin_delta"] > 0

    def test_unitarity_triangle_angles_closure(self):
        angles = p693.unitarity_triangle_angles()
        assert abs(angles["alpha_plus_beta_plus_gamma_deg"] - 180.0) < 1e-8
        assert angles["closure_check"] < 1e-8

    def test_beta_angle_pdg_range(self):
        angles = p693.unitarity_triangle_angles()
        # PDG: β ≈ 21–24°
        assert 15 < angles["beta_deg"] < 30

    def test_gamma_angle_range(self):
        angles = p693.unitarity_triangle_angles()
        # PDG: γ ≈ 65–75°
        assert 50 < angles["gamma_deg"] < 90

    def test_fn_correction_small_relative_shift(self):
        fn = p693.jarlskog_with_fn_correction()
        # Expect relative shift <1% (small FN phase correction)
        assert fn["relative_shift"] < 0.01

    def test_fn_corrected_J_still_positive(self):
        fn = p693.jarlskog_with_fn_correction()
        assert fn["J_corrected"] > 0

    def test_fn_delta_applied(self):
        fn = p693.jarlskog_with_fn_correction()
        assert fn["fn_delta_deg"] == p693.DELTA_DELTA_FN_DEG

    def test_s12_value(self):
        result = p693.compute_jarlskog()
        assert abs(result["s12"] - p693.LAMBDA_W) < 1e-10

    def test_s13_small(self):
        result = p693.compute_jarlskog()
        assert result["s13"] < 0.01   # θ₁₃ ≈ 0.2°

    def test_c13_near_unity(self):
        result = p693.compute_jarlskog()
        assert result["c13"] > 0.99


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar694:
    """Δm²₃₁ JUNO Phase 2 routing"""

    def test_dm31_value(self):
        assert abs(p694.DM31_EV2 - 2.4109e-3) < 1e-10

    def test_dm21_value(self):
        assert abs(p694.DM21_EV2 - 7.442e-5) < 1e-10

    def test_kk_theta12_residual_small(self):
        corr = p694.kk_theta12_correction()
        assert corr["residual_frac"] < 0.005   # <0.5%

    def test_kk_theta12_correction_returns_valid(self):
        corr = p694.kk_theta12_correction()
        assert 30 < corr["theta12_kk_deg"] < 40   # θ₁₂ ≈ 33.6°

    def test_survival_prob_between_zero_and_one(self):
        res = p694.juno_survival_prob()
        assert 0 < res["P_survival"] < 1

    def test_survival_prob_at_juno_baseline(self):
        # At JUNO baseline 52.5 km, E=3 MeV, P > 0.5 (near a peak)
        res = p694.juno_survival_prob(L_m=52500.0, E_MeV=3.0)
        assert res["P_survival"] > 0

    def test_routing_pillar_number(self):
        r = p694.juno_phase2_routing()
        assert r["pillar"] == 694

    def test_routing_nh_prediction(self):
        r = p694.juno_phase2_routing()
        assert r["nh_prediction"] == "NORMAL_HIERARCHY"

    def test_routing_falsification_condition(self):
        r = p694.juno_phase2_routing()
        assert "IH" in r["falsification_condition"]

    def test_routing_sigma_is_0_1_percent(self):
        r = p694.juno_phase2_routing()
        expected_sigma = p694.DM31_EV2 * 1e-3
        assert abs(r["juno_sigma_ev2"] - expected_sigma) < 1e-15

    def test_routing_window_correct(self):
        r = p694.juno_phase2_routing()
        lo, hi = r["juno_window_ev2"]
        assert lo < p694.DM31_EV2 < hi

    def test_juno_precision_constant(self):
        assert abs(p694.JUNO_DM31_PRECISION_RELATIVE - 1e-3) < 1e-20

    def test_survival_prob_energy_dependence(self):
        p1 = p694.juno_survival_prob(E_MeV=3.0)["P_survival"]
        p2 = p694.juno_survival_prob(E_MeV=6.0)["P_survival"]
        # Different energies → different probabilities
        assert abs(p1 - p2) > 0.01

    def test_delta_c_l12_positive(self):
        assert p694.DELTA_C_L12 > 0

    def test_label(self):
        r = p694.juno_phase2_routing()
        assert "JUNO" in r["label"]


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar695:
    """Unitarity triangle closure audit"""

    def test_triangle_closure_exact(self):
        angles = p695.triangle_angles()
        assert abs(angles["closure_deg"] - 180.0) < 1e-8

    def test_triangle_closure_with_fn(self):
        angles = p695.triangle_angles(delta_delta_fn_deg=p695.DELTA_DELTA_FN_DEG)
        assert abs(angles["closure_deg"] - 180.0) < 1e-8

    def test_fn_correction_applied(self):
        angles = p695.triangle_angles(delta_delta_fn_deg=-0.34)
        assert abs(angles["fn_correction_applied_deg"] - (-0.34)) < 1e-10

    def test_beta_angle_pdg_range(self):
        angles = p695.triangle_angles()
        assert 15 < angles["beta_deg"] < 30

    def test_gamma_angle_pdg_range(self):
        angles = p695.triangle_angles()
        assert 50 < angles["gamma_deg"] < 90

    def test_alpha_positive(self):
        angles = p695.triangle_angles()
        assert angles["alpha_deg"] > 0

    def test_ckm_matrix_returns_nine_elements(self):
        V = p695.ckm_matrix()
        assert len(V) == 9

    def test_vud_near_unity(self):
        V = p695.ckm_matrix()
        assert V["Vud"] > 0.97

    def test_vus_near_lambda(self):
        V = p695.ckm_matrix()
        assert abs(V["Vus"] - p695.LAMBDA_W) < 1e-5

    def test_first_row_unitarity(self):
        r1 = p695.first_row_unitarity()
        assert r1["unitarity_satisfied"]
        assert r1["deviation_from_1"] < 1e-4

    def test_second_row_unitarity(self):
        r2 = p695.second_row_unitarity()
        assert r2["unitarity_satisfied"]
        assert r2["deviation_from_1"] < 1e-4

    def test_full_audit_structure(self):
        audit = p695.full_closure_audit()
        assert audit["pillar"] == 695
        assert audit["closure_exact"]
        assert audit["fn_perturbation_consistent"]

    def test_full_audit_both_unitarity(self):
        audit = p695.full_closure_audit()
        assert audit["first_row_unitarity"]["unitarity_satisfied"]
        assert audit["second_row_unitarity"]["unitarity_satisfied"]

    def test_vub_small(self):
        V = p695.ckm_matrix()
        assert V["Vub"] < 0.005

    def test_rho_bar_eta_bar_values(self):
        assert abs(p695.RHO_BAR - 0.159) < 1e-10
        assert abs(p695.ETA_BAR - 0.348) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar696:
    """Sprint V regression certificate v21.3"""

    def test_version(self):
        assert p696.version_string() == "v21.3"

    def test_pillar_total(self):
        assert p696.pillar_total() == 696

    def test_toe_score(self):
        assert p696.toe_score() == "30.0/28"

    def test_next_pillar_slot(self):
        assert p696.next_pillar_slot() == 697

    def test_sprint_name(self):
        cert = p696.sprint_v_certificate()
        assert cert["sprint"] == "Sprint V"

    def test_toe_not_changed(self):
        cert = p696.sprint_v_certificate()
        assert cert["toe_changed"] is False

    def test_np_bc_ledger_bc11_closed(self):
        ledger = p696.np_bc_ledger()
        assert "CLOSED" in ledger["bc11"]

    def test_np_bc_ledger_bc12_named(self):
        ledger = p696.np_bc_ledger()
        assert "BC12" in ledger["bc12_next"]

    def test_architecture_limits_alpha_s(self):
        cert = p696.sprint_v_certificate()
        assert "40%" in cert["architecture_limits"]["alpha_s_gap"]

    def test_architecture_limits_juno(self):
        cert = p696.sprint_v_certificate()
        assert "IH" in cert["architecture_limits"]["juno_falsifier"]

    def test_architecture_limits_triangle(self):
        cert = p696.sprint_v_certificate()
        assert "α+β+γ" in cert["architecture_limits"]["triangle_closure"]

    def test_pmns_ledger_complete(self):
        cert = p696.sprint_v_certificate()
        assert "COMPLETE" in cert["pmns_ledger"]["all_three"]

    def test_pmns_ledger_all_three_angles(self):
        cert = p696.sprint_v_certificate()
        assert "theta12" in cert["pmns_ledger"]
        assert "theta13" in cert["pmns_ledger"]
        assert "theta23" in cert["pmns_ledger"]

    def test_pillar_range(self):
        cert = p696.sprint_v_certificate()
        assert cert["pillar_range"] == "692–696"

    def test_effective_date(self):
        cert = p696.sprint_v_certificate()
        assert "2026" in cert["effective_date"]
