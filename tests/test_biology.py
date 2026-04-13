# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_biology.py
======================
Unit tests for the src/biology package.

Covers:
  - life.py   : negentropy_rate, metabolic_power, atp_synthesis_rate,
                information_current, is_living, cellular_phi_field,
                homeostasis_defect
  - evolution.py : fitness_landscape, selection_gradient, ftum_evolution_step,
                   genetic_drift, mutation_rate, species_distance,
                   extinction_criterion, population_entropy
  - morphogenesis.py : turing_instability_condition, morphogen_gradient,
                       morphogen_length_scale, turing_wavelength,
                       segment_count, positional_information,
                       reaction_diffusion_step
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.biology.life import (
    negentropy_rate,
    metabolic_power,
    atp_synthesis_rate,
    information_current,
    is_living,
    cellular_phi_field,
    homeostasis_defect,
)
from src.biology.evolution import (
    fitness_landscape,
    selection_gradient,
    ftum_evolution_step,
    genetic_drift,
    mutation_rate,
    species_distance,
    extinction_criterion,
    population_entropy,
)
from src.biology.morphogenesis import (
    turing_instability_condition,
    morphogen_gradient,
    morphogen_length_scale,
    turing_wavelength,
    segment_count,
    positional_information,
    reaction_diffusion_step,
)


# ===========================================================================
# life.py — TestNegentropicRate
# ===========================================================================

class TestNegentropicRate:
    def test_phi_greater_gives_positive(self):
        assert negentropy_rate(2.0, 1.0) > 0.0

    def test_phi_equal_gives_zero(self):
        assert negentropy_rate(1.5, 1.5) == pytest.approx(0.0)

    def test_phi_less_gives_negative(self):
        assert negentropy_rate(1.0, 2.0) < 0.0

    def test_error_phi_zero(self):
        with pytest.raises(ValueError):
            negentropy_rate(0.0, 1.0)

    def test_error_phi_negative(self):
        with pytest.raises(ValueError):
            negentropy_rate(-1.0, 1.0)

    def test_error_phi_env_zero(self):
        with pytest.raises(ValueError):
            negentropy_rate(1.0, 0.0)

    def test_scales_with_lam(self):
        r1 = negentropy_rate(2.0, 1.0, lam=1.0)
        r2 = negentropy_rate(2.0, 1.0, lam=2.0)
        assert r2 == pytest.approx(2.0 * r1)

    def test_formula_explicit(self):
        result = negentropy_rate(3.0, 1.0, lam=2.0)
        assert result == pytest.approx(2.0 * (9.0 - 1.0))


# ===========================================================================
# life.py — TestMetabolicPower
# ===========================================================================

class TestMetabolicPower:
    def test_positive_result(self):
        assert metabolic_power(2.0, 3.0) > 0.0

    def test_scales_as_B_squared(self):
        p1 = metabolic_power(1.0, 1.0)
        p2 = metabolic_power(1.0, 2.0)
        assert p2 == pytest.approx(4.0 * p1)

    def test_scales_as_phi_squared(self):
        p1 = metabolic_power(1.0, 2.0)
        p2 = metabolic_power(2.0, 2.0)
        assert p2 == pytest.approx(4.0 * p1)

    def test_formula_explicit(self):
        # lam=1, phi=2, B=3 → 1 * 4 * 9 / 2 = 18
        assert metabolic_power(2.0, 3.0, lam=1.0) == pytest.approx(18.0)

    def test_error_phi_zero(self):
        with pytest.raises(ValueError):
            metabolic_power(0.0, 1.0)

    def test_error_phi_negative(self):
        with pytest.raises(ValueError):
            metabolic_power(-1.0, 1.0)

    def test_error_B_negative(self):
        with pytest.raises(ValueError):
            metabolic_power(1.0, -0.1)

    def test_zero_B_gives_zero(self):
        assert metabolic_power(2.0, 0.0) == pytest.approx(0.0)


# ===========================================================================
# life.py — TestAtpSynthesisRate
# ===========================================================================

class TestAtpSynthesisRate:
    def test_zero_gradient_gives_one(self):
        assert atp_synthesis_rate(0.0, 1.0) == pytest.approx(1.0)

    def test_positive_and_bounded(self):
        r = atp_synthesis_rate(1.0, 1.0)
        assert 0.0 < r < 1.0

    def test_larger_gradient_slower_rate(self):
        r_small = atp_synthesis_rate(0.5, 1.0)
        r_large = atp_synthesis_rate(2.0, 1.0)
        assert r_large < r_small

    def test_higher_T_increases_rate(self):
        r_low = atp_synthesis_rate(1.0, 0.5)
        r_high = atp_synthesis_rate(1.0, 2.0)
        assert r_high > r_low

    def test_error_T_zero(self):
        with pytest.raises(ValueError):
            atp_synthesis_rate(1.0, 0.0)

    def test_error_T_negative(self):
        with pytest.raises(ValueError):
            atp_synthesis_rate(1.0, -1.0)

    def test_formula_explicit(self):
        # exp(-1/(1*2)) = exp(-0.5)
        assert atp_synthesis_rate(1.0, 2.0, k_B=1.0) == pytest.approx(np.exp(-0.5))


# ===========================================================================
# life.py — TestInformationCurrent
# ===========================================================================

class TestInformationCurrent:
    def test_phi1_v1_gives_one(self):
        assert information_current(1.0, 1.0) == pytest.approx(1.0)

    def test_scales_as_phi_squared(self):
        j1 = information_current(1.0, 1.0)
        j2 = information_current(2.0, 1.0)
        assert j2 == pytest.approx(4.0 * j1)

    def test_scales_linearly_with_v(self):
        j1 = information_current(1.0, 2.0)
        j2 = information_current(1.0, 4.0)
        assert j2 == pytest.approx(2.0 * j1)

    def test_error_phi_zero(self):
        with pytest.raises(ValueError):
            information_current(0.0)

    def test_error_phi_negative(self):
        with pytest.raises(ValueError):
            information_current(-1.0)

    def test_formula_explicit(self):
        assert information_current(3.0, 2.0) == pytest.approx(18.0)


# ===========================================================================
# life.py — TestIsLiving
# ===========================================================================

class TestIsLiving:
    def test_phi_greater_returns_true(self):
        assert is_living(2.0, 1.0) is True

    def test_phi_equal_returns_false(self):
        assert is_living(1.0, 1.0) is False

    def test_phi_less_returns_false(self):
        assert is_living(0.5, 1.0) is False

    def test_threshold_respected(self):
        # negentropy_rate(1.1, 1.0) = 1.1²-1² = 0.21; threshold=0.3 → False
        assert is_living(1.1, 1.0, threshold=0.3) is False
        assert is_living(2.0, 1.0, threshold=0.3) is True


# ===========================================================================
# life.py — TestCellularPhiField
# ===========================================================================

class TestCellularPhiField:
    def test_shape(self):
        field = cellular_phi_field(50, 1.0)
        assert field.shape == (50,)

    def test_mean_close_to_phi_mean(self):
        field = cellular_phi_field(10000, 1.0, sigma=0.1, seed=0)
        assert np.mean(field) == pytest.approx(1.0, abs=0.05)

    def test_error_n_cells_zero(self):
        with pytest.raises(ValueError):
            cellular_phi_field(0, 1.0)

    def test_error_phi_mean_zero(self):
        with pytest.raises(ValueError):
            cellular_phi_field(10, 0.0)

    def test_error_phi_mean_negative(self):
        with pytest.raises(ValueError):
            cellular_phi_field(10, -1.0)

    def test_reproducible_with_seed(self):
        f1 = cellular_phi_field(20, 1.0, seed=7)
        f2 = cellular_phi_field(20, 1.0, seed=7)
        np.testing.assert_array_equal(f1, f2)

    def test_different_seeds_differ(self):
        f1 = cellular_phi_field(20, 1.0, seed=1)
        f2 = cellular_phi_field(20, 1.0, seed=2)
        assert not np.allclose(f1, f2)


# ===========================================================================
# life.py — TestHomeostasisDefect
# ===========================================================================

class TestHomeostasisDefect:
    def test_perfect_homeostasis(self):
        field = np.ones(100) * 2.0
        assert homeostasis_defect(field, 2.0) == pytest.approx(0.0)

    def test_deviation_positive(self):
        field = np.ones(10) * 3.0
        assert homeostasis_defect(field, 2.0) == pytest.approx(1.0)

    def test_symmetric(self):
        field = np.ones(10) * 1.0
        d_above = homeostasis_defect(field, 1.5)
        d_below = homeostasis_defect(field, 0.5)
        assert d_above == pytest.approx(d_below)

    def test_array_mean_used(self):
        field = np.array([1.0, 3.0])   # mean = 2.0
        assert homeostasis_defect(field, 2.0) == pytest.approx(0.0)


# ===========================================================================
# evolution.py — TestFitnessLandscape
# ===========================================================================

class TestFitnessLandscape:
    def test_shape_preserved(self):
        phi = np.linspace(0, 4, 50)
        f = fitness_landscape(phi, 2.0)
        assert f.shape == phi.shape

    def test_peak_at_optimal(self):
        phi = np.array([1.0, 2.0, 3.0])
        f = fitness_landscape(phi, 2.0)
        assert f[1] == pytest.approx(1.0)

    def test_values_between_zero_and_one(self):
        phi = np.linspace(-5, 5, 100)
        f = fitness_landscape(phi, 0.0)
        assert np.all(f > 0.0) and np.all(f <= 1.0)

    def test_error_width_zero(self):
        with pytest.raises(ValueError):
            fitness_landscape(np.array([1.0]), 1.0, width=0.0)

    def test_error_width_negative(self):
        with pytest.raises(ValueError):
            fitness_landscape(np.array([1.0]), 1.0, width=-1.0)

    def test_wider_peak_flatter(self):
        phi = np.array([1.0, 2.0])  # off-peak
        f_narrow = fitness_landscape(phi, 2.0, width=0.5)
        f_wide = fitness_landscape(phi, 2.0, width=2.0)
        assert f_wide[0] > f_narrow[0]


# ===========================================================================
# evolution.py — TestSelectionGradient
# ===========================================================================

class TestSelectionGradient:
    def test_shape_preserved(self):
        phi = np.linspace(0, 4, 40)
        g = selection_gradient(phi, 2.0)
        assert g.shape == phi.shape

    def test_zero_at_peak(self):
        phi = np.array([2.0])
        g = selection_gradient(phi, 2.0)
        assert g[0] == pytest.approx(0.0, abs=1e-12)

    def test_positive_below_peak(self):
        g = selection_gradient(np.array([1.0]), 2.0)
        assert g[0] > 0.0

    def test_negative_above_peak(self):
        g = selection_gradient(np.array([3.0]), 2.0)
        assert g[0] < 0.0

    def test_antisymmetric_around_peak(self):
        g_left = selection_gradient(np.array([1.0]), 2.0)
        g_right = selection_gradient(np.array([3.0]), 2.0)
        assert g_left[0] == pytest.approx(-g_right[0])


# ===========================================================================
# evolution.py — TestFtumEvolutionStep
# ===========================================================================

class TestFtumEvolutionStep:
    def test_shape_preserved(self):
        phi = np.array([0.5, 1.0, 1.5, 2.5, 3.0])
        phi_new = ftum_evolution_step(phi, 2.0)
        assert phi_new.shape == phi.shape

    def test_moves_toward_optimal_from_below(self):
        phi = np.array([1.0])
        phi_new = ftum_evolution_step(phi, 2.0, learning_rate=0.1)
        assert phi_new[0] > phi[0]

    def test_moves_toward_optimal_from_above(self):
        phi = np.array([3.0])
        phi_new = ftum_evolution_step(phi, 2.0, learning_rate=0.1)
        assert phi_new[0] < phi[0]

    def test_no_change_at_peak(self):
        phi = np.array([2.0])
        phi_new = ftum_evolution_step(phi, 2.0)
        assert phi_new[0] == pytest.approx(phi[0])

    def test_larger_lr_bigger_step(self):
        phi = np.array([1.0])
        delta_small = ftum_evolution_step(phi, 2.0, learning_rate=0.01)[0] - phi[0]
        delta_large = ftum_evolution_step(phi, 2.0, learning_rate=0.1)[0] - phi[0]
        assert abs(delta_large) > abs(delta_small)


# ===========================================================================
# evolution.py — TestGeneticDrift
# ===========================================================================

class TestGeneticDrift:
    def test_shape_preserved(self):
        phi = np.ones(30)
        phi_d = genetic_drift(phi, 0.1, seed=0)
        assert phi_d.shape == phi.shape

    def test_zero_sigma_unchanged(self):
        phi = np.array([1.0, 2.0, 3.0])
        phi_d = genetic_drift(phi, 0.0, seed=42)
        np.testing.assert_allclose(phi_d, phi)

    def test_nonzero_sigma_changes_values(self):
        phi = np.ones(100)
        phi_d = genetic_drift(phi, 0.5, seed=1)
        assert not np.allclose(phi_d, phi)

    def test_reproducible_with_seed(self):
        phi = np.ones(20)
        d1 = genetic_drift(phi, 0.2, seed=5)
        d2 = genetic_drift(phi, 0.2, seed=5)
        np.testing.assert_array_equal(d1, d2)


# ===========================================================================
# evolution.py — TestMutationRate
# ===========================================================================

class TestMutationRate:
    def test_B_zero_gives_base_rate(self):
        assert mutation_rate(0.0, base_rate=1e-8) == pytest.approx(1e-8)

    def test_increases_with_B(self):
        r1 = mutation_rate(1.0)
        r2 = mutation_rate(10.0)
        assert r2 > r1

    def test_error_B_negative(self):
        with pytest.raises(ValueError):
            mutation_rate(-0.1)

    def test_formula_explicit(self):
        assert mutation_rate(4.0, base_rate=1.0) == pytest.approx(5.0)


# ===========================================================================
# evolution.py — (extra coverage) species_distance, extinction_criterion,
#                population_entropy
# ===========================================================================

class TestSpeciesDistance:
    def test_same_species(self):
        assert species_distance(1.5, 1.5) == pytest.approx(0.0)

    def test_symmetric(self):
        assert species_distance(1.0, 3.0) == pytest.approx(species_distance(3.0, 1.0))

    def test_value(self):
        assert species_distance(1.0, 4.0) == pytest.approx(3.0)


class TestExtinctionCriterion:
    def test_below_min_extinct(self):
        assert extinction_criterion(0.005, phi_min=0.01) is True

    def test_above_min_alive(self):
        assert extinction_criterion(0.02, phi_min=0.01) is False

    def test_at_min_alive(self):
        assert extinction_criterion(0.01, phi_min=0.01) is False


class TestPopulationEntropy:
    def test_non_negative(self):
        phi = np.random.default_rng(0).normal(2.0, 0.3, 200)
        assert population_entropy(phi) >= 0.0

    def test_uniform_pop_higher_entropy(self):
        uniform = np.linspace(0, 4, 200)
        clustered = np.ones(200) * 2.0
        assert population_entropy(uniform) > population_entropy(clustered)

    def test_single_value_low_entropy(self):
        phi = np.ones(50) * 1.0
        assert population_entropy(phi) < 0.5


# ===========================================================================
# morphogenesis.py — TestTuringInstabilityCondition
# ===========================================================================

class TestTuringInstabilityCondition:
    def test_known_unstable_case(self):
        # D_u=1, D_v=100, a=1, b=1 → threshold=(1+1)²=4 → 100/1=100 > 4 → True
        assert turing_instability_condition(1.0, 100.0, 1.0, 1.0) is True

    def test_known_stable_case(self):
        # D_v/D_u = 2, threshold=(1+1)²=4 → 2 < 4 → False
        assert turing_instability_condition(1.0, 2.0, 1.0, 1.0) is False

    def test_error_Du_zero(self):
        with pytest.raises(ValueError):
            turing_instability_condition(0.0, 1.0, 1.0, 1.0)

    def test_error_Dv_zero(self):
        with pytest.raises(ValueError):
            turing_instability_condition(1.0, 0.0, 1.0, 1.0)

    def test_a_zero_returns_false(self):
        assert turing_instability_condition(1.0, 10.0, 0.0, 1.0) is False

    def test_b_zero_returns_false(self):
        assert turing_instability_condition(1.0, 10.0, 1.0, 0.0) is False


# ===========================================================================
# morphogenesis.py — TestMorphogenGradient
# ===========================================================================

class TestMorphogenGradient:
    def test_shape_preserved(self):
        x = np.linspace(0, 10, 50)
        phi = morphogen_gradient(x, 2.0, 1.0)
        assert phi.shape == x.shape

    def test_x_zero_equals_phi0(self):
        assert morphogen_gradient(np.array([0.0]), 3.0, 1.0)[0] == pytest.approx(3.0)

    def test_decaying_with_x(self):
        x = np.array([0.0, 1.0, 2.0, 3.0])
        phi = morphogen_gradient(x, 1.0, 1.0)
        assert np.all(np.diff(phi) < 0)

    def test_error_phi0_zero(self):
        with pytest.raises(ValueError):
            morphogen_gradient(np.array([1.0]), 0.0, 1.0)

    def test_error_lam_m_zero(self):
        with pytest.raises(ValueError):
            morphogen_gradient(np.array([1.0]), 1.0, 0.0)

    def test_formula_explicit(self):
        x = np.array([1.0])
        val = morphogen_gradient(x, 2.0, 2.0)[0]
        assert val == pytest.approx(2.0 * np.exp(-0.5))


# ===========================================================================
# morphogenesis.py — TestMorphogenLengthScale
# ===========================================================================

class TestMorphogenLengthScale:
    def test_formula(self):
        assert morphogen_length_scale(4.0, 1.0) == pytest.approx(2.0)

    def test_error_D_zero(self):
        with pytest.raises(ValueError):
            morphogen_length_scale(0.0, 1.0)

    def test_error_k_deg_zero(self):
        with pytest.raises(ValueError):
            morphogen_length_scale(1.0, 0.0)


# ===========================================================================
# morphogenesis.py — TestTuringWavelength
# ===========================================================================

class TestTuringWavelength:
    def test_unstable_regime_positive(self):
        # D_u=1, D_v=100, a=1, b=1 is unstable
        lam = turing_wavelength(1.0, 100.0, 1.0, 1.0)
        assert np.isfinite(lam) and lam > 0.0

    def test_stable_regime_returns_inf(self):
        lam = turing_wavelength(1.0, 2.0, 1.0, 1.0)
        assert lam == np.inf

    def test_larger_diffusivity_longer_wavelength(self):
        lam_slow = turing_wavelength(1.0, 50.0, 1.0, 1.0)
        lam_fast = turing_wavelength(1.0, 200.0, 1.0, 1.0)
        # Both should be finite and positive; verify we get distinct values
        assert np.isfinite(lam_slow) and np.isfinite(lam_fast)

    def test_zero_a_returns_inf(self):
        lam = turing_wavelength(1.0, 10.0, 0.0, 1.0)
        assert lam == np.inf


# ===========================================================================
# morphogenesis.py — TestSegmentCount
# ===========================================================================

class TestSegmentCount:
    def test_n_w_1(self):
        assert segment_count(1) == 2

    def test_n_w_5(self):
        assert segment_count(5) == 10

    def test_n_w_12(self):
        assert segment_count(12) == 24

    def test_error_n_w_zero(self):
        with pytest.raises(ValueError):
            segment_count(0)

    def test_error_n_w_negative(self):
        with pytest.raises(ValueError):
            segment_count(-3)


# ===========================================================================
# morphogenesis.py — TestPositionalInformation
# ===========================================================================

class TestPositionalInformation:
    def test_non_negative(self):
        phi = np.linspace(0, 4, 100)
        assert positional_information(phi) >= 0.0

    def test_uniform_has_higher_info(self):
        uniform = np.linspace(0, 4, 100)
        clustered = np.ones(100) * 2.0
        assert positional_information(uniform) > positional_information(clustered)

    def test_n_types_respected(self):
        phi = np.linspace(0, 4, 100)
        h4 = positional_information(phi, n_types=4)
        h8 = positional_information(phi, n_types=8)
        assert isinstance(h4, float) and isinstance(h8, float)


# ===========================================================================
# morphogenesis.py — TestReactionDiffusionStep
# ===========================================================================

class TestReactionDiffusionStep:
    @pytest.fixture
    def gray_scott_fields(self):
        rng = np.random.default_rng(42)
        N = 64
        u = 0.5 * np.ones(N) + 0.01 * rng.standard_normal(N)
        v = 0.25 * np.ones(N) + 0.01 * rng.standard_normal(N)
        return u, v, N

    def test_shape_preserved(self, gray_scott_fields):
        u, v, N = gray_scott_fields
        u_new, v_new = reaction_diffusion_step(u, v, 0.2, 0.1, 0.04, 0.06)
        assert u_new.shape == (N,) and v_new.shape == (N,)

    def test_changes_values(self, gray_scott_fields):
        u, v, _ = gray_scott_fields
        u_new, v_new = reaction_diffusion_step(u, v, 0.2, 0.1, 0.04, 0.06)
        assert not np.allclose(u_new, u)

    def test_error_Du_zero(self, gray_scott_fields):
        u, v, _ = gray_scott_fields
        with pytest.raises(ValueError):
            reaction_diffusion_step(u, v, 0.0, 0.1, 0.04, 0.06)

    def test_error_Dv_zero(self, gray_scott_fields):
        u, v, _ = gray_scott_fields
        with pytest.raises(ValueError):
            reaction_diffusion_step(u, v, 0.2, 0.0, 0.04, 0.06)

    def test_error_dt_zero(self, gray_scott_fields):
        u, v, _ = gray_scott_fields
        with pytest.raises(ValueError):
            reaction_diffusion_step(u, v, 0.2, 0.1, 0.04, 0.06, dt=0.0)

    def test_small_dt_small_change(self, gray_scott_fields):
        u, v, _ = gray_scott_fields
        u_big, _ = reaction_diffusion_step(u, v, 0.2, 0.1, 0.04, 0.06, dt=0.1)
        u_small, _ = reaction_diffusion_step(u, v, 0.2, 0.1, 0.04, 0.06, dt=0.001)
        assert np.max(np.abs(u_small - u)) < np.max(np.abs(u_big - u))

    def test_pure_diffusion_no_reaction(self):
        # f=0, k=1 means v decays to 0; uv² term negligible for small v
        N = 32
        u = np.ones(N)
        v = np.zeros(N)
        u_new, v_new = reaction_diffusion_step(u, v, 0.2, 0.1, 0.0, 1.0)
        # u should remain ~1 (no reaction, uniform so no diffusion flux)
        np.testing.assert_allclose(u_new, np.ones(N), atol=1e-10)
