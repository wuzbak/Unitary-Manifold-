# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar401_ftum_basin_geometric_bound.py
===================================================
Tests for Pillar 401 — FTUM Basin Geometric Bound.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar401_ftum_basin_geometric_bound import (
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    PHI_0_BRAIDED,
    KAPPA_CRITICAL,
    Z2_DOMAIN_HALF_PERIOD,
    LIPSCHITZ_BOUND,
    KAPPA_CANONICAL,
    orbifold_basin_radius,
    ftum_fixed_point_entropy,
    ftum_contractivity_in_orbifold,
    banach_fpt_conditions,
    ftum_basin_completeness_in_orbifold,
    admission_12_closure_verdict,
    pillar401_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 401

    def test_phi_0_braided(self):
        assert PHI_0_BRAIDED == pytest.approx(5.0 * math.pi / 74.0, rel=1e-10)

    def test_phi_0_order(self):
        assert 0.1 < PHI_0_BRAIDED < 0.5

    def test_kappa_critical(self):
        assert KAPPA_CRITICAL == pytest.approx(0.5, rel=1e-9)

    def test_z2_half_period(self):
        assert Z2_DOMAIN_HALF_PERIOD == pytest.approx(1.0, rel=1e-9)

    def test_lipschitz_bound(self):
        assert 0.0 < LIPSCHITZ_BOUND < 1.0  # contractivity

    def test_kappa_canonical(self):
        assert KAPPA_CANONICAL >= KAPPA_CRITICAL  # in physical regime

    def test_pillar_status(self):
        assert PILLAR_STATUS == "CONTRACTIVE_IN_ORBIFOLD_BASIN"


# ─────────────────────────────────────────────────────────────────────────────
# orbifold_basin_radius
# ─────────────────────────────────────────────────────────────────────────────

class TestOrbifoldBasinRadius:
    @pytest.fixture(scope="class")
    def result(self):
        return orbifold_basin_radius()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_s_star_positive(self, result):
        assert result["s_star_entropy"] > 0.0

    def test_eps_max_phi_units(self, result):
        assert result["eps_max_phi_units"] == pytest.approx(Z2_DOMAIN_HALF_PERIOD, rel=1e-9)

    def test_eps_max_entropy_equals_s_star(self, result):
        assert result["eps_max_entropy_units"] == pytest.approx(
            result["s_star_entropy"], rel=1e-9
        )

    def test_domain_coverage(self, result):
        assert result["domain_coverage_fraction"] == pytest.approx(1.0, rel=1e-9)

    def test_basin_non_trivial(self, result):
        assert result["basin_non_trivial"] is True

    def test_s_star_formula(self, result):
        """S* = φ₀ × √κ / (1+κ)."""
        kappa = result["kappa"]
        expected = PHI_0_BRAIDED * math.sqrt(kappa) / (1.0 + kappa)
        assert result["s_star_entropy"] == pytest.approx(expected, rel=1e-8)

    def test_orbifold_description(self, result):
        assert isinstance(result["orbifold_description"], str)

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)

    def test_raises_negative_kappa(self):
        with pytest.raises(ValueError):
            orbifold_basin_radius(kappa=-0.1)

    def test_s_star_at_kappa_1_is_max(self):
        """S* is maximized at κ = 1."""
        s1 = orbifold_basin_radius(kappa=1.0)["s_star_entropy"]
        s05 = orbifold_basin_radius(kappa=0.5)["s_star_entropy"]
        s2 = orbifold_basin_radius(kappa=2.0)["s_star_entropy"]
        assert s1 >= s05
        assert s1 >= s2

    def test_s_star_max_formula(self):
        """At κ=1: S* = φ₀/2."""
        s_at_1 = orbifold_basin_radius(kappa=1.0)["s_star_entropy"]
        assert s_at_1 == pytest.approx(PHI_0_BRAIDED / 2.0, rel=1e-8)


# ─────────────────────────────────────────────────────────────────────────────
# ftum_fixed_point_entropy
# ─────────────────────────────────────────────────────────────────────────────

class TestFtumFixedPointEntropy:
    def test_non_trivial_at_canonical(self):
        result = ftum_fixed_point_entropy()
        assert result["non_trivial"] is True

    def test_formula(self):
        result = ftum_fixed_point_entropy(0.8)
        expected = PHI_0_BRAIDED * math.sqrt(0.8) / (1.0 + 0.8)
        assert result["s_star"] == pytest.approx(expected, rel=1e-8)

    def test_max_at_kappa_1(self):
        result = ftum_fixed_point_entropy(1.0)
        assert result["s_star"] == pytest.approx(result["s_star_max_at_kappa_1"], rel=1e-8)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            ftum_fixed_point_entropy(-0.1)

    def test_normalised_s_star_at_max_is_1(self):
        result = ftum_fixed_point_entropy(1.0)
        assert result["normalised_s_star"] == pytest.approx(1.0, rel=1e-8)

    def test_normalised_s_star_less_than_1_otherwise(self):
        result = ftum_fixed_point_entropy(0.5)
        assert result["normalised_s_star"] <= 1.0 + 1e-10


# ─────────────────────────────────────────────────────────────────────────────
# ftum_contractivity_in_orbifold
# ─────────────────────────────────────────────────────────────────────────────

class TestFtumContractivity:
    def test_canonical_contractive(self):
        result = ftum_contractivity_in_orbifold()
        assert result["contractive"] is True

    def test_canonical_in_physical_regime(self):
        result = ftum_contractivity_in_orbifold()
        assert result["in_physical_regime"] is True

    def test_l_less_than_1(self):
        result = ftum_contractivity_in_orbifold()
        assert result["lipschitz_constant_L"] < 1.0

    def test_l_positive(self):
        result = ftum_contractivity_in_orbifold()
        assert result["lipschitz_constant_L"] > 0.0

    def test_below_critical_not_contractive(self):
        result = ftum_contractivity_in_orbifold(kappa=0.3)
        assert result["in_physical_regime"] is False
        assert result["contractive"] is False

    def test_exactly_at_critical_contractive(self):
        result = ftum_contractivity_in_orbifold(kappa=0.5)
        assert result["in_physical_regime"] is True
        assert result["contractive"] is True

    def test_verdict_string(self):
        result = ftum_contractivity_in_orbifold()
        assert isinstance(result["verdict"], str)
        assert "CONTRACTIVE" in result["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# banach_fpt_conditions
# ─────────────────────────────────────────────────────────────────────────────

class TestBanachFptConditions:
    @pytest.fixture(scope="class")
    def result(self):
        return banach_fpt_conditions()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_cond1_completeness(self, result):
        assert result["condition_1_completeness"]["satisfied"] is True

    def test_cond2_contractivity(self, result):
        assert result["condition_2_contractivity"]["satisfied"] is True

    def test_cond3_self_mapping(self, result):
        assert result["condition_3_self_mapping"]["satisfied"] is True

    def test_all_conditions_met(self, result):
        assert result["all_conditions_met"] is True

    def test_banach_fpt_applies(self, result):
        assert result["banach_fpt_applies"] is True

    def test_basin_radius_positive(self, result):
        assert result["basin_radius_entropy"] > 0.0

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert "APPLIES" in result["verdict"] or "ALL MET" in result["verdict"]

    def test_below_critical_banach_does_not_apply(self):
        result = banach_fpt_conditions(kappa=0.3)
        assert result["banach_fpt_applies"] is False

    def test_l_value(self, result):
        L = result["condition_2_contractivity"]["L"]
        assert 0.0 < L < 1.0


# ─────────────────────────────────────────────────────────────────────────────
# ftum_basin_completeness_in_orbifold
# ─────────────────────────────────────────────────────────────────────────────

class TestFtumBasinCompletenessInOrbifold:
    @pytest.fixture(scope="class")
    def result(self):
        return ftum_basin_completeness_in_orbifold(n_test_initial_conditions=25)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_n_test_ics(self, result):
        assert result["n_test_ics"] == 25

    def test_all_converge(self, result):
        assert result["all_initial_conditions_converge"] is True

    def test_convergence_fraction(self, result):
        assert result["convergence_fraction"] == pytest.approx(1.0, rel=1e-6)

    def test_n_converged_equals_n_ics(self, result):
        assert result["n_converged"] == result["n_test_ics"]

    def test_s_star_positive(self, result):
        assert result["s_star"] > 0.0

    def test_eps_max_positive(self, result):
        assert result["eps_max"] > 0.0

    def test_banach_fpt_applies(self, result):
        assert result["banach_fpt_applies"] is True

    def test_analytic_guarantee(self, result):
        assert result["analytic_guarantee"] is True

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert "CONVERGE" in result["verdict"]

    def test_lipschitz_l(self, result):
        assert 0.0 < result["lipschitz_L"] < 1.0

    def test_convergence_results_length(self, result):
        assert len(result["convergence_results"]) == 25

    def test_each_result_has_s0(self, result):
        for r in result["convergence_results"]:
            assert "s0" in r
            assert "converged" in r


# ─────────────────────────────────────────────────────────────────────────────
# Admission 12 verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission12Verdict:
    @pytest.fixture(scope="class")
    def verdict(self):
        return admission_12_closure_verdict()

    def test_returns_dict(self, verdict):
        assert isinstance(verdict, dict)

    def test_admission_number(self, verdict):
        assert verdict["admission"] == 12

    def test_previous_status(self, verdict):
        assert verdict["previous_status"] == "OPEN_GAP"

    def test_new_status(self, verdict):
        assert verdict["new_status"] == "CONTRACTIVE_IN_ORBIFOLD_BASIN"

    def test_banach_fpt_applies(self, verdict):
        assert verdict["banach_fpt_applies"] is True

    def test_eps_max_positive(self, verdict):
        assert verdict["eps_max"] > 0.0

    def test_s_star_positive(self, verdict):
        assert verdict["s_star"] > 0.0

    def test_domain_coverage(self, verdict):
        assert verdict["domain_coverage_fraction"] == pytest.approx(1.0, rel=1e-9)

    def test_all_test_ics_converge(self, verdict):
        assert verdict["all_test_ics_converge"] is True

    def test_honest_residual(self, verdict):
        assert isinstance(verdict["honest_residual"], str)
        assert "Z₂" in verdict["honest_residual"] or "Z_2" in verdict["honest_residual"] or "orbifold" in verdict["honest_residual"]

    def test_citation(self, verdict):
        assert "401" in verdict["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Pillar summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar401Summary:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar401_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_pillar_number(self, summary):
        assert summary["pillar_number"] == 401

    def test_status(self, summary):
        assert summary["status"] == "CONTRACTIVE_IN_ORBIFOLD_BASIN"

    def test_admission(self, summary):
        assert summary["admission"] == 12

    def test_banach_fpt_applies(self, summary):
        assert summary["banach_fpt_applies"] is True

    def test_all_conditions_met(self, summary):
        assert summary["all_conditions_met"] is True

    def test_all_test_ics_converge(self, summary):
        assert summary["all_test_ics_converge"] is True

    def test_s_star_positive(self, summary):
        assert summary["s_star"] > 0.0

    def test_key_result(self, summary):
        assert isinstance(summary["key_result"], str)
        assert "Banach" in summary["key_result"]

    def test_honest_residual(self, summary):
        assert isinstance(summary["honest_residual"], str)
        assert "OPEN" in summary["honest_residual"] or "open" in summary["honest_residual"].lower()
