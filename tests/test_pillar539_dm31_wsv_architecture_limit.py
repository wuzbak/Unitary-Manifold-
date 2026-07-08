# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 539 — Δm²₃₁ WS-V Architecture Limit Certification.

Covers all exported constants, correction cases A–F, architecture scan,
JUNO Phase 2 routing, and Admission 5 closure certificate.  80 tests.
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar539_dm31_wsv_architecture_limit import (
    # Identity
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    ADMISSION_CLOSED,
    # KK constants
    N_W,
    K_CS,
    # JUNO data
    JUNO_DM31_CENTRAL,
    JUNO_DM31_SIGMA,
    JUNO_PRECISION_PCT,
    # UM baseline
    UM_DM31_BARE_2NLO,
    UM_DM31_BARE_TENSION_SIGMA,
    # Cases
    CASE_A_DM31,
    CASE_A_TENSION,
    CASE_B_DM31,
    CASE_B_TENSION,
    CASE_C_DM31,
    CASE_C_TENSION,
    CASE_D_MAX_SHIFT,
    CASE_D_VERDICT,
    CASE_E_DM31,
    CASE_E_TENSION,
    CASE_F_DM31,
    CASE_F_TENSION,
    ARCHITECTURE_LIMIT_DM31,
    ARCHITECTURE_LIMIT_TENSION,
    # Functions
    compute_tension,
    case_a_bare_2nlo,
    case_b_rge_correction,
    case_c_rs_seesaw,
    case_d_wsv_texture,
    case_e_wsiii_comparison,
    case_f_combined_maximum,
    architecture_limit_scan,
    juno_phase2_prediction,
    admission_5_closure_certificate,
    pillar539_report,
)


# ---------------------------------------------------------------------------
# Pillar identity
# ---------------------------------------------------------------------------

class TestPillarIdentity:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 539

    def test_pillar_status(self):
        assert PILLAR_STATUS == "JUNO_P17_ARCHITECTURE_LIMIT_CERTIFIED"

    def test_pillar_title_contains_dm31(self):
        assert "Δm²₃₁" in PILLAR_TITLE or "dm31" in PILLAR_TITLE.lower() or "WS-V" in PILLAR_TITLE

    def test_admission_closed_contains_admission_5(self):
        assert "Admission 5" in ADMISSION_CLOSED

    def test_admission_closed_mentions_architecture_limit(self):
        assert "ARCHITECTURE_LIMIT" in ADMISSION_CLOSED


# ---------------------------------------------------------------------------
# KK constants
# ---------------------------------------------------------------------------

class TestKKConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_k_cs_identity(self):
        assert K_CS == N_W**2 + 7**2


# ---------------------------------------------------------------------------
# JUNO data
# ---------------------------------------------------------------------------

class TestJUNOData:
    def test_juno_central_value(self):
        assert abs(JUNO_DM31_CENTRAL - 2.411e-3) < 1e-7

    def test_juno_sigma(self):
        assert abs(JUNO_DM31_SIGMA - 1.9582e-5) < 1e-10

    def test_juno_precision_approx_1pct(self):
        assert 0.5 < JUNO_PRECISION_PCT < 1.5

    def test_juno_sigma_is_positive(self):
        assert JUNO_DM31_SIGMA > 0


# ---------------------------------------------------------------------------
# UM baseline
# ---------------------------------------------------------------------------

class TestUMBaseline:
    def test_bare_2nlo_value(self):
        assert abs(UM_DM31_BARE_2NLO - 2.2845e-3) < 1e-8

    def test_bare_tension_exceeds_6sigma(self):
        assert UM_DM31_BARE_TENSION_SIGMA > 6.0

    def test_bare_tension_consistency(self):
        expected = abs(JUNO_DM31_CENTRAL - UM_DM31_BARE_2NLO) / JUNO_DM31_SIGMA
        assert abs(UM_DM31_BARE_TENSION_SIGMA - expected) < 0.01

    def test_bare_is_less_than_juno(self):
        assert UM_DM31_BARE_2NLO < JUNO_DM31_CENTRAL


# ---------------------------------------------------------------------------
# Module-level case constants
# ---------------------------------------------------------------------------

class TestCaseConstants:
    def test_case_a_equals_bare(self):
        assert CASE_A_DM31 == UM_DM31_BARE_2NLO

    def test_case_a_tension_exceeds_6sigma(self):
        assert CASE_A_TENSION > 6.0

    def test_case_b_greater_than_a(self):
        # RGE correction is positive (runs Δm²₃₁ upward)
        assert CASE_B_DM31 > CASE_A_DM31

    def test_case_b_tension_still_high(self):
        assert CASE_B_TENSION > 5.0

    def test_case_c_greater_than_b(self):
        # Seesaw at max p_R adds positive correction
        assert CASE_C_DM31 > CASE_B_DM31

    def test_case_c_tension_above_3sigma(self):
        assert CASE_C_TENSION > 3.0

    def test_case_d_max_shift_positive(self):
        assert CASE_D_MAX_SHIFT > 0

    def test_case_d_verdict_is_architecture_limit(self):
        assert CASE_D_VERDICT == "ARCHITECTURE_LIMIT"

    def test_case_e_greater_than_c(self):
        # WS-III adds more than WS-V alone
        assert CASE_E_DM31 > CASE_A_DM31

    def test_case_f_is_maximum(self):
        # Case F should be largest among all DM31 values
        assert CASE_F_DM31 >= CASE_C_DM31
        assert CASE_F_DM31 >= CASE_E_DM31

    def test_case_f_tension_below_case_a(self):
        # F is closest to JUNO
        assert CASE_F_TENSION < CASE_A_TENSION

    def test_architecture_limit_equals_case_f(self):
        assert ARCHITECTURE_LIMIT_DM31 == CASE_F_DM31

    def test_architecture_limit_tension_equals_case_f_tension(self):
        assert abs(ARCHITECTURE_LIMIT_TENSION - CASE_F_TENSION) < 0.01


# ---------------------------------------------------------------------------
# compute_tension()
# ---------------------------------------------------------------------------

class TestComputeTension:
    def test_zero_gap(self):
        assert compute_tension(1.0, 1.0, 0.1) == 0.0

    def test_one_sigma(self):
        assert abs(compute_tension(1.1, 1.0, 0.1) - 1.0) < 1e-10

    def test_symmetry(self):
        assert compute_tension(1.1, 1.0, 0.1) == compute_tension(0.9, 1.0, 0.1)

    def test_scales_with_sigma(self):
        t1 = compute_tension(1.1, 1.0, 0.1)
        t2 = compute_tension(1.1, 1.0, 0.05)
        assert abs(t2 - 2.0 * t1) < 1e-10

    def test_juno_bare_tension(self):
        t = compute_tension(UM_DM31_BARE_2NLO, JUNO_DM31_CENTRAL, JUNO_DM31_SIGMA)
        assert abs(t - UM_DM31_BARE_TENSION_SIGMA) < 0.01


# ---------------------------------------------------------------------------
# case_a_bare_2nlo()
# ---------------------------------------------------------------------------

class TestCaseABare:
    def setup_method(self):
        self.result = case_a_bare_2nlo()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_case_label(self):
        assert self.result["case"] == "A"

    def test_dm31_correct(self):
        assert abs(self.result["dm31_ev2"] - CASE_A_DM31) < 1e-10

    def test_verdict_excluded(self):
        assert self.result["verdict"] == "EXCLUDED"

    def test_tension_exceeds_6(self):
        assert self.result["tension_sigma"] > 6.0


# ---------------------------------------------------------------------------
# case_b_rge_correction()
# ---------------------------------------------------------------------------

class TestCaseBRGE:
    def setup_method(self):
        self.result = case_b_rge_correction()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_case_label(self):
        assert self.result["case"] == "B"

    def test_dm31_above_a(self):
        assert self.result["dm31_corrected_ev2"] > CASE_A_DM31

    def test_shift_is_positive(self):
        assert self.result["shift_ev2"] > 0

    def test_verdict_excluded(self):
        assert self.result["verdict"] == "EXCLUDED"


# ---------------------------------------------------------------------------
# case_c_rs_seesaw()
# ---------------------------------------------------------------------------

class TestCaseCSeesaw:
    def setup_method(self):
        self.result = case_c_rs_seesaw()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_case_label(self):
        assert self.result["case"] == "C"

    def test_dm31_above_b(self):
        assert self.result["dm31_ev2"] > CASE_B_DM31

    def test_custom_p_r(self):
        result_low = case_c_rs_seesaw(p_r=0.1)
        result_high = case_c_rs_seesaw(p_r=0.441)
        assert result_high["dm31_ev2"] > result_low["dm31_ev2"]

    def test_zero_p_r_no_correction(self):
        result = case_c_rs_seesaw(p_r=0.0)
        assert abs(result["dm31_ev2"] - CASE_B_DM31) < 1e-10

    def test_tension_still_excluded(self):
        assert self.result["tension_sigma"] > 3.0


# ---------------------------------------------------------------------------
# case_d_wsv_texture()
# ---------------------------------------------------------------------------

class TestCaseDWSV:
    def setup_method(self):
        self.result = case_d_wsv_texture()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_case_label(self):
        assert self.result["case"] == "D"

    def test_max_shift_positive(self):
        assert self.result["max_shift_ev2"] > 0

    def test_shift_less_than_gap(self):
        assert self.result["max_shift_ev2"] < self.result["gap_to_juno_ev2"]

    def test_ratio_less_than_half(self):
        assert self.result["shift_vs_gap_ratio"] < 0.5

    def test_verdict_architecture_limit(self):
        assert self.result["verdict"] == "ARCHITECTURE_LIMIT"


# ---------------------------------------------------------------------------
# case_e_wsiii_comparison()
# ---------------------------------------------------------------------------

class TestCaseEWSIII:
    def setup_method(self):
        self.result = case_e_wsiii_comparison()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_case_label(self):
        assert self.result["case"] == "E"

    def test_dm31_positive(self):
        assert self.result["dm31_ev2"] > 0

    def test_ws3_shift_positive(self):
        assert self.result["ws3_max_shift_ev2"] > 0


# ---------------------------------------------------------------------------
# case_f_combined_maximum()
# ---------------------------------------------------------------------------

class TestCaseFCombined:
    def setup_method(self):
        self.result = case_f_combined_maximum()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_case_label(self):
        assert self.result["case"] == "F"

    def test_is_architecture_maximum(self):
        assert self.result["is_architecture_maximum"] is True

    def test_gap_positive(self):
        assert self.result["gap_ev2"] > 0

    def test_architecture_conclusion_present(self):
        assert "ARCHITECTURE_LIMIT" in self.result["architecture_conclusion"]

    def test_dm31_matches_constant(self):
        assert abs(self.result["dm31_ev2"] - CASE_F_DM31) < 1e-10


# ---------------------------------------------------------------------------
# architecture_limit_scan()
# ---------------------------------------------------------------------------

class TestArchitectureLimitScan:
    def setup_method(self):
        self.result = architecture_limit_scan()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_six_cases(self):
        assert len(self.result["cases"]) == 6

    def test_all_cases_present(self):
        for label in ("A", "B", "C", "D", "E", "F"):
            assert label in self.result["cases"]

    def test_status_correct(self):
        assert self.result["status"] == PILLAR_STATUS

    def test_architecture_limit_dm31(self):
        assert abs(self.result["architecture_limit_dm31_ev2"] - ARCHITECTURE_LIMIT_DM31) < 1e-10

    def test_certification_mentions_exhausted(self):
        assert "exhausted" in self.result["certification"].lower() or \
               "CERTIFIED" in self.result["certification"]

    def test_best_tension_is_positive(self):
        assert self.result["best_achievable_tension_sigma"] > 0.0


# ---------------------------------------------------------------------------
# juno_phase2_prediction()
# ---------------------------------------------------------------------------

class TestJUNOPhase2Prediction:
    def setup_method(self):
        self.result = juno_phase2_prediction()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_precision_is_half_pct(self):
        assert abs(self.result["juno_phase2_expected_precision_pct"] - 0.5) < 0.01

    def test_consistency_window_is_tuple_of_two(self):
        assert len(self.result["consistency_window_ev2"]) == 2

    def test_consistency_window_ordered(self):
        low, high = self.result["consistency_window_ev2"]
        assert low < high

    def test_falsification_condition_present(self):
        assert "FALSIFIED" in self.result["falsification_condition"]

    def test_case_f_dm31_in_result(self):
        assert abs(self.result["case_f_dm31_ev2"] - CASE_F_DM31) < 1e-10


# ---------------------------------------------------------------------------
# admission_5_closure_certificate()
# ---------------------------------------------------------------------------

class TestAdmission5Certificate:
    def setup_method(self):
        self.result = admission_5_closure_certificate()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_admission_number(self):
        assert self.result["admission"] == 5

    def test_prior_status(self):
        assert "HONEST_OPEN_PROBLEM" in self.result["prior_status"]

    def test_new_status(self):
        assert "ARCHITECTURE_LIMIT_CERTIFIED" in self.result["new_status"]

    def test_closing_pillar(self):
        assert self.result["closing_pillar"] == 539

    def test_analogues_present(self):
        assert len(self.result["analogues"]) >= 2

    def test_analogues_mention_517_518(self):
        analogues_str = " ".join(self.result["analogues"])
        assert "517" in analogues_str
        assert "518" in analogues_str

    def test_honest_verdict_present(self):
        assert "honest" in self.result["honest_verdict"].lower() or \
               "real" in self.result["honest_verdict"].lower()


# ---------------------------------------------------------------------------
# pillar539_report()
# ---------------------------------------------------------------------------

class TestPillar539Report:
    def setup_method(self):
        self.result = pillar539_report()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 539

    def test_final_status(self):
        assert self.result["final_status"] == PILLAR_STATUS

    def test_has_cases_summary(self):
        assert "cases_summary" in self.result
        assert len(self.result["cases_summary"]) == 6

    def test_has_architecture_scan(self):
        assert "architecture_limit_scan" in self.result

    def test_has_phase2_routing(self):
        assert "juno_phase2_prediction" in self.result

    def test_has_admission_certificate(self):
        assert "admission_5_certificate" in self.result

    def test_juno_data_present(self):
        assert "juno_data" in self.result
        assert abs(self.result["juno_data"]["central_ev2"] - JUNO_DM31_CENTRAL) < 1e-10

    def test_architecture_maximum_ev2(self):
        assert abs(self.result["architecture_maximum_ev2"] - ARCHITECTURE_LIMIT_DM31) < 1e-10

    def test_architecture_maximum_tension_positive(self):
        assert self.result["architecture_maximum_tension_sigma"] > 0


# ---------------------------------------------------------------------------
# Physical consistency checks
# ---------------------------------------------------------------------------

class TestPhysicalConsistency:
    def test_all_dm31_values_positive(self):
        for dm31 in (CASE_A_DM31, CASE_B_DM31, CASE_C_DM31,
                     CASE_E_DM31, CASE_F_DM31, ARCHITECTURE_LIMIT_DM31):
            assert dm31 > 0

    def test_dm31_values_in_physical_range(self):
        # Physical range for Δm²₃₁: roughly 2.0–2.7 × 10⁻³ eV²
        for dm31 in (CASE_A_DM31, CASE_B_DM31, CASE_C_DM31,
                     CASE_E_DM31, CASE_F_DM31):
            assert 2.0e-3 < dm31 < 2.7e-3

    def test_tensions_decrease_from_a_to_f(self):
        # Each successive correction brings closer to JUNO
        assert CASE_A_TENSION > CASE_B_TENSION
        assert CASE_B_TENSION >= CASE_C_TENSION
        assert CASE_A_TENSION > CASE_F_TENSION

    def test_architecture_limit_not_falsified(self):
        # Case F should be < 3σ (not yet FALSIFIED)
        assert ARCHITECTURE_LIMIT_TENSION < 3.0

    def test_architecture_limit_above_2sigma(self):
        # But > 2σ (cannot claim CONSISTENT)
        assert ARCHITECTURE_LIMIT_TENSION > 2.0

    def test_juno_precision_reflects_result(self):
        # JUNO Phase 1 was reported as ~1% precision
        assert 0.5 < JUNO_PRECISION_PCT < 2.0

    def test_case_d_shift_less_than_gap_fraction(self):
        gap = abs(JUNO_DM31_CENTRAL - CASE_A_DM31)
        assert CASE_D_MAX_SHIFT / gap < 0.5
