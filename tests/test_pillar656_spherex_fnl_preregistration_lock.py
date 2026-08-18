# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 656 — SPHEREx f_NL preregistration lock."""
from __future__ import annotations

import re

import pytest

from src.core.pillar656_spherex_fnl_preregistration_lock import (
    ADJACENT_TRACK,
    FNL_BAND_HIGH,
    FNL_BAND_LOW,
    FNL_DBI_RAW,
    FNL_UM_KK,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SHA256_PREREGISTRATION,
    SPHEREX_SNR,
    VERSION,
    pillar_report,
    spherex_verdict,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
PASS_VERDICT = spherex_verdict(-2.2, 0.2)
TENSION_VERDICT = spherex_verdict(-1.5, 0.25)
FALSIFIED_VERDICT = spherex_verdict(0.5, 0.2)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 656

    def test_status(self):
        assert PILLAR_STATUS == 'SPHEREX_FNL_PREREGISTRATION_LOCKED'

    def test_version(self):
        assert VERSION == 'v21.0'

    def test_band_order(self):
        assert FNL_BAND_LOW < FNL_UM_KK < FNL_BAND_HIGH

    def test_raw_is_below_high_edge(self):
        assert FNL_DBI_RAW < FNL_BAND_HIGH

    def test_snr_positive(self):
        assert SPHEREX_SNR > 0.0

    def test_hash_hex(self):
        assert re.fullmatch(r'[0-9a-f]{64}', SHA256_PREREGISTRATION) is not None

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is False


class TestFunctions:
    def test_pass_branch(self):
        assert PASS_VERDICT['branch'] == 'PASS'
        assert PASS_VERDICT['overlap_width'] > 0.0

    def test_tension_branch(self):
        assert TENSION_VERDICT['branch'] == 'TENSION'
        assert TENSION_VERDICT['overlap_width'] > 0.0

    def test_falsified_branch(self):
        assert FALSIFIED_VERDICT['branch'] == 'FALSIFIED'
        assert FALSIFIED_VERDICT['overlap_width'] == 0.0

    def test_prereg_hash_returned(self):
        assert PASS_VERDICT['sha256_preregistration'] == SHA256_PREREGISTRATION

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            spherex_verdict(-2.0, 0.0)

    def test_exact_central_band_point_passes(self):
        verdict = spherex_verdict(FNL_UM_KK, 0.1)
        assert verdict['branch'] == 'PASS'


class TestReport:
    def test_report_keys(self):
        for key in [
            'pillar', 'title', 'status', 'version', 'adjacent_track',
            'fnl_um_kk', 'fnl_band_low', 'fnl_band_high', 'fnl_dbi_raw',
            'spherex_snr', 'sha256_preregistration', 'what_is_claimed',
            'what_is_NOT_claimed', 'toe_score_delta', 'hardgate_score_delta',
        ]:
            assert key in REPORT

    def test_toe_delta(self):
        assert REPORT['toe_score_delta'] == 0.0
        assert REPORT['hardgate_score_delta'] == 0.0

    def test_claim_lists(self):
        assert len(what_is_claimed()) >= 5
        assert len(what_is_NOT_claimed()) >= 4
