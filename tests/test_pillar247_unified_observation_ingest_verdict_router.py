# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
import pytest

from src.core.pillar247_unified_observation_ingest_verdict_router import (
    ADJACENCY_TRACK_LABEL,
    pillar247_router_report,
    route_observation_packet,
)


def test_router_report():
    report = pillar247_router_report()
    assert report["pillar"] == 247
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert "DESI" in report["supported_experiments"]


def test_route_pass_tension_falsified():
    assert route_observation_packet("DESI", sigma=1.0, in_window=True)["route"] == "PASS"
    assert route_observation_packet("DESI", sigma=2.4, in_window=True)["route"] == "TENSION"
    assert route_observation_packet("DESI", sigma=3.1, in_window=False)["route"] == "FALSIFIED"


def test_route_rejects_invalid_experiment():
    with pytest.raises(ValueError):
        route_observation_packet("UNKNOWN", sigma=1.0, in_window=True)
