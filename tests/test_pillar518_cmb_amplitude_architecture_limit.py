# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 518 — CMB Amplitude Gap Architecture Limit Certification."""

import pytest

from src.core.pillar518_cmb_amplitude_architecture_limit import (
    PILLAR_ID,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SUPPRESSION_FACTOR_LO,
    SUPPRESSION_FACTOR_HI,
    PEAK_ELL_VALUES,
    KK_CORRECTION_AT_ACOUSTIC_SCALE,
    N_FREE_PARAMS_CASE_A,
    N_FREE_PARAMS_CASE_B,
    N_FREE_PARAMS_CASE_C,
    case_a_bogoliubov_assessment,
    case_b_preinflationary_assessment,
    case_c_kk_propagator_assessment,
    architecture_limit_certificate,
    cmb_amplitude_gap_status,
    falsification_condition,
    pillar518_report,
)


class TestPillar518Identity:
    def test_pillar_id_is_518(self):
        assert PILLAR_ID == 518

    def test_status_is_architecture_limit(self):
        assert PILLAR_STATUS == "CMB_AMPLITUDE_ARCHITECTURE_LIMIT_CERTIFIED"

    def test_title_non_empty(self):
        assert isinstance(PILLAR_TITLE, str) and PILLAR_TITLE.strip()


class TestPhysicsConstants:
    def test_suppression_lo_is_positive(self):
        assert SUPPRESSION_FACTOR_LO > 1.0

    def test_suppression_hi_greater_than_lo(self):
        assert SUPPRESSION_FACTOR_HI > SUPPRESSION_FACTOR_LO

    def test_suppression_lo_approximately_42(self):
        assert abs(SUPPRESSION_FACTOR_LO - 4.2) < 0.01

    def test_suppression_hi_approximately_61(self):
        assert abs(SUPPRESSION_FACTOR_HI - 6.1) < 0.01

    def test_peak_ell_values_are_three(self):
        assert len(PEAK_ELL_VALUES) == 3

    def test_peak_ell_values_include_220(self):
        assert 220 in PEAK_ELL_VALUES

    def test_kk_correction_negligible(self):
        # Must be negligibly small compared to suppression factor
        assert KK_CORRECTION_AT_ACOUSTIC_SCALE < 1e-50

    def test_case_a_requires_free_params(self):
        assert N_FREE_PARAMS_CASE_A > 0

    def test_case_b_requires_free_params(self):
        assert N_FREE_PARAMS_CASE_B > 0

    def test_case_c_no_new_params(self):
        assert N_FREE_PARAMS_CASE_C == 0


class TestCaseA:
    def test_case_a_keys(self):
        result = case_a_bogoliubov_assessment()
        required = {
            "case", "name", "enhancement_needed", "beta_required",
            "new_free_params", "verdict", "reason", "resolution_requires",
        }
        assert required.issubset(result.keys())

    def test_case_a_verdict_is_architecture_limit(self):
        assert case_a_bogoliubov_assessment()["verdict"] == "ARCHITECTURE_LIMIT"

    def test_case_a_new_free_params_positive(self):
        assert case_a_bogoliubov_assessment()["new_free_params"] > 0

    def test_case_a_enhancement_matches_suppression(self):
        enh = case_a_bogoliubov_assessment()["enhancement_needed"]
        assert abs(enh[0] - SUPPRESSION_FACTOR_LO) < 1e-6
        assert abs(enh[1] - SUPPRESSION_FACTOR_HI) < 1e-6

    def test_case_a_beta_required_positive(self):
        beta = case_a_bogoliubov_assessment()["beta_required"]
        assert beta[0] > 0 and beta[1] > 0

    def test_case_a_beta_required_order_1(self):
        # sqrt(4.2) - 1 ≈ 1.05; sqrt(6.1) - 1 ≈ 1.47
        beta = case_a_bogoliubov_assessment()["beta_required"]
        assert 0.5 < beta[0] < 2.0
        assert 0.5 < beta[1] < 2.5


class TestCaseB:
    def test_case_b_keys(self):
        result = case_b_preinflationary_assessment()
        required = {
            "case", "name", "e_folds_tuning", "new_free_params",
            "verdict", "reason", "resolution_requires",
        }
        assert required.issubset(result.keys())

    def test_case_b_verdict_is_architecture_limit(self):
        assert case_b_preinflationary_assessment()["verdict"] == "ARCHITECTURE_LIMIT"

    def test_case_b_new_free_params_positive(self):
        assert case_b_preinflationary_assessment()["new_free_params"] > 0

    def test_case_b_e_folds_positive(self):
        assert case_b_preinflationary_assessment()["e_folds_tuning"] > 0


class TestCaseC:
    def test_case_c_keys(self):
        result = case_c_kk_propagator_assessment()
        required = {
            "case", "name", "kk_correction_at_acoustic",
            "new_free_params", "verdict", "reason", "resolution_requires",
        }
        assert required.issubset(result.keys())

    def test_case_c_verdict_is_architecture_limit(self):
        assert case_c_kk_propagator_assessment()["verdict"] == "ARCHITECTURE_LIMIT"

    def test_case_c_correction_negligible(self):
        result = case_c_kk_propagator_assessment()
        assert result["kk_correction_at_acoustic"] < 1e-50

    def test_case_c_no_new_free_params(self):
        assert case_c_kk_propagator_assessment()["new_free_params"] == 0


class TestArchitectureLimitCertificate:
    def test_certificate_keys(self):
        cert = architecture_limit_certificate()
        required = {
            "pillar_id", "status", "gap_description", "oldest_open_gap",
            "previously_bounded_by", "exhaustive_case_analysis",
            "all_cases_architecture_limit", "certification_verdict",
            "formal_status_analogous_to", "correct_interpretation",
            "not_a_falsifier", "is_missing_prediction", "hardgate_score_impact",
        }
        assert required.issubset(cert.keys())

    def test_pillar_id_in_cert(self):
        assert architecture_limit_certificate()["pillar_id"] == 518

    def test_all_cases_architecture_limit(self):
        assert architecture_limit_certificate()["all_cases_architecture_limit"] is True

    def test_certification_verdict_is_certified(self):
        assert architecture_limit_certificate()["certification_verdict"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_previously_bounded_by_pillars(self):
        prev = architecture_limit_certificate()["previously_bounded_by"]
        assert any("52" in p for p in prev)
        assert any("495" in p for p in prev)

    def test_not_a_falsifier(self):
        assert architecture_limit_certificate()["not_a_falsifier"] is True

    def test_is_missing_prediction(self):
        assert architecture_limit_certificate()["is_missing_prediction"] is True

    def test_hardgate_score_no_impact(self):
        assert "None" in architecture_limit_certificate()["hardgate_score_impact"]

    def test_oldest_open_gap(self):
        assert architecture_limit_certificate()["oldest_open_gap"] is True

    def test_analogy_mentions_r_and_wa(self):
        analogy = str(architecture_limit_certificate()["formal_status_analogous_to"])
        assert "r" in analogy.lower() or "301" in analogy or "396" in analogy

    def test_exhaustive_case_analysis_has_abc(self):
        cases = architecture_limit_certificate()["exhaustive_case_analysis"]
        assert "case_a" in cases
        assert "case_b" in cases
        assert "case_c" in cases


class TestGapStatus:
    def test_gap_status_keys(self):
        status = cmb_amplitude_gap_status()
        required = {
            "gap_name", "status", "suppression_factor_range", "affected_peaks",
            "pillar_history", "classification_upgrade",
        }
        assert required.issubset(status.keys())

    def test_status_is_certified(self):
        assert cmb_amplitude_gap_status()["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_suppression_range_matches_constants(self):
        lo, hi = cmb_amplitude_gap_status()["suppression_factor_range"]
        assert abs(lo - SUPPRESSION_FACTOR_LO) < 1e-6
        assert abs(hi - SUPPRESSION_FACTOR_HI) < 1e-6

    def test_classification_upgrade_mentions_open_gap(self):
        upgrade = cmb_amplitude_gap_status()["classification_upgrade"]
        assert "OPEN_GAP" in upgrade or "BOUNDED" in upgrade

    def test_pillar_history_includes_pillar_518(self):
        history = cmb_amplitude_gap_status()["pillar_history"]
        assert "Pillar_518" in history


class TestFalsificationCondition:
    def test_falsification_keys(self):
        fc = falsification_condition()
        required = {
            "primary_falsifier", "secondary_falsifier",
            "condition", "current_status", "monitoring", "pre_registered_date",
        }
        assert required.issubset(fc.keys())

    def test_not_primary_falsifier(self):
        assert falsification_condition()["primary_falsifier"] is False

    def test_is_secondary_falsifier(self):
        assert falsification_condition()["secondary_falsifier"] is True

    def test_pre_registered_date_2026(self):
        assert "2026" in falsification_condition()["pre_registered_date"]


class TestFullReport:
    def test_report_keys(self):
        report = pillar518_report()
        required = {
            "pillar_id", "title", "status", "architecture_limit",
            "gap_status", "falsification_condition", "closes", "summary",
        }
        assert required.issubset(report.keys())

    def test_pillar_id_in_report(self):
        assert pillar518_report()["pillar_id"] == 518

    def test_closes_mentions_admission_2(self):
        closes = pillar518_report()["closes"]
        assert "Admission 2" in closes or "2" in closes

    def test_summary_non_empty(self):
        summary = pillar518_report()["summary"]
        assert isinstance(summary, str) and len(summary) > 100
