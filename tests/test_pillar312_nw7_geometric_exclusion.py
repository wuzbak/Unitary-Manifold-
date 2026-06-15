# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 312 — n_w = 7 Geometric Exclusion Certificate."""
import math
import pytest
from src.core.pillar312_nw7_geometric_exclusion import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    NW7_EXCLUSION_STATUS,
    N1,
    N2,
    N_M7,
    K_CS_NW5,
    K_CS_NW7,
    ETA_BAR_N5,
    ETA_BAR_N7,
    PI_KR,
    GW_EPSILON,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    NS_NW5,
    NS_NW7,
    CHI2_NW5,
    CHI2_NW7,
    DELTA_CHI2,
    LIKELIHOOD_RATIO_NW5_OVER_NW7,
    CS_SOUND_SPEED_NW5,
    CS_SOUND_SPEED_NW7,
    R_BRAIDED_NW5,
    R_BRAIDED_NW7,
    GW_U1_MIN,
    GW_U2_MIN,
    GW_R_RATIO,
    CONSTRAINT_A_APS,
    CONSTRAINT_B_GW,
    CONSTRAINT_C_CS_ACTION,
    CONSTRAINT_D_PLANCK,
    CONSTRAINT_E_CS_SOUND,
    triangular_number,
    eta_bar,
    aps_cs_boundary_phase_check,
    gw_winding_cycle_assignment,
    cs_action_comparison,
    planck_ns_chi2_comparison,
    braided_sound_speed,
    braided_r_eff,
    braided_r_discriminator,
    all_constraints_summary,
    nw7_exclusion_certificate,
    admission_3_status,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 312

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

def test_pillar_title_mentions_exclusion():
    assert "Exclusion" in PILLAR_TITLE or "exclusion" in PILLAR_TITLE

def test_exclusion_status_label():
    assert NW7_EXCLUSION_STATUS == "MULTI_CONSTRAINT_DISFAVOURED_TOPOLOGICAL_PREFERRED"


# ── UM constants ──────────────────────────────────────────────────────────────

def test_n1_is_5():
    assert N1 == 5

def test_n2_is_7():
    assert N2 == 7

def test_n_m7_is_9():
    assert N_M7 == 9

def test_k_cs_nw5():
    assert K_CS_NW5 == 74   # 5²+7²

def test_k_cs_nw7():
    assert K_CS_NW7 == 130  # 7²+9²

def test_k_cs_nw5_algebraic():
    assert K_CS_NW5 == N1**2 + N2**2

def test_k_cs_nw7_algebraic():
    assert K_CS_NW7 == N2**2 + N_M7**2

def test_pi_kr():
    assert PI_KR == 37

def test_pi_kr_half_k_cs():
    assert PI_KR * 2 == K_CS_NW5


# ── APS η̄ ─────────────────────────────────────────────────────────────────────

def test_triangular_number_5():
    assert triangular_number(5) == 15

def test_triangular_number_7():
    assert triangular_number(7) == 28

def test_eta_bar_5():
    assert abs(ETA_BAR_N5 - 0.5) < 1e-12

def test_eta_bar_7():
    assert abs(ETA_BAR_N7 - 0.0) < 1e-12

def test_eta_bar_function_5():
    assert abs(eta_bar(5) - 0.5) < 1e-12

def test_eta_bar_function_7():
    assert abs(eta_bar(7) - 0.0) < 1e-12

def test_eta_bar_n5_nontrivial():
    assert ETA_BAR_N5 != 0.0

def test_eta_bar_n7_trivial():
    assert ETA_BAR_N7 == 0.0


# ── Constraint A: APS boundary phase ──────────────────────────────────────────

def test_aps_n5_consistent():
    result = aps_cs_boundary_phase_check(N1, K_CS_NW5)
    assert result["verdict"] == "CONSISTENT"

def test_aps_n7_excluded():
    result = aps_cs_boundary_phase_check(N2, K_CS_NW7)
    assert result["verdict"] == "EXCLUDED_APS_BOUNDARY_PHASE"

def test_aps_n5_product_is_37():
    result = aps_cs_boundary_phase_check(N1, K_CS_NW5)
    assert abs(result["product"] - 37.0) < 1e-9

def test_aps_n7_product_is_zero():
    result = aps_cs_boundary_phase_check(N2, K_CS_NW7)
    assert abs(result["product"] - 0.0) < 1e-9

def test_aps_n5_product_is_odd():
    result = aps_cs_boundary_phase_check(N1, K_CS_NW5)
    assert result["is_odd"] is True

def test_aps_n7_product_is_not_odd():
    result = aps_cs_boundary_phase_check(N2, K_CS_NW7)
    assert result["is_odd"] is False

def test_aps_n5_is_integer():
    result = aps_cs_boundary_phase_check(N1, K_CS_NW5)
    assert result["is_integer"] is True

def test_constraint_a_aps_n5_consistent():
    assert CONSTRAINT_A_APS["verdict"] == "CONSISTENT"


# ── Constraint B: GW winding cycle assignment ─────────────────────────────────

def test_gw_u1_positive():
    assert GW_U1_MIN > 0

def test_gw_u2_positive():
    assert GW_U2_MIN > 0

def test_gw_r_ratio_less_than_one():
    """n=7 cycle stabilises at smaller radius: R₂/R₁ < 1."""
    assert GW_R_RATIO < 1.0

def test_gw_r_ratio_near_0_52():
    # Computed value from winding back-reaction formula: ~0.516
    assert abs(GW_R_RATIO - 0.516) < 0.05

def test_gw_u1_larger_than_u2():
    assert GW_U1_MIN > GW_U2_MIN

def test_constraint_b_verdict():
    result = gw_winding_cycle_assignment()
    assert result["verdict"] == "CYCLE_ASSIGNMENT_DERIVED"

def test_constraint_b_convention_279_3():
    result = gw_winding_cycle_assignment()
    assert "DERIVED" in result["convention_279_3"]

def test_constraint_b_z2_nontrivial_cycle_is_n5():
    result = gw_winding_cycle_assignment()
    assert "n_w=5" in result["z2_nontrivial_cycle"]

def test_constraint_b_n7_shorter():
    result = gw_winding_cycle_assignment()
    assert result["n7_shorter_cycle"] is True


# ── Constraint C: CS action ───────────────────────────────────────────────────

def test_constraint_c_k_eff_nw5():
    result = cs_action_comparison()
    assert result["k_eff_nw5"] == 74

def test_constraint_c_k_eff_nw7():
    result = cs_action_comparison()
    assert result["k_eff_nw7"] == 130

def test_constraint_c_action_ratio():
    result = cs_action_comparison()
    assert abs(result["action_ratio_nw7_over_nw5"] - K_CS_NW7 / K_CS_NW5) < 1e-9

def test_constraint_c_dominant_saddle_is_nw5():
    result = cs_action_comparison()
    assert result["dominant_saddle"] == "n_w=5"

def test_constraint_c_verdict():
    result = cs_action_comparison()
    assert result["verdict"] == "CS_ACTION_MINIMUM_PREFERRED"

def test_constraint_c_nw5_smaller_action():
    assert K_CS_NW5 < K_CS_NW7


# ── Constraint D: Planck n_s χ² ──────────────────────────────────────────────

def test_ns_nw5_near_canonical():
    assert abs(NS_NW5 - 0.9635) < 0.0005

def test_ns_nw7_above_planck():
    assert NS_NW7 > PLANCK_NS_CENTRAL

def test_chi2_nw5_small():
    assert CHI2_NW5 < 1.0

def test_chi2_nw7_large():
    assert CHI2_NW7 > 4.0

def test_delta_chi2_positive():
    assert DELTA_CHI2 > 0

def test_likelihood_ratio_nw5_over_nw7_large():
    assert LIKELIHOOD_RATIO_NW5_OVER_NW7 > 10.0

def test_planck_ns_sigma():
    assert abs(PLANCK_NS_SIGMA - 0.0042) < 1e-9

def test_constraint_d_verdict():
    result = planck_ns_chi2_comparison()
    assert result["verdict"] == "PLANCK_NS_DISFAVOURED"

def test_constraint_d_sigma_pull_nw7():
    result = planck_ns_chi2_comparison()
    # n_w=7 must be more than 2σ from Planck n_s
    assert result["sigma_pull_nw7"] > 2.0

def test_constraint_d_likelihood_ratio():
    result = planck_ns_chi2_comparison()
    assert result["likelihood_ratio_nw5_over_nw7"] > 10.0


# ── Constraint E: Braided sound speed / r ─────────────────────────────────────

def test_braided_sound_speed_nw5():
    cs = braided_sound_speed(5, 7)
    assert abs(cs - 12 / 37) < 1e-10

def test_braided_sound_speed_nw7():
    cs = braided_sound_speed(7, 9)
    assert abs(cs - 32 / 130) < 1e-10

def test_cs_sound_nw5_canonical():
    assert abs(CS_SOUND_SPEED_NW5 - 12 / 37) < 1e-10

def test_cs_sound_nw7_smaller():
    assert CS_SOUND_SPEED_NW7 < CS_SOUND_SPEED_NW5

def test_r_braided_nw5_below_bicep():
    assert R_BRAIDED_NW5 < 0.036

def test_r_braided_nw7_below_bicep():
    assert R_BRAIDED_NW7 < 0.036

def test_r_braided_nw5_near_0315():
    assert abs(R_BRAIDED_NW5 - 0.0315) < 0.003

def test_r_braided_ratio_nw7_smaller():
    assert R_BRAIDED_NW7 < R_BRAIDED_NW5

def test_r_braided_ratio_below_one():
    ratio = R_BRAIDED_NW7 / R_BRAIDED_NW5
    # n_w=7 braided r is significantly smaller than n_w=5 — ratio < 0.7
    assert 0.2 < ratio < 0.7

def test_constraint_e_verdict():
    result = braided_r_discriminator()
    assert result["verdict"] == "CS_SOUND_SPEED_DISCRIMINATOR"

def test_constraint_e_both_pass_r():
    result = braided_r_discriminator()
    assert result["nw5_passes_r"] is True
    assert result["nw7_passes_r"] is True


# ── All constraints summary ───────────────────────────────────────────────────

def test_all_constraints_count():
    constraints = all_constraints_summary()
    assert len(constraints) == 5

def test_all_constraints_labels():
    constraints = all_constraints_summary()
    labels = [c["constraint"] for c in constraints]
    assert labels == ["A", "B", "C", "D", "E"]

def test_constraint_a_excludes_nw7():
    constraints = all_constraints_summary()
    a = constraints[0]
    assert a["excludes_nw7"] is True

def test_constraints_bce_do_not_alone_exclude():
    constraints = all_constraints_summary()
    for c in constraints[1:]:
        assert c["excludes_nw7"] is False

def test_constraint_a_type_proved():
    constraints = all_constraints_summary()
    assert constraints[0]["type"] == "PROVED"

def test_constraint_b_type_derived():
    constraints = all_constraints_summary()
    assert constraints[1]["type"] == "DERIVED"

def test_constraint_c_type_preferred():
    constraints = all_constraints_summary()
    assert constraints[2]["type"] == "PREFERRED"

def test_constraint_d_type_observational():
    constraints = all_constraints_summary()
    assert constraints[3]["type"] == "OBSERVATIONAL"

def test_constraint_e_type_phenomenological():
    constraints = all_constraints_summary()
    assert constraints[4]["type"] == "PHENOMENOLOGICAL"


# ── Full certificate ──────────────────────────────────────────────────────────

def test_certificate_pillar():
    cert = nw7_exclusion_certificate()
    assert cert["pillar"] == 312

def test_certificate_exclusion_status():
    cert = nw7_exclusion_certificate()
    assert cert["exclusion_status"] == NW7_EXCLUSION_STATUS

def test_certificate_definitive_exclusion_true():
    cert = nw7_exclusion_certificate()
    assert cert["definitive_exclusion"] is True

def test_certificate_source_is_constraint_a():
    cert = nw7_exclusion_certificate()
    assert "A" in cert["definitive_exclusion_source"]

def test_certificate_verdict_mentions_even():
    cert = nw7_exclusion_certificate()
    assert "EVEN" in cert["definitive_exclusion_verdict"]

def test_certificate_remaining_gap_mentions_admission_3():
    cert = nw7_exclusion_certificate()
    assert "Admission 3" in cert["remaining_gap"] or "axiom" in cert["remaining_gap"]

def test_certificate_litebird_mentioned():
    cert = nw7_exclusion_certificate()
    assert "LiteBIRD" in cert["litebird_falsifier"]

def test_certificate_five_constraint_summary():
    cert = nw7_exclusion_certificate()
    summary = cert["five_constraint_summary"]
    assert summary["A_proved_excludes_nw7"] is True
    assert summary["B_derived_assigns_nw5_primary"] is True
    assert summary["C_preferred_cs_action_minimum"] is True
    assert summary["D_observational_planck_ns_sigma"] > 2.0
    assert 0 < summary["E_phenomenological_r_ratio"] < 1.0

def test_certificate_constraints_list_length():
    cert = nw7_exclusion_certificate()
    assert len(cert["constraints"]) == 5


# ── Admission 3 status ────────────────────────────────────────────────────────

def test_admission_3_number():
    status = admission_3_status()
    assert status["admission"] == 3

def test_admission_3_fallibility_ref():
    status = admission_3_status()
    assert "FALLIBILITY" in status["fallibility_ref"]

def test_admission_3_what_is_proved_list():
    status = admission_3_status()
    proved = status["what_is_proved"]
    assert isinstance(proved, list)
    assert len(proved) >= 5

def test_admission_3_includes_pillar_70d():
    status = admission_3_status()
    proved_text = " ".join(status["what_is_proved"])
    assert "70-D" in proved_text or "Pillar 70" in proved_text

def test_admission_3_remains_open():
    status = admission_3_status()
    text = status["what_remains_open"]
    # "not yet derived" or "open" signals the gap is unresolved
    assert "not yet" in text or "open" in text.lower() or "does not" in text

def test_admission_3_status_token():
    status = admission_3_status()
    assert "PROVED" in status["current_status"]
    assert "AXIOM" in status["current_status"] or "CAVEAT" in status["current_status"]

def test_admission_3_upgrade_path_nonempty():
    status = admission_3_status()
    assert len(status["upgrade_path"]) > 50


# ── Separation guard ──────────────────────────────────────────────────────────

def test_separation_guard_pillar():
    sg = separation_guard()
    assert sg["pillar"] == 312

def test_separation_guard_track():
    sg = separation_guard()
    assert sg["track"] == "NON_HARDGATE_ADJACENT"

def test_separation_guard_no_hardgate_impact():
    sg = separation_guard()
    assert sg["hardgate_impact"] is False

def test_separation_guard_no_toe_delta():
    sg = separation_guard()
    assert sg["toe_score_delta"] == 0

def test_separation_guard_no_falsifier_change():
    sg = separation_guard()
    assert sg["falsifier_threshold_changed"] is False
