# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1009 — CMB nonperturbative normalization candidate."""

from __future__ import annotations

from src.core.pillar1009_cmb_nonperturbative_normalization_candidate import (
    CANDIDATE_NAME,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    cmb_nonperturbative_normalization_candidate,
    pillar1009_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1009
    assert PILLAR_GATE == "CMB_NONPERTURBATIVE_GLOBAL_UV_NORMALIZATION_CANDIDATE"
    assert PILLAR_STATUS == "CMB_NONPERTURBATIVE_NORMALIZATION_CANDIDATE_COMPLETE"
    assert CANDIDATE_NAME == "GLOBAL_UV_NONPERTURBATIVE_TRANSFER_NORMALIZATION_KERNEL"
    assert PILLAR_VALID is True


def test_candidate_is_non_fitted_and_binary() -> None:
    report = cmb_nonperturbative_normalization_candidate()
    assert report["candidate"]["uses_external_as_target"] is False
    assert report["candidate"]["free_parameters_added"] == 0
    assert report["outcome"] == "CMB_NONPERTURBATIVE_NORMALIZATION_NOT_EARNED"


def test_hard_bound_strengthened_on_failure() -> None:
    report = cmb_nonperturbative_normalization_candidate()
    assert report["candidate_success"] is False
    assert report["strengthened_certificate"]["status"] == "CMB_RESIDUAL_BUDGET_TIGHTENED"
    assert report["strengthened_certificate"]["lane"] == "CMB_AMP"


def test_summary() -> None:
    summary = pillar1009_summary()
    assert summary["pillar"] == 1009
    assert summary["outcome"] == "CMB_NONPERTURBATIVE_NORMALIZATION_NOT_EARNED"
