# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1015 — 9D CP/anomaly coherence certificate."""

from src.core.pillar1015_nined_cp_anomaly_coherence_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    edge_case_uncertainty_partitions,
    anchor_partition_scan,
    nined_coherence_certificate,
    pillar1015_summary,
)


def test_identity_constants():
    assert PILLAR_NUMBER == 1015
    assert PILLAR_GATE == "NINED_CP_ANOMALY_COHERENCE_CERTIFICATE"
    assert PILLAR_STATUS == "NINED_CP_ANOMALY_COHERENCE_CERTIFICATE_COMPLETE"


def test_partition_scan_shape():
    s = anchor_partition_scan()
    assert s["total_cells"] == s["points_per_axis"] ** 2
    assert s["pass_cells"] + s["fail_cells"] == s["total_cells"]


def test_edge_case_threshold_behavior():
    e = edge_case_uncertainty_partitions()
    assert e["just_below_pass"] is True
    assert e["at_threshold_pass"] is False
    assert e["just_above_pass"] is False


def test_certificate_structure():
    report = nined_coherence_certificate()
    assert report["valid"] is True
    assert report["rung4_hard_gate"]["hard_gate_pass"] is True
    assert report["cp_gate"]["gate_pass"] is True
    assert report["binary_outcome"] in {
        "NINED_CP_ROBUSTNESS_CONFIRMED",
        "NINED_CP_RESIDUAL_CERTIFIED",
    }


def test_summary_fields():
    s = pillar1015_summary()
    assert s["status"] == PILLAR_STATUS
    assert "fail_cells" in s
