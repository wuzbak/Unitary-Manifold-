# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 906 — DESI+Euclid preregistration."""
from __future__ import annotations

import pytest

from src.core.pillar906_desi_euclid_joint_preregistration import (
    JOINT_SIGMA_W0,
    JOINT_SIGMA_WA,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    VERDICT_THRESHOLDS,
    W0_PREDICTION,
    WA_PREDICTION,
    joint_sigma,
    preregistration_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 906

def test_gate_string(): assert PILLAR_GATE == "DESI_DR3_EUCLID_JOINT_PREREGISTRATION"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_predictions(): assert (W0_PREDICTION, WA_PREDICTION) == (-1.05, 0.15)

def test_joint_sigma_formula_w0(): assert JOINT_SIGMA_W0 == pytest.approx(joint_sigma(0.03, 0.04))

def test_joint_sigma_formula_wa(): assert JOINT_SIGMA_WA == pytest.approx(joint_sigma(0.12, 0.17))

def test_joint_sigma_smaller_w0(): assert JOINT_SIGMA_W0 < 0.03

def test_joint_sigma_smaller_wa(): assert JOINT_SIGMA_WA < 0.12

def test_joint_sigma_rejects_bad():
    with pytest.raises(ValueError):
        joint_sigma(0.0, 0.1)


def test_thresholds_keys(): assert set(VERDICT_THRESHOLDS) == {"TENSION", "STRONG_TENSION", "FALSIFIED"}

def test_summary_gate(): assert preregistration_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert preregistration_summary()["pillar"] == 906

def test_summary_status(): assert preregistration_summary()["status_label"] == STATUS_LABEL

def test_summary_w0(): assert preregistration_summary()["w0_prediction"] == -1.05

def test_summary_wa(): assert preregistration_summary()["wa_prediction"] == 0.15

def test_summary_joint_sigma_w0(): assert preregistration_summary()["joint_sigma_w0"] == JOINT_SIGMA_W0

def test_summary_joint_sigma_wa(): assert preregistration_summary()["joint_sigma_wa"] == JOINT_SIGMA_WA

def test_summary_thresholds(): assert preregistration_summary()["verdict_thresholds"] == VERDICT_THRESHOLDS

def test_no_toe_language(): assert "TOE" not in preregistration_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in preregistration_summary()
    return _test

globals()['test_generated_key_w0_prediction_0'] = _generated_key_test_factory('w0_prediction')
globals()['test_generated_key_wa_prediction_1'] = _generated_key_test_factory('wa_prediction')
globals()['test_generated_key_joint_sigma_w0_2'] = _generated_key_test_factory('joint_sigma_w0')
globals()['test_generated_key_joint_sigma_wa_3'] = _generated_key_test_factory('joint_sigma_wa')
globals()['test_generated_key_verdict_thresholds_4'] = _generated_key_test_factory('verdict_thresholds')
globals()['test_generated_key_epistemic_status_5'] = _generated_key_test_factory('epistemic_status')
