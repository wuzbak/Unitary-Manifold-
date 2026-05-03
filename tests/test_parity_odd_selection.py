# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_parity_odd_selection.py
====================================
Tests for src/core/parity_odd_selection.py — Pillar 117:
Parity-Odd Selection Rules for the Unitary Manifold.

Physical claims under test
--------------------------
1. z2_parity_eigenvalues: even_l=+1, odd_l=-1, group="Z2", angle=180.
2. odd_l_power_deficit: 0.0 for even ell; positive, < 1, decreasing for odd;
   ValueError for ell < 1.
3. parity_selection_rules: >= 6 rules; each has required keys; sequential numbering.
4. orbifold_memory_proof: pillar=117; >= 5 steps; sequential numbering; non-empty strings.
5. low_multipole_anomaly_kernel: Gaussian peaked at ell=1 (returns 1.0); in (0,1];
   decreasing; ValueError for ell < 1.
6. um_alignment: all required keys; winding_number=5; cs_level=74; >= 3 observables.
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.core.parity_odd_selection import (
    z2_parity_eigenvalues,
    odd_l_power_deficit,
    parity_selection_rules,
    orbifold_memory_proof,
    low_multipole_anomaly_kernel,
    um_alignment,
    Z2_TWIST_ANGLE_DEG,
    N_W,
    K_CS,
    N_S,
    R_BRAIDED,
    BETA_DEG,
    PHI0_NATURAL,
)


# ---------------------------------------------------------------------------
# TestZ2ParityEigenvalues
# ---------------------------------------------------------------------------

class TestZ2ParityEigenvalues:
    def test_returns_dict(self):
        result = z2_parity_eigenvalues()
        assert isinstance(result, dict)

    def test_even_l_is_plus_one(self):
        result = z2_parity_eigenvalues()
        assert result["even_l"] == +1

    def test_odd_l_is_minus_one(self):
        result = z2_parity_eigenvalues()
        assert result["odd_l"] == -1

    def test_group_is_Z2(self):
        result = z2_parity_eigenvalues()
        assert result["group"] == "Z2"

    def test_generator_angle_is_180(self):
        result = z2_parity_eigenvalues()
        assert result["generator_angle_deg"] == pytest.approx(180.0)

    def test_action_is_string(self):
        result = z2_parity_eigenvalues()
        assert isinstance(result["action"], str)
        assert len(result["action"]) > 5

    def test_physical_effect_is_string(self):
        result = z2_parity_eigenvalues()
        assert isinstance(result["physical_effect"], str)
        assert len(result["physical_effect"]) > 10

    def test_physical_effect_mentions_odd(self):
        result = z2_parity_eigenvalues()
        assert "odd" in result["physical_effect"].lower() or "phase" in result["physical_effect"].lower()


# ---------------------------------------------------------------------------
# TestOddLPowerDeficit
# ---------------------------------------------------------------------------

class TestOddLPowerDeficit:
    def test_even_ell_2_returns_zero(self):
        assert odd_l_power_deficit(2) == pytest.approx(0.0)

    def test_even_ell_4_returns_zero(self):
        assert odd_l_power_deficit(4) == pytest.approx(0.0)

    def test_even_ell_6_returns_zero(self):
        assert odd_l_power_deficit(6) == pytest.approx(0.0)

    def test_odd_ell_1_positive(self):
        assert odd_l_power_deficit(1) > 0.0

    def test_odd_ell_3_positive(self):
        assert odd_l_power_deficit(3) > 0.0

    def test_odd_ell_5_positive(self):
        assert odd_l_power_deficit(5) > 0.0

    def test_odd_ell_7_positive(self):
        assert odd_l_power_deficit(7) > 0.0

    def test_odd_ell_9_positive(self):
        assert odd_l_power_deficit(9) > 0.0

    def test_deficit_strictly_less_than_one(self):
        for ell in [1, 3, 5, 7, 9, 11]:
            assert odd_l_power_deficit(ell) < 1.0

    def test_monotonically_decreasing_for_odd(self):
        d1 = odd_l_power_deficit(1)
        d9 = odd_l_power_deficit(9)
        assert d1 > d9

    def test_value_error_for_ell_zero(self):
        with pytest.raises(ValueError):
            odd_l_power_deficit(0)

    def test_value_error_for_negative_ell(self):
        with pytest.raises(ValueError):
            odd_l_power_deficit(-3)


# ---------------------------------------------------------------------------
# TestParitySelectionRules
# ---------------------------------------------------------------------------

class TestParitySelectionRules:
    def test_returns_list(self):
        rules = parity_selection_rules()
        assert isinstance(rules, list)

    def test_at_least_six_rules(self):
        rules = parity_selection_rules()
        assert len(rules) >= 6

    def test_each_has_rule_number(self):
        for rule in parity_selection_rules():
            assert "rule_number" in rule

    def test_each_has_description(self):
        for rule in parity_selection_rules():
            assert "description" in rule
            assert isinstance(rule["description"], str)
            assert len(rule["description"]) > 5

    def test_each_has_even_l_survives(self):
        for rule in parity_selection_rules():
            assert "even_l_survives" in rule

    def test_each_has_odd_l_survives(self):
        for rule in parity_selection_rules():
            assert "odd_l_survives" in rule

    def test_each_has_suppression_mechanism(self):
        for rule in parity_selection_rules():
            assert "suppression_mechanism" in rule
            assert isinstance(rule["suppression_mechanism"], str)

    def test_each_has_ell_range(self):
        for rule in parity_selection_rules():
            assert "ell_range" in rule
            assert isinstance(rule["ell_range"], str)

    def test_rule_numbers_sequential_from_one(self):
        rules = parity_selection_rules()
        for i, rule in enumerate(rules, start=1):
            assert rule["rule_number"] == i

    def test_even_and_odd_survives_are_bools(self):
        for rule in parity_selection_rules():
            assert isinstance(rule["even_l_survives"], bool)
            assert isinstance(rule["odd_l_survives"], bool)


# ---------------------------------------------------------------------------
# TestOrbifoldMemoryProof
# ---------------------------------------------------------------------------

class TestOrbifoldMemoryProof:
    def test_returns_dict(self):
        proof = orbifold_memory_proof()
        assert isinstance(proof, dict)

    def test_has_theorem_key(self):
        proof = orbifold_memory_proof()
        assert "theorem" in proof
        assert isinstance(proof["theorem"], str)
        assert len(proof["theorem"]) > 10

    def test_has_pillar_key(self):
        proof = orbifold_memory_proof()
        assert "pillar" in proof

    def test_pillar_is_117(self):
        proof = orbifold_memory_proof()
        assert proof["pillar"] == 117

    def test_has_steps_key(self):
        proof = orbifold_memory_proof()
        assert "steps" in proof

    def test_steps_is_list(self):
        proof = orbifold_memory_proof()
        assert isinstance(proof["steps"], list)

    def test_at_least_five_steps(self):
        proof = orbifold_memory_proof()
        assert len(proof["steps"]) >= 5

    def test_each_step_has_step_number(self):
        for step in orbifold_memory_proof()["steps"]:
            assert "step" in step

    def test_each_step_has_title(self):
        for step in orbifold_memory_proof()["steps"]:
            assert "title" in step
            assert isinstance(step["title"], str)
            assert len(step["title"]) > 5

    def test_each_step_has_statement(self):
        for step in orbifold_memory_proof()["steps"]:
            assert "statement" in step
            assert isinstance(step["statement"], str)
            assert len(step["statement"]) > 10

    def test_steps_sequential_from_one(self):
        steps = orbifold_memory_proof()["steps"]
        for i, step in enumerate(steps, start=1):
            assert step["step"] == i

    def test_conclusion_is_nonempty_string(self):
        proof = orbifold_memory_proof()
        assert "conclusion" in proof
        assert isinstance(proof["conclusion"], str)
        assert len(proof["conclusion"]) > 20

    def test_epistemic_status_is_nonempty_string(self):
        proof = orbifold_memory_proof()
        assert "epistemic_status" in proof
        assert isinstance(proof["epistemic_status"], str)
        assert len(proof["epistemic_status"]) > 5


# ---------------------------------------------------------------------------
# TestLowMultipoleAnomalyKernel
# ---------------------------------------------------------------------------

class TestLowMultipoleAnomalyKernel:
    def test_ell_1_returns_approx_one(self):
        assert low_multipole_anomaly_kernel(1) == pytest.approx(1.0, rel=1e-6)

    def test_returns_float(self):
        assert isinstance(low_multipole_anomaly_kernel(3), float)

    def test_in_range_0_to_1_for_ell_1_through_10(self):
        for ell in range(1, 11):
            k = low_multipole_anomaly_kernel(ell)
            assert 0.0 < k <= 1.0

    def test_kernel_1_ge_kernel_5(self):
        assert low_multipole_anomaly_kernel(1) >= low_multipole_anomaly_kernel(5)

    def test_kernel_5_ge_kernel_10(self):
        assert low_multipole_anomaly_kernel(5) >= low_multipole_anomaly_kernel(10)

    def test_kernel_1_ge_kernel_10(self):
        assert low_multipole_anomaly_kernel(1) >= low_multipole_anomaly_kernel(10)

    def test_value_error_for_ell_zero(self):
        with pytest.raises(ValueError):
            low_multipole_anomaly_kernel(0)

    def test_value_error_for_negative_ell(self):
        with pytest.raises(ValueError):
            low_multipole_anomaly_kernel(-1)


# ---------------------------------------------------------------------------
# TestUmAlignment
# ---------------------------------------------------------------------------

class TestUmAlignment:
    def test_returns_dict(self):
        result = um_alignment()
        assert isinstance(result, dict)

    def test_has_all_required_keys(self):
        result = um_alignment()
        required = [
            "pillar", "um_mechanism", "z2_source", "winding_number",
            "cs_level", "cmb_observables", "prediction", "falsification",
            "epistemic_status",
        ]
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_winding_number_is_five(self):
        result = um_alignment()
        assert result["winding_number"] == 5

    def test_cs_level_is_74(self):
        result = um_alignment()
        assert result["cs_level"] == 74

    def test_cmb_observables_is_list_of_at_least_three(self):
        result = um_alignment()
        assert isinstance(result["cmb_observables"], list)
        assert len(result["cmb_observables"]) >= 3
