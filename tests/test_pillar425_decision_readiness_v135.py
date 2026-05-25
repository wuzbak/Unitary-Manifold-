# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 425 — Decision Readiness Package v13.5."""
import pytest

from src.core.pillar425_decision_readiness_v135 import (
    PILLAR_STATUS,
    VERSION,
    N_DECISION_WINDOWS,
    decision_windows_registry,
    v135_state_summary,
    all_windows_preregistered,
    decision_readiness_v135_verdict,
    rehearsal_drills,
)

WINDOWS = decision_windows_registry()
DRILLS = rehearsal_drills()


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'DECISION_READINESS_V135'

    def test_version(self):
        assert VERSION == 'v13.5'

    def test_n_windows(self):
        assert N_DECISION_WINDOWS == 6


class TestDecisionWindowsRegistry:
    def test_returns_six_entries(self):
        assert len(WINDOWS) == 6

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4, 5])
    def test_each_has_window_number(self, idx):
        assert 'window' in WINDOWS[idx]

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4, 5])
    def test_each_has_experiment(self, idx):
        assert 'experiment' in WINDOWS[idx]

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4, 5])
    def test_each_has_um_prediction(self, idx):
        assert 'um_prediction' in WINDOWS[idx]

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4, 5])
    def test_each_has_routing_function(self, idx):
        assert 'routing_function' in WINDOWS[idx]

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4, 5])
    def test_each_has_expected_year(self, idx):
        assert 'expected_year' in WINDOWS[idx]
        assert 2026 <= WINDOWS[idx]['expected_year'] <= 2035

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4, 5])
    def test_each_is_preregistered(self, idx):
        assert WINDOWS[idx]['preregistered'] is True

    def test_desi_window_high_tension(self):
        desi = next(w for w in WINDOWS if 'DESI' in w['name'])
        assert desi['current_status'] == 'HIGH_TENSION'

    def test_litebird_window_pending(self):
        lb = next(w for w in WINDOWS if 'LiteBIRD' in w['name'])
        assert lb['current_status'] == 'PENDING'

    def test_juno_window_consistent(self):
        juno = next(w for w in WINDOWS if 'JUNO' in w['name'])
        assert juno['current_status'] == 'CONSISTENT'


class TestV135StateSummary:
    def test_returns_dict(self):
        assert isinstance(v135_state_summary(), dict)

    def test_version(self):
        assert v135_state_summary()['version'] == 'v13.5'

    def test_completion_certified(self):
        state = v135_state_summary()
        assert state['completion_status'] == 'COMPLETION_CERTIFIED'

    def test_n_admissions(self):
        state = v135_state_summary()
        assert state['n_admissions'] == 13
        assert state['n_admissions_closed'] == 13

    def test_has_key_updates(self):
        state = v135_state_summary()
        assert 'key_epistemic_updates' in state
        assert len(state['key_epistemic_updates']) >= 5

    def test_high_tension_windows_listed(self):
        state = v135_state_summary()
        assert 'high_tension_windows' in state
        assert len(state['high_tension_windows']) >= 2


class TestAllWindowsPreregistered:
    def test_returns_true(self):
        assert all_windows_preregistered() is True


class TestRehearsalDrills:
    def test_returns_ten_entries(self):
        assert len(DRILLS) == 10

    @pytest.mark.parametrize('idx', list(range(10)))
    def test_each_has_drill_number(self, idx):
        assert 'drill' in DRILLS[idx]

    @pytest.mark.parametrize('idx', list(range(10)))
    def test_each_has_scenario(self, idx):
        assert 'scenario' in DRILLS[idx]

    @pytest.mark.parametrize('idx', list(range(10)))
    def test_each_drill_passes(self, idx):
        assert DRILLS[idx]['result'] == 'PASS'

    def test_drills_numbered_1_to_10(self):
        numbers = [d['drill'] for d in DRILLS]
        assert sorted(numbers) == list(range(1, 11))


class TestDecisionReadinessV135Verdict:
    def test_returns_dict(self):
        assert isinstance(decision_readiness_v135_verdict(), dict)

    def test_status(self):
        assert decision_readiness_v135_verdict()['status'] == 'DECISION_READINESS_V135'

    @pytest.mark.parametrize('key', ['version', 'n_windows', 'all_preregistered',
                                     'all_drills_pass', 'n_drills', 'framework_state',
                                     'windows', 'drills', 'verdict'])
    def test_expected_keys(self, key):
        assert key in decision_readiness_v135_verdict()

    def test_all_preregistered(self):
        assert decision_readiness_v135_verdict()['all_preregistered'] is True

    def test_all_drills_pass(self):
        assert decision_readiness_v135_verdict()['all_drills_pass'] is True

    def test_n_drills_ten(self):
        assert decision_readiness_v135_verdict()['n_drills'] == 10

    def test_verdict_is_string(self):
        assert isinstance(decision_readiness_v135_verdict()['verdict'], str)
