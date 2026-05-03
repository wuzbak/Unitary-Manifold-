# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_final_decoupling_identity.py
========================================
Tests for Pillar 127 — The Final Decoupling Identity.

Covers all six public API functions across ~60 tests.
"""

from __future__ import annotations

import math

import pytest

from src.core.final_decoupling_identity import (
    N_W,
    K_CS,
    PHI0,
    R_KK_M,
    BETA_RAD,
    BETA_DEG,
    N_S,
    R_BRAIDED,
    SCALE_RATIO,
    decoupling_identity_matrix,
    final_summary,
    observable_projection,
    topology_map,
    um_state_vector,
    unitarity_proof,
)


# ---------------------------------------------------------------------------
# TestUmStateVector — 12 tests
# ---------------------------------------------------------------------------

class TestUmStateVector:
    def test_returns_dict(self):
        assert isinstance(um_state_vector(), dict)

    def test_has_key_n_w(self):
        assert "n_w" in um_state_vector()

    def test_has_key_k_cs(self):
        assert "k_cs" in um_state_vector()

    def test_has_key_phi0(self):
        assert "phi0" in um_state_vector()

    def test_has_key_R_kk_m(self):
        assert "R_kk_m" in um_state_vector()

    def test_has_key_beta_rad(self):
        assert "beta_rad" in um_state_vector()

    def test_has_key_n_s(self):
        assert "n_s" in um_state_vector()

    def test_has_key_r(self):
        assert "r" in um_state_vector()

    def test_has_key_state_dimension(self):
        assert "state_dimension" in um_state_vector()

    def test_has_key_n_free_parameters(self):
        assert "n_free_parameters" in um_state_vector()

    def test_has_key_epistemic_status(self):
        assert "epistemic_status" in um_state_vector()

    def test_n_w_equals_5(self):
        assert um_state_vector()["n_w"] == 5

    def test_k_cs_equals_74(self):
        assert um_state_vector()["k_cs"] == 74

    def test_phi0_approx_pi_over_4(self):
        assert um_state_vector()["phi0"] == pytest.approx(math.pi / 4, rel=1e-3)

    def test_R_kk_m_equals_constant(self):
        assert um_state_vector()["R_kk_m"] == R_KK_M

    def test_beta_rad_approx(self):
        assert um_state_vector()["beta_rad"] == pytest.approx(BETA_RAD, rel=1e-6)

    def test_state_dimension_equals_5(self):
        assert um_state_vector()["state_dimension"] == 5

    def test_n_free_parameters_equals_0(self):
        assert um_state_vector()["n_free_parameters"] == 0

    def test_n_s_equals_constant(self):
        assert um_state_vector()["n_s"] == N_S

    def test_r_equals_constant(self):
        assert um_state_vector()["r"] == R_BRAIDED

    def test_epistemic_status_is_nonempty_string(self):
        es = um_state_vector()["epistemic_status"]
        assert isinstance(es, str) and len(es) > 0


# ---------------------------------------------------------------------------
# TestTopologyMap — 12 tests
# ---------------------------------------------------------------------------

class TestTopologyMap:
    def _topo(self):
        return topology_map(um_state_vector())

    def test_returns_dict(self):
        assert isinstance(self._topo(), dict)

    def test_has_key_e2_twist_deg(self):
        assert "e2_twist_deg" in self._topo()

    def test_has_key_holonomy_group(self):
        assert "holonomy_group" in self._topo()

    def test_has_key_holonomy_angle_deg(self):
        assert "holonomy_angle_deg" in self._topo()

    def test_has_key_scale_ratio_kk_to_topo(self):
        assert "scale_ratio_kk_to_topo" in self._topo()

    def test_has_key_compact_dim_m(self):
        assert "compact_dim_m" in self._topo()

    def test_has_key_macroscopic_topology(self):
        assert "macroscopic_topology" in self._topo()

    def test_has_key_microscopic_bc(self):
        assert "microscopic_bc" in self._topo()

    def test_has_key_parity_violation(self):
        assert "parity_violation" in self._topo()

    def test_has_key_um_state_n_w(self):
        assert "um_state_n_w" in self._topo()

    def test_has_key_um_state_k_cs(self):
        assert "um_state_k_cs" in self._topo()

    def test_e2_twist_deg_equals_180(self):
        assert self._topo()["e2_twist_deg"] == 180.0

    def test_holonomy_group_is_Z2(self):
        assert self._topo()["holonomy_group"] == "Z\u2082"

    def test_macroscopic_topology_is_E2(self):
        assert self._topo()["macroscopic_topology"] == "E2"

    def test_microscopic_bc(self):
        assert self._topo()["microscopic_bc"] == "S\u00b9/Z\u2082"

    def test_parity_violation_is_bool_true(self):
        pv = self._topo()["parity_violation"]
        assert isinstance(pv, bool)
        assert pv is True

    def test_um_state_n_w_equals_5(self):
        assert self._topo()["um_state_n_w"] == 5

    def test_um_state_k_cs_equals_74(self):
        assert self._topo()["um_state_k_cs"] == 74

    def test_scale_ratio_greater_than_1e60(self):
        assert self._topo()["scale_ratio_kk_to_topo"] > 1e60

    def test_raises_value_error_if_n_w_missing(self):
        state = um_state_vector()
        del state["n_w"]
        with pytest.raises(ValueError):
            topology_map(state)


# ---------------------------------------------------------------------------
# TestObservableProjection — 10 tests
# ---------------------------------------------------------------------------

class TestObservableProjection:
    def _obs(self):
        return observable_projection(topology_map(um_state_vector()))

    def test_returns_dict(self):
        assert isinstance(self._obs(), dict)

    def test_has_key_n_s(self):
        assert "n_s" in self._obs()

    def test_has_key_r(self):
        assert "r" in self._obs()

    def test_has_key_beta_cmb_deg(self):
        assert "beta_cmb_deg" in self._obs()

    def test_has_key_beta_gw_deg(self):
        assert "beta_gw_deg" in self._obs()

    def test_has_key_lambda_m2(self):
        assert "lambda_m2" in self._obs()

    def test_has_key_w_dark_energy(self):
        assert "w_dark_energy" in self._obs()

    def test_has_key_tb_nonzero(self):
        assert "tb_nonzero" in self._obs()

    def test_has_key_eb_nonzero(self):
        assert "eb_nonzero" in self._obs()

    def test_has_key_odd_l_deficit(self):
        assert "odd_l_deficit" in self._obs()

    def test_has_key_gw_chirality(self):
        assert "gw_chirality" in self._obs()

    def test_has_key_n_observables(self):
        assert "n_observables" in self._obs()

    def test_has_key_all_from_topology(self):
        assert "all_from_topology" in self._obs()

    def test_n_s_equals_constant(self):
        assert self._obs()["n_s"] == N_S

    def test_r_equals_constant(self):
        assert self._obs()["r"] == R_BRAIDED

    def test_beta_cmb_deg_equals_constant(self):
        assert self._obs()["beta_cmb_deg"] == BETA_DEG

    def test_n_observables_equals_10(self):
        assert self._obs()["n_observables"] == 10

    def test_w_dark_energy_equals_minus_one(self):
        assert self._obs()["w_dark_energy"] == -1.0

    def test_tb_nonzero_is_bool_true(self):
        tb = self._obs()["tb_nonzero"]
        assert isinstance(tb, bool)
        assert tb is True

    def test_all_from_topology_is_bool_true(self):
        aft = self._obs()["all_from_topology"]
        assert isinstance(aft, bool)
        assert aft is True

    def test_raises_value_error_if_e2_twist_missing(self):
        topo = topology_map(um_state_vector())
        del topo["e2_twist_deg"]
        with pytest.raises(ValueError):
            observable_projection(topo)


# ---------------------------------------------------------------------------
# TestDecouplingIdentityMatrix — 12 tests
# ---------------------------------------------------------------------------

class TestDecouplingIdentityMatrix:
    def _mat(self):
        return decoupling_identity_matrix()

    def test_returns_dict(self):
        assert isinstance(self._mat(), dict)

    def test_matrix_dimension_equals_5(self):
        assert self._mat()["matrix_dimension"] == 5

    def test_rank_equals_5(self):
        assert self._mat()["rank"] == 5

    def test_unitarity_measure_equals_1(self):
        assert self._mat()["unitarity_measure"] == pytest.approx(1.0)

    def test_determinant_sign_equals_1(self):
        assert self._mat()["determinant_sign"] == 1

    def test_diagonal_is_bool_true(self):
        d = self._mat()["diagonal"]
        assert isinstance(d, bool)
        assert d is True

    def test_n_state_dof_equals_5(self):
        assert self._mat()["n_state_dof"] == 5

    def test_n_observables_equals_10(self):
        assert self._mat()["n_observables"] == 10

    def test_redundancy_factor_equals_2(self):
        assert self._mat()["redundancy_factor"] == pytest.approx(2.0)

    def test_information_preserved_is_bool_true(self):
        ip = self._mat()["information_preserved"]
        assert isinstance(ip, bool)
        assert ip is True

    def test_bijection_proof_is_nonempty_string(self):
        bp = self._mat()["bijection_proof"]
        assert isinstance(bp, str) and len(bp) > 0

    def test_pillar_equals_127(self):
        assert self._mat()["pillar"] == 127

    def test_type_of_diagonal_is_bool(self):
        assert type(self._mat()["diagonal"]) is bool


# ---------------------------------------------------------------------------
# TestUnitarityProof — 8 tests
# ---------------------------------------------------------------------------

class TestUnitarityProof:
    def _proof(self):
        return unitarity_proof()

    def test_returns_list(self):
        assert isinstance(self._proof(), list)

    def test_length_at_least_6(self):
        assert len(self._proof()) >= 6

    def test_each_item_is_dict(self):
        for item in self._proof():
            assert isinstance(item, dict)

    def test_each_dict_has_step_key(self):
        for item in self._proof():
            assert "step" in item

    def test_each_dict_has_title_key(self):
        for item in self._proof():
            assert "title" in item

    def test_each_dict_has_statement_key(self):
        for item in self._proof():
            assert "statement" in item

    def test_steps_numbered_sequentially_from_1(self):
        steps = [item["step"] for item in self._proof()]
        assert steps == list(range(1, len(steps) + 1))

    def test_all_titles_nonempty(self):
        for item in self._proof():
            assert isinstance(item["title"], str) and len(item["title"]) > 0

    def test_all_statements_nonempty(self):
        for item in self._proof():
            assert isinstance(item["statement"], str) and len(item["statement"]) > 0

    def test_step_1_mentions_state_or_dof(self):
        step1 = self._proof()[0]["statement"].lower()
        assert "state" in step1 or "dof" in step1

    def test_last_step_mentions_unitary_or_information_or_bijection(self):
        last = self._proof()[-1]["statement"].lower()
        assert (
            "unitary" in last
            or "information" in last
            or "bijection" in last
        )


# ---------------------------------------------------------------------------
# TestFinalSummary — 6 tests (expanded to cover spec)
# ---------------------------------------------------------------------------

class TestFinalSummary:
    def _fs(self):
        return final_summary()

    def test_returns_dict(self):
        assert isinstance(self._fs(), dict)

    def test_pillar_equals_127(self):
        assert self._fs()["pillar"] == 127

    def test_total_pillars_equals_127(self):
        assert self._fs()["total_pillars"] == 127

    def test_phase_1_pillars(self):
        assert self._fs()["phase_1_pillars"] == [117, 118, 119, 120]

    def test_phase_2_pillars(self):
        assert self._fs()["phase_2_pillars"] == [121, 122, 123]

    def test_phase_3_pillars(self):
        assert self._fs()["phase_3_pillars"] == [124, 125, 126]

    def test_final_pillar_equals_127(self):
        assert self._fs()["final_pillar"] == 127

    def test_predictions_is_dict(self):
        assert isinstance(self._fs()["predictions"], dict)

    def test_predictions_count_equals_10(self):
        assert self._fs()["predictions_count"] == 10

    def test_primary_falsifier_is_nonempty_string(self):
        pf = self._fs()["primary_falsifier"]
        assert isinstance(pf, str) and len(pf) > 0

    def test_litebird_launch_equals_2032(self):
        assert self._fs()["litebird_launch"] == 2032

    def test_epistemic_status_contains_127(self):
        es = self._fs()["epistemic_status"]
        assert "127" in es
