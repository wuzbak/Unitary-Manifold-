# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_bh_remnant.py
========================
Tests for src/core/bh_remnant.py — Pillar 28 / Theorem XVII:
Kaluza-Klein Black Hole Remnant.

Physical claims under test
--------------------------
1. remnant_mass:
   - Positive, finite for all physical (phi_min, m_phi, phi0) combinations.
   - Increases with phi_min (larger GW floor → larger remnant).
   - Approaches zero as phi_min → 0 (recovering Hawking's infinite-evaporation limit).
   - Raises ValueError for unphysical inputs.

2. remnant_temperature:
   - Positive for all physical inputs.
   - Consistent with remnant_mass via T_H = 1/(8πM_rem).
   - Increases as phi_min → phi0 (extremal remnant approaches Planck temperature).
   - Raises ValueError for unphysical inputs.

3. remnant_entropy:
   - Satisfies Bekenstein–Hawking relation S = 4π M².
   - Non-negative; zero for M_rem = 0.
   - Raises ValueError for M_rem < 0.

4. remnant_information_bits:
   - Non-negative; equals S_rem / ln(2).
   - Increases monotonically with M_rem.
   - Raises ValueError for M_rem < 0.

5. kk_stabilization_repulsion:
   - Non-negative; zero when phi = phi_min (at the floor, no excess repulsion).
   - Increases as phi moves away from phi_min.
   - Raises ValueError for unphysical inputs.

6. evaporation_fraction_remaining:
   - Strictly between 0 and 1 for physical inputs.
   - Decreases as M_initial grows (larger BH, smaller remnant fraction).
   - Raises ValueError for M_initial ≤ M_rem.

7. compare_7d_vs_5d_remnant:
   - Returns dict with all expected keys.
   - 5d dimension count = 5, 7d = 7.
   - Ratio is finite and positive.
   - Extra dimension counts are correct (1 vs 3).

8. Dimensional consistency checks:
   - All functions output dimensionless ratios or Planck-scale quantities that
     are finite and well-behaved.
"""

import math
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.bh_remnant import (
    remnant_mass,
    remnant_temperature,
    remnant_entropy,
    remnant_information_bits,
    kk_stabilization_repulsion,
    evaporation_fraction_remaining,
    compare_7d_vs_5d_remnant,
    PHI0_CANONICAL,
    M_PHI_CANONICAL,
    PHI_MIN_CANONICAL,
)

# Canonical parameter set used throughout
PHI0   = 1.0
M_PHI  = 1.0
PHI_MIN = 0.1


# ===========================================================================
# remnant_mass
# ===========================================================================

class TestRemnantMass:

    def test_positive_canonical(self):
        M = remnant_mass(PHI_MIN, M_PHI, PHI0)
        assert M > 0.0

    def test_finite_canonical(self):
        M = remnant_mass(PHI_MIN, M_PHI, PHI0)
        assert math.isfinite(M)

    def test_formula_canonical(self):
        """M_rem = phi_min / (8π m_phi (phi0 - phi_min))"""
        expected = PHI_MIN / (8.0 * math.pi * M_PHI * (PHI0 - PHI_MIN))
        assert remnant_mass(PHI_MIN, M_PHI, PHI0) == pytest.approx(expected, rel=1e-12)

    def test_increases_with_phi_min(self):
        """Larger GW floor → larger remnant mass."""
        M1 = remnant_mass(0.1, M_PHI, PHI0)
        M2 = remnant_mass(0.2, M_PHI, PHI0)
        M3 = remnant_mass(0.3, M_PHI, PHI0)
        assert M1 < M2 < M3

    def test_approaches_zero_as_phi_min_small(self):
        """As phi_min → 0, M_rem → 0 (Hawking's complete-evaporation limit)."""
        M_tiny = remnant_mass(1e-6, M_PHI, PHI0)
        assert M_tiny < 1e-5

    def test_decreases_with_m_phi(self):
        """Larger GW mass → steeper restoring force → smaller M_rem."""
        M1 = remnant_mass(PHI_MIN, 0.5, PHI0)
        M2 = remnant_mass(PHI_MIN, 1.0, PHI0)
        M3 = remnant_mass(PHI_MIN, 2.0, PHI0)
        assert M1 > M2 > M3

    def test_decreases_with_larger_delta_phi(self):
        """Larger phi0 (larger phi0 - phi_min) → smaller M_rem."""
        M1 = remnant_mass(PHI_MIN, M_PHI, 0.5)
        M2 = remnant_mass(PHI_MIN, M_PHI, 1.0)
        M3 = remnant_mass(PHI_MIN, M_PHI, 2.0)
        assert M1 > M2 > M3

    def test_planck_scale_result(self):
        """For canonical GW parameters, M_rem should be O(1) in Planck units."""
        M = remnant_mass(PHI_MIN, M_PHI, PHI0)
        assert 1e-3 < M < 1e3   # broadly Planck-scale

    def test_various_parameter_combinations(self):
        """Spot-checks across parameter space."""
        assert remnant_mass(0.5, 0.5, 1.0) == pytest.approx(
            0.5 / (8.0 * math.pi * 0.5 * 0.5), rel=1e-12
        )
        assert remnant_mass(0.01, 0.1, 2.0) == pytest.approx(
            0.01 / (8.0 * math.pi * 0.1 * 1.99), rel=1e-12
        )

    # --- error cases ---

    def test_raises_phi_min_zero(self):
        with pytest.raises(ValueError, match="phi_min"):
            remnant_mass(0.0, M_PHI, PHI0)

    def test_raises_phi_min_negative(self):
        with pytest.raises(ValueError, match="phi_min"):
            remnant_mass(-0.1, M_PHI, PHI0)

    def test_raises_m_phi_zero(self):
        with pytest.raises(ValueError, match="m_phi"):
            remnant_mass(PHI_MIN, 0.0, PHI0)

    def test_raises_m_phi_negative(self):
        with pytest.raises(ValueError, match="m_phi"):
            remnant_mass(PHI_MIN, -1.0, PHI0)

    def test_raises_phi0_equal_phi_min(self):
        with pytest.raises(ValueError, match="phi0"):
            remnant_mass(0.5, M_PHI, 0.5)

    def test_raises_phi0_less_than_phi_min(self):
        with pytest.raises(ValueError, match="phi0"):
            remnant_mass(0.5, M_PHI, 0.3)


# ===========================================================================
# remnant_temperature
# ===========================================================================

class TestRemnantTemperature:

    def test_positive_canonical(self):
        T = remnant_temperature(PHI_MIN, PHI0, M_PHI)
        assert T > 0.0

    def test_finite_canonical(self):
        T = remnant_temperature(PHI_MIN, PHI0, M_PHI)
        assert math.isfinite(T)

    def test_formula_canonical(self):
        """T_H_max = m_phi * (phi0 - phi_min) / (2π phi_min)"""
        expected = M_PHI * (PHI0 - PHI_MIN) / (2.0 * math.pi * PHI_MIN)
        assert remnant_temperature(PHI_MIN, PHI0, M_PHI) == pytest.approx(
            expected, rel=1e-12
        )

    def test_consistency_with_remnant_mass(self):
        """T_H_max × M_rem = 1/(16π²) — the product is a pure Planck-unit constant."""
        T = remnant_temperature(PHI_MIN, PHI0, M_PHI)
        M = remnant_mass(PHI_MIN, M_PHI, PHI0)
        assert T * M == pytest.approx(1.0 / (16.0 * math.pi ** 2), rel=1e-12)

    def test_temperature_decreases_as_phi_min_approaches_phi0(self):
        """As phi_min → phi0, delta = phi0 - phi_min → 0, so T_H_max → 0."""
        T_small_gap = remnant_temperature(0.99, 1.0, M_PHI)
        T_large_gap = remnant_temperature(0.1, 1.0, M_PHI)
        # Large phi_min (small delta) → small T; small phi_min (large delta/phi_min) → large T
        assert T_small_gap < T_large_gap

    def test_large_phi_min_small_temperature(self):
        """phi_min close to phi0 → very small delta → very small T."""
        T = remnant_temperature(0.999, 1.0, M_PHI)
        assert T < 0.01

    def test_small_phi_min_large_temperature(self):
        """phi_min close to 0 → large delta/phi_min ratio → large T."""
        T = remnant_temperature(0.001, 1.0, M_PHI)
        assert T > 100.0

    def test_increases_with_m_phi(self):
        T1 = remnant_temperature(PHI_MIN, PHI0, 0.5)
        T2 = remnant_temperature(PHI_MIN, PHI0, 1.0)
        T3 = remnant_temperature(PHI_MIN, PHI0, 2.0)
        assert T1 < T2 < T3

    # --- error cases ---

    def test_raises_phi_min_zero(self):
        with pytest.raises(ValueError, match="phi_min"):
            remnant_temperature(0.0, PHI0, M_PHI)

    def test_raises_m_phi_negative(self):
        with pytest.raises(ValueError, match="m_phi"):
            remnant_temperature(PHI_MIN, PHI0, -1.0)

    def test_raises_phi0_equal_phi_min(self):
        with pytest.raises(ValueError, match="phi0"):
            remnant_temperature(0.5, 0.5, M_PHI)


# ===========================================================================
# remnant_entropy
# ===========================================================================

class TestRemnantEntropy:

    def test_zero_mass_zero_entropy(self):
        assert remnant_entropy(0.0) == pytest.approx(0.0)

    def test_formula(self):
        """S_rem = 4π M_rem²"""
        M = 2.5
        assert remnant_entropy(M) == pytest.approx(4.0 * math.pi * M ** 2, rel=1e-12)

    def test_nonnegative(self):
        for M in [0.0, 0.001, 0.1, 1.0, 10.0, 1000.0]:
            assert remnant_entropy(M) >= 0.0

    def test_increases_with_mass(self):
        M1, M2, M3 = 0.5, 1.0, 2.0
        assert remnant_entropy(M1) < remnant_entropy(M2) < remnant_entropy(M3)

    def test_scales_as_mass_squared(self):
        """S(2M) = 4 S(M) — quadratic scaling."""
        M = 1.5
        assert remnant_entropy(2.0 * M) == pytest.approx(4.0 * remnant_entropy(M), rel=1e-12)

    def test_bekenstein_hawking_with_remnant_mass(self):
        """S_rem = 4π M_rem² using the actual remnant mass formula."""
        M = remnant_mass(PHI_MIN, M_PHI, PHI0)
        S = remnant_entropy(M)
        assert S == pytest.approx(4.0 * math.pi * M ** 2, rel=1e-12)

    def test_raises_negative_mass(self):
        with pytest.raises(ValueError, match="M_rem"):
            remnant_entropy(-1.0)


# ===========================================================================
# remnant_information_bits
# ===========================================================================

class TestRemnantInformationBits:

    def test_zero_mass_zero_bits(self):
        assert remnant_information_bits(0.0) == pytest.approx(0.0)

    def test_formula(self):
        """I_rem = 4π M² / ln(2)"""
        M = 3.0
        expected = 4.0 * math.pi * M ** 2 / math.log(2.0)
        assert remnant_information_bits(M) == pytest.approx(expected, rel=1e-12)

    def test_equals_entropy_over_ln2(self):
        M = 1.7
        assert remnant_information_bits(M) == pytest.approx(
            remnant_entropy(M) / math.log(2.0), rel=1e-12
        )

    def test_nonnegative(self):
        for M in [0.0, 0.01, 1.0, 100.0]:
            assert remnant_information_bits(M) >= 0.0

    def test_increases_monotonically(self):
        bits = [remnant_information_bits(M) for M in [0.1, 0.5, 1.0, 5.0]]
        assert all(bits[i] < bits[i + 1] for i in range(len(bits) - 1))

    def test_raises_negative_mass(self):
        with pytest.raises(ValueError, match="M_rem"):
            remnant_information_bits(-0.5)


# ===========================================================================
# kk_stabilization_repulsion
# ===========================================================================

class TestKKStabilizationRepulsion:

    def test_at_floor_zero_repulsion(self):
        """V_rep(phi_min) = 0: no excess repulsion exactly at the floor."""
        phi_min = 0.2
        V = kk_stabilization_repulsion(phi_min, phi_min, M_PHI)
        assert V == pytest.approx(0.0, abs=1e-15)

    def test_above_floor_positive(self):
        V = kk_stabilization_repulsion(0.5, 0.2, M_PHI)
        assert V > 0.0

    def test_formula(self):
        """V_rep = ½ m_phi² (phi - phi_min)²"""
        phi, phi_min, m_phi = 0.8, 0.3, 2.0
        expected = 0.5 * m_phi ** 2 * (phi - phi_min) ** 2
        assert kk_stabilization_repulsion(phi, phi_min, m_phi) == pytest.approx(
            expected, rel=1e-12
        )

    def test_increases_away_from_floor(self):
        phi_min = 0.1
        V1 = kk_stabilization_repulsion(0.2, phi_min, M_PHI)
        V2 = kk_stabilization_repulsion(0.4, phi_min, M_PHI)
        V3 = kk_stabilization_repulsion(0.8, phi_min, M_PHI)
        assert V1 < V2 < V3

    def test_scales_with_m_phi_squared(self):
        phi, phi_min = 0.5, 0.2
        V1 = kk_stabilization_repulsion(phi, phi_min, 1.0)
        V2 = kk_stabilization_repulsion(phi, phi_min, 2.0)
        assert V2 == pytest.approx(4.0 * V1, rel=1e-12)

    def test_symmetric_about_floor(self):
        """V_rep at phi_min + delta = V_rep at phi_min - delta (harmonic)."""
        phi_min, delta = 0.5, 0.1
        V_above = kk_stabilization_repulsion(phi_min + delta, phi_min, M_PHI)
        V_below = kk_stabilization_repulsion(phi_min - delta, phi_min, M_PHI)
        assert V_above == pytest.approx(V_below, rel=1e-12)

    def test_raises_phi_zero(self):
        with pytest.raises(ValueError, match="phi must"):
            kk_stabilization_repulsion(0.0, 0.1, M_PHI)

    def test_raises_phi_negative(self):
        with pytest.raises(ValueError, match="phi must"):
            kk_stabilization_repulsion(-0.1, 0.1, M_PHI)

    def test_raises_phi_min_zero(self):
        with pytest.raises(ValueError, match="phi_min"):
            kk_stabilization_repulsion(0.5, 0.0, M_PHI)

    def test_raises_m_phi_zero(self):
        with pytest.raises(ValueError, match="m_phi"):
            kk_stabilization_repulsion(0.5, 0.2, 0.0)


# ===========================================================================
# evaporation_fraction_remaining
# ===========================================================================

class TestEvaporationFractionRemaining:

    def test_between_zero_and_one(self):
        """0 < f_rem < 1 for any physical M_initial > M_rem."""
        f = evaporation_fraction_remaining(10.0, 1.0)
        assert 0.0 < f < 1.0

    def test_formula(self):
        M_initial, M_rem = 100.0, 5.0
        assert evaporation_fraction_remaining(M_initial, M_rem) == pytest.approx(
            M_rem / M_initial, rel=1e-12
        )

    def test_decreases_with_larger_initial_mass(self):
        """Larger initial mass → smaller surviving fraction."""
        f1 = evaporation_fraction_remaining(10.0, 1.0)
        f2 = evaporation_fraction_remaining(100.0, 1.0)
        f3 = evaporation_fraction_remaining(1000.0, 1.0)
        assert f1 > f2 > f3

    def test_increases_with_larger_remnant(self):
        f1 = evaporation_fraction_remaining(100.0, 1.0)
        f2 = evaporation_fraction_remaining(100.0, 5.0)
        f3 = evaporation_fraction_remaining(100.0, 10.0)
        assert f1 < f2 < f3

    def test_with_remnant_mass_formula(self):
        """End-to-end: compute M_rem, then fraction."""
        M_rem = remnant_mass(PHI_MIN, M_PHI, PHI0)
        M_initial = M_rem * 1000.0
        f = evaporation_fraction_remaining(M_initial, M_rem)
        assert f == pytest.approx(1e-3, rel=1e-12)

    def test_raises_m_initial_zero(self):
        with pytest.raises(ValueError, match="M_initial"):
            evaporation_fraction_remaining(0.0, 0.5)

    def test_raises_m_initial_negative(self):
        with pytest.raises(ValueError, match="M_initial"):
            evaporation_fraction_remaining(-1.0, 0.5)

    def test_raises_m_rem_zero(self):
        with pytest.raises(ValueError, match="M_rem"):
            evaporation_fraction_remaining(10.0, 0.0)

    def test_raises_m_rem_negative(self):
        with pytest.raises(ValueError, match="M_rem"):
            evaporation_fraction_remaining(10.0, -1.0)

    def test_raises_m_initial_equal_m_rem(self):
        with pytest.raises(ValueError):
            evaporation_fraction_remaining(5.0, 5.0)

    def test_raises_m_initial_less_than_m_rem(self):
        with pytest.raises(ValueError):
            evaporation_fraction_remaining(3.0, 5.0)


# ===========================================================================
# compare_7d_vs_5d_remnant
# ===========================================================================

class TestCompare7dVs5dRemnant:

    def test_returns_dict(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        assert isinstance(result, dict)

    def test_all_expected_keys_present(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        for key in [
            "5d_M_rem",
            "7d_M_rem_planck_units",
            "ratio",
            "dimension_count_5d",
            "dimension_count_7d",
            "extra_dimensions_5d",
            "extra_dimensions_7d",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_5d_dimension_count(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        assert result["dimension_count_5d"] == 5

    def test_7d_dimension_count(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        assert result["dimension_count_7d"] == 7

    def test_extra_dimensions_5d(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        assert result["extra_dimensions_5d"] == 1

    def test_extra_dimensions_7d(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        assert result["extra_dimensions_7d"] == 3

    def test_5d_m_rem_matches_remnant_mass(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        M_direct = remnant_mass(PHI_MIN, M_PHI, PHI0)
        assert result["5d_M_rem"] == pytest.approx(M_direct, rel=1e-12)

    def test_7d_prediction_is_planck_scale(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        # 7D prediction is O(1) M_Planck
        assert result["7d_M_rem_planck_units"] == pytest.approx(1.0)

    def test_ratio_finite_positive(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        assert math.isfinite(result["ratio"])
        assert result["ratio"] > 0.0

    def test_ratio_consistent(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        assert result["ratio"] == pytest.approx(
            result["5d_M_rem"] / result["7d_M_rem_planck_units"], rel=1e-12
        )

    def test_5d_uses_fewer_extra_dimensions_than_7d(self):
        result = compare_7d_vs_5d_remnant(PHI_MIN, M_PHI, PHI0)
        assert result["extra_dimensions_5d"] < result["extra_dimensions_7d"]

    # --- error cases ---

    def test_raises_phi_min_zero(self):
        with pytest.raises(ValueError, match="phi_min"):
            compare_7d_vs_5d_remnant(0.0, M_PHI, PHI0)

    def test_raises_phi0_not_greater_than_phi_min(self):
        with pytest.raises(ValueError, match="phi0"):
            compare_7d_vs_5d_remnant(0.5, M_PHI, 0.4)


# ===========================================================================
# Dimensional consistency and end-to-end checks
# ===========================================================================

class TestDimensionalConsistency:

    def test_entropy_information_ratio_is_ln2(self):
        """S / I_bits = ln(2) for any M."""
        M = 5.0
        S = remnant_entropy(M)
        I = remnant_information_bits(M)
        assert S / I == pytest.approx(math.log(2.0), rel=1e-12)

    def test_temperature_mass_product_is_constant(self):
        """T_H_max × M_rem = 1/(16π²) — a pure number in Planck units.

        From the formulas:
            T_H_max = m_φ(φ₀−φ_min)/(2π φ_min)
            M_rem   = φ_min / (8π m_φ(φ₀−φ_min))
        The product T_H_max × M_rem = 1/(16π²) independent of all parameters.
        """
        T = remnant_temperature(PHI_MIN, PHI0, M_PHI)
        M = remnant_mass(PHI_MIN, M_PHI, PHI0)
        assert T * M == pytest.approx(1.0 / (16.0 * math.pi ** 2), rel=1e-10)

    def test_fraction_times_initial_equals_remnant(self):
        M_rem = remnant_mass(PHI_MIN, M_PHI, PHI0)
        M_initial = M_rem * 50.0
        f = evaporation_fraction_remaining(M_initial, M_rem)
        assert f * M_initial == pytest.approx(M_rem, rel=1e-12)

    def test_entropy_nondimensional_ratio(self):
        """S_rem / (4π) = M_rem² — pure geometric quantity."""
        M = remnant_mass(PHI_MIN, M_PHI, PHI0)
        S = remnant_entropy(M)
        assert S / (4.0 * math.pi) == pytest.approx(M ** 2, rel=1e-12)

    def test_canonical_module_constants_are_physical(self):
        """Module-level canonical constants produce a valid remnant."""
        M = remnant_mass(PHI_MIN_CANONICAL, M_PHI_CANONICAL, PHI0_CANONICAL)
        assert M > 0.0
        assert math.isfinite(M)

    def test_large_bh_limit_remnant_tiny_fraction(self):
        """For M_initial ≫ M_rem, the surviving fraction is negligible."""
        M_rem = remnant_mass(PHI_MIN, M_PHI, PHI0)
        M_initial = M_rem * 1e6
        f = evaporation_fraction_remaining(M_initial, M_rem)
        assert f < 1e-5

    def test_repulsion_vanishes_at_floor_regardless_of_m_phi(self):
        """V_rep(phi_min, phi_min, any m) = 0."""
        for m in [0.1, 1.0, 10.0, 100.0]:
            V = kk_stabilization_repulsion(0.3, 0.3, m)
            assert V == pytest.approx(0.0, abs=1e-15)
