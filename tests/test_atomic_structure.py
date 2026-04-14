# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_atomic_structure.py
===============================
Unit tests for src/atomic_structure/orbitals.py, spectroscopy.py,
and fine_structure.py.

Covers every public function (110 tests total).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.atomic_structure.orbitals import (
    hydrogen_energy_level,
    orbital_radius,
    wavefunction_amplitude,
    quantum_degeneracy,
    angular_momentum_squared,
    magnetic_quantum_states,
    spin_orbital_coupling,
    transition_energy,
    lyman_wavelength,
    balmer_wavelength,
    phi_field_at_orbital,
    selection_rule_allowed,
)
from src.atomic_structure.spectroscopy import (
    rydberg_constant_from_geometry,
    series_wavelengths,
    emission_intensity,
    absorption_cross_section,
    doppler_width,
    natural_linewidth,
    einstein_A_coefficient,
    photoionization_threshold,
    stark_shift,
    zeeman_splitting,
    phi_emission_enhancement,
    b_field_line_broadening,
)
from src.atomic_structure.fine_structure import (
    fine_structure_constant_from_kk,
    dirac_energy,
    lamb_shift_estimate,
    hyperfine_splitting,
    g_factor_anomaly,
    relativistic_correction,
    spin_orbit_j_values,
    total_angular_momentum_magnitude,
    lande_g_factor,
    kk_spin_connection,
)

_ALPHA = 1.0 / 137.0


# ===========================================================================
# TestHydrogenEnergyLevel
# ===========================================================================

class TestHydrogenEnergyLevel:

    def test_ground_state_formula(self):
        E1 = hydrogen_energy_level(1)
        assert abs(E1 - (-_ALPHA ** 2 / 2.0)) < 1e-12

    def test_n2_level(self):
        E2 = hydrogen_energy_level(2)
        assert abs(E2 - (-_ALPHA ** 2 / 8.0)) < 1e-12

    def test_energy_negative(self):
        for n in range(1, 6):
            assert hydrogen_energy_level(n) < 0.0

    def test_energy_increases_toward_zero(self):
        energies = [hydrogen_energy_level(n) for n in range(1, 6)]
        for i in range(len(energies) - 1):
            assert energies[i] < energies[i + 1]

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            hydrogen_energy_level(0)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            hydrogen_energy_level(-1)

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            hydrogen_energy_level(1, alpha_fs=0.0)

    def test_returns_float(self):
        assert isinstance(hydrogen_energy_level(1), float)


# ===========================================================================
# TestOrbitalRadius
# ===========================================================================

class TestOrbitalRadius:

    def test_n1_bohr_unit(self):
        assert abs(orbital_radius(1, a0=1.0) - 1.0) < 1e-12

    def test_n2_is_four(self):
        assert abs(orbital_radius(2, a0=1.0) - 4.0) < 1e-12

    def test_n_squared_scaling(self):
        a0 = 0.5
        for n in range(1, 5):
            assert abs(orbital_radius(n, a0=a0) - n ** 2 * a0) < 1e-12

    def test_radius_grows_with_n(self):
        radii = [orbital_radius(n) for n in range(1, 6)]
        for i in range(len(radii) - 1):
            assert radii[i] < radii[i + 1]

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            orbital_radius(0)

    def test_a0_zero_raises(self):
        with pytest.raises(ValueError):
            orbital_radius(1, a0=0.0)

    def test_returns_float(self):
        assert isinstance(orbital_radius(2), float)


# ===========================================================================
# TestWavefunctionAmplitude
# ===========================================================================

class TestWavefunctionAmplitude:

    def test_output_shape(self):
        r = np.linspace(0.0, 10.0, 50)
        psi2 = wavefunction_amplitude(r, n=1)
        assert psi2.shape == (50,)

    def test_non_negative(self):
        r = np.linspace(0.0, 20.0, 100)
        assert np.all(wavefunction_amplitude(r, n=1) >= 0.0)

    def test_decays_with_r(self):
        r = np.linspace(0.1, 20.0, 200)
        psi2 = wavefunction_amplitude(r, n=1)
        assert psi2[0] > psi2[-1]

    def test_higher_n_slower_decay(self):
        r_val = np.array([5.0])
        psi2_n1 = wavefunction_amplitude(r_val, n=1)[0]
        psi2_n3 = wavefunction_amplitude(r_val, n=3)[0]
        assert psi2_n3 > psi2_n1

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            wavefunction_amplitude(np.array([1.0]), n=0)

    def test_a0_zero_raises(self):
        with pytest.raises(ValueError):
            wavefunction_amplitude(np.array([1.0]), n=1, a0=0.0)


# ===========================================================================
# TestQuantumDegeneracy
# ===========================================================================

class TestQuantumDegeneracy:

    def test_n1_is_two(self):
        assert quantum_degeneracy(1) == 2

    def test_n2_is_eight(self):
        assert quantum_degeneracy(2) == 8

    def test_n3_is_eighteen(self):
        assert quantum_degeneracy(3) == 18

    def test_n4_is_thirtytwo(self):
        assert quantum_degeneracy(4) == 32

    def test_formula_two_n_squared(self):
        for n in range(1, 8):
            assert quantum_degeneracy(n) == 2 * n ** 2

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            quantum_degeneracy(0)

    def test_returns_int(self):
        assert isinstance(quantum_degeneracy(1), int)


# ===========================================================================
# TestAngularMomentumSquared
# ===========================================================================

class TestAngularMomentumSquared:

    def test_l0_is_zero(self):
        assert angular_momentum_squared(0) == 0.0

    def test_l1_is_two(self):
        assert abs(angular_momentum_squared(1) - 2.0) < 1e-12

    def test_l2_is_six(self):
        assert abs(angular_momentum_squared(2) - 6.0) < 1e-12

    def test_formula_l_lp1(self):
        for l in range(0, 5):
            assert abs(angular_momentum_squared(l) - l * (l + 1)) < 1e-12

    def test_negative_l_raises(self):
        with pytest.raises(ValueError):
            angular_momentum_squared(-1)


# ===========================================================================
# TestMagneticQuantumStates
# ===========================================================================

class TestMagneticQuantumStates:

    def test_l0_returns_zero_only(self):
        assert magnetic_quantum_states(0) == [0]

    def test_l1_returns_minus1_0_plus1(self):
        assert magnetic_quantum_states(1) == [-1, 0, 1]

    def test_l2_has_five_states(self):
        states = magnetic_quantum_states(2)
        assert len(states) == 5
        assert states == [-2, -1, 0, 1, 2]

    def test_count_is_two_l_plus_one(self):
        for l in range(0, 5):
            assert len(magnetic_quantum_states(l)) == 2 * l + 1

    def test_negative_l_raises(self):
        with pytest.raises(ValueError):
            magnetic_quantum_states(-1)


# ===========================================================================
# TestSpinOrbitalCoupling
# ===========================================================================

class TestSpinOrbitalCoupling:

    def test_positive_result(self):
        dE = spin_orbital_coupling(n=2, l=1, j=1.5, Z=1)
        assert dE > 0.0

    def test_scales_with_Z4(self):
        dE1 = spin_orbital_coupling(n=2, l=1, j=1.5, Z=1)
        dE2 = spin_orbital_coupling(n=2, l=1, j=1.5, Z=2)
        assert abs(dE2 / dE1 - 16.0) < 1e-8

    def test_decreases_with_n(self):
        dE2 = spin_orbital_coupling(n=2, l=1, j=1.5, Z=1)
        dE3 = spin_orbital_coupling(n=3, l=1, j=1.5, Z=1)
        assert dE2 > dE3

    def test_l_zero_raises(self):
        with pytest.raises(ValueError):
            spin_orbital_coupling(n=2, l=0, j=0.5, Z=1)

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            spin_orbital_coupling(n=0, l=1, j=1.5, Z=1)

    def test_Z_zero_raises(self):
        with pytest.raises(ValueError):
            spin_orbital_coupling(n=2, l=1, j=1.5, Z=0)


# ===========================================================================
# TestTransitionEnergy
# ===========================================================================

class TestTransitionEnergy:

    def test_emission_is_negative_for_ni_gt_nf(self):
        # ΔE = E_nf − E_ni; E_1 < E_2 so result is negative for downward transition
        assert transition_energy(2, 1) < 0.0

    def test_absorption_is_positive_for_ni_lt_nf(self):
        # Upward transition: E_nf > E_ni → positive ΔE
        assert transition_energy(1, 2) > 0.0

    def test_same_level_zero(self):
        assert abs(transition_energy(3, 3)) < 1e-15

    def test_antisymmetric(self):
        dE_em = transition_energy(3, 1)
        dE_ab = transition_energy(1, 3)
        assert abs(dE_em + dE_ab) < 1e-14

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            transition_energy(0, 1)

    def test_nf_zero_raises(self):
        with pytest.raises(ValueError):
            transition_energy(2, 0)


# ===========================================================================
# TestLymanWavelength
# ===========================================================================

class TestLymanWavelength:

    def test_n2_positive(self):
        assert lyman_wavelength(2) > 0.0

    def test_n2_value(self):
        expected = 1.0 / (1.0 - 1.0 / 4.0)
        assert abs(lyman_wavelength(2) - expected) < 1e-12

    def test_wavelength_increases_with_n(self):
        lam2 = lyman_wavelength(2)
        lam3 = lyman_wavelength(3)
        lam_inf = lyman_wavelength(100)
        assert lam2 > lam3 > lam_inf

    def test_series_limit(self):
        lam = lyman_wavelength(1000)
        assert abs(lam - 1.0) < 0.01

    def test_n1_raises(self):
        with pytest.raises(ValueError):
            lyman_wavelength(1)


# ===========================================================================
# TestBalmerWavelength
# ===========================================================================

class TestBalmerWavelength:

    def test_n3_positive(self):
        assert balmer_wavelength(3) > 0.0

    def test_n3_value(self):
        expected = 1.0 / (0.25 - 1.0 / 9.0)
        assert abs(balmer_wavelength(3) - expected) < 1e-12

    def test_wavelength_increases_with_n(self):
        lam3 = balmer_wavelength(3)
        lam4 = balmer_wavelength(4)
        assert lam3 > lam4

    def test_n2_raises(self):
        with pytest.raises(ValueError):
            balmer_wavelength(2)

    def test_returns_float(self):
        assert isinstance(balmer_wavelength(3), float)


# ===========================================================================
# TestPhiFieldAtOrbital
# ===========================================================================

class TestPhiFieldAtOrbital:

    def test_n1_returns_phi0(self):
        assert abs(phi_field_at_orbital(1, phi0=2.0) - 2.0) < 1e-12

    def test_n2_returns_half_phi0(self):
        assert abs(phi_field_at_orbital(2, phi0=2.0) - 1.0) < 1e-12

    def test_decreases_with_n(self):
        vals = [phi_field_at_orbital(n) for n in range(1, 6)]
        for i in range(len(vals) - 1):
            assert vals[i] > vals[i + 1]

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            phi_field_at_orbital(0)

    def test_phi0_zero_raises(self):
        with pytest.raises(ValueError):
            phi_field_at_orbital(1, phi0=0.0)


# ===========================================================================
# TestSelectionRuleAllowed
# ===========================================================================

class TestSelectionRuleAllowed:

    def test_delta_l_plus1_allowed(self):
        assert selection_rule_allowed(0, 1, 0, 0) is True

    def test_delta_l_minus1_allowed(self):
        assert selection_rule_allowed(1, 0, 0, 0) is True

    def test_delta_l_zero_forbidden(self):
        assert selection_rule_allowed(1, 1, 0, 0) is False

    def test_delta_l_two_forbidden(self):
        assert selection_rule_allowed(0, 2, 0, 0) is False

    def test_delta_m_zero_allowed(self):
        assert selection_rule_allowed(0, 1, 0, 0) is True

    def test_delta_m_plus1_allowed(self):
        assert selection_rule_allowed(0, 1, 0, 1) is True

    def test_delta_m_minus1_allowed(self):
        assert selection_rule_allowed(1, 0, 1, 0) is True

    def test_delta_m_two_forbidden(self):
        assert selection_rule_allowed(0, 1, 0, 2) is False

    def test_returns_bool(self):
        result = selection_rule_allowed(0, 1, 0, 0)
        assert isinstance(result, bool)


# ===========================================================================
# TestRydbergConstantFromGeometry
# ===========================================================================

class TestRydbergConstantFromGeometry:

    def test_unit_phi0_gives_alpha_sq_over_2(self):
        R = rydberg_constant_from_geometry(phi0_eff=1.0, alpha_fs=_ALPHA)
        assert abs(R - _ALPHA ** 2 / 2.0) < 1e-15

    def test_positive(self):
        assert rydberg_constant_from_geometry(1.0) > 0.0

    def test_scales_with_phi0_inverse_sq(self):
        R1 = rydberg_constant_from_geometry(1.0)
        R2 = rydberg_constant_from_geometry(2.0)
        assert abs(R1 / R2 - 4.0) < 1e-10

    def test_phi0_zero_raises(self):
        with pytest.raises(ValueError):
            rydberg_constant_from_geometry(0.0)

    def test_alpha_zero_raises(self):
        with pytest.raises(ValueError):
            rydberg_constant_from_geometry(1.0, alpha_fs=0.0)


# ===========================================================================
# TestSeriesWavelengths
# ===========================================================================

class TestSeriesWavelengths:

    def test_lyman_shape(self):
        lams = series_wavelengths(1, range(2, 7))
        assert lams.shape == (5,)

    def test_lyman_all_positive(self):
        lams = series_wavelengths(1, range(2, 7))
        assert np.all(lams > 0.0)

    def test_balmer_shape(self):
        lams = series_wavelengths(2, range(3, 8))
        assert lams.shape == (5,)

    def test_wavelengths_decrease_with_upper_n(self):
        lams = series_wavelengths(1, range(2, 8))
        for i in range(len(lams) - 1):
            assert lams[i] > lams[i + 1]

    def test_n_equal_n_final_raises(self):
        with pytest.raises(ValueError):
            series_wavelengths(2, [2])

    def test_n_final_zero_raises(self):
        with pytest.raises(ValueError):
            series_wavelengths(0, [1])


# ===========================================================================
# TestEmissionIntensity
# ===========================================================================

class TestEmissionIntensity:

    def test_positive(self):
        assert emission_intensity(2, 1, T=1.0) > 0.0

    def test_higher_T_larger_intensity(self):
        I_low = emission_intensity(2, 1, T=0.01)
        I_high = emission_intensity(2, 1, T=1.0)
        assert I_high > I_low

    def test_T_zero_raises(self):
        with pytest.raises(ValueError):
            emission_intensity(2, 1, T=0.0)

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            emission_intensity(0, 1, T=1.0)

    def test_returns_float(self):
        assert isinstance(emission_intensity(3, 1, T=1.0), float)


# ===========================================================================
# TestAbsorptionCrossSection
# ===========================================================================

class TestAbsorptionCrossSection:

    def test_positive(self):
        assert absorption_cross_section(1, 2) > 0.0

    def test_higher_n_larger_sigma(self):
        sigma12 = absorption_cross_section(1, 2)
        sigma13 = absorption_cross_section(1, 3)
        assert sigma13 > sigma12

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            absorption_cross_section(0, 2)

    def test_alpha_zero_raises(self):
        with pytest.raises(ValueError):
            absorption_cross_section(1, 2, alpha_fs=0.0)

    def test_returns_float(self):
        assert isinstance(absorption_cross_section(1, 2), float)


# ===========================================================================
# TestDopplerWidth
# ===========================================================================

class TestDopplerWidth:

    def test_positive(self):
        assert doppler_width(T=1.0, m_atom=1.0, omega_0=1.0) > 0.0

    def test_scales_with_omega_0(self):
        dw1 = doppler_width(1.0, 1.0, 1.0)
        dw2 = doppler_width(1.0, 1.0, 2.0)
        assert abs(dw2 / dw1 - 2.0) < 1e-10

    def test_scales_with_sqrt_T(self):
        dw1 = doppler_width(1.0, 1.0, 1.0)
        dw4 = doppler_width(4.0, 1.0, 1.0)
        assert abs(dw4 / dw1 - 2.0) < 1e-10

    def test_T_zero_raises(self):
        with pytest.raises(ValueError):
            doppler_width(0.0, 1.0, 1.0)

    def test_m_zero_raises(self):
        with pytest.raises(ValueError):
            doppler_width(1.0, 0.0, 1.0)

    def test_omega_zero_raises(self):
        with pytest.raises(ValueError):
            doppler_width(1.0, 1.0, 0.0)


# ===========================================================================
# TestNaturalLinewidth
# ===========================================================================

class TestNaturalLinewidth:

    def test_positive(self):
        assert natural_linewidth(2, 1) > 0.0

    def test_increases_with_energy_gap(self):
        g21 = natural_linewidth(2, 1)
        g31 = natural_linewidth(3, 1)
        assert g31 > g21

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            natural_linewidth(0, 1)

    def test_alpha_zero_raises(self):
        with pytest.raises(ValueError):
            natural_linewidth(2, 1, alpha_fs=0.0)

    def test_returns_float(self):
        assert isinstance(natural_linewidth(2, 1), float)


# ===========================================================================
# TestEinsteinACoefficient
# ===========================================================================

class TestEinsteinACoefficient:

    def test_positive(self):
        assert einstein_A_coefficient(2, 1) > 0.0

    def test_proportional_to_alpha_cubed_dE_cubed(self):
        # A = alpha^3 * |dE|^3, and |dE| itself scales as alpha^2, so A ~ alpha^9
        a1 = 1.0 / 137.0
        a2 = 2.0 / 137.0
        A1 = einstein_A_coefficient(2, 1, alpha_fs=a1)
        A2 = einstein_A_coefficient(2, 1, alpha_fs=a2)
        assert abs(A2 / A1 - 2.0 ** 9) < 1e-3

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            einstein_A_coefficient(0, 1)

    def test_nf_zero_raises(self):
        with pytest.raises(ValueError):
            einstein_A_coefficient(2, 0)

    def test_returns_float(self):
        assert isinstance(einstein_A_coefficient(2, 1), float)


# ===========================================================================
# TestPhotoionizationThreshold
# ===========================================================================

class TestPhotoionizationThreshold:

    def test_positive(self):
        assert photoionization_threshold(1) > 0.0

    def test_n1_value(self):
        expected = _ALPHA ** 2 / 2.0
        assert abs(photoionization_threshold(1) - expected) < 1e-15

    def test_decreases_with_n(self):
        E1 = photoionization_threshold(1)
        E2 = photoionization_threshold(2)
        assert E1 > E2

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            photoionization_threshold(0)

    def test_alpha_zero_raises(self):
        with pytest.raises(ValueError):
            photoionization_threshold(1, alpha_fs=0.0)


# ===========================================================================
# TestStarkShift
# ===========================================================================

class TestStarkShift:

    def test_zero_field_zero_shift(self):
        assert abs(stark_shift(0.0, n=2)) < 1e-15

    def test_nonzero_field_negative(self):
        assert stark_shift(1.0, n=2) < 0.0

    def test_scales_n4(self):
        dE1 = stark_shift(1.0, n=1)
        dE2 = stark_shift(1.0, n=2)
        assert abs(dE2 / dE1 - 16.0) < 1e-10

    def test_scales_E_field_squared(self):
        dE1 = stark_shift(1.0, n=2)
        dE2 = stark_shift(2.0, n=2)
        assert abs(dE2 / dE1 - 4.0) < 1e-10

    def test_negative_field_raises(self):
        with pytest.raises(ValueError):
            stark_shift(-1.0, n=2)

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            stark_shift(1.0, n=0)


# ===========================================================================
# TestZeemanSplitting
# ===========================================================================

class TestZeemanSplitting:

    def test_m_zero_gives_zero(self):
        assert abs(zeeman_splitting(1.0, m_l=0)) < 1e-15

    def test_positive_m_positive_split(self):
        assert zeeman_splitting(1.0, m_l=1) > 0.0

    def test_negative_m_negative_split(self):
        assert zeeman_splitting(1.0, m_l=-1) < 0.0

    def test_scales_with_B(self):
        dE1 = zeeman_splitting(1.0, m_l=1)
        dE2 = zeeman_splitting(2.0, m_l=1)
        assert abs(dE2 / dE1 - 2.0) < 1e-12

    def test_negative_B_raises(self):
        with pytest.raises(ValueError):
            zeeman_splitting(-1.0, m_l=1)

    def test_g_factor_scaling(self):
        dE1 = zeeman_splitting(1.0, m_l=1, g_L=1.0)
        dE2 = zeeman_splitting(1.0, m_l=1, g_L=2.0)
        assert abs(dE2 / dE1 - 2.0) < 1e-12


# ===========================================================================
# TestPhiEmissionEnhancement
# ===========================================================================

class TestPhiEmissionEnhancement:

    def test_equal_phi_gives_one(self):
        assert abs(phi_emission_enhancement(1.0, phi_ref=1.0) - 1.0) < 1e-12

    def test_double_phi_gives_four(self):
        assert abs(phi_emission_enhancement(2.0, phi_ref=1.0) - 4.0) < 1e-12

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            phi_emission_enhancement(0.0)

    def test_phi_ref_zero_raises(self):
        with pytest.raises(ValueError):
            phi_emission_enhancement(1.0, phi_ref=0.0)

    def test_returns_float(self):
        assert isinstance(phi_emission_enhancement(1.5), float)


# ===========================================================================
# TestBFieldLineBroadening
# ===========================================================================

class TestBFieldLineBroadening:

    def test_zero_field_zero_broadening(self):
        assert abs(b_field_line_broadening(0.0)) < 1e-15

    def test_positive_field_positive_broadening(self):
        assert b_field_line_broadening(1.0) > 0.0

    def test_linear_scaling(self):
        dw1 = b_field_line_broadening(1.0)
        dw2 = b_field_line_broadening(3.0)
        assert abs(dw2 / dw1 - 3.0) < 1e-12

    def test_negative_B_raises(self):
        with pytest.raises(ValueError):
            b_field_line_broadening(-0.1)

    def test_returns_float(self):
        assert isinstance(b_field_line_broadening(0.5), float)


# ===========================================================================
# TestFineStructureConstantFromKK
# ===========================================================================

class TestFineStructureConstantFromKK:

    def test_positive(self):
        assert fine_structure_constant_from_kk(k_cs=1.0) > 0.0

    def test_formula(self):
        # alpha = k_cs / (2π * n_w²); for alpha=1/137, n_w=1: k_cs = 2π/137
        k = 2.0 * np.pi / 137.0
        alpha = fine_structure_constant_from_kk(k_cs=k, n_w=1)
        assert abs(alpha - 1.0 / 137.0) < 1e-10

    def test_increases_with_k_cs(self):
        a1 = fine_structure_constant_from_kk(1.0, n_w=5)
        a2 = fine_structure_constant_from_kk(2.0, n_w=5)
        assert a2 > a1

    def test_k_cs_zero_raises(self):
        with pytest.raises(ValueError):
            fine_structure_constant_from_kk(0.0)

    def test_n_w_zero_raises(self):
        with pytest.raises(ValueError):
            fine_structure_constant_from_kk(1.0, n_w=0)


# ===========================================================================
# TestDiracEnergy
# ===========================================================================

class TestDiracEnergy:

    def test_negative_bound_state(self):
        E = dirac_energy(n=1, j=0.5, Z=1, alpha_fs=_ALPHA)
        assert E < 0.0

    def test_higher_n_less_negative(self):
        E1 = dirac_energy(n=1, j=0.5, Z=1, alpha_fs=_ALPHA)
        E2 = dirac_energy(n=2, j=0.5, Z=1, alpha_fs=_ALPHA)
        assert E1 < E2

    def test_returns_float(self):
        assert isinstance(dirac_energy(1, 0.5), float)

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            dirac_energy(0, 0.5)

    def test_Z_zero_raises(self):
        with pytest.raises(ValueError):
            dirac_energy(1, 0.5, Z=0)


# ===========================================================================
# TestLambShiftEstimate
# ===========================================================================

class TestLambShiftEstimate:

    def test_positive_for_s_state(self):
        assert lamb_shift_estimate(1, 0) > 0.0

    def test_s_state_larger_than_p_state(self):
        lamb_s = lamb_shift_estimate(2, 0)
        lamb_p = lamb_shift_estimate(2, 1)
        assert lamb_s > lamb_p

    def test_decreases_with_n(self):
        l1 = lamb_shift_estimate(1, 0)
        l2 = lamb_shift_estimate(2, 0)
        assert l1 > l2

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            lamb_shift_estimate(0, 0)

    def test_l_negative_raises(self):
        with pytest.raises(ValueError):
            lamb_shift_estimate(1, -1)


# ===========================================================================
# TestHyperfineSplitting
# ===========================================================================

class TestHyperfineSplitting:

    def test_hydrogen_ground_state(self):
        # I=0.5, J=0.5: F=1 → ΔE = A_hf/2*[2-0.75-0.75] = A_hf/2*0.5
        dE = hyperfine_splitting(I=0.5, J=0.5, A_hf=1.0)
        assert abs(dE - 0.25) < 1e-12

    def test_scales_with_A_hf(self):
        dE1 = hyperfine_splitting(0.5, 0.5, A_hf=1.0)
        dE2 = hyperfine_splitting(0.5, 0.5, A_hf=2.0)
        assert abs(dE2 / dE1 - 2.0) < 1e-12

    def test_I_negative_raises(self):
        with pytest.raises(ValueError):
            hyperfine_splitting(-0.5, 0.5, 1.0)

    def test_J_negative_raises(self):
        with pytest.raises(ValueError):
            hyperfine_splitting(0.5, -0.5, 1.0)

    def test_returns_float(self):
        assert isinstance(hyperfine_splitting(0.5, 0.5, 1.0), float)


# ===========================================================================
# TestGFactorAnomaly
# ===========================================================================

class TestGFactorAnomaly:

    def test_value_close_to_alpha_over_pi(self):
        g = g_factor_anomaly(_ALPHA)
        assert abs(g - _ALPHA / np.pi) < 1e-15

    def test_positive(self):
        assert g_factor_anomaly() > 0.0

    def test_small(self):
        assert g_factor_anomaly() < 0.01

    def test_alpha_zero_raises(self):
        with pytest.raises(ValueError):
            g_factor_anomaly(0.0)


# ===========================================================================
# TestRelativisticCorrection
# ===========================================================================

class TestRelativisticCorrection:

    def test_negative(self):
        assert relativistic_correction(1, 1) < 0.0

    def test_larger_Z_more_negative(self):
        dE1 = relativistic_correction(1, 1)
        dE2 = relativistic_correction(1, 2)
        assert dE2 < dE1

    def test_higher_n_less_correction(self):
        dE1 = relativistic_correction(1, 1)
        dE2 = relativistic_correction(2, 1)
        assert dE1 < dE2

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            relativistic_correction(0, 1)

    def test_Z_zero_raises(self):
        with pytest.raises(ValueError):
            relativistic_correction(1, 0)


# ===========================================================================
# TestSpinOrbitJValues
# ===========================================================================

class TestSpinOrbitJValues:

    def test_l0_returns_half(self):
        assert spin_orbit_j_values(0) == [0.5]

    def test_l1_returns_half_and_threehalves(self):
        assert spin_orbit_j_values(1) == [0.5, 1.5]

    def test_l2_returns_threehalves_fivehalves(self):
        assert spin_orbit_j_values(2) == [1.5, 2.5]

    def test_two_values_for_l_ge_1(self):
        for l in range(1, 5):
            assert len(spin_orbit_j_values(l)) == 2

    def test_negative_l_raises(self):
        with pytest.raises(ValueError):
            spin_orbit_j_values(-1)


# ===========================================================================
# TestTotalAngularMomentumMagnitude
# ===========================================================================

class TestTotalAngularMomentumMagnitude:

    def test_j0_is_zero(self):
        assert abs(total_angular_momentum_magnitude(0.0)) < 1e-12

    def test_j_half(self):
        expected = np.sqrt(0.5 * 1.5)
        assert abs(total_angular_momentum_magnitude(0.5) - expected) < 1e-12

    def test_j1(self):
        expected = np.sqrt(2.0)
        assert abs(total_angular_momentum_magnitude(1.0) - expected) < 1e-12

    def test_negative_j_raises(self):
        with pytest.raises(ValueError):
            total_angular_momentum_magnitude(-0.5)

    def test_returns_float(self):
        assert isinstance(total_angular_momentum_magnitude(1.0), float)


# ===========================================================================
# TestLandeGFactor
# ===========================================================================

class TestLandeGFactor:

    def test_pure_spin_l0_gives_two(self):
        g = lande_g_factor(j=0.5, l=0, s=0.5)
        assert abs(g - 2.0) < 1e-12

    def test_pure_orbital_s0_gives_one(self):
        g = lande_g_factor(j=1.0, l=1, s=0.0)
        assert abs(g - 1.0) < 1e-12

    def test_j_zero_raises(self):
        with pytest.raises(ValueError):
            lande_g_factor(j=0.0, l=0)

    def test_l_negative_raises(self):
        with pytest.raises(ValueError):
            lande_g_factor(j=0.5, l=-1)

    def test_returns_float(self):
        assert isinstance(lande_g_factor(0.5, 0), float)


# ===========================================================================
# TestKKSpinConnection
# ===========================================================================

class TestKKSpinConnection:

    def test_positive(self):
        assert kk_spin_connection(n_w=1, phi0=1.0) > 0.0

    def test_formula(self):
        omega = kk_spin_connection(n_w=2, phi0=np.pi)
        expected = np.pi / (2 * 2.0 * np.pi)
        assert abs(omega - expected) < 1e-12

    def test_decreases_with_n_w(self):
        w1 = kk_spin_connection(1, 1.0)
        w2 = kk_spin_connection(2, 1.0)
        assert w1 > w2

    def test_n_w_zero_raises(self):
        with pytest.raises(ValueError):
            kk_spin_connection(0, 1.0)

    def test_phi0_zero_raises(self):
        with pytest.raises(ValueError):
            kk_spin_connection(1, 0.0)
