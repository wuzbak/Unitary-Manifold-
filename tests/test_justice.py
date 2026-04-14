# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_justice.py
======================
Unit tests for the src/justice package — Pillar 18.

Covers:
  - courts.py    : verdict_phi_shift, representation_quality, bias_noise_floor,
                   plea_pressure_index, charging_disparity,
                   mandatory_minimum_entropy, civil_asset_phi_loss,
                   case_backlog_entropy, equal_protection_score, bail_phi_impact
  - sentencing.py: just_sentence_length, recidivism_probability,
                   sentencing_disparity_index, incarceration_community_entropy,
                   rehabilitation_phi_gain, collateral_damage_index,
                   solitary_phi_depletion, prison_overcrowding_entropy,
                   restorative_justice_phi_restoration,
                   mass_incarceration_social_cost
  - reform.py    : reform_activation_energy, policy_phi_shift,
                   reform_coalition_strength, public_defender_parity_gap,
                   transparency_score, drug_decrim_phi_gain,
                   police_accountability_reduction, reform_timeline,
                   recidivism_reduction_from_reform, justice_system_phi
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.justice.courts import (
    verdict_phi_shift,
    representation_quality,
    bias_noise_floor,
    plea_pressure_index,
    charging_disparity,
    mandatory_minimum_entropy,
    civil_asset_phi_loss,
    case_backlog_entropy,
    equal_protection_score,
    bail_phi_impact,
)
from src.justice.sentencing import (
    just_sentence_length,
    recidivism_probability,
    sentencing_disparity_index,
    incarceration_community_entropy,
    rehabilitation_phi_gain,
    collateral_damage_index,
    solitary_phi_depletion,
    prison_overcrowding_entropy,
    restorative_justice_phi_restoration,
    mass_incarceration_social_cost,
)
from src.justice.reform import (
    reform_activation_energy,
    policy_phi_shift,
    reform_coalition_strength,
    public_defender_parity_gap,
    transparency_score,
    drug_decrim_phi_gain,
    police_accountability_reduction,
    reform_timeline,
    recidivism_reduction_from_reform,
    justice_system_phi,
)


# ===========================================================================
# TestCourts
# ===========================================================================

class TestCourts:
    # --- verdict_phi_shift ---

    def test_verdict_phi_shift_positive_restoration(self):
        assert verdict_phi_shift(1.0, 1.5) == pytest.approx(0.5)

    def test_verdict_phi_shift_negative_injustice(self):
        assert verdict_phi_shift(2.0, 1.0) == pytest.approx(-1.0)

    def test_verdict_phi_shift_neutral(self):
        assert verdict_phi_shift(1.0, 1.0) == pytest.approx(0.0)

    def test_verdict_phi_shift_error_pre_zero(self):
        with pytest.raises(ValueError):
            verdict_phi_shift(0.0, 1.0)

    def test_verdict_phi_shift_error_post_negative(self):
        with pytest.raises(ValueError):
            verdict_phi_shift(1.0, -0.1)

    # --- representation_quality ---

    def test_representation_quality_zero_income_gives_lam_public(self):
        result = representation_quality(0.0, 50000.0, 0.2, 1.0)
        assert result == pytest.approx(0.2)

    def test_representation_quality_high_income_approaches_lam_private(self):
        result = representation_quality(1e9, 50000.0, 0.2, 1.0)
        assert result > 0.99

    def test_representation_quality_median_income_gives_midpoint(self):
        result = representation_quality(50000.0, 50000.0, 0.0, 1.0)
        assert result == pytest.approx(0.5)

    def test_representation_quality_error_negative_income(self):
        with pytest.raises(ValueError):
            representation_quality(-1.0, 50000.0, 0.2, 1.0)

    def test_representation_quality_error_zero_median(self):
        with pytest.raises(ValueError):
            representation_quality(1000.0, 0.0, 0.2, 1.0)

    def test_representation_quality_error_lam_private_lt_lam_public(self):
        with pytest.raises(ValueError):
            representation_quality(1000.0, 50000.0, 0.8, 0.5)

    # --- bias_noise_floor ---

    def test_bias_noise_floor_all_zero(self):
        assert bias_noise_floor(0.0, 0.0, 0.0) == pytest.approx(0.0)

    def test_bias_noise_floor_unit_vectors(self):
        assert bias_noise_floor(1.0, 0.0, 0.0) == pytest.approx(1.0)
        assert bias_noise_floor(0.0, 1.0, 0.0) == pytest.approx(1.0)

    def test_bias_noise_floor_pythagorean(self):
        assert bias_noise_floor(3.0, 4.0, 0.0) == pytest.approx(5.0)

    def test_bias_noise_floor_error_negative(self):
        with pytest.raises(ValueError):
            bias_noise_floor(-0.1, 0.0, 0.0)

    # --- plea_pressure_index ---

    def test_plea_pressure_index_zero_gap(self):
        assert plea_pressure_index(10.0, 10.0) == pytest.approx(0.0, abs=1e-9)

    def test_plea_pressure_index_large_gap_below_one(self):
        ppi = plea_pressure_index(100.0, 1.0)
        assert 0.0 <= ppi < 1.0

    def test_plea_pressure_index_monotone_with_trial_sentence(self):
        ppi1 = plea_pressure_index(10.0, 1.0)
        ppi2 = plea_pressure_index(20.0, 1.0)
        assert ppi2 > ppi1

    def test_plea_pressure_index_error_negative_trial(self):
        with pytest.raises(ValueError):
            plea_pressure_index(-1.0, 0.0)

    # --- charging_disparity ---

    def test_charging_disparity_equal_sentences(self):
        assert charging_disparity(2.0, 5.0, 5.0) == pytest.approx(0.0)

    def test_charging_disparity_scales_with_difference(self):
        d1 = charging_disparity(2.0, 10.0, 8.0)
        d2 = charging_disparity(2.0, 14.0, 8.0)
        assert d2 > d1

    def test_charging_disparity_zero_phi_offense(self):
        d = charging_disparity(0.0, 10.0, 5.0)
        assert d > 1e10

    def test_charging_disparity_error_negative_sentence(self):
        with pytest.raises(ValueError):
            charging_disparity(1.0, -5.0, 3.0)

    # --- mandatory_minimum_entropy ---

    def test_mandatory_minimum_entropy_equal_sentences_zero(self):
        assert mandatory_minimum_entropy(5.0, 5.0, 100) == pytest.approx(0.0)

    def test_mandatory_minimum_entropy_increases_with_n_cases(self):
        s1 = mandatory_minimum_entropy(10.0, 5.0, 100)
        s2 = mandatory_minimum_entropy(10.0, 5.0, 200)
        assert s2 == pytest.approx(2.0 * s1)

    def test_mandatory_minimum_entropy_zero_cases(self):
        assert mandatory_minimum_entropy(10.0, 5.0, 0) == pytest.approx(0.0)

    def test_mandatory_minimum_entropy_error_negative_mandatory(self):
        with pytest.raises(ValueError):
            mandatory_minimum_entropy(-1.0, 5.0, 10)

    # --- civil_asset_phi_loss ---

    def test_civil_asset_phi_loss_certain_conviction(self):
        assert civil_asset_phi_loss(1000.0, 1.0) == pytest.approx(0.0)

    def test_civil_asset_phi_loss_zero_conviction_prob(self):
        assert civil_asset_phi_loss(1000.0, 0.0) == pytest.approx(1000.0)

    def test_civil_asset_phi_loss_half_prob(self):
        assert civil_asset_phi_loss(1000.0, 0.5) == pytest.approx(500.0)

    def test_civil_asset_phi_loss_error_invalid_prob(self):
        with pytest.raises(ValueError):
            civil_asset_phi_loss(500.0, 1.5)

    # --- equal_protection_score ---

    def test_equal_protection_score_identical_rates(self):
        rates = np.array([0.5, 0.5, 0.5])
        assert equal_protection_score(rates) == pytest.approx(1.0)

    def test_equal_protection_score_high_disparity_low_score(self):
        rates = np.array([0.1, 0.9])
        score = equal_protection_score(rates)
        assert score < 0.5

    def test_equal_protection_score_clipped_at_zero(self):
        rates = np.array([0.01, 0.99])
        assert equal_protection_score(rates) >= 0.0

    def test_equal_protection_score_error_too_few_elements(self):
        with pytest.raises(ValueError):
            equal_protection_score(np.array([0.5]))

    def test_bail_phi_impact_zero_bail(self):
        assert bail_phi_impact(0.0, 3000.0) == pytest.approx(0.0)

    def test_bail_phi_impact_exceeds_income_clips_to_one(self):
        assert bail_phi_impact(100000.0, 500.0) == pytest.approx(1.0)

    def test_bail_phi_impact_proportional(self):
        i1 = bail_phi_impact(500.0, 2000.0)
        i2 = bail_phi_impact(1000.0, 2000.0)
        assert i2 == pytest.approx(2.0 * i1, rel=1e-5)

    def test_bail_phi_impact_error_negative_bail(self):
        with pytest.raises(ValueError):
            bail_phi_impact(-100.0, 2000.0)


# ===========================================================================
# TestSentencing
# ===========================================================================

class TestSentencing:
    # --- just_sentence_length ---

    def test_just_sentence_length_basic(self):
        assert just_sentence_length(2.0, 3.0, 1.0) == pytest.approx(5.0)

    def test_just_sentence_length_scales_with_lambda(self):
        l1 = just_sentence_length(1.0, 1.0, 1.0)
        l2 = just_sentence_length(1.0, 1.0, 3.0)
        assert l2 == pytest.approx(3.0 * l1)

    def test_just_sentence_length_zero_harm(self):
        assert just_sentence_length(0.0, 0.0, 2.0) == pytest.approx(0.0)

    def test_just_sentence_length_error_negative_offense(self):
        with pytest.raises(ValueError):
            just_sentence_length(-1.0, 1.0, 1.0)

    def test_just_sentence_length_error_zero_lambda(self):
        with pytest.raises(ValueError):
            just_sentence_length(1.0, 1.0, 0.0)

    # --- recidivism_probability ---

    def test_recidivism_probability_zero_support_equals_base(self):
        p = recidivism_probability(0.0, 0.0, 0.68)
        assert p == pytest.approx(0.68)

    def test_recidivism_probability_decreases_with_phi(self):
        p_low = recidivism_probability(0.5, 0.5, 0.68)
        p_high = recidivism_probability(2.0, 2.0, 0.68)
        assert p_high < p_low

    def test_recidivism_probability_bounded_above_by_base(self):
        p = recidivism_probability(1.0, 1.0, 0.5)
        assert p <= 0.5

    def test_recidivism_probability_error_invalid_base(self):
        with pytest.raises(ValueError):
            recidivism_probability(1.0, 1.0, 1.5)

    def test_recidivism_probability_error_negative_phi(self):
        with pytest.raises(ValueError):
            recidivism_probability(-0.1, 1.0, 0.5)

    # --- sentencing_disparity_index ---

    def test_sentencing_disparity_index_equal_groups(self):
        sentences = np.array([5.0, 5.0, 5.0, 5.0])
        labels = np.array([0, 0, 1, 1])
        assert sentencing_disparity_index(sentences, labels) == pytest.approx(0.0, abs=1e-9)

    def test_sentencing_disparity_index_clear_disparity(self):
        sentences = np.array([3.0, 3.0, 6.0, 6.0])
        labels = np.array([0, 0, 1, 1])
        sdi = sentencing_disparity_index(sentences, labels)
        assert sdi == pytest.approx(1.0, rel=1e-5)

    def test_sentencing_disparity_index_error_one_group(self):
        with pytest.raises(ValueError):
            sentencing_disparity_index(np.array([5.0, 5.0]), np.array([0, 0]))

    def test_sentencing_disparity_index_error_negative_sentence(self):
        with pytest.raises(ValueError):
            sentencing_disparity_index(np.array([-1.0, 5.0]), np.array([0, 1]))

    # --- incarceration_community_entropy ---

    def test_incarceration_community_entropy_none_incarcerated(self):
        assert incarceration_community_entropy(0, 1000) == pytest.approx(0.0)

    def test_incarceration_community_entropy_all_incarcerated(self):
        assert incarceration_community_entropy(500, 500) == pytest.approx(1.0)

    def test_incarceration_community_entropy_clips_at_one(self):
        assert incarceration_community_entropy(1000, 500) == pytest.approx(1.0)

    def test_incarceration_community_entropy_error_zero_community(self):
        with pytest.raises(ValueError):
            incarceration_community_entropy(10, 0)

    # --- rehabilitation_phi_gain ---

    def test_rehabilitation_phi_gain_zero_duration(self):
        assert rehabilitation_phi_gain(1.0, 0.5, 0.0) == pytest.approx(1.0)

    def test_rehabilitation_phi_gain_increases_with_duration(self):
        g1 = rehabilitation_phi_gain(1.0, 1.0, 6.0)
        g2 = rehabilitation_phi_gain(1.0, 1.0, 12.0)
        assert g2 > g1

    def test_rehabilitation_phi_gain_formula(self):
        result = rehabilitation_phi_gain(2.0, 1.0, 12.0)
        assert result == pytest.approx(2.0 * (1.0 + 1.0))

    def test_rehabilitation_phi_gain_error_zero_intake(self):
        with pytest.raises(ValueError):
            rehabilitation_phi_gain(0.0, 0.5, 6.0)

    def test_rehabilitation_phi_gain_error_invalid_intensity(self):
        with pytest.raises(ValueError):
            rehabilitation_phi_gain(1.0, 1.5, 6.0)

    # --- collateral_damage_index ---

    def test_collateral_damage_index_zero_dependents(self):
        assert collateral_damage_index(5.0, 0) == pytest.approx(0.0)

    def test_collateral_damage_index_scales_linearly(self):
        cdi1 = collateral_damage_index(2.0, 3)
        cdi2 = collateral_damage_index(4.0, 3)
        assert cdi2 == pytest.approx(2.0 * cdi1)

    def test_collateral_damage_index_formula(self):
        assert collateral_damage_index(3.0, 4) == pytest.approx(12.0)

    def test_collateral_damage_index_error_negative_years(self):
        with pytest.raises(ValueError):
            collateral_damage_index(-1.0, 2)

    # --- solitary_phi_depletion ---

    def test_solitary_phi_depletion_zero_days(self):
        assert solitary_phi_depletion(0.0, 0.01) == pytest.approx(0.0)

    def test_solitary_phi_depletion_many_days_approaches_one(self):
        loss = solitary_phi_depletion(10000.0, 1.0)
        assert loss == pytest.approx(1.0, abs=1e-6)

    def test_solitary_phi_depletion_monotone(self):
        l1 = solitary_phi_depletion(10.0, 0.1)
        l2 = solitary_phi_depletion(20.0, 0.1)
        assert l2 > l1

    def test_solitary_phi_depletion_error_zero_rate(self):
        with pytest.raises(ValueError):
            solitary_phi_depletion(10.0, 0.0)

    # --- prison_overcrowding_entropy ---

    def test_prison_overcrowding_entropy_at_capacity(self):
        assert prison_overcrowding_entropy(100, 100) == pytest.approx(0.0, abs=1e-9)

    def test_prison_overcrowding_entropy_overcrowded(self):
        s = prison_overcrowding_entropy(150, 100)
        assert s == pytest.approx(50.0 / 100.0, rel=1e-5)

    def test_prison_overcrowding_entropy_under_capacity(self):
        assert prison_overcrowding_entropy(50, 100) == pytest.approx(0.0)

    def test_prison_overcrowding_entropy_error_zero_capacity(self):
        with pytest.raises(ValueError):
            prison_overcrowding_entropy(10, 0)

    # --- restorative_justice_phi_restoration ---

    def test_restorative_phi_restoration_full_recovery(self):
        r = restorative_justice_phi_restoration(1.0, 2.0)
        assert r == pytest.approx(1.0, rel=1e-5)

    def test_restorative_phi_restoration_no_change(self):
        r = restorative_justice_phi_restoration(1.0, 1.0)
        assert r == pytest.approx(0.0, abs=1e-9)

    def test_restorative_phi_restoration_negative_outcome(self):
        r = restorative_justice_phi_restoration(2.0, 1.0)
        assert r < 0.0

    def test_restorative_phi_restoration_error_zero_pre(self):
        with pytest.raises(ValueError):
            restorative_justice_phi_restoration(0.0, 1.0)

    # --- mass_incarceration_social_cost ---

    def test_mass_incarceration_social_cost_zero_inmates(self):
        assert mass_incarceration_social_cost(1.0, 0, 3.0) == pytest.approx(0.0)

    def test_mass_incarceration_social_cost_formula(self):
        assert mass_incarceration_social_cost(1.0, 100, 2.0) == pytest.approx(200.0)

    def test_mass_incarceration_social_cost_error_multiplier_lt_one(self):
        with pytest.raises(ValueError):
            mass_incarceration_social_cost(1.0, 100, 0.5)

    def test_mass_incarceration_social_cost_error_negative_loss(self):
        with pytest.raises(ValueError):
            mass_incarceration_social_cost(-0.5, 100, 2.0)


# ===========================================================================
# TestReform
# ===========================================================================

class TestReform:
    # --- reform_activation_energy ---

    def test_reform_activation_energy_scales_with_B(self):
        e1 = reform_activation_energy(1.0, 100)
        e2 = reform_activation_energy(2.0, 100)
        assert e2 == pytest.approx(2.0 * e1)

    def test_reform_activation_energy_scales_with_sqrt_n(self):
        e1 = reform_activation_energy(1.0, 100)
        e4 = reform_activation_energy(1.0, 400)
        assert e4 == pytest.approx(2.0 * e1)

    def test_reform_activation_energy_zero_B(self):
        assert reform_activation_energy(0.0, 50) == pytest.approx(0.0)

    def test_reform_activation_energy_error_negative_B(self):
        with pytest.raises(ValueError):
            reform_activation_energy(-1.0, 10)

    def test_reform_activation_energy_error_zero_stakeholders(self):
        with pytest.raises(ValueError):
            reform_activation_energy(1.0, 0)

    # --- policy_phi_shift ---

    def test_policy_phi_shift_zero_decay(self):
        result = policy_phi_shift(1.0, 0.5, 0.0)
        assert result == pytest.approx(1.5)

    def test_policy_phi_shift_high_decay_small_shift(self):
        result = policy_phi_shift(1.0, 1.0, 100.0)
        assert result == pytest.approx(1.0, abs=1e-3)

    def test_policy_phi_shift_negative_delta_decreases_phi(self):
        result = policy_phi_shift(2.0, -1.0, 0.0)
        assert result == pytest.approx(1.0)

    def test_policy_phi_shift_error_zero_phi_current(self):
        with pytest.raises(ValueError):
            policy_phi_shift(0.0, 1.0, 0.0)

    def test_policy_phi_shift_error_negative_decay(self):
        with pytest.raises(ValueError):
            policy_phi_shift(1.0, 0.5, -0.1)

    # --- reform_coalition_strength ---

    def test_reform_coalition_strength_uniform(self):
        result = reform_coalition_strength(np.array([2.0, 2.0, 2.0]))
        assert result == pytest.approx(2.0, rel=1e-5)

    def test_reform_coalition_strength_scales_with_members(self):
        s_small = reform_coalition_strength(np.array([1.0, 1.0]))
        s_large = reform_coalition_strength(np.array([1.0, 1.0, 1.0, 1.0]))
        assert abs(s_large - s_small) < 0.1

    def test_reform_coalition_strength_error_empty(self):
        with pytest.raises(ValueError):
            reform_coalition_strength(np.array([]))

    def test_reform_coalition_strength_error_zero_phi(self):
        with pytest.raises(ValueError):
            reform_coalition_strength(np.array([1.0, 0.0, 1.0]))

    # --- public_defender_parity_gap ---

    def test_public_defender_parity_gap_equal_budgets(self):
        gap = public_defender_parity_gap(1e6, 1e6)
        assert gap == pytest.approx(0.0, abs=1e-9)

    def test_public_defender_parity_gap_defense_underfunded(self):
        gap = public_defender_parity_gap(500_000, 1_000_000)
        assert gap == pytest.approx(0.5, rel=1e-5)

    def test_public_defender_parity_gap_clipped_below_one(self):
        gap = public_defender_parity_gap(0.0, 1_000_000)
        assert gap < 1.0

    def test_public_defender_parity_gap_error_negative_budget(self):
        with pytest.raises(ValueError):
            public_defender_parity_gap(-100.0, 1_000_000)

    # --- transparency_score ---

    def test_transparency_score_all_public(self):
        assert transparency_score(100, 100) == pytest.approx(1.0, rel=1e-5)

    def test_transparency_score_none_public(self):
        assert transparency_score(0, 100) == pytest.approx(0.0, abs=1e-9)

    def test_transparency_score_half(self):
        assert transparency_score(50, 100) == pytest.approx(0.5, rel=1e-5)

    def test_transparency_score_error_public_exceeds_total(self):
        with pytest.raises(ValueError):
            transparency_score(101, 100)

    # --- drug_decrim_phi_gain ---

    def test_drug_decrim_phi_gain_full_decrim(self):
        gain = drug_decrim_phi_gain(3.0, 1.0, 1.0)
        assert gain == pytest.approx(2.0)

    def test_drug_decrim_phi_gain_zero_fraction(self):
        assert drug_decrim_phi_gain(3.0, 1.0, 0.0) == pytest.approx(0.0)

    def test_drug_decrim_phi_gain_negative_when_treatment_worse(self):
        gain = drug_decrim_phi_gain(0.5, 2.0, 1.0)
        assert gain < 0.0

    def test_drug_decrim_phi_gain_error_invalid_fraction(self):
        with pytest.raises(ValueError):
            drug_decrim_phi_gain(2.0, 1.0, 1.5)

    # --- police_accountability_reduction ---

    def test_police_accountability_reduction_no_accountability(self):
        assert police_accountability_reduction(0.8, 0.0) == pytest.approx(0.8)

    def test_police_accountability_reduction_full_accountability(self):
        assert police_accountability_reduction(0.8, 1.0) == pytest.approx(0.0)

    def test_police_accountability_reduction_half(self):
        assert police_accountability_reduction(1.0, 0.5) == pytest.approx(0.5)

    def test_police_accountability_reduction_error_invalid_factor(self):
        with pytest.raises(ValueError):
            police_accountability_reduction(1.0, 1.5)

    # --- reform_timeline ---

    def test_reform_timeline_zero_activation_energy(self):
        assert reform_timeline(0.0, 2.0, 5.0) == pytest.approx(0.0)

    def test_reform_timeline_larger_coalition_faster(self):
        t_small = reform_timeline(10.0, 1.0, 1.0)
        t_large = reform_timeline(10.0, 10.0, 1.0)
        assert t_large < t_small

    def test_reform_timeline_scales_with_time_constant(self):
        t1 = reform_timeline(5.0, 2.0, 1.0)
        t2 = reform_timeline(5.0, 2.0, 2.0)
        assert t2 == pytest.approx(2.0 * t1, rel=1e-5)

    def test_reform_timeline_error_zero_coalition(self):
        with pytest.raises(ValueError):
            reform_timeline(10.0, 0.0, 1.0)

    # --- recidivism_reduction_from_reform ---

    def test_recidivism_reduction_zero_gain(self):
        assert recidivism_reduction_from_reform(0.68, 0.0) == pytest.approx(0.0)

    def test_recidivism_reduction_large_gain_approaches_base(self):
        r = recidivism_reduction_from_reform(0.68, 100.0)
        assert r == pytest.approx(0.68, abs=1e-3)

    def test_recidivism_reduction_monotone(self):
        r1 = recidivism_reduction_from_reform(0.68, 1.0)
        r2 = recidivism_reduction_from_reform(0.68, 2.0)
        assert r2 > r1

    def test_recidivism_reduction_error_invalid_base(self):
        with pytest.raises(ValueError):
            recidivism_reduction_from_reform(0.0, 1.0)

    # --- justice_system_phi ---

    def test_justice_system_phi_equal_pillars(self):
        assert justice_system_phi(2.0, 2.0, 2.0, 2.0) == pytest.approx(2.0)

    def test_justice_system_phi_average(self):
        result = justice_system_phi(1.0, 2.0, 3.0, 4.0)
        assert result == pytest.approx(2.5)

    def test_justice_system_phi_all_zero(self):
        assert justice_system_phi(0.0, 0.0, 0.0, 0.0) == pytest.approx(0.0)

    def test_justice_system_phi_error_negative_pillar(self):
        with pytest.raises(ValueError):
            justice_system_phi(-0.1, 1.0, 1.0, 1.0)
