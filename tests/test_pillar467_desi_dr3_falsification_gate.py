# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 467 — DESI DR3 falsification gate."""
from __future__ import annotations

import hashlib
import math
import pytest

from src.core.pillar467_desi_dr3_falsification_gate import (
    DESI_DR2_VALUES,
    PILLAR_STATUS,
    UM_PREDICTION,
    VERSION,
    apply_decision_protocol,
    compute_1d_tension,
    compute_2d_joint_tension,
    current_desi_dr2_verdict,
    pillar_report,
    preregistration_statement,
    project_dr3_tension,
    sha256_preregistration,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'DESI_DR3_FALSIFICATION_GATE_PREREGISTERED'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_um_prediction(self):
        assert UM_PREDICTION == {'w0': -1.0, 'wa': 0.0}

    def test_dr2_wa_value(self):
        assert DESI_DR2_VALUES['wa'] == pytest.approx(-0.62)

    def test_dr2_rho_value(self):
        assert DESI_DR2_VALUES['rho_w0_wa'] == pytest.approx(-0.97)


class TestTensionComputations:
    def test_1d_tension(self):
        assert compute_1d_tension(-0.62, 0.30) == pytest.approx(2.0666666667)

    def test_1d_requires_positive_error(self):
        with pytest.raises(ValueError):
            compute_1d_tension(-0.62, 0.0)

    def test_2d_tension_positive(self):
        value = compute_2d_joint_tension(-0.838, 0.072, -0.62, 0.30, -0.97)
        assert value > 0

    def test_2d_matches_manual_formula(self):
        w0, w0e, wa, wae, rho = -0.838, 0.072, -0.62, 0.30, -0.97
        delta0 = w0 + 1.0
        delta1 = wa
        cov00 = w0e ** 2
        cov11 = wae ** 2
        cov01 = rho * w0e * wae
        det = cov00 * cov11 - cov01 ** 2
        inv00 = cov11 / det
        inv11 = cov00 / det
        inv01 = -cov01 / det
        expected = math.sqrt(delta0 * (inv00 * delta0 + inv01 * delta1) + delta1 * (inv01 * delta0 + inv11 * delta1))
        assert compute_2d_joint_tension(w0, w0e, wa, wae, rho) == pytest.approx(expected)

    def test_2d_rejects_bad_error(self):
        with pytest.raises(ValueError):
            compute_2d_joint_tension(-1, 0, 0, 0.3, 0)

    def test_2d_rejects_bad_rho(self):
        with pytest.raises(ValueError):
            compute_2d_joint_tension(-1, 0.1, 0, 0.3, 1.0)


class TestDecisionProtocol:
    def test_falsified_rule(self):
        assert apply_decision_protocol(3.0, 3.0) == 'FALSIFIED'

    def test_confirmed_rule(self):
        assert apply_decision_protocol(1.9, 1.8) == 'CONFIRMED'

    def test_inconclusive_rule(self):
        assert apply_decision_protocol(2.2, 2.9) == 'INCONCLUSIVE'

    def test_current_dr2_inconclusive(self):
        assert current_desi_dr2_verdict()['verdict'] == 'INCONCLUSIVE'


class TestProjection:
    def setup_method(self):
        self.result = project_dr3_tension()

    def test_default_wa_central(self):
        assert self.result['wa_central'] == pytest.approx(-0.62)

    def test_default_wa_err(self):
        assert self.result['wa_err'] == pytest.approx(0.18)

    def test_projected_1d_tension(self):
        assert self.result['projected_1d_tension'] == pytest.approx(abs(-0.62) / 0.18)

    def test_projected_verdict_string(self):
        assert self.result['projected_verdict'] in {'FALSIFIED', 'CONFIRMED', 'INCONCLUSIVE'}

    def test_legacy_headline_present(self):
        assert self.result['legacy_headline_if_sigma_wa_0p135'] == pytest.approx(abs(-0.62) / 0.135)

    def test_negative_error_rejected(self):
        with pytest.raises(ValueError):
            project_dr3_tension(dr3_wa_err=0)


class TestPreregistration:
    def test_statement_mentions_decision_rule(self):
        assert 'Decision rule' in preregistration_statement()

    def test_statement_mentions_no_post_hoc(self):
        assert 'No post-hoc threshold changes' in preregistration_statement()

    def test_sha256_length(self):
        assert len(sha256_preregistration()) == 64

    def test_sha256_matches_hashlib(self):
        assert sha256_preregistration() == hashlib.sha256(preregistration_statement().encode('utf-8')).hexdigest()


class TestReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 467

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_projection(self):
        assert 'dr3_projection' in self.report

    def test_contains_current_verdict(self):
        assert 'current_verdict' in self.report

    def test_contains_hash(self):
        assert self.report['preregistration_sha256'] == sha256_preregistration()
