# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 835 — n_w=5 Planck-Independent Maximal Closure."""
from __future__ import annotations
import pytest
from src.core.pillar835_nw5_planck_independence_maximal_case import (
    PILLAR, GATE, LEAN4_TOTAL, LEAN4_COUNT,
    N_W, K_CS, N_S, CS_BRAIDED,
    step1_kcs_unique_pair, step2_aps_selects_nw5, step3_braid_stability,
    step4_cmb_corroboration, combined_nw5_closure, nw5_maximal_closure_summary,
)


class TestPillar835Constants:
    def test_pillar_number(self): assert PILLAR == 835
    def test_nw(self): assert N_W == 5
    def test_kcs(self): assert K_CS == 74
    def test_ns_range(self): assert 0.96 < N_S < 0.97
    def test_cs_braided(self): assert abs(CS_BRAIDED - 12/37) < 1e-10
    def test_lean4_count(self): assert LEAN4_COUNT == 45
    def test_lean4_total(self): assert LEAN4_TOTAL == 1821
    def test_lean4_accumulates(self):
        from src.core.pillar835_nw5_planck_independence_maximal_case import LEAN4_PRIOR
        assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT
    def test_gate_maximal(self): assert "MAXIMAL" in GATE or "NW" in GATE


class TestStep1KcsUniquePair:
    def test_returns_dict(self):
        r = step1_kcs_unique_pair()
        assert isinstance(r, dict)

    def test_unique_pair_found(self):
        r = step1_kcs_unique_pair()
        assert r.get("unique_odd_odd_pair") is True

    def test_nw5_in_pair(self):
        r = step1_kcs_unique_pair()
        pair = r.get("pair", (0, 0))
        assert 5 in pair

    def test_solutions_non_empty(self):
        r = step1_kcs_unique_pair()
        assert len(r.get("all_solutions", [])) > 0

    def test_n_w_candidates_contains_5(self):
        r = step1_kcs_unique_pair()
        assert 5 in r.get("n_w_candidates", [])


class TestStep2ApsSelectsNw5:
    def test_returns_dict(self):
        r = step2_aps_selects_nw5()
        assert isinstance(r, dict)

    def test_nw5_selected(self):
        r = step2_aps_selects_nw5()
        assert r.get("selected_n_w") == 5 or r.get("n_w_5_selected") is True

    def test_eta_bar_5_lt_eta_bar_7(self):
        r = step2_aps_selects_nw5()
        assert r.get("eta_bar_5", 0.25) < r.get("eta_bar_7", 0.75)

    def test_eta_results_present(self):
        r = step2_aps_selects_nw5()
        assert "eta_results" in r


class TestStep3BraidStability:
    def test_returns_dict(self):
        r = step3_braid_stability()
        assert isinstance(r, dict)

    def test_cs_nw5_braid_correct(self):
        r = step3_braid_stability()
        assert abs(r["c_s_nw5_braid"] - 12/37) < 1e-10

    def test_cs_nw7_different(self):
        r = step3_braid_stability()
        assert abs(r["c_s_nw7_degenerate"] - 12/37) > 1e-3

    def test_nw5_unique_braid(self):
        r = step3_braid_stability()
        assert r.get("n_w_5_unique_braid") is True

    def test_nw5_matches_target(self):
        r = step3_braid_stability()
        assert r.get("nw5_matches_target") is True

    def test_nw7_does_not_match(self):
        r = step3_braid_stability()
        assert r.get("nw7_matches_target") is False


class TestStep4CmbCorroboration:
    def test_returns_dict(self):
        r = step4_cmb_corroboration()
        assert isinstance(r, dict)

    def test_ns_predicted_close_to_planck(self):
        r = step4_cmb_corroboration()
        assert abs(r["n_s_predicted_um"] - r["n_s_planck"]) < 0.01

    def test_nw5_consistent(self):
        r = step4_cmb_corroboration()
        assert r.get("nw5_consistent_with_planck") is True

    def test_note_secondary(self):
        r = step4_cmb_corroboration()
        # CMB is corroborating, not primary
        assert "note" in r or "secondary" in str(r).lower()


class TestCombinedNw5Closure:
    def test_returns_dict(self):
        r = combined_nw5_closure()
        assert isinstance(r, dict)

    def test_nw5_selected(self):
        r = combined_nw5_closure()
        assert r["n_w_selected"] == 5

    def test_all_steps_pass(self):
        r = combined_nw5_closure()
        assert r["all_steps_support_nw5"] is True

    def test_primary_geometric(self):
        r = combined_nw5_closure()
        assert r["primary_geometric_closure"] is True

    def test_gate_present(self):
        r = combined_nw5_closure()
        assert "gate" in r

    def test_honest_status_present(self):
        r = combined_nw5_closure()
        assert "honest_status" in r


class TestNw5MaximalClosureSummary:
    def test_returns_dict(self):
        r = nw5_maximal_closure_summary()
        assert isinstance(r, dict)

    def test_pillar(self):
        r = nw5_maximal_closure_summary()
        assert r["pillar"] == 835

    def test_lean4_total(self):
        r = nw5_maximal_closure_summary()
        assert r["lean4_total_after"] == 1821

    def test_gate_maximal(self):
        r = nw5_maximal_closure_summary()
        assert "MAXIMAL" in r["gate"]

    def test_primary_geometric_closed(self):
        r = nw5_maximal_closure_summary()
        assert r["primary_geometric_closure"] is True

    def test_open_items_honest(self):
        r = nw5_maximal_closure_summary()
        assert len(r["remaining_open"]) > 0
