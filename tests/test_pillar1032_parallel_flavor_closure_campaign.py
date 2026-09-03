# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1032 — parallel flavor closure campaign."""

from src.core.pillar1032_parallel_flavor_closure_campaign import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    PRIMARY_SHARED_ROOT_OBJECT,
    parallel_flavor_closure_campaign,
    pillar1032_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1032
    assert PILLAR_GATE == "PARALLEL_FLAVOR_CLOSURE_CAMPAIGN"
    assert PILLAR_STATUS == "PARALLEL_FLAVOR_CLOSURE_CAMPAIGN_COMPLETE"
    assert PILLAR_VALID is True


def test_flavor_campaign_keeps_root_first_and_nonpromotion() -> None:
    report = parallel_flavor_closure_campaign()
    assert report["execution_order_rank"] == 1
    assert report["primary_shared_root_object"] == PRIMARY_SHARED_ROOT_OBJECT
    assert report["runtime_flip_earned"] is False
    assert report["outcome"] == "FLAVOR_PARALLEL_BOUNDARY_SHARPENED"


def test_blocker_map_is_sharper_than_prior_attempt() -> None:
    report = parallel_flavor_closure_campaign()
    assert report["sharper_blocker_map"] is True
    assert len(report["grouped_blockers"]) == 3
    assert PRIMARY_SHARED_ROOT_OBJECT in report["named_unresolved_objects"]
    assert report["dominant_blocker"]["pressure"] > 1.0


def test_summary() -> None:
    summary = pillar1032_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
    assert summary["sharper_blocker_map"] is True
