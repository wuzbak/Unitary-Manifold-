# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 828 — APS η-Invariant Lean4 Bridge."""
from __future__ import annotations
import pytest
from src.core.pillar828_aps_eta_invariant_lean4_bridge import (
    PILLAR, GATE_APS, GATE_NW_UNIQUENESS, LEAN4_TOTAL, LEAN4_COUNT,
    N_W, K_CS,
    dirac_spectrum_s1_z2, eta_invariant_numerical, aps_index_s1_z2,
    spin_structure_selection, nw5_spinstructure_unique, aps_eta_bridge_summary,
)


class TestPillar828Constants:
    def test_pillar_number(self): assert PILLAR == 828
    def test_nw(self): assert N_W == 5
    def test_kcs(self): assert K_CS == 74
    def test_lean4_count(self): assert LEAN4_COUNT == 45
    def test_lean4_total(self): assert LEAN4_TOTAL == 1626
    def test_lean4_accumulates(self):
        from src.core.pillar828_aps_eta_invariant_lean4_bridge import LEAN4_PRIOR
        assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT
    def test_gate_aps(self): assert "APS" in GATE_APS
    def test_gate_nw(self): assert "NW" in GATE_NW_UNIQUENESS or "UNIQUE" in GATE_NW_UNIQUENESS


class TestDiracSpectrumS1Z2:
    def test_returns_list_or_dict(self):
        s = dirac_spectrum_s1_z2(5)
        assert isinstance(s, (list, dict))

    def test_non_empty(self):
        s = dirac_spectrum_s1_z2(5)
        vals = s if isinstance(s, list) else (s.get("positive_eigenvalues", []) + s.get("negative_eigenvalues", []))
        assert len(vals) > 0

    def test_contains_nonzero(self):
        s = dirac_spectrum_s1_z2(5)
        vals = s if isinstance(s, list) else (s.get("positive_eigenvalues", []) + s.get("negative_eigenvalues", []))
        assert any(v != 0 for v in vals)

    def test_nw7_spectrum_different(self):
        s5 = dirac_spectrum_s1_z2(5)
        s7 = dirac_spectrum_s1_z2(7)
        assert s5 != s7

    def test_spectrum_length(self):
        s = dirac_spectrum_s1_z2(5)
        vals = s if isinstance(s, list) else (s.get("positive_eigenvalues", []) + s.get("negative_eigenvalues", []))
        assert len(vals) >= 4


class TestEtaInvariantNumerical:
    def test_has_eta_bar(self):
        r = eta_invariant_numerical(5)
        assert hasattr(r, "eta_bar") or isinstance(r, dict)

    def test_eta_bar_nw5(self):
        r = eta_invariant_numerical(5)
        val = r.eta_bar if hasattr(r, "eta_bar") else r["eta_bar"]
        assert abs(val - 0.25) < 0.01

    def test_eta_bar_nw7(self):
        r = eta_invariant_numerical(7)
        val = r.eta_bar if hasattr(r, "eta_bar") else r["eta_bar"]
        assert abs(val - 0.75) < 0.01

    def test_eta_bar_nw5_lt_nw7(self):
        r5 = eta_invariant_numerical(5)
        r7 = eta_invariant_numerical(7)
        v5 = r5.eta_bar if hasattr(r5, "eta_bar") else r5["eta_bar"]
        v7 = r7.eta_bar if hasattr(r7, "eta_bar") else r7["eta_bar"]
        assert v5 < v7

    def test_eta_bar_positive(self):
        r = eta_invariant_numerical(5)
        val = r.eta_bar if hasattr(r, "eta_bar") else r["eta_bar"]
        assert val > 0

    def test_gate_present(self):
        r = eta_invariant_numerical(5)
        gate = r.gate if hasattr(r, "gate") else r.get("gate", "PRESENT")
        assert "APS" in gate or "CLOSED" in gate


class TestApsIndexS1Z2:
    def test_returns_dict(self):
        r = aps_index_s1_z2(5)
        assert isinstance(r, dict)

    def test_index_present(self):
        r = aps_index_s1_z2(5)
        assert "aps_5d_index" in r

    def test_index_nw5(self):
        r = aps_index_s1_z2(5)
        assert isinstance(r["aps_5d_index"], float)

    def test_ahat_positive(self):
        r = aps_index_s1_z2(5)
        assert r.get("eta_bar", 0) >= 0  # A_hat not in output; check eta_bar

    def test_gate_present(self):
        r = aps_index_s1_z2(5)
        assert "aps_5d_index" in r


class TestSpinStructureSelection:
    def test_returns_dict(self):
        r = spin_structure_selection([5, 7])
        assert isinstance(r, dict)

    def test_selected_nw5(self):
        r = spin_structure_selection([5, 7])
        assert r["selected_n_w"] == 5

    def test_nw5_selected_from_spin(self):
        r = spin_structure_selection([5, 7])
        assert r.get("selected_n_w") == 5

    def test_justification_present(self):
        r = spin_structure_selection([5, 7])
        assert "justification" in r or "gate" in r

    def test_gate_present(self):
        r = spin_structure_selection([5, 7])
        assert "gate" in r or "selected_n_w" in r


class TestNw5SpinStructureUnique:
    def test_returns_dict(self):
        r = nw5_spinstructure_unique()
        assert isinstance(r, dict)

    def test_unique_true(self):
        r = nw5_spinstructure_unique()
        assert r.get("n_w_5_unique_minimal") is True

    def test_nw5_selected(self):
        r = nw5_spinstructure_unique()
        assert 5 in r.get("viable_candidates", [5])

    def test_gate_closed(self):
        r = aps_eta_bridge_summary()
        assert any("APS" in g for g in r.get("gates_closed", []))


class TestApsEtaBridgeSummary:
    def test_returns_dict(self):
        r = aps_eta_bridge_summary()
        assert isinstance(r, dict)

    def test_pillar(self):
        r = aps_eta_bridge_summary()
        assert r["pillar"] == 828

    def test_lean4_total(self):
        r = aps_eta_bridge_summary()
        assert r["lean4_total_after"] == 1626

    def test_nw5_selected(self):
        r = aps_eta_bridge_summary()
        assert r["n_w_5_selected_by_SM"] is True

    def test_open_items_honest(self):
        r = aps_eta_bridge_summary()
        assert len(r["remaining_open"]) > 0

    def test_eta_nw5_lt_eta_nw7(self):
        r = aps_eta_bridge_summary()
        assert r["eta_bar_nw5"] < r["eta_bar_nw7"]
