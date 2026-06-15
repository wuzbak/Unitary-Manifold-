# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 533 — θ₁₂ Solar/Reactor Routing."""

from __future__ import annotations
import math
import pytest
from src.core.theta12_solar_reactor_routing import (
    DELTA_MSW, K_CS, N_W, PILLAR_NUMBER, PILLAR_STATUS, PILLAR_TITLE,
    TAN2_THETA12_UM, THETA12_REACTOR_DEG, THETA12_REACTOR_SIGMA,
    THETA12_SOLAR_DEG, THETA12_UM_VACUUM_DEG,
    msw_solar_correction, pillar533_report, theta12_solar_predicted,
    theta12_tension_verdict, theta12_um_vacuum,
)


class TestPillarMetadata:
    def test_pillar_number(self): assert PILLAR_NUMBER == 533
    def test_status(self): assert PILLAR_STATUS == "THETA12_ROUTING_MSW_CORRECTED"
    def test_title_mentions_msw(self): assert "MSW" in PILLAR_TITLE or "Solar" in PILLAR_TITLE
    def test_k_cs(self): assert K_CS == 74
    def test_n_w(self): assert N_W == 5


class TestTheta12UMVacuum:
    def test_in_range(self):
        theta = theta12_um_vacuum()
        assert 30.0 < theta < 40.0

    def test_approximately_33_to_34_deg(self):
        theta = theta12_um_vacuum()
        assert 33.0 < theta < 35.0

    def test_matches_constant(self):
        assert abs(theta12_um_vacuum() - THETA12_UM_VACUUM_DEG) < 1e-8

    def test_tan2_formula(self):
        expected = 0.302252 / (1.0 - 0.302252)
        assert abs(TAN2_THETA12_UM - expected) < 1e-8


class TestMSWCorrection:
    def test_positive(self): assert msw_solar_correction() > 0
    def test_matches_delta_msw(self): assert abs(msw_solar_correction() - DELTA_MSW) < 1e-10
    def test_less_than_5deg(self): assert msw_solar_correction() < 5.0


class TestTheta12SolarPredicted:
    def test_above_vacuum(self): assert theta12_solar_predicted() > THETA12_UM_VACUUM_DEG
    def test_formula(self):
        assert abs(theta12_solar_predicted() - (THETA12_UM_VACUUM_DEG + DELTA_MSW)) < 1e-10
    def test_close_to_solar_measurement(self):
        assert abs(theta12_solar_predicted() - THETA12_SOLAR_DEG) < 3.0


class TestTheta12TensionVerdict:
    def setup_method(self): self.v = theta12_tension_verdict()
    def test_returns_dict(self): assert isinstance(self.v, dict)
    def test_reactor_consistent(self): assert self.v["reactor_consistent"] is True
    def test_verdict_consistent(self): assert "CONSISTENT" in self.v["verdict"]
    def test_delta_msw_recorded(self): assert abs(self.v["delta_msw_deg"] - DELTA_MSW) < 1e-8
    def test_reactor_tension_below_2sigma(self): assert self.v["reactor_tension_sigma"] < 2.0


class TestPillar533Report:
    def setup_method(self): self.r = pillar533_report()
    def test_returns_dict(self): assert isinstance(self.r, dict)
    def test_pillar_number(self): assert self.r["pillar"] == 533
    def test_status(self): assert self.r["status"] == "THETA12_ROUTING_MSW_CORRECTED"
    def test_derivation_section(self): assert "derivation" in self.r
    def test_tension_section(self): assert "tension" in self.r
    def test_reactor_consistent_in_report(self): assert self.r["tension"]["reactor_consistent"] is True
