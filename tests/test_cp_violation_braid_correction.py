# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for CP Violation Braid NLO Correction (Pillar 221, Track A Session 4)."""

import math
import pytest

from src.core.cp_violation_braid_correction import (
    N_W, K_CS, N_C,
    N1_BRAID, N2_BRAID,
    DELTA_CP_LEADING,
    DELTA_CP_NLO,
    DELTA_CP_TOTAL,
    DELTA_CP_PDG,
    JARLSKOG_PDG,
    JARLSKOG_BRAID,
    JARLSKOG_GAP_FRACTION,
    ARCHITECTURE_LIMIT,
    REQUIRES_DIMENSION,
    cp_phase_leading,
    cp_phase_nlo,
    cp_phase_total,
    ckm_mixing_angles_braid,
    jarlskog_braid,
    jarlskog_gap_analysis,
    cp_violation_braid_audit,
    pillar221_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n1_braid(self):
        assert N1_BRAID == 5

    def test_n2_braid(self):
        assert N2_BRAID == 7

    def test_braid_product_is_35(self):
        assert N1_BRAID * N2_BRAID == 35

    def test_braid_sum_squares_is_k_cs(self):
        assert N1_BRAID ** 2 + N2_BRAID ** 2 == K_CS

    def test_delta_cp_leading_negative(self):
        # n₂ > n₁ → negative leading phase
        assert DELTA_CP_LEADING < 0

    def test_delta_cp_nlo_positive(self):
        # NLO correction: π × n₁ × n₂ / (4 k_CS) > 0
        assert DELTA_CP_NLO > 0

    def test_delta_cp_leading_formula(self):
        expected = -math.pi * (N2_BRAID - N1_BRAID) / K_CS
        assert DELTA_CP_LEADING == pytest.approx(expected, rel=1e-10)

    def test_delta_cp_nlo_formula(self):
        expected = math.pi * N1_BRAID * N2_BRAID / (4.0 * K_CS)
        assert DELTA_CP_NLO == pytest.approx(expected, rel=1e-10)

    def test_delta_cp_total_is_sum(self):
        assert DELTA_CP_TOTAL == pytest.approx(DELTA_CP_LEADING + DELTA_CP_NLO, rel=1e-10)

    def test_jarlskog_braid_positive(self):
        assert JARLSKOG_BRAID > 0

    def test_jarlskog_gap_between_0_and_inf(self):
        assert JARLSKOG_GAP_FRACTION >= 0

    def test_architecture_limit_flag(self):
        assert ARCHITECTURE_LIMIT is True

    def test_requires_dimension_6(self):
        assert REQUIRES_DIMENSION == 6


class TestCPPhaseLeading:
    def test_returns_float(self):
        assert isinstance(cp_phase_leading(), float)

    def test_formula_correct(self):
        phase = cp_phase_leading(5, 7, 74)
        expected = -math.pi * 2 / 74
        assert phase == pytest.approx(expected)

    def test_zero_when_n1_equals_n2(self):
        phase = cp_phase_leading(5, 5, 74)
        assert phase == pytest.approx(0.0)


class TestCPPhaseNLO:
    def test_returns_float(self):
        assert isinstance(cp_phase_nlo(), float)

    def test_positive(self):
        assert cp_phase_nlo() > 0

    def test_formula_correct(self):
        phase = cp_phase_nlo(5, 7, 74)
        expected = math.pi * 35 / 296
        assert phase == pytest.approx(expected)


class TestCPPhaseTotal:
    def test_order_1_equals_leading(self):
        total = cp_phase_total(order=1)
        assert total == pytest.approx(DELTA_CP_LEADING, rel=1e-10)

    def test_order_2_equals_leading_plus_nlo(self):
        total = cp_phase_total(order=2)
        assert total == pytest.approx(DELTA_CP_LEADING + DELTA_CP_NLO, rel=1e-10)


class TestCKMMixingAnglesBraid:
    def test_returns_dict(self):
        result = ckm_mixing_angles_braid()
        assert isinstance(result, dict)

    def test_sin2_theta12_between_0_and_1(self):
        result = ckm_mixing_angles_braid()
        assert 0 < result["sin2_theta12_braid"] < 1

    def test_sin2_theta23_between_0_and_1(self):
        result = ckm_mixing_angles_braid()
        assert 0 < result["sin2_theta23_braid"] < 1

    def test_sin2_theta13_small(self):
        result = ckm_mixing_angles_braid()
        assert result["sin2_theta13_braid"] < 0.01   # small angle

    def test_has_sources(self):
        result = ckm_mixing_angles_braid()
        assert "sources" in result


class TestJarlskogBraid:
    def test_returns_float_and_dict(self):
        j, det = jarlskog_braid()
        assert isinstance(j, float)
        assert isinstance(det, dict)

    def test_j_positive(self):
        j, _ = jarlskog_braid()
        assert j > 0

    def test_j_nlo_has_gap_fraction(self):
        _, det = jarlskog_braid(order=2)
        assert "gap_fraction" in det


class TestJarlskogGapAnalysis:
    def test_returns_dict(self):
        result = jarlskog_gap_analysis()
        assert isinstance(result, dict)

    def test_has_nlo_corrected(self):
        result = jarlskog_gap_analysis()
        assert "nlo_corrected" in result

    def test_jarlskog_gap_is_documented(self):
        # The braid approximation has a large Jarlskog gap — this is documented
        result = jarlskog_gap_analysis()
        assert result["gap_fraction_nlo"] >= 0

    def test_architecture_limit_in_result(self):
        result = jarlskog_gap_analysis()
        assert result["architecture_limit"] is True

    def test_requires_dimension_6(self):
        result = jarlskog_gap_analysis()
        assert result["requires_dimension"] == 6


class TestCPViolationBraidAudit:
    def test_returns_dict(self):
        result = cp_violation_braid_audit()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = cp_violation_braid_audit()
        assert result["pillar"] == 221

    def test_axiom_zero_compliant(self):
        result = cp_violation_braid_audit()
        assert result["axiom_zero_compliant"] is True

    def test_honest_verdict_present(self):
        result = cp_violation_braid_audit()
        assert len(result["honest_verdict"]) > 50


class TestPillar221Summary:
    def test_returns_dict(self):
        s = pillar221_summary()
        assert isinstance(s, dict)

    def test_pillar_number(self):
        s = pillar221_summary()
        assert s["pillar"] == 221

    def test_architecture_limit_true(self):
        s = pillar221_summary()
        assert s["architecture_limit"] is True

    def test_requires_dimension_6(self):
        s = pillar221_summary()
        assert s["requires_dimension"] == 6

    def test_delta_cp_leading_present(self):
        s = pillar221_summary()
        assert "delta_cp_leading" in s

    def test_jarlskog_gap_fraction_positive(self):
        # The braid CP phase is an approximation; gap fraction can be large
        s = pillar221_summary()
        assert s["jarlskog_gap_fraction"] >= 0
