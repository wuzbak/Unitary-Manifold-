# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1004 — 13D bifurcation sink."""

from __future__ import annotations

from src.core.pillar1004_thirteen_dimensional_bifurcation_sink import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    thirteen_dimensional_bifurcation_sink,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1004
    assert PILLAR_GATE == "THIRTEEN_DIMENSIONAL_BIFURCATION_SINK"
    assert PILLAR_STATUS == "THIRTEEN_DIMENSIONAL_BIFURCATION_SINK_COMPLETE"
    assert PILLAR_VALID is True


def test_sink_remains_organizational_only() -> None:
    report = thirteen_dimensional_bifurcation_sink()
    assert report["sink_outcome"] == "THIRTEEN_D_ORGANIZATIONAL_SINK_ONLY"
    assert report["downstream_binary_lanes"]["ckm"]["runtime_status"].endswith("CERTIFIED")
    assert report["downstream_binary_lanes"]["fermion"]["runtime_status"].endswith("CERTIFIED")


def test_sink_gates_pass() -> None:
    report = thirteen_dimensional_bifurcation_sink()
    assert report["valid"] is True
    assert all(report["non_negotiable_consistency_gates"].values())
