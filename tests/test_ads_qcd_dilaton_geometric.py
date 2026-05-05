# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_ads_qcd_dilaton_geometric.py
=========================================
Tests for Pillar 171 — AdS/QCD Dilaton Geometric Derivation.

Theory, scientific direction, and framework: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""

import math
import pytest

from src.core.ads_qcd_dilaton_geometric import (
    N_W, K_CS, PI_KR, M_PL_GEV, M_KK_GEV,
    RHO_MESON_PDG_GEV, LAMBDA_QCD_PDG_MEV, LAMBDA_QCD_PDG_GEV,
    C_LAT, R_DIL_ERLICH,
    r_dil_geometric, m_kk_from_geometry, rho_meson_rs1,
    dilaton_slope_kappa, lambda_qcd_geometric, string_tension,
    proton_mass_estimate, erlich_comparison, sensitivity_analysis,
    pillar171_summary, pillar171_full_report,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr_equals_k_cs_over_2(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-12)

    def test_m_pl_gev_order_of_magnitude(self):
        assert 1e18 < M_PL_GEV < 1e20

    def test_m_kk_gev_positive(self):
        assert M_KK_GEV > 0

    def test_m_kk_gev_order_of_magnitude(self):
        assert 100.0 < M_KK_GEV < 1e5

    def test_rho_meson_pdg_gev(self):
        assert RHO_MESON_PDG_GEV == pytest.approx(0.775, rel=1e-9)

    def test_lambda_qcd_pdg_mev(self):
        assert LAMBDA_QCD_PDG_MEV == pytest.approx(210.0, rel=1e-9)

    def test_lambda_qcd_pdg_gev_consistent(self):
        assert LAMBDA_QCD_PDG_GEV == pytest.approx(LAMBDA_QCD_PDG_MEV / 1000.0, rel=1e-9)

    def test_c_lat_value(self):
        assert C_LAT == pytest.approx(2.84, rel=1e-9)

    def test_r_dil_erlich(self):
        assert R_DIL_ERLICH == pytest.approx(3.83, rel=1e-9)


class TestRDilGeometric:
    def test_default_value(self):
        r = r_dil_geometric()
        assert r == pytest.approx(math.sqrt(74.0 / 5.0), rel=1e-12)

    def test_default_value_numerical(self):
        r = r_dil_geometric()
        assert r == pytest.approx(3.8471, rel=1e-3)

    def test_erlich_agreement_within_1pct(self):
        r = r_dil_geometric()
        assert abs(r - R_DIL_ERLICH) / R_DIL_ERLICH < 0.01

    def test_erlich_agreement_within_0p5pct(self):
        r = r_dil_geometric()
        assert abs(r - R_DIL_ERLICH) / R_DIL_ERLICH < 0.005

    def test_formula_sqrt_kcs_over_nw(self):
        for n_w, k_cs in [(5, 74), (1, 9), (2, 16), (3, 36)]:
            r = r_dil_geometric(n_w=n_w, k_cs=k_cs)
            assert r == pytest.approx(math.sqrt(float(k_cs) / float(n_w)), rel=1e-12)

    def test_increases_with_k_cs(self):
        r1 = r_dil_geometric(n_w=5, k_cs=74)
        r2 = r_dil_geometric(n_w=5, k_cs=100)
        assert r2 > r1

    def test_decreases_with_n_w(self):
        r1 = r_dil_geometric(n_w=5, k_cs=74)
        r2 = r_dil_geometric(n_w=10, k_cs=74)
        assert r2 < r1

    def test_raises_on_zero_n_w(self):
        with pytest.raises(ValueError):
            r_dil_geometric(n_w=0, k_cs=74)

    def test_raises_on_negative_n_w(self):
        with pytest.raises(ValueError):
            r_dil_geometric(n_w=-1, k_cs=74)

    def test_raises_on_zero_k_cs(self):
        with pytest.raises(ValueError):
            r_dil_geometric(n_w=5, k_cs=0)

    def test_raises_on_negative_k_cs(self):
        with pytest.raises(ValueError):
            r_dil_geometric(n_w=5, k_cs=-74)

    def test_value_greater_than_1(self):
        assert r_dil_geometric() > 1.0

    def test_value_less_than_10(self):
        assert r_dil_geometric() < 10.0


class TestMKKFromGeometry:
    def test_default_positive(self):
        m = m_kk_from_geometry()
        assert m > 0

    def test_default_consistent_with_constant(self):
        m = m_kk_from_geometry()
        assert m == pytest.approx(M_KK_GEV, rel=1e-9)

    def test_formula_correctness(self):
        m = m_kk_from_geometry(m_pl_gev=1e19, pi_kr=37.0)
        assert m == pytest.approx(1e19 * math.exp(-37.0), rel=1e-9)

    def test_raises_on_zero_m_pl(self):
        with pytest.raises(ValueError):
            m_kk_from_geometry(m_pl_gev=0)

    def test_raises_on_negative_m_pl(self):
        with pytest.raises(ValueError):
            m_kk_from_geometry(m_pl_gev=-1e19)

    def test_raises_on_zero_pi_kr(self):
        with pytest.raises(ValueError):
            m_kk_from_geometry(pi_kr=0)

    def test_decreases_with_pi_kr(self):
        m1 = m_kk_from_geometry(pi_kr=37.0)
        m2 = m_kk_from_geometry(pi_kr=40.0)
        assert m2 < m1

    def test_scales_with_m_pl(self):
        m1 = m_kk_from_geometry(m_pl_gev=1e19)
        m2 = m_kk_from_geometry(m_pl_gev=2e19)
        assert m2 == pytest.approx(2.0 * m1, rel=1e-9)


class TestRhoMesonRS1:
    def test_returns_dict(self):
        r = rho_meson_rs1()
        assert isinstance(r, dict)

    def test_m_rho_gev_positive(self):
        r = rho_meson_rs1()
        assert r["m_rho_gev"] > 0

    def test_m_rho_mev_consistent(self):
        r = rho_meson_rs1()
        assert r["m_rho_mev"] == pytest.approx(r["m_rho_gev"] * 1e3, rel=1e-9)

    def test_m_rho_pdg_correct(self):
        r = rho_meson_rs1()
        assert r["m_rho_pdg_gev"] == pytest.approx(0.775, rel=1e-9)

    def test_m_rho_within_10pct_of_pdg(self):
        r = rho_meson_rs1()
        assert abs(r["m_rho_gev"] - 0.775) / 0.775 < 0.10

    def test_m_rho_formula(self):
        r = rho_meson_rs1()
        expected = M_KK_GEV / PI_KR**2
        assert r["m_rho_gev"] == pytest.approx(expected, rel=1e-9)

    def test_fractional_error_positive(self):
        r = rho_meson_rs1()
        assert r["fractional_error"] >= 0

    def test_fractional_error_less_than_5pct(self):
        r = rho_meson_rs1()
        assert r["fractional_error"] < 0.05

    def test_raises_on_zero_pi_kr(self):
        with pytest.raises(ValueError):
            rho_meson_rs1(pi_kr=0)

    def test_raises_on_zero_m_pl(self):
        with pytest.raises(ValueError):
            rho_meson_rs1(m_pl_gev=0)


class TestDilatonSlopeKappa:
    def test_returns_dict(self):
        d = dilaton_slope_kappa()
        assert isinstance(d, dict)

    def test_kappa_gev_positive(self):
        d = dilaton_slope_kappa()
        assert d["kappa_gev"] > 0

    def test_m_rho_from_kappa_equals_2kappa(self):
        d = dilaton_slope_kappa()
        assert d["m_rho_from_kappa_gev"] == pytest.approx(2.0 * d["kappa_gev"], rel=1e-9)

    def test_regge_slope_equals_kappa_squared(self):
        d = dilaton_slope_kappa()
        assert d["regge_slope_gev2"] == pytest.approx(d["kappa_gev"]**2, rel=1e-9)

    def test_kappa_formula(self):
        d = dilaton_slope_kappa()
        expected_kappa = M_KK_GEV / (2.0 * PI_KR**2)
        assert d["kappa_gev"] == pytest.approx(expected_kappa, rel=1e-9)

    def test_raises_on_zero_n_w(self):
        with pytest.raises(ValueError):
            dilaton_slope_kappa(n_w=0)

    def test_raises_on_zero_k_cs(self):
        with pytest.raises(ValueError):
            dilaton_slope_kappa(k_cs=0)


class TestLambdaQCDGeometric:
    def test_returns_dict(self):
        r = lambda_qcd_geometric()
        assert isinstance(r, dict)

    def test_lambda_qcd_gev_positive(self):
        r = lambda_qcd_geometric()
        assert r["lambda_qcd_gev"] > 0

    def test_lambda_qcd_mev_consistent(self):
        r = lambda_qcd_geometric()
        assert r["lambda_qcd_mev"] == pytest.approx(r["lambda_qcd_gev"] * 1e3, rel=1e-9)

    def test_lambda_qcd_mev_order_of_magnitude(self):
        r = lambda_qcd_geometric()
        assert 50.0 < r["lambda_qcd_mev"] < 1000.0

    def test_lambda_qcd_within_factor_2_of_pdg(self):
        r = lambda_qcd_geometric()
        assert r["ratio_to_pdg"] < 2.0
        assert r["ratio_to_pdg"] > 0.1

    def test_r_dil_um_correct(self):
        r = lambda_qcd_geometric()
        assert r["r_dil_um"] == pytest.approx(math.sqrt(74.0 / 5.0), rel=1e-9)

    def test_r_dil_agreement_pct_present(self):
        r = lambda_qcd_geometric()
        assert "r_dil_agreement_pct" in r
        assert r["r_dil_agreement_pct"] > 0

    def test_r_dil_agreement_within_1pct(self):
        r = lambda_qcd_geometric()
        assert abs(r["r_dil_um"] - R_DIL_ERLICH) / R_DIL_ERLICH < 0.01

    def test_status_derived(self):
        r = lambda_qcd_geometric()
        assert r["status"] == "DERIVED"

    def test_fractional_error_finite(self):
        r = lambda_qcd_geometric()
        assert math.isfinite(r["fractional_error"])

    def test_formula_chain(self):
        r = lambda_qcd_geometric()
        m_kk = M_PL_GEV * math.exp(-PI_KR)
        m_rho = m_kk / PI_KR**2
        r_dil = math.sqrt(float(K_CS) / float(N_W))
        lam_expected = m_rho / r_dil
        assert r["lambda_qcd_gev"] == pytest.approx(lam_expected, rel=1e-9)


class TestStringTension:
    def test_returns_dict(self):
        st = string_tension()
        assert isinstance(st, dict)

    def test_sigma_positive(self):
        st = string_tension()
        assert st["sigma_gev2"] > 0

    def test_sigma_finite(self):
        st = string_tension()
        assert math.isfinite(st["sigma_gev2"])

    def test_sigma_lattice_correct(self):
        st = string_tension()
        assert st["sigma_lattice_gev2"] == pytest.approx(0.18, rel=1e-9)

    def test_sigma_ratio_positive(self):
        st = string_tension()
        assert st["ratio_to_lattice"] > 0

    def test_sigma_order_of_magnitude(self):
        st = string_tension()
        assert st["ratio_to_lattice"] < 3.0

    def test_consistency_string_present(self):
        st = string_tension()
        assert "consistency" in st


class TestProtonMassEstimate:
    def test_returns_dict(self):
        mp = proton_mass_estimate()
        assert isinstance(mp, dict)

    def test_m_p_gev_positive(self):
        mp = proton_mass_estimate()
        assert mp["m_p_gev"] > 0

    def test_m_p_pdg_correct(self):
        mp = proton_mass_estimate()
        assert mp["m_p_pdg_gev"] == pytest.approx(0.938272, rel=1e-4)

    def test_c_lat_correct(self):
        mp = proton_mass_estimate()
        assert mp["c_lat"] == pytest.approx(2.84, rel=1e-9)

    def test_c_lat_status_external(self):
        mp = proton_mass_estimate()
        assert "PERMANENT_EXTERNAL_INPUT" in mp["c_lat_status"]

    def test_m_p_within_factor_3_of_pdg(self):
        mp = proton_mass_estimate()
        assert 0.1 < mp["ratio_to_pdg"] < 5.0

    def test_m_p_formula(self):
        mp = proton_mass_estimate()
        lam = mp["lambda_qcd_gev"]
        assert mp["m_p_gev"] == pytest.approx(C_LAT * lam, rel=1e-9)


class TestErlichComparison:
    def test_returns_dict(self):
        c = erlich_comparison()
        assert isinstance(c, dict)

    def test_r_dil_um_correct(self):
        c = erlich_comparison()
        assert c["r_dil_um"] == pytest.approx(math.sqrt(74.0 / 5.0), rel=1e-9)

    def test_r_dil_erlich_correct(self):
        c = erlich_comparison()
        assert c["r_dil_erlich"] == pytest.approx(3.83, rel=1e-9)

    def test_agreement_pct_above_99(self):
        c = erlich_comparison()
        assert c["agreement_pct"] > 99.0

    def test_discrepancy_pct_below_1(self):
        c = erlich_comparison()
        assert c["discrepancy_pct"] < 1.0

    def test_difference_small(self):
        c = erlich_comparison()
        assert abs(c["difference"]) < 0.1

    def test_status_derived(self):
        c = erlich_comparison()
        assert c["status"] == "DERIVED"

    def test_formula_present(self):
        c = erlich_comparison()
        assert "sqrt" in c["formula"].lower() or "sqrt" in c["formula"]


class TestSensitivityAnalysis:
    def test_returns_dict(self):
        s = sensitivity_analysis()
        assert isinstance(s, dict)

    def test_central_value_correct(self):
        s = sensitivity_analysis()
        assert s["r_dil_central"] == pytest.approx(r_dil_geometric(), rel=1e-9)

    def test_kcs_plus_increases_r_dil(self):
        s = sensitivity_analysis()
        assert s["r_dil_kcs_plus_1pct"] > s["r_dil_central"]

    def test_kcs_minus_decreases_r_dil(self):
        s = sensitivity_analysis()
        assert s["r_dil_kcs_minus_1pct"] < s["r_dil_central"]

    def test_nw_plus_decreases_r_dil(self):
        s = sensitivity_analysis()
        assert s["r_dil_nw_plus_1pct"] < s["r_dil_central"]

    def test_nw_minus_increases_r_dil(self):
        s = sensitivity_analysis()
        assert s["r_dil_nw_minus_1pct"] > s["r_dil_central"]

    def test_frac_sensitivity_kcs_positive(self):
        s = sensitivity_analysis()
        assert s["frac_sensitivity_KCS"] > 0

    def test_frac_sensitivity_nw_negative(self):
        s = sensitivity_analysis()
        assert s["frac_sensitivity_NW"] < 0

    def test_half_power_law_kcs(self):
        s = sensitivity_analysis()
        assert s["frac_sensitivity_KCS"] == pytest.approx(0.5, rel=0.05)

    def test_half_power_law_nw(self):
        s = sensitivity_analysis()
        assert s["frac_sensitivity_NW"] == pytest.approx(-0.5, rel=0.05)


class TestPillar171Summary:
    def test_returns_dict(self):
        s = pillar171_summary()
        assert isinstance(s, dict)

    def test_pillar_id(self):
        s = pillar171_summary()
        assert s["pillar"] == 171

    def test_n_w_k_cs_pi_kr(self):
        s = pillar171_summary()
        assert s["n_w"] == 5
        assert s["k_cs"] == 74
        assert s["pi_kr"] == pytest.approx(37.0, rel=1e-9)

    def test_r_dil_um_present(self):
        s = pillar171_summary()
        assert s["r_dil_um"] == pytest.approx(math.sqrt(74.0 / 5.0), rel=1e-9)

    def test_r_dil_agreement_pct_high(self):
        s = pillar171_summary()
        assert s["r_dil_agreement_pct"] > 99.0

    def test_lambda_qcd_mev_present(self):
        s = pillar171_summary()
        assert s["lambda_qcd_mev"] > 0

    def test_status_derived(self):
        s = pillar171_summary()
        assert s["status"] == "DERIVED"

    def test_dilaton_status_derived(self):
        s = pillar171_summary()
        assert s["dilaton_status"] == "DERIVED"

    def test_permanent_external_input_mentioned(self):
        s = pillar171_summary()
        assert "C_lat" in s["permanent_external_input"] or "2.84" in s["permanent_external_input"]

    def test_open_issue_present(self):
        s = pillar171_summary()
        assert len(s["open_issue"]) > 10


class TestPillar171FullReport:
    def test_returns_dict(self):
        r = pillar171_full_report()
        assert isinstance(r, dict)

    def test_pillar_171(self):
        r = pillar171_full_report()
        assert r["pillar"] == 171

    def test_geometry_section(self):
        r = pillar171_full_report()
        g = r["geometry"]
        assert g["n_w"] == 5
        assert g["k_cs"] == 74
        assert g["pi_kr"] == pytest.approx(37.0, rel=1e-9)

    def test_dilaton_section(self):
        r = pillar171_full_report()
        d = r["dilaton"]
        assert d["r_dil_um"] > 0
        assert d["agreement_pct"] > 99.0

    def test_rho_meson_section(self):
        r = pillar171_full_report()
        rho = r["rho_meson"]
        assert rho["m_rho_gev"] > 0
        assert rho["m_rho_pdg_gev"] == pytest.approx(0.775, rel=1e-9)

    def test_lambda_qcd_section(self):
        r = pillar171_full_report()
        lam = r["lambda_qcd"]
        assert lam["lambda_qcd_gev"] > 0
        assert lam["status"] == "DERIVED"

    def test_string_tension_section(self):
        r = pillar171_full_report()
        st = r["string_tension"]
        assert st["sigma_gev2"] > 0

    def test_proton_mass_section(self):
        r = pillar171_full_report()
        pm = r["proton_mass"]
        assert pm["m_p_gev"] > 0

    def test_sensitivity_section(self):
        r = pillar171_full_report()
        assert "sensitivity" in r

    def test_epistemic_label_derived(self):
        r = pillar171_full_report()
        assert r["epistemic_label"] == "DERIVED"

    def test_open_issues_list(self):
        r = pillar171_full_report()
        assert isinstance(r["open_issues"], list)
        assert len(r["open_issues"]) >= 2

    def test_status_derived(self):
        r = pillar171_full_report()
        assert r["status"] == "DERIVED"
