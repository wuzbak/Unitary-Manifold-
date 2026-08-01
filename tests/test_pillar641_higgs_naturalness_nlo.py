# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 641 — Higgs naturalness 6D two-loop NLO."""
from __future__ import annotations

import math

from src.core.pillar641_higgs_naturalness_6d_nlo import (
    DELTA_6D_NLO,
    DELTA_6D_ONE_LOOP,
    KK_GRAVITON_CORRECTION,
    NATURALNESS_CRITERION,
    NATURALNESS_STATUS_AFTER,
    NATURALNESS_STATUS_BEFORE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TWO_LOOP_FRAC,
    VERSION,
    Y_TOP,
    kk_graviton_stability,
    naturalness_status,
    one_loop_naturalness,
    pillar_report,
    two_loop_nlo_correction,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
ONE_LOOP = one_loop_naturalness()
TWO_LOOP = two_loop_nlo_correction()
KK_GR = kk_graviton_stability()
NAT_STATUS = naturalness_status()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 641

    def test_status(self):
        assert "NLO_IMPROVED" in PILLAR_STATUS

    def test_two_loop_frac(self):
        expected = Y_TOP ** 2 / (16.0 * math.pi ** 2)
        assert abs(TWO_LOOP_FRAC - expected) < 1e-12

    def test_delta_nlo_larger(self):
        assert DELTA_6D_NLO > DELTA_6D_ONE_LOOP

    def test_delta_nlo_below_criterion(self):
        assert DELTA_6D_NLO < NATURALNESS_CRITERION

    def test_kk_graviton_negligible(self):
        assert KK_GRAVITON_CORRECTION < 1e-30

    def test_status_advance(self):
        assert "DERIVED_PARTIAL" in NATURALNESS_STATUS_BEFORE
        assert "NLO_IMPROVED" in NATURALNESS_STATUS_AFTER


class TestOneLoop:
    def test_delta_6d_value(self):
        assert abs(ONE_LOOP["delta_6d"] - DELTA_6D_ONE_LOOP) < 1e-12

    def test_naturally_fine_tuned(self):
        assert ONE_LOOP["naturally_fine_tuned"] is True


class TestTwoLoop:
    def test_subdominant(self):
        assert TWO_LOOP["subdominant"] is True

    def test_criterion_met_at_nlo(self):
        assert TWO_LOOP["criterion_met_at_nlo"] is True

    def test_status_unchanged(self):
        assert TWO_LOOP["status_unchanged"] is True

    def test_delta_nlo_formula(self):
        expected = DELTA_6D_ONE_LOOP * (1.0 + TWO_LOOP_FRAC)
        assert abs(DELTA_6D_NLO - expected) < 1e-12


class TestKKGraviton:
    def test_correction_negligible(self):
        assert KK_GR["correction_negligible"] is True


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
