# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/proof_close_certification_report.py."""
from __future__ import annotations

from src.core.proof_close_certification_report import (
    ADJACENCY_TRACK_LABEL,
    proof_close_certification_report,
)


def test_proof_close_certification_report_shape():
    report = proof_close_certification_report()
    assert report["report_id"] == "FINAL_PROOF_CLOSE_CERTIFICATION"
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert "proof_closure" in report
    assert "residual_dashboard" in report


def test_proof_close_certification_lists_present():
    report = proof_close_certification_report()
    assert isinstance(report["closed_items"], list)
    assert isinstance(report["hardened_items"], list)
    assert isinstance(report["measurement_gated_items"], list)
    assert "G3_DESI" in report["measurement_gated_items"]
    assert "LITEBIRD_BETA" in report["measurement_gated_items"]
