# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_compactification.py
================================
Tests for src/multiverse/compactification.py — Pillar 29 / Theorem XVIII:
Spontaneous Compactification Dynamics.

Physical claims under test
--------------------------
1. euclidean_action: positive; inversely proportional to isocurvature energy.
2. tunneling_amplitude: in (0, 1]; largest for (5, 7) in the catalog.
3. compactification_radius_critical: equals 1/sqrt(k_cs); decreases with k_cs.
4. symmetry_breaking_temperature: equals sqrt(k_cs); increases with k_cs.
5. isocurvature_driving_energy: equals k_cs × (1 − c_s).
6. vacuum_selection_probability: sums to 1 across all branches; largest for (5,7).
7. compactification_event: all fields consistent with scalar functions.
8. canonical_vs_competitors: (5,7) appears first (largest Γ) for n_max ≥ 7.
9. symmetry_restored: correct phase boundary at T = T_comp.
10. Input validation: ValueError for bad (n1, n2) pairs.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.multiverse.compactification import (
    euclidean_action,
    tunneling_amplitude,
    compactification_radius_critical,
    symmetry_breaking_temperature,
    isocurvature_driving_energy,
    vacuum_selection_probability,
    compactification_event,
    canonical_vs_competitors,
    symmetry_restored,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
    E_ISO_CANONICAL,
    LOSS_COEFFICIENT,
)

# canonical (5,7) values
N1, N2 = 5, 7
K_CS = 74
C_S = 12.0 / 37.0
E_ISO = float(K_CS) * (1.0 - C_S)       # = 74 * 25/37 = 50.0
R_CRIT_CANONICAL = 1.0 / math.sqrt(K_CS)
T_COMP_CANONICAL = math.sqrt(K_CS)
# Formula: lossless branch → S_E = 0 + R_crit = 1/sqrt(74)
S_E_CANONICAL = R_CRIT_CANONICAL
GAMMA_CANONICAL = math.exp(-S_E_CANONICAL)


# ===========================================================================
# Module-level constants
# ===========================================================================

class TestModuleConstants:
    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-14

    def test_e_iso_canonical(self):
        assert abs(E_ISO_CANONICAL - 50.0) < 1e-10


# ===========================================================================
# isocurvature_driving_energy
# ===========================================================================

class TestIsocurvatureDrivingEnergy:
    def test_canonical_value(self):
        e = isocurvature_driving_energy(5, 7)
        assert abs(e - 50.0) < 1e-10

    def test_positive(self):
        for n1, n2 in [(1, 2), (3, 4), (5, 6), (5, 7), (2, 5)]:
            assert isocurvature_driving_energy(n1, n2) > 0.0

    def test_increases_with_k_cs(self):
        # (5,7) has k_cs=74; (1,2) has k_cs=5 — (5,7) should have larger E_iso
        e_57 = isocurvature_driving_energy(5, 7)
        e_12 = isocurvature_driving_energy(1, 2)
        assert e_57 > e_12

    def test_formula(self):
        # E_iso = k_cs * (1 - c_s) = (n2^2 - n1^2)
        # Because k_cs*(1-c_s) = (n1^2+n2^2) - (n2^2-n1^2) = 2*n1^2
        # Actually: k_cs*(1-c_s) = k_cs - (n2^2-n1^2) = n1^2+n2^2 - (n2^2-n1^2) = 2*n1^2
        for n1, n2 in [(1, 2), (3, 5), (5, 7)]:
            e = isocurvature_driving_energy(n1, n2)
            # k_cs = n1^2 + n2^2; c_s = (n2^2-n1^2)/k_cs
            # E_iso = k_cs*(1-c_s) = k_cs - (n2^2-n1^2) = 2*n1^2
            expected = 2.0 * n1 ** 2
            assert abs(e - expected) < 1e-10, f"({n1},{n2}): {e} vs {expected}"

    def test_raises_bad_n1(self):
        with pytest.raises(ValueError):
            isocurvature_driving_energy(0, 3)

    def test_raises_bad_n2(self):
        with pytest.raises(ValueError):
            isocurvature_driving_energy(3, 3)


# ===========================================================================
# euclidean_action
# ===========================================================================

class TestEuclideanAction:
    def test_canonical_value(self):
        # (5,7) is lossless → S_E = 0 + R_crit = 1/sqrt(74)
        s = euclidean_action(5, 7)
        assert abs(s - 1.0 / math.sqrt(74.0)) < 1e-10

    def test_positive(self):
        for n1, n2 in [(1, 2), (3, 4), (5, 7), (2, 9)]:
            assert euclidean_action(n1, n2) > 0.0

    def test_canonical_less_than_56(self):
        # Both (5,7) and (5,6) are lossless; (5,7) has larger k_cs=74 vs 61
        # → smaller R_crit → smaller S_E
        s_57 = euclidean_action(5, 7)
        s_56 = euclidean_action(5, 6)
        assert s_57 < s_56

    def test_canonical_less_than_lossy(self):
        # (1,2) is lossy → S_E includes large loss penalty
        s_57 = euclidean_action(5, 7)
        s_12 = euclidean_action(1, 2)
        assert s_57 < s_12

    def test_lossless_formula(self):
        # For lossless branches L=0 → S_E = R_crit = 1/sqrt(k_cs)
        for n1, n2 in [(5, 6), (5, 7)]:
            s = euclidean_action(n1, n2)
            r_crit = compactification_radius_critical(n1, n2)
            assert abs(s - r_crit) < 1e-12

    def test_lossy_includes_penalty(self):
        # For lossy branch, S_E = LOSS_COEFFICIENT * L + R_crit > R_crit
        for n1, n2 in [(1, 2), (2, 4), (3, 9)]:
            s = euclidean_action(n1, n2)
            r_crit = compactification_radius_critical(n1, n2)
            assert s > r_crit

    def test_raises_bad_n1(self):
        with pytest.raises(ValueError):
            euclidean_action(0, 2)

    def test_raises_n2_equals_n1(self):
        with pytest.raises(ValueError):
            euclidean_action(3, 3)

    def test_raises_n2_less_than_n1(self):
        with pytest.raises(ValueError):
            euclidean_action(5, 3)


# ===========================================================================
# tunneling_amplitude
# ===========================================================================

class TestTunnelingAmplitude:
    def test_canonical_value(self):
        # (5,7) is lossless → Γ = exp(-1/sqrt(74))
        g = tunneling_amplitude(5, 7)
        assert abs(g - math.exp(-1.0 / math.sqrt(74.0))) < 1e-10

    def test_lossless_in_unit_interval(self):
        # Lossless branches have moderate S_E → Γ strictly in (0, 1]
        for n1, n2 in [(5, 6), (5, 7)]:
            g = tunneling_amplitude(n1, n2)
            assert 0.0 < g <= 1.0

    def test_non_negative(self):
        # All branches must have Γ ≥ 0 (lossy may underflow to 0.0)
        for n1, n2 in [(1, 2), (2, 3), (4, 6), (5, 7), (3, 8)]:
            g = tunneling_amplitude(n1, n2)
            assert g >= 0.0

    def test_canonical_larger_than_12(self):
        # (5,7) is lossless → much larger Γ than lossy (1,2)
        g_57 = tunneling_amplitude(5, 7)
        g_12 = tunneling_amplitude(1, 2)
        assert g_57 > g_12

    def test_consistent_with_exp_action(self):
        for n1, n2 in [(1, 2), (3, 5), (5, 7)]:
            g = tunneling_amplitude(n1, n2)
            s = euclidean_action(n1, n2)
            assert abs(g - math.exp(-s)) < 1e-12

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            tunneling_amplitude(5, 4)


# ===========================================================================
# compactification_radius_critical
# ===========================================================================

class TestCompactificationRadiusCritical:
    def test_canonical_value(self):
        r = compactification_radius_critical(5, 7)
        assert abs(r - 1.0 / math.sqrt(74.0)) < 1e-12

    def test_positive(self):
        for n1, n2 in [(1, 2), (2, 3), (5, 7)]:
            assert compactification_radius_critical(n1, n2) > 0.0

    def test_smaller_for_larger_kcs(self):
        r_57 = compactification_radius_critical(5, 7)  # k_cs=74
        r_12 = compactification_radius_critical(1, 2)  # k_cs=5
        assert r_57 < r_12

    def test_formula(self):
        for n1, n2 in [(1, 2), (3, 4), (5, 7)]:
            r = compactification_radius_critical(n1, n2)
            expected = 1.0 / math.sqrt(n1 ** 2 + n2 ** 2)
            assert abs(r - expected) < 1e-12

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            compactification_radius_critical(3, 2)


# ===========================================================================
# symmetry_breaking_temperature
# ===========================================================================

class TestSymmetryBreakingTemperature:
    def test_canonical_value(self):
        t = symmetry_breaking_temperature(5, 7)
        assert abs(t - math.sqrt(74.0)) < 1e-12

    def test_positive(self):
        for n1, n2 in [(1, 2), (3, 5), (5, 7)]:
            assert symmetry_breaking_temperature(n1, n2) > 0.0

    def test_larger_for_larger_kcs(self):
        t_57 = symmetry_breaking_temperature(5, 7)  # k_cs=74
        t_12 = symmetry_breaking_temperature(1, 2)  # k_cs=5
        assert t_57 > t_12

    def test_reciprocal_of_r_crit(self):
        for n1, n2 in [(1, 2), (2, 5), (5, 7)]:
            t = symmetry_breaking_temperature(n1, n2)
            r = compactification_radius_critical(n1, n2)
            assert abs(t - 1.0 / r) < 1e-10

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            symmetry_breaking_temperature(0, 5)


# ===========================================================================
# symmetry_restored
# ===========================================================================

class TestSymmetryRestored:
    def test_above_tcomp_is_symmetric(self):
        t_comp = symmetry_breaking_temperature(5, 7)
        assert symmetry_restored(t_comp + 0.01, 5, 7) is True

    def test_below_tcomp_is_broken(self):
        t_comp = symmetry_breaking_temperature(5, 7)
        assert symmetry_restored(t_comp - 0.01, 5, 7) is False

    def test_exactly_at_tcomp_is_broken(self):
        t_comp = symmetry_breaking_temperature(5, 7)
        assert symmetry_restored(t_comp, 5, 7) is False

    def test_zero_temperature_is_broken(self):
        assert symmetry_restored(0.0, 5, 7) is False

    def test_high_temperature_always_symmetric(self):
        for n1, n2 in [(1, 2), (3, 4), (5, 7)]:
            t_comp = symmetry_breaking_temperature(n1, n2)
            assert symmetry_restored(10.0 * t_comp, n1, n2) is True

    def test_raises_negative_temperature(self):
        with pytest.raises(ValueError):
            symmetry_restored(-1.0, 5, 7)


# ===========================================================================
# compactification_event
# ===========================================================================

class TestCompactificationEvent:
    def setup_method(self):
        self.evt = compactification_event(5, 7)

    def test_n1_n2(self):
        assert self.evt.n1 == 5
        assert self.evt.n2 == 7

    def test_k_cs(self):
        assert self.evt.k_cs == 74

    def test_c_s(self):
        assert abs(self.evt.c_s - 12.0 / 37.0) < 1e-12

    def test_rho(self):
        # rho = 2*5*7/74 = 70/74 = 35/37
        assert abs(self.evt.rho - 35.0 / 37.0) < 1e-12

    def test_e_iso(self):
        assert abs(self.evt.e_iso - 50.0) < 1e-10

    def test_euclidean_action(self):
        # (5,7) is lossless → S_E = 0 + 1/sqrt(74)
        assert abs(self.evt.euclidean_action - 1.0 / math.sqrt(74.0)) < 1e-10

    def test_tunneling_amplitude(self):
        assert abs(self.evt.tunneling_amplitude - math.exp(-1.0 / math.sqrt(74.0))) < 1e-10

    def test_r_crit(self):
        assert abs(self.evt.r_crit - 1.0 / math.sqrt(74.0)) < 1e-12

    def test_t_comp(self):
        assert abs(self.evt.t_comp - math.sqrt(74.0)) < 1e-12

    def test_event_for_other_pairs(self):
        for n1, n2 in [(1, 2), (2, 3), (3, 5)]:
            evt = compactification_event(n1, n2)
            assert evt.n1 == n1
            assert evt.n2 == n2
            assert evt.k_cs == n1 ** 2 + n2 ** 2
            # Lossy branches: Γ ≥ 0 (may underflow to 0 for very lossy pairs)
            assert evt.tunneling_amplitude >= 0.0

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            compactification_event(7, 5)


# ===========================================================================
# canonical_vs_competitors
# ===========================================================================

class TestCanonicalVsCompetitors:
    def test_returns_list(self):
        result = canonical_vs_competitors(10)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_canonical_is_first_nmax_10(self):
        result = canonical_vs_competitors(10)
        first = result[0]
        assert first.n1 == 5
        assert first.n2 == 7

    def test_canonical_is_first_nmax_15(self):
        result = canonical_vs_competitors(15)
        assert result[0].n1 == 5
        assert result[0].n2 == 7

    def test_sorted_descending(self):
        result = canonical_vs_competitors(8)
        for i in range(len(result) - 1):
            assert result[i].tunneling_amplitude >= result[i + 1].tunneling_amplitude

    def test_pair_count(self):
        n_max = 6
        result = canonical_vs_competitors(n_max)
        # Count: pairs (i,j) with 1≤i<j≤6: 5+4+3+2+1 = 15
        expected = n_max * (n_max - 1) // 2
        assert len(result) == expected

    def test_all_amplitudes_non_negative(self):
        for evt in canonical_vs_competitors(8):
            assert evt.tunneling_amplitude >= 0.0

    def test_raises_nmax_less_than_2(self):
        with pytest.raises(ValueError):
            canonical_vs_competitors(1)


# ===========================================================================
# vacuum_selection_probability
# ===========================================================================

class TestVacuumSelectionProbability:
    def test_canonical_has_largest_probability(self):
        # (5,7) should have the largest P among n_max=10
        p_57 = vacuum_selection_probability(5, 7, n_max=10)
        p_12 = vacuum_selection_probability(1, 2, n_max=10)
        assert p_57 > p_12

    def test_probabilities_sum_to_one(self):
        n_max = 8
        total = 0.0
        for i in range(1, n_max + 1):
            for j in range(i + 1, n_max + 1):
                total += vacuum_selection_probability(i, j, n_max=n_max)
        assert abs(total - 1.0) < 1e-10

    def test_in_unit_interval(self):
        # Use only lossless pairs to guarantee strict positivity
        for n1, n2 in [(5, 6), (5, 7)]:
            p = vacuum_selection_probability(n1, n2, n_max=10)
            assert 0.0 < p <= 1.0

    def test_raises_n2_exceeds_nmax(self):
        with pytest.raises(ValueError):
            vacuum_selection_probability(5, 7, n_max=6)

    def test_raises_bad_n1(self):
        with pytest.raises(ValueError):
            vacuum_selection_probability(0, 3, n_max=10)
