# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1058_flavor_execution_packet as p1058

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


def test_incomplete_packet_routing_when_less_than_two_rows(monkeypatch) -> None:
    monkeypatch.setattr(
        p1058,
        "_packet_rows",
        lambda _report: [
            {
                "family": "only_family",
                "covered_lanes": ["CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED"],
                "coverage_count": 1,
                "max_pressure": 1.0,
                "mean_closure_ratio": 0.2,
                "score": 1.2,
            }
        ],
    )
    report = p1058.sprint_cc_flavor_execution_packet()
    assert report["valid"] is False
    assert report["deterministic_verdict"] == "FALSIFIED"
    assert report["outcome"] == "FLAVOR_PACKET_INCOMPLETE_INPUT"
    assert report["primary_target"] is None
    assert report["fallback_target"] is None


def test_malformed_upstream_payload_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(p1058, "flavor_priority_continuation", lambda: {})
    report = p1058.sprint_cc_flavor_execution_packet()
    assert report["valid"] is False
    assert report["deterministic_verdict"] == "FALSIFIED"
    assert report["outcome"] == "FLAVOR_PACKET_INCOMPLETE_INPUT"


def test_nondeterministic_tie_path_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(
        p1058,
        "_packet_rows",
        lambda _report: [
            {
                "family": "a",
                "covered_lanes": ["CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED"],
                "coverage_count": 1,
                "max_pressure": 1.0,
                "mean_closure_ratio": 0.2,
                "score": 2.0,
            },
            {
                "family": "b",
                "covered_lanes": ["FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED"],
                "coverage_count": 1,
                "max_pressure": 1.0,
                "mean_closure_ratio": 0.2,
                "score": 2.0,
            },
        ],
    )
    report = p1058.sprint_cc_flavor_execution_packet()
    assert report["valid"] is False
    assert report["deterministic_verdict"] == "FALSIFIED"
    assert report["outcome"] == "FLAVOR_PACKET_NONDETERMINISTIC_TIE"


def test_summary() -> None:
    summary = pillar1058_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
    assert summary["deterministic_verdict"] == "TENSION"
