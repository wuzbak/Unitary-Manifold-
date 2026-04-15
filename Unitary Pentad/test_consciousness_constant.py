# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_consciousness_constant.py
==============================================
Unit tests for the universal consciousness coupling constant module.

Covers:
  - Module constants: N_TOTAL=12, CONSCIOUSNESS_COUPLING=35/74,
    CONSCIOUSNESS_GAP=1/37, HUMAN_COUPLING_FRACTION=35/888
  - consciousness_coupling(): all fields, identity, xi_c, gap
  - jacobi_cs_identity(): beat=2 identity holds, beat≠2 does not
  - derive_total_body_count(): canonical (74,2)→12, non-square raises
  - coupling_from_architecture(): canonical (5,7), symmetry, bounds
  - entanglement_gap(): canonical value, always ≥ 0
  - Mathematical proofs: Ξ_c = ρ/2, δΞ = 1/37, N_total from k_cs+beat
"""

import math
import pytest
import numpy as np

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from consciousness_constant import (
    N_TOTAL,
    CONSCIOUSNESS_COUPLING,
    CONSCIOUSNESS_GAP,
    HUMAN_COUPLING_FRACTION,
    UniversalConstant,
    consciousness_coupling,
    jacobi_cs_identity,
    derive_total_body_count,
    coupling_from_architecture,
    entanglement_gap,
    _XI_NUMERATOR,
    _XI_DENOMINATOR,
)
from five_seven_architecture import (
    N_CORE,
    N_LAYER,
    K_CS_RESONANCE,
    BEAT_FREQUENCY,
    JACOBI_SUM,
)


# ===========================================================================
# Module-level constants
# ===========================================================================

class TestModuleConstants:
    def test_n_total_is_12(self):
        assert N_TOTAL == 12

    def test_n_total_equals_jacobi_sum(self):
        assert N_TOTAL == JACOBI_SUM

    def test_consciousness_coupling_exact(self):
        """Ξ_c = 35/74 exactly."""
        assert CONSCIOUSNESS_COUPLING == pytest.approx(35 / 74)

    def test_consciousness_coupling_value(self):
        assert abs(CONSCIOUSNESS_COUPLING - 0.4730) < 0.0001

    def test_consciousness_coupling_below_half(self):
        assert CONSCIOUSNESS_COUPLING < 0.5

    def test_consciousness_coupling_positive(self):
        assert CONSCIOUSNESS_COUPLING > 0.0

    def test_consciousness_gap_exact(self):
        """δΞ = 1/37 exactly."""
        assert CONSCIOUSNESS_GAP == pytest.approx(1 / 37)

    def test_consciousness_gap_plus_coupling_is_half(self):
        assert CONSCIOUSNESS_GAP + CONSCIOUSNESS_COUPLING == pytest.approx(0.5)

    def test_human_coupling_exact(self):
        """Ξ_human = 35/888 exactly."""
        assert HUMAN_COUPLING_FRACTION == pytest.approx(35 / 888)

    def test_human_coupling_equals_xi_over_n_total(self):
        assert HUMAN_COUPLING_FRACTION == pytest.approx(CONSCIOUSNESS_COUPLING / N_TOTAL)

    def test_xi_numerator(self):
        assert _XI_NUMERATOR == 35

    def test_xi_denominator(self):
        assert _XI_DENOMINATOR == 74

    def test_xi_numerator_equals_n_core_times_n_layer(self):
        assert _XI_NUMERATOR == N_CORE * N_LAYER

    def test_xi_denominator_equals_k_cs(self):
        assert _XI_DENOMINATOR == K_CS_RESONANCE


# ===========================================================================
# consciousness_coupling() — full derivation
# ===========================================================================

class TestConsciousnessCoupling:
    @pytest.fixture()
    def uc(self):
        return consciousness_coupling()

    def test_returns_universal_constant(self, uc):
        assert isinstance(uc, UniversalConstant)

    def test_n_core(self, uc):
        assert uc.n_core == N_CORE == 5

    def test_n_layer(self, uc):
        assert uc.n_layer == N_LAYER == 7

    def test_k_cs(self, uc):
        assert uc.k_cs == K_CS_RESONANCE == 74

    def test_beat(self, uc):
        assert uc.beat == BEAT_FREQUENCY == 2

    def test_jacobi_sum(self, uc):
        assert uc.jacobi_sum == JACOBI_SUM == 12

    def test_n_total_derived(self, uc):
        assert uc.n_total_derived == 12

    def test_identity_lhs(self, uc):
        assert uc.identity_lhs == pytest.approx(74.0)

    def test_identity_rhs(self, uc):
        """J²/2 + beat = 144/2 + 2 = 74."""
        assert uc.identity_rhs == pytest.approx(74.0)

    def test_identity_holds(self, uc):
        assert uc.identity_holds is True

    def test_xi_c(self, uc):
        assert uc.xi_c == pytest.approx(35 / 74)

    def test_xi_c_numerator(self, uc):
        assert uc.xi_c_numerator == 35

    def test_xi_c_denominator(self, uc):
        assert uc.xi_c_denominator == 74

    def test_xi_c_equals_half_rho(self, uc):
        """Ξ_c = ρ/2."""
        assert uc.xi_c == pytest.approx(uc.xi_c_as_half_rho)

    def test_consciousness_gap(self, uc):
        assert uc.consciousness_gap == pytest.approx(1 / 37)

    def test_gap_denominator(self, uc):
        """The denominator of δΞ is 37 = k_cs / beat."""
        assert uc.gap_denominator == 37

    def test_gap_denominator_equals_k_cs_over_beat(self, uc):
        assert uc.gap_denominator == uc.k_cs // uc.beat

    def test_xi_human(self, uc):
        assert uc.xi_human == pytest.approx(35 / 888)

    def test_xi_plus_gap_equals_half(self, uc):
        assert uc.xi_c + uc.consciousness_gap == pytest.approx(0.5)


# ===========================================================================
# jacobi_cs_identity()
# ===========================================================================

class TestJacobiCsIdentity:
    def test_canonical_57_holds(self):
        result = jacobi_cs_identity(5, 7)
        assert result["identity_holds"] is True

    def test_canonical_57_beat_is_minimal(self):
        result = jacobi_cs_identity(5, 7)
        assert result["beat_is_minimal"] is True

    def test_57_lhs_equals_74(self):
        result = jacobi_cs_identity(5, 7)
        assert result["lhs"] == pytest.approx(74.0)

    def test_57_rhs_equals_74(self):
        result = jacobi_cs_identity(5, 7)
        assert result["rhs"] == pytest.approx(74.0)

    def test_57_jacobi_sum_is_12(self):
        result = jacobi_cs_identity(5, 7)
        assert result["jacobi_sum"] == 12

    def test_57_beat_is_2(self):
        result = jacobi_cs_identity(5, 7)
        assert result["beat"] == 2

    def test_27_identity_does_not_hold(self):
        """(2,7) has beat=5 ≠ 2; identity must fail."""
        result = jacobi_cs_identity(2, 7)
        assert result["identity_holds"] is False

    def test_27_beat_not_minimal(self):
        result = jacobi_cs_identity(2, 7)
        assert result["beat_is_minimal"] is False

    def test_36_beat_3_not_minimal(self):
        """(3,6) has beat=3; identity fails."""
        result = jacobi_cs_identity(3, 6)
        assert result["identity_holds"] is False

    def test_46_beat_2_holds(self):
        """(4,6) has beat=2; identity must hold."""
        result = jacobi_cs_identity(4, 6)
        assert result["identity_holds"] is True
        assert result["beat_is_minimal"] is True

    def test_13_beat_2_holds(self):
        """(1,3) has beat=2; identity holds."""
        result = jacobi_cs_identity(1, 3)
        assert result["identity_holds"] is True

    def test_beat_2_always_holds(self):
        """For any n_core, setting n_layer = n_core + 2 always satisfies identity."""
        for n in range(1, 10):
            result = jacobi_cs_identity(n, n + 2)
            assert result["identity_holds"] is True, f"Failed for n={n}"

    def test_beat_3_never_holds(self):
        """For n_layer = n_core + 3, identity never holds (beat=3 ≠ 2)."""
        for n in range(1, 8):
            result = jacobi_cs_identity(n, n + 3)
            assert result["identity_holds"] is False, f"Unexpectedly held for n={n}"

    def test_result_keys(self):
        result = jacobi_cs_identity(5, 7)
        for key in ("n_core", "n_layer", "k_cs", "beat", "jacobi_sum",
                    "lhs", "rhs", "identity_holds", "beat_is_minimal"):
            assert key in result


# ===========================================================================
# derive_total_body_count()
# ===========================================================================

class TestDeriveTotalBodyCount:
    def test_canonical_74_2_gives_12(self):
        assert derive_total_body_count(74, 2) == 12

    def test_result_satisfies_identity(self):
        """J = √(2·(k_cs − beat)) → J² = 2·(k_cs − beat)."""
        n = derive_total_body_count(74, 2)
        assert n * n == 2 * (74 - 2)

    def test_raises_for_non_square(self):
        """k_cs=75, beat=2 → 2×73=146, not a perfect square."""
        with pytest.raises(ValueError, match="perfect square"):
            derive_total_body_count(75, 2)

    def test_raises_for_negative(self):
        with pytest.raises(ValueError):
            derive_total_body_count(1, 10)

    def test_small_exact_case(self):
        """(1,3) pair: k_cs=10, beat=2 → 2×8=16 → N_total=4."""
        assert derive_total_body_count(10, 2) == 4

    def test_another_beat_2_case(self):
        """(4,6) pair: k_cs=52, beat=2 → 2×50=100 → N_total=10."""
        assert derive_total_body_count(52, 2) == 10


# ===========================================================================
# coupling_from_architecture()
# ===========================================================================

class TestCouplingFromArchitecture:
    def test_canonical_57(self):
        xi = coupling_from_architecture(5, 7)
        assert xi == pytest.approx(35 / 74)

    def test_equals_module_constant(self):
        assert coupling_from_architecture(N_CORE, N_LAYER) == pytest.approx(
            CONSCIOUSNESS_COUPLING
        )

    def test_symmetric(self):
        """Coupling is symmetric: Ξ(a,b) = Ξ(b,a)."""
        assert coupling_from_architecture(3, 7) == pytest.approx(
            coupling_from_architecture(7, 3)
        )

    def test_always_below_half(self):
        """Ξ < 1/2 for all a ≠ b (AM-GM: a²+b² ≥ 2ab → ab/(a²+b²) ≤ 1/2)."""
        for n_core in range(1, 6):
            for n_layer in range(n_core + 1, 10):
                xi = coupling_from_architecture(n_core, n_layer)
                assert xi < 0.5, f"Ξ({n_core},{n_layer}) = {xi} ≥ 0.5"

    def test_equal_pair_gives_half(self):
        """When n_core = n_layer, Ξ = n²/(2n²) = 1/2 exactly."""
        assert coupling_from_architecture(5, 5) == pytest.approx(0.5)

    def test_positive(self):
        for n in range(1, 8):
            assert coupling_from_architecture(n, n + 1) > 0.0

    def test_raises_for_zero(self):
        with pytest.raises(ValueError):
            coupling_from_architecture(0, 5)

    def test_raises_for_negative(self):
        with pytest.raises(ValueError):
            coupling_from_architecture(-1, 5)


# ===========================================================================
# entanglement_gap()
# ===========================================================================

class TestEntanglementGap:
    def test_canonical_57_exact(self):
        """δΞ = 1/37 for (5,7)."""
        gap = entanglement_gap(5, 7)
        assert gap == pytest.approx(1 / 37)

    def test_equals_module_constant(self):
        assert entanglement_gap(N_CORE, N_LAYER) == pytest.approx(CONSCIOUSNESS_GAP)

    def test_always_nonnegative(self):
        for n_core in range(1, 6):
            for n_layer in range(n_core, 10):
                assert entanglement_gap(n_core, n_layer) >= 0.0

    def test_zero_for_equal_pair(self):
        """When n_core = n_layer, Ξ = 1/2, gap = 0."""
        assert entanglement_gap(4, 4) == pytest.approx(0.0)

    def test_larger_ratio_means_larger_gap(self):
        """As n_layer / n_core grows, the gap increases (core and layer decouple)."""
        gap_small = entanglement_gap(5, 6)
        gap_large = entanglement_gap(5, 20)
        assert gap_large > gap_small

    def test_gap_plus_coupling_is_half(self):
        for n_core, n_layer in [(3, 5), (4, 6), (5, 7), (6, 8)]:
            xi  = coupling_from_architecture(n_core, n_layer)
            gap = entanglement_gap(n_core, n_layer)
            assert xi + gap == pytest.approx(0.5)


# ===========================================================================
# Mathematical relationships
# ===========================================================================

class TestMathematicalRelationships:
    def test_xi_c_equals_rho_over_2(self):
        """Ξ_c = ρ/2, where ρ = 2·n_core·n_layer / k_cs."""
        k_cs = K_CS_RESONANCE
        rho  = 2 * N_CORE * N_LAYER / k_cs
        assert CONSCIOUSNESS_COUPLING == pytest.approx(rho / 2)

    def test_gap_denominator_is_k_cs_over_beat(self):
        """The gap denominator 37 = k_cs / beat = 74 / 2."""
        uc = consciousness_coupling()
        assert uc.gap_denominator == K_CS_RESONANCE // BEAT_FREQUENCY

    def test_n_total_squared_equals_2_times_k_cs_minus_beat(self):
        """N_total² = 2·(k_cs − beat)."""
        expected = 2 * (K_CS_RESONANCE - BEAT_FREQUENCY)
        assert N_TOTAL ** 2 == expected

    def test_xi_human_denominator_contains_37(self):
        """Ξ_human = 35/888 = 35/(24×37) — denominator divisible by 37."""
        denom = 888
        assert denom % 37 == 0

    def test_n_total_is_perfect_square_root(self):
        val = 2 * (K_CS_RESONANCE - BEAT_FREQUENCY)
        assert math.isqrt(val) ** 2 == val

    def test_consciousness_coupling_between_zero_and_half(self):
        assert 0.0 < CONSCIOUSNESS_COUPLING < 0.5

    def test_human_coupling_fraction_very_small(self):
        """Ξ_human ≈ 0.039 — human body is ~4% of total coupling."""
        assert 0.03 < HUMAN_COUPLING_FRACTION < 0.05
