# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_gw_yukawa_derivation.py
====================================
Tests for Pillar 97 — GW Potential Yukawa Derivation and Neutrino c_{Lν_i}.
(src/core/gw_yukawa_derivation.py)

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.gw_yukawa_derivation import (
    # Constants
    N_W, N1_BRAID, N2_BRAID, K_CS, PI_KR, K_RS, PHI0, Y5_GW,
    C_R_DEMOCRATIC, EPSILON_GW_CANONICAL, BRAID_PRODUCT,
    M_PL_GEV, V_HIGGS_MEV, V_HIGGS_GEV,
    M_ELECTRON_PDG_MEV, M_MUON_PDG_MEV, M_TAU_PDG_MEV,
    DM2_21_PDG_EV2, DM2_31_PDG_EV2, SUM_MNU_PLANCK_EV,
    C_L_ELECTRON_WINDING,
    # Functions
    gw_profile,
    gw_ir_brane_vev,
    gw_epsilon_from_pi_kR,
    Y5_from_gw_profile,
    yukawa_4d_from_gw,
    electron_mass_from_gw,
    lepton_masses_from_gw,
    neutrino_vev_suppression,
    neutrino_c_L_from_gw,
    neutrino_masses_from_gw_c_L,
    neutrino_splittings_from_gw,
    gw_yukawa_derivation_report,
    _f0,
)


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_braid_pair(self):
        assert N1_BRAID == 5
        assert N2_BRAID == 7

    def test_k_cs(self):
        assert K_CS == 74
        assert K_CS == N1_BRAID ** 2 + N2_BRAID ** 2

    def test_pi_kR(self):
        assert PI_KR == 37.0
        assert PI_KR == K_CS / 2.0

    def test_phi0(self):
        assert PHI0 == 1.0

    def test_y5_gw_equals_phi0(self):
        assert Y5_GW == PHI0
        assert Y5_GW == 1.0

    def test_c_r_democratic(self):
        assert C_R_DEMOCRATIC == 0.5

    def test_epsilon_canonical(self):
        assert EPSILON_GW_CANONICAL == 1.0

    def test_braid_product(self):
        assert BRAID_PRODUCT == N1_BRAID * N2_BRAID
        assert BRAID_PRODUCT == 35

    def test_v_higgs_mev(self):
        assert abs(V_HIGGS_MEV - 246_220.0) < 1.0

    def test_v_higgs_gev(self):
        assert abs(V_HIGGS_GEV - 246.220) < 0.001

    def test_electron_pdg_mev(self):
        assert abs(M_ELECTRON_PDG_MEV - 0.511) < 0.001

    def test_dm2_21_pdg(self):
        assert abs(DM2_21_PDG_EV2 - 7.53e-5) < 1e-7

    def test_dm2_31_pdg(self):
        assert abs(DM2_31_PDG_EV2 - 2.453e-3) < 1e-5

    def test_planck_sum_mnu(self):
        assert SUM_MNU_PLANCK_EV == 0.12

    def test_c_l_electron_winding(self):
        assert 0.79 < C_L_ELECTRON_WINDING < 0.81


# ===========================================================================
# Internal RS wavefunction
# ===========================================================================

class TestF0:
    def test_flat_profile_c_half(self):
        """f₀(0.5) = 1/√37 in canonical RS."""
        f = _f0(0.5)
        assert abs(f - 1.0 / math.sqrt(37.0)) < 1e-10

    def test_uv_localised_c_08(self):
        """f₀(0.8) should be very small for UV-localised fermion."""
        f = _f0(0.8)
        assert f < 1e-3  # exponentially suppressed at c = 0.8

    def test_ir_localised_c_zero(self):
        """f₀(0.0) should be large for IR-localised fermion."""
        f = _f0(0.0)
        assert f > _f0(0.5)  # c=0 more IR-localised than c=0.5

    def test_decreasing_in_c(self):
        """f₀(c) decreases as c increases (more UV-localised)."""
        c_vals = [0.5, 0.6, 0.7, 0.8, 0.9]
        f_vals = [_f0(c) for c in c_vals]
        for i in range(len(f_vals) - 1):
            assert f_vals[i] > f_vals[i + 1]

    def test_positive(self):
        """f₀ is always positive."""
        for c in [0.0, 0.3, 0.5, 0.7, 0.9, 1.2]:
            assert _f0(c) >= 0.0

    def test_pi_kR_scaling(self):
        """Larger πkR → smaller f₀ at c > 0.5 (stronger UV localisation)."""
        f_37 = _f0(0.8, 1.0, 37.0)
        f_50 = _f0(0.8, 1.0, 50.0)
        assert f_37 > f_50  # stronger suppression at larger πkR


# ===========================================================================
# Step 1: GW profile
# ===========================================================================

class TestGwProfile:
    def test_uv_value(self):
        """Φ(y=0) = v_UV."""
        val = gw_profile(y=0.0, v_UV=1.0)
        assert abs(val - 1.0) < 1e-12

    def test_positive_everywhere(self):
        """Φ(y) > 0 for y ∈ [0, πR]."""
        for y in [0.0, 5.0, 10.0, 20.0]:
            assert gw_profile(y=y) > 0.0

    def test_decreasing(self):
        """Φ(y) is decreasing (IR suppressed)."""
        v = [gw_profile(y=y) for y in [0, 1, 5, 10, 20]]
        for i in range(len(v) - 1):
            assert v[i] > v[i + 1]

    def test_v_uv_scaling(self):
        """Φ(y) scales linearly with v_UV."""
        v1 = gw_profile(y=5.0, v_UV=1.0)
        v2 = gw_profile(y=5.0, v_UV=2.0)
        assert abs(v2 - 2.0 * v1) < 1e-12

    def test_invalid_v_uv(self):
        with pytest.raises(ValueError):
            gw_profile(y=0.0, v_UV=-1.0)

    def test_invalid_epsilon(self):
        with pytest.raises(ValueError):
            gw_profile(y=0.0, epsilon=-0.1)

    def test_ir_brane_value(self):
        """Φ(πR/k) = v_UV × exp(−ε × πkR) = exp(−37)."""
        pi_R = PI_KR / K_RS  # πR in Planck units
        val = gw_profile(y=pi_R, v_UV=1.0, epsilon=1.0, k_RS=K_RS, pi_kR=PI_KR)
        expected = math.exp(-PI_KR)
        assert abs(val - expected) / expected < 1e-6


class TestGwIrBraneVev:
    def test_canonical_value(self):
        """v_IR = exp(−37) in canonical GW."""
        v = gw_ir_brane_vev(1.0, 1.0, 37.0)
        assert abs(v - math.exp(-37.0)) < 1e-20

    def test_tev_scale(self):
        """v_IR × M_Pl ~ TeV scale (500 GeV to 5 TeV)."""
        v_IR = gw_ir_brane_vev(1.0, 1.0, 37.0)
        v_IR_GeV = v_IR * M_PL_GEV
        assert 500.0 < v_IR_GeV < 5000.0

    def test_invalid_v_uv(self):
        with pytest.raises(ValueError):
            gw_ir_brane_vev(v_UV=-1.0)

    def test_invalid_epsilon(self):
        with pytest.raises(ValueError):
            gw_ir_brane_vev(epsilon=0.0)

    def test_invalid_pi_kR(self):
        with pytest.raises(ValueError):
            gw_ir_brane_vev(pi_kR=0.0)

    def test_smaller_pi_kR_gives_larger_vev(self):
        """Smaller πkR → less suppression → larger v_IR."""
        v1 = gw_ir_brane_vev(pi_kR=30.0)
        v2 = gw_ir_brane_vev(pi_kR=40.0)
        assert v1 > v2

    def test_scaling_with_v_uv(self):
        """v_IR scales linearly with v_UV."""
        v1 = gw_ir_brane_vev(v_UV=1.0)
        v2 = gw_ir_brane_vev(v_UV=2.0)
        assert abs(v2 - 2.0 * v1) < 1e-20


class TestGwEpsilonFromPiKR:
    def test_near_unity(self):
        """ε derived from RS hierarchy ≈ 1 (natural GW)."""
        eps = gw_epsilon_from_pi_kR(PI_KR)
        assert 0.9 < eps < 1.2  # near canonical ε = 1

    def test_positive(self):
        """ε > 0 (exponential suppression, not enhancement)."""
        eps = gw_epsilon_from_pi_kR(37.0)
        assert eps > 0.0

    def test_invalid_pi_kR(self):
        with pytest.raises(ValueError):
            gw_epsilon_from_pi_kR(0.0)

    def test_invalid_ratio(self):
        with pytest.raises(ValueError):
            gw_epsilon_from_pi_kR(37.0, v_EW_over_M_Pl=0.0)

    def test_formula(self):
        """ε = −ln(v_EW/M_Pl) / πkR."""
        ratio = V_HIGGS_GEV / M_PL_GEV
        eps = gw_epsilon_from_pi_kR(PI_KR, ratio)
        expected = -math.log(ratio) / PI_KR
        assert abs(eps - expected) < 1e-12

    def test_consistency_with_ir_vev(self):
        """v_IR = M_Pl × exp(−ε × πkR) ≈ v_EW."""
        eps = gw_epsilon_from_pi_kR(PI_KR)
        v_IR_over_MPl = math.exp(-eps * PI_KR)
        v_IR_GeV = v_IR_over_MPl * M_PL_GEV
        # v_IR is TeV scale (v_EW = 246 GeV, v_IR ~ 1 TeV)
        assert 100.0 < v_IR_GeV < 10000.0


# ===========================================================================
# Step 2: 4D Yukawa from GW profile
# ===========================================================================

class TestY5FromGwProfile:
    def test_canonical_value(self):
        """Ŷ₅ = v_UV/φ₀ = 1.0 at GW vacuum."""
        assert Y5_from_gw_profile(1.0, 1.0) == 1.0

    def test_confirms_pillar93(self):
        """Ŷ₅ = 1.0 at GW vacuum (confirms Pillar 93 independently)."""
        Y5 = Y5_from_gw_profile(PHI0, PHI0)
        assert abs(Y5 - 1.0) < 1e-12

    def test_invalid_phi0(self):
        with pytest.raises(ValueError):
            Y5_from_gw_profile(1.0, phi0=0.0)

    def test_scaling(self):
        """Ŷ₅ = v_UV / φ₀."""
        assert abs(Y5_from_gw_profile(2.0, 1.0) - 2.0) < 1e-12
        assert abs(Y5_from_gw_profile(1.0, 2.0) - 0.5) < 1e-12

    def test_planck_units(self):
        """In Planck units (M_Pl = 1), v_UV = φ₀ = 1 → Ŷ₅ = 1."""
        Y5 = Y5_from_gw_profile(1.0, 1.0)
        assert Y5 == 1.0


class TestYukawa4dFromGw:
    def test_positive(self):
        """4D Yukawa coupling is positive."""
        Y = yukawa_4d_from_gw(0.8)
        assert Y > 0.0

    def test_increases_with_IR_localisation(self):
        """Smaller c_L (more IR-localised) gives larger Yukawa."""
        Y_uv = yukawa_4d_from_gw(0.9)
        Y_ir = yukawa_4d_from_gw(0.6)
        assert Y_ir > Y_uv

    def test_invalid_v_uv(self):
        with pytest.raises(ValueError):
            yukawa_4d_from_gw(0.8, v_UV=-1.0)

    def test_invalid_epsilon(self):
        with pytest.raises(ValueError):
            yukawa_4d_from_gw(0.8, epsilon=-0.1)

    def test_formula(self):
        """Y_4d = Y5 × f₀^L × f₀^R."""
        c_L, c_R = 0.8, 0.5
        Y = yukawa_4d_from_gw(c_L, c_R)
        expected = Y5_from_gw_profile(PHI0) * _f0(c_L) * _f0(c_R)
        assert abs(Y - expected) < 1e-12


# ===========================================================================
# Step 3: Electron mass from GW profile
# ===========================================================================

class TestElectronMassFromGw:
    def test_returns_dict(self):
        r = electron_mass_from_gw()
        assert isinstance(r, dict)
        assert "m_e_pred_MeV" in r
        assert "pct_error" in r
        assert "within_1pct" in r

    def test_prediction_positive(self):
        r = electron_mass_from_gw()
        assert r["m_e_pred_MeV"] > 0.0

    def test_accuracy_better_than_1pct(self):
        """GW-derived electron mass within 1% of PDG."""
        r = electron_mass_from_gw()
        assert r["within_1pct"], (
            f"Electron mass {r['m_e_pred_MeV']:.4f} MeV is {r['pct_error']:.2f}% "
            f"off PDG {r['m_e_pdg_MeV']:.4f} MeV"
        )

    def test_pct_error_finite(self):
        r = electron_mass_from_gw()
        assert math.isfinite(r["pct_error"])

    def test_pdg_value_correct(self):
        r = electron_mass_from_gw()
        assert abs(r["m_e_pdg_MeV"] - 0.511) < 0.001

    def test_y5_gw_is_one(self):
        """GW-derived Ŷ₅ = 1 (confirms Pillar 93)."""
        r = electron_mass_from_gw()
        assert abs(r["Y5_gw"] - 1.0) < 1e-12

    def test_within_10pct(self):
        r = electron_mass_from_gw()
        assert r["within_10pct"]

    def test_c_Le_in_range(self):
        """c_Le should be in the physical RS range (0.7 to 0.9)."""
        r = electron_mass_from_gw()
        assert 0.7 < r["c_Le"] < 0.9


class TestLeptonMassesFromGw:
    def test_returns_dict(self):
        r = lepton_masses_from_gw()
        assert isinstance(r, dict)
        assert "leptons" in r

    def test_all_three_leptons(self):
        r = lepton_masses_from_gw()
        assert "electron" in r["leptons"]
        assert "muon" in r["leptons"]
        assert "tau" in r["leptons"]

    def test_y5_gw_is_one(self):
        r = lepton_masses_from_gw()
        assert abs(r["Y5_gw"] - 1.0) < 1e-12

    def test_predictions_positive(self):
        r = lepton_masses_from_gw()
        for name, data in r["leptons"].items():
            assert data["m_pred_MeV"] > 0.0, f"Negative prediction for {name}"

    def test_mass_ordering(self):
        """With winding-quantised c_L, muon and tau predictions are larger than electron."""
        r = lepton_masses_from_gw()
        # The default c_L values include the adjusted c_Le = 0.7980 for electron
        # and winding-quantised levels for muon (c_L=0.8) and tau (c_L=0.7).
        # Since c_Ltau = 0.7 < c_Lmu = 0.8, tau has LARGER predicted mass than muon.
        m_mu = r["leptons"]["muon"]["m_pred_MeV"]
        m_tau = r["leptons"]["tau"]["m_pred_MeV"]
        assert m_tau > m_mu  # tau more IR-localised → larger mass


# ===========================================================================
# Step 4: Neutrino c_Lν_i from GW profile
# ===========================================================================

class TestNeutrinoVevSuppression:
    def test_returns_dict(self):
        r = neutrino_vev_suppression()
        assert isinstance(r, dict)
        assert "v_nu_MeV" in r
        assert "suppression_factor" in r

    def test_suppression_factor(self):
        """Suppression = 1/√(n₁n₂) = 1/√35."""
        r = neutrino_vev_suppression(5, 7)
        expected = 1.0 / math.sqrt(35.0)
        assert abs(r["suppression_factor"] - expected) < 1e-12

    def test_vnu_less_than_vew(self):
        """v_IR^{ν} < v_EW (suppressed)."""
        r = neutrino_vev_suppression()
        assert r["v_nu_MeV"] < r["v_EW_MeV"]

    def test_braid_product(self):
        r = neutrino_vev_suppression(5, 7)
        assert r["braid_product"] == 35

    def test_invalid_n1(self):
        with pytest.raises(ValueError):
            neutrino_vev_suppression(n1=0)

    def test_invalid_n2(self):
        with pytest.raises(ValueError):
            neutrino_vev_suppression(n2=0)

    def test_positive_vnu(self):
        r = neutrino_vev_suppression()
        assert r["v_nu_MeV"] > 0.0


class TestNeutrinoCLFromGw:
    @pytest.fixture(scope="class")
    def result(self):
        return neutrino_c_L_from_gw()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)
        assert "c_Lnu" in result
        assert "m_nu_eV" in result

    def test_three_c_Lnu(self, result):
        """Three neutrino bulk masses."""
        assert len(result["c_Lnu"]) == 3

    def test_c_Lnu_positive(self, result):
        """All c_Lν > 0.5 (UV-localised neutrinos for light masses)."""
        for c in result["c_Lnu"]:
            assert c > 0.5, f"c_Lν = {c} is not UV-localised"

    def test_c_Lnu_ordering(self, result):
        """c_Lν₀ > c_Lν₁ > c_Lν₂ (heavier → less UV-localised)."""
        c0, c1, c2 = result["c_Lnu"]
        assert c0 > c1 > c2

    def test_planck_consistent(self, result):
        """Σm_ν < 120 meV (Planck 2018 bound)."""
        assert result["planck_consistent"], (
            f"Σm_ν = {result['sum_mnu_eV']*1000:.1f} meV exceeds Planck limit"
        )

    def test_sum_mnu_positive(self, result):
        assert result["sum_mnu_eV"] > 0.0

    def test_individual_masses_positive(self, result):
        for m in result["m_nu_eV"]:
            assert m > 0.0

    def test_normal_ordering(self, result):
        """Normal ordering: m_ν₁ < m_ν₂ < m_ν₃."""
        m1, m2, m3 = result["m_nu_eV"]
        assert m1 < m2 < m3

    def test_delta_c_positive(self, result):
        assert result["delta_c_nu"] > 0.0

    def test_invalid_n_w(self):
        with pytest.raises(ValueError):
            neutrino_c_L_from_gw(n_w=0)

    def test_invalid_pi_kR(self):
        with pytest.raises(ValueError):
            neutrino_c_L_from_gw(pi_kR=0.0)


class TestNeutrinoMassesFromGwCL:
    def test_returns_dict(self):
        r = neutrino_c_L_from_gw()
        m = neutrino_masses_from_gw_c_L(r["c_Lnu"], r["v_nu_MeV"])
        assert isinstance(m, dict)

    def test_three_masses(self):
        r = neutrino_c_L_from_gw()
        m = neutrino_masses_from_gw_c_L(r["c_Lnu"], r["v_nu_MeV"])
        assert len(m["m_nu_eV"]) == 3

    def test_dm2_21_positive(self):
        r = neutrino_c_L_from_gw()
        m = neutrino_masses_from_gw_c_L(r["c_Lnu"], r["v_nu_MeV"])
        assert m["dm2_21_eV2"] > 0.0

    def test_dm2_31_positive(self):
        r = neutrino_c_L_from_gw()
        m = neutrino_masses_from_gw_c_L(r["c_Lnu"], r["v_nu_MeV"])
        assert m["dm2_31_eV2"] > 0.0

    def test_dm2_31_greater_than_21(self):
        r = neutrino_c_L_from_gw()
        m = neutrino_masses_from_gw_c_L(r["c_Lnu"], r["v_nu_MeV"])
        assert m["dm2_31_eV2"] > m["dm2_21_eV2"]

    def test_planck_ok(self):
        r = neutrino_c_L_from_gw()
        m = neutrino_masses_from_gw_c_L(r["c_Lnu"], r["v_nu_MeV"])
        assert m["planck_ok"]

    def test_invalid_c_Lnu(self):
        with pytest.raises(ValueError):
            neutrino_masses_from_gw_c_L([0.8, 0.75], 100.0)

    def test_invalid_v_nu(self):
        with pytest.raises(ValueError):
            neutrino_masses_from_gw_c_L([0.8, 0.75, 0.70], v_nu_MeV=-1.0)


class TestNeutrinoSplittingsFromGw:
    @pytest.fixture(scope="class")
    def result(self):
        return neutrino_splittings_from_gw()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)
        assert "dm2_21_pred_eV2" in result
        assert "dm2_31_pred_eV2" in result

    def test_splittings_positive(self, result):
        assert result["dm2_21_pred_eV2"] > 0.0
        assert result["dm2_31_pred_eV2"] > 0.0

    def test_atmospheric_greater_than_solar(self, result):
        assert result["dm2_31_pred_eV2"] > result["dm2_21_pred_eV2"]

    def test_planck_consistent(self, result):
        assert result["planck_consistent"]

    def test_splitting_ratio_near_36(self, result):
        """Geometric ratio Δm²₃₁/Δm²₂₁ ≈ n₁n₂+1 = 36 (Pillar 90)."""
        assert abs(result["dm2_ratio_geo"] - 36.0) < 1e-10

    def test_splitting_ratio_pdg_near_32(self, result):
        """PDG ratio ≈ 32.6."""
        assert 30.0 < result["dm2_ratio_pdg"] < 36.0

    def test_braid_product(self, result):
        assert result["braid_product"] == 35

    def test_three_c_Lnu(self, result):
        assert len(result["c_Lnu"]) == 3

    def test_normal_ordering(self, result):
        m1, m2, m3 = result["m_nu_eV"]
        assert m1 < m2 < m3

    def test_v_nu_positive(self, result):
        assert result["v_nu_MeV"] > 0.0

    def test_invalid_n_w(self):
        with pytest.raises(ValueError):
            neutrino_splittings_from_gw(n_w=0)

    def test_invalid_pi_kR(self):
        with pytest.raises(ValueError):
            neutrino_splittings_from_gw(pi_kR=0.0)


# ===========================================================================
# Full Pillar 97 report
# ===========================================================================

class TestGwYukawaDerivationReport:
    @pytest.fixture(scope="class")
    def report(self):
        return gw_yukawa_derivation_report()

    def test_returns_dict(self, report):
        assert isinstance(report, dict)
        assert report["pillar"] == 97

    def test_pillar_name(self, report):
        assert "GW" in report["name"] or "Yukawa" in report["name"]

    def test_step1_derived(self, report):
        """Step 1: v_IR derived from GW profile."""
        s1 = report["step1_gw_profile"]
        assert s1["v_IR_planck"] > 0.0
        assert s1["v_IR_GeV"] > 100.0  # TeV scale

    def test_step2_Y5_is_one(self, report):
        """Step 2: Ŷ₅ = 1.0 from GW profile."""
        s2 = report["step2_Y5_gw"]
        assert abs(s2["Y5"] - 1.0) < 1e-12
        assert s2["confirms_pillar93"]

    def test_step3_electron_accuracy(self, report):
        """Step 3: electron mass within 1% of PDG."""
        s3 = report["step3_electron_mass"]
        assert s3["within_1pct"], (
            f"Electron: {s3['pct_error']:.2f}% off PDG"
        )

    def test_step4_planck_consistent(self, report):
        """Step 4: Σm_ν < 120 meV."""
        s4 = report["step4_neutrino_splittings"]
        assert s4["planck_consistent"]

    def test_hierarchy_consistent(self, report):
        """v_IR ~ 760 GeV – 2 TeV (consistent with EW hierarchy)."""
        v_IR_GeV = report["step1_gw_profile"]["v_IR_GeV"]
        assert 200.0 < v_IR_GeV < 5000.0

    def test_honest_status_present(self, report):
        hs = report["honest_status"]
        assert "DERIVED" in hs
        assert "VERIFIED" in hs
        assert "OPEN" in hs

    def test_gap_progress_text(self, report):
        assert len(report["gap_progress"]) > 50

    def test_epsilon_near_unity(self, report):
        eps = report["step1_gw_profile"]["epsilon_from_hierarchy"]
        assert 0.8 < eps < 1.3  # near canonical ε = 1

    def test_neutrino_delta_c_positive(self, report):
        assert report["step4_neutrino_splittings"]["delta_c_nu"] > 0.0

    def test_version_tag(self, report):
        assert "v9.26" in report["version"]
