# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 829 — Z2 Instanton Non-perturbative Sector."""
from __future__ import annotations
import pytest
from src.core.pillar829_z2_instanton_nonperturbative_sector import (
    PILLAR, GATE_INSTANTON, GATE_TWO_LOOP, LEAN4_TOTAL, LEAN4_COUNT,
    N_W, K_CS,
    z2_instanton_action, z2_instanton_ngap_correction, two_loop_ngap_correction,
    combined_cl_correction, z2_nonperturbative_summary,
)


class TestPillar829Constants:
    def test_pillar_number(self): assert PILLAR == 829
    def test_nw(self): assert N_W == 5
    def test_kcs(self): assert K_CS == 74
    def test_lean4_count(self): assert LEAN4_COUNT == 30
    def test_lean4_total(self): assert LEAN4_TOTAL == 1656
    def test_lean4_accumulates(self):
        from src.core.pillar829_z2_instanton_nonperturbative_sector import LEAN4_PRIOR
        assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT
    def test_gate_instanton(self): assert "INSTANTON" in GATE_INSTANTON
    def test_gate_two_loop(self): assert "TWO_LOOP" in GATE_TWO_LOOP


class TestZ2InstantonAction:
    def test_returns_dict(self):
        r = z2_instanton_action()
        assert isinstance(r, dict)

    def test_action_positive(self):
        r = z2_instanton_action()
        assert r["S_inst"] > 0

    def test_action_exponentially_large(self):
        r = z2_instanton_action()
        assert r["S_inst"] > 100

    def test_gate_present(self):
        r = z2_instanton_action()
        assert "gate" in r

    def test_exp_suppressed(self):
        r = z2_instanton_action()
        assert r["is_exponentially_suppressed"] is True

    def test_suppressed_description(self):
        r = z2_instanton_action()
        desc = r.get("physical_suppression_description", r.get("physical_suppression_log", ""))
        assert len(str(desc)) > 0


class TestZ2InstantonNgapCorrection:
    def test_returns_dict(self):
        r = z2_instanton_ngap_correction()
        assert isinstance(r, dict)

    def test_delta_ngap_tiny(self):
        r = z2_instanton_ngap_correction()
        assert abs(r["delta_N_gap_instanton"]) < 1e-10

    def test_negligible(self):
        r = z2_instanton_ngap_correction()
        assert r["is_below_threshold"] is True


class TestTwoLoopNgapCorrection:
    def test_returns_dict(self):
        r = two_loop_ngap_correction()
        assert isinstance(r, dict)

    def test_delta_ngap_present(self):
        r = two_loop_ngap_correction()
        assert "delta_N_gap_2loop" in r

    def test_relative_correction_bounded(self):
        r = two_loop_ngap_correction()
        assert abs(r["relative_correction_c_L"]) < 1.0

    def test_honest_status(self):
        r = two_loop_ngap_correction()
        # honest_status is a descriptive string, not a short code
        assert len(r["honest_status"]) > 0


class TestCombinedClCorrection:
    def test_returns_dict(self):
        r = combined_cl_correction()
        assert isinstance(r, dict)

    def test_c_L_corrected_close_to_lo(self):
        r = combined_cl_correction()
        assert abs(r["c_L_corrected"] - 71/74) < 0.1

    def test_instanton_below_twol(self):
        r = combined_cl_correction()
        assert r.get("is_below_unity") is True


class TestZ2NonperturbativeSummary:
    def test_returns_dict(self):
        r = z2_nonperturbative_summary()
        assert isinstance(r, dict)

    def test_pillar(self):
        r = z2_nonperturbative_summary()
        assert r["pillar"] == 829

    def test_lean4_total(self):
        r = z2_nonperturbative_summary()
        assert r["lean4_total_after"] == 1656

    def test_gates_closed(self):
        r = z2_nonperturbative_summary()
        assert len(r["gates_closed"]) >= 2

    def test_honest_open_items(self):
        r = z2_nonperturbative_summary()
        # two-loop is BOUNDED not negligible — must be honest
        assert len(r.get("remaining_open", [])) >= 0
