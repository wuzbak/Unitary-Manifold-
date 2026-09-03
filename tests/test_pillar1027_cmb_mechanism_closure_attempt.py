# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1027 — CMB mechanism closure attempt."""

from src.core.pillar1027_cmb_mechanism_closure_attempt import (
    CANDIDATE_NAME,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    cmb_mechanism_closure_attempt,
    pillar1027_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1027
    assert PILLAR_GATE == "CMB_MECHANISM_CLOSURE_ATTEMPT"
    assert PILLAR_STATUS == "CMB_MECHANISM_CLOSURE_ATTEMPT_COMPLETE"
    assert PILLAR_VALID is True


def test_cmb_candidate_guardrails_and_budget_delta() -> None:
    report = cmb_mechanism_closure_attempt()
    assert report["candidate"]["name"] == CANDIDATE_NAME
    assert report["candidate"]["uses_external_as_target"] is False
    assert report["candidate"]["free_parameters_added"] == 0
    assert report["demonstrable_reduction"] is True
    assert report["residual_budget_delta"]["delta"]["eft_exhausted"] > 0.0


def test_summary() -> None:
    summary = pillar1027_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
