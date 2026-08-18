# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 653 — DESI DR3 live routing protocol."""
from __future__ import annotations

import re

import pytest

from src.core.pillar653_desi_dr3_live_routing_protocol import (
    ADJACENT_TRACK,
    FALSIFICATION_THRESHOLD,
    PILLAR_631_LINK,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SHA256_PREREGISTRATION,
    TENSION_THRESHOLD,
    VERSION,
    WA_FROZEN_RADION,
    desi_dr3_verdict,
    pillar_report,
    routing_hash,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
HASH_INFO = routing_hash()
PASS_VERDICT = desi_dr3_verdict(-0.1, 0.5)
TENSION_VERDICT = desi_dr3_verdict(-0.4, 0.15)
FALSIFIED_VERDICT = desi_dr3_verdict(-0.55, 0.15)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 653

    def test_status(self):
        assert PILLAR_STATUS == 'DESI_DR3_LIVE_ROUTING_PROTOCOL_PREREGISTERED'

    def test_title(self):
        assert PILLAR_TITLE == 'DESI DR3 Live Routing Protocol'

    def test_version(self):
        assert VERSION == 'v21.0'

    def test_frozen_radion(self):
        assert WA_FROZEN_RADION == 0.0

    def test_thresholds(self):
        assert TENSION_THRESHOLD == 2.0
        assert FALSIFICATION_THRESHOLD == 3.0

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is False

    def test_pillar_link(self):
        assert PILLAR_631_LINK == 'pillar631_desi_dr3_falsification_response'

    def test_hash_length(self):
        assert len(SHA256_PREREGISTRATION) == 64

    def test_hash_hex(self):
        assert re.fullmatch(r'[0-9a-f]{64}', SHA256_PREREGISTRATION) is not None


class TestFunctions:
    def test_routing_hash_keys(self):
        for key in ['pillar', 'version', 'sha256_preregistration', 'payload']:
            assert key in HASH_INFO

    def test_pass_branch(self):
        assert PASS_VERDICT['branch'] == 'PASS'
        assert PASS_VERDICT['sigma_tension'] == pytest.approx(0.2)
        assert PASS_VERDICT['extension_triggered'] is False
        assert PASS_VERDICT['architecture_trigger'] is False

    def test_tension_branch(self):
        assert TENSION_VERDICT['branch'] == 'TENSION'
        assert TENSION_VERDICT['sigma_tension'] == pytest.approx(abs(-0.4) / 0.15)
        assert TENSION_VERDICT['extension_triggered'] is False

    def test_falsified_branch(self):
        assert FALSIFIED_VERDICT['branch'] == 'FALSIFIED'
        assert FALSIFIED_VERDICT['sigma_tension'] == pytest.approx(abs(-0.55) / 0.15)
        assert FALSIFIED_VERDICT['extension_triggered'] is True
        assert FALSIFIED_VERDICT['architecture_trigger'] is True

    def test_action_strings(self):
        assert PASS_VERDICT['action'] == 'frozen_radion_retained'
        assert TENSION_VERDICT['action'] == 'rolling_radion_extension_scoped'
        assert FALSIFIED_VERDICT['action'] == 'rolling_radion_extension_activated'

    def test_rolling_link_returned(self):
        assert PASS_VERDICT['rolling_radion_link'] == PILLAR_631_LINK

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            desi_dr3_verdict(0.1, 0.0)

    def test_extension_only_when_falsified(self):
        assert PASS_VERDICT['extension_triggered'] is False
        assert TENSION_VERDICT['extension_triggered'] is False
        assert FALSIFIED_VERDICT['extension_triggered'] is True

    def test_boundary_tension(self):
        verdict = desi_dr3_verdict(-0.3, 0.15)
        assert verdict['branch'] == 'TENSION'

    def test_boundary_falsified(self):
        verdict = desi_dr3_verdict(-0.45, 0.15)
        assert verdict['branch'] == 'FALSIFIED'


class TestReport:
    def test_pillar_report_keys(self):
        for key in [
            'pillar', 'title', 'status', 'version', 'adjacent_track',
            'wa_frozen_radion', 'falsification_threshold', 'tension_threshold',
            'routing_hash', 'pillar_631_link', 'what_is_claimed',
            'what_is_NOT_claimed', 'toe_score_delta', 'hardgate_score_delta',
        ]:
            assert key in REPORT

    def test_report_identity(self):
        assert REPORT['pillar'] == 653
        assert REPORT['status'] == PILLAR_STATUS

    def test_toe_delta(self):
        assert REPORT['toe_score_delta'] == 0.0
        assert REPORT['hardgate_score_delta'] == 0.0

    def test_claim_lists(self):
        assert len(what_is_claimed()) >= 5
        assert len(what_is_NOT_claimed()) >= 4
