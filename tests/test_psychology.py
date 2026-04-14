# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_psychology.py
=========================
Unit tests for the src/psychology package — Pillar 24: Psychology.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import numpy as np
import pytest

from src.psychology.cognition import (
    cognitive_phi_load, perception_snr_phi, attention_bandwidth_phi,
    memory_phi_trace, reasoning_phi, problem_solving_phi, creativity_phi,
    metacognition_phi, executive_phi_function, cognitive_phi_bias,
)
from src.psychology.behavior import (
    motivation_phi_drive, reward_phi_signal, habit_phi_formation,
    decision_phi_threshold, risk_phi_tolerance, altruism_phi,
    aggression_phi_trigger, emotional_phi_regulation, behavioral_phi_flexibility,
    social_conformity_phi,
)
from src.psychology.social_psychology import (
    group_phi_cohesion, social_phi_influence, prejudice_phi,
    conformity_phi_pressure, leadership_phi, trust_phi_network,
    crowd_phi_dynamics, social_identity_phi, cooperation_phi, social_phi_entropy,
)


# ---------------------------------------------------------------------------
# cognition.py
# ---------------------------------------------------------------------------

class TestCognitivePhiLoad:
    def test_underload(self):
        assert cognitive_phi_load(3, 1.0, 10.0) == pytest.approx(0.3)

    def test_overload(self):
        assert cognitive_phi_load(20, 1.0, 10.0) > 1.0

    def test_raises_zero_capacity(self):
        with pytest.raises(ValueError):
            cognitive_phi_load(3, 1.0, 0.0)


class TestPerceptionSNRPhi:
    def test_positive(self):
        assert perception_snr_phi(2.0, 1.0) > 0.0

    def test_raises_negative_stimulus(self):
        with pytest.raises(ValueError):
            perception_snr_phi(-1.0, 1.0)


class TestAttentionBandwidthPhi:
    def test_full(self):
        assert attention_bandwidth_phi(1.0, 1.0) == pytest.approx(1.0)

    def test_half(self):
        assert attention_bandwidth_phi(0.5, 1.0) == pytest.approx(0.5)

    def test_clipped(self):
        assert attention_bandwidth_phi(2.0, 1.0) == pytest.approx(1.0)

    def test_raises_zero_total(self):
        with pytest.raises(ValueError):
            attention_bandwidth_phi(1.0, 0.0)


class TestMemoryPhiTrace:
    def test_t_zero(self):
        assert memory_phi_trace(1.0, 0.0) == pytest.approx(1.0)

    def test_decay(self):
        v = memory_phi_trace(1.0, 24.0, 24.0)
        assert v == pytest.approx(math.exp(-1.0), rel=1e-4)

    def test_raises_negative_tau(self):
        with pytest.raises(ValueError):
            memory_phi_trace(1.0, 1.0, 0.0)


class TestReasoningPhi:
    def test_positive_net(self):
        assert reasoning_phi(5.0, 2.0) == pytest.approx(3.0)

    def test_floored(self):
        assert reasoning_phi(1.0, 5.0) == pytest.approx(0.0)

    def test_raises_negative_premises(self):
        with pytest.raises(ValueError):
            reasoning_phi(-1.0, 0.0)


class TestProblemSolvingPhi:
    def test_easy_problem(self):
        v = problem_solving_phi(3.0, 1.0, 10.0)
        assert v > 0.0

    def test_raises_negative_repertoire(self):
        with pytest.raises(ValueError):
            problem_solving_phi(3.0, 1.0, -1.0)


class TestCreativityPhi:
    def test_unconstrained(self):
        assert creativity_phi(10.0, 2.0) == pytest.approx(8.0)

    def test_over_constrained(self):
        assert creativity_phi(1.0, 5.0) == pytest.approx(0.0)


class TestMetacognitionPhi:
    def test_perfect_accuracy(self):
        assert metacognition_phi(5.0, 5.0) == pytest.approx(1.0)

    def test_imperfect(self):
        v = metacognition_phi(5.0, 3.0)
        assert v < 1.0

    def test_clipped_to_zero(self):
        v = metacognition_phi(0.1, 100.0)
        assert v == pytest.approx(0.0)


class TestExecutivePhiFunction:
    def test_additive(self):
        assert executive_phi_function(2.0, 3.0, 4.0) == pytest.approx(9.0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            executive_phi_function(-1.0, 1.0, 1.0)


class TestCognitivePhiBias:
    def test_overestimate(self):
        assert cognitive_phi_bias(5.0, 7.0) == pytest.approx(2.0)

    def test_underestimate(self):
        assert cognitive_phi_bias(5.0, 3.0) == pytest.approx(-2.0)

    def test_no_bias(self):
        assert cognitive_phi_bias(5.0, 5.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# behavior.py
# ---------------------------------------------------------------------------

class TestMotivationPhiDrive:
    def test_unsatisfied(self):
        assert motivation_phi_drive(5.0, 2.0) == pytest.approx(3.0)

    def test_satisfied(self):
        assert motivation_phi_drive(2.0, 5.0) == pytest.approx(0.0)

    def test_raises_negative_need(self):
        with pytest.raises(ValueError):
            motivation_phi_drive(-1.0, 0.0)


class TestRewardPhiSignal:
    def test_positive_rpe(self):
        assert reward_phi_signal(2.0, 1.0) == pytest.approx(1.0)

    def test_negative_rpe(self):
        assert reward_phi_signal(1.0, 2.0) == pytest.approx(-1.0)

    def test_zero_rpe(self):
        assert reward_phi_signal(1.0, 1.0) == pytest.approx(0.0)


class TestHabitPhiFormation:
    def test_zero_reps(self):
        assert habit_phi_formation(1.0, 0) == pytest.approx(0.0)

    def test_asymptote(self):
        v = habit_phi_formation(1.0, 10000, 30.0)
        assert v == pytest.approx(1.0, abs=1e-3)

    def test_raises_negative_rep(self):
        with pytest.raises(ValueError):
            habit_phi_formation(1.0, -1)


class TestDecisionPhiThreshold:
    def test_above_threshold(self):
        assert decision_phi_threshold(2.0, 1.0, 0.0) is True

    def test_below_threshold(self):
        assert decision_phi_threshold(0.5, 1.0, 0.0) is False

    def test_raises_negative_noise(self):
        with pytest.raises(ValueError):
            decision_phi_threshold(2.0, 1.0, -0.1)


class TestRiskPhiTolerance:
    def test_risk_neutral(self):
        v = risk_phi_tolerance(1.0, 2.0, 0.5)
        assert v == pytest.approx(0.0)

    def test_risk_seeking(self):
        v = risk_phi_tolerance(1.0, 3.0, 0.5)
        assert v > 0.0

    def test_raises_bad_prob(self):
        with pytest.raises(ValueError):
            risk_phi_tolerance(1.0, 2.0, 1.5)


class TestAltruismPhi:
    def test_favoured(self):
        assert altruism_phi(1.0, 3.0, 0.5) == pytest.approx(0.5)

    def test_not_favoured(self):
        assert altruism_phi(5.0, 2.0, 0.5) < 0.0

    def test_raises_bad_coefficient(self):
        with pytest.raises(ValueError):
            altruism_phi(1.0, 3.0, 1.5)


class TestAggressionPhiTrigger:
    def test_inhibited(self):
        assert aggression_phi_trigger(1.0, 5.0, 1.0) == pytest.approx(0.0)

    def test_positive(self):
        v = aggression_phi_trigger(5.0, 1.0, 1.0)
        assert v > 0.0

    def test_raises_negative_noise(self):
        with pytest.raises(ValueError):
            aggression_phi_trigger(5.0, 1.0, -1.0)


class TestEmotionalPhiRegulation:
    def test_full_regulation(self):
        assert emotional_phi_regulation(1.0, 1.0) == pytest.approx(0.0)

    def test_no_regulation(self):
        assert emotional_phi_regulation(1.0, 0.0) == pytest.approx(1.0)

    def test_raises_bad_efficacy(self):
        with pytest.raises(ValueError):
            emotional_phi_regulation(1.0, 1.5)


class TestBehavioralPhiFlexibility:
    def test_zero_strategies(self):
        assert behavioral_phi_flexibility(0, 1.0) == pytest.approx(0.0)

    def test_scales(self):
        assert behavioral_phi_flexibility(5, 2.0) == pytest.approx(10.0)


class TestSocialConformityPhi:
    def test_pure_individual(self):
        v = social_conformity_phi(3.0, 7.0, 0.0)
        assert v == pytest.approx(3.0)

    def test_pure_group(self):
        v = social_conformity_phi(3.0, 7.0, 1.0)
        assert v == pytest.approx(7.0)

    def test_midpoint(self):
        v = social_conformity_phi(2.0, 4.0, 0.5)
        assert v == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# social_psychology.py
# ---------------------------------------------------------------------------

class TestGroupPhiCohesion:
    def test_uniform_high_cohesion(self):
        v = group_phi_cohesion([1.0, 1.0, 1.0])
        assert v > 10.0  # very high (std ≈ 0)

    def test_diverse_lower(self):
        v = group_phi_cohesion([1.0, 5.0, 10.0])
        assert v < group_phi_cohesion([3.0, 3.0, 3.0])

    def test_raises_empty(self):
        with pytest.raises(ValueError):
            group_phi_cohesion([])


class TestSocialPhiInfluence:
    def test_direct_full(self):
        assert social_phi_influence(1.0, 0) == pytest.approx(1.0)

    def test_decay_with_distance(self):
        v1 = social_phi_influence(1.0, 1, 0.5)
        v2 = social_phi_influence(1.0, 2, 0.5)
        assert v1 > v2

    def test_raises_negative_source(self):
        with pytest.raises(ValueError):
            social_phi_influence(-1.0, 1)


class TestPrejudicePhi:
    def test_equal_groups(self):
        assert prejudice_phi(5.0, 5.0) == pytest.approx(0.0)

    def test_biased(self):
        v = prejudice_phi(2.0, 8.0)
        assert v > 0.0

    def test_range(self):
        assert 0.0 <= prejudice_phi(0.0, 5.0) <= 1.0


class TestConformityPhiPressure:
    def test_zero_majority(self):
        assert conformity_phi_pressure(5.0, 7.0, 0) == pytest.approx(0.0)

    def test_larger_majority_more_pressure(self):
        p1 = conformity_phi_pressure(5.0, 7.0, 3)
        p2 = conformity_phi_pressure(5.0, 7.0, 5)
        assert p2 > p1


class TestLeadershipPhi:
    def test_zero_component_zero_leadership(self):
        assert leadership_phi(0.0, 5.0, 5.0) == pytest.approx(0.0)

    def test_balanced_higher(self):
        v_balanced = leadership_phi(3.0, 3.0, 3.0)
        assert v_balanced > 0.0


class TestTrustPhiNetwork:
    def test_pure_direct(self):
        assert trust_phi_network(4.0, 2.0, 0.0) == pytest.approx(4.0)

    def test_mixed(self):
        v = trust_phi_network(4.0, 2.0, 0.5)
        assert v == pytest.approx(3.0)

    def test_raises_bad_weight(self):
        with pytest.raises(ValueError):
            trust_phi_network(4.0, 2.0, 1.5)


class TestCrowdPhiDynamics:
    def test_single_person(self):
        v = crowd_phi_dynamics(1.0, 1, 1.5)
        assert v == pytest.approx(1.5)

    def test_scales_sqrt(self):
        v4 = crowd_phi_dynamics(1.0, 4, 1.0)
        v1 = crowd_phi_dynamics(1.0, 1, 1.0)
        assert v4 == pytest.approx(2.0 * v1)

    def test_raises_zero_crowd(self):
        with pytest.raises(ValueError):
            crowd_phi_dynamics(1.0, 0)


class TestSocialIdentityPhi:
    def test_pure_personal(self):
        assert social_identity_phi(3.0, 7.0, 0.0) == pytest.approx(7.0)

    def test_pure_group(self):
        assert social_identity_phi(3.0, 7.0, 1.0) == pytest.approx(3.0)


class TestCooperationPhi:
    def test_certain_cooperate(self):
        assert cooperation_phi(5.0, 8.0, 1.0) == pytest.approx(5.0)

    def test_certain_defect(self):
        assert cooperation_phi(5.0, 8.0, 0.0) == pytest.approx(8.0)

    def test_raises_bad_prob(self):
        with pytest.raises(ValueError):
            cooperation_phi(5.0, 8.0, 1.5)


class TestSocialPhiEntropy:
    def test_uniform(self):
        H = social_phi_entropy([1.0, 1.0, 1.0, 1.0])
        assert H == pytest.approx(math.log(4.0), rel=1e-3)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            social_phi_entropy([-1.0, 2.0])
