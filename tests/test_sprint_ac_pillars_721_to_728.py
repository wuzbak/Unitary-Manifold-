# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for Sprint AC — Pillars 721–728

  P721  NP-BC17 gravitino conformal compensator kernel
  P722  Jarlskog Layer 3 FN sub-lattice correction
  P723  Higgs GHU NLO KK tower correction
  P724  Lean4 WarpFactorUniqueness certificate
  P725  Lean4 BraidUniquenessAlgebraic certificate
  P726  Lean4 PMNSRationalBounds certificate
  P727  DESI DR3 live status drill + circularity audit certificate
  P728  Sprint AC regression certificate v21.9
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

import pytest

import pillar721_np_bc17_gravitino_compensator     as p721
import pillar722_jarlskog_layer3_fn_sublattice     as p722
import pillar723_higgs_ghu_nlo_kk_tower            as p723
import pillar724_lean4_warpfactor_uniqueness       as p724
import pillar725_lean4_braid_uniqueness_algebraic  as p725
import pillar726_lean4_pmns_rational_bounds        as p726
import pillar727_desi_dr3_live_status_drill        as p727
import pillar728_sprint_ac_regression_certificate  as p728


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar721:
    """NP-BC17: Gravitino conformal compensator kernel"""

    def test_epsilon_c_positive(self):
        assert p721.EPSILON_C > 0

    def test_epsilon_c_formula(self):
        expected = (5 / 74) ** 2
        assert abs(p721.EPSILON_C - expected) < 1e-12

    def test_kernel_nonneg(self):
        result = p721.compute_bc17_kernel()
        assert result["kernel_bc17"] >= 0

    def test_pillar_number(self):
        result = p721.compute_bc17_kernel()
        assert result["pillar"] == 721

    def test_bc17_label(self):
        result = p721.compute_bc17_kernel()
        assert "BC17" in result["label"]

    def test_fixed_point_vanishing(self):
        fp = p721.bc17_fixed_point_vanishing()
        assert fp["vanishes"]

    def test_bc17_ledger_closed(self):
        ledger = p721.np_bc_ledger()
        assert "CLOSED" in ledger["bc17_status"]

    def test_bc17_ledger_complete_through(self):
        ledger = p721.np_bc_ledger()
        assert "BC17" in ledger["ledger_complete_through"]

    def test_bc17_kernel_at_zero_gn_positive(self):
        result = p721.compute_bc17_kernel(g_n=0.0, g_n_star=p721.G_N_STAR)
        assert result["kernel_bc17"] > 0

    def test_epsilon_c_small(self):
        assert p721.EPSILON_C < 0.01

    def test_gravitino_mass_ratio_tiny(self):
        assert p721.M_32_RATIO < 1e-10

    def test_epsilon_c_function(self):
        assert p721.epsilon_c_value() == p721.EPSILON_C

    def test_gravitino_mass_ratio_function(self):
        assert p721.gravitino_mass_ratio() == p721.M_32_RATIO

    def test_status_closed(self):
        result = p721.compute_bc17_kernel()
        assert result["status"] == "CLOSED"

    def test_bc17_architecture_limit_documented(self):
        ledger = p721.np_bc_ledger()
        assert "architecture limit" in ledger["bc17_honest_gap"].lower() or \
               "Architecture" in ledger["bc17_honest_gap"]


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar722:
    """Jarlskog Layer 3: FN sub-lattice correction"""

    def test_xi_sublattice_formula(self):
        assert abs(p722.XI_SUBLATTICE - 5 / 74) < 1e-12

    def test_delta_rho_l3_positive(self):
        dl3 = p722.compute_delta_rho_layer3()
        assert dl3["delta_rho_l3"] > 0

    def test_delta_rho_l3_small(self):
        dl3 = p722.compute_delta_rho_layer3()
        assert dl3["delta_rho_l3"] < 0.05   # should be a small correction

    def test_rho_bar_l3_larger_than_geo(self):
        r = p722.rho_bar_through_layer3()
        assert r["rho_bar_l3"] > p722.RHO_BAR_GEO

    def test_rho_bar_l3_closer_to_pdg_than_l2(self):
        r = p722.rho_bar_through_layer3()
        assert r["residual_pct"] < r["layer2_residual_pct"]

    def test_residual_approaching_closure(self):
        r = p722.rho_bar_through_layer3()
        # Should be < 15% (approaching closure)
        assert r["residual_pct"] < 15.0

    def test_residual_still_nonzero(self):
        r = p722.rho_bar_through_layer3()
        assert r["residual_pct"] > 0.5

    def test_status_approaching_closure(self):
        r = p722.rho_bar_through_layer3()
        assert r["status"] == "APPROACHING_CLOSURE"

    def test_layer3_improvement_factor_gt1(self):
        assert p722.layer3_improvement_factor() > 1.0

    def test_xi_sublattice_function(self):
        assert p722.xi_sublattice_value() == p722.XI_SUBLATTICE

    def test_pillar_label(self):
        dl3 = p722.compute_delta_rho_layer3()
        assert "LAYER3" in dl3["label"]

    def test_pillar_number(self):
        dl3 = p722.compute_delta_rho_layer3()
        assert dl3["pillar"] == 722

    def test_epsilon_fn_equals_lambda_c(self):
        assert abs(p722.EPSILON_FN - p722.LAMBDA_C) < 1e-12

    def test_honest_gap_present(self):
        r = p722.rho_bar_through_layer3()
        assert "architecture limit" in r["honest_gap"].lower()


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar723:
    """Higgs GHU NLO: KK tower correction"""

    def test_tower_sum_positive(self):
        assert p723.TOWER_SUM > 1.5

    def test_tower_sum_lt_pi_sq_over_6(self):
        # Partial sum ≤ π²/6 ≈ 1.6449
        assert p723.TOWER_SUM <= math.pi**2 / 6 + 1e-9

    def test_delta_lambda_positive(self):
        dl = p723.compute_delta_lambda_kk()
        assert dl["delta_lambda_kk"] > 0

    def test_mh_nlo_larger_than_lo(self):
        r = p723.compute_mh_ghu_nlo()
        assert r["m_h_ghu_nlo_gev"] > r["m_h_ghu_lo_gev"]

    def test_mh_nlo_still_below_pdg(self):
        r = p723.compute_mh_ghu_nlo()
        assert r["m_h_ghu_nlo_gev"] < p723.M_H_PDG

    def test_nlo_residual_less_than_lo(self):
        r = p723.compute_mh_ghu_nlo()
        assert r["nlo_residual_pct"] < r["lo_residual_pct"]

    def test_architecture_limit_confirmed(self):
        assert p723.nlo_architecture_limit_confirmed()

    def test_gap_reduction_positive(self):
        r = p723.compute_mh_ghu_nlo()
        assert r["gap_reduction_pct"] > 0

    def test_status_tightened(self):
        r = p723.compute_mh_ghu_nlo()
        assert "TIGHTENED" in r["status"]

    def test_pillar_number(self):
        r = p723.compute_mh_ghu_nlo()
        assert r["pillar"] == 723

    def test_label(self):
        r = p723.compute_mh_ghu_nlo()
        assert "NLO" in r["label"]

    def test_nlo_residual_above_20pct(self):
        r = p723.compute_mh_ghu_nlo()
        # Honest: gap > 20% even after NLO
        assert r["nlo_residual_pct"] > 20.0

    def test_honest_gap_documented(self):
        r = p723.compute_mh_ghu_nlo()
        assert "architecture limit" in r["honest_gap"].lower()

    def test_kk_tower_sum_function(self):
        assert p723.kk_tower_sum_value() == p723.TOWER_SUM


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar724:
    """Lean4 WarpFactor Uniqueness certificate"""

    def test_pi_kr_int_equals_cs_denom(self):
        assert p724.PI_KR_INT == p724.CS_DENOM

    def test_kcs_double_pi_kr(self):
        assert p724.K_CS == 2 * p724.PI_KR_INT

    def test_nw_kcs_codetermination(self):
        assert p724.N_W**2 + (p724.N_W + 2)**2 == p724.K_CS

    def test_certificate_label(self):
        cert = p724.warp_factor_certificate()
        assert "WARPFACTOR" in cert["label"]

    def test_certificate_pillar(self):
        cert = p724.warp_factor_certificate()
        assert cert["pillar"] == 724

    def test_hierarchy_self_consistency(self):
        assert p724.hierarchy_self_consistency()

    def test_kcs_is_double_pi_kr(self):
        assert p724.kcs_is_double_pi_kr()

    def test_nw_kcs_codetermination_function(self):
        assert p724.nw_kcs_codetermination()

    def test_new_theorems_count(self):
        cert = p724.warp_factor_certificate()
        assert cert["new_theorems"] == 18

    def test_total_theorems_494(self):
        assert p724.theorem_count() == 494

    def test_module_name(self):
        cert = p724.warp_factor_certificate()
        assert cert["lean4_module"] == "WarpFactorUniqueness"

    def test_status_proved(self):
        cert = p724.warp_factor_certificate()
        assert cert["status"] == "LEAN4_PROVED"

    def test_37_divides_74(self):
        cert = p724.warp_factor_certificate()
        assert cert["37_divides_74"]


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar725:
    """Lean4 BraidUniqueness Algebraic certificate"""

    def test_cs_action_57_equals_74(self):
        assert p725.cs_action_step2(5) == 74

    def test_action_minimum_at_5(self):
        cert = p725.braid_algebraic_certificate()
        assert cert["min_action_seed"] == 5

    def test_unique_in_70_80(self):
        assert p725.braid_uniqueness_in_window() == [5]

    def test_action_strictly_increasing(self):
        assert p725.action_strictly_increasing()

    def test_cs_action_79_lt_cs_action_97(self):
        assert p725.cs_action_step2(7) < p725.cs_action_step2(9)

    def test_certificate_pillar(self):
        cert = p725.braid_algebraic_certificate()
        assert cert["pillar"] == 725

    def test_new_theorems_count(self):
        cert = p725.braid_algebraic_certificate()
        assert cert["new_theorems"] == 15

    def test_total_theorems_509(self):
        assert p725.theorem_count() == 509

    def test_module_name(self):
        cert = p725.braid_algebraic_certificate()
        assert cert["lean4_module"] == "BraidUniquenessAlgebraic"

    def test_status_proved(self):
        cert = p725.braid_algebraic_certificate()
        assert cert["status"] == "LEAN4_PROVED"

    def test_coprime_57(self):
        cert = p725.braid_algebraic_certificate()
        assert cert["coprime_57"]

    def test_action_increasing_flag(self):
        cert = p725.braid_algebraic_certificate()
        assert cert["action_increasing"]


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar726:
    """Lean4 PMNS Rational Bounds certificate"""

    def test_theta12_within_2sigma(self):
        assert p726.theta12_within_2sigma()

    def test_theta23_architecture_limit(self):
        assert p726.theta23_architecture_limit()

    def test_theta13_within_1sigma(self):
        assert p726.theta13_within_1sigma()

    def test_solar_atm_ordering(self):
        cert = p726.pmns_certificate()
        assert cert["solar_atm_ordering"]

    def test_reactor_small(self):
        cert = p726.pmns_certificate()
        assert cert["reactor_small"]

    def test_nh_consistency(self):
        cert = p726.pmns_certificate()
        assert cert["nh_consistency"]

    def test_certificate_pillar(self):
        cert = p726.pmns_certificate()
        assert cert["pillar"] == 726

    def test_new_theorems_count(self):
        cert = p726.pmns_certificate()
        assert cert["new_theorems"] == 12

    def test_total_theorems_521(self):
        assert p726.theorem_count() == 521

    def test_module_name(self):
        cert = p726.pmns_certificate()
        assert cert["lean4_module"] == "PMNSRationalBounds"

    def test_status_proved(self):
        cert = p726.pmns_certificate()
        assert cert["status"] == "LEAN4_PROVED"

    def test_theta23_gap_quantified(self):
        cert = p726.pmns_certificate()
        assert cert["theta23_gap_x10k"] == 450

    def test_theta12_residual_lt_5pct(self):
        cert = p726.pmns_certificate()
        assert cert["theta12_residual_pct"] < 5.0

    def test_honest_gap_theta23(self):
        cert = p726.pmns_certificate()
        assert "architecture limit" in cert["honest_gap"].lower() or \
               "off-diagonal" in cert["honest_gap"]


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar727:
    """DESI DR3 live status drill + circularity audit"""

    def test_desi_routing_returns_tension(self):
        routing = p727.desi_dr3_routing()
        assert routing["verdict"] == "TENSION"

    def test_desi_routing_sigma_gt2(self):
        routing = p727.desi_dr3_routing()
        assert routing["tension_sigma"] > 2.0

    def test_desi_routing_sigma_lt3(self):
        routing = p727.desi_dr3_routing()
        assert routing["tension_sigma"] < 3.0

    def test_um_wa_prediction_zero(self):
        assert p727.UM_WA_PRED == 0.0

    def test_desi_live_status_pillar(self):
        s = p727.desi_dr3_live_status()
        assert s["pillar"] == 727

    def test_desi_live_status_completed(self):
        s = p727.desi_dr3_live_status()
        assert s["status"] == "DRILL_COMPLETED"

    def test_circularity_not_circular(self):
        cert = p727.circularity_audit_certificate()
        assert not cert["circular"]

    def test_circularity_resolved(self):
        cert = p727.circularity_audit_certificate()
        assert "RESOLVED" in cert["status"]

    def test_circularity_chain_named(self):
        cert = p727.circularity_audit_certificate()
        assert "alpha_GW" in cert["chain"] or "α_GW" in cert["chain"]

    def test_consistent_routing_at_low_sigma(self):
        routing = p727.desi_dr3_routing(wa_obs=0.05, sigma_wa=0.30)
        assert routing["verdict"] == "CONSISTENT"

    def test_falsified_routing_at_high_sigma(self):
        routing = p727.desi_dr3_routing(wa_obs=-0.95, sigma_wa=0.30)
        assert routing["verdict"] == "FALSIFIED"

    def test_summary_combined_status(self):
        s = p727.pillar727_summary()
        assert "DRILL_COMPLETED" in s["combined_status"]


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar728:
    """Sprint AC regression certificate v21.9"""

    def test_version(self):
        assert p728.version_string() == "v21.9"

    def test_sprint_name(self):
        cert = p728.sprint_ac_certificate()
        assert cert["sprint"] == "Sprint AC"

    def test_pillar_total(self):
        assert p728.pillar_total() == 728

    def test_toe_unchanged(self):
        cert = p728.sprint_ac_certificate()
        assert not cert["toe_changed"]

    def test_toe_score(self):
        assert p728.toe_score() == "30.0/28"

    def test_lean4_new_total_521(self):
        assert p728.lean4_total_theorems() == 521

    def test_lean4_new_theorems_45(self):
        cert = p728.sprint_ac_certificate()
        assert cert["lean4_summary"]["new_theorems_total"] == 45

    def test_lean4_modules_three(self):
        cert = p728.sprint_ac_certificate()
        assert len(cert["lean4_summary"]["new_modules"]) == 3

    def test_np_bc17_in_physics(self):
        cert = p728.sprint_ac_certificate()
        assert "np_bc17" in cert["physics_advances"]

    def test_next_pillar_slot_729(self):
        cert = p728.sprint_ac_certificate()
        assert cert["next_pillar_slot"] == 729

    def test_open_falsifiers_present(self):
        cert = p728.sprint_ac_certificate()
        assert "litebird" in cert["open_falsifiers"]

    def test_architecture_limits_documented(self):
        cert = p728.sprint_ac_certificate()
        assert len(cert["architecture_limits"]) >= 3

    def test_jarlskog_l3_in_physics(self):
        cert = p728.sprint_ac_certificate()
        assert "jarlskog_l3" in cert["physics_advances"]

    def test_higgs_nlo_in_physics(self):
        cert = p728.sprint_ac_certificate()
        assert "higgs_nlo" in cert["physics_advances"]
