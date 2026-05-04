# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_chiral_fermion_orbifold.py
=======================================
Pillar 154 — Tests for chiral_fermion_orbifold.py.

Tests cover:
  - Constants: N_W, N_EVEN, N_ODD, N_GENERATIONS, SM_HYPERCHARGES
  - witten_obstruction_check(): 3 conditions all violated by orbifold
  - su5_10rep_decomposition(): Q_L, u_R^c, e_R^c from UV brane
  - su5_5bar_decomposition(): d_R^c, L from IR brane
  - hypercharge_from_su5(): exact SM hypercharges
  - three_generation_count(): n_w=5 → 3 generations
  - chiral_bc_zero_modes(): boundary condition chirality selection
  - sm_matter_content_summary(): complete SM matter table
  - chiral_fermion_closure_status(): full closure status
  - pillar154_summary(): audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.chiral_fermion_orbifold import (
    N_W,
    N_EVEN,
    N_ODD,
    N_GENERATIONS,
    M_GUT_GEV,
    HYPERCHARGE_NORM,
    SM_HYPERCHARGES,
    witten_obstruction_check,
    su5_10rep_decomposition,
    su5_5bar_decomposition,
    hypercharge_from_su5,
    three_generation_count,
    chiral_bc_zero_modes,
    sm_matter_content_summary,
    chiral_fermion_closure_status,
    pillar154_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_n_even_is_3(self):
        """⌈5/2⌉ = 3"""
        assert N_EVEN == 3

    def test_n_odd_is_2(self):
        """⌊5/2⌋ = 2"""
        assert N_ODD == 2

    def test_n_even_plus_n_odd_equals_n_w(self):
        assert N_EVEN + N_ODD == N_W

    def test_n_generations_is_3(self):
        assert N_GENERATIONS == 3

    def test_m_gut_gev_order(self):
        assert 1e15 < M_GUT_GEV < 1e17

    def test_hypercharge_norm_sqrt_3_over_5(self):
        assert abs(HYPERCHARGE_NORM - math.sqrt(3.0 / 5.0)) < 1e-12

    def test_hypercharge_q_l(self):
        assert abs(SM_HYPERCHARGES["Q_L"] - 1.0 / 6.0) < 1e-12

    def test_hypercharge_u_r_c(self):
        assert abs(SM_HYPERCHARGES["u_R_c"] - (-2.0 / 3.0)) < 1e-12

    def test_hypercharge_e_r_c(self):
        assert abs(SM_HYPERCHARGES["e_R_c"] - 1.0) < 1e-12

    def test_hypercharge_d_r_c(self):
        assert abs(SM_HYPERCHARGES["d_R_c"] - 1.0 / 3.0) < 1e-12

    def test_hypercharge_l(self):
        assert abs(SM_HYPERCHARGES["L"] - (-1.0 / 2.0)) < 1e-12

    def test_all_sm_hypercharges_present(self):
        expected = {"Q_L", "u_R_c", "e_R_c", "d_R_c", "L"}
        assert set(SM_HYPERCHARGES.keys()) == expected


# ---------------------------------------------------------------------------
# Witten obstruction check
# ---------------------------------------------------------------------------

class TestWittenObstructionCheck:
    def setup_method(self):
        self.result = witten_obstruction_check()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_witten_does_not_apply(self):
        assert self.result["witten_applies_to_su5_z2_orbifold"] is False

    def test_witten_obstruction_resolved(self):
        assert self.result["witten_obstruction_resolved"] is True

    def test_three_conditions_checked(self):
        assert len(self.result["conditions_checked"]) == 3

    def test_all_conditions_violated(self):
        assert len(self.result["conditions_violated"]) == 3

    def test_condition_c1_violated(self):
        assert "C1" in self.result["conditions_violated"]

    def test_condition_c2_violated(self):
        assert "C2" in self.result["conditions_violated"]

    def test_condition_c3_violated(self):
        assert "C3" in self.result["conditions_violated"]

    def test_each_condition_has_reason(self):
        for cond in self.result["conditions_checked"]:
            assert "reason" in cond
            assert len(cond["reason"]) > 20

    def test_c1_smooth_manifold_violated(self):
        c1 = next(c for c in self.result["conditions_checked"]
                   if c["condition"] == "C1")
        assert not c1["applies_to_su5_z2"]

    def test_c2_continuous_group_violated(self):
        c2 = next(c for c in self.result["conditions_checked"]
                   if c["condition"] == "C2")
        assert not c2["applies_to_su5_z2"]

    def test_c3_bulk_eom_violated(self):
        c3 = next(c for c in self.result["conditions_checked"]
                   if c["condition"] == "C3")
        assert not c3["applies_to_su5_z2"]

    def test_conclusion_string_nonempty(self):
        assert len(self.result["conclusion"]) > 50


# ---------------------------------------------------------------------------
# SU(5) 10-representation decomposition
# ---------------------------------------------------------------------------

class TestSU5TenRepDecomposition:
    def setup_method(self):
        self.result = su5_10rep_decomposition()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_rep_is_10(self):
        assert self.result["su5_dim"] == 10

    def test_uv_brane_origin(self):
        assert "UV brane" in self.result["orbifold_fixed_point"].lower() or \
               "y = 0" in self.result["orbifold_fixed_point"]

    def test_three_sm_components_in_decomposition(self):
        # Q_L, u_R^c, e_R^c → 3 zero-mode entries (plus X/Y)
        assert len(self.result["sm_decomposition"]) >= 3

    def test_q_l_present(self):
        fields = [f["sm_field"] for f in self.result["sm_decomposition"]]
        assert any("Q_L" in f for f in fields)

    def test_u_r_c_present(self):
        fields = [f["sm_field"] for f in self.result["sm_decomposition"]]
        assert any("u_R" in f for f in fields)

    def test_e_r_c_present(self):
        fields = [f["sm_field"] for f in self.result["sm_decomposition"]]
        assert any("e_R" in f for f in fields)

    def test_q_l_hypercharge(self):
        q_l = next(f for f in self.result["sm_decomposition"]
                    if f["sm_field"] == "Q_L")
        assert abs(q_l["hypercharge_Y"] - 1.0 / 6.0) < 1e-10

    def test_u_r_c_hypercharge(self):
        u_r = next(f for f in self.result["sm_decomposition"]
                    if f["sm_field"] == "u_R^c")
        assert abs(u_r["hypercharge_Y"] - (-2.0 / 3.0)) < 1e-10

    def test_e_r_c_hypercharge(self):
        e_r = next(f for f in self.result["sm_decomposition"]
                    if f["sm_field"] == "e_R^c")
        assert abs(e_r["hypercharge_Y"] - 1.0) < 1e-10

    def test_q_l_has_zero_mode(self):
        q_l = next(f for f in self.result["sm_decomposition"]
                    if f["sm_field"] == "Q_L")
        assert q_l["zero_mode"] is True

    def test_xy_bosons_no_zero_mode(self):
        xy = next(f for f in self.result["sm_decomposition"]
                   if "X/Y" in f["sm_field"] or "X" in f["sm_field"])
        assert xy["zero_mode"] is False

    def test_zero_mode_count_is_3(self):
        assert self.result["zero_mode_count"] == 3

    def test_n_generations_is_3(self):
        assert self.result["n_generations"] == 3

    def test_total_zero_modes(self):
        assert self.result["total_zero_modes"] == 3 * 3  # 3 fields × 3 gen


# ---------------------------------------------------------------------------
# SU(5) 5̄-representation decomposition
# ---------------------------------------------------------------------------

class TestSU5FiveBarDecomposition:
    def setup_method(self):
        self.result = su5_5bar_decomposition()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_rep_is_5bar(self):
        assert self.result["su5_dim"] == 5

    def test_ir_brane_origin(self):
        assert "IR brane" in self.result["orbifold_fixed_point"] or \
               "πR" in self.result["orbifold_fixed_point"]

    def test_d_r_c_present(self):
        fields = [f["sm_field"] for f in self.result["sm_decomposition"]]
        assert any("d_R" in f for f in fields)

    def test_l_present(self):
        fields = [f["sm_field"] for f in self.result["sm_decomposition"]]
        assert any(f == "L" for f in fields)

    def test_d_r_c_hypercharge(self):
        d_r = next(f for f in self.result["sm_decomposition"]
                    if f["sm_field"] == "d_R^c")
        assert abs(d_r["hypercharge_Y"] - 1.0 / 3.0) < 1e-10

    def test_l_hypercharge(self):
        l_field = next(f for f in self.result["sm_decomposition"]
                        if f["sm_field"] == "L")
        assert abs(l_field["hypercharge_Y"] - (-1.0 / 2.0)) < 1e-10

    def test_colour_triplet_higgs_no_zero_mode(self):
        higgs_triplet = next(
            f for f in self.result["sm_decomposition"]
            if "triplet" in f["sm_field"].lower() or "Higgs" in f["sm_field"]
        )
        assert higgs_triplet["zero_mode"] is False

    def test_zero_mode_count_is_2(self):
        assert self.result["zero_mode_count"] == 2

    def test_doublet_triplet_splitting_mentioned(self):
        triplet = next(
            f for f in self.result["sm_decomposition"]
            if not f["zero_mode"]
        )
        assert "mass" in triplet["description"].lower() or \
               "GUT" in triplet["description"] or \
               "splitting" in triplet["description"]


# ---------------------------------------------------------------------------
# Hypercharge computation
# ---------------------------------------------------------------------------

class TestHyperchargeFromSU5:
    def test_q_l_from_10(self):
        Y = hypercharge_from_su5("10", "Q_L")
        assert abs(Y - 1.0 / 6.0) < 1e-12

    def test_u_r_c_from_10(self):
        Y = hypercharge_from_su5("10", "u_R_c")
        assert abs(Y - (-2.0 / 3.0)) < 1e-12

    def test_e_r_c_from_10(self):
        Y = hypercharge_from_su5("10", "e_R_c")
        assert abs(Y - 1.0) < 1e-12

    def test_d_r_c_from_5bar(self):
        Y = hypercharge_from_su5("5bar", "d_R_c")
        assert abs(Y - 1.0 / 3.0) < 1e-12

    def test_l_from_5bar(self):
        Y = hypercharge_from_su5("5bar", "L")
        assert abs(Y - (-1.0 / 2.0)) < 1e-12

    def test_invalid_rep_raises(self):
        with pytest.raises(ValueError, match="must be"):
            hypercharge_from_su5("15", "Q_L")

    def test_invalid_component_raises(self):
        with pytest.raises(KeyError):
            hypercharge_from_su5("10", "Higgs")


# ---------------------------------------------------------------------------
# Three-generation count
# ---------------------------------------------------------------------------

class TestThreeGenerationCount:
    def test_n_w_5_gives_3_generations(self):
        result = three_generation_count(5)
        assert result["n_generations_derived"] == 3

    def test_matches_observed(self):
        result = three_generation_count(5)
        assert result["matches_observed"] is True

    def test_n_z2_even_is_3(self):
        result = three_generation_count(5)
        assert result["n_z2_even_modes"] == 3

    def test_n_z2_odd_is_2(self):
        result = three_generation_count(5)
        assert result["n_z2_odd_modes"] == 2

    def test_n_w_1_gives_1_generation(self):
        result = three_generation_count(1)
        assert result["n_generations_derived"] == 1

    def test_n_w_3_gives_2_generations(self):
        result = three_generation_count(3)
        assert result["n_generations_derived"] == 2

    def test_n_w_7_gives_4_generations(self):
        result = three_generation_count(7)
        assert result["n_generations_derived"] == 4

    def test_invalid_n_w_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            three_generation_count(0)

    def test_negative_n_w_raises(self):
        with pytest.raises(ValueError):
            three_generation_count(-1)

    def test_derivation_string_nonempty(self):
        result = three_generation_count(5)
        assert len(result["derivation"]) > 20

    def test_mode_count_sums_to_n_w(self):
        for n_w in [3, 5, 7, 9]:
            result = three_generation_count(n_w)
            assert result["n_z2_even_modes"] + result["n_z2_odd_modes"] == n_w


# ---------------------------------------------------------------------------
# Boundary condition chirality selection
# ---------------------------------------------------------------------------

class TestChiralBCZeroModes:
    def test_even_parity_gives_left_handed(self):
        result = chiral_bc_zero_modes("even", c_bulk=0.6)
        assert result["psi_L_zero_mode"] is True
        assert result["psi_R_zero_mode"] is False

    def test_odd_parity_gives_right_handed(self):
        result = chiral_bc_zero_modes("odd", c_bulk=0.6)
        assert result["psi_L_zero_mode"] is False
        assert result["psi_R_zero_mode"] is True

    def test_even_parity_active_chirality(self):
        result = chiral_bc_zero_modes("even")
        assert result["active_chirality"] == "left-handed"

    def test_odd_parity_active_chirality(self):
        result = chiral_bc_zero_modes("odd")
        assert result["active_chirality"] == "right-handed"

    def test_neumann_bc_for_even_psi_l(self):
        result = chiral_bc_zero_modes("even")
        assert result["psi_L_bc"] == "Neumann"
        assert result["psi_R_bc"] == "Dirichlet"

    def test_dirichlet_bc_for_odd_psi_l(self):
        result = chiral_bc_zero_modes("odd")
        assert result["psi_L_bc"] == "Dirichlet"
        assert result["psi_R_bc"] == "Neumann"

    def test_invalid_parity_raises(self):
        with pytest.raises(ValueError, match="must be"):
            chiral_bc_zero_modes("both")

    def test_invalid_pi_kr_raises(self):
        with pytest.raises(ValueError, match="positive"):
            chiral_bc_zero_modes("even", pi_kr=-1.0)

    def test_uv_localised_c_bulk(self):
        """c_bulk = 0.8 > 0.5 → UV-localised."""
        result = chiral_bc_zero_modes("even", c_bulk=0.8)
        assert result["psi_L_zero_mode"] is True

    def test_ir_localised_c_bulk(self):
        """c_bulk = 0.2 < 0.5 → IR-localised."""
        result = chiral_bc_zero_modes("even", c_bulk=0.2)
        assert result["psi_L_zero_mode"] is True  # still zero mode, just IR-peaked

    def test_conclusion_nonempty(self):
        result = chiral_bc_zero_modes("even")
        assert len(result["conclusion"]) > 20


# ---------------------------------------------------------------------------
# SM matter content summary
# ---------------------------------------------------------------------------

class TestSmMatterContentSummary:
    def setup_method(self):
        self.result = sm_matter_content_summary(3)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_n_generations(self):
        assert self.result["n_generations"] == 3

    def test_n_w_source_is_5(self):
        assert self.result["n_w_source"] == 5

    def test_five_sm_fields_per_generation(self):
        # Q_L, u_R^c, e_R^c from 10 + d_R^c, L from 5̄
        assert self.result["total_sm_matter_fields"] == 5

    def test_fields_from_10_count(self):
        assert len(self.result["fields_from_10rep"]) == 3 * 3  # 3 fields × 3 gen

    def test_fields_from_5bar_count(self):
        assert len(self.result["fields_from_5bar_rep"]) == 2 * 3  # 2 fields × 3 gen

    def test_dof_per_generation_is_15(self):
        # Q_L(6) + u_R^c(3) + e_R^c(1) + d_R^c(3) + L(2) = 15
        assert self.result["dof_per_generation"] == 15

    def test_total_dof(self):
        assert self.result["total_fermionic_dof"] == 15 * 3  # = 45

    def test_anomaly_free(self):
        assert self.result["hypercharge_check"]["anomaly_free"] is True

    def test_higgs_sector_mentioned(self):
        assert "Higgs" in self.result["higgs_sector"]
        assert "doublet" in self.result["higgs_sector"].lower()

    def test_all_fields_have_hypercharge(self):
        for f in self.result["all_fields"]:
            assert "hypercharge_Y" in f
            assert isinstance(f["hypercharge_Y"], float)

    def test_invalid_n_generations_raises(self):
        with pytest.raises(ValueError, match="positive"):
            sm_matter_content_summary(0)

    def test_generation_numbers_1_to_3(self):
        gen_numbers = {f["generation"] for f in self.result["all_fields"]}
        assert gen_numbers == {1, 2, 3}

    def test_missing_nu_r_noted(self):
        assert "ν" in self.result["missing_fields"] or "nu" in self.result["missing_fields"].lower() or \
               "right-handed" in self.result["missing_fields"].lower()


# ---------------------------------------------------------------------------
# Full closure status
# ---------------------------------------------------------------------------

class TestChiralFermionClosureStatus:
    def setup_method(self):
        self.result = chiral_fermion_closure_status()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_154(self):
        assert self.result["pillar"] == 154

    def test_status_resolved(self):
        assert "✅" in self.result["status"] or "RESOLVED" in self.result["status"]

    def test_witten_resolved(self):
        assert self.result["witten_obstruction"]["witten_obstruction_resolved"] is True

    def test_previous_status_open(self):
        assert "OPEN" in self.result["previous_status"]

    def test_new_status_resolved(self):
        assert "RESOLVED" in self.result["new_status"]

    def test_closure_chain_nonempty(self):
        assert len(self.result["closure_chain"]) > 50

    def test_witten_resolution_explanation(self):
        assert "smooth" in self.result["witten_resolution"].lower() or \
               "Witten" in self.result["witten_resolution"]

    def test_remaining_open_items_list(self):
        assert isinstance(self.result["remaining_open_items"], list)
        assert len(self.result["remaining_open_items"]) >= 2


# ---------------------------------------------------------------------------
# Pillar 154 summary
# ---------------------------------------------------------------------------

class TestPillar154Summary:
    def setup_method(self):
        self.result = pillar154_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_154(self):
        assert self.result["pillar"] == 154

    def test_status_resolved(self):
        assert "RESOLVED" in self.result["status"]

    def test_n_generations_3(self):
        assert self.result["n_generations_from_nw5"] == 3

    def test_generation_match_true(self):
        assert self.result["generation_match"] is True

    def test_witten_resolved_true(self):
        assert self.result["witten_obstruction_resolved"] is True

    def test_sm_fields_from_10(self):
        assert "Q_L" in self.result["sm_fields_from_10"]
        assert "u_R^c" in self.result["sm_fields_from_10"]
        assert "e_R^c" in self.result["sm_fields_from_10"]

    def test_sm_fields_from_5bar(self):
        assert "d_R^c" in self.result["sm_fields_from_5bar"]
        assert "L" in self.result["sm_fields_from_5bar"]

    def test_hypercharges_exact(self):
        hc = self.result["hypercharges_exact"]
        assert abs(hc["Q_L"] - 1.0 / 6.0) < 1e-12
        assert abs(hc["L"] - (-1.0 / 2.0)) < 1e-12

    def test_doublet_triplet_splitting_solved(self):
        assert "SOLVED" in self.result["doublet_triplet_splitting"] or \
               "solved" in self.result["doublet_triplet_splitting"].lower()

    def test_pillar_references_nonempty(self):
        assert len(self.result["pillar_references"]) >= 3

    def test_grand_synthesis_update_nonempty(self):
        assert len(self.result["grand_synthesis_update"]) > 30
