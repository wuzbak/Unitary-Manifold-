# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 531 — Radion Wheeler-DeWitt Minisuperspace."""

from __future__ import annotations
import math
import pytest
from src.core.radion_wdw_minisuperspace import (
    ETA_BAR, K_CS, M_RADION, M_RADION_SQUARED, N_W, PI_KR_CANONICAL,
    PILLAR_NUMBER, PILLAR_STATUS, PILLAR_TITLE,
    pillar531_report, wdw_radion_mass_squared, wdw_stability_check,
)


class TestPillarMetadata:
    def test_pillar_number(self): assert PILLAR_NUMBER == 531
    def test_status(self): assert PILLAR_STATUS == "WDW_RADION_MINISUPERSPACE_CERTIFIED"
    def test_title_mentions_saddle(self): assert "Saddle" in PILLAR_TITLE or "saddle" in PILLAR_TITLE or "WdW" in PILLAR_TITLE
    def test_k_cs(self): assert K_CS == 74
    def test_n_w(self): assert N_W == 5
    def test_eta_bar(self): assert ETA_BAR == 0.5
    def test_pi_kr_canonical(self): assert abs(PI_KR_CANONICAL - 37.0) < 1e-10


class TestRadionMass:
    def test_positive(self): assert M_RADION_SQUARED > 0
    def test_formula(self):
        expected = (74**2 * 25 * 0.25) / (4 * math.pi**2)
        assert abs(wdw_radion_mass_squared() - expected) < 1e-8
    def test_m_radion_positive(self): assert M_RADION > 0
    def test_sqrt_consistent(self): assert abs(M_RADION**2 - M_RADION_SQUARED) < 1e-8
    def test_custom(self):
        m2 = wdw_radion_mass_squared(74, 5, 0.5)
        assert abs(m2 - M_RADION_SQUARED) < 1e-10


class TestWDWStabilityCheck:
    def setup_method(self): self.v = wdw_stability_check()
    def test_returns_dict(self): assert isinstance(self.v, dict)
    def test_stable_true(self): assert self.v["stable"] is True
    def test_verdict(self): assert self.v["verdict"] == "WDW_STABLE"
    def test_pi_kr(self): assert abs(self.v["pi_kr_canonical"] - 37.0) < 1e-10
    def test_m_radion_squared_positive(self): assert self.v["m_radion_squared"] > 0


class TestPillar531Report:
    def setup_method(self): self.r = pillar531_report()
    def test_returns_dict(self): assert isinstance(self.r, dict)
    def test_pillar_number(self): assert self.r["pillar"] == 531
    def test_status(self): assert self.r["status"] == "WDW_RADION_MINISUPERSPACE_CERTIFIED"
    def test_wdw_section(self): assert "wdw" in self.r
    def test_stability_stable(self): assert self.r["stability"]["stable"] is True
    def test_summary_mentions_stable(self): assert "stable" in self.r["summary"].lower()
