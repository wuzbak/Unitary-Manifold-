# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_torsion_remnant.py
==============================
Test suite for src/core/torsion_remnant.py  (Pillar 48)

Covers:
  - Module constants (G₂ remnant mass, UM constants, QNM coefficients)
  - g2_remnant_mass_planck()
  - torsion_repulsion_pressure()
  - torsion_planck_floor_density()
  - um_ec_torsion_correction()
  - um_ec_remnant_mass()
  - qnm_frequency_fundamental()
  - qnm_decay_rate()
  - qnm_lifetime()
  - qnm_oscillation_count()
  - qnm_information_capacity_bits()
  - torsion_extended_qnm_lifetime()
  - electroweak_scale_ratio_um()
  - electroweak_scale_ratio_observed()
  - higgs_scale_discrepancy_factor()
  - remnant_mass_ratio_5d_to_7d()
  - TorsionComparison dataclass
  - compare_frameworks()
"""

import math

import pytest

from src.core.torsion_remnant import (
    C_S_CANONICAL,
    DIMENSION_COUNT_G2,
    DIMENSION_COUNT_UM,
    EXTRA_DIMS_G2,
    EXTRA_DIMS_UM,
    G2_REMNANT_MASS_KG,
    G2_REMNANT_MASS_PLANCK,
    HIGGS_MASS_GEV,
    HIGGS_VEV_GEV,
    K_CS_CANONICAL,
    M_PHI_CANONICAL,
    N_W_CANONICAL,
    PHI0_CANONICAL,
    PHI_MIN_CANONICAL,
    PLANCK_MASS_GEV,
    PLANCK_MASS_KG,
    TorsionComparison,
    compare_frameworks,
    electroweak_scale_ratio_observed,
    electroweak_scale_ratio_um,
    g2_remnant_mass_planck,
    higgs_scale_discrepancy_factor,
    qnm_decay_rate,
    qnm_frequency_fundamental,
    qnm_information_capacity_bits,
    qnm_lifetime,
    qnm_oscillation_count,
    remnant_mass_ratio_5d_to_7d,
    torsion_extended_qnm_lifetime,
    torsion_planck_floor_density,
    torsion_repulsion_pressure,
    um_ec_remnant_mass,
    um_ec_torsion_correction,
)


# ===========================================================================
# TestConstants
# ===========================================================================

class TestConstants:

    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert C_S_CANONICAL == pytest.approx(12.0 / 37.0, rel=1e-12)

    def test_phi0_canonical(self):
        assert PHI0_CANONICAL == pytest.approx(1.0)

    def test_m_phi_canonical(self):
        assert M_PHI_CANONICAL == pytest.approx(1.0)

    def test_phi_min_canonical(self):
        assert PHI_MIN_CANONICAL == pytest.approx(0.1)

    def test_g2_mass_kg(self):
        assert G2_REMNANT_MASS_KG == pytest.approx(9.0e-41, rel=1e-6)

    def test_planck_mass_kg(self):
        assert PLANCK_MASS_KG == pytest.approx(2.176434e-8, rel=1e-5)

    def test_g2_mass_planck_formula(self):
        assert G2_REMNANT_MASS_PLANCK == pytest.approx(
            G2_REMNANT_MASS_KG / PLANCK_MASS_KG, rel=1e-10
        )

    def test_g2_mass_planck_tiny(self):
        assert G2_REMNANT_MASS_PLANCK < 1e-30

    def test_higgs_vev_246(self):
        assert HIGGS_VEV_GEV == pytest.approx(246.0, rel=1e-6)

    def test_higgs_mass_125(self):
        assert HIGGS_MASS_GEV == pytest.approx(125.09, rel=1e-4)

    def test_planck_mass_gev_order(self):
        assert 1e18 < PLANCK_MASS_GEV < 2e19

    def test_dimension_count_um(self):
        assert DIMENSION_COUNT_UM == 5

    def test_dimension_count_g2(self):
        assert DIMENSION_COUNT_G2 == 7

    def test_extra_dims_um(self):
        assert EXTRA_DIMS_UM == 1

    def test_extra_dims_g2(self):
        assert EXTRA_DIMS_G2 == 3

    def test_k_cs_sum_of_squares(self):
        assert N_W_CANONICAL ** 2 + 7 ** 2 == K_CS_CANONICAL


# ===========================================================================
# TestG2RemnantMass
# ===========================================================================

class TestG2RemnantMass:

    def test_returns_float(self):
        assert isinstance(g2_remnant_mass_planck(), float)

    def test_value_matches_constant(self):
        assert g2_remnant_mass_planck() == pytest.approx(G2_REMNANT_MASS_PLANCK, rel=1e-12)

    def test_positive(self):
        assert g2_remnant_mass_planck() > 0.0

    def test_tiny_compared_to_planck(self):
        assert g2_remnant_mass_planck() < 1e-30

    def test_kg_to_planck_conversion(self):
        expected = 9.0e-41 / 2.176434e-8
        assert g2_remnant_mass_planck() == pytest.approx(expected, rel=1e-5)


# ===========================================================================
# TestTorsionRepulsionPressure
# ===========================================================================

class TestTorsionRepulsionPressure:

    def test_zero_density(self):
        assert torsion_repulsion_pressure(0.0, 1.0) == pytest.approx(0.0)

    def test_planck_density_unit_coupling(self):
        # rho=1, kappa=1 → p_T = 1/(8π)
        result = torsion_repulsion_pressure(1.0, 1.0)
        assert result == pytest.approx(1.0 / (8.0 * math.pi), rel=1e-10)

    def test_quadratic_in_rho(self):
        p1 = torsion_repulsion_pressure(1.0, 2.0)
        p2 = torsion_repulsion_pressure(2.0, 2.0)
        assert p2 == pytest.approx(4.0 * p1, rel=1e-10)

    def test_linear_in_kappa(self):
        p1 = torsion_repulsion_pressure(1.0, 1.0)
        p2 = torsion_repulsion_pressure(1.0, 3.0)
        assert p2 == pytest.approx(3.0 * p1, rel=1e-10)

    def test_positive_result(self):
        assert torsion_repulsion_pressure(0.5, 0.5) > 0.0

    def test_negative_rho_raises(self):
        with pytest.raises(ValueError, match="rho"):
            torsion_repulsion_pressure(-0.1, 1.0)

    def test_zero_kappa_raises(self):
        with pytest.raises(ValueError, match="kappa_torsion"):
            torsion_repulsion_pressure(1.0, 0.0)

    def test_negative_kappa_raises(self):
        with pytest.raises(ValueError, match="kappa_torsion"):
            torsion_repulsion_pressure(1.0, -1.0)


# ===========================================================================
# TestTorsionPlanckFloorDensity
# ===========================================================================

class TestTorsionPlanckFloorDensity:

    def test_formula(self):
        kappa = 2.5
        assert torsion_planck_floor_density(kappa) == pytest.approx(
            8.0 * math.pi / kappa, rel=1e-12
        )

    def test_positive(self):
        assert torsion_planck_floor_density(1.0) > 0.0

    def test_large_kappa_small_floor(self):
        assert torsion_planck_floor_density(100.0) < 1.0

    def test_small_kappa_large_floor(self):
        assert torsion_planck_floor_density(0.01) > 100.0

    def test_zero_kappa_raises(self):
        with pytest.raises(ValueError, match="kappa_torsion"):
            torsion_planck_floor_density(0.0)

    def test_negative_kappa_raises(self):
        with pytest.raises(ValueError, match="kappa_torsion"):
            torsion_planck_floor_density(-1.0)


# ===========================================================================
# TestUmEcTorsionCorrection
# ===========================================================================

class TestUmEcTorsionCorrection:

    def test_zero_coupling(self):
        assert um_ec_torsion_correction(0.1, 0.0) == pytest.approx(0.0)

    def test_formula(self):
        phi_min, kappa = 0.1, 0.5
        expected = kappa * (5 / 74) ** 2 * phi_min
        assert um_ec_torsion_correction(phi_min, kappa) == pytest.approx(
            expected, rel=1e-12
        )

    def test_proportional_to_phi_min(self):
        d1 = um_ec_torsion_correction(0.1, 1.0)
        d2 = um_ec_torsion_correction(0.2, 1.0)
        assert d2 == pytest.approx(2.0 * d1, rel=1e-12)

    def test_proportional_to_kappa(self):
        d1 = um_ec_torsion_correction(0.1, 1.0)
        d2 = um_ec_torsion_correction(0.1, 2.0)
        assert d2 == pytest.approx(2.0 * d1, rel=1e-12)

    def test_nonnegative(self):
        assert um_ec_torsion_correction(0.1, 0.5) >= 0.0

    def test_phi_min_zero_raises(self):
        with pytest.raises(ValueError, match="phi_min"):
            um_ec_torsion_correction(0.0, 1.0)

    def test_phi_min_negative_raises(self):
        with pytest.raises(ValueError, match="phi_min"):
            um_ec_torsion_correction(-0.1, 1.0)

    def test_negative_kappa_raises(self):
        with pytest.raises(ValueError, match="kappa_torsion"):
            um_ec_torsion_correction(0.1, -0.5)

    def test_custom_n_w_k_cs(self):
        result = um_ec_torsion_correction(0.1, 1.0, n_w=3, k_cs=10)
        expected = 1.0 * (3 / 10) ** 2 * 0.1
        assert result == pytest.approx(expected, rel=1e-12)


# ===========================================================================
# TestUmEcRemnantMass
# ===========================================================================

class TestUmEcRemnantMass:

    def test_zero_torsion_matches_gw(self):
        from src.core.bh_remnant import remnant_mass
        M_gw = remnant_mass(0.1, 1.0, 1.0)
        M_ec = um_ec_remnant_mass(0.1, 1.0, 1.0, 0.0)
        assert M_ec == pytest.approx(M_gw, rel=1e-12)

    def test_positive_torsion_increases_mass(self):
        M0 = um_ec_remnant_mass(0.1, 1.0, 1.0, 0.0)
        M1 = um_ec_remnant_mass(0.1, 1.0, 1.0, 0.1)
        assert M1 > M0

    def test_positive_result(self):
        assert um_ec_remnant_mass(0.1, 1.0, 1.0, 0.05) > 0.0

    def test_nonphysical_phi0_raises(self):
        # kappa=500 pushes phi_min_eff = 0.1*(1 + 500*(5/74)^2) ≈ 0.328 > phi0=0.11
        with pytest.raises(ValueError):
            um_ec_remnant_mass(0.1, 1.0, 0.11, kappa_torsion=500.0)

    def test_m_phi_zero_raises(self):
        with pytest.raises(ValueError, match="m_phi"):
            um_ec_remnant_mass(0.1, 0.0, 1.0)

    def test_negative_kappa_raises(self):
        with pytest.raises(ValueError, match="kappa_torsion"):
            um_ec_remnant_mass(0.1, 1.0, 1.0, -0.1)

    def test_monotone_in_kappa(self):
        masses = [um_ec_remnant_mass(0.1, 1.0, 1.0, k) for k in [0.0, 0.01, 0.05, 0.1]]
        assert all(masses[i] < masses[i + 1] for i in range(len(masses) - 1))

    def test_canonical_parameters(self):
        M = um_ec_remnant_mass(PHI_MIN_CANONICAL, M_PHI_CANONICAL, PHI0_CANONICAL, 0.0)
        # M_rem = 0.1 / (8π × 1.0 × 0.9) ≈ 4.42e-3
        assert M == pytest.approx(0.1 / (8.0 * math.pi * 0.9), rel=1e-10)


# ===========================================================================
# TestQnmFrequencyFundamental
# ===========================================================================

class TestQnmFrequencyFundamental:

    def test_formula(self):
        M = 0.01
        assert qnm_frequency_fundamental(M) == pytest.approx(0.3737 / (2 * M), rel=1e-10)

    def test_positive(self):
        assert qnm_frequency_fundamental(0.01) > 0.0

    def test_inverse_mass_scaling(self):
        f1 = qnm_frequency_fundamental(1.0)
        f2 = qnm_frequency_fundamental(2.0)
        assert f1 == pytest.approx(2.0 * f2, rel=1e-10)

    def test_zero_mass_raises(self):
        with pytest.raises(ValueError, match="M_rem"):
            qnm_frequency_fundamental(0.0)

    def test_negative_mass_raises(self):
        with pytest.raises(ValueError, match="M_rem"):
            qnm_frequency_fundamental(-1.0)

    def test_large_remnant_small_frequency(self):
        assert qnm_frequency_fundamental(1e6) < 1e-5


# ===========================================================================
# TestQnmDecayRate
# ===========================================================================

class TestQnmDecayRate:

    def test_formula(self):
        M = 0.01
        assert qnm_decay_rate(M) == pytest.approx(0.0890 / (2 * M), rel=1e-10)

    def test_positive(self):
        assert qnm_decay_rate(0.01) > 0.0

    def test_inverse_mass_scaling(self):
        r1 = qnm_decay_rate(1.0)
        r2 = qnm_decay_rate(2.0)
        assert r1 == pytest.approx(2.0 * r2, rel=1e-10)

    def test_zero_mass_raises(self):
        with pytest.raises(ValueError, match="M_rem"):
            qnm_decay_rate(0.0)

    def test_decay_rate_less_than_frequency(self):
        M = 0.05
        assert qnm_decay_rate(M) < qnm_frequency_fundamental(M)


# ===========================================================================
# TestQnmLifetime
# ===========================================================================

class TestQnmLifetime:

    def test_is_inverse_decay_rate(self):
        M = 0.05
        assert qnm_lifetime(M) == pytest.approx(1.0 / qnm_decay_rate(M), rel=1e-12)

    def test_proportional_to_mass(self):
        tau1 = qnm_lifetime(1.0)
        tau2 = qnm_lifetime(2.0)
        assert tau2 == pytest.approx(2.0 * tau1, rel=1e-10)

    def test_positive(self):
        assert qnm_lifetime(0.1) > 0.0

    def test_formula(self):
        M = 0.1
        expected = 2.0 * M / 0.0890
        assert qnm_lifetime(M) == pytest.approx(expected, rel=1e-10)


# ===========================================================================
# TestQnmOscillationCount
# ===========================================================================

class TestQnmOscillationCount:

    def test_mass_independent(self):
        n1 = qnm_oscillation_count(0.01)
        n2 = qnm_oscillation_count(1.0)
        assert n1 == pytest.approx(n2, rel=1e-10)

    def test_value(self):
        assert qnm_oscillation_count(0.05) == pytest.approx(0.3737 / 0.0890, rel=1e-8)

    def test_above_four(self):
        assert qnm_oscillation_count(1.0) > 4.0

    def test_below_five(self):
        assert qnm_oscillation_count(1.0) < 5.0

    def test_zero_mass_raises(self):
        with pytest.raises(ValueError, match="M_rem"):
            qnm_oscillation_count(0.0)


# ===========================================================================
# TestQnmInformationCapacityBits
# ===========================================================================

class TestQnmInformationCapacityBits:

    def test_l_max_2_single_mode(self):
        # Only l=2: log2(5) ≈ 2.322 bits
        result = qnm_information_capacity_bits(10.0, l_max=2)
        assert result == pytest.approx(math.log2(5), rel=1e-10)

    def test_l_max_3_two_modes(self):
        # l=2: log2(5), l=3: log2(7)
        result = qnm_information_capacity_bits(10.0, l_max=3)
        expected = math.log2(5) + math.log2(7)
        assert result == pytest.approx(expected, rel=1e-10)

    def test_increases_with_l_max(self):
        b1 = qnm_information_capacity_bits(10.0, l_max=5)
        b2 = qnm_information_capacity_bits(10.0, l_max=10)
        assert b2 > b1

    def test_positive(self):
        assert qnm_information_capacity_bits(1.0, l_max=5) > 0.0

    def test_zero_mass_raises(self):
        with pytest.raises(ValueError, match="M_rem"):
            qnm_information_capacity_bits(0.0)

    def test_l_max_below_2_raises(self):
        with pytest.raises(ValueError, match="l_max"):
            qnm_information_capacity_bits(1.0, l_max=1)

    def test_large_mass_uses_full_l_max(self):
        # For M_rem >> 1 all modes up to l_max are physically supported
        b = qnm_information_capacity_bits(1e6, l_max=10)
        expected = sum(math.log2(2 * l + 1) for l in range(2, 11))
        assert b == pytest.approx(expected, rel=1e-10)

    def test_small_mass_truncates(self):
        # For very small M_rem, l_max_physical < 10
        b_small = qnm_information_capacity_bits(0.01, l_max=10)
        b_large = qnm_information_capacity_bits(100.0, l_max=10)
        assert b_small <= b_large

    def test_bits_less_than_bh_entropy(self):
        M = 1.0
        qnm_bits = qnm_information_capacity_bits(M, l_max=10)
        bh_bits = 4.0 * math.pi * M ** 2 / math.log(2.0)
        assert qnm_bits <= bh_bits


# ===========================================================================
# TestTorsionExtendedQnmLifetime
# ===========================================================================

class TestTorsionExtendedQnmLifetime:

    def test_zero_torsion_equals_standard(self):
        M = 0.1
        assert torsion_extended_qnm_lifetime(M, 0.0) == pytest.approx(
            qnm_lifetime(M), rel=1e-12
        )

    def test_positive_torsion_extends(self):
        M = 0.1
        assert torsion_extended_qnm_lifetime(M, 1.0) > qnm_lifetime(M)

    def test_formula(self):
        M, kappa = 0.1, 0.5
        factor = 1.0 + kappa * (5 / 74) ** 2
        expected = qnm_lifetime(M) * factor
        assert torsion_extended_qnm_lifetime(M, kappa) == pytest.approx(expected, rel=1e-10)

    def test_proportional_to_mass(self):
        tau1 = torsion_extended_qnm_lifetime(1.0, 0.5)
        tau2 = torsion_extended_qnm_lifetime(2.0, 0.5)
        assert tau2 == pytest.approx(2.0 * tau1, rel=1e-10)

    def test_zero_mass_raises(self):
        with pytest.raises(ValueError, match="M_rem"):
            torsion_extended_qnm_lifetime(0.0, 1.0)

    def test_negative_kappa_raises(self):
        with pytest.raises(ValueError, match="kappa_torsion"):
            torsion_extended_qnm_lifetime(0.1, -0.5)

    def test_large_kappa_large_lifetime(self):
        assert torsion_extended_qnm_lifetime(0.1, 100.0) > torsion_extended_qnm_lifetime(0.1, 1.0)


# ===========================================================================
# TestElectroweakScaleRatioUm
# ===========================================================================

class TestElectroweakScaleRatioUm:

    def test_formula(self):
        expected = math.sqrt((12.0 / 37.0) / 74)
        assert electroweak_scale_ratio_um() == pytest.approx(expected, rel=1e-12)

    def test_positive(self):
        assert electroweak_scale_ratio_um() > 0.0

    def test_less_than_one(self):
        assert electroweak_scale_ratio_um() < 1.0

    def test_much_greater_than_observed(self):
        ratio_um = electroweak_scale_ratio_um()
        ratio_obs = electroweak_scale_ratio_observed()
        assert ratio_um > 1e12 * ratio_obs

    def test_custom_params(self):
        result = electroweak_scale_ratio_um(c_s=0.5, k_cs=100)
        assert result == pytest.approx(math.sqrt(0.5 / 100), rel=1e-12)


# ===========================================================================
# TestElectroweakScaleRatioObserved
# ===========================================================================

class TestElectroweakScaleRatioObserved:

    def test_formula(self):
        assert electroweak_scale_ratio_observed() == pytest.approx(
            246.0 / 1.220890e19, rel=1e-5
        )

    def test_tiny(self):
        assert electroweak_scale_ratio_observed() < 1e-15

    def test_positive(self):
        assert electroweak_scale_ratio_observed() > 0.0


# ===========================================================================
# TestHiggsScaleDiscrepancyFactor
# ===========================================================================

class TestHiggsScaleDiscrepancyFactor:

    def test_large_discrepancy(self):
        # UM EW scale >> observed EW scale → large ratio
        assert higgs_scale_discrepancy_factor() > 1e12

    def test_formula(self):
        ratio_um = electroweak_scale_ratio_um()
        ratio_obs = electroweak_scale_ratio_observed()
        assert higgs_scale_discrepancy_factor() == pytest.approx(
            ratio_um / ratio_obs, rel=1e-10
        )

    def test_positive(self):
        assert higgs_scale_discrepancy_factor() > 0.0


# ===========================================================================
# TestRemnantMassRatio5dTo7d
# ===========================================================================

class TestRemnantMassRatio5dTo7d:

    def test_much_larger_than_one(self):
        # UM 5D remnant >> G₂ 7D remnant in Planck units
        assert remnant_mass_ratio_5d_to_7d() > 1e25

    def test_positive(self):
        assert remnant_mass_ratio_5d_to_7d() > 0.0

    def test_consistent_with_individual_values(self):
        from src.core.bh_remnant import remnant_mass
        M_5d = remnant_mass(PHI_MIN_CANONICAL, M_PHI_CANONICAL, PHI0_CANONICAL)
        M_7d = G2_REMNANT_MASS_PLANCK
        assert remnant_mass_ratio_5d_to_7d() == pytest.approx(M_5d / M_7d, rel=1e-10)

    def test_custom_params(self):
        r1 = remnant_mass_ratio_5d_to_7d(0.05, 1.0, 1.0)
        r2 = remnant_mass_ratio_5d_to_7d(0.10, 1.0, 1.0)
        # Smaller phi_min → smaller M_rem_5d → smaller ratio
        assert r1 < r2


# ===========================================================================
# TestCompareFrameworks
# ===========================================================================

class TestCompareFrameworks:

    @pytest.fixture(scope="class")
    def result(self):
        return compare_frameworks()

    def test_returns_torsion_comparison(self, result):
        assert isinstance(result, TorsionComparison)

    def test_qualitative_agreement_true(self, result):
        assert result.qualitative_agreement is True

    def test_dimension_counts(self, result):
        assert result.dimension_count_um == 5
        assert result.dimension_count_g2 == 7

    def test_g2_mass_tiny(self, result):
        assert result.g2_7d_M_rem < 1e-30

    def test_um_mass_much_larger(self, result):
        assert result.um_5d_M_rem > 1e-5

    def test_ratio_5d_to_7d_large(self, result):
        assert result.ratio_5d_to_7d > 1e25

    def test_ec_mass_larger_than_gw_mass(self, result):
        assert result.um_ec_M_rem >= result.um_5d_M_rem

    def test_ratio_ec_to_7d_large(self, result):
        assert result.ratio_ec_to_7d > 1e25

    def test_qnm_frequency_positive(self, result):
        assert result.qnm_frequency > 0.0

    def test_qnm_lifetime_standard_positive(self, result):
        assert result.qnm_lifetime_standard > 0.0

    def test_qnm_lifetime_torsion_geq_standard(self, result):
        assert result.qnm_lifetime_torsion >= result.qnm_lifetime_standard

    def test_qnm_info_bits_positive(self, result):
        assert result.qnm_info_bits > 0.0

    def test_bh_entropy_bits_larger_than_qnm_bits(self, result):
        assert result.bh_entropy_bits >= result.qnm_info_bits

    def test_ew_scale_um_less_than_one(self, result):
        assert 0.0 < result.ew_scale_ratio_um < 1.0

    def test_ew_scale_observed_tiny(self, result):
        assert result.ew_scale_ratio_observed < 1e-15

    def test_higgs_discrepancy_large(self, result):
        assert result.higgs_discrepancy > 1e12

    def test_default_kappa_torsion_applied(self):
        r0 = compare_frameworks(kappa_torsion=0.0)
        r1 = compare_frameworks(kappa_torsion=0.1)
        assert r1.um_ec_M_rem > r0.um_ec_M_rem

    def test_l_max_affects_qnm_bits(self):
        r5 = compare_frameworks(l_max=5)
        r10 = compare_frameworks(l_max=10)
        assert r10.qnm_info_bits >= r5.qnm_info_bits

    def test_bh_entropy_formula(self, result):
        expected = 4.0 * math.pi * result.um_5d_M_rem ** 2 / math.log(2.0)
        assert result.bh_entropy_bits == pytest.approx(expected, rel=1e-10)

    def test_qnm_frequency_matches_standalone(self, result):
        expected = qnm_frequency_fundamental(result.um_5d_M_rem)
        assert result.qnm_frequency == pytest.approx(expected, rel=1e-12)
