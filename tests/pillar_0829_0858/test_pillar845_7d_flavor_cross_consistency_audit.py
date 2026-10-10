# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 845 — 7D flavor-sector cross-consistency audit."""
from __future__ import annotations

from src.sevend.pillar845_7d_flavor_cross_consistency_audit import (
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    N_W,
    PI_KR,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    audited_pillars,
    cross_consistency_rows,
    sevend_cross_consistency_summary,
)


class TestPillar845Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 845

    def test_gate(self):
        assert PILLAR_GATE == "SEVEND_FLAVOR_CROSS_CONSISTENCY_AUDIT_PARTIAL"

    def test_title(self):
        assert "7D" in PILLAR_TITLE

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_lean4_zero(self):
        assert LEAN4_THEOREM_COUNT == 0

    def test_lean4_total_unchanged(self):
        assert LEAN4_TOTAL_AFTER == 1996


class TestAuditedPillars:
    def test_contains_843_844(self):
        assert audited_pillars() == [843, 844]


class TestCrossConsistencyRows:
    def test_three_rows(self):
        assert len(cross_consistency_rows()) == 3

    def test_all_rows_pass(self):
        for row in cross_consistency_rows():
            assert row["kill_switch_pass"] is True

    def test_pillar_575_row_has_residual(self):
        rows = cross_consistency_rows()
        p575 = next(r for r in rows if r["pillar"] == 575)
        assert p575["residual_physical"] < p575["residual_tolerance"]


class TestSummary:
    def test_pillar(self):
        assert sevend_cross_consistency_summary()["pillar"] == 845

    def test_all_kill_switches_pass(self):
        assert sevend_cross_consistency_summary()["all_kill_switches_pass"] is True

    def test_acceptance_gate(self):
        assert sevend_cross_consistency_summary()["acceptance_gate_passed"] is True

    def test_epistemic_status_mentions_partial(self):
        assert "PARTIAL" in sevend_cross_consistency_summary()["epistemic_status"]

    def test_remaining_open_carries_over(self):
        remaining = sevend_cross_consistency_summary()["remaining_open"]
        assert any("843" in item for item in remaining)
        assert any("844" in item for item in remaining)

    def test_lean4_fields(self):
        summary = sevend_cross_consistency_summary()
        assert summary["lean4_theorems"] == 0
        assert summary["lean4_total_after"] == 1996
