# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 847 — 8D Wilson-line gauge scaffold (Rung 3) pillar certificate."""
from __future__ import annotations

from src.eightd.pillar847_wilson_line_rung3_pillar_certificate import (
    ADJACENCY_TRACK_LABEL,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    eightd_wilson_line_pillar_certificate,
    separation_guard,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 847


def test_gate():
    assert PILLAR_GATE == "EIGHTD_WILSON_LINE_RUNG3_PILLAR_CERTIFICATE"


def test_title_mentions_8d():
    assert "8D" in PILLAR_TITLE


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_lean4_zero():
    assert LEAN4_THEOREM_COUNT == 0
    assert LEAN4_TOTAL_AFTER == 1996


class TestSeparationGuard:
    def test_not_hardgate(self):
        assert separation_guard()["is_hardgate"] is False

    def test_wraps_existing_only(self):
        assert separation_guard()["wraps_existing_scaffold_only"] is True


class TestCertificate:
    def test_pillar(self):
        assert eightd_wilson_line_pillar_certificate()["pillar"] == 847

    def test_rung_id(self):
        assert eightd_wilson_line_pillar_certificate()["rung_id"] == "R3"

    def test_dimension(self):
        assert eightd_wilson_line_pillar_certificate()["dimension"] == "8D"

    def test_kill_switch_pass(self):
        assert eightd_wilson_line_pillar_certificate()["kill_switch_pass"] is True

    def test_acceptance_gate_passed(self):
        assert eightd_wilson_line_pillar_certificate()["acceptance_gate_passed"] is True

    def test_source_module(self):
        cert = eightd_wilson_line_pillar_certificate()
        assert cert["source_module"] == "src/eightd/wilson_line_gauge.py"

    def test_status_rung_solid(self):
        assert eightd_wilson_line_pillar_certificate()["status"] == "RUNG_SOLID"
