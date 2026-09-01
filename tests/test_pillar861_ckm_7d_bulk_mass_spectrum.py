# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 861 — 7D CKM bulk mass spectrum."""
from __future__ import annotations

import math

import numpy as np
import pytest

from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import (
    C_DOWN,
    C_UP,
    EPSILON_WARP,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    M_5_GEV,
    N_GENERATIONS,
    N_W,
    OVERLAP_WIDTH_SQ,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PI_K_R,
    REMAINING_OPEN,
    THETA_TORSION_7D,
    bulk_mass_matrix,
    bulk_mass_spectrum_summary,
    mass_ratios,
    overlap_coefficient,
    singular_values,
    warp_suppression,
    zero_mode_normalization,
)


class TestPillar861Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 861
    def test_gate(self): assert PILLAR_GATE == "CKM_7D_BULK_MASS_SPECTRUM_DERIVED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 35
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2186
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2221
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_k_cs_from_braid(self): assert 5**2 + 7**2 == K_CS
    def test_n_generations(self): assert N_GENERATIONS == 3
    def test_pi_k_r(self): assert PI_K_R == pytest.approx(37.0)
    def test_m5_scale(self): assert M_5_GEV == pytest.approx(1042.0)


class TestPillar861Geometry:
    def test_theta_torsion(self): assert THETA_TORSION_7D == pytest.approx(math.pi * N_W / K_CS)
    def test_epsilon_warp(self): assert EPSILON_WARP == pytest.approx(math.exp(-2.5), rel=1e-9)
    def test_epsilon_in_unit_interval(self): assert 0.0 < EPSILON_WARP < 1.0
    def test_overlap_width_sq(self): assert OVERLAP_WIDTH_SQ == pytest.approx(K_CS / N_W**2)
    def test_zero_mode_normalization(self): assert zero_mode_normalization(1.0) > 0.0
    def test_zero_mode_scales_inversely(self):
        assert zero_mode_normalization(4.0) < zero_mode_normalization(1.0)
    def test_zero_mode_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            zero_mode_normalization(0.0)
    def test_warp_suppression_monotone(self):
        assert warp_suppression(1.0) < warp_suppression(0.5)
    def test_overlap_diagonal_is_one(self): assert overlap_coefficient(1, 1) == pytest.approx(1.0)
    def test_overlap_offdiagonal_below_one(self): assert overlap_coefficient(0, 2) < 1.0
    def test_overlap_symmetric(self):
        assert overlap_coefficient(0, 2) == pytest.approx(overlap_coefficient(2, 0))


class TestPillar861Charges:
    def test_c_up_values(self): assert C_UP == (0.0, 0.5, 1.0)
    def test_c_down_values(self): assert C_DOWN == (0.0, 0.25, 0.75)
    def test_c_up_ordered(self): assert list(C_UP) == sorted(C_UP)
    def test_c_down_ordered(self): assert list(C_DOWN) == sorted(C_DOWN)
    def test_charge_count(self): assert len(C_UP) == len(C_DOWN) == N_GENERATIONS


class TestPillar861Matrix:
    def test_matrix_shape(self): assert bulk_mass_matrix(C_UP).shape == (3, 3)
    def test_matrix_symmetric(self):
        m = bulk_mass_matrix(C_UP)
        assert np.allclose(m, m.T)
    def test_matrix_positive(self): assert np.all(bulk_mass_matrix(C_UP) > 0.0)
    def test_matrix_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            bulk_mass_matrix((0.0, 1.0))
    def test_singular_values_up(self):
        sv = singular_values(C_UP)
        assert float(sv[0]) == pytest.approx(74.7584325, rel=1e-6)
    def test_singular_values_descending(self):
        sv = singular_values(C_UP)
        assert float(sv[0]) > float(sv[1]) > float(sv[2]) > 0.0
    def test_rank_full(self):
        assert np.linalg.matrix_rank(bulk_mass_matrix(C_UP)) == 3
    def test_mass_ratios_keys(self):
        assert set(mass_ratios(C_UP)) == {"m2_over_m3", "m1_over_m2", "m1_over_m3"}
    def test_mass_ratio_hierarchy(self):
        r = mass_ratios(C_UP)
        assert r["m1_over_m3"] < r["m2_over_m3"] < 1.0


class TestPillar861Summary:
    def test_summary_gate(self): assert bulk_mass_spectrum_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert bulk_mass_spectrum_summary()["pillar"] == 861
    def test_summary_hierarchy_ordered(self):
        assert bulk_mass_spectrum_summary()["hierarchy_ordered"] is True
    def test_summary_lean4(self):
        assert bulk_mass_spectrum_summary()["lean4_total_after"] == 2221
    def test_summary_has_epistemic_status(self):
        assert "epistemic_status" in bulk_mass_spectrum_summary()
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_remaining_open_labelled(self):
        assert all("OPEN" in item for item in REMAINING_OPEN)
    def test_no_toe_language(self):
        assert "ToE" not in bulk_mass_spectrum_summary()["epistemic_status"]
