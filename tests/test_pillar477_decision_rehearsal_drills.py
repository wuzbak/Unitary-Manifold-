# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 477 — 2027 Decision Rehearsal Full Drills."""
from __future__ import annotations

from src.core.pillar477_decision_rehearsal_full_drills import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    WINDOW_DESI_DR3,
    WINDOW_SO_DR1,
    WINDOW_JUNO,
    WINDOW_SPHEREX_FNL,
    WINDOW_NEDM_SNS,
    WINDOW_LITEBIRD,
    route_verdict,
    run_window_drill,
    run_all_drills,
    full_rehearsal_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'REHEARSAL_DRILLS_2027_COMPLETE'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 477


class TestWindowDefinitions:
    def test_w1_id(self):
        assert WINDOW_DESI_DR3['id'] == 'W1'

    def test_w2_id(self):
        assert WINDOW_SO_DR1['id'] == 'W2'

    def test_w3_id(self):
        assert WINDOW_JUNO['id'] == 'W3'

    def test_w4_id(self):
        assert WINDOW_SPHEREX_FNL['id'] == 'W4'

    def test_w5_id(self):
        assert WINDOW_NEDM_SNS['id'] == 'W5'

    def test_w6_id(self):
        assert WINDOW_LITEBIRD['id'] == 'W6'

    def test_all_have_sigma(self):
        for w in [WINDOW_DESI_DR3, WINDOW_SO_DR1, WINDOW_JUNO,
                  WINDOW_SPHEREX_FNL, WINDOW_NEDM_SNS, WINDOW_LITEBIRD]:
            assert 'sigma_experiment' in w
            assert w['sigma_experiment'] > 0

    def test_desi_prediction_zero(self):
        assert WINDOW_DESI_DR3['um_prediction'] == 0.0

    def test_juno_prediction_reasonable(self):
        # Pillar 475 NLO prediction
        assert 2.44e-3 < WINDOW_JUNO['um_prediction'] < 2.46e-3

    def test_so_dr1_prediction_braided(self):
        assert abs(WINDOW_SO_DR1['um_prediction'] - 0.0315) < 0.001


class TestRouteVerdict:
    def test_pass_at_prediction(self):
        result = route_verdict(WINDOW_DESI_DR3, 0.0, 0.2)
        assert result['verdict'] == 'PASS'

    def test_tension_at_2sigma(self):
        sigma = WINDOW_DESI_DR3['sigma_experiment']
        result = route_verdict(WINDOW_DESI_DR3, 0.0 + 2.5 * sigma, sigma)
        assert result['verdict'] == 'TENSION'

    def test_falsified_at_3sigma(self):
        sigma = WINDOW_DESI_DR3['sigma_experiment']
        result = route_verdict(WINDOW_DESI_DR3, 0.0 + 4.0 * sigma, sigma)
        assert result['verdict'] == 'FALSIFIED'

    def test_returns_dict(self):
        result = route_verdict(WINDOW_JUNO, 2.452e-3, 0.005 * 2.453e-3)
        assert isinstance(result, dict)

    def test_has_deviation(self):
        result = route_verdict(WINDOW_JUNO, 2.452e-3, 0.005 * 2.453e-3)
        assert 'deviation_sigma' in result

    def test_litebird_forbidden_gap(self):
        # A measurement inside the forbidden gap should be FALSIFIED
        sigma = WINDOW_LITEBIRD['sigma_experiment']
        # β = 0.300° is inside forbidden gap (0.29, 0.31)
        result = route_verdict(WINDOW_LITEBIRD, 0.300, sigma)
        assert result['verdict'] == 'FALSIFIED'

    def test_litebird_mode1_pass(self):
        sigma = WINDOW_LITEBIRD['sigma_experiment']
        result = route_verdict(WINDOW_LITEBIRD, 0.331, sigma)
        assert result['verdict'] == 'PASS'

    def test_litebird_mode2_pass(self):
        sigma = WINDOW_LITEBIRD['sigma_experiment']
        result = route_verdict(WINDOW_LITEBIRD, 0.273, sigma)
        assert result['verdict'] == 'PASS'


class TestWindowDrill:
    def test_w1_routing_correct(self):
        drill = run_window_drill(WINDOW_DESI_DR3)
        assert drill['routing_correct'] is True

    def test_w2_routing_correct(self):
        drill = run_window_drill(WINDOW_SO_DR1)
        assert drill['routing_correct'] is True

    def test_w3_routing_correct(self):
        drill = run_window_drill(WINDOW_JUNO)
        assert drill['routing_correct'] is True

    def test_w4_routing_correct(self):
        drill = run_window_drill(WINDOW_SPHEREX_FNL)
        assert drill['routing_correct'] is True

    def test_w5_routing_correct(self):
        drill = run_window_drill(WINDOW_NEDM_SNS)
        assert drill['routing_correct'] is True

    def test_w6_routing_correct(self):
        drill = run_window_drill(WINDOW_LITEBIRD)
        assert drill['routing_correct'] is True

    def test_has_all_scenarios(self):
        drill = run_window_drill(WINDOW_DESI_DR3)
        assert 'scenarios' in drill
        assert 'A_CONFIRM' in drill['scenarios']
        assert 'E_HARD_FALSIFIED_5S' in drill['scenarios']

    def test_scenario_a_is_pass(self):
        drill = run_window_drill(WINDOW_DESI_DR3)
        assert drill['scenarios']['A_CONFIRM']['verdict'] == 'PASS'

    def test_scenario_c_is_falsified(self):
        drill = run_window_drill(WINDOW_DESI_DR3)
        assert drill['scenarios']['C_EDGE_3S']['verdict'] == 'FALSIFIED'

    def test_scenario_e_is_falsified(self):
        drill = run_window_drill(WINDOW_DESI_DR3)
        assert drill['scenarios']['E_HARD_FALSIFIED_5S']['verdict'] == 'FALSIFIED'

    def test_status_drill_pass(self):
        drill = run_window_drill(WINDOW_DESI_DR3)
        assert drill['status'] == 'DRILL_PASS'


class TestRunAllDrills:
    def setup_method(self):
        self.drills = run_all_drills()

    def test_returns_list(self):
        assert isinstance(self.drills, list)

    def test_six_windows(self):
        assert len(self.drills) == 6

    def test_all_pass(self):
        for d in self.drills:
            assert d['status'] == 'DRILL_PASS', f"Window {d['window_id']} failed"

    def test_all_routing_correct(self):
        for d in self.drills:
            assert d['routing_correct'] is True


class TestFullRehearsalReport:
    def setup_method(self):
        self.report = full_rehearsal_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_status(self):
        assert self.report['status'] == 'REHEARSAL_DRILLS_2027_COMPLETE'

    def test_six_windows(self):
        assert self.report['n_windows'] == 6

    def test_thirty_scenarios(self):
        assert self.report['total_scenarios'] == 30

    def test_all_routing_correct(self):
        assert self.report['all_routing_correct'] is True

    def test_verdict_complete(self):
        assert self.report['verdict'] == 'REHEARSAL_COMPLETE'

    def test_readiness_level(self):
        assert self.report['readiness_level'] == 'FULLY_READY'

    def test_has_next_real_data(self):
        assert 'next_real_data' in self.report
        assert 'W1_DESI_DR3' in self.report['next_real_data']

    def test_routing_status_all_pass(self):
        for wid, status in self.report['routing_status'].items():
            assert status == 'DRILL_PASS', f"Window {wid} status: {status}"
