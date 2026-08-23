# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 796 — JUNO_DM21_PRECISION_UPDATE
~50 tests covering JUNO measurement ingestion, G4 tension routing,
NH consistency, and Year 2 forward model.
"""
import pytest
from src.core.pillar796_juno_dm21_precision_update import (
    DM21_UM_PREDICTION_EV2,
    DM21_PDG_PRE_JUNO_EV2,
    DM21_PDG_SIGMA_PRE_JUNO,
    JUNO_PRECISION_IMPROVEMENT,
    JUNO_DM21_SIGMA_POST,
    JUNO_DM21_CENTRAL_EV2,
    JUNO_SIN2_THETA12,
    JUNO_SIN2_THETA12_SIGMA,
    JUNO_NH_DELTA_CHI2,
    TENSION_PRE_JUNO,
    GATE_APPROACHING_FLOOR,
    GATE_STABLE_UPPER,
    GATE_TYPE_A_RISK,
    PILLAR_796_GATE,
    tension_with_juno,
    route_tension,
    juno_g4_update,
    scenario_analysis,
    nh_ordering_consistency,
    sin2_theta12_consistency,
    forward_model_juno_year2,
    pillar796_summary,
    PILLAR_796_SUMMARY,
)


class TestConstants:
    def test_gate(self):
        assert PILLAR_796_GATE == "JUNO_G4_TENSION_UPDATE"

    def test_um_prediction_order_of_magnitude(self):
        assert 7.0e-5 < DM21_UM_PREDICTION_EV2 < 8.0e-5

    def test_pdg_pre_juno_order_of_magnitude(self):
        assert 7.0e-5 < DM21_PDG_PRE_JUNO_EV2 < 8.0e-5

    def test_pre_juno_tension_positive(self):
        assert TENSION_PRE_JUNO > 0.0

    def test_pre_juno_tension_magnitude(self):
        assert 0.5 < TENSION_PRE_JUNO < 2.0

    def test_juno_improvement_positive(self):
        assert JUNO_PRECISION_IMPROVEMENT > 1.0

    def test_juno_sigma_post_smaller(self):
        assert JUNO_DM21_SIGMA_POST < DM21_PDG_SIGMA_PRE_JUNO

    def test_gate_thresholds_ordered(self):
        assert GATE_APPROACHING_FLOOR < GATE_STABLE_UPPER < GATE_TYPE_A_RISK


class TestTensionCalculation:
    def test_tension_central_value_increases(self):
        t_post = tension_with_juno(JUNO_DM21_CENTRAL_EV2, JUNO_DM21_SIGMA_POST)
        assert t_post > TENSION_PRE_JUNO   # tighter σ increases tension

    def test_tension_positive(self):
        t = tension_with_juno()
        assert t > 0.0

    def test_tension_custom_central(self):
        t = tension_with_juno(DM21_UM_PREDICTION_EV2, JUNO_DM21_SIGMA_POST)
        assert t == 0.0   # perfect agreement

    def test_tension_formula(self):
        t = tension_with_juno(7.60e-5, 1.1e-6)
        expected = abs(7.60e-5 - DM21_UM_PREDICTION_EV2) / 1.1e-6
        assert abs(t - expected) < 1e-10


class TestRouting:
    def test_approaching_floor_route(self):
        assert route_tension(0.5) == "JUNO_G4_APPROACHING_TYPE_B_FLOOR"

    def test_stable_route(self):
        assert route_tension(1.2) == "JUNO_G4_TENSION_STABLE"

    def test_elevated_route(self):
        assert route_tension(2.0) == "JUNO_G4_TENSION_ELEVATED"

    def test_type_a_risk_route(self):
        assert route_tension(3.0) == "JUNO_G4_TYPE_A_RISK"

    def test_boundary_approaching(self):
        assert route_tension(GATE_APPROACHING_FLOOR - 0.01) == "JUNO_G4_APPROACHING_TYPE_B_FLOOR"

    def test_boundary_stable_upper(self):
        assert route_tension(GATE_STABLE_UPPER + 0.01) == "JUNO_G4_TENSION_ELEVATED"


class TestG4Update:
    def test_g4_update_gate(self):
        r = juno_g4_update()
        assert r['gate'] == PILLAR_796_GATE

    def test_g4_update_prior_tension(self):
        r = juno_g4_update()
        assert abs(r['g4_prior_tension_sigma'] - TENSION_PRE_JUNO) < 1e-10

    def test_g4_update_tension_positive(self):
        r = juno_g4_update()
        assert r['g4_post_juno_tension_sigma'] > 0.0

    def test_g4_update_routing_key(self):
        r = juno_g4_update()
        assert 'g4_tension_routing' in r

    def test_g4_update_um_prediction(self):
        r = juno_g4_update()
        assert abs(r['um_prediction_ev2'] - DM21_UM_PREDICTION_EV2) < 1e-15


class TestScenarioAnalysis:
    def test_three_scenarios(self):
        s = scenario_analysis()
        assert len(s) == 3

    def test_scenario_keys(self):
        s = scenario_analysis()
        for key in ('A_juno_central_same_as_pdg', 'B_juno_moves_toward_um', 'C_juno_moves_away_from_um'):
            assert key in s

    def test_scenario_b_lower_tension(self):
        s = scenario_analysis()
        t_a = s['A_juno_central_same_as_pdg']['tension_sigma']
        t_b = s['B_juno_moves_toward_um']['tension_sigma']
        assert t_b < t_a   # moving toward UM reduces tension

    def test_scenario_c_higher_tension(self):
        s = scenario_analysis()
        t_a = s['A_juno_central_same_as_pdg']['tension_sigma']
        t_c = s['C_juno_moves_away_from_um']['tension_sigma']
        assert t_c > t_a   # moving away increases tension

    def test_scenario_routing_present(self):
        s = scenario_analysis()
        for v in s.values():
            assert 'routing' in v


class TestNHOrdering:
    def test_nh_predicted(self):
        r = nh_ordering_consistency()
        assert r['consistent'] is True

    def test_um_predicts_nh(self):
        r = nh_ordering_consistency()
        assert 'NORMAL_HIERARCHY' in r['um_prediction']

    def test_juno_preference_positive(self):
        r = nh_ordering_consistency()
        assert r['juno_nh_preference_sigma'] > 0.0

    def test_global_stronger_than_juno_alone(self):
        r = nh_ordering_consistency()
        assert r['juno_global_delta_chi2'] > r['juno_delta_chi2']

    def test_honest_note_present(self):
        r = nh_ordering_consistency()
        assert len(r['honest_note']) > 20


class TestSin2Theta12:
    def test_consistency_keys(self):
        r = sin2_theta12_consistency()
        assert 'juno_sin2_theta12' in r
        assert 'um_geometric_estimate' in r

    def test_juno_value_correct(self):
        r = sin2_theta12_consistency()
        assert abs(r['juno_sin2_theta12'] - JUNO_SIN2_THETA12) < 1e-9

    def test_tension_finite(self):
        r = sin2_theta12_consistency()
        assert r['tension_sigma'] > 0.0


class TestForwardModel:
    def test_year2_sigma_smaller(self):
        r = forward_model_juno_year2()
        assert r['year2_sigma_ev2'] < JUNO_DM21_SIGMA_POST

    def test_year2_tension_higher_than_post(self):
        r = forward_model_juno_year2()
        t_post = tension_with_juno()
        assert r['year2_tension_sigma'] > t_post

    def test_year2_projection_note_present(self):
        r = forward_model_juno_year2()
        assert len(r['projection_note']) > 50


class TestSummary:
    def test_summary_pillar(self):
        s = pillar796_summary()
        assert s['pillar'] == 796

    def test_summary_gate(self):
        s = pillar796_summary()
        assert s['gate'] == PILLAR_796_GATE

    def test_summary_has_honest(self):
        s = pillar796_summary()
        assert 'honest_summary' in s

    def test_summary_alias(self):
        s = PILLAR_796_SUMMARY()
        assert s['pillar'] == 796
