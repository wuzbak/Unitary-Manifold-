# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_dirty_data_test.py
==============================
Test suite for Pillar 61: The AxiomZero Challenge — Internal Falsifier Suite
(src/core/dirty_data_test.py).

~62 tests covering:
  - Module-level constants
  - ns_from_phi0_eff: correctness, edge cases
  - r_from_phi0_eff: correctness
  - perturbed_phi0_eff: formula
  - ns_perturbation_response: keys, direction, magnitude
  - ns_linear_sensitivity: sign, magnitude
  - ns_linear_sensitivity_analytic: formula
  - dirty_data_check: verdict, keys, edge cases
  - oracle_detection_report: structure, oracle_falsified
  - r_perturbation_response: keys, direction
  - alpha_kk_scale: formula, free_parameters
  - alpha_rg_run: correctness, error cases
  - alpha_low_energy: keys, n_f_is_free, status
  - mp_over_me_gap_report: keys, discrepancy
  - axiomzero_challenge_summary: keys, dirty_data verdict

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dirty_data_test import (
    # Constants
    N_W,
    N_W2,
    K_CS,
    PHI0_BARE,
    PHI0_EFF_CANONICAL,
    R_C_CANONICAL,
    C_S_CANONICAL,
    ALPHA_EM_PDG,
    MP_OVER_ME_PDG,
    NS_PLANCK_CENTRAL,
    NS_PLANCK_SIGMA,
    NS_CANONICAL,
    M_PROTON_MEV,
    M_ELECTRON_MEV,
    # Functions
    ns_from_phi0_eff,
    r_from_phi0_eff,
    perturbed_phi0_eff,
    ns_perturbation_response,
    ns_linear_sensitivity,
    ns_linear_sensitivity_analytic,
    dirty_data_check,
    oracle_detection_report,
    r_perturbation_response,
    alpha_kk_scale,
    alpha_rg_run,
    alpha_low_energy,
    mp_over_me_gap_report,
    axiomzero_challenge_summary,
)


# ---------------------------------------------------------------------------
# I. Module-level constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n_w2(self):
        assert N_W2 == 7

    def test_k_cs(self):
        assert K_CS == N_W**2 + N_W2**2
        assert K_CS == 74

    def test_phi0_bare(self):
        assert PHI0_BARE == 1.0

    def test_phi0_eff_canonical(self):
        expected = 5 * 2.0 * math.pi
        assert abs(PHI0_EFF_CANONICAL - expected) < 1e-10

    def test_r_c_canonical(self):
        assert R_C_CANONICAL == 12.0

    def test_c_s_canonical(self):
        # c_s = (N_W2² - N_W²) / K_CS = 24/74 = 12/37
        expected = (N_W2**2 - N_W**2) / K_CS
        assert abs(C_S_CANONICAL - expected) < 1e-10
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-10

    def test_alpha_em_pdg(self):
        # PDG value: 1/137.035...
        assert abs(1.0 / ALPHA_EM_PDG - 137.036) < 0.01

    def test_mp_over_me_pdg(self):
        assert abs(MP_OVER_ME_PDG - 1836.15) < 0.01

    def test_ns_planck_central(self):
        assert abs(NS_PLANCK_CENTRAL - 0.9649) < 1e-5

    def test_ns_planck_sigma(self):
        assert abs(NS_PLANCK_SIGMA - 0.0042) < 1e-5

    def test_proton_mass_mev(self):
        assert abs(M_PROTON_MEV - 938.27) < 0.01

    def test_electron_mass_mev(self):
        assert abs(M_ELECTRON_MEV - 0.511) < 0.001

    def test_mp_over_me_ratio_consistency(self):
        # Derived from stored masses
        assert abs(M_PROTON_MEV / M_ELECTRON_MEV - MP_OVER_ME_PDG) < 0.01


# ---------------------------------------------------------------------------
# II. ns_from_phi0_eff
# ---------------------------------------------------------------------------

class TestNsFromPhi0Eff:
    def test_canonical_value_reasonable(self):
        ns = ns_from_phi0_eff(PHI0_EFF_CANONICAL)
        # Should be in the range [0.95, 0.99] (typical slow-roll KK prediction)
        assert 0.95 < ns < 0.99

    def test_larger_phi0_gives_larger_ns(self):
        ns1 = ns_from_phi0_eff(30.0)
        ns2 = ns_from_phi0_eff(40.0)
        assert ns2 > ns1

    def test_smaller_phi0_gives_smaller_ns(self):
        ns1 = ns_from_phi0_eff(PHI0_EFF_CANONICAL)
        ns2 = ns_from_phi0_eff(PHI0_EFF_CANONICAL * 0.5)
        assert ns2 < ns1

    def test_returns_float(self):
        assert isinstance(ns_from_phi0_eff(PHI0_EFF_CANONICAL), float)

    def test_raises_on_nonpositive(self):
        with pytest.raises(ValueError):
            ns_from_phi0_eff(0.0)
        with pytest.raises(ValueError):
            ns_from_phi0_eff(-1.0)

    def test_large_phi0_approaches_1(self):
        # As φ₀_eff → ∞, nₛ → 1 (scale-invariant limit)
        ns = ns_from_phi0_eff(1000.0)
        assert ns > 0.999

    def test_lambda_independence(self):
        # nₛ should be independent of λ at leading order
        ns1 = ns_from_phi0_eff(PHI0_EFF_CANONICAL, lam=1.0)
        ns2 = ns_from_phi0_eff(PHI0_EFF_CANONICAL, lam=100.0)
        assert abs(ns1 - ns2) < 1e-10


# ---------------------------------------------------------------------------
# III. r_from_phi0_eff
# ---------------------------------------------------------------------------

class TestRFromPhi0Eff:
    def test_canonical_r_positive(self):
        r = r_from_phi0_eff(PHI0_EFF_CANONICAL)
        assert r > 0

    def test_larger_phi0_gives_smaller_r(self):
        r1 = r_from_phi0_eff(PHI0_EFF_CANONICAL)
        r2 = r_from_phi0_eff(PHI0_EFF_CANONICAL * 2.0)
        assert r2 < r1

    def test_returns_float(self):
        assert isinstance(r_from_phi0_eff(PHI0_EFF_CANONICAL), float)

    def test_raises_on_nonpositive(self):
        with pytest.raises(ValueError):
            r_from_phi0_eff(0.0)


# ---------------------------------------------------------------------------
# IV. perturbed_phi0_eff
# ---------------------------------------------------------------------------

class TestPerturbedPhi0Eff:
    def test_zero_perturbation(self):
        assert abs(perturbed_phi0_eff(0.0) - PHI0_EFF_CANONICAL) < 1e-12

    def test_positive_perturbation(self):
        result = perturbed_phi0_eff(0.1)
        assert abs(result - PHI0_EFF_CANONICAL * 1.1) < 1e-10

    def test_negative_perturbation(self):
        result = perturbed_phi0_eff(-0.1)
        assert abs(result - PHI0_EFF_CANONICAL * 0.9) < 1e-10

    def test_larger_delta_gives_larger_phi(self):
        assert perturbed_phi0_eff(0.2) > perturbed_phi0_eff(0.1)

    def test_negative_delta_gives_smaller_phi(self):
        assert perturbed_phi0_eff(-0.1) < PHI0_EFF_CANONICAL


# ---------------------------------------------------------------------------
# V. ns_perturbation_response
# ---------------------------------------------------------------------------

class TestNsPerturbationResponse:
    def test_keys_present(self):
        resp = ns_perturbation_response(0.05)
        for key in ("phi0_eff_clean", "phi0_eff_dirty", "ns_clean",
                    "ns_dirty", "delta_ns", "delta_ns_linear"):
            assert key in resp

    def test_phi0_clean_is_canonical(self):
        resp = ns_perturbation_response(0.05)
        assert abs(resp["phi0_eff_clean"] - PHI0_EFF_CANONICAL) < 1e-10

    def test_phi0_dirty_matches_formula(self):
        delta = 0.08
        resp = ns_perturbation_response(delta)
        assert abs(resp["phi0_eff_dirty"] - PHI0_EFF_CANONICAL * (1 + delta)) < 1e-10

    def test_positive_delta_increases_ns(self):
        resp = ns_perturbation_response(0.05)
        assert resp["delta_ns"] > 0

    def test_negative_delta_decreases_ns(self):
        resp = ns_perturbation_response(-0.05)
        assert resp["delta_ns"] < 0

    def test_delta_ns_linear_correct_sign_positive(self):
        resp = ns_perturbation_response(0.05)
        # Both actual and linear prediction should be positive
        assert resp["delta_ns"] > 0
        assert resp["delta_ns_linear"] > 0

    def test_delta_ns_linear_correct_sign_negative(self):
        resp = ns_perturbation_response(-0.05)
        assert resp["delta_ns"] < 0
        assert resp["delta_ns_linear"] < 0


# ---------------------------------------------------------------------------
# VI. ns_linear_sensitivity
# ---------------------------------------------------------------------------

class TestNsLinearSensitivity:
    def test_positive(self):
        assert ns_linear_sensitivity() > 0

    def test_magnitude_reasonable(self):
        # Expected ≈ 72 / PHI0_EFF_CANONICAL²  ≈ 0.073
        s = ns_linear_sensitivity()
        assert 0.04 < s < 0.12

    def test_analytic_vs_numeric_close(self):
        numeric   = ns_linear_sensitivity()
        analytic  = ns_linear_sensitivity_analytic()
        # The analytic formula 72/φ₀² is the exact leading-order coefficient;
        # the numerical derivative should agree to within 5%.
        assert abs(numeric - analytic) / analytic < 0.05

    def test_analytic_formula(self):
        analytic = ns_linear_sensitivity_analytic()
        expected = 72.0 / PHI0_EFF_CANONICAL**2
        assert abs(analytic - expected) < 1e-12


# ---------------------------------------------------------------------------
# VII. dirty_data_check
# ---------------------------------------------------------------------------

class TestDirtyDataCheck:
    def test_passes_small_delta(self):
        result = dirty_data_check(delta=0.05)
        assert result["tracks_perturbation"] is True

    def test_passes_large_delta(self):
        # For large δ=0.20 the nonlinear correction is ~23%, so use wider rtol
        result = dirty_data_check(delta=0.20, rtol=0.30)
        assert result["tracks_perturbation"] is True

    def test_passes_negative_delta(self):
        result = dirty_data_check(delta=-0.10)
        assert result["tracks_perturbation"] is True

    def test_keys_present(self):
        result = dirty_data_check(delta=0.05)
        for key in ("delta", "ns_clean", "ns_dirty", "delta_ns_actual",
                    "delta_ns_predicted", "sensitivity", "relative_error",
                    "rtol", "tracks_perturbation", "verdict"):
            assert key in result

    def test_delta_stored(self):
        result = dirty_data_check(delta=0.07)
        assert abs(result["delta"] - 0.07) < 1e-10

    def test_rtol_stored(self):
        result = dirty_data_check(delta=0.05, rtol=0.15)
        assert abs(result["rtol"] - 0.15) < 1e-10

    def test_raises_on_zero_delta(self):
        with pytest.raises(ValueError):
            dirty_data_check(delta=0.0)

    def test_relative_error_small_for_small_delta(self):
        result = dirty_data_check(delta=0.01)
        # For small δ, linear approximation is very good (< 5% error)
        assert result["relative_error"] < 0.05

    def test_verdict_contains_pass(self):
        result = dirty_data_check(delta=0.05)
        assert "PASS" in result["verdict"]

    def test_positive_delta_increases_ns(self):
        result = dirty_data_check(delta=0.05)
        assert result["ns_dirty"] > result["ns_clean"]

    def test_negative_delta_decreases_ns(self):
        result = dirty_data_check(delta=-0.05)
        assert result["ns_dirty"] < result["ns_clean"]


# ---------------------------------------------------------------------------
# VIII. oracle_detection_report
# ---------------------------------------------------------------------------

class TestOracleDetectionReport:
    def test_keys_present(self):
        rep = oracle_detection_report()
        assert "ns_canonical" in rep
        assert "ns_planck_central" in rep
        assert "perturbations" in rep
        assert "oracle_falsified" in rep

    def test_oracle_is_falsified(self):
        rep = oracle_detection_report()
        assert rep["oracle_falsified"] is True

    def test_all_perturbations_deviate(self):
        rep = oracle_detection_report()
        for delta, info in rep["perturbations"].items():
            assert info["deviates_from_canonical"] is True, (
                f"Perturbation δ={delta} did not deviate from canonical nₛ"
            )

    def test_ns_canonical_reasonable(self):
        rep = oracle_detection_report()
        assert 0.95 < rep["ns_canonical"] < 0.99

    def test_perturbations_has_expected_deltas(self):
        rep = oracle_detection_report()
        assert len(rep["perturbations"]) == 6

    def test_negative_delta_gives_lower_ns(self):
        rep = oracle_detection_report()
        ns_neg = rep["perturbations"][-0.20]["ns_dirty"]
        ns_pos = rep["perturbations"][0.20]["ns_dirty"]
        assert ns_neg < ns_pos


# ---------------------------------------------------------------------------
# IX. r_perturbation_response
# ---------------------------------------------------------------------------

class TestRPerturbationResponse:
    def test_keys_present(self):
        resp = r_perturbation_response(0.05)
        for key in ("phi0_eff_clean", "phi0_eff_dirty", "r_clean", "r_dirty", "delta_r"):
            assert key in resp

    def test_positive_delta_decreases_r(self):
        # r ∝ 1/φ₀_eff², so larger φ → smaller r
        resp = r_perturbation_response(0.10)
        assert resp["delta_r"] < 0

    def test_negative_delta_increases_r(self):
        resp = r_perturbation_response(-0.10)
        assert resp["delta_r"] > 0

    def test_r_clean_positive(self):
        resp = r_perturbation_response(0.05)
        assert resp["r_clean"] > 0

    def test_r_dirty_positive(self):
        resp = r_perturbation_response(0.05)
        assert resp["r_dirty"] > 0


# ---------------------------------------------------------------------------
# X. alpha_kk_scale
# ---------------------------------------------------------------------------

class TestAlphaKkScale:
    def test_keys_present(self):
        info = alpha_kk_scale()
        for key in ("k_cs", "r_c", "f_gauge", "alpha_kk", "alpha_kk_inv",
                    "free_parameters", "status"):
            assert key in info

    def test_k_cs_default(self):
        info = alpha_kk_scale()
        assert info["k_cs"] == 74

    def test_f_gauge_formula(self):
        info = alpha_kk_scale(k_cs=74)
        expected = 74 / (8.0 * math.pi**2)
        assert abs(info["f_gauge"] - expected) < 1e-10

    def test_alpha_kk_formula(self):
        info = alpha_kk_scale(k_cs=74)
        expected = 2.0 * math.pi / 74
        assert abs(info["alpha_kk"] - expected) < 1e-10

    def test_alpha_kk_is_order_one(self):
        # α(M_KK) should be O(1), NOT ≈ 1/137
        info = alpha_kk_scale()
        assert 0.05 < info["alpha_kk"] < 1.0

    def test_alpha_kk_inv_reasonable(self):
        info = alpha_kk_scale()
        # 1/α(M_KK) should be small (order 10), NOT ≈ 137
        assert 5 < info["alpha_kk_inv"] < 20

    def test_no_free_parameters_at_kk_step(self):
        # k_CS is derived; r_c is derived — no free params at this step
        info = alpha_kk_scale()
        assert len(info["free_parameters"]) == 0

    def test_status_says_derived(self):
        info = alpha_kk_scale()
        assert "DERIVED" in info["status"]

    def test_custom_k_cs(self):
        info = alpha_kk_scale(k_cs=61)  # (5,6) pair
        expected_alpha = 2.0 * math.pi / 61
        assert abs(info["alpha_kk"] - expected_alpha) < 1e-10


# ---------------------------------------------------------------------------
# XI. alpha_rg_run
# ---------------------------------------------------------------------------

class TestAlphaRgRun:
    def test_running_decreases_alpha(self):
        # Running from high scale down gives smaller α (larger 1/α)
        # Use moderate scale range to avoid overflow
        alpha_kk = 2.0 * math.pi / 74   # ≈ 0.085
        alpha_low = alpha_rg_run(alpha_kk, m_kk_gev=1e6, mu_gev=0.000511, n_f=3)
        assert alpha_low < alpha_kk

    def test_no_running_at_same_scale(self):
        alpha_kk = 2.0 * math.pi / 74
        alpha_low = alpha_rg_run(alpha_kk, m_kk_gev=1.0, mu_gev=1.0, n_f=3)
        assert abs(alpha_low - alpha_kk) < 1e-10

    def test_more_fermions_more_running(self):
        alpha_kk = 2.0 * math.pi / 74
        alpha_nf1 = alpha_rg_run(alpha_kk, m_kk_gev=1e4, mu_gev=0.001, n_f=1)
        alpha_nf3 = alpha_rg_run(alpha_kk, m_kk_gev=1e4, mu_gev=0.001, n_f=3)
        # More fermions → more running → smaller α at low energy
        assert alpha_nf3 < alpha_nf1

    def test_raises_bad_scales(self):
        with pytest.raises(ValueError):
            alpha_rg_run(0.1, m_kk_gev=0.0, mu_gev=0.001, n_f=3)
        with pytest.raises(ValueError):
            alpha_rg_run(0.1, m_kk_gev=1.0, mu_gev=2.0, n_f=3)

    def test_returns_positive(self):
        alpha_kk = 2.0 * math.pi / 74
        alpha_low = alpha_rg_run(alpha_kk, m_kk_gev=1e5, mu_gev=0.001, n_f=1)
        assert alpha_low > 0


# ---------------------------------------------------------------------------
# XII. alpha_low_energy
# ---------------------------------------------------------------------------

class TestAlphaLowEnergy:
    def test_keys_present(self):
        info = alpha_low_energy()
        for key in ("k_cs", "r_c", "m_kk_gev", "mu_gev", "n_f",
                    "alpha_kk", "alpha_kk_inv", "alpha_low", "alpha_low_inv",
                    "alpha_pdg_inv", "n_f_is_free", "derivation_status",
                    "free_parameters"):
            assert key in info

    def test_n_f_is_free(self):
        info = alpha_low_energy()
        assert info["n_f_is_free"] is True

    def test_free_parameters_nonempty(self):
        info = alpha_low_energy()
        assert len(info["free_parameters"]) >= 1

    def test_status_says_partially_derived(self):
        info = alpha_low_energy()
        assert "PARTIALLY DERIVED" in info["derivation_status"]

    def test_status_mentions_n_f(self):
        info = alpha_low_energy()
        assert "n_f" in info["derivation_status"]

    def test_alpha_pdg_inv_is_137(self):
        info = alpha_low_energy()
        assert abs(info["alpha_pdg_inv"] - 137.036) < 0.01

    def test_alpha_kk_is_order_one(self):
        info = alpha_low_energy()
        assert 0.05 < info["alpha_kk"] < 1.0

    def test_alpha_low_positive(self):
        info = alpha_low_energy()
        assert info["alpha_low"] > 0


# ---------------------------------------------------------------------------
# XIII. mp_over_me_gap_report
# ---------------------------------------------------------------------------

class TestMpOverMeGapReport:
    def test_keys_present(self):
        rep = mp_over_me_gap_report()
        for key in ("target_ratio", "geometric_ratio", "discrepancy_factor",
                    "gaps", "derivation_status"):
            assert key in rep

    def test_target_ratio_correct(self):
        rep = mp_over_me_gap_report()
        assert abs(rep["target_ratio"] - 1836.15) < 0.01

    def test_geometric_ratio_much_smaller(self):
        rep = mp_over_me_gap_report()
        assert rep["geometric_ratio"] < 2.0

    def test_discrepancy_factor_large(self):
        rep = mp_over_me_gap_report()
        # The geometric ratio is ~ 1.3; target is ~1836 → factor ~1400
        assert rep["discrepancy_factor"] > 500

    def test_gaps_list_nonempty(self):
        rep = mp_over_me_gap_report()
        assert len(rep["gaps"]) >= 3

    def test_status_says_not_derivable(self):
        rep = mp_over_me_gap_report()
        assert "NOT DERIVABLE" in rep["derivation_status"]

    def test_geometric_ratio_from_n_w_5(self):
        rep = mp_over_me_gap_report()
        expected = math.sqrt(1.0 + 4.0 / N_W)  # sqrt(9/5) ≈ 1.342
        assert abs(rep["geometric_ratio"] - expected) < 1e-10


# ---------------------------------------------------------------------------
# XIV. axiomzero_challenge_summary
# ---------------------------------------------------------------------------

class TestAxiomzeroChallengeummary:
    def test_keys_present(self):
        summary = axiomzero_challenge_summary()
        for key in ("dirty_data_test", "alpha_derivation",
                    "mp_over_me_derivation", "ns_r_derivation",
                    "overall_verdict"):
            assert key in summary

    def test_dirty_data_verdict_pass(self):
        summary = axiomzero_challenge_summary()
        assert "PASS" in summary["dirty_data_test"]["verdict"]

    def test_oracle_falsified(self):
        summary = axiomzero_challenge_summary()
        assert summary["dirty_data_test"]["oracle_falsified"] is True

    def test_alpha_n_f_is_free(self):
        summary = axiomzero_challenge_summary()
        assert summary["alpha_derivation"]["n_f_is_free"] is True

    def test_mp_over_me_not_derivable(self):
        summary = axiomzero_challenge_summary()
        assert "NOT DERIVABLE" in summary["mp_over_me_derivation"]["status"]

    def test_overall_verdict_string(self):
        summary = axiomzero_challenge_summary()
        assert isinstance(summary["overall_verdict"], str)
        assert len(summary["overall_verdict"]) > 50
