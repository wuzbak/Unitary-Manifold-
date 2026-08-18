# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 654 — SO DR1 / ACT joint verdict lock."""
from __future__ import annotations

import re

import pytest

from src.core.pillar654_so_dr1_act_joint_verdict_lock import (
    ADJACENT_TRACK,
    ARCHITECTURE_LIMIT_THRESHOLD_R,
    HIGH_TENSION_THRESHOLD_R,
    PASS_THRESHOLD_R,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    R_IRREDUCIBILITY_CERTIFIED,
    R_NLO_UM,
    SHA256_PREREGISTRATION,
    VERSION,
    pillar_report,
    so_dr1_joint_verdict,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
CONSISTENT = so_dr1_joint_verdict(0.032, 0.005)
IRREDUCIBLE = so_dr1_joint_verdict(0.018, 0.003)
ARCH_LIMIT = so_dr1_joint_verdict(0.013, 0.002)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 654

    def test_status(self):
        assert PILLAR_STATUS == 'SO_DR1_ACT_JOINT_VERDICT_LOCK_PREREGISTERED'

    def test_version(self):
        assert VERSION == 'v21.0'

    def test_r_nlo(self):
        assert R_NLO_UM == pytest.approx(0.03132)

    def test_irreducibility_certified(self):
        assert R_IRREDUCIBILITY_CERTIFIED is True

    def test_threshold_ordering(self):
        assert ARCHITECTURE_LIMIT_THRESHOLD_R < HIGH_TENSION_THRESHOLD_R < PASS_THRESHOLD_R

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is False

    def test_hash_shape(self):
        assert re.fullmatch(r'[0-9a-f]{64}', SHA256_PREREGISTRATION) is not None


class TestFunctions:
    def test_consistent_branch(self):
        assert CONSISTENT['branch'] == 'CONSISTENT'
        assert CONSISTENT['sigma_tension'] == pytest.approx(abs(0.032 - R_NLO_UM) / 0.005)
        assert CONSISTENT['architecture_limit_triggered'] is False

    def test_irreducible_branch(self):
        assert IRREDUCIBLE['branch'] == 'IRREDUCIBLE_CONFIRMED'
        assert IRREDUCIBLE['architecture_limit_triggered'] is False

    def test_architecture_limit_branch(self):
        assert ARCH_LIMIT['branch'] == 'ARCHITECTURE_LIMIT_TRIGGERED'
        assert ARCH_LIMIT['architecture_limit_triggered'] is True

    def test_action_strings(self):
        assert CONSISTENT['action'] == 'retain_braided_inflation_sector'
        assert IRREDUCIBLE['action'] == 'confirm_act_side_irreducibility'
        assert ARCH_LIMIT['action'] == 'activate_inflation_architecture_review'

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            so_dr1_joint_verdict(0.03, 0.0)

    def test_high_value_can_still_be_consistent(self):
        verdict = so_dr1_joint_verdict(0.034, 0.004)
        assert verdict['branch'] == 'CONSISTENT'

    def test_midrange_maps_to_irreducible(self):
        verdict = so_dr1_joint_verdict(0.021, 0.002)
        assert verdict['branch'] == 'IRREDUCIBLE_CONFIRMED'


class TestReport:
    def test_report_keys(self):
        for key in [
            'pillar', 'title', 'status', 'version', 'adjacent_track',
            'r_nlo_um', 'pass_threshold_r', 'high_tension_threshold_r',
            'architecture_limit_threshold_r', 'sha256_preregistration',
            'what_is_claimed', 'what_is_NOT_claimed', 'toe_score_delta', 'hardgate_score_delta',
        ]:
            assert key in REPORT

    def test_toe_delta(self):
        assert REPORT['toe_score_delta'] == 0.0
        assert REPORT['hardgate_score_delta'] == 0.0

    def test_claims_present(self):
        assert len(what_is_claimed()) >= 5
        assert len(what_is_NOT_claimed()) >= 4
