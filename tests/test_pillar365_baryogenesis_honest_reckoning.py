# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar365_baryogenesis_honest_reckoning.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar365_baryogenesis_honest_reckoning import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    ETA_B_OBSERVED, ETA_B_CENTRAL_ESTIMATE, UNCERTAINTY_FACTOR, K_CS,
    separation_guard, ptft_central_estimate, braid_enhancement_factor,
    maximum_eta_b_estimate, gap_factor, washout_factor_sensitivity,
    missing_factor_audit, baryogenesis_honest_reckoning, pillar365_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 365
    def test_status(self): assert PILLAR_STATUS == "ARCHITECTURE_LIMIT"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_eta_b_observed(self): assert abs(ETA_B_OBSERVED - 6.1e-10) < 1e-11
    def test_eta_b_central(self): assert ETA_B_CENTRAL_ESTIMATE < ETA_B_OBSERVED
    def test_uncertainty_factor(self): assert abs(UNCERTAINTY_FACTOR - 30.0) < 1.0
    def test_k_cs(self): assert K_CS == 74


class TestEstimates:
    def test_ptft_central(self): assert ptft_central_estimate() == ETA_B_CENTRAL_ESTIMATE
    def test_braid_enhancement(self): assert abs(braid_enhancement_factor() - 74.0) < 1.0
    def test_max_estimate(self):
        max_est = maximum_eta_b_estimate()
        assert max_est > ETA_B_CENTRAL_ESTIMATE
    def test_gap_factor(self):
        gap = gap_factor()
        assert gap > 100  # at least 100× gap


class TestWashoutSensitivity:
    def test_returns_dict(self): assert isinstance(washout_factor_sensitivity(), dict)
    def test_eta_max_with_braid(self):
        result = washout_factor_sensitivity()
        assert result["eta_b_max_with_braid"] > result["eta_b_central"]
    def test_gap_central_large(self):
        result = washout_factor_sensitivity()
        assert result["gap_central"] > 1000
    def test_comment_present(self):
        assert "comment" in washout_factor_sensitivity()


class TestMissingFactorAudit:
    def test_returns_list(self): assert isinstance(missing_factor_audit(), list)
    def test_at_least_4_items(self): assert len(missing_factor_audit()) >= 4
    def test_each_has_verdict(self):
        for item in missing_factor_audit():
            assert "verdict" in item
    def test_each_has_mechanism(self):
        for item in missing_factor_audit():
            assert "mechanism" in item


class TestHonestReckoning:
    def test_returns_dict(self): assert isinstance(baryogenesis_honest_reckoning(), dict)
    def test_pillar_365(self): assert baryogenesis_honest_reckoning()["pillar"] == 365
    def test_status(self): assert baryogenesis_honest_reckoning()["status"] == "ARCHITECTURE_LIMIT"
    def test_architecture_limit_statement(self):
        result = baryogenesis_honest_reckoning()
        assert "ARCHITECTURE_LIMIT" in result["architecture_limit_statement"]
    def test_paths_forward(self):
        result = baryogenesis_honest_reckoning()
        assert len(result["paths_forward"]) >= 2


class TestSummary:
    def test_pillar_365(self): assert pillar365_summary()["pillar"] == 365
    def test_status(self): assert pillar365_summary()["status"] == "ARCHITECTURE_LIMIT"


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
