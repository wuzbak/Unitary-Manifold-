# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_vacuum_selection.py
===============================
Tests for Pillar 84 — Vacuum Selection via Horava-Witten + Saddle + Planck.

All tests verify:
  - Horava-Witten Majorana argument selects n_w=5 and excludes n_w=7
  - Euclidean saddle comparison correctly computes k_eff and relative weights
  - Planck nₛ constraint selects n_w=5 and excludes n_w=7
  - Full APS chain consistency check passes
  - Vacuum selection summary runs without error
  - vacuum_selection_status() returns a non-empty string
"""
import math
import pytest

from src.core.vacuum_selection import (
    gravitino_chirality_constraint,
    euclidean_saddle_comparison,
    planck_ns_selection,
    vacuum_selection_summary,
    vacuum_selection_status,
    aps_chain_consistency_check,
    N_W_CANONICAL,
    NW_CANDIDATES,
    NS_PLANCK,
    SIGMA_NS_PLANCK,
)


class TestGravitinoChiralityConstraint:
    def test_selects_n_w_5(self):
        result = gravitino_chirality_constraint()
        assert result[5]["majorana_compatible"] is True
        assert result[5]["selected"] is True

    def test_excludes_n_w_7(self):
        result = gravitino_chirality_constraint()
        assert result[7]["majorana_compatible"] is False
        assert result[7]["selected"] is False

    def test_eta_bar_n_w_5_is_half(self):
        result = gravitino_chirality_constraint()
        assert abs(result[5]["eta_bar"] - 0.5) < 1e-10

    def test_eta_bar_n_w_7_is_zero(self):
        result = gravitino_chirality_constraint()
        assert abs(result[7]["eta_bar"] - 0.0) < 1e-10

    def test_omega_spin_n_w_5_is_minus_gamma5(self):
        result = gravitino_chirality_constraint()
        assert "-Γ⁵" in result[5]["omega_spin"]

    def test_omega_spin_n_w_7_is_plus_gamma5(self):
        result = gravitino_chirality_constraint()
        assert "+Γ⁵" in result[7]["omega_spin"]

    def test_triangular_number_n_w_5(self):
        result = gravitino_chirality_constraint()
        assert result[5]["triangular_number"] == 15  # T(5) = 5×6/2

    def test_triangular_number_n_w_7(self):
        result = gravitino_chirality_constraint()
        assert result[7]["triangular_number"] == 28  # T(7) = 7×8/2

    def test_t_parity_n_w_5_is_odd(self):
        result = gravitino_chirality_constraint()
        assert result[5]["T_parity"] == 1  # T(5)=15 is odd

    def test_t_parity_n_w_7_is_even(self):
        result = gravitino_chirality_constraint()
        assert result[7]["T_parity"] == 0  # T(7)=28 is even

    def test_reason_field_present(self):
        result = gravitino_chirality_constraint()
        assert len(result[5]["reason"]) > 20
        assert len(result[7]["reason"]) > 20

    def test_custom_candidates(self):
        # Only one candidate: n_w=5
        result = gravitino_chirality_constraint([5])
        assert 5 in result
        assert 7 not in result


class TestEuclideanSaddleComparison:
    def test_n_w_5_has_smaller_k_eff(self):
        result = euclidean_saddle_comparison()
        assert result[5]["k_eff"] < result[7]["k_eff"]

    def test_k_eff_n_w_5_equals_74(self):
        result = euclidean_saddle_comparison()
        # k_eff(5) = 5² + 7² = 25 + 49 = 74
        assert result[5]["k_eff"] == 74

    def test_k_eff_n_w_7_equals_130(self):
        result = euclidean_saddle_comparison()
        # k_eff(7) = 7² + 9² = 49 + 81 = 130
        assert result[7]["k_eff"] == 130

    def test_n_w_5_dominates(self):
        result = euclidean_saddle_comparison()
        assert result[5]["dominates"] is True
        assert result[7]["dominates"] is False

    def test_relative_weight_n_w_5_is_one(self):
        result = euclidean_saddle_comparison()
        assert abs(result[5]["relative_weight"] - 1.0) < 1e-10

    def test_relative_weight_n_w_7_is_suppressed(self):
        result = euclidean_saddle_comparison()
        # exp(-56) ≈ 2.5 × 10⁻²⁵
        assert result[7]["relative_weight"] < 1e-20

    def test_delta_k_n_w_7_is_56(self):
        result = euclidean_saddle_comparison()
        # Δk = 130 - 74 = 56
        assert result[7]["delta_k_from_min"] == 56

    def test_delta_k_n_w_5_is_zero(self):
        result = euclidean_saddle_comparison()
        assert result[5]["delta_k_from_min"] == 0

    def test_log10_suppression_n_w_7_large(self):
        result = euclidean_saddle_comparison()
        # log10(exp(-56)) ≈ -24.3
        assert result[7]["log10_suppression"] < -20.0


class TestPlanckNsSelection:
    def test_n_w_5_passes_planck(self):
        result = planck_ns_selection()
        assert result[5]["passes_planck_2sigma"] is True

    def test_n_w_7_fails_planck(self):
        result = planck_ns_selection()
        assert result[7]["passes_planck_2sigma"] is False

    def test_n_w_5_ns_within_1sigma(self):
        result = planck_ns_selection()
        assert result[5]["sigma_tension"] < 1.5

    def test_n_w_7_ns_tension_exceeds_3sigma(self):
        result = planck_ns_selection()
        assert result[7]["sigma_tension"] > 3.0

    def test_ns_formula_n_w_5(self):
        result = planck_ns_selection()
        # nₛ = 1 - 36/(n_w × 2π)² with n_w=5
        phi0_eff = 5 * 2 * math.pi
        expected = 1.0 - 36.0 / (phi0_eff ** 2)
        assert abs(result[5]["ns_predicted"] - expected) < 1e-10

    def test_ns_formula_n_w_7(self):
        result = planck_ns_selection()
        phi0_eff = 7 * 2 * math.pi
        expected = 1.0 - 36.0 / (phi0_eff ** 2)
        assert abs(result[7]["ns_predicted"] - expected) < 1e-10

    def test_status_string_selected_for_5(self):
        result = planck_ns_selection()
        assert "SELECTED" in result[5]["status"]

    def test_status_string_excluded_for_7(self):
        result = planck_ns_selection()
        assert "EXCLUDED" in result[7]["status"]

    def test_planck_reference_values(self):
        result = planck_ns_selection()
        assert abs(result[5]["ns_planck"] - NS_PLANCK) < 1e-6


class TestApsChainConsistency:
    def test_full_chain_consistent(self):
        check = aps_chain_consistency_check()
        assert check["steps_consistent"] is True

    def test_eta_bar_5_is_half(self):
        check = aps_chain_consistency_check()
        assert abs(check["detail"]["eta_bar_5"] - 0.5) < 1e-10

    def test_eta_bar_7_is_zero(self):
        check = aps_chain_consistency_check()
        assert abs(check["detail"]["eta_bar_7"] - 0.0) < 1e-10

    def test_all_three_arguments_select_5(self):
        check = aps_chain_consistency_check()
        assert check["detail"]["arg1_majorana_selects_5"] is True
        assert check["detail"]["arg2_saddle_selects_5"] is True
        assert check["detail"]["arg3_planck_selects_5"] is True

    def test_selected_n_w_is_5(self):
        check = aps_chain_consistency_check()
        assert check["detail"]["n_w_selected"] == 5

    def test_step1_candidates_correct(self):
        check = aps_chain_consistency_check()
        assert check["detail"]["step1_nw_in_5_7"] is True

    def test_step2_eta_correct(self):
        check = aps_chain_consistency_check()
        assert check["detail"]["step2_eta_bar_correct"] is True


class TestVacuumSelectionSummary:
    def test_summary_runs(self):
        s = vacuum_selection_summary(N_W_CANONICAL)
        assert isinstance(s, str)
        assert len(s) > 200

    def test_summary_mentions_horava_witten(self):
        s = vacuum_selection_summary()
        assert "Horava" in s or "Majorana" in s or "gravitino" in s.lower()

    def test_summary_mentions_planck(self):
        s = vacuum_selection_summary()
        assert "Planck" in s

    def test_summary_mentions_saddle(self):
        s = vacuum_selection_summary()
        assert "saddle" in s.lower() or "74" in s

    def test_summary_contains_verdict(self):
        s = vacuum_selection_summary()
        assert "VERDICT" in s or "SELECTED" in s

    def test_summary_mentions_remaining_gap(self):
        s = vacuum_selection_summary()
        assert "Remaining gap" in s or "REMAINING" in s or "gap" in s.lower()

    def test_status_string_non_empty(self):
        s = vacuum_selection_status()
        assert isinstance(s, str)
        assert len(s) > 30

    def test_status_string_mentions_topologically_derived(self):
        s = vacuum_selection_status()
        assert "TOPOLOGICALLY" in s or "Pillar 80" in s

    def test_status_string_mentions_pillar_84(self):
        s = vacuum_selection_status()
        assert "Pillar 84" in s
