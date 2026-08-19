# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for Sprint W — Pillars 697–701
  P697  NP-BC12 higher-loop mixed graviton-matter kernel
  P698  Majorana δ_CP refinement + |m_ββ|
  P699  CKM λ⁶ higher-order corrections
  P700  framework derivation coverage audit 30.0/28 (700-pillar milestone)
  P701  Sprint W regression certificate v21.4
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

import pytest

import pillar697_np_bc12_higher_loop_wdw_kernel      as p697
import pillar698_majorana_delta_cp_phase_refinement  as p698
import pillar699_ckm_lambda6_higher_order_terms      as p699
import pillar700_toe_score_audit_30_28               as p700
import pillar701_sprint_w_regression_certificate     as p701


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar697:
    """NP-BC12: Higher-loop mixed graviton-matter WdW kernel"""

    def test_gamma_two_loop_positive(self):
        assert p697.compute_gamma_two_loop() > 0

    def test_kernel_nonnegative(self):
        result = p697.compute_bc12_kernel()
        assert result["kernel_bc12"] >= 0

    def test_pillar_number(self):
        result = p697.compute_bc12_kernel()
        assert result["pillar"] == 697

    def test_bc12_label(self):
        result = p697.compute_bc12_kernel()
        assert "BC12" in result["label"]

    def test_fixed_point_vanishing(self):
        fp = p697.bc12_fixed_point_vanishing()
        assert fp["vanishes"]
        assert fp["kernel_at_fp"] == 0.0

    def test_quartic_suppression_at_zero(self):
        # At G_N = 0, suppression = 1; kernel = G_N*² × Γ₂-loop
        result = p697.compute_bc12_kernel(g_n=0.0, g_n_star=p697.G_N_STAR)
        gamma_2l = p697.compute_gamma_two_loop()
        expected = p697.G_N_STAR ** 2 * gamma_2l
        assert abs(result["kernel_bc12"] - expected) / (expected + 1e-200) < 1e-10

    def test_ratio_small(self):
        # Two-loop mixing coefficient c_mix = G_N*/(4π²) ~ 6.6e-4
        c_mix = p697.two_loop_mixing_coefficient()
        assert c_mix < 0.01

    def test_mixing_coefficient(self):
        c_mix = p697.two_loop_mixing_coefficient()
        expected = p697.G_N_STAR / (4 * math.pi ** 2)
        assert abs(c_mix - expected) < 1e-14

    def test_np_bc_ledger_bc12_closed(self):
        ledger = p697.np_bc_ledger()
        assert "CLOSED" in ledger["bc12_status"]
        assert "BC12" in ledger["bc12"]

    def test_np_bc_ledger_bc13_named(self):
        ledger = p697.np_bc_ledger()
        assert "BC13" in ledger["next_bc13"]

    def test_ledger_complete_through_bc12(self):
        ledger = p697.np_bc_ledger()
        assert "BC12" in ledger["ledger_complete_through"]

    def test_units(self):
        result = p697.compute_bc12_kernel()
        assert result["units"] == "M_Pl = 1"

    def test_suppression_quartic_structure(self):
        g_half = p697.G_N_STAR / 2
        result = p697.compute_bc12_kernel(g_n=g_half, g_n_star=p697.G_N_STAR)
        expected_supp = (1 - 0.5) ** 4
        assert abs(result["suppression"] - expected_supp) < 1e-14

    def test_g_n_star_value(self):
        expected = 3 * math.pi / (5 * 74 - 10)
        assert abs(p697.G_N_STAR - expected) < 1e-12


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar698:
    """Majorana phase δ_CP refinement"""

    def test_delta_cp_kk_in_0_360(self):
        d = p698.kk_predicted_delta_cp_deg()
        assert 0 <= d <= 360

    def test_delta_cp_consistent_at_2sigma(self):
        check = p698.delta_cp_consistent_with_nufit()
        assert check["consistent_2sigma"]

    def test_majorana_phases_not_negative(self):
        mp = p698.majorana_phases()
        assert mp["alpha1_deg"] >= 0
        assert mp["alpha2_deg"] >= 0

    def test_m_bb_positive(self):
        result = p698.m_bb_effective()
        assert result["m_bb_eV"] >= 0

    def test_m_bb_below_ks3_bound(self):
        result = p698.m_bb_effective()
        assert result["below_ks3_bound"]

    def test_m_bb_meV_consistent(self):
        result = p698.m_bb_effective()
        assert abs(result["m_bb_meV"] - result["m_bb_eV"] * 1e3) < 1e-15

    def test_nh_flag_true(self):
        result = p698.m_bb_effective()
        assert result["nh_hierarchy"]

    def test_pillar_number(self):
        result = p698.m_bb_effective()
        assert result["pillar"] == 698

    def test_angular_diff_small(self):
        check = p698.delta_cp_consistent_with_nufit()
        # Should be well within 2σ = 50°
        assert check["angular_diff_deg"] < 50

    def test_nufit_best_value(self):
        assert abs(p698.DELTA_CP_NUFIT_DEG - 197.0) < 1e-10

    def test_m_bb_label(self):
        result = p698.m_bb_effective()
        assert "MAJORANA" in result["label"]

    def test_dm21_dm31_positive(self):
        assert p698.DM21_EV2 > 0
        assert p698.DM31_EV2 > 0


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar699:
    """CKM λ⁶ higher-order corrections"""

    def test_vud_o6_less_than_o4(self):
        V = p699.wolfenstein_o_lambda6()
        assert V["Vud_o6"] < V["Vud_o4"]

    def test_vus_o6_less_than_o4(self):
        V = p699.wolfenstein_o_lambda6()
        assert V["Vus_o6"] < V["Vus_o4"]

    def test_vub_o6_less_than_o4(self):
        V = p699.wolfenstein_o_lambda6()
        assert V["Vub_o6"] < V["Vub_o4"]

    def test_pillar_number(self):
        V = p699.wolfenstein_o_lambda6()
        assert V["pillar"] == 699

    def test_delta_vud_small(self):
        V = p699.wolfenstein_o_lambda6()
        # δVud ~ λ⁶ ~ 1.6×10⁻⁴
        assert V["delta_Vud"] < 1e-3

    def test_delta_vus_small(self):
        V = p699.wolfenstein_o_lambda6()
        # δVus ~ λ⁵ ~ 7×10⁻⁵
        assert V["delta_Vus"] < 5e-4

    def test_jarlskog_perturbativity(self):
        J = p699.jarlskog_o_lambda6_correction()
        assert J["perturbativity_ok"]

    def test_jarlskog_o6_positive(self):
        J = p699.jarlskog_o_lambda6_correction()
        assert J["J_o6"] > 0

    def test_cabibbo_angle_o6_near_o4(self):
        cab = p699.cabibbo_angle_precision()
        assert cab["delta_theta_c_deg"] < 0.1

    def test_cabibbo_angle_near_13_deg(self):
        cab = p699.cabibbo_angle_precision()
        assert 12 < cab["theta_c_o6_deg"] < 14

    def test_first_row_unitarity_o6(self):
        r1 = p699.first_row_unitarity_o6()
        assert r1["unitarity_satisfied"]

    def test_vud_near_unity(self):
        V = p699.wolfenstein_o_lambda6()
        assert V["Vud_o6"] > 0.97

    def test_relative_shift_cabibbo_small(self):
        cab = p699.cabibbo_angle_precision()
        assert cab["relative_shift"] < 0.005


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar700:
    """framework derivation coverage audit 30.0/28"""

    def test_score_string(self):
        assert p700.score_string() == "30.0/28"

    def test_percent_over_100(self):
        assert p700.percent() > 100

    def test_percent_near_107(self):
        assert abs(p700.percent() - round(100 * 30/28, 2)) < 0.01

    def test_open_windows_nonempty(self):
        assert len(p700.open_windows()) >= 3

    def test_litebird_in_windows(self):
        assert any("LiteBIRD" in w or "β" in w for w in p700.open_windows())

    def test_architecture_limits_nonempty(self):
        assert len(p700.architecture_limits()) >= 5

    def test_np_bc_closed_string(self):
        assert "BC12" in p700.np_bc_closed()

    def test_pillar_milestone(self):
        rec = p700.toe_score()
        assert rec["pillar_milestone"] == 700

    def test_pmns_complete_flag(self):
        rec = p700.toe_score()
        assert rec["pmns_angles_complete"]

    def test_ckm_jarlskog_audited_flag(self):
        rec = p700.toe_score()
        assert rec["ckm_jarlskog_audited"]

    def test_unitarity_triangle_closed_flag(self):
        rec = p700.toe_score()
        assert rec["unitarity_triangle_closed"]

    def test_bonus_points_two(self):
        rec = p700.toe_score()
        assert len(rec["bonus_points"]) == 2

    def test_version_v21(self):
        rec = p700.toe_score()
        assert "v21" in rec["version"]


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar701:
    """Sprint W regression certificate v21.4"""

    def test_version(self):
        assert p701.version_string() == "v21.4"

    def test_pillar_total(self):
        assert p701.pillar_total() == 701

    def test_toe_score(self):
        assert p701.toe_score() == "framework internally consistent"

    def test_next_slot(self):
        assert p701.next_pillar_slot() == 702

    def test_sprint_name(self):
        cert = p701.sprint_w_certificate()
        assert cert["sprint"] == "Sprint W"

    def test_toe_not_changed(self):
        cert = p701.sprint_w_certificate()
        assert cert["toe_changed"] is False

    def test_bc12_closed_in_ledger(self):
        ledger = p701.np_bc_ledger()
        assert "CLOSED" in ledger["bc12"]

    def test_bc13_next_in_ledger(self):
        ledger = p701.np_bc_ledger()
        assert "BC13" in ledger["bc13_next"]

    def test_700_milestone_in_cert(self):
        cert = p701.sprint_w_certificate()
        assert "700" in cert["milestones"].get("700_pillars", "")

    def test_pmns_complete_in_cert(self):
        cert = p701.sprint_w_certificate()
        assert "PMNS" in cert["milestones"].get("pmns_complete", "") or \
               "PMNS" in str(cert["milestones"])

    def test_pillar_range(self):
        cert = p701.sprint_w_certificate()
        assert cert["pillar_range"] == "697–701"

    def test_ckm_lambda6_in_architecture(self):
        cert = p701.sprint_w_certificate()
        assert "λ⁶" in cert["architecture_limits"].get("ckm_lambda6", "")

    def test_delta_cp_in_architecture(self):
        cert = p701.sprint_w_certificate()
        assert "NuFIT" in cert["architecture_limits"].get("delta_cp", "")
