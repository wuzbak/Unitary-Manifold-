# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 795 — BIREFRINGENCE_ACT_PLANCK_DR6_SIGNAL_HARDENING
~50 tests covering birefringence status upgrade, window containment,
Bayes factor, and discriminant conditions.
"""
import math
import pytest
from src.core.pillar795_birefringence_act_planck_dr6 import (
    BETA_LOW_DEG,
    BETA_HIGH_DEG,
    BETA_GAP_LO,
    BETA_GAP_HI,
    BETA_ADMISSIBLE_LO,
    BETA_ADMISSIBLE_HI,
    JOINT_BETA_DEG,
    JOINT_SIGMA_DEG,
    JOINT_SIGNIFICANCE,
    ACT_DR6_BETA_DEG,
    ACT_DR6_SIGMA_DEG,
    PRIOR_BETA_DEG,
    PRIOR_SIGNIFICANCE,
    PILLAR_795_GATE,
    tension_from_prediction,
    window_containment,
    act_planck_joint_consistency,
    act_dr6_only_consistency,
    posterior_probability_low_branch,
    posterior_probability_high_branch,
    bayes_factor_low_vs_high,
    discriminant_condition_litebird,
    discriminant_condition_simons_obs,
    birefringence_status_report,
    pillar795_summary,
    PILLAR_795_SUMMARY,
)


class TestConstants:
    def test_gate(self):
        assert PILLAR_795_GATE == "BIREFRINGENCE_FIRST_DETECTION_CANDIDATE"

    def test_beta_low_deg(self):
        assert abs(BETA_LOW_DEG - 0.273) < 1e-6

    def test_beta_high_deg(self):
        assert abs(BETA_HIGH_DEG - 0.331) < 1e-6

    def test_gap_ordering(self):
        assert BETA_LOW_DEG < BETA_GAP_LO
        assert BETA_GAP_LO < BETA_GAP_HI
        assert BETA_GAP_HI < BETA_HIGH_DEG

    def test_admissible_window(self):
        assert BETA_ADMISSIBLE_LO < BETA_LOW_DEG
        assert BETA_HIGH_DEG < BETA_ADMISSIBLE_HI

    def test_joint_significance(self):
        assert JOINT_SIGNIFICANCE >= 4.5

    def test_joint_beta(self):
        assert abs(JOINT_BETA_DEG - 0.277) < 1e-6

    def test_prior_significance(self):
        assert PRIOR_SIGNIFICANCE >= 3.0


class TestTensionCalculation:
    def test_tension_low_branch_nearly_zero(self):
        t = tension_from_prediction(JOINT_BETA_DEG, JOINT_SIGMA_DEG, BETA_LOW_DEG)
        assert t < 1.0, f"Expected <1σ, got {t:.3f}σ"

    def test_tension_low_branch_very_small(self):
        t = tension_from_prediction(JOINT_BETA_DEG, JOINT_SIGMA_DEG, BETA_LOW_DEG)
        assert t < 0.2, f"Expected <0.2σ, got {t:.3f}σ"

    def test_tension_high_branch_larger(self):
        t_low = tension_from_prediction(JOINT_BETA_DEG, JOINT_SIGMA_DEG, BETA_LOW_DEG)
        t_high = tension_from_prediction(JOINT_BETA_DEG, JOINT_SIGMA_DEG, BETA_HIGH_DEG)
        assert t_high > t_low

    def test_tension_zero_when_equal(self):
        t = tension_from_prediction(BETA_LOW_DEG, JOINT_SIGMA_DEG, BETA_LOW_DEG)
        assert t == 0.0

    def test_tension_positive(self):
        t = tension_from_prediction(0.3, 0.05, 0.25)
        assert t > 0.0

    def test_act_dr6_tension_low(self):
        t = tension_from_prediction(ACT_DR6_BETA_DEG, ACT_DR6_SIGMA_DEG, BETA_LOW_DEG)
        assert t < 3.0


class TestWindowContainment:
    def test_joint_low_branch_within_1sigma(self):
        c = window_containment(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
        assert c['low_branch_within_1sigma']

    def test_joint_admissible(self):
        c = window_containment(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
        assert c['admissible']

    def test_joint_not_in_gap(self):
        c = window_containment(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
        assert not c['gap_occupied']

    def test_inadmissible_below(self):
        c = window_containment(0.10, 0.01)
        assert not c['admissible']

    def test_inadmissible_above(self):
        c = window_containment(0.50, 0.01)
        assert not c['admissible']

    def test_gap_occupied_when_in_gap(self):
        c = window_containment(0.300, 0.001)
        assert c['gap_occupied']

    def test_returns_tensions(self):
        c = window_containment(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
        assert 'tension_low_branch' in c
        assert 'tension_high_branch' in c


class TestConsistencyFunctions:
    def test_joint_consistency_gate(self):
        r = act_planck_joint_consistency()
        assert r['status'] == PILLAR_795_GATE

    def test_joint_consistency_beta(self):
        r = act_planck_joint_consistency()
        assert abs(r['beta_deg'] - JOINT_BETA_DEG) < 1e-9

    def test_act_dr6_consistency_keys(self):
        r = act_dr6_only_consistency()
        assert 'tension_low_branch' in r
        assert 'admissible' in r

    def test_act_dr6_admissible(self):
        r = act_dr6_only_consistency()
        # ACT DR6 alone at 0.215° is slightly below the canonical 0.22° window
        # but consistent with measurement uncertainty; the function uses 0.20° lower bound
        assert r['admissible']


class TestPosteriorAndBayes:
    def test_posterior_low_max_at_prediction(self):
        p = posterior_probability_low_branch(BETA_LOW_DEG, JOINT_SIGMA_DEG)
        assert abs(p - 1.0) < 1e-6

    def test_posterior_high_max_at_prediction(self):
        p = posterior_probability_high_branch(BETA_HIGH_DEG, JOINT_SIGMA_DEG)
        assert abs(p - 1.0) < 1e-6

    def test_posterior_low_at_joint_obs_near_1(self):
        p = posterior_probability_low_branch(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
        assert p > 0.99   # 0.07σ → near unity

    def test_bayes_factor_favours_low(self):
        bf = bayes_factor_low_vs_high(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
        assert bf > 1.0

    def test_bayes_factor_strongly_favours_low(self):
        bf = bayes_factor_low_vs_high(JOINT_BETA_DEG, JOINT_SIGMA_DEG)
        assert bf > 1.5   # meaningfully more probable at low branch

    def test_bayes_factor_positive(self):
        bf = bayes_factor_low_vs_high(0.280, 0.050)
        assert bf > 0.0


class TestDiscriminantConditions:
    def test_litebird_resolves_branches(self):
        d = discriminant_condition_litebird()
        assert d['will_resolve_branches']

    def test_litebird_sigma_small(self):
        d = discriminant_condition_litebird()
        assert d['projected_sigma_deg'] < 0.02

    def test_litebird_has_falsification(self):
        d = discriminant_condition_litebird()
        assert 'falsification_condition' in d

    def test_litebird_has_confirmation(self):
        d = discriminant_condition_litebird()
        assert 'confirmation_condition' in d

    def test_simons_obs_keys(self):
        d = discriminant_condition_simons_obs()
        assert 'experiment' in d
        assert 'falsification_condition' in d

    def test_simons_obs_year_near_term(self):
        d = discriminant_condition_simons_obs()
        assert d['decision_year'] < 2030


class TestStatusReport:
    def test_report_gate(self):
        r = birefringence_status_report()
        assert r.gate == PILLAR_795_GATE

    def test_report_previous_hint(self):
        r = birefringence_status_report()
        assert 'HINT' in r.previous_status

    def test_report_gap_not_occupied(self):
        r = birefringence_status_report()
        assert r.gap_not_occupied

    def test_report_admissible(self):
        r = birefringence_status_report()
        assert r.admissible

    def test_report_litebird_resolves(self):
        r = birefringence_status_report()
        assert r.litebird_resolves

    def test_report_honest_caveat_present(self):
        r = birefringence_status_report()
        assert len(r.honest_caveat) > 50

    def test_report_caveat_mentions_litebird(self):
        r = birefringence_status_report()
        assert 'LiteBIRD' in r.honest_caveat


class TestSummary:
    def test_summary_pillar(self):
        s = pillar795_summary()
        assert s['pillar'] == 795

    def test_summary_gate(self):
        s = pillar795_summary()
        assert s['gate'] == PILLAR_795_GATE

    def test_summary_has_measurements(self):
        s = pillar795_summary()
        assert 'measurements' in s

    def test_summary_joint_measurement(self):
        s = pillar795_summary()
        assert 'act_planck_joint' in s['measurements']

    def test_summary_has_future(self):
        s = pillar795_summary()
        assert 'future_discriminants' in s

    def test_summary_alias(self):
        s = PILLAR_795_SUMMARY()
        assert s['pillar'] == 795
