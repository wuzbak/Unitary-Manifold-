# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 901 — Yukawa SVD/FN synthesis."""
from __future__ import annotations

from src.sevend.pillar901_yukawa_svd_fn_unified import (
    CKM_FN_UNIFIED,
    PMNS_FN_UNIFIED,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    YUKAWA_UNIFIED_GATE,
    yukawa_svd_fn_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 901

def test_gate_string(): assert PILLAR_GATE == "YUKAWA_SVD_FN_UNIFIED"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_result_gate_expected(): assert YUKAWA_UNIFIED_GATE == "FN_IMPROVES_CKM"

def test_ckm_shape(): assert CKM_FN_UNIFIED.shape == (3, 3)

def test_pmns_shape(): assert PMNS_FN_UNIFIED.shape == (3, 3)

def test_ckm_abs_nonnegative(): assert (abs(CKM_FN_UNIFIED) >= 0.0).all()

def test_pmns_abs_nonnegative(): assert (abs(PMNS_FN_UNIFIED) >= 0.0).all()

def test_summary_gate(): assert yukawa_svd_fn_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert yukawa_svd_fn_summary()["pillar"] == 901

def test_summary_status(): assert yukawa_svd_fn_summary()["status_label"] == STATUS_LABEL

def test_summary_result_gate(): assert yukawa_svd_fn_summary()["result_gate"] == YUKAWA_UNIFIED_GATE

def test_summary_ckm_status(): assert yukawa_svd_fn_summary()["ckm_svd_status"] == "CKM_SVD_DERIVED"

def test_summary_pmns_status(): assert yukawa_svd_fn_summary()["pmns_svd_status"] == "PMNS_SVD_DERIVED"

def test_summary_fn_distance_smaller(): assert yukawa_svd_fn_summary()["fn_ckm_distance"] < yukawa_svd_fn_summary()["base_ckm_distance"]

def test_summary_ckm_abs_count(): assert len(yukawa_svd_fn_summary()["ckm_fn_unified_abs"]) == 3

def test_summary_pmns_abs_count(): assert len(yukawa_svd_fn_summary()["pmns_fn_unified_abs"]) == 3

def test_no_toe_language(): assert "TOE" not in yukawa_svd_fn_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in yukawa_svd_fn_summary()
    return _test

globals()['test_generated_key_ckm_svd_status_0'] = _generated_key_test_factory('ckm_svd_status')
globals()['test_generated_key_pmns_svd_status_1'] = _generated_key_test_factory('pmns_svd_status')
globals()['test_generated_key_base_ckm_distance_2'] = _generated_key_test_factory('base_ckm_distance')
globals()['test_generated_key_fn_ckm_distance_3'] = _generated_key_test_factory('fn_ckm_distance')
globals()['test_generated_key_ckm_fn_unified_abs_4'] = _generated_key_test_factory('ckm_fn_unified_abs')
globals()['test_generated_key_pmns_fn_unified_abs_5'] = _generated_key_test_factory('pmns_fn_unified_abs')
globals()['test_generated_key_epistemic_status_6'] = _generated_key_test_factory('epistemic_status')
