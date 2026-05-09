# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
test_desi_dr2_gap_report.py — Tests for desi_dr2_gap_report.py (v10.31).

Validates routing verdicts for the DESI DR2 BAO-only and combined
BAO+CMB+SNe constraints, checks scenario table coverage, and confirms
that the HIGH_TENSION (< 3σ) / TENSION / FALSIFIED split is computed
correctly and honestly.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import pytest

from src.core.desi_dr2_gap_report import (
    DESI_DR2_COMBINED,
    FUTURE_DESI_SCENARIOS,
    execute_dr2_bao_routing,
    execute_dr2_combined_routing,
    full_dr2_gap_report,
    scenario_table,
)


# ---------------------------------------------------------------------------
# DESI_DR2_COMBINED constant
# ---------------------------------------------------------------------------


def test_desi_dr2_combined_has_wa_central():
    assert "wa_central" in DESI_DR2_COMBINED


def test_desi_dr2_combined_has_w0_central():
    assert "w0_central" in DESI_DR2_COMBINED


def test_desi_dr2_combined_wa_central_value():
    assert abs(DESI_DR2_COMBINED["wa_central"] - (-0.55)) < 1e-9


def test_desi_dr2_combined_w0_central_value():
    assert abs(DESI_DR2_COMBINED["w0_central"] - (-0.90)) < 1e-9


def test_desi_dr2_combined_sigma_level_approx():
    # sigma_level_combined should encode ~2.75σ (|wa_central| / wa_sigma)
    expected = abs(DESI_DR2_COMBINED["wa_central"]) / DESI_DR2_COMBINED["wa_sigma"]
    assert abs(DESI_DR2_COMBINED["sigma_level_combined"] - expected) < 0.01


# ---------------------------------------------------------------------------
# execute_dr2_bao_routing()
# ---------------------------------------------------------------------------


def test_bao_routing_returns_dict():
    result = execute_dr2_bao_routing()
    assert isinstance(result, dict)


def test_bao_routing_route_is_tension():
    """BAO-only: 2.07σ < 3σ → TENSION, not FALSIFIED."""
    result = execute_dr2_bao_routing()
    assert result["route"] == "TENSION"


def test_bao_routing_wa_tension_sigma_above_2():
    """BAO-only tension must exceed 2σ (should be ~2.07σ)."""
    result = execute_dr2_bao_routing()
    assert result["wa_tension_sigma"] > 2.0


def test_bao_routing_wa_tension_sigma_below_3():
    """BAO-only tension must be below falsification threshold of 3σ."""
    result = execute_dr2_bao_routing()
    assert result["wa_tension_sigma"] < 3.0


# ---------------------------------------------------------------------------
# execute_dr2_combined_routing()
# ---------------------------------------------------------------------------


def test_combined_routing_returns_dict():
    result = execute_dr2_combined_routing()
    assert isinstance(result, dict)


def test_combined_routing_route_is_tension():
    """Combined BAO+CMB+SNe: 2.75σ < 3σ → TENSION (not FALSIFIED)."""
    result = execute_dr2_combined_routing()
    assert result["route"] == "TENSION"


def test_combined_routing_wa_tension_sigma_between_2_and_3():
    """Combined tension 2.75σ must be in (2, 3) — high tension, not yet falsified."""
    result = execute_dr2_combined_routing()
    sigma = result["wa_tension_sigma"]
    assert 2.0 < sigma < 3.0


def test_combined_routing_higher_sigma_than_bao_only():
    """Combined constraint tighter → higher σ than BAO-only (2.75 > 2.07)."""
    bao = execute_dr2_bao_routing()
    combined = execute_dr2_combined_routing()
    assert combined["wa_tension_sigma"] > bao["wa_tension_sigma"]


# ---------------------------------------------------------------------------
# full_dr2_gap_report()
# ---------------------------------------------------------------------------


def test_full_report_returns_dict():
    report = full_dr2_gap_report()
    assert isinstance(report, dict)


def test_full_report_has_bao_only_routing():
    report = full_dr2_gap_report()
    assert "bao_only_routing" in report


def test_full_report_has_combined_routing():
    report = full_dr2_gap_report()
    assert "combined_routing" in report


def test_full_report_current_status_not_pass():
    """Neither analysis is consistent — status must indicate tension."""
    report = full_dr2_gap_report()
    assert report["current_status"] != "PASS"


def test_full_report_bao_tension_sigma_correct():
    """BAO-only tension: |−0.62| / 0.30 = 2.0667σ."""
    report = full_dr2_gap_report()
    expected = abs(-0.62) / 0.30
    assert abs(report["bao_tension_sigma"] - expected) < 0.001


def test_full_report_combined_tension_sigma_correct():
    """Combined tension: |−0.55| / 0.20 = 2.75σ."""
    report = full_dr2_gap_report()
    expected = abs(-0.55) / 0.20
    assert abs(report["combined_tension_sigma"] - expected) < 0.001


def test_full_report_next_data_release_present():
    report = full_dr2_gap_report()
    assert "next_data_release" in report
    assert "2027" in report["next_data_release"]


def test_full_report_action_required_present():
    report = full_dr2_gap_report()
    assert "action_required" in report
    assert len(report["action_required"]) > 20


def test_full_report_falsification_threshold_present():
    report = full_dr2_gap_report()
    assert "falsification_threshold" in report
    assert "3" in report["falsification_threshold"]


# ---------------------------------------------------------------------------
# scenario_table()
# ---------------------------------------------------------------------------


def test_scenario_table_returns_list():
    table = scenario_table()
    assert isinstance(table, list)


def test_scenario_table_has_at_least_5_entries():
    table = scenario_table()
    assert len(table) >= 5


def test_scenario_table_has_exactly_7_entries():
    table = scenario_table()
    assert len(table) == 7


def test_scenario_table_has_falsified_scenario():
    """At least one DR3 scenario must route to FALSIFIED."""
    table = scenario_table()
    routes = [entry["route"] for entry in table]
    assert "FALSIFIED" in routes


def test_scenario_table_has_pass_scenario():
    """At least one DR3 scenario must route to PASS."""
    table = scenario_table()
    routes = [entry["route"] for entry in table]
    assert "PASS" in routes


def test_scenario_table_has_tension_scenario():
    """At least one DR3 scenario must route to TENSION."""
    table = scenario_table()
    routes = [entry["route"] for entry in table]
    assert "TENSION" in routes


def test_scenario_table_entries_have_route_key():
    table = scenario_table()
    for entry in table:
        assert "route" in entry, f"Entry {entry.get('name')} missing 'route' key"


def test_scenario_table_entries_have_wa_tension_sigma():
    table = scenario_table()
    for entry in table:
        assert "wa_tension_sigma" in entry


def test_scenario_table_all_expected_verdicts_match():
    """Every scenario's actual routing must match its expected_verdict."""
    table = scenario_table()
    mismatches = [
        entry["name"]
        for entry in table
        if not entry.get("verdict_matches_expected", False)
    ]
    assert mismatches == [], (
        f"Scenario routing mismatches: {mismatches}. "
        "Check FUTURE_DESI_SCENARIOS definitions in desi_dr2_gap_report.py."
    )


def test_scenario_table_falsified_scenarios_above_3sigma():
    """All FALSIFIED scenarios must have wa_tension_sigma >= 3.0."""
    table = scenario_table()
    for entry in table:
        if entry["route"] == "FALSIFIED":
            assert entry["wa_tension_sigma"] >= 3.0, (
                f"Scenario {entry['name']} routed FALSIFIED but tension "
                f"{entry['wa_tension_sigma']:.2f}σ < 3σ"
            )


def test_scenario_table_pass_scenarios_below_1sigma():
    """All PASS scenarios must have wa_tension_sigma < 1.0 (and w0 < 2σ)."""
    table = scenario_table()
    for entry in table:
        if entry["route"] == "PASS":
            assert entry["wa_tension_sigma"] < 1.0, (
                f"Scenario {entry['name']} routed PASS but tension "
                f"{entry['wa_tension_sigma']:.2f}σ >= 1σ"
            )


# ---------------------------------------------------------------------------
# Honesty: BAO-only and combined both TENSION (not FALSIFIED)
# ---------------------------------------------------------------------------


def test_dr2_does_not_falsify_um():
    """DESI DR2 (both BAO-only and combined) must NOT be routed as FALSIFIED."""
    bao = execute_dr2_bao_routing()
    combined = execute_dr2_combined_routing()
    assert bao["route"] != "FALSIFIED", "BAO-only 2.07σ should not be FALSIFIED"
    assert combined["route"] != "FALSIFIED", "Combined 2.75σ should not be FALSIFIED"
