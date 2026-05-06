# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 203 — Multi-KK Metric Feedback and QCD Scheme Audit."""

import math
import pytest

from src.core.pillar203_kk_metric_feedback import (
    N_W, K_CS, N_C,
    DELTA_B0_KK_SINGLE, DELTA_B0_KK_TOTAL, B0_EFF,
    LAMBDA_QCD_SW_MEV, LAMBDA_QCD_NF5_MS_MEV, LAMBDA_QCD_NF3_MS_MEV,
    SCHEME_RESIDUAL_PCT,
    kk_tower_beta_correction,
    kk_backreaction_on_mkk,
    qcd_scheme_audit,
    forward_chain_kk_corrected,
    axiom_zero_audit,
    pillar203_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_delta_b0_single(self):
        expected = (11.0 * 3 / 3.0) * (5.0 / 74.0)
        assert DELTA_B0_KK_SINGLE == pytest.approx(expected, rel=1e-5)

    def test_delta_b0_single_positive(self):
        assert DELTA_B0_KK_SINGLE > 0

    def test_delta_b0_total_larger_than_single(self):
        assert DELTA_B0_KK_TOTAL > DELTA_B0_KK_SINGLE

    def test_delta_b0_total_ratio(self):
        zeta2 = math.pi ** 2 / 6.0
        assert DELTA_B0_KK_TOTAL == pytest.approx(DELTA_B0_KK_SINGLE * zeta2, rel=1e-5)

    def test_b0_eff_larger_than_sm(self):
        b0_sm = (11.0 * 3 - 12.0) / 3.0  # = 7.0
        assert B0_EFF > b0_sm

    def test_lambda_sw_mev(self):
        assert 190 < LAMBDA_QCD_SW_MEV < 210

    def test_lambda_nf5_mev(self):
        assert 200 < LAMBDA_QCD_NF5_MS_MEV < 220

    def test_lambda_nf3_mev(self):
        assert 310 < LAMBDA_QCD_NF3_MS_MEV < 360

    def test_scheme_residual_below_10pct(self):
        assert SCHEME_RESIDUAL_PCT < 10.0

    def test_scheme_residual_approx_6pct(self):
        assert 4.0 < SCHEME_RESIDUAL_PCT < 8.0


class TestKkTowerBetaCorrection:
    def setup_method(self):
        self.result = kk_tower_beta_correction()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_b0_sm_is_7(self):
        assert self.result["b0_sm_nf6"] == pytest.approx(7.0)

    def test_delta_single_positive(self):
        assert self.result["delta_b0_kk_single"] > 0

    def test_delta_total_positive(self):
        assert self.result["delta_b0_kk_total"] > 0

    def test_total_larger_single(self):
        assert self.result["delta_b0_kk_total"] > self.result["delta_b0_kk_single"]

    def test_b0_eff_positive(self):
        assert self.result["b0_eff"] > 0

    def test_b0_eff_larger_b0_sm(self):
        assert self.result["b0_eff"] > self.result["b0_sm_nf6"]

    def test_no_zeta_resummation_equal_to_single(self):
        result_no_zeta = kk_tower_beta_correction(use_zeta_resummation=False)
        assert result_no_zeta["delta_b0_kk_total"] == pytest.approx(
            result_no_zeta["delta_b0_kk_single"], rel=1e-10
        )

    def test_correction_fraction_below_20pct(self):
        assert self.result["correction_pct_of_b0"] < 20.0

    def test_correction_fraction_above_10pct(self):
        assert self.result["correction_pct_of_b0"] > 10.0

    def test_method_string_zeta(self):
        assert "ζ(2)" in self.result["method"] or "zeta" in self.result["method"].lower()

    def test_method_string_no_zeta(self):
        result_no_z = kk_tower_beta_correction(use_zeta_resummation=False)
        assert "Pillar 200" in result_no_z["method"] or "n=1" in result_no_z["method"]


class TestKkBackreactionOnMkk:
    def setup_method(self):
        self.result = kk_backreaction_on_mkk()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_fractional_below_001(self):
        assert self.result["delta_mkk_fractional"] < 0.001

    def test_fractional_positive(self):
        assert self.result["delta_mkk_fractional"] > 0

    def test_pct_below_01(self):
        assert self.result["delta_mkk_pct"] < 0.1

    def test_status_negligible(self):
        assert "NEGLIGIBLE" in self.result["status"]

    def test_formula_present(self):
        assert "N_c" in self.result["formula"]

    def test_alpha_s_positive(self):
        assert self.result["alpha_s_mkk"] > 0


class TestQcdSchemeAudit:
    def setup_method(self):
        self.result = qcd_scheme_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_residual_vs_nf5_below_10(self):
        assert self.result["residual_vs_nf5_pct"] < 10.0

    def test_residual_vs_nf3_above_30(self):
        assert self.result["residual_vs_nf3_pct"] > 30.0

    def test_factor_vs_nf3_above_1(self):
        assert self.result["factor_vs_nf3"] > 1.5

    def test_correct_comparison_residual_below_10(self):
        assert self.result["correct_comparison"]["residual_pct"] < 10.0

    def test_incorrect_comparison_residual_above_30(self):
        assert self.result["incorrect_comparison"]["residual_pct"] > 30.0

    def test_scheme_resolution_mentions_convention(self):
        assert "SCHEME" in self.result["scheme_resolution"].upper()

    def test_p3_impact_remains_check(self):
        assert "CONSISTENCY CHECK" in self.result["p3_impact"]

    def test_um_value_correct(self):
        assert self.result["correct_comparison"]["um_value"] == pytest.approx(197.7, rel=0.01)

    def test_why_wrong_present(self):
        assert "why_wrong" in self.result["incorrect_comparison"]


class TestForwardChainKkCorrected:
    def setup_method(self):
        self.result = forward_chain_kk_corrected()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_b0_eff_larger_b0_sm(self):
        assert self.result["b0_eff"] > self.result["b0_sm"]

    def test_gap_change_small(self):
        # KK resummation changes the gap by < 2% (either direction)
        gap_change = abs(self.result["improvement_from_resummation_pct"])
        assert gap_change < 2.0

    def test_b0_eff_increases_with_resummation(self):
        # Larger β₀_eff from KK tower: denominator grows → α_s(M_EW) shifts
        assert self.result["b0_eff"] > self.result["b0_sm"]

    def test_gap_kk_still_above_3(self):
        # Gap should remain > 3 (still factor-3+ from PDG)
        assert self.result["warp_anchor_gap_kk"] > 3.0

    def test_alpha_s_kk_positive(self):
        assert self.result["alpha_s_kk_resummed"] > 0

    def test_verdict_present(self):
        assert "KK resummation" in self.result["verdict"]


class TestAxiomZeroAudit:
    def setup_method(self):
        self.result = axiom_zero_audit()

    def test_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_zero_sm_anchors(self):
        assert self.result["sm_anchors_count"] == 0

    def test_three_inputs(self):
        assert len(self.result["derivation_inputs"]) == 3

    def test_lambda_in_comparison_only(self):
        comp = " ".join(self.result["quantities_used_for_comparison_only"])
        assert "210" in comp or "nf=5" in comp


class TestPillar203Summary:
    def setup_method(self):
        self.result = pillar203_summary()

    def test_pillar_tag(self):
        assert self.result["pillar"] == "203"

    def test_version(self):
        assert "v10" in self.result["version"]

    def test_key_finding(self):
        assert "SCHEME" in self.result["key_finding"].upper()

    def test_toe_impact_p3_check(self):
        assert "CONSISTENCY CHECK" in self.result["toe_impact"]

    def test_status(self):
        assert "SCHEME AUDIT" in self.result["status"]

    def test_part_a_present(self):
        assert "part_a_kk_resummation" in self.result

    def test_part_b_present(self):
        assert "part_b_scheme_audit" in self.result
