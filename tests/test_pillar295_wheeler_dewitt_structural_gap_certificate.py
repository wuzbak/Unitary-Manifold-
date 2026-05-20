# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 295 — Wheeler–DeWitt Structural Gap Certificate."""
import pytest
from src.core.pillar295_wheeler_dewitt_structural_gap_certificate import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    GAP_NAME,
    GAP_STATUS,
    separation_guard,
    existing_wdw_closures,
    gap_precise_statement,
    predictions_independent_of_gap,
    predictions_dependent_on_gap,
    closing_mechanism,
    wdw_architecture_limit_certificate,
    wdw_gap_certificate_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 295


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_gap_name():
    assert GAP_NAME == "WDW_NONPERTURBATIVE_INHOMOGENEOUS_5D_KK"


def test_gap_status():
    assert GAP_STATUS == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_separation_guard():
    g = separation_guard()
    assert g["pillar"] == 295
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
    assert g["alters_toe_score"] is False
    assert g["gap_type"] == "STRUCTURAL_ARCHITECTURE_LIMIT"


def test_existing_wdw_closures_count():
    closures = existing_wdw_closures()
    assert len(closures) >= 3


def test_existing_wdw_closures_keys():
    closures = existing_wdw_closures()
    for c in closures:
        assert "module" in c
        assert "status" in c
        assert "scope" in c


def test_existing_wdw_closures_have_closed():
    closures = existing_wdw_closures()
    statuses = [c["status"] for c in closures]
    # At least one should be closed
    assert any("CLOSED" in s for s in statuses)


def test_gap_precise_statement_keys():
    s = gap_precise_statement()
    for key in ("gap_name", "equation", "dimension", "breakdown_conditions", "honest_statement"):
        assert key in s


def test_gap_precise_statement_dimension():
    s = gap_precise_statement()
    assert "5D" in s["dimension"]


def test_gap_precise_breakdown_conditions():
    s = gap_precise_statement()
    assert len(s["breakdown_conditions"]) >= 3


def test_predictions_independent():
    p = predictions_independent_of_gap()
    assert len(p) >= 10
    for item in p:
        assert item["independent"] is True
        assert "param" in item


def test_predictions_independent_includes_ns_r():
    p = predictions_independent_of_gap()
    params = [item["param"] for item in p]
    assert any("n_s" in param for param in params)
    assert any("r" in param for param in params)


def test_predictions_dependent():
    p = predictions_dependent_on_gap()
    assert len(p) >= 1
    for item in p:
        assert "item" in item
        assert "status" in item


def test_closing_mechanism_keys():
    m = closing_mechanism()
    for key in ("primary_path", "secondary_path", "blocking_dependencies", "near_term_substitute"):
        assert key in m


def test_closing_mechanism_primary_identified():
    m = closing_mechanism()
    assert "LQG" in m["primary_path"]["mechanism"] or "Loop" in m["primary_path"]["mechanism"]


def test_closing_mechanism_not_ready():
    m = closing_mechanism()
    assert "not yet" in m["primary_path"]["current_status"].lower()


def test_wdw_architecture_limit_certificate_keys():
    cert = wdw_architecture_limit_certificate()
    for key in ("gap_name", "gap_status", "impact_on_toe_score", "certificate"):
        assert key in cert


def test_wdw_cert_no_toe_impact():
    cert = wdw_architecture_limit_certificate()
    assert cert["impact_on_toe_score"] == "NONE — all 28 parameters independent"


def test_wdw_cert_gap_name():
    cert = wdw_architecture_limit_certificate()
    assert cert["gap_name"] == GAP_NAME


def test_wdw_cert_status():
    cert = wdw_architecture_limit_certificate()
    assert cert["gap_status"] == GAP_STATUS


def test_wdw_cert_no_hardgate_impact():
    cert = wdw_architecture_limit_certificate()
    assert cert["impact_on_hardgate_labels"] == "NONE — classical derivations unaffected"


def test_wdw_cert_closing_mechanism_identified():
    cert = wdw_architecture_limit_certificate()
    assert cert["closing_mechanism_identified"] is True
    assert cert["closing_mechanism_ready"] is False


def test_wdw_cert_independent_count():
    cert = wdw_architecture_limit_certificate()
    assert cert["independent_predictions"] >= 10


def test_wdw_gap_certificate_report_keys():
    rep = wdw_gap_certificate_report()
    for key in ("pillar", "title", "certificate", "summary"):
        assert key in rep


def test_wdw_gap_certificate_report_pillar():
    rep = wdw_gap_certificate_report()
    assert rep["pillar"] == 295


def test_wdw_gap_certificate_summary():
    rep = wdw_gap_certificate_report()
    assert "architecture limit" in rep["summary"].lower() or "Architecture" in rep["summary"]
    assert isinstance(rep["summary"], str)
