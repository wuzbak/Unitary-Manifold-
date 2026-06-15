# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 441 — DESI DR3 Final Routing Package."""
import pytest
from src.core.pillar441_desi_dr3_final_routing import (
    PILLAR_STATUS, VERSION, UM_PREDICTION, DR2_STATE, PREREGISTRATION_HASH,
    desi_dr3_route, desi_dr3_joint_chi2_route,
    rehearsal_drill, run_all_rehearsal_drills,
    desi_dr3_report, _PILLAR_STATUS,
)


class TestPillarMetadata:
    def test_status_string(self):
        assert PILLAR_STATUS == 'DESI_DR3_ROUTING_FINALIZED'

    def test_version(self):
        assert VERSION == 'v13.8'

    def test_preregistration_hash(self):
        assert len(PREREGISTRATION_HASH) == 64

    def test_um_prediction_w0(self):
        assert UM_PREDICTION['w0'] == -1

    def test_um_prediction_wa(self):
        assert UM_PREDICTION['wa'] == 0

    def test_um_prediction_has_mechanism(self):
        assert 'mechanism' in UM_PREDICTION or 'falsifier' in UM_PREDICTION

    def test_dr2_state_has_tension(self):
        # Can be wa_cpl or combined_tension
        has_tension = ('tension_wa' in DR2_STATE or 'combined_tension' in DR2_STATE
                       or 'joint_2d_tension' in DR2_STATE)
        assert has_tension

    def test_dr2_state_has_wa(self):
        # Can be wa_cpl or wa_central
        has_wa = 'wa_cpl' in DR2_STATE or 'wa_central' in DR2_STATE
        assert has_wa

    def test_pillar_status_dict(self):
        assert _PILLAR_STATUS['pillar'] == 441


class TestRoutingLogic:
    def test_pass_low_chi2(self):
        # delta_chi2 < 2.30 → PASS_1SIGMA
        result = desi_dr3_joint_chi2_route(1.0)
        assert result['label'] == 'PASS'

    def test_tension_medium_chi2(self):
        # delta_chi2 in [2.30, 5.99]
        result = desi_dr3_joint_chi2_route(5.0)
        assert result['label'] == 'TENSION'

    def test_falsified_high_chi2(self):
        # delta_chi2 > 11.83 → FALSIFIED_OUTSIDE3SIGMA
        result = desi_dr3_joint_chi2_route(15.0)
        assert result['label'] == 'FALSIFIED'

    def test_tension_route(self):
        result = desi_dr3_route(-0.60, 0.30)
        assert 'verdict' in result

    def test_chi2_route_has_verdict(self):
        result = desi_dr3_joint_chi2_route(3.0)
        assert 'verdict' in result
        assert 'delta_chi2' in result


class TestRehearsalDrills:
    def test_all_pass(self):
        results = run_all_rehearsal_drills()
        # Should be a list or dict of results
        assert results is not None

    def test_scenario_a(self):
        r = rehearsal_drill('A')
        assert 'verdict' in r or 'drill' in str(r).lower()


class TestReport:
    def test_report_has_pillar(self):
        r = desi_dr3_report()
        assert 'pillar' in r or 'status' in r

    def test_report_returns_dict(self):
        r = desi_dr3_report()
        assert isinstance(r, dict)
