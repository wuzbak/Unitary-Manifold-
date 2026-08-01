# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 570: F-Theory DBP Rung 7 Architecture Scaffold.

src/twelved/ftheory_scaffold.py — 🔵 ADJACENT TRACK
"""

from __future__ import annotations

import pytest

from src.twelved.ftheory_scaffold import (
    ANCHOR,
    CY4_CHI,
    CY4_COMPLEX_DIM,
    CY4_H11,
    CY4_H21,
    CY4_H31,
    CY4_REAL_DIM,
    DIMENSION,
    EPISTEMIC_STATUS,
    HARD_GATE_CHECKS,
    K_CS,
    KILL_SWITCH_PASS,
    MECHANISM,
    N_D3_TADPOLE,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    RUNG_ID,
    SPACETIME_DIM,
    STATUS,
    TARGET_PARAMETER,
    axiomzero_seed_purity_check,
    cy4_dimension_check,
    d3_tadpole_positivity_check,
    euler_char_sign_check,
    evaluate_candidate,
    hard_gate_check,
    hodge_consistency_check,
    kill_switch_check,
    rung7_gate_evidence,
    scaffold_spec,
    topology_braid_link_check,
)


# ---------------------------------------------------------------------------
# Metadata constants
# ---------------------------------------------------------------------------

class TestMetadataConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 570

    def test_rung_id(self):
        assert RUNG_ID == "R7"

    def test_dimension(self):
        assert DIMENSION == "12D"

    def test_epistemic_status_adjacent(self):
        assert EPISTEMIC_STATUS == "ADJACENT_TRACK"

    def test_status(self):
        assert STATUS == "RUNG_SOLID_ARCHITECTURE_TRACK"

    def test_pillar_title_nonempty(self):
        assert len(PILLAR_TITLE) > 10

    def test_anchor_ftheory(self):
        assert "F_theory" in ANCHOR or "CY4" in ANCHOR

    def test_mechanism_contains_t2(self):
        assert "T2" in MECHANISM or "CY4" in MECHANISM

    def test_kill_switch_pass_true(self):
        assert KILL_SWITCH_PASS is True

    def test_hard_gate_checks_nonempty(self):
        assert len(HARD_GATE_CHECKS) == 6


# ---------------------------------------------------------------------------
# CY4 geometry constants
# ---------------------------------------------------------------------------

class TestCY4GeometryConstants:
    def test_cy4_complex_dim(self):
        assert CY4_COMPLEX_DIM == 4

    def test_cy4_real_dim(self):
        assert CY4_REAL_DIM == 8
        assert CY4_REAL_DIM == 2 * CY4_COMPLEX_DIM

    def test_spacetime_dim_12(self):
        assert SPACETIME_DIM == 12
        assert SPACETIME_DIM == 4 + CY4_REAL_DIM

    def test_chi_cy4_value(self):
        assert CY4_CHI == 1_820_160

    def test_chi_cy4_positive(self):
        assert CY4_CHI > 0

    def test_chi_divisible_by_24(self):
        assert CY4_CHI % 24 == 0

    def test_n_d3_tadpole_value(self):
        assert N_D3_TADPOLE == 75_840

    def test_n_d3_equals_chi_over_24(self):
        assert N_D3_TADPOLE == CY4_CHI // 24

    def test_n_d3_positive(self):
        assert N_D3_TADPOLE > 0

    def test_hodge_h11(self):
        assert CY4_H11 == 1

    def test_hodge_h21(self):
        assert CY4_H21 == 0

    def test_hodge_h31(self):
        assert CY4_H31 == 3878

    def test_hodge_h11_nontrivial(self):
        assert CY4_H11 >= 1

    def test_hodge_h31_nontrivial(self):
        assert CY4_H31 >= 1


# ---------------------------------------------------------------------------
# UM braid invariants
# ---------------------------------------------------------------------------

class TestBraidInvariants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs_braid_identity(self):
        assert K_CS == N_W**2 + 7**2


# ---------------------------------------------------------------------------
# cy4_dimension_check
# ---------------------------------------------------------------------------

class TestCY4DimensionCheck:
    def test_default_passes(self):
        r = cy4_dimension_check()
        assert r["pass"] is True

    def test_total_dim_12(self):
        r = cy4_dimension_check()
        assert r["total_dim"] == 12

    def test_real_dim_8(self):
        r = cy4_dimension_check()
        assert r["cy4_real_dim"] == 8

    def test_wrong_complex_dim_fails(self):
        r = cy4_dimension_check(cy4_complex_dim=3)
        assert r["pass"] is False

    def test_complex_dim_3_gives_10d(self):
        r = cy4_dimension_check(cy4_complex_dim=3)
        assert r["total_dim"] == 10  # CY3: 4+6=10

    def test_evidence_string_nonempty(self):
        r = cy4_dimension_check()
        assert isinstance(r["evidence"], str) and len(r["evidence"]) > 0


# ---------------------------------------------------------------------------
# euler_char_sign_check
# ---------------------------------------------------------------------------

class TestEulerCharSignCheck:
    def test_default_passes(self):
        r = euler_char_sign_check()
        assert r["pass"] is True

    def test_positive_chi(self):
        r = euler_char_sign_check(chi_cy4=1000)
        assert r["pass"] is True

    def test_negative_chi_fails(self):
        r = euler_char_sign_check(chi_cy4=-200)
        assert r["pass"] is False

    def test_zero_chi_fails(self):
        r = euler_char_sign_check(chi_cy4=0)
        assert r["pass"] is False

    def test_reference_chi_value(self):
        r = euler_char_sign_check()
        assert r["chi_cy4"] == 1_820_160


# ---------------------------------------------------------------------------
# d3_tadpole_positivity_check
# ---------------------------------------------------------------------------

class TestD3TadpolePositivityCheck:
    def test_default_passes(self):
        r = d3_tadpole_positivity_check()
        assert r["pass"] is True

    def test_n_d3_correct_value(self):
        r = d3_tadpole_positivity_check()
        assert r["n_d3_derived"] == 75_840

    def test_chi_divisible_by_24(self):
        r = d3_tadpole_positivity_check()
        assert r["chi_divisible_by_24"] is True

    def test_mismatched_n_d3_fails(self):
        r = d3_tadpole_positivity_check(chi_cy4=CY4_CHI, n_d3=99999)
        assert r["pass"] is False

    def test_negative_n_d3_fails(self):
        # chi negative → derived n_d3 negative
        r = d3_tadpole_positivity_check(chi_cy4=-240, n_d3=-10)
        assert r["pass"] is False


# ---------------------------------------------------------------------------
# hodge_consistency_check
# ---------------------------------------------------------------------------

class TestHodgeConsistencyCheck:
    def test_default_passes(self):
        r = hodge_consistency_check()
        assert r["pass"] is True

    def test_h11_zero_fails(self):
        r = hodge_consistency_check(h11=0, h21=0, h31=100)
        assert r["pass"] is False

    def test_h31_zero_fails(self):
        r = hodge_consistency_check(h11=1, h21=0, h31=0)
        assert r["pass"] is False

    def test_h11_h31_both_nonzero_passes(self):
        r = hodge_consistency_check(h11=2, h21=5, h31=100)
        assert r["pass"] is True

    def test_reference_hodge_values(self):
        r = hodge_consistency_check()
        assert r["h11"] == 1
        assert r["h31"] == 3878


# ---------------------------------------------------------------------------
# axiomzero_seed_purity_check
# ---------------------------------------------------------------------------

class TestAxiomZeroSeedPurityCheck:
    def test_passes(self):
        r = axiomzero_seed_purity_check()
        assert r["pass"] is True

    def test_no_pdg_inputs(self):
        r = axiomzero_seed_purity_check()
        assert r["n_pdg"] == 0
        assert len(r["pdg_inputs"]) == 0

    def test_geometric_seeds_present(self):
        r = axiomzero_seed_purity_check()
        assert r["n_geometric"] >= 5

    def test_evidence_mentions_geometric(self):
        r = axiomzero_seed_purity_check()
        assert "geometric" in r["evidence"].lower() or "AxiomZero" in r["evidence"]


# ---------------------------------------------------------------------------
# topology_braid_link_check
# ---------------------------------------------------------------------------

class TestTopologyBraidLinkCheck:
    def test_default_passes(self):
        r = topology_braid_link_check()
        assert r["pass"] is True

    def test_k_cs_74(self):
        r = topology_braid_link_check()
        assert r["k_cs_derived"] == 74

    def test_wrong_k_cs_fails(self):
        r = topology_braid_link_check(k_cs=100)
        assert r["pass"] is False

    def test_n_w_5(self):
        r = topology_braid_link_check()
        assert r["n_w"] == 5

    def test_braid_identity(self):
        r = topology_braid_link_check(n_w=5, n2=7, k_cs=74)
        assert r["k_cs_derived"] == 5**2 + 7**2


# ---------------------------------------------------------------------------
# kill_switch_check
# ---------------------------------------------------------------------------

class TestKillSwitchCheck:
    def test_returns_true(self):
        assert kill_switch_check() is True


# ---------------------------------------------------------------------------
# hard_gate_check
# ---------------------------------------------------------------------------

class TestHardGateCheck:
    def test_all_pass(self):
        r = hard_gate_check()
        assert r["all_pass"] is True

    def test_n_checks(self):
        r = hard_gate_check()
        assert r["n_checks"] == 6

    def test_status_correct(self):
        r = hard_gate_check()
        assert r["status"] == "RUNG_SOLID_ARCHITECTURE_TRACK"

    def test_results_is_dict(self):
        r = hard_gate_check()
        assert isinstance(r["results"], dict)
        assert len(r["results"]) == 6


# ---------------------------------------------------------------------------
# rung7_gate_evidence
# ---------------------------------------------------------------------------

class TestRung7GateEvidence:
    def test_pillar_number(self):
        r = rung7_gate_evidence()
        assert r["pillar"] == 570

    def test_kill_switch_pass(self):
        r = rung7_gate_evidence()
        assert r["kill_switch_pass"] is True

    def test_adjacency_note_present(self):
        r = rung7_gate_evidence()
        assert "ADJACENT" in r["adjacency_note"]

    def test_cy4_chi(self):
        r = rung7_gate_evidence()
        assert r["cy4_chi"] == 1_820_160

    def test_n_d3_tadpole(self):
        r = rung7_gate_evidence()
        assert r["n_d3_tadpole"] == 75_840

    def test_spacetime_dim(self):
        r = rung7_gate_evidence()
        assert r["spacetime_dim"] == 12

    def test_k_cs(self):
        r = rung7_gate_evidence()
        assert r["k_cs"] == 74


# ---------------------------------------------------------------------------
# scaffold_spec
# ---------------------------------------------------------------------------

class TestScaffoldSpec:
    def test_rung_id(self):
        s = scaffold_spec()
        assert s["rung_id"] == "R7"

    def test_from_to_dim(self):
        s = scaffold_spec()
        assert s["from_dim"] == "11D"
        assert s["to_dim"] == "12D"

    def test_three_anchors(self):
        s = scaffold_spec()
        assert len(s["open_anchors"]) == 3

    def test_anchor_ids(self):
        s = scaffold_spec()
        ids = [a["id"] for a in s["open_anchors"]]
        assert "A" in ids and "B" in ids and "C" in ids

    def test_cy4_reference_present(self):
        s = scaffold_spec()
        assert "cy4_reference" in s
        assert s["cy4_reference"]["chi"] == 1_820_160

    def test_previous_rung_r6(self):
        s = scaffold_spec()
        assert s["previous_rung"]["id"] == "R6"
        assert s["previous_rung"]["status"] == "RUNG_SOLID"


# ---------------------------------------------------------------------------
# evaluate_candidate
# ---------------------------------------------------------------------------

class TestEvaluateCandidate:
    def test_reference_cy4_passes(self):
        r = evaluate_candidate()
        assert r["all_pass"] is True
        assert r["status"] == "RUNG_SOLID_CANDIDATE"

    def test_wrong_complex_dim_fails(self):
        r = evaluate_candidate(cy4_complex_dim=3, chi_cy4=1_820_160,
                               h11=1, h31=3878, k_cs=74, n_w=5)
        assert r["all_pass"] is False

    def test_negative_chi_fails(self):
        r = evaluate_candidate(cy4_complex_dim=4, chi_cy4=-100,
                               h11=1, h31=3878, k_cs=74, n_w=5)
        assert r["all_pass"] is False

    def test_total_dim_reported(self):
        r = evaluate_candidate()
        assert r["total_dim"] == 12

    def test_n_d3_reported(self):
        r = evaluate_candidate()
        assert r["n_d3"] == 75_840

    def test_wrong_k_cs_fails(self):
        r = evaluate_candidate(cy4_complex_dim=4, chi_cy4=1_820_160,
                               h11=1, h31=3878, k_cs=100, n_w=5)
        assert r["all_pass"] is False
