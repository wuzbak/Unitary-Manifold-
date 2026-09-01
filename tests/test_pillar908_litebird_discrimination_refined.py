# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 908 — refined LiteBIRD discrimination."""
from __future__ import annotations

import pytest

from src.core.pillar908_litebird_discrimination_refined import (
    BAYES_FACTOR_57_VS_0,
    BAYES_FACTOR_57_VS_56,
    BETA_56_SHADOW,
    BETA_57,
    DISCRIMINATION_GATE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    SIGMA_LITEBIRD,
    STATUS_LABEL,
    discrimination_summary,
    gaussian_bayes_factor,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 908

def test_gate_string(): assert PILLAR_GATE == "LITEBIRD_DISCRIMINATION_REFINED"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_betas_ordered(): assert BETA_57 > BETA_56_SHADOW > 0.0

def test_sigma_positive(): assert SIGMA_LITEBIRD > 0.0

def test_bayes_factor_vs_zero_large(): assert BAYES_FACTOR_57_VS_0 > 10.0

def test_bayes_factor_vs_shadow_gt_one(): assert BAYES_FACTOR_57_VS_56 > 1.0

def test_gate_ready(): assert DISCRIMINATION_GATE == "DISCRIMINATION_READY"

def test_gaussian_bayes_self(): assert gaussian_bayes_factor(BETA_57, BETA_57, BETA_56_SHADOW) == pytest.approx(BAYES_FACTOR_57_VS_56)

def test_gaussian_bayes_bad_sigma():
    with pytest.raises(ValueError):
        gaussian_bayes_factor(0.1, 0.1, 0.0, 0.0)


def test_summary_gate(): assert discrimination_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert discrimination_summary()["pillar"] == 908

def test_summary_status(): assert discrimination_summary()["status_label"] == STATUS_LABEL

def test_summary_beta57(): assert discrimination_summary()["beta_57"] == BETA_57

def test_summary_beta56(): assert discrimination_summary()["beta_56_shadow"] == BETA_56_SHADOW

def test_summary_sigma(): assert discrimination_summary()["sigma_litebird"] == SIGMA_LITEBIRD

def test_summary_bayes0(): assert discrimination_summary()["bayes_factor_57_vs_0"] == BAYES_FACTOR_57_VS_0

def test_summary_bayes56(): assert discrimination_summary()["bayes_factor_57_vs_56"] == BAYES_FACTOR_57_VS_56

def test_summary_gate_ready(): assert discrimination_summary()["discrimination_gate"] == DISCRIMINATION_GATE

def test_summary_delta_sigma_gt_one(): assert discrimination_summary()["delta_beta_over_sigma"] > 1.0

def test_no_toe_language(): assert "TOE" not in discrimination_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in discrimination_summary()
    return _test

globals()['test_generated_key_beta_57_0'] = _generated_key_test_factory('beta_57')
globals()['test_generated_key_beta_56_shadow_1'] = _generated_key_test_factory('beta_56_shadow')
globals()['test_generated_key_sigma_litebird_2'] = _generated_key_test_factory('sigma_litebird')
globals()['test_generated_key_bayes_factor_57_vs_0_3'] = _generated_key_test_factory('bayes_factor_57_vs_0')
globals()['test_generated_key_bayes_factor_57_vs_56_4'] = _generated_key_test_factory('bayes_factor_57_vs_56')
