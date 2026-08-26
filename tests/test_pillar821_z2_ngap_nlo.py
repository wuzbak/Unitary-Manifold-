# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 821 — Z2 N_gap NLO Correction."""
from __future__ import annotations

import pytest

from src.core.pillar821_z2_ngap_nlo_correction import (
    C_L_LO,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_GAP_LO,
    NLO_THRESHOLD,
    PILLAR_GATE,
    PILLAR_NUMBER,
    Z2_NLO_RESULT,
    compute_nlo_correction,
    z2_ngap_nlo_verdict,
)


class TestPillar821Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 821

    def test_gate(self):
        assert PILLAR_GATE == "Z2_NGAP_NLO_CONFIRMED"

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_gap_lo(self):
        assert N_GAP_LO == 3

    def test_c_l_lo(self):
        assert abs(C_L_LO - 71 / 74) < 1e-10

    def test_nlo_threshold(self):
        assert NLO_THRESHOLD == 1e-3

    def test_lean4_count(self):
        assert LEAN4_THEOREM_COUNT == 18

    def test_lean4_total_before(self):
        assert LEAN4_TOTAL_BEFORE == 1431

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT


class TestZ2NLOComputation:
    def test_runs(self):
        result = compute_nlo_correction()
        assert result is not None

    def test_c_l_lo_value(self):
        result = compute_nlo_correction()
        assert abs(result.c_l_lo - 71 / 74) < 1e-10

    def test_delta_c_l_positive(self):
        """NLO correction should be positive (small upward shift)."""
        result = compute_nlo_correction()
        assert result.delta_c_l > 0

    def test_delta_c_l_sub_threshold(self):
        """NLO correction must be sub-0.1%."""
        result = compute_nlo_correction()
        assert abs(result.delta_c_l) < NLO_THRESHOLD

    def test_fractional_correction_sub_threshold(self):
        result = compute_nlo_correction()
        assert result.fractional_correction < NLO_THRESHOLD

    def test_is_robust_true(self):
        result = compute_nlo_correction()
        assert result.is_robust is True

    def test_gate_confirmed(self):
        result = compute_nlo_correction()
        assert result.gate == PILLAR_GATE

    def test_delta_y_nlo_positive(self):
        result = compute_nlo_correction()
        assert result.delta_y_nlo > 0

    def test_delta_n_gap_positive(self):
        result = compute_nlo_correction()
        assert result.delta_n_gap > 0

    def test_c_l_nlo_close_to_lo(self):
        """NLO c_L should be very close to leading-order 71/74."""
        result = compute_nlo_correction()
        assert abs(result.c_l_nlo - result.c_l_lo) < NLO_THRESHOLD

    def test_c_l_nlo_less_than_lo(self):
        """NLO correction reduces c_L slightly (modes partially restored)."""
        result = compute_nlo_correction()
        # delta_c_l = delta_n_gap / K_CS > 0
        # c_l_nlo = (K_CS - N_gap - delta_n_gap) / K_CS < c_l_lo
        assert result.c_l_nlo < result.c_l_lo


class TestZ2NLOVerdict:
    def test_verdict_runs(self):
        verdict = z2_ngap_nlo_verdict()
        assert verdict is not None

    def test_verdict_closure(self):
        verdict = z2_ngap_nlo_verdict()
        assert verdict["closure"] is True

    def test_verdict_gate(self):
        verdict = z2_ngap_nlo_verdict()
        assert verdict["gate"] == PILLAR_GATE

    def test_verdict_pillar(self):
        verdict = z2_ngap_nlo_verdict()
        assert verdict["pillar"] == 821

    def test_verdict_open_items(self):
        verdict = z2_ngap_nlo_verdict()
        assert len(verdict["open_items"]) >= 3

    def test_verdict_lean4(self):
        verdict = z2_ngap_nlo_verdict()
        assert verdict["lean4_theorems"] == 18
        assert verdict["lean4_total"] == 1449

    def test_verdict_interpretation(self):
        verdict = z2_ngap_nlo_verdict()
        assert "robust" in verdict["interpretation"].lower()

    def test_verdict_k_cs(self):
        verdict = z2_ngap_nlo_verdict()
        assert verdict["k_cs"] == 74

    def test_verdict_phi_0(self):
        verdict = z2_ngap_nlo_verdict()
        assert verdict["phi_0"] == 37.0

    def test_verdict_n_gap_lo(self):
        verdict = z2_ngap_nlo_verdict()
        assert verdict["n_gap_lo"] == 3


class TestZ2NLOModuleSingleton:
    def test_singleton_exists(self):
        assert Z2_NLO_RESULT is not None

    def test_singleton_robust(self):
        assert Z2_NLO_RESULT.is_robust is True

    def test_singleton_gate(self):
        assert Z2_NLO_RESULT.gate == PILLAR_GATE
