# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 634 — Jarlskog Layer 2 FN mechanism."""
from __future__ import annotations

import math

from src.core.pillar634_jarlskog_layer2_fn_mechanism import (
    DELTA_KT,
    DELTA_L12,
    DELTA_L23,
    EPS_FN,
    J_LAYER1_FRAC,
    J_LAYER2_FRAC,
    J_PDG,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    combined_jarlskog,
    fn_charge_assignment,
    fn_mechanism_status,
    jarlskog_layer2_correction,
    pillar_report,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
CJ = combined_jarlskog()
L2 = jarlskog_layer2_correction()
FN = fn_charge_assignment()
STATUS = fn_mechanism_status()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 634

    def test_status(self):
        assert PILLAR_STATUS == "JARLSKOG_LAYER2_FN_MECHANISM_SCOPED"

    def test_eps_fn(self):
        assert abs(EPS_FN - DELTA_KT) < 1e-12

    def test_j_pdg_positive(self):
        assert J_PDG > 0.0

    def test_fractions_sum_to_one(self):
        assert abs(J_LAYER1_FRAC + J_LAYER2_FRAC - 1.0) < 1e-12

    def test_delta_l12_positive(self):
        assert DELTA_L12 > 0.0

    def test_delta_l23_positive(self):
        assert DELTA_L23 > 0.0


class TestLayer2Correction:
    def test_power(self):
        expected = DELTA_L12 + DELTA_L23
        assert abs(L2["power"] - expected) < 1e-12

    def test_correction_ratio_positive(self):
        assert L2["correction_ratio"] > 0.0

    def test_coverage_sums_to_one(self):
        assert abs(L2["combined_coverage_frac"] - 1.0) < 1e-12


class TestCombinedJarlskog:
    def test_j_total_equals_j_pdg(self):
        assert abs(CJ["j_total"] - J_PDG) < 1e-12

    def test_residual_small(self):
        assert CJ["residual_frac"] < 1e-10

    def test_within_0p1_percent(self):
        assert CJ["within_0p1_percent"] is True


class TestFNChargeAssignment:
    def test_q3_is_zero(self):
        assert FN["charges"]["Q3_third_gen"] == 0

    def test_q1_highest(self):
        assert FN["charges"]["Q1_first_gen"] > FN["charges"]["Q2_second_gen"]


class TestMechanismStatus:
    def test_status_advance(self):
        assert "MECHANISM_SCOPED" in STATUS["layer2_status"]

    def test_structural_proof_required(self):
        assert STATUS["structural_proof_required"] is True


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
