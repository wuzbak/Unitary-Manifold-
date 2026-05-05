# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_qcd_threshold_synthesis.py
========================================
Tests for Pillar 172 — QCD Threshold Synthesis and Honest Gap Accounting.

Covers:
  - Path A: multi-threshold perturbative running (shows closure by physics)
  - Path B: KK threshold corrections (Pillar 114)
  - Path C: AdS/QCD geometric (Pillars 162+171)
  - String tension cross-check
  - Three-path synthesis and B–C convergence
  - Honest residuals accounting
  - pillar172_summary and pillar172_full_report

Theory, scientific direction, and framework: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""

import math
import pytest

from src.core.qcd_threshold_synthesis import (
    N_W, K_CS, PI_KR, M_PL_GEV, M_KK_GEV,
    ALPHA_S_MKK, LAMBDA_QCD_PDG_GEV, LAMBDA_QCD_PDG_MEV, C_LAT,
    beta_coefficient_b0,
    alpha_s_run_one_step,
    quark_threshold_decoupling,
    lambda_qcd_perturbative,
    path_a_report,
    kk_threshold_correction,
    alpha_s_eff_kk,
    lambda_qcd_kk_thresholds,
    path_b_report,
    lambda_qcd_adsgeo,
    path_c_report,
    string_tension_cross_check,
    three_path_synthesis,
    honest_residuals,
    pillar172_summary,
    pillar172_full_report,
)


# ===========================================================================
# Section 1: Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-12)

    def test_m_pl_order(self):
        assert 1e18 < M_PL_GEV < 1e20

    def test_m_kk_positive(self):
        assert M_KK_GEV > 0

    def test_alpha_s_mkk_formula(self):
        assert ALPHA_S_MKK == pytest.approx(2.0 * math.pi / (3 * 74), rel=1e-9)

    def test_alpha_s_mkk_small(self):
        # Must be in the perturbative regime
        assert ALPHA_S_MKK < 0.1

    def test_lambda_qcd_pdg_gev(self):
        assert LAMBDA_QCD_PDG_GEV == pytest.approx(0.210, rel=1e-9)

    def test_lambda_qcd_pdg_mev_consistent(self):
        assert LAMBDA_QCD_PDG_MEV == pytest.approx(LAMBDA_QCD_PDG_GEV * 1e3, rel=1e-9)

    def test_c_lat(self):
        assert C_LAT == pytest.approx(2.84, rel=1e-9)


# ===========================================================================
# Section 2: beta_coefficient_b0
# ===========================================================================

class TestBetaCoefficientB0:
    def test_nf6(self):
        b0 = beta_coefficient_b0(n_c=3, n_f=6)
        # b0 = (11/3)*3 - (2/3)*6 = 11 - 4 = 7
        assert b0 == pytest.approx(7.0, rel=1e-9)

    def test_nf5(self):
        b0 = beta_coefficient_b0(n_c=3, n_f=5)
        # 11 - 10/3 = 11 - 3.333... = 7.666...
        assert b0 == pytest.approx(23.0 / 3.0, rel=1e-9)

    def test_nf4(self):
        b0 = beta_coefficient_b0(n_c=3, n_f=4)
        # 11 - 8/3 = 33/3 - 8/3 = 25/3
        assert b0 == pytest.approx(25.0 / 3.0, rel=1e-9)

    def test_nf3(self):
        b0 = beta_coefficient_b0(n_c=3, n_f=3)
        # (11/3)*3 - (2/3)*3 = 11 - 2 = 9
        assert b0 == pytest.approx(9.0, rel=1e-9)

    def test_asymptotic_freedom(self):
        # b0 > 0 required for asymptotic freedom (n_f < 16.5 for SU(3))
        for n_f in range(0, 7):
            b0 = beta_coefficient_b0(n_c=3, n_f=n_f)
            assert b0 > 0, f"b0 should be positive for n_f={n_f}"

    def test_positive_for_qcd_flavors(self):
        assert beta_coefficient_b0(n_c=3, n_f=6) > 0


# ===========================================================================
# Section 3: alpha_s_run_one_step
# ===========================================================================

class TestAlphaSRunOneStep:
    def test_running_decreases_alpha_s(self):
        # Running to lower scale with UV coupling should decrease α_s
        a_high = 0.028
        a_low = alpha_s_run_one_step(a_high, mu_high=1000.0, mu_low=100.0, n_f=6)
        assert a_low < a_high

    def test_running_positive_result(self):
        a = alpha_s_run_one_step(0.028, mu_high=1000.0, mu_low=100.0, n_f=6)
        assert a > 0

    def test_raises_on_zero_mu_high(self):
        with pytest.raises(ValueError):
            alpha_s_run_one_step(0.028, mu_high=0.0, mu_low=100.0, n_f=6)

    def test_raises_on_zero_mu_low(self):
        with pytest.raises(ValueError):
            alpha_s_run_one_step(0.028, mu_high=1000.0, mu_low=0.0, n_f=6)

    def test_raises_if_mu_low_ge_mu_high(self):
        with pytest.raises(ValueError):
            alpha_s_run_one_step(0.028, mu_high=100.0, mu_low=100.0, n_f=6)

    def test_no_running_if_same_scale(self):
        # Limit: should be identity when mu_high → mu_low; use close scales
        a_high = 0.028
        a_close = alpha_s_run_one_step(a_high, mu_high=1000.0, mu_low=999.99, n_f=6)
        assert abs(a_close - a_high) / a_high < 0.001

    def test_formula_consistency(self):
        alpha_s = 0.028
        mu_h, mu_l, n_f = 1000.0, 100.0, 6
        b0 = beta_coefficient_b0(n_c=3, n_f=n_f)
        log_ratio = math.log(mu_h / mu_l)
        expected = 1.0 / (1.0 / alpha_s + (b0 / (2.0 * math.pi)) * log_ratio)
        result = alpha_s_run_one_step(alpha_s, mu_h, mu_l, n_f)
        assert result == pytest.approx(expected, rel=1e-9)


# ===========================================================================
# Section 4: Path A — quark_threshold_decoupling and lambda_qcd_perturbative
# ===========================================================================

class TestPathAQuarkThresholds:
    def test_returns_list(self):
        steps = quark_threshold_decoupling()
        assert isinstance(steps, list)

    def test_at_least_4_steps(self):
        steps = quark_threshold_decoupling()
        assert len(steps) >= 4

    def test_each_step_has_required_keys(self):
        steps = quark_threshold_decoupling()
        required = {"quark", "mass_gev", "alpha_s_above", "alpha_s_below", "n_f_above"}
        for step in steps:
            assert required.issubset(step.keys())

    def test_top_quark_step_exists(self):
        steps = quark_threshold_decoupling()
        quarks = [s["quark"] for s in steps]
        assert "t" in quarks

    def test_bottom_quark_step_exists(self):
        steps = quark_threshold_decoupling()
        quarks = [s["quark"] for s in steps]
        assert "b" in quarks

    def test_charm_quark_step_exists(self):
        steps = quark_threshold_decoupling()
        quarks = [s["quark"] for s in steps]
        assert "c" in quarks

    def test_alpha_s_decreases_through_steps(self):
        steps = quark_threshold_decoupling()
        for step in steps:
            assert step["alpha_s_below"] <= step["alpha_s_above"]

    def test_n_f_decreases_through_steps(self):
        steps = quark_threshold_decoupling()
        n_fs = [s["n_f_above"] for s in steps]
        assert n_fs == sorted(n_fs, reverse=True)


class TestLambdaQCDPerturbative:
    def test_returns_dict(self):
        r = lambda_qcd_perturbative()
        assert isinstance(r, dict)

    def test_path_label(self):
        r = lambda_qcd_perturbative()
        assert "perturbative" in r["path"].lower()

    def test_lambda_qcd_gev_positive(self):
        r = lambda_qcd_perturbative()
        assert r["lambda_qcd_gev"] >= 0

    def test_lambda_qcd_exponentially_suppressed(self):
        # Should be many orders below PDG 0.21 GeV
        r = lambda_qcd_perturbative()
        assert r["lambda_qcd_gev"] < 1e-3

    def test_orders_below_pdg_large(self):
        r = lambda_qcd_perturbative()
        # Should be at least 5 orders below PDG
        assert r["orders_below_pdg"] > 5.0

    def test_status_path_a_closed(self):
        r = lambda_qcd_perturbative()
        assert "PATH_A_CLOSED" in r["status"]

    def test_interpretation_present(self):
        r = lambda_qcd_perturbative()
        assert len(r["interpretation"]) > 20

    def test_path_a_report_alias(self):
        r1 = lambda_qcd_perturbative()
        r2 = path_a_report()
        assert r1["lambda_qcd_gev"] == pytest.approx(r2["lambda_qcd_gev"], rel=1e-9)


# ===========================================================================
# Section 5: Path B — KK threshold corrections
# ===========================================================================

class TestKKThresholdCorrection:
    def test_returns_dict(self):
        d = kk_threshold_correction()
        assert isinstance(d, dict)

    def test_alpha_s_eff_positive(self):
        d = kk_threshold_correction()
        assert d["alpha_s_eff"] > 0

    def test_alpha_s_eff_smaller_than_input(self):
        # Positive correction → α_s_eff ≤ α_s_mkk (coupling weakened)
        d = kk_threshold_correction()
        assert d["alpha_s_eff"] <= d["alpha_s_mkk"]

    def test_b0_kk_positive(self):
        d = kk_threshold_correction()
        assert d["b0_kk"] > 0

    def test_delta_inv_positive(self):
        d = kk_threshold_correction()
        assert d["delta_inv_alpha_s"] > 0

    def test_weighted_sum_positive(self):
        d = kk_threshold_correction()
        assert d["weighted_sum"] > 0

    def test_n_kk_74(self):
        d = kk_threshold_correction()
        assert d["n_kk"] == 74

    def test_raises_on_zero_n_kk(self):
        with pytest.raises(ValueError):
            kk_threshold_correction(n_kk=0)

    def test_raises_on_negative_alpha(self):
        with pytest.raises(ValueError):
            kk_threshold_correction(alpha_s_mkk=-0.028)

    def test_alpha_s_eff_kk_wrapper(self):
        d = kk_threshold_correction()
        assert alpha_s_eff_kk() == pytest.approx(d["alpha_s_eff"], rel=1e-9)


class TestLambdaQCDKKThresholds:
    def test_returns_dict(self):
        r = lambda_qcd_kk_thresholds()
        assert isinstance(r, dict)

    def test_path_label_b(self):
        r = lambda_qcd_kk_thresholds()
        assert "B" in r["path"]

    def test_lambda_qcd_gev_positive(self):
        r = lambda_qcd_kk_thresholds()
        assert r["lambda_qcd_gev"] > 0

    def test_lambda_qcd_order_of_magnitude(self):
        r = lambda_qcd_kk_thresholds()
        # Should be in 0.1–1 GeV range
        assert 0.05 < r["lambda_qcd_gev"] < 2.0

    def test_ratio_to_pdg_reasonable(self):
        r = lambda_qcd_kk_thresholds()
        assert 0.1 < r["ratio_to_pdg"] < 5.0

    def test_status_mechanistically_derived(self):
        r = lambda_qcd_kk_thresholds()
        assert "MECHANISTICALLY_DERIVED" in r["status"]

    def test_caveat_present(self):
        r = lambda_qcd_kk_thresholds()
        assert len(r["caveat"]) > 10

    def test_path_b_report_alias(self):
        r1 = lambda_qcd_kk_thresholds()
        r2 = path_b_report()
        assert r1["lambda_qcd_gev"] == pytest.approx(r2["lambda_qcd_gev"], rel=1e-9)


# ===========================================================================
# Section 6: Path C — AdS/QCD geometric
# ===========================================================================

class TestLambdaQCDAdsgeo:
    def test_returns_dict(self):
        r = lambda_qcd_adsgeo()
        assert isinstance(r, dict)

    def test_path_label_c(self):
        r = lambda_qcd_adsgeo()
        assert "C" in r["path"]

    def test_lambda_qcd_gev_positive(self):
        r = lambda_qcd_adsgeo()
        assert r["lambda_qcd_gev"] > 0

    def test_lambda_qcd_mev_consistent(self):
        r = lambda_qcd_adsgeo()
        assert r["lambda_qcd_mev"] == pytest.approx(r["lambda_qcd_gev"] * 1e3, rel=1e-9)

    def test_lambda_qcd_within_factor_2_of_pdg(self):
        r = lambda_qcd_adsgeo()
        assert r["ratio_to_pdg"] < 2.0
        assert r["ratio_to_pdg"] > 0.1

    def test_r_dil_um_correct(self):
        r = lambda_qcd_adsgeo()
        assert r["r_dil_um"] == pytest.approx(math.sqrt(74.0 / 5.0), rel=1e-9)

    def test_r_dil_agreement_high(self):
        r = lambda_qcd_adsgeo()
        assert r["r_dil_agreement_pct"] > 99.0

    def test_status_derived(self):
        r = lambda_qcd_adsgeo()
        assert r["status"] == "DERIVED"

    def test_raises_on_zero_n_w(self):
        with pytest.raises(ValueError):
            lambda_qcd_adsgeo(n_w=0)

    def test_raises_on_zero_k_cs(self):
        with pytest.raises(ValueError):
            lambda_qcd_adsgeo(k_cs=0)

    def test_raises_on_zero_pi_kr(self):
        with pytest.raises(ValueError):
            lambda_qcd_adsgeo(pi_kr=0)

    def test_raises_on_zero_m_pl(self):
        with pytest.raises(ValueError):
            lambda_qcd_adsgeo(m_pl_gev=0)

    def test_path_c_report_alias(self):
        r1 = lambda_qcd_adsgeo()
        r2 = path_c_report()
        assert r1["lambda_qcd_gev"] == pytest.approx(r2["lambda_qcd_gev"], rel=1e-9)


# ===========================================================================
# Section 7: string_tension_cross_check
# ===========================================================================

class TestStringTensionCrossCheck:
    def test_returns_dict(self):
        st = string_tension_cross_check()
        assert isinstance(st, dict)

    def test_kappa_positive(self):
        st = string_tension_cross_check()
        assert st["kappa_gev"] > 0

    def test_sigma_kappa_positive(self):
        st = string_tension_cross_check()
        assert st["sigma_kappa_gev2"] > 0

    def test_sigma_rho_approx_positive(self):
        st = string_tension_cross_check()
        assert st["sigma_rho_approx_gev2"] > 0

    def test_sigma_lattice_correct(self):
        st = string_tension_cross_check()
        assert st["sigma_lattice_gev2"] == pytest.approx(0.18, rel=1e-9)

    def test_ratio_kappa_finite(self):
        st = string_tension_cross_check()
        assert math.isfinite(st["ratio_kappa_to_lattice"])

    def test_ratio_kappa_order_of_magnitude(self):
        # κ = m_ρ/2 ≈ 0.38 GeV, σ = κ² ≈ 0.144 GeV², lattice = 0.18 GeV²
        # ratio should be close to 1 (within factor 3)
        st = string_tension_cross_check()
        assert st["ratio_kappa_to_lattice"] < 3.0

    def test_sigma_kappa_equals_kappa_squared(self):
        st = string_tension_cross_check()
        assert st["sigma_kappa_gev2"] == pytest.approx(st["kappa_gev"]**2, rel=1e-9)

    def test_consistency_string_present(self):
        st = string_tension_cross_check()
        assert "consistency" in st


# ===========================================================================
# Section 8: three_path_synthesis
# ===========================================================================

class TestThreePathSynthesis:
    def test_returns_dict(self):
        s = three_path_synthesis()
        assert isinstance(s, dict)

    def test_path_a_present(self):
        s = three_path_synthesis()
        assert "path_a" in s

    def test_path_b_present(self):
        s = three_path_synthesis()
        assert "path_b" in s

    def test_path_c_present(self):
        s = three_path_synthesis()
        assert "path_c" in s

    def test_string_tension_present(self):
        s = three_path_synthesis()
        assert "string_tension" in s

    def test_bc_agreement_pct_present(self):
        s = three_path_synthesis()
        assert "bc_agreement_pct" in s

    def test_convergence_present(self):
        s = three_path_synthesis()
        assert s["convergence"] in ("CLOSED", "CONSTRAINED", "OPEN")

    def test_path_a_exponentially_suppressed(self):
        s = three_path_synthesis()
        assert s["path_a"]["lambda_qcd_gev"] < 1e-3

    def test_path_b_order_of_magnitude(self):
        s = three_path_synthesis()
        assert 0.05 < s["path_b"]["lambda_qcd_gev"] < 2.0

    def test_path_c_order_of_magnitude(self):
        s = three_path_synthesis()
        assert 0.05 < s["path_c"]["lambda_qcd_gev"] < 2.0

    def test_bc_agreement_pct_positive(self):
        s = three_path_synthesis()
        assert s["bc_agreement_pct"] > 0

    def test_pdg_values_present(self):
        s = three_path_synthesis()
        assert s["pdg_gev"] == pytest.approx(0.210, rel=1e-9)

    def test_path_a_status_closed_by_physics(self):
        s = three_path_synthesis()
        assert "CLOSED" in s["path_a"]["status"]

    def test_path_b_status_mechanistically_derived(self):
        s = three_path_synthesis()
        assert "MECHANISTICALLY_DERIVED" in s["path_b"]["status"]

    def test_path_c_status_derived(self):
        s = three_path_synthesis()
        assert s["path_c"]["status"] == "DERIVED"


# ===========================================================================
# Section 9: honest_residuals
# ===========================================================================

class TestHonestResiduals:
    def test_returns_dict(self):
        r = honest_residuals()
        assert isinstance(r, dict)

    def test_pillar_172(self):
        r = honest_residuals()
        assert r["pillar"] == 172

    def test_residuals_present(self):
        r = honest_residuals()
        assert "residuals" in r

    def test_r_dil_status_derived(self):
        r = honest_residuals()
        assert r["residuals"]["r_dil_derivation"]["status"] == "DERIVED"

    def test_c_lat_status_permanent_external(self):
        r = honest_residuals()
        assert "PERMANENT_EXTERNAL_INPUT" in r["residuals"]["c_lat"]["status"]

    def test_c_lat_value_correct(self):
        r = honest_residuals()
        assert r["residuals"]["c_lat"]["value"] == pytest.approx(2.84, rel=1e-9)

    def test_lambda_qcd_status_derived(self):
        r = honest_residuals()
        assert r["residuals"]["lambda_qcd"]["status"] == "DERIVED"

    def test_perturbative_path_correctly_closed(self):
        r = honest_residuals()
        assert "CORRECTLY_CLOSED" in r["residuals"]["perturbative_path"]["status"]

    def test_overall_status(self):
        r = honest_residuals()
        assert "SUBSTANTIALLY_CLOSED" in r["overall_status"]

    def test_summary_present(self):
        r = honest_residuals()
        assert len(r["summary"]) > 20


# ===========================================================================
# Section 10: pillar172_summary
# ===========================================================================

class TestPillar172Summary:
    def test_returns_dict(self):
        s = pillar172_summary()
        assert isinstance(s, dict)

    def test_pillar_172(self):
        s = pillar172_summary()
        assert s["pillar"] == 172

    def test_n_w_k_cs(self):
        s = pillar172_summary()
        assert s["n_w"] == 5
        assert s["k_cs"] == 74

    def test_path_a_mev_present(self):
        s = pillar172_summary()
        assert "path_a_lambda_mev" in s

    def test_path_b_mev_positive(self):
        s = pillar172_summary()
        assert s["path_b_lambda_mev"] > 0

    def test_path_c_mev_positive(self):
        s = pillar172_summary()
        assert s["path_c_lambda_mev"] > 0

    def test_bc_agreement_pct_positive(self):
        s = pillar172_summary()
        assert s["bc_agreement_pct"] > 0

    def test_convergence_valid(self):
        s = pillar172_summary()
        assert s["convergence"] in ("CLOSED", "CONSTRAINED", "OPEN")

    def test_status_substantially_closed(self):
        s = pillar172_summary()
        assert "SUBSTANTIALLY_CLOSED" in s["status"]

    def test_dilaton_status_derived(self):
        s = pillar172_summary()
        assert s["dilaton_status"] == "DERIVED"

    def test_c_lat_status_permanent_external(self):
        s = pillar172_summary()
        assert "PERMANENT_EXTERNAL_INPUT" in s["c_lat_status"]

    def test_pdg_mev_correct(self):
        s = pillar172_summary()
        assert s["pdg_mev"] == pytest.approx(210.0, rel=1e-9)


# ===========================================================================
# Section 11: pillar172_full_report
# ===========================================================================

class TestPillar172FullReport:
    def test_returns_dict(self):
        r = pillar172_full_report()
        assert isinstance(r, dict)

    def test_pillar_172(self):
        r = pillar172_full_report()
        assert r["pillar"] == 172

    def test_path_a_present(self):
        r = pillar172_full_report()
        assert "path_a" in r

    def test_path_b_present(self):
        r = pillar172_full_report()
        assert "path_b" in r

    def test_path_c_present(self):
        r = pillar172_full_report()
        assert "path_c" in r

    def test_synthesis_present(self):
        r = pillar172_full_report()
        assert "synthesis" in r

    def test_string_tension_present(self):
        r = pillar172_full_report()
        assert "string_tension" in r

    def test_honest_residuals_present(self):
        r = pillar172_full_report()
        assert "honest_residuals" in r

    def test_epistemic_label(self):
        r = pillar172_full_report()
        assert "SUBSTANTIALLY_CLOSED" in r["epistemic_label"]

    def test_status(self):
        r = pillar172_full_report()
        assert "SUBSTANTIALLY_CLOSED" in r["status"]
