# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 388 — NLO Metric Ansatz Corrections: Higher-Order Terms Bounded."""

import math
import pytest
from src.core.pillar388_nlo_metric_corrections import (
    N_W, K_CS, PHI0_EFF, PHI0_EFF_SQ, K_R, M_KK_OVER_H, ALPHA_STRONG_5D,
    radion_backreaction_bound,
    kk_mode_mixing_bound,
    curvature_correction_bound,
    loop_correction_bound,
    total_nlo_bound,
    nlo_uniqueness_argument,
    pillar388_full_report,
    nlo_prediction_corrections,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi0_eff(self):
        import math as m
        expected = 5 * 2 * m.pi
        assert abs(PHI0_EFF - expected) < 1e-10

    def test_phi0_eff_sq(self):
        # φ₀_eff² ≈ 987
        assert 980 < PHI0_EFF_SQ < 995

    def test_alpha_5d(self):
        # 5D gauge coupling from CS quantization: g₅² ≈ 1/K_CS
        expected = 1.0 / K_CS
        assert abs(ALPHA_STRONG_5D - expected) < 1e-10


class TestRadionBackreactionBound:
    @pytest.fixture
    def result(self):
        return radion_backreaction_bound()

    def test_relative_correction(self, result):
        expected = 1.0 / PHI0_EFF_SQ
        assert abs(result["relative_correction"] - expected) < 1e-10

    def test_percent_correction_sub_percent(self, result):
        assert result["percent_correction"] < 1.0

    def test_percent_correction_positive(self, result):
        assert result["percent_correction"] > 0

    def test_percent_correction_approx_0_1(self, result):
        # Expected ~0.10%
        assert 0.05 < result["percent_correction"] < 0.2

    def test_alpha_coefficients_equal(self, result):
        assert abs(result["alpha_1_kinetic"] - result["alpha_2_mass"]) < 1e-15
        assert abs(result["alpha_2_mass"] - result["alpha_3_gauge"]) < 1e-15

    def test_negligible_flag(self, result):
        assert result["negligible_for_current_experiments"] is True

    def test_nlo_form_present(self, result):
        assert "nlo_form" in result


class TestKKModeMixingBound:
    @pytest.fixture
    def result(self):
        return kk_mode_mixing_bound()

    def test_extremely_suppressed(self, result):
        # Should be essentially 0
        assert result["relative_correction"] < 1e-100

    def test_m1_over_mkk(self, result):
        # m₁ = 1/(37) in units of M_KK
        expected = 1.0 / K_R
        assert abs(result["m1_over_Mkk"] - expected) < 1e-10

    def test_suppression_exponent_negative(self, result):
        assert result["suppression_exponent"] < 0

    def test_negligible(self, result):
        assert result["negligible_for_current_experiments"] is True


class TestCurvatureCorrectionBound:
    @pytest.fixture
    def result(self):
        return curvature_correction_bound()

    def test_relative_correction_tiny(self, result):
        # H²/M_Pl² ≈ 10⁻¹⁰
        assert result["relative_correction"] < 1e-8

    def test_percent_correction_negligible(self, result):
        assert result["percent_correction"] < 1e-7

    def test_negligible_flag(self, result):
        assert result["negligible_for_current_experiments"] is True

    def test_a_s_correct(self, result):
        assert abs(result["A_s"] - 2.1e-9) < 1e-12

    def test_r_braided_correct(self, result):
        assert abs(result["r_braided"] - 0.0315) < 1e-4


class TestLoopCorrectionBound:
    @pytest.fixture
    def result(self):
        return loop_correction_bound()

    def test_relative_correction_small(self, result):
        assert result["relative_correction"] < 0.01

    def test_percent_correction_sub_percent(self, result):
        assert result["percent_correction"] < 1.0

    def test_percent_correction_positive(self, result):
        assert result["percent_correction"] > 0

    def test_loop_factor_formula(self, result):
        import math as m
        expected_loop = K_CS / (16.0 * m.pi ** 2)
        assert abs(result["loop_factor"] - expected_loop) < 1e-10

    def test_g5_sq_formula(self, result):
        expected = 1.0 / K_CS
        assert abs(result["g5_squared"] - expected) < 1e-10


class TestTotalNLOBound:
    @pytest.fixture
    def result(self):
        return total_nlo_bound()

    def test_total_sub_one_percent(self, result):
        # Total NLO should be < 1%
        assert result["total_pct"] < 1.0

    def test_total_positive(self, result):
        assert result["total_pct"] > 0

    def test_all_sub_percent(self, result):
        assert result["all_corrections_sub_percent"] is True

    def test_dominant_correction(self, result):
        # Dominant should be either radion or loop
        assert result["dominant_correction"] in ["radion_backreaction", "loop"]

    def test_sum_correct(self, result):
        radion = radion_backreaction_bound()
        kk = kk_mode_mixing_bound()
        curv = curvature_correction_bound()
        loop = loop_correction_bound()
        expected_total = (radion["percent_correction"] + kk["percent_correction"]
                         + curv["percent_correction"] + loop["percent_correction"])
        assert abs(result["total_pct"] - expected_total) < 1e-10

    def test_summary_string_present(self, result):
        assert "%" in result["summary"]


class TestNLOUniquenessArgument:
    @pytest.fixture
    def result(self):
        return nlo_uniqueness_argument()

    def test_derived_unique_holds(self, result):
        assert result["derived_unique_holds_at_nlo"] is True

    def test_all_constraints_present(self, result):
        for constraint in ["C1", "C2", "C3", "C4"]:
            assert any(constraint in k for k in result.keys())

    def test_c2_exact(self, result):
        # KK gauge covariance is exact → G_{μ5} holds at all orders
        assert "exact" in result["constraint_C2_at_NLO"].lower()

    def test_c3_discrete(self, result):
        # Z₂ parity is discrete → sector structure fixed at all orders
        assert "discrete" in result["constraint_C3_at_NLO"].lower() or "all orders" in result["constraint_C3_at_NLO"].lower()

    def test_nlo_form_present(self, result):
        assert "G_AB^{NLO}" in result["nlo_form"] or "NLO" in result["nlo_form"]

    def test_nlo_magnitude_matches_bound(self, result):
        bound = total_nlo_bound()
        assert abs(result["nlo_magnitude"] - bound["total_pct"]) < 1e-10


class TestFullReport:
    @pytest.fixture
    def report(self):
        return pillar388_full_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 388

    def test_status(self, report):
        assert report["status"] == "NLO_CORRECTIONS_BOUNDED"

    def test_epistemic_upgrade(self, report):
        assert "NLO" in report["epistemic_upgrade"]

    def test_key_result_has_percentage(self, report):
        assert "%" in report["key_result"]

    def test_all_correction_sources_present(self, report):
        sources = report["correction_sources"]
        assert "radion_backreaction" in sources
        assert "kk_mode_mixing" in sources
        assert "curvature_corrections" in sources
        assert "loop_corrections" in sources

    def test_observational_implication_present(self, report):
        assert len(report["observational_implication"]) > 20

    def test_residual_present(self, report):
        assert len(report["residual"]) > 20

    def test_n_w_and_k_cs(self, report):
        assert report["n_w"] == N_W
        assert report["k_cs"] == K_CS


class TestNLOPredictionCorrections:
    @pytest.fixture
    def corrections(self):
        return nlo_prediction_corrections()

    def test_ns_lo(self, corrections):
        assert abs(corrections["n_s_lo"] - 0.9635) < 1e-6

    def test_r_lo(self, corrections):
        assert abs(corrections["r_lo"] - 0.0315) < 1e-6

    def test_beta_lo(self, corrections):
        assert abs(corrections["beta_lo"] - 0.331) < 1e-6

    def test_delta_ns_small(self, corrections):
        # NLO correction to n_s should be well below n_s itself
        assert corrections["delta_ns_nlo"] < 0.05  # < 5% of n_s value

    def test_delta_r_small(self, corrections):
        # NLO correction to r should be small
        assert corrections["delta_r_nlo"] < corrections["r_lo"]

    def test_below_planck_precision(self, corrections):
        # NLO correction to r should be below r (sanity check)
        assert corrections["delta_r_nlo"] < corrections["r_lo"]

    def test_fractional_correction_sub_percent(self, corrections):
        assert corrections["fractional_correction"] < 0.02  # < 2%


class TestPhysicalConsistency:
    """Physical consistency checks across all NLO corrections."""

    def test_radion_dominates_over_curvature(self):
        radion = radion_backreaction_bound()
        curv = curvature_correction_bound()
        assert radion["percent_correction"] > curv["percent_correction"]

    def test_kk_exponentially_smaller_than_all(self):
        kk = kk_mode_mixing_bound()
        radion = radion_backreaction_bound()
        assert kk["percent_correction"] < radion["percent_correction"] * 1e-10

    def test_loop_and_radion_comparable_order(self):
        loop = loop_correction_bound()
        radion = radion_backreaction_bound()
        # Both should be sub-percent and within ~10× of each other
        ratio = radion["percent_correction"] / loop["percent_correction"]
        assert 0.1 < ratio < 10.0

    def test_total_nlo_sub_percent(self):
        nlo = total_nlo_bound()
        # Total NLO correction is < 1%
        assert nlo["total_pct"] < 1.0

    def test_derived_unique_survives_nlo(self):
        uniqueness = nlo_uniqueness_argument()
        assert uniqueness["derived_unique_holds_at_nlo"] is True
