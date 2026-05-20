# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 300 — Observatory Network Integration Dashboard."""
import pytest
from src.core.pillar300_observatory_network_integration_dashboard import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    NETWORK_VERSION,
    NETWORK_DATE,
    separation_guard,
    build_network_table,
    observatory_network_status,
    query_experiment,
    experiments_by_status,
    falsifier_priority_matrix,
    upcoming_decision_windows,
    network_integration_report,
)


# ── Constants ──────────────────────────────────────────────────────────────


def test_pillar_number():
    assert PILLAR_NUMBER == 300


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_network_version():
    assert NETWORK_VERSION == "v11.10"


def test_network_date():
    assert "2026" in NETWORK_DATE


# ── separation_guard ────────────────────────────────────────────────────────


def test_separation_guard_pillar():
    g = separation_guard()
    assert g["pillar"] == 300


def test_separation_guard_not_hardgate():
    g = separation_guard()
    assert g["is_hardgate"] is False


def test_separation_guard_aggregates():
    g = separation_guard()
    agg = g["aggregates_pillars"]
    assert isinstance(agg, list)
    assert len(agg) >= 10


def test_separation_guard_milestone():
    g = separation_guard()
    assert "300" in g["milestone"]


# ── build_network_table ────────────────────────────────────────────────────


def test_network_table_is_list():
    table = build_network_table()
    assert isinstance(table, list)


def test_network_table_nonempty():
    table = build_network_table()
    assert len(table) >= 8


def test_network_table_required_keys():
    table = build_network_table()
    required = ["experiment", "pillar", "observable", "um_prediction",
                "status", "expected_year", "data_available", "action"]
    for entry in table:
        for key in required:
            assert key in entry, f"Missing {key!r} in {entry['experiment']}"


def test_network_table_has_act_dr6():
    table = build_network_table()
    act = [e for e in table if "ACT DR6" in e["experiment"]]
    assert len(act) >= 1


def test_network_table_has_litebird():
    table = build_network_table()
    lb = [e for e in table if "LiteBIRD" in e["experiment"]]
    assert len(lb) == 1


def test_network_table_has_lisa():
    table = build_network_table()
    lisa = [e for e in table if "LISA" in e["experiment"]]
    assert len(lisa) == 1


def test_network_table_has_simons():
    table = build_network_table()
    so = [e for e in table if "Simons" in e["experiment"]]
    assert len(so) == 1


def test_network_table_has_spt3g():
    table = build_network_table()
    spt = [e for e in table if "SPT" in e["experiment"]]
    assert len(spt) == 1


def test_network_table_has_hyperk():
    table = build_network_table()
    hk = [e for e in table if "Hyper" in e["experiment"]]
    assert len(hk) >= 1


def test_network_table_no_falsifiers_triggered():
    table = build_network_table()
    triggered = [e for e in table if e.get("p_falsifier_triggered", False)]
    assert len(triggered) == 0


def test_network_table_um_prediction_present():
    table = build_network_table()
    for entry in table:
        assert isinstance(entry["um_prediction"], dict)
        assert len(entry["um_prediction"]) >= 1


# ── observatory_network_status ─────────────────────────────────────────────


def test_network_status_keys():
    s = observatory_network_status()
    for key in ("network_version", "network_date", "total_experiments",
                "experiments", "summary", "open_falsifier_windows", "label"):
        assert key in s


def test_network_status_version():
    s = observatory_network_status()
    assert s["network_version"] == NETWORK_VERSION


def test_network_status_total_experiments():
    s = observatory_network_status()
    assert s["total_experiments"] >= 8


def test_network_status_no_falsifiers_triggered():
    s = observatory_network_status()
    assert s["summary"]["p_falsifier_triggered_count"] == 0


def test_network_status_label():
    s = observatory_network_status()
    assert s["label"] == "ADJACENT_TRACK"


def test_network_status_summary_counts():
    s = observatory_network_status()
    total_from_counts = sum(s["summary"]["status_counts"].values())
    assert total_from_counts == s["total_experiments"]


def test_network_status_open_falsifier_windows():
    s = observatory_network_status()
    windows = s["open_falsifier_windows"]
    assert isinstance(windows, list)
    # There should be several open windows (preregistered experiments)
    assert len(windows) >= 3


# ── query_experiment ────────────────────────────────────────────────────────


def test_query_act_dr6():
    result = query_experiment("ACT DR6")
    assert result is not None
    assert "ACT" in result["experiment"]


def test_query_litebird():
    result = query_experiment("LiteBIRD")
    assert result is not None
    assert result["expected_year"] == 2032


def test_query_case_insensitive():
    result = query_experiment("litebird")
    assert result is not None


def test_query_partial_match():
    result = query_experiment("Simons")
    assert result is not None
    assert "Simons" in result["experiment"]


def test_query_not_found():
    result = query_experiment("NonExistentExperiment_XYZ_2099")
    assert result is None


def test_query_returns_dict():
    result = query_experiment("JUNO")
    assert result is None or isinstance(result, dict)


def test_query_hyper_k():
    result = query_experiment("Hyper")
    assert result is not None
    assert result["pillar"] == 293


# ── experiments_by_status ──────────────────────────────────────────────────


def test_status_filter_preregistered():
    results = experiments_by_status("PREREGISTERED")
    assert len(results) >= 2
    for e in results:
        assert e["status"] == "PREREGISTERED"


def test_status_filter_consistent():
    results = experiments_by_status("CONSISTENT")
    assert len(results) >= 2
    for e in results:
        assert e["status"] == "CONSISTENT"


def test_status_filter_high_tension():
    results = experiments_by_status("HIGH_TENSION")
    assert len(results) >= 1
    for e in results:
        assert e["status"] == "HIGH_TENSION"


def test_status_filter_empty():
    results = experiments_by_status("FALSIFIED")
    assert results == []


def test_status_filter_returns_list():
    results = experiments_by_status("ROUTED")
    assert isinstance(results, list)


# ── falsifier_priority_matrix ─────────────────────────────────────────────


def test_falsifier_matrix_is_list():
    f = falsifier_priority_matrix()
    assert isinstance(f, list)


def test_falsifier_matrix_nonempty():
    f = falsifier_priority_matrix()
    assert len(f) >= 5


def test_falsifier_matrix_required_keys():
    f = falsifier_priority_matrix()
    for entry in f:
        for key in ("priority", "falsifier", "condition", "timeline",
                    "module", "impact", "preregistered_version"):
            assert key in entry, f"Missing {key!r} in {entry['falsifier']}"


def test_falsifier_p1_litebird():
    f = falsifier_priority_matrix()
    p1 = [e for e in f if e["priority"] == "P.1"]
    assert len(p1) == 1
    assert "LiteBIRD" in p1[0]["falsifier"]


def test_falsifier_p2_cmbs4():
    f = falsifier_priority_matrix()
    p2 = [e for e in f if e["priority"] == "P.2"]
    assert len(p2) == 1
    assert "CMB-S4" in p2[0]["falsifier"]


def test_falsifier_priorities_sequential():
    f = falsifier_priority_matrix()
    priorities = [e["priority"] for e in f]
    # P.1, P.2, P.3, ... should all start with "P."
    assert all(p.startswith("P.") for p in priorities)


def test_falsifier_so_included():
    f = falsifier_priority_matrix()
    so = [e for e in f if "Simons" in e["falsifier"]]
    assert len(so) == 1
    assert "v11.10" in so[0]["preregistered_version"]


# ── upcoming_decision_windows ─────────────────────────────────────────────


def test_windows_is_list():
    w = upcoming_decision_windows()
    assert isinstance(w, list)


def test_windows_nonempty():
    w = upcoming_decision_windows()
    assert len(w) >= 3


def test_windows_keys():
    w = upcoming_decision_windows()
    for entry in w:
        for key in ("year", "experiments", "action"):
            assert key in entry


def test_windows_chronological():
    w = upcoming_decision_windows()
    years = [e["year"] for e in w]
    assert years == sorted(years)


def test_windows_2032_litebird():
    w = upcoming_decision_windows()
    litebird_windows = [e for e in w if e["year"] == 2032]
    assert len(litebird_windows) == 1
    assert "LiteBIRD" in litebird_windows[0]["experiments"]


def test_windows_2027_has_juno_and_desi():
    w = upcoming_decision_windows()
    y2027 = [e for e in w if e["year"] == 2027]
    assert len(y2027) == 1
    exps = y2027[0]["experiments"]
    # Should contain JUNO and DESI in 2027 window
    assert any("JUNO" in exp for exp in exps)


# ── network_integration_report ────────────────────────────────────────────


def test_report_keys():
    r = network_integration_report()
    for key in ("pillar", "title", "network_version", "network_date",
                "adjacency_guard", "network_status", "falsifier_priority_matrix",
                "upcoming_decision_windows", "summary", "status",
                "label", "milestone"):
        assert key in r


def test_report_pillar():
    r = network_integration_report()
    assert r["pillar"] == 300


def test_report_status():
    r = network_integration_report()
    assert r["status"] == "INTEGRATION_DASHBOARD_OPERATIONAL"


def test_report_framework_standing():
    r = network_integration_report()
    assert r["summary"]["framework_status"] == "STANDING"


def test_report_no_falsifier_triggered():
    r = network_integration_report()
    assert r["summary"]["p_falsifier_triggered"] is False


def test_report_primary_falsifier():
    r = network_integration_report()
    assert r["summary"]["primary_falsifier_year"] == 2032
    assert r["summary"]["primary_falsifier_experiment"] == "LiteBIRD"


def test_report_label():
    r = network_integration_report()
    assert r["label"] == "ADJACENT_TRACK"


def test_report_milestone():
    r = network_integration_report()
    assert "300" in r["milestone"]


def test_report_usage_string():
    r = network_integration_report()
    assert "observatory_network_status" in r["usage"]


def test_report_upcoming_windows_years():
    r = network_integration_report()
    years = r["summary"]["upcoming_decision_years"]
    assert isinstance(years, list)
    assert 2032 in years
