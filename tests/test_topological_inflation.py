# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_topological_inflation.py
=====================================
Test suite for Pillar 121 — Topological Inflationary Backreaction.

Covers all six public-API functions of src/core/topological_inflation.py.
Target: ~55 tests, 0 failures.
"""

from __future__ import annotations

import math

import pytest

from src.core.topological_inflation import (
    EPSILON_BACKREACTION,
    H_INF,
    K_CS,
    M_PLANCK_GEV,
    N_S,
    N_W,
    OMEGA_K_OBSERVED,
    PHI_SLOW_ROLL,
    R_BRAIDED,
    backreaction_tension,
    flatness_preservation_proof,
    inflation_topology_coupling,
    scalar_field_effective_potential,
    twist_retention_mechanism,
    um_alignment,
)


# ---------------------------------------------------------------------------
# TestBackreactionTension  (12 tests)
# ---------------------------------------------------------------------------

class TestBackreactionTension:
    def test_returns_float(self):
        result = backreaction_tension(1.0)
        assert isinstance(result, float)

    def test_positive_for_l_over_chi_half(self):
        assert backreaction_tension(0.5) > 0.0

    def test_large_l_gives_small_tension(self):
        assert backreaction_tension(1000.0) < 1.0e-6

    def test_large_l_smaller_than_small_l(self):
        assert backreaction_tension(1000.0) < backreaction_tension(1.0)

    def test_monotonically_decreasing(self):
        values = [backreaction_tension(float(x)) for x in [0.1, 1.0, 10.0, 100.0]]
        for i in range(len(values) - 1):
            assert values[i] > values[i + 1]

    def test_value_error_for_negative_l(self):
        with pytest.raises(ValueError):
            backreaction_tension(-0.5)

    def test_l_zero_returns_epsilon_backreaction(self):
        assert backreaction_tension(0.0) == pytest.approx(EPSILON_BACKREACTION)

    def test_l_0_1_positive(self):
        assert backreaction_tension(0.1) > 0.0

    def test_l_1_0_positive(self):
        assert backreaction_tension(1.0) > 0.0

    def test_l_10_0_positive(self):
        assert backreaction_tension(10.0) > 0.0

    def test_max_value_at_most_epsilon_backreaction(self):
        assert backreaction_tension(0.0) <= EPSILON_BACKREACTION + 1.0e-15

    def test_l_1_formula(self):
        expected = EPSILON_BACKREACTION * (1.0 - math.exp(-1.0))
        assert backreaction_tension(1.0) == pytest.approx(expected, rel=1.0e-9)


# ---------------------------------------------------------------------------
# TestScalarFieldEffectivePotential  (10 tests)
# ---------------------------------------------------------------------------

class TestScalarFieldEffectivePotential:
    def test_returns_float(self):
        result = scalar_field_effective_potential(math.pi / 2, 1.0)
        assert isinstance(result, float)

    def test_phi_zero_returns_zero(self):
        assert scalar_field_effective_potential(0.0, 1.0) == pytest.approx(0.0, abs=1.0e-10)

    def test_nonneg_phi_pi_over_2(self):
        assert scalar_field_effective_potential(math.pi / 2, 1.0) >= 0.0

    def test_phi_pi_greater_than_phi_zero(self):
        assert scalar_field_effective_potential(math.pi, 1.0) > scalar_field_effective_potential(0.0, 1.0)

    def test_increasing_l_reduces_correction(self):
        v_small = scalar_field_effective_potential(math.pi / 4, 0.1)
        v_large = scalar_field_effective_potential(math.pi / 4, 100.0)
        assert v_large < v_small

    def test_value_error_for_negative_l(self):
        with pytest.raises(ValueError):
            scalar_field_effective_potential(1.0, -1.0)

    def test_phi_pi_over_4_l_1(self):
        result = scalar_field_effective_potential(math.pi / 4, 1.0)
        assert result > 0.0

    def test_phi_pi_over_3_l_2(self):
        result = scalar_field_effective_potential(math.pi / 3, 2.0)
        assert result > 0.0

    def test_v_eff_phi_zero_l_1_exactly_zero(self):
        assert scalar_field_effective_potential(0.0, 1.0) == pytest.approx(0.0, abs=1.0e-10)

    def test_large_l_approaches_bare_potential(self):
        phi = math.pi / 4
        v_0 = H_INF ** 2 * M_PLANCK_GEV ** 2 * (1.0 - math.cos(phi))
        v_eff_large_l = scalar_field_effective_potential(phi, 1.0e6)
        # For very large L, correction → 0; V_eff ≈ V_0
        assert abs(v_eff_large_l - v_0) / v_0 < 1.0e-4


# ---------------------------------------------------------------------------
# TestFlatnessPreservationProof  (12 tests)
# ---------------------------------------------------------------------------

class TestFlatnessPreservationProof:
    def setup_method(self):
        self.proof = flatness_preservation_proof()

    def test_returns_dict(self):
        assert isinstance(self.proof, dict)

    def test_pillar_is_121(self):
        assert self.proof["pillar"] == 121

    def test_omega_k_bound(self):
        assert self.proof["omega_k_bound"] == pytest.approx(OMEGA_K_OBSERVED)

    def test_backreaction_max(self):
        assert self.proof["backreaction_max"] == pytest.approx(EPSILON_BACKREACTION)

    def test_omega_k_from_backreaction_less_than_bound(self):
        assert self.proof["omega_k_from_backreaction"] < self.proof["omega_k_bound"]

    def test_flatness_preserved_is_true(self):
        assert self.proof["flatness_preserved"] is True

    def test_flatness_preserved_is_bool(self):
        assert type(self.proof["flatness_preserved"]) is bool

    def test_steps_is_list(self):
        assert isinstance(self.proof["steps"], list)

    def test_steps_at_least_five(self):
        assert len(self.proof["steps"]) >= 5

    def test_each_step_has_required_keys(self):
        for step in self.proof["steps"]:
            assert "step" in step
            assert "title" in step
            assert "statement" in step

    def test_conclusion_nonempty(self):
        assert isinstance(self.proof["conclusion"], str)
        assert len(self.proof["conclusion"]) > 0

    def test_epistemic_status_nonempty(self):
        assert isinstance(self.proof["epistemic_status"], str)
        assert len(self.proof["epistemic_status"]) > 0


# ---------------------------------------------------------------------------
# TestTwistRetentionMechanism  (10 tests)
# ---------------------------------------------------------------------------

class TestTwistRetentionMechanism:
    def setup_method(self):
        self.trm = twist_retention_mechanism()

    def test_returns_dict(self):
        assert isinstance(self.trm, dict)

    def test_pillar_is_121(self):
        assert self.trm["pillar"] == 121

    def test_superhorizon_modes_frozen_is_true(self):
        assert self.trm["superhorizon_modes_frozen"] is True

    def test_superhorizon_modes_frozen_is_bool(self):
        assert type(self.trm["superhorizon_modes_frozen"]) is bool

    def test_twist_survives_is_true(self):
        assert self.trm["twist_survives"] is True

    def test_twist_survives_is_bool(self):
        assert type(self.trm["twist_survives"]) is bool

    def test_explanation_steps_is_list(self):
        assert isinstance(self.trm["explanation_steps"], list)

    def test_explanation_steps_at_least_four(self):
        assert len(self.trm["explanation_steps"]) >= 4

    def test_each_explanation_step_has_required_keys(self):
        for step in self.trm["explanation_steps"]:
            assert "step" in step
            assert "title" in step
            assert "statement" in step

    def test_mechanism_nonempty_string(self):
        assert isinstance(self.trm["mechanism"], str)
        assert len(self.trm["mechanism"]) > 0

    def test_observational_consequence_nonempty_string(self):
        assert isinstance(self.trm["observational_consequence"], str)
        assert len(self.trm["observational_consequence"]) > 0

    def test_epistemic_status_nonempty_string(self):
        assert isinstance(self.trm["epistemic_status"], str)
        assert len(self.trm["epistemic_status"]) > 0


# ---------------------------------------------------------------------------
# TestInflationTopologyCoupling  (8 tests)
# ---------------------------------------------------------------------------

class TestInflationTopologyCoupling:
    def test_returns_dict_ell_1(self):
        assert isinstance(inflation_topology_coupling(1), dict)

    def test_returns_dict_ell_2(self):
        assert isinstance(inflation_topology_coupling(2), dict)

    def test_returns_dict_ell_10(self):
        assert isinstance(inflation_topology_coupling(10), dict)

    def test_has_all_required_keys(self):
        result = inflation_topology_coupling(5)
        for key in ("ell", "coupling_strength", "mode_frozen", "topology_imprint",
                    "scale_factor_at_exit", "physical_interpretation"):
            assert key in result

    def test_coupling_strength_positive(self):
        assert inflation_topology_coupling(3)["coupling_strength"] > 0.0

    def test_mode_frozen_is_true(self):
        assert inflation_topology_coupling(4)["mode_frozen"] is True

    def test_topology_imprint_is_true(self):
        assert inflation_topology_coupling(4)["topology_imprint"] is True

    def test_low_ell_stronger_coupling_than_high_ell(self):
        c_low = inflation_topology_coupling(1)["coupling_strength"]
        c_high = inflation_topology_coupling(10)["coupling_strength"]
        assert c_low > c_high

    def test_value_error_for_ell_zero(self):
        with pytest.raises(ValueError):
            inflation_topology_coupling(0)

    def test_value_error_for_ell_negative(self):
        with pytest.raises(ValueError):
            inflation_topology_coupling(-1)


# ---------------------------------------------------------------------------
# TestUmAlignment  (5 tests)
# ---------------------------------------------------------------------------

class TestUmAlignment:
    def setup_method(self):
        self.aln = um_alignment()

    def test_returns_dict(self):
        assert isinstance(self.aln, dict)

    def test_pillar_is_121(self):
        assert self.aln["pillar"] == 121

    def test_phi0_value_close_to_pi_over_4(self):
        assert self.aln["phi0_value"] == pytest.approx(math.pi / 4, rel=1.0e-3)

    def test_winding_number_is_5(self):
        assert self.aln["winding_number"] == 5

    def test_cs_level_is_74(self):
        assert self.aln["cs_level"] == 74

    def test_observable_consequences_at_least_three(self):
        assert isinstance(self.aln["observable_consequences"], list)
        assert len(self.aln["observable_consequences"]) >= 3
