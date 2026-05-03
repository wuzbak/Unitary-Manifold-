# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_holonomy_orbifold.py
================================
Test suite for Pillar 120 — Holonomy-Orbifold Equivalence.

~50 tests verifying correctness and internal consistency of every public
function in src/core/holonomy_orbifold.py.
"""

from __future__ import annotations

import pytest

from src.core.holonomy_orbifold import (
    E2_HOLONOMY_DEG,
    H0_EV,
    K_CS,
    M_PLANCK_EV,
    N_S,
    R_BRAIDED,
    S1_Z2_ANGLE_DEG,
    SCALE_RATIO,
    WINDING_NUMBER,
    e2_holonomy_angle,
    equivalence_theorem,
    formal_proof_steps,
    low_energy_limit_proof,
    s1_z2_boundary_condition,
    scale_hierarchy_ratio,
)


# ---------------------------------------------------------------------------
# TestS1Z2BoundaryCondition (10 tests)
# ---------------------------------------------------------------------------

class TestS1Z2BoundaryCondition:
    def test_returns_dict(self):
        assert isinstance(s1_z2_boundary_condition(), dict)

    def test_manifold_key(self):
        assert s1_z2_boundary_condition()["manifold"] == "S¹/Z₂"

    def test_group_z2(self):
        assert s1_z2_boundary_condition()["group"] == "Z₂"

    def test_identification_angle_deg(self):
        assert s1_z2_boundary_condition()["identification_angle_deg"] == pytest.approx(180.0)

    def test_bc_formula_contains_phi(self):
        bc = s1_z2_boundary_condition()["bc_formula"]
        assert "φ" in bc

    def test_orbifold_fixed_points_is_list(self):
        fps = s1_z2_boundary_condition()["orbifold_fixed_points"]
        assert isinstance(fps, list)

    def test_orbifold_fixed_points_two_elements(self):
        fps = s1_z2_boundary_condition()["orbifold_fixed_points"]
        assert len(fps) == 2

    def test_zero_mode_parity_minus_one(self):
        assert s1_z2_boundary_condition()["zero_mode_parity"] == -1

    def test_kk_mode_spectrum_non_empty(self):
        spec = s1_z2_boundary_condition()["kk_mode_spectrum"]
        assert isinstance(spec, str) and len(spec) > 0

    def test_identification_angle_matches_constant(self):
        assert s1_z2_boundary_condition()["identification_angle_deg"] == pytest.approx(
            S1_Z2_ANGLE_DEG
        )

    def test_epistemic_status_non_empty(self):
        es = s1_z2_boundary_condition()["epistemic_status"]
        assert isinstance(es, str) and len(es) > 0


# ---------------------------------------------------------------------------
# TestE2HolonomyAngle (5 tests)
# ---------------------------------------------------------------------------

class TestE2HolonomyAngle:
    def test_returns_float(self):
        assert isinstance(e2_holonomy_angle(), float)

    def test_equals_180(self):
        assert e2_holonomy_angle() == pytest.approx(180.0)

    def test_equals_e2_holonomy_deg_constant(self):
        assert e2_holonomy_angle() == pytest.approx(E2_HOLONOMY_DEG)

    def test_equals_s1_z2_angle_deg(self):
        assert e2_holonomy_angle() == pytest.approx(S1_Z2_ANGLE_DEG)

    def test_type_is_float(self):
        assert type(e2_holonomy_angle()) is float


# ---------------------------------------------------------------------------
# TestLowEnergyLimitProof (10 tests)
# ---------------------------------------------------------------------------

class TestLowEnergyLimitProof:
    def test_returns_list(self):
        assert isinstance(low_energy_limit_proof(), list)

    def test_at_least_six_steps(self):
        assert len(low_energy_limit_proof()) >= 6

    def test_each_step_has_step_key(self):
        for entry in low_energy_limit_proof():
            assert "step" in entry

    def test_each_step_has_title_key(self):
        for entry in low_energy_limit_proof():
            assert "title" in entry

    def test_each_step_has_statement_key(self):
        for entry in low_energy_limit_proof():
            assert "statement" in entry

    def test_steps_numbered_sequentially_from_one(self):
        steps = [e["step"] for e in low_energy_limit_proof()]
        assert steps == list(range(1, len(steps) + 1))

    def test_all_titles_non_empty(self):
        for entry in low_energy_limit_proof():
            assert len(entry["title"]) > 0

    def test_all_statements_non_empty(self):
        for entry in low_energy_limit_proof():
            assert len(entry["statement"]) > 0

    def test_step_one_mentions_boundary_or_orbifold(self):
        step1 = low_energy_limit_proof()[0]["statement"]
        assert "S¹/Z₂" in step1 or "boundary" in step1

    def test_last_step_mentions_correction_or_suppression_or_eft(self):
        last = low_energy_limit_proof()[-1]["statement"].lower()
        assert any(word in last for word in ("correction", "suppression", "eft"))


# ---------------------------------------------------------------------------
# TestEquivalenceTheorem (12 tests)
# ---------------------------------------------------------------------------

class TestEquivalenceTheorem:
    def test_returns_dict(self):
        assert isinstance(equivalence_theorem(), dict)

    def test_pillar_is_120(self):
        assert equivalence_theorem()["pillar"] == 120

    def test_microscopic_bc_180(self):
        assert equivalence_theorem()["microscopic_bc"] == pytest.approx(180.0)

    def test_macroscopic_holonomy_180(self):
        assert equivalence_theorem()["macroscopic_holonomy"] == pytest.approx(180.0)

    def test_angle_agreement_is_true(self):
        assert equivalence_theorem()["angle_agreement"] is True

    def test_angle_agreement_is_bool(self):
        assert type(equivalence_theorem()["angle_agreement"]) is bool

    def test_suppression_factor_less_than_1e_60(self):
        assert equivalence_theorem()["suppression_factor"] < 1e-60

    def test_suppression_factor_positive(self):
        assert equivalence_theorem()["suppression_factor"] > 0

    def test_scale_ratio_greater_than_1e60(self):
        assert equivalence_theorem()["scale_ratio"] > 1e60

    def test_conclusion_non_empty(self):
        conclusion = equivalence_theorem()["conclusion"]
        assert isinstance(conclusion, str) and len(conclusion) > 0

    def test_epistemic_status_non_empty(self):
        es = equivalence_theorem()["epistemic_status"]
        assert isinstance(es, str) and len(es) > 0

    def test_theorem_non_empty(self):
        thm = equivalence_theorem()["theorem"]
        assert isinstance(thm, str) and len(thm) > 0


# ---------------------------------------------------------------------------
# TestScaleHierarchyRatio (5 tests)
# ---------------------------------------------------------------------------

class TestScaleHierarchyRatio:
    def test_returns_float(self):
        assert isinstance(scale_hierarchy_ratio(), float)

    def test_greater_than_1e60(self):
        assert scale_hierarchy_ratio() > 1e60

    def test_less_than_1e62(self):
        assert scale_hierarchy_ratio() < 1e62

    def test_equals_scale_ratio_constant(self):
        assert scale_hierarchy_ratio() == pytest.approx(SCALE_RATIO)

    def test_consistent_with_m_planck_over_h0(self):
        expected = M_PLANCK_EV / H0_EV
        assert scale_hierarchy_ratio() == pytest.approx(expected, rel=1e-9)


# ---------------------------------------------------------------------------
# TestFormalProofSteps (8 tests)
# ---------------------------------------------------------------------------

class TestFormalProofSteps:
    def test_returns_list(self):
        assert isinstance(formal_proof_steps(), list)

    def test_at_least_six_steps(self):
        assert len(formal_proof_steps()) >= 6

    def test_each_step_has_step_key(self):
        for entry in formal_proof_steps():
            assert "step" in entry

    def test_each_step_has_title_key(self):
        for entry in formal_proof_steps():
            assert "title" in entry

    def test_each_step_has_statement_key(self):
        for entry in formal_proof_steps():
            assert "statement" in entry

    def test_each_step_has_citation_key(self):
        for entry in formal_proof_steps():
            assert "citation" in entry

    def test_all_citations_non_empty_strings(self):
        for entry in formal_proof_steps():
            assert isinstance(entry["citation"], str) and len(entry["citation"]) > 0

    def test_same_length_as_low_energy_proof(self):
        assert len(formal_proof_steps()) == len(low_energy_limit_proof())

    def test_steps_sequential_from_one(self):
        steps = [e["step"] for e in formal_proof_steps()]
        assert steps == list(range(1, len(steps) + 1))

    def test_all_titles_non_empty(self):
        for entry in formal_proof_steps():
            assert len(entry["title"]) > 0
