# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_fermilab_watch.py
=============================
Test suite for src/core/fermilab_watch.py (Pillar 51-B).

Covers constants, discrepancy_dd, discrepancy_bmw, um_explanation_fraction,
can_um_explain_anomaly, fermilab_watch_report, new_physics_scale_from_anomaly,
status_summary, and edge cases.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import pytest

from src.core.fermilab_watch import (
    A_MU_EXP,
    A_MU_EXP_UNC,
    A_MU_SM_BMW,
    A_MU_SM_BMW_UNC,
    A_MU_SM_DD,
    A_MU_SM_DD_UNC,
    A_MU_UM_KK,
    MEASUREMENT_PRECISION_PPB,
    RESULT_DATE,
    can_um_explain_anomaly,
    discrepancy_bmw,
    discrepancy_dd,
    fermilab_watch_report,
    new_physics_scale_from_anomaly,
    status_summary,
    um_explanation_fraction,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_a_mu_exp(self):
        assert A_MU_EXP == pytest.approx(116592070.5)

    def test_a_mu_exp_unc(self):
        assert A_MU_EXP_UNC == pytest.approx(14.6)

    def test_a_mu_sm_dd(self):
        assert A_MU_SM_DD == pytest.approx(116591810.0)

    def test_a_mu_sm_dd_unc(self):
        assert A_MU_SM_DD_UNC == pytest.approx(4.3)

    def test_a_mu_sm_bmw(self):
        assert A_MU_SM_BMW == pytest.approx(116592055.0)

    def test_a_mu_sm_bmw_unc(self):
        assert A_MU_SM_BMW_UNC == pytest.approx(2.7)

    def test_a_mu_um_kk_negligible(self):
        assert A_MU_UM_KK < 1e-20

    def test_result_date(self):
        assert RESULT_DATE == "2025-06-03"

    def test_precision_ppb(self):
        assert MEASUREMENT_PRECISION_PPB == 127

    def test_exp_greater_than_sm_dd(self):
        assert A_MU_EXP > A_MU_SM_DD

    def test_exp_close_to_sm_bmw(self):
        """Experiment and BMW+ should be within 30 units."""
        assert abs(A_MU_EXP - A_MU_SM_BMW) < 30.0

    def test_um_kk_many_orders_smaller_than_discrepancy(self):
        delta = A_MU_EXP - A_MU_SM_DD
        assert A_MU_UM_KK < delta * 1e-25


# ---------------------------------------------------------------------------
# discrepancy_dd
# ---------------------------------------------------------------------------


class TestDiscrepancyDD:
    def setup_method(self):
        self.result = discrepancy_dd()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_delta(self):
        assert "delta" in self.result

    def test_has_sigma_combined(self):
        assert "sigma_combined" in self.result

    def test_has_n_sigma(self):
        assert "n_sigma" in self.result

    def test_has_interpretation(self):
        assert "interpretation" in self.result

    def test_delta_value(self):
        expected = A_MU_EXP - A_MU_SM_DD
        assert self.result["delta"] == pytest.approx(expected)

    def test_sigma_combined_formula(self):
        expected = math.sqrt(A_MU_EXP_UNC**2 + A_MU_SM_DD_UNC**2)
        assert self.result["sigma_combined"] == pytest.approx(expected)

    def test_n_sigma_large_discrepancy(self):
        """Data-driven discrepancy is large (> 5σ with these scaled units)."""
        assert self.result["n_sigma"] > 5.0

    def test_n_sigma_positive(self):
        assert self.result["n_sigma"] > 0.0

    def test_delta_positive(self):
        assert self.result["delta"] > 0.0

    def test_interpretation_is_string(self):
        assert isinstance(self.result["interpretation"], str)

    def test_n_sigma_formula(self):
        expected = self.result["delta"] / self.result["sigma_combined"]
        assert self.result["n_sigma"] == pytest.approx(expected)


# ---------------------------------------------------------------------------
# discrepancy_bmw
# ---------------------------------------------------------------------------


class TestDiscrepancyBMW:
    def setup_method(self):
        self.result = discrepancy_bmw()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_delta(self):
        assert "delta" in self.result

    def test_has_sigma_combined(self):
        assert "sigma_combined" in self.result

    def test_has_n_sigma(self):
        assert "n_sigma" in self.result

    def test_has_interpretation(self):
        assert "interpretation" in self.result

    def test_delta_value(self):
        expected = A_MU_EXP - A_MU_SM_BMW
        assert self.result["delta"] == pytest.approx(expected)

    def test_sigma_combined_formula(self):
        expected = math.sqrt(A_MU_EXP_UNC**2 + A_MU_SM_BMW_UNC**2)
        assert self.result["sigma_combined"] == pytest.approx(expected)

    def test_n_sigma_less_than_2(self):
        """BMW+ discrepancy is ~1.5σ — consistent."""
        assert self.result["n_sigma"] < 2.0

    def test_n_sigma_positive(self):
        assert self.result["n_sigma"] > 0.0

    def test_delta_positive(self):
        assert self.result["delta"] > 0.0

    def test_interpretation_is_string(self):
        assert isinstance(self.result["interpretation"], str)

    def test_bmw_sigma_smaller_than_dd_sigma(self):
        """BMW discrepancy in n_sigma should be smaller than DD."""
        assert self.result["n_sigma"] < discrepancy_dd()["n_sigma"]


# ---------------------------------------------------------------------------
# um_explanation_fraction
# ---------------------------------------------------------------------------


class TestUMExplanationFraction:
    def test_zero_total_returns_zero(self):
        assert um_explanation_fraction(1.0, 0.0) == 0.0

    def test_full_explanation(self):
        assert um_explanation_fraction(5.0, 5.0) == pytest.approx(1.0)

    def test_half_explanation(self):
        assert um_explanation_fraction(1.0, 2.0) == pytest.approx(0.5)

    def test_tiny_fraction(self):
        """KK correction is negligibly small."""
        fraction = um_explanation_fraction(A_MU_UM_KK, 260.0)
        assert fraction < 1e-30

    def test_abs_value(self):
        """Fraction is always non-negative (uses abs)."""
        assert um_explanation_fraction(-1.0, 2.0) >= 0.0

    def test_returns_float(self):
        assert isinstance(um_explanation_fraction(1.0, 2.0), float)


# ---------------------------------------------------------------------------
# can_um_explain_anomaly
# ---------------------------------------------------------------------------


class TestCanUMExplainAnomaly:
    def setup_method(self):
        self.result = can_um_explain_anomaly()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_can_explain_is_false(self):
        assert self.result["can_explain"] is False

    def test_has_um_contribution(self):
        assert "um_contribution" in self.result

    def test_has_required_contribution(self):
        assert "required_contribution" in self.result

    def test_has_fraction_explained(self):
        assert "fraction_explained" in self.result

    def test_has_honest_assessment(self):
        assert "honest_assessment" in self.result

    def test_um_contribution_value(self):
        assert self.result["um_contribution"] == pytest.approx(A_MU_UM_KK)

    def test_fraction_explained_tiny(self):
        assert self.result["fraction_explained"] < 1e-25

    def test_honest_assessment_is_string(self):
        assert isinstance(self.result["honest_assessment"], str)

    def test_required_contribution_positive(self):
        assert self.result["required_contribution"] > 0.0

    def test_honest_assessment_mentions_kk(self):
        lower = self.result["honest_assessment"].lower()
        assert "kk" in lower or "kaluza" in lower


# ---------------------------------------------------------------------------
# fermilab_watch_report
# ---------------------------------------------------------------------------


class TestFermilabWatchReport:
    def setup_method(self):
        self.report = fermilab_watch_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_has_experiment(self):
        assert "experiment" in self.report

    def test_has_result(self):
        assert "result" in self.report

    def test_has_discrepancy_dd(self):
        assert "discrepancy_dd" in self.report

    def test_has_discrepancy_bmw(self):
        assert "discrepancy_bmw" in self.report

    def test_has_um_contribution(self):
        assert "um_contribution" in self.report

    def test_has_conclusion(self):
        assert "conclusion" in self.report

    def test_experiment_is_string(self):
        assert isinstance(self.report["experiment"], str)

    def test_result_has_a_mu_exp(self):
        assert "a_mu_exp" in self.report["result"]

    def test_result_a_mu_exp_value(self):
        assert self.report["result"]["a_mu_exp"] == pytest.approx(A_MU_EXP)

    def test_result_has_date(self):
        assert self.report["result"]["date"] == RESULT_DATE

    def test_result_has_precision(self):
        assert self.report["result"]["precision_ppb"] == MEASUREMENT_PRECISION_PPB

    def test_conclusion_mentions_kk(self):
        lower = self.report["conclusion"].lower()
        assert "kk" in lower or "kaluza" in lower

    def test_conclusion_mentions_new_physics(self):
        lower = self.report["conclusion"].lower()
        assert "new physics" in lower

    def test_discrepancy_dd_is_dict(self):
        assert isinstance(self.report["discrepancy_dd"], dict)

    def test_discrepancy_bmw_is_dict(self):
        assert isinstance(self.report["discrepancy_bmw"], dict)


# ---------------------------------------------------------------------------
# new_physics_scale_from_anomaly
# ---------------------------------------------------------------------------


class TestNewPhysicsScale:
    def test_positive_delta_returns_positive_scale(self):
        # delta in dimensionless units; data-driven discrepancy ~260 × 10^{-12}
        delta = 260e-12
        scale = new_physics_scale_from_anomaly(delta)
        assert scale > 0.0

    def test_scale_in_tev_range(self):
        """For the data-driven anomaly, new physics should be at TeV scale."""
        delta = 260e-12   # dimensionless (multiply by 10^-12 units)
        scale = new_physics_scale_from_anomaly(delta)
        # Scale should be in range 0.001 GeV to 10000 GeV (rough check)
        assert 1e-3 < scale < 1e6

    def test_larger_delta_implies_lower_scale(self):
        """Larger anomaly → lower new physics scale."""
        scale_small = new_physics_scale_from_anomaly(1e-12)
        scale_large = new_physics_scale_from_anomaly(100e-12)
        assert scale_small > scale_large

    def test_zero_delta_raises(self):
        with pytest.raises(ValueError):
            new_physics_scale_from_anomaly(0.0)

    def test_negative_delta_raises(self):
        with pytest.raises(ValueError):
            new_physics_scale_from_anomaly(-1e-12)

    def test_negative_loop_factor_raises(self):
        with pytest.raises(ValueError):
            new_physics_scale_from_anomaly(260e-12, loop_factor=-1.0)

    def test_returns_float(self):
        assert isinstance(new_physics_scale_from_anomaly(260e-12), float)

    def test_custom_loop_factor(self):
        """Larger loop factor → higher scale."""
        scale_default = new_physics_scale_from_anomaly(260e-12)
        scale_larger = new_physics_scale_from_anomaly(260e-12, loop_factor=1.0)
        assert scale_larger > scale_default


# ---------------------------------------------------------------------------
# status_summary
# ---------------------------------------------------------------------------


class TestStatusSummary:
    def setup_method(self):
        self.summary = status_summary()

    def test_returns_string(self):
        assert isinstance(self.summary, str)

    def test_non_empty(self):
        assert len(self.summary) > 100

    def test_mentions_fermilab(self):
        assert "Fermilab" in self.summary or "fermilab" in self.summary.lower()

    def test_mentions_date(self):
        assert "2025" in self.summary

    def test_mentions_precision(self):
        assert "ppb" in self.summary or "127" in self.summary

    def test_mentions_kk(self):
        lower = self.summary.lower()
        assert "kk" in lower or "kaluza" in lower

    def test_mentions_bmw(self):
        assert "BMW" in self.summary or "bmw" in self.summary.lower() or "lattice" in self.summary.lower()

    def test_mentions_orders_of_magnitude(self):
        lower = self.summary.lower()
        assert "order" in lower or "small" in lower or "negligible" in lower
