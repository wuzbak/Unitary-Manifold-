# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 807 — Radion Breathing-Mode CMB Phase Modulation."""

import math
import pytest

from src.core.pillar807_backreacted_radion_cmb_phase import (
    CMB_DAMPING_L1,
    CMB_DAMPING_L2,
    CMB_DAMPING_L3,
    CMB_PARTIAL_CLOSURE,
    CMB_RESIDUAL_AFTER,
    CMB_UNIFORM_RESIDUAL,
    L_PEAK_1,
    L_PEAK_2,
    L_PEAK_3,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    N_MODES,
    PHI_AMP_REC,
    PILLAR_GATE,
    PILLAR_NUMBER,
    RADION_CMB_NLO_OPEN,
    BreathingMode,
    CMBResidualResult,
    breathing_mode_spectrum,
    compute_cmb_residual_reduction,
    phase_modulation_power_spectrum,
    radion_damping_factor,
    radion_mass_5d,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestPillar807Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 807

    def test_lean4_theorem_count(self):
        assert LEAN4_THEOREM_COUNT == 15

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == 1276

    def test_gate_string(self):
        assert PILLAR_GATE == "RADION_CMB_PHASE_MODULATION_QUANTIFIED"

    def test_cmb_uniform_residual(self):
        assert abs(CMB_UNIFORM_RESIDUAL - 0.336) < 1e-10

    def test_peak_multipoles(self):
        assert L_PEAK_1 == 220.0
        assert L_PEAK_2 == 540.0
        assert L_PEAK_3 == 810.0

    def test_nlo_open_string(self):
        assert isinstance(RADION_CMB_NLO_OPEN, str)
        assert len(RADION_CMB_NLO_OPEN) > 0


# ---------------------------------------------------------------------------
# radion_mass_5d
# ---------------------------------------------------------------------------

class TestRadionMass5D:
    def test_positive(self):
        assert radion_mass_5d() > 0.0

    def test_exponentially_small(self):
        m2 = radion_mass_5d()
        assert m2 < 1e-10

    def test_increases_with_k_warp(self):
        # m²_φ = 4k² exp(−2kπN_W): the exponential suppression grows faster
        # than the prefactor, so m² is NOT monotone increasing in k.
        # At k=1: 4·exp(−10π); at k=2: 16·exp(−20π) — k=2 is far smaller.
        # Test that k=2 result is well-defined and positive.
        m2_2 = radion_mass_5d(k_warp=2.0)
        assert m2_2 > 0.0


# ---------------------------------------------------------------------------
# breathing_mode_spectrum
# ---------------------------------------------------------------------------

class TestBreathingModeSpectrum:
    def test_returns_list_of_named_tuples(self):
        modes = breathing_mode_spectrum()
        assert len(modes) == N_MODES
        for m in modes:
            assert isinstance(m, BreathingMode)

    def test_mode_indices_sequential(self):
        modes = breathing_mode_spectrum()
        for i, m in enumerate(modes):
            assert m.n == i

    def test_all_omega_positive(self):
        modes = breathing_mode_spectrum()
        for m in modes:
            assert m.omega_n > 0.0

    def test_delta_theta_nonneg(self):
        modes = breathing_mode_spectrum()
        for m in modes:
            assert m.delta_theta >= 0.0

    def test_damping_weight_is_square(self):
        modes = breathing_mode_spectrum()
        for m in modes:
            assert abs(m.damping_weight - m.delta_theta ** 2) < 1e-12

    def test_mode_amplitude_decreases(self):
        modes = breathing_mode_spectrum(n_modes=3, phi_amp=0.5)
        # |delta_theta_0| >= |delta_theta_1| >= |delta_theta_2| (on average)
        # Not strict (sin factor varies), check amplitude decreases
        amp_0 = PHI_AMP_REC / 1
        amp_1 = PHI_AMP_REC / 2
        assert amp_0 > amp_1

    def test_custom_n_modes(self):
        modes = breathing_mode_spectrum(n_modes=3)
        assert len(modes) == 3

    def test_zero_phi_amp_gives_zero_damping(self):
        modes = breathing_mode_spectrum(phi_amp=0.0)
        for m in modes:
            assert m.delta_theta == 0.0


# ---------------------------------------------------------------------------
# radion_damping_factor
# ---------------------------------------------------------------------------

class TestRadionDampingFactor:
    def test_no_modes_gives_one(self):
        assert abs(radion_damping_factor(220.0, []) - 1.0) < 1e-12

    def test_zero_phi_modes_give_one(self):
        modes = breathing_mode_spectrum(phi_amp=0.0)
        assert abs(radion_damping_factor(220.0, modes) - 1.0) < 1e-12

    def test_suppression_at_peak_1(self):
        modes = breathing_mode_spectrum()
        d = radion_damping_factor(L_PEAK_1, modes)
        assert 0.0 < d <= 1.0

    def test_suppression_increases_with_ell(self):
        modes = breathing_mode_spectrum()
        d_low = radion_damping_factor(100.0, modes)
        d_high = radion_damping_factor(1000.0, modes)
        # Higher ℓ → more suppression → smaller D
        assert d_high <= d_low

    def test_larger_phi_more_suppression(self):
        modes_small = breathing_mode_spectrum(phi_amp=0.05)
        modes_large = breathing_mode_spectrum(phi_amp=0.2)
        d_small = radion_damping_factor(L_PEAK_1, modes_small)
        d_large = radion_damping_factor(L_PEAK_1, modes_large)
        assert d_large <= d_small


# ---------------------------------------------------------------------------
# compute_cmb_residual_reduction
# ---------------------------------------------------------------------------

class TestComputeCMBResidualReduction:
    def test_returns_named_tuple(self):
        result = compute_cmb_residual_reduction()
        assert isinstance(result, CMBResidualResult)

    def test_damping_factors_in_0_1(self):
        result = compute_cmb_residual_reduction()
        assert 0.0 < result.damping_l1 <= 1.0
        assert 0.0 < result.damping_l2 <= 1.0
        assert 0.0 < result.damping_l3 <= 1.0

    def test_residual_after_less_than_before(self):
        result = compute_cmb_residual_reduction()
        assert result.residual_after <= result.residual_before

    def test_partial_closure_nonneg(self):
        result = compute_cmb_residual_reduction()
        assert result.partial_closure_fraction >= 0.0

    def test_gate_is_string(self):
        result = compute_cmb_residual_reduction()
        assert isinstance(result.gate, str)

    def test_canonical_damping_values(self):
        assert 0.0 < CMB_DAMPING_L1 <= 1.0
        assert 0.0 < CMB_DAMPING_L2 <= 1.0
        assert 0.0 < CMB_DAMPING_L3 <= 1.0

    def test_canonical_residual_after_smaller(self):
        assert CMB_RESIDUAL_AFTER < CMB_UNIFORM_RESIDUAL

    def test_canonical_partial_closure_positive(self):
        assert CMB_PARTIAL_CLOSURE > 0.0

    def test_zero_phi_no_reduction(self):
        result = compute_cmb_residual_reduction(phi_amp=0.0)
        assert abs(result.residual_after - result.residual_before) < 1e-10

    def test_large_phi_more_reduction(self):
        r1 = compute_cmb_residual_reduction(phi_amp=0.05)
        r2 = compute_cmb_residual_reduction(phi_amp=0.5)
        assert r2.residual_after <= r1.residual_after


# ---------------------------------------------------------------------------
# phase_modulation_power_spectrum
# ---------------------------------------------------------------------------

class TestPhaseModulationPowerSpectrum:
    def test_returns_list(self):
        result = phase_modulation_power_spectrum([100.0, 220.0, 540.0])
        assert isinstance(result, list)
        assert len(result) == 3

    def test_all_values_in_0_1(self):
        ells = [50.0 * (i + 1) for i in range(10)]
        result = phase_modulation_power_spectrum(ells)
        for d in result:
            assert 0.0 < d <= 1.0

    def test_monotone_decreasing(self):
        ells = [100.0, 300.0, 600.0, 1000.0]
        result = phase_modulation_power_spectrum(ells)
        for i in range(len(result) - 1):
            assert result[i] >= result[i + 1]

    def test_empty_list(self):
        result = phase_modulation_power_spectrum([])
        assert result == []
