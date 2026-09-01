# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 849 — 9D GS anomaly bridge."""
from __future__ import annotations

from pathlib import Path

from src.nined.pillar849_9d_gs_anomaly_bridge import (
    BRAID_PAIR_SQ_SUM,
    GS_ANOMALY_CANCELLED,
    K_CS_BRAID,
    K_CS_FROM_GS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    PILLAR_GATE,
    PILLAR_NUMBER,
    braid_partner_from_winding,
    gs_9d_bridge_summary,
    gs_bridge_invariants,
    gs_cs_level_from_braid_pair,
)


class TestPillar849Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 849
    def test_gate(self): assert PILLAR_GATE == "NINEDD_GS_5D_ANOMALY_BRIDGE_CLOSED"
    def test_kcs(self): assert K_CS_FROM_GS == 74
    def test_pair(self): assert K_CS_BRAID == (5, 7)
    def test_sq_sum(self): assert BRAID_PAIR_SQ_SUM == 74
    def test_anomaly_cancelled(self): assert GS_ANOMALY_CANCELLED is True
    def test_lean4(self):
        assert LEAN4_THEOREM_COUNT == 30
        assert LEAN4_TOTAL_AFTER == 2026


class TestBridgeArithmetic:
    def test_partner_from_winding(self):
        assert braid_partner_from_winding(5) == 7

    def test_cs_formula(self):
        assert gs_cs_level_from_braid_pair(5) == 74

    def test_invariants(self):
        inv = gs_bridge_invariants()
        assert inv["sum_of_squares_identity"] is True
        assert inv["five_d_cs_not_free"] is True


class TestSummary:
    def test_returns_dict(self):
        assert isinstance(gs_9d_bridge_summary(), dict)

    def test_summary_gate(self):
        assert gs_9d_bridge_summary()["gate"] == PILLAR_GATE

    def test_not_free(self):
        assert gs_9d_bridge_summary()["not_free_parameter"] is True

    def test_bianchi_and_counterterm(self):
        s = gs_9d_bridge_summary()
        assert s["bianchi_balance_pass"] is True
        assert s["counterterm_present"] is True


class TestLean4File:
    LEAN_FILE = Path(__file__).resolve().parents[1] / "lean4" / "UnitaryManifold" / "GS9DAnomalyBridge.lean"

    def test_exists(self):
        assert self.LEAN_FILE.exists()

    def test_no_sorry(self):
        assert "sorry" not in self.LEAN_FILE.read_text()

    def test_theorem_count(self):
        assert self.LEAN_FILE.read_text().count("theorem ") >= 25
