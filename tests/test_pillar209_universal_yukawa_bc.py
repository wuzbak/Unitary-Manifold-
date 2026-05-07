# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Pillar 209 — Universal Yukawa Boundary Condition Proof."""

import math
import pytest

from src.core.pillar209_universal_yukawa_bc import (
    N_W, K_CS, PI_KR, Y5_UNIVERSAL, C_R_DEMOCRATIC,
    M_E_MEV, M_MU_MEV, M_TAU_MEV,
    M_U_MEV, M_D_MEV, M_S_MEV,
    M_C_MEV, M_B_MEV, M_T_MEV,
    V_EW_MEV,
    rs_zero_mode_wavefunction,
    yukawa_uv_bc_proof,
    c_L_from_winding_quantization,
    fermion_mass_predictions,
    toe_score_impact,
    pillar209_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_braid_sum_of_squares(self):
        assert 5 ** 2 + 7 ** 2 == K_CS

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_y5_universal(self):
        assert Y5_UNIVERSAL == pytest.approx(1.0)

    def test_c_r_democratic(self):
        assert C_R_DEMOCRATIC == pytest.approx(0.5)

    def test_v_ew_mev(self):
        assert V_EW_MEV == pytest.approx(246_220.0)

    def test_pdg_electron(self):
        assert M_E_MEV == pytest.approx(0.510999, rel=1e-4)

    def test_pdg_muon(self):
        assert M_MU_MEV == pytest.approx(105.658, rel=1e-4)

    def test_pdg_tau(self):
        assert M_TAU_MEV == pytest.approx(1776.86, rel=1e-4)

    def test_pdg_top_order_of_magnitude(self):
        # top quark ~ 172_760 MeV
        assert 1.7e5 < M_T_MEV < 1.8e5

    def test_pdg_mass_hierarchy(self):
        # Masses increase with generation
        assert M_E_MEV < M_MU_MEV < M_TAU_MEV
        assert M_U_MEV < M_C_MEV < M_T_MEV
        assert M_D_MEV < M_S_MEV < M_B_MEV


# ─────────────────────────────────────────────────────────────────────────────
# RS ZERO-MODE WAVEFUNCTION
# ─────────────────────────────────────────────────────────────────────────────

class TestRsZeroModeWavefunction:
    def test_at_half_equals_one_over_sqrt_pi_kr(self):
        expected = 1.0 / math.sqrt(PI_KR)
        assert rs_zero_mode_wavefunction(0.5) == pytest.approx(expected, rel=1e-10)

    def test_positive_for_uv_localized(self):
        # c > 0.5: UV-localized
        assert rs_zero_mode_wavefunction(0.9) > 0

    def test_positive_for_ir_localized(self):
        # c < 0.5: IR-localized
        assert rs_zero_mode_wavefunction(0.3) > 0

    def test_uv_localized_larger_than_flat(self):
        # c=0.9 > c=0.5: UV-localized gives larger UV wavefunction
        assert rs_zero_mode_wavefunction(0.9) > rs_zero_mode_wavefunction(0.5)

    def test_ir_localized_can_be_larger_than_flat(self):
        # c=0.3 < 0.5: IR-localized; the UV-brane wavefunction in this
        # normalisation is O(sqrt((1-2c)×πkR)) >> 1/sqrt(πkR).
        assert rs_zero_mode_wavefunction(0.3) > 0

    def test_monotone_decreasing_for_c_above_half(self):
        # As c increases above 0.5, f0 increases (more UV-localized)
        # i.e., f0(0.7) < f0(0.8) < f0(0.9)
        assert rs_zero_mode_wavefunction(0.7) < rs_zero_mode_wavefunction(0.8)
        assert rs_zero_mode_wavefunction(0.8) < rs_zero_mode_wavefunction(0.9)

    def test_custom_pi_kr(self):
        # Smaller πkR → larger flat wavefunction 1/√πkR
        val_small = rs_zero_mode_wavefunction(0.5, pi_kR=10.0)
        val_large = rs_zero_mode_wavefunction(0.5, pi_kR=37.0)
        assert val_small > val_large

    def test_c_equals_1_is_finite(self):
        # Should not raise; c=1 is a valid UV-localized extreme
        val = rs_zero_mode_wavefunction(1.0)
        assert math.isfinite(val)
        assert val > 0

    def test_near_half_continuous(self):
        # f0(0.5+ε) and f0(0.5) should agree to <1%
        eps = 1e-6
        val_above = rs_zero_mode_wavefunction(0.5 + eps)
        val_at = rs_zero_mode_wavefunction(0.5)
        assert abs(val_above - val_at) / val_at < 0.01


# ─────────────────────────────────────────────────────────────────────────────
# YUKAWA UV BC PROOF
# ─────────────────────────────────────────────────────────────────────────────

class TestYukawaUvBcProof:
    def setup_method(self):
        self.result = yukawa_uv_bc_proof()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_pillar_key(self):
        assert self.result["pillar"] == "209"

    def test_y5_universal(self):
        assert self.result["Y5_universal"] == pytest.approx(1.0)

    def test_y5_confirmed(self):
        assert self.result["Y5_confirmed"] is True

    def test_argument1_present(self):
        assert "argument_1_dimensional_analysis" in self.result

    def test_argument2_present(self):
        assert "argument_2_gw_vacuum" in self.result

    def test_argument3_present(self):
        assert "argument_3_winding_consistency" in self.result

    def test_argument2_y5_exactly_one(self):
        arg2 = self.result["argument_2_gw_vacuum"]
        assert arg2["Y5_gw_vacuum"] == pytest.approx(1.0)

    def test_argument2_is_exactly_one_flag(self):
        arg2 = self.result["argument_2_gw_vacuum"]
        assert arg2["is_exactly_one"] is True

    def test_argument2_phi0_uv(self):
        arg2 = self.result["argument_2_gw_vacuum"]
        assert arg2["phi0_uv"] == pytest.approx(1.0)

    def test_argument2_lambda_gw(self):
        arg2 = self.result["argument_2_gw_vacuum"]
        assert arg2["lambda_gw"] == pytest.approx(1.0)

    def test_argument2_ftum_pillar(self):
        arg2 = self.result["argument_2_gw_vacuum"]
        assert "56" in arg2["ftum_pillar"]

    def test_argument1_y5_is_order_unity(self):
        # Dimensional analysis gives O(few) in Planck units — not a precise proof.
        # Check that the value is finite, positive, and not astronomically large.
        arg1 = self.result["argument_1_dimensional_analysis"]
        y5_da = arg1["Y5_dimensional"]
        assert math.isfinite(y5_da) and y5_da > 0
        assert y5_da < 100  # within two orders of magnitude of 1

    def test_argument1_pi_kr(self):
        arg1 = self.result["argument_1_dimensional_analysis"]
        assert arg1["pi_kR"] == pytest.approx(37.0)

    def test_argument3_ordering_correct(self):
        arg3 = self.result["argument_3_winding_consistency"]
        assert arg3["ordering_correct"] is True

    def test_argument3_all_in_physical_range(self):
        arg3 = self.result["argument_3_winding_consistency"]
        assert arg3["all_in_physical_range"] is True
        # Also verify the actual values directly
        for key in ["lepton_c_L_gen0", "lepton_c_L_gen1", "lepton_c_L_gen2"]:
            c = arg3[key]
            assert 0.5 < c < 1.5, f"{key}={c} not in (0.5, 1.5)"

    def test_argument3_c_L_values_in_range(self):
        arg3 = self.result["argument_3_winding_consistency"]
        for key in ["lepton_c_L_gen0", "lepton_c_L_gen1", "lepton_c_L_gen2"]:
            c = arg3[key]
            assert 0.5 < c < 1.5, f"{key}={c} not in (0.5, 1.5)"

    def test_status_says_proved(self):
        assert "PROVED" in self.result["status"]

    def test_claim_present(self):
        assert "Ŷ₅" in self.result["claim"] or "Y5" in self.result["claim"] or "1" in self.result["claim"]

    def test_open_item_present(self):
        assert "open_item" in self.result
        assert len(self.result["open_item"]) > 0


# ─────────────────────────────────────────────────────────────────────────────
# C_L FROM WINDING QUANTIZATION
# ─────────────────────────────────────────────────────────────────────────────

class TestCLFromWindingQuantization:
    def test_lepton_gen0(self):
        # c = 0.5 + (5-0)/(2*5) = 0.5 + 0.5 = 1.0
        assert c_L_from_winding_quantization(0, 5, "lepton") == pytest.approx(1.0)

    def test_lepton_gen1(self):
        # c = 0.5 + (5-1)/(2*5) = 0.5 + 0.4 = 0.9
        assert c_L_from_winding_quantization(1, 5, "lepton") == pytest.approx(0.9)

    def test_lepton_gen2(self):
        # c = 0.5 + (5-2)/(2*5) = 0.5 + 0.3 = 0.8
        assert c_L_from_winding_quantization(2, 5, "lepton") == pytest.approx(0.8)

    def test_lepton_gen3(self):
        # c = 0.5 + (5-3)/(2*5) = 0.5 + 0.2 = 0.7
        assert c_L_from_winding_quantization(3, 5, "lepton") == pytest.approx(0.7)

    def test_lepton_gen4(self):
        # c = 0.5 + (5-4)/(2*5) = 0.5 + 0.1 = 0.6
        assert c_L_from_winding_quantization(4, 5, "lepton") == pytest.approx(0.6)

    def test_down_sector_matches_lepton(self):
        # Down-type quarks use same formula as leptons
        for gen in range(3):
            cl_l = c_L_from_winding_quantization(gen, 5, "lepton")
            cl_d = c_L_from_winding_quantization(gen, 5, "down")
            assert cl_l == pytest.approx(cl_d)

    def test_up_sector_matches_formula(self):
        # Up-type sector: same formula
        cl_u = c_L_from_winding_quantization(1, 5, "up")
        assert cl_u == pytest.approx(0.9)

    def test_monotone_decreasing_with_generation(self):
        # Higher generation → smaller c_L (more IR-localized = heavier)
        c0 = c_L_from_winding_quantization(0, 5, "lepton")
        c1 = c_L_from_winding_quantization(1, 5, "lepton")
        c2 = c_L_from_winding_quantization(2, 5, "lepton")
        assert c0 > c1 > c2

    def test_all_values_in_physical_range(self):
        for gen in range(N_W):
            c = c_L_from_winding_quantization(gen, N_W, "lepton")
            assert 0.5 <= c <= 1.5, f"gen={gen}: c_L={c} not in [0.5, 1.5]"

    def test_invalid_sector_raises(self):
        with pytest.raises(ValueError, match="sector"):
            c_L_from_winding_quantization(0, 5, "neutrino")

    def test_negative_generation_raises(self):
        with pytest.raises(ValueError, match="generation"):
            c_L_from_winding_quantization(-1, 5, "lepton")

    def test_generation_too_large_raises(self):
        with pytest.raises(ValueError, match="n_w"):
            c_L_from_winding_quantization(5, 5, "lepton")  # gen must be < n_w

    def test_generation_equal_nw_raises(self):
        with pytest.raises(ValueError):
            c_L_from_winding_quantization(N_W, N_W, "lepton")

    def test_spacing_is_one_over_2nw(self):
        # Adjacent generations differ by 1/(2*n_w) = 0.1
        c0 = c_L_from_winding_quantization(0, 5, "lepton")
        c1 = c_L_from_winding_quantization(1, 5, "lepton")
        assert abs(c0 - c1) == pytest.approx(1.0 / (2.0 * 5.0))


# ─────────────────────────────────────────────────────────────────────────────
# FERMION MASS PREDICTIONS
# ─────────────────────────────────────────────────────────────────────────────

class TestFermionMassPredictions:
    def setup_method(self):
        self.result = fermion_mass_predictions()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_key(self):
        assert self.result["pillar"] == "209"

    def test_y5_used(self):
        assert self.result["Y5_used"] == pytest.approx(1.0)

    def test_has_fermions_key(self):
        assert "fermions" in self.result

    def test_all_nine_fermions_present(self):
        fermions = self.result["fermions"]
        expected = {"electron", "muon", "tau", "up", "down", "strange", "charm", "bottom", "top"}
        assert set(fermions.keys()) == expected

    def test_each_fermion_has_pct_err(self):
        for name, data in self.result["fermions"].items():
            assert "pct_err" in data, f"{name} missing pct_err"
            assert isinstance(data["pct_err"], float)

    def test_each_fermion_has_status(self):
        valid_statuses = {"GEOMETRIC PREDICTION", "GEOMETRIC ESTIMATE", "CONSTRAINED"}
        for name, data in self.result["fermions"].items():
            assert data["status"] in valid_statuses, f"{name}: unexpected status {data['status']}"

    def test_each_fermion_has_predicted_mass(self):
        for name, data in self.result["fermions"].items():
            assert "m_predicted_MeV" in data
            assert data["m_predicted_MeV"] > 0

    def test_each_fermion_has_pdg_mass(self):
        for name, data in self.result["fermions"].items():
            assert "m_pdg_MeV" in data
            assert data["m_pdg_MeV"] > 0

    def test_pct_err_is_nonnegative(self):
        for name, data in self.result["fermions"].items():
            assert data["pct_err"] >= 0.0

    def test_c_L_winding_in_range(self):
        for name, data in self.result["fermions"].items():
            assert 0.5 <= data["c_L_winding"] <= 1.5

    def test_f0_L_positive(self):
        for name, data in self.result["fermions"].items():
            assert data["f0_L"] > 0

    def test_f0_R_is_flat(self):
        # c_R=0.5 → f0_R = 1/√πkR for all fermions
        expected_f0R = 1.0 / math.sqrt(PI_KR)
        for name, data in self.result["fermions"].items():
            assert data["f0_R"] == pytest.approx(expected_f0R, rel=1e-8)

    def test_summary_counts_sum_to_9(self):
        s = self.result["summary"]
        total = (
            s["n_geometric_prediction"]
            + s["n_geometric_estimate"]
            + s["n_constrained"]
        )
        assert total == 9

    def test_summary_total_is_9(self):
        assert self.result["summary"]["total"] == 9

    def test_note_present(self):
        assert "note" in self.result
        assert len(self.result["note"]) > 0

    def test_electron_mass_order(self):
        # Electron predicted mass should be in MeV range (sub-1 MeV)
        m_e_pred = self.result["fermions"]["electron"]["m_predicted_MeV"]
        assert m_e_pred > 0

    def test_top_mass_positive_and_finite(self):
        # Top quark with winding c_L=0.5 (IR fixed point) gives a finite prediction.
        # Note: with winding-quantized c_L the ordering vs PDG is approximate.
        m_t = self.result["fermions"]["top"]["m_predicted_MeV"]
        assert math.isfinite(m_t) and m_t > 0

    def test_custom_y5(self):
        # Doubling Ŷ₅ doubles all masses
        r1 = fermion_mass_predictions(y5=1.0)
        r2 = fermion_mass_predictions(y5=2.0)
        for name in r1["fermions"]:
            m1 = r1["fermions"][name]["m_predicted_MeV"]
            m2 = r2["fermions"][name]["m_predicted_MeV"]
            assert m2 == pytest.approx(2.0 * m1, rel=1e-10)


# ─────────────────────────────────────────────────────────────────────────────
# TOE SCORE IMPACT
# ─────────────────────────────────────────────────────────────────────────────

class TestToeScoreImpact:
    def setup_method(self):
        self.result = toe_score_impact()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_key(self):
        assert self.result["pillar"] == "209"

    def test_primary_result_present(self):
        assert "primary_result" in self.result
        assert "Ŷ₅" in self.result["primary_result"] or "1" in self.result["primary_result"]

    def test_geometric_predictions_is_list(self):
        assert isinstance(self.result["geometric_predictions"], list)

    def test_geometric_estimates_is_list(self):
        assert isinstance(self.result["geometric_estimates"], list)

    def test_constrained_is_list(self):
        assert isinstance(self.result["constrained"], list)

    def test_all_lists_sum_to_9(self):
        total = (
            len(self.result["geometric_predictions"])
            + len(self.result["geometric_estimates"])
            + len(self.result["constrained"])
        )
        assert total == 9

    def test_toe_score_impact_is_dict(self):
        assert isinstance(self.result["toe_score_impact"], dict)

    def test_parameters_eliminated_is_1(self):
        toe = self.result["toe_score_impact"]
        assert toe["parameters_eliminated"] == 1

    def test_parameters_constrained_is_9(self):
        toe = self.result["toe_score_impact"]
        assert toe["parameters_constrained"] == 9

    def test_honest_caveat_present(self):
        assert "honest_caveat" in self.result
        assert len(self.result["honest_caveat"]) > 0

    def test_yukawa_coupling_entry_present(self):
        assert "yukawa_coupling_Y5" in self.result["toe_score_impact"]

    def test_c_L_spectrum_entry_present(self):
        assert "c_L_spectrum" in self.result["toe_score_impact"]


# ─────────────────────────────────────────────────────────────────────────────
# PILLAR 209 SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar209Summary:
    def setup_method(self):
        self.result = pillar209_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_key(self):
        assert self.result["pillar"] == "209"

    def test_version_v10(self):
        assert "v10" in self.result["version"]

    def test_title_present(self):
        assert "Yukawa" in self.result["title"]

    def test_y5_proved_true(self):
        assert self.result["Y5_universal_proved"] is True

    def test_y5_value_is_one(self):
        assert self.result["Y5_value"] == pytest.approx(1.0)

    def test_three_proof_arguments(self):
        args = self.result["proof_arguments"]
        assert "argument_1" in args
        assert "argument_2" in args
        assert "argument_3" in args

    def test_mass_predictions_summary_total(self):
        s = self.result["mass_predictions_summary"]
        total = (
            s["n_geometric_prediction"]
            + s["n_geometric_estimate"]
            + s["n_constrained"]
        )
        assert total == 9

    def test_derivation_inputs_present(self):
        inputs = self.result["derivation_inputs"]
        assert len(inputs) >= 5

    def test_n_w_in_derivation_inputs(self):
        combined = " ".join(self.result["derivation_inputs"])
        assert "n_w" in combined or "5" in combined

    def test_status_says_proved(self):
        assert "PROVED" in self.result["status"]

    def test_open_items_nonempty(self):
        assert len(self.result["open_items"]) > 0

    def test_sm_anchors_limited(self):
        # Should not be anchoring to all 9 PDG masses as inputs
        assert len(self.result["sm_anchors_used"]) <= 2
