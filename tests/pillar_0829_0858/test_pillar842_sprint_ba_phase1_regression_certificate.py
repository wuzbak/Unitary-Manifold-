# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 842 — Sprint BA Phase 1 regression certificate."""
from __future__ import annotations

from src.core.pillar842_sprint_ba_phase1_regression_certificate import (
    GATE,
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    PILLARS,
    PILLAR,
    REMAINING_OPEN,
    SPRINT_NAME,
    SPRINT_VALID,
    SPRINT_VERSION,
    sprint_ba_phase1_summary,
    validate_sprint,
)


class TestPillar842Constants:
    def test_pillar_number(self): assert PILLAR == 842
    def test_gate(self): assert GATE == "SPRINT_BA_PHASE1_REGRESSION_CERTIFICATE"
    def test_sprint_name(self): assert "6D Architecture" in SPRINT_NAME
    def test_sprint_version(self): assert SPRINT_VERSION == "v25.1"
    def test_lean4_start(self): assert LEAN4_START == 1821
    def test_lean4_end(self): assert LEAN4_END == 1951
    def test_lean4_delta(self): assert LEAN4_DELTA == 130
    def test_pillar_count(self): assert len(PILLARS) == 5
    def test_sprint_valid_const(self): assert SPRINT_VALID is True


class TestPillar842Registry:
    def test_pillars_are_contiguous(self):
        assert [p["number"] for p in PILLARS] == [837, 838, 839, 840, 841]

    def test_theorem_sum_matches_delta(self):
        assert sum(p["lean4_theorems"] for p in PILLARS) == LEAN4_DELTA

    def test_remaining_open_registered(self):
        assert len(REMAINING_OPEN) == 4

    def test_remaining_open_honest_labels(self):
        assert all("OPEN" in item for item in REMAINING_OPEN)


class TestValidateSprint:
    def test_returns_dict(self):
        assert isinstance(validate_sprint(), dict)

    def test_passed(self):
        result = validate_sprint()
        assert result["passed"] is True, result["errors"]

    def test_no_errors(self):
        assert validate_sprint()["errors"] == []

    def test_lean4_chain(self):
        result = validate_sprint()
        assert result["lean4_start"] == 1821 and result["lean4_end"] == 1951

    def test_supporting_summaries_count(self):
        assert len(validate_sprint()["supporting_summaries"]) == 5


class TestSprintSummary:
    def test_summary_pillar(self):
        assert sprint_ba_phase1_summary()["pillar"] == 842

    def test_summary_gate(self):
        assert sprint_ba_phase1_summary()["gate"] == GATE

    def test_summary_valid(self):
        assert sprint_ba_phase1_summary()["sprint_valid"] is True

    def test_summary_no_errors(self):
        assert sprint_ba_phase1_summary()["errors"] == []
