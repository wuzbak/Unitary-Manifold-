# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar384_c5_no_torsion.py
=====================================
Tests for the C5 (No Torsion) extension to Pillar 384 — Admission 13.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import pytest

from src.core.pillar384_metric_ansatz_uniqueness import (
    no_torsion_constraint,
    five_constraint_uniqueness_verdict,
    admission_13_closure_verdict,
    pillar384_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# C5 no-torsion constraint
# ─────────────────────────────────────────────────────────────────────────────

class TestNoTorsionConstraint:
    @pytest.fixture(scope="class")
    def result(self):
        return no_torsion_constraint()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_constraint_name(self, result):
        assert result["constraint"] == "C5"

    def test_name_contains_torsion(self, result):
        assert "torsion" in result["name"].lower() or "Torsion" in result["name"]

    def test_action_is_minimal_eh(self, result):
        assert "R₅" in result["action"] or "EH" in result["action"]

    def test_excludes_list(self, result):
        assert isinstance(result["excludes"], list)
        assert len(result["excludes"]) >= 2

    def test_excludes_einstein_cartan(self, result):
        excludes_str = " ".join(result["excludes"]).lower()
        assert "einstein-cartan" in excludes_str or "torsion" in excludes_str

    def test_does_not_exclude_list(self, result):
        assert isinstance(result["does_not_exclude"], list)
        assert len(result["does_not_exclude"]) >= 2

    def test_does_not_exclude_6d(self, result):
        """6D alternatives are NOT excluded by C5 — honest boundary."""
        does_not_str = " ".join(result["does_not_exclude"]).lower()
        assert "6d" in does_not_str or "g₂" in does_not_str or "calabi" in does_not_str

    def test_c5_satisfied(self, result):
        assert result["c5_satisfied"] is True

    def test_ec_alternative_excluded(self, result):
        assert result["ec_alternative_excluded"] is True

    def test_six_d_NOT_excluded(self, result):
        """Honest: 6D alternatives are NOT excluded by C5."""
        assert result["six_d_alternative_excluded"] is False

    def test_justification_string(self, result):
        assert isinstance(result["justification"], str)
        assert len(result["justification"]) > 30

    def test_honest_note_string(self, result):
        assert isinstance(result["honest_note"], str)
        assert "6D" in result["honest_note"] or "6d" in result["honest_note"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# Five-constraint uniqueness verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestFiveConstraintUniquenessVerdict:
    @pytest.fixture(scope="class")
    def result(self):
        return five_constraint_uniqueness_verdict()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_five_constraints_listed(self, result):
        assert "C1" in result["constraints"]
        assert "C5" in result["constraints"]
        assert len(result["constraints"]) == 5

    def test_c1_eh_met(self, result):
        assert result["c1_eh_stationarity"] is True

    def test_c2_kk_met(self, result):
        assert result["c2_kk_gauge_covariance"] is True

    def test_c3_z2_met(self, result):
        assert result["c3_z2_parity"] is True

    def test_c4_radion_met(self, result):
        assert result["c4_radion_normalization"] is True

    def test_c5_no_torsion_met(self, result):
        assert result["c5_no_torsion"] is True

    def test_all_c1_c4_met(self, result):
        assert result["all_c1_c4_met"] is True

    def test_all_c1_c5_met(self, result):
        assert result["all_c1_c5_met"] is True

    def test_ec_alternative_excluded(self, result):
        assert result["ec_alternative_excluded_by_c5"] is True

    def test_six_d_NOT_excluded(self, result):
        """Honest: 6D not excluded."""
        assert result["six_d_alternative_excluded"] is False

    def test_admission_13_new_status(self, result):
        assert result["admission_13_new_status"] == "NARROWED_GAP"

    def test_admission_13_old_status(self, result):
        assert result["admission_13_previous_status"] == "OPEN_GAP"

    def test_uniqueness_scope_string(self, result):
        assert isinstance(result["uniqueness_scope"], str)
        assert "5D" in result["uniqueness_scope"]

    def test_honest_residual_string(self, result):
        assert isinstance(result["honest_residual"], str)
        assert "6D" in result["honest_residual"] or "11D" in result["honest_residual"]

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert "NARROWED_GAP" in result["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# Admission 13 closure verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission13ClosureVerdict:
    @pytest.fixture(scope="class")
    def verdict(self):
        return admission_13_closure_verdict()

    def test_returns_dict(self, verdict):
        assert isinstance(verdict, dict)

    def test_admission_number(self, verdict):
        assert verdict["admission"] == 13

    def test_previous_status(self, verdict):
        assert verdict["previous_status"] == "OPEN_GAP"

    def test_new_status(self, verdict):
        assert verdict["new_status"] == "NARROWED_GAP"

    def test_c1_c5_met(self, verdict):
        assert verdict["constraints_c1_c5_met"] is True

    def test_c5_excludes_einstein_cartan(self, verdict):
        assert verdict["c5_excludes_einstein_cartan"] is True

    def test_c5_does_not_exclude_6d(self, verdict):
        assert verdict["c5_does_not_exclude_6d"] is True

    def test_honest_residual(self, verdict):
        assert isinstance(verdict["honest_residual"], str)
        assert "6D" in verdict["honest_residual"] or "6d" in verdict["honest_residual"].lower()

    def test_uniqueness_scope(self, verdict):
        assert isinstance(verdict["uniqueness_scope"], str)
        assert "5D" in verdict["uniqueness_scope"]

    def test_citation_contains_384(self, verdict):
        assert "384" in verdict["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Pillar 384 updated summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar384SummaryWithC5:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar384_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_pillar_number(self, summary):
        assert summary["pillar_number"] == 384

    def test_admission_13_key(self, summary):
        assert "admission_13" in summary

    def test_admission_13_new_status(self, summary):
        assert summary["admission_13"]["new_status"] == "NARROWED_GAP"

    def test_c5_constraint_present(self, summary):
        assert "c5_constraint" in summary

    def test_c5_all_met(self, summary):
        assert summary["c5_constraint"]["all_c1_c5_met"] is True

    def test_key_result_mentions_c5(self, summary):
        assert "C5" in summary["key_result"]

    def test_key_result_mentions_narrowed(self, summary):
        assert "NARROWED" in summary["key_result"]

    def test_falsification_mentions_torsion(self, summary):
        assert "torsion" in summary["falsification"].lower()
