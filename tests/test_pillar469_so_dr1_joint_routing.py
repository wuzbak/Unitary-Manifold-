# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 469 — SO DR1 joint routing."""
from __future__ import annotations

import pytest

from src.core.pillar469_so_dr1_joint_routing import (
    ACT_DR6_BOUND,
    PILLAR_STATUS,
    SO_SIGMA_R,
    UM_R_PREDICTION,
    VERSION,
    decision_protocol,
    five_d_eft_irreducibility_proof,
    pillar_report,
    pre_so_dr1_status,
    required_um_modification,
    so_dr1_projected_sensitivity,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'SO_DR1_JOINT_ROUTING_FORMALIZED'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_um_prediction(self):
        assert UM_R_PREDICTION == pytest.approx(0.0315)

    def test_act_bound(self):
        assert ACT_DR6_BOUND['upper'] == pytest.approx(0.016)

    def test_so_sigma(self):
        assert SO_SIGMA_R == pytest.approx(0.003)


class TestSensitivity:
    def setup_method(self):
        self.result = so_dr1_projected_sensitivity()

    def test_sigma_r(self):
        assert self.result['sigma_r'] == pytest.approx(0.003)

    def test_expected_date(self):
        assert self.result['expected_date'] == 2027

    def test_five_sigma_floor(self):
        assert self.result['five_sigma_floor'] == pytest.approx(0.015)


class TestDecisionProtocol:
    def test_softening_above_002(self):
        assert decision_protocol(0.021, 0.003) == 'ARCHITECTURE_LIMIT_SOFTENING'

    def test_falsified_below_001_at_three_sigma(self):
        assert decision_protocol(0.007, 0.001) == 'FALSIFIED'

    def test_tension_confirmed_midrange(self):
        assert decision_protocol(0.015, 0.003) == 'TENSION_CONFIRMED'

    def test_tension_confirmed_if_below_threshold_but_not_significant(self):
        assert decision_protocol(0.009, 0.002) == 'TENSION_CONFIRMED'

    def test_positive_error_required(self):
        with pytest.raises(ValueError):
            decision_protocol(0.02, 0.0)


class TestModificationRequirements:
    def setup_method(self):
        self.result = required_um_modification()

    def test_option_1_mentions_6d(self):
        assert '6D' in self.result['option_1']

    def test_option_2_mentions_irreducible(self):
        assert 'IRREDUCIBLE' in self.result['option_2']

    def test_option_3_mentions_delta_n(self):
        assert 'Δn = 4' in self.result['option_3']

    def test_conclusion_mentions_minimal_5d(self):
        assert 'minimal 5D' in self.result['conclusion']


class TestIrreducibilityProof:
    def setup_method(self):
        self.result = five_d_eft_irreducibility_proof()

    def test_required_suppression_positive(self):
        assert self.result['required_fractional_suppression'] > 0

    def test_architecture_limit_true(self):
        assert self.result['architecture_limit'] is True

    def test_minimal_r_matches_prediction(self):
        assert self.result['minimal_r_in_5d'] == pytest.approx(0.0315)

    def test_statement_mentions_49(self):
        assert '49%' in self.result['proof_statement'] or '>49%' in self.result['proof_statement']


class TestPreSOStatus:
    def setup_method(self):
        self.result = pre_so_dr1_status()

    def test_not_falsified_yet(self):
        assert self.result['falsified'] is False

    def test_verdict_label(self):
        assert self.result['verdict'] == 'ARCHITECTURE_LIMIT_ACTIVE'

    def test_next_experiment_expected_date(self):
        assert self.result['next_decisive_experiment']['expected_date'] == 2027


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 469

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_sensitivity(self):
        assert 'so_sensitivity' in self.report

    def test_contains_irreducibility_proof(self):
        assert 'irreducibility_proof' in self.report

    def test_contains_required_modification(self):
        assert 'required_modification' in self.report

    def test_contains_pre_so_status(self):
        assert 'pre_so_status' in self.report
