# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_kk_zero_mode_spectral_closure.py
============================================
Tests for src/core/kk_zero_mode_spectral_closure.py

Covers all public functions: ~25 tests.
"""

import math

import pytest

from src.core.kk_zero_mode_spectral_closure import (
    H_INFLATION_PLANCK,
    N_MAX_DEFAULT,
    backreaction_control_parameter,
    kk_mass_spectrum,
    kk_zero_mode_spectral_closure_report,
    mass_gap_to_hubble_ratio,
    newton_coupling_from_kk_reduction,
    spectral_sum_convergence,
    zero_mode_dominance_at_low_energy,
    zero_mode_masslessness_proof,
)
from src.core.kk_backreaction import N_W, PHI0_FTUM, R_KK_NATURAL


# ---------------------------------------------------------------------------
# kk_mass_spectrum
# ---------------------------------------------------------------------------


class TestKKMassSpectrum:
    def test_zero_mode_mass_is_zero(self):
        result = kk_mass_spectrum()
        assert result["masses"][0] == 0.0

    def test_m0_is_zero_flag(self):
        assert kk_mass_spectrum()["m0_is_zero"] is True

    def test_levels_length(self):
        result = kk_mass_spectrum(n_max=10)
        assert len(result["levels"]) == 11
        assert len(result["masses"]) == 11

    def test_mass_formula_m1(self):
        R = 2.0
        result = kk_mass_spectrum(n_max=5, R_KK=R)
        assert result["masses"][1] == pytest.approx(1.0 / R)

    def test_mass_formula_m5(self):
        R = 0.5
        result = kk_mass_spectrum(n_max=5, R_KK=R)
        assert result["masses"][5] == pytest.approx(5.0 / R)

    def test_mass_gap_equals_m1(self):
        result = kk_mass_spectrum(R_KK=R_KK_NATURAL)
        assert result["mass_gap"] == pytest.approx(result["m1"])

    def test_invalid_n_max(self):
        with pytest.raises(ValueError):
            kk_mass_spectrum(n_max=-1)

    def test_invalid_R_KK(self):
        with pytest.raises(ValueError):
            kk_mass_spectrum(R_KK=0.0)


# ---------------------------------------------------------------------------
# zero_mode_masslessness_proof
# ---------------------------------------------------------------------------


class TestZeroModeMasslessnessProof:
    def test_is_massless_true(self):
        result = zero_mode_masslessness_proof()
        assert result["is_massless"] is True

    def test_m0_exactly_zero(self):
        result = zero_mode_masslessness_proof()
        assert result["m0"] == 0.0

    def test_massless_for_various_R(self):
        for R in [0.1, 0.5, 1.0, 10.0]:
            assert zero_mode_masslessness_proof(R_KK=R)["is_massless"] is True

    def test_proof_string_present(self):
        result = zero_mode_masslessness_proof()
        assert isinstance(result["proof"], str)
        assert len(result["proof"]) > 10


# ---------------------------------------------------------------------------
# mass_gap_to_hubble_ratio
# ---------------------------------------------------------------------------


class TestMassGapToHubbleRatio:
    def test_ratio_exceeds_100(self):
        result = mass_gap_to_hubble_ratio()
        assert result["ratio"] > 100.0

    def test_ratio_large_with_default_H(self):
        result = mass_gap_to_hubble_ratio(H_hubble=H_INFLATION_PLANCK)
        # m_1 = 1/R_KK_NATURAL = 1.0; H ~ 1.85e-5
        assert result["ratio"] == pytest.approx(1.0 / H_INFLATION_PLANCK, rel=1e-6)

    def test_decouples_flag(self):
        result = mass_gap_to_hubble_ratio()
        assert result["decouples"] is True

    def test_custom_H_decoupling(self):
        # Even with a higher H, m_1/H > 1 as long as H < m_1
        result = mass_gap_to_hubble_ratio(H_hubble=0.5, R_KK=1.0)
        assert result["ratio"] == pytest.approx(2.0)
        assert result["decouples"] is True

    def test_invalid_H(self):
        with pytest.raises(ValueError):
            mass_gap_to_hubble_ratio(H_hubble=0.0)


# ---------------------------------------------------------------------------
# newton_coupling_from_kk_reduction
# ---------------------------------------------------------------------------


class TestNewtonCouplingFromKKReduction:
    def test_G4_times_pi_R_equals_G5(self):
        result = newton_coupling_from_kk_reduction()
        assert result["G_4_times_pi_R"] == pytest.approx(1.0, rel=1e-10)

    def test_identity_holds_flag(self):
        assert newton_coupling_from_kk_reduction()["identity_holds"] is True

    def test_G4_formula(self):
        G5 = 2.0
        R = 3.0
        result = newton_coupling_from_kk_reduction(G5=G5, R_KK=R)
        assert result["G_4"] == pytest.approx(G5 / (math.pi * R), rel=1e-10)

    def test_residual_is_tiny(self):
        result = newton_coupling_from_kk_reduction()
        assert result["residual"] < 1e-12

    def test_invalid_G5(self):
        with pytest.raises(ValueError):
            newton_coupling_from_kk_reduction(G5=0.0)

    def test_invalid_R(self):
        with pytest.raises(ValueError):
            newton_coupling_from_kk_reduction(R_KK=-1.0)


# ---------------------------------------------------------------------------
# backreaction_control_parameter
# ---------------------------------------------------------------------------


class TestBackreactionControlParameter:
    def test_delta_phi_less_than_0_1(self):
        result = backreaction_control_parameter()
        assert result["delta_phi_over_phi"] < 0.1

    def test_is_controlled_true(self):
        assert backreaction_control_parameter()["is_controlled"] is True

    def test_is_small_true_for_n_w(self):
        result = backreaction_control_parameter(n_modes=N_W)
        assert result["is_small"] is True

    def test_formula_value_at_n_w_5(self):
        expected = 25.0 / (48.0 * math.pi ** 2)
        result = backreaction_control_parameter(n_modes=5)
        assert result["delta_phi_over_phi"] == pytest.approx(expected, rel=1e-10)

    def test_delta_phi_absolute(self):
        result = backreaction_control_parameter(n_modes=5, phi0=PHI0_FTUM)
        expected = 25.0 / (48.0 * math.pi ** 2) * PHI0_FTUM
        assert result["delta_phi"] == pytest.approx(expected, rel=1e-10)

    def test_invalid_n_modes(self):
        with pytest.raises(ValueError):
            backreaction_control_parameter(n_modes=0)


# ---------------------------------------------------------------------------
# zero_mode_dominance_at_low_energy
# ---------------------------------------------------------------------------


class TestZeroModeDominanceAtLowEnergy:
    def test_zero_mode_dominates_all(self):
        result = zero_mode_dominance_at_low_energy()
        assert result["zero_mode_dominates_all"] is True

    def test_zero_mode_always_propagates(self):
        result = zero_mode_dominance_at_low_energy()
        assert all(result["zero_mode_propagates"])

    def test_kk_modes_not_accessible_at_low_E(self):
        result = zero_mode_dominance_at_low_energy()
        assert not any(result["kk_modes_accessible"])

    def test_custom_energies_below_m1(self):
        R = 1.0
        m1 = 1.0 / R
        E_values = [m1 * f for f in [0.01, 0.1, 0.5, 0.9]]
        result = zero_mode_dominance_at_low_energy(E_test_values=E_values, R_KK=R)
        assert result["zero_mode_dominates_all"] is True


# ---------------------------------------------------------------------------
# spectral_sum_convergence
# ---------------------------------------------------------------------------


class TestSpectralSumConvergence:
    def test_returns_expected_keys(self):
        result = spectral_sum_convergence()
        for key in ("T55_partial_sums", "relative_increments", "reference_T55", "n_max"):
            assert key in result

    def test_partial_sums_length(self):
        result = spectral_sum_convergence(n_max=10)
        assert len(result["T55_partial_sums"]) == 10

    def test_reference_T55_matches_last_partial_sum(self):
        result = spectral_sum_convergence(n_max=N_MAX_DEFAULT)
        assert result["T55_partial_sums"][-1] == pytest.approx(result["reference_T55"], rel=1e-10)

    def test_invalid_n_max(self):
        with pytest.raises(ValueError):
            spectral_sum_convergence(n_max=1)


# ---------------------------------------------------------------------------
# kk_zero_mode_spectral_closure_report
# ---------------------------------------------------------------------------


class TestSpectralClosureReport:
    def test_status_is_closed(self):
        report = kk_zero_mode_spectral_closure_report()
        assert report["status"] == "CLOSED"

    def test_all_closure_flags_true(self):
        report = kk_zero_mode_spectral_closure_report()
        flags = report["closure_flags"]
        assert flags["zero_mode_massless"] is True
        assert flags["mass_gap_exceeds_hubble"] is True
        assert flags["newton_identity_holds"] is True
        assert flags["backreaction_controlled"] is True
        assert flags["zero_mode_dominates"] is True

    def test_residual_open_items_present(self):
        report = kk_zero_mode_spectral_closure_report()
        items = report["residual_open_items"]
        assert len(items) >= 1
        assert any("UV" in item for item in items)

    def test_summary_string(self):
        report = kk_zero_mode_spectral_closure_report()
        assert "CLOSED" in report["summary"]

    def test_checks_keys_present(self):
        report = kk_zero_mode_spectral_closure_report()
        for key in ("masslessness", "mass_gap", "newton_coupling", "backreaction",
                    "zero_mode_dominance", "spectral_convergence", "spectrum"):
            assert key in report["checks"]
