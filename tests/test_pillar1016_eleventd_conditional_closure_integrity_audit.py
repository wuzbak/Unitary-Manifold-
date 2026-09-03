# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1016 — 11D conditional-closure integrity audit."""

from src.core.pillar1016_eleventd_conditional_closure_integrity_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    STRESS_POINTS,
    boundary_stress_audit,
    contradiction_checks,
    eleventd_integrity_audit,
    pillar1016_summary,
)


def test_identity_constants():
    assert PILLAR_NUMBER == 1016
    assert PILLAR_GATE == "ELEVENTD_CONDITIONAL_CLOSURE_INTEGRITY_AUDIT"
    assert PILLAR_STATUS == "ELEVENTD_CONDITIONAL_CLOSURE_INTEGRITY_AUDIT_COMPLETE"


def test_contradiction_checks_shape():
    checks = contradiction_checks()
    assert "checks" in checks
    assert "all_pass" in checks


def test_boundary_stress_cases_present():
    stress = boundary_stress_audit()
    assert len(stress["cases"]) == len(STRESS_POINTS)


def test_lane_report_structure():
    report = eleventd_integrity_audit()
    assert report["valid"] is True
    assert report["binary_outcome"] in {
        "ELEVENTD_CONDITIONAL_CHAIN_COHERENT",
        "ELEVENTD_BREAKPOINTS_CERTIFIED",
    }


def test_summary_fields():
    s = pillar1016_summary()
    assert s["status"] == PILLAR_STATUS
    assert "coherent" in s
