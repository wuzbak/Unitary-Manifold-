# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 994 — Unified 13D compactification state."""

from __future__ import annotations

from src.core.pillar994_unified_13d_compactification_state import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    unified_13d_compactification_state,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 994
    assert PILLAR_STATUS == "UNIFIED_13D_COMPACTIFICATION_STATE_COMPLETE"
    assert PILLAR_VALID is True


def test_state_is_valid_and_has_consumers() -> None:
    state = unified_13d_compactification_state()
    assert state["valid"] is True
    assert len(state["consumers"]) == 2


def test_state_contains_shared_inputs() -> None:
    state = unified_13d_compactification_state()
    shared = state["shared_parent_state"]
    assert shared["n_w"] == 5
    assert shared["k_cs"] == 74
    assert shared["tau"] > 0.0
    assert shared["rho"] > 0.0
