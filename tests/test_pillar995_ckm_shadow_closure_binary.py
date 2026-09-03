# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 995 — CKM shadow closure binary decision."""

from __future__ import annotations

from src.core.pillar995_ckm_shadow_closure_binary import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    ckm_shadow_closure_binary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 995
    assert PILLAR_STATUS == "CKM_SHADOW_CLOSURE_BINARY_COMPLETE"
    assert PILLAR_VALID is True


def test_binary_status_only() -> None:
    status = ckm_shadow_closure_binary()["runtime_status"]
    assert status in {
        "CKM_SHADOW_CLOSED_FROM_PARENT_13D",
        "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
    }


def test_source_is_unified_state() -> None:
    report = ckm_shadow_closure_binary()
    assert report["input_source"] == "PILLAR_994_UNIFIED_13D_COMPACTIFICATION_STATE"
