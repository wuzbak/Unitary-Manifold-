# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1082_foundation_first_photon_action_audit as p1082

from src.core.action_to_evolution_contract import PRIMARY_DELIVERABLE_IDS
from src.core.evolution import phenomenological_flow_boundary
from src.core.pillar1082_foundation_first_photon_action_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    foundation_first_photon_action_audit,
    pillar1082_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1082
    assert PILLAR_GATE == "FOUNDATION_FIRST_PHOTON_ACTION_AUDIT"
    assert PILLAR_STATUS == "FOUNDATION_FIRST_PHOTON_ACTION_AUDIT_COMPLETE"
    assert isinstance(PILLAR_VALID, bool)


def test_packet_contracts_foundation_blocker_set() -> None:
    report = foundation_first_photon_action_audit()
    assert report["lane"] == "FOUNDATION_PHOTON_ACTION"
    assert report["outcome"] == "FOUNDATION_BLOCKER_SET_CONTRACTED"
    assert report["blocker_contraction"]["before_count"] == 4
    assert report["blocker_contraction"]["after_count"] == 2
    assert report["scientific_progress"] is True
    assert report["valid"] is True
    assert report["honesty_boundaries"]["no_unearned_closure_labels"] is True


def test_remaining_blockers_are_explicit() -> None:
    report = foundation_first_photon_action_audit()
    assert report["blocker_contraction"]["initial_questions"] == report["merlin_handoff"]["blocker_state_before"]
    remaining = report["blocker_contraction"]["remaining_blockers"]
    assert len(remaining) == 2
    assert any("gauge sector" in item for item in remaining)
    assert any("Euler-Lagrange" in item for item in remaining)
    action_row = next(row for row in report["rows"] if row["item"] == "Action-to-evolution equivalence")
    assert action_row["exact_deliverable_blockers"] == PRIMARY_DELIVERABLE_IDS
    assert report["merlin_handoff"]["primary_lane"] == "FOUNDATION_PHOTON_ACTION"
    assert len(report["merlin_handoff"]["evidence_reviewed"]) == 4


def test_fail_closed_when_action_boundary_is_misreported(monkeypatch) -> None:
    monkeypatch.setattr(
        p1082,
        "action_to_evolution_deliverable_contract",
        lambda: {
            "promotion_ready": False,
            "remaining_blockers": PRIMARY_DELIVERABLE_IDS,
            "primary_deliverables": [{"id": item} for item in PRIMARY_DELIVERABLE_IDS],
            "boundary": {
                "status": "OPEN",
                "derived_from_circle_eh_action": True,
                "flow_parameter_is_coordinate_time": False,
                "remaining_obligation": "bad",
            },
        },
    )
    report = foundation_first_photon_action_audit()
    assert report["valid"] is False
    assert report["scientific_progress"] is False


def test_evolution_boundary_api_stays_explicitly_open() -> None:
    boundary = phenomenological_flow_boundary()
    assert boundary["status"] == "OPEN"
    assert boundary["derived_from_circle_eh_action"] is False
    assert boundary["flow_parameter_is_coordinate_time"] is False
    assert "Euler-Lagrange" in boundary["remaining_obligation"]


def test_summary() -> None:
    summary = pillar1082_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["scientific_progress"] is True
