# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar367_desi_dr3_canonical_routing.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar367_desi_dr3_canonical_routing import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    W0_UM_CANONICAL, WA_UM_CANONICAL,
    DESI_DR2_W0_BAO, DESI_DR2_W0_BAO_SIGMA,
    DESI_DR2_WA_COMBINED, DESI_DR2_WA_COMBINED_SIGMA,
    ROMAN_SIGMA_W0, ROMAN_SIGMA_WA,
    separation_guard, compute_tension_sigma,
    desi_dr2_current_status, desi_dr3_scenario_table,
    desi_dr3_canonical_routing, roman_routing,
    full_dark_energy_routing_matrix, pillar367_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 367
    def test_status(self): assert PILLAR_STATUS == "ROUTING_INFRASTRUCTURE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_w0_canonical(self): assert W0_UM_CANONICAL == -1.0
    def test_wa_canonical(self): assert WA_UM_CANONICAL == 0.0
    def test_roman_sigma_w0(self): assert abs(ROMAN_SIGMA_W0 - 0.02) < 1e-5
    def test_roman_sigma_wa(self): assert abs(ROMAN_SIGMA_WA - 0.10) < 1e-5
    def test_desi_dr2_w0(self): assert abs(DESI_DR2_W0_BAO - (-0.838)) < 0.01
    def test_desi_dr2_wa(self): assert abs(DESI_DR2_WA_COMBINED - (-0.55)) < 0.05


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_mentions_routing(self): assert "ROUTING" in separation_guard().upper()
    def test_mentions_canonical(self): assert "canonical" in separation_guard().lower() or "w" in separation_guard()


class TestComputeTensionSigma:
    def test_zero_tension_exact_match(self):
        assert compute_tension_sigma(1.0, 1.0, 0.1) == 0.0

    def test_one_sigma(self):
        assert abs(compute_tension_sigma(1.1, 1.0, 0.1) - 1.0) < 1e-10

    def test_two_sigma(self):
        assert abs(compute_tension_sigma(1.2, 1.0, 0.1) - 2.0) < 1e-10

    def test_zero_sigma_returns_zero(self):
        assert compute_tension_sigma(2.0, 1.0, 0.0) == 0.0

    def test_symmetric(self):
        t1 = compute_tension_sigma(1.1, 1.0, 0.1)
        t2 = compute_tension_sigma(0.9, 1.0, 0.1)
        assert abs(t1 - t2) < 1e-10

    def test_w0_canonical_tension(self):
        # W0_UM = -1, DESI_DR2_W0 = -0.838, sigma = 0.072 → ~2.25σ
        t = compute_tension_sigma(W0_UM_CANONICAL, DESI_DR2_W0_BAO, DESI_DR2_W0_BAO_SIGMA)
        assert 1.5 < t < 4.0

    def test_wa_canonical_tension(self):
        # WA_UM = 0, DESI_DR2_WA = -0.55, sigma = 0.20 → ~2.75σ
        t = compute_tension_sigma(WA_UM_CANONICAL, DESI_DR2_WA_COMBINED, DESI_DR2_WA_COMBINED_SIGMA)
        assert 2.0 < t < 4.0


class TestDesiDr2CurrentStatus:
    def test_returns_dict(self): assert isinstance(desi_dr2_current_status(), dict)
    def test_canonical_w0(self):
        s = desi_dr2_current_status()
        assert s["canonical_w0_um"] == -1.0
    def test_canonical_wa(self):
        s = desi_dr2_current_status()
        assert s["canonical_wa_um"] == 0.0
    def test_w0_tension_positive(self):
        s = desi_dr2_current_status()
        assert s["w0_tension_sigma"] > 0
    def test_wa_tension_positive(self):
        s = desi_dr2_current_status()
        assert s["wa_tension_sigma"] > 0
    def test_w0_verdict_present(self):
        s = desi_dr2_current_status()
        assert "w0_verdict" in s
    def test_wa_verdict_present(self):
        s = desi_dr2_current_status()
        assert "wa_verdict" in s
    def test_deprecated_formula_note(self):
        s = desi_dr2_current_status()
        assert "deprecated_formula_note" in s
    def test_wa_high_tension(self):
        s = desi_dr2_current_status()
        assert s["wa_verdict"] in ["HIGH_TENSION", "TENSION", "FALSIFIED"]


class TestDesiDr3ScenarioTable:
    def test_returns_list(self): assert isinstance(desi_dr3_scenario_table(), list)
    def test_seven_scenarios(self): assert len(desi_dr3_scenario_table()) == 7
    def test_each_has_scenario_label(self):
        for s in desi_dr3_scenario_table():
            assert "scenario" in s
    def test_each_has_tension_sigma(self):
        for s in desi_dr3_scenario_table():
            assert "tension_sigma" in s
    def test_each_has_verdict(self):
        for s in desi_dr3_scenario_table():
            assert "verdict" in s
    def test_s6_falsified(self):
        table = desi_dr3_scenario_table()
        s6 = next(s for s in table if s["scenario"] == "DR3-S6")
        assert s6["verdict"] == "FALSIFIED"
    def test_s6_tension_above_three(self):
        table = desi_dr3_scenario_table()
        s6 = next(s for s in table if s["scenario"] == "DR3-S6")
        assert s6["tension_sigma"] >= 3.0
    def test_s1_consistent_or_tension(self):
        table = desi_dr3_scenario_table()
        s1 = next(s for s in table if s["scenario"] == "DR3-S1")
        assert s1["verdict"] in ["CONSISTENT", "TENSION"]
    def test_at_least_one_falsified(self):
        table = desi_dr3_scenario_table()
        falsified = [s for s in table if s["verdict"] == "FALSIFIED"]
        assert len(falsified) >= 1


class TestDesiDr3CanonicalRouting:
    def test_returns_dict(self):
        r = desi_dr3_canonical_routing(-0.62, 0.18)
        assert isinstance(r, dict)

    def test_falsified_at_s6(self):
        r = desi_dr3_canonical_routing(-0.62, 0.18)
        assert r["wa_verdict"] == "FALSIFIED"

    def test_consistent_at_low_tension(self):
        r = desi_dr3_canonical_routing(-0.10, 0.20)
        assert r["wa_verdict"] in ["CONSISTENT", "TENSION"]

    def test_pillar_number(self):
        r = desi_dr3_canonical_routing(-0.55, 0.20)
        assert r["pillar"] == PILLAR_NUMBER

    def test_with_w0(self):
        r = desi_dr3_canonical_routing(-0.55, 0.20, w0_measured=-1.0, sigma_w0=0.05)
        assert "w0_tension_sigma" in r

    def test_w0_consistent_at_minus1(self):
        r = desi_dr3_canonical_routing(-0.55, 0.20, w0_measured=-1.0, sigma_w0=0.05)
        assert r["w0_verdict"] == "CONSISTENT"

    def test_required_action_present(self):
        r = desi_dr3_canonical_routing(-0.62, 0.18)
        assert "required_action" in r

    def test_falsified_action_contains_word(self):
        r = desi_dr3_canonical_routing(-0.62, 0.18)
        assert "FALSIFIED" in r["required_action"]

    def test_tension_sigma_correct(self):
        r = desi_dr3_canonical_routing(-0.62, 0.18)
        expected = abs(-0.62) / 0.18
        assert abs(r["wa_tension_sigma"] - expected) < 0.01


class TestRomanRouting:
    def test_returns_dict(self):
        r = roman_routing(-1.0, 0.02, 0.0, 0.10)
        assert isinstance(r, dict)

    def test_consistent_at_canonical(self):
        r = roman_routing(-1.0, 0.02, 0.0, 0.10)
        assert r["combined_verdict"] == "CONSISTENT"

    def test_falsified_at_w0_deviation(self):
        # w0 = -0.90 vs UM -1.0, sigma = 0.02 → 5σ tension
        r = roman_routing(-0.90, 0.02, 0.0, 0.10)
        assert r["w0_verdict"] == "FALSIFIED"

    def test_instrument_label(self):
        r = roman_routing(-1.0, 0.02, 0.0, 0.10)
        assert "Roman" in r["instrument"]

    def test_w0_tension_zero_at_canonical(self):
        r = roman_routing(-1.0, 0.02, 0.0, 0.10)
        assert r["w0_tension_sigma"] == 0.0

    def test_wa_tension_zero_at_canonical(self):
        r = roman_routing(-1.0, 0.02, 0.0, 0.10)
        assert r["wa_tension_sigma"] == 0.0


class TestFullDarkEnergyRoutingMatrix:
    def test_returns_dict(self): assert isinstance(full_dark_energy_routing_matrix(), dict)
    def test_canonical_prediction(self):
        m = full_dark_energy_routing_matrix()
        assert m["canonical_prediction"]["w0"] == -1.0
        assert m["canonical_prediction"]["wa"] == 0.0
    def test_desi_dr3_scenarios_present(self):
        m = full_dark_energy_routing_matrix()
        assert "desi_dr3_scenarios" in m
    def test_roman_lane_present(self):
        m = full_dark_energy_routing_matrix()
        assert "roman_lane" in m
    def test_nearest_falsification_present(self):
        m = full_dark_energy_routing_matrix()
        assert "nearest_falsification_scenario" in m
    def test_deprecated_formula_note(self):
        m = full_dark_energy_routing_matrix()
        assert "deprecated_formula_note" in m


class TestPillar367Summary:
    def test_pillar(self): assert pillar367_summary()["pillar"] == 367
    def test_status(self): assert pillar367_summary()["status"] == "ROUTING_INFRASTRUCTURE"
    def test_canonical_w0(self): assert pillar367_summary()["canonical_prediction_w0"] == -1.0
    def test_canonical_wa(self): assert pillar367_summary()["canonical_prediction_wa"] == 0.0
    def test_roman_lane_added(self): assert pillar367_summary()["roman_lane_added"] is True
    def test_key_fix_present(self): assert "key_fix" in pillar367_summary()
