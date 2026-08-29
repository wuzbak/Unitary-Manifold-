# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 836 — Sprint AZ Regression Certificate."""
from __future__ import annotations
import pytest
from src.core.pillar836_sprint_az_regression_certificate import (
    PILLAR_NUMBER, PILLAR_GATE, SPRINT_NAME, SPRINT_VERSION,
    LEAN4_START, LEAN4_END, LEAN4_DELTA, PILLARS, REMAINING_OPEN,
    SPRINT_VALID, validate_sprint, sprint_az_summary,
)


class TestPillar836Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 836
    def test_gate(self): assert PILLAR_GATE == "SPRINT_AZ_REGRESSION_CERTIFICATE"
    def test_sprint_name(self): assert "AZ" in SPRINT_NAME
    def test_sprint_version(self): assert SPRINT_VERSION == "v25.0"
    def test_lean4_start(self): assert LEAN4_START == 1506
    def test_lean4_end(self): assert LEAN4_END == 1821
    def test_lean4_delta(self): assert LEAN4_DELTA == 315
    def test_n_pillars(self): assert len(PILLARS) == 10
    def test_sprint_valid(self): assert SPRINT_VALID is True
    def test_remaining_open_honest(self): assert len(REMAINING_OPEN) >= 8


class TestPillarRegistry:
    def test_pillars_826_to_835(self):
        numbers = [p["number"] for p in PILLARS]
        for n in range(826, 836):
            assert n in numbers

    def test_all_have_gates(self):
        for p in PILLARS:
            assert "gate" in p
            assert isinstance(p["gate"], str)

    def test_all_have_lean4(self):
        for p in PILLARS:
            assert "lean4_theorems" in p
            assert p["lean4_theorems"] > 0

    def test_total_lean4_matches(self):
        total = sum(p["lean4_theorems"] for p in PILLARS)
        assert total == LEAN4_DELTA


class TestValidateSprint:
    def test_returns_dict(self):
        r = validate_sprint()
        assert isinstance(r, dict)

    def test_passed(self):
        r = validate_sprint()
        assert r["passed"] is True, f"Sprint failed: {r['errors']}"

    def test_no_errors(self):
        r = validate_sprint()
        assert len(r["errors"]) == 0, f"Errors: {r['errors']}"

    def test_lean4_total_1821(self):
        r = validate_sprint()
        assert r["lean4_total"] == 1821

    def test_lean4_delta_315(self):
        r = validate_sprint()
        assert r["lean4_delta"] == 315

    def test_pillars_in_sprint(self):
        r = validate_sprint()
        assert len(r["pillars_in_sprint"]) == 10

    def test_remaining_open_present(self):
        r = validate_sprint()
        assert r["n_remaining_open"] >= 8

    def test_gate_present(self):
        r = validate_sprint()
        assert r["gate"] == "SPRINT_AZ_REGRESSION_CERTIFICATE"


class TestSprintAzSummary:
    def test_returns_dict(self):
        r = sprint_az_summary()
        assert isinstance(r, dict)

    def test_sprint_complete(self):
        r = sprint_az_summary()
        assert r["sprint_complete"] is True, f"Not complete: {r.get('errors')}"

    def test_lean4_total(self):
        r = sprint_az_summary()
        assert r["lean4_total"] == 1821

    def test_lean4_delta(self):
        r = sprint_az_summary()
        assert r["lean4_delta"] == 315

    def test_version(self):
        r = sprint_az_summary()
        assert r["version"] == "v25.0"

    def test_n_pillars(self):
        r = sprint_az_summary()
        assert r["n_pillars"] == 10
