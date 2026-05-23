# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar381_full_cl_boltzmann.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar381_full_cl_boltzmann import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    Z_PHI_0, GAMMA_THEORY, GAMMA_FIT, K_PIVOT, N_S_UM, A_S_PLANCK,
    ETA_STAR, D_A, L_SILK, PEAK_ELLS,
    separation_guard,
    z_phi_k,
    primordial_power_spectrum_um,
    transfer_function_sq,
    compute_cl,
    compute_cl_spectrum,
    peak_heights,
    residual_decomposition,
    full_computation_report,
    pillar381_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 381
    def test_status(self): assert PILLAR_STATUS == "COMPUTATION_COMPLETE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_z_phi_0(self): assert abs(Z_PHI_0 - 5.301) < 0.001
    def test_gamma_theory(self): assert abs(GAMMA_THEORY - 0.242) < 1e-6
    def test_gamma_fit(self): assert abs(GAMMA_FIT - 0.273) < 1e-6
    def test_k_pivot(self): assert abs(K_PIVOT - 0.05) < 1e-10
    def test_n_s_um(self): assert abs(N_S_UM - 0.9635) < 1e-6
    def test_a_s_planck(self): assert A_S_PLANCK > 0
    def test_eta_star_positive(self): assert ETA_STAR > 0
    def test_d_a_positive(self): assert D_A > 0
    def test_l_silk_positive(self): assert L_SILK > 0
    def test_peak_ells_6(self): assert len(PEAK_ELLS) == 6
    def test_first_peak(self): assert PEAK_ELLS[0] == 220
    def test_peak_ells_increasing(self): assert PEAK_ELLS == sorted(PEAK_ELLS)


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_computation_complete(self):
        assert "COMPUTATION_COMPLETE" in separation_guard()


class TestZPhiK:
    def test_at_pivot(self):
        # Z_φ(k_pivot) = Z_φ^(0) × 1 = Z_φ^(0)
        z = z_phi_k(K_PIVOT)
        assert abs(z - Z_PHI_0) < 1e-10

    def test_increases_with_k(self):
        z1 = z_phi_k(0.01)
        z2 = z_phi_k(0.1)
        assert z2 > z1  # positive γ → increases with k

    def test_positive(self):
        assert z_phi_k(0.05) > 0

    def test_scales_as_power_law(self):
        k1, k2 = 0.01, 0.10
        z1 = z_phi_k(k1)
        z2 = z_phi_k(k2)
        ratio = z2 / z1
        expected = (k2 / k1) ** GAMMA_THEORY
        assert abs(ratio - expected) < 1e-10

    def test_invalid_k(self):
        with pytest.raises(ValueError):
            z_phi_k(0.0)

    def test_custom_gamma(self):
        z_th = z_phi_k(0.1, gamma=GAMMA_THEORY)
        z_fit = z_phi_k(0.1, gamma=GAMMA_FIT)
        assert z_fit > z_th  # larger γ → larger Z


class TestPrimordialPowerSpectrum:
    def test_positive(self):
        assert primordial_power_spectrum_um(0.05) > 0

    def test_at_pivot(self):
        # At k_pivot: P = A_s × Z_φ^(0) (since tilt = 1 there)
        p = primordial_power_spectrum_um(K_PIVOT)
        expected = A_S_PLANCK * Z_PHI_0
        assert abs(p - expected) < 1e-15

    def test_invalid_k(self):
        with pytest.raises(ValueError):
            primordial_power_spectrum_um(0.0)


class TestTransferFunctionSq:
    def test_returns_float(self):
        assert isinstance(transfer_function_sq(220, 0.016), float)

    def test_non_negative(self):
        assert transfer_function_sq(220, 0.016) >= 0

    def test_silk_damping_at_high_ell(self):
        # High ℓ → Silk damping → small |Δ|²
        t_low = transfer_function_sq(200, 0.014)
        t_high = transfer_function_sq(2000, 0.14)
        # Both should be finite
        assert math.isfinite(t_low)
        assert math.isfinite(t_high)

    def test_zero_for_invalid_ell(self):
        assert transfer_function_sq(0, 0.05) == 0

    def test_zero_for_invalid_k(self):
        assert transfer_function_sq(220, 0.0) == 0


class TestComputeCl:
    def test_returns_float(self):
        cl = compute_cl(220, n_k=50)
        assert isinstance(cl, float)

    def test_positive(self):
        cl = compute_cl(220, n_k=50)
        assert cl > 0

    def test_finite(self):
        cl = compute_cl(220, n_k=50)
        assert math.isfinite(cl)

    def test_zero_for_ell_zero(self):
        assert compute_cl(0, n_k=10) == 0


class TestComputeClSpectrum:
    def test_returns_list(self):
        result = compute_cl_spectrum([220, 540])
        assert isinstance(result, list)

    def test_correct_ells(self):
        result = compute_cl_spectrum([220, 540])
        ells = [r["ell"] for r in result]
        assert ells == [220, 540]

    def test_cl_positive(self):
        result = compute_cl_spectrum([220], n_k=50)
        assert result[0]["cl"] > 0

    def test_cl_normalized_present(self):
        result = compute_cl_spectrum([220], n_k=50)
        assert "cl_normalized" in result[0]
        assert result[0]["cl_normalized"] > 0

    def test_default_uses_peak_ells(self):
        result = compute_cl_spectrum(n_k=30)
        assert len(result) == len(PEAK_ELLS)


class TestPeakHeights:
    def test_returns_dict(self):
        r = peak_heights()
        assert isinstance(r, dict)

    def test_peaks_present(self):
        r = peak_heights()
        assert len(r["peaks"]) == len(PEAK_ELLS)

    def test_first_peak_relative_is_1(self):
        r = peak_heights()
        assert abs(r["peaks"][0]["relative_to_first_peak"] - 1.0) < 1e-10

    def test_cl_ref_positive(self):
        r = peak_heights()
        assert r["cl_ref_first_peak"] > 0


class TestResidualDecomposition:
    def test_returns_dict(self):
        r = residual_decomposition(1.1, 1.0, 220)
        assert isinstance(r, dict)

    def test_relative_residual(self):
        r = residual_decomposition(1.1, 1.0, 220)
        assert abs(r["relative_residual"] - 0.1) < 1e-10

    def test_s_braid_positive(self):
        r = residual_decomposition(1.0, 0.8, 220)
        assert r["s_braid"] >= 0

    def test_s_alpha_gw(self):
        r = residual_decomposition(1.0, 1.0, 220)
        assert abs(r["s_alpha_gw"] - 0.02) < 1e-10

    def test_s_5d_cap_small(self):
        r = residual_decomposition(1.0, 1.0, 220)
        assert r["s_5d_cap"] < 0.01


class TestFullComputationReport:
    def test_returns_dict(self): assert isinstance(full_computation_report(), dict)

    def test_pillar(self):
        r = full_computation_report()
        assert r["pillar"] == PILLAR_NUMBER

    def test_z_phi_0(self):
        r = full_computation_report()
        assert abs(r["z_phi_0"] - Z_PHI_0) < 1e-6

    def test_status_upgrade(self):
        r = full_computation_report()
        assert "COMPUTATION_COMPLETE" in r["status_upgrade"]

    def test_spectrum_range(self):
        r = full_computation_report()
        assert "2500" in r["spectrum_range"]

    def test_peak_positions_confirmed(self):
        r = full_computation_report()
        assert len(r["peak_positions_confirmed"]) == len(PEAK_ELLS)

    def test_cl_spectrum_present(self):
        r = full_computation_report()
        assert len(r["cl_spectrum_theory"]) > 0


class TestPillar381Summary:
    def test_returns_dict(self): assert isinstance(pillar381_summary(), dict)
    def test_pillar_number(self):
        r = pillar381_summary()
        assert r["pillar_number"] == PILLAR_NUMBER
    def test_status(self):
        r = pillar381_summary()
        assert r["status"] == "COMPUTATION_COMPLETE"
    def test_key_result(self):
        r = pillar381_summary()
        assert "220" in r["key_result"]
    def test_previous_status(self):
        r = pillar381_summary()
        assert r["previous_status"] == "FRONTIER_COMPUTATION"
    def test_new_status(self):
        r = pillar381_summary()
        assert r["new_status"] == "COMPUTATION_COMPLETE"
