# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 517 — WS-V Yukawa Texture First-Principles p_R Derivation."""

import math
import pytest

from src.core.pillar517_wsv_pr_first_principles import (
    PILLAR_ID,
    PILLAR_STATUS,
    PILLAR_TITLE,
    DM2_31_PDG_EV2,
    DM2_31_UM_BASELINE_EV2,
    BASELINE_RESIDUAL_PCT,
    THETA_23_DEG,
    THETA_13_DEG,
    N_W,
    K_CS,
    C_S,
    P_R_FITTED,
    P_R_LEADING,
    P_R_WINDOW_LO,
    P_R_WINDOW_HI,
    S_KK_REQUIRED,
    P_R_STATUS,
    cs_braid_correction,
    leading_participation_single_mode,
    kk_tower_suppression_required,
    admissible_pr_window,
    pr_window_consistency_check,
    architecture_limit_certificate,
    juno_monitoring_status,
    juno_response_protocol,
    pillar517_report,
)


class TestPillar517Identity:
    def test_pillar_id_is_517(self):
        assert PILLAR_ID == 517

    def test_status_is_architecture_limit(self):
        assert PILLAR_STATUS == "P_R_ARCHITECTURE_LIMIT_CERTIFIED"

    def test_title_non_empty(self):
        assert isinstance(PILLAR_TITLE, str) and PILLAR_TITLE.strip()

    def test_p_r_status(self):
        assert P_R_STATUS == "ARCHITECTURE_LIMIT_CERTIFIED"


class TestPhysicsConstants:
    def test_dm2_31_pdg_reasonable(self):
        # PDG 2024: 2.453e-3 eV²
        assert abs(DM2_31_PDG_EV2 - 2.453e-3) < 1e-6

    def test_dm2_31_um_baseline_below_pdg(self):
        assert DM2_31_UM_BASELINE_EV2 < DM2_31_PDG_EV2

    def test_baseline_residual_approximately_2_18pct(self):
        assert 2.0 < BASELINE_RESIDUAL_PCT < 2.4

    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_c_s_is_12_over_37(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_p_r_fitted_is_0364(self):
        assert abs(P_R_FITTED - 0.364) < 1e-6


class TestCSBraidCorrection:
    def test_cs_braid_correction_positive(self):
        assert cs_braid_correction() > 0

    def test_cs_braid_correction_formula(self):
        expected = (N_W ** 2 / K_CS) * C_S
        assert abs(cs_braid_correction() - expected) < 1e-12

    def test_cs_braid_correction_approximately_01(self):
        # n_w²/k_CS · c_s = 25/74 · 12/37 ≈ 0.1097
        assert 0.09 < cs_braid_correction() < 0.13


class TestLeadingParticipation:
    def test_leading_participation_positive(self):
        assert leading_participation_single_mode() > 0

    def test_leading_participation_below_1(self):
        assert leading_participation_single_mode() < 1.0

    def test_leading_participation_approximately_0491(self):
        # sin²(42.2°) · cos²(8.53°) · (1 + 0.1097) ≈ 0.491
        val = leading_participation_single_mode()
        assert 0.43 < val < 0.56

    def test_leading_participation_exceeds_fitted(self):
        # Leading (single mode) > fitted (multi-mode suppressed)
        assert P_R_LEADING > P_R_FITTED

    def test_p_r_leading_constant_matches_function(self):
        assert abs(P_R_LEADING - leading_participation_single_mode()) < 1e-12


class TestKKTowerSuppression:
    def test_s_kk_required_greater_than_1(self):
        # Tower suppresses leading result → S_KK > 1
        assert kk_tower_suppression_required() > 1.0

    def test_s_kk_required_below_max(self):
        # Must be below S_KK_max = 2.0 for the window to include p_R
        assert kk_tower_suppression_required() < 2.0

    def test_s_kk_required_approximately_135(self):
        # 0.491 / 0.364 ≈ 1.35
        val = kk_tower_suppression_required()
        assert 1.2 < val < 1.6

    def test_s_kk_constant_matches_function(self):
        assert abs(S_KK_REQUIRED - kk_tower_suppression_required()) < 1e-10


class TestAdmissibleWindow:
    def test_window_lo_below_hi(self):
        lo, hi = admissible_pr_window()
        assert lo < hi

    def test_window_hi_equals_leading(self):
        _, hi = admissible_pr_window()
        assert abs(hi - P_R_LEADING) < 1e-12

    def test_window_lo_is_hi_over_s_kk_max(self):
        lo, hi = admissible_pr_window(s_kk_max=2.0)
        assert abs(lo - hi / 2.0) < 1e-12

    def test_fitted_in_window(self):
        lo, hi = admissible_pr_window()
        assert lo <= P_R_FITTED <= hi

    def test_window_constants_match_function(self):
        lo, hi = admissible_pr_window()
        assert abs(P_R_WINDOW_LO - lo) < 1e-12
        assert abs(P_R_WINDOW_HI - hi) < 1e-12

    def test_window_tighter_than_pmns(self):
        # Tightened window is narrower than [0, sin²θ₂₃ · cos²θ₁₃]
        pmns_upper = math.sin(math.radians(THETA_23_DEG)) ** 2 * math.cos(math.radians(THETA_13_DEG)) ** 2
        lo, hi = admissible_pr_window()
        assert (hi - lo) < pmns_upper


class TestWindowConsistency:
    def test_consistency_check_structure(self):
        result = pr_window_consistency_check()
        required_keys = {
            "p_r_fitted", "window_lo", "window_hi", "pmns_upper_bound",
            "in_tightened_window", "in_pmns_window", "window_narrowing_factor",
            "leading_p_r", "s_kk_required", "delta_cs",
        }
        assert required_keys.issubset(result.keys())

    def test_fitted_in_tightened_window(self):
        result = pr_window_consistency_check()
        assert result["in_tightened_window"] is True

    def test_fitted_in_pmns_window(self):
        result = pr_window_consistency_check()
        assert result["in_pmns_window"] is True

    def test_window_narrowing_factor_less_than_1(self):
        result = pr_window_consistency_check()
        assert result["window_narrowing_factor"] < 1.0

    def test_s_kk_required_gt_1(self):
        result = pr_window_consistency_check()
        assert result["s_kk_required"] > 1.0


class TestArchitectureLimitCertificate:
    def test_certificate_keys(self):
        cert = architecture_limit_certificate()
        required_keys = {
            "pillar_id", "status", "p_r_status", "exact_obstruction",
            "shared_root_cause", "classification_upgrade",
            "what_is_derived", "what_is_not_derived",
            "required_for_closure", "architecture_limit_shared_with",
            "juno_risk",
        }
        assert required_keys.issubset(cert.keys())

    def test_pillar_id_in_cert(self):
        assert architecture_limit_certificate()["pillar_id"] == 517

    def test_shared_root_cause_is_pillar_516(self):
        cert = architecture_limit_certificate()
        assert "516" in cert["shared_root_cause"]

    def test_classification_upgrade_mentions_conditional(self):
        cert = architecture_limit_certificate()
        assert "CONDITIONAL_DERIVATION" in cert["classification_upgrade"]

    def test_what_is_derived_has_p_r_leading(self):
        derived = architecture_limit_certificate()["what_is_derived"]
        assert "p_r_leading" in derived
        assert derived["p_r_leading"] > 0

    def test_fitted_in_tightened_window_in_cert(self):
        derived = architecture_limit_certificate()["what_is_derived"]
        assert derived["fitted_in_tightened_window"] is True

    def test_juno_risk_mentions_sigma(self):
        cert = architecture_limit_certificate()
        assert "σ" in cert["juno_risk"] or "sigma" in cert["juno_risk"].lower()


class TestJunoMonitoringStatus:
    def test_status_structure(self):
        status = juno_monitoring_status()
        required_keys = {
            "current_residual_pct", "sigma_juno_phase1", "sigma_juno_full",
            "verdict", "juno_phase1_date", "juno_full_date",
            "response_required_within_days", "nlo_verdict",
        }
        assert required_keys.issubset(status.keys())

    def test_baseline_residual_is_2_18(self):
        status = juno_monitoring_status()
        assert 2.0 < status["current_residual_pct"] < 2.4

    def test_sigma_juno_full_is_approx_4_4(self):
        status = juno_monitoring_status()
        # 2.18% / 0.5% = 4.36σ
        assert 3.5 < status["sigma_juno_full"] < 5.5

    def test_sigma_juno_phase1_is_approx_2_2(self):
        status = juno_monitoring_status()
        # 2.18% / 1.0% = 2.18σ
        assert 1.5 < status["sigma_juno_phase1"] < 3.0

    def test_baseline_verdict_indicates_risk(self):
        status = juno_monitoring_status()
        assert "RISK" in status["verdict"] or "MONITOR" in status["verdict"]

    def test_nlo_verdict_is_pass(self):
        # NLO+seesaw tightened prediction (P274) is at 0.004%
        status = juno_monitoring_status()
        assert status["nlo_verdict"] == "PASS_AT_JUNO_PRECISION"

    def test_response_window_is_30_days(self):
        assert juno_monitoring_status()["response_required_within_days"] == 30

    def test_near_zero_residual_gives_pass(self):
        status = juno_monitoring_status(current_residual_pct=0.001)
        assert status["verdict"] == "PASS_AT_JUNO_PRECISION"

    def test_large_residual_gives_risk(self):
        status = juno_monitoring_status(current_residual_pct=5.0)
        assert "RISK" in status["verdict"]


class TestJunoResponseProtocol:
    def test_protocol_status_is_staged(self):
        proto = juno_response_protocol()
        assert proto["protocol_status"] == "STAGED"

    def test_staged_date_is_2026(self):
        proto = juno_response_protocol()
        assert "2026" in proto["staged_date"]

    def test_response_window_30_days(self):
        assert juno_response_protocol()["response_window_days"] == 30

    def test_pre_registered_steps_non_empty(self):
        steps = juno_response_protocol()["pre_registered_analysis_steps"]
        assert len(steps) >= 5

    def test_falsification_sigma_is_3(self):
        thresholds = juno_response_protocol()["decision_thresholds"]
        assert thresholds["falsification_sigma"] == 3.0

    def test_pre_registered_comparison_has_pdg(self):
        comp = juno_response_protocol()["pre_registered_comparison_structure"]
        assert comp["dm2_31_pdg"] == DM2_31_PDG_EV2

    def test_measured_slot_is_none(self):
        # Not yet filled — placeholder for JUNO data
        comp = juno_response_protocol()["pre_registered_comparison_structure"]
        assert comp["dm2_31_juno_measured"] is None


class TestFullReport:
    def test_report_keys(self):
        report = pillar517_report()
        required_keys = {
            "pillar_id", "title", "status", "architecture_limit",
            "window_check", "juno_monitoring", "juno_response_protocol",
            "classification_upgrade", "blocking_for", "new_deliverables",
        }
        assert required_keys.issubset(report.keys())

    def test_pillar_id_in_report(self):
        assert pillar517_report()["pillar_id"] == 517

    def test_new_deliverables_non_empty(self):
        assert len(pillar517_report()["new_deliverables"]) >= 2

    def test_blocking_for_mentions_kk_backreaction(self):
        blocking = pillar517_report()["blocking_for"].lower()
        assert "kk" in blocking or "backreaction" in blocking
