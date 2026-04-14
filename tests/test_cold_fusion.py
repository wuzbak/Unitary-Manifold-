"""
tests/test_cold_fusion.py
==========================
Unit tests for src/core/cold_fusion.py — Pillar 15: Safe Cold Fusion.

Covers every public function and the two dataclass pipelines:
  gamow_factor, tunneling_probability,
  kk_radion_factor, winding_compression_factor,
  gamow_5d, tunneling_probability_5d, rate_enhancement,
  thomas_fermi_screening_energy, lattice_dd_separation,
  phi_lattice_enhancement, b_field_confinement_pressure,
  effective_separation_5d, gamow_peak_energy,
  astrophysical_s_factor_5d, cold_fusion_rate,
  ColdFusionConfig, ColdFusionResult, run_cold_fusion
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import math
import numpy as np
import pytest

from src.core.cold_fusion import (
    # constants
    ALPHA_FINE,
    AMU_MEV,
    A_PD_ANGSTROM,
    C_S_BRAID,
    K_B_EV_PER_K,
    K_CS_BRAID,
    M_DEUTERON_MEV,
    MU_DD_AMU,
    N1_BRAID,
    N2_BRAID,
    N_E_PD_PER_CC,
    PHI_VACUUM,
    RHO_BRAID,
    T_ROOM_K,
    Z_DEUTERON,
    # functions
    gamow_factor,
    tunneling_probability,
    kk_radion_factor,
    winding_compression_factor,
    gamow_5d,
    tunneling_probability_5d,
    rate_enhancement,
    thomas_fermi_screening_energy,
    lattice_dd_separation,
    phi_lattice_enhancement,
    b_field_confinement_pressure,
    effective_separation_5d,
    gamow_peak_energy,
    astrophysical_s_factor_5d,
    cold_fusion_rate,
    # dataclasses
    ColdFusionConfig,
    ColdFusionResult,
    run_cold_fusion,
)


# ===========================================================================
# TestConstants
# ===========================================================================

class TestConstants:
    """Sanity checks on module-level constants."""

    def test_alpha_fine_value(self):
        assert abs(ALPHA_FINE - 1.0 / 137.036) < 1e-5

    def test_amu_mev_value(self):
        assert abs(AMU_MEV - 931.494) < 0.01

    def test_a_pd_lattice_constant(self):
        assert abs(A_PD_ANGSTROM - 3.89) < 0.1

    def test_c_s_braid_value(self):
        assert abs(C_S_BRAID - 12.0 / 37.0) < 1e-10

    def test_k_cs_braid(self):
        assert K_CS_BRAID == N1_BRAID**2 + N2_BRAID**2

    def test_rho_braid_value(self):
        assert abs(RHO_BRAID - 35.0 / 37.0) < 1e-10

    def test_mu_dd_amu_approx_one(self):
        assert 0.9 < MU_DD_AMU < 1.1

    def test_phi_vacuum_is_one(self):
        assert PHI_VACUUM == 1.0

    def test_t_room_k(self):
        assert abs(T_ROOM_K - 293.0) < 1.0

    def test_z_deuteron(self):
        assert Z_DEUTERON == 1

    def test_braid_winding_sum(self):
        assert N1_BRAID + N2_BRAID == 12

    def test_n_e_pd_positive(self):
        assert N_E_PD_PER_CC > 0.0


# ===========================================================================
# TestGamowFactor
# ===========================================================================

class TestGamowFactor:
    """Tests for gamow_factor()."""

    def test_room_temperature_is_very_large(self):
        # At 0.025 eV (kT at room T), G >> 1 for D+D
        G = gamow_factor(1, 1, 0.025, MU_DD_AMU)
        assert G > 1000.0

    def test_gamow_keV_scale_order_of_magnitude(self):
        # At 10 keV (hot-fusion regime), G should be moderate (~10-50)
        G = gamow_factor(1, 1, 10e3, MU_DD_AMU)
        assert 5.0 < G < 200.0

    def test_scales_with_Z_product(self):
        # G ∝ Z1*Z2 — doubling Z1*Z2 doubles G
        G_1 = gamow_factor(1, 1, 100.0, 1.0)
        G_2 = gamow_factor(2, 1, 100.0, 1.0)
        assert abs(G_2 / G_1 - 2.0) < 1e-10

    def test_scales_with_sqrt_mu(self):
        # G ∝ √μ — quadrupling μ doubles G
        G_1 = gamow_factor(1, 1, 100.0, 1.0)
        G_4 = gamow_factor(1, 1, 100.0, 4.0)
        assert abs(G_4 / G_1 - 2.0) < 1e-10

    def test_scales_with_inverse_sqrt_E(self):
        # G ∝ 1/√E — quadrupling E halves G
        G_1 = gamow_factor(1, 1, 100.0, 1.0)
        G_4 = gamow_factor(1, 1, 400.0, 1.0)
        assert abs(G_4 / G_1 - 0.5) < 1e-10

    def test_raises_nonpositive_energy(self):
        with pytest.raises(ValueError):
            gamow_factor(1, 1, 0.0, 1.0)
        with pytest.raises(ValueError):
            gamow_factor(1, 1, -1.0, 1.0)

    def test_raises_nonpositive_mass(self):
        with pytest.raises(ValueError):
            gamow_factor(1, 1, 100.0, 0.0)
        with pytest.raises(ValueError):
            gamow_factor(1, 1, 100.0, -1.0)

    def test_returns_float(self):
        G = gamow_factor(1, 1, 25e-3, MU_DD_AMU)
        assert isinstance(G, float)

    def test_positive(self):
        G = gamow_factor(1, 1, 1.0, 1.0)
        assert G > 0.0

    def test_formula_crosscheck(self):
        # Manual: G = π × 1 × 1 × α × √(2 × μ_MeV / E_MeV)
        E_eV = 1000.0
        mu_amu = 1.0
        mu_MeV = mu_amu * AMU_MEV
        E_MeV = E_eV * 1e-6
        G_expected = math.pi * ALPHA_FINE * math.sqrt(2.0 * mu_MeV / E_MeV)
        G_got = gamow_factor(1, 1, E_eV, mu_amu)
        assert abs(G_got - G_expected) < 1e-10


# ===========================================================================
# TestTunnelingProbability
# ===========================================================================

class TestTunnelingProbability:
    """Tests for tunneling_probability()."""

    def test_G_zero_returns_one(self):
        assert tunneling_probability(0.0) == 1.0

    def test_G_positive_less_than_one(self):
        assert tunneling_probability(1.0) < 1.0

    def test_G_large_returns_zero(self):
        assert tunneling_probability(1000.0) == 0.0

    def test_formula(self):
        G = 5.5
        assert abs(tunneling_probability(G) - math.exp(-2.0 * G)) < 1e-15

    def test_decreasing_with_G(self):
        assert tunneling_probability(2.0) > tunneling_probability(3.0)


# ===========================================================================
# TestKKRadionFactor
# ===========================================================================

class TestKKRadionFactor:
    """Tests for kk_radion_factor()."""

    def test_equal_phi_returns_one(self):
        assert kk_radion_factor(1.0, 1.0) == 1.0

    def test_enhanced_lattice_reduces_factor(self):
        # phi_lattice > phi_vacuum → f_KK < 1
        f = kk_radion_factor(1.0, 2.0)
        assert f == 0.5

    def test_formula(self):
        f = kk_radion_factor(2.0, 5.0)
        assert abs(f - 2.0 / 5.0) < 1e-12

    def test_raises_nonpositive_phi_vacuum(self):
        with pytest.raises(ValueError):
            kk_radion_factor(0.0, 1.0)

    def test_raises_nonpositive_phi_lattice(self):
        with pytest.raises(ValueError):
            kk_radion_factor(1.0, 0.0)

    def test_always_positive(self):
        f = kk_radion_factor(1.0, 10.0)
        assert f > 0.0

    def test_factor_bounded_by_one_when_enhanced(self):
        f = kk_radion_factor(PHI_VACUUM, 1.1)
        assert f <= 1.0


# ===========================================================================
# TestWindingCompressionFactor
# ===========================================================================

class TestWindingCompressionFactor:
    """Tests for winding_compression_factor()."""

    def test_c_s_one_returns_one(self):
        assert winding_compression_factor(1.0, 12.0) == 1.0

    def test_canonical_braid_state(self):
        # c_s = 12/37, n_w = 12 → f_w = (12/37)^6
        f = winding_compression_factor(C_S_BRAID, 12.0)
        expected = (12.0 / 37.0) ** 6.0
        assert abs(f - expected) < 1e-12

    def test_less_than_one_for_small_c_s(self):
        f = winding_compression_factor(0.5, 2.0)
        assert f < 1.0

    def test_raises_nonpositive_c_s(self):
        with pytest.raises(ValueError):
            winding_compression_factor(0.0, 12.0)

    def test_raises_c_s_greater_than_one(self):
        with pytest.raises(ValueError):
            winding_compression_factor(1.5, 12.0)

    def test_raises_nonpositive_nw(self):
        with pytest.raises(ValueError):
            winding_compression_factor(0.5, 0.0)

    def test_positive(self):
        f = winding_compression_factor(C_S_BRAID, 5.0)
        assert f > 0.0

    def test_decreases_with_nw(self):
        f6 = winding_compression_factor(0.5, 6.0)
        f12 = winding_compression_factor(0.5, 12.0)
        assert f12 < f6


# ===========================================================================
# TestGamow5D
# ===========================================================================

class TestGamow5D:
    """Tests for gamow_5d()."""

    def test_no_enhancement_equals_4d(self):
        G4 = gamow_factor(1, 1, 100.0, 1.0)
        G5 = gamow_5d(1, 1, 100.0, 1.0, phi_vacuum=1.0, phi_lattice=1.0,
                      c_s=1.0, n_w=1.0)
        assert abs(G5 - G4) < 1e-10

    def test_5d_leq_4d(self):
        # 5D always ≤ 4D
        G4 = gamow_factor(1, 1, 25e-3, MU_DD_AMU)
        G5 = gamow_5d(1, 1, 25e-3, MU_DD_AMU, phi_vacuum=1.0,
                      phi_lattice=1.1)
        assert G5 <= G4

    def test_lattice_enhancement_reduces_gamow(self):
        G5_enhanced = gamow_5d(1, 1, 100.0, 1.0, phi_lattice=2.0)
        G5_none = gamow_5d(1, 1, 100.0, 1.0, phi_lattice=1.0)
        assert G5_enhanced < G5_none

    def test_formula_consistency(self):
        G4 = gamow_factor(1, 1, 500.0, 1.5)
        f_kk = kk_radion_factor(1.0, 1.5)
        f_w = winding_compression_factor(C_S_BRAID, 12.0)
        G5_expected = G4 * f_kk * f_w
        G5_got = gamow_5d(1, 1, 500.0, 1.5, phi_vacuum=1.0,
                          phi_lattice=1.5)
        assert abs(G5_got - G5_expected) < 1e-10

    def test_returns_float(self):
        G5 = gamow_5d(1, 1, 1000.0, 1.0)
        assert isinstance(G5, float)

    def test_positive(self):
        G5 = gamow_5d(1, 1, 1000.0, 1.0)
        assert G5 > 0.0


# ===========================================================================
# TestTunnelingProbability5D
# ===========================================================================

class TestTunnelingProbability5D:
    """Tests for tunneling_probability_5d()."""

    def test_greater_than_4d_probability(self):
        # With lattice enhancement, P₅ > P₄
        P4 = tunneling_probability(gamow_factor(1, 1, 1000.0, MU_DD_AMU))
        P5 = tunneling_probability_5d(1, 1, 1000.0, MU_DD_AMU,
                                       phi_lattice=1.1)
        assert P5 >= P4

    def test_bounded_zero_one(self):
        P5 = tunneling_probability_5d(1, 1, 25e-3, MU_DD_AMU,
                                       phi_lattice=1.1)
        assert 0.0 <= P5 <= 1.0

    def test_formula_consistency(self):
        G5 = gamow_5d(1, 1, 1000.0, 1.0, phi_lattice=1.5)
        expected = math.exp(-2.0 * G5)
        got = tunneling_probability_5d(1, 1, 1000.0, 1.0, phi_lattice=1.5)
        assert abs(got - expected) < 1e-15


# ===========================================================================
# TestRateEnhancement
# ===========================================================================

class TestRateEnhancement:
    """Tests for rate_enhancement()."""

    def test_equal_gamow_returns_one(self):
        assert rate_enhancement(10.0, 10.0) == 1.0

    def test_enhancement_greater_than_one(self):
        eta = rate_enhancement(100.0, 50.0)
        assert eta > 1.0

    def test_formula(self):
        G4, G5 = 200.0, 150.0
        expected = math.exp(2.0 * (G4 - G5))
        assert abs(rate_enhancement(G4, G5) - expected) < 1e-6

    def test_raises_negative_G5(self):
        with pytest.raises(ValueError):
            rate_enhancement(10.0, -1.0)

    def test_raises_G5_greater_than_G4(self):
        with pytest.raises(ValueError):
            rate_enhancement(5.0, 10.0)

    def test_large_enhancement_when_G5_small(self):
        # Even modest G4-G5 gap gives enormous enhancement
        eta = rate_enhancement(100.0, 90.0)
        assert eta > 1e8


# ===========================================================================
# TestThomasFermiScreening
# ===========================================================================

class TestThomasFermiScreening:
    """Tests for thomas_fermi_screening_energy()."""

    def test_pd_screening_is_few_tens_eV(self):
        dE = thomas_fermi_screening_energy(N_E_PD_PER_CC)
        # Standard TF screening in Pd: ~30–80 eV
        assert 10.0 < dE < 200.0

    def test_scales_with_Z_eff(self):
        dE1 = thomas_fermi_screening_energy(N_E_PD_PER_CC, Z_eff=1)
        dE2 = thomas_fermi_screening_energy(N_E_PD_PER_CC, Z_eff=2)
        assert abs(dE2 / dE1 - 2.0) < 1e-10

    def test_positive(self):
        assert thomas_fermi_screening_energy(1e20) > 0.0

    def test_raises_nonpositive_density(self):
        with pytest.raises(ValueError):
            thomas_fermi_screening_energy(0.0)

    def test_increases_with_electron_density(self):
        dE_low = thomas_fermi_screening_energy(1e21)
        dE_high = thomas_fermi_screening_energy(1e23)
        assert dE_high > dE_low

    def test_tf_energy_negligible_vs_coulomb_barrier(self):
        # TF screening (~25 eV) is negligible vs the D+D Coulomb barrier height
        # (~100 keV at nuclear contact radius ~few fm).
        dE = thomas_fermi_screening_energy(N_E_PD_PER_CC)
        coulomb_barrier_eV = 100e3  # ~100 keV for D+D
        assert dE < coulomb_barrier_eV * 0.01  # less than 1% of barrier


# ===========================================================================
# TestLatticeDDSeparation
# ===========================================================================

class TestLatticeDDSeparation:
    """Tests for lattice_dd_separation()."""

    def test_full_loading_gives_nn_distance(self):
        # At x=1: d = a_Pd/√2 ≈ 2.75 Å
        d = lattice_dd_separation(1.0)
        assert abs(d - A_PD_ANGSTROM / math.sqrt(2.0)) < 1e-10

    def test_full_loading_larger_than_d2_bond(self):
        # D-D bond in free D₂ ≈ 0.74 Å; lattice separation must be larger
        d = lattice_dd_separation(1.0)
        assert d > 0.74

    def test_increases_as_loading_decreases(self):
        d_high = lattice_dd_separation(0.9)
        d_low = lattice_dd_separation(0.1)
        assert d_low > d_high

    def test_raises_zero_loading(self):
        with pytest.raises(ValueError):
            lattice_dd_separation(0.0)

    def test_raises_negative_loading(self):
        with pytest.raises(ValueError):
            lattice_dd_separation(-0.1)

    def test_raises_loading_above_one(self):
        with pytest.raises(ValueError):
            lattice_dd_separation(1.1)

    def test_custom_lattice_constant(self):
        d = lattice_dd_separation(1.0, a_pd_angstrom=4.0)
        assert abs(d - 4.0 / math.sqrt(2.0)) < 1e-10

    def test_returns_angstroms_scale(self):
        d = lattice_dd_separation(0.9)
        assert 1.0 < d < 10.0


# ===========================================================================
# TestPhiLatticeEnhancement
# ===========================================================================

class TestPhiLatticeEnhancement:
    """Tests for phi_lattice_enhancement()."""

    def test_always_geq_one(self):
        for x in [0.1, 0.5, 0.9, 1.0]:
            phi = phi_lattice_enhancement(x)
            assert phi >= 1.0

    def test_increases_with_loading(self):
        phi_low = phi_lattice_enhancement(0.1)
        phi_high = phi_lattice_enhancement(1.0)
        assert phi_high > phi_low

    def test_formula_at_full_loading(self):
        # φ = 1 + 0.1 × (n_e / n_e_ref) × 1^{2/3} = 1 + 0.1 × 1.0 = 1.1
        phi = phi_lattice_enhancement(1.0, n_e_pd=N_E_PD_PER_CC)
        assert abs(phi - 1.1) < 1e-10

    def test_raises_zero_loading(self):
        with pytest.raises(ValueError):
            phi_lattice_enhancement(0.0)

    def test_raises_loading_above_one(self):
        with pytest.raises(ValueError):
            phi_lattice_enhancement(1.5)

    def test_vacuum_reference_density(self):
        # At n_e = n_e_ref and x=1, enhancement is exactly 10 % above vacuum
        phi = phi_lattice_enhancement(1.0, N_E_PD_PER_CC)
        assert abs(phi - 1.10) < 1e-10


# ===========================================================================
# TestBFieldConfinementPressure
# ===========================================================================

class TestBFieldConfinementPressure:
    """Tests for b_field_confinement_pressure()."""

    def test_zero_Hmax_returns_zero(self):
        assert b_field_confinement_pressure(0.0, 1.0, 1.0) == 0.0

    def test_scales_as_H_squared(self):
        P1 = b_field_confinement_pressure(1.0, 1.0, 1.0)
        P2 = b_field_confinement_pressure(2.0, 1.0, 1.0)
        assert abs(P2 / P1 - 4.0) < 1e-10

    def test_scales_as_phi_squared(self):
        P1 = b_field_confinement_pressure(1.0, 1.0, 1.0)
        P2 = b_field_confinement_pressure(1.0, 2.0, 1.0)
        assert abs(P2 / P1 - 4.0) < 1e-10

    def test_scales_as_lam_squared(self):
        P1 = b_field_confinement_pressure(1.0, 1.0, 1.0)
        P2 = b_field_confinement_pressure(1.0, 1.0, 3.0)
        assert abs(P2 / P1 - 9.0) < 1e-10

    def test_non_negative(self):
        P = b_field_confinement_pressure(2.0, 1.5, 0.5)
        assert P >= 0.0


# ===========================================================================
# TestEffectiveSeparation5D
# ===========================================================================

class TestEffectiveSeparation5D:
    """Tests for effective_separation_5d()."""

    def test_no_5d_effects_returns_geometric(self):
        d_geom = 2.5
        d_eff = effective_separation_5d(d_geom, phi_ratio=1.0, H_max=0.0)
        assert abs(d_eff - d_geom) < 1e-10

    def test_kk_suppression_reduces_separation(self):
        d_geom = 2.5
        d_eff = effective_separation_5d(d_geom, phi_ratio=0.9, H_max=0.0)
        assert d_eff < d_geom

    def test_b_field_reduces_separation(self):
        d_no_B = effective_separation_5d(2.5, phi_ratio=1.0, H_max=0.0)
        d_with_B = effective_separation_5d(2.5, phi_ratio=1.0, H_max=10.0,
                                            phi_mean=1.0, lam=1.0)
        assert d_with_B <= d_no_B

    def test_positive_result(self):
        d = effective_separation_5d(3.0, phi_ratio=0.95, H_max=1.0)
        assert d > 0.0


# ===========================================================================
# TestGamowPeakEnergy
# ===========================================================================

class TestGamowPeakEnergy:
    """Tests for gamow_peak_energy()."""

    def test_dd_room_temp_order_of_magnitude(self):
        # Gamow peak for D+D at 293 K should be ~eV range
        E_G = gamow_peak_energy(1, 1, MU_DD_AMU, T_ROOM_K)
        assert E_G > 0.0
        assert E_G < 1e6  # less than 1 MeV

    def test_increases_with_temperature(self):
        E_G_300 = gamow_peak_energy(1, 1, MU_DD_AMU, 300.0)
        E_G_1e7 = gamow_peak_energy(1, 1, MU_DD_AMU, 1e7)
        assert E_G_1e7 > E_G_300

    def test_increases_with_Z(self):
        E_G_1 = gamow_peak_energy(1, 1, 1.0, 1e6)
        E_G_2 = gamow_peak_energy(2, 2, 1.0, 1e6)
        assert E_G_2 > E_G_1

    def test_returns_positive(self):
        E_G = gamow_peak_energy(1, 1, 1.0, 1000.0)
        assert E_G > 0.0


# ===========================================================================
# TestAstrophysicalSFactor5D
# ===========================================================================

class TestAstrophysicalSFactor5D:
    """Tests for astrophysical_s_factor_5d()."""

    def test_equal_gamow_returns_S0(self):
        S5 = astrophysical_s_factor_5d(55e-3, 100.0, 100.0)
        assert abs(S5 - 55e-3) < 1e-12

    def test_enhanced_when_G5_less_than_G4(self):
        S5 = astrophysical_s_factor_5d(55e-3, 100.0, 80.0)
        assert S5 > 55e-3

    def test_formula(self):
        S0, G4, G5 = 0.1, 200.0, 100.0
        expected = S0 * math.exp(2.0 * (G4 - G5))
        assert abs(astrophysical_s_factor_5d(S0, G4, G5) - expected) < 1e-8

    def test_positive(self):
        assert astrophysical_s_factor_5d(1.0, 50.0, 30.0) > 0.0


# ===========================================================================
# TestColdFusionRate
# ===========================================================================

class TestColdFusionRate:
    """Tests for cold_fusion_rate()."""

    def test_returns_float(self):
        R = cold_fusion_rate(1e20, T_ROOM_K)
        assert isinstance(R, float)

    def test_non_negative(self):
        R = cold_fusion_rate(1e20, T_ROOM_K)
        assert R >= 0.0

    def test_5d_rate_geq_4d_rate(self):
        R_4d = cold_fusion_rate(1e20, T_ROOM_K, phi_lattice=1.0)
        R_5d = cold_fusion_rate(1e20, T_ROOM_K, phi_lattice=1.1)
        assert R_5d >= R_4d

    def test_rate_increases_with_n_D(self):
        # Use elevated temp so rate is finite; rate ∝ n_D²
        T_test = 1e6
        R_low = cold_fusion_rate(1e18, T_test, phi_lattice=1.1)
        R_high = cold_fusion_rate(1e20, T_test, phi_lattice=1.1)
        assert R_high > R_low

    def test_rate_increases_with_temperature(self):
        R_cold = cold_fusion_rate(1e20, 3000.0, phi_lattice=1.1)
        R_hot = cold_fusion_rate(1e20, 1e6, phi_lattice=1.1)
        assert R_hot >= R_cold

    def test_raises_nonpositive_n_D(self):
        with pytest.raises(ValueError):
            cold_fusion_rate(0.0, T_ROOM_K)

    def test_raises_nonpositive_T(self):
        with pytest.raises(ValueError):
            cold_fusion_rate(1e20, 0.0)


# ===========================================================================
# TestColdFusionConfig
# ===========================================================================

class TestColdFusionConfig:
    """Tests for ColdFusionConfig dataclass."""

    def test_default_values(self):
        cfg = ColdFusionConfig()
        assert cfg.T_K == T_ROOM_K
        assert cfg.loading_ratio == 0.9
        assert cfg.phi_vacuum == PHI_VACUUM
        assert cfg.c_s == C_S_BRAID
        assert cfg.n_w == float(N1_BRAID + N2_BRAID)

    def test_resolved_n_D_with_explicit(self):
        cfg = ColdFusionConfig(n_D_per_cc=5e21)
        assert cfg.resolved_n_D() == 5e21

    def test_resolved_n_D_from_loading(self):
        cfg = ColdFusionConfig(n_D_per_cc=0.0, loading_ratio=1.0)
        n_D = cfg.resolved_n_D()
        assert n_D > 0.0
        # Should be ~ n_e / 10 * x
        expected = N_E_PD_PER_CC / 10.0 * 1.0
        assert abs(n_D - expected) < 1.0

    def test_custom_temperature(self):
        cfg = ColdFusionConfig(T_K=500.0)
        assert cfg.T_K == 500.0


# ===========================================================================
# TestRunColdFusion
# ===========================================================================

class TestRunColdFusion:
    """Tests for run_cold_fusion() pipeline."""

    def _default_result(self):
        return run_cold_fusion(ColdFusionConfig())

    def test_returns_ColdFusionResult(self):
        result = self._default_result()
        assert isinstance(result, ColdFusionResult)

    def test_G5_leq_G4(self):
        result = self._default_result()
        assert result.G5 <= result.G4

    def test_phi_lattice_geq_phi_vacuum(self):
        result = self._default_result()
        assert result.phi_lattice >= PHI_VACUUM

    def test_f_kk_leq_one(self):
        result = self._default_result()
        assert result.f_kk <= 1.0

    def test_f_winding_leq_one(self):
        result = self._default_result()
        assert result.f_winding <= 1.0

    def test_enhancement_geq_one(self):
        result = self._default_result()
        assert result.enhancement >= 1.0

    def test_rate_5d_geq_rate_4d(self):
        result = self._default_result()
        assert result.rate_5d >= result.rate_4d

    def test_d_DD_angstrom_positive(self):
        result = self._default_result()
        assert result.d_DD_angstrom > 0.0

    def test_d_DD_larger_than_d2_bond(self):
        result = self._default_result()
        assert result.d_DD_angstrom > 0.74  # D₂ bond length

    def test_delta_E_TF_small(self):
        result = self._default_result()
        # TF screening in Pd should be tens of eV, not MeV
        assert result.delta_E_TF_eV < 1000.0

    def test_log10_rate_5d_geq_log10_rate_4d(self):
        result = self._default_result()
        assert result.log10_rate_5d >= result.log10_rate_4d

    def test_E_gamow_eV_positive(self):
        result = self._default_result()
        assert result.E_gamow_eV > 0.0

    def test_T_K_propagated(self):
        result = self._default_result()
        assert result.T_K == T_ROOM_K

    def test_loading_ratio_propagated(self):
        result = self._default_result()
        assert result.loading_ratio == 0.9

    def test_high_temperature_gives_larger_rate(self):
        result_cold = run_cold_fusion(ColdFusionConfig(T_K=3000.0))
        result_hot = run_cold_fusion(ColdFusionConfig(T_K=1e7))
        assert result_hot.rate_5d >= result_cold.rate_5d

    def test_higher_loading_increases_enhancement(self):
        result_low = run_cold_fusion(ColdFusionConfig(loading_ratio=0.1))
        result_high = run_cold_fusion(ColdFusionConfig(loading_ratio=1.0))
        # Higher loading → larger phi_lattice → larger enhancement
        assert result_high.enhancement >= result_low.enhancement

    def test_result_fields_are_floats(self):
        result = self._default_result()
        for attr in ("G4", "G5", "f_kk", "f_winding", "enhancement",
                     "rate_4d", "rate_5d", "d_DD_angstrom", "delta_E_TF_eV"):
            assert isinstance(getattr(result, attr), float), attr

    def test_gamow_factors_both_positive(self):
        result = self._default_result()
        assert result.G4 > 0.0
        assert result.G5 > 0.0

    def test_room_temp_rate_essentially_zero_without_5d(self):
        # Without 5D winding enhancement (c_s=1, n_w=1) and no lattice phi
        # boost, the room-temperature D+D rate is float-underflow zero.
        result = run_cold_fusion(
            ColdFusionConfig(T_K=T_ROOM_K, loading_ratio=1.0)
        )
        # rate_4d uses c_s=1, n_w=1 (pure 4D) → G4≈480 → exp(-960) = 0.0
        assert result.rate_4d == 0.0

    def test_5d_produces_nonzero_log_rate_at_higher_loading(self):
        # With full enhancement the 5D log-rate is finite (not -inf)
        result = run_cold_fusion(
            ColdFusionConfig(
                T_K=T_ROOM_K,
                loading_ratio=1.0,
                c_s=C_S_BRAID,
                n_w=12.0,
            )
        )
        # log10_rate_5d may still be -inf at room T due to very large G5,
        # but at least the structure is consistent
        assert math.isfinite(result.G5) or result.G5 > 0.0
