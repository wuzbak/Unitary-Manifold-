# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 852 — Sprint BA Phase 3 regression certificate."""
from __future__ import annotations

from src.nined.pillar852_sprint_ba_phase3_regression_certificate import (
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    PILLARS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SPRINT_NAME,
    SPRINT_VALID,
    SPRINT_VERSION,
    sprint_ba_phase3_summary,
    validate_sprint,
)


class TestPillar852Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 852
    def test_gate(self): assert PILLAR_GATE == "SPRINT_BA_PHASE3_REGRESSION_CERTIFICATE"
    def test_name(self): assert "Phase 3" in SPRINT_NAME
    def test_version(self): assert SPRINT_VERSION == "v25.3"
    def test_lean_chain(self):
        assert LEAN4_START == 1996
        assert LEAN4_END == 2046
        assert LEAN4_DELTA == 50
    def test_pillars(self): assert [p["number"] for p in PILLARS] == [849, 850]
    def test_valid_flag(self): assert SPRINT_VALID is True
    def test_remaining_open_present(self): assert len(REMAINING_OPEN) >= 1


class TestValidateSprint:
    def test_passed(self):
        result = validate_sprint()
        assert result["passed"] is True, result["errors"]

    def test_no_errors(self):
        assert validate_sprint()["errors"] == []

    def test_gate(self):
        assert validate_sprint()["gate"] == PILLAR_GATE


class TestPhase3Summary:
    def test_complete(self):
        assert sprint_ba_phase3_summary()["sprint_complete"] is True

    def test_n_pillars(self):
        assert sprint_ba_phase3_summary()["n_pillars"] == 2

    def test_lean_total(self):
        assert sprint_ba_phase3_summary()["lean4_total"] == 2046
