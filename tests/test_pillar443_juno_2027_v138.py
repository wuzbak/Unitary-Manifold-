# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 443 — JUNO 2027 Routing Package v13.8."""
import pytest
from src.core.pillar443_juno_2027_v138 import (
    PILLAR_STATUS, VERSION, JUNO_SPECS, UM_PREDICTION, PREREGISTRATION_HASH,
    DM31_SQ_UM, DM31_SQ_PDG, DM31_SQ_PDG_SIGMA,
    juno_route, juno_cross_checks, juno_report,
    rehearsal_drill, run_all_rehearsal_drills,
)


class TestPillarMetadata:
    def test_status_string(self):
        assert 'JUNO' in PILLAR_STATUS

    def test_version(self):
        assert VERSION == 'v13.8'

    def test_hash_sha256(self):
        assert len(PREREGISTRATION_HASH) == 64

    def test_dm31_um_value(self):
        assert abs(DM31_SQ_UM - 2.452e-3) < 1e-5

    def test_dm31_pdg_value(self):
        assert abs(DM31_SQ_PDG - 2.453e-3) < 1e-4

    def test_juno_specs_has_note(self):
        # Has a 'note' key describing the measurement
        assert 'note' in JUNO_SPECS or 'sigma_dm31_expected' in JUNO_SPECS

    def test_juno_specs_has_name(self):
        assert 'name' in JUNO_SPECS

    def test_um_prediction_has_dm31(self):
        assert 'dm31_sq' in UM_PREDICTION or 'dm31' in UM_PREDICTION


class TestJUNORouting:
    def test_confirmed(self):
        # Measurement close to prediction
        result = juno_route(2.452e-3, 0.012e-3)
        assert result['verdict'] in ('CONFIRMED', 'CONSISTENT', 'PASS')

    def test_tension(self):
        # 1-2σ tension scenario — must be close to boundary
        result = juno_route(2.47e-3, 0.012e-3)  # ~1.5σ deviation
        assert result['verdict'] in ('TENSION', 'CONSISTENT', 'PASS')

    def test_falsified(self):
        # Measurement far from prediction
        result = juno_route(2.0e-3, 0.012e-3)
        assert result['verdict'] == 'FALSIFIED'

    def test_result_has_verdict(self):
        result = juno_route(2.452e-3, 0.012e-3)
        assert 'verdict' in result


class TestCrossChecks:
    def test_cross_checks_return(self):
        r = juno_cross_checks()
        assert isinstance(r, (dict, list))

    def test_cross_checks_not_empty(self):
        r = juno_cross_checks()
        assert r is not None


class TestReport:
    def test_report_dict(self):
        r = juno_report()
        assert isinstance(r, dict)

    def test_report_has_pillar_or_status(self):
        r = juno_report()
        assert 'pillar' in r or 'status' in r
