# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/yukawa_tier4_purity_sprint.py."""
from __future__ import annotations

from src.core.yukawa_tier4_purity_sprint import (
    PURITY_FRAMEWORK_PASS,
    PURITY_INPUTS_PENDING,
    RESIDUAL_GATE_BLOCKED,
    PILLAR183_MILESTONE,
    tier4_purity_sprint_report,
    tier4_purity_gate_evidence,
)


def test_framework_purity_status():
    assert PURITY_FRAMEWORK_PASS is True
    assert PURITY_INPUTS_PENDING is True
    assert RESIDUAL_GATE_BLOCKED is True


def test_pillar183_milestone_defined():
    assert "183" in PILLAR183_MILESTONE
    assert len(PILLAR183_MILESTONE) > 10


def test_report_structure():
    report = tier4_purity_sprint_report()
    assert report["promotion_allowed"] is False
    assert report["toe_delta"] == 0.0
    assert len(report["parameters"]) == 4
    assert set(report["parameters"].keys()) == {"P7", "P8", "P9", "P10"}


def test_report_all_constrained():
    report = tier4_purity_sprint_report()
    for pid, data in report["parameters"].items():
        assert data["status"] == "CONSTRAINED", f"{pid} should be CONSTRAINED"
        assert data["nominal_residual_gate_pass"] is False, (
            f"{pid} should fail the nominal_residual gate (residual {data['residual_pct']:.1f}%)"
        )


def test_report_blocking_gates_present():
    report = tier4_purity_sprint_report()
    assert len(report["blocking_gates"]) >= 2
    # At least one gate about residuals
    combined = " ".join(report["blocking_gates"])
    assert "residual" in combined.lower()


def test_report_passing_gates():
    report = tier4_purity_sprint_report()
    assert len(report["passing_gates"]) >= 1
    combined = " ".join(report["passing_gates"])
    assert "purity" in combined.lower() or "hierarchy" in combined.lower()


def test_purity_gate_evidence_structure():
    evidence = tier4_purity_gate_evidence()
    assert evidence["gate"] == "axiomzero_purity"
    assert evidence["pdg_anchors_in_formula"] == []
    assert "INPUTS_PENDING" in evidence["gate_status"]
    assert len(evidence["geometric_inputs"]) > 0


def test_purity_gate_evidence_pi_kr():
    evidence = tier4_purity_gate_evidence()
    pi_kr = evidence["geometric_inputs"]["pi_kr"]
    assert abs(pi_kr - 37.0) < 1e-10


def test_purity_gate_evidence_no_pdg_in_formula():
    evidence = tier4_purity_gate_evidence()
    # The formula inputs should not include PDG Yukawa values
    assert evidence["pdg_anchors_in_formula"] == []
    # PDG values should only appear as comparison targets
    assert len(evidence["pdg_anchors_for_comparison"]) > 0
