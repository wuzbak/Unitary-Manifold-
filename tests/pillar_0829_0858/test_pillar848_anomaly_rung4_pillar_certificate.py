# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 848 — 8D→9D GS anomaly scaffold (Rung 4) pillar certificate."""
from __future__ import annotations

from src.eightd.pillar848_anomaly_rung4_pillar_certificate import (
    ADJACENCY_TRACK_LABEL,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    nined_anomaly_pillar_certificate,
    separation_guard,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 848


def test_gate():
    assert PILLAR_GATE == "EIGHTD_TO_NINED_ANOMALY_RUNG4_PILLAR_CERTIFICATE"


def test_title_mentions_rungs():
    assert "8D" in PILLAR_TITLE and "9D" in PILLAR_TITLE


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
        assert nined_anomaly_pillar_certificate()["pillar"] == 848

    def test_rung_id(self):
        assert nined_anomaly_pillar_certificate()["rung_id"] == "R4"

    def test_dimension(self):
        assert nined_anomaly_pillar_certificate()["dimension"] == "9D"

    def test_kill_switch_pass(self):
        assert nined_anomaly_pillar_certificate()["kill_switch_pass"] is True

    def test_acceptance_gate_passed(self):
        assert nined_anomaly_pillar_certificate()["acceptance_gate_passed"] is True

    def test_feeds_pillar_849(self):
        assert nined_anomaly_pillar_certificate()["feeds_pillar"] == 849

    def test_source_module(self):
        cert = nined_anomaly_pillar_certificate()
        assert cert["source_module"] == "src/nined/anomaly_cancellation_gs.py"
