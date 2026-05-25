# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 444 — CMB-S4 Prediction Package."""
import pytest
from src.core.pillar444_cmbs4_prediction_package import (
    PILLAR_STATUS, VERSION, UM_PREDICTIONS, CMBS4_SPECS,
    R_BRAIDED, N_S, K_CS, N_W,
    cmbs4_route_r, cmbs4_route_ns, snr_projections,
    cmbs4_report, rehearsal_drill, run_all_rehearsal_drills,
)


class TestPillarMetadata:
    def test_status_string(self):
        assert 'CMB' in PILLAR_STATUS or 'PREDICTION' in PILLAR_STATUS

    def test_version(self):
        assert VERSION == 'v13.8'

    def test_r_braided(self):
        assert abs(R_BRAIDED - 0.0315) < 1e-3

    def test_n_s(self):
        assert abs(N_S - 0.9635) < 1e-3

    def test_k_cs(self):
        assert K_CS == 74

    def test_um_predictions_r(self):
        assert 'r' in UM_PREDICTIONS

    def test_cmbs4_specs_sigma_r(self):
        assert 'sigma_r' in CMBS4_SPECS


class TestCMBS4RouteR:
    def test_detectable_scenario(self):
        # r_meas = r_braided, well-detected
        r = cmbs4_route_r(R_BRAIDED, 0.002)
        assert 'verdict' in r

    def test_returns_dict(self):
        r = cmbs4_route_r(0.01, 0.005)
        assert isinstance(r, dict)

    def test_um_prediction_in_result(self):
        r = cmbs4_route_r(R_BRAIDED, 0.002)
        assert 'um_prediction' in r

    def test_snr_present(self):
        r = cmbs4_route_r(R_BRAIDED, 0.002)
        assert 'snr' in r


class TestCMBS4RouteNs:
    def test_consistent_ns(self):
        r = cmbs4_route_ns(N_S, 0.002)
        assert 'verdict' in r

    def test_returns_dict(self):
        r = cmbs4_route_ns(N_S, 0.002)
        assert isinstance(r, dict)


class TestSNRProjections:
    def test_has_r(self):
        r = snr_projections()
        assert 'r' in r

    def test_has_biref(self):
        r = snr_projections()
        assert 'biref_primary' in r or 'biref' in str(r.keys())


class TestReport:
    def test_report_dict(self):
        r = cmbs4_report()
        assert isinstance(r, dict)

    def test_report_has_pillar_or_status(self):
        r = cmbs4_report()
        assert 'pillar' in r or 'status' in r
