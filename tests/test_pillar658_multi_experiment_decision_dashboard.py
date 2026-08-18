# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 658 — multi-experiment decision dashboard."""
from __future__ import annotations

import json

from src.core.pillar658_multi_experiment_decision_dashboard import (
    ADJACENT_TRACK,
    EXPERIMENTS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERDICT_DATES,
    VERSION,
    decision_dashboard,
    pillar_report,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
DASHBOARD = decision_dashboard()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 658

    def test_status(self):
        assert PILLAR_STATUS == 'MULTI_EXPERIMENT_DECISION_DASHBOARD_CERTIFIED'

    def test_version(self):
        assert VERSION == 'v21.0'

    def test_experiments_count(self):
        assert len(EXPERIMENTS) == 5

    def test_dates_count(self):
        assert len(VERDICT_DATES) == 5

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is False


class TestFunctions:
    def test_dashboard_has_five_entries(self):
        assert DASHBOARD['n_experiments'] == 5
        assert len(DASHBOARD['experiments']) == 5

    def test_each_experiment_has_required_keys(self):
        required = {'name', 'verdict_date', 'current_status', 'sigma_level', 'routing_branch', 'pillar_refs'}
        for experiment in DASHBOARD['experiments']:
            assert required.issubset(experiment.keys())

    def test_all_routing_branches_awaiting(self):
        for experiment in DASHBOARD['experiments']:
            assert experiment['routing_branch'] == 'AWAITING'

    def test_dashboard_json_serializable(self):
        encoded = json.dumps(DASHBOARD)
        assert 'DESI_DR3' in encoded

    def test_names_match_constant(self):
        names = [experiment['name'] for experiment in DASHBOARD['experiments']]
        assert names == EXPERIMENTS

    def test_litebird_date(self):
        litebird = next(item for item in DASHBOARD['experiments'] if item['name'] == 'LITEBIRD_2032')
        assert litebird['verdict_date'] == '2032'


class TestReport:
    def test_report_keys(self):
        for key in ['pillar', 'title', 'status', 'version', 'adjacent_track', 'decision_dashboard', 'what_is_claimed', 'what_is_NOT_claimed', 'toe_score_delta', 'hardgate_score_delta']:
            assert key in REPORT

    def test_toe_delta(self):
        assert REPORT['toe_score_delta'] == 0.0
        assert REPORT['hardgate_score_delta'] == 0.0

    def test_claims_present(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
