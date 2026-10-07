# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 864 — 7D Jarlskog invariant."""
from __future__ import annotations

import numpy as np
import pytest

from src.sevend.pillar864_jarlskog_invariant_7d import (
    J_7D,
    J_IDENTITY,
    J_ORDER_OF_MAGNITUDE_WITHIN_TEN,
    J_PDG,
    J_PDG_ERR,
    J_RATIO_VS_PDG,
    J_SIGN_CORRECT,
    J_TENSION_SIGMA,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    ckm_complex_matrix,
    jarlskog_from_matrix,
    jarlskog_identity,
    jarlskog_invariant_7d_summary,
)


class TestPillar864Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 864
    def test_gate(self): assert PILLAR_GATE == "JARLSKOG_INVARIANT_7D_COMPUTED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2276
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2296
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_pdg_value(self): assert J_PDG == pytest.approx(3.08e-5)
    def test_pdg_error(self): assert J_PDG_ERR == pytest.approx(1.5e-6)


class TestPillar864Matrix:
    def test_matrix_shape(self): assert ckm_complex_matrix().shape == (3, 3)
    def test_matrix_complex(self): assert np.iscomplexobj(ckm_complex_matrix())
    def test_matrix_unitary(self):
        v = ckm_complex_matrix()
        assert np.allclose(v @ v.conj().T, np.eye(3), atol=1e-10)
    def test_matrix_has_imaginary_part(self):
        assert np.max(np.abs(ckm_complex_matrix().imag)) > 1e-6
    def test_matrix_zero_phase_is_real(self):
        assert np.max(np.abs(ckm_complex_matrix(delta_rad=0.0).imag)) < 1e-12


class TestPillar864Invariant:
    def test_j_value(self): assert J_7D == pytest.approx(1.1289467e-4, rel=1e-5)
    def test_j_positive(self): assert J_7D > 0.0
    def test_j_sign_correct(self): assert J_SIGN_CORRECT is True
    def test_j_identity_agrees(self): assert J_IDENTITY == pytest.approx(J_7D, rel=1e-10)
    def test_j_from_matrix_matches(self):
        assert jarlskog_from_matrix(ckm_complex_matrix()) == pytest.approx(J_7D, rel=1e-12)
    def test_j_identity_function(self):
        assert jarlskog_identity() == pytest.approx(J_IDENTITY, rel=1e-12)
    def test_j_vanishes_without_phase(self):
        assert abs(jarlskog_from_matrix(ckm_complex_matrix(delta_rad=0.0))) < 1e-18
    def test_j_rejects_wrong_shape(self):
        with pytest.raises(ValueError):
            jarlskog_from_matrix(np.eye(2, dtype=complex))


class TestPillar864Tension:
    def test_ratio_vs_pdg(self): assert J_RATIO_VS_PDG == pytest.approx(3.66541, rel=1e-5)
    def test_ratio_above_one(self): assert J_RATIO_VS_PDG > 1.0
    def test_tension_sigma(self): assert J_TENSION_SIGMA == pytest.approx(54.7298, rel=1e-5)
    def test_tension_reported_large(self): assert J_TENSION_SIGMA > 10.0
    def test_order_of_magnitude_within_ten(self): assert J_ORDER_OF_MAGNITUDE_WITHIN_TEN is True


class TestPillar864Summary:
    def test_summary_gate(self): assert jarlskog_invariant_7d_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert jarlskog_invariant_7d_summary()["pillar"] == 864
    def test_summary_lean4(self): assert jarlskog_invariant_7d_summary()["lean4_total_after"] == 2296
    def test_summary_parameter_free(self):
        assert jarlskog_invariant_7d_summary()["parameter_free"] is True
    def test_summary_reports_tension(self):
        assert jarlskog_invariant_7d_summary()["j_tension_sigma"] > 10.0
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_honest(self):
        status = jarlskog_invariant_7d_summary()["epistemic_status"].upper()
        assert "TENSION" in status or "OPEN" in status
