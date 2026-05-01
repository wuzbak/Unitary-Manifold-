# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_moduli_survival.py
==============================
Tests for src/core/moduli_survival.py — Pillar 30:
Moduli Survival under Dimensional Reduction.

Physical claims under test
--------------------------
1. kk_mode_mass: m_n = n/R; zero for n=0; positive for n>0.
2. is_braid_locked: True only for n = n1 or n = n2.
3. mode_survival_weight: 1.0 for zero and braid-locked modes; Gaussian decay
   exp(-n²/k_cs) for others.
4. surviving_modes: zero mode and braid-locked modes always survive; all have w > 0.5.
5. projected_out_modes: no zero or braid-locked mode is projected out.
6. information_current_deficit: D=0 at φ=φ_star; D>0 elsewhere; raises on bad inputs.
7. information_current_conserved: True at φ=φ_star; False away from it.
8. moduli_dof_count: correct metric component counts and DOF totals.
9. dimension_reduction_matrix: shape, values for zero and braid-locked modes.
10. kk_mass_spectrum: sorted; zero for n=0; linear with n.
11. braid_effective_mass: c_s suppression for locked modes; bare mass otherwise.

"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np

from src.core.moduli_survival import (
    kk_mode_mass,
    is_braid_locked,
    mode_survival_weight,
    surviving_modes,
    projected_out_modes,
    information_current_deficit,
    information_current_conserved,
    moduli_dof_count,
    dimension_reduction_matrix,
    kk_mass_spectrum,
    braid_effective_mass,
    PHI_STAR_DEFAULT,
    METRIC_COMPONENTS_5D,
    METRIC_COMPONENTS_4D_METRIC,
    METRIC_COMPONENTS_KK_GAUGE,
    METRIC_COMPONENTS_RADION,
    ZERO_MODE_DOF,
    GRAVITON_DOF,
    KK_PHOTON_DOF,
    RADION_DOF,
)

N1, N2 = 5, 7
K_CS = 74
R_DEFAULT = 1.0 / math.sqrt(K_CS)   # critical radius


# ===========================================================================
# Module-level constants
# ===========================================================================

class TestModuleConstants:
    def test_metric_components_5d(self):
        assert METRIC_COMPONENTS_5D == 15

    def test_kk_decomposition_sum(self):
        total = METRIC_COMPONENTS_4D_METRIC + METRIC_COMPONENTS_KK_GAUGE + METRIC_COMPONENTS_RADION
        assert total == METRIC_COMPONENTS_5D

    def test_zero_mode_dof(self):
        assert ZERO_MODE_DOF == GRAVITON_DOF + KK_PHOTON_DOF + RADION_DOF == 5

    def test_graviton_dof(self):
        assert GRAVITON_DOF == 2

    def test_kk_photon_dof(self):
        assert KK_PHOTON_DOF == 2

    def test_radion_dof(self):
        assert RADION_DOF == 1

    def test_phi_star_positive(self):
        assert PHI_STAR_DEFAULT > 0.0


# ===========================================================================
# kk_mode_mass
# ===========================================================================

class TestKKModeMass:
    def test_zero_mode_is_massless(self):
        assert kk_mode_mass(0, 1.0) == 0.0

    def test_mass_formula(self):
        for n, R in [(1, 1.0), (3, 2.0), (5, 0.5)]:
            assert abs(kk_mode_mass(n, R) - float(n) / R) < 1e-14

    def test_positive_for_n_gt_0(self):
        for n in range(1, 8):
            assert kk_mode_mass(n, 1.0) > 0.0

    def test_linear_in_n(self):
        m1 = kk_mode_mass(1, 1.0)
        m5 = kk_mode_mass(5, 1.0)
        assert abs(m5 - 5.0 * m1) < 1e-14

    def test_raises_negative_n(self):
        with pytest.raises(ValueError):
            kk_mode_mass(-1, 1.0)

    def test_raises_zero_R(self):
        with pytest.raises(ValueError):
            kk_mode_mass(3, 0.0)

    def test_raises_negative_R(self):
        with pytest.raises(ValueError):
            kk_mode_mass(3, -0.5)


# ===========================================================================
# is_braid_locked
# ===========================================================================

class TestIsBraidLocked:
    def test_n1_is_locked(self):
        assert is_braid_locked(5, 5, 7) is True

    def test_n2_is_locked(self):
        assert is_braid_locked(7, 5, 7) is True

    def test_zero_mode_not_locked(self):
        assert is_braid_locked(0, 5, 7) is False

    def test_other_modes_not_locked(self):
        for n in [1, 2, 3, 4, 6, 8, 10]:
            assert is_braid_locked(n, 5, 7) is False

    def test_works_for_other_pairs(self):
        assert is_braid_locked(3, 3, 5) is True
        assert is_braid_locked(5, 3, 5) is True
        assert is_braid_locked(4, 3, 5) is False


# ===========================================================================
# mode_survival_weight
# ===========================================================================

class TestModeSurvivalWeight:
    def test_zero_mode_weight_is_one(self):
        assert mode_survival_weight(0, 5, 7, 74) == 1.0

    def test_n1_weight_is_one(self):
        assert mode_survival_weight(5, 5, 7, 74) == 1.0

    def test_n2_weight_is_one(self):
        assert mode_survival_weight(7, 5, 7, 74) == 1.0

    def test_generic_mode_gaussian_decay(self):
        for n in [1, 2, 3, 4, 6, 8]:
            w = mode_survival_weight(n, 5, 7, 74)
            expected = math.exp(-n * n / 74.0)
            assert abs(w - expected) < 1e-12

    def test_weight_in_unit_interval(self):
        for n in range(20):
            w = mode_survival_weight(n, 5, 7, 74)
            assert 0.0 < w <= 1.0

    def test_decays_with_n(self):
        w3 = mode_survival_weight(3, 5, 7, 74)
        w8 = mode_survival_weight(8, 5, 7, 74)
        # n=8 is not braid-locked, n=3 is not; 8^2/74 > 3^2/74 → w8 < w3
        assert w8 < w3

    def test_raises_negative_n(self):
        with pytest.raises(ValueError):
            mode_survival_weight(-1, 5, 7, 74)

    def test_raises_zero_k_cs(self):
        with pytest.raises(ValueError):
            mode_survival_weight(3, 5, 7, 0)


# ===========================================================================
# surviving_modes
# ===========================================================================

class TestSurvivingModes:
    def test_zero_mode_always_survives(self):
        modes = surviving_modes(15, 5, 7)
        ns = [m.n for m in modes]
        assert 0 in ns

    def test_n1_always_survives(self):
        modes = surviving_modes(15, 5, 7)
        ns = [m.n for m in modes]
        assert 5 in ns

    def test_n2_always_survives(self):
        modes = surviving_modes(15, 5, 7)
        ns = [m.n for m in modes]
        assert 7 in ns

    def test_all_have_weight_gt_half(self):
        for m in surviving_modes(20, 5, 7):
            assert m.survival_weight > 0.5

    def test_all_marked_as_survives(self):
        for m in surviving_modes(20, 5, 7):
            assert m.survives is True

    def test_zero_mode_record_correct(self):
        modes = surviving_modes(15, 5, 7)
        zero = next(m for m in modes if m.n == 0)
        assert zero.is_zero_mode is True
        assert zero.is_braid_locked is False
        assert zero.survival_weight == 1.0

    def test_braid_locked_record_correct(self):
        modes = surviving_modes(15, 5, 7)
        m5 = next(m for m in modes if m.n == 5)
        assert m5.is_braid_locked is True
        assert m5.survival_weight == 1.0

    def test_raises_negative_nmax(self):
        with pytest.raises(ValueError):
            surviving_modes(-1, 5, 7)


# ===========================================================================
# projected_out_modes
# ===========================================================================

class TestProjectedOutModes:
    def test_zero_mode_not_projected(self):
        modes = projected_out_modes(20, 5, 7)
        ns = [m.n for m in modes]
        assert 0 not in ns

    def test_n1_not_projected(self):
        modes = projected_out_modes(20, 5, 7)
        ns = [m.n for m in modes]
        assert 5 not in ns

    def test_n2_not_projected(self):
        modes = projected_out_modes(20, 5, 7)
        ns = [m.n for m in modes]
        assert 7 not in ns

    def test_all_have_weight_leq_half(self):
        for m in projected_out_modes(20, 5, 7):
            assert m.survival_weight <= 0.5

    def test_all_marked_not_survives(self):
        for m in projected_out_modes(20, 5, 7):
            assert m.survives is False

    def test_surviving_plus_projected_equals_nmax_plus_1(self):
        n_max = 15
        s_modes = surviving_modes(n_max, 5, 7)
        p_modes = projected_out_modes(n_max, 5, 7)
        assert len(s_modes) + len(p_modes) == n_max + 1


# ===========================================================================
# information_current_deficit
# ===========================================================================

class TestInformationCurrentDeficit:
    def test_zero_at_phi_star(self):
        d = information_current_deficit(PHI_STAR_DEFAULT, PHI_STAR_DEFAULT)
        assert abs(d) < 1e-14

    def test_positive_away_from_phi_star(self):
        assert information_current_deficit(PHI_STAR_DEFAULT * 1.1, PHI_STAR_DEFAULT) > 0.0
        assert information_current_deficit(PHI_STAR_DEFAULT * 0.9, PHI_STAR_DEFAULT) > 0.0

    def test_formula(self):
        for phi, phi_star in [(1.0, 2.0), (3.0, 3.0), (0.5, 1.0)]:
            d = information_current_deficit(phi, phi_star)
            expected = abs(1.0 - (phi / phi_star) ** 2)
            assert abs(d - expected) < 1e-14

    def test_approaches_one_as_phi_approaches_zero(self):
        d = information_current_deficit(1e-6, 1.0)
        assert abs(d - 1.0) < 1e-5

    def test_raises_phi_zero(self):
        with pytest.raises(ValueError):
            information_current_deficit(0.0, 1.0)

    def test_raises_phi_negative(self):
        with pytest.raises(ValueError):
            information_current_deficit(-1.0, 1.0)

    def test_raises_phi_star_zero(self):
        with pytest.raises(ValueError):
            information_current_deficit(1.0, 0.0)


# ===========================================================================
# information_current_conserved
# ===========================================================================

class TestInformationCurrentConserved:
    def test_true_at_phi_star(self):
        assert information_current_conserved(PHI_STAR_DEFAULT, PHI_STAR_DEFAULT) is True

    def test_false_away_from_phi_star(self):
        assert information_current_conserved(1.0, 100.0, tol=1e-3) is False

    def test_tol_respected(self):
        phi = PHI_STAR_DEFAULT * (1 + 1e-6)
        assert information_current_conserved(phi, PHI_STAR_DEFAULT, tol=1e-4) is True
        assert information_current_conserved(phi, PHI_STAR_DEFAULT, tol=1e-15) is False


# ===========================================================================
# moduli_dof_count
# ===========================================================================

class TestModuliDofCount:
    def test_returns_dict(self):
        result = moduli_dof_count(5, 7)
        assert isinstance(result, dict)

    def test_metric_components_5d(self):
        result = moduli_dof_count(5, 7)
        assert result["metric_components_5d"] == 15

    def test_kk_decomposition_sum(self):
        result = moduli_dof_count(5, 7)
        decomp = result["kk_decomposition"]
        assert decomp["g_munu"] + decomp["A_mu"] + decomp["phi"] == 15

    def test_braid_locked_modes(self):
        result = moduli_dof_count(5, 7)
        assert result["braid_locked_modes"] == [5, 7]

    def test_braid_locked_dof(self):
        result = moduli_dof_count(5, 7)
        assert result["braid_locked_dof"] == 2

    def test_zero_mode_dof(self):
        result = moduli_dof_count(5, 7)
        assert result["zero_mode_propagating_dof"] == 5

    def test_total_surviving_dof(self):
        result = moduli_dof_count(5, 7)
        assert result["total_surviving_dof"] == 7

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            moduli_dof_count(7, 5)


# ===========================================================================
# dimension_reduction_matrix
# ===========================================================================

class TestDimensionReductionMatrix:
    def test_shape(self):
        w = dimension_reduction_matrix(5, 7, 15)
        assert w.shape == (16,)

    def test_zero_mode_is_one(self):
        w = dimension_reduction_matrix(5, 7, 15)
        assert w[0] == 1.0

    def test_n1_is_one(self):
        w = dimension_reduction_matrix(5, 7, 15)
        assert w[5] == 1.0

    def test_n2_is_one(self):
        w = dimension_reduction_matrix(5, 7, 15)
        assert w[7] == 1.0

    def test_generic_mode_gaussian(self):
        w = dimension_reduction_matrix(5, 7, 15)
        for n in [1, 2, 3, 4, 6, 8]:
            expected = math.exp(-n * n / 74.0)
            assert abs(w[n] - expected) < 1e-12

    def test_all_positive(self):
        w = dimension_reduction_matrix(5, 7, 15)
        assert np.all(w > 0.0)

    def test_all_leq_one(self):
        w = dimension_reduction_matrix(5, 7, 15)
        assert np.all(w <= 1.0)

    def test_raises_bad_pair(self):
        with pytest.raises(ValueError):
            dimension_reduction_matrix(7, 5, 15)

    def test_raises_negative_nmax(self):
        with pytest.raises(ValueError):
            dimension_reduction_matrix(5, 7, -1)


# ===========================================================================
# kk_mass_spectrum
# ===========================================================================

class TestKKMassSpectrum:
    def test_shape(self):
        m = kk_mass_spectrum(10, 1.0)
        assert m.shape == (11,)

    def test_zero_mode_massless(self):
        m = kk_mass_spectrum(10, 1.0)
        assert m[0] == 0.0

    def test_linear(self):
        m = kk_mass_spectrum(5, 2.0)
        for n in range(6):
            assert abs(m[n] - n / 2.0) < 1e-14

    def test_raises_negative_nmax(self):
        with pytest.raises(ValueError):
            kk_mass_spectrum(-1, 1.0)

    def test_raises_zero_R(self):
        with pytest.raises(ValueError):
            kk_mass_spectrum(10, 0.0)


# ===========================================================================
# braid_effective_mass
# ===========================================================================

class TestBraidEffectiveMass:
    def test_zero_mode(self):
        assert braid_effective_mass(0, 5, 7, 1.0) == 0.0

    def test_braid_locked_softened(self):
        c_s = 12.0 / 37.0
        m5 = braid_effective_mass(5, 5, 7, 1.0)
        expected = 5.0 * c_s
        assert abs(m5 - expected) < 1e-10

    def test_n2_braid_locked_softened(self):
        c_s = 12.0 / 37.0
        m7 = braid_effective_mass(7, 5, 7, 1.0)
        expected = 7.0 * c_s
        assert abs(m7 - expected) < 1e-10

    def test_generic_mode_bare_mass(self):
        m3 = braid_effective_mass(3, 5, 7, 1.0)
        assert abs(m3 - 3.0) < 1e-14

    def test_braid_effective_less_than_bare(self):
        bare = 5.0 / 1.0
        soft = braid_effective_mass(5, 5, 7, 1.0)
        assert soft < bare

    def test_raises_negative_n(self):
        with pytest.raises(ValueError):
            braid_effective_mass(-1, 5, 7, 1.0)

    def test_raises_zero_R(self):
        with pytest.raises(ValueError):
            braid_effective_mass(3, 5, 7, 0.0)
