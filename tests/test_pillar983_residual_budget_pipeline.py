# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 983 — Residual Budget Pipeline."""

from __future__ import annotations

from src.core.pillar983_residual_budget_pipeline import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    RESIDUAL_BUDGET_TABLE,
    residual_budget_pipeline,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 983
    assert PILLAR_STATUS == "RESIDUAL_BUDGET_PIPELINE_COMPLETE"
    assert PILLAR_VALID is True


def test_rows_normalized() -> None:
    for row in RESIDUAL_BUDGET_TABLE:
        total = row["eft_exhausted"] + row["uv_missing"] + row["external_pending"]
        assert abs(total - 1.0) < 1e-9


def test_pipeline_summary() -> None:
    summary = residual_budget_pipeline()
    assert summary["all_rows_normalized"] is True
    assert summary["all_architecture_rows_linked"] is True
    assert summary["n_external_pending_dominant"] == 2
