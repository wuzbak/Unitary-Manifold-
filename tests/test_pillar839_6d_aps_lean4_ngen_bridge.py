# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 839 — Lean4 APS T²/Z₂ → N_gen bridge."""
from __future__ import annotations

from src.core.pillar839_6d_aps_lean4_ngen_bridge import (
    GATE,
    LEAN4_COUNT,
    LEAN4_FILE,
    LEAN4_PRIOR,
    LEAN4_TOTAL,
    PILLAR,
    aps_t2z2_ngen_bridge_summary,
    lean4_bridge_metadata,
)


class TestPillar839Constants:
    def test_pillar_number(self): assert PILLAR == 839
    def test_gate(self): assert GATE == "APS_T2Z2_NGEN_LEAN4_BRIDGE"
    def test_file_name(self): assert LEAN4_FILE == "APS_T2Z2_NgenBridge.lean"
    def test_lean4_count(self): assert LEAN4_COUNT == 35
    def test_lean4_total(self): assert LEAN4_TOTAL == 1911
    def test_lean4_accumulates(self): assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT


class TestLean4BridgeMetadata:
    def test_file_exists(self):
        assert lean4_bridge_metadata()["exists"] is True

    def test_theorem_count(self):
        assert lean4_bridge_metadata()["theorem_count"] == 35

    def test_no_sorry(self):
        assert lean4_bridge_metadata()["contains_sorry"] is False

    def test_native_decide_used(self):
        assert lean4_bridge_metadata()["native_decide_count"] >= 10


class TestPillar839Summary:
    def test_summary_pillar(self):
        assert aps_t2z2_ngen_bridge_summary()["pillar"] == 839

    def test_summary_bridge_valid(self):
        assert aps_t2z2_ngen_bridge_summary()["bridge_valid"] is True

    def test_summary_chern_number(self):
        assert aps_t2z2_ngen_bridge_summary()["chern_number_c1"] == 3

    def test_summary_ngen(self):
        assert aps_t2z2_ngen_bridge_summary()["n_gen_derived"] == 3

    def test_summary_honest_status(self):
        assert "proxy" in aps_t2z2_ngen_bridge_summary()["honest_status"].lower()
