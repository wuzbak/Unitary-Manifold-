# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 442 — Simons Observatory DR1 Routing."""
import pytest
from src.core.pillar442_so_dr1_routing import (
    PILLAR_STATUS, VERSION, UM_PREDICTION, SO_SPECS, PREREGISTRATION_HASH,
    so_dr1_route, so_dr1_sensitivity_projection, so_dr1_report,
    rehearsal_drill, run_all_rehearsal_drills, R_BRAIDED, K_CS, N_W,
)


class TestPillarMetadata:
    def test_status_string(self):
        assert PILLAR_STATUS == 'SO_DR1_ROUTING_CERTIFIED'

    def test_version(self):
        assert VERSION == 'v13.8'

    def test_r_braided(self):
        assert abs(R_BRAIDED - 0.0315) < 1e-3

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_hash_sha256(self):
        assert len(PREREGISTRATION_HASH) == 64

    def test_um_prediction_r(self):
        assert 'r_braided' in UM_PREDICTION or 'r_canonical' in UM_PREDICTION


class TestRoutingLogic:
    def test_strong_confirmation(self):
        # r_meas close to UM prediction, small sigma
        result = so_dr1_route(0.0315, 0.003)
        assert result['label'] == 'PASS' or 'CONFIRMATION' in result['verdict']

    def test_upper_limit_zero_sigma(self):
        # Upper limit mode: r=0 means upper limit only
        with pytest.raises((ValueError, Exception)):
            so_dr1_route(0.0, 0.0)

    def test_result_has_verdict(self):
        result = so_dr1_route(0.0315, 0.003)
        assert 'verdict' in result

    def test_result_has_preregistration_hash(self):
        result = so_dr1_route(0.0315, 0.003)
        assert 'preregistration_hash' in result

    def test_tension_scenario(self):
        # Measured value far from UM prediction
        result = so_dr1_route(0.015, 0.002)
        assert 'verdict' in result


class TestSensitivityProjection:
    def test_has_year1_and_5year(self):
        r = so_dr1_sensitivity_projection()
        assert 'year1' in r
        assert '5year' in r

    def test_year1_has_sigma_r(self):
        r = so_dr1_sensitivity_projection()
        assert 'sigma_r' in r['year1']

    def test_5year_sigma_smaller(self):
        r = so_dr1_sensitivity_projection()
        assert r['5year']['sigma_r'] < r['year1']['sigma_r']


class TestReport:
    def test_report_pillar(self):
        r = so_dr1_report()
        assert 'pillar' in r or 'status' in r

    def test_report_dict(self):
        r = so_dr1_report()
        assert isinstance(r, dict)
