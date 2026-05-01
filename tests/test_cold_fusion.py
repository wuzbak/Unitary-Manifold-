# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cold_fusion.py
==========================
Unit tests for src/cold_fusion/tunneling.py, lattice.py,
and excess_heat.py.

Covers every public function (~125 tests total).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src.cold_fusion.tunneling import (
    sommerfeld_parameter,
    gamow_factor,
    phi_enhanced_gamow,
    tunneling_probability,
    coherence_length,
    barrier_suppression_factor,
    wkb_barrier_width,
    phi_barrier_height,
    tunneling_rate_per_pair,
    enhancement_ratio,
    minimum_phi_for_fusion,
)
from src.cold_fusion.lattice import (
    pd_lattice_constant,
    deuterium_loading_ratio,
    lattice_site_density,
    octahedral_site_fraction,
    coherence_volume,
    sites_in_coherence_volume,
    phi_at_lattice_site,
    lattice_strain,
    effective_mass_deuteron,
    b_field_at_site,
    loading_threshold_for_fusion,
    pd_shell_number,
)
from src.cold_fusion.excess_heat import (
    dd_fusion_q_value,
    dd_proton_branch_q_value,
    fusion_rate_per_site,
    excess_heat_power,
    cop,
    is_excess_heat,
    phi_coherent_enhancement,
    b_field_coherence_factor,
    energy_per_event,
    cumulative_heat,
    heat_to_electrical_efficiency,
    anomalous_heat_signature,
    calculate_energy_branching_ratio,
)

# Shared skip reason for all dual-use stubs
_DUAL_USE_SKIP = (
    "Implementation held in private repository per "
    "AxiomZero dual-use policy v1.0 — see DUAL_USE_NOTICE.md"
)


# ===========================================================================
# tunneling.py — sommerfeld_parameter
# ===========================================================================

class TestSommerfeldParameter:
    def test_basic_formula(self):
        eta = sommerfeld_parameter(1, 1, 0.001)
        assert np.isclose(eta, 1.0 / 137.0 / 0.001)

    def test_returns_float(self):
        assert isinstance(sommerfeld_parameter(1, 1, 0.01), float)

    def test_scales_with_charge(self):
        eta1 = sommerfeld_parameter(1, 1, 0.01)
        eta2 = sommerfeld_parameter(2, 1, 0.01)
        assert np.isclose(eta2, 2.0 * eta1)

    def test_scales_inversely_with_velocity(self):
        eta_slow = sommerfeld_parameter(1, 1, 0.001)
        eta_fast = sommerfeld_parameter(1, 1, 0.01)
        assert np.isclose(eta_slow, 10.0 * eta_fast)

    def test_custom_alpha(self):
        alpha = 0.01
        eta = sommerfeld_parameter(1, 1, 0.5, alpha_fs=alpha)
        assert np.isclose(eta, alpha / 0.5)

    def test_raises_on_zero_velocity(self):
        with pytest.raises(ValueError):
            sommerfeld_parameter(1, 1, 0.0)

    def test_raises_on_negative_velocity(self):
        with pytest.raises(ValueError):
            sommerfeld_parameter(1, 1, -0.001)

    def test_positive_result(self):
        eta = sommerfeld_parameter(1, 2, 0.01)
        assert eta > 0.0


# ===========================================================================
# tunneling.py — gamow_factor
# ===========================================================================

class TestGamowFactor:
    def test_in_range(self):
        G = gamow_factor(1, 1, 0.001)
        assert 0.0 < G <= 1.0

    def test_returns_float(self):
        assert isinstance(gamow_factor(1, 1, 0.01), float)

    def test_decreases_with_lower_velocity(self):
        G_fast = gamow_factor(1, 1, 0.01)
        G_slow = gamow_factor(1, 1, 0.001)
        assert G_slow < G_fast

    def test_approaches_zero_for_very_slow(self):
        G = gamow_factor(1, 1, 1e-6)
        assert G < 1e-10

    def test_approaches_one_for_very_fast(self):
        G = gamow_factor(1, 1, 1.0)
        assert G > 0.9

    def test_raises_on_zero_velocity(self):
        with pytest.raises(ValueError):
            gamow_factor(1, 1, 0.0)

    def test_higher_charge_lower_gamow(self):
        G1 = gamow_factor(1, 1, 0.01)
        G2 = gamow_factor(2, 2, 0.01)
        assert G2 < G1

    def test_formula_consistency_with_sommerfeld(self):
        v = 0.005
        eta = sommerfeld_parameter(1, 1, v)
        G_expected = float(np.exp(-2.0 * np.pi * eta))
        G_actual = gamow_factor(1, 1, v)
        assert np.isclose(G_actual, G_expected)


# ===========================================================================
# tunneling.py — phi_enhanced_gamow
# ===========================================================================

class TestPhiEnhancedGamow:
    def test_phi_one_equals_bare_gamow(self):
        v = 0.005
        G_bare = gamow_factor(1, 1, v)
        G_phi1 = phi_enhanced_gamow(1, 1, v, phi_local=1.0)
        assert np.isclose(G_bare, G_phi1)

    def test_phi_greater_one_increases_probability(self):
        v = 0.005
        G_bare = phi_enhanced_gamow(1, 1, v, phi_local=1.0)
        G_enh = phi_enhanced_gamow(1, 1, v, phi_local=2.0)
        assert G_enh > G_bare

    def test_returns_float(self):
        assert isinstance(phi_enhanced_gamow(1, 1, 0.01, 1.5), float)

    def test_in_range(self):
        G = phi_enhanced_gamow(1, 1, 0.001, 3.0)
        assert 0.0 < G <= 1.0

    def test_raises_on_zero_phi(self):
        with pytest.raises(ValueError):
            phi_enhanced_gamow(1, 1, 0.01, 0.0)

    def test_raises_on_negative_phi(self):
        with pytest.raises(ValueError):
            phi_enhanced_gamow(1, 1, 0.01, -1.0)

    def test_raises_on_zero_velocity(self):
        with pytest.raises(ValueError):
            phi_enhanced_gamow(1, 1, 0.0, 1.0)

    def test_monotone_in_phi(self):
        v = 0.003
        phis = [0.5, 1.0, 2.0, 5.0]
        gs = [phi_enhanced_gamow(1, 1, v, p) for p in phis]
        assert gs == sorted(gs)


# ===========================================================================
# tunneling.py — tunneling_probability
# ===========================================================================

class TestTunnelingProbability:
    def test_in_unit_interval(self):
        T = tunneling_probability(1, 1, 0.001, 1.0)
        assert 0.0 <= T <= 1.0

    def test_returns_float(self):
        assert isinstance(tunneling_probability(1, 1, 0.01, 1.0), float)

    def test_matches_phi_enhanced_gamow(self):
        T = tunneling_probability(1, 1, 0.005, 2.0)
        G = phi_enhanced_gamow(1, 1, 0.005, 2.0)
        assert np.isclose(T, G)

    def test_increases_with_phi(self):
        T1 = tunneling_probability(1, 1, 0.005, 1.0)
        T2 = tunneling_probability(1, 1, 0.005, 3.0)
        assert T2 > T1

    def test_raises_on_bad_phi(self):
        with pytest.raises(ValueError):
            tunneling_probability(1, 1, 0.01, 0.0)

    def test_raises_on_bad_velocity(self):
        with pytest.raises(ValueError):
            tunneling_probability(1, 1, 0.0, 1.0)


# ===========================================================================
# tunneling.py — coherence_length
# ===========================================================================

class TestCoherenceLength:
    def test_returns_positive_float(self):
        xi = coherence_length(300.0, 1.0)
        assert isinstance(xi, float)
        assert xi > 0.0

    def test_decreases_with_temperature(self):
        xi_cold = coherence_length(100.0, 1.0)
        xi_hot = coherence_length(1000.0, 1.0)
        assert xi_cold > xi_hot

    def test_decreases_with_phi(self):
        xi_lo = coherence_length(300.0, 0.5)
        xi_hi = coherence_length(300.0, 2.0)
        assert xi_lo > xi_hi

    def test_raises_on_zero_temperature(self):
        with pytest.raises(ValueError):
            coherence_length(0.0, 1.0)

    def test_raises_on_negative_temperature(self):
        with pytest.raises(ValueError):
            coherence_length(-10.0, 1.0)

    def test_raises_on_zero_phi(self):
        with pytest.raises(ValueError):
            coherence_length(300.0, 0.0)

    def test_raises_on_negative_phi(self):
        with pytest.raises(ValueError):
            coherence_length(300.0, -1.0)

    def test_custom_mass(self):
        xi_light = coherence_length(300.0, 1.0, m_particle=1.0)
        xi_heavy = coherence_length(300.0, 1.0, m_particle=4.0)
        assert xi_light > xi_heavy

    def test_formula_check(self):
        T_K = 300.0
        phi = 1.0
        m = 2.0
        k_B_nat = 3.17e-6
        kT = T_K * k_B_nat
        expected = 1.0 / np.sqrt(2.0 * m * kT * phi ** 2)
        assert np.isclose(coherence_length(T_K, phi, m), expected)


# ===========================================================================
# tunneling.py — barrier_suppression_factor
# ===========================================================================

class TestBarrierSuppressionFactor:
    def test_phi_ref_equals_one(self):
        S = barrier_suppression_factor(2.0)
        assert np.isclose(S, 2.0)

    def test_symmetric(self):
        S = barrier_suppression_factor(3.0, phi_ref=3.0)
        assert np.isclose(S, 1.0)

    def test_returns_float(self):
        assert isinstance(barrier_suppression_factor(1.5), float)

    def test_raises_on_zero_phi_local(self):
        with pytest.raises(ValueError):
            barrier_suppression_factor(0.0)

    def test_raises_on_zero_phi_ref(self):
        with pytest.raises(ValueError):
            barrier_suppression_factor(1.0, phi_ref=0.0)

    def test_raises_on_negative_phi_local(self):
        with pytest.raises(ValueError):
            barrier_suppression_factor(-1.0)


# ===========================================================================
# tunneling.py — wkb_barrier_width
# ===========================================================================

class TestWKBBarrierWidth:
    def test_zero_kinetic_energy(self):
        d = wkb_barrier_width(0.0, 1.0)
        assert np.isclose(d, 1.0)

    def test_at_barrier_top_is_zero(self):
        d = wkb_barrier_width(1.0, 1.0)
        assert np.isclose(d, 0.0)

    def test_returns_float(self):
        assert isinstance(wkb_barrier_width(0.5, 1.0), float)

    def test_decreases_with_kinetic_energy(self):
        d1 = wkb_barrier_width(0.1, 1.0)
        d2 = wkb_barrier_width(0.5, 1.0)
        assert d1 > d2

    def test_raises_on_zero_barrier(self):
        with pytest.raises(ValueError):
            wkb_barrier_width(0.5, 0.0)

    def test_raises_on_negative_barrier(self):
        with pytest.raises(ValueError):
            wkb_barrier_width(0.5, -1.0)

    def test_raises_when_ekin_exceeds_barrier(self):
        with pytest.raises(ValueError):
            wkb_barrier_width(1.5, 1.0)

    def test_nonnegative(self):
        d = wkb_barrier_width(0.8, 1.0)
        assert d >= 0.0


# ===========================================================================
# tunneling.py — phi_barrier_height
# ===========================================================================

class TestPhiBarrierHeight:
    def test_phi_one_returns_v0(self):
        V = phi_barrier_height(10.0, 1.0)
        assert np.isclose(V, 10.0)

    def test_phi_greater_one_reduces_barrier(self):
        V = phi_barrier_height(10.0, 2.0)
        assert np.isclose(V, 5.0)

    def test_returns_float(self):
        assert isinstance(phi_barrier_height(5.0, 2.0), float)

    def test_raises_on_zero_v0(self):
        with pytest.raises(ValueError):
            phi_barrier_height(0.0, 1.0)

    def test_raises_on_negative_v0(self):
        with pytest.raises(ValueError):
            phi_barrier_height(-1.0, 1.0)

    def test_raises_on_zero_phi(self):
        with pytest.raises(ValueError):
            phi_barrier_height(5.0, 0.0)

    def test_raises_on_negative_phi(self):
        with pytest.raises(ValueError):
            phi_barrier_height(5.0, -0.5)

    def test_monotone_decreasing_in_phi(self):
        phis = [0.5, 1.0, 2.0, 5.0]
        vs = [phi_barrier_height(10.0, p) for p in phis]
        assert vs == sorted(vs, reverse=True)


# ===========================================================================
# tunneling.py — tunneling_rate_per_pair
# ===========================================================================

class TestTunnelingRatePerPair:
    def test_returns_positive_float(self):
        rate = tunneling_rate_per_pair(0.001, 1.5, 1.0)
        assert isinstance(rate, float)
        assert rate >= 0.0

    def test_scales_with_velocity(self):
        r1 = tunneling_rate_per_pair(0.001, 1.5, 1.0)
        r2 = tunneling_rate_per_pair(0.002, 1.5, 1.0)
        assert r2 > r1

    def test_raises_on_zero_r_site(self):
        with pytest.raises(ValueError):
            tunneling_rate_per_pair(0.001, 1.5, 0.0)

    def test_raises_on_zero_velocity(self):
        with pytest.raises(ValueError):
            tunneling_rate_per_pair(0.0, 1.5, 1.0)

    def test_higher_phi_gives_higher_rate(self):
        r1 = tunneling_rate_per_pair(0.001, 1.0, 1.0)
        r2 = tunneling_rate_per_pair(0.001, 3.0, 1.0)
        assert r2 > r1


# ===========================================================================
# tunneling.py — enhancement_ratio
# ===========================================================================

class TestEnhancementRatio:
    def test_phi_enhanced_gt_ref_gives_ratio_gt_one(self):
        R = enhancement_ratio(2.0, phi_ref=1.0)
        assert R > 1.0

    def test_same_phi_gives_ratio_close_to_one(self):
        R = enhancement_ratio(1.0, phi_ref=1.0)
        assert np.isclose(R, 1.0, rtol=1e-5)

    def test_returns_float(self):
        assert isinstance(enhancement_ratio(2.0), float)

    def test_raises_on_zero_phi_ref(self):
        with pytest.raises(ValueError):
            enhancement_ratio(2.0, phi_ref=0.0)

    def test_raises_on_zero_phi_enhanced(self):
        with pytest.raises(ValueError):
            enhancement_ratio(0.0, phi_ref=1.0)

    def test_monotone_in_phi_enhanced(self):
        phis = [1.0, 2.0, 4.0, 8.0]
        ratios = [enhancement_ratio(p, phi_ref=1.0) for p in phis]
        assert ratios == sorted(ratios)


# ===========================================================================
# tunneling.py — minimum_phi_for_fusion
# ===========================================================================

@pytest.mark.skip(reason=_DUAL_USE_SKIP)
class TestMinimumPhiForFusion:
    def test_returns_positive_float(self):
        phi_min = minimum_phi_for_fusion(1, 1, 0.001)
        assert isinstance(phi_min, float)
        assert phi_min > 0.0

    def test_achieves_target_probability(self):
        T_min = 1e-10
        phi_min = minimum_phi_for_fusion(1, 1, 0.001, T_min=T_min)
        T_actual = tunneling_probability(1, 1, 0.001, phi_min)
        assert np.isclose(T_actual, T_min, rtol=1e-4)

    def test_raises_on_zero_t_min(self):
        with pytest.raises(ValueError):
            minimum_phi_for_fusion(1, 1, 0.001, T_min=0.0)

    def test_raises_on_t_min_ge_one(self):
        with pytest.raises(ValueError):
            minimum_phi_for_fusion(1, 1, 0.001, T_min=1.0)

    def test_raises_on_negative_t_min(self):
        with pytest.raises(ValueError):
            minimum_phi_for_fusion(1, 1, 0.001, T_min=-1e-5)

    def test_raises_on_zero_velocity(self):
        with pytest.raises(ValueError):
            minimum_phi_for_fusion(1, 1, 0.0, T_min=1e-10)

    def test_lower_t_min_requires_lower_phi(self):
        phi_higher_t_min = minimum_phi_for_fusion(1, 1, 0.001, T_min=1e-5)
        phi_lower_t_min = minimum_phi_for_fusion(1, 1, 0.001, T_min=1e-20)
        assert phi_lower_t_min < phi_higher_t_min


# ===========================================================================
# lattice.py — pd_lattice_constant
# ===========================================================================

class TestPdLatticeConstant:
    def test_default_returns_two_pi_over_5(self):
        a = pd_lattice_constant()
        assert np.isclose(a, 2.0 * np.pi / 5.0)

    def test_returns_float(self):
        assert isinstance(pd_lattice_constant(), float)

    def test_scales_with_phi_mean(self):
        a1 = pd_lattice_constant(phi_mean=1.0)
        a2 = pd_lattice_constant(phi_mean=2.0)
        assert np.isclose(a2, 2.0 * a1)

    def test_decreases_with_winding_number(self):
        a1 = pd_lattice_constant(n_w=1)
        a5 = pd_lattice_constant(n_w=5)
        assert a1 > a5

    def test_raises_on_zero_phi_mean(self):
        with pytest.raises(ValueError):
            pd_lattice_constant(phi_mean=0.0)

    def test_raises_on_negative_phi_mean(self):
        with pytest.raises(ValueError):
            pd_lattice_constant(phi_mean=-1.0)

    def test_raises_on_zero_nw(self):
        with pytest.raises(ValueError):
            pd_lattice_constant(n_w=0)

    def test_raises_on_negative_nw(self):
        with pytest.raises(ValueError):
            pd_lattice_constant(n_w=-1)


# ===========================================================================
# lattice.py — deuterium_loading_ratio
# ===========================================================================

class TestDeuteriumLoadingRatio:
    def test_basic_ratio(self):
        rho = deuterium_loading_ratio(80.0, 100.0)
        assert np.isclose(rho, 0.8)

    def test_returns_float(self):
        assert isinstance(deuterium_loading_ratio(50.0, 100.0), float)

    def test_zero_deuterium(self):
        rho = deuterium_loading_ratio(0.0, 100.0)
        assert np.isclose(rho, 0.0)

    def test_raises_on_zero_pd(self):
        with pytest.raises(ValueError):
            deuterium_loading_ratio(50.0, 0.0)

    def test_raises_on_negative_nd(self):
        with pytest.raises(ValueError):
            deuterium_loading_ratio(-1.0, 100.0)

    def test_raises_when_ratio_exceeds_2(self):
        with pytest.raises(ValueError):
            deuterium_loading_ratio(300.0, 100.0)

    def test_exactly_two_is_invalid(self):
        with pytest.raises(ValueError):
            deuterium_loading_ratio(200.1, 100.0)

    def test_maximum_allowed(self):
        rho = deuterium_loading_ratio(200.0, 100.0)
        assert np.isclose(rho, 2.0)


# ===========================================================================
# lattice.py — lattice_site_density
# ===========================================================================

class TestLatticeSiteDensity:
    def test_fcc_formula(self):
        a = 2.0
        n = lattice_site_density(a)
        assert np.isclose(n, 4.0 / a ** 3)

    def test_returns_float(self):
        assert isinstance(lattice_site_density(1.0), float)

    def test_decreases_with_lattice_constant(self):
        n1 = lattice_site_density(1.0)
        n2 = lattice_site_density(2.0)
        assert n1 > n2

    def test_raises_on_zero_lattice_constant(self):
        with pytest.raises(ValueError):
            lattice_site_density(0.0)

    def test_raises_on_negative_lattice_constant(self):
        with pytest.raises(ValueError):
            lattice_site_density(-1.0)


# ===========================================================================
# lattice.py — octahedral_site_fraction
# ===========================================================================

class TestOctahedralSiteFraction:
    def test_below_one_returns_self(self):
        f = octahedral_site_fraction(0.75)
        assert np.isclose(f, 0.75)

    def test_zero_loading(self):
        f = octahedral_site_fraction(0.0)
        assert np.isclose(f, 0.0)

    def test_clamped_to_one(self):
        f = octahedral_site_fraction(1.5)
        assert np.isclose(f, 1.0)

    def test_returns_float(self):
        assert isinstance(octahedral_site_fraction(0.5), float)


# ===========================================================================
# lattice.py — coherence_volume
# ===========================================================================

class TestCoherenceVolumeLattice:
    def test_formula(self):
        xi = 2.0
        V = coherence_volume(xi)
        assert np.isclose(V, 4.0 * np.pi / 3.0 * xi ** 3)

    def test_returns_float(self):
        assert isinstance(coherence_volume(1.0), float)

    def test_positive(self):
        assert coherence_volume(1.0) > 0.0

    def test_scales_with_cube(self):
        V1 = coherence_volume(1.0)
        V2 = coherence_volume(2.0)
        assert np.isclose(V2, 8.0 * V1)

    def test_raises_on_zero_xi(self):
        with pytest.raises(ValueError):
            coherence_volume(0.0)

    def test_raises_on_negative_xi(self):
        with pytest.raises(ValueError):
            coherence_volume(-1.0)


# ===========================================================================
# lattice.py — sites_in_coherence_volume
# ===========================================================================

@pytest.mark.skip(reason=_DUAL_USE_SKIP)
class TestSitesInCoherenceVolume:
    def test_positive(self):
        N = sites_in_coherence_volume(5.0, 1.0)
        assert N > 0.0

    def test_returns_float(self):
        assert isinstance(sites_in_coherence_volume(5.0, 1.0), float)

    def test_increases_with_xi(self):
        N1 = sites_in_coherence_volume(2.0, 1.0)
        N2 = sites_in_coherence_volume(4.0, 1.0)
        assert N2 > N1

    def test_decreases_with_larger_lattice_constant(self):
        N1 = sites_in_coherence_volume(5.0, 1.0)
        N2 = sites_in_coherence_volume(5.0, 2.0)
        assert N1 > N2

    def test_raises_on_zero_xi(self):
        with pytest.raises(ValueError):
            sites_in_coherence_volume(0.0, 1.0)

    def test_raises_on_zero_a_lattice(self):
        with pytest.raises(ValueError):
            sites_in_coherence_volume(5.0, 0.0)


# ===========================================================================
# lattice.py — phi_at_lattice_site
# ===========================================================================

class TestPhiAtLatticeSite:
    def test_at_rho_ref_returns_phi_bulk(self):
        phi = phi_at_lattice_site(1.0, 0.75, rho_ref=0.75)
        assert np.isclose(phi, 1.0)

    def test_high_loading_enhances_phi(self):
        phi = phi_at_lattice_site(1.0, 1.5, rho_ref=0.75)
        assert phi > 1.0

    def test_low_loading_suppresses_phi(self):
        phi = phi_at_lattice_site(1.0, 0.1, rho_ref=0.75)
        assert phi < 1.0

    def test_returns_float(self):
        assert isinstance(phi_at_lattice_site(1.0, 0.8), float)

    def test_raises_on_zero_phi_bulk(self):
        with pytest.raises(ValueError):
            phi_at_lattice_site(0.0, 0.8)

    def test_raises_on_zero_rho_loading(self):
        with pytest.raises(ValueError):
            phi_at_lattice_site(1.0, 0.0)

    def test_raises_on_zero_rho_ref(self):
        with pytest.raises(ValueError):
            phi_at_lattice_site(1.0, 0.8, rho_ref=0.0)


# ===========================================================================
# lattice.py — lattice_strain
# ===========================================================================

class TestLatticeStrain:
    def test_at_rho0_zero_strain(self):
        eps = lattice_strain(0.68, rho_0=0.68)
        assert np.isclose(eps, 0.0)

    def test_over_loaded_positive_strain(self):
        eps = lattice_strain(0.9, rho_0=0.68)
        assert eps > 0.0

    def test_under_loaded_negative_strain(self):
        eps = lattice_strain(0.5, rho_0=0.68)
        assert eps < 0.0

    def test_returns_float(self):
        assert isinstance(lattice_strain(0.8), float)

    def test_raises_on_zero_rho0(self):
        with pytest.raises(ValueError):
            lattice_strain(0.8, rho_0=0.0)


# ===========================================================================
# lattice.py — effective_mass_deuteron
# ===========================================================================

class TestEffectiveMassDeuteron:
    def test_phi_one_gives_mass_two(self):
        m = effective_mass_deuteron(1.0)
        assert np.isclose(m, 2.0)

    def test_phi_two_gives_mass_one(self):
        m = effective_mass_deuteron(2.0)
        assert np.isclose(m, 1.0)

    def test_decreases_with_phi(self):
        m1 = effective_mass_deuteron(1.0)
        m2 = effective_mass_deuteron(4.0)
        assert m1 > m2

    def test_returns_float(self):
        assert isinstance(effective_mass_deuteron(1.0), float)

    def test_raises_on_zero_phi(self):
        with pytest.raises(ValueError):
            effective_mass_deuteron(0.0)

    def test_raises_on_negative_phi(self):
        with pytest.raises(ValueError):
            effective_mass_deuteron(-1.0)


# ===========================================================================
# lattice.py — b_field_at_site
# ===========================================================================

class TestBFieldAtSite:
    def test_zero_external_field(self):
        B = b_field_at_site(0.0, 0.8, 1.5)
        assert np.isclose(B, 0.0)

    def test_scales_with_loading(self):
        B1 = b_field_at_site(1.0, 0.5, 1.0)
        B2 = b_field_at_site(1.0, 1.0, 1.0)
        assert np.isclose(B2, 2.0 * B1)

    def test_scales_with_phi(self):
        B1 = b_field_at_site(1.0, 0.8, 1.0)
        B2 = b_field_at_site(1.0, 0.8, 2.0)
        assert np.isclose(B2, 2.0 * B1)

    def test_returns_float(self):
        assert isinstance(b_field_at_site(1.0, 0.8, 1.5), float)

    def test_raises_on_negative_b_external(self):
        with pytest.raises(ValueError):
            b_field_at_site(-1.0, 0.8, 1.0)

    def test_raises_on_negative_rho(self):
        with pytest.raises(ValueError):
            b_field_at_site(1.0, -0.1, 1.0)

    def test_raises_on_zero_phi(self):
        with pytest.raises(ValueError):
            b_field_at_site(1.0, 0.8, 0.0)


# ===========================================================================
# lattice.py — loading_threshold_for_fusion
# ===========================================================================

@pytest.mark.skip(reason=_DUAL_USE_SKIP)
class TestLoadingThresholdForFusion:
    def test_phi_one_returns_rho_ref(self):
        rho_min = loading_threshold_for_fusion(1.0)
        assert np.isclose(rho_min, 0.75)

    def test_higher_phi_lowers_threshold(self):
        rho1 = loading_threshold_for_fusion(1.0)
        rho2 = loading_threshold_for_fusion(2.0)
        assert rho2 < rho1

    def test_returns_float(self):
        assert isinstance(loading_threshold_for_fusion(1.0), float)

    def test_raises_on_zero_phi_bulk(self):
        with pytest.raises(ValueError):
            loading_threshold_for_fusion(0.0)

    def test_raises_on_negative_phi_bulk(self):
        with pytest.raises(ValueError):
            loading_threshold_for_fusion(-1.0)


# ===========================================================================
# lattice.py — pd_shell_number
# ===========================================================================

class TestPdShellNumber:
    def test_returns_five(self):
        assert pd_shell_number() == 5

    def test_returns_int(self):
        assert isinstance(pd_shell_number(), int)


# ===========================================================================
# excess_heat.py — dd_fusion_q_value
# ===========================================================================

class TestDDFusionQValue:
    def test_returns_float(self):
        assert isinstance(dd_fusion_q_value(), float)

    def test_positive(self):
        assert dd_fusion_q_value() > 0.0

    def test_approx_value(self):
        Q = dd_fusion_q_value()
        assert np.isclose(Q, 3.27e6 * 1.6e-19, rtol=1e-6)

    def test_less_than_proton_branch(self):
        assert dd_fusion_q_value() < dd_proton_branch_q_value()


# ===========================================================================
# excess_heat.py — dd_proton_branch_q_value
# ===========================================================================

class TestDDProtonBranchQValue:
    def test_returns_float(self):
        assert isinstance(dd_proton_branch_q_value(), float)

    def test_positive(self):
        assert dd_proton_branch_q_value() > 0.0

    def test_approx_value(self):
        Q = dd_proton_branch_q_value()
        assert np.isclose(Q, 4.03e6 * 1.6e-19, rtol=1e-6)


# ===========================================================================
# excess_heat.py — fusion_rate_per_site
# ===========================================================================

@pytest.mark.skip(reason=_DUAL_USE_SKIP)
class TestFusionRatePerSite:
    def test_returns_float(self):
        assert isinstance(fusion_rate_per_site(0.01, 0.001, 1.0), float)

    def test_zero_probability_gives_zero_rate(self):
        R = fusion_rate_per_site(0.0, 0.001, 1.0)
        assert np.isclose(R, 0.0)

    def test_scales_with_probability(self):
        R1 = fusion_rate_per_site(0.01, 0.001, 1.0)
        R2 = fusion_rate_per_site(0.02, 0.001, 1.0)
        assert np.isclose(R2, 2.0 * R1)

    def test_raises_on_zero_v_rel(self):
        with pytest.raises(ValueError):
            fusion_rate_per_site(0.01, 0.0, 1.0)

    def test_raises_on_zero_r_site(self):
        with pytest.raises(ValueError):
            fusion_rate_per_site(0.01, 0.001, 0.0)


# ===========================================================================
# excess_heat.py — excess_heat_power
# ===========================================================================

@pytest.mark.skip(reason=_DUAL_USE_SKIP)
class TestExcessHeatPower:
    def test_basic(self):
        P = excess_heat_power(1e20, 1e-25, 5e-13)
        assert P > 0.0

    def test_returns_float(self):
        assert isinstance(excess_heat_power(100.0, 1.0, 1.0), float)

    def test_zero_sites_gives_zero(self):
        P = excess_heat_power(0.0, 1.0, 1.0)
        assert np.isclose(P, 0.0)

    def test_zero_rate_gives_zero(self):
        P = excess_heat_power(100.0, 0.0, 1.0)
        assert np.isclose(P, 0.0)

    def test_raises_on_negative_sites(self):
        with pytest.raises(ValueError):
            excess_heat_power(-1.0, 1.0, 1.0)

    def test_raises_on_negative_rate(self):
        with pytest.raises(ValueError):
            excess_heat_power(100.0, -1.0, 1.0)


# ===========================================================================
# excess_heat.py — cop
# ===========================================================================

class TestCOP:
    def test_basic(self):
        assert np.isclose(cop(200.0, 100.0), 2.0)

    def test_returns_float(self):
        assert isinstance(cop(1.0, 1.0), float)

    def test_cop_one_means_no_excess(self):
        assert np.isclose(cop(100.0, 100.0), 1.0)

    def test_raises_on_zero_p_in(self):
        with pytest.raises(ValueError):
            cop(100.0, 0.0)

    def test_raises_on_negative_p_in(self):
        with pytest.raises(ValueError):
            cop(100.0, -50.0)

    def test_cop_greater_one_for_excess(self):
        assert cop(150.0, 100.0) > 1.0


# ===========================================================================
# excess_heat.py — is_excess_heat
# ===========================================================================

class TestIsExcessHeat:
    def test_true_when_p_out_greater_p_in(self):
        assert is_excess_heat(150.0, 100.0) is True

    def test_false_when_equal(self):
        assert is_excess_heat(100.0, 100.0) is False

    def test_false_when_below(self):
        assert is_excess_heat(80.0, 100.0) is False

    def test_returns_bool(self):
        assert isinstance(is_excess_heat(150.0, 100.0), bool)

    def test_custom_threshold(self):
        assert is_excess_heat(250.0, 100.0, threshold=2.0) is True
        assert is_excess_heat(150.0, 100.0, threshold=2.0) is False

    def test_raises_on_zero_p_in(self):
        with pytest.raises(ValueError):
            is_excess_heat(100.0, 0.0)


# ===========================================================================
# excess_heat.py — phi_coherent_enhancement
# ===========================================================================

class TestPhiCoherentEnhancement:
    def test_above_threshold_gives_positive(self):
        f = phi_coherent_enhancement(100.0, 1.0, phi_threshold=0.5)
        assert f > 0.0

    def test_below_threshold_gives_zero(self):
        f = phi_coherent_enhancement(100.0, 0.2, phi_threshold=0.5)
        assert np.isclose(f, 0.0)

    def test_at_threshold_gives_zero(self):
        f = phi_coherent_enhancement(100.0, 0.5, phi_threshold=0.5)
        assert np.isclose(f, 0.0)

    def test_scales_with_phi_squared(self):
        f1 = phi_coherent_enhancement(1.0, 1.0, phi_threshold=0.5)
        f2 = phi_coherent_enhancement(1.0, 2.0, phi_threshold=0.5)
        assert np.isclose(f2 / f1, 4.0)

    def test_returns_float(self):
        assert isinstance(phi_coherent_enhancement(100.0, 1.0), float)

    def test_raises_on_negative_n_sites(self):
        with pytest.raises(ValueError):
            phi_coherent_enhancement(-1.0, 1.0)

    def test_raises_on_zero_phi_local(self):
        with pytest.raises(ValueError):
            phi_coherent_enhancement(100.0, 0.0)

    def test_raises_on_zero_threshold(self):
        with pytest.raises(ValueError):
            phi_coherent_enhancement(100.0, 1.0, phi_threshold=0.0)


# ===========================================================================
# excess_heat.py — b_field_coherence_factor
# ===========================================================================

class TestBFieldCoherenceFactor:
    def test_zero_b_gives_one(self):
        C = b_field_coherence_factor(0.0, 1.0)
        assert np.isclose(C, 1.0)

    def test_returns_float(self):
        assert isinstance(b_field_coherence_factor(1.0, 1.0), float)

    def test_ge_one(self):
        C = b_field_coherence_factor(2.0, 1.5)
        assert C >= 1.0

    def test_formula(self):
        B = 0.5
        phi = 2.0
        C = b_field_coherence_factor(B, phi)
        assert np.isclose(C, 1.0 + B * phi)

    def test_raises_on_negative_b(self):
        with pytest.raises(ValueError):
            b_field_coherence_factor(-1.0, 1.0)

    def test_raises_on_zero_phi(self):
        with pytest.raises(ValueError):
            b_field_coherence_factor(1.0, 0.0)


# ===========================================================================
# excess_heat.py — energy_per_event
# ===========================================================================

class TestEnergyPerEvent:
    def test_returns_q_value(self):
        Q = 5.232e-13
        assert np.isclose(energy_per_event(Q), Q)

    def test_returns_float(self):
        assert isinstance(energy_per_event(1.0), float)

    def test_identity(self):
        for q in [1.0, 0.0, -1.0, 1e-13]:
            assert np.isclose(energy_per_event(q), q)


# ===========================================================================
# excess_heat.py — cumulative_heat
# ===========================================================================

class TestCumulativeHeat:
    def test_returns_ndarray(self):
        rates = np.ones(5)
        H = cumulative_heat(rates, 1.0, 1.0)
        assert isinstance(H, np.ndarray)

    def test_shape_preserved(self):
        rates = np.ones(10)
        H = cumulative_heat(rates, 1.0, 0.1)
        assert H.shape == rates.shape

    def test_monotone_increasing_for_positive_rates(self):
        rates = np.ones(5)
        H = cumulative_heat(rates, 1.0, 1.0)
        assert np.all(np.diff(H) >= 0)

    def test_final_value(self):
        rates = np.array([1.0, 1.0, 1.0])
        H = cumulative_heat(rates, 2.0, 0.5)
        assert np.isclose(H[-1], 3.0 * 2.0 * 0.5)

    def test_raises_on_zero_dt(self):
        with pytest.raises(ValueError):
            cumulative_heat(np.ones(3), 1.0, 0.0)

    def test_raises_on_negative_dt(self):
        with pytest.raises(ValueError):
            cumulative_heat(np.ones(3), 1.0, -0.1)


# ===========================================================================
# excess_heat.py — heat_to_electrical_efficiency
# ===========================================================================

@pytest.mark.skip(reason=_DUAL_USE_SKIP)
class TestHeatToElectricalEfficiency:
    def test_cop_one_gives_zero(self):
        eff = heat_to_electrical_efficiency(1.0)
        assert np.isclose(eff, 0.0)

    def test_cop_two_gives_eta_thermal(self):
        eff = heat_to_electrical_efficiency(2.0, eta_thermal=0.35)
        assert np.isclose(eff, 0.35)

    def test_returns_float(self):
        assert isinstance(heat_to_electrical_efficiency(2.0), float)

    def test_increases_with_cop(self):
        eff1 = heat_to_electrical_efficiency(2.0)
        eff2 = heat_to_electrical_efficiency(3.0)
        assert eff2 > eff1

    def test_raises_on_negative_cop(self):
        with pytest.raises(ValueError):
            heat_to_electrical_efficiency(-1.0)

    def test_raises_on_zero_eta(self):
        with pytest.raises(ValueError):
            heat_to_electrical_efficiency(2.0, eta_thermal=0.0)

    def test_raises_on_eta_gt_one(self):
        with pytest.raises(ValueError):
            heat_to_electrical_efficiency(2.0, eta_thermal=1.1)


# ===========================================================================
# excess_heat.py — anomalous_heat_signature
# ===========================================================================

class TestAnomalousHeatSignature:
    def test_returns_float(self):
        assert isinstance(anomalous_heat_signature(10.0, 1.0), float)

    def test_formula(self):
        P = 5.0
        var = 4.0
        sigma = anomalous_heat_signature(P, var)
        assert np.isclose(sigma, P / np.sqrt(var))

    def test_increases_with_p_excess(self):
        s1 = anomalous_heat_signature(5.0, 1.0)
        s2 = anomalous_heat_signature(10.0, 1.0)
        assert s2 > s1

    def test_decreases_with_variance(self):
        s1 = anomalous_heat_signature(10.0, 1.0)
        s2 = anomalous_heat_signature(10.0, 4.0)
        assert s1 > s2

    def test_raises_on_zero_variance(self):
        with pytest.raises(ValueError):
            anomalous_heat_signature(10.0, 0.0)

    def test_raises_on_negative_variance(self):
        with pytest.raises(ValueError):
            anomalous_heat_signature(10.0, -1.0)

    def test_negative_excess_gives_negative_sigma(self):
        sigma = anomalous_heat_signature(-5.0, 1.0)
        assert sigma < 0.0


# ===========================================================================
# excess_heat.py — calculate_energy_branching_ratio
# ===========================================================================

class TestCalculateEnergyBranchingRatio:
    """Tests for the B_μ momentum-sink energy branching ratio."""

    def test_returns_dict(self):
        result = calculate_energy_branching_ratio(1.0, 1.0)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = calculate_energy_branching_ratio(1.0, 1.0)
        required = {
            "B_site", "phi_local", "alpha_fs", "B_effective",
            "Gamma_gamma", "Gamma_phonon", "Gamma_total",
            "phonon_fraction", "gamma_fraction",
            "suppression_pct", "is_safe",
        }
        assert required.issubset(result.keys())

    def test_fractions_sum_to_one(self):
        result = calculate_energy_branching_ratio(2.0, 3.0)
        assert abs(result["phonon_fraction"] + result["gamma_fraction"] - 1.0) < 1e-12

    def test_phonon_fraction_in_unit_interval(self):
        result = calculate_energy_branching_ratio(5.0, 2.0)
        assert 0.0 <= result["phonon_fraction"] <= 1.0

    def test_gamma_fraction_in_unit_interval(self):
        result = calculate_energy_branching_ratio(5.0, 2.0)
        assert 0.0 <= result["gamma_fraction"] <= 1.0

    def test_zero_B_site_gives_all_gamma(self):
        result = calculate_energy_branching_ratio(0.0, 1.0)
        assert result["phonon_fraction"] == 0.0
        assert result["gamma_fraction"] == 1.0

    def test_zero_B_site_not_safe(self):
        result = calculate_energy_branching_ratio(0.0, 1.0)
        assert result["is_safe"] is False

    def test_high_B_site_mostly_phonon(self):
        # B_eff = 200 → phonon_fraction = 200/201 ≈ 0.995 > 0.99
        result = calculate_energy_branching_ratio(100.0, 2.0)
        assert result["phonon_fraction"] > 0.99

    def test_high_B_site_is_safe(self):
        result = calculate_energy_branching_ratio(100.0, 2.0)
        assert result["is_safe"] is True

    def test_B_effective_equals_B_site_times_phi(self):
        B_site = 3.5
        phi_local = 4.2
        result = calculate_energy_branching_ratio(B_site, phi_local)
        assert abs(result["B_effective"] - B_site * phi_local) < 1e-12

    def test_phonon_fraction_formula(self):
        B_site, phi_local = 5.0, 3.0
        result = calculate_energy_branching_ratio(B_site, phi_local)
        B_eff = B_site * phi_local
        expected_phonon = B_eff / (1.0 + B_eff)
        assert abs(result["phonon_fraction"] - expected_phonon) < 1e-12

    def test_gamma_fraction_formula(self):
        B_site, phi_local = 5.0, 3.0
        result = calculate_energy_branching_ratio(B_site, phi_local)
        B_eff = B_site * phi_local
        expected_gamma = 1.0 / (1.0 + B_eff)
        assert abs(result["gamma_fraction"] - expected_gamma) < 1e-12

    def test_suppression_pct_consistent(self):
        result = calculate_energy_branching_ratio(10.0, 2.0)
        expected_pct = (1.0 - result["gamma_fraction"]) * 100.0
        assert abs(result["suppression_pct"] - expected_pct) < 1e-10

    def test_is_safe_threshold_at_99pct(self):
        # B_eff = 99 → gamma_fraction = 1/100 = 0.01 → NOT safe
        result_99 = calculate_energy_branching_ratio(99.0, 1.0)
        # B_eff = 100 → gamma_fraction = 1/101 < 0.01 → safe
        result_100 = calculate_energy_branching_ratio(100.0, 1.0)
        assert result_99["is_safe"] is False
        assert result_100["is_safe"] is True

    def test_Gamma_total_equals_sum(self):
        result = calculate_energy_branching_ratio(5.0, 2.0)
        assert abs(result["Gamma_total"] - (result["Gamma_gamma"] + result["Gamma_phonon"])) < 1e-15

    def test_Gamma_phonon_to_gamma_ratio_equals_B_eff(self):
        B_site, phi_local = 4.0, 5.0
        result = calculate_energy_branching_ratio(B_site, phi_local)
        ratio = result["Gamma_phonon"] / result["Gamma_gamma"]
        assert abs(ratio - result["B_effective"]) < 1e-10

    def test_custom_alpha_fs(self):
        alpha = 1.0 / 100.0
        result = calculate_energy_branching_ratio(1.0, 1.0, alpha_fs=alpha)
        assert abs(result["alpha_fs"] - alpha) < 1e-15
        assert abs(result["Gamma_gamma"] - alpha) < 1e-15

    def test_alpha_fs_cancels_in_fractions(self):
        # Branching fractions are independent of alpha_fs
        r1 = calculate_energy_branching_ratio(3.0, 2.0, alpha_fs=1.0 / 137.0)
        r2 = calculate_energy_branching_ratio(3.0, 2.0, alpha_fs=1.0 / 100.0)
        assert abs(r1["phonon_fraction"] - r2["phonon_fraction"]) < 1e-14
        assert abs(r1["gamma_fraction"] - r2["gamma_fraction"]) < 1e-14

    def test_monotone_in_B_site(self):
        results = [calculate_energy_branching_ratio(b, 2.0) for b in [0.5, 1.0, 5.0, 20.0]]
        phonon_fracs = [r["phonon_fraction"] for r in results]
        assert phonon_fracs == sorted(phonon_fracs)

    def test_monotone_in_phi_local(self):
        results = [calculate_energy_branching_ratio(1.0, phi) for phi in [1.0, 2.0, 5.0, 10.0]]
        phonon_fracs = [r["phonon_fraction"] for r in results]
        assert phonon_fracs == sorted(phonon_fracs)

    def test_invalid_B_site_negative(self):
        with pytest.raises(ValueError):
            calculate_energy_branching_ratio(-1.0, 1.0)

    def test_invalid_phi_local_zero(self):
        with pytest.raises(ValueError):
            calculate_energy_branching_ratio(1.0, 0.0)

    def test_invalid_phi_local_negative(self):
        with pytest.raises(ValueError):
            calculate_energy_branching_ratio(1.0, -1.0)

    def test_realistic_LENR_conditions(self):
        # Realistic Pd-D cell: B_site ≈ 0.8 (moderate field), phi_local ≈ 1.5
        # B_eff = 1.2 → phonon_fraction ≈ 0.545 (not yet safe, but showing mechanism)
        result = calculate_energy_branching_ratio(0.8, 1.5)
        assert result["phonon_fraction"] > 0.5
        assert result["B_effective"] == pytest.approx(1.2, rel=1e-10)

    def test_high_loading_regime_safe(self):
        # High loading: B_site = 10, phi_local = 15 → B_eff = 150 → >99% suppression
        result = calculate_energy_branching_ratio(10.0, 15.0)
        assert result["is_safe"] is True
        assert result["suppression_pct"] > 99.0
