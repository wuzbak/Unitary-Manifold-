# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 846 — Sprint BA Phase 2 regression certificate."""
from __future__ import annotations

from pathlib import Path

from src.sevend.pillar846_sprint_ba_phase2_regression_certificate import (
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
    sprint_ba_phase2_summary,
    validate_sprint,
)


class TestPillar846Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 846
    def test_gate(self): assert PILLAR_GATE == "SPRINT_BA_PHASE2_REGRESSION_CERTIFICATE"
    def test_name(self): assert "Phase 2" in SPRINT_NAME
    def test_version(self): assert SPRINT_VERSION == "v25.2"
    def test_lean_chain(self):
        assert LEAN4_START == 1951
        assert LEAN4_END == 1996
        assert LEAN4_DELTA == 45
    def test_pillars(self): assert [p["number"] for p in PILLARS] == [843, 844]
    def test_remaining_open(self): assert len(REMAINING_OPEN) == 2
    def test_valid_flag(self): assert SPRINT_VALID is True


class TestValidateSprint:
    def test_passed(self):
        result = validate_sprint()
        assert result["passed"] is True, result["errors"]

    def test_no_errors(self):
        assert validate_sprint()["errors"] == []

    def test_gate(self):
        assert validate_sprint()["gate"] == PILLAR_GATE

    def test_lean_delta(self):
        assert validate_sprint()["lean4_delta"] == 45


class TestPhase2Summary:
    def test_complete(self):
        assert sprint_ba_phase2_summary()["sprint_complete"] is True

    def test_n_pillars(self):
        assert sprint_ba_phase2_summary()["n_pillars"] == 2

    def test_remaining_open_count(self):
        assert sprint_ba_phase2_summary()["n_remaining_open"] == 2


class TestLean4Files:
    def test_ckm_file_exists(self):
        lean = Path(__file__).resolve().parents[1] / "lean4" / "UnitaryManifold" / "CKM7DMixingAngles.lean"
        assert lean.exists()
