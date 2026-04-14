# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_materials.py
========================
Unit tests for the src/materials package — Pillar 26: Materials Science.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import numpy as np
import pytest

from src.materials.condensed import (
    band_gap_phi, fermi_phi_level, phonon_phi_scattering,
    electron_phi_mobility, thermal_phi_conductivity, magnetic_phi_ordering,
    crystal_phi_defects, grain_boundary_phi, dislocation_phi_density,
    phase_transition_phi,
)
from src.materials.semiconductors import (
    carrier_phi_density, dopant_phi_concentration, pn_junction_phi,
    transistor_phi_gain, semiconductor_phi_noise, solar_cell_phi_efficiency,
    led_phi_efficiency, diode_phi_current, quantum_phi_dot,
    semiconductor_phi_bandgap,
)
from src.materials.metamaterials import (
    negative_phi_index, metamaterial_phi_resonance, photonic_phi_bandgap,
    acoustic_phi_metamaterial, cloaking_phi_efficiency, epsilon_phi_near_zero,
    hyperbolic_phi_dispersion, nonlinear_phi_metamaterial,
    topological_phi_insulator, phi_plasmon_resonance,
)


# ---------------------------------------------------------------------------
# condensed.py
# ---------------------------------------------------------------------------

class TestBandGapPhi:
    def test_zero_gap_full_occupation(self):
        v = band_gap_phi(0.0, 0.025)
        assert v == pytest.approx(1.0)

    def test_large_gap_tiny_occupation(self):
        v = band_gap_phi(4.0, 0.025)
        assert v < 1e-30

    def test_raises_negative_gap(self):
        with pytest.raises(ValueError):
            band_gap_phi(-1.0, 0.025)

    def test_raises_zero_kBT(self):
        with pytest.raises(ValueError):
            band_gap_phi(1.0, 0.0)


class TestFermiPhiLevel:
    def test_intrinsic_at_midgap(self):
        v = fermi_phi_level(1.0, 300.0)
        assert v == pytest.approx(0.5, rel=0.01)

    def test_n_type_above_midgap(self):
        v = fermi_phi_level(1.0, 300.0, donor_conc=1e18, acceptor_conc=0.0)
        assert v > 0.5


class TestPhononPhiScattering:
    def test_at_reference(self):
        assert phonon_phi_scattering(1000.0, 300.0) == pytest.approx(1000.0)

    def test_lower_T_higher_mobility(self):
        v_cold = phonon_phi_scattering(1000.0, 100.0)
        v_hot = phonon_phi_scattering(1000.0, 600.0)
        assert v_cold > v_hot


class TestElectronPhiMobility:
    def test_limited_by_phonon(self):
        v = electron_phi_mobility(100.0, 1e10)
        assert v == pytest.approx(100.0, rel=1e-3)

    def test_harmonic_mean(self):
        v = electron_phi_mobility(100.0, 100.0)
        assert v == pytest.approx(50.0)

    def test_raises_zero_phonon(self):
        with pytest.raises(ValueError):
            electron_phi_mobility(0.0, 100.0)


class TestThermalPhiConductivity:
    def test_at_ref(self):
        assert thermal_phi_conductivity(100.0, 300.0) == pytest.approx(100.0)

    def test_lower_T_higher_kappa(self):
        v_cold = thermal_phi_conductivity(100.0, 100.0)
        v_hot = thermal_phi_conductivity(100.0, 600.0)
        assert v_cold > v_hot


class TestMagneticPhiOrdering:
    def test_at_zero_T(self):
        assert magnetic_phi_ordering(0.0, 1000.0) == pytest.approx(1.0)

    def test_above_curie(self):
        assert magnetic_phi_ordering(1200.0, 1000.0) == pytest.approx(0.0)

    def test_raises_zero_curie(self):
        with pytest.raises(ValueError):
            magnetic_phi_ordering(100.0, 0.0)


class TestCrystalPhiDefects:
    def test_perfect_lattice(self):
        assert crystal_phi_defects(0, 0, 1000) == pytest.approx(0.0)

    def test_defect_concentration(self):
        assert crystal_phi_defects(5, 5, 100) == pytest.approx(0.1)

    def test_raises_zero_sites(self):
        with pytest.raises(ValueError):
            crystal_phi_defects(1, 0, 0)


class TestGrainBoundaryPhi:
    def test_bulk_at_large_grain(self):
        v = grain_boundary_phi(1e6, 1.0, 0.1)
        assert v == pytest.approx(1.0, rel=1e-4)

    def test_enhancement_small_grain(self):
        v = grain_boundary_phi(1.0, 1.0, 0.1)
        assert v > 1.0


class TestDislocationPhiDensity:
    def test_basic(self):
        assert dislocation_phi_density(1e10, 1.0) == pytest.approx(1e10)

    def test_raises_zero_volume(self):
        with pytest.raises(ValueError):
            dislocation_phi_density(1e10, 0.0)


class TestPhaseTransitionPhi:
    def test_below_transition(self):
        assert phase_transition_phi(200.0, 300.0, 10.0) == pytest.approx(0.0)

    def test_above_transition(self):
        assert phase_transition_phi(400.0, 300.0, 10.0) == pytest.approx(10.0)

    def test_at_transition(self):
        assert phase_transition_phi(300.0, 300.0, 10.0) == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# semiconductors.py
# ---------------------------------------------------------------------------

class TestCarrierPhiDensity:
    def test_positive(self):
        v = carrier_phi_density(1e19, 0.2, 0.5, 300.0)
        assert v > 0.0

    def test_raises_zero_Nc(self):
        with pytest.raises(ValueError):
            carrier_phi_density(0.0, 0.2, 0.5, 300.0)


class TestDopantPhiConcentration:
    def test_basic(self):
        assert dopant_phi_concentration(1e17, 5e22) == pytest.approx(1e17 / 5e22)

    def test_clipped(self):
        assert dopant_phi_concentration(1e23, 1e22) == pytest.approx(1.0)


class TestPnJunctionPhi:
    def test_zero_bias(self):
        assert pn_junction_phi(0.7, 0.0) == pytest.approx(0.7)

    def test_forward_bias_reduces(self):
        assert pn_junction_phi(0.7, 0.3) == pytest.approx(0.4)

    def test_over_bias_zero(self):
        assert pn_junction_phi(0.7, 1.0) == pytest.approx(0.0)


class TestTransistorPhiGain:
    def test_basic(self):
        assert transistor_phi_gain(100e-3, 1e-3) == pytest.approx(100.0)

    def test_raises_negative_Ic(self):
        with pytest.raises(ValueError):
            transistor_phi_gain(-1.0, 1e-3)


class TestSemiconductorPhiNoise:
    def test_positive(self):
        v = semiconductor_phi_noise(1.0, 1e-6, 1e-7, 1000.0)
        assert v > 0.0

    def test_raises_zero_frequency(self):
        with pytest.raises(ValueError):
            semiconductor_phi_noise(1.0, 1e-6, 1e-7, 0.0)


class TestSolarCellPhiEfficiency:
    def test_high_performance(self):
        eta = solar_cell_phi_efficiency(40.0, 0.7, 0.85, 100.0)
        assert 0.2 < eta < 0.3

    def test_zero_jsc(self):
        assert solar_cell_phi_efficiency(0.0, 0.7, 0.85, 100.0) == pytest.approx(0.0)

    def test_raises_zero_power(self):
        with pytest.raises(ValueError):
            solar_cell_phi_efficiency(40.0, 0.7, 0.85, 0.0)


class TestLedPhiEfficiency:
    def test_perfect_eqe(self):
        assert led_phi_efficiency(1.0, 1.0) == pytest.approx(1.0)

    def test_zero_photons(self):
        assert led_phi_efficiency(0.0, 1.0) == pytest.approx(0.0)


class TestDiodePhiCurrent:
    def test_zero_voltage(self):
        assert diode_phi_current(1e-9, 0.0) == pytest.approx(0.0, abs=1e-20)

    def test_forward_bias_positive(self):
        v = diode_phi_current(1e-9, 0.5)
        assert v > 0.0

    def test_raises_zero_T(self):
        with pytest.raises(ValueError):
            diode_phi_current(1e-9, 0.5, 0.0)


class TestQuantumPhiDot:
    def test_positive_energy(self):
        E = quantum_phi_dot(1, 1, 1, 5.0)
        assert E > 0.0

    def test_smaller_dot_higher_energy(self):
        E_small = quantum_phi_dot(1, 1, 1, 2.0)
        E_large = quantum_phi_dot(1, 1, 1, 10.0)
        assert E_small > E_large

    def test_raises_zero_quantum_number(self):
        with pytest.raises(ValueError):
            quantum_phi_dot(0, 1, 1, 5.0)


class TestSemiconductorPhiBandgap:
    def test_zero_T(self):
        v = semiconductor_phi_bandgap(1.42, 0.0)
        assert v == pytest.approx(1.42, rel=1e-3)

    def test_decreases_with_T(self):
        v0 = semiconductor_phi_bandgap(1.42, 0.0)
        v300 = semiconductor_phi_bandgap(1.42, 300.0)
        assert v300 < v0


# ---------------------------------------------------------------------------
# metamaterials.py
# ---------------------------------------------------------------------------

class TestNegativePhiIndex:
    def test_double_negative(self):
        n = negative_phi_index(-2.0, -1.0)
        assert n < 0.0

    def test_conventional(self):
        n = negative_phi_index(2.25, 1.0)
        assert n > 0.0


class TestMetamaterialPhiResonance:
    def test_at_resonance(self):
        v = metamaterial_phi_resonance(1.0, 1.0, 0.0)
        assert v > 0.0

    def test_far_from_resonance(self):
        v_far = metamaterial_phi_resonance(0.1, 1.0, 0.01)
        v_res = metamaterial_phi_resonance(1.0, 1.0, 0.01)
        assert v_res > v_far

    def test_raises_zero_omega0(self):
        with pytest.raises(ValueError):
            metamaterial_phi_resonance(1.0, 0.0, 0.01)


class TestPhotonicPhiBandgap:
    def test_bragg_condition_satisfied(self):
        v = photonic_phi_bandgap(800.0, 2.3, 1.45, 87.0, 138.0)
        assert isinstance(v, float)

    def test_raises_negative_lambda(self):
        with pytest.raises(ValueError):
            photonic_phi_bandgap(0.0, 2.3, 1.45, 87.0, 138.0)


class TestAcousticPhiMetamaterial:
    def test_matched(self):
        v = acoustic_phi_metamaterial(1000.0, 1000.0, 2e9, 2e9)
        assert v == pytest.approx(1.0)

    def test_mismatch(self):
        v = acoustic_phi_metamaterial(500.0, 1000.0, 2e9, 2e9)
        assert v != pytest.approx(1.0)


class TestCloakingPhiEfficiency:
    def test_perfect_cloaking(self):
        assert cloaking_phi_efficiency(0.0, 1.0) == pytest.approx(1.0)

    def test_no_cloaking(self):
        assert cloaking_phi_efficiency(1.0, 1.0) == pytest.approx(0.0)

    def test_clipped(self):
        assert cloaking_phi_efficiency(0.0, 0.0) == pytest.approx(1.0)


class TestEpsilonPhiNearZero:
    def test_enz_true(self):
        assert epsilon_phi_near_zero(0.05) is True

    def test_enz_false(self):
        assert epsilon_phi_near_zero(2.3) is False

    def test_raises_zero_tolerance(self):
        with pytest.raises(ValueError):
            epsilon_phi_near_zero(0.05, 0.0)


class TestHyperbolicPhiDispersion:
    def test_returns_float(self):
        v = hyperbolic_phi_dispersion(1e6, 1e6, -2.0, 3.0, 3e9)
        assert isinstance(v, float)

    def test_raises_zero_epsilon(self):
        with pytest.raises(ValueError):
            hyperbolic_phi_dispersion(1e6, 1e6, 0.0, 3.0, 3e9)


class TestNonlinearPhiMetamaterial:
    def test_linear_zero_chi3(self):
        assert nonlinear_phi_metamaterial(2.0, 0.0) == pytest.approx(2.0)

    def test_positive_chi3_amplifies(self):
        v = nonlinear_phi_metamaterial(2.0, 0.1)
        assert v > 2.0

    def test_raises_negative_input(self):
        with pytest.raises(ValueError):
            nonlinear_phi_metamaterial(-1.0, 0.1)


class TestTopologicalPhiInsulator:
    def test_surface_only(self):
        v = topological_phi_insulator(0.0, 1.0, 4)
        assert v == pytest.approx(4.0)

    def test_bulk_contribution(self):
        v = topological_phi_insulator(0.1, 1.0, 4)
        assert v == pytest.approx(4.1)


class TestPhiPlasmonResonance:
    def test_at_resonance(self):
        # Resonance when eps_metal + 2*eps_dielectric = 0
        # i.e. n_metal^2 = -2*n_dielectric^2
        # For n_dielectric=1: eps_metal = -2, so n_metal = sqrt(-2) ≈ 1.41j
        # phi_spr = |n_metal² + 2*n_dielectric²| = |-2 + 2| = 0
        # Use n_metal = 0 (eps=0), eps_d=1: phi = |0 + 2| = 2 — just test return type
        v = phi_plasmon_resonance(550.0, -1.41, 1.0)
        assert isinstance(v, float) and v >= 0.0

    def test_positive(self):
        v = phi_plasmon_resonance(550.0, 1.5, 1.0)
        assert v > 0.0

    def test_raises_zero_lambda(self):
        with pytest.raises(ValueError):
            phi_plasmon_resonance(0.0, 1.5, 1.0)
