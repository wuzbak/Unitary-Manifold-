# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 888 — CKM FN correction."""
from __future__ import annotations

import numpy as np
import pytest

from src.sevend.pillar888_ckm_7d_fn_correction import (
    CKM_7D_FN_GATE,
    CKM_FN_MATRIX,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    THETA_12_FN,
    THETA_13_FN,
    THETA_23_FN,
    ckm_fn_correction_summary,
    corrected_bulk_mass_matrix,
)
from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import C_DOWN, C_UP
from src.sevend.pillar887_fn_charge_assignment import FN_CHARGES_DOWN, FN_CHARGES_UP

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 888

def test_gate_string(): assert PILLAR_GATE == "CKM_7D_FN_CORRECTION"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_ckm_verdict_allowed(): assert CKM_7D_FN_GATE in {"RESOLVED", "TENSION_PERSISTS"}

def test_up_matrix_shape(): assert corrected_bulk_mass_matrix(C_UP, FN_CHARGES_UP).shape == (3, 3)

def test_down_matrix_shape(): assert corrected_bulk_mass_matrix(C_DOWN, FN_CHARGES_DOWN).shape == (3, 3)

def test_ckm_shape(): assert CKM_FN_MATRIX.shape == (3, 3)

def test_ckm_unitary(): assert np.allclose(CKM_FN_MATRIX.T @ CKM_FN_MATRIX, np.eye(3), atol=1e-12)

def test_ckm_entries_finite(): assert np.isfinite(CKM_FN_MATRIX).all()

def test_theta12_positive(): assert THETA_12_FN > 0.0

def test_theta13_positive(): assert THETA_13_FN > 0.0

def test_theta23_nonnegative(): assert THETA_23_FN >= 0.0

def test_theta_ordering(): assert THETA_12_FN > THETA_23_FN > THETA_13_FN

def test_theta12_less_than_pdg(): assert THETA_12_FN < 13.04

def test_theta13_below_one_degree(): assert THETA_13_FN < 1.0

def test_theta23_few_degrees(): assert THETA_23_FN < 5.0

def test_summary_gate(): assert ckm_fn_correction_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert ckm_fn_correction_summary()["pillar"] == 888

def test_summary_status(): assert ckm_fn_correction_summary()["status_label"] == STATUS_LABEL

def test_summary_angles_keys(): assert set(ckm_fn_correction_summary()["angles_deg"]) == {"theta_12", "theta_13", "theta_23"}

def test_summary_pdg_keys(): assert set(ckm_fn_correction_summary()["pdg_deg"]) == {"theta_12", "theta_13", "theta_23"}

def test_summary_sigma_keys(): assert set(ckm_fn_correction_summary()["tension_sigma"]) == {"theta_12", "theta_13", "theta_23"}

def test_summary_unitarity_small(): assert ckm_fn_correction_summary()["unitarity_residual"] < 1e-12

def test_summary_all_within_two_sigma_false(): assert ckm_fn_correction_summary()["all_within_2sigma"] is False

def test_summary_distance_positive(): assert ckm_fn_correction_summary()["pdg_distance_deg"] > 0.0

def test_no_toe_language(): assert "TOE" not in ckm_fn_correction_summary()["epistemic_status"].upper()
