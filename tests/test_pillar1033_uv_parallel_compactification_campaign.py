# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1033 — UV parallel compactification campaign."""

from src.core.pillar1033_uv_parallel_compactification_campaign import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SHARED_UV_PACKET,
    pillar1033_summary,
    uv_parallel_compactification_campaign,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1033
    assert PILLAR_GATE == "UV_PARALLEL_COMPACTIFICATION_CAMPAIGN"
    assert PILLAR_STATUS == "UV_PARALLEL_COMPACTIFICATION_CAMPAIGN_COMPLETE"
    assert PILLAR_VALID is True


def test_uv_campaign_keeps_shared_packet_and_no_rescue_knobs() -> None:
    report = uv_parallel_compactification_campaign()
    assert report["execution_order_rank"] == 2
    assert report["shared_uv_packet"] == SHARED_UV_PACKET
    assert report["per_lane_rescue_parameters_added"] == 0
    assert report["closure_earned"] is False


def test_uv_campaign_sharpens_joint_boundary() -> None:
    report = uv_parallel_compactification_campaign()
    assert report["simultaneous_narrowing"] is True
    assert report["strengthened_architecture_certificate"] is True
    assert report["outcome"] == "UV_PARALLEL_ARCHITECTURE_BOUNDARY_SHARPENED"


def test_summary() -> None:
    summary = pillar1033_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
