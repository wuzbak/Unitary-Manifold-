"""
tests/test_chemistry.py
=======================
Unit tests for src/chemistry/bonds.py, src/chemistry/reactions.py,
and src/chemistry/periodic.py.

Covers every public function in the chemistry package (100 tests total).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.chemistry.bonds import (
    phi_bond_well,
    bond_energy,
    bond_length_from_winding,
    chemical_potential,
    bond_order,
    is_bond_stable,
    shell_capacity,
)
from src.chemistry.reactions import (
    arrhenius_rate,
    b_field_activation_energy,
    equilibrium_constant,
    reaction_flux,
    field_strength_tensor,
    gibbs_analog,
)
from src.chemistry.periodic import (
    shell_capacity as periodic_shell_capacity,
    cumulative_capacity,
    period_length,
    shell_radius,
    geometric_ionization_energy,
    atomic_number_at_shell_fill,
    winding_to_element,
)


# ===========================================================================
# TestPhiBondWell
# ===========================================================================

class TestPhiBondWell:
    """Tests for phi_bond_well."""

    def test_shape_preserved(self):
        r = np.linspace(0.0, 4.0, 50)
        result = phi_bond_well(r, r0=2.0, phi_inf=1.0, phi_min=0.5, a=1.0)
        assert result.shape == (50,)

    def test_minimum_at_r0(self):
        r = np.linspace(0.0, 4.0, 1000)
        result = phi_bond_well(r, r0=2.0, phi_inf=1.0, phi_min=0.3, a=2.0)
        idx_min = np.argmin(result)
        assert abs(r[idx_min] - 2.0) < 0.01

    def test_minimum_value_equals_phi_min(self):
        r = np.array([2.0])
        result = phi_bond_well(r, r0=2.0, phi_inf=1.0, phi_min=0.3, a=1.0)
        assert abs(result[0] - 0.3) < 1e-10

    def test_asymptotic_value_at_far_r(self):
        r = np.array([1e6])
        result = phi_bond_well(r, r0=2.0, phi_inf=1.0, phi_min=0.3, a=1.0)
        assert abs(result[0] - 1.0) < 1e-10

    def test_symmetric_about_r0(self):
        r0 = 3.0
        dr = 0.5
        result_left = phi_bond_well(
            np.array([r0 - dr]), r0=r0, phi_inf=1.0, phi_min=0.2, a=1.5
        )
        result_right = phi_bond_well(
            np.array([r0 + dr]), r0=r0, phi_inf=1.0, phi_min=0.2, a=1.5
        )
        assert abs(result_left[0] - result_right[0]) < 1e-12

    def test_scalar_input_works(self):
        result = phi_bond_well(np.array([0.0, 1.0, 2.0]), r0=1.0,
                               phi_inf=2.0, phi_min=1.0, a=1.0)
        assert result.shape == (3,)

    def test_depth_matches_formula(self):
        r = np.array([1.0])
        phi_inf, phi_min, a, r0 = 2.0, 0.5, 1.0, 1.0
        expected = phi_inf - (phi_inf - phi_min) * np.exp(-(a ** 2) * (1.0 - r0) ** 2)
        result = phi_bond_well(r, r0=r0, phi_inf=phi_inf, phi_min=phi_min, a=a)
        assert abs(result[0] - expected) < 1e-12


# ===========================================================================
# TestBondEnergy
# ===========================================================================

class TestBondEnergy:
    """Tests for bond_energy."""

    def test_positive_energy(self):
        assert bond_energy(1.0, 0.5) > 0.0

    def test_zero_when_equal(self):
        assert bond_energy(0.7, 0.7) == 0.0

    def test_proportional_to_difference(self):
        assert abs(bond_energy(2.0, 1.0) - 1.0) < 1e-12
        assert abs(bond_energy(3.0, 1.0) - 2.0) < 1e-12

    def test_raises_when_min_exceeds_inf(self):
        with pytest.raises(ValueError):
            bond_energy(0.5, 1.0)

    def test_large_well(self):
        assert abs(bond_energy(100.0, 0.0) - 100.0) < 1e-10


# ===========================================================================
# TestBondLength
# ===========================================================================

class TestBondLength:
    """Tests for bond_length_from_winding."""

    def test_positive(self):
        assert bond_length_from_winding(1, 1.0) > 0.0

    def test_scales_with_phi_mean(self):
        r1 = bond_length_from_winding(1, 1.0)
        r2 = bond_length_from_winding(1, 2.0)
        assert abs(r2 / r1 - 2.0) < 1e-10

    def test_inverse_in_n_w(self):
        r1 = bond_length_from_winding(1, 1.0)
        r2 = bond_length_from_winding(2, 1.0)
        assert abs(r1 / r2 - 2.0) < 1e-10

    def test_formula_value(self):
        r = bond_length_from_winding(2, 1.0, lam=1.0)
        expected = 2.0 * np.pi * 1.0 / (1.0 * 2)
        assert abs(r - expected) < 1e-10

    def test_raises_n_w_zero(self):
        with pytest.raises(ValueError):
            bond_length_from_winding(0, 1.0)

    def test_raises_phi_zero(self):
        with pytest.raises(ValueError):
            bond_length_from_winding(1, 0.0)

    def test_raises_lam_zero(self):
        with pytest.raises(ValueError):
            bond_length_from_winding(1, 1.0, lam=0.0)


# ===========================================================================
# TestChemicalPotential
# ===========================================================================

class TestChemicalPotential:
    """Tests for chemical_potential."""

    def test_shape_preserved(self):
        r = np.linspace(0.0, 1.0, 20)
        phi = np.ones(20)
        mu = chemical_potential(r, phi)
        assert mu.shape == (20,)

    def test_flat_phi_near_zero_gradient(self):
        r = np.linspace(0.0, 5.0, 100)
        phi = np.ones(100)
        mu = chemical_potential(r, phi)
        assert np.allclose(mu, 0.0, atol=1e-10)

    def test_linear_phi_constant_negative_gradient(self):
        r = np.linspace(0.0, 1.0, 100)
        phi = 2.0 * r + 1.0    # dphi/dr = 2  everywhere
        mu = chemical_potential(r, phi, dx=r[1] - r[0])
        # mu = -dphi/dr = -2 everywhere (interior)
        assert np.allclose(mu[2:-2], -2.0, atol=1e-3)

    def test_well_gradient_at_minimum_near_zero(self):
        r = np.linspace(0.0, 4.0, 1000)
        phi = phi_bond_well(r, r0=2.0, phi_inf=1.0, phi_min=0.5, a=1.0)
        mu = chemical_potential(r, phi, dx=r[1] - r[0])
        idx_r0 = np.argmin(np.abs(r - 2.0))
        assert abs(mu[idx_r0]) < 0.05


# ===========================================================================
# TestBondOrder
# ===========================================================================

class TestBondOrder:
    """Tests for bond_order."""

    def test_unit_bond(self):
        assert abs(bond_order(5, n_w_ref=5) - 1.0) < 1e-10

    def test_double_bond(self):
        assert abs(bond_order(10, n_w_ref=5) - 2.0) < 1e-10

    def test_triple_bond(self):
        assert abs(bond_order(15, n_w_ref=5) - 3.0) < 1e-10

    def test_fractional_bond(self):
        assert abs(bond_order(1, n_w_ref=5) - 0.2) < 1e-10

    def test_raises_negative_n_w_bond(self):
        with pytest.raises(ValueError):
            bond_order(-1, n_w_ref=5)

    def test_raises_zero_n_w_ref(self):
        with pytest.raises(ValueError):
            bond_order(5, n_w_ref=0)


# ===========================================================================
# TestIsBondStable
# ===========================================================================

class TestIsBondStable:
    """Tests for is_bond_stable."""

    def test_stable_below_threshold(self):
        assert bool(is_bond_stable(0.5, 1.0)) is True

    def test_unstable_above_threshold(self):
        assert bool(is_bond_stable(1.5, 1.0)) is False

    def test_array_output(self):
        B = np.array([0.1, 0.5, 1.5, 2.0])
        result = is_bond_stable(B, 1.0)
        assert result.shape == (4,)
        np.testing.assert_array_equal(result, [True, True, False, False])

    def test_raises_zero_threshold(self):
        with pytest.raises(ValueError):
            is_bond_stable(0.5, 0.0)


# ===========================================================================
# TestShellCapacity (bonds.py)
# ===========================================================================

class TestShellCapacity:
    """Tests for shell_capacity in bonds.py."""

    def test_n1_gives_2(self):
        assert shell_capacity(1) == 2

    def test_n2_gives_8(self):
        assert shell_capacity(2) == 8

    def test_n3_gives_18(self):
        assert shell_capacity(3) == 18

    def test_n4_gives_32(self):
        assert shell_capacity(4) == 32

    def test_n5_gives_50(self):
        assert shell_capacity(5) == 50

    def test_raises_n0(self):
        with pytest.raises(ValueError):
            shell_capacity(0)


# ===========================================================================
# TestArrheniusRate
# ===========================================================================

class TestArrheniusRate:
    """Tests for arrhenius_rate."""

    def test_high_T_limit(self):
        k = arrhenius_rate(A=1.0, E_a=1.0, T=1e10, k_B=1.0)
        assert abs(k - 1.0) < 1e-6

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            arrhenius_rate(1.0, 1.0, T=0.0)

    def test_negative_T_raises(self):
        with pytest.raises(ValueError):
            arrhenius_rate(1.0, 1.0, T=-1.0)

    def test_zero_activation_energy(self):
        k = arrhenius_rate(A=2.0, E_a=0.0, T=300.0)
        assert abs(k - 2.0) < 1e-10

    def test_scaling_with_A(self):
        k1 = arrhenius_rate(A=1.0, E_a=1.0, T=1.0)
        k2 = arrhenius_rate(A=2.0, E_a=1.0, T=1.0)
        assert abs(k2 / k1 - 2.0) < 1e-10

    def test_positive_result(self):
        assert arrhenius_rate(1.0, 0.5, 1.0) > 0.0


# ===========================================================================
# TestBFieldActivationEnergy
# ===========================================================================

class TestBFieldActivationEnergy:
    """Tests for b_field_activation_energy."""

    def test_positive(self):
        assert b_field_activation_energy(1.0, 1.0) > 0.0

    def test_quadratic_in_H_max(self):
        e1 = b_field_activation_energy(H_max=1.0, phi_mean=1.0)
        e2 = b_field_activation_energy(H_max=2.0, phi_mean=1.0)
        assert abs(e2 / e1 - 4.0) < 1e-10

    def test_quadratic_in_phi_mean(self):
        e1 = b_field_activation_energy(H_max=1.0, phi_mean=1.0)
        e2 = b_field_activation_energy(H_max=1.0, phi_mean=2.0)
        assert abs(e2 / e1 - 4.0) < 1e-10

    def test_formula_value(self):
        e = b_field_activation_energy(H_max=2.0, phi_mean=3.0, lam=1.0)
        expected = 0.5 * 1.0 ** 2 * 3.0 ** 2 * 2.0 ** 2
        assert abs(e - expected) < 1e-10

    def test_zero_H_gives_zero(self):
        assert b_field_activation_energy(H_max=0.0, phi_mean=1.0) == 0.0


# ===========================================================================
# TestEquilibriumConstant
# ===========================================================================

class TestEquilibriumConstant:
    """Tests for equilibrium_constant."""

    def test_delta_phi_zero_gives_K_one(self):
        assert abs(equilibrium_constant(0.0, T=1.0) - 1.0) < 1e-12

    def test_positive_delta_phi_K_less_than_one(self):
        K = equilibrium_constant(1.0, T=1.0)
        assert K < 1.0

    def test_negative_delta_phi_K_greater_than_one(self):
        K = equilibrium_constant(-1.0, T=1.0)
        assert K > 1.0

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            equilibrium_constant(1.0, T=0.0)

    def test_formula_value(self):
        K = equilibrium_constant(2.0, T=2.0, k_B=1.0)
        expected = np.exp(-1.0)
        assert abs(K - expected) < 1e-12


# ===========================================================================
# TestReactionFlux
# ===========================================================================

class TestReactionFlux:
    """Tests for reaction_flux."""

    def test_shape_preserved(self):
        phi = np.ones(40)
        J = reaction_flux(phi)
        assert J.shape == (40,)

    def test_constant_phi_zero_flux(self):
        phi = np.ones(50) * 2.0
        J = reaction_flux(phi, D=1.0, dx=1.0)
        assert np.allclose(J, 0.0, atol=1e-10)

    def test_linear_phi_nonzero_flux(self):
        phi = np.linspace(1.0, 2.0, 50)
        J = reaction_flux(phi, D=1.0, dx=phi[1] - phi[0])
        # gradient is positive → flux should be positive in interior
        assert np.all(J[2:-2] > 0)

    def test_scaling_with_D(self):
        phi = np.linspace(1.0, 3.0, 50)
        J1 = reaction_flux(phi, D=1.0)
        J2 = reaction_flux(phi, D=3.0)
        np.testing.assert_allclose(J2, 3.0 * J1, rtol=1e-10)


# ===========================================================================
# TestFieldStrengthTensor
# ===========================================================================

class TestFieldStrengthTensor:
    """Tests for field_strength_tensor."""

    def test_constant_B_zero_field_strength(self):
        B = np.ones(40) * 3.0
        H = field_strength_tensor(B)
        assert np.allclose(H, 0.0, atol=1e-10)

    def test_linear_B_constant_field_strength(self):
        B = np.linspace(0.0, 1.0, 100)
        dx = B[1] - B[0]
        H = field_strength_tensor(B, dx=dx)
        # B goes from 0 to 1 over 100 points → slope = 1.0, so |dB/dx| ≈ 1.0
        assert np.allclose(H[2:-2], 1.0, atol=1e-6)

    def test_shape_preserved(self):
        B = np.sin(np.linspace(0, 2 * np.pi, 64))
        H = field_strength_tensor(B)
        assert H.shape == (64,)

    def test_non_negative(self):
        B = np.random.default_rng(0).standard_normal(80)
        H = field_strength_tensor(B)
        assert np.all(H >= 0.0)


# ===========================================================================
# TestGibbsAnalog
# ===========================================================================

class TestGibbsAnalog:
    """Tests for gibbs_analog."""

    def test_zero_delta_S_gives_zero(self):
        assert gibbs_analog(0.0, T=300.0) == 0.0

    def test_scales_with_T(self):
        dG1 = gibbs_analog(1.0, T=1.0)
        dG2 = gibbs_analog(1.0, T=2.0)
        assert abs(dG2 / dG1 - 2.0) < 1e-10

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            gibbs_analog(1.0, T=0.0)

    def test_negative_delta_S(self):
        dG = gibbs_analog(-1.0, T=1.0)
        assert dG < 0.0


# ===========================================================================
# TestPeriodLength
# ===========================================================================

class TestPeriodLength:
    """Tests for period_length."""

    def test_period1_is_2(self):
        assert period_length(1) == 2

    def test_period2_is_8(self):
        assert period_length(2) == 8

    def test_period3_is_8(self):
        assert period_length(3) == 8

    def test_period4_is_18(self):
        assert period_length(4) == 18

    def test_period5_is_18(self):
        assert period_length(5) == 18

    def test_period6_is_32(self):
        assert period_length(6) == 32

    def test_period7_is_32(self):
        assert period_length(7) == 32

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            period_length(8)


# ===========================================================================
# TestPeriodicShellCapacity
# ===========================================================================

class TestPeriodicShellCapacity:
    """Tests for shell_capacity in periodic.py."""

    def test_n1(self):
        assert periodic_shell_capacity(1) == 2

    def test_n2(self):
        assert periodic_shell_capacity(2) == 8

    def test_n3(self):
        assert periodic_shell_capacity(3) == 18

    def test_n4(self):
        assert periodic_shell_capacity(4) == 32

    def test_raises_n0(self):
        with pytest.raises(ValueError):
            periodic_shell_capacity(0)


# ===========================================================================
# TestCumulativeCapacity
# ===========================================================================

class TestCumulativeCapacity:
    """Tests for cumulative_capacity."""

    def test_n1_is_2(self):
        assert cumulative_capacity(1) == 2

    def test_n2_is_10(self):
        assert cumulative_capacity(2) == 10

    def test_n3_is_28(self):
        assert cumulative_capacity(3) == 28

    def test_raises_n0(self):
        with pytest.raises(ValueError):
            cumulative_capacity(0)


# ===========================================================================
# TestShellRadius
# ===========================================================================

class TestShellRadius:
    """Tests for shell_radius."""

    def test_n1_a0_1(self):
        assert abs(shell_radius(1, a0=1.0) - 1.0) < 1e-10

    def test_n2_a0_1(self):
        assert abs(shell_radius(2, a0=1.0) - 4.0) < 1e-10

    def test_scales_with_a0(self):
        r1 = shell_radius(1, a0=1.0)
        r2 = shell_radius(1, a0=2.0)
        assert abs(r2 / r1 - 2.0) < 1e-10

    def test_raises_n0(self):
        with pytest.raises(ValueError):
            shell_radius(0)

    def test_raises_a0_zero(self):
        with pytest.raises(ValueError):
            shell_radius(1, a0=0.0)


# ===========================================================================
# TestGeometricIonizationEnergy
# ===========================================================================

class TestGeometricIonizationEnergy:
    """Tests for geometric_ionization_energy."""

    def test_positive(self):
        assert geometric_ionization_energy(1.0, 1, 1.0) > 0.0

    def test_scales_with_Z_eff(self):
        e1 = geometric_ionization_energy(1.0, 1, 1.0)
        e2 = geometric_ionization_energy(2.0, 1, 1.0)
        assert abs(e2 / e1 - 2.0) < 1e-10

    def test_decreases_with_n(self):
        e1 = geometric_ionization_energy(1.0, 1, 1.0)
        e2 = geometric_ionization_energy(1.0, 2, 1.0)
        assert e2 < e1

    def test_formula_value(self):
        e = geometric_ionization_energy(Z_eff=2.0, n=2, phi_mean=1.0, lam=1.0)
        expected = 1.0 ** 2 * 2.0 / (2 ** 2 * 1.0) ** 2
        assert abs(e - expected) < 1e-10

    def test_raises_zero_Z(self):
        with pytest.raises(ValueError):
            geometric_ionization_energy(0.0, 1, 1.0)


# ===========================================================================
# TestAtomicNumberAtShellFill
# ===========================================================================

class TestAtomicNumberAtShellFill:
    """Tests for atomic_number_at_shell_fill."""

    def test_n1_gives_2(self):
        assert atomic_number_at_shell_fill(1) == 2

    def test_n2_gives_10(self):
        assert atomic_number_at_shell_fill(2) == 10

    def test_matches_cumulative_capacity(self):
        for n in range(1, 6):
            assert atomic_number_at_shell_fill(n) == cumulative_capacity(n)

    def test_raises_n0(self):
        with pytest.raises(ValueError):
            atomic_number_at_shell_fill(0)


# ===========================================================================
# TestWindingToElement
# ===========================================================================

class TestWindingToElement:
    """Tests for winding_to_element."""

    def test_keys_present(self):
        info = winding_to_element(1)
        assert set(info.keys()) == {"shell", "capacity", "Z_fill"}

    def test_n1_values(self):
        info = winding_to_element(1)
        assert info["shell"] == 1
        assert info["capacity"] == 2
        assert info["Z_fill"] == 2

    def test_n3_values(self):
        info = winding_to_element(3)
        assert info["capacity"] == 18
        assert info["Z_fill"] == cumulative_capacity(3)

    def test_raises_n0(self):
        with pytest.raises(ValueError):
            winding_to_element(0)
