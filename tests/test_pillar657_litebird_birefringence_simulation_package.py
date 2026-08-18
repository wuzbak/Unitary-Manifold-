# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 657 — LiteBIRD birefringence simulation package."""
from __future__ import annotations

import pytest

from src.core.pillar657_litebird_birefringence_simulation_package import (
    ADJACENT_TRACK,
    BETA_ADMISSIBLE_HIGH,
    BETA_ADMISSIBLE_LOW,
    BETA_CANONICAL_HIGH,
    BETA_CANONICAL_LOW,
    BETA_GAP_HIGH,
    BETA_GAP_LOW,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TOE_IMPACT_FAIL,
    TOE_IMPACT_PARTIAL,
    TOE_IMPACT_PASS,
    VERSION,
    litebird_verdict,
    pillar_report,
    simulate_litebird_campaign,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
OM_A = litebird_verdict(0.273, 0.02)
OM_B = litebird_verdict(0.225, 0.02)
OM_C = litebird_verdict(0.30, 0.02)
OM_D = litebird_verdict(0.40, 0.02)
SIM_A = simulate_litebird_campaign(1000, 42)
SIM_B = simulate_litebird_campaign(1000, 42)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 657

    def test_status(self):
        assert PILLAR_STATUS == 'LITEBIRD_BIREFRINGENCE_SIMULATION_CERTIFIED'

    def test_version(self):
        assert VERSION == 'v21.0'

    def test_window_order(self):
        assert BETA_ADMISSIBLE_LOW < BETA_CANONICAL_LOW < BETA_GAP_LOW
        assert BETA_GAP_LOW < BETA_GAP_HIGH < BETA_CANONICAL_HIGH < BETA_ADMISSIBLE_HIGH

    def test_toe_impacts(self):
        assert TOE_IMPACT_PASS == 2.0
        assert TOE_IMPACT_PARTIAL == 1.0
        assert TOE_IMPACT_FAIL == 0.0

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is False


class TestFunctions:
    def test_om_a_branch(self):
        assert OM_A['branch'] == 'OM_A'
        assert OM_A['toe_impact_pts'] == TOE_IMPACT_PASS
        assert OM_A['simulation_mode'] is True

    def test_om_b_branch(self):
        assert OM_B['branch'] == 'OM_B'
        assert OM_B['toe_impact_pts'] == TOE_IMPACT_PARTIAL

    def test_om_c_branch(self):
        assert OM_C['branch'] == 'OM_C'
        assert OM_C['toe_impact_pts'] == TOE_IMPACT_FAIL

    def test_om_d_branch(self):
        assert OM_D['branch'] == 'OM_D'
        assert OM_D['toe_impact_pts'] == TOE_IMPACT_FAIL

    def test_gap_takes_priority(self):
        verdict = litebird_verdict(0.295, 0.02)
        assert verdict['branch'] == 'OM_C'

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            litebird_verdict(0.3, 0.0)

    def test_simulation_deterministic(self):
        assert SIM_A == SIM_B

    def test_simulation_fraction_sum(self):
        total = SIM_A['fraction_OM_A'] + SIM_A['fraction_OM_B'] + SIM_A['fraction_OM_C'] + SIM_A['fraction_OM_D']
        assert total == pytest.approx(1.0)

    def test_simulation_all_fractions_bounded(self):
        for key in ['fraction_OM_A', 'fraction_OM_B', 'fraction_OM_C', 'fraction_OM_D']:
            assert 0.0 <= SIM_A[key] <= 1.0

    def test_simulation_invalid_trials(self):
        with pytest.raises(ValueError):
            simulate_litebird_campaign(0, 42)


class TestReport:
    def test_report_keys(self):
        for key in [
            'pillar', 'title', 'status', 'version', 'adjacent_track',
            'beta_canonical_low', 'beta_canonical_high', 'beta_admissible_low',
            'beta_admissible_high', 'beta_gap_low', 'beta_gap_high',
            'what_is_claimed', 'what_is_NOT_claimed', 'toe_score_delta', 'hardgate_score_delta',
        ]:
            assert key in REPORT

    def test_toe_delta(self):
        assert REPORT['toe_score_delta'] == 0.0
        assert REPORT['hardgate_score_delta'] == 0.0

    def test_claim_lists(self):
        assert len(what_is_claimed()) >= 5
        assert len(what_is_NOT_claimed()) >= 4
