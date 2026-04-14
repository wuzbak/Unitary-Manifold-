# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
recycling/tests/test_recycling.py
==================================
Unit tests for Pillar 16: Material Recovery & Recycling.

Covers every public function in:
  - recycling/polymers.py              (~70 tests)
  - recycling/thermochemical.py        (~70 tests)
  - recycling/entropy_ledger.py        (~75 tests)
  - recycling/producer_responsibility.py (~80 tests)

Total: ~295 tests.
"""

import sys
import os

# Allow imports from the repo root and from the recycling package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


import numpy as np
import pytest

from recycling.polymers import (
    polymer_bond_phi,
    recyclability_index,
    depolymerization_barrier,
    sorting_discriminability,
    is_contaminated,
    degradation_rate,
    cycle_quality_loss,
    microplastic_flux,
    polymer_winding_number,
    chain_entanglement_density,
    phi_from_recyclate_density,
    sorting_purity,
)
from recycling.thermochemical import (
    pyrolysis_onset_temperature,
    pyrolysis_yield,
    gasification_efficiency,
    solvolysis_rate,
    activation_energy_chemical_recycling,
    b_field_phase_boundary,
    syngas_phi,
    thermal_cracking_threshold,
    co2_reduction_factor,
    chemical_recycling_cop,
    monomer_purity,
)
from recycling.entropy_ledger import (
    production_entropy,
    use_phase_phi,
    recycling_entropy_cost,
    landfill_entropy_rate,
    true_recycling_efficiency,
    lifecycle_phi_trace,
    alignment_score,
    material_entropy_debt,
    information_loss_per_cycle,
    closed_loop_criterion,
    open_loop_entropy_budget,
    downcycling_depth,
)
from recycling.producer_responsibility import (
    phi_return_force,
    producer_phi_debt,
    epr_levy,
    deposit_refund_amount,
    closed_loop_radius,
    return_probability,
    takeback_efficiency,
    phi_origin_label,
    systemic_entropy_saved,
    lifecycle_return_incentive,
)


# ===========================================================================
# polymers.py — TestPolymerBondPhi
# ===========================================================================

class TestPolymerBondPhi:
    def test_at_minimum(self):
        r = np.array([1.5])
        phi = polymer_bond_phi(r, r0=1.5, phi_inf=2.0, phi_min=0.5, a=1.0)
        assert np.isclose(phi[0], 0.5)

    def test_asymptote(self):
        r = np.array([1000.0])
        phi = polymer_bond_phi(r, r0=0.0, phi_inf=2.0, phi_min=0.5, a=1.0)
        assert np.isclose(phi[0], 2.0, atol=1e-6)

    def test_symmetric_about_r0(self):
        r = np.array([0.5, 2.5])
        phi = polymer_bond_phi(r, r0=1.5, phi_inf=2.0, phi_min=0.5, a=1.0)
        assert np.isclose(phi[0], phi[1])

    def test_returns_array(self):
        r = np.linspace(0, 3, 20)
        phi = polymer_bond_phi(r, r0=1.5, phi_inf=2.0, phi_min=0.5, a=1.0)
        assert phi.shape == (20,)

    def test_phi_bounded(self):
        r = np.linspace(0, 5, 100)
        phi = polymer_bond_phi(r, r0=2.5, phi_inf=3.0, phi_min=1.0, a=0.5)
        assert np.all(phi >= 1.0 - 1e-12)
        assert np.all(phi <= 3.0 + 1e-12)

    def test_wider_well_shallower_gradient(self):
        r = np.array([2.0])
        phi_narrow = polymer_bond_phi(r, r0=1.5, phi_inf=2.0, phi_min=0.5, a=2.0)
        phi_wide   = polymer_bond_phi(r, r0=1.5, phi_inf=2.0, phi_min=0.5, a=0.5)
        # narrow well (large a) recovers toward phi_inf quickly; wide well stays lower
        assert phi_narrow[0] > phi_wide[0]


# ===========================================================================
# polymers.py — TestRecyclabilityIndex
# ===========================================================================

class TestRecyclabilityIndex:
    def test_perfect_recovery(self):
        assert np.isclose(recyclability_index(2.0, 2.0), 1.0)

    def test_zero_recovery(self):
        assert np.isclose(recyclability_index(0.0, 2.0), 0.0)

    def test_partial_recovery(self):
        ri = recyclability_index(1.0, 2.0)
        assert np.isclose(ri, 0.5)

    def test_clamped_above_one(self):
        ri = recyclability_index(3.0, 2.0)
        assert np.isclose(ri, 1.0)

    def test_zero_formation_raises(self):
        with pytest.raises(ValueError):
            recyclability_index(1.0, 0.0)

    def test_returns_float(self):
        assert isinstance(recyclability_index(1.0, 2.0), float)


# ===========================================================================
# polymers.py — TestDepolymerizationBarrier
# ===========================================================================

class TestDepolymerizationBarrier:
    def test_zero_H_max(self):
        assert np.isclose(depolymerization_barrier(0.0, 1.0), 0.0)

    def test_scales_quadratic_H(self):
        e1 = depolymerization_barrier(1.0, 1.0)
        e2 = depolymerization_barrier(2.0, 1.0)
        assert np.isclose(e2, 4.0 * e1)

    def test_scales_quadratic_phi(self):
        e1 = depolymerization_barrier(1.0, 1.0)
        e2 = depolymerization_barrier(1.0, 2.0)
        assert np.isclose(e2, 4.0 * e1)

    def test_scales_quadratic_lam(self):
        e1 = depolymerization_barrier(1.0, 1.0, lam=1.0)
        e2 = depolymerization_barrier(1.0, 1.0, lam=2.0)
        assert np.isclose(e2, 4.0 * e1)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            depolymerization_barrier(1.0, 0.0)

    def test_lam_zero_raises(self):
        with pytest.raises(ValueError):
            depolymerization_barrier(1.0, 1.0, lam=0.0)

    def test_formula(self):
        result = depolymerization_barrier(2.0, 3.0, lam=0.5)
        expected = 0.5 * 0.25 * 9.0 * 4.0
        assert np.isclose(result, expected)


# ===========================================================================
# polymers.py — TestSortingDiscriminability
# ===========================================================================

class TestSortingDiscriminability:
    def test_identical_phi(self):
        assert np.isclose(sorting_discriminability(1.0, 1.0), 0.0)

    def test_symmetric(self):
        d_ab = sorting_discriminability(1.0, 3.0)
        d_ba = sorting_discriminability(3.0, 1.0)
        assert np.isclose(d_ab, d_ba)

    def test_formula(self):
        d = sorting_discriminability(1.0, 3.0)
        assert np.isclose(d, 2.0 / 4.0)

    def test_large_contrast(self):
        d = sorting_discriminability(0.01, 100.0)
        assert d > 0.99

    def test_phi_a_zero_raises(self):
        with pytest.raises(ValueError):
            sorting_discriminability(0.0, 1.0)

    def test_phi_b_zero_raises(self):
        with pytest.raises(ValueError):
            sorting_discriminability(1.0, 0.0)


# ===========================================================================
# polymers.py — TestIsContaminated
# ===========================================================================

class TestIsContaminated:
    def test_clean_stream(self):
        B = np.array([0.1, 0.2, 0.05])
        mask = is_contaminated(B, B_threshold=0.5)
        assert not np.any(mask)

    def test_full_contamination(self):
        B = np.array([1.0, 2.0, 3.0])
        mask = is_contaminated(B, B_threshold=0.5)
        assert np.all(mask)

    def test_mixed(self):
        B = np.array([0.1, 0.6, 0.3])
        mask = is_contaminated(B, B_threshold=0.5)
        assert not mask[0]
        assert mask[1]
        assert not mask[2]

    def test_boundary_at_threshold(self):
        B = np.array([0.5])
        mask = is_contaminated(B, B_threshold=0.5)
        assert mask[0]

    def test_zero_threshold_raises(self):
        with pytest.raises(ValueError):
            is_contaminated(np.array([0.5]), B_threshold=0.0)


# ===========================================================================
# polymers.py — TestDegradationRate
# ===========================================================================

class TestDegradationRate:
    def test_higher_phi_lower_rate(self):
        k1 = degradation_rate(1.0, phi_chain=1.0)
        k2 = degradation_rate(1.0, phi_chain=2.0)
        assert k2 < k1

    def test_higher_T_higher_rate(self):
        k1 = degradation_rate(1.0, phi_chain=1.0)
        k2 = degradation_rate(2.0, phi_chain=1.0)
        assert k2 > k1

    def test_T_zero_raises(self):
        with pytest.raises(ValueError):
            degradation_rate(0.0, phi_chain=1.0)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            degradation_rate(1.0, phi_chain=0.0)

    def test_returns_float(self):
        assert isinstance(degradation_rate(1.0, phi_chain=1.0), float)

    def test_formula(self):
        k = degradation_rate(T=2.0, phi_chain=3.0, A=1.0, E_a=6.0, k_B=1.0)
        assert np.isclose(k, np.exp(-3.0 * 6.0 / (1.0 * 2.0)))


# ===========================================================================
# polymers.py — TestCycleQualityLoss
# ===========================================================================

class TestCycleQualityLoss:
    def test_zero_cycles(self):
        assert np.isclose(cycle_quality_loss(2.0, 0, 0.1), 2.0)

    def test_one_cycle(self):
        phi = cycle_quality_loss(1.0, 1, 0.5)
        assert np.isclose(phi, np.exp(-0.5))

    def test_monotone_decreasing(self):
        vals = [cycle_quality_loss(1.0, n, 0.1) for n in range(10)]
        assert all(vals[i] > vals[i + 1] for i in range(9))

    def test_negative_cycles_raises(self):
        with pytest.raises(ValueError):
            cycle_quality_loss(1.0, -1, 0.1)

    def test_phi0_zero_raises(self):
        with pytest.raises(ValueError):
            cycle_quality_loss(0.0, 1, 0.1)

    def test_alpha_zero_raises(self):
        with pytest.raises(ValueError):
            cycle_quality_loss(1.0, 1, 0.0)

    def test_five_cycles(self):
        phi = cycle_quality_loss(1.0, 5, 0.15)
        assert np.isclose(phi, np.exp(-0.75))


# ===========================================================================
# polymers.py — TestMicroplasticFlux
# ===========================================================================

class TestMicroplasticFlux:
    def test_flat_phi_zero_flux(self):
        phi = np.ones(10) * 2.0
        J = microplastic_flux(phi)
        assert np.allclose(J, 0.0, atol=1e-12)

    def test_gradient_drives_flux(self):
        phi = np.linspace(1.0, 2.0, 10)
        J = microplastic_flux(phi, D=1.0, dx=1.0)
        assert np.any(J > 0.0)

    def test_returns_array(self):
        phi = np.linspace(0.5, 1.5, 20)
        J = microplastic_flux(phi)
        assert J.shape == (20,)

    def test_diffusivity_scales(self):
        phi = np.linspace(1.0, 2.0, 10)
        J1 = microplastic_flux(phi, D=1.0)
        J2 = microplastic_flux(phi, D=2.0)
        assert np.allclose(J2, 2.0 * J1)


# ===========================================================================
# polymers.py — TestPolymerWindingNumber
# ===========================================================================

class TestPolymerWindingNumber:
    def test_basic(self):
        assert polymer_winding_number(10.0, 1.0) == 10

    def test_minimum_one(self):
        assert polymer_winding_number(0.1, 1.0) == 1

    def test_rounding(self):
        assert polymer_winding_number(10.6, 1.0) == 11

    def test_zero_backbone_raises(self):
        with pytest.raises(ValueError):
            polymer_winding_number(0.0, 1.0)

    def test_zero_kuhn_raises(self):
        with pytest.raises(ValueError):
            polymer_winding_number(10.0, 0.0)

    def test_returns_int(self):
        assert isinstance(polymer_winding_number(10.0, 1.0), int)


# ===========================================================================
# polymers.py — TestChainEntanglementDensity
# ===========================================================================

class TestChainEntanglementDensity:
    def test_basic(self):
        rho = chain_entanglement_density(n_chains=10.0, phi_mean=2.0, volume=5.0)
        assert np.isclose(rho, 4.0)

    def test_scales_with_chains(self):
        rho1 = chain_entanglement_density(5.0, 1.0, 1.0)
        rho2 = chain_entanglement_density(10.0, 1.0, 1.0)
        assert np.isclose(rho2, 2.0 * rho1)

    def test_n_chains_zero_raises(self):
        with pytest.raises(ValueError):
            chain_entanglement_density(0.0, 1.0, 1.0)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            chain_entanglement_density(1.0, 0.0, 1.0)

    def test_volume_zero_raises(self):
        with pytest.raises(ValueError):
            chain_entanglement_density(1.0, 1.0, 0.0)


# ===========================================================================
# polymers.py — TestPhiFromRecyclateDensity
# ===========================================================================

class TestPhiFromRecyclateDensity:
    def test_at_reference(self):
        assert np.isclose(phi_from_recyclate_density(1000.0, 1000.0, 1.0), 1.0)

    def test_double_density(self):
        phi = phi_from_recyclate_density(2000.0, 1000.0, 1.0)
        assert np.isclose(phi, 2.0)

    def test_half_density(self):
        phi = phi_from_recyclate_density(500.0, 1000.0, 1.0)
        assert np.isclose(phi, 0.5)

    def test_zero_density_raises(self):
        with pytest.raises(ValueError):
            phi_from_recyclate_density(0.0, 1000.0, 1.0)

    def test_zero_ref_raises(self):
        with pytest.raises(ValueError):
            phi_from_recyclate_density(1000.0, 0.0, 1.0)


# ===========================================================================
# polymers.py — TestSortingPurity
# ===========================================================================

class TestSortingPurity:
    def test_perfect_match(self):
        assert np.isclose(sorting_purity(1.0, 1.0, 0.1), 1.0)

    def test_decreases_with_offset(self):
        p1 = sorting_purity(1.0, 1.0, 0.5)
        p2 = sorting_purity(1.5, 1.0, 0.5)
        assert p1 > p2

    def test_sigma_zero_raises(self):
        with pytest.raises(ValueError):
            sorting_purity(1.0, 1.0, 0.0)

    def test_symmetric(self):
        p1 = sorting_purity(0.5, 1.0, 0.3)
        p2 = sorting_purity(1.5, 1.0, 0.3)
        assert np.isclose(p1, p2)

    def test_returns_float(self):
        assert isinstance(sorting_purity(1.0, 1.0, 0.1), float)


# ===========================================================================
# thermochemical.py — TestPyrolysisOnsetTemperature
# ===========================================================================

class TestPyrolysisOnsetTemperature:
    def test_basic(self):
        T = pyrolysis_onset_temperature(phi_chain=1.0, E_a=1.0, A=np.e, k_rate_target=1.0)
        assert np.isclose(T, 1.0)  # phi*E_a / (k_B * ln(e/1)) = 1*1/(1*1) = 1

    def test_higher_phi_higher_T(self):
        T1 = pyrolysis_onset_temperature(1.0, 1.0, A=2.0, k_rate_target=1.0)
        T2 = pyrolysis_onset_temperature(2.0, 1.0, A=2.0, k_rate_target=1.0)
        assert T2 > T1

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            pyrolysis_onset_temperature(0.0, 1.0)

    def test_E_a_zero_raises(self):
        with pytest.raises(ValueError):
            pyrolysis_onset_temperature(1.0, 0.0)

    def test_A_le_target_raises(self):
        with pytest.raises(ValueError):
            pyrolysis_onset_temperature(1.0, 1.0, A=0.5, k_rate_target=1.0)

    def test_returns_positive(self):
        T = pyrolysis_onset_temperature(1.0, 1.0, A=10.0, k_rate_target=1.0)
        assert T > 0.0


# ===========================================================================
# thermochemical.py — TestPyrolysisYield
# ===========================================================================

class TestPyrolysisYield:
    def test_equal_barriers_full_yield(self):
        Y = pyrolysis_yield(1.0, 1.0, T=1.0)
        assert np.isclose(Y, 1.0)

    def test_chain_barrier_higher_reduces_yield(self):
        Y = pyrolysis_yield(E_a_chain=2.0, E_a_monomer=1.0, T=1.0)
        assert Y < 1.0

    def test_high_T_raises_yield(self):
        Y1 = pyrolysis_yield(2.0, 1.0, T=1.0)
        Y2 = pyrolysis_yield(2.0, 1.0, T=10.0)
        assert Y2 > Y1

    def test_T_zero_raises(self):
        with pytest.raises(ValueError):
            pyrolysis_yield(1.0, 1.0, T=0.0)

    def test_yield_clamped(self):
        Y = pyrolysis_yield(0.0, 2.0, T=1.0)
        assert 0.0 <= Y <= 1.0

    def test_returns_float(self):
        assert isinstance(pyrolysis_yield(1.0, 1.0, T=1.0), float)


# ===========================================================================
# thermochemical.py — TestGasificationEfficiency
# ===========================================================================

class TestGasificationEfficiency:
    def test_perfect_conversion(self):
        assert np.isclose(gasification_efficiency(2.0, 2.0), 1.0)

    def test_partial_conversion(self):
        assert np.isclose(gasification_efficiency(2.0, 1.0), 0.5)

    def test_clamped_at_one(self):
        assert np.isclose(gasification_efficiency(1.0, 2.0), 1.0)

    def test_zero_syngas(self):
        assert np.isclose(gasification_efficiency(2.0, 0.0), 0.0)

    def test_phi_solid_zero_raises(self):
        with pytest.raises(ValueError):
            gasification_efficiency(0.0, 1.0)

    def test_phi_syngas_negative_raises(self):
        with pytest.raises(ValueError):
            gasification_efficiency(1.0, -0.1)


# ===========================================================================
# thermochemical.py — TestSolvolysisRate
# ===========================================================================

class TestSolvolysisRate:
    def test_higher_phi_solvent_higher_rate(self):
        k1 = solvolysis_rate(1.0, phi_solvent=1.0)
        k2 = solvolysis_rate(1.0, phi_solvent=2.0)
        assert k2 > k1

    def test_higher_T_higher_rate(self):
        k1 = solvolysis_rate(1.0, phi_solvent=1.0)
        k2 = solvolysis_rate(2.0, phi_solvent=1.0)
        assert k2 > k1

    def test_T_zero_raises(self):
        with pytest.raises(ValueError):
            solvolysis_rate(0.0, phi_solvent=1.0)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            solvolysis_rate(1.0, phi_solvent=0.0)

    def test_formula(self):
        k = solvolysis_rate(T=2.0, phi_solvent=2.0, A=1.0, E_a=4.0, k_B=1.0)
        assert np.isclose(k, np.exp(-1.0))


# ===========================================================================
# thermochemical.py — TestActivationEnergyChemicalRecycling
# ===========================================================================

class TestActivationEnergyChemicalRecycling:
    def test_zero_H(self):
        assert np.isclose(activation_energy_chemical_recycling(0.0, 1.0), 0.0)

    def test_formula(self):
        E = activation_energy_chemical_recycling(2.0, 3.0, lam=1.0)
        assert np.isclose(E, 0.5 * 1.0 * 9.0 * 4.0)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            activation_energy_chemical_recycling(1.0, 0.0)

    def test_lam_zero_raises(self):
        with pytest.raises(ValueError):
            activation_energy_chemical_recycling(1.0, 1.0, lam=0.0)


# ===========================================================================
# thermochemical.py — TestBFieldPhaseBoundary
# ===========================================================================

class TestBFieldPhaseBoundary:
    def test_basic(self):
        B = b_field_phase_boundary(3.0, 1.0)
        assert np.isclose(B, np.sqrt(4.0))

    def test_small_difference(self):
        B = b_field_phase_boundary(1.01, 1.0)
        assert np.isclose(B, np.sqrt(0.02))

    def test_solid_le_liquid_raises(self):
        with pytest.raises(ValueError):
            b_field_phase_boundary(1.0, 2.0)

    def test_equal_raises(self):
        with pytest.raises(ValueError):
            b_field_phase_boundary(1.0, 1.0)

    def test_positive(self):
        assert b_field_phase_boundary(2.0, 1.0) > 0.0


# ===========================================================================
# thermochemical.py — TestSyngasPhi
# ===========================================================================

class TestSyngasPhi:
    def test_pure_H2(self):
        phi = syngas_phi(1.0, 0.0)
        assert np.isclose(phi, 1.2)

    def test_pure_CO(self):
        phi = syngas_phi(0.0, 1.0)
        assert np.isclose(phi, 0.9)

    def test_50_50(self):
        phi = syngas_phi(0.5, 0.5)
        assert np.isclose(phi, 0.5 * 1.2 + 0.5 * 0.9)

    def test_fractions_sum_gt_one_raises(self):
        with pytest.raises(ValueError):
            syngas_phi(0.7, 0.6)

    def test_negative_H2_raises(self):
        with pytest.raises(ValueError):
            syngas_phi(-0.1, 0.5)

    def test_negative_CO_raises(self):
        with pytest.raises(ValueError):
            syngas_phi(0.5, -0.1)

    def test_zero_mix(self):
        assert np.isclose(syngas_phi(0.0, 0.0), 0.0)


# ===========================================================================
# thermochemical.py — TestThermalCrackingThreshold
# ===========================================================================

class TestThermalCrackingThreshold:
    def test_formula(self):
        V = thermal_cracking_threshold(4.0, 2.0)
        assert np.isclose(V, 2.0)

    def test_higher_phi_lower_barrier(self):
        V1 = thermal_cracking_threshold(4.0, 1.0)
        V2 = thermal_cracking_threshold(4.0, 2.0)
        assert V1 > V2

    def test_V_zero_raises(self):
        with pytest.raises(ValueError):
            thermal_cracking_threshold(0.0, 1.0)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            thermal_cracking_threshold(1.0, 0.0)


# ===========================================================================
# thermochemical.py — TestCo2ReductionFactor
# ===========================================================================

class TestCo2ReductionFactor:
    def test_perfect_recovery(self):
        assert np.isclose(co2_reduction_factor(2.0, 2.0), 0.0)

    def test_no_recovery(self):
        assert np.isclose(co2_reduction_factor(0.0, 2.0), 1.0)

    def test_partial(self):
        f = co2_reduction_factor(1.0, 2.0)
        assert np.isclose(f, 0.5)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            co2_reduction_factor(1.0, 0.0)

    def test_phi_recovery_negative_raises(self):
        with pytest.raises(ValueError):
            co2_reduction_factor(-0.1, 2.0)

    def test_clamped_zero(self):
        assert co2_reduction_factor(5.0, 2.0) == 0.0


# ===========================================================================
# thermochemical.py — TestChemicalRecyclingCop
# ===========================================================================

class TestChemicalRecyclingCop:
    def test_cop_greater_than_one(self):
        cop = chemical_recycling_cop(1.0, 2.0)
        assert cop > 1.0

    def test_cop_equal_one(self):
        assert np.isclose(chemical_recycling_cop(1.0, 1.0), 1.0)

    def test_cop_less_than_one(self):
        assert chemical_recycling_cop(2.0, 1.0) < 1.0

    def test_energy_in_zero_raises(self):
        with pytest.raises(ValueError):
            chemical_recycling_cop(0.0, 1.0)

    def test_energy_recovered_zero(self):
        assert np.isclose(chemical_recycling_cop(1.0, 0.0), 0.0)

    def test_energy_negative_raises(self):
        with pytest.raises(ValueError):
            chemical_recycling_cop(1.0, -1.0)


# ===========================================================================
# thermochemical.py — TestMonomerPurity
# ===========================================================================

class TestMonomerPurity:
    def test_perfect(self):
        assert np.isclose(monomer_purity(2.0, 2.0), 1.0)

    def test_zero_recovery(self):
        assert np.isclose(monomer_purity(0.0, 2.0), 0.0)

    def test_clamped_at_one(self):
        assert np.isclose(monomer_purity(3.0, 2.0), 1.0)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            monomer_purity(1.0, 0.0)

    def test_phi_recovered_negative_raises(self):
        with pytest.raises(ValueError):
            monomer_purity(-0.1, 2.0)


# ===========================================================================
# entropy_ledger.py — TestProductionEntropy
# ===========================================================================

class TestProductionEntropy:
    def test_same_phi_zero_entropy(self):
        S = production_entropy(1.0, 1.0)
        assert np.isclose(S, 0.0)

    def test_higher_product_positive(self):
        S = production_entropy(1.0, np.e)
        assert np.isclose(S, 1.0)

    def test_n_steps_scales(self):
        S1 = production_entropy(1.0, 2.0, n_steps=1)
        S2 = production_entropy(1.0, 2.0, n_steps=3)
        assert np.isclose(S2, 3.0 * S1)

    def test_phi_raw_zero_raises(self):
        with pytest.raises(ValueError):
            production_entropy(0.0, 1.0)

    def test_phi_product_zero_raises(self):
        with pytest.raises(ValueError):
            production_entropy(1.0, 0.0)

    def test_n_steps_zero_raises(self):
        with pytest.raises(ValueError):
            production_entropy(1.0, 2.0, n_steps=0)


# ===========================================================================
# entropy_ledger.py — TestUsePhasePhi
# ===========================================================================

class TestUsePhasePhi:
    def test_zero_time(self):
        assert np.isclose(use_phase_phi(2.0, 0.0, 0.1), 2.0)

    def test_decay(self):
        phi = use_phase_phi(1.0, 1.0, 1.0)
        assert np.isclose(phi, np.exp(-1.0))

    def test_long_use(self):
        phi = use_phase_phi(1.0, 100.0, 1.0)
        assert phi < 1e-30

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            use_phase_phi(0.0, 1.0, 0.1)

    def test_t_negative_raises(self):
        with pytest.raises(ValueError):
            use_phase_phi(1.0, -1.0, 0.1)

    def test_decay_rate_zero_raises(self):
        with pytest.raises(ValueError):
            use_phase_phi(1.0, 1.0, 0.0)


# ===========================================================================
# entropy_ledger.py — TestRecyclingEntropyCost
# ===========================================================================

class TestRecyclingEntropyCost:
    def test_same_phi_zero_cost(self):
        assert np.isclose(recycling_entropy_cost(1.0, 1.0), 0.0)

    def test_symmetric_about_ratio(self):
        c1 = recycling_entropy_cost(1.0, 2.0)
        c2 = recycling_entropy_cost(2.0, 1.0)
        assert np.isclose(c1, c2)

    def test_double_phi(self):
        c = recycling_entropy_cost(1.0, 2.0)
        assert np.isclose(c, np.log(2.0))

    def test_phi_waste_zero_raises(self):
        with pytest.raises(ValueError):
            recycling_entropy_cost(0.0, 1.0)

    def test_phi_recycled_zero_raises(self):
        with pytest.raises(ValueError):
            recycling_entropy_cost(1.0, 0.0)


# ===========================================================================
# entropy_ledger.py — TestLandfillEntropyRate
# ===========================================================================

class TestLandfillEntropyRate:
    def test_formula(self):
        rate = landfill_entropy_rate(2.0, 0.5)
        assert np.isclose(rate, 1.0)

    def test_scales_with_phi(self):
        r1 = landfill_entropy_rate(1.0, 1.0)
        r2 = landfill_entropy_rate(2.0, 1.0)
        assert np.isclose(r2, 2.0 * r1)

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            landfill_entropy_rate(0.0, 1.0)

    def test_k_zero_raises(self):
        with pytest.raises(ValueError):
            landfill_entropy_rate(1.0, 0.0)


# ===========================================================================
# entropy_ledger.py — TestTrueRecyclingEfficiency
# ===========================================================================

class TestTrueRecyclingEfficiency:
    def test_perfect_recycling(self):
        assert np.isclose(true_recycling_efficiency(2.0, 0.5, 2.0), 1.0)

    def test_no_improvement(self):
        assert np.isclose(true_recycling_efficiency(0.5, 0.5, 2.0), 0.0)

    def test_partial(self):
        eta = true_recycling_efficiency(1.0, 0.0, 2.0)
        assert np.isclose(eta, 0.5)

    def test_phi_virgin_le_waste_raises(self):
        with pytest.raises(ValueError):
            true_recycling_efficiency(1.0, 2.0, 1.5)

    def test_negative_efficiency_possible(self):
        eta = true_recycling_efficiency(0.0, 0.5, 2.0)
        assert eta < 0.0


# ===========================================================================
# entropy_ledger.py — TestLifecyclePhiTrace
# ===========================================================================

class TestLifecyclePhiTrace:
    def test_no_steps(self):
        trace = lifecycle_phi_trace(1.0, [])
        assert trace == [1.0]

    def test_mfg_step(self):
        trace = lifecycle_phi_trace(1.0, [("mfg", 2.0)])
        assert np.isclose(trace[-1], 2.0)

    def test_use_step(self):
        trace = lifecycle_phi_trace(1.0, [("use", 1.0)])
        assert np.isclose(trace[-1], np.exp(-1.0))

    def test_recycle_step(self):
        trace = lifecycle_phi_trace(2.0, [("recycle", 0.9)])
        assert np.isclose(trace[-1], 1.8)

    def test_full_lifecycle(self):
        steps = [("mfg", 2.0), ("use", 0.1), ("recycle", 0.8)]
        trace = lifecycle_phi_trace(1.0, steps)
        assert len(trace) == 4
        assert trace[0] == 1.0
        assert trace[1] == 2.0
        assert np.isclose(trace[2], 2.0 * np.exp(-0.1))
        assert np.isclose(trace[3], 2.0 * np.exp(-0.1) * 0.8)

    def test_phi_raw_zero_raises(self):
        with pytest.raises(ValueError):
            lifecycle_phi_trace(0.0, [("mfg", 2.0)])

    def test_negative_param_raises(self):
        with pytest.raises(ValueError):
            lifecycle_phi_trace(1.0, [("mfg", -1.0)])


# ===========================================================================
# entropy_ledger.py — TestAlignmentScore
# ===========================================================================

class TestAlignmentScore:
    def test_perfect_alignment(self):
        assert np.isclose(alignment_score(2.0, 2.0), 1.0)

    def test_zero_recycled(self):
        assert np.isclose(alignment_score(0.0, 2.0), 0.0)

    def test_half(self):
        assert np.isclose(alignment_score(1.0, 2.0), 0.5)

    def test_clamped_above_one(self):
        assert np.isclose(alignment_score(3.0, 2.0), 1.0)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            alignment_score(1.0, 0.0)

    def test_phi_recycled_negative_raises(self):
        with pytest.raises(ValueError):
            alignment_score(-0.1, 2.0)


# ===========================================================================
# entropy_ledger.py — TestMaterialEntropyDebt
# ===========================================================================

class TestMaterialEntropyDebt:
    def test_no_loss(self):
        assert np.isclose(material_entropy_debt(1.0, 1.0), 0.0)

    def test_quality_loss(self):
        assert np.isclose(material_entropy_debt(2.0, 1.0), 1.0)

    def test_quality_gain_negative_debt(self):
        assert np.isclose(material_entropy_debt(1.0, 2.0), -1.0)

    def test_phi_in_zero_raises(self):
        with pytest.raises(ValueError):
            material_entropy_debt(0.0, 1.0)

    def test_phi_out_negative_raises(self):
        with pytest.raises(ValueError):
            material_entropy_debt(1.0, -0.1)


# ===========================================================================
# entropy_ledger.py — TestInformationLossPerCycle
# ===========================================================================

class TestInformationLossPerCycle:
    def test_zero_cycles_no_loss(self):
        assert np.isclose(information_loss_per_cycle(2.0, 0, 0.1), 0.0)

    def test_one_cycle(self):
        il = information_loss_per_cycle(1.0, 1, 0.5)
        assert np.isclose(il, 1.0 - np.exp(-0.5))

    def test_increases_with_cycles(self):
        il1 = information_loss_per_cycle(1.0, 1, 0.1)
        il5 = information_loss_per_cycle(1.0, 5, 0.1)
        assert il5 > il1

    def test_asymptote_approaches_phi0(self):
        il = information_loss_per_cycle(1.0, 1000, 1.0)
        assert np.isclose(il, 1.0, atol=1e-6)

    def test_phi0_zero_raises(self):
        with pytest.raises(ValueError):
            information_loss_per_cycle(0.0, 1, 0.1)

    def test_negative_cycles_raises(self):
        with pytest.raises(ValueError):
            information_loss_per_cycle(1.0, -1, 0.1)


# ===========================================================================
# entropy_ledger.py — TestClosedLoopCriterion
# ===========================================================================

class TestClosedLoopCriterion:
    def test_perfect_closed_loop(self):
        assert closed_loop_criterion(2.0, 2.0)

    def test_within_tolerance(self):
        assert closed_loop_criterion(1.96, 2.0, tol=0.05)

    def test_outside_tolerance(self):
        assert not closed_loop_criterion(1.8, 2.0, tol=0.05)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            closed_loop_criterion(1.0, 0.0)

    def test_tol_negative_raises(self):
        with pytest.raises(ValueError):
            closed_loop_criterion(1.0, 2.0, tol=-0.1)

    def test_tol_gt_one_raises(self):
        with pytest.raises(ValueError):
            closed_loop_criterion(1.0, 2.0, tol=1.1)


# ===========================================================================
# entropy_ledger.py — TestOpenLoopEntropyBudget
# ===========================================================================

class TestOpenLoopEntropyBudget:
    def test_monotone_decreasing_chain(self):
        budget = open_loop_entropy_budget([3.0, 2.0, 1.0])
        assert np.isclose(budget, 2.0)

    def test_flat_chain_zero_budget(self):
        budget = open_loop_entropy_budget([1.0, 1.0, 1.0])
        assert np.isclose(budget, 0.0)

    def test_increasing_not_counted(self):
        budget = open_loop_entropy_budget([1.0, 2.0])
        assert np.isclose(budget, 0.0)

    def test_mixed(self):
        budget = open_loop_entropy_budget([3.0, 2.0, 2.5, 1.0])
        assert np.isclose(budget, 1.0 + 0.0 + 1.5)

    def test_too_short_raises(self):
        with pytest.raises(ValueError):
            open_loop_entropy_budget([1.0])

    def test_zero_in_sequence_raises(self):
        with pytest.raises(ValueError):
            open_loop_entropy_budget([1.0, 0.0, 0.5])


# ===========================================================================
# entropy_ledger.py — TestDowncyclingDepth
# ===========================================================================

class TestDowncyclingDepth:
    def test_closed_loop(self):
        assert np.isclose(downcycling_depth(2.0, 2.0, 0.0), 0.0)

    def test_landfill_equivalent(self):
        assert np.isclose(downcycling_depth(0.0, 2.0, 0.0), 1.0)

    def test_halfway(self):
        dd = downcycling_depth(1.0, 2.0, 0.0)
        assert np.isclose(dd, 0.5)

    def test_phi_virgin_le_landfill_raises(self):
        with pytest.raises(ValueError):
            downcycling_depth(1.0, 1.0, 1.0)

    def test_degradation_below_landfill(self):
        dd = downcycling_depth(-0.5, 2.0, 0.0)
        assert dd > 1.0


# ===========================================================================
# Integration: full lifecycle scenario
# ===========================================================================

class TestFullLifecycleScenario:
    """End-to-end scenario: PET bottle lifecycle with the manifold ledger."""

    PHI_VIRGIN   = 2.0   # virgin PET
    PHI_LANDFILL = 0.1   # degraded landfill PET

    def test_mechanical_recycling_downcycles(self):
        phi_mech = cycle_quality_loss(self.PHI_VIRGIN, n_cycles=5, alpha=0.15)
        ri = recyclability_index(phi_mech, self.PHI_VIRGIN)
        score = alignment_score(phi_mech, self.PHI_VIRGIN)
        assert ri < 1.0
        assert score < 1.0

    def test_chemical_recycling_can_close_loop(self):
        # Chemical recycling restores monomer φ
        purity = monomer_purity(1.9, self.PHI_VIRGIN)
        assert closed_loop_criterion(1.9, self.PHI_VIRGIN, tol=0.1)
        assert purity >= 0.9

    def test_contamination_prevents_sorting(self):
        B = np.array([0.8, 0.9, 1.1])
        B_thresh = 0.5
        mask = is_contaminated(B, B_thresh)
        assert np.all(mask)

    def test_landfill_is_worst_outcome(self):
        dd_landfill = downcycling_depth(
            self.PHI_LANDFILL, self.PHI_VIRGIN, self.PHI_LANDFILL
        )
        dd_mech = downcycling_depth(
            cycle_quality_loss(self.PHI_VIRGIN, 3, 0.1),
            self.PHI_VIRGIN,
            self.PHI_LANDFILL,
        )
        assert dd_landfill >= dd_mech

    def test_entropy_debt_accumulates_over_cycles(self):
        phi_after = [cycle_quality_loss(self.PHI_VIRGIN, n, 0.1) for n in range(6)]
        budget = open_loop_entropy_budget(phi_after)
        assert budget > 0.0

    def test_cop_criterion_for_chemical_recycling(self):
        cop = chemical_recycling_cop(energy_in=3.0, energy_recovered=4.5)
        assert cop > 1.0

    def test_co2_reduction_from_chemical_recycling(self):
        f = co2_reduction_factor(phi_recovery=1.8, phi_virgin=self.PHI_VIRGIN)
        assert f < 0.5  # significant CO2 reduction


# ===========================================================================
# producer_responsibility.py — TestPhiReturnForce
# ===========================================================================

class TestPhiReturnForce:
    def test_zero_at_equal_phi(self):
        f = phi_return_force(2.0, 2.0, r=1.0)
        assert np.isclose(f, 0.0)

    def test_decays_with_distance(self):
        f1 = phi_return_force(2.0, 1.0, r=1.0)
        f2 = phi_return_force(2.0, 1.0, r=2.0)
        assert f2 < f1

    def test_zero_distance(self):
        f = phi_return_force(2.0, 1.0, r=0.0)
        expected = 1.0 * (2.0 - 1.0) * np.exp(0.0)
        assert np.isclose(f, expected)

    def test_kappa_scales_linearly(self):
        f1 = phi_return_force(2.0, 1.0, r=1.0, kappa=1.0)
        f2 = phi_return_force(2.0, 1.0, r=1.0, kappa=3.0)
        assert np.isclose(f2, 3.0 * f1)

    def test_xi_controls_decay(self):
        # Longer xi → slower decay → larger force at same distance
        f_short = phi_return_force(2.0, 1.0, r=2.0, xi=1.0)
        f_long  = phi_return_force(2.0, 1.0, r=2.0, xi=5.0)
        assert f_long > f_short

    def test_larger_phi_gap_larger_force(self):
        f1 = phi_return_force(2.0, 1.5, r=1.0)
        f2 = phi_return_force(2.0, 0.5, r=1.0)
        assert f2 > f1

    def test_formula(self):
        f = phi_return_force(3.0, 1.0, r=2.0, kappa=2.0, xi=4.0)
        expected = 2.0 * (3.0 - 1.0) * np.exp(-2.0 / 4.0)
        assert np.isclose(f, expected)

    def test_non_negative(self):
        # Even when phi_waste > phi_origin the clamp keeps force ≥ 0
        f = phi_return_force(1.0, 1.5, r=0.0)
        assert f >= 0.0

    def test_phi_origin_zero_raises(self):
        with pytest.raises(ValueError):
            phi_return_force(0.0, 1.0, r=1.0)

    def test_phi_waste_negative_raises(self):
        with pytest.raises(ValueError):
            phi_return_force(2.0, -0.1, r=1.0)

    def test_r_negative_raises(self):
        with pytest.raises(ValueError):
            phi_return_force(2.0, 1.0, r=-0.5)

    def test_kappa_zero_raises(self):
        with pytest.raises(ValueError):
            phi_return_force(2.0, 1.0, r=1.0, kappa=0.0)

    def test_xi_zero_raises(self):
        with pytest.raises(ValueError):
            phi_return_force(2.0, 1.0, r=1.0, xi=0.0)

    def test_returns_float(self):
        assert isinstance(phi_return_force(2.0, 1.0, r=1.0), float)


# ===========================================================================
# producer_responsibility.py — TestProducerPhiDebt
# ===========================================================================

class TestProducerPhiDebt:
    def test_zero_a_score_full_debt(self):
        assert np.isclose(producer_phi_debt(2.0, 0.0), 2.0)

    def test_full_a_score_no_debt(self):
        assert np.isclose(producer_phi_debt(2.0, 1.0), 0.0)

    def test_partial_a_score(self):
        assert np.isclose(producer_phi_debt(2.0, 0.5), 1.0)

    def test_high_a_score_small_debt(self):
        d = producer_phi_debt(2.0, 0.95)
        assert np.isclose(d, 2.0 * 0.05)

    def test_scales_with_phi_virgin(self):
        d1 = producer_phi_debt(1.0, 0.3)
        d2 = producer_phi_debt(4.0, 0.3)
        assert np.isclose(d2, 4.0 * d1)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            producer_phi_debt(0.0, 0.5)

    def test_a_score_negative_raises(self):
        with pytest.raises(ValueError):
            producer_phi_debt(2.0, -0.1)

    def test_a_score_above_one_raises(self):
        with pytest.raises(ValueError):
            producer_phi_debt(2.0, 1.1)

    def test_returns_float(self):
        assert isinstance(producer_phi_debt(2.0, 0.5), float)

    def test_non_negative(self):
        assert producer_phi_debt(2.0, 0.99) >= 0.0


# ===========================================================================
# producer_responsibility.py — TestEprLevy
# ===========================================================================

class TestEprLevy:
    def test_equal_phi_zero_levy(self):
        # phi_waste == phi_virgin → no entropy gap → zero levy
        assert np.isclose(epr_levy(2.0, 2.0), 0.0)

    def test_higher_entropy_gap_higher_levy(self):
        L1 = epr_levy(2.0, 1.0)
        L2 = epr_levy(2.0, 0.5)
        assert L2 > L1

    def test_formula(self):
        L = epr_levy(np.e, 1.0, c_levy=1.0, k_B=1.0)
        assert np.isclose(L, 1.0)

    def test_c_levy_scales_linearly(self):
        L1 = epr_levy(2.0, 1.0, c_levy=1.0)
        L2 = epr_levy(2.0, 1.0, c_levy=3.0)
        assert np.isclose(L2, 3.0 * L1)

    def test_k_B_scales_linearly(self):
        L1 = epr_levy(2.0, 1.0, k_B=1.0)
        L2 = epr_levy(2.0, 1.0, k_B=2.0)
        assert np.isclose(L2, 2.0 * L1)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            epr_levy(0.0, 1.0)

    def test_phi_waste_zero_raises(self):
        with pytest.raises(ValueError):
            epr_levy(2.0, 0.0)

    def test_c_levy_negative_raises(self):
        with pytest.raises(ValueError):
            epr_levy(2.0, 1.0, c_levy=-1.0)

    def test_returns_non_negative(self):
        assert epr_levy(2.0, 1.0) >= 0.0

    def test_returns_float(self):
        assert isinstance(epr_levy(2.0, 1.0), float)

    def test_clamps_when_waste_exceeds_virgin(self):
        # phi_waste > phi_virgin is clamped → levy = 0
        assert np.isclose(epr_levy(1.0, 2.0), 0.0)


# ===========================================================================
# producer_responsibility.py — TestDepositRefundAmount
# ===========================================================================

class TestDepositRefundAmount:
    def test_zero_phi_gap_zero_deposit(self):
        assert np.isclose(deposit_refund_amount(2.0, 2.0), 0.0)

    def test_formula(self):
        d = deposit_refund_amount(3.0, 1.0, c_levy=2.0, collection_efficiency=0.5)
        assert np.isclose(d, 2.0 * 2.0 / 0.5)

    def test_lower_collection_higher_deposit(self):
        d1 = deposit_refund_amount(2.0, 1.0, collection_efficiency=0.9)
        d2 = deposit_refund_amount(2.0, 1.0, collection_efficiency=0.5)
        assert d2 > d1

    def test_perfect_collection_equals_phi_gap(self):
        d = deposit_refund_amount(3.0, 1.0, c_levy=1.0, collection_efficiency=1.0)
        assert np.isclose(d, 2.0)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            deposit_refund_amount(0.0, 1.0)

    def test_phi_waste_negative_raises(self):
        with pytest.raises(ValueError):
            deposit_refund_amount(2.0, -0.1)

    def test_c_levy_negative_raises(self):
        with pytest.raises(ValueError):
            deposit_refund_amount(2.0, 1.0, c_levy=-1.0)

    def test_collection_zero_raises(self):
        with pytest.raises(ValueError):
            deposit_refund_amount(2.0, 1.0, collection_efficiency=0.0)

    def test_collection_above_one_raises(self):
        with pytest.raises(ValueError):
            deposit_refund_amount(2.0, 1.0, collection_efficiency=1.1)

    def test_returns_non_negative(self):
        assert deposit_refund_amount(2.0, 1.0) >= 0.0

    def test_returns_float(self):
        assert isinstance(deposit_refund_amount(2.0, 1.0), float)


# ===========================================================================
# producer_responsibility.py — TestClosedLoopRadius
# ===========================================================================

class TestClosedLoopRadius:
    def test_no_phi_gap_returns_minus_one(self):
        assert closed_loop_radius(1.0, 1.0) == -1.0

    def test_waste_exceeds_origin_returns_minus_one(self):
        assert closed_loop_radius(1.0, 2.0) == -1.0

    def test_force_at_zero_below_F_min_returns_minus_one(self):
        # kappa * delta_phi < F_min
        r = closed_loop_radius(1.001, 1.0, kappa=1.0, xi=1.0, F_min=10.0)
        assert r == -1.0

    def test_positive_radius(self):
        r = closed_loop_radius(2.0, 0.0, kappa=1.0, xi=1.0, F_min=1e-3)
        assert r > 0.0

    def test_larger_xi_larger_radius(self):
        r1 = closed_loop_radius(2.0, 0.0, kappa=1.0, xi=1.0, F_min=0.01)
        r2 = closed_loop_radius(2.0, 0.0, kappa=1.0, xi=2.0, F_min=0.01)
        assert r2 > r1

    def test_formula(self):
        r = closed_loop_radius(3.0, 1.0, kappa=2.0, xi=5.0, F_min=0.1)
        expected = 5.0 * np.log(2.0 * 2.0 / 0.1)
        assert np.isclose(r, expected)

    def test_phi_origin_zero_raises(self):
        with pytest.raises(ValueError):
            closed_loop_radius(0.0, 0.0)

    def test_phi_waste_negative_raises(self):
        with pytest.raises(ValueError):
            closed_loop_radius(2.0, -0.1)

    def test_kappa_zero_raises(self):
        with pytest.raises(ValueError):
            closed_loop_radius(2.0, 1.0, kappa=0.0)

    def test_xi_zero_raises(self):
        with pytest.raises(ValueError):
            closed_loop_radius(2.0, 1.0, xi=0.0)

    def test_F_min_zero_raises(self):
        with pytest.raises(ValueError):
            closed_loop_radius(2.0, 1.0, F_min=0.0)


# ===========================================================================
# producer_responsibility.py — TestReturnProbability
# ===========================================================================

class TestReturnProbability:
    def test_zero_debt_certainty(self):
        assert np.isclose(return_probability(0.0, k_econ=1.0), 1.0)

    def test_large_debt_low_probability(self):
        p = return_probability(100.0, k_econ=1.0)
        assert p < 1e-10

    def test_higher_k_econ_higher_probability(self):
        p1 = return_probability(2.0, k_econ=1.0)
        p2 = return_probability(2.0, k_econ=5.0)
        assert p2 > p1

    def test_probability_in_unit_interval(self):
        for d in [0.0, 0.5, 1.0, 5.0]:
            p = return_probability(d, k_econ=1.0)
            assert 0.0 < p <= 1.0

    def test_formula(self):
        p = return_probability(2.0, k_econ=4.0)
        assert np.isclose(p, np.exp(-0.5))

    def test_phi_debt_negative_raises(self):
        with pytest.raises(ValueError):
            return_probability(-0.1)

    def test_k_econ_zero_raises(self):
        with pytest.raises(ValueError):
            return_probability(1.0, k_econ=0.0)

    def test_returns_float(self):
        assert isinstance(return_probability(1.0), float)


# ===========================================================================
# producer_responsibility.py — TestTakebackEfficiency
# ===========================================================================

class TestTakebackEfficiency:
    def test_perfect_both(self):
        assert np.isclose(takeback_efficiency(1.0, 1.0), 1.0)

    def test_zero_a_score(self):
        assert np.isclose(takeback_efficiency(0.0, 0.8), 0.0)

    def test_zero_collection(self):
        assert np.isclose(takeback_efficiency(0.9, 0.0), 0.0)

    def test_formula(self):
        assert np.isclose(takeback_efficiency(0.8, 0.7), 0.56)

    def test_in_unit_interval(self):
        eta = takeback_efficiency(0.7, 0.85)
        assert 0.0 <= eta <= 1.0

    def test_a_score_negative_raises(self):
        with pytest.raises(ValueError):
            takeback_efficiency(-0.1, 0.5)

    def test_a_score_above_one_raises(self):
        with pytest.raises(ValueError):
            takeback_efficiency(1.1, 0.5)

    def test_collection_negative_raises(self):
        with pytest.raises(ValueError):
            takeback_efficiency(0.5, -0.1)

    def test_collection_above_one_raises(self):
        with pytest.raises(ValueError):
            takeback_efficiency(0.5, 1.1)

    def test_returns_float(self):
        assert isinstance(takeback_efficiency(0.5, 0.5), float)


# ===========================================================================
# producer_responsibility.py — TestPhiOriginLabel
# ===========================================================================

class TestPhiOriginLabel:
    def test_in_range(self):
        lbl = phi_origin_label(2.0, 10, 1.5, phi_max=10.0)
        assert 0.0 <= lbl < 10.0

    def test_deterministic(self):
        lbl1 = phi_origin_label(2.0, 5, 3.0)
        lbl2 = phi_origin_label(2.0, 5, 3.0)
        assert lbl1 == lbl2

    def test_different_seeds_different_labels(self):
        # Use phi_virgin=1.7, n_w=3 so (1.7*3*seed) % 10 differs for seed=1 vs 2
        lbl1 = phi_origin_label(1.7, 3, 1.0)
        lbl2 = phi_origin_label(1.7, 3, 2.0)
        # Seeds differ → labels should generally differ
        assert not np.isclose(lbl1, lbl2)

    def test_different_n_w_different_labels(self):
        lbl1 = phi_origin_label(2.0, 3, 1.0)
        lbl2 = phi_origin_label(2.0, 7, 1.0)
        assert not np.isclose(lbl1, lbl2)

    def test_formula(self):
        phi_max = 10.0
        lbl = phi_origin_label(2.0, 5, 3.0, phi_max=phi_max)
        expected = (2.0 * 5 * 3.0) % phi_max
        assert np.isclose(lbl, expected)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            phi_origin_label(0.0, 5, 1.0)

    def test_n_w_zero_raises(self):
        with pytest.raises(ValueError):
            phi_origin_label(2.0, 0, 1.0)

    def test_producer_seed_zero_raises(self):
        with pytest.raises(ValueError):
            phi_origin_label(2.0, 5, 0.0)

    def test_phi_max_zero_raises(self):
        with pytest.raises(ValueError):
            phi_origin_label(2.0, 5, 1.0, phi_max=0.0)

    def test_returns_float(self):
        assert isinstance(phi_origin_label(2.0, 5, 1.0), float)


# ===========================================================================
# producer_responsibility.py — TestSystemicEntropySaved
# ===========================================================================

class TestSystemicEntropySaved:
    def test_epr_better_than_municipal_positive(self):
        ds = systemic_entropy_saved(1000, 2.0, 0.85, 0.50)
        assert ds > 0.0

    def test_equal_scores_zero_benefit(self):
        ds = systemic_entropy_saved(1000, 2.0, 0.60, 0.60)
        assert np.isclose(ds, 0.0)

    def test_epr_worse_negative(self):
        ds = systemic_entropy_saved(100, 2.0, 0.30, 0.70)
        assert ds < 0.0

    def test_formula(self):
        ds = systemic_entropy_saved(500, 4.0, 0.9, 0.6)
        assert np.isclose(ds, 500 * 4.0 * 0.3)

    def test_scales_with_n_products(self):
        ds1 = systemic_entropy_saved(100, 2.0, 0.8, 0.5)
        ds2 = systemic_entropy_saved(200, 2.0, 0.8, 0.5)
        assert np.isclose(ds2, 2.0 * ds1)

    def test_zero_products_zero_benefit(self):
        assert np.isclose(systemic_entropy_saved(0, 2.0, 0.9, 0.5), 0.0)

    def test_phi_virgin_zero_raises(self):
        with pytest.raises(ValueError):
            systemic_entropy_saved(100, 0.0, 0.8, 0.5)

    def test_n_products_negative_raises(self):
        with pytest.raises(ValueError):
            systemic_entropy_saved(-1, 2.0, 0.8, 0.5)

    def test_a_score_epr_negative_raises(self):
        with pytest.raises(ValueError):
            systemic_entropy_saved(100, 2.0, -0.1, 0.5)

    def test_a_score_municipal_above_one_raises(self):
        with pytest.raises(ValueError):
            systemic_entropy_saved(100, 2.0, 0.8, 1.1)

    def test_returns_float(self):
        assert isinstance(systemic_entropy_saved(10, 2.0, 0.8, 0.5), float)


# ===========================================================================
# producer_responsibility.py — TestLifecycleReturnIncentive
# ===========================================================================

class TestLifecycleReturnIncentive:
    def test_single_element_zero_incentive(self):
        result = lifecycle_return_incentive([2.0])
        assert result == [0.0]

    def test_strictly_increasing_phi_zero_incentive(self):
        # No φ loss → no levy
        result = lifecycle_return_incentive([1.0, 2.0, 3.0])
        assert all(np.isclose(x, 0.0) for x in result)

    def test_strictly_decreasing_phi(self):
        result = lifecycle_return_incentive([3.0, 2.0, 1.0], c_levy=1.0)
        assert np.isclose(result[0], 0.0)
        assert np.isclose(result[1], 1.0)
        assert np.isclose(result[2], 1.0)

    def test_mixed_trace(self):
        # [1.0, 3.0, 2.0] → losses at step 2 (1.0), zero at step 1
        result = lifecycle_return_incentive([1.0, 3.0, 2.0], c_levy=2.0)
        assert np.isclose(result[0], 0.0)
        assert np.isclose(result[1], 0.0)   # increase: no levy
        assert np.isclose(result[2], 2.0)   # decrease of 1.0 × c_levy=2.0

    def test_c_levy_scales_linearly(self):
        r1 = lifecycle_return_incentive([3.0, 1.0], c_levy=1.0)
        r2 = lifecycle_return_incentive([3.0, 1.0], c_levy=5.0)
        assert np.isclose(r2[1], 5.0 * r1[1])

    def test_length_preserved(self):
        trace = [2.0, 1.8, 1.5, 0.9]
        result = lifecycle_return_incentive(trace)
        assert len(result) == len(trace)

    def test_first_element_always_zero(self):
        result = lifecycle_return_incentive([5.0, 1.0, 0.5])
        assert np.isclose(result[0], 0.0)

    def test_empty_trace_raises(self):
        with pytest.raises(ValueError):
            lifecycle_return_incentive([])

    def test_phi_zero_in_trace_raises(self):
        with pytest.raises(ValueError):
            lifecycle_return_incentive([2.0, 0.0, 1.0])

    def test_c_levy_negative_raises(self):
        with pytest.raises(ValueError):
            lifecycle_return_incentive([2.0, 1.0], c_levy=-1.0)

    def test_returns_list(self):
        result = lifecycle_return_incentive([2.0, 1.0])
        assert isinstance(result, list)


# ===========================================================================
# producer_responsibility.py — TestIntegration
# ===========================================================================

class TestProducerResponsibilityIntegration:
    """End-to-end scenarios combining multiple functions."""

    PHI_VIRGIN = 2.0
    PHI_WASTE  = 0.4

    def test_deposit_covers_epr_levy_at_full_collection(self):
        # If collection_efficiency = 1, deposit should equal φ-gap × c_levy
        deposit = deposit_refund_amount(
            self.PHI_VIRGIN, self.PHI_WASTE, c_levy=1.0, collection_efficiency=1.0
        )
        assert np.isclose(deposit, self.PHI_VIRGIN - self.PHI_WASTE)

    def test_high_a_score_clears_debt(self):
        debt = producer_phi_debt(self.PHI_VIRGIN, a_score=0.97)
        assert debt < 0.1

    def test_levy_positive_when_waste_below_virgin(self):
        L = epr_levy(self.PHI_VIRGIN, self.PHI_WASTE)
        assert L > 0.0

    def test_return_force_positive_and_finite(self):
        f = phi_return_force(self.PHI_VIRGIN, self.PHI_WASTE, r=5.0)
        assert np.isfinite(f) and f > 0.0

    def test_epr_outperforms_municipal_entropy(self):
        ds = systemic_entropy_saved(10_000, self.PHI_VIRGIN, 0.88, 0.45)
        assert ds > 0.0

    def test_lifecycle_incentive_sums_to_total_levy(self):
        trace = [self.PHI_VIRGIN, 1.6, 1.0, self.PHI_WASTE]
        c_levy = 2.0
        incentives = lifecycle_return_incentive(trace, c_levy=c_levy)
        total = sum(incentives)
        # Total levy should equal c_levy × total φ-loss across chain
        phi_loss = sum(max(trace[i] - trace[i + 1], 0.0) for i in range(len(trace) - 1))
        assert np.isclose(total, c_levy * phi_loss)

    def test_takeback_vs_return_probability_consistency(self):
        a_score = 0.85
        collect  = 0.75
        eta = takeback_efficiency(a_score, collect)
        debt = producer_phi_debt(self.PHI_VIRGIN, a_score * collect)
        # Higher take-back efficiency → lower remaining debt → higher return prob
        p = return_probability(debt, k_econ=1.0)
        assert eta > 0.0
        assert 0.0 < p <= 1.0
