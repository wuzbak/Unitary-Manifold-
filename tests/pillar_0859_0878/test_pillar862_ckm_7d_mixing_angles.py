# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 862 — 7D CKM mixing angles."""
from __future__ import annotations

import numpy as np
import pytest

from src.sevend.pillar862_ckm_7d_mixing_angles import (
    ALL_WITHIN_2SIGMA,
    CKM_MATRIX_ABS,
    GATE_PARTIAL_CLOSURE,
    GATE_PARTIAL_TENSION,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    THETA_12_DEG,
    THETA_12_PDG_DEG,
    THETA_13_DEG,
    THETA_13_PDG_DEG,
    THETA_23_DEG,
    THETA_23_PDG_DEG,
    ckm_7d_mixing_angles_summary,
    ckm_matrix,
    left_rotation,
    mixing_angles_deg,
    tension_sigma,
)


class TestPillar862Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 862
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 30
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2221
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2251
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_gate_is_one_of_two(self): assert PILLAR_GATE in {GATE_PARTIAL_CLOSURE, GATE_PARTIAL_TENSION}
    def test_gate_computed_tension(self): assert PILLAR_GATE == "CKM_7D_PARTIAL_TENSION"
    def test_gate_not_asserted_closure(self): assert PILLAR_GATE != GATE_PARTIAL_CLOSURE


class TestPillar862PDGReferences:
    def test_theta12_pdg(self): assert THETA_12_PDG_DEG == pytest.approx(13.04)
    def test_theta13_pdg(self): assert THETA_13_PDG_DEG == pytest.approx(0.201)
    def test_theta23_pdg(self): assert THETA_23_PDG_DEG == pytest.approx(2.38)
    def test_pdg_ordering(self): assert THETA_12_PDG_DEG > THETA_23_PDG_DEG > THETA_13_PDG_DEG


class TestPillar862Matrix:
    def test_rotation_shape(self): assert left_rotation((0.0, 0.5, 1.0)).shape == (3, 3)
    def test_rotation_orthogonal(self):
        u = left_rotation((0.0, 0.5, 1.0))
        assert np.allclose(u.T @ u, np.eye(3), atol=1e-12)
    def test_ckm_shape(self): assert ckm_matrix().shape == (3, 3)
    def test_ckm_unitary(self):
        v = ckm_matrix()
        assert np.allclose(v.T @ v, np.eye(3), atol=1e-12)
    def test_ckm_abs_nonnegative(self): assert np.all(CKM_MATRIX_ABS >= 0.0)
    def test_ckm_dominant_diagonal(self):
        assert CKM_MATRIX_ABS[0, 0] > 0.9 and CKM_MATRIX_ABS[2, 2] > 0.9


class TestPillar862Angles:
    def test_theta12_value(self): assert THETA_12_DEG == pytest.approx(11.939143, rel=1e-6)
    def test_theta13_value(self): assert THETA_13_DEG == pytest.approx(2.768346, rel=1e-6)
    def test_theta23_value(self): assert THETA_23_DEG == pytest.approx(0.737674, rel=1e-6)
    def test_angles_positive(self): assert min(THETA_12_DEG, THETA_13_DEG, THETA_23_DEG) > 0.0
    def test_angles_keys(self): assert set(mixing_angles_deg()) == {"theta_12", "theta_13", "theta_23"}
    def test_theta12_within_ten_percent(self):
        assert abs(THETA_12_DEG - THETA_12_PDG_DEG) / THETA_12_PDG_DEG < 0.10


class TestPillar862Tension:
    def test_tension_sigma_zero(self): assert tension_sigma(1.0, 1.0, 0.1) == pytest.approx(0.0)
    def test_tension_sigma_rejects_zero_error(self):
        with pytest.raises(ValueError):
            tension_sigma(1.0, 1.0, 0.0)
    def test_not_all_within_two_sigma(self): assert ALL_WITHIN_2SIGMA is False
    def test_summary_reports_tension(self):
        assert ckm_7d_mixing_angles_summary()["all_within_2sigma"] is False
    def test_summary_gate(self): assert ckm_7d_mixing_angles_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert ckm_7d_mixing_angles_summary()["pillar"] == 862
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_honest(self):
        assert "TENSION" in ckm_7d_mixing_angles_summary()["epistemic_status"].upper()
