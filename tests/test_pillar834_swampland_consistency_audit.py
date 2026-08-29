# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 834 — Swampland Consistency Audit."""
from __future__ import annotations
import pytest
from src.core.pillar834_swampland_consistency_audit import (
    PILLAR, LEAN4_TOTAL, LEAN4_COUNT,
    distance_conjecture_check, de_sitter_conjecture_check, weak_gravity_conjecture_check,
    swampland_audit_report,
)


class TestPillar834Constants:
    def test_pillar_number(self): assert PILLAR == 834
    def test_lean4_count(self): assert LEAN4_COUNT == 20
    def test_lean4_total(self): assert LEAN4_TOTAL == 1776
    def test_lean4_accumulates(self):
        from src.core.pillar834_swampland_consistency_audit import LEAN4_PRIOR
        assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT


class TestDistanceConjectureCheck:
    def test_returns_dict(self):
        r = distance_conjecture_check()
        assert isinstance(r, dict)

    def test_delta_phi_5d(self):
        r = distance_conjecture_check()
        assert r["delta_phi_5d_units"] > 0

    def test_p806_tension_resolved(self):
        r = distance_conjecture_check()
        assert r["p806_tension_resolved"] is True

    def test_4d_subplanckian(self):
        r = distance_conjecture_check()
        assert r["is_sub_planckian_4d"] is True

    def test_verdict_pass(self):
        r = distance_conjecture_check()
        assert "PASS" in r["verdict"]

    def test_explanation_present(self):
        r = distance_conjecture_check()
        assert len(r["explanation"]) > 0


class TestDeSitterConjectureCheck:
    def test_returns_dict(self):
        r = de_sitter_conjecture_check()
        assert isinstance(r, dict)

    def test_ratio_present(self):
        r = de_sitter_conjecture_check()
        assert "ratio_VpV" in r

    def test_is_rolling(self):
        r = de_sitter_conjecture_check()
        assert r["is_rolling"] is True

    def test_verdict_present(self):
        r = de_sitter_conjecture_check()
        assert "verdict" in r


class TestWeakGravityConjectureCheck:
    def test_returns_dict(self):
        r = weak_gravity_conjecture_check()
        assert isinstance(r, dict)

    def test_verdict_present(self):
        r = weak_gravity_conjecture_check()
        assert "verdict" in r

    def test_coupling_positive(self):
        r = weak_gravity_conjecture_check()
        assert r.get("g5", 1.0) > 0


class TestSwamplandAuditReport:
    def test_returns_dict(self):
        r = swampland_audit_report()
        assert isinstance(r, dict)

    def test_pillar(self):
        r = swampland_audit_report()
        assert r["pillar"] == 834

    def test_lean4_total(self):
        r = swampland_audit_report()
        assert r["lean4_total_after"] == 1776

    def test_distance_conjecture_pass(self):
        r = swampland_audit_report()
        assert "PASS" in r["distance_conjecture"]

    def test_p806_resolved(self):
        r = swampland_audit_report()
        assert r["p806_tension_resolved"] is True

    def test_overall_status_present(self):
        r = swampland_audit_report()
        assert "overall_status" in r

    def test_open_items_honest(self):
        r = swampland_audit_report()
        assert "remaining_open" in r
