# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_yukawa_geometric_closure.py
=========================================
Tests for Pillar 93 — Yukawa Geometric Closure
(src/core/yukawa_geometric_closure.py).

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.yukawa_geometric_closure import (
    # Constants
    N_W, N1_BRAID, N2_BRAID, K_CS, PI_KR, K_RS, PHI0,
    Y5_FTUM_VALUE, LAMBDA_Y_EFF, C_R_DEMOCRATIC,
    V_HIGGS_MEV, V_HIGGS_GEV, M_PL_GEV,
    M_ELECTRON_PDG, M_MUON_PDG, M_TAU_PDG,
    M_UP_PDG, M_DOWN_PDG, M_STRANGE_PDG,
    M_CHARM_PDG, M_BOTTOM_PDG, M_TOP_PDG,
    # Functions
    pi_kR_from_kCS,
    pi_kR_consistency_check,
    Y5_ftum,
    lambda_Y_effective,
    lambda_Y_derivation_report,
    winding_quantised_c_L,
    winding_quantised_spectrum,
    predict_fermion_mass,
    electron_mass_prediction,
    lepton_mass_predictions,
    quark_mass_predictions,
    fermion_absolute_mass_closure,
    yukawa_closure_proof,
    _f0,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_braid_pair(self):
        assert N1_BRAID == 5
        assert N2_BRAID == 7

    def test_k_cs(self):
        assert K_CS == 74
        assert K_CS == N1_BRAID**2 + N2_BRAID**2

    def test_pi_kR_equals_k_cs_over_2(self):
        assert PI_KR == 37.0
        assert PI_KR == K_CS / 2.0

    def test_phi0(self):
        assert PHI0 == 1.0

    def test_Y5_ftum_value(self):
        assert Y5_FTUM_VALUE == 1.0
        assert Y5_FTUM_VALUE == PHI0

    def test_lambda_Y_eff(self):
        assert abs(LAMBDA_Y_EFF - 1.0 / math.sqrt(37.0)) < 1e-12

    def test_lambda_Y_eff_equals_sqrt_2_over_k_cs(self):
        assert abs(LAMBDA_Y_EFF - math.sqrt(2.0 / K_CS)) < 1e-12

    def test_c_r_democratic(self):
        assert C_R_DEMOCRATIC == 0.5

    def test_v_higgs_mev(self):
        assert abs(V_HIGGS_MEV - 246_220.0) < 1.0

    def test_m_pl_gev_magnitude(self):
        assert 1.0e19 < M_PL_GEV < 1.3e19

    def test_pdg_electron_mass(self):
        assert abs(M_ELECTRON_PDG - 0.511) < 0.001

    def test_pdg_muon_mass(self):
        assert abs(M_MUON_PDG - 105.658) < 0.01

    def test_pdg_tau_mass(self):
        assert abs(M_TAU_PDG - 1776.0) < 1.0


# ===========================================================================
# Step 1: πkR = k_CS/2
# ===========================================================================

class TestPiKR:
    def test_pi_kR_from_kCS_default(self):
        assert pi_kR_from_kCS() == 37.0

    def test_pi_kR_from_kCS_explicit_74(self):
        assert pi_kR_from_kCS(74) == 37.0

    def test_pi_kR_from_kCS_identity(self):
        for k in [10, 20, 50, 74, 100, 200]:
            assert pi_kR_from_kCS(k) == k / 2.0

    def test_pi_kR_raises_zero(self):
        with pytest.raises(ValueError):
            pi_kR_from_kCS(0)

    def test_pi_kR_raises_negative(self):
        with pytest.raises(ValueError):
            pi_kR_from_kCS(-10)

    def test_pi_kR_consistency_returns_dict(self):
        result = pi_kR_consistency_check()
        assert isinstance(result, dict)

    def test_pi_kR_consistency_um_value(self):
        result = pi_kR_consistency_check()
        assert result["pi_kR_UM"] == 37.0

    def test_pi_kR_consistency_k_cs(self):
        result = pi_kR_consistency_check()
        assert result["k_CS"] == 74

    def test_pi_kR_identity_proved(self):
        result = pi_kR_consistency_check()
        assert result["identity_proved"] is True

    def test_pi_kR_hierarchy_consistent(self):
        """RS hierarchy ln(M_Pl/TeV) ≈ 37 consistent with UM within 15%."""
        result = pi_kR_consistency_check()
        assert result["hierarchy_consistency"] is True

    def test_pi_kR_ew_scale_consistent(self):
        result = pi_kR_consistency_check()
        assert result["EW_scale_consistency"] is True

    def test_pi_kR_RS_hierarchy_range(self):
        """Observed hierarchy value should be 30–45."""
        result = pi_kR_consistency_check()
        assert 30.0 < result["pi_kR_RS_hierarchy"] < 45.0

    def test_pi_kR_v_IR_tev_scale(self):
        """IR brane VEV from πkR=37 should be in 1–10⁶ GeV range."""
        result = pi_kR_consistency_check()
        assert 1.0 < result["v_IR_UM_GeV"] < 1e6

    def test_pi_kR_derivation_string_has_74(self):
        result = pi_kR_consistency_check()
        assert "74" in result["pi_kR_UM_derivation"]

    def test_pi_kR_proof_statement_present(self):
        result = pi_kR_consistency_check()
        assert "πkR" in result["proof_statement"]


# ===========================================================================
# Step 2: Ŷ₅ = φ₀ = 1
# ===========================================================================

class TestY5FtumAndLambdaEff:
    def test_Y5_ftum_returns_1(self):
        assert Y5_ftum() == 1.0

    def test_Y5_ftum_equals_phi0(self):
        assert Y5_ftum() == PHI0

    def test_Y5_ftum_custom_phi0(self):
        assert Y5_ftum(phi0=2.0) == 2.0

    def test_lambda_Y_effective_default(self):
        lY = lambda_Y_effective()
        assert abs(lY - math.sqrt(2.0 / K_CS)) < 1e-12

    def test_lambda_Y_effective_equals_1_over_sqrt37(self):
        lY = lambda_Y_effective()
        assert abs(lY - 1.0 / math.sqrt(37.0)) < 1e-12

    def test_lambda_Y_effective_natural_order(self):
        """λ_eff should be O(0.1) — sub-unity, not tiny."""
        lY = lambda_Y_effective()
        assert 0.05 < lY < 0.5

    def test_lambda_Y_derivation_structure(self):
        report = lambda_Y_derivation_report()
        for key in ["step1_pi_kR", "step2_Y5", "step3_lambda_eff",
                    "k_cs", "pi_kR", "Y5", "lambda_eff", "proof_statement"]:
            assert key in report

    def test_lambda_Y_derivation_pi_kR_value(self):
        report = lambda_Y_derivation_report()
        assert report["step1_pi_kR"]["value"] == 37.0

    def test_lambda_Y_derivation_Y5_value(self):
        report = lambda_Y_derivation_report()
        assert report["step2_Y5"]["value"] == 1.0

    def test_lambda_Y_derivation_forms_consistent(self):
        report = lambda_Y_derivation_report()
        assert report["step3_lambda_eff"]["forms_consistent"] is True

    def test_lambda_Y_derivation_status_derived(self):
        report = lambda_Y_derivation_report()
        assert "DERIVED" in report["step3_lambda_eff"]["status"]

    def test_lambda_Y_derivation_proof_statement(self):
        report = lambda_Y_derivation_report()
        assert "DERIVED" in report["proof_statement"]
        assert "k_CS" in report["proof_statement"]


# ===========================================================================
# Winding-quantised bulk mass spectrum
# ===========================================================================

class TestWindingQuantisedSpectrum:
    def test_c_L_n0_decoupled(self):
        assert winding_quantised_c_L(5, 0) == 1.0

    def test_c_L_n1(self):
        assert abs(winding_quantised_c_L(5, 1) - 0.9) < 1e-10

    def test_c_L_n2_electron_reference(self):
        """n=2 is the electron winding-quantised reference c_L = 0.800."""
        assert abs(winding_quantised_c_L(5, 2) - 0.8) < 1e-10

    def test_c_L_n3(self):
        assert abs(winding_quantised_c_L(5, 3) - 0.7) < 1e-10

    def test_c_L_n4(self):
        assert abs(winding_quantised_c_L(5, 4) - 0.6) < 1e-10

    def test_c_L_n5_flat(self):
        assert abs(winding_quantised_c_L(5, 5) - 0.5) < 1e-10

    def test_c_L_all_gte_half(self):
        for n in range(6):
            assert winding_quantised_c_L(5, n) >= 0.5

    def test_c_L_non_increasing(self):
        spectrum = winding_quantised_spectrum(5)
        for i in range(len(spectrum) - 1):
            assert spectrum[i] >= spectrum[i + 1]

    def test_winding_spectrum_length(self):
        assert len(winding_quantised_spectrum(5)) == 6

    def test_winding_spectrum_min_max(self):
        s = winding_quantised_spectrum(5)
        assert min(s) == 0.5
        assert max(s) == 1.0

    def test_winding_spacing(self):
        s = winding_quantised_spectrum(5)
        for i in range(len(s) - 1):
            assert abs(s[i] - s[i + 1] - 0.1) < 1e-10

    def test_c_L_raises_n_negative(self):
        with pytest.raises(ValueError):
            winding_quantised_c_L(5, -1)

    def test_c_L_raises_n_too_large(self):
        with pytest.raises(ValueError):
            winding_quantised_c_L(5, 6)

    def test_c_L_raises_n_w_zero(self):
        with pytest.raises(ValueError):
            winding_quantised_c_L(0, 0)


# ===========================================================================
# RS wavefunction
# ===========================================================================

class TestF0Wavefunction:
    def test_f0_flat_at_0p5(self):
        """f₀(0.5) = 1/√37 = λ_eff."""
        f = _f0(0.5, 1.0, 37.0)
        assert abs(f - 1.0 / math.sqrt(37.0)) < 1e-10

    def test_f0_positive(self):
        for c in [0.3, 0.5, 0.7, 0.9]:
            assert _f0(c) >= 0.0

    def test_f0_decreasing_above_half(self):
        """f₀(c) is monotonically decreasing for c > 0.5."""
        f_vals = [_f0(c) for c in [0.5, 0.6, 0.7, 0.8, 0.9]]
        for i in range(len(f_vals) - 1):
            assert f_vals[i] >= f_vals[i + 1]


# ===========================================================================
# Fermion mass predictions
# ===========================================================================

class TestPredictFermionMass:
    def test_returns_positive_float(self):
        m = predict_fermion_mass(0.8)
        assert isinstance(m, float)
        assert m > 0.0

    def test_decreasing_with_c_L(self):
        """Higher c_L → more UV-localised → lighter mass."""
        assert predict_fermion_mass(0.7) > predict_fermion_mass(0.9)

    def test_y5_scaling(self):
        """Mass scales linearly with Y5."""
        m1 = predict_fermion_mass(0.8, Y5=1.0)
        m2 = predict_fermion_mass(0.8, Y5=2.0)
        assert abs(m2 / m1 - 2.0) < 1e-10

    def test_v_EW_scaling(self):
        """Mass scales linearly with v_EW."""
        m1 = predict_fermion_mass(0.8, v_EW_MeV=246220.0)
        m2 = predict_fermion_mass(0.8, v_EW_MeV=100000.0)
        assert abs(m2 / m1 - 100000.0 / 246220.0) < 1e-8


class TestElectronMassPrediction:
    def test_returns_dict(self):
        assert isinstance(electron_mass_prediction(), dict)

    def test_winding_c_Le_is_0p800(self):
        result = electron_mass_prediction()
        assert result["c_Le_winding_quantised"] == 0.800

    def test_exact_c_Le_is_0p7980(self):
        result = electron_mass_prediction()
        assert result["c_Le_exact"] == 0.7980

    def test_winding_within_15pct(self):
        """Leading-order winding c_Le=0.800 gives m_e within 15% of PDG."""
        result = electron_mass_prediction()
        assert result["pct_err_winding"] < 15.0

    def test_exact_within_1pct(self):
        """Exact c_Le=0.798 gives m_e within 1% of PDG."""
        result = electron_mass_prediction()
        assert result["pct_err_exact"] < 1.0

    def test_pdg_value_correct(self):
        result = electron_mass_prediction()
        assert abs(result["m_e_PDG_MeV"] - 0.511) < 0.001

    def test_consistent_winding(self):
        result = electron_mass_prediction()
        assert result["consistent_winding"] is True

    def test_consistent_exact(self):
        result = electron_mass_prediction()
        assert result["consistent_exact"] is True

    def test_Y5_is_1(self):
        result = electron_mass_prediction()
        assert result["Y5"] == 1.0

    def test_pi_kR_is_37(self):
        result = electron_mass_prediction()
        assert result["pi_kR"] == 37.0


class TestLeptonMassPredictions:
    def test_returns_dict_with_leptons(self):
        result = lepton_mass_predictions()
        assert "leptons" in result
        for name in ["electron", "muon", "tau"]:
            assert name in result["leptons"]

    def test_Y5_is_1(self):
        result = lepton_mass_predictions()
        assert result["Y5"] == 1.0

    def test_pi_kR_is_37(self):
        result = lepton_mass_predictions()
        assert result["pi_kR"] == 37.0

    def test_c_R_democratic(self):
        result = lepton_mass_predictions()
        assert result["c_R_democratic"] == 0.5

    def test_all_masses_positive(self):
        result = lepton_mass_predictions()
        for name, lep in result["leptons"].items():
            assert lep["m_pred_MeV"] > 0, f"{name} not positive"

    def test_mass_hierarchy(self):
        """m_e < m_mu < m_tau."""
        leps = lepton_mass_predictions()["leptons"]
        assert leps["electron"]["m_pred_MeV"] < leps["muon"]["m_pred_MeV"]
        assert leps["muon"]["m_pred_MeV"] < leps["tau"]["m_pred_MeV"]

    def test_systematic_offset_documented(self):
        result = lepton_mass_predictions()
        assert result["systematic_offset_pct"] == pytest.approx(7.36, abs=0.1)

    def test_status_contains_predicted(self):
        result = lepton_mass_predictions()
        assert "PREDICTED" in result["status"]


class TestQuarkMassPredictions:
    def test_returns_dict_with_quarks(self):
        result = quark_mass_predictions()
        assert "quarks" in result
        for q in ["up", "charm", "top", "down", "strange", "bottom"]:
            assert q in result["quarks"]

    def test_hierarchy_up_type(self):
        result = quark_mass_predictions()
        assert result["hierarchy_up_type"] is True

    def test_hierarchy_down_type(self):
        result = quark_mass_predictions()
        assert result["hierarchy_down_type"] is True

    def test_all_masses_positive(self):
        result = quark_mass_predictions()
        for name, q in result["quarks"].items():
            assert q["m_pred_MeV"] > 0, f"{name} not positive"

    def test_status_contains_open(self):
        result = quark_mass_predictions()
        assert "OPEN" in result["status"] or "OPEN" in result["status"]

    def test_Y5_is_1(self):
        result = quark_mass_predictions()
        assert result["Y5"] == 1.0


# ===========================================================================
# Full closure and proof
# ===========================================================================

class TestFermionAbsolutemassClosure:
    def test_returns_dict(self):
        assert isinstance(fermion_absolute_mass_closure(), dict)

    def test_pillar_93(self):
        assert fermion_absolute_mass_closure()["pillar"] == 93

    def test_k_cs(self):
        assert fermion_absolute_mass_closure()["k_cs"] == 74

    def test_pi_kR(self):
        assert fermion_absolute_mass_closure()["pi_kR"] == 37.0

    def test_phi0(self):
        assert fermion_absolute_mass_closure()["phi0"] == 1.0

    def test_Y5_derived(self):
        assert fermion_absolute_mass_closure()["Y5_derived"] == 1.0

    def test_lambda_Y_eff(self):
        result = fermion_absolute_mass_closure()
        assert abs(result["lambda_Y_eff"] - math.sqrt(2.0 / K_CS)) < 1e-12

    def test_step1_proved(self):
        result = fermion_absolute_mass_closure()
        assert "PROVED" in result["step1_pi_kR"]["status"]

    def test_step2_derived(self):
        result = fermion_absolute_mass_closure()
        assert "DERIVED" in result["step2_Y5"]["status"]

    def test_gap_closed(self):
        result = fermion_absolute_mass_closure()
        assert "CLOSED" in result["gap_closed"]

    def test_honest_remaining_gap(self):
        result = fermion_absolute_mass_closure()
        assert "c_L" in result["honest_remaining_gap"]

    def test_electron_winding_err_within_15pct(self):
        result = fermion_absolute_mass_closure()
        assert result["step3_lepton_masses"]["electron_winding_pct_err"] < 15.0

    def test_electron_exact_err_within_1pct(self):
        result = fermion_absolute_mass_closure()
        assert result["step3_lepton_masses"]["electron_exact_pct_err"] < 1.0


class TestYukawaClosureProof:
    def test_returns_dict(self):
        assert isinstance(yukawa_closure_proof(), dict)

    def test_step1_proved(self):
        result = yukawa_closure_proof()
        assert result["step1"]["status"] == "PROVED"

    def test_step1_pi_kR_in_numerical(self):
        result = yukawa_closure_proof()
        assert "37" in result["step1"]["numerical"]

    def test_step2_derived(self):
        result = yukawa_closure_proof()
        assert "DERIVED" in result["step2"]["status"]

    def test_step2_phi0_in_numerical(self):
        result = yukawa_closure_proof()
        assert "1.0" in result["step2"]["numerical"]

    def test_step3_derived(self):
        result = yukawa_closure_proof()
        assert "DERIVED" in result["step3"]["status"]

    def test_step3_forms_identical(self):
        result = yukawa_closure_proof()
        assert result["step3"]["forms_identical"] is True

    def test_step3_lambda_eff_value(self):
        result = yukawa_closure_proof()
        assert "0.16" in result["step3"]["numerical"]

    def test_corollary_predicted(self):
        result = yukawa_closure_proof()
        assert "PREDICTED" in result["corollary"]["status"]

    def test_corollary_electron_exact_pct(self):
        result = yukawa_closure_proof()
        assert result["corollary"]["electron_exact_pct"] < 1.0

    def test_qed_present(self):
        result = yukawa_closure_proof()
        assert "Q.E.D." in result["qed"]
        assert "74" in result["qed"]
        assert "37" in result["qed"]

    def test_theorem_statement(self):
        result = yukawa_closure_proof()
        assert "Ŷ₅" in result["theorem"]
        assert "geometrically derived" in result["theorem"]
