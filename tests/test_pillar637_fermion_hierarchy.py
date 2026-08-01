# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 637 — fermion hierarchy FN analytic formula completion."""
from __future__ import annotations

import math

import pytest

from src.core.pillar637_fermion_hierarchy_fn_complete import (
    DELTA_C,
    EPS_FN,
    FERMION_HIERARCHY_STATUS_AFTER,
    FERMION_HIERARCHY_STATUS_BEFORE,
    K_CS,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PI_KR,
    VERSION,
    WITHIN_05_DEX,
    WITHIN_10_DEX,
    Y_TOP,
    fermion_hierarchy_table,
    fn_corrected_yukawa,
    hierarchy_coverage,
    pillar_report,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
TABLE = fermion_hierarchy_table()
COV = hierarchy_coverage()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 637

    def test_status(self):
        assert "FN_COMPLETE" in PILLAR_STATUS

    def test_delta_c(self):
        assert abs(DELTA_C - N_W / K_CS) < 1e-12

    def test_pi_kr(self):
        assert abs(PI_KR - (K_CS / N_W) * math.pi) < 1e-10

    def test_y_top(self):
        assert abs(Y_TOP - 0.935) < 1e-9

    def test_status_advance(self):
        assert "PARTIALLY_CONSTRAINED" in FERMION_HIERARCHY_STATUS_BEFORE
        assert "FN_COMPLETE" in FERMION_HIERARCHY_STATUS_AFTER


class TestFNCorrectYukawa:
    def test_top_anchor(self):
        y = fn_corrected_yukawa(0.0, 0)
        assert abs(y - Y_TOP) < 1e-12

    def test_fn_suppression(self):
        y0 = fn_corrected_yukawa(1.0, 0)
        y1 = fn_corrected_yukawa(1.0, 1)
        assert y1 < y0

    def test_positive_yukawa(self):
        for ell in [0.0, 0.5, 1.0, 2.0]:
            for n_fn in [0, 1, 2]:
                assert fn_corrected_yukawa(ell, n_fn) > 0.0


class TestFermionTable:
    def test_9_fermions(self):
        assert len(TABLE) == 9

    def test_top_quark_anchor(self):
        top = next(r for r in TABLE if r["fermion"] == "top")
        assert top["dex"] < 1e-10

    def test_all_within_1_dex(self):
        for row in TABLE:
            assert row["within_10_dex"], f"{row['fermion']} dex = {row['dex']:.2f}"

    def test_at_least_7_within_05_dex(self):
        assert WITHIN_05_DEX >= 7


class TestCoverage:
    def test_within_10_dex_all(self):
        assert WITHIN_10_DEX == 9

    def test_coverage_10_fraction(self):
        assert COV["coverage_10_frac"] == 1.0


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
