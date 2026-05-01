# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_su5_orbifold_proof.py
==================================
Tests for Pillar 94 — SU(5) Orbifold Proof from n_w = 5.
(src/core/su5_orbifold_proof.py)

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.su5_orbifold_proof import (
    # Constants
    N_W, K_CS, PI_KR, M_PL_GEV,
    SU5_RANK, SU5_DIMENSION, SU5_N_GENERATORS, SM_GENERATORS, XY_BOSONS,
    KAWAMURA_P_EIGENVALUES, SIN2_THETA_W_GUT, SIN2_THETA_W_PDG, ALPHA_S_PDG,
    ALPHA_EM_PDG, M_GUT_STANDARD_GEV,
    # Functions
    n_w_min_for_gauge_group,
    su5_from_n_w,
    kawamura_projection_matrix,
    orbifold_spectrum,
    sin2_theta_W_gut,
    sin2_theta_W_mz,
    alpha_s_mz,
    M_GUT_from_UM,
    su5_parameter_closure,
    su5_proof_chain,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kR(self):
        assert PI_KR == 37.0

    def test_su5_rank(self):
        assert SU5_RANK == 4

    def test_su5_dimension(self):
        assert SU5_DIMENSION == 24  # 5²-1

    def test_sm_generators(self):
        assert SM_GENERATORS == 12  # 8+3+1

    def test_xy_bosons(self):
        assert XY_BOSONS == 12  # 24-12

    def test_sm_plus_xy_equals_su5(self):
        assert SM_GENERATORS + XY_BOSONS == SU5_DIMENSION

    def test_kawamura_p_eigenvalues(self):
        assert KAWAMURA_P_EIGENVALUES == [+1, +1, +1, -1, -1]

    def test_kawamura_p_det_is_1(self):
        """det(P) = (-1)^2 = +1 → P ∈ SU(5)."""
        det = 1
        for ev in KAWAMURA_P_EIGENVALUES:
            det *= ev
        assert det == 1

    def test_kawamura_p_squared_is_identity(self):
        """P² = I → Z₂ symmetry."""
        for ev in KAWAMURA_P_EIGENVALUES:
            assert ev ** 2 == 1

    def test_sin2_theta_W_GUT(self):
        assert SIN2_THETA_W_GUT == 3.0 / 8.0

    def test_sin2_theta_W_GUT_value(self):
        assert abs(SIN2_THETA_W_GUT - 0.375) < 1e-12

    def test_pdg_sin2_theta_W(self):
        assert abs(SIN2_THETA_W_PDG - 0.23122) < 0.001

    def test_pdg_alpha_s(self):
        assert abs(ALPHA_S_PDG - 0.118) < 0.001

    def test_m_gut_standard(self):
        assert M_GUT_STANDARD_GEV == 2.0e16


# ===========================================================================
# Step A+B: n_w = 5 selects SU(5)
# ===========================================================================

class TestNWMinForGaugeGroup:
    def test_su5_rank4(self):
        assert n_w_min_for_gauge_group(4) == 5

    def test_so10_rank5(self):
        assert n_w_min_for_gauge_group(5) == 6

    def test_e6_rank6(self):
        assert n_w_min_for_gauge_group(6) == 7

    def test_formula_rank_plus_1(self):
        for r in [1, 2, 3, 4, 5, 6, 7, 8]:
            assert n_w_min_for_gauge_group(r) == r + 1

    def test_raises_rank_zero(self):
        with pytest.raises(ValueError):
            n_w_min_for_gauge_group(0)

    def test_raises_rank_negative(self):
        with pytest.raises(ValueError):
            n_w_min_for_gauge_group(-1)


class TestSU5FromNW:
    def test_returns_dict(self):
        assert isinstance(su5_from_n_w(), dict)

    def test_n_w_correct(self):
        result = su5_from_n_w()
        assert result["n_w"] == 5

    def test_su5_uniquely_selected(self):
        result = su5_from_n_w()
        assert result["su5_uniquely_selected"] is True

    def test_status_proved(self):
        result = su5_from_n_w()
        assert result["status"] == "PROVED"

    def test_su5_n_w_min_equals_5(self):
        result = su5_from_n_w()
        assert result["su5_n_w_min_equals_n_w"] is True

    def test_su5_n_w_min_value(self):
        result = su5_from_n_w()
        assert result["su5_n_w_min"] == 5

    def test_so10_not_selected(self):
        result = su5_from_n_w()
        assert "SO(10)" not in result["selected_group"]

    def test_e6_not_selected(self):
        result = su5_from_n_w()
        assert "E6" not in result["selected_group"]

    def test_su5_in_selected(self):
        result = su5_from_n_w()
        assert "SU(5)" in result["selected_group"]

    def test_winding_constraint_documented(self):
        result = su5_from_n_w()
        assert "rank" in result["winding_constraint"]

    def test_proof_mentions_su5(self):
        result = su5_from_n_w()
        assert "SU(5)" in result["proof"]

    def test_proof_mentions_so10(self):
        result = su5_from_n_w()
        assert "SO(10)" in result["proof"]

    def test_n_w_6_selects_so10(self):
        result = su5_from_n_w(n_w=6)
        assert "SO(10)" in result["selected_group"]
        assert "SU(5)" not in result["selected_group"]

    def test_n_w_7_selects_e6(self):
        result = su5_from_n_w(n_w=7)
        assert "E6" in result["selected_group"]


# ===========================================================================
# Step C: Kawamura mechanism
# ===========================================================================

class TestKawamuraprojectionMatrix:
    def test_returns_dict(self):
        assert isinstance(kawamura_projection_matrix(), dict)

    def test_group_su5(self):
        assert kawamura_projection_matrix()["group"] == "SU(5)"

    def test_P_eigenvalues(self):
        result = kawamura_projection_matrix()
        assert result["P_eigenvalues"] == [+1, +1, +1, -1, -1]

    def test_P_det_plus_1(self):
        result = kawamura_projection_matrix()
        assert result["P_determinant"] == 1

    def test_P_squared_identity(self):
        result = kawamura_projection_matrix()
        assert all(v == 1 for v in result["P_squared"])

    def test_n_even_generators(self):
        result = kawamura_projection_matrix()
        assert result["n_Z2_even_generators"] == 12

    def test_n_odd_generators(self):
        result = kawamura_projection_matrix()
        assert result["n_Z2_odd_generators"] == 12

    def test_even_plus_odd_equals_24(self):
        result = kawamura_projection_matrix()
        assert result["n_Z2_even_generators"] + result["n_Z2_odd_generators"] == 24

    def test_remnant_symmetry_sm(self):
        result = kawamura_projection_matrix()
        assert "SU(3)" in result["remnant_symmetry"]
        assert "SU(2)" in result["remnant_symmetry"]
        assert "U(1)" in result["remnant_symmetry"]

    def test_status_proved(self):
        result = kawamura_projection_matrix()
        assert "PROVED" in result["status"]

    def test_mechanism_kawamura(self):
        result = kawamura_projection_matrix()
        assert "Kawamura" in result["mechanism"]


class TestOrbifoldSpectrum:
    def test_returns_dict(self):
        assert isinstance(orbifold_spectrum(), dict)

    def test_total_generators(self):
        result = orbifold_spectrum()
        assert result["total_generators"] == 24

    def test_massless_count(self):
        result = orbifold_spectrum()
        assert result["massless_zero_modes"]["count"] == 12

    def test_massive_count(self):
        result = orbifold_spectrum()
        assert result["massive_kk_modes"]["count"] == 12

    def test_massless_plus_massive_eq_24(self):
        result = orbifold_spectrum()
        assert (result["massless_zero_modes"]["count"] +
                result["massive_kk_modes"]["count"]) == 24

    def test_breaking_pattern(self):
        result = orbifold_spectrum()
        assert "SU(5)" in result["breaking_pattern"]
        assert "SU(3)" in result["breaking_pattern"]

    def test_su3_generators(self):
        result = orbifold_spectrum()
        assert result["massless_zero_modes"]["su3"]["generators"] == 8

    def test_su2_generators(self):
        result = orbifold_spectrum()
        assert result["massless_zero_modes"]["su2"]["generators"] == 3

    def test_u1_generators(self):
        result = orbifold_spectrum()
        assert result["massless_zero_modes"]["u1"]["generators"] == 1


# ===========================================================================
# Step D: sin²θ_W = 3/8 exact
# ===========================================================================

class TestSin2ThetaWGut:
    def test_returns_dict(self):
        assert isinstance(sin2_theta_W_gut(), dict)

    def test_sin2_exact_value(self):
        result = sin2_theta_W_gut()
        assert result["sin2_theta_W_GUT"] == 3.0 / 8.0

    def test_sin2_fraction(self):
        result = sin2_theta_W_gut()
        assert result["sin2_exact_fraction"] == "3/8"

    def test_cos2_value(self):
        result = sin2_theta_W_gut()
        assert abs(result["cos2_theta_W_GUT"] - 5.0 / 8.0) < 1e-12

    def test_tan2_value(self):
        result = sin2_theta_W_gut()
        assert abs(result["tan2_theta_W_GUT"] - 3.0 / 5.0) < 1e-12

    def test_sin2_cos2_sum_to_1(self):
        result = sin2_theta_W_gut()
        assert abs(result["sin2_theta_W_GUT"] + result["cos2_theta_W_GUT"] - 1.0) < 1e-12

    def test_status_proved(self):
        result = sin2_theta_W_gut()
        assert "PROVED" in result["status"]

    def test_group_su5(self):
        result = sin2_theta_W_gut()
        assert result["group"] == "SU(5)"

    def test_n_w_equals_5(self):
        result = sin2_theta_W_gut()
        assert result["n_w"] == 5

    def test_reference_georgi_glashow(self):
        result = sin2_theta_W_gut()
        assert "Georgi" in result["reference"]

    def test_derivation_contains_3_over_8(self):
        result = sin2_theta_W_gut()
        assert "3/8" in result["derivation"]


# ===========================================================================
# Step E: RGE running
# ===========================================================================

class TestSin2ThetaWMZ:
    def test_returns_dict(self):
        assert isinstance(sin2_theta_W_mz(), dict)

    def test_sin2_GUT_is_3_8(self):
        result = sin2_theta_W_mz()
        assert result["sin2_theta_W_GUT"] == 3.0 / 8.0

    def test_fraction_label(self):
        result = sin2_theta_W_mz()
        assert result["sin2_theta_W_GUT_fraction"] == "3/8"

    def test_predicted_in_range(self):
        """Predicted sin²θ_W(M_Z) should be in [0.20, 0.26]."""
        result = sin2_theta_W_mz()
        assert 0.20 < result["sin2_theta_W_MZ_predicted"] < 0.26

    def test_pdg_value_correct(self):
        result = sin2_theta_W_mz()
        assert abs(result["sin2_theta_W_MZ_PDG"] - 0.23122) < 1e-4

    def test_consistent_2pct(self):
        """MSSM 1-loop should be consistent within 2%."""
        result = sin2_theta_W_mz()
        assert result["consistent_2pct"] is True

    def test_consistent_5pct(self):
        """Should be consistent within 5%."""
        result = sin2_theta_W_mz()
        assert result["consistent_5pct"] is True

    def test_pct_err_positive(self):
        result = sin2_theta_W_mz()
        assert result["pct_err"] >= 0.0

    def test_pct_err_lt_2pct(self):
        """MSSM 1-loop RGE gives < 2% error for sin²θ_W."""
        result = sin2_theta_W_mz()
        assert result["pct_err"] < 2.0

    def test_status_contains_derived(self):
        result = sin2_theta_W_mz()
        assert "DERIVED" in result["status"]

    def test_m_gut_correct(self):
        result = sin2_theta_W_mz()
        assert result["M_GUT_GeV"] == 2.0e16


class TestAlphasMZ:
    def test_returns_dict(self):
        assert isinstance(alpha_s_mz(), dict)

    def test_alpha_s_predicted_in_range(self):
        """α_s(M_Z) should be in [0.09, 0.15]."""
        result = alpha_s_mz()
        assert 0.09 < result["alpha_s_MZ_predicted"] < 0.15

    def test_pdg_correct(self):
        result = alpha_s_mz()
        assert abs(result["alpha_s_MZ_PDG"] - 0.118) < 0.001

    def test_consistent_2pct(self):
        """MSSM 1-loop should be consistent within 2%."""
        result = alpha_s_mz()
        assert result["consistent_2pct"] is True

    def test_consistent_5pct(self):
        result = alpha_s_mz()
        assert result["consistent_5pct"] is True

    def test_consistent_10pct(self):
        result = alpha_s_mz()
        assert result["consistent_10pct"] is True

    def test_pct_err_positive(self):
        result = alpha_s_mz()
        assert result["pct_err"] >= 0.0

    def test_pct_err_lt_2pct(self):
        """MSSM 1-loop RGE gives < 2% error for α_s."""
        result = alpha_s_mz()
        assert result["pct_err"] < 2.0

    def test_status_derived(self):
        result = alpha_s_mz()
        assert "DERIVED" in result["status"]

    def test_b3_mssm_value(self):
        result = alpha_s_mz()
        assert result["b3_mssm"] == -3.0


# ===========================================================================
# M_GUT from UM
# ===========================================================================

class TestMGUTfromUM:
    def test_returns_dict(self):
        assert isinstance(M_GUT_from_UM(), dict)

    def test_m_gut_gev(self):
        result = M_GUT_from_UM()
        assert result["M_GUT_GeV"] == 2.0e16

    def test_pi_kR_GUT_positive(self):
        result = M_GUT_from_UM()
        assert result["pi_kR_GUT"] > 0

    def test_pi_kR_EW_equals_37(self):
        result = M_GUT_from_UM()
        assert result["pi_kR_EW"] == 37.0

    def test_ratio_positive(self):
        result = M_GUT_from_UM()
        assert result["ratio_pi_kR_EW_over_GUT"] > 0

    def test_m_kk_ew_tev_scale(self):
        """EW KK mass from πkR=37 should be in 1 GeV – 100 TeV."""
        result = M_GUT_from_UM()
        assert 1.0 < result["M_KK_EW_GeV"] < 1e8

    def test_pi_kR_GUT_range(self):
        """πkR_GUT = ln(M_Pl/M_GUT) should be 5–10."""
        result = M_GUT_from_UM()
        assert 4.0 < result["pi_kR_GUT"] < 12.0

    def test_n_w_is_5(self):
        result = M_GUT_from_UM()
        assert result["n_w"] == 5


# ===========================================================================
# Full closure and proof
# ===========================================================================

class TestSU5ParameterClosure:
    def test_returns_dict(self):
        assert isinstance(su5_parameter_closure(), dict)

    def test_pillar_94(self):
        assert su5_parameter_closure()["pillar"] == 94

    def test_n_w_5(self):
        assert su5_parameter_closure()["n_w"] == 5

    def test_k_cs_74(self):
        assert su5_parameter_closure()["k_cs"] == 74

    def test_step_AB_proved(self):
        result = su5_parameter_closure()
        assert "PROVED" in result["step_A_B"]["status"]

    def test_step_C_proved(self):
        result = su5_parameter_closure()
        assert "PROVED" in result["step_C"]["status"]

    def test_step_D_sin2_gut(self):
        result = su5_parameter_closure()
        assert result["step_D"]["value"] == 3.0 / 8.0

    def test_step_D_proved(self):
        result = su5_parameter_closure()
        assert "PROVED" in result["step_D"]["status"]

    def test_step_E_sin2_predicted(self):
        result = su5_parameter_closure()
        sin2 = result["step_E"]["sin2_mz_predicted"]
        assert 0.20 < sin2 < 0.26

    def test_step_E_sin2_within_2pct(self):
        result = su5_parameter_closure()
        sin2 = result["step_E"]["sin2_mz_predicted"]
        assert abs(sin2 - SIN2_THETA_W_PDG) / SIN2_THETA_W_PDG < 0.02

    def test_step_E_alpha_s_predicted(self):
        result = su5_parameter_closure()
        alpha_s = result["step_E"]["alpha_s_predicted"]
        assert 0.09 < alpha_s < 0.15

    def test_step_E_alpha_s_within_2pct(self):
        result = su5_parameter_closure()
        alpha_s = result["step_E"]["alpha_s_predicted"]
        assert abs(alpha_s - ALPHA_S_PDG) / ALPHA_S_PDG < 0.02

    def test_p2_upgrade_to_proved(self):
        result = su5_parameter_closure()
        assert "PROVED" in result["parameter_upgrades"]["P2_sin2_theta_W"]["after"]

    def test_p3_upgrade_to_derived(self):
        result = su5_parameter_closure()
        assert "DERIVED" in result["parameter_upgrades"]["P3_alpha_s"]["after"]

    def test_p2_before_was_conjecture(self):
        result = su5_parameter_closure()
        assert "CONJECTURE" in result["parameter_upgrades"]["P2_sin2_theta_W"]["before"]

    def test_status_contains_proved(self):
        result = su5_parameter_closure()
        assert "PROVED" in result["status"]

    def test_massless_bosons_12(self):
        result = su5_parameter_closure()
        assert result["step_C"]["massless_bosons"] == 12

    def test_massive_bosons_12(self):
        result = su5_parameter_closure()
        assert result["step_C"]["massive_bosons"] == 12


class TestSU5ProofChain:
    def test_returns_dict(self):
        assert isinstance(su5_proof_chain(), dict)

    def test_theorem_present(self):
        result = su5_proof_chain()
        assert "n_w" in result["theorem"]
        assert "SU(5)" in result["theorem"]

    def test_step_A_proved(self):
        result = su5_proof_chain()
        assert "PROVED" in result["step_A"]["status"]

    def test_step_B_proved(self):
        result = su5_proof_chain()
        assert result["step_B"]["status"] == "PROVED"

    def test_step_C_proved(self):
        result = su5_proof_chain()
        assert "PROVED" in result["step_C"]["status"]

    def test_step_D_proved(self):
        result = su5_proof_chain()
        assert "PROVED" in result["step_D"]["status"]

    def test_step_D_value_exact(self):
        result = su5_proof_chain()
        assert result["step_D"]["value"] == 3.0 / 8.0

    def test_step_E_sin2_in_range(self):
        result = su5_proof_chain()
        assert 0.20 < result["step_E"]["sin2_pred"] < 0.26

    def test_step_E_sin2_within_2pct(self):
        result = su5_proof_chain()
        sin2 = result["step_E"]["sin2_pred"]
        assert abs(sin2 - SIN2_THETA_W_PDG) / SIN2_THETA_W_PDG < 0.02

    def test_step_E_alpha_s_in_range(self):
        result = su5_proof_chain()
        assert 0.09 < result["step_E"]["alpha_s_pred"] < 0.15

    def test_step_E_alpha_s_within_2pct(self):
        result = su5_proof_chain()
        alpha_s = result["step_E"]["alpha_s_pred"]
        assert abs(alpha_s - ALPHA_S_PDG) / ALPHA_S_PDG < 0.02

    def test_qed_contains_su5(self):
        result = su5_proof_chain()
        assert "SU(5)" in result["qed"]

    def test_qed_contains_qed(self):
        result = su5_proof_chain()
        assert "Q.E.D." in result["qed"]

    def test_step_C_massless_modes(self):
        result = su5_proof_chain()
        assert result["step_C"]["massless_modes"] == 12

    def test_step_C_massive_modes(self):
        result = su5_proof_chain()
        assert result["step_C"]["massive_modes"] == 12
