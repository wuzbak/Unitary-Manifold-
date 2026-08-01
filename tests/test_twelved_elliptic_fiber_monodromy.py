# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 572: Anchor B — Elliptic Fiber Monodromy → n_w=5 Probe.

src/twelved/elliptic_fiber_monodromy.py — 🔵 ADJACENT TRACK
"""

from __future__ import annotations

import pytest

from src.twelved.elliptic_fiber_monodromy import (
    DISCRIMINANT_ORDER,
    EPISTEMIC_STATUS,
    FIBER_INDEX,
    GAUGE_GROUP,
    K_CS,
    KODAIRA_TABLE,
    KODAIRA_TYPE,
    MONODROMY_PERIOD,
    N2_BRAID,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    aps_discriminator_compatibility,
    axiomzero_seed_purity_check,
    k_cs_braid_decomposition,
    kill_switch_check,
    kodaira_classification,
    monodromy_matrix_i_n,
    monodromy_period_check,
    monodromy_summary,
    sl2z_braid_non_commutativity,
    su5_fiber_consistency,
)


# ---------------------------------------------------------------------------
# Metadata constants
# ---------------------------------------------------------------------------

class TestMetadataConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 572

    def test_pillar_status(self):
        assert "ADJACENT" in PILLAR_STATUS

    def test_epistemic_status(self):
        assert EPISTEMIC_STATUS == "ADJACENT_TRACK"

    def test_title_nonempty(self):
        assert len(PILLAR_TITLE) > 10

    def test_kodaira_type(self):
        assert KODAIRA_TYPE == "I_5"

    def test_gauge_group(self):
        assert GAUGE_GROUP == "SU(5)"

    def test_fiber_index(self):
        assert FIBER_INDEX == 5

    def test_monodromy_period(self):
        assert MONODROMY_PERIOD == 5

    def test_discriminant_order(self):
        assert DISCRIMINANT_ORDER == 5

    def test_n_w(self):
        assert N_W == 5

    def test_n2_braid(self):
        assert N2_BRAID == 7

    def test_k_cs(self):
        assert K_CS == 74


# ---------------------------------------------------------------------------
# monodromy_matrix_i_n
# ---------------------------------------------------------------------------

class TestMonodromyMatrixIN:
    def test_i5_matrix(self):
        m = monodromy_matrix_i_n(5)
        assert m == [[1, 5], [0, 1]]

    def test_i7_matrix(self):
        m = monodromy_matrix_i_n(7)
        assert m == [[1, 7], [0, 1]]

    def test_i1_matrix(self):
        m = monodromy_matrix_i_n(1)
        assert m == [[1, 1], [0, 1]]

    def test_shape_2x2(self):
        m = monodromy_matrix_i_n(3)
        assert len(m) == 2
        assert len(m[0]) == 2

    def test_top_left_always_1(self):
        for n in [1, 2, 3, 5, 7, 10]:
            m = monodromy_matrix_i_n(n)
            assert m[0][0] == 1

    def test_bottom_row_zero_one(self):
        for n in [1, 5, 7]:
            m = monodromy_matrix_i_n(n)
            assert m[1][0] == 0
            assert m[1][1] == 1

    def test_off_diagonal_equals_n(self):
        for n in [2, 3, 5, 6, 7, 9]:
            m = monodromy_matrix_i_n(n)
            assert m[0][1] == n

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            monodromy_matrix_i_n(0)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            monodromy_matrix_i_n(-1)


# ---------------------------------------------------------------------------
# monodromy_period_check
# ---------------------------------------------------------------------------

class TestMonodromyPeriodCheck:
    def test_i5_matches_nw5(self):
        r = monodromy_period_check(n=5, n_w=5)
        assert r["pass"] is True

    def test_default_passes(self):
        r = monodromy_period_check()
        assert r["pass"] is True

    def test_i7_does_not_match_nw5(self):
        r = monodromy_period_check(n=7, n_w=5)
        assert r["pass"] is False

    def test_off_diagonal_entry(self):
        r = monodromy_period_check(n=5, n_w=5)
        assert r["off_diagonal_entry"] == 5

    def test_honest_note_present(self):
        r = monodromy_period_check()
        assert "circular" in r["honest_note"].lower() or "coincidence" in r["honest_note"].lower()

    def test_evidence_string(self):
        r = monodromy_period_check()
        assert len(r["evidence"]) > 0


# ---------------------------------------------------------------------------
# sl2z_braid_non_commutativity
# ---------------------------------------------------------------------------

class TestSL2ZBraidNonCommutativity:
    def test_5_7_inequivalent(self):
        r = sl2z_braid_non_commutativity(n_w=5, n2=7)
        assert r["inequivalent_as_gauge_groups"] is True
        assert r["pass"] is True

    def test_equal_fails(self):
        r = sl2z_braid_non_commutativity(n_w=5, n2=5)
        assert r["pass"] is False

    def test_both_parabolic(self):
        r = sl2z_braid_non_commutativity()
        assert r["both_parabolic"] is True
        assert r["trace_nw"] == 2
        assert r["trace_n2"] == 2

    def test_ranks_different(self):
        r = sl2z_braid_non_commutativity()
        assert r["rank_su_nw"] != r["rank_su_n2"]

    def test_rank_su5(self):
        r = sl2z_braid_non_commutativity()
        assert r["rank_su_nw"] == 4  # SU(5) rank = 4

    def test_rank_su7(self):
        r = sl2z_braid_non_commutativity()
        assert r["rank_su_n2"] == 6  # SU(7) rank = 6


# ---------------------------------------------------------------------------
# kodaira_classification
# ---------------------------------------------------------------------------

class TestKodairaClassification:
    def test_i5_known(self):
        r = kodaira_classification("I_5")
        assert r["known"] is True
        assert r["pass"] is True

    def test_i5_gauge_group(self):
        r = kodaira_classification("I_5")
        assert r["gauge_group"] == "SU(5)"

    def test_i5_discriminant_order(self):
        r = kodaira_classification("I_5")
        assert r["ord_delta"] == 5

    def test_i7_gauge_group(self):
        r = kodaira_classification("I_7")
        assert r["gauge_group"] == "SU(7)"

    def test_e8_from_ii_star(self):
        r = kodaira_classification("II*")
        assert r["gauge_group"] == "E_8"
        assert r["rank"] == 8

    def test_unknown_type_fails(self):
        r = kodaira_classification("I_99")
        assert r["known"] is False
        assert r["pass"] is False

    def test_all_table_entries_valid(self):
        for ft in KODAIRA_TABLE:
            r = kodaira_classification(ft)
            assert r["pass"] is True
            assert r["known"] is True


# ---------------------------------------------------------------------------
# su5_fiber_consistency
# ---------------------------------------------------------------------------

class TestSU5FiberConsistency:
    def test_default_passes(self):
        r = su5_fiber_consistency()
        assert r["pass"] is True

    def test_fiber_index_equals_nw(self):
        r = su5_fiber_consistency()
        assert r["fiber_index_equals_nw"] is True

    def test_gauge_su5(self):
        r = su5_fiber_consistency()
        assert r["kodaira_gauge"] == "SU(5)"

    def test_honest_caveat_present(self):
        r = su5_fiber_consistency()
        assert "consistency" in r["honest_caveat"].lower() or "circular" in r["honest_caveat"].lower()

    def test_wrong_fiber_index_fails(self):
        r = su5_fiber_consistency(n_w=5, fiber_index=7)
        assert r["pass"] is False


# ---------------------------------------------------------------------------
# aps_discriminator_compatibility
# ---------------------------------------------------------------------------

class TestAPSDiscriminatorCompatibility:
    def test_default_passes(self):
        r = aps_discriminator_compatibility()
        assert r["pass"] is True

    def test_nw_selected(self):
        r = aps_discriminator_compatibility()
        assert r["nw_selected_by_aps"] is True

    def test_n2_rejected(self):
        r = aps_discriminator_compatibility()
        assert r["n2_rejected_by_aps"] is True

    def test_product_37(self):
        r = aps_discriminator_compatibility()
        assert r["product_k_cs_eta_nw"] == 37.0

    def test_product_n2_zero(self):
        r = aps_discriminator_compatibility()
        assert r["product_k_cs_eta_n2"] == 0.0

    def test_blocking_residual_documented(self):
        r = aps_discriminator_compatibility()
        assert len(r["blocking_residual"]) > 30

    def test_discriminant_orders(self):
        r = aps_discriminator_compatibility()
        assert r["i5_discriminant_order"] == 5
        assert r["i7_discriminant_order"] == 7


# ---------------------------------------------------------------------------
# k_cs_braid_decomposition
# ---------------------------------------------------------------------------

class TestKCSBraidDecomposition:
    def test_default_passes(self):
        r = k_cs_braid_decomposition()
        assert r["pass"] is True

    def test_k_cs_derived_74(self):
        r = k_cs_braid_decomposition()
        assert r["k_cs_derived"] == 74

    def test_squares_sum(self):
        r = k_cs_braid_decomposition()
        assert r["n_w_sq"] == 25
        assert r["n2_sq"] == 49
        assert r["n_w_sq"] + r["n2_sq"] == 74

    def test_matrices_present(self):
        r = k_cs_braid_decomposition()
        assert r["T_nw"] == [[1, 5], [0, 1]]
        assert r["T_n2"] == [[1, 7], [0, 1]]

    def test_wrong_k_cs_fails(self):
        r = k_cs_braid_decomposition(k_cs=100)
        assert r["pass"] is False


# ---------------------------------------------------------------------------
# axiomzero_seed_purity_check
# ---------------------------------------------------------------------------

class TestAxiomZeroSeedPurityCheck:
    def test_passes(self):
        r = axiomzero_seed_purity_check()
        assert r["pass"] is True

    def test_no_pdg(self):
        r = axiomzero_seed_purity_check()
        assert len(r["pdg_inputs"]) == 0

    def test_geometric_inputs(self):
        r = axiomzero_seed_purity_check()
        assert len(r["geometric_inputs"]) >= 5


# ---------------------------------------------------------------------------
# kill_switch_check
# ---------------------------------------------------------------------------

class TestKillSwitchCheck:
    def test_returns_true(self):
        assert kill_switch_check() is True


# ---------------------------------------------------------------------------
# monodromy_summary
# ---------------------------------------------------------------------------

class TestMonodromySummary:
    def test_pillar_number(self):
        r = monodromy_summary()
        assert r["pillar"] == 572

    def test_anchor_b(self):
        r = monodromy_summary()
        assert r["anchor"] == "B"

    def test_kill_switch_pass(self):
        r = monodromy_summary()
        assert r["kill_switch_pass"] is True

    def test_period_matches_nw(self):
        r = monodromy_summary()
        assert r["period_matches_nw"] is True

    def test_braid_inequivalent(self):
        r = monodromy_summary()
        assert r["braid_pair_inequivalent"] is True

    def test_blocking_residuals(self):
        r = monodromy_summary()
        assert len(r["blocking_residuals"]) >= 2

    def test_honest_summary_present(self):
        r = monodromy_summary()
        assert "compatibility" in r["honest_summary"].lower() or "COMPATIBILITY" in r["honest_summary"]

    def test_k_cs_74(self):
        r = monodromy_summary()
        assert r["k_cs"] == 74
