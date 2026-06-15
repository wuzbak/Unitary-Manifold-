# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar374_full_zphi_cmb_power_spectrum.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar374_full_zphi_cmb_power_spectrum import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    Z_PHI_0, GAMMA_SPECTRAL, GAMMA_FIT, K_PIVOT, N_S_UM, R_UM,
    PEAK_ELLS, CLASSICAL_SUPPRESSION,
    separation_guard, z_phi_k, primordial_power_spectrum_um,
    cmb_peak_transfer, full_cl_prediction, peak_residual_table,
    honest_residual_summary, pillar374_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 374
    def test_status(self): assert PILLAR_STATUS == "FRONTIER_COMPUTATION"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_z_phi_0(self): assert abs(Z_PHI_0 - 5.301) < 0.01
    def test_gamma_spectral(self): assert abs(GAMMA_SPECTRAL - 0.242) < 0.001
    def test_gamma_fit(self): assert abs(GAMMA_FIT - 0.273) < 0.001
    def test_k_pivot(self): assert abs(K_PIVOT - 0.05) < 0.001
    def test_n_s_um(self): assert abs(N_S_UM - 0.9635) < 0.001
    def test_r_um(self): assert abs(R_UM - 0.0315) < 0.001
    def test_peak_ells_nonempty(self): assert len(PEAK_ELLS) >= 5
    def test_classical_suppression_nonempty(self): assert len(CLASSICAL_SUPPRESSION) >= 4


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_frontier(self): assert "FRONTIER" in separation_guard()


class TestZPhiK:
    def test_at_pivot_returns_zphi0(self):
        z = z_phi_k(K_PIVOT, GAMMA_SPECTRAL)
        assert abs(z - Z_PHI_0) < 1e-6

    def test_increases_above_pivot(self):
        z_above = z_phi_k(K_PIVOT * 10, GAMMA_SPECTRAL)
        z_at = z_phi_k(K_PIVOT, GAMMA_SPECTRAL)
        assert z_above > z_at   # k > k_piv → k/k_piv > 1 → z^γ > 1

    def test_decreases_below_pivot(self):
        z_below = z_phi_k(K_PIVOT * 0.1, GAMMA_SPECTRAL)
        z_at = z_phi_k(K_PIVOT, GAMMA_SPECTRAL)
        assert z_below < z_at

    def test_zero_k_returns_zphi0(self):
        z = z_phi_k(0.0)
        assert abs(z - Z_PHI_0) < 1e-6

    def test_positive_for_any_k(self):
        for k in [0.001, 0.05, 0.5, 5.0]:
            assert z_phi_k(k) > 0

    def test_gamma_fit_vs_theory(self):
        z_theory = z_phi_k(0.1, GAMMA_SPECTRAL)
        z_fit = z_phi_k(0.1, GAMMA_FIT)
        assert z_fit > z_theory   # higher γ → larger exponent above pivot


class TestPrimordialPowerSpectrumUm:
    def test_positive_at_pivot(self):
        p = primordial_power_spectrum_um(K_PIVOT)
        assert p > 0

    def test_as_scale(self):
        p1 = primordial_power_spectrum_um(K_PIVOT, use_as_planck=True)
        p2 = primordial_power_spectrum_um(K_PIVOT, use_as_planck=False)
        assert abs(p1 / p2 - 2.1e-9) < 1e-9

    def test_zero_k_returns_zero(self):
        assert primordial_power_spectrum_um(0.0) == 0.0

    def test_includes_z_phi(self):
        p_um = primordial_power_spectrum_um(K_PIVOT)
        p_bare = 2.1e-9   # A_s at pivot without tilt or Z_phi
        assert abs(p_um / p_bare - Z_PHI_0) < 0.1


class TestCmbPeakTransfer:
    def test_returns_dict(self): assert isinstance(cmb_peak_transfer(220), dict)
    def test_ell_in_result(self): assert cmb_peak_transfer(220)["ell"] == 220
    def test_z_phi_k_positive(self): assert cmb_peak_transfer(220)["z_phi_k"] > 0
    def test_classical_suppression_present(self): assert "classical_suppression" in cmb_peak_transfer(220)
    def test_amplitude_ratio_present(self): assert "amplitude_ratio_to_lcdm" in cmb_peak_transfer(220)
    def test_percent_deviation_present(self): assert "percent_deviation" in cmb_peak_transfer(220)
    def test_l2_ell(self): assert "k_ell_mpc" in cmb_peak_transfer(2)


class TestFullClPrediction:
    def test_returns_list(self): assert isinstance(full_cl_prediction(), list)
    def test_same_length_as_peak_ells(self):
        result = full_cl_prediction()
        assert len(result) == len(PEAK_ELLS)
    def test_custom_ells(self):
        result = full_cl_prediction(ells=[220, 540])
        assert len(result) == 2
    def test_each_has_ell(self):
        for r in full_cl_prediction():
            assert "ell" in r
    def test_custom_gamma(self):
        r1 = full_cl_prediction(gamma=GAMMA_SPECTRAL)
        r2 = full_cl_prediction(gamma=GAMMA_FIT)
        # Different gamma → different amplitudes
        assert r1[1]["amplitude_ratio_to_lcdm"] != r2[1]["amplitude_ratio_to_lcdm"]


class TestPeakResidualTable:
    def test_returns_list(self): assert isinstance(peak_residual_table(), list)
    def test_three_peaks(self): assert len(peak_residual_table()) == 3
    def test_ells_220_540_820(self):
        ells = [r["ell"] for r in peak_residual_table()]
        assert 220 in ells and 540 in ells and 820 in ells
    def test_each_has_residual_pct(self):
        for r in peak_residual_table():
            assert "residual_pct_theory" in r
            assert "residual_pct_fit" in r
    def test_status_present(self):
        for r in peak_residual_table():
            assert "status" in r


class TestHonestResidualSummary:
    def test_returns_dict(self): assert isinstance(honest_residual_summary(), dict)
    def test_pillar(self): assert honest_residual_summary()["pillar"] == 374
    def test_z_phi_0_present(self): assert abs(honest_residual_summary()["z_phi_0"] - Z_PHI_0) < 0.01
    def test_peak_table_present(self): assert "peak_table" in honest_residual_summary()
    def test_open_frontiers_present(self): assert len(honest_residual_summary()["open_frontiers"]) >= 3
    def test_l2_mention(self):
        s = honest_residual_summary()
        assert "l2_gamma_discrepancy_impact" in s


class TestPillar374Summary:
    def test_pillar(self): assert pillar374_summary()["pillar"] == 374
    def test_status(self): assert pillar374_summary()["status"] == "FRONTIER_COMPUTATION"
    def test_honest_residuals(self): assert pillar374_summary()["honest_residuals"] is True
    def test_peaks_covered(self):
        s = pillar374_summary()
        assert len(s["peaks_covered"]) >= 5
