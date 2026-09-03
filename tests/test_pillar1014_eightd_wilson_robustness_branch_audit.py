# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1014 — 8D Wilson robustness and branch audit."""

from src.core.pillar1014_eightd_wilson_robustness_branch_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    ROBUSTNESS_WINDOWS_DEG,
    adversarial_failure_certificates,
    branch_consistency_audit,
    eightd_wilson_lane_report,
    pillar1014_summary,
    robustness_window_scan,
)


def test_identity_constants():
    assert PILLAR_NUMBER == 1014
    assert PILLAR_GATE == "EIGHTD_WILSON_ROBUSTNESS_BRANCH_AUDIT"
    assert PILLAR_STATUS == "EIGHTD_WILSON_ROBUSTNESS_BRANCH_AUDIT_COMPLETE"


def test_window_scan_shape():
    scan = robustness_window_scan()
    assert scan["window_count"] == len(ROBUSTNESS_WINDOWS_DEG)
    assert len(scan["scan_rows"]) == len(ROBUSTNESS_WINDOWS_DEG)


def test_branch_consistency_core_flags():
    audit = branch_consistency_audit()
    assert audit["rung3_kill_switch_pass"] is True
    assert audit["base_p14_residual_gate"] is True


def test_adversarial_cases_fail_as_expected():
    rows = adversarial_failure_certificates()
    assert len(rows) == 3
    assert all(row["failure_confirmed"] for row in rows)


def test_lane_report_structure():
    report = eightd_wilson_lane_report()
    assert report["valid"] is True
    assert "analytic_check" in report["three_evidence_classes"]
    assert "executable_check" in report["three_evidence_classes"]
    assert "adversarial_check" in report["three_evidence_classes"]
    assert report["binary_outcome"] in {
        "EIGHTD_WILSON_ROBUST_CLOSURE_EARNED",
        "EIGHTD_WILSON_NON_PROMOTION_CERTIFIED",
    }


def test_summary_has_outcome():
    s = pillar1014_summary()
    assert s["status"] == PILLAR_STATUS
    assert "binary_outcome" in s
