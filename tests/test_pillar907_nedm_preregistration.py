# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 907 — nEDM preregistration."""
from __future__ import annotations

from src.core.pillar907_nedm_preregistration import (
    DN_WINDOW_HIGH,
    DN_WINDOW_LOW,
    NEDM_SNS_SENSITIVITY,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    VERDICT_THRESHOLDS,
    nedm_preregistration_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 907

def test_gate_string(): assert PILLAR_GATE == "NEDM_SNS_PREREGISTRATION"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_window_ordered(): assert 0.0 < DN_WINDOW_LOW < DN_WINDOW_HIGH

def test_window_width_positive(): assert DN_WINDOW_HIGH - DN_WINDOW_LOW > 0.0

def test_sensitivity_positive(): assert NEDM_SNS_SENSITIVITY > 0.0

def test_sensitivity_below_window(): assert NEDM_SNS_SENSITIVITY < DN_WINDOW_LOW

def test_threshold_keys(): assert set(VERDICT_THRESHOLDS) == {"CONFIRMED", "FALSIFIED", "TENSION"}

def test_summary_gate(): assert nedm_preregistration_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert nedm_preregistration_summary()["pillar"] == 907

def test_summary_status(): assert nedm_preregistration_summary()["status_label"] == STATUS_LABEL

def test_summary_window_low(): assert nedm_preregistration_summary()["dn_window_low"] == DN_WINDOW_LOW

def test_summary_window_high(): assert nedm_preregistration_summary()["dn_window_high"] == DN_WINDOW_HIGH

def test_summary_sensitivity(): assert nedm_preregistration_summary()["nedm_sns_sensitivity"] == NEDM_SNS_SENSITIVITY

def test_summary_thresholds(): assert nedm_preregistration_summary()["verdict_thresholds"] == VERDICT_THRESHOLDS

def test_no_toe_language(): assert "TOE" not in nedm_preregistration_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in nedm_preregistration_summary()
    return _test

globals()['test_generated_key_dn_window_low_0'] = _generated_key_test_factory('dn_window_low')
globals()['test_generated_key_dn_window_high_1'] = _generated_key_test_factory('dn_window_high')
globals()['test_generated_key_nedm_sns_sensitivity_2'] = _generated_key_test_factory('nedm_sns_sensitivity')
globals()['test_generated_key_verdict_thresholds_3'] = _generated_key_test_factory('verdict_thresholds')
globals()['test_generated_key_epistemic_status_4'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_status_label_5'] = _generated_key_test_factory('status_label')
globals()['test_generated_key_gate_6'] = _generated_key_test_factory('gate')
globals()['test_generated_key_pillar_7'] = _generated_key_test_factory('pillar')
globals()['test_generated_key_window_width_8'] = _generated_key_test_factory('window_width')
