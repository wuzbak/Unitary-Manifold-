# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_grand_synthesis.py
================================
Tests for Pillar 132 — The Grand Synthesis Identity (Master Action).

~80 tests covering: action components, variational equations, completeness
identity, open gaps, falsifiers, and the full grand synthesis summary.
"""

from __future__ import annotations

import math

import pytest

from src.core.grand_synthesis import (
    K_CS,
    N_W,
    PHI0,
    L_PL_M,
    G_N,
    M_PL_KG,
    N_S,
    R_BRAIDED,
    BETA_DEG,
    LAMBDA_QCD_UM_GEV,
    LAMBDA_QCD_OBS_GEV,
    LAMBDA_QCD_GAP,
    master_action_components,
    vary_wrt_metric,
    vary_wrt_gauge_field,
    vary_wrt_fermion,
    vary_wrt_dilaton,
    completeness_identity,
    grand_synthesis_summary,
)


# ---------------------------------------------------------------------------
# TestConstants — 8 tests
# ---------------------------------------------------------------------------

class TestConstants:
    def test_k_cs_74(self):
        assert K_CS == 74

    def test_n_w_5(self):
        assert N_W == 5

    def test_phi0_pi_over_4(self):
        assert abs(PHI0 - math.pi / 4) < 1e-10

    def test_l_pl_positive(self):
        assert L_PL_M > 0

    def test_n_s_approx_0963(self):
        assert 0.96 < N_S < 0.97

    def test_r_braided_positive(self):
        assert R_BRAIDED > 0

    def test_lambda_qcd_gap_large(self):
        assert LAMBDA_QCD_GAP > 1e6

    def test_lambda_qcd_um_larger_than_obs(self):
        assert LAMBDA_QCD_UM_GEV > LAMBDA_QCD_OBS_GEV


# ---------------------------------------------------------------------------
# TestMasterActionComponents — 16 tests
# ---------------------------------------------------------------------------

class TestMasterActionComponents:
    def test_returns_dict(self):
        assert isinstance(master_action_components(), dict)

    def test_action_name(self):
        assert master_action_components()["action_name"] == "S_UM"

    def test_spacetime_dimension_5(self):
        assert master_action_components()["spacetime_dimension"] == 5

    def test_has_components(self):
        assert "components" in master_action_components()

    def test_has_r5_gravity(self):
        assert "R5_gravity" in master_action_components()["components"]

    def test_has_cs5(self):
        assert "CS5_chern_simons" in master_action_components()["components"]

    def test_has_matter(self):
        assert "L_matter" in master_action_components()["components"]

    def test_k_cs_in_cs5(self):
        cs = master_action_components()["components"]["CS5_chern_simons"]
        assert cs["k_cs"] == K_CS

    def test_n_w_in_matter(self):
        m = master_action_components()["components"]["L_matter"]
        assert m["n_w"] == N_W

    def test_n_generations_3(self):
        m = master_action_components()["components"]["L_matter"]
        assert m["n_generations"] == 3

    def test_gravity_prefactor_positive(self):
        g = master_action_components()["components"]["R5_gravity"]
        assert g["prefactor"] > 0

    def test_cs_prefactor_positive(self):
        cs = master_action_components()["components"]["CS5_chern_simons"]
        assert cs["prefactor"] > 0

    def test_free_parameters_zero(self):
        assert master_action_components()["free_parameters"] == 0

    def test_pillar_58_mentioned(self):
        p = master_action_components()["pillar_alignment"]
        assert "pillar_58" in p

    def test_pillar_70_mentioned(self):
        p = master_action_components()["pillar_alignment"]
        assert "pillar_70_D" in p

    def test_gravity_has_eom(self):
        g = master_action_components()["components"]["R5_gravity"]
        assert "Einstein" in g["equation_of_motion"]


# ---------------------------------------------------------------------------
# TestVaryWrtMetric — 8 tests
# ---------------------------------------------------------------------------

class TestVaryWrtMetric:
    def test_returns_dict(self):
        assert isinstance(vary_wrt_metric(), dict)

    def test_has_variation(self):
        assert "variation" in vary_wrt_metric()

    def test_equation_einstein(self):
        d = vary_wrt_metric()
        assert "Einstein" in d["equation_name"]

    def test_kk_reduction_flrw(self):
        d = vary_wrt_metric()
        assert "FLRW" in d["kk_reduction"]["zero_mode"]

    def test_radion_stabilised(self):
        d = vary_wrt_metric()
        assert d["kk_reduction"]["radion_stabilised"] is True

    def test_sigma_late_times_zero(self):
        d = vary_wrt_metric()
        assert d["kk_reduction"]["sigma_at_late_times"] == 0.0

    def test_derived_from_s_um(self):
        assert vary_wrt_metric()["derived_from_s_um"] is True

    def test_has_pillar_reference(self):
        assert "pillar_reference" in vary_wrt_metric()


# ---------------------------------------------------------------------------
# TestVaryWrtGaugeField — 10 tests
# ---------------------------------------------------------------------------

class TestVaryWrtGaugeField:
    def test_returns_dict(self):
        assert isinstance(vary_wrt_gauge_field(), dict)

    def test_sm_gauge_group_correct(self):
        d = vary_wrt_gauge_field()
        assert "SU(3)" in d["sm_gauge_group"]
        assert "SU(2)" in d["sm_gauge_group"]
        assert "U(1)" in d["sm_gauge_group"]

    def test_has_u1(self):
        d = vary_wrt_gauge_field()
        assert "U1_hypercharge" in d["kk_decomposition"]

    def test_has_su2(self):
        d = vary_wrt_gauge_field()
        assert "SU2_weak" in d["kk_decomposition"]

    def test_has_su3(self):
        d = vary_wrt_gauge_field()
        assert "SU3_strong" in d["kk_decomposition"]

    def test_u1_mass_zero(self):
        d = vary_wrt_gauge_field()
        assert d["kk_decomposition"]["U1_hypercharge"]["mass"] == 0.0

    def test_derived_from_s_um(self):
        assert vary_wrt_gauge_field()["derived_from_s_um"] is True

    def test_has_variation(self):
        assert "variation" in vary_wrt_gauge_field()

    def test_variation_contains_a_mu(self):
        d = vary_wrt_gauge_field()
        assert "A_μ" in d["variation"] or "A_mu" in d["variation"] or "δA" in d["variation"]

    def test_pillar_62_referenced(self):
        d = vary_wrt_gauge_field()
        assert "62" in d["pillar_reference"]


# ---------------------------------------------------------------------------
# TestVaryWrtFermion — 6 tests
# ---------------------------------------------------------------------------

class TestVaryWrtFermion:
    def test_returns_dict(self):
        assert isinstance(vary_wrt_fermion(), dict)

    def test_equation_dirac(self):
        d = vary_wrt_fermion()
        assert "Dirac" in d["equation_name"]

    def test_n_generations_3(self):
        d = vary_wrt_fermion()
        assert d["mass_generation"]["n_generations"] == 3

    def test_derived_from_s_um(self):
        assert vary_wrt_fermion()["derived_from_s_um"] is True

    def test_has_5d_equation(self):
        d = vary_wrt_fermion()
        assert "5d" in d or "equation_5d" in d

    def test_pillar_130_referenced(self):
        d = vary_wrt_fermion()
        assert "130" in d["pillar_reference"]


# ---------------------------------------------------------------------------
# TestVaryWrtDilaton — 7 tests
# ---------------------------------------------------------------------------

class TestVaryWrtDilaton:
    def test_returns_dict(self):
        assert isinstance(vary_wrt_dilaton(), dict)

    def test_phi0_value(self):
        d = vary_wrt_dilaton()
        assert abs(d["static_solution"]["phi0"] - math.pi / 4) < 1e-10

    def test_phi0_degrees_45(self):
        d = vary_wrt_dilaton()
        assert abs(d["static_solution"]["phi0_degrees"] - 45.0) < 0.01

    def test_ftum_connection(self):
        d = vary_wrt_dilaton()
        assert "ftum_connection" in d

    def test_derived_from_s_um(self):
        assert vary_wrt_dilaton()["derived_from_s_um"] is True

    def test_n_s_in_ftum(self):
        d = vary_wrt_dilaton()
        assert str(N_S) in d["ftum_connection"]["cms_spectral_index"]

    def test_pillar_56_referenced(self):
        d = vary_wrt_dilaton()
        assert "56" in d["pillar_reference"]


# ---------------------------------------------------------------------------
# TestCompletenessIdentity — 10 tests
# ---------------------------------------------------------------------------

class TestCompletenessIdentity:
    def test_returns_dict(self):
        assert isinstance(completeness_identity(), dict)

    def test_map_is_bijection(self):
        assert completeness_identity()["map_is_bijection"] is True

    def test_physics_equals_geometry(self):
        assert completeness_identity()["physics_equals_geometry"] is True

    def test_on_shell_dof_5(self):
        assert completeness_identity()["on_shell_dof"] == 5

    def test_n_observables_10(self):
        assert completeness_identity()["n_observables"] == 10

    def test_has_proof_steps(self):
        assert "proof_steps" in completeness_identity()

    def test_proof_has_6_steps(self):
        assert len(completeness_identity()["proof_steps"]) == 6

    def test_last_step_conclusion(self):
        last = completeness_identity()["proof_steps"][-1]
        assert "Conclusion" in last["statement"] or "conclusion" in last["statement"].lower()

    def test_pillar_127_mentioned(self):
        d = completeness_identity()
        assert "127" in d["connection_to_pillar_127"]

    def test_epistemic_status_present(self):
        d = completeness_identity()
        assert "epistemic_status" in d


# ---------------------------------------------------------------------------
# TestGrandSynthesisSummary — 15 tests
# ---------------------------------------------------------------------------

class TestGrandSynthesisSummary:
    def test_returns_dict(self):
        assert isinstance(grand_synthesis_summary(), dict)

    def test_pillar_number_132(self):
        assert grand_synthesis_summary()["pillar"] == 132

    def test_n_pillars_132(self):
        assert grand_synthesis_summary()["n_pillars"] == 132

    def test_has_master_action(self):
        assert "master_action" in grand_synthesis_summary()

    def test_has_variational_equations(self):
        assert "variational_equations" in grand_synthesis_summary()

    def test_variational_equations_has_4_keys(self):
        d = grand_synthesis_summary()["variational_equations"]
        assert len(d) == 4

    def test_has_completeness_identity(self):
        assert "completeness_identity" in grand_synthesis_summary()

    def test_k_cs_in_predictions(self):
        p = grand_synthesis_summary()["key_predictions"]
        assert p["k_cs"] == K_CS

    def test_n_w_in_predictions(self):
        p = grand_synthesis_summary()["key_predictions"]
        assert p["n_w"] == N_W

    def test_has_open_gaps(self):
        assert "open_gaps" in grand_synthesis_summary()

    def test_lambda_qcd_gap_documented(self):
        g = grand_synthesis_summary()["open_gaps"]
        assert "lambda_qcd" in g
        assert g["lambda_qcd"]["status"] == "OPEN"

    def test_has_falsifiers(self):
        d = grand_synthesis_summary()
        assert len(d["falsifiers"]) >= 5

    def test_total_free_parameters_zero(self):
        assert grand_synthesis_summary()["total_free_parameters"] == 0

    def test_framework_closed(self):
        assert grand_synthesis_summary()["framework_closed"] is True

    def test_epistemic_status_physics_derivation(self):
        assert grand_synthesis_summary()["epistemic_status"] == "PHYSICS_DERIVATION"
