# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1058_flavor_execution_packet import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1058_summary,
    sprint_cc_flavor_execution_packet,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1058
    assert PILLAR_GATE == "SPRINT_CC_FLAVOR_EXECUTION_PACKET"
    assert PILLAR_STATUS == "SPRINT_CC_FLAVOR_EXECUTION_PACKET_COMPLETE"
    assert PILLAR_VALID is True


def test_primary_and_fallback_targets_are_selected_deterministically() -> None:
    report = sprint_cc_flavor_execution_packet()
    assert report["primary_target"]["family"] == "phase_completion"
    assert report["fallback_target"]["family"] == "shared_root"
    assert report["primary_target"]["score"] > report["fallback_target"]["score"]


def test_packet_tightens_boundary_without_unearned_promotion() -> None:
    report = sprint_cc_flavor_execution_packet()
    contraction = report["blocker_contraction"]
    assert report["runtime_flip_earned"] is False
    assert report["boundary_tightened"] is True
    assert report["deterministic_verdict"] == "TENSION"
    assert contraction["contracted_packets"] == 1
    assert contraction["all_flavor_lanes_covered"] is True
    assert report["anti_hidden_calibration"]["pass"] is True


def test_summary() -> None:
    summary = pillar1058_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
    assert summary["deterministic_verdict"] == "TENSION"
