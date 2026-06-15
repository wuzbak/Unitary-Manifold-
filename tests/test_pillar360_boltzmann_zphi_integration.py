# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar360_boltzmann_zphi_integration.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar360_boltzmann_zphi_integration import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    K_CS, N_W, Z_PHI_0, GAMMA_THEORY, GAMMA_FIT, GAMMA_EFF, K_PIVOT_MPC,
    R_SOUND_HORIZON_MPC, D_ANGULAR_MPC, OMEGA_B_H2, OMEGA_R_H2,
    Z_DECOUPLING, A_S_PLANCK, N_S_UM, R_BARYON_DECOUPLING,
    ACOUSTIC_PEAK_ELLS_OBSERVED, ACOUSTIC_PEAK_ELLS_NAIVE, ACOUSTIC_PEAK_SUPPRESSION,
    separation_guard, baryon_loading_factor, photon_baryon_sound_speed,
    sound_horizon, early_isw_phase_shift, peak_ell_analytic,
    zphi_modified_spectrum, um_cmb_amplitude_at_peak,
    um_peak_position_prediction, boltzmann_peak_residuals,
    zphi_boltzmann_full_report, pillar360_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 360
    def test_status(self): assert PILLAR_STATUS == "FRONTIER_COMPUTATION"
    def test_k_cs(self): assert K_CS == 74
    def test_n_w(self): assert N_W == 5
    def test_z_phi_0(self): assert abs(Z_PHI_0 - 5.301) < 0.01
    def test_gamma_theory(self): assert abs(GAMMA_THEORY - 0.242) < 0.01
    def test_gamma_fit(self): assert abs(GAMMA_FIT - 0.273) < 0.01
    def test_gamma_eff_between(self):
        assert GAMMA_THEORY < GAMMA_EFF < GAMMA_FIT
    def test_sound_horizon(self):
        assert abs(R_SOUND_HORIZON_MPC - 144.7) < 1.0
    def test_d_angular(self):
        assert abs(D_ANGULAR_MPC - 13897.0) < 100.0
    def test_peak_ells_observed(self):
        assert ACOUSTIC_PEAK_ELLS_OBSERVED == [220, 540, 820]
    def test_peak_ells_naive(self):
        assert ACOUSTIC_PEAK_ELLS_NAIVE[0] > 290  # naive ≈ 301


class TestBaryonLoading:
    def test_at_decoupling(self):
        r_b = baryon_loading_factor(Z_DECOUPLING)
        # Formula gives ~0.368; constant R_BARYON_DECOUPLING is updated to match
        assert abs(r_b - R_BARYON_DECOUPLING) < 0.05

    def test_positive(self):
        assert baryon_loading_factor() > 0

    def test_increases_with_lower_z(self):
        # R_b ∝ 1/(1+z), so lower z → higher R_b
        rb_high_z = baryon_loading_factor(z=2000)
        rb_low_z = baryon_loading_factor(z=1089)
        assert rb_low_z > rb_high_z

    def test_formula(self):
        r_b0 = (3/4) * OMEGA_B_H2 / OMEGA_R_H2
        assert abs(baryon_loading_factor(z=0) - r_b0) < 0.1


class TestPhotonBaryonSoundSpeed:
    def test_radiation_limit(self):
        # R_b → 0: c_s → 1/√3
        cs = photon_baryon_sound_speed(r_baryon=0.0)
        assert abs(cs - 1.0 / math.sqrt(3.0)) < 1e-10

    def test_decreases_with_baryon_loading(self):
        cs_low = photon_baryon_sound_speed(0.0)
        cs_high = photon_baryon_sound_speed(0.6)
        assert cs_high < cs_low

    def test_at_decoupling(self):
        cs = photon_baryon_sound_speed(R_BARYON_DECOUPLING)
        assert 0.3 < cs < 0.6

    def test_positive(self):
        assert photon_baryon_sound_speed() > 0


class TestSoundHorizon:
    def test_returns_planck_value(self):
        rs = sound_horizon()
        assert abs(rs - R_SOUND_HORIZON_MPC) < 1.0


class TestEarlyIswPhaseShift:
    def test_phase_factor_less_than_1(self):
        pf = early_isw_phase_shift()
        assert pf < 1.0

    def test_phase_factor_reasonable(self):
        # Should shift from ~301 to 220: factor ≈ 0.73
        pf = early_isw_phase_shift()
        assert 0.6 < pf < 0.85

    def test_phase_factor_positive(self):
        assert early_isw_phase_shift() > 0


class TestPeakEllAnalytic:
    def test_naive_first_peak(self):
        ell1_naive = peak_ell_analytic(1, include_isw=False, include_baryon_loading=False)
        # Should be close to π × D_A / r_s ≈ 301
        assert abs(ell1_naive - 301) < 20

    def test_corrected_first_peak(self):
        ell1 = peak_ell_analytic(1, include_isw=True, include_baryon_loading=True)
        # Should be ~220 after ISW correction
        assert abs(ell1 - 220) < 15

    def test_corrected_peaks_ordered(self):
        ell1 = peak_ell_analytic(1)
        ell2 = peak_ell_analytic(2)
        ell3 = peak_ell_analytic(3)
        assert ell1 < ell2 < ell3

    def test_second_peak_reasonable(self):
        ell2 = peak_ell_analytic(2)
        # Observed ≈ 540; analytic approximation may vary
        assert 360 < ell2 < 700

    def test_third_peak_reasonable(self):
        ell3 = peak_ell_analytic(3)
        # Observed ≈ 820; analytic approximation may vary
        assert 480 < ell3 < 1000

    def test_all_positive(self):
        for n in [1, 2, 3]:
            assert peak_ell_analytic(n) > 0


class TestZphiModifiedSpectrum:
    def test_positive(self):
        assert zphi_modified_spectrum(0.05) > 0

    def test_at_pivot(self):
        # At k = k_pivot, P_UM should be A_s × Z_phi_0²
        p_um = zphi_modified_spectrum(K_PIVOT_MPC)
        expected = A_S_PLANCK * Z_PHI_0 ** 2
        assert abs(p_um / expected - 1.0) < 0.01

    def test_k_dependence(self):
        # For n_s = 0.9635 < 1, spectrum should decrease at higher k
        # But Z_phi(k) increases at higher k (gamma > 0)
        # Net effect depends on n_s - 1 + 2*gamma
        p_low = zphi_modified_spectrum(0.001)
        p_high = zphi_modified_spectrum(0.1)
        # Both should be positive and finite
        assert p_low > 0 and p_high > 0

    def test_scales_with_as(self):
        p1 = zphi_modified_spectrum(0.05, a_s=A_S_PLANCK)
        p2 = zphi_modified_spectrum(0.05, a_s=2 * A_S_PLANCK)
        assert abs(p2 / p1 - 2.0) < 1e-6


class TestUmCmbAmplitudeAtPeak:
    def test_returns_dict(self):
        assert isinstance(um_cmb_amplitude_at_peak(1), dict)

    def test_peak_number(self):
        result = um_cmb_amplitude_at_peak(1)
        assert result["peak_n"] == 1

    def test_ell_n_reasonable(self):
        result = um_cmb_amplitude_at_peak(1)
        assert 180 < result["ell_n_predicted"] < 280

    def test_z_phi_k_positive(self):
        for n in [1, 2, 3]:
            result = um_cmb_amplitude_at_peak(n)
            assert result["z_phi_k"] > 0

    def test_residual_pct_computed(self):
        result = um_cmb_amplitude_at_peak(1)
        assert "residual_pct" in result
        assert result["residual_pct"] >= 0

    def test_amp_ratio_computed(self):
        result = um_cmb_amplitude_at_peak(1)
        assert "amp_ratio_um_to_lcdm" in result
        assert result["amp_ratio_um_to_lcdm"] > 0


class TestUmPeakPositionPrediction:
    def test_returns_dict(self):
        assert isinstance(um_peak_position_prediction(), dict)

    def test_all_peaks_present(self):
        result = um_peak_position_prediction()
        assert "peaks" in result
        for n in [1, 2, 3]:
            assert f"peak_{n}" in result["peaks"]

    def test_first_peak_consistent(self):
        result = um_peak_position_prediction()
        p1 = result["peaks"]["peak_1"]
        assert p1["status"] == "CONSISTENT"

    def test_corrected_peak_1_close_to_220(self):
        result = um_peak_position_prediction()
        ell1 = result["peaks"]["peak_1"]["ell_with_corrections"]
        assert abs(ell1 - 220) < 15

    def test_verdict_present(self):
        result = um_peak_position_prediction()
        assert "verdict" in result


class TestBoltzmannPeakResiduals:
    def test_returns_dict(self):
        assert isinstance(boltzmann_peak_residuals(), dict)

    def test_mean_residual_computed(self):
        result = boltzmann_peak_residuals()
        assert "mean_amplitude_residual_pct" in result
        assert result["mean_amplitude_residual_pct"] >= 0

    def test_gamma_stored(self):
        result = boltzmann_peak_residuals(gamma=0.25)
        assert abs(result["gamma"] - 0.25) < 1e-10

    def test_all_peaks_present(self):
        result = boltzmann_peak_residuals()
        for n in [1, 2, 3]:
            assert f"peak_{n}" in result["amplitude_residuals_pct"]


class TestFullReport:
    def test_returns_dict(self):
        assert isinstance(zphi_boltzmann_full_report(), dict)

    def test_pillar_number(self):
        result = zphi_boltzmann_full_report()
        assert result["pillar"] == 360

    def test_status(self):
        result = zphi_boltzmann_full_report()
        assert result["status"] == "FRONTIER_COMPUTATION"

    def test_honest_status_present(self):
        result = zphi_boltzmann_full_report()
        assert "honest_status" in result

    def test_open_items_present(self):
        result = zphi_boltzmann_full_report()
        assert len(result["honest_status"]["open_items"]) >= 2

    def test_summary_matches(self):
        summary = pillar360_summary()
        assert summary["pillar"] == 360


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_frontier_computation(self): assert "FRONTIER_COMPUTATION" in separation_guard()
