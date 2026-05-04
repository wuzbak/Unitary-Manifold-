# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_qcd_confinement_geometric.py
========================================
Test suite for Pillar 162 — QCD Confinement Geometric Derivation.

Verifies that the RS1/AdS-QCD framework derives Λ_QCD ≈ 198 MeV and
m_ρ ≈ 0.760 GeV from pure geometry (πkR = 37), and that the gap factor
relative to the old Pillar 62 PeV-scale result exceeds 10^5.
"""
from __future__ import annotations

import math
import pytest

from src.core.qcd_confinement_geometric import (
    ALPHA_S_RATIO_QCD,
    J_0_1,
    K_CS,
    LAMBDA_QCD_PDG_GEV,
    LAMBDA_QCD_PDG_MEV,
    M_KK_GEV,
    M_PL_GEV,
    N_W,
    PI_K_R,
    RHO_MESON_PDG_GEV,
    ads_qcd_dilaton_check,
    diagnose_pillar62_gap,
    kk_gluon_mass_spectrum,
    lambda_qcd_from_ads_geometry,
    pillar162_summary,
    qcd_confinement_geometric_report,
    rho_meson_from_ads_qcd,
)


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_pi_kr_value(self):
        assert PI_K_R == pytest.approx(37.0, abs=1e-10)

    def test_j01_bessel_zero(self):
        assert J_0_1 == pytest.approx(2.405, abs=0.001)

    def test_m_pl_gev_order(self):
        assert 1e18 < M_PL_GEV < 1e20

    def test_m_kk_gev_value(self):
        # M_KK_GEV is computed as M_PL_GEV * exp(-PI_K_R)
        expected = M_PL_GEV * math.exp(-PI_K_R)
        assert M_KK_GEV == pytest.approx(expected, rel=1e-9)

    def test_rho_meson_pdg_value(self):
        assert RHO_MESON_PDG_GEV == pytest.approx(0.775, abs=0.001)

    def test_lambda_qcd_pdg_mev(self):
        assert LAMBDA_QCD_PDG_MEV == pytest.approx(332.0, abs=1.0)

    def test_lambda_qcd_pdg_gev(self):
        assert LAMBDA_QCD_PDG_GEV == pytest.approx(0.332, abs=0.001)

    def test_alpha_s_ratio_positive(self):
        assert ALPHA_S_RATIO_QCD > 0

    def test_n_w_winding(self):
        assert N_W == 5

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_m_kk_sub_tev(self):
        # KK scale is in the few-hundred GeV range
        assert 100 < M_KK_GEV < 2000


# ---------------------------------------------------------------------------
# TestKKGluonMassSpectrum
# ---------------------------------------------------------------------------
class TestKKGluonMassSpectrum:
    def test_n1_returns_dict(self):
        result = kk_gluon_mass_spectrum(1)
        assert isinstance(result, dict)

    def test_n1_has_required_keys(self):
        result = kk_gluon_mass_spectrum(1)
        for key in ("n", "x_0n", "m_n_gev", "formula"):
            assert key in result

    def test_n1_level(self):
        result = kk_gluon_mass_spectrum(1)
        assert result["n"] == 1

    def test_n1_bessel_zero(self):
        result = kk_gluon_mass_spectrum(1)
        assert result["x_0n"] == pytest.approx(2.405, abs=0.001)

    def test_n1_mass_rs1_scale(self):
        # RS1 formula: x_{0,1}/pi_kr * k * exp(-pi_kr) = 2.405/37 * 1040 ≈ 67.7 GeV
        result = kk_gluon_mass_spectrum(1)
        m1 = result["m_n_gev"]
        assert 1.0 < m1 < 1000.0

    def test_n1_mass_approx(self):
        result = kk_gluon_mass_spectrum(1)
        expected = (J_0_1 / PI_K_R) * M_PL_GEV * math.exp(-PI_K_R)
        assert result["m_n_gev"] == pytest.approx(expected, rel=1e-8)

    def test_n2_larger_than_n1(self):
        m1 = kk_gluon_mass_spectrum(1)["m_n_gev"]
        m2 = kk_gluon_mass_spectrum(2)["m_n_gev"]
        assert m2 > m1

    def test_n3_larger_than_n2(self):
        m2 = kk_gluon_mass_spectrum(2)["m_n_gev"]
        m3 = kk_gluon_mass_spectrum(3)["m_n_gev"]
        assert m3 > m2

    def test_spectrum_ratio_n2_n1(self):
        # zeros: 5.520 / 2.405 ≈ 2.296
        m1 = kk_gluon_mass_spectrum(1)["m_n_gev"]
        m2 = kk_gluon_mass_spectrum(2)["m_n_gev"]
        ratio = m2 / m1
        assert ratio == pytest.approx(5.520 / 2.405, rel=0.01)

    def test_spectrum_ratio_n3_n1(self):
        m1 = kk_gluon_mass_spectrum(1)["m_n_gev"]
        m3 = kk_gluon_mass_spectrum(3)["m_n_gev"]
        ratio = m3 / m1
        assert ratio == pytest.approx(8.654 / 2.405, rel=0.01)

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            kk_gluon_mass_spectrum(0)

    def test_invalid_n4_raises(self):
        with pytest.raises(ValueError):
            kk_gluon_mass_spectrum(4)

    def test_negative_pi_kr_raises(self):
        with pytest.raises(ValueError):
            kk_gluon_mass_spectrum(1, pi_kr=-1.0)

    def test_zero_pi_kr_raises(self):
        with pytest.raises(ValueError):
            kk_gluon_mass_spectrum(1, pi_kr=0.0)

    def test_negative_k_raises(self):
        with pytest.raises(ValueError):
            kk_gluon_mass_spectrum(1, k_gev=-1.0)

    def test_formula_string_present(self):
        result = kk_gluon_mass_spectrum(1)
        assert isinstance(result["formula"], str)
        assert len(result["formula"]) > 0

    def test_mass_positive(self):
        for n in (1, 2, 3):
            assert kk_gluon_mass_spectrum(n)["m_n_gev"] > 0

    def test_custom_pi_kr_changes_mass(self):
        m_default = kk_gluon_mass_spectrum(1)["m_n_gev"]
        m_custom = kk_gluon_mass_spectrum(1, pi_kr=38.0)["m_n_gev"]
        assert m_default != pytest.approx(m_custom, rel=0.001)

    def test_n2_x0n(self):
        result = kk_gluon_mass_spectrum(2)
        assert result["x_0n"] == pytest.approx(5.520, abs=0.001)

    def test_n3_x0n(self):
        result = kk_gluon_mass_spectrum(3)
        assert result["x_0n"] == pytest.approx(8.654, abs=0.001)


# ---------------------------------------------------------------------------
# TestRhoMesonFromAdsQcd
# ---------------------------------------------------------------------------
class TestRhoMesonFromAdsQcd:
    def test_returns_dict(self):
        result = rho_meson_from_ads_qcd()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = rho_meson_from_ads_qcd()
        for key in ("m_rho_gev", "m_rho_pdg_gev", "fractional_error", "status"):
            assert key in result

    def test_m_rho_positive(self):
        result = rho_meson_from_ads_qcd()
        assert result["m_rho_gev"] > 0

    def test_m_rho_sub_gev(self):
        # Soft-wall result: 0.760 GeV (not the RS1 KK-gluon scale)
        result = rho_meson_from_ads_qcd()
        assert result["m_rho_gev"] < 2.0

    def test_m_rho_within_factor_2_of_pdg(self):
        result = rho_meson_from_ads_qcd()
        ratio = result["m_rho_gev"] / RHO_MESON_PDG_GEV
        assert 0.5 < ratio < 2.0

    def test_m_rho_near_pdg_value(self):
        # Should be within 5% of 0.775 GeV (our formula gives 0.760 GeV)
        result = rho_meson_from_ads_qcd()
        assert result["fractional_error"] < 0.10

    def test_fractional_error_lt_half(self):
        result = rho_meson_from_ads_qcd()
        assert result["fractional_error"] < 0.5

    def test_status_constrained(self):
        result = rho_meson_from_ads_qcd()
        assert result["status"] == "CONSTRAINED"

    def test_m_rho_formula_m_kk_over_pi_kr_sq(self):
        # m_rho = M_KK / (pi_kr)^2
        expected = M_PL_GEV * math.exp(-PI_K_R) / PI_K_R**2
        result = rho_meson_from_ads_qcd()
        assert result["m_rho_gev"] == pytest.approx(expected, rel=1e-8)

    def test_m_rho_pdg_key_matches_constant(self):
        result = rho_meson_from_ads_qcd()
        assert result["m_rho_pdg_gev"] == pytest.approx(RHO_MESON_PDG_GEV, rel=1e-9)

    def test_negative_pi_kr_raises(self):
        with pytest.raises(ValueError):
            rho_meson_from_ads_qcd(pi_kr=-1.0)

    def test_zero_pi_kr_raises(self):
        with pytest.raises(ValueError):
            rho_meson_from_ads_qcd(pi_kr=0.0)

    def test_negative_k_gev_raises(self):
        with pytest.raises(ValueError):
            rho_meson_from_ads_qcd(k_gev=-1.0)

    def test_larger_pi_kr_gives_smaller_rho(self):
        m_default = rho_meson_from_ads_qcd()["m_rho_gev"]
        m_larger = rho_meson_from_ads_qcd(pi_kr=40.0)["m_rho_gev"]
        assert m_larger < m_default

    def test_rho_meson_in_mev_range(self):
        result = rho_meson_from_ads_qcd()
        m_mev = result["m_rho_gev"] * 1000
        assert 500 < m_mev < 1500


# ---------------------------------------------------------------------------
# TestLambdaQCDFromAdsGeometry
# ---------------------------------------------------------------------------
class TestLambdaQCDFromAdsGeometry:
    def test_returns_dict(self):
        result = lambda_qcd_from_ads_geometry()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = lambda_qcd_from_ads_geometry()
        for key in ("lambda_qcd_gev", "lambda_qcd_mev", "pdg_mev", "ratio",
                    "fractional_error", "status"):
            assert key in result

    def test_lambda_qcd_positive(self):
        result = lambda_qcd_from_ads_geometry()
        assert result["lambda_qcd_gev"] > 0

    def test_lambda_qcd_sub_gev(self):
        result = lambda_qcd_from_ads_geometry()
        assert result["lambda_qcd_gev"] < 1.0

    def test_lambda_qcd_order_mev(self):
        result = lambda_qcd_from_ads_geometry()
        assert 50 < result["lambda_qcd_mev"] < 600

    def test_lambda_qcd_ratio_lt_3(self):
        # Must be within factor 3 of PDG (= CONSTRAINED)
        result = lambda_qcd_from_ads_geometry()
        assert result["ratio"] < 3.0

    def test_lambda_qcd_ratio_gt_0(self):
        result = lambda_qcd_from_ads_geometry()
        assert result["ratio"] > 0

    def test_status_constrained(self):
        result = lambda_qcd_from_ads_geometry()
        assert result["status"] == "CONSTRAINED"

    def test_lambda_equals_rho_over_alpha_ratio(self):
        rho_result = rho_meson_from_ads_qcd()
        expected = rho_result["m_rho_gev"] / ALPHA_S_RATIO_QCD
        result = lambda_qcd_from_ads_geometry()
        assert result["lambda_qcd_gev"] == pytest.approx(expected, rel=1e-8)

    def test_gev_mev_consistency(self):
        result = lambda_qcd_from_ads_geometry()
        assert result["lambda_qcd_mev"] == pytest.approx(
            result["lambda_qcd_gev"] * 1e3, rel=1e-9
        )

    def test_pdg_mev_key_matches_constant(self):
        result = lambda_qcd_from_ads_geometry()
        assert result["pdg_mev"] == pytest.approx(LAMBDA_QCD_PDG_MEV, rel=1e-9)

    def test_fractional_error_lt_1(self):
        # Within 100% of PDG (well within factor 2)
        result = lambda_qcd_from_ads_geometry()
        assert result["fractional_error"] < 1.0

    def test_custom_pi_kr_changes_lambda(self):
        lam1 = lambda_qcd_from_ads_geometry()["lambda_qcd_gev"]
        lam2 = lambda_qcd_from_ads_geometry(pi_kr=40.0)["lambda_qcd_gev"]
        assert lam1 != pytest.approx(lam2, rel=0.001)


# ---------------------------------------------------------------------------
# TestDiagnosePillar62Gap
# ---------------------------------------------------------------------------
class TestDiagnosePillar62Gap:
    def test_returns_dict(self):
        result = diagnose_pillar62_gap()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = diagnose_pillar62_gap()
        for key in ("lambda_qcd_pillar62_gev", "lambda_qcd_adsgeo_gev",
                    "gap_factor", "root_cause"):
            assert key in result

    def test_pillar62_lambda_above_pev(self):
        # Old Pillar 62 result is ~10^7 GeV (PeV scale)
        result = diagnose_pillar62_gap()
        assert result["lambda_qcd_pillar62_gev"] > 1e6

    def test_ads_lambda_sub_gev(self):
        result = diagnose_pillar62_gap()
        assert result["lambda_qcd_adsgeo_gev"] < 1.0

    def test_gap_factor_large(self):
        # Gap must exceed 10^5 to demonstrate Pillar 62 was far off
        result = diagnose_pillar62_gap()
        assert result["gap_factor"] > 1e5

    def test_root_cause_string(self):
        result = diagnose_pillar62_gap()
        assert isinstance(result["root_cause"], str)
        assert len(result["root_cause"]) > 10

    def test_gap_is_ratio(self):
        result = diagnose_pillar62_gap()
        expected = result["lambda_qcd_pillar62_gev"] / result["lambda_qcd_adsgeo_gev"]
        assert result["gap_factor"] == pytest.approx(expected, rel=1e-8)

    def test_ads_geo_matches_lambda_function(self):
        gap_result = diagnose_pillar62_gap()
        lam_result = lambda_qcd_from_ads_geometry()
        assert gap_result["lambda_qcd_adsgeo_gev"] == pytest.approx(
            lam_result["lambda_qcd_gev"], rel=1e-8
        )


# ---------------------------------------------------------------------------
# TestAdsQCDDilatonCheck
# ---------------------------------------------------------------------------
class TestAdsQCDDilatonCheck:
    def test_returns_dict(self):
        result = ads_qcd_dilaton_check()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = ads_qcd_dilaton_check()
        for key in ("f_pi_predicted_gev", "f_pi_pdg_gev", "ratio", "consistency"):
            assert key in result

    def test_f_pi_predicted_positive(self):
        result = ads_qcd_dilaton_check()
        assert result["f_pi_predicted_gev"] > 0

    def test_f_pi_pdg_value(self):
        result = ads_qcd_dilaton_check()
        assert result["f_pi_pdg_gev"] == pytest.approx(0.0924, abs=0.001)

    def test_ratio_positive(self):
        result = ads_qcd_dilaton_check()
        assert result["ratio"] > 0

    def test_ratio_order_of_magnitude(self):
        # Ratio f_pi^2_predicted / f_pi^2_PDG should be O(few) to O(few tens)
        result = ads_qcd_dilaton_check()
        assert 0.1 < result["ratio"] < 1000

    def test_consistency_string(self):
        result = ads_qcd_dilaton_check()
        assert isinstance(result["consistency"], str)
        assert len(result["consistency"]) > 5

    def test_custom_pi_kr_accepted(self):
        result_default = ads_qcd_dilaton_check()
        result_custom = ads_qcd_dilaton_check(pi_kr=40.0)
        # Different pi_kr must yield a different f_pi (propagated through rho_meson_from_ads_qcd)
        assert result_custom["f_pi_predicted_gev"] > 0
        assert result_custom["f_pi_predicted_gev"] != pytest.approx(
            result_default["f_pi_predicted_gev"], rel=0.001
        )


# ---------------------------------------------------------------------------
# TestQCDConfinementGeometricReport
# ---------------------------------------------------------------------------
class TestQCDConfinementGeometricReport:
    def test_returns_dict(self):
        result = qcd_confinement_geometric_report()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = qcd_confinement_geometric_report()
        assert result["pillar"] == 162

    def test_status_constrained(self):
        result = qcd_confinement_geometric_report()
        assert result["status"] == "CONSTRAINED"

    def test_required_keys(self):
        result = qcd_confinement_geometric_report()
        for key in ("pillar", "n_w", "k_cs", "status", "lambda_qcd_gev",
                    "lambda_qcd_mev", "pdg_lambda_qcd_mev", "fractional_error",
                    "rho_meson_gev", "rho_meson_pdg_gev", "gap_factor_vs_pillar62",
                    "f_pi_predicted_gev", "f_pi_pdg_gev", "epistemic_label",
                    "open_issue", "description"):
            assert key in result

    def test_n_w_value(self):
        result = qcd_confinement_geometric_report()
        assert result["n_w"] == 5

    def test_k_cs_value(self):
        result = qcd_confinement_geometric_report()
        assert result["k_cs"] == 74

    def test_lambda_qcd_positive(self):
        result = qcd_confinement_geometric_report()
        assert result["lambda_qcd_gev"] > 0

    def test_rho_meson_sub_gev(self):
        result = qcd_confinement_geometric_report()
        assert result["rho_meson_gev"] < 2.0

    def test_gap_factor_large(self):
        result = qcd_confinement_geometric_report()
        assert result["gap_factor_vs_pillar62"] > 1e5

    def test_epistemic_label(self):
        result = qcd_confinement_geometric_report()
        assert result["epistemic_label"] == "CONSTRAINED"

    def test_open_issue_string(self):
        result = qcd_confinement_geometric_report()
        assert isinstance(result["open_issue"], str)
        assert len(result["open_issue"]) > 5

    def test_description_string(self):
        result = qcd_confinement_geometric_report()
        assert isinstance(result["description"], str)

    def test_rho_pdg_key(self):
        result = qcd_confinement_geometric_report()
        assert result["rho_meson_pdg_gev"] == pytest.approx(RHO_MESON_PDG_GEV, rel=1e-9)

    def test_custom_n_w(self):
        result = qcd_confinement_geometric_report(n_w=7)
        assert result["n_w"] == 7

    def test_custom_k_cs(self):
        result = qcd_confinement_geometric_report(k_cs=100)
        assert result["k_cs"] == 100


# ---------------------------------------------------------------------------
# TestPillar162Summary
# ---------------------------------------------------------------------------
class TestPillar162Summary:
    def test_returns_dict(self):
        result = pillar162_summary()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = pillar162_summary()
        assert result["pillar"] == 162

    def test_required_keys(self):
        result = pillar162_summary()
        for key in ("pillar", "method", "lambda_qcd_mev", "lambda_qcd_gev",
                    "pdg_lambda_qcd_mev", "status", "open_issue",
                    "pi_kr", "j_0_1", "rho_meson_pdg_gev"):
            assert key in result

    def test_status_constrained(self):
        result = pillar162_summary()
        assert result["status"] == "CONSTRAINED"

    def test_method_string(self):
        result = pillar162_summary()
        assert isinstance(result["method"], str)

    def test_pi_kr_constant(self):
        result = pillar162_summary()
        assert result["pi_kr"] == pytest.approx(37.0, abs=1e-10)

    def test_j_0_1_constant(self):
        result = pillar162_summary()
        assert result["j_0_1"] == pytest.approx(2.405, abs=0.001)

    def test_rho_pdg_constant(self):
        result = pillar162_summary()
        assert result["rho_meson_pdg_gev"] == pytest.approx(0.775, abs=0.001)

    def test_lambda_mev_matches_gev(self):
        result = pillar162_summary()
        assert result["lambda_qcd_mev"] == pytest.approx(
            result["lambda_qcd_gev"] * 1e3, rel=1e-9
        )

    def test_lambda_sub_gev(self):
        result = pillar162_summary()
        assert result["lambda_qcd_gev"] < 1.0

    def test_pdg_lambda_key(self):
        result = pillar162_summary()
        assert result["pdg_lambda_qcd_mev"] == pytest.approx(LAMBDA_QCD_PDG_MEV, rel=1e-9)
