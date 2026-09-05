# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1053_merlin_frontier_development import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    merlin_frontier_development,
    pillar1053_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1053
    assert PILLAR_GATE == "MERLIN_FRONTIER_DEVELOPMENT"
    assert PILLAR_STATUS == "MERLIN_FRONTIER_DEVELOPMENT_COMPLETE"
    assert PILLAR_VALID is True


def test_frontier_report() -> None:
    report = merlin_frontier_development()
    assert report["valid"] is True
    assert report["frontier_readiness"]["sovereign_primary"] is True
    assert report["frontier_readiness"]["openrouter_fallback_only"] is True
    assert len(report["frontier_readiness"]["promotion_blockers"]) >= 4


def test_summary() -> None:
    summary = pillar1053_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
