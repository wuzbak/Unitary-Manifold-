# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 180 — Comparative Falsification Calendar."""
import pytest
from src.core.falsification_calendar import (
    LITEBIRD_LAUNCH, FCC_EE_LAUNCH, LISA_LAUNCH, CMB_S4_LAUNCH, SKA_LAUNCH,
    um_falsification_profile, wolfram_falsification_profile, gu_falsification_profile,
    e8_falsification_profile, cdt_falsification_profile,
    comparative_calendar, theories_with_near_term_falsifiers, falsification_calendar_audit,
    pillar178_summary,
)

class TestConstants:
    def test_litebird(self): assert LITEBIRD_LAUNCH == 2032
    def test_fcc(self): assert FCC_EE_LAUNCH == 2041
    def test_lisa(self): assert LISA_LAUNCH == 2034
    def test_cmb_s4(self): assert CMB_S4_LAUNCH == 2028
    def test_ska(self): assert SKA_LAUNCH == 2028

class TestUmProfile:
    def setup_method(self): self.r = um_falsification_profile()
    def test_experiment(self): assert self.r["experiment"] == "LiteBIRD"
    def test_launch_year(self): assert self.r["launch_year"] == LITEBIRD_LAUNCH
    def test_near_term(self): assert self.r["has_near_term_falsifier"] is True
    def test_year_2033(self): assert self.r["falsification_year_estimate"] == 2033

class TestWolframProfile:
    def setup_method(self): self.r = wolfram_falsification_profile()
    def test_no_near_term(self): assert self.r["has_near_term_falsifier"] is False
    def test_far_future(self): assert self.r["falsification_year_estimate"] >= 9999

class TestGUProfile:
    def test_no_near_term(self): assert gu_falsification_profile()["has_near_term_falsifier"] is False

class TestE8Profile:
    def setup_method(self): self.r = e8_falsification_profile()
    def test_has_near_term(self): assert self.r["has_near_term_falsifier"] is True
    def test_fcc_experiment(self): assert "FCC" in self.r["experiment"]

class TestCDTProfile:
    def setup_method(self): self.r = cdt_falsification_profile()
    def test_has_near_term(self): assert self.r["has_near_term_falsifier"] is True
    def test_lisa_experiment(self): assert self.r["experiment"] == "LISA"

class TestComparativeCalendar:
    def test_sorted_ascending(self):
        years = [p["falsification_year_estimate"] for p in comparative_calendar()]
        assert years == sorted(years)
    def test_length_5(self): assert len(comparative_calendar()) == 5

class TestNearTermFalsifiers:
    def test_um_in_list(self): assert any("Unitary" in t or "UM" in t for t in theories_with_near_term_falsifiers())
    def test_wolfram_not_in_list(self): assert not any("Wolfram" in t for t in theories_with_near_term_falsifiers())
    def test_cdt_in_list(self): assert any("CDT" in t or "Causal" in t for t in theories_with_near_term_falsifiers())

class TestCalendarAudit:
    def setup_method(self): self.r = falsification_calendar_audit()
    def test_status(self): assert self.r["status"] == "STRATEGIC_ASSET"
    def test_5_profiles(self): assert len(self.r["profiles"]) == 5

class TestPillar178Summary:
    def test_returns_string(self): assert isinstance(pillar178_summary(), str)
    def test_contains_178(self): assert "178" in pillar178_summary()
    def test_contains_status(self): assert "STRATEGIC_ASSET" in pillar178_summary()
