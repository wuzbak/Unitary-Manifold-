# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1049_sprint_ca_full_throttle_execution import (
    DECISION_GATES,
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    OPEN_LANES,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SPRINT_NAME,
    SUBSTACK_ARTICLES,
    VERSION,
    pillar1049_summary,
    sprint_ca_full_throttle_execution,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1049
    assert PILLAR_STATUS == "SPRINT_CA_FULL_THROTTLE_EXECUTION_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert VERSION == "v35.7"
    assert SPRINT_NAME == "CA"
    assert NEXT_PILLAR_SLOT == 1051
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA == 12


def test_open_lanes_and_articles() -> None:
    assert len(OPEN_LANES) == 9
    assert len(SUBSTACK_ARTICLES) == 5


def test_full_sprint_report() -> None:
    report = sprint_ca_full_throttle_execution()
    assert report["status"] == PILLAR_STATUS
    assert report["valid"] is True
    assert all(report["definition_of_done"].values()) is True
    assert set(report["decision_matrix"].values()).issubset(set(DECISION_GATES))


def test_summary() -> None:
    summary = pillar1049_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["version"] == VERSION
    assert summary["valid"] is True
