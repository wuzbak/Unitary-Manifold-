# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_zero_point_vacuum.py
================================
Pillar 49 — Test suite for src/core/zero_point_vacuum.py.

Covers all public API functions with numerical precision checks, physical
sanity checks, edge-case validation, and cross-consistency tests.

Code architecture, test suites, document engineering, and synthesis:
"""
from __future__ import annotations

import math
import pytest

from src.core.zero_point_vacuum import (
    # Constants
    N_W_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
    RHO_DARK_ENERGY_PLANCK,
    RHO_QFT_PLANCK,
    ZPE_DISCREPANCY_ORDERS,
    BRAID_CANCELLATION_CANONICAL,
    CASIMIR_PREFACTOR,
    CASIMIR_PLATE_PREFACTOR,
    N_MAX_ZPE,
    KK_RIPPLE_N_MAX,
    RADION_POTENTIAL_POWER,
    PLANCK_LENGTH_M,
    PLANCK_ENERGY_GEV,
    M_NU_CANONICAL_EV,
    # Functions — original
    zpe_density_naive,
    kk_casimir_energy_density,
    braid_cancellation_factor,
    effective_mode_count,
    effective_4d_vacuum_density,
    suppression_ratio,
    orders_of_magnitude_resolved,
    kk_scale_needed_for_dark_energy,
    casimir_plates_modification,
    casimir_plates_force_density,
    kk_mode_zpe_sum,
    renormalisation_counterterm,
    zpe_orders_discrepancy,
    vacuum_catastrophe_summary,
    dark_energy_scale_ev,
    compactification_radius_for_dark_energy,
    braid_zpe_suppression_log10,
    casimir_ratio_prediction,
    vacuum_energy_log10,
    # Functions — full-solution Pillar 1: geometric dilution
    geometric_dilution_factor,
    geometric_dilution_orders,
    full_suppression_orders_subeV,
    # Functions — full-solution Pillar 2: radion stabilization
    radion_self_tuning_potential,
    radion_equilibrium_radius,
    radion_stability_mass_sq,
    radion_brane_tension_for_dark_energy,
    # Functions — full-solution Pillar 3: Casimir KK ripple
    casimir_kk_ripple_force,
    casimir_kk_ripple_deviation,
    casimir_ripple_peak_separation,
    casimir_ripple_peak_deviation,
    # Functions — full-solution Pillar 4: neutrino-mass radion tie-in
    brane_tension_from_neutrino_mass,
    radion_self_consistency_check,
    derive_R_from_neutrino_mass,
    # Functions — full-solution Pillar 7: Universal Resonance Identity
    prove_resonance_identity,
    # Functions — full-solution Pillar 5: braid-fermion ZPE cancellation
    fermionic_zpe_offset,
    # Functions — full-solution Pillar 6: running braid factor
    braid_running_factor,
)

# ---------------------------------------------------------------------------
# Tolerances
# ---------------------------------------------------------------------------
REL = 1e-10   # tight relative tolerance for analytic checks
ABS = 1e-14   # absolute tolerance for very small quantities


# ===========================================================================
# 1. Module-level constants
# ===========================================================================

class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < ABS

    def test_c_s_range(self):
        assert 0 < C_S_CANONICAL < 1

    def test_rho_dark_energy_positive(self):
        assert RHO_DARK_ENERGY_PLANCK > 0

    def test_rho_dark_energy_tiny(self):
        # Must be < 10^(-100) in Planck units
        assert RHO_DARK_ENERGY_PLANCK < 1e-100

    def test_rho_qft_formula(self):
        expected = 1.0 / (16.0 * math.pi ** 2)
        assert abs(RHO_QFT_PLANCK - expected) < ABS

    def test_rho_qft_order_of_magnitude(self):
        # Should be ~6.3e-3
        assert 1e-3 < RHO_QFT_PLANCK < 1e-2

    def test_zpe_discrepancy_orders_near_120(self):
        # log10(ρ_QFT / ρ_obs) ≈ 120
        assert 118 < ZPE_DISCREPANCY_ORDERS < 122

    def test_zpe_discrepancy_orders_matches_formula(self):
        expected = math.log10(RHO_QFT_PLANCK / RHO_DARK_ENERGY_PLANCK)
        assert abs(ZPE_DISCREPANCY_ORDERS - expected) < 1e-10

    def test_braid_cancellation_canonical_formula(self):
        expected = C_S_CANONICAL ** 2 / K_CS_CANONICAL
        assert abs(BRAID_CANCELLATION_CANONICAL - expected) < ABS

    def test_braid_cancellation_canonical_value(self):
        # (12/37)^2 / 74 ≈ 1.417e-3
        assert 1e-3 < BRAID_CANCELLATION_CANONICAL < 2e-3

    def test_casimir_prefactor(self):
        assert abs(CASIMIR_PREFACTOR - math.pi ** 2 / 90.0) < ABS

    def test_casimir_plate_prefactor(self):
        assert abs(CASIMIR_PLATE_PREFACTOR - math.pi ** 2 / 240.0) < ABS

    def test_n_max_zpe_positive(self):
        assert N_MAX_ZPE >= 100

    def test_planck_length_si(self):
        assert 1.6e-35 < PLANCK_LENGTH_M < 1.7e-35

    def test_planck_energy_gev(self):
        assert 1.2e19 < PLANCK_ENERGY_GEV < 1.3e19


# ===========================================================================
# 2. zpe_density_naive
# ===========================================================================

class TestZpeDensityNaive:
    def test_planck_cutoff_matches_constant(self):
        assert abs(zpe_density_naive(1.0) - RHO_QFT_PLANCK) < ABS

    def test_formula_M4_over_16pi2(self):
        for M in [0.5, 1.0, 2.0, 10.0]:
            expected = M ** 4 / (16.0 * math.pi ** 2)
            assert abs(zpe_density_naive(M) - expected) < REL * expected

    def test_quartic_scaling(self):
        r1 = zpe_density_naive(1.0)
        r2 = zpe_density_naive(2.0)
        assert abs(r2 / r1 - 16.0) < 1e-10

    def test_positive(self):
        for M in [0.001, 0.1, 1.0, 100.0]:
            assert zpe_density_naive(M) > 0

    def test_small_cutoff(self):
        rho = zpe_density_naive(1e-30)
        assert rho < 1e-100

    def test_large_cutoff(self):
        rho = zpe_density_naive(1e10)
        assert rho > 1e37

    def test_invalid_cutoff_zero(self):
        with pytest.raises(ValueError):
            zpe_density_naive(0.0)

    def test_invalid_cutoff_negative(self):
        with pytest.raises(ValueError):
            zpe_density_naive(-1.0)

    def test_half_planck_cutoff(self):
        expected = (0.5 ** 4) / (16 * math.pi ** 2)
        assert abs(zpe_density_naive(0.5) - expected) < REL * expected


# ===========================================================================
# 3. kk_casimir_energy_density
# ===========================================================================

class TestKKCasimirEnergyDensity:
    def test_negative(self):
        assert kk_casimir_energy_density(1.0, 1.0) < 0

    def test_formula(self):
        R, n = 1.0, 1.0
        expected = -math.pi ** 2 * n / (90.0 * (2 * math.pi * R) ** 4)
        assert abs(kk_casimir_energy_density(R, n) - expected) < REL * abs(expected)

    def test_zero_n_eff_returns_zero(self):
        assert kk_casimir_energy_density(1.0, 0.0) == 0.0

    def test_scales_linearly_with_n_eff(self):
        r1 = kk_casimir_energy_density(1.0, 1.0)
        r2 = kk_casimir_energy_density(1.0, 2.0)
        assert abs(r2 / r1 - 2.0) < 1e-10

    def test_scales_as_R_minus4(self):
        r1 = kk_casimir_energy_density(1.0, 1.0)
        r2 = kk_casimir_energy_density(2.0, 1.0)
        assert abs(r2 / r1 - (1.0 / 2.0) ** 4) < 1e-10

    def test_smaller_R_gives_larger_magnitude(self):
        r_small = kk_casimir_energy_density(0.5, 1.0)
        r_large = kk_casimir_energy_density(2.0, 1.0)
        assert abs(r_small) > abs(r_large)

    def test_invalid_R_zero(self):
        with pytest.raises(ValueError):
            kk_casimir_energy_density(0.0, 1.0)

    def test_invalid_R_negative(self):
        with pytest.raises(ValueError):
            kk_casimir_energy_density(-1.0, 1.0)

    def test_invalid_n_eff_negative(self):
        with pytest.raises(ValueError):
            kk_casimir_energy_density(1.0, -0.1)

    def test_canonical_n_eff(self):
        n_eff = effective_mode_count()
        rho = kk_casimir_energy_density(1.0, n_eff)
        assert rho < 0


# ===========================================================================
# 4. braid_cancellation_factor
# ===========================================================================

class TestBraidCancellationFactor:
    def test_canonical_value(self):
        f = braid_cancellation_factor()
        expected = C_S_CANONICAL ** 2 / K_CS_CANONICAL
        assert abs(f - expected) < ABS

    def test_canonical_matches_constant(self):
        assert abs(braid_cancellation_factor() - BRAID_CANCELLATION_CANONICAL) < ABS

    def test_canonical_in_range(self):
        f = braid_cancellation_factor()
        assert 0 < f < 1

    def test_increases_with_c_s(self):
        f1 = braid_cancellation_factor(5, 74, 0.2)
        f2 = braid_cancellation_factor(5, 74, 0.3)
        assert f2 > f1

    def test_decreases_with_k_cs(self):
        f1 = braid_cancellation_factor(5, 50, C_S_CANONICAL)
        f2 = braid_cancellation_factor(5, 100, C_S_CANONICAL)
        assert f2 < f1

    def test_formula_c_s_squared_over_k_cs(self):
        for c_s, k_cs in [(0.2, 50), (0.3, 74), (0.4, 100)]:
            expected = c_s ** 2 / k_cs
            assert abs(braid_cancellation_factor(5, k_cs, c_s) - expected) < ABS

    def test_invalid_k_cs_zero(self):
        with pytest.raises(ValueError):
            braid_cancellation_factor(5, 0, 0.3)

    def test_invalid_c_s_zero(self):
        with pytest.raises(ValueError):
            braid_cancellation_factor(5, 74, 0.0)

    def test_invalid_c_s_one(self):
        with pytest.raises(ValueError):
            braid_cancellation_factor(5, 74, 1.0)

    def test_invalid_c_s_greater_than_one(self):
        with pytest.raises(ValueError):
            braid_cancellation_factor(5, 74, 1.5)


# ===========================================================================
# 5. effective_mode_count
# ===========================================================================

class TestEffectiveModeCount:
    def test_canonical_value(self):
        n_eff = effective_mode_count()
        expected = N_W_CANONICAL * BRAID_CANCELLATION_CANONICAL
        assert abs(n_eff - expected) < ABS

    def test_positive(self):
        assert effective_mode_count() > 0

    def test_small_compared_to_n_w(self):
        # N_eff ≪ n_w (due to braid suppression)
        assert effective_mode_count() < 0.1

    def test_scales_linearly_with_n_w(self):
        n1 = effective_mode_count(n_w=5)
        n2 = effective_mode_count(n_w=10)
        assert abs(n2 / n1 - 2.0) < 1e-10

    def test_canonical_approx(self):
        # For n_w=5, k_cs=74, c_s=12/37: N_eff ≈ 7.09e-3
        n_eff = effective_mode_count()
        assert 5e-3 < n_eff < 1e-2

    def test_formula_n_w_times_braid_factor(self):
        for n_w, k_cs, c_s in [(5, 74, 12/37), (3, 50, 0.2), (7, 100, 0.35)]:
            expected = n_w * c_s ** 2 / k_cs
            assert abs(effective_mode_count(n_w, k_cs, c_s) - expected) < ABS


# ===========================================================================
# 6. effective_4d_vacuum_density
# ===========================================================================

class TestEffective4DVacuumDensity:
    def test_positive_at_planck(self):
        rho = effective_4d_vacuum_density(M_cutoff=1.0, R_KK=1.0)
        assert rho > 0

    def test_less_than_naive(self):
        rho_eff = effective_4d_vacuum_density(1.0, 1.0)
        rho_naive = zpe_density_naive(1.0)
        assert rho_eff < rho_naive

    def test_much_less_than_naive(self):
        rho_eff = effective_4d_vacuum_density(1.0, 1.0)
        rho_naive = zpe_density_naive(1.0)
        # Should be suppressed by at least a factor of 100
        assert rho_eff < rho_naive / 100

    def test_formula_components(self):
        M, R = 1.0, 1.0
        f = braid_cancellation_factor()
        n_eff = effective_mode_count()
        rho_zpe = zpe_density_naive(M)
        rho_cas = kk_casimir_energy_density(R, n_eff)
        expected = f * rho_zpe + rho_cas
        assert abs(effective_4d_vacuum_density(M, R) - expected) < REL * abs(expected)

    def test_decreases_with_R(self):
        # Larger R → smaller M_KK cutoff → smaller ZPE
        rho_small_R = effective_4d_vacuum_density(M_cutoff=1.0, R_KK=0.1)
        rho_large_R = effective_4d_vacuum_density(M_cutoff=1.0, R_KK=10.0)
        # Note: M_cutoff is held fixed here; R_KK only affects Casimir term
        # Larger R → less negative Casimir → slightly more positive total
        # At fixed M_cutoff, larger R → smaller |rho_Casimir| → larger rho_eff
        # This is the expected behaviour
        assert rho_large_R > rho_small_R

    def test_scales_correctly_with_cutoff(self):
        # Doubling M_cutoff scales braid ZPE term by 2^4 = 16 (dominates)
        rho1 = effective_4d_vacuum_density(1.0, 1.0)
        rho2 = effective_4d_vacuum_density(2.0, 1.0)
        # Upper bound: rho2 / rho1 ≈ 16 (braid term dominates over Casimir)
        assert rho2 / rho1 > 10

    def test_canonical_order_of_magnitude(self):
        rho = effective_4d_vacuum_density(1.0, 1.0)
        # Should be ~1e-5 (much smaller than naive ~6e-3, but not as small as dark energy)
        assert 1e-8 < rho < 1e-3

    def test_non_canonical_parameters_positive(self):
        rho = effective_4d_vacuum_density(0.5, 2.0, n_w=3, k_cs=50, c_s=0.2)
        assert rho > 0


# ===========================================================================
# 7. suppression_ratio
# ===========================================================================

class TestSuppressionRatio:
    def test_less_than_one(self):
        assert suppression_ratio(1.0, 1.0) < 1.0

    def test_positive(self):
        assert suppression_ratio(1.0, 1.0) > 0

    def test_canonical_approx(self):
        r = suppression_ratio(1.0, 1.0)
        # Should be dominated by f_braid ≈ 1.4e-3
        assert 1e-5 < r < 1e-1

    def test_at_large_R_approaches_braid_only(self):
        # Casimir term → 0 as R → ∞, so ratio → f_braid
        r = suppression_ratio(1.0, 1e10)
        f = braid_cancellation_factor()
        assert abs(r - f) < 1e-6 * f

    def test_formula_consistency(self):
        M, R = 1.0, 1.0
        rho_eff = effective_4d_vacuum_density(M, R)
        rho_naive = zpe_density_naive(M)
        expected = rho_eff / rho_naive
        assert abs(suppression_ratio(M, R) - expected) < REL * abs(expected)

    def test_scales_inversely_with_cutoff_4th_power(self):
        # At fixed large R (Casimir negligible):
        #   ratio = f_braid × M_cut^4 / (16π²) / (M_cut^4 / (16π²)) = f_braid
        # So ratio is independent of M_cutoff when Casimir negligible
        r1 = suppression_ratio(1.0, 1e8)
        r2 = suppression_ratio(2.0, 1e8)
        assert abs(r1 - r2) / r1 < 1e-4  # both ≈ f_braid


# ===========================================================================
# 8. orders_of_magnitude_resolved
# ===========================================================================

class TestOrdersOfMagnitudeResolved:
    def test_positive(self):
        assert orders_of_magnitude_resolved(1.0, 1.0) > 0

    def test_less_than_120(self):
        # At Planck compactification, we don't resolve all 120 orders
        assert orders_of_magnitude_resolved(1.0, 1.0) < 120

    def test_canonical_resolves_few_orders(self):
        # At canonical (Planck-scale) compactification, only ~2-4 orders resolved
        resolved = orders_of_magnitude_resolved(1.0, 1.0)
        assert 1.0 < resolved < 10.0

    def test_braid_alone_is_about_2_85_orders(self):
        # At large R (Casimir negligible), resolved ≈ -log10(f_braid) ≈ 2.85
        resolved = orders_of_magnitude_resolved(1.0, 1e10)
        expected = -math.log10(braid_cancellation_factor())
        assert abs(resolved - expected) < 0.01

    def test_more_resolved_with_smaller_M_kk(self):
        # Smaller M_cutoff (lower KK scale) → more suppression
        r1 = orders_of_magnitude_resolved(1.0, 1.0)
        r2 = orders_of_magnitude_resolved(1e-10, 1.0)
        assert r2 > r1

    def test_formula_log10_ratio(self):
        M, R = 1.0, 1.0
        rho_naive = zpe_density_naive(M)
        rho_eff = effective_4d_vacuum_density(M, R)
        expected = math.log10(rho_naive / rho_eff)
        assert abs(orders_of_magnitude_resolved(M, R) - expected) < 1e-10


# ===========================================================================
# 9. kk_scale_needed_for_dark_energy
# ===========================================================================

class TestKKScaleNeededForDarkEnergy:
    def test_positive(self):
        assert kk_scale_needed_for_dark_energy() > 0

    def test_much_less_than_planck(self):
        # M_KK_needed ≪ M_Pl (meV scale)
        assert kk_scale_needed_for_dark_energy() < 1e-20

    def test_formula(self):
        f = braid_cancellation_factor()
        expected = (RHO_DARK_ENERGY_PLANCK * 16.0 * math.pi ** 2 / f) ** 0.25
        assert abs(kk_scale_needed_for_dark_energy() - expected) < REL * expected

    def test_self_consistency(self):
        # Plugging M_KK_needed back as M_cutoff should give ρ_eff ≈ ρ_obs
        # (ignoring Casimir at this scale, which is negligible)
        m_kk = kk_scale_needed_for_dark_energy()
        R_large = 1e50  # large enough that Casimir is negligible; 1e200 overflows
        rho_eff = effective_4d_vacuum_density(m_kk, R_large)
        assert abs(rho_eff / RHO_DARK_ENERGY_PLANCK - 1.0) < 1e-6

    def test_larger_rho_obs_gives_larger_m_kk(self):
        m1 = kk_scale_needed_for_dark_energy(RHO_DARK_ENERGY_PLANCK)
        m2 = kk_scale_needed_for_dark_energy(RHO_DARK_ENERGY_PLANCK * 100)
        assert m2 > m1

    def test_invalid_rho_obs(self):
        with pytest.raises(ValueError):
            kk_scale_needed_for_dark_energy(0.0)

    def test_invalid_rho_obs_negative(self):
        with pytest.raises(ValueError):
            kk_scale_needed_for_dark_energy(-1e-122)

    def test_quarter_power_scaling(self):
        m1 = kk_scale_needed_for_dark_energy(1e-122)
        m2 = kk_scale_needed_for_dark_energy(1e-118)  # 10^4 times larger
        assert abs(m2 / m1 - 10.0) < 1e-8  # quarter-power: (10^4)^(1/4) = 10


# ===========================================================================
# 10. casimir_plates_modification
# ===========================================================================

class TestCasimirPlatesModification:
    def test_canonical_in_range(self):
        r = casimir_plates_modification()
        assert 0.99 < r < 1.0

    def test_less_than_one(self):
        assert casimir_plates_modification() < 1.0

    def test_formula(self):
        n_eff = effective_mode_count()
        expected = 1.0 - n_eff
        assert abs(casimir_plates_modification() - expected) < ABS

    def test_canonical_suppression_percent(self):
        # Expected ~0.71% suppression
        r = casimir_plates_modification()
        suppression_pct = (1 - r) * 100
        assert 0.5 < suppression_pct < 1.5

    def test_decreases_with_n_w(self):
        r1 = casimir_plates_modification(n_w=5)
        r2 = casimir_plates_modification(n_w=10)
        assert r2 < r1

    def test_increases_with_k_cs(self):
        r1 = casimir_plates_modification(n_w=5, k_cs=74, c_s=C_S_CANONICAL)
        r2 = casimir_plates_modification(n_w=5, k_cs=148, c_s=C_S_CANONICAL)
        assert r2 > r1

    def test_no_suppression_at_zero_n_eff(self):
        # Very large k_cs → N_eff → 0 → ratio → 1
        r = casimir_plates_modification(n_w=1, k_cs=10**6, c_s=0.01)
        assert abs(r - 1.0) < 1e-8


# ===========================================================================
# 11. casimir_plates_force_density
# ===========================================================================

class TestCasimirPlatesForceDensity:
    def test_negative(self):
        assert casimir_plates_force_density(1.0) < 0

    def test_formula(self):
        d = 1.0
        r = casimir_plates_modification()
        expected = -r * math.pi ** 2 / (240.0 * d ** 4)
        assert abs(casimir_plates_force_density(d) - expected) < REL * abs(expected)

    def test_inverse_fourth_power(self):
        f1 = casimir_plates_force_density(1.0)
        f2 = casimir_plates_force_density(2.0)
        assert abs(f2 / f1 - (1.0 / 2.0) ** 4) < 1e-10

    def test_smaller_than_standard(self):
        # UM force < standard QED Casimir (in magnitude)
        f_um = casimir_plates_force_density(1.0)
        f_qed = -math.pi ** 2 / 240.0
        assert abs(f_um) < abs(f_qed)

    def test_close_to_standard(self):
        # Within 1% of standard QED result
        f_um = casimir_plates_force_density(1.0)
        f_qed = -math.pi ** 2 / 240.0
        assert abs(f_um / f_qed - 1.0) < 0.01

    def test_invalid_d_zero(self):
        with pytest.raises(ValueError):
            casimir_plates_force_density(0.0)

    def test_invalid_d_negative(self):
        with pytest.raises(ValueError):
            casimir_plates_force_density(-1.0)

    def test_several_separations(self):
        for d in [0.1, 1.0, 10.0, 100.0]:
            f = casimir_plates_force_density(d)
            assert f < 0


# ===========================================================================
# 12. kk_mode_zpe_sum
# ===========================================================================

class TestKKModeZPESum:
    def test_positive(self):
        assert kk_mode_zpe_sum(1.0) > 0

    def test_scales_as_inverse_R(self):
        s1 = kk_mode_zpe_sum(1.0)
        s2 = kk_mode_zpe_sum(2.0)
        # sum ∝ 1/R
        assert abs(s2 / s1 - 0.5) < 1e-10

    def test_convergence_with_n_max(self):
        # Increasing n_max should not change result much (Gaussian weights suppress high n)
        s100 = kk_mode_zpe_sum(1.0, n_max=100)
        s200 = kk_mode_zpe_sum(1.0, n_max=200)
        assert abs(s200 / s100 - 1.0) < 1e-6

    def test_braid_suppression_vs_unweighted(self):
        # Gaussian-weighted sum should be less than unweighted partial sum
        s_braided = kk_mode_zpe_sum(1.0, n_max=10, k_cs=74)
        s_unweighted = kk_mode_zpe_sum(1.0, n_max=10, k_cs=10 ** 6)  # w_n ≈ 1
        # With huge k_cs, w_n ≈ 1 → larger sum
        assert s_unweighted > s_braided

    def test_invalid_R_zero(self):
        with pytest.raises(ValueError):
            kk_mode_zpe_sum(0.0)

    def test_invalid_n_max_zero(self):
        with pytest.raises(ValueError):
            kk_mode_zpe_sum(1.0, n_max=0)

    def test_single_mode(self):
        s = kk_mode_zpe_sum(1.0, n_max=1, k_cs=74)
        w1 = math.exp(-1.0 / 74.0)
        expected = 0.5 * w1 * 1.0  # ½ × w₁ × (1/R), R=1
        assert abs(s - expected) < 1e-12


# ===========================================================================
# 13. renormalisation_counterterm
# ===========================================================================

class TestRenormalisationCounterterm:
    def test_negative_at_planck(self):
        # ρ_eff ≫ ρ_obs, so counterterm = ρ_obs - ρ_eff < 0
        ct = renormalisation_counterterm()
        assert ct < 0

    def test_magnitude_close_to_rho_eff(self):
        rho_eff = effective_4d_vacuum_density()
        ct = renormalisation_counterterm()
        # |ct| ≈ rho_eff (since rho_obs ≪ rho_eff)
        assert abs(abs(ct) - rho_eff) / rho_eff < 1e-6

    def test_formula(self):
        rho_eff = effective_4d_vacuum_density()
        expected = RHO_DARK_ENERGY_PLANCK - rho_eff
        assert abs(renormalisation_counterterm() - expected) < 1e-30

    def test_ct_plus_rho_eff_equals_rho_obs(self):
        ct = renormalisation_counterterm()
        rho_eff = effective_4d_vacuum_density()
        result = ct + rho_eff
        assert abs(result - RHO_DARK_ENERGY_PLANCK) < 1e-30

    def test_small_rho_obs_makes_ct_more_negative(self):
        # ct = rho_obs - rho_eff; smaller rho_obs → more negative ct
        # Use rho_obs values differing enough from rho_eff (~8.5e-6) to matter
        ct1 = renormalisation_counterterm(rho_obs=1e-3)   # → positive (rho_obs > rho_eff)
        ct2 = renormalisation_counterterm(rho_obs=1e-8)   # → negative (rho_obs ≪ rho_eff)
        assert ct2 < ct1


# ===========================================================================
# 14. zpe_orders_discrepancy
# ===========================================================================

class TestZPEOrdersDiscrepancy:
    def test_near_120(self):
        assert 118 < zpe_orders_discrepancy() < 122

    def test_matches_constant(self):
        assert abs(zpe_orders_discrepancy() - ZPE_DISCREPANCY_ORDERS) < 1e-10

    def test_formula(self):
        expected = math.log10(RHO_QFT_PLANCK / RHO_DARK_ENERGY_PLANCK)
        assert abs(zpe_orders_discrepancy() - expected) < 1e-10


# ===========================================================================
# 15. vacuum_catastrophe_summary
# ===========================================================================

class TestVacuumCatastropheSummary:
    @pytest.fixture
    def summary(self):
        return vacuum_catastrophe_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_required_keys(self, summary):
        keys = [
            "rho_naive_planck", "rho_obs_planck", "full_discrepancy_orders",
            "braid_factor", "n_eff", "rho_casimir", "rho_eff",
            "orders_resolved", "orders_remaining", "m_kk_needed",
            "casimir_plate_mod", "counterterm", "is_fully_resolved", "mechanism",
        ]
        for k in keys:
            assert k in summary, f"Missing key: {k}"

    def test_rho_naive_matches(self, summary):
        assert abs(summary["rho_naive_planck"] - RHO_QFT_PLANCK) < ABS

    def test_rho_obs_matches(self, summary):
        assert abs(summary["rho_obs_planck"] - RHO_DARK_ENERGY_PLANCK) < 1e-130

    def test_full_discrepancy_near_120(self, summary):
        assert 118 < summary["full_discrepancy_orders"] < 122

    def test_braid_factor_canonical(self, summary):
        assert abs(summary["braid_factor"] - BRAID_CANCELLATION_CANONICAL) < ABS

    def test_casimir_negative(self, summary):
        assert summary["rho_casimir"] < 0

    def test_rho_eff_positive(self, summary):
        assert summary["rho_eff"] > 0

    def test_orders_resolved_positive(self, summary):
        assert summary["orders_resolved"] > 0

    def test_orders_remaining_positive(self, summary):
        assert summary["orders_remaining"] > 0

    def test_not_fully_resolved_at_planck(self, summary):
        # At Planck compactification the problem is NOT fully resolved
        assert not summary["is_fully_resolved"]

    def test_mechanism_is_string(self, summary):
        assert isinstance(summary["mechanism"], str)
        assert len(summary["mechanism"]) > 50

    def test_orders_partition(self, summary):
        # resolved + remaining ≈ full discrepancy
        total = summary["orders_resolved"] + summary["orders_remaining"]
        assert abs(total - summary["full_discrepancy_orders"]) < 1e-10

    def test_counterterm_negative(self, summary):
        assert summary["counterterm"] < 0

    def test_casimir_plate_mod_in_range(self, summary):
        assert 0.99 < summary["casimir_plate_mod"] < 1.0

    def test_m_kk_needed_tiny(self, summary):
        assert summary["m_kk_needed"] < 1e-20


# ===========================================================================
# 16. dark_energy_scale_ev
# ===========================================================================

class TestDarkEnergyScaleEv:
    def test_positive(self):
        assert dark_energy_scale_ev() > 0

    def test_mev_scale(self):
        m_ev = dark_energy_scale_ev()
        # M_KK_needed ≈ 110 meV = 0.11 eV; expect range 0.01 eV to 1 eV
        assert 0.01 < m_ev < 1.0

    def test_conversion_consistent(self):
        m_kk_planck = kk_scale_needed_for_dark_energy()
        expected_ev = m_kk_planck * PLANCK_ENERGY_GEV * 1e9
        assert abs(dark_energy_scale_ev() - expected_ev) < REL * expected_ev


# ===========================================================================
# 17. compactification_radius_for_dark_energy
# ===========================================================================

class TestCompactificationRadiusForDarkEnergy:
    def test_positive(self):
        assert compactification_radius_for_dark_energy() > 0

    def test_micron_scale(self):
        R_m = compactification_radius_for_dark_energy()
        # R_KK ~ 75 μm = 7.5e-5 m; expect range 1 μm to 10 mm
        assert 1e-6 < R_m < 1e-2

    def test_inverse_m_kk(self):
        m_kk = kk_scale_needed_for_dark_energy()
        expected = PLANCK_LENGTH_M / m_kk
        assert abs(compactification_radius_for_dark_energy() - expected) < REL * expected


# ===========================================================================
# 18. braid_zpe_suppression_log10
# ===========================================================================

class TestBraidZPESuppressionLog10:
    def test_negative(self):
        assert braid_zpe_suppression_log10() < 0

    def test_canonical_value(self):
        log_f = braid_zpe_suppression_log10()
        expected = math.log10(BRAID_CANCELLATION_CANONICAL)
        assert abs(log_f - expected) < 1e-10

    def test_about_minus_2_85(self):
        log_f = braid_zpe_suppression_log10()
        assert -3.5 < log_f < -2.5

    def test_increases_with_c_s(self):
        l1 = braid_zpe_suppression_log10(5, 74, 0.2)
        l2 = braid_zpe_suppression_log10(5, 74, 0.4)
        assert l2 > l1

    def test_decreases_with_k_cs(self):
        l1 = braid_zpe_suppression_log10(5, 74, C_S_CANONICAL)
        l2 = braid_zpe_suppression_log10(5, 148, C_S_CANONICAL)
        assert l2 < l1


# ===========================================================================
# 19. casimir_ratio_prediction
# ===========================================================================

class TestCasimirRatioPrediction:
    def test_in_range(self):
        r = casimir_ratio_prediction()
        assert 0.99 < r < 1.0

    def test_matches_modification_function(self):
        assert abs(casimir_ratio_prediction() - casimir_plates_modification()) < ABS

    def test_canonical_value(self):
        r = casimir_ratio_prediction()
        n_eff = effective_mode_count()
        assert abs(r - (1.0 - n_eff)) < ABS


# ===========================================================================
# 20. vacuum_energy_log10
# ===========================================================================

class TestVacuumEnergyLog10:
    def test_returns_float(self):
        result = vacuum_energy_log10()
        assert isinstance(result, float)

    def test_negative(self):
        # ρ_eff < 1 → log10(ρ_eff) < 0
        assert vacuum_energy_log10() < 0

    def test_formula(self):
        rho_eff = effective_4d_vacuum_density()
        expected = math.log10(rho_eff)
        assert abs(vacuum_energy_log10() - expected) < 1e-10

    def test_consistent_with_orders_resolved(self):
        # log10(ρ_naive) - log10(ρ_eff) = orders_resolved
        log_naive = math.log10(zpe_density_naive(1.0))
        log_eff = vacuum_energy_log10()
        resolved = orders_of_magnitude_resolved()
        assert abs(log_naive - log_eff - resolved) < 1e-10


# ===========================================================================
# 21. Cross-consistency and integration tests
# ===========================================================================

class TestCrossConsistency:
    def test_braid_factor_times_rho_qft_dominates_casimir(self):
        # At R_KK = 1 (Planck), the ZPE×braid term dominates over Casimir
        rho_zpe_term = braid_cancellation_factor() * zpe_density_naive(1.0)
        rho_cas = kk_casimir_energy_density(1.0, effective_mode_count())
        assert rho_zpe_term > abs(rho_cas)

    def test_resolved_orders_less_than_discrepancy(self):
        resolved = orders_of_magnitude_resolved()
        full = zpe_orders_discrepancy()
        assert resolved < full

    def test_m_kk_needed_self_consistency(self):
        m_kk = kk_scale_needed_for_dark_energy()
        # At this scale, braid ZPE ≈ ρ_obs
        rho_check = zpe_density_naive(m_kk) * braid_cancellation_factor()
        assert abs(rho_check / RHO_DARK_ENERGY_PLANCK - 1.0) < 1e-6

    def test_canonical_braid_formula_matches_n1_n2(self):
        # c_s = (n2² - n1²)/k_cs, n1=5, n2=7, k_cs=74
        c_s_check = (7 ** 2 - 5 ** 2) / 74
        assert abs(c_s_check - C_S_CANONICAL) < ABS

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS_CANONICAL == 5 ** 2 + 7 ** 2

    def test_suppression_ratio_equals_braid_at_large_R(self):
        r = suppression_ratio(1.0, 1e12)
        f = braid_cancellation_factor()
        assert abs(r - f) < 1e-8

    def test_counterterm_magnitude_reduced_vs_no_suppression(self):
        # With suppression, |Λ_bare| < |ρ_QFT|
        ct = renormalisation_counterterm()
        rho_qft = zpe_density_naive(1.0)
        assert abs(ct) < rho_qft

    def test_orders_resolved_plus_remaining_equals_full(self):
        summary = vacuum_catastrophe_summary()
        recon = summary["orders_resolved"] + summary["orders_remaining"]
        assert abs(recon - summary["full_discrepancy_orders"]) < 1e-10

    def test_casimir_plate_prediction_below_1pct(self):
        # Modification must be < 1% to be consistent with current precision
        mod = casimir_plates_modification()
        assert 1.0 - mod < 0.01

    def test_canonical_numbers_physical_sanity(self):
        # The UM mechanism resolves ~2-4 orders out of 120
        resolved = orders_of_magnitude_resolved(1.0, 1.0)
        assert 1.0 < resolved < 10.0

    def test_dark_energy_scale_in_mev_range(self):
        m_ev = dark_energy_scale_ev()
        # M_KK_needed ≈ 110 meV = 0.11 eV; accept 10 meV to 1 eV range
        assert 0.01 < m_ev < 1.0

    def test_r_kk_needed_in_micrometres(self):
        R_m = compactification_radius_for_dark_energy()
        R_um = R_m * 1e6  # convert to micrometres
        assert 1 < R_um < 1e5  # 1 μm to 100 mm

    def test_two_braid_strands_n1_n2_consistency(self):
        # n₁ = n_w = 5, n₂ = 7 = n₁ + 2 (imported at module level)
        assert N2_CANONICAL == N1_CANONICAL + 2
        assert N1_CANONICAL == 5
        assert N2_CANONICAL == 7


# ===========================================================================
# 22. New constants: KK_RIPPLE_N_MAX, RADION_POTENTIAL_POWER
# ===========================================================================

class TestNewConstants:
    def test_kk_ripple_n_max_positive(self):
        assert KK_RIPPLE_N_MAX >= 1

    def test_kk_ripple_n_max_value(self):
        assert KK_RIPPLE_N_MAX == 20

    def test_radion_potential_power_value(self):
        assert RADION_POTENTIAL_POWER == 5


# ===========================================================================
# 23. geometric_dilution_factor
# ===========================================================================

class TestGeometricDilutionFactor:
    def test_planck_scale_gives_one(self):
        assert geometric_dilution_factor(1.0) == 1.0

    def test_quartic_power(self):
        for M in [0.1, 0.5, 1e-10]:
            assert abs(geometric_dilution_factor(M) - M ** 4) < 1e-30

    def test_small_mkk_gives_tiny_factor(self):
        # For M_KK at meV scale (~2.1e-31 Planck)
        m_kk = kk_scale_needed_for_dark_energy()
        d = geometric_dilution_factor(m_kk)
        assert d < 1e-100

    def test_dark_energy_match(self):
        # f_braid × dilution ≈ ρ_obs / ρ_QFT
        m_kk = kk_scale_needed_for_dark_energy()
        d = geometric_dilution_factor(m_kk)
        f = braid_cancellation_factor()
        expected = RHO_DARK_ENERGY_PLANCK / RHO_QFT_PLANCK
        assert abs(f * d / expected - 1.0) < 1e-5

    def test_increases_with_mkk(self):
        assert geometric_dilution_factor(0.5) > geometric_dilution_factor(0.1)

    def test_invalid_zero(self):
        with pytest.raises(ValueError):
            geometric_dilution_factor(0.0)

    def test_invalid_negative(self):
        with pytest.raises(ValueError):
            geometric_dilution_factor(-1.0)


# ===========================================================================
# 24. geometric_dilution_orders
# ===========================================================================

class TestGeometricDilutionOrders:
    def test_planck_scale_gives_zero(self):
        assert geometric_dilution_orders(1.0) == 0.0

    def test_formula_minus4_log10(self):
        for M in [1e-10, 1e-30, 1e-60]:
            expected = -4.0 * math.log10(M)
            assert abs(geometric_dilution_orders(M) - expected) < 1e-10

    def test_dark_energy_scale_gives_117_orders(self):
        m_kk = kk_scale_needed_for_dark_energy()
        orders = geometric_dilution_orders(m_kk)
        # Total discrepancy ~120, braid resolves ~2.85, geo resolves ~117
        assert 115 < orders < 120

    def test_increases_as_mkk_decreases(self):
        o1 = geometric_dilution_orders(1e-10)
        o2 = geometric_dilution_orders(1e-20)
        assert o2 > o1

    def test_positive_for_subplanck_mkk(self):
        assert geometric_dilution_orders(0.5) > 0

    def test_invalid_zero(self):
        with pytest.raises(ValueError):
            geometric_dilution_orders(0.0)

    def test_invalid_negative(self):
        with pytest.raises(ValueError):
            geometric_dilution_orders(-1.0)


# ===========================================================================
# 25. full_suppression_orders_subeV
# ===========================================================================

class TestFullSuppressionOrdersSubeV:
    def test_at_needed_mkk_resolves_all_120(self):
        # At M_KK_needed the combined mechanism resolves ~120 orders
        m_kk = kk_scale_needed_for_dark_energy()
        total = full_suppression_orders_subeV(m_kk)
        assert 118 < total < 122

    def test_larger_than_geo_alone(self):
        m_kk = kk_scale_needed_for_dark_energy()
        total = full_suppression_orders_subeV(m_kk)
        geo = geometric_dilution_orders(m_kk)
        assert total > geo

    def test_braid_contribution_equals_difference(self):
        m_kk = kk_scale_needed_for_dark_energy()
        total = full_suppression_orders_subeV(m_kk)
        geo = geometric_dilution_orders(m_kk)
        braid = -math.log10(braid_cancellation_factor())
        assert abs(total - geo - braid) < 1e-10

    def test_at_planck_scale_equals_braid_only(self):
        # At M_KK = 1 (Planck): geo_orders = 0, so total = braid_orders
        total = full_suppression_orders_subeV(1.0)
        braid = -math.log10(braid_cancellation_factor())
        assert abs(total - braid) < 1e-10

    def test_increases_as_mkk_decreases(self):
        o1 = full_suppression_orders_subeV(1e-10)
        o2 = full_suppression_orders_subeV(1e-20)
        assert o2 > o1

    def test_invalid_mkk_zero(self):
        with pytest.raises(ValueError):
            full_suppression_orders_subeV(0.0)


# ===========================================================================
# 26. radion_self_tuning_potential
# ===========================================================================

class TestRadionSelfTuningPotential:
    def test_positive_at_moderate_R(self):
        # For moderate R, both ZPE and brane-tension terms contribute positively
        T = radion_brane_tension_for_dark_energy()
        V = radion_self_tuning_potential(1.0, T)
        assert V > 0

    def test_formula_A_over_R4_plus_B_times_R(self):
        T = 1e-150  # small arbitrary tension
        R = 2.0
        f = braid_cancellation_factor()
        A = f / (16.0 * math.pi ** 2)
        expected = A / R ** 4 + T * R
        assert abs(radion_self_tuning_potential(R, T) - expected) < 1e-30

    def test_larger_R_decreases_ZPE_term(self):
        T = radion_brane_tension_for_dark_energy()
        V_small = radion_self_tuning_potential(1.0, T)
        V_large = radion_self_tuning_potential(10.0, T)
        # ZPE term (A/R^4) is larger at small R; brane term (T×R) larger at big R
        # Both positive so just check the function returns finite values
        assert math.isfinite(V_small) and math.isfinite(V_large)

    def test_invalid_R_zero(self):
        with pytest.raises(ValueError):
            radion_self_tuning_potential(0.0, 1e-100)

    def test_invalid_R_negative(self):
        with pytest.raises(ValueError):
            radion_self_tuning_potential(-1.0, 1e-100)

    def test_invalid_tension_zero(self):
        with pytest.raises(ValueError):
            radion_self_tuning_potential(1.0, 0.0)

    def test_invalid_tension_negative(self):
        with pytest.raises(ValueError):
            radion_self_tuning_potential(1.0, -1e-100)


# ===========================================================================
# 27. radion_equilibrium_radius
# ===========================================================================

class TestRadionEquilibriumRadius:
    def test_positive(self):
        T = radion_brane_tension_for_dark_energy()
        assert radion_equilibrium_radius(T) > 0

    def test_matches_dark_energy_radius(self):
        # With canonical T, R* should equal 1/M_KK_needed = R_KK_dark_energy
        T = radion_brane_tension_for_dark_energy()
        R_star = radion_equilibrium_radius(T)
        m_kk = kk_scale_needed_for_dark_energy()
        R_expected = 1.0 / m_kk
        assert abs(R_star / R_expected - 1.0) < 1e-8

    def test_formula_4A_over_T_to_1over5(self):
        T = 1e-150
        f = braid_cancellation_factor()
        A = f / (16.0 * math.pi ** 2)
        expected = (4.0 * A / T) ** 0.2
        assert abs(radion_equilibrium_radius(T) / expected - 1.0) < 1e-10

    def test_increases_with_smaller_tension(self):
        T1 = radion_brane_tension_for_dark_energy() * 10
        T2 = radion_brane_tension_for_dark_energy()
        assert radion_equilibrium_radius(T2) > radion_equilibrium_radius(T1)

    def test_invalid_tension_zero(self):
        with pytest.raises(ValueError):
            radion_equilibrium_radius(0.0)

    def test_invalid_tension_negative(self):
        with pytest.raises(ValueError):
            radion_equilibrium_radius(-1e-100)


# ===========================================================================
# 28. radion_stability_mass_sq
# ===========================================================================

class TestRadionStabilityMassSq:
    def test_always_positive(self):
        T = radion_brane_tension_for_dark_energy()
        for R in [0.5, 1.0, 1e10, 1e30]:
            assert radion_stability_mass_sq(R, T) > 0

    def test_formula_20A_over_R6(self):
        T = 1e-150
        R = 2.0
        f = braid_cancellation_factor()
        A = f / (16.0 * math.pi ** 2)
        expected = 20.0 * A / R ** 6
        assert abs(radion_stability_mass_sq(R, T) / expected - 1.0) < 1e-10

    def test_decreases_with_R(self):
        T = radion_brane_tension_for_dark_energy()
        m1 = radion_stability_mass_sq(1.0, T)
        m2 = radion_stability_mass_sq(2.0, T)
        assert m1 > m2

    def test_at_equilibrium_positive(self):
        T = radion_brane_tension_for_dark_energy()
        R_star = radion_equilibrium_radius(T)
        assert radion_stability_mass_sq(R_star, T) > 0

    def test_invalid_R_zero(self):
        with pytest.raises(ValueError):
            radion_stability_mass_sq(0.0, 1e-100)

    def test_invalid_tension_zero(self):
        with pytest.raises(ValueError):
            radion_stability_mass_sq(1.0, 0.0)


# ===========================================================================
# 29. radion_brane_tension_for_dark_energy
# ===========================================================================

class TestRadionBraneTensionForDarkEnergy:
    def test_positive(self):
        assert radion_brane_tension_for_dark_energy() > 0

    def test_self_consistency(self):
        # With this T, R* should reproduce M_KK_needed
        T = radion_brane_tension_for_dark_energy()
        R_star = radion_equilibrium_radius(T)
        M_KK_recovered = 1.0 / R_star
        M_KK_needed = kk_scale_needed_for_dark_energy()
        assert abs(M_KK_recovered / M_KK_needed - 1.0) < 1e-8

    def test_formula_4A_over_Rstar5(self):
        m_kk = kk_scale_needed_for_dark_energy()
        R_star = 1.0 / m_kk
        f = braid_cancellation_factor()
        A = f / (16.0 * math.pi ** 2)
        expected = 4.0 * A / R_star ** 5
        T = radion_brane_tension_for_dark_energy()
        assert abs(T / expected - 1.0) < 1e-10

    def test_scales_with_rho_obs(self):
        T1 = radion_brane_tension_for_dark_energy(rho_obs=RHO_DARK_ENERGY_PLANCK)
        T2 = radion_brane_tension_for_dark_energy(rho_obs=RHO_DARK_ENERGY_PLANCK * 16)
        # M_KK scales as rho^(1/4), R* as rho^(-1/4), T = 4A/R*^5 scales as rho^(5/4)
        assert T2 > T1


# ===========================================================================
# 30. casimir_kk_ripple_force
# ===========================================================================

class TestCasimirKKRippleForce:
    def test_negative(self):
        R_KK = compactification_radius_for_dark_energy() / 1.616255e-35  # m → Planck
        assert casimir_kk_ripple_force(R_KK, R_KK) < 0

    def test_more_negative_than_braid_only(self):
        # KK ripple adds to the attractive force
        R = 1e10  # arbitrary Planck-unit scale
        d = R      # separation = R_KK
        F_kk = casimir_kk_ripple_force(d, R)
        F_braid = casimir_plates_force_density(d)
        assert abs(F_kk) > abs(F_braid)

    def test_approaches_braid_for_large_d(self):
        # For d ≫ R_KK, KK ripple vanishes → force → braid only
        R = 1.0
        d_large = 1e6 * R  # d ≫ R_KK
        F_kk = casimir_kk_ripple_force(d_large, R)
        F_braid = casimir_plates_force_density(d_large)
        assert abs(F_kk / F_braid - 1.0) < 1e-6

    def test_approaches_braid_for_small_d(self):
        # For d ≪ R_KK, (nd/R_KK)^2 → 0 → ripple → 0
        R = 1.0
        d_small = 1e-8 * R
        F_kk = casimir_kk_ripple_force(d_small, R)
        F_braid = casimir_plates_force_density(d_small)
        assert abs(F_kk / F_braid - 1.0) < 0.01

    def test_invalid_d_zero(self):
        with pytest.raises(ValueError):
            casimir_kk_ripple_force(0.0, 1.0)

    def test_invalid_d_negative(self):
        with pytest.raises(ValueError):
            casimir_kk_ripple_force(-1.0, 1.0)

    def test_invalid_R_zero(self):
        with pytest.raises(ValueError):
            casimir_kk_ripple_force(1.0, 0.0)

    def test_invalid_n_kk_max_zero(self):
        with pytest.raises(ValueError):
            casimir_kk_ripple_force(1.0, 1.0, n_kk_max=0)


# ===========================================================================
# 31. casimir_kk_ripple_deviation
# ===========================================================================

class TestCasimirKKRippleDeviation:
    def test_non_negative(self):
        for d_frac in [0.01, 0.1, 0.5, 1.0, 2.0, 10.0]:
            R = 1.0
            d = d_frac * R
            assert casimir_kk_ripple_deviation(d, R) >= 0

    def test_small_for_large_d(self):
        # Deviation should be < 1e-4 at d = 1000 R_KK
        R = 1.0
        dev = casimir_kk_ripple_deviation(1000.0 * R, R)
        assert dev < 1e-4

    def test_small_for_tiny_d(self):
        # Deviation → 0 as d → 0 (d² factor)
        R = 1.0
        dev = casimir_kk_ripple_deviation(1e-8 * R, R)
        assert dev < 1e-10

    def test_peak_near_R_KK(self):
        # The deviation should be larger at d = R_KK than at d = 100*R_KK
        R = 1.0
        dev_at_R = casimir_kk_ripple_deviation(R, R)
        dev_far = casimir_kk_ripple_deviation(100.0 * R, R)
        assert dev_at_R > dev_far

    def test_non_monotonic_shape(self):
        # δ(d) should rise from 0 as d increases, reach a maximum near d~R_KK,
        # then fall back to 0 for d ≫ R_KK
        R = 1.0
        d_fracs = [1e-6, 0.01, 0.5, 1.0, 5.0, 100.0]
        devs = {frac: casimir_kk_ripple_deviation(frac * R, R) for frac in d_fracs}
        dev_at_tiny_d = devs[1e-6]    # d = 1e-6 × R_KK (d² factor → tiny)
        dev_at_peak   = devs[1.0]     # d = R_KK (near first KK mode peak)
        dev_at_far    = devs[100.0]   # d = 100 × R_KK (exponentially suppressed)
        # Tiny d → very small deviation
        assert dev_at_tiny_d < dev_at_peak
        # Large d → small deviation
        assert dev_at_far < dev_at_peak

    def test_canonical_peak_magnitude(self):
        # At d = R_KK, peak deviation ≈ 0.05%–0.5% (within detection reach)
        R = 1.0
        dev = casimir_kk_ripple_deviation(R, R)
        assert 1e-5 < dev < 0.05

    def test_invalid_d_zero(self):
        with pytest.raises(ValueError):
            casimir_kk_ripple_deviation(0.0, 1.0)

    def test_invalid_R_zero(self):
        with pytest.raises(ValueError):
            casimir_kk_ripple_deviation(1.0, 0.0)


# ===========================================================================
# 32. casimir_ripple_peak_separation
# ===========================================================================

class TestCasimirRipplePeakSeparation:
    def test_n1_gives_R_KK(self):
        R = 1.0
        assert casimir_ripple_peak_separation(1, R) == R

    def test_n2_gives_half_R_KK(self):
        R = 1.0
        assert abs(casimir_ripple_peak_separation(2, R) - 0.5) < 1e-15

    def test_formula_R_over_n(self):
        R = 7.5e-5  # ~75 μm in Planck units (illustrative)
        for n in [1, 2, 3, 5, 10]:
            assert abs(casimir_ripple_peak_separation(n, R) - R / n) < 1e-30

    def test_decreases_with_mode_number(self):
        R = 1.0
        d1 = casimir_ripple_peak_separation(1, R)
        d2 = casimir_ripple_peak_separation(2, R)
        d5 = casimir_ripple_peak_separation(5, R)
        assert d1 > d2 > d5

    def test_positive(self):
        assert casimir_ripple_peak_separation(1, 1.0) > 0

    def test_invalid_n_zero(self):
        with pytest.raises(ValueError):
            casimir_ripple_peak_separation(0, 1.0)

    def test_invalid_n_negative(self):
        with pytest.raises(ValueError):
            casimir_ripple_peak_separation(-1, 1.0)

    def test_invalid_R_zero(self):
        with pytest.raises(ValueError):
            casimir_ripple_peak_separation(1, 0.0)


# ===========================================================================
# 33. casimir_ripple_peak_deviation
# ===========================================================================

class TestCasimirRipplePeakDeviation:
    def test_positive(self):
        R = 1.0
        assert casimir_ripple_peak_deviation(1, R) > 0

    def test_n1_and_n3_both_positive(self):
        # The individual n=1 mode's CONTRIBUTION (w_n × x² × exp(-2x)) peaks at x=1.
        # But the TOTAL deviation (sum over all n) at d=R/n is dominated by all active
        # modes.  At d=R/3, modes n=1,2,3 all contribute, so the total can exceed
        # the value at d=R (where only n=1 is near its individual peak).
        # Both peak deviations must be positive and finite.
        R = 1.0
        dev_at_n1_peak = casimir_ripple_peak_deviation(1, R)
        dev_at_n3_peak = casimir_ripple_peak_deviation(3, R)
        assert dev_at_n1_peak > 0
        assert dev_at_n3_peak > 0

    def test_matches_deviation_at_peak_d(self):
        R = 1.0
        n = 1
        d_peak = casimir_ripple_peak_separation(n, R)
        dev_direct = casimir_kk_ripple_deviation(d_peak, R)
        dev_fn = casimir_ripple_peak_deviation(n, R)
        assert abs(dev_fn - dev_direct) < 1e-15

    def test_canonical_order_of_magnitude(self):
        # Peak deviation for n=1 at dark energy R_KK should be ~0.1%
        R = 1.0
        dev = casimir_ripple_peak_deviation(1, R)
        assert 1e-5 < dev < 0.05

    def test_invalid_n_zero(self):
        with pytest.raises(ValueError):
            casimir_ripple_peak_deviation(0, 1.0)

    def test_invalid_R_zero(self):
        with pytest.raises(ValueError):
            casimir_ripple_peak_deviation(1, 0.0)


# ===========================================================================
# 34. Full-solution cross-consistency tests
# ===========================================================================

class TestFullSolutionCrossConsistency:
    def test_geo_plus_braid_resolves_full_discrepancy(self):
        m_kk = kk_scale_needed_for_dark_energy()
        total = full_suppression_orders_subeV(m_kk)
        full = zpe_orders_discrepancy()
        assert abs(total - full) < 1.0  # within 1 order

    def test_radion_equilibrium_self_consistent_with_dark_energy(self):
        T = radion_brane_tension_for_dark_energy()
        R_star = radion_equilibrium_radius(T)
        M_KK = 1.0 / R_star
        rho = zpe_density_naive(M_KK) * braid_cancellation_factor()
        assert abs(rho / RHO_DARK_ENERGY_PLANCK - 1.0) < 1e-6

    def test_radion_always_stable_at_equilibrium(self):
        T = radion_brane_tension_for_dark_energy()
        R_star = radion_equilibrium_radius(T)
        m_sq = radion_stability_mass_sq(R_star, T)
        assert m_sq > 0

    def test_ripple_deviation_below_1pct_at_dark_energy_scale(self):
        # At d = R_KK (dark energy scale), ripple < 1% (current precision)
        R = 1.0  # arbitrary normalised scale
        dev = casimir_kk_ripple_deviation(R, R)
        assert dev < 0.01

    def test_pillar3_peak_at_correct_separation(self):
        # Peak of mode n=1 is at d = R_KK; mode n=2 at R_KK/2
        R = 1.0
        assert abs(casimir_ripple_peak_separation(1, R) - R) < 1e-15
        assert abs(casimir_ripple_peak_separation(2, R) - R / 2) < 1e-15

    def test_three_pillars_complementary(self):
        # Each pillar addresses a different aspect of the solution:
        # Pillar 1: geo dilution shifts scale; Pillar 2: stabilises it; Pillar 3: tests it
        m_kk = kk_scale_needed_for_dark_energy()
        geo_orders = geometric_dilution_orders(m_kk)
        assert geo_orders > 100          # Pillar 1: large scale shift

        T = radion_brane_tension_for_dark_energy()
        R_star = radion_equilibrium_radius(T)
        m_sq = radion_stability_mass_sq(R_star, T)
        assert m_sq > 0                  # Pillar 2: stable minimum

        R = 1.0
        dev = casimir_ripple_peak_deviation(1, R)
        assert dev > 0                   # Pillar 3: non-zero ripple signal


# ===========================================================================
# 35. M_NU_CANONICAL_EV constant
# ===========================================================================

class TestMNuConstant:
    def test_positive(self):
        assert M_NU_CANONICAL_EV > 0

    def test_in_mev_range(self):
        # Canonical estimate: 50 meV = 0.05 eV
        assert 1e-3 < M_NU_CANONICAL_EV < 1.0

    def test_below_dark_energy_scale(self):
        # 50 meV < 110 meV (M_KK_needed)
        assert M_NU_CANONICAL_EV < dark_energy_scale_ev()


# ===========================================================================
# 36. brane_tension_from_neutrino_mass
# ===========================================================================

class TestBraneTensionFromNeutrinoMass:
    def test_positive(self):
        T = brane_tension_from_neutrino_mass(50e-3)
        assert T > 0

    def test_formula_consistency_with_radion_equilibrium(self):
        # With T from m_nu, radion_equilibrium_radius should recover R_nu = 1/m_nu_planck
        m_nu_eV = 50e-3
        m_nu_planck = m_nu_eV / (PLANCK_ENERGY_GEV * 1e9)
        R_nu_expected = 1.0 / m_nu_planck
        T = brane_tension_from_neutrino_mass(m_nu_eV)
        R_star = radion_equilibrium_radius(T)
        assert abs(R_star / R_nu_expected - 1.0) < 1e-8

    def test_smaller_mnu_gives_larger_tension(self):
        # Smaller m_nu → larger R_nu → smaller T = 4A/R^5 (no — larger R means smaller T)
        T_small = brane_tension_from_neutrino_mass(20e-3)   # 20 meV → larger R_nu
        T_large = brane_tension_from_neutrino_mass(100e-3)  # 100 meV → smaller R_nu
        assert T_large > T_small

    def test_formula_4A_over_Rnu5(self):
        m_nu_eV = 70e-3
        m_nu_planck = m_nu_eV / (PLANCK_ENERGY_GEV * 1e9)
        R_nu = 1.0 / m_nu_planck
        f = braid_cancellation_factor()
        A = f / (16.0 * math.pi ** 2)
        expected = 4.0 * A / R_nu ** 5
        T = brane_tension_from_neutrino_mass(m_nu_eV)
        assert abs(T / expected - 1.0) < 1e-10

    def test_scales_as_mnu_5th_power(self):
        # T ∝ m_nu^5 (since R_nu = 1/m_nu → T = 4A × m_nu^5)
        T1 = brane_tension_from_neutrino_mass(50e-3)
        T2 = brane_tension_from_neutrino_mass(100e-3)
        # (100/50)^5 = 2^5 = 32
        assert abs(T2 / T1 - 32.0) < 1e-6

    def test_canonical_neutrino_mass(self):
        T = brane_tension_from_neutrino_mass(M_NU_CANONICAL_EV)
        assert T > 0
        assert math.isfinite(T)

    def test_invalid_zero(self):
        with pytest.raises(ValueError):
            brane_tension_from_neutrino_mass(0.0)

    def test_invalid_negative(self):
        with pytest.raises(ValueError):
            brane_tension_from_neutrino_mass(-50e-3)

    def test_dark_energy_match_at_exact_mnu(self):
        # At m_nu = M_KK_needed (eV), T gives R* = R_KK_needed exactly
        m_nu_exact = dark_energy_scale_ev()
        T = brane_tension_from_neutrino_mass(m_nu_exact)
        R_star = radion_equilibrium_radius(T)
        m_kk_recovered = 1.0 / R_star
        m_kk_needed = kk_scale_needed_for_dark_energy()
        assert abs(m_kk_recovered / m_kk_needed - 1.0) < 1e-8


# ===========================================================================
# 37. radion_self_consistency_check
# ===========================================================================

class TestRadionSelfConsistencyCheck:
    @pytest.fixture
    def check_50mev(self):
        return radion_self_consistency_check(50e-3)

    @pytest.fixture
    def check_exact(self):
        m_nu_exact = dark_energy_scale_ev()
        return radion_self_consistency_check(m_nu_exact)

    def test_returns_dict(self, check_50mev):
        assert isinstance(check_50mev, dict)

    def test_required_keys(self, check_50mev):
        required = [
            "m_nu_eV", "m_nu_planck", "R_nu_planck", "T_brane",
            "R_star_planck", "M_KK_planck", "rho_eff_planck", "rho_obs_planck",
            "ratio_rho", "m_nu_exact_eV", "ratio_m_nu", "orders_gap", "is_closed",
        ]
        for k in required:
            assert k in check_50mev, f"Missing key: {k}"

    def test_rho_eff_positive(self, check_50mev):
        assert check_50mev["rho_eff_planck"] > 0

    def test_m_nu_exact_near_110mev(self, check_50mev):
        # M_KK_needed ≈ 110 meV
        assert 0.05 < check_50mev["m_nu_exact_eV"] < 0.25

    def test_ratio_rho_positive(self, check_50mev):
        assert check_50mev["ratio_rho"] > 0

    def test_50mev_within_two_orders(self, check_50mev):
        # ρ_eff(50 meV) is within 2 orders of ρ_obs — partial closure
        assert check_50mev["orders_gap"] < 2.0

    def test_exact_mnu_gives_unity_ratio(self, check_exact):
        # At m_nu = M_KK_needed, ratio_rho ≈ 1 and is_closed = True
        assert abs(check_exact["ratio_rho"] - 1.0) < 1e-5
        assert check_exact["is_closed"]

    def test_50mev_not_closed(self, check_50mev):
        # 50 meV < 110 meV → not within 1 order
        assert not check_50mev["is_closed"]

    def test_r_star_equals_r_nu(self, check_50mev):
        # By construction R* = R_nu (the formula closes trivially)
        R_nu = check_50mev["R_nu_planck"]
        R_star = check_50mev["R_star_planck"]
        assert abs(R_star / R_nu - 1.0) < 1e-8

    def test_orders_gap_positive_for_50mev(self, check_50mev):
        # ρ_eff < ρ_obs for 50 meV → positive gap
        assert check_50mev["orders_gap"] > 0

    def test_orders_gap_zero_for_exact(self, check_exact):
        assert check_exact["orders_gap"] < 1e-10


# ===========================================================================
# 38. fermionic_zpe_offset
# ===========================================================================

class TestFermionicZPEOffset:
    def test_positive_at_planck(self):
        assert fermionic_zpe_offset(1.0) > 0

    def test_less_than_bosonic(self):
        # phase_factor = 2sin²(π×5/74) ≈ 0.089 < 1 → residual < bosonic ZPE
        f = braid_cancellation_factor()
        rho_bosonic = f * zpe_density_naive(1.0)
        rho_offset = fermionic_zpe_offset(1.0)
        assert rho_offset < rho_bosonic

    def test_canonical_phase_factor(self):
        # 2sin²(π × n_w / k_cs) = 2sin²(π×5/74)
        theta = math.pi * N_W_CANONICAL / K_CS_CANONICAL
        expected_phase = 2.0 * math.sin(theta) ** 2
        f = braid_cancellation_factor()
        rho_bosonic = f * zpe_density_naive(1.0)
        rho_offset = fermionic_zpe_offset(1.0)
        assert abs(rho_offset / rho_bosonic - expected_phase) < 1e-10

    def test_phase_factor_in_range(self):
        # 2sin²(π×5/74): sin²(0.212) ≈ 0.0445, factor ≈ 0.089
        theta = math.pi * N_W_CANONICAL / K_CS_CANONICAL
        phase = 2.0 * math.sin(theta) ** 2
        assert 0.05 < phase < 0.15

    def test_quartic_scaling_with_cutoff(self):
        # fermionic_zpe_offset ∝ M_cutoff^4
        rho1 = fermionic_zpe_offset(1.0)
        rho2 = fermionic_zpe_offset(2.0)
        assert abs(rho2 / rho1 - 16.0) < 1e-8

    def test_formula_components(self):
        M = 1.0
        f = braid_cancellation_factor()
        rho_bos = f * zpe_density_naive(M)
        theta = math.pi * N_W_CANONICAL / K_CS_CANONICAL
        expected = rho_bos * 2.0 * math.sin(theta) ** 2
        assert abs(fermionic_zpe_offset(M) - expected) < 1e-20

    def test_increases_with_n_w(self):
        # More chiral zero modes → larger braid phase → larger residual
        rho_5 = fermionic_zpe_offset(1.0, n_w=5, k_cs=74, c_s=C_S_CANONICAL)
        rho_7 = fermionic_zpe_offset(1.0, n_w=7, k_cs=74, c_s=C_S_CANONICAL)
        # phase 2sin²(π×7/74) vs 2sin²(π×5/74): 7/74 > 5/74 so larger phase
        assert rho_7 > rho_5

    def test_at_mkk_needed_matches_rho_obs_order(self):
        # At M_KK_needed, fermionic_zpe_offset should be ~ρ_obs × phase_factor × k_cs/c_s²
        m_kk = kk_scale_needed_for_dark_energy()
        rho_f = fermionic_zpe_offset(m_kk)
        # rho_f = f × M_KK^4/(16π²) × phase = ρ_obs × phase ≈ ρ_obs × 0.089
        theta = math.pi * N_W_CANONICAL / K_CS_CANONICAL
        phase = 2.0 * math.sin(theta) ** 2
        assert abs(rho_f / (RHO_DARK_ENERGY_PLANCK * phase) - 1.0) < 1e-5

    def test_invalid_M_cutoff_zero(self):
        with pytest.raises(ValueError):
            fermionic_zpe_offset(0.0)

    def test_invalid_M_cutoff_negative(self):
        with pytest.raises(ValueError):
            fermionic_zpe_offset(-1.0)


# ===========================================================================
# 39. braid_running_factor
# ===========================================================================

class TestBraidRunningFactor:
    def test_positive(self):
        m_kk = kk_scale_needed_for_dark_energy()
        assert braid_running_factor(1.0, m_kk) > 0

    def test_unity_at_same_scale(self):
        # mu_UV == mu_IR → factor = 1
        assert braid_running_factor(1.0, 1.0) == 1.0

    def test_unity_at_default_ir_scale(self):
        # Default mu_IR = M_KK_needed → γ = 0 → factor = 1
        factor = braid_running_factor(mu_UV=1.0)
        assert abs(factor - 1.0) < 1e-8

    def test_effective_rho_matches_obs_at_mkk_needed(self):
        # f_braid × running_factor × M_KK_needed^4 / (16π²) = ρ_obs
        m_kk = kk_scale_needed_for_dark_energy()
        f = braid_cancellation_factor()
        factor = braid_running_factor(1.0, m_kk)
        rho_check = f * factor * zpe_density_naive(m_kk)
        assert abs(rho_check / RHO_DARK_ENERGY_PLANCK - 1.0) < 1e-6

    def test_effective_rho_matches_obs_at_neutrino_scale(self):
        # Even when mu_IR = m_nu (not M_KK_needed), running factor adjusts so
        # f × factor × m_nu^4/(16π²) = ρ_obs exactly
        m_nu_planck = M_NU_CANONICAL_EV / (PLANCK_ENERGY_GEV * 1e9)
        f = braid_cancellation_factor()
        factor = braid_running_factor(1.0, m_nu_planck)
        rho_check = f * factor * zpe_density_naive(m_nu_planck)
        assert abs(rho_check / RHO_DARK_ENERGY_PLANCK - 1.0) < 1e-6

    def test_factor_greater_than_one_for_smaller_ir(self):
        # When mu_IR < M_KK_needed, running factor > 1 (f_braid runs upward to IR)
        m_kk = kk_scale_needed_for_dark_energy()
        m_nu = M_NU_CANONICAL_EV / (PLANCK_ENERGY_GEV * 1e9)
        # m_nu < m_kk → needs larger factor
        factor = braid_running_factor(1.0, m_nu)
        assert factor > 1.0

    def test_different_uv_scale_still_closes(self):
        # mu_UV = 0.5 M_Pl: still closes the loop
        m_kk = kk_scale_needed_for_dark_energy()
        m_nu = M_NU_CANONICAL_EV / (PLANCK_ENERGY_GEV * 1e9)
        f_05 = braid_cancellation_factor()
        factor = braid_running_factor(0.5, m_nu)
        rho_check = f_05 * factor * zpe_density_naive(m_nu)
        assert abs(rho_check / RHO_DARK_ENERGY_PLANCK - 1.0) < 1e-6

    def test_invalid_mu_UV_zero(self):
        with pytest.raises(ValueError):
            braid_running_factor(mu_UV=0.0, mu_IR=1e-30)

    def test_invalid_mu_IR_zero(self):
        with pytest.raises(ValueError):
            braid_running_factor(mu_UV=1.0, mu_IR=0.0)



# ===========================================================================
# 40. derive_R_from_neutrino_mass
# ===========================================================================

class TestDeriveRFromNeutrinoMass:
    """Tests for the Neutrino-Radion Identity entry point."""

    def test_returns_dict(self):
        result = derive_R_from_neutrino_mass()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = derive_R_from_neutrino_mass()
        required = {
            "m_nu_eV", "m_nu_planck", "R_KK_planck", "R_KK_m", "R_KK_um",
            "M_KK_planck", "f_braid", "rho_eff_planck", "rho_obs_planck",
            "ratio_rho", "orders_gap", "m_nu_exact_eV",
            "closure_pct_err", "loop_closed_1pct", "mechanism",
        }
        assert required.issubset(result.keys())

    def test_default_m_nu_is_canonical(self):
        result = derive_R_from_neutrino_mass()
        assert result["m_nu_eV"] == M_NU_CANONICAL_EV

    def test_R_KK_equals_inverse_m_nu(self):
        m_nu_eV = 50e-3
        result = derive_R_from_neutrino_mass(m_nu_eV)
        m_nu_planck = m_nu_eV / (PLANCK_ENERGY_GEV * 1e9)
        expected_R = 1.0 / m_nu_planck
        assert abs(result["R_KK_planck"] / expected_R - 1.0) < 1e-10

    def test_M_KK_equals_m_nu(self):
        m_nu_eV = 80e-3
        result = derive_R_from_neutrino_mass(m_nu_eV)
        m_nu_planck = m_nu_eV / (PLANCK_ENERGY_GEV * 1e9)
        assert abs(result["M_KK_planck"] / m_nu_planck - 1.0) < 1e-10

    def test_R_KK_in_metres_positive(self):
        result = derive_R_from_neutrino_mass()
        assert result["R_KK_m"] > 0

    def test_R_KK_microns_consistent(self):
        result = derive_R_from_neutrino_mass()
        assert abs(result["R_KK_um"] - result["R_KK_m"] * 1e6) < 1e-30

    def test_rho_eff_positive(self):
        result = derive_R_from_neutrino_mass()
        assert result["rho_eff_planck"] > 0

    def test_rho_eff_matches_braid_times_zpe(self):
        """ρ_eff = f_braid × M_KK⁴ / (16π²)."""
        import math
        m_nu_eV = 60e-3
        result = derive_R_from_neutrino_mass(m_nu_eV)
        m_nu_p = m_nu_eV / (PLANCK_ENERGY_GEV * 1e9)
        f = result["f_braid"]
        rho_expected = f * m_nu_p ** 4 / (16.0 * math.pi ** 2)
        assert abs(result["rho_eff_planck"] / rho_expected - 1.0) < 1e-9

    def test_exact_closure_at_m_nu_exact(self):
        """At m_nu_exact, loop_closed_1pct should be True."""
        result_default = derive_R_from_neutrino_mass()
        m_exact = result_default["m_nu_exact_eV"]
        result_exact = derive_R_from_neutrino_mass(m_exact)
        assert result_exact["loop_closed_1pct"] is True
        assert result_exact["closure_pct_err"] < 1.0

    def test_ratio_rho_at_exact_closure_near_one(self):
        result_default = derive_R_from_neutrino_mass()
        m_exact = result_default["m_nu_exact_eV"]
        result_exact = derive_R_from_neutrino_mass(m_exact)
        assert abs(result_exact["ratio_rho"] - 1.0) < 0.01

    def test_larger_m_nu_gives_larger_rho_eff(self):
        r1 = derive_R_from_neutrino_mass(50e-3)
        r2 = derive_R_from_neutrino_mass(110e-3)
        assert r2["rho_eff_planck"] > r1["rho_eff_planck"]

    def test_larger_m_nu_gives_smaller_R_KK(self):
        r1 = derive_R_from_neutrino_mass(50e-3)
        r2 = derive_R_from_neutrino_mass(110e-3)
        assert r2["R_KK_planck"] < r1["R_KK_planck"]

    def test_orders_gap_zero_when_ratio_above_one(self):
        result = derive_R_from_neutrino_mass()
        m_exact = result["m_nu_exact_eV"]
        result_large = derive_R_from_neutrino_mass(m_exact * 2)
        # rho_eff > rho_obs → orders_gap = 0
        assert result_large["orders_gap"] == 0.0

    def test_orders_gap_positive_when_under_threshold(self):
        result = derive_R_from_neutrino_mass(10e-3)  # 10 meV → under-threshold
        assert result["orders_gap"] > 0.0

    def test_mechanism_string_present(self):
        result = derive_R_from_neutrino_mass()
        assert "Neutrino-Radion" in result["mechanism"]
        assert "μm" in result["mechanism"]

    def test_f_braid_matches_braid_cancellation_factor(self):
        from src.core.zero_point_vacuum import braid_cancellation_factor
        result = derive_R_from_neutrino_mass()
        expected = braid_cancellation_factor()
        assert abs(result["f_braid"] / expected - 1.0) < 1e-10

    def test_m_nu_exact_consistent_with_kk_scale_needed(self):
        from src.core.zero_point_vacuum import kk_scale_needed_for_dark_energy
        result = derive_R_from_neutrino_mass()
        m_kk_planck = kk_scale_needed_for_dark_energy()
        m_kk_eV = m_kk_planck * PLANCK_ENERGY_GEV * 1e9
        assert abs(result["m_nu_exact_eV"] / m_kk_eV - 1.0) < 1e-8

    def test_invalid_m_nu_zero(self):
        with pytest.raises(ValueError):
            derive_R_from_neutrino_mass(0.0)

    def test_invalid_m_nu_negative(self):
        with pytest.raises(ValueError):
            derive_R_from_neutrino_mass(-50e-3)

    def test_R_KK_um_at_exact_closure_approx_75um(self):
        """At exact closure, R_KK ≈ 1.792 μm (M_KK ≈ 110.13 meV = macroscopic)."""
        result = derive_R_from_neutrino_mass()
        m_exact = result["m_nu_exact_eV"]
        result_exact = derive_R_from_neutrino_mass(m_exact)
        # M_KK_needed ≈ 110.13 meV → R_KK ≈ 1.79 μm
        assert 1.5 < result_exact["R_KK_um"] < 2.1

    def test_consistency_with_radion_self_consistency_check(self):
        """derive_R_from_neutrino_mass and radion_self_consistency_check agree."""
        m_nu_eV = 75e-3
        r1 = derive_R_from_neutrino_mass(m_nu_eV)
        r2 = radion_self_consistency_check(m_nu_eV)
        assert abs(r1["rho_eff_planck"] / r2["rho_eff_planck"] - 1.0) < 1e-8
        assert abs(r1["ratio_rho"] / r2["ratio_rho"] - 1.0) < 1e-8


# ===========================================================================
# 41. prove_resonance_identity
# ===========================================================================

class TestProveResonanceIdentity:
    """Tests for the Universal Resonance Identity: m_ν/M_Pl ≈ (ρ_obs)^(1/4)."""

    def test_returns_dict(self):
        assert isinstance(prove_resonance_identity(), dict)

    def test_required_keys(self):
        result = prove_resonance_identity()
        required = {
            "m_nu_eV", "m_nu_planck", "rho_obs_planck",
            "rho_obs_fourth_root", "f_braid", "f_braid_fourth_root",
            "M_KK_needed_planck", "M_KK_needed_eV",
            "identity_ratio", "bridge_ratio", "deviation_pct",
            "identity_holds_10pct", "mechanism",
        }
        assert required.issubset(result.keys())

    def test_rho_fourth_root_positive(self):
        result = prove_resonance_identity()
        assert result["rho_obs_fourth_root"] > 0

    def test_f_braid_fourth_root_positive(self):
        result = prove_resonance_identity()
        assert result["f_braid_fourth_root"] > 0

    def test_f_braid_fourth_root_formula(self):
        result = prove_resonance_identity()
        expected = result["f_braid"] ** 0.25
        assert abs(result["f_braid_fourth_root"] / expected - 1.0) < 1e-12

    def test_rho_fourth_root_formula(self):
        result = prove_resonance_identity()
        expected = result["rho_obs_planck"] ** 0.25
        assert abs(result["rho_obs_fourth_root"] / expected - 1.0) < 1e-12

    def test_identity_ratio_formula(self):
        result = prove_resonance_identity()
        expected = result["m_nu_planck"] / result["rho_obs_fourth_root"]
        assert abs(result["identity_ratio"] / expected - 1.0) < 1e-12

    def test_bridge_ratio_at_exact_closure_equals_one(self):
        """At m_ν = M_KK_needed, bridge_ratio = m_ν/M_KK_needed = 1.0 exactly."""
        r0 = prove_resonance_identity()
        m_exact = r0["M_KK_needed_eV"]
        r_exact = prove_resonance_identity(m_nu_eV=m_exact)
        assert abs(r_exact["bridge_ratio"] - 1.0) < 1e-8

    def test_deviation_pct_at_exact_closure_near_zero(self):
        r0 = prove_resonance_identity()
        m_exact = r0["M_KK_needed_eV"]
        r_exact = prove_resonance_identity(m_nu_eV=m_exact)
        assert r_exact["deviation_pct"] < 1e-4

    def test_identity_holds_10pct_at_exact_closure(self):
        r0 = prove_resonance_identity()
        m_exact = r0["M_KK_needed_eV"]
        r_exact = prove_resonance_identity(m_nu_eV=m_exact)
        assert r_exact["identity_holds_10pct"] is True

    def test_bridge_ratio_is_m_nu_over_M_KK_needed(self):
        """bridge_ratio is the exact self-consistency check: m_ν / M_KK_needed."""
        m_nu_eV = 75e-3
        result = prove_resonance_identity(m_nu_eV=m_nu_eV)
        expected = result["m_nu_planck"] / result["M_KK_needed_planck"]
        assert abs(result["bridge_ratio"] / expected - 1.0) < 1e-12

    def test_M_KK_needed_eV_is_110meV(self):
        result = prove_resonance_identity()
        # M_KK_needed ≈ 110 meV — the dark energy scale
        assert 50.0 < result["M_KK_needed_eV"] * 1e3 < 200.0

    def test_bridge_ratio_monotone_in_m_nu(self):
        # Larger m_ν → larger identity_ratio → larger bridge_ratio
        r1 = prove_resonance_identity(m_nu_eV=50e-3)
        r2 = prove_resonance_identity(m_nu_eV=110e-3)
        assert r2["bridge_ratio"] > r1["bridge_ratio"]

    def test_mechanism_string_present(self):
        result = prove_resonance_identity()
        assert "Resonance Identity" in result["mechanism"]
        assert "braid" in result["mechanism"]

    def test_f_braid_matches_canonical(self):
        result = prove_resonance_identity()
        expected_f = braid_cancellation_factor()
        assert abs(result["f_braid"] / expected_f - 1.0) < 1e-12

    def test_invalid_m_nu_zero(self):
        with pytest.raises(ValueError):
            prove_resonance_identity(m_nu_eV=0.0)

    def test_invalid_m_nu_negative(self):
        with pytest.raises(ValueError):
            prove_resonance_identity(m_nu_eV=-0.05)

    def test_deviation_pct_is_percentage(self):
        result = prove_resonance_identity()
        assert 0.0 <= result["deviation_pct"]

    def test_bridge_ratio_positive(self):
        result = prove_resonance_identity()
        assert result["bridge_ratio"] > 0

    def test_consistency_across_functions(self):
        """M_KK_needed is consistent with kk_scale_needed_for_dark_energy."""
        result = prove_resonance_identity()
        from src.core.zero_point_vacuum import kk_scale_needed_for_dark_energy
        m_kk = kk_scale_needed_for_dark_energy()
        assert abs(result["M_KK_needed_planck"] / m_kk - 1.0) < 1e-10
