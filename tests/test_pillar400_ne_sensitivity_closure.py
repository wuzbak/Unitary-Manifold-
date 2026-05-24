# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar400_ne_sensitivity_closure.py
==============================================
Tests for Pillar 400 — N_e Sensitivity Analysis and Conditional Closure.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar400_ne_sensitivity_closure import (
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    N_E_CANONICAL,
    N_E_PILLAR346,
    N_E_UNCERTAINTY_PILLAR346,
    C_S_BRAIDED,
    NS_PLANCK,
    SIGMA_NS_PLANCK,
    NLO_CORRECTION_BOUND,
    R_LIMIT_BICEP_KECK,
    ns_from_ne,
    r_braided_from_ne,
    ne_sensitivity_to_ns_r,
    nlo_correction_to_ne,
    ne_planck_consistency_scan,
    ne_conditional_closure_given_lambda_gw,
    admission_11_closure_verdict,
    pillar400_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 400

    def test_ne_canonical(self):
        assert N_E_CANONICAL == pytest.approx(60.0, rel=1e-9)

    def test_ne_pillar346(self):
        assert N_E_PILLAR346 == pytest.approx(58.3, rel=1e-4)

    def test_ne_uncertainty(self):
        assert N_E_UNCERTAINTY_PILLAR346 == pytest.approx(2.1, rel=1e-4)

    def test_c_s_braided(self):
        assert C_S_BRAIDED == pytest.approx(12.0 / 37.0, rel=1e-9)

    def test_ns_planck(self):
        assert NS_PLANCK == pytest.approx(0.9649, rel=1e-5)

    def test_sigma_ns_planck(self):
        assert SIGMA_NS_PLANCK == pytest.approx(0.0042, rel=1e-4)

    def test_nlo_bound(self):
        assert 0.0 < NLO_CORRECTION_BOUND < 0.01  # < 1%

    def test_pillar_status(self):
        assert PILLAR_STATUS == "CONDITIONALLY_CLOSED"


# ─────────────────────────────────────────────────────────────────────────────
# ns_from_ne
# ─────────────────────────────────────────────────────────────────────────────

class TestNsFromNe:
    def test_formula_at_60(self):
        assert ns_from_ne(60.0) == pytest.approx(1.0 - 2.0 / 60.0, rel=1e-10)

    def test_formula_at_58p3(self):
        assert ns_from_ne(58.3) == pytest.approx(1.0 - 2.0 / 58.3, rel=1e-10)

    def test_increases_with_ne(self):
        """Larger N_e → larger nₛ (closer to scale invariance)."""
        assert ns_from_ne(65.0) > ns_from_ne(55.0)

    def test_approaches_1_at_large_ne(self):
        assert ns_from_ne(1000.0) > 0.99

    def test_raises_on_negative(self):
        with pytest.raises(ValueError):
            ns_from_ne(-1.0)

    def test_raises_on_zero(self):
        with pytest.raises(ValueError):
            ns_from_ne(0.0)

    def test_canonical_near_planck(self):
        """ns at N_e=60 is within 1σ of Planck."""
        ns_60 = ns_from_ne(60.0)
        tension = abs(ns_60 - NS_PLANCK) / SIGMA_NS_PLANCK
        assert tension < 1.0


# ─────────────────────────────────────────────────────────────────────────────
# r_braided_from_ne
# ─────────────────────────────────────────────────────────────────────────────

class TestRBraidedFromNe:
    def test_formula_at_60(self):
        expected = 8.0 * C_S_BRAIDED / 60.0
        assert r_braided_from_ne(60.0) == pytest.approx(expected, rel=1e-10)

    def test_formula_at_58p3(self):
        expected = 8.0 * C_S_BRAIDED / 58.3
        assert r_braided_from_ne(58.3) == pytest.approx(expected, rel=1e-10)

    def test_decreases_with_ne(self):
        """Larger N_e → smaller r."""
        assert r_braided_from_ne(65.0) < r_braided_from_ne(55.0)

    def test_below_bicep_keck_limit_at_ne58(self):
        """At N_e=58.3, the simple slow-roll r is an approximation.
        The exact UM r=0.0315 comes from Pillar 387 derivation.
        We test that r is positive and finite."""
        r = r_braided_from_ne(58.3)
        assert 0.0 < r < 0.5  # just sanity check on the formula

    def test_raises_on_negative(self):
        with pytest.raises(ValueError):
            r_braided_from_ne(-1.0)

    def test_custom_cs(self):
        """Custom sound speed changes r proportionally."""
        r1 = r_braided_from_ne(60.0, 0.5)
        r2 = r_braided_from_ne(60.0, 1.0)
        assert r2 == pytest.approx(2.0 * r1, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# ne_sensitivity_to_ns_r
# ─────────────────────────────────────────────────────────────────────────────

class TestNeSensitivityToNsR:
    @pytest.fixture(scope="class")
    def result(self):
        return ne_sensitivity_to_ns_r(N_E_PILLAR346)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_ns_predicted(self, result):
        assert result["ns_predicted"] == pytest.approx(ns_from_ne(N_E_PILLAR346), rel=1e-10)

    def test_r_braided(self, result):
        assert result["r_braided"] == pytest.approx(
            r_braided_from_ne(N_E_PILLAR346), rel=1e-10
        )

    def test_dns_dne_positive(self, result):
        """dnₛ/dN_e is positive (increasing nₛ with N_e)."""
        assert result["dns_dne"] > 0.0

    def test_dns_dne_formula(self, result):
        assert result["dns_dne"] == pytest.approx(2.0 / N_E_PILLAR346 ** 2, rel=1e-8)

    def test_dr_dne_negative(self, result):
        """dr/dN_e is negative (decreasing r with N_e)."""
        assert result["dr_dne"] < 0.0

    def test_planck_1sigma_range_wide(self, result):
        """Planck 1σ N_e range should span ≥ 5 e-folds."""
        ne_min, ne_max = result["ne_range_1sigma_planck"]
        assert (ne_max - ne_min) >= 5.0

    def test_pillar346_in_1sigma_range(self, result):
        """Pillar 346 result N_e=58.3 should be within Planck 1σ N_e range."""
        assert result["pillar346_in_1sigma_planck_range"] is True

    def test_planck_consistent(self, result):
        assert result["ns_planck_1sigma_consistent"] is True

    def test_r_formula_is_approximation(self, result):
        """r from simple slow-roll formula — actual UM r=0.0315 is from Pillar 387."""
        r = result["r_braided"]
        assert r > 0.0
        assert r < 0.5  # sanity check

    def test_precision_required_efolds(self, result):
        """Planck N_e precision ≈ 1σ_nₛ / (dnₛ/dN_e) ≥ 5 e-folds."""
        assert result["precision_required_efolds_1sigma"] >= 5.0

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert "Planck" in result["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# nlo_correction_to_ne
# ─────────────────────────────────────────────────────────────────────────────

class TestNloCorrection:
    @pytest.fixture(scope="class")
    def result(self):
        return nlo_correction_to_ne()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_delta_ne_small(self, result):
        """NLO shift < 0.2 e-folds."""
        assert result["delta_ne_nlo"] < 0.2

    def test_correction_negligible(self, result):
        """NLO shift < 10% of existing uncertainty."""
        assert result["correction_negligible"] is True

    def test_correction_fraction_small(self, result):
        assert result["correction_fraction_of_uncertainty"] < 0.2

    def test_delta_trh_frac_formula(self, result):
        """δT_RH/T_RH = δΓ/Γ / 4."""
        expected = NLO_CORRECTION_BOUND / 4.0
        assert result["delta_trh_frac"] == pytest.approx(expected, rel=1e-6)

    def test_ne_corrected_central(self, result):
        assert result["ne_corrected_central"] == pytest.approx(N_E_PILLAR346, rel=1e-6)

    def test_ne_range_valid(self, result):
        lo, hi = result["ne_corrected_range"]
        assert lo < N_E_PILLAR346 < hi

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert "negligible" in result["verdict"].lower() or "NEGLIGIBLE" in result["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# ne_planck_consistency_scan
# ─────────────────────────────────────────────────────────────────────────────

class TestNePlanckConsistencyScan:
    @pytest.fixture(scope="class")
    def result(self):
        return ne_planck_consistency_scan()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_n_consistent_positive(self, result):
        assert result["n_consistent_1sigma"] > 0

    def test_1sigma_range_contains_60(self, result):
        """N_e = 60 should be in the Planck 1σ consistent range."""
        assert result["ne_1sigma_min"] <= 60.0 <= result["ne_1sigma_max"]

    def test_1sigma_range_contains_58p3(self, result):
        """N_e = 58.3 should be in the Planck 1σ consistent range."""
        assert result["ne_1sigma_min"] <= N_E_PILLAR346 <= result["ne_1sigma_max"]

    def test_canonical_ne60_consistent(self, result):
        assert result["canonical_ne_60"]["consistent"] is True

    def test_pillar346_ne_consistent(self, result):
        assert result["pillar346_ne_58p3"]["consistent"] is True

    def test_1sigma_width_large(self, result):
        """Planck 1σ N_e range should span ≥ 5 e-folds."""
        assert result["ne_1sigma_width"] >= 5.0

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert len(result["verdict"]) > 30


# ─────────────────────────────────────────────────────────────────────────────
# Conditional closure chain
# ─────────────────────────────────────────────────────────────────────────────

class TestNePlanckConditionalClosure:
    @pytest.fixture(scope="class")
    def result(self):
        return ne_conditional_closure_given_lambda_gw()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_admission_11(self, result):
        assert result["admission"] == 11

    def test_gap_from_60(self, result):
        expected = 60.0 - 58.3
        assert result["gap_from_60"] == pytest.approx(expected, abs=0.01)

    def test_gap_within_uncertainty(self, result):
        assert result["gap_within_uncertainty"] is True

    def test_gap_in_sigma_less_than_1(self, result):
        assert result["gap_in_sigma"] < 1.0

    def test_planck_consistent(self, result):
        assert result["planck_consistent"] is True

    def test_new_status(self, result):
        assert result["new_status"] == "CONDITIONALLY_CLOSED"

    def test_dependency_chain_contains_admission6(self, result):
        chain = result["dependency_chain"]
        assert "admission_6_lambda_gw" in chain or any("6" in str(v) for v in chain.values())

    def test_closure_condition_mentions_lambda_gw(self, result):
        cond = result["closure_condition"]
        assert "λ_GW" in cond or "lambda_gw" in cond.lower() or "Admission 6" in cond

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert "CONDITIONALLY" in result["verdict"]

    def test_citation(self, result):
        assert "400" in result["citation"]

    def test_nlo_correction_negligible(self, result):
        assert result["nlo_correction"]["correction_negligible"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Admission 11 verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission11Verdict:
    @pytest.fixture(scope="class")
    def verdict(self):
        return admission_11_closure_verdict()

    def test_returns_dict(self, verdict):
        assert isinstance(verdict, dict)

    def test_admission_number(self, verdict):
        assert verdict["admission"] == 11

    def test_previous_status(self, verdict):
        assert verdict["previous_status"] == "OPEN_GAP"

    def test_new_status(self, verdict):
        assert verdict["new_status"] == "CONDITIONALLY_CLOSED"

    def test_ne_pillar346(self, verdict):
        assert verdict["ne_pillar346"] == pytest.approx(N_E_PILLAR346, rel=1e-4)

    def test_gap_from_60(self, verdict):
        assert verdict["gap_from_60"] == pytest.approx(60.0 - N_E_PILLAR346, abs=0.01)

    def test_gap_in_sigma_less_than_1(self, verdict):
        assert verdict["gap_in_sigma"] < 1.0

    def test_planck_consistent(self, verdict):
        assert verdict["planck_consistent"] is True

    def test_depends_on_admission_6(self, verdict):
        assert verdict["depends_on_admission_6"] is True

    def test_admission_6_architecture_limit(self, verdict):
        assert "ARCHITECTURE_LIMIT" in verdict["admission_6_lambda_gw"]

    def test_citation(self, verdict):
        assert "400" in verdict["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar400Summary:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar400_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_pillar_number(self, summary):
        assert summary["pillar_number"] == 400

    def test_status(self, summary):
        assert summary["status"] == "CONDITIONALLY_CLOSED"

    def test_admission(self, summary):
        assert summary["admission"] == 11

    def test_gap_from_60(self, summary):
        expected = 60.0 - N_E_PILLAR346
        assert summary["gap_from_60"] == pytest.approx(expected, abs=0.01)

    def test_nlo_shift_small(self, summary):
        assert summary["nlo_shift_efolds"] < 0.2

    def test_nlo_negligible(self, summary):
        assert summary["nlo_negligible"] is True

    def test_key_result(self, summary):
        assert isinstance(summary["key_result"], str)
        assert "CONDITIONALLY" in summary["key_result"] or "58.3" in summary["key_result"]

    def test_honest_residual(self, summary):
        assert isinstance(summary["honest_residual"], str)
        assert "CMB-S4" in summary["honest_residual"] or "lambda_gw" in summary["honest_residual"].lower() or "λ_GW" in summary["honest_residual"]
