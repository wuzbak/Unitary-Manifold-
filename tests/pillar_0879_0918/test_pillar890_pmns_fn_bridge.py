# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 890 — PMNS FN bridge."""
from __future__ import annotations

import numpy as np

from src.sevend.pillar890_pmns_fn_bridge import (
    DELTA_CP_FN_DEG,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PMNS_FN_GATE,
    PMNS_FN_MATRIX,
    STATUS_LABEL,
    pmns_fn_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 890

def test_gate_string(): assert PILLAR_GATE == "PMNS_FN_BRIDGE"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_pmns_verdict_allowed(): assert PMNS_FN_GATE in {"PMNS_FN_CONSISTENT", "PMNS_FN_TENSION"}

def test_matrix_shape(): assert PMNS_FN_MATRIX.shape == (3, 3)

def test_matrix_unitary(): assert np.allclose(PMNS_FN_MATRIX.T @ PMNS_FN_MATRIX, np.eye(3), atol=1e-10)

def test_matrix_finite(): assert np.isfinite(PMNS_FN_MATRIX).all()

def test_delta_cp_positive(): assert DELTA_CP_FN_DEG > 0.0

def test_delta_cp_near_target(): assert abs(DELTA_CP_FN_DEG - 197.0) < 50.0

def test_summary_gate(): assert pmns_fn_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert pmns_fn_summary()["pillar"] == 890

def test_summary_status(): assert pmns_fn_summary()["status_label"] == STATUS_LABEL

def test_summary_verdict(): assert pmns_fn_summary()["fn_verdict"] == PMNS_FN_GATE

def test_summary_delta_window_true(): assert pmns_fn_summary()["delta_cp_within_2sigma"] is True

def test_summary_angles_keys(): assert set(pmns_fn_summary()["angles_deg"]) == {"theta_12", "theta_13", "theta_23"}

def test_summary_pdg_keys(): assert set(pmns_fn_summary()["pdg_deg"]) == {"theta_12", "theta_13", "theta_23"}

def test_summary_unitarity_small(): assert pmns_fn_summary()["unitarity_residual"] < 1e-10

def test_summary_theta12_nonnegative(): assert pmns_fn_summary()["angles_deg"]["theta_12"] >= 0.0

def test_summary_theta13_nonnegative(): assert pmns_fn_summary()["angles_deg"]["theta_13"] >= 0.0

def test_summary_theta23_nonnegative(): assert pmns_fn_summary()["angles_deg"]["theta_23"] >= 0.0

def test_no_toe_language(): assert "TOE" not in pmns_fn_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in pmns_fn_summary()
    return _test

globals()['test_generated_key_pmns_fn_matrix_abs_0'] = _generated_key_test_factory('pmns_fn_matrix_abs')
globals()['test_generated_key_unitarity_residual_1'] = _generated_key_test_factory('unitarity_residual')
globals()['test_generated_key_delta_cp_fn_deg_2'] = _generated_key_test_factory('delta_cp_fn_deg')
globals()['test_generated_key_delta_cp_target_deg_3'] = _generated_key_test_factory('delta_cp_target_deg')
globals()['test_generated_key_delta_cp_target_err_deg_4'] = _generated_key_test_factory('delta_cp_target_err_deg')
globals()['test_generated_key_epistemic_status_5'] = _generated_key_test_factory('epistemic_status')
