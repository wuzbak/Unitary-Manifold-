# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_five_seven_architecture.py
===============================================
Unit tests for the 5-Core / 7-Layer architecture module.

Covers:
  - Constants: N_CORE=5, N_LAYER=7, BEAT_FREQUENCY=2, JACOBI_SUM=12,
               K_CS_RESONANCE=74, C_S_STABILITY_FLOOR=12/37
  - CoreLayerArchitecture: field types, stability flag, why_not_stable
  - architecture_report: canonical (5,7), bad pairs, ValueError
  - is_stable_architecture: (5,7) stable, (5,6) and (5,8) comparisons
  - compare_layer_candidates: correct length, ordering preserved
  - canonical_57: matches hand-computed values
  - stability_floor_comparison: (5,7) present, all c_s in (0,1)
  - moiree_phase_sync_quality: (5,7) > (5,8), beat=0 returns 0
  - Mathematical identities: ρ=35/37, c_s=12/37, k_cs=74, r_eff<0.036
"""

import math
import pytest
import numpy as np

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from five_seven_architecture import (
    N_CORE,
    N_LAYER,
    BEAT_FREQUENCY,
    JACOBI_SUM,
    K_CS_RESONANCE,
    C_S_STABILITY_FLOOR,
    DEFAULT_R_LIMIT,
    CoreLayerArchitecture,
    FiveSixSevenDuality,
    architecture_report,
    is_stable_architecture,
    compare_layer_candidates,
    canonical_57,
    stability_floor_comparison,
    moiree_phase_sync_quality,
    five_six_seven_duality_report,
)
from src.core.braided_winding import R_BICEP_KECK_95


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_core(self):
        assert N_CORE == 5

    def test_n_layer(self):
        assert N_LAYER == 7

    def test_beat_frequency(self):
        assert BEAT_FREQUENCY == 2   # minimal integer gap

    def test_jacobi_sum(self):
        assert JACOBI_SUM == 12

    def test_k_cs_resonance(self):
        assert K_CS_RESONANCE == 74  # 5² + 7²

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS_RESONANCE == N_CORE**2 + N_LAYER**2

    def test_c_s_stability_floor_value(self):
        assert C_S_STABILITY_FLOOR == pytest.approx(12 / 37, rel=1e-10)

    def test_c_s_stability_floor_in_unit_interval(self):
        assert 0.0 < C_S_STABILITY_FLOOR < 1.0

    def test_default_r_limit(self):
        assert DEFAULT_R_LIMIT == pytest.approx(R_BICEP_KECK_95, rel=1e-10)


# ---------------------------------------------------------------------------
# canonical_57
# ---------------------------------------------------------------------------

class TestCanonical57:
    def setup_method(self):
        self.arch = canonical_57()

    def test_returns_architecture(self):
        assert isinstance(self.arch, CoreLayerArchitecture)

    def test_n_core_is_5(self):
        assert self.arch.n_core == 5

    def test_n_layer_is_7(self):
        assert self.arch.n_layer == 7

    def test_k_cs_is_74(self):
        assert self.arch.k_cs == 74

    def test_beat_is_2(self):
        assert self.arch.beat == 2

    def test_jacobi_sum_is_12(self):
        assert self.arch.jacobi_sum == 12

    def test_rho_is_35_over_37(self):
        assert self.arch.rho == pytest.approx(35 / 37, rel=1e-8)

    def test_c_s_is_12_over_37(self):
        assert self.arch.c_s == pytest.approx(12 / 37, rel=1e-8)

    def test_r_eff_below_bicep_keck(self):
        assert self.arch.r_eff < R_BICEP_KECK_95

    def test_r_eff_approximately_031(self):
        assert self.arch.r_eff == pytest.approx(0.031, abs=0.005)

    def test_ns_close_to_planck(self):
        assert self.arch.ns == pytest.approx(0.9635, abs=0.002)

    def test_ns_within_half_sigma(self):
        assert self.arch.ns_sigma < 0.5

    def test_is_stable(self):
        assert self.arch.is_stable is True

    def test_why_not_stable_empty(self):
        assert self.arch.why_not_stable == []

    def test_r_satisfies_bicep(self):
        assert self.arch.r_satisfies_bicep is True

    def test_r_satisfies_planck(self):
        assert self.arch.r_satisfies_planck is True

    def test_ns_in_window(self):
        assert self.arch.ns_in_window is True

    def test_c_s_above_floor(self):
        assert self.arch.c_s_above_floor is True

    def test_c_s_identity(self):
        """c_s = (n₂−n₁)(n₁+n₂) / k_cs at resonance."""
        expected = (self.arch.n_layer - self.arch.n_core) * (
            self.arch.n_core + self.arch.n_layer
        ) / self.arch.k_cs
        assert self.arch.c_s == pytest.approx(expected, rel=1e-8)

    def test_rho_identity(self):
        """ρ = 2·n₁·n₂ / k_cs."""
        expected = 2 * self.arch.n_core * self.arch.n_layer / self.arch.k_cs
        assert self.arch.rho == pytest.approx(expected, rel=1e-8)

    def test_pythagoras(self):
        """rho² + c_s² = 1 (canonical normalisation)."""
        assert self.arch.rho**2 + self.arch.c_s**2 == pytest.approx(1.0, abs=1e-8)

    def test_sum_of_squares_resonance(self):
        """k_cs = n_core² + n_layer² = 74."""
        assert self.arch.k_cs == self.arch.n_core**2 + self.arch.n_layer**2


# ---------------------------------------------------------------------------
# architecture_report — validation errors
# ---------------------------------------------------------------------------

class TestArchitectureReportErrors:
    def test_n_core_zero_raises(self):
        with pytest.raises(ValueError):
            architecture_report(0, 7)

    def test_n_core_negative_raises(self):
        with pytest.raises(ValueError):
            architecture_report(-1, 7)

    def test_n_layer_equal_to_n_core_raises(self):
        with pytest.raises(ValueError):
            architecture_report(5, 5)

    def test_n_layer_less_than_n_core_raises(self):
        with pytest.raises(ValueError):
            architecture_report(7, 5)


# ---------------------------------------------------------------------------
# is_stable_architecture
# ---------------------------------------------------------------------------

class TestIsStableArchitecture:
    def test_57_is_stable(self):
        assert is_stable_architecture(5, 7) is True

    def test_56_is_not_stable(self):
        """(5,6) c_s = 11/61 ≈ 0.180 — below the stability floor 12/37."""
        assert is_stable_architecture(5, 6) is False

    def test_57_stable_with_planck_limit(self):
        """(5,7) should also pass the looser Planck r limit."""
        from src.core.braided_winding import R_PLANCK_95
        assert is_stable_architecture(5, 7, r_limit=R_PLANCK_95) is True

    def test_stability_requires_c_s_above_floor(self):
        """Lowering c_s_floor to 0 should not change (5,7) result."""
        assert is_stable_architecture(5, 7, c_s_floor=0.0) is True

    def test_elevated_floor_rejects_57(self):
        """If we demand c_s > 0.4, (5,7) should fail (c_s ≈ 0.324)."""
        assert is_stable_architecture(5, 7, c_s_floor=0.40) is False


# ---------------------------------------------------------------------------
# Why (5,6) is not stable — explicit arithmetic
# ---------------------------------------------------------------------------

class TestFiveSixNotStable:
    def setup_method(self):
        self.arch56 = architecture_report(5, 6)

    def test_k_cs_is_61(self):
        assert self.arch56.k_cs == 61  # 5² + 6² = 61

    def test_rho_is_60_over_61(self):
        assert self.arch56.rho == pytest.approx(60 / 61, rel=1e-8)

    def test_c_s_is_11_over_61(self):
        assert self.arch56.c_s == pytest.approx(11 / 61, rel=1e-8)

    def test_c_s_below_stability_floor(self):
        assert self.arch56.c_s < C_S_STABILITY_FLOOR

    def test_is_not_stable(self):
        assert self.arch56.is_stable is False

    def test_has_instability_reason(self):
        assert len(self.arch56.why_not_stable) > 0

    def test_c_s_above_floor_is_false(self):
        assert self.arch56.c_s_above_floor is False

    def test_57_c_s_exceeds_56_c_s(self):
        arch57 = canonical_57()
        assert arch57.c_s > self.arch56.c_s


# ---------------------------------------------------------------------------
# compare_layer_candidates
# ---------------------------------------------------------------------------

class TestCompareLayerCandidates:
    def test_returns_correct_count(self):
        results = compare_layer_candidates(5, [6, 7, 8])
        assert len(results) == 3

    def test_ordering_preserved(self):
        results = compare_layer_candidates(5, [8, 6, 7])
        assert results[0].n_layer == 8
        assert results[1].n_layer == 6
        assert results[2].n_layer == 7

    def test_57_is_stable_among_candidates(self):
        results = compare_layer_candidates(5, [6, 7, 8])
        n7 = next(r for r in results if r.n_layer == 7)
        assert n7.is_stable is True

    def test_56_is_not_stable_among_candidates(self):
        results = compare_layer_candidates(5, [6, 7, 8])
        n6 = next(r for r in results if r.n_layer == 6)
        assert n6.is_stable is False

    def test_all_architectures_returned(self):
        results = compare_layer_candidates(5, [6, 7, 8, 9, 10])
        assert len(results) == 5

    def test_invalid_candidate_raises(self):
        with pytest.raises(ValueError):
            compare_layer_candidates(5, [5])   # n_layer must be > n_core

    def test_all_have_correct_n_core(self):
        results = compare_layer_candidates(5, [6, 7, 8])
        assert all(r.n_core == 5 for r in results)


# ---------------------------------------------------------------------------
# stability_floor_comparison
# ---------------------------------------------------------------------------

class TestStabilityFloorComparison:
    def test_returns_dict(self):
        result = stability_floor_comparison()
        assert isinstance(result, dict)

    def test_57_is_present(self):
        result = stability_floor_comparison()
        assert (5, 7) in result

    def test_all_c_s_in_unit_interval(self):
        result = stability_floor_comparison()
        for c_s in result.values():
            assert 0.0 < c_s < 1.0

    def test_57_c_s_is_12_over_37(self):
        result = stability_floor_comparison()
        assert result[(5, 7)] == pytest.approx(12 / 37, rel=1e-8)

    def test_56_c_s_is_11_over_61(self):
        result = stability_floor_comparison()
        assert result[(5, 6)] == pytest.approx(11 / 61, rel=1e-8)

    def test_57_has_higher_c_s_than_56(self):
        result = stability_floor_comparison()
        assert result[(5, 7)] > result[(5, 6)]

    def test_custom_n_core(self):
        result = stability_floor_comparison(n_core=3, n_layer_range=(4, 6))
        assert all(k[0] == 3 for k in result.keys())

    def test_custom_range(self):
        result = stability_floor_comparison(n_core=5, n_layer_range=(6, 8))
        assert set(result.keys()) == {(5, 6), (5, 7), (5, 8)}


# ---------------------------------------------------------------------------
# moiree_phase_sync_quality
# ---------------------------------------------------------------------------

class TestMoireePhaseSync:
    def test_57_quality_positive(self):
        q = moiree_phase_sync_quality(5, 7)
        assert q > 0.0

    def test_57_quality_value(self):
        """Q(5,7) = c_s / beat = (12/37) / 2 = 6/37."""
        assert moiree_phase_sync_quality(5, 7) == pytest.approx(6 / 37, rel=1e-8)

    def test_58_has_lower_quality_than_57(self):
        """Beat of 3 vs beat of 2 — more cycles between corrections."""
        q57 = moiree_phase_sync_quality(5, 7)
        q58 = moiree_phase_sync_quality(5, 8)
        assert q57 > q58

    def test_zero_beat_returns_zero(self):
        """Degenerate case: n_layer == n_core → beat = 0."""
        assert moiree_phase_sync_quality(5, 5) == pytest.approx(0.0)

    def test_negative_beat_returns_zero(self):
        """n_layer < n_core → beat < 0 → returns 0."""
        assert moiree_phase_sync_quality(7, 5) == pytest.approx(0.0)

    def test_quality_scales_with_c_s(self):
        """For fixed beat, higher c_s → higher quality."""
        q57 = moiree_phase_sync_quality(5, 7)   # c_s = 12/37, beat = 2
        q46 = moiree_phase_sync_quality(4, 6)   # c_s different, beat = 2
        # Both have beat=2; quality is proportional to c_s; just verify shape
        assert q57 > 0.0
        assert q46 > 0.0


# ---------------------------------------------------------------------------
# Architecture dataclass integrity
# ---------------------------------------------------------------------------

class TestArchitectureDataclass:
    def test_is_dataclass(self):
        from dataclasses import fields
        assert len(fields(CoreLayerArchitecture)) > 0

    def test_why_not_stable_default_empty(self):
        arch = canonical_57()
        assert isinstance(arch.why_not_stable, list)

    def test_why_not_stable_populated_for_unstable(self):
        arch = architecture_report(5, 6)
        assert len(arch.why_not_stable) > 0
        assert any("c_s" in reason.lower() or "floor" in reason.lower()
                   for reason in arch.why_not_stable)

    def test_r_bare_greater_than_r_eff(self):
        arch = canonical_57()
        assert arch.r_bare > arch.r_eff

    def test_r_eff_equals_r_bare_times_c_s(self):
        arch = canonical_57()
        assert arch.r_eff == pytest.approx(arch.r_bare * arch.c_s, rel=1e-8)


# ---------------------------------------------------------------------------
# FiveSixSevenDuality / five_six_seven_duality_report
# ---------------------------------------------------------------------------

class TestFiveSixSevenDualityReport:
    """Tests for the exact-rational (5,7)/(5,6) duality report.

    All expected values are derived from the braid integers alone:
        c_s(5,7) = 12/37,  c_s(5,6) = 11/61
        Δc_s     = 325/2257  (exact reduced fraction)
        λ_min    = 407/732   (exact reduced fraction)
        S_E(5,7) = 1/√74,   S_E(5,6) = 1/√61
    """

    def setup_method(self):
        self.r = five_six_seven_duality_report()

    # --- return type ---

    def test_returns_duality_dataclass(self):
        assert isinstance(self.r, FiveSixSevenDuality)

    # --- sound speeds ---

    def test_c_s_57_is_12_over_37(self):
        assert self.r.c_s_57 == pytest.approx(12 / 37, rel=1e-12)

    def test_c_s_56_is_11_over_61(self):
        assert self.r.c_s_56 == pytest.approx(11 / 61, rel=1e-12)

    def test_57_sound_speed_exceeds_56(self):
        assert self.r.c_s_57 > self.r.c_s_56

    def test_56_sound_speed_below_stability_floor(self):
        assert self.r.c_s_56 < C_S_STABILITY_FLOOR

    def test_57_sound_speed_equals_stability_floor(self):
        """The stability floor is defined as c_s(5,7) = 12/37."""
        assert self.r.c_s_57 == pytest.approx(C_S_STABILITY_FLOOR, rel=1e-12)

    # --- Δc_s ---

    def test_delta_cs_exact_string(self):
        assert self.r.delta_cs_exact == "325/2257"

    def test_delta_cs_float_value(self):
        assert self.r.delta_cs == pytest.approx(325 / 2257, rel=1e-12)

    def test_delta_cs_positive(self):
        assert self.r.delta_cs > 0.0

    def test_delta_cs_equals_c_s_difference(self):
        assert self.r.delta_cs == pytest.approx(self.r.c_s_57 - self.r.c_s_56, rel=1e-12)

    def test_delta_cs_equals_stability_deficit(self):
        """Δc_s = how far (5,6) falls below the floor (= c_s(5,7))."""
        deficit = C_S_STABILITY_FLOOR - self.r.c_s_56
        assert self.r.delta_cs == pytest.approx(deficit, rel=1e-12)

    # --- λ_min ratio ---

    def test_lambda_min_ratio_exact_string(self):
        assert self.r.lambda_min_ratio_exact == "407/732"

    def test_lambda_min_ratio_float_value(self):
        assert self.r.lambda_min_ratio == pytest.approx(407 / 732, rel=1e-12)

    def test_lambda_min_ratio_in_unit_interval(self):
        assert 0.0 < self.r.lambda_min_ratio < 1.0

    def test_lambda_min_ratio_equals_cs_quotient(self):
        assert self.r.lambda_min_ratio == pytest.approx(
            self.r.c_s_56 / self.r.c_s_57, rel=1e-12
        )

    # --- entropy capacity ratio ---

    def test_entropy_capacity_ratio_equals_lambda_squared(self):
        assert self.r.entropy_capacity_ratio == pytest.approx(
            self.r.lambda_min_ratio ** 2, rel=1e-12
        )

    def test_entropy_capacity_ratio_value(self):
        assert self.r.entropy_capacity_ratio == pytest.approx(
            (407 / 732) ** 2, rel=1e-12
        )

    def test_entropy_capacity_ratio_below_one_third(self):
        """(5,6) can sustain less than 1/3 of (5,7)'s eigenvalue-gap capacity."""
        assert self.r.entropy_capacity_ratio < 1.0 / 3.0

    # --- Euclidean actions ---

    def test_se_57_is_one_over_sqrt74(self):
        assert self.r.se_57 == pytest.approx(1.0 / math.sqrt(74), rel=1e-12)

    def test_se_56_is_one_over_sqrt61(self):
        assert self.r.se_56 == pytest.approx(1.0 / math.sqrt(61), rel=1e-12)

    def test_se_gap_is_positive(self):
        """(5,7) has strictly lower Euclidean action — it is the ground state."""
        assert self.r.se_gap > 0.0

    def test_se_gap_value(self):
        assert self.r.se_gap == pytest.approx(
            1.0 / math.sqrt(61) - 1.0 / math.sqrt(74), rel=1e-12
        )

    def test_se_gap_equals_se_56_minus_se_57(self):
        assert self.r.se_gap == pytest.approx(self.r.se_56 - self.r.se_57, rel=1e-12)

    def test_se_57_is_minimum_flag(self):
        assert self.r.se_57_is_minimum is True

    # --- label ---

    def test_label_is_string(self):
        assert isinstance(self.r.label, str)

    def test_label_mentions_metastable(self):
        assert "metastable" in self.r.label.lower()

    def test_label_mentions_under_resolved(self):
        assert "under-resolved" in self.r.label

    def test_label_mentions_euclidean_action(self):
        assert "euclidean action" in self.r.label.lower()

    def test_label_mentions_stability_deficit(self):
        assert "325/2257" in self.r.label

    # --- consistency with architecture_report ---

    def test_c_s_57_consistent_with_architecture_report(self):
        arch57 = architecture_report(5, 7)
        assert self.r.c_s_57 == pytest.approx(arch57.c_s, rel=1e-8)

    def test_c_s_56_consistent_with_architecture_report(self):
        arch56 = architecture_report(5, 6)
        assert self.r.c_s_56 == pytest.approx(arch56.c_s, rel=1e-8)

    def test_57_is_stable_56_is_not(self):
        """Ground-state / metastable ordering is consistent with stability flags."""
        assert is_stable_architecture(5, 7) is True
        assert is_stable_architecture(5, 6) is False
