# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1034 — parallel CMB closure campaign."""

from src.core.pillar1034_parallel_cmb_closure_campaign import (
    CANDIDATE_PACKET,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    parallel_cmb_closure_campaign,
    pillar1034_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1034
    assert PILLAR_GATE == "PARALLEL_CMB_CLOSURE_CAMPAIGN"
    assert PILLAR_STATUS == "PARALLEL_CMB_CLOSURE_CAMPAIGN_COMPLETE"
    assert PILLAR_VALID is True


def test_candidate_keeps_honesty_guardrails() -> None:
    report = parallel_cmb_closure_campaign()
    assert report["execution_order_rank"] == 3
    assert report["candidate"]["name"] == CANDIDATE_PACKET
    assert report["candidate"]["uses_external_as_target"] is False
    assert report["candidate"]["free_parameters_added"] == 0


def test_cmb_campaign_strengthens_nonpromotion_boundary() -> None:
    report = parallel_cmb_closure_campaign()
    assert report["closure_earned"] is False
    assert report["demonstrable_reduction"] is True
    assert report["strengthened_irreducibility_certificate"] is True
    assert report["outcome"] == "CMB_PARALLEL_NONPROMOTION_STRENGTHENED"


def test_summary() -> None:
    summary = pillar1034_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
