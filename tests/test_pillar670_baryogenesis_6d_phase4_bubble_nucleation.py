# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 670 — Baryogenesis 6D Phase 4 bubble nucleation."""
from __future__ import annotations

import math

from src.core.pillar670_baryogenesis_6d_phase4_bubble_nucleation_adjacent import (
    ADJACENT_TRACK,
    ARCHITECTURE_LIMIT_QUANTIFIED,
    BUBBLE_NUCLEATION_SUPPRESSED,
    M_KK_FIRST_GEV,
    NUCLEATION_CRITERION,
    PILLAR_NUMBER,
    S3_OVER_T_EW,
    T_EW_GEV,
    THETA_6,
    VERSION,
    bubble_nucleation_rate,
    cp_violation_link,
    kk_tower_integration,
    pillar_report,
)

KK = kk_tower_integration()
RATE = bubble_nucleation_rate()
CP = cp_violation_link()
REPORT = pillar_report()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 670

    def test_version(self) -> None:
        assert VERSION == "v21.0"

    def test_kk_ratio_large(self) -> None:
        assert M_KK_FIRST_GEV / T_EW_GEV > 10.0

    def test_suppressed_flag(self) -> None:
        assert BUBBLE_NUCLEATION_SUPPRESSED is True

    def test_action_exceeds_criterion(self) -> None:
        assert S3_OVER_T_EW > NUCLEATION_CRITERION


class TestKKTowerIntegration:
    def test_integrated_out(self) -> None:
        assert KK["kk_modes_integrated_out"] is True

    def test_architecture_limit_confirmed(self) -> None:
        assert KK["architecture_limit_confirmed"] is True


class TestBubbleRate:
    def test_rate_suppression_factor_window(self) -> None:
        assert 0.0 < RATE["rate_suppression_factor"] < 1.0

    def test_suppression_factor_matches_exp(self) -> None:
        assert math.isclose(
            RATE["rate_suppression_factor"],
            math.exp(-S3_OVER_T_EW),
            rel_tol=0.0,
            abs_tol=0.0,
        )

    def test_architecture_limit_quantified(self) -> None:
        assert RATE["architecture_limit_quantified"] is ARCHITECTURE_LIMIT_QUANTIFIED is True


class TestCPViolationLink:
    def test_theta_6_canonical(self) -> None:
        assert math.isclose(CP["theta_6"], THETA_6, rel_tol=0.0, abs_tol=1e-15)

    def test_sns_date(self) -> None:
        assert CP["sns_date"] == "2028"


class TestReport:
    def test_report_core_fields(self) -> None:
        assert REPORT["adjacent_track"] is ADJACENT_TRACK is True
        assert REPORT["toe_score_delta"] == 0.0
        assert REPORT["hardgate_score_delta"] == 0.0

    def test_report_sections(self) -> None:
        assert set(REPORT).issuperset(
            {"kk_tower_integration", "bubble_nucleation_rate", "cp_violation_link"}
        )
