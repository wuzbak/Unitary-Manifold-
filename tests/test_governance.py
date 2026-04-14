# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_governance.py
=========================
Unit tests for the src/governance package — Pillar 19.

Covers:
  - social_contract.py : social_phi_balance, contract_stability,
                         inequality_index, corruption_phi_drain,
                         free_rider_fraction, legitimacy_score,
                         redistribution_effectiveness, public_goods_phi,
                         trust_decay, intergenerational_phi_transfer
  - democracy.py       : condorcet_phi, voter_phi_density,
                         democratic_legitimacy, authoritarian_fragility,
                         misinformation_phi_noise, gerrymandering_index,
                         polarisation_index, campaign_finance_distortion,
                         ranked_choice_phi_gain, press_freedom_phi
  - stability.py       : lyapunov_stability, checks_balance_score,
                         democratic_backsliding_rate, institutional_resilience,
                         rule_of_law_index, term_limit_benefit, coup_risk,
                         economic_pluralism_index, international_cooperation_phi,
                         governance_quality_score
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math

import numpy as np
import pytest

from src.governance.social_contract import (
    social_phi_balance,
    contract_stability,
    inequality_index,
    corruption_phi_drain,
    free_rider_fraction,
    legitimacy_score,
    redistribution_effectiveness,
    public_goods_phi,
    trust_decay,
    intergenerational_phi_transfer,
)
from src.governance.democracy import (
    condorcet_phi,
    voter_phi_density,
    democratic_legitimacy,
    authoritarian_fragility,
    misinformation_phi_noise,
    gerrymandering_index,
    polarisation_index,
    campaign_finance_distortion,
    ranked_choice_phi_gain,
    press_freedom_phi,
)
from src.governance.stability import (
    lyapunov_stability,
    checks_balance_score,
    democratic_backsliding_rate,
    institutional_resilience,
    rule_of_law_index,
    term_limit_benefit,
    coup_risk,
    economic_pluralism_index,
    international_cooperation_phi,
    governance_quality_score,
)


# ===========================================================================
# TestSocialContract
# ===========================================================================

class TestSocialContract:
    # --- social_phi_balance ---

    def test_balance_positive_when_returns_exceed_contributions(self):
        assert social_phi_balance([1.0, 1.0], [2.0, 2.0]) == pytest.approx(2.0)

    def test_balance_zero_when_equal(self):
        assert social_phi_balance([3.0, 2.0], [3.0, 2.0]) == pytest.approx(0.0)

    def test_balance_negative_when_contributions_exceed_returns(self):
        assert social_phi_balance([5.0], [2.0]) == pytest.approx(-3.0)

    def test_balance_raises_on_empty_contributions(self):
        with pytest.raises(ValueError):
            social_phi_balance([], [1.0])

    def test_balance_raises_on_empty_returns(self):
        with pytest.raises(ValueError):
            social_phi_balance([1.0], [])

    # --- contract_stability ---

    def test_stable_when_at_minimum(self):
        assert contract_stability(5.0, 5.0) is True

    def test_stable_when_above_minimum(self):
        assert contract_stability(10.0, 5.0) is True

    def test_unstable_when_below_minimum(self):
        assert contract_stability(3.0, 5.0) is False

    def test_stability_raises_negative_collective(self):
        with pytest.raises(ValueError):
            contract_stability(-1.0, 1.0)

    def test_stability_raises_negative_minimum(self):
        with pytest.raises(ValueError):
            contract_stability(1.0, -1.0)

    # --- inequality_index ---

    def test_equality_gives_zero(self):
        assert inequality_index([2.0, 2.0, 2.0]) == pytest.approx(0.0)

    def test_inequality_positive(self):
        assert inequality_index([1.0, 10.0]) > 0.0

    def test_inequality_monotone_with_spread(self):
        i_low = inequality_index([1.0, 2.0, 3.0])
        i_high = inequality_index([1.0, 5.0, 9.0])
        assert i_high > i_low

    def test_inequality_raises_empty(self):
        with pytest.raises(ValueError):
            inequality_index([])

    # --- corruption_phi_drain ---

    def test_drain_zero_when_B_zero(self):
        assert corruption_phi_drain(0.0, 10.0, 0.5) == pytest.approx(0.0)

    def test_drain_zero_when_phi_zero(self):
        assert corruption_phi_drain(1.0, 0.0, 0.5) == pytest.approx(0.0)

    def test_drain_formula(self):
        assert corruption_phi_drain(2.0, 5.0, 0.1) == pytest.approx(1.0)

    def test_drain_raises_negative_B(self):
        with pytest.raises(ValueError):
            corruption_phi_drain(-1.0, 5.0, 0.1)

    def test_drain_raises_negative_phi(self):
        with pytest.raises(ValueError):
            corruption_phi_drain(1.0, -1.0, 0.1)

    # --- free_rider_fraction ---

    def test_no_free_rider_when_contributed_equals_taken(self):
        assert free_rider_fraction(3.0, 3.0) == pytest.approx(0.0, abs=1e-10)

    def test_full_free_rider_when_contributed_zero(self):
        assert free_rider_fraction(5.0, 0.0) == pytest.approx(1.0, abs=1e-10)

    def test_partial_free_rider(self):
        fr = free_rider_fraction(4.0, 2.0)
        assert 0.0 < fr < 1.0

    def test_free_rider_non_negative(self):
        assert free_rider_fraction(1.0, 10.0) == pytest.approx(0.0)

    # --- legitimacy_score ---

    def test_full_legitimacy_when_fairness_equals_required(self):
        assert legitimacy_score(5.0, 5.0) == pytest.approx(1.0, abs=1e-6)

    def test_legitimacy_capped_at_one(self):
        assert legitimacy_score(10.0, 5.0) == pytest.approx(1.0)

    def test_legitimacy_below_one_when_fairness_low(self):
        assert legitimacy_score(2.0, 5.0) < 1.0

    def test_legitimacy_zero_required_gives_one(self):
        assert legitimacy_score(1.0, 0.0) == pytest.approx(1.0)

    # --- redistribution_effectiveness ---

    def test_effectiveness_positive_when_phi_increases(self):
        assert redistribution_effectiveness(5.0, 8.0, 3.0) > 0.0

    def test_effectiveness_formula(self):
        assert redistribution_effectiveness(4.0, 7.0, 3.0) == pytest.approx(1.0, abs=1e-6)

    def test_effectiveness_raises_negative_transferred(self):
        with pytest.raises(ValueError):
            redistribution_effectiveness(1.0, 2.0, -1.0)

    # --- public_goods_phi ---

    def test_zero_tax_gives_zero_goods(self):
        assert public_goods_phi(0.0, 0.9) == pytest.approx(0.0)

    def test_efficiency_one_returns_full_tax(self):
        assert public_goods_phi(100.0, 1.0) == pytest.approx(100.0)

    def test_efficiency_clipped_above_one(self):
        assert public_goods_phi(100.0, 1.5) == pytest.approx(100.0)

    def test_public_goods_raises_negative_tax(self):
        with pytest.raises(ValueError):
            public_goods_phi(-10.0, 0.8)

    # --- trust_decay ---

    def test_no_scandal_no_decay(self):
        assert trust_decay(10.0, 0.0, 5.0, 1.0) == pytest.approx(10.0)

    def test_trust_decays_exponentially(self):
        phi1 = trust_decay(10.0, 1.0, 1.0, 1.0)
        phi2 = trust_decay(10.0, 1.0, 2.0, 1.0)
        assert phi2 == pytest.approx(phi1 ** 2 / 10.0, rel=1e-6)

    def test_trust_raises_negative_tau(self):
        with pytest.raises(ValueError):
            trust_decay(5.0, 1.0, 1.0, -1.0)

    def test_trust_raises_zero_tau(self):
        with pytest.raises(ValueError):
            trust_decay(5.0, 1.0, 1.0, 0.0)

    # --- intergenerational_phi_transfer ---

    def test_zero_investment_gives_zero_transfer(self):
        assert intergenerational_phi_transfer(100.0, 0.0, 0.05) == pytest.approx(0.0)

    def test_larger_investment_fraction_gives_more(self):
        low = intergenerational_phi_transfer(100.0, 0.1, 0.05)
        high = intergenerational_phi_transfer(100.0, 0.5, 0.05)
        assert high > low

    def test_raises_negative_phi_current(self):
        with pytest.raises(ValueError):
            intergenerational_phi_transfer(-10.0, 0.3, 0.05)


# ===========================================================================
# TestDemocracy
# ===========================================================================

class TestDemocracy:
    # --- condorcet_phi ---

    def test_accuracy_half_gives_half(self):
        result = condorcet_phi(100, 0.5)
        assert result == pytest.approx(0.5, abs=1e-6)

    def test_accuracy_above_half_gives_above_half(self):
        assert condorcet_phi(100, 0.6) > 0.5

    def test_accuracy_below_half_gives_below_half(self):
        assert condorcet_phi(100, 0.4) < 0.5

    def test_more_voters_improves_accuracy(self):
        p_small = condorcet_phi(10, 0.6)
        p_large = condorcet_phi(1000, 0.6)
        assert p_large > p_small

    def test_raises_zero_voters(self):
        with pytest.raises(ValueError):
            condorcet_phi(0, 0.6)

    def test_raises_accuracy_zero(self):
        with pytest.raises(ValueError):
            condorcet_phi(100, 0.0)

    def test_raises_accuracy_one(self):
        with pytest.raises(ValueError):
            condorcet_phi(100, 1.0)

    def test_uses_math_erf(self):
        n, p = 25, 0.7
        expected = 0.5 + 0.5 * math.erf((p - 0.5) * math.sqrt(n))
        assert condorcet_phi(n, p) == pytest.approx(expected)

    # --- voter_phi_density ---

    def test_full_registration_gives_one(self):
        assert voter_phi_density(1000.0, 1000.0) == pytest.approx(1.0, abs=1e-6)

    def test_density_clipped_at_one(self):
        assert voter_phi_density(1200.0, 1000.0) == pytest.approx(1.0)

    def test_zero_registered_gives_zero(self):
        assert voter_phi_density(0.0, 1000.0) == pytest.approx(0.0)

    def test_raises_negative_registered(self):
        with pytest.raises(ValueError):
            voter_phi_density(-10.0, 100.0)

    # --- democratic_legitimacy ---

    def test_perfect_conditions_near_maximum(self):
        # margin=0.5 (maximally competitive) → factor (1-|0.5-0.5|)=1 → legitimacy=1
        result = democratic_legitimacy(1.0, 0.5, 1.0)
        assert result == pytest.approx(1.0)

    def test_zero_turnout_gives_zero(self):
        assert democratic_legitimacy(0.0, 0.5, 1.0) == pytest.approx(0.0)

    def test_raises_turnout_above_one(self):
        with pytest.raises(ValueError):
            democratic_legitimacy(1.2, 0.5, 1.0)

    def test_raises_negative_press_freedom(self):
        with pytest.raises(ValueError):
            democratic_legitimacy(0.8, 0.5, -0.1)

    # --- authoritarian_fragility ---

    def test_zero_concentration_gives_zero(self):
        assert authoritarian_fragility(0.0, 5.0) == pytest.approx(0.0)

    def test_fragility_increases_with_concentration(self):
        f_low = authoritarian_fragility(1.0, 5.0)
        f_high = authoritarian_fragility(3.0, 5.0)
        assert f_high > f_low

    def test_fragility_decreases_with_institutions(self):
        f_few = authoritarian_fragility(2.0, 1.0)
        f_many = authoritarian_fragility(2.0, 10.0)
        assert f_many < f_few

    # --- misinformation_phi_noise ---

    def test_zero_B_gives_zero_noise(self):
        assert misinformation_phi_noise(0.0, 1000.0, 0.5) == pytest.approx(0.0)

    def test_full_correction_gives_zero_noise(self):
        assert misinformation_phi_noise(1.0, 1000.0, 1.0) == pytest.approx(0.0)

    def test_no_correction_gives_full_noise(self):
        assert misinformation_phi_noise(2.0, 500.0, 0.0) == pytest.approx(1000.0)

    def test_raises_negative_B(self):
        with pytest.raises(ValueError):
            misinformation_phi_noise(-1.0, 100.0, 0.5)

    # --- gerrymandering_index ---

    def test_proportional_gives_zero(self):
        assert gerrymandering_index(0.5, 0.5) == pytest.approx(0.0)

    def test_extreme_gerrymandering(self):
        assert gerrymandering_index(0.5, 0.9) == pytest.approx(0.4)

    def test_raises_votes_out_of_range(self):
        with pytest.raises(ValueError):
            gerrymandering_index(1.2, 0.5)

    # --- polarisation_index ---

    def test_equal_poles_give_zero(self):
        assert polarisation_index(5.0, 5.0) == pytest.approx(0.0, abs=1e-6)

    def test_large_difference_gives_near_one(self):
        pi = polarisation_index(100.0, 0.001)
        assert pi > 0.99

    def test_raises_negative_phi(self):
        with pytest.raises(ValueError):
            polarisation_index(-1.0, 5.0)

    # --- campaign_finance_distortion ---

    def test_zero_money_gives_zero(self):
        assert campaign_finance_distortion(0.0, 5.0) == pytest.approx(0.0)

    def test_distortion_increases_with_money(self):
        d_low = campaign_finance_distortion(1.0, 5.0)
        d_high = campaign_finance_distortion(10.0, 5.0)
        assert d_high > d_low

    def test_raises_negative_B_money(self):
        with pytest.raises(ValueError):
            campaign_finance_distortion(-1.0, 5.0)

    # --- ranked_choice_phi_gain ---

    def test_zero_rounds_gives_zero(self):
        assert ranked_choice_phi_gain(5, 0) == pytest.approx(0.0)

    def test_gain_increases_with_rounds(self):
        g1 = ranked_choice_phi_gain(5, 1)
        g3 = ranked_choice_phi_gain(5, 3)
        assert g3 > g1

    def test_raises_zero_candidates(self):
        with pytest.raises(ValueError):
            ranked_choice_phi_gain(0, 2)

    # --- press_freedom_phi ---

    def test_zero_censorship_returns_outlet_count(self):
        assert press_freedom_phi(10.0, 0.0) == pytest.approx(10.0)

    def test_high_censorship_suppresses_phi(self):
        phi = press_freedom_phi(10.0, 10.0)
        assert phi < 0.001

    def test_raises_negative_censorship(self):
        with pytest.raises(ValueError):
            press_freedom_phi(5.0, -1.0)


# ===========================================================================
# TestStability
# ===========================================================================

class TestStability:
    # --- lyapunov_stability ---

    def test_at_optimum_gives_zero(self):
        assert lyapunov_stability(3.0, 3.0) == pytest.approx(0.0)

    def test_deviation_gives_positive(self):
        assert lyapunov_stability(5.0, 3.0) > 0.0

    def test_symmetry(self):
        assert lyapunov_stability(5.0, 3.0) == pytest.approx(lyapunov_stability(3.0, 5.0))

    def test_formula_explicit(self):
        assert lyapunov_stability(7.0, 4.0) == pytest.approx(9.0)

    # --- checks_balance_score ---

    def test_equal_branches_give_one(self):
        assert checks_balance_score(5.0, 5.0, 5.0) == pytest.approx(1.0, abs=1e-6)

    def test_unequal_branches_below_one(self):
        assert checks_balance_score(10.0, 1.0, 1.0) < 1.0

    def test_score_clipped_at_zero(self):
        result = checks_balance_score(100.0, 0.0, 0.0)
        assert result >= 0.0

    def test_raises_negative_branch(self):
        with pytest.raises(ValueError):
            checks_balance_score(-1.0, 5.0, 5.0)

    # --- democratic_backsliding_rate ---

    def test_no_change_gives_zero(self):
        assert democratic_backsliding_rate(5.0, 5.0, 1.0) == pytest.approx(0.0)

    def test_positive_rate_when_backsliding(self):
        assert democratic_backsliding_rate(8.0, 5.0, 3.0) > 0.0

    def test_negative_rate_when_improving(self):
        assert democratic_backsliding_rate(3.0, 7.0, 2.0) < 0.0

    def test_raises_negative_dt(self):
        with pytest.raises(ValueError):
            democratic_backsliding_rate(5.0, 4.0, -1.0)

    # --- institutional_resilience ---

    def test_zero_civil_society_gives_zero(self):
        assert institutional_resilience(5.0, 0.0) == pytest.approx(0.0)

    def test_resilience_scales_linearly(self):
        r1 = institutional_resilience(3.0, 2.0)
        r2 = institutional_resilience(6.0, 2.0)
        assert r2 == pytest.approx(2.0 * r1)

    def test_raises_negative_veto_players(self):
        with pytest.raises(ValueError):
            institutional_resilience(-1.0, 2.0)

    # --- rule_of_law_index ---

    def test_zero_variance_gives_one(self):
        assert rule_of_law_index(0.0, 5.0) == pytest.approx(1.0)

    def test_positive_variance_reduces_rli(self):
        assert rule_of_law_index(4.0, 2.0) < 1.0

    def test_raises_negative_variance(self):
        with pytest.raises(ValueError):
            rule_of_law_index(-1.0, 2.0)

    def test_raises_negative_mean(self):
        with pytest.raises(ValueError):
            rule_of_law_index(1.0, -1.0)

    # --- term_limit_benefit ---

    def test_zero_terms_gives_zero(self):
        assert term_limit_benefit(2.0, 0.0) == pytest.approx(0.0)

    def test_benefit_scales_with_terms(self):
        b1 = term_limit_benefit(2.0, 3.0)
        b2 = term_limit_benefit(2.0, 6.0)
        assert b2 == pytest.approx(2.0 * b1)

    def test_raises_negative_advantage(self):
        with pytest.raises(ValueError):
            term_limit_benefit(-1.0, 3.0)

    # --- coup_risk ---

    def test_zero_military_gives_zero(self):
        assert coup_risk(0.0, 5.0) == pytest.approx(0.0)

    def test_risk_clipped_at_one(self):
        assert coup_risk(1000.0, 0.0) == pytest.approx(1.0)

    def test_risk_increases_with_military_autonomy(self):
        r_low = coup_risk(1.0, 5.0)
        r_high = coup_risk(4.0, 5.0)
        assert r_high > r_low

    def test_raises_negative_military(self):
        with pytest.raises(ValueError):
            coup_risk(-1.0, 5.0)

    # --- economic_pluralism_index ---

    def test_equal_distribution_gives_one(self):
        assert economic_pluralism_index([3.0, 3.0, 3.0]) == pytest.approx(1.0, abs=1e-6)

    def test_unequal_gives_below_one(self):
        assert economic_pluralism_index([1.0, 100.0]) < 1.0

    def test_epi_non_negative(self):
        assert economic_pluralism_index([1.0, 1000.0]) >= 0.0

    def test_raises_empty(self):
        with pytest.raises(ValueError):
            economic_pluralism_index([])

    # --- international_cooperation_phi ---

    def test_zero_agreements_gives_zero(self):
        assert international_cooperation_phi(0.0, 2.0) == pytest.approx(0.0)

    def test_scales_linearly_with_agreements(self):
        p1 = international_cooperation_phi(3.0, 2.0)
        p2 = international_cooperation_phi(6.0, 2.0)
        assert p2 == pytest.approx(2.0 * p1)

    def test_raises_negative_agreements(self):
        with pytest.raises(ValueError):
            international_cooperation_phi(-1.0, 2.0)

    # --- governance_quality_score ---

    def test_all_ones_gives_one(self):
        assert governance_quality_score(1.0, 1.0, 1.0, 1.0, 1.0) == pytest.approx(1.0)

    def test_all_zeros_gives_zero(self):
        assert governance_quality_score(0.0, 0.0, 0.0, 0.0, 0.0) == pytest.approx(0.0)

    def test_formula_explicit(self):
        assert governance_quality_score(0.8, 0.6, 0.7, 0.9, 0.5) == pytest.approx(
            (0.8 + 0.6 + 0.7 + 0.9 + 0.5) / 5.0
        )

    def test_monotone_in_each_dimension(self):
        base = governance_quality_score(0.5, 0.5, 0.5, 0.5, 0.5)
        higher = governance_quality_score(0.9, 0.5, 0.5, 0.5, 0.5)
        assert higher > base
