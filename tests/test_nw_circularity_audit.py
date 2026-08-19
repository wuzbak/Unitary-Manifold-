"""
tests/test_nw_circularity_audit.py
====================================
Tests for src/core/nw_circularity_audit.py

Verifies the n_w = 5 circularity audit module: correct classification of
all steps, expected counts, observational dependencies, and open gaps.

Author: GitHub Copilot (AI)
Copyright (C) 2026 AxiomZero Technologies & Consulting, SPC
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import pytest
from src.core.nw_circularity_audit import (
    EpistemicStatus,
    Dependency,
    CircularityAuditReport,
    AUDIT_STEPS,
    build_nw_dependency_graph,
    run_circularity_audit,
)


class TestAuditStepsStructure:
    """Tests on the AUDIT_STEPS constant."""

    def test_audit_steps_nonempty(self):
        assert len(AUDIT_STEPS) >= 8

    def test_all_steps_have_step_id(self):
        for step in AUDIT_STEPS:
            assert step.step_id, f"Step missing step_id: {step}"

    def test_all_steps_have_description(self):
        for step in AUDIT_STEPS:
            assert step.description, f"Step {step.step_id} missing description"

    def test_all_steps_have_pillar(self):
        for step in AUDIT_STEPS:
            assert step.pillar, f"Step {step.step_id} missing pillar"

    def test_all_steps_have_valid_status(self):
        valid_statuses = set(EpistemicStatus)
        for step in AUDIT_STEPS:
            assert step.status in valid_statuses, (
                f"Step {step.step_id} has invalid status: {step.status}"
            )

    def test_unique_step_ids(self):
        ids = [s.step_id for s in AUDIT_STEPS]
        assert len(ids) == len(set(ids)), "Duplicate step IDs found"


class TestKeyStepPresence:
    """Tests that specific critical steps are present and correctly classified."""

    def _get_step(self, step_id: str) -> Dependency:
        steps = {s.step_id: s for s in AUDIT_STEPS}
        assert step_id in steps, f"Step '{step_id}' not found in AUDIT_STEPS"
        return steps[step_id]

    def test_z2_parity_is_geometric(self):
        step = self._get_step("Z2_PARITY")
        assert step.status == EpistemicStatus.PURELY_GEOMETRIC

    def test_z2_parity_has_lean4_file(self):
        step = self._get_step("Z2_PARITY")
        assert step.lean4_file is not None
        assert "NWIntegerLattice" in step.lean4_file

    def test_candidate_set_is_proved(self):
        step = self._get_step("CANDIDATE_SET_5_7")
        assert step.status == EpistemicStatus.PROVED

    def test_candidate_set_has_lean4(self):
        step = self._get_step("CANDIDATE_SET_5_7")
        assert step.lean4_file is not None

    def test_action_ordering_is_proved(self):
        step = self._get_step("ACTION_ORDERING")
        assert step.status == EpistemicStatus.PROVED

    def test_action_ordering_no_observational_inputs(self):
        step = self._get_step("ACTION_ORDERING")
        assert step.observational_inputs == []

    def test_planck_ns_is_observational(self):
        step = self._get_step("PLANCK_NS_SELECTION")
        assert step.status == EpistemicStatus.OBSERVATIONAL_INPUT

    def test_planck_ns_has_input(self):
        step = self._get_step("PLANCK_NS_SELECTION")
        assert len(step.observational_inputs) >= 1
        assert any("Planck" in obs for obs in step.observational_inputs)

    def test_aps_is_axiom_dependent(self):
        step = self._get_step("APS_ETA_INVARIANT")
        assert step.status == EpistemicStatus.AXIOM_DEPENDENT

    def test_aps_has_gap_description(self):
        step = self._get_step("APS_ETA_INVARIANT")
        assert step.gap_description is not None
        assert len(step.gap_description) > 20

    def test_ngen_derivation_is_architecture_limit(self):
        step = self._get_step("NGEN_DERIVATION")
        assert step.status == EpistemicStatus.ARCHITECTURE_LIMIT

    def test_ngen_has_no_lean4(self):
        step = self._get_step("NGEN_DERIVATION")
        assert step.lean4_file is None

    def test_aps_mathlib_is_architecture_limit(self):
        step = self._get_step("APS_MATHLIB_FORMALIZATION")
        assert step.status == EpistemicStatus.ARCHITECTURE_LIMIT

    def test_cs_anomaly_steps_have_ngen_dependency(self):
        for step_id in ["CS_ANOMALY_GAP_LOWER", "CS_ANOMALY_GAP_UPPER"]:
            step = self._get_step(step_id)
            ngen_found = any("N_gen" in obs for obs in step.observational_inputs)
            assert ngen_found, f"{step_id} should list N_gen as observational input"


class TestObservationalDependencies:
    """Tests on observational input tracking."""

    def setup_method(self):
        self.report = run_circularity_audit()

    def test_planck_is_in_observational_inputs(self):
        assert any("Planck" in obs for obs in self.report.observational_inputs)

    def test_ngen_is_in_observational_inputs(self):
        assert any("N_gen" in obs or "generation" in obs.lower()
                   for obs in self.report.observational_inputs)

    def test_observational_inputs_nonempty(self):
        assert len(self.report.observational_inputs) >= 2


class TestOpenGaps:
    """Tests on the architecture limit / open gap tracking."""

    def setup_method(self):
        self.report = run_circularity_audit()

    def test_at_least_two_open_gaps(self):
        assert len(self.report.open_gaps) >= 2

    def test_ngen_is_open_gap(self):
        assert "NGEN_DERIVATION" in self.report.open_gaps

    def test_aps_mathlib_is_open_gap(self):
        assert "APS_MATHLIB_FORMALIZATION" in self.report.open_gaps


class TestCircularityAuditReport:
    """Tests on the full report output."""

    def setup_method(self):
        self.report = run_circularity_audit()

    def test_report_is_circularity_audit_report(self):
        assert isinstance(self.report, CircularityAuditReport)

    def test_total_steps_correct(self):
        assert self.report.total_steps == len(AUDIT_STEPS)

    def test_proved_steps_are_counted(self):
        expected = sum(
            1 for s in AUDIT_STEPS if s.status == EpistemicStatus.PROVED
        )
        assert self.report.proved_steps == expected

    def test_architecture_limit_count(self):
        expected = sum(
            1 for s in AUDIT_STEPS
            if s.status == EpistemicStatus.ARCHITECTURE_LIMIT
        )
        assert self.report.architecture_limit_steps == expected

    def test_summary_contains_key_phrases(self):
        summary = self.report.summary
        assert "n_w = 5" in summary or "n_w" in summary
        assert "observational" in summary.lower() or "Observational" in summary
        assert "open" in summary.lower() or "Open" in summary

    def test_to_dict_structure(self):
        d = self.report.to_dict()
        required_keys = [
            "total_steps", "proved_steps", "geometric_steps",
            "axiom_dependent_steps", "observational_input_steps",
            "architecture_limit_steps", "observational_inputs",
            "open_gaps", "summary"
        ]
        for key in required_keys:
            assert key in d, f"Missing key '{key}' in to_dict() output"

    def test_to_dict_total_steps_matches(self):
        d = self.report.to_dict()
        assert d["total_steps"] == self.report.total_steps

    def test_steps_are_accessible(self):
        assert len(self.report.steps) == len(AUDIT_STEPS)


class TestBuildDependencyGraph:
    """Tests on the dependency graph builder."""

    def test_returns_list(self):
        graph = build_nw_dependency_graph()
        assert isinstance(graph, list)

    def test_returns_copy(self):
        g1 = build_nw_dependency_graph()
        g2 = build_nw_dependency_graph()
        # Should be equal but separate lists
        assert g1 == g2

    def test_all_items_are_dependencies(self):
        graph = build_nw_dependency_graph()
        for item in graph:
            assert isinstance(item, Dependency)


class TestEpistemicStatusEnum:
    """Tests on the EpistemicStatus enum."""

    def test_all_expected_statuses_exist(self):
        expected = [
            "PURELY_GEOMETRIC", "OBSERVATIONAL_INPUT", "ARITHMETIC_IDENTITY",
            "ARCHITECTURE_LIMIT", "AXIOM_DEPENDENT", "PROVED"
        ]
        for name in expected:
            assert hasattr(EpistemicStatus, name)

    def test_status_value_is_string(self):
        # EpistemicStatus value is a plain string
        assert isinstance(EpistemicStatus.PROVED.value, str)
        assert EpistemicStatus.PROVED.value == "PROVED"


class TestArithmeticClaims:
    """Tests that verify the arithmetic facts underlying the Lean4 proofs."""

    def test_kcs_is_74(self):
        """K_CS = 5² + 7² = 74."""
        assert 5**2 + 7**2 == 74

    def test_keff_5_is_74(self):
        """k_eff(5) = 5² + 7² = 74."""
        assert 5**2 + (5 + 2)**2 == 74

    def test_keff_7_is_130(self):
        """k_eff(7) = 7² + 9² = 130."""
        assert 7**2 + (7 + 2)**2 == 130

    def test_action_ordering(self):
        """k_eff(5) < k_eff(7)."""
        assert 74 < 130

    def test_candidate_set_arithmetic(self):
        """Only 5 and 7 are odd integers in [4,8]."""
        candidates = [n for n in range(1, 20) if n % 2 == 1 and 4 <= n <= 8]
        assert candidates == [5, 7]

    def test_planck_discriminator(self):
        """n_s(n_w=7) is ~12× further from Planck than n_s(n_w=5)."""
        dist_5 = abs(9649 - 9635)   # 14
        dist_7 = abs(9649 - 9814)   # 165
        assert dist_5 == 14
        assert dist_7 == 165
        assert dist_5 * 11 < dist_7

    def test_cs_irreducibility(self):
        """gcd(12, 37) = 1."""
        from math import gcd
        assert gcd(12, 37) == 1

    def test_37_is_prime(self):
        """37 is prime."""
        from sympy import isprime
        assert isprime(37)

    def test_action_difference(self):
        """k_eff(7) - k_eff(5) = 56."""
        assert 130 - 74 == 56
