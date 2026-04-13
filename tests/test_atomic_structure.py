"""
tests/test_atomic_structure.py
================================
Unit tests for src/core/atomic_structure.py  — Pillar 14.

Covers every public function:
  quark_content, constituent_quark_mass, hadron_mass,
  qcd_flux_tube_energy, bohr_radius_kk, rydberg_energy,
  hydrogen_energy_level, hydrogen_wavelength,
  hydrogen_1s_radial_density, atomic_orbital_radius,
  nuclear_binding_energy, nuclear_binding_per_nucleon
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src.core.atomic_structure import (
    HADRON_CATALOG,
    quark_content,
    constituent_quark_mass,
    hadron_mass,
    qcd_flux_tube_energy,
    bohr_radius_kk,
    rydberg_energy,
    hydrogen_energy_level,
    hydrogen_wavelength,
    hydrogen_1s_radial_density,
    atomic_orbital_radius,
    nuclear_binding_energy,
    nuclear_binding_per_nucleon,
)


# ===========================================================================
# TestHadronCatalog
# ===========================================================================

class TestHadronCatalog:
    """Sanity checks on the module-level HADRON_CATALOG constant."""

    def test_proton_present(self):
        assert "proton" in HADRON_CATALOG

    def test_neutron_present(self):
        assert "neutron" in HADRON_CATALOG

    def test_proton_has_two_up(self):
        assert HADRON_CATALOG["proton"]["up"] == 2

    def test_proton_has_one_down(self):
        assert HADRON_CATALOG["proton"]["down"] == 1

    def test_neutron_has_one_up(self):
        assert HADRON_CATALOG["neutron"]["up"] == 1

    def test_neutron_has_two_down(self):
        assert HADRON_CATALOG["neutron"]["down"] == 2


# ===========================================================================
# TestQuarkContent
# ===========================================================================

class TestQuarkContent:
    """Tests for quark_content."""

    def test_proton_content(self):
        content = quark_content("proton")
        assert content == {"up": 2, "down": 1}

    def test_neutron_content(self):
        content = quark_content("neutron")
        assert content == {"up": 1, "down": 2}

    def test_returns_copy(self):
        c1 = quark_content("proton")
        c2 = quark_content("proton")
        c1["up"] = 99
        assert c2["up"] == 2

    def test_total_quarks_proton(self):
        assert sum(quark_content("proton").values()) == 3

    def test_total_quarks_neutron(self):
        assert sum(quark_content("neutron").values()) == 3

    def test_unknown_hadron_raises(self):
        with pytest.raises(ValueError):
            quark_content("pion")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            quark_content("")


# ===========================================================================
# TestConstituentQuarkMass
# ===========================================================================

class TestConstituentQuarkMass:
    """Tests for constituent_quark_mass."""

    def test_positive_for_up(self):
        assert constituent_quark_mass("up") > 0.0

    def test_positive_for_down(self):
        assert constituent_quark_mass("down") > 0.0

    def test_gen1_quarks_equal_phi_eff(self):
        m_up = constituent_quark_mass("up")
        m_down = constituent_quark_mass("down")
        assert abs(m_up - m_down) < 1e-30

    def test_gen2_heavier_than_gen1(self):
        m_u = constituent_quark_mass("up")
        m_s = constituent_quark_mass("strange")
        assert m_s > m_u

    def test_gen3_heavier_than_gen2(self):
        m_s = constituent_quark_mass("strange")
        m_b = constituent_quark_mass("bottom")
        assert m_b > m_s

    def test_scales_inversely_with_phi(self):
        m1 = constituent_quark_mass("up", phi_mean=1.0)
        m2 = constituent_quark_mass("up", phi_mean=2.0)
        assert abs(m1 / m2 - 2.0) < 1e-10

    def test_scales_linearly_with_lam(self):
        m1 = constituent_quark_mass("up", phi_mean=1.0, lam=1.0)
        m2 = constituent_quark_mass("up", phi_mean=1.0, lam=3.0)
        assert abs(m2 / m1 - 3.0) < 1e-10

    def test_scales_linearly_with_n_w(self):
        m1 = constituent_quark_mass("up", phi_mean=1.0, n_w=5)
        m2 = constituent_quark_mass("up", phi_mean=1.0, n_w=10)
        assert abs(m2 / m1 - 2.0) < 1e-10

    def test_n_w_zero_gives_zero(self):
        m = constituent_quark_mass("up", phi_mean=1.0, n_w=0)
        assert m == 0.0

    def test_unknown_flavor_raises(self):
        with pytest.raises(ValueError):
            constituent_quark_mass("gluon")

    def test_nonpositive_phi_raises(self):
        with pytest.raises(ValueError):
            constituent_quark_mass("up", phi_mean=0.0)

    def test_nonpositive_lam_raises(self):
        with pytest.raises(ValueError):
            constituent_quark_mass("up", phi_mean=1.0, lam=0.0)

    def test_negative_n_w_raises(self):
        with pytest.raises(ValueError):
            constituent_quark_mass("up", phi_mean=1.0, n_w=-1)


# ===========================================================================
# TestHadronMass
# ===========================================================================

class TestHadronMass:
    """Tests for hadron_mass."""

    def test_zero_binding_returns_quark_sum(self):
        m = hadron_mass([2.2, 2.2, 4.7], binding_energy_mev=0.0)
        assert abs(m - 9.1) < 1e-10

    def test_positive_binding_increases_mass(self):
        m = hadron_mass([2.2, 2.2, 4.7], binding_energy_mev=929.0)
        assert abs(m - 938.1) < 1e-10

    def test_single_quark_no_binding(self):
        assert abs(hadron_mass([100.0]) - 100.0) < 1e-10

    def test_zero_quarks_no_binding(self):
        assert hadron_mass([]) == 0.0

    def test_negative_quark_mass_raises(self):
        with pytest.raises(ValueError):
            hadron_mass([-1.0, 2.0])

    def test_negative_binding_raises(self):
        with pytest.raises(ValueError):
            hadron_mass([2.0], binding_energy_mev=-1.0)

    def test_scales_with_binding(self):
        m1 = hadron_mass([10.0], binding_energy_mev=100.0)
        m2 = hadron_mass([10.0], binding_energy_mev=200.0)
        assert abs(m2 - m1 - 100.0) < 1e-10


# ===========================================================================
# TestQcdFluxTubeEnergy
# ===========================================================================

class TestQcdFluxTubeEnergy:
    """Tests for qcd_flux_tube_energy."""

    def test_positive_result(self):
        assert qcd_flux_tube_energy(0.85) > 0.0

    def test_scales_with_r(self):
        e1 = qcd_flux_tube_energy(1.0)
        e2 = qcd_flux_tube_energy(2.0)
        assert abs(e2 / e1 - 2.0) < 1e-10

    def test_scales_with_sigma(self):
        e1 = qcd_flux_tube_energy(1.0, sigma_mev_per_fm=1000.0)
        e2 = qcd_flux_tube_energy(1.0, sigma_mev_per_fm=2000.0)
        assert abs(e2 / e1 - 2.0) < 1e-10

    def test_scales_with_n_tubes(self):
        e1 = qcd_flux_tube_energy(1.0, n_tubes=3)
        e2 = qcd_flux_tube_energy(1.0, n_tubes=6)
        assert abs(e2 / e1 - 2.0) < 1e-10

    def test_formula_value(self):
        e = qcd_flux_tube_energy(r_hadron_fm=1.0, sigma_mev_per_fm=1000.0, n_tubes=3)
        assert abs(e - 3000.0) < 1e-10

    def test_nonpositive_r_raises(self):
        with pytest.raises(ValueError):
            qcd_flux_tube_energy(0.0)

    def test_nonpositive_sigma_raises(self):
        with pytest.raises(ValueError):
            qcd_flux_tube_energy(1.0, sigma_mev_per_fm=0.0)

    def test_n_tubes_zero_raises(self):
        with pytest.raises(ValueError):
            qcd_flux_tube_energy(1.0, n_tubes=0)


# ===========================================================================
# TestBohrRadiusKK
# ===========================================================================

class TestBohrRadiusKK:
    """Tests for bohr_radius_kk."""

    def test_positive(self):
        assert bohr_radius_kk() > 0.0

    def test_physical_value_in_planck_lengths(self):
        # a0 / l_Pl = 5.29e-11 m / 1.616e-35 m ≈ 3.27e24
        a0 = bohr_radius_kk()
        assert 3.0e24 < a0 < 3.6e24

    def test_scales_with_phi_mean(self):
        a1 = bohr_radius_kk(phi_mean=1.0)
        a2 = bohr_radius_kk(phi_mean=2.0)
        assert abs(a2 / a1 - 2.0) < 1e-10

    def test_inverse_in_m_electron(self):
        a1 = bohr_radius_kk(m_electron_planck=1e-22)
        a2 = bohr_radius_kk(m_electron_planck=2e-22)
        assert abs(a1 / a2 - 2.0) < 1e-10

    def test_inverse_in_alpha(self):
        a1 = bohr_radius_kk(alpha=1e-2)
        a2 = bohr_radius_kk(alpha=2e-2)
        assert abs(a1 / a2 - 2.0) < 1e-10

    def test_formula_direct(self):
        phi = 0.5
        me = 1e-22
        al = 1e-2
        expected = phi / (me * al)
        assert abs(bohr_radius_kk(phi, me, al) - expected) < 1e-30

    def test_nonpositive_phi_raises(self):
        with pytest.raises(ValueError):
            bohr_radius_kk(phi_mean=0.0)

    def test_nonpositive_me_raises(self):
        with pytest.raises(ValueError):
            bohr_radius_kk(m_electron_planck=0.0)

    def test_nonpositive_alpha_raises(self):
        with pytest.raises(ValueError):
            bohr_radius_kk(alpha=0.0)


# ===========================================================================
# TestRydbergEnergy
# ===========================================================================

class TestRydbergEnergy:
    """Tests for rydberg_energy."""

    def test_positive(self):
        assert rydberg_energy() > 0.0

    def test_physical_value_in_planck_units(self):
        # E1 = m_e α²/2 ≈ 13.6 eV / (1.221e28 eV) ≈ 1.11e-27 E_Pl
        E1 = rydberg_energy()
        assert 1.0e-27 < E1 < 1.2e-27

    def test_scales_quadratic_with_alpha(self):
        e1 = rydberg_energy(alpha=1e-2)
        e2 = rydberg_energy(alpha=2e-2)
        assert abs(e2 / e1 - 4.0) < 1e-10

    def test_scales_linear_with_me(self):
        e1 = rydberg_energy(m_electron_planck=1e-23)
        e2 = rydberg_energy(m_electron_planck=2e-23)
        assert abs(e2 / e1 - 2.0) < 1e-10

    def test_nonpositive_me_raises(self):
        with pytest.raises(ValueError):
            rydberg_energy(m_electron_planck=0.0)

    def test_nonpositive_alpha_raises(self):
        with pytest.raises(ValueError):
            rydberg_energy(alpha=0.0)


# ===========================================================================
# TestHydrogenEnergyLevel
# ===========================================================================

class TestHydrogenEnergyLevel:
    """Tests for hydrogen_energy_level."""

    def test_ground_state_negative(self):
        assert hydrogen_energy_level(1) < 0.0

    def test_excited_states_less_negative(self):
        E1 = hydrogen_energy_level(1)
        E2 = hydrogen_energy_level(2)
        assert E2 > E1

    def test_n2_equals_quarter_n1(self):
        E1 = hydrogen_energy_level(1, E1=1.0)
        E2 = hydrogen_energy_level(2, E1=1.0)
        assert abs(E2 / E1 - 0.25) < 1e-10

    def test_n_infinite_limit(self):
        E100 = hydrogen_energy_level(100, E1=1.0)
        assert abs(E100) < 1e-3

    def test_formula_value_explicit(self):
        E = hydrogen_energy_level(3, E1=9.0)
        assert abs(E - (-1.0)) < 1e-10

    def test_scales_with_E1(self):
        E1a = hydrogen_energy_level(2, E1=1.0)
        E1b = hydrogen_energy_level(2, E1=4.0)
        assert abs(E1b / E1a - 4.0) < 1e-10

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            hydrogen_energy_level(0)

    def test_negative_E1_raises(self):
        with pytest.raises(ValueError):
            hydrogen_energy_level(1, E1=-1.0)

    def test_levels_ordered(self):
        levels = [hydrogen_energy_level(n, E1=1.0) for n in range(1, 6)]
        assert levels == sorted(levels)


# ===========================================================================
# TestHydrogenWavelength
# ===========================================================================

class TestHydrogenWavelength:
    """Tests for hydrogen_wavelength."""

    def test_positive_wavelength(self):
        assert hydrogen_wavelength(2, 1) > 0.0

    def test_lyman_alpha_physical_value(self):
        # Lyman α: n=2 → n=1, λ ≈ 121.6 nm = 7.52e27 Planck lengths
        lam = hydrogen_wavelength(2, 1)
        assert 7.0e27 < lam < 8.0e27

    def test_lyman_alpha_formula(self):
        E1 = rydberg_energy()
        expected = 2.0 * np.pi / (E1 * (1.0 - 0.25))
        assert abs(hydrogen_wavelength(2, 1) / expected - 1.0) < 1e-10

    def test_lyman_series_decreasing(self):
        lam2 = hydrogen_wavelength(2, 1)
        lam3 = hydrogen_wavelength(3, 1)
        lam4 = hydrogen_wavelength(4, 1)
        assert lam2 > lam3 > lam4

    def test_balmer_longer_than_lyman(self):
        lyman_alpha = hydrogen_wavelength(2, 1)
        balmer_alpha = hydrogen_wavelength(3, 2)
        assert balmer_alpha > lyman_alpha

    def test_balmer_series_decreasing(self):
        lam32 = hydrogen_wavelength(3, 2)
        lam42 = hydrogen_wavelength(4, 2)
        lam52 = hydrogen_wavelength(5, 2)
        assert lam32 > lam42 > lam52

    def test_scales_inversely_with_E1(self):
        lam1 = hydrogen_wavelength(2, 1, E1=1e-27)
        lam2 = hydrogen_wavelength(2, 1, E1=2e-27)
        assert abs(lam1 / lam2 - 2.0) < 1e-10

    def test_n_i_equals_n_f_raises(self):
        with pytest.raises(ValueError):
            hydrogen_wavelength(2, 2)

    def test_n_i_less_than_n_f_raises(self):
        with pytest.raises(ValueError):
            hydrogen_wavelength(1, 2)

    def test_n_f_zero_raises(self):
        with pytest.raises(ValueError):
            hydrogen_wavelength(2, 0)

    def test_negative_E1_raises(self):
        with pytest.raises(ValueError):
            hydrogen_wavelength(2, 1, E1=-1.0)


# ===========================================================================
# TestHydrogen1sRadialDensity
# ===========================================================================

class TestHydrogen1sRadialDensity:
    """Tests for hydrogen_1s_radial_density."""

    def test_shape_preserved(self):
        r = np.linspace(0.0, 5.0, 50)
        P = hydrogen_1s_radial_density(r, a0=1.0)
        assert P.shape == (50,)

    def test_non_negative_everywhere(self):
        r = np.linspace(0.0, 10.0, 200)
        P = hydrogen_1s_radial_density(r, a0=1.0)
        assert np.all(P >= 0.0)

    def test_zero_at_origin(self):
        P = hydrogen_1s_radial_density(np.array([0.0]), a0=1.0)
        assert abs(P[0]) < 1e-30

    def test_peaks_at_bohr_radius(self):
        a0 = 1.0
        r = np.linspace(0.0, 5.0 * a0, 10_000)
        P = hydrogen_1s_radial_density(r, a0=a0)
        r_peak = r[np.argmax(P)]
        assert abs(r_peak - a0) < 0.001

    def test_normalization(self):
        a0 = 1.0
        r = np.linspace(0.0, 30.0 * a0, 100_000)
        P = hydrogen_1s_radial_density(r, a0=a0)
        dr = r[1] - r[0]
        integral = np.trapezoid(P, r)
        assert abs(integral - 1.0) < 1e-3

    def test_formula_at_bohr_radius(self):
        a0 = 2.0
        r = np.array([a0])
        P = hydrogen_1s_radial_density(r, a0=a0)
        expected = (4.0 / a0 ** 3) * a0 ** 2 * np.exp(-2.0)
        assert abs(P[0] - expected) < 1e-12

    def test_decays_at_large_r(self):
        a0 = 1.0
        P_close = hydrogen_1s_radial_density(np.array([a0]), a0=a0)
        P_far = hydrogen_1s_radial_density(np.array([10.0 * a0]), a0=a0)
        assert P_far[0] < P_close[0]

    def test_scales_with_a0(self):
        r1 = np.array([1.0])
        P1 = hydrogen_1s_radial_density(r1, a0=1.0)
        r2 = np.array([2.0])
        P2 = hydrogen_1s_radial_density(r2, a0=2.0)
        # At r = a0 in both cases: P = (4/a0) * exp(-2)
        assert abs(P1[0] * 1.0 - P2[0] * 2.0) < 1e-12

    def test_nonpositive_a0_raises(self):
        with pytest.raises(ValueError):
            hydrogen_1s_radial_density(np.array([1.0]), a0=0.0)


# ===========================================================================
# TestAtomicOrbitalRadius
# ===========================================================================

class TestAtomicOrbitalRadius:
    """Tests for atomic_orbital_radius."""

    def test_n1_equals_a0(self):
        a0 = 2.5
        assert abs(atomic_orbital_radius(1, a0=a0) - a0) < 1e-12

    def test_n2_equals_four_a0(self):
        a0 = 1.0
        assert abs(atomic_orbital_radius(2, a0=a0) - 4.0) < 1e-12

    def test_n3_equals_nine_a0(self):
        a0 = 1.0
        assert abs(atomic_orbital_radius(3, a0=a0) - 9.0) < 1e-12

    def test_scales_quadratic_with_n(self):
        a0 = 1.0
        r1 = atomic_orbital_radius(1, a0=a0)
        r2 = atomic_orbital_radius(2, a0=a0)
        r3 = atomic_orbital_radius(3, a0=a0)
        assert abs(r2 / r1 - 4.0) < 1e-10
        assert abs(r3 / r1 - 9.0) < 1e-10

    def test_scales_with_a0(self):
        r1 = atomic_orbital_radius(2, a0=1.0)
        r2 = atomic_orbital_radius(2, a0=3.0)
        assert abs(r2 / r1 - 3.0) < 1e-10

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            atomic_orbital_radius(0)

    def test_nonpositive_a0_raises(self):
        with pytest.raises(ValueError):
            atomic_orbital_radius(1, a0=0.0)


# ===========================================================================
# TestNuclearBindingEnergy
# ===========================================================================

class TestNuclearBindingEnergy:
    """Tests for nuclear_binding_energy."""

    def test_carbon12_positive(self):
        # Carbon-12: Z=6, N=6; real B ≈ 92.2 MeV
        B = nuclear_binding_energy(6, 6)
        assert B > 0.0

    def test_iron56_positive(self):
        # Iron-56: Z=26, N=30
        B = nuclear_binding_energy(26, 30)
        assert B > 0.0

    def test_increases_with_A_light_region(self):
        # For light even-even nuclei, binding should grow with A
        B_c12 = nuclear_binding_energy(6, 6)    # A=12
        B_o16 = nuclear_binding_energy(8, 8)    # A=16
        assert B_o16 > B_c12

    def test_iron56_approximate_value(self):
        # Semi-empirical formula gives ~499 MeV for Fe-56
        B = nuclear_binding_energy(26, 30)
        assert 480.0 < B < 520.0

    def test_carbon12_approximate_value(self):
        # Semi-empirical formula gives ~89–92 MeV for C-12
        B = nuclear_binding_energy(6, 6)
        assert 80.0 < B < 100.0

    def test_pairing_even_even_vs_odd_odd(self):
        # Even-even (Z=6, N=6, A=12) should be more bound than odd-odd
        # odd-odd: Z=5, N=7 (A=12, Z odd, N odd)
        B_ee = nuclear_binding_energy(6, 6)
        B_oo = nuclear_binding_energy(5, 7)
        assert B_ee > B_oo

    def test_odd_A_no_pairing(self):
        # For odd-A (e.g., N-14 adjusted to have odd A):  A=13, Z=6
        # pairing term = 0; result should be between even-even and odd-odd
        B_odd = nuclear_binding_energy(6, 7)   # A=13, odd
        B_ee = nuclear_binding_energy(6, 6)    # A=12, even-even
        # odd-A should not have the pairing bonus
        assert B_odd != B_ee

    def test_scales_roughly_with_A(self):
        B12 = nuclear_binding_energy(6, 6)
        B24 = nuclear_binding_energy(12, 12)
        # B/A roughly constant → B24 ≈ 2 * B12 (within 20%)
        ratio = B24 / B12
        assert 1.7 < ratio < 2.4

    def test_Z_one_raises(self):
        # Z=0 should raise
        with pytest.raises(ValueError):
            nuclear_binding_energy(0, 1)

    def test_negative_N_raises(self):
        with pytest.raises(ValueError):
            nuclear_binding_energy(1, -1)

    def test_negative_coefficient_raises(self):
        with pytest.raises(ValueError):
            nuclear_binding_energy(6, 6, a_v=-1.0)

    def test_coulomb_only_proton_no_repulsion(self):
        # Hydrogen nucleus (proton): Z=1, N=0 → Coulomb term = a_c * 1*0/A^(1/3) = 0
        B = nuclear_binding_energy(1, 0)
        # No Coulomb, no asymmetry (since A-2Z = -1, odd → pairing=0)
        # B = 15.75 - 17.80 - 0 - 23.70*1/1 + 0 (negative; proton unbound by SEMF)
        # Just verify the formula runs without error
        assert isinstance(B, float)


# ===========================================================================
# TestNuclearBindingPerNucleon
# ===========================================================================

class TestNuclearBindingPerNucleon:
    """Tests for nuclear_binding_per_nucleon."""

    def test_positive_for_iron(self):
        assert nuclear_binding_per_nucleon(26, 30) > 0.0

    def test_iron_near_peak(self):
        # Fe-56 B/A ≈ 8.8 MeV; our formula gives ~8.9 MeV
        B_A = nuclear_binding_per_nucleon(26, 30)
        assert 8.5 < B_A < 9.2

    def test_iron_higher_than_carbon(self):
        B_Fe = nuclear_binding_per_nucleon(26, 30)
        B_C = nuclear_binding_per_nucleon(6, 6)
        assert B_Fe > B_C

    def test_iron_higher_than_uranium(self):
        B_Fe = nuclear_binding_per_nucleon(26, 30)
        B_U = nuclear_binding_per_nucleon(92, 146)
        assert B_Fe > B_U

    def test_consistent_with_total_binding(self):
        Z, N = 20, 20   # Ca-40
        B_total = nuclear_binding_energy(Z, N)
        B_per = nuclear_binding_per_nucleon(Z, N)
        assert abs(B_per * (Z + N) - B_total) < 1e-10

    def test_Z_zero_raises(self):
        with pytest.raises(ValueError):
            nuclear_binding_per_nucleon(0, 10)
