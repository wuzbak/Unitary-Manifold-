# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from src.core.pillar226_cmbs4_acoustic_peak_hardening_brief import (
    ADJACENCY_TRACK_LABEL,
    acoustic_peak_hardening_metrics,
    pillar226_hardening_brief,
)


def test_metrics_cover_three_lanes():
    metrics = acoustic_peak_hardening_metrics()
    assert len(metrics) == 3
    assert all(v > 0 for v in metrics.values())


def test_hardening_brief_status():
    report = pillar226_hardening_brief()
    assert report["pillar"] == 226
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["status"] in {"READY_FOR_CMB_S4", "HARDENING_IN_PROGRESS"}
