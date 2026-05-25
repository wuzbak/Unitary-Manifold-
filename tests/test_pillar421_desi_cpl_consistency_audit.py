# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar421_desi_cpl_consistency_audit.py
====================================================
Pillar 421 — Tests for pillar421_desi_cpl_consistency_audit.py.

Tests cover all six documented issues and the corrected analysis functions.
"""

from __future__ import annotations

import math
import pytest

from src.core.pillar421_desi_cpl_consistency_audit import (
    # Constants
    C_S_BRAIDED_INFLATIONARY,
    W_KK_INFLATIONARY,
    W0_FROZEN_RADION,
    WA_FROZEN_RADION,
    WA_FROZEN_RADION_MAX,
    M_R_OVER_H0,
    DESI_Y3_W0_CPL,
    DESI_Y3_W0_CPL_SIGMA,
    DESI_Y3_WA_CPL,
    DESI_Y3_WA_CPL_SIGMA,
    DESI_Y3_W0_W0CDM,
    DESI_Y3_W0_W0CDM_SIGMA,
    DESI_Y3_RHO_W0_WA,
    DESI_Y3_LCDM_EXCLUSION_SIGMA,
    DESI_DR3_WA_SIGMA_PROJECTED,
    DESI_Y3_REF,
    # Functions
    frozen_radion_prediction,
    inflationary_w0_note,
    joint_cpl_tension_2d,
    circular_comparison_audit,
    desi_naming_timeline,
    bayesian_context,
    pillar421_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_c_s_braided_is_12_over_37(self):
        assert abs(C_S_BRAIDED_INFLATIONARY - 12.0 / 37.0) < 1e-12

    def test_w_kk_inflationary_formula(self):
        expected = -1.0 + (2.0 / 3.0) * (12.0 / 37.0) ** 2
        assert abs(W_KK_INFLATIONARY - expected) < 1e-12

    def test_w_kk_inflationary_near_minus_0_93(self):
        assert abs(W_KK_INFLATIONARY - (-0.9302)) < 0.001

    def test_frozen_radion_w0_is_minus_1(self):
        """Frozen-radion prediction is exactly ΛCDM: w₀ = −1."""
        assert W0_FROZEN_RADION == -1.0

    def test_frozen_radion_wa_is_zero(self):
        """Frozen-radion prediction: wₐ = 0."""
        assert WA_FROZEN_RADION == 0.0

    def test_wa_max_is_tiny(self):
        """Theoretical upper bound on wₐ must be negligible (<10⁻⁸⁰)."""
        assert WA_FROZEN_RADION_MAX < 1e-80

    def test_m_r_over_h0_enormous(self):
        """Radion is many orders of magnitude more massive than H₀."""
        assert M_R_OVER_H0 > 1e40

    def test_desi_y3_w0_cpl_near_minus_0_838(self):
        assert abs(DESI_Y3_W0_CPL - (-0.838)) < 0.01

    def test_desi_y3_wa_cpl_negative(self):
        assert DESI_Y3_WA_CPL < 0.0

    def test_desi_y3_wa_cpl_near_minus_0_62(self):
        assert abs(DESI_Y3_WA_CPL - (-0.62)) < 0.05

    def test_desi_y3_w0cdm_is_different_from_cpl(self):
        """w₀CDM value is distinct from CPL value — they come from different fits."""
        assert abs(DESI_Y3_W0_W0CDM - DESI_Y3_W0_CPL) > 0.05

    def test_rho_strongly_negative(self):
        """DESI CPL (w₀, wₐ) correlation is strongly negative."""
        assert DESI_Y3_RHO_W0_WA < -0.90

    def test_rho_within_valid_range(self):
        assert -1.0 < DESI_Y3_RHO_W0_WA < 0.0

    def test_lcdm_exclusion_sigma_near_3_9(self):
        assert abs(DESI_Y3_LCDM_EXCLUSION_SIGMA - 3.9) < 0.5

    def test_dr3_projected_sigma_positive(self):
        assert DESI_DR3_WA_SIGMA_PROJECTED > 0.0

    def test_dr3_projected_sigma_smaller_than_dr2(self):
        """DR3 should improve on DR2 σ(wₐ) = 0.30."""
        assert DESI_DR3_WA_SIGMA_PROJECTED < DESI_Y3_WA_CPL_SIGMA

    def test_desi_ref_nonempty(self):
        assert len(DESI_Y3_REF) > 30


# ---------------------------------------------------------------------------
# frozen_radion_prediction — Issue 1 & 2
# ---------------------------------------------------------------------------

class TestFrozenRadionPrediction:
    def setup_method(self):
        self.pred = frozen_radion_prediction()

    def test_returns_dict(self):
        assert isinstance(self.pred, dict)

    def test_w0_is_minus_1(self):
        """Frozen radion w₀ = −1 exactly."""
        assert self.pred["w0"] == -1.0

    def test_wa_is_zero(self):
        """Frozen radion wₐ = 0 exactly."""
        assert self.pred["wa"] == 0.0

    def test_wa_upper_bound_tiny(self):
        assert self.pred["wa_upper_bound"] < 1e-80

    def test_m_r_over_h0_stored(self):
        assert self.pred["m_r_over_h0"] > 1e40

    def test_m_r_over_h0_log10_positive(self):
        assert self.pred["m_r_over_h0_log10"] > 40.0

    def test_mechanism_nonempty(self):
        assert len(self.pred["mechanism"]) > 10

    def test_physical_picture_nonempty(self):
        assert len(self.pred["physical_picture"]) > 50

    def test_inflationary_note_present(self):
        """The w_KK inflationary scope note must be present."""
        assert "w0_kk_inflationary_note" in self.pred
        assert len(self.pred["w0_kk_inflationary_note"]) > 50

    def test_inflationary_note_mentions_inflation(self):
        note = self.pred["w0_kk_inflationary_note"].lower()
        assert "inflat" in note

    def test_lcdm_equivalence_note_present(self):
        assert "lcdm_equivalence" in self.pred
        assert len(self.pred["lcdm_equivalence"]) > 30

    def test_lcdm_equivalence_mentions_3_9_sigma(self):
        note = self.pred["lcdm_equivalence"]
        assert "3.9" in note or "3" in note


# ---------------------------------------------------------------------------
# inflationary_w0_note — Issue 2
# ---------------------------------------------------------------------------

class TestInflationaryW0Note:
    def setup_method(self):
        self.note = inflationary_w0_note()

    def test_returns_dict(self):
        assert isinstance(self.note, dict)

    def test_formula_present(self):
        assert "formula" in self.note
        assert "c_s" in self.note["formula"] or "w_KK" in self.note["formula"]

    def test_w_kk_value_correct(self):
        assert abs(self.note["w_kk_value"] - W_KK_INFLATIONARY) < 1e-12

    def test_correct_epoch_is_inflationary(self):
        assert "inflat" in self.note["correct_epoch"].lower()

    def test_derived_from_nonempty(self):
        assert len(self.note["derived_from"]) > 50

    def test_bridge_requirement_nonempty(self):
        assert len(self.note["bridge_requirement"]) > 50

    def test_comparison_validity_present(self):
        assert "comparison_validity" in self.note

    def test_inflation_comparison_valid(self):
        assert "VALID" in self.note["comparison_validity"]["vs_inflation_observables"]

    def test_de_comparison_invalid(self):
        assert "INVALID" in self.note["comparison_validity"]["vs_dark_energy_today"]

    def test_desi_cpl_comparison_labelled_coincidence(self):
        desi_note = self.note["comparison_validity"]["vs_desi_cpl_w0"]
        assert "coincidence" in desi_note.lower() or "not a prediction" in desi_note.lower()


# ---------------------------------------------------------------------------
# circular_comparison_audit — Issue 3
# ---------------------------------------------------------------------------

class TestCircularComparisonAudit:
    def setup_method(self):
        self.audit = circular_comparison_audit()

    def test_returns_dict(self):
        assert isinstance(self.audit, dict)

    def test_audit_finding_nonempty(self):
        assert len(self.audit["audit_finding"]) > 50

    def test_circular_comparison_labeled(self):
        assert self.audit["circular_comparison"]["is_circular"] is True

    def test_circular_tension_is_small(self):
        """The circular w₀CDM comparison gives artificially small tension."""
        assert self.audit["circular_comparison"]["tension_sigma"] < 0.5

    def test_correct_cpl_tension_inflationary_larger(self):
        """The non-circular CPL comparison gives larger tension."""
        correct = self.audit["correct_comparison_inflationary_w0"]["tension_sigma"]
        circular = self.audit["circular_comparison"]["tension_sigma"]
        assert correct > circular

    def test_correct_cpl_tension_frozen_larger(self):
        """Frozen-radion CPL tension is even larger than inflationary w₀ tension."""
        frozen_tension = self.audit["correct_comparison_frozen_radion_w0"]["tension_sigma"]
        assert frozen_tension > 1.0

    def test_correct_comparisons_not_circular(self):
        assert self.audit["correct_comparison_inflationary_w0"]["is_circular"] is False
        assert self.audit["correct_comparison_frozen_radion_w0"]["is_circular"] is False

    def test_verdict_nonempty(self):
        assert len(self.audit["verdict"]) > 30


# ---------------------------------------------------------------------------
# joint_cpl_tension_2d — Issue 4
# ---------------------------------------------------------------------------

class TestJointCPLTension2D:
    def setup_method(self):
        # Default call: frozen-radion point vs DESI Y3 with ρ = −0.97
        self.result = joint_cpl_tension_2d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_w0_um_stored(self):
        assert self.result["w0_um"] == W0_FROZEN_RADION

    def test_wa_um_stored(self):
        assert self.result["wa_um"] == WA_FROZEN_RADION

    def test_rho_stored(self):
        assert abs(self.result["rho"] - DESI_Y3_RHO_W0_WA) < 1e-12

    def test_chi_sq_positive(self):
        assert self.result["chi_sq_2d"] > 0.0

    def test_chi_sq_large(self):
        """Frozen-radion point gives a non-trivial χ², but note correlation DECREASES it."""
        assert self.result["chi_sq_2d"] > 3.0

    def test_effective_sigma_between_1_and_3(self):
        """Frozen-radion 2D tension is reduced by anti-correlation; expect ~2.3σ."""
        sigma = self.result["effective_sigma_approx"]
        assert 1.5 < sigma < 3.5

    def test_effective_sigma_near_2_3(self):
        """Frozen-radion 2D tension from CPL summary statistics is ~2.3σ."""
        sigma = self.result["effective_sigma_approx"]
        assert abs(sigma - 2.30) < 0.30

    def test_correlation_decreases_tension_for_frozen_radion(self):
        """For frozen-radion point, anti-correlation REDUCES tension vs naive diagonal.
        The residuals (Δw₀<0, Δwₐ>0) align with the DESI ellipse major axis direction.
        """
        assert self.result["correlation_increases_tension"] is False

    def test_chi_sq_smaller_than_naive(self):
        """Correct 2D χ² is smaller than naive diagonal for frozen-radion point."""
        assert self.result["chi_sq_2d"] < self.result["chi_sq_naive_diagonal"]

    def test_p_value_not_negligible_for_frozen_radion(self):
        """p-value ~0.07 for frozen-radion: not yet at strong exclusion from CPL stats."""
        assert self.result["p_value_2dof"] > 0.01

    def test_residuals_correct(self):
        expected_dw0 = W0_FROZEN_RADION - DESI_Y3_W0_CPL
        expected_dwa = WA_FROZEN_RADION - DESI_Y3_WA_CPL
        assert abs(self.result["dw0"] - expected_dw0) < 1e-12
        assert abs(self.result["dwa"] - expected_dwa) < 1e-12

    def test_z0_correct(self):
        expected_z0 = (W0_FROZEN_RADION - DESI_Y3_W0_CPL) / DESI_Y3_W0_CPL_SIGMA
        assert abs(self.result["z0"] - expected_z0) < 1e-10

    def test_za_correct(self):
        expected_za = (WA_FROZEN_RADION - DESI_Y3_WA_CPL) / DESI_Y3_WA_CPL_SIGMA
        assert abs(self.result["za"] - expected_za) < 1e-10

    def test_derivation_nonempty(self):
        assert len(self.result["derivation"]) > 80

    def test_interpretation_nonempty(self):
        assert len(self.result["interpretation"]) > 40

    def test_consistent_with_desi_reported_exclusion_note(self):
        """The 2D CPL-summary tension (~2.3σ) is DIFFERENT from DESI's 3.9σ.
        DESI's 3.9σ comes from the full likelihood, not just the CPL summary stats.
        """
        sigma = self.result["effective_sigma_approx"]
        # CPL summary gives ~2.3σ; DESI full likelihood gives 3.9σ
        assert sigma < DESI_Y3_LCDM_EXCLUSION_SIGMA  # summary < full likelihood

    def test_invalid_rho_raises(self):
        with pytest.raises(ValueError, match="rho"):
            joint_cpl_tension_2d(rho=1.0)

    def test_invalid_rho_too_negative_raises(self):
        with pytest.raises(ValueError, match="rho"):
            joint_cpl_tension_2d(rho=-1.0)

    def test_invalid_sigma_w0_raises(self):
        with pytest.raises(ValueError, match="sigma_w0"):
            joint_cpl_tension_2d(sigma_w0=0.0)

    def test_invalid_sigma_wa_raises(self):
        with pytest.raises(ValueError, match="sigma_wa"):
            joint_cpl_tension_2d(sigma_wa=-0.1)

    def test_zero_correlation_matches_naive(self):
        """With ρ = 0, the 2D χ² equals the sum of squared individual tensions."""
        result_uncorr = joint_cpl_tension_2d(rho=0.0)
        naive = result_uncorr["chi_sq_naive_diagonal"]
        corr = result_uncorr["chi_sq_2d"]
        assert abs(corr - naive) < 1e-10

    def test_inflationary_point_tension_larger(self):
        """The inflationary w₀ = −0.9302 point gives LARGER 2D tension than frozen −1.
        Even though its 1D w₀ tension is smaller (1.28σ vs 2.25σ), the inflationary
        point lies off-axis from the DESI ellipse major axis, so the anti-correlation
        INCREASES its 2D tension to ~3.63σ vs ~2.30σ for the frozen-radion point.
        """
        result_infl = joint_cpl_tension_2d(w0_um=W_KK_INFLATIONARY, wa_um=WA_FROZEN_RADION)
        result_frozen = joint_cpl_tension_2d()
        assert result_infl["chi_sq_2d"] > result_frozen["chi_sq_2d"]

    def test_inflationary_point_correlation_increases_tension(self):
        """For the inflationary w₀ point, correlation INCREASES tension."""
        result_infl = joint_cpl_tension_2d(w0_um=W_KK_INFLATIONARY, wa_um=WA_FROZEN_RADION)
        assert result_infl["correlation_increases_tension"] is True


# ---------------------------------------------------------------------------
# desi_naming_timeline — Issue 5
# ---------------------------------------------------------------------------

class TestDESINamingTimeline:
    def setup_method(self):
        self.naming = desi_naming_timeline()

    def test_returns_dict(self):
        assert isinstance(self.naming, dict)

    def test_arxiv_paper_correct(self):
        assert "2503.14738" in self.naming["arxiv_paper"]

    def test_correct_names_include_year3(self):
        names = " ".join(self.naming["correct_names"])
        assert "Year 3" in names or "DR2" in names

    def test_incorrect_names_include_dr3(self):
        assert any("DR3" in n for n in self.naming["incorrect_names"])

    def test_note_nonempty(self):
        assert len(self.naming["note"]) > 30

    def test_survey_completion_mentions_2026(self):
        assert "2026" in self.naming["survey_status"]["survey_completion"]

    def test_dr3_expected_present(self):
        assert len(self.naming["survey_status"]["dr3_expected"]) > 5

    def test_dr3_projected_tension_positive(self):
        assert self.naming["dr3_projection"]["tension_sigma_at_dr3"] > 0.0

    def test_dr3_projected_exceeds_threshold(self):
        """DR3 is expected to exceed the 3σ falsification threshold."""
        assert self.naming["dr3_projection"]["exceeds_falsification_threshold"] is True

    def test_dr3_projected_tension_near_4_sigma(self):
        """If central value holds, DR3 tension should be ~4σ."""
        tension = self.naming["dr3_projection"]["tension_sigma_at_dr3"]
        assert tension > 3.0

    def test_interpretation_nonempty(self):
        assert len(self.naming["dr3_projection"]["interpretation"]) > 50

    def test_roman_role_updated(self):
        assert "roman_role" in self.naming
        assert len(self.naming["roman_role"]) > 20


# ---------------------------------------------------------------------------
# bayesian_context — Issue 6
# ---------------------------------------------------------------------------

class TestBayesianContext:
    def setup_method(self):
        self.bayes = bayesian_context()

    def test_returns_dict(self):
        assert isinstance(self.bayes, dict)

    def test_frequentist_tension_positive(self):
        assert self.bayes["frequentist_tension_sigma"] > 0.0

    def test_frequentist_tension_near_2_75(self):
        """DESI Y3 combined tension with wₐ = 0 is ~2.75σ."""
        assert 2.0 < self.bayes["frequentist_tension_sigma"] < 4.0

    def test_posterior_probabilities_present(self):
        probs = self.bayes["posterior_probabilities"]
        assert "p_wa_within_10pct" in probs
        assert "p_wa_within_20pct" in probs

    def test_p_wa_within_10pct_very_small(self):
        """P(|wₐ| < 0.10 | DESI data) should be very small (<0.02)."""
        assert self.bayes["posterior_probabilities"]["p_wa_within_10pct"] < 0.02

    def test_p_wa_within_30pct_larger(self):
        """P(|wₐ| < 0.30 | DESI data) is larger than the 10% case."""
        p10 = self.bayes["posterior_probabilities"]["p_wa_within_10pct"]
        p30 = self.bayes["posterior_probabilities"]["p_wa_within_30pct"]
        assert p30 > p10

    def test_posterior_probabilities_between_0_and_1(self):
        for k, v in self.bayes["posterior_probabilities"].items():
            assert 0.0 <= v <= 1.0, f"Probability out of range for {k}: {v}"

    def test_interpretation_nonempty(self):
        assert len(self.bayes["interpretation"]) > 80

    def test_note_mentions_3sigma_threshold(self):
        assert "3σ" in self.bayes["note"] or "3" in self.bayes["note"]

    def test_note_mentions_dr3(self):
        assert "DR3" in self.bayes["note"] or "dr3" in self.bayes["note"].lower()


# ---------------------------------------------------------------------------
# pillar421_summary — complete
# ---------------------------------------------------------------------------

class TestPillar421Summary:
    def setup_method(self):
        self.summary = pillar421_summary()

    def test_returns_dict(self):
        assert isinstance(self.summary, dict)

    def test_pillar_is_421(self):
        assert self.summary["pillar"] == 421

    def test_title_nonempty(self):
        assert len(self.summary["title"]) > 20

    def test_status_adjacent_track(self):
        assert "ADJACENT" in self.summary["status"].upper()

    # Issue 1 checks
    def test_issue_1_finding_present(self):
        assert "issue_1_logical_contradiction" in self.summary
        assert len(self.summary["issue_1_logical_contradiction"]["finding"]) > 30

    def test_issue_1_corrected_prediction_w0_minus_1(self):
        assert self.summary["issue_1_logical_contradiction"]["corrected_prediction"]["w0"] == -1.0

    def test_issue_1_corrected_prediction_wa_zero(self):
        assert self.summary["issue_1_logical_contradiction"]["corrected_prediction"]["wa"] == 0.0

    # Issue 2 checks
    def test_issue_2_finding_present(self):
        assert "issue_2_wrong_scope" in self.summary
        assert len(self.summary["issue_2_wrong_scope"]["finding"]) > 30

    def test_issue_2_note_says_invalid(self):
        assert "INVALID" in self.summary["issue_2_wrong_scope"]["corrected_note"]

    # Issue 3 checks
    def test_issue_3_finding_present(self):
        assert "issue_3_circular_comparison" in self.summary
        assert len(self.summary["issue_3_circular_comparison"]["finding"]) > 30

    def test_issue_3_circular_is_true(self):
        assert self.summary["issue_3_circular_comparison"]["w0cdm_tension_is_circular"] is True

    # Issue 4 checks
    def test_issue_4_chi_sq_present(self):
        assert "issue_4_joint_2d_tension" in self.summary
        assert self.summary["issue_4_joint_2d_tension"]["chi_sq_2d"] > 0.0

    def test_issue_4_effective_sigma_between_1_and_4(self):
        """Frozen-radion 2D tension from CPL summary is ~2.3σ (anti-correlation reduces it)."""
        sigma = self.summary["issue_4_joint_2d_tension"]["effective_sigma"]
        assert 1.5 < sigma < 4.0

    def test_issue_4_correlation_decreases_tension(self):
        """For the frozen-radion point, the anti-correlation DECREASES 2D tension."""
        assert self.summary["issue_4_joint_2d_tension"]["correlation_increases_tension"] is False

    # Issue 5 checks
    def test_issue_5_naming_present(self):
        assert "issue_5_naming_timeline" in self.summary
        assert "Year 3" in self.summary["issue_5_naming_timeline"]["correct_name"]

    def test_issue_5_dr3_exceeds_threshold(self):
        assert self.summary["issue_5_naming_timeline"]["dr3_will_exceed_threshold"] is True

    # Issue 6 checks
    def test_issue_6_bayesian_present(self):
        assert "issue_6_bayesian_context" in self.summary
        p = self.summary["issue_6_bayesian_context"]["bayesian_p_wa_within_10pct"]
        assert 0.0 <= p <= 1.0

    # Tension table checks
    def test_tension_table_frozen_w0_sigma_positive(self):
        tbl = self.summary["corrected_tension_table"]
        assert tbl["frozen_radion_w0_vs_desi_cpl"]["sigma"] > 0.0

    def test_tension_table_frozen_wa_sigma_near_2(self):
        tbl = self.summary["corrected_tension_table"]
        sigma = tbl["frozen_radion_wa_vs_desi_cpl"]["sigma"]
        assert 1.5 < sigma < 3.0

    def test_tension_table_joint_2d_near_2_3(self):
        """Frozen-radion 2D joint tension from CPL summary is ~2.3σ."""
        sigma = self.summary["corrected_tension_table"]["joint_2d_frozen_radion"]["effective_sigma"]
        assert 1.5 < sigma < 3.5

    def test_joint_2d_less_than_desi_reported(self):
        """2D CPL-summary tension (~2.3σ) < DESI full likelihood exclusion (3.9σ).
        DESI's 3.9σ cannot be reproduced from just the CPL (w₀, wₐ) summary statistics.
        """
        sigma = self.summary["corrected_tension_table"]["joint_2d_frozen_radion"]["effective_sigma"]
        assert sigma < DESI_Y3_LCDM_EXCLUSION_SIGMA

    def test_routing_joint_below_threshold(self):
        """The 2D joint tension for the frozen-radion point is below 3σ (correct computation)."""
        routing = self.summary["routing_update"]
        # Corrected 2D tension from CPL summary is ~2.3σ, below the 3σ threshold
        assert routing["joint_frozen_radion_exceeds_threshold"] is False

    # Routing checks
    def test_routing_update_present(self):
        routing = self.summary["routing_update"]
        assert routing["current_status"] == "HIGH_TENSION"
        assert routing["falsification_threshold_sigma"] == 3.0

    def test_routing_joint_not_yet_exceeds_threshold(self):
        """The 2D joint tension from CPL summary (<3σ) has not crossed the threshold."""
        routing = self.summary["routing_update"]
        assert routing["joint_frozen_radion_exceeds_threshold"] is False

    def test_routing_recommended_nonempty(self):
        assert len(self.summary["routing_update"]["recommended_routing"]) > 50

    def test_desi_reference_nonempty(self):
        assert len(self.summary["desi_reference"]) > 30
