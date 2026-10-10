# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 857 — cross-dimensional pre-closure open-items audit."""
from __future__ import annotations

from src.core.pillar857_cross_dimensional_preclosure_audit import (
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    consolidated_open_items,
    phase_certificates_audited,
    preclosure_audit_summary,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 857


def test_gate():
    assert PILLAR_GATE == "CROSS_DIMENSIONAL_PRECLOSURE_OPEN_ITEMS_AUDIT_PARTIAL"


def test_title():
    assert "Pre-Closure" in PILLAR_TITLE


def test_lean4_zero():
    assert LEAN4_THEOREM_COUNT == 0
    assert LEAN4_TOTAL_AFTER == 2116


def test_phase_certificates_audited():
    assert phase_certificates_audited() == [842, 846, 852, 856]


def test_consolidated_open_items_nonempty():
    assert len(consolidated_open_items()) >= 3


class TestSummary:
    def test_pillar(self):
        assert preclosure_audit_summary()["pillar"] == 857

    def test_n_certificates(self):
        assert preclosure_audit_summary()["n_phase_certificates_audited"] == 4

    def test_audit_internally_consistent(self):
        assert preclosure_audit_summary()["audit_internally_consistent"] is True

    def test_acceptance_gate_passed(self):
        assert preclosure_audit_summary()["acceptance_gate_passed"] is True

    def test_hands_off_to_858(self):
        assert preclosure_audit_summary()["hands_off_to_pillar"] == 858

    def test_epistemic_status_mentions_partial(self):
        assert "PARTIAL" in preclosure_audit_summary()["epistemic_status"]

    def test_no_new_hardgate_claim(self):
        status = preclosure_audit_summary()["epistemic_status"]
        assert "no new hardgate" in status.lower()
