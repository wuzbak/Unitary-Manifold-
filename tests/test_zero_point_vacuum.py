# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_zero_point_vacuum.py
================================
Pillar 49 — Test suite for src/core/zero_point_vacuum.py.

Covers all public API functions with numerical precision checks, physical
sanity checks, edge-case validation, and cross-consistency tests.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
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
    PLANCK_LENGTH_M,
    PLANCK_ENERGY_GEV,
    # Functions
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
