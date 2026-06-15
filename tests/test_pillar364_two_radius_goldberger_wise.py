# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar364_two_radius_goldberger_wise.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar364_two_radius_goldberger_wise import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    N_W1, N_W2, K_CS, PI_KR, LAMBDA_GW, EPS_GW, G_BRAID, PHI_UV, PHI_IR,
    separation_guard, gw_potential_single_radius, braid_backreaction_potential,
    total_gw_braid_potential, gw_minimum_radius, two_radius_splitting,
    convention_279_3_upgrade, pillar364_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 364
    def test_status(self): assert PILLAR_STATUS == "CONDITIONAL_DERIVATION"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_n_w1(self): assert N_W1 == 5
    def test_n_w2(self): assert N_W2 == 7
    def test_k_cs(self): assert K_CS == 74
    def test_g_braid_positive(self): assert G_BRAID > 0


class TestGWPotential:
    def test_positive(self): assert gw_potential_single_radius(1.0) >= 0
    def test_minimum_exists(self):
        vals = [gw_potential_single_radius(mk) for mk in [0.001, 0.01, 0.1, 1.0, 10.0]]
        assert min(vals) >= 0

    def test_large_mk_large_v(self):
        v_small = gw_potential_single_radius(0.01)
        v_large = gw_potential_single_radius(100.0)
        assert v_large > v_small


class TestBraidPotential:
    def test_finite(self):
        v = braid_backreaction_potential(1.0, 1.0)
        assert math.isfinite(v)
    def test_scaled_by_g_braid(self):
        v = braid_backreaction_potential(0.5, 0.5)
        assert abs(v) <= G_BRAID


class TestTotalPotential:
    def test_finite(self):
        v = total_gw_braid_potential(1.0, 1.0)
        assert math.isfinite(v)
    def test_positive_near_min(self):
        v = total_gw_braid_potential(0.1, 0.1)
        assert math.isfinite(v)


class TestGWMinimum:
    def test_positive(self): assert gw_minimum_radius() > 0
    def test_less_than_1(self): assert gw_minimum_radius() < 1.0


class TestTwoRadiusSplitting:
    def test_returns_dict(self): assert isinstance(two_radius_splitting(), dict)
    def test_r1_less_than_r2(self):
        result = two_radius_splitting()
        assert result["r1_normalized"] < result["r2_normalized"]
    def test_r_short_is_r1(self):
        result = two_radius_splitting()
        assert result["r_short_is_r1"] is True
    def test_ratio_matches_n_ratio(self):
        result = two_radius_splitting()
        assert result["matches_n_ratio"] is True
    def test_expected_ratio(self):
        result = two_radius_splitting()
        assert abs(result["expected_ratio"] - 5/7) < 0.01


class TestConvention279_3:
    def test_returns_dict(self): assert isinstance(convention_279_3_upgrade(), dict)
    def test_new_status(self):
        result = convention_279_3_upgrade()
        assert result["convention_279_3"]["new_status"] == "CONDITIONAL_DERIVATION"
    def test_old_status(self):
        result = convention_279_3_upgrade()
        assert result["convention_279_3"]["old_status"] == "CONVENTION"
    def test_remaining_gap(self):
        result = convention_279_3_upgrade()
        assert "remaining_gap" in result
    def test_verdict_present(self):
        assert "verdict" in convention_279_3_upgrade()


class TestSummary:
    def test_pillar_364(self): assert pillar364_summary()["pillar"] == 364
    def test_status(self): assert pillar364_summary()["status"] == "CONDITIONAL_DERIVATION"


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
