# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 254 — Monograph Irreversibility Validation & Certification Engine."""

from __future__ import annotations

import math

import pytest

pytest.importorskip("sympy", reason="sympy not installed — skip SymPy-dependent tests")

from src.core.pillar254_monograph_irreversibility_validation_certification_engine import (
    ADJACENCY_TRACK_LABEL,
    C_S,
    K_CS,
    LANE_ORDER,
    MONOGRAPH_CERT_TRACK_LABEL,
    N_LANES,
    N_W,
    PHI0,
    __provenance__,
    certification_lane_reports,
    certification_summary,
    formal_theorem_consistency_gate,
    irreversibility_claim_encoding_gate,
    monograph_artifact_presence_gate,
    pillar254_monograph_irreversibility_validation_certification_report,
    precision_proof_machine_gate,
    runtime_irreversibility_execution_gate,
    separation_guard,
)


def test_provenance_contract():
    assert __provenance__["pillar"] == 254
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]


def test_core_constants_contract():
    assert N_W == 5
    assert K_CS == 74
    assert K_CS == 5**2 + 7**2
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_lane_order_contract():
    assert N_LANES == len(LANE_ORDER)
    assert LANE_ORDER == (
        "monograph_artifact_presence",
        "irreversibility_claim_encoding",
        "precision_proof_machine",
        "formal_theorem_consistency",
        "runtime_irreversibility_execution",
    )


def test_separation_guard_contract():
    g = separation_guard()
    assert g["label"] == ADJACENCY_TRACK_LABEL
    assert g["track"] == MONOGRAPH_CERT_TRACK_LABEL
    assert g["hardgate_isolation"] is True
    assert g["toe_score_delta_allowed"] is False
    assert g["physics_claim_promotion_allowed"] is False


def test_monograph_artifact_presence_gate_passes():
    gate = monograph_artifact_presence_gate()
    assert gate["pass"] is True
    assert gate["missing"] == []


def test_irreversibility_claim_encoding_gate_passes():
    gate = irreversibility_claim_encoding_gate()
    assert gate["pass"] is True
    assert gate["missing_markers"] == []


def test_precision_proof_machine_gate_passes():
    gate = precision_proof_machine_gate()
    assert gate["pass"] is True
    assert gate["four_lane"]["overall_pass"] is True
    assert gate["four_lane"]["precision_stable"] is True
    assert gate["full_precision_audit"]["all_pass"] is True


def test_formal_theorem_consistency_gate_passes():
    gate = formal_theorem_consistency_gate()
    assert gate["pass"] is True
    assert gate["failed_theorems"] == []
    assert len(gate["theorems"]) >= 3


def test_runtime_irreversibility_execution_gate_passes():
    gate = runtime_irreversibility_execution_gate()
    assert gate["pass"] is True
    assert gate["finite_fields"] is True
    assert gate["j0_nonnegative"] is True
    assert gate["time_advanced"] is True
    assert gate["mean_j0"] >= 0.0


def test_lane_reports_shape_and_keys():
    reports = certification_lane_reports()
    assert tuple(reports.keys()) == LANE_ORDER
    for lane in LANE_ORDER:
        assert "pass" in reports[lane]
        assert "reason" in reports[lane]
        assert isinstance(reports[lane]["pass"], bool)


def test_lane_reports_all_pass():
    reports = certification_lane_reports()
    assert all(reports[lane]["pass"] for lane in LANE_ORDER)


def test_summary_contract():
    summary = certification_summary()
    assert summary["track"] == MONOGRAPH_CERT_TRACK_LABEL
    assert summary["lane_order"] == LANE_ORDER
    assert summary["certification_index"] == 1.0
    assert summary["certified"] is True
    assert summary["status"] == "MONOGRAPH_IRREVERSIBILITY_CERTIFIED"
    assert summary["failed_lanes"] == []
    assert summary["rejection_reasons"] == []


def test_final_report_contract():
    rep = pillar254_monograph_irreversibility_validation_certification_report()
    assert rep["pillar"] == 254
    assert rep["adjacency_track_label"] == ADJACENCY_TRACK_LABEL
    assert rep["monograph_cert_track"] == MONOGRAPH_CERT_TRACK_LABEL
    assert rep["adjacent_toe_score_delta"] == 0.0
    assert rep["final_verdict"] == "CERTIFIED"
    assert "FALSIFIED" in rep["falsification_condition"]


def test_final_report_has_expected_top_keys():
    rep = pillar254_monograph_irreversibility_validation_certification_report()
    expected = {
        "pillar",
        "title",
        "status",
        "adjacency_track_label",
        "monograph_cert_track",
        "adjacent_toe_score_delta",
        "separation_guard",
        "lane_reports",
        "certification_summary",
        "final_verdict",
        "falsification_condition",
    }
    assert expected.issubset(set(rep.keys()))

